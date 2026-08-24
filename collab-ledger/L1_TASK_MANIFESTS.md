# L1 · 合同与 Manifest 定位

> 规则正文见 [COLLAB_CONTINUITY_PROTOCOL.md](COLLAB_CONTINUITY_PROTOCOL.md)。
> 本文件按 `task_id` 定位：**稳定 Task Contract、当前 Manifest、授权依据、起算基线、允许改动范围、受保护资产、终态引用**。
> **只放定位，不复制合同正文。** 追加式：只加不改，更正另起一条。

## 定位表

| task_id | Task Contract | 当前 Manifest | 授权依据 | 终态 |
|---|---|---|---|---|
| `COLLAB-LEDGER-BOOTSTRAP-001` | **v2（当前）§T-001.6** ／ v1（历史）§T-001.1 | v1 §T-001.2（v2 只写收口 Delta 口径，其余继承 v1） | Founder 2026-08-24 明确授权 ＋ 两份收口 Delta | 见 [L2](L2_TASK_STATE_AND_HANDOFF.md) 与 [L3 §CLOSEOUT](L3_ATTEMPTS_AND_EVIDENCE.md) |
| `V1-REBASE-EP00-CURRENT` | [V1 决策链改造产品合同](../decision-chain/docs/V1_DECISION_CHAIN_REBASE_PRODUCT_CONTRACT_v0.1.md) §「授权状态与下一步」 | 尚未编译（任务未开工） | 上位合同 `PRODUCT_CONTRACT_ACCEPTED — REPO_PREFLIGHT_AUTHORIZED` | 未开工 |
| `SINGLE-ACCOUNT-SLICE-EP00` | [单账号纵向切片子合同](../decision-chain/docs/V1_SINGLE_ACCOUNT_SLICE_CONTRACT_v0.1.md) | **不得编译** | **无** —— 子合同 `CONTRACT_REVISION_REQUIRED`，**未被接受，不构成授权** | 不可开工 |

> **上位合同被接受 ≠ 子合同被接受 ≠ 授权 Skill／DSL／持久化／工作流施工。**
> 执行侧**不得**自行宣布任何合同「已接受」，也**不得**自行把状态往上推一级。

---

## §T-001 · `COLLAB-LEDGER-BOOTSTRAP-001`

### T-001.1 Task Contract（稳定合同）

> 下面这个 ```yaml 代码块的**块内字节**即 `task_contract_hash` 的哈希对象。**不含**聊天摘要与执行计划。

```yaml
task_id: COLLAB-LEDGER-BOOTSTRAP-001
task_entry_mode: NEW_TASK
parent_task_id: ""
task_type: MIXED
risk_level: MEDIUM
authority_refs:
  - "Founder 于 2026-08-24 明确授权：在仓库建立所有后续执行 AI 共用的轻量协作连续性规则；已有账本保持，缺失账本从当前基线起补齐。"
  - "Founder 明确指定 DIYU-BOUNDED-EXECUTION-OWNER-PROTOCOL v1.2 与 DIYU-EXECUTION-PROMPT-PLANNING-COMPILER v1.1 作为本任务的治理引用；该任务级引用不改变两份文件自身的 CANDIDATE 文档状态。"
governance_refs:
  - protocol_id: DIYU-BOUNDED-EXECUTION-OWNER-PROTOCOL
    version: "1.2"
    declared_file: 受边界约束的执行总负责人协议_v1.2.md
    declared_sha256: 151808b0749789dc8ff5713193a9a756a0bbd2f0ac46bf2a80d016efbbd3742a
    availability_at_execution: ABSENT
  - protocol_id: DIYU-EXECUTION-PROMPT-PLANNING-COMPILER
    version: "1.1"
    declared_file: 执行Prompt生成总则_规划侧约束框架_v1.1.md
    declared_sha256: 7cd63848ecbda8ad6a69bdf94572a6b0a17954fc373edf8983c42b2e798e25fb
    availability_at_execution: ABSENT
  governance_conformance: NOT_VERIFIED
  governance_note: >-
    两份治理协议以文件名与 SHA-256 被引用，但在本次执行环境中不存在（仓库、远端 main、
    执行机文件系统穷尽检索均未命中），也不允许复制进仓库。因此本任务对两份协议
    「文件内部条款」的符合性无法核验，标 NOT_VERIFIED。实际执行依据是 Execution Prompt
    自身写明的完整 Task Contract 语义（Manifest 字段表、L1—L5 语义、副作用状态枚举、
    完成检查 YAML、终态判定顺序、最小充分约束），Prompt 已声明其自带完整合同语义。
core_problem: >-
  一个没有本次聊天上下文、不依赖前任记忆、只有仓库读取权限的全新执行会话，
  目前无法从仓库自行回答「当前任务合同是什么／上次做到哪／跑过哪些／哪条路已排除／
  往外写过什么」这五问。
final_deliverable: >-
  仓库中存在一处 canonical 协作连续性规则，加上可定位的五类逻辑账本，
  并已进入远程默认工作基线 main。
p0:
  - 建立 canonical 规则说明，位于目标执行代理默认会读取的位置（或经其可达的极薄指针）。
  - 建立 L1—L5 五类逻辑账本，全部可定位、非空模板。
  - 项目级 Current Handoff 按 task_id 区分，不用一个全局「下一步」覆盖并行任务。
  - 历史 57 份 evidence 只建索引目录，不反向补造 Formal Attempt。
  - 通过真正隔离的新执行单元验证五问可独立回答，保留完整原始问答。
  - 规则与账本进入远程默认工作基线 main，并核验最终远端 ref。
p1:
  enabled: false
  reason: "本任务未预定义阶段性交付，因此不得使用 PARTIAL。"
p2:
  - 在 PROJECT_INDEX 与 README 建立可发现入口。
non_goals:
  - 修改任何产品合同、Skill、Reference、Prompt、DSL、Workflow、Dify 配置、业务数据库或 tools/
  - 推进或执行 V1-REBASE-EP00-CURRENT
  - 开展 SINGLE-ACCOUNT-SLICE-EP00
  - 修改、移动、重命名、合并或删除既有 evidence、fixtures 或 Gap Register
  - 为历史运行补造 Attempt、失败路线或副作用条目
  - 清理其他分支、worktree 或未推送提交
  - 建校验脚本、CI、JSON Schema、数据库、事件溯源平台、状态机、模板生成器、Judge 或第二套治理体系
  - 把两份完整协议复制进仓库形成新的长篇治理文档
  - 因发现产品问题顺手修复产品资产
  - 宣布子合同已接受或开放 M1–M4 施工
  - 清理、改写或强推默认分支及其他分支历史；绕过仓库现有保护流程
protected_assets:
  - decision-chain/docs/**  (现有合同与阶段基线)
  - decision-chain/skills/** · content-production/skills/**
  - decision-chain/workflows/** · content-production/workflows/**
  - decision-chain/fixtures/** · content-production/fixtures/**
  - content-production/references/**
  - decision-chain/evidence/** (43) · content-production/evidence/** (14)
  - decision-chain/docs/V1_PRODUCTION_GAP_REGISTER_v0.1.md
  - content-production/docs/CONTENT_PRODUCTION_RUNTIME_CONTRACT_v0.1.md
  - tools/**
  - 笛语项目基线.md
minimum_sufficiency_constraints:
  max_new_files: 6
  max_canonical_lines: 80
  empty_template_forbidden: true
  history_must_stay_in_place: true
acceptance:
  A1: 五类账本全部可定位，实际载体存在且不是空模板
  A2: 真正隔离的新执行单元能独立回答五问并指出当前基线；保留完整原始问答；不得由当前 Agent 角色扮演失忆
  A3: 每个活动 task_id 的下一动作含动作／对象／基线输入／完成信号，且不需要新产品裁决
  A4: 历史资产零内容改动、零重命名、零删除
  A5: 新增文件 ≤6；canonical ≤80 行；无脚本／CI／Schema／数据库／状态机／Judge／模板生成器／第二治理体系
  A6: 对声称支持的每类执行代理，验证其默认入口能找到 canonical 说明；无法验证的不得写入支持声明
  A7: Checkpoint／Final Manifest／Current Handoff 不混用；历史只索引不补造；Gap 不冒充 failed path；副作用状态受控
  A8: 本任务自身被记账（Manifest／Attempt／验收证据／失败路径／commit push 副作用）
  A9: 远程默认工作基线已含 canonical 规则与账本；提供 tested functional hash、closing evidence hash、最终 default ref 与 URL；无 force／amend／reset／无关改动
terminal_state_order: [INVALID, DONE, PARTIAL_DISABLED, BLOCKED, FAILED]
next_stage_default: false
remote_closure_required: true
```

### T-001.2 Run Manifest（v1，首次写入前编译）

> 下面这个 ```yaml 代码块的**块内字节**即 `manifest_hash` 的哈希对象。**块内不含 `manifest_hash` 自身**，因此可无环重算。

```yaml
manifest_version: 1
task_id: COLLAB-LEDGER-BOOTSTRAP-001
compiled_at: "2026-08-24"
task_contract_ref: "collab-ledger/L1_TASK_MANIFESTS.md §T-001.1"
task_contract_hash: d5ee949a9dd61af3a40fbf67bb0f185c04ae05d6f8f6008f2c2e9bfcdc22f380

final_deliverable: "canonical 协作连续性规则 + 五类逻辑账本，已进入远程默认工作基线 main。"
core_problem: "无聊天上下文的新执行会话无法从仓库自行回答连续性五问。"
observable_changes:
  - 仓库存在唯一权威说明，明确五类逻辑账本、唯一落点、更新时机与责任主体
  - canonical 位于目标执行代理默认会读取的位置；其余入口只放极薄指针，不复制规则正文
  - 五类逻辑账本全部可定位（合并为 5 个 Markdown 文件，不要求一类一文件）
  - 项目级 Current Handoff 按 task_id 区分，不用单一全局「下一步」覆盖并行任务
  - Checkpoint／Final Manifest／Current Handoff 三者分离，不混为一物
  - 新 Attempt／失败路径／副作用从本任务钉住的基线起追加；历史只索引不补造
  - 独立新会话可完整回答五问并指出当前基线
  - 规则与账本已进入远程默认工作基线，新会话不依赖候选分支或聊天

truth_sources:
  - decision-chain/docs/V1_DECISION_CHAIN_REBASE_PRODUCT_CONTRACT_v0.1.md   # 上位合同
  - decision-chain/docs/V1_SINGLE_ACCOUNT_SLICE_CONTRACT_v0.1.md            # 子合同（未接受）
  - decision-chain/docs/V1_DECISION_CHAIN_STAGE_BASELINE_v0.2.md            # 当前阶段基线
  - 笛语项目基线.md §〇
  - CLAUDE.md · PROJECT_INDEX.md
  - Git 历史与远端 ref                                                       # 推送事实的原始权威

actual_baseline_verified_at_execution:
  remote: https://github.com/andyan77/diyu-demo.git
  branch_checked_out_before: main
  main_local: 6ae78abf5967535bda81392255b8ee3e79e4bcb5
  main_remote: 6ae78abf5967535bda81392255b8ee3e79e4bcb5
  working_tree: clean
  remote_heads: 8
  worktrees: 5
  decision_evidence_files: 43
  production_evidence_files: 14
  prior_ledger_for_this_task_id: NONE          # 故 task_entry_mode 保持 NEW_TASK
  drift_vs_planning_observation: NONE
accepted_baseline: 6ae78abf5967535bda81392255b8ee3e79e4bcb5

allowed_delta:
  new_files:                                    # 6 个，等于上限
    - collab-ledger/COLLAB_CONTINUITY_PROTOCOL.md
    - collab-ledger/L1_TASK_MANIFESTS.md
    - collab-ledger/L2_TASK_STATE_AND_HANDOFF.md
    - collab-ledger/L3_ATTEMPTS_AND_EVIDENCE.md
    - collab-ledger/L4_FAILED_PATHS.md
    - collab-ledger/L5_SIDE_EFFECTS.md
  modified_files:                               # 仅极薄指针与索引链接，不复制规则正文
    - CLAUDE.md
    - PROJECT_INDEX.md
    - README.md
  everything_else: FORBIDDEN

authorizations:
  read: [仓库全文, Git 历史, remote refs, branches, worktrees, 两个 evidence 目录, Gap Register]
  write: [canonical 规则, 五类账本载体, 极薄入口指针, 本任务 Manifest／Attempt／原始问答／交付证据, 项目索引链接]
  execute: [只读侦察与 Git 核验, 建任务分支, 文档编辑, 本地一致性检查, 隔离新执行单元测试, commit, push 任务分支, 按仓库现有安全流程采用进 main]
  network: [fetch origin, push 任务分支, 正常合并采用, 读远端 ref 验哈希]
  forbidden_ops: [force, amend, reset, 绕过分支保护, 带入无关提交]

acceptance_oracle:
  A1: 从 canonical 出发逐项点开五个落点，文件存在且含真实条目
  A2: 隔离新执行单元读取冻结 commit，无聊天上下文，回答五问 + 当前基线；原始问答留存于 L3
  A3: 逐条检查活动 task_id 的下一动作四要素齐全
  A4: git diff <baseline>..<head> --stat 对受保护路径为空
  A5: 新增文件计数 ≤6；wc -l canonical ≤80；无新增可执行脚本或 Schema
  A6: 对每类声称支持的代理，实证其默认入口可达 canonical；无法实证的不写支持声明
  A7: 逐条对照三类状态语义定义与「历史只索引」「Gap 不升级」「副作用状态受控」
  A8: 本任务在 L1／L3／L5 均有条目
  A9: git ls-remote 核验 main HEAD == 合并提交；提供 tested functional hash 与 closing evidence hash

evidence_reuse_policy:
  default: EXACT_BINDING_ONLY
  final_full_run_required: true
  dynamic_evidence_requires_refresh: true
completion_checks:
  artifact_persisted: REQUIRED
  target_environment_run: REQUIRED
  fixed_configuration_run: NOT_APPLICABLE
  fixed_configuration_run_reason: >-
    纯文档治理任务，交付物不由任何受控模型配置产出，无固定模型配置可钉。
    A2 隔离测试所用执行单元的模型标识仍记录进 L3 以备追溯，但它不是产品模型配置运行。
  positive_tests: REQUIRED
  negative_tests: REQUIRED
  regression_tests: REQUIRED
  raw_evidence_preserved: REQUIRED
  git_closure: REQUIRED
  remote_closure: REQUIRED
retry_policy:
  transient_retry_allowed: true
  maximum_authorized_attempts: RUNTIME_OR_TASK_DEFINED
  blind_resampling_allowed: false
  all_attempts_must_be_preserved: true

remote_target:
  task_branch: chore/collab-ledger-bootstrap-001
  default_working_baseline: main
  adoption_path: "任务分支 → 推远程 → --no-ff 合并 main → 推 main → ls-remote 核验"
  forbidden: [force, amend, reset, squash, 删除来源分支]
next_stage_default: false
continuity_refs:
  L2: collab-ledger/L2_TASK_STATE_AND_HANDOFF.md
  L3: collab-ledger/L3_ATTEMPTS_AND_EVIDENCE.md
  L4: collab-ledger/L4_FAILED_PATHS.md
  L5: collab-ledger/L5_SIDE_EFFECTS.md
```

### T-001.3 哈希登记

| 项 | 值 | 怎么重算 |
|---|---|---|
| `task_contract_hash` | `d5ee949a9dd61af3a40fbf67bb0f185c04ae05d6f8f6008f2c2e9bfcdc22f380` | 取 §T-001.1 那个 ```yaml 代码块的**块内字节**（两行 ``` 围栏本身不算），做 SHA-256 |
| `manifest_hash`（v1） | `35a67aa54052ca34e2de726e4d993b4b79e8287d06f42e6f02668bcd0c5fa870` | 取 §T-001.2 那个 ```yaml 代码块的**块内字节**做 SHA-256。**该值不写进块内本身**，以免自引用成环 |

### T-001.4 本任务的公开缺口

| 缺口 | 处置 |
|---|---|
| 两份治理协议文件在执行环境中不存在（仅有文件名与声明哈希） | 如实标 `governance_conformance: NOT_VERIFIED`，**不猜其内部条款**，改以 Execution Prompt 自带的完整合同语义执行；已报 Founder |
| **入口覆盖缺口**：[笛语项目基线.md](../笛语项目基线.md) 开篇自称「新会话／新窗口进入项目先读这一篇」，但**全文零处**提到本账本。只读它的新会话拿不到账本指路 | 该文件是**受保护资产**（`protected_assets` 列内），本任务 `non_goals` 禁止修改。**不擅自改、不放宽边界**——登记为公开缺口**报 Founder 裁决**是否授权加一行指针。由 A2 第 2 轮对抗性隔离单元查出 |
| **A2 隔离性声明本身不可复核**：L3 中「独立执行单元／只读工具集／不继承对话上下文／不是角色扮演失忆」四句，是执行侧对自己实验装置的自述，**仓库里没有任何东西能证伪它**。而 A2 恰是本账本最核心的验收项 | 如实标注，**不辩解**。是否接受这一层不可复核性，**报 Founder 裁决**。由 A2 第 3 轮对抗性隔离单元查出 |
| **canonical 已卡死 80/80 行**：A5「≤80 行」与 canonical §三「只加不改」在 canonical 上**已经互斥**——再要更正就只能覆盖 | 属**规则设计冲突**，非执行错误。执行侧**不擅自放宽 A5**，登记报 Founder 裁决：放宽行数上限，还是允许 canonical 例外覆盖。由 A2 第 3 轮对抗性隔离单元查出 |
| **「断言门禁」不可从仓库复核**：执行侧用了一个一次性断言脚本做提交前拦截，但 A5 禁止向仓库新增脚本（`git diff --diff-filter=A` 实测新增文件全为 6 个 Markdown、零脚本），该脚本**未入库** | 按 [L4 §一](L4_FAILED_PATHS.md) 自订标准「自述不是证据」，**其输出一律不作为验收证据**。所有验收结论改用[可复算命令](L3_ATTEMPTS_AND_EVIDENCE.md)。由 A2 第 2 轮对抗性隔离单元查出 |

### T-001.5 执行澄清（同一任务内，不新建任务）

Founder 于 2026-08-24 在本任务执行中追加澄清。**它不建立新任务、不重启执行、不改变 P0、授权范围、A1–A9 或 `task_contract_hash`，也不作废已形成的有效证据**——因此 §T-001.1 与 §T-001.2 两个 ```yaml 块**逐字节未动**，两个哈希仍然有效。落实点全部在块外：

| # | 澄清 | 落实位置 | 本次是否需要调整 |
|---|---|---|---|
| 1 | canonical 只承担低频规则与账本定位，不承载高频运行状态 | [canonical §六](COLLAB_CONTINUITY_PROTOCOL.md) 新增一条硬规矩 | 已调整 |
| 2 | Checkpoint／Manifest／Attempt／失败路径／副作用**按 `task_id` 分区**，不得把并行任务堆进一个高频全局文件 | [canonical §一](COLLAB_CONTINUITY_PROTOCOL.md)；[L3 §一](L3_ATTEMPTS_AND_EVIDENCE.md)／[L4 §二](L4_FAILED_PATHS.md)／[L5 §三](L5_SIDE_EFFECTS.md) 各加 `task_id` 索引表与归属行；并行 ≥2 时另建 `collab-ledger/tasks/<task_id>.md` | 已调整 |
| 3 | 账本按 `task_id` 建，不按 Agent／窗口／worktree 建 | [canonical §一](COLLAB_CONTINUITY_PROTOCOL.md) | 原实现即如此，补写成明规则 |
| 4 | 同一 `task_id` 同一时刻只有执行总负责人写其任务账本；子代理只返回证据与引用 | [canonical §三](COLLAB_CONTINUITY_PROTOCOL.md) | 已调整 |
| 5 | 项目级 Current Handoff 只维护活动 `task_id`、依赖关系与定位引用，不设全局「唯一下一步」 | [L2 §二](L2_TASK_STATE_AND_HANDOFF.md) 增 `依赖` / `定位引用` 两列并改写口径 | 已调整 |
| 6 | `新增文件数 ≤6` 只约束本次 bootstrap 交付，不是未来任务记录的永久总量上限 | [canonical §六](COLLAB_CONTINUITY_PROTOCOL.md) | 已调整 |
| 7 | 已满足的不制造额外改动；未满足的在合并前做最小调整，保留已有 Attempt 与证据 | 本表即调整清单；`ATT-001` 与 §二 历史目录**未动** | 遵守 |

---

### T-001.6 Task Contract v2（收口 Delta，`REBASE_TASK`）

> **v1（§T-001.1／§T-001.2）逐字节原样保留，两个哈希继续有效。** 本节只写两份收口 Delta **明确修改**的验收口径，其余条款**继承 v1**。
> 下面这个 ```yaml 代码块的**块内字节**即 `task_contract_hash_v2` 的哈希对象。

```yaml
contract_version: 2
task_id: COLLAB-LEDGER-BOOTSTRAP-001
task_entry_mode: REBASE_TASK
prompt_kind: CLOSEOUT_DELTA
risk_level: LOW
inherits_from:
  contract_v1: "collab-ledger/L1_TASK_MANIFESTS.md §T-001.1"
  contract_v1_hash: d5ee949a9dd61af3a40fbf67bb0f185c04ae05d6f8f6008f2c2e9bfcdc22f380
  manifest_v1: "collab-ledger/L1_TASK_MANIFESTS.md §T-001.2"
  manifest_v1_hash: 35a67aa54052ca34e2de726e4d993b4b79e8287d06f42e6f02668bcd0c5fa870
  unchanged: [P0, 授权范围, 非目标, 受保护资产, 账本语义, 安全边界]
predecessor_prompts:
  - "Execution Prompt — 协作连续性账本立规（修订版）"
  - "Execution Prompt Delta — 协作连续性账本立规收口补充指令"
  - "Execution Prompt Delta — 账本正文过期引用与静态计数清理"
authority_refs:
  - "Founder 2026-08-24 裁决：功能内容冻结，停止追求无边际收益的反复返工，按收口口径完成。"
  - "Founder 2026-08-24 裁决：把过期引用和会随仓库变化失真的静态计数从账本正文中去掉。"

delta_1_closeout:
  goal: "在不继续扩写或重构账本功能的前提下安全收口。"
  only_fix: "确实阻止他人读懂账本、定位任务或定位下一动作的阻断性缺陷。"
  do_not: [重新设计账本结构或规则, 因非阻断性瑕疵开启新一轮返工,
           删除或改写已登记的问题与修复记录, 重做已有证据支持的前三轮验证,
           把本次放宽外推到其他任务]
  reuse_verification: "功能内容未再变化时复用最近一次真实隔离验证及其 functional hash；
                       只有解除真实阻断的功能修改才对受影响路径做一次定向复验。"
  acceptance:
    C1: 功能内容保持冻结——除解除真实阻断所需的最小修复外无扩张
    C2: 历史证据完整——问题、修复记录、Attempt、失败路径、原始证据均可定位，零删改
    C3: 独立接续仍成立——最近一次真实隔离验证已证明可读懂状态并定位下一动作；最终采用内容与被测 functional hash 等价
    C4: 已知问题显式登记——表现、引用、影响、可接受理由齐全
    C5: 默认基线采用完成——远程默认分支已含成果，本地与远端 Hash 可核验，过程安全可追溯
    C6: 收口记录最小充分——只写通过项、已知问题、引用、采用状态与终局
  non_blocking_rule: "非阻断性问题不再使 C3 失败。C3 判断的是能否正确接续，不是措辞、版式或记录密度是否完美。"

delta_2_cleanup:
  goal: "current-facing 账本正文不得继续承载已过期引用与会漂移的静态计数。"
  remove: [已被替代仍冒充当前的引用, 不可解析的路径分支提交或证据定位,
           已失效的下一步动作或状态, evidence/文件/分支/任务/问题的静态总数,
           需人工同步的「当前共有 N 项」类汇总]
  keep: [原始问题与修复记录, Formal Attempt, 失败路径, 外部副作用历史,
         原始 evidence 与 Git 历史, 精确绑定历史运行的 Commit/版本/对象标识,
         当前有效且可解析的 Contract/Manifest/Handoff/证据入口,
         各活动任务的下一可执行动作, 远程默认工作基线的可核验引用]
  history_rule: "历史记录中的数量若是某次运行在当时的原始事实，不得回写篡改；
                 只需避免把该历史数量复制进 current-facing 正文。"
  forbidden_substitutes: [计数脚本, CI, 自动索引器, 数据库, Schema 校验器, 状态机, 第二套账本]
  unverifiable_rule: "引用是否仍有效无法核验时不得猜测：从 current-facing 正文移除该当前性主张，
                      历史来源原样保留，并在收口记录中标 NOT_VERIFIED。"
  acceptance:
    R1: 过期引用清除
    R2: 漂移计数清除
    R3: 当前接续能力保留
    R4: 历史完整性不受损——零删除零篡改
    R5: 无过度工程
    R6: 默认基线收口——本地与远端最终 Hash 可核验

terminal_rule:
  forbidden: [PARTIAL, "用 CONTINUE 延迟已可完成的收口", "因最后一轮非阻断问题重启完整返工"]
  on_pass: |
    COLLAB_LEDGER_BOOTSTRAP_001 = DONE
    activation_status = ACTIVE_ON_DEFAULT_BASELINE
    next_stage_allowed = true:V1-REBASE-EP00-CURRENT
scope_boundary: "仅适用于 COLLAB-LEDGER-BOOTSTRAP-001 本次收口。不修改执行协议 v1.2 与规划协议 v1.1，
                 不构成项目级验收降级，不适用于 V1-REBASE-EP00-CURRENT / SINGLE-ACCOUNT-SLICE-EP00 / M1–M5
                 及任何 Skill、工作流、生产链或智能保真验收。"
```

| 项 | 值 | 怎么重算 |
|---|---|---|
| `task_contract_hash_v2` | `54a2e635e641a7134b28c7955397471c091294e0ffe0ba283ecb56c88df407d3` | 取 §T-001.6 那个 ```yaml 代码块的**块内字节**做 SHA-256（本表在块外，不影响该值） |
