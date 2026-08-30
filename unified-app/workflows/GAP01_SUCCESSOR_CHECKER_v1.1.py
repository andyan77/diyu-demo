#!/usr/bin/env python3
"""Versioned GAP-01 checker accepting a legal, non-repeated next gap."""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
from types import ModuleType
from typing import Any

HERE = os.path.dirname(os.path.abspath(__file__))
UAPP_ROOT = os.path.abspath(os.path.join(HERE, ".."))
SCENARIOS = os.path.join(UAPP_ROOT, "stages", "UAPP_S5_FROZEN_SCENARIOS_v1.1.json")
GATE = os.path.join(UAPP_ROOT, "stages", "GAP01_SUCCESSOR_GATE_v1.1.json")
EVIDENCE = os.path.join(UAPP_ROOT, "evidence", "stages", "gap01_successor_v1_1", "formal")


def load_module(name: str, path: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


BASE = load_module("gap01_v11_checker_base", os.path.join(HERE, "GAP01_SUCCESSOR_CHECKER_v1.0.py"))
BASE.SCENARIOS = SCENARIOS
BASE.GATE = GATE
BASE.EVIDENCE = EVIDENCE
BASE.BASE.SCENARIOS = SCENARIOS
BASE.BASE.GATE = GATE
BASE.BASE.EVIDENCE = EVIDENCE
BASE.BASE.BASE.SCENARIOS = SCENARIOS
BASE.BASE.BASE.GATE = GATE
BASE.BASE.BASE.EVIDENCE = EVIDENCE


def safe_key(key: str) -> str:
    return key.replace(":", "_").replace("/", "_")


def raw_path(key: str) -> str:
    return os.path.join(EVIDENCE, "raw", f"{safe_key(key)}.json")


def check_path(key: str) -> str:
    return os.path.join(EVIDENCE, "checks", f"{safe_key(key)}.json")


BASE.raw_path = raw_path
BASE.check_path = check_path
BASE.BASE.raw_path = raw_path
BASE.BASE.check_path = check_path
BASE.BASE.BASE.raw_path = raw_path
BASE.BASE.BASE.check_path = check_path


def legal_next_gap(answer: str, missing: str, returns_status: str) -> dict[str, bool]:
    repeated_promise = "content_promise" in missing or any(
        token in answer for token in ("内容对观众的承诺", "她能拿到什么", "看完能得到什么")
    )
    repeated_route = any(token in answer for token in ("整体发布节奏", "具体商品或内容方向"))
    precise = BASE.question_count(answer) == 1 and bool(answer.strip())
    component_return = returns_status == "COMPONENT_RETURN"
    return {
        "component_return": component_return,
        "one_precise_question": precise,
        "does_not_repeat_promise": not repeated_promise,
        "does_not_repeat_g1": not repeated_route,
    }


def evaluate_turn(
    raw: dict[str, Any],
    turn: dict[str, Any],
    gate: dict[str, Any],
    predecessors: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    result = BASE.evaluate_turn(raw, turn, gate, predecessors)
    if turn["key"] != "UAPP-GAP-01:G2":
        return result
    checks = [item for item in result["checks"] if item["id"] not in ("GAP-S6", "GAP-S7")]
    answer = str(raw.get("answer") or "")
    route = BASE.BASE.BASE.node_output(raw, "uapp_route")
    target = str(route.get("target_capability") or "")
    observation = BASE.BASE.artifact_observation(raw, target) if target in BASE.CAPABILITIES else {"checks": {}}
    artifact_valid = bool(observation.get("checks")) and all(observation["checks"].values())
    target_runs = raw.get("app_runs_in_window", {}).get(target) or []
    outputs = {}
    if target_runs:
        try:
            outputs = json.loads(target_runs[0].get("outputs") or "{}")
        except json.JSONDecodeError:
            outputs = {}
    gap_checks = legal_next_gap(
        answer,
        str(outputs.get("missing") or ""),
        str(outputs.get("returns_status") or ""),
    )
    BASE.add_check(
        checks,
        "GAP-S6",
        artifact_valid or all(gap_checks.values()),
        {"artifact_valid": artifact_valid, "artifact": observation, "legal_next_gap": gap_checks},
    )
    BASE.add_check(
        checks,
        "GAP-S7",
        not BASE.BASE.BASE.node_executed(raw, "uapp_ask_one")
        and gap_checks["does_not_repeat_promise"]
        and gap_checks["does_not_repeat_g1"],
        {"ask_one": BASE.BASE.BASE.node_executed(raw, "uapp_ask_one"), "answer": answer[:500]},
    )
    result["checks"] = checks
    result["verdict"] = "PASS" if checks and all(item["result"] == "PASS" for item in checks) else "FAIL"
    return result


def verify_turn(key: str) -> dict[str, Any]:
    scenarios = BASE.BASE.load_json(SCENARIOS)
    gate = BASE.BASE.load_json(GATE)
    turns = [turn for turn in scenarios["turns"] if turn["key"] == key]
    if len(turns) != 1 or not os.path.exists(raw_path(key)):
        return {"turn_key": key, "verdict": "NOT_VERIFIED", "reason": "Frozen turn or RAW absent"}
    raw = BASE.BASE.load_json(raw_path(key))
    if raw.get("gate_sha256") != BASE.BASE.sha256_file(GATE):
        return {"turn_key": key, "verdict": "NOT_VERIFIED", "freshness": "STALE", "reason": "Gate mismatch"}
    return evaluate_turn(raw, turns[0], gate)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--turn", required=True)
    args = parser.parse_args()
    result = verify_turn(args.turn)
    BASE.BASE.exclusive_write(check_path(args.turn), result)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0 if result.get("verdict") == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
