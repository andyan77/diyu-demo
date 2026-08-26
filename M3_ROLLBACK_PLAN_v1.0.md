# M3 回滚计划 v1.0

> `task_id` = `DIYU-V1-M3-ACCOUNT-CONTENT-OPERATOR-001`
> 取证时间（UTC）：2026-08-26
> 覆盖 Prompt §13 EP-05 末项「回滚导出与恢复路径预检」

本文件回答一个问题：**如果现在要把这个任务完全撤销，需要做什么、会留下什么。**
下面每一条都附实测命令与literal 输出，不是设想。

---

## 1. 结论先行

| 项 | 结论 |
|---|---|
| 撤销 Git 侧改动 | **一条命令**（删分支 + 删 worktree），`main` 不受任何影响 |
| `main` 是否需要恢复 | **不需要**——从未被触碰，HEAD 仍是入场时的 `df2c595` |
| 受保护模块是否需要恢复 | **不需要**——零改动，实测 diff 为空 |
| 不可自动撤销的残留 | **一项**：运行中 M2 实例里的一份取证 workspace（见 §4） |
| Dify 对象 | **未创建任何对象**，无需回滚 |
| 远端 | **从未推送**，无需回滚 |

---

## 2. Git 侧：全部改动都是新增

```console
$ git diff --name-status main | awk '{print $1}' | sort | uniq -c
     31 A
```

**31 个文件，全部 `A`（新增）；0 修改、0 删除、0 重命名。** 这不是"大部分是新增"，
是一个都没有改到既有文件——所以回滚不需要恢复任何内容，只需要丢弃新增。

`main` 未被改写：

```console
$ git rev-parse main
df2c5952551f386a0e9a509404357f23c1d223c9

$ git merge-base --is-ancestor main task/m3-account-content-operator-v1 && echo OK
OK
```

第二条证明 `main` 是任务分支的**祖先**——即分支只在 `main` 之上追加，没有
rebase、amend、reset 或任何形式的历史改写。`df2c595` 与入场 Manifest 记录的基线一致。

受保护模块零改动：

```console
$ git diff --stat main -- content-production decision-chain business-persistence collab-ledger
（无输出）
```

**无输出 = 四个受保护目录一个字节都没变。** 其中
`decision-chain/skills/Content_Brief_Architect_v0.1.md` 被 EP-05 的下游消费测试
按 SHA-256 `a0268a21…` 只读绑定，测试会在它变化时失败。

---

## 3. 回滚操作（Git 侧）

```bash
# 1. 离开工作树后删除它（--force 仅因工作树内有未跟踪的 __pycache__）
git worktree remove --force /home/faye/diyu-demo-worktrees/m3-account-content-operator-v1

# 2. 删除任务分支
git branch -D task/m3-account-content-operator-v1
```

执行后 `main` 的 HEAD 与文件树**不变**——因为分支上的 3 个 commit 从未进入 `main`，
`main` 也从未被 merge 或 rebase。

> **本轮未实际执行删除**（那会毁掉尚未交付的工作）。上面两条的安全性由 §2 的三条
> 实测证据推出：全部改动是新增、分支是 `main` 的严格后继、`main` HEAD 仍是 `df2c595`。
> 这是**推断**，不是已观察——`git worktree remove` 本身没有在本轮被运行过。

### 只回滚部分内容

由于产物集中在一个新目录，粒度回滚也很简单：

| 想撤销 | 做法 |
|---|---|
| 全部工程产物 | `rm -rf account-operations/` |
| 只撤 EP-05 | `git revert f6d953c` |
| 只撤 EP-04 实跑证据 | `git revert 0f2240f` |
| 只撤某个 schema 收紧 | 单文件 `git checkout <commit>^ -- <path>` |

---

## 4. 不可由 Git 撤销的残留：M2 实例中的取证数据

EP-04 通过 M2 **自己的公开 API** 建了一份取证 workspace（与
`business-persistence/dify/bootstrap_demo_workspace.py` 同一种用法）。这是真实写入，
Git 回滚不会撤销它。

| 项 | 值 |
|---|---|
| 实例 | 容器 `diyu-m2-app`（`diyu-m2-app:dev`），无宿主端口映射 |
| workspace_id | `4a419aa1-2b55-4ee6-a4ea-d3650139de00`（名为「M3 契约取证 workspace」） |
| 建立者 | user `external_ref = m3-acco-001-founder` |
| 数据量 | 2 用户、1 workspace、2 账号、2 周期、1 Campaign overlay、3 市场观察、1 task/artifact/version/publish、2 反馈、1 周期决策 |
| 幂等键前缀 | 全部为 `m3-acco-001:` |

**为什么可以不清理**：全部数据在一个独立 workspace 内，与其他 workspace 隔离；
M2 的成员校验（实测 403「actor is not a member of this workspace」）保证其他
actor 读不到它；全部幂等键带 `m3-acco-001:` 前缀，可被精确识别。

**若确实要清理**：M2 当前**没有**删除 workspace 的端点（实测端点清单里无
`DELETE /workspaces/*`），因此只能由 M2 侧决定如何清理。这属于 M2 的新任务，
不在本合同授权范围内。

**未触碰的**：M2 的源码、迁移、其他任何 workspace 的数据。本轮对 M2 只有
"经其公开 API 新建独立数据 + 读取" 两类动作。

---

## 5. Dify

**本轮未创建、未修改、未删除任何 Dify 对象。** 因此无回滚输入需要保存，也没有
需要恢复的对象清单。原因见 Checkpoint：Console 不可用，而 Prompt §12.3 要求的
候选 App 创建需要 Console。

对照记录（只读 SELECT，未写入）：当前实例共 27 个 app，本轮前后一致。

---

## 6. 远端

```console
$ git branch -vv --list task/m3-account-content-operator-v1
* task/m3-account-content-operator-v1 f6d953c DIYU-V1-M3-...
```

**无上游追踪分支 = 从未推送。** 另外实测远端当前不可达
（`fatal: unable to access 'https://github.com/andyan77/diyu-demo.git/'`），
故 Prompt §12.4 要求的"从远端重新读取完整 commit hash 证明"本轮
`NOT_VERIFIED (ABSENT)`，留待 EP-10。

---

## 7. 恢复演练的状态

| 项 | 状态 |
|---|---|
| 回滚路径已写明并逐条附实测证据 | `static_verified` |
| `main` 不受影响 | `static_verified`（HEAD 比对 + 祖先关系 + 空 diff 三条独立证据） |
| **实际执行一次删除并恢复** | **`NOT_VERIFIED`** —— 本轮未执行，执行即毁掉未交付工作 |

Prompt §13 EP-10 要求的是"导出恢复演练"。本轮只做到**预检**（EP-05 的职责），
真正的演练属于 EP-10，需要在工作已交付或已推送远端之后进行，否则演练本身就是
不可逆的。**不把预检写成演练。**

---

```text
END_MARKER = DIYU-V1-M3-ACCOUNT-CONTENT-OPERATOR-001-ROLLBACK-PLAN-v1.0-END
```
