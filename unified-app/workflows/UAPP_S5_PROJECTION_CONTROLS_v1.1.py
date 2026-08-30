#!/usr/bin/env python3
"""Read-only post-publish rebind of the projection controls."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
from typing import Any

HERE = os.path.dirname(os.path.abspath(__file__))
path = os.path.join(HERE, "UAPP_S5_PROJECTION_CONTROLS_v1.0.py")
spec = importlib.util.spec_from_file_location("projection_controls_v10", path)
if spec is None or spec.loader is None:
    raise RuntimeError(path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

OUTPUT = module.OUTPUT.replace("v1.0.json", "v1.1.json")
EXPECTED_GRAPH_MD5 = "02610a77c3ce86f46f7a80de6d47ac2e"
EXPECTED_GRAPH_SHA256 = "726b1d196717bb4e68b43fe9e6a3b9b85734a5db4611cf4d10bac19ee213dad5"


def main() -> int:
    graph = module.BUILD.published_graph()
    graph_sha256 = module.BUILD.sha256_text(module.BUILD.canonical(graph))
    fields = next(node for node in graph["nodes"] if node["id"] == "uapp_fields")
    fn = module.code_module(fields["data"]["code"])["main"]
    user = "我们要正式重做四个账号的长期定位和职责分工，不是只解决眼下一条内容。"
    reason = "用户明确要求重做四个账号的长期定位和职责分工，属于账号层面的长期治理。"
    positive = module.run_case(fn, "MATRIX", user, reason)
    wrong_cap = module.run_case(fn, "CAMPAIGN", user, reason)
    unsupported = module.run_case(fn, "MATRIX", user, "这是模型自行补出的另一件事")
    checks: dict[str, bool] = {
        "published_md5_bound": module.BUILD.graph_md5() == EXPECTED_GRAPH_MD5,
        "published_sha256_bound": graph_sha256 == EXPECTED_GRAPH_SHA256,
        "positive_projects_once": positive["capability_call"].count("applicability_reason:") == 1,
        "positive_value_exact": f"applicability_reason: {reason}" in positive["capability_call"],
        "positive_status": positive["applicability_projection_status"]
        == "PROJECTED_USER_SUPPORTED_ROUTE_REASON",
        "negative_wrong_cap": "applicability_reason:" not in wrong_cap["capability_call"],
        "negative_unsupported_reason": "applicability_reason:" not in unsupported["capability_call"],
        "negative_unsupported_status": unsupported["applicability_projection_status"]
        == "REJECTED_UNSUPPORTED",
        "canonical_fields_exclude_projection": "applicability_reason" not in positive["pending_state_json"],
        "no_new_conversation_variable": not any(
            item.get("variable") == "applicability_reason"
            for item in fields["data"]["variables"]
        ),
    }
    result: dict[str, Any] = {
        "document": {
            "id": "UAPP_S5_PROJECTION_CONTROLS_v1.1",
            "task_id": "DIYU-V1-UNIFIED-DIFY-APPLICATION-001",
            "model_calls": 0,
            "mode": "READ_ONLY_PUBLISHED_CANDIDATE",
        },
        "checks": checks,
        "pass_count": sum(checks.values()),
        "total": len(checks),
        "result": "PASS" if all(checks.values()) else "FAIL",
        "published_graph_md5": module.BUILD.graph_md5(),
        "published_graph_canonical_sha256": graph_sha256,
        "builder_sha256": hashlib.sha256(open(module.BUILD.__file__, "rb").read()).hexdigest(),
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
