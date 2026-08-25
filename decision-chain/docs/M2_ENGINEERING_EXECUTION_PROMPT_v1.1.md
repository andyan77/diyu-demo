# Execution Prompt — M2 业务持久化、版本、发布实例、反馈与任务投影 v1.1

## 0. 使用方式与任务身份

本文件是 W2 编译的 M2 完整根 Execution Prompt。它用于交给 M2 专属工程执行终端，在 Founder 对本文件准确版本明确授权后执行。它是一份覆盖 M2 全部 P0 的长期任务合同：执行总负责人应在同一 `task_id` 下自主侦察、拆解、实现、自验、隔离审查、定向修复、受影响范围复验、目标环境部署和交付 Founder 实测包；不得把内部阶段拆成新的根 Prompt。

v1.1 在 v1.0 完整合同上补齐开发/测试数据建设与迁移授权、Dify 候选交付、Founder 画布验收、单次隔离 Reviewer 预算和同任务续作机制。v1.0 作为历史候选保留，不得覆盖；工程执行只能以 Founder 明确授权的准确版本为准。

本 Prompt 当前只完成规划编译；它没有被本规划窗口执行，也不因文件存在而自动授权工程施工。执行终端不得把本 Prompt 再解释为 M1、M3、M4 或 M5 的合并任务。

```text
M2_ENGINEERING_EXECUTION_PROMPT = READY_FOR_FOUNDER_USE
engineering_execution_performed = false
```

任务进入模式为 `NEW_TASK`。稳定任务身份为：

```yaml
task_id: DIYU-V1-M2-BUSINESS-PERSISTENCE-VERSION-FEEDBACK-001
task_entry_mode: NEW_TASK
task_type: MIXED
risk_level: HIGH
```

若执行时已经存在同一 `task_id` 的 Manifest、分支、worktree、数据库副作用或 Checkpoint，必须先按现行协议核验并改判为 `CONTINUE_TASK`、`RECOVERY_TASK` 或 `REBASE_TASK`；不得重建新任务、重复迁移或覆盖既有副作用。

---

## 1. 现行治理与真源

### 1.1 现行规划与执行协议

```yaml
planning_protocol:
  protocol_id: DIYU-EXECUTION-PROMPT-PLANNING-COMPILER
  version: "1.2"
  path: /mnt/c/Users/Administrator/Documents/Codex/Diyu-V1-Planning/执行Prompt生成总则_规划侧约束框架_v1.2.md
  sha256: 8023bf3e21ff8fb9ba9a2e81b95d1afb178ebf1c04545d0deaac709f603b05b8
execution_protocol:
  protocol_id: DIYU-BOUNDED-EXECUTION-OWNER-PROTOCOL
  version: "1.3"
  path: /mnt/c/Users/Administrator/Documents/Codex/Diyu-V1-Planning/受边界约束的执行总负责人协议_v1.3.md
  sha256: 3ba07a67784056f36211ac634e25a948ce8482f1831aa3dbdc6ab5945ccffcfc
planning_workspace_rules:
  path: /mnt/c/Users/Administrator/Documents/Codex/Diyu-V1-Planning/AGENTS.md
  sha256_at_prompt_compile: af4374972b9843345abb1ea5cf1ac863960a316c6c49170131145a212968d6d2
```

执行前复算以上哈希。哈希变化不自动意味着合同失效，但必须核验准确版本是否仍由 Founder 接受；不得自行把新版本当作现行协议。

### 1.2 产品、共享合同与项目事实真源

```yaml
planning_prd:
  path: /mnt/c/Users/Administrator/Documents/Codex/Diyu-V1-Planning/笛语_V1_单账号持续内容运营纵向切片统一构建规划_v0.3.md
  sha256_at_prompt_compile: b25d17865553dd906e262694f71f0cb030262be93030d43a19f735ea3d0b9e27
project_repository:
  path: /home/faye/diyu-demo
  remote: https://github.com/andyan77/diyu-demo.git
upper_product_contract:
  path: decision-chain/docs/V1_DECISION_CHAIN_REBASE_PRODUCT_CONTRACT_v0.1.md
  sha256_at_prompt_compile: 9a57d255dec44477ceb38f6f61faaa5f43d36343f89803364eac5df6d5fc5ca0
single_account_contract:
  path: decision-chain/docs/V1_SINGLE_ACCOUNT_SLICE_CONTRACT_v0.2.md
  sha256_at_prompt_compile: 677c7f350410b934b5e25caa3cf98f4665a48936588adc66798d093b042ece9d
general_preflight:
  path: decision-chain/docs/V1_REBASE_EP00_CURRENT_PREFLIGHT_v0.1.md
  sha256_at_prompt_compile: afea2d975b1e214ee57aaaab3bfaee63bb6d0319403bfe6d8e66285c2b1bce11
single_account_preflight:
  path: decision-chain/docs/V1_SINGLE_ACCOUNT_SLICE_EP00_PREFLIGHT_v0.1.md
  sha256_at_prompt_compile: 921091b5a43fb72371c5c95e6bb07e6ccd87db6baa29fb9cff2716e5dd2fbc4d
shared_contract_task_context:
  path: decision-chain/docs/V1_M0_SHARED_CONTRACT_TASK_CONTEXT_SNAPSHOT_v0.1.md
  sha256_at_prompt_compile: 76b730d47566eccc188e2dbb0c4da2e8aa594936cc813987cc8d0fd7901bd63b
shared_contract_capabilities:
  path: decision-chain/docs/V1_M0_SHARED_CONTRACT_EIGHT_CAPABILITIES_v0.1.md
  sha256_at_prompt_compile: 6d3fb85ebce417c4d34103775f833656dab7d62e390b0c9ba482ccc9108e8a30
shared_contract_version_publish_feedback:
  path: decision-chain/docs/V1_M0_SHARED_CONTRACT_VERSION_PUBLISH_FEEDBACK_v0.1.md
  sha256_at_prompt_compile: 67af3e991394fb27964470bcdbf5a46678a494e4045db60eb573b31ea924ee2b
shared_contract_write_permission_recovery:
  path: decision-chain/docs/V1_M0_SHARED_CONTRACT_WRITE_PERMISSION_RECOVERY_v0.1.md
  sha256_at_prompt_compile: 108209b52df232e91e06b5726b2c19eb6094f06eb7025971a958750143a172f0
phase0_shared_preamble:
  path: decision-chain/docs/V1_M1_M4_CONSTRUCTION_PROMPT_SHARED_PREAMBLE_v0.1.md
  sha256_at_prompt_compile_on_current_main: 210ccf7407498a9566ff99aa1486a0815abb53879705aff83448252a2a58a388
```

说明：规划桌面快照中的 Phase 0 前言哈希 `9b046e...` 对应采用前的原始附件；当前远程 `main` 已在状态收口任务中更新其 YAML 状态块，现场文件哈希为 `210ccf...`。执行时以远程默认分支的当前文件和账本为准，不得用桌面快照旧哈希覆盖当前仓库事实。

### 1.3 权威域

- Founder 当前明确裁决、已接受产品合同与四份共享合同决定产品语义、责任边界与验收口径。
- 本 Prompt 决定本次 M2 P0、授权范围、受保护资产、非目标和验收合同。
- 远程默认分支、当前工作区、PostgreSQL、Dify 实际对象和原始运行证据决定“现在是什么”。
- EP-00 报告是经核验的历史时点证据；执行时动态事实必须刷新。若当前事实与报告不同，记录 Delta，不得反向修改已接受产品目标。
- `V1_TASK_SNAPSHOT_SCHEMA_v0.1.json` 是旧 Demo 会话态 Schema，只能作为兼容输入证据，不能成为未来业务持久化 Schema 的物理蓝图。

---

## 2. 规划编译时的现场基线与最小工程路径

### 2.1 现场基线

W2 首次于 `2026-08-25T05:48:48-07:00` 完成完整现场核验，并于 `2026-08-25T07:06:46-07:00` 再次刷新远程默认分支、`origin/main`、本地 `main` 和工作树状态：

```yaml
repository: /home/faye/diyu-demo
remote_default_branch: main
remote_default_branch_source: git ls-remote --symref origin HEAD
remote_main_commit: 2a0822692802ac084d92e032f098da33079f063d
local_branch: main
local_head: 2a0822692802ac084d92e032f098da33079f063d
local_origin_main: 2a0822692802ac084d92e032f098da33079f063d
working_tree: clean
postgres_runtime: PostgreSQL 15.19, docker-db_postgres-1, healthy
existing_non_template_databases: [dify, dify_plugin, postgres]
existing_non_system_schemas_in_dify: [public]
dify_version_observed: 1.16.1
```

当前事实：

- 当前全部持久状态仍是 Dify 内部状态；任务快照和产物按 `conversation_id` 存于 `workflow_conversation_variables`，同槽覆盖、跨会话不延续。
- 现场计数仍与 EP-00 一致：`workflow_conversation_variables=1033`、`conversations=253`、`messages=622`、`workflow_runs=738`、`workflow_node_executions=5704`。
- 没有笛语业务数据库、业务 Schema 或应用后端数据层；没有运营周期、内容任务版本历史、发布实例、反馈归属、服务端业务身份或工作空间隔离载体。
- 可以复用的工程基础包括：健康的 PostgreSQL 15 运行实例；现有内容寻址身份与追溯字段所表达的能力（如内容哈希、父产物引用、Skill/Run/夹具版本引用）；跨阶段哈希回验；从运行系统读回确定性事实的既有路径。
- 不能复用为业务真源的对象包括：Dify 会话变量、Dify 内部账号/租户表、Dify 消息反馈表、Dify 运行历史和测试身份。它们属于 Dify 平台内部实现或工程回归证据，不是笛语业务身份、真实发布历史或经营数据。

执行时必须重新 `fetch` 并刷新上述动态事实。若远程默认分支、数据库拓扑、现有 M2 分支或外部副作用已变化，按现行协议重判进入模式与复验面。

### 2.2 已选择的最小工程路径

本 Prompt 已依据当前现场选择以下方向，执行侧不得把它改写为“另建一套数据库平台”：

> 复用当前 PostgreSQL 15 运行基础，在其上建立由笛语应用后端拥有、与 Dify 内部表和权限隔离的最小业务持久化边界；Dify 只通过受权限约束的应用接口取得当轮最小投影，不直接读写业务库。

这项选择冻结的是“复用现有 PostgreSQL 运行基础、业务真源与 Dify 内部存储隔离”，不冻结：

- 独立数据库还是独立 Schema；
- 物理表名、字段名、索引名、枚举名；
- ORM、迁移框架、API 路由和代码目录；
- 具体事务拆分和内部模块组织。

执行侧在刷新部署、权限、备份/恢复和并发前提后，自主选择独立数据库或独立 Schema 中更小且安全的实现，并把依据、隔离证明和迁移/回滚证据写入任务证据。除非真实证据证明当前 PostgreSQL 无法满足隔离、权限、迁移或恢复要求，否则不得启动新的数据库服务；若确实无法满足，必须按治理阻塞提交证据，不得静默扩建。

---

## 3. 稳定 Task Contract

下面 `TASK_CONTRACT_BEGIN` 与 `TASK_CONTRACT_END` 之间 YAML 代码块的块内 UTF-8 字节是稳定 Task Contract 的哈希对象；围栏和标记不计入。

<!-- TASK_CONTRACT_BEGIN -->
```yaml
contract_version: "1.1"
task_id: DIYU-V1-M2-BUSINESS-PERSISTENCE-VERSION-FEEDBACK-001
task_entry_mode: NEW_TASK
parent_task_id: ""
task_type: MIXED
risk_level: HIGH

authority_refs:
  - Founder 明确要求编译 M2 业务持久化、版本、发布实例、反馈与任务投影施工 Prompt
  - Founder 要求现场核验当前默认分支、现有 PostgreSQL、已有对象和运行基础后选择最小工程路径
  - Founder 已接受单账号纵向切片合同 v0.2、M0.3 四份共享合同和 Phase 0 共享编译前言当前语义
  - Founder 已接受规划协议 v1.2 与执行协议 v1.3 的准确哈希版本
  - Founder 补充裁决：M2 以一条完整 Root Execution Prompt 覆盖模块全部 P0；中断使用同一 task_id、Checkpoint 和 CONTINUE_TASK
  - Founder 补充裁决：执行侧完成技术验收和一次隔离只读 Reviewer 审查；Founder 只通过 Dify 画布做产品与业务实测
  - Founder 补充授权：M2 可在指定开发/测试环境内完成必要数据建设、迁移、Dify 候选部署与运行；生产环境和受保护资产仍需独立裁决

final_deliverable: >-
  在独立 M2 分支、worktree 和受控目标环境中形成可运行的最小业务持久化与应用后端能力：
  跨会话恢复用户/工作空间/主体/账号/周期状态，保存任务快照与按需投影，区分当前有效版本和历史版本，
  准确记录内容任务、产物、内容版本、发布实例、反馈和市场观察，严格隔离真实/测试/模拟/人工证据，
  支持 Campaign 覆盖恢复、资料撤回、幂等写回、并发控制和失败恢复；完成迁移、兼容、目标环境运行、
  定向回归、独立审查、证据和远程任务分支收口；在 Founder 指定的开发/测试 Dify 环境形成可回滚的 M2 候选入口和实测包，
  支持 Founder 通过“首次任务→保存状态→再次进入→发布记录→导入反馈→下一周期读取”完成产品与业务验收，
  并在同一 task_id 下处理范围内退回；不越权形成 M1 路由、M3 策略或 M4 生产能力。

core_problem: >-
  当前系统的状态全部局限在 Dify 会话变量中：同槽覆盖、跨会话不延续，没有笛语业务身份、工作空间隔离、
  周期和任务历史、当前版本原子晋升、准确发布实例、反馈归属、素材撤回、并发控制或恢复载体。
  因此系统可以完成单次 Demo，但不能诚实声称具备跨会话、跨周期持续运营闭环。

observable_changes:
  - 用户、工作空间、表达主体、账号和运营周期具有稳定、可恢复且受权限隔离的业务身份
  - 任务上下文快照可持久化，并可按当前任务、权限、作用域和时效编译最小投影
  - 当前有效版本与历史版本严格分离，旧版可读取、可比较、可回退，模型自评不能自动替换当前版
  - 内容任务、决策/生产产物、内容版本、发布实例和效果观察具有准确且不可混淆的身份与关系
  - 真实、测试、模拟、发布前人工评价、发布后人工录入和真实市场结果不能互相升级或混入
  - 反馈只能绑定准确发布实例、准确内容版本、账号、平台、观察窗口、来源和当时经营目标
  - Cycle N 的观测和解释假设可成为 Cycle N+1 的输入，但 M2 只记录和投影，不替 M3 决定调整
  - Campaign 覆盖只占用点名范围，结束后恢复仍有效的周期基线，历史已发布内容不被改写
  - 账号基线产能、当前周期实际产能和用户期望发布量分别保存和投影
  - 市场观察保留来源、平台、采集时间、适用范围、权限、时效和证据状态
  - 可跨内容任务验证的打法及其观察状态可被记录；变化由 M3 提议，M2 不定义专业规则
  - 用户撤回资料后，该资料退出未来投影，依赖它的未发布对象局部失效，历史发布不被静默改写
  - 同一业务请求重试不会重复创建周期、任务、内容版本、发布实例或反馈；失败可从最近提交点恢复
  - Dify 内部表和会话记忆不再承担笛语业务真源，Dify 仅获得当前工作空间的最小授权投影
  - 既有 Demo 会话态和历史产物保持可读/可适配，不要求用户重新录入，不污染真实业务历史
  - Founder 指定开发/测试 Dify 中存在可回滚、可追溯且只承载 M2 验收路径的候选应用或工作流入口
  - 技术验收由执行负责人、确定性检查器和隔离只读 Reviewer 完成；Founder 不承担 Schema、迁移、节点、测试或 Git 审核
  - 技术候选完成后持久化 AWAITING_FOUNDER_DIFY_ACCEPTANCE Checkpoint；Founder 退回时沿用同一 task_id 定向续作

authorized_scope:
  read:
    - /home/faye/diyu-demo 全仓库、Git 历史、远端 refs、worktrees、collab-ledger 和当前任务状态
    - 当前已接受产品合同、两份 EP-00、四份共享合同、Phase 0 前言、统一构建规划和 M2 证据
    - 当前 PostgreSQL/Dify 的只读结构、版本、权限、运行状态、必要统计和与 M2 直接相关的原始证据
    - 与业务身份、任务快照、产物身份、版本、发布、反馈、权限、并发、迁移和恢复相关的当前实现
  write:
    - M2 独立 worktree 和任务分支内，为完成 M2 所必需的应用后端、持久化、迁移、适配、测试、文档和证据
    - collab-ledger 中本 task_id 的 Manifest、Attempt、失败路径、验收和外部副作用记录
    - 经入口门核验后，在 Founder 指定开发/测试环境的 M2 应用自有隔离边界内创建和迁移业务对象及测试数据
    - 在 Founder 指定的开发/测试 Dify 环境内，创建一个新的 M2 候选应用/工作流，或更新已明确划给本任务的 M2 候选对象；保存前后版本、导出、对象 ID 和回滚证据
    - 为 Founder 实测保存候选配置、代表性测试身份/夹具、入口说明、预期观察点、已知限制和验收回执
  execute:
    - 仓库侦察、依赖安装、静态检查、迁移 dry-run、迁移/回滚验证、单元/集成/并发/权限/恢复/回归测试
    - 在受控开发/测试目标环境运行 M2 应用后端、业务持久化和契约测试；读取 Dify 投影接缝，不改专业 Skill
    - 导入、创建、更新、校验并发布 Founder 指定开发/测试 Dify 中的 M2 候选版本，执行真实画布运行、失败恢复和回滚演练
    - 建立独立 task 分支和 worktree，commit，推送远程 task 分支并核验远端 hash
    - 启动一次独立只读正式审查和一次限定闭环复验
  network:
    - fetch origin、读取远端 refs、推送 M2 任务分支
    - 在现有授权和凭证范围内访问当前本地 PostgreSQL 及 Founder 指定开发/测试 Dify 环境；允许完成 M2 候选导入、更新、发布、运行、回滚和 Founder 访问准备
    - 不访问或操作社交平台账号，不调用自动发布或全平台效果采集

non_goals:
  - 建设 M1 自然语言意图编译、能力选择、对话编排或第二套路由
  - 形成 M3 账号阶段、周期目标、内容比例、节奏、实验、复盘或打法变化的专业判断
  - 实现 M4 的组件调用、Skill 适配、局部重跑、创意、脚本、制作或发布包装能力
  - 新建或修改 Skill，全面改写六份既有 Skill，修改其专业判断或模型参数
  - 自动发布、平台 OAuth、社交平台凭证管理、全平台效果采集、投流、直播或交易系统
  - 修改真实生产 Dify 应用、生产工作流、线上已发布版本或共享画布；M2 新建/明确划拨的开发测试候选除外
  - 要求 Founder 审核代码、文件组织、Schema、节点连线、迁移、单元测试、普通技术缺陷或 Git 规范
  - 通用数据库平台、数据中台、重型事件溯源、复杂字段级权限、完整合规/删除平台、完整数字资产管理系统
  - 全平台市场数据库、爬虫、领域知识库、RAG-first、自动训练、自动修改 Prompt/Skill/权重
  - 冻结数据库表名、字段名、API、打法物理枚举、M3 判断规则、固定内容比例或阶段迁移算法
  - 把 Dify Memory、Dify 内部租户/账号/消息反馈表或会话原文直接升级为笛语业务真源
  - 迁移、重标或删除既有 Dify 测试运行，使其冒充真实账号、真实发布或真实经营反馈
  - 合并或推送 main，force、amend、reset、squash、改写历史，删除其他分支/worktree 或覆盖其他任务改动
  - 修改已接受产品合同、四份共享合同、Phase 0 前言、冻结验收 Oracle 或受保护证据

accepted_baseline:
  - origin/main @ 2a0822692802ac084d92e032f098da33079f063d（规划编译时现场核验；执行前必须刷新）
  - 当前默认基线已包含已接受的下位合同、两份 EP-00、四份共享合同和 ACTIVE Phase 0 前言
  - 当前 PostgreSQL 15.19 实例与 Dify 1.16.1 运行基础可用，但不存在笛语业务持久化边界
  - 现有内容寻址身份、父产物引用、Skill/Run/夹具版本引用和哈希回验能力可作为兼容基础
  - 现有 Dify 会话变量、运行历史和测试身份只作旧 Demo 兼容与工程证据，不是业务真源

allowed_delta:
  - 复用现有 PostgreSQL 运行基础，建立应用后端拥有且与 Dify 内部表隔离的最小业务持久化边界
  - 实现 M2 责任内的身份、工作空间隔离、业务记录、版本、发布实例、反馈、市场观察、权限和恢复能力
  - 实现任务上下文快照的持久化、按需投影和与 M1/M3/M4 的最小稳定接口
  - 实现当前版本原子晋升、历史保留、真实依赖的局部失效、幂等键、乐观并发/事务和恢复检查点
  - 为旧 Dify 会话态、Matrix/Campaign/Brief/生产产物建立最小兼容读取或显式导入适配，不把旧测试数据升级为真实数据
  - 对 M2 Delta 直接或传递影响的应用后端、测试和有限集成接缝进行最小必要修正与局部重构
  - 生成完成 M2 所必需的迁移、回滚、契约测试、有限夹具、原始证据和运维说明

protected_assets:
  - 已接受上位合同、下位合同、四份共享合同、Phase 0 前言和统一验收语义
  - Dify 现有数据库、表、会话、消息、运行历史、生产/共享应用、线上发布版本和平台内部权限数据；仅明确划给本 task_id 的开发测试 M2 候选对象可按授权修改
  - Matrix/Campaign/Content Brief/Creative Script/Production Director/Publishing & Packaging Skill、DSL、工作流和模型参数
  - 冻结 fixtures、references、evidence、运行合同、原始失败 Attempt 和历史发布/运行记录
  - M1 的意图与路由决定权、M3 的运营专业判断权、M4 的组件执行和生产能力责任
  - 用户确认事实、工作空间隔离、素材权限、当前有效版本和真实发布历史
  - 其他并行任务的分支、worktree、账本分区、候选、Attempt、失败路径和外部副作用记录
  - 社交平台账号、凭证、发布权限和任何真实外部发布

target_environment:
  repository: /home/faye/diyu-demo
  branch: task/m2-business-persistence-version-feedback-v1
  worktree: 独立 worktree，由执行时依据真实 Git/worktree 状态安全建立或恢复
  database_runtime: 复用当前 PostgreSQL 15 运行基础；M2 应用自有隔离边界
  application_runtime: 执行侧依据当前仓库选择最小应用后端形态，不新建第二套工作流引擎
  dify_environment: Founder 指定的本地或开发/测试 Dify；禁止默认为生产环境
  dify_candidate_scope: 优先复用已明确划给本 task_id 的 M2 候选；若不存在，可新建一个仅用于 M2 接缝和 Founder 验收的最小候选应用/工作流
  dify_publish_permission: 允许导入、更新并发布该开发/测试候选版本；不授权修改生产/共享应用或真实对外发布
  dify_role: 只消费最小任务投影并返回生成结果/建议，不持有业务数据库管理权限

admission_gate:
  - 远程默认分支仍可访问，当前基线、工作区和并行任务状态已刷新
  - 下位合同 v0.2、四份共享合同和 Phase 0 前言当前状态可从默认分支核验
  - Founder 已针对本 Prompt 准确版本明确授权 M2 工程执行
  - M2 独立分支、worktree、账本写入区和数据库隔离边界不存在未解析写者冲突
  - PostgreSQL/Dify 当前状态与外部副作用已只读核验，不存在 UNKNOWN 状态下的重复迁移风险
  - Task Contract、Run Manifest、迁移目标、回滚/恢复方法和受保护对象已在首次写入前实例化
  - Founder 指定开发/测试 Dify 环境可访问；候选对象的精确 ID、当前版本、备份/导出、写权限、发布权限和回滚路线在首次 Dify 写入前实例化
  - 若执行时只存在生产/共享 Dify 对象且无法安全建立隔离候选，必须停止该分支并请求授权，不得就地修改

p0:
  deliverables:
    - M2 应用后端与最小业务持久化的可运行实现
    - 可恢复的用户/工作空间/主体/账号/周期/任务/产物/版本/发布/反馈/市场观察业务能力
    - 任务上下文快照持久化和按权限/作用域/时效的最小投影接口
    - 当前有效版本原子晋升、历史保留、资料撤回局部失效、幂等/并发/失败恢复实现
    - 旧 Demo 会话态与历史产物的最小兼容适配和真实/测试/模拟证据隔离
    - 迁移、回滚、备份/恢复、权限隔离、正向/负向/并发/恢复/回归的原始证据
    - 独立审查、任务账本、Git commit 和远程任务分支收口
    - Founder 指定开发/测试 Dify 的可回滚候选部署、真实画布运行和 Founder 实测包
    - Founder Dify 产品与业务验收回执，或同一 task_id 下可恢复的等待/退回 Checkpoint
  acceptance_criteria:
    - M2-AC-00 至 M2-AC-17 全部 PASS，且证据对最终候选仍为 CURRENT

p1:
  enabled: false
  deliverables: []
  acceptance_criteria: []
  permitted_next_stage: NONE

allowed_final_states: [DONE, BLOCKED, FAILED, INVALID]

p2_evidence_requirements:
  - 每项验收绑定最终代码/迁移哈希、输入、Oracle、数据库/应用版本、环境、观察时间和验证主体
  - 保留每个 Formal Attempt、迁移 Attempt、失败输出、回滚结果、已证伪路径和实质差异，不选择性删除
  - 数据库写入、迁移和远程推送按 task_id 记录副作用标识、目标、内容哈希、幂等信息、原始响应和状态
  - 任何 STARTED 或 UNKNOWN 的迁移/外部副作用在重试前先查询目标系统，不得盲目重放
  - 测试/模拟/人工导入数据带清晰身份；真实用户资料、凭证和隐私不得明文进入仓库或评审包
  - 证明 Dify 自有表零结构/数据改写，或逐项披露经明确授权的最小接缝变化
  - 保存迁移前后结构、权限、隔离、备份/恢复和旧记录可读性的可复算证据
  - 保存 Dify 候选对象 ID、导入/发布版本、画布配置、运行 ID、输入输出、回滚结果和与最终 commit/配置的绑定
  - Founder 回执只证明产品与业务验收；不得拿 Founder 画布通过替代数据库、迁移、权限、并发、恢复或独立审查证据

acceptance_oracles:
  - 本 Prompt 第 9 节 M2-AC-00 至 M2-AC-17
  - 已接受共享合同一、三、四及共享合同二/Phase 0 前言中 M2 接缝的冻结业务语义
  - 单账号纵向切片合同 v0.2 第 3、4、6、7、8 节与统一构建规划 M2/M5 适用验收
  - 两份 EP-00 的 M2 当前事实、生产 Gap G-01/G-02/G-03/G-04/G-05/G-06/G-07 和执行时刷新证据
  - 真实 PostgreSQL/Application 运行、确定性测试、并发/故障注入和独立审查；不以模型自评或文件存在代替
  - Founder 指定开发/测试 Dify 的当前候选画布、真实运行与 Founder 产品/业务验收；不要求 Founder 审核技术实现

evidence_reuse_policy:
  default: EXACT_BINDING_ONLY
  final_full_run_required: true
  dynamic_evidence_requires_refresh: true
  criterion_dependency_map:
    - 数据模型、迁移、权限、事务、投影或恢复实现变化时，其直接与传递影响验收必须重验
    - 当前版本晋升、发布/反馈身份或撤回失效实现变化时，相关正向和负向探针必须重验
    - PostgreSQL/Dify/应用版本、最终 commit 或配置变化后，旧目标环境与独立审查证据自动 STALE
    - Dify 候选画布、应用后端、数据接口或 Founder 实测夹具变化后，M2-AC-16 与 M2-AC-17 的受影响证据必须刷新
    - 未受影响的既有 Skill/生产链证据可引用，但不能据此声明 M2 集成或 M5 已完成

verification_authority:
  executor_self_check:
    - 静态检查、迁移检查、单元/契约/集成/权限/并发/恢复/负向/回归测试和证据完整性
  deterministic_checkers:
    - 当前仓库仍适用的验证工具、数据库约束、事务结果和为 M2 建立的可复算检查
  independent_reviewer:
    - 未参与候选实现、上下文隔离、默认只读的独立 Reviewer
  founder_authority_scope:
    - 通过 Dify 画布判断真实用户交互、产品意图和业务价值，并接受或退回模块阶段交付
    - 新产品语义、M3 专业规则、验收口径、授权扩大、受保护能力、风险接受和真实对外动作
    - Founder 不承担文件、Schema、节点、迁移、测试、Git 或普通技术缺陷审核

review_model:
  executor_self_verification: required
  independent_reviewer: one_context_isolated_read_only_agent
  reviewer_write_permission: false
  formal_review_budget: 1
  repair_budget: 1
  closing_verification: affected_scope_only

review_contract:
  required: true
  authority: 未参与实现、上下文隔离、默认只读的独立 Reviewer
  scope:
    - M2-AC-00 至 M2-AC-17 的证据充分性、数据身份和跨模块边界
    - 工作空间隔离、权限、当前版本晋升、发布/反馈绑定、撤回、幂等、并发、迁移和恢复安全
    - 真实/测试/模拟/人工证据隔离与工程闭环/真实运营/经营提升三类结论是否被准确限制
    - 是否误改 Dify 内部表、冻结资产、M1/M3/M4 责任或引入通用数据库平台
  budget: >-
    一个上下文隔离、只读 Reviewer；一次正式审查；一个定向修复预算；收口仅复验受影响范围。
    Reviewer 不改代码、不新增标准、不指定 HOW，不开启第二轮开放式审查。
  closure_rule: >-
    Reviewer 只能提出两类阻断：明确违反某条验收标准；明确违反安全、权限、受保护资产或数据完整性边界。
    每项必须同时给出 criterion_id、可复核证据和受影响范围。命名偏好、文档排版、“可以更优雅”、
    无验收映射的重构建议、没有基线证据的“能力下降”及 Reviewer 偏好实现方案均不得阻断交付。

completion_checks:
  artifact_persisted: REQUIRED
  target_environment_run: REQUIRED
  fixed_configuration_run: REQUIRED
  positive_tests: REQUIRED
  negative_tests: REQUIRED
  regression_tests: REQUIRED
  raw_evidence_preserved: REQUIRED
  dify_candidate_run: REQUIRED
  founder_dify_acceptance: REQUIRED_FOR_DONE
  git_closure: REQUIRED
  remote_closure: REQUIRED

retry_policy:
  transient_retry_allowed: true
  maximum_authorized_attempts: RUNTIME_OR_TASK_DEFINED
  blind_resampling_allowed: false
  all_attempts_must_be_preserved: true

remote_target:
  repository: https://github.com/andyan77/diyu-demo.git
  branch: task/m2-business-persistence-version-feedback-v1
  required_proof:
    - 远程任务分支存在且接收方可访问
    - 本地最终 commit 与远端任务分支 hash 一致
    - 数据库迁移/应用候选版本与最终 commit、配置和证据相互绑定
    - Dify 候选对象、发布版本、运行证据和 Founder 实测入口与最终 commit/配置相互绑定
  forbidden:
    - 合并或推送 main
    - force、amend、reset、squash、删除其他分支或改写历史
    - 未经独立授权修改真实社交平台、自动发布或采集真实效果

next_stage_default: false
```
<!-- TASK_CONTRACT_END -->

`task_contract_hash`：`e17b354b97d53bfa52eeb30ffca50970e5469acabee98b3cfc32a1031b1b90ca`。执行者必须独立重算并登记进 Run Manifest。不得把当前进度、实施计划、会话摘要或实际验收结果混入稳定合同哈希。

---

## 4. 入口门、基线锁定与隔离

### 4.1 首次写入前

执行侧必须：

1. 读取 `/home/faye/diyu-demo/CLAUDE.md`、`笛语项目基线.md`、协作账本当前态、两份 EP-00、四份共享合同和 Phase 0 前言；
2. `fetch origin` 并核验远程默认分支、`origin/main`、本地 HEAD、工作树、现有 worktree、同名任务分支和同 `task_id` 账本；
3. 只读核验当前 PostgreSQL 版本、数据库/Schema、权限、备份/恢复条件、Dify 内部对象和任何既存 M2 副作用；
4. 编译完整 Run Manifest、Task Contract 哈希、实际 target、迁移目标、回滚/恢复方法和副作用标识；
5. 只读核验 Founder 指定开发/测试 Dify 的候选对象、当前发布版本、写权限和回滚条件；若不存在明确候选，可按本 Prompt 授权新建一个最小 M2 候选，但不得修改生产/共享应用；
6. 冻结 Founder 实测所用的测试身份、工作空间、账号、周期、发布和反馈夹具；夹具必须明确为测试，不得冒充真实经营数据；
5. 从当时远程默认基线建立或恢复独立 M2 worktree 与任务分支；不在主工作区直接施工；
6. 记录用户原有改动并隔离，不得吸收、覆盖、删除或冒充其他任务变更。

远程 `main` 如果已前进但产品合同和授权未改变，按真实差异判定是否 `REBASE_TASK` 并做定向影响分析；不得静默使用本 Prompt 编制时的 `2a082...`，也不得无理由从头重做。

### 4.2 数据库隔离门

在创建任何数据库对象或测试数据前，必须证明：

- 目标属于 M2 应用自有边界，不是 Dify 内部 `public` 表的扩写；
- 应用身份只拥有完成 M2 所需的最小权限，Dify/模型没有数据库管理权限；
- 测试/模拟数据与任何真实业务数据隔离且可识别；
- 迁移具有可重复的 dry-run、失败检测、恢复或回滚路径；
- 不会覆盖当前有效版本、历史 Dify 记录或其他任务数据；
- 迁移副作用在账本中处于可安全执行状态，而不是 `STARTED`/`UNKNOWN`。

如果当前 PostgreSQL 无法在不破坏 Dify 和其他任务的前提下形成隔离边界，只暂停数据库写入分支，完成其他可安全准备工作后提交精确治理阻塞证据。不得把普通表名、ORM、数据库/Schema二选一上推 Founder。

---

## 5. Active Work Package：M2 P0

### 5.1 真实侦察与技术定位

- 先识别当前仓库是否已有应用后端、迁移框架、身份边界、配置载体和测试运行方式；不存在时选择最小可运行形态。
- 复用现有 PostgreSQL 运行基础和已验证的内容寻址/哈希追溯思想，但不复制 Dify 平台内部 Schema。
- 验证现有对象哪些能作为兼容引用，哪些只能作为旧 Demo 证据；不得因名称相似就合并业务身份。
- 给出数据库/Schema、应用后端、迁移和接口 HOW 的简洁技术决策记录，说明为什么是当前最小充分方案；该记录不晋升为产品合同。
- 仅处理 M2 直接影响的仓库、运行和回归面；不开放式复验全部 Skill 或全仓历史。

### 5.2 最小身份与可恢复业务状态

实现能够稳定区分并恢复的业务关系：

- 用户身份；
- 当前工作空间及用户对该工作空间的访问关系；
- 表达主体；
- 单账号；
- 运营周期；
- 任务和当轮快照；
- 资料/素材索引与授权状态；
- 产物、内容版本、发布实例、反馈和市场观察。

同一用户可以在授权下进入多个工作空间，但每次读取、写入和投影均受当前工作空间隔离。个人工作空间与企业工作空间不得无授权混用。第一阶段只实现支撑纵向切片所需的最小身份和权限，不建设通用多租户管理平台。

普通咨询、临时创意讨论和无持久化诉求的单次任务不强制形成账号档案；但系统不得在未持久化时声称跨会话持续运营成立。

### 5.3 信息五维与任务上下文投影

持久化和投影必须保留共享合同冻结的五个正交维度：

1. 信息性质：事实、偏好、参考、系统判断；
2. 来源与证据；
3. 确认和生命周期状态；
4. 作用域与有效期；
5. 可用性状态。

物理实现不要求每条记录机械拥有五个同名字段，但必须能无损表达和测试这些差异。系统推断不能因为落库就升级为用户确认事实；参考、市场观察和旧产物不能覆盖用户确认事实。

任务快照持久化至少承载共享合同一的业务语义，并保留本轮主诉求外的附带诉求、运行中新增证据和必要原话/资料引用。对 M1/M3/M4 输出的运行载荷必须是当前任务真正需要、仍有效、在权限内的最小投影；不把整个账号历史或租户数据塞给模型。

### 5.4 周期、Campaign 覆盖与产能三分

- 周期基线和当前有效周期版本必须可恢复；历史周期保留且不可被下一周期反向改写。
- Campaign 可以独立存在，也可以作为有明确时间/范围的周期覆盖层；覆盖只占用点名内容位置，不静默改写其他周期任务。
- 当轮投影必须能回答“当前是否存在有效 Campaign 覆盖、覆盖哪一段周期/哪些内容位置、何时生效与退出、覆盖依据是什么”；这些是必须可观察的业务语义，不要求冻结物理状态枚举。
- 覆盖结束、取消或到期后，恢复当时仍有效的周期基线；如果基线在覆盖期间已合法更新，恢复的是最新仍有效基线，不是盲目回滚到旧快照。
- 已发布内容和发布实例始终保留为历史，不因覆盖退出或上游后来变化而失效。
- 账号/团队基线产能、当前周期实际可用产能、用户期望发布量必须分别记录、分别投影、分别有来源/作用域；M2 不选择减量、延期、调结构、增资源或不发，由 M3/用户裁决。

### 5.5 内容任务、产物、内容版本与当前版本

必须在业务语义上准确区分：

- 内容任务；
- 决策或生产产物及其修订；
- 候选和发布前人工评价；
- 当前有效内容版本；
- 历史内容版本；
- 制作过、被选中过、已发布等累积里程碑。

“生成过、被选中过、制作过、已发布、已观察到效果”不是五个互斥状态。执行侧可自主选择状态表达，但不能把它们压成一个会丢事实的单一枚举。

当前有效版本的晋升必须满足相应权限、用户/人工裁决和适用确定性门禁，并原子完成；模型自评不得单独替换。新结果较弱时保留当前有效版本；“较弱”只能由用户选择、人工验收或已冻结确定性质量合同判断。

实质修改才触发依赖它的未发布下游局部失效；措辞、排版、说明或结果未变不触发。依赖机制使用内容哈希、版本引用或其他最小可复算方式，禁止建设重型依赖图或全量事件溯源。

### 5.6 发布实例与反馈身份

发布实例必须对应：准确内容版本、发布账号、平台、实际或测试发生时间、业务身份和必要来源。发布后修改形成新内容版本；只有新版本实际发布时才形成新的发布实例。未再次发布的修订不能产生发布实例，也不能改写旧发布历史。

严格隔离以下身份：

- 真实发布实例；
- 测试发布记录；
- 模拟发布记录；
- 发布前人工评价；
- 发布后人工评价；
- 人工录入/导入经营结果；
- 真实平台效果；
- 模拟反馈；
- 运营观察；
- 因果提升结论。

结构相同不代表身份相同。测试/模拟记录不得混入真实发布历史，模拟反馈不得进入真实市场效果。人工导入必须保留来源、对象、录入时间、观察窗口和可信状态；不得匿名化成系统自动采集或真实平台原始数据。

发布后反馈只能绑定准确发布实例，并通过它关联准确内容版本；同时保留账号、平台、观察窗口、数据来源、分发条件和当时经营目标。无发布实例的版本、草稿、候选、Brief、PRE 或未发布 FINAL 不能绑定市场效果。

反馈记录分为“观测、解释假设、是否调整的决策”。M2 保存三者及来源关系，不把观测直接升级为策略改写或因果结论。

### 5.7 Cycle N 到 Cycle N+1 与打法记录

- M2 为周期 N 的准确任务、版本、发布实例、反馈、观察窗口、解释假设和外部变化提供可恢复投影。
- M3 可以据此提出周期 N+1 调整，也可以有依据地保持不变；M2 记录该决定、来源、适用范围和当前有效版本。
- M2 不为了展示“会学习”而自动制造变化，不把一次高表现变成长期规则，不自动训练模型或修改 Skill/Prompt。
- M2 能记录可跨多个内容任务重复验证的“打法”及其观察状态、适用范围、来源和版本；打法不是单个选题、单条内容、抽象目标或固定内容比例。
- 打法的专业定义、提出、修改和停用理由由 M3/用户提供；M2 只保存、投影、保留历史并确保权限和时效，不冻结物理枚举。

### 5.8 市场观察

市场观察至少保留：来源、平台、采集时间、适用赛道/对象、观察范围、内容机制摘要、权限、有效期或时效状态，以及它属于原始观察、分析结果还是高度同质判断的哪一层。

没有市场资料时仍可生产，M2 只投影“缺失/未完成外部比较”，不得伪造观察。外部资料不会自动转为租户品牌事实；是否证据充分、是否改版或不发由 M3/责任组件判断。

### 5.9 资料/素材授权、撤回和局部失效

资料或素材至少能表达来源、提供者/所有者、分析授权、生成/改编授权、发布授权、适用工作空间/账号/任务以及撤回/失效状态。

撤回后：

- 后续检索和任务投影不再返回该资料内容；
- Dify 历史记录不能成为继续使用的绕过渠道；
- 依赖它但未发布的任务、产物和可发布判断按真实依赖局部失效并进入重新检查；
- 已发布实例和必要历史关系不被静默删除或改写；可以保留不含原始内容的最小失效标记，防止绕过撤回；
- 物理删除、法定保留和完整合规流程不在本任务范围。

### 5.10 权限、幂等、并发和失败恢复

- Dify 只返回生成结果和建议变化，不能直接覆盖确认事实、修改权限、删除业务记录或晋升长期当前版本。
- 正式写回、版本晋升、权限变化、不可逆动作和外部副作用必须验证相应权限和裁决。
- 每个会创建或晋升周期、任务、内容版本、发布实例、反馈的业务请求必须有稳定幂等身份；同一请求重试返回同一业务结果或明确冲突，不重复创建。
- 并发写入采用最小事务/CAS/乐观并发机制，禁止 last-write-wins 静默覆盖；冲突返回可恢复、可重试的事实结果。
- 产物内容和状态/当前版本引用必须形成一致提交点，不能产生用户不可见的孤儿产物或状态声称存在而内容不存在。
- 恢复至少保留任务身份、当轮快照、成功组件/产物引用、失败位置、恢复入口和已发生副作用；输入未变的昂贵成功组件不重复运行。
- 恢复时不得要求用户重输任务或固定确认口令；不得向用户编造网络、数据库或落库失败原因。
- 所有数据库迁移、写回和远程推送副作用遵守执行协议的 `PLANNED/STARTED/CONFIRMED/FAILED_NO_EFFECT/UNKNOWN/COMPENSATED` 记录与重放规则。

### 5.11 运行接缝

M2 必须提供稳定、受权限约束的能力接缝，使其他模块不依赖数据库物理结构：

- 读取任务最小投影；
- 保存用户输入、快照、草稿、产物、原始观测和失败/恢复状态；
- 请求需要权限的当前版本晋升；
- 登记发布记录和反馈并验证业务身份；
- 读取周期、内容版本、市场观察和恢复状态；
- 撤回资料并取得受影响但未发布对象的局部失效结果。

具体 API、函数名、字段和传输协议由执行侧根据当前仓库自主决定。Skill 不直接读取数据库物理结构，Dify 不取得数据库管理权限。

### 5.12 Dify 候选交付与 Founder 实测入口

- 执行侧必须在 Founder 指定的本地或开发/测试 Dify 中形成一个最小、可回滚、可追溯的 M2 候选入口；优先使用明确划给本任务的候选对象，不得覆盖生产/共享应用。
- 候选只承载 M2 验收需要的薄接缝：首次任务、状态保存、重新进入、发布记录、反馈导入和下一周期读取。不得借机建设 M1 自然语言编译、M3 策略或 M4 生产链。
- 执行侧负责应用/工作流导入、更新、发布、真实运行、失败恢复、技术自验、Reviewer 审查和回滚证据；Founder 不负责节点、Schema、迁移、测试或 Git 审核。
- Founder 实测包至少包含：候选应用/工作流准确身份与入口、测试账号/工作空间说明、六步自然语言场景、预期可观察业务状态、禁止误判项、已知限制、反馈/接受方式和恢复入口。
- 技术验收完成后写入 `AWAITING_FOUNDER_DIFY_ACCEPTANCE` Checkpoint 并停止功能扩展；Founder 接受前不得声明 `DONE`，Founder 退回的范围内问题沿用同一 `task_id` 执行 `CONTINUE_TASK`。

---

## 6. 与 M1、M3、M4 的接口边界

| 接缝 | M2 负责 | M2 不负责 |
|---|---|---|
| M1 → M2 | 接收稳定用户/工作空间/任务身份、用户原始输入与来源、权限上下文、用户裁决和撤回/修改意图；按权限写回 | 解释自然语言、选择 Skill、判断当前应调用哪个能力 |
| M2 → M1 | 返回当前任务所需的最小投影、恢复位置、当前版本、权限缺口和局部失效结果 | 生成面向用户的对话策略、追问或路由 |
| M2 → M3 | 提供账号/周期/任务/版本/发布/反馈/市场观察/打法的准确投影和证据身份 | 决定账号阶段、内容比例、节奏、实验、反馈解释或周期 N+1 策略 |
| M3 → M2 | 保存 M3 提出的周期策略、打法变化、复盘判断或保持不变决定，并保留来源、版本和权限状态 | 把 M3 建议自动升级为用户确认长期规则 |
| M4 → M2 | 接收产物内容/引用、版本身份、真实依赖、确定性门禁结果、组件运行和副作用状态 | 执行 Skill、生产链、创意、拍摄、包装或局部重跑 |
| M2 → M4 | 提供当轮最小输入、当前有效产物/版本、素材权限、发布/反馈身份和幂等/恢复状态 | 决定组件调用计划、下游专业失效或成品质量 |

并行模块尚未完成时，可以使用冻结接口的契约测试替身验证 M2；必须明确“接口合同成立”不等于其他模块已经实现，更不等于 M5 集成通过。

M2 不等待 M3 外部头脑风暴或唯一 Skill 成稿才能施工。M2 只要能保存和投影“由 M3 提议、由用户/权限决定是否成为当前”的变化即可；不得替 M3 冻结专业运营语义。

---

## 7. 迁移与向后兼容

### 7.1 数据与迁移纪律

- 新增业务持久化采用可重复、可检查、版本化的迁移；新增信息原则上先可选，历史记录保持可读。
- 首次正式迁移前完成结构 dry-run、权限检查、备份/恢复或等价可逆证明；失败不得留下半迁移状态。
- 不在 Dify `public` 表上添加笛语业务字段、触发器或外键，不把 Dify 升级生命周期与业务 Schema 耦合。
- 不迁移、重标或清洗现有 Dify 测试运行来制造“已有真实业务数据”；旧数据如需导入，必须显式选择、保留原始来源和 `测试/模拟/历史 Demo` 身份。
- 内容大文件继续由对象存储或不可变引用承载；数据库保存元数据、归属、权限和稳定引用，不把完整数字资产管理系统塞入本任务。
- 任何不可逆删除或真实数据迁移不属于默认授权；若执行环境出现真实业务数据，先保护并按明确迁移授权处理。

### 7.2 旧任务快照与历史产物

- `V1_TASK_SNAPSHOT_SCHEMA_v0.1.json` 和 Dify 5 槽会话态作为兼容输入；不得照抄为业务 Schema。
- 旧 Matrix、Campaign、Content Brief 和生产产物可通过适配器进入统一业务语义，并保留原始引用、内容哈希、父产物、Skill/Run/夹具版本和证据身份。
- 旧会话只有当前槽位时，不得伪造不存在的版本历史；只能记录“导入时观察到的版本”和来源。
- 兼容读取不要求用户重新录入；无法无损确定的信息保持未知/未提供/不适用，不得猜测补齐。
- 旧 Dify 流程在 M2 施工期间不被改写；最终 M1/M4 接入和全链切换由各自任务/M5 决定。

### 7.3 前后向兼容

稳定业务核心保持行业和平台中立；行业/平台扩展信息允许以不污染核心的方式增加。未来多账号、更多平台、自动发布或外部采集可以接入，但本任务不提前实现，也不得因此设计通用平台。

---

## 8. 必跑代表性场景与局部回归

以下是冻结的代表性集合，不声称覆盖无限组合；执行侧可增加有限高信号探针，但不得用新增场景无限扩大 P0。

1. **跨会话恢复**：同一授权用户在新会话进入同一工作空间/账号，恢复当前周期、任务、当前版本和待处理事项；另一工作空间不可见。
2. **信息五维**：同一业务核心分别来自用户确认、系统假设、参考资料和历史产物时，投影核心语义等价但来源、权限、作用域、时效和确认状态不丢。
3. **无预存数据单次任务**：没有账号数据库也可完成单次任务；不会伪称持续运营闭环或强制建档。
4. **当前版与历史版**：创建候选、人工选择、原子晋升、回退、未采纳候选和历史可读；模型自评不能替换当前版。
5. **发布绑定**：同一内容两个版本、多个平台/账号发布时，反馈只进入准确发布实例；未发布修订无发布实例。
6. **证据身份隔离**：真实、测试、模拟、发布前人工评价、发布后人工录入和真实市场结果在同构数据下仍不可混淆；模拟数据不能得出真实运营结论。
7. **Cycle N→N+1**：周期 N 的准确反馈被投影给 M3，M3 返回调整或保持不变后形成周期 N+1 当前状态；M2 不自行改策略。
8. **Campaign 覆盖恢复**：覆盖点名部分、未覆盖部分继续；覆盖结束后恢复最新仍有效周期基线，覆盖期发布历史保留。
9. **产能三分**：基线产能、当期实际产能、用户期望发布量不同且来源/作用域各异，保存和投影不互相覆盖。
10. **市场观察时效**：有来源/时间/范围的观察在有效期内投影，过期后标为过期且不冒充当前比较；没有观察时返回明确缺口。
11. **打法记录**：同一打法跨多个任务积累观察；M3 提出变化后形成新版本，旧版保留；M2 不定义打法枚举或好坏规则。
12. **资料撤回**：撤回后未来投影不含资料内容，依赖它的未发布对象局部失效；无依赖对象不受影响，已发布历史不被改写。
13. **幂等重试**：相同请求在超时、客户端重试或服务恢复后不重复创建周期、任务、版本、发布实例或反馈。
14. **并发冲突**：两个并发更新基于同一旧版本时，不发生静默 last-write-wins；一个成功，另一个得到可恢复冲突并可在新基线上重算。
15. **原子提交/故障注入**：在产物保存、状态晋升、发布登记、反馈写入和迁移中点故障，恢复后无孤儿、无重复、无伪成功。
16. **权限负向**：未授权用户、跨工作空间、撤回素材、缺发布权限、模型直接写当前版均被精确拒绝；不扩大成无关任务硬停。
17. **旧 Demo 兼容**：旧 3 槽/5 槽快照和旧产物可显式导入或适配读取；测试身份不被升级为真实业务数据，原 Dify 状态零改写。
18. **最小投影**：M1/M3/M4 各自只获得任务所需字段/引用；不泄漏其他工作空间、无关历史、撤回资料或数据库物理信息。
19. **Founder Dify 连续实测**：在同一测试工作空间完成“首次任务→保存状态→再次进入→登记准确发布实例→导入明确身份的反馈→下一周期读取”，画布可观察结果与业务库事实一致，不把测试数据冒充真实经营结果。
20. **Founder 退回续作**：Founder 对产品意图或业务价值提出范围内调整时，保留同一 task_id、Checkpoint、历史 Attempt 和副作用，定向修改并只复验直接/传递影响；不重发根 Prompt、不重建任务、不重复迁移。

局部回归只覆盖 M2 Delta 的真实影响面：既有 Dify 主链读写不被数据库迁移破坏；旧会话态和内容身份仍可读取；受影响的任务状态、产物引用、哈希回验、对话恢复接缝不退化。没有证据证明受影响的 Skill/生产链不做开放式全量复跑；M5 的专业价值和完整生产链验收不在 M2 单模块内冒充完成。

---

## 9. 验收标准、证据与 Oracle

| criterion_id | 必须证明的结果 | 主要证据/Oracle |
|---|---|---|
| `M2-AC-00` | 入口门、任务身份、当前基线、独立 worktree/分支、Manifest、数据库隔离和副作用状态可核验 | Git/远端、账本、PostgreSQL/Dify 只读快照、Manifest 哈希 |
| `M2-AC-01` | 用户、工作空间、主体、账号、周期和访问关系可跨会话恢复，个人/企业工作空间不越权混用 | 正向恢复、跨工作空间负向、权限查询与原始响应 |
| `M2-AC-02` | 信息五维和任务快照业务语义可持久化；最小投影保留来源/权限/时效差异且无跨租户泄漏 | 成对夹具、投影断言、权限/撤回负向、原始载荷 |
| `M2-AC-03` | 当前有效版本、候选和历史版本分离；晋升原子、旧版可读/回退、模型自评不能替换 | 版本并发/故障测试、人工裁决、数据库约束和历史读取 |
| `M2-AC-04` | 内容任务、产物、内容版本、发布实例和效果观察身份准确；五类里程碑不被压成互斥状态 | 关系断言、多个版本/平台/账号发布场景、历史查询 |
| `M2-AC-05` | 真实/测试/模拟/人工评价/人工录入/市场结果严格隔离，结构同构也不会互相升级 | 证据身份负向探针、约束、查询与结论边界检查 |
| `M2-AC-06` | 反馈只能绑定准确发布实例及准确版本、账号、平台、时间窗、来源和当时目标；无发布实例不能绑效果 | 发布绑定正负向测试、约束失败原始证据 |
| `M2-AC-07` | Cycle N 的准确证据可进入 Cycle N+1 投影；M3 调整或保持不变均可记录，M2 不自动改策略 | 两周期契约运行、状态 diff、M3 测试替身与证据身份 |
| `M2-AC-08` | Campaign 覆盖范围和退出恢复正确；未覆盖任务、最新有效基线和历史发布不被误改 | 覆盖/更新/到期/取消组合场景和版本历史 |
| `M2-AC-09` | 基线产能、当期实际产能、用户期望发布量三分；市场观察来源/时间/范围/时效完整 | 三产能断言、市场观察过期/缺失探针、投影结果 |
| `M2-AC-10` | 打法可跨任务版本化记录并保留观察状态；M3 提议变化、M2 记录，未冻结物理枚举或专业规则 | M3 契约替身、历史版本、Schema/代码审查 |
| `M2-AC-11` | 资料撤回后未来投影退出，真实依赖的未发布对象局部失效，无依赖对象和历史发布保持 | 撤回正负向、依赖影响、投影/历史查询 |
| `M2-AC-12` | 幂等、并发、原子提交和恢复成立；重试无重复记录，冲突不静默覆盖，失败无孤儿/伪成功 | 并发测试、故障注入、幂等键、事务结果和恢复日志 |
| `M2-AC-13` | 数据库迁移可重复、失败可恢复/回滚、旧记录可读，Dify 内部表和数据未被改写 | dry-run、迁移/回滚、前后结构/计数/哈希、权限证明 |
| `M2-AC-14` | 旧 Demo 快照和历史产物可兼容读取/显式导入；缺失历史不被伪造，测试身份不污染真实业务 | 3 槽/5 槽夹具、旧产物导入、来源身份与 Dify 零改写 |
| `M2-AC-15` | M1/M3/M4 接口合同成立且责任未越界；无 M1 路由、M3 策略、M4 生产链或新 Skill 实现 | 契约测试、代码/变更范围审查、独立 Reviewer |
| `M2-AC-16` | 最终候选在真实 PostgreSQL/应用和 Founder 指定开发/测试 Dify 目标环境运行，正向/负向/回归、审查、账本、Git、远程任务分支、Dify 候选与回滚证据收口完整，无受保护基线退化 | 最终 commit/远端 ref、运行/迁移/Dify 发布 ID、画布与回滚证据、Reviewer 结果 |
| `M2-AC-17` | Founder 已通过 Dify 画布完成 M2 产品与业务实测并明确接受；若尚未接受，任务保持同 task_id 的可恢复等待/退回状态，不冒充 DONE | Founder 回执、候选入口、六步运行 ID/画布观察、Checkpoint/CONTINUE_TASK 证据 |

每项验收记录：`criterion_id`、`required_change`、`verification_method`、`acceptance_oracle`、`evidence_ref`、`evidence_binding`、`evidence_currency`、`verification_authority`、`result`。

没有完整绑定证据只能为 `NOT_VERIFIED`。文件存在、迁移脚本写完、测试数量、模型自评、HTTP 200 或单次成功不等于 P0 通过。模拟/测试数据可以证明工程纵向切片机制，但不能证明真实运营闭环、经营结果提升或专业价值增益。

---

## 10. 执行自主权

执行总负责人可以在稳定合同内自主：

- 选择应用后端语言/框架、ORM/查询层、迁移框架、数据库或 Schema 隔离方式、物理表/字段/API 和代码组织；
- 根据当前仓库和 PostgreSQL 证据选择更小、更可靠的实现，并进行必要局部重构；
- 设计最小约束、索引、事务、幂等、乐观并发、快照投影和恢复机制；
- 选择可复算测试、有限夹具、故障注入和证据组织；
- 首条路线失败后分析根因并换路；
- 复用仍为 CURRENT 的证据，只重验 M2 Delta 直接和传递影响项；
- 在 Founder 指定开发/测试 Dify 中创建或更新本 task_id 的候选应用/工作流、导入/发布候选版本、运行和回滚；
- 内部拆解工作、调用隔离 Reviewer、保存 Checkpoint，并在外部中断或 Founder 范围内退回后以同一 task_id 继续。

执行侧不得：

- 因 Prompt 未给表名/字段/API 而要求 Founder 选择普通技术方案；
- 把实现便利升级为新的产品语义、M3 专业规则或长期物理架构；
- 把数据库/Schema 二选一、ORM、索引和函数名写进稳定 Task Contract；
- 因首条路线失败、上下文长度、施工复杂或 M3 研究未完成而停止；
- 用桩证明真实 PostgreSQL/应用运行，或用单次真实运行替代确定性和负向测试；
- 删除失败 Attempt、随机重抽成功、放宽 Oracle、创造 P1 或使用 `PARTIAL`。

如果本 Prompt 的建议路径与执行时真实仓库、运行结果或更高权威真源冲突，以真实事实和高权威真源为准；执行侧在不改变 P0、边界和验收的前提下自行选择正确 HOW，并记录偏离依据。

---

## 11. 审查预算、停止和阻塞

### 11.1 技术自验与独立审查

审查模型冻结为：

```yaml
review_model:
  executor_self_verification: required
  independent_reviewer: one_context_isolated_read_only_agent
  reviewer_write_permission: false
  formal_review_budget: 1
  repair_budget: 1
  closing_verification: affected_scope_only
```

1. 执行总负责人完成实现、迁移、目标环境运行和自验，冻结候选 commit、迁移版本、Dify 候选版本、配置及证据哈希；
2. 调用一个未参与实现、上下文隔离、只读的 Reviewer 做一次正式审查；Reviewer 不得写代码、改数据库、改 Dify、修改证据或指定实现方案；
3. Reviewer 只能提出两类阻断：
   - 明确违反某条 `M2-AC-00` 至 `M2-AC-17`；
   - 明确违反安全、权限、受保护资产或数据完整性边界；
4. 每个阻断必须同时给出 `criterion_id + evidence + affected_scope`；缺任一项均不是有效阻断；
5. 命名偏好、文档排版、“可以更优雅”、无验收映射的重构建议、没有基线证据的“能力下降”以及要求采用 Reviewer 偏好的 HOW 不得阻断；
6. 执行总负责人判断阻断、在一个修复预算内只修验收阻断项，完成自验；收口验证只覆盖原阻断及其直接/传递影响，不开启第二轮开放式找茬；
7. 候选 commit、迁移、Dify 配置或关键业务行为变化时，受影响证据必须重新绑定；不得因预算耗尽把真实阻断改判通过。

### 11.2 技术交付门与 Founder Dify 验收

当 `M2-AC-00` 至 `M2-AC-16` 已通过、技术证据 CURRENT、远程任务分支和 Dify 候选已收口，但 Founder 尚未完成产品验收时，必须持久化：

```text
execution_disposition = CONTINUE
task_final_status = null
module_delivery_state = AWAITING_FOUNDER_DIFY_ACCEPTANCE
next_stage_allowed = false
```

然后停止功能扩展，提交 Founder 实测包，等待 Founder 只在 Dify 画布验证：

- 首次自然任务能否形成并保存正确业务状态；
- 再次进入能否恢复准确上下文；
- 发布记录和反馈是否绑定准确实例/版本；
- 下一周期读取是否符合产品意图和真实用户习惯；
- 输出是否有实际业务价值，是否接受或退回模块交付。

Founder 不审核文件组织、Schema、节点连线、迁移实现、单元测试、Git 规范或普通技术缺陷；这些必须在提交实测包前由执行侧与 Reviewer 收口。

Founder 明确接受且 `M2-AC-17` 通过后，才允许使用 `DONE`。Founder 范围内退回时，使用同一 `task_id`、现有 Checkpoint、Manifest、Attempt 和副作用账本执行 `CONTINUE_TASK`，定向修改、受影响复验、重新部署同一候选并回到 Founder 实测门；不得重发根 Prompt 或重建任务。若退回内容改变产品语义、扩大权限、触碰生产环境/受保护资产或要求 M2 决定 M3 专业语义，必须精确请求 Founder 裁决，不得静默扩展。

### 11.3 强制停止条件

以下全部成立后必须立即停止并提交最终回执：

- M2 P0 全部落盘；
- `M2-AC-00` 至 `M2-AC-17` 全部 `PASS` 且证据对最终候选 `CURRENT`；
- PostgreSQL、应用后端和 Founder 指定开发/测试 Dify 的迁移、运行、正向、负向、并发、恢复、回归、回滚与审查完成；
- Founder 已通过 Dify 画布明确接受产品与业务交付；
- 没有已证明的权限、隔离、数据身份、受保护资产或既有能力退化；
- 失败 Attempt、限制、迁移、Dify 和 Git 副作用完整保留；
- 最终 commit 已推送远程任务分支，本地与远端 hash 一致且可访问。

停止后不得继续润色、改名、顺手重构、附加研究、扩建未来平台、启动新一轮开放审查或合并 main。

### 11.4 治理阻塞与终态

- 只有改变产品语义或验收、必要权限缺失、隔离边界无法安全建立、必须触碰生产环境/受保护资产、M3 专业语义冲突或需要未经授权不可逆/外部动作时，才提交精确治理阻塞；只暂停受影响分支，其他安全工作继续。
- PostgreSQL 表名、数据库/Schema 选择、ORM、应用框架、Dify 候选节点、普通技术失败、测试失败和迁移脚本缺陷属于执行问题，不是 Founder 阻塞。
- `BLOCKED` 必须满足执行协议 v1.3 全部条件并给出解除主体、条件和原始证据。
- `PARTIAL` 禁止：本任务没有 P1。
- `FAILED`：证据有效但 P0 未成立、授权内合理路径穷尽且没有治理阻塞，或结果低于受保护基线。
- `INVALID`：决定最终状态的运行、数据或证据整体不可修复地失真。
- `DONE`：仅在全部 P0、完成检查、技术审查、Founder Dify 验收和远程任务分支收口成立时使用。

`next_stage_allowed` 默认 `false`。M2 `DONE` 只表示 M2 是进入后续集成的必要条件；不自动授权合并 `main`、M1/M3/M4、M5、真实发布或真实运营结论。

若外部执行单元真实中断且仍有明确可执行 P0 路径，持久化协议定义的 Checkpoint：

```text
execution_disposition = CONTINUE
task_final_status = null
module_delivery_state = IN_PROGRESS
next_stage_allowed = false
```

任务复杂、普通技术路线未定、需要继续调试、上下文变长或一次执行会话结束不构成主动停止理由；后续必须以 `CONTINUE_TASK` 恢复同一任务。
---

## 12. Git、远程收口与最终回执

### 12.1 Git 规则

- 任务分支：`task/m2-business-persistence-version-feedback-v1`；独立 worktree。
- 施工基线是执行时刷新后的远程默认 `main`，不是规划快照 `c085eb...`，也不是历史 EP-00 基线。
- 若同名远程分支或同 `task_id` 已存在，先恢复状态和副作用，不得覆盖或重建。
- 只提交 M2 授权范围内的代码、迁移、测试、文档、证据和本 task_id 账本；不吸收其他工作树改动。
- 禁止 force、amend、reset、squash、改写历史、删除其他分支/worktree、合并或推送 `main`。
- 最终远程收口只到远程任务分支；后续采用进 `main` 需要独立授权。

### 12.2 最终回执

执行侧最终回执必须包含：

1. 正式最终状态；
2. `task_id`、`task_entry_mode`、Task Contract 哈希、Manifest ID/版本/哈希；
3. 实际执行基线、分支、worktree、最终本地 commit、远程任务分支和远端 hash；
4. PostgreSQL 实际版本、选择的数据库/Schema 隔离方式、应用身份权限和“不修改 Dify 内部表”的证明；
5. 应用后端、迁移版本、配置、PostgreSQL/应用/Dify 目标环境运行与回滚/恢复结果；
6. Dify 候选应用/工作流的准确 ID、导入/发布版本、画布配置、运行 ID、入口、备份/导出和回滚证明；
7. 变更文件、迁移对象、兼容适配和明确未改资产清单；
8. `M2-AC-00` 至 `M2-AC-17` 逐项结果、证据引用和时效；
9. 代表性场景、正向/负向/并发/故障注入/回归结果和原始证据；
10. 全部 Formal Attempt、失败路径、迁移/数据库/Dify/Git 外部副作用账本；
11. 独立审查的候选哈希、冻结阻塞集合、`criterion_id + evidence + affected_scope`、修复和受影响收口结论；
12. 真实/测试/模拟/人工证据隔离、发布/反馈绑定、资料撤回和跨周期投影结论；
13. 已知限制、真正未解决问题和未授权事项；
14. `ENGINEERING_VERTICAL_SLICE_VERIFIED` 是否成立；没有真实发布证据时必须明确 `REAL_OPERATION_LOOP_VERIFIED = false/not_verified`，不得声明经营提升；
15. Founder Dify 实测包、产品/业务接受或退回回执，以及 Founder 未被要求审核技术实现的说明；
16. `next_stage_allowed` 的明确值和适用范围。

不得用“代码已写”“迁移已创建”“测试大多通过”“基本完成”“总体可用”代替正式状态和证据。

### Prompt 冻结信息

```yaml
prompt_file: M2_业务持久化版本发布反馈投影_Execution_Prompt_v1.1.md
supersedes_for_future_authorization: M2_业务持久化版本发布反馈投影_Execution_Prompt_v1.0.md
planning_compiled_at: 2026-08-25T07:06:46-07:00
current_main_verified_at_compile: 2a0822692802ac084d92e032f098da33079f063d
task_contract_hash: e17b354b97d53bfa52eeb30ffca50970e5469acabee98b3cfc32a1031b1b90ca
prompt_sha256: 由 W2 最终冻结回执计算；本文件不内嵌自身哈希，避免自引用
engineering_execution_performed: false
```
