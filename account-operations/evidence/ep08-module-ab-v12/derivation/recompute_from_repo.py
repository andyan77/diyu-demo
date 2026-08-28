#!/usr/bin/env python3
"""只用仓库内材料重算 EP-08 A/B 推导，并与当轮落盘的 _unblinded_results_v3.json 比对。

为什么有这个脚本：ADDENDUM_002 §2.3 第 5 步承诺"推导代码与全部判定原文一并落盘供独立重算"，
第 6 轮独立收口 Reviewer 的观察 O-4 指出仓库里当时只有 sha256 与 mtime，没有原文与脚本。
ADDENDUM_003 §6 把材料补齐；本脚本证明补齐之后**真的能从仓库单独重算**。

用法：python3 recompute_from_repo.py      （零参数，路径全部相对本文件）
推导规则逐字照抄 unblind_v3.py 的 derive()，冻结于 ADDENDUM_002 §2.4/§2.5，本文件不改一处。
"""
import json, os, statistics

HERE = os.path.dirname(os.path.abspath(__file__))
EVID = os.path.dirname(HERE)
VERDICTS = os.path.join(EVID, "verdicts_raw")
SEALED = os.path.join(HERE, "_SEALED_AB_MAPPING_v3.json")
RECORDED = os.path.join(EVID, "_unblinded_results_v3.json")

DIMS = ["运营判断", "周期组合", "产能取舍", "实验设计", "反馈判断", "内容任务质量", "共同质量底线"]
GATES = ["目标忠实", "事实", "权限", "风险", "当前任务必要条件"]
GRADE = {"优秀": 4, "合格": 3, "勉强": 2, "不足": 1, "缺失": 0}


def med(vals):
    vals = [v for v in vals if v is not None]
    return statistics.median(vals) if vals else None


def main():
    files = sorted(f for f in os.listdir(VERDICTS)
                   if f.startswith("verdict_") and f.endswith(".json"))
    sealed = json.load(open(SEALED, encoding="utf-8"))

    cells = {}
    for f in files:
        v = json.load(open(os.path.join(VERDICTS, f), encoding="utf-8"))
        m = sealed["mapping"][v["unit"]]
        cells.setdefault((m["case_id"], m["arm"]), []).append(v)

    cases = sorted({c for c, _ in cells})
    grades, gate_marks = {}, {}
    for (c, a), vs in cells.items():
        for d in DIMS:
            raw = [GRADE.get(x["dimensions"].get(d, {}).get("grade")) for x in vs]
            na = sum(1 for x in vs if x["dimensions"].get(d, {}).get("grade") == "不适用")
            grades[(c, a, d)] = None if na > len(vs) / 2 else med(raw)
        for g in GATES:
            deg = sum(1 for x in vs if x["hard_gates"].get(g, {}).get("verdict") == "实质退化")
            gate_marks[(c, a, g)] = deg > len(vs) / 2

    def derive(chal, base):
        dim_out, gain_dims = {}, []
        for d in DIMS:
            pairs = [(grades.get((c, chal, d)), grades.get((c, base, d))) for c in cases]
            usable = [(x, y) for x, y in pairs if x is not None and y is not None]
            if len(usable) < len(cases) / 2:
                dim_out[d] = "不适用"
                continue
            chal_win = sum(1 for x, y in usable if x > y)
            base_win = sum(1 for x, y in usable if y > x)
            base_big = any(y - x >= 2 for x, y in usable)
            if base_big or base_win >= 2:
                dim_out[d] = f"{base}优且实质"
            elif chal_win >= 2 and not base_big:
                dim_out[d] = f"{chal}优"
                gain_dims.append(d)
            else:
                dim_out[d] = "相当"
        applicable = [d for d in DIMS if dim_out[d] != "不适用"]
        substantive_loss = [d for d in applicable if dim_out[d].endswith("优且实质")]
        overall = (len(gain_dims) > len(applicable) / 2) and not substantive_loss
        hard = [g for g in GATES
                if any(gate_marks.get((c, chal, g)) and not gate_marks.get((c, base, g))
                       for c in cases)]
        return {"dimensions": dim_out, "applicable": applicable,
                "gain_dimensions": gain_dims, "substantive_loss_dimensions": substantive_loss,
                "overall_gain": overall, "hard_gate_degradations": hard}

    rec = json.load(open(RECORDED, encoding="utf-8"))
    report = {"verdicts_read": len(files), "cells": len(cells), "mismatches": []}

    g_now = {f"{c}|{a}|{d}": v for (c, a, d), v in grades.items()}
    for k, v in g_now.items():
        if rec["grades"].get(k) != v:
            report["mismatches"].append({"kind": "grade", "key": k,
                                         "recorded": rec["grades"].get(k), "recomputed": v})
    report["grade_cells_compared"] = len(g_now)

    m_now = {f"{c}|{a}|{g}": v for (c, a, g), v in gate_marks.items()}
    for k, v in m_now.items():
        if rec["hard_gate_marks"].get(k) != v:
            report["mismatches"].append({"kind": "hard_gate", "key": k,
                                         "recorded": rec["hard_gate_marks"].get(k), "recomputed": v})
    report["hard_gate_cells_compared"] = len(m_now)

    for pair, key in (("B_vs_A", "B_vs_A"), ("B_vs_Bprime", "B_vs_Bprime"),
                      ("B_vs_Aplus_observation_only", "B_vs_Aplus_observation_only")):
        chal, base = ("B", {"B_vs_A": "A", "B_vs_Bprime": "Bprime",
                            "B_vs_Aplus_observation_only": "Aplus"}[pair])
        d_now = derive(chal, base)
        if d_now != rec[key]:
            report["mismatches"].append({"kind": "derivation", "key": key,
                                         "recorded": rec[key], "recomputed": d_now})
        report[key] = d_now

    report["verdict"] = "IDENTICAL" if not report["mismatches"] else "MISMATCH"
    report["note"] = ("本脚本只重算推导本身。AC-01③ 的**正式等级**不由本文件决定："
                      "见 ADDENDUM_003 §4——该轮判据在结果之后被改写，按 A2 只算探索，"
                      "推导输出的 PASS 不等于正式 PASS。")
    out = os.path.join(EVID, "recompute_check.json")
    json.dump(report, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(json.dumps({k: report[k] for k in
                      ("verdicts_read", "cells", "grade_cells_compared",
                       "hard_gate_cells_compared", "verdict")}, ensure_ascii=False, indent=2))
    print("mismatches:", len(report["mismatches"]))
    print("written:", out)


if __name__ == "__main__":
    main()
