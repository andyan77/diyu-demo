#!/usr/bin/env python3
"""Semantic GAP-01 checker plus the unchanged current S5 business checks."""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import re
from types import ModuleType
from typing import Any

HERE = os.path.dirname(os.path.abspath(__file__))
UAPP_ROOT = os.path.abspath(os.path.join(HERE, ".."))
SCENARIOS = os.path.join(UAPP_ROOT, "stages", "UAPP_S5_FROZEN_SCENARIOS_v1.1.json")
GATE = os.path.join(UAPP_ROOT, "stages", "GAP01_SUCCESSOR_GATE_v1.0.json")
EVIDENCE = os.path.join(UAPP_ROOT, "evidence", "stages", "gap01_successor_v1_0", "formal")
RESULT = os.path.join(UAPP_ROOT, "stages", "UAPP_S5_FINAL_TECHNICAL_RESULT_v1.0.json")
MATRIX = os.path.join(UAPP_ROOT, "stages", "UAPP_S5_AC_MATRIX_v1.7.json")
CAPABILITIES = [
    "MATRIX",
    "CAMPAIGN",
    "CONTENT_BRIEF",
    "CREATIVE_SCRIPT",
    "PRODUCTION_DIRECTOR",
    "PUBLISHING_PACKAGING",
]
INHERITED = {
    "UAPP-CAP-01": os.path.join(UAPP_ROOT, "evidence", "stages", "uapp_s5_v1_4", "checks", "UAPP-CAP-01.json"),
    "UAPP-CAP-02": os.path.join(UAPP_ROOT, "evidence", "stages", "uapp_s5_v1_4", "checks", "UAPP-CAP-02.json"),
    "UAPP-CAP-03": os.path.join(UAPP_ROOT, "evidence", "stages", "uapp_s5_v1_4", "checks", "UAPP-CAP-03.json"),
    "UAPP-CAP-04": os.path.join(UAPP_ROOT, "evidence", "stages", "uapp_s5_v1_4", "checks", "UAPP-CAP-04.json"),
    "UAPP-CAP-05": os.path.join(UAPP_ROOT, "evidence", "stages", "uapp_s5_inline_artifact_successor_v1_0", "formal", "checks", "UAPP-CAP-05.json"),
    "UAPP-CAP-06": os.path.join(UAPP_ROOT, "stages", "CAP06_FORMAL_RESULT_v1.1.json"),
}


def load_module(name: str, path: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


BASE = load_module("gap01_checker_base", os.path.join(HERE, "UAPP_S5_VERIFY_v1.2.py"))
BASE.SCENARIOS = SCENARIOS
BASE.GATE = GATE
BASE.EVIDENCE = EVIDENCE
BASE.RESULT = RESULT
BASE.MATRIX = MATRIX
BASE.BASE.SCENARIOS = SCENARIOS
BASE.BASE.GATE = GATE
BASE.BASE.EVIDENCE = EVIDENCE
BASE.BASE.RESULT = RESULT
BASE.BASE.MATRIX = MATRIX


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


def question_count(text: str) -> int:
    return text.count("？") + text.count("?")


def g1_semantics(answer: str, g2_query: str) -> dict[str, bool]:
    route_side = bool(re.search(r"(?:整周|一周|整体).{0,12}(?:排期|节奏|安排)|发布节奏", answer))
    content_side = bool(re.search(r"(?:商品|内容方向|具体内容|一条内容)", answer))
    alternative = "还是" in answer or "或者" in answer or "或是" in answer
    g2_has_content_answer = bool(re.search(r"(?:主推|商品|外套|内容方向|希望.{0,20}(?:知道|明白))", g2_query))
    return {
        "one_question": question_count(answer) == 1,
        "route_changing_fork": route_side and content_side and alternative,
        "answerable_by_frozen_g2": content_side and g2_has_content_answer,
        "does_not_prioritize_deadline": not bool(re.search(r"(?:截止|最晚|时间边界|到什么时候)", answer)),
        "natural_language": not any(token in answer for token in ("AMBIGUOUS", "target_capability", "uapp_", "CAMPAIGN")),
    }


def add_check(checks: list[dict[str, Any]], check_id: str, passed: bool, detail: Any) -> None:
    checks.append({"id": check_id, "result": "PASS" if passed else "FAIL", "detail": detail})


def evaluate_turn(
    raw: dict[str, Any],
    turn: dict[str, Any],
    gate: dict[str, Any],
    predecessors: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    result = BASE.evaluate_turn(raw, turn, gate, predecessors)
    key = str(turn["key"])
    if key not in ("UAPP-GAP-01:G1", "UAPP-GAP-01:G2"):
        return result
    checks = [item for item in result["checks"] if not str(item["id"]).startswith("GAP-")]
    answer = str(raw.get("answer") or "")
    route = BASE.BASE.node_output(raw, "uapp_route")
    capability_runs = {name: BASE.BASE.app_run_count(raw, name) for name in CAPABILITIES}
    scenarios = BASE.load_json(SCENARIOS)
    g2_query = next(item["query"] for item in scenarios["turns"] if item["key"] == "UAPP-GAP-01:G2")
    if key == "UAPP-GAP-01:G1":
        semantics = g1_semantics(answer, g2_query)
        variables = raw.get("conversation_variables_after") or {}
        add_check(checks, "GAP-S1", all(semantics.values()), semantics)
        add_check(
            checks,
            "GAP-S2",
            not route.get("target_capability") and all(value == 0 for value in capability_runs.values()),
            {"route": route, "capability_runs": capability_runs},
        )
        add_check(
            checks,
            "GAP-S3",
            not str(variables.get("uapp_last_artifact") or "").strip(),
            {"artifact_store_present": bool(str(variables.get("uapp_last_artifact") or "").strip())},
        )
    else:
        predecessor = (predecessors or {}).get("UAPP-GAP-01:G1")
        if predecessor is None and os.path.exists(raw_path("UAPP-GAP-01:G1")):
            predecessor = BASE.load_json(raw_path("UAPP-GAP-01:G1"))
        target = str(route.get("target_capability") or "")
        observation = BASE.artifact_observation(raw, target) if target in CAPABILITIES else {"checks": {}}
        one_capability = sum(capability_runs.values()) == 1 and capability_runs.get(target) == 1
        add_check(
            checks,
            "GAP-S4",
            bool(predecessor)
            and raw.get("conversation_id") == predecessor.get("conversation_id")
            and raw.get("end_user") == predecessor.get("end_user"),
            {"conversation_id": raw.get("conversation_id"), "predecessor": (predecessor or {}).get("conversation_id")},
        )
        add_check(
            checks,
            "GAP-S5",
            target == "CONTENT_BRIEF" and BASE.BASE.node_executed(raw, "uapp_seam") and one_capability,
            {"target": target, "seam": BASE.BASE.node_executed(raw, "uapp_seam"), "runs": capability_runs},
        )
        add_check(
            checks,
            "GAP-S6",
            bool(observation.get("checks")) and all(observation["checks"].values()),
            observation,
        )
        add_check(
            checks,
            "GAP-S7",
            not BASE.BASE.node_executed(raw, "uapp_ask_one")
            and "整体发布节奏" not in answer
            and "具体商品或内容方向" not in answer,
            {"ask_one": BASE.BASE.node_executed(raw, "uapp_ask_one"), "answer": answer[:500]},
        )
    result["checks"] = checks
    result["verdict"] = "PASS" if checks and all(item["result"] == "PASS" for item in checks) else "FAIL"
    return result


def verify_turn(key: str) -> dict[str, Any]:
    scenarios = BASE.load_json(SCENARIOS)
    gate = BASE.load_json(GATE)
    turns = [turn for turn in scenarios["turns"] if turn["key"] == key]
    if len(turns) != 1 or not os.path.exists(raw_path(key)):
        return {"turn_key": key, "verdict": "NOT_VERIFIED", "reason": "Frozen turn or RAW absent"}
    raw = BASE.load_json(raw_path(key))
    if raw.get("gate_sha256") != BASE.sha256_file(GATE) or raw.get("scenarios_sha256") != BASE.sha256_file(SCENARIOS):
        return {"turn_key": key, "verdict": "NOT_VERIFIED", "freshness": "STALE", "reason": "Binding mismatch"}
    return evaluate_turn(raw, turns[0], gate)


def inherited_pass(key: str) -> bool:
    value = BASE.load_json(INHERITED[key])
    return value.get("verdict") == "PASS" or value.get("verdict") == "PASS / CURRENT"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--turn", required=True)
    args = parser.parse_args()
    result = verify_turn(args.turn)
    BASE.exclusive_write(check_path(args.turn), result)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0 if result.get("verdict") == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

