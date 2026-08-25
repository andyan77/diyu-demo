# V1-REBASE-EP00-CURRENT · M0 当前真相预检报告 v0.1

> 文档角色：**只读预检结论**，不是施工包，不冻结任何未来 Schema／接口／状态机。
> 任务 Manifest：[collab-ledger/L1_TASK_MANIFESTS.md §T-002](../../collab-ledger/L1_TASK_MANIFESTS.md)（`task_contract_hash=0a176145f7e7ed5b99f2fb09c583800c81a8829ca5cba227571d51d0f32b1210`）
> 授权依据：[V1 决策链改造产品合同](V1_DECISION_CHAIN_REBASE_PRODUCT_CONTRACT_v0.1.md)「授权状态与下一步」；[决策链当前阶段基线 v0.2](V1_DECISION_CHAIN_STAGE_BASELINE_v0.2.md)。

---

## 〇、核验时间、环境与基线

| 项 | 值 |
|---|---|
| 核验时间 | 2026-08-24（本任务首次开工） |
| 执行分支 | `task/v1-rebase-ep00-current-m0-preflight`（从 `main` 切出，内容与 main 一致，未合并） |
| **实际执行基线** | `main @ 4d84cd2a4bbd9bcbcff97105f226cf5652f13e29`（local == origin/main，工作区在本任务开工前 clean） |
| 账本 / Prompt 观察的 `6ae78ab` | **STALE_BENIGN，非 CONFLICT**：collab-ledger canonical §七与 L2 记的是**固定起算锚点**，不追踪 HEAD；`6ae78ab` 是 `4d84cd2` 的祖先，二者间 8 个 commit 经 `git diff --stat` 核验只动 `collab-ledger/**`、`CLAUDE.md`、`PROJECT_INDEX.md`、`README.md`（COLLAB-LEDGER-BOOTSTRAP-001 自身收口），零产品语义漂移 |
| remote | `https://github.com/andyan77/diyu-demo.git`（origin） |
| remote heads | 9（含 origin/main） |
| local branches | 11 |
| worktrees | 5（含本 worktree） |
| Dify 目标环境 | 本机 Docker，Dify **1.16.1**，17 容器，2 天在线，健康（`docker ps -a` 核验，见 §七） |
| Dify 核验通道 | `docker exec docker-db_postgres-1 psql -U postgres -d dify` 只读查询（详见 §〇.1） |

### 〇.1 真源与证据有效性说明（Dify 核验通道的一处重要更正）

本仓库声明可用的 MCP 工具 `dify-platform-expert` 与 `dify-workflow-1/2/3`：
- `mcp__dify-platform-expert__get_platform_info` 返回 `base_url: http://localhost:8080`，看似指向本地；但 `list_workflows` 调用**自报**：`"note": "Dify API not available. This is demonstration data."`，返回的两条示例工作流（"Content Generation Pipeline" "Data Processing Workflow"）与本项目任何真实资产都对不上。**结论：此工具是与本项目无关的演示/占位 MCP，不构成对本项目真实 Dify 的核验通道，本报告不采信其任何输出。**
- `dify-workflow-1/2/3`（"WF-Topic-Plan" "WF-Retrieve-Generate" "WF-Eval-Feedback"）三个工具名称与本项目任何工作流命名均不匹配，且为**执行型**工具（会真实调用已发布 App 生成内容），按本任务只读边界**未调用**，判定为与本项目无关。

**真实核验通道**：本机 Docker 确实运行着为本项目搭建的真实 Dify 1.16.1 全栈（`docker-db_postgres-1` / `docker-api-1` / `docker-web-1` / `docker-nginx-1` 等 17 容器）。默认沙箱禁止 `docker.sock` 访问（`permission denied`），经证据触发后按 `dangerouslyDisableSandbox: true` 执行只读 `psql SELECT`（`tools/v1_demo_e2e_replay.py` 头部注释证实这正是本项目历史真实回归脚本使用的同一基础设施：真实 Dify Service API + `docker exec docker-db_postgres-1 psql` 只读核验）。本报告中所有「Dify 已发布/草稿」结论均来自该通道的原始查询结果，不来自仓库推断，不来自上述两个假 MCP 工具。

---

## 一、权威与授权链核验（A2）

逐项原文核对，跨 6 份独立文件，**结论：CURRENT，无 CONFLICT**：

| 文件 | 记载的授权状态 |
|---|---|
| `decision-chain/docs/V1_DECISION_CHAIN_REBASE_PRODUCT_CONTRACT_v0.1.md`（上位合同，行 1-21, 895-915） | `PRODUCT_CONTRACT_ACCEPTED — REPO_PREFLIGHT_AUTHORIZED`；**仅**授权 `V1-REBASE-EP00-CURRENT`；不授权 Skill/DSL/持久化/工作流施工；不授权子合同专项预检 |
| `decision-chain/docs/V1_SINGLE_ACCOUNT_SLICE_CONTRACT_v0.1.md`（子合同） | `CONTRACT_REVISION_REQUIRED` — 未被接受，不构成授权 |
| `decision-chain/docs/V1_DECISION_CHAIN_STAGE_BASELINE_v0.2.md`（阶段基线，取代 v0.1「阶段转移」一节，v0.1 原文不改） | 阶段 = V1 Rebase；决策链与内容生产链**都在产品范围内**，无「唯一主线」；下一步 = `V1-REBASE-EP00-CURRENT` |
| `笛语项目基线.md` §〇 | 同上，并声明本文件是当前项目定位/阶段/已裁决事项的最高优先级真相源 |
| `CLAUDE.md` §1 | 同上表述，逐字一致 |
| `PROJECT_INDEX.md` §〇 | 同上表述，逐字一致 |
| `README.md`「当前状态」 | 同上表述，逐字一致 |

三类 EP-00 的语义边界（collab-ledger L2 §三 与 Prompt 第 3 节一致）：
- `V1-REBASE-EP00-CURRENT`（本任务）：已授权，本次为**首次真正开工**（此前 L2 §一.2 记为「未开工」）；
- `SINGLE-ACCOUNT-SLICE-EP00`：依赖未接受的子合同，**不得开展**；
- `AO-EP00-HISTORICAL`（`feature/account-operation-v1 @ df94ed1`）：**只作历史参考**，不得冒充当前预检，不得直接合入 main —— 产品合同 §十八本身已引用其价值耦合初步结论，并**明确标注为历史证据、施工前须复核**（见 §五）。

**未见 CONFLICT。** 唯一需要留意的是「上位合同接受 ≠ 子合同接受 ≠ 授权施工」这条边界在 6 份文件中反复出现且措辞一致，说明这不是巧合对齐，而是有意维护的单一事实源。

---

## 二、八项能力现状卡（A5）

> 交叉版本核验：Matrix/Campaign/Content Brief 三份决策链 Skill 正文 SHA-256 与 DSL 内 `EXPECTED` 钉住值逐一核对，**全部 MATCH**；内容生产三 Skill **无任何 SHA 版本绑定**（`grep -ril skill_sha content-production/workflows/` 零命中）——决策链有版本防护、生产链没有，是一处独立于 A16 之外、值得单列的 CONFLICT。

### 能力 1 · 账号架构与诊断（Matrix）—`CONFLICT`（承诺"可直接进入"，机制上确实是链条起点，无上游依赖）
- **载体**：`decision-chain/skills/Matrix_Architect_v0.1.2.md`（SHA 与 DSL 钉住值一致）→ Tool `diyu_v1_matrix_architect`（`DIYU_DEMO_V1_TOOL_MATRIX_v0.1.yml`）。
- **入口**：`v1_route` 按确定性 `effective_route` 分支，模型不参与选择；是唯一 `UPSTREAM_OF=None` 的能力，机制上真是链条起点。
- **必需输入 vs 实际**：声明输入只有一个 `task_context` 字符串；**品牌事实、账号数量（"四张"）全部硬编码在 Tool 的 Prompt 正文里**，不是真实结构化输入——违反合同 §十六「Prompt 不硬编码夹具人物和行业」。
- **无等价输入通道**：换品牌需要重新发布 Tool 并同步改 `EXPECTED.fixture_bundle_sha`，否则 `pre_matrix` 直接判失败。
- **交付形态**：`fin_matrix` 把**完整内部产物**（A-0 证据实测 7,440 字）整段拼进用户可见消息，不是合同 §十三要求的「一页纸摘要+推荐方案」——六项能力中**唯一没有做"内部产物/用户交付"两层拆分**的一个（对照生产链三 Skill 都做了拆分）。
- **下游失效机制**：存在（`DOWNSTREAM[matrix]=[campaign,content_brief,production_stage1,publishing_stage2]`），但**无条件级联**——只算 `content_hash` 却从不与上一版比对，等于"没有实质修改也会让全部下游失效"，与合同 §十一"未发生实际修改时下游不失效"相反。
- **证据**：`V1_DIALOGUE_ORCHESTRATION_REPAIR_001_EVIDENCE.md` A-0（`DONE`，真实 Dify 对话）。
- **缺口**：资料不足时**整任务硬停**（`INPUT_INSUFFICIENT` 后禁止追问/降级），与 CLAUDE.md §4"资料不足时不得整任务拒绝"直接冲突，六份 Skill 中最严重的一处。

### 能力 2 · 单次经营任务策划（Campaign）—`CONFLICT`（合同称"可独立发起"，实际强制要求 Matrix 已被接受）
- **载体**：`Campaign_Orchestrator_v0.1.md` → Tool `diyu_v1_campaign_orchestrator`。
- **入口**：`gate_reason()` 硬性要求 `matrix.status==USER_ACCEPTED`，合同 §四标注 Campaign"可独立发起"与实际不符。
- **最关键发现**：Tool Prompt 里写死 `RUN_MODE：COMPILE_CONFIRMED_DECISIONS`，并明令"**不得重新选择主要顾客变化、主讲账号、发布顺序、参战组合、内容数量和承接政策**"——**当前部署的 Campaign 不是"从用户意图规划战役"，而是把序里集 C1–C6 Founder 确认稿原样编译成决策包**。产能/承接条件同样来自冻结夹具文本，不是真实结构化输入。
- **交付形态**：同 Matrix，完整内部产物（~23KB）直接进聊天。
- **下游失效**：机制存在，同样无条件级联（不比对哈希）。
- **证据**：A-1（`DONE`）+ 8 次历史 A/B 跑分（`CAMPAIGN_DIFY_RUN_MANIFEST_v0.1.md`，Skill SHA 与当前一致）。
- **缺口**：与合同 §五.1 期望的"真实规划"能力有本质差距；"期望发布量"在全仓库 0 命中。

### 能力 3 · 单账号持续运营能力 —**MISSING（本仓库当前分支零实现）**
- 三重核验确认：目录不存在；全仓 grep 相关术语（account_operation／持续运营／运营周期／栏目疲劳／发布节奏）除夹具散文外零命中；状态机 `SKILLS` 枚举只有 5 个值，无第 6 个槽位。
- **唯一相关历史痕迹**是分支外的 `feature/account-operation-v1 @ df94ed1`——核实后是**一份 209 行的只读预检报告**（`account-operation/docs/ACCOUNT_OPERATION_EP00_PREFLIGHT_v0.1.md`），**不是**部分实现，零 Skill 文件、零工作流 DSL、零代码。collab-ledger 已标注 `AO-EP00-HISTORICAL`：只作参考，不得冒充当前预检。
- **明确排除误代入**：Campaign 的循环执行**不是**替代——Campaign 是对冻结 7 天决策集的一次性编译，无周期 N→N+1、无反馈摄入、无跨会话状态。Matrix 的能力**也不是**替代——合同 §四已把"本周期内容组合和表现调整"划给持续运营，Matrix 两者都没有。
- **持久化前提未满足**：合同 §十六"持续运营的最小持久化例外"要求"声称跨会话持续运营能力就必须有可恢复的业务持久化能力"，而当前状态只存在单会话作用域的 Dify 会话变量（见 §八）。
- **对应 Gap Register**：G-01/G-02/G-05/G-06/G-07 已被明确标注为"持续运营成立条件"，12 项全部未关闭。子合同 `V1_SINGLE_ACCOUNT_SLICE_CONTRACT_v0.1.md` 仍是 `CONTRACT_REVISION_REQUIRED`，不构成授权。

### 能力 4 · Content Brief —`CONFLICT`（合同称"可直接进入"，机制强制要求 Campaign 已接受）
- **载体**：`Content_Brief_Architect_v0.1.md` → Tool `diyu_v1_content_brief_architect`。
- **入口**：`UPSTREAM_OF["content_brief"]="campaign"`，`gate_reason()` 硬阻断——这正是本报告 §四.3 已发现的架构级冲突的运行时后果（Skill 正文与 DSL 状态机双重锁死 Campaign 为唯一上游）。
- **必需输入**：`TARGET_PLATFORM` 在 Prompt 里被硬编码为字面量 `PLATFORM_UNCONFIRMED`，不是真实变量。
- **证据**：独立 App 时代 3 次运行（`CONTENT_BRIEF_DIFY_RUN_MANIFEST_v0.1.md`，相对当前集成 Tool 版本为 **STALE**）+ 集成路径证据（`BRF-SUHE-001` 在 `CONTENT_PRODUCTION_FULL_BRIEF_PRE_CHAIN_RUN_001.md` 中被真实消费）。
- **缺口**：合同 §十八"必须废止"清单里的"Brief 永久被单一决策包锁死"——**当前仍然成立**。

### 能力 5 · 创意决策/创意锦标赛（CS-1，内部能力）—`CONFLICT`（本次核验中最锋利的一条发现）
- **载体**：不是独立 Skill/Workflow，只是 `writing-creative-scripts/SKILL.md` 内一节（"CS-1·创意方向的差异必须是机制差异"）。无路由分支、无枚举值、无节点、无 Tool——用户无法单独触发"只做创意锦标赛"。
- **机制真实存在**：3 个高差异方向、5 条结构轴、"任两方向至少 3 轴不同"判据、明确的"伪差异"清单（换标题/换语气/换案例等不算差异）。
- **但候选从未到达用户**：Creative Script 工作流的用户交付契约明文要求"**只保留最终采用的那一个版本，不写候选方案、不写推演过程、不写淘汰了什么**"，`fin_stage1` 也只透传最终交付块。**候选生成机制存在，但被确定性地在用户看到之前抹除。**
- **对照合同**：合同自己已预先登记两条缺口——①只在内部三方向互比、不与外部平台比较；②Skill 自行选定 1 个深化、未把 2-3 候选交用户裁决——**本次基于当前 HEAD 独立复核，两条均属实**。
- **缺口**：合同验收 D"推荐但不删除备选、用户选择混搭"当前从用户侧完全不可达。

### 能力 6 · Creative Script —`CURRENT`（生产链质量最好的一张卡，但入口仍受线性锁约束）
- **载体**：`writing-creative-scripts/SKILL.md` → 独立 App `DIYU Demo Creative Script v0.1`（也是唯一被下游融合进 `tool_stage1` 的形态）。
- **入口**：主链内**没有独立入口**——与 Production Director 融合成一个 `production_stage1` 槽位、一次 Tool 调用；主链外，独立 App 可直接运行（已有 3 次独立跑通证据，505.7s）。
- **降级通道存在但在主链不可达**：Skill 正文本身有完整的分槽位降级规则（如 `content_origin_mode` 缺失时的处理），但 `gate_prod` 要求 13 个槽位全部非空才放行，Skill 自带的降级契约被编排层架空。
- **交付形态**：六份中实现最好的两层拆分——完整内部产物存会话变量，用户只看到 `---USER_DELIVERY_CS---` 精简块。
- **下游失效**：`cs_hash`/`pd_hash` 独立计算并在 Stage 2 做真正的哈希核对（全系统唯一一处真正基于内容哈希的漂移检测），但 STALE 触发本身仍是无条件的。
- **发现的漂移**：仓库 YAML `reasoning_effort: max`，但 2026-08-23 起全部运行证据显示实际生效值是 `low`（`FIXTURE_RUN_002.md` 记录了这次刻意的 high→low 修改）——与 Dify 扫描 Agent 独立发现的 D2 完全吻合（互证）。

### 能力 7 · Production Director —`CURRENT`（同 Creative Script，入口受同一线性锁约束）
- **载体**：`directing-content-production/SKILL.md` → 独立 App，`reasoning_effort:low`（与证据一致，无漂移）。
- **入口**：与 CS 共享同一 `production_stage1` 槽位——**无法单独重跑**：CS 或 PD 任一变化都会让 Stage 2 整体重新失效，无法只重跑受影响单元（违反合同 §四"只重跑受影响单元"）。
- **交付形态**：`---USER_DELIVERY_PD---` + 回改事项列表，是全系统里最接近合同 §十三"少量关键决策"设计意图的一处。
- **证据**：独立运行 + 集成运行证据齐全（559.6s / DONE）。

### 能力 8 · Publishing & Packaging —`CURRENT`（全系统事实纪律把关最严的一张卡）
- **载体**：`packaging-content-for-release/SKILL.md`（v0.6.2）→ 独立 App，`reasoning_effort:low`。**独立语义事实核验节点**（`semantic_check`，`qwen3.8-max`，与内容生产主链的 DeepSeek 刻意换厂商）挂在父流 Stage2 内。
- **入口**：同样受线性锁约束，要求 `production_stage1` 已接受。
- **PRE/MIXED/FINAL 三级判据真实实现**：由 `realization_manifest`（可选输入）的完整度倒推 mode，"有但不够"本身不决定 mode。
- **四路真实出口**：`deliverable`（正常交付）／`FAILED`（结构缺陷）／`blocked`（确定性闸或语义闸拦下，产物原样保留、问题句原文引用，绝不自行删句重发）／`needs_human`（核验器本身不可用或需人工复核，绝不冒称已通过）。
- **证据链完整且诚实**：STANDALONE_RUN（独立可跑）→ FINAL_CHAIN_RUN_001（PARTIAL，FINAL 档从未真正跑到过，只推导出过 MIXED）→ P05R1（PARTIAL，一处假绿：模型自称删除、实际未删）→ P05R2（PARTIAL，四道确定性闸 12/12 通过，但人工复核揪出一句带真实 fact_id 的编造次数"十几次试穿"，闸和扫描器全部放行）→ P05R3（语义核验节点正确拦下同一句，但其证据范围仅 4 项输入，账号结构类陈述判不稳）。
- **缺口**：`FINAL` 三级判据里最高档从未在任何真实运行中走到过。

---

## 三、路由与任务上下文（A4）

### 三.1 结论：当前是**纯 Skill 路由**，不是经营目标路由，也不是二者混合

判定依据（层层核验，非推断）：
1. 唯一决定调用哪个能力的字段是 `requested_skill`——一个 6 值封闭枚举（`NONE/MATRIX/CAMPAIGN/CONTENT_BRIEF/PRODUCTION_STAGE1/PUBLISHING_STAGE2`），本质是"模块名"而非"经营目标"。
2. 其分类规则是纯**关键词→模块名**映射（如"战役/七天计划/发布顺序→CAMPAIGN"），用户没点名任何关键词就是 `NONE`。
3. `change_goal` 字段被 Prompt 明文禁止参与路由——"填的是经营问题，不是执行命令"，只用于任务确认门槛判断，从不用于选择能力。
4. `v1_route` 节点是纯字符串等值分支，节点自带注释"模型不参与选择，分支只看确定性 effective_route"。
5. 唯一的非用户指名选择是位置性的：`NEXT_SKILL` 表把五个槽位串成固定后继链（Matrix→Campaign→Content Brief→Stage1→Stage2→无），是**更纯粹的 Skill 路由**（固定流水线后继表），不是经营目标驱动。
6. 无任何能力注册表：全仓 grep 不到 registry 文件、每能力输入合同声明、`allow_direct_entry` 标志或降级策略字段——唯一存在的"元数据"是四个硬编码在同一个代码节点里的字典（`SKILL_TO_SLOT`/`UPSTREAM_OF`/`NEXT_SKILL`/`DOWNSTREAM_OF_SLOT`）。

**这与产品合同自带的仓库预registered事实完全吻合**（合同原文即写"只有 Skill 路由，没有经营目标路由……没有任何字段承载主目标、次目标、优先级或不可牺牲条件"）——本次基于当前 HEAD 独立复核，结论一致，判定 `CURRENT`（合同这条自述仍然真实）。

### 三.2 主目标/次目标/优先级/不可牺牲条件/账号阶段/表达裁量/期望发布量/实际产能 —— 全部 `MISSING` 结构化承载

| 字段 | 当前承载方式 | 判定 |
|---|---|---|
| 主目标 | 单个自由文本字符串 `draft_task.goal`（≤400 字），未解析 | `CURRENT`（仅作为不透明字符串）／`MISSING`（作为结构化字段） |
| 次目标 | 全仓零命中；仅作为冻结 Campaign Prompt 里"其他诉求降为支撑目标"的自然语言指令 | **MISSING** |
| 优先级 | 全仓零命中，无字段、无枚举、无排序结构 | **MISSING** |
| 不可牺牲条件 | 无一等字段；最接近的是 `compile_prod.constraints`——从 Brief 文本按固定关键字做字符串抓取拼接，只在生产链内部可见，路由和 Matrix/Campaign 完全看不到 | **MISSING**（结构化）／文本抓取拼接（生产链内部专用） |
| 账号阶段 | 全仓零命中（合同定义的六阶段一个都不存在） | **MISSING** |
| 表达裁量 | 全仓零命中作为字段；合同 §八 的 8 项内容只以**夹具散文**形式硬编码进 Matrix/Campaign/Brief 的 Tool Prompt | **MISSING——硬编码进夹具文本，非真实结构化输入** |
| 期望发布量 | 全仓零命中，任何形式 | **MISSING** |
| 实际产能 | 只以夹具散文形式存在（"七天内可投入的人员与产能"），烘进 42,972 字的 Campaign Tool Prompt | **MISSING——硬编码进夹具文本** |

**结构化状态机实际承载的全部内容**：9 个会话变量（任务快照 + 5 个产物槽位 + 1 个运行态槽位）。`task_snapshot_json` 必需 13 键，业务语义相关的只有两个目标形字符串（`draft_task.goal`/`confirmed_task.goal`）。`production_runtime_state` 只有 5 个键，全部由关键词硬匹配从原文抽取（`production_profile`/`duration_band`/`platform`/`brief_id`/`realization_manifest`），"认不出就留空，宁可再问一次不猜"。

**两处额外发现的 Schema/运行态不一致**：① `V1_TASK_SNAPSHOT_SCHEMA_v0.1.json` 只声明 3 个产物槽位，实际状态机是 5 槽（与 §八.2 持久化侧发现的 STALE 结论互证，同一事实两个独立子任务各自发现）；② `compile_prod` 函数签名接收 `matrix_artifact`/`campaign_artifact` 两个参数，但函数体内从未引用——Matrix/Campaign 的产出能否真正传导到生产链，只取决于 Content Brief 是否恰好把内容抄了过去（`NOT_VERIFIED`，疑似死代码）。

### 三.3 能力选择是否线性锁定？—— **是，硬锁定，与合同直接冲突**

`UPSTREAM_OF` 字典把五个槽位串成单向链（`matrix→None, campaign→matrix, content_brief→campaign, production_stage1→content_brief, publishing_stage2→production_stage1`），`gate_reason()` 确定性强制：上游必须存在、非 STALE、且恰好是 `USER_ACCEPTED`，否则撤销授权、强制转人工决策路由。**无旁路、无备选输入分支、无等价表**。唯一 `None` 上游是 Matrix。

这与合同 §四能力表（八项能力全部标"否"/"可直接进入"）、§四合法组合示例（"用户已有明确选题：直接进入 Brief 或 Creative Script"等）、§十八"必须废止"清单（点名"六个能力只能线性调用"）**三处直接冲突**——CLAUDE.md §3 已宣布线性假设废止，但 DSL 状态机尚未跟上，这是**文档已表态、运行时未跟进**的 CONFLICT，不是已解决项。

### 三.4 是否存在合法直接入口？—— 仅在主链之外

主 Chatflow 内除 Matrix 外无法直接进入任何能力；但 6 个独立 Dify App（Creative Script／Production Director／Publishing & Packaging／三个决策链 Tool App）均可被脱离主链直接运行，且均有独立跑通证据。**但这只证明"操作员可以从 Dify 控制台/API 手动驱动子应用"，不证明"用户对话可以直接到达该能力"**——独立 App 要求调用方手填 11-12 个槽位，普通用户对话触及不到。

### 三.5 是否依赖特定句式/重复确认？

**任务确认层的句式依赖已被证实修复**：三次真实历史失败运行显示旧版本要求用户换成系统指定句式；`TASK_CONFIRMED_FROM_OWN_WORDS_NO_SEPARATE_GOAL` 修复后，A-0 证据证实原句式可直接生效、未再被要求换句式。

**仍然残留的句式/关键词依赖**：① 12 字符硬阈值（`MIN_SAME_TURN_GOAL`）——足够清晰但简短的表达仍会被拒；② `extract_runtime()` 靠字面量列表做关键词匹配（约 20 个时长词、10 个平台名等），列表外的表达一律"认不出就留空"；③ Skill 选择本身依赖固定关键词表，不命中就是 `NONE`，无法选择任何能力。

**重复确认循环**：任务形成/确认层的多轮口令仪式已消除（一句话可一次性完成表态+确认+授权），但**每个能力产出后仍强制要求一次显式 `USER_ACCEPTED`** 才能进入下一能力——线性锁 + 逐级确认叠加，跑完整条链最少需要 5 次接受动作。存在防重复的设计（`open_threads` 每条侧问只出现一次；`EXECUTE_REQUEST` 兜底最多追问一个真正阻塞问题）。

### 三.6 A-0～A-4 与失败兜底：全部 `CURRENT`，且均有真实 Dify 对话证据（`V1_DIALOGUE_ORCHESTRATION_REPAIR_001_EVIDENCE.md`）

| 行为 | 判定 | 机制要点 |
|---|---|---|
| A-0 自然语言理解 | CURRENT | `v1_shadow` 输出 10 个必需字段，模型仅作建议，`v1_state` 做确定性校验与拒绝未知字段/非法枚举 |
| A-0/A-1 任务确认与授权 | CURRENT | 两条独立路径（显式确认 / 同轮口头即视为确认），授权与 `task_revision` 绑定，执行后即消费 |
| A-2 一轮多诉求 | CURRENT（机制）／NOT_VERIFIED（该证据轮次实际走的是另一字段） | `side_question`→`open_threads`，每条最多展示一次；A-2 证据显示当轮走的是 `change_target_object` 而非新字段本身，新字段仅有单测覆盖（10/10） |
| A-3 撤销最近一次接受 | CURRENT | `REVOKE_LAST_ACCEPTANCE`，撤销深度精确为 1，级联 STALE，真实运行证明两个独立槽位互不干扰 |
| A-4 失败 fail-open | CURRENT | 状态патch非法时整体拒绝、保留旧快照、强制转 `DISCUSS`、禁止编造失败原因；两个真实子场景（DeepSeek 结构违规 / 无可撤销目标）均有独立证据 |
| Tool 执行失败兜底 | CURRENT（5/5 业务 Tool）／**CONFLICT**（对话理解节点 `v1_chat_llm` 无任何 `error_strategy`） | 五个业务 Tool 全部有 fail-branch+重试；对话节点是已登记的开放缺口 G-12，2026-08-21 曾真实发生 DNS 故障导致用户看到 Python 报错 |

### 三.7 本节额外发现的独立 CONFLICT（不属五问但与路由/任务上下文直接相关，供 §九汇总）

- **夹具文本硬编码进通用代码节点**：`compile_prod`/`compile_pub` 两个"通用"代码节点内嵌了针对特定 `brief_id="BRF-SUHE-001"` 的约 1,400 字追加事实块，与合同 §十六"通用节点不依赖夹具文本"直接冲突。
- **行业硬编码进核心链**：`subject_domain` 由"试穿"+"门店/商品"关键词命中判定为"服装/门店零售"字面量，与合同 §十七"核心链不得硬编码服装/电商/门店"直接冲突，且发生在两处编译节点里（生产链、发布链各一处）。
- **决策链有版本防护、生产链没有**：见本节开头——已独立记入 §九汇总。

---

## 三、路由与任务上下文（A4）

> 待并行子任务 `cap-cards-a4a5` 回填。

---

## 四、六 Skill 价值耦合分档（A6）

> 核验方式：六份 Skill 全文逐字通读 + 与 `df94ed1`（`AO-EP00-HISTORICAL`）md5 比对 provenance。

**Provenance（决定历史结论是否仍适用的前提）**：`writing-creative-scripts/SKILL.md`（388 行）与 `directing-content-production/SKILL.md`（416 行）相对 `df94ed1` **逐字节 IDENTICAL**；`packaging-content-for-release/SKILL.md` 相对 `df94ed1` **CHANGED（357→555 行，+198 行）**；决策链三份 Skill 正文全部 **IDENTICAL**。388+416+357=1161，与合同引用的「逐字通读 1,161 行」精确吻合——证明该历史数字只覆盖了 `df94ed1` 时点的 PP 旧版，PP 现版未被历史结论覆盖过。

### 四.1 六份汇总

| Skill | Q1 长期价值唯一目标 | Q2 贬低/改写增长目标 | Q3 因目标激进化/替用户代决 | Q4 硬编码业态/平台/角色 | 风险分档 |
|---|---|---|---|---|---|
| Matrix Architect v0.1.2 | 否，且反向（`:170` 把「长期价值」列为**禁用抽象词**） | 否（全文无增长/涨粉/流量/GMV 词面，但也无接口） | 否 | **是**——`:184-186`「商品负责人／试穿搭配陈列／门店销售熟客」进**规则本体**（非示例块） | **NEEDS_PARAMETERIZATION** |
| Campaign Orchestrator v0.1 | 否（但主目标**类型**被锁定为认知变化，`:110`） | **是·3 处**：`:107+:110`（到店/成交/复购降为「经营结果」层，不得并列主目标）、`:120`（禁用增长语言表述）、`:207+:209`（互动/播放/点赞剥夺决策权） | 不自动激进化，但表达刻度单向锁死、Skill 持不进入制作的否决权（`:124/:291/:299`） | 平台显式中立（`:90/:213`，合规）；业态轻度 | **ROLE_CONFLICT** |
| Content Brief Architect v0.1 | 否 | 1 处：`:157`「覆盖面不是价值，判断深度才是」 | 不自动激进化，持不发否决权（`:238`） | 六份中最中性（近乎为零） | **ROLE_CONFLICT**（架构级：见四.3） |
| Creative Script | **零处** | 结构上无接口可改（12 项输入槽位无经营目标字段）；但 `:162` 无条件淘汰「3 个秘密／90%的人不知道」等起号钩子模板 | 否，**全仓最强反自动激进化**（CS-2 张力≠冲突/反转/悬念）；剧情由 `SETTING` 明确支持而非禁止 | 逻辑层已参数化（`subject_domain`/`platform` 缺失即「不加载」）；**示例层**服装偏斜（规范文本仅 1 处） | **NEUTRAL**（价值轴）／NEEDS_PARAMETERIZATION（候选数+句式黑名单） |
| Production Director | **零处** | **零处**（无经营目标字段） | 否；但 `:123`「今天补拍/生成画面重演过去事件」缺 `SETTING` 例外出口，与 `:26`/CS`:223` 的能力承诺有张力 | **规范性文本内**有服装（`:280/:298`「试穿视频/商品图」）与五行业物理条件（`:246/:247/:252`）泄漏 | **NEUTRAL**（价值轴）／NEEDS_PARAMETERIZATION（业态泄漏+固定候选数） |
| Publishing & Packaging | **零处** | `:381` 播放量≠创意质量属归因纪律（不构成）；**`:320-323` 新增**业务动作封禁清单（「关注看答案」等涨粉/转化动作），受 `cta_contract` 门控但 `:112` **默认值即「无 CTA」** | 否，激进度由实拍 `realized_payoff` 封顶（`:235`），非经营目标 | 平台名在 `references/`（3 家硬编码）；**判断层已机制化**（`:219` 按入口形态非平台名分类）；账号定位显式可换（`:111`） | **NEEDS_PARAMETERIZATION** |

### 四.2 与产品合同 §十八 历史结论（`AO-EP00-HISTORICAL @ df94ed1`）的显式对照

> 合同原文（§十八）要求：「该结论只是历史证据，不得冻结成永久事实；施工前须在当前 HEAD 上复核，不得直接引用」——以下是复核结果。

| 历史主张 | 独立复核结论 | 标签 |
|---|---|---|
| 内容生产链三 Skill「逐字通读 1,161 行，零处长期主义/反流量硬编码」 | CS/PD 两份 md5 与 `df94ed1` 完全一致，**零处长期主义确认**；但 PP 已 `+198` 行，1,161 行数**只覆盖旧版 PP**。当前 HEAD 三份合计 1,359 行 | **STALE（PP 部分）** |
| PP「零处」 | **推翻**：`:320-323` 新增业务动作封禁清单（df94ed1 时不存在），且门控参数 `cta_contract` 默认即「无 CTA」——未显式授权时默认落在禁止转化一侧 | **CONFLICT + STALE** |
| 决策链「价值耦合 5 处，分三档」 | 三份决策链 Skill 锚点仍 IDENTICAL、可直接复核，但**计数偏低**：① 历史清单把一条生产链锚点（PP `cta_contract`）计入了「决策链 5 处」，与「生产链零处」自相矛盾；② 漏掉 Campaign 目标层降级的真正条款（`:107+:110`，历史只记了表述层的 `:120`）；③ 漏掉 Campaign 流量信号决策权剥夺（`:207/:209`）与 Content Brief 的 `:157`；④ 历史 §7 建议「Matrix 建号门槛走旁路」，但三档清单里**没有对应锚点**——建号门槛（`:47/:64`）被给了处置建议却未被计数 | **CONFLICT（决策链侧计数不完整，非方向性错误）** |

### 四.3 独立发现：Content Brief 与 Campaign 的架构级职责冲突（本次复核中最硬的一条）

`Content_Brief_Architect_v0.1.md:9,11,50-66,91,244` 把 Campaign 正文硬编码为**唯一合法上游**且**硬阻断**（`:91` 硬阻断清单第一项即「已被接受的上游 Campaign 决策」缺失→只输出 `INPUT_INSUFFICIENT`）。但 CLAUDE.md §3 与已接受的上位合同已认定「Content Brief 的合法上游不止 Campaign」「八项能力可直接进入」。**结果：用户直接进入 Content Brief（合同允许的合法入口）在当前 Skill 正文下会必然收到 `INPUT_INSUFFICIENT`，这是运行时可复现的阻断，不是文档措辞问题。** 治理文件 `CONTENT_BRIEF_CONTRACT_v0.1.md:10-12,18` 已自认「唯一入口假设已废止」但同时明写「解除 Campaign 唯一上游依赖属于 Skill 正文改动，须等预检与新授权，不在本轮执行」——**即合同文档已经知道这处冲突，且明确留给本次预检之后处理，不在 M0 范围内修。**

### 四.4 A16 邻接漂移：文档已更正、Skill 正文未同步改的候选数量条款

`CONTENT_BRIEF_CONTRACT_v0.1.md:27` 明文「本文件是**治理文件，不是模型输入**，不进入 Skill、不进入 Dify Prompt」——即文档里的口径更正块在运行时**零效力**，只有 Skill 正文决定行为。核验发现：

| 更正块声明 | Skill 正文当前状态 | 更正块是否已自认覆盖 |
|---|---|---|
| 验收标准/构建规范文档：「一切固定候选数量表述已被取代，不得硬编码固定数量」 | `writing-creative-scripts/SKILL.md:57,286,372`「3 个高差异方向」仍在 | **是**——文档已点名 CS-1，明写「不在本轮改 Skill 正文」 |
| 同上 | `directing-content-production/SKILL.md:342`「3 套高差异方案」、`packaging-content-for-release/SKILL.md:444`「3 套路线」仍在 | **否——本次新发现**，两处未被任何更正块点名覆盖 |

PP 内部并存两种相反的候选计数原则可作佐证：同文件 `:171,190,449-452`（`titles[]`）已改为「候选数由可用入口类型数决定，不设上下限」，但 `:444`（`packaging_routes[]`）仍硬编码「3 套」。

### 四.5 跨六份的结构性发现：输入不足策略两条链方向相反

决策链三份（Matrix/Campaign/Content Brief）在信息不足时走**整任务硬停**（`Matrix_Architect_v0.1.2.md:25-34` 明确「不得附加建议、询问、结束语」，六类信息缺一即整任务停摆、**无降级通道**）；生产链三份走**产出能产出的部分**（`writing-creative-scripts/SKILL.md:361`「不要输出空结果，也不要用一句『信息不足』打发」）。CLAUDE.md §4「资料不足时不得整任务拒绝……阻止的是无依据的具体主张，不是整个任务」与**生产链一致、与决策链（尤其 Matrix）方向相反**。

---

## 五、创意锦标赛（CS-1）与 Content Brief 接缝（A7）

### 五.1 CS-1 不是独立组件，是嵌在 Creative Script Skill 正文里的一节 Prompt

CS-1（"创意方向的差异必须是机制差异"）只是 `writing-creative-scripts/SKILL.md` 的一节，逐字节嵌入 Creative Script Tool 的 system prompt——**无独立 app_id、无 Tool 名、无节点、无路由槽位、无输出变量**。主链状态机的 5 个产物槽位（matrix/campaign/content_brief/production_stage1/publishing_stage2）里没有任何一个是锦标赛。全仓 grep "锦标赛/tournament/CS-1" 只命中合同、账本和该 Skill 自身文件。这与产品合同自己的记载完全一致（合同原文："它当前寄居在 Creative Script 的 CS-1 内部，不是一份独立 Skill"）。

**机制真实存在**：3 个高差异方向（数量硬编码）、5 条结构轴（核心矛盾/叙事发动机/人物关系/信息释放顺序/视觉前提）、"任两方向至少 3 轴不同"的机械判据、明确的"伪差异"清单（换标题/换语气/换案例等不算）。**选优机制不是独立评分器**，是同一次 LLM 调用自己写出选中方向并说明理由（真实运行证据：模型自己数轴差异数、并按 5 条具名判据说明选择理由）。

### 五.2 候选是否到达用户——两层答案，且两层结果相反（本节最锋利的发现）

| 层 | 3 个方向是否出现 | 证据 |
|---|---|---|
| 完整内部产物（`creative_script_artifact`） | **是**——3 个方向连同各自 5 轴描述全部保留 | 真实运行产出 7,416 字 Final，三个方向 A/B/C 逐一列出 |
| 用户交付块（`user_delivery`，实际交给执行人员的那份） | **否——被显式抹除** | Tool Prompt 明文"**只保留最终采用的那一个版本。**不写候选方案、不写推演过程、不写淘汰了什么"；且这是**验收硬闸**，真实运行的用户交付包逐词核查过"方向/候选"字样 **0 次出现** |

**结论：锦标赛机制在系统内部真实运行过，但其产出候选被确定性地在到达用户之前抹除。** 这与合同自己预先登记的两条缺口完全吻合（①只在内部三方向互比，不与外部平台内容比较；②Skill 自行选定 1 个深化，未输出候选交用户裁决）——本次基于当前 HEAD 的独立复核**确认两条均属实**。（同类两层模式也出现在 Publishing & Packaging 的标题候选上，属并行现象，非 CS-1 本身。）

**外部同质化比较**：`MISSING`。比较严格限定在单次 LLM 调用内的自比，无任何联网/搜索/知识库节点，参考资料加载是确定性模板查表（"不使用知识库，不由任何 LLM 决定加载范围"）。合同 §七/§G 明确要求"外部同质化检查优先于账号自身重复检查"——当前完全不存在。

**CONFLICT（已被合同自己登记为暂缓项）**：CLAUDE.md §4"候选数量不得硬编码"与 CS-1 硬编码"3 个"直接冲突；`context_pack.md` 已明确把这条差异划入本轮"口径更正但不改 Skill 正文"范围内——即**这是一个已知、已登记、本轮刻意不修的 CONFLICT**，不是新发现的漏项。（对照：Publishing & Packaging 的标题候选 PP-1 已经改成"候选数由可用入口类型数决定"，说明同类问题在该 Skill 内已被修过，CS-1 尚未跟进。）

### 五.3 Content Brief 的实际上游依赖——文档已更正、DSL 与 Skill 均未跟进

`CONTENT_BRIEF_CONTRACT_v0.1.md` 的更正块明确写"Matrix→Campaign→Content Brief→内容生产作为唯一入口的假设已废止"、"Content Brief 的合法上游不止 Campaign"，**同时自己声明"解除 Campaign 唯一上游依赖属于 Skill 正文改动，须等预检与新授权，不在本轮执行"**——这是一处主动承认的、有意延后的 CONFLICT。

**运行时验证：三层都还锁死在 Campaign 上**：① 主链状态机的 `UPSTREAM_OF["content_brief"]="campaign"` 与 `gate_reason()` 硬阻断，无任何旁路分支；② Tool 调用参数模板直接要求"已被用户接受的上游 Campaign 决策包"；③ Skill 正文自 `0fbba9e`（早于本次更正）起未再改动，仍把 Campaign 写死为唯一合法上游。**真实运行已证实这一锁定会生效**：一次真实的 Negative Probe（30 字用户直接指名选题请求）在 8.6 秒内被拒，返回 `INPUT_INSUFFICIENT`，明确写"当前仍可安全完成什么：**无**"。

**部分例外（下游边界确实是开放的）**：生产链 Stage 1 把 `content_brief` 当作一个普通自由文本 Start 变量接收，**从不调用 Content Brief App**——所以任何 Brief 文本（粘贴的、历史的、手写的）都能不经过 Campaign 进入生产链。仓库里**每一次**生产链真实运行走的都是这条路径（夹具文本或冻结归档 Brief），从未有过一次真正的 Campaign→Brief 实时调用。**结论**：Content Brief 作为一项"能力"仍被锁定在 Campaign 之后；但作为生产链的"输入边界"，Brief 文本本身早已可以从任何来源直接进入下游——这是两件不同的事，合同/Skill 层锁的是前者，未锁后者。

另发现一处夹具耦合：主链"编译生产输入｜九槽位"代码节点里硬编码了 `ADDENDUM_BRIEF="BRF-SUHE-001"` 及四条补录事实全文——只对这一个特定 Brief ID 生效，与 §三.7 已发现的行业硬编码是同一类问题（通用代码节点里嵌了夹具专属逻辑）。

---

## 六、生产链现状（A8）

> 本节先对既有证据文件做了一轮"仍然成立吗"的复核（而不是直接照抄结论），复核方法是重新计算文件里记的哈希/字符数并与仓库当前值比对。绝大多数复核通过；少数几处发现"证据文件记录的结论已被后续版本取代"，已在下文标注 `STALE`。

### 六.1 CS/PD/PP 独立可调用性——PP 与合同承诺不符

CS 与 PD 均可完全独立调用（11/12 个必填输入全部用户可填，无父流依赖），且有真实独立运行证据（505.7s/559.6s，全部成功）。**PP 不完全独立**：其 Start 节点同时要求 `cs_final` **和** `pd_final` 两个必填字段——合同 §四"用户已有成片信息，只需要发布包装：直接调用 Publishing & Packaging"当前**不可满足**：无法仅凭"成片信息"调用 PP，必须同时提供 PD 产物文本。**CONFLICT，已记入 §九**。

### 六.2 核心接口的真实当前合同

- **`content_promise`**：CS 产出，明确"下游不得静默改写"；PP 只读继承，PRE 模式下用它做承诺上限并全部标草案——接口边界清晰，无发现问题。
- **`realization_plan`（拍摄前）vs `realization_manifest`（拍摄后，是产出不是输入）**：两者语义边界清晰，且被真实运行验证——PD 产出经检查从未出现过"manifest"字样（两次独立运行均确认，只产出 `plan`）。
- **PRE/MIXED/FINAL 三级判据**：`packaging-content-for-release/SKILL.md`（v0.6.1 起）是**三级依次判**——第一级不成立才看第二级，第二级不成立才是第三级；**决定 mode 的不是"有没有缺口"，是"缺口有没有被处置完"**。三个档位均已被真实运行验证到，且有一个非常有力的对照实验：**同一套上游产物、同一套判据，只因某一个 beat 的处置状态一格之差，就从 MIXED 落到 FINAL**——证明判据是真判别的，不是摆设。
  - **CONFLICT（已发现，未被任何既有文档标注）**：`CONTENT_PRODUCTION_RUNTIME_CONTRACT_v0.1.md` §4.3"模式判断"至今仍是旧的**两条件覆盖率判据**表（全部覆盖=FINAL/部分覆盖=MIXED/无 manifest=PRE），自创建以来从未被编辑过，**未跟上 Skill v0.6.1 的三级判据修订**——运行合同文档本身已经 STALE，会给读者错误答案。
  - 由此推出：`CONTENT_PRODUCTION_FINAL_CHAIN_RUN_001.md` 记录的"PP 推导出 MIXED 而非 FINAL"结论是 **v0.6（旧版）判据下的产物，已被 v0.6.1 取代**——该轮的 mode 结论标 `STALE`，但其"realization_manifest 接口设计"相关发现仍然 `CURRENT`。
- **Returns（回改）结构化出口**：真实实现，纯字符串切分适配器（无第二个 LLM），"解析失败绝不当成空数组"；CS/PD 的两个回改标签结构性恒为 NONE（有实测代价：强迫 CS 评估两个结构上不可能的标签曾导致三次连续撞 600s 超时，已修复为恒 NONE）；**第一版明确不自动回环、不自动接受、不自动重跑，每次重跑必须由人重新发起**——这是设计选择,不是缺失。
- **语义事实核验节点**：真实存在两层，**必须分开看，不能混为一谈**——① PP 子流内的四道确定性闸（fact_id 全称/无内部过程语言/假绿检测/CTA 泄漏检测），父流只透传不代为放行；② 独立增设的 qwen3.8-max 只读语义节点，只吃 4 项输入（用户交付块、10 条完整 fact_refs、cta_contract、realized_payoff），**明确不采信 PP 自己"已核实/已删除"的自述**。已验证：负向探针正确拦截、正向探针零误报、十项非衰减判据 10/10。**已知边界（合同自己写明）**：证据范围就这 4 项输入，**不含 Content Brief**——account 结构类陈述判不稳，是否扩大核验范围目前是刻意搁置的开放裁决。
- **用户交付投影**：两层拆分（完整 Artifact + 用户交付块）在切分顺序上有保障——交付块是在原有回改切分**之前**先摘走，正文其余部分不受影响；24 项对抗性自测全过。

### 六.3 局部修改与下游失效——决策链有、生产链没有

**下游失效机制**：决策链侧**已实现**（每槽位的"产物落定与 STALE 传播"代码节点 + 撤销接受级联），但**只有离线单元测试覆盖**，未见过一次真实 Dify 对话里正向触发级联 STALE 的运行证据（唯一一次真实撤销测试验证的是"不该级联的没有级联"，不是"该级联的确实级联了")——`NOT_VERIFIED`。**生产链侧完全 MISSING**：运行合同定义了正确的语义（基于内容哈希判断"是否真的改了"，而非"是否发生了回改"），但全仓 `content-production/` 下的工作流 YAML 里 `STALE` 字符串零命中，段间控制器的文档字符串直接自陈"不给任何产物盖 USER_ACCEPTED、不因产生回改而标下游 STALE"——根因是生产链 Stage1/Stage2 是无状态工作流调用，产物只活在聊天状态机的会话变量里，没有独立的产物状态存储（对应 §八已发现的 G-05 持久化缺口）。

**局部修改（只重跑受影响单元）**：**完全 MISSING**，且只是愿景，不是半成品。全仓没有任何比"整个 Skill 重跑"更细的重跑粒度——回改接受后触发的是 Creative Script **整体重新运行**，不是逐 beat 局部重算；STALE（凡实现处）的粒度是整槽位/整产物，从未有 beat 级。**从未有一次真实运行走完"回改→接受→重跑→哈希比对→STALE"全周期**——历史记录里回改数量要么是 0，要么被记录后主动选择不处理（该轮停在人工评审出口）。

### 六.4 失败恢复——基础设施故障已证实可恢复，内容驱动的失败恢复未实现

**已证实的真实恢复**：① 一次真实 BLOCKED（CS 两次 600.2s 被杀死、零产出）→ 经 Founder 裁决降低模型参数 + 重新绑定三个 Tool 版本 → 下一轮 DONE，六项验收全过，9.5 分钟跑完（**这不是自动恢复，是人工介入+参数调整后的重跑**）；② 一次真实链路中段 TLS 中断，重试一次即成功，上游产物未被重新生成，失败记录原样保留。

**代码与文档口径不一致（CONFLICT）**：段间控制器文档字符串自称"只针对基础设施失败重试"，但实际代码逻辑是"只要产物字段缺失就重试"，不区分失败原因——目前没有被真实运行触发过，但守护条件写了却没真正执行到位。

**已知但未处理的静默陷阱**（与 §七.2.1 Dify 扫描发现的"Tool 版本钉版本"是同一机制）：Dify 把 Workflow Tool 版本钉在绑定那一刻，子应用重新发布不会自动带动父流，无报错——这正是当年 P05 阶段"手动传参卡在 11 个字段、修复后变 12 个"故障的根因，仓库证据文件已完整记录。

**MISSING**：段间控制器目前只能带 PRE 模式的 9 个参数直通，**不支持 `realization_manifest`**，MIXED/FINAL 两档目前只能直接对 Stage 2 父应用发起，绕开控制器——这是控制器侧的真实功能缺口（集成主链本身是支持传 `realization_manifest` 的）。

### 六.5 仓库证据已经证明什么，什么仍然真正未证

**已证明（可信引用）**：最小夹具全链跑通（六项验收全过，9.5 分钟）；完整 Content Brief 全链跑通（九项运行层验收全过）；跨阶段交接为字节级精确（三方重算比对，非仅哈希）；PD 从未产出过伪造的 manifest；PP 自主推导 mode、三档均已被真实触发且证明有区分力；回改/建议解析确定性、无第二 LLM；两层输出拆分确定性且切分顺序正确；四道确定性闸真实拦截过；语义核验节点 10/10 非衰减且抓到过确定性闸漏掉的两处真实编造；两条硬性运行时限（1200s 父流/600s 单次 LLM）均从源码而非猜测确认；基础设施类失败的恢复机制真实跑通过。

**仍然 NOT_VERIFIED / MISSING（不得据此声称已完成）**：全部素材至今仍是 `SIMULATION_ONLY`，从未用过真实拍摄素材；内容质量/可发布性从未被声称过，每一轮 mode 试跑都以 PARTIAL 收尾，最近两轮（P05R2/P05R3）都是被拦下、没有生成 v0.3 交付包；`FINAL` 档"从判定到通过事实闸"全流程干净跑通从未发生过；生产链侧下游失效机制完全没有代码实现；回改→接受→重跑→哈希核对全周期从未真实走完；局部（单元级）重跑没有任何实现；**集成主链的生产分支（production_stage1/publishing_stage2）本身没有一次专门提交的完整运行记录**——仅有的间接痕迹是一段已存在会话快照里四个槽位 `USER_ACCEPTED`、发布包槽位 `FAILED`，Brief→Stage1→Stage2 整条集成路径整体判 `NOT_VERIFIED`；全部计时数据都是单次观测，不构成性能结论；40 类自然语言测试目录里只有 10 类真正跑过多轮真实对话，单元测试不经过 Dify 运行时。

---

## 七、仓库—Dify—部署一致性（A3 / A9）

### 七.1 主 Chatflow（已由本任务主线核验，NON_PRUNABLE 项目样例）

| 项 | 值 |
|---|---|
| Dify App | `id=310ddfcf-e0fb-4211-af98-3d101725e07a`，显示名 `"DIYU Demo V1 Main Chatflow v0.1"` |
| 已发布 workflow | `id=055b7bbe-172f-4456-8459-951ae3e14ce7`，`updated_at=2026-08-24 07:24:31` |
| 草稿 vs 已发布 | 字节长度均为 249047，**完全一致**（无未发布的挂起改动） |
| 节点数 | 56（与 `PROJECT_INDEX.md` 声称「56 节点」一致） |
| 实际对应仓库文件 | `decision-chain/workflows/DIYU_DEMO_V1_FULL_CHAIN_CHATFLOW_v0.2.yml`（**v0.2**，非同目录 v0.1 文件）—— 经节点标题唯一性比对确认（如 `"产物落定与事实核验出口｜发布包"` 仅在 v0.2 文件命中；语义事实核验相关节点仅在 v0.2 与实盘图中出现，v0.1 文件零命中） |
| **发现的漂移** | Dify 应用**显示名称**仍为 "v0.1"，但**内容**已是 v0.2——**命名未同步，非内容漂移**。判定：**STALE（仅命名），非 CONFLICT**。建议 Founder 知悉，不属于本任务施工范围，只登记 |

### 七.2 全部 25 个 App 的核验（含主链，交叉复核一致）

> 核验方法：节点级 payload 指纹（`sha256(json.dumps(normalize(node.data)))`，剥离画布坐标等无语义键），逐 App 与全部 23 个含 graph 的仓库 YAML 比对——**不按名称/节点标题假设匹配**。**重要方法论发现**：`MATRIX_QWEN_V0_1`/`_V0_1_1`/`_V0_1_2` 三者、6 个 `TEST_*`、3 个 `V1_TOOL_*` 分别共享完全相同的节点 id 与标题，仅按 id/标题匹配会把这 9+ 个 App 全部**误判为 1.000 匹配**；只有 payload 指纹能真正区分。

**总计：25 个 App（比初步清单多 1 个）· 3 处仓库↔实盘内容漂移 · 1 处待发布的语义改动 · 3 处纯画布性差异（非漂移）· 5 个从未发布过的 App · 3 个实盘孤儿 · 2 个仓库孤儿 · Tool 版本绑定 0 处过期。**

**三处真实漂移**：

| 编号 | App | 差异 | 方向 |
|---|---|---|---|
| **D1** | Publishing Packaging v0.1 | `returns_adapter` 代码节点：实盘比仓库 YAML 多 8 行（豁免"引用行"误判为假绿的逻辑），仓库文件最后改动于 `8890ceb`（"PP v0.6.2 事实纪律与四道假绿阻断闸落地"），实盘发布于其后 | **实盘领先仓库**——有人在画布上改过后未导出回仓库 YAML |
| **D2** | Creative Script v0.1 | `skill_llm` 节点 `reasoning_effort` 三方不一致：**实盘已发布=`low`**（实际生效值）／**实盘草稿=`max`**（待发布未生效）／**仓库 YAML=`max`**。同类三 Skill 对照：Production Director 与 Publishing & Packaging 实盘均为 `low`，仅 Creative Script 的仓库文件停留在 `max`。`FIXTURE_RUN_002` §1.1 记录过三份 Skill 统一 `high→low` 的裁定，仓库 CS 文件未收到这次修改，且现在又有一个未发布的草稿改回 `max` | **CONFLICT**：仓库、已发布、草稿三者互不一致 |
| **D3** | `DIYU_DEMO_CAMPAIGN_QWEN_V0_1`（**从未发布**） | 名称含"QWEN"，但实盘草稿模型已是 `deepseek-v4-flash`（`max_tokens=384000`），仓库 YAML 仍是 `qwen-max`（`max_tokens=8192, temperature=0.2`） | 应用名称与内容不符；因从未发布，**无实际运行影响**，但历史资产命名易造成误判 |

**5 个从未发布的 App**（`apps.workflow_id IS NULL`，只有 `draft` 版本，因此**不可能**被绑成 Workflow Tool，属纯画布历史遗留，无运行影响）：`DIYU_DEMO_CAMPAIGN_DEEPSEEK_V4_FLASH_COMPILE_V0_1`、`DIYU_DEMO_CAMPAIGN_QWEN_V0_1`、`DIYU_DEMO_MATRIX_QWEN_V0_1_2`、`DIYU_DEMO_MATRIX_QWEN_V0_1_1`、`DIYU_DEMO_MATRIX_QWEN_V0_1`。

**3 处纯画布性草稿/发布差异（明确非漂移）**：Creative Script Reference Projection Probe、TEST_CONTENT_BRIEF_NOSKILL、Content Brief DeepSeek V4 Flash v0.1 三个 App 的草稿/已发布 md5 不同，但逐节点比对后差异仅为 `viewport`/`height`/`width`/`selected` 等画布状态键，**零 Prompt／模型／代码／变量改动**。

**孤儿资产**：
- **实盘有、仓库无对应文件（3 个）**：`DIYU Demo V1 Sandbox Selftest`、`DIYU Demo V1 Tool Probe content_brief`、`DIYU Demo V1 Tool Probe matrix`——全仓 grep "Selftest／Tool Probe／tool_probe／探针" **零命中**，仓库对这三个 App 的存在**完全不知情**。其中两个 Probe App **持有绑定生产 Tool Provider 的真实 Tool 节点**（`diyu_v1_matrix_architect`／`diyu_v1_content_brief_architect`），是**可执行但未被任何文档记录的生产入口**——本身即一处需要 Founder 知悉的治理缺口。
- **仓库有、实盘无对应 App（2 个）**：`DIYU_DEMO_CAMPAIGN_QWEN38_FALLBACK_COMPILE_V0_1.yml`（从未部署过，与任何实盘内容最高只有 4/6 payload 匹配）；`DIYU_DEMO_V1_MAIN_CHATFLOW_v0.1.yml`（已被 v0.2 取代，与主链实盘图仅 30/56 匹配，判定为历史留存文件，非部署缺口）。

**良性差异（预先排除，非漂移）**：CS/PD/PP 三份 Skill 实盘系统 Prompt 均比仓库 `SKILL.md` 多出恰好 110 字符——是固定追加的「本次运行注入的参考文件片段」引用投影占位块，仓库 YAML 与实盘一致内嵌，**不是漂移**。

### 七.2.1 Tool 版本绑定专项核验（「子应用改参数发布 ≠ 父流 Tool 自动跟着变」风险）

`content-production/evidence/CONTENT_PRODUCTION_PRE_CHAIN_FIXTURE_RUN_002.md` §2.3 文档化的风险：Workflow Tool 在绑定时把子应用版本"钉死"（`tool_workflow_providers.version`），子应用后续改参数重新发布，父流的 Tool 绑定**不会自动跟随**，且无报错。

**核验结论：全仓 8 个 Tool Provider（覆盖全部 25 个实盘 App 中出现的全部 10 处 `type: tool` 节点，无遗漏）当前 8/8 CURRENT，零过期绑定。** 逐一核对"绑定钉住的版本"与"子应用当前实际已发布版本"，全部时间戳一致（Matrix/Campaign/Content Brief 三个决策链 Tool 钉在 2026-08-21 07:04 首次发布版；Stage1/Stage2/CS/PD/PP 五个内容生产 Tool 钉在各自最新一次发布版，最晚 2026-08-24 02:28）。参数面核对（Provider 声明参数数 vs 子应用 `start` 节点实际变量数 vs 父流 Tool 节点实际传参数）8 组全部三方一致，无冗余传参也无遗漏声明。

**结论：`FIXTURE_RUN_002` §2.3 记录的这处缺陷曾经真实发生过（CS/PD/PP 三个 Tool 的绑定时间戳证实确实存在过一次"旧绑定→新发布"的窗口），但已被后续重新绑定修复；风险机制本身仍潜伏存在（Dify 平台行为未变），只是当前 25 个 App 里没有任何一处正处于该缺陷状态。**

### 七.2.2 Matrix 部署版本澄清（PROJECT_INDEX.md claim 的精确核验）

`PROJECT_INDEX.md:78` 声称"Matrix Architect → 部署运行的是 v0.1.2"。**核验结论：Skill 正文层面为真，App 资产层面容易误导，需要分层表述**：

- 实盘绑定的 Matrix Tool（`f8d2be15…`「V1 Tool Matrix Architect v0.1」）内嵌的系统 Prompt 自带 `mx_skill_sha=7a6afa3c…`，与 `sha256sum decision-chain/skills/Matrix_Architect_v0.1.2.md` **逐字节相同**——v0.1.2 正文确实是当前生效内容，模型为 `deepseek-v4-flash`。
- 但**同名为"v0.1.2"的独立 App**（`DIYU_DEMO_MATRIX_QWEN_V0_1_2`，用 `tongyi/qwen-max`）**从未发布、未被任何 Tool 绑定**，是一个死画布资产——真正在跑的是另一个名字里根本不带版本号的 App（"V1 Tool Matrix Architect v0.1"）。三个 `DIYU_DEMO_MATRIX_QWEN_V0_1*` App 全部同此，均为孤立、未发布、未绑定的历史画布留存。
- Campaign 同理核验：实盘绑定的是 `deepseek-v4-flash`（`a0d92232…`「V1 Tool Campaign Orchestrator v0.1」，与 `DIYU_DEMO_V1_TOOL_CAMPAIGN_v0.1.yml` 9/9 精确匹配），`DIYU_DEMO_CAMPAIGN_QWEN_V0_1` 与 `..._DEEPSEEK_V4_FLASH_COMPILE_V0_1` 两个候选变体均未发布、未绑定。
- Content Brief 的 Tool 绑定同样精确匹配、`skill_sha` 校验通过，无需更正。

**给 Founder 的建议表述（供裁决，本任务不代为决定）**：「Matrix Skill 正文 v0.1.2 确实是当前生效内容」这句话是对的；但如果按 App 名称去找"部署的是哪个 App"，字面对应的 3 个 `MATRIX_QWEN_V0_1*` App 全部是死资产，容易造成误判。

### 七.3 六 Skill 源文件 ↔ 工作流提示词 ↔ 模型约束一致性（A16）

> 核验方式：仓库文件 sha256/逐字节 diff + 实跑 Dify 只读 SELECT 取当前已发布 graph，节点级/边级全量比对。

#### 七.3.1 内容生产三 Skill（Creative Script / Production Director / Publishing & Packaging）

**共同事实**：三份 references 本地副本与 `content-production/references/` 共享主本 md5 完全一致（12 个文件两两相等）；三份 Skill 正文 → 实盘 System Prompt **逐字节零删改**，仅在末尾追加同一段 9 行的确定性投影注入块（"未列出的参考内容本次没有加载，不得引用、不得凭记忆补写"）。**Skill 原始能力层到工程投影层这一段是干净的。**

**六项缺陷（三项已证实为 repo-vs-live 真实分歧，两项为投影裁剪的已声明事实，一项待运行验证）**：

| ID | 缺陷 | 判定 |
|---|---|---|
| **A16-01** | **运行时自证哈希失效**：`projection_record` 节点自我声明的 `platforms.md` 哈希，四个实盘应用（CS/PD/PP/探针）**全部**落后仓库当前值一个版本；PP 自己的 `SKILL.md` 哈希更是落后**两版、少 5,612 字**（对应仓库 v0.6 时代的旧值）。**正文本身已跟上最新版，只有这道自证完整性控制没跟上**——即"投影内容对了，但检测投影是否漂移的机制本身失效"，无法用来发现未来的漂移 | **已证实** |
| **A16-02** | `examples.md`（占三份共享语料 47%，7,344 字）在**任何** `subject_domain` 取值下投影结果都是 0 字送达，但三份 SKILL.md 均把它列为自身参考资产。已被系统自陈为"已声明裁剪"（`excluded_reference_sections[]` 逐条列出），非静默截断 | **已证实**（已声明裁剪，非缺陷本体，但构成"资产清单与可得资产恒定不等"的事实） |
| **A16-03** | 三份生产应用的 user prompt 与 input 字段标签里都焊死了一句"本轮 platform 为 `PROBE_ONLY` 值……不构成正式发布平台裁决，据此产出的平台适配均为草案"——**这是一次性运行期的探针措辞，被固化进了已发布图**，导致**当前任何一次调用**（无论 Founder 是否已锁定平台）模型都会被告知平台是探针值 | **已证实**，对 Publishing & Packaging 影响最直接（其全部职责就是平台包装，被"平台未锁定＋规格未核实＋不得自填数字"三重收窄） |
| **A16-04** | **Creative Script `reasoning_effort` 仓库=`max` vs 实盘已发布=`low`，实盘草稿又是 `max`**——三档枚举下是"对角分歧"不是"版本落后"。仓库逐提交演进方向是 `high→max`（升档），实盘逐版本演进方向是 `high→low`（降档，且中途有一次回退到 `high` 又再次降回）。**后果**：仓库 `content-production/workflows/` 目录当前不是可安全重建的制品——按仓库 YAML 重新导入会得到 `max` 档 CS，依据下方 A16-模型约束证据几乎必然全链零产出 | **已证实**（与 Dify 扫描 Agent 独立发现的 D2 完全互证） |
| **A16-05** | CS-6（Skill 自称"写任何东西之前的第一个判断"）要求 `content_origin_mode=访谈提取` 时**不得**产出逐字稿、只出提问清单+骨架；但注入的 `---USER_DELIVERY_CS---` 交付块无条件要求 `final_script`（完整口播稿），且明令排除 `question_list`/`skeleton` 等内部字段名，`status` 只有两个值、无"本模式不产出逐字稿"的合法出口 | **NOT_VERIFIED**——全仓运行记录里 `content_origin_mode` 实际取值只出现过"现拍"和"现拍+已有素材剪辑"，"访谈提取/视觉先行/AI 生成"三个分支从未被真实运行触发过，这是读代码得出的结构性风险，不是观测到的故障 |
| **A16-06** | Publishing & Packaging 的 `returns_adapter` 闸 1（fact_id 简写扫描）在**实盘**多出一段仓库没有的豁免逻辑（跳过以"＞"开头的引用说明行），修复源头可追溯到 `CONTENT_PRODUCTION_P05R2_RUN.md`（消掉一次误报，回归 4/4 真命中不丢），**但这次修复只落在 Dify 画布，从未回写仓库**（`git log -S` 全仓零命中）。方向是**实盘比仓库更宽松**——按仓库重建会让已经修好的误报重新出现 | **已证实** |

**模型约束的真实压制链（唯一一条有完整真实运行证据的压制，不靠 token 上限数字推断）**：`max_tokens=384000` 经查证不是压制项（三份产出实测 4,771–9,815 字，离上限有数量级余量）；真正的硬约束是节点级墙钟 `PLUGIN_MAX_EXECUTION_TIMEOUT=600s`。有六层递进的真实运行证据链：① `high` 档下 CS 三次运行均 600.0-600.2s 被杀、零产出；② 把输入砍到 23% 仍然 600s 被杀零产出（"缩小输入可绕过超时"假设已被证伪）；③ `high` 档整链三段产出全部"本轮未产出"，六项验收 0 通过；④ 同一夹具 `high` vs `low` 对照：`high` 档 10 次尝试 6 次超时、全链跑不完，`low` 档单次尝试全部成功、全链 9.5 分钟跑完；⑤ 即便在 `low` 档下，CS/PD 最佳成功样本距 600s 硬顶余量仅 6.2%~6.8%，原文自陈"任何一次模型侧正常波动都可能让某一段越线"；⑥ 这次降档在当时的运行记录里被**明确认定为"会改变产出质量"且需要 Founder 裁决的工程让步**。**结论：`reasoning_effort` 从默认 `high` 降到 `low` 是一次有实测依据、已被记录承认会影响质量的真实压制，且已生效。但 `low` 相对 `high` 的具体质量差异——全仓无同夹具下 `high` 档的成功产出样本可比（`high` 档在该夹具上从未成功产出过），因此"low 档具体弱化了什么"仍是 NOT_VERIFIED，不得据此写"质量必然下降"这类结论。**

Stage 2 独立语义核验节点（`qwen3.8-max`）：实盘核验存在、在关键路径上（非旁路装饰）、`error_strategy=default-value→SEMANTIC_CHECK_NODE_FAILED`，下游 `return_agg` 对不可解析/自相矛盾输出一律不判通过（fail-closed 已从代码逻辑证实）。三个 Tool Provider 版本绑定当前均与子应用最新已发布版本一致，无静默跑旧版本。

**能力影响结论（已证实，非推测）**：PP 是三份中问题最集中的一份——除 A16-01/03/06 外，`P05R2`/`P05R3` 两轮真实运行已经证明"确定性闸对语义型编造是瞎子"（一句带真实 fact_id 但编造次数的话"从十几次试穿里"被四道闸+两个扫描器全部放行，靠后加的语义核验节点才拦下）；`FINAL` 三级 mode 判据至今从未在真实运行中走到过（只验证过 PRE 与 MIXED）；mode 判据"读计划字段判断现实状态"这一内部自相矛盾已被登记但**仍在当前线上生效的 v0.6.2 正文中未修**。

#### 七.3.2 决策链三 Skill（Matrix / Campaign / Content Brief）

**版本配对（三方 sha256/md5 逐字比对，全部实证）**：
- **Matrix**：`Matrix_Architect_v0.1.2.md` → `DIYU_DEMO_V1_TOOL_MATRIX_v0.1.yml` → Dify app `f8d2be15` published `612c8080` → 主链 `tool_matrix`。System prompt 三方 md5 **逐字一致**（`diff` 退出码 0），206 行全部无损送达。v0.1/v0.1.1 只存在于未发布 draft，只对应历史 RUN_001/RUN_002。
- **Campaign**：`Campaign_Orchestrator_v0.1.md` → `DIYU_DEMO_V1_TOOL_CAMPAIGN_v0.1.yml` → app `a0d92232` published `1f5505a6` → 主链 `tool_campaign`。System prompt 在 7 处仓库+线上文件中 md5 **全部相同**，399 行无损送达。
- **Content Brief**：`Content_Brief_Architect_v0.1.md` → `DIYU_DEMO_V1_TOOL_CONTENT_BRIEF_v0.1.yml` → app `eadf8867` published `8248fc80` → 主链 `tool_content_brief`。System prompt 4 处 md5 **全部相同**，334 行无损送达。

**全局前置事实**：主链 56 节点里没有任何一个节点直接内嵌三份 Skill 正文——三份 Skill 通过 `provider_type: workflow` 的 Tool 节点调用三个独立子应用，`tool_name`/`provider_id` 与三个 Tool DSL 逐字一致。仓库↔线上做了 10 对 DSL/图的全节点结构化 diff，**主链 56/56、三个 Tool 9/9/9、Content Brief 独立 App 6/6 节点数据完全一致**；5 个 A/B 期子应用（`DIYU_DEMO_MATRIX_QWEN_V0_1*`、`DIYU_DEMO_CAMPAIGN_QWEN_V0_1`、`..._DEEPSEEK_V4_FLASH_COMPILE_V0_1`）`apps.workflow_id IS NULL`——从未发布，不在任何线上路径上（与 Dify 扫描 Agent 的 P1 发现完全互证）；`DIYU_DEMO_CAMPAIGN_QWEN38_FALLBACK_COMPILE_V0_1.yml` 全仓零引用、线上无对应 App，是孤儿文件（与扫描 Agent 独立发现的仓库孤儿互证）。

**正文差异（按层分类）**：

| 编号 | 层级 | 差异 | 判定 |
|---|---|---|---|
| C-2 | 工程语义理解/投影 | **Campaign 最重要的发现**：Tool Prompt 里硬编码 `RUN_MODE=COMPILE_CONFIRMED_DECISIONS` + 序里集 C1—C6 六份 Founder 确认稿全文（42,972 字），明令"不得重新选择主要顾客变化/主讲账号/发布顺序/参战组合/内容数量/承接政策"。**逐条核对 Skill 正文自身的六步生成职责**（§3 步骤一至六），发现该禁令覆盖了其中至少四步，且**Skill 源文件本身完全没有"上游锁定"章节**（全文 grep 零命中"不得重新选择"/"C1"/"确认稿"）——这条禁令是工程侧从外部注入，不是对 Skill 自带条款的转述 | **已证实**：Campaign 在当前链路上从"决策者"被降级为"编译器"，与本报告 §四.1 六 Skill 价值耦合审计里 Campaign 的"主目标类型锁定"是**同一个根因的两个独立视角**（一个查值观耦合，一个查运行时降权），互证一致 |
| M-1/M-2 | 工程语义理解/投影 | Matrix Tool Prompt 硬编码整份夹具全文（104 行）+ 账号数量常量"四张"（Skill 源原文是"由输入决定的数量"） | 已证实，与 §二能力卡 1 的发现一致 |
| B-1 | 工程语义理解/投影 | **对照发现（重要的反例）**：Content Brief 的"不得重新决定"禁令逐条核对后，是 Skill 自己 §2「上游锁定」原文列举清单的**真子集**（少了两项，未新增任何未授权限制）——**这是 Campaign C-2 的反例**：同样是一句"不得重新选择"，Content Brief 侧是忠实转述，Campaign 侧是外部注入 | 已证实，**Content Brief 无削减** |
| G-3 | Dify/Runtime 表达 | 主链 `pre_*` 节点内置的 `SKILL_SHA_MISMATCH` 完整性校验，其比对的"当前值"来自 Tool 子应用里一个**硬编码字面量**模板节点，不是对实际 system prompt 现场求哈希——即该校验是"常量对常量"，若真的有人在 Dify UI 里改了 system prprompt 而不同步改这个字面量，校验依然 PASS。**今天三份 Skill 的一致性是本次审计逐字比对出来的，不是这道闸验证出来的** | 已证实（今日实测值恰好正确，但机制本身不构成防护） |
| G-4 | Dify/Runtime 表达 | 三个 `judge_*` 节点被要求核对"产物是否满足其 Skill 现有的输出合同"，但 user prompt 实测结构里**从未包含输出合同正文**；确定性侧 `pre_*` 的必需字段检查也只是 4-5 个关键词子串扫描 | 已证实：**三份 Skill 各自数十项输出合同条款，在 runtime 没有任何一层真正校验** |

**模型约束——两条历史已修复、两条当前仍在生效的真实压制/异常**：
1. **[已修复]** Campaign 历史 `max_tokens=8192` 配置下曾两次 `finish_reason=length`，正文（专业判断、参战关系、排序、承接结论）**产出为 0**——DeepSeek 思考模式下推理块吃光了全部 8192 预算，`</think>` 从未闭合。已被当前 `384000` 上限取代，当前线上不复现，仓库证据文件已归档此事件。
2. **[已修复]** `judge_matrix` 历史曾在 `max_tokens=1200` 下 3 次 `finish_reason=length` 导致 `JUDGE_VERDICT_MISSING`——已知机制：DeepSeek 推理块计入 completion tokens，推理:正文比可达 9.6:1，小预算极易被推理块吃光。已提升预算修复。
3. **[当前仍是线上值，未被判定]** `v1_shadow`（任务理解节点）`max_tokens=16000`，实测曾出现 1 次 `finish_reason=length`、`text=""`（2026-08-22 06:09）。是否需要继续调整未有后续证据判定。
4. **[当前未修复，最近一次发生在今天]** `cp_llm`（Campaign）在当前 384000 上限下仍有 **2/17（≈12%）运行 `finish_reason=stop` 但可见正文长度为 0**——不是被截断，是 DeepSeek 分离式推理通道下模型只产出了推理内容、可见通道为空，触发下游 `MODEL_OUTPUT_NO_FINAL`。最近一次实测发生在 **2026-08-24 09:25**（即本任务执行当天）。

**能力影响结论**：三份 Skill 正文本身到 Prompt 投影这一层**全部无损**（三方 md5 逐字一致）。真正的能力削减发生在**工程语义理解/投影层**，且三份表现完全不同——Campaign 被显著降权（C-2，四步生成职责被外部注入的 RUN_MODE 禁用）、Matrix 有可预期的 Demo 收窄（M-1/M-2，与夹具协议自洽）、Content Brief 无削减（B-1，禁令是自身条款子集）。运行时完整性/质量校验机制本身存在结构性盲区（G-3 常量比对、G-4 Judge 拿不到合同正文），意味着"今天三份 Skill 与线上一致"这件事**是本次审计人工核实出来的，系统自身现在还查不出来**。

**NOT_VERIFIED（Founder 盲审侧的诚实缺口）**：`V1_QUALITY_FOUNDER_REVIEW_v0.1.md` 记录的 9 组盲审（Matrix/Campaign/Content Brief × 集成轴/模型轴/Skill 轴）里，**Matrix 与 Content Brief 各自的 3 组全部"无法盲审"**——根因是各自唯一一次 `deepseek` 臂的基础设施故障（分别是 Server Unavailable 与 600s 超时）同时充当三个对照轴的甲方样本。Campaign 三组可判，但 Skill 轴结论是 `SKILL_VALUE_INCONCLUSIVE`（"Skill 让产物更好交付，但没有改变业务判断本身"），且原始文件自陈三组统计上不独立（同一份产物）。**缺失的证据是**：Matrix 和 Content Brief 各自补跑一次成功的 `deepseek` 臂。

---

## 八、持久化现状（A10）

> 核验通道：`docker exec docker-db_postgres-1 psql` 只读查询（真实 Dify Postgres），全程零写入。

### 八.1 分能力现状表

| 能力 | 判定 | 证据 |
|---|---|---|
| 品牌/商品/库存/价格/顾客等业务事实 | **MISSING**（只作为冻结 Markdown 夹具内嵌进 Prompt，非持久化状态） | `decision-chain/fixtures/一页纸夹具品牌事实 v0.1.md:3` 自述"Demo 夹具输入事实源"；`V1_PRODUCTION_GAP_REGISTER_v0.1.md:89`"不建知识库，夹具以 SHA 冻结全文内嵌进 Prompt"；`SELECT count(*) FROM datasets;`→`0`，`documents`→`0` |
| 账号状态（逐账号经营状态） | **MISSING** | 无 account/brand 表；`pg_tables` 只有 Dify 自带表；全仓库 workflow 对 `tenant_id`/`brand_id` 的唯一命中是一句 Prompt 纪律（"你不输出租户、权限、账号或任何系统字段"，`DIYU_DEMO_V1_FULL_CHAIN_CHATFLOW_v0.2.yml:944`），不是机制 |
| 任务快照 | **CURRENT，但仅作为 Dify 会话变量** | `workflow_conversation_variables` 按 `name` 分组：`task_snapshot_json 242` / `matrix_artifact 242` / `campaign_artifact 242` / `content_brief_artifact 242` / `production_plan_artifact 12` / `production_runtime_state 12` / `creative_script_artifact 12` / `publishing_artifact 12` / `production_delivery_pack 12`。阶段分布：`IDLE 142 / READY 35 / COMPLETED 25 / AWAITING_CONFIRMATION 23 / CANCELLED 9 / FAILED 8` |
| 产物版本历史 | **MISSING**（一个槽位只留一版，覆盖即丢） | `workflow_conversation_variables` 列为 `id,conversation_id,app_id,data,created_at,updated_at`——**无版本列**，同 (conversation, name) 只有一行；`V1_PRODUCTION_GAP_REGISTER_v0.1.md` G-05 明确"无版本历史…无跨会话检索…无生命周期管理" |
| 发布实例（某内容版本在某平台/账号/时间的实际发布） | **MISSING** | 无表、无变量、无文件；仅在**未被接受**的子合同里作为未来需求出现（`V1_SINGLE_ACCOUNT_SLICE_CONTRACT_v0.1.md:258`） |
| 用户反馈 | **MISSING** | `message_feedbacks`→`0`，`message_annotations`→`0`，`saved_messages`→`0`，`pinned_conversations`→`0` |
| 权限/身份（产品级） | **MISSING**（只有 Dify 控制台管理员账号） | `accounts`→`1`（`diyu`），`tenants`→`1`，`owner` 角色 1 条；Service API 的 `user` 字段由调用方自填、服务端不校验——92 条脚本自造的 `end_users`（`v1-e2e-SK-03` 等），对应 G-06 |
| 幂等/精确一次 | **MISSING，且合同原文明确不作声称** | `V1_TASK_SNAPSHOT_SCHEMA_v0.1.json:170`"不声称并发原子消费或 exactly-once"；`V1_DEMO_INTEGRATION_CONTRACT_v0.1.md:223`同类声明；G-03：`authorization.consumed` 与 Tool 调用不在同一事务 |
| 恢复能力 | **同会话内 CURRENT／跨会话 MISSING** | 同会话：`conversation_id=aab9fa9d-…`（`v1-e2e-SK-03`）created `2026-08-22 07:08:26`，变量最后更新 `2026-08-24 08:02:48`（跨 2 天完整复现）。跨会话：DSL 把每个新会话硬编码为全新 `IDLE` 快照（`…v0.2.yml:27-32`）；`V1_DEMO_INTEGRATION_CONTRACT_v0.1.md:46`"不支持跨会话长期任务恢复" |
| 独立业务数据库（非 Dify 自带） | **MISSING——不存在** | `docker ps -a`：16 容器全部是 Dify 1.16.1 自带栈；`pg_database`→`postgres, dify, template1, template0, dify_plugin`，无业务库；`tools/`、两个模块 `docs/` 全仓 grep `DATABASE_URL|POSTGRES|MYSQL|psycopg|sqlalchemy|sqlite|redis` 仅命中一处无关的 Codex CLI 状态文件 |

### 八.2 关键漂移：运行时合同 vs 实际部署

- `decision-chain/docs/V1_TASK_SNAPSHOT_SCHEMA_v0.1.json` **定义了但无代码消费**（`tools/` 全仓 grep 零命中），且**相对已部署 DSL 是 STALE**：文件只允许 3 个产物槽位（`matrix/campaign/content_brief`），但已部署状态机（`…v0.2.yml` 的 `v1_state` Code 节点）实际有 **5 槽**（新增 `production_stage1`/`publishing_stage2`）；live 数据证实 5 槽为真（`workflow_conversation_variables` 命中 `production_stage1`/`publishing_stage2` 各 12 条）。
- `content-production/docs/CONTENT_PRODUCTION_RUNTIME_CONTRACT_v0.1.md` §4.2 规定"哈希相同即判未改，下游产物**不转** STALE"，但实际部署的决策链侧节点（`fin_matrix`/`fin_campaign`/`fin_content_brief`/`fin_stage1`）实现的是**无条件级联**（上游一旦 `VALIDATED` 就把全部下游标 `STALE`，不做前后哈希比对）——**CONFLICT：合同条文与实际代码相反**，且 §4.2 规定的"人工回改触发定向重跑"闭环本身也是 **MISSING**（`tools/content_production_pre_chain_controller.py:19-21` 自述"不接受回改、不触发重跑、不标 STALE"）。
- `realization_manifest` 的 PRE/MIXED/FINAL 三档：**PARTIAL**——`FINAL` 档从未在真实运行中走到过（`content-production/evidence/CONTENT_PRODUCTION_FINAL_CHAIN_RUN_001.md`第 9-25 行：PP 自行推导为 `MIXED` 而非 `FINAL`）。

### 八.3 是否为 Dify 内部专属状态

**结论：本产品当前 100% 的持久化状态都在 Dify 内部，不存在第二套存储。** 所有任务快照、产物、对话/消息历史、运行轨迹全部落在 `workflow_conversation_variables`（1,033+242 行）、`conversations`（253）、`messages`（622）、`workflow_runs`（738）、`workflow_node_executions`（5,704）——按 `conversation_id` 分区，跨会话零延续，200KB/变量硬上限（`CONTENT_PRODUCTION_RUNTIME_CONTRACT_v0.1.md:267`），且无留存期/脱敏/删除接口（G-09）。253 条会话全部产生于 2026-08-21～08-24 三天内、由脚本化测试身份（`v1-e2e-*`／`repair-*` 等）针对同一虚构夹具品牌发起——**这是真实系统的真实回归执行证据，但不是任何真实账号的经营历史**。

### 八.4 首个纵向切片已有基础 vs 真缺口

**已有（CURRENT，可复用）**：确定性 5 槽任务状态机（已部署运行，507 次运行记录）；产物已带内容寻址身份（`content_hash`/`parent_artifact_id`/`skill_sha`/`run_id`/`fixture_bundle_sha`，Schema 与 live 数据均已验证存在）；跨阶段哈希回验（`content_production_pre_chain_controller.py:139-155`）；一条从运行系统读回确定性事实的路径（`v1_demo_e2e_replay.py`，证明"可查询"这件事本身已经成立，只是目前只能查 Dify 自己的库）；一个已在运行的 Postgres 15 实例（`docker-db_postgres-1`，是否复用留待 Founder 裁决，子合同 `:160` 已注明为待裁决项）。

**真缺口（MISSING，与 `V1_PRODUCTION_GAP_REGISTER_v0.1.md` G-01～G-09 一一对应）**：Dify 之外的独立业务库；账号/品牌实体与其经营状态；产物版本历史；发布实例；反馈归因；服务端用户身份；租户/权限隔离机制（而非仅 Prompt 纪律）；并发控制（CAS/事务）；授权消费的原子性；产物与状态的原子提交；跨会话任务恢复；哈希门控的 STALE 判定与人工回改重跑闭环；对已部署 v0.2 图（含 2026-08-24 对话编排修复新增内容）的自动化验证覆盖——`tools/v1_demo_verify.py:21-23` 自述其单测目前只覆盖 v0.1 文件，v0.2 与新增的 `side_question`/`open_threads`/`last_acceptance` 均在其覆盖范围之外。

本节只报告当前事实，不提出未来 Schema／接口／状态机设计，不冻结任何合同。

---

## 九、CURRENT / STALE / NOT_VERIFIED / MISSING / CONFLICT 汇总（登记表，非逐条重复正文）

> 各条详情见对应章节；本表只做定位索引 + 一句话结论。

### 九.1 MISSING（能力或机制完全不存在，非降级）

| 项 | 定位 |
|---|---|
| 单账号持续运营能力（八项能力之一） | §二·能力3 |
| CS-1 外部同质化比较 | §五.2 |
| 生产链下游失效（STALE）机制 | §六.3 |
| 局部（单元级）重跑 | §六.3 |
| 独立业务数据库（Dify 之外） | §八.1 |
| 账号状态、产物版本历史、发布实例、用户反馈、服务端用户身份、跨会话任务恢复 | §八.1 |
| 主目标/次目标/优先级/不可牺牲条件/账号阶段/期望发布量的结构化承载 | §三.2 |
| 段间控制器对 MIXED/FINAL（`realization_manifest`）的支持 | §六.4 |

### 九.2 CONFLICT（两处权威表述互相矛盾，均已核实为真）

| # | 冲突双方 | 定位 |
|---|---|---|
| 1 | Content Brief 上游：更正块称"不止 Campaign" vs DSL+Skill 仍硬锁 Campaign（**已被合同自己预先登记为本轮不修**） | §四.3、§五.3 |
| 2 | Publishing & Packaging mode 判据：运行合同 §4.3 仍是旧两条件表 vs Skill v0.6.1 已是三级依次判（**运行合同文档本身 STALE，未跟进**） | §六.2 |
| 3 | CS-1 硬编码候选数 3 vs CLAUDE.md §4"候选数量不得硬编码"（**已被合同登记为本轮暂缓**） | §五.2 |
| 4 | Publishing & Packaging 独立调用要求 `cs_final`+`pd_final` 均必填 vs 合同称"有成片信息即可直接调用" | §六.1 |
| 5 | Creative Script `reasoning_effort`：仓库=`max` vs 线上已发布=`low` vs 线上草稿=`max`（三档对角分歧，仓库不是可安全重建的制品） | §七.3.1（A16-04），§二·能力6 |
| 6 | Publishing & Packaging 闸1豁免：线上比仓库更宽松，修复未回写 | §七.3.1（A16-06） |
| 7 | 下游失效级联：合同§十一/验收D要求"无实质修改不失效" vs 五处 fin_* 节点全部无条件级联（从不比对哈希） | §二各能力卡·第6项，§三.7 |
| 8 | 通用代码节点硬编码夹具专属逻辑（`BRF-SUHE-001` 追加事实块 + "服装/门店"关键词判行业） | §三.7、§五.3 |
| 9 | 六个能力"可直接进入"（合同）vs `UPSTREAM_OF` 单向线性锁（DSL，除 Matrix 外全部受限） | §三.3 |
| 10 | 段间控制器文档字符串"只重试基础设施失败" vs 实际代码"产物字段缺失即重试" | §六.4 |
| 11 | Matrix Tool 完整性校验 `SKILL_SHA_MISMATCH` 是常量对常量，不对实际 Prompt 现场求哈希 | §七.3.2（G-3） |
| 12 | Judge 节点被要求核对"输出合同"，但从未收到合同正文（三份决策链 Skill 共性问题） | §七.3.2（G-4） |
| 13 | Dify 主 Chatflow App 显示名称仍"v0.1"，实际内容是仓库 v0.2 文件 | §七.1 |
| 14 | Publishing Packaging 应用：live `returns_adapter` 代码比仓库多 8 行豁免逻辑，未导出回仓库 | §七.2（D1） |
| 15 | `DIYU_DEMO_CAMPAIGN_QWEN_V0_1` 应用名含"QWEN"，实际草稿模型已是 DeepSeek | §七.2（D3） |

### 九.3 STALE（曾经真实，已被后续版本/事件取代）

| 项 | 定位 |
|---|---|
| `content-production/docs/CONTENT_PRODUCTION_FINAL_CHAIN_RUN_001.md` 的 mode=MIXED 结论（v0.6 旧判据下产物，已被 v0.6.1 三级判据取代） | §六.2 |
| `V1_TASK_SNAPSHOT_SCHEMA_v0.1.json` 只声明 3 产物槽位（实际已部署 5 槽） | §八.2、§三.2 |
| `decision-chain/evidence/V1_DIFY_RUN_MANIFEST_v0.1.md` 记录的主链已发布 workflow_id（已被对话编排修复证据的新 ID 取代） | §二·能力1 |
| L2 账本头部"main @ 6ae78ab"（起算基线固定锚点，非过期，不需更正） | §〇 |
| 规划侧 Prompt 第 3 节 observed main = 6ae78ab（同上，良性滞后） | §〇 |

### 九.4 NOT_VERIFIED（有明确缺证原因，非遗漏）

| 项 | 缺什么证据 |
|---|---|
| 生产链下游 STALE 级联的真实（非离线单测）触发 | 一次真实对话里"上游重出→下游正向被标 STALE"的完整证据 |
| Matrix / Content Brief 的 Skill 真实增益 | 各自补跑一次成功的 deepseek 臂盲审 |
| Creative Script CS-6"访谈提取"等模式与用户交付块的结构性冲突是否真实触发 | 一次 `content_origin_mode≠现拍` 的真实运行 |
| `reasoning_effort=low` 相对 `high` 的具体创意质量差异 | 同夹具下 `high` 档的成功产出样本（`high` 档在该夹具下从未成功过） |
| 集成主链生产分支（production_stage1/publishing_stage2）整体端到端 | 一次专门提交的完整运行记录（目前只有间接会话快照痕迹） |
| Campaign `upstream_overlap` 常年 40-46%（vs Content Brief 79-83%）是否构成实质漂移 | 人工逐条核对 Matrix 责任卡→Campaign 参战判断的承接性 |
| Creative Script/Production Director 投影裁剪对 CS-1/PD-1 等核心判断质量的具体影响 | 针对性对照评测，目前全仓未做 |

### 九.5 CURRENT（已被本次核验实证，正面结论，择要）

主 Chatflow 56 节点草稿=发布=仓库 v0.2；三份决策链 Skill 正文三方逐字一致；8 个 Tool Provider 版本绑定 0 处过期；PRE/MIXED/FINAL 三级判据均已被真实运行触发并证明有区分力；四道确定性闸+语义核验节点已实证拦截过真实编造；A-0～A-4 对话编排修复全部有真实 Dify 对话证据；跨阶段交接为字节级精确（三方重算）；两条硬性运行时限（1200s/600s）均从源码确认。

---

## 十、A1—A10 / A14—A16 验收矩阵

| ID | 结果 | 证据 |
|---|---|---|
| A1 | **PASS** | §〇：git 原始输出（remote/branch/HEAD/worktree/工作区）与本报告基线一致，`6ae78ab` 良性滞后已核实澄清 |
| A2 | **PASS** | §一：6 份独立文件（上位合同/子合同/两版阶段基线/项目基线/CLAUDE.md/README/PROJECT_INDEX）逐字核对，授权边界表述一致，无 CONFLICT |
| A3 `NON_PRUNABLE` | **PASS** | §七：本机真实 Dify 1.16.1（17 容器，2 天在线）全部经 `docker exec psql` 只读原始查询核验；两个自称 Dify 通道的 MCP 工具经核实为演示假数据，已弃用不采信；全部 25 个 App 均已核验，非抽样 |
| A4 | **PASS** | §三：A-0～A-4 全部有真实 Dify 对话证据；路由机制、任务上下文承载方式、线性锁、直接入口、句式依赖、重复确认逐项实证核验 |
| A5 `NON_PRUNABLE` | **PASS** | §二：八张现状卡齐全，能力 3（单账号持续运营）经三重核验明确判定 MISSING（非静默合并、非冒充） |
| A6 `NON_PRUNABLE` | **PASS** | §四：六份 Skill 全文逐字通读分档，每条结论均有具体规则/Prompt 行号引用；与合同自带历史值做了显式比对并发现计数缺口 |
| A7 `NON_PRUNABLE` | **PASS** | §五：CS-1 调用位置、候选出口（两层反差）、外部比较缺失、Content Brief 直接入口均有节点级/运行级证据 |
| A8 `NON_PRUNABLE` | **PASS** | §六：CS/PD/PP、Stage1/2、PRE/MIXED/FINAL、Returns、语义核验、用户交付、恢复机制逐项核验，证明与缺证部分均明确分列 |
| A9 `NON_PRUNABLE` | **PASS** | §七：全部 25 个 App 做了结构/节点级 Hash/版本比对，3 处真实漂移与 Tool 绑定核验结果原样登记，未修复未掩盖 |
| A10 | **PASS** | §八：业务持久化逐项标 CURRENT/MISSING/NOT_VERIFIED，含 Dify 内部状态与"是否可作为业务真源"的明确区分 |
| A14 | **PASS**（见下方核验） | 见 §十.1 |
| A15 | **PASS**（见下方核验） | 见 §十.2 |
| A16 `NON_PRUNABLE` | **PASS** | §七.3：六份 Skill 逐份给出版本配对、正文差异清单（非"基本一致"笼统结论）、模型约束的真实运行证据、能力影响结论；无充分依据处均明确标 NOT_VERIFIED |

### 十.1 A14 核验：受保护资产零变化

全程只执行 `SELECT` 查询（无 `INSERT`/`UPDATE`/`DELETE`），未发布、未更新、未重绑任何 Dify 应用；未修改任何 Skill/Reference/Fixture/Workflow/Tool 绑定/模型参数/业务数据库/部署配置/其他分支或 worktree 内容。仓库侧改动范围见下方 `git diff --stat`（本任务分支相对 `main` 的全部改动，将在末轮验证时附上）——预期只包含：本报告文件、`collab-ledger/L1/L2/L3/L5` 四本账的追加式增量。

### 十.2 A15 核验：远程收口

任务分支 `task/v1-rebase-ep00-current-m0-preflight` 将在本报告与账本增量提交完成后推送至 `origin`，核对本地 `git rev-parse HEAD` 与 `git ls-remote origin` 对应 ref 一致，不直推/不合并 `main`，不创建 PR。核验结果见收尾 commit。

---

## 十一、仍需 Founder 裁决的产品命题

以下均为本次只读预检发现的**事实与差距**，不代为裁决、不预设唯一修法：

1. **单账号持续运营能力完全不存在**（§二·能力3），且其成立前提之一（可恢复的业务持久化能力，§八）也不存在。子合同仍是 `CONTRACT_REVISION_REQUIRED`。这是最大的产品缺口，但按本任务边界不构成本轮施工授权。
2. **Content Brief 唯一上游锁定与产品合同已宣布废止的假设直接冲突**（§四.3、§五.3），合同自己已把"解禁"标记为需要新授权的 Skill 正文改动——是否/何时启动这次改动需要 Founder 裁决。
3. **Campaign 当前实为"编译 C1-C6 冻结决策"而非"真实规划战役"**（§二·能力2、§七.3.2 C-2）——这是否符合 Founder 对"单次经营任务策划"能力的预期，需要明确表态；如不符合，这是运行时降权（外部注入的 RUN_MODE），不是 Skill 本身能力缺陷。
4. **六份 Skill 价值耦合分档结果**（§四）：Matrix 的建号门槛（"职位高低/出镜意愿/表演能力不能单独构成建号理由"）会让达人型/内容型增长账号无法通过建号判断——是否需要为增长场景开旁路。Publishing & Packaging 新增的业务动作封禁清单默认关闭 CTA——默认值方向是否符合 Founder 预期。
5. **CS-1 硬编码 3 个候选方向**违反 CLAUDE.md §4，已被合同登记为本轮暂缓——是否/何时修正。
6. **Creative Script `reasoning_effort` 仓库/线上/草稿三方分歧**（§七.3.1 A16-04）：当前仓库 YAML 不是可安全重建的制品，若不同步会在未来任何"从仓库重新导入"场景下复现全链零产出——建议尽快把线上生效值回写仓库，但这是否算"允许的仓库 Delta"需 Founder 确认（本任务未做此项改动，只登记）。
7. **Publishing & Packaging 线上闸修复未回写仓库**（§七.3.1 A16-06）——同上，建议回写但本任务未做。
8. **3 个未被任何文档记录的实盘 Dify App**（§七.2 孤儿资产），其中两个持有绑定生产 Tool 的真实可执行入口——这是一处治理缺口，建议至少补充文档记录或评估是否应该清理，具体处置需 Founder 裁决。
9. **Dify 主 Chatflow 应用显示名称"v0.1"与实际内容"v0.2"不同步**（§七.1）——是否需要人工改名，纯命名问题，不影响功能。
10. **对话理解节点 `v1_chat_llm` 无任何错误处理策略**（G-12，§三.6），已有真实故障案例（用户看到过 Python 报错）——是否列入近期修复优先级。
11. **决策链五处判据下游失效均无条件级联**（不比对内容哈希，§三.7、§九.2 冲突 7），与合同"无实质修改不应使下游失效"直接相反——是否需要尽快补上哈希比对逻辑。

---

## 十二、明确写出：哪些下一阶段仍未授权

- 子合同 `SINGLE-ACCOUNT-SLICE-EP00` 专项预检 —— 待 Founder 接受子合同。
- 任何 Skill／DSL／Dify 工作流／业务持久化施工（M1—M4）。
- 四份共享合同 readiness map、M1—M4 缺口图与成熟度重估、报告级"无孤儿结论"（A11—A13，已由 Founder 移出本任务，交由预检后规划工作处理）。

```text
V1_REBASE_EP00_CURRENT = DONE
next_stage_allowed = false
```

DONE 在此仅表示：本次通用只读预检完成。**不表示**：M0 全部完成；子合同已接受；`SINGLE-ACCOUNT-SLICE-EP00` 已完成；四个共享合同已冻结；M1—M4 或任何施工已获授权。

任务分支：`task/v1-rebase-ep00-current-m0-preflight`。远程收口结果见 [collab-ledger/L5_SIDE_EFFECTS.md §SE-003](../../collab-ledger/L5_SIDE_EFFECTS.md) 与 [L3 §四 ATT-001.3](../../collab-ledger/L3_ATTEMPTS_AND_EVIDENCE.md)。
