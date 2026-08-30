#!/usr/bin/env python3
"""Versioned checker fix for the Seam tool-parameter binding observation."""

from __future__ import annotations

import argparse
import importlib.util
import json
import logging
from pathlib import Path
from types import ModuleType

LOGGER = logging.getLogger(__name__)
HERE = Path(__file__).resolve().parent
UAPP = HERE.parent
OUTPUT = (
    UAPP
    / "evidence"
    / "stages"
    / "uapp_s5_inline_artifact_successor_v1_0"
    / "controls"
    / "UAPP_S5_INLINE_ARTIFACT_SUCCESSOR_CONTROLS_v1.1.json"
)


def load_module(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


V10 = load_module(
    "uapp_s5_inline_successor_controls_v10",
    HERE / "UAPP_S5_INLINE_ARTIFACT_SUCCESSOR_CONTROLS_v1.0.py",
)


def build_report() -> dict[str, object]:
    report = V10.build_report()
    base = V10.BUILD.BASE.published_graph()
    candidate, _ = V10.BUILD.patch_graph(base)
    nodes = {node["id"]: node for node in candidate["nodes"]}
    seam_parameters = nodes["uapp_seam"]["data"].get("tool_parameters") or {}
    call_parameter = seam_parameters.get("capability_call") or {}
    controls = report["controls"]
    if not isinstance(controls, dict):
        raise RuntimeError("v1.0 controls are not an object")
    controls["P09_pd_actual_input_path_bound"] = (
        call_parameter.get("value") == "{{#uapp_fields.capability_call#}}"
    )
    document = report["document"]
    if not isinstance(document, dict):
        raise RuntimeError("v1.0 document is not an object")
    document["id"] = "UAPP_S5_INLINE_ARTIFACT_SUCCESSOR_CONTROLS_v1.1"
    document["parent"] = "UAPP_S5_INLINE_ARTIFACT_SUCCESSOR_CONTROLS_v1.0"
    document["checker_fix"] = "read tool_parameters.capability_call.value"
    report["passed"] = sum(bool(value) for value in controls.values())
    report["total"] = len(controls)
    report["all_pass"] = all(bool(value) for value in controls.values())
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    report = build_report()
    LOGGER.info("controls %d/%d", report["passed"], report["total"])
    controls = report["controls"]
    failed = [name for name, passed in controls.items() if not passed]
    if failed:
        LOGGER.error("failed controls: %s", ", ".join(failed))
    if args.write:
        if OUTPUT.exists():
            raise FileExistsError(f"Refusing to overwrite {OUTPUT}")
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0 if report["all_pass"] else 1


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    raise SystemExit(main())
