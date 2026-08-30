#!/usr/bin/env python3
"""Adjudicate UAAB successor T2/T3 against the pre-frozen v1.2 Gate.

This verifier is deterministic, starts no workflows, and never mutates Dify.
The T3 implementation and its D1-b/D1-c probes are committed before T3 runs.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
from typing import Any

HERE = os.path.dirname(os.path.abspath(__file__))
UAPP_ROOT = os.path.abspath(os.path.join(HERE, ".."))
EVIDENCE_DIR = os.path.join(UAPP_ROOT, "evidence", "stages", "uapp_artifact_binding")
GATE = os.path.join(UAPP_ROOT, "stages", "UAAB_GATE_v1.2.json")
INPUTS = os.path.join(UAPP_ROOT, "stages", "UAAB_SUCCESSOR_INPUTS_v1.2.json")

GATE_SHA256 = "dbe4c023256e378d93827094b5c762f7c1b67b1c7528fff92fbbb84b219ea622"
INPUTS_SHA256 = "f669c5163533807e47c827f9c08792f014ce4743e0df35ef23adb9b9b3ac29ca"
TASK_KEY = "ec666086-dce5-4e79-ba0f-6ac88f04a0bb"
T1_FP = "3d7342e36d939c31"
T1_BFP = "4af627e012e74e3a"
T1_BODY_SHA256 = "65f58acb09de20b77ff1deb669e2210e5f128a4b06fbaab14fbf31cf9955b938"
PLACEHOLDER = "这一步没有产出可以交给你的内容"

PROFESSIONAL_APPS = (
    "MATRIX",
    "CAMPAIGN",
    "CONTENT_BRIEF",
    "CREATIVE_SCRIPT",
    "PRODUCTION_DIRECTOR",
    "PUBLISHING_PACKAGING",
)
HISTORY_PROBES = ("一直在用", "常用", "长期以来", "十年", "历来", "向来", "一贯", "多年来", "一直以来", "从来都")
HEDGE_PROBES = ("合理推断", "基于职责", "据说", "印象中")


def sha256_file(path: str) -> str:
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def psql(sql: str) -> str:
    completed = subprocess.run(
        ["docker", "exec", "-i", "docker-db_postgres-1", "psql", "-U", "postgres", "-d", "dify", "-tA", "-c", sql],
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(f"psql failed: {(completed.stderr or '')[:300]}")
    return completed.stdout.strip()


def decoded(value: Any) -> Any:
    for _ in range(3):
        if not isinstance(value, str):
            return value
        try:
            value = json.loads(value)
        except json.JSONDecodeError:
            return value
    return value


def node(run: dict[str, Any], node_id: str) -> dict[str, Any]:
    return next(item for item in run["node_detail"] if item["node_id"] == node_id)


def node_outputs(run: dict[str, Any], node_id: str) -> dict[str, Any]:
    output = decoded(node(run, node_id)["outputs"])
    return output if isinstance(output, dict) else {}


def extract_json_slot(text: str, slot: str) -> str | None:
    match = re.search(r'^"%s": ("(?:[^"\\]|\\.)*")$' % re.escape(slot), text or "", re.MULTILINE)
    return json.loads(match.group(1)) if match else None


def qsent(text: str) -> list[str]:
    result: list[str] = []
    for line in (text or "").split("\n"):
        for segment in re.split(r"(?<=[。！\n])", line):
            sentence = segment.strip()
            if sentence.endswith(("？", "?")):
                result.append(sentence)
    return result


def raw(turn_id: str) -> dict[str, Any]:
    path = os.path.join(EVIDENCE_DIR, f"UAAB_SUCCESSOR_RAW_{turn_id}_v1.2.json")
    if not os.path.exists(path):
        raise RuntimeError(f"raw evidence is absent: {path}")
    return json.load(open(path, encoding="utf-8"))


def one_run(document: dict[str, Any], app: str) -> dict[str, Any]:
    runs = document["app_runs_in_window"].get(app) or []
    if len(runs) != 1:
        raise RuntimeError(f"expected one {app} run, observed {len(runs)}")
    return runs[0]


def professional_counts(document: dict[str, Any]) -> dict[str, int]:
    return {app: len(document["app_runs_in_window"].get(app) or []) for app in PROFESSIONAL_APPS}


def llm_observations(document: dict[str, Any]) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for app, runs in document["app_runs_in_window"].items():
        for workflow_run in runs:
            for execution in workflow_run["node_detail"]:
                if execution["type"] == "llm":
                    result.append(
                        {
                            "app": app,
                            "workflow_run_id": workflow_run["id"],
                            "node_id": execution["node_id"],
                            "status": execution["status"],
                            "error": execution.get("error"),
                        }
                    )
    return result


def store_and_ledger(document: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    variables = document["conversation_variables_after"]
    return json.loads(variables["uapp_last_artifact"]), json.loads(variables["uapp_task_fields"])


def add(checks: list[dict[str, Any]], check_id: str, ok: bool, observed: dict[str, Any]) -> None:
    checks.append({"id": check_id, "result": "PASS" if ok else "FAIL", "observed": observed})


def substantive_artifact(outputs: dict[str, Any]) -> tuple[bool, str]:
    artifact = outputs.get("artifact") or ""
    ok = (
        isinstance(artifact, str)
        and len(artifact.strip()) > 80
        and not artifact.startswith(PLACEHOLDER)
        and outputs.get("artifact_status") == "OK"
        and outputs.get("delivery_outcome") == "DELIVERED"
    )
    return ok, artifact


def verify_t2(document: dict[str, Any]) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    top = one_run(document, "UAPP")
    production = one_run(document, "PRODUCTION_DIRECTOR")
    pick = node_outputs(top, "uapp_pick_upstream")
    fields = node_outputs(top, "uapp_fields")
    persist = node_outputs(top, "uapp_persist")
    production_inputs = decoded(production["inputs"])
    production_outputs = decoded(production["outputs"])
    selected_body = pick.get("upstream_delivery") or ""
    fields_body = extract_json_slot(fields.get("capability_call") or "", "script_or_equivalent_beats")
    production_body = extract_json_slot(production_inputs.get("capability_call") or "", "script_or_equivalent_beats")
    artifact_ok, artifact = substantive_artifact(production_outputs)
    store, ledger = store_and_ledger(document)
    stored_cs = next((item for item in store["items"] if item.get("fp") == T1_FP), None)
    stored_pd = next((item for item in store["items"] if item.get("cap") == "PRODUCTION_DIRECTOR" and item.get("body") == artifact), None)
    ledger_cs = next((item for item in ledger["artifacts"] if item.get("fp") == T1_FP), None)
    ledger_pd = next((item for item in ledger["artifacts"] if item.get("fp") == (stored_pd or {}).get("fp")), None)
    counts = professional_counts(document)
    llm = llm_observations(document)

    add(
        checks,
        "T2-01",
        counts == {
            "MATRIX": 0,
            "CAMPAIGN": 0,
            "CONTENT_BRIEF": 0,
            "CREATIVE_SCRIPT": 0,
            "PRODUCTION_DIRECTOR": 1,
            "PUBLISHING_PACKAGING": 0,
        }
        and production["status"] == "succeeded",
        {"professional_runs": counts, "production_run_id": production["id"]},
    )
    add(
        checks,
        "T2-02",
        pick.get("selection_status") == "SELECTED"
        and pick.get("selected_fp") == T1_FP
        and pick.get("selected_bfp") == T1_BFP
        and pick.get("selected_capability") == "CREATIVE_SCRIPT",
        {key: pick.get(key) for key in ("selection_status", "selected_fp", "selected_bfp", "selected_capability")},
    )
    add(
        checks,
        "T2-03",
        len(selected_body) == 3497 and sha256_text(selected_body) == T1_BODY_SHA256,
        {"selector_length": len(selected_body), "selector_sha256": sha256_text(selected_body)},
    )
    add(
        checks,
        "T2-04",
        fields.get("artifact_binding_status") == "BOUND" and '"identity_source": "SELECTOR_DIRECT"' in fields.get("upstream_binding_json", ""),
        {"artifact_binding_status": fields.get("artifact_binding_status"), "binding": decoded(fields.get("upstream_binding_json"))},
    )
    add(
        checks,
        "T2-05",
        fields_body == selected_body and production_body == selected_body,
        {
            "fields_decoded_sha256": sha256_text(fields_body or ""),
            "production_input_decoded_sha256": sha256_text(production_body or ""),
            "expected_sha256": T1_BODY_SHA256,
        },
    )
    add(
        checks,
        "T2-06",
        artifact_ok,
        {"artifact_length": len(artifact), "artifact_sha256": sha256_text(artifact), "artifact_status": production_outputs.get("artifact_status")},
    )
    add(
        checks,
        "T2-07",
        stored_cs is not None
        and stored_pd is not None
        and stored_cs is not stored_pd
        and sha256_text(stored_cs["body"]) == T1_BODY_SHA256
        and sha256_text(stored_pd["body"]) == sha256_text(artifact)
        and stored_cs.get("task_key") == stored_pd.get("task_key") == TASK_KEY,
        {
            "store_item_count": len(store["items"]),
            "CS": {"fp": (stored_cs or {}).get("fp"), "sha256": sha256_text((stored_cs or {}).get("body", ""))},
            "PD": {"fp": (stored_pd or {}).get("fp"), "sha256": sha256_text((stored_pd or {}).get("body", ""))},
            "persist_action": persist.get("persist_action"),
        },
    )
    latest_real = max(
        (item for item in store["items"] if item.get("body") and isinstance(item.get("turn"), int)),
        key=lambda item: item["turn"],
    )
    add(
        checks,
        "T2-08",
        document["conversation_variables_after"].get("uapp_last_capability") == latest_real.get("cap") == "PRODUCTION_DIRECTOR"
        and (ledger_cs or {}).get("accepted") is True
        and (ledger_cs or {}).get("stale") is False
        and (ledger_pd or {}).get("accepted") is False
        and (ledger_pd or {}).get("stale") is False,
        {
            "uapp_last_capability": document["conversation_variables_after"].get("uapp_last_capability"),
            "latest_real_artifact_capability": latest_real.get("cap"),
            "CS_accepted_stale": [(ledger_cs or {}).get("accepted"), (ledger_cs or {}).get("stale")],
            "PD_accepted_stale": [(ledger_pd or {}).get("accepted"), (ledger_pd or {}).get("stale")],
        },
    )
    add(
        checks,
        "T2-COST",
        len(llm) == 6
        and all(item["status"] == "succeeded" and not item["error"] for item in llm)
        and all(len(runs) <= 1 for runs in document["app_runs_in_window"].values()),
        {"llm_node_attempts": llm, "platform_internal_replays": 0, "runner_attempts": document["request_attempts_by_runner"]},
    )
    return {
        "turn": "T2",
        "workflow_run_id": document["workflow_run_id"],
        "production_run_id": production["id"],
        "artifact": {"length": len(artifact), "sha256": sha256_text(artifact), "fp": (stored_pd or {}).get("fp"), "bfp": (stored_pd or {}).get("bfp")},
        "checks": checks,
        "result": "PASS" if all(item["result"] == "PASS" for item in checks) else "FAIL",
    }


def verify_t3(document: dict[str, Any], t2_result: dict[str, Any]) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    top = one_run(document, "UAPP")
    seam = one_run(document, "SEAM")
    packaging = one_run(document, "PUBLISHING_PACKAGING")
    pick = node_outputs(top, "uapp_pick_upstream")
    fields = node_outputs(top, "uapp_fields")
    packaging_inputs = decoded(packaging["inputs"])
    packaging_outputs = decoded(packaging["outputs"])
    selected_body = pick.get("upstream_delivery") or ""
    fields_body = extract_json_slot(fields.get("capability_call") or "", "content_body_or_beats")
    packaging_body = extract_json_slot(packaging_inputs.get("capability_call") or "", "content_body_or_beats")
    artifact_ok, artifact = substantive_artifact(packaging_outputs)
    user_delivery = packaging_outputs.get("user_delivery") or ""
    store, ledger = store_and_ledger(document)
    expected_pd_sha = t2_result["artifact"]["sha256"]
    expected_pd_fp = t2_result["artifact"]["fp"]
    stored_cs = next((item for item in store["items"] if item.get("fp") == T1_FP), None)
    stored_pd = next((item for item in store["items"] if item.get("fp") == expected_pd_fp), None)
    stored_pp = next((item for item in store["items"] if item.get("cap") == "PUBLISHING_PACKAGING" and item.get("body") == artifact), None)
    ledger_pd = next((item for item in ledger["artifacts"] if item.get("fp") == expected_pd_fp), None)
    ledger_pp = next((item for item in ledger["artifacts"] if item.get("fp") == (stored_pp or {}).get("fp")), None)
    counts = professional_counts(document)
    llm = llm_observations(document)
    history_hits = {probe: artifact.count(probe) + user_delivery.count(probe) for probe in HISTORY_PROBES if probe in artifact or probe in user_delivery}
    hedge_hits = {probe: artifact.count(probe) + user_delivery.count(probe) for probe in HEDGE_PROBES if probe in artifact or probe in user_delivery}
    questions = {"artifact": qsent(artifact), "user_delivery": qsent(user_delivery)}
    uapp_workflow_md5 = psql(f"select md5(graph) from workflows where id='{top['workflow_id']}';")
    seam_workflow_md5 = psql(f"select md5(graph) from workflows where id='{seam['workflow_id']}';")
    pp_workflow_md5 = psql(f"select md5(graph) from workflows where id='{packaging['workflow_id']}';")

    add(
        checks,
        "T3-01",
        counts == {
            "MATRIX": 0,
            "CAMPAIGN": 0,
            "CONTENT_BRIEF": 0,
            "CREATIVE_SCRIPT": 0,
            "PRODUCTION_DIRECTOR": 0,
            "PUBLISHING_PACKAGING": 1,
        }
        and packaging["status"] == "succeeded",
        {"professional_runs": counts, "packaging_run_id": packaging["id"]},
    )
    add(
        checks,
        "T3-02",
        pick.get("selection_status") == "SELECTED"
        and pick.get("selected_fp") == expected_pd_fp
        and pick.get("selected_capability") == "PRODUCTION_DIRECTOR",
        {key: pick.get(key) for key in ("selection_status", "selected_fp", "selected_bfp", "selected_capability")},
    )
    add(
        checks,
        "T3-03",
        sha256_text(selected_body) == expected_pd_sha and fields_body == selected_body and packaging_body == selected_body,
        {
            "selector_sha256": sha256_text(selected_body),
            "fields_decoded_sha256": sha256_text(fields_body or ""),
            "packaging_input_decoded_sha256": sha256_text(packaging_body or ""),
            "expected_PD_sha256": expected_pd_sha,
        },
    )
    add(
        checks,
        "T3-04",
        fields.get("artifact_binding_status") == "BOUND"
        and pick.get("selected_capability") == "PRODUCTION_DIRECTOR"
        and (stored_pd or {}).get("task_key") == TASK_KEY,
        {"binding": decoded(fields.get("upstream_binding_json")), "selected_task": (stored_pd or {}).get("task_key"), "selected_fp": pick.get("selected_fp")},
    )
    add(
        checks,
        "T3-05",
        artifact_ok,
        {"artifact_length": len(artifact), "artifact_sha256": sha256_text(artifact), "artifact_status": packaging_outputs.get("artifact_status")},
    )
    add(
        checks,
        "T3-06-D1b",
        not history_hits and not hedge_hits and "used_fact_refs" in artifact and "fact_check_status" in artifact,
        {"habitual_behavior_claims": history_hits, "hedge_words": hedge_hits, "used_fact_refs_present": "used_fact_refs" in artifact, "fact_check_status_present": "fact_check_status" in artifact},
    )
    add(
        checks,
        "T3-07-D1c",
        not questions["artifact"] and not questions["user_delivery"],
        {"audience_directed_question_sentences": questions, "count": len(questions["artifact"]) + len(questions["user_delivery"])},
    )
    add(
        checks,
        "T3-08",
        stored_cs is not None
        and stored_pd is not None
        and stored_pp is not None
        and len({stored_cs.get("fp"), stored_pd.get("fp"), stored_pp.get("fp")}) == 3
        and sha256_text(stored_cs["body"]) == T1_BODY_SHA256
        and sha256_text(stored_pd["body"]) == expected_pd_sha
        and sha256_text(stored_pp["body"]) == sha256_text(artifact),
        {
            "store_item_count": len(store["items"]),
            "CS": {"fp": (stored_cs or {}).get("fp"), "sha256": sha256_text((stored_cs or {}).get("body", ""))},
            "PD": {"fp": (stored_pd or {}).get("fp"), "sha256": sha256_text((stored_pd or {}).get("body", ""))},
            "PP": {"fp": (stored_pp or {}).get("fp"), "sha256": sha256_text((stored_pp or {}).get("body", ""))},
        },
    )
    add(
        checks,
        "T3-09",
        (ledger_pd or {}).get("accepted") is True
        and (ledger_pd or {}).get("stale") is False
        and (ledger_pp or {}).get("accepted") is False
        and (ledger_pp or {}).get("stale") is False,
        {"PD_accepted_stale": [(ledger_pd or {}).get("accepted"), (ledger_pd or {}).get("stale")], "PP_accepted_stale": [(ledger_pp or {}).get("accepted"), (ledger_pp or {}).get("stale")]},
    )
    add(
        checks,
        "T3-10",
        (stored_pd or {}).get("body") == selected_body and (stored_pd or {}).get("body") != (stored_pp or {}).get("body"),
        {"PD_preserved": (stored_pd or {}).get("body") == selected_body, "PP_did_not_overwrite_PD": (stored_pd or {}).get("body") != (stored_pp or {}).get("body")},
    )
    add(
        checks,
        "T3-11",
        len(document["app_runs_in_window"]["SEAM"]) == 1 and all(counts[app] == 0 for app in PROFESSIONAL_APPS if app != "PUBLISHING_PACKAGING"),
        {"other_five_professional_runs": {app: counts[app] for app in PROFESSIONAL_APPS if app != "PUBLISHING_PACKAGING"}},
    )
    add(
        checks,
        "T3-12",
        top["workflow_id"] == "28059850-1745-4e6d-bfac-0fbe278c5615"
        and uapp_workflow_md5 == "91a3984b2c3797d6741165b116fa3cb1"
        and seam_workflow_md5 == "db49a3da8973d4fdcbe9ecf63bdf7e2a"
        and pp_workflow_md5 == "8366328bf827bd0f460455d750d45c4f",
        {"UAPP": {"run_id": top["id"], "workflow_id": top["workflow_id"], "graph_md5": uapp_workflow_md5}, "SEAM": {"run_id": seam["id"], "workflow_id": seam["workflow_id"], "graph_md5": seam_workflow_md5}, "PP_b2": {"run_id": packaging["id"], "workflow_id": packaging["workflow_id"], "graph_md5": pp_workflow_md5}},
    )
    add(
        checks,
        "T3-COST",
        len(llm) == 6
        and all(item["status"] == "succeeded" and not item["error"] for item in llm)
        and all(len(runs) <= 1 for runs in document["app_runs_in_window"].values()),
        {"llm_node_attempts": llm, "platform_internal_replays": 0, "runner_attempts": document["request_attempts_by_runner"]},
    )
    return {
        "turn": "T3",
        "workflow_run_id": document["workflow_run_id"],
        "packaging_run_id": packaging["id"],
        "artifact": {"length": len(artifact), "sha256": sha256_text(artifact), "fp": (stored_pp or {}).get("fp"), "bfp": (stored_pp or {}).get("bfp")},
        "checks": checks,
        "result": "PASS" if all(item["result"] == "PASS" for item in checks) else "FAIL",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--turn", required=True, choices=("T2", "T3"))
    args = parser.parse_args()
    if sha256_file(GATE) != GATE_SHA256 or sha256_file(INPUTS) != INPUTS_SHA256:
        raise RuntimeError("frozen Gate or input hash mismatch")
    t2_result = verify_t2(raw("T2"))
    result = t2_result if args.turn == "T2" else verify_t3(raw("T3"), t2_result)
    report = {
        "document": {
            "id": f"UAAB_SUCCESSOR_{args.turn}_VERIFY_v1.2",
            "task_id": "DIYU-V1-UAPP-ACCEPTED-ARTIFACT-BINDING-001",
            "gate_sha256": GATE_SHA256,
            "inputs_sha256": INPUTS_SHA256,
            "model_calls": 0,
            "dify_writes": 0,
        },
        "result": result,
    }
    output = os.path.join(EVIDENCE_DIR, f"UAAB_SUCCESSOR_{args.turn}_VERIFY_v1.2.json")
    with open(output, "x", encoding="utf-8") as handle:
        json.dump(report, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    print(f"{args.turn} {result['result']} run={result['workflow_run_id']}")
    for check in result["checks"]:
        print(f"  {check['id']}: {check['result']}")
    print(f"SAVED {output}")
    return 0 if result["result"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
