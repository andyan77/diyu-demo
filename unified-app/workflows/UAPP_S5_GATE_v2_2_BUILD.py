#!/usr/bin/env python3
"""Build the single SUT-successor Gate from Gate v2.1."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PARENT = ROOT / "stages" / "UAPP_S5_GATE_v2.1.json"
OUTPUT = ROOT / "stages" / "UAPP_S5_GATE_v2.2.json"
EXECUTOR = ROOT / "workflows" / "UAPP_S5_FINAL_EXEC_v1.2.py"
EVIDENCE = ROOT / "evidence" / "stages" / "s5_final_convergence_v1_0"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    gate = json.loads(PARENT.read_text(encoding="utf-8"))
    gate["document"] = {
        "id": "UAPP_S5_GATE_v2.2",
        "task_id": gate["document"]["task_id"],
        "authority": gate["document"]["authority"],
        "parent_gate": "UAPP_S5_GATE_v2.1",
        "parent_gate_sha256": digest(PARENT),
        "semantic_delta": "NONE_SINGLE_AUTHORIZED_WITHDRAWAL_SUT_SUCCESSOR",
        "frozen_before_successor_model_call": True,
    }
    gate["candidate"]["UAPP_graph_canonical_sha256"] = (
        "1dd9f77466533724536e83837c66f906ca94b6b39e90869e7172b90948517e36"
    )
    gate["candidate"]["graph_md5"]["UAPP"] = "6ac5a45f3953683339f4ea77ebcc00c6"
    gate["candidate"]["node_count"] = 69
    gate["candidate"]["edge_count"] = 74
    gate["frozen_files"]["executor_sha256"] = digest(EXECUTOR)
    gate["frozen_files"]["withdraw_successor_controls_sha256"] = digest(
        EVIDENCE / "WITHDRAW_SUCCESSOR_CONTROLS_v1.0.json"
    )
    gate["frozen_files"]["withdraw_successor_publication_sha256"] = digest(
        EVIDENCE / "withdraw_successor_publication.json"
    )
    gate["inherited_failed_attempt"] = {
        "turn_key": "UAPP-WITHDRAW-01:W1",
        "workflow_run_id": "e135f463-00a5-4d47-a3d4-fadf91194e96",
        "raw_sha256": digest(EVIDENCE / "formal" / "raw" / "UAPP-WITHDRAW-01_W1.json"),
        "check_sha256": digest(
            EVIDENCE / "formal" / "checks_v1_1" / "UAPP-WITHDRAW-01_W1.json"
        ),
        "result": "FAIL / CURRENT",
        "confirmed_origin": "SYSTEM_UNDER_TEST",
        "successor_rerun_authorized": True,
    }
    gate["budget"]["used_top_level_runs"] = 2
    gate["budget"]["used_llm_node_attempts"] = 7
    gate["stop_rules"]["third_withdraw_candidate_prohibited"] = True
    with OUTPUT.open("x", encoding="utf-8") as handle:
        json.dump(gate, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    print(digest(OUTPUT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
