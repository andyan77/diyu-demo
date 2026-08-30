#!/usr/bin/env python3
"""Zero-model discrimination controls for S5 projection repair 1."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
from types import ModuleType
from typing import Any

HERE = os.path.dirname(os.path.abspath(__file__))
UAPP_ROOT = os.path.abspath(os.path.join(HERE, ".."))
OUTPUT = os.path.join(
    UAPP_ROOT, "evidence", "stages", "uapp_s5_v1_1", "repair",
    "UAPP_S5_PROJECTION_CONTROLS_v1.0.json",
)


def load_module(name: str, path: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


BUILD = load_module("projection_build", os.path.join(HERE, "UAPP_S5_PROJECTION_BUILD_v1.0.py"))


def code_module(code: str) -> dict[str, Any]:
    namespace: dict[str, Any] = {}
    exec(compile(code, "<uapp_fields_candidate>", "exec"), namespace)
    return namespace


def run_case(main: Any, cap: str, user: str, reason: str) -> dict[str, Any]:
    state = json.dumps({"task_key": "task-1", "rev": 0, "fields": {},
                        "asked": [], "artifacts": [], "events": []})
    return main(state, "task-1", "objective:\n  `primary_goal`: test", "无", cap,
                user, "{}", "", "", "", "", "NO_UPSTREAM_REQUIRED", "NONE", reason)


def main() -> int:
    candidate, build = BUILD.patch_graph(BUILD.published_graph())
    fields = next(node for node in candidate["nodes"] if node["id"] == "uapp_fields")
    fn = code_module(fields["data"]["code"])["main"]
    user = "我们要正式重做四个账号的长期定位和职责分工，不是只解决眼下一条内容。"
    reason = "用户明确要求重做四个账号的长期定位和职责分工，属于账号层面的长期治理。"
    positive = run_case(fn, "MATRIX", user, reason)
    wrong_cap = run_case(fn, "CAMPAIGN", user, reason)
    unsupported = run_case(fn, "MATRIX", user, "这是模型自行补出的另一件事")
    duplicate = run_case(
        fn, "MATRIX", user, reason
    )
    checks = {
        "positive_projects_once": positive["capability_call"].count("applicability_reason:") == 1,
        "positive_value_exact": f"applicability_reason: {reason}" in positive["capability_call"],
        "positive_status": positive["applicability_projection_status"]
        == "PROJECTED_USER_SUPPORTED_ROUTE_REASON",
        "negative_wrong_cap": "applicability_reason:" not in wrong_cap["capability_call"],
        "negative_unsupported_reason": "applicability_reason:" not in unsupported["capability_call"],
        "negative_unsupported_status": unsupported["applicability_projection_status"]
        == "REJECTED_UNSUPPORTED",
        "idempotent_single_projection": duplicate["capability_call"].count("applicability_reason:") == 1,
        "canonical_fields_exclude_projection": "applicability_reason" not in positive["pending_state_json"],
        "protected_nodes_equal": all(build["protected_nodes_equal"].values()),
        "only_uapp_fields_touched": build["nodes_touched"] == ["uapp_fields"],
        "no_conversation_variables_added": build["conversation_variables_added"] == [],
    }
    result = {
        "document": {
            "id": "UAPP_S5_PROJECTION_CONTROLS_v1.0",
            "task_id": "DIYU-V1-UNIFIED-DIFY-APPLICATION-001",
            "model_calls": 0,
        },
        "checks": checks,
        "pass_count": sum(checks.values()),
        "total": len(checks),
        "result": "PASS" if all(checks.values()) else "FAIL",
        "candidate_graph_canonical_sha256": build["candidate_graph_canonical_sha256"],
        "builder_sha256": hashlib.sha256(open(BUILD.__file__, "rb").read()).hexdigest(),
    }
    if result["result"] != "PASS":
        raise RuntimeError(json.dumps(result, ensure_ascii=False))
    os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
    if os.path.exists(OUTPUT):
        raise RuntimeError(f"Refusing to overwrite {OUTPUT}")
    with open(OUTPUT, "x", encoding="utf-8") as handle:
        json.dump(result, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

