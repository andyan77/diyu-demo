#!/usr/bin/env python3
"""v1.2 adapter: accept the versioned v1.1 Gate in the inherited v1.0 Runner."""

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


BASE = load_module("uapp_s5_exec_v11_for_v12", os.path.join(HERE, "UAPP_S5_EXEC_v1.1.py"))


def frozen() -> tuple[dict, dict]:
    for path in (BASE.RUNNER.SCENARIOS, BASE.RUNNER.MANIFEST, BASE.RUNNER.GATE):
        if not os.path.exists(path):
            raise RuntimeError(f"Frozen prerequisite absent: {path}")
    scenarios = BASE.RUNNER.load_json(BASE.RUNNER.SCENARIOS)
    gate = BASE.RUNNER.load_json(BASE.RUNNER.GATE)
    if gate.get("document", {}).get("id") != "UAPP_S5_GATE_v1.1":
        raise RuntimeError("Unexpected successor Gate identity")
    return scenarios, gate


BASE.RUNNER.frozen = frozen


if __name__ == "__main__":
    raise SystemExit(BASE.main())
