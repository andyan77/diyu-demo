#!/usr/bin/env python3
"""Zero-model controls for the bounded GAP-01 G2 field successor."""

from __future__ import annotations

import importlib.util
import json
import logging
import re
from pathlib import Path
from types import ModuleType
from typing import Any, Callable

LOGGER = logging.getLogger(__name__)
HERE = Path(__file__).resolve().parent
UAPP_ROOT = HERE.parent
OUTPUT = UAPP_ROOT / "evidence" / "stages" / "gap01_successor_v1_1" / "controls.json"


def load_module(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


BUILD = load_module("gap01_v11_controls_build", HERE / "GAP01_SUCCESSOR_BUILD_v1.1.py")


def compile_fields(code: str) -> Callable[..., dict[str, Any]]:
    namespace: dict[str, Any] = {}
    exec(compile(code, "<trusted-uapp-fields>", "exec"), namespace)
    function = namespace.get("main")
    if not callable(function):
        raise RuntimeError("uapp_fields main absent")
    return function


def call_fields(
    function: Callable[..., dict[str, Any]],
    envelope: str,
    gaps: str,
    capability: str,
    query: str,
) -> dict[str, Any]:
    return function(
        "",
        "gap01-control-task",
        envelope,
        gaps,
        capability,
        query,
        "{}",
        "",
        "",
        "",
        "",
        "NOT_SELECTED",
        "NOT_APPLICABLE",
        "fixture",
        "",
        "",
        "",
        "",
        "{}",
    )


def field_value(envelope: str, key: str) -> str:
    match = re.search(r"^\s*`?%s`?\s*:\s*(.*)$" % re.escape(key), envelope, re.M)
    return match.group(1).strip() if match else ""


def env(expected: str, promise: str = "") -> str:
    lines = [
        "provenance:",
        "  target_capability: CONTENT_BRIEF",
        f"`expected_change`: {expected}",
    ]
    if promise:
        lines.append(f"`content_promise`: {promise}")
    return "\n".join(lines)


def main() -> int:
    if OUTPUT.exists():
        raise FileExistsError(OUTPUT)
    graph = BUILD.BASE.published_graph()
    candidate, touched = BUILD.patch_uapp(graph)
    base_code = next(node["data"]["code"] for node in graph["nodes"] if node["id"] == "uapp_fields")
    next_code = next(
        node["data"]["code"] for node in candidate["nodes"] if node["id"] == "uapp_fields"
    )
    base = compile_fields(base_code)
    successor = compile_fields(next_code)
    expected = "希望她看完知道缺的是一件能压住整套的外套"
    query = "说给通勤女性听；希望她看完知道缺的是一件能压住整套的外套。"
    before = call_fields(base, env(expected), "content_promise；expression_subject_and_boundary", "CONTENT_BRIEF", query)
    positive = call_fields(successor, env(expected), "content_promise；expression_subject_and_boundary", "CONTENT_BRIEF", query)
    unsupported = call_fields(
        successor,
        env("希望她看完知道一件外套能压住整套"),
        "content_promise",
        "CONTENT_BRIEF",
        "请继续。",
    )
    no_outcome = call_fields(
        successor,
        env("这是一件廓形西装外套"),
        "content_promise",
        "CONTENT_BRIEF",
        "这是一件廓形西装外套。",
    )
    other_capability = call_fields(
        successor,
        env(expected),
        "content_promise",
        "CREATIVE_SCRIPT",
        query,
    )
    explicit = call_fields(
        successor,
        env(expected, "只讲一件外套如何压住整套"),
        "expression_subject_and_boundary",
        "CONTENT_BRIEF",
        query + "只讲一件外套如何压住整套。",
    )
    checks: list[dict[str, Any]] = []

    def add(check_id: str, passed: bool, detail: Any) -> None:
        checks.append({"id": check_id, "result": "PASS" if passed else "FAIL", "detail": detail})

    add(
        "D-01-predecessor-reproduces-gap",
        "content_promise" in before["gaps_text"] and not field_value(before["capability_call"], "content_promise"),
        {"gaps": before["gaps_text"]},
    )
    add(
        "P-01-exact-user-equivalent-projected",
        field_value(positive["capability_call"], "content_promise") == expected
        and "content_promise" not in positive["gaps_text"],
        {"value": field_value(positive["capability_call"], "content_promise"), "gaps": positive["gaps_text"]},
    )
    add(
        "P-02-independent-subject-gap-preserved",
        "expression_subject_and_boundary" in positive["gaps_text"],
        positive["gaps_text"],
    )
    add(
        "N-01-unsupported-model-value-rejected",
        "content_promise" in unsupported["gaps_text"]
        and not field_value(unsupported["capability_call"], "content_promise"),
        unsupported["gaps_text"],
    )
    add(
        "N-02-no-consumption-outcome-rejected",
        "content_promise" in no_outcome["gaps_text"]
        and not field_value(no_outcome["capability_call"], "content_promise"),
        no_outcome["gaps_text"],
    )
    add(
        "N-03-other-capability-unchanged",
        "content_promise" in other_capability["gaps_text"]
        and not field_value(other_capability["capability_call"], "content_promise"),
        other_capability["gaps_text"],
    )
    add(
        "N-04-explicit-promise-preserved",
        field_value(explicit["capability_call"], "content_promise") == "只讲一件外套如何压住整套",
        field_value(explicit["capability_call"], "content_promise"),
    )
    add("I-01-only-uapp-fields-changed", touched == ["uapp_fields"], touched)
    report = {
        "document": {"id": "GAP01_SUCCESSOR_CONTROLS_v1.1", "model_calls": 0},
        "checks": checks,
        "summary": {
            "passed": sum(item["result"] == "PASS" for item in checks),
            "total": len(checks),
            "verdict": "PASS" if checks and all(item["result"] == "PASS" for item in checks) else "FAIL",
        },
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    LOGGER.info("%s", json.dumps(report["summary"], ensure_ascii=False, sort_keys=True))
    return 0 if report["summary"]["verdict"] == "PASS" else 1


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    raise SystemExit(main())
