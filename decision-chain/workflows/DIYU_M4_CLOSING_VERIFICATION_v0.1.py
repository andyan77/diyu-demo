#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""M4 收口核验与剩余技术验收 v0.1

task_id: V1-M4-CAPABILITY-SEAMS-RUNTIME-INTEGRATION-001
权威事件: RULESIDE-2026-08-26-M4-003（Founder 冻结指令）

**这个脚本证明什么**

在冻结候选 `0dcd66f` 之上，把取证判据合同 §2 里**尚未裁定**的 criterion 跑完：
把冻结夹具包 v0.1 中**尚未运行过**的夹具喂给已发布的 M4 后继应用，落盘原始证据，
再按**结果之前就冻结的** Oracle 逐条判定；最后做**一次** affected-scope 收口核验。

**这个脚本不做什么**

- 不改任何交付物字节（六份后继 Skill / 八份 DSL / 生成器 / 发布脚本 / 绑定记录）
- 不对 Dify 做任何写操作（不发布、不注册工具、不改 provider、不建不删应用）
  —— 只做 GET 与 `/v1/workflows/run` 执行
- 不判断「哪份内容更好」（CLAUDE.md §4）。标 `H` 的判据只把对照运行跑出来、
  把原始输出落盘、生成可直接在 Dify 里复跑的测试卡，判定权在 Founder。

用法：
  run2      跑剩余冻结夹具（FA-14…FA-33）
  swap      AC-02 两两互换（SW-xx，6 能力全部有序对 30 组，非抽样）
"""

import hashlib
import importlib.util
import json
import os
import sys
import time

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
DC_WF = os.path.join(ROOT, "decision-chain", "workflows")
CP_WF = os.path.join(ROOT, "content-production", "workflows")
EVID = os.path.join(ROOT, "decision-chain", "evidence", "m4")
RUNS = os.path.join(EVID, "runs")
PACK = os.path.join(ROOT, "decision-chain", "fixtures", "m4",
                    "V1_M4_SEAM_FIXTURE_PACK_v0.1.md")

ENVIRONMENT = "本机 Docker Dify 1.16.1"
ORACLE_REF = "V1_M4_EVIDENCE_COLLECTION_CONTRACT_v0.1.md §2（结果前冻结）"
FROZEN_CANDIDATE = "0dcd66fd39692ed07df80e39c1f27511d9cbf283"


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


FA = _load("m4fa", os.path.join(DC_WF, "DIYU_M4_FORMAL_ATTEMPT_v0.1.py"))
PUB = FA.PUB
FX = FA.FX


def sha(s):
    return hashlib.sha256((s or "").encode("utf-8")).hexdigest()


def file_sha(p):
    with open(p, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


# ======================================================================
# 冻结夹具的可运行转写
# ----------------------------------------------------------------------
# 纪律：每一条都逐字来自冻结夹具包 v0.1 的对应小节（§号写在常量上方）。
# 夹具包 §0 的共用背景（四个真实组织角色、经营任务、表达边界）是该包
# **已经冻结**的正文，转写时原样引用，不新增品牌事实。
# 凡夹具包只给散文而未给字段的，转写只做「散文 → 同义字段」的形式变换，
# 不补任何夹具未提供的经营事实（CLAUDE.md §4：不补写夹具未提供的事实）。
# ======================================================================

# --- §7.1 FX-M4-CAMPAIGN-UNCONFIRMED（N-05 / N-40）--------------------
# 包原文：「输入是一个尚未形成决定的经营任务描述（有期限、有目标、有受众、
#          有一条可用事实链，但没有已确认的参战名单、顺序或承接结论）」
CAMPAIGN_UNCONFIRMED = """
provenance:
  source_kind: USER_DIRECT
  confirmation_state: NOT_CONFIRMED
subject_and_account_scope: 序里集
objective:
  primary_goal: 初秋通勤衣橱第一阶段，把序里集的分层判断讲到目标顾客能自己复用
  goal_family: LONG_TERM_VALUE
audience_problem: 已经有几件通勤外套的顾客，早上仍然要花十几分钟才决定穿什么
deadline_or_stage_boundary: 初秋通勤衣橱第一阶段
facts_registered:
  - "[夹具登记事实] 苏禾在门店做过一次三组试穿记录：同一件廓形西装，分别配针织马甲、薄衬衫、单穿"
  - "[夹具登记事实] 该记录写明：连穿一天后，加马甲那组在领口、袖窿、下摆三处偏挤"
  - "[夹具登记事实] 同一条记录后半句写明：去掉马甲后，正式感也跟着掉了一档"
confirmed_decisions:
  roster: "[夹具故意缺失] 参战名单尚未确认"
  order: "[夹具故意缺失] 顺序尚未确认"
  handoff_conclusion: "[夹具故意缺失] 承接结论尚未确认"
expression_boundary: 不得制造身材或年龄焦虑
capacity_or_owner: 本周可投入：苏禾半天出镜 + 单人手机拍摄
"""

# --- §7.2 FX-M4-CAMPAIGN-CONFIRMED-PACK（N-06）------------------------
# 包原文：「输入是一份已确认决定包（参战名单、主讲、顺序、承接口径均已由用户确认）」
# 名单与角色取自包 §0 共用背景中的真实组织角色，不新增人物。
CAMPAIGN_CONFIRMED_PACK = """
provenance:
  source_kind: USER_DIRECT
  confirmation_state: CONFIRMED_BY_USER
subject_and_account_scope: 序里集
objective:
  primary_goal: 初秋通勤衣橱第一阶段，把序里集的分层判断讲到目标顾客能自己复用
  goal_family: LONG_TERM_VALUE
deadline_or_stage_boundary: 初秋通勤衣橱第一阶段
confirmed_decisions:
  roster: ["序里集品牌号", "苏禾（零售搭配负责人）", "陈晚（旗舰店店长）", "周宁（商品负责人）"]
  lead_speaker: 苏禾
  order: ["第1条 苏禾", "第2条 序里集品牌号", "第3条 周宁", "第4条 陈晚"]
  handoff_wording: "到店预约；主承接人陈晚，替补苏禾；受理边界：工作日到店时段"
  confirmed_by: USER
facts_registered:
  - "[夹具登记事实] 苏禾三组试穿记录：加马甲那组在领口、袖窿、下摆三处偏挤"
  - "[夹具登记事实] 去掉马甲后，正式感也跟着掉了一档"
expression_boundary: 不得制造身材或年龄焦虑
audience_problem: 已经有几件通勤外套的顾客，早上仍然要花十几分钟才决定穿什么，最后常常穿回同一套
capacity_or_owner: 本周可投入：苏禾半天出镜 + 单人手机拍摄
"""

# --- §7.3 FX-M4-CAMPAIGN-OVERRIDE-END（N-41）--------------------------
# 包 §7.3 的 yaml 逐字转写
CAMPAIGN_OVERRIDE_END = """
provenance:
  source_kind: USER_DIRECT
subject_and_account_scope: 序里集
campaign_scope: CYCLE_OVERRIDE
cycle_baseline_present: true
override_scope: "本周期第 3–4 条内容位置"
event: "覆盖期结束"
conflict: "[夹具登记事实] 周期基线第 4 条原定由陈晚发布，覆盖期内改为苏禾"
objective:
  goal_family: LONG_TERM_VALUE
expression_boundary: 不得制造身材或年龄焦虑
deadline_or_stage_boundary: 初秋通勤衣橱第一阶段
audience_problem: 已经有几件通勤外套的顾客，早上仍然要花十几分钟才决定穿什么，最后常常穿回同一套
facts_registered:
  - "[夹具登记事实] 苏禾三组试穿记录：同一件廓形西装，分别配针织马甲、薄衬衫、单穿"
  - "[夹具登记事实] 连穿一天后，加马甲那组在领口、袖窿、下摆三处偏挤"
  - "[夹具登记事实] 去掉马甲后，正式感也跟着掉了一档"
capacity_or_owner: 本周可投入：苏禾半天出镜 + 单人手机拍摄
"""

# --- §7.4 FX-M4-CAMPAIGN-GOAL-NARROWING（N-33）------------------------
CAMPAIGN_GOAL_NARROWING = """
provenance:
  source_kind: USER_DIRECT
subject_and_account_scope: 序里集
input_goal_family: FOLLOWER_GROWTH
objective:
  primary_goal: 初秋通勤衣橱阶段把账号做起来，让更多目标顾客关注
  goal_family: FOLLOWER_GROWTH
legacy_path_behavior_expected: "旧路径倾向把主目标类型收窄为『认知变化』"
deadline_or_stage_boundary: 初秋通勤衣橱第一阶段
facts_registered:
  - "[夹具登记事实] 苏禾三组试穿记录：加马甲那组在领口、袖窿、下摆三处偏挤"
expression_boundary: 不得制造身材或年龄焦虑
audience_problem: 已经有几件通勤外套的顾客，早上仍然要花十几分钟才决定穿什么，最后常常穿回同一套
capacity_or_owner: 本周可投入：苏禾半天出镜 + 单人手机拍摄
"""

# --- §6.1 FX-M4-MATRIX-SUFFICIENT（AC-19 / N-04 / N-38 / N-39）--------
# 包原文：「输入含：品牌业务模式、核心顾客、当前经营任务、四个真实候选角色
#          及其权责与一手来源、已确认表达边界（全部来自受保护品牌夹具 §一–§八）」
# 四个角色与其权责逐字取自包 §0 共用背景。
MATRIX_SUFFICIENT = """
provenance:
  source_kind: USER_DIRECT
applicability_reason: 用户要求建立四个账号的长期分工，涉及长期定位与账号职责
subject_and_account_scope: 序里集，四个账号
business_model: 面向 30–45 岁城市女性的中高端女装集合店，华东新一线，2 家直营门店
core_customer: 30–45 岁城市女性；已有几件通勤外套，早上仍要花十几分钟决定穿什么
current_business_task: 「初秋通勤衣橱」第一阶段上新；重点商品为廓形西装、阔腿裤、针织马甲、衬衫、半裙、轻外套
objective:
  primary_goal: 建立四个账号的长期分工
  goal_family: LONG_TERM_VALUE
candidate_roles:
  - name: 林序
    title: 创始人
    duty: 买手与门店经营出身；决定品牌方向与选品口径；表达直接务实
    first_person_source: 亲自跑市场与看货的判断过程；门店经营决策现场
  - name: 周宁
    title: 商品负责人
    duty: 选品、商品组合、版型比较
    first_person_source: 每一季的版型比较记录与商品组合决策
  - name: 苏禾
    title: 零售搭配负责人
    duty: 陈列、试穿、成套搭配
    first_person_source: 门店试穿记录（如三组试穿：领口、袖窿、下摆三处偏挤）
  - name: 陈晚
    title: 旗舰店店长
    duty: 一线销售、熟客维护
    first_person_source: 顾客原话记录（如「上班需要正式，但下班接孩子时不想显得过于用力」）
expression_boundary: 禁年龄身材身份焦虑；禁「显瘦十斤」「闭眼入」类无依据话术；禁虚构顾客故事冒充真实案例
facts_registered:
  - "[夹具登记事实] 林序：买手与门店经营出身，亲自跑市场看货；一手来源=选品决策现场"
  - "[夹具登记事实] 周宁：负责选品、商品组合、版型比较；一手来源=每季版型比较记录"
  - "[夹具登记事实] 苏禾：负责陈列、试穿、成套搭配；一手来源=门店试穿记录（三组试穿：领口、袖窿、下摆三处偏挤）"
  - "[夹具登记事实] 陈晚：负责一线销售与熟客维护；一手来源=顾客原话记录"
"""

# --- §5.1 FX-M4-REALIZATION-PLAN-ONLY（应推导为 PRE）------------------
REALIZATION_PLAN_ONLY = """
provenance:
  source_kind: HISTORICAL_ARTIFACT
content_body_or_beats: B1/B2/B3/B4 四个单元
content_promise: 给出一个可以在自己衣橱里直接照做的分层判断
explicit_non_promise: 不承诺哪一件更好
realization_plan_present: true
realization_manifest_present: false
content_origin_mode: [现拍]
plan_note: "四个单元已排好，素材待产出·可控"
cta_level: LOW_RISK_INTERACTION
asset_publish_permission: 门店内拍摄已授权；不得出现其他顾客正脸
subject_domain: 服装 / 门店零售
platform: NOT_LOCKED
objective:
  goal_family: LONG_TERM_VALUE
facts_registered:
  - "[夹具登记事实] 苏禾三组试穿记录：同一件廓形西装，分别配针织马甲、薄衬衫、单穿"
  - "[夹具登记事实] 连穿一天后，加马甲那组在领口、袖窿、下摆三处偏挤"
  - "[夹具登记事实] 去掉马甲后，正式感也跟着掉了一档"
cta_contract: LOW_RISK_INTERACTION
"""

# --- §5.2 FX-M4-REALIZATION-MIXED（应推导为 MIXED）--------------------
REALIZATION_MIXED = """
provenance:
  source_kind: HISTORICAL_ARTIFACT
content_body_or_beats: B1/B2/B3/B4 四个节拍
content_promise: 给出一个可以在自己衣橱里直接照做的分层判断
explicit_non_promise: 不承诺哪一件更好
realization_manifest:
  - {beat_id: B1, unit: U1, source: "00:00:04-00:00:11", support: 有, gap_disposition: 无缺口}
  - {beat_id: B2, unit: U2, source: "00:00:19-00:00:27", support: 有，但不够, gap_disposition: "等待补拍领口特写（未决）"}
  - {beat_id: B3, unit: U3, source: "00:00:31-00:00:40", support: 有, gap_disposition: 无缺口}
  - {beat_id: B4, unit: U4, source: "00:00:44-00:00:49", support: 有, gap_disposition: 无缺口}
all_planned_assets_exist: true
cta_level: LOW_RISK_INTERACTION
asset_publish_permission: 门店内拍摄已授权；不得出现其他顾客正脸
subject_domain: 服装 / 门店零售
platform: NOT_LOCKED
objective:
  goal_family: LONG_TERM_VALUE
facts_registered:
  - "[夹具登记事实] 苏禾三组试穿记录：同一件廓形西装，分别配针织马甲、薄衬衫、单穿"
  - "[夹具登记事实] 连穿一天后，加马甲那组在领口、袖窿、下摆三处偏挤"
  - "[夹具登记事实] 去掉马甲后，正式感也跟着掉了一档"
cta_contract: LOW_RISK_INTERACTION
"""

# --- §5.4 FX-M4-REALIZATION-ASSET-LEVEL-ONLY（应推导为 PRE）-----------
REALIZATION_ASSET_LEVEL_ONLY = """
provenance:
  source_kind: HISTORICAL_ARTIFACT
content_body_or_beats: B1/B2/B3/B4 四个节拍
content_promise: 给出一个可以在自己衣橱里直接照做的分层判断
upstream_says: "拍了 42 分钟"
beat_mapping_present: false
cta_level: LOW_RISK_INTERACTION
asset_publish_permission: 门店内拍摄已授权；不得出现其他顾客正脸
subject_domain: 服装 / 门店零售
platform: NOT_LOCKED
objective:
  goal_family: LONG_TERM_VALUE
explicit_non_promise: 不承诺哪一件更好
facts_registered:
  - "[夹具登记事实] 苏禾三组试穿记录：同一件廓形西装，分别配针织马甲、薄衬衫、单穿"
  - "[夹具登记事实] 连穿一天后，加马甲那组在领口、袖窿、下摆三处偏挤"
  - "[夹具登记事实] 去掉马甲后，正式感也跟着掉了一档"
cta_contract: LOW_RISK_INTERACTION
"""

# --- §5.5 FX-M4-ASSET-WITHDRAWN（N-16）-------------------------------
# 包原文：base = FX-M4-REALIZATION-FINAL；event = 「B2 所用素材的门店拍摄授权被撤回」
ASSET_WITHDRAWN = FX.FOOTAGE_FINAL + """
base_fixture: FX-M4-REALIZATION-FINAL
event: "B2 所用素材的门店拍摄授权被撤回"
"""

# --- §16.3 FX-M4-LOCAL-EDIT（N-11 / AC-14 / AC-09 / AC-24）------------
LOCAL_EDIT = FX.SCRIPT_LEGAL + """
change: "只把 B2 的『三处』改成『领口、袖窿、下摆这三处』（同一事实的更精确表述）"
semantic_keys_changed: []
prior_production_units_present: true
prior_units: ["U1(B1)", "U2(B2)", "U3(B3)", "U4(B4)"]
"""

# --- §22 FX-M4-IRRELEVANT-REFERENCE（N-18 / AC-11）--------------------
IRRELEVANT_REFERENCE = FX.CT_M3 + """
attachments_present:
  - name: "某美妆品牌 2023 年双十一投放复盘全文（27 页）"
    relevance_to_this_task: NONE
    note: "[夹具登记事实] 与本次服装分层判断任务无任何真实依赖关系"
  - name: "一份他人短视频脚本示例"
    relevance_to_this_task: EXAMPLE_ONLY
    note: "[夹具登记事实] 只是示例，不是模板也不是事实来源"
"""

# --- §21 FX-M4-NO-PLATFORM-EVIDENCE（N-17 / AC-11）--------------------
NO_PLATFORM_EVIDENCE = FX.FOOTAGE_FINAL + """
platform_evidence_available: false
platform_spec_source: "[夹具故意缺失] 当前平台的时长、封面尺寸、标题字数、发布时段均无可核实来源"
industry_benchmark_source: "[夹具故意缺失] 无当前行业数据"
"""

# --- §15 FX-M4-CTA-THREE（N-49 / AC-28）------------------------------
CTA_LOW_RISK = FX.CT_M3 + """
cta_case: case_low_risk
cta_goal_family: FOLLOWER_GROWTH
cta_ask: "评论区问一句『你早上卡在哪一层』"
cta_handoff_path: NOT_REQUIRED
"""

CTA_BUSINESS_HANDOFF = FX.CT_M3.replace(
    "  goal_family: LONG_TERM_VALUE", "  goal_family: STORE_VISIT").replace(
    "cta_level: LOW_RISK_INTERACTION", "cta_level: BUSINESS_HANDOFF") + """
cta_case: case_business_handoff
cta_goal_family: STORE_VISIT
cta_ask: "引导到店试穿"
cta_handoff_path:
  entry: "门店预约（唯一正式入口）"
  owner: "陈晚"
  backup: "苏禾"
  capacity: "工作日到店时段"
  min_info: "姓名 + 到店时段"
  confirm_action: "门店回复确认时段即视为申请被确认"
"""

CTA_HIGH_RISK = FX.CT_M3.replace(
    "  goal_family: LONG_TERM_VALUE", "  goal_family: GMV").replace(
    "cta_level: LOW_RISK_INTERACTION", "cta_level: HIGH_RISK") + """
cta_case: case_high_risk
cta_goal_family: GMV
cta_ask: "站外导流 + 承诺一个折扣价"
cta_authorization: NOT_GRANTED
"""

# --- §23 FX-M4-USER-VIEW（N-23 / AC-13）------------------------------
USER_VIEW = FX.CT_M3 + """
delivery_view_requested: USER
internal_artifact_also_required: true
rejected_candidates_present: true
rejected_candidates:
  - "[夹具登记事实] 被淘汰方向：把三组试穿讲成『哪一组最显瘦』——违反表达边界，已淘汰"
review_notes_present: true
review_notes: "[夹具登记事实] 审查便条：上一版有一句无依据的『很多顾客都说好穿』，已删除"
"""

# --- §14 FX-M4-DRAMATIZATION（N-47 / N-48 / AC-27）-------------------
DRAMATIZATION = FX.CT_M3 + """
request: "用一个情境把『马甲成立条件』演出来"
real_event_available: false
expression_latitude: "允许显式标注的演示场景"
probe_variant_N48_injection: "演绎稿中出现『很多顾客买回去都说好穿』这类无依据品牌事实/结果暗示"
"""

# --- §25 FX-M4-SHORT-ENTRY-METHOD（N-35 / N-36 / N-37 / AC-18）-------
SHORT_ENTRY_METHOD = FX.SCRIPT_LEGAL + """
short_entry: true
entry_note: "用户直接从 PD 进入，输入完整，未跑任何上游能力"
n35_applicable_method: "本次任务真正适用的专业方法来自 Production Director 的七维制作判断与并置检查"
n36_proposal_to_reject: "[夹具登记事实] 有人提出『为保护专业价值，要求六个 Skill 全部参与』"
n37_not_applicable_dimension: "[夹具登记事实] 本条是短快转化内容，完整叙事弧维度不适用"
"""

# --- §16.1 FX-M4-RETURN-PARSE-FAIL（N-12 / AC-14）--------------------
RETURN_PARSE_FAIL = FX.CT_M3 + """
downstream_return_raw: '{"return_id": "RETURN-X-001", "source": "CREATIVE_SCRIPT", "precise_gap": '
downstream_return_note: "[夹具登记事实] 上面这段就是下游实际返回的原文：非法 JSON，且缺必填项"
"""

# --- §16.2 FX-M4-RETURN-REJECTED（N-13 / AC-14）----------------------
RETURN_REJECTED = FX.CT_M3 + """
downstream_return_raw: '{"return_id": "RETURN-CS-002", "source": "CREATIVE_SCRIPT", "highest_damaged_layer": "内容承诺", "precise_gap": "要求把 content_promise 改成哪一件更好", "affected_objects": ["content_promise"], "proposed_disposition": "AMEND_UPSTREAM", "needs_user_decision": false}'
upstream_disposition: REJECTED
downstream_return_note: "[夹具登记事实] 该回改被上游拒绝，需要给出权威/事实/边界理由"
"""



# ----------------------------------------------------------------------
# 转写更正登记（2026-08-26，如实记录，不掩盖）
# ----------------------------------------------------------------------
# 第一次运行 FA-14…FA-21 时，上面 8 条转写**漏掉了统一能力合同 §4.3 定义的
# 部分必填语义槽**（CAMPAIGN 缺 capacity_or_owner/audience_problem 等；
# MATRIX 缺 facts_registered；PP 三例缺 facts_registered/cta_contract/
# explicit_non_promise）。后果是这几次运行在**结构性充分性闸**就被局部 Return
# 拦下，根本没有走到被测逻辑（Campaign 的 PLANNING/COMPILE 判定、Matrix 的
# 充分分支、PP 的 PRE/MIXED 推导），因此它们对 AC-07/AC-10/AC-19/AC-20
# **不提供任何信息**，既不是 PASS 也不是这些 criterion 的 FAIL。
#
# 处置（取证判据合同 §1.3）：根因已定位 = 转写把冻结夹具包的散文映射到字段时
# 漏了槽位，不是被测系统的缺陷。干预 = 按冻结夹具包 §0/§1/§5 的**既有正文**
# 把缺的槽位补齐，**不改任何一条夹具的判别变量**
# （PLAN-ONLY 仍 realization_manifest_present:false，MIXED 仍带未决缺口，
#  ASSET-LEVEL-ONLY 仍 beat_mapping_present:false，UNCONFIRMED 仍三项未确认）。
# 第一次的原始运行记录**全部保留**在 runs/attempt1/（N-30：不失败后盲目重抽、
# 不只留满意输出）。
#
# 第一次运行本身是**有效的正向证据**，只是服务于别的 criterion：
# 它证明结构性不足时输出的是**组件级 Return 且 precise_gap 指名到字段**
# （如 FA-18 的 precise_gap = "facts_registered"，不是"信息不足"），
# 服务 AC-04 / AC-06 ① / AC-19 的局部 Return 部分。
# ----------------------------------------------------------------------

# ======================================================================
# 运行清单
# ======================================================================
def attempt_matrix2():
    """FA-14…FA-33：冻结夹具包里**此前从未运行**的条目。
    每一行 = 一次正式运行；夹具与 Oracle 均在结果之前冻结。"""
    return [
        ("FA-14", "FX-M4-CAMPAIGN-UNCONFIRMED", "CAMPAIGN", "", CAMPAIGN_UNCONFIRMED,
         ["AC-07", "AC-20", "N-05", "N-40"], "§7.1"),
        ("FA-15", "FX-M4-CAMPAIGN-CONFIRMED-PACK", "CAMPAIGN", "", CAMPAIGN_CONFIRMED_PACK,
         ["AC-07", "AC-20", "N-06"], "§7.2"),
        ("FA-16", "FX-M4-CAMPAIGN-OVERRIDE-END", "CAMPAIGN", "", CAMPAIGN_OVERRIDE_END,
         ["AC-20", "N-41"], "§7.3"),
        ("FA-17", "FX-M4-CAMPAIGN-GOAL-NARROWING", "CAMPAIGN", "", CAMPAIGN_GOAL_NARROWING,
         ["AC-20", "N-33"], "§7.4"),
        ("FA-18", "FX-M4-MATRIX-SUFFICIENT", "MATRIX", "", MATRIX_SUFFICIENT,
         ["AC-19", "AC-03", "N-04", "N-38", "N-39"], "§6.1"),
        ("FA-19", "FX-M4-REALIZATION-PLAN-ONLY", "PUBLISHING_PACKAGING", "", REALIZATION_PLAN_ONLY,
         ["AC-10", "N-14"], "§5.1"),
        ("FA-20", "FX-M4-REALIZATION-MIXED", "PUBLISHING_PACKAGING", "", REALIZATION_MIXED,
         ["AC-10", "N-15"], "§5.2"),
        ("FA-21", "FX-M4-REALIZATION-ASSET-LEVEL-ONLY", "PUBLISHING_PACKAGING", "",
         REALIZATION_ASSET_LEVEL_ONLY, ["AC-10", "N-14"], "§5.4"),
        ("FA-22", "FX-M4-ASSET-WITHDRAWN", "PUBLISHING_PACKAGING", "", ASSET_WITHDRAWN,
         ["AC-25", "N-16"], "§5.5"),
        ("FA-23", "FX-M4-LOCAL-EDIT", "PRODUCTION_DIRECTOR", "", LOCAL_EDIT,
         ["AC-09", "AC-14", "AC-24", "N-11"], "§16.3"),
        ("FA-24", "FX-M4-IRRELEVANT-REFERENCE", "CONTENT_BRIEF", "", IRRELEVANT_REFERENCE,
         ["AC-11", "N-18"], "§22"),
        ("FA-25", "FX-M4-NO-PLATFORM-EVIDENCE", "PUBLISHING_PACKAGING", "", NO_PLATFORM_EVIDENCE,
         ["AC-11", "N-17"], "§21"),
        ("FA-26", "FX-M4-CTA-THREE/case_low_risk", "CONTENT_BRIEF", "", CTA_LOW_RISK,
         ["AC-28", "N-49"], "§15"),
        ("FA-27", "FX-M4-CTA-THREE/case_business_handoff", "CONTENT_BRIEF", "", CTA_BUSINESS_HANDOFF,
         ["AC-28", "N-49"], "§15"),
        ("FA-28", "FX-M4-CTA-THREE/case_high_risk", "CONTENT_BRIEF", "", CTA_HIGH_RISK,
         ["AC-28", "N-49"], "§15"),
        ("FA-29", "FX-M4-USER-VIEW", "CONTENT_BRIEF", "", USER_VIEW,
         ["AC-13", "N-23"], "§23"),
        ("FA-30", "FX-M4-DRAMATIZATION", "CREATIVE_SCRIPT", "", DRAMATIZATION,
         ["AC-27", "N-47", "N-48"], "§14"),
        ("FA-31", "FX-M4-SHORT-ENTRY-METHOD", "PRODUCTION_DIRECTOR", "", SHORT_ENTRY_METHOD,
         ["AC-18", "N-35", "N-36", "N-37"], "§25"),
        ("FA-32", "FX-M4-RETURN-PARSE-FAIL", "CONTENT_BRIEF", "", RETURN_PARSE_FAIL,
         ["AC-14", "N-12"], "§16.1"),
        ("FA-33", "FX-M4-RETURN-REJECTED", "CONTENT_BRIEF", "", RETURN_REJECTED,
         ["AC-14", "N-13"], "§16.2"),
    ]


# AC-02「两两互换」：6 个能力的**规范 payload**，各自来自该能力自己的冻结夹具。
CANONICAL_PAYLOAD = [
    ("MATRIX", "FX-M4-MATRIX-SUFFICIENT", MATRIX_SUFFICIENT),
    ("CAMPAIGN", "FX-M4-CAMPAIGN-CONFIRMED-PACK", CAMPAIGN_CONFIRMED_PACK),
    ("CONTENT_BRIEF", "FX-M4-CT-M3", FX.CT_M3),
    ("CREATIVE_SCRIPT", "FX-M4-REAL-TRADEOFF", FX.REAL_TRADEOFF),
    ("PRODUCTION_DIRECTOR", "FX-M4-SCRIPT-LEGAL", FX.SCRIPT_LEGAL),
    ("PUBLISHING_PACKAGING", "FX-M4-REALIZATION-FINAL", FX.FOOTAGE_FINAL),
]


def swap_matrix():
    """AC-02：6 个能力的**全部有序对** 30 组，非抽样。
    每组把 payload_of(src) 喂给 dst 能力，看下游是否仍正常消费。"""
    out = []
    n = 0
    for di, (dst, _dfx, _dp) in enumerate(CANONICAL_PAYLOAD):
        for si, (src, sfx, sp) in enumerate(CANONICAL_PAYLOAD):
            if si == di:
                continue
            n += 1
            out.append(("SW-%02d" % n, dst, src, sfx, sp))
    return out


# ======================================================================
# 运行
# ======================================================================
def _runner():
    c = PUB.Console()
    c.login()
    reb = json.load(open(os.path.join(EVID, "M4_DIFY_REBIND.json"), encoding="utf-8"))
    seam_app = reb["seam_app_id"]
    token = FA.ensure_api_key(c, seam_app)
    return c, seam_app, reb["bindings"], token, c.base


def _exec_one(base, token, cap, entry, payload):
    body = {
        "inputs": {
            "capability": cap,
            "entry": entry,
            "capability_call": payload,
            "professional_input": payload,
            "example_reference_requested": "NO",
        },
        "response_mode": "blocking",
        "user": "m4-closing-verification",
    }
    try:
        return FA.service_call(base, token, "/v1/workflows/run", body), None
    except Exception as e:
        return {}, str(e)[:600]


def cmd_run2():
    c, seam_app, bindings, token, base = _runner()
    os.makedirs(RUNS, exist_ok=True)
    only = set(sys.argv[2:])
    pack_sha = file_sha(PACK)
    index = []
    for aid, fx_id, cap, entry, payload, serves, sec in attempt_matrix2():
        p = os.path.join(RUNS, "%s.json" % aid)
        if only and aid not in only:
            if os.path.exists(p):
                old = json.load(open(p, encoding="utf-8"))
                index.append({"attempt_id": aid, "fixture_id": fx_id, "capability": cap,
                              "run_id": old.get("run_id", ""),
                              "status": ((old.get("raw_response") or {}).get("data") or {}).get("status", "?"),
                              "path": os.path.relpath(p, ROOT), "serves_criteria": serves})
            continue
        if os.path.exists(p) and not only:
            old = json.load(open(p, encoding="utf-8"))
            if ((old.get("raw_response") or {}).get("data") or {}).get("status") == "succeeded":
                print("[%s] %-38s 已有成功运行，保留不重跑" % (aid, fx_id))
                index.append({"attempt_id": aid, "fixture_id": fx_id, "capability": cap,
                              "run_id": old.get("run_id", ""), "status": "succeeded",
                              "path": os.path.relpath(p, ROOT), "serves_criteria": serves})
                continue
        t0 = time.time()
        res, err = _exec_one(base, token, cap, entry, payload)
        run_id = ((res.get("data") or {}).get("id")) or res.get("workflow_run_id") or ""
        rec = {
            "attempt_id": aid, "attempt_kind": "FORMAL", "fixture_id": fx_id,
            "fixture_pack_section": sec,
            "fixture_pack_sha256": pack_sha,
            "fixture_transcription_note": (
                "可运行转写：逐字取自冻结夹具包 v0.1 " + sec +
                "（含 §0 共用背景中的真实组织角色与表达边界）；只做散文→同义字段的形式变换，"
                "未新增任何夹具未提供的经营事实。"),
            "capability": cap, "entry_requested": entry or "(由确定性充分性规则推导)",
            "serves_criteria": serves, "oracle_ref": ORACLE_REF, "environment": ENVIRONMENT,
            "frozen_candidate": FROZEN_CANDIDATE,
            "seam_app_id": seam_app, "provider_bindings": bindings,
            "input_sha256": sha(payload), "input_text": payload,
            "run_id": run_id, "elapsed_s": round(time.time() - t0, 2), "error": err,
            "raw_response": res,
            "node_trace": FA.node_trace(c, seam_app, run_id) if run_id else [],
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        }
        with open(p, "w", encoding="utf-8") as fh:
            json.dump(rec, fh, ensure_ascii=False, indent=2)
        status = (res.get("data") or {}).get("status", "ERR" if err else "?")
        print("[%s] %-38s %-20s status=%-10s run_id=%s" % (aid, fx_id, cap, status, run_id or "-"))
        if err:
            print("      ERR: %s" % err[:200])
        index.append({"attempt_id": aid, "fixture_id": fx_id, "capability": cap,
                      "run_id": run_id, "status": status, "path": os.path.relpath(p, ROOT),
                      "serves_criteria": serves})
    with open(os.path.join(EVID, "M4_FORMAL_ATTEMPT_INDEX_2.json"), "w", encoding="utf-8") as fh:
        json.dump({"attempts": index, "environment": ENVIRONMENT, "oracle_ref": ORACLE_REF,
                   "frozen_candidate": FROZEN_CANDIDATE,
                   "fixture_pack_sha256": pack_sha}, fh, ensure_ascii=False, indent=2)
    print("index -> decision-chain/evidence/m4/M4_FORMAL_ATTEMPT_INDEX_2.json")
    return 0


def cmd_swap():
    """AC-02 两两互换。"""
    c, seam_app, bindings, token, base = _runner()
    swaps = os.path.join(EVID, "swaps")
    os.makedirs(swaps, exist_ok=True)
    only = set(sys.argv[2:])
    out = []
    for sid, dst, src, sfx, payload in swap_matrix():
        p = os.path.join(swaps, "%s.json" % sid)
        if only and sid not in only:
            if os.path.exists(p):
                out.append(json.load(open(p, encoding="utf-8"))["summary"])
            continue
        if os.path.exists(p) and not only:
            old = json.load(open(p, encoding="utf-8"))
            if old["summary"].get("status") == "succeeded":
                out.append(old["summary"])
                print("[%s] 已有运行，保留" % sid)
                continue
        res, err = _exec_one(base, token, dst, "", payload)
        d = (res.get("data") or {})
        o = d.get("outputs") or {}
        art = o.get("artifact") or ""
        ud = o.get("user_delivery") or ""
        try:
            rj = json.loads(o.get("returns_json") or "[]")
        except Exception:
            rj = []
        summary = {
            "swap_id": sid, "dst_capability": dst, "src_capability": src,
            "src_fixture": sfx, "run_id": d.get("id", ""),
            "status": d.get("status", "ERR" if err else "?"),
            "error": err,
            "blocked_or_insufficient": ("INSUFFICIENT" in art) or ("BLOCKED" in art)
                                       or ("BLOCKED" in ud[:80].upper()) or bool(rj),
            "returns_count": len(rj),
            "artifact_sha256": sha(art), "artifact_len": len(art),
            "user_delivery_len": len(ud),
        }
        with open(p, "w", encoding="utf-8") as fh:
            json.dump({"summary": summary, "raw_response": res,
                       "input_sha256": sha(payload), "input_text": payload,
                       "oracle_ref": ORACLE_REF, "environment": ENVIRONMENT,
                       "frozen_candidate": FROZEN_CANDIDATE,
                       "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z")},
                      fh, ensure_ascii=False, indent=2)
        out.append(summary)
        print("[%s] %-20s <- %-20s status=%-10s 阻断/不足=%s Return=%d" % (
            sid, dst, src, summary["status"], summary["blocked_or_insufficient"],
            summary["returns_count"]))
    with open(os.path.join(EVID, "M4_AC02_SWAP_RESULTS.json"), "w", encoding="utf-8") as fh:
        json.dump({"swaps": out, "ordered_pairs_total": 30, "sampling": "无抽样，6 能力全部有序对",
                   "oracle_ref": ORACLE_REF, "environment": ENVIRONMENT,
                   "frozen_candidate": FROZEN_CANDIDATE}, fh, ensure_ascii=False, indent=2)
    print("-> decision-chain/evidence/m4/M4_AC02_SWAP_RESULTS.json")
    return 0


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "run2"
    sys.exit({"run2": cmd_run2, "swap": cmd_swap}.get(cmd, cmd_run2)())
