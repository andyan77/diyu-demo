#!/usr/bin/env python3
"""Frozen machine checker for the one CAP-06 formal raw record."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
UAPP_ROOT = HERE.parent
RAW = UAPP_ROOT / "evidence" / "stages" / "cap06_semantic_contract_v1_0" / "formal" / "CAP06_FORMAL_RAW_v1.0.json"
RESULT = UAPP_ROOT / "stages" / "CAP06_FORMAL_RESULT_v1.0.json"
CONTROLS = UAPP_ROOT / "evidence" / "stages" / "cap06_semantic_contract_v1_0" / "CAP06_DETERMINISTIC_CONTROLS_v1.0.json"
EXPECTED_BODY_SHA256 = "00c3372f5b38e5eca06a9cf97fa7acc09707b753deceea2e3f670f84051e9fcd"
CAPABILITIES = (
    "MATRIX", "CAMPAIGN", "CONTENT_BRIEF", "CREATIVE_SCRIPT",
    "PRODUCTION_DIRECTOR", "PUBLISHING_PACKAGING",
)


def parsed(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    if not isinstance(value, str) or not value.strip():
        return {}
    try:
        result = json.loads(value)
    except json.JSONDecodeError:
        return {}
    return result if isinstance(result, dict) else {}


def app_runs(raw: dict[str, Any], name: str) -> list[dict[str, Any]]:
    value = raw.get("app_runs_in_window", {}).get(name, [])
    return value if isinstance(value, list) else []


def node_output(raw: dict[str, Any], app: str, node_id: str) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for run in app_runs(raw, app):
        rows.extend(
            row for row in run.get("node_detail", []) if row.get("node_id") == node_id
        )
    return parsed(rows[-1].get("outputs")) if rows else {}


def json_body(call: str, key: str) -> str:
    match = re.search(rf'^"{re.escape(key)}"\s*:\s*("(?:[^"\\]|\\.)*")$', call, re.MULTILINE)
    return str(json.loads(match.group(1))) if match else ""


def llm_attempts(raw: dict[str, Any]) -> int:
    return sum(
        1
        for runs in raw.get("app_runs_in_window", {}).values()
        for run in runs
        for row in run.get("node_detail", [])
        if row.get("node_type") == "llm"
    )


def evaluate(raw: dict[str, Any]) -> dict[str, Any]:
    fields = node_output(raw, "UAPP", "uapp_fields")
    call = str(fields.get("capability_call") or "")
    body = json_body(call, "content_body_or_beats")
    pp_envelope = node_output(raw, "PUBLISHING_PACKAGING", "envelope_check")
    seam = node_output(raw, "UAPP", "uapp_seam")
    artifact = str(seam.get("artifact") or "")
    delivery = str(seam.get("user_delivery") or raw.get("answer") or "")
    lower_delivery = delivery.lower()
    run_counts = {name: len(app_runs(raw, name)) for name in CAPABILITIES}
    scoped = raw.get("m2_after") or {}
    non_test = raw.get("global_m2_after") or {}
    pre_global = raw.get("preflight", {}).get("global_m2") or {}
    controls = json.loads(CONTROLS.read_text(encoding="utf-8"))
    packaging_markers = {
        "title": bool(re.search(r"标题", artifact)),
        "cover": bool(re.search(r"封面", artifact)),
        "first_frame": bool(re.search(r"首帧", artifact)),
        "publish_copy": bool(re.search(r"发布文案|正文", artifact)),
        "topics": bool(re.search(r"话题|#", artifact)),
        "natural_cta": bool(re.search(r"CTA|引导语|评论|收藏|你更喜欢|你会选", artifact, re.I)),
    }
    forbidden_commercial = (
        "私信购买", "点击购买", "站外购买", "到店购买", "咨询购买", "折扣价", "限时折扣"
    )
    leakage = (
        "PUBLISHING_PACKAGING", "LOW_RISK_INTERACTION", "artifact_binding_status",
        "cta_contract", "app_id", "workflow_run_id", "PASS", "FAIL", "STALE",
    )
    checks = {
        "CAP06-01_only_pp": run_counts["PUBLISHING_PACKAGING"] == 1
        and all(run_counts[name] == 0 for name in CAPABILITIES if name != "PUBLISHING_PACKAGING"),
        "CAP06-02_body_hash": bool(body)
        and hashlib.sha256(body.encode("utf-8")).hexdigest() == EXPECTED_BODY_SHA256,
        "CAP06-03_platform": pp_envelope.get("platform") == "小红书",
        "CAP06-03_low_risk_cta": pp_envelope.get("cta_level") == "LOW_RISK_INTERACTION",
        "CAP06-04_artifact_nonempty": len(artifact.strip()) >= 100,
        "CAP06-04_six_outputs": all(packaging_markers.values()),
        "CAP06-05_no_forbidden_commercial_claim": not any(
            token in artifact or token in delivery for token in forbidden_commercial
        ),
        "CAP06-05_fact_boundary": "显瘦" not in artifact
        or bool(re.search(r"不承诺显瘦|不能承诺显瘦", artifact)),
        "CAP06-06_natural_delivery": bool(delivery.strip())
        and not any(token.lower() in lower_delivery for token in leakage),
        "CAP06-07_http_and_transport": raw.get("http_status") == 200
        and not raw.get("transport_error"),
        "CAP06-07_no_real_publish": not scoped.get("publish_instances")
        and non_test == pre_global,
        "CAP06-07_test_scope": all(
            row.get("is_test") is True or row.get("is_simulated") is True
            for table in ("publish_instances", "feedback_records")
            for row in scoped.get(table, [])
        ),
        "CAP06-08_controls_current": controls.get("all_pass") is True
        and controls.get("passed") == controls.get("total") == 23,
        "CAP06-08_llm_budget": 0 < llm_attempts(raw) <= 14,
        "CAP06-08_no_internal_replay": all(
            len(runs) <= 1 for runs in raw.get("app_runs_in_window", {}).values()
        ),
    }
    return {
        "document": {
            "id": "CAP06_FORMAL_RESULT_v1.0",
            "task_id": "DIYU-V1-UNIFIED-DIFY-APPLICATION-001",
        },
        "run_id": raw.get("workflow_run_id"),
        "checks": checks,
        "packaging_outputs": packaging_markers,
        "capability_run_counts": run_counts,
        "body": {"length": len(body), "sha256": hashlib.sha256(body.encode()).hexdigest() if body else ""},
        "platform": pp_envelope.get("platform"),
        "cta_level": pp_envelope.get("cta_level"),
        "artifact": {"length": len(artifact), "sha256": hashlib.sha256(artifact.encode()).hexdigest() if artifact else ""},
        "llm_attempts": llm_attempts(raw),
        "manual_retries": 0,
        "platform_internal_replays": sum(max(0, len(runs) - 1) for runs in raw.get("app_runs_in_window", {}).values()),
        "verdict": "PASS" if all(checks.values()) else "FAIL",
    }


def main() -> int:
    if RESULT.exists():
        raise FileExistsError(RESULT)
    report = evaluate(json.loads(RAW.read_text(encoding="utf-8")))
    RESULT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0 if report["verdict"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
