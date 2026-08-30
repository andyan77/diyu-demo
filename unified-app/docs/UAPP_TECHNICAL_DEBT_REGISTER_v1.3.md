# 统一 Founder Canvas · 技术债登记 v1.3

`task_id: DIYU-V1-UNIFIED-DIFY-APPLICATION-001`

**本表取代 v1.2，成为唯一当前技术债主表。** v1.0–v1.2 原文保留不改；历史 FAIL、RETURN、Attempt 和旧图身份继续有效为历史事实，不被本版覆盖。

当前候选身份：UAPP `85c01f85-a081-43e9-ab09-9993289cc200`，图 `91a3984b2c3797d6741165b116fa3cb1`（50 节点 / 52 边）；PP 与 provider 均为 `8366328bf827bd0f460455d750d45c4f`；Seam `db49a3da8973d4fdcbe9ecf63bdf7e2a`；Hop `e38378c3c2a66b75aa7e645368c9e1ce`。

## 一、当前验收投影

| 项目 | 当前状态 | 当前依据 |
|---|---|---|
| 已接受上游产物绑定 | `PASS / CURRENT` | UAAB v1.2 T2/T3 真实连续链 |
| PP 事实边界与 CTA 边界 | `PASS / CURRENT` | PP b2 successor 证据；旧失败原样保留 |
| 跨轮纠正传播 | `NOT_VERIFIED (NOT_CHECKED)` | 本轮 Gate 尚未执行真实用户轮 |
| S4 整体 | `NOT_VERIFIED` | 等待纠正传播后按当前图重算 |
| S5 | `NOT_STARTED` | 仅在 S4 全部必要项 `PASS / CURRENT` 后开始 |
| UAPP-AC-12 | `NOT_VERIFIED` | 最终候选尚未交 Founder 实测 |
| main merge | `NOT_ALLOWED` | AC-01…12 与 Founder ACCEPT 尚未全部成立 |

## 二、v1.2 条目在当前图上的分类

| 条目 | 当前分类 | 说明 |
|---|---|---|
| TD-UAPP-01 完整主故事不稳定 | `仍有效 / 待 S5` | 当前图尚未运行最终 FULL-01，旧失败不外推也不删除 |
| TD-UAPP-02 写回链接线 | `当前图实现保留；正式结论待 S5` | 规范载体和链路 successor 已成立，最终全场景写回仍待验 |
| TD-UAPP-03 缺口轮多问 | `仍有效 / 待 S5 GAP-01` | 未被 UAAB successor 覆盖 |
| TD-UAPP-04 撤回交付矛盾 | `当前图实现保留；正式结论待 S5` | 未在当前最终候选运行 WITHDRAW-01 |
| TD-UAPP-05 旧裁定器假 PASS | `已关闭，历史教训保留` | 后继判定均绑定真实正文和节点证据 |
| TD-UAPP-06 等价表达与恢复未运行 | `仍有效 / 待 S5` | EQUIV 与 RECOVERY 仍未在当前最终候选运行 |
| TD-UAPP-07 旧图结果不同步 | `机制已关闭；旧证据按 A3 保持 STALE` | 当前 Gate、Manifest 必须绑定当前图 |
| TD-UAPP-08 M5 八项技术债 | `仍有效` | 本任务未授权偿还 |
| TD-UAPP-09 Checker 缺图新鲜度 | `已关闭 / CURRENT` | 当前冻结件显式绑定 app/workflow/provider/graph |
| TD-UAPP-10 双哈希口径 | `已关闭 / CURRENT` | 同时记录数据库 md5 与规范化 sha256 |
| TD-UAPP-11 意图—能力桥接 | `实现保留；当前图正式结论待 S5` | UAAB T2/T3 路由为窄 successor，不代替六能力全集 |
| TD-UAPP-12 输出类型漏检 | `实现保留；当前图正式结论待 S5` | 旧修复不删除，最终候选仍按真实节点结果验收 |
| TD-UAPP-13 分诊预算不足 | `实现保留；当前图正式结论待 S5` | 当前节点预算已提高，最终自然路由仍待 S5 |
| TD-UAPP-14 空头支票守卫漏句式 | `实现保留；当前图正式结论待 S5` | 最终零内部泄漏仍待 S5 |
| TD-UAPP-15 Checker 元组比较缺陷 | `已关闭，历史证据保留` | 后继检查不沿用该错误谓词 |
| TD-UAPP-16 歧义负例未成立 | `仍有效 / 待 S5 冻结负例` | 不追溯改旧 Gate，不以新例覆盖旧 FAIL |

## 三、successor 新投影

| 条目 | 分类 | 说明 |
|---|---|---|
| UAAB 已接受正文绑定 | `已被 successor 关闭 / CURRENT` | selector 原文、fp/bfp、能力、task、accepted/stale 均真实核对 |
| PP 事实与 CTA 边界旧失败 | `已被 PP b2 successor 关闭 / CURRENT` | 旧 FAIL 留在历史账本，新图上定向 successor PASS |
| 跨轮纠正传播 | `未验证` | 本轮唯一真实场景尚未调用 |
| `artifact_status=STRUCTURE_MISSING_RAW_PRESERVED` | `新披露但不阻断` | 当前合同要求自然语言成品，不冻结结构化状态为硬门；若未来成为下游强依赖，另立任务 |
| Founder 产品自然性 | `未验证` | AC-12 必须由 Founder 对最终候选实测，执行侧不得代判 |

## 四、持续非承诺

- 不连接真实发布、投流、交易或线索系统。
- 不宣称真实经营提升。
- 不把测试域结果外推到非测试数据。
- 不因 UAAB 局部通过宣称统一应用、S4 或 S5 已完成。
- 不在 Founder AC-12 前合并 main。
