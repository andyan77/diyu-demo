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

### SE-012 · 推送任务分支 `task/v1-m2-engineering-prompt-adoption-001`

| 项 | 值 |
|---|---|
| 所属 task_id | `V1-M2-ENGINEERING-PROMPT-ADOPTION-001` |
| 类型 | Git push（新建远程分支，独立于 `main`） |
| 目标 | `https://github.com/andyan77/diyu-demo.git` → `refs/heads/task/v1-m2-engineering-prompt-adoption-001` |
| 内容标识 | 落盘 `decision-chain/docs/M2_ENGINEERING_EXECUTION_PROMPT_v1.1.md` ＋ PROJECT_INDEX／L1／L2／L3／L5 账本登记（含自证哈希不一致披露） |
| 幂等信息 | 同一 commit 重复推送为空操作；**禁用** `--force` |
| 受控状态 | 可逆——任务分支可删；未触碰默认分支，随后经集成分支 `--no-ff` 合入 `main`（见 SE-013） |
| 核验依据 | `git ls-remote origin refs/heads/task/v1-m2-engineering-prompt-adoption-001` —— 以实时返回为准 |
| **状态** | `PLANNED` → **`CONFIRMED`** |
| **状态追加 1**（2026-08-25） | 推送成功：`* [new branch] task/v1-m2-engineering-prompt-adoption-001 -> task/v1-m2-engineering-prompt-adoption-001`。远端核验：`git ls-remote origin refs/heads/task/v1-m2-engineering-prompt-adoption-001` → `c8121179290637fc942204414b8465e87991e9a0`，与本地 `git rev-parse HEAD` 完全一致 |

### SE-013 · 采用进远程默认工作基线 `main`（M2 施工 Execution Prompt 落盘）

| 项 | 值 |
|---|---|
| 所属 task_id | `V1-M2-ENGINEERING-PROMPT-ADOPTION-001` |
| 类型 | Git merge（`--no-ff`，集成分支接入任务分支 tip，再合入 `main`）＋ push |
| 目标 | `https://github.com/andyan77/diyu-demo.git` → `refs/heads/main` |
| 前置基线 | `0de99930ff5da5c24aa2fbe34615abe52cc6c7db` |
| 内容标识 | 见 [L3 §十二 ATT-001](L3_ATTEMPTS_AND_EVIDENCE.md) |
| 幂等信息 | 快进保护：推送前 `fetch` 比对 `origin/main` 未漂移；**禁用** `--force`/`--amend`/`reset`/`squash`；不删除来源分支 `task/v1-m2-engineering-prompt-adoption-001` |
| 受控状态 | **不可逆**（公开仓库）；仅可用新提交前向修正 |
| 核验依据 | `git ls-remote origin refs/heads/main` 的 HEAD **等于**最终合并提交 hash |
| **状态** | `PLANNED` → **`CONFIRMED`** |
| **状态追加 1**（2026-08-25） | 集成分支 `chore/m2-engineering-prompt-adoption`（本地新建，源自 `main`，未推远程）完成两段 `--no-ff` 合并：① 接入任务分支 `task/v1-m2-engineering-prompt-adoption-001` tip `2db32b1`（零冲突，commit `a7d6944`）；② 合并进本地 `main`（合并提交 `1398c83a54fc5e9b89c397b20747818edb5616dc`）。推送前 `git fetch origin main` 核验 `origin/main` 仍为 `0de99930...`，未漂移。推送：`0de9993..1398c83  main -> main`。远程核验：`git ls-remote origin refs/heads/main` → `1398c83a54fc5e9b89c397b20747818edb5616dc`，与本地 `git rev-parse main` 完全一致。双向祖先核验通过（任务分支是新 main 祖先；旧 main tip `0de99930...` 仍是新 main 祖先，历史未改写）。全部受保护资产（四份共享合同、上位/下位合同、两份 EP-00、Phase0 前言、M1 落盘文档）blob hash 合并后重算，逐字未动。落盘的 `decision-chain/docs/M2_ENGINEERING_EXECUTION_PROMPT_v1.1.md` 最终 sha256 = `8008bebd04b35037e16f5462ea1b7284db7dec943e954263762bbdb4688bb0c6`，与落盘时一致。来源分支 `task/v1-m2-engineering-prompt-adoption-001` 远程保留，未删除 |

### SE-014 · 推送任务分支 `task/m2-business-persistence-version-feedback-v1`（工程执行，非落盘）

| 项 | 值 |
|---|---|
| 所属 task_id | `DIYU-V1-M2-BUSINESS-PERSISTENCE-VERSION-FEEDBACK-001` |
| 类型 | Git push（任务分支，独立于 `main`），3 次连续推送，同一目标 ref |
| 目标 | `https://github.com/andyan77/diyu-demo.git` → `refs/heads/task/m2-business-persistence-version-feedback-v1` |
| 内容标识 | 见 [L3 §十三 ATT-001](L3_ATTEMPTS_AND_EVIDENCE.md#十三-diyu-v1-m2-business-persistence-version-feedback-001) |
| 幂等信息 | 同一 commit 重复推送为空操作；**禁用** `--force` |
| 受控状态 | 可逆——任务分支可删；未触碰默认分支 |
| 核验依据 | `git push` 命令本身回显的 ref-update 行（`旧hash..新hash`），逐次核对 |
| **状态** | `PLANNED` → **`CONFIRMED`** |
| **状态追加 1** | `019df51..44f02dd`——首次工程执行修复批（`a3eeb2f` 独立审查 21 项缺陷修复、`0546f30` M2-AC-14、`d7f9e94` M2-AC-07、`44f02dd` M2-AC-15） |
| **状态追加 2** | `44f02dd..020bc58`——两轮独立审查发现的 4 个真实缺陷修复批 |
| **状态追加 3** | `020bc58..f09e292`——收口验证发现的 legacy-import 多快照 500 修复 |

### SE-015 · PostgreSQL 迁移（独立数据库 `diyu_business`）

| 项 | 值 |
|---|---|
| 所属 task_id | `DIYU-V1-M2-BUSINESS-PERSISTENCE-VERSION-FEEDBACK-001` |
| 类型 | Alembic 迁移，`docker-db_postgres-1` 内独立数据库 `diyu_business`（与 `dify`/`dify_plugin` 物理隔离，`diyu_app` 角色对后两者 `REVOKE ALL`） |
| 内容标识 | 7 个迁移线性链：`fdbd31cee7f9`(initial)→`6033064ae1ed`→`6bc000bb178d`→`fb5e3889277c`→`db747c8a1f80`(auth+race fixes)→`a1c5e7d4f2b9`(cycle_decisions)→`c3f8b2e6d0a4`(account 级幂等+legacy-import 隔离) |
| 幂等信息 | `alembic upgrade head` 对已应用版本为空操作；`downgrade`/`upgrade` 往返已在收口验证中核验对称（`c3f8b2e6d0a4` 一节） |
| 受控状态 | 可逆——全部迁移均有对称 `downgrade()`；数据库内容目前仅为工程测试数据，非真实经营数据 |
| 核验依据 | 现场 `alembic current` = `c3f8b2e6d0a4 (head)`；`alembic check` 无模型/schema 漂移 |
| **状态** | **`CONFIRMED`**（现场核验，非自报） |

### SE-016 · Dify 候选应用（沿用既有对象，本轮未新建/未发布新版本）

| 项 | 值 |
|---|---|
| 所属 task_id | `DIYU-V1-M2-BUSINESS-PERSISTENCE-VERSION-FEEDBACK-001` |
| 对象 | `app_id: 8f34e8a3-fb49-4d3e-a222-3d666e767adf`，`diyu 's Workspace`，workflow 类型，命名含 `DO NOT USE FOR PRODUCTION` |
| 本轮动作 | **无**——本轮新增的三个后端能力（M2-AC-07/14/15）未被该候选画布调用，候选契约未变，未重新导入/发布 |
| 已披露限制 | 按 Prompt `evidence_reuse_policy.criterion_dependency_map` 字面要求，应用后端变化后 AC-16 证据应刷新；本轮未重新触发画布真实运行（无可用已认证 Dify 会话，且核验到的 `dify-platform-expert` MCP 连接指向另一个不相关的 Dify 1.9.2 实例，判断不可用后放弃采用，未用其伪造证据）。等价 API 级证据（66 项回归，覆盖候选实际调用的全部端点契约）已现场验证，详见 `business-persistence/M2_ACCEPTANCE_EVIDENCE.md` M2-AC-16 行 |
| **状态** | 沿用既有对象，**未产生新副作用**；限制已披露，非隐藏 |
| **状态追加 1**（2026-08-25，Rebase/Errata 001，R-08） | 尝试通过 Console API 重建认证会话失败——本会话无可用 refresh_token，仓库内未发现任何已保存的 App API Key；未向用户索要或尝试重建密码。按 Rebase Prompt R-08.8"如果当前无法访问准确目标 Dify，M2-AC-16 = NOT_VERIFIED...不得用 API等价证据改判 PASS"，`M2-AC-16` 已在 `business-persistence/M2_ACCEPTANCE_EVIDENCE.md` 中从"PASS 但有限制"下修为 `NOT_VERIFIED`，本条同步更新 |

### SE-017 · 数据库权限修复（`REVOKE CONNECT`）——首次被拦截，Founder 授权后已执行

| 项 | 值 |
|---|---|
| 所属 task_id | `DIYU-V1-M2-BUSINESS-PERSISTENCE-VERSION-FEEDBACK-001` |
| 触发 | Rebase/Errata 001 R-09 现场负向核验发现：`diyu_app` 角色实际可以 `CONNECT` 到 `dify`/`dify_plugin` 数据库（`psql -U diyu_app -d dify -c "SELECT 1;"` 返回成功），表级 `SELECT` 仍被正确拒绝（`ERROR: permission denied for table accounts`），未读到任何真实数据；`pg_database.datacl` 显示 PUBLIC 默认 CONNECT 授权从未被显式撤销，与 `TECHNICAL_DECISION_RECORD.md` 声称的"REVOKE ALL"不一致 |
| 首次尝试 | `REVOKE CONNECT ON DATABASE dify FROM PUBLIC; ...`（以 postgres 超级用户执行）——**被 Claude Code 权限分类器拦截**，理由：该操作触及 `dify`/`dify_plugin`，不属于本 task_id 独占的 `diyu_business` 沙箱；未强行绕过、未改用其他方式尝试执行，如实记录为 `BLOCKED` |
| 授权 | Founder 2026-08-25 在本会话中对该具体、已明确说明内容与风险的操作明确答复"我授权，你是否可以执行？"，构成对此单一操作的授权 |
| 实际执行 | 修复前现场负向复现（确认漏洞真实存在）→ 以 `postgres` 超级用户执行 `REVOKE CONNECT ON DATABASE dify FROM PUBLIC, diyu_app;` 与对 `dify_plugin` 的同语句 → 修复后现场重测确认 `diyu_app` 对两库 `CONNECT` 均被拒绝（`FATAL: permission denied for database ... DETAIL: User does not have CONNECT privilege`）→ 回归验证 `diyu_app` 自身库 `diyu_business` 连接不受影响、Dify 自身容器（`postgres` 超级用户连接，天然绕过 CONNECT ACL）不受影响 |
| 结果 | `dify`/`dify_plugin` 的 `PUBLIC`/`diyu_app` CONNECT 权限已撤销；`diyu_app` 自身工作范围与 Dify 自身运行均未受损 |
| **状态** | `ATTEMPTED → BLOCKED` → **`EXECUTED`**（Founder 明确授权后完成，非执行侧自行解除拦截） |

### SE-018 · Dify 候选画布真实重跑（App API Key，R-08 解除）

| 项 | 值 |
|---|---|
| 所属 task_id | `DIYU-V1-M2-BUSINESS-PERSISTENCE-VERSION-FEEDBACK-001` |
| 触发 | R-08：`M2-AC-16` 要求最终候选在真实 Dify 目标环境重新运行，此前受限于无可用 Console 会话/API Key |
| 授权与凭据 | Founder 主动提供该候选应用（`app_id: 8f34e8a3-fb49-4d3e-a222-3d666e767adf`）专属的 App API Key；执行侧未索要 Console 会话或账号密码，Key 仅在内存中使用，未写入任何文件、commit 或本账本 |
| 执行 | `curl -X POST http://localhost/v1/workflows/run` 携带该 Key，输入六步场景字段（`actor_ref`/`workspace_id`/`account_id`/`idempotency_prefix`/`task_note`/`content_ref`/`platform`/`published_at`/`feedback_note`），`response_mode: blocking` |
| 结果 | `workflow_run_id: 1f123c37-c51c-4dad-a96c-e0696bd8b2e3`，`status: succeeded`，`total_steps: 16`，`elapsed_time: 0.43s`，`error: null`；对照 `FOUNDER_TEST_PACKAGE.md` 9 项判断标准逐项核验全部满足（`task_id`/`version_id`/`publish_instance_id` 均为真实 UUID；`projection_body.latest_snapshot.payload.note` 与填入原文逐字一致；`promote_body.promoted_by` 与填入 Actor Ref 一致；`current_cycle_body.label` 含本次运行标识） |
| 受影响对象 | 该候选应用自身的 workflow 执行记录（Dify 侧新增一条运行历史，`workspace_id: 68df687c-...`、`account_id: 12802f90-...` 下新增真实业务对象：1 个 task、1 个 cycle、1 个 content version、1 个 publish instance、1 个 feedback record）——均在该候选专用的测试 workspace/account 范围内，不触碰任何生产账号或其他工作区 |
| **状态** | `EXECUTED`——`M2-AC-16` 由 `NOT_VERIFIED` 转 `PASS` |

### SE-019 · Rebase/Errata Prompt 文件复制进任务分支

| 项 | 值 |
|---|---|
| 所属 task_id | `DIYU-V1-M2-BUSINESS-PERSISTENCE-VERSION-FEEDBACK-001` |
| 触发 | Founder 复核指出该 Prompt 文件此前只在主工作区作为未跟踪文件存在，未进入本任务分支或远程，脱离本分支单独审计时无法追溯授权来源 |
| 执行 | 将 `/home/faye/diyu-demo/M2_ENGINEERING_EXECUTION_PROMPT_v1.1_REBASE_ERRATA_001.md`（`sha256 = fbb65e1dcdb405a435f03fc8efa8f9828926d9881850aa7c86237bf267ef7c5d`）原样字节复制（保留原 CRLF 换行）进本任务分支 `business-persistence/M2_ENGINEERING_EXECUTION_PROMPT_v1.1_REBASE_ERRATA_001.md`，`diff` 核验字节完全一致；未修改主工作区原文件（仍保留在原位，未删除） |
| 顺带发现 | 该文件本身有一处未闭合 Markdown 代码围栏（外观像复制/转存截断），逐行核对至文末确认内容连续完整、以正常声明块结束，非内容缺失，仅格式缺陷；未修改原文件一字 |
| **状态** | `EXECUTED`——只在 `business-persistence/`（本任务已获授权的修改范围）内新增文件，未触碰主工作区或其他任务资产 |

## 四、其他外部系统

| 系统 | 本任务是否写入 |
|---|---|
| Dify（发布／重绑／工作流） | **否** |
| 业务数据库 / Qdrant / ECS | **否** |
| 对外消息发送 | **否** |

`NONE_VERIFIED_SINCE_BASELINE` —— 自 `6ae78ab` 起，Dify／业务数据库／对外消息发送三类均无写入。**Git 推送类副作用见 §三 索引表**（条目会随任务增加，不在本行重复计数，避免静态数字漂移）。
