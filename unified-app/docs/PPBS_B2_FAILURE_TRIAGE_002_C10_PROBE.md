# FAILURE TRIAGE 002 · Phase C C-10 负向控制探针不匹配

`task_id: DIYU-V1-PP-BOUNDARY-SUCCESSOR-001`｜`task_mode: REBASE`
判据真源：`unified-app/stages/PPBS_GATE_v2.0.json`
发生时点：**任何 b2 模型调用之前**。模型调用 0，Dify 写入 0，状态变化 0。

## observed_failure

Phase C 首次运行 13/14，`C-10`（负向控制）FAIL。
缺失探针一条：`` `false` 时，本节**照常全部适用**，一条都不减 ``。

## frozen_target

Gate v2.0 `C-10` 原文：

> 负向控制：strict_cta_closed=false 分支未被全局删除——false 分支表述在场，
> 且 CTA 三级表『低风险互动』行与 PP-5 原三条要求逐字保留

## candidate_sources

| 候选 | 判定 | 依据 |
|---|---|---|
| `CHECKER_OR_FIXTURE` | **成立** | 见下 |
| `SYSTEM_UNDER_TEST`（b2 少写了 false 分支） | 排除 | b2 第 612 行逐字存在该句 |
| `ORACLE_OR_CRITERION` | 排除 | C-10 判据文本本身没问题，它要求的东西确实在 |
| `CONTRACT_OR_INTENT` | 排除 | 行为合同未变 |
| `INPUT_ENVIRONMENT_OR_TOOL` | 排除 | 纯文本子串匹配，无外部依赖 |

## confirmed_origin

`CHECKER_OR_FIXTURE`。探针字符串写错了一个反引号的位置：

```
b2 实际文本    > `strict_cta_closed = false` 时，本节**照常全部适用**，一条都不减。
                                        ^ 反引号在 false 之后
我写的探针     `false` 时，本节**照常全部适用**，一条都不减
               ^ 反引号在 false 之前
```

同一批探针里 `SHARE_COND` 那条（`` `false` 时，本节照常适用 ``）匹配成功，
因为那处正文的反引号确实在 `false` 之前。两处正文写法不同，探针照抄了其中一种。

`hexdump` 证据：`grep -n "照常全部适用" … | cat -A` 第 612 行为
`` > `strict_cta_closed = false` M-fM-^WM-6M-oM-<M-^L…``（`时，`）。

## mutation_target

`unified-app/workflows/PPBS_B2_PHASE_C_CHECKS_v1.0.py` 的 `OPEN_NEG_CONTROL_NEW`
一条探针字符串。**只改探针，不改被测对象。**

## protected_targets（本轮未改，且无证据证明有错）

b2 SKILL.md、PP graph、Gate v2.0（含 C-10 判据文本）、Inputs、b1 全部历史件、
provider 钉、Seam、其余八个受保护应用。

## next_reverification（已执行）

按运行提示，修 Checker 后重跑了**完整 14 条**，覆盖：

- 正向控制 `C-09` → PASS
- 负向控制 `C-10`（原始失败案例）→ PASS
- 三条单点变异 `C-11 / C-12 / C-13` → PASS，且每条的另两个控制不受影响
- 原冻结验收 `C-01…C-08` 全部回归 → PASS

结果 **14/14**。证据：`unified-app/evidence/stages/pp_boundary_successor/PPBS_B2_PHASE_C_CHECKS.json`。

## 一处需要更正的自述

Gate v2.0 `document.supersedes.what_changed` 里写「Phase C 从 8 条扩到 13 条」。
实际条数是 **v1.1 九条 → v2.0 十四条**（`C-04` 拆成 A/B 后各算一条）。
这是我在 Gate 里写的**叙述性计数**写错了，不是判据内容错——判据条目本身逐条正确。
按「不原地改冻结件」，Gate 文件不动，更正记在这里与账本里；条数可由文件自身复算。
