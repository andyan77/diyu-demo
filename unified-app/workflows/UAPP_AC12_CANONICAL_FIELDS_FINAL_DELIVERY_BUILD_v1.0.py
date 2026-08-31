#!/usr/bin/env python3
"""Build the AC-12 canonical-fields and final-delivery successor (zero model)."""

from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
import re
from pathlib import Path
from types import ModuleType
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
APP_ID = "dbb14eec-a935-445c-9764-280c8fd3375b"
BASE_GRAPH_MD5 = "5720ddf6e0daef0bc82818bb53b95ff4"
ENV_FILE = Path("/home/faye/diyu-demo-worktrees/m3-account-content-operator-v1/.env")


def load_module(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


PRIOR = load_module(
    "uapp_ac12_authority_prior",
    ROOT / "unified-app/workflows/UAPP_AC12_SEMANTIC_AUTHORITY_BUILD_v1.0.py",
)
DC = load_module("dify_client", ROOT / "account-operations/tools/dify_client.py")


FIELDS_REPLACEMENT = r'''
def _natural_expression_subject(raw):
    # The expression subject is a user-owned sentence fact.  This accepts the
    # ordinary Chinese form “由 X 出镜/讲述/表达”, not a fixture literal.
    hit = re.search(r"(?:^|[，。；:：\n])\s*(?:由|请|让)?\s*([^，。；！？:：\n]{2,24}?)(?:真实)?(?:出镜|讲述|表达)", raw or "")
    return _clean_user_value(hit.group(1)) if hit else ""


def _natural_expression_boundary(raw):
    # Keep only explicitly stated expression constraints.  It does not invent
    # product facts, outcomes, or a commercial objective.
    hits = re.findall(r"(?:(?:只|仅)(?:讲|说|用)|不(?:做|承诺|碰|使用|写|要)|不要|不得)[^。！？\n]{0,80}", raw or "")
    return _clean_user_value("；".join(hits)) if hits else ""


def _natural_primary_goal(raw):
    hit = re.search(r"(?:(?:本周|当前|经营|本次)\s*)?目标\s*(?:是|为|：|:)\s*([^。！？\n]+)", raw or "")
    return _clean_user_value(hit.group(1)) if hit else ""


def _expression_only(value):
    # A speaker/format constraint is not a promise to the audience.  It may
    # coexist with a promise, but cannot become one merely through a label.
    val = value or ""
    expression_signal = re.search(r"(?:出镜|讲述|表达|只讲|不做|不承诺|不碰)", val)
    viewer_outcome = re.search(r"(?:看完|读完|听完).{0,10}(?:知道|明白|理解|学会|掌握|看清)", val)
    return bool(expression_signal and not viewer_outcome)


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
    if result.get("audience.expected_change"):
        result.setdefault("content.promise", result["audience.expected_change"])
    result.setdefault("expression.subject", _natural_expression_subject(raw))
    result.setdefault("expression.boundary", _natural_expression_boundary(raw))
    result.setdefault("objective.primary_goal", _natural_primary_goal(raw))
    result = {cid: value for cid, value in result.items() if value}
    if _expression_only(result.get("content.promise", "")):
        result.pop("content.promise", None)
    subject, boundary = result.get("expression.subject", ""), result.get("expression.boundary", "")
    if subject and boundary:
        result["expression.subject_and_boundary"] = subject + "；" + boundary
    hit = re.search(r"(?:做|要|只做|就做|一共)\s*([一二三四五六七八九十0-9])\s*条(?:内容|视频|短片)?", raw)
    if hit:
        result["content.quantity"] = _NUMBERS.get(hit.group(1), hit.group(1))
    return result
'''

DELIVERY_HELPERS = r'''
def _project_delivered_artifact(text):
    """Keep professional substance while removing a component-facing title.

    Optional platform adaptation and presentation alternatives remain visible,
    but are explicitly framed as later choices rather than current blockers.
    """
    out = text or ""
    out = re.sub(r"(?im)^\s*#\s*content\s+brief(?:\s+pack)?[^\n]*\n+", "", out)
    out = re.sub(r"(?im)^\s*##\s*需要你确认[^\n]*$", "## 后续可选调整（不影响先写脚本）", out)
    out = re.sub(r"(?im)^\s*##\s*启动前最后核对\s*$", "## 开始制作前的自查", out)
    return out.strip()


def _natural_gap_delivery(gaps, fallback):
    # The internal gap identity remains in the machine Return.  The user sees
    # the decision in ordinary language, with one question and no status copy.
    unique = list(dict.fromkeys(gaps))
    if unique == ["expression_subject_and_boundary"]:
        return "内容方向已经明确。接下来只需要确认：这条由谁来讲，以及哪些表达边界要守住？"
    return fallback
'''


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value).encode("utf-8")).hexdigest()


def database_value(sql: str) -> str:
    return PRIOR.database_value(sql)


def published_graph() -> dict[str, Any]:
    return PRIOR.published_graph()


def patch_fields(source: str) -> str:
    pattern = r"def _direct_user_semantics\(user_query\):.*?\n    return result\n"
    if len(re.findall(pattern, source, flags=re.S)) != 1:
        raise RuntimeError("direct user semantics anchor mismatch")
    source = re.sub(pattern, lambda _match: FIELDS_REPLACEMENT, source, count=1, flags=re.S)
    anchor = "    # 2. A/E 级：本轮外壳抽取。primary_goal has a stricter source lock:\n    # lexical overlap with a product is not evidence of a user business decision.\n    authority_rejected = []\n"
    replacement = """    # A rejected primary goal must not survive in canonical state merely\n    # because M1 snapshot projection happened earlier in this same turn.\n    if \"objective.primary_goal\" not in direct_authority:\n        F.pop(\"objective.primary_goal\", None)\n        _drop(lines, found, SPEC[\"objective.primary_goal\"][\"k\"])\n\n""" + anchor
    if source.count(anchor) != 1:
        raise RuntimeError("primary goal physical rejection anchor mismatch")
    return source.replace(anchor, replacement)


def patch_delivery(source: str) -> str:
    anchor = "\ndef _scrub(text):\n"
    if source.count(anchor) != 1:
        raise RuntimeError("delivery helper anchor mismatch")
    source = source.replace(anchor, "\n" + DELIVERY_HELPERS + anchor)
    old = "    body = (seam_user_delivery or \"\").strip()\n"
    new = "    body = _project_delivered_artifact((seam_user_delivery or \"\").strip()) if delivered else (seam_user_delivery or \"\").strip()\n"
    if source.count(old) != 1:
        raise RuntimeError("delivery body anchor mismatch")
    source = source.replace(old, new)
    old_branch = '''    if body and (delivered or gaps):
        final = body
'''
    new_branch = '''    if body and delivered:
        final = body
    elif body and gaps:
        final = _natural_gap_delivery(gaps, body)
'''
    if source.count(old_branch) != 1:
        raise RuntimeError("delivery branch anchor mismatch")
    return source.replace(old_branch, new_branch)


def patch_graph(graph: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    candidate = copy.deepcopy(graph)
    before = {item["id"]: item for item in graph["nodes"]}
    nodes = {item["id"]: item for item in candidate["nodes"]}
    nodes["uapp_fields"]["data"]["code"] = patch_fields(nodes["uapp_fields"]["data"]["code"])
    nodes["uapp_delivery"]["data"]["code"] = patch_delivery(nodes["uapp_delivery"]["data"]["code"])
    touched = [node_id for node_id in nodes if canonical(nodes[node_id]) != canonical(before[node_id])]
    if touched != ["uapp_fields", "uapp_delivery"]:
        raise RuntimeError("unexpected touched nodes: %s" % touched)
    return candidate, {
        "document": {"id": "UAPP_AC12_CANONICAL_FIELDS_FINAL_DELIVERY_BUILD_v1.0", "model_calls": 0},
        "base_graph_md5": BASE_GRAPH_MD5,
        "candidate_canonical_sha256": digest(candidate),
        "nodes": len(candidate["nodes"]), "edges": len(candidate["edges"]),
        "touched_nodes": touched,
        "protected_nodes_unchanged": all(canonical(nodes[key]) == canonical(before[key])
                                           for key in ("uapp_route", "uapp_m3", "uapp_hop", "uapp_seam", "m1_compiler")),
        "provider_unchanged": nodes["uapp_seam"]["data"].get("provider_id") == before["uapp_seam"]["data"].get("provider_id"),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--publish", action="store_true")
    args = parser.parse_args()
    if args.dry_run == args.publish:
        raise SystemExit("choose exactly one of --dry-run or --publish")
    actual = database_value("select md5(w.graph) from workflows w join apps a on a.workflow_id=w.id where a.id='%s';" % APP_ID)
    if actual != BASE_GRAPH_MD5:
        raise RuntimeError("candidate baseline drift: %s" % actual)
    candidate, report = patch_graph(published_graph())
    if args.publish:
        console = DC.Console(env=DC.load_env(str(ENV_FILE)))
        status, draft = console.call("GET", "/console/api/apps/%s/workflows/draft" % APP_ID)
        if status != 200:
            raise RuntimeError((status, draft))
        payload = {"graph": candidate, "features": draft.get("features") or {}, "hash": draft.get("hash"),
                   "environment_variables": draft.get("environment_variables") or [],
                   "conversation_variables": draft.get("conversation_variables") or []}
        status, response = console.call("POST", "/console/api/apps/%s/workflows/draft" % APP_ID, body=payload, timeout=900)
        if status != 200:
            raise RuntimeError((status, response))
        status, response = console.call("POST", "/console/api/apps/%s/workflows/publish" % APP_ID,
                                        body={"marked_name": "ac12-canon-v1", "marked_comment": "User-owned canonical fields and final artifact delivery projection"}, timeout=900)
        if status not in (200, 201):
            raise RuntimeError((status, response))
        report["published_graph_md5"] = database_value("select md5(w.graph) from workflows w join apps a on a.workflow_id=w.id where a.id='%s';" % APP_ID)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
