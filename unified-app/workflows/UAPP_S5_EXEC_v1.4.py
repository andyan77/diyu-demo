#!/usr/bin/env python3
"""Gate v1.3 adapter preserving the repaired candidate and isolated slot."""

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


V13 = load_module("uapp_s5_exec_v13_for_v14", os.path.join(HERE, "UAPP_S5_EXEC_v1.3.py"))
GATE = os.path.join(UAPP_ROOT, "stages", "UAPP_S5_GATE_v1.3.json")
MANIFEST = os.path.join(UAPP_ROOT, "stages", "UAPP_S5_CANDIDATE_RUN_MANIFEST_v1.3.yaml")
EVIDENCE = os.path.join(UAPP_ROOT, "evidence", "stages", "uapp_s5_v1_3")


def safe_key(key: str) -> str:
    return key.replace(":", "_").replace("/", "_")


def raw_path(key: str) -> str:
    return os.path.join(EVIDENCE, "raw", f"{safe_key(key)}.json")


def check_path(key: str) -> str:
    return os.path.join(EVIDENCE, "checks", f"{safe_key(key)}.json")


for module in (V13, V13.BASE):
    module.EVIDENCE = EVIDENCE
    module.raw_path = raw_path
    module.check_path = check_path
V13.BASE.RUNNER.GATE = GATE
V13.BASE.RUNNER.MANIFEST = MANIFEST
V13.BASE.RUNNER.EVIDENCE = EVIDENCE
V13.BASE.RUNNER.raw_path = raw_path
V13.BASE.RUNNER.check_path = check_path
V13.BASE.CHECKER.raw_path = raw_path
V13.BASE.CHECKER.check_path = check_path


def frozen() -> tuple[dict[str, Any], dict[str, Any]]:
    for path in (V13.SCENARIOS, MANIFEST, GATE):
        if not os.path.exists(path):
            raise RuntimeError(f"Frozen prerequisite absent: {path}")
    scenarios = V13.BASE.RUNNER.load_json(V13.SCENARIOS)
    gate = V13.BASE.RUNNER.load_json(GATE)
    if gate.get("document", {}).get("id") != "UAPP_S5_GATE_v1.3":
        raise RuntimeError("Unexpected repaired-candidate Gate identity")
    return scenarios, gate


V13.BASE.RUNNER.frozen = frozen


def predecessor_context(
    scenarios: dict[str, Any], turn: dict[str, Any]
) -> tuple[str, str]:
    conversation_id, end_user = V13.BASE._predecessor(scenarios, turn)
    if conversation_id:
        return conversation_id, end_user
    return "", f"uapp-s5-v13-{str(turn['conversation_group']).lower()}-20260830"


V13.BASE.RUNNER.predecessor_context = predecessor_context

if __name__ == "__main__":
    raise SystemExit(V13.BASE.main())

