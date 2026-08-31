# UAPP S5 Final Tool Failure Triage 001 — Check Writer

- `observed_failure`: W0 RAW 已完整落盘，但 v1.0 Executor 的 verify 分支调用基础 Runner
  未导出的 `exclusive_write`，随后 Checker 的旧模块全局路径把相同 RAW 判为 hash mismatch。
- `frozen_target`: 用 Gate v2.0 冻结的 Checker 对 W0 RAW 判定，不重跑输入、不改变业务判据。
- `candidate_sources`: `INPUT_ENVIRONMENT_OR_TOOL`、`CHECKER_OR_FIXTURE`。
- `confirmed_origin`: `INPUT_ENVIRONMENT_OR_TOOL`。RAW 中 Gate/Scenario 哈希与现场逐字一致；
  直接调用同一冻结 `evaluate_turn` 得到全部谓词 PASS，证明错误只在入口模块路径与写函数接线。
- `evidence`: run `b3e44f33-b383-43a8-bd30-bacc271376be`；Gate sha256
  `306b4f29ad403e62582991a66095afd1f73e79a6e5ef69b9da7e179fd0aae515`；原始
  NOT_VERIFIED check 保留，不覆盖。
- `mutation_target`: 版本化 Executor/Gate 后继，只改模块路径、一次写入路径和父 RAW 继承绑定。
- `protected_targets`: W0 RAW、Scenario、业务 Checker 谓词、UAPP/PP/Seam/Hop/专业应用、M2、main。
- `next_reverification`: 对父 W0 RAW 用相同 Checker 谓词生成 successor check；随后 W1 零模型预检。
