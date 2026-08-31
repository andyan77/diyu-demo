#!/usr/bin/env python3
"""Business-semantic successor for the frozen EQUIV negative checker."""

from __future__ import annotations

import importlib.util
import os
from types import ModuleType
from typing import Any

HERE = os.path.dirname(os.path.abspath(__file__))


def load_module(name: str, path: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


BASE = load_module(
    "uapp_s5_final_checker_v11_parent",
    os.path.join(HERE, "UAPP_S5_FINAL_CHECKER_v1.1.py"),
)


def no_new_product(raw: dict[str, Any]) -> bool:
    state = raw.get("m2_after")
    if not isinstance(state, dict):
        return False
    return not state.get("artifacts") and not state.get("content_versions")


def evaluate_turn(
    raw: dict[str, Any],
    turn: dict[str, Any],
    gate: dict[str, Any],
    predecessors: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    result = BASE.evaluate_turn(raw, turn, gate, predecessors)
    if turn.get("equivalence", "").startswith("negative"):
        valid = no_new_product(raw)
        for item in result["checks"]:
            if item["id"] == "EQUIV-N1":
                item["result"] = "PASS" if valid else "FAIL"
                item["detail"] = {
                    "no_new_artifact_or_content_version": valid,
                    "physical_question_node_not_frozen": True,
                }
        result["verdict"] = (
            "PASS"
            if all(item["result"] == "PASS" for item in result["checks"])
            else "FAIL"
        )
    return result


exclusive_write = BASE.exclusive_write
