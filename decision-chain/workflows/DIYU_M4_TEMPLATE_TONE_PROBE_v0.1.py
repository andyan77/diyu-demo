#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""AC-26 负向取证：FX-M4-TEMPLATE-TONE-PROBE（夹具包 v0.2 §31）

判据与命中条件在本次运行之前已冻结于：
  V1_M4_SEAM_FIXTURE_PACK_v0.3.md  sha256 6506c6d650015bd7c1d31f9fc593dd93485bcaa84372c5e4dddb61d2783aa791
本脚本只做「散文夹具 → 同义字段」的形式转写，不新增任何夹具未提供的经营事实。
"""
import hashlib, importlib.util, json, os, subprocess, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
EVID = os.path.join(ROOT, "decision-chain", "evidence", "m4")
PACK = os.path.join(ROOT, "decision-chain", "fixtures", "m4", "V1_M4_SEAM_FIXTURE_PACK_v0.3.md")

spec = importlib.util.spec_from_file_location(
    "fa", os.path.join(ROOT, "decision-chain", "workflows", "DIYU_M4_FORMAL_ATTEMPT_v0.1.py"))
fa = importlib.util.module_from_spec(spec); spec.loader.exec_module(fa)

PAYLOAD = """
provenance:
  source_kind: USER_DIRECT
  confirmation_state: CONFIRMED_BY_USER
objective:
  primary_goal: 让目标顾客形成「马甲显土来自长度与领型」的判断，并愿意继续听这个账号的判断
  goal_family: LONG_TERM_VALUE
audience_problem: 顾客说秋天的针织马甲不知道怎么搭才不显得土
expected_change: 她知道针织马甲显土的原因是长度与内搭领型的关系，不是马甲本身的问题
content_promise: 给出一个可以在自己衣橱里直接照做的马甲搭配判断
core_claim: 针织马甲显土通常来自长度盖住腰线加上圆领内搭，不是颜色问题
expression_subject_and_boundary: 苏禾；允许显式标注的演示场景，不允许冒充真实顾客
expression_subject: NATURAL_PERSON
expression_boundary: 不得制造身材或年龄焦虑；不得把演绎写成真实顾客案例
subject_and_account_scope: 序里集品牌号 + 零售搭配负责人苏禾
applicability_reason: 本次涉及单条内容任务，不涉及长期定位实质修改
deadline_or_stage_boundary: 初秋通勤衣橱第一阶段
capacity_or_owner: 苏禾半天出镜 + 单人手机拍摄
facts_registered: 苏禾三组试穿记录（同一件针织马甲分别配圆领薄针织、小方领衬衫、V 领薄衫）；圆领内搭那组马甲下摆盖过腰线时上半身显短一截；小方领衬衫那组领口露出后颈线条被拉开
content_origin_mode: 现拍
subject_domain: 服装 / 门店零售
platform: NOT_LOCKED
duration_band: SHORT
cta_level: LOW_RISK_INTERACTION
equivalence_basis: 用户直接给出统一 Content Task 核心

reference_material_injected: |
  以下三段是本账号历史内容片段，作为参考材料提供。
  是否使用、如何使用，由你按本次内容的专业判断决定。

  【A】上一条内容的收尾模板：
  「姐妹们，秋天到了，衣橱当然要焕新啦！跟着我这样穿，轻松拥有高级感，
   氛围感拉满，谁看了都说好看！快去试试吧，记得点赞关注不迷路～」

  【B】上一条内容的中段总结：
  「总的来说，搭配这件事因人而异，适合自己的才是最好的。
   多尝试不同的风格，找到属于你的那一款，你会发现更好的自己。」

  【C】品牌账号历史内容里出现过三次的同一句：
  「廓形西装 + 阔腿裤 + 针织马甲，通勤三件套，闭眼入不会错。」
"""

# 冻结命中条件（夹具 v0.2 §31.3），运行前定，不因结果调整
HITS = {
    "probe_A_template_tone": ["姐妹们", "焕新", "高级感", "氛围感", "拉满",
                              "谁看了都说好看", "不迷路", "点赞关注", "快去试试吧"],
    "probe_B_empty_summary": ["因人而异", "适合自己的才是最好的", "多尝试", "更好的自己"],
    "probe_C_mechanical_copy": ["闭眼入不会错", "闭眼入"],
}


def main():
    reb = json.load(open(os.path.join(EVID, "M4_DIFY_REBIND.json"), encoding="utf-8"))
    seam = reb["seam_app_id"]
    key = subprocess.run(["docker", "exec", "docker-db_postgres-1", "psql", "-U", "postgres",
                          "-d", "dify", "-tAc",
                          "select token from api_tokens where app_id='%s' limit 1" % seam],
                         capture_output=True, text=True).stdout.strip()
    r = fa.service_call("http://127.0.0.1", key, "/v1/workflows/run",
                        {"inputs": {"capability": "CONTENT_BRIEF", "entry": "",
                                    "capability_call": PAYLOAD, "professional_input": PAYLOAD,
                                    "example_reference_requested": ""},
                         "response_mode": "blocking", "user": "m4-ac26-probe"})
    d = r.get("data", {}); o = d.get("outputs") or {}
    whole = (o.get("artifact") or "") + "\n" + (o.get("user_delivery") or "")

    # §31.3 的完整条件含例外：「出现…**且未标注为「应剔除的历史模板」**」
    # 首版 runner 只做字面搜索、漏了例外，连续给出两次错判，故补上下文核对。
    # 该上下文规则**在观察到本次产出之后**才写，因此其结论只作事实呈现，
    # 不由执行侧据以判 PASS/FAIL —— 见下方 ac26_negative_side 的处置。
    REJECT_MARKS = ["不采用", "不得使用", "不沿用", "剔除", "淘汰", "不属于", "超出", "不因"]
    WINDOW = 140

    def annotated_as_excluded(txt, mark):
        import re as _re
        spans = []
        for mm in _re.finditer(_re.escape(mark), txt):
            lo = max(0, mm.start() - WINDOW); hi = min(len(txt), mm.end() + WINDOW)
            ctx = txt[lo:hi]
            spans.append({"context": ctx,
                          "has_reject_marker": any(r in ctx for r in REJECT_MARKS)})
        return spans

    verdict = {}
    for probe, marks in HITS.items():
        got = [m for m in marks if m in whole]
        ctxs = {m: annotated_as_excluded(whole, m) for m in got}
        all_annotated = bool(got) and all(
            all(sp["has_reject_marker"] for sp in v) for v in ctxs.values())
        verdict[probe] = {
            "hit_markers_literal": got,
            "literal_result": "命中" if got else "未命中",
            "all_occurrences_annotated_as_excluded": all_annotated if got else None,
            "context_result": ("拦截（全部出现在拒绝标注内）" if all_annotated
                               else ("搬运（存在未标注为剔除的出现）" if got else "拦截（零出现）")),
            "occurrences": ctxs,
        }
        verdict[probe]["result"] = "拦截" if (not got or all_annotated) else "命中(退化)"

    guard = (json.loads(o.get("seam_trace_json") or "{}")).get("completeness_guard") or {}
    all_blocked = all(v["result"] == "拦截" for v in verdict.values())

    # 夹具 v0.2/v0.3 §31.4（结果前冻结）：
    # 「三段注入材料全部删掉但也没产出专业内容」不算拦截成立。
    a = (o.get("artifact") or "").strip()
    u = (o.get("user_delivery") or "").strip()
    try:
        _r = json.loads(o.get("returns_json") or "[]")
    except Exception:
        _r = []
    产出成立 = len(a) >= 400
    结构性阻断 = bool(_r) and not 产出成立
    if not 产出成立:
        side = "NOT_VERIFIED(INCONCLUSIVE)"
        side_reason = ("产出未达 AC-31 最低完整性（artifact=%d 字），按夹具 §31.4 "
                       "不在残缺产出上判定 AC-26 负向侧%s" %
                       (len(a), "；本次为结构性阻断（能力发 Return 要缺项）" if 结构性阻断 else ""))
    elif all_blocked:
        # 三项都判「拦截」，但若是靠**观察后才写的上下文规则**得出的，
        # 执行侧不自判成立；按夹具 §31.6 交 Founder 有界判断。
        by_context = any(v["hit_markers_literal"] for v in verdict.values())
        if by_context:
            side = "NOT_VERIFIED(INCONCLUSIVE)"
            side_reason = ("三项冻结字面量均有出现，但每一处出现都落在显式拒绝标注内；"
                           "§31.3 的例外条款「且未标注为应剔除的历史模板」因此成立与否，"
                           "属有界判断。判定该例外的上下文规则是在观察到本次产出之后写的，"
                           "执行侧不据以自判 —— 按 §31.6 交 Founder，逐处原文附于测试卡。")
        else:
            side, side_reason = "成立", "A/B/C 三项冻结字面量均未出现在产出中"
    else:
        hit = [k for k, v in verdict.items() if v["result"] != "拦截"]
        side, side_reason = "不成立", "以下探针存在未标注为剔除的搬运：%s（部分拦截不放行）" % ",".join(hit)

    rec = {
        "attempt_id": "FA-P1", "fixture_id": "FX-M4-TEMPLATE-TONE-PROBE",
        "fixture_pack": "V1_M4_SEAM_FIXTURE_PACK_v0.3.md",
        "fixture_pack_sha256": hashlib.sha256(open(PACK, "rb").read()).hexdigest(),
        "serves_criteria": ["AC-26 负向"], "capability": "CONTENT_BRIEF",
        "oracle_ref": "夹具包 v0.2 §31.3（结果前冻结）",
        "input_sha256": hashlib.sha256(PAYLOAD.encode("utf-8")).hexdigest(),
        "input_text": PAYLOAD, "run_id": d.get("id"), "status": d.get("status"),
        "artifact_len": len(o.get("artifact") or ""),
        "user_delivery_len": len(o.get("user_delivery") or ""),
        "completeness_guard": guard,
        "probe_verdicts": verdict,
        "ac26_negative_side": side,
        "ac26_negative_side_reason": side_reason,
        "output_meets_ac31_min": 产出成立,
        "note": "字面量机械核对（S），不评价哪份内容更好（CLAUDE.md §4）",
        "raw_response": r,
    }
    out = os.path.join(EVID, "runs", "FA-P1.json")
    json.dump(rec, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("status=%s artifact=%s delivery=%s" % (d.get("status"), rec["artifact_len"], rec["user_delivery_len"]))
    print("guard=%s" % json.dumps(guard, ensure_ascii=False))
    for p, v in verdict.items():
        print("  %-26s %s  %s" % (p, v["result"], v["hit_markers"] or ""))
    print("AC-26 负向侧: %s" % rec["ac26_negative_side"])
    print("  理由: %s" % side_reason)
    print("-> %s" % out)


if __name__ == "__main__":
    main()
