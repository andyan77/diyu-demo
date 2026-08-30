#!/usr/bin/env python3
"""Code-node sources for the TD-UAPP-24 successor candidate.

These strings execute inside Dify's Python code-node sandbox. They only operate on the
existing conversation state carrier; they do not call models, databases, or external APIs.
"""

from __future__ import annotations


CORRECTION_CODE: str = r'''
import json
import re


SCOPES = {"CONTENT_TASK", "PRODUCTION", "OPERATION", "DELIVERY"}
COMPAT = {
    "PUBLISHING_PACKAGING": ["PRODUCTION_DIRECTOR", "CREATIVE_SCRIPT"],
    "PRODUCTION_DIRECTOR": ["CREATIVE_SCRIPT"],
    "CREATIVE_SCRIPT": ["CONTENT_BRIEF"],
}
CHANGE_WORDS = ("改为", "改成", "调整为", "调整成", "变更为", "变成")
EXPLICIT_CHANGE = re.compile(
    r"(?:把)?(?P<label>[^，。；]{1,24}?)从(?P<old>[^，。；]{1,16}?)"
    r"(?:改为|改成|调整为|调整成|变更为|变成)(?P<new>[^，。；]{1,16})"
)


def _norm(value):
    return re.sub(r"\s+", " ", value or "").strip()


def _patch(value):
    if isinstance(value, dict):
        return value
    if isinstance(value, str) and value.strip():
        try:
            parsed = json.loads(value)
            return parsed if isinstance(parsed, dict) else {}
        except Exception:
            return {}
    return {}


def _change_parts(old, new):
    old, new = _norm(old), _norm(new)
    prefix = 0
    while prefix < min(len(old), len(new)) and old[prefix] == new[prefix]:
        prefix += 1
    suffix = 0
    while (suffix < len(old) - prefix and suffix < len(new) - prefix
           and old[len(old) - suffix - 1] == new[len(new) - suffix - 1]):
        suffix += 1
    old_end = len(old) - suffix if suffix else len(old)
    new_end = len(new) - suffix if suffix else len(new)
    old_part, new_part = old[prefix:old_end], new[prefix:new_end]
    # 一人→两人这类变化的真正替换单元包含共同量词；扩一位只用于复算，
    # 不绑定任何字段名或当前案例。
    if old_part and new_part and len(old_part) < 2 and suffix:
        old_part += old[old_end:old_end + 1]
        new_part += new[new_end:new_end + 1]
    preserved = len(old) - max(0, len(old_part))
    ratio = float(preserved) / float(max(1, len(old)))
    return old_part, new_part, ratio


def _quote_supports(quote, old_part, new_part):
    text = _norm(quote)
    return bool(text and old_part and new_part and old_part in text and new_part in text
                and any(word in text for word in CHANGE_WORDS))


def _proposal_deltas(action_patch, fields, user_request):
    patch = _patch(action_patch)
    proposals = patch.get("correction_deltas") or []
    if not isinstance(proposals, list):
        return [], ["PROPOSALS_NOT_LIST"]
    accepted, rejected, seen = [], [], set()
    for index, item in enumerate(proposals):
        if not isinstance(item, dict):
            rejected.append("ITEM_%d_NOT_OBJECT" % index)
            continue
        cid = _norm(item.get("field_id"))
        new_value = _norm(item.get("new_value"))
        quote = _norm(item.get("source_quote"))
        old = fields.get(cid)
        if cid in seen:
            rejected.append("DUPLICATE_FIELD:%s" % cid)
            continue
        seen.add(cid)
        if not isinstance(old, dict) or old.get("sc") not in SCOPES:
            rejected.append("UNKNOWN_FIELD:%s" % cid)
            continue
        if not quote or quote not in (user_request or ""):
            rejected.append("QUOTE_NOT_VERBATIM:%s" % cid)
            continue
        old_value = _norm(old.get("v"))
        if not old_value or not new_value or old_value == new_value:
            rejected.append("NO_VALUE_CHANGE:%s" % cid)
            continue
        old_part, new_part, preserved_ratio = _change_parts(old_value, new_value)
        if preserved_ratio < 0.6 or not _quote_supports(quote, old_part, new_part):
            rejected.append("UNSUPPORTED_TRANSFORM:%s" % cid)
            continue
        accepted.append({
            "field_id": cid,
            "old_value": old_value,
            "new_value": new_value,
            "old_part": old_part,
            "new_part": new_part,
            "source_quote": quote,
            "derived": False,
        })
    return accepted, rejected


def _deterministic_fallback(fields, user_request):
    match = EXPLICIT_CHANGE.search(user_request or "")
    if not match:
        return []
    old_part = _norm(match.group("old"))
    new_part = _norm(match.group("new"))
    quote = match.group(0)
    if not old_part or not new_part or old_part == new_part:
        return []
    groups = {}
    for cid, record in fields.items():
        if not isinstance(record, dict) or record.get("sc") not in SCOPES:
            continue
        value = _norm(record.get("v"))
        if old_part not in value:
            continue
        key = (record.get("sc"), record.get("kind"), record.get("ref"))
        groups.setdefault(key, []).append((cid, record, value))
    if not groups:
        return []
    ordered = sorted(groups.items(), key=lambda pair: len(pair[1]), reverse=True)
    if len(ordered) > 1 and len(ordered[0][1]) == len(ordered[1][1]):
        return []
    # A single unrelated occurrence is too weak to infer a canonical field identity.
    if len(ordered[0][1]) < 2:
        return []
    out = []
    for cid, _record, value in ordered[0][1]:
        out.append({
            "field_id": cid,
            "old_value": value,
            "new_value": value.replace(old_part, new_part),
            "old_part": old_part,
            "new_part": new_part,
            "source_quote": quote,
            "derived": True,
        })
    return out


def _expand_same_provenance(fields, deltas):
    out = list(deltas)
    covered = {item["field_id"] for item in out}
    for delta in list(deltas):
        base = fields.get(delta["field_id"]) or {}
        for cid, record in fields.items():
            if cid in covered or not isinstance(record, dict):
                continue
            if (record.get("sc"), record.get("kind"), record.get("ref")) != (
                    base.get("sc"), base.get("kind"), base.get("ref")):
                continue
            value = _norm(record.get("v"))
            if not delta["old_part"] or delta["old_part"] not in value:
                continue
            out.append({
                "field_id": cid,
                "old_value": value,
                "new_value": value.replace(delta["old_part"], delta["new_part"]),
                "old_part": delta["old_part"],
                "new_part": delta["new_part"],
                "source_quote": delta["source_quote"],
                "derived": True,
            })
            covered.add(cid)
    return out


def _backfill_lineage(artifacts, task_key):
    filled = []
    for record in artifacts:
        if record.get("upstream_fp") or record.get("cap") not in COMPAT:
            continue
        turn = int(record.get("turn") or 0)
        chosen = None
        for upstream_cap in COMPAT[record.get("cap")]:
            candidates = [
                candidate for candidate in artifacts
                if candidate.get("cap") == upstream_cap
                and int(candidate.get("turn") or 0) < turn
                and candidate.get("accepted") is True
                and int(candidate.get("accepted_turn") or 0) <= turn
                and (candidate.get("task_key") or task_key) == task_key
            ]
            if not candidates:
                continue
            latest_turn = max(int(candidate.get("turn") or 0) for candidate in candidates)
            latest = [candidate for candidate in candidates
                      if int(candidate.get("turn") or 0) == latest_turn]
            if len(latest) == 1:
                chosen = latest[0]
            break
        if chosen is not None:
            record["upstream_fp"] = chosen.get("fp")
            record["lineage_kind"] = "DETERMINISTIC_BACKFILL_V1"
            filled.append("%s@t%s->%s" % (
                record.get("cap"), record.get("turn"), chosen.get("fp")))
    return filled


def _apply_stale(artifacts, changed):
    direct, transitive = [], []
    affected_fps = set()
    for record in artifacts:
        if record.get("stale"):
            continue
        hit = [cid for cid in changed if cid in (record.get("dep") or {})]
        if hit:
            record["stale"] = True
            record["stale_reason"] = "FIELD_CHANGED:" + ",".join(sorted(hit))
            direct.append("%s@t%s:%s" % (
                record.get("cap"), record.get("turn"), record.get("fp")))
            affected_fps.add(record.get("fp"))
    changed_any = True
    while changed_any:
        changed_any = False
        for record in artifacts:
            upstream_fp = record.get("upstream_fp")
            if not upstream_fp or upstream_fp not in affected_fps:
                continue
            reason = "UPSTREAM_STALE:" + upstream_fp
            additional = record.setdefault("additional_stale_reasons", [])
            if reason not in additional and record.get("stale_reason") != reason:
                additional.append(reason)
            identity = "%s@t%s:%s" % (
                record.get("cap"), record.get("turn"), record.get("fp"))
            if identity not in transitive:
                transitive.append(identity)
            if not record.get("stale"):
                record["stale"] = True
                record["stale_reason"] = reason
            if record.get("fp") not in affected_fps:
                affected_fps.add(record.get("fp"))
                changed_any = True
    return direct, transitive


def _block_message(deltas, target_capability):
    quote = (deltas[0].get("source_quote") if deltas else "") or "你刚才说的修改"
    target = {
        "PUBLISHING_PACKAGING": "标题和封面",
        "PRODUCTION_DIRECTOR": "制作方案",
        "CREATIVE_SCRIPT": "口播稿",
    }.get(target_capability, "下一步内容")
    return ("你刚才说的“%s”已经记下。这个变化会影响刚才的制作方案，"
            "所以我先不继续用旧方案做%s。需要先更新制作方案，之后才能可靠继续；"
            "其他已经确认且不受影响的内容会保留。") % (quote, target)


def main(prev_state_json, action_patch, user_request, task_key, target_capability):
    try:
        state = json.loads(prev_state_json) if (prev_state_json or "").strip() else {}
    except Exception:
        state = {}
    if not isinstance(state, dict) or state.get("task_key") != (task_key or "").strip():
        return {
            "corrected_state_json": prev_state_json or "{}",
            "correction_delta_json": "[]",
            "correction_status": "REJECTED",
            "corrected_fields": "",
            "direct_stale": "",
            "transitive_stale": "",
            "lineage_backfilled": "",
            "block_message": "这次修改没有和当前任务对上，我先不继续使用旧方案。",
            "correction_note": "TASK_IDENTITY_MISMATCH",
        }
    fields = state.get("fields") if isinstance(state.get("fields"), dict) else {}
    artifacts = state.get("artifacts") if isinstance(state.get("artifacts"), list) else []
    deltas, rejected = _proposal_deltas(action_patch, fields, user_request or "")
    if not deltas:
        deltas = _deterministic_fallback(fields, user_request or "")
    deltas = _expand_same_provenance(fields, deltas)
    if not deltas:
        explicit = bool(EXPLICIT_CHANGE.search(user_request or ""))
        status = "REJECTED" if explicit or rejected else "NONE"
        return {
            "corrected_state_json": json.dumps(state, ensure_ascii=False),
            "correction_delta_json": "[]",
            "correction_status": status,
            "corrected_fields": "",
            "direct_stale": "",
            "transitive_stale": "",
            "lineage_backfilled": "",
            "block_message": ("我听到你在修改已经确认的内容，但还不能准确对应到当前记录，"
                              "所以先不继续使用旧方案。") if status == "REJECTED" else "",
            "correction_note": ",".join(rejected) or "NO_CORRECTION",
        }

    rev = int(state.get("rev") or 0) + 1
    for record in fields.values():
        if isinstance(record, dict) and record.get("lvl") == "A":
            record["lvl"] = "B"
    applied = []
    for delta in deltas:
        cid = delta["field_id"]
        old = fields.get(cid)
        if not isinstance(old, dict) or _norm(old.get("v")) == _norm(delta["new_value"]):
            continue
        fields[cid] = {
            "v": delta["new_value"],
            "lvl": "A",
            "kind": "USER_UTTERANCE",
            "ref": "TURN%d.user_request" % rev,
            "sc": old.get("sc"),
            "frev": int(old.get("frev") or 1) + 1,
            "origin_turn": rev,
        }
        applied.append({
            "field_id": cid,
            "new_value": delta["new_value"],
            "source_kind": "USER_UTTERANCE",
            "source_ref": "TURN%d.user_request" % rev,
            "scope": old.get("sc"),
            "turn": rev,
            "task_identity": state.get("task_key"),
            "source_quote": delta["source_quote"],
            "derived_same_provenance": bool(delta.get("derived")),
        })
    if not applied:
        return {
            "corrected_state_json": json.dumps(state, ensure_ascii=False),
            "correction_delta_json": "[]",
            "correction_status": "NONE",
            "corrected_fields": "",
            "direct_stale": "",
            "transitive_stale": "",
            "lineage_backfilled": "",
            "block_message": "",
            "correction_note": "SAME_VALUE",
        }

    filled = _backfill_lineage(artifacts, state.get("task_key"))
    changed = [item["field_id"] for item in applied]
    direct, transitive = _apply_stale(artifacts, changed)
    state["rev"] = rev
    event = {
        "t": rev,
        "kind": "USER_CORRECTION",
        "fields": changed,
        "source_ref": "TURN%d.user_request" % rev,
        "direct_stale": direct,
        "transitive_stale": transitive,
        "lineage_backfilled": filled,
    }
    state["events"] = (state.get("events") or [])[-59:] + [event]
    return {
        "corrected_state_json": json.dumps(state, ensure_ascii=False),
        "correction_delta_json": json.dumps(applied, ensure_ascii=False),
        "correction_status": "APPLIED",
        "corrected_fields": ",".join(changed),
        "direct_stale": ",".join(direct),
        "transitive_stale": ",".join(transitive),
        "lineage_backfilled": ",".join(filled),
        "block_message": _block_message(applied, target_capability),
        "correction_note": "APPLIED:%d" % len(applied),
    }
'''


BLOCK_CODE: str = r'''
def main(correction_status, block_message, selection_question, gaps_text):
    message = (block_message or "").strip()
    if not message:
        question = (selection_question or "").strip()
        if question:
            message = question
        else:
            message = ("这一步先停一下：刚才可用的上游内容现在不能继续使用。"
                       "先把受影响的内容更新好，其他已经确认的部分会保留。")
    return {"final_text": message,
            "block_reason": (correction_status or "NO_LEGAL_UPSTREAM"),
            "precise_gap": (gaps_text or "").strip()}
'''
