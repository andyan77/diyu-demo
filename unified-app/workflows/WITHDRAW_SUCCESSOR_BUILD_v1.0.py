#!/usr/bin/env python3
"""Build or publish the one bounded W1 withdrawal-branch successor."""

from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
from types import ModuleType
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
APP_ID = "85c01f85-a081-43e9-ab09-9993289cc200"
BASE_MD5 = "40a436cdbc11823eca16d2f1c5ecb037"
M2_BASE = "http://diyu-m2-app:8000"
BUILD_OUTPUT = (
    ROOT
    / "evidence"
    / "stages"
    / "s5_final_convergence_v1_0"
    / "withdraw_successor_build.json"
)
PUBLISH_OUTPUT = (
    ROOT
    / "evidence"
    / "stages"
    / "s5_final_convergence_v1_0"
    / "withdraw_successor_publication.json"
)


def load_module(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


PREV = load_module(
    "withdraw_successor_prev", HERE / "WITHDRAW_MATERIAL_REGISTRATION_BUILD_v1.0.py"
)
RUNTIME = PREV.BASE.BASE.BASE.BASE

PARSE_SOURCE = """from __future__ import annotations
import json
from typing import Any

def main(raw: Any, status: Any, expected_material_id: str) -> dict[str, str]:
    if isinstance(raw, str):
        try:
            body = json.loads(raw)
        except (TypeError, ValueError):
            body = {}
    else:
        body = raw if isinstance(raw, dict) else {}
    ok = (str(status) == "200" and body.get("material_id") == expected_material_id
          and bool(body.get("withdrawn_at")))
    return {"ok": "true" if ok else "false",
            "material_id": str(body.get("material_id") or "") if ok else "",
            "already_withdrawn": "true" if body.get("already_withdrawn") is True else "false",
            "withdrawn_at": str(body.get("withdrawn_at") or "") if ok else "",
            "detail": "" if ok else "MATERIAL_WITHDRAWAL_NOT_CONFIRMED"}
"""


def digest(value: Any) -> str:
    return hashlib.sha256(PREV.canonical(value).encode("utf-8")).hexdigest()


def action_gate() -> dict[str, Any]:
    return {
        "type": "if-else",
        "title": "本轮是否撤回刚才的素材",
        "desc": "只在用户明确撤回且会话有精确 material id 时调用撤回接口",
        "selected": False,
        "logical_operator": "and",
        "cases": [
            {
                "case_id": "withdraw",
                "logical_operator": "and",
                "conditions": [
                    {
                        "comparison_operator": "is",
                        "value": "WITHDRAW_MATERIAL",
                        "variable_selector": ["uapp_route", "action"],
                    },
                    {
                        "comparison_operator": "not empty",
                        "value": "",
                        "variable_selector": ["conversation", "uapp_last_material"],
                    },
                ],
            }
        ],
    }


def http_node() -> dict[str, Any]:
    return {
        "type": "http-request",
        "title": "写 M2｜撤回同一素材",
        "desc": "只改变未来复用资格；不删除历史，不触碰真实平台",
        "method": "post",
        "url": M2_BASE
        + "/workspaces/{{#conversation.uapp_ws#}}/materials/{{#conversation.uapp_last_material#}}/withdraw",
        "authorization": {"type": "no-auth", "config": None},
        "headers": "X-Actor-Ref:{{#conversation.uapp_actor#}}",
        "params": "",
        "selected": False,
        "timeout": {"connect": 10, "read": 60, "write": 20},
        "error_strategy": "default-value",
        "default_value": [
            {"key": "body", "type": "string", "value": ""},
            {"key": "status_code", "type": "number", "value": 0},
            {"key": "headers", "type": "object", "value": {}},
            {"key": "files", "type": "array[file]", "value": []},
        ],
        "body": {"type": "none", "data": []},
    }


def result_gate() -> dict[str, Any]:
    return {
        "type": "if-else",
        "title": "撤回是否真实生效",
        "desc": "状态和 material id 一致才确认",
        "selected": False,
        "logical_operator": "and",
        "cases": [
            {
                "case_id": "ok",
                "logical_operator": "and",
                "conditions": [
                    {
                        "comparison_operator": "is",
                        "value": "true",
                        "variable_selector": ["uapp_withdraw_parse", "ok"],
                    }
                ],
            }
        ],
    }


def answer(title: str, text: str) -> dict[str, Any]:
    return {
        "type": "answer",
        "title": title,
        "desc": "只陈述真实副作用，不暴露内部状态",
        "answer": text,
        "variables": [],
        "selected": False,
    }


def patch(graph: dict[str, Any]) -> tuple[dict[str, Any], list[str], list[str]]:
    candidate = copy.deepcopy(graph)
    before = {node["id"]: node for node in graph["nodes"]}
    if "uapp_withdraw_gate" in before:
        raise RuntimeError("Successor already present")
    removed = "uapp_material_gate-false-uapp_m3_gate"
    if sum(edge["id"] == removed for edge in candidate["edges"]) != 1:
        raise RuntimeError("No-file edge anchor mismatch")
    candidate["edges"] = [edge for edge in candidate["edges"] if edge["id"] != removed]
    candidate["nodes"].extend(
        [
            PREV.node("uapp_withdraw_gate", 4840, -280, action_gate()),
            PREV.node("uapp_withdraw_post", 5160, -280, http_node()),
            PREV.node(
                "uapp_withdraw_parse",
                5480,
                -280,
                PREV.code_data(
                    "复核｜撤回素材身份",
                    "响应 material id 和 withdrawn_at 都匹配才确认",
                    PARSE_SOURCE,
                    [
                        PREV.variable("raw", ["uapp_withdraw_post", "body"]),
                        PREV.variable("status", ["uapp_withdraw_post", "status_code"]),
                        PREV.variable(
                            "expected_material_id",
                            ["conversation", "uapp_last_material"],
                        ),
                    ],
                    [
                        "ok",
                        "material_id",
                        "already_withdrawn",
                        "withdrawn_at",
                        "detail",
                    ],
                ),
            ),
            PREV.node("uapp_withdraw_result_gate", 5800, -280, result_gate()),
            PREV.node(
                "uapp_withdraw_ok_answer",
                6120,
                -400,
                answer(
                    "回复｜素材已撤回",
                    "刚才那份素材已经撤回，今后不会再用于新的内容。历史记录仍然保留；"
                    "这次没有影响已经发布的内容，也没有执行任何对外发布或删除。",
                ),
            ),
            PREV.node(
                "uapp_withdraw_fail_answer",
                6120,
                -160,
                answer(
                    "回复｜素材撤回未确认",
                    "这次没有确认素材已经撤回，所以我不会声称处理成功。"
                    "历史记录和已发布内容都没有被删除，也没有执行任何对外操作。",
                ),
            ),
        ]
    )
    types = {node["id"]: node["data"]["type"] for node in candidate["nodes"]}
    candidate["edges"].extend(
        [
            PREV.edge("uapp_material_gate", "uapp_withdraw_gate", "false", types),
            PREV.edge("uapp_withdraw_gate", "uapp_withdraw_post", "withdraw", types),
            PREV.edge("uapp_withdraw_gate", "uapp_m3_gate", "false", types),
            PREV.edge("uapp_withdraw_post", "uapp_withdraw_parse", "source", types),
            PREV.edge(
                "uapp_withdraw_parse", "uapp_withdraw_result_gate", "source", types
            ),
            PREV.edge(
                "uapp_withdraw_result_gate", "uapp_withdraw_ok_answer", "ok", types
            ),
            PREV.edge(
                "uapp_withdraw_result_gate", "uapp_withdraw_fail_answer", "false", types
            ),
        ]
    )
    after = {node["id"]: node for node in candidate["nodes"]}
    if any(PREV.canonical(before[key]) != PREV.canonical(after[key]) for key in before):
        raise RuntimeError("Existing node changed")
    return (
        candidate,
        sorted(set(after) - set(before)),
        sorted(
            edge["id"]
            for edge in candidate["edges"]
            if edge["id"] not in {old["id"] for old in graph["edges"]}
        ),
    )


def build() -> tuple[dict[str, Any], dict[str, Any]]:
    if PREV.BASE.BASE.graph_md5() != BASE_MD5:
        raise RuntimeError("Published predecessor drift")
    if (
        int(RUNTIME.psql("select count(*) from workflow_runs where status='running';"))
        != 0
    ):
        raise RuntimeError("Active workflow exists")
    graph, nodes, edges = patch(PREV.BASE.BASE.published_graph())
    report = {
        "document": {"id": "WITHDRAW_SUCCESSOR_BUILD_v1.0", "model_calls": 0},
        "base_graph_md5": BASE_MD5,
        "candidate_canonical_sha256": digest(graph),
        "node_count": len(graph["nodes"]),
        "edge_count": len(graph["edges"]),
        "added_nodes": nodes,
        "added_edges": edges,
        "removed_edges": ["uapp_material_gate-false-uapp_m3_gate"],
    }
    return graph, report


def publish(graph: dict[str, Any], report: dict[str, Any]) -> None:
    console = RUNTIME.DC.Console(env=RUNTIME.DC.load_env(RUNTIME.ENV_FILE))
    draft = RUNTIME.console_call(
        console, "GET", f"/console/api/apps/{APP_ID}/workflows/draft"
    )
    RUNTIME.console_call(
        console,
        "POST",
        f"/console/api/apps/{APP_ID}/workflows/draft",
        {
            "graph": graph,
            "features": draft.get("features") or {},
            "hash": draft.get("hash"),
            "environment_variables": draft.get("environment_variables") or [],
            "conversation_variables": list(
                PREV.published_conversation_variables().values()
            ),
        },
    )
    response = RUNTIME.console_call(
        console,
        "POST",
        f"/console/api/apps/{APP_ID}/workflows/publish",
        {
            "marked_name": "s5-withdraw-v2",
            "marked_comment": "Exact W0 material withdrawal successor",
        },
    )
    readback = PREV.BASE.BASE.published_graph()
    if PREV.canonical(readback) != PREV.canonical(graph):
        raise RuntimeError("Published graph differs")
    result = {
        **report,
        "response": response,
        "published_graph_md5": PREV.BASE.BASE.graph_md5(),
        "published_canonical_sha256": digest(readback),
    }
    PUBLISH_OUTPUT.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--publish", action="store_true")
    args = parser.parse_args()
    graph, report = build()
    if args.publish:
        publish(graph, report)
    else:
        BUILD_OUTPUT.write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
