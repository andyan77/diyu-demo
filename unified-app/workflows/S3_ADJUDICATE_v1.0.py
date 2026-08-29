#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Node S3｜按已冻结判据独立判定。与运行器分离。零模型调用。"""
import hashlib
import io
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
GATE = os.path.join(HERE, "..", "stages", "S3_STAGE_GATE_v1.0.json")
EV = os.path.join(HERE, "..", "evidence", "stages")

M2ANY = {"boot_user", "boot_ws", "boot_acct", "boot_cycle", "boot_task", "boot_assign",
         "boot_p1", "boot_p2", "boot_p3", "boot_p4", "boot_p5",
         "uapp_m2_cycle", "uapp_m2_dec", "uapp_m2_run"}
PROMISE = [r"(已经|已)\s*(转交|交给|派给|转给|移交)",
           r"(正在|已在|马上|稍后|随后)\s*(推进|处理|调用|执行|分析|生成|安排)",
           r"等(结果|它)?\s*(出来|返回|回来|好了)"]
# 「要求用户点名模块／选能力」的判据。M3 自己问业务问题不算，问「要不要调用某能力」才算。
PICK = [r"(要不要|需不需要|你希望|请你?选择|你来选)\s*(我)?\s*(帮你)?\s*(现在)?\s*(就)?"
        r"\s*(调用|启动|进入|请|找|叫|用)\s*(?:相应|对应|专业|哪个|哪一个|的)*\s*(能力|模块|专家|功能)",
        r"你想用(哪个|哪一个)\s*(能力|模块|功能)",
        r"(请|麻烦你)?(先)?(告诉我|指定)\s*(要用|调用)\s*(哪个|哪一个)\s*(能力|模块)"]
PRX, PKX = [re.compile(p) for p in PROMISE], [re.compile(p) for p in PICK]
PLACEHOLDER = "这一步没有产出可以交给你的内容"


def J(x):
    if isinstance(x, str):
        try:
            return json.loads(x)
        except Exception:
            return {}
    return x if isinstance(x, dict) else {}


def nd(turn, nid):
    for n in turn.get("node_detail") or []:
        if n.get("node_id") == nid:
            return n
    return None


def out(turn, nid):
    n = nd(turn, nid)
    return J(n.get("outputs")) if n else {}


def inp(turn, nid):
    n = nd(turn, nid)
    return J(n.get("inputs")) if n else {}


def ids(turn):
    return [n.get("node_id") for n in turn.get("nodes_executed") or []]


def ok(turn, nid):
    for n in turn.get("nodes_executed") or []:
        if n.get("node_id") == nid:
            return n.get("status") == "succeeded"
    return False


def leaks(t, toks):
    return [x for x in toks if x in (t or "")]


def qc(t):
    return (t or "").count("?") + (t or "").count("？")


def main():
    g = json.load(io.open(GATE, encoding="utf-8"))
    gsha = hashlib.sha256(io.open(GATE, "rb").read()).hexdigest()
    LEAK = g["leak_forbidden_tokens"]
    res = {"stage": "S3", "stage_gate_sha256": gsha, "model_calls_by_adjudicator": 0, "cases": {}}

    def load(cid):
        d = json.load(io.open(os.path.join(EV, cid + ".json"), encoding="utf-8"))
        assert d["stage_gate_sha256"] == gsha, "证据绑定的判据版本与当前判据不一致，拒绝判定"
        return d

    # ---------------- S3-MAIN-01 ----------------
    d = load("S3-MAIN-01")
    t1, t2 = d["turns"][0], d["turns"][1]
    seed = d.get("seed") or {}
    r1 = out(t1, "uapp_route")
    c = []
    c.append(("T1 形成账号经营诊断方向（route_mode）",
              r1.get("route_mode") in ("CAPABILITY", "OPERATION_ONLY"), r1.get("route_mode")))
    c.append(("T1 落点 ∈ {MATRIX, SINGLE_ACCOUNT_OPERATION}",
              (r1.get("target_capability") in ("MATRIX", "SINGLE_ACCOUNT_OPERATION")
               or r1.get("intent") in ("MATRIX", "SINGLE_ACCOUNT_OPERATION")),
              {"target": r1.get("target_capability"), "intent": r1.get("intent")}))
    c.append(("T1 uapp_m3 节点实际执行且 succeeded", ok(t1, "uapp_m3"),
              {"ran": "uapp_m3" in ids(t1), "succeeded": ok(t1, "uapp_m3")}))
    # M2 投影真实进入 M3：比对 uapp_m3 的入参与 uapp_ctx 的输出
    ctx1 = out(t1, "uapp_ctx")
    m3in1 = inp(t1, "uapp_m3")
    ac_ctx = (ctx1.get("account_context") or "")
    ac_m3 = str(m3in1.get("account_context") or "")
    c.append(("T1 M2 当前投影逐字节进入 M3 的入参",
              bool(ac_ctx) and ac_ctx == ac_m3 and "来源 M2 服务实时读取" in ac_m3,
              {"ctx_len": len(ac_ctx), "m3_in_len": len(ac_m3), "identical": ac_ctx == ac_m3,
               "has_m2_marker": "来源 M2 服务实时读取" in ac_m3}))
    dl1 = out(t1, "uapp_s3_deliver")
    a1 = t1.get("answer") or ""
    c.append(("T1 M3 返回有内容的诊断或精确缺口，非空白非占位",
              dl1.get("delivered_flag") == "true" and not a1.startswith(PLACEHOLDER)
              and len(a1.strip()) >= 120,
              {"delivered_flag": dl1.get("delivered_flag"), "answer_len": len(a1.strip()),
               "is_placeholder": a1.startswith(PLACEHOLDER)}))
    pick1 = [rx.pattern for rx in PKX if rx.search(a1)]
    c.append(("T1 不要求用户点名模块或选择能力", not pick1, pick1))
    prom1 = [rx.pattern for rx in PRX if rx.search(a1)]
    c.append(("T1 不声称未发生的调用或写入", not prom1, prom1))
    c.append(("T1 leak_hit_count = 0", str(dl1.get("leak_hit_count")) == "0",
              {"leak_hit_count": dl1.get("leak_hit_count"),
               "leak_hits": dl1.get("leak_hits_json")}))

    c.append(("T2 同会话追问不退回普通对话：uapp_m3 再次实际执行", ok(t2, "uapp_m3"),
              {"ran": "uapp_m3" in ids(t2), "succeeded": ok(t2, "uapp_m3")}))
    seeded = str(((seed.get("write") or {}).get("request_body") or {}).get("decision") or "")
    m3in2 = inp(t2, "uapp_m3")
    ac2 = str(m3in2.get("account_context") or "")
    c.append(("T2 SEED 写入的决策值确实进入了 M3 这一轮的投影",
              bool(seeded) and seeded in ac2,
              {"seeded": seeded, "found_in_m3_input": bool(seeded) and seeded in ac2,
               "seed_write_http": (seed.get("write") or {}).get("http_status")}))
    dl2 = out(t2, "uapp_s3_deliver")
    a2 = t2.get("answer") or ""
    c.append(("T2 leak_hit_count = 0", str(dl2.get("leak_hit_count")) == "0",
              dl2.get("leak_hit_count")))
    lk = leaks(a1, LEAK) + leaks(a2, LEAK)
    c.append(("两轮正文零禁词命中（判定侧独立复算）", not lk, lk))
    res["cases"]["S3-MAIN-01"] = {
        "checks": [{"desc": x[0], "result": "PASS" if x[1] else "FAIL", "observed": x[2]} for x in c],
        "verdict": "PASS" if all(x[1] for x in c) else "FAIL",
        "T1_route": r1, "T1_answer": a1, "T2_answer": a2,
        "T1_modules_actually_run": dl1.get("modules_actually_run"),
        "workflow_run_ids": [t1.get("workflow_run_id"), t2.get("workflow_run_id")],
        "m3_app_runs": d.get("m3_app_workflow_runs_last_30min")}

    # ---------------- S3-REG-ASK-01 ----------------
    d = load("S3-REG-ASK-01")
    a = d["turns"][0]
    ra = out(a, "uapp_route")
    hit = [n for n in ids(a) if n in M2ANY or n == "uapp_m3"]
    an = a.get("answer") or ""
    c = [("route_mode = ASK_ONE", ra.get("route_mode") == "ASK_ONE", ra.get("route_mode")),
         ("uapp_ask_one 实际执行", "uapp_ask_one" in ids(a), "uapp_ask_one" in ids(a)),
         ("问号计数为 1", qc(an) == 1, qc(an)),
         ("未猜任何能力", not (ra.get("target_capability") or ""), ra.get("target_capability")),
         ("本轮零 M2 节点、零 M3 节点执行", not hit, {"hits": hit}),
         ("零内部字段泄漏", not leaks(an, LEAK), leaks(an, LEAK))]
    res["cases"]["S3-REG-ASK-01"] = {
        "checks": [{"desc": x[0], "result": "PASS" if x[1] else "FAIL", "observed": x[2]} for x in c],
        "verdict": "PASS" if all(x[1] for x in c) else "FAIL",
        "route": ra, "answer": an, "workflow_run_id": a.get("workflow_run_id")}

    v = {k: x["verdict"] for k, x in res["cases"].items()}
    res["summary"] = {"verdicts": v, "all_pass": all(y == "PASS" for y in v.values()),
                      "next_stage_allowed": all(y == "PASS" for y in v.values())}
    print(json.dumps(res["summary"], ensure_ascii=False, indent=2))
    for k, x in res["cases"].items():
        print("=" * 72)
        print(k, "->", x["verdict"])
        for ck in x["checks"]:
            print("   [%s] %s | %s" % (ck["result"], ck["desc"],
                                       json.dumps(ck["observed"], ensure_ascii=False)[:140]))
    with io.open(os.path.join(HERE, "..", "evidence", "S3_ADJUDICATION.json"), "w",
                 encoding="utf-8") as fh:
        fh.write(json.dumps(res, ensure_ascii=False, indent=2) + "\n")


if __name__ == "__main__":
    main()
