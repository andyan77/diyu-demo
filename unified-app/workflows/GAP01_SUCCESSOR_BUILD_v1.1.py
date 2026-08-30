#!/usr/bin/env python3
"""Build the single bounded GAP-01 G2 field-projection successor."""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import logging
from pathlib import Path
from types import ModuleType
from typing import Any

LOGGER = logging.getLogger(__name__)
HERE = Path(__file__).resolve().parent
UAPP_ROOT = HERE.parent
UAPP_APP_ID = "85c01f85-a081-43e9-ab09-9993289cc200"
BASE_UAPP_MD5 = "ff411f51a1916c1ea9dfbd96a9841f12"
OUTPUT = UAPP_ROOT / "evidence" / "stages" / "gap01_successor_v1_1" / "build.json"


def load_module(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


BASE = load_module("gap01_v11_build_base", HERE / "GAP01_SUCCESSOR_BUILD_v1.0.py")
NODES = load_module("gap01_v11_build_nodes", HERE / "GAP01_SUCCESSOR_NODES_v1.1.py")


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def patch_uapp(graph: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    candidate = copy.deepcopy(graph)
    before = {node["id"]: node for node in graph["nodes"]}
    nodes = {node["id"]: node for node in candidate["nodes"]}
    fields = nodes["uapp_fields"]["data"]
    code = fields["code"]
    helper_anchor = "\n\ndef main(prev_state_json, task_key, capability_call, gaps_text, target_capability,"
    if code.count(helper_anchor) != 1:
        raise RuntimeError("uapp_fields helper anchor mismatch")
    code = code.replace(helper_anchor, NODES.PROMISE_HELPER + helper_anchor, 1)
    projection_anchor = "    env_vals, env_missing, unspecified = {}, [], []\n"
    if code.count(projection_anchor) != 1:
        raise RuntimeError("uapp_fields projection anchor mismatch")
    code = code.replace(projection_anchor, NODES.PROMISE_PROJECTION + "\n" + projection_anchor, 1)
    fields["code"] = code
    fields["desc"] = "规范字段、产物绑定与用户原文支持的等价承诺投影"

    after = {node["id"]: node for node in candidate["nodes"]}
    touched = sorted(
        node_id for node_id in before if canonical(before[node_id]) != canonical(after[node_id])
    )
    if touched != ["uapp_fields"]:
        raise RuntimeError(f"Unexpected GAP-01 v1.1 impact: {touched}")
    return candidate, touched


def build_report() -> dict[str, Any]:
    if BASE.graph_md5() != BASE_UAPP_MD5:
        raise RuntimeError("Published UAPP differs from frozen GAP-01 successor predecessor")
    if int(BASE.BASE.BASE.psql("select count(*) from workflow_runs where status='running';")) != 0:
        raise RuntimeError("Active workflow exists")
    graph = BASE.published_graph()
    candidate, touched = patch_uapp(graph)
    return {
        "document": {"id": "GAP01_SUCCESSOR_BUILD_v1.1", "model_calls": 0},
        "base_graph_md5": BASE_UAPP_MD5,
        "candidate_canonical_sha256": sha256_text(canonical(candidate)),
        "node_count": len(candidate["nodes"]),
        "edge_count": len(candidate["edges"]),
        "touched_nodes": touched,
        "conversation_variables_added": [],
        "protected_node_count": len(candidate["nodes"]) - len(touched),
    }


def main() -> int:
    if OUTPUT.exists():
        raise FileExistsError(OUTPUT)
    report = build_report()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    LOGGER.info("%s", json.dumps(report, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    raise SystemExit(main())
