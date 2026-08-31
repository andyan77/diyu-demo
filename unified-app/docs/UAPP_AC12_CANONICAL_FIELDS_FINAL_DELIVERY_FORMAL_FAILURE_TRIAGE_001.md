# Canonical Fields 与最终交付 · Formal Failure Triage 001

`task_id: DIYU-V1-UNIFIED-DIFY-APPLICATION-001`
`gate_sha256: 4761da15c199a05492e2b3e548c842c6439fc2a8abf5d561f491976f9835c089`

## observed_failure

YAML 已证明字段修复生效：用户的期望改变、内容承诺、表达主体和边界进入正确域，`objective.primary_goal` 不存在，内部英文标题也被移除。但最终成果仍把四项后续适配写为“发布前需要确认”，违反“当前内容已足够进入脚本、阻塞问题数为零”。

G1 只问了一个正确的路线问题，却仍由 `uapp_answer_ask` 直接回复旧的固定三段式缺口话术，绕开已修改的 `uapp_delivery`。因此最终用户交付出口并不统一。

FULL T1 在未被本包修改的 `uapp_inline_artifact` 节点收到 `operation not permitted` 后失败，未到达本包验证的 fields/seam/delivery 链路。

## frozen_target

同一最终用户交付出口必须覆盖成功 artifact、缺口和跟进路径；成功内容的非阻塞适配不得冒充当前必答项。四场景只各运行一次，不得在结果后修改候选或重试。

## candidate_sources

- `SYSTEM_UNDER_TEST`: UAPP 成功 artifact 交付的非阻塞/阻塞分类，以及 `ASK_ONE` 的最终回复选择。
- `INPUT_ENVIRONMENT_OR_TOOL`: FULL T1 的 `uapp_inline_artifact` “operation not permitted”。
- `CHECKER_OR_FIXTURE`: 离线真实 RAW 重放与正负控制均通过，未见其为 YAML/G1 的最高失效节点。

## confirmed_origin

1. `SYSTEM_UNDER_TEST`：UAPP 仍有两个未被本候选覆盖的最终交付出口行为：成功 artifact 未把所有非阻塞项降为可选，`ASK_ONE` 绕过 `uapp_delivery`。
2. `INPUT_ENVIRONMENT_OR_TOOL`：FULL T1 失败点是受保护、未改的 `uapp_inline_artifact`，错误是平台/执行权限型 `operation not permitted`；没有合法自动重放，不能推定为本包 SUT 回归。

## mutation_target

`NONE`。本授权只允许一个正式实现批次。YAML/G1 的新发现和 FULL 的环境异常均已保留，不在本包二次修改或重跑。

## protected_targets

M1、M2 schema 与非测试数据、M3、Hop、Seam 路由/能力选择/Provider、六项专业 Skill、Content Brief 专业 Prompt、PP b2、冻结输入、历史 RAW 和 main 未改。

## next_reverification

停在 CHECKPOINT。若获得新的版本化授权，优先修复 UAPP `ASK_ONE` 与 artifact 成功路径的共同最终用户出口；FULL 的 `uapp_inline_artifact` 错误应先作独立环境/权限诊断，不能由本包下游补丁掩盖。
