#!/usr/bin/env python3
"""Build the checker-schema-only successor Gate from Gate v2.2."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PARENT = ROOT / "stages" / "UAPP_S5_GATE_v2.2.json"
OUTPUT = ROOT / "stages" / "UAPP_S5_GATE_v2.3.json"
EXECUTOR = ROOT / "workflows" / "UAPP_S5_FINAL_EXEC_v1.3.py"
CHECKER = ROOT / "workflows" / "UAPP_S5_FINAL_CHECKER_v1.1.py"
EVIDENCE = ROOT / "evidence" / "stages" / "s5_final_convergence_v1_0"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    gate = json.loads(PARENT.read_text(encoding="utf-8"))
    gate["document"] = {
        "id": "UAPP_S5_GATE_v2.3",
        "task_id": gate["document"]["task_id"],
        "authority": gate["document"]["authority"],
        "parent_gate": "UAPP_S5_GATE_v2.2",
        "parent_gate_sha256": digest(PARENT),
        "semantic_delta": "NONE_CHECKER_CANONICAL_FIELD_KEY_ONLY",
        "frozen_before_next_model_call": True,
    }
    gate["frozen_files"]["executor_sha256"] = digest(EXECUTOR)
    gate["frozen_files"]["checker_sha256"] = digest(CHECKER)
    gate["frozen_files"]["checker_schema_controls_sha256"] = digest(
        EVIDENCE / "UAPP_S5_CHECKER_SCHEMA_CONTROLS_v1.0.json"
    )
    gate["inherited_checker_failure"] = {
        "turn_key": "UAPP-EQUIV-01a",
        "workflow_run_id": "fb0c71a3-30d7-45ac-9a3b-a0ad36220790",
        "raw_sha256": digest(
            EVIDENCE / "formal_successor" / "raw" / "UAPP-EQUIV-01a.json"
        ),
        "old_check_sha256": digest(
            EVIDENCE / "formal_successor" / "checks_v1_2" / "UAPP-EQUIV-01a.json"
        ),
        "old_result": "FAIL / CURRENT",
        "confirmed_origin": "CHECKER_OR_FIXTURE",
        "model_rerun": False,
        "adjudication": "REUSE_RAW_WITH_IDENTICAL_BUSINESS_PREDICATES",
    }
    gate["budget"]["used_top_level_runs"] = 4
    gate["budget"]["used_llm_node_attempts"] = 15
    with OUTPUT.open("x", encoding="utf-8") as handle:
        json.dump(gate, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    print(digest(OUTPUT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
