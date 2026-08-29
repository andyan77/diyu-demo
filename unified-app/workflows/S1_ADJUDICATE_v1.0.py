#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Node S1｜按**已冻结**判据独立判定。与运行器分离：运行器不判，判定器不跑。

判定只认 workflow_node_executions 的节点执行记录与回复正文，
不认模型自述、不认平台 succeeded、不认对话正文里的任何承诺。
"""
import hashlib
import io
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
GATE = os.path.join(HERE, "..", "stages", "S1_STAGE_GATE_v1.0.json")
EV = os.path.join(HERE, "..", "evidence", "stages")

# 与画布内守卫同源的空头支票模式。判定侧独立再算一遍，不复用被测节点的输出结论。
PROMISE = [r"(已经|已)\s*(转交|交给|派给|转给|移交)",
           r"(正在|已在|马上|稍后|随后)\s*(推进|处理|调用|执行|分析|生成|安排)",
           r"等(结果|它)?\s*(出来|返回|回来|好了)",
           r"(将|会|即将|准备)\s*(为你|帮你)?\s*(调用|启动|接入|进入)\s*(?:相应|对应|专业|的)*\s*(能力|模块|专家)",
           r"(要不要|需不需要|你希望|需要不需要)\s*(我)?\s*(帮你)?\s*(现在)?\s*(就)?"
           r"\s*(调用|启动|进入|请|找|叫)\s*(?:相应|对应|专业|的)*\s*(能力|模块|专家)",
           r"(可以|能)\s*(帮你)?\s*(看看)?\s*要不要\s*(请|调用|找)"]
PRX = [re.compile(p) for p in PROMISE]


def J(x):
    if isinstance(x, str):
        try:
            return json.loads(x)
        except Exception:
            return {}
    return x if isinstance(x, dict) else {}


def node_out(turn, nid):
    for n in turn.get("node_detail") or []:
        if n.get("node_id") == nid:
            return J(n.get("outputs")), n.get("status")
    return None, None


def ran(turn, nid):
    return any(n.get("node_id") == nid for n in turn.get("nodes_executed") or [])


def leaks(text, tokens):
    t = text or ""
    return [tok for tok in tokens if tok in t]


def qcount(text):
    return (text or "").count("?") + (text or "").count("？")


def main():
    g = json.load(io.open(GATE, encoding="utf-8"))
    gsha = hashlib.sha256(io.open(GATE, "rb").read()).hexdigest()
    LEAK = g["leak_forbidden_tokens"]
    out = {"stage": "S1", "stage_gate_sha256": gsha, "cases": {}, "model_calls_by_adjudicator": 0}

    # ---------------- S1-POS-01 / S1-FOLLOW-01 ----------------
    p = os.path.join(EV, "S1-POS-01.json")
    d = json.load(io.open(p, encoding="utf-8"))
    assert d["stage_gate_sha256"] == gsha, "证据绑定的判据版本与当前判据不一致，拒绝判定"
    t1, t2 = d["turns"][0], d["turns"][1]

    r1, _ = node_out(t1, "uapp_route")
    exp = g["cases"]["S1-POS-01"]["expect"]
    a1 = t1.get("answer") or ""
    pend1, _ = node_out(t1, "uapp_s1_pending")
    ch = []
    ch.append(("route_mode 落在 CAPABILITY/OPERATION_ONLY",
               (r1 or {}).get("route_mode") in exp["route_mode_in"], (r1 or {}).get("route_mode")))
    tgt = (r1 or {}).get("target_capability") or ""
    itn = (r1 or {}).get("intent") or ""
    ch.append(("落点是 MATRIX 或 SINGLE_ACCOUNT_OPERATION",
               tgt in exp["target_or_intent_in"] or itn in exp["target_or_intent_in"],
               {"target_capability": tgt, "intent": itn}))
    ch.append(("intent_source = canvas_triage（系统自己识别）",
               (r1 or {}).get("intent_source") == exp["intent_source"],
               (r1 or {}).get("intent_source")))
    ch.append(("triage 未失败", (r1 or {}).get("triage_failed") == "false",
               (r1 or {}).get("triage_failed")))
    ch.append(("未走只问一个分支", not ran(t1, "uapp_ask_one"), ran(t1, "uapp_ask_one")))
    ch.append(("如实交代本层尚未接通专业分析",
               ran(t1, "uapp_s1_pending") and (pend1 or {}).get("pending_kind") == "routed_not_wired",
               (pend1 or {}).get("pending_kind")))
    hits1 = [rx.pattern for rx in PRX if rx.search(a1)]
    ch.append(("无异步承诺", not hits1, hits1))
    lk1 = leaks(a1, LEAK)
    ch.append(("零内部字段泄漏", not lk1, lk1))
    out["cases"]["S1-POS-01"] = {
        "input": t1["query"], "workflow_run_id": t1["workflow_run_id"],
        "route": r1, "answer": a1,
        "checks": [{"desc": c[0], "result": "PASS" if c[1] else "FAIL", "observed": c[2]} for c in ch],
        "verdict": "PASS" if all(c[1] for c in ch) else "FAIL"}

    r2, _ = node_out(t2, "uapp_route")
    a2 = t2.get("answer") or ""
    e2 = g["cases"]["S1-FOLLOW-01"]["expect"]
    ch2 = []
    ch2.append(("route_mode 仍落在 CAPABILITY/OPERATION_ONLY",
                (r2 or {}).get("route_mode") in e2["route_mode_in"], (r2 or {}).get("route_mode")))
    ch2.append(("未退回 DIALOGUE", (r2 or {}).get("route_mode") != "DIALOGUE",
                (r2 or {}).get("route_mode")))
    lk2 = leaks(a2, LEAK)
    ch2.append(("零内部字段泄漏", not lk2, lk2))
    out["cases"]["S1-FOLLOW-01"] = {
        "input": t2["query"], "workflow_run_id": t2["workflow_run_id"],
        "route": r2, "answer": a2,
        "checks": [{"desc": c[0], "result": "PASS" if c[1] else "FAIL", "observed": c[2]} for c in ch2],
        "verdict": "PASS" if all(c[1] for c in ch2) else "FAIL"}

    # ---------------- S1-NEG-01 ----------------
    p = os.path.join(EV, "S1-NEG-01.json")
    d = json.load(io.open(p, encoding="utf-8"))
    assert d["stage_gate_sha256"] == gsha, "证据绑定的判据版本与当前判据不一致，拒绝判定"
    n1 = d["turns"][0]
    rn, _ = node_out(n1, "uapp_route")
    ao, _ = node_out(n1, "uapp_ask_one")
    an = n1.get("answer") or ""
    ch3 = []
    ch3.append(("route_mode = ASK_ONE", (rn or {}).get("route_mode") == "ASK_ONE",
                (rn or {}).get("route_mode")))
    ch3.append(("asks_one = true", (rn or {}).get("asks_one") == "true", (rn or {}).get("asks_one")))
    ch3.append(("uapp_ask_one 节点实际执行", ran(n1, "uapp_ask_one"), ran(n1, "uapp_ask_one")))
    ch3.append(("回复正文问号计数为 1", qcount(an) == 1, qcount(an)))
    ch3.append(("未硬猜任何能力", not ((rn or {}).get("target_capability") or ""),
                (rn or {}).get("target_capability")))
    ch3.append(("未走能力/未接线分支", not ran(n1, "uapp_s1_pending"), ran(n1, "uapp_s1_pending")))
    lk3 = leaks(an, LEAK)
    ch3.append(("零内部字段泄漏", not lk3, lk3))
    out["cases"]["S1-NEG-01"] = {
        "input": n1["query"], "workflow_run_id": n1["workflow_run_id"],
        "route": rn, "ask_one": ao, "answer": an,
        "checks": [{"desc": c[0], "result": "PASS" if c[1] else "FAIL", "observed": c[2]} for c in ch3],
        "verdict": "PASS" if all(c[1] for c in ch3) else "FAIL"}

    verdicts = {k: v["verdict"] for k, v in out["cases"].items()}
    out["summary"] = {"verdicts": verdicts,
                      "all_pass": all(v == "PASS" for v in verdicts.values()),
                      "next_stage_allowed": all(v == "PASS" for v in verdicts.values())}
    print(json.dumps(out, ensure_ascii=False, indent=2))
    q = os.path.join(HERE, "..", "evidence", "S1_ADJUDICATION.json")
    with io.open(q, "w", encoding="utf-8") as fh:
        fh.write(json.dumps(out, ensure_ascii=False, indent=2) + "\n")


if __name__ == "__main__":
    main()
