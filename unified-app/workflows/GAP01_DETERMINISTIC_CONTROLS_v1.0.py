#!/usr/bin/env python3
"""Pre/post deterministic controls for the GAP-01 UAPP seam."""

from __future__ import annotations

import importlib.util
import json
import logging
from pathlib import Path
from types import ModuleType
from typing import Any, Callable

LOGGER = logging.getLogger(__name__)
HERE = Path(__file__).resolve().parent
UAPP_ROOT = HERE.parent
RAW = UAPP_ROOT / "evidence" / "stages" / "uapp_s5_post_cap06_v1_0" / "raw" / "UAPP-GAP-01_G1.json"
SCENARIOS = UAPP_ROOT / "stages" / "UAPP_S5_FROZEN_SCENARIOS_v1.1.json"
OUTPUT = UAPP_ROOT / "evidence" / "stages" / "gap01_successor_v1_0" / "controls.json"


def load_module(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


BUILD = load_module("gap01_controls_build", HERE / "GAP01_SUCCESSOR_BUILD_v1.0.py")


def node_output(raw: dict[str, Any], node_id: str) -> dict[str, Any]:
    for run in raw["app_runs_in_window"]["UAPP"]:
        for node in run["node_detail"]:
            if node["node_id"] == node_id:
                value = json.loads(node.get("outputs") or "{}")
                return value if isinstance(value, dict) else {}
    return {}


def compile_route(code: str) -> Callable[..., dict[str, Any]]:
    namespace: dict[str, Any] = {}
    exec(compile(code, "<trusted-uapp-route>", "exec"), namespace)
    function = namespace.get("main")
    if not callable(function):
        raise RuntimeError("Route main function absent")
    return function


def call_route(
    function: Callable[..., dict[str, Any]],
    query: str,
    intent: str,
    task_text: str = "",
    picked: list[str] | None = None,
) -> dict[str, Any]:
    call_intent = {"needed_capabilities": picked or []}
    snapshot = {"current_task": {"text": task_text}}
    patch = {
        "action": "NONE",
        "intent": intent,
        "decisive_question_text": "",
        "intent_reason_text": "fixture",
    }
    return function(
        json.dumps(call_intent, ensure_ascii=False),
        json.dumps(snapshot, ensure_ascii=False),
        query,
        "",
        "control-conversation",
        patch,
        "",
    )


def one_question(value: str) -> bool:
    return value.count("？") + value.count("?") == 1


def main() -> int:
    if OUTPUT.exists():
        raise FileExistsError(OUTPUT)
    raw = json.loads(RAW.read_text(encoding="utf-8"))
    scenarios = json.loads(SCENARIOS.read_text(encoding="utf-8"))
    turns = {turn["key"]: turn for turn in scenarios["turns"]}
    g1 = turns["UAPP-GAP-01:G1"]["query"]
    g2 = turns["UAPP-GAP-01:G2"]["query"]
    observed_route = node_output(raw, "uapp_route")
    observed_action = node_output(raw, "uapp_action")

    graph = BUILD.published_graph()
    candidate, touched = BUILD.patch_uapp(graph)
    base_nodes = {node["id"]: node for node in graph["nodes"]}
    candidate_nodes = {node["id"]: node for node in candidate["nodes"]}
    base_route = compile_route(base_nodes["uapp_route"]["data"]["code"])
    next_route = compile_route(candidate_nodes["uapp_route"]["data"]["code"])

    base_g1 = call_route(base_route, g1, "CAMPAIGN", "这周想发点东西")
    next_g1 = call_route(next_route, g1, "CAMPAIGN", "这周想发点东西")
    equivalent = call_route(next_route, "本周想做些内容，交给你来定吧。", "CAMPAIGN")
    explicit_campaign = call_route(
        next_route,
        "请安排这周三条内容的排期、发布节奏和阶段计划。",
        "CAMPAIGN",
    )
    explicit_item = call_route(
        next_route,
        "这周围绕廓形西装做一条通勤穿搭内容，你看着办。",
        "CONTENT_BRIEF",
    )
    g2_route = call_route(next_route, g2, "CONTENT_BRIEF", "这周想发点东西")
    named_capability = call_route(
        next_route,
        "请给这周做排期。",
        "CAMPAIGN",
        picked=["CAMPAIGN"],
    )

    checks: list[dict[str, Any]] = []

    def add(check_id: str, passed: bool, detail: Any) -> None:
        checks.append({"id": check_id, "result": "PASS" if passed else "FAIL", "detail": detail})

    add("A-01-raw-query", raw["request"]["query"] == g1 and "这周" in g1, g1)
    add("A-02-raw-campaign", observed_route.get("target_capability") == "CAMPAIGN", observed_route)
    add("A-03-raw-no-question", not observed_action.get("decisive_question_text"), observed_action)
    add("A-04-raw-deadline", "时间或阶段边界" in raw.get("answer", ""), raw.get("answer"))
    add("A-05-g2-cannot-answer-deadline", "时间" not in g2 and "阶段" not in g2, g2)
    add("B-01-pre-control-discriminates", base_g1["route_mode"] == "CAPABILITY", base_g1)
    add("P1-route-question", next_g1["route_mode"] == "ASK_ONE", next_g1)
    add("P1-one-question", one_question(next_g1["decisive_question"]), next_g1["decisive_question"])
    add("P1-g2-answerable", any(token in next_g1["decisive_question"] for token in ("商品", "内容方向")), next_g1)
    add("P1-no-deadline", "截止" not in next_g1["decisive_question"] and "时间边界" not in next_g1["decisive_question"], next_g1)
    add("P1-no-capability", not next_g1["target_capability"] and next_g1["runs_business"] == "false", next_g1)
    add("P2-g2-semantic-answer", "主推" in g2 and "外套" in g2 and "希望" in g2, g2)
    add("P2-g2-continues", g2_route["route_mode"] == "CAPABILITY" and g2_route["target_capability"] == "CONTENT_BRIEF", g2_route)
    add("P2-g2-does-not-repeat", g2_route["asks_one"] == "false", g2_route)
    add("P3-explicit-campaign", explicit_campaign["route_mode"] == "CAPABILITY" and explicit_campaign["target_capability"] == "CAMPAIGN", explicit_campaign)
    add("P4-explicit-item", explicit_item["route_mode"] == "CAPABILITY" and explicit_item["target_capability"] == "CONTENT_BRIEF", explicit_item)
    add("N1-no-self-choice", next_g1["target_capability"] == "", next_g1)
    add("N2-no-default-campaign", equivalent["route_mode"] == "ASK_ONE", equivalent)
    add("N3-week-not-deadline", "时间" not in next_g1["decisive_question"], next_g1)
    add("N4-multi-question-detectable", not one_question("你想做整周安排吗？还是什么商品？"), "two questions")
    add("N5-unanswerable-detectable", not any(token in "你最晚什么时候发布？" for token in ("商品", "内容方向")), "deadline")
    add("N6-equivalent-expression", equivalent["route_mode"] == "ASK_ONE", equivalent)
    add("N7-named-capability-preserved", named_capability["target_capability"] == "CAMPAIGN", named_capability)
    for key in ("UAPP-CAP-01", "UAPP-CAP-02", "UAPP-CAP-03", "UAPP-CAP-04", "UAPP-CAP-05", "UAPP-CAP-06"):
        turn = turns[key]
        expected = str(turn["expected_capability"])
        before = call_route(base_route, str(turn["query"]), expected)
        after = call_route(next_route, str(turn["query"]), expected)
        add(f"N7-{key}-route-equivalence", before == after, {"before": before, "after": after})
    add("N7-only-two-nodes", touched == ["uapp_action", "uapp_route"], touched)

    report = {
        "document": {"id": "GAP01_DETERMINISTIC_CONTROLS_v1.0", "model_calls": 0},
        "checks": checks,
        "summary": {
            "passed": sum(item["result"] == "PASS" for item in checks),
            "total": len(checks),
            "verdict": "PASS" if all(item["result"] == "PASS" for item in checks) else "FAIL",
        },
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    LOGGER.info("%s", json.dumps(report["summary"], ensure_ascii=False, sort_keys=True))
    return 0 if report["summary"]["verdict"] == "PASS" else 1


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    raise SystemExit(main())
