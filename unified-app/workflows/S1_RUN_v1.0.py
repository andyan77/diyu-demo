#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Node S1｜按已冻结判据执行本层用例。**只发起、只记录，不判定。**

三条硬纪律写进代码：
  1. Stage Gate 不存在 → 拒绝运行。判据必须早于结果（A2）。
  2. 证据文件已存在 → 拒绝覆盖。Attempt 只追加。
  3. 每个正式输入只跑一次。纯传输失败且无任何模型输出时才允许重试一次，两个 Attempt 都留。
"""
import hashlib
import importlib.util
import io
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
ENV = "/home/faye/diyu-demo-worktrees/m3-account-content-operator-v1/.env"
GATE = os.path.join(HERE, "..", "stages", "S1_STAGE_GATE_v1.0.json")
EV = os.path.join(HERE, "..", "evidence", "stages")

TRANSIENT = ("Server Unavailable", "SSLEOF", "UNEXPECTED_EOF", "Max retries exceeded",
             "Connection aborted", "Read timed out", "Remote end closed", "Bad gateway",
             "502", "503", "504")


def _load(n, p):
    s = importlib.util.spec_from_file_location(n, p)
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m


DC = _load("s1_dc", os.path.join(ROOT, "account-operations", "tools", "dify_client.py"))


def psql(sql, db="dify"):
    p = subprocess.run(["docker", "exec", "-i", "docker-db_postgres-1", "psql", "-U", "postgres",
                        "-d", db, "-tA", "-c", sql], capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError("psql: " + (p.stderr or "")[:300])
    return p.stdout.strip()


def gate():
    if not os.path.exists(GATE):
        raise SystemExit("Stage Gate 尚未冻结，拒绝执行：" + GATE)
    d = json.load(io.open(GATE, encoding="utf-8"))
    d["_sha256"] = hashlib.sha256(io.open(GATE, "rb").read()).hexdigest()
    return d


def chat(key, query, user, conv="", timeout=900):
    body = {"inputs": {}, "query": query, "response_mode": "blocking", "user": user}
    if conv:
        body["conversation_id"] = conv
    t0 = time.time()
    r = DC.http_json("POST", "/v1/chat-messages", headers={"Authorization": "Bearer " + key},
                     body=body, timeout=timeout)
    try:
        b = json.loads(r["body"])
    except Exception:
        b = {"raw": r["body"][:4000]}
    return {"http_status": r["status"], "elapsed_seconds": round(time.time() - t0, 2), "body": b}


def trace(message_id):
    run_id = psql("select coalesce(w.id::text,'') from workflow_runs w "
                  "join messages m on m.workflow_run_id = w.id where m.id='%s';" % message_id)
    run_id = run_id.strip().splitlines()[0] if run_id.strip() else ""
    if not run_id:
        return "", []
    raw = psql("select json_agg(json_build_object("
               "'idx', e.index, 'node_id', e.node_id, 'title', e.title, 'type', e.node_type, "
               "'status', e.status, 'error', e.error, 'elapsed', e.elapsed_time, "
               "'inputs', e.inputs, 'outputs', e.outputs) order by e.index) "
               "from workflow_node_executions e where e.workflow_run_id='%s';" % run_id)
    try:
        return run_id, json.loads(raw or "[]")
    except Exception:
        return run_id, []


def one_turn(key, tid, query, user, conv):
    attempts, records = 0, []
    while attempts < 2:
        attempts += 1
        res = chat(key, query, user, conv)
        blob = json.dumps(res.get("body") or {}, ensure_ascii=False)
        transient = res["http_status"] != 200 and any(t in blob for t in TRANSIENT)
        mid = (res["body"] or {}).get("message_id") or ""
        records.append({"attempt": attempts, "http_status": res["http_status"],
                        "elapsed_seconds": res["elapsed_seconds"],
                        "transient": transient, "message_id": mid})
        if not (transient and not mid):
            break
        print("  纯传输失败且无模型输出，按纪律重试一次")
    body = res["body"] or {}
    mid = body.get("message_id") or ""
    cid = body.get("conversation_id") or ""
    run_id, nodes = trace(mid) if mid else ("", [])
    return {"turn_id": tid, "query": query, "attempts": attempts, "attempt_records": records,
            "http_status": res["http_status"], "elapsed_seconds": res["elapsed_seconds"],
            "message_id": mid, "conversation_id": cid, "workflow_run_id": run_id,
            "answer": body.get("answer"),
            "error": body.get("message") if res["http_status"] != 200 else None,
            "nodes_executed": [{"idx": n.get("idx"), "node_id": n.get("node_id"),
                                "type": n.get("type"), "status": n.get("status"),
                                "error": n.get("error"), "elapsed": n.get("elapsed")}
                               for n in nodes],
            "node_detail": nodes}, cid


def run_case(console, key, g, case_id, turns, user_suffix):
    out = os.path.join(EV, "%s.json" % case_id)
    if os.path.exists(out):
        raise SystemExit("拒绝覆盖已有证据：" + out)
    app_id = g["identity"]["successor_app_id"]
    graph_now = psql("select md5(w.graph) from workflows w join apps a on a.workflow_id=w.id "
                     "where a.id='%s';" % app_id).strip()
    user = "s1-" + user_suffix
    conv, recs = "", []
    for tid, q in turns:
        print("[%s/%s] %s" % (case_id, tid, q))
        rec, conv = one_turn(key, tid, q, user, conv)
        print("   http=%s elapsed=%ss nodes=%s" % (
            rec["http_status"], rec["elapsed_seconds"],
            ",".join(n["node_id"] for n in rec["nodes_executed"])))
        recs.append(rec)
    doc = {"case_id": case_id, "stage": "S1",
           "stage_gate_sha256": g["_sha256"],
           "app_id": app_id, "graph_md5_at_run": graph_now,
           "end_user": user, "conversation_id": conv,
           "run_started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "turns": recs,
           "note": "运行器只发起与记录，不判定。判定由 S1_ADJUDICATE 按冻结判据独立执行。"}
    with io.open(out, "w", encoding="utf-8") as fh:
        fh.write(json.dumps(doc, ensure_ascii=False, indent=2) + "\n")
    print("SAVED", out)


def main():
    g = gate()
    console = DC.Console(env=DC.load_env(ENV))
    key = console.app_api_key(g["identity"]["successor_app_id"])
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    if which in ("all", "pos"):
        run_case(console, key, g, "S1-POS-01",
                 [("T1", g["cases"]["S1-POS-01"]["input"]),
                  ("T2", g["cases"]["S1-FOLLOW-01"]["input"])], "pos01")
    if which in ("all", "neg"):
        run_case(console, key, g, "S1-NEG-01",
                 [("N1", g["cases"]["S1-NEG-01"]["input"])], "neg01")


if __name__ == "__main__":
    main()
