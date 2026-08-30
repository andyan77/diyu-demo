#!/usr/bin/env python3
"""Adjudicate frozen S5 raw evidence; never starts a workflow."""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import os
from typing import Any

HERE = os.path.dirname(os.path.abspath(__file__))
UAPP_ROOT = os.path.abspath(os.path.join(HERE, ".."))
SCENARIOS = os.path.join(UAPP_ROOT, "stages", "UAPP_S5_FROZEN_SCENARIOS_v1.0.json")
GATE = os.path.join(UAPP_ROOT, "stages", "UAPP_S5_GATE_v1.0.json")
EVIDENCE = os.path.join(UAPP_ROOT, "evidence", "stages", "uapp_s5")
RESULT = os.path.join(UAPP_ROOT, "stages", "UAPP_S5_RESULT_v1.0.json")
MATRIX = os.path.join(UAPP_ROOT, "stages", "UAPP_S5_AC_MATRIX_v1.0.json")
CAPABILITIES = ["MATRIX", "CAMPAIGN", "CONTENT_BRIEF", "CREATIVE_SCRIPT", "PRODUCTION_DIRECTOR", "PUBLISHING_PACKAGING"]
FORBIDDEN_USER_TEXT = [
    "STALE", "PASS", "FAIL", "NOT_VERIFIED", "app_id", "workflow_id", "node_id",
    "uapp_", "ENTRY-", "target_capability", "PRODUCTION_DIRECTOR", "PUBLISHING_PACKAGING",
    "CONTENT_BRIEF", "CREATIVE_SCRIPT", "CAMPAIGN", "MATRIX",
]


def load_json(path: str) -> dict[str, Any]:
    with open(path, encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise RuntimeError(f"Expected object: {path}")
    return value


def sha256_file(path: str) -> str:
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


def safe_key(key: str) -> str:
    return key.replace(":", "_").replace("/", "_")


def raw_path(key: str) -> str:
    return os.path.join(EVIDENCE, "raw", f"{safe_key(key)}.json")


def check_path(key: str) -> str:
    return os.path.join(EVIDENCE, "checks", f"{safe_key(key)}.json")


def parsed(value: Any) -> Any:
    if isinstance(value, str):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return {}
    return value if value is not None else {}


def top_run(raw: dict[str, Any]) -> dict[str, Any]:
    rows = raw.get("app_runs_in_window", {}).get("UAPP", [])
    matches = [row for row in rows if row.get("id") == raw.get("workflow_run_id")]
    return matches[0] if len(matches) == 1 else {}


def node_output(raw: dict[str, Any], node_id: str) -> dict[str, Any]:
    run = top_run(raw)
    matches = [row for row in run.get("node_detail", []) if row.get("node_id") == node_id]
    if len(matches) != 1:
        return {}
    value = parsed(matches[0].get("outputs"))
    return value if isinstance(value, dict) else {}


def node_executed(raw: dict[str, Any], node_id: str) -> bool:
    return any(row.get("node_id") == node_id for row in top_run(raw).get("node_detail", []))


def app_run_count(raw: dict[str, Any], name: str) -> int:
    return len(raw.get("app_runs_in_window", {}).get(name, []))


def llm_attempts(raw: dict[str, Any]) -> int:
    total = 0
    for rows in raw.get("app_runs_in_window", {}).values():
        for run in rows:
            total += sum(1 for node in run.get("node_detail", []) if node.get("type") == "llm")
    return total


def rows(raw: dict[str, Any], table: str) -> list[dict[str, Any]]:
    value = raw.get("m2_after", {}).get(table, [])
    return value if isinstance(value, list) else []


def evaluate_turn(
    raw: dict[str, Any],
    turn: dict[str, Any],
    gate: dict[str, Any],
    predecessors: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []

    def check(identifier: str, condition: bool, detail: Any) -> None:
        checks.append({"id": identifier, "result": "PASS" if condition else "FAIL", "detail": detail})

    run = top_run(raw)
    answer = str(raw.get("answer") or "")
    leaks = [token for token in FORBIDDEN_USER_TEXT if token in answer]
    all_app_runs = raw.get("app_runs_in_window", {})
    failed_nodes = [
        {"app": app, "run": item.get("id"), "node": node.get("node_id"), "status": node.get("status"), "error": node.get("error")}
        for app, app_rows in all_app_runs.items()
        for item in app_rows
        for node in item.get("node_detail", [])
        if node.get("status") not in ("succeeded", None)
    ]
    expected_graphs = gate["candidate"]["graph_md5"]
    actual_graphs = {name: value.get("graph_md5") for name, value in raw.get("protected_apps_after", {}).items()}
    check("T-01", raw.get("turn_key") == turn["key"] and raw.get("request", {}).get("query") == turn["query"], {"turn_key": raw.get("turn_key")})
    check("T-02", raw.get("request", {}).get("inputs") == {} and raw.get("request_attempts_by_runner") == 1, {"inputs": raw.get("request", {}).get("inputs"), "attempts": raw.get("request_attempts_by_runner")})
    check("T-03", raw.get("http_status") == 200 and not raw.get("transport_error") and bool(run), {"http": raw.get("http_status"), "run_id": raw.get("workflow_run_id"), "transport_error": raw.get("transport_error")})
    check("T-04", not failed_nodes, failed_nodes)
    check("T-05", bool(answer) and not leaks, {"answer_length": len(answer), "forbidden_hits": leaks})
    check("T-06", raw.get("global_m2_after") == gate["protected_surface"]["global_m2_before"], raw.get("global_m2_after"))
    check("T-07", all(actual_graphs.get(name) == value for name, value in expected_graphs.items()), {"expected": expected_graphs, "actual": actual_graphs})
    check("T-08", 0 < llm_attempts(raw) <= gate["budget"]["per_turn_static_reachable_llm_nodes"], {"llm_attempts": llm_attempts(raw)})

    route = node_output(raw, "uapp_route")
    key = turn["key"]
    expected = turn.get("expected_capability")
    if expected:
        others = {name: app_run_count(raw, name) for name in CAPABILITIES if name != expected}
        check("CAP-01", route.get("target_capability") == expected, {"expected": expected, "actual": route.get("target_capability")})
        check("CAP-02", node_executed(raw, "uapp_seam") and app_run_count(raw, expected) == 1, {"seam": node_executed(raw, "uapp_seam"), "expected_runs": app_run_count(raw, expected)})
        check("CAP-03", all(value == 0 for value in others.values()), others)
    elif key == "UAPP-GAP-01:G1":
        check("GAP-01", node_executed(raw, "uapp_ask_one") and not node_executed(raw, "uapp_seam"), {"ask_one": node_executed(raw, "uapp_ask_one"), "seam": node_executed(raw, "uapp_seam")})
        check("GAP-02", all(app_run_count(raw, name) == 0 for name in CAPABILITIES) and any(word in answer for word in ("商品", "主推", "方向")), {"capability_runs": {name: app_run_count(raw, name) for name in CAPABILITIES}})
    elif key == "UAPP-GAP-01:G2":
        predecessor = (predecessors or {}).get("UAPP-GAP-01:G1")
        if predecessor is None:
            predecessor = load_json(raw_path("UAPP-GAP-01:G1")) if os.path.exists(raw_path("UAPP-GAP-01:G1")) else {}
        check("GAP-03", bool(predecessor) and raw.get("conversation_id") == predecessor.get("conversation_id") and node_executed(raw, "uapp_seam"), {"same_conversation": raw.get("conversation_id") == predecessor.get("conversation_id"), "seam": node_executed(raw, "uapp_seam")})
    elif turn.get("equivalence", "").startswith("positive"):
        check("EQUIV-P1", route.get("target_capability") == "CONTENT_BRIEF" and node_executed(raw, "uapp_seam") and app_run_count(raw, "CONTENT_BRIEF") == 1, {"route": route.get("target_capability"), "content_brief_runs": app_run_count(raw, "CONTENT_BRIEF")})
        check("EQUIV-P2", bool(rows(raw, "artifacts")) and bool(rows(raw, "content_versions")), {"artifacts": len(rows(raw, "artifacts")), "versions": len(rows(raw, "content_versions"))})
    elif turn.get("equivalence", "").startswith("negative"):
        check("EQUIV-N1", not node_executed(raw, "uapp_seam") and all(app_run_count(raw, name) == 0 for name in CAPABILITIES), {"seam": node_executed(raw, "uapp_seam"), "runs": {name: app_run_count(raw, name) for name in CAPABILITIES}})
        check("EQUIV-N2", any(word in answer for word in ("希望", "看完", "明白", "改变", "期望")), {"answer": answer})
    elif key == "UAPP-WITHDRAW-01:W0":
        materials = rows(raw, "materials")
        check("WITHDRAW-01", raw.get("upload", {}).get("http_status") in (200, 201) and len(materials) >= 1 and any(item.get("withdrawn_at") is None for item in materials), {"upload": raw.get("upload", {}).get("http_status"), "materials": materials})
    elif key == "UAPP-WITHDRAW-01:W1":
        materials = rows(raw, "materials")
        publishes = rows(raw, "publish_instances")
        check("WITHDRAW-02", bool(materials) and any(item.get("withdrawn_at") for item in materials), materials)
        check("WITHDRAW-03", all(item.get("is_test") is True and item.get("is_simulated") is True for item in publishes), publishes)
    elif key == "UAPP-FULL-01:T1":
        check("FULL-01", bool(rows(raw, "artifacts")) and bool(rows(raw, "content_versions")) and sum(app_run_count(raw, name) for name in CAPABILITIES) == 1, {"artifacts": len(rows(raw, "artifacts")), "versions": len(rows(raw, "content_versions")), "capability_runs": {name: app_run_count(raw, name) for name in CAPABILITIES}})
    elif key == "UAPP-FULL-01:T2":
        publishes = rows(raw, "publish_instances")
        check("FULL-02", len(publishes) == 1 and publishes[0].get("is_test") is True and publishes[0].get("is_simulated") is True, publishes)
        check("FULL-02B", any(word in answer for word in ("模拟", "测试", "没有", "未")), {"answer": answer})
    elif key == "UAPP-FULL-01:T3":
        feedback = rows(raw, "feedback_records")
        check("FULL-03", len(feedback) == 1 and feedback[0].get("is_test") is True and feedback[0].get("is_simulated") is True, feedback)
    elif key == "UAPP-FULL-01:T4":
        check("FULL-04", len(rows(raw, "cycles")) >= 2, {"cycles": len(rows(raw, "cycles"))})
    elif key == "UAPP-RECOVERY-01:R1":
        predecessor = (predecessors or {}).get("UAPP-FULL-01:T4")
        if predecessor is None:
            predecessor = load_json(raw_path("UAPP-FULL-01:T4")) if os.path.exists(raw_path("UAPP-FULL-01:T4")) else {}
        check("RECOVERY-01", bool(predecessor) and raw.get("conversation_id") == predecessor.get("conversation_id") and len(rows(raw, "feedback_records")) == 1, {"same_conversation": raw.get("conversation_id") == predecessor.get("conversation_id"), "feedback_rows": len(rows(raw, "feedback_records"))})

    verdict = "PASS" if checks and all(item["result"] == "PASS" for item in checks) else "FAIL"
    return {"turn_key": turn["key"], "verdict": verdict, "checks": checks, "llm_attempts": llm_attempts(raw), "workflow_run_id": raw.get("workflow_run_id")}


def verify_turn(key: str) -> dict[str, Any]:
    scenarios = load_json(SCENARIOS)
    gate = load_json(GATE)
    turns = [turn for turn in scenarios["turns"] if turn["key"] == key]
    if len(turns) != 1 or not os.path.exists(raw_path(key)):
        return {"turn_key": key, "verdict": "NOT_VERIFIED", "reason": "Frozen turn or raw evidence absent"}
    raw = load_json(raw_path(key))
    if raw.get("gate_sha256") != sha256_file(GATE) or raw.get("scenarios_sha256") != sha256_file(SCENARIOS):
        return {"turn_key": key, "verdict": "NOT_VERIFIED", "freshness": "STALE", "reason": "Evidence binding hash mismatch"}
    return evaluate_turn(raw, turns[0], gate)


def verify_final() -> tuple[dict[str, Any], dict[str, Any]]:
    scenarios = load_json(SCENARIOS)
    gate = load_json(GATE)
    turn_results = [verify_turn(key) for key in scenarios["formal_order"]]
    by_key = {item["turn_key"]: item for item in turn_results}

    def passed(*keys: str) -> bool:
        return all(by_key.get(key, {}).get("verdict") == "PASS" for key in keys)

    caps = tuple(f"UAPP-CAP-0{index}" for index in range(1, 7))
    equiv = ("UAPP-EQUIV-01a", "UAPP-EQUIV-01b", "UAPP-EQUIV-01c", "UAPP-EQUIV-01n")
    full = tuple(f"UAPP-FULL-01:T{index}" for index in range(1, 5))
    all_pass = all(item.get("verdict") == "PASS" for item in turn_results)
    run_ids = [item.get("workflow_run_id") for item in turn_results if item.get("workflow_run_id")]
    actual_llm = sum(int(item.get("llm_attempts") or 0) for item in turn_results)
    ac = {
        "UAPP-AC-01": all_pass,
        "UAPP-AC-02": all_pass,
        "UAPP-AC-03": passed(*full),
        "UAPP-AC-04": passed(*caps),
        "UAPP-AC-05": passed(*caps),
        "UAPP-AC-06": passed("UAPP-GAP-01:G1", "UAPP-GAP-01:G2"),
        "UAPP-AC-07": passed("UAPP-WITHDRAW-01:W0", "UAPP-WITHDRAW-01:W1"),
        "UAPP-AC-08": passed(*equiv),
        "UAPP-AC-09": passed(*full, "UAPP-RECOVERY-01:R1") and gate["inherited_current_evidence"]["cross_turn_correction_propagation"]["result"] == "PASS",
        "UAPP-AC-10": all_pass,
        "UAPP-AC-11": all_pass and len(run_ids) == gate["budget"]["formal_top_level_turn_count"],
    }
    matrix = {
        "document": {"id": "UAPP_S5_AC_MATRIX_v1.0", "task_id": gate["document"]["task_id"]},
        "gate_sha256": sha256_file(GATE),
        "criteria": {identifier: {"result": "PASS" if value else "FAIL", "freshness": "CURRENT"} for identifier, value in ac.items()},
    }
    result = {
        "document": {"id": "UAPP_S5_RESULT_v1.0", "task_id": gate["document"]["task_id"]},
        "gate_sha256": sha256_file(GATE),
        "scenarios_sha256": sha256_file(SCENARIOS),
        "turn_results": turn_results,
        "actual_top_level_runs": len(run_ids),
        "actual_llm_node_attempts": actual_llm,
        "manual_retries": 0,
        "repeat_sampling": 0,
        "ab_tests": 0,
        "reviewer_calls": 0,
        "workflow_run_ids": run_ids,
        "p0_failures": sum(1 for value in ac.values() if not value),
        "S5_TECHNICAL_ACCEPTANCE": "PASS" if all(ac.values()) else "FAIL",
        "freshness": "CURRENT",
        "UAPP_AC_12": "NOT_VERIFIED",
        "main_merge": "NOT_ALLOWED",
        "terminal_state": "unset",
    }
    return result, matrix


def exclusive_write(path: str, value: dict[str, Any]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "x", encoding="utf-8") as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--turn")
    parser.add_argument("--final", action="store_true")
    args = parser.parse_args()
    if bool(args.turn) == bool(args.final):
        raise SystemExit("Choose exactly one of --turn or --final")
    if args.turn:
        result = verify_turn(args.turn)
        exclusive_write(check_path(args.turn), result)
        logging.info("%s", json.dumps(result, ensure_ascii=False, sort_keys=True))
        return 0 if result.get("verdict") == "PASS" else 1
    result, matrix = verify_final()
    exclusive_write(RESULT, result)
    exclusive_write(MATRIX, matrix)
    logging.info("S5_TECHNICAL_ACCEPTANCE=%s runs=%s llm=%s", result["S5_TECHNICAL_ACCEPTANCE"], result["actual_top_level_runs"], result["actual_llm_node_attempts"])
    return 0 if result["S5_TECHNICAL_ACCEPTANCE"] == "PASS" else 1


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    raise SystemExit(main())
