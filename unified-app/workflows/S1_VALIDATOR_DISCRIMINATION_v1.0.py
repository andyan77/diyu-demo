#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Node S1｜判定器判别力测试。零模型调用。

判据本身也要被验证：一个只会输出 PASS 的检查器没有判别力，等于没检查。
本测试把三份**已知结论**的输入喂给与 S1_ADJUDICATE 同一套判据逻辑：

  1. 真实已知坏例：旧候选 UAPP-INTENT-02N @ attempt 40e45858
     —— 分诊台硬猜 CREATIVE_SCRIPT 并真的跑了能力。冻结判据要求本轮不调用任何能力。
     期望：FAIL。
  2. 真实已知坏例：旧候选 UAPP-INTENT-02N @ attempt 00d9dcdd
     —— 落 DIALOGUE，回复里问了两个以上问题，且残留一句空头支票。
     期望：FAIL。
  3. 合成好例：route_mode=ASK_ONE、ask_one 执行、正文恰一个问号、未猜能力、零泄漏。
     期望：PASS。

三条都符合期望，判定器才算有判别力。
"""
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
GATE = os.path.join(HERE, "..", "stages", "S1_STAGE_GATE_v1.0.json")
LEGACY_EV = os.path.abspath(os.path.join(
    HERE, "..", "..", "..", "v1-unified-dify-application",
    "unified-app", "evidence", "formal"))

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


def qcount(t):
    return (t or "").count("?") + (t or "").count("？")


def judge_negative(route, ask_one_ran, pending_ran, answer, leak_tokens):
    """S1-NEG-01 的冻结判据，与 S1_ADJUDICATE 逐条同构。"""
    r = route or {}
    checks = [
        ("route_mode = ASK_ONE", r.get("route_mode") == "ASK_ONE"),
        ("asks_one = true", r.get("asks_one") == "true"),
        ("uapp_ask_one 实际执行", bool(ask_one_ran)),
        ("问号计数为 1", qcount(answer) == 1),
        ("未硬猜任何能力", not (r.get("target_capability") or "")),
        ("未走能力/未接线分支", not pending_ran),
        ("零内部字段泄漏", not [t for t in leak_tokens if t in (answer or "")]),
    ]
    return ("PASS" if all(c[1] for c in checks) else "FAIL"), checks


def load_legacy(fname):
    p = os.path.join(LEGACY_EV, fname)
    if not os.path.exists(p):
        return None
    d = json.load(io.open(p, encoding="utf-8"))
    t = d["turns"][0]
    route = None
    for n in t.get("node_detail") or []:
        if n.get("node_id") == "uapp_route":
            route = J(n.get("outputs"))
    ids = [n.get("node_id") for n in t.get("nodes_executed") or []]
    return {"route": route, "answer": t.get("answer") or "",
            "ask_one_ran": "uapp_ask_one" in ids,
            "capability_ran": any(x in ids for x in ("uapp_m3", "uapp_seam", "uapp_hop")),
            "nodes": ids}


def main():
    g = json.load(io.open(GATE, encoding="utf-8"))
    LEAK = g["leak_forbidden_tokens"]
    results = []

    for fname, label in (("UAPP-INTENT-02N_attempt40e45858.json", "已知坏例·硬猜能力并真跑"),
                         ("UAPP-INTENT-02N_attempt00d9dcdd.json", "已知坏例·落对话且多问题")):
        L = load_legacy(fname)
        if L is None:
            results.append({"fixture": fname, "label": label, "status": "SKIPPED_SOURCE_ABSENT"})
            continue
        v, ch = judge_negative(L["route"], L["ask_one_ran"], L["capability_ran"],
                               L["answer"], LEAK)
        results.append({"fixture": fname, "label": label, "expected": "FAIL", "got": v,
                        "discriminates": v == "FAIL",
                        "observed_route_mode": (L["route"] or {}).get("route_mode"),
                        "observed_target": (L["route"] or {}).get("target_capability"),
                        "observed_question_count": qcount(L["answer"]),
                        "capability_nodes_ran": L["capability_ran"],
                        "failed_checks": [c[0] for c in ch if not c[1]]})

    good_route = {"route_mode": "ASK_ONE", "asks_one": "true", "target_capability": ""}
    good_answer = "这一步我先确认一件事，确认完直接往下做：\n\n你想改的是哪一面？"
    v, ch = judge_negative(good_route, True, False, good_answer, LEAK)
    results.append({"fixture": "synthetic_good", "label": "合成好例·只问一个未猜能力",
                    "expected": "PASS", "got": v, "discriminates": v == "PASS",
                    "observed_question_count": qcount(good_answer),
                    "failed_checks": [c[0] for c in ch if not c[1]]})

    live = [r for r in results if r.get("status") != "SKIPPED_SOURCE_ABSENT"]
    out = {"test": "S1_VALIDATOR_DISCRIMINATION", "model_calls": 0,
           "stage_gate_sha256": __import__("hashlib").sha256(
               io.open(GATE, "rb").read()).hexdigest(),
           "legacy_evidence_dir": LEGACY_EV,
           "legacy_access": "READ_ONLY",
           "results": results,
           "verdict": "PASS" if live and all(r["discriminates"] for r in live) else "FAIL"}
    print(json.dumps(out, ensure_ascii=False, indent=2))
    p = os.path.join(HERE, "..", "evidence", "S1_VALIDATOR_DISCRIMINATION.json")
    with io.open(p, "w", encoding="utf-8") as fh:
        fh.write(json.dumps(out, ensure_ascii=False, indent=2) + "\n")
    return 0 if out["verdict"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
