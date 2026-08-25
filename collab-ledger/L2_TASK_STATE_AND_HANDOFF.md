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

---

## 二、项目当前可执行动作（Current Handoff）

> **本节只维护：活动 `task_id` ＋ 依赖关系 ＋ 定位引用。**
> 每个活动 `task_id` **各自一行**。**这里没有、也不得有一个覆盖所有并行任务的全局「唯一下一步」。**
> 每行的下一动作四要素缺一不可：**动作 ／ 对象 ／ 输入或基线 ／ 完成信号**。
> 当同时有两个及以上任务在跑时，各任务细节写进各自的 `collab-ledger/tasks/<task_id>.md` 分区，本表只留定位引用。
> **已完成的任务移出本表、终态记进 §一**——本表不维护「共几个」的汇总，数量随授权变化，写死必失真。

| task_id | 依赖 | 定位引用 | 动作 | 对象 | 输入／基线 | 完成信号 |
|---|---|---|---|---|---|---|
| `DIYU-V1-M1-NATURAL-CONTEXT-001` | [M1 施工 Execution Prompt v1.2](../decision-chain/docs/M1_ENGINEERING_EXECUTION_PROMPT_v1.2.md) | 本任务自身 Task Contract（内嵌于该 Prompt §2） | 工程实现 M1 全部 P0（自然语言交互、任务上下文编译、唯一调用意图/计划、真实 Dify 候选运行、独立审查、回滚包、远程任务分支收口） | 独立 worktree／任务分支 `task/m1-natural-interaction-context-v1` | `main @ 93377e404e9e29fe2cd41ee9691f7e966c50dbee` ＋ 该 Prompt 全文 | `M1-AC-00` 至 `M1-AC-15` 全部 PASS ＋ 提交 Founder Dify 实测包，见该 Prompt §13 |

**`COLLAB-LEDGER-BOOTSTRAP-001`、`V1-REBASE-EP00-CURRENT`、`M0-EP00-ADOPTION-CLOSEOUT-001`、`V1-M0-1B-SLICE-CONTRACT-REVISION-001`、`V1-M0-SLICE-PREFLIGHT-AND-SHARED-CONTRACT-CLOSEOUT-001`、`V1-M1-M4-PHASE0-PREAMBLE-ADOPTION-AND-DESKTOP-PACK-001`、`V1-M1-M4-PHASE0-DECISION-STATE-CLOSEOUT-001`、`V1-M1-ENGINEERING-PROMPT-ADOPTION-001`、`V1-COLLAB-PROTOCOL-PROMPT-AUTHORIZATION-RULE-001` 均已终结 `DONE`（见 §一）。**M0 已全部完成；M1–M4 Phase 0 共享编译前言已采用且前言内八项能力四类合同值、Matrix 局部降级口径均已 `FOUNDER_CONFIRMED`。Founder 2026-08-25 裁定"执行 Prompt 即授权"铁律（见 [COLLAB_CONTINUITY_PROTOCOL.md](COLLAB_CONTINUITY_PROTOCOL.md) §六 与 [L1 §T-009](L1_TASK_MANIFESTS.md)）后，M1 施工 Execution Prompt 视为已获执行授权，`DIYU-V1-M1-NATURAL-CONTEXT-001` 现为活动工程任务（见上表）；M2/M3/M4 施工 Execution Prompt 仍待规划侧编译，编译后同样适用该铁律。**

**已解决**：EP-00 报告 §十一「仍需 Founder 裁决的产品命题」已由 Founder 通过 F-01～F-10 十项裁决 + 四项定向纠偏答复，并落地进 v0.2（已 `ACCEPTED`）；四份共享合同已起草并经 Founder 接受（见 §一.7）。

**下一权限动作**（不是可执行工程任务，执行侧不得自行开工）：

| 动作 | 对象 | 输入／基线 | 完成信号 |
|---|---|---|---|
| 规划侧编译 M1—M4 施工 Execution Prompt | M1（自然交互、任务上下文与能力路由）／M2（最小业务数据、版本与运营记忆）／M3（运营状态诊断与持续运营决策）／M4（现有能力组件化接入与兼容改造）——**状态更正 2**：本列此前把 M1 误写为"业务持久化"（实为 M2 职责）、M2 误写为"写回权限恢复实现"（写回权限幂等恢复只是 M2 记忆职责下的一项具体能力，非 M2 全部定义）、M4 留空未定，与四窗口已冻结的唯一责任划分不一致；已由 `V1-M1-M4-PHASE0-PREAMBLE-ADOPTION-AND-DESKTOP-PACK-001` 更正，见 [L1 §T-006](L1_TASK_MANIFESTS.md) | 四份已接受的共享合同（[任务上下文快照](../decision-chain/docs/V1_M0_SHARED_CONTRACT_TASK_CONTEXT_SNAPSHOT_v0.1.md)／[八项能力合同](../decision-chain/docs/V1_M0_SHARED_CONTRACT_EIGHT_CAPABILITIES_v0.1.md)／[版本发布反馈归属](../decision-chain/docs/V1_M0_SHARED_CONTRACT_VERSION_PUBLISH_FEEDBACK_v0.1.md)／[写回权限幂等恢复](../decision-chain/docs/V1_M0_SHARED_CONTRACT_WRITE_PERMISSION_RECOVERY_v0.1.md)）＋ 两类 EP-00 证据（[通用](../decision-chain/docs/V1_REBASE_EP00_CURRENT_PREFLIGHT_v0.1.md)／[专项](../decision-chain/docs/V1_SINGLE_ACCOUNT_SLICE_EP00_PREFLIGHT_v0.1.md)） | 规划侧分别产出 M1—M4 各自的完整 Execution Prompt；**执行侧不得自行编写或推断这些 Prompt，也不得据本条自行开工任何 M1–M4 工程实现**。**状态更正 3**：此前登记的"两处尚未指定承接方的缺口"已解除——`EIGHT_CAPABILITY_FOUR_CONTRACT_VALUES = FOUNDER_CONFIRMED_AND_ACTIVE`；`MATRIX_INSUFFICIENT_INPUT_PRODUCT_RULE = FOUNDER_CONFIRMED_AS_LOCAL_DEGRADATION_AND_BRANCH_BLOCKING`；`MATRIX_INSUFFICIENT_INPUT_ENGINEERING = ASSIGNED_TO_M1_AND_M4_CONSTRUCTION`（M4 主修 Matrix 现有全局硬停的物理修复，M1 承接交互／路由／局部继续语义接口责任，M2／M3 按前言 §五冻结边界配合，二者可错峰施工但须在 M5 集成前共同闭合）——Founder 2026-08-25 在 `V1-M1-M4-PHASE0-DECISION-STATE-CLOSEOUT-001` 会话内当场确认，非历史"连续动作"追认，见 [L1 §T-007](L1_TASK_MANIFESTS.md)。**状态更正 4**：M1 施工 Execution Prompt 已由规划侧编译完成并落盘——[`decision-chain/docs/M1_ENGINEERING_EXECUTION_PROMPT_v1.2.md`](../decision-chain/docs/M1_ENGINEERING_EXECUTION_PROMPT_v1.2.md)（`task_id: DIYU-V1-M1-NATURAL-CONTEXT-001`）；**该文档已落盘 ≠ 该文档所定义的 M1 工程执行已获授权**，须 Founder 另行就这一具体 `task_id` 明确给出执行授权，见 [L1 §T-008](L1_TASK_MANIFESTS.md)。M2／M3／M4 施工 Execution Prompt 仍待规划侧编译 |

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

### `DIYU-V1-M1-NATURAL-CONTEXT-001` Checkpoint（本任务分支自身状态，未合入 main，不影响主线其他任务）

```yaml
task_id: DIYU-V1-M1-NATURAL-CONTEXT-001
task_entry_mode: CONTINUE_TASK
execution_disposition: CONTINUE
task_final_status: null
current_state: IMPLEMENTING
next_stage_allowed: false
```

| 项 | 值 |
|---|---|
| 起算基线 | `main @ 0de99930ff5da5c24aa2fbe34615abe52cc6c7db` |
| 独立 worktree | `/home/faye/diyu-demo-worktrees/m1-natural-interaction-context-v1` |
| 任务分支 | `task/m1-natural-interaction-context-v1`（已推送远程） |
| 已完成 | (1) 设计文档 [`V1_M1_TASK_CONTEXT_COMPILER_DESIGN_v0.1.md`](../decision-chain/docs/V1_M1_TASK_CONTEXT_COMPILER_DESIGN_v0.1.md)；(2) 编译器源码 `decision-chain/workflows/m1_context_compiler_v0.1.py`（P0 最小切片：9 个扁平信号字段）；(3) 真实 Dify 候选 App `dd638b91-d39f-4e92-a984-6ad1ab809119`（已定位真实自托管 Dify 1.16.1，与 A-0～A-4 证据同一实例）；(4) DSL 导入并发布三版（v0.1→越界给专业判断→v0.2 修复→A-0/A-2 受控等价回归中发现内部枚举代码泄漏→v0.3 修复）；(5) 六次真实 `/v1/chat-messages` 对话运行（RUN-001~003 + CE-A0/CE-A2/CE-general 首轮 + 三者复验），含两次自验发现并修复的真实缺陷，详见 [`V1_M1_CANDIDATE_RUN_001.md`](../decision-chain/evidence/V1_M1_CANDIDATE_RUN_001.md)；(6) 正式单测文件 `decision-chain/workflows/test_m1_context_compiler_v0.1.py`（29 用例全绿）；(7) A-0～A-4 受控等价回归**部分**完成，M1-AC-12 当前诚实状态见 evidence 文档 §九——A-0/A-2/普通咨询三类已覆盖，A-1/A-3/A-4(b) 因依赖 M1 P0 没有的按槽位接受/撤销状态机而结构性无法覆盖；(8) `project_content_task()` 投影函数（设计参照文档 §三）已实现——纯离线函数，不接入 Dify DSL（设计文档明确其只在移交 Content Brief 时按需调用，非本轮对话节点职责）；P0 快照结构性缺失的四项（`account_stage`／`expression_discretion`／`evidence_and_gaps`／`available_capacity`）如实标 `NOT_CAPTURED_IN_P0_SNAPSHOT`，M1 明确不做专业判断的四项（`audience_problem_scene`／`audience_shift`／`content_promise`／`post_publish_observation`）留给调用方经 `caller_supplied` 传入、未传入时如实计入 `projection_gaps`，不由 M1 编造内容；8 个新单测覆盖上述缺口标记、调用方传值透传、未知键拒绝、`cycle_role` 分支 |
| 已决定的范围边界 | Founder 2026-08-25 明确裁决：M1 严格对齐 Execution Prompt 本身，只做意图/编译层，不触碰 `v1_state` 既有线性锁、不改任何 Skill 正文；已写入设计文档 §四"已知限制" |
| 未完成 | 14 条快照语义×5 维度里仍缺 `evidence_bundle[]`/`market_observations[]`/`gaps[]`/`runtime_evidence[]`（数组型、多维度，设计文档 §七 登记的结构化输出稳定性风险未决，`account_stage`/`expression_discretion`/`capacity_triad` 已在本轮补齐，见下）；`call_intent` 对 CAP-01～08 的完整必需输入判据；`open_threads` 跨轮延迟表面化语义（需设计判断）；A-1/A-3/A-4(b) 的验收边界判断（需 Founder/独立审查裁定，见 evidence §九）；**v0.4 快照扩展未导入/发布到候选 App，live 端到端验证被阻塞**（见下）；独立 Reviewer；`M1-AC-00`～`M1-AC-15` 逐项验收 |
| 下一步可立即执行的动作 | **先解除 Dify 控制台会话阻塞**（`docker-api-1` 容器重启导致此前的 refresh_token 续期机制失效，执行侧未持有 Founder 明文密码，不重新索取——需要 Founder 提供新的登录方式或亲自登录后交接会话）；解除后把 v0.4 DSL 导入/发布并做真实回归复验；之后再继续扩展 `evidence_bundle[]` 等剩余数组型语义（先评估设计文档 §七 的结构化输出稳定性风险，必要时走"LLM 只出粗粒度信号，五维度由确定性代码推导默认值"降级路径）；把 evidence §九 的 M1-AC-12 部分满足状态提请独立审查/Founder 判断 |
| **v0.2 快照扩展（本轮新增，代码+单测已完成，live 未验证）** | 新增 `account_stage`／`expression_discretion`（剧情/二创/冲突/争议四项裁量）／`capacity_triad`（期望发布量/周期可用/基线三分）三组字段，均为扁平字符串/枚举、刻意回避嵌套结构风险；新增向前兼容的快照顶层键补齐逻辑（旧会话快照缺新字段时不丢数据、不崩溃）；`content_task` 投影同步消解三项 `NOT_CAPTURED_IN_P0_SNAPSHOT` 缺口；DSL 生成脚本同步更新（影子节点系统提示词、17 字段结构化输出 schema、默认快照 JSON）；单测从 29 个扩到 35 个全绿。**DSL 尚未导入/发布**——见上一行"下一步"的会话阻塞说明，详见 [`V1_M1_CANDIDATE_RUN_001.md` §十](../decision-chain/evidence/V1_M1_CANDIDATE_RUN_001.md) |
| Checkpoint 触发原因 | 正常阶段性收口（对话上下文即将压缩），非任务失败或外部中断；已提交的代码、证据、账本记录均已落盘，可凭本 Checkpoint 与 Git 历史直接续作 |
