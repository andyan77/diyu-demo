#!/usr/bin/env python3
"""Run one Gate-v1.1-bound AC-12 semantic-handoff turn exactly once.

The runner never performs a manual retry. It records raw execution evidence under a
new versioned directory and rejects overwrites. ``G2`` must receive the exact
conversation id returned by ``G1``.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import subprocess
import time
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
REPO = ROOT.parent
ENV = Path("/home/faye/diyu-demo-worktrees/m3-account-content-operator-v1/.env")
GATE = ROOT / "stages" / "UAPP_AC12_SEMANTIC_HANDOFF_GATE_v1.1.json"
INPUTS = ROOT / "stages" / "UAPP_AC12_SEMANTIC_HANDOFF_FROZEN_INPUTS_v1.0.json"
RAW_DIR = ROOT / "evidence" / "stages" / "uapp_ac12_semantic_handoff_final_batch_v1_1"


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


DC = load_module("dify_client", REPO / "account-operations" / "tools" / "dify_client.py")


def psql(sql: str) -> str:
    result = subprocess.run(["docker", "exec", "-i", "docker-db_postgres-1", "psql", "-U", "postgres", "-d", "dify", "-tA", "-v", "ON_ERROR_STOP=1", "-c", sql], capture_output=True, text=True, check=False)
    if result.returncode:
        raise RuntimeError((result.stderr or result.stdout)[:500])
    return result.stdout.strip()


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"object required: {path}")
    return value


def graph_md5(app_id: str) -> str:
    return psql("select md5(w.graph) from workflows w join apps a on a.workflow_id=w.id where a.id='%s';" % app_id)


def preflight(turn: str) -> dict[str, Any]:
    gate = load(GATE)
    frozen = load(INPUTS)
    turns = {str(item["id"]): item for item in frozen["turns"]}
    if turn not in turns:
        raise RuntimeError("unknown frozen turn: " + turn)
    app_id = str(gate["candidate"]["uapp_app_id"])
    console = DC.Console(env=DC.load_env(str(ENV)))
    key_exists = bool(console.app_api_key(app_id, create_if_missing=False))
    out = RAW_DIR / (turn + ".json")
    checks = {
        "gate_identity": gate["document"]["id"] == "UAPP_AC12_SEMANTIC_HANDOFF_GATE_v1.1",
        "input_freeze": sha(INPUTS) == gate["business_freeze"]["inputs_sha256"],
        "candidate_graph": graph_md5(app_id) == gate["candidate"]["published_graph_md5"],
        "no_active_workflows": psql("select count(*) from workflow_runs where status='running';") == "0",
        "api_key_present": key_exists,
        "fresh_raw_slot": not out.exists(),
        "same_task_branch": subprocess.run(["git", "branch", "--show-current"], cwd=REPO, capture_output=True, text=True, check=True).stdout.strip() == "codex/v1-uapp-progressive-canvas-001",
        "clean_worktree": subprocess.run(["git", "status", "--porcelain"], cwd=REPO, capture_output=True, text=True, check=True).stdout.strip() == "",
    }
    return {"turn": turn, "gate_sha256": sha(GATE), "input_sha256": hashlib.sha256(str(turns[turn]["query"]).encode()).hexdigest(), "checks": checks, "verdict": "PASS" if all(checks.values()) else "FAIL"}


def trace(message_id: str) -> tuple[str, list[dict[str, Any]]]:
    run_id = psql("select coalesce(w.id::text,'') from workflow_runs w join messages m on m.workflow_run_id=w.id where m.id='%s';" % message_id)
    raw = psql("select coalesce(json_agg(json_build_object('idx',e.index,'node_id',e.node_id,'node_type',e.node_type,'status',e.status,'error',e.error,'inputs',e.inputs,'outputs',e.outputs) order by e.index)::text,'[]') from workflow_node_executions e where e.workflow_run_id='%s';" % run_id)
    return run_id, json.loads(raw)


def run(turn: str, conversation_id: str) -> dict[str, Any]:
    pf = preflight(turn)
    if pf["verdict"] != "PASS":
        raise RuntimeError(json.dumps(pf, ensure_ascii=False))
    gate, frozen = load(GATE), load(INPUTS)
    spec = next(item for item in frozen["turns"] if item["id"] == turn)
    if turn == "G2" and not conversation_id:
        raise RuntimeError("G2 requires the G1 conversation id")
    app_id = gate["candidate"]["uapp_app_id"]
    identity = gate["new_formal_identities"]["GAP" if turn in {"G1", "G2"} else turn]
    user = identity["end_user"]
    key = DC.Console(env=DC.load_env(str(ENV))).app_api_key(app_id, create_if_missing=False)
    request = {"inputs": {}, "query": spec["query"], "response_mode": "blocking", "user": user}
    if conversation_id:
        request["conversation_id"] = conversation_id
    started = time.time()
    response = DC.http_json("POST", "/v1/chat-messages", headers={"Authorization": "Bearer " + key}, body=request, timeout=1800)
    elapsed = round(time.time() - started, 3)
    body = response.get("body")
    if isinstance(body, str):
        body = json.loads(body)
    message_id = str((body or {}).get("message_id") or "")
    run_id, nodes = trace(message_id) if message_id else ("", [])
    record = {"document": {"id": "UAPP_AC12_SEMANTIC_HANDOFF_FINAL_BATCH_RAW_v1.1", "turn": turn, "formal": true}, "gate_sha256": sha(GATE), "runner_sha256": sha(Path(__file__)), "preflight": pf, "request": request, "runner_request_attempts": 1, "http_status": response.get("status"), "elapsed_seconds": elapsed, "message_id": message_id, "conversation_id": (body or {}).get("conversation_id"), "workflow_run_id": run_id, "answer": (body or {}).get("answer"), "response_error": (body or {}).get("message") or (body or {}).get("error"), "nodes": nodes}
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    path = RAW_DIR / (turn + ".json")
    with path.open("x", encoding="utf-8") as handle:
        json.dump(record, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    return record


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--preflight", choices=["YAML", "G1", "G2", "FULL_T1"])
    parser.add_argument("--run", choices=["YAML", "G1", "G2", "FULL_T1"])
    parser.add_argument("--conversation-id", default="")
    args = parser.parse_args()
    if bool(args.preflight) == bool(args.run):
        raise SystemExit("choose exactly one of --preflight or --run")
    result = preflight(args.preflight) if args.preflight else run(args.run, args.conversation_id)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
