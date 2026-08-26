#!/usr/bin/env python3
"""确定性正负夹具：逐条断言，不通过就红。"""
import json, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))), "tools/gate_v12"))
from gate_main import main as gate
from assemble_main import main as assemble
from post_gate_main import main as post_gate

SPEC = json.load(open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                  "fixtures/gate_fixtures_v12.json"), encoding="utf-8"))

def check(exp, rep, res):
    fails = []
    def L(k): return len(rep.get(k, []) or [])
    if "gate_status" in exp and rep["gate_status"] != exp["gate_status"]:
        fails.append(f"gate_status={rep['gate_status']} 期望 {exp['gate_status']}")
    if "gate_status_prefix" in exp and not rep["gate_status"].startswith(exp["gate_status_prefix"]):
        fails.append(f"gate_status={rep['gate_status']} 期望前缀 {exp['gate_status_prefix']}")
    if "needs_fix" in exp and res["needs_fix"] != exp["needs_fix"]:
        fails.append(f"needs_fix={res['needs_fix']} 期望 {exp['needs_fix']}")
    if "contains_hard_reason" in exp and not any(
            exp["contains_hard_reason"] in r for r in rep.get("hard_fail_reasons", [])):
        fails.append(f"hard_fail_reasons 未含 {exp['contains_hard_reason']}: {rep.get('hard_fail_reasons')}")
    for key, field in (("min_missing_items","missing_items"), ("min_leaks","internal_leaks"),
                       ("min_hollow","hollow_items"), ("min_unanchored","unanchored_items"),
                       ("min_overlap","overlapping_anchors"), ("min_decorative","decorative_items"),
                       ("min_manifest_contradiction","manifest_contradiction")):
        if key in exp and L(field) < exp[key]:
            fails.append(f"{field} 只有 {L(field)} 条，期望 ≥{exp[key]}：{rep.get(field)}")
    if exp.get("has_input_contradiction") and not rep.get("input_contradiction"):
        fails.append("期望命中 input_contradiction，实际没有")
    if exp.get("has_fail_closed_block") and not rep.get("trigger_fail_closed_blocks"):
        fails.append("期望命中 fail-closed 阻断，实际没有")
    for k, t in (("trigger_effective_conflict","conflict"), ("trigger_effective_anchor","anchor"),
                 ("trigger_effective_explore","explore"), ("trigger_effective_notask","notask")):
        if k in exp and rep["triggers_effective"].get(t) is not exp[k]:
            fails.append(f"triggers_effective[{t}]={rep['triggers_effective'].get(t)} 期望 {exp[k]}")
    if "audit_block_missing" in exp and rep.get("audit_block_missing") is not exp["audit_block_missing"]:
        fails.append(f"audit_block_missing={rep.get('audit_block_missing')} 期望 {exp['audit_block_missing']}")
    if "min_inapplicable" in exp and L("inapplicable_items") < exp["min_inapplicable"]:
        fails.append(f"inapplicable_items 只有 {L('inapplicable_items')} 条，期望 ≥{exp['min_inapplicable']}")
    if exp.get("has_input_contradiction") is False and rep.get("input_contradiction"):
        fails.append(f"不该命中 input_contradiction，实际命中：{rep['input_contradiction']}")
    if "min_render" in exp and L("render_applied") < exp["min_render"]:
        fails.append(f"render_applied 只有 {L('render_applied')} 条，期望 ≥{exp['min_render']}：{rep.get('render_applied')}")
    if "continuity_status" in exp and rep["continuity"]["status"] != exp["continuity_status"]:
        fails.append(f"continuity={rep['continuity']['status']} 期望 {exp['continuity_status']}")
    return fails

npass = nfail = 0
for c in SPEC["cases"]:
    res = gate(c["draft"], c["manifest"], c["account_context"])
    rep = json.loads(res["gate_report"])
    fails = check(c["expect"], rep, res)
    # 端到端：硬失败绝不进补齐；CLEAN 必须逐字返回原稿
    asm = assemble(res["body"], "", res["needs_fix"], res["gate_status"], res["draft_audit"])
    if res["gate_status"].startswith("HARD_FAIL") and asm["path"] != "hard_fail_no_repair":
        fails.append(f"硬失败却走了 {asm['path']}")
    if res["gate_status"] == "CLEAN" and asm["final_text"] != res["body"]:
        fails.append("CLEAN 时最终正文与原稿不逐字相同")
    import shared_checks as SC
    if SC.LABEL_SHELL.search(asm["final_text"]):
        fails.append("成稿里仍有方括号标签壳 —— 渲染层没兜住")
    for _p in SC.REF_DISPLAY:
        if _p in asm["final_text"]:
            fails.append(f"成稿里仍有参考文件路径 {_p}")
    pg = post_gate(asm["final_text"], c["manifest"], res["gate_report"],
                   c["account_context"], asm["final_audit"], asm["path"])
    pgr = json.loads(pg["post_gate_report"])
    if "projection_mode" in c["expect"]:
        from projection_v12 import project
        from shared_checks import _parse_slots
        prev = _parse_slots(c["account_context"]).get("standing_cycle_baseline", "")
        _, prec = project(prev, asm["final_text"], pg["cycle_state_carry"], c["account_context"])
        if prec["mode"] != c["expect"]["projection_mode"]:
            fails.append(f"投影模式 {prec['mode']} 期望 {c['expect']['projection_mode']}")
    if res["gate_status"].startswith("HARD_FAIL"):
        if pg["gaps_closed"] != "no":
            fails.append("硬失败却 gaps_closed=yes —— 这正是 G6 的失效")
        if pg["cycle_state_carry"] != "REJECTED_KEEP_PREVIOUS":
            fails.append(f"硬失败却 carry={pg['cycle_state_carry']}")
        if "（系统说明）" not in pg["operating_judgment_final"]:
            fails.append("硬失败没有对用户显式说明")
    if c["expect"].get("gate_status") == "CLEAN" and pg["gaps_closed"] != "yes":
        fails.append(f"正向夹具复检未通过：{pgr['carry_reject_reason']}")
    if fails:
        nfail += 1
        print(f"FAIL {c['case_id']}  ({c['why']})")
        for f in fails: print("      -", f)
    else:
        npass += 1
        print(f"pass {c['case_id']:38s} status={rep['gate_status']:28s} "
              f"cont={rep['continuity']['status']:14s} carry={pg['cycle_state_carry']}")
print(f"\n{npass} passed, {nfail} failed, {len(SPEC['cases'])} total")
sys.exit(1 if nfail else 0)
