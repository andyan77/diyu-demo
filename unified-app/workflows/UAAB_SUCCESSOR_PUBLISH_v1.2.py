#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Publish the frozen UAAB v1.2 UAPP candidate and existing PP b2. Zero model calls."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import logging
import os
import subprocess
from types import ModuleType
from typing import Any

HERE = os.path.dirname(os.path.abspath(__file__))
UAPP_ROOT = os.path.abspath(os.path.join(HERE, ".."))
REPO = os.path.abspath(os.path.join(UAPP_ROOT, ".."))
EVIDENCE_DIR = os.path.join(UAPP_ROOT, "evidence", "stages", "uapp_artifact_binding")
ENV_FILE = "/home/faye/diyu-demo-worktrees/m3-account-content-operator-v1/.env"

UAPP_APP_ID = "85c01f85-a081-43e9-ab09-9993289cc200"
PP_APP_ID = "c9cdea24-9df3-400b-9ecd-1d740e8c96df"
PP_PROVIDER_ID = "21a000b1-5d14-42e9-b380-64c2c2aa16a0"
SEAM_APP_ID = "5fca0162-e26b-4545-a00b-66b1a2a2a077"
HOP_APP_ID = "6c46fdb1-5f49-4513-a0c0-29957b3dcee4"

UAPP_STABLE_MD5 = "99c3edf7bd12172a4fb011b588f25e57"
UAPP_CANDIDATE_CANONICAL_SHA256 = "75c0afbeb6f9bacba514b221702d113cbca7dcfb5dd857b594945f552e9d3ef7"
PP_STABLE_MD5 = "788c8555aca09e6fa6d979f237f70157"
PP_B2_MD5 = "8366328bf827bd0f460455d750d45c4f"
SEAM_MD5 = "db49a3da8973d4fdcbe9ecf63bdf7e2a"
HOP_MD5 = "e38378c3c2a66b75aa7e645368c9e1ce"
GATE_SHA256 = "dbe4c023256e378d93827094b5c762f7c1b67b1c7528fff92fbbb84b219ea622"

PP_B2_SKILL = os.path.join(REPO, "content-production", "skills", "packaging-content-for-release-m4-b2", "SKILL.md")
PP_M4_SKILL = os.path.join(REPO, "content-production", "skills", "packaging-content-for-release-m4", "SKILL.md")


def load_module(name: str, path: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


DC = load_module("dify_client", os.path.join(REPO, "account-operations", "tools", "dify_client.py"))


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def sha256_file(path: str) -> str:
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


def psql(sql: str, db: str = "dify") -> str:
    completed = subprocess.run(
        ["docker", "exec", "-i", "docker-db_postgres-1", "psql", "-U", "postgres", "-d", db, "-tA", "-c", sql],
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(f"psql failed: {(completed.stderr or '')[:300]}")
    return completed.stdout.strip()


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
        f"where p.id='{PP_PROVIDER_ID}';"
    )
    return json.loads(raw)


def frozen_surfaces() -> dict[str, Any]:
    return {
        "uapp": app_state(UAPP_APP_ID),
        "pp": app_state(PP_APP_ID),
        "provider": provider_state(),
        "seam": app_state(SEAM_APP_ID),
        "hop": app_state(HOP_APP_ID),
        "active_runs": int(psql("select count(*) from workflow_runs where status='running';")),
    }


def read_draft(console: Any, app_id: str) -> dict[str, Any]:
    status, draft = console.call("GET", f"/console/api/apps/{app_id}/workflows/draft", timeout=300)
    if status != 200:
        raise RuntimeError(f"draft read failed for {app_id}: {status} {str(draft)[:300]}")
    return draft


def pp_b2_payload(draft: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    graph = json.loads(canonical(draft["graph"]))
    before_nodes = json.loads(canonical(graph["nodes"]))
    before_edges = json.loads(canonical(graph["edges"]))
    node = next((item for item in graph["nodes"] if item.get("id") == "skill_llm"), None)
    if node is None:
        raise RuntimeError("PP skill_llm node not found")
    prompt_templates = node["data"]["prompt_template"]
    system_indexes = [index for index, prompt in enumerate(prompt_templates) if prompt.get("role") == "system"]
    if len(system_indexes) != 1:
        raise RuntimeError(f"PP system prompt count is {len(system_indexes)}")
    old_system = prompt_templates[system_indexes[0]]["text"]
    with open(PP_M4_SKILL, encoding="utf-8") as handle:
        m4_skill = handle.read()
    with open(PP_B2_SKILL, encoding="utf-8") as handle:
        b2_skill = handle.read()
    if not old_system.startswith(m4_skill):
        raise RuntimeError("PP stable draft system prompt is not based on the frozen M4 source")
    injection_tail = old_system[len(m4_skill) :]
    prompt_templates[system_indexes[0]]["text"] = b2_skill + injection_tail

    touched = [
        after.get("id")
        for before, after in zip(before_nodes, graph["nodes"], strict=True)
        if canonical(before) != canonical(after)
    ]
    if touched != ["skill_llm"] or canonical(before_edges) != canonical(graph["edges"]):
        raise RuntimeError(f"PP b2 impact surface mismatch: touched={touched}")
    payload = {
        "graph": graph,
        "features": draft.get("features") or {},
        "hash": draft.get("hash"),
        "environment_variables": draft.get("environment_variables") or [],
        "conversation_variables": draft.get("conversation_variables") or [],
    }
    evidence = {
        "nodes_touched": touched,
        "edges_unchanged": True,
        "system_prompt_sha256": sha256_text(prompt_templates[system_indexes[0]]["text"]),
        "b2_skill_sha256": sha256_text(b2_skill),
        "injection_tail_sha256": sha256_text(injection_tail),
        "node_count": len(graph["nodes"]),
        "edge_count": len(graph["edges"]),
    }
    return payload, evidence


def call_or_raise(console: Any, method: str, path: str, body: dict[str, Any]) -> tuple[int, Any]:
    status, response = console.call(method, path, body=body, timeout=900)
    if status not in (200, 201):
        raise RuntimeError(f"{method} {path} failed: {status} {str(response)[:400]}")
    return status, response


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--preflight", action="store_true")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    if not (args.preflight or args.apply) or (args.preflight and args.apply):
        raise SystemExit("Choose exactly one of --preflight or --apply")

    gate_path = os.path.join(UAPP_ROOT, "stages", "UAAB_GATE_v1.2.json")
    if sha256_file(gate_path) != GATE_SHA256:
        raise RuntimeError("successor Gate hash mismatch")

    before = frozen_surfaces()
    if before["uapp"]["graph_md5"] != UAPP_STABLE_MD5:
        raise RuntimeError("UAPP published surface is not stable before publish")
    if before["pp"]["graph_md5"] != PP_STABLE_MD5 or before["provider"]["graph_md5"] != PP_STABLE_MD5:
        raise RuntimeError("PP/provider surface is not stable before publish")
    if before["seam"]["graph_md5"] != SEAM_MD5 or before["hop"]["graph_md5"] != HOP_MD5:
        raise RuntimeError("Seam or Hop drifted before publish")
    if before["active_runs"] != 0:
        raise RuntimeError("active workflows exist before publish")

    console = DC.Console(env=DC.load_env(ENV_FILE))
    uapp_draft = read_draft(console, UAPP_APP_ID)
    if sha256_text(canonical(uapp_draft["graph"])) != UAPP_CANDIDATE_CANONICAL_SHA256:
        raise RuntimeError("UAPP draft identity differs from the frozen Gate")
    pp_draft = read_draft(console, PP_APP_ID)
    pp_payload, pp_build = pp_b2_payload(pp_draft)

    report: dict[str, Any] = {
        "document": {
            "id": "UAAB_SUCCESSOR_PUBLISH_v1.2",
            "task_id": "DIYU-V1-UAPP-ACCEPTED-ARTIFACT-BINDING-001",
            "gate_sha256": GATE_SHA256,
            "model_calls": 0,
            "direct_db_updates": 0,
        },
        "before": before,
        "uapp_draft": {
            "canonical_sha256": UAPP_CANDIDATE_CANONICAL_SHA256,
            "nodes": len(uapp_draft["graph"]["nodes"]),
            "edges": len(uapp_draft["graph"]["edges"]),
        },
        "pp_b2_build": pp_build,
        "applied": False,
    }

    if args.apply:
        uapp_status, _ = call_or_raise(
            console,
            "POST",
            f"/console/api/apps/{UAPP_APP_ID}/workflows/publish",
            {"marked_name": "uaab-v12-test", "marked_comment": "UAAB v1.2 frozen successor candidate"},
        )
        call_or_raise(console, "POST", f"/console/api/apps/{PP_APP_ID}/workflows/draft", pp_payload)
        pp_status, _ = call_or_raise(
            console,
            "POST",
            f"/console/api/apps/{PP_APP_ID}/workflows/publish",
            {"marked_name": "pp-b2-uaab-v12", "marked_comment": "Existing PP b2 republished for UAAB v1.2"},
        )

        provider_status, provider_tool = console.call(
            "GET",
            f"/console/api/workspaces/current/tool-provider/workflow/get?workflow_app_id={PP_APP_ID}",
            timeout=300,
        )
        if provider_status != 200:
            raise RuntimeError(f"provider read failed: {provider_status} {str(provider_tool)[:300]}")
        provider_payload = {
            "workflow_tool_id": provider_tool["workflow_tool_id"],
            "name": provider_tool["name"],
            "label": provider_tool["label"],
            "icon": provider_tool["icon"],
            "description": provider_tool["description"],
            "parameters": provider_tool["parameters"],
            "privacy_policy": provider_tool.get("privacy_policy") or "",
            "labels": [
                label["name"] if isinstance(label, dict) else label
                for label in (provider_tool.get("tool") or {}).get("labels", [])
            ],
        }
        provider_update_status, _ = call_or_raise(
            console,
            "POST",
            "/console/api/workspaces/current/tool-provider/workflow/update",
            provider_payload,
        )
        after = frozen_surfaces()
        uapp_graph = json.loads(
            psql(
                "select w.graph from workflows w join apps a on a.workflow_id=w.id "
                f"where a.id='{UAPP_APP_ID}';"
            )
        )
        after["uapp"]["canonical_sha256"] = sha256_text(canonical(uapp_graph))
        if after["uapp"]["canonical_sha256"] != UAPP_CANDIDATE_CANONICAL_SHA256:
            raise RuntimeError("published UAPP graph differs from the frozen candidate")
        if after["pp"]["graph_md5"] != PP_B2_MD5 or after["provider"]["graph_md5"] != PP_B2_MD5:
            raise RuntimeError("published PP or provider is not the existing b2 graph")
        if after["seam"]["graph_md5"] != SEAM_MD5 or after["hop"]["graph_md5"] != HOP_MD5:
            raise RuntimeError("Seam or Hop drifted during publish")
        if after["active_runs"] != 0:
            raise RuntimeError("active workflows exist after publish")
        report["applied"] = True
        report["api_status"] = {
            "uapp_publish": uapp_status,
            "pp_publish": pp_status,
            "provider_update": provider_update_status,
        }
        report["after"] = after
        report["history_rows"] = {
            "uapp": int(psql(f"select count(*) from workflows where app_id='{UAPP_APP_ID}';")),
            "pp": int(psql(f"select count(*) from workflows where app_id='{PP_APP_ID}';")),
            "pp_b2": int(
                psql(
                    f"select count(*) from workflows where app_id='{PP_APP_ID}' and md5(graph)='{PP_B2_MD5}';"
                )
            ),
        }

    os.makedirs(EVIDENCE_DIR, exist_ok=True)
    evidence_path = os.path.join(EVIDENCE_DIR, "UAAB_SUCCESSOR_PUBLISH_v1.2.json")
    with open(evidence_path, "w", encoding="utf-8") as handle:
        json.dump(report, handle, ensure_ascii=False, indent=1)
        handle.write("\n")
    logging.info("%s", json.dumps(report, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    raise SystemExit(main())
