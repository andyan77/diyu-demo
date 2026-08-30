#!/usr/bin/env python3
"""Discrimination controls for the semantic GAP-01 checker."""

from __future__ import annotations

import importlib.util
import json
import logging
from pathlib import Path
from types import ModuleType
from typing import Any

LOGGER = logging.getLogger(__name__)
HERE = Path(__file__).resolve().parent
UAPP_ROOT = HERE.parent
OUTPUT = UAPP_ROOT / "evidence" / "stages" / "gap01_successor_v1_0" / "checker_controls.json"


def load_module(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


CHECKER = load_module("gap01_checker_controls_target", HERE / "GAP01_SUCCESSOR_CHECKER_v1.0.py")


def main() -> int:
    if OUTPUT.exists():
        raise FileExistsError(OUTPUT)
    g2 = "主推秋冬新款廓形西装外套，库存充足可以出镜。希望她看完知道缺的是一件外套。"
    fixtures = {
        "positive": "你这次是想先安排一周的整体发布节奏，还是先围绕一个具体商品或内容方向做一条内容？",
        "multi_question": "你想做整周排期吗？具体做什么商品？",
        "deadline": "这件事最晚什么时候发布？",
        "one_sided": "你想做整周排期吗？",
        "internal_leak": "你想走 CAMPAIGN，还是围绕具体商品做一条内容？",
    }
    observations = {name: CHECKER.g1_semantics(text, g2) for name, text in fixtures.items()}
    checks: list[dict[str, Any]] = []

    def add(check_id: str, passed: bool, detail: Any) -> None:
        checks.append({"id": check_id, "result": "PASS" if passed else "FAIL", "detail": detail})

    add("C-01-positive", all(observations["positive"].values()), observations["positive"])
    add("C-02-multi-question", not observations["multi_question"]["one_question"], observations["multi_question"])
    add("C-03-deadline", not observations["deadline"]["answerable_by_frozen_g2"], observations["deadline"])
    add("C-04-one-sided", not observations["one_sided"]["route_changing_fork"], observations["one_sided"])
    add("C-05-internal-leak", not observations["internal_leak"]["natural_language"], observations["internal_leak"])
    report = {
        "document": {"id": "GAP01_CHECKER_CONTROLS_v1.0", "model_calls": 0},
        "checks": checks,
        "summary": {
            "passed": sum(item["result"] == "PASS" for item in checks),
            "total": len(checks),
            "verdict": "PASS" if all(item["result"] == "PASS" for item in checks) else "FAIL",
        },
    }
    OUTPUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    LOGGER.info("%s", json.dumps(report["summary"], ensure_ascii=False, sort_keys=True))
    return 0 if report["summary"]["verdict"] == "PASS" else 1


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    raise SystemExit(main())
