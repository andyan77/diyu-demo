# Founder 裁决 003 · 接受技术债并收口 M5（追加件）

- `task_id`: `DIYU-V1-M5-UNIFIED-INTEGRATION-FINAL-ACCEPTANCE-001`
- `founder_adjudication_id`: `M5-FOUNDER-ADJUDICATION-003`
- `observed_date`: 2026-08-29
- `entry_mode`: `REBASE_TASK`（同一 `task_id`，不新建、不重置失败历史）
- 本件性质：**追加**。裁决 001／002、R2／R3 判定书、R7 重算、A/B 重建记录与
  全部原始 `verdict` 一字不改、不覆盖、不删除。

## 一、Founder 原话（逐字）

> 我认为两项P0收口后，暂时忽略剩余问题项，作为技术债登记，推进M5后续收口

## 二、编译含义（取自 v1.2 合同 `authorization.compiled_meaning`，未改写）

1. 在两项 P0 已关闭、`RISK-M4-030+031` 正负控制均成立的当前候选上，
   停止继续修复、补人判、补盲评和开启新正式轮；
2. 剩余已知 `FAIL` 之外的非 P0 未决项、`STALE` 项、未完成盲评、索引与检查器缺陷
   如实登记为技术债，不删除、不涂绿、不追溯改写原证据；
3. Founder 接受当前候选作为**带已披露技术债**的 V1 技术集成交付基线，
   并授权完成 M5 账本、证据、任务分支、`main`、`origin/main` 与最终回执收口。

## 三、不表示什么（`does_not_mean`，逐条登记）

- **不**表示原 `M5-AC-00..10` 已全部 `PASS/CURRENT`；
- **不**表示技术债已修复或不存在；
- **不**表示真实平台发布、生产就绪、真实运营闭环或经营提升已经验证；
- **不**允许把 `NOT_VERIFIED`、`STALE` 或历史 `FAIL` 改写为 `PASS`。

## 四、本裁决改变的是什么

**改变的是这些项对 v1.2 收口公式的阻断资格，不是它们自己的技术结果或证据时效。**

```yaml
founder_product_acceptance: PASS/CURRENT
acceptance_type: ACCEPTED_WITH_DISCLOSED_TECHNICAL_DEBT
applicable_p0_failures: 0
remaining_non_p0_items: DEFERRED_ACCEPTED_TECHNICAL_DEBT
new_formal_round: NOT_AUTHORIZED
additional_model_calls: NOT_AUTHORIZED
candidate_runtime_change: NOT_AUTHORIZED
main_closeout: AUTHORIZED_AFTER_CLOSE_AC_01_TO_06
```

旧的 M5 原始全绿公式**不再**作为本 v1.2 收口的阻断公式；
父合同 `M5_ENGINEERING_TASK_CONTRACT_v1.1_AC07_REBASE`（sha256 `a13b5651…2ce7dc`）
与其下的原 AC 状态**不被覆盖**，继续作为历史记录有效。

M5 `DONE` 只表示本 v1.2「可用候选 ＋ 已披露技术债 ＋ Git／远端收口」合同完成。

## 五、禁止的外推（`prohibited_claims`）

`ALL_ORIGINAL_M5_AC_PASS`、`PRODUCTION_READY`、`REAL_OPERATION_LOOP_VERIFIED`、
`OPERATIONAL_UPLIFT_PROVEN` —— 四条一律不得声称。

## 六、回指

| 依据 | 文件 | sha256 |
|---|---|---|
| 裁决 001（`H01-A3` = `PASS`） | `V1_M5_FINAL_P0_FOUNDER_ADJUDICATION_001.md` | `373e492d…17380f` |
| 裁决 002 + 负控制判定 | `V1_M5_FINAL_P0_FOUNDER_ADJUDICATION_002_AND_NEGATIVE_CONTROL_VERDICT_v1.0.md` | `c0b3ef2b…76aedd6` |
| R2 定向复验 | `V1_M5_FINAL_P0_R2_DIRECTED_REVERIFICATION_v1.0.md` | `5fdeebfe…c299a93` |
| R3 留出判定 | `V1_M5_FINAL_P0_R3_HOLDOUT_VERDICT_v1.0.md` | `3e93d308…ded06aa7` |
| R7 十九维与 AC 重算 | `V1_M5_FINAL_P0_R7_INDEX_RECOMPUTE_v1.0.md` | `97dc76d0…86cd70` |
| A/B 重建与旧包标失效 | `V1_M5_FINAL_P0_AB_REBUILD_AND_STALE_MARKING_v1.0.md` | `17508873…157d3` |
| 本轮收口合同 | `M5_ENGINEERING_TASK_CONTRACT_v1.2_FOUNDER_TECHNICAL_DEBT_CLOSEOUT.yaml`（规则侧） | `35ccf590…de9df0e` |
| 本轮收口 Prompt | `M5_FOUNDER_ACCEPTED_TECHNICAL_DEBT_FINAL_CLOSEOUT_EXECUTION_PROMPT_v1.0.md`（规则侧） | `e384df3d…49397cc` |

技术债主表见 `V1_M5_ACCEPTED_TECHNICAL_DEBT_REGISTER_v1.0.md`（全仓唯一一份）。
