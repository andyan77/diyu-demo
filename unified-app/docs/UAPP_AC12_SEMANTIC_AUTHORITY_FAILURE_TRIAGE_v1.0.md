# AC-12 语义权威与自然交付 · Failure Triage v1.0

`task_id: DIYU-V1-UNIFIED-DIFY-APPLICATION-001`
`model_calls_at_triage: 0`

## 观察到的失败

Founder 的 YAML 与 GAP G2 实测都正确到达 Content Brief，却仍把已给的观看结果当作缺口；FULL T1 把用户要求的一条内容扩成两条，并把未确认的购买目标写成用户决定。

## 首次失效节点

1. `uapp_hop → uapp_fields`：旧 capability call 缺失用户的 `content_promise`，并把表达主体、表达边界误装为该字段。
2. `uapp_hop.professional_input → Seam`：M3 原文以未分级正文直接进入专业能力，能绕过已保存的 canonical source guard。
3. 六个能力共用的 `COMPONENT_RETURN_CODE`：所有本地缺口都套用相同机械三段话，尽管机器 Return 本身可解析。

## 归因

```yaml
observed_failure: user-confirmed semantics were changed or bypassed before professional consumption; local gap delivery was mechanically repeated
frozen_target: user authority is the sole decision input; machine return remains internal while user delivery is contextual and asks one real question
candidate_sources:
  - SYSTEM_UNDER_TEST
  - CHECKER_OR_FIXTURE
  - INPUT_ENVIRONMENT_OR_TOOL
confirmed_origin: SYSTEM_UNDER_TEST
mutation_target:
  - UAPP uapp_fields source-authority projection and uapp_seam professional_input binding
  - M4 shared COMPONENT_RETURN_CODE and its six generated successor workflows
protected_targets:
  - M1, M2 schema and non-test data, M3, Hop, Seam routing/provider, professional skills, PP b2, main
next_reverification: frozen YAML, G1/G2, FULL T1 once each on the versioned candidate
```

The route, target-capability reachability and provider routing are not failure sources: the Founder records show the target path executed.  Historical RAW remains untouched.
