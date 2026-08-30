# 统一 Founder Canvas · 技术债登记 v1.8

`task_id: DIYU-V1-UNIFIED-DIFY-APPLICATION-001`

**本表取代 v1.7，成为唯一当前技术债主表。** v1.0–v1.7 原文保留；未在本版变更的条目继续按 v1.7 及其父版本读取。

## 当前验收投影

| 项目 | 当前状态 | 依据 |
|---|---|---|
| S4 整体 | `PASS / CURRENT` | 当前候选图未漂移；TD24 S4 closeout 8/8 PASS |
| S5 F2 技术验收 | `IN_PROGRESS / FAIL / CURRENT` | 后继 CAP-05 路由正确，但目标 Production Director 未真实运行 |
| UAPP-AC-04 / UAPP-AC-05 | `FAIL / CURRENT` | CAP-05 的 Seam 和 Production Director 均为 0 次；冻结 Checker CAP-02 FAIL |
| 其余 UAPP-AC-01–03 / 06–11 | `NOT_VERIFIED` | 在第 5/19 个正式输入后按首个硬门失败停止 |
| UAPP-AC-12 | `NOT_VERIFIED / NOT_AUTHORIZED` | Prompt 2 未授权 |
| main merge | `NOT_ALLOWED` | Prompt 3 未授权 |

## TD-UAPP-25｜正式验收传输稳定性与平台内部重放

**状态：由本次 successor 证据关闭。**

原 CAP-01 的 SSL EOF 和一次 Dify 内部重放仍保留为 `INVALID_FOR_ACCEPTANCE / INPUT_ENVIRONMENT_OR_TOOL`，不追溯改判。Founder 授权的唯一后继槽位已在相同候选、输入、Gate、Runner 和 Checker 下成功执行 5 个场景；共 25 个 LLM 节点尝试，节点失败、人工重试和平台内部重放均为 0。后继停止原因已转为独立的产品硬门失败，不再是 TD-UAPP-25 的环境问题。

## 新增：TD-UAPP-26｜独立 Production Director 短入口被已接受上游绑定闸门拦截

CAP-05 的冻结输入“这条要怎么拍？场地、机位、要准备什么，帮我出一份拍摄方案。”被正确路由到 `PRODUCTION_DIRECTOR`，但新会话没有已接受 `script_or_equivalent_beats` 产物，上游选择与绑定在 Seam 前 fail-closed。结果是专业能力未被调用，无法满足根合同中“六能力分别可达，每能力至少一次最小 smoke”的 AC-04，也不满足 AC-05 的模块实际调用与用户任务一致。

本轮只登记，不修复。最小后继候选是明确区分“用过期/错误上游继续生成”与“无上游时进入专业能力获得精确缺口”；任何修复都必须保留 TD-UAPP-24 已验证的过期产物 fail-closed 边界。该候选需 Founder 新的版本化授权。

## 保护面

UAPP、M1/M2/M3、Hop、Seam、PP/provider、六项专业能力、M2 schema、非测试数据和 main 均未修改。后继五个场景仅通过正常产品路径各创建 1 个测试 workspace/cycle/task；artifact、content version、publish instance 和 feedback record 均为 0。
