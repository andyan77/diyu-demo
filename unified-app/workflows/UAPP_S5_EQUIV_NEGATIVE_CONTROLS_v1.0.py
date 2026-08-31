#!/usr/bin/env python3
"""Zero-model controls for the EQUIV negative product predicate."""

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
    / "UAPP_S5_EQUIV_NEGATIVE_CONTROLS_v1.0.json"
)


def load_module(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


CHECKER = load_module(
    "uapp_s5_equiv_negative_controls",
    HERE / "UAPP_S5_FINAL_CHECKER_v1.2.py",
)


def main() -> int:
    predicate = CHECKER.no_new_product
    controls = {
        "positive_empty_product_rows": predicate(
            {"m2_after": {"artifacts": [], "content_versions": []}}
        ),
        "negative_artifact_present": not predicate(
            {"m2_after": {"artifacts": [{"id": "a"}], "content_versions": []}}
        ),
        "negative_content_version_present": not predicate(
            {"m2_after": {"artifacts": [], "content_versions": [{"id": "v"}]}}
        ),
        "negative_state_missing": not predicate({}),
    }
    result = {
        "document": {"id": "UAPP_S5_EQUIV_NEGATIVE_CONTROLS_v1.0"},
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
