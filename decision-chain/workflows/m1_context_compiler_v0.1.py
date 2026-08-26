"""
M1 任务上下文编译器 · 确定性状态节点
task_id: DIYU-V1-M1-NATURAL-CONTEXT-001

设计参照: decision-chain/docs/V1_M1_TASK_CONTEXT_COMPILER_DESIGN_v0.1.md

本文件是独立开发/测试用源码，最终以字符串形式嵌入 Dify Code 节点（code_language: python3）。
Dify 按 `variables:` 声明把节点输入作为关键字参数传给 main()，返回值字典的键必须与节点
`outputs:` 声明一致。

工程纪律（继承已验证的 v1_state 模式，代码本体不复用、不修改受保护资产）：
  1. 只有本节点能产出最终 call_intent / task_context_snapshot；LLM 影子节点只出扁平结构化 patch。
  2. patch 整体拒绝：任一未知字段或非法枚举值，拒绝整个 patch，不局部采纳。
  3. 失败诚实：不编造原因，不假装已完成。
  4. open_threads 补终态 HANDLED（v1_state 的 OPEN/SURFACED 二值在此基础上扩展，互不覆盖）。

**未决（需 Reviewer/Founder 核对，不由执行侧单方认定为新纪律）**：本批对纪律 2（整体拒绝）
的适用范围做了一处执行侧解释性收窄——UNSTATED 是 evidence_nature 的合法枚举值，不属于纪律 2
逐字写的"未知字段或非法枚举值"，因此按局部跳过处理（只跳过该条证据，本轮其余捕获照常合并、
reject_reason 不变），被跳过的事实登记进 turn_report_json、不进对话文本。这处解释尚未同步进
设计文档 §六.2（V1_M1_TASK_CONTEXT_COMPILER_DESIGN_v0.1.md:142，该行是 AU-05 的通过判据原文，
逐字写的是"整体拒绝"）。当前代码行为按此解释运行，理由是与 CLAUDE.md「资料不足时不得整任务
拒绝」及共享合同一 §五 一致；**但它是否成立属于验收判据的解释，须由 Reviewer/Founder 核对后
才能写进设计文档**，在此之前不作为已确立的纪律陈述。
"""

import json

SCHEMA_VERSION = 1

# ---- CAP-01/02/04/06/07/08：当前有物理路由入口的六项能力 ----
# CAP-03（M3）/ CAP-05（创意锦标赛）当前无物理入口，故不在此枚举中；
# call_intent 对它们如实标记 BLOCKED / NO_PHYSICAL_ENTRY_YET，不伪造入口。
CAPABILITIES = [
    "MATRIX",
    "CAMPAIGN",
    "CONTENT_BRIEF",
    "CREATIVE_SCRIPT",
    "PRODUCTION_DIRECTOR",
    "PUBLISHING_PACKAGING",
]
NO_ENTRY_CAPABILITIES = ["SINGLE_ACCOUNT_OPERATION", "CREATIVE_TOURNAMENT"]  # CAP-03 / CAP-05

# 给对话 LLM 的人话标签：dialogue_directive 面向对话 LLM 组织自然语言，不得把内部枚举代码
# （如 "MATRIX"）原样拼进指令文本——这类代码本质是 Prompt 内部字段值，chat LLM 系统提示词
# 明确禁止"出现 Prompt 内部字段名"，直接拼代码会被它当作用户说过的原话复述出来（真实发现，
# 见 evidence/V1_M1_CANDIDATE_RUN_001.md CE-A2）。
CAPABILITY_LABEL_ZH = {
    "MATRIX": "账号矩阵",
    "CAMPAIGN": "经营任务策划",
    "CONTENT_BRIEF": "内容 Brief",
    "CREATIVE_SCRIPT": "创意脚本",
    "PRODUCTION_DIRECTOR": "成片导演",
    "PUBLISHING_PACKAGING": "发布与打包",
    "SINGLE_ACCOUNT_OPERATION": "单账号持续运营",
    "CREATIVE_TOURNAMENT": "创意锦标赛",
}

# _capability_input_status 里唯一会产出的四个 block_reason 代码，同理不得原样拼进
# dialogue_directive；call_intent_json（机器可读、不面向用户）仍保留原始代码。
BLOCK_REASON_LABEL_ZH = {
    "NO_CURRENT_TASK_STATED": "还没有听你说过具体任务内容",
    "NO_TASK_OR_GOAL_STATED": "还没有听你说过具体任务或目标",
    "NO_PHYSICAL_ENTRY_YET": "这项能力目前还没有可以实际调用的入口",
    "UNKNOWN_CAPABILITY": "无法识别这项能力",
}

VALID_TEMPORAL_SCOPE = ["UNSTATED", "ONE_ITEM", "CYCLE", "LONG_TERM"]
VALID_CONFIRMATION_SIGNAL = ["NONE", "AFFIRM", "DECLINE"]
VALID_ROUTE_INTENT = ["DISCUSS", "FOCUS", "EXECUTE_REQUEST", "CANCEL", "OUT_OF_SCOPE"]
VALID_REQUESTED_CAPABILITY = ["NONE"] + CAPABILITIES
VALID_DISCRETION = ["UNSTATED", "ALLOWED", "NOT_ALLOWED"]
DISCRETION_KEYS = ["plot_allowed", "remix_allowed", "conflict_allowed", "controversy_allowed"]

# 经营目标类别（设计文档 §二 #4 / 共享合同一 §二.4）。**是集合不是单值**：合同逐字要求
# "须能表达账号／周期层面的'混合'而非强制单选"，所以快照里的物理承载是顶层数组
# business_goal_categories[]，patch 侧每轮只出一个类别（扁平枚举，沿用不引入嵌套/数组的
# DeepSeek V4 Flash 约束），由 _merge_patch 去重 append 成集合。
# UNSTATED 是"这一轮没表达经营目标类别"的哨兵，不写入数组。
VALID_BUSINESS_GOAL_CATEGORY = [
    "UNSTATED",
    "LONG_TERM_VALUE",
    "ACCOUNT_GROWTH",
    "FOLLOWER_GROWTH",
    "TRAFFIC",
    "GMV",
    "LEADS",
    "STORE_VISIT",
]

# ---- evidence_bundle 的维度词表（共享合同一 §三 五行 ＋ Execution Prompt v1.2 §4.3 两项）----
#
# **维度来源如实对照**（设计文档 §三 有同一张对照表，两处必须一致；此前代码与文档都只笼统
# 写"五个正交维度"，没写清楚哪一维出自哪份真源，现补齐）：
#   nature / provenance / confirmation / scope / availability
#       ← 共享合同一 §三 逐行对应的五个正交维度（信息性质／来源与证据／确认与生命周期状态／
#         作用域与有效期／可用性状态）。
#   permission / freshness
#       ← Execution Prompt v1.2 §4.3 逐字要求「对进入上下文的事实或产物至少保留：source、
#         permission、scope、freshness、confirmation」；共享合同一 §二 末段（「来源、权限、
#         可信度差异保留」）与 §五（「不表示…用户授权…适用范围、时效、确认状态相同」）同向。
#         freshness 同时承接共享合同一 §三「作用域与有效期」那一行的后半句「生效时间是否仍
#         有效」——在此之前没有任何字段承载它，它被含混地折进了 availability 的 STALE 取值。
#
# **已知不对齐（本批不动，只如实登记，待 Reviewer 裁决）**：共享合同一 §三 的可用性状态有
# 6 个取值（已具备｜未知｜未提供｜**不适用**｜拒绝提供｜已失效），本词表只有 5 个（缺"不适用"）。
# 自行补一个 NOT_APPLICABLE 等于执行侧单方修改共享合同的枚举空间，不在本批授权范围内。
#
# EVIDENCE_DIMENSION_VOCAB 的定位：它是上述维度取值空间的**机器可读声明**，供下游消费方与
# 未来的写入路径引用，不是"这几张表都在被本文件执行"的意思。逐条如实标注 P0 内的真实代码
# 读者，避免把声明当成已实现的能力（计划不等于现实）：
#   nature       ── **P0 唯一有真实代码读者的维度**：_merge_evidence_item 写入前的取值门禁
#                   （词表外取值抛 ValueError）。
#   provenance   ── **P0 无代码读者**，纯声明（写入恒为 USER_DIRECT）。
#   confirmation ── **P0 无代码读者**，纯声明（写入恒为 SYSTEM_TENTATIVE）。
#   scope        ── **P0 无代码读者**（写入只取 patch 值或 UNSTATED；patch 侧的合法性由
#                   VALID_EVIDENCE_SCOPE 承担）。此处纯声明。
#   availability ── **P0 无代码读者**，纯声明。P0 恒为 AVAILABLE，其余四值不可达，
#                   已由 _compute_gaps 的结构性缺口条目如实登记。
#   permission   ── **P0 无代码读者**，纯声明。P0 唯一可达值是 OWNED_BY_USER：本环境唯一的
#                   信息入口是用户自己陈述自己的经营信息，不存在第三方材料的使用权限问题。
#                   THIRD_PARTY_REQUIRES_CONSENT / UNKNOWN 要等真正的材料／历史产物输入通道
#                   建成后才可能被真实使用。**刻意不新增 LLM patch key**——本环境没有任何
#                   可变的权限信息来源，硬加一个模型字段只是制造"这一维在被判断"的假象。
#   freshness    ── **P0 无代码读者**，纯声明。P0 唯一可达值是 FRESH：证据刚被用户在当前
#                   会话里说出口，天然新鲜；P0 没有生命周期时钟，无法判断一条证据是否已过期，
#                   所以 STALE / UNKNOWN 不可达。同样不新增 LLM patch key，理由同上。
#
# 为什么 provenance / confirmation 这两维没有、也不需要一个运行时守卫：P0 的
# _merge_evidence_item 是**纯追加、永不修改既有条目**，所以两条冻结硬约束
#   - 「系统推断不因为被写入持久化就升级为用户确认事实」
#   - 「参考资料和历史产物不得覆盖用户已经确认的事实」
# 在 P0 是**结构上天然满足**的——没有任何"修改既有条目"的动作存在，也就没有东西可违反。
# 真正需要"修改既有条目"这个动作的那一批实现（M4/M5，比如未来的按字段用户确认交互、
# runtime_evidence 的外部写入）才需要引入一个真实的运行时守卫，届时由那一批连同它的调用方
# 一起设计。现在先写一个零调用方的守卫，只是把"未来想法"伪装成"已实现能力"。
EVIDENCE_DIMENSION_VOCAB = {
    "nature": ["FACT", "PREFERENCE", "REFERENCE", "SYSTEM_INFERENCE"],
    "provenance": [
        "USER_DIRECT",
        "SOURCED_MATERIAL",
        "VALID_HISTORICAL_ARTIFACT",
        "AUTHORIZED_EXTERNAL",
        "SYSTEM_DERIVED",
    ],
    "confirmation": ["USER_CONFIRMED", "SYSTEM_TENTATIVE", "REJECTED", "SUPERSEDED", "EXPIRED"],
    "scope": ["THIS_ITEM_ONLY", "THIS_CYCLE_ONLY", "THIS_ACCOUNT", "LONG_TERM_SUBJECT"],
    "availability": ["AVAILABLE", "UNKNOWN", "NOT_PROVIDED", "DECLINED", "STALE"],
    "permission": ["OWNED_BY_USER", "THIRD_PARTY_REQUIRES_CONSENT", "UNKNOWN"],
    "freshness": ["FRESH", "STALE", "UNKNOWN"],
}

# LLM patch 侧允许的 nature 取值：刻意**不含 SYSTEM_INFERENCE**——系统推断只能由确定性代码
# 写入，模型不得给自己对用户原话的复述贴上"系统判断"标签。UNSTATED 是"这一轮没有可记录信息"
# 的哨兵（P0 没有任何代码路径产出 SYSTEM_INFERENCE，不造假的系统推断生成器）。
VALID_EVIDENCE_NATURE_PATCH = ["UNSTATED", "FACT", "PREFERENCE", "REFERENCE"]

# scope 比合同词表多一个 UNSTATED 哨兵：用户没说明适用层级时只能如实记 UNSTATED，不得替用户
# 选一个（共享合同一 §三 反例：不得把"这条不要剧情"静默扩张成长期规则）。**消费方不得把
# UNSTATED 扩宽成 LONG_TERM_SUBJECT 或任何具体层级**，也不得从 current_task.temporal_scope
# 推导——任务的时间作用域不等于某条证据的适用层级。
VALID_EVIDENCE_SCOPE = ["UNSTATED"] + EVIDENCE_DIMENSION_VOCAB["scope"]

# 影子节点必须原样返回的扁平字段集合（v0.1 最小切片覆盖 P0 核心行为；v0.2 扩展第一批：
# account_stage / expression_discretion / capacity_triad；v0.3 扩展第二批：evidence_bundle[]
# 的三个粗粒度信号 evidence_text / evidence_nature / evidence_scope）。
#
# v0.3 采用的是设计文档 §七 官方登记的**降级路径**：「LLM 只出粗粒度信号，五维度由确定性
# 代码从上下文推导默认值」。依据是 v1_shadow（同类组件）设计说明里的既有观察——DeepSeek
# V4 Flash 只能稳定处理扁平字符串/枚举，不支持嵌套对象（decision-chain/evidence/
# V1_DIALOGUE_ORCHESTRATION_REPAIR_001_EVIDENCE.md:68）。因此这里仍然只加扁平字符串/枚举，
# 不引入嵌套对象或布尔，不重跑已有先例证据的那条路线。
#
# gaps[] 零新增 patch key（完全由确定性代码从既有快照状态推导）；market_observations[] 与
# runtime_evidence[] 本批 DEFER（无真实产出通道、M1 内无消费者、关键字段无法诚实填充），
# 理由见 _default_snapshot 里对应注释与 _compute_gaps 的结构性缺口条目。
#
# v0.4 扩展第三批：goal_structure 的 secondary_goals[]／priority_order[] 与顶层
# business_goal_categories[]（设计文档 §二 #3/#4）。这三项此前在快照里要么有物理数组却
# **没有任何写入路径**（前两个恒为空数组），要么连物理字段都没有（第三个）——即"结构在、
# 语义不可达"。同样只加扁平字符串/枚举，每轮各最多一条，由 _merge_patch 去重 append。
PATCH_KEYS = {
    "route_intent",
    "current_task_text",
    "temporal_scope",
    "primary_goal_text",
    "secondary_goal_text",
    "priority_order_text",
    "non_sacrifice_constraint_text",
    "business_goal_category",
    "requested_capability",
    "confirmation_signal",
    "side_question",
    "user_message_summary",
    "account_stage_text",
    "plot_allowed",
    "remix_allowed",
    "conflict_allowed",
    "controversy_allowed",
    "desired_output_text",
    "cycle_available_text",
    "baseline_text",
    "evidence_text",
    "evidence_nature",
    "evidence_scope",
}


# 影子节点这一轮没有产出一份完整候选 patch 的可靠信号，**不是**格式校验失败。
#
# 判据的依据（DSL 层已成立的不变量，不需要新增任何显式失败标记）：m1_shadow 的
# structured_output.schema 把全部 PATCH_KEYS 都放进 `required`（由 DSL 防漂移单测锁定两者
# 集合相等），所以影子节点**真正成功**产出的合法输出，无论内容多"空"，字典里一定有全部
# key（值可能是 UNSTATED / NONE / 空字符串，但 key 本身一定在）。只有 error_strategy:
# default-value 的降级路径才会产出字面上完全没有这些 key 的空字典 {}。因此"patch 是 dict
# 但缺少一个或多个必需 key"这件事本身，就是"影子节点失败了"的可靠信号，和"影子节点成功、
# 但这轮确实没有新信息"（后者 key 全在、只是值平淡）结构性不同。
#
# 修复的是一个真实 bug：此前 {} 会被 _validate_patch 判成完全合法的"什么都没说"的一轮
# （没有未知字段、每个字段都走 .get(key, 默认值) 的宽松取值），于是 patch_ok=true、
# reject_reason 为空，dialogue_directive 断言"不是落库失败，就是还没有形成任务"——在影子
# 节点真的失败的场景下这是假话，且系统不留任何痕迹。违反 M1-AC-10「内部失败诚实可恢复，
# 不伪装成功」与宪法「不编造失败原因」。
SHADOW_NODE_FAILED = "SHADOW_NODE_FAILED"


def _default_snapshot():
    return {
        "schema_version": SCHEMA_VERSION,
        "task_id": None,
        "revision": 0,
        "current_task": {"text": None, "temporal_scope": "UNSTATED", "source_ref": "USER_DIRECT"},
        "goal_structure": {
            "primary_goal": None,
            "secondary_goals": [],
            "priority_order": [],
            "non_sacrifice_constraints": [],
        },
        # 经营目标类别（设计文档 §二 #4）：**集合，不是单值**——共享合同一 §二.4 逐字要求
        # 能表达账号／周期层面的"混合"而非强制单选。v0.4 之前快照里根本没有这个物理字段，
        # 设计文档 §二 #4 的语义完全没有承载位置；现由 business_goal_category 这个扁平
        # patch key 逐轮 append（去重、UNSTATED 不写入）。
        "business_goal_categories": [],
        # 账号阶段：自由文本 + confirmation 维度（设计文档 §二 #5）。P0 扁平 patch 每轮只有
        # 一个通用 confirmation_signal，无法可靠归因到"正在确认的是账号阶段"这一具体字段，
        # 如实固定为 SYSTEM_TENTATIVE，不伪造 USER_CONFIRMED（与 open_threads 的已知限制
        # 同一类问题：真正的按字段确认状态机需要设计判断，不在本批擅自决定）。
        "account_stage": {"text": None, "confirmation": "SYSTEM_TENTATIVE"},
        # 表达裁量与风险边界（设计文档 §二 #6）：剧情/二创/冲突/争议四项裁量，
        # 每项 ALLOWED｜NOT_ALLOWED｜UNSTATED。
        "expression_discretion": {
            "plot_allowed": "UNSTATED",
            "remix_allowed": "UNSTATED",
            "conflict_allowed": "UNSTATED",
            "controversy_allowed": "UNSTATED",
        },
        # 产能三分（设计文档 §二 #7）：期望发布量／当前周期可用产能／基线产能，
        # 三者分别承载，不得静默取其一覆盖三个。
        "capacity_triad": {"desired_output": None, "cycle_available": None, "baseline": None},
        # 可用事实/偏好/参考及其全部维度（设计文档 §二 #9 + 维度表）。纯追加，永不修改既有条目：
        # 冻结硬约束「参考资料和历史产物不得覆盖用户已经确认的事实」在 P0 因此天然不可违反。
        "evidence_bundle": [],
        # 市场观察（设计文档 §二 #10）：本批 **DEFER，未实现**。
        # M1 候选环境里没有任何合法的市场数据通道（DSL 无 Tool 节点、file_upload.enabled=False、
        # 无联网；仓库红线与共享合同一 §八 均把全平台市场情报爬虫列为非目标），消费者
        # CAP-03/CAP-05 又正是当前 NO_ENTRY_CAPABILITIES；observed_at 由编译器补即伪造采集
        # 时间，validity 由代码评级即新增自动评分器。
        # **口径（不得只留空数组）**：孤零零的 [] 会被下游读成"查过了，没有"——那是不实主张
        # （共享合同一 §六「没有市场资料时不得声称已完成市场比较」）。因此 _compute_gaps 恒定
        # 输出一条 market_observations 的 DEGRADED/NOT_CAPTURED_IN_P0_SNAPSHOT 缺口，二者必须
        # 同时存在，并由单测锁定。**该配对成立于完整视图**（_compute_gaps(...,
        # include_structural=True)，即 project_content_task 给下游的那一份）；持久化快照的
        # gaps 只留动态子集，因为这条常量条目内容恒定、读代码常量即可，不必逐轮序列化。
        "market_observations": [],
        # 缺失信息与已降级项（设计文档 §二 #11）。**当轮派生结果的快照，不是累积状态**：
        # 每轮由 _compute_gaps 整体重算覆写，消费方要么用它、要么自己重算，二者等价。
        # 持久化的是 include_structural=False 的动态子集（空快照上 13 条）；完整 22 条视图由
        # 需要它的调用点自行重算，见 _compute_gaps 的 include_structural 说明。
        "gaps": [],
        "allowed_capabilities": [],  # 由 call_intent 现算，不在快照里静态存
        "open_threads": [],
        # 运行中新增的联网/外部证据（设计文档 §二 #14）：本批 **DEFER，未实现**。
        # 该语义的前提是运行期真的发生过一次外部获取动作，而本环境没有任何工具/联网节点，
        # 这个动作在 P0 不可能发生，任何写入都是无中生有；obtained_at / applicable_scope 只有
        # 真正执行获取的那一侧知道，编译器代填即伪造取证时间与适用范围。真正的生产者在
        # M4/M5（共享合同一 §四：外部搜索、素材读取等工具在 Skill 运行期调用）。
        # 未来实现口径：由发起获取的一侧在获取完成后显式追加，条目至少携带
        # {source, obtained_at（获取方给）, applicable_scope（获取方声明）, snapshot_version=写入
        # 时的 revision}；在 evidence 语义上对应 provenance=AUTHORIZED_EXTERNAL、
        # confirmation=SYSTEM_TENTATIVE——**外部证据同样不因为写进快照就变成用户确认事实**。
        # 该批实现一旦引入"修改既有条目"的动作，就必须同时引入一个真实的运行时守卫来承接两条
        # 冻结硬约束（P0 靠"纯追加"这个结构天然满足，所以 P0 不需要该守卫）。
        # 同样不得只留空数组（理由与配对成立的视图同 market_observations，见 _compute_gaps
        # 结构性条目与 include_structural 说明）。
        "runtime_evidence": [],
        "last_confirmation_signal": "NONE",
        "last_route_intent": None,
    }


def _validate_patch(patch):
    """整体校验：任一未知键或非法枚举值，整体拒绝，返回 (ok: bool, reason: str)。"""
    if not isinstance(patch, dict):
        return False, "PATCH_NOT_OBJECT"
    unknown = set(patch.keys()) - PATCH_KEYS
    if unknown:
        return False, "PATCH_UNKNOWN_FIELDS:" + ",".join(sorted(unknown))
    ts = patch.get("temporal_scope", "UNSTATED")
    if ts not in VALID_TEMPORAL_SCOPE:
        return False, "ILLEGAL_ENUM:temporal_scope:" + str(ts)
    cs = patch.get("confirmation_signal", "NONE")
    if cs not in VALID_CONFIRMATION_SIGNAL:
        return False, "ILLEGAL_ENUM:confirmation_signal:" + str(cs)
    ri = patch.get("route_intent")
    if ri is not None and ri not in VALID_ROUTE_INTENT:
        return False, "ILLEGAL_ENUM:route_intent:" + str(ri)
    rc = patch.get("requested_capability", "NONE")
    if rc not in VALID_REQUESTED_CAPABILITY:
        return False, "ILLEGAL_ENUM:requested_capability:" + str(rc)
    for key in DISCRETION_KEYS:
        val = patch.get(key, "UNSTATED")
        if val not in VALID_DISCRETION:
            return False, "ILLEGAL_ENUM:" + key + ":" + str(val)
    # v0.3：只追加两条枚举校验，沿用既有整体拒绝语义。**不新增任何跨字段整体拒绝规则**——
    # 既有"整体拒绝"纪律的适用范围是逐字写死的"任一未知字段或非法枚举值"（本文件 docstring、
    # 设计文档 §六.2）。"evidence_text 非空但 evidence_nature=UNSTATED"用的是合法枚举值，
    # 不属于该范围，按局部降级处理（见 _merge_evidence_item），不整轮作废用户这一轮说的话。
    # **这处收窄是执行侧解释、尚未同步设计文档 §六.2，未决状态见模块 docstring 的"未决"段。**
    en = patch.get("evidence_nature", "UNSTATED")
    if en not in VALID_EVIDENCE_NATURE_PATCH:
        return False, "ILLEGAL_ENUM:evidence_nature:" + str(en)
    es = patch.get("evidence_scope", "UNSTATED")
    if es not in VALID_EVIDENCE_SCOPE:
        return False, "ILLEGAL_ENUM:evidence_scope:" + str(es)
    # v0.4：同样只追加一条枚举校验，整体拒绝语义不变（secondary_goal_text /
    # priority_order_text 是自由文本，没有枚举空间可校验）。
    bgc = patch.get("business_goal_category", "UNSTATED")
    if bgc not in VALID_BUSINESS_GOAL_CATEGORY:
        return False, "ILLEGAL_ENUM:business_goal_category:" + str(bgc)
    return True, ""


def _merge_evidence_item(snap, patch):
    """把本轮 patch 的单条粗粒度证据信号写入 evidence_bundle[]，返回
    (appended: bool, dropped_incomplete: bool)。

    **P0 纯追加：任何情况下都不修改既有条目。** 这件事本身就是冻结约束二（参考资料和历史
    产物不得覆盖用户已经确认的事实）的完整实现——本函数只有 append 一条路径，没有任何修改
    既有条目的动作，所以该约束在 P0 结构上不可违反，不依赖也不需要任何独立的运行时守卫
    去保证。（真正需要"修改既有条目"这个动作的实现在 M4/M5，守卫由那一批连同它的调用方
    一起引入。）

    冻结约束一（系统推断不因为被写入持久化就升级为用户确认事实）的落地：confirmation 是
    字面常量 SYSTEM_TENTATIVE，本函数不接受任何入参覆盖。轮级 confirmation_signal=AFFIRM 是
    对"当前正在确认的事项"的回应，无法归因到具体哪一条证据，**不得**被解释成对某条证据的
    用户确认；同理轮级 DECLINE 也不得写成 REJECTED（与 v0.2 account_stage.confirmation 固定
    SYSTEM_TENTATIVE 是同一条已裁决的理由）。

    七个维度的默认值（P0 只有 nature / scope 两维可以偏离，其余五维不可偏离——偏离需要新的
    物理通道：资料上传／工具调用／按字段确认交互／生命周期时钟，属 M4/M5 范围）：
      nature       ← LLM 给出（唯一只有模型能读出的维度：代码分不清"我们店在杭州"是事实、
                     "我不喜欢强 CTA"是偏好），代码不得代填默认值
      provenance   ← 恒为 USER_DIRECT（本环境唯一的信息入口就是用户这一轮的自然语言；
                     写成 SOURCED_MATERIAL 等值即伪造来源，所以也不需要 LLM 字段）
      confirmation ← 恒为 SYSTEM_TENTATIVE（见上）
      scope        ← 取 patch 值，缺省 UNSTATED；**绝不从 current_task.temporal_scope 推导**
      availability ← 恒为 AVAILABLE（本数组只承载"已经拿到的信息"；UNKNOWN/NOT_PROVIDED/
                     DECLINED/STALE 属于"没拿到"，归 gaps[]；STALE/EXPIRED 还需要生命周期
                     时钟，P0 没有，已由 _compute_gaps 结构性条目如实登记）
      permission   ← 恒为 OWNED_BY_USER（Execution Prompt v1.2 §4.3 逐字要求的权限维度）。
                     本环境唯一的输入渠道是用户自己陈述自己的经营信息，不涉及第三方材料的
                     使用权限问题，所以 P0 唯一可达值就是它；THIRD_PARTY_REQUIRES_CONSENT /
                     UNKNOWN 要等材料／历史产物输入通道真正建成后才可能被真实使用。
                     **不接受任何入参覆盖，也不新增 LLM 字段**——没有可变的信息来源时，加一个
                     模型字段只会制造"这一维在被判断"的假象。已由 _compute_gaps 结构性条目登记。
      freshness    ← 恒为 FRESH（Prompt §4.3 的时效维度，同时承接共享合同一 §三"作用域与
                     有效期"后半句"生效时间是否仍有效"）。这条证据刚被用户在当前会话里说出口，
                     天然新鲜；P0 没有生命周期时钟，无法判断一条证据是否"已过期"，所以 STALE /
                     UNKNOWN 不可达。同样是字面常量、不接受入参覆盖、不新增 LLM 字段，
                     已由 _compute_gaps 结构性条目登记。
    """
    text = (patch.get("evidence_text") or "").strip()
    if not text:
        return False, False

    nature = patch.get("evidence_nature", "UNSTATED")
    if nature not in VALID_EVIDENCE_NATURE_PATCH:
        # 正常路径下 _validate_patch 已整体拒绝；这里是 helper 被直接调用时的取值门禁，
        # 防止绕过校验写进一个词表外的（或 SYSTEM_INFERENCE 这种模型不得自称的）性质。
        raise ValueError("ILLEGAL_EVIDENCE_NATURE:" + str(nature))
    if nature == "UNSTATED":
        # 维度不全（模型给了原话却没给性质）：**只跳过这一条证据**，本轮其余捕获（任务、
        # 目标、产能、裁量……）照常合并，reject_reason 保持不变，dialogue_directive 不变。
        # 不整体拒绝的四条理由见 _validate_patch 注释与设计说明；代码无法诚实推导一条信息
        # 是事实还是偏好，所以宁可不写，也不补一个默认 nature。这一轮的丢弃由
        # turn_report_json.evidence_dropped_incomplete 如实登记在不面向用户的通道里。
        return False, True

    # 与 _compute_gaps / compute_call_intent 的 `.get(...) or []` / isinstance 防御同一风格：
    # helper 可能被直接喂一份手工构造的、或早于 v0.3 持久化的快照（没有这个顶层键）。
    snap.setdefault("evidence_bundle", [])

    for item in snap["evidence_bundle"]:
        # 去重沿用 non_sacrifice_constraints 的 `not in` 先例：同 text 已存在则不追加、
        # 不 bump revision，也不修改既有条目。
        if item.get("text") == text:
            return False, False

    snap["evidence_bundle"].append(
        {
            "id": "ev_%03d" % (len(snap["evidence_bundle"]) + 1),
            "text": text,
            "nature": nature,
            "provenance": "USER_DIRECT",
            "confirmation": "SYSTEM_TENTATIVE",
            "scope": patch.get("evidence_scope", "UNSTATED"),
            "availability": "AVAILABLE",
            "permission": "OWNED_BY_USER",
            "freshness": "FRESH",
            # 取增量前的 revision，与 open_threads.raised_at_revision 同一时序先例。
            # 只有这一个整数，没有变更历史、没有事件流、没有回放——不是事件溯源。
            "captured_at_revision": snap["revision"],
        }
    )
    return True, False


def _merge_patch(snap, patch):
    """把校验通过的 patch 合并进快照。只有用户本轮真的说出口的内容才写入
    （不得把 §四 冻结的"不得把用户没说的目标写成已确认"违反）。

    返回 (snap, changed, evidence_dropped_incomplete)。第三个值只用于机器可读的
    turn_report_json，不进入 dialogue_directive、不影响 patch_ok。
    """
    changed = False

    text = (patch.get("current_task_text") or "").strip()
    if text:
        snap["current_task"]["text"] = text
        snap["current_task"]["temporal_scope"] = patch.get("temporal_scope", "UNSTATED")
        changed = True

    goal = (patch.get("primary_goal_text") or "").strip()
    if goal:
        snap["goal_structure"]["primary_goal"] = goal
        changed = True

    # 次目标：与 non_sacrifice_constraints 同构（自由文本、每轮最多一条、`not in` 去重、
    # 追加不覆盖）——次目标彼此不互斥，用户说"也想兼顾 A""也想兼顾 B"是在累加，不是在
    # 否定前一条，所以追加语义正确。此前该数组有物理位置却没有任何写入路径，恒为空数组。
    sec_goal = (patch.get("secondary_goal_text") or "").strip()
    if sec_goal and sec_goal not in snap["goal_structure"]["secondary_goals"]:
        snap["goal_structure"]["secondary_goals"].append(sec_goal)
        changed = True

    # 优先级：**替换语义，不是追加**。"优先级"本质是一句排序断言而不是一条独立事实——
    # 用户先说"涨粉优先于转化"、后说"转化优先于涨粉"，后一句是对前一句的更正而不是并列
    # 陈述，追加会让快照同时携带两条互相矛盾的排序（对抗式审查真实发现的问题，不是假设）。
    # 保留数组形状（设计文档 §二 #3 declares 为 `priority_order[]`）但语义上只保留用户
    # 最近一次的完整表述——一句话本身可能已经把多个目标的相对顺序都说清楚了，不需要也
    # 不应该由代码去拆解、合并成跨轮的排序图。
    prio = (patch.get("priority_order_text") or "").strip()
    if prio and snap["goal_structure"]["priority_order"] != [prio]:
        snap["goal_structure"]["priority_order"] = [prio]
        changed = True

    nsc = (patch.get("non_sacrifice_constraint_text") or "").strip()
    if nsc and nsc not in snap["goal_structure"]["non_sacrifice_constraints"]:
        snap["goal_structure"]["non_sacrifice_constraints"].append(nsc)
        changed = True

    # 经营目标类别：集合语义（可混合），UNSTATED 是哨兵不写入，去重同上。
    # setdefault 与 _merge_evidence_item 同一风格：helper 可能被直接喂一份手工构造的、
    # 或早于 v0.4 持久化的快照（没有这个顶层键）；走 main() 时升级循环已经补齐。
    bgc = patch.get("business_goal_category", "UNSTATED")
    if bgc and bgc != "UNSTATED":
        snap.setdefault("business_goal_categories", [])
        if bgc not in snap["business_goal_categories"]:
            snap["business_goal_categories"].append(bgc)
            changed = True

    side_q = (patch.get("side_question") or "").strip()
    if side_q:
        tid = "thread_%03d" % (len(snap["open_threads"]) + 1)
        snap["open_threads"].append(
            {"id": tid, "text": side_q, "raised_at_revision": snap["revision"], "status": "OPEN"}
        )
        changed = True

    cs = patch.get("confirmation_signal", "NONE")
    if cs != "NONE":
        snap["last_confirmation_signal"] = cs
        changed = True

    ri = patch.get("route_intent")
    if ri:
        snap["last_route_intent"] = ri

    stage = (patch.get("account_stage_text") or "").strip()
    if stage:
        snap["account_stage"]["text"] = stage
        changed = True

    for key in DISCRETION_KEYS:
        val = patch.get(key, "UNSTATED")
        if val != "UNSTATED":
            snap["expression_discretion"][key] = val
            changed = True

    desired = (patch.get("desired_output_text") or "").strip()
    if desired:
        snap["capacity_triad"]["desired_output"] = desired
        changed = True

    cycle_avail = (patch.get("cycle_available_text") or "").strip()
    if cycle_avail:
        snap["capacity_triad"]["cycle_available"] = cycle_avail
        changed = True

    baseline = (patch.get("baseline_text") or "").strip()
    if baseline:
        snap["capacity_triad"]["baseline"] = baseline
        changed = True

    # evidence_bundle 必须在 revision 自增之前合并：captured_at_revision 取的是增量前的
    # revision（与 open_threads.raised_at_revision 同一时序先例）。
    evidence_appended, evidence_dropped_incomplete = _merge_evidence_item(snap, patch)
    if evidence_appended:
        changed = True

    if changed:
        snap["revision"] = snap["revision"] + 1

    return snap, changed, evidence_dropped_incomplete


# ---- gaps[]：缺失信息与已降级项（设计文档 §二 #11）----
#
# 零新增 LLM patch key：完全由确定性代码从既有快照状态推导（None 值、UNSTATED 哨兵、本批
# 明确不实现的结构性语义清单）。只做"有值/无值/是不是哨兵"的布尔判断，不给任何东西打分或
# 排优先级（阻塞与否直接复用既有 block_reason，不是新算的分数）。
#
# 三类语义靠 status + degraded_to 的组合区分，让下游能判断"能不能追问用户"：
#   结构性未承载（**不得向用户追问**，问了也没地方放）：DEGRADED / NOT_CAPTURED_IN_P0_SNAPSHOT
#   有承载位置但用户还没说（可追问，但仍受"只追问真正阻塞的一项"约束）：MISSING / None
#   有哨兵值继续运行（下游不得推定默认值）：DEGRADED / "UNSTATED"
#
# 条目严格只有设计文档 §二 #11 的三个键，不加第四个。
GAP_NOT_CAPTURED = "NOT_CAPTURED_IN_P0_SNAPSHOT"

# 下面这 9 条是**内容恒定的常量**（不随对话状态变化），因此不进逐轮持久化快照——它们由
# _compute_gaps(..., include_structural=True) 在需要完整合规视图的调用点（project_content_task）
# 现拼出来，需要它们的消费方也可以直接读本常量。见 _compute_gaps 的 include_structural 说明。
P0_STRUCTURAL_GAPS = [
    # 本批范围外、快照里根本没有承载位置的语义。一份自称"缺口登记"的数组如果隐瞒已知缺口，
    # 本身就是误导，所以 #1/#8 这两条虽然不在本批实现范围内，也如实登记。
    # **v0.4 移除了 business_goal_categories（设计文档 §二 #4）**：它已经有真实的物理承载
    # （顶层数组 + business_goal_category patch key），再标 NOT_CAPTURED_IN_P0_SNAPSHOT 就是
    # 一句假话。它改由 _compute_gaps 按"有承载位置但用户还没说"登记为动态的 MISSING/None
    # ——语义差别是实的：结构性未承载**不得向用户追问**（问了也没地方放），MISSING 可追问。
    {"field_ref": "subject_scope", "status": "DEGRADED", "degraded_to": GAP_NOT_CAPTURED},
    {"field_ref": "cycle_ref", "status": "DEGRADED", "degraded_to": GAP_NOT_CAPTURED},
    # 本批明确 DEFER 的两个数组：空数组 + 这两条缺口条目在**完整视图里必须同时存在**
    # （include_structural=True，即 project_content_task 给下游的那一份），否则空数组会被
    # 下游读成"查过了，没有"（不实主张）。已由单测锁定，不只是注释。
    {"field_ref": "market_observations", "status": "DEGRADED", "degraded_to": GAP_NOT_CAPTURED},
    {"field_ref": "runtime_evidence", "status": "DEGRADED", "degraded_to": GAP_NOT_CAPTURED},
    # 确认维度五个取值里 P0 只可达 SYSTEM_TENTATIVE（没有按字段的用户确认通道），
    # 可用性维度里 STALE/EXPIRED 需要生命周期时钟、P0 没有。如实登记为结构缺口。
    {
        "field_ref": "account_stage.confirmation",
        "status": "DEGRADED",
        "degraded_to": "ALWAYS_SYSTEM_TENTATIVE_NO_PER_FIELD_CONFIRM_CHANNEL",
    },
    {
        "field_ref": "evidence_bundle[].confirmation",
        "status": "DEGRADED",
        "degraded_to": "ALWAYS_SYSTEM_TENTATIVE_NO_PER_FIELD_CONFIRM_CHANNEL",
    },
    {
        "field_ref": "evidence_bundle[].availability",
        "status": "DEGRADED",
        "degraded_to": "ALWAYS_AVAILABLE_NO_LIFECYCLE_CLOCK",
    },
    # v0.4 新增的两个维度同理：两者在 P0 都只有一个可达值，不是真正被逐条判断出来的结果。
    # 写进条目却不登记降级，等于让下游把"恒定常量"读成"系统判断过权限/时效"。
    {
        "field_ref": "evidence_bundle[].permission",
        "status": "DEGRADED",
        "degraded_to": "ALWAYS_OWNED_BY_USER_NO_THIRD_PARTY_MATERIAL_CHANNEL",
    },
    {
        "field_ref": "evidence_bundle[].freshness",
        "status": "DEGRADED",
        "degraded_to": "ALWAYS_FRESH_NO_LIFECYCLE_CLOCK",
    },
]


def _compute_gaps(snapshot, include_structural=True):
    """快照 → 当轮缺口清单。**纯函数**：只读入参、返回新列表，不写入 snapshot。

    每轮整体重算、不留历史，快照里只有当下这一份清单，不存在缺口变更流水（不是事件溯源）。

    include_structural：控制 P0_STRUCTURAL_GAPS 那 9 条**内容恒定的常量条目**是否包含在
    返回值里。这 9 条不随对话状态变化，不携带任何"这一轮/这次会话独有"的信息——需要它们的
    消费方直接读代码常量即可，逐轮序列化进 Dify 会话变量纯属浪费，还会让持久化快照每轮都
    背着同一份不变内容。因此：
      - main() 传 include_structural=False，只持久化真正随对话状态变化的动态子集；
        compute_call_intent 的 fallback 分支同口径（non_blocking_gaps 是调用路由信号，
        不是审计副本）。
      - project_content_task 等需要**完整合规视图**的调用点传 include_structural=True
        （设计文档 §三 要求 evidence_and_gaps 完整、不摊平，两条 DEFER 数组的"空数组必须
        配 gaps 登记"口径也落在这条路径上）。
    默认值 True，保持既有调用方与手工调用的向后兼容。
    """
    gaps = [dict(g) for g in P0_STRUCTURAL_GAPS] if include_structural else []

    current_task = snapshot.get("current_task") or {}
    goal = snapshot.get("goal_structure") or {}
    stage = snapshot.get("account_stage") or {}
    triad = snapshot.get("capacity_triad") or {}
    discretion = snapshot.get("expression_discretion") or {}
    evidence = snapshot.get("evidence_bundle") or []

    if not current_task.get("text"):
        gaps.append({"field_ref": "current_task.text", "status": "MISSING", "degraded_to": None})
    if current_task.get("temporal_scope", "UNSTATED") == "UNSTATED":
        gaps.append({"field_ref": "current_task.temporal_scope", "status": "DEGRADED", "degraded_to": "UNSTATED"})

    if not goal.get("primary_goal"):
        gaps.append({"field_ref": "goal_structure.primary_goal", "status": "MISSING", "degraded_to": None})

    # v0.4：有物理承载（顶层数组）但用户还没表达过任何经营目标类别 → MISSING（可追问），
    # 不是 NOT_CAPTURED_IN_P0_SNAPSHOT（那是"没地方放、不得追问"，v0.4 之前才成立）。
    # 次目标／优先级不在此登记：它们是"允许兼顾"的可选项，没有不等于缺信息。
    if not (snapshot.get("business_goal_categories") or []):
        gaps.append({"field_ref": "business_goal_categories", "status": "MISSING", "degraded_to": None})

    if not stage.get("text"):
        gaps.append({"field_ref": "account_stage.text", "status": "MISSING", "degraded_to": None})

    # 产能三项各自独立成条，**绝不合并成一条**（共享合同一 §二.7 逐字要求三者分别承载、
    # 不得静默取其一覆盖三个）。
    for key in ("desired_output", "cycle_available", "baseline"):
        if not triad.get(key):
            gaps.append({"field_ref": "capacity_triad." + key, "status": "MISSING", "degraded_to": None})

    # 未表态不得被推定为允许或不允许，如实登记为带哨兵的降级项。
    for key in DISCRETION_KEYS:
        if discretion.get(key, "UNSTATED") == "UNSTATED":
            gaps.append({"field_ref": "expression_discretion." + key, "status": "DEGRADED", "degraded_to": "UNSTATED"})

    if not evidence:
        gaps.append({"field_ref": "evidence_bundle", "status": "MISSING", "degraded_to": None})
    elif any(item.get("scope", "UNSTATED") == "UNSTATED" for item in evidence):
        # 聚合一条即可：提醒下游"存在未声明作用域的证据"，不得自行把它扩张为长期规则。
        gaps.append({"field_ref": "evidence_bundle[].scope", "status": "DEGRADED", "degraded_to": "UNSTATED"})

    return gaps


# block_reason → 当轮真正在阻塞该能力的字段。用于把"真正阻塞的一项"从"带着继续跑的缺口"里
# 分出来（共享合同一 §五）。只是一张常量映射，不是新算的分数。
BLOCK_REASON_BLOCKING_FIELD_REFS = {
    "NO_CURRENT_TASK_STATED": ["current_task.text"],
    "NO_TASK_OR_GOAL_STATED": ["current_task.text", "goal_structure.primary_goal"],
}


def _capability_input_status(snap, cap_id):
    """对照该能力的"必需业务输入"判定 DIRECT_ENTRY_ELIGIBLE / DEGRADED_INPUT / BLOCKED。

    v0.1 只实现判据里最核心、可从当前扁平快照直接判断的部分（有无当前任务描述、
    有无主目标）；更细的必需输入项（如 Matrix 的六类企业/组织事实）快照里还没有专门
    字段承载，如实标记为 DEGRADED_INPUT 并在 block_reason 里说明缺什么，不假装已满足。
    """
    has_task = bool(snap["current_task"]["text"])
    has_goal = bool(snap["goal_structure"]["primary_goal"])

    if cap_id == "MATRIX":
        # Matrix 六类必需输入里，快照目前只能判断"是否涉及长期定位/账号结构"这一条件本身
        # 是否成立；其余五类（企业事实/组织事实/账号责任卡数量等）本设计尚未采集专门字段。
        if not has_task:
            return "BLOCKED", "NO_CURRENT_TASK_STATED"
        return "DEGRADED_INPUT", "MATRIX_REQUIRES_SIX_INPUT_CATEGORIES_SNAPSHOT_ONLY_HAS_TASK_TEXT"

    if cap_id in ("CAMPAIGN", "CONTENT_BRIEF", "CREATIVE_SCRIPT", "PRODUCTION_DIRECTOR", "PUBLISHING_PACKAGING"):
        if not has_task and not has_goal:
            return "BLOCKED", "NO_TASK_OR_GOAL_STATED"
        return "DEGRADED_INPUT", cap_id + "_REQUIRES_FULL_CONTRACT_INPUT_SNAPSHOT_ONLY_HAS_TASK_AND_GOAL"

    return "BLOCKED", "UNKNOWN_CAPABILITY"


def compute_call_intent(snap, requested_capability):
    per_capability = {}
    needed = []

    if requested_capability and requested_capability != "NONE":
        needed = [requested_capability]

    for cap_id in CAPABILITIES:
        status, reason = _capability_input_status(snap, cap_id)
        per_capability[cap_id] = {
            "status": status,
            "reachable_if_requested": status != "BLOCKED",
            "block_reason": reason if status == "BLOCKED" else None,
            "known_limitation": "此判定不代表主 Chatflow 的既有线性锁(v1_state.UPSTREAM_OF)会放行；"
            "M1 候选环境不经过该锁，锁的解除暂定为 M4 施工范围。"
            if cap_id in ("CAMPAIGN", "CONTENT_BRIEF")
            else None,
        }

    for cap_id in NO_ENTRY_CAPABILITIES:
        per_capability[cap_id] = {
            "status": "BLOCKED",
            "reachable_if_requested": False,
            "block_reason": "NO_PHYSICAL_ENTRY_YET",
            "known_limitation": None,
        }

    open_now = [t for t in snap["open_threads"] if t.get("status") == "OPEN"]

    # 共享合同一 §五「只追问真正阻塞当前任务的一项，其余作为缺口继续运行」的机制化落地。
    # 阻塞集合只在"本轮请求了某项能力、且该能力当轮判定为 BLOCKED"时才非空；否则为空集，
    # 全部缺口都是非阻塞缺口——这与"没有任何一项在阻塞"是同一件事，不需要额外分支。
    blocking_field_refs = set()
    requested_info = per_capability.get(requested_capability) if requested_capability else None
    if requested_info and requested_info["status"] == "BLOCKED":
        blocking_field_refs = set(BLOCK_REASON_BLOCKING_FIELD_REFS.get(requested_info["block_reason"], []))

    # gaps 正常由 main() 在合并后、调用本函数前重算写入；若调用方喂来的快照没有该键，
    # 这里自行重算而不是退化成空列表——空列表会被读成"查过了，没有缺口"，那是不实主张。
    # fallback 用 include_structural=False，与 main() 实际持久化的口径一致：
    # non_blocking_gaps 是调用路由信号，不是审计副本，9 条恒定常量不必塞进每轮 call_intent。
    gaps = snap["gaps"] if isinstance(snap.get("gaps"), list) else _compute_gaps(snap, include_structural=False)
    # 只放 field_ref 字符串，完整对象留在 snapshot.gaps，避免 call_intent 膨胀。
    non_blocking_gaps = [g["field_ref"] for g in gaps if g["field_ref"] not in blocking_field_refs]

    return {
        "needed_capabilities": needed,
        "per_capability": per_capability,
        "continuation": {
            "open_threads_to_surface": [t["id"] for t in open_now[:1]],
            "non_blocking_gaps": non_blocking_gaps,
        },
    }


def _dialogue_directive(snap, patch_ok, reject_reason, call_intent, requested_capability,
                        current_route_intent=None, changed=False):
    """给对话 LLM 的确定性指令，不让模型自己判断状态或编造原因（继承 A-4 纪律）。

    current_route_intent：**本轮 patch 里的原始 route_intent**，不是 snap["last_route_intent"]。
    后者是跨轮持久化的"最后一次"，只读它会让一次取消表达在之后每一轮都被误判成"还在撤销中"。
    patch 未通过时调用方传 None（那种轮次本来就没有可信的本轮意图）。

    changed：本轮 _merge_patch 是否真的改动了快照其他部分。用来防止 CANCEL 分支说出"没有任何
    内容被撤销或删除"这句话——如果用户在同一轮里既说了"算了取消"又给出了新内容（比如"算了，
    改成做家居内容"），新内容会正常覆盖旧值，"没有任何内容被撤销或删除"在这种轮次就是假话
    （对抗式审查真实发现的问题）。changed=True 时跳过这句断言，只让其余分支如实描述当前状态。
    """
    if not patch_ok:
        if reject_reason == SHADOW_NODE_FAILED:
            # **与"补丁校验未通过"是两种性质不同的失败，措辞不得混用。** 这一轮压根没有产出
            # 一份完整候选 patch（影子节点走了 default-value 降级路径），不是格式校验没过，
            # 更不是落库失败。不提内部代码（CE-A2 纪律），不编造网络/系统故障之类的具体原因。
            return (
                "这一轮系统内部的处理没有正常完成——不是用户表达得不清楚，也不是任务保存失败，"
                "就是这一步系统这边没跑通。如实把这件事告诉用户，请他把刚才想说的内容再说一遍。"
                "保持旧任务状态不变，不要推测具体是什么故障，也不要声称任何确认、授权或执行已经生效。"
            )
        return (
            "补丁校验未通过（" + reject_reason + "）。保持旧任务状态不变，正常回答用户，"
            "不要声称任何确认、授权或执行已经生效。"
        )

    parts = []

    # 用户本轮表达了撤回/取消。**本批只做诚实反馈，不实现撤销状态机**：按字段撤销需要什么样的
    # 状态机是设计判断，与 account_stage/open_threads 的"按字段确认状态机"同一类，不在本批
    # 擅自新建。此前 route_intent 写进 last_route_intent 后从未被任何分支读过，用户说"算了、
    # 取消"时系统一声不吭继续走别的逻辑——那是靠沉默造成的不实。
    #
    # 只在本轮**没有其他状态变化**时才说"没有任何内容被撤销或删除"——用户完全可能在同一句话
    # 里既说取消又给出新内容（"算了，改成做家居内容"），这种情况下旧值确实被新值覆盖了，
    # 断言"什么都没变"就是假话（对抗式审查真实发现的问题，不是假设）。changed=True 时只让
    # 其余分支如实描述当前状态（比如下面会附加"当前任务：改成做家居内容"），不再重复这句话。
    # 追问措辞也刻意不要求用户"说清楚具体想撤回哪一项"——系统本来就接不住任何具体答案，
    # 追问一个自己无法处理的答案本身就是一种隐含的虚假承诺；改为如实说明限制、正常继续对话。
    if current_route_intent == "CANCEL" and not changed:
        parts.append(
            "用户这一轮表达了要取消或撤回。当前系统这边并没有把撤回绑定到任何具体动作上，"
            "所以实际上没有任何内容被撤销或删除。如实告诉用户这一点，不要说已经撤销了什么，"
            "也不要说正在处理撤销；不必追问具体想撤销哪一项（当前环境接不住这类追问的答案），"
            "直接请用户按自己的想法继续说明接下来要做什么即可。"
        )

    if snap["current_task"]["text"]:
        parts.append("当前任务：" + snap["current_task"]["text"])
    else:
        parts.append("当前系统这边确实还没有记录任何任务内容（不是用户表达得不够清楚，"
                      "也不是落库失败，就是还没有形成任务）。")

    if requested_capability and requested_capability != "NONE":
        info = call_intent["per_capability"].get(requested_capability)
        if info:
            label = CAPABILITY_LABEL_ZH.get(requested_capability, requested_capability)
            if info["status"] == "BLOCKED":
                reason_label = BLOCK_REASON_LABEL_ZH.get(info["block_reason"], str(info["block_reason"]))
                parts.append(
                    "当前识别到你想调用的能力是" + label + "，判定为阻塞，原因是：" + reason_label
                    + "。如实告知，不编造网络或系统故障之类的原因。"
                )
            else:
                parts.append(
                    "当前识别到你想调用的能力是" + label + "，业务语义上可以直接进入，"
                    "但本候选环境是独立评估，不代表主 Chatflow 会立即放行——如实说明这是"
                    "M1 候选环境下的意图判定，不代表已经执行。"
                )

    open_now = [t for t in snap["open_threads"] if t.get("status") == "OPEN"]
    if open_now:
        parts.append("有一件之前提到、还没细聊的事：" + open_now[0]["text"])
        open_now[0]["status"] = "SURFACED"

    return "\n".join(parts)


# ---- Content Task 投影：快照 → Content Brief 下游精简视图 ----
# 设计参照：V1_M1_TASK_CONTEXT_COMPILER_DESIGN_v0.1.md §三。
#
# v0.2 起 account_stage / expression_discretion / available_capacity 已由快照扩展承载；
# v0.3 起 evidence_and_gaps 也不再是哨兵——真实拼装 evidence_bundle[] + gaps[]，保留来源与
# 确认状态、不摊平（设计文档 §三 原文）。
#
# 剩下的结构缺口收窄成一条 evidence_and_gaps.relevance_filter：设计文档 §三 要求取"与本条
# 相关的子集"，而 P0 快照没有"本条内容"的标识符（无 item_id），任何过滤都会是编造出来的
# 相关性判断。因此如实全量透传，并把"相关性过滤未实现"登记进 projection_gaps。
CONTENT_TASK_P0_STRUCTURAL_GAPS = [
    "evidence_and_gaps.relevance_filter",
]

# 这四项设计文档明确规定"M1 不做专业判断"，只能由调用方（Campaign 决策包／未来 M3）在
# 投影时补入；M1 自身产出会越界进入 CAP-02/CAP-04 的专业判断范围。
CONTENT_TASK_CALLER_SUPPLIED_KEYS = [
    "audience_problem_scene",
    "audience_shift",
    "content_promise",
    "post_publish_observation",
]


def project_content_task(snapshot, source_override=None, caller_supplied=None):
    """任务上下文快照 → Content Task 投影，只在把工作交给 Content Brief 时调用。

    caller_supplied：可选 dict，键限于 CONTENT_TASK_CALLER_SUPPLIED_KEYS，用于承接
    Campaign 决策包或未来 M3 补入的专业判断内容；未提供的键如实留空并计入
    projection_gaps，不由本函数代为判断或编造。
    """
    caller_supplied = caller_supplied or {}
    unknown_keys = set(caller_supplied.keys()) - set(CONTENT_TASK_CALLER_SUPPLIED_KEYS)
    if unknown_keys:
        raise ValueError("CALLER_SUPPLIED_UNKNOWN_KEYS:" + ",".join(sorted(unknown_keys)))

    current_task = snapshot.get("current_task") or {}
    goal = snapshot.get("goal_structure") or {}
    temporal_scope = current_task.get("temporal_scope", "UNSTATED")

    # 温度范围非 CYCLE 时明确 NOT_APPLICABLE；等于 CYCLE 时 P0 快照也没有专门的
    # cycle_role 字段可取，同样如实标记为结构性缺口，不得从 temporal_scope 本身编造。
    if temporal_scope == "CYCLE":
        cycle_role = "NOT_CAPTURED_IN_P0_SNAPSHOT"
    else:
        cycle_role = "NOT_APPLICABLE"

    missing_caller_keys = [k for k in CONTENT_TASK_CALLER_SUPPLIED_KEYS if not caller_supplied.get(k)]

    return {
        "source": source_override or current_task.get("source_ref") or "USER_DIRECT",
        "cycle_role": cycle_role,
        "primary_goal": goal.get("primary_goal"),
        "secondary_goals": list(goal.get("secondary_goals") or []),
        "priority_order": list(goal.get("priority_order") or []),
        "non_sacrifice_constraints": list(goal.get("non_sacrifice_constraints") or []),
        "audience_problem_scene": caller_supplied.get("audience_problem_scene"),
        "audience_shift": caller_supplied.get("audience_shift"),
        "content_promise": caller_supplied.get("content_promise"),
        "account_stage": (snapshot.get("account_stage") or {}).get("text"),
        "expression_discretion": dict(
            snapshot.get("expression_discretion")
            or {"plot_allowed": "UNSTATED", "remix_allowed": "UNSTATED", "conflict_allowed": "UNSTATED", "controversy_allowed": "UNSTATED"}
        ),
        # 各维度整条保留，不摊平；gaps **自行重算而不是读 snapshot["gaps"] 的存量值**——
        # 投影可能被喂一份手工构造的、或早于 v0.3 持久化的快照，此时存量值是 [] 或缺失，
        # 直接透传就会输出 "gaps": []，下游只能读成"查过了，没有缺口"。_compute_gaps 是纯
        # 函数、幂等、无副作用，重算成本可忽略。
        # **必须 include_structural=True**：这里正是设计文档 §三 要求"完整、不摊平"的落地点，
        # 也是两条 DEFER 数组（market_observations / runtime_evidence）"空数组必须配一条 gaps
        # 登记"这条诚实口径真正被下游看到的地方；持久化路径只留动态子集，不影响本视图。
        "evidence_and_gaps": {
            "evidence": [dict(item) for item in (snapshot.get("evidence_bundle") or [])],
            "gaps": _compute_gaps(snapshot, include_structural=True),
        },
        "platform_and_form": "PLATFORM_UNCONFIRMED",
        "available_capacity": (snapshot.get("capacity_triad") or {}).get("cycle_available"),
        "post_publish_observation": caller_supplied.get("post_publish_observation"),
        "projection_gaps": list(CONTENT_TASK_P0_STRUCTURAL_GAPS) + missing_caller_keys,
    }


def main(user_query: str, snapshot_json: str, shadow_patch: dict) -> dict:
    try:
        snap = json.loads(snapshot_json) if snapshot_json else _default_snapshot()
    except Exception:
        snap = _default_snapshot()
    if not isinstance(snap, dict) or "schema_version" not in snap:
        snap = _default_snapshot()

    # 向前兼容：更早持久化的快照没有 v0.2 扩展的 account_stage/expression_discretion/
    # capacity_triad，也没有 v0.3 扩展的 evidence_bundle/market_observations/gaps/
    # runtime_evidence。只补齐缺失的顶层键，不整体重置——已有数据（如 current_task/
    # goal_structure）必须原样保留，否则等于悄悄丢弃旧会话的真实状态。本循环遍历
    # _default_snapshot() 的全部顶层键，新增字段自动被覆盖，无需为每批扩展另写升级代码。
    for _key, _default_val in _default_snapshot().items():
        if _key not in snap:
            snap[_key] = _default_val

    # 条目级向前兼容：v0.4 给 evidence_bundle[] 每条追加了 permission/freshness 两个维度，
    # 但上面的循环只补顶层键，不会去补"已经存在的顶层数组"里每个既有条目缺的新字段。旧会话
    # （v0.3 及更早）持久化的条目只有 8 个键，缺这两维；如果不补，project_content_task 会把
    # 一份异构数组原样透传给下游，而设计文档已经写死"每条必须携带全部维度"——对这些旧条目
    # 那句话会是假的，下游按新 schema 读 item["permission"] 还会直接 KeyError。这里只补
    # 缺失的键、不覆盖已有值，且补的值和 _merge_evidence_item 对新条目写入的值完全一致
    # （旧条目同样只可能来自用户直接陈述，补真实值不是编造）。
    for _item in snap.get("evidence_bundle") or []:
        _item.setdefault("permission", "OWNED_BY_USER")
        _item.setdefault("freshness", "FRESH")

    # Dify 把 LLM 节点的 structured_output 作为原生 object 传给下游 Code 节点
    # （非 JSON 字符串），故这里直接按 dict 校验，不做 json.loads。
    patch = shadow_patch if isinstance(shadow_patch, dict) else None

    if patch is None:
        patch_ok = False
        reject_reason = "PATCH_NOT_OBJECT"
    elif set(PATCH_KEYS) - set(patch.keys()):
        # 缺任意一个必需 key（含 {} 这种全缺的降级输出）= 这一轮压根没有一份完整候选 patch，
        # 不是"格式校验没通过"，所以**不再往下调用 _validate_patch**，理由见 SHADOW_NODE_FAILED。
        patch_ok = False
        reject_reason = SHADOW_NODE_FAILED
    else:
        patch_ok, reject_reason = _validate_patch(patch)

    # 本轮原始 route_intent，只在 patch 真的可信时才取（见 _dialogue_directive 的形参说明：
    # 不能读 snap["last_route_intent"]，那是跨轮的"最后一次"）。
    current_route_intent = patch.get("route_intent") if patch_ok and isinstance(patch, dict) else None

    requested_capability = "NONE"
    if patch_ok:
        snap, changed, evidence_dropped_incomplete = _merge_patch(snap, patch)
        requested_capability = patch.get("requested_capability", "NONE")
    else:
        changed = False
        evidence_dropped_incomplete = False

    # gaps[] 每轮整体重算并覆写。**无条件执行**（不放在 if patch_ok 分支内）：patch 被拒绝的
    # 轮次同样重算，结果与上一轮相同，因为快照没变。这次覆写**不置 changed、不推进 revision**
    # ——缺口清单是既有状态的派生视图，不是用户造成的状态变化。
    # include_structural=False：只持久化随对话状态变化的动态子集（空快照上 13 条）。9 条结构性
    # 常量内容恒定、不携带任何本轮独有信息，逐轮写进 Dify 会话变量只会让快照白白膨胀；需要完整
    # 22 条合规视图的调用点（project_content_task）自行以 include_structural=True 重算。
    snap["gaps"] = _compute_gaps(snap, include_structural=False)

    call_intent = compute_call_intent(snap, requested_capability)
    directive = _dialogue_directive(
        snap, patch_ok, reject_reason, call_intent, requested_capability, current_route_intent, changed
    )

    return {
        "snapshot_json": json.dumps(snap, ensure_ascii=False),
        "call_intent_json": json.dumps(call_intent, ensure_ascii=False),
        "dialogue_directive": directive,
        "patch_ok": "true" if patch_ok else "false",
        "reject_reason": reject_reason,
        "state_changed": "true" if changed else "false",
        "turn_report_json": json.dumps(
            {
                "patch_ok": patch_ok,
                "reject_reason": reject_reason,
                "revision": snap["revision"],
                "requested_capability": requested_capability,
                "needed_capabilities": call_intent["needed_capabilities"],
                "open_threads_open_count": len(
                    [t for t in snap["open_threads"] if t.get("status") in ("OPEN", "SURFACED")]
                ),
                # 本轮有一条证据因维度不全（给了原话、没给性质）被丢弃。如实登记在**不面向
                # 用户**的机器可读通道里：dialogue_directive 不变、reject_reason 不变，
                # 不给"内部枚举被对话 LLM 复述给用户"（CE-A2）这个已知缺陷新增触发器。
                "evidence_dropped_incomplete": evidence_dropped_incomplete,
            },
            ensure_ascii=False,
        ),
    }
