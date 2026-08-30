# UAPP S5 v1.6 Failure Triage 002 — CAP-05 Inline Artifact Binding

`task_id: DIYU-V1-UNIFIED-DIFY-APPLICATION-001`

`attempt_run_id: cbabab77-bbb3-4f07-a655-83d61bbd9b62`

`frozen_gate: UAPP_S5_GATE_v1.6`

## FAILURE TRIAGE

```yaml
observed_failure: >
  修复后的纠正节点正确返回 NONE / NEW_TASK_NO_CORRECTION，但 CAP-05 仍未进入 Seam 和
  PRODUCTION_DIRECTOR。uapp_pick_upstream 将用户本轮点名的目标能力误作上游产物能力，
  返回 NAMED_UPSTREAM_INCOMPATIBLE；uapp_fields 又只允许历史 accepted ledger 的 selector
  正文进入 script_or_equivalent_beats，没有接纳用户本轮直接提供的完整脚本。最终产物为空，
  且用户回复泄露 PRODUCTION_DIRECTOR 内部标识。
frozen_target: >
  用户在自然语言中直接提供完整、确认可用的脚本和制作条件时，统一入口必须真实运行
  PRODUCTION_DIRECTOR 并生成可回指产物；其他五能力零暗跑，用户回复不得泄露内部标识。
candidate_sources:
  - CONTRACT_OR_INTENT
  - ORACLE_OR_CRITERION
  - CHECKER_OR_FIXTURE
  - INPUT_ENVIRONMENT_OR_TOOL
  - SYSTEM_UNDER_TEST
  - INSUFFICIENT_EVIDENCE
confirmed_origin: SYSTEM_UNDER_TEST
evidence:
  - run_id=cbabab77-bbb3-4f07-a655-83d61bbd9b62; HTTP 200; transport=direct
  - uapp_td24_correction=NONE / NEW_TASK_NO_CORRECTION, proving repair 2 worked
  - uapp_pick_upstream=NAMED_UPSTREAM_INCOMPATIBLE
  - selector note treated PRODUCTION_DIRECTOR as the named upstream for PRODUCTION_DIRECTOR
  - Hop extracted the supplied script as content_body_or_beats, while script_or_equivalent_beats was empty
  - uapp_fields.artifact_binding_status=REJECTED and upstream lineage=SELECTOR_NOT_SELECTED
  - Seam=0; PRODUCTION_DIRECTOR=0; other professional capabilities=0
  - user answer contains literal PRODUCTION_DIRECTOR; Checker T-05=FAIL
  - Checker CAP-02=FAIL and CAP-04=FAIL; transport/protection/budget checks PASS
mutation_target: NONE
protected_targets:
  - frozen Scenario v1.1, Gate v1.6 and Checker v1.2
  - M1 / M2 / M3, Hop, Seam, six professional applications and PP/provider
  - M2 schema and non-test data
  - CAP-01..04 PASS evidence and both CAP-05 failed Attempts
  - main / origin/main
next_reverification: >
  本 Active Work Package 不再复验。若 Founder 建立新的 REBASE，最高修复节点应限定为
  UAPP 对“用户本轮直接提供完整 artifact”的来源识别、能力兼容和调用前绑定，同时保留
  历史 accepted artifact、STALE、task、fp/bfp 的 fail-closed 边界和自然回复脱敏。
model_calls_before_failure: 5 in this Attempt; 44 cumulative in this Active Work Package
side_effects: >
  当前测试作用域创建 workspace/cycle/task 各 1 行；没有 artifact、content_version、
  publish_instance 或 feedback；非测试计数和 M2 schema 不变；无真实发布。
```

## 收敛裁决

- distinct SUT repair nodes：`2 / 2`，额度耗尽。
- post-result Oracle/Checker rebase：`1 / 1`，额度耗尽且本次没有 Checker 失效证据。
- extra formal run slot：`1 / 1`，已由本次定向复验使用。
- transient replay：`0`；本次不是暂态失败，不具备重放资格。
- 当前累计：顶层运行 `8 / 22`，LLM 节点尝试 `44 / 130`。

本次停止原因不是总调用预算耗尽，而是有界修复路径已达到授权上限且 S5 硬门仍失败。
继续需要第三个 SUT 修复节点，超出本 Active Work Package；不得继续修改或试跑。

## 保留的 CURRENT 结果

- S4：`PASS / CURRENT`
- UAPP-CAP-01～04：`PASS / CURRENT`
- TD-UAPP-24 跨轮纠正传播：匹配状态分支未变且控制通过，继续 `PASS / CURRENT`
- 保护面、M2 schema、非测试数据、main：无漂移

`next_state: FOUNDER_CHECKPOINT_AFTER_BOUNDED_CONVERGENCE_LIMIT`
