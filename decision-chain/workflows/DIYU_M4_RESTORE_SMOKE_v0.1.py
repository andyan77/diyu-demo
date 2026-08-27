#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""M4 最终成果复原 · 最小运行确认（Founder 复原指令 §7）

这不是重新验收，只确认复原成功：八个应用可打开、有 published workflow、
六能力各完成一次真实 Runtime 调用、Seam 完成一次能力调用、Canvas 完成一次端到端调用，
结果非空、不含 <think>、Seam 实际调用的是新绑定的能力应用、模型 provider 真实可用。
不使用故障注入、模拟输出或离线结果。
凭据只在内存中使用，不打印、不提交、不写入证据文件。
"""
import hashlib, importlib.util, json, os, subprocess, sys, time

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
DC_WF = os.path.join(ROOT, "decision-chain", "workflows")
OUT = os.path.join(ROOT, "decision-chain/evidence/m4/restore")


def _load(n, p):
    s = importlib.util.spec_from_file_location(n, p); m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m); return m


PUB = _load("m4pub", os.path.join(DC_WF, "DIYU_M4_PUBLISH_AND_REBIND_v0.1.py"))
FA = _load("m4fa", os.path.join(DC_WF, "DIYU_M4_FORMAL_ATTEMPT_v0.1.py"))
FX = _load("m4fx", os.path.join(DC_WF, "DIYU_M4_DETERMINISTIC_PROBE_v0.1.py"))

APPS = {
    "MATRIX":               ("d7c2cc11-9a59-47eb-93d7-a25ebc0b8cc3", FX.MATRIX_INSUFFICIENT),
    "CAMPAIGN":             ("cfd48281-d2e6-4f77-b4a6-32f0fca98f2b", FX.CT_CAMPAIGN),
    "CONTENT_BRIEF":        ("a3264c95-9b30-4ac8-833a-dc96ea8b7ee1", FX.CT_M3),
    "CREATIVE_SCRIPT":      ("8d518554-bfbc-4be0-8a57-3b1f04983edf", FX.ACCEPTED_DIRECTION),
    "PRODUCTION_DIRECTOR":  ("57ebc138-ed9e-4202-bce2-38e44da0ec1d", FX.SCRIPT_LEGAL),
    "PUBLISHING_PACKAGING": ("10056fcf-9237-4889-a3e3-81e3a695cae0", FX.FOOTAGE_FINAL),
}
SEAM = "de0cb1e9-2af8-415a-9762-31b6cf348c22"
CANVAS = "f0b1c5f5-afc5-43e9-9ea4-ae36e25f33c8"
BASE = "http://127.0.0.1"
THINK = ["<think>", "</think>", "dify-deepseek-reasoning"]


def psql(sql):
    p = subprocess.run(["docker", "exec", "-i", "docker-db_postgres-1", "psql", "-U", "postgres", "-d", "dify",
                        "-t", "-A", "-c", "SELECT coalesce(json_agg(t)::text,'[]') FROM (%s) t;" % sql.rstrip(";")],
                       capture_output=True, text=True)
    if p.returncode: raise RuntimeError(p.stderr[:400])
    return json.loads(p.stdout.strip() or "[]")


def now():
    p = subprocess.run(["docker", "exec", "-i", "docker-db_postgres-1", "psql", "-U", "postgres", "-d", "dify",
                        "-t", "-A", "-c", "SELECT to_char(now(),'YYYY-MM-DD HH24:MI:SS');"],
                       capture_output=True, text=True)
    return p.stdout.strip()


def main():
    c = PUB.Console(); c.login()
    R = {"purpose": "复原后最小运行确认（非重新验收）", "capabilities": [], "seam": None, "canvas": None}
    empty = 0; leak = 0

    # ── 六个能力应用各一次真实 Runtime 调用 ────────────────────────────────
    for cap, (aid, payload) in APPS.items():
        tok = FA.ensure_api_key(c, aid)
        t0 = now(); time.sleep(1)
        body = {"inputs": {"capability_call": payload, "professional_input": payload,
                           "entry": "", "run_mode": "", "example_reference_requested": "NO"},
                "response_mode": "blocking", "user": "m4-restore-%s" % cap.lower()}
        try:
            r = FA.service_call(BASE, tok, "/v1/workflows/run", body, timeout=900); err = None
        except Exception as e:
            r, err = {}, str(e)[:300]
        d = (r.get("data") or {}); o = d.get("outputs") or {}
        ud = (o.get("user_delivery") or "").strip()
        lk = [w for w in THINK if w in ud]
        ex = psql("SELECT node_id,status FROM workflow_node_executions WHERE app_id='%s' AND created_at >= '%s'"
                  % (aid, t0))
        llm = [x for x in ex if x["node_id"] in ("skill_llm", "recovery_llm")]
        row = {"capability": cap, "app_id": aid, "smoke_run_id": d.get("workflow_run_id") or d.get("id"),
               "platform_status": d.get("status"), "service_error": err,
               "user_delivery_length": len(ud), "user_delivery_excerpt": ud[:150],
               "delivery_outcome": o.get("delivery_outcome"),
               "think_leak": lk,
               "model_actually_invoked": any(x["node_id"] == "skill_llm" and x["status"] == "succeeded" for x in ex),
               "llm_nodes": [(x["node_id"], x["status"]) for x in llm]}
        row["ok"] = bool(ud) and not lk and row["model_actually_invoked"]
        if not ud: empty += 1
        leak += len(lk)
        R["capabilities"].append(row)
        print("  %-22s ud=%-5d outcome=%-24s llm=%s think=%s -> %s"
              % (cap, len(ud), o.get("delivery_outcome"), row["llm_nodes"], lk,
                 "OK" if row["ok"] else "FAIL"), flush=True)

    # ── Capability Seam 一次能力调用 ──────────────────────────────────────
    tok = FA.ensure_api_key(c, SEAM); t0 = now(); time.sleep(1)
    body = {"inputs": {"capability": "CONTENT_BRIEF", "entry": "", "capability_call": FX.CT_M3,
                       "professional_input": FX.CT_M3, "example_reference_requested": "NO"},
            "response_mode": "blocking", "user": "m4-restore-seam"}
    try:
        r = FA.service_call(BASE, tok, "/v1/workflows/run", body, timeout=900); err = None
    except Exception as e:
        r, err = {}, str(e)[:300]
    d = (r.get("data") or {}); o = d.get("outputs") or {}
    ud = (o.get("user_delivery") or "").strip(); lk = [w for w in THINK if w in ud]
    sx = psql("SELECT node_id,status FROM workflow_node_executions WHERE app_id='%s' AND created_at >= '%s'" % (SEAM, t0))
    cb = psql("SELECT id,status FROM workflow_runs WHERE app_id='%s' AND created_at >= '%s'"
              % (APPS["CONTENT_BRIEF"][0], t0))
    R["seam"] = {"app_id": SEAM, "smoke_run_id": d.get("workflow_run_id") or d.get("id"),
                 "platform_status": d.get("status"), "service_error": err,
                 "user_delivery_length": len(ud), "user_delivery_excerpt": ud[:150],
                 "business_delivery_outcome": o.get("business_delivery_outcome"),
                 "think_leak": lk,
                 "tool_nodes_executed": sorted({x["node_id"] for x in sx if x["node_id"].startswith("tool_")}),
                 "child_app_actually_invoked": [x["id"] for x in cb],
                 "ok": bool(ud) and not lk and bool(cb)}
    if not ud: empty += 1
    leak += len(lk)
    print("  %-22s ud=%-5d 调到子应用=%d tool=%s -> %s"
          % ("CAPABILITY_SEAM", len(ud), len(cb), R["seam"]["tool_nodes_executed"],
             "OK" if R["seam"]["ok"] else "FAIL"), flush=True)

    # ── Founder Canvas 一次自然语言端到端 ─────────────────────────────────
    tok = FA.ensure_api_key(c, CANVAS); t0 = now(); time.sleep(1)
    q = "帮我把序里集这条初秋通勤外套的内容任务判断做出来。\n" + FX.CT_M3
    try:
        r = FA.service_call(BASE, tok, "/v1/chat-messages",
                            {"inputs": {}, "query": q, "response_mode": "blocking",
                             "user": "m4-restore-canvas"}, timeout=900); err = None
    except Exception as e:
        r, err = {}, str(e)[:300]
    ans = (r.get("answer") or "").strip(); lk = [w for w in THINK if w in ans]
    seam_runs = psql("SELECT id,status FROM workflow_runs WHERE app_id='%s' AND created_at >= '%s'" % (SEAM, t0))
    R["canvas"] = {"app_id": CANVAS, "smoke_run_id": r.get("message_id") or r.get("id"),
                   "conversation_id": r.get("conversation_id"), "service_error": err,
                   "smoke_test_input": q.split("\n")[0],
                   "answer_length": len(ans), "answer": ans,
                   "think_leak": lk, "seam_invoked": [x["id"] for x in seam_runs],
                   "ok": bool(ans) and not lk}
    if not ans: empty += 1
    leak += len(lk)
    print("  %-22s ans=%-5d 调到 Seam=%d think=%s -> %s"
          % ("FOUNDER_CANVAS", len(ans), len(seam_runs), lk, "OK" if R["canvas"]["ok"] else "FAIL"), flush=True)

    R["empty_user_delivery_count"] = empty
    R["think_leak_count"] = leak
    R["all_ok"] = (empty == 0 and leak == 0
                   and all(x["ok"] for x in R["capabilities"])
                   and R["seam"]["ok"] and R["canvas"]["ok"])
    os.makedirs(OUT, exist_ok=True)
    json.dump(R, open(os.path.join(OUT, "M4_RESTORE_SMOKE.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=2, sort_keys=True)
    print("\n最小运行确认 = %s（空正文 %d，think 泄漏 %d）"
          % ("PASS" if R["all_ok"] else "FAIL", empty, leak), flush=True)


if __name__ == "__main__":
    main()
