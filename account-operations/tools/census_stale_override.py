#!/usr/bin/env python3
"""对 stale_value_override 做全量普查：61 例样本里每一次命中逐条列出。

为什么要单独做这件事：REBIND_004 §2.2 给 G-2 冻结了「误报族与漏检族两族都跑、
两个数字都写进记录」的方法义务，**G-4 没有对应条款**。后果就是这份普查的结果 ——
本轮夹具里 G-4 的旧值覆盖族（S1–S4）误报 0，而真实运行里 12 次命中 11 次是误报。
夹具是我自己造的句子，真实正文不是。这正是 G-2 当初栽的同一个跟头换了个位置。

判定每一次命中是真是假，靠的是同一条冻结判据自己的作用域声明（§2.3）：
「这一条只挡『用旧值压当轮输入』，不挡『解释为什么产能会变』。」
凡是正文里的数量与槽位**一致**、或根本不是发布量、或是模型在正确复述三值分离的，
都不属于「用旧值压当轮输入」。
"""
import json, glob, os, re, sys

WT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(WT, "account-operations/evidence/ep19-gate-v13-defects")

# 每一次命中的判读，逐条写死，附理由；判读依据是 §2.3 自己的作用域声明。
RULING = {
    "B02-2-blank-account":      ("误报", "「完成三件事」被读成 1 条发布量；句中无发布量主张"),
    "B02-4-blocking-dependency":("误报", "正文断言 3条，与槽位 3条/周**一致**；仅因未在同句重复单位而未命中豁免"),
    "B03-1-objective-01":       ("误报", "被拦的正是三值分离原句「你期望一周三条，账号基线产能一周三条，当前实际可投入也是一周三条」"),
    "B03-4-objective-04":       ("误报", "「三条都在当前产能内」与槽位一致"),
    "B03-8-objective-08":       ("误报", "「本周三条按目标分工」与槽位一致"),
    "B04-N1-all-in-one":        ("误报", "拦的是模型**拒绝**用一条覆盖四目标——正是该例 Oracle 要求的行为"),
    "B07-P-daily-three":        ("误报", "拦的是「21 条怎么分配…当前实际产能只能支撑 3 条」，"
                                        "即 Founder 第 3 条逐字授权的等价换算"),
    "B09-2-medium-signal-good-fit":("误报", "三值分离原句「三个数一致，不需要削产能」"),
    "B10-3-conflicting":        ("误报", "「两条反馈」被读成 2 条发布量"),
    "E03":                      ("误报", "「不为凑三条把本周压缩成一条内容里同时讲…」是反面陈述，非当前产能主张"),
    "E04":                      ("真阳性", "槽位 actual_capacity 逐字 3条/周，正文断言「本周实际产能只有一条」并据此压任务"),
    "E06":                      ("误报", "主语锚裸词「目标」命中「不承载其他目标」；句中无发布量主张"),
}


def main():
    rows, total = [], 0
    for pat in ("account-operations/evidence/ep06b-runtime-behavior-v13/*.json",
                "account-operations/evidence/ep07-longitudinal-v13/E*.json"):
        for p in sorted(glob.glob(os.path.join(WT, pat))):
            if "/_" in p:
                continue
            total += 1
            d = json.load(open(p, encoding="utf-8"))
            o = (d.get("raw_response_body") or {}).get("data", {}).get("outputs") or {}
            gr = o.get("gate_report")
            if isinstance(gr, str):
                gr = json.loads(gr)
            sv = (gr or {}).get("stale_value_override") or []
            if not sv:
                continue
            name = os.path.basename(p)[:-5]
            ruling, why = RULING.get(name, ("未判读", ""))
            rows.append({"case": name, "fired": sv, "ruling": ruling, "reason": why,
                         "delivery_rejected": bool(
                             (json.loads(o["post_gate_report"]) if isinstance(o.get("post_gate_report"), str)
                              else o.get("post_gate_report") or {}).get("carry_blocking"))})

    fp = [r for r in rows if r["ruling"] == "误报"]
    tp = [r for r in rows if r["ruling"] == "真阳性"]
    report = {
        "what": "stale_value_override（G-4）在真实运行上的全量普查",
        "sample": {"behavior_cases": 49, "longitudinal_steps": 12, "total": total},
        "fired": len(rows), "false_positives": len(fp), "true_positives": len(tp),
        "false_positive_rate": f"{len(fp)}/{len(rows)}",
        "fixture_said": "夹具旧值覆盖族 S1–S4：误报 0 —— 夹具句子是执行侧自己造的，真实正文不是",
        "frozen_scope_used_to_rule":
            "REBIND_004 §2.3：「这一条只挡『用旧值压当轮输入』，不挡『解释为什么产能会变』。」",
        "what_the_false_positives_hit":
            "误报集中打在冻结判据**要求**的行为上：三值分离原句（B03-1 / B09-2 / B02-4）、"
            "Founder 第 3 条逐字授权的等价换算（B07-P）、该例 Oracle 要求的拒绝合并（B04-N1）。"
            "为保护 AC-06 而建的检查，几乎只在正确的 AC-06 行为上开火。",
        "method_gap":
            "REBIND_004 §2.2 只给 G-2 冻结了「误报与漏检两个数字都要报」的方法义务，"
            "G-4 没有对应条款。这是 G-2 当初栽的同一个跟头换了个位置："
            "在自己造的样本上量误报，等于自己给自己出题。",
        "rows": rows,
    }
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "STALE_OVERRIDE_CENSUS.json"), "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"样本 {total}，命中 {len(rows)}，误报 {len(fp)}，真阳性 {len(tp)}")
    for r in rows:
        print(f"  {r['ruling']:4}  {r['case']:32} 拒收={r['delivery_rejected']}  {r['reason'][:60]}")


if __name__ == "__main__":
    main()
