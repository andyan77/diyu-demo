#!/usr/bin/env python3
"""Replay both CAP-05 failures and freeze the inline-artifact seam oracle.

This diagnostic performs no model or Dify write.  It binds the historical RAW
attempts to a deterministic source-classification oracle, single-variable
negative controls, and equivalent natural-language carriers.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import re
from pathlib import Path
from typing import Any

LOGGER = logging.getLogger(__name__)
REPO = Path(__file__).resolve().parents[2]
UAPP = REPO / "unified-app"
SCENARIOS = UAPP / "stages" / "UAPP_S5_FROZEN_SCENARIOS_v1.1.json"
RAW_V15 = UAPP / "evidence" / "stages" / "uapp_s5_v1_4" / "raw" / "UAPP-CAP-05.json"
RAW_V16 = UAPP / "evidence" / "stages" / "uapp_s5_v1_6" / "raw" / "UAPP-CAP-05.json"
OUTPUT = (
    UAPP
    / "evidence"
    / "stages"
    / "uapp_s5_inline_artifact_v1_0"
    / "phase_a"
    / "UAPP_S5_INLINE_ARTIFACT_PHASE_A_REPLAY_v1.0.json"
)

CONFIRM_RE = re.compile(r"确认可用|已确认|已经确认|已定稿|已经拍完|已经实现|现有成片|现有素材")
PLACEHOLDER_RE = re.compile(r"待补|稍后补|略|占位|TBD|TODO|\.\.\.|……", re.IGNORECASE)
SCRIPT_RE = re.compile(
    r"(?:口播稿|脚本|逐字稿)\s*[：:]\s*(?:[“\"](?P<quoted>.+?)[”\"]|```(?:\w+)?\s*(?P<fenced>.+?)```)",
    re.DOTALL,
)
CONTENT_RE = re.compile(
    r"(?:实际成片内容是|已有成片内容|已有内容正文|素材说明)\s*[：:]\s*(?P<body>.+?)"
    r"(?=(?:\n|。)?(?:商品当前|本次发|请基于))",
    re.DOTALL,
)


def sha256_bytes(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def fnv1a64(value: str) -> str:
    result = 0xCBF29CE484222325
    for byte in value.encode("utf-8"):
        result = ((result ^ byte) * 0x100000001B3) & 0xFFFFFFFFFFFFFFFF
    return f"{result:016x}"


def normalized(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def json_value(value: Any) -> Any:
    if not isinstance(value, str):
        return value
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return value


def node_row(raw: dict[str, Any], node_id: str) -> dict[str, Any] | None:
    runs = raw.get("app_runs_in_window", {}).get("UAPP", [])
    if not runs:
        return None
    for row in runs[0].get("node_detail", []):
        if row.get("node_id") == node_id:
            return {
                "status": row.get("status"),
                "inputs": json_value(row.get("inputs")),
                "outputs": json_value(row.get("outputs")),
            }
    return None


def frozen_turn(case_id: str) -> dict[str, Any]:
    document = json.loads(SCENARIOS.read_text(encoding="utf-8"))
    return next(turn for turn in document["turns"] if turn["case_id"] == case_id)


def classify_inline(
    user_request: str,
    target_capability: str,
    task_key: str,
    correction_status: str = "NONE",
) -> dict[str, Any]:
    request = user_request or ""
    target = (target_capability or "").strip()
    task = (task_key or "").strip()
    if correction_status == "REJECTED":
        return {"status": "REJECTED", "reason": "CORRECTION_REJECTED"}
    if not task:
        return {"status": "REJECTED", "reason": "TASK_SCOPE_MISSING"}
    if not CONFIRM_RE.search(request):
        return {"status": "REJECTED", "reason": "NOT_CONFIRMED"}

    body = ""
    artifact_type = ""
    upstream_capability = ""
    if target == "PRODUCTION_DIRECTOR":
        matches = list(SCRIPT_RE.finditer(request))
        if len(matches) != 1:
            return {
                "status": "REJECTED",
                "reason": "AMBIGUOUS" if len(matches) > 1 else "BODY_NOT_FOUND",
            }
        body = matches[0].group("quoted") or matches[0].group("fenced") or ""
        artifact_type = "SCRIPT_OR_EQUIVALENT_BEATS"
        upstream_capability = "CREATIVE_SCRIPT"
    elif target == "PUBLISHING_PACKAGING":
        matches = list(CONTENT_RE.finditer(request))
        if len(matches) != 1:
            return {
                "status": "REJECTED",
                "reason": "AMBIGUOUS" if len(matches) > 1 else "BODY_NOT_FOUND",
            }
        body = matches[0].group("body") or ""
        artifact_type = "CONTENT_BODY_OR_BEATS"
        upstream_capability = "USER_REALIZED_CONTENT"
    else:
        return {"status": "NONE", "reason": "TARGET_HAS_NO_INLINE_SLOT"}

    body = body.strip()
    compact = normalized(body)
    if len(compact) < 40 or PLACEHOLDER_RE.search(compact):
        return {"status": "REJECTED", "reason": "BODY_INCOMPLETE"}
    return {
        "status": "INLINE_READY",
        "reason": "CURRENT_TURN_USER_CONFIRMED",
        "body": body,
        "artifact_type": artifact_type,
        "upstream_capability": upstream_capability,
        "source_kind": "USER_INLINE_CONFIRMED",
        "source_turn": "CURRENT_TURN",
        "task_key": task,
        "fp": fnv1a64(compact[:256]),
        "bfp": fnv1a64(compact),
        "sha256": sha256_text(body),
    }


def phase_a_controls() -> dict[str, bool]:
    cap05 = frozen_turn("UAPP-CAP-05")
    cap06 = frozen_turn("UAPP-CAP-06")
    script = classify_inline(cap05["query"], cap05["expected_capability"], "task-a")
    content = classify_inline(cap06["query"], cap06["expected_capability"], "task-a")
    script_body = str(script.get("body") or "")

    double_quote = cap05["query"].replace("“", '"', 1).replace("”", '"', 1)
    fenced = cap05["query"].replace(f"“{script_body}”", f"```text\n{script_body}\n```")
    ambiguous = cap05["query"].replace(
        f"“{script_body}”", f"“{script_body}”\n另一份脚本：“{script_body}”", 1
    )
    unconfirmed = cap05["query"].replace("确认可用", "待讨论").replace("已确认脚本", "这份脚本")
    incomplete = cap05["query"].replace(script_body, "稍后补完整脚本", 1)

    controls = {
        "P01_cap05_inline_script_ready": script.get("status") == "INLINE_READY",
        "P02_cap05_body_is_exact_quote": script_body in cap05["query"] and bool(script_body),
        "P03_cap05_upstream_is_not_target": script.get("upstream_capability") == "CREATIVE_SCRIPT",
        "P04_cap05_task_scope_bound": script.get("task_key") == "task-a",
        "P05_cap05_hashes_recomputable": (
            script.get("fp") == fnv1a64(normalized(script_body)[:256])
            and script.get("bfp") == fnv1a64(normalized(script_body))
            and script.get("sha256") == sha256_text(script_body)
        ),
        "P06_cap06_inline_content_ready": content.get("status") == "INLINE_READY",
        "P07_double_quote_equivalent": classify_inline(
            double_quote, "PRODUCTION_DIRECTOR", "task-a"
        ).get("sha256")
        == script.get("sha256"),
        "P08_fenced_equivalent": classify_inline(fenced, "PRODUCTION_DIRECTOR", "task-a").get(
            "sha256"
        )
        == script.get("sha256"),
        "N01_unconfirmed_rejected": classify_inline(
            unconfirmed, "PRODUCTION_DIRECTOR", "task-a"
        ).get("reason")
        == "NOT_CONFIRMED",
        "N02_incomplete_rejected": classify_inline(
            incomplete, "PRODUCTION_DIRECTOR", "task-a"
        ).get("reason")
        == "BODY_INCOMPLETE",
        "N03_task_scope_missing_rejected": classify_inline(
            cap05["query"], "PRODUCTION_DIRECTOR", ""
        ).get("reason")
        == "TASK_SCOPE_MISSING",
        "N04_correction_rejected_stops": classify_inline(
            cap05["query"], "PRODUCTION_DIRECTOR", "task-a", "REJECTED"
        ).get("reason")
        == "CORRECTION_REJECTED",
        "N05_ambiguous_rejected": classify_inline(
            ambiguous, "PRODUCTION_DIRECTOR", "task-a"
        ).get("reason")
        == "AMBIGUOUS",
        "N06_wrong_target_not_bound": classify_inline(
            cap05["query"], "MATRIX", "task-a"
        ).get("status")
        == "NONE",
    }
    return controls


def build_report() -> dict[str, Any]:
    raw_v15 = json.loads(RAW_V15.read_text(encoding="utf-8"))
    raw_v16 = json.loads(RAW_V16.read_text(encoding="utf-8"))
    v15_correction = node_row(raw_v15, "uapp_td24_correction") or {}
    v16_correction = node_row(raw_v16, "uapp_td24_correction") or {}
    v16_selector = node_row(raw_v16, "uapp_pick_upstream") or {}
    v16_fields = node_row(raw_v16, "uapp_fields") or {}
    v16_gate = node_row(raw_v16, "uapp_td24_binding_gate") or {}
    v16_block = node_row(raw_v16, "uapp_td24_block") or {}
    v16_hop = node_row(raw_v16, "uapp_hop") or {}

    hop_outputs = v16_hop.get("outputs") if isinstance(v16_hop.get("outputs"), dict) else {}
    controls = phase_a_controls()
    observations = {
        "O01_v15_correction_rejected": (
            v15_correction.get("outputs", {}).get("correction_status") == "REJECTED"
        ),
        "O02_v16_correction_fixed": (
            v16_correction.get("outputs", {}).get("correction_status") == "NONE"
        ),
        "O03_v16_selector_self_upstream_confusion": (
            v16_selector.get("outputs", {}).get("selection_status") == "NAMED_UPSTREAM_INCOMPATIBLE"
        ),
        "O04_v16_hop_lost_script_slot": (
            "script_or_equivalent_beats" in str(hop_outputs.get("extraction_gaps_text") or "")
            and "content_body_or_beats" in str(hop_outputs.get("extracted_json") or "")
        ),
        "O05_v16_fields_rejected": (
            v16_fields.get("outputs", {}).get("artifact_binding_status") == "REJECTED"
        ),
        "O06_v16_seam_ineligible": v16_gate.get("outputs", {}).get("selected_case_id") == "blocked",
        "O07_v16_delivery_leaked_internal_name": "PRODUCTION_DIRECTOR"
        in str(v16_block.get("outputs", {}).get("final_text") or ""),
    }
    return {
        "document": {
            "id": "UAPP_S5_INLINE_ARTIFACT_PHASE_A_REPLAY_v1.0",
            "task_id": "DIYU-V1-UNIFIED-DIFY-APPLICATION-001",
            "model_calls": 0,
            "dify_writes": 0,
        },
        "bindings": {
            "scenarios_sha256": sha256_bytes(SCENARIOS),
            "raw_v15_sha256": sha256_bytes(RAW_V15),
            "raw_v16_sha256": sha256_bytes(RAW_V16),
        },
        "historical_replay_observations": observations,
        "frozen_positive_negative_and_equivalence_controls": controls,
        "observation_pass": all(observations.values()),
        "control_pass": all(controls.values()),
        "confirmed_highest_failing_seam": (
            "UAPP_CURRENT_TURN_INLINE_ARTIFACT_SOURCE_TO_BINDING_AND_DELIVERY"
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    report = build_report()
    LOGGER.info(
        "Phase A observations=%s controls=%s",
        report["observation_pass"],
        report["control_pass"],
    )
    if args.write:
        if OUTPUT.exists():
            raise FileExistsError(f"Refusing to overwrite {OUTPUT}")
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0 if report["observation_pass"] and report["control_pass"] else 1


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    raise SystemExit(main())
