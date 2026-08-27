# M3 回滚计划 **v1.1**（后继版本，不覆盖 v1.0）

> `supersedes`: `M3_ROLLBACK_PLAN_v1.0.md`（原文保留，不删不改）
> 为什么要有 v1.1：v1.0 里有两条已经不成立了——它写「Dify 对象**未创建**，无需回滚」
> 与「远端**从未推送**，无需回滚」。这两条在后续几轮都变了，冻结文档不原地改，另立后继版本。

## 1. 结论先行

| 项 | 结论 |
|---|---|
| 撤销 Git 侧改动 | **一条命令**（删分支 + 删 worktree），`main` 不受任何影响 |
| `main` 是否需要恢复 | **不需要**——从未被触碰，入场基线 `df2c5952551f` 仍是本分支的祖先 |
| 受保护模块是否需要恢复 | **不需要**——相对入场基线零修改零删除 |
| **Dify 对象** | **已创建一个**（task-id 专用候选 App），需要手动删除；**已实测可从快照恢复** |
| **远端** | **已推送任务分支**，需要删除远端分支 |
| 不可自动撤销的残留 | 运行中 M2 实例里的一份取证 workspace（沿用 v1.0 §4，未变） |

## 2. Git 侧：全部改动仍然是新增

相对入场基线 `df2c5952551f`：**476 个文件，476 个 `A`（新增）、0 个修改、0 个删除。**

```console
$ git merge-base main task/m3-account-content-operator-v1
df2c5952551f386a0e9a509404357f23c1d223c9
$ git rev-parse HEAD
6963829d6a2c7356c22fe1a4905eccbd7e919aa2
$ git diff --stat df2c595 HEAD -- content-production decision-chain business-persistence
（无输出 —— 三个受保护目录相对入场基线零改动）
```

`collab-ledger/` 下只多了本任务自己的账本条目一个文件。

**如实记录的一处变化**：`main` 在施工期间由 M1 落地工作推进到 `a7b810109f43`，
其中改到了 `business-persistence/`。这**不影响回滚**（本分支从未合并 main），
但它对 `AC-12`/`AC-13` 的绑定有影响，单独记在
`account-operations/evidence/ep13-a3-main-moved/A3_IMPACT_MAIN_MOVED.md`。

## 3. Dify 侧：实测过的恢复路径

v1.0 写「未创建 Dify 对象」，现在创建了**恰好一个**：

```text
App    M3 单账号持续运营候选 | DIYU-V1-M3-ACCOUNT-CONTENT-OPERATOR-001 | CANDIDATE TEST ONLY
id     b7fb5b1a-9278-426c-bb8a-f9f288639548
mode   workflow
```

**回滚方式**：Dify 控制台里删除该 App。它是任务专用、非生产，删除不影响任何其他对象。

**恢复路径已实测**（不是设想，见 `account-operations/evidence/ep10-closeout-v12/dify_rollback_drill.json`）：

| 步 | 做了什么 | 实测结果 |
|---|---|---|
| 1 | 导出 DSL（可搬走的备份） | 133083 字符，sha256 `cd9ff8b35efe0ab4…` |
| 2 | 快照草稿图（就地备份） | graph sha256 `043f50eab8c4b235…`，7 节点 |
| 3 | **故意破坏**草稿（改节点名 + 删掉通往 end 的边） | HTTP 200 |
| 4 | 确认确实坏了 | graph sha 变为 `926e8bf141dce446…`，边数 6 → 5 |
| 5 | 从快照恢复 | HTTP 200 |
| 6 | 确认恢复 | graph sha 回到 `043f50eab8c4b235…`，**与备份逐位相同**，7 节点 6 边 |
| 7 | 确认**已发布版本**全程未被本演练触碰 | 已发布版本 `2026-08-27 00:24:41.859681`，graph sha `043f50eab8c4b235…` |

`RESTORE_SUCCEEDED = True`。

**演练只动草稿、不动已发布版本**，因此绑定在已发布版本上的取证运行不受影响——
这一条由第 7 步实测，不是声明。

## 4. 远端：已推送，需要一条命令删除

v1.0 写「从未推送」，现在推了：

```text
远端分支  origin/task/m3-account-content-operator-v1
远端 HEAD  b86513a514475c1c97c070322f1cd1d697026216
```

**回滚方式**：`git push origin --delete task/m3-account-content-operator-v1`。
`main` 的远端从未被本任务写过。

## 5. 完整撤销清单（按顺序执行即可）

```bash
git push origin --delete task/m3-account-content-operator-v1     # 远端分支
git worktree remove /home/faye/diyu-demo-worktrees/m3-account-content-operator-v1
git branch -D task/m3-account-content-operator-v1                # 本地分支
# Dify 控制台删除 App b7fb5b1a-9278-426c-bb8a-f9f288639548
```

执行后 `main` 与四个受保护目录保持原状，无需任何恢复动作。

## 6. 沿用 v1.0 未变的部分

§4「不可自动撤销的残留：运行中 M2 实例里的一份取证 workspace」逐字沿用，本轮未新增此类残留。

```text
END_MARKER = M3-ROLLBACK-PLAN-v1.1-END
```
