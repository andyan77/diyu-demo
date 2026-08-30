#!/usr/bin/env python3
"""Run exactly one frozen UAAB successor turn and retain raw Dify evidence.

The runner has no retry loop, uploads no files, supplies ``inputs={}``, and does
not adjudicate the result.  ``--preflight`` is read-only and starts no workflow.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import subprocess
import time
from types import ModuleType
from typing import Any

HERE = os.path.dirname(os.path.abspath(__file__))
UAPP_ROOT = os.path.abspath(os.path.join(HERE, ".."))
REPO = os.path.abspath(os.path.join(UAPP_ROOT, ".."))
ENV_FILE = "/home/faye/diyu-demo-worktrees/m3-account-content-operator-v1/.env"
GATE = os.path.join(UAPP_ROOT, "stages", "UAAB_GATE_v1.2.json")
INPUTS = os.path.join(UAPP_ROOT, "stages", "UAAB_SUCCESSOR_INPUTS_v1.2.json")
EVIDENCE_DIR = os.path.join(UAPP_ROOT, "evidence", "stages", "uapp_artifact_binding")

GATE_SHA256 = "dbe4c023256e378d93827094b5c762f7c1b67b1c7528fff92fbbb84b219ea622"
INPUTS_SHA256 = "f669c5163533807e47c827f9c08792f014ce4743e0df35ef23adb9b9b3ac29ca"
UAPP_CANDIDATE_MD5 = "91a3984b2c3797d6741165b116fa3cb1"
UAPP_CANDIDATE_WORKFLOW = "28059850-1745-4e6d-bfac-0fbe278c5615"
PP_B2_MD5 = "8366328bf827bd0f460455d750d45c4f"
SEAM_MD5 = "db49a3da8973d4fdcbe9ecf63bdf7e2a"
HOP_MD5 = "e38378c3c2a66b75aa7e645368c9e1ce"
T1_BODY_SHA256 = "65f58acb09de20b77ff1deb669e2210e5f128a4b06fbaab14fbf31cf9955b938"
T1_FP = "3d7342e36d939c31"
TASK_KEY = "ec666086-dce5-4e79-ba0f-6ac88f04a0bb"
T2_PD_SHA256 = "8f91984b628da1c65250c7bb2f90e9a31c86233826ceee9271bcc46b77b2c21b"
T2_PD_FP = "559a204d7c4f1f2a"
T2_VERIFY_SHA256 = "24f11c8a5a2231167fe76da48e035d49e3758d15bfe6cdbaf5c6ab9b116abacc"

APPS: dict[str, str] = {
    "UAPP": "85c01f85-a081-43e9-ab09-9993289cc200",
    "M3": "a4c3b19b-243f-490b-9aca-3aa19767d6a5",
    "HOP": "6c46fdb1-5f49-4513-a0c0-29957b3dcee4",
    "SEAM": "5fca0162-e26b-4545-a00b-66b1a2a2a077",
    "MATRIX": "fd25ebfa-db67-40c3-82e5-202e1254facf",
    "CAMPAIGN": "1f9d65ea-8af5-45f0-a1d0-a80223d354e2",
    "CONTENT_BRIEF": "b1dcf784-540e-4b3f-8ba2-3812f477f3ce",
    "CREATIVE_SCRIPT": "44b55f9d-3792-40c3-b095-f2696464b4ec",
    "PRODUCTION_DIRECTOR": "13cfabd5-f592-4354-a304-47098b765697",
    "PUBLISHING_PACKAGING": "c9cdea24-9df3-400b-9ecd-1d740e8c96df",
}


def load_module(name: str, path: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


DC = load_module("uaab_run_dc", os.path.join(REPO, "account-operations", "tools", "dify_client.py"))


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


def sha256_file(path: str) -> str:
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def app_state(app_id: str) -> dict[str, Any]:
    raw = psql(
        "select json_build_object('app_id',a.id,'workflow_id',w.id,'version',w.version,"
        "'graph_md5',md5(w.graph),'nodes',jsonb_array_length(w.graph::jsonb->'nodes'),"
        "'edges',jsonb_array_length(w.graph::jsonb->'edges'))::text "
        "from apps a join workflows w on w.id=a.workflow_id "
        f"where a.id='{app_id}';"
    )
    return json.loads(raw)


def provider_state() -> dict[str, Any]:
    raw = psql(
        "select json_build_object('provider_id',p.id,'version',p.version,'graph_md5',md5(w.graph))::text "
        "from tool_workflow_providers p join workflows w on w.app_id=p.app_id and w.version=p.version "
        "where p.id='21a000b1-5d14-42e9-b380-64c2c2aa16a0';"
    )
    return json.loads(raw)


def conversation_variables(conversation_id: str) -> dict[str, Any]:
    raw = psql(
        "select coalesce(json_agg(data)::text,'[]') from workflow_conversation_variables "
        f"where conversation_id='{conversation_id}';"
    )
    result: dict[str, Any] = {}
    for item in json.loads(raw or "[]"):
        record = json.loads(item) if isinstance(item, str) else item
        result[record.get("name")] = record.get("value")
    return result


def json_rows(sql: str) -> list[dict[str, Any]]:
    raw = psql(sql)
    return json.loads(raw or "[]") or []


def node_details(run_id: str) -> list[dict[str, Any]]:
    return json_rows(
        "select coalesce(json_agg(json_build_object("
        "'idx',e.index,'node_id',e.node_id,'title',e.title,'type',e.node_type,"
        "'status',e.status,'error',e.error,'elapsed',e.elapsed_time,"
        "'inputs',e.inputs,'process_data',e.process_data,'outputs',e.outputs,"
        "'execution_metadata',e.execution_metadata,'created_at',e.created_at,"
        "'finished_at',e.finished_at) order by e.index)::text,'[]') "
        "from workflow_node_executions e "
        f"where e.workflow_run_id='{run_id}';"
    )


def runs_for_window(app_id: str, started_at: str) -> list[dict[str, Any]]:
    rows = json_rows(
        "select coalesce(json_agg(json_build_object("
        "'id',w.id,'app_id',w.app_id,'workflow_id',w.workflow_id,'type',w.type,"
        "'triggered_from',w.triggered_from,'version',w.version,'status',w.status,"
        "'inputs',w.inputs,'outputs',w.outputs,'error',w.error,'elapsed',w.elapsed_time,"
        "'total_tokens',w.total_tokens,'total_steps',w.total_steps,"
        "'exceptions_count',w.exceptions_count,'created_at',w.created_at,"
        "'finished_at',w.finished_at) order by w.created_at)::text,'[]') "
        "from workflow_runs w "
        f"where w.app_id='{app_id}' and w.created_at >= timestamp '{started_at}';"
    )
    for row in rows:
        row["node_detail"] = node_details(row["id"])
    return rows


def raw_evidence_path(turn_id: str) -> str:
    return os.path.join(EVIDENCE_DIR, f"UAAB_SUCCESSOR_RAW_{turn_id}_v1.2.json")


def preflight(turn_id: str) -> dict[str, Any]:
    gate = json.load(open(GATE, encoding="utf-8"))
    frozen_inputs = json.load(open(INPUTS, encoding="utf-8"))
    turn = next(item for item in gate["formal_turns"] if item["id"] == turn_id)
    input_turn = next(item for item in frozen_inputs["turns"] if item["id"] == turn_id)
    conversation_id = gate["inputs"]["conversation_id"]
    variables = conversation_variables(conversation_id)
    store = json.loads(variables.get("uapp_last_artifact") or "{}")
    state = json.loads(variables.get("uapp_task_fields") or "{}")
    stored_t1 = next((item for item in store.get("items", []) if item.get("fp") == T1_FP), None)
    ledger_t1 = next((item for item in state.get("artifacts", []) if item.get("fp") == T1_FP), None)
    stored_t2 = next((item for item in store.get("items", []) if item.get("fp") == T2_PD_FP), None)
    ledger_t2 = next((item for item in state.get("artifacts", []) if item.get("fp") == T2_PD_FP), None)
    t2_verify_path = os.path.join(EVIDENCE_DIR, "UAAB_SUCCESSOR_T2_VERIFY_v1.2.json")
    t2_verify = json.load(open(t2_verify_path, encoding="utf-8")) if os.path.exists(t2_verify_path) else {}
    result = {
        "gate_sha256": sha256_file(GATE),
        "inputs_sha256": sha256_file(INPUTS),
        "query_exact": turn["query"] == input_turn["query"],
        "inputs": frozen_inputs.get("inputs"),
        "files": frozen_inputs.get("files"),
        "uapp": app_state(APPS["UAPP"]),
        "pp": app_state(APPS["PUBLISHING_PACKAGING"]),
        "provider": provider_state(),
        "seam": app_state(APPS["SEAM"]),
        "hop": app_state(APPS["HOP"]),
        "active_runs": int(psql("select count(*) from workflow_runs where status='running';")),
        "candidate_top_level_runs": int(
            psql(
                "select count(*) from workflow_runs "
                f"where app_id='{APPS['UAPP']}' and workflow_id='{UAPP_CANDIDATE_WORKFLOW}';"
            )
        ),
        "T1": {
            "store_present": stored_t1 is not None,
            "body_sha256": sha256_text((stored_t1 or {}).get("body", "")),
            "accepted": (ledger_t1 or {}).get("accepted"),
            "stale": (ledger_t1 or {}).get("stale"),
        },
        "T2_predecessor": {
            "verify_sha256": sha256_file(t2_verify_path) if os.path.exists(t2_verify_path) else None,
            "verify_result": (t2_verify.get("result") or {}).get("result"),
            "store_present": stored_t2 is not None,
            "body_sha256": sha256_text((stored_t2 or {}).get("body", "")),
            "capability": (stored_t2 or {}).get("cap"),
            "task_key": (stored_t2 or {}).get("task_key"),
            "accepted": (ledger_t2 or {}).get("accepted"),
            "stale": (ledger_t2 or {}).get("stale"),
        },
        "raw_evidence_absent": not os.path.exists(raw_evidence_path(turn_id)),
    }
    expected_runs = 0 if turn_id == "T2" else 1
    checks = {
        "gate": result["gate_sha256"] == GATE_SHA256,
        "inputs_file": result["inputs_sha256"] == INPUTS_SHA256,
        "query": result["query_exact"],
        "empty_inputs_and_files": result["inputs"] == {} and result["files"] == [],
        "uapp_candidate": result["uapp"]["graph_md5"] == UAPP_CANDIDATE_MD5
        and result["uapp"]["workflow_id"] == UAPP_CANDIDATE_WORKFLOW,
        "pp_and_provider": result["pp"]["graph_md5"] == PP_B2_MD5
        and result["provider"]["graph_md5"] == PP_B2_MD5,
        "seam_hop": result["seam"]["graph_md5"] == SEAM_MD5 and result["hop"]["graph_md5"] == HOP_MD5,
        "no_active_run": result["active_runs"] == 0,
        "budget_position": result["candidate_top_level_runs"] == expected_runs,
        "T1_identity": result["T1"] == {
            "store_present": True,
            "body_sha256": T1_BODY_SHA256,
            "accepted": True,
            "stale": False,
        },
        "new_evidence_path": result["raw_evidence_absent"],
    }
    if turn_id == "T3":
        checks["T2_predecessor"] = result["T2_predecessor"] == {
            "verify_sha256": T2_VERIFY_SHA256,
            "verify_result": "PASS",
            "store_present": True,
            "body_sha256": T2_PD_SHA256,
            "capability": "PRODUCTION_DIRECTOR",
            "task_key": TASK_KEY,
            "accepted": False,
            "stale": False,
        }
    result["checks"] = checks
    result["verdict"] = "PASS" if all(checks.values()) else "FAIL"
    return result


def run_turn(turn_id: str) -> int:
    pre = preflight(turn_id)
    if pre["verdict"] != "PASS":
        raise RuntimeError(f"preflight failed: {json.dumps(pre['checks'], ensure_ascii=False)}")

    gate = json.load(open(GATE, encoding="utf-8"))
    turn = next(item for item in gate["formal_turns"] if item["id"] == turn_id)
    conversation_id = gate["inputs"]["conversation_id"]
    end_user = gate["inputs"]["end_user"]

    console = DC.Console(env=DC.load_env(ENV_FILE))
    key = console.app_api_key(APPS["UAPP"], create_if_missing=False)
    if not key:
        raise RuntimeError("UAPP API key is absent")

    started_at = psql("select clock_timestamp()::text;")
    request = {
        "inputs": {},
        "query": turn["query"],
        "response_mode": "blocking",
        "user": end_user,
        "conversation_id": conversation_id,
        "files": [],
    }
    start = time.time()
    response = DC.http_json(
        "POST",
        "/v1/chat-messages",
        headers={"Authorization": f"Bearer {key}"},
        body=request,
        timeout=1800,
    )
    elapsed = round(time.time() - start, 2)
    try:
        body = json.loads(response["body"])
    except (TypeError, json.JSONDecodeError):
        body = {"raw": str(response.get("body", ""))[:4000]}

    message_id = body.get("message_id") or ""
    top_run_id = ""
    if message_id:
        top_run_id = psql(
            "select coalesce(w.id::text,'') from workflow_runs w join messages m on m.workflow_run_id=w.id "
            f"where m.id='{message_id}';"
        )
    runs = {name: runs_for_window(app_id, started_at) for name, app_id in APPS.items()}
    evidence = {
        "document": {
            "id": f"UAAB_SUCCESSOR_RAW_{turn_id}_v1.2",
            "task_id": "DIYU-V1-UAPP-ACCEPTED-ARTIFACT-BINDING-001",
            "raw_execution_evidence": True,
            "adjudication": "NOT_PERFORMED_BY_RUNNER",
        },
        "gate_sha256": GATE_SHA256,
        "inputs_sha256": INPUTS_SHA256,
        "preflight": pre,
        "turn": turn_id,
        "target": turn["target"],
        "window_start": started_at,
        "transport": DC.TRANSPORT,
        "request": request,
        "request_attempts_by_runner": 1,
        "http_status": response["status"],
        "elapsed_seconds": elapsed,
        "message_id": message_id,
        "conversation_id": body.get("conversation_id"),
        "workflow_run_id": top_run_id,
        "answer": body.get("answer"),
        "response_error": body.get("message") or body.get("error"),
        "app_runs_in_window": runs,
        "conversation_variables_after": conversation_variables(conversation_id),
    }
    output = raw_evidence_path(turn_id)
    with open(output, "x", encoding="utf-8") as handle:
        json.dump(evidence, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    print(f"HTTP {response['status']} elapsed={elapsed}s transport={DC.TRANSPORT}")
    print(f"workflow_run_id={top_run_id} message_id={message_id}")
    print("runs=" + json.dumps({name: len(items) for name, items in runs.items()}, ensure_ascii=False))
    print(f"SAVED {output}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--preflight", choices=("T2", "T3"))
    parser.add_argument("--turn", choices=("T2", "T3"))
    args = parser.parse_args()
    if bool(args.preflight) == bool(args.turn):
        raise SystemExit("Choose exactly one of --preflight or --turn")
    if args.preflight:
        report = preflight(args.preflight)
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0 if report["verdict"] == "PASS" else 1
    return run_turn(args.turn)


if __name__ == "__main__":
    raise SystemExit(main())
