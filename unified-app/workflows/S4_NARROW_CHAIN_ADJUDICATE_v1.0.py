#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""受影响连续链判定器｜零模型调用，只按 S4_NARROW_CHAIN_GATE_v1.0.json 重算。

判定器不发起任何调用，也不读运行器的结论——只读落盘证据、线上执行记录与 M2 真源。
N-15/N-16 的负控制用本次真实记录做零调用重放，不追加任何模型调用。
任一项无法由确定性记录判断时写 NOT_VERIFIED。
"""
import hashlib
import importlib.util
import io
import json
import os
import re
import subprocess
import types

HERE = os.path.dirname(os.path.abspath(__file__))
UAPP = os.path.abspath(os.path.join(HERE, ".."))
GATE = os.path.join(UAPP, "stages", "S4_NARROW_CHAIN_GATE_v1.0.json")
OLD_GATE = os.path.join(UAPP, "stages", "S4_CONTENT_ORIGIN_CONTINUATION_GATE_v1.0.json")
FB_FREEZE = os.path.join(UAPP, "stages", "S4_PHASE_C_POINT_VERIFICATION_FREEZE_v1.1.json")
R1 = os.path.join(UAPP, "evidence", "UAPP_R1_PROTECTED_BASELINE_v1.0.json")
FIXTURE = os.path.abspath(os.path.join(UAPP, "..", "decision-chain", "fixtures",
                                       "一页纸夹具品牌事实 v0.1.md"))
EV = os.environ.get("S4NC_EV") or os.path.join(UAPP, "evidence", "stages", "s4_narrow_chain")
OUT = os.environ.get("S4NC_OUT") or os.path.join(UAPP, "stages", "S4_NARROW_CHAIN_RESULT_v1.0.json")

PLACEHOLDER = "这一步没有产出可以交给你的内容"


def load(name, fn):
    s = importlib.util.spec_from_file_location(name, os.path.join(HERE, fn))
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m


CA = load("cadj", "S4_CONTINUATION_ADJUDICATE_v1.0.py")
ADJ11 = load("adj11", "S4_PHASE_C_ADJUDICATE_v1.1.py")
B = load("s4build", "S4_BUILD_v1.0.py")
SCOPE = load("scope", "S4_SCOPE_ISOLATION_PREFLIGHT_v1.0.py")

_fm = types.ModuleType("fields_node")
exec(compile(B.FIELDS_SRC, "fields_node", "exec"), _fm.__dict__)


def shaf(p):
    return hashlib.sha256(io.open(p, "rb").read()).hexdigest()


def psql(sql, db="dify"):
    p = subprocess.run(["docker", "exec", "-i", "docker-db_postgres-1", "psql", "-U", "postgres",
                        "-d", db, "-tA", "-c", sql], capture_output=True, text=True)
    if p.returncode:
        raise RuntimeError("psql: " + (p.stderr or "")[:300])
    return p.stdout.strip()


def env_field(env, key):
    m = re.search(r"^\s*`%s`\s*:\s*(.*)$" % re.escape(key), env or "", re.M)
    return (m.group(1).strip() if m else "")


def gapset(text):
    return {x.strip() for x in re.split(r"[；;]", text or "") if x.strip() and x.strip() != "无"}


def fields_out(d):
    return CA.J(CA.node(d, "uapp_fields").get("outputs"))


def carrier(d):
    try:
        return json.loads(fields_out(d).get("task_fields_json") or "{}")
    except Exception:
        return {}


def seam_detail(d, nid):
    for n in ((d.get("nested_app_runs") or {}).get("SEAM") or {}).get("latest_run_detail") or []:
        if n.get("node_id") == nid:
            return n
    return {}


def main():
    g = json.load(io.open(GATE, encoding="utf-8"))
    old = json.load(io.open(OLD_GATE, encoding="utf-8"))
    fbfz = json.load(io.open(FB_FREEZE, encoding="utf-8"))
    if shaf(OLD_GATE) != g["inherited_criteria"]["gate_sha256"]:
        raise SystemExit("继承 Gate 已变动，拒绝判定")
    if shaf(FB_FREEZE) != g["inherited_criteria"]["fabrication_probes_from"]["sha256"]:
        raise SystemExit("编造探针来源已变动，拒绝判定")
    fixture = io.open(FIXTURE, encoding="utf-8").read()
    fb07 = ADJ11.make_fb07(fbfz, fixture)

    def fab(text):
        return [h for h in ADJ11.A.fabrication_hits(text, fbfz["fabrication_probes"], fixture)
                if h["probe"] != "FB-07"] + fb07(text)

    T = {}
    for i in range(1, 7):
        p = os.path.join(EV, "S4-NC-T%d.json" % i)
        if os.path.exists(p):
            d = json.load(io.open(p, encoding="utf-8"))
            if d.get("gate_sha256") != shaf(GATE):
                raise SystemExit("证据绑定的判据版本不一致：" + p)
            T[i] = d
    conds = []

    def add(cid, verdict, obs):
        txt = [c for c in g["pass_conditions"] if c["id"] == cid][0]["text"]
        conds.append({"id": cid, "text": txt, "result": verdict, "observed": obs})

    def V(b):
        return "PASS" if b else "FAIL"

    if len(T) < 6:
        for c in g["pass_conditions"]:
            add(c["id"], "NOT_VERIFIED", {"reason": "证据不全，已有 %s" % sorted(T)})
        res = {"stage": "S4_NARROW_CHAIN", "verdict": "NOT_VERIFIED", "conditions": conds}
        io.open(OUT, "w", encoding="utf-8").write(json.dumps(res, ensure_ascii=False, indent=2) + "\n")
        print("证据不全，已有", sorted(T))
        return

    # ---------- N-01 ----------
    chain = ["uapp_m3", "uapp_hop", "uapp_fields", "uapp_seam"]
    ok, obs = True, {}
    for i in (1, 2):
        st = {n: CA.ran(T[i], n) for n in chain}
        seam = CA.seam_tools(T[i])
        cb = len(((T[i].get("nested_app_runs") or {}).get("CONTENT_BRIEF") or {})
                 .get("runs_during_case") or [])
        obs["T%d" % i] = {"canvas": st, "seam": seam, "content_brief_app_runs": cb}
        if not all(st.values()) or seam.get("tool_content_brief") != "succeeded" or cb < 1:
            ok = False
    add("N-01", V(ok), obs)

    # ---------- N-02 ----------
    a2 = CA.artifact(T[2]).strip()
    add("N-02", V(bool(a2) and not a2.startswith(PLACEHOLDER)),
        {"T2_artifact_len": len(a2), "head": a2[:100]})

    # ---------- N-03 ----------
    ok, obs = True, {}
    for i in (1, 2):
        ctx = CA.nout(T[i], "uapp_ctx").get("registered_facts") or ""
        hin = CA.nin(T[i], "uapp_hop").get("registered_facts") or ""
        merged = fields_out(T[i]).get("capability_call") or ""
        seam_cc = CA.J(seam_detail(T[i], "tool_content_brief").get("inputs")).get("capability_call") or ""
        step = {"ctx_len": len(ctx), "hop_in_identical": ctx == hin,
                "merged_has_key": bool(env_field(merged, "facts_registered")),
                "seam_same_bytes": bool(merged) and merged == seam_cc}
        obs["T%d" % i] = step
        if not (ctx and step["hop_in_identical"] and step["merged_has_key"] and step["seam_same_bytes"]):
            ok = False
    add("N-03", V(ok), obs)

    # ---------- N-04 ----------
    g3 = gapset(fields_out(T[3]).get("gaps_text"))
    add("N-04", V(g3 == {"content_origin_mode"}),
        {"T3_merged_gaps": sorted(g3),
         "T3_hop_gaps": sorted(gapset(CA.nout(T[3], "uapp_hop").get("extraction_gaps_text")))})

    # ---------- N-05 ----------
    ans4 = (fields_out(T[4]).get("user_answered_fields") or "")
    later = {}
    ok5 = "content_origin_mode" in ans4
    ASK = "这条的素材是现拍"
    for i in (5, 6):
        gm = gapset(fields_out(T[i]).get("gaps_text"))
        val = env_field(fields_out(T[i]).get("capability_call") or "", "content_origin_mode")
        req = "content_origin_mode" in gapset(CA.nout(T[i], "uapp_hop").get("extraction_gaps_text"))
        asked_again = ASK in (T[i].get("answer") or "")
        later["T%d" % i] = {"merged_gaps": sorted(gm), "value_len": len(val),
                            "hop_wanted_it_again": req, "asked_user_again": asked_again}
        if "content_origin_mode" in gm or not val or asked_again:
            ok5 = False
    add("N-05", V(ok5), {"T4_user_answered": ans4, "later": later})

    # ---------- N-06 ----------
    keep = ("content_promise", "primary_goal", "audience_problem", "expected_change",
            "expression_boundary", "expression_subject_and_boundary", "cta_contract",
            "explicit_non_promise")
    seen, shrunk, changed, mismatch = {}, [], [], []
    for i in sorted(T):
        c = carrier(T[i]).get("fields") or {}
        for k, v in c.items():
            val = (v.get("v") or "").strip()
            if not val:
                continue
            if k in seen and seen[k] != val:
                changed.append({"turn": i, "field": k, "was": seen[k][:50], "now": val[:50]})
            seen.setdefault(k, val)
        for k in seen:
            if k not in c or not (c.get(k) or {}).get("v"):
                shrunk.append({"turn": i, "field": k})
        env = fields_out(T[i]).get("capability_call") or ""
        for k in keep:
            ev = env_field(env, k)
            if ev and k in seen and ev != seen[k]:
                mismatch.append({"turn": i, "field": k})
    add("N-06", V(not shrunk and not changed and not mismatch),
        {"carrier_shrank": shrunk, "confirmed_value_changed": changed,
         "envelope_disagrees_with_carrier": mismatch,
         "held_by_turn": {("T%d" % i): fields_out(T[i]).get("held_fields") for i in sorted(T)},
         "named_fields_confirmed": sorted(k for k in keep if k in seen)})

    # ---------- N-07 ----------
    want = {4: "tool_creative_script", 5: "tool_production_director", 6: "tool_publishing_packaging"}
    arts, ok7 = {}, True
    for i, tool in want.items():
        a = CA.artifact(T[i]).strip()
        arts["T%d" % i] = {"artifact_len": len(a), "seam": CA.seam_tools(T[i]),
                           "head": a[:80], "outcome": CA.nout(T[i], "uapp_seam").get("business_delivery_outcome")}
        if not (a and not a.startswith(PLACEHOLDER) and CA.seam_tools(T[i]).get(tool) == "succeeded"):
            ok7 = False
    add("N-07", V(ok7), arts)

    # ---------- N-08 ----------
    wa = {1: "tool_content_brief", 2: "tool_content_brief", 3: "tool_creative_script",
          4: "tool_creative_script", 5: "tool_production_director", 6: "tool_publishing_packaging"}
    bad, per = [], {}
    for i in sorted(T):
        st = CA.seam_tools(T[i])
        per["T%d" % i] = st
        shadow = {k: len(((T[i].get("nested_app_runs") or {}).get(k) or {}).get("runs_during_case") or [])
                  for k in ("MATRIX", "CAMPAIGN", "CONTENT_BRIEF", "CREATIVE_SCRIPT",
                            "PRODUCTION_DIRECTOR", "PUBLISHING_PACKAGING")}
        expect_app = {"tool_content_brief": "CONTENT_BRIEF", "tool_creative_script": "CREATIVE_SCRIPT",
                      "tool_production_director": "PRODUCTION_DIRECTOR",
                      "tool_publishing_packaging": "PUBLISHING_PACKAGING"}[wa[i]]
        extra_apps = {k: v for k, v in shadow.items() if v and k != expect_app}
        if st.get(wa[i]) != "succeeded" or [t for t in st if t != wa[i]] or extra_apps:
            bad.append({"turn": i, "want": wa[i], "seam": st, "extra_app_runs": extra_apps})
    add("N-08", V(not bad), {"per_turn": per, "violations": bad})

    # ---------- N-09 / N-14 / N-17 ----------
    over, leaks, fabs = [], [], []
    for i in sorted(T):
        ans = T[i].get("answer") or ""
        over += [{"turn": i, "token": t} for t in old["authorization_overclaim_tokens"] if t in ans]
        leaks += [{"turn": i, "token": t} for t in old["leak_forbidden_tokens"] if t in ans]
        fabs += [dict(x, turn=i) for x in fab(ans + "\n" + CA.artifact(T[i]))]
    add("N-09", V(not over), {"hits": over})
    add("N-14", V(not leaks), {"hits": leaks})
    add("N-17", V(not fabs), {"hits": fabs[:20]})

    # ---------- N-10 ----------
    ok10, obs10, prev = True, {}, 0
    for i in sorted(T):
        po = CA.nout(T[i], "uapp_persist")
        cv = (T[i].get("conversation_variables_after_turn") or {}).get("uapp_last_artifact") or {}
        cur = CA.artifact(T[i]).strip()
        obs10["T%d" % i] = {"artifact_len": len(cur), "persist": po.get("persist_action"),
                            "last_len_after": cv.get("len"), "prev_len": prev}
        if not cur and (po.get("persist_action") != "KEEP_PREVIOUS" or (cv.get("len") or 0) < prev):
            ok10 = False
        prev = cv.get("len") if cv.get("len") is not None else prev
    add("N-10", V(ok10), obs10)

    # ---------- N-11 ----------
    w0 = T[min(T)]["window_start"]
    boot = [i for i in sorted(T) if any(str(n.get("node_id", "")).startswith("boot_")
                                        for n in T[i].get("nodes_executed") or [])]
    counts = {t: int(psql("select count(*) from %s where created_at > timestamp '%s';" % (t, w0),
                          db="diyu_business") or 0)
              for t in ("workspaces", "accounts", "cycles", "tasks")}
    dup = psql("select coalesce(json_agg(x)::text,'[]') from (select key, count(*) c from "
               "idempotency_records where created_at > timestamp '%s' group by key "
               "having count(*) > 1) x;" % w0, db="diyu_business")
    try:
        dup = json.loads(dup or "[]") or []
    except Exception:
        dup = []
    add("N-11", V(boot == [min(T)] and all(v == 1 for v in counts.values()) and not dup),
        {"boot_turns": boot, "m2_rows": counts, "duplicate_keys": dup})

    # ---------- N-12 ----------
    base = json.load(io.open(R1, encoding="utf-8"))
    ids = {k: v["app_id"] for k, v in base["protected_apps"].items()}
    drift = {}
    for k, v in base["protected_apps_graph_md5"].items():
        now = psql("select md5(w.graph) from workflows w join apps a on a.workflow_id=w.id "
                   "where a.id='%s';" % ids[k]).strip()
        if now != v:
            drift[k] = {"baseline": v, "now": now}
    gnow = hashlib.sha256(json.dumps(json.loads(psql(
        "select w.graph from workflows w join apps a on a.workflow_id=w.id where a.id='%s';"
        % g["binding"]["candidate_app_id"])), ensure_ascii=False, sort_keys=True)
        .encode("utf-8")).hexdigest()
    pin = psql("select p.version from tool_workflow_providers p where p.name='diyu_uapp_hop';")
    add("N-12", V(not drift and gnow == g["binding"]["candidate_published_graph_sha256"]
                  and pin == g["binding"]["hop_provider_pinned_version"]),
        {"baseline_file": os.path.basename(R1), "drift": drift,
         "candidate_graph_sha256_now": gnow, "hop_pin_now": pin})

    # ---------- N-13 ----------
    meta_p = os.path.join(EV, "RUN_META.json")
    if os.path.exists(meta_p):
        meta = json.load(io.open(meta_p, encoding="utf-8"))
        before, after = meta["scope_snapshot_before"], meta["scope_snapshot_after"]
        same = before == after
        intrusion = os.path.exists(os.path.join(EV, "SCOPE_INTRUSION.json"))
        add("N-13", V(same and not intrusion),
            {"scope_snapshot_identical_before_after": same,
             "intrusion_file_present": intrusion,
             "concurrent_foreign_writers_disclosed_not_blocking":
                 meta.get("concurrent_foreign_writers_disclosed_not_blocking")})
    else:
        add("N-13", "NOT_VERIFIED", {"reason": "RUN_META.json 缺失"})

    # ---------- N-15 正负控制（负控制零模型调用重放） ----------
    pos15, ok15 = {}, True
    for i in sorted(T):
        hop_gaps = gapset(CA.nout(T[i], "uapp_hop").get("extraction_gaps_text"))
        carried = {x for x in (fields_out(T[i]).get("carried_fields") or "").split(",") if x}
        prev_fields = (carrier(T[i - 1]).get("fields") or {}) if i > 1 else {}
        should = {k for k in hop_gaps if (prev_fields.get(k) or {}).get("v")}
        env = fields_out(T[i]).get("capability_call") or ""
        filled = {k for k in should if env_field(env, k)}
        pos15["T%d" % i] = {"hop_gaps": sorted(hop_gaps), "carrier_could_fill": sorted(should),
                            "carried": sorted(carried), "filled_in_envelope": sorted(filled)}
        if should != filled or not should <= carried:
            ok15 = False
    neg15 = None
    for i in sorted(T):
        if (fields_out(T[i]).get("carried_fields") or ""):
            hi = CA.nout(T[i], "uapp_hop")
            r = _fm.main("", carrier(T[i]).get("task_key") or "X", hi.get("capability_call"),
                         hi.get("extraction_gaps_text"), "")
            k = (fields_out(T[i]).get("carried_fields") or "").split(",")[0]
            neg15 = {"turn": i, "field": k, "with_empty_carrier_still_a_gap":
                     k in gapset(r["gaps_text"]), "carried_when_empty": r["carried_fields"]}
            break
    add("N-15", V(ok15 and neg15 and neg15["with_empty_carrier_still_a_gap"]
                  and not neg15["carried_when_empty"]),
        {"positive": pos15, "negative_control_zero_model_call": neg15})

    # ---------- N-16 正负控制 ----------
    tk = {("T%d" % i): (carrier(T[i]).get("task_key"), carrier(T[i]).get("rev")) for i in sorted(T)}
    keys = {v[0] for v in tk.values()}
    revs = [tk["T%d" % i][1] for i in sorted(T)]
    hi6 = CA.nout(T[6], "uapp_hop")
    rn = _fm.main(json.dumps(carrier(T[5]), ensure_ascii=False), "NEW-TASK-0000",
                  hi6.get("capability_call"), hi6.get("extraction_gaps_text"), "")
    cn = json.loads(rn["task_fields_json"])
    add("N-16", V(len(keys) == 1 and revs == sorted(revs) and revs == list(range(1, 7))
                  and cn["rev"] == 1 and not cn["fields"].get("content_origin_mode")
                  and not rn["carried_fields"]),
        {"positive": {"task_keys": sorted(keys), "revs": revs},
         "negative_control_zero_model_call": {
             "swapped_task_key": "NEW-TASK-0000", "rev_reset_to": cn["rev"],
             "content_origin_mode_inherited": bool(cn["fields"].get("content_origin_mode")),
             "carried": rn["carried_fields"]}})

    vs = [c["result"] for c in conds]
    res = {"stage": "S4_NARROW_CHAIN", "gate_sha256": shaf(GATE),
           "r1_baseline_sha256": shaf(R1), "model_calls_by_adjudicator": 0,
           "verdict": "PASS" if all(v == "PASS" for v in vs) else
                      ("FAIL" if "FAIL" in vs else "NOT_VERIFIED"),
           "summary": {"pass": vs.count("PASS"), "fail": vs.count("FAIL"),
                       "not_verified": vs.count("NOT_VERIFIED"), "total": len(vs)},
           "conditions": conds,
           "allowed_upgrades_if_pass": g["allowed_upgrades_if_all_pass"],
           "what_pass_does_not_imply": g["document"]["what_pass_does_not_imply"]}
    io.open(OUT, "w", encoding="utf-8").write(json.dumps(res, ensure_ascii=False, indent=2) + "\n")
    print("受影响连续链判定：%s  %s" % (res["verdict"], json.dumps(res["summary"], ensure_ascii=False)))
    for c in conds:
        mark = {"PASS": " ok ", "FAIL": "FAIL", "NOT_VERIFIED": " NV "}[c["result"]]
        print("  [%s] %s %s" % (mark, c["id"], c["text"][:54]))
        if c["result"] != "PASS":
            print("        " + json.dumps(c["observed"], ensure_ascii=False)[:700])


if __name__ == "__main__":
    main()
