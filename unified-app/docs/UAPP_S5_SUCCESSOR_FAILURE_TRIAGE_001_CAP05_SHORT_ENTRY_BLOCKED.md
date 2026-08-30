# UAPP S5 SUCCESSOR FAILURE TRIAGE 001 · CAP-05 short entry blocked

`task_id: DIYU-V1-UNIFIED-DIFY-APPLICATION-001`

`successor_attempt: UAPP-S5-F2-SUCCESSOR-001`

`gate_sha256: d27254ff95ba47d4cd056c3697d658e463956382faa5cdbec0d07b187e3b358a`

## FAILURE TRIAGE

```yaml
observed_failure: >-
  后继 CAP-05 的冻结自然语言正确路由到 PRODUCTION_DIRECTOR，其他五个专业能力零暗跑；
  但统一应用在 Seam 与目标能力调用前，因当前新会话没有合法 script_or_equivalent_beats
  而将 upstream binding 标为 REJECTED。Seam 和 PRODUCTION_DIRECTOR 均运行 0 次，
  冻结 Checker CAP-02 FAIL。
frozen_target: >-
  UAPP-AC-04 要求六个专业能力都能从同一统一入口分别到达，每个能力至少一次最小可执行 smoke；
  UAPP-AC-05 要求每个能力场景只运行适用能力，无固定全链和暗跑。
  CAP-05 原句、Gate、Runner、Checker 和候选图均早于本轮结果冻结。
candidate_sources:
  - CONTRACT_OR_INTENT
  - ORACLE_OR_CRITERION
  - CHECKER_OR_FIXTURE
  - INPUT_ENVIRONMENT_OR_TOOL
  - SYSTEM_UNDER_TEST
  - INSUFFICIENT_EVIDENCE
confirmed_origin: SYSTEM_UNDER_TEST
evidence:
  workflow_run_id: d68493e9-f832-4b67-8bd5-36cd4541c273
  raw_sha256: 886eb9bc0d361b715dd5461b48fa9a3ef1cb859b06f2e4f4bbd474ed3ec0a91a
  checker_sha256: 9b52ad4332f31b823de31d830fc257f986acd5d03756cbdab2b48caac05c0d1a
  http_status: 200
  route_target: PRODUCTION_DIRECTOR
  seam_runs: 0
  production_director_runs: 0
  other_five_capability_runs: 0
  correction_deltas: 0
  upstream_slot: script_or_equivalent_beats
  upstream_lineage: REJECTED
  upstream_reason: SELECTOR_NOT_SELECTED
  frozen_checker_failure: CAP-02
mutation_target: NONE
protected_targets:
  - UAPP current published graph
  - M1 / M2 / M3
  - Hop / Seam / PP provider
  - six professional capabilities
  - frozen 19 inputs / Gate / Runner / Checker / controls
  - previous invalid Attempt and all historical evidence
  - M2 schema / non-test data / main
next_reverification: >-
  当前授权不允许修复或第三个正式槽位。最小后继方向是单独版本化审查：
  在不放宽过期或错误上游产物的前提下，让独立的 Production Director 短入口
  能进入专业能力并由其返回精确缺口，而不是在调用前被已接受上游绑定规则一律拦截。
model_calls_before_failure:
  successor_top_level_runs: 5
  successor_deepseek_llm_attempts: 25
  lifetime_top_level_runs: 6
  lifetime_deepseek_llm_attempts: 32
side_effects: >-
  后继五个场景各通过正常路径创建 1 个 is_test 工作区、周期和任务；
  artifact、content_version、publish_instance、feedback_record 均为 0。
  真实发布、非测试数据变化、schema 变化、图漂移和 main 变化均为 0。
```

## 归因排除

- 不是传输故障：HTTP 200，5 个 LLM 节点全部成功，0 重试，0 平台内部重放。
- 不是路由误判：`target_capability=PRODUCTION_DIRECTOR`。
- 不是暗跑：其他五个专业能力均为 0 次。
- 不是 Checker 新增标准：Checker 仅按冻结 AC-04/AC-05 检查 Seam 和目标 app 是否真实运行一次。
- 不是候选或保护面漂移：CAP-05 运行后图指纹、provider、M2 schema 和非测试计数与 Gate 一致。

## 停止结论

CAP-06 与其余 14 个冻结场景均未运行。不修改被测实现，不重跑，不建立第三个正式槽位，不进入 Founder AC-12 或 main merge。
