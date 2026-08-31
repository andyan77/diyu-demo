# UAPP Technical Debt Register v1.16

current_register: `true`
parent: `UAPP_TECHNICAL_DEBT_REGISTER_v1.15.md`
task_id: `DIYU-V1-UNIFIED-DIFY-APPLICATION-001`

本版取代 v1.15，成为唯一当前技术债主表。v1.15 及更早版本原文保留；本版只记录全新环境
基线对现有条目的后继影响，不追溯改写历史 FAIL 或 PASS。

| 条目 | 当前状态 | 本版依据 |
|---|---|---|
| TD-UAPP-30 EQUIV Fixture 前置条件 | `CLOSED_IMPLEMENTATION / NOT_VERIFIED` | 冻结 Scenario v1.2 保持不变；新 UAPP 的通用格式归一控制证明 plain/YAML-like/JSON-like 等价，真实缺项仍 fail-closed；尚无新环境正式运行证据 |
| TD-UAPP-31 上传资料未登记为 M2 可撤回素材 | `STALE_NEW_ENVIRONMENT_IDENTITY` | 历史 W0/W1 PASS 保留；新 M2 与新 UAPP 身份使旧运行不能作为 CURRENT |
| TD-UAPP-32 FULL-01 T1 缺表达主体 | `CLOSED_FIXTURE / NOT_VERIFIED` | Scenario v1.2 保持冻结；尚无新环境正式运行证据 |
| TD-UAPP-33 YAML-like 等价表达语义分歧 | `IMPLEMENTED_ZERO_MODEL_VERIFIED / NOT_VERIFIED` | 新 UAPP 在 M3 前做格式无关的用户原值归一；22/22 控制包含正例、缺项负例和非案例硬编码检查；不得在正式运行前上调 PASS |
| TD-UAPP-34 测试发布与后继写回缺失 | `IMPLEMENTED_ZERO_MODEL_VERIFIED / NOT_VERIFIED` | 新 UAPP 已接入 RECORD_PUBLISH、REGISTER_FEEDBACK、CLOSE/OPEN_CYCLE 与恢复幂等；真实 M2 API 控制通过；不得在正式运行前上调 PASS |
| TD-UAPP-35 重启前 Dify/M2 基线不可恢复 | `OPEN / DISCLOSED / NON_PRODUCT` | 已建立全新 Dify/M2 基线；历史 `1568/117` 未恢复且未伪造；新环境非测试保护计数为 `0/0`，旧运行全部保留但置 STALE |
| S5 F2 技术验收 | `IN_PROGRESS / NOT_VERIFIED(PRE_MODEL_BUDGET_CONFLICT)` | 新身份要求 19 个场景重新取证；现行硬上限仅 10 个顶层运行；Gate 在模型调用前 fail-closed，正式调用为 0 |

当前实现没有新增第二状态层、第二数据库或第二运行时，没有真实发布。Founder AC-12 不可开始，
main 不得合并。唯一下一动作是版本化解决 19 个必需正式场景与 10 次顶层硬上限的冲突。
