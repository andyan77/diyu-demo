#!/usr/bin/env python3
"""Build/publish the second and final bounded S5 UAPP repair without model calls."""

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
BASE_GRAPH_MD5 = "02610a77c3ce86f46f7a80de6d47ac2e"
OUTPUT = os.path.join(
    UAPP_ROOT, "evidence", "stages", "uapp_s5_v1_5", "repair",
    "UAPP_S5_EMPTY_STATE_CORRECTION_BUILD_v1.0.json",
)


def load_module(name: str, path: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


DC = load_module(
    "dify_client_s5_repair_2",
    os.path.join(REPO, "account-operations", "tools", "dify_client.py"),
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
    before_nodes = {item["id"]: item for item in graph["nodes"]}
    nodes = {item["id"]: item for item in candidate["nodes"]}
    node = nodes["uapp_td24_correction"]
    data = node["data"]
    anchor = '''    if not isinstance(state, dict) or state.get("task_key") != (task_key or "").strip():
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
'''
    replacement = '''    state_matches = (isinstance(state, dict)
                     and state.get("task_key") == (task_key or "").strip())
    if not state_matches:
        # S5 repair 2: an empty conversation state with no correction signal is a new
        # task initialization, not a rejected correction.  Real correction language,
        # proposed deltas, and non-empty task mismatches remain fail-closed.
        patch = _patch(action_patch)
        proposals = patch.get("correction_deltas") or []
        has_proposals = bool(proposals)
        explicit_change = bool(EXPLICIT_CHANGE.search(user_request or ""))
        uninitialized = isinstance(state, dict) and not state
        if uninitialized and not has_proposals and not explicit_change:
            return {
                "corrected_state_json": "{}",
                "correction_delta_json": "[]",
                "correction_status": "NONE",
                "corrected_fields": "",
                "direct_stale": "",
                "transitive_stale": "",
                "lineage_backfilled": "",
                "block_message": "",
                "correction_note": "NEW_TASK_NO_CORRECTION",
            }
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
'''
    if data["code"].count(anchor) != 1:
        raise RuntimeError("uapp_td24_correction identity anchor mismatch")
    data["code"] = data["code"].replace(anchor, replacement, 1)
    data["desc"] = (
        "能力中立纠正与失效传播；空状态且无纠正信号按新任务初始化处理"
    )

    touched = [node_id for node_id in nodes
               if canonical(nodes[node_id]) != canonical(before_nodes[node_id])]
    if touched != ["uapp_td24_correction"]:
        raise RuntimeError(f"Unexpected node impact: {touched}")
    protected = {
        node_id: canonical(nodes[node_id]) == canonical(before_nodes[node_id])
        for node_id in nodes if node_id != "uapp_td24_correction"
    }
    if not all(protected.values()):
        raise RuntimeError("Protected UAPP node drift")
    report = {
        "document": {
            "id": "UAPP_S5_EMPTY_STATE_CORRECTION_BUILD_v1.0",
            "task_id": "DIYU-V1-UNIFIED-DIFY-APPLICATION-001",
            "model_calls": 0,
            "repair_node": 2,
            "repair_iteration": 1,
        },
        "base_graph_md5": BASE_GRAPH_MD5,
        "nodes_touched": touched,
        "protected_uapp_nodes_equal": all(protected.values()),
        "protected_uapp_node_count": sum(protected.values()),
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
        "marked_name": "uapp-s5-repair-2",
        "marked_comment": "S5 bounded repair 2: empty state without correction initializes normally",
    })
    published = published_graph()
    if canonical(published) != canonical(candidate):
        raise RuntimeError("Published graph differs")
    report["published"] = True
    report["publish_response"] = response
    report["published_graph_md5"] = graph_md5()
    report["published_graph_canonical_sha256"] = sha256_text(canonical(published))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--publish", action="store_true")
    args = parser.parse_args()
    if args.dry_run == args.publish:
        raise SystemExit("Choose exactly one mode")
    if graph_md5() != BASE_GRAPH_MD5:
        raise RuntimeError("Published UAPP differs from repair base")
    candidate, report = patch_graph(published_graph())
    if args.publish:
        publish(candidate, report)
    output = OUTPUT if args.publish else OUTPUT.replace(".json", "_DRY_RUN.json")
    os.makedirs(os.path.dirname(output), exist_ok=True)
    if os.path.exists(output):
        raise RuntimeError(f"Refusing to overwrite {output}")
    with open(output, "x", encoding="utf-8") as handle:
        json.dump(report, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
