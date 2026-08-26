# M1 Engineering Execution Rebase Prompt v1.3

## 0. 任务身份、激活方式与唯一目的

你是笛语 V1 单账号持续内容运营纵向切片 M1 的受边界约束执行总负责人。

本文件不是新的 Root Execution Prompt，不建立新任务，不要求从头施工。它是 `DIYU-V1-M1-NATURAL-CONTEXT-001` 的版本化 `REBASE_TASK` Prompt，用于修正 M1 v1.2 稳定 Task Contract 的治理完整性，并明确 `V1_DECISION_CHAIN_STAGE_BASELINE_v0.2.md` 中哪些内容已经被后续事实取代、哪些边界继续有效。

Founder 将本准确文件置于真实仓库根目录并明确告知你执行时，即表示授权本次 Rebase 以及在原 M1 P0 和原授权范围内接续剩余工程。该动作不授权扩大 P0、修改生产对象、修改受保护 Skill、建设 M2/M3/M4、合并 main 或生产采用。

```yaml
prompt_id: M1_ENGINEERING_EXECUTION_REBASE_PROMPT
prompt_version: "v1.3"
task_id: DIYU-V1-M1-NATURAL-CONTEXT-001
task_entry_mode: REBASE_TASK
previous_prompt_ref: decision-chain/docs/M1_ENGINEERING_EXECUTION_PROMPT_v1.2.md
previous_prompt_sha256: b0adc1fc770abcb09dc2466d36a4803e3dba81ddafb63876d396e10848c37e4a
previous_task_contract_hash: d6b0b3d84cdf18f0c19f224cd5e9e43ca03839e53b95b7b667411cfb8e647df3
engineering_restart_required: false
preserve_existing_work: true
preserve_attempts_and_failures: true
reset_review_budget: false
main_merge_authorized: false
production_adoption_authorized: false
```

如果同一 `task_id` 已在执行，先读取其最新 Manifest、Checkpoint、Attempt、失败路径、Git/远端、Dify 候选对象、审查记录和外部副作用状态，然后接续。不得新建重复任务，不得重置账本，不得删除失败证据，不得因本 Rebase 默认重做仍为 `CURRENT` 的完成项。

---

## 1. 权威依据与实时基线

### 1.1 本次 Rebase 的权威依据

本次 Rebase 不引入新的产品目标。它依据以下现行治理要求修正 v1.2 的合同编译完整性：

```yaml
planning_protocol:
  path: /mnt/c/Users/Administrator/Documents/Codex/Diyu-V1-Planning/执行Prompt生成总则_规划侧约束框架_v1.2.md
  sha256: 8023bf3e21ff8fb9ba9a2e81b95d1afb178ebf1c04545d0deaac709f603b05b8
execution_protocol:
  path: /mnt/c/Users/Administrator/Documents/Codex/Diyu-V1-Planning/受边界约束的执行总负责人协议_v1.3.md
  sha256: 3ba07a67784056f36211ac634e25a948ce8482f1831aa3dbdc6ab5945ccffcfc
stage_baseline_reference:
  path: decision-chain/docs/V1_DECISION_CHAIN_STAGE_BASELINE_v0.2.md
  sha256: 977933ac794145b83eb59f91d47f86c3744b8dd3f766b07ba28a41a7fb04613f
```

执行时按命题所属权威域判断，不使用一条跨权威域总排序相互覆盖：

- 安全、法律、权限和数据治理命题，以强制边界与 Founder 准确授权为准；
- 产品目标、模块责任和业务语义，以 Founder 裁决及已接受产品/共享合同为准；
- 当前代码、Git、Dify、对象版本和运行状态，以现场可核验事实为准；
- 本任务 P0、非目标、允许 Delta、受保护资产和验收合同，以本 v1.3 Task Contract 为准；
- 是否通过某项验收，以该 criterion 的冻结 Oracle、验证权威和绑定证据为准；
- EP-00、旧 Schema、旧 Prompt、旧 Stage Baseline 和历史运行结论只在其原绑定范围内作为证据，不自行改写当前目标或当前状态。

### 1.2 规划侧最近一次只读观察

```yaml
observed_at: 2026-08-25
repository: /home/faye/diyu-demo
remote: https://github.com/andyan77/diyu-demo.git
remote_default_branch: main
observed_local_head: 78a4ad8a932592bac0b45e9ce835d3dc77ce7374
observed_origin_main: 78a4ad8a932592bac0b45e9ce835d3dc77ce7374
observed_github_main: 78a4ad8a932592bac0b45e9ce835d3dc77ce7374
unrelated_untracked_path_observed:
  - m3-account-content-operator-semantic-v1.0/
```

这只是观察锚点。执行侧在首次新增写入或外部副作用前必须重新现场核验默认分支、任务分支/worktree、当前 commit、未提交改动、Manifest/Checkpoint、Dify 候选 App、发布版本、运行和副作用状态。不得触碰、吸收、覆盖或删除无关 M3 目录及其他用户/任务资产。

### 1.3 Stage Baseline v0.2 的继续有效与已取代部分

`V1_DECISION_CHAIN_STAGE_BASELINE_v0.2.md` 是其形成时的阶段状态快照，不是当前全部授权状态。以下内容已经被后续有权合同和已完成预检取代，不得恢复：

- 子合同仍为 v0.1 且未被 Founder 接受；
- 只授权 `V1-REBASE-EP00-CURRENT` 只读预检；
- 两份 EP-00 尚未完成；
- M1 工程施工尚未获得 Founder 对准确执行 Prompt 的授权。

以下内容继续有效，必须保留：

- v0.1 A/B 阶段的历史 `PARTIAL` 结论仍是历史事实，不得回写改成全面通过；
- A-0～A-4 对话修复、三份决策 Skill 用户可见产物及其原始证据属于受保护回归基线；
- G-01～G-12 及 v0.1 未完成项不因 M1 完成自动关闭；只有有权验收和证据可改变各自状态；
- 下列六条能力声明继续禁止，一条不减：
  1. `V1 已全面通过`；
  2. `三份 Skill 集成后质量没有下降`；
  3. `DeepSeek 普遍优于 Qwen`；
  4. `Skill 普遍优于无 Skill`；
  5. `当前结果可跨品牌、跨行业推广`；
  6. `当前系统已经具备生产可用性`。

Stage Baseline 追加的“子合同未接受”和“EP-00 未完成”两条旧阶段声明已经被后续事实取代，不得继续作为当前限制，也不得反向改写历史文件。

---

## 2. v1.3 稳定 Task Contract

`TASK_CONTRACT_BEGIN` 与 `TASK_CONTRACT_END` 之间 YAML 代码块的块内 UTF-8 字节是新的稳定合同哈希对象；围栏与标记不计入。执行侧必须按原字节重算并核验文末 `task_contract_hash`，然后写入新的 Rebase Manifest。

<!-- TASK_CONTRACT_BEGIN -->
```yaml
contract_version: "1.3"
previous_contract_version: "1.2"
previous_task_contract_hash: d6b0b3d84cdf18f0c19f224cd5e9e43ca03839e53b95b7b667411cfb8e647df3
task_id: DIYU-V1-M1-NATURAL-CONTEXT-001
task_type: MIXED
risk_level: HIGH

final_deliverable: >-
  在原 M1 独立任务分支、worktree 和 task_id 专用 Dify 候选/测试 App 中，接续并完成
  M1 全部 P0：ChatGPT 式自然交互、任务上下文编译、唯一调用意图/计划、真实运行、
  技术验收、有界独立审查、回滚准备和远程任务分支收口；随后提交 Founder Dify 实测包。
  技术候选完成、Founder 产品接受和生产采用必须分开。

core_problem: >-
  当前系统仍可能把用户自然表达压入内部字段、关键词或固定 Matrix→Campaign→Brief 顺序，
  丢失任务层级、目标优先级、来源状态和调整意图，并把局部缺口或普通系统步骤升级为整任务硬停或
  Founder 审核。M1 必须把自然语言、合法资料和有效历史产物编译为下游可消费、可追溯、
  可局部降级的任务上下文和唯一调用意图，同时不侵入 M2、M3、M4 的内部职责。

observable_changes:
  - 用户可用自然语言、合法资料或有效历史产物直接启动和调整任务，不填写内部表单或固定口令
  - 系统明确区分当前任务、本条、本周期、当前账号和长期要求
  - 主目标、有限次目标、优先级、不可牺牲条件和冲突取舍可被编译并传给下游
  - 只有真正阻塞当前分支的关键问题被追问，非阻断缺口局部降级
  - 零个、一个或多个能力按当前任务依赖选择，不存在固定 Matrix→Campaign→Brief 流水线
  - 用户调整形成真实上下文或调用差异；不能调整时返回具体、可核验的硬边界和合法替代
  - 普通可逆内部动作不要求 Founder 逐步审核，高风险正式动作仍有相称确认

authorized_scope:
  read:
    - 真实仓库、远端默认分支、任务分支/worktree、Manifest、Checkpoint、Attempt、失败和证据账本
    - 当前授权 Dify 工作空间内本 task_id 专用候选/测试 App 及其草稿、发布、配置和运行
    - 已接受合同、共享前言、EP-00、历史 Oracle、接口、测试和受保护回归证据
  write:
    - 原 M1 独立任务分支/worktree 内完成既有 P0 必需的代码、配置、DSL、适配器、测试、有限夹具、文档和证据
    - 本 task_id 的 Manifest、Checkpoint、Attempt、失败路径、验收和外部副作用账本
    - 唯一 task_id 专用 Dify 候选/测试 App；允许创建或恢复、导入、更新、配置和候选发布
  execute:
    - 只读侦察、实现、自验、确定性测试、故障注入、受影响回归、真实 Dify 候选运行和恢复验证
    - 一名未参与实现、上下文隔离、只读且无写权限的独立 Reviewer
    - commit、推送原远程任务分支并核验本地与远端完整 hash
  network:
    - 读取 GitHub 远端与默认分支状态，推送本任务分支
    - 仅在现有合法凭证内操作上述唯一 M1 专用 Dify 候选/测试 App

non_goals:
  - 修改、覆盖、重发、下线、切流或采用任何生产 Dify App 或生产对象
  - 修改非本 task_id 的 Dify App、工作流、凭证、知识库、运行记录或其他任务资产
  - 合并或直推 main、创建或合并 PR、force、amend、reset、squash 或改写历史
  - 建设或迁移 M2 数据库、业务 Schema、业务持久化、版本、发布、反馈或跨周期记忆
  - 执行 M3 账号诊断、周期策略、内容组合、节奏、实验或复盘判断
  - 执行 M4 专业组件、生产链 Runtime、局部重跑或依赖失效传播
  - 重写、中性化或旁路六份专业 Skill 的专业判断
  - 建设第二套目标路由、账号状态库、审批系统、工作流引擎、知识库或通用数据平台
  - 提前实现 M5、宣称完整纵向链成立、经营结果提升、V1 全面通过或生产可用
  - 声称 DeepSeek 普遍优于 Qwen、Skill 普遍优于无 Skill或当前结果可跨品牌跨行业推广

source_of_truth:
  founder_decisions:
    - Founder 对本准确 v1.3 Rebase Prompt 的交付与执行授权
    - 已冻结的 Founder 产品语义及后续可核验明确裁决
  frozen_product_contracts:
    - decision-chain/docs/V1_DECISION_CHAIN_REBASE_PRODUCT_CONTRACT_v0.1.md
    - decision-chain/docs/V1_SINGLE_ACCOUNT_SLICE_CONTRACT_v0.2.md
    - decision-chain/docs/V1_M0_SHARED_CONTRACT_TASK_CONTEXT_SNAPSHOT_v0.1.md
    - decision-chain/docs/V1_M0_SHARED_CONTRACT_EIGHT_CAPABILITIES_v0.1.md
    - decision-chain/docs/V1_M0_SHARED_CONTRACT_VERSION_PUBLISH_FEEDBACK_v0.1.md
    - decision-chain/docs/V1_M0_SHARED_CONTRACT_WRITE_PERMISSION_RECOVERY_v0.1.md
    - decision-chain/docs/V1_M1_M4_CONSTRUCTION_PROMPT_SHARED_PREAMBLE_v0.1.md
  formal_data_constraints:
    - 当前 Git、Dify、对象版本、模型参数、运行和账本事实必须现场核验，不由历史摘要覆盖
    - 权限、来源、作用域、时效、确认和外部副作用状态必须保留
  task_brief:
    - decision-chain/docs/M1_ENGINEERING_EXECUTION_PROMPT_v1.2.md 中未被本 Rebase 明确替代的原 M1 P0、边界和执行要求
    - 仓库根目录中的本 M1_ENGINEERING_EXECUTION_REBASE_PROMPT_v1.3.md

accepted_baseline:
  - 执行时现场核验的远程默认分支及其有权后继合同
  - 编译观察锚点 main@78a4ad8a932592bac0b45e9ce835d3dc77ce7374 只作 Delta 比较
  - 已完成且有稳定证据绑定的现有 M1 工程产物、测试、Dify 候选、Checkpoint、Attempt 和审查记录
  - A-0至A-4、现有六能力、CS-1、PRE/MIXED/FINAL、事实核验、Returns 和用户交付投影
  - V1_DECISION_CHAIN_STAGE_BASELINE_v0.2 的历史 A/B 结论、未关闭差距和六条持续能力声明边界

allowed_delta:
  - 继续完成 v1.2 已授权但尚未完成的 M1 P0，不扩大产品目标或模块范围
  - 建立 v1.3 Rebase Manifest、新 Task Contract Hash、新旧合同差异和证据影响映射
  - 将 Stage Baseline 的过期阶段状态与持续有效行为、差距和声明边界显式分开
  - 为新增稳定合同字段补齐确定性合同检查、验收映射、证据引用和最终回执
  - 只修复现有实现中明确违反 M1-AC-00至M1-AC-15或安全边界的项目
  - 对受合同、候选、配置、环境或实现变化直接或传递影响的验收项定向复验

protected_assets:
  - 已接受父子产品合同、四份共享合同、Phase 0 前言和冻结验收语义
  - Matrix 对长期定位、人设和账号职责的专业决定权
  - M2 持久化决定权、M3 运营判断决定权、M4 组件执行决定权
  - Matrix、Campaign、Content Brief、Creative Script、Production Director、Publishing & Packaging 六项专业 Skill 的源文件、专业 Prompt、判断规则和已证明能力
  - 现有六项专业能力、CS-1、PRE/MIXED/FINAL、事实核验、Returns 和用户交付投影
  - A-0至A-4 原始证据、历史 Oracle、全部失败 Attempt 和运行记录
  - Stage Baseline 的历史结论、G-01至G-12 状态和六条持续禁止声明
  - 用户、工作空间、账号、素材、隐私、凭证、生产对象、已发布内容及其他任务资产

target_environment:
  repository: /home/faye/diyu-demo
  branch: task/m1-natural-interaction-context-v1
  worktree: existing_or_recovered_independent_m1_worktree
  dify_workspace: 执行时现场确认的当前授权开发或测试工作空间
  dify_app: 唯一 task_id 专用 M1 候选或测试 App
  dify_publish_authority: 仅发布到该候选或测试 App，不代表生产采用
  database_migration_authority: NONE_FOR_M1

p0:
  deliverables:
    - M1 可运行实现与 M2、M3、M4 稳定业务语义接缝
    - 任务层级、目标层级、来源状态、等价输入、最小追问和局部降级
    - 非线性唯一调用计划、直接入口、Matrix 局部阻断和多诉求继续
    - 用户调整、风险确认、诚实失败恢复和自然语言回执
    - 确定性测试、真实 Dify 运行、受影响回归、技术审查和回滚包
    - 远程任务分支、技术回执和 Founder Dify 画布实测包
  acceptance_criteria:
    - M1-AC-00 授权、进入模式、实时基线、独立工作区、Manifest和保护范围可核验
    - M1-AC-01 自然语言、合法资料和有效历史产物均能形成完整任务上下文
    - M1-AC-02 当前任务、本条、本周期、账号和长期作用域正确且不无声扩张
    - M1-AC-03 主目标、有限次目标、优先级、不可牺牲条件和冲突取舍不丢失
    - M1-AC-04 合法等价输入核心等价且保留来源、权限、时效和确认差异
    - M1-AC-05 只追问真正阻塞项并局部降级，Matrix缺失不终止无关分支
    - M1-AC-06 调用计划按任务选能力，不依赖固定链、内部表单或关键词标签
    - M1-AC-07 多诉求、跑题、短指代、撤回和转向只更新受影响范围
    - M1-AC-08 合法调整形成真实状态或调用差异，或给出具体硬边界和合法替代
    - M1-AC-09 普通可逆动作无Founder审核，高风险正式动作仍需相称确认
    - M1-AC-10 内部失败诚实可恢复，不伪装成功且不重复未知副作用
    - M1-AC-11 M2、M3、M4接口语义成立，只有一套调用语义真源且未越界
    - M1-AC-12 A-0至A-4和真实影响范围无可证实退化
    - M1-AC-13 最终候选在专用Dify App真实运行且对象、图、参数、运行和commit可绑定
    - M1-AC-14 证据、失败历史、账本、Git、远端分支和独立审查完整
    - M1-AC-15 候选发布前状态、回滚包和恢复验证可核验且未触碰生产App
    - M1-AC-16 Stage Baseline过期状态未被恢复，持续历史、差距和六条能力声明边界被保留

p1:
  enabled: false
  deliverables: []
  acceptance_criteria: []
  permitted_next_stage: NONE

allowed_final_states:
  - DONE
  - BLOCKED
  - FAILED
  - INVALID

p2_evidence_requirements:
  - 每项验收记录criterion_id、required_change、verification_method、acceptance_oracle、evidence_ref、evidence_binding、evidence_currency、verification_authority和result
  - 每个Formal Attempt保留输入、输出、模型参数、代码、DSL、Dify对象、Oracle、环境、日志、结果和实质差异
  - 失败Attempt、已证伪路径和真实异常全部保留，不删除失败或随机重抽成功
  - 证据绑定最终commit、输入或哈希、Oracle、Dify App、图、版本、模型参数、环境和观察时间
  - 敏感资料和凭证不明文入库，只保存脱敏引用、必要摘要和稳定哈希
  - Git、Dify和外部副作用按task_id记录；STARTED或UNKNOWN先查目标系统，不盲目重放

acceptance_oracles:
  - M1-AC-00=Founder授权记录、实时Git远端、Manifest、Checkpoint、合同与Prompt哈希
  - M1-AC-01=确定性正负向用例与最终候选真实多轮Dify对话
  - M1-AC-02=本条、本周期、账号、长期成对场景及前后上下文投影差异
  - M1-AC-03=单目标、混合目标和冲突目标的结构断言与用户可见行为
  - M1-AC-04=自然语言、合法资料、有效历史产物成对或三路输入及冻结比较器
  - M1-AC-05=缺失、拒绝、失效和Matrix局部阻断场景的分支断言
  - M1-AC-06=Matrix、Campaign、Brief、Production、Packaging直接入口和固定链负向测试
  - M1-AC-07=多轮多诉求、跑题、短指代、撤回和转向的状态与授权差异
  - M1-AC-08=调整前后上下文、调用、运行和用户交付差异或可核验硬边界
  - M1-AC-09=冻结风险授权矩阵及正负向用户可见文本
  - M1-AC-10=故障注入、原始错误、恢复记录和外部副作用账本
  - M1-AC-11=跨模块契约测试、依赖检查、图检查及只读Reviewer证据
  - M1-AC-12=A-0至A-4相同或受控等价输入、可比基线、冻结Oracle和最终候选真实回归
  - M1-AC-13=最终Dify运行ID、App与版本、工作流图、模型参数、原始输入输出和最终commit绑定
  - M1-AC-14=逐项证据表、全部Attempt、Reviewer记录、本地与远端完整hash
  - M1-AC-15=before-state、回滚导出或稳定版本、恢复步骤、演练日志和after-state
  - M1-AC-16=Stage Baseline延续与取代矩阵、禁止声明确定性检查和最终回执声明审计

evidence_reuse_policy:
  default: EXACT_BINDING_ONLY
  final_full_run_required: true
  dynamic_evidence_requires_refresh: true
  criterion_dependency_map:
    - 合同与授权变化影响M1-AC-00、M1-AC-14和M1-AC-16
    - 上下文编译或路由变化影响M1-AC-01至M1-AC-12
    - 代码、DSL、Dify图、模型或参数变化至少影响其直接或传递用例以及M1-AC-13
    - 候选版本、commit、环境或运行变化影响M1-AC-12至M1-AC-15
    - 回滚、远端或证据组织变化影响M1-AC-14至M1-AC-15
  final_full_run_definition:
    - M1-AC-00至M1-AC-16最终逐项判定
    - M1确定性正向、负向、故障和受影响回归集
    - A-0至A-4最终候选真实Dify回归
    - v1.2代表性场景的最终候选真实Dify运行
    - 不包含六份专业Skill全量价值评测或M5完整纵向链验收

verification_authority:
  executor_self_check:
    - M1-AC-00至M1-AC-16实现、自验、影响分析和证据绑定
  deterministic_checkers:
    - Task Contract与Prompt哈希、Schema或类型、契约测试、正负向测试、Git与远端hash
    - Stage Baseline延续与取代矩阵以及六条禁止声明检查
  independent_reviewer: 一个未参与实现、上下文隔离、只读、无写权限的Reviewer，只按冻结criterion或安全边界阻断
  founder_authority_scope:
    - 在Dify画布判断交互是否自然、是否理解产品意图、调整是否真实、输出是否有业务价值
    - ACCEPT或在原P0内RETURN；产品语义、权限、生产和受保护资产变化由Founder裁决

review_contract:
  required: true
  authority: one_context_isolated_read_only_agent
  scope:
    - M1-AC-00至M1-AC-16
    - 安全、权限、受保护资产和数据完整性边界
  formal_review_budget: 1
  repair_budget: 1
  closing_verification: affected_scope_only
  budget_accounting: 自v1.2起按同一task_id累计，本Rebase不重置已消耗预算
  blocker_format: criterion_id加可复核证据加受影响范围
  closure_rule: 不开启第二次开放式正式审查；修复或Founder原P0退回后的候选只做受影响范围确认
  non_blocking_items:
    - 命名偏好、文档排版、可以更优雅、无验收映射重构、无基线能力下降主张和Reviewer方案偏好

completion_checks:
  artifact_persisted: REQUIRED
  target_environment_run: REQUIRED
  fixed_configuration_run: REQUIRED
  positive_tests: REQUIRED
  negative_tests: REQUIRED
  regression_tests: REQUIRED
  raw_evidence_preserved: REQUIRED
  git_closure: REQUIRED
  remote_closure: REQUIRED

retry_policy:
  transient_retry_allowed: true
  maximum_authorized_attempts: 受执行协议v1.3、实质不同路径和冻结审查预算共同约束
  blind_resampling_allowed: false
  all_attempts_must_be_preserved: true

remote_target:
  repository: https://github.com/andyan77/diyu-demo.git
  branch: task/m1-natural-interaction-context-v1
  required_proof:
    - 本地最终commit与远端分支完整hash一致
    - 接收方可以访问和复核远端对象
  merge_main: NOT_AUTHORIZED

next_stage_default: false
```
<!-- TASK_CONTRACT_END -->

---

## 3. 旧—新合同差异与证据影响

本 Rebase 只做以下合同变化：

1. 补入 `core_problem`、`observable_changes` 和按权威域组织的 `source_of_truth`；
2. 明确 `p1.enabled=false`，最终状态只允许 `DONE/BLOCKED/FAILED/INVALID`，`PARTIAL` 仍被禁止；
3. 把 M1-AC-00至M1-AC-15 的既有语义放入稳定合同，并增加仅用于基线声明治理的 `M1-AC-16`；
4. 冻结 `acceptance_oracles`、证据复用策略、验证权威、Reviewer合同、完成检查、重试和远程收口开关；
5. 显式保留 Stage Baseline 的历史行为、未关闭差距和六条禁止声明，同时废止其已经过期的阶段授权状态；
6. 澄清最终候选的运行和审查顺序，不扩大工程 P0。

这些变化不授权重新设计产品，不自动证明或否定当前实现，也不使旧证据整体失效。

执行侧必须形成 `REBASE_IMPACT_MAP`：

```yaml
required_columns:
  - criterion_id
  - prior_status
  - prior_evidence_ref
  - prior_binding
  - contract_semantics_changed
  - implementation_or_environment_changed
  - evidence_currency_after_rebase
  - action
allowed_actions:
  - REUSE_CURRENT
  - REMAP_AND_VERIFY_BINDING
  - REVERIFY_AFFECTED_SCOPE
  - NOT_VERIFIED
```

复用规则：

- AC语义未变、候选实现/输入/Oracle/模型参数/环境绑定未变且依赖图证明不受影响的证据，可以 `REUSE_CURRENT`；
- 仅因 Task Contract 版本变化但实际 AC 语义相同的证据，可 `REMAP_AND_VERIFY_BINDING`，不得伪造新的运行时间；
- 动态 Git、Dify、远端、权限、运行和外部副作用证据必须刷新；
- M1-AC-16 必须新增验证；
- 最终全量门仍须按本合同的 `final_full_run_definition` 在最终候选上完成；
- 不得为了形式完整全量重跑六份专业 Skill 或 M5 链路。

---

## 4. Active Work Package

按以下顺序接续，但执行负责人可在不改变门禁含义时调整内部并行：

1. 核验本准确 Prompt 的 Founder 交付、文件 SHA、新 Task Contract Hash 和当前任务状态；
2. 定位最近有效 Manifest/Checkpoint，核验 Git、远端、Dify、Attempt、审查预算和副作用；
3. 建立 Rebase Manifest 与 `REBASE_IMPACT_MAP`，不得先改代码再补状态；
4. 继续尚未完成的原 M1 P0，只处理 v1.2 原授权范围；
5. 在最终候选专用 Dify App 上完成确定性测试、真实代表性运行、A-0至A-4和受影响回归；
6. 冻结最终候选、commit、Dify图/参数/运行和证据绑定后进入一次正式只读审查；
7. 若正式审查已经在 v1.2 阶段消耗，不重开开放式审查；只对合同新增项和候选受影响范围使用尚可用的收口确认；
8. 只修冻结阻断集合，任何修复造成的候选变化都必须重跑直接和传递影响测试及真实 Dify 绑定；
9. 完成回滚包、远程分支收口、技术回执和 Founder Dify 实测包；
10. 到达技术门后停止功能扩张，等待 Founder 产品验收。

如果执行侧现状已经超过某一步，只核验其证据后从下一项继续；不得无理由倒退重做。

---

## 5. Reviewer、Founder 与状态边界

Reviewer 只能提出两类阻断：

1. 明确违反 M1-AC-00至M1-AC-16；
2. 明确违反安全、权限、受保护资产或数据完整性边界。

每项阻断必须给出 `criterion_id + 可复核证据 + 受影响范围`。Reviewer 不修改代码、Dify、账本或证据，不得以偏好方案阻断。

Founder 只在 Dify 画布做产品与业务实测，不审核文件布局、Schema、节点、单测、Git规范或普通技术缺陷。Founder 在原 P0 内 RETURN 时，以同一 task继续形成实际调整；不得重开开放式 Reviewer。方向如果改变产品语义、权限、生产对象、受保护资产或 M2/M3/M4 责任，停止受影响分支并提出唯一关键裁决问题。

技术门与产品门仍为：

```text
全部P0 + M1-AC-00至M1-AC-16 + 完成检查 + 有界审查
+ 最终Dify运行 + 回滚包 + 远程任务分支
→ TECHNICALLY_READY_FOR_FOUNDER_DIFY_ACCEPTANCE

Founder在Dify明确ACCEPT
→ DONE
```

`AWAITING_FOUNDER_DIFY_ACCEPTANCE` 和 `FOUNDER_RETURNED` 是运行状态，不是最终状态；Checkpoint 不是 `PARTIAL`。

---

## 6. 强制停止条件

出现以下情况时停止受影响分支并保全证据：

- 没有 Founder 对本准确 v1.3 Rebase Prompt 的交付与执行授权；
- Prompt 文件或 Task Contract Hash 无法核验，且无法从准确原文恢复；
- 继续需要扩大 M1 P0、修改受保护合同/Skill、侵入 M2/M3/M4、修改生产对象或扩大权限；
- 真实基线冲突会改变用户流程、默认策略、目标优先级、验收 Oracle、模块责任或 MVP 范围；
- 外部副作用为 `STARTED/UNKNOWN` 且无法安全查询，重放可能产生不可逆影响；
- 执行协议 v1.3 的 BLOCKED、FAILED 或 INVALID 完整条件成立。

以下不是停工上问理由：普通技术困难、首条路线失败、实现多解、可逆测试失败、需要返工、文件组织、节点设计、Schema选择或当前上下文长度。未受局部阻塞影响且安全的原 P0 工作继续。

---

## 7. Checkpoint、远程收口与最终回执

非终态交接必须持久化：

```yaml
task_id: DIYU-V1-M1-NATURAL-CONTEXT-001
task_entry_mode: REBASE_TASK_OR_CONTINUE_TASK
execution_disposition: CONTINUE
task_final_status: null
current_task_contract_version: "1.3"
previous_task_contract_hash: d6b0b3d84cdf18f0c19f224cd5e9e43ca03839e53b95b7b667411cfb8e647df3
next_stage_allowed: false
```

最终技术回执至少包含：

1. 本 Prompt SHA、新旧 Task Contract Hash、Founder 授权引用和 Rebase Manifest；
2. 当前默认基线、原 M1 worktree/分支、本地与远端最终 commit；
3. 继承的 Checkpoint、Attempt、失败路径、Reviewer预算和外部副作用；
4. 完整 `REBASE_IMPACT_MAP`，披露复用、重映射、失效、复验和 `NOT_VERIFIED`；
5. M1-AC-00至M1-AC-16逐项结果、Oracle、验证权威、证据和时效；
6. 最终确定性正向/负向/故障测试、A-0至A-4、受影响回归和真实 Dify 运行；
7. Stage Baseline 延续/取代矩阵，以及六条禁止声明未被违反的证据；
8. Dify工作空间、专用App、版本、图、参数、运行ID和最终commit绑定；
9. Reviewer正式审查是否已在v1.2消耗、冻结阻断、修复和收口范围；
10. 回滚包、恢复验证、全部已知限制和未验证项；
11. 远程仓库、任务分支、本地/远端完整hash一致及Founder可访问证明；
12. 独立的Founder Dify自然语言实测包。

远程收口只允许推送：

```text
https://github.com/andyan77/diyu-demo.git
branch = task/m1-natural-interaction-context-v1
```

不得合并 main、创建或合并 PR、force、amend、reset、squash 或改写历史。远程推送不等于技术验收或 Founder 产品接受。

任何状态默认：

```text
next_stage_allowed = false
main_merge_authorized = false
production_adoption_authorized = false
```

即使 M1 最终 `DONE`，也不得声称 M2/M3/M4/M5、完整单账号持续运营纵向链、跨品牌推广或生产可用性已经成立。

---

## 8. 冻结信息

```yaml
prompt_file: M1_ENGINEERING_EXECUTION_REBASE_PROMPT_v1.3.md
prompt_location_expected: /home/faye/diyu-demo/M1_ENGINEERING_EXECUTION_REBASE_PROMPT_v1.3.md
task_id: DIYU-V1-M1-NATURAL-CONTEXT-001
task_entry_mode: REBASE_TASK
previous_task_contract_hash: d6b0b3d84cdf18f0c19f224cd5e9e43ca03839e53b95b7b667411cfb8e647df3
task_contract_hash: 94300a76e79c4ea5b731c300ba199a87180f4682c518d0dbc93cf3202eed5d1e
prompt_sha256: 执行侧读取Founder落盘的准确文件后计算并记录，避免自引用
engineering_restart_required: false
preserve_existing_work: true
engineering_execution_performed_by_planning_side: false
```
