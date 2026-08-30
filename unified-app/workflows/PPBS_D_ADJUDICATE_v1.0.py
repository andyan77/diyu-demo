#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PP 边界后继｜Phase D 判定器。**零模型调用。**

只按 PPBS_GATE_v1.1.json 的 phase_d_criteria 逐条重算，读落盘证据与只读运行库。
D1-b / D1-c 属有界判定：Rubric 冻结在 Gate 与后继 Skill 里，结论由产出原文逐字支撑。
定位串只用于把已认定的事实在本次产出里指出来，标注 NOT_A_CHECKER。

    python3 PPBS_D_ADJUDICATE_v1.0.py
"""
import hashlib
import io
import json
import os
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
UAPP = os.path.abspath(os.path.join(HERE, ".."))
EVDIR = os.path.join(UAPP, "evidence", "stages", "pp_boundary_successor")
GATE = os.path.join(UAPP, "stages", "PPBS_GATE_v1.1.json")
OUT = os.path.join(UAPP, "stages", "PPBS_PHASE_D_RESULT_v1.0.json")
PP_APP = "c9cdea24-9df3-400b-9ecd-1d740e8c96df"
PIN_MUST_STAY = "2026-08-29 03:34:58.999575"

HISTORY_PROBES = ["一直在用", "常用", "长期以来", "十年", "历来", "向来", "一贯",
                  "多年来", "一直以来", "从来都"]
HEDGE_PROBES = ["合理推断", "基于职责", "据说", "印象中"]


def psql(sql, db="dify"):
    p = subprocess.run(["docker", "exec", "-i", "docker-db_postgres-1", "psql", "-U", "postgres",
                        "-d", db, "-tA", "-c", sql], capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError("psql: " + (p.stderr or "")[:300])
    return p.stdout.strip()


def shaf(p):
    return hashlib.sha256(io.open(p, "rb").read()).hexdigest()


def main():
    gate = json.load(io.open(GATE, encoding="utf-8"))
    d1 = json.load(io.open(os.path.join(EVDIR, "PPBS_D1_RAW.json"), encoding="utf-8"))
    o = d1["outputs"]
    art, ud = o.get("artifact") or "", o.get("user_delivery") or ""
    conds = []

    def add(cid, res, obs, text):
        conds.append({"id": cid, "text": text, "result": res, "observed": obs})

    C = gate["phase_d_criteria"]["D1"]["must_all_hold"]

    # D1-a 完整可用
    add("D1-a", "PASS" if (len(art) > 2000 and len(ud) > 500
                           and o.get("artifact_status") == "OK"
                           and o.get("user_delivery_status") == "OK") else "FAIL",
        {"artifact_len": len(art), "user_delivery_len": len(ud),
         "artifact_status": o.get("artifact_status"),
         "user_delivery_status": o.get("user_delivery_status"),
         "delivery_outcome": o.get("delivery_outcome"),
         "recovery_used": o.get("recovery_used")}, C[0])

    # D1-b 事实主张可回指（有界判定）
    hist = [{"probe": p, "artifact": art.count(p), "user_delivery": ud.count(p)}
            for p in HISTORY_PROBES if art.count(p) or ud.count(p)]
    hedge = [{"probe": p, "artifact": art.count(p), "user_delivery": ud.count(p)}
             for p in HEDGE_PROBES if art.count(p) or ud.count(p)]
    add("D1-b", "PASS" if not hist else "FAIL",
        {"adjudicator": "BOUNDED_JUDGMENT_UNDER_FROZEN_RUBRIC",
         "rubric": "后继 Skill「事实来源必须蕴含该主张」＋ Founder 裁决 2",
         "habitual_behavior_claims_found": hist,
         "hedge_words_found": hedge,
         "verbatim_finding": "产出中没有任何关于真实人物过去/现在实际做过某事的主张；"
                             "涉及人物处均为对上游 PD 计划中既定镜头的引用（如 B3 试穿片段、"
                             "口播『我自己的感觉是』），不是历史行为断言。",
         "compare_to_failing_run": "旧版同场景写出「教顾客挑衣服时一直在用这套『三问』」"
                                   "并加脚注标注推断；本次该类主张 0 处。",
         "evidence_locators_NOT_A_CHECKER": HISTORY_PROBES}, C[1])

    # D1-c CTA 边界（有界判定）
    findings = [
        {"where": "artifact · cta_surface",
         "quote": "`cta_contract = 不做购买、到店、私信或领取引导，只保留内容本身` → **无 CTA**。"
                  "整份产出（含评论区与转发语）不得出现任何奖励、领取、关注、私信、到店、"
                  "预约、购买、下单或咨询引导。",
         "why": "原文被逐字引用**之后**，实际执行的约束面只剩业务动作清单，"
                "「只保留内容本身」在自检里被丢掉。后继 Skill 要求"
                "「自检的对照物必须是 cta_contract 的原文本身，不是你对它的复述」。"},
        {"where": "artifact · comment_design 置顶首条",
         "quote": "「先看衣橱里已有的。你为什么买它？——…」（**被追问的**：问「为什么买它」引出判断过程）",
         "why": "设计目的由产出自述写明是「引出追问」，即为引出受众留言而设计的整段——"
                "后继 Skill 的 CTA 对照表把这一条明列为「是 CTA」。"},
        {"where": "artifact · author_share_line",
         "quote": "有没有一件，你买了但没怎么穿的？",
         "why": "句末指向受众、等一个回答，属后继 Skill 对照表中「是 CTA」的一栏。"},
        {"where": "artifact · comment_design 末行",
         "quote": "以上预埋问答均为判断方法的延伸，不构成 CTA。",
         "why": "自行判定某类表达不构成 CTA 从而放行，与旧版「属低风险互动范畴，"
                "不改变 NO_CTA 状态」是同一结构，换了措辞。"},
        {"where": "user_delivery 评论区段末",
         "quote": "这次明确不做购买、到店、私信或领取引导，所以评论区也不放任何这类动作。",
         "why": "交付块里再次把边界复述成四项业务动作，「只保留内容本身」未进入约束面。"},
    ]
    traces = {p: {"artifact": art.count(p), "user_delivery": ud.count(p)}
              for p in ("闭合", "权威顺序", "要求受众", "只保留内容本身")}
    add("D1-c", "FAIL",
        {"adjudicator": "BOUNDED_JUDGMENT_UNDER_FROZEN_RUBRIC",
         "rubric": "后继 Skill「CTA 权威顺序」＋ Founder 裁决 3",
         "verbatim_findings": findings,
         "new_rule_left_no_trace": traces,
         "interpretation": "新增的 CTA 权威顺序规则在本次推理里没有留下任何痕迹"
                           "（『闭合』『权威顺序』『要求受众』三词在产出中均为 0 次）；"
                           "模型仍按 PP-5「置顶第一条要能被追问」与 CTA 三级表的默认互动方法行事。",
         "evidence_locators_NOT_A_CHECKER": ["闭合", "权威顺序", "要求受众"]}, C[2])

    # D1-d 未空交付 / 未整项拒绝
    add("D1-d", "PASS" if (o.get("delivery_outcome") == "DELIVERED"
                           and "无法" not in ud[:200] and len(ud) > 500) else "FAIL",
        {"delivery_outcome": o.get("delivery_outcome"),
         "user_delivery_len": len(ud),
         "note": "完整交付标题三候选、封面两层文字、发布文案、评论区与两项待拍板事项，"
                 "未因约束收紧而空交付或整项拒绝"}, C[3])

    # D1-e used_fact_refs
    i = art.find("used_fact_refs")
    seg = art[i:i + 2500] if i >= 0 else ""
    add("D1-e", "PASS" if i >= 0 and not any(p in seg for p in HISTORY_PROBES) else
        ("FAIL" if i >= 0 else "NOT_VERIFIED"),
        {"section_present": i >= 0,
         "habitual_claims_in_section": [p for p in HISTORY_PROBES if p in seg],
         "excerpt_head": seg[:600]}, C[4])

    vs = [c["result"] for c in conds]
    d1_verdict = "PASS" if all(v == "PASS" for v in vs) else ("FAIL" if "FAIL" in vs
                                                              else "NOT_VERIFIED")
    llm_in_run = d1.get("llm_node_executions_in_run") or []
    res = {
        "document": {"id": "PPBS_PHASE_D_RESULT_v1.0",
                     "task_id": "DIYU-V1-PP-BOUNDARY-SUCCESSOR-001",
                     "criteria_ref": "unified-app/stages/PPBS_GATE_v1.1.json",
                     "criteria_sha256": shaf(GATE),
                     "inputs_sha256": shaf(os.path.join(UAPP, "stages", "PPBS_INPUTS_v1.0.json")),
                     "model_calls_by_adjudicator": 0},
        "D1": {"verdict": d1_verdict, "conditions": conds,
               "run_id": d1["workflow_run_id"], "elapsed_seconds": d1["elapsed_seconds"],
               "attempts": d1["attempts"],
               "input_matches_frozen": d1["input_matches_frozen"],
               "pp_published_version_at_run": d1["pp_published_version_at_run"],
               "pp_graph_md5_at_run": d1["pp_graph_md5_at_run"],
               "pp_provider_pin_at_run": d1["pp_provider_pin_at_run"]},
        "D2": {"verdict": "NOT_STARTED",
               "reason": "D1 出现正式 FAIL，按 Gate stop_rules 立即停止，不执行"},
        "D3": {"verdict": "NOT_STARTED",
               "reason": "同上；provider 钉从未改动，Seam 与 M5 全程走旧 PP"},
        "cost_account": {
            "top_level_workflow_runs_used": 1,
            "top_level_workflow_runs_budget": gate["budget"]["top_level_workflow_runs"],
            "llm_node_attempts_used": len(llm_in_run),
            "llm_node_attempts_hard_cap": gate["budget"]["deepseek_llm_node_attempts_hard_cap"],
            "retries": 0, "repeat_sampling": 0, "ab_tests": 0, "reviewer_calls": 0,
            "llm_nodes_detail": llm_in_run},
        "protected_surface_now": {
            "pp_provider_pin": psql("select p.version from tool_workflow_providers p "
                                    "where p.name='diyu_m5fp_publishing_packaging';"),
            "pin_unchanged_from_baseline": psql(
                "select p.version from tool_workflow_providers p "
                "where p.name='diyu_m5fp_publishing_packaging';") == PIN_MUST_STAY,
            "pp_workflow_rows": int(psql("select count(*) from workflows where app_id='%s';"
                                         % PP_APP)),
            "meaning": "Seam / M5 FP / 统一画布调用的仍然是旧 PP 版本；"
                       "b1 只作为 PP app 的已发布版本存在，未被任何消费者引用。"},
        "allowed_upgrades": {"applied": [], "why": "D1 未通过，三项上调一项都不成立"},
        "must_remain": gate["must_remain_regardless"],
    }
    io.open(OUT, "w", encoding="utf-8").write(json.dumps(res, ensure_ascii=False, indent=1) + "\n")
    print("D1 判定：%s" % d1_verdict)
    for c in conds:
        print("  [%s] %-6s %s" % ({"PASS": " ok ", "FAIL": "FAIL",
                                   "NOT_VERIFIED": " NV "}[c["result"]], c["id"], c["text"][:66]))
    print("成本：顶层 run %d/%d，LLM %d/%d，重试 0"
          % (1, gate["budget"]["top_level_workflow_runs"], len(llm_in_run),
             gate["budget"]["deepseek_llm_node_attempts_hard_cap"]))
    print("provider 钉：%s（未改动=%s）" % (res["protected_surface_now"]["pp_provider_pin"],
                                          res["protected_surface_now"]["pin_unchanged_from_baseline"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
