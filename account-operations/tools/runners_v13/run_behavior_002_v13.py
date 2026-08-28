#!/usr/bin/env python3
"""EP-06 behaviour half: execute the FROZEN ECC-M3-RUNTIME-BEHAVIOR-002 case set
through the task-specific Dify candidate app. Records raw transcripts only —
no PASS/FAIL judgement is made here (frozen protocol §5.1)."""
import json
import os
import re
import sys
import time
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor

WORKTREE = "/home/faye/diyu-demo-worktrees/m3-account-content-operator-v1"
V12 = os.path.dirname(os.path.abspath(__file__))
SCRATCH = os.path.dirname(V12)          # 脚本搬到 v12/ 之后，共用模块仍在上一层
EVID = os.path.join(WORKTREE, "account-operations/evidence/ep06b-runtime-behavior-v13")
SPEC_DIR = os.path.join(WORKTREE, "account-operations/evidence/ep06b-runtime-behavior-v11")
SKILL_DIR = os.path.join(WORKTREE, "account-operations/skills/operating-one-account")
SERVICE_URL = "http://localhost/v1/workflows/run"
APP_ID = "b7fb5b1a-9278-426c-bb8a-f9f288639548"

# 闸门与投影的唯一真源是仓库里的 gate_v13/，不是 scratch 副本——
# 上一轮出过一次「跑的和仓库里的不是同一份」，源头钉在仓库侧就不会再有。
GATE_SRC = os.path.join(WORKTREE, "account-operations/tools/gate_v13")
sys.path.insert(0, GATE_SRC)
sys.path.insert(0, SCRATCH)
sys.path.insert(0, V12)
from manifest import build_refs  # noqa: E402


def read(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


def run_workflow(key, inputs, user):
    payload = {"inputs": inputs, "response_mode": "blocking", "user": user}
    req = urllib.request.Request(
        SERVICE_URL, data=json.dumps(payload).encode("utf-8"),
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        method="POST")
    start = time.time()
    try:
        with urllib.request.urlopen(req, timeout=1200) as resp:
            return {"status": resp.status, "body": json.loads(resp.read().decode("utf-8")),
                    "elapsed_seconds": round(time.time() - start, 2)}
    except urllib.error.HTTPError as e:
        return {"status": e.code, "body": {"error": e.read().decode("utf-8")},
                "elapsed_seconds": round(time.time() - start, 2)}
    except Exception as e:  # noqa: BLE001 - record transport failure as evidence, do not hide it
        return {"status": -1, "body": {"error": f"{type(e).__name__}: {e}"},
                "elapsed_seconds": round(time.time() - start, 2)}


TRANSPORT_RETRY_MAX = 2          # 只对"没有产出"的传输/上游断连重试，不对内容重试
TRANSPORT_RETRY_SLEEP = 20


def _is_transport_failure(res):
    """True 仅当这一次调用根本没产出模型正文（传输层或上游断连），
    而不是'产出了但内容不好'。后者绝不重试——那是择优。"""
    if res["status"] != 200:
        return True
    d = res["body"].get("data", {}) if isinstance(res["body"], dict) else {}
    if d.get("status") == "succeeded":
        return False
    err = str(d.get("error") or "")
    return bool(re.search(r"SSLEOFError|UNEXPECTED_EOF|Server Unavailable|"
                          r"Max retries exceeded|Connection|Timeout|timed out", err, re.I))


def run_workflow_with_retry(key, inputs, user):
    attempts = []
    for i in range(TRANSPORT_RETRY_MAX + 1):
        res = run_workflow(key, inputs, f"{user}-a{i}" if i else user)
        d = res["body"].get("data", {}) if isinstance(res["body"], dict) else {}
        attempts.append({"attempt": i + 1, "http_status": res["status"],
                         "workflow_status": d.get("status"),
                         "error": d.get("error"), "elapsed_seconds": res["elapsed_seconds"]})
        if not _is_transport_failure(res):
            res["attempts"] = attempts
            return res
        if i < TRANSPORT_RETRY_MAX:
            print(f"    transport failure, retry {i+1}/{TRANSPORT_RETRY_MAX} in "
                  f"{TRANSPORT_RETRY_SLEEP}s: {str(d.get('error'))[:90]}",
                  file=sys.stderr, flush=True)
            time.sleep(TRANSPORT_RETRY_SLEEP)
    res["attempts"] = attempts
    return res


def main():
    key = read(os.path.join(SCRATCH, "m3_app_key.txt")).strip()
    # 输出目录必须存在且为空：非空说明有上一次残留，混进来会造成产地不明
    os.makedirs(EVID, exist_ok=True)
    leftover = [f for f in os.listdir(EVID) if not f.startswith('.')]
    if leftover:
        raise SystemExit(f"REFUSE: {EVID} 非空（{len(leftover)} 项），先清空或换目录，不混跑")

    fashion = read(os.path.join(SKILL_DIR, "references/fashion-and-market.md"))
    # 判据用**先冻结的版本化 Oracle v2**，不是上一轮那份就地改过的 _cases.json。
    # Founder 第 3 条逐字：更正后的 Oracle 必须版本化、先冻结，再重跑受影响取证。
    oracle_path = os.path.join(WORKTREE, "account-operations/evidence/_oracle/BEHAVIOR_CASES_v2.json")
    spec = json.load(open(oracle_path, encoding="utf-8"))
    import hashlib
    oracle_sha = hashlib.sha256(open(oracle_path, "rb").read()).hexdigest()
    print("oracle:", os.path.basename(oracle_path), "v" + spec["oracle_meta"]["oracle_version"],
          "sha256", oracle_sha[:16], file=sys.stderr)
    cases = spec["cases"]

    def one(case):
        refs = build_refs(case["include_fashion_ref"], fashion)
        inputs = {"account_context": case["account_context"],
                  "user_request": case["user_request"],
                  "loaded_references": refs}
        print(f"start {case['case_id']}", file=sys.stderr, flush=True)
        res = run_workflow_with_retry(key, inputs, f"m3-ep06b-{case['case_id']}")
        data = res["body"].get("data", {}) if isinstance(res["body"], dict) else {}
        rec = {"case_id": case["case_id"], "bound_ac": case["bound_ac"], "fixture": case["fixture"],
               "carrier": "dify_workflow", "dify_app_id": APP_ID,
               "model": "deepseek-v4-flash", "provider": "langgenius/deepseek/deepseek",
               "temperature": 0.4, "include_fashion_ref": case["include_fashion_ref"],
               "workflow_inputs": inputs, "http_status": res["status"],
               "elapsed_seconds": res["elapsed_seconds"], "raw_response_body": res["body"],
               "transport_attempts": res.get("attempts"),
               "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
        with open(os.path.join(EVID, f"{case['case_id']}.json"), "w", encoding="utf-8") as f:
            json.dump(rec, f, ensure_ascii=False, indent=2)
        print(f"  done {case['case_id']} {res['status']} {data.get('status')} "
              f"tok={data.get('total_tokens')} {res['elapsed_seconds']}s", file=sys.stderr, flush=True)
        return {"case_id": case["case_id"], "bound_ac": case["bound_ac"],
                "http_status": res["status"], "workflow_status": data.get("status"),
                "error": data.get("error"), "total_tokens": data.get("total_tokens"),
                "workflow_run_id": res["body"].get("workflow_run_id") if isinstance(res["body"], dict) else None,
                "elapsed_seconds": res["elapsed_seconds"]}

    with ThreadPoolExecutor(max_workers=3) as ex:
        index = list(ex.map(one, cases))

    with open(os.path.join(EVID, "_run_index.json"), "w", encoding="utf-8") as f:
        json.dump({"ecc_id": spec["ecc_id"], "carrier": "dify_workflow", "dify_app_id": APP_ID,
                   "oracle_file": "account-operations/evidence/_oracle/BEHAVIOR_CASES_v2.json",
                   "oracle_version": spec["oracle_meta"]["oracle_version"],
                   "oracle_sha256_at_run": oracle_sha, "total_cases": len(cases),
                   "total_tokens": sum((r.get("total_tokens") or 0) for r in index),
                   "failed": [r["case_id"] for r in index if r["workflow_status"] != "succeeded"],
                   "cases": index}, f, ensure_ascii=False, indent=2)
    bad = [r for r in index if r["workflow_status"] != "succeeded"]
    print(f"\ndone. {len(cases)} cases, {len(bad)} not succeeded", file=sys.stderr)


if __name__ == "__main__":
    main()
