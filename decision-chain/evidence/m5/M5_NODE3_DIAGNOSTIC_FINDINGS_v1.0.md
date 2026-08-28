# M5 Node 3 诊断发现 · v1.0

> **证据等级：DIAGNOSTIC。** 这些运行发生在 Candidate Run Manifest 冻结**之前**，
> 按 Root Prompt Node 3.8 一律只作诊断，**不产生任何正式 PASS/FAIL**。
> 记录时间（UTC）：`2026-08-28T05:34:36Z`

## M5-DIAG-001 · 完整主故事当前不成立，最高失效节点已定位

**现象（可复现，非偶发）**

用 M4 Founder Canvas 作自然语言入口（advanced-chat，`f0b1c5f5`），三轮真实对话：

| 轮次 | 输入要点 | Canvas 回答 | 底层运行 |
|---|---|---|---|
| 1 | 完整经营诉求，**明确写了目标**「验证这个角度能不能打中人，先不追求到店或成交」 | 「任务我已经记下了」+ 让用户选能力 | Canvas run `4b98104b` |
| 2 | 「就做内容 Brief。」 | 「我还差一样东西…**这一轮你想拿到的结果是什么？**」 | Canvas run `4e3a8d0f` |
| 3 | **再次明确给出目标** | 「已按你说的目标来…**内容 Brief 现在开始做，做完后会给你确认**」 | Canvas `64e13072` → Seam `3b259648` → Content Brief Architect `e38c97da` |

**第 3 轮 Seam 运行 `3b259648` 的真实输出：**

```text
business_delivery_outcome = UNKNOWN
artifact                  = 0 字（空）
user_delivery             = 110 字，内容是「我还差一样东西…这一轮你想拿到的结果是什么？」
capabilities_skipped      = [MATRIX, CAMPAIGN, CREATIVE_SCRIPT, PRODUCTION_DIRECTOR, PUBLISHING_PACKAGING]
platform status           = succeeded
```

**两个独立缺陷**

**D-1 目标事实抽取召回不足（对应已登记风险 `RISK-M4-033`）。**
用户在第 1 轮与第 3 轮**两次**明确陈述本轮目标，能力侧仍报「缺目标」。
说明 Canvas 的意图层没有把已陈述的目标带进 `capability_call` / `professional_input`。

**D-2 用户可见层宣称的进度，与业务层结论相矛盾（新发现，比 D-1 严重）。**
同一时刻：业务真相是 `business_delivery_outcome = UNKNOWN`、`artifact` 为空、
能力侧正在回问缺失项；而 Canvas 对用户说的是「已按你说的目标来」「内容 Brief 现在开始做」。
这直接违反 M4 交接契约里被列为 **M5 必须遵守**的语义：

> 读业务结果看 `business_delivery_outcome`，不要拿平台 status 当交付成功。

平台 status 确实是 `succeeded`，但业务没有交付。用户被告知「在做了」，实际什么都没产出。
这不是措辞问题：它会让 Founder 以为拿到了 Brief，而系统其实停在回问。

**影响面**

- `M5-AC-02`（扩展完整主故事）：**当前不成立**。故事在 Content Brief 这一步就断了，
  后面的 Creative Script / Production Director / Publishing & Packaging 全部 `capabilities_skipped`。
- `M5-AC-03`（合法短入口）：`DE-05` Direct Content Brief 受同一根因影响，标 `STALE` 待复验。
- `RISK-M4-033`：诊断阶段已观察到复现证据。
- `RISK-M4-032`（内部状态泄漏）：**未**观察到泄漏；D-2 是反向问题——不是泄漏内部状态，
  而是对外宣称了业务层不支持的进度。

**最高失效节点**

Canvas 意图层 → `capability_call` 组装环节。不是 Content Brief Architect 本身：
该能力在收到形状正确的输入时工作正常——同一 Seam、同一能力，用 M4 冻结夹具
`FX-M4-CT-M3` 调用返回 `business_delivery_outcome = DELIVERED`、
`user_delivery` 2449 字的完整 Content Brief Pack（诊断运行 `175a3329`）。
**所以能力侧是好的，坏的是上游把业务实质组装成统一能力外壳这一步。**

**修复边界**

M4 的八个已发布应用受合同保护：`overwrite_or_delete_existing_m1_m4_apps = PROHIBITED`。
因此**不改** `f0b1c5f5` 等既有应用，改法只能是按
`create_or_update_task_named_m5_test_candidate = AUTHORIZED_REVERSIBLE`
另建 M5 测试候选对象，在候选里修组装环节。

## M5-DIAG-002 · M1 编译器不能脱离 Dify 影子节点单独驱动

`m1_context_compiler_v0.1.py::main()` 传 `shadow_patch={}` 时返回
`patch_ok=false`、`reject_reason=SHADOW_NODE_FAILED`。
该 Python 文件只是**确定性校验与合并器**，自然语言理解由 Dify 图里的 LLM 影子节点完成。
因此 M5 的完整故事必须以 Canvas 为自然语言入口，不能用 Python 直接编排 M1 绕过它。
（这不是缺陷，是架构事实，登记以免后续误用。）

## M5-DIAG-003 · 已成立的部分（同轮诊断中确实跑通的）

以下在同一诊断里真实成立，构成后续正式运行的基础：

- **M2 服务可用且与候选同源**：容器内应用代码哈希 `b6cd1688…` 与 M5 候选树逐字节一致。
- **反馈幂等成立**：同一 `idempotency_key` 连写两次，返回同一行
  `6dab42dc-29d5-4a8a-902c-ab0c290207c7`，未制造双份事实。
- **测试发布身份正确**：`is_test = true`、`is_simulated = true` 显式写入，
  未被伪装成真实发布。
- **Cycle N+1 成立**：`M2_cycle_next` 与 `M2_cycle_decision` 均 200，
  决策绑定 `resulting_cycle_id`，且 `based_on` 记录了反馈为测试模拟。
- **M3 两次真实运行**：`a5cc38dc`（周期判断，`gate_status=CLEAN`，1275 字）与
  `378ffd5c`（复盘，`gate_status=CLEAN`，822 字）。
- **能力可合法跳过**：MATRIX / CAMPAIGN 未被暗跑，`capabilities_skipped` 如实记录。
- **一次只进一个能力**：Seam 每次调用只落一个能力应用，六能力之间零调用边。

## 下一动作

按 Root Prompt Node 3.7「只修集成所需的最高失效节点」，在 M5 测试候选对象中修复
Canvas 意图层 → `capability_call` 的组装；既有 M4/M3 应用零改动。
修复后重跑完整主故事，仍属诊断；正式运行一律等 Candidate Run Manifest 冻结之后。

---

## M5-DIAG-004 · 根因已精确定位：外壳形状不匹配（确定性可复现）

前面把最高失效节点定位到 Canvas 的 `m4_intent_adapter`。现在根因是确定的，不是推测。

**能力侧的判据（`Content Brief Architect` 的 `envelope_check` 节点，确定性代码）**

```python
REQUIRED = ["objective", "audience_problem", "expected_change",
            "content_promise", "facts_registered", "expression_subject_and_boundary"]
```

`_find_scalar` 只认三种写法：`"key": "字符串"`、YAML 行 `key: value`、`` `key`: value ``；
`_present` 另外认 YAML 块（`key:` 独占一行 + 缩进块）。

**Canvas 适配器实际发出的东西（`m4_intent_adapter` 节点）**

```python
envelope = {..., "objective": {"primary_goal": task_goal, "goal_family": "UNDECLARED"}, ...}
capability_call = json.dumps(envelope, ensure_ascii=False, indent=2)
```

即**嵌套 JSON**，且 `objective` 的值是对象不是字符串。

**离线复算判定（把两种形状分别喂给 `envelope_check` 的同一套正则）**

| 输入形状 | `missing` | 判定 |
|---|---|---|
| Canvas 适配器当前输出（嵌套 JSON） | `objective, audience_problem, expected_change, content_promise, facts_registered, expression_subject_and_boundary` —— **六项全缺** | `INSUFFICIENT` |
| M4 冻结夹具 `FX-M4-CT-M3` 的扁平 YAML | 无 | `SUFFICIENT` |

**注意 `objective` 也在缺失名单里。** 适配器确实填了它，但解析器看不见带引号的键 + 对象值，
所以连唯一被填的那个字段也没被识别。

**由此推出的三个连带事实**

1. 经 Canvas 发起的能力调用，`goal_family` 恒为 `UNDECLARED`、`platform` 恒为 `NOT_LOCKED`、
   `cta_level` 恒为 `NO_CTA` —— 不是业务上没声明，是**解析器从来没看见过**。
   这三项随后驱动 `conditionalized`，于是产出被无声降级。
2. D-1 表现为「只问目标」，是因为组件级 Return 一次只问一个问题（M4 的 `single_question` 语义）；
   实际缺的是六项。**D-1 不是抽取召回不足，是外壳形状不匹配** —— 前一版判断在此更正。
   `RISK-M4-033` 是否独立成立，需在修好形状后重新观察，当前证据**不足以**判定它成立。
3. M4 交接映射记的是 `e2e_reached_capability_seam: true` —— **到达接缝**，不是交付成功；
   其 smoke 输出正是本次同一句回问。M4 把它归因为「首轮先走自然对话，属设计行为」。
   设计行为的部分成立，但**形状不匹配这一层此前未被发现**：在当前形状下，
   Canvas 无论对话多少轮都不可能让能力交付，因为缺的六项永远不会以可识别的形状出现。

**为什么 M4 自己的验收没抓到**：M4 的正式运行（`DIYU_M4_FORMAL_ATTEMPT`）是把扁平夹具
**直接注入 Seam**，绕过了 Canvas 适配器。被测的是 Seam→能力这一段，适配器那一段没有被覆盖。
这不是 M4 造假，是覆盖缺口：M5 是第一个真正端到端跑 Canvas 的。

**修复方向（最小、且不碰受保护资产）**

在 M5 测试候选里，把 `m4_intent_adapter` 的输出从嵌套 JSON 改为**扁平外壳**，
并把业务实质从 M1 快照投影到 `REQUIRED` 的六个键上。
投影不新造语义：复用 `m1_context_compiler_v0.1.py::project_content_task()` 已声明的映射，
取不到的字段如实留空并计入 `projection_gaps`，**不代为推断、不编造**。

M4 的八个已发布应用零改动（`overwrite_or_delete_existing_m1_m4_apps = PROHIBITED`）。

---

## M5-DIAG-005 · 修复成立：完整链路首次真正交付（诊断）

记录时间（UTC）：`2026-08-28T05:58:53Z`

**做法**：按 Founder 裁定「M5 候选加抽取适配」，新建 M5 测试候选应用
`DIYU M5 TEST CANDIDATE · M3 判断 → 统一能力外壳（抽取适配）`，
`app_id = e1013ce2-69c5-44c1-ad83-26534f3c5e4c`，published `marked_name = m5-adapter-v0.1`。
M4 八个已发布应用、M3 已发布应用、六份 Skill 源文件**零改动**。

**链路与结果**

```text
M3 真实运行判断（run a5cc38dc，1275 字散文）
  → M5 抽取适配（扁平外壳，抽取耗时随模型）
  → Capability Seam（CONTENT_BRIEF）
  → Content Brief Architect
  → business_delivery_outcome = DELIVERED
    run_id 00e428b5-8869-4619-b497-d12243238a58，57.84s，user_delivery 677 字
```

对照修复前同一条链路：`business_delivery_outcome = UNKNOWN`、`artifact` 空、六项必填全缺。

**抽取忠实性（本次实测，非声明）**

抽到的五项都能在 M3 判断原文里逐句回指：

| 字段 | 抽取值 | 是否原文已有 |
|---|---|---|
| `audience_problem` | 门店试穿反馈里最常问的是肩宽和通勤场景 | 是 |
| `expected_change` | 从「担心显壮」变成「想进一步了解版型和尺码」，并愿意在评论区说出自己的肩宽和困惑 | 是 |
| `content_promise` | 这是真实试穿记录，不是模特图 | 是 |
| `facts_registered` | 苏禾手上有三组真实试穿记录；门店试穿反馈… | 是 |
| `explicit_non_promise` | 不承诺所有肩宽都不显壮（只有三组记录），不虚构价格、库存、优惠 | 是 |

`goal_family` 抽取为空并计入 `extraction_gaps` —— M3 判断确实没声明目标族，
适配器**没有代为推断**。这正是要求的行为。
`expression_subject_and_boundary` 只抽到「苏禾」没抽到边界，因为「不制造身材焦虑」
出现在用户对 Canvas 的原话里、不在 M3 判断正文里 —— 如实反映，不跨源补全。

**下游产出的质量特征（对 AC-02 与多个风险探针有直接意义）**

Content Brief 的 `user_delivery` 表现出下列行为，均可回指：

- **不编造**：明确「不报价格、不碰库存、不提优惠」——与夹具未提供这些事实一致。
- **目标忠实（F-10 方向）**：坚持「验证方向」而非改写成到店/成交，与 M3 判断一致。
- **主动让掉已被让掉的东西**：明确不回答「能不能上班穿到接孩子」，理由是本轮 M3
  已把该场景机会让掉 —— 取舍结论穿过三个组件没有走样。
- **CTA 不越权**：停在 `LOW_RISK_INTERACTION`，明确「不引导咨询、到店或购买
  （本轮没有确认承接路径）」。
- **缺口如实上报**：要求补「三组试穿记录细节」与「锁定发布平台」，不假装已有。
- **给出不发布条件**：记录无法公开或数据撑不起真实呈现就取消。

**状态更新**

- `M5-AC-02` 的 Content Brief 这一段：诊断阶段**已跑通**；正式结论仍待
  Candidate Run Manifest 冻结后重跑。
- 缺口 B（Brief §3.2 仍要求 Campaign 决策包）**未消除也未涂绿**：本次是用
  `source_kind: M3_OPERATION` 通过能力侧的**确定性外壳校验**，没有把
  `upstream_kind` 改标成 `campaign`。下游消费测试 9 条仍全过，
  冻结断言「五条里恰好一条 ABSENT」保持不变。

---

## M5-DIAG-006 · 六个能力的必填清单互不相同，一份写死的清单接不完整条链（诊断）

**怎么发现的**：v0.1 适配器只覆盖 `M3 → Content Brief` 一跳，必填清单被写死成
Content Brief 的六项。把链路往下延伸时，后三个能力全部在 `外壳校验` 处返回
`INPUT_INSUFFICIENT`。

**现场读出的事实**（直接读四个能力**已发布** graph 的 `外壳校验` 节点源码，未经改写）：

| 能力 | `REQUIRED` |
|---|---|
| MATRIX | applicability_reason / subject_and_account_scope / objective / facts_registered / expression_boundary |
| CAMPAIGN | objective / deadline_or_stage_boundary / audience_problem / facts_registered / capacity_or_owner |
| CONTENT_BRIEF | objective / audience_problem / expected_change / content_promise / facts_registered / expression_subject_and_boundary |
| CREATIVE_SCRIPT | objective / expected_change / content_promise / **expression_subject** / **content_origin_mode** / facts_registered |
| PRODUCTION_DIRECTOR | **script_or_equivalent_beats** / content_origin_mode / **production_profile** / **time_window** / content_promise |
| PUBLISHING_PACKAGING | **content_body_or_beats** / content_promise / **explicit_non_promise** / facts_registered / **cta_contract** / **asset_publish_permission** |

**这不是 M4 的缺陷。** M4 冻结的正是「六个能力之间零调用边」；谁把上一跳的产出接成
下一跳的外壳，M4 没有规定也不该由 M4 规定——那是 M5「统一集成」要补的接缝。

后三个能力要的字段（产能班底、时间窗口、出镜与引用授权）**在 M3 的运营判断里没有
也不该有**：它们是资源事实，不是运营判断。真源是已登记事实夹具。因此完整主故事
必须把夹具作为可加载参考真正送进链路，而不是由运行脚本代抄。

**处置**：新建 M5 测试候选应用「跨能力接缝适配器（能力感知抽取）」
`6c46fdb1-5f49-4513-a0c0-29957b3dcee4`，按 `target_capability` 各自的必填清单，
从四类已登记来源（M3 判断 / 上游能力已交付产出 / 已登记事实夹具 / 用户原话与账号投影）
抽取。每个字段必须报出来自哪一个来源，不得跨源拼接。

---

## M5-DIAG-007 · M4 外壳解析器对含引号的值存在硬门假阴性（真实缺陷）

**症状**：`FULL-01` 第一跳，适配器自报只缺 1 项，Content Brief 却报缺 4 项：
`audience_problem, expected_change, facts_registered, expression_subject_and_boundary`。
其中前三项**确实写在外壳里**，能力侧却看不见。

**根因**（`外壳校验` 节点 `_find_scalar` 的第二条正则，原文）：

```python
r"^\s*%s\s*:\s*[\"']?([^\"'\n]+)[\"']?\s*$" % re.escape(key)
```

捕获组 `[^\"'\n]+` **不允许值里出现 ASCII 引号**。而 M3 的运营判断大量使用
`'看着差不多、上身差很多'`、`'人人可穿'` 这类引用。一旦值里出现一个 `'` 或 `"`，
正则在第一个引号处截断、随后 `\s*$` 失败、且因字符类排除引号而无法回溯，整行判为不在场。

**影响面**：任何一条合法 YAML 写法的外壳，只要值里引用了一句话，该字段就对能力侧隐形。
后果不是产出变差，而是**硬门给出假阴性**——能力侧回头向用户索要一份用户已经给过的东西。
六个能力共用同一份 `_find_scalar`，因此六个能力全部受影响。

**为什么不改 M4**：M4 八个已发布应用属受保护面，本任务无授权改动。

**M5 侧处置（不改 M4 一个字）**：改用 M4 解析器**自己就接受**的第三种形状
`` `key`: value ``，其正则为 `` r"`%s`\s*[:：]\s*([^\n]+)" ``，捕获组 `([^\n]+)`
接受任意字符。值一个字都不改写，引号原样保留，能力侧能读到。

**离线复算**（直接 `exec` 能力侧已发布源码，未改一字）：用本次实跑抽到的**原值**
（含 ASCII 引号）重算——YAML 平铺形状 → `INSUFFICIENT`，缺 3 项；
反引号形状 → `SUFFICIENT`，`missing = 无`，`goal_family = MIXED`，
`cta_level = LOW_RISK_INTERACTION`。

**反向控制（防涂绿）**：逐项删除必填字段后重算，11/11 全部仍判 `INSUFFICIENT`
且 `missing` 精确命中被删项。适配器没有替能力侧放松闸门，只是让在场的字段可被看见。

**登记为待 Founder 裁定的 M4 遗留缺陷**：本任务只在 M5 接缝侧绕开，**没有修复 M4**。
任何未来直接用 YAML 平铺写法调用这六个能力的调用方，都会再次踩中。

---

## M5-DIAG-008 · 唯一一条允许的合成规则

抽取器在不同跳上对 `expression_subject` 的召回不一致：Publishing 那跳从夹具抽到了，
Content Brief 那跳没抽到，导致复合字段 `expression_subject_and_boundary` 缺失。

处置：**只在两个部件都已从已登记来源抽到时**，把 `expression_subject` 与
`expression_boundary` 拼成复合字段，并在 `source_map` 里标为
`DERIVED(expression_subject+expression_boundary)`。任一部件缺失一律不合成，照旧计入缺口。

这是格式化不是编造：没有引入任何新事实，且合成事实可审计。
复合字段的定义本身就是「出镜者＋表达边界」。
