# L1 · 合同与 Manifest 定位

> 规则正文见 [COLLAB_CONTINUITY_PROTOCOL.md](COLLAB_CONTINUITY_PROTOCOL.md)。
> 本文件按 `task_id` 定位：**稳定 Task Contract、当前 Manifest、授权依据、起算基线、允许改动范围、受保护资产、终态引用**。
> **只放定位，不复制合同正文。** 追加式：只加不改，更正另起一条。

## 定位表

| task_id | Task Contract | 当前 Manifest | 授权依据 | 终态 |
|---|---|---|---|---|
| `COLLAB-LEDGER-BOOTSTRAP-001` | **v2（当前）§T-001.6** ／ v1（历史）§T-001.1 | v1 §T-001.2（v2 只写收口 Delta 口径，其余继承 v1） | Founder 2026-08-24 明确授权 ＋ 两份收口 Delta | 见 [L2](L2_TASK_STATE_AND_HANDOFF.md) 与 [L3 §CLOSEOUT](L3_ATTEMPTS_AND_EVIDENCE.md) |
| `V1-REBASE-EP00-CURRENT` | §T-002.1（当前） | §T-002.2 | 上位合同 `PRODUCT_CONTRACT_ACCEPTED — REPO_PREFLIGHT_AUTHORIZED` ＋ Founder 2026-08-24 M0 Execution Prompt（审查修订版，含 A16 新增项） | 见 [L2](L2_TASK_STATE_AND_HANDOFF.md) 与 [L3](L3_ATTEMPTS_AND_EVIDENCE.md) |
| `M0-EP00-ADOPTION-CLOSEOUT-001` | §T-003.1（当前） | §T-003.2 | Founder 2026-08-24 M0 · EP-00 采用、当前状态纠偏与默认基线收口 Execution Prompt | 见 [L2](L2_TASK_STATE_AND_HANDOFF.md) 与 [L3](L3_ATTEMPTS_AND_EVIDENCE.md) |
| `V1-M0-1B-SLICE-CONTRACT-REVISION-001` | v2（当前）§T-004.3 ／ v1（历史）§T-004.1 | §T-004.2（v2 只写 Delta，其余继承 v1） | Founder 2026-08-24《M0.1B 下位单账号合同定向修订》Execution Prompt（F-01～F-09）＋ 后续四项定向纠偏与 F-10 Delta ＋ Founder 2026-08-24 明确接受（§T-004.4） | `DONE`。已采用进 `main`，见 [L2](L2_TASK_STATE_AND_HANDOFF.md) 与 [L3](L3_ATTEMPTS_AND_EVIDENCE.md) |
| `SINGLE-ACCOUNT-SLICE-EP00` | [单账号纵向切片子合同 v0.2](../decision-chain/docs/V1_SINGLE_ACCOUNT_SLICE_CONTRACT_v0.2.md) | 不适用（本行不是独立任务，是切片专项预检的授权登记） | 下位合同 v0.2 `ACCEPTED — SINGLE_ACCOUNT_SLICE_PREFLIGHT_AUTHORIZED`（Founder 2026-08-24 接受，见 §T-004.4） | `DONE`。交付见 §T-005（[`V1_SINGLE_ACCOUNT_SLICE_EP00_PREFLIGHT_v0.1.md`](../decision-chain/docs/V1_SINGLE_ACCOUNT_SLICE_EP00_PREFLIGHT_v0.1.md)） |
| `V1-M0-SLICE-PREFLIGHT-AND-SHARED-CONTRACT-CLOSEOUT-001` | §T-005.1（当前） | §T-005.2 | Founder 2026-08-24《M0.2B 专项预检、M0.3 共享合同与 M0 收口》完整 Execution Prompt ＋ Founder 2026-08-25 明确接受（§T-005.4） | `DONE`。已采用进 `main`，见 [L2](L2_TASK_STATE_AND_HANDOFF.md) 与 [L3](L3_ATTEMPTS_AND_EVIDENCE.md) |
| `V1-M1-M4-PHASE0-PREAMBLE-ADOPTION-AND-DESKTOP-PACK-001` | §T-006.1（当前） | §T-006.2～T-006.3 | 规划侧 2026-08-25《M1–M4 Phase 0 共享编译前言采用与桌面资料包》Execution Prompt ＋ Founder 2026-08-25 提供真实附件文件后解除阻塞（§T-006.3） | P0-A `DONE`（首次尝试 `BLOCKED`，见 §T-006.2；附件补齐后 §T-006.3 解除并完成）；P0-B 与 main 采用见 [L2](L2_TASK_STATE_AND_HANDOFF.md) 与 [L3](L3_ATTEMPTS_AND_EVIDENCE.md) |
| `V1-M1-M4-PHASE0-DECISION-STATE-CLOSEOUT-001` | §T-007.1（当前） | §T-007.2 | Founder 2026-08-25《M1–M4 Phase 0 决策状态一致性收口》Execution Prompt ＋ Founder 2026-08-25 通过 AskUserQuestion 当场确认（非 Prompt 自称历史） | `DONE`。已采用进 `main`，见 [L2](L2_TASK_STATE_AND_HANDOFF.md) 与 [L3](L3_ATTEMPTS_AND_EVIDENCE.md) |
| `V1-M1-ENGINEERING-PROMPT-ADOPTION-001` | §T-008.1（当前） | §T-008.2 | 规划侧 2026-08-25《Execution Prompt — M1 自然语言交互与任务上下文编译 v1.2》＋ Founder 2026-08-25「执行落盘」，范围经执行侧澄清未获工程执行明确授权，本任务只落盘文档本身 | `DONE`。文档已采用进 `main`；**M1 工程执行（`task_id: DIYU-V1-M1-NATURAL-CONTEXT-001`）未开工、未授权**，见 [L2](L2_TASK_STATE_AND_HANDOFF.md) 与 [L3](L3_ATTEMPTS_AND_EVIDENCE.md) |
| `V1-COLLAB-PROTOCOL-PROMPT-AUTHORIZATION-RULE-001` | §T-009.1（当前） | §T-009.2 | Founder 2026-08-25 当场裁决「铁律：后续只要注入执行prompt，即视为授权，不再重复」 | `DONE`。已采用进 `main`，见 [L2](L2_TASK_STATE_AND_HANDOFF.md) 与 [L3](L3_ATTEMPTS_AND_EVIDENCE.md) |
| `DIYU-V1-M2-BUSINESS-PERSISTENCE-VERSION-FEEDBACK-001` | [M2 施工 Execution Prompt v1.1 §3](../decision-chain/docs/M2_ENGINEERING_EXECUTION_PROMPT_v1.1.md)（本行不复制合同正文，Task Contract 内嵌于该 Prompt 自身；文档自证 `task_contract_hash` 与实际内容不一致，已由 Founder 裁决改用独立复算值 `4d14eb35c065b650b0380b0c309e0e08ec32e3aa608ece4d62e8d27b97450830` 登记，见 [L1 §T-010.2 DA-02](L1_TASK_MANIFESTS.md)） | 不适用（本任务的 Manifest 状态写进 [L2 §一](L2_TASK_STATE_AND_HANDOFF.md) 当前投影，不另建 L1 §T-0xx 分区——本行只作起点登记） | `V1-COLLAB-PROTOCOL-PROMPT-AUTHORIZATION-RULE-001` 生效后 Founder 就该具体 task_id 当场明确答复「就是要启动，铁律适用」（见 [L2 §一.14](L2_TASK_STATE_AND_HANDOFF.md)）；该 Prompt 自身 `allowed_delta`／`protected_assets`／`remote_target` 等边界照常有效 | `IN_PROGRESS`。独立 worktree `/home/faye/diyu-demo-worktrees/m2-business-persistence-version-feedback-v1`，任务分支 `task/m2-business-persistence-version-feedback-v1`，起算基线 `main @ ba80d63e180d13d8e88b5a3b5e5f1660ffc6ec5d` |

> **上位合同被接受 ≠ 子合同被接受 ≠ 授权 Skill／DSL／持久化／工作流施工。**（本条规则继续有效；`SINGLE-ACCOUNT-SLICE-EP00` 这一行是该规则下**已经解除**的具体实例，不代表规则本身改变）
> 执行侧**不得**自行宣布任何合同「已接受」，也**不得**自行把状态往上推一级——`V1-M0-1B-SLICE-CONTRACT-REVISION-001` 行的 `ACCEPTED` 状态由 Founder 本人在执行过程中明确回答后推进，非执行侧自行判定。

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

---

## §T-002 · `V1-REBASE-EP00-CURRENT`

### T-002.1 Task Contract（稳定合同）

> 下面这个 ```yaml 代码块的**块内字节**即 `task_contract_hash` 的哈希对象。**不含**聊天摘要、侦察计划与当前进度。

```yaml
task_id: V1-REBASE-EP00-CURRENT
task_entry_mode: NEW_TASK
parent_task_id: ""
task_type: RESEARCH_REVIEW
risk_level: LOW
next_stage_default: false
remote_closure_required: true
authority_refs:
  - "V1_DECISION_CHAIN_REBASE_PRODUCT_CONTRACT_v0.1.md：PRODUCT_CONTRACT_ACCEPTED — REPO_PREFLIGHT_AUTHORIZED"
  - "V1_DECISION_CHAIN_STAGE_BASELINE_v0.2.md：当前允许开展 V1-REBASE-EP00-CURRENT，只读预检不构成施工授权"
  - "Founder 于 2026-08-24 下发《M0 当前真相预检（Founder 审查修订版）》Execution Prompt，含 A16（六 Skill 源文件—工作流提示词—模型约束一致性）新增验收项"
  - "L2 §一.2／§二：本任务此前状态为「已授权，可立即开工」「未开工」，此次为该任务的首次正式执行"
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
    两份治理协议以文件名与 SHA-256 被引用，本次执行环境（仓库全历史、当前文件系统）
    穷尽检索均未命中，不允许复制进仓库。对两份协议条款的符合性无法核验，标 NOT_VERIFIED；
    与 COLLAB-LEDGER-BOOTSTRAP-001（T-001.1）同一处置先例一致。实际执行依据是本
    Execution Prompt 自身写明的完整 Task Contract 语义。
core_problem: >-
  上位产品合同已授权对 V1 决策链改造仓库做一次只读、证据绑定、可复核的当前真相预检，
  但此前从未真正开工（L2 §一.2：状态=未开工）。需要以远程 main、真实 Dify 已发布／草稿
  状态和当前部署为对象，逐项核验八项能力、六份 Skill 价值耦合、六份 Skill 源文件—工作流
  提示词—模型约束一致性（A16，Founder 本轮新增）、路由与生产链接缝、仓库—Dify—部署一致性、
  持久化现状，产出一份供 Founder 裁决的 current-state preflight report。
final_deliverable: >-
  一份 current-state preflight report（含八项能力现状卡、六 Skill 价值耦合表、六 Skill
  源文件↔工作流提示词↔模型约束一致性表、CURRENT/STALE/NOT_VERIFIED/MISSING/CONFLICT
  标注、A1—A10 与 A14—A16 验收矩阵结果），连同本任务 Manifest、Attempt 与证据索引，
  已推送至任务分支并核验本地/远端 Hash 一致。
p0_acceptance:
  A1: "当前基线可信——remote/branch/HEAD/worktree/工作区/未推送状态的原始输出，报告基线与之相同"
  A2: "权威与授权不混淆——上位/子合同/阶段基线/三类 EP-00 原文引用；未把子合同或历史预检当当前授权"
  A3_NON_PRUNABLE: "目标环境（真实 Dify）已被真实只读核验——稳定标识/查询时间/原始响应，非仓库推断"
  A4: "路由与任务上下文完成实证映射——当前实现/输入输出/运行证据/缺口逐项绑定"
  A5_NON_PRUNABLE: "八项能力全覆盖——八张 current-state 卡片齐全，无能力被静默合并/冒充/遗漏"
  A6_NON_PRUNABLE: "六份 Skill 价值耦合完成分档——每份结论有具体规则/Prompt/Reference 证据"
  A7_NON_PRUNABLE: "创意锦标赛（CS-1）与 Content Brief 接缝已查清——调用位置/候选出口/外部比较/直接入口"
  A8_NON_PRUNABLE: "生产链当前能力已查清——CS/PD/PP、Stage1/2、PRE/MIXED/FINAL、Returns、语义核验、用户交付、恢复机制"
  A9_NON_PRUNABLE: "仓库—Dify—部署一致性结论可信——对相同对象做结构/Hash/版本比较，漂移原样登记不修复"
  A10: "持久化基础已查清——业务真源/Dify状态/权限/版本/反馈/写回/幂等/恢复逐项标 CURRENT/MISSING/NOT_VERIFIED"
  A14: "受保护资产零变化——除允许的报告/治理 Delta 外，产品资产、运行资产、目标系统均无写入"
  A15: "远程收口——任务分支已推送，本地/远端 Hash 一致，不直推/不合并 main，不建 PR"
  A16: "六份 Skill 源文件—工作流提示词—模型约束一致性已逐份核验——版本配对/正文差异清单/模型约束证据/能力影响结论；无充分依据处标 NOT_VERIFIED，不得凭配置数字推断"
p1:
  enabled: false
  reason: "本任务无预定义阶段性交付，不得使用 PARTIAL。"
non_goals:
  - 修改产品合同、阶段基线、Skill、Reference、fixture、DSL、Workflow、Prompt、Tool 绑定、Dify 应用、模型参数、Checker、业务数据库、部署配置或 tools/
  - 执行任何付费模型生成、内容生产、业务工作流、Dify 发布、重绑或数据写入
  - 开展 SINGLE-ACCOUNT-SLICE-EP00，或把未接受子合同的新增验收当作当前 P0
  - 冻结起始资料合同、业务数据合同、Dify 集成合同或四个共享合同
  - 设计或实施 M1—M4
  - 新建第二套路由、第二套创意锦标赛、第二套生产链、数据库平台、RAG、知识库、插件平台、Judge 网络或重型依赖图
  - 用历史 AO-EP00-HISTORICAL、旧 evidence、自述状态或静态文件存在替代当前核验
  - 为得到整洁结论而修复漂移、删改失败证据或把 MISSING 改写成"规划中"
  - 改动其他分支、worktree 或用户未提交内容
  - 直推或合并 main、创建或合并 PR
protected_assets:
  - decision-chain/docs/** · content-production/docs/**（现有合同与阶段基线）
  - decision-chain/skills/** · content-production/skills/**
  - decision-chain/workflows/** · content-production/workflows/**
  - decision-chain/fixtures/** · content-production/fixtures/**
  - content-production/references/**
  - decision-chain/evidence/** · content-production/evidence/**
  - tools/**
  - 笛语项目基线.md
  - 真实 Dify 应用/工作流/Tool 绑定/模型参数/数据库/部署配置（只读核验，零写入）
  - 其他分支、worktree、用户未提交内容
allowed_writes:
  - 一份新的 current-state preflight report
  - 本任务 Manifest、Attempt、原始检查证据、最终交付（collab-ledger/**、本任务分支下的报告文件）
  - 已采用协作账本中本任务的增量条目（L1—L5，追加式）
  - 为定位本报告所必需的最小项目索引链接（PROJECT_INDEX.md／README.md／CLAUDE.md 的指针性追加）
acceptance_note: >-
  A11—A13（四份共享合同 readiness map／M1—M4 缺口图与成熟度重估／报告级"无孤儿结论"）
  已由 Founder 从本任务验收矩阵移除，交由预检后规划工作处理，不构成本任务 P0。
terminal_state_order: [INVALID, DONE, PARTIAL_UNAVAILABLE, BLOCKED, FAILED]
next_stage_default: false
remote_closure_required: true
```

| 项 | 值 |
|---|---|
| `task_contract_hash` | `0a176145f7e7ed5b99f2fb09c583800c81a8829ca5cba227571d51d0f32b1210` |

### T-002.2 Run Manifest（首次写入前编译）

> 下面这个 ```yaml 代码块的**块内字节**即 `manifest_hash` 的哈希对象。**块内不含 `manifest_hash` 自身**，因此可无环重算。

```yaml
manifest_version: 1
task_id: V1-REBASE-EP00-CURRENT
compiled_at: "2026-08-24"
task_contract_ref: "collab-ledger/L1_TASK_MANIFESTS.md §T-002.1"
task_contract_hash: 0a176145f7e7ed5b99f2fb09c583800c81a8829ca5cba227571d51d0f32b1210

final_deliverable: "current-state preflight report + A1—A10/A14—A16 验收矩阵，已推送任务分支。"
core_problem: "上位合同已授权的只读预检此前从未开工（L2 §一.2 状态=未开工）；需要以真实远程仓库与真实 Dify 为对象逐项核验。"

truth_sources:
  - decision-chain/docs/V1_DECISION_CHAIN_REBASE_PRODUCT_CONTRACT_v0.1.md   # 上位合同
  - decision-chain/docs/V1_SINGLE_ACCOUNT_SLICE_CONTRACT_v0.1.md            # 子合同（未接受）
  - decision-chain/docs/V1_DECISION_CHAIN_STAGE_BASELINE_v0.2.md            # 当前阶段基线
  - PROJECT_INDEX.md · 笛语项目基线.md §〇 · CLAUDE.md
  - Git 历史与远端 ref                                                       # 推送事实的原始权威
  - 真实本机 Dify 1.16.1 Docker 部署（docker-db_postgres-1 只读 psql）        # 目标环境原始权威

actual_baseline_verified_at_execution:
  remote: https://github.com/andyan77/diyu-demo.git
  branch_checked_out_before: main
  main_local: 4d84cd2a4bbd9bcbcff97105f226cf5652f13e29
  main_remote: 4d84cd2a4bbd9bcbcff97105f226cf5652f13e29
  working_tree_before_this_task: clean
  remote_heads: 9
  local_branches: 11
  worktrees: 5
  ledger_header_baseline_6ae78ab_vs_live_main: >-
    L2 §二 与 canonical §七 记的「main @ 6ae78ab」是账本起算基线（固定锚点，不追踪 HEAD），
    非当前 HEAD 过期；6ae78ab 是 4d84cd2 的祖先，二者之间 8 个 commit 经 diff --stat 核验
    只动 collab-ledger/**、CLAUDE.md、PROJECT_INDEX.md、README.md（COLLAB-LEDGER-BOOTSTRAP-001
    自身收口），无产品语义漂移。本任务实际执行基线钉为 main @ 4d84cd2（当前 HEAD）。
  execution_prompt_observed_main_6ae78ab_vs_live: >-
    规划侧 Prompt 第 3 节「当前观察」记录 observed main = 6ae78ab，同样是 4d84cd2 的祖先，
    差异同上，判定为规划侧观察相对当前 HEAD 的良性滞后（STALE_BENIGN），不视为 CONFLICT。
  dify_target_identified: >-
    本机 Docker 运行真实 Dify 1.16.1 全栈（17 容器，2 天在线，健康）；主 Chatflow App
    id=310ddfcf-e0fb-4211-af98-3d101725e07a，name="DIYU Demo V1 Main Chatflow v0.1"（Dify
    应用名未随内容更新，见下）。仓库共列出的 MCP 工具 dify-platform-expert／
    dify-workflow-1/2/3 均非本项目真实通道（前者自报 "demonstration data"，后者名称与
    本项目工作流不匹配）；真实核验改走 docker exec docker-db_postgres-1 psql 只读查询
    apps／workflows 表（沙箱默认禁网络与 docker socket，需按证据触发 dangerouslyDisableSandbox
    执行只读命令，不写不改）。
  main_chatflow_spot_check: >-
    App 310ddfcf 当前 draft graph 与已发布 workflow_id=055b7bbe 的 graph 字节长度相同
    （249047），节点数均为 56，与 PROJECT_INDEX 声称一致。经节点标题唯一性比对，实际内容
    对应仓库 decision-chain/workflows/DIYU_DEMO_V1_FULL_CHAIN_CHATFLOW_v0.2.yml（v0.2），
    而非同目录 DIYU_DEMO_V1_MAIN_CHATFLOW_v0.1.yml（v0.1）——Dify 应用显示名称仍为
    "v0.1" 是命名未同步，非内容漂移。其余 ~20 个 App 的核验见任务证据（本 Manifest
    编译时尚未逐一走完，属首次写入前的部分核验，允许在 Attempt 中继续补齐）。
  prior_ledger_for_this_task_id: NONE_EXCEPT_L1_L2_LOCATOR_ROWS
  drift_vs_planning_observation: BENIGN_ONLY

accepted_baseline: 4d84cd2a4bbd9bcbcff97105f226cf5652f13e29

allowed_delta:
  new_files:
    - task/v1-rebase-ep00-current-m0-preflight 分支下的 preflight report（路径待定，写入时登记）
  modified_files:
    - collab-ledger/L1_TASK_MANIFESTS.md   # 本 Manifest
    - collab-ledger/L2_TASK_STATE_AND_HANDOFF.md
    - collab-ledger/L3_ATTEMPTS_AND_EVIDENCE.md
    - collab-ledger/L5_SIDE_EFFECTS.md     # 记 commit/push 副作用
    - PROJECT_INDEX.md／README.md（可能的最小指针追加，非必须）
  everything_else: FORBIDDEN

authorizations:
  read: [仓库全文, Git 历史, remote refs/branches/worktrees, 真实本机 Dify（只读 API/DB）, tools/**]
  write: [preflight report, 本任务 Manifest／Attempt／证据／交付, L1—L5 追加式增量, 最小索引指针]
  execute: [只读侦察, 建任务分支（已建）, docker exec 只读 psql（需 sandbox 例外）, commit, push 任务分支]
  network: [fetch origin, push 任务分支, 读远端 ref 验哈希, 本机 Dify 只读 API/DB（非公网）]
  forbidden_ops: [force, amend, reset, 绕过分支保护, Dify/DB 任何写操作, 直推或合并 main, 建 PR]

acceptance_oracle:
  A1: git status/branch/log/worktree 原始输出与报告基线一致
  A2: 上位/子合同/阶段基线原文引用逐条核对，未越权代裁
  A3: docker exec psql 对真实 Dify apps/workflows 表的原始查询结果，含时间戳与稳定 ID
  A4: A-0—A-4 运行证据文件逐项引用 + 当前路由实现文件定位
  A5: 八张能力卡逐项绑定仓库文件/Dify App/evidence
  A6: 六 Skill 全文分档，规则/Prompt 行号引用
  A7: CS-1 与 Content Brief 接缝的 workflow 节点级证据
  A8: CS/PD/PP 与两段式生产链的 workflow/evidence 交叉核验
  A9: 仓库 DSL 与 Dify 实际 graph 的结构/节点数/Tool 绑定版本比较
  A10: 业务持久化（DB/Dify 会话状态）只读枚举
  A14: git diff 与 Dify DB 只读查询确认零写入（除 allowed_delta）
  A15: git ls-remote 核对任务分支远端 HEAD 与本地一致
  A16: 六 Skill 源文件与工作流内嵌正文逐份文本比对 + 节点模型参数只读查询
```

| 项 | 值 |
|---|---|
| `manifest_hash` | `f3972b67ca746c228a7827602f51f5df7a644b40a447acea8d2bab76d44446d8` |

---

## §T-003 · `M0-EP00-ADOPTION-CLOSEOUT-001`

### T-003.1 Task Contract（稳定合同）

> 下面这个 ```yaml 代码块的**块内字节**即 `task_contract_hash` 的哈希对象。**不含**聊天摘要与执行计划。

```yaml
task_id: M0-EP00-ADOPTION-CLOSEOUT-001
task_entry_mode: NEW_TASK
parent_task_id: V1-REBASE-EP00-CURRENT
task_type: MIXED
risk_level: MEDIUM
next_stage_default: false
remote_closure_required: true
remote_target: origin/main
authority_refs:
  - "Founder 已确认 COLLAB-LEDGER-BOOTSTRAP-001 与 V1-REBASE-EP00-CURRENT 均已形成正式 DONE；要求先完成剩余 M0 收口，再处理后续入口门。"
  - "Founder 2026-08-24 下发《M0 · EP-00 采用、当前状态纠偏与默认基线收口》Execution Prompt。"
  - "Founder 裁决：历史运行、失败路径和外部副作用留痕只追加；L2 当前状态与总规则页属于当前投影，可以直接替换，旧值由 Git 历史保存。"
  - "Founder 裁决：当前态正文不得保留自然过期的轮次、数量或位置式引用；完成任务必须移出 Current Handoff。"
  - "Founder 裁决：两份规划／执行治理协议不属于项目仓库，本任务不得把其正文写入仓库。"
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
    与 T-001／T-002 同一处置先例：两份协议仅有文件名与声明哈希，穷尽检索本仓库与执行机
    均未命中，不允许复制进仓库（Prompt authority_refs 第 5 条明确禁止）。对其内部条款的
    符合性无法核验，标 NOT_VERIFIED；实际执行依据是 Execution Prompt 自身写明的完整合同语义。
core_problem: >-
  COLLAB-LEDGER-BOOTSTRAP-001 与 V1-REBASE-EP00-CURRENT 均已在各自任务分支上终结 DONE，
  但 EP-00 的完整交付（报告 + 账本证据）尚未进入远程默认分支 main；同时 L2 当前状态页
  仍存在若干过期投影（已终结任务残留在 Current Handoff、Checkpoint 文字与终态状态矛盾、
  账本起算锚点被误读为当前 HEAD 等），新会话可能被误导为两个已完成任务仍需执行。
final_deliverable: >-
  远程 main 同时包含完整、祖先关系不变的 EP-00 交付，以及经纠偏的 L2 当前投影
  （无矛盾终态、Current Handoff 清空并显式声明、下一权限动作按稳定路径引用），
  连同本任务自身的 Manifest／Attempt／副作用记录。
p0_acceptance:
  C_ADOPT: "EP-00 已交付 tip 被默认分支完整接收，来源分支保留，报告与证据在 main 可读"
  C_RULE: "canonical 正确区分历史留痕（只加不改）与当前投影（可直接替换），未新增治理系统"
  C_L2_STATE: "bootstrap 与 EP00 各只有一个无矛盾的当前 DONE，均无 Checkpoint"
  C_L2_HANDOFF: "Current Handoff 不再包含两个已完成任务；明写无已授权执行任务；Founder 审阅报告表述为下一权限动作"
  C_STABLE_REF: "当前态无自然过期计数、轮次、位置式指针；历史证据原文不在清理范围"
  C_HISTORY: "EP-00 与 bootstrap 的历史证据、失败记录、外部副作用及来源提交未被篡改"
  C_SCOPE: "未触碰任何未授权产品或运行资产；变更面仅限来源分支五文件 Delta ＋ canonical／L2 纠偏 ＋ 本任务最小账本收口"
  C_REMOTE: "远程默认基线真实收口——本地 main 与 git ls-remote origin refs/heads/main 一致"
  C_CONTINUITY: "无聊天上下文的新执行会话能正确回答两个任务状态、当前是否有已授权执行任务、下一权限动作、M1—M4 是否获授权，且与最终 L2／报告一致"
p1:
  enabled: false
  permitted_next_stage: NONE
non_goals:
  - 修改 EP-00 报告的事实结论、八项能力卡、六份 Skill 比对、11 项 Founder 待裁决命题或任何原始证据
  - 重跑 EP-00、扩展预检范围或补做 readiness map、M1–M4 缺口图
  - 替 Founder 回答报告中的产品命题
  - 接受、修改或升级下位单账号纵向切片合同；启动 SINGLE-ACCOUNT-SLICE-EP00
  - 起草、写入或冻结四个共享合同；生成或启动 M1–M4 施工
  - 修改 Skill、DSL、Dify、Runtime、数据库、业务持久化、生产链或目标系统
  - 更新四窗口共同规划 v0.3
  - 把《执行 Prompt 生成总则》或《受边界约束的执行总负责人协议》写入项目仓库
  - 新建脚本、CI、Schema、状态机、数据库、Judge、Reviewer 网络或第二套账本
  - 为了让状态页"看起来完整"补造未发生的任务、授权、Checkpoint 或下一阶段权限
  - 删除来源分支、改写远端历史、force push、reset、amend、rebase／squash 已交付的来源提交
protected_assets:
  - decision-chain/docs/**（现有合同与阶段基线；含 EP-00 报告本身，事实结论不可改）
  - decision-chain/skills/** · content-production/skills/**
  - decision-chain/workflows/** · content-production/workflows/**
  - decision-chain/fixtures/** · content-production/fixtures/**
  - content-production/references/**
  - decision-chain/evidence/** · content-production/evidence/**
  - tools/**
  - 笛语项目基线.md
  - L1／L3／L4／L5 中已有的历史条目正文（只可追加，不可覆盖）
  - EP-00 来源分支 task/v1-rebase-ep00-current-m0-preflight 及其提交历史
  - 其他分支、worktree、用户未提交内容
allowed_writes:
  - 为采用 EP-00 交付所需的正常 Git 集成提交（merge，非 squash／rebase）
  - collab-ledger/COLLAB_CONTINUITY_PROTOCOL.md 中与历史／当前投影边界直接相关的最小规则修正
  - collab-ledger/L2_TASK_STATE_AND_HANDOFF.md 的当前状态与 Current Handoff 重写
  - L1／L3／L5 为本任务追加的最小充分记录（身份、验收、远程副作用）
  - 因本次采用出现实际断链时的最小定位链接修复
terminal_state_order: [INVALID, DONE, BLOCKED, FAILED]
```

| 项 | 值 |
|---|---|
| `task_contract_hash` | `57f3eb37325ecf30367e8079ebce1a9c308dfe27edbfd3c4cfc9e2ba82a4603d` |

### T-003.2 Run Manifest（首次写入前编译）

> 下面这个 ```yaml 代码块的**块内字节**即 `manifest_hash` 的哈希对象。**块内不含 `manifest_hash` 自身**，因此可无环重算。

```yaml
manifest_version: 1
task_id: M0-EP00-ADOPTION-CLOSEOUT-001
compiled_at: "2026-08-24"
task_contract_ref: "collab-ledger/L1_TASK_MANIFESTS.md §T-003.1"
task_contract_hash: 57f3eb37325ecf30367e8079ebce1a9c308dfe27edbfd3c4cfc9e2ba82a4603d

final_deliverable: "远程 main 完整接收 EP-00 交付且祖先关系不变；L2 当前投影纠偏；本任务自身记账完成。"
core_problem: "EP-00 已 DONE 但证据未进入默认 main；L2 当前投影存在过期/矛盾表述，可能误导无上下文新会话。"

truth_sources:
  - collab-ledger/COLLAB_CONTINUITY_PROTOCOL.md
  - collab-ledger/L1_TASK_MANIFESTS.md §T-001／§T-002
  - collab-ledger/L2_TASK_STATE_AND_HANDOFF.md（本任务执行前版本）
  - collab-ledger/L3_ATTEMPTS_AND_EVIDENCE.md §四 ATT-001（EP-00 唯一正式尝试）
  - collab-ledger/L5_SIDE_EFFECTS.md SE-001／SE-002／SE-003
  - decision-chain/docs/V1_REBASE_EP00_CURRENT_PREFLIGHT_v0.1.md
  - Git 历史与远端 ref                                       # 推送事实的原始权威

actual_baseline_verified_at_execution:
  remote: https://github.com/andyan77/diyu-demo.git
  branch_checked_out_before: task/v1-rebase-ep00-current-m0-preflight
  main_local_before: 4d84cd2a4bbd9bcbcff97105f226cf5652f13e29
  main_remote_before: 4d84cd2a4bbd9bcbcff97105f226cf5652f13e29
  ep00_source_branch: task/v1-rebase-ep00-current-m0-preflight
  ep00_source_tip: 48c8275e8aa576be7c037303348de0dfb5677641
  ancestry_check: "git merge-base --is-ancestor main origin/task/v1-rebase-ep00-current-m0-preflight → true"
  commits_ahead_behind: "main...task 分支 = 0 behind, 3 ahead"
  file_delta_vs_main: >-
    5 files changed, 888 insertions(+), 7 deletions(-)：L1/L2/L3/L5 四本账 + 新增 preflight
    report；与规划观察完全一致，无未披露改动
  working_tree_before_this_task: clean
  branch_protection_on_main: >-
    gh api repos/andyan77/diyu-demo/branches/main/protection → 404 Branch not protected
    （可用普通 push／merge 采用，无需 PR）
  planning_observation_vs_live: >-
    规划侧记录的 main=4d84cd2、task tip=48c8275、ahead-3-behind-0、5 文件 Delta
    与执行时实测完全一致，无漂移
  prior_ledger_for_this_task_id: NONE
  drift_vs_planning_observation: NONE

accepted_baseline: 4d84cd2a4bbd9bcbcff97105f226cf5652f13e29

integration_path:
  strategy: >-
    本地新建集成分支 chore/m0-ep00-adoption-closeout-001（源自 main）→ --no-ff 合并来源
    分支 tip（保留祖先关系，零冲突）→ 在集成分支上做 canonical／L2 当前投影纠偏 ＋
    本任务 L1/L3/L5 记账 → 一次无上下文接续检查 → 整体 --no-ff 合并进本地 main →
    推送 main → 核验远端 ref
  forbidden_ops_confirmed_not_used: [force, amend, reset, squash, rebase, 删除来源分支]

allowed_delta:
  modified_files:
    - collab-ledger/COLLAB_CONTINUITY_PROTOCOL.md
    - collab-ledger/L1_TASK_MANIFESTS.md
    - collab-ledger/L2_TASK_STATE_AND_HANDOFF.md
    - collab-ledger/L3_ATTEMPTS_AND_EVIDENCE.md
    - collab-ledger/L5_SIDE_EFFECTS.md
  everything_else: FORBIDDEN

authorizations:
  read: [远程仓库/分支/Commit/PR/保护规则/工作树, collab-ledger/** 全部, EP-00 任务分支与其报告/证据, 上位合同/阶段基线/子合同状态/项目索引, Prompt 随附两份外部治理协议的引用（不读正文，正文不在仓库）]
  write: [正常 Git 集成提交, canonical 最小规则修正, L2 当前状态重写, L1/L3/L5 本任务最小追加记录, 必要时的最小定位链接修复]
  execute: [Git/GitHub 只读核验与比较, 创建集成分支, commit, push, 按仓库保护策略采用进 origin/main, 一次无上下文接续检查]
  network: [fetch origin, push 集成结果, 读远端 ref 验哈希]
  forbidden_ops: [force, amend, reset, squash, rebase, 删除来源分支, 建 PR（main 无分支保护，直接 merge+push 即可满足 remote_target）]

acceptance_oracle:
  C_ADOPT: "git merge-base --is-ancestor 与 git log 核验来源 tip 是最终 main 祖先；报告与证据文件在 main 工作树可读；git ls-remote 确认来源分支仍存在"
  C_RULE: "读 canonical 最终正文，确认新增内容仅为历史/当前投影边界一节；diff 确认未新增治理机制"
  C_L2_STATE: "读 L2 §一，确认 bootstrap 与 EP00 各一份无矛盾 DONE 记录，Checkpoint 字段与终态一致"
  C_L2_HANDOFF: "读 L2 §二，确认活动任务表为空、显式声明 NONE、下一权限动作按稳定路径引用"
  C_STABLE_REF: "grep 当前投影正文，确认无「共几项」「第几轮」类表述残留（历史证据正文除外）"
  C_HISTORY: "diff 来源分支与采用后对应文件的 EP00 历史内容段落，确认逐字节未改；L1 两个既有哈希块保持不变"
  C_SCOPE: "git diff --stat 核对变更文件清单仅为预期范围"
  C_REMOTE: "git ls-remote origin refs/heads/main 与本地 git rev-parse main 一致"
  C_CONTINUITY: "派发一个无本会话上下文的只读代理，仅给仓库读权限，核对其回答与最终 L2/报告一致"
```

| 项 | 值 |
|---|---|
| `manifest_hash` | `e7aaff03a5d01156c046a417a5acbb20926d13dab2019daec41c686a0bdc1d9c` |

---

## §T-004 · `V1-M0-1B-SLICE-CONTRACT-REVISION-001`

### T-004.1 Task Contract（稳定合同）

> 下面这个 ```yaml 代码块的**块内字节**即 `task_contract_hash` 的哈希对象。**不含**聊天摘要与执行计划。

```yaml
task_id: V1-M0-1B-SLICE-CONTRACT-REVISION-001
task_entry_mode: NEW_TASK
parent_task_id: ""
task_type: RESEARCH_REVIEW
risk_level: MEDIUM
next_stage_default: false
remote_closure_required: true
remote_target: "独立任务分支 task/v1-m0-1b-slice-contract-revision-001，不得直接写入或合并 main"
authority_refs:
  - "Founder 2026-08-24 下发《M0.1B 下位单账号合同定向修订》Execution Prompt（主体 + 补丁两段合一，Founder 已明确：补丁即 F-08/F-09 与 F-05/F-06/F-07 的完整化，须与主体合并为单一最新版执行，不构成第二个独立任务）。"
  - "Founder 2026-08-24 对单账号合同核心产品命题 F-01～F-09 的明确裁决。"
  - "Founder 2026-08-24 补充确认：起算基线 main @ f94d7a7；M0.1B 可以启动；不得因此推进 M1—M4。"
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
    与 T-001/T-002/T-003 同一处置先例：两份协议仅有文件名与声明哈希，本仓库与执行机均未
    命中，且本 Prompt 明确禁止将其正文写入仓库。实际执行依据是 Execution Prompt 自身写明的
    完整合同语义（主体 + 补丁合一后的版本）。
core_problem: >-
  下位单账号纵向切片合同 v0.1 处于 CONTRACT_REVISION_REQUIRED，其中若干表述（独立顾客问题硬
  准入门、Campaign 编译模式与正式身份混淆、CTA 与平台范围缺失、真实发布与工程验收混淆、项目
  治理角色可能渗入产品运行逻辑、用户调整请求处理不完整）需要 Founder 已裁决的 F-01～F-09 定向
  修订，形成一份可供 Founder 审阅的后继候选版本。
final_deliverable: >-
  decision-chain/docs/V1_SINGLE_ACCOUNT_SLICE_CONTRACT_v0.2.md（候选，v0.1 逐字未动），
  状态字符串沿用 CONTRACT_REVISION_REQUIRED（不由执行侧自行推高），已推送至独立任务分支。
p0_acceptance:
  M01B_C01: "启动基线来自前序任务收口后的最新远程 main"
  M01B_C02: "v0.1 原文件逐字保持不变（Blob Hash 核验）"
  M01B_C03: "F-01、F-02、F-03 完整写入候选合同"
  M01B_C04: "Campaign 身份完整符合 F-04"
  M01B_C05: "CTA 边界完整符合 F-05，未包装成三级体系"
  M01B_C06: "平台支持、动态选台、视频号锁定完整符合 F-06"
  M01B_C07: "真实发布不阻塞 M0—M5；工程与真实运营验证分级命名且全文档一致"
  M01B_C08: "父子合同关系明确；本轮改变之处均登记为切片增量"
  M01B_C09: "候选状态仅供审阅，不自行推高治理状态字符串，不开放专项预检或施工"
  M01B_C10: "没有发生非目标改动"
  M01B_C11: "候选合同已推送到独立远程任务分支，本地与远端 Hash 一致"
  M01B_C12: "F-08 项目治理角色与产品运行角色分离完整落地"
  M01B_C13: "F-09 用户调整请求必须产生实际调整完整落地"
p1:
  enabled: false
non_goals:
  - 修改或覆盖 v0.1 历史合同
  - 修改上位产品合同
  - 把候选合同标记为 ACCEPTED，或自行推高其治理状态字符串
  - 修改 README、CLAUDE、项目基线和正式索引中的当前合同指针
  - 更新四窗口共同母规划
  - 执行或重写 SINGLE-ACCOUNT-SLICE-EP00
  - 起草或冻结四个共享合同
  - 修改 Matrix、Campaign、Content Brief、Creative Script、Production Director 或 Publishing & Packaging
  - 修改任何 DSL、Dify 应用、模型参数或运行配置
  - 创建数据库、Schema、API、状态机或路由
  - 实现平台 OAuth、自动发布或效果采集
  - 开始 M1、M2、M3、M4 或 M5
  - 创建 PR、合并 main
  - 清理其他分支、worktree 或历史文件
  - 新建第二份规划、审查或治理体系
  - 修复 EP-00 发现的工程问题（Skill 参数漂移、仓库与线上漂移、孤儿 Dify App、Content Brief 唯一上游锁定等）
protected_assets:
  - decision-chain/docs/V1_SINGLE_ACCOUNT_SLICE_CONTRACT_v0.1.md（逐字不得改动）
  - decision-chain/docs/V1_DECISION_CHAIN_REBASE_PRODUCT_CONTRACT_v0.1.md（上位合同）
  - decision-chain/skills/** · content-production/skills/**
  - decision-chain/workflows/** · content-production/workflows/**
  - decision-chain/fixtures/** · content-production/fixtures/**
  - content-production/references/**
  - decision-chain/evidence/** · content-production/evidence/**
  - tools/**
  - 笛语项目基线.md
  - collab-ledger/** 既有历史条目正文（只可追加）
  - main 分支（本任务不得写入或合并）
allowed_writes:
  - decision-chain/docs/V1_SINGLE_ACCOUNT_SLICE_CONTRACT_v0.2.md（新建）
  - 本任务 Manifest、Attempt、证据、交付（collab-ledger/**，追加式）
terminal_state_order: [INVALID, DONE, BLOCKED, FAILED]
```

| 项 | 值 |
|---|---|
| `task_contract_hash` | `d025bfec81e060b45066d8f767e41749487bee62890e4dab7fea56a90f670bd2` |

### T-004.2 Run Manifest（首次写入前编译）

> 下面这个 ```yaml 代码块的**块内字节**即 `manifest_hash` 的哈希对象。**块内不含 `manifest_hash` 自身**，因此可无环重算。

```yaml
manifest_version: 1
task_id: V1-M0-1B-SLICE-CONTRACT-REVISION-001
compiled_at: "2026-08-24"
task_contract_ref: "collab-ledger/L1_TASK_MANIFESTS.md §T-004.1"
task_contract_hash: d025bfec81e060b45066d8f767e41749487bee62890e4dab7fea56a90f670bd2

final_deliverable: "V1_SINGLE_ACCOUNT_SLICE_CONTRACT_v0.2.md 候选，F-01～F-09 全部落地，已推送独立任务分支。"
core_problem: "下位合同 v0.1 需要 Founder 已裁决的 F-01～F-09 定向修订，形成后继候选供审阅。"

truth_sources:
  - decision-chain/docs/V1_SINGLE_ACCOUNT_SLICE_CONTRACT_v0.1.md
  - decision-chain/docs/V1_DECISION_CHAIN_REBASE_PRODUCT_CONTRACT_v0.1.md
  - decision-chain/docs/V1_REBASE_EP00_CURRENT_PREFLIGHT_v0.1.md
  - collab-ledger/L2_TASK_STATE_AND_HANDOFF.md（本任务执行前版本）
  - Git 历史与远端 ref

actual_baseline_verified_at_execution:
  remote: https://github.com/andyan77/diyu-demo.git
  branch_checked_out_before: main
  main_local: f94d7a754a46c64f4b3e2f4e48cc4c3faa5b319a
  main_remote: f94d7a754a46c64f4b3e2f4e48cc4c3faa5b319a
  matches_prompt_observation: true
  existing_v0_2: NONE_FOUND_AT_START
  other_branches_touching_contract_file: >-
    仅一个历史提交 b89f78b（已在 main 上），无并行任务正在修改同一文件
  working_tree_before_this_task: clean
  v0_1_blob_hash_at_start: faf4e012c8c9d7c8f689dffcc181fdd05c8ab25c
  prior_ledger_for_this_task_id: NONE
  drift_vs_planning_observation: NONE

accepted_baseline: f94d7a754a46c64f4b3e2f4e48cc4c3faa5b319a

review_process:
  round_1: >-
    执行侧完成 v0.1→v0.2 全部 F-01～F-09 定向修订后，派发 1 个 general-purpose 子代理执行
    一次定向语义审查，仅检查 §8「有界审查与停止规则」列明的阻断类问题，明确排除排版/措辞/
    顺手修复等非阻断意见。
  round_1_findings: >-
    3 处阻断发现：① F-03 在 §1.3 顶层链路遗漏（"单账号诊断"含混未清除，且登记表误标"已合规"）；
    ② F-07 的 ENGINEERING/REAL 两级命名与 §8.2 既有三层验收框架未显式对齐；③ 候选合同自行把
    治理状态字符串推高到 READY_FOR_FOUNDER_ACCEPTANCE，构成执行侧自行推高状态（超出 F-01～F-09
    授权范围的擅自变更）。
  round_1_disposition: >-
    3 处全部确认为真实缺陷，按"只修复其明确破坏的验收项及直接连带范围"原则修复：
    §1.3 改写 + §11.1 登记表更正（对应①）；§8.2 增补对齐段（对应②）；文档头部与 §10.3
    状态字符串回退为 CONTRACT_REVISION_REQUIRED，§11 同步更正（对应③）。未发现的一条非阻断
    问题（F-04 登记表"四条边界"应为"五条"）顺带更正。
  round_2: NOT_TRIGGERED
  round_2_reason: >-
    修复后仅对受影响范围做定向复验（grep 确认三处修复点、v0.1 blob hash 未变、状态字符串
    全文档一致），未重新开放全文审查，符合 Prompt §9 的验证预算与强制停止规则。

allowed_delta:
  new_files:
    - decision-chain/docs/V1_SINGLE_ACCOUNT_SLICE_CONTRACT_v0.2.md
  modified_files:
    - collab-ledger/L1_TASK_MANIFESTS.md
    - collab-ledger/L3_ATTEMPTS_AND_EVIDENCE.md
    - collab-ledger/L5_SIDE_EFFECTS.md
  everything_else: FORBIDDEN

authorizations:
  read: [仓库全文, Git 历史, remote refs, 上位/下位合同, EP-00 报告]
  write: [v0.2 候选合同文件, 本任务 Manifest／Attempt／证据, L1/L3/L5 追加式增量]
  execute: [只读侦察, 建独立任务分支, 定向语义审查子代理, commit, push 任务分支]
  network: [fetch origin, push 任务分支, 读远端 ref 验哈希]
  forbidden_ops: [force, amend, reset, 直推或合并 main, 建 PR, 修改 v0.1, 修改上位合同]

acceptance_oracle:
  M01B_C01: "git rev-parse main 与 origin/main 一致，且等于启动时观测值"
  M01B_C02: "git hash-object v0.1 前后一致；git status 确认 v0.1 未被 git add/modify"
  M01B_C03: "定向语义审查子代理逐条核对 F-01/F-02/F-03 落点，含 F-03 修复后复核"
  M01B_C04: "§5.5.1 五条边界逐条核对；子代理确认无遗漏"
  M01B_C05: "§5.9.1 逐条核对；子代理确认未包装为三级体系"
  M01B_C06: "§1.6 逐条核对；子代理确认视频号锁定表述准确、动态选台条款完整"
  M01B_C07: "§8.1/§8.2 逐条核对；子代理发现衔接缺口后已修复并复验"
  M01B_C08: "§0.5 增量登记表 + §11.1 映射表逐条核对"
  M01B_C09: "文档头部/§10.3/§11.3 状态字符串三处交叉核对，确认沿用 CONTRACT_REVISION_REQUIRED"
  M01B_C10: "diff -u v0.1 v0.2 的 13 个 hunk 逐一核对，均可映射到某个 F 项或其修复"
  M01B_C11: "git ls-remote 与本地 git rev-parse 核对任务分支"
  M01B_C12: "§5.10.2 逐条核对；子代理确认未发现 Founder 审核类角色渗入产品运行逻辑"
  M01B_C13: "§5.10.1 逐条核对；子代理确认未发现拒绝调整类反模式"
```

| 项 | 值 |
|---|---|
| `manifest_hash` | `dadc922d0fe5e998f6d3d2c5e54f9bef4a16fe57a1e9b839ec9cd8e64eadb540` |

---

### T-004.3 Task Contract v2（Founder 复核纠偏 ＋ F-10 Delta，`REBASE_TASK`）

> **v1（§T-004.1／§T-004.2）逐字节原样保留，两个哈希继续有效**——本节只写 Founder 本轮
> 追加的四项定向纠偏与新增命题 F-10 明确修改／新增的验收口径，其余条款**继承 v1**。
> 下面这个 ```yaml 代码块的**块内字节**即 `task_contract_hash_v2` 的哈希对象。

```yaml
contract_version: 2
task_id: V1-M0-1B-SLICE-CONTRACT-REVISION-001
task_entry_mode: REBASE_TASK
prompt_kind: CORRECTION_AND_EXTENSION_DELTA
risk_level: MEDIUM
inherits_from:
  contract_v1: "collab-ledger/L1_TASK_MANIFESTS.md §T-004.1"
  contract_v1_hash: d025bfec81e060b45066d8f767e41749487bee62890e4dab7fea56a90f670bd2
  manifest_v1: "collab-ledger/L1_TASK_MANIFESTS.md §T-004.2"
  manifest_v1_hash: dadc922d0fe5e998f6d3d2c5e54f9bef4a16fe57a1e9b839ec9cd8e64eadb540
  unchanged: [task_id, 独立任务分支不合并主干的边界, protected_assets, v0.1 逐字不得改动, terminal_state_order]
predecessor_prompts:
  - "补充执行指令 — 恢复并完成 Prompt A manifest v2"
  - "Execution Delta — M0.1B Manifest v3 / F-10 产品裁决补丁"
authority_refs:
  - "Founder 2026-08-24：本轮四项定向纠偏（视频号冻结表述取消／上位合同绑定与三类 EP-00 状态／真实与模拟发布记录分离／反馈闭环二选一）在同一任务内完成，不新开任务。"
  - "Founder 2026-08-24：新增产品命题 F-10（目标忠实、适用专业价值保留与证据等级），在同一任务同一 attempt 内与四项纠偏一并处理。"

delta_scope:
  four_fixes: [取消视频号冻结表述, 修正上位合同绑定与三类EP-00状态, 分离真实发布实例与模拟测试发布记录, 反馈闭环统一为有依据调整或有依据保持不变]
  new_proposition: "F-10：目标忠实、适用专业价值保留与证据等级"
  do_not: [把F-10扩张为新Skill, 把F-10扩张为新工作流, 把F-10扩张为新评测平台, 把F-10扩张为第五份共享合同,
           重做manifest_v1已完成的F-01至F-09落地, 回滚或重做manifest_v1无关事项]
  acceptance:
    M01B3_C13: "下位合同已明确目标忠实＋适用专业价值保留，且不存在固定调用六份 Skill 的含义"
    M01B3_C14: "适用专业能力被限制为任务相关、下游必要、允许等价输入满足，不构成全能硬门"
    M01B3_C15: "非关键专业建议不会阻塞整个任务，事实、权限、合规和真实下游必要输入门禁未被削弱"
    M01B3_C16: "专业价值、工程闭环、真实运营闭环和经营提升四类结论已分离，普通运营观察不会被写成因果提升"
    M01B3_C17: "F-10没有引入新 Skill、新链路、第五份共享合同、评测平台或范围外实现要求"
  completion_condition: "M01B_C01～C13（v1，全部通过） 与 M01B3_C13～C17（本 delta）全部通过，方可视为本轮完成"

founder_acceptance_gate:
  mechanism: "定向自验通过后，在当前执行过程中弹出一次授权提示（AskUserQuestion 或等价机制），不新开任务、不判定 BLOCKED、不结束当前执行"
  on_accept: |
    SINGLE_ACCOUNT_VERTICAL_SLICE_PRODUCT_CONTRACT = ACCEPTED
    M0_REMAINING_CLOSEOUT = AUTHORIZED — NOT_STARTED
  successor_task_change:
    superseded: "V1-SINGLE-ACCOUNT-SLICE-EP00-001（不再作为自动后继任务单独执行）"
    new_successor: "V1-M0-SLICE-PREFLIGHT-AND-SHARED-CONTRACT-CLOSEOUT-001（统一承接 M0.2B 切片专项预检 → M0.3 四个共享合同 → Founder 阶段接受 → M0 收口；不得自动进入 M1–M4）"

terminal_rule:
  forbidden: [PARTIAL, 未获Founder明确接受即写ACCEPTED, 自行推高治理状态字符串]
  on_pass: |
    V1-M0-1B-SLICE-CONTRACT-REVISION-001 = DONE
    next_stage_allowed = true:V1-M0-SLICE-PREFLIGHT-AND-SHARED-CONTRACT-CLOSEOUT-001（仅当 founder_acceptance_gate 已触发 on_accept 时生效）
scope_boundary: "仅适用于本任务本轮 Delta；不构成项目级验收降级；不自动授权 M1–M5。"
```

| 项 | 值 | 怎么重算 |
|---|---|---|
| `task_contract_hash_v2` | `27d65007d297d9d8649cefabfee08fc4e5f1efaac62fda64c9daf387b87c0bc3` | 取本节 ```yaml 代码块的**块内字节**做 SHA-256（本表在块外，不影响该值） |

### T-004.4 Founder 接受记录（块外追加，不改动上方 `task_contract_hash_v2` 覆盖的字节）

| 项 | 值 |
|---|---|
| 触发方式 | 执行过程中的授权提示（`AskUserQuestion`），非离线审查——对应 §T-004.3 `founder_acceptance_gate.mechanism` |
| 提问内容 | "四项定向纠偏与 F-10 已完成并通过定向审查修复，未发现范围外产品语义变化。是否接受 V1_SINGLE_ACCOUNT_SLICE_CONTRACT_v0.2.md，授权采用进远程 main？" |
| Founder 回答 | **"接受，采用进 main"**（2026-08-24） |
| 触发的状态变化 | `SINGLE_ACCOUNT_VERTICAL_SLICE_PRODUCT_CONTRACT = ACCEPTED — SINGLE_ACCOUNT_SLICE_PREFLIGHT_AUTHORIZED`；`M0_REMAINING_CLOSEOUT = AUTHORIZED — NOT_STARTED` |
| 后继任务变更登记 | 原 `V1-SINGLE-ACCOUNT-SLICE-EP00-001`（含其完整 Execution Prompt）不再单独执行；新后继 `V1-M0-SLICE-PREFLIGHT-AND-SHARED-CONTRACT-CLOSEOUT-001` 仅有名称与一句话范围（见 §T-004.3 `successor_task_change`），**尚无完整 Execution Prompt，不得据此自行开工** |
| 未被本次接受触发 | 不触发 M1—M4／M5；不触发四个共享合同冻结；不触发 `SINGLE-ACCOUNT-SLICE-EP00` 自动开工（其自身仍需满足 v0.2 §10.1／§10.2 的实施顺序与授权登记） |

---

## §T-005 · `V1-M0-SLICE-PREFLIGHT-AND-SHARED-CONTRACT-CLOSEOUT-001`

### T-005.1 Task Contract（稳定合同）

> 下面这个 ```yaml 代码块的**块内字节**即 `task_contract_hash` 的哈希对象。**不含**聊天摘要与执行计划。

```yaml
task_id: V1-M0-SLICE-PREFLIGHT-AND-SHARED-CONTRACT-CLOSEOUT-001
task_entry_mode: NEW_TASK
parent_task_id: V1-M0-1B-SLICE-CONTRACT-REVISION-001
task_type: MIXED
risk_level: MEDIUM
authority_refs:
  - "Founder 2026-08-24：完整 Execution Prompt《M0.2B 专项预检、M0.3 共享合同与 M0 收口》，统一承接 SINGLE-ACCOUNT-SLICE-EP00 专项预检 → M0.3 四个共享合同 → Founder 阶段接受 → M0 收口，见 collab-ledger/L1_TASK_MANIFESTS.md §T-004.3 successor_task_change 与 §T-004.4"
  - "Founder 2026-08-24：追加要求——若在 Phase C 等待 Founder 裁决期间会话可能中断，须先按账本规则持久化一份收工日志再交接；恢复后从 Phase C 继续，不重跑 Phase A、Phase B。"
core_problem: >-
  下位合同 v0.2 已被接受，但单账号持续运营切片仍缺专项事实预检与可供 M1—M4 施工引用的
  四份最小共享合同；本任务把两者与 Founder 阶段裁决、M0 远程收口合并为一个连续任务完成。
phases: [PhaseA_special_readonly_preflight, PhaseB_four_shared_contracts, PhaseC_consistency_check_and_founder_gate, PhaseD_m0_remote_closeout]

activation_gate_verified_at_execution:
  V1_SINGLE_ACCOUNT_SLICE_CONTRACT_v0.2_status: "ACCEPTED — SINGLE_ACCOUNT_SLICE_PREFLIGHT_AUTHORIZED，已采用进 main（commit b305e1e/0eba71a）"
  V1_SINGLE_ACCOUNT_SLICE_CONTRACT_v0.1_blob_hash: faf4e012c8c9d7c8f689dffcc181fdd05c8ab25c
  V1_REBASE_EP00_CURRENT_PREFLIGHT_v0.1_status: "已采用进 main（commit 2dc4b59，M0-EP00-ADOPTION-CLOSEOUT-001）"
  V1-REBASE-EP00-CURRENT_status: "DONE"
  SINGLE-ACCOUNT-SLICE-EP00_status: "AUTHORIZED — NOT_STARTED（本任务 Phase A 即其交付）"
  main_local: 0eba71a85916d4d993313c015dc8ad87f180d4de
  main_remote: 0eba71a85916d4d993313c015dc8ad87f180d4de
  working_tree_before_this_task: clean
  m1_m4_branches_or_files: NONE_FOUND
  verdict: ALL_CONDITIONS_MET_NOT_BLOCKED

allowed_delta:
  new_files:
    - decision-chain/docs/V1_SINGLE_ACCOUNT_SLICE_EP00_PREFLIGHT_v0.1.md
    - "Phase B：四个共享合同候选文件（路径待 Phase B 起草时登记）"
  modified_files:
    - collab-ledger/L1_TASK_MANIFESTS.md
    - collab-ledger/L2_TASK_STATE_AND_HANDOFF.md
    - collab-ledger/L3_ATTEMPTS_AND_EVIDENCE.md
    - collab-ledger/L5_SIDE_EFFECTS.md
  everything_else: FORBIDDEN

protected_assets: [已接受的上位与下位产品合同正文, 历史v0.1合同, 已采用的通用EP-00报告正文, 全部Skill源文件,
  全部工作流DSL模型参数或Dify发布版本, 数据库结构和业务数据, ECS对象存储身份权限配置, 历史运行证据和失败路径,
  已发布内容或真实平台状态, 外部两份规划执行协议]

authorizations:
  read: [仓库全文, Git历史, remote refs, 上位/下位合同, 两类EP-00报告, 六份Skill及附件, 工作流DSL, Dify真实只读状态,
         现有路由/创意锦标赛/生产链, 后端数据库身份权限存储恢复基础, 账本和既有运行证据]
  write: [专项EP-00报告, 四个共享合同候选, 必要的M0状态索引和账本Delta, 原始核验证据和最小Git元数据]
  execute: [只读侦察, 建独立任务分支, 定向语义审查子代理, commit, push任务分支]
  network: [fetch origin, push任务分支, 读远端ref验哈希, docker exec只读psql]
  forbidden_ops: [force, amend, reset, 直推或合并main, 建PR, 修改v0.1或上位合同, 建M1-M4任何工程实现,
                  自行宣布共享合同已接受, 自行推高治理状态字符串]

phase_c_interruption_protocol:
  rule: "Phase C 提交 Founder 裁决问题后若等待期间会话可能中断，须先持久化收工日志（当前 Phase 产出、待裁决问题原文、下一步续跑点）到 L1/L2/L3，再交接；恢复会话须从 Phase C 继续，不得重跑 Phase A/Phase B。"
  reason: "Founder 2026-08-24 明确要求：等待裁决期间任务保持 IN_PROGRESS、不判 BLOCKED、不出虚假终态，但必须留下可续跑的收工记录，防止会话中断后下一会话读账本看到「进行中但无续跑点」的断裂状态。"

terminal_rule:
  forbidden: [PARTIAL, 未获Founder明确裁决即写ACCEPTED或AUTHORIZED, 自行推高治理状态字符串, 自行启动M1-M4施工]
  on_activation_gate_fail: [BLOCKED, FAILED, INVALID]
scope_boundary: "只做只读预检、四个共享合同起草、一次定向一致性检查、Founder阶段裁决与M0收口；不做M1-M4任何工程实现；不建第五份共享合同。"
```

| 项 | 值 | 怎么重算 |
|---|---|---|
| `task_contract_hash` | `8b5a48885e27969c404ef86068ec2358bcceda85675247b6bb196eb700a57ac9` | `re.finditer(r'```yaml\n(.*?)\n```', content, re.DOTALL)` 取本节匹配块，UTF-8 编码后 SHA-256 |

### T-005.2 当前 Manifest（Phase A 收口，持续更新）

| 项 | 值 |
|---|---|
| Phase A 交付 | [`V1_SINGLE_ACCOUNT_SLICE_EP00_PREFLIGHT_v0.1.md`](../decision-chain/docs/V1_SINGLE_ACCOUNT_SLICE_EP00_PREFLIGHT_v0.1.md) |
| Phase A 状态 | **`DONE`** —— 定向语义审查（general-purpose 子代理，检查项：引用准确性/内部一致性/范围边界/复用有效性声明/F-10风险分析可靠性）查出 11 处真实问题（含 1 处实质性分析缺陷：风险 C 结论遗漏 Matrix 整任务硬停这一已存在的过度阻塞实例），已全部修复；按验证预算未触发第二轮全文审查，只做修复点自检（grep 确认残留问题短语清零） |
| Phase A 报告 blob hash（冻结值，供 Phase B 引用） | `8134ce00645dd86cea6cc7b6d8d6933f762c68a5` |
| Phase B 交付 | 四份共享合同（已修复）：[任务上下文快照](../decision-chain/docs/V1_M0_SHARED_CONTRACT_TASK_CONTEXT_SNAPSHOT_v0.1.md)（`e92100fb66c56b335ca54ceecd260abef984b4a3`）、[八项能力合同](../decision-chain/docs/V1_M0_SHARED_CONTRACT_EIGHT_CAPABILITIES_v0.1.md)（`ce96a5ff18743d648f50e53cc8e79ab0207c66f2`）、[版本发布反馈归属](../decision-chain/docs/V1_M0_SHARED_CONTRACT_VERSION_PUBLISH_FEEDBACK_v0.1.md)（`b8adc95284f0310657de0a3505d685b90130748c`）、[写回权限幂等恢复](../decision-chain/docs/V1_M0_SHARED_CONTRACT_WRITE_PERMISSION_RECOVERY_v0.1.md)（`c39b69a661d5fb5e2abb20f8b6d2bf998ec65e2e`） |
| Phase B 状态 | **`DONE`** —— 一次定向一致性检查（检查项 A-G）查出 8 处问题（含 1 处严重：§8.7 门禁清单被静默删除；2 处双重真源；2 处孤儿 M1-M4 要求；1 处运营效果护栏缺失；2 处引用/裁决主体错误）全部修复；按验证预算未触发第二轮 |
| Phase C 状态 | **`DONE`** —— 定向一致性检查随 Phase B 一并完成（见 [L3 §七 ATT-002](L3_ATTEMPTS_AND_EVIDENCE.md)）；Founder 阶段裁决已获得（见 §T-005.4） |
| Phase D | **`DONE`** —— 四份共享合同状态更正为 `ACCEPTED`、根索引文件（CLAUDE.md／README.md／PROJECT_INDEX.md／笛语项目基线.md）同步、账本更新、采用进 `main`（远程收口结果见 [L5 SE-008](L5_SIDE_EFFECTS.md)） |
| 任务终态 | `DONE`，见 [L2 §一.7](L2_TASK_STATE_AND_HANDOFF.md) |
| 四份共享合同 blob hash（状态更正后，最终值） | 任务上下文快照 `222008fc99f23b3764d28a2537f4160b58ef48be`；八项能力合同 `6f66a95e847f1a28f8acb4495203019c8b64536f`；版本发布反馈归属 `59fc076044c6930bc66441f2131a039b6d21b79c`；写回权限幂等恢复 `c9a6633ccb5268dfa4e65a60185571b8a0db4df3` |

### T-005.4 Founder 接受记录（块外追加，不改动上方 `task_contract_hash` 覆盖的字节）

| 项 | 值 |
|---|---|
| 触发方式 | Phase C 执行过程中的授权提示（`AskUserQuestion`），非离线审查 |
| 提问内容 | "四个共享合同候选已经基于两类 EP-00 证据完成，并通过定向一致性检查。请选择：A. 接受四个共享合同，并授权后续规划侧编译和启动 M1–M4 施工；B. 接受四个共享合同，但暂不授权 M1–M4 施工；C. 不接受，并指出需要修改的具体产品语义。" |
| Founder 回答 | **"A. 接受，授权 M1–M4 施工规划"**（2026-08-25） |
| 触发的状态变化 | 四份共享合同 = `ACCEPTED`；`M1-M4_PLANNING_PROMPT_COMPILATION = AUTHORIZED`；`M1-M4_ENGINEERING_EXECUTION = AUTHORIZED_BY_FOUNDER`（但本任务**仍不得**自行启动 M1–M4，须由规划侧基于本轮证据和已接受共享合同分别编译四份 Execution Prompt） |
| 未被本次接受触发 | 不触发 M1—M4 工程实现本身；不触发任何 Skill／DSL／Dify 工作流／数据库改动；不构成执行侧自行推高状态——状态推进由 Founder 本人回答触发 |

---

## §T-006 · `V1-M1-M4-PHASE0-PREAMBLE-ADOPTION-AND-DESKTOP-PACK-001`

### T-006.1 Task Contract（稳定合同）

> 下面这个 ```yaml 代码块的**块内字节**即 `task_contract_hash` 的哈希对象。**不含**聊天摘要与执行计划。

```yaml
task_id: V1-M1-M4-PHASE0-PREAMBLE-ADOPTION-AND-DESKTOP-PACK-001
task_entry_mode: NEW_TASK
parent_task_id: V1-M0-SLICE-PREFLIGHT-AND-SHARED-CONTRACT-CLOSEOUT-001
task_type: MIXED
risk_level: MEDIUM
authority_refs:
  - "Founder 2026-08-25 当前会话消息：完整 Execution Prompt《M1–M4 Phase 0 共享编译前言采用与桌面资料包》，随文给出规划侧成稿《笛语 V1 · M1–M4 施工 Execution Prompt 共享编译前言 v0.1》正文与冻结 SHA-256 = 9b046e9b6b8008d66e7347fcc878d2eed13cf251c3a899ed3ea989f761774da6。"
core_problem: >-
  共享合同二尚未实例化八项能力的四类业务合同值与 Matrix 局部降级口径；规划侧已产出唯一 Phase 0
  编译前言成稿，本任务负责验证其与已接受真源一致后原样采用进 main，纠正 L2 当前投影里的两处
  错误（工程授权状态、M1-M4 模块职责映射），并从最终 main 生成四窗口桌面资料包。
phases: [P0A_preamble_verification_and_adoption, P0B_desktop_pack]

activation_gate_verified_at_execution:
  main_local: cba3a30054acfc703464d62266b4c68ec4b55d66
  main_remote: cba3a30054acfc703464d62266b4c68ec4b55d66
  working_tree_before_this_task: clean
  planning_observed_origin_main: cba3a30054acfc703464d62266b4c68ec4b55d66
  drift_from_planning_observed_point: NONE
  four_shared_contracts_and_ep00s_present: "全部 6 份冻结真源文件核验存在，blob hash 已记录于 T-006.2"
  target_preamble_file_present_before_task: false（符合预期，本任务负责新增）
  verdict: ALL_CONDITIONS_MET_NOT_BLOCKED_AT_ACTIVATION

attachment_verification:
  declared_sha256: "9b046e9b6b8008d66e7347fcc878d2eed13cf251c3a899ed3ea989f761774da6"
  received_form: "Execution Prompt 消息正文内联的纯文本转写（无 markdown 语法：无 # 标题、无 ** 加粗、无 | 表格、无 ``` yaml 代码围栏），与本仓库全部已采用真源文档（含四份共享合同）的实际字节格式（标准 markdown：#/##标题、>引用块、**加粗、|表格）结构性不同"
  cross_check_method: "对比 decision-chain/docs/V1_M0_SHARED_CONTRACT_EIGHT_CAPABILITIES_v0.1.md 等已采用真源的原始字节（cat -A 逐字节查看），确认本仓库合同文档惯例是标准 markdown 语法，而收到的前言正文完全不含此类符号"
  conclusion: "收到的前言正文是聊天渲染后的转写文本，不是附件原始字节；无法据此计算出等于冻结值的 SHA-256；不得自行补全或猜测 markdown 语法后再计算哈希（= 自行重建附件，Prompt §2 明文禁止）"
  verdict: ATTACHMENT_UNVERIFIABLE_TREATED_AS_MISSING

allowed_delta:
  modified_files:
    - collab-ledger/L1_TASK_MANIFESTS.md
    - collab-ledger/L2_TASK_STATE_AND_HANDOFF.md
    - collab-ledger/L3_ATTEMPTS_AND_EVIDENCE.md
  blocked_deliverables:
    - decision-chain/docs/V1_M1_M4_CONSTRUCTION_PROMPT_SHARED_PREAMBLE_v0.1.md（P0-A 核心交付，因附件不可校验未写入）
    - "桌面四窗口资料包（P0-B，因源 commit 依赖 P0-A 未完成而未执行）"
  everything_else: FORBIDDEN

protected_assets: [四份 V1_M0_SHARED_CONTRACT_*_v0.1.md, 上位产品合同, 下位合同v0.1与v0.2, 两份EP-00报告,
  decision-chain/skills, decision-chain/workflows, content-production/skills, content-production/workflows, tools,
  全部用户未提交改动和其他worktree, 桌面已有文件或目录]

terminal_rule:
  forbidden: [PARTIAL, 自行重建或猜测附件字节, 自行推断/编写前言正文, 自行推高治理状态字符串]
  on_activation_gate_fail: [BLOCKED, FAILED, INVALID]
scope_boundary: "只做附件校验、L2两处独立纠偏、账本登记；附件不可校验时不写入前言文件、不生成桌面包；不编译M1-M4施工Prompt；不做任何工程实现。"
```

| 项 | 值 | 怎么重算 |
|---|---|---|
| `task_contract_hash` | `883c3a0bba0cec3e82ef46bdf29f82ebbb1dd865f898ccdace568e6cf7450709` | `re.finditer(r'```yaml\n(.*?)\n```', content, re.DOTALL)` 取本节匹配块，UTF-8 编码后 SHA-256 |

### T-006.2 当前 Manifest（唯一尝试，终态 `BLOCKED`）

| 项 | 值 |
|---|---|
| 冻结真源 blob hash（执行前核验） | 上位合同 `9a57d255dec44477ceb38f6f61faaa5f43d36343f89803364eac5df6d5fc5ca0`；v0.1下位合同 `a69a467aeca648a5e0a98068278daa6dccca5a5c734fb8dcd93021fe4befbca2`；v0.2下位合同 `677c7f350410b934b5e25caa3cf98f4665a48936588adc66798d093b042ece9d`；通用EP-00 `afea2d975b1e214ee57aaaab3bfaee63bb6d0319403bfe6d8e66285c2b1bce11`；专项EP-00 `921091b5a43fb72371c5c95e6bb07e6ccd87db6baa29fb9cff2716e5dd2fbc4d`；共享合同一 `76b730d47566eccc188e2dbb0c4da2e8aa594936cc813987cc8d0fd7901bd63b`；共享合同二 `6d3fb85ebce417c4d34103775f833656dab7d62e390b0c9ba482ccc9108e8a30`；共享合同三 `67af3e991394fb27964470bcdbf5a46678a494e4045db60eb573b31ea924ee2b`；共享合同四 `108209b52df232e91e06b5726b2c19eb6094f06eb7025971a958750143a172f0` |
| P0-A 状态 | **`BLOCKED`**——见 `attachment_verification`：收到的规划前言正文不含本仓库全部已采用真源文档的标准 markdown 语法特征，判定为聊天转写而非附件原始字节，无法验证其 SHA-256 等于冻结值 `9b046e9b6b8008d66e7347fcc878d2eed13cf251c3a899ed3ea989f761774da6`；按 Prompt §2 明文指令未写入 `decision-chain/docs/V1_M1_M4_CONSTRUCTION_PROMPT_SHARED_PREAMBLE_v0.1.md`，也未自行补全格式后重算哈希 |
| P0-A 内已完成的独立工作 | L2 两处当前投影纠偏（不依赖附件，见 [L2 §一.7](L2_TASK_STATE_AND_HANDOFF.md) `next_stage_allowed` 行「状态更正1」＋ §二「下一权限动作」表「状态更正2」）：(1) `M1-M4_ENGINEERING_EXECUTION` 由误写的 `AUTHORIZED_BY_FOUNDER` 更正为 `NOT_AUTHORIZED`；(2) M1-M4 模块职责映射由误写的「M1=业务持久化／M2=写回权限恢复实现／M3=单账号持续运营能力／M4=待定」更正为 Prompt §二冻结的「M1=自然交互任务上下文与能力路由／M2=最小业务数据版本与运营记忆／M3=运营状态诊断与持续运营决策／M4=现有能力组件化接入与兼容改造」 |
| P0-B 状态 | **`BLOCKED`**（未启动）——依赖 P0-A 产出的最终 `origin/main`（含已采用的前言文件）作为桌面包 `source_full_commit`；P0-A 未完成，P0-B 无有效源可用，不得用当前 main（缺前言文件）冒充最终 main 生成桌面包 |
| 任务终态 | `BLOCKED`，见 [L2](L2_TASK_STATE_AND_HANDOFF.md) 与 [L3](L3_ATTEMPTS_AND_EVIDENCE.md) |
| 解除条件 | Founder／规划侧提供可核验的真实附件文件（而非聊天正文转写）——例如把文件放入仓库指定路径供逐字节读取，或提供能重算出等于冻结值 SHA-256 的原始 markdown 字节；解除后，新会话或新 attempt 只需重新执行本任务的 P0-A/P0-B，无需重跑本次已完成的 L2 纠偏或激活门核验 |
| 范围补记 | T-006.1 `allowed_delta.modified_files` 遗漏了 `collab-ledger/L5_SIDE_EFFECTS.md`；Execution Prompt 自身 `authorized_scope.write` 明确包含该文件（"仅记录真实 Git 远程副作用"），本任务实际按 Prompt 权限记录了任务分支推送（[L5 SE-009](L5_SIDE_EFFECTS.md)），T-006.1 的遗漏属内部合同摘要疏漏，不构成越权 |

### T-006.3 附件解除与 P0-A 完成记录（块外追加，不改动 T-006.1 `task_contract_hash` 覆盖的字节）

| 项 | 值 |
|---|---|
| 触发方式 | Founder 2026-08-25 会话内消息："SHA-256：9b046e9b6b8008d66e7347fcc878d2eed13cf251c3a899ed3ea989f761774da6 已经放到项目根目录"——提供真实附件文件（而非聊天正文转写），回应 [L2 §一.8](L2_TASK_STATE_AND_HANDOFF.md) 登记的解除条件 |
| 附件重新校验 | 文件位于仓库根目录 `V1_M1_M4_CONSTRUCTION_PROMPT_SHARED_PREAMBLE_v0.1.md`（另有 Windows 下载产生的 `:Zone.Identifier` 元数据文件，非内容，已清理不采用）；`sha256sum` 实测 `9b046e9b6b8008d66e7347fcc878d2eed13cf251c3a899ed3ea989f761774da6`，与冻结值**逐字节一致**；抽查内容确认标准 markdown 语法齐全（`#`标题／`\`\`\`yaml`围栏／`\|`表格／`>`引用），与仓库既有真源惯例一致，印证此前 `BLOCKED` 判断（收到的是聊天转写而非原始字节）成立 |
| 内容一致性核查（Prompt §3 六项） | 逐项通过：①明确非第五份共享合同、不替代四份 ACCEPTED 合同（正文 L12）；②八项能力 CAP-01～CAP-08 均给出必需输入／合法等价输入／输出／实质修改下游失效四要素（正文 §四）；③承接用户意图优先、非线性直达、局部失效、角色分离、证据分级、专业能力非全能硬门、不夸大运营提升（正文 §三 各条 + §六）；④Matrix 降级只暂停真实依赖分支，并显式分配 M1/M2/M3/M4 承接责任（正文 §五）；⑤物理 Schema／Dify 节点／数据库／模块实施路线留给后续施工（正文 L33 + §七）；⑥明确 M1-M4 工程仍未授权（正文 `engineering_execution_authorized: false` + L14 + §八第5条）。未发现与六份冻结真源的直接语义冲突，未触发独立复核子代理（六项均为对照原文的直接核对，非需要多角度判断的实质分歧点） |
| 写入结果 | 移动（非复制，保字节）至 `decision-chain/docs/V1_M1_M4_CONSTRUCTION_PROMPT_SHARED_PREAMBLE_v0.1.md`；移动后重算 SHA-256 仍为 `9b046e9b6b8008d66e7347fcc878d2eed13cf251c3a899ed3ea989f761774da6`，未变 |
| P0-A 状态 | **`DONE`**（此前 `BLOCKED` 判断保留在 T-006.2，作为历史记录不删除） |
| P0-B 状态 | `PLANNED`——将在本次 P0-A 内容随任务分支合并进 `main` 并经远端核验后，以该最终 `main` commit 为 `source_full_commit` 执行；结果直接写入本任务最终回执（对 Founder 的收工消息），**不再为记录桌面快照单独创建 Git 提交**（Execution Prompt `authorized_scope.write` 对 L5 的限定：仅记录真实 Git 远程副作用，桌面快照结果在最终回执记录） |

## §T-007 · `V1-M1-M4-PHASE0-DECISION-STATE-CLOSEOUT-001`

### T-007.1 Task Contract（稳定合同）

> 下面这个 ```yaml 代码块的**块内字节**即 `task_contract_hash` 的哈希对象。**不含**聊天摘要与执行计划。

```yaml
task_id: V1-M1-M4-PHASE0-DECISION-STATE-CLOSEOUT-001
task_entry_mode: NEW_TASK
parent_task_id: V1-M1-M4-PHASE0-PREAMBLE-ADOPTION-AND-DESKTOP-PACK-001
task_type: DOC_STATE_CORRECTION
risk_level: LOW
authority_refs:
  - "Founder 2026-08-25 当前会话消息：完整 Execution Prompt《M1–M4 Phase 0 决策状态一致性收口》。"
  - "该 Prompt 自身声称 Founder 已通过'连续动作'完成正式确认，且明文禁止执行侧再次核验此前提——经与本会话实际记录比对（用户此前仅提供前言附件、提问'四类合同值填什么'、提问'是否还有缺口'，执行侧当时明确答复'还有两处缺口需要 Founder 拍板'），该历史叙述不成立；执行侧未按 Prompt 字面指令跳过核验，而是通过 AskUserQuestion 直接向 Founder 求证。"
  - "Founder 2026-08-25 通过 AskUserQuestion 明确选择'我现在就是在确认'——本次确认的真实来源是这一当场答复，不是 Prompt 文本所称的历史'连续动作'。"
core_problem: >-
  M1-M4 Phase 0 共享编译前言采用后，前言状态仍停留在"待验证采用"，L2 当前投影仍把八项能力四类
  合同值与 Matrix 整任务硬停处置列为"待 Founder 或规划侧指定归属"的阻塞项；本任务只做状态表达
  纠偏，不重审 32 项合同值内容，不编译 M1-M4 施工 Prompt，不授权工程实现。

activation_gate_verified_at_execution:
  main_local: c085eb327bbc24c6b5c46a8e3ee4d003038a40e3
  main_remote: c085eb327bbc24c6b5c46a8e3ee4d003038a40e3
  working_tree_before_this_task: clean
  planning_observed_baseline: c085eb327bbc24c6b5c46a8e3ee4d003038a40e3
  drift_from_planning_observed_point: NONE
  preamble_present_on_main: true（sha256 = 9b046e9b6b8008d66e7347fcc878d2eed13cf251c3a899ed3ea989f761774da6，与冻结值一致）
  preamble_section_four_covers_eight_capabilities: true（CAP-01～CAP-08 均含必需业务输入/合法等价输入/输出/下游失效四要素，本会话此前已通读全文核实）
  preamble_section_five_covers_matrix_rules_and_module_assignment: true（七条降级/局部阻断规则 + M1/M2/M3/M4 承接段落，本会话此前已通读全文核实）
  verdict: ALL_CONDITIONS_MET_NOT_BLOCKED_AT_ACTIVATION

allowed_delta:
  modified_files:
    - decision-chain/docs/V1_M1_M4_CONSTRUCTION_PROMPT_SHARED_PREAMBLE_v0.1.md（仅 YAML 状态块：status/product_semantics_confirmation 字段，§三至§八正文字节不变）
    - PROJECT_INDEX.md（仅状态字符串）
    - collab-ledger/L1_TASK_MANIFESTS.md
    - collab-ledger/L2_TASK_STATE_AND_HANDOFF.md
    - collab-ledger/L3_ATTEMPTS_AND_EVIDENCE.md
  everything_else: FORBIDDEN

protected_assets: [四份 V1_M0_SHARED_CONTRACT_*_v0.1.md（含八项能力合同正文）, 上位产品合同, 下位合同v0.1与v0.2,
  两份EP-00报告, 前言正文§三至§八, decision-chain/skills, decision-chain/workflows, content-production/skills,
  content-production/workflows, tools, M3项目外研究资料包, 全部M1-M4工程实现]

terminal_rule:
  forbidden: [PARTIAL, 重审32项合同值, 编译M1-M4施工Prompt, 授权工程实现, 不经核验照抄Prompt自称的确认历史]
  on_activation_gate_fail: [BLOCKED, FAILED, INVALID]
scope_boundary: "只修正前言 YAML 状态字段 + L2 当前投影两处阻塞语言 + PROJECT_INDEX 状态字符串；确认来源必须绑定到 Founder 本次会话内 AskUserQuestion 的真实答复，不得采用 Prompt 自称的历史叙述。"
```

| 项 | 值 | 怎么重算 |
|---|---|---|
| `task_contract_hash` | `acea368883b0029a97223ed46b5933c74a86f4d71bfc65729130c42164f674bd` | `re.finditer(r'```yaml\n(.*?)\n```', content, re.DOTALL)` 取本节匹配块，UTF-8 编码后 SHA-256 |

### T-007.2 当前 Manifest

| 项 | 值 |
|---|---|
| 前提核验 | Prompt §二声称"Founder 已通过连续动作完成正式确认"且要求执行侧不得再次核验；执行侧对照本会话实际记录判定该历史叙述不成立，未直接执行，改为 `AskUserQuestion` 求证；Founder 选择"我现在就是在确认"，确认来源改记为本次当场答复，日期 2026-08-25 |
| DS-C01 | **PASS**——`main` 含前言文件，§四/§五正文未改写（仅 YAML 状态块变化） |
| DS-C02 | **PASS**——前言 `status: "ACTIVE_ON_DEFAULT_BASELINE"`，`product_semantics_confirmation: "FOUNDER_CONFIRMED"`，`engineering_execution_authorized: false` |
| DS-C03 | **PASS**——L2 §二"下一权限动作"表不再把两项列为待 Founder/规划侧指定归属的阻塞条件（见「状态更正3」） |
| DS-C04 | **PASS**——L2 同处明确：`MATRIX_INSUFFICIENT_INPUT_ENGINEERING = ASSIGNED_TO_M1_AND_M4_CONSTRUCTION`，M4 主修物理硬停、M1 承接交互/路由、M2/M3 按前言 §五配合 |
| DS-C05 | **PASS**——PROJECT_INDEX 第 14 行状态字符串同步为 `ACTIVE_ON_DEFAULT_BASELINE — FOUNDER_CONFIRMED`，与前言、L2 一致，无旧状态并排 |
| DS-C06 | **PASS**——四份共享合同、上位/下位合同、两份 EP-00 执行前后 blob hash 见下表，逐一核对无变化 |
| DS-C07 | **PASS**——`git diff --stat` 仅含前言/L1/L2/L3/PROJECT_INDEX 五个文件，无工程施工、无新治理文件 |
| DS-C08 | 见任务分支/远程收口记录（本条随 Git 采用步骤核验，结果写入最终回执） |
| 受保护资产 blob hash（执行前=执行后，逐一核对一致） | 上位合同 `9a57d255dec44477ceb38f6f61faaa5f43d36343f89803364eac5df6d5fc5ca0`；v0.1下位合同 `a69a467aeca648a5e0a98068278daa6dccca5a5c734fb8dcd93021fe4befbca2`；v0.2下位合同 `677c7f350410b934b5e25caa3cf98f4665a48936588adc66798d093b042ece9d`；通用EP-00 `afea2d975b1e214ee57aaaab3bfaee63bb6d0319403bfe6d8e66285c2b1bce11`；专项EP-00 `921091b5a43fb72371c5c95e6bb07e6ccd87db6baa29fb9cff2716e5dd2fbc4d`；共享合同一 `76b730d47566eccc188e2dbb0c4da2e8aa594936cc813987cc8d0fd7901bd63b`；共享合同二 `6d3fb85ebce417c4d34103775f833656dab7d62e390b0c9ba482ccc9108e8a30`；共享合同三 `67af3e991394fb27964470bcdbf5a46678a494e4045db60eb573b31ea924ee2b`；共享合同四 `108209b52df232e91e06b5726b2c19eb6094f06eb7025971a958750143a172f0` |
| 任务终态 | 见最终回执 |

## §T-008 · `V1-M1-ENGINEERING-PROMPT-ADOPTION-001`

### T-008.1 Task Contract（稳定合同）

> 下面这个 ```yaml 代码块的**块内字节**即 `task_contract_hash` 的哈希对象。**不含**聊天摘要与执行计划。

```yaml
task_id: V1-M1-ENGINEERING-PROMPT-ADOPTION-001
task_entry_mode: NEW_TASK
parent_task_id: V1-M1-M4-PHASE0-DECISION-STATE-CLOSEOUT-001
task_type: DOC_ADOPTION
risk_level: LOW
authority_refs:
  - "Founder 2026-08-25 当前会话消息：随文给出规划侧成稿《Execution Prompt — M1 自然语言交互与任务上下文编译 v1.2》正文，随后消息「执行落盘」。"
  - "该正文声明 planning_status: READY_FOR_FOUNDER_USE，并自述 engineering_execution_authorized_by_prompt_compilation: false；正文 0 节与 3.1 节明文要求：只读核验不构成开工，工程写入需 Founder 另行把准确文件交给工程执行终端并明确授权执行。执行侧就「执行落盘」一词的范围（落盘文档本身 / 启动工程执行 / 二者皆是）主动请用户澄清，用户回复仅确认文件已放置于仓库根目录，未答复该范围问题；按未获得针对工程执行的明确授权处理，本任务只落盘/采用规划文档本身，不新建 DIYU-V1-M1-NATURAL-CONTEXT-001 任务分支、不做任何工程/Dify写入。"
core_problem: >-
  规划侧已产出 M1 完整施工 Execution Prompt（W1-M1 窗口），用户以聊天正文粘贴方式提供，
  首次经执行侧手工转录后自算 task_contract_hash 不一致，判定转录漂移，要求用户改以仓库根目录
  真实文件提供；文件到位后逐字节读取核验通过。本任务负责将该文件原样采用进仓库规范位置、
  核验其自证哈希与引用真源哈希、账本登记，明确本任务不构成、也不授权 M1 工程执行本身。

activation_gate_verified_at_execution:
  main_local: 2a0822692802ac084d92e032f098da33079f063d
  main_remote: 2a0822692802ac084d92e032f098da33079f063d
  working_tree_before_this_task: clean
  planning_observed_baseline_in_prompt: 2a0822692802ac084d92e032f098da33079f063d
  drift_from_planning_observed_point: NONE
  referenced_source_docs_hash_check: "文档 §1.3 引用的 9 份仓库真源文件（上位合同/下位合同v0.2/两份EP-00/四份共享合同/Phase0前言）sha256 逐一现算，与文档声明值全部一致"
  task_contract_hash_self_consistency: "文档 §2 TASK_CONTRACT_BEGIN/END 间字节（含末行换行，不含围栏）sha256 与文档 §14 自称 task_contract_hash 一致"
  verdict: ALL_CONDITIONS_MET_NOT_BLOCKED_AT_ACTIVATION

allowed_delta:
  modified_files:
    - decision-chain/docs/M1_ENGINEERING_EXECUTION_PROMPT_v1.2.md（新增，原样移动，字节不变）
    - PROJECT_INDEX.md
    - collab-ledger/L1_TASK_MANIFESTS.md
    - collab-ledger/L2_TASK_STATE_AND_HANDOFF.md
    - collab-ledger/L3_ATTEMPTS_AND_EVIDENCE.md
    - collab-ledger/L5_SIDE_EFFECTS.md
  everything_else: FORBIDDEN

protected_assets: [四份 V1_M0_SHARED_CONTRACT_*_v0.1.md, 上位产品合同, 下位合同v0.1与v0.2, 两份EP-00报告,
  decision-chain/docs/V1_M1_M4_CONSTRUCTION_PROMPT_SHARED_PREAMBLE_v0.1.md, decision-chain/skills,
  decision-chain/workflows, content-production/skills, content-production/workflows, tools,
  全部用户未提交改动和其他worktree]

terminal_rule:
  forbidden: [PARTIAL, 新建或推送 task/m1-natural-interaction-context-v1 分支, 创建或修改任何 Dify 对象,
    自行推断本任务即等于对 M1 工程执行的明确授权, 自行编写或推断 M2/M3/M4 施工 Prompt]
  on_activation_gate_fail: [BLOCKED, FAILED, INVALID]
scope_boundary: "只做文档原样落盘、引用哈希与自证哈希核验、账本登记（含 L5 推送记录）；不新建、不触碰 DIYU-V1-M1-NATURAL-CONTEXT-001 任务的任何分支/worktree/Dify对象/账本条目；不构成对该任务工程执行的授权。"
```

| 项 | 值 | 怎么重算 |
|---|---|---|
| `task_contract_hash` | `fa9fe16a6173ae3502eeef8d64d716461423bd94302e4b73a39420b59baeedc4` | `re.finditer(r'```yaml\n(.*?)\n```', content, re.DOTALL)` 取本节匹配块，UTF-8 编码后 SHA-256 |

### T-008.2 当前 Manifest

| 项 | 值 |
|---|---|
| 范围澄清 | 执行侧收到聊天粘贴正文后先行提问：「执行落盘」具体指落盘文档本身，还是启动 M1 工程执行（新建 `task/m1-natural-interaction-context-v1` 分支/Dify对象），或二者皆是；用户回复"已经放到仓库根目录"，只回答了文件位置问题，未回答范围问题。按最小授权原则，本任务只完成范围内确定无歧义的部分（文档落盘），不推断用户默认同意了工程执行 |
| 转录漂移与解决 | 用户首次以聊天正文粘贴方式提供全文（约 22KB，14 节），执行侧手工转录进暂存文件后自算 `task_contract_hash` 与文档自称值不一致，判定为转录漂移，未采用；请用户改为仓库根目录真实文件提供。文件到位（`M1_ENGINEERING_EXECUTION_PROMPT_v1.2.md`，41315 字节）后用 Read 工具逐字节读取，不再经手工转录 |
| DA-01 引用真源哈希核验 | **PASS**——文档 §1.3 引用的 9 份文件（上位产品合同、下位切片合同v0.2、通用/专项 EP-00、四份 M0.3 共享合同、Phase0 共享前言）sha256 逐一现算，与文档声明值逐字节一致 |
| DA-02 文档自证哈希核验 | **PASS**——用 Python 精确定位 `<!-- TASK_CONTRACT_BEGIN -->`/`<!-- TASK_CONTRACT_END -->` 标记，取内部 `` ```yaml `` 围栏间字节（含最后一行 `next_stage_default: false` 的行尾换行，不含围栏本身）sha256 = `d6b0b3d84cdf18f0c19f224cd5e9e43ca03839e53b95b7b667411cfb8e647df3`，与文档 §14 `task_contract_hash` 字段完全一致 |
| DA-03 现场事实核验 | **PASS**——文档 §1.4 `observed_local_head`/`observed_local_origin_main`/`observed_github_main` 均为 `2a0822692802ac084d92e032f098da33079f063d`，与执行本任务时的 `main`/`origin/main` 一致，无漂移 |
| DA-04 落盘位置与移动保字节 | **PASS**——`mv`（非复制）从仓库根目录移动到 `decision-chain/docs/M1_ENGINEERING_EXECUTION_PROMPT_v1.2.md`（与共享前言同目录，未改文件名，保持文档 §14 `prompt_file` 自称字段与实际文件名一致）；移动前后 sha256 = `b0adc1fc770abcb09dc2466d36a4803e3dba81ddafb63876d396e10848c37e4a`，未变 |
| DA-05 未越权扩大 | **PASS**——`git status --short` 只含本条 `allowed_delta.modified_files` 列出的 6 个文件；未新建、未触碰 `task/m1-natural-interaction-context-v1`；未创建任何 Dify 对象；未编译 M2/M3/M4 Prompt |
| 受保护资产核验 | 四份共享合同、上位/下位合同、两份 EP-00、Phase0 前言执行前后 blob hash 逐一核对，全部一致（前言 sha256 `210ccf7407498a9566ff99aa1486a0815abb53879705aff83448252a2a58a388`，未被本任务触碰） |
| 独立复核 | 未触发——全部为对照文档正文的直接哈希核验与状态字段登记，无需要多角度判断的实质分歧点 |
| 任务终态 | 见最终回执 |

## §T-009 · `V1-COLLAB-PROTOCOL-PROMPT-AUTHORIZATION-RULE-001`

### T-009.1 Task Contract（稳定合同）

> 下面这个 ```yaml 代码块的**块内字节**即 `task_contract_hash` 的哈希对象。**不含**聊天摘要与执行计划。

```yaml
task_id: V1-COLLAB-PROTOCOL-PROMPT-AUTHORIZATION-RULE-001
task_entry_mode: NEW_TASK
parent_task_id: V1-M1-ENGINEERING-PROMPT-ADOPTION-001
task_type: GOVERNANCE_RULE_UPDATE
risk_level: LOW
authority_refs:
  - "Founder 2026-08-25 当前会话消息（直接、当场、非文档自称）：「铁律：后续只要注入执行prompt，即视为授权，不再重复」。按治理来源优先级第 1 项（Founder 当前明确裁决），此条高于任何既有 Prompt 静态写定的 allowed_delta，构成对本条规则本身的直接授权。"
core_problem: >-
  此前每次收到完整 Execution Prompt，执行侧都会为"是否可以开始工程执行"单独征求确认，
  造成重复摩擦。Founder 直接裁定：注入完整 Execution Prompt 本身即为执行授权，今后不需要
  逐次重复确认。本任务把这条裁决写入协作连续性规则正文，使任何未来读到该文件的执行代理
  （不只是本次会话）都能看到并遵守。
allowed_delta:
  modified_files:
    - collab-ledger/COLLAB_CONTINUITY_PROTOCOL.md（§六新增一条硬规矩）
    - collab-ledger/L1_TASK_MANIFESTS.md
    - collab-ledger/L2_TASK_STATE_AND_HANDOFF.md
    - collab-ledger/L3_ATTEMPTS_AND_EVIDENCE.md
  everything_else: FORBIDDEN
protected_assets: [四份 V1_M0_SHARED_CONTRACT_*_v0.1.md, 上位产品合同, 下位合同v0.1与v0.2, 两份EP-00报告,
  decision-chain/docs/V1_M1_M4_CONSTRUCTION_PROMPT_SHARED_PREAMBLE_v0.1.md,
  decision-chain/docs/M1_ENGINEERING_EXECUTION_PROMPT_v1.2.md, decision-chain/skills,
  decision-chain/workflows, content-production/skills, content-production/workflows, tools]
scope_boundary: "只在协作连续性规则正文新增一条'执行 Prompt 即授权'的硬规矩，并在账本登记；不改变本条规则之外的任何既有规则、合同或受保护资产；本条只免除逐次确认，不免除 Prompt 自身写定的 allowed_delta／protected_assets／explicitly_not_authorized 等边界。"
```

| 项 | 值 | 怎么重算 |
|---|---|---|
| `task_contract_hash` | `ea8cc751c5ed6e9799208dde577a2ce1fee53ce60913737c69cf3daf38f02388` | `re.finditer(r'```yaml\n(.*?)\n```', content, re.DOTALL)` 取本节匹配块，UTF-8 编码后 SHA-256 |

### T-009.2 当前 Manifest

| 项 | 值 |
|---|---|
| 触发 | Founder 2026-08-25 直接会话消息，紧接在执行侧交付 `V1-M1-ENGINEERING-PROMPT-ADOPTION-001` 最终回执（其中明确写"启动 M1 实际工程施工需要你另外明确说一句"）之后 |
| 写入内容 | `collab-ledger/COLLAB_CONTINUITY_PROTOCOL.md` §六新增一条硬规矩："执行 Prompt 即授权"——注入完整 Execution Prompt 本身即视为执行授权，免除逐次确认；明确不免除 Prompt 自身的 `allowed_delta`／`protected_assets`／`explicitly_not_authorized` 等边界，也不免除既有 `REBASE_TASK`／`BLOCKED` 机制 |
| 适用范围核验 | 本条只约束"是否需要为同一份 Prompt 逐次重复征求执行确认"这一步；不改变、不放宽任何受保护资产、验收标准或既有合同条款；与 [[project-diyu-demo-governance-self-escalation]] 类记忆／[L3 §九](L3_ATTEMPTS_AND_EVIDENCE.md) 记录的"Prompt 自称历史不可信"纪律不冲突——后者约束的是文档对*过去*事件的自我主张，本条约束的是 Founder *当场直接*给出的指令，两者裁定对象不同 |
| 受保护资产核验 | 未触碰任何受保护资产；`git status --short` 仅含本条授权的 4 个文件 |
| 独立复核 | 未触发——单一规则文本新增，无实质判断分歧点 |
| 任务终态 | 见最终回执 |

## §T-010 · `V1-M2-ENGINEERING-PROMPT-ADOPTION-001`

### T-010.1 Task Contract（稳定合同）

> 下面这个 ```yaml 代码块的**块内字节**即 `task_contract_hash` 的哈希对象。**不含**聊天摘要与执行计划。

```yaml
task_id: V1-M2-ENGINEERING-PROMPT-ADOPTION-001
task_entry_mode: NEW_TASK
parent_task_id: V1-COLLAB-PROTOCOL-PROMPT-AUTHORIZATION-RULE-001
task_type: DOC_ADOPTION
risk_level: LOW
authority_refs:
  - "Founder 2026-08-25 当前会话消息：「M2_业务持久化版本发布反馈投影_Execution_Prompt_v1.1.md 已经放到仓库根目录，授权推进落盘」。字面授权范围限定为「落盘」，不是「工程执行」。"
  - "该正文声明 M2_ENGINEERING_EXECUTION_PROMPT = READY_FOR_FOUNDER_USE、engineering_execution_performed = false，正文 0 节明文：只完成规划编译，未被本规划窗口执行，也不因文件存在而自动授权工程施工。"
  - "§六新增铁律「执行 Prompt 即授权」（见 L1 §T-009）本身声明只免除逐次重复确认，Prompt 自身内容仍是执行范围边界；本任务按该条与 Founder 本次字面用词（「落盘」）的交集，只判定落盘本身已获授权，M2 工程执行是否已被一并授权留待 Founder 就该具体 task_id 显式确认，不由执行侧自行推定。"
core_problem: >-
  规划侧已产出 M2 完整施工 Execution Prompt v1.1（W2 窗口），文件已放置于仓库根目录；
  本任务负责将其原样落盘进规范位置、核验引用真源哈希与文档自证哈希、账本登记，
  并明确本任务本身不构成对 M2 工程执行（task_id: DIYU-V1-M2-BUSINESS-PERSISTENCE-VERSION-FEEDBACK-001）的授权。

activation_gate_verified_at_execution:
  main_local: 0de99930ff5da5c24aa2fbe34615abe52cc6c7db
  main_remote: 0de99930ff5da5c24aa2fbe34615abe52cc6c7db
  working_tree_before_this_task: "clean except untracked root文件 M2_业务持久化版本发布反馈投影_Execution_Prompt_v1.1.md（本任务处理对象）"
  planning_observed_baseline_in_prompt: 2a0822692802ac084d92e032f098da33079f063d
  drift_from_planning_observed_point: "main 已前进 3 个 commit（V1-M1-ENGINEERING-PROMPT-ADOPTION-001 落盘 + V1-COLLAB-PROTOCOL-PROMPT-AUTHORIZATION-RULE-001 铁律登记）；git diff 2a0822..0de9993 -- decision-chain/ 只新增 M1 Prompt 文件，文档 §1.2 引用的 9 份真源文件 blob hash 逐一现算与 main@2a0822 时完全一致，无漂移"
  referenced_source_docs_hash_check: "文档 §1.1/§1.2 引用的 9 份仓库内真源文件（上位合同/下位合同v0.2/两份EP-00/四份共享合同/Phase0前言）sha256 逐一现算，与文档声明值全部一致；规划工作区外部文件（Windows 路径）不可从本仓库核验，按引用记录"
  task_contract_hash_self_consistency: "MISMATCH——用两种独立方法（awk/sed 提取 + Python 精确字节切片，同一方法在 M1 文档上验证可正确复现其 d6b0b3d8... 自证哈希）复算 M2 文档 §3 TASK_CONTRACT_BEGIN/END 间字节，得 4d14eb35c065b650b0380b0c309e0e08ec32e3aa608ece4d62e8d27b97450830，与文档 §3/§12 自称 task_contract_hash（e17b354b97d53bfa52eeb30ffca50970e5469acabee98b3cfc32a1031b1b90ca）不一致；已排除 CRLF/BOM/行尾空白/隐藏字符等转录类误差。已用 AskUserQuestion 向 Founder 报告，Founder 选择「按实测值登记，继续落盘」；本任务后续全部引用改用独立复算值 4d14eb35...，并在 PROJECT_INDEX/本节/T-010.2 显式披露该不一致，不覆盖文档原文、不代文档静默改称一致"
  verdict: ALL_CONDITIONS_MET_NOT_BLOCKED_AT_ACTIVATION_WITH_DISCLOSED_HASH_MISMATCH

allowed_delta:
  modified_files:
    - decision-chain/docs/M2_ENGINEERING_EXECUTION_PROMPT_v1.1.md（新增，原样移动，字节不变）
    - PROJECT_INDEX.md
    - collab-ledger/L1_TASK_MANIFESTS.md
    - collab-ledger/L2_TASK_STATE_AND_HANDOFF.md
    - collab-ledger/L3_ATTEMPTS_AND_EVIDENCE.md
    - collab-ledger/L5_SIDE_EFFECTS.md
  everything_else: FORBIDDEN

protected_assets: [四份 V1_M0_SHARED_CONTRACT_*_v0.1.md, 上位产品合同, 下位合同v0.1与v0.2, 两份EP-00报告,
  decision-chain/docs/V1_M1_M4_CONSTRUCTION_PROMPT_SHARED_PREAMBLE_v0.1.md, decision-chain/docs/M1_ENGINEERING_EXECUTION_PROMPT_v1.2.md,
  decision-chain/skills, decision-chain/workflows, content-production/skills, content-production/workflows, tools,
  全部用户未提交改动和其他worktree]

terminal_rule:
  forbidden: [PARTIAL, 新建或推送 task/m2-business-persistence-version-feedback-v1 分支, 创建或修改任何 PostgreSQL/Dify 对象,
    自行推断本任务即等于对 M2 工程执行的明确授权, 自行编写或推断 M3/M4 施工 Prompt, 静默改写文档正文使自证哈希"看起来"一致]
  on_activation_gate_fail: [BLOCKED, FAILED, INVALID]
scope_boundary: "只做文档原样落盘、引用哈希与自证哈希核验（含披露不一致）、账本登记（含 L5 推送记录）；不新建、不触碰 DIYU-V1-M2-BUSINESS-PERSISTENCE-VERSION-FEEDBACK-001 任务的任何分支/worktree/数据库/Dify对象/账本条目；不构成对该任务工程执行的授权。"
```

| 项 | 值 | 怎么重算 |
|---|---|---|
| `task_contract_hash` | `727075798e0a9cdceb217542c1cf91c37f12c177b9e847bea11fb35f28c58a97` | `re.finditer(r'```yaml\n(.*?)\n```', content, re.DOTALL)` 取本节匹配块，UTF-8 编码后 SHA-256 |

### T-010.2 当前 Manifest

| 项 | 值 |
|---|---|
| 范围核验 | Founder 消息字面只授权「落盘」；参照 [[V1-M1-ENGINEERING-PROMPT-ADOPTION-001]] 先例的最小授权原则，本任务只完成确定无歧义部分（文档落盘），不推断 Founder 已一并授权 M2 工程执行；新铁律（T-009）不改变这一判断——铁律正文自述"不免除 Prompt 自身内容的执行范围边界"，M2 文档正文自身又明写"不因文件存在而自动授权工程施工"，两者叠加后仍是"落盘≠执行授权" |
| DA-01 引用真源哈希核验 | **PASS**——文档 §1.2 引用的 9 份仓库内文件 sha256 逐一现算，与文档声明值逐字节一致 |
| DA-02 文档自证哈希核验 | **FAIL（已披露，非转录漂移）**——用同一方法（先在 M1 文档上验证可正确复现 `d6b0b3d8...`）对 M2 文档精确定位 `<!-- TASK_CONTRACT_BEGIN -->`/`<!-- TASK_CONTRACT_END -->` 间 `` ```yaml `` 围栏内字节，sha256 = `4d14eb35c065b650b0380b0c309e0e08ec32e3aa608ece4d62e8d27b97450830`，与文档 §3/§12 自称值 `e17b354b97d53bfa52eeb30ffca50970e5469acabee98b3cfc32a1031b1b90ca` 不一致；已排查 CRLF（无）、BOM（无）、行尾空白（0 处）、隐藏字符（唯一非 ASCII 命中为正常中文引号/箭头）。判定为文档自身编译时哈希未与最终内容同步，非本次转录/传输引入。已用 AskUserQuestion 向 Founder 报告，Founder 裁决「按实测值登记，继续落盘」——本任务及后续全部引用一律使用独立复算值 `4d14eb35...`，不采用、不代改文档自称值 |
| DA-03 现场事实核验 | **PASS**——`main_local`/`main_remote` 均为 `0de99930...`；`git diff 2a0822..0de9930 -- decision-chain/` 只新增 M1 Prompt 一个文件，M2 文档 §1.2 引用的下位合同/EP-00/四份共享合同/Phase0前言在此期间零改动 |
| DA-04 落盘位置与移动保字节 | **PASS**——`mv`（非复制）从仓库根目录移动到 `decision-chain/docs/M2_ENGINEERING_EXECUTION_PROMPT_v1.1.md`（与 M1/共享前言同目录）；移动前后 sha256 = `8008bebd04b35037e16f5462ea1b7284db7dec943e954263762bbdb4688bb0c6`，未变 |
| DA-05 未越权扩大 | **PASS**——`git status --short` 只含本条 `allowed_delta.modified_files` 列出的 6 个文件；未新建、未触碰 `task/m2-business-persistence-version-feedback-v1`；未创建任何 PostgreSQL/Dify 对象；未编译 M3/M4 Prompt |
| 并发核验 | 落盘前发现主工作区被另一并行会话同时编辑 `COLLAB_CONTINUITY_PROTOCOL.md`/L1/L2（即 T-009 本身，登记"执行 Prompt 即授权"铁律），当时未提交；已用 AskUserQuestion 向 Founder 报告，Founder 选择"等对方提交后再落盘"；本任务在其合并进 `main`（`0de99930...`）之后才开始写入，避免把对方未完成内容打包进本任务 commit |
| 受保护资产核验 | 四份共享合同、上位/下位合同、两份 EP-00、Phase0 前言、M1 落盘文档执行前后 blob hash 逐一核对，全部一致 |
| 独立复核 | 未触发——全部为对照文档正文的直接哈希核验、并发状态核验与状态字段登记，无需要多角度判断的实质分歧点 |
| 任务终态 | 见最终回执 |

---

## §T-011 · `DIYU-V1-M2-BUSINESS-PERSISTENCE-VERSION-FEEDBACK-001`

### T-011.1 Task Contract（稳定合同）

本任务的稳定 Task Contract **就是** `decision-chain/docs/M2_ENGINEERING_EXECUTION_PROMPT_v1.1.md` §3 `TASK_CONTRACT_BEGIN`/`TASK_CONTRACT_END` 围栏内的原文——不在本节重复整段 YAML，避免与源文档产生第二份可能漂移的副本。

```yaml
task_contract_source: decision-chain/docs/M2_ENGINEERING_EXECUTION_PROMPT_v1.1.md
task_contract_fence: TASK_CONTRACT_BEGIN..TASK_CONTRACT_END（该文档 §3）
task_contract_hash_self_declared: e17b354b97d53bfa52eeb30ffca50970e5469acabee98b3cfc32a1031b1b90ca
task_contract_hash_independently_recomputed: 4d14eb35c065b650b0380b0c309e0e08ec32e3aa608ece4d62e8d27b97450830
task_contract_hash_authoritative_for_this_task: 4d14eb35c065b650b0380b0c309e0e08ec32e3aa608ece4d62e8d27b97450830
hash_discrepancy_disclosure: 见 [L1 §T-010.2](#t-1022-当前-manifest) DA-02——Founder 已裁决按独立复算值登记，本任务及其全部引用一律使用该值
```

### T-011.2 当前 Manifest（Rebase/Errata 001 前，历史记录，不覆盖）

| 项 | 值 |
|---|---|
| 授权确认 | [L2 §一.14](L2_TASK_STATE_AND_HANDOFF.md#一14-v1-m2-engineering-prompt-adoption-001m2-工程执行授权确认追加于一13之后不覆盖一13)——Founder 2026-08-25 就本 task_id 明确答复"就是要启动，铁律适用" |
| 入口门 | 分支 `task/m2-business-persistence-version-feedback-v1`、独立 worktree 已建立；PostgreSQL/Dify 现场只读核验已完成（详见 `business-persistence/TECHNICAL_DECISION_RECORD.md`） |
| 数据库隔离门 | PASS——独立数据库 `diyu_business`，owner `diyu_app`（`NOSUPERUSER NOCREATEDB NOCREATEROLE`），对 `dify`/`dify_plugin` `REVOKE ALL`；7 个 Alembic 迁移线性无分叉，现场 `alembic current` = `c3f8b2e6d0a4 (head)`，`upgrade→downgrade -1→upgrade` 往返已在收口验证中核验对称 |
| P0 交付 | 应用后端（FastAPI+SQLAlchemy 2.0+Alembic）、业务身份/工作空间隔离、任务快照五维投影、版本原子晋升、发布/反馈证据隔离、素材撤回级联失效、幂等/并发/恢复、周期与 Campaign 覆盖、产能三分、打法版本化、Cycle N→N+1 双分支记录（M2-AC-07）、旧 Demo 5 槽快照兼容导入（M2-AC-14）、M1/M3/M4 接口边界契约测试（M2-AC-15）、Dify 候选（`app_id: 8f34e8a3-fb49-4d3e-a222-3d666e767adf`）均已交付 |
| 验收标准 | `M2-AC-00` 至 `M2-AC-16` 现场 PASS（`AC-16` 含一项已披露证据新鲜度限制）；`M2-AC-17` 待 Founder。逐条记录见 `business-persistence/M2_ACCEPTANCE_EVIDENCE.md`，不在本表重复 |
| 独立审查 | 三轮，见 [L3 §十三 ATT-001](L3_ATTEMPTS_AND_EVIDENCE.md#十三-diyu-v1-m2-business-persistence-version-feedback-001) |
| Git 收口 | 9 个 commit，本地/远程 head 一致于 `f09e2923a7b57efbcb94cd83ed54c5b6cd94b3c4`；见 [L5](L5_SIDE_EFFECTS.md) SE-014 起 |
| 受保护资产核验 | 四份共享合同、上位/下位合同、两份 EP-00、Phase0 前言、Dify 生产/共享应用与内部表——全程零改动 |
| 独立复核 | 已触发三次（见上「独立审查」行），均为上下文隔离、无写权限的对抗性审查，非本任务自证 |
| 任务终态（本节，已被 T-011.3 取代） | `execution_disposition = CONTINUE`；`task_final_status = null`；`module_delivery_state = AWAITING_FOUNDER_DIFY_ACCEPTANCE`；`next_stage_allowed = false` |

### T-011.3 Rebase/Errata 001 后当前 Manifest（取代 T-011.2 的终态判定，T-011.2 保留为历史）

Founder 投递 `M2_ENGINEERING_EXECUTION_PROMPT_v1.1_REBASE_ERRATA_001.md`，`task_entry_mode` 分层为 `REBASE_TASK`（不写入 T-011.1 稳定合同）。完整记录见 `business-persistence/M2_REBASE_ERRATA_001_RECORD.md`。

| 项 | 值 |
|---|---|
| continuity overlay | `task_entry_mode = REBASE_TASK`（本轮）；后续正常续作用 `CONTINUE_TASK`；不改变 T-011.1 的 `task_contract_hash` |
| 数据库隔离门（纠正） | **部分 PASS**——表级读取隔离有效（`diyu_app` 对 `dify`/`dify_plugin` 实际发起 `SELECT` 被拒绝，现场实测）；但 `CONNECT` 层面未被撤销（`diyu_app` 可实际连接两库，只是读不到数据），此前"REVOKE ALL"表述不准确。修复尝试被权限分类器拦截，未完成，见 [L5](L5_SIDE_EFFECTS.md) 新增条目 |
| P0 修复 | R-04 关闭 `create_version` 并发裸 500（此前刻意披露为不修，本轮真实修复并现场证伪/证实）；R-05 用真实历史产物关闭"旧产物"半，穷尽检索确认"3 槽"Schema 真实不存在；R-09 修复迁移 `downgrade` 对真实数据的裸崩溃 |
| 验收标准（纠正） | `M2-AC-12` 由"已知限制"提升为真 `PASS`；`M2-AC-13`、`M2-AC-16` 由 `PASS`/`PASS 但有限制` 下修为 `NOT_VERIFIED`（真实发现，非放宽标准）；`M2-RB-01`~`14` 新增记录。逐条见 `business-persistence/M2_ACCEPTANCE_EVIDENCE.md`（本轮重写，取代不是追加） |
| 审查预算符合性 | `REVIEW_BUDGET_CONFORMANCE = DEVIATION_REQUIRES_FOUNDER_ACKNOWLEDGEMENT`——冻结预算 1 正式审查+1 修复，实际发生 3 个正式审查单元+1 收口验证单元，本轮如实披露，未追认为"符合预算"，本轮未另开新的正式 Reviewer |
| Git 收口 | 本轮新增 5 个 commit（`3d23674`/`fabffd8`/`6955d66`/`1f8e6c0` 及本次账本登记提交），累计 13 个 commit；见 [L5](L5_SIDE_EFFECTS.md) 新增条目 |
| 任务终态（当前有效） | `execution_disposition = CONTINUE`；`task_final_status = null`；`module_delivery_state = IN_PROGRESS`（**不是** `AWAITING_FOUNDER_DIFY_ACCEPTANCE`——`M2-AC-13`/`M2-AC-16` 未 CURRENT PASS）；`next_stage_allowed = false` |
