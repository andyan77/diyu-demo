#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PP 边界后继｜Phase C 确定性验证 C-01…C-08。**零模型调用、零 Dify 写入。**

判据真源：unified-app/stages/PPBS_GATE_v1.1.json（已冻结并提交，早于任何模型结果）。

C-05 / C-06 的「控制」指**规则层控制**：两条规则是否真的装在后继 Skill 里并且成关卡。
单点变异 = 从后继文本里整块删掉该规则 ⇒ 对应控制器必须由 PASS 翻成 FAIL。
规则装载检查器只看**规则自身的表述结构**，不含任何案例内容；
交付层的判定由 D1/D2/D3 按冻结判据读真实产出，不由本文件代劳。

    python3 PPBS_PHASE_C_CHECKS_v1.0.py
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
GATE = os.path.join(UAPP, "stages", "PPBS_GATE_v1.1.json")
INPUTS = os.path.join(UAPP, "stages", "PPBS_INPUTS_v1.0.json")
ADJ = os.path.join(UAPP, "stages", "PPBS_FOUNDER_ADJUDICATION_v1.0.md")
SUCCESSOR = os.path.join(REPO, "content-production/skills/"
                               "packaging-content-for-release-m4-b1/SKILL.md")
M4_SRC = os.path.join(REPO, "content-production/skills/"
                            "packaging-content-for-release-m4/SKILL.md")
PP_APP = "c9cdea24-9df3-400b-9ecd-1d740e8c96df"
PP_MD5_BEFORE = "788c8555aca09e6fa6d979f237f70157"
PIN_MUST_STAY = "2026-08-29 03:34:58.999575"
CAND = "85c01f85-a081-43e9-ab09-9993289cc200"
HOP_PIN_MUST_STAY = "2026-08-30 03:38:31.449618"
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
CAND_MD5_FROZEN = "99c3edf7bd12172a4fb011b588f25e57"

# 案例专用串禁止面（C-04A）。这是对**本轮新增文本**的约束，不是交付校验器。
CASE_STRINGS = ["苏禾", "SUHE", "三问", "序里集", "XULI", "一直在用这套三问",
                "门店做搭配服务", "常用这套思路", "你自己买衣服前",
                "只有内容讨论和问题回应", "低风险互动范畴", "不含购买引导",
                "衣橱", "搭配师", "初秋通勤", "好看 ≠ 能搭"]

NEW_SCRIPTS = ["PPBS_PHASE_A_SITE_CHECK_v1.0.py", "PPBS_FREEZE_INPUTS_v1.0.py",
               "PPBS_BUILD_SUCCESSOR_SKILL_v1.0.py", "PPBS_APPLY_AND_PUBLISH_v1.0.py",
               "PPBS_PHASE_C_CHECKS_v1.0.py"]

# ---- 规则装载控制器：只看规则自身的表述结构，零案例内容 ----
FACT_CONTROL = [
    "## 事实来源必须蕴含该主张",
    "回指必须是蕴含关系，不是相关关系",
    "这条来源自己有没有说这件事发生过",
    "职责不蕴含行为",
    "任何限定语都不把无来源变成有来源",
    "改为不主张真实历史的当前内容表达",
    "局部失效不升级为整任务拒绝",
]
CTA_CONTROL = [
    "### CTA 权威顺序",
    "cta_contract 的用户／上游自然语言原文",
    "上游闭合表达一旦出现，整份包装闭合",
    "不得用「低风险互动」放宽上游更严格的边界",
    "同样不得自造豁免类目",
    "内容内部的问题不是 CTA",
    "本节不删除低风险互动能力",
]
SELFCHECK_CONTROL = ["15. **（b1）**", "16. **（b1）**"]


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


def fact_control(text):
    return all(p in text for p in FACT_CONTROL) and SELFCHECK_CONTROL[0] in text


def cta_control(text):
    return all(p in text for p in CTA_CONTROL) and SELFCHECK_CONTROL[1] in text


def main():
    R = []

    def add(cid, ok, obs, text=""):
        R.append({"id": cid, "text": text, "result": "PASS" if ok else "FAIL", "observed": obs})

    gate = json.load(io.open(GATE, encoding="utf-8"))
    TXT = {c["id"]: c["text"] for c in gate["phase_c_deterministic_checks"]}

    succ = io.open(SUCCESSOR, encoding="utf-8").read()
    m4 = io.open(M4_SRC, encoding="utf-8").read()
    build = json.load(io.open(os.path.join(EVDIR, "PPBS_BUILD_SUCCESSOR_SKILL.json"),
                              encoding="utf-8"))
    applied = json.load(io.open(os.path.join(EVDIR, "PPBS_APPLY_AND_PUBLISH.json"),
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
    expect = succ + live_sys[len(succ):] if live_sys and live_sys.startswith(succ) else None
    add("C-01", bool(live_sys and live_sys.startswith(succ)
                     and sha(live_sys[len(succ):]) == tail["sha256"]),
        {"live_len": len(live_sys or ""), "successor_len": len(succ),
         "live_starts_with_successor": bool(live_sys and live_sys.startswith(succ)),
         "tail_sha256_live": sha(live_sys[len(succ):]) if live_sys else None,
         "tail_sha256_expected_from_old_version": tail["sha256"],
         "tail_len": len(live_sys) - len(succ) if live_sys else None,
         "successor_sha256": sha(succ)}, TXT["C-01"])

    # ---------- C-02 除 skill_llm.system 外无其它变化 ----------
    g2 = json.loads(json.dumps(graph))
    for n in g2["nodes"]:
        if n.get("id") == "skill_llm":
            for p in n["data"]["prompt_template"]:
                if p.get("role") == "system":
                    p["text"] = m4 + live_sys[len(succ):]
    restored = hashlib.md5(json.dumps(g2, ensure_ascii=False, separators=(", ", ": ")
                                      ).encode("utf-8")).hexdigest()
    # 直接用服务端 md5 语义不可复现时，退回结构比对
    old_graph = json.loads(psql("select graph from workflows where app_id='%s' and version='%s';"
                                % (PP_APP, PIN_MUST_STAY)))
    def strip_sys(g):
        gg = json.loads(json.dumps(g))
        for n in gg["nodes"]:
            if n.get("id") == "skill_llm":
                for p in n["data"]["prompt_template"]:
                    if p.get("role") == "system":
                        p["text"] = "<SYSTEM>"
        return json.dumps(gg, ensure_ascii=False, sort_keys=True)
    same_except_sys = strip_sys(graph) == strip_sys(old_graph)
    add("C-02", same_except_sys and applied["nodes_touched"] == ["skill_llm"]
        and applied["edges_unchanged"] and applied["skill_llm_only_system_text_changed"],
        {"graph_identical_except_skill_llm_system": same_except_sys,
         "nodes_touched_at_apply": applied["nodes_touched"],
         "edges_unchanged": applied["edges_unchanged"],
         "node_count": len(graph["nodes"]), "edge_count": len(graph["edges"]),
         "md5_before": PP_MD5_BEFORE, "md5_after": applied.get("graph_md5_after"),
         "_restored_probe": restored}, TXT["C-02"])

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
    inserted = io.open(os.path.join(EVDIR, "PPBS_INSERTED_TEXT.txt"), encoding="utf-8").read()
    scanned = {"inserted_skill_text": inserted}
    for f in NEW_SCRIPTS:
        scanned["script:" + f] = io.open(os.path.join(HERE, f), encoding="utf-8").read()
    hits = []
    for where, txt in scanned.items():
        for s in CASE_STRINGS:
            c = txt.count(s)
            if c:
                hits.append({"where": where, "string": s, "count": c})
    # 本文件自身的 CASE_STRINGS 常量表不算命中（它是禁止面定义，不是分支）
    selfdef = [h for h in hits if h["where"] == "script:PPBS_PHASE_C_CHECKS_v1.0.py"]
    real = [h for h in hits if h not in selfdef]
    add("C-04A", not real,
        {"case_specific_hits_in_new_text": real,
         "scanned": sorted(scanned), "inserted_chars": len(inserted),
         "excluded_self_definition": "PPBS_PHASE_C_CHECKS_v1.0.py 内的 CASE_STRINGS 禁止面常量表"
                                     "本身包含这些串，它是判据定义不是实现分支，"
                                     "共 %d 处，已单列不计入" % len(selfdef)}, TXT["C-04A"])

    # ---------- C-04B 继承体逐字等同源 ----------
    add("C-04B", build["inherited_body_byte_identical_to_source"]
        and succ.count("BRF-SUHE") == m4.count("BRF-SUHE"),
        {"inherited_body_byte_identical": build["inherited_body_byte_identical_to_source"],
         "BRF_SUHE_in_source": m4.count("BRF-SUHE"),
         "BRF_SUHE_in_successor": succ.count("BRF-SUHE"),
         "note": "两处均为源 Skill 既有的 used_fact_refs 编号格式示例，本轮未增未改未删"},
        TXT["C-04B"])

    # ---------- C-05 / C-06 单点变异 ----------
    base_fact, base_cta = fact_control(succ), cta_control(succ)
    blocks = {b["id"]: b for b in build["inserted_blocks"]}
    fact_block = io.open(os.path.join(EVDIR, "PPBS_INSERTED_TEXT.txt"), encoding="utf-8").read()
    # 直接从后继文本里按小节整块切除
    def cut(text, start_marker, end_marker):
        i = text.find(start_marker)
        j = text.find(end_marker, i + 1) if i >= 0 else -1
        return (text[:i] + text[j:]) if (i >= 0 and j > i) else None
    mut_fact = cut(succ, "\n## 事实来源必须蕴含该主张\n", "\n---\n\n## 局部失效与不反向传播\n")
    mut_cta = cut(succ, "\n### CTA 权威顺序\n", "\n---\n\n## 母版制\n")
    add("C-05", mut_fact is not None and base_fact and not fact_control(mut_fact),
        {"baseline_fact_control": base_fact,
         "after_removing_fact_section": fact_control(mut_fact) if mut_fact is not None else None,
         "removed_chars": len(succ) - len(mut_fact) if mut_fact is not None else None,
         "cta_control_unaffected": cta_control(mut_fact) if mut_fact is not None else None,
         "probes": FACT_CONTROL}, TXT["C-05"])
    add("C-06", mut_cta is not None and base_cta and not cta_control(mut_cta),
        {"baseline_cta_control": base_cta,
         "after_removing_cta_section": cta_control(mut_cta) if mut_cta is not None else None,
         "removed_chars": len(succ) - len(mut_cta) if mut_cta is not None else None,
         "fact_control_unaffected": fact_control(mut_cta) if mut_cta is not None else None,
         "probes": CTA_CONTROL}, TXT["C-06"])

    # ---------- C-07 provider/Seam 仍指旧版本 ----------
    pin = psql("select p.version from tool_workflow_providers p "
               "where p.name='diyu_m5fp_publishing_packaging';")
    seam = psql("select md5(w.graph) from workflows w join apps a on a.workflow_id=w.id "
                "where a.id='%s';" % OTHER_PROTECTED["SEAM"])
    add("C-07", pin == PIN_MUST_STAY and seam == PROTECTED_MD5_FROZEN["SEAM"],
        {"pp_provider_pin_now": pin, "must_stay": PIN_MUST_STAY,
         "seam_graph_md5_now": seam,
         "meaning": "Seam 与 M5 在 D1/D2 期间仍走旧 PP 版本，本次发布不改变它们看到的图"},
        TXT["C-07"])

    # ---------- C-08 判据与输入哈希早于任何模型结果 ----------
    committed = subprocess.run(["git", "-C", REPO, "log", "--oneline", "-1", "--",
                                "unified-app/stages/PPBS_GATE_v1.0.json"],
                               capture_output=True, text=True).stdout.strip()
    inp = json.load(io.open(INPUTS, encoding="utf-8"))
    add("C-08", bool(committed) and inp["document"]["model_calls_so_far"] == 0,
        {"gate_v1_0_commit": committed,
         "gate_v1_0_sha256": shaf(os.path.join(UAPP, "stages", "PPBS_GATE_v1.0.json")),
         "gate_v1_1_sha256": shaf(GATE),
         "inputs_sha256": shaf(INPUTS), "adjudication_sha256": shaf(ADJ),
         "model_calls_so_far_at_freeze": inp["document"]["model_calls_so_far"],
         "model_calls_so_far_now": 0}, TXT["C-08"])

    npass = sum(1 for x in R if x["result"] == "PASS")
    rep = {"document": {"id": "PPBS_PHASE_C_CHECKS_v1.0",
                        "task_id": "DIYU-V1-PP-BOUNDARY-SUCCESSOR-001",
                        "criteria_ref": "unified-app/stages/PPBS_GATE_v1.1.json",
                        "criteria_sha256": shaf(GATE),
                        "successor_skill_sha256": sha(succ),
                        "model_calls": 0, "dify_writes": 0, "workflow_runs_started": 0},
           "summary": {"pass": npass, "total": len(R),
                       "verdict": "PASS" if npass == len(R) else "FAIL"},
           "checks": R}
    io.open(os.path.join(EVDIR, "PPBS_PHASE_C_CHECKS.json"), "w",
            encoding="utf-8").write(json.dumps(rep, ensure_ascii=False, indent=1) + "\n")
    for x in R:
        print("%-6s %-4s %s" % (x["id"], x["result"], x["text"][:70]))
        if x["result"] != "PASS":
            print("       " + json.dumps(x["observed"], ensure_ascii=False)[:700])
    print("---- %d/%d ----" % (npass, len(R)))
    return 0 if npass == len(R) else 1


if __name__ == "__main__":
    raise SystemExit(main())
