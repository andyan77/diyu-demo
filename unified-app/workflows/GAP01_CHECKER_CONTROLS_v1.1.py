#!/usr/bin/env python3
"""Discrimination controls for GAP-01 successor Checker v1.1."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from types import ModuleType
from typing import Any

HERE = Path(__file__).resolve().parent
UAPP_ROOT = HERE.parent
OUTPUT = UAPP_ROOT / "evidence" / "stages" / "gap01_successor_v1_1" / "checker_controls.json"


def load_module(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


CHECKER = load_module("gap01_v11_checker_controls", HERE / "GAP01_SUCCESSOR_CHECKER_v1.1.py")


def main() -> int:
    if OUTPUT.exists():
        raise FileExistsError(OUTPUT)
    cases = [
        (
            "positive-new-subject-gap",
            "这条内容由谁来表达？",
            "expression_subject_and_boundary",
            "COMPONENT_RETURN",
            True,
        ),
        (
            "negative-repeated-promise",
            "这条内容对观众的承诺是什么？",
            "content_promise, expression_subject_and_boundary",
            "COMPONENT_RETURN",
            False,
        ),
        (
            "negative-repeated-route",
            "你是要整体发布节奏，还是具体商品或内容方向？",
            "expression_subject_and_boundary",
            "COMPONENT_RETURN",
            False,
        ),
        (
            "negative-two-questions",
            "由谁表达？在哪里拍？",
            "expression_subject_and_boundary",
            "COMPONENT_RETURN",
            False,
        ),
        (
            "negative-no-component-return",
            "这条内容由谁来表达？",
            "expression_subject_and_boundary",
            "",
            False,
        ),
    ]
    checks: list[dict[str, Any]] = []
    for case_id, answer, missing, status, expected in cases:
        detail = CHECKER.legal_next_gap(answer, missing, status)
        actual = all(detail.values())
        checks.append(
            {
                "id": case_id,
                "result": "PASS" if actual == expected else "FAIL",
                "expected": expected,
                "actual": actual,
                "detail": detail,
            }
        )
    report = {
        "document": {"id": "GAP01_CHECKER_CONTROLS_v1.1", "model_calls": 0},
        "checks": checks,
        "summary": {
            "passed": sum(item["result"] == "PASS" for item in checks),
            "total": len(checks),
            "verdict": "PASS" if all(item["result"] == "PASS" for item in checks) else "FAIL",
        },
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report["summary"], ensure_ascii=False, sort_keys=True))
    return 0 if report["summary"]["verdict"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
