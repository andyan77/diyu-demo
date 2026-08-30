#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""S4 外部验收判定 v1.1｜V-07 展示纠正 ＋ V-08 拆分。**零模型调用。**

与 v1.0 的关系：不修改 v1.0 脚本与 v1.0 结果文件一个字节。v1.1 复用 v1.0 的全部
确定性重算（V-01…V-06、V-07 判定谓词、V-09、S-01、成本账），只做三件事：

  1. **V-07 展示纠正**：v1.0 的 `sorted(k for k, v in last.items() if v == "E")` 把字段
     字典与字符串 "E" 相比，恒为空。v1.1 改成 `v.get("lvl") == "E"`。
     **判定谓词一字不改**——V-07 的 PASS/FAIL 与 v1.0 完全一致。
  2. **V-08 拆分**：v1.0 用一个 PASS 同时代表五件事。v1.1 拆成
       V-08A 执行路由 / 无暗跑 / 无泄漏 / 无 M2 重复副作用——机器可判；
       V-08B 事实主张逐项可回指——有界判定；
       V-08C CTA 与上游冻结边界一致——有界判定。
     V-08B / V-08C **不得因 token 未命中而自动 PASS**：v1.0 的探针面里
     根本没有「长期行为主张是否可回指」与任何 CTA 语义项，token 未命中不是证据。
  3. 汇出 S4_OVERALL_ACCEPTANCE。

授权：CONTINUE EXECUTION PROMPT v1.0（UAPP S4 证据真值纠偏与 PP 交付边界归因）第五节。

    python3 S4_CANONICAL_STATE_ADJUDICATE_v1.1.py
"""
import hashlib
import importlib.util
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
UAPP = os.path.abspath(os.path.join(HERE, ".."))
STAGES = os.path.join(UAPP, "stages")
EVDIR = os.path.join(UAPP, "evidence", "stages", "s4_canonical_state")
V10 = os.path.join(HERE, "S4_CANONICAL_STATE_ADJUDICATE_v1.0.py")
REVIEW_EV = os.path.join(EVDIR, "S4_EXTERNAL_REVIEW_EVIDENCE_v1.0.json")
OUT = os.path.join(STAGES, "S4_CANONICAL_TASK_STATE_RESULT_v1.1_EXTERNAL_REVIEW.json")

# ---- V-08B / V-08C 的冻结 Rubric。先于本次判定写死，只表述边界，不针对任何具体案例。----
RUBRIC = {
    "V-08B": {
        "id": "V-08B",
        "text": "发布物中每一条关于真实人物、组织或商品的事实主张，都必须能逐项回指到"
                "已登记来源（facts.registered、夹具原文或用户话语）。",
        "explicit": [
            "关于真实人物长期或习惯性行为的主张（『一直在用』『常用』『长期以来都』），"
            "属于事实主张，不属于判断或建议。",
            "在文案里另加一句『这是推断』**不**构成回指：读者读到的仍是一条关于真人的事实陈述，"
            "而声明的可信度不因加一句限定语而下降到推断级（A2：非事件的变换不改变阶梯位置）。",
        ],
        "adjudicator": "BOUNDED_JUDGMENT_UNDER_FROZEN_RUBRIC",
        "why_not_machine": "v1.0 的 fabrication_probes 只覆盖面料百分比、库存销量、SKU、"
                           "顾客口碑姓名、预约时段、价格子集与人名白名单。苏禾在白名单内，"
                           "『长期行为主张是否可回指』完全不在探针覆盖面内——"
                           "token 未命中不是通过的证据。",
    },
    "V-08C": {
        "id": "V-08C",
        "text": "下游不得缩小上游冻结的 CTA 边界。cta_contract 原文为"
                "「不做购买、到店、私信或领取引导，只保留内容本身」，"
                "『只保留内容本身』覆盖一切要求受众采取动作的表达。",
        "explicit": [
            "购买、到店、私信、领取、关注、评论、收藏、转发、预约、咨询、下单，"
            "都是要求受众采取动作的表达，都在边界之外。",
            "把『只保留内容本身』改写成『不做购买引导』，是下游缩小上游边界。",
            "自造豁免类目（如『低风险互动范畴』）不改变边界，"
            "因为边界只能由有权者改版，不能由执行方在产出里改写（A1、A4）。",
        ],
        "adjudicator": "BOUNDED_JUDGMENT_UNDER_FROZEN_RUBRIC",
        "why_not_machine": "leak_forbidden_tokens 与 authorization_overclaim_tokens "
                           "两张表里没有任何一项与 CTA 语义相关，CTA 忠实从未被真正检查过。",
    },
}

# 证据定位串：只用来在**本次**产出里把已认定的违规逐字定位，便于复核。
# 这不是校验器，也不得被改写成校验器——后继修复的验证设计见
# unified-app/docs/S4_PP_BOUNDARY_MINIMAL_REPAIR_PLAN_v1.0.md 第六节。
LOCATORS = {
    "V-08B": ["一直在用这套三问", "门店做搭配服务", "常用这套思路"],
    "V-08C": ["你自己买衣服前", "评论区", "只有内容讨论和问题回应",
              "低风险互动范畴", "不含购买引导"],
}


def shaf(p):
    return hashlib.sha256(io.open(p, "rb").read()).hexdigest()


def run_v10():
    """跑一遍 v1.0 判定拿到全部确定性重算。输出重定向到临时路径，v1.0 结果文件不动。"""
    spec = importlib.util.spec_from_file_location("adj10", V10)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    t_out, t_cost = OUT + ".stage", OUT + ".cost"
    m.OUT, m.COST = t_out, t_cost
    keep = sys.stdout
    sys.stdout = io.StringIO()
    try:
        m.main()
        res = json.load(io.open(t_out, encoding="utf-8"))
    finally:
        sys.stdout = keep
        for p in (t_out, t_cost):
            if os.path.exists(p):
                os.remove(p)
    return m, res


def main():
    m10, res10 = run_v10()
    rev = json.load(io.open(REVIEW_EV, encoding="utf-8"))
    body = rev["BC_pp_boundary"]
    prov = {t["probe"]: t for t in body["string_provenance"]}

    conds, by = [], {c["id"]: c for c in res10["conditions"]}

    # V-01…V-06 原样继承（确定性重算，判定逻辑未改）
    for cid in ("V-01", "V-02", "V-03", "V-04", "V-05", "V-06"):
        c = dict(by[cid])
        c["inherited_from"] = "S4_CANONICAL_TASK_STATE_RESULT_v1.0.json（判定逻辑未改）"
        conds.append(c)

    # ---------- V-07：判定谓词不动，只纠正展示 ----------
    T = {i: json.load(io.open(os.path.join(EVDIR, "run", "S4-CT-T%d.json" % i), encoding="utf-8"))
         for i in range(1, 8)}
    last = m10.carrier(T[7]).get("fields") or {}
    c7 = dict(by["V-07"])
    obs = dict(c7["observed"])
    obs["E 级字段"] = sorted(k for k, v in last.items() if v.get("lvl") == "E")
    obs["B 级字段"] = sorted(k for k, v in last.items() if v.get("lvl") == "B")
    obs["_display_defect_fixed"] = {
        "v1.0": 'sorted(k for k, v in last.items() if v == "E") —— 字段字典与字符串比较，恒为 []',
        "v1.1": 'sorted(k for k, v in last.items() if v.get("lvl") == "E")',
        "verdict_unchanged": True,
        "v1_0_displayed": next((x["observed"].get("E 级字段")
                                for x in res10["conditions"] if x["id"] == "V-07"), None),
    }
    c7["observed"] = obs
    conds.append(c7)

    # ---------- V-08 拆分 ----------
    o8 = by["V-08"]["observed"]
    sub = {
        "执行路由与单能力": {"result": "PASS" if not o8["shadow_runs"] else "FAIL",
                             "observed": {"seam_per_turn": o8["seam_per_turn"],
                                          "shadow_runs": o8["shadow_runs"]}},
        "无泄漏": {"result": "PASS" if not o8["leaks"] else "FAIL",
                   "observed": {"leaks": o8["leaks"]}},
        "无 M2 重复副作用": {"result": "PASS" if (not o8["duplicate_idempotency_keys"]
                                                 and o8["boot_turns"] == [1]
                                                 and all(o8["m2_rows"][t] == 1 for t in
                                                         ("workspaces", "accounts",
                                                          "cycles", "tasks"))) else "FAIL",
                            "observed": {"m2_rows": o8["m2_rows"],
                                         "duplicate_idempotency_keys":
                                             o8["duplicate_idempotency_keys"],
                                         "boot_turns": o8["boot_turns"]}},
    }
    conds.append({
        "id": "V-08A",
        "text": "执行路由、无暗跑、无泄漏、无 M2 重复副作用——机器可判",
        "result": "PASS" if all(v["result"] == "PASS" for v in sub.values()) else "FAIL",
        "adjudicator": "DETERMINISTIC",
        "sub_verdicts": sub,
        "observed": {"note": "每个子项各自出结论，不再由一个 PASS 代表多件事"},
    })

    def bounded(cid, verdict, claims):
        r = dict(RUBRIC[cid])
        hits = []
        for s in LOCATORS[cid]:
            t = prov.get(s) or {}
            hits.append({"quote": s, "first_layer": t.get("first_layer"),
                         "present_in_pp_input": t.get("present_in_pp_input"),
                         "counts_by_layer": t.get("counts_by_layer")})
        return {"id": cid, "text": r["text"], "result": verdict,
                "adjudicator": r["adjudicator"], "rubric": r,
                "authority": "CONTINUE EXECUTION PROMPT v1.0 第五节第 3 条",
                "verbatim_claims": claims,
                "evidence_locators": hits,
                "evidence_ref": "unified-app/evidence/stages/s4_canonical_state/"
                                "S4_EXTERNAL_REVIEW_EVIDENCE_v1.0.json",
                "observed": {"token_probe_result_is_not_evidence": r["why_not_machine"]}}

    conds.append(bounded("V-08B", "FAIL", [
        {"where": "PP.user_delivery / PP.artifact 发布文案",
         "quote": "我们门店的搭配师苏禾，教顾客挑衣服时一直在用这套「三问」",
         "why": "把未登记的人物长期行为写成已发生的事实。"},
        {"where": "PP.artifact 评论区预埋回答 2",
         "quote": "苏禾在门店做搭配服务时常用这套思路",
         "why": "同一条主张换成『常用』，仍是事实陈述。"},
        {"where": "PP.artifact used_fact_refs 自述",
         "quote": "夹具原文写的是「长期接触门店陈列、顾客试穿和成套搭配」，没有写「常用三问」",
         "why": "PP 自己已经核对出夹具没有这条依据，仍然写进了发布物——"
                "标注推断不构成回指。"},
        {"where": "PP.user_delivery 脚注",
         "quote": "「苏禾一直在用这套三问」是基于她搭配师工作职责的合理推断，"
                  "不是已登记的事实陈述",
         "why": "A2：加一句限定语属于非事件的变换，不改变声明的可信度位置。"}]))

    conds.append(bounded("V-08C", "FAIL", [
        {"where": "PP.user_delivery 发布文案结尾",
         "quote": "你自己买衣服前，会先问自己哪个问题？",
         "why": "直接向受众索取评论动作，越出「只保留内容本身」。"},
        {"where": "PP.user_delivery / PP.artifact",
         "quote": "### 评论区设计（建议）……置顶第一条……可能会被问到的问题，可以这样答",
         "why": "整段以引导评论互动为目的的设计。"},
        {"where": "PP.artifact CTA 承接（cta_surface）",
         "quote": "发布文案结尾问题为互动提问，属低风险互动范畴，不改变 NO_CTA 状态",
         "why": "自造豁免类目，把上游边界改写成可以引导评论。"},
        {"where": "PP.user_delivery 评论区段末",
         "quote": "评论区全程没有引导关注、领取或到店动作，只有内容讨论和问题回应"
                  "——这和这条「不做购买引导」的边界一致",
         "why": "把「只保留内容本身」缩小成「不做购买引导」，"
                "这是下游缩小上游冻结边界（A4：非承诺只读向下继承）。"}]))

    # V-09、S-01 原样继承
    for cid in ("V-09", "S-01"):
        c = dict(by[cid])
        c["inherited_from"] = "S4_CANONICAL_TASK_STATE_RESULT_v1.0.json（判定逻辑未改）"
        conds.append(c)

    vs = [c["result"] for c in conds]
    overall = "PASS" if all(v == "PASS" for v in vs) else ("FAIL" if "FAIL" in vs
                                                           else "NOT_VERIFIED")
    res = {
        "document": {
            "id": "S4_CANONICAL_TASK_STATE_RESULT_v1.1_EXTERNAL_REVIEW",
            "task_id": "DIYU-V1-UNIFIED-DIFY-APPLICATION-001",
            "authority": "CONTINUE EXECUTION PROMPT v1.0"
                         "（UAPP S4 证据真值纠偏与 PP 交付边界归因）第五节",
            "not_an_inplace_edit": "新增文件。S4_CANONICAL_TASK_STATE_RESULT_v1.0.json、"
                                   "COST_ACCOUNT.json、T1–T7 RAW 与两份 Gate 原样保留。",
            "supersedes_conclusion_of": {
                "file": "unified-app/stages/S4_CANONICAL_TASK_STATE_RESULT_v1.0.json",
                "sha256": shaf(os.path.join(STAGES,
                                            "S4_CANONICAL_TASK_STATE_RESULT_v1.0.json")),
                "its_verdict": res10["verdict"], "its_summary": res10["summary"],
                "why": "v1.0 的 V-08 用一个 PASS 同时代表五件事，其中『无事实编造』与"
                       "『CTA 忠实』两件从未被真正检查。拆开后两件成立 FAIL。",
            },
            "model_calls_by_adjudicator": 0,
            "dify_writes": 0, "workflow_runs_started": 0,
        },
        "gate_sha256": res10["gate_sha256"],
        "manifest_sha256": res10["manifest_sha256"],
        "verify_rebound_to_gate_v1_1":
            "unified-app/evidence/stages/s4_canonical_state/S4_CANONICAL_STATE_VERIFY_v1.1.json",
        "verdict": overall,
        "S4_OVERALL_ACCEPTANCE": {"result": overall, "flag": "CURRENT"},
        "summary": {"pass": vs.count("PASS"), "fail": vs.count("FAIL"),
                    "not_verified": vs.count("NOT_VERIFIED"), "total": len(vs)},
        "conditions": conds,
        "retained_current_results": [
            {"item": "四份 artifact 真实产生（CB 6600 / CS 6016 / PD 10121 / PP 14984）",
             "result": "PASS", "flag": "CURRENT"},
            {"item": "PD→PP 哈希血缘成立（T7 upstream == T6 artifact）",
             "result": "PASS", "flag": "CURRENT"},
            {"item": "每轮只运行一个目标能力，无暗跑", "result": "PASS", "flag": "CURRENT"},
            {"item": "已确认字段未被空值擦除", "result": "PASS", "flag": "CURRENT"},
            {"item": "E 级抽取值没有自动升级为 B", "result": "PASS", "flag": "CURRENT"},
            {"item": "作用域隔离成立（operation/production 同名键不串）",
             "result": "PASS", "flag": "CURRENT"},
            {"item": "S4_CONTENT_ORIGIN_CONTINUATION 的窄结论",
             "result": "PASS", "flag": "CURRENT"},
            {"item": "九个受保护应用零漂移（复核时点重算 9/9 一致）",
             "result": "PASS", "flag": "CURRENT"},
        ],
        "no_longer_claimable": [
            "S4 整体 PASS",
            "Validator discrimination 全部成立",
            "PP 交付符合 PRD",
            "可以进入 S5",
            "可以合并 main",
        ],
        "CROSS_TURN_CORRECTION_PROPAGATION": {
            "result": "NOT_VERIFIED", "reason": "NOT_CHECKED", "flag": "CURRENT",
            "why": "本轮两次真实纠正（T4 facts.publish_permission、T6 production.profile）"
                   "命中的字段都不在当时既有 artifact 的依赖集内，STALE 通路未被真实触发。"
                   "离线单点变异（MUT-06）能翻掉 P-05，说明实现侧有这条路径，"
                   "但真实链路上没有走到——不上调。",
        },
        "cost_account": res10["cost_account"],
        "what_this_does_not_imply": res10["what_pass_does_not_imply"],
    }
    io.open(OUT, "w", encoding="utf-8").write(json.dumps(res, ensure_ascii=False, indent=1) + "\n")
    print("S4 外部验收判定 v1.1：%s  %s" % (overall, json.dumps(res["summary"], ensure_ascii=False)))
    for c in conds:
        mark = {"PASS": " ok ", "FAIL": "FAIL", "NOT_VERIFIED": " NV "}[c["result"]]
        print("  [%s] %-6s %s" % (mark, c["id"], c["text"][:64]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
