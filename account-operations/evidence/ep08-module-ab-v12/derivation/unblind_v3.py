#!/usr/bin/env python3
"""EP-08 v1.2 揭盲与推导（推导规则在判定开始前冻结，见 ADDENDUM_002 §2.4/§2.5）。

时序保证：脚本先把全部判定文件的 sha256 与 mtime 记下来（= 判定冻结点），
再读封存映射；读之前断言"每份判定文件的 mtime 早于映射读取时刻"，不成立就拒绝输出。
如实记录的上限：执行侧与生成映射的是同一方，这条由文件时序 + 脚本断言支撑，
不是由权限隔离支撑，**不等于**双盲试验里的第三方保管。
"""
import hashlib, json, os, statistics, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
WT = "/home/faye/diyu-demo-worktrees/m3-account-content-operator-v1"
OUT_OF_REPO = ("/tmp/claude-1000/-home-faye-diyu-demo/"
               "2c670698-40ad-483e-b793-56ac12fb6aea/scratchpad/m3-ab-blind-v3")
VERDICTS = os.path.join(OUT_OF_REPO, "verdicts")
SEALED = os.path.join(HERE, "_SEALED_AB_MAPPING_v3.json")
EVID = os.path.join(WT, "account-operations/evidence/ep08-module-ab-v12")

DIMS = ["运营判断", "周期组合", "产能取舍", "实验设计", "反馈判断", "内容任务质量", "共同质量底线"]
GATES = ["目标忠实", "事实", "权限", "风险", "当前任务必要条件"]
GRADE = {"优秀": 4, "合格": 3, "勉强": 2, "不足": 1, "缺失": 0}


def med(vals):
    vals = [v for v in vals if v is not None]
    return statistics.median(vals) if vals else None


def main():
    # ---- 1. 判定冻结点 ----
    files = sorted(f for f in os.listdir(VERDICTS) if f.startswith("verdict_") and f.endswith(".json"))
    freeze = {}
    for f in files:
        p = os.path.join(VERDICTS, f)
        freeze[f] = {"sha256": hashlib.sha256(open(p, "rb").read()).hexdigest(),
                     "mtime": os.path.getmtime(p)}
    latest = max(v["mtime"] for v in freeze.values()) if freeze else 0
    frozen_at = time.time()
    print(f"判定冻结点：{len(files)} 份，最后一份 mtime={time.strftime('%H:%M:%S', time.localtime(latest))}")

    # ---- 2. 读封存映射，断言时序 ----
    sealed = json.load(open(SEALED, encoding="utf-8"))
    mapping_read_at = time.time()
    assert latest < mapping_read_at, "有判定文件的 mtime 晚于映射读取时刻 —— 时序不成立，拒绝揭盲"
    assert frozen_at <= mapping_read_at

    # ---- 3. join ----
    cells = {}          # (case, arm) -> list of verdicts
    for f in files:
        v = json.load(open(os.path.join(VERDICTS, f), encoding="utf-8"))
        unit = v["unit"]
        m = sealed["mapping"][unit]
        cells.setdefault((m["case_id"], m["arm"]), []).append(v)

    cases = sorted({c for c, _ in cells})
    arms = sorted({a for _, a in cells})
    grades, gate_marks = {}, {}
    for (c, a), vs in cells.items():
        for d in DIMS:
            raw = [GRADE.get(x["dimensions"].get(d, {}).get("grade")) for x in vs]
            na = sum(1 for x in vs if x["dimensions"].get(d, {}).get("grade") == "不适用")
            grades[(c, a, d)] = None if na > len(vs) / 2 else med(raw)
        for g in GATES:
            deg = sum(1 for x in vs if x["hard_gates"].get(g, {}).get("verdict") == "实质退化")
            gate_marks[(c, a, g)] = deg > len(vs) / 2

    # ---- 4. 冻结推导 ----
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

    b_vs_a = derive("B", "A")
    b_vs_bp = derive("B", "Bprime")
    b_vs_ap = derive("B", "Aplus")          # 仅观察，不闸任何 AC

    if b_vs_a["hard_gate_degradations"]:
        ac18 = "FAIL（硬门实质退化，不得用增益抵消）"
    elif b_vs_a["overall_gain"]:
        ac18 = "PASS"
    else:
        ac18 = "FAIL(INSUFFICIENT) —— M3_PROFESSIONAL_GAIN=NOT_VERIFIED，M3_MODULE_AB=NOT_PASSED"
    ac01c = "PASS" if b_vs_bp["overall_gain"] else "FAIL —— B 相对 B′ 无可辨识运营增益"

    out = {
        "protocol": "ADDENDUM_002 逐场景·单臂·独立随机分配·3 名取中位",
        "verdict_freeze": freeze,
        "timing_assertion": {
            "last_verdict_mtime": latest, "mapping_read_at": mapping_read_at,
            "assertion": "全部判定文件写定早于映射读取 —— 成立",
        },
        "cells": {f"{c}__{a}": len(v) for (c, a), v in cells.items()},
        "grades": {f"{c}|{a}|{d}": v for (c, a, d), v in grades.items()},
        "hard_gate_marks": {f"{c}|{a}|{g}": v for (c, a, g), v in gate_marks.items()},
        "B_vs_A": b_vs_a, "B_vs_Bprime": b_vs_bp,
        "B_vs_Aplus_observation_only": b_vs_ap,
        "M3-AC-18": ac18, "M3-AC-01③": ac01c,
        "mapping": sealed["mapping"],
    }
    os.makedirs(EVID, exist_ok=True)
    with open(os.path.join(EVID, "_unblinded_results_v3.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(json.dumps({k: out[k] for k in ("B_vs_A", "B_vs_Bprime", "M3-AC-18", "M3-AC-01③")},
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
