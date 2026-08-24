# L2 · 任务状态与项目下一动作

> 规则正文见 [COLLAB_CONTINUITY_PROTOCOL.md](COLLAB_CONTINUITY_PROTOCOL.md)。
> **新会话先读本文件。** 追加式：只加不改，更正另起一条。
>
> **三个不能混的东西**（定义见 canonical §四）：
> **Checkpoint** = 任务没做完被中断的续跑点 ｜ **Final Manifest／最终交付引用** = 任务已终结的结论 ｜ **Current Handoff** = 项目层下一步。
> **本文件 §二 是 Current Handoff，不是 Checkpoint，不代表任何任务未完成。**

**当前基线**：`main @ 6ae78abf5967535bda81392255b8ee3e79e4bcb5`

---

## 一、按 `task_id` 的任务状态

| task_id | 终态？ | 状态引用 | 起算基线 |
|---|---|---|---|
| `COLLAB-LEDGER-BOOTSTRAP-001` | **非终态 —— 执行中**（见 §一.1） | [L1 §T-001](L1_TASK_MANIFESTS.md) · [L3 §CLOSEOUT](L3_ATTEMPTS_AND_EVIDENCE.md)（**当前**：收口）；ATT-001～005 **全部**为已判不通过的历史轮次，**不要**当成当前轮次 | `6ae78ab` |
| `V1-REBASE-EP00-CURRENT` | **非终态 —— 从未启动** | 无 Checkpoint（**没开始过 ≠ 被中断**） | `6ae78ab` |

### 一.1 `COLLAB-LEDGER-BOOTSTRAP-001`

| 项 | 值 |
|---|---|
| 状态 | **执行中（非终态）** —— 功能内容已冻结，A2 隔离验证与远程收口**尚未完成** |
| 终结依据 | **尚未产生。** 终态与 A1–A9 结果由收口时的 evidence-only 增量写入 [L3 §CLOSEOUT](L3_ATTEMPTS_AND_EVIDENCE.md)（**当前**：收口）；ATT-001～005 **全部**为已判不通过的历史轮次 |
| 最终交付引用 | **尚未产生** |
| Checkpoint | **无。** 本任务在**执行中**、**未被中断**，不满足写 Checkpoint 的条件（Checkpoint 只给「开工后被外部强制中断」的任务） |

### 一.2 `V1-REBASE-EP00-CURRENT`

| 项 | 值 |
|---|---|
| 状态 | **未开工** |
| 授权 | [上位合同](../decision-chain/docs/V1_DECISION_CHAIN_REBASE_PRODUCT_CONTRACT_v0.1.md) `PRODUCT_CONTRACT_ACCEPTED — REPO_PREFLIGHT_AUTHORIZED` —— **已授权，可立即开工** |
| Checkpoint | **无**。它从未启动，不存在续跑点 |
| 下一动作 | 见 §二 |

---

## 二、项目当前可执行动作（Current Handoff）

> **本节只维护：活动 `task_id` ＋ 依赖关系 ＋ 定位引用。**
> 每个活动 `task_id` **各自一行**。**这里没有、也不得有一个覆盖所有并行任务的全局「唯一下一步」。**
> 每行的下一动作四要素缺一不可：**动作 ／ 对象 ／ 输入或基线 ／ 完成信号**。
> 当同时有两个及以上任务在跑时，各任务细节写进各自的 `collab-ledger/tasks/<task_id>.md` 分区，本表只留定位引用。

| task_id | 依赖 | 定位引用 | 动作 | 对象 | 输入／基线 | 完成信号 |
|---|---|---|---|---|---|---|
| `COLLAB-LEDGER-BOOTSTRAP-001` | 无前置未决依赖 | [L1 §T-001](L1_TASK_MANIFESTS.md) · [L3 §CLOSEOUT](L3_ATTEMPTS_AND_EVIDENCE.md)（**当前**：收口）· [L5](L5_SIDE_EFFECTS.md) | 按 [收口 Delta](L1_TASK_MANIFESTS.md) 口径完成收口：**复用最近一次真实隔离验证**（不重开完整问答轮）→ 对受影响路径做**定向复验** → 写收口记录（C1–C6、已知问题登记、采用状态）→ `--no-ff` 合并进 `main` 并推送 | 分支 `chore/collab-ledger-bootstrap-001`；`collab-ledger/` 下 L2 §一.1、**L3 §CLOSEOUT**（**当前**槽位；**不是** §ATT-001～005，那五轮全部已判不通过）、L5 §三 | **可解算口径**：`git rev-parse chore/collab-ledger-bootstrap-001`，即该任务分支的 **tip**——这就是当前功能内容冻结提交。起算基线 `6ae78ab`。<br>**不要**用 §ATT-001.1 的 `0d6a4d2`、也不要用 §ATT-002.1 的 `8ada866`，那是已判不通过的历史冻结点。<br>**为什么不直接写 hash**：提交无法把自身 hash 写进自身；同 [L5 SE-002](L5_SIDE_EFFECTS.md) 的处置，以**分支 tip / 远端 ref** 为准，不制造无穷追加提交 | `git ls-remote origin refs/heads/main` 的 HEAD **等于**合并提交 hash，且本文件 §一.1 已记为终态 |
| `V1-REBASE-EP00-CURRENT` | 无前置未决依赖。**不依赖**子合同被接受 | [L1 定位表](L1_TASK_MANIFESTS.md) · 本文件 §一.2 | 执行**只读**仓库预检，逐项核验上位合同「授权状态与下一步」列的五项真实状态：① 现有目标路由 ② 现有创意锦标赛（CS-1）③ 六个 Skill 的价值耦合分档 ④ Dify 现有流程 ⑤ 远端真实运行版本 | 本仓库 `main`、六份 Skill 正文、`decision-chain/workflows/**`、`content-production/workflows/**`、真实 Dify 已发布版本 | `main @ 6ae78abf5967535bda81392255b8ee3e79e4bcb5`；五项核验清单出自[上位合同第 907–915 行](../decision-chain/docs/V1_DECISION_CHAIN_REBASE_PRODUCT_CONTRACT_v0.1.md) | 产出一份**只读**预检结论文档，五项**逐项**给出「仓库当前事实 + 与合同口径的差距」，并按 [L1](L1_TASK_MANIFESTS.md) 编译该任务 Manifest、按 [L3](L3_ATTEMPTS_AND_EVIDENCE.md) 记一条 Attempt。**核验完成前不得开始任何改造施工。** |

**一个活动 `task_id` 一行，本表不维护「共几个」的汇总**（数量随授权变化，写死必失真）。**各行互不覆盖**，也**不存在**一个凌驾其上的全局「唯一下一步」。新任务被授权时**新增一行**，已完成的任务移出本表、终态记进 §一。

> **本行是 A2 第 1 轮隔离验证查出来的缺陷修复。** 冻结提交 `0d6a4d2` 时本表**漏了执行中的 bootstrap 任务**，只列了未开工的预检任务，并错写成「当前活动 task_id 只有 1 个」——违反 A3 与「Current Handoff 只维护活动 task_id」。详见 [L3 §ATT-001](L3_ATTEMPTS_AND_EVIDENCE.md)。

---

## 三、不构成活动任务的（**不要**从这里取下一步）

| 项 | 为什么不能开工 |
|---|---|
| `SINGLE-ACCOUNT-SLICE-EP00`（子合同专项预检） | [子合同](../decision-chain/docs/V1_SINGLE_ACCOUNT_SLICE_CONTRACT_v0.1.md) 状态 `CONTRACT_REVISION_REQUIRED`，**未被 Founder 接受**。子合同只有被接受后才能成为其切片专项预检的依据。**执行侧不得自行宣布已接受。** |
| Skill 修改／DSL 改造／业务持久化建设／Dify 工作流施工 | 上位合同**只授权只读预检**。**文档语义对齐不等于授权施工。** |
| [生产差距登记](../decision-chain/docs/V1_PRODUCTION_GAP_REGISTER_v0.1.md) G-01～G-12 | 12 项全部未关闭，但它们是**开放 Gap，不是已授权任务**，也**不是**已排除路线（见 [L4](L4_FAILED_PATHS.md)） |
| `AO-EP00-HISTORICAL`（`feature/account-operation-v1 @ df94ed1`） | **只作历史参考**，不得冒充当前预检，不得直接合入 `main` |

---

## 四、非终态 Checkpoint 区

`NONE_VERIFIED_SINCE_BASELINE`

自起算基线 `6ae78ab` 起，**没有任何任务处于「开工后被中断」状态**，因此没有 Checkpoint。
（`V1-REBASE-EP00-CURRENT` 是**从未启动**，不属于此类；见 §一.2。）
