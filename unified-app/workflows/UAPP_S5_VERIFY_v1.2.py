#!/usr/bin/env python3
"""Current S5 checker: bind current RAW and verify actual UAPP artifact storage."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import re
from types import ModuleType
from typing import Any

HERE = os.path.dirname(os.path.abspath(__file__))
UAPP_ROOT = os.path.abspath(os.path.join(HERE, ".."))
SCENARIOS = os.path.join(UAPP_ROOT, "stages", "UAPP_S5_FROZEN_SCENARIOS_v1.1.json")
GATE = os.path.join(UAPP_ROOT, "stages", "UAPP_S5_GATE_v1.4.json")
EVIDENCE = os.path.join(UAPP_ROOT, "evidence", "stages", "uapp_s5_v1_4")
RESULT = os.path.join(UAPP_ROOT, "stages", "UAPP_S5_RESULT_v1.2.json")
MATRIX = os.path.join(UAPP_ROOT, "stages", "UAPP_S5_AC_MATRIX_v1.2.json")


def load_module(name: str, path: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


BASE = load_module("uapp_s5_verify_v10_for_v12", os.path.join(HERE, "UAPP_S5_VERIFY_v1.0.py"))
BASE.SCENARIOS = SCENARIOS
BASE.GATE = GATE
BASE.EVIDENCE = EVIDENCE
BASE.RESULT = RESULT
BASE.MATRIX = MATRIX


def safe_key(key: str) -> str:
    return BASE.safe_key(key)


def raw_path(key: str) -> str:
    return os.path.join(EVIDENCE, "raw", f"{safe_key(key)}.json")


def check_path(key: str) -> str:
    return os.path.join(EVIDENCE, "checks", f"{safe_key(key)}.json")


BASE.raw_path = raw_path
BASE.check_path = check_path


def parsed(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    if not isinstance(value, str) or not value.strip():
        return {}
    try:
        result = json.loads(value)
    except json.JSONDecodeError:
        return {}
    return result if isinstance(result, dict) else {}


def norm(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def fnv(value: str) -> str:
    number = 0xCBF29CE484222325
    for byte in value.encode("utf-8"):
        number = ((number ^ byte) * 0x100000001B3) & 0xFFFFFFFFFFFFFFFF
    return f"{number:016x}"


def artifact_observation(raw: dict[str, Any], expected: str) -> dict[str, Any]:
    seam = BASE.node_output(raw, "uapp_seam")
    body = str(seam.get("artifact") or "")
    variables = raw.get("conversation_variables_after") or {}
    store = parsed(variables.get("uapp_last_artifact"))
    items = store.get("items") if isinstance(store.get("items"), list) else []
    exact = [item for item in items if isinstance(item, dict)
             and item.get("cap") == expected and item.get("body") == body]
    record = exact[-1] if exact else {}
    state = parsed(variables.get("uapp_task_fields"))
    ledger = state.get("artifacts") if isinstance(state.get("artifacts"), list) else []
    ledger_matches = [item for item in ledger if isinstance(item, dict)
                      and item.get("cap") == expected and item.get("fp") == record.get("fp")]
    normalized = norm(body)
    checks = {
        "seam_artifact_nonempty": bool(body.strip()),
        "seam_artifact_nonplaceholder": len(normalized) >= 100
        and len(re.sub(r"[^0-9A-Za-z\u4e00-\u9fff]", "", normalized)) >= 50,
        "store_exact_body_and_capability": len(exact) == 1,
        "store_length_identity": bool(record)
        and record.get("len") == len(body)
        and record.get("nlen") == len(normalized),
        "store_fingerprint_identity": bool(record)
        and record.get("fp") == fnv(normalized[:256])
        and record.get("bfp") == fnv(normalized),
        "task_ledger_identity": len(ledger_matches) == 1,
        "last_capability_identity": variables.get("uapp_last_capability") == expected,
    }
    return {
        "checks": checks,
        "artifact_len": len(body),
        "artifact_sha256": hashlib.sha256(body.encode("utf-8")).hexdigest() if body else "",
        "record_fp": record.get("fp"),
        "record_bfp": record.get("bfp"),
    }


_base_evaluate = BASE.evaluate_turn


def evaluate_turn(
    raw: dict[str, Any],
    turn: dict[str, Any],
    gate: dict[str, Any],
    predecessors: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    result = _base_evaluate(raw, turn, gate, predecessors)
    expected = turn.get("expected_capability")
    observation = artifact_observation(raw, expected) if expected else None
    if expected and observation is not None:
        result["checks"].append({
            "id": "CAP-04",
            "result": "PASS" if all(observation["checks"].values()) else "FAIL",
            "detail": observation,
        })
    if turn.get("equivalence", "").startswith("positive"):
        observation = artifact_observation(raw, "CONTENT_BRIEF")
        for item in result["checks"]:
            if item["id"] == "EQUIV-P2":
                item["result"] = "PASS" if all(observation["checks"].values()) else "FAIL"
                item["detail"] = observation
    if turn.get("key") == "UAPP-FULL-01:T1":
        route = BASE.node_output(raw, "uapp_route")
        observation = artifact_observation(raw, str(route.get("target_capability") or ""))
        for item in result["checks"]:
            if item["id"] == "FULL-01":
                m2_context = bool(BASE.rows(raw, "tasks")) and bool(BASE.rows(raw, "cycles"))
                one_capability = sum(BASE.app_run_count(raw, name) for name in BASE.CAPABILITIES) == 1
                item["result"] = "PASS" if (
                    m2_context and one_capability and all(observation["checks"].values())
                ) else "FAIL"
                item["detail"] = {
                    "m2_task_and_cycle": m2_context,
                    "one_capability": one_capability,
                    "artifact": observation,
                }
    result["verdict"] = "PASS" if result["checks"] and all(
        item["result"] == "PASS" for item in result["checks"]
    ) else "FAIL"
    return result


BASE.evaluate_turn = evaluate_turn
load_json = BASE.load_json
sha256_file = BASE.sha256_file
verify_turn = BASE.verify_turn
verify_final = BASE.verify_final
exclusive_write = BASE.exclusive_write
rows = BASE.rows
node_executed = BASE.node_executed
app_run_count = BASE.app_run_count
llm_attempts = BASE.llm_attempts


if __name__ == "__main__":
    raise SystemExit(BASE.main())

