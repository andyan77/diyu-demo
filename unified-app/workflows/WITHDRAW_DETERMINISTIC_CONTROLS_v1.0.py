#!/usr/bin/env python3
"""Zero-model controls for the UAPP upload-to-M2 material seam."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from types import ModuleType
from typing import Any

HERE = Path(__file__).resolve().parent
UAPP_ROOT = HERE.parent
OUTPUT = (
    UAPP_ROOT
    / "evidence"
    / "stages"
    / "s5_final_convergence_v1_0"
    / "WITHDRAW_DETERMINISTIC_CONTROLS_v1.0.json"
)
EXPECTED_UAPP_MD5 = "aa32b6385de0024d270ec9f85bd78179"
EXPECTED_M2_SCHEMA_MD5 = "25192c11562827efedfc3b2c22c3b4fd"


def load_module(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


NODES = load_module(
    "withdraw_controls_nodes", HERE / "WITHDRAW_MATERIAL_REGISTRATION_NODES_v1.0.py"
)
BUILD = load_module(
    "withdraw_controls_build", HERE / "WITHDRAW_MATERIAL_REGISTRATION_BUILD_v1.0.py"
)
RUN = load_module("withdraw_controls_run", HERE / "UAPP_S5_RUN_v1.0.py")


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def check(
    checks: list[dict[str, Any]],
    check_id: str,
    passed: bool,
    evidence: Any,
) -> None:
    checks.append({"id": check_id, "result": "PASS" if passed else "FAIL", "evidence": evidence})
    if not passed:
        raise RuntimeError(f"{check_id}: {evidence}")


def fixture_file(upload_id: str = "upload-001", file_name: str = "brand-facts.md") -> dict[str, str]:
    return {"related_id": upload_id, "filename": file_name}


def prepared(
    *,
    files: Any | None = None,
    text: str = "fixture body",
    workspace: str = "workspace-test",
    account: str = "account-test",
    task: str = "task-test",
    actor: str = "founder-test",
    previous: str = "{}",
) -> dict[str, str]:
    return NODES.prepare_material(
        files if files is not None else [fixture_file()],
        text,
        workspace,
        account,
        task,
        actor,
        previous,
    )


def response_for(register: dict[str, str]) -> dict[str, Any]:
    request = json.loads(register["request_body"])
    return {
        "id": "material-test",
        "workspace_id": "workspace-test",
        "analysis_authorized": request["analysis_authorized"],
        "generation_authorized": request["generation_authorized"],
        "publish_authorized": request["publish_authorized"],
        "scope_ref": request["scope_ref"],
        "content_ref": request["content_ref"],
    }


def graph_controls(checks: list[dict[str, Any]]) -> None:
    published = BUILD.BASE.BASE.published_graph()
    candidate, added_nodes, added_edges = BUILD.patch_uapp(published)
    before_nodes = {item["id"]: item for item in published["nodes"]}
    after_nodes = {item["id"]: item for item in candidate["nodes"]}
    unchanged = all(
        canonical(before_nodes[node_id]) == canonical(after_nodes[node_id])
        for node_id in before_nodes
    )
    check(
        checks,
        "WDC-01_existing_nodes_byte_equivalent",
        unchanged and len(before_nodes) == 56,
        {"existing_nodes": len(before_nodes), "added_nodes": added_nodes},
    )
    edge_ids = {item["id"] for item in candidate["edges"]}
    check(
        checks,
        "WDC-02_no_file_path_preserves_downstream",
        "uapp_ctx-source-uapp_m3_gate" not in edge_ids
        and "uapp_ctx-source-uapp_material_prepare" in edge_ids
        and "uapp_material_gate-false-uapp_m3_gate" in edge_ids,
        {"added_edges": added_edges},
    )
    values = BUILD.published_conversation_variables()
    candidate_values = BUILD.patch_conversation_variables(values)
    check(
        checks,
        "WDC-03_single_bounded_binding_variable",
        set(candidate_values) - set(values) == {"uapp_material_binding"}
        and candidate_values["uapp_material_binding"]["value_type"] == "string",
        {"added": sorted(set(candidate_values) - set(values))},
    )


def prepare_controls(checks: list[dict[str, Any]]) -> dict[str, str]:
    no_file = prepared(files=[], text="")
    check(checks, "WDC-04_no_file_no_registration", no_file["decision"] == "NONE", no_file)

    register = prepared()
    request = json.loads(register["request_body"])
    scope = request["scope_ref"]
    check(
        checks,
        "WDC-05_one_file_one_scoped_registration",
        register["decision"] == "REGISTER"
        and scope["task_id"] == "task-test"
        and scope["account_id"] == "account-test"
        and scope["is_test"] is True
        and scope["is_simulated"] is True,
        {"decision": register["decision"], "scope_ref": scope},
    )
    check(
        checks,
        "WDC-06_upload_identity_and_hash_recomputable",
        scope["dify_upload_id"] == "upload-001"
        and scope["file_name"] == "brand-facts.md"
        and scope["extracted_text_sha256"] == register["file_hash"]
        and register["file_hash"]
        == __import__("hashlib").sha256("fixture body".encode("utf-8")).hexdigest(),
        scope,
    )
    check(
        checks,
        "WDC-07_upload_never_grants_publish",
        request["analysis_authorized"] is True
        and request["generation_authorized"] is True
        and request["publish_authorized"] is False,
        {
            "analysis_authorized": request["analysis_authorized"],
            "generation_authorized": request["generation_authorized"],
            "publish_authorized": request["publish_authorized"],
        },
    )

    incomplete_controls = {
        "missing_text": prepared(text="")["decision"],
        "missing_file": prepared(files=[])["decision"],
        "two_files": prepared(files=[fixture_file(), fixture_file("upload-002")])["decision"],
        "missing_task": prepared(task="")["decision"],
        "missing_account": prepared(account="")["decision"],
        "missing_actor": prepared(actor="")["decision"],
        "missing_upload_id": prepared(files=[{"filename": "brand-facts.md"}])["decision"],
        "missing_file_name": prepared(files=[{"related_id": "upload-001"}])["decision"],
    }
    check(
        checks,
        "WDC-08_incomplete_or_ambiguous_upload_fails_closed",
        all(value == "INVALID" for value in incomplete_controls.values()),
        incomplete_controls,
    )
    return register


def parser_controls(checks: list[dict[str, Any]], register: dict[str, str]) -> str:
    response = response_for(register)
    parsed = NODES.parse_registration(response, 200, register["binding_seed"])
    check(
        checks,
        "WDC-09_exact_response_confirms_binding",
        parsed["ok"] == "true" and parsed["material_id"] == "material-test",
        parsed,
    )
    mutations: dict[str, tuple[Any, Any]] = {
        "http_status": (response, 500),
        "missing_id": ({**response, "id": ""}, 200),
        "workspace": ({**response, "workspace_id": "other"}, 200),
        "task": ({**response, "scope_ref": {**response["scope_ref"], "task_id": "other"}}, 200),
        "account": (
            {**response, "scope_ref": {**response["scope_ref"], "account_id": "other"}},
            200,
        ),
        "idempotency": (
            {**response, "scope_ref": {**response["scope_ref"], "idempotency_key": "other"}},
            200,
        ),
        "hash": (
            {
                **response,
                "scope_ref": {**response["scope_ref"], "extracted_text_sha256": "other"},
            },
            200,
        ),
        "upload_id": (
            {**response, "scope_ref": {**response["scope_ref"], "dify_upload_id": "other"}},
            200,
        ),
        "is_test": (
            {**response, "scope_ref": {**response["scope_ref"], "is_test": False}},
            200,
        ),
        "is_simulated": (
            {**response, "scope_ref": {**response["scope_ref"], "is_simulated": False}},
            200,
        ),
        "publish_authorized": ({**response, "publish_authorized": True}, 200),
    }
    results = {
        name: NODES.parse_registration(body, status, register["binding_seed"])["ok"]
        for name, (body, status) in mutations.items()
    }
    check(
        checks,
        "WDC-10_single_variable_negative_controls_discriminate",
        all(value == "false" for value in results.values()),
        results,
    )
    return parsed["binding_json"]


def idempotency_controls(checks: list[dict[str, Any]], binding_json: str) -> None:
    reuse = prepared(previous=binding_json)
    changed_task = prepared(task="task-other", previous=binding_json)
    changed_upload = prepared(files=[fixture_file("upload-other")], previous=binding_json)
    check(
        checks,
        "WDC-11_same_file_task_idempotency_reuses_material",
        reuse["decision"] == "REUSE",
        reuse,
    )
    check(
        checks,
        "WDC-12_task_or_upload_change_does_not_reuse",
        changed_task["decision"] == "REGISTER" and changed_upload["decision"] == "REGISTER",
        {"changed_task": changed_task["decision"], "changed_upload": changed_upload["decision"]},
    )


def m2_controls(checks: list[dict[str, Any]]) -> dict[str, Any]:
    current = RUN.global_m2_guard()
    tests_path = UAPP_ROOT.parent / "business-persistence" / "tests" / "test_material_withdrawal.py"
    service_path = UAPP_ROOT.parent / "business-persistence" / "app" / "services" / "versioning.py"
    tests_text = tests_path.read_text(encoding="utf-8")
    service_text = service_path.read_text(encoding="utf-8")
    required_tests = (
        "test_withdrawal_invalidates_only_unpublished_dependents",
        "test_withdrawal_is_idempotent",
        "test_withdrawn_material_content_not_servable",
        "test_unaffected_artifact_not_touched_by_unrelated_withdrawal",
        "test_withdrawn_material_cannot_be_attached_to_a_new_version",
    )
    check(
        checks,
        "WDC-13_withdrawal_contract_regression",
        all(name in tests_text for name in required_tests)
        and "already_withdrawn" in service_text
        and "published_ids" in service_text
        and "invalidated_version_ids" in service_text,
        {
            "accepted_m2_evidence": "business-persistence/M2_ACCEPTANCE_EVIDENCE.md#M2-AC-11",
            "required_tests_present": list(required_tests),
            "execution_note": "M2 is protected; accepted behavior is inherited read-only.",
        },
    )
    check(
        checks,
        "WDC-14_schema_and_non_test_data_unchanged",
        current["schema_md5"] == EXPECTED_M2_SCHEMA_MD5
        and current["non_test_publish_instances"] == 1568
        and current["non_test_feedback_records"] == 117,
        {"activation_baseline": {"publish": 1568, "feedback": 117}, "current": current},
    )
    return {"activation_baseline": {"publish": 1568, "feedback": 117}, "current": current}


def main() -> int:
    if OUTPUT.exists():
        raise FileExistsError(OUTPUT)
    checks: list[dict[str, Any]] = []
    check(
        checks,
        "WDC-00_published_predecessor_identity",
        BUILD.BASE.BASE.graph_md5() == EXPECTED_UAPP_MD5,
        {"expected": EXPECTED_UAPP_MD5, "actual": BUILD.BASE.BASE.graph_md5()},
    )
    graph_controls(checks)
    register = prepare_controls(checks)
    binding_json = parser_controls(checks, register)
    idempotency_controls(checks, binding_json)
    m2_state = m2_controls(checks)
    report = {
        "document": {
            "id": "WITHDRAW_DETERMINISTIC_CONTROLS_v1.0",
            "task_id": "DIYU-V1-UNIFIED-DIFY-APPLICATION-001",
        },
        "model_calls": 0,
        "positive_and_negative_controls": len(checks),
        "all_pass": all(item["result"] == "PASS" for item in checks),
        "m2_protected_state": m2_state,
        "checks": checks,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: report[key] for key in ("model_calls", "positive_and_negative_controls", "all_pass")}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
