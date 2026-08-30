#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Phase C 判定器 v1.1 判别力自检｜零模型调用、零 Dify 写入、不改动任何真实证据。

必须在继续 C2/C3 之前跑完，且四类控制缺一不可（本轮 Prompt 对 Checker 后继版本的要求）：

  1. 合成正控制   —— v1.0 全套 + 新增：产物包含夹具自身的全部多字职务名，必须零命中
  2. 单点负控制   —— v1.0 全套 + 新增：两个方向的编造人名都必须精确翻 FAIL
  3. 历史失败回放 —— v1.0 在真实 S4-PC-C1 产物上误报的四条，在 v1.1 下必须消失
  4. 反过拟合对照 —— 同一份真实产物注入一个编造人名后必须仍然 FAIL
                     （证明 v1.1 不是"对这份文档一律放行"）
"""
import copy
import importlib.util
import io
import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def load(name, fn):
    s = importlib.util.spec_from_file_location(name, os.path.join(HERE, fn))
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m


SC = load("sc10", "S4_PHASE_C_SELFCHECK_v1.0.py")   # 复用合成件工厂与 v1.0 全套控制
ADJ11 = load("adj11", "S4_PHASE_C_ADJUDICATE_v1.1.py")

A = SC.A                                            # 自检里被判定的那一个模块实例
FZ11 = json.load(io.open(ADJ11.FREEZE, encoding="utf-8"))
GATE = json.load(io.open(A.GATE, encoding="utf-8"))
FIXTURE = io.open(A.FIXTURE, encoding="utf-8").read()
REAL_EV = os.path.join(A.UAPP, "evidence", "stages", "s4_phase_c")

# 把 FB-07 换成 v1.1，其余探针与全部判据保持 v1.0 原样
_orig_fab = A.fabrication_hits
_fb07 = ADJ11.make_fb07(FZ11, FIXTURE)


def _patched(text, probes, fixture):
    return [h for h in _orig_fab(text, probes, fixture)
            if h["probe"] != "FB-07"] + _fb07(text)


A.fabrication_hits = _patched

R = []


def check(name, got, want):
    ok = got == want
    R.append((ok, name, got, want))
    print("  %s  %-56s got=%s want=%s" % ("PASS" if ok else "FAIL", name, got, want))


def vd(layer):
    return {c["id"]: c["result"] for c in layer.get("conditions") or []}


ROLE_SENTENCE = ("出镜的是零售搭配负责人，事实由商品负责人确认；旗舰店店长与门店导购团队"
                 "提供试穿反馈，导购团队不额外出镜。创始人不参与本条。")


def main():
    print("=== 1/4 合成正控制（含 v1.0 全套 + 夹具职务名）===")
    SC.lay(c1=SC.c1_doc())
    check("POS_C1_v11_baseline", A.judge_c1(FZ11, GATE, FIXTURE)["verdict"], "PASS")

    SC.lay(c1=SC.c1_doc(artifact="## 制作依据\n" + ROLE_SENTENCE))
    v = vd(A.judge_c1(FZ11, GATE, FIXTURE))
    check("POS_C1_v11_fixture_role_titles_no_hit", v.get("P1-05"), "PASS")

    SC.lay(turns={1: SC.base_turns()[1], 2: SC.base_turns()[2]})
    check("POS_C2_v11_baseline", A.judge_c2(FZ11, GATE, FIXTURE)["verdict"], "PASS")
    t = copy.deepcopy(SC.base_turns())
    t[2] = SC.turn(2, "tool_content_brief", "x" * 50, [], answer=ROLE_SENTENCE)
    SC.lay(turns={1: t[1], 2: t[2]})
    check("POS_C2_v11_role_titles_in_answer", vd(A.judge_c2(FZ11, GATE, FIXTURE)).get("P2-08"),
          "PASS")

    SC.lay(turns=SC.base_turns())
    v3 = vd(A.judge_c3(FZ11, GATE, FIXTURE, live=False))
    check("POS_C3_v11_baseline", sorted(k for k, x in v3.items() if x != "PASS"),
          ["P3-11", "P3-12"])

    print("=== 2/4 单点负控制（含 v1.0 全套 + 两个方向的编造人名）===")
    for nm, art, cid in (
            ("NEG_v11_name_after_role", "由店长赵婷出镜讲解这条内容。", "P1-05"),
            ("NEG_v11_name_before_role", "赵婷（零售搭配负责人）负责本条试穿。", "P1-05"),
            ("NEG_v11_three_char_name", "创始人欧阳明在片中出镜。", "P1-05"),
            ("NEG_v11_name_with_paren", "本条由 李小曼（商品负责人）确认商品事实。", "P1-05")):
        SC.lay(c1=SC.c1_doc(artifact=art))
        vv = vd(A.judge_c1(FZ11, GATE, FIXTURE))
        check(nm, vv.get(cid), "FAIL")
        check(nm + "_no_collateral", [k for k, x in vv.items() if x == "FAIL" and k != cid], [])

    for nm, kw, cid in (
            ("NEG_v11_skill_llm_not_run", {"skill": "failed"}, "P1-01"),
            ("NEG_v11_placeholder", {"artifact": A.PLACEHOLDER + "，还差一样。"}, "P1-04"),
            ("NEG_v11_fabric_pct", {"artifact": "面料为 95% 棉。"}, "P1-05"),
            ("NEG_v11_price", {"artifact": "这件西装售价 12345 元。"}, "P1-05"),
            ("NEG_v11_leak", {"delivery": "target_capability 已就绪。"}, "P1-06")):
        SC.lay(c1=SC.c1_doc(**kw))
        check(nm, vd(A.judge_c1(FZ11, GATE, FIXTURE)).get(cid), "FAIL")

    def negc2(name, mut, cid):
        tt = copy.deepcopy(SC.base_turns())
        mut(tt)
        SC.lay(turns={1: tt[1], 2: tt[2]})
        check(name, vd(A.judge_c2(FZ11, GATE, FIXTURE)).get(cid), "FAIL")

    negc2("NEG_v11_C2_empty_artifact",
          lambda x: x.__setitem__(2, SC.turn(2, "tool_content_brief", "", [])), "P2-05")
    negc2("NEG_v11_C2_shadow",
          lambda x: x.__setitem__(2, SC.turn(2, "tool_content_brief", "x" * 50, [],
                                             extra_tools=("tool_matrix",))), "P2-02")
    negc2("NEG_v11_C2_facts_erased",
          lambda x: x.__setitem__(2, SC.turn(2, "tool_content_brief", "x" * 50,
                                             ["facts_registered"],
                                             fields=dict(SC.FIELDS, facts_registered=""))), "P2-03")
    negc2("NEG_v11_C2_fabricated_person_in_answer",
          lambda x: x.__setitem__(2, SC.turn(2, "tool_content_brief", "x" * 50, [],
                                             answer="由店长赵婷出镜。")), "P2-08")

    def negc3(name, mut, cid):
        tt = copy.deepcopy(SC.base_turns())
        mut(tt)
        SC.lay(turns=tt)
        check(name, vd(A.judge_c3(FZ11, GATE, FIXTURE, live=False)).get(cid), "FAIL")

    negc3("NEG_v11_C3_cb_rerun",
          lambda x: x.__setitem__(4, SC.turn(4, "tool_creative_script", "x" * 50, [],
                                             extra_tools=("tool_content_brief",),
                                             up_cap="CONTENT_BRIEF", up_del="d")), "P3-02")
    negc3("NEG_v11_C3_empty_overwrites",
          lambda x: x.__setitem__(5, SC.turn(5, "tool_production_director", "", [],
                                             persist="WRITE_NEW", last_len=0,
                                             up_cap="CREATIVE_SCRIPT", up_del="d")), "P3-07")
    negc3("NEG_v11_C3_fabricated_person",
          lambda x: x.__setitem__(5, SC.turn(5, "tool_production_director",
                                             "出镜由店长赵婷负责。", [],
                                             up_cap="CREATIVE_SCRIPT", up_del="d")), "P3-13")

    print("=== 3/4 历史失败证据回放（真实 S4-PC-C1，零模型调用）===")
    real = json.load(io.open(os.path.join(REAL_EV, "S4-PC-C1.json"), encoding="utf-8"))
    outs = real["response_body"]["data"]["outputs"]
    body = str(outs["artifact"]) + "\n" + str(outs["user_delivery"])
    old = [h for h in _orig_fab(body, FZ11["fabrication_probes"], FIXTURE) if h["probe"] == "FB-07"]
    new = _fb07(body)
    check("REPLAY_v10_reproduced_4_false_positives", len(old), 4)
    check("REPLAY_v11_false_positives_gone", [h["candidate"] for h in new], [])

    saved_ev = A.EV
    A.EV = REAL_EV
    real_c1 = A.judge_c1(FZ11, GATE, FIXTURE)
    A.EV = saved_ev
    check("REPLAY_v11_real_C1_P1-05", vd(real_c1).get("P1-05"), "PASS")
    check("REPLAY_v11_real_C1_other_conditions_unchanged",
          {k: x for k, x in vd(real_c1).items() if k != "P1-05"},
          {"P1-01": "PASS", "P1-02": "PASS", "P1-03": "PASS", "P1-04": "PASS", "P1-06": "PASS"})

    print("=== 4/4 反过拟合对照（同一份真实产物注入编造人名）===")
    for nm, inject in (("ANTIOVERFIT_role_first", "\n本条由店长赵婷出镜讲解。"),
                       ("ANTIOVERFIT_name_first", "\n李小曼（商品负责人）确认商品事实。")):
        poisoned = copy.deepcopy(real)
        poisoned["response_body"]["data"]["outputs"]["artifact"] += inject
        SC.lay(c1=poisoned)
        check(nm, vd(A.judge_c1(FZ11, GATE, FIXTURE)).get("P1-05"), "FAIL")

    print("=== 结束 ===")
    bad = [x for x in R if not x[0]]
    print("v1.1 自检 %d/%d 通过" % (len(R) - len(bad), len(R)))
    shutil.rmtree(SC.TMP, ignore_errors=True)
    for x in bad:
        print("  失败：%s got=%s want=%s" % (x[1], x[2], x[3]))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
