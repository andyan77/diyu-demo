#!/usr/bin/env python3
"""Publish and read back the frozen GAP-01 UAPP successor candidate."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from types import ModuleType
from typing import Any

HERE = Path(__file__).resolve().parent
UAPP_ROOT = HERE.parent
OUTPUT = UAPP_ROOT / "evidence" / "stages" / "gap01_successor_v1_0" / "publication.json"


def load_module(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


BUILD = load_module("gap01_publish_build", HERE / "GAP01_SUCCESSOR_BUILD_v1.0.py")


def console_call(console: Any, method: str, path: str, body: dict[str, Any] | None = None) -> dict[str, Any]:
    return BUILD.BASE.console_call(console, method, path, body)


def publish(graph: dict[str, Any]) -> dict[str, Any]:
    console = BUILD.BASE.DC.Console(env=BUILD.BASE.DC.load_env(BUILD.ENV_FILE))
    draft = console_call(console, "GET", f"/console/api/apps/{BUILD.UAPP_APP_ID}/workflows/draft")
    console_call(
        console,
        "POST",
        f"/console/api/apps/{BUILD.UAPP_APP_ID}/workflows/draft",
        {
            "graph": graph,
            "features": draft.get("features") or {},
            "hash": draft.get("hash"),
            "environment_variables": draft.get("environment_variables") or [],
            "conversation_variables": draft.get("conversation_variables") or [],
        },
    )
    readback = console_call(console, "GET", f"/console/api/apps/{BUILD.UAPP_APP_ID}/workflows/draft")
    if BUILD.canonical(readback["graph"]) != BUILD.canonical(graph):
        raise RuntimeError("Draft readback differs")
    return console_call(
        console,
        "POST",
        f"/console/api/apps/{BUILD.UAPP_APP_ID}/workflows/publish",
        {"marked_name": "gap01-v1", "marked_comment": "GAP-01 decisive route question successor"},
    )


def main() -> int:
    if OUTPUT.exists():
        raise FileExistsError(OUTPUT)
    if BUILD.graph_md5() != BUILD.BASE_UAPP_MD5:
        raise RuntimeError("UAPP predecessor drift")
    if int(BUILD.BASE.BASE.psql("select count(*) from workflow_runs where status='running';")) != 0:
        raise RuntimeError("Active workflow exists")
    before_apps = BUILD.BASE.BASE_STATE.protected_apps() if hasattr(BUILD.BASE, "BASE_STATE") else None
    candidate, touched = BUILD.patch_uapp(BUILD.published_graph())
    response = publish(candidate)
    readback = BUILD.published_graph()
    if BUILD.canonical(readback) != BUILD.canonical(candidate):
        raise RuntimeError("Published graph readback mismatch")
    report = {
        "document": {"id": "GAP01_SUCCESSOR_PUBLICATION_v1.0", "model_calls": 0},
        "response": response,
        "published_graph_md5": BUILD.graph_md5(),
        "canonical_sha256": BUILD.sha256_text(BUILD.canonical(readback)),
        "node_count": len(readback["nodes"]),
        "edge_count": len(readback["edges"]),
        "touched_nodes": touched,
        "before_apps_optional": before_apps,
    }
    OUTPUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
