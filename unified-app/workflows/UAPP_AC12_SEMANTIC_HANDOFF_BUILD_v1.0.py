#!/usr/bin/env python3
"""Build the bounded AC-12 semantic-handoff successor (zero model calls)."""

from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
from types import ModuleType
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
BASE_BUILDER_PATH = ROOT / "unified-app/workflows/UAPP_S5_FRESH_FINAL_BUILD_v1.0.py"
APP_ID = "dbb14eec-a935-445c-9764-280c8fd3375b"
BASE_GRAPH_MD5 = "3ac6d9187f27e0f656417de119155480"


def load_module(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


BASE = load_module("uapp_ac12_base_builder", BASE_BUILDER_PATH)

EXTRA_HELPERS = r'''

# AC-12 successor: extract only a directly stated viewer outcome.  Product,
# audience, pain point, or “make content” alone cannot satisfy this predicate.
_OUTCOME_LABEL = re.compile(
    r"(?:希望|想让|希望让|想要让).{0,14}(?:看完|读完|听完|看后|读后|听后|知道|明白|理解|学会|掌握|看清)"
)
_OUTCOME_NATURAL = re.compile(
    r"(?:我)?(?:希望|想让|希望让|想要让)(?:她|他|观众|用户|大家|人)?"
    r"(?:看完|读完|听完|看后|读后|听后)?(?:能)?"
    r"(?:知道|明白|理解|学会|掌握|看清)([^。！？!?\n]+)"
)


def _clean_user_value(value):
    value = _norm(value).strip()
    value = value.strip(chr(34)).strip("'").strip("“”‘’「」")
    return value.rstrip("。！？!?").strip()


def _user_stated_viewer_outcome(user_query):
    """Return only a user-written viewer outcome, preserving the value wording."""
    raw = user_query or ""
    for line in raw.splitlines():
        if "：" not in line and ":" not in line:
            continue
        key, value = re.split(r"[：:]", line, maxsplit=1)
        if not _OUTCOME_LABEL.search(key):
            continue
        value = _clean_user_value(value)
        if value:
            return value
    hit = _OUTCOME_NATURAL.search(raw)
    return _clean_user_value(hit.group(1)) if hit else ""


def _snapshot_primary_goal(snapshot):
    if not isinstance(snapshot, dict):
        return ""
    value = (snapshot.get("goal_structure") or {}).get("primary_goal")
    return _norm(value) if isinstance(value, str) else ""


def _primary_goal_is_direct_user_source(value, snapshot, user_query):
    """Shared product words cannot promote an M3/Hop inference to user intent."""
    candidate = _norm(value)
    recorded = _snapshot_primary_goal(snapshot)
    return bool(candidate and recorded and candidate == recorded and
                _supported(recorded, user_query))
'''

OLD_PROMISE_BLOCK = '''    # GAP-01 successor: a current-turn, user-supported consumption outcome is
    # a valid equivalent content promise.  Preserve the exact value and keep
    # expression subject independent; do not make any professional wording.
    gap01_promise_projection_status = "NOT_APPLICABLE"
    if cap == "CONTENT_BRIEF" and "content.promise" in gaps:
        existing_promise = found.get(SPEC["content.promise"]["k"])
        expected = found.get(SPEC["audience.expected_change"]["k"])
        if existing_promise and not _missing(existing_promise.get("v")):
            gap01_promise_projection_status = "ALREADY_PRESENT"
        elif expected:
            equivalent = _user_expected_change_as_promise(expected.get("v"), uq)
            if equivalent:
                _set(lines, found, "content.promise", equivalent)
                gaps.remove("content.promise")
                gap01_promise_projection_status = "PROJECTED_EXACT_USER_EQUIVALENT"
            else:
                gap01_promise_projection_status = "REJECTED_NOT_USER_SUPPORTED_EQUIVALENT"
        else:
            gap01_promise_projection_status = "REJECTED_EXPECTED_CHANGE_ABSENT"
'''

NEW_PROMISE_BLOCK = '''    # A user-stated viewer outcome is an exact source equivalent for both
    # identities.  This is independent of whether Hop projected expected_change.
    # An explicit content_promise remains authoritative and is never overwritten.
    gap01_promise_projection_status = "NOT_APPLICABLE"
    if cap == "CONTENT_BRIEF":
        existing_promise = found.get(SPEC["content.promise"]["k"])
        existing_expected = found.get(SPEC["audience.expected_change"]["k"])
        direct_outcome = _user_stated_viewer_outcome(uq)
        if existing_promise and not _missing(existing_promise.get("v")):
            gap01_promise_projection_status = "ALREADY_PRESENT"
        elif direct_outcome:
            if not existing_expected or _missing(existing_expected.get("v")):
                _set(lines, found, "audience.expected_change", direct_outcome)
            _set(lines, found, "content.promise", direct_outcome)
            gaps = [cid for cid in gaps
                    if cid not in ("audience.expected_change", "content.promise")]
            gap01_promise_projection_status = "PROJECTED_DIRECT_USER_VIEWER_OUTCOME"
        elif existing_expected:
            equivalent = _user_expected_change_as_promise(existing_expected.get("v"), uq)
            if equivalent:
                _set(lines, found, "content.promise", equivalent)
                gaps = [cid for cid in gaps if cid != "content.promise"]
                gap01_promise_projection_status = "PROJECTED_EXACT_USER_EQUIVALENT"
            else:
                gap01_promise_projection_status = "REJECTED_NOT_USER_SUPPORTED_EQUIVALENT"
        else:
            gap01_promise_projection_status = "REJECTED_EXPECTED_CHANGE_ABSENT"
'''

OLD_ENV_LOOP = '''    # 2. A/E 级：本轮外壳抽取
    for cid in sorted(env_vals):
        # 本轮明确纠正已经由能力中立接缝写入；Hop 的能力投影不得再改写普通字段。
        if correction_active:
            continue
        val = env_vals[cid]
        if cid in asked_prev or _supported(val, uq):
            r = offer(cid, val, "A", "USER_UTTERANCE", "TURN%d.user_request" % rev)
            if r in ("NEW", "UPDATED", "SAME"):
                answered.append(cid)
        else:
            offer(cid, val, "E", "MODEL_EXTRACTION",
                  "TURN%d.uapp_hop.%s" % (rev, cap or "-"))
'''

NEW_ENV_LOOP = '''    # 2. A/E 级：本轮外壳抽取。primary_goal has a stricter source lock:
    # lexical overlap with a product is not evidence of a user business decision.
    authority_rejected = []
    for cid in sorted(env_vals):
        val = env_vals[cid]
        if cid == "objective.primary_goal":
            if _primary_goal_is_direct_user_source(val, snap, uq):
                r = offer(cid, val, "A", "USER_UTTERANCE", "TURN%d.user_request" % rev)
                if r in ("NEW", "UPDATED", "SAME"):
                    answered.append(cid)
            else:
                # Keep M3/Hop raw evidence historically, but do not forward an
                # unsupported commercial suggestion as a user-owned canonical goal.
                _drop(lines, found, SPEC[cid]["k"])
                authority_rejected.append(cid)
            continue
        if correction_active:
            continue
        if cid in asked_prev or _supported(val, uq):
            r = offer(cid, val, "A", "USER_UTTERANCE", "TURN%d.user_request" % rev)
            if r in ("NEW", "UPDATED", "SAME"):
                answered.append(cid)
        else:
            offer(cid, val, "E", "MODEL_EXTRACTION",
                  "TURN%d.uapp_hop.%s" % (rev, cap or "-"))
'''


def patched_source(source: str) -> str:
    main_anchor = "\ndef main(prev_state_json, task_key, capability_call, gaps_text, target_capability,\n"
    if source.count(main_anchor) != 1:
        raise RuntimeError("uapp_fields main anchor mismatch")
    if source.count(OLD_PROMISE_BLOCK) != 1:
        raise RuntimeError("uapp_fields promise anchor mismatch")
    if source.count(OLD_ENV_LOOP) != 1:
        raise RuntimeError("uapp_fields authority anchor mismatch")
    source = source.replace(main_anchor, EXTRA_HELPERS + main_anchor)
    source = source.replace(OLD_PROMISE_BLOCK, NEW_PROMISE_BLOCK)
    source = source.replace(OLD_ENV_LOOP, NEW_ENV_LOOP)
    old_return = '''            "applicability_projection_status": applicability_projection_status,
            "gaps_text": merged_gaps,'''
    new_return = '''            "applicability_projection_status": applicability_projection_status,
            "semantic_projection_status": gap01_promise_projection_status,
            "authority_guard_status": ("REJECTED_UNSUPPORTED_PRIMARY_GOAL" if authority_rejected
                                       else "NO_PRIMARY_GOAL_REJECTION"),
            "gaps_text": merged_gaps,'''
    if source.count(old_return) != 1:
        raise RuntimeError("uapp_fields return anchor mismatch")
    return source.replace(old_return, new_return)


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value).encode("utf-8")).hexdigest()


def database_value(sql: str) -> str:
    return BASE.database_value(sql)


def published_graph() -> dict[str, Any]:
    return BASE.published_graph()


def patch_graph(graph: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    candidate = copy.deepcopy(graph)
    nodes = {item["id"]: item for item in candidate["nodes"]}
    base_nodes = {item["id"]: item for item in graph["nodes"]}
    if "uapp_fields" not in nodes:
        raise RuntimeError("uapp_fields absent")
    data = nodes["uapp_fields"]["data"]
    data["code"] = patched_source(data["code"])
    for key in ("semantic_projection_status", "authority_guard_status"):
        data.setdefault("outputs", {})[key] = {"type": "string", "children": None}
    touched = [key for key in nodes if canonical(nodes[key]) != canonical(base_nodes[key])]
    if touched != ["uapp_fields"]:
        raise RuntimeError(f"unexpected touched nodes: {touched}")
    report = {
        "document": {"id": "UAPP_AC12_SEMANTIC_HANDOFF_BUILD_v1.0", "model_calls": 0},
        "base_graph_md5": BASE_GRAPH_MD5,
        "candidate_canonical_sha256": digest(candidate),
        "nodes": len(candidate["nodes"]), "edges": len(candidate["edges"]),
        "touched_nodes": touched,
        "protected_nodes_unchanged": all(canonical(nodes[key]) == canonical(base_nodes[key])
                                         for key in ("uapp_route", "uapp_m3", "uapp_hop",
                                                     "uapp_seam", "m1_compiler")),
    }
    return candidate, report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--publish", action="store_true")
    args = parser.parse_args()
    if args.dry_run == args.publish:
        raise SystemExit("choose exactly one of --dry-run or --publish")
    actual = database_value(
        "select md5(w.graph) from workflows w join apps a on a.workflow_id=w.id "
        f"where a.id='{APP_ID}';"
    )
    if actual != BASE_GRAPH_MD5:
        raise RuntimeError(f"candidate baseline drift: {actual}")
    candidate, report = patch_graph(published_graph())
    if args.publish:
        console = BASE.DC.Console(env=BASE.DC.load_env(BASE.ENV_FILE))
        status, draft = console.call("GET", f"/console/api/apps/{APP_ID}/workflows/draft")
        if status != 200:
            raise RuntimeError((status, draft))
        payload = {"graph": candidate, "features": draft.get("features") or {},
                   "hash": draft.get("hash"),
                   "environment_variables": draft.get("environment_variables") or [],
                   "conversation_variables": draft.get("conversation_variables") or []}
        status, response = console.call("POST", f"/console/api/apps/{APP_ID}/workflows/draft",
                                        body=payload, timeout=900)
        if status != 200:
            raise RuntimeError((status, response))
        status, response = console.call(
            "POST", f"/console/api/apps/{APP_ID}/workflows/publish",
            body={"marked_name": "ac12-handoff-v1",
                  "marked_comment": "User outcome projection and primary-goal source lock"},
            timeout=900,
        )
        if status not in (200, 201):
            raise RuntimeError((status, response))
        report["published_graph_md5"] = database_value(
            "select md5(w.graph) from workflows w join apps a on a.workflow_id=w.id "
            f"where a.id='{APP_ID}';"
        )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
