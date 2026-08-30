#!/usr/bin/env python3
"""Code-node body for the one authorized inline-artifact successor."""

from __future__ import annotations

INLINE_CODE = r'''
import json
import re

CONFIRM_RE = re.compile(r"确认可用|已确认|已经确认|已定稿|已经拍完|已经实现|现有成片|现有素材")
PLACEHOLDER_RE = re.compile(r"待补|稍后补|略|占位|TBD|TODO|\.\.\.|……", re.I)
SCRIPT_RE = re.compile(
    r"(?:口播稿|脚本|逐字稿)\s*[：:]\s*(?:[“\"](?P<quoted>.+?)[”\"]|```(?:\w+)?\s*(?P<fenced>.+?)```)",
    re.S,
)
CONTENT_RE = re.compile(
    r"(?:实际成片内容是|已有成片内容|已有内容正文|素材说明)\s*[：:]\s*(?P<body>.+?)"
    r"(?=(?:\n|。)?(?:商品当前|本次发|请基于))",
    re.S,
)
ORIGIN_RE = re.compile(r"拍摄|录制|访谈|生成|实拍|素材剪|已有素材")
PROMISE_RE = re.compile(r"不承诺|承诺|只展示|只说|不写价格|不写折扣|不做保证")


def _norm(value):
    return re.sub(r"\s+", " ", value or "").strip()


def _fp(value):
    result = 0xcbf29ce484222325
    for byte in (value or "").encode("utf-8"):
        result = ((result ^ byte) * 0x100000001b3) & 0xFFFFFFFFFFFFFFFF
    return "%016x" % result


def _sentences(value):
    return [_norm(item) for item in re.findall(r"[^。！？\n]+[。！？]?", value or "")
            if _norm(item)]


def _clauses(value):
    return [_norm(item) for item in re.split(r"[，,；;。！？\n]", value or "")
            if _norm(item)]


def _companions(request, body, target, task_key):
    values = {}
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
        promises = [item for item in _sentences(body) if PROMISE_RE.search(item)]
        if promises:
            values["content.promise"] = promises[0]
    return json.dumps({
        "task_key": task_key,
        "source_kind": "USER_INLINE_CONFIRMED",
        "source_turn": "CURRENT_TURN",
        "artifact_bfp": _fp(_norm(body)),
        "values": values,
    }, ensure_ascii=False, sort_keys=True)


def _result(status, reason, question="", body="", artifact_type="", upstream="",
            task_key="", target=""):
    compact = _norm(body)
    ready = status == "INLINE_READY"
    return {
        "inline_status": status,
        "inline_reason": reason,
        "inline_question": question,
        "inline_body": body,
        "inline_artifact_type": artifact_type,
        "inline_upstream_capability": upstream,
        "inline_source_kind": "USER_INLINE_CONFIRMED" if ready else "",
        "inline_source_turn": "CURRENT_TURN" if ready else "",
        "inline_task_key": task_key if ready else "",
        "inline_fp": _fp(compact[:256]) if ready else "",
        "inline_bfp": _fp(compact) if ready else "",
        "inline_companion_json": "",
    }


def main(user_request, target_capability, task_key, correction_status):
    request = user_request or ""
    target = (target_capability or "").strip()
    task = (task_key or "").strip()
    if (correction_status or "").strip() == "REJECTED":
        return _result("INLINE_REJECTED", "CORRECTION_REJECTED",
                       "这次修改还没有准确对应到当前任务，请先确认要修改的是哪一项。")

    body = ""
    artifact_type = ""
    upstream = ""
    if target == "PRODUCTION_DIRECTOR":
        matches = list(SCRIPT_RE.finditer(request))
        if not matches:
            return _result("NONE", "NO_INLINE_CARRIER")
        if len(matches) > 1:
            return _result("INLINE_REJECTED", "AMBIGUOUS",
                           "我看到了不止一份脚本。请明确这次要采用其中哪一份完整定稿。")
        body = matches[0].group("quoted") or matches[0].group("fenced") or ""
        artifact_type = "SCRIPT_OR_EQUIVALENT_BEATS"
        upstream = "CREATIVE_SCRIPT"
    elif target == "PUBLISHING_PACKAGING":
        matches = list(CONTENT_RE.finditer(request))
        if not matches:
            return _result("NONE", "NO_INLINE_CARRIER")
        if len(matches) > 1:
            return _result("INLINE_REJECTED", "AMBIGUOUS",
                           "我看到了不止一份已经完成的内容。请明确这次要包装哪一份。")
        body = matches[0].group("body") or ""
        artifact_type = "CONTENT_BODY_OR_BEATS"
        upstream = "USER_REALIZED_CONTENT"
    else:
        return _result("NONE", "TARGET_HAS_NO_INLINE_SLOT")

    if not task:
        return _result("INLINE_REJECTED", "TASK_SCOPE_MISSING",
                       "这份内容还没有对应到当前任务。请先确认它属于哪一条内容。")
    if not CONFIRM_RE.search(request):
        return _result("INLINE_REJECTED", "NOT_CONFIRMED",
                       "我看到了内容正文，但还不能确认它已经定稿。请只确认这是不是本次可直接采用的版本。")
    compact = _norm(body)
    if len(compact) < 40 or PLACEHOLDER_RE.search(compact):
        return _result("INLINE_REJECTED", "BODY_INCOMPLETE",
                       "这份内容还不完整。请补齐一份完整定稿后，我再继续。")
    result = _result("INLINE_READY", "CURRENT_TURN_USER_CONFIRMED", body=body.strip(),
                     artifact_type=artifact_type, upstream=upstream, task_key=task,
                     target=target)
    result["inline_companion_json"] = _companions(request, body.strip(), target, task)
    return result
'''
