#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""规范任务状态载体｜七轮连续链判定器。零模型调用。

只按 S4_CANONICAL_TASK_STATE_GATE_v1.0/v1.1 的 phase_d_run_criteria 重算 V-01…V-09，
外加 stop_rules 要求的作用域隔离项与成本账。
判定器不发起任何调用，也不读运行器的结论——只读落盘证据、线上执行记录与 M2 真源。
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
GATE = os.path.join(UAPP, "stages", "S4_CANONICAL_TASK_STATE_GATE_v1.1.json")
MANIFEST = os.path.join(UAPP, "stages", "S4_CANONICAL_TASK_STATE_CANDIDATE_MANIFEST_v1.0.json")
OLD_GATE = os.path.join(UAPP, "stages", "S4_CONTENT_ORIGIN_CONTINUATION_GATE_v1.0.json")
FB_FREEZE = os.path.join(UAPP, "stages", "S4_PHASE_C_POINT_VERIFICATION_FREEZE_v1.1.json")
FIXTURE = os.path.abspath(os.path.join(UAPP, "..", "decision-chain", "fixtures",
                                       "一页纸夹具品牌事实 v0.1.md"))
EV = os.path.join(UAPP, "evidence", "stages", "s4_canonical_state", "run")
OUT = os.path.join(UAPP, "stages", "S4_CANONICAL_TASK_STATE_RESULT_v1.0.json")
COST = os.path.join(UAPP, "evidence", "stages", "s4_canonical_state", "COST_ACCOUNT.json")

PLACEHOLDER = "这一步没有产出可以交给你的内容"
PROD_SCOPE = ("production.profile", "production.time_window", "production.capacity_or_owner")
REASK_TOKENS = ["素材是现拍", "现拍还是", "重新拍摄还是", "已有素材剪辑还是", "素材来源",
                "content_origin_mode"]
AUTH_CLAIM_TOKENS = ["已获授权", "授权已确认", "素材已授权", "已取得授权", "授权记录已核对通过"]
FINAL_CLAIM = ["已定稿", "定稿完成", "final_cut", "成片已确认", "母版已完成"]


def load(name, fn):
    s = importlib.util.spec_from_file_location(name, os.path.join(HERE, fn))
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m


CA = load("cadj", "S4_CONTINUATION_ADJUDICATE_v1.0.py")
ADJ11 = load("adj11", "S4_PHASE_C_ADJUDICATE_v1.1.py")
CSN = load("csn", "S4_CANONICAL_STATE_NODES_v1.0.py")
_fm = types.ModuleType("fields_node")
exec(compile(CSN.FIELDS_SRC, "fields_node", "exec"), _fm.__dict__)

APPS = {"M1_HOST": "a4c3b19b-243f-490b-9aca-3aa19767d6a5",
        "HOP": "6c46fdb1-5f49-4513-a0c0-29957b3dcee4",
        "SEAM": "5fca0162-e26b-4545-a00b-66b1a2a2a077",
        "MATRIX": "fd25ebfa-db67-40c3-82e5-202e1254facf",
        "CAMPAIGN": "1f9d65ea-8af5-45f0-a1d0-a80223d354e2",
        "CONTENT_BRIEF": "b1dcf784-540e-4b3f-8ba2-3812f477f3ce",
        "CREATIVE_SCRIPT": "44b55f9d-3792-40c3-b095-f2696464b4ec",
        "PRODUCTION_DIRECTOR": "13cfabd5-f592-4354-a304-47098b765697",
        "PUBLISHING_PACKAGING": "c9cdea24-9df3-400b-9ecd-1d740e8c96df"}
CAND = "85c01f85-a081-43e9-ab09-9993289cc200"


def shaf(p):
    return hashlib.sha256(io.open(p, "rb").read()).hexdigest()


def sha(s):
    return hashlib.sha256((s or "").encode("utf-8")).hexdigest()


def psql(sql, db="dify"):
    p = subprocess.run(["docker", "exec", "-i", "docker-db_postgres-1", "psql", "-U", "postgres",
                        "-d", db, "-tA", "-c", sql], capture_output=True, text=True)
    if p.returncode:
        raise RuntimeError("psql: " + (p.stderr or "")[:300])
    return p.stdout.strip()


def fout(d):
    return CA.J(CA.node(d, "uapp_fields").get("outputs"))


def sout(d):
    return CA.J(CA.node(d, "uapp_state").get("outputs"))


def carrier(d):
    try:
        return json.loads(sout(d).get("task_state_json") or "{}")
    except Exception:
        return {}


def pending(d):
    try:
        return json.loads(fout(d).get("pending_state_json") or "{}")
    except Exception:
        return {}


def gapset(text):
    return {x.strip() for x in re.split(r"[；;]", text or "") if x.strip() and x.strip() != "无"}


def envval(env, key):
    m = re.search(r"^\s*`?%s`?\s*:\s*(.*)$" % re.escape(key), env or "", re.M)
    return (m.group(1).strip() if m else "")


def main():
    g = json.load(io.open(GATE, encoding="utf-8"))
    m = json.load(io.open(MANIFEST, encoding="utf-8"))
    old = json.load(io.open(OLD_GATE, encoding="utf-8"))
    fbfz = json.load(io.open(FB_FREEZE, encoding="utf-8"))
    if shaf(OLD_GATE) != g["phase_d_run_criteria"]["inherited_verbatim"]["sha256"]:
        raise SystemExit("继承 Gate 已变动，拒绝判定")
    if shaf(FB_FREEZE) != g["phase_d_run_criteria"]["fabrication_probes"]["sha256"]:
        raise SystemExit("编造探针来源已变动，拒绝判定")
    if shaf(MANIFEST) != g["candidate_manifest"]["sha256"]:
        raise SystemExit("Candidate Manifest 已变动，拒绝判定")
    fixture = io.open(FIXTURE, encoding="utf-8").read()
    fb07 = ADJ11.make_fb07(fbfz, fixture)

    def fab(text):
        return [h for h in ADJ11.A.fabrication_hits(text, fbfz["fabrication_probes"], fixture)
                if h["probe"] != "FB-07"] + fb07(text)

    T = {}
    for i in range(1, 8):
        p = os.path.join(EV, "S4-CT-T%d.json" % i)
        if os.path.exists(p):
            d = json.load(io.open(p, encoding="utf-8"))
            if d.get("manifest_sha256") != shaf(MANIFEST):
                raise SystemExit("证据绑定的 Manifest 版本不一致：" + p)
            T[i] = d

    conds = []
    TXT = {c["id"]: c["text"] for c in g["phase_d_run_criteria"]["checks"]}

    def add(cid, verdict, obs, text=None):
        conds.append({"id": cid, "text": text or TXT.get(cid, cid),
                      "result": verdict, "observed": obs})

    def V(b):
        return "PASS" if b else "FAIL"

    if len(T) < 7:
        for cid in TXT:
            add(cid, "NOT_VERIFIED", {"reason": "证据不全，已有 %s" % sorted(T)})
        io.open(OUT, "w", encoding="utf-8").write(json.dumps(
            {"stage": "S4_CANONICAL_TASK_STATE", "verdict": "NOT_VERIFIED",
             "conditions": conds}, ensure_ascii=False, indent=2) + "\n")
        print("证据不全，已有", sorted(T))
        return

    # ---------- V-01 T2 Content Brief 真实产出 ----------
    a2 = CA.artifact(T[2]).strip()
    add("V-01", V(bool(a2) and not a2.startswith(PLACEHOLDER)
                 and CA.seam_tools(T[2]).get("tool_content_brief") == "succeeded"),
        {"artifact_len": len(a2), "head": a2[:90], "seam": CA.seam_tools(T[2]),
         "sha256": sha(a2)})

    # ---------- V-02 T3 只问 content.origin_mode，不再缺 goal_family，不用占位符补齐 ----------
    g3 = gapset(fout(T[3]).get("gaps_text"))
    c3 = carrier(T[3]).get("fields") or {}
    env3 = fout(T[3]).get("capability_call") or ""
    carried3 = [x for x in (fout(T[3]).get("carried_fields") or "").split(",") if x]
    ph3 = [k for k in carried3 if _fm._missing((c3.get(k) or {}).get("v") or "")]
    gf3 = c3.get("objective.goal_family") or {}
    add("V-02", V(g3 == {"content_origin_mode"} and gf3.get("v")
                  and not _fm._missing(gf3.get("v")) and not ph3),
        {"merged_gaps": sorted(g3), "hop_gaps": sorted(gapset(
            CA.nout(T[3], "uapp_hop").get("extraction_gaps_text"))),
         "goal_family": gf3, "envelope_goal_family": envval(env3, "goal_family"),
         "carried": carried3, "carried_that_are_placeholders": ph3,
         "对照旧轮": "旧版 T3 缺口是 {content_origin_mode, goal_family}，且用占位符补了 primary_goal"})

    # ---------- V-03 T4 回答后 Creative Script 真实产出 ----------
    a4 = CA.artifact(T[4]).strip()
    ans4 = [x for x in (fout(T[4]).get("user_answered_fields") or "").split(",") if x]
    add("V-03", V(bool(a4) and not a4.startswith(PLACEHOLDER)
                 and CA.seam_tools(T[4]).get("tool_creative_script") == "succeeded"
                 and "content.origin_mode" in ans4),
        {"artifact_len": len(a4), "head": a4[:90], "seam": CA.seam_tools(T[4]),
         "user_answered": ans4, "sha256": sha(a4)})

    # ---------- V-04 T5 只问真正缺的制作条件；不重复询问 content.origin_mode ----------
    g5 = gapset(fout(T[5]).get("gaps_text"))
    c5 = carrier(T[5]).get("fields") or {}
    om5 = c5.get("content.origin_mode") or {}
    reask = {}
    for i in (5, 6, 7):
        ans = T[i].get("answer") or ""
        reask["T%d" % i] = [t for t in REASK_TOKENS if t in ans]
    prod_only = g5 and all(x in [k.split(".")[-1] for k in PROD_SCOPE] or x in PROD_SCOPE
                           for x in g5)
    later_gaps = {("T%d" % i): sorted(gapset(fout(T[i]).get("gaps_text"))) for i in (5, 6, 7)}
    no_reask = not any(reask.values()) and all(
        "content_origin_mode" not in later_gaps["T%d" % i]
        and "content.origin_mode" not in later_gaps["T%d" % i] for i in (5, 6, 7))
    add("V-04", V(prod_only and om5.get("v") and om5.get("lvl") in ("A", "B")
                  and om5.get("ref") and no_reask),
        {"T5_merged_gaps": sorted(g5), "T5_hop_gaps": sorted(gapset(
            CA.nout(T[5], "uapp_hop").get("extraction_gaps_text"))),
         "gaps_all_in_production_scope": prod_only,
         "carrier_content_origin_mode": om5, "later_gaps": later_gaps,
         "reask_token_hits": reask,
         "判据说明": "『保留』判在任务载体与是否重复询问，不判在每个能力外壳里键是否在场"})

    # ---------- V-05 T6 回到同一个 PD 任务并产出 PD artifact ----------
    a6 = CA.artifact(T[6]).strip()
    ans6 = [x for x in (fout(T[6]).get("user_answered_fields") or "").split(",") if x]
    add("V-05", V(bool(a6) and not a6.startswith(PLACEHOLDER)
                 and CA.seam_tools(T[6]).get("tool_production_director") == "succeeded"
                 and any(k in ans6 for k in PROD_SCOPE)),
        {"artifact_len": len(a6), "head": a6[:90], "seam": CA.seam_tools(T[6]),
         "user_answered": ans6, "sha256": sha(a6),
         "T5_produced_nothing": len(CA.artifact(T[5]).strip()),
         "同一任务": {"T5_task_key": carrier(T[5]).get("task_key"),
                      "T6_task_key": carrier(T[6]).get("task_key")}})

    # ---------- V-06 T7 PP 的完整链血缘 ----------
    up7 = CA.nin(T[7], "uapp_hop").get("upstream_delivery") or ""
    upcap7 = CA.nin(T[7], "uapp_hop").get("upstream_capability") or ""
    bind7 = json.loads(fout(T[7]).get("upstream_binding_json") or "[]")
    bound = [b for b in bind7 if b.get("lineage") == "BOUND"]
    a7 = CA.artifact(T[7]).strip()
    final_hits = [t for t in FINAL_CLAIM if t in (a7 + (T[7].get("answer") or ""))]
    add("V-06", V(upcap7 == "PRODUCTION_DIRECTOR" and sha(up7) == sha(a6)
                 and bound and all(b.get("upstream_capability") == "PRODUCTION_DIRECTOR"
                                   for b in bound)
                 and bool(a7) and not a7.startswith(PLACEHOLDER) and not final_hits),
        {"upstream_capability": upcap7,
         "upstream_delivery_sha256": sha(up7), "T6_pd_artifact_sha256": sha(a6),
         "hash_equal": sha(up7) == sha(a6), "upstream_binding": bind7,
         "pp_artifact_len": len(a7), "final_claim_hits": final_hits,
         "对照上一轮": "上一轮 PP 的上游是 CS artifact，属 PRE 短入口，不填完整链位"})

    # ---------- V-07 来源可回指；模型抽取值未成为跨轮硬事实 ----------
    bad_ref, bad_kind, ph = [], [], []
    for i in sorted(T):
        for k, v in (carrier(T[i]).get("fields") or {}).items():
            if not v.get("ref"):
                bad_ref.append({"turn": i, "field": k})
            if v.get("lvl") in ("A", "B") and not str(v.get("ref", "")).startswith("TURN"):
                bad_kind.append({"turn": i, "field": k, "lvl": v.get("lvl"), "ref": v.get("ref")})
            if v.get("lvl") == "D" and not str(v.get("ref", "")).startswith("M1_SNAPSHOT"):
                bad_kind.append({"turn": i, "field": k, "lvl": v.get("lvl"), "ref": v.get("ref")})
            if _fm._missing(v.get("v") or ""):
                ph.append({"turn": i, "field": k, "v": (v.get("v") or "")[:40]})
    last = carrier(T[7]).get("fields") or {}
    lvl_hist = {k: v.get("lvl") for k, v in sorted(last.items())}
    add("V-07", V(not bad_ref and not bad_kind and not ph),
        {"missing_source_ref": bad_ref, "level_ref_mismatch": bad_kind,
         "placeholder_in_carrier": ph, "final_levels": lvl_hist,
         "E 级字段": sorted(k for k, v in last.items() if v == "E")})

    # ---------- V-08 无暗跑、无泄漏、无编造、无未授权素材声明、无重复 M2 副作用 ----------
    want = {1: "tool_content_brief", 2: "tool_content_brief", 3: "tool_creative_script",
            4: "tool_creative_script", 5: "tool_production_director",
            6: "tool_production_director", 7: "tool_publishing_packaging"}
    expect_app = {"tool_content_brief": "CONTENT_BRIEF", "tool_creative_script": "CREATIVE_SCRIPT",
                  "tool_production_director": "PRODUCTION_DIRECTOR",
                  "tool_publishing_packaging": "PUBLISHING_PACKAGING"}
    shadow_bad, per, over, leaks, fabs, authc = [], {}, [], [], [], []
    for i in sorted(T):
        st = CA.seam_tools(T[i])
        per["T%d" % i] = st
        runs = {k: len(((T[i].get("nested_app_runs") or {}).get(k) or {})
                       .get("runs_during_case") or [])
                for k in ("MATRIX", "CAMPAIGN", "CONTENT_BRIEF", "CREATIVE_SCRIPT",
                          "PRODUCTION_DIRECTOR", "PUBLISHING_PACKAGING")}
        extra = {k: v for k, v in runs.items() if v and k != expect_app[want[i]]}
        if st.get(want[i]) != "succeeded" or [t for t in st if t != want[i]] or extra:
            shadow_bad.append({"turn": i, "want": want[i], "seam": st, "extra_app_runs": extra})
        ans, art = T[i].get("answer") or "", CA.artifact(T[i])
        over += [{"turn": i, "token": t} for t in old["authorization_overclaim_tokens"] if t in ans]
        leaks += [{"turn": i, "token": t} for t in old["leak_forbidden_tokens"] if t in ans]
        fabs += [dict(x, turn=i) for x in fab(ans + "\n" + art)]
        authc += [{"turn": i, "token": t} for t in AUTH_CLAIM_TOKENS if t in (ans + art)]
    w0 = T[min(T)]["window_start"]
    counts = {t: int(psql("select count(*) from %s where created_at > timestamp '%s';" % (t, w0),
                          db="diyu_business") or 0)
              for t in ("workspaces", "accounts", "cycles", "tasks",
                        "task_snapshots", "artifacts", "publish_instances")}
    dupraw = psql("select coalesce(json_agg(x)::text,'[]') from (select key, count(*) c from "
                  "idempotency_records where created_at > timestamp '%s' group by key "
                  "having count(*) > 1) x;" % w0, db="diyu_business")
    try:
        dup = json.loads(dupraw or "[]") or []
    except Exception:
        dup = []
    boot = [i for i in sorted(T) if any(str(n.get("node_id", "")).startswith("boot_")
                                        for n in T[i].get("nodes_executed") or [])]
    m2_ok = (boot == [min(T)]
             and all(counts[t] == 1 for t in ("workspaces", "accounts", "cycles", "tasks"))
             and not dup)
    add("V-08", V(not shadow_bad and not over and not leaks and not fabs
                 and not authc and m2_ok),
        {"seam_per_turn": per, "shadow_runs": shadow_bad, "overclaim": over, "leaks": leaks,
         "fabrication": fabs[:20], "unauthorized_material_claims": authc,
         "m2_rows": counts, "duplicate_idempotency_keys": dup, "boot_turns": boot})

    # ---------- V-09 九受保护应用与 provider 零漂移 ----------
    drift = {}
    for k, v in m["protected_apps_graph_md5"].items():
        now = psql("select md5(w.graph) from workflows w join apps a on a.workflow_id=w.id "
                   "where a.id='%s';" % APPS[k]).strip()
        if now != v:
            drift[k] = {"manifest": v, "now": now}
    gnow = hashlib.sha256(json.dumps(json.loads(psql(
        "select w.graph from workflows w join apps a on a.workflow_id=w.id where a.id='%s';"
        % CAND)), ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()
    pin = psql("select p.version from tool_workflow_providers p where p.name='diyu_uapp_hop';")
    add("V-09", V(not drift and gnow == m["candidate_canvas"]["graph_sha256"]
                  and pin == m["hop_provider"]["pinned_version"]),
        {"drift": drift, "candidate_graph_sha256_now": gnow,
         "candidate_graph_sha256_frozen": m["candidate_canvas"]["graph_sha256"],
         "hop_pin_now": pin})

    # ---------- 停止规则项：作用域隔离 ----------
    meta_p = os.path.join(EV, "RUN_META.json")
    if os.path.exists(meta_p):
        meta = json.load(io.open(meta_p, encoding="utf-8"))
        same = meta["scope_snapshot_before"] == meta["scope_snapshot_after"]
        intr = os.path.exists(os.path.join(EV, "SCOPE_INTRUSION.json"))
        add("S-01", V(same and not intr),
            {"scope_snapshot_identical_before_after": same, "intrusion_file_present": intr,
             "concurrent_foreign_writers_disclosed_not_blocking":
                 meta.get("concurrent_foreign_writers_disclosed_not_blocking")},
            text="stop_rules.scope_intrusion：运行前后作用域快照一致，未触发隔离门")
    else:
        add("S-01", "NOT_VERIFIED", {"reason": "RUN_META.json 缺失"},
            text="stop_rules.scope_intrusion")

    # ---------- 成本账（按本任务十个 app_id 作用域统计） ----------
    w1 = psql("select now()::text;")
    ids = "','".join(sorted(set(list(APPS.values()) + [CAND])))
    top = int(psql("select count(*) from workflow_runs where app_id='%s' "
                   "and created_at between timestamp '%s' and timestamp '%s';"
                   % (CAND, w0, w1)) or 0)
    nested = int(psql("select count(*) from workflow_runs where app_id in ('%s') "
                      "and app_id <> '%s' and created_at between timestamp '%s' "
                      "and timestamp '%s';" % (ids, CAND, w0, w1)) or 0)
    llm = psql("select coalesce(json_agg(x)::text,'[]') from (select e.status, count(*) c "
               "from workflow_node_executions e where e.node_type='llm' and e.app_id in ('%s') "
               "and e.created_at between timestamp '%s' and timestamp '%s' group by e.status) x;"
               % (ids, w0, w1))
    try:
        llm = json.loads(llm or "[]") or []
    except Exception:
        llm = []
    attempts = sum(int(T[i].get("attempts") or 1) for i in sorted(T))
    cost = {"window": [w0, w1], "scope_app_ids": sorted(set(list(APPS.values()) + [CAND])),
            "canvas_workflow_runs": top, "budget_canvas_runs": m["run_binding"]["canvas_workflow_runs"],
            "nested_app_runs": nested, "llm_node_executions_by_status": llm,
            "llm_total": sum(x["c"] for x in llm),
            "hard_cap_llm": m["run_binding"]["hard_cap_llm_node_attempts"],
            "turn_attempts": {("T%d" % i): T[i].get("attempts") for i in sorted(T)},
            "retries": attempts - len(T),
            "fixture_uploads": len(T),
            "http_status": {("T%d" % i): T[i].get("http_status") for i in sorted(T)},
            "elapsed_seconds": {("T%d" % i): T[i].get("elapsed_seconds") for i in sorted(T)},
            "m2_rows": counts, "duplicate_idempotency_keys": dup}
    io.open(COST, "w", encoding="utf-8").write(json.dumps(cost, ensure_ascii=False, indent=1) + "\n")

    vs = [c["result"] for c in conds]
    res = {"stage": "S4_CANONICAL_TASK_STATE", "gate_sha256": shaf(GATE),
           "manifest_sha256": shaf(MANIFEST), "model_calls_by_adjudicator": 0,
           "verdict": "PASS" if all(v == "PASS" for v in vs) else
                      ("FAIL" if "FAIL" in vs else "NOT_VERIFIED"),
           "summary": {"pass": vs.count("PASS"), "fail": vs.count("FAIL"),
                       "not_verified": vs.count("NOT_VERIFIED"), "total": len(vs)},
           "conditions": conds, "cost_account": cost,
           "allowed_upgrades_if_all_pass": g["allowed_upgrades_if_all_pass"],
           "what_pass_does_not_imply": g["document"]["what_pass_does_not_imply"]}
    io.open(OUT, "w", encoding="utf-8").write(json.dumps(res, ensure_ascii=False, indent=2) + "\n")
    print("七轮连续链判定：%s  %s" % (res["verdict"], json.dumps(res["summary"], ensure_ascii=False)))
    for c in conds:
        mark = {"PASS": " ok ", "FAIL": "FAIL", "NOT_VERIFIED": " NV "}[c["result"]]
        print("  [%s] %s %s" % (mark, c["id"], c["text"][:58]))
        if c["result"] != "PASS":
            print("        " + json.dumps(c["observed"], ensure_ascii=False)[:900])
    print("成本：画布 %d/%d，嵌套 %d，LLM %d/%d，重试 %d"
          % (top, cost["budget_canvas_runs"], nested, cost["llm_total"], cost["hard_cap_llm"],
             cost["retries"]))


if __name__ == "__main__":
    main()
