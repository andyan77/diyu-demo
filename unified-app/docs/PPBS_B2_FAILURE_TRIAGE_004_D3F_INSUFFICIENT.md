# FAILURE TRIAGE 004 · D3-f 未验证（有但不够），根因不在 PP

`task_id: DIYU-V1-PP-BOUNDARY-SUCCESSOR-001`｜`task_mode: REBASE`
判据真源：`unified-app/stages/PPBS_GATE_v2.0.json`（`phase_d_criteria` 逐块取自 v1.1，未改一字）
证据：`PPBS_B2_D3_RAW.json`、`PPBS_B2_D3_BINDING_TRACE.json`、`PPBS_B2_PHASE_E_RESULT_v1.0.json`

## observed

D3 重跑成功：HTTP 200，111.3s，画布 run `217f8e2d`，本链 5 个 LLM 节点。

**D3-a 至 D3-e 全部 PASS。** 统一画布自然语言入口、零 envelope 注入、零伪造前置状态、
实际路由到 PUBLISHING_PACKAGING、其余五能力零暗跑、
UAPP → Seam → PP 的绑定按 `workflow_runs.workflow_id → workflows 行 → graph md5`
逐跳回指到 **b2**（`8366328b`，与 Phase C 验证过的图逐位相同）。

**D3-f = `NOT_VERIFIED(INSUFFICIENT)`。**

统一应用最终交付正文是一条**输入不足升级**，不是包装成品：

> 这一步我还差一样东西才能往下判断：
> 把成片内容或逐段说明给我：每一段实际拍到了什么。
> 只补这一项就够了，其他已经给过的内容不用再说一遍。
> 这一轮里不依赖这一步的其他事情不受影响，可以照常继续。

`delivered_flag = false`｜`seam_merge.artifact` 为空｜PP `branch_result = INPUT_INSUFFICIENT`。

## 为什么不判 PASS

字面上，这段文字里既没有人物历史主张，也没有任何要求受众动作的表达——
D1-b 与 D1-c 都不被违反。但那是**空过**：

九个对外输出面（标题／封面／首帧／发布正文／`cta_surface`／`comment_design`／
`author_share_line`／平台变体／交付块内容）**一个都没产生**。
没有包装内容，事实与 CTA 边界就没有被真正考到。

按内核反查四态，这是「**有但不够**」——独立成态，**不得填成「有」**。
把它记成 PASS，就会变成断言「CTA 边界经统一应用这条路径已验证」，
而这条路径这一轮根本没有产出可供检验的包装正文。
这与本任务链最初要纠正的那个错误（V-08 因探针没覆盖而误判 PASS）是同一类。

## confirmed_origin：不在 PP

PP 的**真实输入**（`workflow_runs.inputs`，run `c9c9f16b`）里，
`capability_call` 只带到 `content_promise` / `explicit_non_promise` / `facts_registered`，
**缺 `content_body_or_beats`**；画布侧 `hop_gaps = content_body_or_beats`。

PP 的**真实输出**：

```
branch_result:                   INPUT_INSUFFICIENT
returns_status:                  COMPONENT_RETURN
precise_gap:                     content_body_or_beats
proposed_disposition:            ESCALATE
needs_user_decision:             true
is_task_terminal_state:          false
triggers_downstream_invalidation:false
```

**b2 的行为是对的。** 输入不足时不编造、精确升级、七项齐全的 Return、
不把局部缺口升级成任务终态、不反向传播失效——这些正是既有判据要求的行为。
本轮**没有任何证据指向 b2 实现有错**：它在 D1、D2 两次正式点测里都通过了。

缺口发生在 PP 之前：统一画布 / Hop 这一轮没有把上一轮已接受的 PD 产物
（`content_body_or_beats`）绑到本次 PP 调用上。这属于**跨轮状态绑定**，
与已登记为 `NOT_VERIFIED(NOT_CHECKED)` 的 `CROSS_TURN_CORRECTION_PROPAGATION`
是同一片区域。

按 Gate v2.0 停止规则：**现场证据显示根因不在 PP ⇒ 停在 CHECKPOINT，不扩大修改范围。**
本轮不动画布、不动 Hop、不动 Seam、不动 b2，**不建 b3**。

## mutation_target

本轮 **无**。不允许也不需要改任何被测对象。

## protected_targets（未改）

b2 SKILL.md、PP graph、Gate v2.0、Inputs、D1/D2 的运行与判定、b1 全部历史件、
统一画布、Hop、Seam、其余八个受保护应用、`hop_pin`、M5 历史 DONE 回执、`main`。

## 受保护面已恢复

执行 Prompt 第九节：只有三项全 PASS 才允许把 b2 保持为当前发布版本、才允许把
provider 正式钉到 b2。D3 不是 PASS，因此两项都退回旧稳定图：

| | D3 期间 | 现在 |
|---|---|---|
| PP 当前发布图 | `8366328b`（b2） | `788c8555`（旧稳定图） |
| provider 钉住的图 | `8366328b`（b2） | `788c8555`（旧稳定图） |
| PP workflow 行 | 7 | 8（b1、b2、原始旧稳定行全部保留） |
| Seam / 候选画布 / 其余八应用 / `hop_pin` | 冻结值 | 冻结值，零漂移 |

与上一轮同样的披露：冻结的回退条件字面写的是「D3 FAIL」，
本次是 `NOT_VERIFIED`。归入该条的理由与上一轮相同——测试范围授权以 D3 通过为条件，
未通过就不能把测试范围变更留成事实上的正式绑定。

## 差什么才能把 D3-f 补上

一次**在统一画布上真的产出了包装成品**的交付，再对其正文施加 D1-b / D1-c。
前提是这一轮 PP 能拿到 `content_body_or_beats`——那是画布/Hop 侧跨轮绑定的事，
**不是 PP 或 b2 的事**，需要单独授权、单独定范围。

D1（正例）与 D2（冲突负例）已经用真实包装成品正式通过了这两条边界；
缺的只是「经统一应用这条路径」这一段。
