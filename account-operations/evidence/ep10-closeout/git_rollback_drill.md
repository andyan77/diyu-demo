# EP-10 · 代码侧回滚与可恢复性演练（非破坏式）

> **口径更正**：`main` 已在本任务施工期间前进到 `a7b8101`（见 BASELINE_DRIFT_IMPACT_v1.0.md）。
> 受保护目录的"零改动"自证因此改为**对共同祖先 `df2c595` 比对**，而不是对当前 `main` 比对。

```console
$ git rev-parse main
a7b810109f43a4bf500acc285baab477d96796e3
$ git rev-parse HEAD
7564896f9c601c7d6a5c420de5701f08dc0d7277
$ git merge-base main HEAD    # 共同祖先 = 本任务入场基线
df2c5952551f386a0e9a509404357f23c1d223c9
$ git merge-base --is-ancestor df2c595 HEAD && echo BASE_IS_ANCESTOR_OK
BASE_IS_ANCESTOR_OK
$ git merge-base --is-ancestor df2c595 main && echo BASE_STILL_ON_MAIN_OK
BASE_STILL_ON_MAIN_OK

# 受保护目录：对入场基线零改动
$ git diff --stat df2c595 -- content-production decision-chain business-persistence collab-ledger
(空 = 受保护目录零改动)

# 本分支相对入场基线：全部是新增，无修改无删除
$ git diff --name-status df2c595 | awk '{print $1}' | sort | uniq -c
     65 A

# 历史未被改写：入场基线仍在本分支的第一父链上
$ git log --oneline df2c595..HEAD | wc -l
19

# 可恢复性演练：从任务分支 tip 重建一个独立工作树，逐字节比对后删除
$ git worktree add --detach /tmp/claude-1000/m3-restore-drill HEAD
Preparing worktree (detached HEAD 7564896)
HEAD is now at 7564896 M3 EP-08: 冻结 ECC-M3-MODULE-AB-001（四臂、三留出场景、盲评协议）
$ git -C /tmp/claude-1000/m3-restore-drill rev-parse HEAD^{tree}
f91a61f804a838b2092af3e5f0ce58e90ba92f80
$ git rev-parse HEAD^{tree}
f91a61f804a838b2092af3e5f0ce58e90ba92f80
$ diff <(git -C /tmp/claude-1000/m3-restore-drill ls-files -s | sha256sum) <(git ls-files -s | sha256sum) && echo INDEX_IDENTICAL_OK
INDEX_IDENTICAL_OK
$ git worktree remove --force /tmp/claude-1000/m3-restore-drill && echo DRILL_WORKTREE_REMOVED
DRILL_WORKTREE_REMOVED
$ git rev-parse main   # 演练后复查，未被影响
a7b810109f43a4bf500acc285baab477d96796e3
```
