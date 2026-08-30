#!/usr/bin/env python3
"""Code-node bodies for the UAPP current-turn inline-artifact seam."""

from __future__ import annotations

INLINE_CODE = r'''
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


def _norm(value):
    return re.sub(r"\s+", " ", value or "").strip()


def _fp(value):
    result = 0xcbf29ce484222325
    for byte in (value or "").encode("utf-8"):
        result = ((result ^ byte) * 0x100000001b3) & 0xFFFFFFFFFFFFFFFF
    return "%016x" % result


def _result(status, reason, question="", body="", artifact_type="", upstream="",
            task_key=""):
    compact = _norm(body)
    return {
        "inline_status": status,
        "inline_reason": reason,
        "inline_question": question,
        "inline_body": body,
        "inline_artifact_type": artifact_type,
        "inline_upstream_capability": upstream,
        "inline_source_kind": "USER_INLINE_CONFIRMED" if status == "INLINE_READY" else "",
        "inline_source_turn": "CURRENT_TURN" if status == "INLINE_READY" else "",
        "inline_task_key": task_key if status == "INLINE_READY" else "",
        "inline_fp": _fp(compact[:256]) if status == "INLINE_READY" else "",
        "inline_bfp": _fp(compact) if status == "INLINE_READY" else "",
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
    return _result("INLINE_READY", "CURRENT_TURN_USER_CONFIRMED", body=body.strip(),
                   artifact_type=artifact_type, upstream=upstream, task_key=task)
'''


BLOCK_CODE = r'''
import re

REPLACEMENTS = {
    "PRODUCTION_DIRECTOR": "拍摄方案",
    "PUBLISHING_PACKAGING": "发布包装",
    "CREATIVE_SCRIPT": "脚本",
    "CONTENT_BRIEF": "内容制作依据",
    "script_or_equivalent_beats": "完整脚本",
    "content_body_or_beats": "完整内容",
}


def _scrub(value):
    text = value or ""
    for internal, natural in REPLACEMENTS.items():
        text = text.replace(internal, natural)
    text = re.sub(r"\b[A-Z][A-Z0-9_]{2,}\b", "", text)
    text = re.sub(r"\b[a-z][a-z0-9]*(?:_[a-z0-9]+)+\b", "", text)
    text = re.sub(r"[ \t]{2,}", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def main(correction_status, block_message, selection_question, gaps_text):
    message = (block_message or "").strip() or (selection_question or "").strip()
    if not message:
        message = ("这一步先停一下：刚才可用的上游内容现在不能继续使用。"
                   "先把受影响的内容更新好，其他已经确认的部分会保留。")
    return {
        "final_text": _scrub(message),
        "block_reason": (correction_status or "NO_LEGAL_UPSTREAM"),
        "precise_gap": (gaps_text or "").strip(),
    }
'''
