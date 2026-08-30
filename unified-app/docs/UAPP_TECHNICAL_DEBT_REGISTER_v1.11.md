# 统一 Founder Canvas · 技术债登记 v1.11

`task_id: DIYU-V1-UNIFIED-DIFY-APPLICATION-001`

**本表取代 v1.10，成为唯一当前技术债主表。** v1.0–v1.10 原文保留；未在本版变更的条目
继续按父版本读取。

## 当前验收投影

| 项目 | 当前状态 | 依据 |
|---|---|---|
| S4 整体 | `PASS / CURRENT` | 当前改动只触及 inline-artifact 分支；纠正传播保护节点逐字节不变 |
| S5 F2 技术验收 | `IN_PROGRESS / FAIL / CURRENT` | successor CAP-05 PASS；CAP-06 无包装 artifact |
| UAPP-CAP-05 | `PASS / CURRENT` | run `13eb198b…`，Production Director 单能力真实产出 |
| UAPP-CAP-06 | `FAIL / CURRENT` | run `e71e84af…`，CTA contract 缺口，artifact 为空 |
| 其余 17 项 | `NOT_VERIFIED` | 冻结顺序要求 CAP-05/06 均通过后才继续，未运行 |
| UAPP-AC-01 / 02 | `PASS / CURRENT` | 当前图统一入口、自然语言、`inputs={}`、保护面成立 |
| UAPP-AC-04 | `FAIL / CURRENT` | PP 可达但未完成最小可执行 smoke |
| UAPP-AC-05 | `NOT_VERIFIED` | CAP-05/06 隔离成立，但正式全集未完成 |
| UAPP-AC-03 / 06–11 | `NOT_VERIFIED` | 正式场景全集未完成 |
| UAPP-AC-12 | `NOT_VERIFIED / NOT_AUTHORIZED` | S5 技术验收未通过 |
| main merge | `NOT_ALLOWED` | 技术验收未通过 |

## TD-UAPP-25

`CLOSED`，继承 v1.10。本轮正式运行无传输失败、人工重试或平台内部重放。

## TD-UAPP-26

`PARTIALLY_CLOSED / CURRENT`。当前轮合法脚本已能直接到 Production Director：完整正文、来源、
task、指纹、两个必要 companion 字段和真实专业产出全部通过。当前轮已实现内容也能完整绑定到
Publishing & Packaging；剩余缺陷转为 TD-UAPP-28，不追溯撤销 CAP-05 PASS。

## TD-UAPP-27

`CLOSED / CURRENT`。CAP-05 成品与 CAP-06 精确缺口回复均未泄露内部能力名、字段名、状态码或
JSON。历史泄露 Attempt 原样保留。

## TD-UAPP-28｜CAP-06 当前轮成片缺少 CTA 合同规范化

`OPEN / P0 / CURRENT`。冻结输入明确要求自然 CTA，并排除价格、折扣和站外购买承诺；UAPP 已
绑定 78 字完整成片正文及内容承诺，但没有把用户原话规范为受限的平台内低风险 CTA contract。
PP b2 按既有充分性闸准确停下并只问一个缺口，没有编造成品。

最高失效节点是 UAPP inline-artifact companion normalization，不是 Hop、Seam 或 PP。最小后继
只需在同源 record 中增加受用户原话支持的 `cta.contract`，继续保留业务转化/高风险 CTA 的
明确授权边界。当前授权已用尽唯一 successor，禁止在本版继续修复或重跑。

## 保护面

M1/M2/M3、Hop、Seam、六项专业能力、PP/provider、M2 schema、非测试数据和 main 均未修改。
没有真实发布；CAP-05/06 只创建各自测试作用域的 workspace/cycle/task，未产生 artifact、
content_version、publish_instance 或 feedback row。
