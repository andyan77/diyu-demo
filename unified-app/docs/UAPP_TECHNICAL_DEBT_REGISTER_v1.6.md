# 统一 Founder Canvas · 技术债登记 v1.6

`task_id: DIYU-V1-UNIFIED-DIFY-APPLICATION-001`

**本表取代 v1.5，成为唯一当前技术债主表。** v1.0–v1.5 原文保留；未在本版变更的条目继续按 v1.5 及其父版本读取。

## 当前验收投影

| 项目 | 当前状态 | 依据 |
|---|---|---|
| 已接受上游产物绑定 | `PASS / CURRENT` | UAAB v1.2 与 S4 当前图定向重算 |
| PP b2 事实与 CTA 边界 | `PASS / CURRENT` | PP/provider 图 `8366328b…`；当前 successor 证据 |
| 跨轮纠正传播 | `PASS / CURRENT` | TD24 Result `3284ce2b…` |
| S4 整体 | `PASS / CURRENT` | TD24 S4 closeout `2296dbc3…`，8/8 PASS |
| S5 技术验收 | `IN_PROGRESS / NOT_VERIFIED` | Founder 事件 `UAPP-S5-FINAL-TECHNICAL-ACCEPTANCE-2026-08-30` 只授权 F1/F2；尚无正式模型结果 |
| UAPP-AC-12 | `NOT_VERIFIED / NOT_AUTHORIZED` | Prompt 2 未授权 |
| main merge | `NOT_ALLOWED` | Prompt 3 未授权 |

## 本版变化

- S5 F1 已固定 19 个合同来源自然语言输入；没有加入旧版含糊句或结果导向样本。
- 正式预算预冻结为 19 个顶层输入、静态最多 114 个可达 DeepSeek 节点尝试，低于授权硬上限 22/140。
- Checker 首轮负向控制发现一个夹具错误：暗跑负例误加了本例允许能力。该问题在任何模型调用前独立归因并只修夹具；随后 19 个正例与 190 个逐判据单变量负例全部通过。
- 当前没有新发现的系统技术债；控制通过只证明判定器有区分力，不上调任何产品验收项。

## 既有技术债关系

TD-UAPP-24 继续保持 successor 已关闭；`artifact_status=STRUCTURE_MISSING_RAW_PRESERVED` 继续作为已披露、非当前合同硬门的技术债。v1.5 所列仍有效、已关闭、STALE 与未验证条目均不因本次 F1 文件或控制生成而改变。

## 保护面与非承诺

当前 UAPP、M1/M2/M3、Hop、Seam、PP/provider、六项专业能力、M2 schema、非测试数据和 main 均未被 F1 修改。本表不表示 S5 已通过，不授权 Founder AC-12、最终包、main 合并、生产发布或终态填写。
