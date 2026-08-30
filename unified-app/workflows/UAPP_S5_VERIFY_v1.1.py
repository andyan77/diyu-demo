#!/usr/bin/env python3
"""S5 v1.1 checker: v1.0 predicates plus a real capability artifact gate."""

from __future__ import annotations

import importlib.util
import os
from types import ModuleType
from typing import Any

HERE = os.path.dirname(os.path.abspath(__file__))
UAPP_ROOT = os.path.abspath(os.path.join(HERE, ".."))
SCENARIOS = os.path.join(UAPP_ROOT, "stages", "UAPP_S5_FROZEN_SCENARIOS_v1.1.json")
GATE = os.path.join(UAPP_ROOT, "stages", "UAPP_S5_GATE_v1.1.json")
EVIDENCE = os.path.join(UAPP_ROOT, "evidence", "stages", "uapp_s5_v1_1")
RESULT = os.path.join(UAPP_ROOT, "stages", "UAPP_S5_RESULT_v1.1.json")
MATRIX = os.path.join(UAPP_ROOT, "stages", "UAPP_S5_AC_MATRIX_v1.1.json")


def load_module(name: str, path: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


BASE = load_module("uapp_s5_verify_v10_for_v11", os.path.join(HERE, "UAPP_S5_VERIFY_v1.0.py"))
BASE.SCENARIOS = SCENARIOS
BASE.GATE = GATE
BASE.EVIDENCE = EVIDENCE
BASE.RESULT = RESULT
BASE.MATRIX = MATRIX
CAPABILITIES = BASE.CAPABILITIES
FORBIDDEN_USER_TEXT = BASE.FORBIDDEN_USER_TEXT


def safe_key(key: str) -> str:
    return BASE.safe_key(key)


def raw_path(key: str) -> str:
    return os.path.join(EVIDENCE, "raw", f"{safe_key(key)}.json")


def check_path(key: str) -> str:
    return os.path.join(EVIDENCE, "checks", f"{safe_key(key)}.json")


BASE.raw_path = raw_path
BASE.check_path = check_path
_base_evaluate = BASE.evaluate_turn


def evaluate_turn(raw: dict[str, Any], turn: dict[str, Any], gate: dict[str, Any], predecessors: dict[str, dict[str, Any]] | None = None) -> dict[str, Any]:
    result = _base_evaluate(raw, turn, gate, predecessors)
    if turn.get("expected_capability"):
        artifacts = BASE.rows(raw, "artifacts")
        versions = BASE.rows(raw, "content_versions")
        result["checks"].append({"id": "CAP-04", "result": "PASS" if artifacts and versions else "FAIL", "detail": {"artifacts": len(artifacts), "content_versions": len(versions)}})
        result["verdict"] = "PASS" if all(item["result"] == "PASS" for item in result["checks"]) else "FAIL"
    return result


BASE.evaluate_turn = evaluate_turn
load_json = BASE.load_json
sha256_file = BASE.sha256_file
verify_turn = BASE.verify_turn
verify_final = BASE.verify_final
exclusive_write = BASE.exclusive_write
rows = BASE.rows
node_executed = BASE.node_executed
app_run_count = BASE.app_run_count
llm_attempts = BASE.llm_attempts


if __name__ == "__main__":
    raise SystemExit(BASE.main())
