# UAPP S5 v1.5 Failure Triage 001 — CAP-05 Empty-State Correction

`task_id: DIYU-V1-UNIFIED-DIFY-APPLICATION-001`

`attempt_run_id: 45c783b7-b7fc-47fa-80c0-639ce843ee55`

`frozen_gate: UAPP_S5_GATE_v1.5`

## FAILURE TRIAGE

```yaml
observed_failure: >
  CAP-05 的自然语言包含完整口播稿和制作条件，路由也唯一命中
  PRODUCTION_DIRECTOR；但新会话的规范状态为空，且本轮 correction_deltas=[] 时，
  uapp_td24_correction 返回 REJECTED / TASK_IDENTITY_MISMATCH。该结果优先阻断了
  uapp_pick_upstream 和 uapp_fields，Seam 与 PRODUCTION_DIRECTOR 均未运行，产物为空。
frozen_target: >
  CAP-05 必须在合法脚本和制作条件在场时真实运行 PRODUCTION_DIRECTOR，生成可回指的
  非空产物；其他五项专业能力零暗跑，保护面和非测试数据不变。
candidate_sources:
  - CONTRACT_OR_INTENT
  - ORACLE_OR_CRITERION
  - CHECKER_OR_FIXTURE
  - INPUT_ENVIRONMENT_OR_TOOL
  - SYSTEM_UNDER_TEST
  - INSUFFICIENT_EVIDENCE
confirmed_origin: SYSTEM_UNDER_TEST
evidence:
  - run_id=45c783b7-b7fc-47fa-80c0-639ce843ee55; HTTP 200; transport=direct
  - uapp_route.target_capability=PRODUCTION_DIRECTOR
  - uapp_td24_correction.inputs.prev_state_json=""
  - uapp_td24_correction.inputs.action_patch.correction_deltas=[]
  - uapp_td24_correction.outputs.correction_status=REJECTED
  - uapp_td24_correction.outputs.correction_note=TASK_IDENTITY_MISMATCH
  - uapp_pick_upstream.selection_status=CORRECTION_REJECTED
  - Seam=0; PRODUCTION_DIRECTOR=0; other professional capabilities=0
  - Checker CAP-02=FAIL and CAP-04=FAIL; all transport/protection checks PASS
mutation_target: >
  UAPP 自身 uapp_td24_correction 的“无既有状态且没有 correction_delta”分支：
  此时必须返回 NO_CORRECTION，而不是把新任务初始化误判为纠正身份冲突。
protected_targets:
  - M1 / M2 / M3
  - Hop / Seam
  - six professional capability applications and PP/provider
  - M2 schema and non-test data
  - frozen Scenario v1.1, Gate v1.5, business Checker and prior evidence
  - main / origin/main
next_reverification: >
  先用零模型正负控制证明空状态+空 delta=NO_CORRECTION、空状态+实质 delta 仍 fail-closed、
  既有状态的合法纠正与 task mismatch 语义不变；发布后只使用唯一额外运行额度定向复验 CAP-05。
model_calls_before_failure: 5 in this Attempt; 39 cumulative in this Active Work Package
side_effects: >
  创建了当前测试作用域的 workspace/cycle/task 各 1 行；没有 artifact、content_version、
  publish_instance 或 feedback；非测试计数和 M2 schema 不变；无真实发布。
```

## 独立归因依据

输入中明确存在 `script_or_equivalent_beats`，Hop 也逐字提取了该字段；因此不是输入缺失。
路由正确且平台无错误，因此不是传输或路由问题。冻结 Checker 只读取真实节点执行和产物，
没有新增标准。阻断发生在 UAPP 自有纠正接缝，并且 `correction_deltas=[]` 与
`TASK_IDENTITY_MISMATCH` 同时出现，足以把最高失效节点限定在该确定性分支。

## 影响面

- 直接影响：独立新会话中没有纠正语义的 CAP-05、CAP-06 等合法短入口。
- 不受影响：已有规范状态上的真实纠正传播、已接受上游 artifact 绑定、CAP-01～04、
  M1/M2/M3/Hop/Seam/专业能力和历史证据。
- 复验集：确定性正负控制、发布后图与保护面核验、CAP-05 一次定向正式复验。

`sut_repair_node_usage_after_confirmation: 2 / 2`

`extra_formal_run_slot_after_failure: 1 / 1 reserved for CAP-05 directed reverification`
