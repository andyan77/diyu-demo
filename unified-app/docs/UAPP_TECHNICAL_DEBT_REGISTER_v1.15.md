# UAPP Technical Debt Register v1.15

current_register: `true`
parent: `UAPP_TECHNICAL_DEBT_REGISTER_v1.14.md`
task_id: `DIYU-V1-UNIFIED-DIFY-APPLICATION-001`

本版取代 v1.14，成为唯一当前技术债主表。v1.14 原文保留；未在本版列出的条目继续按父版本读取。

| 条目 | 当前状态 | 本版依据 |
|---|---|---|
| TD-UAPP-30 EQUIV Fixture 前置条件 | `PARTIALLY_CLOSED` | 表达主体与单变量负例已修正；a/c/n PASS，但 b 暴露 YAML-like 语义分歧 |
| TD-UAPP-31 上传资料未登记为 M2 可撤回素材 | `CLOSED / PASS / CURRENT` | W0 `b3e44f33…` 登记 material `dfebe06b…`；W1 successor `1bf080f3…` 撤回同一记录 |
| TD-UAPP-32 FULL-01 T1 缺表达主体 | `CLOSED / PASS / CURRENT` | successor T1 `2e5b9488…` 生成 6348 字 Content Brief |
| TD-UAPP-33 YAML-like 等价表达语义分歧 | `OPEN / FAIL / CURRENT / P0` | EQUIV-01b `c4a7cd78…` 在 M3 首先丢失主目标/承诺/目标类别，未产生成品 |
| TD-UAPP-34 RECORD_PUBLISH 测试写回缺失 | `OPEN / FAIL / CURRENT / P0` | FULL T2 `14d66ec7…` 识别动作但未创建 content version / publish instance，错误回落 M3 |
| S5 F2 技术验收 | `IN_PROGRESS / FAIL / CURRENT` | 14/19 PASS，2 FAIL，3 NOT_RUN_DEPENDENT；AC-03/08 FAIL |

Founder AC-12 不可开始。后继必须分别处理受保护的 YAML-like 语义节点和 UAPP 测试发布写回接缝；不得用下游补值或直接数据库写入制造 PASS。
