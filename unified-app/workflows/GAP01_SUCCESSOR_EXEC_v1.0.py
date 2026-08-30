#!/usr/bin/env python3
"""Run and verify one frozen GAP-01 successor S5 turn."""

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
GATE = os.path.join(UAPP_ROOT, "stages", "GAP01_SUCCESSOR_GATE_v1.0.json")
MANIFEST = os.path.join(UAPP_ROOT, "stages", "GAP01_SUCCESSOR_MANIFEST_v1.0.yaml")
EVIDENCE = os.path.join(UAPP_ROOT, "evidence", "stages", "gap01_successor_v1_0", "formal")
EXPECTED_GRAPHS = {
    "UAPP": "ff411f51a1916c1ea9dfbd96a9841f12",
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


BASE = load_module("gap01_exec_base", os.path.join(HERE, "UAPP_S5_POST_CAP06_EXEC_v1.0.py"))
CHECKER = load_module("gap01_exec_checker", os.path.join(HERE, "GAP01_SUCCESSOR_CHECKER_v1.0.py"))
BASE.SCENARIOS = SCENARIOS
BASE.GATE = GATE
BASE.MANIFEST = MANIFEST
BASE.EVIDENCE = EVIDENCE
BASE.EXPECTED_GRAPHS = EXPECTED_GRAPHS
BASE.RUNNER.SCENARIOS = SCENARIOS
BASE.RUNNER.GATE = GATE
BASE.RUNNER.MANIFEST = MANIFEST
BASE.RUNNER.EVIDENCE = EVIDENCE
# Both inherited functions hash their module-global __file__. Bind them to this
# exact executor so RAW and Gate identify the actual orchestration entrypoint.
BASE.__file__ = __file__
BASE.RUNNER.__file__ = __file__


def frozen() -> tuple[dict[str, Any], dict[str, Any]]:
    scenarios = BASE.RUNNER.load_json(SCENARIOS)
    gate = BASE.RUNNER.load_json(GATE)
    if gate.get("document", {}).get("id") != "GAP01_SUCCESSOR_GATE_v1.0":
        raise RuntimeError("Unexpected GAP-01 successor Gate")
    return scenarios, gate


BASE.frozen = frozen
BASE.RUNNER.frozen = frozen


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--turn", required=True)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--preflight", action="store_true")
    modes.add_argument("--run", action="store_true")
    modes.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    if args.preflight:
        result = BASE.preflight(args.turn)
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
        return 0 if result["verdict"] == "PASS" else 1
    if args.run:
        return BASE.RUNNER.run_once(args.turn)
    result = CHECKER.verify_turn(args.turn)
    BASE.exclusive(BASE.check_path(args.turn), result)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0 if result.get("verdict") == "PASS" else 1


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    raise SystemExit(main())
