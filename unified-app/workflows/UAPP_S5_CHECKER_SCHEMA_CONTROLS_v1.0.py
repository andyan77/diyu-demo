#!/usr/bin/env python3
"""Zero-model discrimination controls for Checker field decoding."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from types import ModuleType

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
OUTPUT = (
    ROOT
    / "evidence"
    / "stages"
    / "s5_final_convergence_v1_0"
    / "UAPP_S5_CHECKER_SCHEMA_CONTROLS_v1.0.json"
)


def load_module(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


CHECKER = load_module(
    "uapp_s5_checker_schema_controls",
    HERE / "UAPP_S5_FINAL_CHECKER_v1.1.py",
)


def main() -> int:
    read = CHECKER.field_value
    controls = {
        "canonical_v_positive": read({"f": {"v": "品牌搭配师"}}, "f")
        == "品牌搭配师",
        "legacy_value_compatible": read({"f": {"value": "旧投影"}}, "f")
        == "旧投影",
        "legacy_value_text_compatible": read(
            {"f": {"value_text": "旧文本投影"}}, "f"
        )
        == "旧文本投影",
        "negative_missing_field_empty": read({}, "f") == "",
        "negative_wrong_field_not_substituted": read(
            {"other": {"v": "品牌搭配师"}}, "f"
        )
        == "",
        "negative_empty_v_empty": read({"f": {"v": ""}}, "f") == "",
    }
    result = {
        "document": {
            "id": "UAPP_S5_CHECKER_SCHEMA_CONTROLS_v1.0",
            "task_id": "DIYU-V1-UNIFIED-DIFY-APPLICATION-001",
        },
        "model_calls": 0,
        "controls": controls,
        "passed": sum(controls.values()),
        "total": len(controls),
        "verdict": "PASS" if all(controls.values()) else "FAIL",
    }
    with OUTPUT.open("x", encoding="utf-8") as handle:
        json.dump(result, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0 if result["verdict"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
