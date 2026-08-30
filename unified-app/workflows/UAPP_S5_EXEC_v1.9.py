#!/usr/bin/env python3
"""Execute Gate v1.8 for the single authorized successor candidate."""

from __future__ import annotations

import importlib.util
import os
from types import ModuleType
from typing import Any

HERE = os.path.dirname(os.path.abspath(__file__))
UAPP_ROOT = os.path.abspath(os.path.join(HERE, ".."))
SCENARIOS = os.path.join(UAPP_ROOT, "stages", "UAPP_S5_FROZEN_SCENARIOS_v1.1.json")
GATE = os.path.join(UAPP_ROOT, "stages", "UAPP_S5_GATE_v1.8.json")
MANIFEST = os.path.join(UAPP_ROOT, "stages", "UAPP_S5_CANDIDATE_RUN_MANIFEST_v1.8.yaml")
EVIDENCE = os.path.join(
    UAPP_ROOT, "evidence", "stages", "uapp_s5_inline_artifact_successor_v1_0", "formal"
)
RESULT = os.path.join(UAPP_ROOT, "stages", "UAPP_S5_RESULT_v1.6.json")
MATRIX = os.path.join(UAPP_ROOT, "stages", "UAPP_S5_AC_MATRIX_v1.6.json")


def load_module(name: str, path: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


V18 = load_module("uapp_s5_exec_v18_for_v19", os.path.join(HERE, "UAPP_S5_EXEC_v1.8.py"))
V18.SCENARIOS = SCENARIOS
V18.GATE = GATE
V18.MANIFEST = MANIFEST
V18.EVIDENCE = EVIDENCE
V18.RESULT = RESULT
V18.MATRIX = MATRIX
V18.RUNNER.SCENARIOS = SCENARIOS
V18.RUNNER.GATE = GATE
V18.RUNNER.MANIFEST = MANIFEST
V18.RUNNER.EVIDENCE = EVIDENCE
V18.CHECKER.GATE = GATE
V18.CHECKER.EVIDENCE = EVIDENCE
V18.CHECKER.RESULT = RESULT
V18.CHECKER.MATRIX = MATRIX
V18.CHECKER.BASE.GATE = GATE
V18.CHECKER.BASE.EVIDENCE = EVIDENCE
V18.CHECKER.BASE.RESULT = RESULT
V18.CHECKER.BASE.MATRIX = MATRIX


def raw_path(key: str) -> str:
    return os.path.join(EVIDENCE, "raw", f"{V18.safe_key(key)}.json")


def check_path(key: str) -> str:
    return os.path.join(EVIDENCE, "checks", f"{V18.safe_key(key)}.json")


V18.raw_path = raw_path
V18.check_path = check_path
V18.RUNNER.raw_path = raw_path
V18.RUNNER.check_path = check_path
V18.CHECKER.raw_path = raw_path
V18.CHECKER.check_path = check_path
V18.CHECKER.BASE.raw_path = raw_path
V18.CHECKER.BASE.check_path = check_path


def successor_frozen() -> tuple[dict[str, Any], dict[str, Any]]:
    for path in (SCENARIOS, MANIFEST, GATE):
        if not os.path.exists(path):
            raise RuntimeError(f"Frozen prerequisite absent: {path}")
    scenarios = V18.RUNNER.load_json(SCENARIOS)
    gate = V18.RUNNER.load_json(GATE)
    if gate.get("document", {}).get("id") != "UAPP_S5_GATE_v1.8":
        raise RuntimeError("Unexpected successor Gate identity")
    return scenarios, gate


V18.frozen = successor_frozen
V18.RUNNER.frozen = successor_frozen


if __name__ == "__main__":
    raise SystemExit(V18.main())
