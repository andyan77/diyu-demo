# S4 Phase C · C3 层 FAILURE TRIAGE 002

- `task_id`：`DIYU-V1-UNIFIED-DIFY-APPLICATION-001`
- 冻结规格：`S4_PHASE_C_POINT_VERIFICATION_FREEZE_v1.1.json`（sha256 `789ed5586fd099247b2aef69d1b8f0bfd87a8a6b5a015efdb06d6819bf57ab5e`），判据早于结果
- 判定书：`S4_PHASE_C_RESULT_v1.1.json`；证据：`unified-app/evidence/stages/s4_phase_c/S4-PC-T1…T6.json`
- 本文件只追加登记。**未改判据、未改检查器、未改冻结输入、未改被测对象、未重跑。**

## 层级结果

| 层 | 结果 | |
|---|---|---|
| C1 Content Brief 受影响模块单点 | **PASS** | 6/6 |
| C2 M3 → Hop → Seam → Content Brief 相邻接缝 | **PASS** | 8/8 |
| C3 原窄链 CS → PD → PP | **FAIL** | 9 PASS / 4 FAIL |

C3 的四条 FAIL 分属两个互不相干的原因。

---

## 原因 A｜真实缺陷：`P3-04` `P3-05` `P3-06` 同一根因

### 观察

同一条会话（`dd8c63bb`），`registered_facts` 恒为 2531 字，`upstream_delivery` 恒为那份 6188 字的 Content Brief：

| 轮 | 目标能力 | hop 缺口 | `content_promise` | `content_origin_mode` | `primary_goal` | artifact |
|---|---|---|---|---|---|---|
| T2 | CONTENT_BRIEF | 无 | 37 字 | 空 | 27 字 | **6188** |
| T3 | CREATIVE_SCRIPT | `content_origin_mode` | 22 字 | 空 | 25 字 | 0 |
| T4 | CREATIVE_SCRIPT | `content_promise` | **空** | **18 字（用户已答）** | 25 字 | 0 |
| T5 | PRODUCTION_DIRECTOR | `content_origin_mode；time_window；content_promise` | 空 | **又变空** | 37 字 | 0 |
| T6 | PUBLISHING_PACKAGING | `content_body_or_beats；content_promise` | 空 | 空 | **空** | 0 |

### 决定性证据（自足，不依赖任何"同一输入"前提）

系统在 T3 提问：

> 这条的素材是现拍、用已有素材剪、访谈、还是生成的？（这项猜错整条会作废，我不替你默认）

用户在 T4 回答，hop 确实抽到了：`content_origin_mode = 使用门店已有素材剪辑，不安排重新拍摄`。

**然后系统在 T5 逐字重复了同一个问题**，而该轮 `content_origin_mode` 又是空的。

同类丢失还有两处：`content_promise` 在 T2/T3 有值、T4 起恒空；`primary_goal` 在 T2–T5 有值、T6 变空。

这不需要论证"输入相同结论不同"——**已在同一任务内确认过的字段，在后续轮次被重新抽空，系统因此重复提出已经被回答过的问题**，本身就是可直接观察的失效。

### 与上一轮 `TD-UAPP-18` 的关系

上一轮把这类现象叫"Hop 抽取判定不稳定"，前提是"同一输入、同一张图、同一份夹具，两次结论不同"。Phase A 复算推翻了那个前提（两次 T2 的输入在四个字段上不同），因此没有采纳。

**本轮不重新采纳那个前提，也不主张它。** 本轮主张的是范围更窄、证据更强的另一件事：跨轮已确认字段会丢失。二者不是同一个命题，不得互相替换。

### `confirmed_origin`

`SYSTEM_UNDER_TEST`。

### `highest_failing_node`

**跨轮"已确认字段"没有承载体。**

- 画布的会话变量只有 `uapp_last_artifact` 与 `uapp_last_capability` 两个（Phase B 新增的 `uapp_persist` 闸门保护的正是这两个，它工作正常——`P3-07` PASS）；**没有承载"本任务已确认字段"的变量**。
- hop 每一轮都由 `m5_extract`（LLM）把全部字段从零重抽。于是每一轮都有一次把必填字段抽空的机会，多轮链路在结构上无法走完。

这与 Phase B 修掉的那个缺陷是**同一架构类别**：把"某个确定性来源在不在场"交给模型裁决。区别只在承载物不同——上次是本轮上传的事实，这次是前序轮已确认的字段。

**不指向 `m5_extract` 的 prompt。** 改 prompt 是下游统计补丁：LLM 的逐字段召回率不是可修复的保证，而已确认字段的在场性是确定性事实。

### `mutation_target`（本轮不执行）

跨轮已确认字段的承载与合成规则。具体方案属规划侧。

### `protected_targets`

修复后的 hop `m5_compose`、候选画布、九个受保护应用、全部冻结判据与冻结输入、C1/C2 的十四条已成立判据。

---

## 原因 B｜判据侧陈旧：`P3-12`

`P3-12` 继承 `C11`，比对的是 `UAPP_R0_PROTECTED_BASELINE.json`——那是 **Phase B 修复之前**的基线，HOP 那一行仍是 `d230b62f…`。本轮 Prompt 授权了对 HOP 的最小修复，修复后必然是 `e38378c3…`。

九个应用逐个复算：

| | R0 基线（修复前） | Phase C 冻结绑定 | 现在 | Phase C 期间漂移 |
|---|---|---|---|---|
| HOP | `d230b62f…` | `e38378c3…` | `e38378c3…` | **无** |
| 其余八个 | 与绑定一致 | | 与绑定一致 | **无** |

**Phase C 全程零漂移**，由运行器预检在 C2 前、C3 前各验一次（均报 `受保护面 9/9 无漂移`），本次判定后再验一次。

`confirmed_origin`：`ORACLE_OR_CRITERION`。我在冻结 v1.0/v1.1 里把候选图身份换成了 `8c9788f2…`，却漏了同一条判据引用的受保护应用基线，让它与本轮已授权的 Phase B 改动自相矛盾。**这是我的冻结规格缺陷，不是被测对象漂移。**

按停止规则本轮不修。

---

## 披露｜运行窗口内存在第三方写入者

同一个 Dify 实例中，应用 `FCVSS`（`18dd7b02-b661-4cad-a8db-23058e1bcb48`）在 Phase C 窗口内跑了 **44 次**，并上传了 `wash-log.txt`、`swatch.png`、`report.pdf`、`spec.docx`、`batch.xlsx`、`deck.pptx`、`broken.pdf` 等与本任务无关的文件。

- **不属于本任务**，与本任务九个受保护应用、候选画布、`diyu_business` 均无交集。
- 本轮全部判定读的都是按应用作用域取的记录（`app_id` 限定），不受影响。
- LLM 节点归属逐条核过：32 次全部落在本任务的应用上，`FCVSS` 零占用。
- **但我的预检项"运行窗口内没有其它写入者"只打印了一个数字、没有真正把门**。这是运行器缺陷，一并登记。

---

## `actual_cost`（Phase C 三层实测）

| 项 | 冻结预算 | 实际 | |
|---|---|---|---|
| 顶层 Dify workflow run | 7 | **7** | 画布 6 + Content Brief 直调 1 |
| 嵌套应用 run | ≤24 | **24** | |
| DeepSeek LLM 节点尝试 | 预期 35 / 上限 44 | **32 成功 / 0 失败** | 低于预期，正因为 CS/PD/PP 没产出 |
| 重试 | ≤1（仅纯传输失败） | **0** | |
| 夹具上传 | 6 | **6** | 每轮一次，size 6119 |
| M2 `diyu_business` | workspace/account/cycle/task 各 1 | **各 1** | `task_snapshots`／`artifacts`／`publish_instances` 各 0 |
| 重复幂等键 | 0 | **0** | |
| 真实内容平台 | 从未连接 | **`publish_instances` 0 行** | |

全部在预算内，无一项越界。

---

## 本轮处置

- **C3 = FAIL**，立即停止。不改输入、不改 Checker、不改图、不换模型、不调参数、不追加轮次、不做第二次修复。
- `FACT_SUFFICIENCY_CHAIN_REPAIR` 与 `S4_CONTENT_ORIGIN_CONTINUATION` **均不上调**——冻结规格写明两者要三层全部成立。
- 根任务保持 `IN_PROGRESS`，`terminal_state` 未设，停在 CHECKPOINT。
- `main` 未动；任务分支本轮不 push（push 的条件是三层全 PASS，未达成）。

## 已经成立、可独立复核的部分

本轮 Prompt 的核心问题分三段，据实分别登记：

| 段 | 状态 | 依据 |
|---|---|---|
| ① 定位事实第一次从"来源明确且可用"变成 `facts_registered` 缺失的位置 | **成立** | Phase A：同一会话六轮来源恒非空、外壳四在场两为空；同一次 `m5_compose` 把 `registered_facts` 原样写进 `professional_input` 又判它是缺口 |
| ② 修复最高失效节点，使事实真正抵达 Content Brief | **成立** | C1 PASS 6/6 + C2 PASS 8/8：`registered_facts` 2531 字逐跳保持、hop 缺口 `无`、Content Brief 产出 6188 字非占位 artifact；修复前同一场景 artifact 为 0 |
| ③ 补齐 `content_origin_mode` 后的 CS→PD→PP 窄链被一次有效测试真正覆盖 | **测试有效，链路未走通** | 测试确实跑到了并且有判别力：T3 精确提出 `content_origin_mode`（`P3-05` 前半成立）、T4 用户答后该项不再是缺口。但链路停在**另一个**缺陷上——跨轮已确认字段丢失 |

**②不等于③。** 事实充分性这一跳修好了并被验证；窄链没走通，原因是同一架构类别的第二个缺陷，位置已定位、证据已落盘。
