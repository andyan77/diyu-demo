#!/usr/bin/env python3
"""Run one of the eleven frozen S5 final-convergence turns exactly once."""

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
SCENARIOS = os.path.join(UAPP_ROOT, "stages", "UAPP_S5_FROZEN_SCENARIOS_v1.2.json")
GATE = os.path.join(UAPP_ROOT, "stages", "UAPP_S5_GATE_v2.0.json")
MANIFEST = os.path.join(UAPP_ROOT, "stages", "UAPP_S5_FINAL_MANIFEST_v1.0.yaml")
EVIDENCE = os.path.join(
    UAPP_ROOT, "evidence", "stages", "s5_final_convergence_v1_0", "formal"
)

DEPENDENCIES: dict[str, list[str]] = {
    "UAPP-WITHDRAW-01:W0": [],
    "UAPP-WITHDRAW-01:W1": ["UAPP-WITHDRAW-01:W0"],
    "UAPP-EQUIV-01a": [],
    "UAPP-EQUIV-01b": [],
    "UAPP-EQUIV-01c": [],
    "UAPP-EQUIV-01n": [],
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


RUNNER = load_module(
    "uapp_s5_final_base_runner", os.path.join(HERE, "UAPP_S5_RUN_v1.0.py")
)
CHECKER = load_module(
    "uapp_s5_final_checker", os.path.join(HERE, "UAPP_S5_FINAL_CHECKER_v1.0.py")
)
RUNNER.SCENARIOS = SCENARIOS
RUNNER.GATE = GATE
RUNNER.MANIFEST = MANIFEST
RUNNER.EVIDENCE = EVIDENCE
CHECKER.SCENARIOS = SCENARIOS
CHECKER.GATE = GATE
CHECKER.EVIDENCE = EVIDENCE


def safe_key(key: str) -> str:
    return key.replace(":", "_").replace("/", "_")


def raw_path(key: str) -> str:
    return os.path.join(EVIDENCE, "raw", f"{safe_key(key)}.json")


def check_path(key: str) -> str:
    return os.path.join(EVIDENCE, "checks", f"{safe_key(key)}.json")


RUNNER.raw_path = raw_path
RUNNER.check_path = check_path
CHECKER.raw_path = raw_path
CHECKER.check_path = check_path


def frozen() -> tuple[dict[str, Any], dict[str, Any]]:
    scenarios = RUNNER.load_json(SCENARIOS)
    gate = RUNNER.load_json(GATE)
    if gate.get("document", {}).get("id") != "UAPP_S5_GATE_v2.0":
        raise RuntimeError("Unexpected S5 final Gate")
    return scenarios, gate


RUNNER.frozen = frozen


def passed(key: str) -> bool:
    path = check_path(key)
    return os.path.exists(path) and RUNNER.load_json(path).get("verdict") == "PASS"


def predecessor_context(
    scenarios: dict[str, Any], turn: dict[str, Any]
) -> tuple[str, str]:
    order = scenarios["formal_order"]
    index = order.index(turn["key"])
    for previous_key in reversed(order[:index]):
        previous = RUNNER.find_turn(scenarios, previous_key)
        if previous["conversation_group"] != turn["conversation_group"]:
            continue
        if not passed(previous_key):
            raise RuntimeError(
                f"Same-conversation predecessor did not PASS: {previous_key}"
            )
        evidence = RUNNER.load_json(raw_path(previous_key))
        return str(evidence.get("conversation_id") or ""), str(
            evidence.get("end_user") or ""
        )
    return "", f"uapp-s5-final-{turn['conversation_group'].lower()}-20260830"


RUNNER.predecessor_context = predecessor_context


def preflight(key: str) -> dict[str, Any]:
    scenarios, gate = frozen()
    turn = RUNNER.find_turn(scenarios, key)
    if key not in DEPENDENCIES:
        raise RuntimeError("Turn is outside the authorized final set")
    apps = RUNNER.STATE.protected_apps()
    active = int(
        RUNNER.BASE.psql("select count(*) from workflow_runs where status='running';")
    )
    console = RUNNER.DC.Console(env=RUNNER.DC.load_env(RUNNER.ENV_FILE))
    conversation_id, end_user = predecessor_context(scenarios, turn)
    prerequisites = {item: passed(item) for item in DEPENDENCIES[key]}
    checks = {
        "scenario_hash": RUNNER.sha256_file(SCENARIOS)
        == gate["frozen_files"]["scenarios_sha256"],
        "manifest_hash": RUNNER.sha256_file(MANIFEST)
        == gate["frozen_files"]["manifest_sha256"],
        "executor_hash": RUNNER.sha256_file(__file__)
        == gate["frozen_files"]["executor_sha256"],
        "checker_hash": RUNNER.sha256_file(CHECKER.__file__)
        == gate["frozen_files"]["checker_sha256"],
        "candidate_graphs": all(
            apps[name]["graph_md5"] == value
            for name, value in gate["candidate"]["graph_md5"].items()
        ),
        "no_active_runs": active == 0,
        "global_m2_guard": RUNNER.global_m2_guard()
        == gate["protected_surface"]["global_m2_before"],
        "api_key_present": bool(
            console.app_api_key(RUNNER.UAPP_APP_ID, create_if_missing=False)
        ),
        "raw_absent": not os.path.exists(raw_path(key)),
        "direct_prerequisites_pass": all(prerequisites.values()),
        "authorized_set_exact": list(DEPENDENCIES) == gate["formal_execution"]["order"],
        "budget": gate["budget"]["formal_top_level_runs_max"] == 13
        and gate["budget"]["llm_node_attempts_max"] == 78,
    }
    return {
        "turn_key": key,
        "gate_sha256": RUNNER.sha256_file(GATE),
        "scenarios_sha256": RUNNER.sha256_file(SCENARIOS),
        "runner_sha256": RUNNER.sha256_file(__file__),
        "checker_sha256": RUNNER.sha256_file(CHECKER.__file__),
        "conversation_id": conversation_id,
        "end_user": end_user,
        "apps": apps,
        "active_runs": active,
        "global_m2": RUNNER.global_m2_guard(),
        "prerequisites": prerequisites,
        "checks": checks,
        "verdict": "PASS" if all(checks.values()) else "FAIL",
    }


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
    RUNNER.exclusive_write(check_path(args.turn), result)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0 if result.get("verdict") == "PASS" else 1


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    raise SystemExit(main())
