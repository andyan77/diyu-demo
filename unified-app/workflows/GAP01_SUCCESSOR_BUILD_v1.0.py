#!/usr/bin/env python3
"""Build the bounded UAPP GAP-01 decisive-question successor."""

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
ENV_FILE = "/home/faye/diyu-demo-worktrees/m3-account-content-operator-v1/.env"
UAPP_APP_ID = "85c01f85-a081-43e9-ab09-9993289cc200"
BASE_UAPP_MD5 = "7932502949d91ad366a4fa70d39a8a56"
OUTPUT = UAPP_ROOT / "evidence" / "stages" / "gap01_successor_v1_0" / "build.json"


def load_module(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


BASE = load_module("gap01_build_base", HERE / "CAP06_SEMANTIC_CONTRACT_BUILD_v1.0.py")
NODES = load_module("gap01_build_nodes", HERE / "GAP01_SUCCESSOR_NODES_v1.0.py")


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def graph_md5() -> str:
    return BASE.graph_md5(UAPP_APP_ID)


def published_graph() -> dict[str, Any]:
    return BASE.published_graph(UAPP_APP_ID)


def patch_uapp(graph: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    candidate = copy.deepcopy(graph)
    before = {node["id"]: node for node in graph["nodes"]}
    nodes = {node["id"]: node for node in candidate["nodes"]}

    action = nodes["uapp_action"]["data"]
    prompt = action["prompt_template"][0]["text"]
    if "模糊内容请求的决定性分叉" in prompt:
        raise RuntimeError("GAP-01 action prompt is already patched")
    action["prompt_template"][0]["text"] = prompt + NODES.ACTION_PROMPT_APPEND
    action["desc"] = "自然语言能力分诊；模糊内容委托先问会改变路线的一个问题"

    route = nodes["uapp_route"]["data"]
    code = route["code"]
    helper_anchor = '\n\ndef main(call_intent_json, snapshot_json, user_query, ws_id, conv_id, action_patch=None,'
    if code.count(helper_anchor) != 1:
        raise RuntimeError("Route helper anchor mismatch")
    code = code.replace(helper_anchor, NODES.ROUTE_HELPER + helper_anchor, 1)
    override_anchor = '    decisive_q = (ap.get("decisive_question_text") or "").strip()\n'
    if code.count(override_anchor) != 1:
        raise RuntimeError("Route decisive-question anchor mismatch")
    code = code.replace(override_anchor, override_anchor + NODES.ROUTE_OVERRIDE, 1)
    old_business = '    runs_business = mode != "DIALOGUE"'
    new_business = '    runs_business = mode not in ("DIALOGUE", "ASK_ONE")'
    if code.count(old_business) != 1:
        raise RuntimeError("Route business-branch anchor mismatch")
    route["code"] = code.replace(old_business, new_business, 1)
    route["desc"] = "能力选择前先处理会改变路线的真实分叉；节点位置不属于产品判据"

    after = {node["id"]: node for node in candidate["nodes"]}
    touched = sorted(
        node_id for node_id in before if canonical(before[node_id]) != canonical(after[node_id])
    )
    if touched != ["uapp_action", "uapp_route"]:
        raise RuntimeError(f"Unexpected GAP-01 impact: {touched}")
    return candidate, touched


def build_report() -> dict[str, Any]:
    if graph_md5() != BASE_UAPP_MD5:
        raise RuntimeError("Published UAPP differs from frozen GAP-01 predecessor")
    if int(BASE.BASE.psql("select count(*) from workflow_runs where status='running';")) != 0:
        raise RuntimeError("Active workflow exists")
    graph = published_graph()
    candidate, touched = patch_uapp(graph)
    return {
        "document": {"id": "GAP01_SUCCESSOR_BUILD_v1.0", "model_calls": 0},
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
