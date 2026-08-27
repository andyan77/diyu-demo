#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""M4-CL31-02/03 Runtime 取证：断点续跑 + 从目标系统收集

N-24：进程被外部中断后**不盲重放**。先查目标系统已有副作用，只补跑缺失的注入指令。
v0.5 F-15：每个注入指令只跑一次；已存在的运行一律复用，不重抽、不挑选。
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

SEP = "\x01"
DIRECTIVES = {"INJ-01": "TOOL_FAIL", "INJ-02": "FROZEN_MARKERLESS", "INJ-03": "LIVE_MARKERLESS"}


def sha(s): return hashlib.sha256((s or "").encode("utf-8")).hexdigest()


def psql(sql):
    p = subprocess.run(["docker", "exec", "-i", "docker-db_postgres-1", "psql", "-U", "postgres",
                        "-d", "dify", "-t", "-A", "-F", SEP, "-c", sql], capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError(p.stderr[:500])
    return [l for l in p.stdout.split("\n") if l.strip()]


def qjson(sql):
    """用 psql 端 JSON 聚合取行。

    纪律（M4-FND-028）：早先版本用 -F 分隔符逐行切分，failed 运行的 error 字段含多行
    traceback，首行即错位并把整批**静默丢弃**（INJ-01 的两条子运行因此丢失）。
    分隔符解析对含换行的文本列不可用，改由数据库序列化，不在客户端猜边界。
    """
    p = subprocess.run(["docker", "exec", "-i", "docker-db_postgres-1", "psql", "-U", "postgres",
                        "-d", "dify", "-t", "-A", "-c",
                        "SELECT coalesce(json_agg(t)::text,'[]') FROM (%s) t;" % sql.rstrip(";")],
                       capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError(p.stderr[:500])
    return json.loads(p.stdout.strip() or "[]")


def runs_for(app_id, directive):
    return qjson("SELECT id AS run_id, status, coalesce(error,'') AS error, "
                 "created_at::text AS created_at, coalesce(outputs,'') AS outputs "
                 "FROM workflow_runs WHERE app_id='%s' "
                 "AND inputs LIKE '%%M4_FAULT_DIRECTIVE=%s%%' ORDER BY created_at"
                 % (app_id, directive))


def execs_for(run_id):
    return qjson("SELECT node_id, node_type, title, status, coalesce(error,'') AS error, "
                 "created_at::text AS created_at, coalesce(outputs,'') AS outputs "
                 "FROM workflow_node_executions WHERE workflow_run_id='%s' ORDER BY index"
                 % run_id)


def wait_idle(timeout=1500):
    t0 = time.time()
    while time.time() - t0 < timeout:
        n = psql("SELECT count(*) FROM workflow_runs r JOIN apps a ON a.id=r.app_id "
                 "WHERE a.name LIKE '%FAULT INJECTION%' AND r.status='running';")[0]
        if n == "0":
            return True
        time.sleep(10)
    return False


def main():
    objs = json.load(open(os.path.join(OUT, "INJECTION_OBJECTS.json"), encoding="utf-8"))
    ids = {p["tag"]: p["app_id"] for p in objs["published"]}
    child_id, seam_id = ids["EVAL-1"], ids["EVAL-2"]
    base = "http://127.0.0.1"
    PROF = "professional_input: 见 capability_call"

    print("等待在跑的注入运行结束…", flush=True)
    wait_idle()

    c = PUB.Console(); c.login()
    tok_child = FA.ensure_api_key(c, child_id)

    # ── 只补跑缺失的注入指令 ──────────────────────────────────────────────
    for tag in ("INJ-02", "INJ-03"):
        d = DIRECTIVES[tag]
        have = [r for r in runs_for(child_id, d) if r["status"] != "running"]
        if have:
            print("[%s] 目标系统已有 %d 次运行，复用，不重放" % (tag, len(have)), flush=True)
            continue
        cc = FX.CT_M3 + "\nM4_FAULT_DIRECTIVE=%s\n" % d
        print("[%s] 补跑…" % tag, flush=True)
        body = {"inputs": {"capability_call": cc, "professional_input": PROF, "entry": "",
                           "run_mode": "", "example_reference_requested": "NO"},
                "response_mode": "blocking", "user": "m4-cl31-%s" % tag.lower()}
        try:
            FA.service_call(base, tok_child, "/v1/workflows/run", body, timeout=900)
        except Exception as e:
            print("[%s] 服务调用异常：%s" % (tag, str(e)[:300]), flush=True)
        wait_idle()

    # ── 从目标系统收集全部三条 ────────────────────────────────────────────
    rec = {"contract": "V1_M4_EVIDENCE_COLLECTION_CONTRACT_v0.5.md",
           "current_task_contract_hash":
               "8d73b4f157883eb422e6ae17ececcf87a64d98c6a51f35537b8446155fa85070",
           "sampling_clause": "无。每个注入指令只保留目标系统上的全部运行，不挑选、不重抽（v0.5 F-15）",
           "frozen_artifact_sha256": sha(INJ.frozen_artifact()),
           "frozen_input_sha256": {t: sha(FX.CT_M3 + "\nM4_FAULT_DIRECTIVE=%s\n" % d)
                                   for t, d in DIRECTIVES.items()},
           "eval_app_ids": {"child": child_id, "seam": seam_id}, "runs": {}}

    for tag, d in DIRECTIVES.items():
        entry = {"directive": "M4_FAULT_DIRECTIVE=" + d, "seam_runs": [], "child_runs": []}
        for r in runs_for(seam_id, d):
            r["node_executions"] = execs_for(r["run_id"]); entry["seam_runs"].append(r)
        for r in runs_for(child_id, d):
            r["node_executions"] = execs_for(r["run_id"]); entry["child_runs"].append(r)
        entry["child_run_count"] = len(entry["child_runs"])
        entry["skill_llm_exec_total"] = sum(
            1 for r in entry["child_runs"] for e in r["node_executions"] if e["node_id"] == "skill_llm")
        entry["recovery_llm_exec_total"] = sum(
            1 for r in entry["child_runs"] for e in r["node_executions"] if e["node_id"] == "recovery_llm")
        rec["runs"][tag] = entry
        print("[%s] seam_runs=%d child_runs=%d skill_llm=%d recovery_llm=%d"
              % (tag, len(entry["seam_runs"]), len(entry["child_runs"]),
                 entry["skill_llm_exec_total"], entry["recovery_llm_exec_total"]), flush=True)

    p = os.path.join(OUT, "CL31_RUNTIME_RAW.json")
    json.dump(rec, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=2, sort_keys=True)
    print("evidence ->", os.path.relpath(p, ROOT), flush=True)


if __name__ == "__main__":
    main()
