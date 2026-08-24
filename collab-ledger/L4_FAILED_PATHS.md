# L4 · 已排除路线

> 规则正文见 [COLLAB_CONTINUITY_PROTOCOL.md](COLLAB_CONTINUITY_PROTOCOL.md)。追加式：只加不改，更正另起一条。
>
> **这里只登记有明确失败或排除证据的路线。** 关键前提不变时，**不得重试**。
> **起算基线 `main @ 6ae78abf5967535bda81392255b8ee3e79e4bcb5`。** 基线之前的历史**不补造**失败路线。

## 一、不属于本账本的东西（先划清）

| 不是失败路线 | 为什么 |
|---|---|
| [生产差距登记](../decision-chain/docs/V1_PRODUCTION_GAP_REGISTER_v0.1.md) G-01～G-12 | **开放 Gap ≠ 已排除路线。** 12 项全部未关闭，但没有一项拿到「这条路走死了」的证据。此文件**只读引用**，**不得整批升级**进本账本 |
| 任何「暂时没做」「等授权」「优先级不够」 | 没做过，就没有失败证据 |
| 模型自称「试过不行」 | 自述不是证据。**没有可复核的干预与观测，就不写进来** |

## 二、已排除路线（自起算基线起）

> **按 `task_id` 分区。** 下表是索引；条目正文见各条。并行任务多起来时，各任务的失败路线写进 `collab-ledger/tasks/<task_id>.md`，本文件只留索引行。

| 条目 | 所属 task_id | 一句话 |
|---|---|---|
| FP-001 | `COLLAB-LEDGER-BOOTSTRAP-001` | canonical 规则不能放 `.claude/rules/`——该目录被 gitignore，永远进不了远程基线 |
| FP-002 | `COLLAB-LEDGER-BOOTSTRAP-001` | 不能用关键词 grep 自动提取历史证据的自报状态——会把「引用别人的状态」当成「自己的状态」|

### FP-001 · 把 canonical 规则放进 `.claude/rules/` 路径域

**所属 `task_id`：`COLLAB-LEDGER-BOOTSTRAP-001`**

| 项 | 内容 |
|---|---|
| 根因假设 | 官方 Claude Code 的 `.claude/rules/*.md` 支持按路径域**按需加载**，比全量常驻的 `CLAUDE.md` 更省 context，看起来是放协作规则的更好位置 |
| 干预 | 侦察目标目录是否可进入仓库 |
| 观测 | 仓库 [.gitignore](../.gitignore) **第 2 行就是 `.claude/`**。`git ls-files` 对 `.claude` 路径返回 **0 条**，即整个 `.claude/` 从未被追踪 |
| 结论 | **排除。** 放进去的规则**永远不会进入远程默认工作基线**，新克隆的会话读不到它，直接违背本任务 P0 |
| 关键前提 | 仓库 `.gitignore` 仍然忽略 `.claude/` |
| 对象版本／环境 | `main @ 6ae78ab`；`.gitignore` 于该提交的内容 |
| 证据 | [.gitignore](../.gitignore) · `git ls-files .claude` 输出为空 |
| 重试条件 | **只有** `.gitignore` 不再忽略 `.claude/` 时才可重新评估 |

### FP-002 · 用关键词 grep 从历史证据里自动提取「自报状态」

**所属 `task_id`：`COLLAB-LEDGER-BOOTSTRAP-001`**

| 项 | 内容 |
|---|---|
| 根因假设 | 57 份历史证据里散落着 `DONE` / `PARTIAL` / `BLOCKED` 等状态词，正则扫首个命中即可批量生成目录的状态列 |
| 干预 | 对全部 57 份跑 `grep -oam1 -E "(DONE\|PARTIAL\|BLOCKED\|FAILED\|PASS\|ACCEPTED…)"`，取首个命中当状态 |
| 观测 | 结果**实测错误**：`CONTENT_PRODUCTION_PRE_CHAIN_FIXTURE_RUN_002.md` 被判为 `BLOCKED`，而该文件**自己**的状态字段逐字写的是 `\| 状态 \| **DONE** \|` —— 首个命中的 `BLOCKED` 来自正文中对 RUN_001 的**引用**。同类错判在 `V1_E2E_RUN_002_RAW.md` 等文件上重复出现 |
| 结论 | **排除。** 关键词扫描无法区分「本文件的状态」与「本文件提到的别人的状态」，会系统性生成**假状态**。改为：只取文件**首 40 行内显式的状态字段行**，逐字摘录；取不到就标 `NOT_VERIFIED_BEFORE_BASELINE`（57 份里只有 9 份取得到） |
| 关键前提 | 历史证据文件**不统一**使用结构化状态字段（实测 48/57 根本没有状态字段） |
| 对象版本／环境 | `main @ 6ae78ab` 时的 57 份证据 |
| 证据 | [L3 §二 历史证据目录](L3_ATTEMPTS_AND_EVIDENCE.md) 的最终取值方式与逐字摘录 |
| 重试条件 | **只有**历史证据被统一改造成结构化状态字段之后 —— 而改动既有 evidence 是**受保护资产**，当前禁止 |

---

## 三、其他任务

`NONE_VERIFIED_SINCE_BASELINE` —— 自 `6ae78ab` 起，除上述两条外没有其他被证据判死的路线。
