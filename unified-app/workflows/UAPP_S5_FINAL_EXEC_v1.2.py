#!/usr/bin/env python3
"""Executor for the single W1 SUT successor and remaining frozen turns."""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
from types import ModuleType
from typing import Any

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
SCENARIOS = os.path.join(ROOT, "stages", "UAPP_S5_FROZEN_SCENARIOS_v1.2.json")
GATE = os.path.join(ROOT, "stages", "UAPP_S5_GATE_v2.2.json")
MANIFEST = os.path.join(ROOT, "stages", "UAPP_S5_FINAL_MANIFEST_v1.0.yaml")
PARENT_EVIDENCE = os.path.join(
    ROOT, "evidence", "stages", "s5_final_convergence_v1_0", "formal"
)
EVIDENCE = os.path.join(
    ROOT, "evidence", "stages", "s5_final_convergence_v1_0", "formal_successor"
)
W0_GATE_SHA256 = "306b4f29ad403e62582991a66095afd1f73e79a6e5ef69b9da7e179fd0aae515"


def load_module(name: str, path: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


BASE = load_module(
    "uapp_s5_final_exec_v11_parent", os.path.join(HERE, "UAPP_S5_FINAL_EXEC_v1.1.py")
)
RUNNER = BASE.RUNNER
CHECKER = BASE.CHECKER
DEPENDENCIES = BASE.DEPENDENCIES


def raw_path(key: str) -> str:
    directory = PARENT_EVIDENCE if key == "UAPP-WITHDRAW-01:W0" else EVIDENCE
    return os.path.join(directory, "raw", f"{BASE.BASE.safe_key(key)}.json")


def check_path(key: str) -> str:
    return os.path.join(EVIDENCE, "checks_v1_2", f"{BASE.BASE.safe_key(key)}.json")


RUNNER.SCENARIOS = SCENARIOS
RUNNER.GATE = GATE
RUNNER.MANIFEST = MANIFEST
RUNNER.EVIDENCE = EVIDENCE
RUNNER.raw_path = raw_path
RUNNER.check_path = check_path


def frozen() -> tuple[dict[str, Any], dict[str, Any]]:
    scenarios = RUNNER.load_json(SCENARIOS)
    gate = RUNNER.load_json(GATE)
    if gate.get("document", {}).get("id") != "UAPP_S5_GATE_v2.2":
        raise RuntimeError("Unexpected W1 successor Gate")
    return scenarios, gate


RUNNER.frozen = frozen


def passed(key: str) -> bool:
    path = check_path(key)
    return os.path.exists(path) and RUNNER.load_json(path).get("verdict") == "PASS"


def predecessor_context(
    scenarios: dict[str, Any], turn: dict[str, Any]
) -> tuple[str, str]:
    index = scenarios["formal_order"].index(turn["key"])
    for previous_key in reversed(scenarios["formal_order"][:index]):
        previous = RUNNER.find_turn(scenarios, previous_key)
        if previous["conversation_group"] != turn["conversation_group"]:
            continue
        if not passed(previous_key):
            raise RuntimeError(
                f"Same-conversation predecessor did not PASS: {previous_key}"
            )
        raw = RUNNER.load_json(raw_path(previous_key))
        return str(raw.get("conversation_id") or ""), str(raw.get("end_user") or "")
    return "", f"uapp-s5-final-{turn['conversation_group'].lower()}-20260830"


RUNNER.predecessor_context = predecessor_context


def preflight(key: str) -> dict[str, Any]:
    scenarios, gate = frozen()
    turn = RUNNER.find_turn(scenarios, key)
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
        "check_absent": not os.path.exists(check_path(key)),
        "direct_prerequisites_pass": all(prerequisites.values()),
        "authorized_set_exact": list(DEPENDENCIES) == gate["formal_execution"]["order"],
    }
    return {
        "turn_key": key,
        "gate_sha256": RUNNER.sha256_file(GATE),
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


def verify(key: str) -> dict[str, Any]:
    scenarios, gate = frozen()
    evaluation_gate = (
        RUNNER.load_json(os.path.join(ROOT, "stages", "UAPP_S5_GATE_v2.0.json"))
        if key == "UAPP-WITHDRAW-01:W0"
        else gate
    )
    raw = RUNNER.load_json(raw_path(key))
    expected_gate = (
        W0_GATE_SHA256 if key == "UAPP-WITHDRAW-01:W0" else RUNNER.sha256_file(GATE)
    )
    if raw.get("gate_sha256") != expected_gate or raw.get(
        "scenarios_sha256"
    ) != RUNNER.sha256_file(SCENARIOS):
        return {
            "turn_key": key,
            "verdict": "NOT_VERIFIED",
            "reason": "Raw binding mismatch",
        }
    turn = RUNNER.find_turn(scenarios, key)
    predecessors = {
        item: RUNNER.load_json(raw_path(item))
        for item in DEPENDENCIES[key]
        if os.path.exists(raw_path(item))
    }
    result = CHECKER.evaluate_turn(raw, turn, evaluation_gate, predecessors)
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
        result = preflight(args.turn)
    elif args.run:
        return RUNNER.run_once(args.turn)
    else:
        result = verify(args.turn)
        CHECKER.exclusive_write(check_path(args.turn), result)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0 if result.get("verdict") == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
