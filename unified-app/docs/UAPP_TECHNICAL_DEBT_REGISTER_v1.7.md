# 统一 Founder Canvas · 技术债登记 v1.7

`task_id: DIYU-V1-UNIFIED-DIFY-APPLICATION-001`

**本表取代 v1.6，成为唯一当前技术债主表。** v1.0–v1.6 原文保留；未在本版变更的条目继续按 v1.6 及其父版本读取。

## 当前验收投影

| 项目 | 当前状态 | 依据 |
|---|---|---|
| S4 整体 | `PASS / CURRENT` | 当前候选图未漂移；TD24 S4 closeout 8/8 PASS |
| S5 技术验收 | `NOT_VERIFIED(INPUT_ENVIRONMENT_OR_TOOL)` | CAP-01 的 M3 SSL EOF 与 Dify 一次内部重放；正式全集按停止规则中止 |
| UAPP-AC-01～11 | `NOT_VERIFIED` | 仅第 1/19 个输入发生；不足以上调任一完整 AC |
| UAPP-AC-12 | `NOT_VERIFIED / NOT_AUTHORIZED` | Prompt 2 未授权 |
| main merge | `NOT_ALLOWED` | Prompt 3 未授权 |

## 新披露：TD-UAPP-25｜正式验收传输稳定性与平台内部重放

CAP-01 的 M3 首次模型节点出现 DeepSeek SSL EOF，Dify 自动重放 M3 并成功。本轮业务路由、唯一能力和零暗跑均符合预期，但实际 LLM attempt 为 7，超过单轮静态可达 6；且传输异常前已有模型输出和测试域写入，不满足冻结的纯传输重试资格。

该项当前归因 `INPUT_ENVIRONMENT_OR_TOOL`，不是已确认的统一应用缺陷，也不授权修改 UAPP/M3/Runner/Checker。后继是否允许在相同候选与输入上建立新正式槽位，只能由 Founder 版本化裁决。

## 既有技术债关系

TD-UAPP-24 继续保持 successor 已关闭；v1.6 的其他已关闭、仍有效、STALE、未验证和非阻断披露均不变。本次没有隐藏产品失败，也没有把环境失败改判为系统通过。

## 保护面

UAPP、M1/M2/M3、Hop、Seam、PP/provider、六项专业能力、M2 schema、非测试数据和 main 均未修改。仅正常产品路径创建了本例测试 workspace/cycle/task；没有 artifact、版本、发布或反馈行。
