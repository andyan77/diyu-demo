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


def load_node_code(path, node_id):
    """从已生成的 DSL 里取出代码节点正文并编译成可调用的 main()。
    被测对象就是将要导入 Dify 的那份字节。"""
    with open(path, encoding="utf-8") as fh:
        d = yaml.safe_load(fh)
    nodes = {n["id"]: n for n in d["workflow"]["graph"]["nodes"]}
    code = nodes[node_id]["data"]["code"]
    mod = types.ModuleType("dsl_%s_%s" % (os.path.basename(path), node_id))
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
    consistent = all(
        b[k]["provider_id"] == [t for t in tools if t["data"]["tool_name"] == b[k]["tool_name"]][0]["data"]["provider_id"]
        for k in b)
    check("N-20", "父接缝 provider 绑定与绑定文件逐项一致（重绑机制存在）", consistent,
          "tools=%d pending=%d resolved=%d" % (len(tools), len(pending), len(resolved)))
    RESULTS.append({
        "probe": "N-20", "name": "provider 绑定当前状态",
        "result": "PASS" if len(pending) == 0 else "NOT_VERIFIED",
        "detail": "%d/%d 个 tool 节点仍为 PENDING_PUBLISH。未解析前不得宣称 Runtime 入口可达成立。"
                  % (len(pending), len(tools)),
    })


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
