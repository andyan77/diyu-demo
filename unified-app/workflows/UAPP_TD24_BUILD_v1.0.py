#!/usr/bin/env python3
"""Build the TD-UAPP-24 successor candidate without model calls.

The builder starts from the exact currently published UAPP graph. ``--dry-run`` only
produces local evidence; ``--apply-draft`` writes the same candidate to the existing
UAPP draft through the Dify console API and reads it back.
"""

from __future__ import annotations

import argparse
import copy
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
EVIDENCE_DIR = os.path.join(UAPP_ROOT, "evidence", "stages", "uapp_td24")
ENV_FILE = "/home/faye/diyu-demo-worktrees/m3-account-content-operator-v1/.env"

UAPP_APP_ID = "85c01f85-a081-43e9-ab09-9993289cc200"
BASE_GRAPH_MD5 = "91a3984b2c3797d6741165b116fa3cb1"


def load_module(name: str, path: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


NODES = load_module("uapp_td24_nodes", os.path.join(HERE, "UAPP_TD24_NODES_v1.0.py"))
DC = load_module(
    "dify_client",
    os.path.join(REPO, "account-operations", "tools", "dify_client.py"),
)


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def psql(sql: str) -> str:
    completed = subprocess.run(
        [
            "docker",
            "exec",
            "-i",
            "docker-db_postgres-1",
            "psql",
            "-U",
            "postgres",
            "-d",
            "dify",
            "-tA",
            "-v",
            "ON_ERROR_STOP=1",
            "-c",
            sql,
        ],
        capture_output=True,
        check=False,
        text=True,
    )
    if completed.returncode != 0:
        raise RuntimeError((completed.stderr or completed.stdout)[:1000])
    return completed.stdout.strip()


def published_graph() -> dict[str, Any]:
    raw = psql(
        "select w.graph from workflows w join apps a on a.workflow_id=w.id "
        f"where a.id='{UAPP_APP_ID}';"
    )
    graph = json.loads(raw)
    if not isinstance(graph, dict):
        raise RuntimeError("Published graph is not an object")
    return graph


def graph_md5() -> str:
    return psql(
        "select md5(w.graph) from workflows w join apps a on a.workflow_id=w.id "
        f"where a.id='{UAPP_APP_ID}';"
    )


def patch_action(node: dict[str, Any]) -> None:
    data = node["data"]
    prompts = data["prompt_template"]
    system = next(item for item in prompts if item.get("role") == "system")
    user = next(item for item in prompts if item.get("role") == "user")
    marker = "TD-UAPP-24 能力中立纠正提议"
    if marker in system["text"]:
        raise RuntimeError("uapp_action is already patched")
    system["text"] += f"""

────────── {marker} ──────────

无论本轮 intent 指向哪个能力，都要独立检查用户是否在明确纠正当前规范状态。
这一步只提出候选，不直接写状态；后面的确定性节点会逐字复核用户原话。

`correction_deltas` 是数组。没有明确纠正就输出空数组。每条只含：
- `field_id`：必须逐字取自下方当前规范状态 `fields` 的现有键；
- `new_value`：应用用户这一处明确修改后的完整字段值，其他明确说不变的内容逐字保留；
- `source_quote`：用户本轮原话中的连续逐字片段，必须同时包含旧值、新值和修改关系。

禁止把建议、猜测、模糊表达、当前能力需要的字段、模型自己补出的事实写进数组。
如果同一条纠正会让两个同范围、同用户来源的现有字段出现矛盾，应分别提出两条，
但不得合并字段身份或创造新字段。
"""
    state_block = "\n\n【当前规范任务状态（仅用于提出纠正候选）】\n{{#conversation.uapp_task_fields#}}"
    if state_block in user["text"]:
        raise RuntimeError("uapp_action user prompt is already patched")
    user["text"] += state_block

    schema = data["structured_output"]["schema"]
    schema["properties"]["correction_deltas"] = {
        "description": "能力中立的明确用户纠正候选；没有则为空数组",
        "type": "array",
        "items": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "field_id": {"type": "string"},
                "new_value": {"type": "string"},
                "source_quote": {"type": "string"},
            },
            "required": ["field_id", "new_value", "source_quote"],
        },
    }
    schema["required"].append("correction_deltas")
    data["desc"] = (
        "自然语言分诊与能力中立纠正候选；候选只供后续确定性复核，不直接写事实"
    )


def patch_selector(node: dict[str, Any]) -> None:
    data = node["data"]
    signature = "def main(store_json, state_json, target_capability, user_request, task_key):"
    replacement = (
        "def main(store_json, state_json, target_capability, user_request, task_key, "
        "correction_status):"
    )
    if data["code"].count(signature) != 1:
        raise RuntimeError("selector signature anchor mismatch")
    data["code"] = data["code"].replace(signature, replacement, 1)
    anchor = '    tk = (task_key or "").strip()\n\n'
    guard = (
        '    tk = (task_key or "").strip()\n\n'
        '    if (correction_status or "").strip() == "REJECTED":\n'
        '        return _fail("CORRECTION_REJECTED",\n'
        '                     "这次修改还不能准确对应到当前记录，先不继续使用旧方案。",\n'
        '                     "明确纠正未通过确定性复核")\n\n'
    )
    if data["code"].count(anchor) != 1:
        raise RuntimeError("selector guard anchor mismatch")
    data["code"] = data["code"].replace(anchor, guard, 1)
    for variable in data["variables"]:
        if variable.get("variable") == "state_json":
            variable["value_selector"] = ["uapp_td24_correction", "corrected_state_json"]
    data["variables"].append(
        {
            "value_selector": ["uapp_td24_correction", "correction_status"],
            "variable": "correction_status",
        }
    )
    data["desc"] = (
        "只读纠正后状态；同 task、已接受、未失效、能力兼容且正文指纹一致"
    )


def patch_fields(node: dict[str, Any]) -> None:
    data = node["data"]
    signature = (
        "def main(prev_state_json, task_key, capability_call, gaps_text, target_capability,\n"
        "         user_request, snapshot_json, selector_delivery, selector_fp, selector_bfp,\n"
        "         selector_capability, selector_status):"
    )
    replacement = signature[:-2] + ", correction_status):"
    if data["code"].count(signature) != 1:
        raise RuntimeError("fields signature anchor mismatch")
    data["code"] = data["code"].replace(signature, replacement, 1)
    rev_anchor = (
        "    rev = int(st.get(\"rev\") or 0) + 1\n"
        "    F = st[\"fields\"]\n"
        "    # 本轮开始前：上一轮的 A 级降为 B（用户更早说过的），本轮的 A 才是\"用户本轮说的\"\n"
        "    for e in F.values():\n"
        "        if e.get(\"lvl\") == \"A\":\n"
        "            e[\"lvl\"] = \"B\"\n"
    )
    rev_replacement = (
        "    correction_active = (correction_status or \"\").strip() == \"APPLIED\"\n"
        "    rev = int(st.get(\"rev\") or 0) if correction_active else int(st.get(\"rev\") or 0) + 1\n"
        "    F = st[\"fields\"]\n"
        "    # 纠正节点已经建立本轮 A 级来源；不得在同一 turn 再降级或重复加 revision。\n"
        "    if not correction_active:\n"
        "        for e in F.values():\n"
        "            if e.get(\"lvl\") == \"A\":\n"
        "                e[\"lvl\"] = \"B\"\n"
    )
    if data["code"].count(rev_anchor) != 1:
        raise RuntimeError("fields revision anchor mismatch")
    data["code"] = data["code"].replace(rev_anchor, rev_replacement, 1)
    offer_anchor = "    for cid in sorted(env_vals):\n        val = env_vals[cid]\n"
    offer_replacement = (
        "    for cid in sorted(env_vals):\n"
        "        # 本轮明确纠正已经由能力中立接缝写入；Hop 的能力投影不得再改写普通字段。\n"
        "        if correction_active:\n"
        "            continue\n"
        "        val = env_vals[cid]\n"
    )
    if data["code"].count(offer_anchor) != 1:
        raise RuntimeError("fields offer anchor mismatch")
    data["code"] = data["code"].replace(offer_anchor, offer_replacement, 1)
    for variable in data["variables"]:
        if variable.get("variable") == "prev_state_json":
            variable["value_selector"] = ["uapp_td24_correction", "corrected_state_json"]
    data["variables"].append(
        {
            "value_selector": ["uapp_td24_correction", "correction_status"],
            "variable": "correction_status",
        }
    )
    data["desc"] = (
        "基于纠正后状态复核 selector；纠正 turn 不再让 Hop 投影重复改写规范字段"
    )


def patch_state(node: dict[str, Any]) -> None:
    data = node["data"]
    signature = "def main(pending_state_json, envelope_fields_json, new_artifact, new_capability):"
    replacement = (
        "def main(pending_state_json, envelope_fields_json, new_artifact, new_capability, "
        "upstream_binding_json):"
    )
    if data["code"].count(signature) != 1:
        raise RuntimeError("state signature anchor mismatch")
    data["code"] = data["code"].replace(signature, replacement, 1)
    dep_anchor = "    except Exception:\n        dep = {}\n\n    a = (new_artifact or \"\").strip()\n"
    dep_replacement = (
        "    except Exception:\n"
        "        dep = {}\n"
        "    try:\n"
        "        bindings = json.loads(upstream_binding_json) if "
        "(upstream_binding_json or \"\").strip() else []\n"
        "    except Exception:\n"
        "        bindings = []\n"
        "    upstream_fp = \"\"\n"
        "    for binding in bindings if isinstance(bindings, list) else []:\n"
        "        if isinstance(binding, dict) and binding.get(\"lineage\") == \"BOUND\":\n"
        "            upstream_fp = binding.get(\"fp\") or \"\"\n"
        "            break\n\n"
        "    a = (new_artifact or \"\").strip()\n"
    )
    if data["code"].count(dep_anchor) != 1:
        raise RuntimeError("state dependency anchor mismatch")
    data["code"] = data["code"].replace(dep_anchor, dep_replacement, 1)
    record_anchor = (
        '                "dep": dep, "stale": False, "stale_reason": None})'
    )
    record_replacement = (
        '                "dep": dep, "upstream_fp": upstream_fp or None,\n'
        '                "lineage_kind": "RECORDED_AT_CREATION" if upstream_fp else None,\n'
        '                "stale": False, "stale_reason": None})'
    )
    if data["code"].count(record_anchor) != 1:
        raise RuntimeError("state record anchor mismatch")
    data["code"] = data["code"].replace(record_anchor, record_replacement, 1)
    data["variables"].append(
        {
            "value_selector": ["uapp_fields", "upstream_binding_json"],
            "variable": "upstream_binding_json",
        }
    )
    data["desc"] = "在现有 artifact 账本中登记字段依赖及最小直接 upstream_fp"


def code_node(
    node_id: str,
    title: str,
    description: str,
    code: str,
    variables: list[dict[str, Any]],
    outputs: tuple[str, ...],
    position: dict[str, float],
) -> dict[str, Any]:
    return {
        "id": node_id,
        "type": "custom",
        "position": position,
        "positionAbsolute": dict(position),
        "width": 244,
        "height": 98,
        "selected": False,
        "sourcePosition": "right",
        "targetPosition": "left",
        "zIndex": 0,
        "data": {
            "type": "code",
            "code_language": "python3",
            "title": title,
            "desc": description,
            "code": code,
            "variables": variables,
            "outputs": {name: {"children": None, "type": "string"} for name in outputs},
            "selected": False,
        },
    }


def clone_edge(edge: dict[str, Any], edge_id: str, source: str, target: str) -> dict[str, Any]:
    cloned = copy.deepcopy(edge)
    cloned["id"] = edge_id
    cloned["source"] = source
    cloned["sourceHandle"] = "source"
    cloned["target"] = target
    cloned["targetHandle"] = "target"
    if isinstance(cloned.get("data"), dict):
        cloned["data"]["sourceType"] = "code"
        cloned["data"]["targetType"] = "code"
    return cloned


def build_candidate(graph: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    candidate = json.loads(canonical(graph))
    before = json.loads(canonical(graph))
    nodes = {node["id"]: node for node in candidate["nodes"]}
    if "uapp_td24_correction" in nodes:
        raise RuntimeError("TD24 nodes already exist")

    patch_action(nodes["uapp_action"])
    patch_selector(nodes["uapp_pick_upstream"])
    patch_fields(nodes["uapp_fields"])
    patch_state(nodes["uapp_state"])

    pick_position = nodes["uapp_pick_upstream"]["position"]
    fields_position = nodes["uapp_fields"]["position"]
    correction = code_node(
        "uapp_td24_correction",
        "纠正｜能力中立规范 delta 与失效传播",
        "先于 selector 复核用户原话，更新现有状态并传播直接/传递失效",
        NODES.CORRECTION_CODE,
        [
            {"value_selector": ["conversation", "uapp_task_fields"], "variable": "prev_state_json"},
            {"value_selector": ["uapp_action", "structured_output"], "variable": "action_patch"},
            {"value_selector": ["uapp_route", "user_request"], "variable": "user_request"},
            {"value_selector": ["conversation", "uapp_task"], "variable": "task_key"},
            {"value_selector": ["uapp_route", "target_capability"], "variable": "target_capability"},
        ],
        (
            "corrected_state_json",
            "correction_delta_json",
            "correction_status",
            "corrected_fields",
            "direct_stale",
            "transitive_stale",
            "lineage_backfilled",
            "block_message",
            "correction_note",
        ),
        {"x": pick_position["x"] - 300, "y": pick_position["y"]},
    )
    candidate["nodes"].append(correction)

    binding_gate = {
        "id": "uapp_td24_binding_gate",
        "type": "custom",
        "position": {"x": fields_position["x"] + 280, "y": fields_position["y"]},
        "positionAbsolute": {"x": fields_position["x"] + 280, "y": fields_position["y"]},
        "width": 244,
        "height": 98,
        "selected": False,
        "sourcePosition": "right",
        "targetPosition": "left",
        "zIndex": 0,
        "data": {
            "type": "if-else",
            "title": "闸门｜上游绑定后再进能力",
            "desc": "REJECTED 在 Seam 与专业能力之前精确停支",
            "logical_operator": "and",
            "cases": [
                {
                    "case_id": "blocked",
                    "logical_operator": "and",
                    "conditions": [
                        {
                            "comparison_operator": "is",
                            "value": "REJECTED",
                            "variable_selector": ["uapp_fields", "artifact_binding_status"],
                        }
                    ],
                }
            ],
            "selected": False,
        },
    }
    candidate["nodes"].append(binding_gate)

    block = code_node(
        "uapp_td24_block",
        "停支｜旧上游不可继续使用",
        "不调用 Seam/PP；给用户自然、精确的下一步",
        NODES.BLOCK_CODE,
        [
            {"value_selector": ["uapp_td24_correction", "correction_status"], "variable": "correction_status"},
            {"value_selector": ["uapp_td24_correction", "block_message"], "variable": "block_message"},
            {"value_selector": ["uapp_pick_upstream", "selection_question"], "variable": "selection_question"},
            {"value_selector": ["uapp_fields", "gaps_text"], "variable": "gaps_text"},
        ],
        ("final_text", "block_reason", "precise_gap"),
        {"x": fields_position["x"] + 560, "y": fields_position["y"] + 240},
    )
    candidate["nodes"].append(block)

    block_save = copy.deepcopy(nodes["uapp_save"])
    block_save["id"] = "uapp_td24_block_save"
    block_save["position"] = {"x": fields_position["x"] + 840, "y": fields_position["y"] + 240}
    block_save["positionAbsolute"] = dict(block_save["position"])
    block_save["data"]["title"] = "记住｜只保存纠正后的规范状态"
    block_save["data"]["desc"] = "保留产物正文存储与上一合法能力标记，不产生新 artifact"
    block_save["data"]["items"] = [
        {
            "input_type": "variable",
            "operation": "over-write",
            "value": ["uapp_fields", "pending_state_json"],
            "variable_selector": ["conversation", "uapp_task_fields"],
            "write_mode": "over-write",
        }
    ]
    candidate["nodes"].append(block_save)

    block_answer = copy.deepcopy(nodes["uapp_answer_main"])
    block_answer["id"] = "uapp_td24_block_answer"
    block_answer["position"] = {"x": fields_position["x"] + 1120, "y": fields_position["y"] + 240}
    block_answer["positionAbsolute"] = dict(block_answer["position"])
    block_answer["data"]["title"] = "回复｜先更新受影响方案"
    block_answer["data"]["answer"] = "{{#uapp_td24_block.final_text#}}"
    candidate["nodes"].append(block_answer)

    op_pick = next(
        edge for edge in candidate["edges"]
        if edge["source"] == "uapp_op_gate" and edge["target"] == "uapp_pick_upstream"
    )
    op_pick["id"] = "uapp_op_gate-capability-uapp_td24_correction"
    op_pick["target"] = "uapp_td24_correction"
    candidate["edges"].append(
        clone_edge(
            op_pick,
            "uapp_td24_correction-source-uapp_pick_upstream",
            "uapp_td24_correction",
            "uapp_pick_upstream",
        )
    )

    fields_seam = next(
        edge for edge in candidate["edges"]
        if edge["source"] == "uapp_fields" and edge["target"] == "uapp_seam"
    )
    fields_seam["id"] = "uapp_fields-source-uapp_td24_binding_gate"
    fields_seam["target"] = "uapp_td24_binding_gate"
    gate_template = copy.deepcopy(fields_seam)
    seam_edge = clone_edge(
        gate_template,
        "uapp_td24_binding_gate-false-uapp_seam",
        "uapp_td24_binding_gate",
        "uapp_seam",
    )
    seam_edge["sourceHandle"] = "false"
    block_edge = clone_edge(
        gate_template,
        "uapp_td24_binding_gate-blocked-uapp_td24_block",
        "uapp_td24_binding_gate",
        "uapp_td24_block",
    )
    block_edge["sourceHandle"] = "blocked"
    candidate["edges"].extend(
        [
            seam_edge,
            block_edge,
            clone_edge(gate_template, "uapp_td24_block-source-uapp_td24_block_save", "uapp_td24_block", "uapp_td24_block_save"),
            clone_edge(gate_template, "uapp_td24_block_save-source-uapp_td24_block_answer", "uapp_td24_block_save", "uapp_td24_block_answer"),
        ]
    )

    before_map = {node["id"]: node for node in before["nodes"]}
    after_map = {node["id"]: node for node in candidate["nodes"]}
    touched = sorted(
        [node_id for node_id in before_map if canonical(before_map[node_id]) != canonical(after_map[node_id])]
        + [node_id + "(NEW)" for node_id in after_map if node_id not in before_map]
    )
    expected = sorted(
        [
            "uapp_action",
            "uapp_pick_upstream",
            "uapp_fields",
            "uapp_state",
            "uapp_td24_correction(NEW)",
            "uapp_td24_binding_gate(NEW)",
            "uapp_td24_block(NEW)",
            "uapp_td24_block_save(NEW)",
            "uapp_td24_block_answer(NEW)",
        ]
    )
    if touched != expected:
        raise RuntimeError(f"Unexpected node impact surface: {touched}")
    protected_ids = [
        "m1_shadow",
        "m1_compiler",
        "uapp_m3",
        "uapp_hop",
        "uapp_seam",
        "uapp_persist",
        "uapp_delivery",
        "uapp_save",
    ]
    protected_equal = {
        node_id: canonical(before_map[node_id]) == canonical(after_map[node_id])
        for node_id in protected_ids
    }
    if not all(protected_equal.values()):
        raise RuntimeError(f"Protected node drift: {protected_equal}")

    report = {
        "document": {
            "id": "UAPP_TD24_BUILD_v1.0",
            "task_id": "DIYU-V1-UNIFIED-DIFY-APPLICATION-001",
            "model_calls": 0,
            "direct_db_writes": 0,
        },
        "base_graph_md5": BASE_GRAPH_MD5,
        "nodes_touched": touched,
        "protected_nodes_equal": protected_equal,
        "node_count": {"before": len(before["nodes"]), "after": len(candidate["nodes"])},
        "edge_count": {"before": len(before["edges"]), "after": len(candidate["edges"])},
        "conversation_variables_added": [],
        "correction_code_sha256": sha256_text(NODES.CORRECTION_CODE),
        "block_code_sha256": sha256_text(NODES.BLOCK_CODE),
        "candidate_graph_canonical_sha256": sha256_text(canonical(candidate)),
        "applied_to_draft": False,
    }
    return candidate, report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--apply-draft", action="store_true")
    args = parser.parse_args()
    if args.dry_run == args.apply_draft:
        raise SystemExit("Choose exactly one of --dry-run or --apply-draft")
    if graph_md5() != BASE_GRAPH_MD5:
        raise RuntimeError("Published UAPP graph differs from the frozen TD24 base")

    base = published_graph()
    candidate, report = build_candidate(base)
    if args.apply_draft:
        console = DC.Console(env=DC.load_env(ENV_FILE))
        status, draft = console.call(
            "GET", f"/console/api/apps/{UAPP_APP_ID}/workflows/draft", timeout=300
        )
        if status != 200:
            raise RuntimeError(f"Draft read failed: {status} {str(draft)[:300]}")
        payload = {
            "graph": candidate,
            "features": draft.get("features") or {},
            "hash": draft.get("hash"),
            "environment_variables": draft.get("environment_variables") or [],
            "conversation_variables": draft.get("conversation_variables") or [],
        }
        write_status, response = console.call(
            "POST",
            f"/console/api/apps/{UAPP_APP_ID}/workflows/draft",
            body=payload,
            timeout=900,
        )
        if write_status != 200:
            raise RuntimeError(f"Draft write failed: {write_status} {str(response)[:400]}")
        read_status, readback = console.call(
            "GET", f"/console/api/apps/{UAPP_APP_ID}/workflows/draft", timeout=300
        )
        if read_status != 200 or canonical(readback["graph"]) != canonical(candidate):
            raise RuntimeError("Draft readback differs from candidate")
        report["applied_to_draft"] = True
        report["draft_readback_equal"] = True
        report["draft_hash_after"] = readback.get("hash")

    os.makedirs(EVIDENCE_DIR, exist_ok=True)
    evidence = os.path.join(EVIDENCE_DIR, "UAPP_TD24_BUILD_v1.0.json")
    with open(evidence, "w", encoding="utf-8") as handle:
        json.dump(report, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    logging.info("%s", json.dumps(report, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    raise SystemExit(main())
