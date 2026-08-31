# UAPP Technical Debt Register v1.14

current_register: `true`
parent: `UAPP_TECHNICAL_DEBT_REGISTER_v1.13.md`
task_id: `DIYU-V1-UNIFIED-DIFY-APPLICATION-001`

本版取代 v1.13，成为唯一当前技术债主表。v1.13 原文保留；未在本版列出的条目继续按父版本读取。

| 条目 | 当前状态 | 本版依据 |
|---|---|---|
| TD-UAPP-29 GAP-01 决定性缺口与后继输入断链 | `CLOSED / PASS / CURRENT` | successor G1 `52f7f504…` 与 G2 `306c2e7f…` 同会话连续通过；G2 产物 7433 字 |
| TD-UAPP-30 EQUIV 正负 Fixture 与能力前置条件不等价 | `OPEN / ORACLE_OR_CRITERION` | 01a 与 01n 均缺表达主体；负例还同时缺 expected change，不是单变量负例 |
| TD-UAPP-31 上传资料未登记为 M2 可撤回素材 | `OPEN / FAIL / CURRENT / P0` | W0 run `c97d9b12…` 上传和读取成功，但 M2 `materials=[]`，W1 无合法撤回对象 |
| TD-UAPP-32 FULL-01 T1 缺表达主体 | `OPEN / ORACLE_OR_CRITERION` | T1 run `f05a4a30…` 精确 Return；T2 不补缺口，完整故事无法连续 |
| S5 F2 技术验收 | `IN_PROGRESS / FAIL / CURRENT` | 8/19 PASS/CURRENT；AC-07 FAIL；AC-03/08/09/11 未验证 |

最窄后继必须先解决 TD-UAPP-31，并版本化修正 TD-UAPP-30/32 的冻结场景与能力前置条件冲突。
不得改写历史失败、放宽专业合同或用旧图证据占位。Founder AC-12 尚不可开始。

