# AC-12 语义权威与自然交付 · 正式批次 Failure Triage 001

`task_id: DIYU-V1-UNIFIED-DIFY-APPLICATION-001`
`package: UAPP-AC12-SEMANTIC-AUTHORITY-AND-HUMAN-DELIVERY-REBASE-001`
`gate: UAPP_AC12_SEMANTIC_AUTHORITY_GATE_v1.2.json`
`gate_sha256: d497d7afde69dfacf695139d366371be81ff4c1f1def8f666189b64ac52291fa`

## observed_failure

四个冻结场景均已各运行一次。G1 符合单一决定性问题要求；其余三个结果说明候选没有达到冻结验收：

- YAML 的内容成果忠实保留了用户语义，但用户可见标题暴露了内部能力名，并把两个不相互依赖的待确认事项放在同一轮。
- G2 的对话承接正确，但 canonical state 把“主推商品”写成 `objective.primary_goal`，其来源是 `M1_SNAPSHOT/D`，不是用户确认的经营主目标。
- FULL T1 中用户已明确给出表达主体和边界，`uapp_fields` 却没有将其纳入 canonical contract；下游因此重复询问该信息。该场景也将用户期望改变错误写成 `objective.primary_goal`。

## frozen_target

用户已经明确表达的目标、期望改变、内容承诺、数量、事实和权限必须以其原始来源进入唯一业务合同；专业建议和原始 `professional_input` 不得越级。用户交付必须承接已知信息、只问一个真正缺口，且不出现内部能力名或状态词。

## candidate_sources

- `SYSTEM_UNDER_TEST`: UAPP 的用户原文识别/投影和最终交付投影；
- `CHECKER_OR_FIXTURE`: 已由运行前单变量控制排除为本次主因；
- `M1/M3/Hop/Seam/Content Brief`: 没有独立证据证明其路由、能力可达或 Provider 调度有错；
- `INPUT_ENVIRONMENT_OR_TOOL`: 四个工作流和其链上子运行均成功，未见重放、传输错误或未完成状态。

## confirmed_origin

`SYSTEM_UNDER_TEST`，且有两个同一授权包内、相互独立的最早失效接缝：

1. `uapp_fields` 的自然语言用户来源投影与来源守卫不完整：仅能稳定处理某些显式标签式表达；FULL T1 的自然表达主体/边界没有进入 `expression.*`，且 `M1_SNAPSHOT` 的 primary goal 仍被写入 state，即使输出字段声称已拒绝。
2. UAPP 在已交付 artifact 路径直接使用能力返回的 `user_delivery`，没有经过最终用户投影，因此 YAML 显示 `Content Brief Pack` 和未压缩的两个后续确认事项。

`professional_input_safe` 已实际传给 Seam；没有证据显示 raw `professional_input` 越过该守卫。因此该旁路在本批次并非首个失效节点。

## evidence

| 场景 | 顶层 run | 直接事实 |
|---|---|---|
| YAML | `aea42816-4296-4230-8f9b-fcbfc469d429` | `user_projection_used=false`；交付开头为 `Content Brief Pack`，并要求两个确认事项。 |
| G1 | `89ad3031-4fc8-42ba-8f91-ee487eec72ba` | 一个可由 G2 回答的分叉问题，未运行专业能力。 |
| G2 | `0ca83c8f-e0ed-4f60-9538-7eef51cb5a12` | `objective.primary_goal=主推秋冬新款廓形西装外套`，`kind=M1_SNAPSHOT`，`lvl=D`。 |
| FULL T1 | `fa13182d-f9e5-43f1-9f5b-abe8657df1d0` | 原话含“品牌搭配师真实出镜…不做剧情…不承诺改变身材”；`direct_authority_fields` 却只有 expected change/content promise，最终仍问表达主体/边界。 |

完整原始记录位于 `unified-app/evidence/stages/uapp_ac12_semantic_authority_v1_0/`；其 SHA-256 由 `UAPP_AC12_SEMANTIC_AUTHORITY_FORMAL_RESULT_v1.0.json` 索引。所有四场景的目标路由均为 Content Brief 或本地提问，其他五项专业能力为零运行。

## mutation_target

`NONE`。本执行包只允许一个正式实现批次；四次正式运行已消耗完毕。不能在看到结果后修改候选、Gate、输入、Checker 或进行第二批调用。

## protected_targets

M1、M2 schema 与非测试数据、M3、Hop、Seam 的路由/能力选择/Provider、六项专业 Skill、PP b2、CTA 边界、冻结输入、历史 RAW、main 和真实发布平台保持受保护。

## next_reverification

本包在 `CHECKPOINT` 停止。任何后继必须新建版本化合同，先分别验证自然语言 `expression.*` 投影、primary-goal 来源拒绝、以及 delivered-artifact 的最终用户投影；不得修改已通过的意图、路由或组件可达性结论。

## accounting

顶层运行 `4/4`；DeepSeek 节点尝试 `18/32`；人工重试 `0`；平台透明重放 `0`；重复采样、A/B 和 Reviewer 均为 `0`。
