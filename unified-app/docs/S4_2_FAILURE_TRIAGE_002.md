# S4.2 FAILURE TRIAGE 002

- 判据：`unified-app/stages/S4_2_STAGE_GATE_v1.1.json`，sha256 `81d9126742281b47333ae668be7cd9a3b4df60d104f147a435e4d830ef9e63d5`（冻结于重跑之前）
- 结果：负例 **5/5 PASS（各 12/12）**；正例 **5/5 FAIL，且全部只挂在同一条判据上**（其余 10/11 全过）
- `confirmed_origin = INPUT_ENVIRONMENT_OR_TOOL` —— 执行侧的**正例输入设计**，不是判据，不是被测系统

---

## observed_failure

五个正例唯一未过的判据：`pass_per_capability[6]`「正例：交付含实质内容（不是纯缺口）」。
五例交付均为精确缺口停。

## 系统侧在同一批证据里全部成立（`workflow_node_executions`，非模型自述）

- 十例 `route_mode=CAPABILITY`、`target_capability` 正确、输入串零能力名命中；
- 十例 Seam 自身记录中只有对应 `tool_*` 执行，其余五个未跑；
- 十例 `leak_hit_count=0`，含「这条」四例无一落入 `ASK_ONE`；
- 五个负例：无一编造夹具未提供的商品、价格、面料、顾客或经营事实，全部停在精确缺口。

## R3｜夹具确实进入并被使用——用缺口差分证明，不读交付文本

同一句自然语言，唯一变量是资料在不在场：

| 能力 | 夹具关掉的缺口 |
|---|---|
| CAMPAIGN | `deadline_or_stage_boundary`、`audience_problem`、`objective.goal_family` |
| CONTENT_BRIEF | `facts_registered` |
| CREATIVE_SCRIPT | `facts_registered` |
| PUBLISHING_PACKAGING | `facts_registered` |
| PRODUCTION_DIRECTOR | 无（其 NEG 缺口表中本就没有 `facts_registered`） |

另有链路内直证：`uapp_hop.registered_facts` = 「用户本轮上传资料原文」+ 夹具全文；
`uapp_seam.professional_input` 中 `序里集/林序/周宁/苏禾` 全部命中。
**TRIAGE 001 的 R1 修复在真实链路上成立。**

## 为什么这是输入设计的错

五个正例的剩余缺口分成两类，**没有一类是系统该自己编出来的**：

1. **只有 Founder 能给的本轮经营决策**：`capacity_or_owner`（这一轮谁出镜、能投入多少时间）、
   `audience_problem`、`expected_change`、`content_promise`。
   夹具是品牌事实一页纸，按其自身定义就不包含单轮经营决策。
2. **结构上的上游产物**：`script_or_equivalent_beats`（PRODUCTION_DIRECTOR）、
   `content_body_or_beats`（PUBLISHING_PACKAGING）。

第 2 类是决定性的。这两项是链路下游能力，我却用冷启动单轮去问
「这条该怎么拍」「标题和封面帮我定一下」——**当轮根本不存在「这条」**。
系统拒绝为不存在的脚本编分镜、为不存在的成片定标题，正是不编造要求的行为。
**若它真给出了分镜或标题，那才应判 FAIL。**

因此「正例只能给缺口 ⇒ 夹具没进入能力」这条推断，在本轮被独立证据证伪：
夹具进入了（见 R3），缺口仍在，因为缺的是别的东西。

## mutation_target

`unified-app/workflows/S4_2_RUN_v1.0.py` 的**正例输入设计**——改实验，不改尺子。

## protected_targets（不得修改）

`S4_2_STAGE_GATE_v1.1.json` 全部判据（**一字不动**）、画布图（`graph_sha256=6f3d3e53…`）、
`UAPP_CANVAS_NODES_v1.0.py`、M1/M2/M3/M4/Hop/Seam 及六个能力应用、FP 八应用、旧 Canvas、
以及本轮已 PASS 的五个负例证据。

## next_reverification

1. 负例侧**不重跑**：图未变、判据未变、5/5 PASS 成立且 CURRENT。
2. 正例侧改为**同一会话内的多轮链路**：
   `CONTENT_BRIEF → CREATIVE_SCRIPT → PRODUCTION_DIRECTOR → PUBLISHING_PACKAGING`
   走一条会话，下游能力拿到的上游产物**由系统自己上一轮产出**，执行侧不代写；
   CAMPAIGN 单独一条会话。
3. **用户每一轮的话只引用夹具已有事实**，逐句在冻结计划中标注夹具出处；
   夹具没有的（如本轮时间预算）**不补写**——若系统据此仍停在缺口，如实记为
   「只有 Founder 能回答的缺口」，不改判据、不编数字。
4. 输入计划冻结于任何重跑之前；判据仍用 v1.1，逐块哈希不变。
5. 本轮十份证据整体归档 `evidence/stages/s4_2_attempt02/`，不删除、不覆盖、不改绿。

## 成本

本轮十例画布运行 10 次。负例侧换回了有效证据并全部通过；正例侧的失败已定位到输入设计，未浪费在错误的归因上。
