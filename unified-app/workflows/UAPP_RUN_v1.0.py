#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""在统一 Founder Canvas 里发一轮自然语言，并把真实发生的事原样取回。

**只发自然语言。** inputs 恒为空字典——用户不填 capability、entry、app_id、JSON。
运行后从 Dify 库里取回本轮实际执行的节点清单与各节点输入输出，
不靠模型自述、不靠"跑通了"当证据。
"""
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
APP_ID = "2448e4f9-818f-4b88-9311-d18546e97da9"


def _load(n, p):
    s = importlib.util.spec_from_file_location(n, p)
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m


DC = _load("uapp_dc", os.path.join(ROOT, "account-operations", "tools", "dify_client.py"))


def psql(sql, db="dify"):
    p = subprocess.run(["docker", "exec", "-i", "docker-db_postgres-1", "psql", "-U", "postgres",
                        "-d", db, "-tA", "-c", sql], capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError("psql: " + (p.stderr or "")[:300])
    return p.stdout.strip()


def upload(key, path, user):
    """把一份本地文件按 Dify 的用户上传通道传上去。这是**用户可见的正常产品动作**
    （Founder 上传自己的品牌资料），不是内部字段——AC-02 说的是不填内部字段，
    不是不许上传资料。"""
    import uuid as _uuid
    boundary = "----uapp" + _uuid.uuid4().hex
    name = os.path.basename(path)
    body = io.open(path, "rb").read()
    parts = []
    parts.append(("--%s\r\nContent-Disposition: form-data; name=\"user\"\r\n\r\n%s\r\n"
                  % (boundary, user)).encode("utf-8"))
    parts.append(("--%s\r\nContent-Disposition: form-data; name=\"file\"; filename=\"%s\"\r\n"
                  "Content-Type: text/markdown\r\n\r\n" % (boundary, name)).encode("utf-8"))
    parts.append(body)
    parts.append(("\r\n--%s--\r\n" % boundary).encode("utf-8"))
    raw = b"".join(parts)
    r = DC.http_json("POST", "/v1/files/upload",
                     headers={"Authorization": "Bearer " + key,
                              "Content-Type": "multipart/form-data; boundary=" + boundary},
                     raw_body=raw.decode("latin-1"), timeout=120)
    return r["status"], json.loads(r["body"]) if r["body"].strip().startswith("{") else r["body"]


def chat(key, query, user, conversation_id="", files=None, timeout=1800):
    body = {"inputs": {}, "query": query, "response_mode": "blocking", "user": user}
    if conversation_id:
        body["conversation_id"] = conversation_id
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
    """本轮实际执行了哪些节点。取自 Dify 的 workflow_node_executions，不是模型自述。"""
    wr = psql("select id from workflow_runs where triggered_from='debugging' or true "
              "order by created_at desc limit 1;")
    rows = psql(
        "select coalesce(w.id::text,'') from workflow_runs w "
        "join messages m on m.workflow_run_id = w.id where m.id='%s';" % message_id)
    run_id = rows.strip().splitlines()[0] if rows.strip() else wr
    raw = psql(
        "select json_agg(json_build_object("
        "'idx', e.index, 'node_id', e.node_id, 'title', e.title, 'type', e.node_type, "
        "'status', e.status, 'error', e.error, 'elapsed', e.elapsed_time, "
        "'inputs', e.inputs, 'outputs', e.outputs) order by e.index) "
        "from workflow_node_executions e where e.workflow_run_id='%s';" % run_id)
    try:
        return run_id, json.loads(raw or "[]")
    except Exception:
        return run_id, []


def main():
    tag = sys.argv[1] if len(sys.argv) > 1 else "slice01"
    query = sys.argv[2] if len(sys.argv) > 2 else (
        "我想把这周要发的内容定下来。帮我出一份内容制作依据。")
    conv = sys.argv[3] if len(sys.argv) > 3 else ""
    console = DC.Console(env=DC.load_env(ENV))
    key = console.app_api_key(APP_ID)
    # Dify 的会话按 end-user 隔离：续同一个 conversation 必须用同一个 user，
    # 换 user 会拿到 "Conversation Not Exists"。续跑时用 UAPP_USER 显式指定。
    user = os.environ.get("UAPP_USER") or ("uapp-exec-" + tag)

    files = None
    up_path = os.environ.get("UAPP_UPLOAD", "")
    up_info = None
    if up_path:
        st_u, up = upload(key, up_path, user)
        up_info = {"status": st_u, "id": (up or {}).get("id") if isinstance(up, dict) else None,
                   "name": os.path.basename(up_path)}
        if st_u in (200, 201) and isinstance(up, dict):
            files = [{"type": "document", "transfer_method": "local_file",
                      "upload_file_id": up["id"]}]
        else:
            raise SystemExit("上传失败，不继续跑：%s %s" % (st_u, str(up)[:300]))

    res = chat(key, query, user, conv, files=files)
    body = res["body"]
    mid = body.get("message_id") or ""
    cid = body.get("conversation_id") or ""
    run_id, nodes = trace(mid) if mid else ("", [])

    rec = {
        "tag": tag, "app_id": APP_ID, "user": user,
        "query": query, "conversation_id_in": conv, "uploaded_file": up_info,
        "http_status": res["http_status"], "elapsed_seconds": res["elapsed_seconds"],
        "message_id": mid, "conversation_id": cid, "workflow_run_id": run_id,
        "answer": body.get("answer"),
        "error": body.get("message") if res["http_status"] != 200 else None,
        "nodes_executed": [{"idx": n.get("idx"), "node_id": n.get("node_id"),
                            "title": n.get("title"), "type": n.get("type"),
                            "status": n.get("status"), "error": n.get("error"),
                            "elapsed": n.get("elapsed")} for n in nodes],
        "node_detail": nodes,
    }
    out = os.path.join(HERE, "..", "evidence", "UAPP_RUN_%s.json" % tag)
    if os.path.exists(out):
        raise SystemExit("拒绝覆盖已有运行证据：" + out)
    with io.open(out, "w", encoding="utf-8") as fh:
        fh.write(json.dumps(rec, ensure_ascii=False, indent=2) + "\n")
    print("HTTP", res["http_status"], "| elapsed", res["elapsed_seconds"], "s")
    print("conversation_id", cid)
    print("nodes executed:")
    for n in rec["nodes_executed"]:
        print("   %-3s %-20s %-18s %s %s" % (n["idx"], n["node_id"], n["type"],
                                             n["status"], (n["error"] or "")[:80]))
    print("--- ANSWER ---")
    print((body.get("answer") or "")[:3000])
    print("SAVED", out)


if __name__ == "__main__":
    main()
