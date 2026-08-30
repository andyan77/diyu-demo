# S4 · PP 交付边界 FAILURE TRIAGE 001

- `task_id`: `DIYU-V1-UNIFIED-DIFY-APPLICATION-001`
- `authority`: CONTINUE EXECUTION PROMPT v1.0《DIYU V1 · UAPP S4 证据真值纠偏与 PP 交付边界归因》第四节
- `constitution`: `UNIVERSAL-BOUNDED-EVIDENCE-AI-COLLABORATION v0.3.1-kernel revision 2`
- `model_calls`: 0 ｜ `dify_writes`: 0 ｜ `workflow_runs_started`: 0
- `git_head_at_review`: `a13a73458ee8e3008d67fc4b14758b80296a0df2`
- 证据真源：`unified-app/evidence/stages/s4_canonical_state/S4_EXTERNAL_REVIEW_EVIDENCE_v1.0.json`

本文件是**新增**文件，不覆盖 `S4_CANONICAL_STATE_FAILURE_TRIAGE_004.md` 与任何 v1.0/v1.1 冻结件。

---

## 0. 复核共同前提（零模型独立重算，不引用既有摘要）

| 事实 | 重算值 | 来源 |
|---|---|---|
| 顶层 run | 7/7 succeeded | T1–T7 RAW `workflow_run_id` |
| 嵌套应用 run | 28/28 succeeded | RAW `nested_app_runs` 逐条计数 |
| LLM 节点执行 | 39 succeeded / 0 failed | `workflow_node_executions` 按窗口与十个 app_id 现查 |
| 会话 | 单一 `5cfcaf57-8808-4fc7-8c66-d661e515d05a` | RAW |
| 每轮 Seam 工具 | T1/T2=`tool_content_brief`，T3/T4=`tool_creative_script`，T5/T6=`tool_production_director`，T7=`tool_publishing_packaging` | Seam `latest_run_nodes` |
| CB artifact | 6600 · `5912166572ff6e23…` | T2 `uapp_seam.artifact` |
| CS artifact | 6016 · `81635d887e13ef6e…` | T4 同上 |
| PD artifact | 10121 · `b032cfd7cb6f1862…` | T6 同上 |
| PP artifact | 14984 · `88909e875b0c4c69…` | T7 同上 |
| T7 上游 | `upstream_capability = PRODUCTION_DIRECTOR`，`sha256(upstream_delivery) = b032cfd7cb6f1862…` | T7 `uapp_hop.inputs` |
| 链哈希相等 | **True**（T7 上游 == T6 PD artifact，逐字节） | 现算 |
| 受保护面 | 9/9 md5 与 `RUN_META.scope_snapshot_before` 一致；候选图 `6bf7c8f5f050e0e8…`（49 节点 / 51 边）一致；`hop_pin` 一致 | 复核时点现查 |

**这一节全部成立。技术链是真的，本文件不否定它。**

---

## F1 · SYSTEM_UNDER_TEST — PP 把未登记的人物长期行为写成事实

- `observed_failure`：PP 在发布文案里写「我们门店的搭配师苏禾，教顾客挑衣服时一直在用这套『三问』」，在评论区预埋回答里写「苏禾在门店做搭配服务时常用这套思路」。夹具只登记了苏禾「长期接触门店陈列、顾客试穿和成套搭配」，从未登记「三问」是她的既有方法。**PP 自己在 `used_fact_refs` 里已经核对出这一点**——原文：「夹具原文写的是『长期接触门店陈列、顾客试穿和成套搭配』，没有写『常用三问』」——仍然写进了交付物。
- `frozen_target`：不编造；所有事实与发布主张必须可回指；推断不得冒充已发生事实。
- `confirmed_origin`：`SYSTEM_UNDER_TEST` = **PUBLISHING_PACKAGING 交付生成层**（app `c9cdea24-9df3-400b-9ecd-1d740e8c96df`，run `15e2643a-7710-47d0-a162-40b13726219d`）。
- `evidence`：
  - 违规文字在 `PP.raw_preserved`（PP 自己的原始模型输出）**首次出现**；在 `IN.capability_call` 与 `IN.professional_input` 中**零命中**。
  - 逐层计数：`一直在用这套三问` = raw_preserved 4 / PP.artifact 3 / PP.user_delivery 1 / SEAM 同值 / CANVAS.answer 1。
- **「标注为推断」不能合法化**：PP 在文案后加了脚注「『苏禾一直在用这套三问』是基于她搭配师工作职责的合理推断，不是已登记的事实陈述」。按 A2，加限定语是**非事件的变换**，不改变声明在阶梯上的位置；读者读到的正文仍然是一条关于真人的已发生事实。发布物的受众是顾客，不是审计员，脚注不随内容进入受众视野。
- `mutation_target`：PP 能力应用的交付生成层（本 Prompt **不授权**实施）。
- `protected_targets`：M1、M2、M3、Hop、Seam、统一画布投影层、其余五个能力应用——均无证据证明有错，不得修改。

---

## F2 · SYSTEM_UNDER_TEST — 已收到 NO_CTA，仍生成面向评论互动的表达

- `observed_failure`：PP 输入里逐字带有 `cta_contract: 不做购买、到店、私信或领取引导，只保留内容本身`。PP 仍然：
  1. 在发布文案结尾写「你自己买衣服前，会先问自己哪个问题？」——直接向受众索取评论动作；
  2. 整段输出「### 评论区设计（建议）」，含置顶首条与预埋问答脚本；
  3. 在 `cta_surface` 自述里写「**发布文案结尾问题为互动提问，属低风险互动范畴，不改变 NO_CTA 状态**」；
  4. 在交付正文里写「评论区全程没有引导关注、领取或到店动作，只有内容讨论和问题回应——这和这条**「不做购买引导」**的边界一致」。
- `frozen_target`：下游不得缩小上游 CTA 边界；「只保留内容本身」不得被改写成「可以引导评论但不引导购买」。
- `confirmed_origin`：`SYSTEM_UNDER_TEST` = **PUBLISHING_PACKAGING 交付生成层**（同一 run）。
- `evidence`：
  - PP 的合规自检表逐行只问「是否含购买引导」，把上游六项边界（购买／到店／私信／领取／**只保留内容本身**）压缩成一项。
  - 第 4 条把 `cta_contract` 原文改写成「不做购买引导」，是**下游缩小上游冻结边界**（A4：非承诺只读向下继承，任何形式都不得复活；A1：边界属有权者域，执行方不得在产出里改版）。
  - 第 3 条自造豁免类目「低风险互动范畴」——该类目不在任何冻结判据里。
  - 全部文字在 `PP.raw_preserved` 首次出现，PP 输入零命中。
- `mutation_target` / `protected_targets`：同 F1。

---

## F3 · CHECKER_OR_FIXTURE — V-08 报 `fabrication=[]` 且 PASS，而真实交付已出现 F1/F2

- `observed_failure`：`S4_CANONICAL_TASK_STATE_RESULT_v1.0.json` 的 V-08 = PASS，`fabrication = []`，`leaks = []`。
- `confirmed_origin`：`CHECKER_OR_FIXTURE`。当前 V-08 的判定面由两张表决定，**两张表都不覆盖 F1/F2**：
  - `fabrication_probes`（`S4_PHASE_C_POINT_VERIFICATION_FREEZE_v1.1.json`）只有七项：面料成分百分比、库存销量断言、SKU 货号、编造顾客口碑姓名、承诺预约时段、价格数字子集、人名白名单。**苏禾在白名单内**，「关于真实人物长期行为的主张是否可回指」完全不在覆盖面内。
  - `leak_forbidden_tokens` 与 `authorization_overclaim_tokens`（`S4_CONTENT_ORIGIN_CONTINUATION_GATE_v1.0.json`）合计 43 项，**没有任何一项与 CTA 语义相关**。「CTA 忠实」从未被真正检查过。
- 因此 V-08 的 PASS 是**探针未命中**，不是**证据支持的通过**。按 A2，token 未命中不是合法的上行事件。
- `mutation_target`：判定器的结论结构——V-08 拆分为 V-08A/V-08B/V-08C（本轮已执行，见 `S4_CANONICAL_STATE_ADJUDICATE_v1.1.py`）。
- `protected_targets`：v1.0 判定器、v1.0 结果文件、T1–T7 RAW、两份 Gate、COST_ACCOUNT——原样保留，一个字节不动。

---

## F4 · ORACLE_OR_CRITERION / EVIDENCE_BINDING — 判据与证据的绑定错位

复算结果见 `unified-app/stages/S4_CANONICAL_TASK_STATE_BINDING_RECONCILIATION_v1.0.json`。

| 编号 | 事实 | 判定 |
|---|---|---|
| BR-01 | Gate v1.1 的 `frozen_before_any_implementation_change: true` 与它自身 `supersedes.when`「Phase C **实现之后**、任何模型调用之前」直接冲突 | `CONTRADICTORY`。成立的只有 `frozen_before_any_model_run: true`；`frozen_before_any_implementation_change` 是 v1.0 的属性被复制到 v1.1，对 v1.1 不成立 |
| BR-02 | Candidate Manifest v1.0 的 `criteria_ref` 指向 Gate v1.0（`724aace1…`），而正式 T1–T7 的 `gate_sha256` 全部是 Gate v1.1（`a7986e47…`） | `MISMATCH`。Manifest 冻结于 Phase B（`git_head=1f5004c`），早于 v1.1，属时序事实；但引用结果时不得把两者当同一判据 |
| BR-03 | `S4_CANONICAL_STATE_VERIFY.json`（14/14）的 `criteria_ref` / `criteria_sha256` 指向 Gate v1.0 | `MISMATCH`。该 14/14 在 Gate v1.0 下成立，**不能**被引用成「Gate v1.1 下的 14/14」。本轮以 `S4_CANONICAL_STATE_VERIFY_v1.1.json` 重绑定后零模型重算 |
| BR-04 | `S4_CANONICAL_STATE_ADJUDICATE_v1.0.py` 的 V-07 展示行 `sorted(k for k, v in last.items() if v == "E")` 把字段字典与字符串比较，恒为 `[]` | `DISPLAY_ONLY`。不进入 PASS 谓词 `V(not bad_ref and not bad_kind and not ph)`，V-07 判定本身不受影响。v1.1 已纠正展示，判定谓词一字未改 |
| BR-05 | v1.0 的 V-08 用一个 PASS 同时代表五件事 | `OVERBROAD_SINGLE_VERDICT`。见 F3 |

---

## F5 · INSUFFICIENT_EVIDENCE — 跨轮纠正传播未被真实触发

```yaml
CROSS_TURN_CORRECTION_PROPAGATION: NOT_VERIFIED(NOT_CHECKED)
```

- 本轮真实发生两次纠正：T4 `facts.publish_permission`、T6 `production.profile`，两次 `stale_artifacts` 均为空。
- 空是**正确**的：T4 时账本里只有 T2 的 CB，其 12 个依赖字段不含 `facts.publish_permission`（该字段 T3 才登记）；T6 时账本里是 CB 与 CS，都不依赖 `production.profile`（该字段 T5 才登记）。按 A3「不多算」，不该置 STALE。
- 但这也意味着**「纠正 → 依赖 artifact 置 STALE」这条通路在真实链路上一次都没走到**。
- 离线单点变异证据（`S4_CANONICAL_STATE_VERIFY_v1.1.json`，MUT-06：`a["stale"] = True` → `False`）能翻掉 P-05，说明实现侧存在这条路径。**离线通过不能替代真实链路验证，本项不上调。**
- 要真验，需要一轮让用户修改一个**已被既有 artifact 依赖**的字段。这需要新的 Execution Prompt，本轮授权不含。

---

## 最高失效节点

```yaml
highest_confirmed_failing_node: PUBLISHING_PACKAGING delivery generation
app_id: c9cdea24-9df3-400b-9ecd-1d740e8c96df
run_id: 15e2643a-7710-47d0-a162-40b13726219d
```

**理由（可复算）**：F1/F2 的全部违规文字在 `PP.raw_preserved` 首次出现，在 PP 的两路输入中零命中；下游四层逐层哈希相等——
`PP.artifact == SEAM.artifact`、`PP.user_delivery == SEAM.user_delivery == CANVAS.final_text == CANVAS.answer`。
Seam 与统一画布是**纯透传**，没有新增一个字。按 A3「修复指向最高失效节点，不在下游打补丁」，**不得在统一画布投影层打补丁**。
