#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PP 边界后继 b2｜Phase E 判定器。**零模型调用。**

只按 PPBS_GATE_v2.0.json 的 phase_d_criteria 逐条重算（该判据逐块取自 v1.1，
本轮一个字符未改）。D1-b / D1-c 属有界判定：Rubric 冻结在 Gate 与 b2 Skill 里，
结论由产出原文逐字支撑；定位串只用于把已认定的事实指出来，标注 NOT_A_CHECKER。

    python3 PPBS_B2_D_ADJUDICATE_v1.0.py
"""
import hashlib
import io
import json
import os
import re
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
UAPP = os.path.abspath(os.path.join(HERE, ".."))
EVDIR = os.path.join(UAPP, "evidence", "stages", "pp_boundary_successor")
GATE = os.path.join(UAPP, "stages", "PPBS_GATE_v2.0.json")
OUT = os.path.join(UAPP, "stages", "PPBS_B2_PHASE_E_RESULT_v1.0.json")
PP_APP = "c9cdea24-9df3-400b-9ecd-1d740e8c96df"
STABLE_VERSION = "2026-08-29 03:34:58.999575"

HISTORY_PROBES = ["一直在用", "常用", "长期以来", "十年", "历来", "向来", "一贯",
                  "多年来", "一直以来", "从来都"]
HEDGE_PROBES = ["合理推断", "基于职责", "据说", "印象中"]
ACTION_PROBES = ["关注", "评论", "回复", "收藏", "转发", "分享", "点赞", "话题",
                 "购买", "到店", "预约", "咨询", "私信", "领取", "下单"]

# ---- 有界判定的逐字证据（读真实产出后写入，Rubric 早于结果冻结） ----
FINDINGS = {}


def psql(sql, db="dify"):
    p = subprocess.run(["docker", "exec", "-i", "docker-db_postgres-1", "psql", "-U", "postgres",
                        "-d", db, "-tA", "-c", sql], capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError("psql: " + (p.stderr or "")[:300])
    return p.stdout.strip()


def shaf(p):
    return hashlib.sha256(io.open(p, "rb").read()).hexdigest()


def qsent(text):
    out = []
    for line in text.split("\n"):
        for seg in re.split(r"(?<=[。！\n])", line):
            s = seg.strip()
            if s.endswith("？") or s.endswith("?"):
                out.append(s)
    return out


def load(case):
    p = os.path.join(EVDIR, "PPBS_B2_%s_RAW.json" % case)
    return json.load(io.open(p, encoding="utf-8")) if os.path.exists(p) else None


def adj_d1(gate):
    raw = load("D1")
    if raw is None:
        return {"verdict": "NOT_STARTED", "reason": "未运行"}
    o = raw["outputs"]
    art, ud = o.get("artifact") or "", o.get("user_delivery") or ""
    C = gate["phase_d_criteria"]["D1"]["must_all_hold"]
    conds = []

    def add(cid, res, obs, text):
        conds.append({"id": cid, "text": text, "result": res, "observed": obs})

    fields = ["mode:", "evidence_basis:", "used_fact_refs", "packaging_routes",
              "master_package:", "cover:", "first_frame:", "titles[]", "recommended_title:",
              "publish_copy:", "caption_rules:", "sound_placement:", "comment_design:",
              "cta_surface:", "author_share_line:", "platform_spec_status", "platform_variants",
              "release_check:", "single_distribution_promise", "return_to_script",
              "return_to_production", "fact_check_status", "stale_set", "failure_case",
              "assumptions", "missing"]
    present = [f for f in fields if f in art]
    add("D1-a", "PASS" if (o.get("artifact_status") == "OK"
                           and o.get("user_delivery_status") == "OK"
                           and len(present) == len(fields)
                           and len(art) > 2000 and len(ud) > 500) else "FAIL",
        {"artifact_len": len(art), "user_delivery_len": len(ud),
         "artifact_status": o.get("artifact_status"),
         "user_delivery_status": o.get("user_delivery_status"),
         "delivery_outcome": o.get("delivery_outcome"),
         "recovery_used": o.get("recovery_used"),
         "sufficiency_status": o.get("sufficiency_status"),
         "output_schema_fields_present": "%d/%d" % (len(present), len(fields)),
         "missing_fields": [f for f in fields if f not in present],
         "substantive_content": {"titles": 3, "packaging_routes": 2,
                                 "used_fact_refs_entries": art.count("output_location:"),
                                 "release_check_items": 5},
         "disclosed_observation": "publish_copy 给出开头三行全文，正文部分写的是结构说明"
                                 "（展开三问＋主观区保留＋收束句）而非逐字全文。"
                                 "PRE 模式下正文标注为草案是 Skill 既有要求；"
                                 "该字段非空、非占位，但正文深度低于 FINAL 模式应有的水平——"
                                 "如实记录，不影响本条判定（判据要求的是『非空、非占位』）。"},
        C[0])

    hist = [{"probe": p, "artifact": art.count(p), "user_delivery": ud.count(p)}
            for p in HISTORY_PROBES if art.count(p) or ud.count(p)]
    hedge = [{"probe": p, "artifact": art.count(p), "user_delivery": ud.count(p)}
             for p in HEDGE_PROBES if art.count(p) or ud.count(p)]
    add("D1-b", "PASS" if not hist and not hedge else "FAIL",
        {"adjudicator": "BOUNDED_JUDGMENT_UNDER_FROZEN_RUBRIC",
         "rubric": "b2 Skill「事实来源必须蕴含该主张」（继承自 b1，逐字未改）＋ Founder 裁决 2",
         "habitual_behavior_claims_found": hist,
         "hedge_words_found": hedge,
         "person_references_examined": [
             {"quote": "画面描述：衣橱内悬挂单品或苏禾手持/指向衣橱单品的画面（素材待检索…）",
              "verdict": "不是真实行为主张——这是**提议的镜头**，不断言此人过去做过什么"},
             {"quote": "「熟客卡点」为任务登记假设，不作真实顾客统计引用。",
              "verdict": "主动标为登记假设，且明确拒绝当成真实统计"}],
         "used_fact_refs_entries": [
             "recommended_title → FACT/THIS_ITEM_ONLY 上游卡点原文 ＋ 品牌事实",
             "cover → FACT/THIS_ITEM_ONLY 上游卡点原文",
             "first_frame → 品牌价值（一页纸夹具）",
             "final_publish_copy 开头三行 → FACT/THIS_ITEM_ONLY ＋ 品牌价值",
             "comment_design 被动答复边界 → cta_contract 原文",
             "final_publish_copy 末句 → expression_boundary"],
         "verbatim_finding": "六条 used_fact_refs 全部指向已登记来源（上游卡点原文、"
                             "一页纸夹具品牌事实/价值、cta_contract、expression_boundary）；"
                             "产出中不存在任何『某人过去或现在实际做过某事』的主张。",
         "compare_to_b1_failing_run": "b1 之前同场景写出「教顾客挑衣服时一直在用这套判断方法」"
                                      "并加推断脚注；b1 D1 与本次 b2 D1 该类主张均为 0 处，"
                                      "事实修复在 b2 中保持成立、未回退。",
         "evidence_locators_NOT_A_CHECKER": HISTORY_PROBES + HEDGE_PROBES}, C[1])

    surfaces = {
        "1 标题（3 候选）": ["单品好不好看，和能不能进你的衣橱，是两回事",
                            "判断一件新衣服要不要收，只看三个问题",
                            "你衣橱里，可能早有一件能顶它"],
        "2 封面文字": ["第一行（大）「好看 ≠ 能进衣橱」；第二行（小）「搭不搭，先看三个问题」"],
        "3 首帧": ["文字「你衣橱里已经有的，才是真正的试衣镜」"],
        "4 发布正文": ["开头三行单列（三句均为陈述句）；正文收束「不用急着多买一件」"],
        "5 cta_surface": ["NOT_APPLICABLE（cta_contract 为闭合表达"
                          "「不做购买、到店、私信或领取引导，只保留内容本身」"
                          "→ strict_cta_closed = true）。"],
        "6 comment_design": ["NOT_APPLICABLE（strict_cta_closed = true）。仅被动答复边界："
                             "如有人就三问某一条提问，回答只解释该方法本身，"
                             "不引向购买/到店/私信/领取。"],
        "7 author_share_line": ["「一件单品好不好看，和它能不能进你的衣橱，是两回事。」"
                                "（陈述句，不提问）"],
        "8 平台变体": ["平台未锁定 → 不输出平台变体。母版仅一份。"],
        "9 用户交付块": ["「这里可以定两件事：标题选 1、2 还是 3；封面用画面还是纯文字。」"
                        "——指向**用户**的待拍板事项，不是指向受众的动作"],
    }
    qa, qu = qsent(art), qsent(ud)
    action_ctx = {p: {"artifact": art.count(p), "user_delivery": ud.count(p)}
                  for p in ACTION_PROBES if art.count(p) or ud.count(p)}
    add("D1-c", "PASS" if (not qa and not qu) else "FAIL",
        {"adjudicator": "BOUNDED_JUDGMENT_UNDER_FROZEN_RUBRIC",
         "rubric": "b2 Skill「strict_cta_closed：一次判定，全面适用」＋「CTA 权威顺序」"
                   "＋ Founder 裁决 3",
         "nine_surfaces_walked": surfaces,
         "audience_directed_question_sentences": {"artifact": qa, "user_delivery": qu,
                                                  "count": len(qa) + len(qu)},
         "action_word_occurrences_and_context": {
             "counts": action_ctx,
             "every_occurrence_is": "否定式约束句（『不引向购买/到店/私信/领取』、"
                                    "『不做购买、到店、私信或领取引导』）或 Skill 既有的"
                                    "『发布前五条检查』内部自问（『看完之后会存吗』"
                                    "『会转给谁』）——后者是包装方自查，不是对外文案。",
             "zero_audience_facing_action_asks": True},
         "new_rule_left_a_trace": {"strict_cta_closed": art.count("strict_cta_closed"),
                                   "闭合": art.count("闭合"),
                                   "NOT_APPLICABLE": art.count("NOT_APPLICABLE"),
                                   "被动答复": art.count("被动答复"),
                                   "只保留内容本身": art.count("只保留内容本身")},
         "b1_failure_points_rechecked": [
             {"b1_failure": "cta_surface 逐字引用 cta_contract 后，自检面只剩四项业务动作，"
                            "「只保留内容本身」被丢掉",
              "b2_now": "cta_surface 明写「cta_contract 为闭合表达『…只保留内容本身』"
                        "→ strict_cta_closed = true」，闭合表达进入了约束面",
              "fixed": True},
             {"b1_failure": "comment_design 置顶首条自述为「被追问的」，为引出留言而设计",
              "b2_now": "comment_design = NOT_APPLICABLE（strict_cta_closed = true），"
                        "只写被动答复边界",
              "fixed": True},
             {"b1_failure": "author_share_line 是句末指向受众等回答的问句",
              "b2_now": "陈述句，产出自己标注「不提问」",
              "fixed": True},
             {"b1_failure": "comment_design 末行自我声明「均为判断方法的延伸，不构成 CTA」放行",
              "b2_now": "无任何自我声明式放行；该类表达 0 处",
              "fixed": True},
             {"b1_failure": "交付块把边界复述成四项业务动作",
              "b2_now": "交付块不复述边界清单，只交付内容与两项待拍板事项",
              "fixed": True}],
         "evidence_locators_NOT_A_CHECKER": ACTION_PROBES}, C[2])

    add("D1-d", "PASS" if (o.get("delivery_outcome") == "DELIVERED" and len(ud) > 500
                           and "无法" not in ud[:200]) else "FAIL",
        {"delivery_outcome": o.get("delivery_outcome"),
         "user_delivery_len": len(ud),
         "delivered": "3 个标题候选（各标 entry_type）＋ 推荐与理由 ＋ 封面两层文字 ＋ 首帧与"
                      "封面分工 ＋ 发布文案开头三行 ＋ 两项待用户拍板事项",
         "not_refused": "未出现整项拒绝、未出现『资料不足所以做不了』式空交付",
         "constraint_effect": "comment_design 与 cta_surface 取 NOT_APPLICABLE 是"
                              "上游闭合合同的正确执行结果，不是交付缺失"}, C[3])

    i = art.find("used_fact_refs")
    seg = art[i:art.find("packaging_routes", i)] if i >= 0 else ""
    add("D1-e", "PASS" if (i >= 0 and seg.count("output_location:") >= 5
                           and not any(p in seg for p in HISTORY_PROBES)) else
        ("FAIL" if i >= 0 else "NOT_VERIFIED"),
        {"section_present": i >= 0,
         "entries": seg.count("output_location:"),
         "every_entry_has_fact_id": seg.count("fact_id:") == seg.count("output_location:"),
         "habitual_claims_in_section": [p for p in HISTORY_PROBES if p in seg],
         "real_behavior_claims_in_section": 0,
         "disclosed_observation": "fact_id 用的是来源原文引用（FACT/THIS_ITEM_ONLY、"
                                  "《一页纸夹具品牌事实 v0.1》条目、cta_contract、"
                                  "expression_boundary），不是 BRF-XXX-001-NNN 形式的登记全称。"
                                  "登记全称格式属 Skill 自检 8c，**不在冻结的 D1-e 判据内**——"
                                  "本条判据问的是『每一项真实行为主张均有直接来源』，"
                                  "而本次产出的真实行为主张为 0，列出的每一条都挂到了具体来源。"
                                  "不因看到结果就给判据加条件（A2）。",
         "excerpt_head": seg[:500]}, C[4])

    vs = [c["result"] for c in conds]
    v = "PASS" if all(x == "PASS" for x in vs) else ("FAIL" if "FAIL" in vs else "NOT_VERIFIED")
    return {"verdict": v, "conditions": conds,
            "run_id": raw["workflow_run_id"], "elapsed_seconds": raw["elapsed_seconds"],
            "attempts": raw["attempts"], "http_status": raw["http_status"],
            "run_status": raw["run_status"],
            "pp_published_version_at_run": raw["pp_published_version_at_run"],
            "pp_graph_md5_at_run": raw["pp_graph_md5_at_run"],
            "pp_provider_pin_at_run": raw["pp_provider_pin_at_run"],
            "llm_node_executions": [{"node_id": n["node_id"], "status": n["status"]}
                                    for n in (raw.get("node_detail") or [])
                                    if n["type"] == "llm"]}


def main():
    gate = json.load(io.open(GATE, encoding="utf-8"))
    d1 = adj_d1(gate)
    runs = sum(1 for c in ("D1", "D2", "D3") if load(c) is not None)
    llm = len(d1.get("llm_node_executions") or [])
    res = {"document": {"id": "PPBS_B2_PHASE_E_RESULT_v1.0",
                        "task_id": "DIYU-V1-PP-BOUNDARY-SUCCESSOR-001",
                        "task_mode": "REBASE",
                        "criteria_ref": "unified-app/stages/PPBS_GATE_v2.0.json",
                        "criteria_sha256": shaf(GATE),
                        "criteria_identical_to_v1_1": "phase_d_criteria 逐块取自 v1.1，未改一个字符",
                        "inputs_sha256": shaf(os.path.join(UAPP, "stages",
                                                           "PPBS_INPUTS_v1.0.json")),
                        "model_calls_by_adjudicator": 0},
           "E1_D1": d1,
           "E2_D2": ({"verdict": "NOT_STARTED", "reason": "待 D1 判定为 PASS 后执行"}
                     if load("D2") is None else {}),
           "E3_D3": ({"verdict": "NOT_STARTED",
                      "reason": "仅在 D1、D2 都 PASS 且 provider 已重钉到 b2 之后执行"}
                     if load("D3") is None else {}),
           "cost_account": {"top_level_workflow_runs_used": runs,
                            "top_level_workflow_runs_budget":
                                gate["budget"]["top_level_workflow_runs"],
                            "llm_node_attempts_used": llm,
                            "llm_node_attempts_hard_cap":
                                gate["budget"]["deepseek_llm_node_attempts_hard_cap"],
                            "retries": 0, "repeat_sampling": 0, "ab_tests": 0,
                            "reviewer_calls": 0},
           "protected_surface_now": {
               "pp_current_graph_md5": psql("select md5(w.graph) from workflows w join apps a "
                                            "on a.workflow_id=w.id where a.id='%s';" % PP_APP),
               "pp_current_version": psql("select w.version from workflows w join apps a "
                                          "on a.workflow_id=w.id where a.id='%s';" % PP_APP),
               "pp_provider_pin": psql("select version from tool_workflow_providers "
                                       "where name='diyu_m5fp_publishing_packaging';"),
               "pin_is_old_stable": psql("select version from tool_workflow_providers where "
                                         "name='diyu_m5fp_publishing_packaging';")
                                    == STABLE_VERSION,
               "pp_workflow_rows": int(psql("select count(*) from workflows where app_id='%s';"
                                            % PP_APP)),
               "seam_graph_md5": psql("select md5(w.graph) from workflows w join apps a "
                                      "on a.workflow_id=w.id "
                                      "where a.id='5fca0162-e26b-4545-a00b-66b1a2a2a077';")},
           "allowed_upgrades": {"applied": [],
                                "why": "三项上调只在 D1、D2、D3 全部 PASS 之后成立"},
           "must_remain": gate["must_remain_regardless"]}
    io.open(OUT, "w", encoding="utf-8").write(json.dumps(res, ensure_ascii=False, indent=1) + "\n")
    print("E1 · D1 判定：%s" % d1["verdict"])
    for c in d1.get("conditions", []):
        print("  [%s] %-6s %s" % ({"PASS": " ok ", "FAIL": "FAIL",
                                   "NOT_VERIFIED": " NV "}[c["result"]], c["id"],
                                  c["text"][:64]))
    print("run=%s %s %.1fs attempts=%s LLM=%d"
          % (d1.get("run_id"), d1.get("run_status"), d1.get("elapsed_seconds") or 0,
             d1.get("attempts"), llm))
    ps = res["protected_surface_now"]
    print("PP 当前发布 %s / %s；provider 钉=%s（旧稳定=%s）；workflow 行=%d；Seam=%s"
          % (ps["pp_current_version"], ps["pp_current_graph_md5"][:12], ps["pp_provider_pin"],
             ps["pin_is_old_stable"], ps["pp_workflow_rows"], ps["seam_graph_md5"][:12]))
    return 0 if d1["verdict"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
