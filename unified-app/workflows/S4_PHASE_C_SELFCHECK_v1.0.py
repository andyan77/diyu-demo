#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Phase C 判定器判别力自检｜零模型调用、零 Dify 写入、不碰真实证据目录。

在任何一次真实调用之前回答一个问题：这个判定器能不能把假的判成 FAIL。
做法是用合成证据喂进判定函数：一份正控制应全 PASS；每个负控制只动一个变量，
必须精确翻掉对应那一条，且不牵连其它条。

真实证据目录不受影响——全部合成件写在临时目录，判定函数通过 S4PC_EV 指过去。
"""
import copy
import io
import importlib.util
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
TMP = tempfile.mkdtemp(prefix="s4pc_selfcheck_")
os.environ["S4PC_EV"] = TMP
os.environ["S4PC_OUT"] = os.path.join(TMP, "RESULT.json")

_s = importlib.util.spec_from_file_location(
    "pcadj", os.path.join(HERE, "S4_PHASE_C_ADJUDICATE_v1.0.py"))
A = importlib.util.module_from_spec(_s)
_s.loader.exec_module(A)

FZ = json.load(io.open(A.FREEZE, encoding="utf-8"))
GATE = json.load(io.open(A.GATE, encoding="utf-8"))
FIXTURE = io.open(A.FIXTURE, encoding="utf-8").read()

REG = "===== 用户本轮上传资料原文 =====\n序里集 XULI SELECT，2家直营门店。\n" \
      "===== 用户在对话中说出口、已登记的事实与偏好 =====\n- [PREFERENCE] 出镜用最懂搭配试穿的那位。"
FIELDS = {"primary_goal": "让熟客掌握一个衣橱适配的判断框架",
          "audience_problem": "这件跟我衣橱里已经有的搭不搭",
          "expected_change": "看完之后她能自己判断搭不搭",
          "content_promise": "用真实试穿示范回答搭不搭",
          "facts_registered": REG,
          "expression_subject": "苏禾",
          "expression_subject_and_boundary": "苏禾；不制造年龄焦虑",
          "expression_boundary": "不制造年龄焦虑"}


def envelope(fields, gaps):
    lines = ["provenance:", "  target_capability: X"]
    for k, v in fields.items():
        if v:
            lines.append("`%s`: %s" % (k, str(v).replace("\n", " ")))
    return "\n".join(lines)


def N(nid, inputs=None, outputs=None, status="succeeded"):
    return {"idx": 0, "node_id": nid, "type": "code", "status": status, "error": None,
            "inputs": json.dumps(inputs or {}, ensure_ascii=False),
            "outputs": json.dumps(outputs or {}, ensure_ascii=False)}


def turn(idx, tool, artifact, gaps, fields=None, answer="好的，这条内容的依据如下。",
         registered=REG, hop_reg=None, seam_cc=None, persist=None, last_len=None,
         extra_tools=(), boot=False, up_cap="", up_del=""):
    f = dict(fields or FIELDS)
    cc = envelope(f, gaps)
    gap_txt = "；".join(gaps) if gaps else "无"
    hop_reg = REG if hop_reg is None else hop_reg
    seam_cc = cc if seam_cc is None else seam_cc
    if persist is None:
        persist = "WRITE_NEW" if artifact else "KEEP_PREVIOUS"
    if last_len is None:
        last_len = len(artifact) if artifact else 0
    nodes = [
        N("uapp_ctx", {}, {"registered_facts": registered}),
        N("uapp_m3"), N("uapp_route"),
        N("uapp_hop", {"registered_facts": hop_reg, "target_capability": "X",
                       "upstream_capability": up_cap, "upstream_delivery": up_del},
          {"extracted_json": json.dumps(f, ensure_ascii=False),
           "source_map_json": "{}", "capability_call": cc,
           "extraction_gaps_text": gap_txt}),
        N("uapp_seam", {}, {"returns_json": json.dumps(
            {"precise_gap": gaps[0] if gaps else ""}, ensure_ascii=False)}),
        N("uapp_seam_merge", {}, {"artifact": {"output": artifact}}),
        N("uapp_delivery", {}, {"leak_hit_count": 0}),
        N("uapp_persist", {}, {"persist_action": persist}),
        N("uapp_save"),
    ]
    if boot:
        nodes.append(N("boot_ws"))
    seam_nodes = [{"node_id": t, "status": "succeeded"} for t in ([tool] + list(extra_tools))]
    seam_detail = [dict(N(t, {"capability_call": seam_cc}), node_id=t)
                   for t in ([tool] + list(extra_tools))]
    cap = {"tool_content_brief": "CONTENT_BRIEF", "tool_creative_script": "CREATIVE_SCRIPT",
           "tool_production_director": "PRODUCTION_DIRECTOR",
           "tool_publishing_packaging": "PUBLISHING_PACKAGING",
           "tool_matrix": "MATRIX", "tool_campaign": "CAMPAIGN"}
    nested = {k: {"app_id": "x", "runs_during_case": []} for k in
              ("M3", "HOP", "SEAM", "MATRIX", "CAMPAIGN", "CONTENT_BRIEF", "CREATIVE_SCRIPT",
               "PRODUCTION_DIRECTOR", "PUBLISHING_PACKAGING")}
    for t in [tool] + list(extra_tools):
        nested[cap[t]]["runs_during_case"] = [{"id": "r", "status": "succeeded"}]
    nested["SEAM"]["runs_during_case"] = [{"id": "s", "status": "succeeded"}]
    nested["SEAM"]["latest_run_nodes"] = seam_nodes
    nested["SEAM"]["latest_run_detail"] = seam_detail
    return {"case_id": "S4-PC-T%d" % idx, "turn_index": idx, "answer": answer,
            "window_start": "2026-08-30 00:00:00", "nodes_executed":
                [{"node_id": n["node_id"], "status": n["status"]} for n in nodes],
            "node_detail": nodes, "nested_app_runs": nested,
            "conversation_variables_after_turn": {"uapp_last_artifact": {"len": last_len}}}


def c1_doc(artifact="## 内容制作依据\n主目标：让熟客掌握判断框架。",
           skill="succeeded", status="succeeded", outcome="DELIVERED", delivery="给你的依据如下。"):
    return {"case_id": "S4-PC-C1", "http_status": 200, "attempts": 1,
            "response_body": {"data": {"status": status, "outputs": {
                "artifact": artifact, "user_delivery": delivery,
                "delivery_outcome": outcome, "artifact_status": "OK",
                "user_delivery_leaks": ""}}},
            "node_detail": [{"node_id": "skill_llm", "status": skill, "type": "llm",
                             "inputs": "{}", "outputs": "{}"}]}


def base_turns():
    t = {}
    t[1] = turn(1, "tool_content_brief", "", ["audience_problem"],
                answer="这一步我还差一样东西：这条给谁看？", boot=True, last_len=0)
    t[2] = turn(2, "tool_content_brief", "## 制作依据\n主目标：判断框架。" * 20, [],
                last_len=len("## 制作依据\n主目标：判断框架。" * 20))
    L2 = t[2]["conversation_variables_after_turn"]["uapp_last_artifact"]["len"]
    t[3] = turn(3, "tool_creative_script", "", ["content_origin_mode"],
                answer="还差一件事：这条素材从哪来？", persist="KEEP_PREVIOUS", last_len=L2)
    t[4] = turn(4, "tool_creative_script", "## 口播稿\n开场。" * 20, [], last_len=200,
                up_cap="CONTENT_BRIEF", up_del="上游交付")
    t[5] = turn(5, "tool_production_director", "## 拍摄方案\n机位。" * 20, [], last_len=200,
                up_cap="CREATIVE_SCRIPT", up_del="上游交付")
    t[6] = turn(6, "tool_publishing_packaging", "## 标题与封面\n标题。" * 20, [], last_len=200,
                up_cap="PRODUCTION_DIRECTOR", up_del="上游交付")
    return t


def lay(turns=None, c1=None):
    for f in os.listdir(TMP):
        os.remove(os.path.join(TMP, f))
    if c1 is not None:
        io.open(os.path.join(TMP, "S4-PC-C1.json"), "w", encoding="utf-8").write(
            json.dumps(c1, ensure_ascii=False))
    for i, d in (turns or {}).items():
        io.open(os.path.join(TMP, "S4-PC-T%d.json" % i), "w", encoding="utf-8").write(
            json.dumps(d, ensure_ascii=False))


RESULTS = []


def check(name, got, want):
    ok = got == want
    RESULTS.append((ok, name, got, want))
    print("  %s  %-52s got=%s want=%s" % ("PASS" if ok else "FAIL", name, got, want))


def verdicts(layer_res):
    return {c["id"]: c["result"] for c in layer_res.get("conditions") or []}


def main():
    print("=== C1 ===")
    lay(c1=c1_doc())
    r = A.judge_c1(FZ, GATE, FIXTURE)
    v = verdicts(r)
    print("   ", json.dumps(v, ensure_ascii=False))
    check("POS_C1_all_pass", r["verdict"], "PASS")

    for nm, kw, cid in (
            ("NEG_C1_skill_llm_not_run", {"skill": "failed"}, "P1-01"),
            ("NEG_C1_placeholder_artifact",
             {"artifact": A.PLACEHOLDER + "，还差一样东西。"}, "P1-04"),
            ("NEG_C1_input_insufficiency_outcome",
             {"outcome": "INPUT_SUFFICIENCY_STOP"}, "P1-04"),
            ("NEG_C1_fabricated_fabric",
             {"artifact": "面料为 95% 棉，亲肤透气。"}, "P1-05"),
            ("NEG_C1_fabricated_price",
             {"artifact": "这件西装售价 12345 元。"}, "P1-05"),
            ("NEG_C1_fabricated_person",
             {"artifact": "由店长赵婷出镜讲解。"}, "P1-05"),
            ("NEG_C1_leak", {"delivery": "target_capability 已就绪。"}, "P1-06")):
        lay(c1=c1_doc(**kw))
        vv = verdicts(A.judge_c1(FZ, GATE, FIXTURE))
        check(nm, vv.get(cid), "FAIL")
        others = [k for k, x in vv.items() if x == "FAIL" and k != cid]
        check(nm + "_no_collateral", others, [])

    print("=== C2 ===")
    T = base_turns()
    lay(turns={1: T[1], 2: T[2]})
    r2 = A.judge_c2(FZ, GATE, FIXTURE)
    print("   ", json.dumps(verdicts(r2), ensure_ascii=False))
    check("POS_C2_all_pass", r2["verdict"], "PASS")

    def negc2(name, mut, cid):
        t = copy.deepcopy(base_turns())
        mut(t)
        lay(turns={1: t[1], 2: t[2]})
        vv = verdicts(A.judge_c2(FZ, GATE, FIXTURE))
        check(name, vv.get(cid), "FAIL")

    negc2("NEG_C2_empty_T2_artifact",
          lambda t: t.__setitem__(2, turn(2, "tool_content_brief", "", [])), "P2-05")
    negc2("NEG_C2_shadow_capability",
          lambda t: t.__setitem__(2, turn(2, "tool_content_brief", "x" * 50, [],
                                          extra_tools=("tool_matrix",))), "P2-02")
    negc2("NEG_C2_hop_input_not_source",
          lambda t: t.__setitem__(2, turn(2, "tool_content_brief", "x" * 50, [],
                                          hop_reg="被改写过的事实")), "P2-03")
    negc2("NEG_C2_seam_carries_different_bytes",
          lambda t: t.__setitem__(2, turn(2, "tool_content_brief", "x" * 50, [],
                                          seam_cc="另一份外壳")), "P2-03")
    negc2("NEG_C2_facts_registered_is_a_gap",
          lambda t: t.__setitem__(2, turn(2, "tool_content_brief", "x" * 50,
                                          ["facts_registered"],
                                          fields=dict(FIELDS, facts_registered=""))), "P2-03")
    negc2("NEG_C2_primary_goal_rewritten_by_seam",
          lambda t: t.__setitem__(2, turn(2, "tool_content_brief", "x" * 50, [],
                                          seam_cc=envelope(dict(FIELDS,
                                                                primary_goal="换了个目标"),
                                                           []))), "P2-04")
    negc2("NEG_C2_fabrication_in_answer",
          lambda t: t.__setitem__(2, turn(2, "tool_content_brief", "x" * 50, [],
                                          answer="库存 42 件，售价 88888 元。")), "P2-08")
    negc2("NEG_C2_authorization_overclaim",
          lambda t: t.__setitem__(2, turn(2, "tool_content_brief", "x" * 50, [],
                                          answer="素材已获授权，可直接发布。")), "P2-08")
    negc2("NEG_C2_leak_in_answer",
          lambda t: t.__setitem__(2, turn(2, "tool_content_brief", "x" * 50, [],
                                          answer="route_mode 已确定。")), "P2-08")
    negc2("NEG_C2_m3_not_run",
          lambda t: t[2]["nodes_executed"].__setitem__(
              1, {"node_id": "uapp_m3", "status": "failed"}), "P2-01")

    print("=== C3 ===")
    lay(turns=base_turns())
    r3 = A.judge_c3(FZ, GATE, FIXTURE, live=False)
    v3 = verdicts(r3)
    print("   ", json.dumps(v3, ensure_ascii=False))
    check("POS_C3_all_pass_except_live_only",
          sorted(k for k, x in v3.items() if x != "PASS"), ["P3-11", "P3-12"])

    def negc3(name, mut, cid):
        t = copy.deepcopy(base_turns())
        mut(t)
        lay(turns=t)
        vv = verdicts(A.judge_c3(FZ, GATE, FIXTURE, live=False))
        check(name, vv.get(cid), "FAIL")

    negc3("NEG_C3_content_brief_rerun",
          lambda t: t.__setitem__(4, turn(4, "tool_creative_script", "x" * 50, [],
                                          extra_tools=("tool_content_brief",),
                                          up_cap="CONTENT_BRIEF", up_del="d")), "P3-02")
    negc3("NEG_C3_task_identity_lost",
          lambda t: t.__setitem__(4, turn(4, "tool_creative_script", "x" * 50, [],
                                          fields=dict(FIELDS, primary_goal="另起一个新目标"),
                                          up_cap="CONTENT_BRIEF", up_del="d")), "P3-03")
    negc3("NEG_C3_content_promise_drift",
          lambda t: t.__setitem__(5, turn(5, "tool_production_director", "x" * 50, [],
                                          fields=dict(FIELDS, content_promise="换了个承诺"),
                                          up_cap="CREATIVE_SCRIPT", up_del="d")), "P3-04")
    negc3("NEG_C3_extra_gap_at_T3",
          lambda t: t.__setitem__(3, turn(3, "tool_creative_script", "",
                                          ["content_origin_mode", "无关缺口"])), "P3-05")
    negc3("NEG_C3_gap_persists_after_T4",
          lambda t: t.__setitem__(4, turn(4, "tool_creative_script", "",
                                          ["content_origin_mode"],
                                          up_cap="CONTENT_BRIEF", up_del="d")), "P3-05")
    negc3("NEG_C3_pd_artifact_empty",
          lambda t: t.__setitem__(5, turn(5, "tool_production_director", "", [],
                                          up_cap="CREATIVE_SCRIPT", up_del="d")), "P3-06")
    negc3("NEG_C3_upstream_delivery_empty",
          lambda t: t.__setitem__(6, turn(6, "tool_publishing_packaging", "x" * 50, [],
                                          up_cap="PRODUCTION_DIRECTOR", up_del="")), "P3-06")
    negc3("NEG_C3_empty_artifact_overwrites_previous",
          lambda t: t.__setitem__(5, turn(5, "tool_production_director", "", [],
                                          persist="WRITE_NEW", last_len=0,
                                          up_cap="CREATIVE_SCRIPT", up_del="d")), "P3-07")
    negc3("NEG_C3_shadow_run",
          lambda t: t.__setitem__(6, turn(6, "tool_publishing_packaging", "x" * 50, [],
                                          extra_tools=("tool_campaign",),
                                          up_cap="PRODUCTION_DIRECTOR", up_del="d")), "P3-08")
    negc3("NEG_C3_authorization_overclaim",
          lambda t: t.__setitem__(6, turn(6, "tool_publishing_packaging", "x" * 50, [],
                                          answer="这批素材已获授权。",
                                          up_cap="PRODUCTION_DIRECTOR", up_del="d")), "P3-09")
    negc3("NEG_C3_leak",
          lambda t: t.__setitem__(6, turn(6, "tool_publishing_packaging", "x" * 50, [],
                                          answer="precise_gap 为空。",
                                          up_cap="PRODUCTION_DIRECTOR", up_del="d")), "P3-10")
    negc3("NEG_C3_fabricated_fact",
          lambda t: t.__setitem__(5, turn(5, "tool_production_director",
                                          "准备 3 件样衣，货号 XL-2026-A。", [],
                                          up_cap="CREATIVE_SCRIPT", up_del="d")), "P3-13")

    print("=== 结束 ===")
    bad = [r for r in RESULTS if not r[0]]
    print("自检 %d/%d 通过" % (len(RESULTS) - len(bad), len(RESULTS)))
    shutil.rmtree(TMP, ignore_errors=True)
    if bad:
        for r in bad:
            print("  失败：%s got=%s want=%s" % (r[1], r[2], r[3]))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
