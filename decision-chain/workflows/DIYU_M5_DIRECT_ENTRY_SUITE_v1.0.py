#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""M5 合法短入口套件 · DE-01..10（目录 M5-DIRECT-ENTRY-CATALOG-v1.0）。

**判据写死在本文件里，且必须在任何一次正式运行之前提交。** 看到结果之后再改判据，
本次只算探索，不产生正式 PASS（宪法 A2「判据事件必须早于结果事件」）。

短入口要证的不是「能跑通」，而是三件更难的事：
  1. **不暗跑**：进入某个能力时，不偷偷补跑它的上游。用两条独立证据交叉验证——
     接缝自报的 capabilities_skipped，加上按时间窗直接查 Dify 运行台账，
     核对本用例窗口内**实际被调用过的应用集合**。台账是客观的，自报不是。
  2. **不越界**：目标、事实、权限、CTA 不因为「走了近路」就放松。
  3. **不丢适用专业方法**：直达不等于降级，该用的专业判断仍然要用。

入口数量是**本次正式验收的有限库存**，不是产品永久语义。未来合法入口变化须版本化。
"""
import importlib.util, json, os, subprocess, sys, time

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
def _load(n, p):
    s = importlib.util.spec_from_file_location(n, p); m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m); return m
FS = _load("fs", os.path.join(ROOT, "decision-chain", "workflows", "DIYU_M5_FULL_STORY_v0.1.py"))
RT = FS.RT

# 六个能力应用 id → 名字，用于按时间窗核对「谁真的被调用过」
APP_ROLE = {v: k for k, v in RT.CAPABILITY_APPS.items()}
APP_ROLE[RT.SEAM_APP] = "SEAM"
APP_ROLE[RT.M3_APP] = "M3"
APP_ROLE[RT.HOP_ADAPTER_APP] = "M5_HOP_ADAPTER"
APP_ROLE[RT.CANVAS_APP] = "CANVAS"


def runs_in_window(t0, t1):
    """直接查 Dify 运行台账：这段时间里到底哪些应用真的跑过。
    这是**客观**证据，用来交叉核对接缝的自报，不采信任何一方的单方面声明。"""
    sql = ("SELECT app_id, count(*) FROM workflow_runs "
           "WHERE created_at > '%s' AND created_at <= '%s' GROUP BY app_id;" % (t0, t1))
    p = subprocess.run(["docker", "exec", "-i", "docker-db_postgres-1", "psql", "-U", "postgres",
                        "-d", "dify", "-t", "-A", "-F", "|", "-c", sql],
                       capture_output=True, text=True, timeout=60)
    out = {}
    for line in (p.stdout or "").strip().splitlines():
        if "|" not in line:
            continue
        app, n = line.split("|", 1)
        out[APP_ROLE.get(app.strip(), app.strip())] = int(n)
    return out


def assert_no_concurrent_runs():
    """本套件的「不暗跑」证据靠按时间窗查 Dify 运行台账。
    只要同时有**任何**别的运行在跑，窗口里就会混进不属于本用例的调用，
    这条证据当场作废。所以开跑前先确认全场安静，不安静就拒绝开始——
    宁可不跑，也不要产出一条看起来成立、实则被污染的证据。"""
    p = subprocess.run(["docker", "exec", "-i", "docker-db_postgres-1", "psql", "-U", "postgres",
                        "-d", "dify", "-t", "-A", "-F", "|", "-c",
                        "SELECT app_id, count(*) FROM workflow_runs "
                        "WHERE status='running' GROUP BY app_id;"],
                       capture_output=True, text=True, timeout=60)
    rows = [l for l in (p.stdout or "").strip().splitlines() if l.strip()]
    if rows:
        names = [APP_ROLE.get(l.split("|")[0].strip(), l.split("|")[0].strip()) for l in rows]
        raise SystemExit("拒绝开跑：Dify 当前有运行中的工作流 %s。"
                         "并发会污染时间窗台账，使「不暗跑」证据失效。" % names)


def db_now():
    p = subprocess.run(["docker", "exec", "-i", "docker-db_postgres-1", "psql", "-U", "postgres",
                        "-d", "dify", "-t", "-A", "-c",
                        "SELECT to_char(now(),'YYYY-MM-DD HH24:MI:SS.US');"],
                       capture_output=True, text=True, timeout=60)
    return p.stdout.strip()


# ================================================================ 直达输入
# 全部取自已登记事实夹具的原文或其最小截断。**不补写夹具没有的经营事实。**
# 写成反引号形状是因为 M4 外壳解析器的 YAML 分支排除引号值（见 M5-DIAG-007）。

DIRECT = {}

DIRECT["MATRIX"] = """`applicability_reason`: 序里集第一阶段有四个可出镜主体（林序、周宁、苏禾、陈晚），需要判断谁承担什么、是否真的分工，而不是同一内容换四种说法
`subject_and_account_scope`: 序里集 XULI SELECT 品牌，四个候选账号主体：创始人林序、买手周宁、店长苏禾、门店服务陈晚
objective:
  `primary_goal`: 判断四个主体是否构成真实分工，以及本阶段谁应该主讲
  goal_family: LONG_TERM_VALUE
`facts_registered`: A01 林序 9 分钟经营取舍录音（已确认，有限）；B01 周宁六款商品选品比较表与 12 分钟口述（已确认，充分）；C01 苏禾三组内部演示试穿记录（已确认，充分）；D01 陈晚一组可匿名门店问题记录（已确认，有限）
`expression_boundary`: 内部试穿人员可以出镜但不得包装成现实顾客案例；不得虚构林序与商品团队发生争执；不得把商品组合判断写成通用衣橱公式
`capacity_or_owner`: 林序一次 30 分钟访谈；周宁两次各 1 小时拍摄；苏禾一次 3 小时拍摄加一次 30 分钟补录；陈晚一次 30 分钟事实确认
platform: NOT_LOCKED
"""

DIRECT["CAMPAIGN"] = """objective:
  `primary_goal`: 把初秋通勤衣橱第一阶段的七天做成一个可执行的经营任务，而不是四个账号各发各的
  goal_family: LONG_TERM_VALUE
`deadline_or_stage_boundary`: 七天第一阶段；资源快照日期 2026-08-20；是否扩展为完整四周计划待后续确认，本轮不预先决定
`audience_problem`: 顾客上班需要正式，但下班接孩子时不想显得过于用力；同时面对相似商品不知道先比较什么
`facts_registered`: 六款登记商品 XQ-2501 至 XQ-2506 及其材质、版型与库存快照；四组已确认素材 A01/B01/C01/D01；媒体资产 IMG-P01、DOC-B01、AUD-A01、VID-C01、IMG-C02、NOTE-D01、BROLL-S01
`capacity_or_owner`: 1 名拍摄与现场执行、1 名剪辑可兼字幕封面；七天内最多 3 条主要短视频加 2 条轻量图文或短切片；不支持为四个账号分别制作完整高规格视频；无外部演员、场地和大型制作预算
`explicit_non_promise`: 本轮无折扣促销清仓任务；库存数字不得解释为库存压力或稀缺理由；最终发布平台、正式预约入口、接待人、每日接待能力均未确认
platform: NOT_LOCKED
"""

DIRECT["CONTENT_BRIEF"] = """objective:
  `primary_goal`: 做一条内容，让顾客知道判断一件廓形西装是否适合自己要先看什么、先排除什么
  goal_family: LONG_TERM_VALUE
`audience_problem`: 面对两件看起来差不多的西装，顾客不知道先比较什么、先排除什么，只能靠上身那一瞬间的感觉
`expected_change`: 看完后能自己说出两三个可以先看的位置，并且知道最后一步必须本人试穿
`content_promise`: 说明廓形西装 XQ-2501 承担什么衣橱任务，以及哪些结论必须留到本人试穿
`facts_registered`: XQ-2501 暮灰廓形西装已登记材质与版型（微宽松 H 形、轻薄肩垫、单排一粒扣、长度过臀、全里布）；B01 记录未选择明显收腰、肩部更强调造型的候选，理由是当前款更适合叠穿衬衫和针织马甲
`expression_subject_and_boundary`: 周宁主讲，基于选品比较表；不得推断未登记的防水防风抗皱保暖显瘦耐磨和洗护性能；不得把商品组合判断写成对所有顾客通用的衣橱公式
`explicit_non_promise`: 不承诺该商品适合所有身材；肩部结构和长度仍需试穿
`cta_level`: LOW_RISK_INTERACTION
platform: NOT_LOCKED
"""

# DE-06 要进锦标赛：接缝的入口解析要求输入里出现至少三个结构轴的显式差异标注，
# 且不得出现 accepted_direction。五个结构轴是 M4 冻结的，不是本文件发明的。
DIRECT["CREATIVE_TOURNAMENT"] = """objective:
  `primary_goal`: 同一个判断，本轮存在真实的表达取舍，需要先比较方向再定稿
  goal_family: LONG_TERM_VALUE
`expected_change`: 看完后能自己说出两三个可以先看的位置，并且知道最后一步必须本人试穿
`content_promise`: 说明廓形西装承担什么衣橱任务，以及哪些结论必须留到本人试穿
`expression_subject`: 周宁，买手，可参与两次各 1 小时集中拍摄并完成商品事实确认
`content_origin_mode`: 已登记素材剪辑加原创口播：DOC-B01 选品比较表、IMG-P01 商品图 36 张、BROLL-S01 门店空镜
`facts_registered`: XQ-2501 已登记材质与版型；B01 未选择收腰更明显候选的比较记录；C01 苏禾三组试穿观察
`real_tradeoff_axes`: 本轮在下列结构轴上存在真实取舍——核心矛盾（是讲商品还是讲判断方法）、叙事发动机（用一次真实排除做发动机还是用顾客问题做发动机）、信息释放顺序（先给结论还是先给比较过程）、视觉前提（先给商品特写还是先给门店场景）
`explicit_non_promise`: 不承诺适合所有身材；不推断未登记性能
`cta_level`: LOW_RISK_INTERACTION
platform: NOT_LOCKED
"""

DIRECT["CREATIVE_SCRIPT"] = """objective:
  `primary_goal`: 把已经选定的表达方向写成可拍的脚本
  goal_family: LONG_TERM_VALUE
`accepted_direction`: 用一次真实的选品排除做叙事发动机——先讲为什么没选那件收腰更明显的，再回到怎么判断
`expected_change`: 看完后能自己说出两三个可以先看的位置，并且知道最后一步必须本人试穿
`content_promise`: 说明廓形西装承担什么衣橱任务，以及哪些结论必须留到本人试穿
`expression_subject`: 周宁，买手，可参与两次各 1 小时集中拍摄
`content_origin_mode`: 已登记素材剪辑加原创口播：DOC-B01 选品比较表、IMG-P01 商品图、BROLL-S01 门店空镜
`facts_registered`: XQ-2501 已登记材质与版型；B01 未选择收腰更明显候选的比较记录及其理由
`explicit_non_promise`: 不承诺适合所有身材；不推断未登记性能；不虚构与商品团队的争执
`cta_level`: LOW_RISK_INTERACTION
platform: NOT_LOCKED
"""

DIRECT["PRODUCTION_DIRECTOR"] = """`script_or_equivalent_beats`: 节拍一 拿出两件看起来差不多的西装，说明本轮没选哪一件；节拍二 用肩部结构、袖长、衣长、叠穿空间四个位置说明比较方法；节拍三 明确肩部结构和长度仍需本人试穿，判断权交回观众
`content_origin_mode`: 已登记素材剪辑加原创口播：DOC-B01 选品比较表、IMG-P01 商品图 36 张、BROLL-S01 门店空镜
`production_profile`: 1 名拍摄与现场执行、1 名剪辑可兼字幕与封面；周宁可参与两次各 1 小时集中拍摄；七天内最多 3 条主要短视频加 2 条轻量图文；不支持为四个账号分别制作完整高规格视频；无外部演员、场地和大型制作预算
`time_window`: 七天第一阶段；资源快照日期 2026-08-20；企业内部单条事实确认预计 24 小时内完成
`content_promise`: 说明廓形西装承担什么衣橱任务，以及哪些结论必须留到本人试穿
`explicit_non_promise`: 无额外预算用于外部演员场地和大型制作
platform: NOT_LOCKED
"""

DIRECT["PUBLISHING_PACKAGING"] = """`content_body_or_beats`: 节拍一 拿出两件看起来差不多的西装，说明本轮没选哪一件；节拍二 用肩部结构、袖长、衣长、叠穿空间四个位置说明比较方法；节拍三 明确肩部结构和长度仍需本人试穿
`content_promise`: 说明廓形西装承担什么衣橱任务，以及哪些结论必须留到本人试穿
`explicit_non_promise`: 不承诺顾客一定少买；不承诺提高衣橱利用率的具体比例；不得声称陈列调整后提高了销售；不发布新的预约政策和服务承诺
`facts_registered`: XQ-2501 已登记材质与版型；B01 未选择收腰更明显候选的比较记录；C01 三组内部演示试穿记录
`cta_contract`: 本轮正式预约入口、具体接待人、服务时效和每日容量仍未确认，因此只能做低风险互动，不得承诺预约、到店或购买
`cta_level`: LOW_RISK_INTERACTION
`asset_publish_permission`: IMG-P01 与 DOC-B01 已确认，周宁主用；VID-C01 苏禾主用、周宁可引用试穿结果；内部试穿人员可以出镜但不得包装成现实顾客案例；其他账号引用需标明来源
platform: NOT_LOCKED
"""

# 缺一项必填的输入，用于 DE-10：先触发组件级 Return，再补齐后**只重入该节点**
DIRECT["PUBLISHING_MISSING_PERMISSION"] = "\n".join(
    l for l in DIRECT["PUBLISHING_PACKAGING"].strip().splitlines()
    if not l.startswith("`asset_publish_permission`"))


# ================================================================ 冻结判据
# 每条判据都是**可确定性判定**的：要么查台账，要么查接缝返回的结构化字段。
# 「产出好不好」不在这里判——那属于业务判断，交盲评。
CASES = [
    {"id": "DE-01", "name": "Matrix-only 账号定位/诊断", "capability": "MATRIX",
     "call": DIRECT["MATRIX"],
     "expect": {"apps_allowed": {"SEAM", "MATRIX"},
                "entry_resolved": "ENTRY-01",
                "must_not_run": {"CONTENT_BRIEF", "CREATIVE_SCRIPT", "PRODUCTION_DIRECTOR",
                                 "PUBLISHING_PACKAGING", "CAMPAIGN", "M3"},
                "oracle": "只返回 Matrix 专业判断或组件级补充请求；不启动内容生产"}},
    {"id": "DE-02", "name": "Campaign-only 策划", "capability": "CAMPAIGN",
     "call": DIRECT["CAMPAIGN"],
     "expect": {"apps_allowed": {"SEAM", "CAMPAIGN"},
                "entry_resolved": "ENTRY-02",
                "must_not_run": {"MATRIX", "M3", "CONTENT_BRIEF", "CREATIVE_SCRIPT",
                                 "PRODUCTION_DIRECTOR", "PUBLISHING_PACKAGING"},
                "oracle": "输出策划或合法 Content Task 接缝；不强制 Matrix/M3/全链"}},
    {"id": "DE-03", "name": "M3 运营判断-only", "capability": None,
     "expect": {"apps_allowed": {"M3"},
                "must_not_run": {"SEAM", "MATRIX", "CAMPAIGN", "CONTENT_BRIEF",
                                 "CREATIVE_SCRIPT", "PRODUCTION_DIRECTOR", "PUBLISHING_PACKAGING"},
                "oracle": "可停在运营判断，不伪造内容任务或暗启生产链"}},
    {"id": "DE-04", "name": "M3 Content Task 到 Content Brief", "capability": "CONTENT_BRIEF",
     "from_m3": True,
     "expect": {"apps_allowed": {"M3", "M5_HOP_ADAPTER", "SEAM", "CONTENT_BRIEF"},
                "entry_resolved": "ENTRY-03",
                "must_not_run": {"MATRIX", "CAMPAIGN", "CREATIVE_SCRIPT",
                                 "PRODUCTION_DIRECTOR", "PUBLISHING_PACKAGING"},
                "oracle": "以统一业务语义进入 Brief；不重跑 M1/Matrix/Campaign"}},
    {"id": "DE-05", "name": "Direct Content Brief", "capability": "CONTENT_BRIEF",
     "call": DIRECT["CONTENT_BRIEF"],
     "expect": {"apps_allowed": {"SEAM", "CONTENT_BRIEF"},
                "entry_resolved": "ENTRY-03",
                "must_not_run": {"M3", "MATRIX", "CAMPAIGN", "CREATIVE_SCRIPT",
                                 "PRODUCTION_DIRECTOR", "PUBLISHING_PACKAGING"},
                "oracle": "直达 Brief；单条主目标收敛；保留事实、权限和表达裁量"}},
    {"id": "DE-06", "name": "Direct Creative Tournament", "capability": "CREATIVE_SCRIPT",
     "call": DIRECT["CREATIVE_TOURNAMENT"],
     "expect": {"apps_allowed": {"SEAM", "CREATIVE_SCRIPT"},
                "entry_resolved": "ENTRY-04", "run_mode": "TOURNAMENT_ONLY",
                "must_not_run": {"M3", "MATRIX", "CAMPAIGN", "CONTENT_BRIEF",
                                 "PRODUCTION_DIRECTOR", "PUBLISHING_PACKAGING"},
                "oracle": "复用唯一锦标赛；候选实质不同；不固定候选数"}},
    {"id": "DE-07", "name": "Direct Creative Script", "capability": "CREATIVE_SCRIPT",
     "call": DIRECT["CREATIVE_SCRIPT"],
     "expect": {"apps_allowed": {"SEAM", "CREATIVE_SCRIPT"},
                "entry_resolved": "ENTRY-05", "run_mode": "SELECTED_DIRECTION_TO_SCRIPT",
                "must_not_run": {"M3", "MATRIX", "CAMPAIGN", "CONTENT_BRIEF",
                                 "PRODUCTION_DIRECTOR", "PUBLISHING_PACKAGING"},
                "oracle": "直达脚本；不强制重赛、物理 Brief 或重复确认"}},
    {"id": "DE-08", "name": "Direct Production Director", "capability": "PRODUCTION_DIRECTOR",
     "call": DIRECT["PRODUCTION_DIRECTOR"],
     "expect": {"apps_allowed": {"SEAM", "PRODUCTION_DIRECTOR"},
                "entry_resolved": "ENTRY-06",
                "must_not_run": {"M3", "MATRIX", "CAMPAIGN", "CONTENT_BRIEF",
                                 "CREATIVE_SCRIPT", "PUBLISHING_PACKAGING"},
                "oracle": "直达制作计划/manifest；不重跑运营、Brief 或脚本"}},
    {"id": "DE-09", "name": "Direct Publishing & Packaging", "capability": "PUBLISHING_PACKAGING",
     "call": DIRECT["PUBLISHING_PACKAGING"],
     "expect": {"apps_allowed": {"SEAM", "PUBLISHING_PACKAGING"},
                "entry_resolved": "ENTRY-07",
                "must_not_run": {"M3", "MATRIX", "CAMPAIGN", "CONTENT_BRIEF",
                                 "CREATIVE_SCRIPT", "PRODUCTION_DIRECTOR"},
                "oracle": "直达包装；不补跑上游；承诺不超兑现和权限"}},
    {"id": "DE-10", "name": "局部 Return 后合法重入", "capability": "PUBLISHING_PACKAGING",
     "two_phase": True,
     "call_phase1": DIRECT["PUBLISHING_MISSING_PERMISSION"],
     "call_phase2": DIRECT["PUBLISHING_PACKAGING"],
     "expect": {"phase1_component_return": True,
                "phase1_is_task_terminal_state": "false",
                "phase1_precise_gap_contains": "asset_publish_permission",
                "phase1_fabricated_artifact_produced": "false",
                "phase2_delivered": True,
                "apps_allowed": {"SEAM", "PUBLISHING_PACKAGING"},
                "must_not_run": {"M3", "MATRIX", "CAMPAIGN", "CONTENT_BRIEF",
                                 "CREATIVE_SCRIPT", "PRODUCTION_DIRECTOR"},
                "oracle": "只重入最高失效节点及受影响下游；不把组件 Return 变成全任务硬停或全链重跑"}},
]


def _seam_field(r, key):
    try:
        return json.loads((r.get("seam_trace_json") or "{}")).get(key)
    except Exception:
        return None


def capability_run_outputs(capability, since):
    """取**能力应用自己**那一次运行的输出。

    这一条踩过三次坑，写死在这里：is_task_terminal_state /
    fabricated_artifact_produced / downstream_invoked / user_delivery_leaks /
    single_question / missing 这些字段挂在**能力应用**的运行上，
    **不在接缝的返回里**。从接缝返回读会全部读到 null——
    那不是「缺陷」，是观测读错了地方，会同时制造假 FAIL 和假 PASS。
    """
    app = RT.CAPABILITY_APPS.get(capability)
    if not app:
        return {}
    q = ("SELECT outputs FROM workflow_runs WHERE app_id='%s' AND created_at > '%s' "
         "ORDER BY created_at DESC LIMIT 1;" % (app, since))
    p = subprocess.run(["docker", "exec", "-i", "docker-db_postgres-1", "psql", "-U", "postgres",
                        "-d", "dify", "-t", "-A", "-c", q],
                       capture_output=True, text=True, timeout=60)
    try:
        return json.loads((p.stdout or "").strip())
    except Exception:
        return {}


def _binding(r, key):
    try:
        return json.loads(r.get("binding_json") or "{}").get(key)
    except Exception:
        return None


def _returns(r):
    try:
        return json.loads(((r.get("outputs") or {}).get("returns_json")) or "[]")
    except Exception:
        return []


def run_case(rt, case, facts, m3_judgment_cache):
    t0 = db_now()
    rec = {"id": case["id"], "name": case["name"], "oracle": case["expect"]["oracle"],
           "window_start": t0}

    if case["id"] == "DE-03":
        m3 = rt.m3_operate(account_context=m3_judgment_cache["account_context"],
                           user_request="这周我们不做内容，只想让你判断这一轮该怎么走、"
                                        "以及要不要减量。给判断就行，不用给内容任务。",
                           loaded_references=m3_judgment_cache["refs"])
        rec["m3_run_id"] = m3["run_id"]
        rec["m3_gate_status"] = (m3["outputs"] or {}).get("gate_status")
        rec["judgment_chars"] = len((m3["outputs"] or {}).get("operating_judgment") or "")
        rec["attempts"] = m3.get("attempts")
    elif case.get("from_m3"):
        h = rt.hop("CONTENT_BRIEF", m3_judgment=m3_judgment_cache["judgment"],
                   registered_facts=facts,
                   account_context=m3_judgment_cache["account_context"])
        ho = h["outputs"] or {}
        rec["hop_gaps"] = ho.get("extraction_gaps_text")
        rec["hop_source_map"] = ho.get("source_map_json")
        r = rt.seam("CONTENT_BRIEF", capability_call=ho.get("capability_call") or "",
                    professional_input=ho.get("professional_input") or "")
        rec.update(_seam_record(r))
    elif case.get("two_phase"):
        since1 = db_now()
        r1 = rt.seam(case["capability"], capability_call=case["call_phase1"],
                     professional_input="")
        rets = _returns(r1)
        # 这几个字段只有能力应用自己有，必须从它的运行行读
        o1 = capability_run_outputs(case["capability"], since1)
        rec["phase1"] = {"business_delivery_outcome": r1["business_delivery_outcome"],
                         "component_return": RT.is_component_return(r1),
                         "is_task_terminal_state": o1.get("is_task_terminal_state"),
                         "fabricated_artifact_produced": o1.get("fabricated_artifact_produced"),
                         "downstream_invoked": o1.get("downstream_invoked"),
                         "triggers_downstream_invalidation": o1.get("triggers_downstream_invalidation"),
                         "branch_result": o1.get("branch_result"),
                         "missing": o1.get("missing"),
                         "user_delivery_leaks": o1.get("user_delivery_leaks"),
                         "precise_gap": (rets[0].get("precise_gap") if rets else None),
                         "highest_damaged_layer": (rets[0].get("highest_damaged_layer") if rets else None),
                         "single_question": o1.get("single_question"),
                         "capability_run_fields_seen": sorted(o1)[:14],
                         "run_id": r1["run_id"]}
        r2 = rt.seam(case["capability"], capability_call=case["call_phase2"],
                     professional_input="")
        rec["phase2"] = _seam_record(r2)
    else:
        r = rt.seam(case["capability"], capability_call=case["call"], professional_input="")
        rec.update(_seam_record(r))

    rec["window_end"] = db_now()
    rec["apps_actually_run"] = runs_in_window(t0, rec["window_end"])
    return rec


def _seam_record(r):
    o = r.get("outputs") or {}
    return {"business_delivery_outcome": r["business_delivery_outcome"],
            "delivered": RT.delivered(r),
            "component_return": RT.is_component_return(r),
            "user_delivery_chars": len(r.get("user_delivery") or ""),
            "artifact_chars": len(r.get("artifact") or ""),
            "capabilities_skipped": o.get("capabilities_skipped"),
            # 接缝自报的键名是 entry / run_mode（现场读已发布输出确认，不是猜）
            "entry_resolved": _seam_field(r, "entry"),
            "run_mode": _seam_field(r, "run_mode"),
            "entry_derivation": _seam_field(r, "entry_derivation"),
            # 接缝自己就报「有没有自动补跑上游」——这是不暗跑的**直接自报**，
            # 与时间窗台账互为独立证据；两条都要，只信一条不够。
            "upstream_auto_invoked": _seam_field(r, "upstream_auto_invoked"),
            "upstream_auto_invoked_note": _seam_field(r, "upstream_auto_invoked_note"),
            "capabilities_skipped_declared": _seam_field(
                r, "capabilities_skipped_because_not_applicable_or_equivalent_input_satisfied"),
            "source_skill_path": _binding(r, "source_skill_path"),
            "source_skill_sha256": _binding(r, "source_skill_sha256"),
            "run_id": r["run_id"], "attempts": r.get("attempts"),
            "seam_trace_json": r.get("seam_trace_json")}


def judge(case, rec):
    """按**冻结判据**判定。只判可确定性判定的项；产出质量不在此判。"""
    e = case["expect"]; fails = []
    ran = set(rec.get("apps_actually_run") or {})
    for forbidden in e.get("must_not_run", set()):
        if forbidden in ran:
            fails.append("暗跑：本用例窗口内实际调用了 %s" % forbidden)
    extra = ran - set(e.get("apps_allowed", set()))
    if extra:
        fails.append("窗口内出现未预期的应用调用：%s" % ", ".join(sorted(extra)))
    ua = rec.get("upstream_auto_invoked")
    if ua not in (None, False, "false", "False", "", [], {}):
        fails.append("接缝自报自动补跑了上游：%r（%s）"
                     % (ua, rec.get("upstream_auto_invoked_note")))
    if e.get("entry_resolved") and rec.get("entry_resolved") != e["entry_resolved"]:
        fails.append("entry 期望 %s 实得 %s" % (e["entry_resolved"], rec.get("entry_resolved")))
    if e.get("run_mode") and rec.get("run_mode") != e["run_mode"]:
        fails.append("run_mode 期望 %s 实得 %s" % (e["run_mode"], rec.get("run_mode")))
    if case["id"] == "DE-03":
        if not rec.get("judgment_chars"):
            fails.append("M3 未产出运营判断")
    elif case.get("two_phase"):
        p1 = rec.get("phase1") or {}; p2 = rec.get("phase2") or {}
        if not p1.get("component_return"):
            fails.append("phase1 未触发组件级 Return")
        if str(p1.get("is_task_terminal_state")).lower() != "false":
            fails.append("phase1 把组件 Return 变成了整任务终态")
        if str(p1.get("fabricated_artifact_produced")).lower() != "false":
            fails.append("phase1 产出了编造产物")
        if e["phase1_precise_gap_contains"] not in str(p1.get("precise_gap") or ""):
            fails.append("phase1 缺口未精确指向 %s，实得 %s"
                         % (e["phase1_precise_gap_contains"], p1.get("precise_gap")))
        if not p2.get("delivered"):
            fails.append("phase2 补齐后仍未交付：%s" % p2.get("business_delivery_outcome"))
    else:
        if not rec.get("delivered") and not rec.get("component_return"):
            fails.append("既未交付也未给出组件级 Return，业务结果 %s"
                         % rec.get("business_delivery_outcome"))
    return ("PASS" if not fails else "FAIL"), fails


def main():
    assert_no_concurrent_runs()
    rt = RT.Runtime()
    facts = FS.registered_facts()
    boot = FS.bootstrap("de" + (sys.argv[1] if len(sys.argv) > 1 else "a"))
    acct_text, _ = FS.projection_text(boot)
    m3_judgment_cache = {"account_context": acct_text, "judgment": "", "refs": "",
                         "refs_sha256": ""}

    # DE-04 需要一份真实的 M3 判断作上游。先跑一次并缓存，避免每个用例重复跑 M3。
    # 参考资料信封走**唯一** canonical builder。以前这里传的是裸夹具正文，
    # M3 因为没有清单而拒绝引用专业方法，短入口拿到的 M3 和完整主故事不是同一个。
    refs = FS.m3_loaded_references(facts)
    m3_judgment_cache["refs"] = refs
    m3_judgment_cache["refs_sha256"] = FS.refs_sha256(refs)
    m3 = rt.m3_operate(account_context=acct_text,
                       user_request="这周想出一条内容，验证顾客能不能自己判断哪件衣服适合自己。",
                       loaded_references=refs)
    m3_judgment_cache["judgment"] = (m3["outputs"] or {}).get("operating_judgment") or ""
    print("m3 seed judgment chars=%d run=%s" % (len(m3_judgment_cache["judgment"]), m3["run_id"]),
          flush=True)

    results = []
    only = os.environ.get("DE_ONLY")
    for case in CASES:
        if only and case["id"] not in only.split(","):
            continue
        print("\n>>> %s %s" % (case["id"], case["name"]), flush=True)
        rec = run_case(rt, case, facts, m3_judgment_cache)
        verdict, fails = judge(case, rec)
        rec["verdict"] = verdict
        rec["failures"] = fails
        results.append(rec)
        print("    %-4s apps_run=%s" % (verdict, rec.get("apps_actually_run")), flush=True)
        for f in fails:
            print("    ! %s" % f, flush=True)

    out = os.path.join(ROOT, "decision-chain", "evidence", "m5",
                       "DIRECT_ENTRY_SUITE_%s.json" % boot["tag"])
    with open(out, "w", encoding="utf-8") as f:
        json.dump({"catalog_id": "M5-DIRECT-ENTRY-CATALOG-v1.0", "boot": boot,
                   "results": results}, f, ensure_ascii=False, indent=2)
    npass = sum(1 for r in results if r["verdict"] == "PASS")
    print("\n=== DE 套件 %d/%d PASS ===" % (npass, len(results)), flush=True)
    print("SAVED", out, flush=True)


if __name__ == "__main__":
    main()
