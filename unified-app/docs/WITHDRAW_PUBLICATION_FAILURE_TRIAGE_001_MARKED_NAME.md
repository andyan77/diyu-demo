# WITHDRAW Publication Failure Triage 001 — marked_name

- `observed_failure`: Dify draft 写入成功，但 publish API 返回 HTTP 400；`marked_name` 超过平台
  20 字符上限。
- `frozen_target`: 发布已通过零模型控制的同一 UAPP graph 与 conversation variables，不改变图。
- `candidate_sources`: `INPUT_ENVIRONMENT_OR_TOOL`。
- `confirmed_origin`: `INPUT_ENVIRONMENT_OR_TOOL` — API 明确返回
  `String should have at most 20 characters`。
- `evidence`: published graph 仍为 `aa32b6385de0024d270ec9f85bd78179`，active workflow `0`；
  正式输入和模型调用均为 0。
- `mutation_target`: 只把非产品版本标签从 `s5-material-registration-v1` 缩短为
  `s5-matreg-v1`。
- `protected_targets`: graph、conversation variables、Scenario、判据、UAPP/专业模块、数据库、main。
- `next_reverification`: 用同一草稿图再次 publish，随后逐字回读 graph 与 conversation variables。
