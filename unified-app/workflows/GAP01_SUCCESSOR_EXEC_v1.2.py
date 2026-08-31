#!/usr/bin/env python3
"""Dependency-aware continuation runner for unaffected frozen S5 turns."""

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
GATE = os.path.join(UAPP_ROOT, "stages", "GAP01_SUCCESSOR_GATE_v1.2.json")
MANIFEST = os.path.join(UAPP_ROOT, "stages", "GAP01_SUCCESSOR_MANIFEST_v1.2.yaml")
EVIDENCE = os.path.join(UAPP_ROOT, "evidence", "stages", "gap01_successor_v1_1", "formal")
DEPENDENCIES = {
    "UAPP-EQUIV-01n": [],
    "UAPP-WITHDRAW-01:W0": [],
    "UAPP-WITHDRAW-01:W1": ["UAPP-WITHDRAW-01:W0"],
    "UAPP-FULL-01:T1": [],
    "UAPP-FULL-01:T2": ["UAPP-FULL-01:T1"],
    "UAPP-FULL-01:T3": ["UAPP-FULL-01:T2"],
    "UAPP-FULL-01:T4": ["UAPP-FULL-01:T3"],
    "UAPP-RECOVERY-01:R1": ["UAPP-FULL-01:T4"],
}


def load_module(name: str, path: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


BASE = load_module("gap01_v12_exec_base", os.path.join(HERE, "GAP01_SUCCESSOR_EXEC_v1.1.py"))
CHECKER = load_module("gap01_v12_exec_checker", os.path.join(HERE, "GAP01_SUCCESSOR_CHECKER_v1.1.py"))
ORCHESTRATOR = BASE.ORCHESTRATOR
RUNNER = BASE.RUNNER
ORCHESTRATOR.GATE = GATE
ORCHESTRATOR.MANIFEST = MANIFEST
RUNNER.GATE = GATE
RUNNER.MANIFEST = MANIFEST
CHECKER.GATE = GATE
CHECKER.BASE.GATE = GATE
CHECKER.BASE.BASE.GATE = GATE
ORCHESTRATOR.__file__ = __file__
RUNNER.__file__ = __file__


def frozen() -> tuple[dict[str, Any], dict[str, Any]]:
    scenarios = RUNNER.load_json(SCENARIOS)
    gate = RUNNER.load_json(GATE)
    if gate.get("document", {}).get("id") != "GAP01_SUCCESSOR_GATE_v1.2":
        raise RuntimeError("Unexpected dependency-aware Gate")
    return scenarios, gate


ORCHESTRATOR.frozen = frozen
RUNNER.frozen = frozen


def preflight(key: str) -> dict[str, Any]:
    scenarios, gate = frozen()
    turn = RUNNER.find_turn(scenarios, key)
    if key not in DEPENDENCIES:
        raise RuntimeError("Turn is not authorized by the dependency-aware continuation")
    apps = RUNNER.STATE.protected_apps()
    active = int(RUNNER.BASE.psql("select count(*) from workflow_runs where status='running';"))
    console = RUNNER.DC.Console(env=RUNNER.DC.load_env(RUNNER.ENV_FILE))
    conversation_id, end_user = ORCHESTRATOR.predecessor_context(scenarios, turn)
    prerequisites = {item: ORCHESTRATOR.passed(item) for item in DEPENDENCIES[key]}
    checks = {
        "scenario_hash": RUNNER.sha256_file(SCENARIOS) == gate["frozen_files"]["scenarios_sha256"],
        "executor_hash": RUNNER.sha256_file(__file__) == gate["frozen_files"]["executor_sha256"],
        "candidate_graphs": all(
            apps[name]["graph_md5"] == value for name, value in gate["candidate"]["graph_md5"].items()
        ),
        "no_active_runs": active == 0,
        "global_m2_guard": RUNNER.global_m2_guard() == gate["protected_surface"]["global_m2_before"],
        "api_key_present": bool(console.app_api_key(RUNNER.UAPP_APP_ID, create_if_missing=False)),
        "raw_absent": not os.path.exists(ORCHESTRATOR.raw_path(key)),
        "direct_prerequisites_pass": all(prerequisites.values()),
        "independent_continuation_budget": len(DEPENDENCIES) == 8,
    }
    return {
        "turn_key": key,
        "gate_sha256": RUNNER.sha256_file(GATE),
        "scenarios_sha256": RUNNER.sha256_file(SCENARIOS),
        "runner_sha256": RUNNER.sha256_file(__file__),
        "conversation_id": conversation_id,
        "end_user": end_user,
        "apps": apps,
        "active_runs": active,
        "global_m2": RUNNER.global_m2_guard(),
        "api_key_present": checks["api_key_present"],
        "raw_path_absent": checks["raw_absent"],
        "prerequisites": prerequisites,
        "checks": checks,
        "verdict": "PASS" if all(checks.values()) else "FAIL",
    }


ORCHESTRATOR.preflight = preflight
RUNNER.preflight = preflight


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--turn", required=True)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--preflight", action="store_true")
    modes.add_argument("--run", action="store_true")
    modes.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    if args.preflight:
        result = preflight(args.turn)
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
        return 0 if result["verdict"] == "PASS" else 1
    if args.run:
        return RUNNER.run_once(args.turn)
    result = CHECKER.verify_turn(args.turn)
    ORCHESTRATOR.exclusive(ORCHESTRATOR.check_path(args.turn), result)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0 if result.get("verdict") == "PASS" else 1


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    raise SystemExit(main())
