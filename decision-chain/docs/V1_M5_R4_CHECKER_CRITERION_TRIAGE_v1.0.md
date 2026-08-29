# `RISK-M4-030+031` · checker／criterion mismatch 归因与既有运行重裁定 v1.0

- `task_id`: `DIYU-V1-M5-UNIFIED-INTEGRATION-FINAL-ACCEPTANCE-001`
- 授权：Founder 2026-08-29 裁决书「下一步只执行已经要求的 R4 checker/criterion mismatch
  归因与既有四次运行重裁定」
- 边界（逐条遵守）：**不修改 M4；不修改冻结判据；不重新调用模型；不追加采样；
  不启动新的正式轮；不合并 main。**
- 证据：`decision-chain/evidence/m5-final-p0/R4_CHECKER_CRITERION_TRIAGE.json`
- 脚本：`decision-chain/workflows/DIYU_M5_R4_CHECKER_CRITERION_TRIAGE_v1.0.py`
  （只读既有证据文件；`model_calls: 0`，`new_sampling: 0`，`modifications_to_sut: 0`）

---

## FAILURE TRIAGE

### `observed_failure`

R4 本轮记 `FAIL`，判词：

> 同一语义只因值里多一个引号就换了结论：`DELIVERED` vs `DELIVERED_AFTER_RECOVERY`
> （M4 外壳解析器假阴性）

### `frozen_target`

判据原文（`RISK-M4-030+031` 的 `oracle` 字段，逐字）：

> **质量判定使用任务适用的语义标准；等价表达不被误判为失败**

### `candidate_sources`

`SYSTEM_UNDER_TEST`（M4 外壳解析器真有假阴性）／`CHECKER_OR_FIXTURE`（检查器比判据严）／
`ORACLE_OR_CRITERION`（判据本身不可判）／`INSUFFICIENT_EVIDENCE`。

### `confirmed_origin` = `CHECKER_OR_FIXTURE`

有独立证据确认，理由三条：

**其一，「失败」的定义在系统里已经有真源，检查器没有用它。**
运行时自己定义什么叫交付：

```python
def delivered(result):
    """业务是否真的交付。只认 business_delivery_outcome，不认平台 status。"""
    return result.get("business_delivery_outcome") in ("DELIVERED", "DELIVERED_AFTER_RECOVERY")
```

`DELIVERED_AFTER_RECOVERY` **是已交付**。判据说的是"不被误判为**失败**"，
检查器测的却是**枚举字符串逐格相等**。两者不是一回事：字符串不等 ≠ 被判为失败。

**其二，本轮四形式没有任何一格未交付。**

| 写法 | 结论 | 运行时判定 | 产物字数 | 用户交付字数 |
|---|---|---|---|---|
| `json` | `DELIVERED` | 已交付 | 4494 | 685 |
| `yaml_plain` | `DELIVERED` | 已交付 | 3781 | 665 |
| `markdown_backtick` | `DELIVERED` | 已交付 | 3150 | 945 |
| `yaml_with_quote` | `DELIVERED_AFTER_RECOVERY` | **已交付** | 4695 | 1098 |

引号变体不但交付了，产物与用户交付都是四格里最长的，`missing` 为空。
判据要挡的"等价表达被误判为失败"在本轮**没有发生**。

**其三，检查器判词里那句根因断言，已被证据推翻。**
判词写死了"（M4 外壳解析器假阴性）"。假阴性意味着语义充分却被判为不在场／未交付。
本轮四格全部交付，不存在假阴性。该断言在写下时是对的（见下节两个时期），
现在是过期结论被硬编码在判词里。

### `evidence`

五次既有运行，按两个权威各判一遍（脚本机械重算，零模型调用）：

| 证据文件 | 入库时间 | 原记录 | 按判据原文 | 按检查器实现 |
|---|---|---|---|---|
| `RISK_PROBE_SUITE_riska.json` | 08-28 01:26 | `FAIL` | **`FAIL`** | `FAIL` |
| `RISK_PROBE_SUITE_riskF.json` | 08-28 03:34 | `FAIL` | **`FAIL`** | `FAIL` |
| `RISK_PROBE_SUITE_riskFRB2.json` | 08-28 07:42 | `FAIL` | **`PASS`** | `FAIL` |
| `RISK_PROBE_SUITE_riskFRB3.json` | 08-28 09:14 | `FAIL` | **`PASS`** | `FAIL` |
| `RISK_PROBE_SUITE_riskfp1.json` | 08-28 23:37 | `FAIL` | **`PASS`** | `FAIL` |

**两个时期，分界线是一次真实修复，不是判据漂移。**

- **第一期（`riska`、`riskF`）**：引号变体 `UNKNOWN`、产物 **0 字**；
  `riskF` 里 `markdown_backtick` 更是 `NOT_DELIVERED`、产物 **21 字**。
  这是**货真价实的假阴性**——语义充分的等价表达被判成没交付。
  两个权威都判 `FAIL`，检查器当时的判词也是对的。
- **第二期（`riskFRB2`、`riskFRB3`、`riskfp1`）**：三次运行共 12 格，
  **没有一格未交付**，产物最短 3150 字。判据原文要挡的现象消失了。

分界线可核对：M4 解析 successor 由 commit `4d03367`（08-28 06:00）建立，
落在 `riskF`（03:34）之后、`riskFRB2`（07:42）之前。
**第一期的真实缺陷在该 successor 之后不再复现。**

第二期三次的检查器 `FAIL` 各挂在哪一条，也不固定：

| 运行 | 触发的检查器条款 | 偏离的那一格 |
|---|---|---|
| `riskFRB2` | 三形式不一致 | `json` |
| `riskFRB3` | 三形式不一致 | `json` |
| `riskfp1` | 引号变体与 `yaml_plain` 不等 | `yaml_with_quote` |

**偏离格在轮间移动，且每次只有一格。** 这是恢复分支的随机触发，
不是"写法在判事"——若是写法在判事，同一写法应当稳定地落在同一侧。

### `mutation_target`

**本轮为空。** Founder 明确不授权修改 M4、判据、检查器，也不授权重新调用模型。
本件只产出归因与重裁定，不动任何被测对象或判据文件。

### `protected_targets`（未证明有错，不得修改）

M4 外壳解析器与其八个已发布应用；`SEALED_ORACLES_*` 三份判据；
`DIYU_M5_RISK_PROBE_SUITE_v1.0.py` 的 `oracle` 与 `judge_*` 实现；
`rb` / `legacy` 绑定的全部应用；五份既有 `RISK_PROBE_SUITE_*.json` 原始证据。

### `next_reverification`

本轮不执行（无模型调用授权）。待 Founder 决定后，按原冻结目标做定向复验的最小集合应为：

1. 对引号变体做正／负控制——正控制：语义充分 + 引号 → 必须已交付；
   负控制：语义**不足** + 引号 → 必须不交付。现有五次运行只有正控制侧，**负控制缺失**，
   所以"解析器是否还会因引号漏判"这一点严格来说仍是 `NOT_VERIFIED`，
   不能因为三次都交付了就说它已修好。
2. 同一输入重复采样，用来分离"恢复分支随机触发"与"写法决定结论"。

---

## 一、重裁定结果

Founder 要求的是「既有四次运行重裁定」。执行侧登记时把**全部五次**既有运行一并重裁，
以免只挑其中四次造成选择性取样；本轮候选（`riskfp1`）的四种形式逐格结果见上表。

| 层 | 结论 |
|---|---|
| 按**冻结判据原文**重裁 `riskfp1` | **`PASS`** —— 四种等价表达无一被判为失败，无长度阈值可疑项 |
| 按**检查器实现**重裁 `riskfp1` | `FAIL` —— 枚举字符串逐格不等（原记录，保留） |
| 归因 | `CHECKER_OR_FIXTURE`：检查器比它所实现的判据严，且其判词硬编码了一条已过期的根因断言 |
| 第一期两次（`riska`／`riskF`） | 两个权威一致 `FAIL`，**真实缺陷**，不翻案 |
| 第二期三次（`FRB2`／`FRB3`／`fp1`） | 判据原文 `PASS`，检查器 `FAIL`，差异全部来自同一处 mismatch |

## 二、执行侧不做的判定（交 Founder）

判据原文与检查器实现冲突时以谁为准，属**验收判据域**，执行侧无权自裁。
因此本件**不**把 `RISK-M4-030+031` 的记录状态从 `FAIL` 改写为 `PASS`，
`RISK_PROBE_SUITE_riskfp1.json` 里的 `"verdict": "FAIL"` 原样保留，
`M5-AC-07` 维持 `FAIL` 不变。

需要 Founder 裁决的是一件事：

> `RISK-M4-030+031` 的权威判据，是 `oracle` 字段的那句话，还是 `judge_m4_030_031` 的实现？

- 若以 `oracle` 原文为准 → `riskfp1` 重裁为 `PASS`，检查器登记为待修（下一版判据），
  且仍需补第 `next_reverification` 条的负控制才能说解析器已修好；
- 若以检查器实现为准 → 维持 `FAIL`，则需说明"枚举串不等"本身为何构成产品缺陷，
  因为按运行时定义两者都是已交付。

在该裁决作出之前，本件只是归因与重算，不产生任何状态上行。

```yaml
task_progress: IN_PROGRESS
terminal_state:            # 留空
main_merge: NOT_ALLOWED
model_calls_this_step: 0
new_sampling_this_step: 0
sut_modifications_this_step: 0
criteria_modifications_this_step: 0
```
