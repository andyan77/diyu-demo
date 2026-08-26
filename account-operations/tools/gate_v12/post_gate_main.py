import json
import re

from shared_checks import *  # noqa: F401,F403


# ---------------------------------------------------------------- 入口

def main(final_text: str, manifest: str, prior_report: str,
         account_context: str, final_audit: str, gate_path: str) -> dict:
    """在**装配之后**的最终正文上重跑同一套确定性检查，并做出周期状态承载决定。

    v1.1 的复检复用了模型自报的触发标志，因此第一道闸门错了它一定跟着错。
    v1.2 复检不复用自报——触发生效值来自输入侧计算，与第一道闸门同源、可独立复算。
    """
    body = final_text or ""
    body, _render, shell_fams = render_body(body)
    try:
        prior = json.loads(prior_report or "{}")
    except Exception:  # noqa: BLE001
        prior = {}
    slots = _parse_slots(account_context)

    eff = prior.get("triggers_effective") or {}
    if not eff:                       # 第一道闸门的报告不可解析时不许静默放行
        eff = {k: True for k in TRIGGER_ITEMS}

    # 独立复算：自己解析审计块，不复用第一道闸门的锚定行。
    _self, anchors, _mach = parse_audit(final_audit if (final_audit or "").strip() else None)
    audit_missing_after_repair = (gate_path == "gate_repaired"
                                  and not (final_audit or "").strip())
    if audit_missing_after_repair:
        # 补齐节点改了正文却没重发审计块。不一刀切判死：回落到首轮锚定行，
        # 指得回新正文的仍然算数，指不回的如实计为 unanchored。
        anchors = (prior.get("audit_anchors") or {})
        _mach = {}
    min_fails = check_min_output(body)
    leaks = check_leaks(body)
    contra_in, contra_in_adv = check_input_contradiction(slots, body)
    loaded, notloaded, contra_man, man_present, man_echo = check_manifest(manifest, body, _mach)
    base_obj = prior.get("baseline_objects") or extract_baseline_objects(slots)
    cont = check_continuity(base_obj, body)

    # 锚定行的实质检查在最终正文上重跑一遍（引用必须仍然逐字在正文里）
    missing, unanchored, hollow, decorative, overlap, inapplicable, mostly_na = check_items(eff, anchors, body)

    hard = []
    if min_fails:
        hard.append("MIN_OUTPUT")
    if str(prior.get("gate_status", "")).startswith("HARD_FAIL"):
        hard.append("FIRST_PASS_" + str(prior.get("gate_status")).replace("HARD_FAIL_", ""))
    if not (final_audit or "").strip() and gate_path != "hard_fail_no_repair":
        audit_missing_after_repair = True

    gaps_closed = not (hard or leaks or contra_in or contra_man
                       or missing or unanchored
                       or hollow or decorative or overlap)

    reasons = []
    if hard:
        reasons.append("本轮没有产出可用的运营判断（" + "；".join(min_fails or ["上一道闸门已判硬失败"]) + "）")
    if cont.get("status") == "MERGED":
        reasons.append("上一有效基线里的 " + "、".join(cont["not_restated"])
                       + " 本轮未涉及 —— 投影按连续性义务逐字保留它们，不整体覆盖")
    if contra_in:
        reasons.append("正文与本轮输入自相矛盾：" + "；".join(contra_in))
    if leaks:
        reasons.append("交付里残留内部字段：" + "；".join(leaks[:4]))
    if contra_man:
        reasons.append("与本轮参考文件清单矛盾：" + "；".join(contra_man[:3]))
    if audit_missing_after_repair:
        reasons.append("补齐节点改了正文却没有重发配套的审计块，已回落用首轮锚点复核")
    if missing or unanchored or hollow or decorative or overlap:
        reasons.append("必填项仍未落实：缺 %d 项、指不回正文 %d 项、空洞 %d 项、装饰 %d 项、引用重叠 %d 项"
                       % (len(missing), len(unanchored), len(hollow),
                          len(decorative), len(overlap)))

    # 两件事分开，别混成一个：
    #   gaps_closed —— 必填项闸门有没有完全闭合（含"补齐后锚点还能不能复核"）；
    #   carry       —— 这份交付够不够格成为**当前有效周期判断**。
    # 后者只看交付本身是不是错的或丢了东西（零产出、丢基线对象、与输入矛盾、与清单矛盾、
    # 残留内部字段）。锚点复核不上是"没核到"，不是"交付错了"——按 A3，
    # 让有证据不受影响的项失效同样是错。
    carry_blocking = bool(hard or contra_in or contra_man or leaks)
    carry = "REJECTED_KEEP_PREVIOUS" if carry_blocking else "ACCEPTABLE_AS_NEW_BASELINE"
    if carry_blocking and not reasons:
        reasons.append("交付本身不合格，具体见 post_gate_report")

    # 显式失败：不静默继续，也不假装合规。用户可见的说明是自然语言，不含内部字段。
    notice = ""
    if hard:
        if base_obj.get("baseline_present"):
            notice = ("（系统说明）本轮没有产出可用的运营判断，上面的内容不足以作为本周期的新判断。"
                      "上一轮仍然有效的周期基线保持不变，本次不替换它。")
        else:
            notice = ("（系统说明）本轮没有产出可用的运营判断，本账号目前也还没有被接受的周期基线。"
                      "请补齐所缺的输入后重新发起。")
    # 未重述的对象由投影逐字保留，用户不需要看到这条系统内务，正文不追加噪声。

    out_text = (body + ("\n\n" + notice if notice else ""))

    report = {
        "post_gate_version": "v1.2",
        "first_pass_gate_status": prior.get("gate_status"),
        "hard_fail_reasons": min_fails,
        "still_leaks": leaks,
        "still_input_contradiction": contra_in,
        "still_input_contradiction_advisory": contra_in_adv,
        "still_manifest_contradiction": contra_man,
        "still_missing": missing, "still_unanchored": unanchored,
        "still_hollow": hollow, "still_decorative": decorative,
        "still_overlapping": overlap,
        "still_inapplicable": inapplicable,
        "still_family_mostly_inapplicable": mostly_na,
        "audit_missing_after_repair": audit_missing_after_repair,
        "continuity": cont,
        "triggers_effective_used": eff,
        "gaps_closed": gaps_closed,
        "carry_blocking": carry_blocking,
        "cycle_state_carry": carry,
        "carry_reject_reason": reasons,
        "control_marker_leaked": ("<<AUDIT>>" in body or "<<TRIGGERS>>" in body),
        "think_leaked": "<think>" in body,
        "body_chars": len(_nows(body)),
    }
    return {"post_gate_report": json.dumps(report, ensure_ascii=False),
            "gaps_closed": "yes" if gaps_closed else "no",
            "cycle_state_carry": carry,
            "carry_reject_reason": json.dumps(reasons, ensure_ascii=False),
            "operating_judgment_final": out_text}
