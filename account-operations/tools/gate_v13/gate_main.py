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
    audit_missing = audit is None
    if audit_missing:
        self_rep, anchors, machine, pos_lines = {k: None for k in TRIGGER_ITEMS}, {}, {}, []
    else:
        self_rep, anchors, machine, pos_lines = parse_audit(audit)

    # ---- 持续位：结构对结构，全程不经过散文（G-3） ----
    input_pos = parse_standing_positions(slots)
    decls, bad_pos_lines = parse_positions_declaration(pos_lines)

    computed = compute_triggers_from_input(slots)
    # 结构事实压过自报：模型自己声明了一个 kind=探索 的新持续位，探索六项就必答。
    # 这一层不看任何措辞，因此不会被"换个说法"绕过——G-2 的正面挡板。
    struct_explore = [d["id"] for d in decls if d["is_new"] and d["kind"] == "exploration"]
    if struct_explore:
        computed["explore"] = True

    eff, blocks, notes = resolve_triggers(computed, self_rep, body, shell_fams)
    if struct_explore:
        notes.append("探索提案: 审计块声明了新建探索位 " + "、".join(struct_explore)
                     + " ⇒ 结构事实判定为是（不看措辞）")

    (missing, unanchored, hollow, decorative, overlap,
     inapplicable, mostly_na, item_spans) = check_items(eff, anchors, body)
    pos = check_positions(input_pos, decls, bad_pos_lines, body, used_spans=item_spans)

    leaks = check_leaks(body)
    contra_in, contra_in_adv = check_input_contradiction(slots, body)
    stale_override, stale_advisory = check_stale_value_override(slots, body)   # G-4 v2
    loaded, notloaded, contra_man, man_present, man_echo = check_manifest(manifest, body, machine)

    for it in list(ALWAYS_ITEMS) + [x for k, (_, items) in TRIGGER_ITEMS.items()
                                    if eff.get(k) for x in items]:
        required_lines.append(f"{it} :: <正文里承载这一项的那句原话，逐字复制>")
    for pid in input_pos.get("positions", []):
        required_lines.append(f"POS :: {pid['id']} :: 继续|处置|替换 :: <正文里承载这一处置的那句原话>")

    repairable = bool(missing or unanchored or hollow or decorative or overlap
                      or leaks or contra_in or contra_man or audit_missing
                      or pos["blocking"] or stale_override)

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
        "gate_version": "v1.3",
        "gate_status": gate_status,
        "hard_fail_reasons": min_fails,
        "audit_block_missing": audit_missing,
        "shell_families_detected": shell_fams,
        "triggers_computed_from_input": computed,
        "triggers_self_reported": self_rep,
        "triggers_effective": eff,
        "trigger_fail_closed_blocks": blocks,
        "trigger_notes": notes,
        "structural_exploration_positions": struct_explore,
        "missing_items": missing,
        "unanchored_items": unanchored,
        "hollow_items": hollow,
        "decorative_items": decorative,
        "overlapping_anchors": overlap,
        "inapplicable_items": inapplicable,
        "family_mostly_inapplicable": mostly_na,
        "positions": pos,
        "internal_leaks": leaks,
        "input_contradiction": contra_in,
        "input_contradiction_advisory": contra_in_adv,
        "stale_value_override": stale_override,
        "stale_value_override_advisory": stale_advisory,
        "draft_pos_lines": list(pos_lines or []),
        "draft_declared_position_ids": [d["id"] for d in decls],
        "draft_new_position_ids": [d["id"] for d in decls if d["is_new"]],
        "manifest_present": man_present,
        "manifest_loaded": loaded,
        "manifest_not_loaded": notloaded,
        "manifest_contradiction": contra_man,
        "manifest_machine_lines": machine,
        "manifest_echo_note": man_echo,
        "audit_anchors": anchors,
        "blanket_carry_in_draft": has_blanket_carry(body),
        "render_applied": render_applied,
        "body_chars": len(_nows(body)),
    }
    return {"gate_report": json.dumps(report, ensure_ascii=False),
            "needs_fix": needs_fix,
            "gate_status": gate_status,
            "positions_report": json.dumps(pos, ensure_ascii=False),
            "draft_audit": audit or "",
            "required_audit_lines": "<<AUDIT>>\n" + trig_line + "\n"
                                    + "\n".join(required_lines) + "\n<<END_AUDIT>>",
            "body": body}
