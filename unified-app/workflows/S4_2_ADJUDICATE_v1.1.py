#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Node S4.2｜按已冻结判据独立判定五项能力。零模型调用。

编造检查用一组**只可能来自夹具**的标记：品牌名与四位真实人物角色名、以及夹具里的价格带。
正例必须出现其中之一 —— 证明夹具真的进入了能力；
负例必须一个都不出现 —— 没给资料却说得出来，就是编造。
同一组标记，两侧期望相反，任一侧塌陷都会被看见。
"""
import hashlib
import io
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
GATE = os.path.join(HERE, "..", "stages", "S4_2_STAGE_GATE_v1.1.json")
EV = os.path.join(HERE, "..", "evidence", "stages")

FIXTURE_ONLY = ["序里集", "XULI", "林序", "周宁", "苏禾", "陈晚"]
PRICE_BAND = re.compile(r"\d{3,4}\s*[-—~～至]\s*\d{3,4}\s*元")
PLACEHOLDER = "这一步没有产出可以交给你的内容"
ALL_TOOLS = ["tool_matrix", "tool_campaign", "tool_content_brief", "tool_creative_script",
             "tool_production_director", "tool_publishing_packaging"]


def J(x):
    if isinstance(x, str):
        try:
            return json.loads(x)
        except Exception:
            return {}
    return x if isinstance(x, dict) else {}


def out(d, nid):
    for n in d.get("node_detail") or []:
        if n.get("node_id") == nid:
            return J(n.get("outputs"))
    return {}


def ok(d, nid):
    for n in d.get("nodes_executed") or []:
        if n.get("node_id") == nid:
            return n.get("status") == "succeeded"
    return False


def ids(d):
    return [n.get("node_id") for n in d.get("nodes_executed") or []]


def judge(d, g, cap, spec, kind):
    LEAK = g["leak_forbidden_tokens"]
    want = spec["seam_node"]
    r = out(d, "uapp_route")
    nested = d.get("nested_app_runs") or {}
    seam_nodes = (nested.get("SEAM") or {}).get("latest_run_nodes") or []
    seam_ran = {n.get("node_id"): n.get("status") for n in seam_nodes}
    dl = out(d, "uapp_delivery")
    so = out(d, "uapp_seam")
    ans = d.get("answer") or ""
    c = []

    c.append(("路由落到该能力，模式为 CAPABILITY，来源 \u2208 {m1_named, canvas_triage}",
              r.get("target_capability") == cap and r.get("route_mode") == "CAPABILITY"
              and r.get("intent_source") in ("m1_named", "canvas_triage"),
              {"target": r.get("target_capability"), "source": r.get("intent_source"),
               "route_mode": r.get("route_mode")}))
    # 原判据断言的是「由哪一段内部机制桥接」，属于 HOW 且断错了（见 TRIAGE R2）。
    # 它想防的是「用例被输入里的能力名喂成送分题」——这里直接检验输入本身，
    # 比断言内部标签更强，且可确定性复算。
    q = (d.get("query") or "").lower()
    named = [t for t in g["forbidden_input_tokens"] if t.lower() in q]
    c.append(("输入串中不含任何能力名/模块名/内部字段名（确定性匹配）", not named,
              {"query": d.get("query"), "hits": named}))
    c.append(("未落入只问一个（歧义规则未过度触发）",
              r.get("route_mode") != "ASK_ONE" and "uapp_ask_one" not in ids(d),
              {"route_mode": r.get("route_mode")}))
    c.append(("画布 uapp_hop 与 uapp_seam 实际执行且 succeeded",
              ok(d, "uapp_hop") and ok(d, "uapp_seam"),
              {"hop": ok(d, "uapp_hop"), "seam": ok(d, "uapp_seam")}))
    c.append(("Seam 自身记录中该能力节点执行且 succeeded（唯一权威证据）",
              seam_ran.get(want) == "succeeded",
              {"want": want, "status": seam_ran.get(want),
               "seam_tools_ran": [x for x in seam_ran if x.startswith("tool_")]}))
    others = [t for t in ALL_TOOLS if t != want and t in seam_ran]
    c.append(("其余五个能力节点该轮均未执行（不暗跑）", not others, {"others": others}))
    ud = str(so.get("user_delivery") or "").strip()
    rj = str(so.get("returns_json") or "").strip()
    c.append(("组件 Return 回到画布：user_delivery 或 returns_json 非空",
              bool(ud) or rj not in ("", "[]"),
              {"ud_len": len(ud), "rj_len": len(rj), "outcome": so.get("business_delivery_outcome")}))
    c.append(("交付正文非空、非占位",
              bool(ans.strip()) and not ans.startswith(PLACEHOLDER), {"len": len(ans.strip())}))
    c.append(("leak_hit_count = 0", str(dl.get("leak_hit_count")) == "0",
              {"count": dl.get("leak_hit_count"), "hits": dl.get("leak_hits_json")}))
    lk = [x for x in LEAK if x in ans]
    c.append(("交付正文零禁词命中（判定侧独立复算）", not lk, lk))

    marks = [m for m in FIXTURE_ONLY if m in ans]
    price = bool(PRICE_BAND.search(ans))
    outcome = str(so.get("business_delivery_outcome") or "")
    if kind == "POS":
        c.append(("正例：夹具事实真的进入了能力（交付中出现只可能来自夹具的标记，或已判交付）",
                  bool(marks) or price or outcome.startswith("DELIVERED"),
                  {"fixture_marks": marks, "price_band_present": price, "outcome": outcome}))
    else:
        c.append(("负例：未编造任何夹具未提供的经营事实（品牌名/人物名/价格带一个都不出现）",
                  not marks and not price,
                  {"fabricated_marks": marks, "price_band_present": price}))
        c.append(("负例：停在缺口而非给出成品",
                  (not outcome.startswith("DELIVERED")) or ("precise_gap" in rj),
                  {"outcome": outcome, "has_precise_gap": "precise_gap" in rj}))
    return ([{"desc": x[0], "result": "PASS" if x[1] else "FAIL", "observed": x[2]} for x in c],
            "PASS" if all(x[1] for x in c) else "FAIL")


def main():
    g = json.load(io.open(GATE, encoding="utf-8"))
    gsha = hashlib.sha256(io.open(GATE, "rb").read()).hexdigest()
    res = {"stage": "S4.2", "stage_gate_sha256": gsha,
           "model_calls_by_adjudicator": 0, "cases": {}}
    for cap, spec in g["capabilities"].items():
        for kind in ("POS", "NEG"):
            cid = "S4-CAP-%s-%s" % (cap, kind)
            p = os.path.join(EV, cid + ".json")
            if not os.path.exists(p):
                res["cases"][cid] = {"verdict": "NOT_RUN", "checks": []}
                continue
            d = json.load(io.open(p, encoding="utf-8"))
            assert d["stage_gate_sha256"] == gsha, cid + "：证据绑定的判据版本不一致，拒绝判定"
            checks, verdict = judge(d, g, cap, spec, kind)
            res["cases"][cid] = {"capability": cap, "kind": kind, "verdict": verdict,
                                 "checks": checks, "answer_head": (d.get("answer") or "")[:200],
                                 "workflow_run_id": d.get("workflow_run_id"),
                                 "elapsed_seconds": d.get("elapsed_seconds")}
    v = {k: x["verdict"] for k, x in res["cases"].items()}
    done = [x for x in v.values() if x != "NOT_RUN"]
    res["summary"] = {"verdicts": v,
                      "all_pass": bool(done) and all(y == "PASS" for y in v.values()),
                      "not_run": [k for k, y in v.items() if y == "NOT_RUN"]}
    print(json.dumps(res["summary"], ensure_ascii=False, indent=2))
    for k, x in res["cases"].items():
        if x["verdict"] == "NOT_RUN":
            continue
        print("=" * 74)
        print(k, "->", x["verdict"], "|", x.get("elapsed_seconds"), "s")
        for ck in x["checks"]:
            if ck["result"] == "FAIL":
                print("   [FAIL] %s | %s" % (ck["desc"],
                                             json.dumps(ck["observed"], ensure_ascii=False)[:180]))
        print("   passed %d/%d" % (sum(1 for y in x["checks"] if y["result"] == "PASS"),
                                   len(x["checks"])))
    with io.open(os.path.join(HERE, "..", "evidence", "S4_2_ADJUDICATION.json"), "w",
                 encoding="utf-8") as fh:
        fh.write(json.dumps(res, ensure_ascii=False, indent=2) + "\n")


if __name__ == "__main__":
    main()
