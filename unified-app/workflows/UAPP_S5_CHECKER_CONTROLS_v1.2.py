#!/usr/bin/env python3
"""Zero-model positive and single-variable negative controls for Checker v1.2."""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import os
from types import ModuleType

HERE = os.path.dirname(os.path.abspath(__file__))
UAPP_ROOT = os.path.abspath(os.path.join(HERE, ".."))
SOURCE_RAW = os.path.join(
    UAPP_ROOT, "evidence", "stages", "uapp_s5_v1_3", "raw", "UAPP-CAP-01.json"
)
OUTPUT = os.path.join(
    UAPP_ROOT, "evidence", "stages", "uapp_s5_v1_4", "controls",
    "UAPP_S5_CHECKER_CONTROLS_v1.2.json",
)


def load_module(name: str, path: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


CHECKER = load_module("uapp_s5_verify_v12_controls", os.path.join(HERE, "UAPP_S5_VERIFY_v1.2.py"))


def find_node(raw: dict, node_id: str) -> dict:
    run_id = raw["workflow_run_id"]
    run = next(item for item in raw["app_runs_in_window"]["UAPP"] if item["id"] == run_id)
    return next(item for item in run["node_detail"] if item["node_id"] == node_id)


def main() -> int:
    raw = CHECKER.load_json(SOURCE_RAW)
    expected = "MATRIX"
    positive = CHECKER.artifact_observation(raw, expected)
    cases: dict[str, dict] = {}

    no_seam_body = copy.deepcopy(raw)
    seam = find_node(no_seam_body, "uapp_seam")
    outputs = json.loads(seam["outputs"])
    outputs["artifact"] = ""
    seam["outputs"] = json.dumps(outputs, ensure_ascii=False)
    cases["negative_empty_seam_body"] = CHECKER.artifact_observation(no_seam_body, expected)

    placeholder = copy.deepcopy(raw)
    seam = find_node(placeholder, "uapp_seam")
    outputs = json.loads(seam["outputs"])
    outputs["artifact"] = "待补充"
    seam["outputs"] = json.dumps(outputs, ensure_ascii=False)
    cases["negative_placeholder"] = CHECKER.artifact_observation(placeholder, expected)

    wrong_store_body = copy.deepcopy(raw)
    store = json.loads(wrong_store_body["conversation_variables_after"]["uapp_last_artifact"])
    store["items"][-1]["body"] += "x"
    wrong_store_body["conversation_variables_after"]["uapp_last_artifact"] = json.dumps(store, ensure_ascii=False)
    cases["negative_store_body_mismatch"] = CHECKER.artifact_observation(wrong_store_body, expected)

    wrong_fp = copy.deepcopy(raw)
    store = json.loads(wrong_fp["conversation_variables_after"]["uapp_last_artifact"])
    store["items"][-1]["bfp"] = "0000000000000000"
    wrong_fp["conversation_variables_after"]["uapp_last_artifact"] = json.dumps(store, ensure_ascii=False)
    cases["negative_fingerprint_mismatch"] = CHECKER.artifact_observation(wrong_fp, expected)

    wrong_ledger = copy.deepcopy(raw)
    state = json.loads(wrong_ledger["conversation_variables_after"]["uapp_task_fields"])
    state["artifacts"][-1]["fp"] = "0000000000000000"
    wrong_ledger["conversation_variables_after"]["uapp_task_fields"] = json.dumps(state, ensure_ascii=False)
    cases["negative_ledger_mismatch"] = CHECKER.artifact_observation(wrong_ledger, expected)

    wrong_cap = copy.deepcopy(raw)
    wrong_cap["conversation_variables_after"]["uapp_last_capability"] = "CAMPAIGN"
    cases["negative_last_capability"] = CHECKER.artifact_observation(wrong_cap, expected)

    checks = {
        "positive_all_predicates": all(positive["checks"].values()),
        "negative_empty_discriminated": not cases["negative_empty_seam_body"]["checks"]["seam_artifact_nonempty"],
        "negative_placeholder_discriminated": not cases["negative_placeholder"]["checks"]["seam_artifact_nonplaceholder"],
        "negative_store_body_discriminated": not cases["negative_store_body_mismatch"]["checks"]["store_exact_body_and_capability"],
        "negative_fingerprint_discriminated": not cases["negative_fingerprint_mismatch"]["checks"]["store_fingerprint_identity"],
        "negative_ledger_discriminated": not cases["negative_ledger_mismatch"]["checks"]["task_ledger_identity"],
        "negative_last_capability_discriminated": not cases["negative_last_capability"]["checks"]["last_capability_identity"],
    }
    result = {
        "document": {
            "id": "UAPP_S5_CHECKER_CONTROLS_v1.2",
            "task_id": "DIYU-V1-UNIFIED-DIFY-APPLICATION-001",
            "model_calls": 0,
            "post_result_checker_rebase": "1/1",
        },
        "source_raw_sha256": hashlib.sha256(open(SOURCE_RAW, "rb").read()).hexdigest(),
        "positive": positive,
        "negative_cases": cases,
        "checks": checks,
        "pass_count": sum(checks.values()),
        "total": len(checks),
        "result": "PASS" if all(checks.values()) else "FAIL",
    }
    if result["result"] != "PASS":
        raise RuntimeError(json.dumps(result, ensure_ascii=False))
    os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
    if os.path.exists(OUTPUT):
        raise RuntimeError(f"Refusing to overwrite {OUTPUT}")
    with open(OUTPUT, "x", encoding="utf-8") as handle:
        json.dump(result, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    print(json.dumps({"result": result["result"], "checks": checks}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

