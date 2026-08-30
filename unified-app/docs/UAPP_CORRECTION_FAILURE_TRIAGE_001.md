# FAILURE TRIAGE · 跨轮纠正没有进入规范制作字段

`task_id: DIYU-V1-UNIFIED-DIFY-APPLICATION-001`
`gate: UAPP_CORRECTION_GATE_v1.0.json / 9220a7bd587ec030fa340892609addab15cb70432199924285e1b1fa634a95d7`

## observed_failure

用户逐字要求把制作规模从一人改成两人，并要求继续使用旧制作方案做标题和封面。真实运行后：

- `production.profile` 仍是旧的一人值，字段版本仍为 2；
- 两份依赖该字段的制作方案仍是 `stale=false`；
- 旧 PD 9304 字正文以相同 sha256 `8f91984b…c21b` 被绑定进 PP；
- 系统新增一份 7370 字 PP artifact，并向用户交付了标题和封面。

第一处冻结硬门失败是 `C-01`。按停止规则，未进入 S4 或 S5。

## frozen_target

`C-01` 要求 `production.profile` 准确改成两人对应的用户确认值、来源回指本轮、字段版本精确 +1，并保持 `production.time_window` 等其余字段不变。随后 `C-02…C-06` 要求依赖 PD 失效、旧正文不下传、不生成新包装、自然回复先要求更新制作方案。

## candidate_sources

- `CONTRACT_OR_INTENT`：已排除。输入原文和 correction field 在 Gate 中早于运行冻结。
- `ORACLE_OR_CRITERION`：已排除。C-01 直接比对真实会话变量，不依赖自然语言主观解释。
- `CHECKER_OR_FIXTURE`：已排除。现场读取 `workflow_conversation_variables`、节点 inputs/outputs 和 artifact store；无合成夹具参与正式判定。
- `INPUT_ENVIRONMENT_OR_TOOL`：已排除。HTTP 200，六个 LLM 节点均成功，M3 真实输出明确识别“制作规模从一人改为两人”。
- `SYSTEM_UNDER_TEST`：确认成立。
- `INSUFFICIENT_EVIDENCE`：不成立；最高失效路径可由相邻真实节点独立定位。

## confirmed_origin

`SYSTEM_UNDER_TEST`。

最高已确认失效路径是统一应用内部的“用户纠正 → 规范字段 → artifact 失效”接续：

1. M3 已识别“两人”并写进运营判断，证明输入没有丢失；
2. `uapp_hop` 的 PP 能力外壳没有输出 `production_profile`，却继续携带旧 PD 正文；
3. `uapp_fields` 因此只把 `facts.registered` 记为纠正，没有更新 `production.profile`；
4. 后置血缘门看到 PD 仍非 STALE，于是输出 `artifact_binding_status=BOUND`；
5. PP 收到旧 PD 并生成新包装。

这是被测系统真实接续行为，不是模型正文自述。

## evidence

- 顶层 run：`592ba2d3-c6a4-41a7-a8e9-f33818be98c4`；HTTP 200；591.97s。
- M3：`dca3cc1f-d1e0-409a-8967-4da81e866d00`，输出含“制作规模从一人改为两人”。
- Hop：`396cee36-13a2-4d02-a965-e5775223b353`，`capability_call` 不含 `production_profile`。
- `uapp_fields`：`corrected_fields=facts.registered`；`stale_artifacts=PUBLISHING_PACKAGING@t12`；`artifact_binding_status=BOUND`。
- 绑定正文：9304 字，sha256 `8f91984b628da1c65250c7bb2f90e9a31c86233826ceee9271bcc46b77b2c21b`，与运行前 PD 完全相同。
- PP：`213101ba-cb9e-4585-b9f6-befdf3c8f9e0`；新 artifact fp `a7bf609e2dc9eecb`，7370 字，sha256 `ca5ca64e…43c9f`。
- RAW：`unified-app/evidence/stages/uapp_correction/UAPP_CORRECTION_RAW_v1.0.json`，sha256 `cc2b0c9a…2642dc`。
- 结果：`unified-app/stages/UAPP_CORRECTION_RESULT_v1.0.json`。

## mutation_target

`NONE`。当前 Prompt 不授权第三轮边测边修；没有修改 UAPP、Hop、M3、Seam、PP 或任何专业能力。

## protected_targets

M1/M2/M3、Hop、Seam、六个专业能力、PP/provider、M2 Schema、非测试数据、冻结 Gate/输入/控制、历史 RAW、main 均不得修改。运行前后应用与 provider 绑定逐项相等；M2 计数和 Schema 指纹逐项相等。

## next_reverification

唯一后继候选是由 Founder 版本化授权最小 successor repair：只处理统一应用“纠正字段提取/接线到规范字段及后置失效门”的最高失效路径；建立新 Gate 后，用同一自然语言场景做一次定向复验。当前执行不实施该修复，也不重跑。

## model_calls_before_failure

顶层 1；LLM 节点 6；失败节点 0；人工重试 0；平台内部重放 0；重复采样 0；A/B 0；Reviewer 0。

## side_effects

仅测试会话发生正常路径写入：state rev 12→13，`facts.registered` 被改写，旧 PP@t12 被置 STALE，新 PP@t13 被追加。M2 行 0→0；publish_instance 0→0；无真实发布、撤回、删除或权限变化。该失败状态保留为证据，不直接改库修复。

```yaml
CROSS_TURN_CORRECTION_PROPAGATION: FAIL / CURRENT
S4_OVERALL_ACCEPTANCE: NOT_VERIFIED
S5: NOT_STARTED
UAPP-AC-12: NOT_VERIFIED
main_merge: NOT_ALLOWED
task_progress: IN_PROGRESS
terminal_state: unset
next_state: CHECKPOINT
```
