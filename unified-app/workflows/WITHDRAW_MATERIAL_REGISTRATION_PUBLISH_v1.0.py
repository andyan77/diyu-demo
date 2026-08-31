#!/usr/bin/env python3
"""Publish and read back the bounded UAPP material-registration candidate."""

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
    / "track_a_publication.json"
)


def load_module(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


BUILD = load_module(
    "withdraw_material_publish_build", HERE / "WITHDRAW_MATERIAL_REGISTRATION_BUILD_v1.0.py"
)
RUNTIME = BUILD.BASE.BASE.BASE.BASE


def console_call(
    console: Any,
    method: str,
    path: str,
    body: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return RUNTIME.console_call(console, method, path, body)


def main() -> int:
    if OUTPUT.exists():
        raise FileExistsError(OUTPUT)
    if BUILD.BASE.BASE.graph_md5() != BUILD.BASE_UAPP_MD5:
        raise RuntimeError("Published UAPP predecessor drift")
    if int(RUNTIME.psql("select count(*) from workflow_runs where status='running';")) != 0:
        raise RuntimeError("Active workflow exists")
    if BUILD.BASE.BASE.BASE.BASE.psql(
        "select count(*) from workflow_runs where status='running';"
    ) != "0":
        raise RuntimeError("Dify active workflow guard mismatch")
    graph, added_nodes, added_edges = BUILD.patch_uapp(BUILD.BASE.BASE.published_graph())
    conversation_variables = BUILD.patch_conversation_variables(
        BUILD.published_conversation_variables()
    )
    console = RUNTIME.DC.Console(env=RUNTIME.DC.load_env(RUNTIME.ENV_FILE))
    draft = console_call(
        console, "GET", f"/console/api/apps/{BUILD.UAPP_APP_ID}/workflows/draft"
    )
    console_call(
        console,
        "POST",
        f"/console/api/apps/{BUILD.UAPP_APP_ID}/workflows/draft",
        {
            "graph": graph,
            "features": draft.get("features") or {},
            "hash": draft.get("hash"),
            "environment_variables": draft.get("environment_variables") or [],
            "conversation_variables": list(conversation_variables.values()),
        },
    )
    draft_readback = console_call(
        console, "GET", f"/console/api/apps/{BUILD.UAPP_APP_ID}/workflows/draft"
    )
    if BUILD.canonical(draft_readback["graph"]) != BUILD.canonical(graph):
        raise RuntimeError("Draft graph readback differs")
    response = console_call(
        console,
        "POST",
        f"/console/api/apps/{BUILD.UAPP_APP_ID}/workflows/publish",
        {
            "marked_name": "s5-matreg-v1",
            "marked_comment": "Exact test-scoped upload-to-M2 material registration seam",
        },
    )
    graph_readback = BUILD.BASE.BASE.published_graph()
    variables_readback = BUILD.published_conversation_variables()
    if BUILD.canonical(graph_readback) != BUILD.canonical(graph):
        raise RuntimeError("Published graph readback differs")
    if BUILD.canonical(variables_readback) != BUILD.canonical(conversation_variables):
        raise RuntimeError("Published conversation variables differ")
    report = {
        "document": {"id": "WITHDRAW_MATERIAL_REGISTRATION_PUBLICATION_v1.0", "model_calls": 0},
        "response": response,
        "published_graph_md5": BUILD.BASE.BASE.graph_md5(),
        "canonical_sha256": BUILD.sha256_text(BUILD.canonical(graph_readback)),
        "conversation_variables_sha256": BUILD.sha256_text(BUILD.canonical(variables_readback)),
        "node_count": len(graph_readback["nodes"]),
        "edge_count": len(graph_readback["edges"]),
        "added_nodes": added_nodes,
        "added_edges": added_edges,
        "conversation_variables_added": ["uapp_material_binding"],
    }
    OUTPUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
