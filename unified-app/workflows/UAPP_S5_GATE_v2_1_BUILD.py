#!/usr/bin/env python3
"""Build the check-writer-only successor Gate from frozen Gate v2.0."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PARENT = ROOT / "stages" / "UAPP_S5_GATE_v2.0.json"
OUTPUT = ROOT / "stages" / "UAPP_S5_GATE_v2.1.json"
EXECUTOR = ROOT / "workflows" / "UAPP_S5_FINAL_EXEC_v1.1.py"
W0_RAW = (
    ROOT
    / "evidence"
    / "stages"
    / "s5_final_convergence_v1_0"
    / "formal"
    / "raw"
    / "UAPP-WITHDRAW-01_W0.json"
)
W0_TOOL_CHECK = (
    ROOT
    / "evidence"
    / "stages"
    / "s5_final_convergence_v1_0"
    / "formal"
    / "checks"
    / "UAPP-WITHDRAW-01_W0.json"
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    gate = json.loads(PARENT.read_text(encoding="utf-8"))
    gate["document"] = {
        "id": "UAPP_S5_GATE_v2.1",
        "task_id": gate["document"]["task_id"],
        "authority": gate["document"]["authority"],
        "parent_gate": "UAPP_S5_GATE_v2.0",
        "parent_gate_sha256": digest(PARENT),
        "semantic_delta": "NONE_CHECK_WRITER_AND_MODULE_PATH_ONLY",
        "frozen_before_next_model_call": True,
    }
    gate["frozen_files"]["executor_sha256"] = digest(EXECUTOR)
    gate["inherited_parent_attempt"] = {
        "turn_key": "UAPP-WITHDRAW-01:W0",
        "workflow_run_id": "b3e44f33-b383-43a8-bd30-bacc271376be",
        "raw_sha256": digest(W0_RAW),
        "raw_gate_sha256": digest(PARENT),
        "erroneous_tool_check_sha256": digest(W0_TOOL_CHECK),
        "erroneous_tool_check_result": "NOT_VERIFIED(INPUT_ENVIRONMENT_OR_TOOL)",
        "model_rerun": False,
        "adjudication": "REUSE_RAW_WITH_IDENTICAL_BUSINESS_PREDICATES",
    }
    with OUTPUT.open("x", encoding="utf-8") as handle:
        json.dump(gate, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    print(digest(OUTPUT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
