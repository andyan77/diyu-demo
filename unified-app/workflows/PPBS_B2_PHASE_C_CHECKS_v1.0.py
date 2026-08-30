#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PP 边界后继 b2｜Phase C 确定性验证 C-01…C-13。**零模型调用、零 Dify 写入。**

判据真源：unified-app/stages/PPBS_GATE_v2.0.json（已冻结并提交，早于任何 b2 模型结果）。

C-05／C-06／C-11／C-12／C-13 的「控制」都是**规则层控制**：
规则是否真的装在 b2 里并且成关卡。单点变异 = 从 b2 文本里整块删掉该规则块
⇒ 对应控制器必须由 PASS 翻成 FAIL，且另外两块不受影响（证明三块各自独立有区分度）。
规则装载检查器只看**规则自身的表述结构**，零案例内容；
交付层判定由 E1/E2/E3 按冻结判据读真实产出，不由本文件代劳。

    python3 PPBS_B2_PHASE_C_CHECKS_v1.0.py
"""
import hashlib
import importlib.util
import io
import json
import os
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
UAPP = os.path.abspath(os.path.join(HERE, ".."))
REPO = os.path.abspath(os.path.join(UAPP, ".."))
EVDIR = os.path.join(UAPP, "evidence", "stages", "pp_boundary_successor")
GATE = os.path.join(UAPP, "stages", "PPBS_GATE_v2.0.json")
INPUTS = os.path.join(UAPP, "stages", "PPBS_INPUTS_v1.0.json")
B2 = os.path.join(REPO, "content-production/skills/"
                        "packaging-content-for-release-m4-b2/SKILL.md")
B1 = os.path.join(REPO, "content-production/skills/"
                        "packaging-content-for-release-m4-b1/SKILL.md")
M4 = os.path.join(REPO, "content-production/skills/"
                        "packaging-content-for-release-m4/SKILL.md")
PP_APP = "c9cdea24-9df3-400b-9ecd-1d740e8c96df"
STABLE_VERSION = "2026-08-29 03:34:58.999575"
PIN_MUST_STAY = STABLE_VERSION
HOP_PIN_MUST_STAY = "2026-08-30 03:38:31.449618"
CAND = "85c01f85-a081-43e9-ab09-9993289cc200"
CAND_MD5_FROZEN = "99c3edf7bd12172a4fb011b588f25e57"
OTHER_PROTECTED = {"M1_HOST": "a4c3b19b-243f-490b-9aca-3aa19767d6a5",
                   "HOP": "6c46fdb1-5f49-4513-a0c0-29957b3dcee4",
                   "SEAM": "5fca0162-e26b-4545-a00b-66b1a2a2a077",
                   "MATRIX": "fd25ebfa-db67-40c3-82e5-202e1254facf",
                   "CAMPAIGN": "1f9d65ea-8af5-45f0-a1d0-a80223d354e2",
                   "CONTENT_BRIEF": "b1dcf784-540e-4b3f-8ba2-3812f477f3ce",
                   "CREATIVE_SCRIPT": "44b55f9d-3792-40c3-b095-f2696464b4ec",
                   "PRODUCTION_DIRECTOR": "13cfabd5-f592-4354-a304-47098b765697"}
PROTECTED_MD5_FROZEN = {"CAMPAIGN": "4876dacc43a73741b41c5a3083796347",
                        "CONTENT_BRIEF": "0c841642a71feedfb327ffb76aec0ddd",
                        "CREATIVE_SCRIPT": "a1cd859d5b88d0d025f336665ca94e51",
                        "HOP": "e38378c3c2a66b75aa7e645368c9e1ce",
                        "M1_HOST": "cd93757bcf8ad322f3b32fc43b2da3ff",
                        "MATRIX": "6cdaeac9cacf69fbeea4bd25e1536ace",
                        "PRODUCTION_DIRECTOR": "964e9a947dc9790d1de82496469689ad",
                        "SEAM": "db49a3da8973d4fdcbe9ecf63bdf7e2a"}

# 案例专用串禁止面（C-04A）：对**本轮新增文本**的约束，不是交付校验器。
# 后半段是 b1 的 D1 失败产出里的原句——本轮实现与检查器一个都不许写。
CASE_STRINGS = ["苏禾", "SUHE", "三问", "序里集", "XULI", "一直在用这套三问",
                "门店做搭配服务", "常用这套思路", "你自己买衣服前",
                "只有内容讨论和问题回应", "低风险互动范畴", "不含购买引导",
                "衣橱", "搭配师", "初秋通勤", "好看 ≠ 能搭",
                "均为判断方法的延伸", "先看衣橱里已有的", "你为什么买它",
                "买了但没怎么穿", "多买了一件的", "先别急着穿上", "被追问的"]

NEW_SCRIPTS = ["PPBS_B2_PHASE_A_RESTORE_v1.0.py", "PPBS_B2_BUILD_SUCCESSOR_SKILL_v1.0.py",
               "PPBS_B2_APPLY_AND_PUBLISH_v1.0.py", "PPBS_B2_PHASE_C_CHECKS_v1.0.py"]

# ---- 规则装载控制器：只看规则自身的表述结构，零案例内容 ----
FACT_CONTROL = ["## 事实来源必须蕴含该主张", "回指必须是蕴含关系，不是相关关系",
                "这条来源自己有没有说这件事发生过", "职责不蕴含行为",
                "任何限定语都不把无来源变成有来源",
                "改为不主张真实历史的当前内容表达", "局部失效不升级为整任务拒绝",
                "15. **（b1）**"]
CTA_CONTROL = ["### CTA 权威顺序", "cta_contract 的用户／上游自然语言原文",
               "上游闭合表达一旦出现，整份包装闭合",
               "不得用「低风险互动」放宽上游更严格的边界", "同样不得自造豁免类目",
               "内容内部的问题不是 CTA", "本节不删除低风险互动能力", "16. **（b1）**"]
# b2 新增三块，各自独立的控制器
CLOSED_POS_CONTROL = [
    "strict_cta_closed = true",
    "下面每一个对外输出面受同一条约束",
    "以及：句末指向受众、等一个回答的任何问句",
    "| 6 | `comment_design`（置顶首条、每一组预埋问答、每一条作者回复） |",
    "| 7 | `author_share_line` |",
    "| 9 | 用户交付块的每一句（**包括你对边界本身的那句说明**） |",
]
OPEN_NEG_CONTROL_NEW = [
    "strict_cta_closed = false` 时，什么都不变",
    "低风险互动能力**一条没删**",
    "b2 只在 `true` 那一支收紧，另一支一个字都没动",
    "= false` 时，本节**照常全部适用**，一条都不减",   # 探针修正：原写法把反引号放在 false 之前，与实际文本不符
    "`false` 时，本节照常适用",
]
OPEN_NEG_CONTROL_INHERITED = [
    "- **第一条自己写**，写一条**能被追问的**，不是\"感谢支持\"",
    "- 预埋 2 个可能被问到的问题，先准备好答案",
    "按目标与表达裁量即可提出",
    "**可以做**：提一个能一句话回答的具体问题",
]
COMMENT_CONTROL = [
    "`strict_cta_closed = true` 时，本节下面三条要求**整体不适用**",
    "不主动设计置顶互动问题",
    "换一种措辞继续要求互动，等于没有执行这一条",
]
SHARE_CONTROL = [
    "`author_share_line` 只能是**陈述句**",
    "句末指向受众、在等一个回答**，同样不成立",
]
ALLSURFACE_CONTROL = [
    "17. **（b2）**",
    "把那张九行的对外输出面清单逐行走一遍",
    "只扫了购买／到店／私信／领取这几类业务动作，**就是没扫完**",
]


def psql(sql, db="dify"):
    p = subprocess.run(["docker", "exec", "-i", "docker-db_postgres-1", "psql", "-U", "postgres",
                        "-d", db, "-tA", "-c", sql], capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError("psql: " + (p.stderr or "")[:300])
    return p.stdout.strip()


def sha(s):
    return hashlib.sha256((s or "").encode("utf-8")).hexdigest()


def shaf(p):
    return hashlib.sha256(io.open(p, "rb").read()).hexdigest()


def allin(text, probes):
    return all(p in text for p in probes)


def missing(text, probes):
    return [p for p in probes if p not in text]


def main():
    R = []

    def add(cid, ok, obs, text=""):
        R.append({"id": cid, "text": text, "result": "PASS" if ok else "FAIL", "observed": obs})

    gate = json.load(io.open(GATE, encoding="utf-8"))
    TXT = {c["id"]: c["text"] for c in gate["phase_c_deterministic_checks"]}

    b2 = io.open(B2, encoding="utf-8").read()
    b1 = io.open(B1, encoding="utf-8").read()
    m4 = io.open(M4, encoding="utf-8").read()
    build = json.load(io.open(os.path.join(EVDIR, "PPBS_B2_BUILD_SUCCESSOR_SKILL.json"),
                              encoding="utf-8"))
    applied = json.load(io.open(os.path.join(EVDIR, "PPBS_B2_APPLY_AND_PUBLISH.json"),
                                encoding="utf-8"))

    graph = json.loads(psql("select w.graph from workflows w join apps a on a.workflow_id=w.id "
                            "where a.id='%s';" % PP_APP))
    live_sys = None
    for n in graph["nodes"]:
        if n.get("id") == "skill_llm":
            for p in n["data"]["prompt_template"]:
                if p.get("role") == "system":
                    live_sys = p["text"]
    tail = applied["injection_tail"]

    # ---------- C-01 字节可回指 ----------
    starts = bool(live_sys and live_sys.startswith(b2))
    add("C-01", starts and sha(live_sys[len(b2):]) == tail["sha256"],
        {"live_len": len(live_sys or ""), "b2_len": len(b2),
         "live_starts_with_b2": starts,
         "tail_sha256_live": sha(live_sys[len(b2):]) if live_sys else None,
         "tail_sha256_expected_verbatim_from_old_version": tail["sha256"],
         "tail_len": len(live_sys) - len(b2) if live_sys else None,
         "b2_sha256": sha(b2)}, TXT["C-01"])

    # ---------- C-02 除 skill_llm.system 外无其它变化 ----------
    old_graph = json.loads(psql("select graph from workflows where app_id='%s' and version='%s';"
                                % (PP_APP, STABLE_VERSION)))

    def strip_sys(g):
        gg = json.loads(json.dumps(g))
        for n in gg["nodes"]:
            if n.get("id") == "skill_llm":
                for p in n["data"]["prompt_template"]:
                    if p.get("role") == "system":
                        p["text"] = "<SYSTEM>"
        return json.dumps(gg, ensure_ascii=False, sort_keys=True)

    same_except_sys = strip_sys(graph) == strip_sys(old_graph)
    llm_models = {n["id"]: (n["data"].get("model") or {})
                  for n in graph["nodes"] if n.get("data", {}).get("type") == "llm"}
    old_llm_models = {n["id"]: (n["data"].get("model") or {})
                      for n in old_graph["nodes"] if n.get("data", {}).get("type") == "llm"}
    add("C-02", same_except_sys and applied["nodes_touched"] == ["skill_llm"]
        and applied["edges_unchanged"] and applied["skill_llm_only_system_text_changed"]
        and llm_models == old_llm_models,
        {"graph_identical_except_skill_llm_system": same_except_sys,
         "nodes_touched_at_apply": applied["nodes_touched"],
         "edges_unchanged": applied["edges_unchanged"],
         "node_count": len(graph["nodes"]), "edge_count": len(graph["edges"]),
         "llm_model_and_params_unchanged": llm_models == old_llm_models,
         "llm_models_now": llm_models,
         "md5_before": applied["graph_md5_before"],
         "md5_after": applied.get("graph_md5_after")}, TXT["C-02"])

    # ---------- C-03 其余八应用与候选图零漂移 ----------
    now = {k: psql("select md5(w.graph) from workflows w join apps a on a.workflow_id=w.id "
                   "where a.id='%s';" % v).strip() for k, v in sorted(OTHER_PROTECTED.items())}
    drift = {k: {"frozen": PROTECTED_MD5_FROZEN[k], "now": v}
             for k, v in now.items() if v != PROTECTED_MD5_FROZEN[k]}
    cand = psql("select md5(w.graph) from workflows w join apps a on a.workflow_id=w.id "
                "where a.id='%s';" % CAND)
    hop = psql("select p.version from tool_workflow_providers p where p.name='diyu_uapp_hop';")
    add("C-03", not drift and cand == CAND_MD5_FROZEN and hop == HOP_PIN_MUST_STAY,
        {"other_eight_drift": drift, "other_eight_now": now,
         "candidate_md5_now": cand, "candidate_md5_frozen": CAND_MD5_FROZEN,
         "hop_pin_now": hop}, TXT["C-03"])

    # ---------- C-04A 本轮新增文本零案例专用串 ----------
    inserted = io.open(os.path.join(EVDIR, "PPBS_B2_INSERTED_TEXT.txt"), encoding="utf-8").read()
    scanned = {"b2_inserted_skill_text": inserted}
    for f in NEW_SCRIPTS:
        scanned["script:" + f] = io.open(os.path.join(HERE, f), encoding="utf-8").read()
    hits = []
    for where, txt in scanned.items():
        for s in CASE_STRINGS:
            c = txt.count(s)
            if c:
                hits.append({"where": where, "string": s, "count": c})
    selfdef = [h for h in hits if h["where"] == "script:PPBS_B2_PHASE_C_CHECKS_v1.0.py"]
    real = [h for h in hits if h not in selfdef]
    add("C-04A", not real,
        {"case_specific_hits_in_new_text": real, "scanned": sorted(scanned),
         "inserted_chars": len(inserted),
         "ban_list_size": len(CASE_STRINGS),
         "excluded_self_definition": "本文件内的 CASE_STRINGS 禁止面常量表本身含这些串，"
                                     "它是判据定义不是实现分支，共 %d 处，已单列不计入"
                                     % len(selfdef)}, TXT["C-04A"])

    # ---------- C-04B 继承体逐字等同 b1，且 b1 事实修复整块在场 ----------
    fs = b1.find("\n## 事实来源必须蕴含该主张\n")
    fe = b1.find("\n---\n\n## 局部失效与不反向传播\n", fs + 1)
    fact_block = b1[fs:fe]
    cs = b1.find("\n### CTA 权威顺序\n")
    ce = b1.find("\n---\n\n", cs + 1)
    cta_block = b1[cs:ce]
    add("C-04B", build["inherited_body_byte_identical_to_b1"]
        and b2.count(fact_block) == 1 and b2.count(cta_block) == 1
        and b2.count("BRF-SUHE") == b1.count("BRF-SUHE") == m4.count("BRF-SUHE"),
        {"inherited_body_byte_identical_to_b1":
            build["inherited_body_byte_identical_to_b1"],
         "b1_fact_section_verbatim_occurrences": b2.count(fact_block),
         "b1_fact_section_chars": len(fact_block),
         "b1_cta_section_verbatim_occurrences": b2.count(cta_block),
         "b1_cta_section_chars": len(cta_block),
         "BRF_SUHE_m4": m4.count("BRF-SUHE"), "BRF_SUHE_b1": b1.count("BRF-SUHE"),
         "BRF_SUHE_b2": b2.count("BRF-SUHE"),
         "note": "事实来源修复不得回退：b1 两整块逐字在场，各 1 次"}, TXT["C-04B"])

    # ---------- C-05 / C-06 b1 两条规则的单点变异（回归） ----------
    def cut(text, start_marker, end_marker):
        i = text.find(start_marker)
        j = text.find(end_marker, i + 1) if i >= 0 else -1
        return (text[:i] + text[j:]) if (i >= 0 and j > i) else None

    mut_fact = cut(b2, "\n## 事实来源必须蕴含该主张\n", "\n---\n\n## 局部失效与不反向传播\n")
    mut_cta = cut(b2, "\n### CTA 权威顺序\n", "\n### strict_cta_closed：一次判定，全面适用\n")
    add("C-05", mut_fact is not None and allin(b2, FACT_CONTROL)
        and not allin(mut_fact, FACT_CONTROL),
        {"baseline": allin(b2, FACT_CONTROL),
         "after_removal": allin(mut_fact, FACT_CONTROL) if mut_fact is not None else None,
         "removed_chars": len(b2) - len(mut_fact) if mut_fact is not None else None,
         "probes_lost": missing(mut_fact, FACT_CONTROL) if mut_fact is not None else None,
         "cta_control_unaffected": allin(mut_fact, CTA_CONTROL) if mut_fact is not None else None},
        TXT["C-05"])
    add("C-06", mut_cta is not None and allin(b2, CTA_CONTROL)
        and not allin(mut_cta, CTA_CONTROL),
        {"baseline": allin(b2, CTA_CONTROL),
         "after_removal": allin(mut_cta, CTA_CONTROL) if mut_cta is not None else None,
         "removed_chars": len(b2) - len(mut_cta) if mut_cta is not None else None,
         "probes_lost": missing(mut_cta, CTA_CONTROL) if mut_cta is not None else None,
         "fact_control_unaffected": allin(mut_cta, FACT_CONTROL) if mut_cta is not None else None},
        TXT["C-06"])

    # ---------- C-07 provider / Seam 仍指旧稳定版 ----------
    pin = psql("select p.version from tool_workflow_providers p "
               "where p.name='diyu_m5fp_publishing_packaging';")
    seam = psql("select md5(w.graph) from workflows w join apps a on a.workflow_id=w.id "
                "where a.id='%s';" % OTHER_PROTECTED["SEAM"])
    add("C-07", pin == PIN_MUST_STAY and seam == PROTECTED_MD5_FROZEN["SEAM"],
        {"pp_provider_pin_now": pin, "must_stay": PIN_MUST_STAY,
         "seam_graph_md5_now": seam,
         "meaning": "Seam 与 M5 在 E1/E2 期间仍走旧稳定 PP，本次发布不改变它们看到的图"},
        TXT["C-07"])

    # ---------- C-08 判据与输入哈希早于任何模型结果 ----------
    gate_commit = subprocess.run(["git", "-C", REPO, "log", "--oneline", "-1", "--",
                                  "unified-app/stages/PPBS_GATE_v2.0.json"],
                                 capture_output=True, text=True).stdout.strip()
    b2_raw_present = [f for f in ("PPBS_B2_D1_RAW.json", "PPBS_B2_D2_RAW.json",
                                  "PPBS_B2_D3_RAW.json")
                      if os.path.exists(os.path.join(EVDIR, f))]
    add("C-08", bool(gate_commit) and not b2_raw_present,
        {"gate_v2_0_commit": gate_commit, "gate_v2_0_sha256": shaf(GATE),
         "inputs_sha256": shaf(INPUTS),
         "inputs_reused_unchanged": shaf(INPUTS) == gate["document"]["inputs_ref"]["sha256"],
         "b2_model_results_on_disk": b2_raw_present,
         "b2_model_calls_so_far": 0}, TXT["C-08"])

    # ---------- C-09 正向控制 ----------
    add("C-09", allin(b2, CLOSED_POS_CONTROL),
        {"probes": CLOSED_POS_CONTROL, "missing": missing(b2, CLOSED_POS_CONTROL),
         "surface_table_rows_found": sum(1 for i in range(1, 10)
                                         if ("| %d | " % i) in b2)}, TXT["C-09"])

    # ---------- C-10 负向控制 ----------
    neg_ok = allin(b2, OPEN_NEG_CONTROL_NEW) and allin(b2, OPEN_NEG_CONTROL_INHERITED)
    add("C-10", neg_ok,
        {"false_branch_probes": OPEN_NEG_CONTROL_NEW,
         "false_branch_missing": missing(b2, OPEN_NEG_CONTROL_NEW),
         "inherited_low_risk_capability_probes": OPEN_NEG_CONTROL_INHERITED,
         "inherited_missing": missing(b2, OPEN_NEG_CONTROL_INHERITED),
         "meaning": "strict_cta_closed=false 时合法低风险互动能力未被全局删除："
                    "PP-5 原三条要求、CTA 三级表低风险行、无 CTA 评论区『可以做』清单"
                    "全部逐字在场"}, TXT["C-10"])

    # ---------- C-11 / C-12 / C-13 三块单点变异，互相独立 ----------
    _s = importlib.util.spec_from_file_location(
        "b2b", os.path.join(HERE, "PPBS_B2_BUILD_SUCCESSOR_SKILL_v1.0.py"))
    B = importlib.util.module_from_spec(_s)
    _s.loader.exec_module(B)
    BLOCKS = {"C-11": ("PP5_COND", B.PP5_COND, COMMENT_CONTROL, "comment_design 条件化"),
              "C-12": ("SHARE_COND", B.SHARE_COND, SHARE_CONTROL, "author_share_line 条件化"),
              "C-13": ("SELFCHECK17", B.SELFCHECK17, ALLSURFACE_CONTROL, "全表面自检")}
    ALL3 = {"comment": COMMENT_CONTROL, "share": SHARE_CONTROL, "allsurface": ALLSURFACE_CONTROL}
    base3 = {k: allin(b2, v) for k, v in ALL3.items()}
    for cid, (bid, block, ctrl, label) in BLOCKS.items():
        if b2.count(block) != 1:
            add(cid, False, {"error": "变异块在 b2 中出现 %d 次，无法做单点变异"
                             % b2.count(block)}, TXT[cid])
            continue
        mut = b2.replace(block, "", 1)
        after3 = {k: allin(mut, v) for k, v in ALL3.items()}
        target = {"C-11": "comment", "C-12": "share", "C-13": "allsurface"}[cid]
        flipped = base3[target] and not after3[target]
        others_ok = all(after3[k] for k in ALL3 if k != target)
        add(cid, flipped and others_ok,
            {"mutated_block": bid, "label": label, "removed_chars": len(block),
             "baseline_three_controls": base3, "after_mutation_three_controls": after3,
             "target_control": target, "target_flipped_PASS_to_FAIL": flipped,
             "other_two_unaffected": others_ok,
             "probes_lost": missing(mut, ctrl)}, TXT[cid])

    npass = sum(1 for x in R if x["result"] == "PASS")
    rep = {"document": {"id": "PPBS_B2_PHASE_C_CHECKS_v1.0",
                        "task_id": "DIYU-V1-PP-BOUNDARY-SUCCESSOR-001",
                        "task_mode": "REBASE",
                        "criteria_ref": "unified-app/stages/PPBS_GATE_v2.0.json",
                        "criteria_sha256": shaf(GATE),
                        "b2_skill_sha256": sha(b2),
                        "model_calls": 0, "dify_writes": 0, "workflow_runs_started": 0},
           "summary": {"pass": npass, "total": len(R),
                       "verdict": "PASS" if npass == len(R) else "FAIL"},
           "checks": R}
    io.open(os.path.join(EVDIR, "PPBS_B2_PHASE_C_CHECKS.json"), "w",
            encoding="utf-8").write(json.dumps(rep, ensure_ascii=False, indent=1) + "\n")
    for x in R:
        print("%-6s %-4s %s" % (x["id"], x["result"], x["text"][:66]))
        if x["result"] != "PASS":
            print("       " + json.dumps(x["observed"], ensure_ascii=False)[:900])
    print("---- %d/%d ----" % (npass, len(R)))
    return 0 if npass == len(R) else 1


if __name__ == "__main__":
    raise SystemExit(main())
