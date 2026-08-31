# UAPP Technical Debt Register v1.22

`current_register: true`
`parent: UAPP_TECHNICAL_DEBT_REGISTER_v1.21.md`
`task_id: DIYU-V1-UNIFIED-DIFY-APPLICATION-001`

| 条目 | 当前状态 | 依据 |
|---|---|---|
| TD-UAPP-36 自然语言表达字段投影 | `PARTIAL / NOT_VERIFIED / P0` | YAML 真实运行证明期望改变、内容承诺、表达主体和边界可按用户来源进入合同；FULL T1 在进入字段节点前因环境权限错误中断，不能上调为完整通过。 |
| TD-UAPP-37 primary goal 来源守卫 | `PARTIAL / CURRENT / P0` | YAML 实际删除未获用户支持的 primary goal。FULL 的独立环境故障不反证 YAML 结果，也不足以证明全场景完成。 |
| TD-UAPP-38 最终用户交付出口未统一 | `OPEN / FAIL / CURRENT / P0` | YAML 成功 artifact 仍将四项后续适配说成当前硬门；G1 的 ASK_ONE 路径绕过 `uapp_delivery` 并保留固定开场。两者均指向 UAPP 最终交付接缝。 |
| professional_input 原文权威旁路 | `CLOSED_FOR_THIS_BATCH / CURRENT` | 本包未修改既有 `professional_input_safe` 守卫；YAML 未见旁路写入。 |
| FULL T1 `uapp_inline_artifact` 权限异常 | `OPEN / NOT_VERIFIED(INPUT_ENVIRONMENT_OR_TOOL) / P0` | 受保护、未改节点报 `operation not permitted`，在 fields/seam/delivery 前终止；未发生合法自动重放，人工重试为零。 |
| UAPP-AC-12 Founder 实测 | `RETURN / CURRENT` | Founder RETURN 与所有历史及本包 RAW 均保留；未取得复测资格。 |
| S5 技术验收 | `FAIL / CURRENT` | 本包的四场景后继未全部获得 PASS / CURRENT，且不授权上调 S5。 |

保护面：M1、M2 schema/非测试数据、M3、Hop、Seam 路由/provider、专业 Skill、PP b2、历史证据与 main 未改。当前新环境非测试保护基线为 `0/0`；历史 `1568/117` 仅为已保留历史证据，不能写成当前计数。
