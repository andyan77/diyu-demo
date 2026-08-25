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
| **状态** | `PLANNED` |

## 四、其他外部系统

| 系统 | 本任务是否写入 |
|---|---|
| Dify（发布／重绑／工作流） | **否** |
| 业务数据库 / Qdrant / ECS | **否** |
| 对外消息发送 | **否** |

`NONE_VERIFIED_SINCE_BASELINE` —— 自 `6ae78ab` 起，Dify／业务数据库／对外消息发送三类均无写入。**Git 推送类副作用见 §三 索引表**（条目会随任务增加，不在本行重复计数，避免静态数字漂移）。
