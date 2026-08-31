#!/usr/bin/env python3
"""Schema-compatible successor for the frozen S5 business checker."""

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
    "uapp_s5_final_checker_v10_parent",
    os.path.join(HERE, "UAPP_S5_FINAL_CHECKER_v1.0.py"),
)


def field_value(fields: dict[str, Any], field_id: str) -> str:
    """Read the current canonical ``v`` key and legacy evidence projections."""
    value = fields.get(field_id)
    if isinstance(value, dict):
        return str(
            value.get("v") or value.get("value") or value.get("value_text") or ""
        )
    return str(value or "")


BASE.field_value = field_value
evaluate_turn = BASE.evaluate_turn
exclusive_write = BASE.exclusive_write
