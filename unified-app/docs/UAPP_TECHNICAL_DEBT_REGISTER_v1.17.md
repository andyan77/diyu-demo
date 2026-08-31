# UAPP Technical Debt Register v1.17

current_register: `true`
parent: `UAPP_TECHNICAL_DEBT_REGISTER_v1.16.md`
task_id: `DIYU-V1-UNIFIED-DIFY-APPLICATION-001`

本版取代 v1.16，成为唯一当前技术债主表；历史版本原文保留。

| 条目 | 当前状态 | 本版依据 |
|---|---|---|
| TD-UAPP-30～34 | `IMPLEMENTED_ZERO_MODEL_VERIFIED / NOT_VERIFIED` | 新候选确定性控制 22/22、真实 M2 API 控制 PASS；Founder 已豁免全新环境 19 项正式复验，故不得上调为技术 PASS |
| TD-UAPP-35 重启前 Dify/M2 基线不可恢复 | `OPEN / DISCLOSED / ACCEPTED_FOR_FOUNDER_TRIAL` | 全新基线已建立；历史 `1568/117` 未恢复且未伪造；当前非测试保护计数 `0/0` |
| S5 F2 技术验收 | `NOT_VERIFIED(FOUNDER_WAIVED_REVALIDATION)` | Founder 明确免除新环境 19 项重复正式复验并批准推进下一步 |
| UAPP-AC-12 Founder 实测 | `READY_FOR_FOUNDER_TEST / NOT_VERIFIED` | v1.1 实测包已绑定当前候选；必须由 Founder 亲自运行并裁定 |

非阻断披露：当前没有真实发布，没有非测试数据写入；main 未合并。正式模型调用保持 0。
