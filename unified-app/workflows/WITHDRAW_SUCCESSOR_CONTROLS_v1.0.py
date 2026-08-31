#!/usr/bin/env python3
"""Zero-model controls for the bounded W1 withdrawal successor."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from types import ModuleType

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
OUTPUT = (
    ROOT
    / "evidence"
    / "stages"
    / "s5_final_convergence_v1_0"
    / "WITHDRAW_SUCCESSOR_CONTROLS_v1.0.json"
)


def load_module(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


BUILD = load_module(
    "withdraw_successor_controls_build", HERE / "WITHDRAW_SUCCESSOR_BUILD_v1.0.py"
)


def main() -> int:
    graph, report = BUILD.build()
    nodes = {node["id"]: node for node in graph["nodes"]}
    edges = {edge["id"]: edge for edge in graph["edges"]}
    namespace: dict[str, object] = {}
    exec(BUILD.PARSE_SOURCE, namespace)
    parse = namespace["main"]
    positive = parse(
        {
            "material_id": "material-1",
            "already_withdrawn": False,
            "withdrawn_at": "2026-08-31T00:00:00Z",
        },
        200,
        "material-1",
    )
    controls = {
        "candidate_shape": report["node_count"] == 69 and report["edge_count"] == 74,
        "exact_added_nodes": set(report["added_nodes"])
        == {
            "uapp_withdraw_gate",
            "uapp_withdraw_post",
            "uapp_withdraw_parse",
            "uapp_withdraw_result_gate",
            "uapp_withdraw_ok_answer",
            "uapp_withdraw_fail_answer",
        },
        "old_no_file_edge_removed": "uapp_material_gate-false-uapp_m3_gate"
        not in edges,
        "withdraw_branch_present": "uapp_withdraw_gate-withdraw-uapp_withdraw_post"
        in edges,
        "non_withdraw_continuation_present": "uapp_withdraw_gate-false-uapp_m3_gate"
        in edges,
        "exact_m2_endpoint": nodes["uapp_withdraw_post"]["data"]["url"].endswith(
            "/workspaces/{{#conversation.uapp_ws#}}/materials/{{#conversation.uapp_last_material#}}/withdraw"
        ),
        "actor_header_present": nodes["uapp_withdraw_post"]["data"]["headers"]
        == "X-Actor-Ref:{{#conversation.uapp_actor#}}",
        "positive_response_bound": positive["ok"] == "true"
        and positive["material_id"] == "material-1",
        "negative_status_rejected": parse(
            {"material_id": "material-1", "withdrawn_at": "x"}, 500, "material-1"
        )["ok"]
        == "false",
        "negative_identity_rejected": parse(
            {"material_id": "other", "withdrawn_at": "x"}, 200, "material-1"
        )["ok"]
        == "false",
        "negative_missing_timestamp_rejected": parse(
            {"material_id": "material-1", "withdrawn_at": ""}, 200, "material-1"
        )["ok"]
        == "false",
        "success_answer_preserves_history": "历史记录仍然保留"
        in nodes["uapp_withdraw_ok_answer"]["data"]["answer"],
        "success_answer_no_external_claim": "没有执行任何对外发布或删除"
        in nodes["uapp_withdraw_ok_answer"]["data"]["answer"],
        "failure_answer_fail_closed": "不会声称处理成功"
        in nodes["uapp_withdraw_fail_answer"]["data"]["answer"],
    }
    result = {
        "document": {
            "id": "WITHDRAW_SUCCESSOR_CONTROLS_v1.0",
            "task_id": "DIYU-V1-UNIFIED-DIFY-APPLICATION-001",
        },
        "model_calls": 0,
        "controls": controls,
        "passed": sum(controls.values()),
        "total": len(controls),
        "verdict": "PASS" if all(controls.values()) else "FAIL",
    }
    with OUTPUT.open("x", encoding="utf-8") as handle:
        json.dump(result, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0 if result["verdict"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
