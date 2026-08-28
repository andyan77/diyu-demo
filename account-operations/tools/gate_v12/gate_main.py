import json
import re

from shared_checks import *  # noqa: F401,F403


# ---------------------------------------------------------------- 入口

def main(draft: str, manifest: str, account_context: str) -> dict:
    src = draft or ""
    body, audit = split_audit(src)
    body, render_applied, shell_fams = render_body(body)   # 外观层由代码还原，不退给模型
    slots = _parse_slots(account_context)

    hard = []
    min_fails = check_min_output(body)
    required_lines = []
    if min_fails:
        hard.append("MIN_OUTPUT")

    # 审计块缺失不再算硬失败：正文可能是好的，缺的是**可核验性**。
    # 补齐节点手上有正文与由代码算好的审计骨架，补一段审计块不是无中生有。
    audit_missing = audit is None
    if audit_missing:
        self_rep, anchors, machine = {k: None for k in TRIGGER_ITEMS}, {}, {}
    else:
        self_rep, anchors, machine = parse_audit(audit)

    computed = compute_triggers_from_input(slots)
    eff, blocks, notes = resolve_triggers(computed, self_rep, body, shell_fams)

    missing, unanchored, hollow, decorative, overlap, inapplicable, mostly_na = check_items(eff, anchors, body)
    leaks = check_leaks(body)
    contra_in, contra_in_adv = check_input_contradiction(slots, body)
    loaded, notloaded, contra_man, man_present, man_echo = check_manifest(manifest, body, machine)
    base_obj = extract_baseline_objects(slots)
    cont = check_continuity(base_obj, body)

    for it in list(ALWAYS_ITEMS) + [x for k, (_, items) in TRIGGER_ITEMS.items()
                                    if eff.get(k) for x in items]:
        required_lines.append(f"{it} :: <正文里承载这一项的那句原话，逐字复制>")

    repairable = bool(missing or unanchored or hollow or decorative or overlap
                      or leaks or contra_in or contra_man or audit_missing)

    trig_line = ";".join(f"{cn}={'是' if eff.get(k) else '否'}"
                         for k, (cn, _) in TRIGGER_ITEMS.items())
    if hard:
        gate_status = "HARD_FAIL_" + "+".join(hard)
        needs_fix = "no"          # 硬失败绝不进补齐：补齐节点不许无中生有写交付物
    elif repairable:
        gate_status = "NEEDS_FIX"
        needs_fix = "yes"
    else:
        gate_status = "CLEAN"
        needs_fix = "no"

    report = {
        "gate_version": "v1.2",
        "gate_status": gate_status,
        "hard_fail_reasons": min_fails,
        "audit_block_missing": audit_missing,
        "shell_families_detected": shell_fams,
        "triggers_computed_from_input": computed,
        "triggers_self_reported": self_rep,
        "triggers_effective": eff,
        "trigger_fail_closed_blocks": blocks,
        "trigger_notes": notes,
        "missing_items": missing,
        "unanchored_items": unanchored,
        "hollow_items": hollow,
        "decorative_items": decorative,
        "overlapping_anchors": overlap,
        "inapplicable_items": inapplicable,
        "family_mostly_inapplicable": mostly_na,
        "internal_leaks": leaks,
        "input_contradiction": contra_in,
        "input_contradiction_advisory": contra_in_adv,
        "manifest_present": man_present,
        "manifest_loaded": loaded,
        "manifest_not_loaded": notloaded,
        "manifest_contradiction": contra_man,
        "manifest_machine_lines": machine,
        "manifest_echo_note": man_echo,
        "baseline_objects": base_obj,
        "continuity": cont,
        "audit_anchors": anchors,
        "render_applied": render_applied,
        "body_chars": len(_nows(body)),
    }
    return {"gate_report": json.dumps(report, ensure_ascii=False),
            "needs_fix": needs_fix,
            "gate_status": gate_status,
            "baseline_objects": json.dumps(base_obj, ensure_ascii=False),
            "draft_audit": audit or "",
            "required_audit_lines": "<<AUDIT>>\n" + trig_line + "\n"
                                    + "\n".join(required_lines) + "\n<<END_AUDIT>>",
            "body": body}
