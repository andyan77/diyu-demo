#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Step 1 归因的节点绑定证据。只读 Dify，不改任何应用。

产出一份可复算的 JSON：谁写了带泄漏的 user_delivery、泄漏检查表缺什么、
以及 returns_adapter 是不是六个能力共享的同一份。
"""
import hashlib, json, os, re, subprocess, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
OUT = os.path.join(ROOT, "decision-chain", "evidence", "m5", "FINAL_P0_TRIAGE_NODE_BINDING.json")

RB_CAPS = [
    ("MATRIX",               "47e52165-f6cb-48ff-93be-6c6a8ea5cecf"),
    ("CAMPAIGN",             "7d10e28d-30e6-4c4a-950b-88dcbb5fd0fc"),
    ("CONTENT_BRIEF",        "cbbeab61-a4de-4a21-a6be-7dc2385dd6f3"),
    ("CREATIVE_SCRIPT",      "4fbcfea8-48a3-41b3-b2b5-cdb50276eeb2"),
    ("PRODUCTION_DIRECTOR",  "07e99f7b-71a3-40af-85f3-fc43b68e774a"),
    ("PUBLISHING_PACKAGING", "0fb7636a-55e8-49a9-92f7-3d11ad0a35fa"),
]
SEAM_RB = "9e1b1fd8-f696-436d-9d42-54700a29a4dd"
M3_RB = "ca4c28aa-e0fd-4c54-bde3-a0918dc4c884"

# M5-05 定向复验那一跳的三个运行
HOP_RUN = "2d7d1a2b-bf72-45ca-b953-f8fc4f9129cf"
SEAM_RUN = "3b8a88f2-84f6-49f3-bc9d-e3732a4136b8"
BRIEF_RUN = "a742d63a-6990-476b-9fff-9add3564f52f"

# 变形与泄漏的三个判别串
MARKERS = ["status: READY", "整轮重跑", "从头跑完"]
# 统一状态词（宪法 §4）。泄漏表应当覆盖它们。
STATE_WORDS = ["PASS", "FAIL", "NOT_VERIFIED", "CURRENT", "STALE", "APPLICABLE",
               "NOT_APPLICABLE", "NOT_STARTED", "IN_PROGRESS", "COMPLETED",
               "INVALID", "DONE", "PARTIAL", "BLOCKED", "FAILED", "READY"]


def psql(q):
    p = subprocess.run(["docker", "exec", "-i", "docker-db_postgres-1", "psql", "-U", "postgres",
                        "-d", "dify", "-t", "-A", "-c", q],
                       capture_output=True, text=True, timeout=300)
    if p.returncode != 0:
        raise RuntimeError(p.stderr[:300])
    return p.stdout.strip()


def node_code(app_id, node_id):
    """一次只取一个节点的 code，不把六张 graph 同时留在内存里（上一次那样跑被 OOM kill）。"""
    # graph 是 text 列，必须显式转 jsonb，否则 -> 操作符不匹配。
    q = ("select n->'data'->>'code' from workflows w join apps a on a.workflow_id=w.id, "
         "jsonb_array_elements(w.graph::jsonb->'nodes') n "
         "where a.id='%s' and n->>'id'='%s';" % (app_id, node_id))
    return psql(q)


def sha(s):
    return hashlib.sha256((s or "").encode("utf-8")).hexdigest()


def run_outputs(run_id):
    return json.loads(psql("select outputs from workflow_runs where id='%s';" % run_id))


def run_app(run_id):
    return psql("select app_id from workflow_runs where id='%s';" % run_id)


def main():
    ev = {"binding": {"m3_rb": M3_RB, "seam_rb": SEAM_RB,
                      "capability_apps_rb": dict(RB_CAPS)},
          "read_only": True, "apps_modified": []}

    # ---------------- 1. 谁写了带泄漏的 user_delivery
    brief_out = run_outputs(BRIEF_RUN)
    seam_app = run_app(SEAM_RUN)
    brief_app = run_app(BRIEF_RUN)
    ud = brief_out.get("user_delivery") or ""
    ev["m5_05_delivery_authorship"] = {
        "hop_run": HOP_RUN,
        "seam_run": SEAM_RUN, "seam_run_app": seam_app,
        "capability_run": BRIEF_RUN, "capability_run_app": brief_app,
        "capability_app_is_content_brief": brief_app == dict(RB_CAPS)["CONTENT_BRIEF"],
        "user_delivery_head": ud[:60],
        "markers_in_capability_user_delivery": {m: (m in ud) for m in MARKERS},
        "capability_self_reported": {k: brief_out.get(k) for k in
                                     ("user_delivery_leaks", "user_delivery_status",
                                      "artifact_status", "delivery_outcome",
                                      "recovery_used", "sufficiency_status")},
    }

    # ---------------- 2. 上游是否已经带着这些串（若否，则变形发生在能力应用）
    hop_out = run_outputs(HOP_RUN)
    up = "\n".join(str(v) for v in hop_out.values())
    ev["m5_05_upstream_check"] = {
        "hop_outputs_keys": sorted(hop_out.keys()),
        "markers_in_hop_outputs": {m: (m in up) for m in MARKERS},
        "m3_refusal_sentence_present_in_professional_input":
            "为什么不是" in (hop_out.get("professional_input") or ""),
        "note": "professional_input 逐字含 M3 判断全文；接缝与能力侧收到的上游是同一份。",
    }

    # ---------------- 3. returns_adapter 是不是六能力共享同一份
    per, leaks_src = {}, None
    for cap, aid in RB_CAPS:
        code = node_code(aid, "returns_adapter")
        norm = re.sub(r'CAPABILITY = ".*?"', 'CAPABILITY = "<CAP>"', code or "")
        m = re.search(r"LEAK_PATTERNS = \[(.*?)\]", code or "", re.S)
        leaks = m.group(1) if m else ""
        if leaks_src is None:
            leaks_src = leaks
        fin = node_code(aid, "delivery_finalize")
        per[cap] = {"app_id": aid,
                    "returns_adapter_sha256_normalized": sha(norm),
                    "leak_patterns_sha256": sha(leaks),
                    "delivery_finalize_sha256": sha(fin or "")}
    ras = {v["returns_adapter_sha256_normalized"] for v in per.values()}
    lps = {v["leak_patterns_sha256"] for v in per.values()}
    dfs = {v["delivery_finalize_sha256"] for v in per.values()}
    covered = [w for w in STATE_WORDS if '"%s"' % w in (leaks_src or "")]
    ev["shared_returns_adapter"] = {
        "per_capability": per,
        "returns_adapter_identical_across_six": len(ras) == 1,
        "leak_patterns_identical_across_six": len(lps) == 1,
        "delivery_finalize_identical_across_six": len(dfs) == 1,
        "state_words_checked": STATE_WORDS,
        "state_words_covered_by_leak_patterns": covered,
        "state_words_missing_from_leak_patterns": [w for w in STATE_WORDS if w not in covered],
    }

    # ---------------- 4. delivery_finalize 的泄漏检查只在恢复分支
    fin = node_code(dict(RB_CAPS)["CONTENT_BRIEF"], "delivery_finalize")
    normal_branch = re.search(r"if not need and ud:(.*?)return", fin or "", re.S)
    ev["leak_check_branch_coverage"] = {
        "returns_adapter_computes_leaks_on_all_paths": "leaks = [p for p in LEAK_PATTERNS" in (
            node_code(dict(RB_CAPS)["CONTENT_BRIEF"], "returns_adapter") or ""),
        "delivery_finalize_leak_check_only_in_recovery_branch":
            bool(fin) and "leaked = [w for w in LEAK" in fin
            and (normal_branch is not None and "leaked" not in normal_branch.group(1)),
        "m5_05_path_taken": "normal (recovery_used=false)",
    }

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(ev, f, ensure_ascii=False, indent=1, sort_keys=True)
    print(json.dumps(ev, ensure_ascii=False, indent=1, sort_keys=True)[:2600])
    print("\nSAVED", OUT)
    return 0


sys.exit(main())
