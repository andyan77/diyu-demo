# 统一 Founder Canvas · 技术债登记 v1.5

`task_id: DIYU-V1-UNIFIED-DIFY-APPLICATION-001`

**本表取代 v1.4，成为唯一当前技术债主表。** v1.0–v1.4 原文保留，不覆盖历史失败或判断。未在本版变更的既有条目继续按 v1.4 及其父版本读取。

## 当前验收投影

| 项目 | 当前状态 | 依据 |
|---|---|---|
| 已接受上游产物绑定 | `PASS / CURRENT` | UAAB v1.2；当前候选的非纠正路径正例绑定与错误指纹负例复算均通过 |
| PP b2 事实与 CTA 边界 | `PASS / CURRENT` | UAAB successor；PP/provider 图保持 `8366328b…` |
| 跨轮纠正传播 | **`PASS / CURRENT`** | TD24 正式 run `010fe130…`，C-01…C-12 为 12/12 PASS |
| S4 整体 | **`PASS / CURRENT`** | `UAPP_TD24_S4_CLOSEOUT_v1.0.json`，8/8 PASS |
| S5 | `NOT_STARTED` | 等待 Founder 另行授权 |
| UAPP-AC-12 | `NOT_VERIFIED` | 本轮未授权 Founder 最终实测 |
| main merge | `NOT_ALLOWED` | 本轮明确禁止 |

## TD-UAPP-24｜已由 successor 关闭

旧失败原样保留：用户纠正曾被 M3 识别，却未进入统一任务状态，旧 PD 继续下传并生成新 PP。

当前 successor 的真实结果：

- `production.profile` 与同来源、同作用域的 `production.capacity_or_owner` 由一人同步改为两人；状态 revision 13→14，字段 revision 各精确 +1；
- `production.time_window` 与 `facts.registered` 保持原值和原 revision；
- PD `099061257c9677bd`、`559a204d7c4f1f2a` 因字段变化直接失效；
- PP `a7bf609e2dc9eecb` 通过 `upstream_fp=559a204d7c4f1f2a` 传递失效；
- 旧 PD 被选择器和后置绑定门拒绝；Seam/PP 均未运行，artifact 总数 8→8；
- 无 M2 行、真实发布或其他外部副作用。

关闭证据：Gate `fb040eb9…`，正式 Result `3284ce2b…`，S4 closeout `2296dbc3…`。这只关闭 TD-UAPP-24 的窄问题，不代表 S5、AC-12 或生产就绪。

## 既有条目当前关系

- TD-UAPP-01/03/06/08/16 及 v1.4 标为“仍有效/待 S5”的条目继续保持，S5 未开始。
- TD-UAPP-02/04/11/12/13/14 的实现保留；本轮不外推为最终全场景验收。
- TD-UAPP-05/09/10/15 与 TD-UAPP-18/19/20/23 的 successor 关闭结论继续有效。
- TD-UAPP-17/21/22 的历史状态和证据继续按父账本读取；本轮未改变其绑定。
- `artifact_status=STRUCTURE_MISSING_RAW_PRESERVED` 仍是已披露、非当前合同硬门的技术债；若未来结构化字段成为下游强依赖，需另立任务。

## 保护面与非承诺

M1/M2/M3、Hop、Seam、PP b2/provider、六项专业能力、M2 schema、非测试数据和 main 均未被本轮误改。当前 UAPP 候选图 md5 为 `89bbfeade1f149ccce12a768bed6e94a`；其余受保护图保持冻结值。

本表不授权 S5、Founder AC-12、main 合并、生产发布或经营效果声明。
