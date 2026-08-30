#!/usr/bin/env python3
"""Namespace adapter for the authorized S5 successor formal slot.

The frozen Runner and Checker are imported byte-for-byte.  This adapter only
changes the evidence namespace and first-turn test identity; it does not alter
queries, order, criteria, or adjudication logic.
"""

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
SUCCESSOR_EVIDENCE = os.path.join(UAPP_ROOT, "evidence", "stages", "uapp_s5_successor_v1")
SUCCESSOR_RESULT = os.path.join(UAPP_ROOT, "stages", "UAPP_S5_SUCCESSOR_RESULT_v1.0.json")
SUCCESSOR_MATRIX = os.path.join(UAPP_ROOT, "stages", "UAPP_S5_SUCCESSOR_AC_MATRIX_v1.0.json")
RUNNER_PATH = os.path.join(HERE, "UAPP_S5_RUN_v1.0.py")
CHECKER_PATH = os.path.join(HERE, "UAPP_S5_VERIFY_v1.0.py")
TEST_IDENTITY_PREFIX = "uapp-s5-succ-v1"


def load_module(name: str, path: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


RUNNER = load_module("uapp_s5_successor_frozen_runner", RUNNER_PATH)
CHECKER = load_module("uapp_s5_successor_frozen_checker", CHECKER_PATH)


def safe_key(key: str) -> str:
    return key.replace(":", "_").replace("/", "_")


def raw_path(key: str) -> str:
    return os.path.join(SUCCESSOR_EVIDENCE, "raw", f"{safe_key(key)}.json")


def check_path(key: str) -> str:
    return os.path.join(SUCCESSOR_EVIDENCE, "checks", f"{safe_key(key)}.json")


def exclusive_write(path: str, value: dict[str, Any]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "x", encoding="utf-8") as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


RUNNER.raw_path = raw_path
RUNNER.check_path = check_path
CHECKER.raw_path = raw_path
CHECKER.check_path = check_path

_frozen_predecessor_context = RUNNER.predecessor_context


def successor_predecessor_context(
    scenarios: dict[str, Any], turn: dict[str, Any]
) -> tuple[str, str]:
    conversation_id, end_user = _frozen_predecessor_context(scenarios, turn)
    if conversation_id:
        return conversation_id, end_user
    group = str(turn["conversation_group"]).lower()
    return "", f"{TEST_IDENTITY_PREFIX}-{group}-20260830"


RUNNER.predecessor_context = successor_predecessor_context


def platform_internal_replays(raw: dict[str, Any]) -> int:
    return sum(
        max(0, len(runs) - 1)
        for runs in raw.get("app_runs_in_window", {}).values()
    )


def run_turn(key: str) -> int:
    status = RUNNER.run_once(key)
    raw = RUNNER.load_json(raw_path(key))
    replay_count = platform_internal_replays(raw)
    if replay_count:
        logging.error("platform_internal_replays=%s", replay_count)
        return 2
    return status


def verify_turn(key: str) -> int:
    result = CHECKER.verify_turn(key)
    result["successor_attempt"] = "UAPP-S5-F2-SUCCESSOR-001"
    result["platform_internal_replays"] = platform_internal_replays(
        CHECKER.load_json(raw_path(key))
    )
    exclusive_write(check_path(key), result)
    logging.info("%s", json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0 if result.get("verdict") == "PASS" and result["platform_internal_replays"] == 0 else 1


def verify_final() -> int:
    result, matrix = CHECKER.verify_final()
    result["document"]["id"] = "UAPP_S5_SUCCESSOR_RESULT_v1.0"
    result["successor_attempt"] = "UAPP-S5-F2-SUCCESSOR-001"
    result["previous_invalid_attempt"] = {"top_level_runs": 1, "llm_attempts": 7}
    result["lifetime_top_level_runs"] = 1 + int(result["actual_top_level_runs"])
    result["lifetime_llm_node_attempts"] = 7 + int(result["actual_llm_node_attempts"])
    result["platform_internal_replays"] = sum(
        platform_internal_replays(CHECKER.load_json(raw_path(key)))
        for key in CHECKER.load_json(CHECKER.SCENARIOS)["formal_order"]
    )
    matrix["document"]["id"] = "UAPP_S5_SUCCESSOR_AC_MATRIX_v1.0"
    matrix["successor_attempt"] = "UAPP-S5-F2-SUCCESSOR-001"
    exclusive_write(SUCCESSOR_RESULT, result)
    exclusive_write(SUCCESSOR_MATRIX, matrix)
    logging.info(
        "S5_TECHNICAL_ACCEPTANCE=%s successor_runs=%s successor_llm=%s lifetime_runs=%s lifetime_llm=%s",
        result["S5_TECHNICAL_ACCEPTANCE"],
        result["actual_top_level_runs"],
        result["actual_llm_node_attempts"],
        result["lifetime_top_level_runs"],
        result["lifetime_llm_node_attempts"],
    )
    return 0 if result["S5_TECHNICAL_ACCEPTANCE"] == "PASS" and result["platform_internal_replays"] == 0 else 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--turn")
    parser.add_argument("--preflight", action="store_true")
    parser.add_argument("--run", action="store_true")
    parser.add_argument("--verify", action="store_true")
    parser.add_argument("--final", action="store_true")
    args = parser.parse_args()
    selected = sum(bool(value) for value in (args.preflight, args.run, args.verify, args.final))
    if selected != 1:
        raise SystemExit("Choose exactly one mode")
    if args.final:
        return verify_final()
    if not args.turn:
        raise SystemExit("--turn is required for preflight/run/verify")
    if args.preflight:
        result = RUNNER.preflight(args.turn)
        logging.info("%s", json.dumps(result, ensure_ascii=False, sort_keys=True))
        return 0 if result.get("verdict") == "PASS" else 1
    if args.run:
        return run_turn(args.turn)
    return verify_turn(args.turn)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    raise SystemExit(main())
