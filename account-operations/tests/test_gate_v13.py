#!/usr/bin/env python3
"""v1.3 六族确定性夹具：逐条断言，并且**误报与漏检两个数字都报**。

只报一个数字的收紧，本轮不接受——REBIND_004 §2.2 把它冻结成了方法义务。
上一轮把探索触发收紧成"动作性措辞"，收紧后量了误报（0/70）、没量漏检，
那次方法漏直接造成 G-2：一次完整的探索提案整句逃逸。
"""
import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
sys.path.insert(0, os.path.join(_ROOT, "tools/gate_v13"))

from gate_main import main as gate                      # noqa: E402
from assemble_main import main as assemble              # noqa: E402
from post_gate_main import main as post_gate            # noqa: E402
from projection_v13 import project                      # noqa: E402
import shared_checks as SC                              # noqa: E402

SPEC = json.load(open(os.path.join(_ROOT, "fixtures/gate_fixtures_v13.json"), encoding="utf-8"))

def expectation_polarity(exp):
    """这条用例期望闸门**响**还是**不响**——按 expect 本身判，不按族名判。

    第一版按族名统计，把「漏检族里的下界用例」（该族里故意不该响的那条）
    错算成漏检，得出 3/7 这种看不懂的数。族名是给人读的，判据得从期望里来。
    返回 True=该响、False=不该响、None=这条不参与这两个数字。
    """
    fire, quiet = [], []
    if exp.get("gate_status") == "CLEAN":
        quiet.append("gate_status=CLEAN")
    if exp.get("gate_status") == "NEEDS_FIX" or exp.get("gate_status_prefix", "").startswith("HARD_FAIL"):
        fire.append("gate_status")
    if exp.get("trigger_effective_explore") is True:
        fire.append("explore=True")
    if exp.get("trigger_effective_explore") is False:
        quiet.append("explore=False")
    for k in ("min_stale_override", "min_missing_items", "min_leaks", "min_hollow",
              "min_unanchored", "min_overlap", "min_decorative",
              "min_manifest_contradiction", "min_positions_bad_anchor"):
        if exp.get(k):
            fire.append(k)
    if exp.get("positions_unaccounted") or exp.get("positions_fabricated"):
        fire.append("positions")
    if exp.get("stale_override") == 0:
        quiet.append("stale_override=0")
    if fire and quiet:
        return None                 # 混合期望（如"探索要响、旧值不要响"）不进单一计数
    if fire:
        return True
    if quiet:
        return False
    return None


def check(exp, rep, res, pg, pgr):
    f = []
    def L(k, d=None):
        return len((d or rep).get(k, []) or [])
    pos = rep.get("positions", {})

    if "gate_status" in exp and rep["gate_status"] != exp["gate_status"]:
        f.append(f"gate_status={rep['gate_status']} 期望 {exp['gate_status']}")
    if "gate_status_prefix" in exp and not rep["gate_status"].startswith(exp["gate_status_prefix"]):
        f.append(f"gate_status={rep['gate_status']} 期望前缀 {exp['gate_status_prefix']}")
    if "needs_fix" in exp and res["needs_fix"] != exp["needs_fix"]:
        f.append(f"needs_fix={res['needs_fix']} 期望 {exp['needs_fix']}")
    if "contains_hard_reason" in exp and not any(
            exp["contains_hard_reason"] in r for r in rep.get("hard_fail_reasons", [])):
        f.append(f"hard_fail_reasons 未含 {exp['contains_hard_reason']}")
    for key, field in (("min_missing_items", "missing_items"), ("min_leaks", "internal_leaks"),
                       ("min_hollow", "hollow_items"), ("min_unanchored", "unanchored_items"),
                       ("min_overlap", "overlapping_anchors"),
                       ("min_decorative", "decorative_items"),
                       ("min_inapplicable", "inapplicable_items"),
                       ("min_render", "render_applied"),
                       ("min_manifest_contradiction", "manifest_contradiction"),
                       ("min_stale_override", "stale_value_override")):
        if key in exp and L(field) < exp[key]:
            f.append(f"{field} 只有 {L(field)} 条，期望 ≥{exp[key]}：{rep.get(field)}")
    if "stale_override" in exp and L("stale_value_override") != exp["stale_override"]:
        f.append(f"stale_value_override={rep.get('stale_value_override')} 期望 {exp['stale_override']} 条")
    if "positions_unaccounted" in exp and len(pos.get("positions_unaccounted", [])) != exp["positions_unaccounted"]:
        f.append(f"positions_unaccounted={pos.get('positions_unaccounted')} 期望 {exp['positions_unaccounted']} 个")
    if "positions_fabricated" in exp and len(pos.get("positions_fabricated", [])) != exp["positions_fabricated"]:
        f.append(f"positions_fabricated={pos.get('positions_fabricated')} 期望 {exp['positions_fabricated']} 个")
    if "min_positions_bad_anchor" in exp and len(pos.get("positions_bad_anchor", [])) < exp["min_positions_bad_anchor"]:
        f.append(f"positions_bad_anchor={pos.get('positions_bad_anchor')} 期望 ≥{exp['min_positions_bad_anchor']}")
    if exp.get("has_positions_parse_error") and not pos.get("input_parse_error"):
        f.append("期望持续位 JSON 解析报错，实际没有")
    if "min_structural_exploration" in exp and L("structural_exploration_positions") < exp["min_structural_exploration"]:
        f.append("structural_exploration_positions 少于期望")
    if exp.get("has_input_contradiction") and not rep.get("input_contradiction"):
        f.append("期望命中 input_contradiction，实际没有")
    if exp.get("has_input_contradiction") is False and rep.get("input_contradiction"):
        f.append(f"不该命中 input_contradiction：{rep['input_contradiction']}")
    if exp.get("has_fail_closed_block") and not rep.get("trigger_fail_closed_blocks"):
        f.append("期望命中 fail-closed 阻断，实际没有")
    for k, t in (("trigger_effective_conflict", "conflict"), ("trigger_effective_anchor", "anchor"),
                 ("trigger_effective_explore", "explore"), ("trigger_effective_notask", "notask")):
        if k in exp and rep["triggers_effective"].get(t) is not exp[k]:
            f.append(f"triggers_effective[{t}]={rep['triggers_effective'].get(t)} 期望 {exp[k]}")
    if "audit_block_missing" in exp and rep.get("audit_block_missing") is not exp["audit_block_missing"]:
        f.append(f"audit_block_missing={rep.get('audit_block_missing')} 期望 {exp['audit_block_missing']}")
    if "carry" in exp and pg["cycle_state_carry"] != exp["carry"]:
        f.append(f"carry={pg['cycle_state_carry']} 期望 {exp['carry']}（原因：{pgr['carry_reject_reason']}）")
    return f


def main():
    npass = nfail = 0
    fp = fn = fp_total = fn_total = 0
    fp_cases, fn_cases = [], []
    fails_detail = []
    for c in SPEC["cases"]:
        res = gate(c["draft"], c["manifest"], c["account_context"])
        rep = json.loads(res["gate_report"])
        asm = assemble(res["body"], "", res["needs_fix"], res["gate_status"], res["draft_audit"])
        pg = post_gate(asm["final_text"], c["manifest"], res["gate_report"],
                       c["account_context"], asm["final_audit"], asm["path"])
        pgr = json.loads(pg["post_gate_report"])
        f = check(c["expect"], rep, res, pg, pgr)

        # 端到端不变量（与 v12 同款，不放松）
        if res["gate_status"].startswith("HARD_FAIL"):
            if asm["path"] != "hard_fail_no_repair":
                f.append(f"硬失败却走了 {asm['path']}")
            if pg["gaps_closed"] != "no":
                f.append("硬失败却 gaps_closed=yes —— 这正是 G6 的失效")
            if pg["cycle_state_carry"] != "REJECTED_KEEP_PREVIOUS":
                f.append(f"硬失败却 carry={pg['cycle_state_carry']}")
            if "（系统说明）" not in pg["operating_judgment_final"]:
                f.append("硬失败没有对用户显式说明")
        if res["gate_status"] == "CLEAN" and asm["final_text"] != res["body"]:
            f.append("CLEAN 时最终正文与原稿不逐字相同")
        if SC.LABEL_SHELL.search(asm["final_text"]):
            f.append("成稿里仍有方括号标签壳")
        for _p in SC.REF_DISPLAY:
            if _p in asm["final_text"]:
                f.append(f"成稿里仍有参考文件路径 {_p}")
        if c["expect"].get("gate_status") == "CLEAN" and pg["gaps_closed"] != "yes":
            f.append(f"正向夹具复检未通过：{pgr['carry_reject_reason']}")

        # 投影层断言
        if "expect_projection" in c:
            slots = SC._parse_slots(c["account_context"])
            prev_pos = SC.parse_standing_positions(slots)["positions"]
            _, newpos, prec = project(slots.get("standing_cycle_baseline", ""), prev_pos,
                                      asm["final_text"], pg["cycle_state_carry"],
                                      pg["positions_final"], "TEST")
            ep = c["expect_projection"]
            if "mode" in ep and prec["mode"] != ep["mode"]:
                f.append(f"投影模式 {prec['mode']} 期望 {ep['mode']}")
            if "positions_after" in ep and prec["positions_after"] != ep["positions_after"]:
                f.append(f"投影后持续位 {prec['positions_after']} 期望 {ep['positions_after']}")

        # 误报 / 漏检两个数字：按期望极性统计，全部 48 条都参与
        pol = expectation_polarity(c["expect"])
        fired = bool(rep["gate_status"] != "CLEAN"
                     or rep["triggers_effective"].get("explore")
                     or rep.get("stale_value_override"))
        if pol is False:
            fp_total += 1
            if fired:
                fp += 1
                fp_cases.append(c["case_id"])
        elif pol is True:
            fn_total += 1
            if not fired:
                fn += 1
                fn_cases.append(c["case_id"])

        if f:
            nfail += 1
            fails_detail.append((c["case_id"], c["why"], f))
            print(f"FAIL {c['case_id']:36s} [{c['family']}]")
            for x in f:
                print("      -", x)
        else:
            npass += 1
            print(f"pass {c['case_id']:36s} [{c['family']:8s}] {rep['gate_status']:10s} "
                  f"carry={pg['cycle_state_carry']}")

    print()
    print(f"{npass} passed, {nfail} failed, {len(SPEC['cases'])} total")
    print(f"误报（不该命中却命中）: {fp}/{fp_total}" + (f"  {fp_cases}" if fp_cases else ""))
    print(f"漏检（该命中却没命中）: {fn}/{fn_total}" + (f"  {fn_cases}" if fn_cases else ""))
    print(f"（另有 {len(SPEC['cases']) - fp_total - fn_total} 条期望是混合的，不进这两个数字）")
    print("两个数字都在这里，缺一不可 —— 只报误报正是 G-2 的成因。")
    return 1 if nfail else 0


if __name__ == "__main__":
    sys.exit(main())
