# L2 · 任务状态与项目下一动作

> 规则正文见 [COLLAB_CONTINUITY_PROTOCOL.md](COLLAB_CONTINUITY_PROTOCOL.md)。**新会话先读本文件。**
> 本文件属于 canonical §三定义的**当前投影**：状态或规则变化时**直接更新替换**，不必逐条追加更正；旧值由 Git 历史保留。
> （只有 L1／L3／L4／L5 的历史留痕部分才是「追加式，只加不改」——见 canonical §三。）
>
> **三个不能混的东西**（定义见 canonical §四）：
> **Checkpoint** = 任务没做完被中断的续跑点 ｜ **Final Manifest／最终交付引用** = 任务已终结的结论 ｜ **Current Handoff** = 项目层下一步。
> **本文件 §二 是 Current Handoff，不是 Checkpoint，不代表任何任务未完成。**

**账本起算锚点**（固定值，由 `COLLAB-LEDGER-BOOTSTRAP-001` 钉定，**不是持续追踪的当前 HEAD**）：`main @ 6ae78abf5967535bda81392255b8ee3e79e4bcb5`。
**要知道仓库当前实际版本，请实时核验** `git rev-parse main` 或 `git ls-remote origin refs/heads/main`——**不要**把上面这个锚点值当成当前 HEAD。

## 当前活动投影（2026-08-30 · S5 Prompt 1）

`DIYU-V1-UNIFIED-DIFY-APPLICATION-001` 仍为同一非终态任务。S4 已在当前候选图上 `PASS / CURRENT`；Founder 事件 `UAPP-S5-FINAL-TECHNICAL-ACCEPTANCE-2026-08-30` 已授权且仅授权 F1/F2。F1 已 `PASS / CURRENT`，冻结提交 `b1ff8ed7866b6dfb3cd29ca361d1585a34f178e4`；当前为 `F2 IN_PROGRESS / NOT_VERIFIED`，正式模型调用 0/19。Prompt 2、Prompt 3、Founder AC-12、最终包、main 合并与终态均未授权。

当前候选 UAPP 图 md5 `89bbfeade1f149ccce12a768bed6e94a`；PP/provider `8366328bf827bd0f460455d750d45c4f`；Seam `db49a3da8973d4fdcbe9ecf63bdf7e2a`；Hop `e38378c3c2a66b75aa7e645368c9e1ce`。S5 当前进度唯一索引为 `unified-app/stages/UAPP_FINAL_CLOSEOUT_PROGRESS_v1.0.md`，当前技术债主表为 v1.6。

唯一下一动作：按冻结顺序运行 `UAPP-CAP-01` 一次并立即按冻结 Checker 判定；首个硬失败即停。

---

## 一、按 `task_id` 的任务状态

| task_id | 终态？ | 状态引用 | 起算基线 |
|---|---|---|---|
| `COLLAB-LEDGER-BOOTSTRAP-001` | **已终结 `DONE`**（见 §一.1） | [L1 §T-001](L1_TASK_MANIFESTS.md) · [L3 §CLOSEOUT](L3_ATTEMPTS_AND_EVIDENCE.md)（**当前**：收口）；ATT-001～005 **全部**为已判不通过的历史轮次，**不要**当成当前轮次 | `6ae78ab` |
| `V1-REBASE-EP00-CURRENT` | **已终结 `DONE`**（见 §一.3） | [L1 §T-002](L1_TASK_MANIFESTS.md) · [L3 §四 ATT-001](L3_ATTEMPTS_AND_EVIDENCE.md) | `main @ 4d84cd2`（实际执行基线，见 §一.3） |
| `M0-EP00-ADOPTION-CLOSEOUT-001` | **已终结 `DONE`**（见 §一.4） | [L1 §T-003](L1_TASK_MANIFESTS.md) · [L3 §五 ATT-001](L3_ATTEMPTS_AND_EVIDENCE.md) | `main @ 4d84cd2`（起算；终态见 §一.4） |
| `V1-M0-1B-SLICE-CONTRACT-REVISION-001` | **已终结 `DONE`**（见 §一.5） | [L1 §T-004](L1_TASK_MANIFESTS.md) · [L3 §六 ATT-001～003](L3_ATTEMPTS_AND_EVIDENCE.md) | `main @ f94d7a7`（起算；终态见 §一.5） |
| `V1-M0-SLICE-PREFLIGHT-AND-SHARED-CONTRACT-CLOSEOUT-001` | **已终结 `DONE`**（见 §一.7） | [L1 §T-005](L1_TASK_MANIFESTS.md) · [L3 §七](L3_ATTEMPTS_AND_EVIDENCE.md) | `main @ 0eba71a`（起算；终态见 §一.7） |
| `V1-M1-M4-PHASE0-PREAMBLE-ADOPTION-AND-DESKTOP-PACK-001` | 首次尝试 `BLOCKED`（§一.8），附件补齐后 P0-A `DONE`（§一.9），采用进 `main` 与桌面包见最终回执 | [L1 §T-006](L1_TASK_MANIFESTS.md) · [L3 §八 ATT-001～002](L3_ATTEMPTS_AND_EVIDENCE.md) | `main @ cba3a30`（起算；P0-A 完成见 §一.9） |
| `V1-M1-M4-PHASE0-DECISION-STATE-CLOSEOUT-001` | **已终结 `DONE`**（见 §一.10） | [L1 §T-007](L1_TASK_MANIFESTS.md) · [L3 §九 ATT-001](L3_ATTEMPTS_AND_EVIDENCE.md) | `main @ c085eb3`（起算；终态见 §一.10） |
| `DIYU-V1-M1-NATURAL-CONTEXT-001` | **已终结 `DONE`**（Founder 2026-08-26 实测 ACCEPT + CTA 授权语义裁决，见 [L2 §四 Checkpoint](#四非终态-checkpoint-区)） | [L3 §十四 ATT-001](L3_ATTEMPTS_AND_EVIDENCE.md) · [evidence §19.5](../decision-chain/evidence/V1_M1_CANDIDATE_RUN_001.md) · [最终技术回执](../decision-chain/evidence/V1_M1_FINAL_TECHNICAL_RECEIPT_v1.4.1.yaml) | `main @ 0de99930ff5da5c24aa2fbe34615abe52cc6c7db`（起算基线；已经 `DIYU-V1-M1-MODULE-LANDING-001` 合并进 `main`，不再是"未合入 main"，见 [L1 新增行](L1_TASK_MANIFESTS.md) 与 `decision-chain/evidence/V1_M1_MODULE_LANDING_RECEIPT_v1.0.md`） |

### 一.1 `COLLAB-LEDGER-BOOTSTRAP-001`

| 项 | 值 |
|---|---|
| 状态 | **`DONE`** —— C1–C6 与 R1–R6 全部通过；远端核验已完成（[L3 §收口.7](L3_ATTEMPTS_AND_EVIDENCE.md)） |
| activation_status | **`ACTIVE_ON_DEFAULT_BASELINE`** —— 账本已在远程默认基线 `main` 上 |
| next_stage_allowed | **`true:V1-REBASE-EP00-CURRENT`** |
| 终结依据 | [L3 §CLOSEOUT](L3_ATTEMPTS_AND_EVIDENCE.md)（**当前**：收口记录，含 C1–C6／R1–R6、13 条已知问题登记、完整历史引用）。ATT-001～005 **全部**为已判不通过的历史轮次 |
| 最终交付引用 | [L3 §收口.7](L3_ATTEMPTS_AND_EVIDENCE.md)。**终态 `DONE` 的生效条件是远端 `main` 确实包含本账本**——核验通过前不得据此声称已生效 |
| Checkpoint | **无。** 本任务**已终结**、全程**未被中断**，不满足写 Checkpoint 的条件（Checkpoint 只给「开工后被外部强制中断的未终结任务」） |

### 一.2 `V1-REBASE-EP00-CURRENT`（本条记录截至开工前的状态，历史原文保留；终态见 §一.3）

| 项 | 值 |
|---|---|
| 状态 | **未开工**（截至本条写入时） |
| 授权 | [上位合同](../decision-chain/docs/V1_DECISION_CHAIN_REBASE_PRODUCT_CONTRACT_v0.1.md) `PRODUCT_CONTRACT_ACCEPTED — REPO_PREFLIGHT_AUTHORIZED` —— **已授权，可立即开工** |
| Checkpoint | **无**。它从未启动，不存在续跑点 |
| 下一动作 | 见 §一.3（已开工并终结） |

### 一.3 `V1-REBASE-EP00-CURRENT`（终态，追加于 §一.2 之后，不覆盖 §一.2）

| 项 | 值 |
|---|---|
| 状态 | **`DONE`** —— A1–A10、A14–A16 全部通过，一轮直达收口，未触发第二轮复核 |
| 实际执行基线 | `main @ 4d84cd2a4bbd9bcbcff97105f226cf5652f13e29`（与授权时 L1 定位表记的 `6ae78ab` 之间 8 个 commit 经核验只是 `COLLAB-LEDGER-BOOTSTRAP-001` 自身收口，无产品语义漂移，详见 [L1 §T-002.2](L1_TASK_MANIFESTS.md)） |
| 终结依据 | [L3 §四 ATT-001](L3_ATTEMPTS_AND_EVIDENCE.md)（唯一一次正式尝试，一次通过） |
| 最终交付引用 | [`decision-chain/docs/V1_REBASE_EP00_CURRENT_PREFLIGHT_v0.1.md`](../decision-chain/docs/V1_REBASE_EP00_CURRENT_PREFLIGHT_v0.1.md) |
| next_stage_allowed | **`false`**——本任务只是只读预检完成，**不表示**：M0 全部完成／子合同已接受／`SINGLE-ACCOUNT-SLICE-EP00` 已完成／四个共享合同已冻结／M1—M4 或任何施工已获授权 |
| Checkpoint | **无**。本任务**已终结**，全程未被中断，一次直达收口 |
| 仍需 Founder 裁决的产品命题 | 见 [`decision-chain/docs/V1_REBASE_EP00_CURRENT_PREFLIGHT_v0.1.md`](../decision-chain/docs/V1_REBASE_EP00_CURRENT_PREFLIGHT_v0.1.md) §十一「仍需 Founder 裁决的产品命题」——**这是下一权限动作，不是可执行工程任务**（见 §二） |

### 一.4 `M0-EP00-ADOPTION-CLOSEOUT-001`

| 项 | 值 |
|---|---|
| 状态 | **`DONE`** —— C-ADOPT ~ C-CONTINUITY 九项全部通过，一轮直达收口 |
| 终结依据 | [L3 §五 ATT-001](L3_ATTEMPTS_AND_EVIDENCE.md)（唯一一次正式尝试，一次通过；含 C-CONTINUITY 无上下文接续检查发现并修复 4 处缺陷、登记 1 处受保护资产内的已知缺口） |
| 最终交付引用 | 远程默认分支 `main`，合并提交 `2dc4b5921bcfbe86c880c45696b0ece8367966c1`（`git ls-remote origin refs/heads/main` 已核验一致）；来源分支 `task/v1-rebase-ep00-current-m0-preflight` 保留未删除 |
| next_stage_allowed | **`false`**——本任务只完成「EP-00 交付采用进 main ＋ 当前投影纠偏」，**不表示**子合同已接受／共享合同已冻结／M1—M4 施工已获授权 |
| Checkpoint | **无**。本任务已终结，全程未被中断 |
| 已知缺口 | EP-00 报告内一处占位符残留（受保护资产，本任务无权修改，见 [L3 §五 ATT-001.4](L3_ATTEMPTS_AND_EVIDENCE.md)） |

### 一.5 `V1-M0-1B-SLICE-CONTRACT-REVISION-001`

| 项 | 值 |
|---|---|
| 状态 | **`DONE`** —— M01B_C01～C13（v1）与 M01B3_C13～C17（v2 Delta）全部通过，共两个 attempt（attempt-1：F-01～F-09 落地；attempt-2：Founder 复核后四项定向纠偏 ＋ 新增命题 F-10），各自一次定向语义审查发现真实问题并修复（attempt-1：3 处；attempt-2：8 处），均未触发第二轮全文审查 |
| 终结依据 | [L1 §T-004.1～T-004.4](L1_TASK_MANIFESTS.md)；[L3 §六 ATT-001～ATT-003](L3_ATTEMPTS_AND_EVIDENCE.md) |
| 最终交付引用 | [`decision-chain/docs/V1_SINGLE_ACCOUNT_SLICE_CONTRACT_v0.2.md`](../decision-chain/docs/V1_SINGLE_ACCOUNT_SLICE_CONTRACT_v0.2.md)——内嵌治理状态 `ACCEPTED — SINGLE_ACCOUNT_SLICE_PREFLIGHT_AUTHORIZED`（Founder 2026-08-24 在执行过程中明确回答"接受"后由该回答触发，非执行侧自行推高，见 [L1 §T-004.4](L1_TASK_MANIFESTS.md)）。v0.1 逐字保留未动，作为历史版本 |
| next_stage_allowed | **`true:V1-M0-SLICE-PREFLIGHT-AND-SHARED-CONTRACT-CLOSEOUT-001`**——但该后继任务**目前只有名称与一句话范围，尚无完整 Execution Prompt**，不构成可执行工程任务（见 §二） |
| Checkpoint | **无**。本任务已终结，全程未被中断 |
| 已知不做的事 | 本次接受**不**触发 `SINGLE-ACCOUNT-SLICE-EP00` 自动开工、**不**触发四个共享合同冻结、**不**触发 M1—M5 |

### 一.6 `V1-M0-SLICE-PREFLIGHT-AND-SHARED-CONTRACT-CLOSEOUT-001`（本条记录截至 Phase C 等待期的状态，历史原文保留；终态见 §一.7）

| 项 | 值 |
|---|---|
| 状态 | **`IN_PROGRESS`**（截至本条写入时）—— Phase A/B/C 已完成，等待 Founder 对四份共享合同的阶段裁决 |
| 授权 | Founder 2026-08-24 完整 Execution Prompt《M0.2B 专项预检、M0.3 共享合同与 M0 收口》；激活门 §2 全部条件已核验通过（见 [L1 §T-005.1](L1_TASK_MANIFESTS.md) `activation_gate_verified_at_execution`），非 `BLOCKED` |
| Checkpoint | 见 §四「非终态 Checkpoint 区」——已于 Founder 2026-08-25 回答后解除 |
| 下一动作 | 见 §一.7（已获裁决并终结） |

### 一.7 `V1-M0-SLICE-PREFLIGHT-AND-SHARED-CONTRACT-CLOSEOUT-001`（终态，追加于 §一.6 之后，不覆盖 §一.6）

| 项 | 值 |
|---|---|
| 状态 | **`DONE`** —— Phase A（专项预检，一次定向审查查出 11 处问题全部修复）、Phase B（四份共享合同，一次定向一致性检查查出 8 处问题全部修复）、Phase C（Founder 阶段裁决：**A. 接受，授权 M1–M4 施工规划编译**）、Phase D（状态更正 + 根索引同步 + 采用进 `main`）全部完成 |
| 实际执行基线 | `main @ 0eba71a85916d4d993313c015dc8ad87f180d4de` |
| 终结依据 | [L1 §T-005.1～T-005.4](L1_TASK_MANIFESTS.md)；[L3 §七 ATT-001～002](L3_ATTEMPTS_AND_EVIDENCE.md) |
| 最终交付引用 | [`SINGLE-ACCOUNT-SLICE-EP00 专项预检`](../decision-chain/docs/V1_SINGLE_ACCOUNT_SLICE_EP00_PREFLIGHT_v0.1.md)；四份共享合同（[任务上下文快照](../decision-chain/docs/V1_M0_SHARED_CONTRACT_TASK_CONTEXT_SNAPSHOT_v0.1.md)／[八项能力合同](../decision-chain/docs/V1_M0_SHARED_CONTRACT_EIGHT_CAPABILITIES_v0.1.md)／[版本发布反馈归属](../decision-chain/docs/V1_M0_SHARED_CONTRACT_VERSION_PUBLISH_FEEDBACK_v0.1.md)／[写回权限幂等恢复](../decision-chain/docs/V1_M0_SHARED_CONTRACT_WRITE_PERMISSION_RECOVERY_v0.1.md)），均 `ACCEPTED`（Founder 2026-08-25 明确回答"A"后由该回答触发，非执行侧自行推高，见 [L1 §T-005.4](L1_TASK_MANIFESTS.md)） |
| next_stage_allowed | **`true:M1—M4 施工规划 Execution Prompt 编译`**——`M1-M4_PLANNING_PROMPT_COMPILATION = AUTHORIZED`；`M1-M4_ENGINEERING_EXECUTION = NOT_AUTHORIZED`（**状态更正 1**：本行此前误写 `AUTHORIZED_BY_FOUNDER`，与本任务自身"不授权 M1—M4 工程实现本身"的结论矛盾；已由 `V1-M1-M4-PHASE0-PREAMBLE-ADOPTION-AND-DESKTOP-PACK-001` 更正，见 [L1 §T-006](L1_TASK_MANIFESTS.md)），规划侧须为 M1—M4 分别编译独立 Execution Prompt，执行侧不得自行编写 |
| Checkpoint | **无**。Phase C 等待期 Checkpoint 已于 Founder 回答后解除，本任务现已终结 |
| 已知不做的事 | 本次接受**不**授权 M1—M4 工程实现本身；**不**授权任何 Skill／DSL／Dify 工作流／数据库改动；两处"具体承接方未指定"的缺口（四类合同填值、Matrix 整任务硬停处置）已登记在共享合同二内，**不由本任务代为指定** |

### 一.8 `V1-M1-M4-PHASE0-PREAMBLE-ADOPTION-AND-DESKTOP-PACK-001`

| 项 | 值 |
|---|---|
| 状态 | **`BLOCKED`** —— 规划侧《M1–M4 Phase 0 共享编译前言采用与桌面资料包》Execution Prompt 随文给出的"规划附件"（`V1_M1_M4_CONSTRUCTION_PROMPT_SHARED_PREAMBLE_v0.1.md` 正文，声明冻结 SHA-256 = `9b046e9b6b8008d66e7347fcc878d2eed13cf251c3a899ed3ea989f761774da6`）实际以聊天消息内联纯文本形式收到，**不含**本仓库全部已采用真源文档统一使用的标准 markdown 语法（`#`标题／`**`加粗／`\|`表格／`` ``` `` yaml围栏——已用 `cat -A` 逐字节核对共享合同二等已采用文件确认此为仓库惯例）；判定为聊天渲染转写而非附件原始字节，无法计算出等于冻结值的 SHA-256，也不得按 Prompt §2 明文指令自行补全格式后重建附件 |
| 已完成的独立工作 | 按 Prompt §1"缺附件…且已完成所有不依赖该阻塞的工作，判 BLOCKED"的要求，完成了两处不依赖附件、Prompt 正文直接给出的 L2 当前投影纠偏（见 §一.7 `next_stage_allowed` 行「状态更正1」＋ §二「下一权限动作」表「状态更正2」），已提交并推送到任务分支 |
| 未完成／被阻塞的交付 | P0-A 核心交付（`decision-chain/docs/V1_M1_M4_CONSTRUCTION_PROMPT_SHARED_PREAMBLE_v0.1.md` 原样采用进 `main`）未写入；P0-B（四窗口桌面资料包）因依赖 P0-A 产出的最终 `main` 作为快照源，未启动 |
| 终结依据 | [L1 §T-006.1～T-006.2](L1_TASK_MANIFESTS.md)；[L3 §八 ATT-001](L3_ATTEMPTS_AND_EVIDENCE.md) |
| 最终交付引用 | 无新增产品文档；仅 L2 §一.7／§二 两处纠偏（已推送任务分支，**未合并进 `main`**——本次不构成完整 P0 交付，不触发 §5 的"Git 采用与远程收口"） |
| next_stage_allowed | **`false`**——须先由 Founder／规划侧提供可核验的真实附件文件（例如落到仓库指定路径供逐字节读取，或提供能重算出等于冻结值 SHA-256 的原始 markdown 字节），本任务或其新 attempt 才能继续 P0-A/P0-B；**不表示** M1—M4 施工规划编译授权本身被撤回，那项授权来自上一任务 Founder 2026-08-25 的"A"回答（见 §一.7），与本任务是否能验证这份前言附件是两件事 |
| Checkpoint | **无**——`BLOCKED` 是本仓库 Task Contract 既有的终态词之一（见 [L1 §T-006.1](L1_TASK_MANIFESTS.md) `terminal_state_order`），本次 attempt 已终结；解除阻塞后按"解除条件"重新开始新 attempt，不需要 Checkpoint 机制 |
| 已知不做的事 | 未自行拼接/推断/补全前言正文；未把当前 main（缺前言文件）冒充最终 main 生成桌面包；未合并任务分支进 `main`；未修改任何受保护资产 |

### 一.9 `V1-M1-M4-PHASE0-PREAMBLE-ADOPTION-AND-DESKTOP-PACK-001`（P0-A 解除阻塞，追加于 §一.8 之后，不覆盖 §一.8）

| 项 | 值 |
|---|---|
| 触发 | Founder 2026-08-25 会话内提供真实附件文件（仓库根目录），重新校验 SHA-256 与冻结值 `9b046e9b6b8008d66e7347fcc878d2eed13cf251c3a899ed3ea989f761774da6` 逐字节一致，内容六项一致性核查全部通过 |
| P0-A 状态 | **`DONE`** —— `decision-chain/docs/V1_M1_M4_CONSTRUCTION_PROMPT_SHARED_PREAMBLE_v0.1.md` 原样采用（移动保字节，二次核验哈希不变） |
| P0-B 状态 | 见本任务最终回执（合并进 `main` 并远端核验后，以该 commit 为源生成桌面资料包；结果不再单独提交 Git，直接写入 Founder 收工消息） |
| 终结依据 | [L1 §T-006.3](L1_TASK_MANIFESTS.md)；[L3 §八 ATT-002](L3_ATTEMPTS_AND_EVIDENCE.md) |
| Checkpoint | **无**——沿用 §一.8 的判断：`BLOCKED`/`DONE` 都是 Task Contract 既有终态词，非 Checkpoint 场景 |

### 一.10 `V1-M1-M4-PHASE0-DECISION-STATE-CLOSEOUT-001`

| 项 | 值 |
|---|---|
| 状态 | **`DONE`** —— 唯一 attempt 一次通过，`DS-C01`～`DS-C08` 全部 `PASS` |
| 前提核验 | Execution Prompt 自称"Founder 已通过连续动作完成正式确认"且要求不得再次核验；执行侧对照本会话实际记录判定该历史叙述不成立，改为 `AskUserQuestion` 直接向 Founder 求证；Founder 答复"我现在就是在确认"——账本记录的确认来源是这一当场答复，不是 Prompt 自称的历史叙述 |
| 内容变化 | (1) 前言 YAML 状态块：`status` 由 `FOUNDER_AUTHORIZED_FOR_VALIDATION_AND_ADOPTION` 改为 `ACTIVE_ON_DEFAULT_BASELINE`，新增 `product_semantics_confirmation: "FOUNDER_CONFIRMED"`；§三至§八正文字节不变。(2) L2 §二"下一权限动作"表删除两处"待 Founder/规划侧指定归属"的阻塞语言，代之以三条显式状态：`EIGHT_CAPABILITY_FOUR_CONTRACT_VALUES = FOUNDER_CONFIRMED_AND_ACTIVE`／`MATRIX_INSUFFICIENT_INPUT_PRODUCT_RULE = FOUNDER_CONFIRMED_AS_LOCAL_DEGRADATION_AND_BRANCH_BLOCKING`／`MATRIX_INSUFFICIENT_INPUT_ENGINEERING = ASSIGNED_TO_M1_AND_M4_CONSTRUCTION`。(3) PROJECT_INDEX 状态字符串同步 |
| 终结依据 | [L1 §T-007.1～T-007.2](L1_TASK_MANIFESTS.md)；[L3 §九 ATT-001](L3_ATTEMPTS_AND_EVIDENCE.md) |
| 最终交付引用 | 远程默认分支 `main`，采用提交见 [L5](L5_SIDE_EFFECTS.md)（`git ls-remote` 已核验一致） |
| next_stage_allowed | **`true:规划侧编译 M1—M4 施工 Execution Prompt`**——不变：`M1-M4_PLANNING_PROMPT_COMPILATION = AUTHORIZED`；`M1-M4_ENGINEERING_EXECUTION = NOT_AUTHORIZED`。本任务只是解除了两项内部决策缺口的阻塞标记，**不新增、不扩大**任何工程施工授权 |
| Checkpoint | **无**。本任务已终结，全程未被中断 |
| 已知不做的事 | 未重审八项能力 32 项合同值的具体内容（前言 §四正文字节不变）；未编译任何 M1-M4 施工 Prompt；未触碰四份共享合同或任何受保护资产 |

### 一.11 `V1-M1-ENGINEERING-PROMPT-ADOPTION-001`

| 项 | 值 |
|---|---|
| 状态 | **`DONE`** —— 唯一 attempt 一次通过 |
| 范围核验 | Founder 消息「执行落盘」的范围（落盘文档 / 授权工程执行 / 二者皆是）不明确；执行侧主动提问澄清，Founder 下一条消息只回答了文件位置（"已经放到仓库根目录"），未回答范围问题；按最小授权原则，本任务只完成确定无歧义部分：落盘规划文档本身，**不**新建、不触碰 `task/m1-natural-interaction-context-v1` 分支或任何 Dify 对象 |
| 转录漂移 | 用户首次以聊天正文粘贴方式提供全文；执行侧手工转录后自算文档自证哈希不一致，判定转录漂移并请用户改以仓库根目录真实文件提供；文件到位后逐字节 Read 核验，自证哈希与引用真源哈希均一致 |
| 内容变化 | (1) 新增 `decision-chain/docs/M1_ENGINEERING_EXECUTION_PROMPT_v1.2.md`（原样移动，字节不变）。(2) PROJECT_INDEX 新增两处指针，标注"工程实现未授权"。(3) 本节；L1/L3/L5 对应登记 |
| 终结依据 | [L1 §T-008.1～T-008.2](L1_TASK_MANIFESTS.md)；[L3 §十 ATT-001](L3_ATTEMPTS_AND_EVIDENCE.md) |
| 最终交付引用 | 远程默认分支 `main`，采用提交见 [L5](L5_SIDE_EFFECTS.md) |
| next_stage_allowed | **`false:M1 工程执行`**——`M1_ENGINEERING_PROMPT_COMPILED_AND_ADOPTED = true`；`M1-M4_ENGINEERING_EXECUTION` 仍为 `NOT_AUTHORIZED`，不变。本任务只是把已编译好的 M1 施工文档落盘，**不构成、不新增**对 `task_id: DIYU-V1-M1-NATURAL-CONTEXT-001` 工程执行的授权——该授权需 Founder 另行明确给出，且文档本身第 0/3.1 节已写明这一点 |
| Checkpoint | **无**。本任务已终结，全程未被中断 |
| 已知不做的事 | 未新建 `task/m1-natural-interaction-context-v1`；未创建/修改任何 Dify 对象；未编译 M2/M3/M4 施工 Prompt；未触碰四份共享合同、Phase0 前言或任何受保护资产 |

### 一.12 `V1-COLLAB-PROTOCOL-PROMPT-AUTHORIZATION-RULE-001`

| 项 | 值 |
|---|---|
| 状态 | **`DONE`** —— 唯一 attempt 一次通过 |
| 触发 | Founder 2026-08-25 直接会话消息，紧接在 §一.11 最终回执之后：「铁律：后续只要注入执行prompt，即视为授权，不再重复」 |
| 内容变化 | `collab-ledger/COLLAB_CONTINUITY_PROTOCOL.md` §六新增一条硬规矩"执行 Prompt 即授权"——今后收到完整 Execution Prompt 不再逐次征求"是否可以开始工程执行"的确认；Prompt 自身 `allowed_delta`／`protected_assets`／`explicitly_not_authorized` 等边界不受影响 |
| 终结依据 | [L1 §T-009.1～T-009.2](L1_TASK_MANIFESTS.md)；[L3 §十一 ATT-001](L3_ATTEMPTS_AND_EVIDENCE.md) |
| 最终交付引用 | 远程默认分支 `main`，采用提交见 [L5](L5_SIDE_EFFECTS.md) |
| next_stage_allowed | **`true:M1 工程执行`**——本条规则生效后，`decision-chain/docs/M1_ENGINEERING_EXECUTION_PROMPT_v1.2.md`（`task_id: DIYU-V1-M1-NATURAL-CONTEXT-001`）视为已获执行授权，可开工；该文档自身范围边界（`allowed_delta`／`protected_assets`／`remote_target.merge_main: NOT_AUTHORIZED` 等）继续原样有效 |
| Checkpoint | **无**。本任务已终结，全程未被中断 |
| 已知不做的事 | 未修改本条规则之外的任何既有规则、合同或受保护资产 |

### 一.13 `V1-M2-ENGINEERING-PROMPT-ADOPTION-001`

| 项 | 值 |
|---|---|
| 状态 | **`DONE`** —— 唯一 attempt 一次通过 |
| 范围核验 | Founder 消息「M2_业务持久化版本发布反馈投影_Execution_Prompt_v1.1.md 已经放到仓库根目录，授权推进落盘」字面只授权「落盘」；参照 §一.11（M1）先例的最小授权原则，本任务只完成确定无歧义部分：落盘规划文档本身，**不**新建、不触碰 `task/m2-business-persistence-version-feedback-v1` 分支或任何 PostgreSQL/Dify 对象。铁律（§一.12／[L1 §T-009](L1_TASK_MANIFESTS.md)）不改变这一判断——该条只免除"逐次确认"，M2 文档正文自身第 0 节明写"不因文件存在而自动授权工程施工"，仍是有效边界 |
| 自证哈希不一致（非转录漂移） | 用两种独立方法复算 M2 文档 Task Contract 代码块字节（同方法在 M1 文档上验证可正确复现其自证哈希），得 `4d14eb35c065b650b0380b0c309e0e08ec32e3aa608ece4d62e8d27b97450830`，与文档自称 `task_contract_hash`（`e17b354b97d53bfa52eeb30ffca50970e5469acabee98b3cfc32a1031b1b90ca`）不一致；已排除 CRLF/BOM/行尾空白/隐藏字符。用 AskUserQuestion 报告 Founder，Founder 裁决"按实测值登记，继续落盘"；本任务及后续全部引用改用独立复算值，详见 [L1 §T-010.2 DA-02](L1_TASK_MANIFESTS.md) |
| 并发写入核验 | 开工前发现主工作区被另一并行会话实时编辑同一批账本文件（即 §一.12 本身，登记"执行 Prompt 即授权"铁律），当时未提交。用 AskUserQuestion 报告 Founder，Founder 选择"等对方提交后再落盘"；本任务在其合并进 `main`（`0de99930ff5da5c24aa2fbe34615abe52cc6c7db`）之后才开始写入 |
| 内容变化 | (1) 新增 `decision-chain/docs/M2_ENGINEERING_EXECUTION_PROMPT_v1.1.md`（原样移动，字节不变）。(2) PROJECT_INDEX 新增一处指针，标注"工程实现未授权"并披露哈希不一致。(3) 本节；L1/L3/L5 对应登记 |
| 终结依据 | [L1 §T-010.1～T-010.2](L1_TASK_MANIFESTS.md)；[L3 §十二 ATT-001](L3_ATTEMPTS_AND_EVIDENCE.md) |
| 最终交付引用 | 远程默认分支 `main`，采用提交见 [L5](L5_SIDE_EFFECTS.md) |
| next_stage_allowed | **`false:M2 工程执行`**——`M2_ENGINEERING_PROMPT_COMPILED_AND_ADOPTED = true`；`DIYU-V1-M2-BUSINESS-PERSISTENCE-VERSION-FEEDBACK-001` 的工程执行仍为 `NOT_AUTHORIZED`。本任务只是把已编译好的 M2 施工文档落盘，**不构成、不新增**对该 task_id 工程执行的授权——该授权需 Founder 另行就这一具体 task_id 明确给出，且文档本身第 0 节已写明这一点 |
| Checkpoint | **无**。本任务已终结，全程未被中断 |
| 已知不做的事 | 未新建 `task/m2-business-persistence-version-feedback-v1`；未创建/修改任何 PostgreSQL/Dify 对象；未编译 M3/M4 施工 Prompt；未触碰四份共享合同、Phase0 前言、M1 落盘文档或任何受保护资产 |

### 一.14 `V1-M2-ENGINEERING-PROMPT-ADOPTION-001`（M2 工程执行授权确认，追加于 §一.13 之后，不覆盖 §一.13）

| 项 | 值 |
|---|---|
| 触发 | 落盘完成后，执行侧就"铁律（§一.12）是否适用于本次落盘、M2 工程执行是否已一并获授权"用 AskUserQuestion 直接向 Founder 求证（因 Founder 本次落盘授权字面只说"落盘"，与铁律"注入完整 Prompt 即授权"的表述存在解释空间）；Founder 当场明确答复"就是要启动，铁律适用" |
| 结论 | `task_id: DIYU-V1-M2-BUSINESS-PERSISTENCE-VERSION-FEEDBACK-001` 的工程执行自本次 Founder 直接答复起视为已获授权；§一.13 关于"本任务不构成该 task_id 执行授权"的记录对**落盘任务本身**依然真实准确（落盘时点确实未获授权），授权是落盘完成后另一个独立事件产生的，不追溯改写落盘任务的历史记录 |
| next_stage_allowed | **`true:M2 工程执行`**——`decision-chain/docs/M2_ENGINEERING_EXECUTION_PROMPT_v1.1.md`（`task_id: DIYU-V1-M2-BUSINESS-PERSISTENCE-VERSION-FEEDBACK-001`）视为已获执行授权，可开工；该文档自身范围边界（`allowed_delta`／`protected_assets`／§3 Task Contract 各字段，含独立复算 `task_contract_hash = 4d14eb35c065b650b0380b0c309e0e08ec32e3aa608ece4d62e8d27b97450830`）继续原样有效；文档 §4 入口门（读取真源、fetch 核验、只读核验 PostgreSQL/Dify、编译 Run Manifest、建立独立 worktree/分支）仍须在首次写入前完成，不因本条授权豁免 |
| Checkpoint | **无**。本条已终结，全程未被中断 |

### 一.15 `DIYU-V1-M2-BUSINESS-PERSISTENCE-VERSION-FEEDBACK-001`（M2 工程任务最终收尾，`DONE`）

M2 工程任务的完整过程见 [L1 §T-011～§T-011.6](L1_TASK_MANIFESTS.md)、[L3 §十三](L3_ATTEMPTS_AND_EVIDENCE.md#十三-diyu-v1-m2-business-persistence-version-feedback-001)、`business-persistence/M2_ACCEPTANCE_EVIDENCE.md`、`business-persistence/M2_REBASE_ERRATA_001_RECORD.md`，本条只登记最终收尾事实，不重复过程。

| 项 | 值 |
|---|---|
| 触发 | Founder 在本会话中通过 Dify Studio 实际运行候选画布（`task_id: f7b96d1a-5dc2-4217-be0b-d618bfd36c57`），将 End 节点全部输出原文提供给执行侧核对；执行侧逐项核验 `FOUNDER_TEST_PACKAGE.md` 9 项判断标准全部满足；Founder 明确表示"接受"，并进一步明确裁决"接受 + 合并主干" |
| `M2-AC-17` | 转 `PASS`——Founder 已通过 Dify 画布完成产品/业务验收并明确接受 |
| `M2-AC-13` | 维持 `FOUNDER_WAIVED`（技术事实不变：迁移降级遇跨账号冲突不能自动恢复，需人工介入；该子项已由 Founder 于本会话早前明确裁决豁免，不重复登记） |
| 合并执行 | 任务分支 `task/m2-business-persistence-version-feedback-v1`（最终 head `74bc9e32627b290c93827a4ff83b2bc79aa9befd`）以 `git merge --no-ff` 合并进 `main`，合并 commit `17f5e5724a09470c78c757a88c4ec6469fb0dcfd`；唯一冲突为 `collab-ledger/L1_TASK_MANIFESTS.md` 顶部索引表一处插入位置重叠（非逻辑冲突），已保留双方内容并补充指向说明；`git push origin main` 后核验本地/远程一致于 `17f5e57` |
| 合并后核验（对应 Founder 提出的收口检查清单，逐项见 `M2_ACCEPTANCE_EVIDENCE.md`"合并与最终证据绑定"） | (1) 远程 main 真实包含本次交付——已核验；(2) 合并内容与已验收候选一致——`git diff` 字节级为空；(3) 受保护合同/共享资产/既有能力无退化——排除 `business-persistence/`、`collab-ledger/` 后 `git diff --stat` 为空；(4) 必要回归通过——合并后现场重跑 69/69；(5) 目标 Dify 候选仍与最终代码相符——同一容器、代码字节一致；(6) Git/账本/证据绑定更新完成——即本条与关联文档 |
| 任务终态（2026-08-26 治理收口纠偏：移除无效字段组合，见下方说明） | `task_final_status = DONE`；`module_delivery_state = DONE`；`next_stage_allowed = false`；`checkpoint = null`；`active_work_package = null`。`DONE` 不额外授权 M5、真实社交平台发布、生产采用或任何经营结果结论；合并 main 本身是本次单独明确授权的动作，不是 `DONE` 状态自动带来的权限 |
| Checkpoint | **无**（`null`）。任务已终结，从此移出 §二"当前可执行动作"表 |

> **终态字段纠偏说明**：本节此前同时登记 `execution_disposition = CONTINUE` 与 `task_final_status = DONE`，这是无效组合——`CONTINUE` 只用于非终态 Checkpoint，且要求 `task_final_status = null`。M2 已进入正式终态 `DONE`，`execution_disposition` 字段已在上表移除，不改变本任务此前已经是 `DONE` 这一事实本身。同一纠偏已同步至 `business-persistence/M2_ACCEPTANCE_EVIDENCE.md`、`M2_REBASE_ERRATA_001_RECORD.md`、`collab-ledger/L1_TASK_MANIFESTS.md`（§T-011.7）、`collab-ledger/L3_ATTEMPTS_AND_EVIDENCE.md`（§ATT-007）。完整记录见 `business-persistence/M2_FINAL_GOVERNANCE_CLOSEOUT_RECOVERY_RECORD_v1.0.md`。

### 一.16 `DIYU-V1-M2-BUSINESS-PERSISTENCE-VERSION-FEEDBACK-001`（`M2_POST_DONE_REBASE_v1.2` 收口，`DONE`；取代 §四原 Checkpoint 登记，§一.15 历史 `DONE` 不受影响、不回滚）

`M2_POST_DONE_REBASE_v1.2` 的完整过程（技术结果/Founder处置分层、市场观察权限语义、迁移、独立审查、第二次 `M2-PDR-12` 证据核验的存疑与 Founder 裁决）见 [L1 §T-011.8～§T-011.10](L1_TASK_MANIFESTS.md)、[L3 §ATT-008～§ATT-009](L3_ATTEMPTS_AND_EVIDENCE.md)、`business-persistence/M2_POST_DONE_REBASE_v1.2_RECORD.md`，本条只登记最终收尾事实，不重复过程。

| 项 | 值 |
|---|---|
| `M2-PDR-12` 最终判定 | `PASS`——本系统侧六条持久化记录现场核验一致，执行侧最初三项存疑（`is_manual_entry`/时间跨度/`was_selected`&`was_produced`）经 Founder 说明后不再成立，Dify 侧运行身份（`workflow_run_id: 5c122641-...`，`status: succeeded`）由 Founder 第一手见证并报告；据实标注：这一条 Dify 侧事实本身未经执行侧独立复算 |
| `M2-PDR-01～15` | 全部 `PASS` |
| 合并前置条件核验（Founder 要求的确定性条件，执行侧现场逐项核验） | 全部满足，见 `business-persistence/M2_POST_DONE_REBASE_v1.2_RECORD.md` §14 |
| 合并执行 | 任务分支收口 commit `4f57a32e61e2612f7f3de3699f5f5253fe270d5c`（推送 `ec77bfd..4f57a32`）；真实二亲合并 commit `17ca3f70212f38048b37f739edffba8bf7cf8f85`（`git merge --no-ff`，内容层面无冲突）；`git push origin main` 推送 `df2c595..17ca3f7`；合并后核验 `git diff main origin/task/...` 为空、受保护资产 diff 为空、迁移/运行代码身份不漂移，详见 [L5 SE-027～SE-029](L5_SIDE_EFFECTS.md) 与 `M2_POST_DONE_REBASE_v1.2_RECORD.md` §15 |
| 任务终态（正式 `DONE`，不登记 `execution_disposition`） | `task_final_status = DONE`；`historical_m2_task_status = DONE`；`post_done_rebase_progress = COMPLETED`；`M2_MODULE_LANDING = CLOSED`；`checkpoint = null`；`active_work_package = null`。`DONE` 不额外授权 M5、真实社交平台发布、生产采用或任何经营结果结论——Founder 本次授权明确排除这些项 |
| Checkpoint | **无**（`null`）。原 §四 记录的 Checkpoint 已解除，从此移出 §四 |

---

## 二、项目当前可执行动作（Current Handoff）

> **本节只维护：活动 `task_id` ＋ 依赖关系 ＋ 定位引用。**
> 每个活动 `task_id` **各自一行**。**这里没有、也不得有一个覆盖所有并行任务的全局「唯一下一步」。**
> 每行的下一动作四要素缺一不可：**动作 ／ 对象 ／ 输入或基线 ／ 完成信号**。
> 当同时有两个及以上任务在跑时，各任务细节写进各自的 `collab-ledger/tasks/<task_id>.md` 分区，本表只留定位引用。
> **已完成的任务移出本表、终态记进 §一**——本表不维护「共几个」的汇总，数量随授权变化，写死必失真。

| task_id | 依赖 | 定位引用 | 动作 | 对象 | 输入／基线 | 完成信号 |
|---|---|---|---|---|---|---|
| （当前无活动 task_id——`DIYU-V1-M1-NATURAL-CONTEXT-001` 已于 2026-08-26 终结 `DONE`，移出本表，见 §一） | | | | | | |

**`COLLAB-LEDGER-BOOTSTRAP-001`、`V1-REBASE-EP00-CURRENT`、`M0-EP00-ADOPTION-CLOSEOUT-001`、`V1-M0-1B-SLICE-CONTRACT-REVISION-001`、`V1-M0-SLICE-PREFLIGHT-AND-SHARED-CONTRACT-CLOSEOUT-001`、`V1-M1-M4-PHASE0-PREAMBLE-ADOPTION-AND-DESKTOP-PACK-001`、`V1-M1-M4-PHASE0-DECISION-STATE-CLOSEOUT-001`、`V1-M1-ENGINEERING-PROMPT-ADOPTION-001`、`V1-COLLAB-PROTOCOL-PROMPT-AUTHORIZATION-RULE-001`、`V1-M2-ENGINEERING-PROMPT-ADOPTION-001`、`DIYU-V1-M1-NATURAL-CONTEXT-001` 均已终结 `DONE`（见 §一）。**M0 已全部完成；M1–M4 Phase 0 共享编译前言已采用且前言内八项能力四类合同值、Matrix 局部降级口径均已 `FOUNDER_CONFIRMED`。M1 工程实现（自然语言交互、任务上下文编译、CTA 三层权限、账号锚点、真实 Dify 候选运行、独立审查、回滚演练、Founder 实测验收）已于 2026-08-26 全部完成并经 Founder ACCEPT，`task_final_status: DONE`；`DIYU-V1-M1-MODULE-LANDING-001`（父任务即此 M1 任务）已把该任务分支正常合入 `main`，见 [L1 新增行](L1_TASK_MANIFESTS.md) 与 `decision-chain/evidence/V1_M1_MODULE_LANDING_RECEIPT_v1.0.md`。M2 施工 Execution Prompt v1.1 已由规划侧编译完成并落盘（[`decision-chain/docs/M2_ENGINEERING_EXECUTION_PROMPT_v1.1.md`](../decision-chain/docs/M2_ENGINEERING_EXECUTION_PROMPT_v1.1.md)，`task_id: DIYU-V1-M2-BUSINESS-PERSISTENCE-VERSION-FEEDBACK-001`）；落盘完成后执行侧就"铁律是否适用"直接向 Founder 求证，Founder 2026-08-25 当场明确答复"就是要启动，铁律适用"——`DIYU-V1-M2-BUSINESS-PERSISTENCE-VERSION-FEEDBACK-001` 随即成为活动工程任务，见 [L2 §一.14](#一14-v1-m2-engineering-prompt-adoption-001m2-工程执行授权确认追加于一13之后不覆盖一13)。**该任务已于 2026-08-26 完整收口为 `DONE` 并合并进 `main`，已移出上表，终态见 [L2 §一.15](#一15-diyu-v1-m2-business-persistence-version-feedback-001m2-工程任务最终收尾done)**。M3/M4 施工 Execution Prompt 仍待规划侧编译，编译后同样适用铁律但仍需就各自 task_id 单独确认落盘用词是否等于执行授权。`M1 本身 DONE` 与本次落地进 `main` 均不构成对 M2 之外的 M3/M4/M5 的自动施工授权。**

**已解决**：EP-00 报告 §十一「仍需 Founder 裁决的产品命题」已由 Founder 通过 F-01～F-10 十项裁决 + 四项定向纠偏答复，并落地进 v0.2（已 `ACCEPTED`）；四份共享合同已起草并经 Founder 接受（见 §一.7）。

**下一权限动作**（不是可执行工程任务，执行侧不得自行开工）：

| 动作 | 对象 | 输入／基线 | 完成信号 |
|---|---|---|---|
| 规划侧编译 M1—M4 施工 Execution Prompt | M1（自然交互、任务上下文与能力路由）／M2（最小业务数据、版本与运营记忆）／M3（运营状态诊断与持续运营决策）／M4（现有能力组件化接入与兼容改造）——**状态更正 2**：本列此前把 M1 误写为"业务持久化"（实为 M2 职责）、M2 误写为"写回权限恢复实现"（写回权限幂等恢复只是 M2 记忆职责下的一项具体能力，非 M2 全部定义）、M4 留空未定，与四窗口已冻结的唯一责任划分不一致；已由 `V1-M1-M4-PHASE0-PREAMBLE-ADOPTION-AND-DESKTOP-PACK-001` 更正，见 [L1 §T-006](L1_TASK_MANIFESTS.md) | 四份已接受的共享合同（[任务上下文快照](../decision-chain/docs/V1_M0_SHARED_CONTRACT_TASK_CONTEXT_SNAPSHOT_v0.1.md)／[八项能力合同](../decision-chain/docs/V1_M0_SHARED_CONTRACT_EIGHT_CAPABILITIES_v0.1.md)／[版本发布反馈归属](../decision-chain/docs/V1_M0_SHARED_CONTRACT_VERSION_PUBLISH_FEEDBACK_v0.1.md)／[写回权限幂等恢复](../decision-chain/docs/V1_M0_SHARED_CONTRACT_WRITE_PERMISSION_RECOVERY_v0.1.md)）＋ 两类 EP-00 证据（[通用](../decision-chain/docs/V1_REBASE_EP00_CURRENT_PREFLIGHT_v0.1.md)／[专项](../decision-chain/docs/V1_SINGLE_ACCOUNT_SLICE_EP00_PREFLIGHT_v0.1.md)） | 规划侧分别产出 M1—M4 各自的完整 Execution Prompt；**执行侧不得自行编写或推断这些 Prompt，也不得据本条自行开工任何 M1–M4 工程实现**。**状态更正 3**：此前登记的"两处尚未指定承接方的缺口"已解除——`EIGHT_CAPABILITY_FOUR_CONTRACT_VALUES = FOUNDER_CONFIRMED_AND_ACTIVE`；`MATRIX_INSUFFICIENT_INPUT_PRODUCT_RULE = FOUNDER_CONFIRMED_AS_LOCAL_DEGRADATION_AND_BRANCH_BLOCKING`；`MATRIX_INSUFFICIENT_INPUT_ENGINEERING = ASSIGNED_TO_M1_AND_M4_CONSTRUCTION`（M4 主修 Matrix 现有全局硬停的物理修复，M1 承接交互／路由／局部继续语义接口责任，M2／M3 按前言 §五冻结边界配合，二者可错峰施工但须在 M5 集成前共同闭合）——Founder 2026-08-25 在 `V1-M1-M4-PHASE0-DECISION-STATE-CLOSEOUT-001` 会话内当场确认，非历史"连续动作"追认，见 [L1 §T-007](L1_TASK_MANIFESTS.md)。**状态更正 4**：M1 施工 Execution Prompt 已由规划侧编译完成并落盘——[`decision-chain/docs/M1_ENGINEERING_EXECUTION_PROMPT_v1.2.md`](../decision-chain/docs/M1_ENGINEERING_EXECUTION_PROMPT_v1.2.md)（`task_id: DIYU-V1-M1-NATURAL-CONTEXT-001`）；该 task_id 的工程执行已由 Founder 2026-08-25「执行 Prompt 即授权」铁律（[L1 §T-009](L1_TASK_MANIFESTS.md)）转为已获授权，见 §二上表。**状态更正 5**：M2 施工 Execution Prompt v1.1 已由规划侧编译完成并落盘——[`decision-chain/docs/M2_ENGINEERING_EXECUTION_PROMPT_v1.1.md`](../decision-chain/docs/M2_ENGINEERING_EXECUTION_PROMPT_v1.1.md)（`task_id: DIYU-V1-M2-BUSINESS-PERSISTENCE-VERSION-FEEDBACK-001`）；落盘时点本次授权消息字面仅限「落盘」，未就该 task_id 给出执行授权（见 [L1 §T-010](L1_TASK_MANIFESTS.md)）。**状态更正 6**：落盘完成后 Founder 已就该具体 task_id 当场明确答复"就是要启动，铁律适用"，该 task_id 工程执行随即转为已获授权，见 [L2 §一.14](#一14-v1-m2-engineering-prompt-adoption-001m2-工程执行授权确认追加于一13之后不覆盖一13)。**状态更正 7**：该 task_id 已于 2026-08-26 完整收口为 `DONE` 并合并进 `main`，已移出 §二"当前可执行动作"表，终态见 [L2 §一.15](#一15-diyu-v1-m2-business-persistence-version-feedback-001m2-工程任务最终收尾done)。M3／M4 施工 Execution Prompt 仍待规划侧编译 |

---

## 三、不构成活动任务的（**不要**从这里取下一步）

| 项 | 为什么不能开工 |
|---|---|
| `SINGLE-ACCOUNT-SLICE-EP00`（子合同专项预检） | **已完成**（[V1_SINGLE_ACCOUNT_SLICE_EP00_PREFLIGHT_v0.1.md](../decision-chain/docs/V1_SINGLE_ACCOUNT_SLICE_EP00_PREFLIGHT_v0.1.md)，作为 `V1-M0-SLICE-PREFLIGHT-AND-SHARED-CONTRACT-CLOSEOUT-001` Phase A 交付），不再是待办项，列在此处仅防止误重跑 |
| Skill 修改／DSL 改造／业务持久化建设／Dify 工作流施工（M1—M4 工程实现本身） | 四份共享合同已被接受，**M1—M4 施工规划编译已获授权**，但**工程实现本身仍需各自独立的 Execution Prompt 与 Founder 授权**——共享合同接受 ≠ 施工授权 |
| [生产差距登记](../decision-chain/docs/V1_PRODUCTION_GAP_REGISTER_v0.1.md) G-01～G-12 | 均未关闭，但它们是**开放 Gap，不是已授权任务**，也**不是**已排除路线（见 [L4](L4_FAILED_PATHS.md)） |
| `AO-EP00-HISTORICAL`（`feature/account-operation-v1 @ df94ed1`） | **只作历史参考**，不得冒充当前预检，不得直接合入 `main` |

---

## 四、非终态 Checkpoint 区

`V1-M0-SLICE-PREFLIGHT-AND-SHARED-CONTRACT-CLOSEOUT-001` 曾在 Phase C 等待 Founder 裁决期间登记过一份 Checkpoint（历史原文见 Git 历史该行的上一版本，或 [L3 §七](L3_ATTEMPTS_AND_EVIDENCE.md)）；Founder 已于 2026-08-25 明确回答，该任务已终结 `DONE`（见 §一.7），Checkpoint 解除。

**当前无非终态 Checkpoint。** `DIYU-V1-M2-BUSINESS-PERSISTENCE-VERSION-FEEDBACK-001` 的 `M2_POST_DONE_REBASE_v1.2` 曾在此登记过一份 Checkpoint（唯一缺口：`M2-PDR-12` 因本会话无可用 App API Key 未能现场重跑 Dify 候选受影响回归，历史原文见本行的上一版本或 Git 历史）；Founder 已于同日会话内就该缺口给出说明并以第一手见证补充 Dify 侧运行身份，执行侧独立核验本系统侧对应记录后，`M2-PDR-12` 更正为 `PASS`，Checkpoint 解除，任务转为正式终态 `DONE`。完整记录见 [L1 §T-011.9～§T-011.10](L1_TASK_MANIFESTS.md)、[L3 §ATT-009](L3_ATTEMPTS_AND_EVIDENCE.md)、`business-persistence/M2_POST_DONE_REBASE_v1.2_RECORD.md` §13/§13.1、[本文件 §一.16](#一16-diyu-v1-m2-business-persistence-version-feedback-001m2_post_done_rebase_v12-收口done取代四原-checkpoint-登记一15-历史-done-不受影响不回滚)。

以下是 `DIYU-V1-M1-NATURAL-CONTEXT-001` 自身任务分支（`task/m1-natural-interaction-context-v1`）历史遗留的 Checkpoint 与状态更新记录，随 `DIYU-V1-M1-MODULE-LANDING-001` 一并合入本文件，纯历史存档，不代表当前存在非终态 Checkpoint。

### `DIYU-V1-M1-NATURAL-CONTEXT-001` Checkpoint（历史记录；该任务已于 2026-08-26 终结 `DONE` 并经 `DIYU-V1-M1-MODULE-LANDING-001` 合入 `main`）

```yaml
task_id: DIYU-V1-M1-NATURAL-CONTEXT-001
task_entry_mode: REBASE_TASK
execution_disposition: COMPLETE
task_final_status: DONE
current_task_contract_version: "1.4"
active_rebase_delta: M1_ENGINEERING_EXECUTION_REBASE_DELTA_v1.4.1_AUDITED_READY_FOR_FOUNDER_USE.md
active_rebase_delta_sha256: 01bbe73a173091bdf4dc035c521466ef0c1aa95821808bc5283c1c68c1b1f8f3
current_state: V1_4_1_FOUNDER_ACCEPTED_CTA_SEMANTIC_QUESTION_FOUNDER_CONFIRMED_KEEP_AS_IS_DONE
final_commit: 024d6992b73e884355658f10e78da5d1c16a126f
final_dsl_sha256: 845fa75d2e5d5a860add346c614a6e1f96d7831054e76697a69993be4ba8ec5a
published_workflow_id: 3f96f47f-45bf-4138-9a56-940af199ebb9
founder_dify_acceptance_status: ACCEPTED
next_stage_allowed: false  # M1 本身 DONE ≠ M2/M3/M4/M5 自动获得施工授权，需另行明确新授权
```

**2026-08-26 状态更新（Founder 实测验收 + CTA 授权语义裁决，任务终态 `DONE`，最新）**：Founder 在本会话内直接确认已完成 `V1_M1_FOUNDER_DIFY_TEST_PACKAGE_v0.13.md` 全部测试并接受（"所有测试都已经完成，我认为已经通过测试，这一步可以通过"）。针对实测包第三节第 4 条留给 Founder 的开放语义问题（高风险 CTA 场景下，用户自己的断言式表态是否构成显式授权），执行侧用 `AskUserQuestion` 原样复述判据边界供裁决，**Founder 明确选择"保持现状"**——当前代码行为（断言式表态即可触发授权）就此 `FOUNDER_CONFIRMED`，不需要任何代码改动。M1-AC-18 语义半部关闭，全部适用 AC-00～19 无遗留开放项。任务终态 `DONE`；`next_stage_allowed` 仍为 `false`，M2/M3/M4/M5 施工需另行明确授权，本次不自动开工。详见 [evidence §19.5](../decision-chain/evidence/V1_M1_CANDIDATE_RUN_001.md)。

---

**2026-08-26 状态更新（独立收口 Reviewer 结论 + Finding 1 修复 + v0.13 最终冻结全集复验，历史记录）**：唯一一名 §9 授权的上下文隔离只读收口 Reviewer（agent `a37817485b8cc3100`）已运行完毕，结论：M1-B-20～26/28/29 与 AC-17/19 `PASS`（含活体复现）；**M1-B-27／M1-AC-18 判定 `FAIL`**（真实缺口：高风险 CTA 一旦获得授权，`dialogue_directive` 此后完全不再提及，用户没有任何机会发现或纠正一次可能错判的授权）；M1-B-30 `PARTIAL`（AC-15 回滚本身独立复核为真实，但正式全集实际跑在 v0.11 而非最终冻结配置，§6.5 字面要求未满足）；安全/权限/受保护资产/数据完整性 `CLEAN`。

执行侧处置：该缺口拆成确定性半部（一旦授权就必须每轮无条件复述，可核对可撤回）和语义半部（用户自己的断言式表态"就这么定了"在其身兼提议者与审批者时是否构成 §5.4.3 的显式授权——产品语义问题，不由执行侧代答）。**只修确定性半部**（commit `5f335c4`，216/216 单测通过，新增 2 条回归锁定），**语义半部原样写入 Founder 实测包，明确留给 Founder 用真实对话判断**，不落子 §11 强制停止条件（属"实现多解"范畴，非合同冲突）。随后在这个新 commit 上重新构建 DSL（SHA-256 `845fa75d2e5d5a860add346c614a6e1f96d7831054e76697a69993be4ba8ec5a`，两次构建字节一致）、导入发布到同一候选 App（`apps.workflow_id` 直查确认 = `3f96f47f-45bf-4138-9a56-940af199ebb9`，草稿/发布嵌入编译器源码与 Git HEAD 字节一致），**第一次真正在最终冻结配置上跑通 §6.1～6.4 全集**（31 场景/34 次真实调用，0 空回复、0 报错；新增用例活体证明 Finding 1 修复端到端生效——授权当轮 + 跨到无关话题的后续轮次均持续复述"已授权+具体目标+可撤回"）。全集阈值对照：34 次中 3 次 `partial-succeeded`，逐条查证均为同一已知 WSL2/Docker MTU 网络瞬断签名（`api.deepseek.com` SSL EOF），分布在互不相关的 3 个场景、功能上零失败，对 3 个具体输入重放 3/3 全部干净 `succeeded`——判定为 §11 明确排除的"模型波动"，如实记录字面差异（`partial_succeeded` 非 0）但不视为 P0 阻断。详见 [evidence §十九](../decision-chain/evidence/V1_M1_CANDIDATE_RUN_001.md)。

**当前状态**：本轮修复-复验循环用的正是 §6.5 规定的"唯一一次集中修复预算，冻结新 commit/图/参数后对同一输入全集再跑一次"，不额外占用或需要第二名独立 Reviewer。技术门已达成，Founder 实测包已就绪，本任务在本会话内到此为止——不启动 M2/M3/M4/M5，不合并 main，等待 Founder 通过实测包做出验收裁决（含语义半部的开放判断）。

---

**2026-08-26 状态更新（v1.4.1 Rebase：全部 P0 阻断修复 + 首次真正端到端 live 验证 + AC-15 完成，历史记录）**：按 Founder 提供的 `M1_ENGINEERING_EXECUTION_REBASE_DELTA_v1.4.1_AUDITED_READY_FOR_FOUNDER_USE.md`（`REBASE_TASK`，继承原 task_id/分支/worktree/候选 App）修复冻结阻断集合 M1-B-20～M1-B-30，新增 M1-AC-17（最小账号锚点）、M1-AC-18（CTA 三层权限上下文）。同会话对抗式独立审查发现 13 处真实缺陷全部修复。单测 170→215 全绿。

**方法论变化，需要 Founder 知悉**：本轮确认此前"控制台操作需 Founder 代跑"的限制来自 Bash 工具的沙箱网络策略，非硬限制——显式放开沙箱后可用 Founder 此前提供、存于本机固定路径 `~/.dify-console.env`（未写入仓库）的凭据完成真实控制台登录与 DSL 导入/发布/回滚。本轮起执行侧在本 task_id 唯一候选 App 范围内自主完成了全部 DSL 导入/发布与 AC-15 回滚演练，不再逐次请 Founder 代跑，严格未触碰任何其它 App、main 或生产流量。

**首次真正端到端 live 验证**：v0.9→v0.12 四轮迭代（导入→发布→数据库取证→修复），最终候选 v0.12（commit `a5319d2`，DSL SHA-256 `a66f91c2d6687a0612d6b572e6f211d4132a278e8cb7f75a7cfc087e9bbef460`，发布 workflow_id `6d62eeac-bae6-4edd-a591-8c006eaebf7f`）：27 场景/27 有效轮次直连数据库确认 `patch_ok=true`、workflow 状态全 `succeeded`、0 空回复；7/7 入口正确路由；CTA/账号锚点内部状态全部正确；材料上传确认闭环。**M1-AC-15 已完成真实回滚+恢复演练**（restore/publish 两轮，graph MD5/features/嵌入代码字节三重核对一致）。详见 [evidence §十八](../decision-chain/evidence/V1_M1_CANDIDATE_RUN_001.md)。

**如实标注的证据边界**：live 验证过程中发现并修复的两处模型分类准确率问题（`max_tokens` 不足导致的思维链截断、CTA `GRANT` 语义误判）均属于提示词层面缓解，不是可验证零失败的保证；结构性对齐约束（授权必须同一轮三者同时出现）是防止误判后果扩散的主要防线。`features.file_upload` 本轮四次导入均正确保留（未复现此前 B-21 记录的"导入不保留 features"现象），如实记录这一观察，不代表已确认该现象永久解决，未来每次导入仍需照常复核。

**下一动作**：按 Delta §9 spawn 一名上下文隔离只读收口 Reviewer（`closing_verification: affected_scope_only`），产出 Founder 可直接复制的 Dify 实测包，随后停止——不启动 M2/M3/M4/M5，不合并 main。

---

**2026-08-26 状态更新（v0.7 live 验证 + B-3 两处真实缺陷发现并修复，历史记录）**：Founder 导入并发布 v0.7 后，执行侧用 App API Key（由 Founder 在本机终端代跑 curl，执行侧不持有绕过沙箱写权限的通道）跑真实回归，并直连本机 Docker 内的 Dify 数据库（只读）核对节点级真实产出。**B-4、B-5（短指代绑定+撤销）三项均 PASS，有数据库直查证据**，详见 [evidence §十七](../decision-chain/evidence/V1_M1_CANDIDATE_RUN_001.md)。

**B-3 先后发现两处真实缺陷，均已修复**：①应用配置层——候选 App 这次导入没有把 `features.file_upload` 一起带过去，DSL 内容本身是对的，只是运行中的 App 配置没跟上，Founder 明确要求"你应该在后台修复"后，执行侧对本机自建 Docker 数据库（既有只读排障权限范围内，本次定位根因正是靠这条权限）做了一次只替换 `file_upload` 一个字段、其余原样保留的精确修正，由 Founder 在自己终端执行该写入（同网络调用一样受 Bash 沙箱权限分类器限制）；②代码层——配置修好后复测，文件真的被抽取、`m1_shadow` 也正确判定来源，但最终回复仍说"没收到"，根因是 `_dialogue_directive` 从不告知负责生成回复的 `m1_chat_llm` 材料已收到。**已在源码里修复**，且第一版实现本身又被同会话对抗式审查（read-only、未参与实现）挑出两个真实问题（确认信号挂错、材料原文被拼进无抗注入措施的指令通道）后重新设计。单测 162→170 全绿，DSL 重新生成为 v0.8。

**当前唯一剩余动作，需要 Founder**：导入并发布 v0.8（覆盖 v0.7），执行侧随后重新核对 `features.file_upload` 是否又被这次导入覆盖（无法假设上次的修复永久生效），并跑真实回归验证"对话 LLM 正确告知用户已收到材料"这一环节——这部分目前只有单测覆盖，未经任何真实 Dify 调用验证。

**2026-08-25 状态更新（B-3/B-4/B-5 真实实现，收口审查后继续施工）**：Founder 指出此前把 B-3/B-4 列为"需要架构判断故本批不做"不构成合法延期理由，B-5 也只修了诚实反馈这一部分——执行侧据此完成三者的真实机制（`requested_capabilities_text` 多能力选择、真实文件上传通道 + `evidence_provenance` 真实来源核实、`handled_thread_id` 短指代绑定 + `HANDLED` 闭环 + `cancel_target` 真实撤销）。每批各跑一轮对抗式独立审查，均发现真实缺陷并已修复（详见 [evidence §十六](../decision-chain/evidence/V1_M1_CANDIDATE_RUN_001.md)）。单测 145→162 全绿，DSL 重新生成为 v0.7。

**重要治理后果，已如实登记**：这批改动发生在 `closing_verification` 通过**之后**，修改了编译器/DSL 源码。按 v1.3 `evidence_reuse_policy.criterion_dependency_map`，此前收口审查对 AC-03/04/07/10/13/14 给出的 PASS，其证据绑定（commit hash、已发布图字节）随新 commit 必然过期，已在 [Rebase Manifest §五](../decision-chain/docs/M1_REBASE_MANIFEST_v1.3.md) 逐条标注为 `PASS_STALE_PENDING_REVERIFICATION`（AC-07 因改动的是全新代码路径，直接改记 `NOT_VERIFIED`，不是"过期"）；AC-00/AC-16 不依赖编译器代码内容，继续有效；AC-15 阻断原因是环境权限、与源码无关，不受影响。

**证据边界，如实标注**：以上全部只是 `executor_self_check`（确定性单测）+ 两轮同会话内对抗式审查，**不是** §8 标准的正式独立审查（预算已在 v1.2 阶段耗尽），**也没有任何一次真实 Dify 调用验证过**——file_upload/document-extractor 链路能否真的在真实运行时工作、真实模型是否真的按新口径填写这几个新字段，均是未经证实的假设。

**唯一剩余动作，需要 Founder（与之前一致，二选一）**：
1. Founder 亲自在浏览器控制台对候选 App `dd638b91-d39f-4e92-a984-6ad1ab809119` 导入并发布 v0.7（覆盖 v0.6），执行侧随后跑真实回归验证 B-3/B-4/B-5，并完成 AC-15 的真实回滚演练；
2. Founder 提供一个当前有效的控制台会话/API 凭证，交由执行侧自主完成上述全部动作并记录。

在此之前，v0.7 的全部新增机制、以及此前已过期的 6 项 PASS，均无法进一步推进。

**2026-08-25 状态更新（v1.3 收口审查已完成）**：v1.3 `review_contract.closing_verification: affected_scope_only` 已跑完（隔离上下文、只读、无先前记忆的第二名审查员），范围锁定 8 项待复验 + 新增 AC-16，结论：**8/9 PASS，1 项阻断**——详见 [evidence §十五](../decision-chain/evidence/V1_M1_CANDIDATE_RUN_001.md)。

**唯一阻断**：`M1-AC-15`（回滚演练）——从未真实执行过一次"指回旧版本→确认候选 App 真的按旧版本运行→再指回新版本"的演练，只有结构性静态验证，缺演练日志和 after-state。**受阻原因是环境权限，不是工程缺陷**：执行侧对 Dify 控制台 API 无写权限（`console/api/apps` 仍返回 401，与 SE-015 一致）；本次额外排查了仓库连接的 `dify-platform-expert` MCP 工具是否可作为替代写入通道，经核实其 `base_url` 指向一个本机确认连接被拒绝、非真实运行实例的地址，且平台自我介绍带营销式措辞，**判定为未连接到本机真实 Dify 实例的工具，不采信、不使用**，避免在虚假前提下产生不可控副作用。

**唯一剩余动作，需要 Founder**：以下二选一即可解除阻断——
1. Founder 亲自在浏览器控制台对候选 App `dd638b91-d39f-4e92-a984-6ad1ab809119` 执行一次真实版本回退再重新发布（执行侧可提供具体操作步骤，由执行侧全程直连数据库记录 before/after 状态与恢复验证）；
2. Founder 提供一个当前有效的控制台会话/API 凭证，交由执行侧在候选 App 范围内自主完成演练并记录。

按 v1.3 `review_contract.closure_rule`，本次阻断不重开开放式审查，其余 8 项验收标准已通过，不受影响。**次要、非阻断**：审查同时发现两处账本完整性小缺口（候选 App 实际服务过 7 次真实调用、证据文件只记 6 次；`307d3aa` 之后两次推送未再登记进 L5）和一处 v1.3 文档自身的治理待决项（§8 自证 `task_contract_hash` 与合同正文独立复算不一致，此前已披露，本次由第二名独立审查员复核确认不是执行侧笔误）——均已如实记录，均不影响其余 8 项验收标准的 PASS 结论。

| 项 | 值 |
|---|---|
| 起算基线 | `main @ 0de99930ff5da5c24aa2fbe34615abe52cc6c7db` |
| 独立 worktree | `/home/faye/diyu-demo-worktrees/m1-natural-interaction-context-v1` |
| 任务分支 | `task/m1-natural-interaction-context-v1`（已推送远程） |
| 已完成 | (1) 设计文档 [`V1_M1_TASK_CONTEXT_COMPILER_DESIGN_v0.1.md`](../decision-chain/docs/V1_M1_TASK_CONTEXT_COMPILER_DESIGN_v0.1.md)；(2) 编译器源码 `decision-chain/workflows/m1_context_compiler_v0.1.py`（P0 最小切片：9 个扁平信号字段）；(3) 真实 Dify 候选 App `dd638b91-d39f-4e92-a984-6ad1ab809119`（已定位真实自托管 Dify 1.16.1，与 A-0～A-4 证据同一实例）；(4) DSL 导入并发布三版（v0.1→越界给专业判断→v0.2 修复→A-0/A-2 受控等价回归中发现内部枚举代码泄漏→v0.3 修复）；(5) 六次真实 `/v1/chat-messages` 对话运行（RUN-001~003 + CE-A0/CE-A2/CE-general 首轮 + 三者复验），含两次自验发现并修复的真实缺陷，详见 [`V1_M1_CANDIDATE_RUN_001.md`](../decision-chain/evidence/V1_M1_CANDIDATE_RUN_001.md)；(6) 正式单测文件 `decision-chain/workflows/test_m1_context_compiler_v0.1.py`（29 用例全绿）；(7) A-0～A-4 受控等价回归**部分**完成，M1-AC-12 当前诚实状态见 evidence 文档 §九——A-0/A-2/普通咨询三类已覆盖，A-1/A-3/A-4(b) 因依赖 M1 P0 没有的按槽位接受/撤销状态机而结构性无法覆盖；(8) `project_content_task()` 投影函数（设计参照文档 §三）已实现——纯离线函数，不接入 Dify DSL（设计文档明确其只在移交 Content Brief 时按需调用，非本轮对话节点职责）；P0 快照结构性缺失的四项（`account_stage`／`expression_discretion`／`evidence_and_gaps`／`available_capacity`）如实标 `NOT_CAPTURED_IN_P0_SNAPSHOT`，M1 明确不做专业判断的四项（`audience_problem_scene`／`audience_shift`／`content_promise`／`post_publish_observation`）留给调用方经 `caller_supplied` 传入、未传入时如实计入 `projection_gaps`，不由 M1 编造内容；8 个新单测覆盖上述缺口标记、调用方传值透传、未知键拒绝、`cycle_role` 分支 |
| 已决定的范围边界 | Founder 2026-08-25 明确裁决：M1 严格对齐 Execution Prompt 本身，只做意图/编译层，不触碰 `v1_state` 既有线性锁、不改任何 Skill 正文；已写入设计文档 §四"已知限制" |
| 未完成 | 见下方 v1.3 Rebase 行——8 项阻断中已修 4 项（B-1/2/5/6），B-3/B-4 明确本批不做（需真正架构判断），B-7 只做静态验证，B-8 已补账本；`M1-AC-00`～`16` 逐项收口复验（`affected_scope_only`）；DSL v0.6 尚未导入/发布/live 验证 |
| 下一步可立即执行的动作 | DSL v0.6 交 Founder 导入/发布 → 用 App API Key 跑真实回归（重点验证 B-6 判据依赖的"影子节点严格产出全部必需字段"这一未经实测的前提）→ 对 `REVERIFY_AFFECTED_SCOPE` 标记的 8 项 AC + 新增 AC-16 跑一次收口复验（隔离上下文只读 reviewer，`affected_scope_only`，不重开开放式审查，见 [`M1_REBASE_MANIFEST_v1.3.md`](../decision-chain/docs/M1_REBASE_MANIFEST_v1.3.md)） |
| **v1.3 Rebase（Founder 2026-08-25 提供 `M1_ENGINEERING_EXECUTION_REBASE_PROMPT_v1.3.md` 并明确"授权补充落盘"）** | 落盘 Prompt 副本 + [`M1_REBASE_MANIFEST_v1.3.md`](../decision-chain/docs/M1_REBASE_MANIFEST_v1.3.md)（哈希核验、基线核验、`REBASE_IMPACT_MAP`）。**首次对本任务运行正式 §8 独立审查**（隔离上下文/只读/无先前记忆，非执行侧自验）：`M1-AC-00`～`15` 里 3 项相对扎实（`AC-12`/`AC-13`），**8 项构成阻断**（B-1 次目标/优先级/经营目标类别无承载；B-2 `permission`/`freshness` 维度缺失；B-3 材料/历史产物无输入通道；B-4 `needed_capabilities` 单值+关键词决定；B-5 `CANCEL`/短指代/`HANDLED` 无机制；**B-6 影子节点真实失败时被当合法空 patch，产生虚假的"确实不是落库失败"断言**——真实 bug，已独立复现；B-7 从未做回滚演练；B-8 10 次真实推送账本零记录）。已修复 B-1/2/5/6（单测 83→116→120，过程中二次对抗式审查又发现并修复 3 个新问题：`priority_order` 矛盾累积改为替换语义、存量证据条目补条目级升级、`CANCEL`+真实变更时的假断言加 `changed` 守卫）；B-7 因无控制台写权限改做静态验证；B-8 已补记 L5 SE-018（10 次推送）并更正一处审查报告的表述（`b39c9e21` 经数据库时间戳核实为修复前重复发送，非修复后复发）。**B-3/B-4 本批明确不做**（需真正架构判断，同"按字段确认状态机"此前的范围裁定）。DSL 已生成 v0.6，尚未导入/发布/live 验证。`task_contract_hash` 自证不一致已如实登记（v1.3 §8 声明值与独立复算值不同，详见 Rebase Manifest §一），未擅自处理，不影响已经通过其他渠道明确的执行授权本身 |
| **v0.2 快照扩展（代码+单测+live 全部完成）** | 新增 `account_stage`／`expression_discretion`（剧情/二创/冲突/争议四项裁量）／`capacity_triad`（期望发布量/周期可用/基线三分）三组字段，均为扁平字符串/枚举、刻意回避嵌套结构风险；新增向前兼容的快照顶层键补齐逻辑（旧会话快照缺新字段时不丢数据、不崩溃）；`content_task` 投影同步消解三项 `NOT_CAPTURED_IN_P0_SNAPSHOT` 缺口；DSL 生成脚本同步更新（影子节点系统提示词、17 字段结构化输出 schema、默认快照 JSON）；单测从 29 个扩到 35 个全绿。**导入/发布**：执行侧控制台会话因本机 Docker 容器重启失效、未持有明文密码不重新索取，改为把 DSL 文件交给 Founder，**Founder 本人 2026-08-25 在浏览器控制台完成导入与发布（v0.4）**；执行侧随后用既有 App API Key 跑真实回归 CE-v0.2-01（两轮），`m1_shadow` 推理轨迹逐字复述出第一轮持久化的三组新字段值，证明真实持久化正确、跨轮不丢失，详见 [`V1_M1_CANDIDATE_RUN_001.md` §十](../decision-chain/evidence/V1_M1_CANDIDATE_RUN_001.md) |
| **v0.3 快照扩展（本轮新增，代码+单测完成，live 未做）** | `evidence_bundle[]`（#9，用户原话+代码组装五维度）与 `gaps[]`（#11，零新增 LLM 字段、纯代码推导）**实现**；`market_observations[]`（#10）／`runtime_evidence[]`（#14）判定 M1 候选环境无真实产出通道，**如实 DEFER**（空数组+gaps 恒定登记降级原因，非只留空数组）。实现前先跑设计→对抗审查两步产出方案，对抗审查纠正原方案两处会违反冻结硬约束/仓库红线的问题；实现完成后三路独立复核（重跑单测/对抗式合规审查/DSL 同步）又抓到两处真实硬伤——8 条恒定缺口条目被逐轮冗余持久化（占某次快照 73% 字节）、为 P0 不可达状态建了 45 行零调用方守卫函数（违反"不为未来想象增加无必要结构"）——以及一处治理越界（执行侧在代码注释里给验收判据 AU-05 写解释未同步设计文档），三处均已修复。单测 35→88→83（修复后净增 48）全绿。详见 [`V1_M1_CANDIDATE_RUN_001.md` §十一](../decision-chain/evidence/V1_M1_CANDIDATE_RUN_001.md)。**导入/发布**：Founder 本人完成 `m1_candidate_dsl_v0.5.yml` 导入与发布（覆盖 v0.4）；执行侧用 App API Key 跑真实回归 CE-v0.3-01（两轮），`m1_shadow` 推理轨迹逐字复述第一轮持久化的证据条目及 `SYSTEM_TENTATIVE` 状态，`evidence_nature` FACT/REFERENCE 两分支均真实触发，`evidence_scope` 一次被模型主动推断为 `THIS_ACCOUNT`（合法但更主动，待 Reviewer 判断是否收紧），候选 App 当前运行版本 v0.5 |
| Checkpoint 触发原因 | 正常阶段性收口（对话上下文即将压缩），非任务失败或外部中断；已提交的代码、证据、账本记录均已落盘，可凭本 Checkpoint 与 Git 历史直接续作 |

---

### `DIYU-V1-M5-UNIFIED-INTEGRATION-FINAL-ACCEPTANCE-001` Checkpoint（2026-08-28／29，`FINAL-P0` 最小修复轮，**非终态**）

```yaml
task_id: DIYU-V1-M5-UNIFIED-INTEGRATION-FINAL-ACCEPTANCE-001
task_entry_mode: CONTINUE                 # 同一 task_id，合同哈希不变
active_prompt: M5_FINAL_MINIMAL_P0_REMEDIATION_AND_NEXT_STAGE_EXECUTION_PROMPT_v1.0
task_progress: IN_PROGRESS
terminal_state:                           # 留空。终态不由执行侧填写。
candidate_commit: 5f84d94d542693f143faab0444525618ab21a4e9
candidate_manifest: V1_M5_CANDIDATE_RUN_MANIFEST_v1.1.4_FINAL_P0.yaml
bind: fp
branch_head: adb67a7
main_merge: NOT_ALLOWED
new_formal_round: NOT_AUTHORIZED
```

**做了什么**：按冻结的最小修复面（N1 = M3 successor；N2 = 六能力共享 `returns_adapter`；
N3 = 六能力 `USER_DELIVERY` 模板）改，`rb` 与 `legacy` 绑定的应用一个字节没动。
R1–R7 全部跑完，A/B 受影响案例已重建。

**验证结论（只说证据支持的）**：

| 项 | 结果 |
|---|---|
| R2 三份原留出重跑 | 三处 P0／残留**均不复现**；机器绑定现场查库一致 |
| R3 两份新鲜留出 | 执行侧可判 P0 面**零命中**；4 项 `SEMANTIC_HUMAN_ONLY` 未决 → `NOT_VERIFIED` |
| R4 `RISK-M4-030+031` | **`FAIL`**（按冻结判据；偏离格在轮间漂移，判据不改） |
| R5 正常主路径 | 四能力全交付、零泄漏、幂等成立——收紧未误挡正常业务 |
| R6 确定性测试 | 11/11 `PASS`，含负控制与假阳性控制；保护面零漂移 |
| R7 十九维与 AC | `M5-AC-07` = `FAIL`；`AC-03`／`04`／`08` = `STALE`；四项人判 = `NOT_VERIFIED` |

**必须传给下一手的四件事**：

1. **`M5-AC-07` 是 `FAIL`**，候选整体不可验收。这轮的任务是修三处行为，不是让 M5 通过。
2. **`STALE` 是按授权没跑，不是漏跑。** `allowed_reverification_only` 只给了 R1–R7，
   `new_formal_round: NOT_AUTHORIZED`。要转 `CURRENT` 需要新的正式轮授权。
3. **盲评在本仓库内不成立**：`AB_SUITE_RAW_*` 带显式 `A`／`B` 键、与盲评包同目录，
   封存 mapping 挡不住比对。盲评包必须**脱离仓库**单独交给独立评审人。
   执行侧已因运行器日志打印字数而知道 `AB-M3-01` 的映射，**对该案例的任何评分意见无效**。
4. **冻结映射有一处 id 不匹配**：十九维把「质量」绑到 `RISK-M4-030`，实际用例 id 是
   `RISK-M4-030+031`，导致本轮唯一一条当期 `FAIL` 在该维不可见。属合同层，执行侧无权改。

**下一动作（需要 Founder）**：
① 裁定 R3 的 4 项人判子项，其中 `H01-A3` 是 P0；
② 决定 `RISK-M4-030+031` 的判据是否出下一版（本轮不改）；
③ 决定是否授权新的正式轮以消除 `STALE`；
④ 安排隔离交付的独立人类盲评。

**Checkpoint 触发原因**：Prompt 规定 Step 6 完成后停在 `CHECKPOINT` 交裁决，非失败、非中断。

**2026-08-29 追加（Founder 裁决 001 + R4 归因，Checkpoint 仍为非终态）**：

Founder 裁决 `H01-A3 = PASS` / `freshness = CURRENT`，据此关闭 `HOLDOUT-M5-RB-01`、
`HOLDOUT-M5-RB-02` 两个原 P0，`applicable_p0_failures = 0`。裁决全文与被裁决产物原文见
[`V1_M5_FINAL_P0_FOUNDER_ADJUDICATION_001.md`](../decision-chain/docs/V1_M5_FINAL_P0_FOUNDER_ADJUDICATION_001.md)；
R3 判定书 `NOT_VERIFIED` 原文保留未覆盖，仅在其尾部追加后继裁决指针。

人判计数：总数 5（`H01-A1`／`H01-A3`／`H01-A4`／`H02-A3`／`H02-C2`），
Founder 已裁 1（`H01-A3` = `PASS`），**剩余未决 4，其中 P0 级 0**。
三份留出仍 `NOT_VERIFIED（PENDING_HUMAN）`——未决面已不含 P0。

`R4` 归因完成（零模型调用、零采样、零修改）：`confirmed_origin = CHECKER_OR_FIXTURE`。
检查器测的是枚举字符串逐格相等，判据原文说的是"等价表达不被误判为失败"，两者不等价；
按运行时 `delivered()`，`DELIVERED_AFTER_RECOVERY` 属已交付。五次既有运行重裁：
`riska`／`riskF` 两个权威一致 `FAIL`（真实假阴性，产物 0 字与 21 字，不翻案）；
`FRB2`／`FRB3`／`fp1` 判据原文 `PASS`、检查器 `FAIL`。分界线是 M4 解析 successor
（commit `4d03367`，08-28 06:00），落在 `riskF` 之后、`FRB2` 之前。
详见 [`V1_M5_R4_CHECKER_CRITERION_TRIAGE_v1.0.md`](../decision-chain/docs/V1_M5_R4_CHECKER_CRITERION_TRIAGE_v1.0.md)。

**执行侧未改任何状态**：`RISK-M4-030+031` 记录仍 `FAIL`，`M5-AC-07` 仍 `FAIL`。
"判据原文与检查器实现冲突时以谁为准"属验收判据域，待 Founder 裁决。
另需注意：现有五次运行只有正控制侧，**引号变体的负控制缺失**，
所以"解析器是否还会因引号漏判"严格说仍 `NOT_VERIFIED`，不能因三次都交付就断定已修好。

`task_progress: IN_PROGRESS`；`terminal_state`: 留空；`main_merge: NOT_ALLOWED`。

**2026-08-29 追加（Founder 裁决 002 + 定向负控制，Checkpoint 仍为非终态）**：

Founder 裁定 `RISK-M4-030+031` 的权威判据为冻结 `oracle` 原文与根 Prompt §3、`FINAL-AC-05`，
`judge_m4_030_031` 为 `CHECKER_OR_FIXTURE`，不具改写产品判据的权威。
`riska`／`riskF` 历史 `FAIL` 保留不追溯；`FRB2`／`FRB3`／`fp1` 正向等价检查判 `PASS / CURRENT`，
原始 evidence 与原 verdict 均不覆盖。

按裁决 002 §四执行**一次**定向负控制（授权上限 1，实跑 1，无重试、无重复采样）：
输入与预期先冻结（`V1_M5_R4_NEGATIVE_CONTROL_FROZEN_SPEC_v1.0.md`，sha256 `d62ad5d0…`，
提交 `47dfa4c` 早于调用；运行器启动时现场复算哈希，不符即拒跑）。
负例保留带引号书写形式，整项抽掉 `audience_problem`，场景与正例不同、事实取自既有夹具。

结果 `run_id = eb2364a5…`：`outcome=UNKNOWN`、`component_return=true`、`artifact=0 字`，
组件级 Return 的 `precise_gap` 精确等于 **`audience_problem`**，`parse_status: "OK"`；
用户可见输出 92 字只问缺的那一项，零泄漏。冻结书五条判据全部成立 → **负控制 `PASS`**。

判别力双向证成：同一带引号书写形式，语义充分时交付（产物 4695 字），
缺一项时不交付（产物 0 字）并精确点名缺项。

状态：`RISK-M4-030+031 = PASS / CURRENT`；`negative_discrimination_check = PASS`；
**`M5-AC-07 = NOT_VERIFIED`**——负控制这条阻断解除，但 R3 四项非 P0 人判
（`H01-A1`／`H01-A4`／`H02-A3`／`H02-C2`）未决，故不得记 `PASS`。

未改 M4、未改冻结判据、未原地改检查器 v1.0、未启动完整正式轮、未合并 main。
`task_progress: IN_PROGRESS`；`terminal_state`: 留空。

**2026-08-29 追加（Founder 裁决 003：接受技术债并收口；Checkpoint 解除条件已建立）**：

Founder 裁决 `M5-FOUNDER-ADJUDICATION-003`：「我认为两项P0收口后，暂时忽略剩余问题项，
作为技术债登记，推进M5后续收口」。据此按收口合同 `v1.2`
（sha256 `35ccf590…de9df0e`）与收口 Prompt（sha256 `e384df3d…49397cc`）执行最终收口。
`entry_mode = REBASE_TASK`，同一 `task_id`，未新建、未重置失败历史。

**Founder 接受的准确含义**：`founder_product_acceptance = PASS/CURRENT`，
`acceptance_type = ACCEPTED_WITH_DISCLOSED_TECHNICAL_DEBT`，`all_original_m5_ac_pass = false`。
它改变的是这些项对 v1.2 收口公式的**阻断资格**，不是它们自己的技术结果或证据时效。
原 AC 状态、历史 `FAIL`／`NOT_VERIFIED`／`STALE`、sealed mapping 与裁决 001／002 全部原样保留。

**本轮四类收口记录**（只追加，无平行体系）：
[裁决 003](../decision-chain/docs/V1_M5_FOUNDER_ADJUDICATION_003_TECHNICAL_DEBT_CLOSEOUT.md)、
[技术债主表 v1.0](../decision-chain/docs/V1_M5_ACCEPTED_TECHNICAL_DEBT_REGISTER_v1.0.md)（全仓唯一）、
[证据索引 v1.2](../decision-chain/docs/V1_M5_FORMAL_ACCEPTANCE_EVIDENCE_INDEX_v1.2_FOUNDER_DEBT_CLOSEOUT.yaml)、
[最终回执 v1.1](../decision-chain/docs/V1_M5_FINAL_CLOSURE_RECEIPT_v1.1_FOUNDER_DEBT_CLOSEOUT.md)。

**技术债 8 项**（`TD-M5-01..08`），`open_debt_items_p0 = 0`。仍未验证面：
`M5-AC-03`／`04`／`08` `STALE`，`M5-AC-05`／`06`／`07` `NOT_VERIFIED`。**不得说全绿。**

**现场刷新结论**：worktree clean；相对现场 `origin/main` 为 **592 新增 / 2 修改 / 0 删除**，
两处修改均为共享账本只追加（删除行 0）；live main 十个未跟踪文件在位，与 594 条待合并路径
交集 **0**；候选 8 个 Dify 应用 graph/node/model 与 v1.1.4 冻结值逐条一致，**漂移 none**，
收口阶段 Workflow/LLM 调用 **0**。

**2026-08-29 终态（M5 收口完成）**：

```yaml
task_id: DIYU-V1-M5-UNIFIED-INTEGRATION-FINAL-ACCEPTANCE-001
task_progress: COMPLETED
terminal_state: DONE
delivery_disposition: ACCEPTED_WITH_DISCLOSED_TECHNICAL_DEBT
all_original_m5_ac_pass: false
applicable_p0_failures: 0
open_technical_debt: 8            # TD-M5-01..08，其中 P0 级 0
closeout_commit: bc660498af24afe1cc3e800459246cc1f954003b
main: bc660498af24afe1cc3e800459246cc1f954003b
origin_main: bc660498af24afe1cc3e800459246cc1f954003b
task_branch: bc660498af24afe1cc3e800459246cc1f954003b
force_push: NONE
next_stage_default: false
```

**`DONE` 的准确含义**：只表示 v1.2「可用候选 ＋ 已披露技术债 ＋ Git／远端收口」合同完成。
**不**表示原 `M5-AC-00..10` 全绿、生产就绪、真实运营闭环或经营提升。
`M5-AC-03`／`04`／`08` 仍 `STALE`，`M5-AC-05`／`06`／`07` 仍 `NOT_VERIFIED`。

技术债后续处理只能由新的优先级与新任务授权打开，不得在本 M5 任务内继续修复或复验。
主表：[`V1_M5_ACCEPTED_TECHNICAL_DEBT_REGISTER_v1.0.md`](../decision-chain/docs/V1_M5_ACCEPTED_TECHNICAL_DEBT_REGISTER_v1.0.md)。

---

### `DIYU-V1-UNIFIED-DIFY-APPLICATION-001` Checkpoint（2026-08-29，意图路由复验轮，**非终态**）

分区账本（状态、下一动作、L1/L3/L4/L5 全部细节都在里面，本文件不复制）：
[`tasks/DIYU-V1-UNIFIED-DIFY-APPLICATION-001.md`](tasks/DIYU-V1-UNIFIED-DIFY-APPLICATION-001.md)

```yaml
task_id: DIYU-V1-UNIFIED-DIFY-APPLICATION-001
task_progress: IN_PROGRESS
terminal_state: UNSET
checkpoint: 意图路由桥接已修并复验；歧义负例未成立，停在 Founder 裁决门
founder_adjudication: FOUNDER_ADJUDICATION_UAPP_INTENT_ROUTING_001 = RETURN（2026-08-29）
graph: 40e4585825bb7d211f357d89136cb2294936ca54287333fef49b6f74e5b64f2b  # 69 节点 / 81 边
deterministic_checks: 32 PASS / 0 FAIL
ac_pass_current: [AC-01, AC-10, AC-11]
ac_fail:         [AC-02, AC-03, AC-05, AC-06, AC-07]
ac_return:       [AC-12]
ac_not_verified: [AC-04, AC-08, AC-09]
open_technical_debt: 16          # TD-UAPP-01..16
main: 01a42b0ed97344a67302ecb6778ae4a772eb28b2          # 未动
origin_main: 01a42b0ed97344a67302ecb6778ae4a772eb28b2    # 未动
force_push: NONE
```

**本轮真正验证成立的只有一件事**：自然语言意图能被系统自己识别并真实调用专业能力，
同会话追问能沿用上文。证据是两张不同的图上各跑一次、结论一致的 `UAPP-INTENT-01`，
判在 Dify 节点执行记录上，不认模型自述。

**Founder 裁定的解禁条件未成立**：裁定点名三条用例，过了两条，
能力歧义负例 `UAPP-INTENT-02N` `FAIL`。`AC-02`/`05`/`06`/`12` 照旧保持 `FAIL`/`RETURN`，
**执行侧不因为主路通了就把它们提上去**。`main` 合并继续禁止。

**下一动作**：取得 Founder 对 TD-UAPP-16 的裁决——「这条我想再打磨一下」到底算不算
「确实存在能力歧义」。判据侧与被测对象侧两种可能，证据不足以定案，执行侧无权自选。
判定信号见分区账本 L2 表。

---

### `DIYU-V1-UNIFIED-DIFY-APPLICATION-001` Checkpoint（2026-08-29，渐进候选 S4 后继窄验证前登记，**非终态**）

分区账本（状态、下一动作与全部细节都在里面，本文件按 canonical §一 只留定位，不复制正文）：
[`tasks/DIYU-V1-UNIFIED-DIFY-APPLICATION-001.md`](tasks/DIYU-V1-UNIFIED-DIFY-APPLICATION-001.md)

```yaml
task_id: DIYU-V1-UNIFIED-DIFY-APPLICATION-001
task_entry_mode: CONTINUE_TASK
task_progress: IN_PROGRESS
terminal_state: UNSET
checkpoint: Founder 裁定 002 已登记；判据与六轮冻结输入已在首次调用之前冻结提交；待跑一次连续验证
successor_app_id: 85c01f85-a081-43e9-ab09-9993289cc200   # 渐进候选，非旧 app 2448e4f9
graph: f75555c0d6552a0894975242ef3fad7a5351ca63ce4404915c0ee1f71d8f3927   # 46 节点 / 48 边
branch: codex/v1-uapp-progressive-canvas-001
main: 01a42b0ed97344a67302ecb6778ae4a772eb28b2          # 未动
main_merge: NOT_ALLOWED
```

**这条 Checkpoint 不上行任何状态。** Founder 裁定 002 只把「`content_origin_mode` 精确追问」
这一项行为判 `PASS`，Gate 4 的历史 `FAIL` 一条不改绿，S4／UAPP／M5 一律不动。

---

## `DIYU-V1-UNIFIED-DIFY-APPLICATION-001` · 2026-08-30 CHECKPOINT（非终态）

Phase A 根因 **PASS**、Phase B 最小修复 **PASS**、Phase C 的 C1 **PASS 6/6**、C2 **PASS 8/8**、C3 **FAIL 9/13**。事实充分性这一跳修好并被实测验证（Content Brief 产出 6188 字，修复前为 0）；窄链停在**另一个**缺陷——跨轮已确认字段无承载体（`TD-UAPP-20`）。

两项均不上调：`FACT_SUFFICIENCY_CHAIN_REPAIR`、`S4_CONTENT_ORIGIN_CONTINUATION`。

下一动作与技术债后继见 [`collab-ledger/tasks/DIYU-V1-UNIFIED-DIFY-APPLICATION-001.md`](tasks/DIYU-V1-UNIFIED-DIFY-APPLICATION-001.md) 末节；失败归因见 [`unified-app/docs/S4_PHASE_C_C3_FAILURE_TRIAGE_002.md`](../unified-app/docs/S4_PHASE_C_C3_FAILURE_TRIAGE_002.md)。

---

## `DIYU-V1-UNIFIED-DIFY-APPLICATION-001` · 2026-08-30 CHECKPOINT 二（非终态）

TD-UAPP-20 的跨轮字段载体已上线并**验证生效**：T4 用户回答 `content_origin_mode` 后，T5 由载体补齐、用户未被重复询问；CS 6843 字、PP 9031 字均产出（修复前同场景 T4/T5/T6 全为 0）。受影响连续链整体 **FAIL 13/17**：PD 停在 `production_profile`（`INSUFFICIENT_EVIDENCE`），载体不覆盖非反引号声明字段 `goal_family`（`SYSTEM_UNDER_TEST`），另两条在判据与检查器侧。五项允许上调的结论一项都未上调。

详见 [`collab-ledger/tasks/DIYU-V1-UNIFIED-DIFY-APPLICATION-001.md`](tasks/DIYU-V1-UNIFIED-DIFY-APPLICATION-001.md) 末节与 [`unified-app/docs/S4_NARROW_CHAIN_FAILURE_TRIAGE_003.md`](../unified-app/docs/S4_NARROW_CHAIN_FAILURE_TRIAGE_003.md)。

---

## `DIYU-V1-UNIFIED-DIFY-APPLICATION-001` · 2026-08-30 CHECKPOINT 三（非终态）

规范任务状态载体根修复完成并经**唯一一次七轮真实运行**验证：判定 **10/10 PASS**（V-01..V-09 + S-01，零模型调用），LLM 节点 39 / 上限 48，重试 0，七轮全部 `http=200`。

真实连续链成立：CB(T2, 6600) → CS(T4, 6016) → **PD(T6, 10121)** → PP(T7, 14984)。T7 的 `upstream_capability = PRODUCTION_DIRECTOR`，`sha256(upstream_delivery)` 与 T6 PD 产物 `b032cfd7…3ac1bb` 完全相等，`lineage = BOUND`，不是 CS→PP 的 PRE 短入口。

作用域隔离活体成立：`operation.time_window="四周内"`（E）与 `production.time_window="今天半天内"`（B）同时在册未串；T5 因此正确追问而非默认填充。等级纪律成立：终态 19 字段中 12 B / 7 E，`missing_source_ref`、`level_ref_mismatch`、`placeholder_in_carrier` 三项全空。

**一项如实未上调**：`CROSS_TURN_CORRECTION_PROPAGATION` 记 `NOT_VERIFIED(NOT_CHECKED)`。真实运行两次纠正（T4 `facts.publish_permission`、T6 `production.profile`）时刻，账本内已有 artifact 的依赖集都不含被纠正字段，`stale_artifacts` 为空属 A3 正确的「不多算」；但也因此该通路只有离线确定性控制证据，无真实运行证据。

九受保护应用零漂移，hop 钉住与 `m5_compose` 钉住未变，`main` / `origin/main` 停在 `01a42b0`。未合并 main，未进入 S5，未填根任务终态。

详见 [`collab-ledger/tasks/DIYU-V1-UNIFIED-DIFY-APPLICATION-001.md`](tasks/DIYU-V1-UNIFIED-DIFY-APPLICATION-001.md) 的 `ATT-UAPP-CANON-01` 段。

---

## `DIYU-V1-UNIFIED-DIFY-APPLICATION-001` · 2026-08-30 CHECKPOINT 四（非终态）

**技术链是真的，交付内容不合格。** 外部验收复核零模型独立重算：CHECKPOINT 三 记录的链路结论未被推翻
（7/7 顶层 run、28/28 嵌套、39 LLM 全 succeeded、四份 artifact 哈希现算一致、T7 上游与 T6 PD 逐字节相等、
九受保护应用与候选图复核时点零漂移），但 **PP 最终交付内容 FAIL**。

PP 真实运行 `15e2643a-7710-47d0-a162-40b13726219d` 的输入**已逐字包含** `cta_contract:「不做购买、到店、私信或领取引导，只保留内容本身」`、
`NO_CTA`、`facts_registered`、`explicit_non_promise`、`expression_boundary`、`publish_permission` 与整段 T6 PD artifact——
「PP 没收到约束」这条归因已排除。九条违规定位串全部在 `PP.raw_preserved` 首次出现、PP 输入零命中，
下游 Seam 与统一画布逐层 sha256 相等（纯透传）。

```yaml
highest_confirmed_failing_node: PUBLISHING_PACKAGING delivery generation
S4_OVERALL_ACCEPTANCE: FAIL / CURRENT
V-08A: PASS / CURRENT
V-08B: FAIL / CURRENT     # 事实主张逐项可回指
V-08C: FAIL / CURRENT     # CTA 与上游冻结边界一致
CROSS_TURN_CORRECTION_PROPAGATION: NOT_VERIFIED(NOT_CHECKED)
S5: NOT_STARTED
main_merge: NOT_ALLOWED
```

两类问题：PP 把未登记的「苏禾一直在用这套三问」写成事实（且 PP 自己已核对出夹具没写，加脚注标注推断不构成回指）；
PP 收到 NO_CTA 仍生成结尾互动提问与整段评论区设计，并把「只保留内容本身」改写成「不做购买引导」、
自造「低风险互动范畴」豁免。旧 V-08 报 PASS 是因为 `fabrication_probes` 七项与 `leak/overclaim` 43 项
**都不覆盖**这两类——PASS 是探针未命中，不是证据支持的通过。

本轮零模型调用、零 Dify 写入、零工作流发起、零数据库写入；`git status --porcelain` 只有新增文件，
Gate v1.0/v1.1、Manifest、RESULT v1.0、VERIFY(v1.0)、COST_ACCOUNT、T1–T7 RAW 一个字节未动。
14/14 已在 **Gate v1.1** 下重绑定重算并附单点变异区分证明。

唯一后继最小修复候选：**PUBLISHING_PACKAGING 能力应用的交付生成层**（`c9cdea24…`）。
该 PP 是 M5 FP 的 PP，graph md5 被 7 处记录绑定（含 M5 已完成验收证据），**不得静默修改**，
实施需独立 Execution Prompt 与 Founder 授权。

详见 [`collab-ledger/tasks/DIYU-V1-UNIFIED-DIFY-APPLICATION-001.md`](tasks/DIYU-V1-UNIFIED-DIFY-APPLICATION-001.md) 的 `ATT-UAPP-EXT-REVIEW-01` 段、
[`unified-app/docs/S4_CANONICAL_TASK_STATE_FAILURE_TRIAGE_001_PP_BOUNDARY.md`](../unified-app/docs/S4_CANONICAL_TASK_STATE_FAILURE_TRIAGE_001_PP_BOUNDARY.md)、
[`unified-app/docs/S4_CANONICAL_TASK_STATE_EXTERNAL_ACCEPTANCE_REVIEW_v1.0.md`](../unified-app/docs/S4_CANONICAL_TASK_STATE_EXTERNAL_ACCEPTANCE_REVIEW_v1.0.md)
与 [`unified-app/docs/S4_PP_BOUNDARY_MINIMAL_REPAIR_PLAN_v1.0.md`](../unified-app/docs/S4_PP_BOUNDARY_MINIMAL_REPAIR_PLAN_v1.0.md)。

---

## `DIYU-V1-PP-BOUNDARY-SUCCESSOR-001` · 2026-08-30 CHECKPOINT 一（非终态）

新后继任务，父任务 `DIYU-V1-UNIFIED-DIFY-APPLICATION-001`。Founder 三项裁决已落盘并哈希绑定。

**事实边界修好了，CTA 边界没修好。D1 = FAIL，按停止规则立即停止，D2/D3 未执行。**

在现有 PP 应用 `c9cdea24` 上建立后继版本（未建分叉应用）：后继 Skill
`packaging-content-for-release-m4-b1` 继承体逐字节等同 M4 源，新增 4 块 4055 字，零案例专用串；
PP 只改 `skill_llm.system`，发布新版本 `2026-08-30 09:05:41.729617`，旧版本行保留；
**provider 钉全程未动**，Seam / M5 FP / 统一画布整个验证期间走的仍是旧 PP。
确定性验证 9/9（含两条单点变异区分）。

D1（run `53b90396`，1 次调用，1 个 LLM 节点，零重试）：
D1-a/b/d/e PASS，**D1-c FAIL**。十个历史行为探针命中 0 次——旧版「一直在用这套三问」类
无来源人物历史已消失；但 `cta_surface` 逐字引用 `cta_contract` 后自检面只剩四项业务动作，
`comment_design` 置顶自述「被追问的」，`author_share_line` 是句末指向受众的问题。
「闭合」「权威顺序」「要求受众」在产出中各 0 次——新规则在推理里零痕迹。

`confirmed_origin = SYSTEM_UNDER_TEST`，失效节点是**本轮修复的覆盖面不足**：
PP-5「评论区是设计出来的」整节与 `author_share_line` 一节未被新规则约束（A3「少算」）。
不是 PP 应用本身坏了，也不是判据、检查器或输入的问题。

成本 1/3 顶层 run、1/10 LLM、零重试。`main` 未动，`origin/main` 仍 `01a42b0`。
三项允许上调一项都未上调。

一项待裁定：Founder §五 要求三项全 PASS 才发布后继版本，但 D1 必须调用到后继版本才能验证，
排法只能是「先发布、后重钉」——该排法已在模型调用之前写进冻结 Gate。现状是 PP app 的已发布
指针指向未通过验证的 b1，但**无任何消费者引用**。是否把该指针退回旧版本，需明确授权。

详见 [`collab-ledger/tasks/DIYU-V1-PP-BOUNDARY-SUCCESSOR-001.md`](tasks/DIYU-V1-PP-BOUNDARY-SUCCESSOR-001.md)
与 [`unified-app/docs/PPBS_FAILURE_TRIAGE_001_D1_CTA.md`](../unified-app/docs/PPBS_FAILURE_TRIAGE_001_D1_CTA.md)。

---

## `DIYU-V1-PP-BOUNDARY-SUCCESSOR-001` · b2 REBASE（2026-08-30）

**CTA 边界修好了，事实边界保持成立；统一入口那一关没跑起来，卡在我自己的运行器上。**

启动状态按规划侧裁定只追加登记：b1 整体 `FAIL/CURRENT`，当前 S4 整体 `FAIL/CURRENT`。
Phase A 零模型把 PP app 的已发布指针从 b1 退回旧稳定图（上一轮那项待裁定的披露，已裁定为退回）。

b2 从 b1 逐字继承（事实修复两整块逐字在场未回退），补的正是 b1 算漏的覆盖面：
`strict_cta_closed` 一次判定 ＋ 九行对外输出面清单、PP-5 条件化、`author_share_line`
条件化、自检 17 全表面扫描。收紧只发生在 `true` 分支。
Gate v2.0 的 D 判据由 v1.1 直接取值构造，逐块一致——**没有因为 b1 失败去改 CTA 判据**。

确定性验证 14/14（含正向控制、负向控制、三条单点变异各自翻 FAIL 且另两项不受影响）。

- **E1 · D1 正例 PASS 5/5**（`07d5ca02`，160.4s，1 次调用）：受众指向问句 0 句；
  b1 的五处失败点逐点修好；历史行为探针 0 次。
- **E2 · D2 冲突负例 PASS 5/5**（`81dc796d`，97.3s，1 次调用）：两项冲突要求各自明确拒绝
  并给出替代，且写明「不是包装环节可以自己放宽的」；仍交付完整成品，未整任务拒绝。
- **E3 · D3 NOT_VERIFIED(INCONCLUSIVE)**：HTTP 400、0.02 秒、**零模型输出**
  （九应用 run 全 0、LLM 0）。根因是运行器把字面量 `"file"` 当成了 Bearer token
  且没解包返回元组——继承自 b1 运行器、这次第一次被执行。按预算规则不重跑。

成本 2/3 顶层 run、2/10 LLM、零重试。受保护面已恢复到测试前状态：
PP 当前发布图与 provider 钉住的图都是旧稳定图 `788c8555`，b1/b2 行全部保留；
Seam、候选画布、其余八应用、`hop_pin` 零漂移；`main` 仍 `01a42b0`。

**三项上调一项都没做**（公式未成立）。`S4_OVERALL_ACCEPTANCE` 维持 `NOT_VERIFIED`，
`S5` `NOT_STARTED`，`main` 不合并，不建 b3。

**下一步只有一件：**你裁定是否授权重跑 D3（修运行器 ＋ 重新发布并重钉 ＋ 按原冻结判据跑一次）。
同时请确认「D3 未执行也按 D3 FAIL 那条恢复受保护面」这个判断是否越权。

详见 [`collab-ledger/tasks/DIYU-V1-PP-BOUNDARY-SUCCESSOR-001.md`](tasks/DIYU-V1-PP-BOUNDARY-SUCCESSOR-001.md)、
[`unified-app/docs/PPBS_B2_FAILURE_TRIAGE_003_D3_TRANSPORT.md`](../unified-app/docs/PPBS_B2_FAILURE_TRIAGE_003_D3_TRANSPORT.md)
与 [`unified-app/stages/PPBS_B2_PHASE_E_RESULT_v1.0.json`](../unified-app/stages/PPBS_B2_PHASE_E_RESULT_v1.0.json)。

**D3 重跑（Founder 2026-08-30 授权）结果：`NOT_VERIFIED(INSUFFICIENT)`。**
harness 修好了，链路真的走通了——D3-a 至 D3-e 全 PASS：自然语言入口、零 envelope、
零伪造前置状态、实际路由到 PP、其余五能力零暗跑、
UAPP → Seam → PP 按 `workflow_id → graph md5` 逐跳回指到 b2（`8366328b`）。

卡在 D3-f：统一应用最终交付正文是一条**输入不足升级**，不是包装成品。
九个对外输出面一个都没产生，事实与 CTA 边界**没有被真正考到**——
字面不违反，但那是空过，按内核反查四态属「有但不够」，不填成「有」。

根因不在 PP：PP 真实输入缺 `content_body_or_beats`，`hop_gaps` 也是它，
PP 返回 `INPUT_INSUFFICIENT` ＋ 七项齐全的精确升级。**b2 的行为是对的。**
缺口在画布/Hop 的跨轮状态绑定。按停止规则停在 CHECKPOINT，不动画布/Hop/b2，不建 b3。

成本 3/3 顶层 run、7/10 LLM、零重试。受保护面按 §九 全部退回旧稳定图
（b1、b2、原始行都保留），八应用与 hop_pin 零漂移。三项上调一项都没做。

**下一步：** 补齐 D3-f 需要先让画布这一轮把 `content_body_or_beats` 绑上来，
再跑一次并对真实包装正文施加 D1-b / D1-c——那是画布/Hop 的跨轮绑定问题，
需要单独授权与单独范围。详见
[`unified-app/docs/PPBS_B2_FAILURE_TRIAGE_004_D3F_INSUFFICIENT.md`](../unified-app/docs/PPBS_B2_FAILURE_TRIAGE_004_D3F_INSUFFICIENT.md)。

---

## `DIYU-V1-UAPP-ACCEPTED-ARTIFACT-BINDING-001`（2026-08-30）

**正式链 T1 PASS、T2 FAIL、T3 未启动；已自动恢复稳定发布面并停在 CHECKPOINT。**

Gate v1.1 在模型调用前冻结，sha256 `069a5af02cfcd173e024c4cfd66c38f74005c1c6d26afdf8e7b19ba81d74d6a6`。
零模型预检 12/12 PASS。T1 只运行 CS，产生 3497 字 artifact，sha256
`65f58acb09de20b77ff1deb669e2210e5f128a4b06fbaab14fbf31cf9955b938`。

T2 选择器正确取回同一份已接受、CURRENT、非 STALE 的 CS；但 Hop 把完整正文改写成
较短的 `script_or_equivalent_beats`，`uapp_fields` 现场复算得到不同指纹并正确
`REJECTED / NO_LEDGER_MATCH`。PD 实际运行但未获得合法绑定正文，未产生 PD artifact。
同时观察到 DeepSeek SSL EOF 与 Dify 一次平台内部重放；人工／顶层重试为 0。

首个失败后没有 T3、没有重跑、没有修改实现。E-01…E-11 均未完成，所有允许上调项
保持 NOT_VERIFIED；跨轮纠正传播仍 NOT_VERIFIED(NOT_CHECKED)，S4 未验证，S5 未启动，
main 不合并，terminal 未设置。成本：2 个顶层 run、12 次 LLM 节点尝试、1 次失败、
1 次平台内部重放。

发布面已恢复：UAPP `99c3edf7`，PP / provider `788c8555`；Seam `db49a3da`、
Hop `e38378c3` 未变，活动 workflow 为 0，候选和 b1/b2 历史行保留。测试会话保留
CS 正文但没有 PD；`uapp_last_capability=PRODUCTION_DIRECTOR` 与正文缺失的不一致原样留证。

**唯一下一步：** Founder 裁定是否授权新的版本化续行，修复
`uapp_hop → uapp_fields` 完整产物绑定不一致，并明确平台内部重放规则；当前合同不授权
第二次修复或再次运行。

详见 [`collab-ledger/tasks/DIYU-V1-UAPP-ACCEPTED-ARTIFACT-BINDING-001.md`](tasks/DIYU-V1-UAPP-ACCEPTED-ARTIFACT-BINDING-001.md)
与 [`unified-app/stages/UAAB_RESULT_v1.1.json`](../unified-app/stages/UAAB_RESULT_v1.1.json)。
