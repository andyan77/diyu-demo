#!/usr/bin/env python3
"""Run the one frozen CAP-06 formal turn and preserve raw evidence."""

from __future__ import annotations

import importlib.util
import json
import logging
import os
from types import ModuleType
from typing import Any

HERE = os.path.dirname(os.path.abspath(__file__))
UAPP_ROOT = os.path.abspath(os.path.join(HERE, ".."))
SCENARIOS = os.path.join(UAPP_ROOT, "stages", "UAPP_S5_FROZEN_SCENARIOS_v1.1.json")
GATE = os.path.join(UAPP_ROOT, "stages", "CAP06_FROZEN_GATE_v1.2.json")
MANIFEST = os.path.join(UAPP_ROOT, "stages", "UAPP_S5_CANDIDATE_RUN_MANIFEST_v1.8.yaml")
EVIDENCE = os.path.join(UAPP_ROOT, "evidence", "stages", "cap06_semantic_contract_v1_0", "formal")
RAW = os.path.join(EVIDENCE, "CAP06_FORMAL_RAW_v1.0.json")
CAP05_CHECK = os.path.join(
    UAPP_ROOT,
    "evidence",
    "stages",
    "uapp_s5_inline_artifact_successor_v1_0",
    "formal",
    "checks",
    "UAPP-CAP-05.json",
)
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
}


def load_module(name: str, path: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


BASE = load_module("cap06_formal_base", os.path.join(HERE, "UAPP_S5_RUN_v1.0.py"))
BASE.SCENARIOS = SCENARIOS
BASE.GATE = GATE
BASE.MANIFEST = MANIFEST
BASE.EVIDENCE = EVIDENCE
BASE.raw_path = lambda _key: RAW
BASE.check_path = lambda _key: os.path.join(EVIDENCE, "CAP06_FORMAL_RESULT_v1.0.json")


def frozen() -> tuple[dict[str, Any], dict[str, Any]]:
    scenarios = BASE.load_json(SCENARIOS)
    gate = BASE.load_json(GATE)
    if gate.get("document", {}).get("id") != "CAP06_FROZEN_GATE_v1.2":
        raise RuntimeError("Unexpected CAP-06 Gate")
    return scenarios, gate


def predecessor_context(
    _scenarios: dict[str, Any], _turn: dict[str, Any]
) -> tuple[str, str]:
    return "", "uapp-cap06-contract-v1-20260830"


def preflight(key: str) -> dict[str, Any]:
    if key != "UAPP-CAP-06":
        raise RuntimeError("Only UAPP-CAP-06 is authorized")
    scenarios, gate = frozen()
    turn = BASE.find_turn(scenarios, key)
    apps = BASE.STATE.protected_apps()
    active = int(BASE.BASE.psql("select count(*) from workflow_runs where status='running';"))
    console = BASE.DC.Console(env=BASE.DC.load_env(BASE.ENV_FILE))
    api_key = bool(console.app_api_key(BASE.UAPP_APP_ID, create_if_missing=False))
    cap05 = BASE.load_json(CAP05_CHECK)
    checks = {
        "original_input": turn["query"]
        == next(row for row in scenarios["turns"] if row["key"] == key)["query"],
        "scenario_hash": BASE.sha256_file(SCENARIOS)
        == gate["inheritance"]["scenario_sha256"],
        "runner_hash": BASE.sha256_file(__file__) == gate["frozen_files"]["runner_sha256"],
        "checker_hash": BASE.sha256_file(
            os.path.join(HERE, "CAP06_FORMAL_VERIFY_v1.0.py")
        ) == gate["frozen_files"]["checker_sha256"],
        "candidate_graphs": all(
            apps[name]["graph_md5"] == value for name, value in EXPECTED_GRAPHS.items()
        ),
        "no_active_runs": active == 0,
        "api_key_present": api_key,
        "raw_absent": not os.path.exists(RAW),
        "cap05_inherited_current": cap05.get("verdict") == "PASS",
        "global_m2_guard": BASE.global_m2_guard() == gate["protected_surface"]["global_m2"],
        "budget": gate["budget"]["formal_runs_max"] == 2
        and gate["budget"]["llm_attempts_max"] == 14,
    }
    return {
        "turn_key": key,
        "gate_sha256": BASE.sha256_file(GATE),
        "scenarios_sha256": BASE.sha256_file(SCENARIOS),
        "runner_sha256": BASE.sha256_file(__file__),
        "conversation_id": "",
        "end_user": "uapp-cap06-contract-v1-20260830",
        "apps": apps,
        "active_runs": active,
        "global_m2": BASE.global_m2_guard(),
        "api_key_present": api_key,
        "raw_path_absent": not os.path.exists(RAW),
        "checks": checks,
        "verdict": "PASS" if all(checks.values()) else "FAIL",
    }


BASE.frozen = frozen
BASE.predecessor_context = predecessor_context
BASE.preflight = preflight


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--preflight", action="store_true")
    parser.add_argument("--run", action="store_true")
    args = parser.parse_args()
    if args.preflight == args.run:
        raise SystemExit("choose one mode")
    if args.preflight:
        report = preflight("UAPP-CAP-06")
        logging.info("%s", json.dumps(report, ensure_ascii=False, sort_keys=True))
        return 0 if report["verdict"] == "PASS" else 1
    return BASE.run_once("UAPP-CAP-06")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    raise SystemExit(main())

