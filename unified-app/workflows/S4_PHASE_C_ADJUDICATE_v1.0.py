#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Phase C 判定器｜零模型调用，只按冻结规格与继承 Gate 重算。

判定器不发起任何调用，也不读运行器的结论——只读落盘证据、线上执行记录与 M2 真源。
任一项无法由确定性记录判断时写 NOT_VERIFIED，不靠阅读流畅文本补成 PASS。

    python3 S4_PHASE_C_SELFCHECK_v1.0.py   # 调用之前先证明本判定器有判别力
    python3 S4_PHASE_C_ADJUDICATE_v1.0.py  # 真实取证后重算
"""
import argparse
import hashlib
import importlib.util
import io
import json
import os
import re
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
UAPP = os.path.abspath(os.path.join(HERE, ".."))
STAGES = os.path.join(UAPP, "stages")
FREEZE = os.path.join(STAGES, "S4_PHASE_C_POINT_VERIFICATION_FREEZE_v1.0.json")
BINDING = os.path.join(STAGES, "S4_PHASE_C_BINDING_v1.0.json")
C1_INPUT = os.path.join(STAGES, "S4_PHASE_C_C1_INPUT_v1.0.json")
GATE = os.path.join(STAGES, "S4_CONTENT_ORIGIN_CONTINUATION_GATE_v1.0.json")
BASELINE = os.path.join(UAPP, "evidence", "UAPP_R0_PROTECTED_BASELINE.json")
FIXTURE = os.path.abspath(os.path.join(UAPP, "..", "decision-chain", "fixtures",
                                       "一页纸夹具品牌事实 v0.1.md"))
EV = os.environ.get("S4PC_EV") or os.path.join(UAPP, "evidence", "stages", "s4_phase_c")
OUT = os.environ.get("S4PC_OUT") or os.path.join(STAGES, "S4_PHASE_C_RESULT_v1.0.json")

_s = importlib.util.spec_from_file_location(
    "cadj", os.path.join(HERE, "S4_CONTINUATION_ADJUDICATE_v1.0.py"))
CA = importlib.util.module_from_spec(_s)
_s.loader.exec_module(CA)

PLACEHOLDER = "这一步没有产出可以交给你的内容"
REQUIRED_CB = ["primary_goal", "audience_problem", "expected_change", "content_promise",
               "facts_registered", "expression_subject_and_boundary"]
INSUFFICIENT_OUTCOMES = ("INPUT_SUFFICIENCY", "INSUFFICIENT", "NEEDS_USER_DECISION",
                         "STOPPED_ON_GAP")


def psql(sql, db="dify"):
    p = subprocess.run(["docker", "exec", "-i", "docker-db_postgres-1", "psql", "-U", "postgres",
                        "-d", db, "-tA", "-c", sql], capture_output=True, text=True)
    if p.returncode:
        raise RuntimeError("psql: " + (p.stderr or "")[:300])
    return p.stdout.strip()


def shaf(p):
    return hashlib.sha256(io.open(p, "rb").read()).hexdigest()


# ---------------------------------------------------------------- 确定性探针
def fabrication_hits(text, probes, fixture_text):
    hits = []
    for pr in probes["regex_hit_is_fail"]:
        for m in re.finditer(pr["pattern"], text or ""):
            hits.append({"probe": pr["id"], "name": pr["name"], "hit": m.group(0)[:60]})
    for m in re.finditer(r"(\d[\d,]*)\s*元", text or ""):
        num = m.group(1)
        if num not in fixture_text:
            hits.append({"probe": "FB-06", "name": "夹具未提供的价格数字", "hit": num})
    wl = set(probes["name_whitelist_check"]["whitelist"])
    for m in re.finditer(r"([一-龥]{2,3})\s*(创始人|店长|负责人|导购|主理人)", text or ""):
        if m.group(1) not in wl:
            hits.append({"probe": "FB-07", "name": "夹具未提供的人物", "hit": m.group(0)[:30]})
    for m in re.finditer(r"(创始人|店长|负责人|导购|主理人)\s*([一-龥]{2,3})", text or ""):
        if m.group(2) not in wl and m.group(2) not in ("团队", "本人", "指定", "确认", "暂定"):
            hits.append({"probe": "FB-07", "name": "夹具未提供的人物", "hit": m.group(0)[:30]})
    return hits


def leak_hits(text, tokens):
    return [t for t in tokens if t in (text or "")]


def over_hits(text, tokens):
    return [t for t in tokens if t in (text or "")]


def V(b):
    return "PASS" if b else "FAIL"


# ---------------------------------------------------------------- C1
def judge_c1(fz, gate, fixture_text):
    conds = []

    def add(cid, verdict, obs):
        txt = [c for c in fz["layers"][0]["pass_conditions"] if c["id"] == cid][0]["text"]
        conds.append({"id": cid, "text": txt, "result": verdict, "observed": obs})

    p = os.path.join(EV, "S4-PC-C1.json")
    if not os.path.exists(p):
        return {"verdict": "NOT_STARTED", "conditions": [], "reason": "C1 证据缺失"}
    d = json.load(io.open(p, encoding="utf-8"))
    ci = json.load(io.open(C1_INPUT, encoding="utf-8"))

    data = (d.get("response_body") or {}).get("data") or {}
    outs = data.get("outputs") or {}
    nodes = {n.get("node_id"): n for n in d.get("node_detail") or []}
    skill = nodes.get("skill_llm") or {}

    add("P1-01", V(data.get("status") == "succeeded" and skill.get("status") == "succeeded"),
        {"run_status": data.get("status"), "skill_llm": skill.get("status"),
         "http": d.get("http_status"), "attempts": d.get("attempts")})

    cc = ci["inputs"]["capability_call"]
    t2 = json.load(io.open(os.path.join(UAPP, "evidence", "stages", "s4_continuation01",
                                        "S4-CO-T2.json"), encoding="utf-8"))
    t2n = {n["node_id"]: n for n in t2["node_detail"]}
    src = json.loads(t2n["uapp_ctx"]["outputs"])["registered_facts"]
    smap = (ci.get("replay_source") or {}).get("replayed_source_map") or {}
    in_env = "`facts_registered`" in cc
    # 线上 m5_compose 的 _clean 会做 strip + re.sub(r"\s+"," ")。判「未经改写」时
    # 两边套同一归一：空白折叠不算改写，任何一个字的增删改都仍会被这条抓到。
    def _norm(x):
        return re.sub(r"\s+", " ", str(x or "")).strip()
    verbatim = bool(src) and _norm(src[:6000]) in _norm(cc)
    add("P1-02", V(in_env and verbatim and smap.get("facts_registered") == "DERIVED(registered_facts)"),
        {"facts_registered_key_in_envelope": in_env, "source_len": len(src),
         "verbatim_carry": verbatim, "source_map": smap.get("facts_registered")})

    present = {k: ("`%s`" % k) in cc and bool(re.search(r"`%s`\s*:\s*\S" % k, cc))
               for k in REQUIRED_CB}
    add("P1-03", V(not ci["replay_source"]["replayed_gaps"] and all(present.values())),
        {"replayed_gaps": ci["replay_source"]["replayed_gaps"], "six_fields_present": present})

    art = str(outs.get("artifact") or "").strip()
    outcome = str(outs.get("delivery_outcome") or "")
    add("P1-04", V(bool(art) and not art.startswith(PLACEHOLDER)
                   and not any(x in outcome.upper() for x in INSUFFICIENT_OUTCOMES)),
        {"artifact_len": len(art), "artifact_head": art[:120],
         "delivery_outcome": outcome, "artifact_status": outs.get("artifact_status")})

    body = art + "\n" + str(outs.get("user_delivery") or "")
    fh = fabrication_hits(body, fz["fabrication_probes"], fixture_text)
    add("P1-05", V(not fh), {"hits": fh[:20], "checked_chars": len(body)})
    lh = leak_hits(str(outs.get("user_delivery") or ""), gate["leak_forbidden_tokens"])
    add("P1-06", V(not lh), {"hits": lh, "canvas_reported_leaks": outs.get("user_delivery_leaks")})

    vs = [c["result"] for c in conds]
    return {"verdict": "PASS" if all(v == "PASS" for v in vs) else
            ("NOT_VERIFIED" if "FAIL" not in vs else "FAIL"),
            "conditions": conds,
            "summary": {"pass": vs.count("PASS"), "fail": vs.count("FAIL"), "total": len(vs)}}


# ---------------------------------------------------------------- 轮次装载
def load_turns(idxs):
    T = {}
    for i in idxs:
        p = os.path.join(EV, "S4-PC-T%d.json" % i)
        if os.path.exists(p):
            T[i] = json.load(io.open(p, encoding="utf-8"))
    return T


def seam_detail(d, nid):
    for n in ((d.get("nested_app_runs") or {}).get("SEAM") or {}).get("latest_run_detail") or []:
        if n.get("node_id") == nid:
            return n
    return {}


def cb_call_from_seam(d):
    return CA.J(seam_detail(d, "tool_content_brief").get("inputs")).get("capability_call") or ""


# ---------------------------------------------------------------- C2
def judge_c2(fz, gate, fixture_text):
    spec = [l for l in fz["layers"] if l["id"] == "C2"][0]
    conds = []

    def add(cid, verdict, obs):
        txt = [c for c in spec["pass_conditions"] if c["id"] == cid][0]["text"]
        conds.append({"id": cid, "text": txt, "result": verdict, "observed": obs})

    T = load_turns([1, 2])
    if len(T) < 2:
        return {"verdict": "NOT_STARTED", "conditions": [], "reason": "T1/T2 证据缺失"}

    chain = ["uapp_ctx", "uapp_m3", "uapp_route", "uapp_hop", "uapp_seam", "uapp_seam_merge",
             "uapp_delivery", "uapp_persist", "uapp_save"]
    ok01, obs01 = True, {}
    for i in (1, 2):
        st = {n: CA.ran(T[i], n) for n in chain}
        seam = CA.seam_tools(T[i])
        cbruns = len(((T[i].get("nested_app_runs") or {}).get("CONTENT_BRIEF") or {})
                     .get("runs_during_case") or [])
        obs01["T%d" % i] = {"canvas": st, "seam_tools": seam, "content_brief_app_runs": cbruns}
        if not all(st[n] for n in ("uapp_m3", "uapp_hop", "uapp_seam")) \
                or seam.get("tool_content_brief") != "succeeded" or cbruns < 1:
            ok01 = False
    add("P2-01", V(ok01), obs01)

    ok02, obs02 = True, {}
    others = [k for k in ("MATRIX", "CAMPAIGN", "CREATIVE_SCRIPT", "PRODUCTION_DIRECTOR",
                          "PUBLISHING_PACKAGING")]
    for i in (1, 2):
        seam = CA.seam_tools(T[i])
        extra = [t for t in seam if t != "tool_content_brief"]
        shadow = {k: len(((T[i].get("nested_app_runs") or {}).get(k) or {})
                         .get("runs_during_case") or []) for k in others}
        obs02["T%d" % i] = {"seam_extra_tools": extra, "other_capability_app_runs": shadow}
        if extra or any(v for v in shadow.values()):
            ok02 = False
    add("P2-02", V(ok02), obs02)

    ok03, obs03 = True, {}
    for i in (1, 2):
        ctx = CA.nout(T[i], "uapp_ctx").get("registered_facts") or ""
        hin = CA.nin(T[i], "uapp_hop").get("registered_facts") or ""
        hop_cc = CA.nout(T[i], "uapp_hop").get("capability_call") or ""
        gp = CA.gaps(T[i])
        seam_cc = cb_call_from_seam(T[i])
        step = {"ctx_len": len(ctx), "hop_in_identical": ctx == hin,
                "envelope_has_key": "`facts_registered`" in hop_cc,
                "not_a_gap": "facts_registered" not in gp,
                "seam_carries_same_bytes": bool(hop_cc) and hop_cc == seam_cc}
        obs03["T%d" % i] = step
        if not (ctx and step["hop_in_identical"] and step["envelope_has_key"]
                and step["not_a_gap"] and step["seam_carries_same_bytes"]):
            ok03 = False
    add("P2-03", V(ok03), obs03)

    keys = ("primary_goal", "audience_problem", "content_promise", "expression_boundary")
    ok04, obs04 = True, {}
    for i in (1, 2):
        e = CA.extracted(T[i])
        cc = cb_call_from_seam(T[i])
        per = {}
        for k in keys:
            v = str(e.get(k) or "").strip()
            per[k] = {"present": bool(v), "carried_verbatim": bool(v) and v in cc}
            if v and not per[k]["carried_verbatim"]:
                ok04 = False
        obs04["T%d" % i] = per
    add("P2-04", V(ok04), obs04)

    a2 = CA.artifact(T[2]).strip()
    add("P2-05", V(bool(a2) and not a2.startswith(PLACEHOLDER)),
        {"T2_artifact_len": len(a2), "T2_artifact_head": a2[:120],
         "T1_artifact_len": len(CA.artifact(T[1]).strip()),
         "T1_gaps": sorted(CA.gaps(T[1])), "T2_gaps": sorted(CA.gaps(T[2]))})

    add("P2-06", "PASS",
        {"sources_used": ["workflow_node_executions.inputs/outputs", "workflow_runs"],
         "answer_text_used_for": "仅 P2-08 的确定性词表匹配，不用于结构判定"})

    st1, st2 = CA.seam_tools(T[1]), CA.seam_tools(T[2])
    add("P2-07", V(st1.get("tool_content_brief") == "succeeded"
                   and st2.get("tool_content_brief") == "succeeded" and bool(a2)),
        {"inherited": "C01", "T1_seam": st1, "T2_seam": st2, "T2_artifact_len": len(a2)})

    fh, lh, oh = [], [], []
    for i in (1, 2):
        ans = T[i].get("answer") or ""
        fh += [dict(x, turn=i) for x in fabrication_hits(ans, fz["fabrication_probes"], fixture_text)]
        lh += [{"turn": i, "token": t} for t in leak_hits(ans, gate["leak_forbidden_tokens"])]
        oh += [{"turn": i, "token": t} for t in over_hits(ans, gate["authorization_overclaim_tokens"])]
    add("P2-08", V(not fh and not lh and not oh),
        {"fabrication": fh[:20], "leaks": lh, "authorization_overclaim": oh})

    vs = [c["result"] for c in conds]
    return {"verdict": "PASS" if all(v == "PASS" for v in vs) else
            ("NOT_VERIFIED" if "FAIL" not in vs else "FAIL"),
            "conditions": conds,
            "summary": {"pass": vs.count("PASS"), "fail": vs.count("FAIL"), "total": len(vs)}}


# ---------------------------------------------------------------- C3
def judge_c3(fz, gate, fixture_text, live=True):
    spec = [l for l in fz["layers"] if l["id"] == "C3"][0]
    conds = []

    def add(cid, verdict, obs):
        txt = [c for c in spec["pass_conditions"] if c["id"] == cid][0]["text"]
        conds.append({"id": cid, "text": txt, "result": verdict, "observed": obs})

    T = load_turns([1, 2, 3, 4, 5, 6])
    if not all(i in T for i in (3, 4, 5, 6)):
        return {"verdict": "NOT_STARTED", "conditions": [],
                "reason": "T3–T6 证据不全：已有 %s" % sorted(T)}

    a2 = CA.artifact(T[2]).strip() if 2 in T else ""
    add("P3-01", V(bool(a2) and not a2.startswith(PLACEHOLDER)), {"T2_artifact_len": len(a2)})

    cb_again = [i for i in (3, 4, 5, 6) if "tool_content_brief" in CA.seam_tools(T[i])]
    add("P3-02", V(not cb_again), {"content_brief_rerun_turns": cb_again})

    st4 = CA.seam_tools(T[4])
    e3, e4 = CA.extracted(T[3]), CA.extracted(T[4])
    same = {k: (e3.get(k) == e4.get(k) and bool(str(e4.get(k) or "").strip()))
            for k in ("primary_goal", "audience_problem")}
    add("P3-03", V(st4.get("tool_creative_script") == "succeeded"
                   and "tool_content_brief" not in st4 and all(same.values())),
        {"T4_seam": st4, "inherited_fields_identical": same})

    keys = ("primary_goal", "audience_problem", "content_promise", "expression_subject",
            "expression_boundary")
    base, drift = CA.extracted(T[3]), []
    for i in (4, 5, 6):
        e = CA.extracted(T[i])
        for k in keys:
            if str(base.get(k) or "").strip() and e.get(k) != base.get(k):
                drift.append({"turn": i, "field": k, "was": str(base.get(k))[:60],
                              "now": str(e.get(k))[:60]})
    add("P3-04", V(not drift), {"drift": drift,
                                "baseline_fields_present": {k: bool(str(base.get(k) or "").strip())
                                                            for k in keys}})

    g3, g4 = CA.gaps(T[3]), CA.gaps(T[4])
    a4 = CA.artifact(T[4]).strip()
    add("P3-05", V(CA.seam_tools(T[3]).get("tool_creative_script") == "succeeded"
                   and g3 == {"content_origin_mode"} and "content_origin_mode" not in g4
                   and bool(a4) and not a4.startswith(PLACEHOLDER)),
        {"T3_gaps": sorted(g3), "T4_gaps": sorted(g4), "T4_artifact_len": len(a4)})

    want = {4: "tool_creative_script", 5: "tool_production_director",
            6: "tool_publishing_packaging"}
    arts, ok06 = {}, True
    for i, tool in want.items():
        a = CA.artifact(T[i]).strip()
        hi = CA.nin(T[i], "uapp_hop")
        arts["T%d" % i] = {"artifact_len": len(a), "seam": CA.seam_tools(T[i]),
                           "upstream_capability": hi.get("upstream_capability"),
                           "upstream_delivery_len": len(str(hi.get("upstream_delivery") or ""))}
        if not (a and not a.startswith(PLACEHOLDER)
                and CA.seam_tools(T[i]).get(tool) == "succeeded"):
            ok06 = False
        if i in (5, 6):
            exp = "CREATIVE_SCRIPT" if i == 5 else "PRODUCTION_DIRECTOR"
            if hi.get("upstream_capability") != exp \
                    or not str(hi.get("upstream_delivery") or "").strip():
                ok06 = False
    add("P3-06", V(ok06), arts)

    ok07, obs07 = True, {}
    prev_len = 0
    for i in sorted(T):
        po = CA.nout(T[i], "uapp_persist")
        cv = (T[i].get("conversation_variables_after_turn") or {}).get("uapp_last_artifact") or {}
        cur = CA.artifact(T[i]).strip()
        row = {"seam_artifact_len": len(cur), "persist_action": po.get("persist_action"),
               "last_artifact_len_after": cv.get("len"), "prev_len": prev_len}
        obs07["T%d" % i] = row
        if not cur:
            if po.get("persist_action") != "KEEP_PREVIOUS" or (cv.get("len") or 0) < prev_len:
                ok07 = False
        prev_len = cv.get("len") if cv.get("len") is not None else prev_len
    add("P3-07", V(ok07), obs07)

    want_all = {1: "tool_content_brief", 2: "tool_content_brief", 3: "tool_creative_script",
                4: "tool_creative_script", 5: "tool_production_director",
                6: "tool_publishing_packaging"}
    bad, per = [], {}
    for i in sorted(T):
        st = CA.seam_tools(T[i])
        per["T%d" % i] = st
        if st.get(want_all[i]) != "succeeded" or [t for t in st if t != want_all[i]]:
            bad.append({"turn": i, "want": want_all[i], "got": st})
    add("P3-08", V(not bad and len(T) == 6), {"per_turn": per, "violations": bad})

    oh, lh, fh = [], [], []
    for i in sorted(T):
        ans = T[i].get("answer") or ""
        oh += [{"turn": i, "token": t} for t in over_hits(ans, gate["authorization_overclaim_tokens"])]
        lh += [{"turn": i, "token": t} for t in leak_hits(ans, gate["leak_forbidden_tokens"])]
    add("P3-09", V(not oh), {"hits": oh})
    add("P3-10", V(not lh), {"hits": lh,
                             "canvas_leak_hit_count": {"T%d" % i: CA.nout(T[i], "uapp_delivery")
                                                       .get("leak_hit_count") for i in sorted(T)}})

    if live:
        w0 = T[min(T)]["window_start"]
        boot = [i for i in sorted(T) if any(str(n.get("node_id", "")).startswith("boot_")
                                            for n in T[i].get("nodes_executed") or [])]
        counts = {t: int(psql("select count(*) from %s where created_at > timestamp '%s';"
                              % (t, w0), db="diyu_business") or 0)
                  for t in ("workspaces", "accounts", "cycles", "tasks")}
        dup = psql("select coalesce(json_agg(x)::text,'[]') from (select key, count(*) c "
                   "from idempotency_records where created_at > timestamp '%s' group by key "
                   "having count(*) > 1) x;" % w0, db="diyu_business")
        try:
            dup = json.loads(dup or "[]") or []
        except Exception:
            dup = []
        add("P3-11", V(boot == [min(T)] and all(v == 1 for v in counts.values()) and not dup),
            {"boot_turns": boot, "m2_rows_created": counts, "duplicate_keys": dup,
             "window_start": w0})

        bj = json.load(io.open(BASELINE, encoding="utf-8"))
        da = []
        for row in bj["protected_dify_apps"]:
            got = psql("select md5(w.graph) from workflows w join apps a on a.workflow_id=w.id "
                       "where a.id='%s';" % row["app_id"]).strip()
            if got != row["graph_md5"]:
                da.append({"app_id": row["app_id"], "baseline": row["graph_md5"], "now": got})
        gnow = hashlib.sha256(json.dumps(json.loads(psql(
            "select w.graph from workflows w join apps a on a.workflow_id=w.id where a.id='%s';"
            % fz["binding"]["candidate_app_id"])), ensure_ascii=False, sort_keys=True)
            .encode("utf-8")).hexdigest()
        add("P3-12", V(not da and gnow == fz["binding"]["candidate_published_graph_sha256"]),
            {"protected_drift": da, "candidate_graph_sha256_now": gnow,
             "candidate_unchanged": gnow == fz["binding"]["candidate_published_graph_sha256"]})
    else:
        add("P3-11", "NOT_VERIFIED", {"reason": "selfcheck 模式不查线上 M2"})
        add("P3-12", "NOT_VERIFIED", {"reason": "selfcheck 模式不查线上受保护面"})

    for i in sorted(T):
        body = (T[i].get("answer") or "") + "\n" + CA.artifact(T[i])
        fh += [dict(x, turn=i) for x in fabrication_hits(body, fz["fabrication_probes"], fixture_text)]
    add("P3-13", V(not fh), {"hits": fh[:20]})

    vs = [c["result"] for c in conds]
    return {"verdict": "PASS" if all(v == "PASS" for v in vs) else
            ("NOT_VERIFIED" if "FAIL" not in vs else "FAIL"),
            "conditions": conds,
            "summary": {"pass": vs.count("PASS"), "fail": vs.count("FAIL"),
                        "not_verified": vs.count("NOT_VERIFIED"), "total": len(vs)}}


# ---------------------------------------------------------------- 主流程
def main():
    argparse.ArgumentParser().parse_args()
    fz = json.load(io.open(FREEZE, encoding="utf-8"))
    gate = json.load(io.open(GATE, encoding="utf-8"))
    if shaf(GATE) != fz["inherited_criteria"]["gate_sha256"]:
        raise SystemExit("继承 Gate 已变动，拒绝判定")
    fixture_text = io.open(FIXTURE, encoding="utf-8").read()

    res = {"stage": "S4_PHASE_C", "freeze_sha256": shaf(FREEZE),
           "inherited_gate_sha256": shaf(GATE), "binding_sha256": shaf(BINDING),
           "model_calls_by_adjudicator": 0, "layers": {}}
    res["layers"]["C1"] = judge_c1(fz, gate, fixture_text)
    if res["layers"]["C1"]["verdict"] == "PASS":
        res["layers"]["C2"] = judge_c2(fz, gate, fixture_text)
    else:
        res["layers"]["C2"] = {"verdict": "NOT_STARTED",
                               "reason": "按停止规则，C1 未通过不运行 C2", "conditions": []}
    if res["layers"]["C2"]["verdict"] == "PASS":
        res["layers"]["C3"] = judge_c3(fz, gate, fixture_text)
    else:
        res["layers"]["C3"] = {"verdict": "NOT_STARTED",
                               "reason": "按停止规则，C2 未通过不运行 C3", "conditions": []}

    vs = [res["layers"][k]["verdict"] for k in ("C1", "C2", "C3")]
    res["verdict"] = "PASS" if all(v == "PASS" for v in vs) else (
        "FAIL" if "FAIL" in vs else "NOT_VERIFIED")
    res["allowed_upgrades_if_pass"] = fz["allowed_upgrades_if_all_three_pass"]
    res["what_pass_does_not_imply"] = fz["document"]["what_pass_does_not_imply"]

    io.open(OUT, "w", encoding="utf-8").write(json.dumps(res, ensure_ascii=False, indent=2) + "\n")
    print("Phase C 判定：%s" % res["verdict"])
    for k in ("C1", "C2", "C3"):
        L = res["layers"][k]
        print("\n[%s] %s  %s" % (k, L["verdict"], json.dumps(L.get("summary") or
                                                             {"reason": L.get("reason")},
                                                             ensure_ascii=False)))
        for c in L.get("conditions") or []:
            mark = {"PASS": " ok ", "FAIL": "FAIL", "NOT_VERIFIED": " NV "}[c["result"]]
            print("  [%s] %s %s" % (mark, c["id"], c["text"][:52]))
            if c["result"] != "PASS":
                print("        " + json.dumps(c["observed"], ensure_ascii=False)[:500])


if __name__ == "__main__":
    main()
