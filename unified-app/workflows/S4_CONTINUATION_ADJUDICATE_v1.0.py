#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""S4 后继窄验证判定器｜零模型调用，只按冻结 Gate 的 12 项条件重算。

判定器不发起任何调用，也不读运行器的结论——只读落盘证据、线上执行记录与 M2 真源。
任一项无法由确定性记录判断时写 NOT_VERIFIED，不靠阅读流畅文本补成 PASS。
"""
import hashlib
import io
import json
import os
import re
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
GATE = os.path.join(HERE, "..", "stages", "S4_CONTENT_ORIGIN_CONTINUATION_GATE_v1.0.json")
INPUTS = os.path.join(HERE, "..", "stages", "S4_CONTENT_ORIGIN_CONTINUATION_INPUTS_v1.0.json")
BASELINE = os.path.join(HERE, "..", "evidence", "UAPP_R0_PROTECTED_BASELINE.json")
# 证据目录与判定书路径可被环境变量改写——这是为了在**运行之前**用合成正负控制
# 检验判定器本身有没有判别力（能不能把假的判成 FAIL）。真实取证一律用默认路径。
EV = os.environ.get("S4CO_EV") or os.path.join(HERE, "..", "evidence", "stages",
                                               "s4_continuation01")
OUT = os.environ.get("S4CO_OUT") or os.path.join(
    HERE, "..", "stages", "S4_CONTENT_ORIGIN_CONTINUATION_RESULT_v1.0.json")

ALL_TOOLS = ["tool_matrix", "tool_campaign", "tool_content_brief", "tool_creative_script",
             "tool_production_director", "tool_publishing_packaging"]
PLACEHOLDER = "这一步没有产出可以交给你的内容"


def psql(sql, db="dify"):
    p = subprocess.run(["docker", "exec", "-i", "docker-db_postgres-1", "psql", "-U", "postgres",
                        "-d", db, "-tA", "-c", sql], capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError("psql: " + (p.stderr or "")[:300])
    return p.stdout.strip()


def J(x):
    if isinstance(x, str):
        try:
            return json.loads(x)
        except Exception:
            return {}
    return x if isinstance(x, dict) else {}


def node(d, nid):
    for n in d.get("node_detail") or []:
        if n.get("node_id") == nid:
            return n
    return {}


def nout(d, nid):
    return J(node(d, nid).get("outputs"))


def nin(d, nid):
    return J(node(d, nid).get("inputs"))


def ran(d, nid):
    for n in d.get("nodes_executed") or []:
        if n.get("node_id") == nid:
            return n.get("status") == "succeeded"
    return False


def seam_tools(d):
    rows = ((d.get("nested_app_runs") or {}).get("SEAM") or {}).get("latest_run_nodes") or []
    return {n.get("node_id"): n.get("status") for n in rows if str(n.get("node_id", "")).startswith("tool_")}


def gaps(d):
    """本轮的精确缺口集合：hop 抽取缺口 ∪ Seam Return 里的 precise_gap。"""
    s = set()
    txt = str(nout(d, "uapp_hop").get("extraction_gaps_text") or "").strip()
    for x in re.split(r"[,\s、;；]+", txt):
        if x:
            s.add(x)
    rj = str(nout(d, "uapp_seam").get("returns_json") or "")
    for m in re.finditer(r'"precise_gap"\s*:\s*"([^"]*)"', rj):
        if m.group(1):
            s.add(m.group(1))
    return s


def artifact(d):
    return str((nout(d, "uapp_seam_merge").get("artifact") or {}).get("output") or "")


def extracted(d):
    return J(nout(d, "uapp_hop").get("extracted_json"))


def main():
    g = json.load(io.open(GATE, encoding="utf-8"))
    gsha = hashlib.sha256(io.open(GATE, "rb").read()).hexdigest()
    isha = hashlib.sha256(io.open(INPUTS, "rb").read()).hexdigest()
    T = {}
    missing = []
    for i in range(1, 7):
        p = os.path.join(EV, "S4-CO-T%d.json" % i)
        if not os.path.exists(p):
            missing.append(os.path.basename(p))
            continue
        d = json.load(io.open(p, encoding="utf-8"))
        if d.get("gate_sha256") != gsha:
            raise SystemExit("证据绑定的判据版本不一致，拒绝判定：" + p)
        T[i] = d

    res = {"stage": "S4_CONTENT_ORIGIN_CONTINUATION", "gate_sha256": gsha,
           "inputs_sha256": isha, "model_calls_by_adjudicator": 0,
           "turns_present": sorted(T), "turns_missing": missing, "conditions": []}

    def add(cid, verdict, observed):
        text = [c for c in g["pass_conditions"] if c["id"] == cid][0]["text"]
        res["conditions"].append({"id": cid, "text": text, "result": verdict,
                                  "observed": observed})

    def V(b):
        return "PASS" if b else "FAIL"

    # ---------- C01 ----------
    if 1 in T and 2 in T:
        st1, st2 = seam_tools(T[1]), seam_tools(T[2])
        a2 = artifact(T[2])
        ok = (st1.get("tool_content_brief") == "succeeded"
              and st2.get("tool_content_brief") == "succeeded" and bool(a2.strip()))
        add("C01", V(ok), {"T1_seam": st1, "T2_seam": st2, "T2_artifact_len": len(a2),
                           "T1_gaps": sorted(gaps(T[1])), "T2_gaps": sorted(gaps(T[2]))})
    else:
        add("C01", "NOT_VERIFIED", {"reason": "T1/T2 证据缺失"})

    # ---------- C02 ----------
    if 3 in T:
        st = seam_tools(T[3])
        gp = gaps(T[3])
        ok = st.get("tool_creative_script") == "succeeded" and gp == {"content_origin_mode"}
        add("C02", V(ok), {"seam": st, "gaps": sorted(gp)})
    else:
        add("C02", "NOT_VERIFIED", {"reason": "T3 证据缺失"})

    # ---------- C03 ----------
    if 3 in T and 4 in T:
        st = seam_tools(T[4])
        e3, e4 = extracted(T[3]), extracted(T[4])
        same = {k: (e3.get(k) == e4.get(k) and bool(str(e4.get(k) or "").strip()))
                for k in ("primary_goal", "audience_problem")}
        ok = (st.get("tool_creative_script") == "succeeded"
              and "tool_content_brief" not in st and all(same.values()))
        add("C03", V(ok), {"T4_seam": st, "inherited_fields_identical": same,
                           "T4_primary_goal_head": str(e4.get("primary_goal") or "")[:80],
                           "T4_audience_problem_head": str(e4.get("audience_problem") or "")[:80]})
    else:
        add("C03", "NOT_VERIFIED", {"reason": "T3/T4 证据缺失"})

    # ---------- C04 ----------
    if 4 in T:
        gp = gaps(T[4])
        a4 = artifact(T[4]).strip()
        ok = ("content_origin_mode" not in gp) and bool(a4) and not a4.startswith(PLACEHOLDER)
        add("C04", V(ok), {"gaps": sorted(gp), "artifact_len": len(a4),
                           "artifact_head": a4[:120],
                           "outcome": nout(T[4], "uapp_seam").get("business_delivery_outcome")})
    else:
        add("C04", "NOT_VERIFIED", {"reason": "T4 证据缺失"})

    # ---------- C05 / C06 ----------
    for cid, idx, up_cap, tool in (("C05", 5, "CREATIVE_SCRIPT", "tool_production_director"),
                                   ("C06", 6, "PRODUCTION_DIRECTOR", "tool_publishing_packaging")):
        if idx not in T:
            add(cid, "NOT_VERIFIED", {"reason": "T%d 证据缺失" % idx})
            continue
        hi = nin(T[idx], "uapp_hop")
        uc = str(hi.get("upstream_capability") or "")
        ud = str(hi.get("upstream_delivery") or "")
        st = seam_tools(T[idx])
        a = artifact(T[idx]).strip()
        ok = (uc == up_cap and bool(ud.strip()) and st.get(tool) == "succeeded"
              and bool(a) and not a.startswith(PLACEHOLDER))
        add(cid, V(ok), {"upstream_capability": uc, "upstream_delivery_len": len(ud),
                         "seam": st, "artifact_len": len(a), "gaps": sorted(gaps(T[idx]))})

    # ---------- C07 ----------
    want = {1: "tool_content_brief", 2: "tool_content_brief", 3: "tool_creative_script",
            4: "tool_creative_script", 5: "tool_production_director",
            6: "tool_publishing_packaging"}
    obs, bad = {}, []
    for i in sorted(T):
        st = seam_tools(T[i])
        obs["T%d" % i] = st
        extra = [t for t in st if t != want[i]]
        if st.get(want[i]) != "succeeded" or extra:
            bad.append({"turn": i, "want": want[i], "got": st})
    add("C07", ("NOT_VERIFIED" if len(T) < 6 else V(not bad)), {"per_turn": obs, "violations": bad})

    # ---------- C08 ----------
    later = {i: seam_tools(T[i]) for i in sorted(T) if i >= 3}
    cb_again = [i for i, st in later.items() if "tool_content_brief" in st]
    keys = ("primary_goal", "audience_problem", "expression_subject")
    base = extracted(T[3]) if 3 in T else {}
    drift = []
    for i in sorted(later):
        e = extracted(T[i])
        for k in keys:
            if str(base.get(k) or "").strip() and e.get(k) != base.get(k):
                drift.append({"turn": i, "field": k, "was": str(base.get(k))[:60],
                              "now": str(e.get(k))[:60]})
    add("C08", ("NOT_VERIFIED" if len(T) < 6 else V(not cb_again and not drift)),
        {"content_brief_rerun_turns": cb_again, "confirmed_fact_drift": drift})

    # ---------- C09 / C10 ----------
    over, leaks = [], []
    for i in sorted(T):
        ans = T[i].get("answer") or ""
        for tok in g["authorization_overclaim_tokens"]:
            if tok in ans:
                over.append({"turn": i, "token": tok})
        for tok in g["leak_forbidden_tokens"]:
            if tok in ans:
                leaks.append({"turn": i, "token": tok})
    add("C09", ("NOT_VERIFIED" if len(T) < 6 else V(not over)), {"hits": over})
    lk_counts = {"T%d" % i: nout(T[i], "uapp_delivery").get("leak_hit_count") for i in sorted(T)}
    add("C10", ("NOT_VERIFIED" if len(T) < 6 else V(not leaks)),
        {"independent_recompute_hits": leaks, "canvas_leak_hit_count": lk_counts})

    # ---------- C11 ----------
    base_j = json.load(io.open(BASELINE, encoding="utf-8"))
    drift_apps = []
    for row in base_j["protected_dify_apps"]:
        got = psql("select md5(w.graph) from workflows w join apps a on a.workflow_id=w.id "
                   "where a.id='%s';" % row["app_id"]).strip()
        if got != row["graph_md5"]:
            drift_apps.append({"app_id": row["app_id"], "baseline": row["graph_md5"], "now": got})
    legacy_now = psql("select md5(w.graph) from workflows w join apps a on a.workflow_id=w.id "
                      "where a.id='%s';" % base_j["legacy_diagnostic_candidate"]["app_id"]).strip()
    legacy_ok = legacy_now == base_j["legacy_diagnostic_candidate"]["draft_graph_md5"]
    gsha_now = hashlib.sha256(json.dumps(json.loads(psql(
        "select w.graph from workflows w join apps a on a.workflow_id=w.id where a.id='%s';"
        % g["identity"]["successor_app_id"])), ensure_ascii=False, sort_keys=True)
        .encode("utf-8")).hexdigest()
    add("C11", V(not drift_apps and legacy_ok and gsha_now == g["identity"]["graph_sha256"]),
        {"protected_checked": len(base_j["protected_dify_apps"]), "drift": drift_apps,
         "legacy_unchanged": legacy_ok, "candidate_graph_sha256_now": gsha_now,
         "candidate_graph_unchanged": gsha_now == g["identity"]["graph_sha256"]})

    # ---------- C12 ----------
    if T:
        w0 = T[min(T)]["window_start"]
        boot_turns = [i for i in sorted(T)
                      if any(str(n.get("node_id", "")).startswith("boot_")
                             for n in T[i].get("nodes_executed") or [])]
        counts = {}
        for tbl in ("workspaces", "accounts", "cycles", "tasks"):
            counts[tbl] = int(psql("select count(*) from %s where created_at > timestamp '%s';"
                                   % (tbl, w0), db="diyu_business") or 0)
        dup = psql("select coalesce(json_agg(x)::text,'[]') from (select key, count(*) c "
                   "from idempotency_records where created_at > timestamp '%s' "
                   "group by key having count(*) > 1) x;" % w0, db="diyu_business")
        try:
            dup = json.loads(dup or "[]") or []
        except Exception:
            dup = []
        ok = boot_turns == [min(T)] and all(v == 1 for v in counts.values()) and not dup
        add("C12", ("NOT_VERIFIED" if len(T) < 6 else V(ok)),
            {"boot_nodes_ran_in_turns": boot_turns, "m2_rows_created_in_window": counts,
             "duplicate_idempotency_keys": dup, "window_start": w0})
    else:
        add("C12", "NOT_VERIFIED", {"reason": "无证据"})

    vs = [c["result"] for c in res["conditions"]]
    res["verdict"] = ("PASS" if all(v == "PASS" for v in vs)
                      else ("NOT_VERIFIED" if "FAIL" not in vs else "FAIL"))
    res["summary"] = {"pass": vs.count("PASS"), "fail": vs.count("FAIL"),
                      "not_verified": vs.count("NOT_VERIFIED"), "total": len(vs)}
    res["scope_note"] = g["document"]["what_pass_does_not_imply"]

    with io.open(OUT, "w", encoding="utf-8") as fh:
        fh.write(json.dumps(res, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"verdict": res["verdict"], "summary": res["summary"]},
                     ensure_ascii=False, indent=2))
    for c in res["conditions"]:
        mark = {"PASS": "  ok  ", "FAIL": " FAIL ", "NOT_VERIFIED": "  NV  "}[c["result"]]
        print("[%s] %s %s" % (mark, c["id"], c["text"][:56]))
        if c["result"] != "PASS":
            print("        " + json.dumps(c["observed"], ensure_ascii=False)[:400])


if __name__ == "__main__":
    main()
