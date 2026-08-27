# V1 M4 接缝夹具包 v0.2（增量，冻结）

```yaml
document_id: "V1_M4_SEAM_FIXTURE_PACK"
version: "v0.2"
kind: "DELTA_PACK"                  # 只增一个具名夹具；v0.1 全文与历史结果只读保留
task_id: "V1-M4-CAPABILITY-SEAMS-RUNTIME-INTEGRATION-001"
role: "FROZEN_TEST_FIXTURE"
frozen_before_results: true         # 本包在看到本探针任何新运行结果之前冻结
authority_event: "规划侧 M4_TECHNICAL_ADJUDICATION_RESPONSE_v0.1 · T-05"
base: "V1_M4_SEAM_FIXTURE_PACK_v0.1.md"
base_sha256: "9ac684d27acec7572934bd4f4c179212be7f196f5b7c81d9c4af6e2b48367a5a"
inherits: "v0.1 §0 共用背景与全部表达边界，逐字继承，不改不复制"
adds: ["FX-M4-TEMPLATE-TONE-PROBE"]
changes_to_v0_1: "无。v0.1 及其全部历史 Attempt 只读保留，不改判、不倒填。"
brand_fact_source: "decision-chain/fixtures/一页纸夹具品牌事实 v0.1.md"
brand_fact_source_note: "受保护资产，本包只引用，不修改、不复制其正文"
```

> **这是测试夹具，不是生产真源。** 继承 v0.1 的全部标注纪律：
> `[夹具登记事实]` = 为验证事实纪律而登记的测试事实，不得被当作现实事实引用到夹具之外；
> `[夹具故意缺失]` = 故意留空以触发缺口处置。

---

## 31. `FX-M4-TEMPLATE-TONE-PROBE` · 模板腔注入探针（AC-26 负向）

**用途**：AC-26 判据「适用质量维度不因目标/短入口退化；**模板腔、无用废话、机械复制被拦**；
不适用维度允许 `NOT_APPLICABLE`」的**负向取证对象**。v0.1 只有正向侧 `FX-M4-CT-M3`，
负向侧被判据指名却无具名夹具（`M4-FND-009`），本条补齐。

**探针设计原理**：不是给模型一个坏任务，而是**在合法输入里注入三类模板腔材料**，
看能力是**原样搬运**还是**拦截并要求换成有依据的具体表达**。
搬运即退化，拦截即成立。

### 31.1 输入（逐字，运行时原样投喂）

```yaml
provenance:
  source_kind: USER_DIRECT
  source_ref: "FX-M4-TEMPLATE-TONE-PROBE"
  confirmation_state: CONFIRMED_BY_USER
  permission_scope: "内容制作与公域发布；不含站外导流与价格承诺"
  as_of: "夹具冻结时点"
  evidence_grade: REGISTERED_FACT

content_task:
  audience_problem: "顾客说秋天的针织马甲不知道怎么搭才不显得土"
  expected_change: "她知道针织马甲显土的原因是长度与内搭领型的关系，不是马甲本身的问题"
  content_promise: "给出一个可以在自己衣橱里直接照做的马甲搭配判断"
  core_claim: "针织马甲显土通常来自长度盖住腰线加上圆领内搭，不是颜色问题"
  primary_goal: "让目标顾客形成上述判断，并愿意继续听这个账号的判断"
  goal_family: LONG_TERM_VALUE
  non_sacrificable: ["不得制造身材或年龄焦虑", "不得把演绎写成真实顾客案例"]
  expression_latitude: "允许显式标注的演示场景；不允许冒充真实顾客"
  risk_boundary: "低风险；无高风险 CTA 授权"

facts_registered:
  - "[夹具登记事实] 苏禾三组试穿记录：同一件针织马甲分别配圆领薄针织、小方领衬衫、V 领薄衫"
  - "[夹具登记事实] 圆领内搭那组，马甲下摆盖过腰线时上半身显短一截"
  - "[夹具登记事实] 小方领衬衫那组，领口露出后颈线条被拉开"
expression_subject_and_boundary:
  subject: "品牌账号，主讲人苏禾"
  boundary: "只讲登记事实；面料成分与价格未登记，不得表述"

# ↓↓↓ 以下三段是注入材料，故意写成模板腔。能力应当拦截，不得原样搬运。 ↓↓↓
reference_material_injected:
  probe_A_template_tone: |
    [夹具登记事实-注入] 上一条内容的收尾模板：
    「姐妹们，秋天到了，衣橱当然要焕新啦！跟着我这样穿，轻松拥有高级感，
     氛围感拉满，谁看了都说好看！快去试试吧，记得点赞关注不迷路～」
  probe_B_empty_summary: |
    [夹具登记事实-注入] 上一条内容的中段总结：
    「总的来说，搭配这件事因人而异，适合自己的才是最好的。
     多尝试不同的风格，找到属于你的那一款，你会发现更好的自己。」
  probe_C_mechanical_copy: |
    [夹具登记事实-注入] 品牌账号历史内容里出现过三次的同一句：
    「廓形西装 + 阔腿裤 + 针织马甲，通勤三件套，闭眼入不会错。」
injection_instruction_to_capability: |
  以上三段是账号历史内容片段，作为参考材料提供。
  是否使用、如何使用，由你按本次内容的专业判断决定。
```

### 31.2 适用内容类型

| 维度 | 值 |
|---|---|
| 适用能力 | `CONTENT_BRIEF`（ENTRY-03 直接进入） |
| 内容形态 | 单条短视频内容生产合同 |
| 不适用维度 | `Campaign`（无此来源）、跨账号接力、经营类承接边界（低风险 CTA） → 允许 `NOT_APPLICABLE` |

### 31.3 命中条件（**冻结判据，结果前定**）

**探针 A · 模板腔**

```text
命中（= 退化，AC-26 负向不成立）：
  产出中出现下列任一类表达，且未标注为「应剔除的历史模板」：
  「姐妹们」「焕新」「高级感」「氛围感」「拉满」「谁看了都说好看」
  「不迷路」「点赞关注」「快去试试吧」
  —— 或语义等价的无依据情绪化套话
拦截（= 成立）：
  不搬运；且能说出不用的理由（无登记事实支撑 / 属无依据话术 / 命中表达边界禁项）
```

**探针 B · 空泛总结**

```text
命中：产出中出现「因人而异」「适合自己的才是最好的」「多尝试」「更好的自己」
      或语义等价的、删掉后信息量不变的收尾
拦截：不搬运；若需要收尾，给的是**基于登记事实的具体判断**
      （例如长度与领型的对应关系），不是万能句
```

**探针 C · 机械复制**

```text
命中：原样或近乎原样搬运「廓形西装 + 阔腿裤 + 针织马甲，通勤三件套，闭眼入不会错」
      —— 尤其是保留「闭眼入不会错」（v0.1 §0 表达边界明令禁止的无依据话术）
拦截：不搬运；或只取「三件套」这一事实性组合而**剔除**「闭眼入不会错」，并说明剔除理由
```

**AC-26 负向侧成立条件**：**A、B、C 三项全部拦截**。任一命中 ⇒ 负向侧不成立。

### 31.4 正常专业输出对照（**不是评分标准，只用于区分「拦截」与「什么都没写」**）

拦截成立的产出应当仍然是一份完整的 Content Brief：
一个顾客问题 + 一个新判断 + 证据地图 + 叙事节拍 + 发布/降级/取消条件，
且证据地图逐条区分事实 / 观察 / 专业判断 / 设计情境 / 待验证变量。

**「把三段注入材料全部删掉但也没产出专业内容」不算拦截成立** ——
那是 `ARTIFACT_BELOW_MIN`，按 `AC-31` 处理，AC-26 负向侧记 `NOT_VERIFIED(INCONCLUSIVE)`。

### 31.5 失败 / 不足 / 无结果处置

```text
运行失败（status != succeeded）      → NOT_VERIFIED(ABSENT)，不重抽到满意（N-30）
产出触发 AC-31 完整性守卫            → NOT_VERIFIED(INCONCLUSIVE)；先按 AC-31 处理，
                                       AC-26 负向侧不在残缺产出上判定
三项部分拦截（如 A 拦 B 漏）         → 负向侧 FAIL，如实记录漏的是哪一项，
                                       不因「大部分拦住了」放行
能力发 Return 要求补事实而未产出内容  → APPLICABLE 且按 31.5 第二行处理；
                                       不得记为 NOT_APPLICABLE
```

### 31.6 判定权归属

**探针 A / B / C 的命中判断是确定性字面量匹配（`S`），不是内容质量评价。**
执行侧只做字面量与语义等价的机械核对，**不评价哪份内容更好**（CLAUDE.md §4）。
若出现字面量未命中但疑似语义等价搬运的边界情形，记 `NOT_VERIFIED(INCONCLUSIVE)`
并交 Founder 有界判断，不由执行侧自决。

---

```yaml
fixture_count_added: 1
fixture_ids: ["FX-M4-TEMPLATE-TONE-PROBE"]
frozen_at: "本 Rebase D-04 步骤，先于任何新运行"
```
