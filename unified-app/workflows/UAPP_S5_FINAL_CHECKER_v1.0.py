#!/usr/bin/env python3
"""Adjudicate the eleven frozen S5 final-convergence turns."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
from types import ModuleType
from typing import Any

HERE = os.path.dirname(os.path.abspath(__file__))
UAPP_ROOT = os.path.abspath(os.path.join(HERE, ".."))
SCENARIOS = os.path.join(UAPP_ROOT, "stages", "UAPP_S5_FROZEN_SCENARIOS_v1.2.json")
GATE = os.path.join(UAPP_ROOT, "stages", "UAPP_S5_GATE_v2.0.json")
EVIDENCE = os.path.join(
    UAPP_ROOT, "evidence", "stages", "s5_final_convergence_v1_0", "formal"
)


def load_module(name: str, path: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


BASE = load_module(
    "uapp_s5_final_checker_base", os.path.join(HERE, "UAPP_S5_VERIFY_v1.2.py")
)
BASE.SCENARIOS = SCENARIOS
BASE.GATE = GATE
BASE.EVIDENCE = EVIDENCE


def safe_key(key: str) -> str:
    return key.replace(":", "_").replace("/", "_")


def raw_path(key: str) -> str:
    return os.path.join(EVIDENCE, "raw", f"{safe_key(key)}.json")


def check_path(key: str) -> str:
    return os.path.join(EVIDENCE, "checks", f"{safe_key(key)}.json")


BASE.raw_path = raw_path
BASE.check_path = check_path
BASE.BASE.raw_path = raw_path
BASE.BASE.check_path = check_path
_base_evaluate = BASE.evaluate_turn


def as_object(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError:
            return {}
        return parsed if isinstance(parsed, dict) else {}
    return {}


def add_check(
    result: dict[str, Any], identifier: str, condition: bool, detail: Any
) -> None:
    result["checks"].append(
        {"id": identifier, "result": "PASS" if condition else "FAIL", "detail": detail}
    )


def remove_checks(result: dict[str, Any], identifiers: set[str]) -> None:
    result["checks"] = [
        item for item in result["checks"] if item["id"] not in identifiers
    ]


def predecessor(key: str) -> dict[str, Any]:
    path = raw_path(key)
    return BASE.load_json(path) if os.path.exists(path) else {}


def current_fields(raw: dict[str, Any]) -> dict[str, Any]:
    output = BASE.BASE.node_output(raw, "uapp_fields")
    state = as_object(output.get("pending_state_json"))
    fields = state.get("fields")
    return fields if isinstance(fields, dict) else {}


def field_value(fields: dict[str, Any], field_id: str) -> str:
    value = fields.get(field_id)
    if isinstance(value, dict):
        return str(value.get("value") or value.get("value_text") or "")
    return str(value or "")


def exact_material(
    raw: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    materials = BASE.rows(raw, "materials")
    material = materials[0] if len(materials) == 1 else {}
    scope = as_object(material.get("scope_ref"))
    variables = raw.get("conversation_variables_after") or {}
    binding = as_object(variables.get("uapp_material_binding"))
    return material, scope, binding


def evaluate_turn(
    raw: dict[str, Any],
    turn: dict[str, Any],
    gate: dict[str, Any],
    predecessors: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    result = _base_evaluate(raw, turn, gate, predecessors)
    key = turn["key"]
    answer = str(raw.get("answer") or "")

    if key == "UAPP-WITHDRAW-01:W0":
        remove_checks(result, {"WITHDRAW-01"})
        material, scope, binding = exact_material(raw)
        upload = raw.get("upload") or {}
        upload_response = upload.get("response") or {}
        upload_id = str(upload_response.get("id") or "")
        fixture_hash = str(upload.get("sha256") or "")
        prepare = BASE.BASE.node_output(raw, "uapp_material_prepare")
        parse = BASE.BASE.node_output(raw, "uapp_material_parse")
        m1_text = str(
            BASE.BASE.node_output(raw, "m1_join").get("material_text") or ""
        ).strip()
        extracted_hash = (
            hashlib.sha256(m1_text.encode("utf-8")).hexdigest() if m1_text else ""
        )
        variables = raw.get("conversation_variables_after") or {}
        task_rows = BASE.rows(raw, "tasks")
        workspace_rows = raw.get("m2_after", {}).get("workspace", [])
        workspace_id = (
            str(workspace_rows[0].get("id") or "") if len(workspace_rows) == 1 else ""
        )
        task_id = str(task_rows[0].get("id") or "") if len(task_rows) == 1 else ""
        identity = {
            "upload_http": upload.get("http_status"),
            "upload_id": upload_id,
            "fixture_sha256": fixture_hash,
            "extracted_sha256": extracted_hash,
            "material_id": material.get("id"),
            "workspace_id": workspace_id,
            "task_id": task_id,
            "scope": scope,
            "binding": binding,
            "prepare": prepare,
            "parse": parse,
        }
        add_check(
            result,
            "WITHDRAW-W0-01",
            upload.get("http_status") in (200, 201)
            and bool(upload_id)
            and len(BASE.rows(raw, "materials")) == 1
            and bool(material),
            identity,
        )
        add_check(
            result,
            "WITHDRAW-W0-02",
            BASE.BASE.node_executed(raw, "uapp_material_prepare")
            and BASE.BASE.node_executed(raw, "uapp_material_parse")
            and prepare.get("decision") == "REGISTER"
            and str(parse.get("ok")).lower() == "true",
            identity,
        )
        add_check(
            result,
            "WITHDRAW-W0-03",
            bool(extracted_hash)
            and scope.get("extracted_text_sha256") == extracted_hash
            and binding.get("extracted_text_sha256") == extracted_hash
            and prepare.get("file_hash") == extracted_hash,
            identity,
        )
        add_check(
            result,
            "WITHDRAW-W0-04",
            scope.get("dify_upload_id") == upload_id
            and binding.get("dify_upload_id") == upload_id
            and prepare.get("upload_id") == upload_id
            and scope.get("file_name") == prepare.get("file_name"),
            identity,
        )
        add_check(
            result,
            "WITHDRAW-W0-05",
            material.get("workspace_id") == workspace_id
            and scope.get("task_id") == task_id
            and binding.get("task_id") == task_id
            and binding.get("workspace_id") == workspace_id
            and scope.get("is_test") is True
            and scope.get("is_simulated") is True,
            identity,
        )
        add_check(
            result,
            "WITHDRAW-W0-06",
            material.get("publish_authorized") is False
            and binding.get("publish_authorized") is False
            and variables.get("uapp_last_material") == material.get("id")
            and binding.get("material_id") == material.get("id")
            and not BASE.rows(raw, "publish_instances"),
            identity,
        )

    elif key == "UAPP-WITHDRAW-01:W1":
        remove_checks(result, {"WITHDRAW-02", "WITHDRAW-03"})
        before = (predecessors or {}).get("UAPP-WITHDRAW-01:W0") or predecessor(
            "UAPP-WITHDRAW-01:W0"
        )
        before_material, _, _ = exact_material(before) if before else ({}, {}, {})
        materials = BASE.rows(raw, "materials")
        material = materials[0] if len(materials) == 1 else {}
        capability_runs = {
            name: BASE.app_run_count(raw, name) for name in BASE.BASE.CAPABILITIES
        }
        same_conversation = raw.get("conversation_id") == before.get("conversation_id")
        same_material = bool(before_material) and material.get(
            "id"
        ) == before_material.get("id")
        add_check(
            result,
            "WITHDRAW-W1-01",
            same_conversation
            and len(materials) == 1
            and same_material
            and bool(material.get("withdrawn_at")),
            {
                "same_conversation": same_conversation,
                "before": before_material,
                "after": material,
            },
        )
        add_check(
            result,
            "WITHDRAW-W1-02",
            material.get("content_ref") == before_material.get("content_ref")
            and material.get("workspace_id") == before_material.get("workspace_id")
            and material.get("publish_authorized") is False,
            {"before": before_material, "after": material},
        )
        add_check(
            result,
            "WITHDRAW-W1-03",
            all(value == 0 for value in capability_runs.values())
            and not BASE.rows(raw, "publish_instances")
            and not any(
                token in answer for token in ("物理删除", "历史发布失效", "已经下架")
            ),
            {"capability_runs": capability_runs, "answer": answer},
        )

    elif turn.get("equivalence", "").startswith("positive"):
        fields = current_fields(raw)
        subject = field_value(fields, "expression.subject_and_boundary")
        audience = field_value(fields, "audience.expected_change")
        gaps = str(BASE.BASE.node_output(raw, "uapp_fields").get("gaps_text") or "")
        add_check(
            result,
            "EQUIV-P3",
            "品牌搭配师" in subject
            and ("三天" in audience or "外套" in audience)
            and gaps in ("", "无", "NONE"),
            {"subject": subject, "expected_change": audience, "gaps": gaps},
        )

    elif turn.get("equivalence", "").startswith("negative"):
        remove_checks(result, {"EQUIV-N1", "EQUIV-N2"})
        capability_runs = {
            name: BASE.app_run_count(raw, name) for name in BASE.BASE.CAPABILITIES
        }
        no_new_artifact = not BASE.rows(raw, "artifacts") and not BASE.rows(
            raw, "content_versions"
        )
        asks_expected_change = any(
            word in answer for word in ("希望", "看完", "明白", "改变", "期望")
        )
        repeats_subject = any(
            word in answer for word in ("谁来讲", "谁出镜", "表达主体", "由谁")
        )
        add_check(
            result,
            "EQUIV-N1",
            all(value == 0 for value in capability_runs.values()) and no_new_artifact,
            {"capability_runs": capability_runs, "no_new_artifact": no_new_artifact},
        )
        add_check(
            result,
            "EQUIV-N2",
            asks_expected_change and not repeats_subject,
            {
                "answer": answer,
                "asks_expected_change": asks_expected_change,
                "repeats_subject": repeats_subject,
            },
        )

    elif key == "UAPP-FULL-01:T1":
        fields = current_fields(raw)
        subject = field_value(fields, "expression.subject_and_boundary")
        add_check(
            result, "FULL-T1-SUBJECT", "品牌搭配师" in subject, {"subject": subject}
        )

    elif key == "UAPP-FULL-01:T2":
        publishes = BASE.rows(raw, "publish_instances")
        versions = {str(row.get("id")) for row in BASE.rows(raw, "content_versions")}
        valid = (
            len(publishes) == 1
            and publishes[0].get("is_test") is True
            and publishes[0].get("is_simulated") is True
            and str(publishes[0].get("content_version_id")) in versions
        )
        add_check(
            result,
            "FULL-T2-BINDING",
            valid,
            {"publishes": publishes, "version_ids": sorted(versions)},
        )

    elif key == "UAPP-FULL-01:T3":
        before = (predecessors or {}).get("UAPP-FULL-01:T2") or predecessor(
            "UAPP-FULL-01:T2"
        )
        before_publishes = BASE.rows(before, "publish_instances") if before else []
        feedback = BASE.rows(raw, "feedback_records")
        valid = (
            len(before_publishes) == 1
            and len(feedback) == 1
            and feedback[0].get("publish_instance_id") == before_publishes[0].get("id")
            and feedback[0].get("is_test") is True
            and feedback[0].get("is_simulated") is True
        )
        add_check(
            result,
            "FULL-T3-BINDING",
            valid,
            {"publish": before_publishes, "feedback": feedback},
        )

    elif key == "UAPP-FULL-01:T4":
        before = (predecessors or {}).get("UAPP-FULL-01:T3") or predecessor(
            "UAPP-FULL-01:T3"
        )
        add_check(
            result,
            "FULL-T4-CONTINUITY",
            bool(before)
            and raw.get("conversation_id") == before.get("conversation_id")
            and len(BASE.rows(raw, "cycles")) >= 2
            and len(BASE.rows(raw, "feedback_records")) == 1,
            {
                "cycles": BASE.rows(raw, "cycles"),
                "feedback": BASE.rows(raw, "feedback_records"),
            },
        )

    elif key == "UAPP-RECOVERY-01:R1":
        before = (predecessors or {}).get("UAPP-FULL-01:T4") or predecessor(
            "UAPP-FULL-01:T4"
        )
        before_feedback = BASE.rows(before, "feedback_records") if before else []
        after_feedback = BASE.rows(raw, "feedback_records")
        add_check(
            result,
            "RECOVERY-IDEMPOTENCY",
            bool(before)
            and raw.get("conversation_id") == before.get("conversation_id")
            and len(before_feedback) == 1
            and len(after_feedback) == 1
            and before_feedback[0].get("id") == after_feedback[0].get("id"),
            {"before_feedback": before_feedback, "after_feedback": after_feedback},
        )

    result["verdict"] = (
        "PASS"
        if result["checks"]
        and all(item["result"] == "PASS" for item in result["checks"])
        else "FAIL"
    )
    return result


BASE.evaluate_turn = evaluate_turn
BASE.BASE.evaluate_turn = evaluate_turn
load_json = BASE.load_json
sha256_file = BASE.sha256_file
verify_turn = BASE.verify_turn
exclusive_write = BASE.exclusive_write
rows = BASE.rows
node_output = BASE.BASE.node_output
node_executed = BASE.BASE.node_executed
app_run_count = BASE.app_run_count
llm_attempts = BASE.llm_attempts
CAPABILITIES = BASE.BASE.CAPABILITIES


if __name__ == "__main__":
    raise SystemExit(BASE.BASE.main())
