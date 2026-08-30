#!/usr/bin/env python3
"""Continue the 13 frozen S5 turns after CAP-06 PASS on the same candidate."""

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
GATE = os.path.join(UAPP_ROOT, "stages", "UAPP_S5_GATE_v1.9.json")
MANIFEST = os.path.join(UAPP_ROOT, "stages", "UAPP_S5_CANDIDATE_RUN_MANIFEST_v1.8.yaml")
EVIDENCE = os.path.join(UAPP_ROOT, "evidence", "stages", "uapp_s5_post_cap06_v1_0")
RESULT = os.path.join(UAPP_ROOT, "stages", "UAPP_S5_RESULT_v1.6.json")
MATRIX = os.path.join(UAPP_ROOT, "stages", "UAPP_S5_AC_MATRIX_v1.6.json")
INHERITED = {
    "UAPP-CAP-01": os.path.join(UAPP_ROOT, "evidence", "stages", "uapp_s5_v1_4", "checks", "UAPP-CAP-01.json"),
    "UAPP-CAP-02": os.path.join(UAPP_ROOT, "evidence", "stages", "uapp_s5_v1_4", "checks", "UAPP-CAP-02.json"),
    "UAPP-CAP-03": os.path.join(UAPP_ROOT, "evidence", "stages", "uapp_s5_v1_4", "checks", "UAPP-CAP-03.json"),
    "UAPP-CAP-04": os.path.join(UAPP_ROOT, "evidence", "stages", "uapp_s5_v1_4", "checks", "UAPP-CAP-04.json"),
    "UAPP-CAP-05": os.path.join(UAPP_ROOT, "evidence", "stages", "uapp_s5_inline_artifact_successor_v1_0", "formal", "checks", "UAPP-CAP-05.json"),
    "UAPP-CAP-06": os.path.join(UAPP_ROOT, "stages", "CAP06_FORMAL_RESULT_v1.1.json"),
}
EXPECTED_GRAPHS = {
    "UAPP": "7932502949d91ad366a4fa70d39a8a56",
    "M3": "cd93757bcf8ad322f3b32fc43b2da3ff",
    "HOP": "e38378c3c2a66b75aa7e645368c9e1ce",
    "SEAM": "db49a3da8973d4fdcbe9ecf63bdf7e2a",
    "MATRIX": "6cdaeac9cacf69fbeea4bd25e1536ace",
    "CAMPAIGN": "4876dacc43a73741b41c5a3083796347",
    "CONTENT_BRIEF": "0c841642a71feedfb327ffb76aec0ddd",
    "CREATIVE_SCRIPT": "a1cd859d5b88d0d025f336665ca94e51",
    "PRODUCTION_DIRECTOR": "964e9a947dc9790d1de82496469689ad",
    "PUBLISHING_PACKAGING": "99287feadcd784e86bf4c298bea555fc",
    "PP_provider": "99287feadcd784e86bf4c298bea555fc",
}


def load_module(name: str, path: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


RUNNER = load_module("s5_post_cap06_runner", os.path.join(HERE, "UAPP_S5_RUN_v1.0.py"))
CHECKER = load_module("s5_post_cap06_checker", os.path.join(HERE, "UAPP_S5_VERIFY_v1.2.py"))
RUNNER.SCENARIOS = SCENARIOS
RUNNER.GATE = GATE
RUNNER.MANIFEST = MANIFEST
RUNNER.EVIDENCE = EVIDENCE
CHECKER.SCENARIOS = SCENARIOS
CHECKER.GATE = GATE
CHECKER.EVIDENCE = EVIDENCE
CHECKER.RESULT = RESULT
CHECKER.MATRIX = MATRIX
CHECKER.BASE.SCENARIOS = SCENARIOS
CHECKER.BASE.GATE = GATE
CHECKER.BASE.EVIDENCE = EVIDENCE
CHECKER.BASE.RESULT = RESULT
CHECKER.BASE.MATRIX = MATRIX


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
CHECKER.BASE.raw_path = raw_path
CHECKER.BASE.check_path = check_path


def frozen() -> tuple[dict[str, Any], dict[str, Any]]:
    scenarios = RUNNER.load_json(SCENARIOS)
    gate = RUNNER.load_json(GATE)
    if gate.get("document", {}).get("id") != "UAPP_S5_GATE_v1.9":
        raise RuntimeError("Unexpected S5 Gate")
    return scenarios, gate


RUNNER.frozen = frozen


def passed(key: str) -> bool:
    path = INHERITED.get(key, check_path(key))
    return os.path.exists(path) and RUNNER.load_json(path).get("verdict") == "PASS"


def predecessor_context(
    scenarios: dict[str, Any], turn: dict[str, Any]
) -> tuple[str, str]:
    order = scenarios["formal_order"]
    for previous_key in reversed(order[:order.index(turn["key"])]):
        previous = RUNNER.find_turn(scenarios, previous_key)
        if previous["conversation_group"] != turn["conversation_group"]:
            continue
        if not passed(previous_key) or not os.path.exists(raw_path(previous_key)):
            raise RuntimeError(f"Current predecessor unavailable: {previous_key}")
        evidence = RUNNER.load_json(raw_path(previous_key))
        return str(evidence.get("conversation_id") or ""), str(evidence.get("end_user") or "")
    return "", f"uapp-s5-post-cap06-{str(turn['conversation_group']).lower()}-20260830"


RUNNER.predecessor_context = predecessor_context


def preflight(key: str) -> dict[str, Any]:
    scenarios, gate = frozen()
    turn = RUNNER.find_turn(scenarios, key)
    if key in INHERITED:
        raise RuntimeError("Inherited CAP evidence must not be rerun")
    prior = scenarios["formal_order"][:scenarios["formal_order"].index(key)]
    apps = RUNNER.STATE.protected_apps()
    active = int(RUNNER.BASE.psql("select count(*) from workflow_runs where status='running';"))
    console = RUNNER.DC.Console(env=RUNNER.DC.load_env(RUNNER.ENV_FILE))
    conversation_id, end_user = predecessor_context(scenarios, turn)
    checks = {
        "scenario_hash": RUNNER.sha256_file(SCENARIOS) == gate["frozen_files"]["scenarios_sha256"],
        "executor_hash": RUNNER.sha256_file(__file__) == gate["frozen_files"]["executor_sha256"],
        "candidate_graphs": all(apps[name]["graph_md5"] == value for name, value in EXPECTED_GRAPHS.items()),
        "no_active_runs": active == 0,
        "global_m2_guard": RUNNER.global_m2_guard() == gate["protected_surface"]["global_m2_before"],
        "api_key_present": bool(console.app_api_key(RUNNER.UAPP_APP_ID, create_if_missing=False)),
        "raw_absent": not os.path.exists(raw_path(key)),
        "all_prior_pass": all(passed(item) for item in prior),
        "remaining_budget": len([item for item in scenarios["formal_order"] if item not in INHERITED]) == 13,
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
        "checks": checks,
        "verdict": "PASS" if all(checks.values()) else "FAIL",
    }


RUNNER.preflight = preflight


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
    args = parser.parse_args()
    if sum(map(bool, (args.preflight, args.run, args.verify))) != 1 or not args.turn:
        raise SystemExit("choose one mode and one turn")
    if args.preflight:
        result = preflight(args.turn)
        logging.info("%s", json.dumps(result, ensure_ascii=False, sort_keys=True))
        return 0 if result["verdict"] == "PASS" else 1
    if args.run:
        return RUNNER.run_once(args.turn)
    result = CHECKER.verify_turn(args.turn)
    exclusive(check_path(args.turn), result)
    logging.info("%s", json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0 if result.get("verdict") == "PASS" else 1


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    raise SystemExit(main())
