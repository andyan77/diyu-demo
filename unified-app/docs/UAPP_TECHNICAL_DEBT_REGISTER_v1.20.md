# UAPP Technical Debt Register v1.20

`current_register: true`
`parent: UAPP_TECHNICAL_DEBT_REGISTER_v1.19.md`
`task_id: DIYU-V1-UNIFIED-DIFY-APPLICATION-001`

| 条目 | 当前状态 | 依据 |
|---|---|---|
| TD-UAPP-36 用户期望改变/表达字段的自然语言投影 | `OPEN / FAIL / CURRENT / P0` | FULL T1 已提供表达主体与边界，`uapp_fields` 未投影至 `expression.*`，下游重复询问。见 Formal Triage 001。 |
| TD-UAPP-37 未确认 primary goal 的来源守卫 | `OPEN / FAIL / CURRENT / P0` | G2 把主推商品、FULL T1 把期望改变以 `M1_SNAPSHOT/D` 写入 `objective.primary_goal`；这不是用户确认的经营目标。 |
| TD-UAPP-38 delivered artifact 的最终用户投影 | `OPEN / FAIL / CURRENT / P1` | YAML 的已交付专业成果绕过最终用户投影，暴露 `Content Brief Pack` 并合并两个待确认事项。 |
| professional_input 原文权威旁路 | `CLOSED_FOR_THIS_BATCH / CURRENT` | Seam 实际收到 `professional_input_safe`；未见原始专业文本覆盖业务合同。该结论不外推为所有未来路径均安全。 |
| FULL 测试写回链 | `PASS / CURRENT` | 本包未改变其写回节点、M2 或其测试记录。 |
| UAPP-AC-12 Founder 实测 | `RETURN / CURRENT` | Founder RETURN 与本批次失败均保留；本包不能代替 Founder 给出 ACCEPT。 |
| S5 技术验收 | `FAIL / CURRENT` | 四场景语义权威与自然交付硬门未通过，不能上调。 |

保护面未改：M1、M2 schema/非测试数据、M3、Hop、Seam 路由/provider、专业 Skill、PP b2、历史证据和 main。
