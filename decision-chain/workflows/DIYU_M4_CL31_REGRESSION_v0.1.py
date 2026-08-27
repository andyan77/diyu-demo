#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""M4-CL31-05⑧⑨ / CL31-07⑥⑦⑩ / NEG-C14 受影响范围回归

A3 影响面：本轮改动了六个能力子应用的 delivery_finalize 与接缝的收口/失败终止路径。
  受影响 ⇒ 六项能力的**用户交付**证据、接缝失败路径、Canvas 用户可见结果 → 定向复验；
  不受影响 ⇒ 专业生成链（skill_llm 及其上游）本身，已由 CL31-05①②③④ 静态证明零变化，
             不因本轮变化整体失效（A3 不得多算）。

夹具全部复用已冻结夹具，不新造。
"""
import hashlib, importlib.util, json, os, sys, time

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
DC_WF = os.path.join(ROOT, "decision-chain", "workflows")
OUT = os.path.join(ROOT, "decision-chain/evidence/m4/final_closure/CL31_07_REGRESSION.json")


def _load(n, p):
    s = importlib.util.spec_from_file_location(n, p); m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m); return m


PUB = _load("m4pub", os.path.join(DC_WF, "DIYU_M4_PUBLISH_AND_REBIND_v0.1.py"))
FA = _load("m4fa", os.path.join(DC_WF, "DIYU_M4_FORMAL_ATTEMPT_v0.1.py"))
FX = _load("m4fx", os.path.join(DC_WF, "DIYU_M4_DETERMINISTIC_PROBE_v0.1.py"))
COL = _load("m4col", os.path.join(DC_WF, "DIYU_M4_CL31_RUNTIME_COLLECT_v0.1.py"))

SEAM_APP = "de0cb1e9-2af8-415a-9762-31b6cf348c22"
CANVAS_APP = "f0b1c5f5-afc5-43e9-9ea4-ae36e25f33c8"

# 冻结夹具复用（与 FORMAL_ATTEMPT 的 attempt_matrix 同源）
CASES = [
    ("RG-01", "CONTENT_BRIEF", "FX-M4-CT-M3", FX.CT_M3, "DELIVERED"),
    ("RG-02", "MATRIX", "FX-M4-MATRIX-INSUFFICIENT-WITH-UNRELATED", FX.MATRIX_INSUFFICIENT, "ANY"),
    ("RG-03", "CAMPAIGN", "FX-M4-CT-CAMPAIGN", FX.CT_CAMPAIGN, "ANY"),
    ("RG-04", "CREATIVE_SCRIPT", "FX-M4-ACCEPTED-DIRECTION", FX.ACCEPTED_DIRECTION, "ANY"),
    ("RG-05", "PRODUCTION_DIRECTOR", "FX-M4-SCRIPT-LEGAL", FX.SCRIPT_LEGAL, "ANY"),
    ("RG-06", "PUBLISHING_PACKAGING", "FX-M4-REALIZATION-FINAL", FX.FOOTAGE_FINAL, "ANY"),
    ("RG-07", "CONTENT_BRIEF", "FX-M4-THIN-FIELDS（资料不足 Return）", FX.THIN_FIELDS, "ANY"),
    ("RG-08", "NOT_A_CAPABILITY", "不支持的能力", FX.CT_M3, "NOT_DELIVERED"),
]

LEAKS = ["<think>", "</think>", "dify-deepseek-reasoning", "PARSE_FAIL", "NOT_APPLICABLE",
         "STALE", "NOT_VERIFIED", "returns_json", "artifact_status", "user_delivery_status",
         "capability_call", "goal_family", "skill_llm", "recovery_llm", "returns_adapter",
         "delivery_finalize", "final_extract", "binding_record", "system prompt",
         "M4_ARTIFACT", "M4_USER_DELIVERY", "M4_RETURNS"]


def sha(s): return hashlib.sha256((s or "").encode("utf-8")).hexdigest()


def main():
    c = PUB.Console(); c.login()
    tok = FA.ensure_api_key(c, SEAM_APP)
    tok_canvas = FA.ensure_api_key(c, CANVAS_APP)
    base = "http://127.0.0.1"
    res, fails = [], []

    for cid, cap, fxid, payload, want in CASES:
        t0 = COL.psql("SELECT to_char(now(),'YYYY-MM-DD HH24:MI:SS');")[0]; time.sleep(1)
        body = {"inputs": {"capability": cap, "entry": "", "capability_call": payload,
                           "professional_input": payload, "example_reference_requested": "NO"},
                "response_mode": "blocking", "user": "m4-cl31-reg-%s" % cid.lower()}
        try:
            r = FA.service_call(base, tok, "/v1/workflows/run", body, timeout=900)
            err = None
        except Exception as e:
            r, err = {}, str(e)[:400]
        d = (r.get("data") or {})
        o = d.get("outputs") or {}
        ud = (o.get("user_delivery") or "").strip()
        lk = [w for w in LEAKS if w in ud]
        ex = COL.qjson("SELECT node_id,status,created_at::text AS created_at "
                       "FROM workflow_node_executions WHERE app_id='%s' AND created_at >= '%s' "
                       "ORDER BY index" % (SEAM_APP, t0))
        tools = sorted({x["node_id"] for x in ex if x["node_id"].startswith("tool_")})
        row = {"case": cid, "capability": cap, "fixture": fxid, "input_sha256": sha(payload),
               "run_id": d.get("workflow_run_id") or d.get("id"), "platform_status": d.get("status"),
               "service_error": err, "user_delivery_length": len(ud),
               "user_delivery_excerpt": ud[:160],
               "business_delivery_outcome": o.get("business_delivery_outcome"),
               "artifact_length": len(o.get("artifact") or ""),
               "leaks": lk, "capability_tool_nodes_executed": tools,
               "expected_outcome": want}
        ok = bool(ud) and not lk and len(tools) <= 1
        if want != "ANY" and o.get("business_delivery_outcome") != want:
            ok = False
        row["result"] = "PASS" if ok else "FAIL"
        if not ok:
            fails.append(cid)
        res.append(row)
        print("  %-6s %-22s ud=%-5d outcome=%-16s tools=%s leaks=%s -> %s"
              % (cid, cap, len(ud), o.get("business_delivery_outcome"), tools, lk, row["result"]),
              flush=True)

    # ── NEG-C14 / CL31-07⑩ Founder Canvas 用户可见结果 ──────────────────
    canvas = []
    for cid, msg in (("CV-01", "帮我把序里集这条初秋通勤外套的内容任务判断做出来。"
                              + FX.CT_M3),
                     ("CV-02", "帮我算一下这个月的工资条和五险一金。")):
        try:
            r = FA.service_call(base, tok_canvas, "/v1/chat-messages",
                                {"inputs": {}, "query": msg, "response_mode": "blocking",
                                 "user": "m4-cl31-%s" % cid.lower()}, timeout=900)
            err = None
        except Exception as e:
            r, err = {}, str(e)[:400]
        ans = (r.get("answer") or "").strip()
        lk = [w for w in LEAKS if w in ans]
        ok = bool(ans) and not lk
        canvas.append({"case": cid, "query_head": msg[:40], "answer_length": len(ans),
                       "answer_excerpt": ans[:220], "leaks": lk, "service_error": err,
                       "result": "PASS" if ok else "FAIL"})
        if not ok:
            fails.append(cid)
        print("  %-6s Canvas ans=%-5d leaks=%s -> %s" % (cid, len(ans), lk,
              "PASS" if ok else "FAIL"), flush=True)

    rec = {"criteria": ["M4-CL31-05⑧⑨", "M4-CL31-07⑥⑦⑩", "NEG-C14"],
           "affected_scope_rule": ("只复验受本轮变化影响的项：六项能力的用户交付、接缝失败终止路径、"
                                   "Canvas 用户可见结果。专业生成链已由 CL31-05①②③④ 静态证明零变化，"
                                   "不整体失效（A3 不得多算）。"),
           "seam_runs": res, "canvas_runs": canvas,
           "capabilities_covered": sorted({r["capability"] for r in res if r["capability"] != "NOT_A_CAPABILITY"}),
           "max_capability_tools_per_run": max((len(r["capability_tool_nodes_executed"]) for r in res), default=0),
           "failed": fails,
           "verdict": "PASS" if not fails else "FAIL"}
    json.dump(rec, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=2, sort_keys=True)
    print("\n回归 = %s（失败：%s）" % (rec["verdict"], fails or "无"), flush=True)


if __name__ == "__main__":
    main()
