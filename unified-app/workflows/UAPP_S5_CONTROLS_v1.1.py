#!/usr/bin/env python3
"""Zero-model controls for the frozen S5 v1.1 checker."""

from __future__ import annotations

import copy
import importlib.util
import json
import os
from types import ModuleType
from typing import Any

HERE = os.path.dirname(os.path.abspath(__file__))
UAPP_ROOT = os.path.abspath(os.path.join(HERE, ".."))
SCENARIOS = os.path.join(UAPP_ROOT, "stages", "UAPP_S5_FROZEN_SCENARIOS_v1.1.json")
GATE = os.path.join(UAPP_ROOT, "stages", "UAPP_S5_GATE_v1.1.json")
OUTPUT = os.path.join(UAPP_ROOT, "evidence", "stages", "uapp_s5_v1_1", "preflight", "UAPP_S5_CONTROLS_v1.1.json")


def load_module(name: str, path: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


OLD = load_module("uapp_s5_controls_v10_for_v11", os.path.join(HERE, "UAPP_S5_CONTROLS_v1.0.py"))
VERIFY = load_module("uapp_s5_verify_v11_controls", os.path.join(HERE, "UAPP_S5_VERIFY_v1.1.py"))


def loaded(path: str) -> dict[str, Any]:
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def ideal_raw(turn: dict[str, Any], gate: dict[str, Any]) -> dict[str, Any]:
    raw = OLD.ideal_raw(turn, gate)
    if turn.get("expected_capability"):
        raw["m2_after"]["artifacts"] = [{"id": "artifact-1"}]
        raw["m2_after"]["content_versions"] = [{"id": "version-1"}]
    return raw


def mutate(raw: dict[str, Any], check_id: str) -> None:
    if check_id == "CAP-04":
        raw["m2_after"]["artifacts"] = []
        return
    OLD.VERIFY = VERIFY
    OLD.mutate(raw, check_id)


def main() -> int:
    scenarios, gate = loaded(SCENARIOS), loaded(GATE)
    predecessors = {"UAPP-GAP-01:G1": {"conversation_id": "conversation-GAP01V11"}, "UAPP-FULL-01:T4": {"conversation_id": "conversation-FULL01V11"}}
    controls: list[dict[str, Any]] = []
    for turn in scenarios["turns"]:
        raw = ideal_raw(turn, gate)
        positive = VERIFY.evaluate_turn(raw, turn, gate, predecessors)
        controls.append({"turn_key": turn["key"], "control": "positive", "verdict": positive["verdict"]})
        if positive["verdict"] != "PASS":
            raise RuntimeError(f"positive failed: {turn['key']} {positive}")
        for predicate in positive["checks"]:
            negative_raw = copy.deepcopy(raw)
            mutate(negative_raw, predicate["id"])
            negative = VERIFY.evaluate_turn(negative_raw, turn, gate, predecessors)
            matching = [item for item in negative["checks"] if item["id"] == predicate["id"]]
            flipped = bool(matching) and all(item["result"] == "FAIL" for item in matching)
            controls.append({"turn_key": turn["key"], "control": f"negative:{predicate['id']}", "single_variable": True, "target_flipped_to_fail": flipped})
            if not flipped:
                raise RuntimeError(f"negative failed: {turn['key']} {predicate['id']}")
    report = {"document": {"id": "UAPP_S5_CONTROLS_v1.1", "task_id": gate["document"]["task_id"]}, "model_calls": 0, "positive_controls": sum(item["control"] == "positive" for item in controls), "single_variable_negative_controls": sum(item["control"].startswith("negative:") for item in controls), "all_pass": True, "controls": controls}
    os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
    with open(OUTPUT, "x", encoding="utf-8") as handle:
        json.dump(report, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
