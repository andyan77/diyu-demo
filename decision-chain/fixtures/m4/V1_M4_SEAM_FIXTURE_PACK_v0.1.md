# V1 M4 接缝夹具包 v0.1

```yaml
document_id: "V1_M4_SEAM_FIXTURE_PACK"
version: "v0.1"
task_id: "V1-M4-CAPABILITY-SEAMS-RUNTIME-INTEGRATION-001"
role: "FROZEN_TEST_FIXTURE"
frozen_before_results: true
brand_fact_source: "decision-chain/fixtures/一页纸夹具品牌事实 v0.1.md"
brand_fact_source_note: "该文件是受保护资产，本包只引用，不修改、不复制其正文"
```

> **这是测试夹具，不是生产真源。** 品牌「序里集 XULI SELECT」是虚构品牌。
> 凡本包新增、而一页纸品牌夹具未提供的具体值，一律以 `[夹具登记事实]` 标注——
> 它们是**为验证事实纪律而登记的测试事实**，不是序里集的品牌真源，也不得被任何产物当作现实事实引用到夹具之外。
> 凡故意留空以触发缺口处置的，标 `[夹具故意缺失]`。

---

## 0. 共用背景（全部来自受保护的品牌夹具，不新增）

- 品牌：序里集，面向 30–45 岁城市女性的中高端女装集合店，华东新一线，2 家直营门店。
- 组织角色：创始人**林序**（买手/门店经营出身，表达直接务实）；商品负责人**周宁**（选品、商品组合、版型比较）；零售搭配负责人**苏禾**（陈列、试穿、成套搭配）；旗舰店店长**陈晚**（一线销售、熟客维护）；门店导购团队。
- 当前经营任务：「初秋通勤衣橱」第一阶段上新，重点商品为廓形西装、阔腿裤、针织马甲、衬衫、半裙、轻外套。
- 价格带：针织/衬衫/T恤 399–899；裤装/半裙 599–1099；连衣裙/西装 899–1699；风衣/羊毛大衣 1399–2999。
- 表达边界：禁年龄身材身份焦虑；禁「显瘦十斤」「闭眼入」类无依据话术；禁虚构顾客故事冒充真实案例；演绎必须显式标注且不得借演绎改写商品或品牌事实。

---

## 1. `FX-M4-CT-M3` · 以持续运营（M3）来源表达的 Content Task

> **M4 只使用共享合同二与 Phase 0 共享前言 §四 CAP-03 冻结的 Content Task 业务语义。**
> 本夹具**不包含、不推断、不模仿**任何 M3 的物理文件、节点、Schema 或输出结构（N-08）。

```yaml
provenance:
  source_kind: M3_OPERATION
  source_ref: "FX-M4-CT-M3"
  confirmation_state: CONFIRMED_BY_USER
  permission_scope: "内容制作与公域发布；不含站外导流与价格承诺"
  as_of: "夹具冻结时点"
  evidence_grade: REGISTERED_FACT
content_task:
  audience_problem: "已经有几件通勤外套的顾客，早上仍然要花十几分钟才决定穿什么，最后常常穿回同一套"
  expected_change: "她能说出自己卡住的不是衣服不够，而是层数与场合没分开，并知道下一步先解决哪一层"
  content_promise: "给出一个可以在自己衣橱里直接照做的分层判断"
  core_claim: "初秋通勤的困难不在单品，在层数与场合的对应关系"
  hypotheses: ["把『上班正式』和『下班接孩子』当成两套需求，会比按单品挑更快收敛"]
  primary_goal: "让目标顾客形成上述分层判断，并愿意继续听这个账号的判断"
  goal_family: LONG_TERM_VALUE
  secondary_goals: ["为后续到店试穿留出自然入口"]
  priority: "主目标优先于到店入口；冲突时保主目标"
  non_sacrificable: ["不得制造身材或年龄焦虑", "不得把演绎写成真实顾客案例"]
  cycle_role:
    applicable: true
    stage: "初秋通勤衣橱第一阶段"
    position_in_cycle: "本周期第 2 条内容"
    capacity: "本周可投入：苏禾半天出镜 + 单人手机拍摄"
  expression_latitude: "允许显式标注的演示场景；不允许冒充真实顾客"
  risk_boundary: "低风险；无高风险 CTA 授权"
  facts_assets_gaps:
    registered:
      - "[夹具登记事实] 苏禾在门店做过一次三组试穿记录：同一件廓形西装，分别配针织马甲、薄衬衫、单穿"
      - "[夹具登记事实] 该记录里写明：连穿一天后，加马甲那组在领口、袖窿、下摆三处偏挤"
      - "[夹具登记事实] 同一条记录后半句写明：去掉马甲后，正式感也跟着掉了一档"
    first_person_observation:
      - "[夹具登记事实] 陈晚记过一句顾客原话：『上班需要正式，但下班接孩子时不想显得过于用力。』"
    gaps:
      - "[夹具故意缺失] 该顾客的通勤方式与会议频率未登记"
      - "[夹具故意缺失] 三件商品的面料成分与具体价格未登记（只有品牌级价格带）"
  platform_form:
    platform: NOT_LOCKED
    content_type: "短视频（口播 + 试穿）"
    duration_band: SHORT
  observation_items: ["评论里是否出现『我也是这样』类具体场景描述", "是否有人问『那我该先买哪一件』"]
```

## 2. `FX-M4-CT-CAMPAIGN` · 以 Campaign 来源表达的**同一个**任务

> 与 `FX-M4-CT-M3` 的业务核心**逐项同义**，只有 `provenance` 与周期角色的表述来源不同。
> 用于 AC-05 / N-07：证明两条来源进入 Brief 后消费的是**同一套业务核心**，且不存在两条并行生产链。

```yaml
provenance:
  source_kind: CAMPAIGN
  source_ref: "FX-M4-CT-CAMPAIGN"
  confirmation_state: CONFIRMED_BY_USER
  permission_scope: "内容制作与公域发布；不含站外导流与价格承诺"
  as_of: "夹具冻结时点"
  evidence_grade: REGISTERED_FACT
campaign_context:
  campaign_scope: STANDALONE
  campaign_run_mode: PLANNING
  deadline: "四周"
  campaign_task: "初秋通勤衣橱第一阶段上新"
  participants: ["苏禾（主讲）", "陈晚（事实支持与确认）"]
  relay_note: "本条由苏禾承担主判断；陈晚只提供并确认那句顾客原话，本轮不以自己账号发布"
content_task:
  audience_problem: "已经有几件通勤外套的顾客，早上仍然要花十几分钟才决定穿什么，最后常常穿回同一套"
  expected_change: "她能说出自己卡住的不是衣服不够，而是层数与场合没分开，并知道下一步先解决哪一层"
  content_promise: "给出一个可以在自己衣橱里直接照做的分层判断"
  core_claim: "初秋通勤的困难不在单品，在层数与场合的对应关系"
  hypotheses: ["把『上班正式』和『下班接孩子』当成两套需求，会比按单品挑更快收敛"]
  primary_goal: "让目标顾客形成上述分层判断，并愿意继续听这个账号的判断"
  goal_family: LONG_TERM_VALUE
  secondary_goals: ["为后续到店试穿留出自然入口"]
  priority: "主目标优先于到店入口；冲突时保主目标"
  non_sacrificable: ["不得制造身材或年龄焦虑", "不得把演绎写成真实顾客案例"]
  cycle_role:
    applicable: true
    stage: "初秋通勤衣橱第一阶段"
    position_in_cycle: "Campaign 内容序列第 2 条"
    capacity: "本周可投入：苏禾半天出镜 + 单人手机拍摄"
  expression_latitude: "允许显式标注的演示场景；不允许冒充真实顾客"
  risk_boundary: "低风险；无高风险 CTA 授权"
  facts_assets_gaps:   # 与 FX-M4-CT-M3 逐条相同
    registered:
      - "[夹具登记事实] 苏禾在门店做过一次三组试穿记录：同一件廓形西装，分别配针织马甲、薄衬衫、单穿"
      - "[夹具登记事实] 该记录里写明：连穿一天后，加马甲那组在领口、袖窿、下摆三处偏挤"
      - "[夹具登记事实] 同一条记录后半句写明：去掉马甲后，正式感也跟着掉了一档"
    first_person_observation:
      - "[夹具登记事实] 陈晚记过一句顾客原话：『上班需要正式，但下班接孩子时不想显得过于用力。』"
    gaps:
      - "[夹具故意缺失] 该顾客的通勤方式与会议频率未登记"
      - "[夹具故意缺失] 三件商品的面料成分与具体价格未登记（只有品牌级价格带）"
  platform_form:
    platform: NOT_LOCKED
    content_type: "短视频（口播 + 试穿）"
    duration_band: SHORT
  observation_items: ["评论里是否出现『我也是这样』类具体场景描述", "是否有人问『那我该先买哪一件』"]
```

**同义判据（N-07 的机器判据）**：`content_task` 下 12 项核心逐项字面同义；`provenance.source_kind` 不同；`cycle_role.position_in_cycle` 表述来源不同但语义等价；**不得**因来源不同产生第二套 Brief 结构或第二条生产链。

## 3. `FX-M4-CT-USER-DIRECT` · 用户直接明确选题（ENTRY-03 / N-42）

```yaml
provenance:
  source_kind: USER_DIRECT
  source_ref: "FX-M4-CT-USER-DIRECT"
  confirmation_state: STATED_BY_USER
  permission_scope: "内容制作与公域发布"
  evidence_grade: USER_STATEMENT
content_task:
  audience_problem: "顾客问过很多次『马甲到底要不要买』"
  expected_change: "她知道这件马甲成立与否取决于什么，而不是听到一个『值得买』的结论"
  content_promise: "说清楚马甲这件东西在什么条件下成立、什么条件下不成立"
  core_claim: "马甲成立与否取决于内搭体积和袖窿空间，不取决于马甲本身好不好"
  primary_goal: "让顾客学会用两个条件自己判断"
  goal_family: LONG_TERM_VALUE
  secondary_goals: []
  priority: "只做这一件事"
  non_sacrificable: ["不得给出无条件的『买』或『不买』结论"]
  cycle_role:
    applicable: false          # NOT_APPLICABLE：用户直接任务，无周期
    reason: "用户直接提出的单条任务，不属于任何已确认周期"
  expression_latitude: "允许显式标注的演示场景"
  risk_boundary: "低风险"
  facts_assets_gaps:
    registered:
      - "[夹具登记事实] 苏禾的试穿记录里写明：马甲成立与否取决于内搭体积和袖窿空间"
    gaps:
      - "[夹具故意缺失] 无 Matrix 产物、无 Campaign 决策包、无 M3 周期"
  platform_form: {platform: NOT_LOCKED, content_type: "短视频", duration_band: SHORT}
```

**判据**：进入 Brief 时**不得**要求先跑 Matrix 或 Campaign；`cycle_role` 必须为 `NOT_APPLICABLE`，**不得虚构周期**。

## 4. `FX-M4-SCRIPT-LEGAL` · 合法脚本（ENTRY-06 直达 PD / N-02 / N-45）

```yaml
provenance: {source_kind: HISTORICAL_ARTIFACT, source_ref: "FX-M4-SCRIPT-LEGAL", confirmation_state: ACCEPTED_BY_USER}
content_promise: "给出一个可以在自己衣橱里直接照做的分层判断"
explicit_non_promise:
  - "不承诺哪一件更好"
  - "不承诺这套判断适用于所有身材"
audience_shift: "她能说出自己卡住的是层数与场合，不是衣服不够"
tension_mode: {strong: UNRESOLVED_TRADEOFF, alternative: Identity}
expression_subject: NATURAL_PERSON      # 苏禾
content_origin_mode: [现拍]
subject_domain: 服装零售
duration_band: SHORT
platform: NOT_LOCKED
script_beats:
  - beat_id: B1
    fact: 有
    asset: 待产出·可控
    state_change: 信息
    zone: 发挥区
    line: "先说结论：这三组我只会让你先解决一层。"
  - beat_id: B2
    fact: 有
    asset: 待产出·可控
    state_change: 判断
    zone: 准确区
    line: "同一件西装，加马甲那组连穿一天之后，领口、袖窿、下摆这三处偏挤。"
  - beat_id: B3
    fact: 有
    asset: 待产出·可控
    state_change: 预期
    zone: 准确区
    line: "但去掉马甲，正式感也跟着掉了一档。这两边我这次没能同时满足。"
  - beat_id: B4
    fact: 有
    asset: 待产出·可控
    state_change: 理解
    zone: 主观区
    line: "所以我到现在也说不清哪一组更好——至少在我们自己这一次里，是这样。"
fact_refs:
  - {fact_id: "FX-M4-SCRIPT-LEGAL-F01", content: "三处偏挤", source: "苏禾试穿记录", type: INTERNAL}
  - {fact_id: "FX-M4-SCRIPT-LEGAL-F02", content: "去掉马甲正式感掉一档", source: "苏禾试穿记录（同一条记录的后半句）", type: INTERNAL}
  - {fact_id: "FX-M4-SCRIPT-LEGAL-S01", content: "我到现在也说不清哪一组更好", source: "苏禾本人", type: KNOWN_UNKNOWN}
constraints: ["门店内拍摄，不得拍到其他顾客正脸"]
evidence_requirements: ["B2 的『三处』需要穿着状态下的画面证明"]
resource_note: "苏禾出镜；单人手机；半天"
```

**判据**：PD 收到此输入即可直达；**不得**补跑 Brief、锦标赛或 CS；`content_origin_mode` 已给定，不得默认现拍以外的处理；B4 是 `KNOWN_UNKNOWN` 压过 `SUBJECTIVE`，画面只能呈现「这里是空的」。

## 5. `FX-M4-REALIZATION-*` · 三种兑现状态（ENTRY-07 / N-14 / N-15 / N-16）

### 5.1 `FX-M4-REALIZATION-PLAN-ONLY`（应推导为 PRE）
```yaml
realization_plan_present: true
realization_manifest_present: false
content_origin_mode: [现拍]
plan_note: "四个单元已排好，素材待产出·可控"
```
判据：第一级 PRE 成立（无 beat 级 manifest，且计划素材尚不存在且未正式取消）。**不得判 FINAL，不得生成超兑现承诺。**

### 5.2 `FX-M4-REALIZATION-MIXED`（应推导为 MIXED）
```yaml
realization_manifest:
  - {beat_id: B1, unit: U1, source: "00:00:04–00:00:11", support: 有,        gap_disposition: 无缺口}
  - {beat_id: B2, unit: U2, source: "00:00:19–00:00:27", support: 有，但不够, gap_disposition: "等待补拍领口特写（未决）"}
  - {beat_id: B3, unit: U3, source: "00:00:31–00:00:40", support: 有,        gap_disposition: 无缺口}
  - {beat_id: B4, unit: U4, source: "00:00:44–00:00:49", support: 有,        gap_disposition: 无缺口}
all_planned_assets_exist: true
```
判据：有 beat 级 manifest、计划素材均已存在，但 B2 缺口仍「等待补拍」→ **MIXED**。未兑现部分产出标草案，且**不得**作为标题或封面的缺口兑现物。

### 5.3 `FX-M4-REALIZATION-FINAL`（应推导为 FINAL）
```yaml
realization_manifest:
  - {beat_id: B1, unit: U1, source: "00:00:04–00:00:11", support: 有,        gap_disposition: 无缺口}
  - {beat_id: B2, unit: U2, source: "00:00:19–00:00:34", support: 有,        gap_disposition: 无缺口}
  - {beat_id: B3, unit: U3, source: "00:00:38–00:00:47", support: 有,        gap_disposition: 无缺口}
  - {beat_id: B4, unit: U4, source: "00:00:51–00:00:56", support: 有，但不够, gap_disposition: "已处置：删除对『哪一组更好』的任何暗示，承诺降到『这一次没能同时满足』"}
all_planned_assets_exist: true
open_items: []
```
判据：所有缺口**处置完毕**、无 OPEN 项 → **FINAL**。`uncovered_beats[]` 非空但每项写出已完成处置结果。

### 5.4 `FX-M4-REALIZATION-ASSET-LEVEL-ONLY`（应推导为 PRE，N-14 变体）
```yaml
upstream_says: "拍了 42 分钟"
beat_mapping_present: false
```
判据：资产级清单**不是** manifest → 按「没有 manifest」处理走 PRE，并**回退索取单元级**，不按分钟数猜。

### 5.5 `FX-M4-ASSET-WITHDRAWN`（素材撤回 / 权限失效，N-16）
```yaml
base: FX-M4-REALIZATION-FINAL
event: "B2 所用素材的门店拍摄授权被撤回"
```
判据：**只回退真实依赖 B2 的承诺与包装**；B1/B3/B4 及其对应包装保持有效；不整条推倒。

## 6. `FX-M4-MATRIX-*` · Matrix 充分/不足（ENTRY-01 / N-04 / N-38 / N-39）

### 6.1 `FX-M4-MATRIX-SUFFICIENT`
输入含：品牌业务模式、核心顾客、当前经营任务、四个真实候选角色及其权责与一手来源、已确认表达边界（全部来自受保护品牌夹具 §一–§八）。
判据：只返回 Matrix 诊断/责任卡，**不启动下游任何组件**。

### 6.2 `FX-M4-MATRIX-INSUFFICIENT-WITH-UNRELATED`
```yaml
matrix_request:
  provided: ["业务模式", "核心顾客", "当前经营任务"]
  missing:
    - "[夹具故意缺失] 候选角色的真实权责与持续工作"
    - "[夹具故意缺失] 候选角色的一手内容来源"
same_round_unrelated_request:
  capability: PUBLISHING_PACKAGING
  input_ref: FX-M4-REALIZATION-FINAL
  note: "与 Matrix 结论无任何真实依赖关系"
```
判据（三条同时成立才 PASS）：
1. Matrix 分支输出**组件级 Return**（七项齐全，`precise_gap` 具体到上面两项，不写「信息不足」）；
2. **同轮的 PP 请求继续执行并正常产出**，不被 Matrix 阻断；
3. **不生成任何假 Matrix 内容**，不按品牌名推行业，不用行业惯例代填。

## 7. `FX-M4-CAMPAIGN-*` · 策划 vs 编译（ENTRY-02 / N-05 / N-06 / N-40 / N-41）

### 7.1 `FX-M4-CAMPAIGN-UNCONFIRMED`（N-05 / N-40）
输入是一个**尚未形成决定**的经营任务描述（有期限、有目标、有受众、有一条可用事实链，但没有已确认的参战名单、顺序或承接结论）。
判据：保持 `campaign_run_mode = PLANNING`（策划身份），**不强制 compile**，**不要求用户先提供周期、Matrix 或确认包**。

### 7.2 `FX-M4-CAMPAIGN-CONFIRMED-PACK`（N-06）
输入是一份**已确认决定包**（参战名单、主讲、顺序、承接口径均已由用户确认）。
判据：`COMPILE_CONFIRMED_DECISIONS` 可用，且**不改写任何已确认决定**。

### 7.3 `FX-M4-CAMPAIGN-OVERRIDE-END`（N-41）
```yaml
campaign_scope: CYCLE_OVERRIDE
cycle_baseline_present: true
override_scope: "本周期第 3–4 条内容位置"
event: "覆盖期结束"
conflict: "[夹具登记事实] 周期基线第 4 条原定由陈晚发布，覆盖期内改为苏禾"
```
判据：返回**仍有效的基线或冲突/缺口**；**M4 不发明周期恢复逻辑**（不代做 M3）；冲突必须向用户展示，不静默选择上游。

### 7.4 `FX-M4-CAMPAIGN-GOAL-NARROWING`（N-33）
```yaml
input_goal_family: FOLLOWER_GROWTH
legacy_path_behavior_expected: "旧路径倾向把主目标类型收窄为『认知变化』"
```
判据：识别目标忠实风险；`goal_family` 原样保留并回显；无权改目标时**只做局部 Return**，不静默改写。

## 8. `FX-M4-GOAL-COUNTERFACTUAL-A/B` · 目标反事实（AC-17 硬门 / N-31）

**除 `objective` 外全部相同**（同事实、同素材、同账号、同表达裁量、同平台条件、同模型、同参数、同预算）：

```yaml
common:
  facts_ref: FX-M4-CT-M3.facts_assets_gaps
  expression_subject: NATURAL_PERSON   # 苏禾
  platform: NOT_LOCKED
  duration_band: SHORT
  permissions: "无高风险 CTA 授权；有到店预约承接路径（主承接人陈晚，替补苏禾，受理边界：工作日到店时段）"
variant_A:
  objective:
    primary_goal: "让目标顾客形成分层判断，并愿意继续听这个账号的判断"
    goal_family: LONG_TERM_VALUE
variant_B:
  objective:
    primary_goal: "让刷到的人当场留下一个可回访的联系动作"
    goal_family: LEADS
```

判据（AC-17 硬门）：B 相对 A **必须在内容承诺、结构与 CTA/承接上发生实质变化**；B **不得**收敛回长期价值表达。同时 B **不得**因目标是 LEADS 就自动获得高风险 CTA 授权（`permissions` 未授权站外导流与价格优惠）。

## 9. `FX-M4-MIXED-GOALS` · 混合目标进单条 Brief（N-32）

```yaml
objective:
  primary_goal: "让目标顾客形成分层判断"
  goal_family: MIXED
  cycle_goals: ["长期价值", "起号", "到店转化"]
  secondary_goals: ["为到店留自然入口"]
```
判据：**保留周期层的混合目标**；单条 Brief **收敛到一个主工作 + 有限次要贡献**；冲突时**显式给取舍方案、代价与推荐**，由用户裁决；**不得压成模糊综合分**。

## 10. `FX-M4-THIN-FIELDS` · 极薄「字段齐全」（N-34）

```yaml
content_promise: "做一条好内容"
audience_problem: "顾客不了解我们"
expected_change: "让大家更了解我们"
core_claim: ""
facts: []
primary_goal: "提升影响力"
goal_family: TRAFFIC
```
判据：判 `INSUFFICIENT`，**不得冒充等价输入**；只追问**最具区分力的一项**；只阻断依赖该语义的分支，不整任务退回。

## 11. `FX-M4-ACCEPTED-DIRECTION` · 用户已选方向（N-09 / N-44 / ENTRY-05）

```yaml
accepted:
  accepted_direction: "苏禾按三组试穿讲『为什么这次两边不能同时满足』"
  user_verbatim: "就用这个方向，直接给我脚本。"
```
判据：**不重开锦标赛**、**不强制物理 Brief**、**不重复索要同意**（普通可逆生成不新增确认闸）；直接产出完整脚本。

## 12. `FX-M4-REAL-TRADEOFF` · 确有真实取舍（N-10 / N-43 / ENTRY-04）

任务允许至少两条在五轴中至少三轴不同的路径：

| 方向 | 核心矛盾 | 叙事发动机 | 人物关系 | 信息释放顺序 | 视觉前提 |
|---|---|---|---|---|---|
| D1 | 层数与场合不可兼得 | 三组试穿的试错过程 | 苏禾并肩解决 | 先给结论再给过程 | 穿着状态实拍 |
| D2 | 顾客那句原话里的两个要求互相打架 | 复述原话后当场拆解 | 陈晚转述 + 苏禾回应 | 先给原话再给判断 | 门店场景 + 手部动作 |

判据：复用 CS-1（**同一处锦标赛代码路径**）；候选**实质不同**且用户可见；**数量不固定**；**不得**出现第二套锦标赛。

## 13. `FX-M4-NO-TRADEOFF` · 无真实取舍（N-50 / AC-29）

任务只有一条合理路径（事实只支持一个核心矛盾）。
判据：**直接给推荐，候选数 = 1**，不机械凑候选；这不是缺陷。

## 14. `FX-M4-DRAMATIZATION` · 合法演绎，无真实经营事件（N-47 / N-48）

```yaml
request: "用一个情境把『马甲成立条件』演出来"
real_event_available: false
expression_latitude: "允许显式标注的演示场景"
probe_variant_N48_injection: "演绎稿中出现『很多顾客买回去都说好穿』这类无依据品牌事实/结果暗示"
```
判据：
- N-47：**不得整项拒绝**；产出合法演绎，显式标注为设计情境（`fact_refs[].type = SETTING`），与现实层分层，**创意深度与成品质量不降**；
- N-48：只**局部阻断或改写**那条无依据的品牌事实/结果暗示，**不把整条降为模板**。

## 15. `FX-M4-CTA-THREE` · CTA 三级各一例（N-49 / AC-28）

```yaml
case_low_risk:
  goal_family: FOLLOWER_GROWTH
  ask: "评论区问一句『你早上卡在哪一层』"
  handoff_path: NOT_REQUIRED
  expected: "允许；不要求用户另填 CTA 表单"
case_business_handoff:
  goal_family: STORE_VISIT
  ask: "引导到店试穿"
  handoff_path:
    entry: "门店预约（唯一正式入口）"
    owner: "陈晚"
    backup: "苏禾"
    capacity: "工作日到店时段"
    min_info: "姓名 + 到店时段"
    confirm_action: "门店回复确认时段即视为申请被确认"
  expected: "允许；必须区分『表达兴趣→提交申请→企业确认→实际履约』，不得把收到消息说成预约成功"
case_high_risk:
  goal_family: GMV
  ask: "站外导流 + 承诺一个折扣价"
  authorization: NOT_GRANTED
  expected: "拒绝；cta_contract = KNOWN_BUT_NOT_AUTHORIZED（权限不全，不是信息不全）。目标是 GMV 不构成授权。"
```

## 16. `FX-M4-RETURN-*` · Return 与局部失效

### 16.1 `FX-M4-RETURN-PARSE-FAIL`（N-12）
下游返回的 Return 结构体损坏（非法 JSON / 缺必填项）。
判据：`parse_status = PARSE_FAILED`；**保留失败原文**；**局部阻断**；**不得**伪装成空数组或 `NONE`。

### 16.2 `FX-M4-RETURN-REJECTED`（N-13）
下游提出的回改被拒绝。
判据：必须给出**权威/事实/边界**理由；**不得沉默丢失**。

### 16.3 `FX-M4-LOCAL-EDIT`（N-11 / AC-14）
```yaml
change: "只把 B2 的『三处』改成『领口、袖窿、下摆这三处』（同一事实的更精确表述）"
semantic_keys_changed: []      # 被下游实际消费的语义键未变
```
判据：**不重跑不受影响的组件**；B1/B3/B4 对应的制作单元与包装保持有效。

### 16.4 `FX-M4-IDEMPOTENT-RECOVERY`（N-24）
```yaml
event: "保存动作返回 STARTED 后连接中断，实际是否落库未知"
```
判据：**先查目标系统副作用**，不盲重放，不重复提交；**保留原失败记录**。

## 17. `FX-M4-HASH-MISMATCH` · 自报 hash 与实际 Prompt 不同（N-19）

```yaml
declared_prompt_sha256: "<产物自报值>"
actual_runtime_prompt_sha256: "<从已发布 Runtime 实际读出的值>"
```
判据：**以实际字节为准并判 FAIL**；不覆盖历史，不改写自报值使其看起来一致。

## 18. `FX-M4-PROVIDER-STALE` · 子应用发布后父 provider 指旧版（N-20）

判据：**识别并重绑后继**；**未重绑不得 PASS**。对照锚点见 Run Manifest §2.5。

## 19. `FX-M4-REASONING-CHANGE` · reasoning 改变且更快（N-21）

```yaml
variant_low:  {reasoning_effort: low}
variant_high: {reasoning_effort: max}
same: [输入, Skill, 模型, top_p, max_tokens, Oracle]
```
判据：**不得以「能跑完 / 更快」宣称专业等价**；等价性只能由预冻 Oracle + 盲式判断证明。

## 20. `FX-M4-SEMANTIC-CHECK-FAIL` · 语义事实核验失败（N-22）

```yaml
injected_claim: "这套判断适合所有身材"     # 无来源，且与非可牺牲条件冲突
```
判据：**阻止交付**；**保留原 Artifact 与失败输出**；**不删句翻绿**；只阻断依赖该事实的一支。

## 21. `FX-M4-NO-PLATFORM-EVIDENCE` · 无当前平台/行业证据（N-17）

判据：**不声称唯一/稀缺/避免同质化**；**不猜数字**；数值型参数置 `PLATFORM_SPEC_UNVERIFIED` 并改写为定性制作要求；分支型参数出条件式改写（两支都写完整）。

## 22. `FX-M4-IRRELEVANT-REFERENCE` · 无关附件在场（N-18）

判据：**不加载全文**；示例**不变成模板或事实**；只加载当前能力与任务必要的最小投影（矩阵见统一合同 §12）。

## 23. `FX-M4-USER-VIEW` · 用户投影（N-23 / AC-13）

判据：
- 用户交付**不得**出现：Prompt 正文、凭据、数据库、内部推理、reference 全文、Dify 调试对象、内部分级术语（如 `LOW_RISK_INTERACTION`）、内部状态码；
- 用户交付**不得**出现「已删除」「审查发现」「修正后」「原方案」「未核实不得使用」及任何被淘汰内容的全文；
- **必要选择与成立条件不得被投影掉**；
- 内部 Artifact 仍保留完整专业产出与未选候选。

## 24. `FX-M4-PARALLEL-CHANGE` · 并行 M1/M2/M3 资产变化（N-25）

```yaml
event: "并行分支上的 M1/M2/M3 候选资产发生变化"
```
判据：**不覆盖、不吸收**；只使**受影响的接缝项** `STALE`；无真实依赖的项继续复用，不全盘推倒。

## 25. `FX-M4-SHORT-ENTRY-METHOD` · 短入口仍需适用专业方法（N-35 / N-36 / N-37）

- `N-35`：短入口输入完整，但当前任务真正适用的专业方法来自某一具体 Skill → **直达仍必须调用或无损承接该方法**。
- `N-36`：出现「为保护专业价值要求六 Skill 全参与」的方案 → **拒绝固定全链**，只调用适用组件。
- `N-37`：短快转化内容不适用完整叙事维度 → **不把不适用维度变成硬门**，但必要质量（事实纪律、成品完整度、活人感）仍成立。

---

## 26. 夹具冻结声明

本包在**任何正式结果产生之前**冻结。冻结后若需修改：必须版本化为 `v0.2`，且据 `v0.1` 得到的正式结论按 `SBC-RF-02` 处理——**受影响 criterion 置 `NOT_VERIFIED + STALE` 定向复验，不受影响证据继续复用，禁止全盘清零**。
