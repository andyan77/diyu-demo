#!/usr/bin/env python3
"""Run and verify one frozen GAP-01 G2 successor S5 turn."""

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
GATE = os.path.join(UAPP_ROOT, "stages", "GAP01_SUCCESSOR_GATE_v1.1.json")
MANIFEST = os.path.join(UAPP_ROOT, "stages", "GAP01_SUCCESSOR_MANIFEST_v1.1.yaml")
EVIDENCE = os.path.join(UAPP_ROOT, "evidence", "stages", "gap01_successor_v1_1", "formal")
EXPECTED_GRAPHS = {
    "UAPP": "aa32b6385de0024d270ec9f85bd78179",
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


BASE = load_module("gap01_v11_exec_base", os.path.join(HERE, "GAP01_SUCCESSOR_EXEC_v1.0.py"))
CHECKER = load_module("gap01_v11_exec_checker", os.path.join(HERE, "GAP01_SUCCESSOR_CHECKER_v1.1.py"))


def safe_key(key: str) -> str:
    return key.replace(":", "_").replace("/", "_")


def raw_path(key: str) -> str:
    return os.path.join(EVIDENCE, "raw", f"{safe_key(key)}.json")


def check_path(key: str) -> str:
    return os.path.join(EVIDENCE, "checks", f"{safe_key(key)}.json")


ORCHESTRATOR = BASE.BASE
RUNNER = ORCHESTRATOR.RUNNER
ORCHESTRATOR.SCENARIOS = SCENARIOS
ORCHESTRATOR.GATE = GATE
ORCHESTRATOR.MANIFEST = MANIFEST
ORCHESTRATOR.EVIDENCE = EVIDENCE
ORCHESTRATOR.EXPECTED_GRAPHS = EXPECTED_GRAPHS
ORCHESTRATOR.raw_path = raw_path
ORCHESTRATOR.check_path = check_path
RUNNER.SCENARIOS = SCENARIOS
RUNNER.GATE = GATE
RUNNER.MANIFEST = MANIFEST
RUNNER.EVIDENCE = EVIDENCE
RUNNER.raw_path = raw_path
RUNNER.check_path = check_path
ORCHESTRATOR.__file__ = __file__
RUNNER.__file__ = __file__


def frozen() -> tuple[dict[str, Any], dict[str, Any]]:
    scenarios = RUNNER.load_json(SCENARIOS)
    gate = RUNNER.load_json(GATE)
    if gate.get("document", {}).get("id") != "GAP01_SUCCESSOR_GATE_v1.1":
        raise RuntimeError("Unexpected GAP-01 successor Gate")
    return scenarios, gate


ORCHESTRATOR.frozen = frozen
RUNNER.frozen = frozen


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--turn", required=True)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--preflight", action="store_true")
    modes.add_argument("--run", action="store_true")
    modes.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    if args.preflight:
        result = ORCHESTRATOR.preflight(args.turn)
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
        return 0 if result["verdict"] == "PASS" else 1
    if args.run:
        return RUNNER.run_once(args.turn)
    result = CHECKER.verify_turn(args.turn)
    ORCHESTRATOR.exclusive(check_path(args.turn), result)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0 if result.get("verdict") == "PASS" else 1


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    raise SystemExit(main())
