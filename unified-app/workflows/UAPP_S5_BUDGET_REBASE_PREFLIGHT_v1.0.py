#!/usr/bin/env python3
"""Zero-model preflight for every remaining Gate v1.5 formal turn."""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
from types import ModuleType
from typing import Any

import yaml

HERE = Path(__file__).resolve().parent
UAPP_ROOT = HERE.parent
GATE_OLD = UAPP_ROOT / "stages" / "UAPP_S5_GATE_v1.4.json"
GATE = UAPP_ROOT / "stages" / "UAPP_S5_GATE_v1.5.json"
SCENARIOS = UAPP_ROOT / "stages" / "UAPP_S5_FROZEN_SCENARIOS_v1.1.json"
MANIFEST = UAPP_ROOT / "stages" / "UAPP_S5_CANDIDATE_RUN_MANIFEST_v1.5.yaml"
EXECUTOR = UAPP_ROOT / "workflows" / "UAPP_S5_EXEC_v1.6.py"
EVIDENCE = UAPP_ROOT / "evidence" / "stages" / "uapp_s5_v1_4"
OUTPUT = EVIDENCE / "controls" / "UAPP_S5_BUDGET_REBASE_PREFLIGHT_v1.0.json"
PRIOR = [f"UAPP-CAP-0{number}" for number in range(1, 5)]


def load_module(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(path)
    return value


def safe_key(key: str) -> str:
    return key.replace(":", "_").replace("/", "_")


def strip_allowed_gate_delta(value: dict[str, Any]) -> dict[str, Any]:
    result = copy.deepcopy(value)
    document = result["document"]
    for key in ("id", "authority_event", "parent_gate", "parent_gate_sha256"):
        document.pop(key)
    result["contract"].pop("manifest_sha256")
    result["frozen_files"].pop("executor_sha256")
    budget = result["budget"]
    for key in (
        "used_top_level_runs",
        "used_llm_node_attempts",
        "new_top_level_runs_total_max",
        "new_llm_node_attempts_total_max",
    ):
        budget.pop(key)
    return result


def main() -> int:
    if OUTPUT.exists():
        raise RuntimeError(f"Refusing to overwrite {OUTPUT}")
    executor = load_module("uapp_s5_exec_v16_preflight", EXECUTOR)
    gate_old = load_json(GATE_OLD)
    gate = load_json(GATE)
    scenarios = load_json(SCENARIOS)
    manifest = yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))
    if not isinstance(manifest, dict):
        raise RuntimeError(MANIFEST)

    order = scenarios["formal_order"]
    remaining = order[4:]
    turns_by_key = {turn["key"]: turn for turn in scenarios["turns"]}
    apps = executor.RUNNER.STATE.protected_apps()
    active_runs = int(executor.RUNNER.BASE.psql(
        "select count(*) from workflow_runs where status='running';"
    ))
    global_m2 = executor.RUNNER.global_m2_guard()
    api_key = executor.RUNNER.DC.Console(
        env=executor.RUNNER.DC.load_env(executor.RUNNER.ENV_FILE)
    ).app_api_key(executor.RUNNER.UAPP_APP_ID, create_if_missing=False)

    prior_evidence: dict[str, Any] = {}
    for key in PRIOR:
        raw = Path(executor.raw_path(key))
        check = Path(executor.check_path(key))
        check_value = load_json(check) if check.exists() else {}
        prior_evidence[key] = {
            "raw_exists": raw.exists(),
            "raw_sha256": sha256(raw) if raw.exists() else "",
            "check_exists": check.exists(),
            "check_sha256": sha256(check) if check.exists() else "",
            "verdict": check_value.get("verdict"),
        }

    per_turn: list[dict[str, Any]] = []
    for key in remaining:
        turn = turns_by_key[key]
        group = turn["conversation_group"]
        prior_same_group = [
            previous for previous in order[:order.index(key)]
            if turns_by_key[previous]["conversation_group"] == group
        ]
        raw = Path(executor.raw_path(key))
        check = Path(executor.check_path(key))
        checks = {
            "turn_identity_unique": sum(item["key"] == key for item in scenarios["turns"]) == 1,
            "natural_language_nonempty": bool(str(turn.get("query") or "").strip()),
            "raw_path_absent": not raw.exists(),
            "check_path_absent": not check.exists(),
            "conversation_predecessors_identified": all(previous in order for previous in prior_same_group),
            "runtime_predecessor_gate_deferred_until_ordered_execution": True,
        }
        per_turn.append({
            "turn_key": key,
            "conversation_group": group,
            "prior_same_group": prior_same_group,
            "checks": checks,
            "verdict": "PASS" if all(checks.values()) else "FAIL",
        })

    hashes = {
        "gate_v1_4": sha256(GATE_OLD),
        "gate_v1_5": sha256(GATE),
        "scenarios_v1_1": sha256(SCENARIOS),
        "manifest_v1_5": sha256(MANIFEST),
        "executor_v1_6": sha256(EXECUTOR),
        "runner_v1_0": sha256(HERE / "UAPP_S5_RUN_v1.0.py"),
        "checker_v1_2": sha256(HERE / "UAPP_S5_VERIFY_v1.2.py"),
    }
    common_checks = {
        "parent_gate_bound": hashes["gate_v1_4"] == gate["document"]["parent_gate_sha256"],
        "manifest_bound": hashes["manifest_v1_5"] == gate["contract"]["manifest_sha256"],
        "scenario_bound": hashes["scenarios_v1_1"] == gate["frozen_files"]["scenarios_sha256"],
        "executor_bound": hashes["executor_v1_6"] == gate["frozen_files"]["executor_sha256"],
        "runner_bound": hashes["runner_v1_0"] == gate["frozen_files"]["runner_sha256"],
        "checker_bound": hashes["checker_v1_2"] == gate["frozen_files"]["checker_sha256"],
        "only_authorized_gate_delta": strip_allowed_gate_delta(gate_old) == strip_allowed_gate_delta(gate),
        "formal_order_unchanged": len(order) == 19 and order == gate_old.get("formal_order", order),
        "candidate_graphs_current": all(
            apps[name]["graph_md5"] == expected
            for name, expected in gate["candidate"]["graph_md5"].items()
        ),
        "no_active_runs": active_runs == 0,
        "api_key_present": bool(api_key),
        "m2_guard_current": global_m2 == gate["protected_surface"]["global_m2_before"],
        "prior_cap01_to_04_current": all(
            item["raw_exists"] and item["check_exists"] and item["verdict"] == "PASS"
            for item in prior_evidence.values()
        ),
        "prior_evidence_not_invalidated_by_budget_only_delta": (
            strip_allowed_gate_delta(gate_old) == strip_allowed_gate_delta(gate)
            and gate_old["candidate"] == gate["candidate"]
            and gate_old["criteria"] == gate["criteria"]
            and gate_old["frozen_files"]["scenarios_sha256"]
            == gate["frozen_files"]["scenarios_sha256"]
            and gate_old["frozen_files"]["checker_sha256"]
            == gate["frozen_files"]["checker_sha256"]
        ),
        "top_level_budget_sufficient": gate["budget"]["used_top_level_runs"] + len(remaining)
        <= gate["budget"]["new_top_level_runs_total_max"],
        "llm_static_budget_sufficient": gate["budget"]["used_llm_node_attempts"]
        + len(remaining) * gate["budget"]["per_turn_static_reachable_llm_nodes"]
        <= gate["budget"]["new_llm_node_attempts_total_max"],
        "manifest_budget_matches_gate": (
            manifest["budget"]["used_top_level_runs"] == gate["budget"]["used_top_level_runs"]
            and manifest["budget"]["used_llm_node_attempts"] == gate["budget"]["used_llm_node_attempts"]
            and manifest["budget"]["new_total_limits"]["top_level_runs"]
            == gate["budget"]["new_top_level_runs_total_max"]
            and manifest["budget"]["new_total_limits"]["llm_attempts"]
            == gate["budget"]["new_llm_node_attempts_total_max"]
        ),
    }
    verdict = "PASS" if all(common_checks.values()) and all(
        item["verdict"] == "PASS" for item in per_turn
    ) else "FAIL"
    result = {
        "document": {
            "id": "UAPP_S5_BUDGET_REBASE_PREFLIGHT_v1.0",
            "task_id": gate["document"]["task_id"],
            "model_calls": 0,
        },
        "hashes": hashes,
        "current": {
            "active_runs": active_runs,
            "apps": apps,
            "global_m2": global_m2,
            "api_key_present": bool(api_key),
        },
        "budget": {
            "used_top_level_runs": gate["budget"]["used_top_level_runs"],
            "used_llm_node_attempts": gate["budget"]["used_llm_node_attempts"],
            "remaining_turns": len(remaining),
            "minimum_final_top_level_runs": gate["budget"]["used_top_level_runs"] + len(remaining),
            "static_final_llm_attempt_cap": gate["budget"]["used_llm_node_attempts"]
            + len(remaining) * gate["budget"]["per_turn_static_reachable_llm_nodes"],
            "limits": {
                "top_level_runs": gate["budget"]["new_top_level_runs_total_max"],
                "llm_attempts": gate["budget"]["new_llm_node_attempts_total_max"],
            },
        },
        "prior_cap01_to_04": prior_evidence,
        "remaining_turn_preflights": per_turn,
        "common_checks": common_checks,
        "common_pass_count": sum(common_checks.values()),
        "common_check_count": len(common_checks),
        "turn_pass_count": sum(item["verdict"] == "PASS" for item in per_turn),
        "turn_check_count": len(per_turn),
        "verdict": verdict,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("x", encoding="utf-8") as handle:
        json.dump(result, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    print(json.dumps({
        "verdict": verdict,
        "common": f"{result['common_pass_count']}/{result['common_check_count']}",
        "turns": f"{result['turn_pass_count']}/{result['turn_check_count']}",
        "output": str(OUTPUT),
    }, ensure_ascii=False))
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
