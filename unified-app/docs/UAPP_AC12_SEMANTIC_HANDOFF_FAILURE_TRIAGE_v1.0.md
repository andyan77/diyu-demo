# UAPP AC-12 语义承接与来源锁定 · FAILURE TRIAGE v1.0

`task_id: DIYU-V1-UNIFIED-DIFY-APPLICATION-001`  
`method: 只读 Founder AC-12 原始节点载荷 + 当前 uapp_fields 源码离线重放`  
`new_model_calls: 0`

## observed_failure

用户已经明确说明观众看完应获得的结果，Content Brief 仍重复询问内容承诺；完整故事又把未由用户提出的“促进购买决策”写成用户决定。

## confirmed_origin

`SYSTEM_UNDER_TEST / UAPP uapp_fields`，分为两个同层但独立的最小缺陷：

1. YAML 原始运行 `9da91e61-adf2-46a2-b6a0-2493bc492963` 中，Hop 已输出 `expected_change`，但 `uapp_fields` 只在该值自身出现“看完/读完/听完”词时才投影 `content_promise`。YAML 标签“希望她看完明白”的语义在用户原话中，而不在被抽取值中，因此投影被错误拒绝。
2. GAP G2 原始运行 `03871811-eb66-45e6-a496-e6764e203463` 中，Hop 同时遗漏 `expected_change` 与 `content_promise`；但 `uapp_fields` 的真实输入已经包括本轮用户原话和 M1 snapshot。它没有对直接用户来源的观众结果执行规范投影，是首次可由本授权 UAPP 节点闭合的确定性缺失。Hop 外部应用保持受保护。
3. FULL T1 原始运行 `0c603685-8a4e-4b50-bf97-92c71049cb79` 中，M1 的 `primary_goal` 是用户观众结果；M3/Hop 另给出“促进购买决策”。`uapp_fields` 以产品词重叠为依据把后者升级成 `USER_UTTERANCE` 并回指 `TURN1.user_request`，属于来源等级和回指错误。首次受授权可修点是该升级守卫，不修改 M3。

## frozen_target

- 用户直接表达的观众结果可原样进入 `expected_change` 与 `content_promise`；没有此类表达时精确停下。
- 系统商业推断不得成为用户确认的 `primary_goal`，除非 M1 保存相同值且可回指用户原话。
- 意图、路由、Hop、Seam、Content Brief、Provider、M1/M2/M3、M2 schema 和历史 run 均不修改。

## candidate_sources

| 来源 | 裁决 | 依据 |
| --- | --- | --- |
| CONTRACT_OR_INTENT | 排除 | Prompt 已允许“用户观众结果”作为两个字段的等价，且禁止把系统建议冒充用户决定。 |
| ORACLE_OR_CRITERION | 排除 | 原始用户话语与组件精确缺口对应；正负控制可区分。 |
| CHECKER_OR_FIXTURE | 排除 | 直接执行真实 fields 输入可复现缺失与错误等级。 |
| INPUT_ENVIRONMENT_OR_TOOL | 排除为根因 | 三条历史 run 的相关节点成功，且错误由纯 Python 代码确定性重放。 |
| SYSTEM_UNDER_TEST | 确认 | `uapp_fields` 的等价投影与来源升级分支。 |

## mutation_target

仅 `uapp_fields`：通用观众结果投影、`primary_goal` 来源锁定、对应输出声明。候选构建器和控制脚本只服务该节点。

## protected_targets

`uapp_route`、`uapp_m3`、`uapp_hop`、`uapp_seam`、M1/M2/M3、六项专业能力、Provider、M2 schema、非测试数据、历史 RAW、main。

## next_reverification

先运行冻结的 16 项零模型正负控制；其后仅按原话运行 YAML、G1→G2（同一新会话）与 FULL T1。首次正式失败只在本授权范围且独立证据确认 SUT 时使用唯一后继迭代。
