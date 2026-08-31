# UAPP Technical Debt Register v1.18

current_register: `true`
parent: `UAPP_TECHNICAL_DEBT_REGISTER_v1.17.md`
task_id: `DIYU-V1-UNIFIED-DIFY-APPLICATION-001`

| 条目 | 当前状态 | 依据 |
|---|---|---|
| TD-UAPP-36 用户期望改变未投影为 Content Brief 内容承诺 | `OPEN / FAIL / CURRENT / P0` | Founder YAML 与 G2 两个真实 run 均正确路由并真实调用 Content Brief，但 Hop 缺少 `content_promise`，导致重复追问 |
| TD-UAPP-37 未授权商业主目标升级与错误来源回指 | `OPEN / FAIL / CURRENT / P0` | FULL T1 M3 将用户内容结果改为“促进购买决策”；Hop/UAPP state 错标为用户来源 |
| FULL 测试写回链 | `PASS / CURRENT` | T2/T3/T4 的 M2 发布、反馈、周期记录和关联已只读核验；无真实发布 |
| UAPP-AC-12 Founder 实测 | `RETURN / CURRENT` | Founder 已实测，最先阻断真实使用的问题为语义承接与目标权威越界 |
| S5 技术验收 | `FAIL / CURRENT` | AC-12 RETURN 与两个 P0 语义问题存在，不能收口 |

保护面保持：M1、M2 schema、M3、Hop、Seam、专业能力、Provider 和 main 未被本次审计修改。
