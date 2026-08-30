# 统一 Founder Canvas · 技术债登记 v1.10

`task_id: DIYU-V1-UNIFIED-DIFY-APPLICATION-001`

**本表取代 v1.9，成为唯一当前技术债主表。** v1.0–v1.9 原文保留；未在本版变更的条目继续按父版本读取。

## 当前验收投影

| 项目 | 当前状态 | 依据 |
|---|---|---|
| S4 整体 | `PASS / CURRENT` | 修复 2 不改变匹配状态的纠正与失效传播分支；正负控制通过 |
| S5 F2 技术验收 | `IN_PROGRESS / FAIL / CURRENT` | 当前图 CAP-05 硬门失败且有界修复上限已耗尽 |
| UAPP-CAP-01～04 | `PASS / STALE` | 修复 2 改动的空状态分支在四项旧 RAW 中均真实可达 |
| UAPP-AC-01 / 02 | `PASS / CURRENT` | 当前图 CAP-05 证明统一入口、自然语言、inputs={} 与保护面 |
| UAPP-AC-04 / 05 / 10 | `FAIL / CURRENT` | 当前图 CAP-05 目标能力 0 次、产物为空、回复泄露内部能力名 |
| UAPP-AC-03 / 06–09 / 11 | `NOT_VERIFIED` | 正式场景全集未完成 |
| UAPP-AC-12 | `NOT_VERIFIED / NOT_AUTHORIZED` | Founder 产品实测未授权 |
| main merge | `NOT_ALLOWED` | 技术验收未通过 |

## TD-UAPP-25

`CLOSED`，继承 v1.9。本轮无传输失败、人工重试或平台内部重放。

## TD-UAPP-26

`OPEN / P0 / CURRENT`，继承 v1.9。用户本轮直接提供的完整脚本不能形成合法上游绑定，
Seam 和 Production Director 未运行。

## TD-UAPP-27

`OPEN / P0 / CURRENT`，继承 v1.9。缺口回复泄露 `PRODUCTION_DIRECTOR` 内部标识。

## 证据时效纠正

v1.9 将 CAP-01～04 投影为 CURRENT 不成立。四项旧 RAW 的纠正节点均以空状态和空 delta
进入修复 2 改动的分支，因此旧 PASS 只能保留为 `STALE`。纠正依据见
`UAPP_S5_EVIDENCE_FRESHNESS_CORRECTION_v1.0.md`；没有删除或改写旧证据。

## 保护面

M1/M2/M3、Hop、Seam、六项专业能力、PP/provider、M2 schema、非测试数据和 main 均未修改。
当前 UAPP 的两个改动节点均在授权范围内；没有真实发布内容或非测试副作用。
