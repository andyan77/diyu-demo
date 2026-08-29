#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Node S4.1｜按已冻结判据独立判定。零模型调用。

核心取证口径：**目标能力是否真的执行，只认 Seam 应用自己的节点执行记录。**
画布 succeeded、模型自述、交付正文的任何说法都不构成证据。
"""
import hashlib
import io
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
GATE = os.path.join(HERE, "..", "stages", "S4_1_STAGE_GATE_v1.1.json")
EV = os.path.join(HERE, "..", "evidence", "stages")

SEAM_TOOLS = {"MATRIX": "tool_matrix", "CAMPAIGN": "tool_campaign",
              "CONTENT_BRIEF": "tool_content_brief", "CREATIVE_SCRIPT": "tool_creative_script",
              "PRODUCTION_DIRECTOR": "tool_production_director",
              "PUBLISHING_PACKAGING": "tool_publishing_packaging"}
HEAVY = {"uapp_m3", "uapp_hop", "uapp_seam", "boot_user", "boot_ws", "boot_acct",
         "boot_cycle", "boot_task", "uapp_m2_cycle", "uapp_m2_dec", "uapp_m2_run"}
PLACEHOLDER = "这一步没有产出可以交给你的内容"


def J(x):
    if isinstance(x, str):
        try:
            return json.loads(x)
        except Exception:
            return {}
    return x if isinstance(x, dict) else {}


def nd(t, nid):
    for n in t.get("node_detail") or []:
        if n.get("node_id") == nid:
            return n
    return None


def out(t, nid):
    n = nd(t, nid)
    return J(n.get("outputs")) if n else {}


def inp(t, nid):
    n = nd(t, nid)
    return J(n.get("inputs")) if n else {}


def ids(t):
    return [n.get("node_id") for n in t.get("nodes_executed") or []]


def ok(t, nid):
    for n in t.get("nodes_executed") or []:
        if n.get("node_id") == nid:
            return n.get("status") == "succeeded"
    return False


def qc(t):
    return (t or "").count("?") + (t or "").count("？")


def main():
    g = json.load(io.open(GATE, encoding="utf-8"))
    gsha = hashlib.sha256(io.open(GATE, "rb").read()).hexdigest()
    LEAK = g["leak_forbidden_tokens"]
    TARGET = g["representative_capability"]["chosen"]
    res = {"stage": "S4.1", "stage_gate_sha256": gsha, "model_calls_by_adjudicator": 0, "cases": {}}

    def load(cid):
        d = json.load(io.open(os.path.join(EV, cid + ".json"), encoding="utf-8"))
        assert d["stage_gate_sha256"] == gsha, "证据绑定的判据版本与当前判据不一致，拒绝判定"
        return d

    # ---------------- S4-CAP-MATRIX-01 ----------------
    d = load("S4-CAP-MATRIX-01_a2")
    t = d["turns"][0]
    r = out(t, "uapp_route")
    nested = d.get("nested_app_runs") or {}
    seam_nodes = (nested.get("SEAM") or {}).get("latest_run_nodes") or []
    seam_ran = {n.get("node_id"): n.get("status") for n in seam_nodes}
    c = []
    c.append(("画布侧 uapp_m3 / uapp_hop / uapp_seam 依次实际执行且 succeeded",
              ok(t, "uapp_m3") and ok(t, "uapp_hop") and ok(t, "uapp_seam"),
              {n: ok(t, n) for n in ("uapp_m3", "uapp_hop", "uapp_seam")}))
    want_tool = SEAM_TOOLS[TARGET]
    c.append(("Seam 自身运行记录中目标能力节点实际执行且 succeeded（唯一权威证据）",
              seam_ran.get(want_tool) == "succeeded",
              {"target": TARGET, "seam_node": want_tool,
               "status": seam_ran.get(want_tool), "seam_nodes_ran": list(seam_ran)}))
    others = [v for k, v in SEAM_TOOLS.items() if k != TARGET and v in seam_ran]
    c.append(("Seam 内其余五个能力节点均未执行（不暗跑）", not others, {"others_ran": others}))
    so = out(t, "uapp_seam")
    ud = str(so.get("user_delivery") or "").strip()
    rj = str(so.get("returns_json") or "").strip()
    c.append(("组件 Return 回到画布：user_delivery 或 returns_json 非空",
              bool(ud) or rj not in ("", "[]"),
              {"user_delivery_len": len(ud), "returns_json_len": len(rj),
               "outcome": so.get("business_delivery_outcome")}))
    dl = out(t, "uapp_delivery")
    ans = t.get("answer") or ""
    c.append(("交付正文非空、非占位",
              bool(ans.strip()) and not ans.startswith(PLACEHOLDER) and len(ans.strip()) >= 80,
              {"answer_len": len(ans.strip()), "is_placeholder": ans.startswith(PLACEHOLDER)}))
    # 跨跳不丢不改
    m3o = str(out(t, "uapp_m3").get("operating_judgment") or "")
    hopi = str(inp(t, "uapp_hop").get("m3_judgment") or "")
    seami = str(inp(t, "uapp_seam").get("capability") or "")
    c.append(("跨跳不丢不改·M3 判断逐字节进入 Hop 入参",
              bool(m3o) and m3o == hopi,
              {"m3_len": len(m3o), "hop_in_len": len(hopi), "identical": m3o == hopi}))
    c.append(("跨跳不丢不改·Seam 入参 capability = 路由确定的目标能力",
              seami == (r.get("target_capability") or "") and seami == TARGET,
              {"seam_in": seami, "route_target": r.get("target_capability")}))
    c.append(("leak_hit_count = 0", str(dl.get("leak_hit_count")) == "0",
              {"count": dl.get("leak_hit_count"), "hits": dl.get("leak_hits_json")}))
    lk = [x for x in LEAK if x in ans]
    c.append(("交付正文零禁词命中（判定侧独立复算）", not lk, lk))
    mods = str(dl.get("modules_actually_run") or "")
    c.append(("modules_actually_run 报告了 M4 能力接缝这一跳，与实际执行一致",
              "接缝" in mods or "M4" in mods, {"modules": mods}))
    res["cases"]["S4-CAP-MATRIX-01"] = {
        "checks": [{"desc": x[0], "result": "PASS" if x[1] else "FAIL", "observed": x[2]} for x in c],
        "verdict": "PASS" if all(x[1] for x in c) else "FAIL",
        "route": r, "answer": ans, "seam_nodes_ran": seam_ran,
        "workflow_run_id": t.get("workflow_run_id"),
        "nested_run_counts": {k: len((v or {}).get("runs") or []) for k, v in nested.items()}}

    # ---------------- S4-REG-ASK-01 ----------------
    d = load("S4-REG-ASK-01_a2")
    a = d["turns"][0]
    ra = out(a, "uapp_route")
    hit = [n for n in ids(a) if n in HEAVY]
    an = a.get("answer") or ""
    c = [("route_mode = ASK_ONE", ra.get("route_mode") == "ASK_ONE", ra.get("route_mode")),
         ("uapp_ask_one 实际执行", "uapp_ask_one" in ids(a), "uapp_ask_one" in ids(a)),
         ("问号计数为 1", qc(an) == 1, qc(an)),
         ("未猜任何能力", not (ra.get("target_capability") or ""), ra.get("target_capability")),
         ("本轮零 M2 / 零 M3 / 零 Hop / 零 Seam 节点执行", not hit, {"hits": hit}),
         ("零内部字段泄漏", not [x for x in LEAK if x in an], [x for x in LEAK if x in an])]
    res["cases"]["S4-REG-ASK-01"] = {
        "checks": [{"desc": x[0], "result": "PASS" if x[1] else "FAIL", "observed": x[2]} for x in c],
        "verdict": "PASS" if all(x[1] for x in c) else "FAIL",
        "route": ra, "answer": an, "workflow_run_id": a.get("workflow_run_id")}

    v = {k: x["verdict"] for k, x in res["cases"].items()}
    res["summary"] = {"verdicts": v, "all_pass": all(y == "PASS" for y in v.values()),
                      "next_step_allowed": all(y == "PASS" for y in v.values())}
    print(json.dumps(res["summary"], ensure_ascii=False, indent=2))
    for k, x in res["cases"].items():
        print("=" * 74)
        print(k, "->", x["verdict"])
        for ck in x["checks"]:
            print("   [%s] %s | %s" % (ck["result"], ck["desc"],
                                       json.dumps(ck["observed"], ensure_ascii=False)[:150]))
    with io.open(os.path.join(HERE, "..", "evidence", "S4_1_ADJUDICATION_a2.json"), "w",
                 encoding="utf-8") as fh:
        fh.write(json.dumps(res, ensure_ascii=False, indent=2) + "\n")


if __name__ == "__main__":
    main()
