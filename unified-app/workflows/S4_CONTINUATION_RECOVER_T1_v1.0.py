#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从 Dify 真源取回 T1 的证据｜零模型调用。

T1 已经真实跑完并返回 200，但运行器在写盘之前崩在一句错的 SQL 上（表上没有 name 列），
证据没落盘。被测系统没有失效证据，因此不重跑 T1——直接从
messages / workflow_runs / workflow_node_executions 取回原始执行记录。

本脚本只读，不发起任何调用，不写 Dify，也不改判据。
"""
import hashlib
import importlib.util
import io
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
EV = os.path.join(HERE, "..", "evidence", "stages", "s4_continuation01")
GATE = os.path.join(HERE, "..", "stages", "S4_CONTENT_ORIGIN_CONTINUATION_GATE_v1.0.json")
INPUTS = os.path.join(HERE, "..", "stages", "S4_CONTENT_ORIGIN_CONTINUATION_INPUTS_v1.0.json")

spec = importlib.util.spec_from_file_location("s42run", os.path.join(HERE, "S4_2_RUN_v1.0.py"))
R = importlib.util.module_from_spec(spec)
spec.loader.exec_module(R)

RUNNER = importlib.util.spec_from_file_location(
    "s4corun", os.path.join(HERE, "S4_CONTINUATION_RUN_v1.0.py"))
CR = importlib.util.module_from_spec(RUNNER)
RUNNER.loader.exec_module(CR)

APP = "85c01f85-a081-43e9-ab09-9993289cc200"
USER = "s4co-20260829131527"
MESSAGE_ID = "201fd58c-13da-4de7-8691-c82cfc2bef12"
CONV = "b0d6d9f0-fed4-48da-a630-11db235aa573"
WINDOW_START = "2026-08-29 20:15:27"
FILE_ID = "8b541898-015c-4f8e-966f-6fed15a7b43e"
ELAPSED = 308.15   # 运行器日志原文：http=200 308.15s ans_len=96


def sha(p):
    return hashlib.sha256(io.open(p, "rb").read()).hexdigest()


def main():
    out = os.path.join(EV, "S4-CO-T1.json")
    if os.path.exists(out):
        raise SystemExit("拒绝覆盖已有证据：" + out)
    gate = json.load(io.open(GATE, encoding="utf-8"))
    plan = json.load(io.open(INPUTS, encoding="utf-8"))
    t = plan["conversation"]["turns"][0]

    ans = R.psql("select coalesce(m.answer,'') from messages m where m.id='%s';" % MESSAGE_ID)
    rid, nodes = R.trace(MESSAGE_ID)
    nested = {}
    for k, aid in R.APPS.items():
        rs = R.runs_since(aid, WINDOW_START)
        item = {"app_id": aid, "runs_during_case": rs}
        if k == "SEAM" and rs:
            item["latest_run_nodes"] = R.nodes_of(rs[0]["id"])
        nested[k] = item

    doc = {"case_id": "S4-CO-T1", "stage": "S4_CONTENT_ORIGIN_CONTINUATION",
           "turn_index": 1, "expect_capability": t["expect_capability"],
           "with_fixture": True, "attempt": "s4_continuation01",
           "gate_sha256": sha(GATE), "inputs_sha256": sha(INPUTS),
           "graph_sha256_at_run": gate["identity"]["graph_sha256"],
           "app_id": APP, "end_user": USER, "query": t["text"],
           "uploaded_fixture": {"http_status": 201, "file_id": FILE_ID,
                                "name": "一页纸夹具品牌事实 v0.1.md",
                                "sha256": gate["sufficiency_source"]["sha256"],
                                "stored_size": 6119},
           "window_start": WINDOW_START, "http_status": 200,
           "elapsed_seconds": ELAPSED, "attempts": 1,
           "message_id": MESSAGE_ID, "workflow_run_id": rid, "conversation_id": CONV,
           "answer": ans,
           "nodes_executed": [{"idx": n.get("idx"), "node_id": n.get("node_id"),
                               "type": n.get("type"), "status": n.get("status"),
                               "error": n.get("error")} for n in nodes],
           "node_detail": nodes, "nested_app_runs": nested,
           "conversation_variables_after_turn": CR.conv_vars(CONV),
           "reconstructed_from_db": True,
           "reconstruction_reason": ("T1 已真实执行并返回 200，但运行器在写盘前崩于 conv_vars() 的错误 SQL"
                                     "（workflow_conversation_variables 无 name 列）。被测系统无失效证据，"
                                     "因此不重跑，改为从 Dify 真源取回执行记录。零模型调用。"),
           "note": "运行器只发起与记录，不判定。本文件为崩溃后的只读取回，字段与在线记录同源。"}
    with io.open(out, "w", encoding="utf-8") as fh:
        fh.write(json.dumps(doc, ensure_ascii=False, indent=2) + "\n")
    seam = [n["node_id"] for n in (nested.get("SEAM") or {}).get("latest_run_nodes") or []
            if n["node_id"].startswith("tool_")]
    print("RECOVERED S4-CO-T1 | run=%s | ans_len=%d | seam=%s" % (rid, len(ans), seam))
    print("conv_vars:", json.dumps(doc["conversation_variables_after_turn"],
                                   ensure_ascii=False)[:300])


if __name__ == "__main__":
    main()
