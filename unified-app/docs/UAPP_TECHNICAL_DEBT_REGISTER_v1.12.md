# UAPP Technical Debt Register v1.12

current_register: `true`
parent: `UAPP_TECHNICAL_DEBT_REGISTER_v1.11.md`
task_id: `DIYU-V1-UNIFIED-DIFY-APPLICATION-001`

本版继承 v1.11 中未列出的全部条目与状态；v1.11 保留为历史，不再是当前投影。

| 条目 | 当前状态 | 本版依据 |
|---|---|---|
| TD-UAPP-28 CAP-06 同轮成片 CTA/平台规范化 | `IN_PROGRESS / CANDIDATE_BUILT` | 根因已独立确认；零模型控制 23/23 PASS；尚未取得正式真实行为证据 |
| CAP-05 inline script direct entry | `CLOSED / PASS / CURRENT` | 修复不触及 Production Director 分支的 companion 语义与专业应用 |
| S5 F2 技术验收 | `IN_PROGRESS / NOT_VERIFIED` | CAP-06 与剩余冻结场景尚未全部完成 |

新增披露：PP `cta_contract` 无条件必填与 Skill“缺省 NO_CTA”语义冲突已由候选外壳修复，
但只有正式 CAP-06 通过后才能关闭 TD-UAPP-28。`artifact_status=STRUCTURE_MISSING_RAW_PRESERVED`
仍按既有裁决披露，不在本轮新增为阻断标准。

