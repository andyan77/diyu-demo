#!/usr/bin/env python3
"""Adjudicate the single TD-UAPP-24 formal run against its frozen Gate."""

from __future__ import annotations

import hashlib
import json
import logging
import os
from typing import Any

HERE = os.path.dirname(os.path.abspath(__file__))
UAPP_ROOT = os.path.abspath(os.path.join(HERE, ".."))
GATE_PATH = os.path.join(UAPP_ROOT, "stages", "UAPP_TD24_GATE_v1.0.json")
RAW_PATH = os.path.join(UAPP_ROOT, "evidence", "stages", "uapp_td24", "UAPP_TD24_RAW_v1.0.json")
OUTPUT_PATH = os.path.join(UAPP_ROOT, "stages", "UAPP_TD24_RESULT_v1.0.json")


def sha256_file(path: str) -> str:
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def load_json(path: str) -> dict[str, Any]:
    with open(path, encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise RuntimeError(f"JSON root is not an object: {path}")
    return value


def decode(value: Any) -> Any:
    if not isinstance(value, str):
        return value
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return value


def node_detail(raw: dict[str, Any], app: str, node_id: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for run in raw.get("app_runs_in_window", {}).get(app, []):
        for row in run.get("node_detail", []) or []:
            if isinstance(row, dict) and row.get("node_id") == node_id:
                rows.append(row)
    return rows


def node_outputs(raw: dict[str, Any], app: str, node_id: str) -> dict[str, Any]:
    rows = node_detail(raw, app, node_id)
    if len(rows) != 1:
        return {}
    value = decode(rows[0].get("outputs"))
    return value if isinstance(value, dict) else {}


def artifact_map(state: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(item.get("fp")): item
        for item in state.get("artifacts", [])
        if isinstance(item, dict) and item.get("fp")
    }


def criterion(
    criteria: list[dict[str, Any]],
    criterion_id: str,
    passed: bool,
    evidence: dict[str, Any],
) -> None:
    criteria.append(
        {
            "id": criterion_id,
            "result": "PASS / CURRENT" if passed else "FAIL / CURRENT",
            "evidence": evidence,
        }
    )


def run() -> dict[str, Any]:
    gate = load_json(GATE_PATH)
    raw = load_json(RAW_PATH)
    after_variables = raw.get("conversation_variables_after", {})
    state_raw = after_variables.get("uapp_task_fields") or "{}"
    store_raw = after_variables.get("uapp_last_artifact") or ""
    after = json.loads(state_raw)
    artifacts = artifact_map(after)
    fields = after.get("fields", {})
    before = gate["state_before"]
    expected = gate["expected_after"]

    correction = node_outputs(raw, "UAPP", "uapp_td24_correction")
    selector = node_outputs(raw, "UAPP", "uapp_pick_upstream")
    field_node = node_outputs(raw, "UAPP", "uapp_fields")
    block = node_outputs(raw, "UAPP", "uapp_td24_block")
    seam_rows = raw.get("app_runs_in_window", {}).get("SEAM", [])
    pp_rows = raw.get("app_runs_in_window", {}).get("PUBLISHING_PACKAGING", [])

    all_runs = [
        run
        for runs in raw.get("app_runs_in_window", {}).values()
        for run in runs
        if isinstance(run, dict)
    ]
    llm_nodes = [
        row
        for run in all_runs
        for row in (run.get("node_detail", []) or [])
        if isinstance(row, dict) and row.get("type") == "llm"
    ]
    failed_llm = [row for row in llm_nodes if row.get("status") != "succeeded"]

    profile = fields.get("production.profile", {})
    capacity = fields.get("production.capacity_or_owner", {})
    time_window = fields.get("production.time_window", {})
    facts = fields.get("facts.registered", {})
    criteria: list[dict[str, Any]] = []

    criterion(
        criteria,
        "C-01",
        correction.get("correction_status") == "APPLIED"
        and after.get("rev") == before["revision"] + 1
        and profile.get("v") == expected["fields"]["production.profile"]["value"]
        and profile.get("frev") == expected["fields"]["production.profile"]["frev"]
        and profile.get("kind") == "USER_UTTERANCE"
        and profile.get("ref") == expected["source_ref"],
        {
            "correction_status": correction.get("correction_status"),
            "state_revision": after.get("rev"),
            "profile": profile,
        },
    )
    criterion(
        criteria,
        "C-02",
        capacity.get("v") == expected["fields"]["production.capacity_or_owner"]["value"]
        and capacity.get("frev") == expected["fields"]["production.capacity_or_owner"]["frev"]
        and capacity.get("kind") == "USER_UTTERANCE"
        and capacity.get("ref") == expected["source_ref"]
        and "一人" not in profile.get("v", "")
        and "一人" not in capacity.get("v", ""),
        {"profile_value": profile.get("v"), "capacity_value": capacity.get("v")},
    )
    criterion(
        criteria,
        "C-03",
        time_window == before["fields"]["production.time_window"]
        and facts.get("v") == before["fields"]["facts.registered"]["v"]
        and facts.get("frev") == before["fields"]["facts.registered"]["frev"],
        {
            "time_window": time_window,
            "facts_value_sha256": sha256_text(facts.get("v", "")),
            "facts_frev": facts.get("frev"),
        },
    )
    direct_ok = all(
        artifacts[fp].get("stale") is True
        and "FIELD_CHANGED:" in (artifacts[fp].get("stale_reason") or "")
        for fp in expected["direct_affected_pd_fps"]
    )
    criterion(
        criteria,
        "C-04",
        direct_ok,
        {
            fp: {
                "stale": artifacts[fp].get("stale"),
                "reason": artifacts[fp].get("stale_reason"),
            }
            for fp in expected["direct_affected_pd_fps"]
        },
    )
    transitive_fp = expected["current_pp_fp"]
    transitive = artifacts.get(transitive_fp, {})
    criterion(
        criteria,
        "C-05",
        transitive.get("stale") is True
        and transitive.get("upstream_fp") == expected["current_pd_fp"]
        and f"UPSTREAM_STALE:{expected['current_pd_fp']}"
        in transitive.get("additional_stale_reasons", []),
        {
            "pp_fp": transitive_fp,
            "stale": transitive.get("stale"),
            "upstream_fp": transitive.get("upstream_fp"),
            "additional_stale_reasons": transitive.get("additional_stale_reasons"),
        },
    )
    preserved = all(
        artifacts[fp].get("stale") == record["stale"]
        and artifacts[fp].get("stale_reason") == record["stale_reason"]
        for fp, record in before["unaffected_artifacts"].items()
    )
    criterion(
        criteria,
        "C-06",
        preserved,
        {
            fp: {
                "before": record,
                "after": {
                    "stale": artifacts[fp].get("stale"),
                    "stale_reason": artifacts[fp].get("stale_reason"),
                },
            }
            for fp, record in before["unaffected_artifacts"].items()
        },
    )
    field_binding = decode(field_node.get("upstream_binding_json"))
    bound_old_pd = expected["current_pd_fp"] in json.dumps(field_binding, ensure_ascii=False) and any(
        isinstance(item, dict) and item.get("lineage") == "BOUND"
        for item in (field_binding if isinstance(field_binding, list) else [])
    )
    criterion(
        criteria,
        "C-07",
        selector.get("selection_status") == "NO_LEGAL_UPSTREAM"
        and field_node.get("artifact_binding_status") == "REJECTED"
        and not bound_old_pd
        and expected["current_pd_body_sha256"]
        != sha256_text(field_node.get("capability_call", "")),
        {
            "selector_status": selector.get("selection_status"),
            "binding_status": field_node.get("artifact_binding_status"),
            "binding": field_binding,
        },
    )
    criterion(
        criteria,
        "C-08",
        len(after.get("artifacts", [])) == before["artifact_count"]
        and not seam_rows
        and not pp_rows
        and node_detail(raw, "UAPP", "uapp_td24_block")
        and node_detail(raw, "UAPP", "uapp_td24_block_save")
        and not node_detail(raw, "UAPP", "uapp_seam"),
        {
            "artifact_count_before": before["artifact_count"],
            "artifact_count_after": len(after.get("artifacts", [])),
            "seam_runs": len(seam_rows),
            "pp_runs": len(pp_rows),
        },
    )
    answer = raw.get("answer") or ""
    forbidden = [
        token
        for token in (
            "STALE",
            "PASS",
            "FAIL",
            "uapp_",
            "app_id",
            "production.profile",
            "JSON",
        )
        if token in answer
    ]
    criterion(
        criteria,
        "C-09",
        "制作规模" in answer
        and "制作方案" in answer
        and "标题和封面" in answer
        and ("先" in answer or "更新" in answer)
        and "其他已经确认且不受影响的内容会保留" in answer
        and not forbidden
        and answer == block.get("final_text"),
        {"answer": answer, "forbidden_hits": forbidden},
    )
    m2_before = raw["preflight"]["m2"]
    criterion(
        criteria,
        "C-10",
        raw.get("m2_after") == m2_before
        and raw.get("m2_after", {}).get("account_publish_instances") == 0,
        {"m2_before": m2_before, "m2_after": raw.get("m2_after")},
    )
    professional_runs = {
        name: len(raw.get("app_runs_in_window", {}).get(name, []))
        for name in (
            "MATRIX",
            "CAMPAIGN",
            "CONTENT_BRIEF",
            "CREATIVE_SCRIPT",
            "PRODUCTION_DIRECTOR",
            "PUBLISHING_PACKAGING",
        )
    }
    criterion(
        criteria,
        "C-11",
        len(raw.get("app_runs_in_window", {}).get("UAPP", [])) == 1
        and len(raw.get("app_runs_in_window", {}).get("M3", [])) == 1
        and len(raw.get("app_runs_in_window", {}).get("HOP", [])) == 1
        and all(count == 0 for count in professional_runs.values())
        and len(llm_nodes) <= gate["budget"]["deepseek_llm_node_attempts_max"]
        and not failed_llm
        and raw.get("request_attempts_by_runner") == 1
        and not raw.get("transport_error"),
        {
            "professional_runs": professional_runs,
            "llm_attempts": len(llm_nodes),
            "failed_llm": len(failed_llm),
            "runner_attempts": raw.get("request_attempts_by_runner"),
        },
    )
    apps_after = raw.get("protected_apps_after", {})
    protected_expected = gate["protected_surface_after"]
    protected_ok = all(
        apps_after[name]["graph_md5"] == graph_md5
        for name, graph_md5 in protected_expected["graph_md5"].items()
    )
    git_after = raw.get("git_after", {})
    criterion(
        criteria,
        "C-12",
        protected_ok
        and git_after.get("main") == gate["git"]["main"]
        and git_after.get("origin_main") == gate["git"]["origin_main"]
        and sha256_text(store_raw) == before["store_sha256"],
        {
            "protected_apps": apps_after,
            "main": git_after.get("main"),
            "store_sha256": sha256_text(store_raw),
        },
    )

    passed = sum(item["result"] == "PASS / CURRENT" for item in criteria)
    verdict = "PASS / CURRENT" if passed == len(criteria) else "FAIL / CURRENT"
    return {
        "document": {
            "id": "UAPP_TD24_RESULT_v1.0",
            "task_id": "DIYU-V1-UNIFIED-DIFY-APPLICATION-001",
            "gate_sha256": sha256_file(GATE_PATH),
            "raw_sha256": sha256_file(RAW_PATH),
            "checker_sha256": sha256_file(__file__),
        },
        "formal_run": {
            "workflow_run_id": raw.get("workflow_run_id"),
            "message_id": raw.get("message_id"),
            "http_status": raw.get("http_status"),
            "top_level_workflow_runs": len(raw.get("app_runs_in_window", {}).get("UAPP", [])),
            "llm_node_attempts": len(llm_nodes),
            "failed_llm_nodes": len(failed_llm),
            "manual_retries": 0,
            "platform_internal_replays": 0,
            "repeat_sampling": 0,
            "ab_tests": 0,
            "reviewer_calls": 0,
        },
        "summary": {"pass": passed, "total": len(criteria), "verdict": verdict},
        "criteria": criteria,
        "result": verdict,
    }


def main() -> int:
    if os.path.exists(OUTPUT_PATH):
        raise RuntimeError(f"Refusing to overwrite result: {OUTPUT_PATH}")
    result = run()
    with open(OUTPUT_PATH, "x", encoding="utf-8") as handle:
        json.dump(result, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    logging.info("%s", json.dumps(result["summary"], ensure_ascii=False, sort_keys=True))
    return 0 if result["result"] == "PASS / CURRENT" else 1


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    raise SystemExit(main())
