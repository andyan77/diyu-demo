# PP 边界后继 · FAILURE TRIAGE 001（D1 CTA 边界）

- `task_id`: `DIYU-V1-PP-BOUNDARY-SUCCESSOR-001`
- `authority`: FOUNDER ADJUDICATION + EXECUTION PROMPT v1.0
- `model_calls`: 1（D1 一次，`skill_llm` 单节点）｜`retries`: 0
- 判定真源：`unified-app/stages/PPBS_PHASE_D_RESULT_v1.0.json`
- 运行真源：PP run `53b90396-eb9a-47ab-8250-92cf117df814`，succeeded，60.14s

**第一次正式 FAIL 已出现，按停止规则立即停止。D2、D3 未执行，未开启第二次修复迭代。**

---

## `observed_failure`

D1 正例的产出里仍然出现要求受众采取动作的表达，逐字：

| 位置 | 原文 | 为什么越界 |
|---|---|---|
| `artifact · cta_surface` | 「`cta_contract = 不做购买、到店、私信或领取引导，只保留内容本身` → **无 CTA**。整份产出（含评论区与转发语）不得出现任何奖励、领取、关注、私信、到店、预约、购买、下单或咨询引导。」 | 原文被**逐字引用之后**，实际执行的约束面只剩业务动作清单，「只保留内容本身」在自检里被丢掉 |
| `artifact · comment_design` 置顶首条 | 「先看衣橱里已有的。你为什么买它？——…」（**被追问的**：问「为什么买它」引出判断过程） | 设计目的由产出**自述**写明是「引出追问」，即为引出受众留言而设计 |
| `artifact · author_share_line` | 「有没有一件，你买了但没怎么穿的？」 | 句末指向受众、等一个回答 |
| `artifact · comment_design` 末行 | 「以上预埋问答均为判断方法的延伸，不构成 CTA。」 | 自行判定某类表达不构成 CTA 从而放行，与旧版「属低风险互动范畴，不改变 NO_CTA 状态」是同一结构，换了措辞 |
| `user_delivery` 评论区段末 | 「这次明确不做购买、到店、私信或领取引导，所以评论区也不放任何这类动作。」 | 交付块里再次把边界复述成四项业务动作 |

**新规则在推理里零痕迹。** 「闭合」「权威顺序」「要求受众」三个词在整份产出中各出现 **0** 次。

---

## `frozen_target`

Gate v1.1 `phase_d_criteria.D1.must_all_hold[2]`（D1-c）：
「不要求受众采取动作：不得出现要求关注、评论、回复、收藏、转发、分享、点赞、参与话题、购买、到店、预约、咨询、私信、领取的表达。」
判据于 Phase A 冻结并提交（commit `33318ff`），早于任何模型调用。

---

## `candidate_sources`

| 候选 | 是否成立 |
|---|---|
| `CONTRACT_OR_INTENT` | 不成立。Founder 裁决 3 表述明确，无歧义 |
| `ORACLE_OR_CRITERION` | 不成立。D1-c 逐条列举了动作面，判据本身可判 |
| `CHECKER_OR_FIXTURE` | 不成立。本次判定读的是产出原文逐字，不依赖 token 探针放行 |
| `INPUT_ENVIRONMENT_OR_TOOL` | 不成立。输入与冻结件逐字段哈希相等（`input_matches_frozen` 全 true）；`cta_contract` 原文完整在输入内 |
| `SYSTEM_UNDER_TEST` | **成立**，但**不在 PP 应用本身，在本轮的修复方案** |
| `INSUFFICIENT_EVIDENCE` | 不成立。原文证据充分 |

---

## `confirmed_origin`

```yaml
confirmed_origin: SYSTEM_UNDER_TEST
failing_node: 本轮 b1 后继 Skill 的**修复覆盖面不足**
```

**根因不是 PP 应用坏了，是这一次修复没修全。**

后继 Skill 在两处装了 CTA 权威顺序：新增「CTA 权威顺序」整节（插在 CTA 三级接缝之后），
以及给「无 CTA 时，评论区能做什么、不能做什么」小节加了前置条件句。

**但 PP-5「评论区是设计出来的，不是等来的」整节没有被约束。** 该节无条件要求：

> - **第一条自己写**，写一条**能被追问的**，不是"感谢支持"
> - 预埋 2 个可能被问到的问题，先准备好答案

产出的置顶首条自述「**被追问的**」——用的正是 PP-5 的原词。模型执行的是 PP-5，
新规则被排在更靠后的位置、且没有显式声明它压过 PP-5。
同理，`author_share_line` 一节也只被 PP-1 规则约束，未被新节覆盖。

**这是本轮修复的影响面算少了（A3「少算」）**：装了规则，但没把规则挂到所有会产生受众动作表达的既有节点上。

---

## `evidence`

```
run_id            53b90396-eb9a-47ab-8250-92cf117df814   succeeded  60.14s  attempts=1
输入与冻结件       capability_call / professional_input / entry / run_mode /
                  example_reference_requested 五项 sha256 全等
PP 版本            2026-08-30 09:05:41.729617（b1）   graph md5 7940dc009d0bba06e1b5ca99dac61e2e
provider 钉        2026-08-29 03:34:58.999575（**未改动**）
LLM 节点           skill_llm × 1，succeeded
产出               artifact 9732 字 / user_delivery 1674 字，delivered
「闭合」「权威顺序」「要求受众」在产出中 0 / 0 / 0 次
```

---

## 本次修复确实生效的部分（不因一处 FAIL 抹掉）

**D1-b PASS —— 事实边界修好了。** 同一场景下：

- 旧版写出「我们门店的搭配师苏禾，教顾客挑衣服时一直在用这套『三问』」并加脚注标注推断；
- b1 版：`一直在用 / 常用 / 长期以来 / 十年 / 历来 / 向来 / 一贯 / 多年来 / 一直以来 / 从来都`
  十个探针在 artifact 与 user_delivery 中命中 **0 次**；涉及人物处均为对上游 PD 计划中
  既定镜头的引用，不是历史行为断言。

D1-a、D1-d、D1-e 同样 PASS：交付完整（标题三候选、封面两层文字、发布文案、评论区、两项待拍板），
未因约束收紧而空交付或整任务拒绝。

---

## `mutation_target`（**本轮不授权实施**）

若规划侧决定继续，最小修复对象是**同一个 b1 后继 Skill**，把 CTA 权威顺序挂到所有会产生
受众动作表达的既有节点上，至少：PP-5 整节、`author_share_line` 一节、`cta_surface` 自检行。
方式仍必须是规则层、无案例专用分支。

**本 Prompt 明确禁止第二次修复迭代，因此不实施。**

## `protected_targets`（无证据证明有错，不得修改）

M1、M2、M3、Hop、Seam、统一画布投影层、其余五个能力应用、旧 PP Skill 两份、旧 PP Workflow 版本行、
M5 历史 DONE 回执、任何历史 RAW/Gate/Result、main。

## `next_reverification`（供规划侧冻结，不在本轮执行）

按原冻结目标定向复验：D1 正例、D2 冲突负例、D3 统一应用短入口，顺序与判据不变。
