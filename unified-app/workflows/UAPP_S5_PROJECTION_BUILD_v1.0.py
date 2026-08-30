#!/usr/bin/env python3
"""Build/publish the first bounded S5 UAPP repair without model calls.

The repair changes only ``uapp_fields``.  A user-supported MATRIX route reason is
projected into the current capability call as ``applicability_reason``.  It is not
written into the canonical task field carrier and does not create a second state
source.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
import os
import subprocess
from types import ModuleType
from typing import Any

HERE = os.path.dirname(os.path.abspath(__file__))
UAPP_ROOT = os.path.abspath(os.path.join(HERE, ".."))
REPO = os.path.abspath(os.path.join(UAPP_ROOT, ".."))
ENV_FILE = "/home/faye/diyu-demo-worktrees/m3-account-content-operator-v1/.env"
UAPP_APP_ID = "85c01f85-a081-43e9-ab09-9993289cc200"
BASE_GRAPH_MD5 = "89bbfeade1f149ccce12a768bed6e94a"
OUTPUT = os.path.join(
    UAPP_ROOT, "evidence", "stages", "uapp_s5_v1_1", "repair",
    "UAPP_S5_PROJECTION_BUILD_v1.0.json",
)


def load_module(name: str, path: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


DC = load_module(
    "dify_client", os.path.join(REPO, "account-operations", "tools", "dify_client.py")
)


def psql(sql: str) -> str:
    result = subprocess.run(
        ["docker", "exec", "-i", "docker-db_postgres-1", "psql", "-U", "postgres",
         "-d", "dify", "-tA", "-v", "ON_ERROR_STOP=1", "-c", sql],
        capture_output=True, check=False, text=True,
    )
    if result.returncode != 0:
        raise RuntimeError((result.stderr or result.stdout)[:1000])
    return result.stdout.strip()


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def graph_md5() -> str:
    return psql(
        "select md5(w.graph) from workflows w join apps a on a.workflow_id=w.id "
        f"where a.id='{UAPP_APP_ID}';"
    )


def published_graph() -> dict[str, Any]:
    value = json.loads(psql(
        "select w.graph from workflows w join apps a on a.workflow_id=w.id "
        f"where a.id='{UAPP_APP_ID}';"
    ))
    if not isinstance(value, dict):
        raise RuntimeError("Published graph is not an object")
    return value


def patch_graph(graph: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    candidate = copy.deepcopy(graph)
    nodes = {node["id"]: node for node in candidate["nodes"]}
    node = nodes["uapp_fields"]
    data = node["data"]
    old_signature = (
        "         selector_capability, selector_status, correction_status):"
    )
    new_signature = (
        "         selector_capability, selector_status, correction_status, intent_reason):"
    )
    if data["code"].count(old_signature) != 1:
        raise RuntimeError("uapp_fields signature anchor mismatch")
    data["code"] = data["code"].replace(old_signature, new_signature, 1)
    anchor = "    lines, found = _parse(capability_call)\n"
    projection = '''    lines, found = _parse(capability_call)\n\n    # S5 repair 1: project a user-supported route reason into the MATRIX call.\n    # This is call-local capability metadata, never a canonical field or state source.\n    applicability_projection_status = "NOT_APPLICABLE"\n    route_reason = _norm(intent_reason)\n    if cap == "MATRIX":\n        applicability_projection_status = "REJECTED_UNSUPPORTED"\n        if route_reason and _supported(route_reason, uq):\n            key = "applicability_reason"\n            line = "%s: %s" % (key, route_reason)\n            matches = [i for i, value in enumerate(lines)\n                       if value.strip().startswith(key + ":")]\n            if matches:\n                lines[matches[0]] = line\n                for i in reversed(matches[1:]):\n                    lines.pop(i)\n            else:\n                lines.append(line)\n            applicability_projection_status = "PROJECTED_USER_SUPPORTED_ROUTE_REASON"\n'''
    if data["code"].count(anchor) != 1:
        raise RuntimeError("uapp_fields parse anchor mismatch")
    data["code"] = data["code"].replace(anchor, projection, 1)
    return_anchor = '    return {"capability_call": "\\n".join(lines),\n'
    return_replacement = (
        '    return {"capability_call": "\\n".join(lines),\n'
        '            "applicability_projection_status": applicability_projection_status,\n'
    )
    if data["code"].count(return_anchor) != 1:
        raise RuntimeError("uapp_fields return anchor mismatch")
    data["code"] = data["code"].replace(return_anchor, return_replacement, 1)
    data["variables"].append({
        "value_selector": ["uapp_route", "intent_reason"],
        "variable": "intent_reason",
    })
    data["outputs"]["applicability_projection_status"] = {
        "children": None, "type": "string"
    }
    data["desc"] = (
        "复核 selector，并把有用户原话支持的能力适用理由投影到当前 MATRIX 调用"
    )
    before_nodes = {item["id"]: item for item in graph["nodes"]}
    touched = [node_id for node_id in nodes
               if canonical(nodes[node_id]) != canonical(before_nodes[node_id])]
    if touched != ["uapp_fields"]:
        raise RuntimeError(f"Unexpected node impact: {touched}")
    protected = {
        node_id: canonical(nodes[node_id]) == canonical(before_nodes[node_id])
        for node_id in ("uapp_m3", "uapp_hop", "uapp_seam", "uapp_state",
                        "uapp_persist", "uapp_save", "uapp_delivery")
    }
    if not all(protected.values()):
        raise RuntimeError(f"Protected UAPP node drift: {protected}")
    report = {
        "document": {
            "id": "UAPP_S5_PROJECTION_BUILD_v1.0",
            "task_id": "DIYU-V1-UNIFIED-DIFY-APPLICATION-001",
            "model_calls": 0,
            "repair_node": 1,
            "repair_iteration": 1,
        },
        "base_graph_md5": BASE_GRAPH_MD5,
        "nodes_touched": touched,
        "protected_nodes_equal": protected,
        "node_count": len(candidate["nodes"]),
        "edge_count": len(candidate["edges"]),
        "conversation_variables_added": [],
        "candidate_graph_canonical_sha256": sha256_text(canonical(candidate)),
    }
    return candidate, report


def call(console: Any, method: str, path: str, body: dict[str, Any] | None = None) -> dict[str, Any]:
    status, response = console.call(method, path, body=body, timeout=900)
    if status not in (200, 201) or not isinstance(response, dict):
        raise RuntimeError(f"{method} {path}: {status} {str(response)[:500]}")
    return response


def publish(candidate: dict[str, Any], report: dict[str, Any]) -> None:
    if int(psql("select count(*) from workflow_runs where status='running';")) != 0:
        raise RuntimeError("Active workflows exist")
    console = DC.Console(env=DC.load_env(ENV_FILE))
    draft = call(console, "GET", f"/console/api/apps/{UAPP_APP_ID}/workflows/draft")
    call(console, "POST", f"/console/api/apps/{UAPP_APP_ID}/workflows/draft", {
        "graph": candidate,
        "features": draft.get("features") or {},
        "hash": draft.get("hash"),
        "environment_variables": draft.get("environment_variables") or [],
        "conversation_variables": draft.get("conversation_variables") or [],
    })
    readback = call(console, "GET", f"/console/api/apps/{UAPP_APP_ID}/workflows/draft")
    if canonical(readback["graph"]) != canonical(candidate):
        raise RuntimeError("Draft readback differs")
    response = call(console, "POST", f"/console/api/apps/{UAPP_APP_ID}/workflows/publish", {
        "marked_name": "uapp-s5-projection-repair-1",
        "marked_comment": "S5 bounded repair 1: user-supported MATRIX applicability projection",
    })
    if canonical(published_graph()) != canonical(candidate):
        raise RuntimeError("Published graph differs")
    report["published"] = True
    report["publish_response"] = response
    report["published_graph_md5"] = graph_md5()
    report["published_graph_canonical_sha256"] = sha256_text(canonical(published_graph()))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--publish", action="store_true")
    args = parser.parse_args()
    if args.dry_run == args.publish:
        raise SystemExit("Choose exactly one of --dry-run or --publish")
    if graph_md5() != BASE_GRAPH_MD5:
        raise RuntimeError("Published UAPP differs from repair base")
    candidate, report = patch_graph(published_graph())
    if args.publish:
        publish(candidate, report)
    os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
    output = OUTPUT if args.publish else OUTPUT.replace(".json", "_DRY_RUN.json")
    if os.path.exists(output):
        raise RuntimeError(f"Refusing to overwrite {output}")
    with open(output, "x", encoding="utf-8") as handle:
        json.dump(report, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

