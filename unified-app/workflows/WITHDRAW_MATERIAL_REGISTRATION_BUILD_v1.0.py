#!/usr/bin/env python3
"""Build the bounded UAPP material-registration successor without publishing it."""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import logging
import uuid
from pathlib import Path
from types import ModuleType
from typing import Any

LOGGER = logging.getLogger(__name__)
HERE = Path(__file__).resolve().parent
UAPP_ROOT = HERE.parent
UAPP_APP_ID = "85c01f85-a081-43e9-ab09-9993289cc200"
BASE_UAPP_MD5 = "aa32b6385de0024d270ec9f85bd78179"
OUTPUT = UAPP_ROOT / "evidence" / "stages" / "s5_final_convergence_v1_0" / "track_a_build.json"
M2_BASE = "http://diyu-m2-app:8000"


def load_module(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


BASE = load_module("withdraw_build_base", HERE / "GAP01_SUCCESSOR_BUILD_v1.1.py")
NODES = load_module("withdraw_build_nodes", HERE / "WITHDRAW_MATERIAL_REGISTRATION_NODES_v1.0.py")


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def node(node_id: str, x: int, y: int, data: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": node_id,
        "position": {"x": x, "y": y},
        "positionAbsolute": {"x": x, "y": y},
        "selected": False,
        "sourcePosition": "right",
        "targetPosition": "left",
        "type": "custom",
        "width": 244,
        "height": 98,
        "zIndex": 0,
        "data": data,
    }


def code_data(
    title: str,
    description: str,
    source: str,
    variables: list[dict[str, Any]],
    outputs: list[str],
) -> dict[str, Any]:
    return {
        "type": "code",
        "title": title,
        "desc": description,
        "code_language": "python3",
        "code": source,
        "variables": variables,
        "outputs": {name: {"type": "string", "children": None} for name in outputs},
        "selected": False,
    }


def variable(name: str, selector: list[str]) -> dict[str, Any]:
    return {"variable": name, "value_selector": selector}


def if_else(title: str, description: str, cases: list[tuple[str, str]]) -> dict[str, Any]:
    return {
        "type": "if-else",
        "title": title,
        "desc": description,
        "selected": False,
        "logical_operator": "and",
        "cases": [
            {
                "case_id": case_id,
                "logical_operator": "and",
                "conditions": [
                    {
                        "comparison_operator": "is",
                        "value": expected,
                        "variable_selector": ["uapp_material_prepare", "decision"],
                    }
                ],
            }
            for case_id, expected in cases
        ],
    }


def result_if_else() -> dict[str, Any]:
    return {
        "type": "if-else",
        "title": "素材登记成功吗",
        "desc": "只有响应身份、scope 和权限逐项复核成功才继续",
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
                        "variable_selector": ["uapp_material_parse", "ok"],
                    }
                ],
            }
        ],
    }


def http_data() -> dict[str, Any]:
    return {
        "type": "http-request",
        "title": "写 M2｜登记本轮上传素材",
        "desc": "只登记测试域身份、权限和内容引用，不存第二份正文",
        "method": "post",
        "url": M2_BASE + "/workspaces/{{#conversation.uapp_ws#}}/materials",
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
        "body": {
            "type": "json",
            "data": [
                {"key": "", "type": "text", "value": "{{#uapp_material_prepare.request_body#}}"}
            ],
        },
    }


def assigner_data() -> dict[str, Any]:
    return {
        "type": "assigner",
        "version": "2",
        "title": "记住｜本轮素材绑定",
        "desc": "保存 M2 material id 与可复算绑定，供同会话幂等和精确撤回",
        "selected": False,
        "items": [
            {
                "input_type": "variable",
                "operation": "over-write",
                "write_mode": "over-write",
                "value": ["uapp_material_parse", "material_id"],
                "variable_selector": ["conversation", "uapp_last_material"],
            },
            {
                "input_type": "variable",
                "operation": "over-write",
                "write_mode": "over-write",
                "value": ["uapp_material_parse", "binding_json"],
                "variable_selector": ["conversation", "uapp_material_binding"],
            },
        ],
    }


def edge(
    source: str,
    target: str,
    handle: str,
    node_types: dict[str, str],
) -> dict[str, Any]:
    return {
        "id": f"{source}-{handle}-{target}",
        "type": "custom",
        "source": source,
        "target": target,
        "sourceHandle": handle,
        "targetHandle": "target",
        "zIndex": 0,
        "data": {
            "isInIteration": False,
            "isInLoop": False,
            "sourceType": node_types[source],
            "targetType": node_types[target],
        },
    }


def patch_uapp(graph: dict[str, Any]) -> tuple[dict[str, Any], list[str], list[str]]:
    candidate = copy.deepcopy(graph)
    before_nodes = {item["id"]: item for item in graph["nodes"]}
    if "uapp_material_prepare" in before_nodes:
        raise RuntimeError("Material-registration successor already present")
    direct_edge = "uapp_ctx-source-uapp_m3_gate"
    if sum(item["id"] == direct_edge for item in candidate["edges"]) != 1:
        raise RuntimeError("uapp_ctx direct edge anchor mismatch")
    candidate["edges"] = [item for item in candidate["edges"] if item["id"] != direct_edge]
    additions = [
        node(
            "uapp_material_prepare",
            4200,
            -520,
            code_data(
                "识别｜本轮上传素材绑定",
                "一个文件、当前 task scope、可复算 hash 和幂等键；无文件不执行",
                NODES.PREPARE_SRC,
                [
                    variable("files", ["sys", "files"]),
                    variable("material_text", ["m1_join", "material_text"]),
                    variable("workspace_id", ["conversation", "uapp_ws"]),
                    variable("account_id", ["conversation", "uapp_account"]),
                    variable("task_id", ["conversation", "uapp_task"]),
                    variable("actor_ref", ["conversation", "uapp_actor"]),
                    variable("previous_binding_json", ["conversation", "uapp_material_binding"]),
                ],
                [
                    "decision",
                    "request_body",
                    "binding_seed",
                    "idempotency_key",
                    "file_hash",
                    "file_name",
                    "upload_id",
                    "detail",
                ],
            ),
        ),
        node(
            "uapp_material_gate",
            4520,
            -520,
            if_else(
                "本轮素材如何处理",
                "新文件登记；同 task 同幂等键复用；身份不完整 fail-closed",
                [("register", "REGISTER"), ("reuse", "REUSE"), ("invalid", "INVALID")],
            ),
        ),
        node("uapp_material_post", 4840, -760, http_data()),
        node(
            "uapp_material_parse",
            5160,
            -760,
            code_data(
                "复核｜素材登记身份与权限",
                "M2 响应与请求的 workspace/task/account/hash/权限逐项一致才算登记成功",
                NODES.PARSE_SRC,
                [
                    variable("raw", ["uapp_material_post", "body"]),
                    variable("status", ["uapp_material_post", "status_code"]),
                    variable("binding_seed_json", ["uapp_material_prepare", "binding_seed"]),
                ],
                ["ok", "material_id", "binding_json", "detail"],
            ),
        ),
        node("uapp_material_result_gate", 5480, -760, result_if_else()),
        node("uapp_material_assign", 5800, -760, assigner_data()),
        node(
            "uapp_material_fail_answer",
            5800,
            -400,
            {
                "type": "answer",
                "title": "回复｜素材没有登记成功",
                "desc": "fail-closed，不暴露内部字段或声称已保存",
                "answer": (
                    "这份资料我已经收到，但这次没有成功保存为后续可用的素材，所以先不继续往下处理。"
                    "目前没有产生发布或其他外部动作。"
                ),
                "variables": [],
                "selected": False,
            },
        ),
    ]
    candidate["nodes"].extend(additions)
    node_types = {item["id"]: item["data"]["type"] for item in candidate["nodes"]}
    candidate["edges"].extend(
        [
            edge("uapp_ctx", "uapp_material_prepare", "source", node_types),
            edge("uapp_material_prepare", "uapp_material_gate", "source", node_types),
            edge("uapp_material_gate", "uapp_material_post", "register", node_types),
            edge("uapp_material_post", "uapp_material_parse", "source", node_types),
            edge("uapp_material_parse", "uapp_material_result_gate", "source", node_types),
            edge("uapp_material_result_gate", "uapp_material_assign", "ok", node_types),
            edge("uapp_material_assign", "uapp_m3_gate", "source", node_types),
            edge("uapp_material_result_gate", "uapp_material_fail_answer", "false", node_types),
            edge("uapp_material_gate", "uapp_material_fail_answer", "invalid", node_types),
            edge("uapp_material_gate", "uapp_m3_gate", "reuse", node_types),
            edge("uapp_material_gate", "uapp_m3_gate", "false", node_types),
        ]
    )
    after_nodes = {item["id"]: item for item in candidate["nodes"]}
    changed_existing = sorted(
        node_id
        for node_id in before_nodes
        if canonical(before_nodes[node_id]) != canonical(after_nodes[node_id])
    )
    if changed_existing:
        raise RuntimeError(f"Existing nodes changed: {changed_existing}")
    added_nodes = sorted(set(after_nodes) - set(before_nodes))
    added_edges = sorted(
        item["id"] for item in candidate["edges"] if item["id"] not in {e["id"] for e in graph["edges"]}
    )
    return candidate, added_nodes, added_edges


def patch_conversation_variables(values: dict[str, Any]) -> dict[str, Any]:
    candidate = copy.deepcopy(values)
    if "uapp_material_binding" in candidate:
        raise RuntimeError("uapp_material_binding already exists")
    variable_id = str(uuid.uuid5(uuid.NAMESPACE_URL, "diyu:uapp:conversation:uapp_material_binding"))
    candidate["uapp_material_binding"] = {
        "value_type": "string",
        "value": "",
        "id": variable_id,
        "name": "uapp_material_binding",
        "description": "本会话最近上传素材的 task/upload/hash/idempotency 绑定；正文不在此保存。",
        "selector": ["conversation", "uapp_material_binding"],
    }
    return candidate


def published_conversation_variables() -> dict[str, Any]:
    raw = BASE.BASE.BASE.BASE.psql(
        "select conversation_variables from workflows w join apps a on a.workflow_id=w.id "
        f"where a.id='{UAPP_APP_ID}';"
    )
    parsed = json.loads(raw)
    if not isinstance(parsed, dict):
        raise RuntimeError("Conversation variables are not an object")
    return parsed


def build_report() -> dict[str, Any]:
    if BASE.BASE.graph_md5() != BASE_UAPP_MD5:
        raise RuntimeError("Published UAPP differs from frozen predecessor")
    if int(BASE.BASE.BASE.BASE.psql("select count(*) from workflow_runs where status='running';")) != 0:
        raise RuntimeError("Active workflow exists")
    base_graph = BASE.BASE.published_graph()
    candidate, added_nodes, added_edges = patch_uapp(base_graph)
    base_variables = published_conversation_variables()
    candidate_variables = patch_conversation_variables(base_variables)
    return {
        "document": {"id": "WITHDRAW_MATERIAL_REGISTRATION_BUILD_v1.0", "model_calls": 0},
        "base_graph_md5": BASE_UAPP_MD5,
        "candidate_canonical_sha256": sha256_text(canonical(candidate)),
        "conversation_variables_sha256": sha256_text(canonical(candidate_variables)),
        "node_count": len(candidate["nodes"]),
        "edge_count": len(candidate["edges"]),
        "added_nodes": added_nodes,
        "added_edges": added_edges,
        "removed_edges": ["uapp_ctx-source-uapp_m3_gate"],
        "existing_nodes_unchanged": len(base_graph["nodes"]),
        "conversation_variables_added": ["uapp_material_binding"],
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
