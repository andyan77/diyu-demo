#!/usr/bin/env python3
"""Run the single Gate-bound TD-UAPP-24 formal turn.

There is no retry loop. ``--preflight`` is read-only and starts no workflow.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import logging
import os
import time
from types import ModuleType
from typing import Any

HERE = os.path.dirname(os.path.abspath(__file__))
UAPP_ROOT = os.path.abspath(os.path.join(HERE, ".."))
REPO = os.path.abspath(os.path.join(UAPP_ROOT, ".."))
ENV_FILE = "/home/faye/diyu-demo-worktrees/m3-account-content-operator-v1/.env"
GATE_PATH = os.path.join(UAPP_ROOT, "stages", "UAPP_TD24_GATE_v1.0.json")
OUTPUT_PATH = os.path.join(
    UAPP_ROOT,
    "evidence",
    "stages",
    "uapp_td24",
    "UAPP_TD24_RAW_v1.0.json",
)


def load_module(name: str, path: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


OLD_RUN = load_module("uapp_correction_run", os.path.join(HERE, "UAPP_CORRECTION_RUN_v1.0.py"))
BASE = OLD_RUN.BASE
DC = OLD_RUN.DC


def sha256_file(path: str) -> str:
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def published_graph_sha256(app_id: str) -> str:
    graph = json.loads(
        BASE.psql(
            "select w.graph from workflows w join apps a on a.workflow_id=w.id "
            f"where a.id='{app_id}';"
        )
    )
    return sha256_text(canonical(graph))


def load_gate() -> dict[str, Any]:
    with open(GATE_PATH, encoding="utf-8") as handle:
        gate = json.load(handle)
    if gate.get("document", {}).get("id") != "UAPP_TD24_GATE_v1.0":
        raise RuntimeError("Unexpected Gate identity")
    return gate


def preflight() -> dict[str, Any]:
    gate = load_gate()
    candidate = gate["candidate"]
    inputs = gate["formal_turn"]
    console = DC.Console(env=DC.load_env(ENV_FILE))
    api_key_present = bool(
        console.app_api_key(candidate["UAPP"]["app_id"], create_if_missing=False)
    )
    variables = BASE.conversation_variables(inputs["conversation_id"])
    state_raw = variables.get("uapp_task_fields") or ""
    store_raw = variables.get("uapp_last_artifact") or ""
    apps = OLD_RUN.protected_apps()
    git = OLD_RUN.git_state()
    m2 = OLD_RUN.m2_snapshot()
    result = {
        "gate_sha256": sha256_file(GATE_PATH),
        "query_sha256": sha256_text(inputs["query"]),
        "git": git,
        "apps": apps,
        "active_runs": int(BASE.psql("select count(*) from workflow_runs where status='running';")),
        "state_sha256": sha256_text(state_raw),
        "store_sha256": sha256_text(store_raw),
        "state_revision": json.loads(state_raw).get("rev") if state_raw else None,
        "m2": m2,
        "api_key_present": api_key_present,
        "raw_evidence_absent": not os.path.exists(OUTPUT_PATH),
        "uapp_graph_canonical_sha256": published_graph_sha256(candidate["UAPP"]["app_id"]),
    }
    protected_expected = gate["protected_surface_before"]
    checks = {
        "query": result["query_sha256"] == inputs["query_sha256"],
        "git": git["root"] == REPO
        and git["branch"] == "codex/v1-uapp-progressive-canvas-001"
        and git["head"] == git["origin_branch"]
        and git["main"] == git["origin_main"]
        and git["status"] == "",
        "candidate": result["uapp_graph_canonical_sha256"]
        == candidate["UAPP"]["graph_canonical_sha256"],
        "protected": all(
            apps[name]["graph_md5"] == expected
            for name, expected in protected_expected["graph_md5"].items()
        ),
        "no_active_runs": result["active_runs"] == 0,
        "state_identity": result["state_sha256"] == gate["state_before"]["state_sha256"]
        and result["store_sha256"] == gate["state_before"]["store_sha256"]
        and result["state_revision"] == gate["state_before"]["revision"],
        "m2": m2 == gate["protected_surface_before"]["m2"],
        "api_key_present": api_key_present,
        "raw_path": result["raw_evidence_absent"],
        "budget": gate["budget"]["expected_reachable_llm_attempts"]
        <= gate["budget"]["deepseek_llm_node_attempts_max"],
    }
    result["checks"] = checks
    result["verdict"] = "PASS" if all(checks.values()) else "FAIL"
    return result


def run_once() -> int:
    before = preflight()
    if before["verdict"] != "PASS":
        raise RuntimeError(f"Preflight failed: {before['checks']}")
    gate = load_gate()
    turn = gate["formal_turn"]
    app_id = gate["candidate"]["UAPP"]["app_id"]
    console = DC.Console(env=DC.load_env(ENV_FILE))
    api_key = console.app_api_key(app_id, create_if_missing=False)
    if not api_key:
        raise RuntimeError("UAPP API key is absent")

    request = {
        "inputs": {},
        "query": turn["query"],
        "response_mode": "blocking",
        "user": turn["end_user"],
        "conversation_id": turn["conversation_id"],
        "files": [],
    }
    started_at = BASE.psql("select clock_timestamp()::text;")
    started = time.time()
    transport_error = ""
    try:
        response = DC.http_json(
            "POST",
            "/v1/chat-messages",
            headers={"Authorization": f"Bearer {api_key}"},
            body=request,
            timeout=1800,
        )
    except Exception as error:  # noqa: BLE001 - raw evidence must retain transport failures
        transport_error = f"{type(error).__name__}: {error}"
        response = {"status": 0, "body": {"error": transport_error}}
    elapsed = round(time.time() - started, 2)
    body = response.get("body")
    if isinstance(body, str):
        try:
            body = json.loads(body)
        except json.JSONDecodeError:
            body = {"raw": body[:4000]}
    if not isinstance(body, dict):
        body = {"raw": str(body)[:4000]}

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
            "id": "UAPP_TD24_RAW_v1.0",
            "task_id": "DIYU-V1-UNIFIED-DIFY-APPLICATION-001",
            "raw_execution_evidence": True,
            "adjudication": "NOT_PERFORMED_BY_RUNNER",
        },
        "gate_sha256": sha256_file(GATE_PATH),
        "runner_sha256": sha256_file(__file__),
        "preflight": before,
        "window_start": started_at,
        "transport": DC.TRANSPORT,
        "transport_error": transport_error,
        "request": request,
        "request_attempts_by_runner": 1,
        "http_status": response.get("status"),
        "elapsed_seconds": elapsed,
        "message_id": message_id,
        "conversation_id": body.get("conversation_id"),
        "workflow_run_id": top_run_id,
        "answer": body.get("answer"),
        "response_error": body.get("message") or body.get("error"),
        "app_runs_in_window": runs,
        "conversation_variables_after": BASE.conversation_variables(turn["conversation_id"]),
        "protected_apps_after": OLD_RUN.protected_apps(),
        "m2_after": OLD_RUN.m2_snapshot(),
        "git_after": OLD_RUN.git_state(),
    }
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "x", encoding="utf-8") as handle:
        json.dump(evidence, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    logging.info(
        "http=%s elapsed=%ss workflow_run_id=%s transport_error=%s",
        response.get("status"),
        elapsed,
        top_run_id or "-",
        bool(transport_error),
    )
    return 0 if response.get("status") == 200 and not transport_error else 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--preflight", action="store_true")
    parser.add_argument("--run", action="store_true")
    args = parser.parse_args()
    if args.preflight == args.run:
        raise SystemExit("Choose exactly one of --preflight or --run")
    if args.preflight:
        report = preflight()
        logging.info("%s", json.dumps(report, ensure_ascii=False, sort_keys=True))
        return 0 if report["verdict"] == "PASS" else 1
    return run_once()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    raise SystemExit(main())
