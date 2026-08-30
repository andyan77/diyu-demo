#!/usr/bin/env python3
"""Deterministic positive and single-variable negative controls for S5 repair 2."""

from __future__ import annotations

import importlib.util
import json
import os
from types import ModuleType
from typing import Any

HERE = os.path.dirname(os.path.abspath(__file__))
UAPP_ROOT = os.path.abspath(os.path.join(HERE, ".."))
OUTPUT = os.path.join(
    UAPP_ROOT, "evidence", "stages", "uapp_s5_v1_5", "controls",
    "UAPP_S5_EMPTY_STATE_CORRECTION_CONTROLS_v1.0.json",
)


def load_module(name: str, path: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


BUILD = load_module(
    "uapp_s5_empty_state_build_controls",
    os.path.join(HERE, "UAPP_S5_EMPTY_STATE_CORRECTION_BUILD_v1.0.py"),
)


def correction_main(candidate: dict[str, Any]) -> Any:
    node = next(item for item in candidate["nodes"] if item["id"] == "uapp_td24_correction")
    namespace: dict[str, Any] = {}
    exec(node["data"]["code"], namespace)  # noqa: S102 - exact candidate code under test
    return namespace["main"]


def main() -> int:
    if os.path.exists(OUTPUT):
        raise RuntimeError(f"Refusing to overwrite {OUTPUT}")
    candidate, build = BUILD.patch_graph(BUILD.published_graph())
    run = correction_main(candidate)
    empty_patch = {"correction_deltas": []}
    explicit = "把制作规模从一人改为两人，其他不变。"
    valid_state = {
        "task_key": "task-A",
        "rev": 1,
        "fields": {
            "production.profile": {
                "v": "一人制作，半天完成", "lvl": "A", "kind": "USER_UTTERANCE",
                "ref": "TURN1.user_request", "sc": "PRODUCTION", "frev": 1,
            }
        },
        "artifacts": [],
        "events": [],
    }
    proposal = {"correction_deltas": [{
        "field_id": "production.profile",
        "new_value": "两人制作，半天完成",
        "source_quote": explicit,
    }]}
    cases = []

    def check(case_id: str, actual: dict[str, Any], expected: dict[str, Any]) -> None:
        predicates = {key: actual.get(key) == value for key, value in expected.items()}
        cases.append({
            "id": case_id,
            "expected": expected,
            "actual": {key: actual.get(key) for key in expected},
            "predicates": predicates,
            "verdict": "PASS" if all(predicates.values()) else "FAIL",
        })

    check("P-01_EMPTY_STATE_NO_CORRECTION_INITIALIZES", run(
        "", empty_patch, "请基于已有脚本给出拍摄方案。", "task-A", "PRODUCTION_DIRECTOR"
    ), {"correction_status": "NONE", "correction_note": "NEW_TASK_NO_CORRECTION"})
    check("N-01_EMPTY_STATE_EXPLICIT_CHANGE_FAILS_CLOSED", run(
        "", empty_patch, explicit, "task-A", "PRODUCTION_DIRECTOR"
    ), {"correction_status": "REJECTED", "correction_note": "TASK_IDENTITY_MISMATCH"})
    check("N-02_EMPTY_STATE_PROPOSED_DELTA_FAILS_CLOSED", run(
        "", proposal, explicit, "task-A", "PRODUCTION_DIRECTOR"
    ), {"correction_status": "REJECTED", "correction_note": "TASK_IDENTITY_MISMATCH"})
    check("P-02_MATCHED_STATE_NO_CORRECTION_UNCHANGED", run(
        json.dumps(valid_state, ensure_ascii=False), empty_patch,
        "请基于已有脚本给出拍摄方案。", "task-A", "PRODUCTION_DIRECTOR"
    ), {"correction_status": "NONE", "correction_note": "NO_CORRECTION"})
    check("P-03_MATCHED_STATE_REAL_CORRECTION_APPLIES", run(
        json.dumps(valid_state, ensure_ascii=False), proposal,
        explicit, "task-A", "PRODUCTION_DIRECTOR"
    ), {"correction_status": "APPLIED", "corrected_fields": "production.profile"})
    check("N-03_WRONG_TASK_REAL_CORRECTION_FAILS_CLOSED", run(
        json.dumps(valid_state, ensure_ascii=False), proposal,
        explicit, "task-B", "PRODUCTION_DIRECTOR"
    ), {"correction_status": "REJECTED", "correction_note": "TASK_IDENTITY_MISMATCH"})

    structural = {
        "only_correction_node_touched": build["nodes_touched"] == ["uapp_td24_correction"],
        "all_other_uapp_nodes_equal": build["protected_uapp_nodes_equal"],
        "no_conversation_variables_added": build["conversation_variables_added"] == [],
        "node_and_edge_counts_stable": (
            build["node_count"] == 55 and build["edge_count"] == 57
        ),
    }
    verdict = "PASS" if all(structural.values()) and all(
        case["verdict"] == "PASS" for case in cases
    ) else "FAIL"
    result = {
        "document": {
            "id": "UAPP_S5_EMPTY_STATE_CORRECTION_CONTROLS_v1.0",
            "task_id": "DIYU-V1-UNIFIED-DIFY-APPLICATION-001",
            "model_calls": 0,
        },
        "candidate_graph_canonical_sha256": build["candidate_graph_canonical_sha256"],
        "cases": cases,
        "case_pass_count": sum(case["verdict"] == "PASS" for case in cases),
        "case_count": len(cases),
        "structural": structural,
        "structural_pass_count": sum(structural.values()),
        "structural_count": len(structural),
        "verdict": verdict,
    }
    os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
    with open(OUTPUT, "x", encoding="utf-8") as handle:
        json.dump(result, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    print(json.dumps({
        "verdict": verdict,
        "cases": f"{result['case_pass_count']}/{result['case_count']}",
        "structural": f"{result['structural_pass_count']}/{result['structural_count']}",
        "candidate": result["candidate_graph_canonical_sha256"],
    }, ensure_ascii=False))
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
