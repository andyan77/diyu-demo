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

---

## 二、项目当前可执行动作（Current Handoff）

> **本节只维护：活动 `task_id` ＋ 依赖关系 ＋ 定位引用。**
> 每个活动 `task_id` **各自一行**。**这里没有、也不得有一个覆盖所有并行任务的全局「唯一下一步」。**
> 每行的下一动作四要素缺一不可：**动作 ／ 对象 ／ 输入或基线 ／ 完成信号**。
> 当同时有两个及以上任务在跑时，各任务细节写进各自的 `collab-ledger/tasks/<task_id>.md` 分区，本表只留定位引用。
> **已完成的任务移出本表、终态记进 §一**——本表不维护「共几个」的汇总，数量随授权变化，写死必失真。

| task_id | 依赖 | 定位引用 | 动作 | 对象 | 输入／基线 | 完成信号 |
|---|---|---|---|---|---|---|
| `NONE` | — | — | — | — | — | — |

**当前没有任何已授权、待执行的工程任务。** `COLLAB-LEDGER-BOOTSTRAP-001`、`V1-REBASE-EP00-CURRENT`、`M0-EP00-ADOPTION-CLOSEOUT-001`、`V1-M0-1B-SLICE-CONTRACT-REVISION-001` 均已终结 `DONE`（见 §一），新会话**不需要、也不应该**重跑其中任何一个。

**已解决**：EP-00 报告 §十一「仍需 Founder 裁决的产品命题」已由 Founder 通过 F-01～F-10 十项裁决 + 四项定向纠偏答复，并落地进 [`V1_SINGLE_ACCOUNT_SLICE_CONTRACT_v0.2.md`](../decision-chain/docs/V1_SINGLE_ACCOUNT_SLICE_CONTRACT_v0.2.md)（已 `ACCEPTED`）。原"Founder 审阅并裁决 EP-00 §十一"这一权限动作**已完成**，不再是待办项。

**下一权限动作**（不是可执行工程任务，执行侧不得自行开工）：

| 动作 | 对象 | 输入／基线 | 完成信号 |
|---|---|---|---|
| Founder 下发完整 Execution Prompt | `V1-M0-SLICE-PREFLIGHT-AND-SHARED-CONTRACT-CLOSEOUT-001`（唯一后继任务，统一承接 `SINGLE-ACCOUNT-SLICE-EP00` 专项预检 → M0.3 四个共享合同 → Founder 阶段接受 → M0 收口） | 已接受的 [下位合同 v0.2](../decision-chain/docs/V1_SINGLE_ACCOUNT_SLICE_CONTRACT_v0.2.md)（`ACCEPTED`）＋ 已采用的 [通用 EP-00 报告](../decision-chain/docs/V1_REBASE_EP00_CURRENT_PREFLIGHT_v0.1.md) | Founder 下发该任务的完整 Execution Prompt（目前只有名称与一句话范围，执行侧**不得**据一句话范围自行编写并开工，**不得**自行推断其验收标准） |

---

## 三、不构成活动任务的（**不要**从这里取下一步）

| 项 | 为什么不能开工 |
|---|---|
| `SINGLE-ACCOUNT-SLICE-EP00`（子合同专项预检） | 下位合同已升级到 [v0.2](../decision-chain/docs/V1_SINGLE_ACCOUNT_SLICE_CONTRACT_v0.2.md)，状态 `ACCEPTED — SINGLE_ACCOUNT_SLICE_PREFLIGHT_AUTHORIZED`（Founder 2026-08-24 明确接受）——**依据已就位**，但仍不构成活动任务：**尚无独立 Execution Prompt**，实质工作已并入唯一后继 `V1-M0-SLICE-PREFLIGHT-AND-SHARED-CONTRACT-CLOSEOUT-001`（同样尚无完整 Prompt，见 §二） |
| Skill 修改／DSL 改造／业务持久化建设／Dify 工作流施工 | 上位合同**只授权只读预检**。**文档语义对齐不等于授权施工。** |
| [生产差距登记](../decision-chain/docs/V1_PRODUCTION_GAP_REGISTER_v0.1.md) G-01～G-12 | 均未关闭，但它们是**开放 Gap，不是已授权任务**，也**不是**已排除路线（见 [L4](L4_FAILED_PATHS.md)） |
| `AO-EP00-HISTORICAL`（`feature/account-operation-v1 @ df94ed1`） | **只作历史参考**，不得冒充当前预检，不得直接合入 `main` |

---

## 四、非终态 Checkpoint 区

`NONE_VERIFIED_SINCE_BASELINE`

自起算基线 `6ae78ab` 起，**没有任何任务处于「开工后被中断」状态**，因此没有 Checkpoint。
（`V1-REBASE-EP00-CURRENT` 是**从未启动**，不属于此类；见 §一.2。）
