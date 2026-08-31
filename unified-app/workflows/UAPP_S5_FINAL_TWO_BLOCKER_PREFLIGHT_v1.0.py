#!/usr/bin/env python3
"""Read-only P1 reachability and historical-first-difference preflight."""

from __future__ import annotations

import hashlib
import json
import logging
import subprocess
from pathlib import Path
from typing import Any

LOGGER = logging.getLogger(__name__)
HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
REPO = ROOT.parent
SCENARIOS = ROOT / "stages" / "UAPP_S5_FROZEN_SCENARIOS_v1.2.json"
RAW_ROOT = (
    ROOT
    / "evidence"
    / "stages"
    / "s5_final_convergence_v1_0"
    / "formal_successor"
    / "raw"
)
UAPP_ID = "85c01f85-a081-43e9-ab09-9993289cc200"
EXPECTED_GRAPH_MD5 = "6ac5a45f3953683339f4ea77ebcc00c6"
EXPECTED_SCENARIO_SHA256 = (
    "7cef6cca903a9ea464ac860a59a64c5cdde85ea774a7d57a7e1028501e5b862a"
)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"Expected object: {path}")
    return value


def psql(database: str, sql: str) -> str:
    completed = subprocess.run(
        [
            "docker",
            "exec",
            "-i",
            "docker-db_postgres-1",
            "psql",
            "-U",
            "postgres",
            "-d",
            database,
            "-tA",
            "-v",
            "ON_ERROR_STOP=1",
            "-c",
            sql,
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        raise RuntimeError((completed.stderr or completed.stdout)[:2000])
    return completed.stdout.strip()


def published_graph() -> dict[str, Any]:
    raw = psql(
        "dify",
        "select w.graph from workflows w join apps a on a.workflow_id=w.id "
        f"where a.id='{UAPP_ID}';",
    )
    value = json.loads(raw)
    if not isinstance(value, dict):
        raise TypeError("Published UAPP graph is not an object")
    return value


def node_output(raw: dict[str, Any], node_id: str) -> dict[str, Any]:
    for run in raw["app_runs_in_window"]["UAPP"]:
        for node in run["node_detail"]:
            if node.get("node_id") != node_id:
                continue
            value = node.get("outputs") or "{}"
            if isinstance(value, str):
                value = json.loads(value)
            return value if isinstance(value, dict) else {}
    return {}


def main() -> int:
    load_json(SCENARIOS)
    equiv = load_json(RAW_ROOT / "UAPP-EQUIV-01b.json")
    full_t2 = load_json(RAW_ROOT / "UAPP-FULL-01_T2.json")
    graph = published_graph()
    nodes = {str(item["id"]): item for item in graph["nodes"]}
    titles = {str(item["data"].get("title") or "") for item in graph["nodes"]}
    route = node_output(full_t2, "uapp_route")
    action = node_output(full_t2, "uapp_action")
    equiv_fields = json.loads(
        str(equiv["conversation_variables_after"]["uapp_task_fields"])
    )["fields"]
    full_store = json.loads(
        str(full_t2["conversation_variables_after"]["uapp_last_artifact"])
    )
    checks = {
        "scenario_hash_current": sha256_bytes(SCENARIOS.read_bytes())
        == EXPECTED_SCENARIO_SHA256,
        "uapp_graph_current": psql(
            "dify",
            "select md5(w.graph) from workflows w join apps a on a.workflow_id=w.id "
            f"where a.id='{UAPP_ID}';",
        )
        == EXPECTED_GRAPH_MD5,
        "active_workflows_zero": int(
            psql("dify", "select count(*) from workflow_runs where status='running';")
        )
        == 0,
        "equiv_yaml_input_contains_expected_change": "希望她看完明白"
        in str(equiv["request"]["query"]),
        "equiv_yaml_failed_to_register_content_promise": "content.promise"
        not in equiv_fields,
        "full_t2_action_is_record_publish": action.get("structured_output", {}).get(
            "action"
        )
        == "RECORD_PUBLISH",
        "full_t2_route_is_writeback": route.get("route_mode") == "WRITEBACK",
        "full_t1_artifact_remained_available": len(full_store.get("items") or []) == 1,
        "publish_writeback_branch_present": any(
            "发布" in title and ("写 M2" in title or "登记" in title)
            for title in titles
        ),
        "feedback_writeback_branch_present": any(
            "反馈" in title and ("写 M2" in title or "登记" in title)
            for title in titles
        ),
        "cycle_close_writeback_branch_present": any(
            "周期" in title and ("收口" in title or "结束" in title or "下一周期" in title)
            for title in titles
        ),
        "publish_session_binding_present": "uapp_last_publish"
        in json.loads(
            psql(
                "dify",
                "select w.conversation_variables from workflows w join apps a "
                f"on a.workflow_id=w.id where a.id='{UAPP_ID}';",
            )
        ),
    }
    guard = {
        "publish": int(
            psql(
                "diyu_business",
                "select count(*) from publish_instances "
                "where not is_test or not is_simulated;",
            )
        ),
        "feedback": int(
            psql(
                "diyu_business",
                "select count(*) from feedback_records "
                "where not is_test or not is_simulated;",
            )
        ),
    }
    report = {
        "document": {
            "id": "UAPP_S5_FINAL_TWO_BLOCKER_PREFLIGHT_v1.0",
            "task_id": "DIYU-V1-UNIFIED-DIFY-APPLICATION-001",
            "model_calls": 0,
        },
        "graph": {
            "node_count": len(nodes),
            "edge_count": len(graph["edges"]),
            "graph_md5": EXPECTED_GRAPH_MD5,
        },
        "checks": checks,
        "m2_guard": guard,
        "authorized_tracks_reproducible": all(
            checks[key]
            for key in (
                "scenario_hash_current",
                "uapp_graph_current",
                "active_workflows_zero",
                "equiv_yaml_input_contains_expected_change",
                "equiv_yaml_failed_to_register_content_promise",
                "full_t2_action_is_record_publish",
                "full_t2_route_is_writeback",
                "full_t1_artifact_remained_available",
                "publish_session_binding_present",
            )
        ),
        "full_chain_reachable_before_model_calls": all(
            checks[key]
            for key in (
                "publish_writeback_branch_present",
                "feedback_writeback_branch_present",
                "cycle_close_writeback_branch_present",
            )
        ),
        "blocking_scope_gap": [
            name
            for name, present in (
                ("UAPP_REGISTER_FEEDBACK_WRITEBACK", checks["feedback_writeback_branch_present"]),
                ("UAPP_CLOSE_CYCLE_AND_NEXT_CYCLE", checks["cycle_close_writeback_branch_present"]),
            )
            if not present
        ],
    }
    LOGGER.info("%s", json.dumps(report, ensure_ascii=False, sort_keys=True))
    return 0 if report["full_chain_reachable_before_model_calls"] else 2


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    raise SystemExit(main())
