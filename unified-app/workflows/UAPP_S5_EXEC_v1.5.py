#!/usr/bin/env python3
"""Execute one Gate v1.4 turn with the current Checker and isolated evidence."""

from __future__ import annotations

import argparse
import importlib.util
import json
import logging
import os
from types import ModuleType
from typing import Any

HERE = os.path.dirname(os.path.abspath(__file__))
UAPP_ROOT = os.path.abspath(os.path.join(HERE, ".."))
SCENARIOS = os.path.join(UAPP_ROOT, "stages", "UAPP_S5_FROZEN_SCENARIOS_v1.1.json")
GATE = os.path.join(UAPP_ROOT, "stages", "UAPP_S5_GATE_v1.4.json")
MANIFEST = os.path.join(UAPP_ROOT, "stages", "UAPP_S5_CANDIDATE_RUN_MANIFEST_v1.4.yaml")
EVIDENCE = os.path.join(UAPP_ROOT, "evidence", "stages", "uapp_s5_v1_4")


def load_module(name: str, path: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


RUNNER = load_module("uapp_s5_runner_for_v15", os.path.join(HERE, "UAPP_S5_RUN_v1.0.py"))
CHECKER = load_module("uapp_s5_checker_v12_for_v15", os.path.join(HERE, "UAPP_S5_VERIFY_v1.2.py"))
RUNNER.SCENARIOS = SCENARIOS
RUNNER.GATE = GATE
RUNNER.MANIFEST = MANIFEST
RUNNER.EVIDENCE = EVIDENCE


def safe_key(key: str) -> str:
    return key.replace(":", "_").replace("/", "_")


def raw_path(key: str) -> str:
    return os.path.join(EVIDENCE, "raw", f"{safe_key(key)}.json")


def check_path(key: str) -> str:
    return os.path.join(EVIDENCE, "checks", f"{safe_key(key)}.json")


RUNNER.raw_path = raw_path
RUNNER.check_path = check_path
CHECKER.EVIDENCE = EVIDENCE
CHECKER.raw_path = raw_path
CHECKER.check_path = check_path
CHECKER.BASE.EVIDENCE = EVIDENCE
CHECKER.BASE.raw_path = raw_path
CHECKER.BASE.check_path = check_path


def frozen() -> tuple[dict[str, Any], dict[str, Any]]:
    for path in (SCENARIOS, MANIFEST, GATE):
        if not os.path.exists(path):
            raise RuntimeError(f"Frozen prerequisite absent: {path}")
    scenarios = RUNNER.load_json(SCENARIOS)
    gate = RUNNER.load_json(GATE)
    if gate.get("document", {}).get("id") != "UAPP_S5_GATE_v1.4":
        raise RuntimeError("Unexpected current Gate identity")
    return scenarios, gate


RUNNER.frozen = frozen
_base_predecessor = RUNNER.predecessor_context


def predecessor_context(
    scenarios: dict[str, Any], turn: dict[str, Any]
) -> tuple[str, str]:
    conversation_id, end_user = _base_predecessor(scenarios, turn)
    if conversation_id:
        return conversation_id, end_user
    return "", f"uapp-s5-v14-{str(turn['conversation_group']).lower()}-20260830"


RUNNER.predecessor_context = predecessor_context


def replays(raw: dict[str, Any]) -> int:
    return sum(max(0, len(rows) - 1) for rows in raw.get("app_runs_in_window", {}).values())


def exclusive(path: str, value: dict[str, Any]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "x", encoding="utf-8") as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--turn")
    parser.add_argument("--preflight", action="store_true")
    parser.add_argument("--run", action="store_true")
    parser.add_argument("--verify", action="store_true")
    parser.add_argument("--final", action="store_true")
    args = parser.parse_args()
    if sum(map(bool, (args.preflight, args.run, args.verify, args.final))) != 1:
        raise SystemExit("choose one mode")
    if args.final:
        result, matrix = CHECKER.verify_final()
        exclusive(CHECKER.RESULT, result)
        exclusive(CHECKER.MATRIX, matrix)
        return 0 if result["S5_TECHNICAL_ACCEPTANCE"] == "PASS" else 1
    if not args.turn:
        raise SystemExit("--turn required")
    if args.preflight:
        result = RUNNER.preflight(args.turn)
        logging.info("%s", json.dumps(result, ensure_ascii=False, sort_keys=True))
        return 0 if result["verdict"] == "PASS" else 1
    if args.run:
        code = RUNNER.run_once(args.turn)
        return 2 if replays(RUNNER.load_json(raw_path(args.turn))) else code
    result = CHECKER.verify_turn(args.turn)
    result["platform_internal_replays"] = replays(CHECKER.load_json(raw_path(args.turn)))
    exclusive(check_path(args.turn), result)
    logging.info("%s", json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0 if result["verdict"] == "PASS" and result["platform_internal_replays"] == 0 else 1


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    raise SystemExit(main())

