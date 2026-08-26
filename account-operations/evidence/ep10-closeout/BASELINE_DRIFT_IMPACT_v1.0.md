# 基线漂移影响面核算（A3）· `main` 在本任务施工期间前进

> `task_id` = `DIYU-V1-M3-ACCOUNT-CONTENT-OPERATOR-001`
> 观察时间 = 2026-08-26（本任务 EP-10 阶段）
> 触发事件 = 另一条工作线把 `DIYU-V1-M1-MODULE-LANDING-001` 合并并推送进 `main`

## 1. 事实（实测，非推断）

```console
$ git rev-parse main                    # 本任务入场时
df2c5952551f386a0e9a509404357f23c1d223c9

$ git rev-parse main                    # 本会话开始时
ca5281aee70943f02cf5b3be50c8c139ebfd15d4

$ git rev-parse main                    # EP-10 复查时
a7b810109f43a4bf500acc285baab477d96796e3

$ git ls-remote origin refs/heads/main
a7b810109f43a4bf500acc285baab477d96796e3

$ git merge-base --is-ancestor df2c595 main && echo YES
YES

$ git merge-base main task/m3-account-content-operator-v1
df2c5952551f386a0e9a509404357f23c1d223c9
```

`df2c595` 仍是 `main` 的祖先；`main` 沿另一条线快进到 `a7b8101`。M3 任务分支仍以 `df2c595` 为共同祖先，**未被改写、未被 rebase、未被 reset**。

## 2. 影响面：不多算，不少算

按 A3，只有**真实依赖已变绑定**的项失效。逐条核算：

| 绑定 | 是否被 `df2c595 → a7b8101` 改动 | 处置 |
|---|---|---|
| `SKILL.md` 与两份 `references/` | 否（全部是本任务分支新增文件） | 不失效 |
| `ECC-M3-RUNTIME-FIDELITY-001` 两轮直连 + 一轮 Dify 证据 | 否（绑定 Skill/模型/Dify 图，与 `main` 无关） | 不失效 |
| `ECC-M3-RUNTIME-BEHAVIOR-002` / `LONGITUDINAL-001` / `MODULE-AB-001` | 否（同上） | 不失效 |
| Dify 候选 App、图、发布版本 | 否 | 不失效 |
| `AC-12` / `AC-09` 的 **M2 接口版本**绑定 | **是** —— `business-persistence/app/api/knowledge.py`、`app/models/knowledge.py`、一支迁移与两份测试被改动 | **定向复验，见 §3** |
| 受保护目录零改动的自证 | 口径需更新 —— 见 §4 |

**没有**因为 `main` 动了就把全部证据置 `STALE`：那是"多算"，会让有证据且不受影响的项失效。

## 3. 定向复验结果：`AC-12` 的市场观察半从 `STALE` 转 `CURRENT`

`M3_CHECKPOINT_ROUND_2.md` §4.2 已经预判过这件事，原话是："M2 那两个文件合入 `main` 后，**只**需定向复验 AC-09 与 AC-12 的市场观察半。"

现在合入了。实测：

```console
$ # 容器内 /srv/app/** 与 git show main:business-persistence/** 逐文件比对
app/api/knowledge.py     : 容器 vs main(a7b8101) = IDENTICAL | 容器 vs df2c595 = DIFFERENT
app/models/knowledge.py  : 容器 vs main(a7b8101) = IDENTICAL | 容器 vs df2c595 = DIFFERENT

$ # 全量 business-persistence/app 与 migrations 逐文件比对（容器 vs 新 main）
（无 DIFF、无 MISSING 输出 —— 逐字节一致）

$ docker inspect -f '{{.State.StartedAt}}' diyu-m2-app
2026-08-26T11:44:24Z            # 容器启动

$ stat -c '%y' account-operations/fixtures/m2_live_capture_v1.json
2026-08-26 05:04:08 -0700       # 夹具抓取（= 12:04 UTC，晚于容器启动，同一实例）
```

三条结论：

1. 取证时运行的那份 M2 代码，与**当前 `main`** 逐字节一致；
2. 容器自启动后**未重建、未重启**，取证与本次比对是同一实例；
3. 因此 EP-04／EP-05 中被标为 `runtime_verified @ diyu-m2-app:dev(在途)`、对旧基线 `STALE` 的那一族证据，**现在对 `main@a7b8101` 是 `CURRENT`**。

这是**上行**，因此必须有事件支撑（A2）：事件就是"在途改动被合入 `main` 且内容未变"，由上面的逐字节比对证明，不是靠"应该没变"推断。

## 4. 一条必须更正的自证口径

前两轮 Checkpoint 用过这条自证：

```console
$ git diff --stat main -- content-production decision-chain business-persistence collab-ledger
（无输出）
```

`main` 前进后，这条命令**不再无输出**——但那是因为 `main` 上多了 M1／M2 的落地内容，**不是**因为 M3 动了这些目录。正确的自证口径改为**对共同祖先**比对：

```console
$ git diff --stat df2c595 -- content-production decision-chain business-persistence collab-ledger
```

见 `git_rollback_drill.md` 的复核记录。用旧口径继续声称"受保护目录零改动"会是一次**过时且会误导**的自证，故在此显式更正。

## 5. 本任务的处置

- **不 merge、不 rebase、不 cherry-pick `main` 进任务分支**：合同 `never_authorized_by_this_contract` 明确禁止 `merge or direct-push main ... or rewrite history`；把 `main` 并进来同样是改写本分支的历史基线，不在授权内；
- 交付物据此明确声明：**M3 候选构建在 `df2c595` 之上**，`main` 当前已前进到 `a7b8101`；是否把 M3 并入当前 `main`，是 Founder 的决定，不是执行侧可自行完成的动作；
- M1 落地引入的任何新接口、新能力，**本任务一律不消费、不适配**——那超出本合同的 WHAT。
