# V1 M4 统一业务能力合同 v0.1

```yaml
document_id: "V1_M4_UNIFIED_CAPABILITY_CONTRACT"
version: "v0.1"
task_id: "V1-M4-CAPABILITY-SEAMS-RUNTIME-INTEGRATION-001"
task_contract_hash: "b3ceabcbe9bcd82dae2fae84161dce0f0aadd96e395a8d6fa06a3355138331c6"
document_role: "ENGINEERING_IMPLEMENTATION_SPEC"
authority_note: >
  本文件是 M4 执行侧对已冻结业务语义的**工程实现规格**。
  业务语义真源是：上位产品合同、单账号切片子合同 v0.2、M0.3 四份共享合同、
  M1-M4 Phase 0 共享编译前言 §三/§四/§五/§六。
  本文件不新增、不改写、不收窄任何业务语义；它只回答「这些语义在 Runtime 里长什么样」。
  物理字段名属执行侧 HOW，可在同一业务语义下变更。
```

---

## 0. 这份合同解决什么

一句话：**让六份现有专业 Skill 变成可以按需调用、可以直接进入、可以合法组合、可以局部失效的同一条生产能力链，同时一个专业责任都不丢。**

它必须同时挡住两个相反的失败：

| 失败方向 | 长什么样 | 本合同的机械关卡 |
|---|---|---|
| **旧专业链改写经营目标** | 用户要起号/吸粉/流量/GMV，输出却变成长期价值内容 | §7 目标忠实；`objective.goal_family` 全链只读继承 + §7.2 反事实探针 |
| **短入口丢失适用专业方法** | 直达 PP 就没人管事实纪律，直达 CS 就没人管差异机制 | §4 等价输入按**业务语义**判定；§6 每个能力的不可中性化责任；跳过组件 ≠ 降低事实/权限/风险/必要质量 |

以及两个「过度修正」：

- 为保专业价值把六 Skill 变成固定全链 → §3 禁止；`REQUIRED_ALWAYS` 集合为空。
- 为支持短入口把下游输入合同压成无专业含量的最小合规字段 → §4.3 `minimum_sufficient` 按**业务语义**定义，不按字段数。

---

## 1. 统一外壳：承载什么、不承载什么

### 1.1 外壳只承载共通业务语义

统一外壳 `capability_call` 是**信封**，不是内容。它承载所有能力都需要回答的共通业务问题：

| 语义组 | 回答什么 | 实现字段（执行侧可改名） |
|---|---|---|
| 调用身份 | 这次要用哪项能力、从哪个入口进来 | `capability` / `entry` / `call_id` |
| 来源与效力 | 这份输入从哪来、确认到什么程度、什么权限、什么时效 | `provenance{source_kind, source_ref, confirmation_state, permission_scope, as_of, evidence_grade}` |
| 当前目标与优先级 | 主目标、有限次目标、优先级、不可牺牲条件 | `objective{primary_goal, goal_family, secondary_goals[], priority, non_sacrificable[]}` |
| 能力适用原因 | 为什么这次需要（或不需要）这项能力 | `applicability{state, reason}` |
| 用户已提供/已接受内容 | 用户原话、已接受的方向、已接受的产物 | `accepted{user_verbatim[], accepted_artifacts[], accepted_direction}` |
| 最小充分输入 | 本次判断到底够不够 | `sufficiency{decision, equivalence_basis, missing_required[], conditionalized[]}` |
| 等价来源 | 用什么替代了物理上游 | `sufficiency.equivalence_basis` |
| 事实/素材/权限/风险/缺口 | 五类内容分层 | `facts{}` / `assets{}` / `permissions{}` / `risk{}` / `facts.gaps[]` |
| 专业输出边界 | 这项能力到哪停 | `output_boundary{produces[], must_not_produce[]}` |
| 下游可消费语义 | 交给下一段的是什么 | `downstream_handoff{}` |
| 保真绑定 | 源 Skill/版本/hash/附件投影/依赖 | `binding{}` |
| Return 与适用性 | 回改、局部失效 | `returns[]` / `stale_set[]` |
| 双投影 | 内部结构化 vs 用户自然交付 | `views{internal_artifact, user_delivery}` |

### 1.2 外壳明确不承载的东西（硬禁）

1. **不做巨型中性 Schema**：外壳不定义任何能力的专业内容结构。每项能力的专业产出在 `professional_payload` 内，**逐能力不同、不可互换**（AC-02 消融/互换判据挂在这里）。
2. **不得「缺字段即业务不足」**：充分性由 §4.3 的**业务语义清单**判定。外壳字段缺失只触发「这一项未提供」，不自动等于 `INSUFFICIENT`。
3. **不得所有组件同一输入输出**：六项能力的 `required_business_semantics`、`professional_payload`、`output_boundary`、`stop_boundary` 必须逐项不同（§6 表）。
4. **不得把业务判断藏进外壳、父 Workflow、代码节点或 user prompt**。代码节点只允许做：确定性校验、hash、字段搬运、状态推导（由证据推导，规则在本文件明文）、Return 聚合。**任何需要专业判断的规则必须写在对应 Skill 的清晰后继版本正文里。**
5. **不得把专业结果压成摘要**：`views.internal_artifact` 保存完整专业产出；`views.user_delivery` 是**另做的一份自然语言交付**，不是对前者的截断摘要。

### 1.3 `professional_payload` 的不可互换性（AC-02 / AC-15 的挂点）

每项能力的 `professional_payload` 必须至少含三项**只有它能产生**的内容：

| 能力 | 独有输入 | 独有输出 | 独有停止边界 |
|---|---|---|---|
| Matrix | 组织能力候选 + 真实角色权责 + 一手内容来源 | 账号责任卡（唯一使命/重叠对象/不可互换理由）+ 人格四项 | 不做周期目标、排期、脚本、包装 |
| Campaign | 阶段经营任务 + 周期边界 + 产能与承接快照 | 参战/主讲关系 + 不可互换表达角度 + 接力顺序 + 承接判断 | 不写完整脚本、逐镜、成片文案 |
| Content Brief | 已接受的单条业务核心 | 单条制作合同（一个顾客问题 + 一个新判断 + 证据地图 + 叙事节拍 + 发布/降级/取消条件） | 不写完整口播、逐镜头、最终标题/封面/发布文案 |
| Creative Tournament（CS-1） | 存在真实取舍的创意空间 | 机制上实质不同的方向（五轴至少三轴不同） | 只出方向，不出完整脚本 |
| Creative Script | 已选方向 + 表达主体 + 来源方式 | 完整逐字稿 + 三区标注 + 两问表 + `fact_refs[].type` | 不做分镜、机位、剪辑、标题、封面、发布文案 |
| Production Director | 脚本节拍 + 资源档 + 时间窗口 + 已有素材 | `realization_plan`（含七维表演指导、并置检查）+ beat 级 `realization_manifest` | 不改台词、不做包装、不做平台适配 |
| Publishing & Packaging | 兑现证据（manifest 或合法等价） | 推导出的 `mode` + `realized_payoff` + 母版包 + 平台适配 + `used_fact_refs[]` | 不重写脚本或分镜 |

**消融判据**：把任意两项能力的 `professional_payload` 去掉名称后互换，若下游仍能正常消费、或产出没有实质变化，则 AC-02 FAIL。

---

## 2. 七类直接入口

### 2.1 入口定义与 Runtime 表达

`entry` 取值与对应的 Runtime 调用目标：

| ID | 入口 | Runtime 调用 | 必须行为 | 硬禁 |
|---|---|---|---|---|
| `ENTRY-01` | Matrix-only | M4 Matrix 后继应用 | 独立账号架构/诊断；不足只做**组件级 Return**；不继续生产链 | 假 Matrix、全局硬停、暗启下游 |
| `ENTRY-02` | Campaign-only | M4 Campaign 后继应用 | 独立任务或周期覆盖均可；保留**策划身份**或合法 compile；覆盖退出与 Content Task 接缝 | 默认 compile-only、默认调用/绕过、静默改写周期基线 |
| `ENTRY-03` | Direct Brief | M4 Content Brief 后继应用 | 明确选题/等价输入直达；保留目标、事实、权限、表达裁量 | 暗跑 Matrix/Campaign/M3；把周期全部目标塞进单条 Brief |
| `ENTRY-04` | Direct Creative Tournament | **M4 Creative Script 后继应用，`cs_run_mode = TOURNAMENT_ONLY`** | 复用 CS-1；仅真实取舍时给实质不同候选 | 第二套锦标赛、固定候选数、混入周期/包装候选 |
| `ENTRY-05` | Direct Creative Script | **同一个 CS 后继应用，`cs_run_mode = SELECTED_DIRECTION_TO_SCRIPT`** | 已选方向/语义充分时直达完整脚本 | 强制重赛、强制物理 Brief、重复索要同意 |
| `ENTRY-06` | Direct Production Director | M4 PD 后继应用 | 合法脚本与制作约束直达 plan/manifest | 重跑运营/Brief/CS；混淆 plan/manifest |
| `ENTRY-07` | Direct Publishing & Packaging | M4 PP 后继应用 | 合法成片/beat 兑现、平台、目标、权限直达；**mode 由证据推导** | 补跑上游、计划冒充兑现、超成品/权限承诺 |

> **ENTRY-04 与 ENTRY-05 共用同一个物理应用**，只由 `cs_run_mode` 区分。这是共享合同二 §七.2「创意锦标赛继续寄居 CS-1 或由适配层调用；不新建独立 Skill」的直接实现，也是 AC-22/N-43「不得第二套锦标赛」的机械保证：**系统里只存在一处锦标赛代码路径。**

### 2.2 M1 边界（不建第二套路由）

- **M1 负责**：自然语言理解、跨诉求路由、最小追问判断，输出**唯一能力调用意图**。
- **M4 负责**：接收该意图 → 建立统一外壳 → 等价输入判定 → 组合/跳过 → Return → 局部失效。
- **M4 不得**：在接缝内重新做自然语言意图识别。M4 的入口解析器只接受**已结构化的能力调用意图**（`capability` + `entry` + 外壳），或在 `entry` 缺失时按 §2.3 的**确定性充分性规则**推导入口——该推导只读已提供输入的业务充分性，**不读用户自然语言、不做意图判断**。

### 2.3 `entry` 缺省时的确定性推导（不是路由，是充分性推导）

当上游只给出 `capability` 而未给出 `entry` 时，按下表**确定性**推导，规则全部只看输入充分性：

```text
capability=CREATIVE_SCRIPT:
    accepted.accepted_direction 存在且非空  → ENTRY-05
    否则若存在真实取舍（§8.3 判据成立）    → ENTRY-04
    否则                                    → ENTRY-05（直接推荐，不办锦标赛）
capability=PRODUCTION_DIRECTOR             → ENTRY-06
capability=PUBLISHING_PACKAGING            → ENTRY-07
capability=CONTENT_BRIEF                   → ENTRY-03
capability=CAMPAIGN                        → ENTRY-02
capability=MATRIX                          → ENTRY-01
```

**该推导不改变任何业务语义，也不新增能力选择权**：能力已由 M1 选定，此处只决定同一能力内部的运行模式。

### 2.4 跳过物理组件的合法性

跳过某个物理组件**只表示等价输入已经满足**。它**不允许**：

- 降低事实纪律、权限约束、风险约束或当前任务必要的专业质量；
- 暗中补跑上游（任何 M4 后继应用**不得**调用其上游能力的应用——机械保证：M4 六个能力应用之间**零 tool 调用边**，组合只由父接缝按显式 `plan` 编排）。

---

## 3. 按需调用：没有任何能力是必经门

```yaml
REQUIRED_ALWAYS: []          # 空集合。任何能力都不是每次必调
DEFAULT_CALL:    []          # 空集合。Campaign 既不默认调用也不默认绕过
FIXED_ORDER:     false       # 不存在固定顺序
FULL_CHAIN_GATE: false       # 不得要求六 Skill 全参与
```

- 代表性完整关系 `Content Task → Brief → 锦标赛（仅真实取舍时）→ CS → PD → PP` 是**可组合关系**，不是固定流水线。
- 任何「为保护专业价值而要求六 Skill 全参与」的方案一律拒绝（N-36）。
- 任何「适用维度变成全内容统一硬门」的方案一律拒绝（N-37）。

---

## 4. 合法等价输入

### 4.1 等价性按业务语义判定

等价性**不按**上游文件、上游节点、固定字段名或产物完整度判定；**按**业务核心语义是否充分判定。

来源不同只增加 `provenance.source_kind` 标识，**不改变**下游所需的业务核心。但**来源、确认状态、权限、作用域、时效、证据等级必须原样保留**——语义等价 ≠ 证据等价 ≠ 权限等价（Phase 0 前言 §三.2）。

### 4.2 至少必须成立的七条等价路径

| # | 等价路径 | 判据 |
|---|---|---|
| 1 | 完整自然任务或明确选题 → Content Brief | 具备 §5 Content Task 核心的必需子集 |
| 2 | M3 与 Campaign → 同一种 Content Task → Content Brief | §5，provenance 不同、核心同义 |
| 3 | 已接受创意方向或最小语义充分 → Creative Script | `accepted.accepted_direction` 或 §4.3 CS 必需语义齐 |
| 4 | 合法脚本 + 制作约束 → Production Director | 有节拍、事实/素材两问、来源方式、承诺与不承诺 |
| 5 | 合法成片信息 / beat 兑现 / 等价 manifest → Publishing & Packaging | §9 mode 推导所需证据 |
| 6 | 只需包装时 | 不补跑 Brief / 锦标赛 / CS / PD |
| 7 | 不需要 Matrix / Campaign 时 | 直接跳过；需要但不足时**只 Return 依赖分支** |

### 4.3 每项能力的「最小充分业务语义」（不是表单）

> 判据是**语义是否够做出本次专业判断**，不是字段是否填满。
> 下表 `required` 的每一项缺失都必须能说清「它会阻塞哪一个具体判断」，说不清就不是 required。

**MATRIX**
- required：本次确实涉及长期定位/人设/账号职责/表达主体关系/多账号结构的建立、诊断或实质修改；主体与账号范围；足以支持本次长期主张的事实（业务模式、核心顾客、当前经营任务、真实候选角色、角色权责与一手来源、已确认边界）及其来源/确认状态/权限。
- 不足处置：**组件级 Return**（不是整任务停止）。只追问当前最具区分力的一项。见 §6.1。

**CAMPAIGN**
- required：有明确时间或阶段边界的经营任务；主目标 + 有限次目标 + 优先级 + 不可牺牲条件；目标受众及其真实问题；至少一条本轮可用可确认的事实链，且该事实链有实际负责人可确认并具备最低制作条件。
- 涉及承接时 required：对应经营目标 + 有效承接路径。
- 周期覆盖模式 required：当前周期基线 + 覆盖范围 + 恢复边界。
- 不足处置：`INPUT_INSUFFICIENT` 作为**本分支结果**（不是终态），或 `READY_WITH_CONDITIONS`。

**CONTENT_BRIEF**
- required：一个选中的单条内容任务或明确选题；一个主目标 + 有限次目标 + 优先级 + 不可牺牲条件；受众问题/场景/机会 + 期望变化；内容承诺/核心命题/待验证判断；表达主体与责任边界；至少一条可用可确认可公开可制作的事实链及其确认人；内容形态与产能条件。
- **不 required**：Matrix 产物、Campaign 决策包、M3 周期。周期角色不适用时标 `NOT_APPLICABLE`，**不得虚构周期**。
- 平台未确认：不阻塞，输出平台中立 Brief。

**CREATIVE_TOURNAMENT（CS-1）**
- required：主目标 + 受众问题 + 期望变化 + 内容承诺；事实/素材/缺口/明确不承诺；表达主体与表达裁量；内容形态与生产约束。
- 额外判据：**存在真实取舍**（§8.3）。不存在则不办锦标赛，直接推荐。

**CREATIVE_SCRIPT**
- required：已选方向或足以合法触发单条创意判断的明确任务；主目标 + 受众变化 + 内容承诺 + 表达主体与表达条件；事实/原话/观察/设定/素材/来源方式/明确不承诺/权限与表达边界；内容形态。
- 非阻断缺失（时长、平台、资源）：用显式默认 + `assumptions[]`，不停。

**PRODUCTION_DIRECTOR**
- required：脚本或业务含义与可制作结构上等价的内容方案（含节拍、事实/素材两问、承诺与不承诺、事实边界）；`content_origin_mode[]`；资源档 + 时间窗口。
- **硬规则**：`content_origin_mode[]` 缺失 → **回退上游索取，不得静默默认现拍**（源 Skill 已有，后继保留）。
- 「事实=无」的段是上游正常产出，**不是残缺输入**：排「待成立单元」，不退回。

**PUBLISHING_PACKAGING**
- required：准确内容正文 / 脚本节拍 / 等价成片内容说明；内容承诺 + 明确不承诺；事实及来源；表达主体或账号包装定位；CTA 目标/授权/承接边界；素材发布权限。
- `realization_manifest`（beat 级）或合法等价兑现证据：**MIXED/FINAL 必需，PRE 不必需**。
- **不 required**：`cs_final`、`pd_final` 这两个物理产物本身。有合法成片时不得强制补跑 CS/PD（Phase 0 前言 §四 CAP-08）。

### 4.4 「极薄字段齐全」不构成等价（N-34）

输入若只是字段名齐全、但缺少上表 required 的**业务语义**（例如 `content_promise` 填了「做一条好内容」、`facts` 为空、`audience.expected_change` 是「让大家更了解我们」），判定为 `INSUFFICIENT`，**不得冒充等价输入**。处置：只追问最具区分力的一项，或只阻断依赖该语义的分支。

---

## 5. 同一种 Content Task 业务语义

M3 与 Campaign 的 provenance 可以不同，但进入 Content Brief 的**业务核心必须同义**。核心项：

```text
1  受众问题 / 场景 / 机会
2  期望发生的变化
3  适用的内容承诺 / 核心命题 / 待验证假设
4  一个主目标 + 有限次目标
5  优先级与不可牺牲条件
6  周期角色（阶段 / 周期内位置 / 产能）—— 不适用时 NOT_APPLICABLE
7  表达裁量
8  风险边界
9  事实 / 素材 / 缺口及其权限
10 平台 / 内容形态
11 来源（provenance）
12 发布后观察项
```

规则：

- 不适用项写 `NOT_APPLICABLE`，**不得虚构周期、Campaign 或 M3 上游**。
- `provenance.source_kind ∈ {M3_OPERATION, CAMPAIGN, USER_DIRECT, HISTORICAL_ARTIFACT}`，**不是封闭枚举的业务门**：来源只增加标识，不改变 Brief 所需核心。
- **M4 可用冻结 M3 业务夹具规划/验证接缝**，不等待 M3 Skill 最终实现；但**不得读取未采用候选来猜 M3 文件、节点、Schema 或输出**，不得复制 M3 运营判断，不得建临时运营引擎（N-08）。
- Campaign 作为周期覆盖层时只占用其点名的内容位置；未覆盖位置与 Campaign 结束后的周期基线仍归 M3。两者不得静默修改对方的当前有效内容。

**接缝判据（AC-05 / N-07）**：同一业务任务分别以 M3 夹具与 Campaign 夹具表达，进入 Brief 后 12 项核心的**业务含义逐项同义**，`provenance` 不同且可追溯，且**不存在两条并行的 Brief 生产链**。

---

## 6. 六项能力的不可中性化专业责任

### 6.1 Matrix

- 负责：账号设立、长期定位、表达主体、职责关系、事实纪律。
- **不足时返回真实缺口，不造假、不全局终止。**
- **M4 的改造点（本任务核心 Delta 之一）**：源 Skill v0.1.2 §0 要求「输出 `INPUT_INSUFFICIENT` 后立即停止」。后继版本把它改成**组件级 / 分支级 Return**：
  - 只阻断真实依赖 Matrix 结论的分支；
  - 同一轮内的无关诉求继续执行且不受影响；
  - 只追问当前最具区分力的**一项**，不要求重填整套夹具；
  - `INPUT_INSUFFICIENT` 是**本分支结果**，不是整任务终态，本身不触发下游失效；
  - 不生成假 Matrix、不给暂定结论冒充当前有效长期真源。
- 依据：Phase 0 共享前言 §五（该节明文把这项改造指派给 M4）。

### 6.2 Campaign

- 负责：围绕阶段经营任务决定参战、主讲、角度、接力、承接与异常回退。
- **compile 只是合法模式之一**：`campaign_run_mode ∈ {PLANNING, COMPILE_CONFIRMED_DECISIONS}`。
  - `COMPILE_CONFIRMED_DECISIONS` **仅在输入确为已确认决定包时**合法；
  - 不得成为唯一产品身份、默认入口，不得要求用户先手工形成完整决策包；
  - 该模式名称**不得**被冻结为新的 Runtime 枚举门（它是运行模式，不是能力身份）。
- **目标忠实硬规则**：不得把起号/吸粉/流量/GMV/线索/到店静默改写为「认知变化」。无权改目标时**局部 Return**（N-33）。

### 6.3 Content Brief

- 负责：把**已接受的业务核心**编译成单条制作合同。不重做运营判断，不提前代做脚本/镜头/包装。
- **M4 的改造点**：源 Skill v0.1 把「已被接受的 Campaign 决策包」写成唯一上游与硬阻断条件。后继版本改为**来源开放**：
  - 合法上游 = 持续运营决策 / Campaign / 用户直接明确选题 / 合法历史产物 / 满足最小输入的已有脚本构想；
  - §2「上游锁定项」改为**「已接受项」**：只对**当前来源实际提供**的项目继承与执行，未提供项按 `NOT_APPLICABLE` 或条件化处理，**不得用推断补齐，也不得因缺失而拒绝整任务**；
  - 不得为进入 Brief 暗中补跑 Matrix 或 Campaign。
- **单条主目标收敛**：周期可以是混合目标，单条内容只承担一个主要工作 + 有限次要贡献。**不得把整个周期的全部目标塞进同一份 Brief**；冲突时给取舍方案、代价与推荐，由用户裁决，**不压成模糊综合分**（N-32）。

### 6.4 Creative Tournament（CS-1）与 Creative Script

- CS-1 在**真实取舍时**形成题材、钩子、叙事与表达机制的**实质差异**（五轴至少三轴不同）。
- **M4 的改造点**：源 Skill CS-1 硬编码「生成 3 个高差异方向」。后继版本改为**数量由真实取舍决定，不固定**：
  - 存在真实取舍 → 给实质不同的方向（通常 2–3 个，不设上下限）；
  - 不存在真实取舍 → **直接给推荐**，不机械凑候选；
  - 候选在用户选择前**不得被确定性抹掉**（修正「投影剥离候选」）；
  - 用户已选方向 → 不重赛、不强制物理 Brief、不新增确认闸。
- Creative Script 保留：准确区/发挥区/主观区三区、状态推进、台词、失败条件、两问表、`fact_refs[].type`、`explicit_non_promise[]` 只读继承。

### 6.5 Production Director

- 负责：把脚本/等价输入变成场景、镜头、表演、声音、字幕、剪辑与资源降级方案。
- **plan 与 manifest 严格区分**（源 Skill 已有，后继保留并加机械关卡）：
  - `available_assets` = 开拍前手上有什么（输入）；
  - `realization_plan` = 准备怎么做（拍摄前）；
  - `realization_manifest` = **beat 级**实际兑现（素材回来且对上 beat 之后才存在）。
  - 资产级清单（「拍了 42 分钟」）**不是 manifest**。
- **M4 的改造点**：局部重跑——只改脚本局部事实句时，不重跑不受影响的制作单元（§10）。

### 6.6 Publishing & Packaging

- 负责：按已兑现内容与平台条件形成标题、封面、首帧、文案、评论区、CTA 与发布条件。**状态由证据推导**；事实核验不重写创意。
- **M4 的改造点**：解除 `cs_final + pd_final` 物理硬门，改为消费**合法成片等价输入**（§4.3）。等价语义提取规则见 §9.3。
- **live `returns_adapter` 优先**：M4 后继 PP 的 Returns 处理以**当前已发布 Runtime 版本**为理解与保留基线，不得用仓库旧版覆盖（Run Manifest §3.1 `M4-DRIFT-N3`）。

---

## 7. F-10 双向保护

### 7.1 两条对称约束

1. 旧 Skill、附件、Workflow 或 Prompt **不得**把起号、吸粉、流量、GMV、线索、到店及混合目标静默改为长期价值。
2. 按需、直接或短入口**不得**无声丢失当前任务真正适用的专业方法。
3. 跳过组件**不降低**事实、权限、风险与必要质量。
4. 保护专业价值**不得**反向变成六 Skill 固定全链或所有专业维度的统一硬门。

### 7.2 目标忠实的机械实现

```yaml
objective.goal_family:
  enum: [LONG_TERM_VALUE, ACCOUNT_STARTUP, FOLLOWER_GROWTH, TRAFFIC, GMV, LEADS, STORE_VISIT, MIXED]
  propagation: READ_ONLY_INHERIT      # 全链只读继承
  rewrite_authority: USER_OR_FOUNDER_ONLY
  on_conflict: LOCAL_RETURN           # 组件无权改目标时只做局部 Return，不静默改写
```

**验证方式（AC-17，硬门）**：目标反事实——同一事实资源、同一账号、同一表达裁量、同一平台条件、同一模型/参数/预算，**只改变 `objective`**，观察内容承诺、结构、CTA/承接是否**实质变化**。若输出在目标改变后仍收敛到长期价值表达，AC-17 FAIL。

### 7.3 适用专业方法保留的验证方式

**AC-18**：同输入 / 同模型 / 同参数 / 同预算的公平对照 + **盲式人类判断**。

- 不得以调用 Skill 数量证明增益；
- 不得以模型自评证明增益；
- 不得故意弱化对照基线；
- 不得用不同模型、参数、事实、权限或输出预算制造胜利。
- M4 只证明**模块级保真 / 非退化**；整体增益留给 M5（`explicit_non_promise`）。

---

## 8. 共同质量、演绎、CTA 与候选裁量

### 8.1 共同质量底线（按内容类型适用，不是统一硬门）

- 短快、传播或转化目标**不允许**退化为 AI 总结腔、模板拼装、正确但无用的废话或机械复制。
- 活人感、生活感、人设辨识度、创意差异、可拍性、事实纪律、成品完整度：**按内容类型适用**。
- 叙事、共情、视觉感、信息密度、转化机制：**不是全内容统一硬门**，适用性由内容类型决定，允许标 `NOT_APPLICABLE`。

### 8.2 合法演绎与局部事实阻断

- 在事实、权限与用户表达裁量内，剧情、角色、情境模拟、演绎与二创**合法**。
- **没有真实事件 / 岗位 / 案例 / 一手反馈不构成整项前置门**（N-47）。
- 无依据的具体事实**只局部阻断依赖分支**，不降低创意深度与成品质量（N-48）。
- 演绎与现实必须分层：`fact_refs[].type = SETTING` 按设定核对，与现实层在画面/文本上分层。

### 8.3 「真实取舍」判据（候选数量的唯一依据）

存在真实取舍 ⟺ 至少两个方向在下列结构轴中**至少三轴不同**：

```text
核心矛盾 | 叙事发动机 | 人物关系 | 信息释放顺序 | 视觉前提
```

**不构成新方向**（发现即合并）：换标题、换第一句、换语气、换修辞、换案例、换平台名、贴「故事版/干货版/情绪版」标签。

不存在真实取舍 → 直接给推荐，候选数 = 1，**这不是缺陷**。

### 8.4 CTA 三级接缝

| 级别 | 范围 | 条件 |
|---|---|---|
| `LOW_RISK_INTERACTION` | 关注、评论、收藏 | 按目标与表达裁量即可提出，不要求用户另填 CTA 表单 |
| `BUSINESS_HANDOFF` | 商品点击、咨询、线索、到店、购买引导 | 需要**对应经营目标 + 有效承接路径 + 事实依据** |
| `HIGH_RISK` | 站外导流、价格优惠、强购买承诺等 | 需要**明确授权** |

硬规则：

- **目标本身不自动授权高风险表达**（流量/吸粉/GMV 目标 ≠ 授权激进、争议或高风险 CTA）。
- CTA 不得编造商品事实、价格、优惠、库存、承接能力或经营承诺。
- `cta_contract` 可取 `KNOWN_BUT_NOT_AUTHORIZED`（知道存在业务动作但本条未获授权）——这是**权限不全**，不是信息不全。
- `cta_contract = 无 CTA` 时，**整份产出**（含评论区与转发语）不得出现奖励、领取、关注交换、私信、到店、预约、购买、下单或咨询引导。
- 面向用户使用自然语言表达具体行动方向，**不暴露内部分级术语**。

### 8.5 三层候选不得混写

```text
周期策略候选   —— 本周期做什么组合、目标如何分配、节奏如何安排   （M3 层，M4 不代做）
单条创意候选   —— 题材、钩子、叙事、表达机制                     （CS-1）
包装候选       —— 关键标题、封面、入口包装                       （PP）
```

- 三层**不得互相替代**，不得混写进同一个候选列表。
- 只有真实取舍才给多方案；数量不固定，**不得硬编码**。
- 用户可选择、混搭、局部修改；**普通可逆生成不新增确认闸**。

---

## 9. 状态：PRE / MIXED / FINAL

### 9.1 定义（由证据推导，不由字段声称）

```text
PRE    只有计划、脚本、预期资源或未兑现素材
MIXED  部分 beat/素材兑现，部分未兑现，逐项限制
FINAL  所有决定发布承诺的必要 beat/素材有当前 manifest 或等价兑现证据
```

### 9.2 三级推导（顺序不可颠倒）

```text
第一级 PRE（满足任一即 PRE，优先于其他一切判断）
  · 没有 beat 级 realization_manifest（或等价兑现证据）
  · content_origin_mode[] 中仍有一种计划使用的素材尚不存在（待拍/待画/待生成/待采集）且未被正式取消

第二级 MIXED
  · 已有 beat 级兑现证据，计划素材均已存在或已正式取消
  · 但任一 beat 的覆盖缺口仍处于：等待补拍 / 等待替代素材 / 等待人工决定 /
    处理方式不明确 / 尚未完成承诺降档

第三级 FINAL
  · 已有 beat 级兑现证据，计划素材均已存在或已正式取消，且
  · 所有 beat 画面支撑为「有」，或每一处「没有」「有但不够」都已通过删除、替换或降低承诺**完成处置**
  · 无待补拍 / 待替换 / 待人工决定事项
  · 最终标题、封面、发布文案与 CTA 已按 realized_payoff 收敛
```

硬规则：

- 「有，但不够」**本身不决定 mode**；决定 mode 的是缺口有没有**处置完**。
- 「有覆盖单元」≠「已处置」。
- FINAL 的 `uncovered_beats[]` 允许非空，但每一项必须写出**已完成的处置结果**，**不得留 OPEN 项**；有一项写不出，退回 MIXED。
- **plan 不等于 manifest**；资产级清单不是 manifest。
- **素材撤回只回退受影响承诺**（N-16），不整条推倒。

### 9.3 合法等价兑现证据（PP 直达的实现，Phase 0 前言 §七.4 指派给本任务）

当没有上游 PD 产出的 `realization_manifest` 时，下列输入可作为**等价兑现证据**，前提是它能按 beat（或等价内容单元）逐条回答「这条的事实有多少画面/内容支撑」：

| 等价输入 | 成立条件 |
|---|---|
| 已有成片 + 成片内容说明 | 能逐条对应到内容单元，并标明每单元的支撑状态（有 / 没有 / 有但不够） |
| 用户提供的 beat 兑现清单 | 含内容单元、素材出处（起止时间码或第几张）、支撑程度、缺口处置 |
| 已有素材剪辑且检索已完成 | 检索完成且对上单元 → 真实 manifest，可走 FINAL（「没有新拍」不是走 PRE 的理由） |
| 图文/纯音频等非视频成品 | 按对应载体的单元定义逐条回答同两个问题 |

**不成立**：只给资产级数量（「拍了 42 分钟」「有 36 张图」）→ 按「没有 manifest」处理，走 PRE，并**回退索取单元级**，不自行按分钟数猜（N-14）。

---

## 10. Return、局部失效与幂等恢复

### 10.1 Return 结构（每条必须含七项）

```yaml
return:
  return_id: <稳定 id>
  source: <哪个能力 / 哪个环节发出>
  highest_damaged_layer: <被新事实实际破坏的最上游判断层>
  precise_gap: <具体缺什么，不写"信息不足">
  affected_objects: [<受影响的对象，逐个列出>]
  proposed_disposition: ACCEPT_AND_PATCH | REJECT_WITH_AUTHORITY | ESCALATE
  needs_user_decision: true|false
  downstream_stale: [<哪些下游变 STALE，只列真实依赖>]
  parse_status: OK | PARSE_FAILED
```

### 10.2 处置规则

- 每条 Return 必须形成**且仅形成一种**处置：
  1. **接受并局部修改**；
  2. **依据权威/事实/边界拒绝**（必须给出理由，不得沉默丢失，N-13）；
  3. **精确升级**。
- **Return 不自动回环**：不得因为收到 Return 就自动重跑上游。
- **解析失败 ≠ NONE**：`parse_status = PARSE_FAILED` 时**局部阻断并保留失败原文**，不得伪装成空数组或 `NONE`（N-12）。
- 恢复前**先查目标系统**以防重复副作用（N-24）。

### 10.3 局部失效（A3 实现）

```text
INVALIDATED = changed_bindings ∪ transitive_dependents ∪ unknown_dependency_items
```

- **正文/关键语义未实质变化 → 不使下游全链失效。** 判定依据：`body_hash` + 被下游实际消费的业务含义。排版、措辞、说明文字、重跑但结果未变、用户提出建议但最终未采纳，**均不触发失效**。
- 变化只下传**直接依赖、传递依赖与影响关系未知项**；未知项标 `STALE`，待定向复验。
- **修复指向最高失效层**，不在下游打补丁。
- 不反向传播：包装变化不使 Script/Brief/PD 失效。
- **已发布内容保留为历史**，不因上游后来变化而失效或被改写。

### 10.4 依赖记录机制（Phase 0 前言 §七.5：最小机制，不建重型依赖图）

每个产物记录：

```yaml
artifact:
  artifact_id
  body_hash            # 正文规范化后的 sha256
  semantic_keys        # 被下游实际消费的业务含义键值（逐能力定义，见 §10.5）
  depends_on: [{artifact_id, body_hash, semantic_keys_consumed[]}]
```

失效判定：只有当 `depends_on` 中某条的 **`semantic_keys_consumed` 实际变化**时才失效；`body_hash` 变了但被消费的 semantic key 未变 → 不失效，只更新引用。

**不建**：事件溯源平台、通用依赖图服务、图数据库。

### 10.5 各能力被下游消费的 semantic keys

| 产物 | semantic_keys |
|---|---|
| Matrix | `account_mission` / `positioning` / `account_duty` / `expression_subject_relation` / `fact_permission` / `expression_boundary` |
| Campaign | `deadline` / `objective` / `priority` / `participants` / `content_tradeoff` / `evidence_chain` / `capacity` / `cta_contract` / `override_scope` |
| Content Task | §5 的 12 项核心 |
| Content Brief | `primary_goal` / `audience_problem` / `core_claim` / `content_promise` / `evidence_map` / `expression_boundary` / `asset_condition` / `cta_contract` / `production_condition` |
| Creative Direction | `selected_direction` / `core_conflict` / `narrative_engine` / `info_release_order` / `expression_subject` / `fact_premise` |
| Creative Script | `content_promise` / `explicit_non_promise` / `script_beats` / `lines` / `fact_refs` / `asset_needs` / `expression_subject` / `constraints` |
| PD plan | `capture_units` / `beat_coverage_plan` / `asset_list` / `constraints` |
| PD manifest | `beat_coverage_actual` / `evidence_source` / `gap_disposition` |
| PP | `mode` / `realized_payoff` / `single_distribution_promise` / `cta_surface` / `platform_variants` |

---

## 11. 内部与用户交付分离

### 11.1 内部可保存

结构化合同、来源、版本、hash、状态、Return、附件投影、证据、**未选候选**与调试信息。

### 11.2 用户只看到

自然、完整、可使用的结果；必要候选；推荐；真实阻断；最小决定。

### 11.3 硬禁（N-23）

- 不得泄露：Prompt 正文、凭据、数据库、内部推理、reference 全文、Dify 调试对象、内部分级术语、内部状态码。
- **也不得把用户必要选择和成立条件投影掉**——「不泄露」不是「少给」。
- 事实核验失败时：**保留原 Artifact 与失败输出，不删句翻绿**（N-22）。
- 用户交付块内**不得**出现「已删除」「审查发现」「修正后」「原方案」「未核实不得使用」以及任何被淘汰内容的全文；淘汰原因写在内部 Artifact 里（源 PP Skill 已有，后继保留）。

---

## 12. 条件附件加载

当前 references：`platforms.md`、`industry-conditions.md`、`examples.md`。

规则：

1. **只按当前能力和当前任务加载必要且仍有效的最小投影**；已有等价事实不重复全文。
2. 示例只作**形式/质量参考**，不变成事实、话术或模板。
3. 动态项过期或无来源 → 保留 `NOT_VERIFIED` 并**降低相应主张**，不得凭记忆补数字。
4. 撤回或权限失效 → 只使**真实依赖项** `STALE`。
5. 主本与投影登记 hash 与同步关系。
6. **不得建第二套附件库、知识库或 RAG-first 层。**
7. 数值型平台参数拿不到 → `platform_spec_status = PLATFORM_SPEC_UNVERIFIED` + 定性制作要求，**不得自造数字**；分支型参数拿不到 → 条件式改写，两支都写完整。

**加载矩阵**（`references_projection` 的确定性规则）：

| 能力 | platforms.md | industry-conditions.md | examples.md |
|---|---|---|---|
| Matrix | 不加载 | 不加载 | 不加载 |
| Campaign | 不加载 | 不加载 | 不加载 |
| Content Brief | 不加载（平台中立） | 不加载 | 不加载 |
| Creative Tournament | 仅当平台结构参数改变 beat 数时加载该节 | 按 `subject_domain` 加载对应段 | 仅当显式请求 |
| Creative Script | 同上 | 同上 | 仅当显式请求 |
| Production Director | 仅当影响构图/单元数时加载该节 | 按 `subject_domain` | 仅当显式请求 |
| Publishing & Packaging | 按目标平台加载对应条目（含 `as_of`） | 按 `subject_domain` | 仅当显式请求 |

无关附件存在时**不加载全文**，不让示例变模板或事实（N-18）。

---

## 13. 保真绑定（每次调用必须可回指）

```text
源 Skill / 授权后继
  → Workflow System Prompt 正文与适配 diff
  → 条件 reference 最小投影
  → draft / published 实际 Prompt 字节
  → 模型、参数、reasoning
  → Tool provider 与父 Workflow 绑定
  → Formal Attempt 实际绑定与原始输出
```

**不能单独证明保真的东西**：自报 hash、文件存在、导入成功、发布成功、模型自评、静态 YAML。

**薄适配 vs 后继 Skill 的划线**：

- **允许做薄适配**（不进 Skill 正文）：纯传输、格式转换、来源标识、hash 计算、字段搬运、状态推导（规则已在本文件明文且确定性）、Return 聚合。
- **必须进 Skill 后继正文**：任何新增业务判断。本任务据此为**全部六项能力**建立清晰后继版本（§6 逐项列出改造点）。

**模型参数不得压制专业方法**：参数漂移必须以**同输入、同 Skill、同模型、固定参数与预算、预冻 Oracle** 公平验证（N-21：reasoning 改变且更快，不得据此宣称专业等价）。

---

## 14. 明确不承诺

- M4 完成 ≠ 完整单账号持续运营纵向切片已验证。
- M4 不证明真实运营闭环、真实经营提升或完整生产链整体增益。
- 冻结 M3 夹具通过 ≠ M3 Runtime 已接入。
- 文件、DSL、自报 hash、导入成功或模型自评 ≠ Runtime 保真。
- 短入口 ≠ 降低事实、权限、风险或必要专业质量。
- 保护专业价值 ≠ 固定调用全部六 Skill。
