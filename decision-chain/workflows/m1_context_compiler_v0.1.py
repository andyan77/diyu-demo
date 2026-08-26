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

# **v1.4.1 Rebase 修复 M1-B-24**：requested_capabilities_text 的合法性校验此前只认
# CAPABILITIES 六项——用户直接点名 ENTRY-04（创意锦标赛）或 CAP-03（单账号持续运营）时，
# 影子模型如实输出 "CREATIVE_TOURNAMENT"/"SINGLE_ACCOUNT_OPERATION"，却被 `_validate_patch`
# 当成非法枚举整体拒绝——这两项业务上合法可路由，只是物理 Runtime 未接线（NO_ENTRY_
# CAPABILITIES 的定义本身就是"合法但当前无入口"，`compute_call_intent` 也早已为它们产出
# 正确的 BLOCKED/NO_PHYSICAL_ENTRY_YET 状态），"没有物理入口"不等于"不该出现在合法枚举里"
# ——这正是 Delta v1.4.1 §5.2 逐字要求的"业务上合法可路由与物理 Runtime 是否已接通分开表达；
# CAP-05 不得因 M4 尚未接线而从 M1 意图空间删除"。校验改为对照这个合并后的全集。
ALL_CAPABILITY_CODES = CAPABILITIES + NO_ENTRY_CAPABILITIES


def _parse_capabilities_text(raw):
    """把 requested_capabilities_text 这个逗号分隔的扁平字符串解析成去重、保序的列表。

    **B-4 修复**：此前 requested_capability 是单值枚举，一轮只能点名一个能力，`needed`
    结构性地不可能超过一个元素，不符合"按真实依赖选择零个、一个或多个能力"（P0 observable_
    changes 原文）。修复不引入 JSON 数组类型的 patch 字段——那会跳出本文件目前唯一验证过的
    "扁平字符串/枚举"结构（DeepSeek V4 Flash 不支持嵌套对象的既有观察，见 PATCH_KEYS 注释），
    在缺少 live 实测的情况下引入一个全新的未验证结构本身就是风险。改为让模型在同一个扁平
    字符串字段里用英文逗号列出多个能力代码（"CAMPAIGN,CONTENT_BRIEF"），由确定性代码解析，
    不新增未验证的 schema 结构。合法性由调用方对每个元素单独校验（不在本函数里做，本函数
    只负责去重、保序、丢弃空白项）。

    **对抗式审查发现的真实回归，已修复**：旧的单值字段有 `"NONE"` 这个官方哨兵值表示
    "这一轮没点名"；本字段改用空字符串表示同样的意思（system prompt 已改口径），但模型
    仍可能沿用同一份 schema 里其它字段（如 confirmation_signal）的 `"NONE"` 习惯，写出
    `"NONE"` 或 `"MATRIX,NONE"`。修复前 `"NONE"` 不在 CAPABILITIES 里，会被
    `_validate_patch` 判成非法枚举、**整轮拒绝**——一个语义上完全合理、只是格式沿用旧习惯
    的输出，被罚以最重的整任务拒绝，直接违反"资料不足时不得整任务拒绝"。这里把 `"NONE"`
    当无操作词元过滤掉，不进入后续合法性校验，其余真正无法识别的代码仍然会在
    `_validate_patch` 里触发整体拒绝（不改变既有"非法枚举整体拒绝"纪律，只是补一个
    历史遗留的合法哨兵词）。
    """
    if not isinstance(raw, str):
        return []
    items = []
    for part in raw.split(","):
        item = part.strip()
        if not item or item == "NONE":
            continue
        if item not in items:
            items.append(item)
    return items

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

# B-5 修复（实际撤销机制）：只覆盖三个纯追加、此前完全没有移除路径的集合。
# 不含 priority_order（替换语义，"撤销"语义不明确，需要历史栈才能真正回退，属于需要
# 额外设计判断的范畴，本批不做）、不含 requested_capabilities_text（本身就是逐轮瞬时
# 信号，不持久化，天然不需要撤销）、不含 primary_goal/current_task（单值替换字段，
# 撤销等价于"回到上一个值"，同样需要历史栈，同一类范围裁定）。
VALID_CANCEL_TARGET = ["NONE", "SECONDARY_GOAL", "NON_SACRIFICE_CONSTRAINT", "BUSINESS_GOAL_CATEGORY"]
CANCEL_TARGET_LABEL_ZH = {
    "SECONDARY_GOAL": "次要目标",
    "NON_SACRIFICE_CONSTRAINT": "不可让步条件",
    "BUSINESS_GOAL_CATEGORY": "经营目标类别",
}

# 对抗式审查发现的真实泄漏：business_goal_categories[] 存的是内部枚举代码（如
# "STORE_VISIT"），撤销机制把 target_list.pop() 的原始返回值直接拼进 dialogue_directive
# 就会把这个代码原样递给对话 LLM——与 CAPABILITY_LABEL_ZH/BLOCK_REASON_LABEL_ZH 同一类
# CE-A2 缺陷。取值与 SHADOW_SYSTEM_PROMPT 里 business_goal_category 字段口径的中文说明
# 逐一对应，不新造一套措辞。
BUSINESS_GOAL_CATEGORY_LABEL_ZH = {
    "LONG_TERM_VALUE": "长期价值",
    "ACCOUNT_GROWTH": "起号",
    "FOLLOWER_GROWTH": "吸粉",
    "TRAFFIC": "流量",
    "GMV": "成交额",
    "LEADS": "线索",
    "STORE_VISIT": "到店",
}

VALID_TEMPORAL_SCOPE = ["UNSTATED", "ONE_ITEM", "CYCLE", "LONG_TERM"]
VALID_CONFIRMATION_SIGNAL = ["NONE", "AFFIRM", "DECLINE"]
VALID_ROUTE_INTENT = ["DISCUSS", "FOCUS", "EXECUTE_REQUEST", "CANCEL", "OUT_OF_SCOPE"]
VALID_DISCRETION = ["UNSTATED", "ALLOWED", "NOT_ALLOWED"]
DISCRETION_KEYS = ["plot_allowed", "remix_allowed", "conflict_allowed", "controversy_allowed"]

# ---- M1-AC-18（CTA 三层权限上下文，Delta v1.4.1 §5.4）----
# M1 只编译 CTA 目标/风险层级/事实/承接路径/授权，不写最终 CTA 文案本身。三层对应
# §5.4 逐字的三类风险：关注/评论/收藏等低风险平台互动｜商品点击/咨询/线索/到店/购买等
# 一般经营转化｜站外导流/价格优惠/强购买承诺等高风险动作。
VALID_CTA_RISK_TIER = ["UNSTATED", "LOW_RISK", "BUSINESS_CONVERSION", "HIGH_RISK"]
# 不建审批系统、不建第二套权限真源：授权只是本会话内、针对具体目标文本的一次性信号，
# 见 _merge_patch 里 authorized_high_risk_targets 的写入条件。
VALID_CTA_AUTHORIZATION_SIGNAL = ["NONE", "GRANT", "DECLINE"]
VALID_CTA_PREFERENCE_SIGNAL = ["NONE", "REQUEST_NO_CTA", "REQUEST_CTA"]

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
#   provenance   ── **B-3 修复后有真实代码读者**：写入取 patch 的 evidence_provenance
#                   （USER_DIRECT / SOURCED_MATERIAL），不再是恒定常量。VALID_HISTORICAL_
#                   ARTIFACT / AUTHORIZED_EXTERNAL / SYSTEM_DERIVED 仍不可达——本批只新增
#                   了"文件上传材料"这一个真实非对话输入通道，没有历史产物库、没有外部工具
#                   调用、没有系统推断证据生成器，如实只声明已建成的这一条。
#   confirmation ── **P0 无代码读者**，纯声明（写入恒为 SYSTEM_TENTATIVE）。
#   scope        ── **P0 无代码读者**（写入只取 patch 值或 UNSTATED；patch 侧的合法性由
#                   VALID_EVIDENCE_SCOPE 承担）。此处纯声明。
#   availability ── **P0 无代码读者**，纯声明。P0 恒为 AVAILABLE，其余四值不可达，
#                   已由 _compute_gaps 的结构性缺口条目如实登记。
#   permission   ── **P0 无代码读者**，纯声明，写入仍恒为 OWNED_BY_USER。**B-3 修复后这条
#                   注释的旧理由（"不存在第三方材料"）不再成立**——文件上传通道建成后，
#                   用户完全可能上传第三方材料；但本批没有引入"这份材料的使用权限是谁给的"
#                   这一问询机制，如实保持常量、不假装已经判断，登记为新的已知限制（见
#                   P0_STRUCTURAL_GAPS 对应条目），不是延续旧理由。
#   freshness    ── **B-3 修复后有真实代码读者**：不再恒为 FRESH。verbatim 陈述
#                   （provenance=USER_DIRECT）仍是 FRESH（刚说出口，天然新鲜）；上传材料
#                   （provenance=SOURCED_MATERIAL）改判 UNKNOWN——P0 拿不到文件的真实生成
#                   时间，声称"新鲜"是编造，声称"过期"同样是编造，UNKNOWN 才是诚实值。
#                   由确定性代码从 provenance 派生，不新增 LLM patch key（模型无法可靠判断
#                   一份文件内容的真实新旧）。
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

# B-3 修复：evidence_provenance 的 LLM patch 侧合法取值。**只开放词表五个真实取值里已经
# 建成物理通道的两个**：USER_DIRECT（对话原话）、SOURCED_MATERIAL（本轮上传材料，见
# m1_extract/m1_join 节点）。VALID_HISTORICAL_ARTIFACT/AUTHORIZED_EXTERNAL/SYSTEM_DERIVED
# 没有对应输入通道，开放给模型只会诱导它编造来源，故不在此列。
VALID_EVIDENCE_PROVENANCE_PATCH = ["USER_DIRECT", "SOURCED_MATERIAL"]

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
# v0.7 扩展第四批：B-3（合法资料输入通道）／B-4（多能力选择）。
#   requested_capability → requested_capabilities_text：**改名不改型**，仍是扁平字符串，
#     不引入数组/嵌套对象（见 _parse_capabilities_text 注释，B-4 修复）。
#   evidence_provenance：新增字段，B-3 修复后 provenance 维度首次有真实可变取值。
PATCH_KEYS = {
    "route_intent",
    "current_task_text",
    "temporal_scope",
    "primary_goal_text",
    "secondary_goal_text",
    "priority_order_text",
    "non_sacrifice_constraint_text",
    "business_goal_category",
    "requested_capabilities_text",
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
    "evidence_provenance",
    # B-5 修复第五批：短指代绑定（handled_thread_id）与实际撤销机制（cancel_target）。
    "handled_thread_id",
    "cancel_target",
    # v1.4.1 Rebase 新增批次：M1-AC-17 最小账号锚点（account_anchor_text）与
    # M1-AC-18 CTA 三层权限上下文（cta_* 六项）。同样只加扁平字符串/枚举。
    "account_anchor_text",
    "cta_target_text",
    "cta_risk_tier",
    "cta_conversion_goal_text",
    "cta_access_path_text",
    "cta_authorization_signal",
    "cta_preference_signal",
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
        # 最小账号锚点（M1-AC-17，Delta v1.4.1 §5.3）：普通咨询/单次创作不要求这个字段有值
        # （见 _compute_gaps 里按 temporal_scope 收窄的判断，不强行建档）；持续运营场景下
        # 从自然语言形成 SYSTEM_TENTATIVE 最小锚点即可，空白账号是合法事实。source=
        # CALLER_SUPPLIED 是留给未来 M2 最小投影消费路径的入口（见 main() 的
        # account_anchor_supplied 形参），P0 当前 Dify DSL 没有任何调用方会传这个参数，
        # 行为等价于本字段一直是 NONE/USER_DIRECT 二选一。M1 不因此建账号库、不直写 M2。
        "account_anchor": {"identity_text": None, "source": "NONE", "confirmation": "SYSTEM_TENTATIVE"},
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
        # CTA 三层权限上下文（M1-AC-18，Delta v1.4.1 §5.4）：M1 只编译目标/风险层级/经营
        # 目标事实/承接路径/授权，不写最终 CTA 文案。authorized_high_risk_targets 纯追加，
        # 只有"本轮同时点名具体目标 + 当前层级是 HIGH_RISK + 用户本轮显式 GRANT 信号"三者
        # 同时成立才会写入（见 _merge_patch）——流量/吸粉/GMV/线索/到店目标本身不经过这条
        # 写入路径，不会自动变成授权，这是"目标不自动授权高风险 CTA"的结构性保证，不是
        # 靠对话文本口头劝阻。不建立独立的第二套权限真源，也不建审批系统。
        "cta_context": {
            "risk_tier": "UNSTATED",
            "target_text": None,
            "conversion_goal_text": None,
            "access_path_text": None,
            "authorized_high_risk_targets": [],
            "no_cta_requested": False,
        },
        # 可用事实/偏好/参考及其全部维度（设计文档 §二 #9 + 维度表）。纯追加，永不修改既有条目：
        # 冻结硬约束「参考资料和历史产物不得覆盖用户已经确认的事实」在 P0 因此天然不可违反。
        "evidence_bundle": [],
        # 市场观察（设计文档 §二 #10）：本批 **DEFER，未实现**。
        # **B-3 修复后更正**：DSL 已有 Tool 无关的 file_upload 通道（不再是 enabled=False），
        # 但这条 DEFER 结论不受影响——file_upload 建成的是"用户主动提供一份自己的资料"这条
        # 通道，不是自动化的市场情报采集；market_observations 语义上要求的是运行期主动
        # 联网/调用工具获取的外部市场数据，本环境仍然没有 Tool 节点、没有联网能力，仓库红线
        # 与共享合同一 §八也仍把全平台市场情报爬虫列为非目标，消费者 CAP-03/CAP-05 仍是
        # NO_ENTRY_CAPABILITIES；observed_at 由编译器补即伪造采集时间，validity 由代码评级
        # 即新增自动评分器。
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
    rc_text = patch.get("requested_capabilities_text", "")
    if not isinstance(rc_text, str):
        return False, "ILLEGAL_TYPE:requested_capabilities_text:NOT_STRING"
    for item in _parse_capabilities_text(rc_text):
        if item not in ALL_CAPABILITY_CODES:
            return False, "ILLEGAL_ENUM:requested_capabilities_text:" + item
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
    # B-3：evidence_provenance 校验，缺省 USER_DIRECT（没有材料被采纳的一轮，来源就是对话本身）。
    ep = patch.get("evidence_provenance", "USER_DIRECT")
    if ep not in VALID_EVIDENCE_PROVENANCE_PATCH:
        return False, "ILLEGAL_ENUM:evidence_provenance:" + str(ep)
    # v0.4：同样只追加一条枚举校验，整体拒绝语义不变（secondary_goal_text /
    # priority_order_text 是自由文本，没有枚举空间可校验）。
    bgc = patch.get("business_goal_category", "UNSTATED")
    if bgc not in VALID_BUSINESS_GOAL_CATEGORY:
        return False, "ILLEGAL_ENUM:business_goal_category:" + str(bgc)
    # B-5：handled_thread_id 是自由文本（模型原样复制一个 open_threads[].id 或留空），
    # 没有枚举空间可校验，只校验类型；真正存在性校验在 _merge_patch 里做（那里才有
    # snap["open_threads"] 的实际内容，找不到匹配就静默忽略，不是校验失败）。
    hti = patch.get("handled_thread_id", "")
    if not isinstance(hti, str):
        return False, "ILLEGAL_TYPE:handled_thread_id:NOT_STRING"
    ct = patch.get("cancel_target", "NONE")
    if ct not in VALID_CANCEL_TARGET:
        return False, "ILLEGAL_ENUM:cancel_target:" + str(ct)
    # v1.4.1 Rebase：CTA 三层权限上下文三个枚举字段，同一整体拒绝语义。account_anchor_text/
    # cta_target_text/cta_conversion_goal_text/cta_access_path_text 是自由文本，无枚举可校验。
    crt = patch.get("cta_risk_tier", "UNSTATED")
    if crt not in VALID_CTA_RISK_TIER:
        return False, "ILLEGAL_ENUM:cta_risk_tier:" + str(crt)
    cas = patch.get("cta_authorization_signal", "NONE")
    if cas not in VALID_CTA_AUTHORIZATION_SIGNAL:
        return False, "ILLEGAL_ENUM:cta_authorization_signal:" + str(cas)
    cps = patch.get("cta_preference_signal", "NONE")
    if cps not in VALID_CTA_PREFERENCE_SIGNAL:
        return False, "ILLEGAL_ENUM:cta_preference_signal:" + str(cps)
    return True, ""


def _merge_evidence_item(snap, patch, material_present):
    """把本轮 patch 的单条粗粒度证据信号写入 evidence_bundle[]，返回
    (appended: bool, dropped_incomplete: bool, provenance_downgraded: bool)。

    material_present：本轮 m1_join 抽取出的材料文本是否非空（由 main() 传入，来自
    m1_extract/m1_join 节点链路，不是 patch 的一部分）。**对抗式审查发现的真实缺口，
    已修复**：此前 evidence_provenance 完全由模型自称，m1_compiler 节点根本没有接入
    m1_join 的输出，模型说 SOURCED_MATERIAL 就是 SOURCED_MATERIAL，没有任何代码核实
    ——这正是 B-3 修复之前就在批判的"伪造来源"，只是把伪造的主体从代码换成了模型。
    现在如果模型声称 SOURCED_MATERIAL 但本轮客观上没有材料文本，代码把它降级回
    USER_DIRECT（更保守的默认，而不是维持一条无法核实的第三方来源断言），并把这次
    降级如实记录进 turn_report_json（机器可读通道，不进 dialogue_directive）。

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

    七个维度的默认值（B-3 修复后 P0 有 nature / scope / provenance / freshness 四维可以
    偏离，confirmation / availability / permission 三维仍不可偏离——偏离仍需要新的物理
    通道：工具调用／按字段确认交互／生命周期时钟／材料权属问询，属后续批次或 M4/M5 范围）：
      nature       ← LLM 给出（唯一只有模型能读出的维度：代码分不清"我们店在杭州"是事实、
                     "我不喜欢强 CTA"是偏好），代码不得代填默认值
      provenance   ← 取 patch 的 evidence_provenance，缺省 USER_DIRECT。**B-3 新增的真实
                     可变维度**：本轮证据若来自 m1_extract/m1_join 抽取的上传材料内容，模型
                     应给 SOURCED_MATERIAL；来自对话原话仍是 USER_DIRECT。
      confirmation ← 恒为 SYSTEM_TENTATIVE（见上）
      scope        ← 取 patch 值，缺省 UNSTATED；**绝不从 current_task.temporal_scope 推导**
      availability ← 恒为 AVAILABLE（本数组只承载"已经拿到的信息"；UNKNOWN/NOT_PROVIDED/
                     DECLINED/STALE 属于"没拿到"，归 gaps[]；STALE/EXPIRED 还需要生命周期
                     时钟，P0 没有，已由 _compute_gaps 结构性条目如实登记）
      permission   ← 恒为 OWNED_BY_USER（Execution Prompt v1.2 §4.3 逐字要求的权限维度）。
                     B-3 修复后本环境已有材料上传通道，第三方材料在物理上可能出现，但本批
                     没有引入"这份材料的使用权限归属"问询机制，如实保持常量、不假装已判断，
                     **不接受入参覆盖，也不新增 LLM 字段**——加一个模型字段只会制造"这一维
                     在被判断"的假象，登记为已知限制（见 P0_STRUCTURAL_GAPS）。
      freshness    ← 由 provenance 派生（确定性代码，非 LLM 字段）：USER_DIRECT → FRESH
                     （刚说出口，天然新鲜）；SOURCED_MATERIAL → UNKNOWN（P0 拿不到文件的
                     真实生成时间，声称新鲜或过期都是编造）。承接 Prompt §4.3 的时效维度
                     与共享合同一 §三"作用域与有效期"后半句"生效时间是否仍有效"。
    """
    text = (patch.get("evidence_text") or "").strip()
    if not text:
        return False, False, False

    nature = patch.get("evidence_nature", "UNSTATED")
    if nature not in VALID_EVIDENCE_NATURE_PATCH:
        # 正常路径下 _validate_patch 已整体拒绝；这里是 helper 被直接调用时的取值门禁，
        # 防止绕过校验写进一个词表外的（或 SYSTEM_INFERENCE 这种模型不得自称的）性质。
        raise ValueError("ILLEGAL_EVIDENCE_NATURE:" + str(nature))

    # provenance 的取值门禁与 nature 放在同一处、同一时机（对抗式审查发现的真实不一致：
    # 此前这条检查放在下面的去重判断之后，导致"重复 text + 非法 provenance"的手工调用会
    # 静默走去重分支返回 (False, False, False)，而不是像 nature 那样直接抛错——两条门禁
    # 语义相同，必须在去重判断生效之前统一处理，不能因为写入顺序不同而表现不同）。
    provenance = patch.get("evidence_provenance", "USER_DIRECT")
    if provenance not in VALID_EVIDENCE_PROVENANCE_PATCH:
        raise ValueError("ILLEGAL_EVIDENCE_PROVENANCE:" + str(provenance))

    if nature == "UNSTATED":
        # 维度不全（模型给了原话却没给性质）：**只跳过这一条证据**，本轮其余捕获（任务、
        # 目标、产能、裁量……）照常合并，reject_reason 保持不变，dialogue_directive 不变。
        # 不整体拒绝的四条理由见 _validate_patch 注释与设计说明；代码无法诚实推导一条信息
        # 是事实还是偏好，所以宁可不写，也不补一个默认 nature。这一轮的丢弃由
        # turn_report_json.evidence_dropped_incomplete 如实登记在不面向用户的通道里。
        return False, True, False

    # 与 _compute_gaps / compute_call_intent 的 `.get(...) or []` / isinstance 防御同一风格：
    # helper 可能被直接喂一份手工构造的、或早于 v0.3 持久化的快照（没有这个顶层键）。
    snap.setdefault("evidence_bundle", [])

    for item in snap["evidence_bundle"]:
        # 去重沿用 non_sacrifice_constraints 的 `not in` 先例：同 text 已存在则不追加、
        # 不 bump revision，也不修改既有条目。
        if item.get("text") == text:
            return False, False, False

    # B-3 的核实修复：SOURCED_MATERIAL 是模型对"这条信息来自本轮上传材料"的自我声明，
    # 不是代码独立核实的事实。唯一能核实的信号是 material_present（本轮 m1_join 是否真的
    # 抽出了非空文本）——声称来自材料但本轮客观没有材料，代码不予采信，降级为 USER_DIRECT。
    downgraded = False
    if provenance == "SOURCED_MATERIAL" and not material_present:
        provenance = "USER_DIRECT"
        downgraded = True
    freshness = "FRESH" if provenance == "USER_DIRECT" else "UNKNOWN"

    snap["evidence_bundle"].append(
        {
            "id": "ev_%03d" % (len(snap["evidence_bundle"]) + 1),
            "text": text,
            "nature": nature,
            "provenance": provenance,
            "confirmation": "SYSTEM_TENTATIVE",
            "scope": patch.get("evidence_scope", "UNSTATED"),
            "availability": "AVAILABLE",
            "permission": "OWNED_BY_USER",
            "freshness": freshness,
            # 取增量前的 revision，与 open_threads.raised_at_revision 同一时序先例。
            # 只有这一个整数，没有变更历史、没有事件流、没有回放——不是事件溯源。
            "captured_at_revision": snap["revision"],
        }
    )
    return True, False, downgraded


def _merge_patch(snap, patch, material_present=False):
    """把校验通过的 patch 合并进快照。只有用户本轮真的说出口的内容才写入
    （不得把 §四 冻结的"不得把用户没说的目标写成已确认"违反）。

    material_present：本轮 m1_join 是否真的抽出了非空材料文本，透传给
    _merge_evidence_item 核实 evidence_provenance=SOURCED_MATERIAL 的声明（B-3 修复）。

    返回 (snap, changed, evidence_dropped_incomplete, evidence_provenance_downgraded,
    cancel_effect, content_changed)。除 changed 外均只用于机器可读通道或
    _dialogue_directive 组织如实反馈，不影响 patch_ok。cancel_effect 见下方 B-5 撤销
    机制注释，None 表示本轮不涉及。content_changed 见函数末尾注释——与 changed 的唯一
    差异是排除了"仅仅是线程被标记 HANDLED"这一种情况。
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

    # **对抗式审查发现的两个真实缺口，已修复，均通过把下面两块提到本轮任何"追加新内容"
    # 之前来解决**：
    #
    # 缺口一（数据丢失）：如果这两块放在 secondary_goal/non_sacrifice_constraint/
    # business_goal_category 的追加逻辑**之后**（此前的顺序），用户在同一句话里"撤销 A、
    # 同时说出 B"（比如"算了，不要涨粉了，改成兼顾口碑"）会先把 B 追加进列表，再撤销逻辑
    # 弹出列表最后一项——弹出的是刚追加的 B，不是本该撤销的 A，直接吞掉用户这一轮真正说
    # 出口的新内容，且对话反馈还会把这个错误当成"成功撤销"讲给用户听。
    #
    # 缺口二（状态被污染）：handled_thread_id 如果放在 side_question 追加**之后**，模型
    # 引用一个本轮才由 side_question 新建的 id（这个 id 在模型看到的快照里根本不存在，
    # 纯属幻觉）会被当成合法匹配，把用户刚提出的新问题直接判定成"已处理"，不会被
    # 追问、不会被计入 open_threads_open_count——一个查无实据的 id 反而生效了，
    # 而不是被安全忽略。
    #
    # 把这两块移到这里（在任何本轮追加动作之前），它们看到的 open_threads/secondary_goals/
    # non_sacrifice_constraints/business_goal_categories 都严格是**本轮开始前**的状态，
    # 不可能撤销或匹配到本轮才刚写入的内容。

    # B-5 修复（短指代绑定）：模型能看到 snapshot_json 里 open_threads[] 的全部 id/text/
    # status（跟着 {{#conversation.snapshot_json#}} 一起进它的 prompt），当用户本轮的话
    # 是在回应/处理其中一条时，只需要原样复制这条已存在的 id 回来——不需要模型做模糊匹配，
    # 代码只负责校验这个 id 真的存在且状态还没到终态。找不到匹配（模型引用了不存在的、或
    # 已经是 HANDLED 的 id）时静默忽略：这是模型自己的判断信号，不是用户直接陈述的事实，
    # 宁可漏判，也不能凭一个查无实据的 id 编造一次状态转换。
    #
    # **对抗式审查发现的第三个真实缺口，已修复**：这里不直接把 `changed` 置 True，只记录
    # thread_handled_this_turn——纯粹的"线程标记已处理"不是用户本轮说出口的新内容，如果
    # 直接算进 changed，会让下面 CANCEL 分支的"没有绑定到具体动作"诚实反馈被错误跳过
    # （用户说"这件事不用管了"时，route_intent=CANCEL 与 handled_thread_id 很自然地同时
    # 出现，见 _dialogue_directive 里 content_changed 的计算与使用）。函数末尾会再把
    # thread_handled_this_turn 并入最终返回的 changed（该状态转换仍然是真实变化，仍然
    # 推进 revision），只是不计入"是否有值得对话 LLM 描述的新内容"这个更窄的判断。
    thread_handled_this_turn = False
    handled_id = (patch.get("handled_thread_id") or "").strip()
    if handled_id:
        for t in snap["open_threads"]:
            if t.get("id") == handled_id and t.get("status") in ("OPEN", "SURFACED"):
                t["status"] = "HANDLED"
                thread_handled_this_turn = True
                break

    # B-5 修复（实际撤销机制）：只覆盖三个纯追加、此前完全没有移除路径的集合（见
    # VALID_CANCEL_TARGET 注释）。两个信号必须同时成立才触发移除：route_intent=CANCEL
    # （用户确实在表达撤销）且 cancel_target 指明具体分类（不是含混的"算了"）——避免模型
    # 单独填错 cancel_target 却没有真正的撤销意图时误删用户数据。只移除**最近一条**，
    # 定点删除历史中某一条需要额外的指代能力，本批不做。
    cancel_target = patch.get("cancel_target", "NONE")
    cancel_effect = None
    if patch.get("route_intent") == "CANCEL" and cancel_target != "NONE":
        if cancel_target == "SECONDARY_GOAL":
            target_list = snap["goal_structure"]["secondary_goals"]
        elif cancel_target == "NON_SACRIFICE_CONSTRAINT":
            target_list = snap["goal_structure"]["non_sacrifice_constraints"]
        else:  # BUSINESS_GOAL_CATEGORY —— VALID_CANCEL_TARGET 里唯一剩下的非 NONE 取值
            target_list = snap.setdefault("business_goal_categories", [])
        if target_list:
            removed_text = target_list.pop()
            changed = True
            cancel_effect = {"target": cancel_target, "removed_text": removed_text}
        else:
            cancel_effect = {"target": cancel_target, "removed_text": None}

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

    # M1-AC-17 修复（最小账号锚点）：扁平自由文本，遇到才写入，不强制建档。confirmation
    # 恒为 SYSTEM_TENTATIVE（与 account_stage.confirmation 同一类已裁决理由：P0 没有按
    # 字段的用户确认通道）。source 标 USER_DIRECT——本轮真是从自然语言里抽出来的，不是
    # 调用方注入的（后者走 main() 的 account_anchor_supplied，发生在 _merge_patch 之外）。
    #
    # **对抗式审查发现的真实缺口，已修复**：此前一旦 source 已经是 CALLER_SUPPLIED（未来
    # M2 真实锚点），本轮任何一句自然语言旁白（哪怕只是顺口提一句"我们好像还有个小号"）
    # 都会把它静默覆盖成 USER_DIRECT，且遗留的 confirmation 仍是调用方给的高等级值——
    # 变成一条被模型临时文本冒名的"高置信度"记录。M2 锚点的权威性应该高于对话里的临时
    # 线索，这里改为 source 已是 CALLER_SUPPLIED 时不接受自然语言覆盖；写入 USER_DIRECT
    # 的同时也把 confirmation 一并重置为 SYSTEM_TENTATIVE，不遗留旧等级。
    snap.setdefault("account_anchor", {"identity_text": None, "source": "NONE", "confirmation": "SYSTEM_TENTATIVE"})
    anchor_text = (patch.get("account_anchor_text") or "").strip()
    if anchor_text and snap["account_anchor"].get("source") != "CALLER_SUPPLIED":
        # 幂等写入（同 priority_order 先例）：文本和来源都已经是这个状态时不重复置 changed，
        # 避免用户逐轮重复同一句账号身份陈述也在无意义地推进 revision（对抗式审查发现
        # 的同一类回归，见下方 cta_context 几处写入的相同修复）。
        if snap["account_anchor"].get("identity_text") != anchor_text or snap["account_anchor"].get("source") != "USER_DIRECT":
            snap["account_anchor"]["identity_text"] = anchor_text
            snap["account_anchor"]["source"] = "USER_DIRECT"
            snap["account_anchor"]["confirmation"] = "SYSTEM_TENTATIVE"
            changed = True

    # M1-AC-18 修复（CTA 三层权限上下文）：M1 只编译，不写最终 CTA 文案。
    snap.setdefault(
        "cta_context",
        {
            "risk_tier": "UNSTATED",
            "target_text": None,
            "conversion_goal_text": None,
            "access_path_text": None,
            "authorized_high_risk_targets": [],
            "no_cta_requested": False,
        },
    )
    cta_ctx = snap["cta_context"]
    # 对抗式审查发现的真实 KeyError 隐患（helper 被直接喂一份手工构造、只有部分键的
    # cta_context 时）：不可达 main()（升级循环已补齐整份默认对象），但同 evidence_bundle/
    # business_goal_categories 一样的防御风格，保护直接调用 helper 的场景。
    cta_ctx.setdefault("authorized_high_risk_targets", [])
    cta_ctx.setdefault("no_cta_requested", False)

    # 本轮 patch 的原始取值——**下面的授权判定必须只用这两个"本轮"值，不能读
    # cta_ctx 里可能是很多轮以前留下的持久化值**（见下方授权判定的详细说明）。
    cta_target_this_turn = (patch.get("cta_target_text") or "").strip()
    cta_tier_this_turn = patch.get("cta_risk_tier", "UNSTATED")

    # 幂等写入（同 priority_order/business_goal_categories 先例）：值真的变化才置
    # changed，避免同一件事逐轮重复陈述也在无意义地推进 revision，也避免在 CANCEL
    # 分支"没有绑定到具体动作"的诚实反馈判断里被一次单纯的重复陈述污染（对抗式审查
    # 发现的真实回归：此前无条件 changed=True 会让"CANCEL + 恰好重复同一个 CTA 层级"
    # 这种轮次错误地跳过那句诚实反馈）。
    if cta_target_this_turn and cta_ctx.get("target_text") != cta_target_this_turn:
        cta_ctx["target_text"] = cta_target_this_turn
        changed = True
    if cta_tier_this_turn != "UNSTATED" and cta_ctx.get("risk_tier") != cta_tier_this_turn:
        cta_ctx["risk_tier"] = cta_tier_this_turn
        changed = True

    cta_goal = (patch.get("cta_conversion_goal_text") or "").strip()
    if cta_goal and cta_ctx.get("conversion_goal_text") != cta_goal:
        cta_ctx["conversion_goal_text"] = cta_goal
        changed = True

    cta_path = (patch.get("cta_access_path_text") or "").strip()
    if cta_path and cta_ctx.get("access_path_text") != cta_path:
        cta_ctx["access_path_text"] = cta_path
        changed = True

    # 高风险 CTA 授权：只有"本轮同时点名具体目标 + 本轮同时给出 HIGH_RISK 层级 + 用户
    # 本轮显式 GRANT 信号"三者同时成立才写入。**对抗式审查发现的真实缺口，已修复**：
    # 此前用的是 cta_ctx 里跨轮持久化的 risk_tier/target_text，只有 GRANT 信号本身是
    # 本轮的——层级和目标一旦在早前某一轮被设置就不会自动清零，导致很多轮之后一句和
    # CTA 毫无关系、只是被模型误判成 GRANT 的"行"/"好啊"，就能把一个早就不在讨论的
    # 目标授权掉；目标本身又是单值覆盖，同样可能把 GRANT 错配给"当前挂着的"另一个目标，
    # 而不是用户这一轮真正想授权的那个。改为要求三者都在同一轮 patch 里同时出现，
    # 结构上不再存在"跨轮授权"这条路径——这也是"缺一就暂停该 CTA 分支"在授权维度最
    # 严格的落地：不但缺一暂停，任何一项不是本轮同时说出口的，也一律不采信。
    cta_auth_signal = patch.get("cta_authorization_signal", "NONE")
    if (
        cta_auth_signal == "GRANT"
        and cta_tier_this_turn == "HIGH_RISK"
        and cta_target_this_turn
        and cta_target_this_turn not in cta_ctx["authorized_high_risk_targets"]
    ):
        cta_ctx["authorized_high_risk_targets"].append(cta_target_this_turn)
        changed = True

    # 对抗式审查发现的真实缺口，已修复：DECLINE 此前没有任何消费方，授权只能单向累加，
    # 一次误判的 GRANT 永久生效，一次真实的 DECLINE 却完全不生效。只在用户本轮明确
    # 针对同一个目标文本表示 DECLINE 时才移除——同 handled_thread_id 的先例一致：只做
    # 精确文本匹配，不做模糊匹配，宁可漏判也不凭空编造一次撤销。
    if (
        cta_auth_signal == "DECLINE"
        and cta_target_this_turn
        and cta_target_this_turn in cta_ctx["authorized_high_risk_targets"]
    ):
        cta_ctx["authorized_high_risk_targets"].remove(cta_target_this_turn)
        changed = True

    # "无 CTA ↔ 有授权 CTA"的多轮调整（§6.3）：双向开关，不是纯追加，用户改变方向时
    # 只重算这一处受影响的偏好本身。
    cta_pref = patch.get("cta_preference_signal", "NONE")
    if cta_pref == "REQUEST_NO_CTA" and not cta_ctx["no_cta_requested"]:
        cta_ctx["no_cta_requested"] = True
        changed = True
    elif cta_pref == "REQUEST_CTA" and cta_ctx["no_cta_requested"]:
        cta_ctx["no_cta_requested"] = False
        changed = True

    # evidence_bundle 必须在 revision 自增之前合并：captured_at_revision 取的是增量前的
    # revision（与 open_threads.raised_at_revision 同一时序先例）。
    evidence_appended, evidence_dropped_incomplete, evidence_provenance_downgraded = (
        _merge_evidence_item(snap, patch, material_present)
    )
    if evidence_appended:
        changed = True

    # content_changed：**在**并入 thread_handled_this_turn 之前的 changed 快照，供
    # _dialogue_directive 判断"本轮有没有值得对话 LLM 描述的新内容"（对抗式审查发现的
    # 第四个真实缺口的修复：纯粹的线程标记已处理不算这类新内容，否则会错误跳过 CANCEL
    # 分支"没有绑定到具体动作"的诚实反馈——用户说"这件事不用管了"时 route_intent=CANCEL
    # 与 handled_thread_id 很自然地同时出现）。
    content_changed = changed
    if thread_handled_this_turn:
        changed = True

    if changed:
        snap["revision"] = snap["revision"] + 1

    return snap, changed, evidence_dropped_incomplete, evidence_provenance_downgraded, cancel_effect, content_changed


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
    # permission 在 P0 仍只有一个可达值，不是真正被逐条判断出来的结果。写进条目却不登记
    # 降级，等于让下游把"恒定常量"读成"系统判断过权限"。**B-3 修复后旧的 degraded_to 理由
    # （"没有第三方材料通道"）已经失真**——材料上传通道已建成，第三方材料在物理上可能出现，
    # 只是本批没有引入材料权属问询机制，如实改写为新理由，不是延续旧结论。
    {
        "field_ref": "evidence_bundle[].permission",
        "status": "DEGRADED",
        "degraded_to": "ALWAYS_OWNED_BY_USER_NO_MATERIAL_OWNERSHIP_INQUIRY_CHANNEL",
    },
    # freshness 自 B-3 起不再是恒定常量（USER_DIRECT→FRESH，SOURCED_MATERIAL→UNKNOWN，
    # 见 _merge_evidence_item），这条改登记为"仍只有粗粒度二值判断，无法判断材料的真实
    # 生成时间"，不是"全恒定"。
    {
        "field_ref": "evidence_bundle[].freshness",
        "status": "DEGRADED",
        "degraded_to": "COARSE_TWO_VALUE_NO_REAL_DOCUMENT_AGE_FOR_SOURCED_MATERIAL",
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

    # M1-AC-17：账号锚点只在持续运营场景（CYCLE/LONG_TERM）下才算缺口——普通咨询/单次
    # 创作（ONE_ITEM/UNSTATED）不要求建档，问了也没地方用，不得强行追问（§5.3 原文）。
    # **对抗式审查发现的真实缺口，已修复**：此前额外要求 `source == "NONE"`，导致调用方
    # 传入一个没有 identity_text 的退化 account_anchor_supplied（比如只给了 confirmation
    # 没给 identity_text）时，source 变成 CALLER_SUPPLIED 但账号身份其实什么都没有，这条
    # 缺口却因为 source 不等于 NONE 而被静默吞掉——判据应该只看"有没有真实身份内容"，
    # 不看来源标签，和其它字段（如 account_stage.text）的缺口判据同一口径。
    anchor = snapshot.get("account_anchor") or {}
    temporal_scope = current_task.get("temporal_scope", "UNSTATED")
    if temporal_scope in ("CYCLE", "LONG_TERM") and not anchor.get("identity_text"):
        gaps.append({"field_ref": "account_anchor.identity_text", "status": "MISSING", "degraded_to": None})

    # M1-AC-18：只在真的有 CTA 在讨论时才登记缺口——没有话题就没有"缺信息"可言。经营
    # 目标/承接路径缺一，只暂停 CTA 这一个分支（不是整任务拒绝），且用户已表示这个阶段
    # 不要 CTA 时不必追问这两项（不打算做就不用先备齐材料）。
    #
    # **对抗式审查发现的真实缺口，已修复**：授权缺口此前和 no_cta_requested 共用同一个
    # 判断分支，导致"用户说了不要 CTA，之后又在同一/后续轮次真的提到一个具体高风险动作"
    # 时，授权检查被 no_cta_requested 短路跳过——一个仍然真实存在、尚未获得授权的高风险
    # 目标就这样从缺口清单和对话提醒里同时消失。这不是"要不要主动建议 CTA"的开关能覆盖
    # 的范围：授权是安全门槛，不是建议开关，必须独立判断、不受 no_cta_requested 影响。
    # 同时补上"层级是 HIGH_RISK 但没有具体目标"本身也是缺口——一个连目标都不清楚的高
    # 风险动作，结构上不可能满足"作用域明确"的授权前提，不能因为没有 target 就悄悄放行。
    cta = snapshot.get("cta_context") or {}
    cta_tier = cta.get("risk_tier", "UNSTATED")
    if cta_tier in ("BUSINESS_CONVERSION", "HIGH_RISK") and not cta.get("no_cta_requested"):
        if not cta.get("conversion_goal_text"):
            gaps.append({"field_ref": "cta_context.conversion_goal_text", "status": "MISSING", "degraded_to": None})
        if not cta.get("access_path_text"):
            gaps.append({"field_ref": "cta_context.access_path_text", "status": "MISSING", "degraded_to": None})
    if cta_tier == "HIGH_RISK":
        target = cta.get("target_text")
        if not target:
            gaps.append({"field_ref": "cta_context.target_text", "status": "MISSING", "degraded_to": None})
        elif target not in (cta.get("authorized_high_risk_targets") or []):
            gaps.append({"field_ref": "cta_context.authorization", "status": "MISSING", "degraded_to": None})
    # **已知限制，如实登记（对抗式审查指出，本批不做结构性修复）**：risk_tier 是单值、
    # 逐轮由模型现判现写，target_text 也是单值覆盖——如果某一轮模型把 risk_tier 判成
    # LOW_RISK/BUSINESS_CONVERSION（哪怕 target_text 实际还是同一个客观上高风险的动作，
    # 只是这一轮分类判轻了），上面这条 HIGH_RISK 专属的授权缺口会跟着消失，不会有
    # "曾经是 HIGH_RISK、现在被降级但目标没变"这种更细的追踪。要正确处理需要把风险层级
    # 按目标分别记录（而不是一个全局单值），是真正的结构调整，不在本批范围内。

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


def compute_call_intent(snap, requested_capabilities):
    """requested_capabilities：已解析、去重、保序的能力代码列表（见
    _parse_capabilities_text，B-4 修复）。空列表表示本轮没有点名任何能力。"""
    per_capability = {}
    needed = list(requested_capabilities or [])

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
    # 阻塞集合是本轮**全部**被请求且判定为 BLOCKED 的能力的阻塞字段并集（B-4 修复前只可能
    # 有一项被请求，并集退化成单项，行为不变；现在可能有多项同时被请求并同时 BLOCKED）。
    blocking_field_refs = set()
    for cap_id in needed:
        requested_info = per_capability.get(cap_id)
        if requested_info and requested_info["status"] == "BLOCKED":
            blocking_field_refs |= set(BLOCK_REASON_BLOCKING_FIELD_REFS.get(requested_info["block_reason"], []))

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


def _dialogue_directive(snap, patch_ok, reject_reason, call_intent, requested_capabilities,
                        current_route_intent=None, changed=False, cancel_effect=None,
                        material_present=False, cta_authorization_signal_this_turn="NONE"):
    """给对话 LLM 的确定性指令，不让模型自己判断状态或编造原因（继承 A-4 纪律）。

    current_route_intent：**本轮 patch 里的原始 route_intent**，不是 snap["last_route_intent"]。
    后者是跨轮持久化的"最后一次"，只读它会让一次取消表达在之后每一轮都被误判成"还在撤销中"。
    patch 未通过时调用方传 None（那种轮次本来就没有可信的本轮意图）。

    changed：**调用方传入的实为 _merge_patch 返回的 content_changed，不是它返回的 changed**
    （对抗式审查发现的真实问题：早期版本直接传 changed，会把"仅仅是某条 open_thread 被标记
    HANDLED"也算作"有内容变化"，导致用户说"这件事不用管了"——route_intent=CANCEL 与
    handled_thread_id 同时出现的自然表达——时，下面的诚实反馈被错误跳过，变成整轮沉默）。
    用来防止 CANCEL 分支说出"没有任何内容被撤销或删除"这句话——如果用户在同一轮里既说了
    "算了取消"又给出了新内容（比如"算了，改成做家居内容"），新内容会正常覆盖旧值，"没有
    任何内容被撤销或删除"在这种轮次就是假话（对抗式审查真实发现的问题）。changed=True 时
    跳过这句断言，只让其余分支如实描述当前状态。

    cancel_effect：B-5 修复新增，_merge_patch 算好的实际撤销结果（见该函数注释），三种取值：
    None（本轮没有指明具体撤销分类）／{"removed_text": 具体内容}（真的撤销了一条）／
    {"removed_text": None}（指明了分类但那个分类下当前没有可撤销的内容）。

    material_present：本轮 m1_join 是否真的抽出了非空材料文本（由 main() 传入，与
    _merge_evidence_item 核实 SOURCED_MATERIAL 声明用的是同一个信号）。**live 验证
    发现的真实缺口，已修复**：m1_chat_llm 的 prompt 里看不到材料原文（只有 m1_shadow
    才看得到 {{#m1_join.material_text#}}），它判断"有没有收到资料"的唯一信息来源就是
    这份 dialogue_directive；这里不说，它就只能诚实地猜"没收到"，跟系统内部真实收到并
    处理了材料的事实矛盾——真实 Dify 环境里实测到这个场景。

    **两次真实回归都发现的问题，已修复为直接用 material_present 而不是"本轮是否真的
    追加了一条 evidence_bundle 条目"**：后者会在材料被重复上传（去重跳过追加）、
    evidence_nature 缺失（整条证据被丢弃）、或模型把材料内容写进了 evidence_text 以外
    的字段这三种情况下都不成立，而这三种情况下 material_present 仍然是 True——用同一个
    "有没有材料"的问题接了两种不同、可能不一致的答案，是真实的活口。改用 material_present
    后这三种情况都能正确触发确认，且不再需要把 _merge_evidence_item 追加的具体证据文本
    往上传：只做一句不含材料原文的事实确认（"本轮确实收到了资料"），不复述、不引用
    材料里的具体字句——避免把未经代码核实"这句话真的来自材料"的模型自称，包装成对用户
    的确定性断言，也避免把材料原文的任意内容拼进对话 LLM 的指令通道（m1_chat_llm 的
    prompt/system 提示词里没有 SHADOW_SYSTEM_PROMPT 那样的抗注入条款，材料原文一旦被
    整段引用进这里就是一个新的、没有任何缓解措施的注入面）。

    cta_authorization_signal_this_turn：v1.4.1 Rebase 新增（M1-AC-18），本轮 patch 里的
    原始 cta_authorization_signal。只用于 DECLINE 确认这一处——DECLINE 是一次性动作
    信号，没有持久化状态可读，天然只能靠本轮值驱动。CTA 的"无 CTA 偏好"和"高风险未
    授权"这两段提醒改读 snap["cta_context"] 的持久化状态、每轮无条件如实反映现状（同
    current_task.text 的既有做法），不再用"这一轮有没有重提"做门禁——对抗式审查发现
    那样做会在用户恰好在同一轮要求执行、但没有重复给出分类时制造一个真空窗口，让
    "不要再问、直接推进"和"其实还没授权"这两个本该同时出现的信号变成只出现一个。
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
        # **对抗式审查发现的真实缺口，已修复**：此前把原始 reject_reason（形如
        # "ILLEGAL_ENUM:cta_risk_tier:EXTREME_RISK"）直接拼进这句话——这正是
        # CAPABILITY_LABEL_ZH/BLOCK_REASON_LABEL_ZH/BUSINESS_GOAL_CATEGORY_LABEL_ZH 三处
        # 已经在防的同一类 CE-A2 缺陷（内部字段名/枚举代码经这条指令通道被对话 LLM 当成
        # 用户说过的话复述出来），新增的七个字段只是又开了七条新的泄漏路径，不是新问题。
        # 不给具体是哪个字段/取值出了问题——诚实到"校验没通过"这一层即可，不需要归因到
        # 内部实现细节。
        return (
            "补丁校验未通过（内部取值不合法，不是用户表达得不清楚）。保持旧任务状态不变，"
            "正常回答用户，不要声称任何确认、授权或执行已经生效，也不要提及具体是哪个"
            "字段或代码出了问题。"
        )

    parts = []

    # 用户本轮表达了撤回/取消。**B-5 修复：cancel_target 指明具体分类时，是真实撤销机制**
    # （见 _merge_patch 注释），不再是"只做诚实反馈,不实现撤销状态机"——那句旧话只对
    # "没有指明具体分类"这种含混情况仍然成立，因为按其它字段撤销需要的历史栈/额外指代能力
    # 是真正的设计判断，不在本批擅自新建（同一类范围裁定见 VALID_CANCEL_TARGET 注释）。
    #
    # 三条分支，按 cancel_effect 的形状区分：
    #   1) 真的撤销了一条内容（removed_text 非空）→ 明确告知撤销的具体分类和内容。
    #   2) 指明了分类但那个分类下当前没有可撤销的内容（removed_text 是 None）→ 如实说明
    #      "没有可撤销的内容"，不得声称已经撤销了什么。
    #   3) 没有指明具体分类（cancel_effect 是 None）且本轮**没有其他状态变化**→ 沿用此前
    #      已修复的诚实反馈："没有把撤回绑定到任何具体动作"。用户完全可能在同一句话里既说
    #      取消又给出新内容（"算了，改成做家居内容"），这种情况下旧值确实被新值覆盖了，
    #      断言"什么都没变"就是假话（对抗式审查真实发现的问题，不是假设）——changed=True
    #      时跳过这句断言，交给下面的分支如实描述当前状态即可。
    if current_route_intent == "CANCEL":
        if cancel_effect and cancel_effect["removed_text"] is not None:
            label = CANCEL_TARGET_LABEL_ZH.get(cancel_effect["target"], cancel_effect["target"])
            removed_display = cancel_effect["removed_text"]
            # **对抗式审查发现的真实泄漏，已修复**：business_goal_categories 存的是内部
            # 枚举代码（如 "STORE_VISIT"），不是用户原话；直接拼进指令文本会被对话 LLM
            # 当成用户说过的话复述出来，是 CE-A2 那一类缺陷的新触发口（CAPABILITY_LABEL_ZH/
            # BLOCK_REASON_LABEL_ZH 已经在处理这一类问题，这里补上第三处遗漏）。
            if cancel_effect["target"] == "BUSINESS_GOAL_CATEGORY":
                removed_display = BUSINESS_GOAL_CATEGORY_LABEL_ZH.get(removed_display, removed_display)
            parts.append(
                "用户这一轮要求撤销，已经把最近说的一条" + label + "去掉了：" + removed_display
                + "。如实告知这个具体撤销结果，不要复述成其它内容。"
            )
        elif cancel_effect and cancel_effect["removed_text"] is None:
            label = CANCEL_TARGET_LABEL_ZH.get(cancel_effect["target"], cancel_effect["target"])
            parts.append(
                "用户这一轮要求撤销" + label + "，但当前这个分类下没有记录任何可撤销的内容。"
                "如实告知这一点，不要声称已经撤销了什么。"
            )
        elif not changed:
            # **对抗式审查发现的措辞问题，已修复**：不得断言"用户没有指明"——cancel_target
            # 是影子模型的解析结果，指明不明确既可能是用户真的说得含混，也可能是模型没
            # 解析出来；把这个不确定性单方面归给用户是不实归因，与
            # test_directive_does_not_overclaim_user_named_the_capability 锁定的同一条
            # 纪律（不得断言"用户点名"）性质相同。措辞改回只描述系统这边的状态，不对用户
            # 表达的清晰度下判断。
            parts.append(
                "用户这一轮表达了要取消或撤回。当前系统这边并没有把这次撤回绑定到任何具体"
                "动作上，所以实际上没有任何内容被撤销或删除。如实告诉用户这一点，不要说"
                "已经撤销了什么，也不要说正在处理撤销；可以提示用户，如果是想撤销最近说过"
                "的某一条次要目标、不可让步条件或经营目标类别，可以再具体说明是哪一类；"
                "不必追问其它当前环境接不住答案的撤销请求。"
            )
        # 剩下一种情况：cancel_effect 是 None 且 changed=True——用户同一轮里除了含混的
        # "算了"之外还给了新内容，新内容已经正常合并，交给下面的分支如实描述当前状态，
        # 不重复"什么都没变"这句现在已经是假话的断言。

    # **v1.4.1 Rebase 修复 M1-B-25**：用户已经明确要求现在执行，系统这边却继续追问
    # "要不要调用/推进"——真实 live 审计发现的对话稳定性缺陷（Delta v1.4.1 §5.5「明确执行
    # 请求已经足够时，直接形成调用意图，不再问"要不要调用"」）。此前 dialogue_directive
    # 对 EXECUTE_REQUEST 和 DISCUSS/FOCUS 一视同仁，没有任何文本告诉 m1_chat_llm 不要再
    # 征求同意，模型只能自己猜、猜错就变成重复确认。
    if current_route_intent == "EXECUTE_REQUEST":
        parts.append(
            "用户这一轮已经明确要求现在执行或接受结果。不要再问\"要不要调用\"或\"是否需要"
            "现在处理\"这类确认性问题，直接确认已经识别到这个执行请求，并如实说明当前状态"
            "（比如具体还在等哪个信息、还是已经可以说明接下来会怎么处理）。"
        )

    if snap["current_task"]["text"]:
        parts.append("当前任务：" + snap["current_task"]["text"])
    else:
        parts.append("当前系统这边确实还没有记录任何任务内容（不是用户表达得不够清楚，"
                      "也不是落库失败，就是还没有形成任务）。")

    # **live 验证发现的真实缺口，已修复**：本轮客观上真的收到了上传材料，如实告知对话
    # LLM——它自己看不到材料原文，不说这句它就只能猜"没收到"。只做事实确认，不复述材料
    # 具体内容（原因见函数 docstring：避免未经核实的内容归属断言，也避免材料原文经这条
    # 通道拼进对话 LLM 的指令里）。
    if material_present:
        parts.append(
            "本轮确实收到并处理了你上传的资料。如实确认收到了资料，不要声称没有收到"
            "资料或内容；具体内容不必复述，除非用户追问细节。"
        )

    # M1-AC-18 修复（CTA 三层权限上下文）。**对抗式审查发现的真实缺口，已修复**：
    # 此前这三段提醒都套在"本轮 patch 是否重新给出 cta_risk_tier"这个此前设想的
    # 反噪音开关下面，且授权提醒还和 no_cta_requested 共用同一个 if/elif——制造了两个
    # 真实的不设防窗口：①用户已表示不要 CTA、之后真的又提到一个具体高风险动作时，
    # no_cta_requested 直接短路掉授权检查；②只要这一轮的 patch 没有重新给出
    # cta_risk_tier（哪怕快照里仍然记着一个未授权的 HIGH_RISK 目标——比如用户这一轮说
    # "行，就按这个来"，route_intent=EXECUTE_REQUEST 但没有重复分类），提醒和上面
    # "不要再问、直接推进"的指令会同时出现在同一轮指令里，是最危险的组合。改为下面
    # 三段全部只读**持久化快照状态**、每轮无条件如实反映现状（与 current_task.text 的
    # 既有做法同一原则），不再用"这一轮有没有重提"做门禁——授权是安全门槛，不是
    # "要不要建议 CTA"这种可以随话题淡出的建议开关。cta_target_text 是用户本轮说出口
    # 的原话/贴近原话，直接引用与 current_task.text、CANCEL 分支的 removed_text 是
    # 同一类已确立的做法，不需要经 *_LABEL_ZH 翻译（那类映射只处理内部枚举代码）。
    cta = snap.get("cta_context") or {}
    if cta.get("no_cta_requested"):
        parts.append(
            "用户已经表示这个阶段不需要 CTA，如实遵从这一点，不要主动建议 CTA 内容，"
            "除非用户之后又明确改变说法。"
        )

    # 对抗式审查发现的真实缺口，已修复：cta_authorization_signal=DECLINE 此前没有任何
    # 消费方，用户明确拒绝授权这件事完全不会被告知给对话 LLM。只在本轮 patch 真的给出
    # DECLINE 信号时确认一次（这是瞬时动作，不是持久化状态，天然只能靠本轮信号驱动，
    # 和上面两段"读持久化状态"性质不同）。
    if cta_authorization_signal_this_turn == "DECLINE":
        parts.append(
            "用户这一轮明确表示不同意/拒绝这个 CTA 动作。如实确认没有获得授权，"
            "不要建议或推进这个动作。"
        )

    if cta.get("risk_tier") == "HIGH_RISK":
        target = cta.get("target_text")
        if not target:
            # 对抗式审查发现的真实缺口，已修复：层级已经是 HIGH_RISK 但没有具体目标时，
            # 此前两处判断都用 `if target and ...`，一个连目标都不清楚的高风险动作就这样
            # 完全不设防——一个空目标结构上不可能满足"作用域明确"的授权前提。
            parts.append(
                "识别到当前在讨论一个高风险动作（站外导流／价格优惠／强购买承诺等），"
                "但还不清楚具体是什么行动。如实说明需要先弄清楚具体想做什么，才能再谈"
                "是否可以执行，不要假设或编造具体内容。"
            )
        elif target not in (cta.get("authorized_high_risk_targets") or []):
            parts.append(
                "当前在讨论的这类站外导流／价格优惠／强购买承诺等高风险动作（" + target
                + "），还没有获得明确、针对这个具体动作的授权。如实告知这一点，不要声称"
                "已经可以这样做，也不要因为用户提到起号、吸粉、流量、成交额或线索这类"
                "经营目标就当作已经获得授权——这些目标不自动授权高风险动作。"
            )

    # B-4 修复：本轮可能同时点名了多个能力，逐个描述各自状态，不再只能报告单一能力。
    for cap_id in requested_capabilities or []:
        info = call_intent["per_capability"].get(cap_id)
        if not info:
            continue
        label = CAPABILITY_LABEL_ZH.get(cap_id, cap_id)
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
        # v1.4.1 Rebase 新增：M1-AC-17 最小账号锚点 + M1-AC-18 CTA 三层权限上下文透传。
        # 与其它维度同一原则：整条保留，不摊平，下游自行判断 confirmation/risk_tier。
        "account_anchor": dict(
            snapshot.get("account_anchor") or {"identity_text": None, "source": "NONE", "confirmation": "SYSTEM_TENTATIVE"}
        ),
        "cta_context": {
            "risk_tier": (snapshot.get("cta_context") or {}).get("risk_tier", "UNSTATED"),
            "target_text": (snapshot.get("cta_context") or {}).get("target_text"),
            "conversion_goal_text": (snapshot.get("cta_context") or {}).get("conversion_goal_text"),
            "access_path_text": (snapshot.get("cta_context") or {}).get("access_path_text"),
            "authorized_high_risk_targets": list((snapshot.get("cta_context") or {}).get("authorized_high_risk_targets") or []),
            "no_cta_requested": bool((snapshot.get("cta_context") or {}).get("no_cta_requested", False)),
        },
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


def main(user_query: str, snapshot_json: str, shadow_patch: dict, material_text: str = "",
         account_anchor_supplied: dict = None) -> dict:
    """material_text：m1_join 节点抽取并拼接后的本轮上传材料原文，默认空字符串（B-3 修复；
    Dify 节点接线见 build_m1_candidate_dsl_v0.1.py 里 m1_compiler.variables 新增的
    material_text 输入）。只用于核实 evidence_provenance=SOURCED_MATERIAL 的声明，不直接
    进入快照或对话文本。

    account_anchor_supplied：v1.4.1 Rebase 新增（M1-AC-17），可选。留给未来"持续运营且
    M2 有当前合法锚点"这条路径的消费入口——调用方（未来的 M2 最小投影读取方）已经确认的
    账号锚点，形如 {"identity_text": ..., "confirmation": "..."}。提供时覆盖 account_anchor
    且 source=CALLER_SUPPLIED，不依赖本轮自然语言重新提取。**当前 Dify DSL 图里没有任何
    节点会传这个参数**（M2 本身还不存在），默认 None，行为与不传完全一致——这只是一个纯
    参数注入点，M1 不因此读取或写入任何外部数据库，真正的 M2 读取动作（如果将来存在）
    发生在调用方，不在本文件内。"""
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

    material_present = bool((material_text or "").strip())

    requested_capabilities = []
    if patch_ok:
        snap, changed, evidence_dropped_incomplete, evidence_provenance_downgraded, cancel_effect, content_changed = (
            _merge_patch(snap, patch, material_present)
        )
        requested_capabilities = _parse_capabilities_text(patch.get("requested_capabilities_text", ""))
    else:
        changed = False
        evidence_dropped_incomplete = False
        evidence_provenance_downgraded = False
        cancel_effect = None
        content_changed = False

    # M1-AC-17：调用方显式提供的账号锚点（当前无实际调用方，见形参说明）覆盖本轮自然语言
    # 提取结果——真实 M2 锚点的权威性高于对话里的临时线索。放在 _merge_patch 之后，确保
    # 不被本轮 account_anchor_text 覆盖回去。
    #
    # **对抗式审查发现的真实缺口，已修复**：此前只判断 account_anchor_supplied 这个字典
    # 本身是否非空，一个没带 identity_text 的退化调用（比如只给了 confirmation）也会被
    # 接受，把 source 标成 CALLER_SUPPLIED 却没有任何真实身份内容——账号锚点缺口的判据
    # 已经改成只看 identity_text 是否有值（见 _compute_gaps），这里必须同一个口径，否则
    # 这种退化调用会让一个其实什么都没有的账号锚点悄悄不再被追问。
    if account_anchor_supplied and account_anchor_supplied.get("identity_text"):
        snap["account_anchor"] = {
            "identity_text": account_anchor_supplied.get("identity_text"),
            "source": "CALLER_SUPPLIED",
            "confirmation": account_anchor_supplied.get("confirmation", "SYSTEM_TENTATIVE"),
        }

    # gaps[] 每轮整体重算并覆写。**无条件执行**（不放在 if patch_ok 分支内）：patch 被拒绝的
    # 轮次同样重算，结果与上一轮相同，因为快照没变。这次覆写**不置 changed、不推进 revision**
    # ——缺口清单是既有状态的派生视图，不是用户造成的状态变化。
    # include_structural=False：只持久化随对话状态变化的动态子集（空快照上 13 条）。9 条结构性
    # 常量内容恒定、不携带任何本轮独有信息，逐轮写进 Dify 会话变量只会让快照白白膨胀；需要完整
    # 22 条合规视图的调用点（project_content_task）自行以 include_structural=True 重算。
    snap["gaps"] = _compute_gaps(snap, include_structural=False)

    call_intent = compute_call_intent(snap, requested_capabilities)
    # M1-AC-18：本轮原始 cta_authorization_signal，同 current_route_intent 一样只能取本轮
    # patch 的值（DECLINE 是一次性动作信号，理由同 _dialogue_directive 的形参说明）。
    cta_authorization_signal_this_turn = (
        patch.get("cta_authorization_signal", "NONE") if patch_ok and isinstance(patch, dict) else "NONE"
    )
    directive = _dialogue_directive(
        snap, patch_ok, reject_reason, call_intent, requested_capabilities, current_route_intent,
        content_changed, cancel_effect, material_present, cta_authorization_signal_this_turn,
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
                "requested_capabilities": requested_capabilities,
                "needed_capabilities": call_intent["needed_capabilities"],
                "open_threads_open_count": len(
                    [t for t in snap["open_threads"] if t.get("status") in ("OPEN", "SURFACED")]
                ),
                # 本轮有一条证据因维度不全（给了原话、没给性质）被丢弃。如实登记在**不面向
                # 用户**的机器可读通道里：dialogue_directive 不变、reject_reason 不变，
                # 不给"内部枚举被对话 LLM 复述给用户"（CE-A2）这个已知缺陷新增触发器。
                "evidence_dropped_incomplete": evidence_dropped_incomplete,
                # B-3 修复：本轮是否发生了"模型声称材料来源，但客观没有材料文本"的降级。
                # 如实登记在不面向用户的通道里，供 Reviewer/后续批次判断模型是否常态化
                # 误判来源（若这条经常为 true，说明 evidence_provenance 判据需要重新设计）。
                "evidence_provenance_downgraded": evidence_provenance_downgraded,
            },
            ensure_ascii=False,
        ),
    }
