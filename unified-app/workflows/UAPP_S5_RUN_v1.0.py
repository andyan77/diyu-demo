#!/usr/bin/env python3
"""Run one frozen S5 turn and preserve raw evidence without adjudicating it."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import logging
import os
import subprocess
import time
from types import ModuleType
from typing import Any

HERE = os.path.dirname(os.path.abspath(__file__))
UAPP_ROOT = os.path.abspath(os.path.join(HERE, ".."))
REPO = os.path.abspath(os.path.join(UAPP_ROOT, ".."))
ENV_FILE = "/home/faye/diyu-demo-worktrees/m3-account-content-operator-v1/.env"
SCENARIOS = os.path.join(UAPP_ROOT, "stages", "UAPP_S5_FROZEN_SCENARIOS_v1.0.json")
MANIFEST = os.path.join(UAPP_ROOT, "stages", "UAPP_S5_CANDIDATE_RUN_MANIFEST_v1.0.yaml")
GATE = os.path.join(UAPP_ROOT, "stages", "UAPP_S5_GATE_v1.0.json")
EVIDENCE = os.path.join(UAPP_ROOT, "evidence", "stages", "uapp_s5")
UAPP_APP_ID = "85c01f85-a081-43e9-ab09-9993289cc200"


def load_module(name: str, path: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


BASE = load_module("uapp_s5_base", os.path.join(HERE, "UAAB_SUCCESSOR_RUN_v1.2.py"))
STATE = load_module("uapp_s5_state", os.path.join(HERE, "UAPP_CORRECTION_RUN_v1.0.py"))
UPLOAD = load_module("uapp_s5_upload", os.path.join(HERE, "UAPP_RUN_v1.0.py"))
DC = BASE.DC


def sha256_file(path: str) -> str:
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


def load_json(path: str) -> dict[str, Any]:
    with open(path, encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise RuntimeError(f"Expected object: {path}")
    return value


def safe_key(key: str) -> str:
    return key.replace(":", "_").replace("/", "_")


def raw_path(key: str) -> str:
    return os.path.join(EVIDENCE, "raw", f"{safe_key(key)}.json")


def check_path(key: str) -> str:
    return os.path.join(EVIDENCE, "checks", f"{safe_key(key)}.json")


def m2(sql: str) -> str:
    completed = subprocess.run(
        ["docker", "exec", "-i", "docker-db_postgres-1", "psql", "-U", "postgres",
         "-d", "diyu_business", "-tA", "-v", "ON_ERROR_STOP=1", "-c", sql],
        capture_output=True, check=False, text=True,
    )
    if completed.returncode != 0:
        raise RuntimeError((completed.stderr or completed.stdout)[:1000])
    return completed.stdout.strip()


def m2_json(sql: str) -> Any:
    raw = m2(sql)
    return json.loads(raw or "[]")


def global_m2_guard() -> dict[str, Any]:
    return {
        "non_test_publish_instances": int(m2("select count(*) from publish_instances where not is_test or not is_simulated;")),
        "non_test_feedback_records": int(m2("select count(*) from feedback_records where not is_test or not is_simulated;")),
        "schema_md5": m2("select md5(string_agg(table_name||'.'||column_name||':'||data_type,',' order by table_name,ordinal_position)) from information_schema.columns where table_schema='public';"),
    }


def scoped_m2(conversation_id: str) -> dict[str, Any]:
    tag = "".join(char for char in conversation_id if char.isalnum())[:12]
    workspace = m2_json(
        "select coalesce(json_agg(to_jsonb(x))::text,'[]') from "
        f"(select * from workspaces where name='ws-uapp-{tag}') x;"
    ) if tag else []
    workspace_id = workspace[0]["id"] if workspace else ""
    quoted_ws = f"'{workspace_id}'" if workspace_id else "'00000000-0000-0000-0000-000000000000'"
    tasks = m2_json(
        "select coalesce(json_agg(to_jsonb(x))::text,'[]') from "
        f"(select * from tasks where workspace_id={quoted_ws} order by created_at,id) x;"
    )
    task_ids = [row["id"] for row in tasks]
    task_array = "array[" + ",".join(f"'{value}'::uuid" for value in task_ids) + "]" if task_ids else "array[]::uuid[]"
    artifact_ids = m2_json(
        "select coalesce(json_agg(id)::text,'[]') from artifacts "
        f"where task_id=any({task_array});"
    )
    artifact_array = "array[" + ",".join(f"'{value}'::uuid" for value in artifact_ids) + "]" if artifact_ids else "array[]::uuid[]"

    def rows(table: str, clause: str) -> Any:
        return m2_json(
            "select coalesce(json_agg(to_jsonb(x))::text,'[]') from "
            f"(select * from {table} where {clause} order by created_at,id) x;"
        )

    return {
        "workspace": workspace,
        "cycles": rows("cycles", f"workspace_id={quoted_ws}"),
        "tasks": tasks,
        "materials": rows("materials", f"workspace_id={quoted_ws}"),
        "artifacts": rows("artifacts", f"task_id=any({task_array})"),
        "content_versions": rows("content_versions", f"artifact_id=any({artifact_array})"),
        "publish_instances": rows("publish_instances", f"workspace_id={quoted_ws}"),
        "feedback_records": rows("feedback_records", f"workspace_id={quoted_ws}"),
        "task_snapshots": rows("task_snapshots", f"task_id=any({task_array})"),
        "task_run_states": rows("task_run_states", f"task_id=any({task_array})"),
    }


def frozen() -> tuple[dict[str, Any], dict[str, Any]]:
    for path in (SCENARIOS, MANIFEST, GATE):
        if not os.path.exists(path):
            raise RuntimeError(f"Frozen prerequisite absent: {path}")
    scenarios = load_json(SCENARIOS)
    gate = load_json(GATE)
    if gate.get("document", {}).get("id") != "UAPP_S5_GATE_v1.0":
        raise RuntimeError("Unexpected Gate identity")
    return scenarios, gate


def find_turn(scenarios: dict[str, Any], key: str) -> dict[str, Any]:
    matches = [turn for turn in scenarios["turns"] if turn["key"] == key]
    if len(matches) != 1:
        raise RuntimeError(f"Frozen turn identity is not unique: {key}")
    return matches[0]


def predecessor_context(scenarios: dict[str, Any], turn: dict[str, Any]) -> tuple[str, str]:
    order = scenarios["formal_order"]
    index = order.index(turn["key"])
    for previous_key in reversed(order[:index]):
        previous = find_turn(scenarios, previous_key)
        if previous["conversation_group"] != turn["conversation_group"]:
            continue
        evidence = load_json(raw_path(previous_key))
        check = load_json(check_path(previous_key))
        if check.get("verdict") != "PASS":
            raise RuntimeError(f"Predecessor turn did not PASS: {previous_key}")
        return str(evidence.get("conversation_id") or ""), str(evidence.get("end_user") or "")
    return "", f"uapp-s5-{turn['conversation_group'].lower()}-20260830"


def preflight(key: str) -> dict[str, Any]:
    scenarios, gate = frozen()
    turn = find_turn(scenarios, key)
    order = scenarios["formal_order"]
    prior_keys = order[:order.index(key)]
    prior_checks = {
        prior: (os.path.exists(check_path(prior)) and load_json(check_path(prior)).get("verdict") == "PASS")
        for prior in prior_keys
    }
    conversation_id, end_user = predecessor_context(scenarios, turn)
    apps = STATE.protected_apps()
    expected = gate["candidate"]["graph_md5"]
    active_runs = int(BASE.psql("select count(*) from workflow_runs where status='running';"))
    console = DC.Console(env=DC.load_env(ENV_FILE))
    key_present = bool(console.app_api_key(UAPP_APP_ID, create_if_missing=False))
    result = {
        "turn_key": key,
        "gate_sha256": sha256_file(GATE),
        "scenarios_sha256": sha256_file(SCENARIOS),
        "runner_sha256": sha256_file(__file__),
        "conversation_id": conversation_id,
        "end_user": end_user,
        "apps": apps,
        "active_runs": active_runs,
        "global_m2": global_m2_guard(),
        "api_key_present": key_present,
        "raw_path_absent": not os.path.exists(raw_path(key)),
        "all_prior_turns_pass": all(prior_checks.values()),
    }
    checks = {
        "scenario_hash": result["scenarios_sha256"] == gate["frozen_files"]["scenarios_sha256"],
        "runner_hash": result["runner_sha256"] == gate["frozen_files"]["runner_sha256"],
        "candidate_graphs": all(apps[name]["graph_md5"] == value for name, value in expected.items()),
        "no_active_runs": active_runs == 0,
        "global_m2_guard": result["global_m2"] == gate["protected_surface"]["global_m2_before"],
        "api_key_present": key_present,
        "raw_path_absent": result["raw_path_absent"],
        "prior_turns_pass": result["all_prior_turns_pass"],
        "budget": len(order) == gate["budget"]["formal_top_level_turn_count"] and gate["budget"]["reachable_llm_node_attempt_cap"] <= 140,
    }
    result["checks"] = checks
    result["verdict"] = "PASS" if all(checks.values()) else "FAIL"
    return result


def run_once(key: str) -> int:
    before = preflight(key)
    if before["verdict"] != "PASS":
        raise RuntimeError(f"Preflight failed: {before['checks']}")
    scenarios, _ = frozen()
    turn = find_turn(scenarios, key)
    conversation_id = before["conversation_id"]
    end_user = before["end_user"]
    console = DC.Console(env=DC.load_env(ENV_FILE))
    api_key = console.app_api_key(UAPP_APP_ID, create_if_missing=False)
    if not api_key:
        raise RuntimeError("UAPP API key is absent")
    files: list[dict[str, str]] = []
    upload_record: dict[str, Any] | None = None
    if turn.get("upload"):
        upload_abs = os.path.join(REPO, str(turn["upload"]))
        status, uploaded = UPLOAD.upload(api_key, upload_abs, end_user)
        upload_record = {"http_status": status, "path": turn["upload"], "sha256": sha256_file(upload_abs), "response": uploaded}
        if status not in (200, 201) or not isinstance(uploaded, dict) or not uploaded.get("id"):
            raise RuntimeError(f"Fixture upload failed before workflow call: {status}")
        files = [{"type": "document", "transfer_method": "local_file", "upload_file_id": uploaded["id"]}]
    request: dict[str, Any] = {"inputs": {}, "query": turn["query"], "response_mode": "blocking", "user": end_user, "files": files}
    if conversation_id:
        request["conversation_id"] = conversation_id
    started_at = BASE.psql("select clock_timestamp()::text;")
    started = time.time()
    transport_error = ""
    try:
        response = DC.http_json("POST", "/v1/chat-messages", headers={"Authorization": f"Bearer {api_key}"}, body=request, timeout=1800)
    except Exception as error:  # noqa: BLE001 - preserve exact transport failure
        transport_error = f"{type(error).__name__}: {error}"
        response = {"status": 0, "body": json.dumps({"error": transport_error})}
    elapsed = round(time.time() - started, 2)
    body = response.get("body")
    if isinstance(body, str):
        try:
            body = json.loads(body)
        except json.JSONDecodeError:
            body = {"raw": body[:4000]}
    if not isinstance(body, dict):
        body = {"raw": str(body)[:4000]}
    message_id = str(body.get("message_id") or "")
    run_id = BASE.psql(
        "select coalesce(w.id::text,'') from workflow_runs w join messages m on m.workflow_run_id=w.id "
        f"where m.id='{message_id}';"
    ) if message_id else ""
    actual_conversation = str(body.get("conversation_id") or conversation_id)
    runs = {name: BASE.runs_for_window(app_id, started_at) for name, app_id in BASE.APPS.items()}
    evidence = {
        "document": {"id": f"UAPP_S5_RAW_{safe_key(key)}", "task_id": scenarios["document"]["task_id"], "raw_execution_evidence": True, "adjudication": "NOT_PERFORMED_BY_RUNNER"},
        "turn_key": key,
        "case_id": turn["case_id"],
        "turn_id": turn["turn_id"],
        "conversation_group": turn["conversation_group"],
        "end_user": end_user,
        "conversation_id": actual_conversation,
        "gate_sha256": sha256_file(GATE),
        "scenarios_sha256": sha256_file(SCENARIOS),
        "runner_sha256": sha256_file(__file__),
        "preflight": before,
        "window_start": started_at,
        "transport": DC.TRANSPORT,
        "transport_error": transport_error,
        "request": request,
        "request_attempts_by_runner": 1,
        "upload": upload_record,
        "http_status": response.get("status"),
        "elapsed_seconds": elapsed,
        "message_id": message_id,
        "workflow_run_id": run_id,
        "answer": body.get("answer"),
        "response_error": body.get("message") or body.get("error"),
        "app_runs_in_window": runs,
        "conversation_variables_after": BASE.conversation_variables(actual_conversation) if actual_conversation else {},
        "m2_after": scoped_m2(actual_conversation),
        "global_m2_after": global_m2_guard(),
        "protected_apps_after": STATE.protected_apps(),
        "git_after": STATE.git_state(),
    }
    os.makedirs(os.path.dirname(raw_path(key)), exist_ok=True)
    with open(raw_path(key), "x", encoding="utf-8") as handle:
        json.dump(evidence, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    logging.info("turn=%s http=%s run_id=%s elapsed=%ss", key, response.get("status"), run_id or "-", elapsed)
    return 0 if response.get("status") == 200 and not transport_error else 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("turn_key")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--preflight", action="store_true")
    mode.add_argument("--run", action="store_true")
    args = parser.parse_args()
    if args.preflight:
        report = preflight(args.turn_key)
        logging.info("%s", json.dumps(report, ensure_ascii=False, sort_keys=True))
        return 0 if report["verdict"] == "PASS" else 1
    return run_once(args.turn_key)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    raise SystemExit(main())
