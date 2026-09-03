#!/usr/bin/env python3
"""E4 v2.0 阶段 C 单次真实调用执行器。

对给定 (case_id, tier, k) 组合发起一次真实 Dify workflow 调用，把原始 SSE
落盘到 p0-empirical-r1/raw/<case_id>_<tier>_k<k>.sse，并把结构化摘要（用于
报告，不含完整正文）追加进 p0-empirical-r1/PHASE_C_CALL_LOG.jsonl。

用法：python3 run_phase_c_call.py <case_id> <tier> <k>
  <tier> 只用于命名与日志标注——实际生效的 reasoning_effort 由当前发布在
  Dify 的 DSL 决定，调用方必须自己保证发起调用时发布的 DSL 与 <tier> 相符
  （本轮方法：low 批次跑完才允许把 Dify 里发布的 DSL 换成 high 批次）。
"""
import json
import os
import sys
import time

import requests

REPO_ROOT = "/home/faye/diyu-demo"
API_BASE = "http://localhost/v1"
APP_API_KEY = "app-4LLHCyCpIuKw9xDjMfJJpSH8"
RAW_DIR = os.path.join(REPO_ROOT, "p0-empirical-r1", "raw")
LOG_PATH = os.path.join(REPO_ROOT, "p0-empirical-r1", "PHASE_C_CALL_LOG.jsonl")


def load_case_inputs(case_id):
    with open(os.path.join(REPO_ROOT, "eval", "%s.json" % case_id)) as f:
        case = json.load(f)
    return {
        "capability_call": case["capability_call"],
        "professional_input": case["professional_input"],
        "example_reference_requested": case["example_reference_requested"],
    }


def run_call(case_id, tier, k):
    inputs = load_case_inputs(case_id)
    user_id = "e4-r1-%s-%s-k%s" % (case_id.lower(), tier, k)
    body = {"inputs": inputs, "response_mode": "streaming", "user": user_id}

    raw_path = os.path.join(RAW_DIR, "%s_%s_k%s.sse" % (case_id, tier, k))
    if os.path.exists(raw_path):
        print("SKIP (raw file already exists): %s" % raw_path)
        return

    t0 = time.monotonic()
    started_at = time.time()
    resp = requests.post(
        "%s/workflows/run" % API_BASE,
        headers={"Authorization": "Bearer %s" % APP_API_KEY, "Content-Type": "application/json"},
        json=body,
        stream=True,
        timeout=(30, 1800),
    )
    lines = []
    workflow_finished = None
    node_finished_events = []
    for raw_line in resp.iter_lines(decode_unicode=True):
        if raw_line is None:
            continue
        lines.append(raw_line)
        if raw_line.startswith("data:"):
            payload = raw_line[len("data:"):].strip()
            if not payload:
                continue
            try:
                evt = json.loads(payload)
            except json.JSONDecodeError:
                continue
            if evt.get("event") == "workflow_finished":
                workflow_finished = evt
            elif evt.get("event") == "node_finished":
                node_finished_events.append(evt)
    wall_s = time.monotonic() - t0

    with open(raw_path, "w") as f:
        f.write("\n".join(lines))

    data = (workflow_finished or {}).get("data", {})
    outputs = data.get("outputs") or {}
    usage = (outputs.get("_usage") if isinstance(outputs, dict) else None) or {}
    # Dify's workflow_finished.data.total_tokens is the authoritative usage
    # figure (matches what we captured for the phase-B call); node-level
    # usage in node_finished(skill_llm).process_data.usage is the same figure
    # scoped to just that node — record both when present.
    llm_node_usage = None
    for evt in node_finished_events:
        nd = evt.get("data", {})
        if nd.get("node_id") == "skill_llm" or (nd.get("title") or "").lower().find("llm") >= 0:
            pd = nd.get("process_data") or {}
            if isinstance(pd, dict) and "usage" in pd:
                llm_node_usage = pd.get("usage")

    summary = {
        "case_id": case_id,
        "tier": tier,
        "k": k,
        "user_id": user_id,
        "started_at_unix": started_at,
        "http_status": resp.status_code,
        "workflow_run_id": data.get("workflow_run_id") or data.get("id"),
        "status": data.get("status"),
        "error": data.get("error"),
        "elapsed_time_s": data.get("elapsed_time"),
        "wall_clock_s_observed": round(wall_s, 3),
        "total_tokens": data.get("total_tokens"),
        "llm_node_usage": llm_node_usage,
        "raw_sse_file": os.path.relpath(raw_path, REPO_ROOT),
        "reached_skill_llm": any(
            evt.get("data", {}).get("node_id") == "skill_llm" for evt in node_finished_events
        ),
    }
    with open(LOG_PATH, "a") as f:
        f.write(json.dumps(summary, ensure_ascii=False) + "\n")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    run_call(sys.argv[1], sys.argv[2], int(sys.argv[3]))
