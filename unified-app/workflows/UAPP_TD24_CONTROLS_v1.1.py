#!/usr/bin/env python3
"""Versioned TD24 controls with the A-02 negative fixture isolated.

v1.0 is preserved with its 10/11 result. This successor reruns the complete v1.0
suite and replaces only A-02 with an equivalent explicit-correction phrase that does
not also activate the independent ``from ... change to ...`` deterministic fallback.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import logging
import os
from types import ModuleType
from typing import Any

HERE = os.path.dirname(os.path.abspath(__file__))
UAPP_ROOT = os.path.abspath(os.path.join(HERE, ".."))
EVIDENCE_DIR = os.path.join(UAPP_ROOT, "evidence", "stages", "uapp_td24")


def load_module(name: str, path: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


BASE = load_module("uapp_td24_controls_v10", os.path.join(HERE, "UAPP_TD24_CONTROLS_v1.0.py"))


def sha256_file(path: str) -> str:
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


def isolated_a02() -> dict[str, Any]:
    graph, _ = BASE.BUILDER.build_candidate(BASE.BUILDER.published_graph())
    node = next(item for item in graph["nodes"] if item["id"] == "uapp_td24_correction")
    correction = BASE.load_main(node["data"]["code"], "td24_correction_v11")
    state_raw = BASE.current_variable("uapp_task_fields")
    state = json.loads(state_raw)
    old_profile = state["fields"]["production.profile"]["v"]
    proposal_query = "制作规模由一人改成两人，其他已经确认的内容不变。"
    valid_proposal = {
        "correction_deltas": [
            {
                "field_id": "production.profile",
                "new_value": old_profile.replace("一人", "两人"),
                "source_quote": "制作规模由一人改成两人",
            }
        ]
    }
    valid = correction(
        state_raw,
        valid_proposal,
        proposal_query,
        BASE.TASK_KEY,
        "PUBLISHING_PACKAGING",
    )
    unsupported = json.loads(json.dumps(valid_proposal, ensure_ascii=False))
    unsupported["correction_deltas"][0]["source_quote"] = "两人"
    rejected = correction(
        state_raw,
        unsupported,
        proposal_query,
        BASE.TASK_KEY,
        "PUBLISHING_PACKAGING",
    )
    valid_state = json.loads(valid["corrected_state_json"])
    rejected_state = json.loads(rejected["corrected_state_json"])
    positive_ok = (
        valid["correction_status"] == "APPLIED"
        and valid_state["fields"]["production.profile"]["kind"] == "USER_UTTERANCE"
    )
    negative_ok = (
        rejected["correction_status"] == "REJECTED"
        and rejected_state["rev"] == state["rev"]
    )
    return {
        "id": "A-02",
        "text": "模型只提议；逐字用户证据成立才升级为 USER_UTTERANCE",
        "result": "PASS" if positive_ok and negative_ok else "FAIL",
        "positive_control": {
            "pass": positive_ok,
            "equivalent_phrase": proposal_query,
            "deterministic_fallback_also_applicable": False,
        },
        "single_variable_negative_control": {
            "pass": negative_ok,
            "mutated": "source_quote",
            "status": rejected["correction_status"],
        },
    }


def run() -> dict[str, Any]:
    report = BASE.run()
    replacement = isolated_a02()
    report["checks"] = [
        replacement if item["id"] == "A-02" else item for item in report["checks"]
    ]
    passed = sum(item["result"] == "PASS" for item in report["checks"])
    report["document"]["id"] = "UAPP_TD24_CONTROLS_v1.1"
    report["document"]["parent_checker"] = "UAPP_TD24_CONTROLS_v1.0.py"
    report["document"]["parent_checker_sha256"] = sha256_file(
        os.path.join(HERE, "UAPP_TD24_CONTROLS_v1.0.py")
    )
    report["document"]["fixture_triage"] = (
        "unified-app/docs/UAPP_TD24_CONTROLS_FAILURE_TRIAGE_001.md"
    )
    report["summary"] = {
        "pass": passed,
        "total": len(report["checks"]),
        "positive_controls": len(report["checks"]),
        "single_variable_negative_controls": len(report["checks"]),
        "verdict": "PASS" if passed == len(report["checks"]) else "FAIL",
    }
    return report


def main() -> int:
    report = run()
    os.makedirs(EVIDENCE_DIR, exist_ok=True)
    output = os.path.join(EVIDENCE_DIR, "UAPP_TD24_CONTROLS_v1.1.json")
    with open(output, "x", encoding="utf-8") as handle:
        json.dump(report, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    logging.info("%s", json.dumps(report["summary"], ensure_ascii=False, sort_keys=True))
    return 0 if report["summary"]["verdict"] == "PASS" else 1


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    raise SystemExit(main())
