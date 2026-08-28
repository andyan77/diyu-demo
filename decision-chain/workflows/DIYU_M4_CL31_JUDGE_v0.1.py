#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""M4-CL31-02 / 03 / 04 判定器

判据全部来自已冻结的取证合同 v0.5，必保清单与泄漏词表**从合同文件解析**，
不在本脚本内另抄一份，避免器械与判据漂移。
"""
import hashlib, json, os, re, sys, yaml

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
OUT = os.path.join(ROOT, "decision-chain/evidence/m4/final_closure")
CONTRACT = os.path.join(ROOT, "decision-chain/docs/V1_M4_EVIDENCE_COLLECTION_CONTRACT_v0.5.md")

RET_FIELDS = ["return_id", "source", "highest_damaged_layer", "precise_gap",
              "affected_objects", "proposed_disposition", "needs_user_decision"]


def contract_yaml(header):
    md = open(CONTRACT, encoding="utf-8").read()
    i = md.index(header)
    j = md.index("```yaml", i) + len("```yaml\n")
    k = md.index("```", j)
    return yaml.safe_load(md[j:k])


def frozen_artifact():
    md = open(CONTRACT, encoding="utf-8").read()
    i = md.index("### §2.3 冻结专业产出")
    j = md.index("```text", i) + len("```text\n")
    return md[j:md.index("```", j)].rstrip("\n")


MUST = contract_yaml("### §2.4 冻结必保内容清单")
LEAKS = contract_yaml("## §2.6 内部泄漏词表")["leak_terms"]


def lcs_len(a, b):
    """最长公共子串长度（滚动 DP）。"""
    if not a or not b:
        return 0
    if len(a) > len(b):
        a, b = b, a
    prev = [0] * (len(a) + 1); best = 0
    for cb in b:
        cur = [0] * (len(a) + 1)
        for i, ca in enumerate(a, 1):
            if ca == cb:
                cur[i] = prev[i - 1] + 1
                if cur[i] > best: best = cur[i]
        prev = cur
    return best


RE_NUM = re.compile(r"\d+(?:\.\d+)?")
RE_CN_TIME = re.compile(r"(早晨|早上|中午|下午|晚上|工作日|周[一二三四五六日末]|"
                        r"[0-9]+月|[0-9]+日|[0-9]+点|初秋|入秋|换季|季末)")
ENTITIES = ["序里集", "苏禾", "周宁", "陈晚", "林可", "通勤外套", "马甲", "内搭",
            "风衣", "西装外套", "针织开衫", "衬衫", "门店", "到店", "私域", "社群"]


def extract_facts(text):
    """§2.5 冻结五类：具体数字 / 专有名词 / 商品名 / 地点 / 时间。不含引号内整句。"""
    t = text or ""
    return sorted(set(RE_NUM.findall(t)) | set(RE_CN_TIME.findall(t))
                  | {e for e in ENTITIES if e in t})


def leaks_in(t):
    return [w for w in LEAKS if w in (t or "")]


def must_report(ud):
    rep, missing = {}, []
    for grp in ("CORE", "COND", "NEXT"):
        for k, alts in MUST[grp].items():
            hit = next((a for a in alts if a in (ud or "")), None)
            rep[k] = {"present": bool(hit), "matched": hit, "alternatives": alts}
            if not hit:
                missing.append(k)
    return rep, missing


def j(node_outputs):
    try:
        return json.loads(node_outputs) if node_outputs else {}
    except Exception:
        return {}


def main():
    raw = json.load(open(os.path.join(OUT, "CL31_RUNTIME_RAW.json"), encoding="utf-8"))
    art = frozen_artifact()
    V = {"contract": "V1-M4-EVIDENCE-COLLECTION-v0.5", "criteria": {}, "notes": [], "findings": []}

    # ══════════════ M4-CL31-02（INJ-01） ══════════════
    e = raw["runs"]["INJ-01"]
    seam_runs = e["seam_runs"]
    c = {}
    sr = seam_runs[0] if seam_runs else None
    execs = sr["node_executions"] if sr else []
    c["①"] = "PASS" if any(x["node_id"] == "end_tool_fail" and x["status"] == "succeeded"
                           for x in execs) else "FAIL"
    end = next((x for x in execs if x["node_id"] == "end_tool_fail"), None)
    eo = j(end["outputs"]) if end else {}
    # END 节点 outputs 里带 inputs 包装的情况一并兼容
    ud = (eo.get("user_delivery") or (eo.get("outputs") or {}).get("user_delivery") or "").strip()
    outcome = eo.get("business_delivery_outcome") or (eo.get("outputs") or {}).get("business_delivery_outcome")
    rj = eo.get("returns_json") or (eo.get("outputs") or {}).get("returns_json") or "[]"
    c["②"] = "PASS" if ud else "FAIL"
    c["③"] = "PASS" if outcome == "NOT_DELIVERED" else "FAIL"
    try:
        rets = json.loads(rj)
    except Exception:
        rets = []
    c["④"] = "PASS" if rets and all(all(f in r for f in RET_FIELDS) for r in rets) else "FAIL"
    # ⑤ 两种读法都算，不挑一个能过的（见 M4-FND-027）
    per_run = [sum(1 for x in r["node_executions"] if x["node_id"] == "skill_llm")
               for r in e["child_runs"]]
    other_caps = [x["node_id"] for x in execs
                  if x["node_id"].startswith("tool_") and x["node_id"] != "tool_content_brief"]
    c5_prompt = "PASS" if not other_caps else "FAIL"           # Prompt 原文：没有重跑「其他」专业能力
    c5_literal = "PASS" if sum(per_run) <= 1 else "FAIL"       # v0.5 重述：总数 <= 1
    c["⑤"] = c5_prompt
    c["⑤_note"] = {"prompt_reading": c5_prompt, "v05_literal_total_reading": c5_literal,
                   "skill_llm_per_child_run": per_run, "skill_llm_total": sum(per_run),
                   "other_capability_tool_nodes_executed": other_caps}
    c["⑥"] = "PASS" if len(e["child_runs"]) <= 2 and all(
        r["status"] in ("failed", "succeeded", "partial-succeeded") for r in e["child_runs"]) else "FAIL"
    c["⑥_note"] = {"child_run_count": len(e["child_runs"]),
                   "retry_config": "max_retries=1（冻结设计，全部留痕）",
                   "child_run_ids": [r["run_id"] for r in e["child_runs"]]}
    c["⑦"] = "PASS" if sr and sr["run_id"] and execs else "FAIL"
    V["criteria"]["M4-CL31-02"] = {
        "conjuncts": c,
        "verdict": "PASS" if all(v == "PASS" for k, v in c.items() if not k.endswith("_note")) else "FAIL",
        "seam_run_id": sr["run_id"] if sr else None,
        "seam_run_status": sr["status"] if sr else None,
        "user_delivery_length": len(ud), "user_delivery": ud,
        "business_delivery_outcome": outcome,
        "leaks": leaks_in(ud), "returns_count": len(rets),
    }
    if leaks_in(ud):
        V["criteria"]["M4-CL31-02"]["verdict"] = "FAIL"
        V["criteria"]["M4-CL31-02"]["conjuncts"]["②"] = "FAIL"

    # ══════════════ M4-CL31-03（INJ-02 主 / INJ-03 补） ══════════════
    def judge_recovery(tag, with_fidelity):
        ee = raw["runs"][tag]
        crs = [r for r in ee["child_runs"] if r["status"] != "running"]
        r0 = crs[-1] if crs else None
        ex = r0["node_executions"] if r0 else []
        o = j(r0["outputs"]) if r0 else {}
        udl = (o.get("user_delivery") or "").strip()
        outc = o.get("delivery_outcome")
        a = (o.get("artifact") or "").strip()
        n_rec = sum(1 for x in ex if x["node_id"] == "recovery_llm")
        n_skill = sum(1 for x in ex if x["node_id"] == "skill_llm")
        L = lcs_len(udl, a)
        cc = {}
        cc["①"] = "PASS" if any(x["node_id"] == "recovery_llm" and x["status"] == "succeeded"
                                for x in ex) else "FAIL"
        cc["②"] = "PASS" if n_rec == 1 else "FAIL"
        cc["③"] = "PASS" if n_skill == 1 else "FAIL"
        cc["④"] = "PASS" if udl else "FAIL"
        lk = leaks_in(udl)
        cc["⑤"] = "PASS" if not lk else "FAIL"
        cc["⑥"] = "PASS" if (a and L < 0.60 * len(a) and len(udl) < 0.80 * len(a)) else "FAIL"
        rets_ = j(o.get("returns_json") or "[]") if isinstance(o.get("returns_json"), str) else []
        try:
            rets_ = json.loads(o.get("returns_json") or "[]")
        except Exception:
            rets_ = []
        cc["⑨"] = "PASS" if (any((r.get("parse_status") == "RECOVERED_ONCE") for r in rets_)
                             and (o.get("raw_preserved") or "").strip()) else "FAIL"
        cc["⑩"] = "PASS" if outc == "DELIVERED_AFTER_RECOVERY" else "FAIL"
        det = {"run_id": r0["run_id"] if r0 else None, "run_status": r0["status"] if r0 else None,
               "recovery_llm_exec": n_rec, "skill_llm_exec": n_skill,
               "user_delivery_length": len(udl), "artifact_length": len(a),
               "lcs": L, "lcs_ratio": round(L / len(a), 4) if a else None,
               "len_ratio": round(len(udl) / len(a), 4) if a else None,
               "delivery_outcome": outc, "leaks": lk, "user_delivery": udl,
               "raw_preserved_length": len((o.get("raw_preserved") or ""))}
        if with_fidelity:
            rep, missing = must_report(udl)
            src = art + "\n" + raw["frozen_input_sha256"].get(tag, "")
            # 事实回查：冻结 artifact ∪ 冻结注入输入
            import importlib.util as iu
            sp = iu.spec_from_file_location(
                "fx", os.path.join(ROOT, "decision-chain/workflows/DIYU_M4_DETERMINISTIC_PROBE_v0.1.py"))
            fx = iu.module_from_spec(sp); sp.loader.exec_module(fx)
            haystack = art + "\n" + fx.CT_M3
            facts = extract_facts(udl)
            unsupported = [f for f in facts if f not in haystack]
            cc["⑦"] = "PASS" if not unsupported else "FAIL"
            cc["⑧"] = "PASS" if not missing else "FAIL"
            det["must_preserve"] = rep
            det["must_preserve_missing"] = missing
            det["facts_in_user_delivery"] = facts
            det["unsupported_facts"] = unsupported
            det["unsupported_fact_count"] = len(unsupported)
        det["conjuncts"] = cc
        det["verdict"] = "PASS" if all(v == "PASS" for v in cc.values()) else "FAIL"
        return det

    d02 = judge_recovery("INJ-02", True)
    d03 = judge_recovery("INJ-03", False)
    V["criteria"]["M4-CL31-03"] = {
        "primary_INJ-02": d02, "supplementary_INJ-03": d03,
        "verdict": "PASS" if d02["verdict"] == "PASS" and d03["verdict"] == "PASS" else "FAIL"}

    V["criteria"]["M4-CL31-04"] = {
        "input": "INJ-02（冻结 artifact + 运行前冻结必保清单）",
        "conjuncts": {
            "①": "PASS" if not [k for k in d02.get("must_preserve_missing", ["x"]) if k.startswith("CORE")] else "FAIL",
            "②": "PASS" if not [k for k in d02.get("must_preserve_missing", ["x"]) if k.startswith("COND")] else "FAIL",
            "③": "PASS" if not [k for k in d02.get("must_preserve_missing", ["x"]) if k.startswith("NEXT")] else "FAIL",
            "④": d02["conjuncts"].get("⑦", "FAIL"),
            "⑤": d02["conjuncts"].get("⑤", "FAIL"),
        },
        "must_preserve": d02.get("must_preserve"),
        "missing": d02.get("must_preserve_missing"),
        "unsupported_facts": d02.get("unsupported_facts"),
        "scope_limit": "只验证本次新增的恢复投影；不对其他五个能力施加事后补写的要素清单",
    }
    V["criteria"]["M4-CL31-04"]["verdict"] = (
        "PASS" if all(v == "PASS" for v in V["criteria"]["M4-CL31-04"]["conjuncts"].values()) else "FAIL")

    V["findings"].append({
        "id": "M4-FND-027",
        "type": "执行侧器械缺陷（我自己的），非产品缺陷",
        "what": "我在 v0.5 §3 CL31-02⑤ 把 Prompt 的「没有重跑其他专业能力」重述为「skill_llm 执行总数 <= 1」。",
        "why_wrong": ("① 比 Prompt 的 ACCEPTANCE 原文严；② 与同一条的⑥（明确允许基础设施重试且必须留痕）"
                      "在有重试时自相矛盾——重试必然产生第二次子应用运行，skill_llm 总数必然为 2。"),
        "disposition": ("按 A1 跨域不覆盖：ACCEPTANCE 由 Prompt 冻结，v0.5 只是判据载体，"
                        "载体与合同冲突时以合同为准。因此⑤按 Prompt 原文判定，"
                        "同时把严格总数读法的结果一并登记，不隐藏、不挑选。"),
        "escalate_to": "规划侧（判据措辞归验收判据域，执行侧不得自行改判）",
    })

    json.dump(V, open(os.path.join(OUT, "CL31_02_03_04_VERDICT.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=2, sort_keys=True)
    for k in ("M4-CL31-02", "M4-CL31-03", "M4-CL31-04"):
        print("%s = %s" % (k, V["criteria"][k]["verdict"]))
    print("\nCL31-02 合取:", json.dumps({k: v for k, v in V["criteria"]["M4-CL31-02"]["conjuncts"].items()
                                       if not k.endswith("_note")}, ensure_ascii=False))
    print("  ⑤ 两种读法:", json.dumps(V["criteria"]["M4-CL31-02"]["conjuncts"]["⑤_note"], ensure_ascii=False))
    print("  user_delivery(%d字):" % V["criteria"]["M4-CL31-02"]["user_delivery_length"],
          V["criteria"]["M4-CL31-02"]["user_delivery"][:120].replace("\n", " "))
    print("\nCL31-03 INJ-02:", json.dumps(d02["conjuncts"], ensure_ascii=False))
    print("  ", json.dumps({k: d02.get(k) for k in
          ("run_status", "recovery_llm_exec", "skill_llm_exec", "user_delivery_length",
           "artifact_length", "lcs_ratio", "len_ratio", "delivery_outcome",
           "unsupported_fact_count", "must_preserve_missing")}, ensure_ascii=False))
    print("CL31-03 INJ-03:", json.dumps(d03["conjuncts"], ensure_ascii=False))
    print("  ", json.dumps({k: d03.get(k) for k in
          ("run_status", "recovery_llm_exec", "skill_llm_exec", "user_delivery_length",
           "artifact_length", "lcs_ratio", "len_ratio", "delivery_outcome")}, ensure_ascii=False))
    print("\nCL31-04 合取:", json.dumps(V["criteria"]["M4-CL31-04"]["conjuncts"], ensure_ascii=False),
          "missing =", V["criteria"]["M4-CL31-04"]["missing"])


if __name__ == "__main__":
    main()
