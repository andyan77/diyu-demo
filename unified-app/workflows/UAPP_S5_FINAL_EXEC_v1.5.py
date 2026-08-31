#!/usr/bin/env python3
"""Executor successor binding the semantic EQUIV negative checker."""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
from types import ModuleType
from typing import Any

HERE = os.path.dirname(os.path.abspath(__file__))


def load_module(name: str, path: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


PARENT = load_module(
    "uapp_s5_final_exec_v14_parent",
    os.path.join(HERE, "UAPP_S5_FINAL_EXEC_v1.4.py"),
)
EXECUTOR = PARENT.BASE
RUNNER = EXECUTOR.BASE.RUNNER
CHECKER = load_module(
    "uapp_s5_final_checker_v12",
    os.path.join(HERE, "UAPP_S5_FINAL_CHECKER_v1.2.py"),
)
GATE = os.path.join(EXECUTOR.BASE.ROOT, "stages", "UAPP_S5_GATE_v2.5.json")
CHECKS = os.path.join(EXECUTOR.BASE.EVIDENCE, "checks_v1_5")
PARENT_A_GATE = "53e6215f0d1d2e4c4b19e7f45919eb1d9b9844be8a45a5aa9b0b5b3f694ac614"
PARENT_N_GATE = "eefadcf27a764d42b73b3b30bc9cb45c0f8db8ef05ec07c2b538735a206550fe"


def check_path(key: str) -> str:
    safe = key.replace(":", "_").replace("/", "_")
    return os.path.join(CHECKS, f"{safe}.json")


def frozen() -> tuple[dict[str, Any], dict[str, Any]]:
    scenarios = RUNNER.load_json(EXECUTOR.BASE.SCENARIOS)
    gate = RUNNER.load_json(GATE)
    if gate.get("document", {}).get("id") != "UAPP_S5_GATE_v2.5":
        raise RuntimeError("Unexpected EQUIV-negative successor Gate")
    return scenarios, gate


PARENT.GATE = GATE
EXECUTOR.GATE = GATE
EXECUTOR.__file__ = __file__
EXECUTOR.CHECKER = CHECKER
EXECUTOR.check_path = check_path
EXECUTOR.frozen = frozen
EXECUTOR.BASE.GATE = GATE
EXECUTOR.BASE.check_path = check_path
RUNNER.GATE = GATE
RUNNER.check_path = check_path
RUNNER.frozen = frozen
RUNNER.preflight = EXECUTOR.preflight


def verify(key: str) -> dict[str, Any]:
    scenarios, gate = frozen()
    raw = RUNNER.load_json(EXECUTOR.BASE.raw_path(key))
    legacy = {
        "UAPP-EQUIV-01a": PARENT_A_GATE,
        "UAPP-EQUIV-01n": PARENT_N_GATE,
    }
    expected_gate = legacy.get(key, RUNNER.sha256_file(GATE))
    if raw.get("gate_sha256") != expected_gate or raw.get(
        "scenarios_sha256"
    ) != RUNNER.sha256_file(EXECUTOR.BASE.SCENARIOS):
        return {
            "turn_key": key,
            "verdict": "NOT_VERIFIED",
            "reason": "Raw binding mismatch",
        }
    turn = RUNNER.find_turn(scenarios, key)
    predecessors = {
        item: RUNNER.load_json(EXECUTOR.BASE.raw_path(item))
        for item in EXECUTOR.BASE.DEPENDENCIES[key]
        if os.path.exists(EXECUTOR.BASE.raw_path(item))
    }
    result = CHECKER.evaluate_turn(raw, turn, gate, predecessors)
    result["adjudication_gate_sha256"] = RUNNER.sha256_file(GATE)
    result["raw_gate_sha256"] = raw.get("gate_sha256")
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--turn", required=True)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--preflight", action="store_true")
    modes.add_argument("--run", action="store_true")
    modes.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    if args.preflight:
        result = EXECUTOR.preflight(args.turn)
    elif args.run:
        return RUNNER.run_once(args.turn)
    else:
        result = verify(args.turn)
        CHECKER.exclusive_write(check_path(args.turn), result)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0 if result.get("verdict") == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
