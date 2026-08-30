#!/usr/bin/env python3
"""Gate v1.2 adapter for the repaired UAPP candidate and isolated evidence slot."""

from __future__ import annotations

import importlib.util
import os
from types import ModuleType
from typing import Any

HERE = os.path.dirname(os.path.abspath(__file__))
UAPP_ROOT = os.path.abspath(os.path.join(HERE, ".."))


def load_module(name: str, path: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


BASE = load_module("uapp_s5_exec_v11_for_v13", os.path.join(HERE, "UAPP_S5_EXEC_v1.1.py"))
SCENARIOS = os.path.join(UAPP_ROOT, "stages", "UAPP_S5_FROZEN_SCENARIOS_v1.1.json")
GATE = os.path.join(UAPP_ROOT, "stages", "UAPP_S5_GATE_v1.2.json")
MANIFEST = os.path.join(UAPP_ROOT, "stages", "UAPP_S5_CANDIDATE_RUN_MANIFEST_v1.2.yaml")
EVIDENCE = os.path.join(UAPP_ROOT, "evidence", "stages", "uapp_s5_v1_2")


def safe_key(key: str) -> str:
    return key.replace(":", "_").replace("/", "_")


def raw_path(key: str) -> str:
    return os.path.join(EVIDENCE, "raw", f"{safe_key(key)}.json")


def check_path(key: str) -> str:
    return os.path.join(EVIDENCE, "checks", f"{safe_key(key)}.json")


BASE.EVIDENCE = EVIDENCE
BASE.raw_path = raw_path
BASE.check_path = check_path
BASE.RUNNER.SCENARIOS = SCENARIOS
BASE.RUNNER.GATE = GATE
BASE.RUNNER.MANIFEST = MANIFEST
BASE.RUNNER.EVIDENCE = EVIDENCE
BASE.RUNNER.raw_path = raw_path
BASE.RUNNER.check_path = check_path
BASE.CHECKER.raw_path = raw_path
BASE.CHECKER.check_path = check_path


def frozen() -> tuple[dict[str, Any], dict[str, Any]]:
    for path in (SCENARIOS, MANIFEST, GATE):
        if not os.path.exists(path):
            raise RuntimeError(f"Frozen prerequisite absent: {path}")
    scenarios = BASE.RUNNER.load_json(SCENARIOS)
    gate = BASE.RUNNER.load_json(GATE)
    if gate.get("document", {}).get("id") != "UAPP_S5_GATE_v1.2":
        raise RuntimeError("Unexpected repaired-candidate Gate identity")
    return scenarios, gate


BASE.RUNNER.frozen = frozen


def predecessor_context(
    scenarios: dict[str, Any], turn: dict[str, Any]
) -> tuple[str, str]:
    conversation_id, end_user = BASE._predecessor(scenarios, turn)
    if conversation_id:
        return conversation_id, end_user
    return "", f"uapp-s5-v12-{str(turn['conversation_group']).lower()}-20260830"


BASE.RUNNER.predecessor_context = predecessor_context

if __name__ == "__main__":
    raise SystemExit(BASE.main())

