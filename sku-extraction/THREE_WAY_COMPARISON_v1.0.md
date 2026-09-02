# 三 SKU 结构比对与共用件清单 v1.0（E1-1）

```yaml
task_id: DIYU-V1-THREE-SKU-EXTRACTION-001
report_date: "2026-09-02"
zero_model_calls: true
zero_dsl_or_skill_content_changes: true
method: 对三份 DSL 用 yaml.safe_load 结构化解析节点/边/变量引用链，逐节点代码/模板做程序化字符串
  相等性比较与 diff（非目测、非按名字假设相同）；对三份 SKILL.md 做标题结构对照与关键节引文核对。
compared_objects:
  P0: content-production/workflows/DIYU_M4_TOOL_PUBLISHING_PACKAGING_v1_4.yml（82cadc34…，205504 字节）
      + packaging-content-for-release-m4/SKILL_v1.4.md（1e7a9f1a…，66761 字节）
  P1: content-production/workflows/DIYU_M4_TOOL_CREATIVE_SCRIPT_v1_3_TEST.yml（99e8ae5c…，117956 字节）
      + writing-creative-scripts-m4/SKILL.md（442dc126…，47221 字节）
  P1.5: content-production/workflows/DIYU_M4_TOOL_PRODUCTION_DIRECTOR_v1_3_TEST.yml（a25788a3…，117523 字节）
      + directing-content-production-m4/SKILL.md（b48b8840…，46649 字节）
note_on_P0_delta: P0 的 v1_4 比另两个多出 S1-S4 的六条阻断修复内容（fact_verification／market_claim_scan
  两个新节点；hashtags_topics／release_decision 两个新字段；ref_projection 真实字节嵌入）。
  下表逐处标出这是「P0 已修、另两个未修」的部分，不是三者的天然差异——已在各行注明，不重复计入
  E1-1(c) 的「真实专业差异」分类。
```

---

## a) 三方节点骨架对照表

### 节点清单（按图内 id，三者节点 id 命名本身就相同——这不是巧合，是共用同一套「统一能力接缝」骨架的直接证据；但下表仍逐一核实**行为**是否等价，不因命名相同而假定等价）

| 节点 id | 类型 | P0 | P1 | P1.5 | 归属 |
|---|---|---|---|---|---|
| `1788000000001`（输入） | start | ✅ | ✅ | ✅ | **三者都有，变量 schema 逐字段核对完全相同**（`capability_call`/`professional_input`/`entry`/`run_mode`/`example_reference_requested`） |
| `envelope_check`（外壳校验） | code | ✅ | ✅ | ✅ | **三者都有**。剥离 `REQUIRED`/`CAPABILITY`/`ALLOWED_ENTRIES`/`ALLOWED_RUN_MODES`/`DEFAULT_RUN_MODE` 这五行配置头后，**其余代码逐字节 100% 相同**（`_sha`/`_norm`/`_find_scalar`/`_present`/`_vacuous`/`main()` 全部一致，含 `VACUOUS`/`GOAL_FAMILIES`/`CTA_LEVELS` 三个常量列表逐字节相同） |
| `gate_sufficiency`（充分性闸） | if-else | ✅ | ✅ | ✅ | **三者都有，条件逻辑（`envelope_check.can_run == 'true'`）逐字节相同** |
| `ref_projection` | template-transform | ✅（已按 B-03 重写） | ✅（旧版） | ✅（旧版） | 三者都有，但**实现状态不同**——见下方「P0 已修」说明 |
| `projection_record` | template-transform | ✅（新增 `reference_embedding_method`/`reference_provenance`） | ✅（旧版） | ✅（旧版，与 P1 逐字节相同，仅 `capability` 字段值不同） | 三者都有，P0 结构已扩展 |
| `skill_llm` | llm | ✅ | ✅ | ✅ | 三者都有，`completion_params` 数值不同（见下） |
| `final_extract` | template-transform | ✅ | ✅ | ✅ | **三者模板逐字节相同**（P1/P1.5 完全一致；P0 同一套剥离 thinking 段逻辑） |
| `fact_verification` | code | ✅（新增） | ❌ | ❌ | **仅 P0 有，S1-S4 新增，不是天然差异** |
| `market_claim_scan` | code | ✅（新增） | ❌ | ❌ | **仅 P0 有，S1-S4 新增，不是天然差异** |
| `returns_adapter` | code | ✅ | ✅ | ✅ | **三者代码除 `CAPABILITY` 字符串外逐字节 100% 相同**（`LEAK_PATTERNS`/`BACKREF_MARKERS`/`MIN_ARTIFACT_CHARS`/全部解析逻辑一致）。P0 的输入源从 `final_extract.output` 改为 `market_claim_scan.verified_text`（S1-S4 改动，代码本身未变） |
| `projection_gate`（交付缺失判定） | if-else | ✅ | ✅ | ✅ | **三者都有，条件逻辑相同** |
| `recovery_llm`（用户交付投影） | llm | ✅ | ✅ | ✅ | **三者 `prompt_template` 逐字节 100% 相同** |
| `delivery_finalize`（交付收口） | code | ✅（已扩展） | ✅ | ✅ | P1/P1.5 **逐字节完全相同**；P0 = P1/P1.5 版本 + S1-S4 新增的 `fact_gate_blocked`/`market_claim_blocked` 处理分支（新增部分之外，其余代码相同） |
| `binding_record`（保真绑定记录） | code | ✅ | ✅ | ✅ | 三者都有，`RECORD` JSON 内容各自不同（capability/路径/sha256），**代码结构相同，数据不同** |
| `component_return`（组件级 Return） | code | ✅ | ✅ | ✅ | 三者代码除 `CAPABILITY`/`LAYER` 两个字符串常量外**逐字节 100% 相同**——**包括 `QUESTION_MAP` 整个字典**：三份文件里的 `QUESTION_MAP` **逐字节相同**，且这个字典本身已经是一个**覆盖三个 SKU 全部 REQUIRED 字段的超集**（`content_body_or_beats`/`explicit_non_promise`/`cta_contract`/`asset_publish_permission` 是 P0 用的键，`objective`/`expected_change`/`expression_subject`/`content_origin_mode` 是 P1 用的键，`script_or_equivalent_beats`/`production_profile`/`time_window` 是 P1.5 用的键，三组键**同时**出现在三份文件里，各自只用到自己需要的那几个） |
| `end_ok` / `end_component_return` | end | ✅ | ✅ | ✅ | 三者都有，输出变量列表结构一致（P0 多出与新节点相关的字段） |

### 边拓扑

**P1 与 P1.5 的边集合逐字节相同**（15 条边，`(source, sourceHandle, target)` 三元组完全一致，节点 id 也完全一致）。**P0 的边集合 = P1/P1.5 的边集合，唯一差异是把 `final_extract → returns_adapter` 这一条边拆成了 `final_extract → fact_verification → market_claim_scan → returns_adapter` 三段**（S1-S4 新增，17 条边）。

**结论**：三个 DSL 的图骨架在 S1-S4 之前是**完全同构**的（同一套模板生成的三份实例），P0 现在的额外结构是已修复内容，不是三者天然的架构差异。

---

## b) 三方共用件清单（本任务最重要的产出）

| 候选 | 判定 | 判据 |
|---|---|---|
| **外壳校验**（`envelope_check`） | `SHARED_BY_ALL_THREE` | 三份代码剥离五行 SKU 专属配置常量后逐字节 100% 相同，含三个共享常量列表（`VACUOUS`/`GOAL_FAMILIES`/`CTA_LEVELS`）。**机制完全共用，仅 `REQUIRED`/`CAPABILITY`/`ALLOWED_ENTRIES`/`ALLOWED_RUN_MODES`/`DEFAULT_RUN_MODE` 五个配置值按 SKU 各自的产品合同不同而不同**——这是"共用引擎 + 每 SKU 一份配置"模式的清晰实例 |
| **充分性闸**（`gate_sufficiency`） | `SHARED_BY_ALL_THREE` | 条件逻辑（读 `envelope_check.can_run`）三者逐字节相同，纯结构判断，不含任何 SKU 专属语义 |
| **参考文件投影**（`ref_projection` + `projection_record`） | `SHARED_BY_ALL_THREE`（机制角色），**但当前三份实现处于两种不同状态** | 三者都承担"按 M4 统一能力合同 §12 加载矩阵做确定性参考文件投影"这一同一职能，且投影的判据文字（"数值型参数拿不到时不得自造数字，改写定性制作要求"）逐处核对**用词相同**；但 **P0 已按 B-03 重写为真实字节嵌入（17221 字符模板），P1/P1.5 仍是旧版"只描述该不该加载"的实现（839 字符模板，P1 与 P1.5 逐字节相同）**——这是 P0 已修、另两个未修的部分，不是三者天然要做成不同实现 |
| **交付适配**（`returns_adapter`） | `SHARED_BY_ALL_THREE` | 三份代码除 `CAPABILITY` 字符串常量外逐字节 100% 相同，`LEAK_PATTERNS`/`BACKREF_MARKERS`/`MIN_ARTIFACT_CHARS`/`_parse_returns`/`_artifact_status` 全部通用，不含任何 SKU 专属分支 |
| **交付缺失判定**（`projection_gate` + `recovery_llm` + 交付收口 `delivery_finalize`） | `SHARED_BY_ALL_THREE` | `projection_gate` 条件三者相同；`recovery_llm.prompt_template` 三者逐字节 100% 相同；`delivery_finalize` 在 P1/P1.5 之间逐字节 100% 相同，P0 是同一份代码之上叠加 S1-S4 新增分支（新增部分之外完全相同） |
| **保真绑定记录**（`binding_record`） | `SHARED_BY_ALL_THREE`（结构层面），数据各异 | 代码结构（读取哈希、拼 `RECORD`、输出 `binding_json`）三者相同，`RECORD` 里的具体值（`capability`/`source_skill_path`/各 sha256）各自不同——**这是共用机制装载 SKU 专属数据，不是三套不同机制** |
| **事实核验**（`fact_verification`） | `SKU_SPECIFIC`（**目前**）——但代码设计上已声明为可复用单元 | 目前**只有 P0 有这个节点**（S1-S4 新增，闭 B-02）。它读的 `FACT_LEDGER` 格式、判定逻辑不含任何 P0 专属语义（不引用"发布""包装"等 P0 词汇），理论上可以原样搬进 P1/P1.5——但**尚未被搬过去**，因此按"现状"判 `SKU_SPECIFIC`（只有一个 SKU 实际拥有），按"设计意图"应记为"可复用但未推广"，两者不是一回事，本表如实分列，不因设计意图就先判成共用 |
| **市场断言检测**（`market_claim_scan`） | `SKU_SPECIFIC`（**目前**）——同上，已按可复用单元写但未推广 | 同上。它扫描的是"当前最热/现在最少/最佳发布时间"一类**跨 SKU 通用**的无依据当前市场断言模式，P1（内容创意方向）与 P1.5（拍摄决策）同样可能被要求"现在最流行的叙事结构是……"或"现在最省时间的拍法是……"这类断言，模式清单本身（`MARKET_CLAIM_PATTERNS_v1.0.json`）在设计时已声明"供 Matrix / Campaign / Content Brief / Creative Script 等其余能力复用"（该文件 `reuse_note` 字段原文），但**代码节点当前只接入了 P0 一处** |

**三档分布**：`SHARED_BY_ALL_THREE` 6 项（外壳校验／充分性闸／参考文件投影／交付适配／交付缺失判定与交付收口／保真绑定记录）；`SHARED_BY_TWO` 0 项（没有恰好两个 SKU 共用而第三个没有的机制——三者要么全有要么全无）；`SKU_SPECIFIC` 2 项（事实核验／市场断言检测，且均为"P0 已建、另两个未建但设计上可复用"，不是"P0 专属、另两个本不需要"）。

---

## c) 差异性质分类

### 真实的专业差异（这个 SKU 本来就该不一样）

| 差异 | P0 | P1 | P1.5 | 为什么是真实差异 |
|---|---|---|---|---|
| `envelope_check.REQUIRED` | `content_body_or_beats`/`content_promise`/`explicit_non_promise`/`facts_registered`/`cta_contract`/`asset_publish_permission` | `objective`/`expected_change`/`content_promise`/`expression_subject`/`content_origin_mode`/`facts_registered` | `script_or_equivalent_beats`/`content_origin_mode`/`production_profile`/`time_window`/`content_promise` | 三个 SKU 的最低合法输入本来就不同（Q-COMM-04/05/06 §1 各自定义），只有 `content_promise` 与部分事实类字段重叠，其余字段对应各自领域的专业前提 |
| `ALLOWED_RUN_MODES` | 仅 `DERIVE_MODE_AND_PACKAGE` 一种 | `TOURNAMENT_ONLY`/`SELECTED_DIRECTION_TO_SCRIPT`/`FULL` 三种 | `PLAN`/`MANIFEST` 两种 | 对应 Q-COMM-05 §1 明文要求的三种合法入口 A/B/C；P0 是终端包装环节，天然只有一种运行模式；P1.5 的两种模式对应"先出计划"与"按已有素材出 manifest"两个阶段性产出 |
| 核心判断规则（PP-1~5 / CS-1~7 / PD-1~7） | 标题不是摘要、承诺上限取实际成片等 5 条 | 创意方向差异必须是机制差异、不编造/删减取舍等 7 条 | 表演指导必须具体、动作先于机位等 7 条 | 三个 SKU 卖的是完全不同的专业判断（发布包装 vs 创意取舍 vs 制作决策），核心判断内容理应不同，这正是 Gate 表定义的产品差异化本身 |
| G2 评分维度与配比 | M1-M7，总分 82 | M1-M8，总分 84 | M1-M8，总分 85 | 索引文档 §2 明文列为"非共用件"，各 SKU 特有，按代价定档（P1.5 拍摄成本最高，通过分最高） |
| `default_failure_mode`（默认失败模式对照）表内容 | 对应 PP-x | 对应 CS-x | 对应 PD-x | 表格**格式**共用（同一种"默认动作 → 对应判断"两列结构），但**内容**逐条对应各自领域的核心判断，是真实差异——这一项**格式共用但内容专有**，见下方"混合型"说明 |

### 历史偶然（同一件事在三处写法不同，应当归一）

| 差异 | 描述 | 为什么是历史偶然而非专业差异 |
|---|---|---|
| `QUESTION_MAP` 三份逐字节相同却分别维护在三个文件里 | 三份 `component_return` 代码里的 `QUESTION_MAP` 字典**内容完全相同**（包含三个 SKU 全部字段的问句），却在三个 DSL 文件里各自复制了一份 | 内容本身证明这就是一份共用词典，不是三份"碰巧写成一样"——只是当初生成时复制进了每份 DSL，而不是引用一个共享定义。今后任一份要新增一个字段的追问措辞，需要同时改三处才不会漂移，这正是"应当归一"的典型信号 |
| `VACUOUS`/`GOAL_FAMILIES`/`CTA_LEVELS` 三个常量列表 | `envelope_check` 里这三个列表三份逐字节相同 | 同上——明显是同一份配置被复制三次，不是三个 SKU 各自独立设计出了完全一样的清单 |
| "两个问题"（事实/素材）框架 | P1 SKILL.md 明文自称"三份 Skill 共用"，P1.5 SKILL.md 也使用同一套"事实∈{有,无}／素材∈{已确认,待检索,待产出·可控,待产出·不可控}"框架 | 这是被**声明为**共用的专业微标准，但目前只以各自独立措辞的散文形式分别写在 2-3 份 SKILL.md 里，没有一个共同的源文件——是"概念共用、载体各写一份"的历史状态，不是"这个概念在三个 SKU 里本该不同" |
| `explicit_non_promise[]`／`objective.goal_family` 只读继承规则 | 三份 SKILL.md 都有"与统一能力接缝的对接"一节，各自独立措辞地重申同一条规则（目标只读继承、不得静默改写为长期价值内容、目标本身不自动授权高风险表达） | 规则的实质内容（源自 `V1_M4_UNIFIED_CAPABILITY_CONTRACT_v0.1.md`，仓库路径 `decision-chain/docs/`，本任务范围外未摘取）完全相同，只是各 SKILL.md 独立复述了一遍——用词不同但不构成专业判断上的差异，是"同一条合同条款被抄了三份不同的白话版本" |
| `binding_record` 的 JSON 结构键名 | 三者的 `RECORD` 字典键名集合相同（`capability`/`completion_params`/`model_name`/`source_skill_path`/…），只有值不同 | 结构本身相同，只是"数据"不同，本条已计入 b) 的共用件清单，此处仅重申它不是三份独立设计的结构 |

### 混合型（格式共用，内容专有——单列，避免混进上面两类）

- **`默认失败模式对照`**：表格格式（"默认动作 → 对应判断"两列）三者共用，是一种共同的写作规范；具体行内容各自对应本 SKU 的核心判断，是真实差异。这既不是纯粹的历史偶然（格式统一是刻意的写作约定），也不是纯粹的专业差异（格式本身不携带专业信息）。
- **`Return` 七/八项闭环结构**（`return_id`/`source`/`highest_damaged_layer`/`precise_gap`/`affected_objects`/`proposed_disposition`/`needs_user_decision`/`downstream_stale`）：字段结构三者相同（已计入共用件清单的 `returns_adapter.RET_FIELDS`），具体每条 Return 记录的内容当然因任务而异——结构共用、数据专有，与 `binding_record` 同一性质。

---

## P0 已修、另两个未修的部分（不计入上述差异分类，单独列出防止误读为"天然差异"）

| 项 | P0（v1_4，已修） | P1 / P1.5（v1_3_TEST，未修） |
|---|---|---|
| `completion_params` | `temperature: 0`／`top_p: 1` | 无 `temperature` 键（落到 provider 默认）／`top_p: 0.8`——与 P0 修复前的 v1_3 完全一致 |
| Layer A 参考文件真实接入 | `ref_projection` 真实字节嵌入 platforms.md 全文 / industry-conditions.md 选段 / examples.md 全文 | 仍是"只描述该不该加载"的旧实现，`references/platforms.md` 等文件从未被任何节点实际读取——与 P0 修复前的原始架构缺口完全相同 |
| 事实核验代码判定 | 有 `fact_verification` 节点 | 无——`returns_adapter` 不解析 `fact_check_status`，唯一把关者是模型自己（与 P0 v1_3 时代同一缺口） |
| 无依据市场断言检测 | 有 `market_claim_scan` 节点 | 无——无任何代码级校验能拦截"现在最流行的叙事机制是……"一类断言 |
| §1.3/§2 标准输出对象的字段缺口 | `hashtags_topics`／`release_decision` 已补 | 未评估是否有类似缺口需要补字段——见 `CONTRACT_ALIGNMENT_P1_v1.0.md`／`CONTRACT_ALIGNMENT_P1_5_v1.0.md` 各自的产品合同对齐表 |

**这四行差异全部是"P0 走完了 S1-S4，P1/P1.5 还没有"，不是三个 SKU 在架构设计上故意做成不同。** 若 P1/P1.5 走一遍与 P0 相同的阻断修复流程（阶段二各 SKU 静态验证会重新发现这些缺口），预计会得到结构上与 P0 v1_4 高度相似的修复方案——这正是共用件清单为什么值得先比出来再摘：`fact_verification`/`market_claim_scan` 的代码本身已经不含 P0 专属语义，理论上可以直接复用而不是三个 SKU 各自重新设计一遍。
