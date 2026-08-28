#!/usr/bin/env python3
"""EP-06 (Dify binding): re-run the ALREADY-FROZEN ECC-M3-RUNTIME-FIDELITY-001
seven groups / nine cases through the task-specific Dify candidate app.

Criteria are NOT re-frozen and NOT modified — `M3_ECC_RUNTIME_FIDELITY_001_FROZEN_v1.0.md`
stays byte-identical. Only the *binding* changes (locked variable "Workflow 图"):
round 1/2 ran Skill -> conditional reference -> direct DeepSeek API;
this round runs Skill -> conditional reference -> Dify Workflow graph -> Dify -> DeepSeek.

Case inputs are imported verbatim from the round-2 harness so the only variable
that moves is the carrier.
"""
import json
import os
import sys
import time
import urllib.request
import urllib.error

_V12 = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _V12)                                  # v12/：本轮闸门与投影
sys.path.insert(0, os.path.dirname(_V12))                 # m3/：manifest、dify_client
sys.path.insert(0, os.path.dirname(os.path.dirname(_V12)))  # scratchpad/：EP-06 冻结用例集
from manifest import build_refs  # noqa: E402

from ep06_runtime_fidelity_v2 import CASES, SKILL_DIR, read  # noqa: E402

WORKTREE = "/home/faye/diyu-demo-worktrees/m3-account-content-operator-v1"
V12 = os.path.dirname(os.path.abspath(__file__))
SCRATCH = os.path.dirname(V12)          # 脚本搬到 v12/ 之后，共用模块仍在上一层
EVIDENCE_DIR = os.path.join(WORKTREE, "account-operations/evidence/ep06-runtime-fidelity-dify-v14")
SERVICE_URL = "http://localhost/v1/workflows/run"
APP_ID = "b7fb5b1a-9278-426c-bb8a-f9f288639548"


def run_workflow(key, inputs, user):
    payload = {"inputs": inputs, "response_mode": "blocking", "user": user}
    req = urllib.request.Request(
        SERVICE_URL, data=json.dumps(payload).encode("utf-8"),
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        method="POST",
    )
    start = time.time()
    try:
        with urllib.request.urlopen(req, timeout=900) as resp:
            body = json.loads(resp.read().decode("utf-8"))
            status = resp.status
    except urllib.error.HTTPError as e:
        body = {"error": e.read().decode("utf-8")}
        status = e.code
    return {"status": status, "body": body, "elapsed_seconds": round(time.time() - start, 2)}


def main():
    key = read(os.path.join(SCRATCH, "m3_app_key.txt")).strip()
    fashion = read(os.path.join(SKILL_DIR, "references/fashion-and-market.md"))
    os.makedirs(EVIDENCE_DIR, exist_ok=True)

    from concurrent.futures import ThreadPoolExecutor

    def one(case):
        refs = build_refs(case["include_fashion_ref"], fashion)
        inputs = {
            "account_context": case["context"],
            "user_request": case["user"],
            "loaded_references": refs,
        }
        print(f"=== dify {case['id']} start ===", file=sys.stderr, flush=True)
        res = run_workflow(key, inputs, f"m3-ep06-dify-{case['id']}")
        data = res["body"].get("data", {}) if isinstance(res["body"], dict) else {}
        record = {
            "case_id": case["id"],
            "carrier": "dify_workflow",
            "dify_app_id": APP_ID,
            "dify_service_url": SERVICE_URL,
            "model": "deepseek-v4-flash",
            "provider": "langgenius/deepseek/deepseek",
            "temperature": 0.4,
            "include_fashion_ref": case["include_fashion_ref"],
            "workflow_inputs": inputs,
            "http_status": res["status"],
            "elapsed_seconds": res["elapsed_seconds"],
            "raw_response_body": res["body"],
            "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }
        with open(os.path.join(EVIDENCE_DIR, f"{case['id']}.json"), "w", encoding="utf-8") as f:
            json.dump(record, f, ensure_ascii=False, indent=2)
        print(f"    done {case['id']} {res['status']} {data.get('status')} "
              f"tokens={data.get('total_tokens')} {res['elapsed_seconds']}s", file=sys.stderr, flush=True)
        return {
            "case_id": case["id"], "http_status": res["status"],
            "workflow_status": data.get("status"), "error": data.get("error"),
            "total_tokens": data.get("total_tokens"),
            "workflow_run_id": res["body"].get("workflow_run_id") if isinstance(res["body"], dict) else None,
            "elapsed_seconds": res["elapsed_seconds"],
        }

    with ThreadPoolExecutor(max_workers=3) as ex:
        index = list(ex.map(one, CASES))
    total_tokens = sum((r.get("total_tokens") or 0) for r in index)

    with open(os.path.join(EVIDENCE_DIR, "_run_index.json"), "w", encoding="utf-8") as f:
        json.dump({
            "carrier": "dify_workflow",
            "dify_app_id": APP_ID,
            "total_cases": len(CASES),
            "total_tokens": total_tokens,
            "cases": index,
        }, f, ensure_ascii=False, indent=2)
    print(f"\ndone. total_tokens={total_tokens}", file=sys.stderr)


if __name__ == "__main__":
    main()
