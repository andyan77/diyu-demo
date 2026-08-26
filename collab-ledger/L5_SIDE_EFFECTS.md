# L5 · 外部副作用

> 规则正文见 [COLLAB_CONTINUITY_PROTOCOL.md](COLLAB_CONTINUITY_PROTOCOL.md)。追加式：只加不改，更正另起一条。
>
> **往仓库外写之前和之后各记一次。** 之前记 `PLANNED`，之后按实际观测改记一条新状态行。
> **起算基线 `main @ 6ae78abf5967535bda81392255b8ee3e79e4bcb5`。** 基线之前的推送**不补造**条目。

## 一、状态枚举（固定六值，不得自创）

```text
PLANNED | STARTED | CONFIRMED | FAILED_NO_EFFECT | UNKNOWN | COMPENSATED
```

## 二、原始权威归属

| 事实 | 谁是原始权威 |
|---|---|
| Git 推送到底发生没发生、落到哪个 hash | **Git 历史与远端 ref**（`git ls-remote`），**不是本账本** |
| Dify 发布／重绑、数据库写入、消息发送 | 目标系统自身的响应与状态 |

**本账本只提供定位与状态，不复制 Git 历史。**

## 三、副作用条目（自起算基线起）

> **按 `task_id` 分区。** 并行任务多起来时，各任务的副作用写进 `collab-ledger/tasks/<task_id>.md`，本文件只留索引行。

| 条目 | 所属 task_id | 目标 | 状态 |
|---|---|---|---|
| SE-001 | `COLLAB-LEDGER-BOOTSTRAP-001` | 远程分支 `chore/collab-ledger-bootstrap-001` | 见下 |
| SE-002 | `COLLAB-LEDGER-BOOTSTRAP-001` | 远程默认分支 `main`（收口推送） | 见下 |
| SE-003 | `V1-REBASE-EP00-CURRENT` | 远程分支 `task/v1-rebase-ep00-current-m0-preflight` | 见下 |
| SE-004 | `M0-EP00-ADOPTION-CLOSEOUT-001` | 远程默认分支 `main`（采用 EP-00 交付 + 当前投影纠偏） | 见下 |
| SE-005 | `V1-M0-1B-SLICE-CONTRACT-REVISION-001` | 远程分支 `task/v1-m0-1b-slice-contract-revision-001` | 见下 |
| SE-006 | `V1-M0-1B-SLICE-CONTRACT-REVISION-001` | 远程默认分支 `main`（采用下位合同 v0.2 ACCEPTED 交付 + 当前投影纠偏） | 见下 |

### SE-001 · 推送任务分支 `chore/collab-ledger-bootstrap-001`

| 项 | 值 |
|---|---|
| 所属 task_id | `COLLAB-LEDGER-BOOTSTRAP-001` |
| 类型 | Git push（新建远程分支） |
| 目标 | `https://github.com/andyan77/diyu-demo.git` → `refs/heads/chore/collab-ledger-bootstrap-001` |
| 内容标识 | 见 [L3 §ATT-001.1](L3_ATTEMPTS_AND_EVIDENCE.md) 的 tested functional hash |
| 幂等信息 | 同一 commit 重复推送为空操作；**禁用** `--force` |
| 受控状态 | 可逆——分支可删；**未触碰默认分支** |
| 原始响应 | 2026-08-24 推送成功：`* [new branch]  chore/collab-ledger-bootstrap-001 -> chore/collab-ledger-bootstrap-001` |
| 核验依据 | `git ls-remote origin refs/heads/chore/collab-ledger-bootstrap-001` —— **以实时返回为准**。本栏**不再登记具体 hash**（登记必滞后；历史推送记录见下方状态追加行） |
| **状态** | `PLANNED` → **`CONFIRMED`**（attempt-1 的功能冻结提交已在远程分支上） |
| **状态追加 1**（2026-08-24） | attempt-2 冻结提交推同一分支：`0d6a4d2..8873881`，远端 ref → `8873881964569310252326976eab4a563757c084`。状态仍 `CONFIRMED` |
| **状态追加 2**（2026-08-24） | attempt-2 最终冻结推同一分支：`8873881..8ada866`，远端 ref → `8ada8663db357d91c1c4038ef944d9a3c6a1c930`。状态仍 `CONFIRMED` |
| **为什么要追加** | A2 第 2 轮对抗性隔离单元实测 `refs/remotes/origin/chore/...` 已到 `8ada866`，而本条当时只记 `0d6a4d2`，并把最新值甩给了尚是 `PENDING` 的 `§ATT-002.5`——**账本保留了一个已知与远端 ref 不符的 hash**，违反本文件 §二「远端 ref 才是原始权威」。按 canonical §三「只加不改」以追加行更正，不覆盖原记录 |
| **状态追加 3**（2026-08-24） | attempt-3 冻结提交推同一分支：`8ada866..d07ddd7`，远端 ref → `d07ddd7984800b091bfe45dcf0454dd97ab2564c`。状态仍 `CONFIRMED` |
| **状态追加 4 · 口径更正**（2026-08-24） | A2 第 3 轮对抗性单元实测：本条每次只记到「上一次推送」，最新值总被甩给尚是 `PENDING` 的下一节——**同一缺陷模式连续两轮复现**。**改口径**：本条不再逐次登记 hash，**以 `git ls-remote origin refs/heads/chore/collab-ledger-bootstrap-001` 的实时返回为准**（L5 §二 早已写明「远端 ref 才是原始权威，不是本账本」）。上面三条历史追加**保留不删**，作为该缺陷的证据 |
| 状态 | `CONFIRMED` —— 分支确已存在于远端；**具体 hash 以远端 ref 实时查询为准** |

### SE-002 · 采用进远程默认工作基线 `main`（收口推送）

| 项 | 值 |
|---|---|
| 所属 task_id | `COLLAB-LEDGER-BOOTSTRAP-001` |
| 类型 | Git merge（`--no-ff`，真合并）＋ push |
| 目标 | `https://github.com/andyan77/diyu-demo.git` → `refs/heads/main` |
| 前置基线 | `6ae78abf5967535bda81392255b8ee3e79e4bcb5` |
| 内容标识 | 合并提交 hash，见 [L3 §CLOSEOUT](L3_ATTEMPTS_AND_EVIDENCE.md) |
| 幂等信息 | 快进保护：推送前重新 `fetch` 比对；**禁用** `--force` / `--amend` / `reset` / `squash`；不删除来源分支 |
| 受控状态 | **不可逆**（公开仓库，推上去即世界可见）；仅可用新提交前向修正，**不得改写历史** |
| 原始响应 | 见 [L3 §收口.7](L3_ATTEMPTS_AND_EVIDENCE.md) |
| 核验依据 | `git ls-remote origin refs/heads/main` 的 HEAD **等于**合并提交 hash —— **远端 ref 是原始权威，不是本账本** |
| **状态** | `PLANNED` → `STARTED` → **`CONFIRMED`** |
| 实际发生 | 2026-08-24 `--no-ff` 真合并：`6ae78ab` + `5a02310` → 合并提交 **`16ecb2a81bd5bf0f168f4f5ad28fdf3f46b2ce7d`**，推送 `6ae78ab..16ecb2a  main -> main` |
| **远端核验（原始权威）** | `git ls-remote origin refs/heads/main` → `16ecb2a81bd5bf0f168f4f5ad28fdf3f46b2ce7d` == 合并提交 ✅。`git ls-tree origin/main collab-ledger/` 返回 6 个文件 ✅。`CLAUDE.md` §7 指针在远端 main 上可达 ✅ |
| 反自引用说明 | 本行写的是**已发生的**合并 hash，不是本提交自身的 hash，**到此终止**。此后再有一次采用即以**当时的远端 ref** 为准，不再回写 |

> **关于自引用**：SE-002 是本任务的 closing push。按合同，**最终远端 ref 与交付证据即为其确认依据**——
> **不得**为了把最终 commit hash 写回同一个 commit 而制造无穷追加提交。

### SE-003 · 推送任务分支 `task/v1-rebase-ep00-current-m0-preflight`

| 项 | 值 |
|---|---|
| 所属 task_id | `V1-REBASE-EP00-CURRENT` |
| 类型 | Git push（新建远程分支） |
| 目标 | `https://github.com/andyan77/diyu-demo.git` → `refs/heads/task/v1-rebase-ep00-current-m0-preflight` |
| 内容标识 | 见 [L3 §四 ATT-001.1](L3_ATTEMPTS_AND_EVIDENCE.md) 的 tested functional hash（分支 tip，不写死字面值，避免自引用） |
| 幂等信息 | 同一 commit 重复推送为空操作；**禁用** `--force` |
| 受控状态 | 可逆——任务分支可删；**未触碰默认分支**，不合并、不建 PR |
| 核验依据 | `git ls-remote origin refs/heads/task/v1-rebase-ep00-current-m0-preflight` —— **以实时返回为准**，本栏不登记具体 hash |
| **状态** | `PLANNED` → **`CONFIRMED`** |
| **状态追加 1**（2026-08-24） | 推送成功：`* [new branch] task/v1-rebase-ep00-current-m0-preflight -> task/v1-rebase-ep00-current-m0-preflight`。远端核验：`git ls-remote origin refs/heads/task/v1-rebase-ep00-current-m0-preflight` → `8413a94d3125d54426527be987d082ed28017c96`，与本地 `git rev-parse HEAD` 完全一致。未直推／未合并 `main`，未建 PR |

### SE-004 · 采用进远程默认工作基线 `main`（EP-00 交付 + 当前投影纠偏）

| 项 | 值 |
|---|---|
| 所属 task_id | `M0-EP00-ADOPTION-CLOSEOUT-001` |
| 类型 | Git merge（`--no-ff`，真合并，两段：① 集成分支接入 EP-00 tip ② 集成分支合并进 main）＋ push |
| 目标 | `https://github.com/andyan77/diyu-demo.git` → `refs/heads/main` |
| 前置基线 | `4d84cd2a4bbd9bcbcff97105f226cf5652f13e29` |
| 内容标识 | 见 [L3 §五 ATT-001.1](L3_ATTEMPTS_AND_EVIDENCE.md) 的 tested functional hash（分支 tip，不写死字面值，避免自引用） |
| 幂等信息 | 快进保护：推送前重新 `fetch` 比对；**禁用** `--force` / `--amend` / `reset` / `squash`；不删除来源分支 `task/v1-rebase-ep00-current-m0-preflight` |
| 受控状态 | **不可逆**（公开仓库，推上去即世界可见）；仅可用新提交前向修正，**不得改写历史** |
| 核验依据 | `git ls-remote origin refs/heads/main` 的 HEAD **等于**最终合并提交 hash —— **远端 ref 是原始权威，不是本账本** |
| **状态** | `PLANNED` → **`CONFIRMED`** |
| **状态追加 1**（2026-08-24） | 集成分支 `chore/m0-ep00-adoption-closeout-001`（本地新建，源自 `main`，未推远程）完成两段 `--no-ff` 合并：① 接入来源分支 `task/v1-rebase-ep00-current-m0-preflight` tip `48c8275`（零冲突，file delta 与规划观察完全一致）；② 叠加本任务的 canonical／L2／L1／L3／L5 当前投影纠偏与记账后，合并进本地 `main`（合并提交 `2dc4b5921bcfbe86c880c45696b0ece8367966c1`）。推送：`4d84cd2..2dc4b59  main -> main`。远程核验：`git ls-remote origin refs/heads/main` → `2dc4b5921bcfbe86c880c45696b0ece8367966c1`，与本地 `git rev-parse main` 完全一致。`git merge-base --is-ancestor` 双向核验：来源分支 tip 与旧 `main` tip（`4d84cd2`）均为新 `main` 的祖先。来源分支 `task/v1-rebase-ep00-current-m0-preflight` 远程核验仍为 `48c8275e8aa576be7c037303348de0dfb5677641`，未被删除、未被改写 |

### SE-005 · 推送任务分支 `task/v1-m0-1b-slice-contract-revision-001`

| 项 | 值 |
|---|---|
| 所属 task_id | `V1-M0-1B-SLICE-CONTRACT-REVISION-001` |
| 类型 | Git push（新建远程分支，独立于 `main`） |
| 目标 | `https://github.com/andyan77/diyu-demo.git` → `refs/heads/task/v1-m0-1b-slice-contract-revision-001` |
| 内容标识 | 见 [L3 §六 ATT-001.1](L3_ATTEMPTS_AND_EVIDENCE.md) 的 tested functional hash（分支 tip，不写死字面值） |
| 幂等信息 | 同一 commit 重复推送为空操作；**禁用** `--force` |
| 受控状态 | 可逆——任务分支可删；**未触碰默认分支**，不合并、不建 PR |
| 核验依据 | `git ls-remote origin refs/heads/task/v1-m0-1b-slice-contract-revision-001` —— 以实时返回为准 |
| **状态** | `PLANNED` → **`CONFIRMED`** |
| **状态追加 1**（2026-08-24） | 推送成功：`* [new branch] task/v1-m0-1b-slice-contract-revision-001 -> task/v1-m0-1b-slice-contract-revision-001`。远端核验：`git ls-remote origin refs/heads/task/v1-m0-1b-slice-contract-revision-001` → `e21ff4d11fc7d90b25168844260b8e325e1179d1`，与本地 `git rev-parse HEAD` 完全一致。未直推／未合并 `main`，未建 PR（GitHub 自动提示的 PR 创建链接未使用）；`git fetch` 后核验 `origin/main` 仍为 `f94d7a754a46c64f4b3e2f4e48cc4c3faa5b319a`，未变 |
| **状态追加 2**（2026-08-24） | attempt-2（四项定向纠偏 + F-10）推送：`922a99b..c32a42e  task/v1-m0-1b-slice-contract-revision-001 -> task/v1-m0-1b-slice-contract-revision-001`。远端核验：`git ls-remote origin refs/heads/task/v1-m0-1b-slice-contract-revision-001` → `c32a42e4c3121951a5557840ac3a87c7d1ee8dce`，与本地 `git rev-parse HEAD` 完全一致；同次查询 `refs/heads/main` 仍为 `f94d7a754a46c64f4b3e2f4e48cc4c3faa5b319a`，未变。状态仍 `CONFIRMED` |
| **状态追加 3**（2026-08-24） | Founder 接受后登记接受记录，推送：`9687e90..a3d8940  task/v1-m0-1b-slice-contract-revision-001 -> task/v1-m0-1b-slice-contract-revision-001`。远端核验：`git ls-remote` → `a3d8940c276c1682047d5c3b8417ca884e5d979b`，与本地一致。状态仍 `CONFIRMED` |

### SE-006 · 采用进远程默认工作基线 `main`（下位合同 v0.2 ACCEPTED 交付 + 当前投影纠偏）

| 项 | 值 |
|---|---|
| 所属 task_id | `V1-M0-1B-SLICE-CONTRACT-REVISION-001` |
| 类型 | Git merge（`--no-ff`，真合并，两段：① 集成分支接入任务分支 tip ② 集成分支合并进 main）＋ push |
| 目标 | `https://github.com/andyan77/diyu-demo.git` → `refs/heads/main` |
| 前置基线 | `f94d7a754a46c64f4b3e2f4e48cc4c3faa5b319a` |
| 内容标识 | 见 [L3 §六 ATT-003.1](L3_ATTEMPTS_AND_EVIDENCE.md) |
| 幂等信息 | 快进保护：推送前 `fetch` 比对 `origin/main` 未漂移；**禁用** `--force` / `--amend` / `reset` / `squash`；不删除来源分支 `task/v1-m0-1b-slice-contract-revision-001` |
| 受控状态 | **不可逆**（公开仓库，推上去即世界可见）；仅可用新提交前向修正，**不得改写历史** |
| 核验依据 | `git ls-remote origin refs/heads/main` 的 HEAD **等于**最终合并提交 hash —— **远端 ref 是原始权威，不是本账本** |
| **状态** | `PLANNED` → **`CONFIRMED`** |
| **状态追加 1**（2026-08-24） | 集成分支 `chore/m0-1b-adoption-closeout`（本地新建，源自 `main`，未推远程）完成两段 `--no-ff` 合并：① 接入任务分支 `task/v1-m0-1b-slice-contract-revision-001` tip `a3d8940`（零冲突）；② 叠加 L1／L2 当前投影纠偏（commit `732c27f`）后，合并进本地 `main`（合并提交 `b305e1eb6f058a2d89b2dcec8aa21a9a98080e58`）。推送：`f94d7a7..b305e1e  main -> main`。远程核验：`git ls-remote origin refs/heads/main` → `b305e1eb6f058a2d89b2dcec8aa21a9a98080e58`，与本地 `git rev-parse main` 完全一致。`git merge-base --is-ancestor` 双向核验通过。来源分支 `task/v1-m0-1b-slice-contract-revision-001` 远程核验仍为 `a3d8940c276c1682047d5c3b8417ca884e5d979b`，未被删除、未被改写 |

### SE-007 · 推送任务分支 `task/v1-m0-slice-preflight-and-shared-contract-closeout-001`

| 项 | 值 |
|---|---|
| 所属 task_id | `V1-M0-SLICE-PREFLIGHT-AND-SHARED-CONTRACT-CLOSEOUT-001` |
| 类型 | Git push（新建远程分支，独立于 `main`） |
| 目标 | `https://github.com/andyan77/diyu-demo.git` → `refs/heads/task/v1-m0-slice-preflight-and-shared-contract-closeout-001` |
| 内容标识 | Phase A（commit `4681cc6`）＋ Phase B（commit `c1156aa`）＋ Phase C 等待期 Checkpoint（commit `66194fe`） |
| 幂等信息 | 同一 commit 重复推送为空操作；**禁用** `--force` |
| 受控状态 | 可逆——任务分支可删；**未触碰默认分支**，不合并、不建 PR（GitHub 自动提示的 PR 创建链接未使用） |
| 核验依据 | `git ls-remote origin refs/heads/task/v1-m0-slice-preflight-and-shared-contract-closeout-001` —— 以实时返回为准 |
| **状态** | `PLANNED` → **`CONFIRMED`** |
| **状态追加 1**（2026-08-25） | 推送成功：`* [new branch] task/v1-m0-slice-preflight-and-shared-contract-closeout-001 -> task/v1-m0-slice-preflight-and-shared-contract-closeout-001`。远端核验：`git ls-remote origin refs/heads/task/v1-m0-slice-preflight-and-shared-contract-closeout-001` → `66194fe8e3375c23d14c5bbb8369e14e2ca189b1`，与本地 `git rev-parse HEAD` 完全一致。未直推／未合并 `main`，未建 PR。推送目的：使 Phase C 等待期 Checkpoint（见 [L2 §四](L2_TASK_STATE_AND_HANDOFF.md)）在本地状态丢失时仍可从远程恢复 |
| **状态追加 2**（2026-08-25） | SE-007 登记本身推送：`66194fe..d5edf63`。远端核验：`git ls-remote` → `d5edf63`，一致 |
| **状态追加 3**（2026-08-25） | Phase D 内容变更（四份共享合同 `ACCEPTED` + 根索引同步）推送：`d5edf63..34880b2`。远端核验：`git ls-remote origin refs/heads/task/v1-m0-slice-preflight-and-shared-contract-closeout-001` → `34880b230d60f61227b8a14cc95248e74833041b`，与本地一致。此后任务分支未再变更，`34880b2` 是其最终 tip，后续 Phase D 收口在独立集成分支上进行（见 SE-008） |

### SE-008 · 采用进远程默认工作基线 `main`（M0.2B 专项预检 + M0.3 四份共享合同 ACCEPTED 交付 + 当前投影纠偏）

| 项 | 值 |
|---|---|
| 所属 task_id | `V1-M0-SLICE-PREFLIGHT-AND-SHARED-CONTRACT-CLOSEOUT-001` |
| 类型 | Git merge（`--no-ff`，真合并，两段：① 集成分支接入任务分支 tip ② 集成分支合并进 main）＋ push |
| 目标 | `https://github.com/andyan77/diyu-demo.git` → `refs/heads/main` |
| 前置基线 | `0eba71a85916d4d993313c015dc8ad87f180d4de` |
| 内容标识 | 见 [L3 §七 ATT-003.1](L3_ATTEMPTS_AND_EVIDENCE.md) |
| 幂等信息 | 快进保护：推送前 `fetch` 比对 `origin/main` 未漂移；**禁用** `--force` / `--amend` / `reset` / `squash`；不删除来源分支 `task/v1-m0-slice-preflight-and-shared-contract-closeout-001` |
| 受控状态 | **不可逆**（公开仓库，推上去即世界可见）；仅可用新提交前向修正，**不得改写历史** |
| 核验依据 | `git ls-remote origin refs/heads/main` 的 HEAD **等于**最终合并提交 hash —— **远端 ref 是原始权威，不是本账本** |
| **状态** | `PLANNED` → **`CONFIRMED`** |
| **状态追加 1**（2026-08-25） | 集成分支 `chore/m0-slice-preflight-shared-contract-adoption`（本地新建，源自 `main`，未推远程）完成两段 `--no-ff` 合并：① 接入任务分支 `task/v1-m0-slice-preflight-and-shared-contract-closeout-001` tip `34880b2`（零冲突，commit `07a75b8`）；② 叠加 L1／L2／L3 当前投影纠偏（commit `fd350e3`）后，合并进本地 `main`（合并提交 `df2f73987780ea49c1b0e3c25368180105635f94`）。推送前 `git fetch origin main` 核验 `origin/main` 仍为 `0eba71a`，未漂移。推送：`0eba71a..df2f739  main -> main`。远程核验：`git ls-remote origin refs/heads/main` → `df2f73987780ea49c1b0e3c25368180105635f94`，与本地 `git rev-parse main` 完全一致。`git merge-base --is-ancestor` 双向核验通过（任务分支是 main 祖先；旧 main tip `0eba71a` 仍是新 main 祖先，未改写历史）。v0.1／v0.2／通用 EP-00 三份受保护文件 blob hash 合并后重算，逐字未动。来源分支 `task/v1-m0-slice-preflight-and-shared-contract-closeout-001` 远程核验仍为 `34880b230d60f61227b8a14cc95248e74833041b`，未被删除、未被改写 |

### SE-009 · 推送任务分支 `task/v1-m1-m4-phase0-preamble-adoption-and-desktop-pack-001`

| 项 | 值 |
|---|---|
| 所属 task_id | `V1-M1-M4-PHASE0-PREAMBLE-ADOPTION-AND-DESKTOP-PACK-001` |
| 类型 | Git push（新建远程分支，独立于 `main`） |
| 目标 | `https://github.com/andyan77/diyu-demo.git` → `refs/heads/task/v1-m1-m4-phase0-preamble-adoption-and-desktop-pack-001` |
| 内容标识 | commit `b5b268b1a50fa4294d6f74866e190e1e3ee420a1`——L2 两处独立纠偏 + L1/L3 该任务 `BLOCKED` 终态登记 |
| 幂等信息 | 同一 commit 重复推送为空操作；**禁用** `--force` |
| 受控状态 | 可逆——任务分支可删；**未触碰默认分支**，不合并、不建 PR（本任务未达成完整 P0 交付，Prompt §5"Git 采用与远程收口"流程未触发） |
| 核验依据 | `git ls-remote origin refs/heads/task/v1-m1-m4-phase0-preamble-adoption-and-desktop-pack-001` —— 以实时返回为准 |
| **状态** | `PLANNED` → **`CONFIRMED`** |
| **状态追加 1**（2026-08-25） | 推送成功：`* [new branch] task/v1-m1-m4-phase0-preamble-adoption-and-desktop-pack-001 -> task/v1-m1-m4-phase0-preamble-adoption-and-desktop-pack-001`。远端核验：`git ls-remote origin refs/heads/task/v1-m1-m4-phase0-preamble-adoption-and-desktop-pack-001` → `b5b268b1a50fa4294d6f74866e190e1e3ee420a1`，与本地 `git rev-parse HEAD` 完全一致。未直推／未合并 `main`，未建 PR。推送目的：使本次 `BLOCKED` 终态记录（含已完成的 L2 纠偏）在远程可见、可续跑，不因本地状态丢失而需要重做 |

> **记录缺口说明（本任务发现，未回补）**：`V1-M1-M4-PHASE0-PREAMBLE-ADOPTION-AND-DESKTOP-PACK-001` 的 P0-A 完成后合入 `main`、以及 `V1-M1-M4-PHASE0-DECISION-STATE-CLOSEOUT-001` 合入 `main` 这两次远程默认分支采用，L1/L2/L3 均写"见 L5"，但本文件当时未追加对应 SE 条目（本文件在此之前止于 SE-009）。这是此前任务遗留的账本记录缺口，不是本任务范围内容，本任务不回填，仅如实指出，供后续任务或 Founder 决定是否需要补记。

### SE-010 · 推送任务分支 `task/v1-m1-engineering-prompt-adoption-001`

| 项 | 值 |
|---|---|
| 所属 task_id | `V1-M1-ENGINEERING-PROMPT-ADOPTION-001` |
| 类型 | Git push（新建远程分支，独立于 `main`） |
| 目标 | `https://github.com/andyan77/diyu-demo.git` → `refs/heads/task/v1-m1-engineering-prompt-adoption-001` |
| 内容标识 | 落盘 `decision-chain/docs/M1_ENGINEERING_EXECUTION_PROMPT_v1.2.md` ＋ PROJECT_INDEX／L1／L2／L3／L5 账本登记 |
| 幂等信息 | 同一 commit 重复推送为空操作；**禁用** `--force` |
| 受控状态 | 可逆——任务分支可删；未触碰默认分支，随后经集成分支 `--no-ff` 合入 `main`（见 SE-011） |
| 核验依据 | `git ls-remote origin refs/heads/task/v1-m1-engineering-prompt-adoption-001` —— 以实时返回为准 |
| **状态** | `PLANNED` → **`CONFIRMED`** |
| **状态追加 1**（2026-08-25） | 推送成功：`* [new branch] task/v1-m1-engineering-prompt-adoption-001 -> task/v1-m1-engineering-prompt-adoption-001`。远端核验（首次遇代理超时 `408`，重试后成功，非实质阻塞）：`git ls-remote origin refs/heads/task/v1-m1-engineering-prompt-adoption-001` → `341da44d189bee5c9f05fa9ce7e9d398f8331b85`，与本地 `git rev-parse HEAD` 完全一致 |

### SE-011 · 采用进远程默认工作基线 `main`（M1 施工 Execution Prompt 落盘）

| 项 | 值 |
|---|---|
| 所属 task_id | `V1-M1-ENGINEERING-PROMPT-ADOPTION-001` |
| 类型 | Git merge（`--no-ff`，集成分支接入任务分支 tip，再合入 `main`）＋ push |
| 目标 | `https://github.com/andyan77/diyu-demo.git` → `refs/heads/main` |
| 前置基线 | `2a0822692802ac084d92e032f098da33079f063d` |
| 内容标识 | 见 [L3 §十 ATT-001](L3_ATTEMPTS_AND_EVIDENCE.md) |
| 幂等信息 | 快进保护：推送前 `fetch` 比对 `origin/main` 未漂移；**禁用** `--force`/`--amend`/`reset`/`squash`；不删除来源分支 `task/v1-m1-engineering-prompt-adoption-001` |
| 受控状态 | **不可逆**（公开仓库）；仅可用新提交前向修正 |
| 核验依据 | `git ls-remote origin refs/heads/main` 的 HEAD **等于**最终合并提交 hash |
| **状态** | `PLANNED` → **`CONFIRMED`** |
| **状态追加 1**（2026-08-25） | 集成分支 `chore/m1-engineering-prompt-adoption`（本地新建，源自 `main`，未推远程）完成两段 `--no-ff` 合并：① 接入任务分支 `task/v1-m1-engineering-prompt-adoption-001` tip `06870b8`（零冲突，commit `2d3084a`）；② 合并进本地 `main`（合并提交 `2ccd6d847f119c2280031902c98d511fb33aaa1f`）。推送前 `git fetch origin main` 核验 `origin/main` 仍为 `2a082269`，未漂移。推送：`2a08226..2ccd6d8  main -> main`。远程核验：`git ls-remote origin refs/heads/main` → `2ccd6d847f119c2280031902c98d511fb33aaa1f`，与本地 `git rev-parse main` 完全一致。双向祖先核验通过（任务分支是新 main 祖先；旧 main tip `2a082269` 仍是新 main 祖先，历史未改写）。全部受保护资产（四份共享合同、上位/下位合同、两份 EP-00、Phase0 前言）blob hash 合并后重算，逐字未动。落盘的 `decision-chain/docs/M1_ENGINEERING_EXECUTION_PROMPT_v1.2.md` 最终 sha256 = `b0adc1fc770abcb09dc2466d36a4803e3dba81ddafb63876d396e10848c37e4a`，与落盘时一致。来源分支 `task/v1-m1-engineering-prompt-adoption-001` 远程保留，未删除 |

### SE-012 · 创建 Dify 专用候选 App（`DIYU-V1-M1-NATURAL-CONTEXT-001`）

| 项 | 值 |
|---|---|
| 所属 task_id | `DIYU-V1-M1-NATURAL-CONTEXT-001` |
| 类型 | Dify 控制台 API 写入（`POST /console/api/apps`，新建 App） |
| 目标 | 本机自托管 Dify（`/home/faye/dify/docker/`，version 1.16.1，`http://localhost`）——与 A-0～A-4 证据绑定的同一实例（现有 App `310ddfcf-e0fb-4211-af98-3d101725e07a` 已核实在同一工作区列表中） |
| 凭据来源 | Founder 2026-08-25 会话内直接提供控制台登录邮箱与密码；未写入仓库任何文件，仅用于本机临时 cookie jar（`$TMPDIR` 范围内，不在仓库路径下） |
| 内容标识 | 新建 App id `dd638b91-d39f-4e92-a984-6ad1ab809119`，name `DIYU V1 M1 Natural Context Candidate v0.1`，mode `advanced-chat`，创建时 `workflow: null`（空工作流，尚未导入任何节点） |
| 幂等信息 | 创建动作本身不可重放去重（每次调用会新建一个 App）；已现场核验创建前工作区内不存在任何名称/描述包含 `M1`／`NATURAL-CONTEXT`／`DIYU-V1-M1` 的 App（25 个既有 App 逐一核对），本次是唯一一次创建 |
| 受控状态 | 可逆——该 App 本身可删除（`app.acl.delete` 权限已授予）；**未触碰任何现有 App**（25 个既有 App 逐一核对未被读写、未被引用、未被修改） |
| 核验依据 | `GET /console/api/apps` 返回列表包含该 App id 且字段与创建响应一致 —— 以该接口实时返回为准 |
| **状态** | `PLANNED` → **`CONFIRMED`** |
| **状态追加 1**（2026-08-25） | 创建请求 `POST /console/api/apps` 返回 `201`，响应体含完整 App 对象（id/name/mode/site 均确认），`api_base_url: http://localhost/v1`，`site.access_token` 已生成但未使用；后续核验 `GET /console/api/apps?page=1&limit=20` 返回列表中新 App 存在，字段一致 |

### SE-013 · 导入工作流 DSL、创建 API Key、两次发布、三次真实对话运行

| 项 | 值 |
|---|---|
| 所属 task_id | `DIYU-V1-M1-NATURAL-CONTEXT-001` |
| 目标 App | `dd638b91-d39f-4e92-a984-6ad1ab809119`（SE-012 新建，专用候选 App，不涉及任何既有 App） |
| 操作序列 | ① `POST /console/api/apps/imports`（DSL v0.1，`mode:yaml-content`）→ `completed`；② `POST /console/api/apps/{id}/workflows/publish`（`marked_name: m1-v0.1`）；③ `POST /console/api/apps/{id}/api-keys` 新建一个 API Key（未写入仓库，仅存本机临时文件 `$TMPDIR` 范围内）；④ `POST /v1/chat-messages` 真实运行 RUN-001（`conversation_id 9f9922aa-...`）；⑤ 同会话内真实运行 RUN-002，发现真实缺陷（专业判断越界）；⑥ 修复系统提示词后重新执行 ①②（DSL v0.2，`marked_name: m1-v0.2`）；⑦ 新会话真实运行 RUN-003 复验缺陷已修复 |
| 内容标识 | DSL 源：`decision-chain/workflows/build_m1_candidate_dsl_v0.1.py`（可重新生成）＋ `decision-chain/workflows/m1_context_compiler_v0.1.py`；三次真实运行详情见 [`decision-chain/evidence/V1_M1_CANDIDATE_RUN_001.md`](../decision-chain/evidence/V1_M1_CANDIDATE_RUN_001.md) |
| 幂等信息 | 导入/发布均为幂等覆盖（同一 app_id，非新建）；三次对话运行各自产生独立 `conversation_id`/`message_id`，不可重放去重，原始 id 见证据文件 |
| 受控状态 | 可逆——工作流可再次导入覆盖；对话记录属于候选 App 内测试数据，非生产数据；**未触碰任何既有 App、既有 Skill 正文、既有主 Chatflow** |
| 核验依据 | `GET /console/api/apps/{id}/workflows/draft` 返回节点与预期一致；`GET /console/api/apps/{id}/workflows/publish` 返回已发布版本；三次真实运行的 `conversation_id`/`message_id` 见证据文件，可用同一 API Key 或控制台会话日志核对 |
| **状态** | `PLANNED` → **`CONFIRMED`** |

### SE-014 · 会话 access_token 过期后用 refresh_token 续期（未再次索要密码）、DSL v0.3 导入发布、三次受控等价回归运行

| 项 | 值 |
|---|---|
| 所属 task_id | `DIYU-V1-M1-NATURAL-CONTEXT-001` |
| 目标 App | `dd638b91-d39f-4e92-a984-6ad1ab809119`（同 SE-012/SE-013，非新建） |
| 触发原因 | 上次 Checkpoint 后本轮延续工作时，之前保存的控制台会话 `access_token` 已过期（`GET /console/api/apps` 返回 `401 Invalid Authorization token`）；未重新索要 Founder 密码，改为读 Dify 后端源码（`docker exec docker-api-1` 读 `controllers/console/auth/login.py` 的 `RefreshTokenApi`）确认存在 `POST /console/api/refresh-token`，凭仍在有效期内的 `refresh_token` cookie换发新 `access_token`/`csrf_token`，续期成功（`200 {"result":"success"}`），全程未接触明文密码 |
| 操作序列 | ① 用 `test_m1_context_compiler_v0.1.py`（本轮新增，见下）之外的真实 Dify 对话做 A-0～A-4 受控等价回归，发现真实缺陷：`_dialogue_directive` 把内部枚举代码（如 `MATRIX`、`NO_PHYSICAL_ENTRY_YET`）原样拼进给对话 LLM 的指令文本，被复述给用户且在 CE-A2 场景里被错误表述成"用户提到的"内容；② 修复 `m1_context_compiler_v0.1.py`（新增 `CAPABILITY_LABEL_ZH`/`BLOCK_REASON_LABEL_ZH` 人话标签映射，`_dialogue_directive` 改用标签且不再断言"用户点名"）；③ 重新生成 DSL（`build_m1_candidate_dsl_v0.1.py`，DSL v0.3）；④ `POST /console/api/apps/imports` 导入（`app_id` 定向，非新建）；⑤ `POST .../workflows/publish`（`marked_name: v0.3`）；⑥ 用同一枚 SE-013 已创建的 API Key 重新运行 CE-A0/CE-A2 并新增 CE-general（一次"普通咨询不误触发专业模块"受控等价检查），确认泄漏已修复且无新回归 |
| 内容标识 | 修复后源码 `decision-chain/workflows/m1_context_compiler_v0.1.py`；受控等价回归详情与 conversation_id/message_id 见 [`decision-chain/evidence/V1_M1_CANDIDATE_RUN_001.md`](../decision-chain/evidence/V1_M1_CANDIDATE_RUN_001.md) 新增章节 |
| 幂等信息 | 导入/发布同 SE-013，幂等覆盖；三次新对话各自独立 `conversation_id` |
| 受控状态 | 可逆；仅作用于本任务专用候选 App；**未触碰任何既有 App、既有 Skill 正文、既有主 Chatflow**；`refresh-token` 操作本身只读续期一个既有会话，不创建新账号权限、不修改任何账号数据 |
| 核验依据 | 导入/发布响应见 `dify_import3_resp.json`/`dify_publish3_resp.json`（本机临时文件）；三次回归运行的 answer 文本经关键词扫描确认不含内部枚举代码 |
| **状态** | `PLANNED` → **`CONFIRMED`** |

### SE-015 · refresh_token 续期尝试失败（如实记录未成功的外部调用，非成功副作用）

| 项 | 值 |
|---|---|
| 所属 task_id | `DIYU-V1-M1-NATURAL-CONTEXT-001` |
| 触发原因 | 继续本轮快照 v0.2 扩展工作时，`GET /console/api/apps?limit=1`（带既有 cookie）返回 `401`；沿用 SE-014 已验证的免密码续期路径，`POST /console/api/refresh-token`（带 `refresh_token` cookie） |
| 实际结果 | 续期请求本身返回 `200 {"result":"success"}`，但用续期后的 `access_token`（JWT 本身按 `exp` 字段判断仍在有效期内）重新请求 `/console/api/apps` 仍返回 `401` |
| 根因判断 | `docker ps` 显示 `docker-api-1`/`docker-redis-1` 等容器 `created` 时间为 3 天前但 `Up` 时长仅 8 小时，判断本机 Docker 服务在会话期间发生过一次重启；推断服务端会话/刷新令牌校验所依赖的存储（通常是 Redis）在重启时被清空或重建，导致旧 `refresh_token` 在服务端已不被承认，即使其 JWT 本身未过期。已用 `curl http://localhost/console/api/system-features`（无需鉴权）确认 Dify 服务本身健康可达，排除"服务未启动"这一更简单的解释 |
| 未采取的动作 | 未尝试猜测、爆破或以任何方式绕过登录；未向 Founder 重新索要明文密码（沿用 SE-014 建立的凭据最小暴露原则）；未修改任何 Dify 账号/权限配置 |
| 后续影响 | 本轮快照 v0.2 扩展当时**未能导入/发布到候选 App 做真实回归**；阻塞已于同日通过 SE-016（Founder 本人操作）解除 |
| **状态** | **`CONFIRMED`**（记录的是"尝试续期但未恢复访问"这一实际发生的外部调用序列，不是声称已完成的正面副作用） |

### SE-016 · Founder 本人完成 v0.4 DSL 导入与发布；执行侧用 App API Key 跑真实回归

| 项 | 值 |
|---|---|
| 所属 task_id | `DIYU-V1-M1-NATURAL-CONTEXT-001` |
| 目标 App | `dd638b91-d39f-4e92-a984-6ad1ab809119`（同 SE-012/013/014，非新建） |
| 操作方 | **控制台导入与发布由 Founder 本人在浏览器里完成**（2026-08-25）——执行侧因 SE-015 记录的会话失效且未持有明文密码，把重新生成的 DSL 文件（`m1_candidate_dsl_v0.4.yml`）通过 SendUserFile 交给 Founder，由 Founder 在已登录的控制台会话内完成导入（覆盖同一 App 草稿，非新建）与发布；执行侧全程未接触、未索取任何登录凭证 |
| 执行侧后续操作 | 发布确认后，执行侧用 SE-013 已创建的 App 级 API Key（`app-fHRsI6...`，非控制台会话，无导入/发布权限，仅能调用 `/v1/chat-messages` 等公开运行时接口）跑真实回归 CE-v0.2-01：① 新对话第一轮陈述账号阶段/四项表达裁量/产能三分；② 同会话第二轮提出执行请求，验证跨轮持久化 |
| 内容标识 | 两轮真实运行的 `conversation_id`/`message_id`、`m1_shadow` 推理轨迹逐字复述持久化快照的证据，详见 [`V1_M1_CANDIDATE_RUN_001.md` §十](../decision-chain/evidence/V1_M1_CANDIDATE_RUN_001.md) |
| 幂等信息 | 导入/发布为幂等覆盖（同一 app_id）；两轮对话共享同一 `conversation_id`，`message_id` 各自独立 |
| 受控状态 | 可逆——工作流历史版本（v0.1～v0.3）未删除，可随时回退；仅作用于本任务专用候选 App；**未触碰任何既有 App、既有 Skill 正文、既有主 Chatflow** |
| 核验依据 | 两次 `/v1/chat-messages` 响应（本机临时文件 `ce_v0_2_01_resp.json`/`ce_v0_2_02_resp.json`）：`answer` 字段无内部字段泄漏，`metadata.reasoning.m1_shadow` 第二轮逐字包含第一轮写入的三组新字段值 |
| **状态** | `PLANNED` → **`CONFIRMED`** |

### SE-017 · Founder 本人完成 v0.5 DSL 导入与发布；执行侧用 App API Key 跑 v0.3 字段真实回归

| 项 | 值 |
|---|---|
| 所属 task_id | `DIYU-V1-M1-NATURAL-CONTEXT-001` |
| 目标 App | `dd638b91-d39f-4e92-a984-6ad1ab809119`（同 SE-012/013/014/016，非新建） |
| 操作方 | **控制台导入与发布由 Founder 本人在浏览器里完成**——执行侧把重新生成的 DSL 文件（`m1_candidate_dsl_v0.5.yml`）通过 SendUserFile 交给 Founder，由 Founder 在已登录的控制台会话内完成导入（覆盖同一 App 草稿，非新建）与发布，覆盖 v0.4；执行侧全程未接触、未索取任何登录凭证 |
| 执行侧后续操作 | 发布确认后，执行侧用 SE-013 已创建的 App 级 API Key（`app-fHRsI6...`）跑真实回归 CE-v0.3-01：① 新对话第一轮陈述一条 FACT 性质的经营事实；② 同会话第二轮提出一条 REFERENCE 性质的参考对象偏好，验证跨轮持久化与 nature 枚举的 REFERENCE 分支 |
| 内容标识 | 两轮真实运行的 `conversation_id`/`message_id`、`m1_shadow` 推理轨迹逐字复述第一轮持久化证据条目（`ev_001`）及其 `confirmation: SYSTEM_TENTATIVE`，详见 [`V1_M1_CANDIDATE_RUN_001.md` §十一](../decision-chain/evidence/V1_M1_CANDIDATE_RUN_001.md) |
| 幂等信息 | 导入/发布为幂等覆盖（同一 app_id）；两轮对话共享同一 `conversation_id`，`message_id` 各自独立 |
| 受控状态 | 可逆——工作流历史版本（v0.1～v0.4）未删除，可随时回退；仅作用于本任务专用候选 App；**未触碰任何既有 App、既有 Skill 正文、既有主 Chatflow** |
| 核验依据 | 两次 `/v1/chat-messages` 响应（本机临时文件 `ce_v0_3_01_resp.json`/`ce_v0_3_02_resp.json`）：`answer` 字段经关键词扫描（`FACT`/`PREFERENCE`/`REFERENCE`/`UNSTATED`/`evidence_bundle`/`SYSTEM_TENTATIVE`/`SYSTEM_INFERENCE`/`ev_00`/`DISCUSS`/`FOCUS`/`THIS_ACCOUNT`/`NOT_CAPTURED_IN_P0_SNAPSHOT`）均未命中；`metadata.reasoning.m1_shadow` 第二轮逐字包含第一轮写入的证据条目与 `confirmation` 值 |
| **状态** | `PLANNED` → **`CONFIRMED`** |

### SE-018 · 补记远程任务分支 10 次推送（正式 §8 独立审查发现的账本缺口，补造历史）

| 项 | 值 |
|---|---|
| 所属 task_id | `DIYU-V1-M1-NATURAL-CONTEXT-001` |
| 目标 | 远程分支 `https://github.com/andyan77/diyu-demo.git` `task/m1-natural-interaction-context-v1` |
| 触发原因 | 正式 §8 独立审查（见 evidence §十二）核对发现：本任务分支自开工以来共真实推送 10 次（`git reflog show refs/remotes/origin/task/m1-natural-interaction-context-v1` 逐条可查），但 L5 此前一条都没记录——本任务其余批次只记了 Dify 侧副作用（SE-012～017），Git 推送这一类side effect被漏记。本条是发现后的补记，不是本次新推送 |
| 推送记录（commit hash / 本地推送时间，均已用 `git ls-remote` 核验远端与本地 `refs/remotes/origin/...` 一致） | `1c1fe4e`(09:55) → `146c39b`(09:59) → `083cd36`(10:37) → `25c1cc1`(10:49) → `500791d`(11:10) → `3a4ddb9`(11:19) → `875d6df`(11:32) → `b2258e7`(12:03) → `bc224aa`(13:17) → `7258fae`(18:18)，均为 2026-08-25 |
| 幂等信息 | Git push 本身不可重放去重；每次推送对应一个真实 commit，commit 历史见 `git log --oneline task/m1-natural-interaction-context-v1` |
| 受控状态 | 可逆——分支可回退到任一历史 commit；**未 force push、未改写历史、未合并/直推 `main`**（`git log main..task/m1-natural-interaction-context-v1` 与 `git log task/m1-natural-interaction-context-v1..main` 均可核验） |
| 核验依据 | 本条记录时刻 `git ls-remote origin refs/heads/task/m1-natural-interaction-context-v1` 返回 `7258fae2d731c179b6a5dd980f809a8cb917c228`，与本地 `git rev-parse HEAD` 完全一致 |
| **状态** | **`CONFIRMED`**（补记，非本次新触发） |

### SE-019 · Founder 本人完成 v0.6 DSL 导入与发布；执行侧用 App API Key 跑 B-6 判据前提 live 实测

| 项 | 值 |
|---|---|
| 所属 task_id | `DIYU-V1-M1-NATURAL-CONTEXT-001` |
| 目标 App | `dd638b91-d39f-4e92-a984-6ad1ab809119`（同前，非新建） |
| 操作方 | **控制台导入与发布由 Founder 本人完成**——执行侧把 `m1_candidate_dsl_v0.6.yml` 通过 SendUserFile 交给 Founder，由 Founder 完成导入（覆盖同一 App 草稿）与发布，覆盖 v0.5；执行侧全程未接触登录凭证 |
| 执行侧后续操作 | 发布确认后，直连数据库核验发布对象（`workflow_id 2cdd034f-...`，发布时间 2026-08-26 03:36:38 UTC，图字节 118772，逐字节核对 23 键 required 与三个新字段存在）；随后用 App API Key 发起 6 次真实调用，专项验证 B-6 判据前提（"缺 1-2 个字段"的部分失败模式是否真实存在）及优先级替换语义在真实模型下是否生效 |
| 内容标识 | 6 次调用的 `conversation_id`/`message_id`（`adb194c3`/`40955a0c`/`eb385da8`/`73a15660`/`b0d3c431`+`7a207029` 同会话）；直连 `m1_shadow`/`m1_compiler` 节点 `outputs` 原始 JSON，非经 `answer` 转述；详见 [`V1_M1_CANDIDATE_RUN_001.md` §十四](../decision-chain/evidence/V1_M1_CANDIDATE_RUN_001.md) |
| 幂等信息 | 导入/发布为幂等覆盖（同一 app_id）；6 次调用中 5 个各自独立会话，1 组为同一 `conversation_id` 下的两轮 |
| 受控状态 | 可逆——工作流历史版本（v0.1～v0.6）未删除；仅作用于本任务专用候选 App；未触碰任何既有 App、既有 Skill 正文、既有主 Chatflow |
| 核验依据 | 直连数据库 `workflow_node_executions.outputs`，逐条解析确认 23/23 键齐全（6/6）；`m1_compiler` 输出的 `goal_structure.priority_order` 两轮分别为 `["涨粉优先于转化"]`→`["转化优先于涨粉"]`，替换而非累积 |
| **状态** | `PLANNED` → **`CONFIRMED`** |

### SE-020 · Founder 本人完成 v0.7 DSL 导入与发布；执行侧跑 B-3/B-4/B-5 live 回归，直连数据库取证

| 项 | 值 |
|---|---|
| 所属 task_id | `DIYU-V1-M1-NATURAL-CONTEXT-001` |
| 目标 App | `dd638b91-d39f-4e92-a984-6ad1ab809119`（同前，非新建） |
| 操作方 | **控制台导入与发布由 Founder 本人完成**（覆盖 v0.6）；执行侧全程未接触登录凭证 |
| 执行侧后续操作 | 执行侧准备 curl 脚本（App API Key，仅 `/v1/chat-messages`／`/v1/files/upload` 权限），**由 Founder 在本机终端代跑**（执行侧 Bash 沙箱对带 `Authorization` 头的网络调用有权限分类器拦截，同 SE-013 起沿用的做法一致，只是这次连读操作也被拦，需要 Founder 代跑）；执行侧随后直连本机 Docker 内 Dify 数据库（`docker exec docker-db_postgres-1 psql`，只读）核对 `workflow_node_executions`/`messages`/`message_files` 等表的真实落库内容 |
| 内容标识 | B-4/B-5 相关多组 `conversation_id`/`message_id`（详见 evidence §十七正文引用的具体值）；B-3 诊断定位到 `workflows.id = 900e8c67-e952-432b-9e62-fe3c4112df41` 的 `features.file_upload` 字段与已发布 DSL 内容不一致 |
| 幂等信息 | 导入/发布为幂等覆盖（同一 app_id）；每次调用各自独立会话或同一 `conversation_id` 下的多轮 |
| 受控状态 | 可逆——工作流历史版本未删除；仅作用于本任务专用候选 App；未触碰任何既有 App、既有 Skill 正文、既有主 Chatflow |
| 核验依据 | 直连数据库逐字段核对 `m1_shadow`/`m1_compiler` 节点 `outputs`；B-3 根因用 `workflows.features::text` 与已生成 DSL 源码逐字段比对确认不一致 |
| **状态** | **`CONFIRMED`** |

### SE-021 · 执行侧对本机 Dify 数据库执行一次定向 UPDATE，修正候选 App 的 `features.file_upload` 配置（Founder 授权、Founder 本人执行写入命令）

| 项 | 值 |
|---|---|
| 所属 task_id | `DIYU-V1-M1-NATURAL-CONTEXT-001` |
| 触发 | Founder 会话内消息原文：「卡在应用级"文件上传"开关没有被这次导入正确应用，这个问题，你应该在后台修复，不能什么问题都推给founder」——明确指示这类问题不应止步于诊断/转交 Founder，执行侧应在自身权限范围内直接修复 |
| 目标 | 本机自建 Docker 内的 Dify Postgres 数据库（非远程、非生产实例，与前述 SE-019/SE-020 用于取证的只读连接是同一个数据库容器）；`workflows` 表 `id = 900e8c67-e952-432b-9e62-fe3c4112df41`（候选 App `dd638b91-...` 当前生效的 workflow 记录）一行的 `features` 列 |
| 操作方 | 执行侧先只读取出完整现有 `features` JSON，用 Python 做字典级合并（只替换 `file_upload` 一个子键，`opening_statement`/`speech_to_text`/`retriever_resource` 等其余全部字段原样保留），生成新 JSON 与对应 `UPDATE ... WHERE id = '...'` 语句，写入本地脚本文件；**执行侧 Bash 沙箱的权限分类器拦截了直接执行该 UPDATE**（数据库写操作与此前网络调用一样被拦），**由 Founder 在自己终端里执行该条已经准备好的命令**，执行侧不持有绕过该拦截的通道 |
| 变更内容 | `file_upload.enabled` 由 `false` 改为 `true`；`allowed_file_types` 由 `["image"]` 改为 `["custom"]`；`allowed_file_extensions` 由图片扩展名列表改为 `[".txt", ".md"]`；`allowed_file_upload_methods` 由 `["local_file", "remote_url"]` 改为 `["local_file"]`；`number_limits` 由 `3` 改为 `1`；新增 `fileUploadConfig` 子对象——**全部取值与本仓库 `build_m1_candidate_dsl_v0.1.py` 里声明的 `file_upload` 配置逐字段一致**，不是执行侧自行拟定的新配置 |
| 幂等信息 | UPDATE 按主键定点覆盖，可重复执行、结果幂等；执行前已用 `SELECT` 读出并保存修改前的完整 `features` 原文（本条记录内可见），可据此逐字段还原 |
| 受控状态 | **可逆**——修改前的完整 `features` 原文已如实记录在本条与 evidence §十七；仅影响候选 App 这一条记录，未触碰生产库、未触碰其他 App、未触碰用户账号/凭证类数据；本机自建测试环境，非远程/共享基础设施 |
| 核验依据 | 写入后 `SELECT features::text ilike '%"enabled": true%'` 返回真；随后重新上传文件测试，`message_files` 表出现记录、`m1_extract`/`m1_join` 真实产出非空文本，确认修复生效 |
| **状态** | **`CONFIRMED`** |

## 四、其他外部系统

| 系统 | 本任务是否写入 |
|---|---|
| Dify（发布／重绑／工作流） | **是**——`DIYU-V1-M1-NATURAL-CONTEXT-001` 任务已创建专用候选 App，见 SE-012；仅限该 App，未触碰任何既有 App |
| 业务数据库 / Qdrant / ECS | **否** |
| 对外消息发送 | **否** |

**Git 推送类副作用见 §三 索引表**（条目会随任务增加，不在本行重复计数，避免静态数字漂移）。Dify 写入类副作用见本节 SE-012 起。
