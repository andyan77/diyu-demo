#!/usr/bin/env python3
"""Deterministic node bodies for the bounded CAP-06 semantic-contract repair."""

from __future__ import annotations

INLINE_COMPANION_FUNCTION = r'''
PLATFORM_RE = re.compile(r"(?:本次|这次|准备)?发(?:到|在)?\s*(小红书|抖音|视频号)")
NATURAL_CTA_RE = re.compile(r"自然\s*CTA|自然引导语|自然互动")
COMMERCIAL_EXCLUSION_RE = re.compile(
    r"不(?:写|做|包含|承诺)[^。！？]*(?:价格|折扣)[^。！？]*(?:站外|购买|成交|下单)"
)


def _realized_payoff(body):
    for clause in _clauses(body):
        if re.search(r"展示|演示|讲解|说明|示范", clause) and not re.search(r"不承诺|保证", clause):
            return clause
    for clause in _clauses(body):
        if not re.search(r"不承诺|保证", clause):
            return clause
    return ""


def _companions(request, body, target, task_key):
    values = {}
    derived_values = {}
    if target == "PRODUCTION_DIRECTOR":
        outside = request.replace(body, "", 1)
        origins = [item for item in _clauses(outside)
                   if ORIGIN_RE.search(item) and not item.startswith("请")]
        promises = [item for item in _sentences(body) if PROMISE_RE.search(item)]
        if origins:
            values["content.origin_mode"] = origins[0]
        if promises:
            values["content.promise"] = promises[0]
    elif target == "PUBLISHING_PACKAGING":
        payoff = _realized_payoff(body)
        platform_match = PLATFORM_RE.search(request)
        cta_match = NATURAL_CTA_RE.search(request)
        if payoff:
            values["content.promise"] = payoff
        if platform_match:
            values["delivery.platform"] = platform_match.group(1)
        if cta_match:
            values["cta.contract"] = cta_match.group(0)
        if cta_match and COMMERCIAL_EXCLUSION_RE.search(request):
            derived_values["cta.level"] = {
                "value": "LOW_RISK_INTERACTION",
                "source_excerpt": cta_match.group(0),
                "derivation_rule": "NATURAL_CTA_WITH_COMMERCIAL_EXCLUSIONS",
            }
    return json.dumps({
        "task_key": task_key,
        "source_kind": "USER_INLINE_CONFIRMED",
        "source_turn": "CURRENT_TURN",
        "artifact_bfp": _fp(_norm(body)),
        "request_bfp": _fp(_norm(request)),
        "values": values,
        "derived_values": derived_values,
    }, ensure_ascii=False, sort_keys=True)
'''


PP_REQUIRED = (
    'REQUIRED = ["content_body_or_beats", "content_promise", '
    '"explicit_non_promise", "facts_registered", "asset_publish_permission"]'
)


PP_CTA_RESOLUTION = r'''    cta_requested = (
        _find_scalar(blob, "cta_level") or _find_scalar(blob, "cta_contract") or ""
    ).upper()
    if not cta_requested:
        cta_requested = "NO_CTA"
    elif cta_requested not in CTA_LEVELS:
        cta_requested = "NO_CTA"

    cta_level = cta_requested
    cta_policy_status = "AUTHORIZED"
    cta_policy_note = "按已声明授权边界执行"
    if cta_requested == "KNOWN_BUT_NOT_AUTHORIZED":
        cta_level = "NO_CTA"
        cta_policy_status = "HELD_NOT_AUTHORIZED"
        cta_policy_note = "CTA 未获授权；非 CTA 包装继续，任何引导动作都不生成"
    elif cta_requested == "HIGH_RISK":
        cta_level = "NO_CTA"
        cta_policy_status = "REJECTED_HIGH_RISK"
        cta_policy_note = "高风险 CTA 不在本次授权内；非 CTA 包装继续"
    elif cta_requested == "BUSINESS_HANDOFF":
        handoff_required = ["cta_target", "cta_reception_path", "cta_authorized_facts"]
        handoff_missing = [key for key in handoff_required if not _present(blob, key)[0]]
        if handoff_missing:
            cta_level = "NO_CTA"
            cta_policy_status = "HELD_MISSING_HANDOFF_CONTRACT"
            cta_policy_note = (
                "经营承接缺少 %s；只停 CTA，非 CTA 包装继续" % ", ".join(handoff_missing)
            )
'''

