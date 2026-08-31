#!/usr/bin/env python3
"""Build the AC-12 semantic-authority successor without calling a model.

Only the UAPP field authority projection and the UAPP-to-Seam reference payload
are changed.  M3, Hop, Seam's routing implementation, providers, and all
professional skills remain untouched.
"""

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
APP_ID = "dbb14eec-a935-445c-9764-280c8fd3375b"
BASE_GRAPH_MD5 = "db49ac79449899a8eeedfa3b0b01bf2b"
# The candidate is published once under this package.  Keeping this identity
# separate lets deterministic controls inspect the live candidate without
# trying to apply the source transformation a second time.
PUBLISHED_CANDIDATE_GRAPH_MD5 = "5720ddf6e0daef0bc82818bb53b95ff4"
ENV_FILE = Path("/home/faye/diyu-demo-worktrees/m3-account-content-operator-v1/.env")


def load_module(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


PRIOR = load_module(
    "uapp_ac12_semantic_authority_prior",
    ROOT / "unified-app/workflows/UAPP_AC12_SEMANTIC_HANDOFF_BUILD_v1.0.py",
)

DIRECT_HELPERS = r'''

# The labels below are semantic labels, not fixture text.  They are accepted
# only when the value is in this turn's user request, and they never turn a
# recommendation into a user decision.
_DIRECT_LABELS = {
    "audience.expected_change": ("希望她看完明白", "期望改变", "希望观众明白", "希望她知道"),
    "content.promise": ("内容承诺",),
    "expression.subject": ("表达主体", "出镜主体", "谁来表达"),
    "expression.boundary": ("表达边界", "表达限制", "不能说什么"),
    "objective.primary_goal": ("经营目标", "本周目标", "主目标"),
}
_NUMBERS = {"一": "1", "二": "2", "三": "3", "四": "4", "五": "5",
            "六": "6", "七": "7", "八": "8", "九": "9", "十": "10"}


def _direct_user_semantics(user_query):
    raw = user_query or ""
    result = {}
    for line in raw.splitlines():
        if ":" not in line and "：" not in line:
            continue
        key, value = re.split(r"[：:]", line, maxsplit=1)
        key, value = _norm(key), _clean_user_value(value)
        if not value:
            continue
        for cid, labels in _DIRECT_LABELS.items():
            if any(label in key for label in labels):
                result[cid] = value
                break
    outcome = _user_stated_viewer_outcome(raw)
    if outcome:
        result.setdefault("audience.expected_change", outcome)
    # A viewer outcome is a content promise only when the user made it.  It is
    # never substituted by expression subject or expression boundary.
    if result.get("audience.expected_change"):
        result.setdefault("content.promise", result["audience.expected_change"])
    subject = result.get("expression.subject", "")
    boundary = result.get("expression.boundary", "")
    if subject and boundary:
        result["expression.subject_and_boundary"] = subject + "；" + boundary
    # Quantity is retained as a user constraint.  It is intentionally not an
    # M3 recommendation and is visible to the downstream contract.
    hit = re.search(r"(?:做|要|只做|就做|一共)\s*([一二三四五六七八九十0-9])\s*条(?:内容|视频|短片)?", raw)
    if hit:
        result["content.quantity"] = _NUMBERS.get(hit.group(1), hit.group(1))
    return result
'''

INSERT_DIRECT = '''    direct_authority = _direct_user_semantics(uq)
    for cid, val in direct_authority.items():
        if cid not in SPEC or not val:
            continue
        _set(lines, found, cid, val)
        env_vals[cid] = val
        if cid in env_missing:
            env_missing.remove(cid)
    gaps = [cid for cid in gaps if cid not in direct_authority]
    # These identities change business meaning.  Hop/M3 prose may be retained
    # as historical evidence, but cannot fill them when this turn lacks the
    # corresponding direct user statement.
    for cid in ("content.promise", "expression.subject", "expression.boundary",
                "expression.subject_and_boundary", "content.quantity"):
        if cid not in direct_authority and cid in env_vals:
            env_vals.pop(cid, None)
            _drop(lines, found, SPEC[cid]["k"])

'''

OLD_LOOP = '''    for cid in sorted(env_vals):
        val = env_vals[cid]
        if cid == "objective.primary_goal":'''
NEW_LOOP = '''    for cid in sorted(env_vals):
        val = env_vals[cid]
        if cid in direct_authority:
            if not correction_active:
                r = offer(cid, val, "A", "USER_UTTERANCE", "TURN%d.user_request" % rev)
                if r in ("NEW", "UPDATED", "SAME", "REFINED"):
                    answered.append(cid)
            continue
        if cid == "objective.primary_goal":'''

OLD_RETURN = '''            "authority_guard_status": ("REJECTED_UNSUPPORTED_PRIMARY_GOAL" if authority_rejected
                                       else "NO_PRIMARY_GOAL_REJECTION"),
            "gaps_text": merged_gaps,'''
NEW_RETURN = '''            "authority_guard_status": ("REJECTED_UNSUPPORTED_PRIMARY_GOAL" if authority_rejected
                                       else "NO_PRIMARY_GOAL_REJECTION"),
            "direct_authority_fields": ",".join(sorted(direct_authority)),
            "professional_input_safe": ("本轮没有可作为业务决定依据的专业参考原文。"
                                        "用户确认的目标、内容承诺、数量、事实与权限"
                                        "只以 capability_call 为准。"),
            "gaps_text": merged_gaps,'''


def patched_fields(source: str) -> str:
    # A control may run after the candidate is published.  The transformation
    # is intentionally idempotent for that read-only inspection path; a
    # second publication is still refused below.
    if "_DIRECT_LABELS = {" in source and "professional_input_safe" in source \
            and '"content.quantity": {"k": "content_quantity"' in source:
        return source
    main_anchor = "\ndef main(prev_state_json, task_key, capability_call, gaps_text, target_capability,\n"
    env_anchor = "    # P-08 fail-closed：同一规范身份不能同时非空又出现在缺口里\n"
    if source.count(main_anchor) != 1 or source.count(env_anchor) != 1:
        raise RuntimeError("uapp_fields patch anchors changed")
    quantity_anchor = '''    "content.promise": {"k": "content_promise", "st": "BT", "sc": "CONTENT_TASK"},
'''
    quantity_line = '''    "content.quantity": {"k": "content_quantity", "st": "BT", "sc": "CONTENT_TASK"},
'''
    if source.count(OLD_LOOP) != 1 or source.count(OLD_RETURN) != 1 \
            or source.count(quantity_anchor) != 1:
        raise RuntimeError("uapp_fields authority anchors changed")
    source = source.replace(main_anchor, DIRECT_HELPERS + main_anchor)
    source = source.replace(quantity_anchor, quantity_anchor + quantity_line)
    source = source.replace(env_anchor, INSERT_DIRECT + env_anchor)
    source = source.replace(OLD_LOOP, NEW_LOOP)
    return source.replace(OLD_RETURN, NEW_RETURN)


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value).encode("utf-8")).hexdigest()


def database_value(sql: str) -> str:
    return PRIOR.database_value(sql)


def published_graph() -> dict[str, Any]:
    return PRIOR.BASE.published_graph()


def patch_graph(graph: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    candidate = copy.deepcopy(graph)
    before = {item["id"]: item for item in graph["nodes"]}
    nodes = {item["id"]: item for item in candidate["nodes"]}
    fields = nodes["uapp_fields"]["data"]
    was_patched = "_DIRECT_LABELS = {" in fields["code"] and "professional_input_safe" in fields["code"]
    fields["code"] = patched_fields(fields["code"])
    for name in ("direct_authority_fields", "professional_input_safe"):
        fields.setdefault("outputs", {})[name] = {"type": "string", "children": None}
    seam = nodes["uapp_seam"]["data"]
    params = seam.get("tool_parameters") or {}
    if "professional_input" not in params:
        raise RuntimeError("uapp_seam professional_input parameter absent")
    params["professional_input"]["value"] = "{{#uapp_fields.professional_input_safe#}}"
    touched = [node_id for node_id in nodes if canonical(nodes[node_id]) != canonical(before[node_id])]
    expected_touched = [] if was_patched else ["uapp_fields", "uapp_seam"]
    if touched != expected_touched:
        raise RuntimeError("unexpected touched nodes: %s" % touched)
    return candidate, {
        "document": {"id": "UAPP_AC12_SEMANTIC_AUTHORITY_BUILD_v1.0", "model_calls": 0},
        "base_graph_md5": BASE_GRAPH_MD5,
        "candidate_canonical_sha256": digest(candidate),
        "nodes": len(candidate["nodes"]), "edges": len(candidate["edges"]),
        "touched_nodes": touched,
        "already_patched": was_patched,
        "protected_nodes_unchanged": all(canonical(nodes[k]) == canonical(before[k])
                                           for k in ("uapp_route", "uapp_m3", "uapp_hop", "m1_compiler")),
        "seam_routing_unchanged": (nodes["uapp_seam"]["data"].get("provider_id") ==
                                    before["uapp_seam"]["data"].get("provider_id")),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--publish", action="store_true")
    args = parser.parse_args()
    if args.dry_run == args.publish:
        raise SystemExit("choose exactly one of --dry-run or --publish")
    actual = database_value(
        "select md5(w.graph) from workflows w join apps a on a.workflow_id=w.id "
        "where a.id='%s';" % APP_ID
    )
    if actual not in (BASE_GRAPH_MD5, PUBLISHED_CANDIDATE_GRAPH_MD5):
        raise RuntimeError("candidate baseline drift: %s" % actual)
    if args.publish and actual != BASE_GRAPH_MD5:
        raise RuntimeError("candidate is already published; refusing a second publication")
    candidate, report = patch_graph(published_graph())
    if args.publish:
        console = PRIOR.BASE.DC.Console(env=PRIOR.BASE.DC.load_env(ENV_FILE))
        status, draft = console.call("GET", "/console/api/apps/%s/workflows/draft" % APP_ID)
        if status != 200:
            raise RuntimeError((status, draft))
        payload = {"graph": candidate, "features": draft.get("features") or {}, "hash": draft.get("hash"),
                   "environment_variables": draft.get("environment_variables") or [],
                   "conversation_variables": draft.get("conversation_variables") or []}
        status, response = console.call("POST", "/console/api/apps/%s/workflows/draft" % APP_ID,
                                        body=payload, timeout=900)
        if status != 200:
            raise RuntimeError((status, response))
        status, response = console.call(
            "POST", "/console/api/apps/%s/workflows/publish" % APP_ID,
            body={"marked_name": "ac12-auth-v1",
                  "marked_comment": "Direct user authority contract and non-authoritative reference filter"},
            timeout=900)
        if status not in (200, 201):
            raise RuntimeError((status, response))
        report["published_graph_md5"] = database_value(
            "select md5(w.graph) from workflows w join apps a on a.workflow_id=w.id where a.id='%s';" % APP_ID)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
