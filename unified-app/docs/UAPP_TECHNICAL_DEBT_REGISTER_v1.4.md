# 统一 Founder Canvas · 技术债登记 v1.4

`task_id: DIYU-V1-UNIFIED-DIFY-APPLICATION-001`

**本表取代 v1.3，成为唯一当前技术债主表。** v1.0–v1.3 原文保留不改。v1.3 的既有条目分类继续有效，除非本版明确更新。

## 当前验收投影

| 项目 | 当前状态 | 依据 |
|---|---|---|
| 已接受上游产物绑定 | `PASS / CURRENT` | UAAB v1.2；本轮失败没有推翻正文身份绑定本身 |
| PP b2 事实与 CTA 边界 | `PASS / CURRENT` | successor 证据仍绑定当前 PP 图 |
| 跨轮纠正传播 | **`FAIL / CURRENT`** | `UAPP_CORRECTION_RESULT_v1.0.json` |
| S4 整体 | `NOT_VERIFIED` | 因纠正传播硬门失败未进入收口 |
| S5 | `NOT_STARTED` | 未获启动条件 |
| UAPP-AC-12 | `NOT_VERIFIED` | 无最终候选，不交 Founder 实测 |
| main merge | `NOT_ALLOWED` | 公式未成立 |

## 新增条目

### TD-UAPP-24｜纠正被识别但没有进入规范字段，旧制作方案继续下传　**新增，未修**

冻结用户原话明确把制作规模从一人改成两人。M3 已正确识别这项变化，但 Hop 为 PP 生成的能力外壳没有 `production_profile`；`uapp_fields` 因而只改了 `facts.registered`，没有更新规范制作字段，也没有让依赖 PD 失效。后置血缘门随即把旧 PD 以 `BOUND` 下传，PP 又生成了新标题和封面。

影响：`C-01…C-06` 失败，跨轮纠正传播为 `FAIL / CURRENT`，S4/S5 不得开始。

归因：`SYSTEM_UNDER_TEST`。本轮 `mutation_target=NONE`，不修、不重跑。详见 `UAPP_CORRECTION_FAILURE_TRIAGE_001.md`。

## 既有条目当前关系

- TD-UAPP-01/03/06/08/16 及 v1.3 标为“仍有效/待 S5”的条目继续保持；本轮未进入 S5，不作上调。
- TD-UAPP-02/04/11/12/13/14 的实现保留，但本轮失败不构成它们的最终全场景验收。
- TD-UAPP-05/09/10/15 与 TD-UAPP-18/19/20/23 的既有 successor 关闭结论不因本轮失败追溯撤销。
- TD-UAPP-17/21/22 的历史状态和证据继续按父账本读取；本轮没有修改其绑定。
- `artifact_status=STRUCTURE_MISSING_RAW_PRESERVED` 仍是已披露、非本合同硬门的技术债，不用来解释或掩盖 TD-UAPP-24。

## 保护面与非承诺

运行前后 UAPP、PP/provider、Seam、Hop、M3 与六能力图逐项相等；M2 Schema、非测试发布和反馈计数逐项相等。没有真实发布或外部副作用。不得把本轮 HTTP 200 或 workflow succeeded 读成验收通过。
