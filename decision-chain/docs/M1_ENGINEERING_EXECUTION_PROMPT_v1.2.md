# Execution Prompt — M1 自然语言交互与任务上下文编译 v1.2

## 0. 使用方式、任务身份与授权门

你是笛语 V1 单账号持续内容运营纵向切片 M1 的**受边界约束执行总负责人**。本文件是一份覆盖 M1 完整 P0 的 Root Execution Prompt：你必须在同一 `task_id` 下自主完成侦察、拆解、工程实现、自验、一次上下文隔离只读审查、阻断修复、受影响范围复验、真实 Dify 候选环境部署与运行、远程任务分支收口，以及 Founder Dify 实测包提交。

本文件不是要求你在一次聊天回复中完成全部工作，也不是按阶段重新索取新 Prompt。执行被正常中断时，必须持久化 Checkpoint，并以同一 `task_id` 通过 `CONTINUE_TASK` 恢复。只有产品合同、授权范围或受保护资产发生实质变化时，才进入 `REBASE_TASK` 或请求 Founder 裁决。

本文件是 `M1_ENGINEERING_EXECUTION_PROMPT_v1.1.md` 的后继版；v1.1 与更早版本只作历史，不得再用于新开工，也不得被覆盖或伪装成当前版本。

本文件的规划编译不构成施工授权。只有 Founder 把**本准确 v1.2 文件**交给工程执行终端并明确授权执行，才允许产生任何工程、Git、Dify 或账本写入。只读核验不构成开工。

```yaml
prompt_id: M1_ENGINEERING_EXECUTION_PROMPT
prompt_version: "v1.2"
planning_status: READY_FOR_FOUNDER_USE
engineering_execution_performed_by_planning_window: false
engineering_execution_authorized_by_prompt_compilation: false
task_id: DIYU-V1-M1-NATURAL-CONTEXT-001
initial_task_entry_mode: NEW_TASK
execution_protocol_ref: DIYU-BOUNDED-EXECUTION-OWNER-PROTOCOL v1.3
root_prompt_model: ONE_ROOT_PROMPT_FOR_COMPLETE_M1_P0
```

首次获授权时，如果远端分支、worktree、账本、Dify 候选对象或 Manifest 显示同一 `task_id` 已经开工，不得新建重复任务；必须读取真实状态后改判为 `CONTINUE_TASK`、`RECOVERY_TASK` 或 `REBASE_TASK`，保留全部 Attempt、失败路径、Checkpoint 和外部副作用。

---

## 1. 治理真源与当前基线

### 1.1 真源优先级

发生冲突时按下列顺序裁定：

1. Founder 当前明确裁决；
2. 下列现行规划协议 v1.2 与执行协议 v1.3；
3. 已接受上位产品合同、单账号切片合同、四份 M0.3 共享合同和 Phase 0 共享编译前言；
4. 统一构建规划 v0.3 的当前产品语义；
5. 执行时实时仓库、账本、Dify 草稿/发布对象和原始运行证据；
6. EP-00、旧 Schema、旧集成合同和历史 Prompt。

仓库事实描述“当前实现是什么”，不能改写已接受产品目标；历史计划中的 SHA、状态和授权不能覆盖实时事实。

### 1.2 现行规划与执行协议

```yaml
planning_protocol:
  path: /mnt/c/Users/Administrator/Documents/Codex/Diyu-V1-Planning/执行Prompt生成总则_规划侧约束框架_v1.2.md
  sha256: 8023bf3e21ff8fb9ba9a2e81b95d1afb178ebf1c04545d0deaac709f603b05b8
execution_protocol:
  path: /mnt/c/Users/Administrator/Documents/Codex/Diyu-V1-Planning/受边界约束的执行总负责人协议_v1.3.md
  sha256: 3ba07a67784056f36211ac634e25a948ce8482f1831aa3dbdc6ab5945ccffcfc
program_plan:
  path: /mnt/c/Users/Administrator/Documents/Codex/Diyu-V1-Planning/笛语_V1_单账号持续内容运营纵向切片统一构建规划_v0.3.md
  sha256: b25d17865553dd906e262694f71f0cb030262be93030d43a19f735ea3d0b9e27
```

不得自行把上述协议文件自身的候选治理状态升级为 Founder 已接受；但执行本任务时必须使用这里冻结的版本和内容指纹。

### 1.3 产品合同、预检和共享合同

以下路径相对真实仓库根 `/home/faye/diyu-demo`：

```yaml
upper_product_contract:
  path: decision-chain/docs/V1_DECISION_CHAIN_REBASE_PRODUCT_CONTRACT_v0.1.md
  sha256: 9a57d255dec44477ceb38f6f61faaa5f43d36343f89803364eac5df6d5fc5ca0
single_account_slice_contract:
  path: decision-chain/docs/V1_SINGLE_ACCOUNT_SLICE_CONTRACT_v0.2.md
  sha256: 677c7f350410b934b5e25caa3cf98f4665a48936588adc66798d093b042ece9d
general_ep00:
  path: decision-chain/docs/V1_REBASE_EP00_CURRENT_PREFLIGHT_v0.1.md
  sha256: afea2d975b1e214ee57aaaab3bfaee63bb6d0319403bfe6d8e66285c2b1bce11
single_account_ep00:
  path: decision-chain/docs/V1_SINGLE_ACCOUNT_SLICE_EP00_PREFLIGHT_v0.1.md
  sha256: 921091b5a43fb72371c5c95e6bb07e6ccd87db6baa29fb9cff2716e5dd2fbc4d
shared_contract_task_context:
  path: decision-chain/docs/V1_M0_SHARED_CONTRACT_TASK_CONTEXT_SNAPSHOT_v0.1.md
  sha256: 76b730d47566eccc188e2dbb0c4da2e8aa594936cc813987cc8d0fd7901bd63b
shared_contract_eight_capabilities:
  path: decision-chain/docs/V1_M0_SHARED_CONTRACT_EIGHT_CAPABILITIES_v0.1.md
  sha256: 6d3fb85ebce417c4d34103775f833656dab7d62e390b0c9ba482ccc9108e8a30
shared_contract_version_publish_feedback:
  path: decision-chain/docs/V1_M0_SHARED_CONTRACT_VERSION_PUBLISH_FEEDBACK_v0.1.md
  sha256: 67af3e991394fb27964470bcdbf5a46678a494e4045db60eb573b31ea924ee2b
shared_contract_write_permission_recovery:
  path: decision-chain/docs/V1_M0_SHARED_CONTRACT_WRITE_PERMISSION_RECOVERY_v0.1.md
  sha256: 108209b52df232e91e06b5726b2c19eb6094f06eb7025971a958750143a172f0
shared_construction_preamble:
  path: decision-chain/docs/V1_M1_M4_CONSTRUCTION_PROMPT_SHARED_PREAMBLE_v0.1.md
  sha256: 210ccf7407498a9566ff99aa1486a0815abb53879705aff83448252a2a58a388
```

两份 EP-00 只是其绑定基线的实现证据，不是目标合同。`V1_TASK_SNAPSHOT_SCHEMA_v0.1.json`、`V1_DEMO_INTEGRATION_CONTRACT_v0.1.md`、旧 DSL 和历史测试同样只是当前兼容/回归证据，不得用来恢复固定流水线或拒绝新合同要求。

### 1.4 规划编译时现场事实

```yaml
observed_at: 2026-08-25
repository: /home/faye/diyu-demo
remote_url: https://github.com/andyan77/diyu-demo.git
remote_default_branch: main
observed_local_branch: main
observed_local_head: 2a0822692802ac084d92e032f098da33079f063d
observed_local_origin_main: 2a0822692802ac084d92e032f098da33079f063d
observed_github_main: 2a0822692802ac084d92e032f098da33079f063d
working_tree: clean
latest_commit_time: 2026-08-25T04:52:52-07:00
latest_commit_subject: 采用 V1-M1-M4-PHASE0-DECISION-STATE-CLOSEOUT-001 交付进 main：八项能力四类合同值与 Matrix 处置状态确认
m0_status: DONE
phase0_preamble_status: ACTIVE_ON_DEFAULT_BASELINE
phase0_product_semantics_confirmation: FOUNDER_CONFIRMED
m1_prompt_compilation: AUTHORIZED
m1_engineering_execution: NOT_STARTED_AND_NOT_AUTHORIZED_BY_COMPILATION
```

从专项 EP-00 基线到当前 HEAD，`decision-chain/skills/`、`decision-chain/workflows/`、`content-production/skills/`、`content-production/workflows/` 和 `tools/` 未发现路径级工程变化。因此 EP-00 中与 M1 相关的起点仍可用于侦察，但执行侧必须现场刷新：当前仍偏模块名/关键词路由；目标层级承载不足；固定 `UPSTREAM_OF` 线性锁仍是风险；Matrix 资料不足仍可能硬停整任务；三槽旧 Schema 与五槽部署事实不一致；A-0～A-4 的运行证据需要绑定最终候选重验。

### 1.5 执行时必须刷新、不得预设的事实

首次写入前必须现场核验：

- GitHub 远程默认分支、远端 HEAD、本地工作区、worktree、同名任务分支和同一 `task_id` 账本；
- 当前 Dify 工作空间、应用、草稿图、已发布图、节点、Tool、模型参数、环境和运行历史；
- 是否已有本任务专用候选 App；若没有，是否可在授权工作空间创建；
- A-0～A-4 与历史回归证据对当前对象是否仍为 `CURRENT`；
- M1 实际代码、DSL、节点、接口、字段、测试和证据位置；
- M2/M3/M4 是否已有可读稳定接口或只能使用冻结夹具；
- 当前凭证是否足以创建/更新/发布专用候选 App、运行测试和推送远程任务分支。

若默认分支前移但产品合同、共享语义、受保护资产和 P0 未实质变化，从新的真实默认分支开工并记录 Delta；不得从本节历史 SHA 强行开工。若有权合同、权限或验收 Oracle 实质变化，先停止写入并进入 `REBASE_TASK`。

---

## 2. 稳定 Task Contract

`TASK_CONTRACT_BEGIN` 与 `TASK_CONTRACT_END` 之间 YAML 代码块的块内 UTF-8 字节构成稳定合同哈希对象；围栏和标记不计入。

<!-- TASK_CONTRACT_BEGIN -->
```yaml
contract_version: "1.2"
task_id: DIYU-V1-M1-NATURAL-CONTEXT-001
task_entry_mode: NEW_TASK
task_type: MIXED
risk_level: HIGH

final_deliverable: >-
  在独立 M1 任务分支、worktree 和专用 Dify 候选/测试 App 中完成 M1 全部 P0：
  ChatGPT 式自然交互、任务上下文编译、唯一调用意图/计划、真实运行、技术验收、
  有界独立审查、回滚准备和远程任务分支收口；随后提交 Founder Dify 画布实测包。
  技术候选完成与 Founder 产品接受必须分开，不得互相冒充。

product_goal:
  - 用户以自然语言、合法资料和有效历史产物直接协作，不填写内部表单或固定口令
  - 正确区分当前任务、本条、本周期、当前账号与长期要求
  - 保留主目标、有限次目标、优先级、不可牺牲条件和冲突取舍
  - 只追问真正阻塞当前分支的最关键问题
  - 按当前任务选择能力，不建立 Matrix→Campaign→Brief 固定流水线
  - 用户要求调整时形成实际调整结果，或如实说明可核验硬边界
  - 普通可逆内部动作不包装成 Founder 逐步审核

authorized_scope:
  repository_write:
    - 独立 M1 worktree/任务分支内为 P0 必需的代码、配置、DSL、适配器、测试、有限夹具、文档和证据
    - collab-ledger 中本 task_id 的 Manifest、Attempt、Checkpoint、失败路径、验收和外部副作用记录
  dify_write:
    - 在当前已授权 Dify 工作空间内创建或恢复唯一一个带 task_id 标识的 M1 专用候选/测试 App
    - 在该专用 App 内导入、更新、配置、发布候选工作流版本并完成真实运行
    - 保留发布前导出、对象/版本标识、图、模型参数和与 Git commit 的绑定
  execution:
    - 只读侦察、依赖安装、实现、测试、故障注入、受影响回归、真实 Dify 运行和证据归档
    - 创建或恢复独立分支/worktree，commit，推送远程任务分支并核验远端完整 hash
    - 调用一个未参与实现、上下文隔离、只读且无写权限的独立 Reviewer
  network:
    - 读取 GitHub 远端、获取默认分支状态、推送本任务分支
    - 在现有合法凭证内操作上述唯一 M1 专用 Dify 候选/测试 App

explicitly_not_authorized:
  - 修改、覆盖、重发、下线或切流任何当前生产 Dify App/已发布生产对象
  - 修改非本 task_id 的 Dify App、工作流、凭证、知识库或运行记录
  - 合并或直推 main、创建或合并 PR、force、amend、reset、squash 或改写历史
  - 建设或迁移 M2 数据库、业务 Schema、业务持久化、版本/发布/反馈或跨周期记忆
  - 执行真实社交平台发布、投流、交易、OAuth、权限扩大或其他不可逆外部动作

non_goals:
  - M2 的持久化、版本晋升、发布实例、反馈归属、事务、幂等、权限存储和恢复
  - M3 的账号状态诊断、周期策略、内容组合、节奏、产能、实验和复盘判断
  - M4 的专业组件执行、生产链、Runtime 集成、局部重跑和依赖失效传播
  - 重写或中性化 Matrix、Campaign、Content Brief、Creative Script、Production Director、Publishing & Packaging 的专业判断
  - 第二套目标路由、账号状态库、审批系统、工作流引擎、知识库或通用数据平台
  - 全量重写六份 Skill、提前实现 M5、宣称完整单账号持续运营闭环或经营结果提升

protected_assets:
  - 已接受父子产品合同、四份共享合同、Phase 0 前言和冻结验收语义
  - Matrix 对长期定位/人设/账号职责的专业决定权
  - M2 持久化决定权、M3 运营判断决定权、M4 组件执行决定权
  - Matrix、Campaign、Content Brief、Creative Script、Production Director、Publishing & Packaging 六项专业 Skill 的源文件、专业 Prompt、判断规则和已证明能力；M1 通过路由/适配器接入，不修改其专业内部
  - 现有六项专业能力、CS-1、PRE/MIXED/FINAL、事实核验、Returns 和用户交付投影
  - A-0至A-4 原始证据、历史 Oracle、失败 Attempt 和运行记录
  - 用户/工作空间/账号/素材/隐私/凭证/已发布内容及其他任务资产

accepted_baseline:
  - 执行时核验的远程默认分支及其有权后继合同
  - 编译观察锚点 main@2a0822692802ac084d92e032f098da33079f063d 只作 Delta 比较
  - A-0至A-4、现有六能力、CS-1、PRE/MIXED/FINAL、事实核验、Returns 和用户交付投影

allowed_delta:
  - 仅补足 M1 自然交互、任务上下文编译、唯一调用意图/计划和用户交互/恢复接缝
  - 复用并增强当前骨架；如证据证明位置不适合，可自主换技术路径，但只保留一套调用语义真源
  - 为 M2/M3/M4 冻结接口建立最小适配、契约测试或夹具，不实现对方内部
  - 修复 M1 Delta 直接或传递影响的代码、DSL、配置和测试

target_environment:
  repository: /home/faye/diyu-demo
  branch: task/m1-natural-interaction-context-v1
  worktree: independent
  dify_workspace: 执行时现场确认的当前授权开发/测试工作空间
  dify_app: 唯一 task_id 专用 M1 候选/测试 App；允许创建或恢复
  dify_publish_authority: 仅允许发布到该专用候选/测试 App，不代表生产采用
  database_migration_authority: NONE_FOR_M1

review_model:
  executor_self_verification: required
  independent_reviewer: one_context_isolated_read_only_agent
  reviewer_write_permission: false
  formal_review_budget: 1
  repair_budget: 1
  closing_verification: affected_scope_only

p0:
  deliverables:
    - M1 可运行实现与 M2/M3/M4 稳定业务语义接缝
    - 任务层级、目标层级、来源状态、等价输入、最小追问和局部降级
    - 非线性调用计划、直接入口、Matrix 局部阻断和多诉求继续
    - 用户调整、风险确认、诚实失败恢复和自然语言回执
    - 确定性测试、真实 Dify 运行、受影响回归、技术审查和回滚包
    - 远程任务分支、技术回执和 Founder Dify 画布实测包
  technical_acceptance:
    - M1-AC-00 至 M1-AC-15 全部 PASS，证据绑定最终候选且为 CURRENT
  founder_product_acceptance:
    - Founder 在 Dify 画布完成代表性自然语言产品实测后明确 ACCEPT 或 RETURN

completion_state_machine:
  - IMPLEMENTING
  - TECHNICAL_REVIEW
  - TECHNICALLY_READY_FOR_FOUNDER_DIFY_ACCEPTANCE
  - AWAITING_FOUNDER_DIFY_ACCEPTANCE
  - FOUNDER_RETURNED
  - DONE
  - BLOCKED
  - FAILED
  - INVALID

evidence_requirements:
  - 每个 Formal Attempt 保留输入、输出、模型参数、代码/DSL/Dify对象、Oracle、环境、日志、结果和实质差异
  - 失败 Attempt、已证伪路径和真实异常全部保留，不删除失败或随机重抽成功
  - 证据绑定最终 commit、输入/哈希、Oracle、Dify App/图/版本、模型参数、环境和观察时间
  - 敏感资料和凭证不明文入库，只使用脱敏引用、必要摘要和稳定哈希
  - Git、Dify 和外部副作用按 task_id 记录；STARTED/UNKNOWN 先查目标系统，不盲目重放

remote_target:
  repository: https://github.com/andyan77/diyu-demo.git
  branch: task/m1-natural-interaction-context-v1
  merge_main: NOT_AUTHORIZED

next_stage_default: false
```
<!-- TASK_CONTRACT_END -->

执行侧必须在首次写入前独立重算 Task Contract Hash 并写入 Run Manifest。执行计划、会话摘要和进度不得混入该稳定哈希对象。

---

## 3. 入场、续作与执行侧自主权

### 3.1 入场门

首次工程写入或创建 Dify 对象前必须确认：

- Founder 已明确授权执行本准确 v1.2；
- 实时默认分支、工作区、账本、同名分支/worktree 和 Dify 状态已刷新；
- 当前基线包含已接受合同及激活的 Phase 0 前言；
- M1 授权范围、受保护资产、验收 Oracle 和远程目标不存在真实冲突；
- 既有同 `task_id` 状态已识别并继承。

Founder 未授权时只允许安全只读核验，然后停止；不得创建分支、worktree、账本任务或 Dify 对象。

### 3.2 一条根 Prompt 与同任务续作

- 默认执行顺序是：只读侦察与拆解 → 工程实现 → 执行侧自验 → 上下文隔离只读 Reviewer → 只修验收阻断 → 受影响范围复验 → 冻结候选部署到专用 Dify App 并真实运行 → 技术回执与 Founder 实测包；执行侧可在不改变门禁含义时调整内部并行顺序；
- 执行总负责人自主拆成工作包、测试单元和隔离审查，不向 Founder 逐阶段索取新 Prompt；
- 正常中断、上下文切换或异步等待时写 Checkpoint，不得用聊天摘要冒充持久化状态；
- 恢复使用同一 `task_id` 与 `CONTINUE_TASK`，先核验产物/证据/副作用哈希再续作；
- Founder 在 Dify 阶段验收中退回且调整仍在 M1 P0 和原授权内时，进入 `FOUNDER_RETURNED → CONTINUE_TASK`，实施实际调整并重验受影响范围；
- Founder 退回不要求重生成 Root Prompt，也不自动扩大 P0；若方向改变合同、模块责任、权限、生产对象或受保护资产，进入 `REBASE_TASK` 并停止等待裁决。

### 3.3 执行侧自主权

在 P0、授权和验收不变的前提下，执行总负责人自主决定：

- 侦察、拆解、并行和实现顺序；
- 文件、节点、字段、类型、Schema、适配方式和内部架构；
- 复用、最小重构或替代技术路径；
- 测试、有限夹具、诊断工具和证据组织；
- 失败后的根因修复和实质不同换路；
- 辅助执行单元的使用，但只有总负责人可写最终任务状态。

普通 HOW、文件布局、节点连接、Schema 设计、迁移方式、单测写法、Git 提交组织和普通技术缺陷不得上推 Founder。只有会改变产品语义、验收口径、权限、受保护资产、生产环境或模块责任的事项才请求 Founder 裁决。

---

## 4. M1 P0 工程施工要求

### 4.1 ChatGPT 式自然语言交互

- 接受自然语言、附件说明、合法业务资料和有效历史产物；
- 不要求用户填写内部字段表、固定问卷、夹具、编号或精确口令；
- 普通咨询、创意讨论和跑题正常处理，不强制建档或误触发能力；
- 用户一次说清目标并要求执行时，任务范围内的可逆生成和内部调用不逐层确认；
- 只有对外发布、正式当前版本写回、权限变化、不可逆动作、经营承诺，以及长期定位/人设/规则正式变更才要求相称的明确确认；
- 产品运行时不得出现“Founder 审核”或同义角色；Founder 只存在于项目治理和阶段产品验收层。

### 4.2 任务上下文编译

从用户自然语言、合法资料和有效历史产物编译轻量、可消费的当前任务上下文。业务语义至少包括：

- `current_task`：用户此刻要完成的工作、对象、平台、交付形态和当前状态；
- `content_item_scope`：仅本条内容的要求、禁忌和临时偏好；
- `cycle_scope`：本周期目标、节奏、数量、主题、实验和资源约束输入；
- `account_scope`：当前账号稳定但可修订的事实与要求；
- `long_term_scope`：经合法来源和适当确认成立的长期定位、边界与持续规则；
- `primary_goal`、有限 `secondary_goals`、`priority_order`、`non_sacrifice_constraints` 和显式冲突；
- 用户原话/资料引用、来源、证据、确认状态、权限、作用域、时效、可用性和缺口；
- 当前有效 `open_threads`、用户选择、撤回、修改方向和风险确认。

不得把本条偏好自动升级为周期或长期规则，不得把多个目标压成无法解释的总分，不得把缺失信息编造成已确认事实。

### 4.3 五维来源状态与合法等价输入

对进入上下文的事实或产物至少保留：`source`、`permission`、`scope`、`freshness`、`confirmation`，并区分 `available / missing / not_applicable / stale / denied / invalid`。

自然语言、合法资料和有效历史产物只要表达相同业务核心，就必须允许进入相同能力；来源差异仍要保留。不得因缺少内部表单、固定字段名或特定上游产物而拒绝合法等价输入。

### 4.4 最小追问与局部降级

- 只追问会阻断**当前分支**的最关键一项；
- 非阻断缺口以暂定假设、缺口标记、范围缩小或降级承诺继续；
- 用户拒绝补充时，能合法降级就继续，不能合法继续才暂停该分支；
- Matrix 资料不足只暂停真实依赖 Matrix 正式结论的分支；明确选题直达 Brief、已有脚本直达 Production、合法成片信息直达 Packaging 和同轮无关诉求继续；
- M1 不编造 Matrix 结论，也不把暂定画像写成长期真源。

### 4.5 唯一调用意图与非固定路由

M1 必须形成唯一有效的当前调用意图/调用计划，按任务需要选择零个、一个或多个能力：

- 普通咨询可以不调用专业组件；
- Matrix、Campaign、Content Brief、Creative Script、Production Director、Publishing & Packaging 均允许满足合同的直接入口；
- 组合调用必须由真实依赖决定，不得暗中补跑不需要的前置；
- 不建立第二套路由，也不把关键词标签当唯一决定依据；
- M1 只决定“需要什么能力和上下文”，不执行专业判断或组件生产。

### 4.6 用户调整必须产生结果

用户提出“换方向”“只改这里”“先讲通勤”“混合两个候选”“保留旧版派生”等合法调整时：

1. 理解修改对象、作用域和不可牺牲条件，不要求用户判断内部应改哪一层；
2. 更新受影响上下文和调用计划，把意图交给正确责任组件；
3. 返回实际调整结果，或者在事实、权限、合规、不可牺牲条件或冻结门禁形成真实硬边界时，说明具体冲突并给出最接近目标的合法替代；
4. 只有可验证地已满足目标或确实无需变化时才允许保持不变；
5. 不得用“内部状态不允许”“先重走全链”“只有这一份”或解释原方案合理性回避调整；
6. M1 模块测试证明意图和影响范围正确进入接口；真实跨组件调整结果留给 M4/M5，不冒充已经完成。

### 4.7 多诉求、撤回和诚实恢复

- 同轮主诉求和附带诉求分别保留，完成一项后返回仍有效的 `open_threads`；
- “继续”“这个”“第三条”等短表达只绑定当前明确对象；
- 用户撤回选择或改变目标时，旧授权不静默复用，只更新真实受影响范围；
- Tool、模型、网络、Dify、状态或下游失败时，如实说明未完成部分、已完成部分和恢复方法；
- 不编造根因、不假装落库/完成、不把内部错误归咎用户表达；
- 恢复不重复已成功且输入未变的昂贵组件，不重复未知外部副作用。

---

## 5. 稳定跨窗口接口与责任边界

本 Prompt 冻结业务语义，不冻结物理字段、类、API、Schema 或节点。

| 接缝 | M1 交付/消费 | M1 不负责 |
|---|---|---|
| M1 → M2 | 任务身份、上下文投影、原话/资料引用、来源/权限/作用域/时效/确认/缺口、用户选择/撤回/修改 | 数据库、事务、幂等、版本晋升、发布实例、反馈归属、跨周期恢复 |
| M2 → M1 | 当前工作空间内受权限/时效约束的最小业务投影、恢复状态、稳定版本引用 | 读取全租户数据、用 Dify Memory 代替业务真源、替 M2 决定写回 |
| M1 → M3 | 目标层级、账号/周期输入、平台、期望量/产能输入、表达裁量、事实与缺口 | 账号阶段诊断、周期策略、组合、节奏、实验、复盘和保持不变判断 |
| M1 → M4 | 唯一调用意图/计划、任务上下文、等价输入/缺口、修改意图、继续/暂停分支 | 组件执行、专业适配内部、局部重跑、失效传播、生产与包装 |
| M4 → M1 | 候选与用户交付投影、事实/权限/合规门禁证据、调整或失败结果 | 替 M4 作专业判断、直接修改专业产物 |

接口必须满足：

- 使用稳定能力 ID 与接口版本，保留来源和原始引用；
- M3 与 Campaign 进入 Brief 时使用同一种 Content Task 业务语义；
- M1 的调用计划是唯一语义真源，M4 不擅自改选能力，M1 不执行组件；
- 下游未实现时允许冻结夹具/契约替身，但必须标记为 M1 模块证据，不得声称跨会话、跨周期或完整纵向链已成立；
- 接口变化如改变用户流程、默认策略、权限、目标优先级、模块责任或 MVP 范围，提交影响和证据给 Founder；普通技术适配自主解决。

---

## 6. 代表性场景与回归范围

以下为必跑有界代表集，可增加有限高价值场景，但不得无限扩张：

1. 用户仅用一段自然介绍启动，无数据库夹具或表单仍能形成可继续上下文；
2. “这条不要剧情”只作用本条；明确长期要求才进入长期作用域；
3. 混合经营目标保留主目标、有限次目标、优先级和不可牺牲条件；
4. 自然语言、合法资料和有效历史产物形成核心等价上下文，同时保留来源状态差异；
5. 非阻断资料缺失继续；真正阻断时只问一项；拒绝补充后合法降级；
6. Matrix、独立 Campaign、选题直达 Brief、脚本直达 Production、成片信息直达 Packaging，不补跑无关前置；
7. Matrix 缺失只暂停依赖分支，同轮无关诉求继续；
8. 普通咨询、跑题和解释请求不误触发组件或修改任务核心；
9. 一轮多诉求均保留，完成一项后能回到另一项；
10. 短指代、撤回、目标改变和方向调整对象准确，旧授权不复用；
11. 局部修改、方向替换、候选混搭、保留旧版派生均进入实际结果闭环；
12. 无依据事实、越权素材或违规承诺只阻止具体不合法主张，并给合法替代；
13. 普通可逆内部动作无 Founder 审核；高风险正式动作仍有明确确认；
14. 理解失败、状态失败、下游 Tool 失败和 Dify 暂态故障各至少一个受控场景；
15. 最终候选在专用 Dify App 完成代表性多轮运行并与最终 commit 绑定；
16. 回滚/恢复演练不会触碰生产对象，且恢复后候选状态可核验。

既有回归边界：

- A-0～A-4 是受保护行为基线，最终候选必须以相同或受控等价输入做真实回归；
- `V1_NATURAL_LANGUAGE_TEST_CATALOG_v0.1.md` 是历史风险分类，不是 Rebase 目标合同；与新合同冲突的固定上游门、逐级接受或旧槽位假设不得继续作为新 Oracle；
- 旧 Task Snapshot Schema 和 Demo Integration Contract 只作兼容证据；
- 只复验 M1 Delta 直接或传递影响的入口和用户交付，不开放式全跑六份 Skill，不替 M5 做完整专业价值验收；
- “能力下降”必须有可比基线、受控输入和冻结 Oracle，否则只能记为 `NOT_VERIFIED`，不得阻断。

---

## 7. 技术验收标准与证据

| criterion_id | 可观察结果 | 主要验证方式 |
|---|---|---|
| `M1-AC-00` | Founder 对准确 v1.2 的授权、进入模式、实时基线、独立 worktree/分支、Manifest 和保护范围可核验 | 授权记录、Git/远端、账本、合同哈希 |
| `M1-AC-01` | 自然语言、合法资料、有效历史产物均能形成完整任务上下文 | 确定性断言、正负向用例、真实多轮对话 |
| `M1-AC-02` | 当前任务、本条、本周期、账号和长期作用域正确，不无声扩张 | 成对场景、前后投影差异 |
| `M1-AC-03` | 主目标、有限次目标、优先级、不可牺牲条件和冲突取舍不丢失 | 单/混合/冲突目标测试 |
| `M1-AC-04` | 合法等价输入核心等价，同时保留来源、权限、时效与确认差异 | 成对/三路输入、冻结比较器 |
| `M1-AC-05` | 只追问真正阻塞项并局部降级；Matrix 缺失不终止无关分支 | 缺失/拒绝/失效场景、分支断言 |
| `M1-AC-06` | 调用计划按任务选能力，不依赖固定链或关键词标签 | 直接/组合入口、固定链负向测试 |
| `M1-AC-07` | 多诉求、跑题、短指代、撤回、转向只更新受影响范围 | 多轮对话、状态差异、授权绑定 |
| `M1-AC-08` | 合法调整形成真实状态/调用差异或具体硬边界与合法替代 | 前后差异、调整/不变/边界场景 |
| `M1-AC-09` | 普通可逆动作无 Founder 审核；高风险正式动作仍需确认 | 正负向授权矩阵、用户可见文本 |
| `M1-AC-10` | 内部失败诚实可恢复，不伪装成功、不重复副作用 | 故障注入、原始错误、恢复与副作用账本 |
| `M1-AC-11` | M2/M3/M4 接口语义成立，只有一套调用语义真源，未越界 | 契约测试、依赖和图检查、Reviewer |
| `M1-AC-12` | A-0～A-4 和真实影响范围无可证实退化 | 可比基线、冻结 Oracle、真实回归 |
| `M1-AC-13` | 最终候选在专用 Dify App 真实运行，App/图/参数/commit 可绑定 | 运行 ID、对象版本、原始输入输出 |
| `M1-AC-14` | 证据、失败历史、账本、Git、远端任务分支和独立审查完整 | 证据表、Review、Git diff、远端 ref |
| `M1-AC-15` | 候选发布前状态、回滚包和恢复演练可核验，未触碰生产 App | 导出/版本引用、演练日志、前后状态 |

每项必须记录：`criterion_id`、`required_change`、`verification_method`、`acceptance_oracle`、`evidence_ref`、`evidence_binding`、`evidence_currency`、`verification_authority`、`result`。

证据规则：

- 无完整证据只能 `NOT_VERIFIED`，不能 `PASS`；
- 文件存在、测试存在、代码已改、静态自述或模型自评不等于能力成立；
- 单次 Dify 成功不替代确定性正负向测试，模拟测试也不替代真实 Dify 代表性运行；
- 失败 Attempt 全部保留；修复后可以重验，但不删失败、不随机重抽；
- 最终 commit、Dify App/图、模型参数或关键配置变化后，受影响的旧证据和审查自动失效；
- 技术 PASS 只表示候选具备提交 Founder Dify 产品验收的条件，不表示 Founder 已接受。

---

## 8. 有界独立审查

```yaml
review_model:
  executor_self_verification: required
  independent_reviewer: one_context_isolated_read_only_agent
  reviewer_write_permission: false
  formal_review_budget: 1
  repair_budget: 1
  closing_verification: affected_scope_only
```

### 8.1 审查顺序

1. 执行负责人完成自验并冻结候选、证据和哈希；
2. 调用一个未参与实现、上下文隔离、只读、无写权限的 Reviewer；
3. Reviewer 进行一次正式审查并冻结阻断集合；
4. 执行负责人只修阻断项，自验直接/传递影响；
5. Reviewer 做一次收口复验，只看原阻断和受影响范围；
6. 不开启第三轮开放式审查。

### 8.2 唯一允许的阻断

Reviewer 只能以两类问题阻断：

1. 明确违反 `M1-AC-00` 至 `M1-AC-15` 中某项；
2. 明确违反安全、权限、受保护资产或数据完整性边界。

每个阻断必须同时提供：

```text
criterion_id
+ 可复核证据
+ 受影响范围
```

命名偏好、文档排版、“可以更优雅”、无验收映射的重构建议、无基线证据的“能力下降”以及要求采用 Reviewer 偏好的实现方案，均不得阻断交付。Reviewer 不修改代码、Dify、账本或证据，只提交只读审查证据。

### 8.3 Founder 退回与审查预算

Founder Dify 产品验收不是第二次开放式技术审查。Founder 在原 P0 内退回后，执行负责人以同一 task 形成新候选并自验受影响范围；已有 Reviewer 只允许做 `affected_scope_only` 的收口确认，不重新开放全局找茬。若 Founder 的方向造成超出原 P0 的广泛合同变化，则停止并请求 Rebase，不以无限审查消化产品范围变化。

---

## 9. Dify 候选部署、真实运行与回滚

### 9.1 一次性授权

本 Root Prompt 一次性授权执行侧在**现有合法凭证可访问的开发/测试工作空间**中：

- 现场识别已有 task 专用 M1 候选 App；不存在时创建唯一一个带 `DIYU-V1-M1-NATURAL-CONTEXT-001` 标识的专用 App；
- 向该专用 App 导入、更新、配置并发布候选工作流版本；
- 配置完成 P0 必需且不暴露秘密的模型、参数、Tool 和变量；
- 在该 App 内进行真实代表性运行、故障场景和恢复验证；
- 将 Dify 对象/版本/图/参数/运行与最终 Git commit 绑定。

该授权不允许修改或覆盖任何现有生产 App、非本任务 App、生产发布版本、生产流量、真实社交账号或真实业务数据。候选 App 中的“发布”只表示该开发/测试 App 内可运行，不表示生产采用。

如果当前唯一可访问对象是生产 App，或无法可靠区分候选与生产对象，停止 Dify 写入；先提交对象证据和所需最小权限，不得猜测或覆盖。

### 9.2 回滚与恢复包

首次 Dify 写入前保存可核验 before-state：工作空间、App ID、草稿/发布版本、图、节点、Tool、模型和参数。完成前必须交付：

- 仓库候选变更的恢复点和非破坏性恢复步骤；
- Dify 候选发布前导出或稳定版本引用；
- 候选 App 的恢复/回退步骤、适用条件和预计副作用；
- 一次不触碰生产对象的恢复演练，或在真实演练会产生未授权破坏时提交可执行的静态恢复验证并标记限制；
- 恢复后的对象、版本、图、参数和运行状态证据。

不得以清理为名删除候选 App、历史运行或失败证据。需要破坏性清理时另行请求明确授权。

---

## 10. Git 分支与远程收口

- 仓库：`https://github.com/andyan77/diyu-demo.git`；
- 分支：`task/m1-natural-interaction-context-v1`；
- 基线：开工时现场核验的远程默认分支；`2a082269...` 只作编译锚点；
- 使用独立 worktree；不在规划目录或 `repo-files/` 施工；
- 保留用户及其他任务改动，不 force、amend、reset、squash、改写或删除历史；
- 形成可审查 commit 并推送远程任务分支；
- 用远端 ref 证明本地最终 commit 与远端完整 hash 一致；
- 不创建/合并 PR，不合并/直推 `main`；这些动作需要 Founder 对准确外部动作的后续独立授权；
- 推送成功只证明远程落点，不替代技术验收或 Founder 产品验收。

---

## 11. 技术候选与 Founder Dify 产品验收

### 11.1 两道门

执行侧必须严格区分：

```text
工程实现 + 自验 + 有界Reviewer + 真实Dify运行 + 回滚包 + 远程分支
→ TECHNICALLY_READY_FOR_FOUNDER_DIFY_ACCEPTANCE

Founder在Dify画布进行产品与业务实测并明确接受
→ DONE
```

`TECHNICALLY_READY_FOR_FOUNDER_DIFY_ACCEPTANCE` 不是 `DONE`。到达该状态后，持久化完整 Checkpoint，提交 Founder 实测包，并进入 `AWAITING_FOUNDER_DIFY_ACCEPTANCE`；这不是 `BLOCKED` 或 `PARTIAL`。

### 11.2 Founder Dify 实测包

实测包必须使用自然语言，至少包含：

1. 精确 Dify 工作空间、App 名称/ID、候选版本、画布入口和观察时间；
2. 与最终 Git commit、工作流图、模型参数和运行证据的绑定；
3. 代表性自然语言任务，可直接复制到画布，不要求 Founder 填内部表单；
4. 每个任务的用户场景、操作方法、应观察行为和产品判断点；
5. 至少覆盖：自然语言直入、最小阻塞追问、用户调整真实生效、非固定 Matrix/Campaign 流水线、无多余 Founder 审核；
6. 预期与已观察结果、已知硬边界和失败时的安全重试方式；
7. Founder 可直接给出的 `ACCEPT` 或自然语言 `RETURN` 入口。

Founder 只判断真实用户交互是否自然、是否理解产品意图、调整是否有效、输出是否有业务价值，以及接受或退回。Founder 不需要审核文件布局、Schema、节点连接、迁移、单测、Git 规范或普通技术缺陷；这些由执行侧和独立 Reviewer 负责。

### 11.3 Founder 退回

- Founder 提出的调整在 M1 P0 和既有授权内：记录原话、作用域、不可牺牲条件和候选基线，以同一 `task_id` 进入 `CONTINUE_TASK`，形成实际调整、重跑受影响技术验证和 Dify 场景，再提交更新后的实测包；
- 不得只写“已记录建议”或用内部流程拒绝；
- 调整触及生产、受保护合同/Skill、M2/M3/M4 内部职责或扩大权限：说明具体硬边界、保留目标、给最小裁决问题，然后停止相关分支；
- 未受影响且安全的 P0 工作继续，不因一个局部问题冻结全任务。

---

## 12. 强制停止条件

出现以下任一情况，暂停受影响分支并保全证据：

- Founder 尚未授权本准确 v1.2；
- 继续需要修改已接受合同、共享语义、冻结 Oracle、受保护 Skill 或其他模块内部职责；
- 真实冲突会改变用户流程、默认策略、权限、目标优先级、模块责任或 MVP 范围，现有真源无法消解；
- 继续需要覆盖生产 Dify、切生产流量、真实社交发布、权限扩大、不可逆操作或敏感数据越界；
- 外部副作用为 `STARTED/UNKNOWN` 且不能安全查询，重放可能产生不可逆影响；
- 执行协议 v1.3 的 `BLOCKED`、`FAILED` 或 `INVALID` 完整条件真实成立。

技术困难、首条路线失败、上下文长度、实现多解、普通缺陷、可逆测试失败或需要返工，不构成向 Founder 停工询问的理由。

当技术 P0、`M1-AC-00` 至 `M1-AC-15`、独立审查、回滚包、真实 Dify 运行和远程收口全部成立时，立即停止功能扩张并提交 Founder 实测包。Founder 接受后记录 `DONE` 并停止；不得继续润色、顺手重构、启动 M2/M3/M4/M5、合并 main 或生产采用。

---

## 13. Checkpoint 与最终回执

### 13.1 Checkpoint

执行中断或等待 Founder Dify 验收时，必须持久化：

```yaml
task_id: DIYU-V1-M1-NATURAL-CONTEXT-001
task_entry_mode: CONTINUE_TASK
execution_disposition: CONTINUE
task_final_status: null
current_state: IMPLEMENTING_OR_AWAITING_FOUNDER_DIFY_ACCEPTANCE
next_stage_allowed: false
```

同时记录 Task Contract/Prompt/Manifest/基线/产物/证据哈希、Attempt、失败路径、Dify/Git 外部副作用、未完成项和下一项可立即执行动作。Checkpoint 不是 `PARTIAL`，计划和摘要不能冒充进度。

### 13.2 技术回执

提交 Founder 实测前的技术回执至少包含：

1. `TECHNICALLY_READY_FOR_FOUNDER_DIFY_ACCEPTANCE` 或正式失败状态；
2. `task_id`、进入模式、Prompt SHA、Task Contract Hash、Manifest ID/Hash；
3. 实时默认基线、worktree、任务分支、本地/远端 commit 和远端访问证明；
4. Dify 工作空间、专用 App、候选版本、图/配置、模型参数、运行 ID 与 commit 绑定；
5. 文件变更清单，删除/重命名也必须披露；
6. `M1-AC-00` 至 `M1-AC-15` 逐项结果、验证权威、证据和 `CURRENT/STALE`；
7. 正向、负向、故障、真实 Dify 和受影响回归结果；
8. A-0～A-4、直接入口、Matrix 局部阻断、用户调整和跨模块边界结论；
9. 全部 Formal Attempt、失败路径、重试和副作用账本；
10. Reviewer 候选哈希、冻结阻断集合、修复和收口复验；
11. 回滚包、恢复演练、已知限制和 `NOT_VERIFIED`；
12. 独立的 Founder Dify 实测包入口。

### 13.3 最终状态

- `DONE`：技术候选全部通过，Founder 已在 Dify 产品验收中明确接受；
- `AWAITING_FOUNDER_DIFY_ACCEPTANCE`：技术通过并已提交实测包，不是终局失败；
- `FOUNDER_RETURNED`：Founder 在原 P0 内退回，必须同 task 继续；
- `BLOCKED`：只按执行协议 v1.3 的完整六项门槛；
- `FAILED`：有效证据表明合理路径穷尽后 P0 仍不成立，且不是治理阻塞；
- `INVALID`：决定状态的运行或证据整体不可修复地失真；
- `PARTIAL`：禁止作为最终状态。

任何状态默认：

```text
next_stage_allowed = false
main_merge_authorized = false
production_adoption_authorized = false
```

禁止用“基本完成”“总体可用”“大体通过”代替正式状态和证据。即使 `DONE`，也不证明 M2/M3/M4/M5 或完整单账号持续运营纵向链已经成立。

---

## 14. Prompt 冻结信息

```yaml
prompt_file: M1_ENGINEERING_EXECUTION_PROMPT_v1.2.md
planning_compiled_at: 2026-08-25
planning_output_scope: W1-M1 only
compile_baseline: main@2a0822692802ac084d92e032f098da33079f063d
supersedes_for_new_execution: M1_ENGINEERING_EXECUTION_PROMPT_v1.1.md
task_contract_hash: d6b0b3d84cdf18f0c19f224cd5e9e43ca03839e53b95b7b667411cfb8e647df3
prompt_sha256: 见规划侧最终交付回执；不内嵌自身哈希，避免自引用
engineering_execution_performed: false
```
