#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""M4 确定性节点探针 v0.1

task_id: V1-M4-CAPABILITY-SEAMS-RUNTIME-INTEGRATION-001

**这个脚本证明什么、不证明什么**

证明：M4 后继 DSL 里**确定性代码节点**的实际行为，与冻结夹具包
      `V1_M4_SEAM_FIXTURE_PACK_v0.1.md` 的判据一致。
      被测代码**直接从已生成的 DSL 里取出并执行**，不是复制品。

不证明：Runtime 保真、LLM 专业行为、七入口在真实 Dify 中可达、Founder 验收。
      那些必须由真实 Dify run_id 绑定的 Formal Attempt 产生。
      本脚本的结论等级是 `DETERMINISTIC_NODE_VERIFIED`，**不是** `RUNTIME_VERIFIED`。

判据来源独立性（E12）：期望值来自**冻结夹具包的判据段**，
      由人先写、与被测代码不共享任何过滤逻辑。

用法：
  python3 decision-chain/workflows/DIYU_M4_DETERMINISTIC_PROBE_v0.1.py
"""

import json
import os
import sys
import types

import yaml

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
DC_WF = os.path.join(ROOT, "decision-chain", "workflows")
CP_WF = os.path.join(ROOT, "content-production", "workflows")

APPS = {
    "MATRIX": os.path.join(DC_WF, "DIYU_M4_TOOL_MATRIX_v1_3_TEST.yml"),
    "CAMPAIGN": os.path.join(DC_WF, "DIYU_M4_TOOL_CAMPAIGN_v1_3_TEST.yml"),
    "CONTENT_BRIEF": os.path.join(DC_WF, "DIYU_M4_TOOL_CONTENT_BRIEF_v1_3_TEST.yml"),
    "CREATIVE_SCRIPT": os.path.join(CP_WF, "DIYU_M4_TOOL_CREATIVE_SCRIPT_v1_3_TEST.yml"),
    "PRODUCTION_DIRECTOR": os.path.join(CP_WF, "DIYU_M4_TOOL_PRODUCTION_DIRECTOR_v1_3_TEST.yml"),
    "PUBLISHING_PACKAGING": os.path.join(CP_WF, "DIYU_M4_TOOL_PUBLISHING_PACKAGING_v1_3_TEST.yml"),
}
SEAM = os.path.join(DC_WF, "DIYU_M4_CAPABILITY_SEAM_v1_3_TEST.yml")
CANVAS = os.path.join(DC_WF, "DIYU_M4_FOUNDER_CANVAS_v1_3_TEST.yml")


def load_node_code(path, node_id, preload=None):
    """从已生成的 DSL 里取出代码节点正文并编译成可调用的 main()。
    被测对象就是将要导入 Dify 的那份字节。

    preload：Dify 代码节点沙箱预置在全局里的模块。M1 已落地的 v1_state 正文里
    没有 `import json` 却直接用 `json.dumps` —— 这是 M1 原文的既有写法，
    在真实 Dify 里可运行（该 Chatflow 已发布且 Founder 已验收）。本地探针不在
    Dify 沙箱里，必须把同名模块补进命名空间，才能跑同一份字节；这是复现运行环境，
    不是修改被测代码。"""
    with open(path, encoding="utf-8") as fh:
        d = yaml.safe_load(fh)
    nodes = {n["id"]: n for n in d["workflow"]["graph"]["nodes"]}
    code = nodes[node_id]["data"]["code"]
    mod = types.ModuleType("dsl_%s_%s" % (os.path.basename(path), node_id))
    if preload:
        mod.__dict__.update(preload)
    exec(compile(code, "<%s:%s>" % (os.path.basename(path), node_id), "exec"), mod.__dict__)
    return mod.main


RESULTS = []


def check(probe_id, name, ok, detail):
    RESULTS.append({"probe": probe_id, "name": name, "result": "PASS" if ok else "FAIL",
                    "detail": detail})


# ==========================================================================
# 冻结夹具（与 V1_M4_SEAM_FIXTURE_PACK_v0.1.md 逐条对应）
# ==========================================================================

CT_M3 = """
provenance:
  source_kind: M3_OPERATION
  confirmation_state: CONFIRMED_BY_USER
objective:
  primary_goal: 让目标顾客形成分层判断，并愿意继续听这个账号的判断
  goal_family: LONG_TERM_VALUE
audience_problem: 已经有几件通勤外套的顾客，早上仍然要花十几分钟才决定穿什么
expected_change: 她能说出自己卡住的不是衣服不够，而是层数与场合没分开
content_promise: 给出一个可以在自己衣橱里直接照做的分层判断
expression_subject_and_boundary: 苏禾；允许显式标注的演示场景，不允许冒充真实顾客
expression_subject: NATURAL_PERSON
expression_boundary: 不得制造身材或年龄焦虑
subject_and_account_scope: 序里集品牌号 + 零售搭配负责人苏禾
applicability_reason: 本次涉及单条内容任务，不涉及长期定位实质修改
deadline_or_stage_boundary: 初秋通勤衣橱第一阶段
capacity_or_owner: 苏禾半天出镜 + 单人手机拍摄
facts_registered: 苏禾三组试穿记录；三处偏挤；去掉马甲正式感掉一档
content_origin_mode: 现拍
subject_domain: 服装 / 门店零售
platform: NOT_LOCKED
duration_band: SHORT
cta_level: LOW_RISK_INTERACTION
equivalence_basis: 持续运营决策直接给出统一 Content Task 核心
"""

CT_CAMPAIGN = CT_M3.replace("source_kind: M3_OPERATION", "source_kind: CAMPAIGN").replace(
    "equivalence_basis: 持续运营决策直接给出统一 Content Task 核心",
    "equivalence_basis: Campaign 内容任务以统一 Content Task 语义出口")

THIN_FIELDS = """
objective:
  primary_goal: 提升影响力
  goal_family: TRAFFIC
audience_problem: 顾客不了解我们
expected_change: 让大家更了解我们
content_promise: 做一条好内容
expression_subject_and_boundary: 无
facts_registered:
"""

MATRIX_INSUFFICIENT = """
provenance:
  source_kind: USER_DIRECT
applicability_reason: 用户要求建立四个账号的长期分工，涉及长期定位与账号职责
subject_and_account_scope: 序里集，四个账号
objective:
  primary_goal: 建立四个账号的长期分工
  goal_family: LONG_TERM_VALUE
expression_boundary: 不得制造年龄身材焦虑
facts_registered: 业务模式、核心顾客、当前经营任务
"""

SCRIPT_LEGAL = """
provenance:
  source_kind: HISTORICAL_ARTIFACT
content_promise: 给出一个可以在自己衣橱里直接照做的分层判断
explicit_non_promise: 不承诺哪一件更好
content_origin_mode: 现拍
production_profile: 单人手机
time_window: 半天
script_or_equivalent_beats: B1/B2/B3/B4 四个节拍，逐条带事实与素材两问
objective:
  goal_family: LONG_TERM_VALUE
subject_domain: 服装 / 门店零售
platform: NOT_LOCKED
"""

FOOTAGE_FINAL = """
provenance:
  source_kind: HISTORICAL_ARTIFACT
content_body_or_beats: B1-B4 逐条对应成片时间码
content_promise: 给出一个可以在自己衣橱里直接照做的分层判断
explicit_non_promise: 不承诺哪一件更好；不承诺适用于所有身材
facts_registered: 苏禾三组试穿记录
cta_contract: LOW_RISK_INTERACTION
cta_level: LOW_RISK_INTERACTION
asset_publish_permission: 门店内拍摄已授权；不得出现其他顾客正脸
realization_manifest: B1..B4 逐条 beat 级兑现，缺口已处置
subject_domain: 服装 / 门店零售
platform: NOT_LOCKED
objective:
  goal_family: LONG_TERM_VALUE
"""

ACCEPTED_DIRECTION = CT_M3 + "\naccepted_direction: 苏禾按三组试穿讲为什么这次两边不能同时满足\n"

REAL_TRADEOFF = CT_M3 + """
candidate_axes_note: 两条路径在 核心矛盾 / 叙事发动机 / 人物关系 / 信息释放顺序 上均不同
"""

# FX-M4-NO-TRADEOFF（夹具包 §13）：事实只支持一个核心矛盾，只有一条合理路径。
# 就是不带取舍轴标注的 CT_M3 —— 判据是「直接给推荐、候选数=1」，凑候选才是缺陷。
NO_TRADEOFF = CT_M3

# FX-M4-MIXED-GOALS（夹具包 §9）：周期层混合目标进单条 Brief。
MIXED_GOALS = CT_M3.replace(
    "objective:\n  primary_goal: 让目标顾客形成分层判断，并愿意继续听这个账号的判断\n"
    "  goal_family: LONG_TERM_VALUE",
    "objective:\n  primary_goal: 让目标顾客形成分层判断\n"
    "  goal_family: MIXED\n"
    "  cycle_goals: [\"长期价值\", \"起号\", \"到店转化\"]\n"
    "  secondary_goals: [\"为到店留自然入口\"]")

GOAL_A = CT_M3
GOAL_B = CT_M3.replace("goal_family: LONG_TERM_VALUE", "goal_family: LEADS").replace(
    "primary_goal: 让目标顾客形成分层判断，并愿意继续听这个账号的判断",
    "primary_goal: 让刷到的人当场留下一个可回访的联系动作")


# ==========================================================================
# 探针
# ==========================================================================

def probe_sufficiency():
    """AC-04 / N-34：等价输入按业务语义判定；极薄字段齐全不构成等价。"""
    cases = [
        # (capability, envelope, professional_input, 期望 can_run, 说明)
        ("CONTENT_BRIEF", CT_M3, "", "true", "M3 来源 Content Task 充分"),
        ("CONTENT_BRIEF", CT_CAMPAIGN, "", "true", "Campaign 来源 Content Task 充分"),
        # 期望值取自冻结夹具包 §10 `FX-M4-THIN-FIELDS` 的判据：「判 INSUFFICIENT，不得冒充等价输入」。
        # 这不是按结果反填——夹具在任何结果之前已冻结。
        ("CONTENT_BRIEF", THIN_FIELDS, "", "false", "极薄「字段齐全」判 INSUFFICIENT，不冒充等价输入"),
        ("PRODUCTION_DIRECTOR", SCRIPT_LEGAL, "", "true", "合法脚本等价输入直达 PD"),
        ("PUBLISHING_PACKAGING", FOOTAGE_FINAL, "", "true", "合法成片等价兑现证据直达 PP"),
        ("PUBLISHING_PACKAGING", CT_M3, "", "false", "缺兑现证据/权限语义 → 组件级 Return"),
        ("MATRIX", MATRIX_INSUFFICIENT, "", "true", "Matrix 结构在场"),
    ]
    for cap, env, prof, want, why in cases:
        main = load_node_code(APPS[cap], "envelope_check")
        r = main(env, prof, "", "", "NO")
        ok = r["can_run"] == want
        detail = "%s can_run=%s(want %s) status=%s missing=%s vacuity=%s" % (
            cap, r["can_run"], want, r["status"], r["missing"], r["vacuity_flags"])
        check("AC-04", why, ok, detail)

    # N-34 专项（判据来自冻结夹具 §10）：
    #   ① 判 INSUFFICIENT，不冒充等价输入；
    #   ② 疑似语义单薄项被逐条标出（不是一句「信息不足」）；
    #   ③ 只阻断本分支，不整任务退回。
    main = load_node_code(APPS["CONTENT_BRIEF"], "envelope_check")
    r = main(THIN_FIELDS, "", "", "", "NO")
    ok = (r["status"] == "INSUFFICIENT"
          and bool(r["vacuity_flags"])
          and r["missing"] != [])
    check("N-34", "极薄「字段齐全」判 INSUFFICIENT，且逐条标出单薄项与缺项", ok,
          "status=%s missing=%s vacuity_flags=%s" % (
              r["status"], r["missing"], r["vacuity_flags"]))

    ret = load_node_code(APPS["CONTENT_BRIEF"], "component_return")
    rr = ret(r["status"], r["note"], r["missing"], r["entry_resolved"], r["envelope_hash"], THIN_FIELDS)
    check("N-34", "极薄输入只阻断本分支，不整任务退回",
          rr["is_task_terminal_state"] == "false" and rr["triggers_downstream_invalidation"] == "false",
          "terminal=%s invalidation=%s" % (rr["is_task_terminal_state"],
                                           rr["triggers_downstream_invalidation"]))


def probe_goal_fidelity_readonly():
    """AC-17 / N-31 的确定性部分：goal_family 被原样只读继承，不被外壳改写。"""
    for cap in ("CONTENT_BRIEF", "CREATIVE_SCRIPT", "PUBLISHING_PACKAGING"):
        main = load_node_code(APPS[cap], "envelope_check")
        a = main(GOAL_A, "", "", "", "NO")
        b = main(GOAL_B, "", "", "", "NO")
        ok = a["goal_family"] == "LONG_TERM_VALUE" and b["goal_family"] == "LEADS"
        check("AC-17", "%s：goal_family 原样只读继承（A=%s B=%s）" % (cap, a["goal_family"], b["goal_family"]),
              ok, "外壳未改写目标；实质变化由 Skill 正文与盲评判定（本脚本不代替）")


def probe_cta_not_auto_authorized():
    """AC-28 / N-49：目标本身不自动授权高风险 CTA。"""
    gmv_no_auth = FOOTAGE_FINAL.replace("goal_family: LONG_TERM_VALUE", "goal_family: GMV")
    main = load_node_code(APPS["PUBLISHING_PACKAGING"], "envelope_check")
    r = main(gmv_no_auth, "", "", "", "NO")
    ok = r["goal_family"] == "GMV" and r["cta_level"] == "LOW_RISK_INTERACTION"
    check("AC-28", "goal_family=GMV 未把 cta_level 自动提升到 HIGH_RISK", ok,
          "goal_family=%s cta_level=%s" % (r["goal_family"], r["cta_level"]))

    explicit_high = FOOTAGE_FINAL.replace("cta_level: LOW_RISK_INTERACTION",
                                          "cta_level: KNOWN_BUT_NOT_AUTHORIZED")
    r2 = main(explicit_high, "", "", "", "NO")
    ok2 = r2["cta_level"] == "KNOWN_BUT_NOT_AUTHORIZED"
    check("AC-28", "KNOWN_BUT_NOT_AUTHORIZED 被原样保留（权限不全 != 信息不全）", ok2,
          "cta_level=%s" % r2["cta_level"])


def probe_component_return():
    """AC-06 / N-04 / N-39：不足只出组件级 Return，不是整任务终态，不触发下游失效。"""
    main_env = load_node_code(APPS["MATRIX"], "envelope_check")
    main_ret = load_node_code(APPS["MATRIX"], "component_return")
    bad = "provenance:\n  source_kind: USER_DIRECT\n"
    e = main_env(bad, "", "", "", "NO")
    r = main_ret(e["status"], e["note"], e["missing"], e["entry_resolved"],
                 e["envelope_hash"], bad)
    rets = json.loads(r["returns_json"])
    seven = ["return_id", "source", "highest_damaged_layer", "precise_gap",
             "affected_objects", "proposed_disposition", "needs_user_decision",
             "downstream_stale"]
    ok = (e["can_run"] == "false"
          and len(rets) == 1
          and all(k in rets[0] for k in seven)
          and rets[0]["precise_gap"] not in ("", "信息不足")
          and r["is_task_terminal_state"] == "false"
          and r["triggers_downstream_invalidation"] == "false"
          and r["fabricated_artifact_produced"] == "false"
          and r["downstream_invoked"] == "false")
    check("AC-06", "Matrix 不足 → 七项齐全的组件级 Return；非整任务终态；不造假；不启下游", ok,
          "can_run=%s terminal=%s invalidation=%s fabricated=%s downstream=%s gap=%r" % (
              e["can_run"], r["is_task_terminal_state"], r["triggers_downstream_invalidation"],
              r["fabricated_artifact_produced"], r["downstream_invoked"], rets[0]["precise_gap"][:60]))

    # 判据（冻结夹具 §6.2 + 统一合同 §11.3）：
    #   ① 只追问一项；② 追问是自然语言，**不得出现内部字段名**；③ 不要求重填整套输入。
    ask = r["single_most_discriminating_question"]
    ok2 = (len(ask) > 0
           and r["user_delivery_leaks"] == []
           and "重填" not in ask
           and ask != "applicability_reason")
    check("N-39", "只追问最具区分力的一项，且以自然语言表达（用户交付零内部字段名）", ok2,
          "ask=%r leaks=%s" % (ask[:70], r["user_delivery_leaks"]))


def probe_returns_parse():
    """AC-14 / N-12 / N-13：解析失败 != NONE；显式 NONE 与真实条目分开。"""
    main = load_node_code(APPS["CREATIVE_SCRIPT"], "returns_adapter")

    good = ("---M4_ARTIFACT---\nA\n---END_M4_ARTIFACT---\n"
            "---M4_USER_DELIVERY---\nstatus: READY\n正文\n---END_M4_USER_DELIVERY---\n"
            "---M4_RETURNS---\nNONE\n---END_M4_RETURNS---\n")
    r = main(good)
    check("AC-14", "显式 NONE 被识别为「无回改」而不是解析失败",
          r["returns_status"] == "NONE" and r["local_block"] == "false",
          "status=%s block=%s" % (r["returns_status"], r["local_block"]))

    empty = good.replace("NONE\n", "\n")
    r2 = main(empty)
    check("N-12", "RETURNS 块为空 → PARSE_FAILED + 局部阻断（空 != NONE）",
          r2["returns_status"] == "PARSE_FAILED" and r2["local_block"] == "true",
          "status=%s note=%r" % (r2["returns_status"], r2["returns_parse_note"][:70]))

    broken = good.replace("NONE", "return_id: R1\nsource: CS\nprecise_gap: 缺一句原话")
    r3 = main(broken)
    check("N-12", "RETURNS 条目缺字段 → PARSE_FAILED，不伪装成空数组",
          r3["returns_status"] == "PARSE_FAILED" and json.loads(r3["returns_json"]) == [],
          "status=%s note=%r" % (r3["returns_status"], r3["returns_parse_note"][:90]))

    missing_block = ("---M4_ARTIFACT---\nA\n---END_M4_ARTIFACT---\n"
                     "---M4_USER_DELIVERY---\nstatus: READY\n正文\n---END_M4_USER_DELIVERY---\n")
    r4 = main(missing_block)
    check("N-12", "整个 RETURNS 块缺失 → PARSE_FAILED，不静默当成无回改",
          r4["returns_status"] == "PARSE_FAILED" and r4["returns_raw"] == "ABSENT",
          "status=%s raw=%s" % (r4["returns_status"], r4["returns_raw"]))

    full = ("---M4_ARTIFACT---\nA\n---END_M4_ARTIFACT---\n"
            "---M4_USER_DELIVERY---\nstatus: NEEDS_DECISION\n正文\n---END_M4_USER_DELIVERY---\n"
            "---M4_RETURNS---\n"
            "return_id: R1\nsource: PRODUCTION_DIRECTOR\nhighest_damaged_layer: SCRIPT_FACT\n"
            "precise_gap: B2 的三处没有对应特写单元\naffected_objects: beat-B2 | 单元 U2\n"
            "proposed_disposition: REJECT_WITH_AUTHORITY\nneeds_user_decision: false\n"
            "downstream_stale: PP 对 B2 的兑现判断\n"
            "---END_M4_RETURNS---\n")
    r5 = main(full)
    rets = json.loads(r5["returns_json"])
    ok5 = (r5["returns_status"] == "OK" and len(rets) == 1
           and rets[0]["proposed_disposition"] == "REJECT_WITH_AUTHORITY"
           and rets[0]["downstream_stale"] == ["PP 对 B2 的兑现判断"])
    check("N-13", "被拒绝的 Return 保留权威理由与精确失效集，不沉默丢失", ok5,
          "status=%s disposition=%s stale=%s" % (
              r5["returns_status"], rets[0]["proposed_disposition"] if rets else "-",
              rets[0]["downstream_stale"] if rets else "-"))

    ok6 = rets and rets[0]["downstream_stale"] != [] and len(rets[0]["downstream_stale"]) == 1
    check("AC-30", "失效集只列真实依赖项，不做全链级联", bool(ok6),
          "downstream_stale=%s" % (rets[0]["downstream_stale"] if rets else "-"))


def probe_user_view_leak():
    """AC-13 / N-23：用户交付块禁项被机械拦截；同时不得把必要选择投影掉。"""
    main = load_node_code(APPS["PUBLISHING_PACKAGING"], "returns_adapter")
    leaky = ("---M4_ARTIFACT---\nA\n---END_M4_ARTIFACT---\n"
             "---M4_USER_DELIVERY---\nstatus: READY\n"
             "这句话已删除，因为无事实支撑。CTA 级别 BUSINESS_HANDOFF。\n"
             "---END_M4_USER_DELIVERY---\n"
             "---M4_RETURNS---\nNONE\n---END_M4_RETURNS---\n")
    r = main(leaky)
    ok = r["user_delivery_status"] == "LEAK_DETECTED" and "已删除" in r["user_delivery_leaks"] \
        and "BUSINESS_HANDOFF" in r["user_delivery_leaks"] and r["local_block"] == "true"
    check("AC-13", "用户交付块出现「已删除」便条与内部分级术语 → 拦截并局部阻断", ok,
          "status=%s leaks=%s" % (r["user_delivery_status"], r["user_delivery_leaks"]))

    clean = leaky.replace("这句话已删除，因为无事实支撑。CTA 级别 BUSINESS_HANDOFF。",
                          "你可以先只解决一层。要不要我按到店试穿再写一版？")
    r2 = main(clean)
    ok2 = r2["user_delivery_status"] == "OK" and "要不要" in r2["user_delivery"]
    check("AC-13", "干净交付通过，且用户的必要选择未被投影掉", ok2,
          "status=%s" % r2["user_delivery_status"])


def probe_artifact_preserved():
    """N-22：结构缺失/核验失败时保留原文，不删句翻绿。"""
    main = load_node_code(APPS["PUBLISHING_PACKAGING"], "returns_adapter")
    raw = "模型直接吐了一段没有结构标记的文本，里面有一句无来源主张。"
    r = main(raw)
    ok = (r["artifact_status"] == "STRUCTURE_MISSING_RAW_PRESERVED"
          and r["raw_preserved"] == raw and r["local_block"] == "true")
    check("N-22", "结构缺失时保留原始输出并局部阻断，不静默丢弃、不翻绿", ok,
          "artifact_status=%s block=%s raw_len=%d" % (
              r["artifact_status"], r["local_block"], len(r["raw_preserved"])))


def probe_entry_resolution():
    """AC-22/23 / N-09 / N-43 / N-44：ENTRY-04 与 ENTRY-05 同一处锦标赛路径。"""
    main = load_node_code(SEAM, "entry_resolver")

    r = main("CREATIVE_SCRIPT", "", ACCEPTED_DIRECTION, "")
    check("N-09", "已选方向 → ENTRY-05 直达脚本，不重开锦标赛",
          r["entry_resolved"] == "ENTRY-05" and r["run_mode"] == "SELECTED_DIRECTION_TO_SCRIPT",
          "entry=%s run_mode=%s derivation=%s" % (r["entry_resolved"], r["run_mode"], r["derivation"]))

    r2 = main("CREATIVE_SCRIPT", "", REAL_TRADEOFF, "")
    check("N-43", "确有取舍结构前提 → ENTRY-04 进入 CS-1（同一处锦标赛路径）",
          r2["entry_resolved"] == "ENTRY-04" and r2["run_mode"] == "TOURNAMENT_ONLY",
          "entry=%s run_mode=%s" % (r2["entry_resolved"], r2["run_mode"]))

    r3 = main("CREATIVE_SCRIPT", "", CT_M3, "")
    check("N-50", "无真实取舍结构前提 → 直接推荐（候选数=1），不凑候选",
          r3["entry_resolved"] == "ENTRY-05",
          "entry=%s derivation=%s" % (r3["entry_resolved"], r3["derivation"]))

    for cap, want in [("MATRIX", "ENTRY-01"), ("CAMPAIGN", "ENTRY-02"),
                      ("CONTENT_BRIEF", "ENTRY-03"), ("PRODUCTION_DIRECTOR", "ENTRY-06"),
                      ("PUBLISHING_PACKAGING", "ENTRY-07")]:
        rr = main(cap, "", CT_M3, "")
        check("AC-03", "%s → %s 确定性映射" % (cap, want), rr["entry_resolved"] == want,
              "entry=%s" % rr["entry_resolved"])

    r4 = main("SOME_OTHER_THING", "", CT_M3, "")
    check("AC-03", "不支持的能力被如实拒绝，M4 不代做 M1 的能力选择",
          r4["route"] == "UNSUPPORTED", "route=%s" % r4["route"])

    r5 = main("CAMPAIGN", "", CT_M3 + "\ncampaign_run_mode: COMPILE_CONFIRMED_DECISIONS\n", "")
    check("N-06", "输入显式为已确认决定包时才用 compile 模式",
          r5["run_mode"] == "COMPILE_CONFIRMED_DECISIONS", "run_mode=%s" % r5["run_mode"])

    r6 = main("CAMPAIGN", "", CT_M3, "")
    check("N-05", "未确认经营任务保持 PLANNING，不被强制 compile",
          r6["run_mode"] == "PLANNING", "run_mode=%s" % r6["run_mode"])

    r7 = main("PRODUCTION_DIRECTOR", "", FOOTAGE_FINAL, "")
    check("AC-09", "存在 realization_manifest → MANIFEST 模式；否则 PLAN",
          r7["run_mode"] == "MANIFEST" and main("PRODUCTION_DIRECTOR", "", SCRIPT_LEGAL, "")["run_mode"] == "PLAN",
          "with_manifest=%s without=%s" % (r7["run_mode"],
                                           main("PRODUCTION_DIRECTOR", "", SCRIPT_LEGAL, "")["run_mode"]))


def probe_no_hidden_upstream():
    """AC-03 / N-01 / N-02 / N-03：六个能力应用之间零 tool 调用边。"""
    for cap, path in APPS.items():
        with open(path, encoding="utf-8") as fh:
            d = yaml.safe_load(fh)
        tools = [n for n in d["workflow"]["graph"]["nodes"] if n["data"].get("type") == "tool"]
        check("AC-03", "%s 应用内零 tool 节点（结构上不可能暗跑上游）" % cap,
              len(tools) == 0, "tool_nodes=%d" % len(tools))

    main = load_node_code(SEAM, "fin_content_brief")
    r = main("CONTENT_BRIEF", "ENTRY-03", "DEFAULT", "确定性映射", "A", "U", "[]", "{}", "h")
    trace = json.loads(r["seam_trace_json"])
    ok = (trace["capability_invoked"] == ["CONTENT_BRIEF"]
          and trace["upstream_auto_invoked"] == []
          and set(trace["capabilities_skipped_because_not_applicable_or_equivalent_input_satisfied"])
          == {"MATRIX", "CAMPAIGN", "CREATIVE_SCRIPT", "PRODUCTION_DIRECTOR", "PUBLISHING_PACKAGING"})
    check("N-01", "直接 Brief 的接缝轨迹：只调 CONTENT_BRIEF，其余五项显式跳过，零暗跑", ok,
          "invoked=%s auto=%s" % (trace["capability_invoked"], trace["upstream_auto_invoked"]))


def probe_reference_matrix():
    """AC-11 / N-18：条件附件加载矩阵被机械执行。"""
    expect = {
        "MATRIX": (False, False, False),
        "CAMPAIGN": (False, False, False),
        "CONTENT_BRIEF": (False, False, False),
        "CREATIVE_SCRIPT": (True, True, True),
        "PRODUCTION_DIRECTOR": (True, True, True),
        "PUBLISHING_PACKAGING": (True, True, True),
    }
    for cap, path in APPS.items():
        with open(path, encoding="utf-8") as fh:
            d = yaml.safe_load(fh)
        n = {x["id"]: x for x in d["workflow"]["graph"]["nodes"]}
        t = n["ref_projection"]["data"]["template"]
        got = ("platforms.md ::" in t, "industry-conditions.md ::" in t, "examples.md ::" in t)
        check("AC-11", "%s 的 reference 投影与加载矩阵一致" % cap, got == expect[cap],
              "got(platforms,industry,examples)=%s want=%s" % (got, expect[cap]))
        if not any(expect[cap]):
            check("N-18", "%s：无关附件全文未被加载" % cap, "本次未加载任何参考文件" in t,
                  "模板显式声明未加载")


def probe_fidelity_chain():
    """AC-12 静态部分：system prompt 逐字节派生自后继 SKILL；绑定记录完整。"""
    with open(os.path.join(DC_WF, "DIYU_M4_FIDELITY_RECORDS.json"), encoding="utf-8") as fh:
        recs = json.load(fh)
    import hashlib
    for key, rec in recs.items():
        body = open(os.path.join(ROOT, rec["successor_skill_path"]), encoding="utf-8").read()
        ok = hashlib.sha256(body.encode()).hexdigest() == rec["successor_skill_sha256"]
        check("AC-12", "%s 后继 SKILL sha256 与绑定记录一致" % rec["capability"], ok,
              rec["successor_skill_sha256"][:16])
        src = open(os.path.join(ROOT, rec["source_skill_path"]), encoding="utf-8").read()
        ok2 = hashlib.sha256(src.encode()).hexdigest() == rec["source_skill_sha256"]
        check("AC-12", "%s 源 SKILL sha256 与绑定记录一致（源零改动）" % rec["capability"], ok2,
              rec["source_skill_sha256"][:16])

        path = APPS[rec["capability"]]
        with open(path, encoding="utf-8") as fh:
            d = yaml.safe_load(fh)
        n = {x["id"]: x for x in d["workflow"]["graph"]["nodes"]}
        sysmsg = [m for m in n["skill_llm"]["data"]["prompt_template"] if m["role"] == "system"][0]["text"]
        ok3 = hashlib.sha256(sysmsg.encode()).hexdigest() == rec["system_prompt_sha256"]
        check("AC-12", "%s DSL 内 system prompt 字节与绑定记录一致" % rec["capability"], ok3,
              rec["system_prompt_sha256"][:16])
        ok4 = body.rstrip() in sysmsg
        check("AC-12", "%s system prompt 逐字节包含后继 SKILL 全文" % rec["capability"], ok4, "")


def probe_provider_binding_honesty():
    """N-20 的前置：provider 绑定未解析时必须如实标记，不得当作已成立。"""
    with open(os.path.join(DC_WF, "DIYU_M4_PROVIDER_BINDINGS.json"), encoding="utf-8") as fh:
        b = json.load(fh)
    with open(SEAM, encoding="utf-8") as fh:
        s = yaml.safe_load(fh)
    tools = [n for n in s["workflow"]["graph"]["nodes"] if n["data"].get("type") == "tool"]
    pending = [t for t in tools if t["data"]["provider_id"] == "PENDING_PUBLISH"]
    resolved = [t for t in tools if t["data"]["provider_id"] != "PENDING_PUBLISH"]
    # 判据：绑定文件与 DSL 必须一致，且 PENDING 必须被如实反映
    by_tool = {t["data"]["tool_name"]: t["data"]["provider_id"] for t in tools}
    mismatch = []
    for k, v in b.items():
        if k == "_seam":            # 接缝自己的 provider 属于画布，不在接缝的 tool 节点里
            continue
        if by_tool.get(v["tool_name"]) != v["provider_id"]:
            mismatch.append("%s: 绑定表=%s DSL=%s"
                            % (k, v["provider_id"], by_tool.get(v["tool_name"], "缺节点")))
    check("N-20", "父接缝 provider 绑定与绑定文件逐项一致（重绑机制存在）", not mismatch,
          "tools=%d pending=%d resolved=%d 不一致=%s"
          % (len(tools), len(pending), len(resolved), mismatch or "无"))

    # 画布那一层：唯一的 tool 节点必须指向接缝的 provider
    if "_seam" in b:
        with open(CANVAS, encoding="utf-8") as fh:
            cv = yaml.safe_load(fh)
        ct = [n for n in cv["workflow"]["graph"]["nodes"] if n["data"].get("type") == "tool"]
        ok = len(ct) == 1 and ct[0]["data"]["provider_id"] == b["_seam"]["provider_id"]
        check("N-20", "Founder 画布的唯一 tool 节点指向统一接缝 provider", ok,
              "canvas_tools=%d provider=%s 期望=%s"
              % (len(ct), ct[0]["data"]["provider_id"] if ct else "无", b["_seam"]["provider_id"]))
    RESULTS.append({
        "probe": "N-20", "name": "provider 绑定当前状态",
        "result": "PASS" if len(pending) == 0 else "NOT_VERIFIED",
        "detail": "%d/%d 个 tool 节点仍为 PENDING_PUBLISH。未解析前不得宣称 Runtime 入口可达成立。"
                  % (len(pending), len(tools)),
    })




# ---------------------------------------------------------------------------
# M4-BLK-002 解锁后的画布行为（Founder 2026-08-26 授权后新增）
#
# 判据来源（**先于结果冻结**，不是看到结果才写的）：
#   · 统一能力合同 §2「七入口 / REQUIRED_ALWAYS: [] / DEFAULT_CALL: [] /
#     FIXED_ORDER: false / FULL_CHAIN_GATE: false」
#   · CLAUDE.md §3「Campaign 既不默认调用，也不默认绕过」
#     「不得为进入某组件暗中补跑前置组件」
# 新增的只是**探针**（测量手段），不是新判据。判据早于结果，A2 第 3 项成立。
# ---------------------------------------------------------------------------

def _canvas_snap(confirmed=True, artifacts=None, last_result_ref=None,
                 last_acceptance=None, no_goal=False):
    art = {"matrix": None, "campaign": None, "content_brief": None,
           "production_stage1": None, "publishing_stage2": None}
    if artifacts:
        art.update(artifacts)
    task = {"goal": "初秋通勤这批货，想让顾客早上不再纠结怎么穿", "target_object": "初秋通勤系列"}
    draft = {"goal": None, "target_object": None} if no_goal else dict(task)
    return {
        "schema_version": 1,
        "task_id": "task_001",
        "revision": 1,
        "phase": "READY" if confirmed else "FORMING",
        "candidate_skill": "NONE",
        "draft_task": draft,
        "confirmed_task": dict(task) if confirmed else None,
        "pending_action": None,
        "authorization": {"skill": "NONE", "task_revision": None,
                          "confirmation_id": None, "granted": False, "consumed": True},
        "artifacts": art,
        "blocking_gap": None,
        "last_result_ref": last_result_ref,
        "last_error": None,
        "open_threads": [],
        "last_acceptance": last_acceptance,
    }


def probe_canvas_linear_lock_removed():
    """M4-BLK-002：画布路径上的线性硬锁已拆，且用户授权门原样保留。"""
    main = load_node_code(CANVAS, "v1_state", preload={"json": json})

    # N-51 直达入口：上游产物一份都没有，仍必须能执行
    direct = [("CONTENT_BRIEF", "EXECUTE_CONTENT_BRIEF", "ENTRY-03 直达 Content Brief"),
              ("PRODUCTION_STAGE1", "EXECUTE_PRODUCTION_STAGE1", "ENTRY-05/06 直达脚本与拍摄方案"),
              ("PUBLISHING_STAGE2", "EXECUTE_PUBLISHING_STAGE2", "ENTRY-07 直达发布包"),
              ("CAMPAIGN", "EXECUTE_CAMPAIGN", "ENTRY-02 直达 Campaign（不先跑矩阵）"),
              ("MATRIX", "EXECUTE_MATRIX", "ENTRY-01 矩阵")]
    for skill, want_route, label in direct:
        r = main("这一步直接做，别的先不做。", json.dumps(_canvas_snap()),
                 {"route_intent": "EXECUTE_REQUEST", "requested_skill": skill}, "")
        tr = json.loads(r["turn_report"])
        check("N-51", "无任何上游产物时 %s 仍可执行" % label,
              r["effective_route"] == want_route,
              "route=%s blocking_gap=%s notes=%s"
              % (r["effective_route"], tr.get("blocking_gap"), tr.get("notes")))

    # N-52 差分判据：与 M1 原文同输入对跑，行为差异必须**恰好**等于被授权拆掉的那把锁。
    #
    # 判据修正说明（A2 如实登记）：本探针初版把「用户授权门」写成
    # 「confirmed_task 为空就一定不执行」，跑出 3 条 FAIL。定向复核后确认那是
    # **我的判据写错**，不是补丁削弱了门：M1 原文本来就允许在用户自己那句话里
    # 确认任务（notes 里的 TASK_CONFIRMED_BY_EXPLICIT_EXECUTION_REQUEST），
    # 打补丁前后**完全一致**。冻结判据（统一能力合同 §2「只拆固定顺序，
    # 不动用户授权」）没有变，变的只是测量方式，而且换成了更强的差分测量。
    m1_main = load_node_code(
        os.path.join(DC_WF, "DIYU_DEMO_V1_FULL_CHAIN_CHATFLOW_v0.2.yml"),
        "v1_state", preload={"json": json})

    ALLOWED_DELTA = "EXECUTION_BLOCKED:UPSTREAM_"      # 唯一被授权消失的行为
    states = [("有草稿目标但未确认", _canvas_snap(confirmed=False)),
              ("完全没有任务", _canvas_snap(confirmed=False, no_goal=True)),
              ("已确认任务", _canvas_snap())]
    unexpected, blocked_both = [], 0
    for label, sc in states:
        for skill in ["MATRIX", "CAMPAIGN", "CONTENT_BRIEF",
                      "PRODUCTION_STAGE1", "PUBLISHING_STAGE2"]:
            p = {"route_intent": "EXECUTE_REQUEST", "requested_skill": skill}
            a = m1_main("跑一下。", json.dumps(sc), dict(p), "")
            b = main("跑一下。", json.dumps(sc), dict(p), "")
            ra, rb = a["effective_route"], b["effective_route"]
            na = json.loads(a["turn_report"])["notes"]
            if ra == rb:
                if not rb.startswith("EXECUTE_"):
                    blocked_both += 1
                continue
            # 只允许这一种差异：M1 因上游锁拦下、M4 放行
            if not (any(n.startswith(ALLOWED_DELTA) for n in na)
                    and rb == "EXECUTE_" + skill):
                unexpected.append("%s/%s: M1=%s M4=%s notes=%s" % (label, skill, ra, rb, na))

    check("N-52", "解锁前后的行为差异恰好等于被授权拆掉的上游锁，没有第二种差异",
          not unexpected, "越界差异：" + ("；".join(unexpected) if unexpected else "无"))

    r_none = main("跑一下。", json.dumps(_canvas_snap(confirmed=False, no_goal=True)),
                  {"route_intent": "EXECUTE_REQUEST", "requested_skill": "PUBLISHING_STAGE2"}, "")
    check("N-52", "完全没有任务时仍然不执行（用户授权门保留，不是流水线锁）",
          not r_none["effective_route"].startswith("EXECUTE_")
          and blocked_both >= 5,
          "route=%s 两版同时拦下的组合数=%d" % (r_none["effective_route"], blocked_both))

    r_ctrl = main("跑一下。", json.dumps(_canvas_snap()),
                  {"route_intent": "EXECUTE_REQUEST", "requested_skill": "MATRIX"}, "")
    r_ctrl_m1 = m1_main("跑一下。", json.dumps(_canvas_snap()),
                        {"route_intent": "EXECUTE_REQUEST", "requested_skill": "MATRIX"}, "")
    check("N-52", "对照组 MATRIX（本来就没有上游锁）行为与 M1 原文完全一致",
          r_ctrl["effective_route"] == r_ctrl_m1["effective_route"] == "EXECUTE_MATRIX",
          "M1=%s M4=%s" % (r_ctrl_m1["effective_route"], r_ctrl["effective_route"]))

    # N-53 「接受并继续」不再自动授权固定的下一棒
    snap = _canvas_snap(artifacts={"matrix": {"status": "VALIDATED"}},
                        last_result_ref="matrix")
    r = main("这份可以，继续。", json.dumps(snap),
             {"route_intent": "CONFIRM_TASK", "acceptance_signal": "ACCEPT_CURRENT_ARTIFACT",
              "continue_signal": "YES"}, "")
    tr = json.loads(r["turn_report"])
    notes = tr.get("notes") or []
    check("N-53", "接受矩阵并说「继续」不自动调用 Campaign（DEFAULT_CALL 为空）",
          r["effective_route"] != "EXECUTE_CAMPAIGN"
          and not any(n.startswith("CONTINUE_TO_NEXT_SKILL") for n in notes),
          "route=%s notes=%s" % (r["effective_route"], notes))
    check("N-54", "接受仍然生效，且回执落到既有分支而不是死路",
          any(n.startswith("ARTIFACT_ACCEPTED:") for n in notes)
          and r["effective_route"] == "CONFIRM_TASK",
          "route=%s notes=%s" % (r["effective_route"], notes))

    # N-55 回归：撤销接受时的保守失效（DOWNSTREAM_OF_SLOT）未被误删
    snap2 = _canvas_snap(artifacts={"matrix": {"status": "USER_ACCEPTED",
                                              "accepted_turn_id": "rev_001"},
                                    "content_brief": {"status": "USER_ACCEPTED",
                                                      "accepted_turn_id": "rev_001"}},
                         last_result_ref="matrix",
                         last_acceptance={"slot": "matrix", "revision": 1})
    r2 = main("刚才那个矩阵先不算接受了。", json.dumps(snap2),
              {"route_intent": "DISCUSS", "acceptance_signal": "REVOKE_LAST_ACCEPTANCE"}, "")
    st = json.loads(r2["snapshot_json"])["artifacts"]
    check("N-55", "撤销接受仍级联标 STALE（A3 保守失效未被误删）",
          st["matrix"]["status"] == "VALIDATED" and st["content_brief"]["status"] == "STALE",
          "matrix=%s content_brief=%s" % (st["matrix"]["status"], st["content_brief"]["status"]))

    # N-56 越界断言：差异恰好等于两处定义
    import difflib
    with open(os.path.join(DC_WF, "DIYU_DEMO_V1_FULL_CHAIN_CHATFLOW_v0.2.yml"), encoding="utf-8") as fh:
        m1 = yaml.safe_load(fh)
    with open(CANVAS, encoding="utf-8") as fh:
        cv = yaml.safe_load(fh)
    mn = {n["id"]: n for n in m1["workflow"]["graph"]["nodes"]}
    cn = {n["id"]: n for n in cv["workflow"]["graph"]["nodes"]}
    a = mn["v1_state"]["data"]["code"].splitlines()
    b = cn["v1_state"]["data"]["code"].splitlines()
    # ---- N-56：保持 v0.1 冻结口径不动 ----
    # 冻结原文（判据合同 §8.2）：「差异恰好 6 行、恰好属于 NEXT_SKILL 与 UPSTREAM_OF
    # 两处定义」，oracle =「本次授权范围本身」。
    #
    # 独立 Reviewer（FND-R-03）指出：把这条判据的允许集改成「由生成器自己的补丁
    # 登记表派生」，等于让被测物定义自己的通过条件，且当时已就地覆盖证据文件为 PASS。
    # **这条意见成立。** 已回退：N-56 恢复 v0.1 原文口径，当前产物在这个口径下
    # 就是 FAIL —— 因为授权边界确实从「两处」扩到了「四处」。
    # 那次扩边界有权威事件（见判据合同 §9），但**权威事件不能追溯地把旧口径变成 PASS**。
    # 新口径另起编号 N-59，两条并列上报：旧边界被突破是事实，新边界成立也是事实。
    import difflib as _dl
    sm = _dl.SequenceMatcher(None, a, b, autojunk=False)
    blocks = [op for op in sm.get_opcodes() if op[0] != "equal"]
    v01_lines = 0
    v01_only_two_defs = True
    for tag, i1, i2, j1, j2 in blocks:
        v01_lines += max(i2 - i1, j2 - j1)
        for ln in a[i1:i2]:
            if not (ln.startswith(("NEXT_SKILL", "UPSTREAM_OF"))
                    or ln.startswith(('              "', '               "'))):
                v01_only_two_defs = False
    v01_ok = (len(a) == len(b) and len(blocks) == 2
              and v01_lines == 6 and v01_only_two_defs)
    check("N-56", "[v0.1 冻结口径] 差异恰好 6 行、恰好属于 NEXT_SKILL 与 UPSTREAM_OF 两处定义",
          v01_ok,
          "实测：行数 %d->%d（v0.1 要求不变），差异块 %d 个（要求 2 个），涉及行 %d（要求 6）。"
          "超出部分是 M4-FND-001 与 M4-FND-003 两处后续补丁 —— 授权边界确实从两处扩到了四处。"
          "权威事件见判据合同 §9；**旧口径不因新授权而追溯变绿**，故如实记 FAIL。新口径见 N-59。"
          % (len(a), len(b), len(blocks), v01_lines))

    # ---- N-59：新口径（登记表派生），另起编号，不覆盖 N-56 ----
    import importlib.util as _iu
    _sp = _iu.spec_from_file_location("m4b", os.path.join(DC_WF, "DIYU_M4_DSL_BUILD_v0.1.py"))
    _bm = _iu.module_from_spec(_sp)
    _sp.loader.exec_module(_bm)
    allowed_minus, allowed_plus = set(), set()
    for old, new in _bm.V1_STATE_PATCHES:
        allowed_minus |= set(old.splitlines())
        allowed_plus |= set(new.splitlines())
    expected_added = sum(len(new.splitlines()) - len(old.splitlines())
                         for old, new in _bm.V1_STATE_PATCHES)
    stray = []
    for line in difflib.unified_diff(a, b, lineterm="", n=0):
        if line.startswith(("---", "+++", "@@")):
            continue
        if line.startswith("-") and line[1:] not in allowed_minus:
            stray.append("越界删除：" + line[1:][:60])
        elif line.startswith("+") and line[1:] not in allowed_plus:
            stray.append("越界新增：" + line[1:][:60])
    check("N-59", "[新口径] 差异全部落在已登记的 %d 处补丁内，无第三方改动"
          % len(_bm.V1_STATE_PATCHES),
          (len(b) - len(a)) == expected_added and not stray,
          "行数 %d->%d（期望净增 %d）越界项=%s。"
          "**这条不能替代 N-56**：允许集由登记表派生，只能证明「没有未登记的改动」，"
          "不能证明「授权边界本身没被放宽」——后者要靠 N-56 与权威事件记录。"
          % (len(a), len(b), expected_added, stray or "无"))

    same = json.dumps(mn["v1_shadow"]["data"], ensure_ascii=False, sort_keys=True) == \
           json.dumps(cn["v1_shadow"]["data"], ensure_ascii=False, sort_keys=True)
    check("N-56", "v1_shadow（M1 的自然语言理解）零改动", same,
          "byte_identical=%s" % same)


def probe_all_code_nodes_importable():
    """N-57：每一个代码节点都必须能在沙箱里加载并暴露 main()。

    为什么必须有这条：本探针原先只执行**被单独点名**的那几个代码节点，
    没有被点名的节点从未被执行过。2026-08-26 首次真实 Dify 运行时，
    六个能力应用的 `binding_record` 节点全部在模块级 `NameError:
    name 'true' is not defined` 上炸掉 —— 根因是生成器把 json.dumps 的
    结果直接当 Python 字面量贴进源码，`True` 变成了 JSON 的 `true`。
    这是一个**静态就能发现**的缺陷，却拖到线上才暴露。补这条探针，
    让「没被点名的节点」不再是盲区。
    """
    import glob
    targets = sorted(glob.glob(os.path.join(DC_WF, "DIYU_M4_*_v1_3_TEST.yml"))
                     + glob.glob(os.path.join(CP_WF, "DIYU_M4_*_v1_3_TEST.yml")))
    total, bad = 0, []
    for path in targets:
        with open(path, encoding="utf-8") as fh:
            d = yaml.safe_load(fh)
        for n in d["workflow"]["graph"]["nodes"]:
            if n["data"].get("type") != "code":
                continue
            total += 1
            try:
                fn = load_node_code(path, n["id"], preload={"json": json})
                if not callable(fn):
                    bad.append("%s::%s 没有可调用的 main()" % (os.path.basename(path), n["id"]))
            except Exception as e:
                bad.append("%s::%s -> %s: %s"
                           % (os.path.basename(path), n["id"], type(e).__name__, str(e)[:120]))
    check("N-57", "全部 %d 个代码节点都能加载并暴露 main()" % total, not bad,
          "加载失败：" + ("；".join(bad) if bad else "无"))

    # 另一半：JSON 字面量不得被当成 Python 字面量（就是上面那个缺陷的根因）
    import re as _re
    pat = _re.compile(r'(?<![\w"\'])(true|false|null)(?![\w"\'])')
    leaks = []
    for path in targets:
        with open(path, encoding="utf-8") as fh:
            d = yaml.safe_load(fh)
        for n in d["workflow"]["graph"]["nodes"]:
            if n["data"].get("type") != "code":
                continue
            for i, line in enumerate(n["data"]["code"].split("\n"), 1):
                stripped = _re.sub(r'"[^"]*"|\'[^\']*\'', "", line.split("#")[0])
                if pat.search(stripped):
                    leaks.append("%s::%s:%d" % (os.path.basename(path), n["id"], i))
    check("N-57", "代码节点里没有把 JSON 的 true/false/null 当成 Python 字面量",
          not leaks, "命中：" + ("；".join(leaks[:10]) if leaks else "无"))


# ---------------------------------------------------------------------------
# N-58：M4-FND-001 的 text 兜底
#
# 夹具不是编的 —— 下面两个坏载荷是 2026-08-26 从画布**线上运行**里实际抓到的
# structured_output 值（一个是 schema 里 continue_signal 自己的属性定义，
# 一个是被注入快照里的 pending_action 对象）。
# ---------------------------------------------------------------------------

BAD_SO_SCHEMA_FRAGMENT = {
    "description": "用户是否表达了「接受后继续下一步」。只有用户真的表达了继续才填 YES。",
    "enum": ["YES", "NO"], "type": "string",
}
BAD_SO_PENDING_ACTION = {
    "kind": "CONFIRM_TASK", "task_revision": 1, "confirmation_id": "confirm_001",
}
GOOD_PATCH = {
    "route_intent": "EXECUTE_REQUEST", "task_action": "NONE", "change_goal": "",
    "change_target_object": "", "confirmation_signal": "AFFIRM",
    "requested_skill": "CONTENT_BRIEF", "acceptance_signal": "NONE",
    "continue_signal": "YES", "user_message_summary": "用户确认任务，要求直接给出内容制作依据。",
    "side_question": "",
}


def probe_patch_text_fallback():
    main = load_node_code(CANVAS, "v1_state", preload={"json": json})
    snap = _canvas_snap()

    for label, bad in [("schema 片段", BAD_SO_SCHEMA_FRAGMENT),
                       ("pending_action 对象", BAD_SO_PENDING_ACTION)]:
        r = main("确认这个任务。直接给我这条内容的制作依据。", json.dumps(snap),
                 bad, "", json.dumps(GOOD_PATCH))
        tr = json.loads(r["turn_report"]) if r.get("patch_ok") == "true" else {}
        notes = tr.get("notes") or []
        check("N-58", "structured_output 是%s时，从 text 回收补丁并正常执行" % label,
              r["effective_route"] == "EXECUTE_CONTENT_BRIEF"
              and any(n.startswith("PATCH_RECOVERED_FROM_TEXT:") for n in notes),
              "route=%s notes=%s" % (r["effective_route"], notes))

    # 安全性质：两边都坏，必须照样拒 —— 兜底不得变成放行
    r2 = main("确认这个任务。", json.dumps(snap), BAD_SO_SCHEMA_FRAGMENT, "",
              json.dumps(BAD_SO_PENDING_ACTION))
    check("N-58", "text 也是坏补丁时仍然拒绝（兜底不放松安全性质）",
          r2.get("patch_ok") == "false" and r2["effective_route"] == "DISCUSS"
          and r2.get("reject_reason", "").startswith("PATCH_UNKNOWN_FIELDS"),
          "patch_ok=%s route=%s reject=%s"
          % (r2.get("patch_ok"), r2["effective_route"], r2.get("reject_reason")))

    # 正常路径不受影响：structured_output 好的时候不得留下回收痕迹
    r3 = main("确认这个任务。直接给我这条内容的制作依据。", json.dumps(snap),
              GOOD_PATCH, "", json.dumps(GOOD_PATCH))
    notes3 = json.loads(r3["turn_report"]).get("notes") or []
    check("N-58", "structured_output 正常时不触发兜底，行为与打补丁前一致",
          r3["effective_route"] == "EXECUTE_CONTENT_BRIEF"
          and not any(n.startswith("PATCH_RECOVERED_FROM_TEXT") for n in notes3),
          "route=%s notes=%s" % (r3["effective_route"], notes3))

    # 兜底缺省时（老调用方不传 patch_text）不得炸
    r4 = main("确认这个任务。直接给我这条内容的制作依据。", json.dumps(snap), GOOD_PATCH, "")
    check("N-58", "不传 patch_text 时向后兼容，不抛异常",
          r4["effective_route"] == "EXECUTE_CONTENT_BRIEF", "route=%s" % r4["effective_route"])


def main():
    probe_sufficiency()
    probe_goal_fidelity_readonly()
    probe_cta_not_auto_authorized()
    probe_component_return()
    probe_returns_parse()
    probe_user_view_leak()
    probe_artifact_preserved()
    probe_entry_resolution()
    probe_no_hidden_upstream()
    probe_reference_matrix()
    probe_fidelity_chain()
    probe_provider_binding_honesty()
    probe_canvas_linear_lock_removed()
    probe_all_code_nodes_importable()
    probe_patch_text_fallback()

    n_pass = sum(1 for r in RESULTS if r["result"] == "PASS")
    n_fail = sum(1 for r in RESULTS if r["result"] == "FAIL")
    n_nv = sum(1 for r in RESULTS if r["result"] == "NOT_VERIFIED")

    for r in RESULTS:
        mark = {"PASS": "  ok ", "FAIL": "FAIL!", "NOT_VERIFIED": " nv "}[r["result"]]
        print("%s [%-6s] %s" % (mark, r["probe"], r["name"]))
        if r["result"] != "PASS":
            print("        -> %s" % r["detail"])

    print("=" * 78)
    print("total=%d  PASS=%d  FAIL=%d  NOT_VERIFIED=%d" % (len(RESULTS), n_pass, n_fail, n_nv))
    print("evidence_grade = DETERMINISTIC_NODE_VERIFIED（不是 RUNTIME_VERIFIED）")
    print("=" * 78)

    out = os.path.join(ROOT, "decision-chain", "evidence", "m4",
                       "M4_DETERMINISTIC_PROBE_RESULTS.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as fh:
        json.dump({"evidence_grade": "DETERMINISTIC_NODE_VERIFIED",
                   "runtime_verified": False,
                   "total": len(RESULTS), "pass": n_pass, "fail": n_fail,
                   "not_verified": n_nv, "results": RESULTS},
                  fh, ensure_ascii=False, indent=2)
    print("results -> %s" % os.path.relpath(out, ROOT))
    return 1 if n_fail else 0


if __name__ == "__main__":
    sys.exit(main())
