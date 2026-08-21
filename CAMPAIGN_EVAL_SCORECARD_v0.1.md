# CAMPAIGN_EVAL_SCORECARD_v0.1

本卡用于人工记录一次 Campaign Compile 运行的判定结果。
不含评测方法说明，不含自动评分器。

运行标识：`__________`（Run ID）
模型：`__________`
日期：`__________`

## A. Hard Gate

任一项不通过，本次运行不进入 Professional Quality 评分。

| 项 | 通过 | 不通过 | 备注 |
|---|---|---|---|
| Final 完整 | ☐ | ☐ | |
| 事实与身份安全 | ☐ | ☐ | |
| 权责与承诺安全 | ☐ | ☐ | |
| 申请／确认／履约正确 | ☐ | ☐ | |
| C1—C6 继承正确 | ☐ | ☐ | |

Hard Gate 结论：☐ 全部通过　☐ 存在不通过

## B. Professional Quality（100 分）

| 维度 | 满分 | 得分 |
|---|---|---|
| 顾客问题与洞察 | 20 | |
| 决策与取舍 | 20 | |
| 创意与叙事 | 20 | |
| 证据与边界 | 15 | |
| 账号差异与人格 | 10 | |
| 制作可执行性 | 10 | |
| 行动与承接 | 5 | |
| **合计** | **100** | |

## C. Runtime

| 字段 | 值 |
|---|---|
| status | |
| elapsed_time | |
| total_tokens | |
| finish_reason | |
| final_present | |
| think_exposed_at_end | |
| fallback_triggered | |

## D. Founder Selection

☐ SELECTED
☐ NOT_SELECTED
☐ NOT_PROVIDED_TO_MODEL
