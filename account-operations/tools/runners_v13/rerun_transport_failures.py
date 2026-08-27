#!/usr/bin/env python3
"""只重跑**传输故障**，不重跑模型行为。

为什么要单独立一个工具，而不是随手补跑：
「重跑」这件事本身有被质疑成择优的风险。第 6 轮独立收口 Reviewer 判过一次同类
（「重跑前看过 E01」），结论是不构成择优，理由是**择优所需的梯度不存在**：
输入逐字节相同、判定全同。这个工具把那个理由做成机制，而不是每次靠解释：

  1. 只认传输故障签名（上游 5xx / SSL EOF / 连接超时），**模型产出的坏结果一律不重跑**；
  2. 输入取自失败记录里冻结的那份，逐字节复用，不重新编译；
  3. 失败那次**保留**为 <case>__transport_failure_N.json，不删不改；
  4. 每次重跑写进 _transport_retries.json：错误原文、时刻、输入哈希。

用法：python3 rerun_transport_failures.py <evidence_dir> [--dry]
"""
import hashlib
import json
import os
import sys
import time
import urllib.error
import urllib.request

WORKTREE = "/home/faye/diyu-demo-worktrees/m3-account-content-operator-v1"
SCRATCH = ("/tmp/claude-1000/-home-faye-diyu-demo/"
           "2c670698-40ad-483e-b793-56ac12fb6aea/scratchpad/m3")
SERVICE_URL = "http://localhost/v1/workflows/run"

TRANSPORT_SIGNS = (
    "Server Unavailable", "SSLEOFError", "UNEXPECTED_EOF_WHILE_READING",
    "Max retries exceeded", "Connection reset", "Read timed out",
    "Bad gateway", "502", "503", "504",
)
# 明确**不**属于传输故障、绝不在这里重跑的（它们是产出问题，属于证据）
MODEL_SIGNS = ("Not all output parameters are validated", "Insufficient Balance",
               "content_filter", "invalid_param")


def is_transport_failure(err_text):
    t = str(err_text or "")
    if any(m in t for m in MODEL_SIGNS):
        return False
    return any(s in t for s in TRANSPORT_SIGNS)


def run_workflow(key, inputs, user):
    req = urllib.request.Request(
        SERVICE_URL,
        data=json.dumps({"inputs": inputs, "response_mode": "blocking", "user": user}).encode(),
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        method="POST")
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=1800) as r:
            return {"status": r.status, "body": json.loads(r.read().decode()),
                    "elapsed_seconds": round(time.time() - t0, 2)}
    except urllib.error.HTTPError as e:
        return {"status": e.code, "body": {"error": e.read().decode()},
                "elapsed_seconds": round(time.time() - t0, 2)}


def inputs_sha(inputs):
    return hashlib.sha256(json.dumps(inputs, ensure_ascii=False, sort_keys=True)
                          .encode("utf-8")).hexdigest()


def main():
    evid = sys.argv[1]
    dry = "--dry" in sys.argv
    key = open(os.path.join(SCRATCH, "m3_app_key.txt"), encoding="utf-8").read().strip()
    log_path = os.path.join(evid, "_transport_retries.json")
    log = json.load(open(log_path, encoding="utf-8")) if os.path.exists(log_path) else []

    targets = []
    for name in sorted(os.listdir(evid)):
        if not name.endswith(".json") or name.startswith("_") or "__transport_failure" in name:
            continue
        rec = json.load(open(os.path.join(evid, name), encoding="utf-8"))
        data = (rec.get("raw_response_body") or {}).get("data") or {}
        if data.get("status") != "failed":
            continue
        if not is_transport_failure(data.get("error")):
            print(f"SKIP {name}: 不是传输故障签名，属于证据，不重跑 —— {str(data.get('error'))[:90]}")
            continue
        targets.append((name, rec, data.get("error")))

    print(f"{evid}: {len(targets)} 例传输故障待重跑")
    for name, rec, err in targets:
        print(f"  {name}: {str(err)[:100]}")
    if dry or not targets:
        return 0

    for name, rec, err in targets:
        base = name[:-5]
        n = 1
        while os.path.exists(os.path.join(evid, f"{base}__transport_failure_{n}.json")):
            n += 1
        # 失败那次原样保留，不删不改
        with open(os.path.join(evid, f"{base}__transport_failure_{n}.json"), "w",
                  encoding="utf-8") as f:
            json.dump(rec, f, ensure_ascii=False, indent=2)

        inputs = rec["workflow_inputs"]                  # 冻结输入逐字节复用，不重新编译
        sha_before = inputs_sha(inputs)
        res = run_workflow(key, inputs, f"m3-retry-{base}-{n}")
        assert inputs_sha(inputs) == sha_before, "输入在重跑过程中变了 —— 拒绝写入"

        rec["raw_response_body"] = res["body"]
        rec["http_status"] = res["status"]
        rec["elapsed_seconds"] = res["elapsed_seconds"]
        rec["transport_retry"] = {
            "attempt": n + 1,
            "previous_attempts_preserved_as": [f"{base}__transport_failure_{i}.json"
                                               for i in range(1, n + 1)],
            "previous_error": str(err)[:500],
            "inputs_sha256": sha_before,
            "why_not_cherry_picking": ("输入逐字节复用同一份冻结输入；只在**传输**失败时重跑，"
                                       "模型产出的坏结果一律不重跑；失败那次全部保留可回指。"),
        }
        with open(os.path.join(evid, name), "w", encoding="utf-8") as f:
            json.dump(rec, f, ensure_ascii=False, indent=2)
        st = ((res["body"].get("data") or {}) if isinstance(res["body"], dict) else {}).get("status")
        print(f"  RETRY {base} attempt#{n+1} -> {st}")
        log.append({"case": base, "attempt": n + 1, "previous_error": str(err)[:300],
                    "new_status": st, "inputs_sha256": sha_before})

    with open(log_path, "w", encoding="utf-8") as f:
        json.dump(log, f, ensure_ascii=False, indent=2)
    print("written:", log_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
