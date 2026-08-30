# 统一 Founder Canvas · 技术债登记 v1.9

`task_id: DIYU-V1-UNIFIED-DIFY-APPLICATION-001`

**本表取代 v1.8，成为唯一当前技术债主表。** v1.0–v1.8 原文保留；未在本版变更的条目继续按父版本读取。

## 当前验收投影

| 项目 | 当前状态 | 依据 |
|---|---|---|
| S4 整体 | `PASS / CURRENT` | 修复 2 只改变空状态无纠正分支；匹配状态纠正分支未变且正负控制通过 |
| S5 F2 技术验收 | `IN_PROGRESS / FAIL / CURRENT` | CAP-05 定向复验仍未运行 Production Director，且有内部标识泄漏 |
| UAPP-AC-01 / 02 | `PASS / CURRENT` | 当前候选、统一自然语言入口和保护面真实证据成立 |
| UAPP-AC-04 / 05 / 10 | `FAIL / CURRENT` | CAP-05 目标能力 0 次、产物为空、用户回复泄露内部能力名 |
| UAPP-AC-03 / 06–09 / 11 | `NOT_VERIFIED` | 达到有界修复上限后其余 14 个冻结输入未运行或正式全集不完整 |
| UAPP-AC-12 | `NOT_VERIFIED / NOT_AUTHORIZED` | Founder 产品实测未授权 |
| main merge | `NOT_ALLOWED` | 技术验收未通过 |

## TD-UAPP-25｜正式验收传输稳定性与平台内部重放

**状态：CLOSED，继承 v1.8。** 本轮两个 CAP-05 Attempt 均为直接 HTTP 200，平台内部重放、人工重试和传输失败均为 0。

## TD-UAPP-26｜用户本轮直接提供的完整产物不能作为合法短入口上游

**状态：OPEN / P0 / CURRENT。**

修复 2 已关闭“空状态无纠正被误拒绝”这一前置缺陷，但真实定向复验继续证明：

- 用户在 CAP-05 原文中直接提供了完整、确认可用的口播稿和制作条件；
- selector 将用户点名的目标能力 `PRODUCTION_DIRECTOR` 错当成上游产物能力，返回 `NAMED_UPSTREAM_INCOMPATIBLE`；
- Hop 没有把本轮脚本投影到 `script_or_equivalent_beats`；
- uapp_fields 只接受历史 accepted ledger selector，不能为用户本轮直接提供的完整正文建立一次性、task-scoped、可复核绑定；
- Seam 与 Production Director 均未运行，产物为空。

最高后继修复面仍应限定在 UAPP 自身的本轮直接 artifact 来源识别、能力兼容和调用前绑定，不能修改 Hop、Seam 或专业能力，也不能放松对历史 STALE、错误 task、错误能力、fp/bfp 失配产物的 fail-closed 保护。

当前 Active Work Package 已使用 `2/2` 个 SUT 修复节点和 `1/1` 个额外正式运行槽，不授权第三次修复。

## TD-UAPP-27｜缺口回复泄露内部能力标识

**状态：OPEN / P0 / CURRENT。**

CAP-05 定向复验的用户回复三次出现字面量 `PRODUCTION_DIRECTOR`，冻结 Checker T-05 正确判 FAIL。该问题与“直接 artifact 未绑定”同一阻断路径同时暴露，但属于用户交付脱敏硬门；不得用改 Checker 或删禁词解决。

## 保护面与副作用

当前授权修改仅涉及 UAPP 的 `uapp_fields` 和 `uapp_td24_correction` 两个已留证修复节点。M1/M2/M3、Hop、Seam、六项专业能力、PP/provider、M2 schema、非测试数据和 main 均未修改。CAP-05 两次 Attempt 仅创建各自测试作用域的 workspace/cycle/task，没有 artifact、content version、publish instance、feedback 或真实发布。
