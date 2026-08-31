#!/usr/bin/env python3
"""Executor successor binding the schema-compatible S5 checker."""

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


BASE = load_module(
    "uapp_s5_final_exec_v12_parent",
    os.path.join(HERE, "UAPP_S5_FINAL_EXEC_v1.2.py"),
)
CHECKER = load_module(
    "uapp_s5_final_checker_v11",
    os.path.join(HERE, "UAPP_S5_FINAL_CHECKER_v1.1.py"),
)
GATE = os.path.join(BASE.ROOT, "stages", "UAPP_S5_GATE_v2.3.json")
CHECKS = os.path.join(BASE.EVIDENCE, "checks_v1_3")


def check_path(key: str) -> str:
    return os.path.join(CHECKS, f"{BASE.BASE.BASE.safe_key(key)}.json")


def frozen() -> tuple[dict[str, object], dict[str, object]]:
    scenarios = BASE.RUNNER.load_json(BASE.SCENARIOS)
    gate = BASE.RUNNER.load_json(GATE)
    if gate.get("document", {}).get("id") != "UAPP_S5_GATE_v2.3":
        raise RuntimeError("Unexpected checker successor Gate")
    return scenarios, gate


BASE.GATE = GATE
BASE.CHECKER = CHECKER
BASE.check_path = check_path
BASE.RUNNER.GATE = GATE
BASE.RUNNER.check_path = check_path
BASE.RUNNER.frozen = frozen

PARENT_GATE_SHA256 = "53e6215f0d1d2e4c4b19e7f45919eb1d9b9844be8a45a5aa9b0b5b3f694ac614"


def preflight(key: str) -> dict[str, Any]:
    scenarios, gate = frozen()
    turn = BASE.RUNNER.find_turn(scenarios, key)
    apps = BASE.RUNNER.STATE.protected_apps()
    active = int(
        BASE.RUNNER.BASE.psql(
            "select count(*) from workflow_runs where status='running';"
        )
    )
    console = BASE.RUNNER.DC.Console(
        env=BASE.RUNNER.DC.load_env(BASE.RUNNER.ENV_FILE)
    )
    conversation_id, end_user = BASE.predecessor_context(scenarios, turn)
    prerequisites = {
        item: BASE.passed(item) for item in BASE.DEPENDENCIES[key]
    }
    checks = {
        "scenario_hash": BASE.RUNNER.sha256_file(BASE.SCENARIOS)
        == gate["frozen_files"]["scenarios_sha256"],
        "manifest_hash": BASE.RUNNER.sha256_file(BASE.MANIFEST)
        == gate["frozen_files"]["manifest_sha256"],
        "executor_hash": BASE.RUNNER.sha256_file(__file__)
        == gate["frozen_files"]["executor_sha256"],
        "checker_hash": BASE.RUNNER.sha256_file(CHECKER.__file__)
        == gate["frozen_files"]["checker_sha256"],
        "candidate_graphs": all(
            apps[name]["graph_md5"] == value
            for name, value in gate["candidate"]["graph_md5"].items()
        ),
        "no_active_runs": active == 0,
        "global_m2_guard": BASE.RUNNER.global_m2_guard()
        == gate["protected_surface"]["global_m2_before"],
        "api_key_present": bool(
            console.app_api_key(BASE.RUNNER.UAPP_APP_ID, create_if_missing=False)
        ),
        "raw_absent": not os.path.exists(BASE.raw_path(key)),
        "check_absent": not os.path.exists(check_path(key)),
        "direct_prerequisites_pass": all(prerequisites.values()),
        "authorized_set_exact": list(BASE.DEPENDENCIES)
        == gate["formal_execution"]["order"],
    }
    return {
        "turn_key": key,
        "gate_sha256": BASE.RUNNER.sha256_file(GATE),
        "conversation_id": conversation_id,
        "end_user": end_user,
        "apps": apps,
        "active_runs": active,
        "global_m2": BASE.RUNNER.global_m2_guard(),
        "prerequisites": prerequisites,
        "checks": checks,
        "verdict": "PASS" if all(checks.values()) else "FAIL",
    }


def verify(key: str) -> dict[str, Any]:
    scenarios, gate = frozen()
    raw = BASE.RUNNER.load_json(BASE.raw_path(key))
    expected_gate = (
        PARENT_GATE_SHA256
        if key == "UAPP-EQUIV-01a"
        else BASE.RUNNER.sha256_file(GATE)
    )
    if raw.get("gate_sha256") != expected_gate or raw.get(
        "scenarios_sha256"
    ) != BASE.RUNNER.sha256_file(BASE.SCENARIOS):
        return {
            "turn_key": key,
            "verdict": "NOT_VERIFIED",
            "reason": "Raw binding mismatch",
        }
    turn = BASE.RUNNER.find_turn(scenarios, key)
    predecessors = {
        item: BASE.RUNNER.load_json(BASE.raw_path(item))
        for item in BASE.DEPENDENCIES[key]
        if os.path.exists(BASE.raw_path(item))
    }
    result = CHECKER.evaluate_turn(raw, turn, gate, predecessors)
    result["adjudication_gate_sha256"] = BASE.RUNNER.sha256_file(GATE)
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
        result = preflight(args.turn)
    elif args.run:
        return BASE.RUNNER.run_once(args.turn)
    else:
        result = verify(args.turn)
        CHECKER.exclusive_write(check_path(args.turn), result)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0 if result.get("verdict") == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
