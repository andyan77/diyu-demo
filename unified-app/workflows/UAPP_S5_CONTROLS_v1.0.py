#!/usr/bin/env python3
"""Zero-model positive and single-variable negative controls for the S5 checker."""

from __future__ import annotations

import copy
import importlib.util
import json
import os
from types import ModuleType
from typing import Any

HERE = os.path.dirname(os.path.abspath(__file__))
UAPP_ROOT = os.path.abspath(os.path.join(HERE, ".."))
SCENARIOS = os.path.join(UAPP_ROOT, "stages", "UAPP_S5_FROZEN_SCENARIOS_v1.0.json")
GATE = os.path.join(UAPP_ROOT, "stages", "UAPP_S5_GATE_v1.0.json")
OUTPUT = os.path.join(UAPP_ROOT, "evidence", "stages", "uapp_s5", "preflight", "UAPP_S5_CONTROLS_v1.0.json")


def load_module(name: str, path: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


VERIFY = load_module("uapp_s5_verify_controls", os.path.join(HERE, "UAPP_S5_VERIFY_v1.0.py"))


def loaded(path: str) -> dict[str, Any]:
    with open(path, encoding="utf-8") as handle:
        value = json.load(handle)
    return value


def execution(node_id: str, outputs: dict[str, Any] | None = None, node_type: str = "code") -> dict[str, Any]:
    return {"node_id": node_id, "type": node_type, "status": "succeeded", "error": None, "outputs": json.dumps(outputs or {}, ensure_ascii=False)}


def app_run(app: str, nodes: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    return {"id": f"run-{app}", "status": "succeeded", "node_detail": nodes or [execution(f"{app.lower()}-llm", node_type="llm")]}


def ideal_raw(turn: dict[str, Any], gate: dict[str, Any]) -> dict[str, Any]:
    key = turn["key"]
    route = turn.get("expected_capability") or ("CONTENT_BRIEF" if turn.get("equivalence", "").startswith("positive") else "")
    top_nodes = [execution("static-llm", node_type="llm"), execution("uapp_route", {"target_capability": route})]
    runs: dict[str, list[dict[str, Any]]] = {name: [] for name in ["UAPP", "M3", "HOP", "SEAM", *VERIFY.CAPABILITIES]}
    answer = "已根据你提供的信息继续处理。"
    if turn.get("expected_capability"):
        top_nodes.append(execution("uapp_seam"))
        runs[str(turn["expected_capability"])] = [app_run(str(turn["expected_capability"]))]
    elif key == "UAPP-GAP-01:G1":
        top_nodes.append(execution("uapp_ask_one"))
        answer = "还需要你确认这周主推什么商品或方向；其他已经说清楚的内容会保留。"
    elif key == "UAPP-GAP-01:G2":
        top_nodes.append(execution("uapp_seam"))
        runs["CONTENT_BRIEF"] = [app_run("CONTENT_BRIEF")]
    elif turn.get("equivalence", "").startswith("positive"):
        top_nodes.append(execution("uapp_seam"))
        runs["CONTENT_BRIEF"] = [app_run("CONTENT_BRIEF")]
    elif turn.get("equivalence", "").startswith("negative"):
        top_nodes.append(execution("uapp_ask_one"))
        answer = "还缺少希望受众看完明白什么、能做什么。"
    runs["UAPP"] = [{"id": "top-run", "status": "succeeded", "node_detail": top_nodes}]
    m2 = {name: [] for name in ("workspace", "cycles", "tasks", "materials", "artifacts", "content_versions", "publish_instances", "feedback_records", "task_snapshots", "task_run_states")}
    if key == "UAPP-WITHDRAW-01:W0":
        m2["materials"] = [{"id": "material-1", "withdrawn_at": None}]
    elif key == "UAPP-WITHDRAW-01:W1":
        m2["materials"] = [{"id": "material-1", "withdrawn_at": "2026-08-30T00:00:00Z"}]
    elif key == "UAPP-FULL-01:T1" or turn.get("equivalence", "").startswith("positive"):
        m2["artifacts"] = [{"id": "artifact-1"}]
        m2["content_versions"] = [{"id": "version-1"}]
        if key == "UAPP-FULL-01:T1":
            runs["CONTENT_BRIEF"] = [app_run("CONTENT_BRIEF")]
    elif key == "UAPP-FULL-01:T2":
        m2["publish_instances"] = [{"id": "publish-1", "is_test": True, "is_simulated": True}]
        answer = "已登记为模拟测试记录，没有操作真实平台。"
    elif key == "UAPP-FULL-01:T3":
        m2["feedback_records"] = [{"id": "feedback-1", "is_test": True, "is_simulated": True}]
    elif key == "UAPP-FULL-01:T4":
        m2["cycles"] = [{"id": "cycle-1"}, {"id": "cycle-2"}]
    elif key == "UAPP-RECOVERY-01:R1":
        m2["feedback_records"] = [{"id": "feedback-1", "is_test": True, "is_simulated": True}]
    apps = {name: {"graph_md5": value} for name, value in gate["candidate"]["graph_md5"].items()}
    raw = {
        "turn_key": key,
        "request": {"query": turn["query"], "inputs": {}},
        "request_attempts_by_runner": 1,
        "http_status": 200,
        "transport_error": "",
        "workflow_run_id": "top-run",
        "answer": answer,
        "conversation_id": f"conversation-{turn['conversation_group']}",
        "app_runs_in_window": runs,
        "m2_after": m2,
        "global_m2_after": copy.deepcopy(gate["protected_surface"]["global_m2_before"]),
        "protected_apps_after": apps,
    }
    if key == "UAPP-WITHDRAW-01:W0":
        raw["upload"] = {"http_status": 201}
    return raw


def mutate(raw: dict[str, Any], check_id: str) -> None:
    top = raw["app_runs_in_window"]["UAPP"][0]
    if check_id == "T-01":
        raw["request"]["query"] += " altered"
    elif check_id == "T-02":
        raw["request"]["inputs"] = {"forbidden": True}
    elif check_id == "T-03":
        raw["http_status"] = 500
    elif check_id == "T-04":
        top["node_detail"].append({"node_id": "failed", "type": "code", "status": "failed", "error": "fixture", "outputs": "{}"})
    elif check_id == "T-05":
        raw["answer"] += " uapp_internal"
    elif check_id == "T-06":
        raw["global_m2_after"]["non_test_publish_instances"] += 1
    elif check_id == "T-07":
        raw["protected_apps_after"]["UAPP"]["graph_md5"] = "drift"
    elif check_id == "T-08":
        for app_rows in raw["app_runs_in_window"].values():
            for run in app_rows:
                for node in run["node_detail"]:
                    if node.get("type") == "llm":
                        node["type"] = "code"
    elif check_id in ("CAP-01", "EQUIV-P1"):
        for node in top["node_detail"]:
            if node["node_id"] == "uapp_route":
                node["outputs"] = json.dumps({"target_capability": "WRONG"})
    elif check_id in ("CAP-02", "GAP-01", "EQUIV-N1"):
        top["node_detail"] = [node for node in top["node_detail"] if node["node_id"] != "uapp_seam"]
        if check_id == "GAP-01" or check_id == "EQUIV-N1":
            top["node_detail"].append(execution("uapp_seam"))
    elif check_id in ("CAP-03", "GAP-02"):
        allowed = next(
            (name for name in VERIFY.CAPABILITIES if raw["app_runs_in_window"][name]),
            "",
        )
        dark_run = next(name for name in VERIFY.CAPABILITIES if name != allowed)
        raw["app_runs_in_window"][dark_run] = [app_run(dark_run)]
    elif check_id == "GAP-03" or check_id == "RECOVERY-01":
        raw["conversation_id"] = "wrong-conversation"
    elif check_id == "EQUIV-P2" or check_id == "FULL-01":
        raw["m2_after"]["artifacts"] = []
    elif check_id == "EQUIV-N2":
        raw["answer"] = "请再补充。"
    elif check_id in ("WITHDRAW-01", "WITHDRAW-02"):
        raw["m2_after"]["materials"] = []
    elif check_id == "WITHDRAW-03":
        raw["m2_after"]["publish_instances"] = [{"id": "publish-1", "is_test": False, "is_simulated": False}]
    elif check_id == "FULL-02":
        raw["m2_after"]["publish_instances"][0]["is_test"] = False
    elif check_id == "FULL-02B":
        raw["answer"] = "已经登记。"
    elif check_id == "FULL-03":
        raw["m2_after"]["feedback_records"] = []
    elif check_id == "FULL-04":
        raw["m2_after"]["cycles"] = raw["m2_after"]["cycles"][:1]
    else:
        raise RuntimeError(f"No single-variable negative control for {check_id}")


def main() -> int:
    scenarios = loaded(SCENARIOS)
    gate = loaded(GATE)
    predecessor_map = {
        "UAPP-GAP-01:G1": {"conversation_id": "conversation-GAP01"},
        "UAPP-FULL-01:T4": {"conversation_id": "conversation-FULL01"},
    }
    controls: list[dict[str, Any]] = []
    for turn in scenarios["turns"]:
        raw = ideal_raw(turn, gate)
        positive = VERIFY.evaluate_turn(raw, turn, gate, predecessor_map)
        controls.append({"turn_key": turn["key"], "control": "positive", "verdict": positive["verdict"]})
        if positive["verdict"] != "PASS":
            raise RuntimeError(f"Positive control failed for {turn['key']}: {positive}")
        for predicate in positive["checks"]:
            negative_raw = copy.deepcopy(raw)
            mutate(negative_raw, predicate["id"])
            negative = VERIFY.evaluate_turn(negative_raw, turn, gate, predecessor_map)
            matching = [item for item in negative["checks"] if item["id"] == predicate["id"]]
            flipped = bool(matching) and all(item["result"] == "FAIL" for item in matching)
            controls.append({"turn_key": turn["key"], "control": f"negative:{predicate['id']}", "single_variable": True, "target_flipped_to_fail": flipped})
            if not flipped:
                raise RuntimeError(f"Negative control did not discriminate {turn['key']} {predicate['id']}: {negative}")
    report = {
        "document": {"id": "UAPP_S5_CONTROLS_v1.0", "task_id": gate["document"]["task_id"]},
        "model_calls": 0,
        "positive_controls": sum(1 for item in controls if item["control"] == "positive"),
        "single_variable_negative_controls": sum(1 for item in controls if item["control"].startswith("negative:")),
        "all_pass": True,
        "controls": controls,
    }
    os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
    with open(OUTPUT, "x", encoding="utf-8") as handle:
        json.dump(report, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
