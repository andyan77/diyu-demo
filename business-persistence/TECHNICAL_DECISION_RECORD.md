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

## 独立对抗性审查发现的问题与修复（2026-08-25）

初版实现交付前引入了一次独立的对抗性代码审查（另开 agent、不共享本任务上下文、要求
对真实 Postgres + 真实 API 实测复现，而非只读代码）。审查发现 21 个真实缺陷，其中 6 个
被判定为阻断 Founder 验收级别。以下记录问题本质与修复方式，供未来变更参考；不改写已冻结
的合同文本。

**1. 完全没有身份认证（阻断级）。** 原实现只检查 `workspace_id` 是否存在
（`require_workspace`），任何拿到过一个 workspace UUID 的调用方都能读写它——而 UUID 在
每个 API 响应里都会返回。改为 `require_membership`（`app/api/deps.py`）：调用方必须带
`X-Actor-Ref` header，解析为一个真实 `User`，且该 `User` 必须在目标 workspace 有
`WorkspaceMembership` 行，否则 401/403。所有 workspace 作用域端点统一改用这个依赖。

**2. 幂等键跨租户泄漏（阻断级，3/4 端点命中）。** `publish_instances` /
`feedback_records` 的 `idempotency_key` 原来是全局唯一列，workspace A 的重试请求可能
命中 workspace B 先前创建的行（同一个字符串巧合撞上）。改为在这两张表上加去规范化的
`workspace_id` 列，唯一约束改成 `(workspace_id, idempotency_key)` 复合唯一，查重逻辑
同步只按这个复合键匹配。`tasks` / `task_snapshots` / `cycles` / `content_versions` /
`playbooks` 原本就该如此，一并改正。

**3. 跨 workspace 的 cycle 写入污染（阻断级）。** `create_cycle` 查找"当前 cycle"时未按
`workspace_id` 过滤，理论上可能把另一个 workspace 的 cycle 错误地识别为本次创建要
supersede 的对象。修复：所有相关查询显式加 `workspace_id` 过滤。

**4. 并发写入下的裸 500（阻断级）。** Postgres 对非 deferred 唯一约束在
`db.execute()` 阶段就可能抛 `UniqueViolation`，不是只在 `db.commit()`。多处写入路径原来
只在 `db.commit()` 外包了 `try/except`，并发重试触发裸 500 而非预期的幂等命中或 409。
修复：把可能触发唯一约束冲突的 `db.execute()` 与 `db.commit()` 包进同一个
`try/except IntegrityError`，冲突后重新查询返回既有行（幂等场景）或返回诚实的 409
（互斥场景）。`upsert_run_state` 的首次插入分支同样缺这个处理，独立压测（非原始审查
发现，是修复过程中自行加压测出的）另外确认并修了一次。

**5. 撤回-发布竞态可污染已发布历史（阻断级，重点）。** `withdraw_material` 原实现是
"先 SELECT 哪些版本已发布，再 UPDATE 失效未发布的" —— 两条语句之间有窗口：一个
`register_publish_instance` 恰好在这个窗口内提交，会让一个刚刚变成"已发布"的版本被
错误地标记失效。

第一次修复把 SELECT 和 UPDATE 合并成一条带 `NOT EXISTS` 相关子查询的原子 `UPDATE`
语句，理论上"看起来"原子。但独立并发压测（30 次并发 trial 里出现 1~17 次不等的违反）
证明这个形式并不可靠：Postgres 不保证在等待行锁之后，`UPDATE ... WHERE` 里的相关子查询
会针对最新数据重新求值的方式与顶层列比较完全一致，这条子查询在锁等待发生时没有
可靠地看到发布方最新提交的状态。

真正生效的修复分两部分，且两部分缺一不可：(a) `withdraw_material` 对每个候选
`content_version` 先 `SELECT ... FOR UPDATE` 取锁，锁到手之后才去查是否已发布，最后再
`UPDATE` ——锁、查、写严格拆成三条语句，而不是塞进一条语句里"看起来"原子；
(b) `register_publish_instance` 在写入前必须 `db.refresh(version, with_for_update=True)`
而不能只用 `db.execute(select(...).with_for_update())`——因为 `version` 这个 ORM 对象
已经在本次请求的 Session identity map 里，SQLAlchemy 默认会复用内存里的旧对象、不用新
查询结果覆盖其属性，即使新查询在数据库层确实正确地拿到了锁并等待。不用 `refresh()` 会
让"拿到锁"和"读到锁保护的最新数据"这两件事被悄悄拆开，锁形同虚设。

两处都改完后，专门写的并发压测脚本（`app/api/publish.py` + `app/services/versioning.py`
互相竞态，每轮新建素材+版本，连续 150+ 轮）实测 0 次违反，测试套件里的
`test_withdraw_and_publish_race_never_invalidates_a_published_version_concurrent`
固化了这个回归保护（20 轮并发 trial）。

**6. 素材撤回后仍可被新版本引用（阻断级）。** `create_version` 原来只检查
`material_id` 是否存在，不检查是否已撤回、是否属于本 workspace。修复：新增校验，撤回
后的素材返回 409，跨 workspace 的素材返回 404（与"不存在"同等对待，不泄漏存在性）。

**已知残留、刻意不处理的问题：** `create_version` 的 `version_no` 分配
（`max(version_no)+1`）在同一 artifact 上高并发创建时可能撞 `uq_version_artifact_no`
唯一约束触发裸 500——这不是审查发现的 6 个阻断项之一，本次也未修（不属于本次 Execution
Prompt 授权范围内的"新增重试循环"）。多个候选版本几乎同时创建本身在当前业务场景下
概率低、后果轻（重试即可），留待未来若真实出现再处理，此处明确披露而非隐藏。
