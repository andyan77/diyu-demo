#!/usr/bin/env python3
"""Run the single frozen cross-turn correction and retain raw evidence.

There is intentionally no retry loop and no adjudication in this runner.
``--preflight`` is read-only and starts no workflow.
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
GATE = os.path.join(UAPP_ROOT, "stages", "UAPP_CORRECTION_GATE_v1.0.json")
INPUTS = os.path.join(UAPP_ROOT, "stages", "UAPP_CORRECTION_INPUTS_v1.0.json")
OUTPUT = os.path.join(
    UAPP_ROOT,
    "evidence",
    "stages",
    "uapp_correction",
    "UAPP_CORRECTION_RAW_v1.0.json",
)

GATE_SHA256 = "9220a7bd587ec030fa340892609addab15cb70432199924285e1b1fa634a95d7"
INPUTS_SHA256 = "eda84ad987a58e1db3fd79f028859d0ddbce9146d83dca7038ce5c804d2c9549"
UAPP_MD5 = "91a3984b2c3797d6741165b116fa3cb1"
PP_MD5 = "8366328bf827bd0f460455d750d45c4f"
SEAM_MD5 = "db49a3da8973d4fdcbe9ecf63bdf7e2a"
HOP_MD5 = "e38378c3c2a66b75aa7e645368c9e1ce"
M3_MD5 = "cd93757bcf8ad322f3b32fc43b2da3ff"
STATE_SHA256 = "7d7c678b4f9a54e26acf8040d0e95869f1fa2858f34825bbf7a6d46c1d91b070"
STORE_SHA256 = "1d095c20c2a3e4815c4e5a53b1e2f870cd80ba009d0fc0bf24ff70a61170c217"
PD_FP = "559a204d7c4f1f2a"
PD_SHA256 = "8f91984b628da1c65250c7bb2f90e9a31c86233826ceee9271bcc46b77b2c21b"
TASK_KEY = "ec666086-dce5-4e79-ba0f-6ac88f04a0bb"
ACCOUNT_ID = "a2f101c5-2e9d-4538-b677-2efcdfc1f0bf"


def load_module(name: str, path: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


BASE = load_module("uapp_correction_base", os.path.join(HERE, "UAAB_SUCCESSOR_RUN_v1.2.py"))
DC = BASE.DC


def sha256_file(path: str) -> str:
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def m2_psql(sql: str) -> str:
    completed = subprocess.run(
        [
            "docker",
            "exec",
            "-i",
            "docker-db_postgres-1",
            "psql",
            "-U",
            "postgres",
            "-d",
            "diyu_business",
            "-tA",
            "-v",
            "ON_ERROR_STOP=1",
            "-c",
            sql,
        ],
        capture_output=True,
        check=False,
        text=True,
    )
    if completed.returncode != 0:
        raise RuntimeError((completed.stderr or completed.stdout)[:1000])
    return completed.stdout.strip()


def git_state() -> dict[str, Any]:
    def command(*args: str) -> str:
        completed = subprocess.run(
            ["git", *args], cwd=REPO, capture_output=True, check=True, text=True
        )
        return completed.stdout.strip()

    return {
        "root": command("rev-parse", "--show-toplevel"),
        "branch": command("branch", "--show-current"),
        "head": command("rev-parse", "HEAD"),
        "origin_branch": command("rev-parse", "origin/codex/v1-uapp-progressive-canvas-001"),
        "main": command("rev-parse", "main"),
        "origin_main": command("rev-parse", "origin/main"),
        "status": command("status", "--porcelain=v1"),
    }


def m2_snapshot() -> dict[str, Any]:
    return {
        "task_snapshots": int(
            m2_psql(f"select count(*) from task_snapshots where task_id='{TASK_KEY}';")
        ),
        "artifacts": int(m2_psql(f"select count(*) from artifacts where task_id='{TASK_KEY}';")),
        "task_run_states": int(
            m2_psql(f"select count(*) from task_run_states where task_id='{TASK_KEY}';")
        ),
        "account_publish_instances": int(
            m2_psql(f"select count(*) from publish_instances where account_id='{ACCOUNT_ID}';")
        ),
        "non_test_publish_instances": int(
            m2_psql("select count(*) from publish_instances where not is_test or not is_simulated;")
        ),
        "non_test_feedback_records": int(
            m2_psql("select count(*) from feedback_records where not is_test or not is_simulated;")
        ),
        "schema_md5": m2_psql(
            "select md5(string_agg(table_name||'.'||column_name||':'||data_type,',' "
            "order by table_name,ordinal_position)) from information_schema.columns "
            "where table_schema='public';"
        ),
    }


def protected_apps() -> dict[str, Any]:
    return {
        name: BASE.app_state(app_id)
        for name, app_id in BASE.APPS.items()
    } | {"PP_provider": BASE.provider_state()}


def preflight() -> dict[str, Any]:
    gate = json.load(open(GATE, encoding="utf-8"))
    inputs = json.load(open(INPUTS, encoding="utf-8"))
    variables = BASE.conversation_variables(gate["inputs"]["conversation_id"])
    state_raw = variables.get("uapp_task_fields") or ""
    store_raw = variables.get("uapp_last_artifact") or ""
    state = json.loads(state_raw)
    store = json.loads(store_raw)
    ledger_pd = next((item for item in state.get("artifacts", []) if item.get("fp") == PD_FP), {})
    stored_pd = next((item for item in store.get("items", []) if item.get("fp") == PD_FP), {})
    apps = protected_apps()
    git = git_state()
    m2 = m2_snapshot()
    result = {
        "gate_sha256": sha256_file(GATE),
        "inputs_sha256": sha256_file(INPUTS),
        "query_sha256": sha256_text(inputs["turn"]["query"]),
        "git": git,
        "apps": apps,
        "active_runs": int(BASE.psql("select count(*) from workflow_runs where status='running';")),
        "state_sha256": sha256_text(state_raw),
        "store_sha256": sha256_text(store_raw),
        "state_revision": state.get("rev"),
        "production_profile": state.get("fields", {}).get("production.profile"),
        "production_time_window": state.get("fields", {}).get("production.time_window"),
        "pd": {
            "ledger": ledger_pd,
            "store_identity": {
                "fp": stored_pd.get("fp"),
                "bfp": stored_pd.get("bfp"),
                "cap": stored_pd.get("cap"),
                "task_key": stored_pd.get("task_key"),
                "length": len(stored_pd.get("body") or ""),
                "sha256": sha256_text(stored_pd.get("body") or ""),
            },
        },
        "m2": m2,
        "raw_evidence_absent": not os.path.exists(OUTPUT),
    }
    checks = {
        "gate": result["gate_sha256"] == GATE_SHA256,
        "inputs": result["inputs_sha256"] == INPUTS_SHA256,
        "query": result["query_sha256"] == inputs["turn"]["sha256"],
        "git": git["root"] == REPO
        and git["branch"] == "codex/v1-uapp-progressive-canvas-001"
        and git["head"] == git["origin_branch"]
        and git["main"] == git["origin_main"]
        and git["status"] == "",
        "published_bindings": apps["UAPP"]["graph_md5"] == UAPP_MD5
        and apps["PUBLISHING_PACKAGING"]["graph_md5"] == PP_MD5
        and apps["PP_provider"]["graph_md5"] == PP_MD5
        and apps["SEAM"]["graph_md5"] == SEAM_MD5
        and apps["HOP"]["graph_md5"] == HOP_MD5
        and apps["M3"]["graph_md5"] == M3_MD5,
        "no_active_runs": result["active_runs"] == 0,
        "state_identity": result["state_sha256"] == STATE_SHA256
        and result["store_sha256"] == STORE_SHA256
        and result["state_revision"] == 12,
        "pd_current": ledger_pd.get("accepted") is True
        and ledger_pd.get("stale") is False
        and result["pd"]["store_identity"] == {
            "fp": PD_FP,
            "bfp": "846c1f3833180c11",
            "cap": "PRODUCTION_DIRECTOR",
            "task_key": TASK_KEY,
            "length": 9304,
            "sha256": PD_SHA256,
        },
        "m2_scope": m2 == {
            "task_snapshots": 0,
            "artifacts": 0,
            "task_run_states": 0,
            "account_publish_instances": 0,
            "non_test_publish_instances": 1568,
            "non_test_feedback_records": 117,
            "schema_md5": "25192c11562827efedfc3b2c22c3b4fd",
        },
        "new_raw_path": result["raw_evidence_absent"],
    }
    result["checks"] = checks
    result["verdict"] = "PASS" if all(checks.values()) else "FAIL"
    return result


def run_once() -> int:
    before = preflight()
    if before["verdict"] != "PASS":
        raise RuntimeError(f"preflight failed: {json.dumps(before['checks'], ensure_ascii=False)}")

    gate = json.load(open(GATE, encoding="utf-8"))
    inputs = json.load(open(INPUTS, encoding="utf-8"))
    app_id = gate["candidate"]["UAPP"]["app_id"]
    conversation_id = gate["inputs"]["conversation_id"]
    end_user = gate["inputs"]["end_user"]
    console = DC.Console(env=DC.load_env(ENV_FILE))
    key = console.app_api_key(app_id, create_if_missing=False)
    if not key:
        raise RuntimeError("UAPP API key is absent")

    started_at = BASE.psql("select clock_timestamp()::text;")
    request = {
        "inputs": {},
        "query": inputs["turn"]["query"],
        "response_mode": "blocking",
        "user": end_user,
        "conversation_id": conversation_id,
        "files": [],
    }
    started = time.time()
    response = DC.http_json(
        "POST",
        "/v1/chat-messages",
        headers={"Authorization": f"Bearer {key}"},
        body=request,
        timeout=1800,
    )
    elapsed = round(time.time() - started, 2)
    try:
        body = json.loads(response["body"])
    except (TypeError, json.JSONDecodeError):
        body = {"raw": str(response.get("body", ""))[:4000]}

    message_id = body.get("message_id") or ""
    top_run_id = ""
    if message_id:
        top_run_id = BASE.psql(
            "select coalesce(w.id::text,'') from workflow_runs w "
            "join messages m on m.workflow_run_id=w.id "
            f"where m.id='{message_id}';"
        )
    runs = {
        name: BASE.runs_for_window(app_id_value, started_at)
        for name, app_id_value in BASE.APPS.items()
    }
    evidence = {
        "document": {
            "id": "UAPP_CORRECTION_RAW_v1.0",
            "task_id": "DIYU-V1-UNIFIED-DIFY-APPLICATION-001",
            "raw_execution_evidence": True,
            "adjudication": "NOT_PERFORMED_BY_RUNNER",
        },
        "gate_sha256": GATE_SHA256,
        "inputs_sha256": INPUTS_SHA256,
        "runner_sha256": sha256_file(__file__),
        "preflight": before,
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
        "conversation_variables_after": BASE.conversation_variables(conversation_id),
        "protected_apps_after": protected_apps(),
        "m2_after": m2_snapshot(),
        "git_after": git_state(),
    }
    with open(OUTPUT, "x", encoding="utf-8") as handle:
        json.dump(evidence, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    print(f"HTTP {response['status']} elapsed={elapsed}s transport={DC.TRANSPORT}")
    print(f"workflow_run_id={top_run_id} message_id={message_id}")
    print("runs=" + json.dumps({name: len(items) for name, items in runs.items()}, ensure_ascii=False))
    print(f"SAVED {OUTPUT}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--preflight", action="store_true")
    parser.add_argument("--run", action="store_true")
    args = parser.parse_args()
    if args.preflight == args.run:
        raise SystemExit("Choose exactly one of --preflight or --run")
    if args.preflight:
        report = preflight()
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0 if report["verdict"] == "PASS" else 1
    return run_once()


if __name__ == "__main__":
    raise SystemExit(main())
