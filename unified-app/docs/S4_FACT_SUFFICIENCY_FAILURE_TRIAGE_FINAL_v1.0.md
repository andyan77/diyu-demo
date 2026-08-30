# S4 事实充分性链 · 第一失效节点定位与最终 FAILURE TRIAGE v1.0

`task_id: DIYU-V1-UNIFIED-DIFY-APPLICATION-001` ｜ Phase A ｜ 2026-08-29
上位 Prompt：`DIYU_V1_UAPP_FACT_SUFFICIENCY_ROOT_CAUSE_AND_MINIMAL_REPAIR_CONTINUE_EXECUTION_PROMPT_v1.0.md`
sha256 `5d4fcbe0d5e6915314e098dd41d251d61b58bc9575106dec7e42d8e1a97496f3`（激活时复算一致）

**本阶段模型调用 0，Dify 写入 0，被测图修改 0。** 全部结论由归档证据与只读图重算得出。
机器原文：`unified-app/evidence/stages/s4_fact_chain_root_cause/FACT_SUFFICIENCY_TRACE.json`
诊断器：`unified-app/workflows/S4_FACT_CHAIN_DIAGNOSE_v1.0.py`（判定规则 R1–R6 写在源码里，先于结果冻结）

---

## 0. PRODUCT_ALIGNMENT_CHECK

逐条回指现行 PRD 与核心合同，不另建对齐矩阵。§2.4 全部 9 份文件哈希复算一致。

| # | 产品语义 | 本轮结论 | 回指 |
|---|---|---|---|
| 1 | 用户只用自然语言、合法资料与有效历史产物，不填内部字段 | **不冲突**。修复只改系统内部字段在场的判定来源，用户侧输入形态一字不动 | 六轮话术均为自然语言，`S4_CONTENT_ORIGIN_CONTINUATION_INPUTS_v1.0.json` |
| 2 | M1 编译上下文、M2 给最小投影、M3 形成内容任务、M4/Seam 按需接入；不重建固定全链 | **不冲突**。修复落在 hop 适配器内部，不新增节点、不改路由、不改闸门 | `S4_BUILD_v1.0.py:60-89`；六轮 `C07` 路由 PASS 原样保留 |
| 3 | Content Brief 可接受 M3 等多种合法上游；不得因来源不同丢失来源、权限、作用域、时效、确认状态 | **本轮失败正是违反了这一条**：来源在场、作用域与性质标签齐备的事实，在外壳里被丢成不在场 | `CONTENT_BRIEF_CONTRACT_v0.1.md` §4「已登记事实、素材和资源快照」 |
| 4 | 「缺口」是可用性状态，不是信息性质；上传／抽取／登记／生成授权／发布授权必须分开 | **本轮失败违反了这一条**：`registered_facts` 已上传、已抽取、已登记、带 nature/scope 标签，却被报成「缺口」 | `V1_M0_SHARED_CONTRACT_TASK_CONTEXT_SNAPSHOT_v0.1.md` §47 可用性状态六值；PRD v0.3「下游真正必要的输入不得无声消失」 |
| 5 | 只追问真正阻塞当前分支的一项；不整任务无差别拒绝 | **不冲突**，且本轮失败使这一条无法成立：T3 一次抛出 7 项复合缺口 | `CLAUDE.md` §4；`S4-CO-T3` hop_gaps |
| 6 | Content Brief 不得重写 M3 已确认的主目标与受众问题；CS/PD/PP 不得反向改写上游、不得新增事实 | **不冲突**。修复不引入任何新事实，只把已在场的同一份字节据实标为在场 | `V1_M4_UNIFIED_CAPABILITY_CONTRACT_v0.1.md` §1.2 |
| 7 | `content_origin_mode` 属当前内容任务的制作决定，不是长期默认 | **不冲突**，本轮未触碰该字段语义 | `UAPP_FOUNDER_ADJUDICATION_002_CONTENT_ORIGIN_MODE.md` |
| 8 | 不得复活「Campaign 唯一上游、固定线性调用、普通生成逐段强制确认」 | **不冲突**。本轮不新增确认轮、不新增前置组件、不改调用顺序 | 上位合同已废止固定链 |

**决定性回指**：`V1_M4_UNIFIED_CAPABILITY_CONTRACT_v0.1.md` §1.2 硬禁第 2 条——

> **不得「缺字段即业务不足」**：充分性由 §4.3 的业务语义清单判定。外壳字段缺失只触发「这一项未提供」，不自动等于 `INSUFFICIENT`。

本轮观测到的正是「外壳字段缺失 ⇒ 直接 `INSUFFICIENT` ⇒ 空 artifact」。
**修复方向与已接受合同同向，不改变任何产品语义**，因此不归因 `CONTRACT_OR_INTENT`，不需要 Founder 产品裁决。

---

## 1. 两个 T2 的实际加载集合（Prompt §A2）

绑定的不是「同一轮的两份文件」，而是两条真实链上各自的 Content Brief 轮：

| | A：`attempt03_chain` conv `637ac1a6` turn 2 | B：`S4_CONTENT_ORIGIN_CONTINUATION` conv `b0d6d9f0` turn 2 |
|---|---|---|
| 证据文件 | `evidence/stages/S4-CAP-CONTENT_BRIEF-POS.json` | `evidence/stages/s4_continuation01/S4-CO-T2.json` |
| 用户原话 | 逐字节相同（`query_sha256` 相等） | 同左 |
| 夹具 | `8c21d41d…`，两侧相同 | 同左 |
| 候选图 | `f75555c0…`（46 节点／48 边） | 同左 |
| `uapp_ctx.registered_facts` | 2501 字，sha `9ccfd131…` | 2459 字，sha `d13e30d4…` |
| ctx → hop 是否原样送达 | **是**（两端 sha 相等） | **是**（两端 sha 相等） |
| `professional_input` 是否带 `[FACT]` 事实块 | **是**（5416 字） | **是**（4593 字） |
| hop 抽取出的 `facts_registered` | 非空 | **空** |
| hop 缺口 | 无 | `facts_registered` |
| Seam `precise_gap` | —（另有交付块标记问题，已 RECOVERED） | `facts_registered` |
| Content Brief artifact | **5593 字** | **0 字** |

**前一轮判定书「同一输入、同一份夹具，两次结论不同」这句不成立。** 两次 hop 的实际加载集合逐字段比对：
`registered_facts`（2501 vs 2459）、`m3_judgment`（2604 vs 1642）、`user_request`（155 vs 146）、
`account_context`（handle 与时间戳）四项均不同。夹具事实块本身逐行相同，差异只在末尾已登记用户原话行数。
**因此「Hop 已被证明自身不稳定」这一结论在证据上不成立，本轮不采用。**

不必依赖跨 attempt 比较——下一节给出**同一次运行、同一条会话内**的直接证据。

---

## 2. 六字段来源矩阵与第一失效点（Prompt §A3／§A4）

判定规则先于结果冻结（`S4_FACT_CHAIN_DIAGNOSE_v1.0.py` 源码 R1–R6）：
六字段中只有 `facts_registered` 有 1:1 的确定性来源绑定（`uapp_ctx.registered_facts`），
其余五项来自 M3 判断正文与用户原话等自然语言，确定性侧无法独立断言在场，缺失只记 `INCONCLUSIVE`。

### 2.1 单条会话内的抹除（不需要跨 attempt 比较）

`S4_CONTENT_ORIGIN_CONTINUATION` 一条会话六轮，确定性来源**每轮都在场**：

| 轮 | `uapp_ctx.registered_facts` | 外壳 `facts_registered` | 判定 |
|---|---|---|---|
| T1 | 2367 字 | 在场 | `NONE` |
| T2 | 2459 字 | **空** | **`SOURCE_PRESENT_BUT_ERASED`** |
| T3 | 2459 字 | **空** | **`SOURCE_PRESENT_BUT_ERASED`** |
| T4 | 2541 字 | 在场 | `NONE` |
| T5 | 2541 字 | 在场 | `NONE` |
| T6 | 2541 字 | 在场 | `NONE` |

同一条会话、同一张图、同一份夹具、来源单调增长且始终非空，外壳字段的在场判定却四次在场、两次不在场。
**这不是「有没有事实」的问题，是「谁来判断事实在不在」的问题。**

### 2.2 抹除发生在哪一跳

```text
uapp_ctx（code，确定性拼装）
  registered_facts = 上传资料原文 + M1 已登记证据条目（带 nature/scope 标签）
  ⇒ 2459 字，非空                                              ✅ 在场
        │  sha 相等，原样送达
        ▼
uapp_hop（tool → app 6c46fdb1）
  ├─ m5_extract（LLM deepseek-v4-flash，reasoning_effort=low）
  │     ⇒ fields.facts_registered = ""                          ❌ 在这里变成不在场
  └─ m5_compose（code）
        ├─ professional_input ← registered_facts 原样照带（同一份字节）  ✅ 仍在场
        └─ gaps / capability_call ← **只读 m5_extract 的输出**            ❌ 判定为缺口
        ▼
uapp_seam → CONTENT_BRIEF（最终 FP）
  收到的外壳没有 facts_registered ⇒ INPUT_SUFFICIENCY 停止 ⇒ artifact 0
```

**同一个 `m5_compose` 函数，在同一次执行里，把同一份 `registered_facts` 既原样写进
`professional_input`，又判定它「不在场」。** 这是一个函数内部的自相矛盾，不需要任何跨轮或跨 attempt 推断。

### 2.3 第一失效节点

```yaml
first_divergence_observed_at: "uapp_hop / app 6c46fdb1 / m5_extract 的输出（fields.facts_registered 由非空来源变成空串）"
highest_failing_node: "uapp_hop / app 6c46fdb1 / m5_compose（code）"
why_not_m5_extract: >-
  m5_extract 是 LLM，它按自己的 system prompt「宁可留空也不要猜」行事；
  要求一个模型对某个字段永不漏抽，不是可保证的性质，改它的 prompt 属于对症状打统计补丁。
  架构缺陷在于：「事实在不在场」这件确定性、可来源绑定的事，被整条委托给了模型。
  该判定的所有权在 m5_compose——它同时持有确定性参数 registered_facts 与缺口计算。
  按 A3「修复最高失效节点，不在下游打补丁」，修复对象是 m5_compose。
why_not_downstream: >-
  CONTENT_BRIEF 与 SEAM 都是最终 FP 应用，它们对一个已经缺项的外壳作出停止是**正确行为**；
  在它们身上改判定等于降低充分性闸门，被本 Prompt Phase B 明令禁止。
```

### 2.4 同链放大器（Prompt §A4 指定检查，**不冒充根因**）

`uapp_save` 是**无条件** assigner：每轮把 `uapp_seam_merge.artifact` 写进 `conversation.uapp_last_artifact`，
能力停在缺口返回空 artifact 时同样写入，于是**用空串覆盖上一轮已确认的有效产物**。

实测确证（`attempt03_chain` conv `637ac1a6`，非推断）：

```text
turn 2  CONTENT_BRIEF      artifact 5593 字  → uapp_save 写入          ✅
turn 3  CREATIVE_SCRIPT    hop.IN.upstream_delivery = 5593（读到了）
                           停在 content_origin_mode 缺口 → artifact 0
                           → uapp_save 用 "" 覆盖                      ❌ 5593 字产物就此消失
turn 4  PRODUCTION_DIRECTOR hop.IN.upstream_delivery = 0
turn 5  PUBLISHING_PACKAGING hop.IN.upstream_delivery = 0
```

定位：`unified-app/workflows/S4_BUILD_v1.0.py:143-148`（统一 Canvas 内，非最终 FP 应用）。

**这不是 T2 首次失败的根因**——T2 的失败发生在它之前，与它无关。
但它是同一条链上的独立缺陷，且**由构造决定**了本 Prompt Phase C 冻结的窄链
（Content Brief → CS 精确询问 → Founder 回答 → CS → PD → PP）**不可能通过**：
CS 的询问轮必然把已完成的 Content Brief 抹掉。因此它属于「使窄链能被一次有效测试真正覆盖」
所必需的**最小连通修改集**，不是顺手扩大范围。

---

## 3. FAILURE TRIAGE

```yaml
observed_failure: >-
  S4_CONTENT_ORIGIN_CONTINUATION 的 T2：Content Brief 真跑且 succeeded，但 artifact 长度 0，
  Seam 返回 precise_gap=facts_registered；T3–T6 因此逐层拿不到上游产物，C01–C06 全部 FAIL。

frozen_target: >-
  S4_CONTENT_ORIGIN_CONTINUATION_GATE_v1.0.json（01405ebf…），12 项条件，冻结并提交于任何调用之前；
  本轮一字未改，历史 FAIL 不追溯改绿。

candidate_sources_evaluated:
  CONTRACT_OR_INTENT: RULED_OUT
    evidence: >-
      修复方向与已接受合同同向而非相悖。M4 统一能力合同 §1.2 硬禁第 2 条明令「不得缺字段即业务不足」；
      Content Brief 合同 §4 把「已登记事实、素材和资源快照」列为标准输入（快照，不是模型摘要）；
      M0 任务上下文合同 §47 把可用性状态定义为六值枚举而非模型判断。
      当前行为违反的是这三条已接受的合同，不需要改变任何产品语义。
  ORACLE_OR_CRITERION: RULED_OUT
    evidence: >-
      判据 commit cea08c9 冻结于调用之前；C01「产生非空 artifact」出自上游 Prompt 原文，
      不是执行侧新增；本轮未修改任何历史判据。
  CHECKER_OR_FIXTURE: RULED_OUT_FOR_THIS_FAILURE
    evidence: >-
      夹具 sha256 8c21d41d… 六轮相同；registered_facts 由 uapp_ctx 到 uapp_hop 两端 sha 相等，
      逐轮原样送达（trace.deterministic_inputs.carried_intact_ctx_to_hop = true）；
      裁定结论 100% 由确定性节点记录得出。
      已知的 TD-UAPP-17（precise_gap 复合串未按全角分号切分）只影响 C02 观测栏的显示，
      即使完美切分 C02 仍因缺口远多于一项而 FAIL——不改变任何一条判定。
  INPUT_ENVIRONMENT_OR_TOOL: RULED_OUT
    evidence: >-
      确定性来源在 hop 输入端六轮全部在场且非空（2367/2459/2459/2541/2541/2541），
      并原样进入 professional_input。输入没有缺失，工具链没有丢数据。
  INSUFFICIENT_EVIDENCE: NO_LONGER_APPLICABLE
    evidence: >-
      前一轮归此类，是因为当时只有跨 attempt 的两次对照，且那两次输入实际并不相同。
      本轮改用同一次运行、同一条会话内的节点前后对照：同一 m5_compose 执行中，
      同一份 registered_facts 既被原样写入 professional_input，又被判定为缺口。
      该矛盾在单次运行内可复算，不依赖任何重复采样。
  SYSTEM_UNDER_TEST: CONFIRMED

confirmed_origin: SYSTEM_UNDER_TEST

first_divergence: >-
  uapp_hop（nested app 6c46fdb1「DIYU M5 TEST CANDIDATE · 跨能力接缝适配器」）内部，
  m5_extract 输出 fields.facts_registered = "" 时首次由「来源明确且可用」变为「缺失」；
  由 m5_compose 定案为 extraction_gap 并从 capability_call 外壳中略去。

evidence_refs:
  - unified-app/evidence/stages/s4_fact_chain_root_cause/FACT_SUFFICIENCY_TRACE.json
  - unified-app/evidence/stages/s4_continuation01/S4-CO-T1..T6.json
  - unified-app/evidence/stages/S4-CAP-CONTENT_BRIEF-POS.json（conv 637ac1a6 turn 2，artifact 5593）
  - unified-app/evidence/stages/S4-CAP-CREATIVE_SCRIPT-POS.json（conv 637ac1a6 turn 3，覆盖发生处）
  - hop 应用只读图：graph_sha256 969f211a…，m5_compose 代码 sha256 f444166c…，
    m5_extract prompt sha256 1215796e…（模型 deepseek-v4-flash，reasoning_effort=low）
  - 诊断器正负控制 12/12 PASS（含「来源为空时不得误报抹除」「跨会话不得配对」两条防伪负控制）

mutation_target:
  - "app 6c46fdb1 的 m5_compose 代码节点：为 facts_registered 建立确定性下限——
     当自身参数 registered_facts 非空而抽取器留空时，按来源绑定据实标为在场，
     source_map 记 DERIVED(registered_facts)。不引入任何新事实，用的就是同一函数已在
     professional_input 里原样照带的同一份字节。"
  - "统一 Canvas S4_BUILD_v1.0.py:143-148 的 uapp_save：空 artifact 不得覆盖已有非空产物。"

protected_targets:
  - "最终 FP 应用：M3 a4c3b19b、SEAM 5fca0162、MATRIX fd25ebfa、CAMPAIGN 1f9d65ea、
     CONTENT_BRIEF b1dcf784、CREATIVE_SCRIPT 44b55f9d、PRODUCTION_DIRECTOR 13cfabd5、
     PUBLISHING_PACKAGING c9cdea24 —— 一律不改。"
  - "旧 Canvas 2448e4f9 与旧 provider 2daa2d27。"
  - "全部历史判据、历史证据、历史 FAIL 与既有裁定书。"
  - "m5_extract 的 system prompt、模型与参数（不改 prompt 求统计好转）。"
  - "S4_CONTINUATION_ADJUDICATE_v1.0.py 与既有判定结果（TD-UAPP-17 只在新诊断器内修正）。"

next_reverification:
  - "Phase B 单元/结构：抹除下限的正例、来源真空的负例、复合 gap 切分、空 artifact 不误覆盖、
     保护面零漂移、无案例专用字符串、无专业语义复制。"
  - "Phase B 离线集成：用保存的真实载荷重放 M1/M2 → M3 → Hop → Seam → Brief gate，
     证明 facts_registered 按来源保留，且来源真空时仍精确停止。"
  - "Phase C 点对点：受影响模块 → 相邻接缝 → 原窄链，各一次冻结输入、一次正式尝试。"
```

---

## 4. Phase A 硬门判定

```text
confirmed_origin = SYSTEM_UNDER_TEST
失效点归属      = 任务专属薄适配授权面（不是受保护的最终 FP 应用）
```

归属依据（三处独立命名证据，非执行侧解释）：

1. 数据库应用名：`DIYU M5 TEST CANDIDATE · 跨能力接缝适配器（能力感知抽取）`
   ——其余八个能力应用与 M3、SEAM 一律为 `DIYU M5 FP ·` 前缀。
2. provider 标签（`UAPP_CREATE_PROVIDERS_v1.0.py:19-27`）：hop 为
   `DIYU V1 UAPP · 跨能力抽取适配 hop v0.2`；M3 与 SEAM 为 `（最终 FP）`。
3. 外壳自报来源：`source_ref: m5_hop_adapter_v0.2`。

第二个修改对象 `uapp_save` 位于统一 Canvas 自身，归属无争议。

**结论：进入 Phase B。** 一次最小连通修改集，零模型调用，机器验证；
Phase B 全绿并完成冻结之前不发起任何 Dify/DeepSeek 模型调用。

需要向规划侧披露的一点：上一轮的 `S4_CONTENT_ORIGIN_CONTINUATION_GATE_v1.0.json`
把 HOP 列入 `protected_apps_zero_drift`，那是**上一轮授权范围**（该轮 `graph_mutation: FORBIDDEN`）
的记录，不是产品层的永久保护声明；本 Prompt Phase B 明确授权「任务专属薄适配授权面」上的一次最小修复。
若规划侧认为 hop 应按最终 FP 保护，本工作包应即刻退回 CHECKPOINT，本节结论随之失效。

---

## 5. 技术债后继登记

```text
TD-UAPP-18 = FACT_SUFFICIENCY_CHAIN_INCONSISTENCY
  前身（历史假设，保留不改）：Hop 抽取判定不稳定
  本轮 confirmed_origin：SYSTEM_UNDER_TEST（不再是 INSUFFICIENT_EVIDENCE）
  精确表述：hop 适配器把「事实是否在场」这一确定性、可来源绑定的判定整条委托给抽取模型，
            缺少确定性下限；同一函数内 professional_input 与 gaps 对同一份字节给出相反结论。

TD-UAPP-19 = EMPTY_ARTIFACT_OVERWRITES_CONFIRMED_UPSTREAM（新增）
  uapp_save 无条件写入，缺口轮的空 artifact 覆盖上一轮已确认产物；
  实测：conv 637ac1a6 turn 3 抹掉 turn 2 的 5593 字 Content Brief。
  归属：统一 Canvas；本轮 Phase B 一并修复（窄链可测性的必要条件）。

TD-UAPP-17（既有）：判定器 gaps() 未按全角分号切分 precise_gap。
  本轮在新诊断器 S4_FACT_CHAIN_DIAGNOSE_v1.0.py 内已修正并有负控制；
  历史裁定器与历史结果一字未动。
```

---

## 6. 表达边界更正（Prompt §0 要求）

- `C07` 证明的是回答被路由回正确能力。`C03` 已 FAIL，**不得声称「同一任务语义完整延续」**。
- `C08` 的历史 `PASS` 原样保留，但**不能单独证明语义连续性**：T2 的 Content Brief 根本没完成，
  「没有重做 Brief」在这种情况下是空通过。
- 本轮**不采用**「Hop 已被证明自身不稳定」这一结论——支撑它的输入同一性前提经复算不成立。

`END_MARKER: S4-FACT-SUFFICIENCY-FAILURE-TRIAGE-FINAL-v1.0-END`
