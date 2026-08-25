# M2 技术决策记录

> 本记录说明"为什么是当前最小充分方案"，不晋升为产品合同（Execution Prompt §5.1）。
> 权威范围边界仍以 `decision-chain/docs/M2_ENGINEERING_EXECUTION_PROMPT_v1.1.md` 为准。

## 数据库隔离方式：独立数据库，而非独立 Schema

在现有 PostgreSQL 15.19 实例（`docker-db_postgres-1`）内新建独立数据库 `diyu_business`，
owner 为专用低权限角色 `diyu_app`（`NOSUPERUSER NOCREATEDB NOCREATEROLE`），与 Dify 的
`dify` / `dify_plugin` 数据库物理隔离，并显式 `REVOKE ALL` 防止 `diyu_app` 连接到那两个库。

选独立数据库而非同库独立 Schema：Postgres 里"能否 CONNECT"是数据库级权限，独立数据库让
"M2 应用连不上 Dify 的表"这件事从物理层面成立，不依赖每次迁移都记得设置 Schema 级 grant；
备份/恢复、连接池、未来独立伸缩也天然按数据库边界走。代价是跨库无法做外键/事务级联，但
M2 与 Dify 之间本来就不该有物理外键——语义边界与地址边界重合是好事。

## 应用后端：Python + FastAPI + SQLAlchemy 2.0 + Alembic

选择依据：仓库现有 `tools/` 目录已是纯 Python 脚本生态，不引入新语言运行时；FastAPI 对
"每个 API 即一个 Pydantic 请求/响应模型"的映射直接，路由/依赖注入足够表达"按 workspace_id
强制作用域"这条硬约束（`require_workspace` 依赖是唯一放行入口）；SQLAlchemy 2.0 的
`Mapped`/`mapped_column` 语法配合 Alembic autogenerate，能把行级乐观并发（`row_version`）、
部分唯一索引（`is_current` 唯一性）这类约束直接声明在模型上，migration 与模型不容易漂移
（已用 `alembic check` 验证零漂移）。

## 迁移与部分唯一索引

`content_versions` / `cycles` / `playbooks` 各自的"当前有效版本只有一条"这条业务不变量，
没有放在应用层做"先查后判断"，而是落成数据库级部分唯一索引
（`CREATE UNIQUE INDEX ... WHERE is_current`）。原因：应用层的 check-then-act 在并发下
天然有竞态窗口；数据库约束是唯一真正原子的最后防线，即使应用代码有 bug 也不会产生两条
"当前版本"。versioning.py 的 `promote_version` 因此需要把两次 `UPDATE` 和 `COMMIT`
包在同一个 `try/except IntegrityError` 里——首次实现遗漏了这点，真实并发测试中复现出
500（而非预期的 409），修复后见 `services/versioning.py` 注释。

## 资料依赖粒度：content_version 级，而非 artifact 级

首次实现把"哪些素材被依赖"挂在 `artifact_id` 上，真实测试中立刻炸出主键冲突——同一
artifact 的两个候选版本引用同一素材时会撞 `(artifact_id, material_id)` 主键，而且级联
失效会错误地波及"没有真的用到该素材"的兄弟版本。改为挂在 `content_version_id` 上后，
撤回素材只精确失效"真的引用了它、且尚未发布"的那些版本，不牵连同一 artifact 下的其他
候选。

## 幂等策略：按端点选择载体，而非统一中间件

创建型写入（task/snapshot/publish_instance/feedback_record）直接在对应表上加
`idempotency_key UNIQUE` 列——重试即命中同一行，语义最直白。晋升/结束这类"改变已有行状态"
的操作（`promote_version`）不适用这个模式（没有新行可去重），改用行级乐观并发
（`row_version` + 数据库唯一索引）保证"重试等于确认当前状态"而不是"重复执行"。
`IdempotencyRecord` 通用账本表已建但目前未接入任何端点——留给未来"幂等键相同但请求体不同
即报错"的场景，暂不引入以避免为不存在的调用方设计。

## Dify 候选：直接 HTTP 调用，不经 LLM

候选工作流是纯 `start -> http-request(...) -> code(JSON 抽出) -> ... -> end` 的线性管线，
不含任何 LLM/问题分类器节点。这是刻意选择：M2 候选只用来验证"持久化层真的可从 Dify
侧被正确调用"，加一层自然语言理解只会把 M1 的职责越权做了，且会让"到底是持久化层的问题
还是 Prompt 理解的问题"变得难以定位。

## SSRF 出网许可

Dify 的 http-request 节点默认经 `ssrf_proxy` 出网，且该代理默认拒绝到私有网段（含
docker `docker_default` 桥接网段）的请求——这是 Dify 自带的合理默认防护，不是本任务引入
的限制。通过 Dify 官方支持的 `SSRF_PROXY_ALLOW_PRIVATE_DOMAINS` 环境变量，只把
`diyu-m2-app` 这一个容器名加入白名单，不放宽对其他私网目标的限制。
