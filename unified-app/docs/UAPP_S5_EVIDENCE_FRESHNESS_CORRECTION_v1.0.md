# UAPP S5 Evidence Freshness Correction v1.0

`task_id: DIYU-V1-UNIFIED-DIFY-APPLICATION-001`

`correction_kind: APPEND_ONLY_SUCCESSOR_ADJUDICATION`

## 观察

修复 2 将 UAPP 图从 `02610a77c3ce86f46f7a80de6d47ac2e` 变更为
`16e10d84dcdf1deb4608d95fe30fb654`，改变 `uapp_td24_correction` 的“空状态、空
correction_deltas”分支。CAP-01～04 原始节点证据逐项显示：

| 场景 | prev_state_json | correction_deltas | 旧图实际输出 |
|---|---|---|---|
| CAP-01 | 空 | `[]` | `REJECTED / TASK_IDENTITY_MISMATCH` |
| CAP-02 | 空 | `[]` | `REJECTED / TASK_IDENTITY_MISMATCH` |
| CAP-03 | 空 | `[]` | `REJECTED / TASK_IDENTITY_MISMATCH` |
| CAP-04 | 空 | `[]` | `REJECTED / TASK_IDENTITY_MISMATCH` |

因此该变化分支对四个旧 PASS 均真实可达。即使四次运行最终仍产出专业能力 artifact，旧图
行为也不能证明当前图会得到相同状态和交付；按依赖失效规则，四项必须标记 `STALE`。

## 后继裁决

- UAPP-CAP-01～04：保留历史 `PASS`，freshness 从 `CURRENT` 改为 `STALE`。
- 不删除、不覆盖原 RAW、Check、run_id 或旧 Result。
- 当前图有效的 CAP-05 失败证据保持 `FAIL / CURRENT`。
- UAPP-AC-01/02 仍可由当前图 CAP-05 的统一入口、自然语言、inputs={}、保护面真实记录判为
  `PASS / CURRENT`；UAPP-AC-04/05/10 继续 `FAIL / CURRENT`。
- 当前图正式场景 PASS 数为 `0/19`；历史 PASS 但 STALE 为 `4`。
- 本 Active Work Package 的修复和额外运行额度均已耗尽，不得为刷新 CAP-01～04 继续运行。

`supersedes_projection_only: UAPP_S5_BOUNDED_CONVERGENCE_RESULT_v1.0 CAP-01..04 freshness`

`model_calls: 0`
