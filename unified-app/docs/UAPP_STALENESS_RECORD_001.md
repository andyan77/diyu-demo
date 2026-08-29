# 失效传播登记 001 · 图变更导致的 STALE 判定

`task_id: DIYU-V1-UNIFIED-DIFY-APPLICATION-001`

## 变化

| | 变更前 | 变更后 |
|---|---|---|
| graph sha256 | `e0cc8b28f9a9293bed81ab1ff448ab880bd938b5d37305931db97baa7b38585c` | `e8819f5b67552645ed4c18657a3fa7648b069a77b3250d36d21460580e421bbf` |
| 节点 / 边 | 59 / 69 | 61 / 71 |
| Manifest | `UAPP_CANDIDATE_RUN_MANIFEST_v1.0.yaml` | `UAPP_CANDIDATE_RUN_MANIFEST_v1.1.yaml` |

**变更内容**：新增 `uapp_noseam` 与 `uapp_seam_merge`（分支汇合）；`uapp_route` 增加
`action_text` 输入与 `action_source` 输出；`uapp_wb_prep` / `uapp_delivery` / `uapp_save`
改读汇合节点。见 commit `12f17b5` 与 `UAPP_FAILURE_TRIAGE_002`。

## 影响面计算（A3：不多算、不少算）

**直接依赖**（结论直接建立在被改节点的输出上）→ 置 `STALE`：

| 结论 | 依赖的被改节点 | 处置 |
|---|---|---|
| `UAPP-CAP-01..05` = PASS | `uapp_route`（路由判定）、`uapp_delivery`（modules / 泄漏计数） | **STALE**，需在新图上定向复验 |
| `UAPP-CAP-06` Attempt 1/2 | 同上 | **STALE** |
| `UAPP-FULL-01` Attempt 1 | 同上，且 T2/T4 正是被修的缺陷 | **STALE** |

**不受影响**（不依赖被改节点）→ 保持 `CURRENT`，不重跑：

| 结论 | 理由 |
|---|---|
| H2（M1 逐字节复用）| M1 子图五个节点一个字节没动；`m1_compiler` sha256 仍为 `326d0888…` |
| 保护面零漂移 | 旧 Canvas / 旧 provider / 最终 FP 九应用均未被本次变更触及 |
| 确定性预检 D-01..D-19 | 已在新图上重跑，19/19 PASS，本身即为新图的证据 |
| M3 方法参考载体同步 | 参考正文与嵌入方式未变 |

**判据未变**：`UAPP_FROZEN_SCENARIOS_v1.0.json`（`c45c4668…`）一个字节没动。
本次变的是**被测系统**，不是判据——所以不新建判据版本，也不允许借机改判据。

## 处置

在新图上重跑 `UAPP-CAP-01..06` 与 `UAPP-FULL-01`。**旧 Attempt 全部原样保留**，
不删除、不覆盖；新结果写新文件并记 `graph_sha256_at_run`。
其余用例（GAP / WITHDRAW / EQUIV / RECOVERY）尚未跑过，直接在新图上首跑。
