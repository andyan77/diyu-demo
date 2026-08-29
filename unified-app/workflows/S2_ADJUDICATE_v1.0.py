#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Node S2｜按已冻结判据独立判定。与运行器分离。零模型调用。

只认 workflow_node_executions 与 M2 数据库真实行。
"""
import hashlib
import io
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
GATE = os.path.join(HERE, "..", "stages", "S2_STAGE_GATE_v1.1.json")
EV = os.path.join(HERE, "..", "evidence", "stages")

BOOT = ["boot_user", "boot_ws", "boot_acct", "boot_cycle", "boot_task", "boot_assign"]
M2READ = ["uapp_m2_cycle", "uapp_m2_dec", "uapp_m2_run"]
M2ANY = set(BOOT + M2READ + ["boot_p1", "boot_p2", "boot_p3", "boot_p4", "boot_p5"])
PROMISE = [r"(已经|已)\s*(转交|交给|派给|转给|移交)",
           r"(正在|已在|马上|稍后|随后)\s*(推进|处理|调用|执行|分析|生成|安排)",
           r"等(结果|它)?\s*(出来|返回|回来|好了)",
           r"(将|会|即将|准备)\s*(为你|帮你)?\s*(调用|启动|接入|进入)\s*(?:相应|对应|专业|的)*\s*(能力|模块|专家)"]
PRX = [re.compile(p) for p in PROMISE]


def J(x):
    if isinstance(x, str):
        try:
            return json.loads(x)
        except Exception:
            return {}
    return x if isinstance(x, dict) else {}


def out(turn, nid):
    for n in turn.get("node_detail") or []:
        if n.get("node_id") == nid:
            return J(n.get("outputs"))
    return {}


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
    res = {"stage": "S2", "stage_gate_sha256": gsha, "model_calls_by_adjudicator": 0, "cases": {}}

    def load(cid):
        d = json.load(io.open(os.path.join(EV, cid + ".json"), encoding="utf-8"))
        assert d["stage_gate_sha256"] == gsha, "证据绑定的判据版本与当前判据不一致，拒绝判定"
        return d

    # ---------------- S2-POS-01 ----------------
    d = load("S2-POS-01_a2")
    t1, t2 = d["turns"][0], d["turns"][1]
    seed = d.get("seed") or {}
    c = []
    c.append(("T1 建域链五个写入节点全部 succeeded",
              all(ok(t1, n) for n in BOOT), {n: ok(t1, n) for n in BOOT}))
    c.append(("T1 三个 M2 只读投影节点全部 succeeded",
              all(ok(t1, n) for n in M2READ), {n: ok(t1, n) for n in M2READ}))
    p1 = out(t1, "uapp_s2_pending")
    c.append(("T1 如实报告尚无经营记录（未把空响应升级成已知事实）",
              p1.get("m2_state") == "reachable_no_record", p1.get("m2_state")))
    c.append(("SEED 写入 M2 成功", seed.get("status") == "DONE"
              and (seed.get("write") or {}).get("http_status") in (200, 201),
              {"status": seed.get("status"),
               "write_http": (seed.get("write") or {}).get("http_status")}))
    c.append(("SEED 在 M2 数据库中可查到真实行",
              (seed.get("db_rows_with_idempotency_key") or "0").strip() not in ("", "0"),
              seed.get("db_rows_with_idempotency_key")))
    ran_boot_t2 = [n for n in BOOT if n in ids(t2)]
    c.append(("T2 建域链未再执行（同会话不重复建域，幂等成立）",
              not ran_boot_t2, {"boot_nodes_in_T2": ran_boot_t2}))
    c.append(("T2 三个 M2 只读投影节点全部 succeeded",
              all(ok(t2, n) for n in M2READ), {n: ok(t2, n) for n in M2READ}))
    p2 = out(t2, "uapp_s2_pending")
    c.append(("T2 读到记录：m2_state = reachable_with_record",
              p2.get("m2_state") == "reachable_with_record", p2.get("m2_state")))
    ctx2 = out(t2, "uapp_ctx")
    # 期望值不硬编码：直接取 SEED 实际写进 M2 的 decision 值，再回查投影正文。
    # 这样判据无法被「改期望去迁就结果」凑过去——期望由被写入的事实自己决定。
    seeded = str(((seed.get("write") or {}).get("request_body") or {}).get("decision") or "")
    dec_line = [l for l in (ctx2.get("account_context") or "").splitlines()
                if "最近一次周期决策" in l]
    c.append(("T2 投影正文含 SEED 实际写入的决策值",
              bool(seeded) and any(seeded in l for l in dec_line),
              {"seeded_decision": seeded, "projection_line": dec_line}))
    p2b = out(t2, "uapp_s2_pending")
    c.append(("T2 pending 读到的 decision 与 SEED 写入值一致（载荷判定，非状态码判定）",
              bool(seeded) and p2b.get("decision_seen") == seeded,
              {"decision_seen": p2b.get("decision_seen"), "seeded": seeded}))
    lk = leaks(t1.get("answer"), LEAK) + leaks(t2.get("answer"), LEAK)
    c.append(("两轮零内部字段泄漏", not lk, lk))
    res["cases"]["S2-POS-01"] = {
        "checks": [{"desc": x[0], "result": "PASS" if x[1] else "FAIL", "observed": x[2]} for x in c],
        "verdict": "PASS" if all(x[1] for x in c) else "FAIL",
        "T1_answer": t1.get("answer"), "T2_answer": t2.get("answer"),
        "workflow_run_ids": [t1.get("workflow_run_id"), t2.get("workflow_run_id")]}

    # ---------------- S2-NEG-01 ----------------
    d = load("S2-NEG-01_a2")
    n1, n2 = d["turns"][0], d["turns"][1]
    r1, r2 = out(n1, "uapp_route"), out(n2, "uapp_route")
    q1 = out(n1, "uapp_s2_pending")
    c = []
    c.append(("N1 决策查询未返回记录，m2_state = reachable_no_record",
              q1.get("m2_state") == "reachable_no_record", q1.get("m2_state")))
    c.append(("N1 正文明确说明还没有可用的经营记录",
              "还没有" in (n1.get("answer") or "") and "确实还没有" in (n1.get("answer") or ""),
              (n1.get("answer") or "")[:120]))
    c.append(("N1 未把「读不到」与「没有记录」混同", q1.get("m2_state") != "unreachable",
              q1.get("m2_state")))
    c.append(("N1 的无记录判定来自载荷而非状态码：decisions/latest 是 200，但 decision 为哨兵值",
              "decisions/latest=200" in (out(n1, "uapp_ctx").get("m2_note") or "")
              and str(q1.get("decision_seen") or "").lower() in
              ("", "none", "null", "none_recorded", "not_recorded", "no_record", "unknown"),
              {"m2_note": out(n1, "uapp_ctx").get("m2_note"),
               "decision_seen": q1.get("decision_seen")}))
    c.append(("回归 S1-POS-01·route_mode ∈ {CAPABILITY, OPERATION_ONLY}",
              r1.get("route_mode") in ("CAPABILITY", "OPERATION_ONLY"), r1.get("route_mode")))
    c.append(("回归 S1-POS-01·落点 ∈ {MATRIX, SINGLE_ACCOUNT_OPERATION}",
              (r1.get("target_capability") in ("MATRIX", "SINGLE_ACCOUNT_OPERATION")
               or r1.get("intent") in ("MATRIX", "SINGLE_ACCOUNT_OPERATION")),
              {"target": r1.get("target_capability"), "intent": r1.get("intent")}))
    c.append(("回归 S1-POS-01·intent_source = canvas_triage",
              r1.get("intent_source") == "canvas_triage", r1.get("intent_source")))
    c.append(("回归 S1-FOLLOW-01·N2 未退回 DIALOGUE",
              r2.get("route_mode") in ("CAPABILITY", "OPERATION_ONLY", "STATUS"),
              r2.get("route_mode")))
    c.append(("N2 未重复建域", not [n for n in BOOT if n in ids(n2)],
              [n for n in BOOT if n in ids(n2)]))
    hits = [rx.pattern for rx in PRX if rx.search(n1.get("answer") or "")] + \
           [rx.pattern for rx in PRX if rx.search(n2.get("answer") or "")]
    c.append(("两轮均无异步承诺", not hits, hits))
    lk = leaks(n1.get("answer"), LEAK) + leaks(n2.get("answer"), LEAK)
    c.append(("两轮零内部字段泄漏", not lk, lk))
    res["cases"]["S2-NEG-01"] = {
        "checks": [{"desc": x[0], "result": "PASS" if x[1] else "FAIL", "observed": x[2]} for x in c],
        "verdict": "PASS" if all(x[1] for x in c) else "FAIL",
        "N1_route": r1, "N2_route": r2, "N1_answer": n1.get("answer"),
        "workflow_run_ids": [n1.get("workflow_run_id"), n2.get("workflow_run_id")]}

    # ---------------- S2-REG-ASK-01 ----------------
    d = load("S2-REG-ASK-01_a2")
    a = d["turns"][0]
    ra = out(a, "uapp_route")
    m2hit = [n for n in ids(a) if n in M2ANY]
    c = []
    c.append(("route_mode = ASK_ONE", ra.get("route_mode") == "ASK_ONE", ra.get("route_mode")))
    c.append(("uapp_ask_one 实际执行", "uapp_ask_one" in ids(a), "uapp_ask_one" in ids(a)))
    c.append(("问号计数为 1", qc(a.get("answer")) == 1, qc(a.get("answer"))))
    c.append(("未猜任何能力", not (ra.get("target_capability") or ""), ra.get("target_capability")))
    c.append(("本轮零 M2 节点执行（只问一个不产生任何持久化副作用）", not m2hit,
              {"m2_nodes_hit": m2hit}))
    lk = leaks(a.get("answer"), LEAK)
    c.append(("零内部字段泄漏", not lk, lk))
    res["cases"]["S2-REG-ASK-01"] = {
        "checks": [{"desc": x[0], "result": "PASS" if x[1] else "FAIL", "observed": x[2]} for x in c],
        "verdict": "PASS" if all(x[1] for x in c) else "FAIL",
        "route": ra, "answer": a.get("answer"), "workflow_run_id": a.get("workflow_run_id")}

    v = {k: x["verdict"] for k, x in res["cases"].items()}
    res["summary"] = {"verdicts": v, "all_pass": all(y == "PASS" for y in v.values()),
                      "next_stage_allowed": all(y == "PASS" for y in v.values())}
    print(json.dumps(res["summary"], ensure_ascii=False, indent=2))
    for k, x in res["cases"].items():
        print("=" * 70)
        print(k, "->", x["verdict"])
        for ck in x["checks"]:
            print("   [%s] %s | observed=%s" % (ck["result"], ck["desc"],
                                                json.dumps(ck["observed"], ensure_ascii=False)[:150]))
    with io.open(os.path.join(HERE, "..", "evidence", "S2_ADJUDICATION_a2.json"), "w",
                 encoding="utf-8") as fh:
        fh.write(json.dumps(res, ensure_ascii=False, indent=2) + "\n")


if __name__ == "__main__":
    main()
