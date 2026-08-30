# UAPP Technical Debt Register v1.13

current_register: `true`
parent: `UAPP_TECHNICAL_DEBT_REGISTER_v1.12.md`
task_id: `DIYU-V1-UNIFIED-DIFY-APPLICATION-001`

本版取代 v1.12，成为唯一当前技术债主表。v1.12 原文保留；未在本版列出的条目继续按父版本读取。

| 条目 | 当前状态 | 本版依据 |
|---|---|---|
| TD-UAPP-28 CAP-06 同轮成片 CTA/平台规范化 | `CLOSED / PASS / CURRENT` | run `9f6ff2fe-b59a-4e46-85d5-c9577b1bd255`；正文 hash、平台、低风险 CTA、六类包装、单能力和副作用门全部通过 |
| TD-UAPP-29 GAP-01 决定性缺口与后继输入断链 | `OPEN / FAIL / CURRENT` | G1 问截止时间，但冻结 G2 补商品/内容方向；同会话无法按冻结链继续。run `347272fd-df0f-4ddd-aaea-cf904f0e3236` |
| GAP Checker 节点位置过度编译 | `DISCLOSED / NON_BLOCKING_ORACLE_DEBT` | Checker 要求 `uapp_ask_one` 且零能力运行，高于根合同；不用于本次 SUT FAIL，也未在结果后改 Checker |
| CAP-05 inline script direct entry | `CLOSED / PASS / CURRENT` | 当前候选未改变 CAP-05 依赖接缝，既有真实 PASS 保留 |
| S5 F2 技术验收 | `IN_PROGRESS / FAIL / CURRENT` | CAP-01～06 PASS；GAP-01:G1 FAIL；其余 12 项按停止规则未运行 |

TD-UAPP-29 的最窄后继应位于 UAPP 的模糊周期请求决定性缺口/路由接缝。不得修改受保护的
CAMPAIGN 专业合同来迎合冻结 G2，也不得把 Checker 的节点位置要求偷加成产品语义。
