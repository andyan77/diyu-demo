#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""按**已冻结**的判据执行正式用例，并原样保存证据。

三条硬纪律，写进代码而不是写进文档：
  1. 判据文件不存在 → 拒绝运行。判据必须早于结果（A2）。
  2. 证据文件已存在 → 拒绝覆盖。历史 Attempt 只追加。
  3. 每个正式输入只跑一次。纯传输失败且没有任何模型输出时才允许重试一次，
     两个 Attempt 都留在证据里。业务失败**一律不重试**——重试就是掩盖。
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
EV = os.path.join(HERE, "..", "evidence", "formal")
DOCS = os.path.join(HERE, "..", "docs")
ENV = "/home/faye/diyu-demo-worktrees/m3-account-content-operator-v1/.env"
APP_ID = "2448e4f9-818f-4b88-9311-d18546e97da9"
SCENARIOS_VERSION = os.environ.get("UAPP_SCENARIOS_VERSION", "v1.0")

RUNNER = importlib.util.spec_from_file_location(
    "uapp_runner", os.path.join(HERE, "UAPP_RUN_v1.0.py"))
_R = importlib.util.module_from_spec(RUNNER)
RUNNER.loader.exec_module(_R)
DC = _R.DC

# 只有这些是传输层/模型可用性故障，可以重试一次。业务结果一律不重试。
TRANSIENT = ("Server Unavailable", "SSLEOF", "UNEXPECTED_EOF", "Max retries exceeded",
             "Connection aborted", "Read timed out", "Remote end closed", "Bad gateway",
             "502", "503", "504")


def frozen():
    p = os.path.join(DOCS, "UAPP_FROZEN_SCENARIOS_%s.json" % SCENARIOS_VERSION)
    if not os.path.exists(p):
        raise SystemExit("判据尚未冻结，拒绝执行正式运行：" + p)
    doc = json.load(io.open(p, encoding="utf-8"))
    doc["_sha256"] = hashlib.sha256(io.open(p, "rb").read()).hexdigest()
    doc["_path"] = p
    return doc


def is_transient(res):
    if res["http_status"] == 200:
        return False
    blob = json.dumps(res.get("body") or {}, ensure_ascii=False)
    return any(t in blob for t in TRANSIENT)


def one_turn(key, query, user, conv, upload_path=None):
    files = None
    up_info = None
    if upload_path:
        st_u, up = _R.upload(key, upload_path, user)
        up_info = {"status": st_u, "name": os.path.basename(upload_path),
                   "id": up.get("id") if isinstance(up, dict) else None}
        if st_u not in (200, 201):
            raise SystemExit("上传失败：%s %s" % (st_u, str(up)[:300]))
        files = [{"type": "document", "transfer_method": "local_file",
                  "upload_file_id": up["id"]}]

    attempts = []
    res = _R.chat(key, query, user, conv, files=files)
    attempts.append(res)
    if res["http_status"] != 200 and is_transient(res):
        # 纯传输失败且没有模型输出：允许重试一次，两个 Attempt 都保留。
        time.sleep(5)
        attempts.append(_R.chat(key, query, user, conv, files=files))
        res = attempts[-1]

    body = res["body"]
    mid = body.get("message_id") or ""
    run_id, nodes = _R.trace(mid) if mid else ("", [])
    return {
        "query": query, "uploaded_file": up_info,
        "attempts": len(attempts), "attempt_records": attempts,
        "http_status": res["http_status"], "elapsed_seconds": res["elapsed_seconds"],
        "message_id": mid, "conversation_id": body.get("conversation_id") or "",
        "workflow_run_id": run_id, "answer": body.get("answer"),
        "nodes_executed": [{"idx": n.get("idx"), "node_id": n.get("node_id"),
                            "type": n.get("type"), "status": n.get("status"),
                            "error": n.get("error")} for n in nodes],
        "node_detail": nodes,
    }


def m2_rows(where_sql):
    p = subprocess.run(["docker", "exec", "-i", "docker-db_postgres-1", "psql", "-U", "postgres",
                        "-d", "diyu_business", "-tA", "-c", where_sql],
                       capture_output=True, text=True)
    return p.stdout.strip()


def main():
    if len(sys.argv) < 2:
        raise SystemExit("用法：UAPP_FORMAL_RUN_v1.0.py <case_id> [conversation_id]")
    case_id = sys.argv[1]
    conv = sys.argv[2] if len(sys.argv) > 2 else ""
    doc = frozen()

    # 冻结取样规则允许对纯传输失败补一次 Attempt。补跑写**新文件**，
    # 原 Attempt 一个字节都不动——历史 Attempt 只追加。
    attempt = os.environ.get("UAPP_ATTEMPT", "")
    suffix = ("_attempt%s" % attempt) if attempt else ""
    out = os.path.join(EV, "%s%s.json" % (case_id, suffix))
    if os.path.exists(out):
        raise SystemExit("拒绝覆盖已有正式证据：" + out)

    # 从冻结判据里取本例的输入，绝不在这里就地编输入。
    sc = doc["scenarios"]
    turns, expected_cap, binds, passc, failc, purpose = [], None, [], [], [], ""
    if case_id.startswith("UAPP-CAP-"):
        blk = sc["UAPP-CAP"]
        hit = [c for c in blk["cases"] if c["id"] == case_id]
        if not hit:
            raise SystemExit("冻结判据里没有这个用例：" + case_id)
        turns = [{"id": case_id, "input": hit[0]["input"]}]
        expected_cap = hit[0]["expected_capability"]
        binds, passc, failc, purpose = blk["binds"], blk["pass"], blk["fail"], blk["purpose"]
    elif case_id.startswith("UAPP-EQUIV-01"):
        blk = sc["UAPP-EQUIV-01"]
        pool = blk["positive"] + [blk["negative"]]
        hit = [c for c in pool if c["id"] == case_id]
        if not hit:
            raise SystemExit("冻结判据里没有这个用例：" + case_id)
        turns = [{"id": case_id, "input": hit[0]["input"]}]
        binds, passc, failc, purpose = blk["binds"], blk["pass"], blk["fail"], blk["purpose"]
    else:
        blk = sc.get(case_id)
        if not blk:
            raise SystemExit("冻结判据里没有这个用例：" + case_id)
        turns = blk["turns"]
        binds, passc, failc, purpose = blk["binds"], blk["pass"], blk["fail"], blk["purpose"]

    console = DC.Console(env=DC.load_env(ENV))
    key = console.app_api_key(APP_ID)
    user = os.environ.get("UAPP_USER") or ("uapp-formal-" + case_id.lower())
    upload_path = os.environ.get("UAPP_UPLOAD") or None

    records = []
    for i, t in enumerate(turns):
        rec = one_turn(key, t["input"], user, conv,
                       upload_path if (i == 0 and upload_path) else None)
        rec["turn_id"] = t["id"]
        conv = rec["conversation_id"] or conv
        records.append(rec)
        print("[%s] turn %s http=%s nodes=%d elapsed=%.1fs" % (
            case_id, t["id"], rec["http_status"], len(rec["nodes_executed"]),
            rec["elapsed_seconds"]))

    doc_out = {
        "case_id": case_id, "attempt": attempt or "1", "purpose": purpose, "binds": binds,
        "frozen_criteria": {"path": os.path.basename(doc["_path"]), "sha256": doc["_sha256"],
                            "pass": passc, "fail": failc,
                            "expected_capability": expected_cap},
        "app_id": APP_ID, "end_user": user, "conversation_id": conv,
        "turns": records,
        "m2_snapshot": {
            "artifacts": m2_rows("select count(*) from artifacts;"),
            "content_versions": m2_rows("select count(*) from content_versions;"),
            "publish_instances": m2_rows("select count(*) from publish_instances;"),
            "feedback": m2_rows("select count(*) from feedback_records;"),
        },
        "note": "本文件只记录发生了什么，不在这里下 PASS/FAIL 判定；判定按冻结判据另行落盘。",
    }
    with io.open(out, "w", encoding="utf-8") as fh:
        fh.write(json.dumps(doc_out, ensure_ascii=False, indent=2) + "\n")
    print("SAVED", out)


if __name__ == "__main__":
    main()
