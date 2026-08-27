#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""M4-CL31-02 / CL31-03 真实 Dify Runtime 故障注入取证

判据来自已冻结的取证合同 v0.5 §2.2 / §3。本脚本只执行判据，不改判据。
禁止取样条款：每个注入指令**只跑一次**，失败即记录失败（v0.5 §0-5 / F-15）。
"""
import hashlib, importlib.util, json, os, subprocess, sys, time

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
DC_WF = os.path.join(ROOT, "decision-chain", "workflows")
OUT = os.path.join(ROOT, "decision-chain/evidence/m4/final_closure")


def _load(n, p):
    s = importlib.util.spec_from_file_location(n, p); m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m); return m


PUB = _load("m4pub", os.path.join(DC_WF, "DIYU_M4_PUBLISH_AND_REBIND_v0.1.py"))
FA = _load("m4fa", os.path.join(DC_WF, "DIYU_M4_FORMAL_ATTEMPT_v0.1.py"))
FX = _load("m4fx", os.path.join(DC_WF, "DIYU_M4_DETERMINISTIC_PROBE_v0.1.py"))
INJ = _load("m4inj", os.path.join(DC_WF, "DIYU_M4_CL31_INJECT_BUILD_v0.1.py"))

CONTRACT = "V1_M4_EVIDENCE_COLLECTION_CONTRACT_v0.5.md"
TASK_HASH = "8d73b4f157883eb422e6ae17ececcf87a64d98c6a51f35537b8446155fa85070"


def sha(s): return hashlib.sha256((s or "").encode("utf-8")).hexdigest()


def psql(sql):
    p = subprocess.run(["docker", "exec", "-i", "docker-db_postgres-1", "psql", "-U", "postgres",
                        "-d", "dify", "-t", "-A", "-F", "\x01", "-c", sql],
                       capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError(p.stderr[:500])
    return [l for l in p.stdout.split("\n") if l.strip()]


def node_execs(app_id, since):
    rows = psql("SELECT node_id,node_type,title,status,coalesce(error,''),"
                "coalesce(left(outputs,20000),''),workflow_run_id,created_at "
                "FROM workflow_node_executions WHERE app_id='%s' AND created_at >= '%s' "
                "ORDER BY created_at, index;" % (app_id, since))
    out = []
    for r in rows:
        f = r.split("\x01")
        if len(f) < 8: continue
        out.append({"node_id": f[0], "node_type": f[1], "title": f[2], "status": f[3],
                    "error": f[4][:400], "outputs": f[5], "run_id": f[6], "at": f[7]})
    return out


def runs_of(app_id, since):
    rows = psql("SELECT id,status,coalesce(error,''),coalesce(left(outputs,20000),''),created_at "
                "FROM workflow_runs WHERE app_id='%s' AND created_at >= '%s' ORDER BY created_at;"
                % (app_id, since))
    out = []
    for r in rows:
        f = r.split("\x01")
        if len(f) < 5: continue
        out.append({"run_id": f[0], "status": f[1], "error": f[2][:400],
                    "outputs": f[3], "at": f[4]})
    return out


def db_now():
    return psql("SELECT to_char(now(),'YYYY-MM-DD HH24:MI:SS');")[0]


def main():
    objs = json.load(open(os.path.join(OUT, "INJECTION_OBJECTS.json"), encoding="utf-8"))
    ids = {p["tag"]: p["app_id"] for p in objs["published"]}
    child_id, seam_id = ids["EVAL-1"], ids["EVAL-2"]
    base = "http://127.0.0.1"

    c = PUB.Console(); c.login()
    tok_seam = FA.ensure_api_key(c, seam_id)
    tok_child = FA.ensure_api_key(c, child_id)

    PROF = "professional_input: 见 capability_call"
    results = {}

    # ── INJ-01 TOOL_FAIL：走 EVAL-2 接缝 ──────────────────────────────────
    cc = FX.CT_M3 + "\nM4_FAULT_DIRECTIVE=TOOL_FAIL\n"
    t0 = db_now(); time.sleep(1)
    body = {"inputs": {"capability": "CONTENT_BRIEF", "entry": "", "capability_call": cc,
                       "professional_input": PROF, "example_reference_requested": "NO"},
            "response_mode": "blocking", "user": "m4-cl31-inj01"}
    try:
        res = FA.service_call(base, tok_seam, "/v1/workflows/run", body)
        err = None
    except Exception as e:
        res, err = {}, str(e)[:600]
    time.sleep(3)
    seam_execs = node_execs(seam_id, t0)
    child_execs = node_execs(child_id, t0)
    results["INJ-01"] = {
        "directive": "M4_FAULT_DIRECTIVE=TOOL_FAIL", "target": "EVAL-2 seam",
        "seam_app_id": seam_id, "child_app_id": child_id,
        "input_sha256": sha(cc), "service_error": err,
        "response": res,
        "seam_run_id": (res.get("data") or {}).get("workflow_run_id") or (res.get("data") or {}).get("id"),
        "seam_status": (res.get("data") or {}).get("status"),
        "seam_outputs": (res.get("data") or {}).get("outputs"),
        "seam_node_trace": [{k: v for k, v in n.items() if k != "outputs"} for n in seam_execs],
        "child_node_trace": [{k: v for k, v in n.items() if k != "outputs"} for n in child_execs],
        "child_runs": [{k: v for k, v in r.items() if k != "outputs"} for r in runs_of(child_id, t0)],
        "skill_llm_exec_count_child": sum(1 for n in child_execs if n["node_id"] == "skill_llm"),
        "recovery_llm_exec_count_child": sum(1 for n in child_execs if n["node_id"] == "recovery_llm"),
        "reached_end_tool_fail": any(n["node_id"] == "end_tool_fail" for n in seam_execs),
        "reached_seam_tool_fail": any(n["node_id"] == "seam_tool_fail" for n in seam_execs),
    }
    print("[INJ-01] seam_status=%s reached_end_tool_fail=%s skill_llm=%d recovery_llm=%d"
          % (results["INJ-01"]["seam_status"], results["INJ-01"]["reached_end_tool_fail"],
             results["INJ-01"]["skill_llm_exec_count_child"],
             results["INJ-01"]["recovery_llm_exec_count_child"]))

    # ── INJ-02 / INJ-03：直接跑 EVAL-1 子应用 ─────────────────────────────
    for tag, directive in (("INJ-02", "FROZEN_MARKERLESS"), ("INJ-03", "LIVE_MARKERLESS")):
        cc = FX.CT_M3 + "\nM4_FAULT_DIRECTIVE=%s\n" % directive
        t0 = db_now(); time.sleep(1)
        body = {"inputs": {"capability_call": cc, "professional_input": PROF,
                           "entry": "", "run_mode": "", "example_reference_requested": "NO"},
                "response_mode": "blocking", "user": "m4-cl31-%s" % tag.lower()}
        try:
            res = FA.service_call(base, tok_child, "/v1/workflows/run", body)
            err = None
        except Exception as e:
            res, err = {}, str(e)[:600]
        time.sleep(3)
        ex = node_execs(child_id, t0)
        d = (res.get("data") or {})
        results[tag] = {
            "directive": "M4_FAULT_DIRECTIVE=" + directive, "target": "EVAL-1 child",
            "child_app_id": child_id, "input_sha256": sha(cc), "service_error": err,
            "run_id": d.get("workflow_run_id") or d.get("id"), "status": d.get("status"),
            "outputs": d.get("outputs"),
            "node_trace": [{k: v for k, v in n.items() if k != "outputs"} for n in ex],
            "skill_llm_exec_count": sum(1 for n in ex if n["node_id"] == "skill_llm"),
            "recovery_llm_exec_count": sum(1 for n in ex if n["node_id"] == "recovery_llm"),
            "final_extract_exec_count": sum(1 for n in ex if n["node_id"] == "final_extract"),
            "returns_adapter_outputs": next((n["outputs"] for n in ex
                                             if n["node_id"] == "returns_adapter"), None),
        }
        o = d.get("outputs") or {}
        print("[%s] status=%s skill_llm=%d recovery_llm=%d delivery_outcome=%s ud_len=%d"
              % (tag, d.get("status"), results[tag]["skill_llm_exec_count"],
                 results[tag]["recovery_llm_exec_count"], o.get("delivery_outcome"),
                 len((o.get("user_delivery") or ""))))

    rec = {"contract": CONTRACT, "current_task_contract_hash": TASK_HASH,
           "sampling_clause": "无。每个注入指令只跑一次，失败即记录失败（v0.5 F-15）",
           "frozen_artifact_sha256": sha(INJ.frozen_artifact()),
           "runs": results}
    json.dump(rec, open(os.path.join(OUT, "CL31_RUNTIME_RAW.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=2, sort_keys=True)
    print("evidence -> decision-chain/evidence/m4/final_closure/CL31_RUNTIME_RAW.json")


if __name__ == "__main__":
    main()
