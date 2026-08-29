#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Node S4.2｜逐项开放其余五项专业能力。只发起、只记录，不判定。

每项能力两例，只差「事实是否在场」这一个变量：
  正例 = 上传夹具品牌事实 + 自然语言任务
  负例 = 同一句自然语言、不上传任何资料

夹具走 Dify 的用户上传通道进入，不写进提示词、不塞进代码——
执行侧不得补写夹具未提供的商品、价格、面料、顾客或经营事实。
"""
import hashlib
import importlib.util
import io
import json
import os
import subprocess
import sys
import time
import uuid as _uuid

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
ENV = "/home/faye/diyu-demo-worktrees/m3-account-content-operator-v1/.env"
GATE = os.path.join(HERE, "..", "stages", "S4_2_STAGE_GATE_v1.1.json")
EV = os.path.join(HERE, "..", "evidence", "stages")
FIXTURE = os.path.join(ROOT, "decision-chain", "fixtures", "一页纸夹具品牌事实 v0.1.md")

TRANSIENT = ("Server Unavailable", "SSLEOF", "UNEXPECTED_EOF", "Max retries exceeded",
             "Connection aborted", "Read timed out", "Remote end closed", "Bad gateway",
             "502", "503", "504")

APPS = {"M3": "a4c3b19b-243f-490b-9aca-3aa19767d6a5",
        "HOP": "6c46fdb1-5f49-4513-a0c0-29957b3dcee4",
        "SEAM": "5fca0162-e26b-4545-a00b-66b1a2a2a077",
        "MATRIX": "fd25ebfa-db67-40c3-82e5-202e1254facf",
        "CAMPAIGN": "1f9d65ea-8af5-45f0-a1d0-a80223d354e2",
        "CONTENT_BRIEF": "b1dcf784-540e-4b3f-8ba2-3812f477f3ce",
        "CREATIVE_SCRIPT": "44b55f9d-3792-40c3-b095-f2696464b4ec",
        "PRODUCTION_DIRECTOR": "13cfabd5-f592-4354-a304-47098b765697",
        "PUBLISHING_PACKAGING": "c9cdea24-9df3-400b-9ecd-1d740e8c96df"}


def _load(n, p):
    s = importlib.util.spec_from_file_location(n, p)
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m


DC = _load("s42_dc", os.path.join(ROOT, "account-operations", "tools", "dify_client.py"))


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


def upload(key, path, user):
    """按 Dify 的用户上传通道传一份资料。这是用户可见的正常产品动作。"""
    boundary = "----uapp" + _uuid.uuid4().hex
    name = os.path.basename(path)
    # 整个多部分体全程按 str 组装。dify_client._direct 会对 data 做一次
    # data.encode("utf-8")，那一次就是唯一的编码。
    # 曾经的写法是把文件字节 .decode("latin-1") 塞进同一个通道，
    # 于是原始 UTF-8 字节先被逐字节映射成 U+0080–U+00FF、再整体编码一次——
    # 夹具以双倍体积的乱码落库（11780 vs 6119），从未以可读形式进入系统。
    # 见 S4_2_FAILURE_TRIAGE_001.md R1。
    text = io.open(path, encoding="utf-8").read()
    raw = ("--%s\r\nContent-Disposition: form-data; name=\"user\"\r\n\r\n%s\r\n"
           % (boundary, user)
           + "--%s\r\nContent-Disposition: form-data; name=\"file\"; filename=\"%s\"\r\n"
             "Content-Type: text/markdown; charset=utf-8\r\n\r\n" % (boundary, name)
           + text
           + "\r\n--%s--\r\n" % boundary)
    r = DC.http_json("POST", "/v1/files/upload",
                     headers={"Authorization": "Bearer " + key,
                              "Content-Type": "multipart/form-data; boundary=" + boundary},
                     raw_body=raw, timeout=180)
    try:
        b = json.loads(r["body"])
    except Exception:
        b = {"raw": r["body"][:500]}
    return r["status"], b


def chat(key, query, user, files=None, timeout=1200):
    body = {"inputs": {}, "query": query, "response_mode": "blocking", "user": user}
    if files:
        body["files"] = files
    t0 = time.time()
    r = DC.http_json("POST", "/v1/chat-messages", headers={"Authorization": "Bearer " + key},
                     body=body, timeout=timeout)
    try:
        b = json.loads(r["body"])
    except Exception:
        b = {"raw": r["body"][:4000]}
    return {"http_status": r["status"], "elapsed_seconds": round(time.time() - t0, 2), "body": b}


def trace(message_id):
    rid = psql("select coalesce(w.id::text,'') from workflow_runs w "
               "join messages m on m.workflow_run_id = w.id where m.id='%s';" % message_id)
    rid = rid.strip().splitlines()[0] if rid.strip() else ""
    if not rid:
        return "", []
    raw = psql("select json_agg(json_build_object('idx',e.index,'node_id',e.node_id,"
               "'title',e.title,'type',e.node_type,'status',e.status,'error',e.error,"
               "'inputs',e.inputs,'outputs',e.outputs) order by e.index) "
               "from workflow_node_executions e where e.workflow_run_id='%s';" % rid)
    try:
        return rid, json.loads(raw or "[]")
    except Exception:
        return rid, []


def nodes_of(run_id):
    raw = psql("select json_agg(json_build_object('idx',e.index,'node_id',e.node_id,"
               "'type',e.node_type,'status',e.status,'error',e.error) order by e.index) "
               "from workflow_node_executions e where e.workflow_run_id='%s';" % run_id)
    try:
        return json.loads(raw or "[]") or []
    except Exception:
        return []


def runs_since(app_id, ts):
    raw = psql("select json_agg(json_build_object('id',w.id,'status',w.status,"
               "'created_at',w.created_at) order by w.created_at desc) from workflow_runs w "
               "where w.app_id='%s' and w.created_at > timestamp '%s';" % (app_id, ts))
    try:
        return json.loads(raw or "[]") or []
    except Exception:
        return []


def run_case(key, g, case_id, cap, query, with_fixture):
    out = os.path.join(EV, "%s.json" % case_id)
    if os.path.exists(out):
        raise SystemExit("拒绝覆盖已有证据：" + out)
    user = "s42-" + case_id.lower().replace("_", "-")
    t_start = psql("select now()::text;")
    up = None
    files = None
    if with_fixture:
        st, body = upload(key, FIXTURE, user)
        up = {"http_status": st, "file_id": (body or {}).get("id"),
              "name": os.path.basename(FIXTURE),
              "sha256": hashlib.sha256(io.open(FIXTURE, "rb").read()).hexdigest()}
        if st not in (200, 201) or not up["file_id"]:
            raise SystemExit("夹具上传失败，拒绝继续：%s %s" % (st, str(body)[:300]))
        files = [{"type": "document", "transfer_method": "local_file",
                  "upload_file_id": up["file_id"]}]

    attempts = 0
    while attempts < 2:
        attempts += 1
        res = chat(key, query, user, files=files)
        blob = json.dumps(res.get("body") or {}, ensure_ascii=False)
        mid = (res["body"] or {}).get("message_id") or ""
        if not (res["http_status"] != 200 and any(t in blob for t in TRANSIENT) and not mid):
            break
        print("   纯传输失败且无模型输出，按纪律重试一次")

    body = res["body"] or {}
    mid = body.get("message_id") or ""
    rid, nodes = trace(mid) if mid else ("", [])
    nested = {}
    for k, aid in APPS.items():
        rs = runs_since(aid, t_start)
        item = {"app_id": aid, "runs_during_case": rs}
        if k == "SEAM" and rs:
            item["latest_run_nodes"] = nodes_of(rs[0]["id"])
        nested[k] = item

    doc = {"case_id": case_id, "stage": "S4.2", "capability": cap,
           "with_fixture": with_fixture, "stage_gate_sha256": g["_sha256"],
           "app_id": g["identity"]["successor_app_id"], "end_user": user,
           "query": query, "uploaded_fixture": up,
           "window_start": t_start,
           "http_status": res["http_status"], "elapsed_seconds": res["elapsed_seconds"],
           "attempts": attempts, "message_id": mid, "workflow_run_id": rid,
           "conversation_id": body.get("conversation_id"),
           "answer": body.get("answer"),
           "nodes_executed": [{"idx": n.get("idx"), "node_id": n.get("node_id"),
                               "type": n.get("type"), "status": n.get("status"),
                               "error": n.get("error")} for n in nodes],
           "node_detail": nodes, "nested_app_runs": nested,
           "note": "运行器只发起与记录，不判定。判定由 S4_2_ADJUDICATE 按冻结判据独立执行。"}
    with io.open(out, "w", encoding="utf-8") as fh:
        fh.write(json.dumps(doc, ensure_ascii=False, indent=2) + "\n")
    seam_nodes = [n["node_id"] for n in (nested.get("SEAM") or {}).get("latest_run_nodes") or []]
    print("   http=%s %ss | seam nodes=%s" % (res["http_status"], res["elapsed_seconds"],
                                              [x for x in seam_nodes if x.startswith("tool_")]))
    print("   SAVED", os.path.basename(out))


def main():
    g = gate()
    console = DC.Console(env=DC.load_env(ENV))
    key = console.app_api_key(g["identity"]["successor_app_id"])
    only = sys.argv[1] if len(sys.argv) > 1 else ""
    for cap, spec in g["capabilities"].items():
        if only and only != cap:
            continue
        for kind, with_fx in (("POS", True), ("NEG", False)):
            cid = "S4-CAP-%s-%s" % (cap, kind)
            if os.path.exists(os.path.join(EV, cid + ".json")):
                print("[skip 已有证据] %s" % cid)
                continue
            print("[%s] %s | fixture=%s" % (cid, spec["input"], with_fx))
            run_case(key, g, cid, cap, spec["input"], with_fx)


if __name__ == "__main__":
    main()
