# GAP-01 Successor Failure Triage 001 · G2 repeated gap

- `task_id`: `DIYU-V1-UNIFIED-DIFY-APPLICATION-001`
- `attempt`: `217fee1f-b6f1-4c1d-b189-f6c510564e31`
- `mutation_status`: `NONE_AT_TRIAGE_TIME`

## FAILURE TRIAGE

- `observed_failure`: G2 在同一 conversation 中被正确路由到 `CONTENT_BRIEF`，Seam 与该唯一专业能力
  均真实执行，但最终再次询问 `content_promise`。冻结 G2 原文已经说出“希望她看完知道缺的是一件
  能压住整套的外套”，因此该问题重复索要用户已经给出的决定相关信息。
- `frozen_target`: 接受冻结 G2 对商品与内容方向的补充；不重复 G1 或已回答缺口；进入合法后续业务链；
  Seam 执行；零暗跑、零编造、零未授权副作用。冻结合同没有要求 G2 必须立即生成 artifact。
- `candidate_sources`: `ORACLE_OR_CRITERION`, `SYSTEM_UNDER_TEST`。
- `confirmed_origin`:
  1. `ORACLE_OR_CRITERION`：Checker v1.0 的 `GAP-S6` 额外要求非空 artifact，超出冻结 G2 产品判据；
  2. `SYSTEM_UNDER_TEST`：UAPP `uapp_fields` 只把用户支持的 `expected_change` 登记为
     `audience.expected_change`，没有把同一用户原句的可复算等价表达投影到缺失的
     `content.promise`，使 Content Brief 外壳重复追问该语义。
- `evidence`:
  - RAW sha256 `8bba63723ddb0949e1d077b963fbbf93c0a1a04982bce3997c0c2d7bc7494d62`；
  - Check sha256 `f733b1f60ff90fd1b42044d1f48b46e177cbc88450704e111fb009451578670f`；
  - `uapp_fields.capability_call` 已含逐字回指用户的 `expected_change`，但
    `gaps_text = content_promise；expression_subject_and_boundary`；
  - Content Brief 唯一运行返回 `missing = content_promise, expression_subject_and_boundary`；
  - 六能力运行数：仅 `CONTENT_BRIEF=1`，其余为 0；非测试计数与 schema 未变化。
- `mutation_target`: 版本化修正 GAP Checker 的 G2 判据；在 UAPP `uapp_fields` 增加通用、
  用户原文支持的 expected-change → content-promise 等价投影，仅补当前真实缺口，不代填表达主体。
- `protected_targets`: M1/M2/M3、Hop、Seam、Content Brief 及其他专业能力、PP、数据库 schema、
  冻结 G1/G2 原文、历史 RAW/Check/Gate、main。
- `next_reverification`: 零模型正负控制后冻结 successor Gate；在全新测试身份下按原文各运行
  G1、G2 一次。G2 可产出 artifact，或精确询问尚未提供的表达主体；不得再询问 content promise。
- `model_calls_before_failure`: 顶层 `2`，DeepSeek 节点 `7`。
- `side_effects`: 测试作用域 bootstrap 写入；真实发布 `0`，非测试数据变化 `0`，schema 变化 `0`，
  重试/内部重放 `0`。

