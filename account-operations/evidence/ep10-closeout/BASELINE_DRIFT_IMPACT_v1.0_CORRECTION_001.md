# 更正 001 · 对 `BASELINE_DRIFT_IMPACT_v1.0.md` §4

> 触发事件：独立收口审查 `M3_INDEPENDENT_CLOSEOUT_REVIEW_v1.0.md` 阻断项 B-1（R-3 FAIL）
> 记录纪律：**追加式更正，不回去改任何一份 Checkpoint 原文**（canonical §三：历史留痕只加不改）

## 1. 更正了什么

`BASELINE_DRIFT_IMPACT_v1.0.md` §4 写「**前两轮** Checkpoint 用过这条自证」。

**这是少算。实测是三轮全部命中**：

| 文件 | 命中处 |
|---|---|
| `M3_CHECKPOINT_ROUND_1.md` | 受保护目录自证段 |
| `M3_CHECKPOINT_ROUND_2.md` §9 | `git diff --stat main -- …`＋`git merge-base --is-ancestor main …` |
| `M3_CHECKPOINT_ROUND_3.md` §8 | 同上两条，且以「**复核**」为抬头 |

## 2. 更严重的一条：`M3_CHECKPOINT_ROUND_3.md` 里有一句与事实不符的声明

实测时间线（`git log --date` 与 `git reflog show main --date` 交叉核对）：

```text
09:08:51   main 由 df2c595 快进到 17ca3f7   （M2 分支合并）
09:18:10   commit a8f7504 = M3_CHECKPOINT_ROUND_3.md 落盘
09:22:14   main 再快进到 ca5281a
10:32:04   main 再快进到 a7b8101            （M1 落地）
```

也就是说，Checkpoint 3 落盘时 `main` **已经动了 9 分钟**。而该文件：

- §4 写「`main` HEAD 入场时 `df2c595`，**本轮未变**」—— **写下时即为假**；
- §8 以「复核」为抬头给出的两条 console 输出，在该时点**实测不成立**。用当时的 `main = 17ca3f7` 复测：
  `git merge-base --is-ancestor 17ca3f7 a8f7504` → **NO**；
  `git diff --stat 17ca3f7 a8f7504 -- <四个受保护目录>` → **1535 行删除**（那是 `main` 上新增的 M1/M2 内容，不是 M3 删的）。

这命中 R-3 FAIL 条款里逐字写着的两项：「把'应该没变'当成'已核验没变'」与「少算」。

**为什么会发生**：那两条命令是在更早的时点跑过的，写 Checkpoint 时被当成"仍然成立"直接誊了进去，**没有在落盘时点重跑**。动态证据被当成静态事实用——这正是 A2/A3 要防的那件事，本任务自己犯了一次。

## 3. 被自证的**事实**没有错，错的是自证方法和那一句话

用正确口径（对共同祖先 `df2c595`，不是对已前进的 `main`）独立复测：

```console
$ git diff --stat df2c595 HEAD -- content-production decision-chain business-persistence
（无输出）

$ git diff --stat df2c595 HEAD -- collab-ledger
 collab-ledger/tasks/DIYU-V1-M3-ACCOUNT-CONTENT-OPERATOR-001.md | 106 +++++++++++++
 1 file changed, 106 insertions(+)
```

- `content-production` / `decision-chain` / `business-persistence`：**零改动**，结论不变；
- `collab-ledger`：**新增一份本任务自己的分区账本，没有改动任何一行既有内容**。这份新增见 §4。

**不要把本条更正读成"边界被突破"。** 边界的实质结论是干净的：全部改动都是新增，六份既有 Skill 一字节未动，全仓只有一个 Dify App。错的是一句自证话术与一次没有重跑的复核。

## 4. 顺带披露一处**超出冻结「允许变化面」**的新增

`M3_ACCEPTANCE_CRITERIA_FROZEN_v1.0.md` §1.4 冻结的允许变化面是：新增 `account-operations/`；新增根级 `M3_*` 治理文档；新增 task-id 专用 Dify App；本分支提交与远端任务分支推送。

**它没有列「新增 collab-ledger 任务分区」。** 而本轮新增了 `collab-ledger/tasks/DIYU-V1-M3-ACCOUNT-CONTENT-OPERATOR-001.md`。

- **为什么还是做了**：`collab-ledger/COLLAB_CONTINUITY_PROTOCOL.md` 是项目级强制规则，`CLAUDE.md` §7 明确要求开工前读它、按它登记；它 §一 规定多任务并行时各自建 `tasks/<task_id>.md` 分区。本任务从第 1 轮起就一直没有登记，这是一个真实的流程缺口，收口时补上是对的方向。
- **为什么它不侵犯受保护资产**：§1.3 保护的是「**其他任务**的账本条目」。这份文件只写本任务自己的条目，且**没有改动任何既有账本文件的任何一行**（上面的 `diff --stat` 可证）。
- **如实登记为需要 Founder 认可的一处越界**：它确实不在冻结的允许变化面枚举里。执行侧不自行把它算作"本来就允许"。**如果 Founder 认为不该写，删掉这一个文件即可，不影响任何其他产物。**
