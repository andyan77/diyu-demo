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
| **状态** | `PLANNED` → **`STARTED`**（收口合并已发起）。**`CONFIRMED` 的唯一依据是上述远端核验通过**；按反自引用条款，最终 hash 不回写进同一提交 |

> **关于自引用**：SE-002 是本任务的 closing push。按合同，**最终远端 ref 与交付证据即为其确认依据**——
> **不得**为了把最终 commit hash 写回同一个 commit 而制造无穷追加提交。

## 四、其他外部系统

| 系统 | 本任务是否写入 |
|---|---|
| Dify（发布／重绑／工作流） | **否** |
| 业务数据库 / Qdrant / ECS | **否** |
| 对外消息发送 | **否** |

`NONE_VERIFIED_SINCE_BASELINE` —— 自 `6ae78ab` 起，除 SE-001／SE-002 外无其他外部副作用。
