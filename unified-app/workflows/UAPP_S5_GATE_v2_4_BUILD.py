#!/usr/bin/env python3
"""Build the executor-binding-only successor Gate from Gate v2.3."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PARENT = ROOT / "stages" / "UAPP_S5_GATE_v2.3.json"
OUTPUT = ROOT / "stages" / "UAPP_S5_GATE_v2.4.json"
EXECUTOR = ROOT / "workflows" / "UAPP_S5_FINAL_EXEC_v1.4.py"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    gate = json.loads(PARENT.read_text(encoding="utf-8"))
    gate["document"] = {
        "id": "UAPP_S5_GATE_v2.4",
        "task_id": gate["document"]["task_id"],
        "authority": gate["document"]["authority"],
        "parent_gate": "UAPP_S5_GATE_v2.3",
        "parent_gate_sha256": digest(PARENT),
        "semantic_delta": "NONE_EXECUTOR_PREFLIGHT_BINDING_ONLY",
        "frozen_before_next_model_call": True,
    }
    gate["frozen_files"]["executor_sha256"] = digest(EXECUTOR)
    gate["inherited_tool_failure"] = {
        "turn_key": "UAPP-EQUIV-01b",
        "model_output": 0,
        "state_side_effect": 0,
        "raw_created": False,
        "classification": "INPUT_ENVIRONMENT_OR_TOOL",
        "same_formal_slot_retained": True,
    }
    with OUTPUT.open("x", encoding="utf-8") as handle:
        json.dump(gate, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    print(digest(OUTPUT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

