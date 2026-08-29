#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Node S3｜按已冻结判据执行本层用例。只发起、只记录，不判定。

含一次**夹具写入**（SEED）：正例需要证明「有匹配投影可读取」，
而新建测试域天然是空的，所以必须先往 M2 写一条真实记录。
写入走 M2 正式 API、落在本会话自己的任务域内，请求与响应原样记录。
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
GATE = os.path.join(HERE, "..", "stages", "S3_STAGE_GATE_v1.0.json")
EV = os.path.join(HERE, "..", "evidence", "stages")
M2 = "http://diyu-m2-app:8000"

TRANSIENT = ("Server Unavailable", "SSLEOF", "UNEXPECTED_EOF", "Max retries exceeded",
             "Connection aborted", "Read timed out", "Remote end closed", "Bad gateway",
             "502", "503", "504")


def _load(n, p):
    s = importlib.util.spec_from_file_location(n, p)
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m


DC = _load("s3_dc", os.path.join(ROOT, "account-operations", "tools", "dify_client.py"))


def psql(sql, db="dify"):
    p = subprocess.run(["docker", "exec", "-i", "docker-db_postgres-1", "psql", "-U", "postgres",
                        "-d", db, "-tA", "-c", sql], capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError("psql: " + (p.stderr or "")[:300])
    return p.stdout.strip()


def m2_call(method, path, body=None, actor=None):
    """从 Dify api 容器内调 M2——与画布走的是同一条容器网络，不经用户 relay。"""
    cmd = ["curl", "-s", "-m", "30", "-X", method.upper(), M2 + path,
           "-H", "Content-Type: application/json", "-w", "\n__HTTP__%{http_code}"]
    if actor:
        cmd += ["-H", "X-Actor-Ref: " + actor]
    if body is not None:
        cmd += ["-d", json.dumps(body, ensure_ascii=False)]
    p = subprocess.run(["docker", "exec", "-i", "docker-api-1"] + cmd,
                       capture_output=True, text=True)
    raw = p.stdout
    code, txt = 0, raw
    if "__HTTP__" in raw:
        txt, _, c = raw.rpartition("__HTTP__")
        code = int(c.strip() or 0)
    try:
        parsed = json.loads(txt.strip() or "{}")
    except Exception:
        parsed = {"raw": txt[:2000]}
    return {"method": method.upper(), "path": path, "request_body": body,
            "http_status": code, "response": parsed}


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
    attempts = 0
    while attempts < 2:
        attempts += 1
        res = chat(key, query, user, conv)
        blob = json.dumps(res.get("body") or {}, ensure_ascii=False)
        mid = (res["body"] or {}).get("message_id") or ""
        if not (res["http_status"] != 200 and any(t in blob for t in TRANSIENT) and not mid):
            break
        print("  纯传输失败且无模型输出，按纪律重试一次")
    body = res["body"] or {}
    mid, cid = body.get("message_id") or "", body.get("conversation_id") or ""
    run_id, nodes = trace(mid) if mid else ("", [])
    return {"turn_id": tid, "query": query, "attempts": attempts,
            "http_status": res["http_status"], "elapsed_seconds": res["elapsed_seconds"],
            "message_id": mid, "conversation_id": cid, "workflow_run_id": run_id,
            "answer": body.get("answer"),
            "nodes_executed": [{"idx": n.get("idx"), "node_id": n.get("node_id"),
                                "type": n.get("type"), "status": n.get("status"),
                                "error": n.get("error")} for n in nodes],
            "node_detail": nodes}, cid


def J(x):
    if isinstance(x, str):
        try:
            return json.loads(x)
        except Exception:
            return {}
    return x if isinstance(x, dict) else {}


def node_out(turn, nid):
    for n in turn.get("node_detail") or []:
        if n.get("node_id") == nid:
            return J(n.get("outputs"))
    return {}


def run_case(key, g, case_id, turns, suffix, seed_after=None):
    out = os.path.join(EV, "%s.json" % case_id)
    if os.path.exists(out):
        raise SystemExit("拒绝覆盖已有证据：" + out)
    user, conv, recs, seed_rec = "s3-" + suffix, "", [], None
    for tid, q in turns:
        print("[%s/%s] %s" % (case_id, tid, q))
        rec, conv = one_turn(key, tid, q, user, conv)
        print("   http=%s %ss nodes=%s" % (rec["http_status"], rec["elapsed_seconds"],
                                           ",".join(n["node_id"] for n in rec["nodes_executed"])))
        recs.append(rec)
        if seed_after and tid == seed_after:
            seed_rec = do_seed(recs[-1])
            print("   SEED:", json.dumps({k: seed_rec[k] for k in ("targets", "write")},
                                         ensure_ascii=False)[:300])
    m3_runs = psql("select json_agg(json_build_object('id',w.id,'status',w.status,"
                   "'created_at',w.created_at)) from workflow_runs w "
                   "where w.app_id='a4c3b19b-243f-490b-9aca-3aa19767d6a5' "
                   "and w.created_at > now() - interval '30 minutes';")
    try:
        m3_runs = json.loads(m3_runs or "[]")
    except Exception:
        m3_runs = []
    doc = {"case_id": case_id, "stage": "S3", "stage_gate_sha256": g["_sha256"],
           "m3_app_workflow_runs_last_30min": m3_runs,
           "app_id": g["identity"]["successor_app_id"], "end_user": user,
           "conversation_id": conv, "seed": seed_rec,
           "run_started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "turns": recs,
           "note": "运行器只发起与记录，不判定。判定由 S3_ADJUDICATE 按冻结判据独立执行。"}
    with io.open(out, "w", encoding="utf-8") as fh:
        fh.write(json.dumps(doc, ensure_ascii=False, indent=2) + "\n")
    print("SAVED", out)


def do_seed(turn):
    """把一条真实的周期决策写进本会话自己的任务域。写入前后都原样取证。"""
    ws = node_out(turn, "boot_p2").get("id") or ""
    acct = node_out(turn, "boot_p3").get("id") or ""
    cyc = node_out(turn, "boot_p4").get("id") or ""
    actor = node_out(turn, "boot_p1").get("actor") or ""
    if not (ws and acct and cyc and actor):
        return {"status": "SKIPPED_NO_DOMAIN", "targets":
                {"ws": ws, "account": acct, "cycle": cyc, "actor": actor}}
    before = m2_call("GET", "/workspaces/%s/accounts/%s/cycles/decisions/latest" % (ws, acct),
                     actor=actor)
    # decision 是枚举，只接受 adjusted / kept_unchanged（attempt01 实测 422 原文：
    # "decision must be 'adjusted' or 'kept_unchanged'"）。散文放 rationale。
    body = {"idempotency_key": "s2-seed-" + cyc[:12], "cycle_id": cyc,
            # 第二次 422 原文：decision='adjusted' requires resulting_cycle_id。
            # 本夹具不产生新周期，所以正确取值是 kept_unchanged。
            # 该请求体已在画布之外用一次性探针域验证通过（200 + 数据库 1 行 + 重复写入同 id），
            # 零模型调用，见 docs/S2_FAILURE_TRIAGE_001.md 附录。
            "decision": "kept_unchanged",
            "source": "S2_STAGE_GATE_FIXTURE",
            "rationale": "本周期先把这个号的内容方向收敛到一条主线，停止同时铺三个方向。"
                         "（S2 正例夹具：证明 M2 里确有记录时投影能真实读到。任务域测试数据。）",
            "based_on": {"fixture": "S2-POS-01", "note": "非真实经营数据"}}
    write = m2_call("POST", "/workspaces/%s/accounts/%s/cycles/decisions" % (ws, acct),
                    body=body, actor=actor)
    after = m2_call("GET", "/workspaces/%s/accounts/%s/cycles/decisions/latest" % (ws, acct),
                    actor=actor)
    db = subprocess.run(["docker", "exec", "-i", "docker-db_postgres-1", "psql", "-U", "postgres",
                         "-d", "diyu_business", "-tA", "-c",
                         "select count(*) from cycle_decisions where idempotency_key='%s';"
                         % body["idempotency_key"]], capture_output=True, text=True).stdout.strip()
    return {"status": "DONE", "targets": {"ws": ws, "account": acct, "cycle": cyc, "actor": actor},
            "before": before, "write": write, "after": after,
            "db_rows_with_idempotency_key": db}


def main():
    g = gate()
    console = DC.Console(env=DC.load_env(ENV))
    key = console.app_api_key(g["identity"]["successor_app_id"])
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    if which in ("all", "main"):
        run_case(key, g, "S3-MAIN-01",
                 [("T1", "有个账号一直没流量，怎么办"), ("T2", "用对应的专业能力来分析")],
                 "main01", seed_after="T1")
    if which in ("all", "reg"):
        run_case(key, g, "S3-REG-ASK-01", [("R1", "这条我想再打磨一下")], "reg01")


if __name__ == "__main__":
    main()
