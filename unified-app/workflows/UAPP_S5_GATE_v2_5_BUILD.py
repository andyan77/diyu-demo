#!/usr/bin/env python3
"""Build the EQUIV-negative checker successor Gate from Gate v2.4."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PARENT = ROOT / "stages" / "UAPP_S5_GATE_v2.4.json"
OUTPUT = ROOT / "stages" / "UAPP_S5_GATE_v2.5.json"
EXECUTOR = ROOT / "workflows" / "UAPP_S5_FINAL_EXEC_v1.5.py"
CHECKER = ROOT / "workflows" / "UAPP_S5_FINAL_CHECKER_v1.2.py"
EVIDENCE = ROOT / "evidence" / "stages" / "s5_final_convergence_v1_0"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    gate = json.loads(PARENT.read_text(encoding="utf-8"))
    gate["document"] = {
        "id": "UAPP_S5_GATE_v2.5",
        "task_id": gate["document"]["task_id"],
        "authority": gate["document"]["authority"],
        "parent_gate": "UAPP_S5_GATE_v2.4",
        "parent_gate_sha256": digest(PARENT),
        "semantic_delta": "NONE_REMOVE_PHYSICAL_QUESTION_NODE_OVERCONSTRAINT",
        "frozen_before_next_model_call": True,
    }
    gate["frozen_files"]["executor_sha256"] = digest(EXECUTOR)
    gate["frozen_files"]["checker_sha256"] = digest(CHECKER)
    gate["frozen_files"]["equiv_negative_controls_sha256"] = digest(
        EVIDENCE / "UAPP_S5_EQUIV_NEGATIVE_CONTROLS_v1.0.json"
    )
    gate["inherited_checker_failure"] = {
        "turn_key": "UAPP-EQUIV-01n",
        "workflow_run_id": "f3d3ac80-366b-4ef6-905f-57a54b689607",
        "raw_sha256": digest(
            EVIDENCE / "formal_successor" / "raw" / "UAPP-EQUIV-01n.json"
        ),
        "old_check_sha256": digest(
            EVIDENCE / "formal_successor" / "checks_v1_3" / "UAPP-EQUIV-01n.json"
        ),
        "old_result": "FAIL / CURRENT",
        "confirmed_origin": "CHECKER_OR_FIXTURE",
        "model_rerun": False,
        "adjudication": "REUSE_RAW_WITH_FROZEN_BUSINESS_PREDICATES",
    }
    gate["budget"]["used_top_level_runs"] = 7
    gate["budget"]["used_llm_node_attempts"] = 31
    with OUTPUT.open("x", encoding="utf-8") as handle:
        json.dump(gate, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    print(digest(OUTPUT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
