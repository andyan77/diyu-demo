# AC-12 Canonical Fields 与最终交付 · Successor Failure Triage

`task_id: DIYU-V1-UNIFIED-DIFY-APPLICATION-001`
`package: UAPP-AC12-CANONICAL-FIELDS-AND-FINAL-DELIVERY-SUCCESSOR-001`
`model_calls_before_mutation: 0`

## observed_failure

上一批四场景的 G2 和 FULL T1 把非用户确认信息写进 `objective.primary_goal`；FULL T1 漏掉用户自然句中的表达主体/边界，重复追问。YAML 的已交付内容直接显示内部标题，并把两个后续适配项写成当前确认事项。

## frozen_target

用户来源的期望改变、内容承诺、表达主体和边界只能写入各自语义域；未被用户明确确认的经营目标必须物理缺席。成功 artifact 必须通过 UAPP 的最终用户投影，保留成果实质、移除内部名，并把非阻塞建议明确为后续可选调整。

## confirmed_origin

`SYSTEM_UNDER_TEST`：

1. `uapp_fields` 先以 M1 快照写入 primary goal，再在后续分支标记拒绝，导致拒绝并未删除 canonical state 污染值；自然语言表达主体/边界也只覆盖了标签式输入。
2. `uapp_delivery` 对成功 artifact 直接保留专业组件 `user_delivery`，没有清理标题式内部名称，也没有区分当前阻塞与后续适配建议。

## ruled_out_or_protected

- M1、M3、Hop、Seam 的路由/能力选择/Provider、Content Brief 专业 Prompt 和其他五项专业能力：只有正确路由和组件可达证据，没有独立错误证据；不修改。
- `professional_input_safe`：上一批真实调用已证明其生效；本后继不改变它。
- M2 schema、非测试数据、main、冻结输入、历史 RAW/Gate/结果：受保护。

## mutation_target

只改 UAPP `uapp_fields` 和 `uapp_delivery` 的同源构建代码；不新增节点、模型、状态载体或数据库。

## next_reverification

使用 YAML、G2、FULL T1 的原始 RAW 做完整离线重放与单变量负控制；控制通过后冻结候选图与 Gate，再各运行 YAML、G1、G2、FULL T1 一次。
