#!/usr/bin/env python3
"""Executor successor correcting the runner preflight function binding."""

from __future__ import annotations

import importlib.util
import os
from types import ModuleType

HERE = os.path.dirname(os.path.abspath(__file__))


def load_module(name: str, path: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


BASE = load_module(
    "uapp_s5_final_exec_v13_parent",
    os.path.join(HERE, "UAPP_S5_FINAL_EXEC_v1.3.py"),
)
GATE = os.path.join(BASE.BASE.ROOT, "stages", "UAPP_S5_GATE_v2.4.json")


def frozen() -> tuple[dict[str, object], dict[str, object]]:
    scenarios = BASE.BASE.RUNNER.load_json(BASE.BASE.SCENARIOS)
    gate = BASE.BASE.RUNNER.load_json(GATE)
    if gate.get("document", {}).get("id") != "UAPP_S5_GATE_v2.4":
        raise RuntimeError("Unexpected preflight-binding successor Gate")
    return scenarios, gate


BASE.GATE = GATE
BASE.__file__ = __file__
BASE.frozen = frozen
BASE.BASE.GATE = GATE
BASE.BASE.RUNNER.GATE = GATE
BASE.BASE.RUNNER.frozen = frozen
BASE.BASE.RUNNER.preflight = BASE.preflight


if __name__ == "__main__":
    raise SystemExit(BASE.main())

