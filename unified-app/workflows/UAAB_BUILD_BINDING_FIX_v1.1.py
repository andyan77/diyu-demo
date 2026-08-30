#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""UAAB successor v1.2 minimum builder. Zero model calls.

Builds the complete successor candidate from the restored stable UAPP draft:

1. Re-applies the bounded artifact store and deterministic upstream selector from v1.0.
2. Wires the selector body and identity directly into ``uapp_fields``.
3. Makes ``uapp_fields`` ignore Hop-projected artifact text for artifact identity.
4. Keeps ``uapp_last_capability`` unchanged when no non-empty artifact exists.

The v1.0 builder remains immutable and is imported only as the source for its already frozen
``PICK_CODE`` and ``PERSIST_CODE`` strings.
"""

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
UAPP = os.path.abspath(os.path.join(HERE, ".."))
REPO = os.path.abspath(os.path.join(UAPP, ".."))
EVIDENCE_DIR = os.path.join(UAPP, "evidence", "stages", "uapp_artifact_binding")
ENV_FILE = "/home/faye/diyu-demo-worktrees/m3-account-content-operator-v1/.env"

UAPP_APP_ID = "85c01f85-a081-43e9-ab09-9993289cc200"
STABLE_GRAPH_MD5 = "99c3edf7bd12172a4fb011b588f25e57"
EXPECTED_TOUCHED = sorted(
    ["uapp_fields", "uapp_hop", "uapp_persist", "uapp_pick_upstream(NEW)", "uapp_save"]
)


def load_module(name: str, path: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


BASE = load_module("uaab_builder_v10", os.path.join(HERE, "UAAB_BUILD_BINDING_FIX_v1.0.py"))
DC = load_module("dify_client", os.path.join(REPO, "account-operations", "tools", "dify_client.py"))

PICK_CODE: str = BASE.PICK_CODE
_PERSIST_OLD = '"capability_to_persist": cap or (prev_capability or ""),'
_PERSIST_NEW = '"capability_to_persist": cap if a and cap else (prev_capability or ""),'
if BASE.PERSIST_CODE.count(_PERSIST_OLD) != 1:
    raise RuntimeError("v1.0 persist guard anchor is not unique")
PERSIST_CODE: str = BASE.PERSIST_CODE.replace(_PERSIST_OLD, _PERSIST_NEW, 1)

_MAIN_OLD = (
    "def main(prev_state_json, task_key, capability_call, gaps_text, target_capability,\n"
    "         user_request, snapshot_json):"
)
_MAIN_NEW = (
    "def main(prev_state_json, task_key, capability_call, gaps_text, target_capability,\n"
    "         user_request, snapshot_json, selector_delivery, selector_fp, selector_bfp,\n"
    "         selector_capability, selector_status):"
)

_BINDING_OLD = '''    # 6. 上游 artifact 接受闸门：未接受或已 STALE 的不得进入下一能力
    binding, rejected = [], []
    for slot in ARTIFACT_SLOTS:
        e = found.get(slot)
        if e is None or not e["v"]:
            continue
        fp = _fp(_norm(e["v"])[:256])
        rec = None
        for a in st["artifacts"]:
            if a.get("fp") == fp:
                rec = a
                break
        if rec and rec.get("accepted") and not rec.get("stale"):
            binding.append({"slot": slot, "upstream_capability": rec.get("cap"),
                            "fp": fp, "artifact_norm_len": rec.get("nlen"),
                            "produced_turn": rec.get("turn"),
                            "accepted_turn": rec.get("accepted_turn"),
                            "accepted_revision": rec.get("accepted_rev"),
                            "lineage": "BOUND"})
        else:
            why = "NO_LEDGER_MATCH" if not rec else (
                "STALE" if rec.get("stale") else "NOT_ACCEPTED")
            _drop(lines, found, slot)
            rejected.append(slot)
            binding.append({"slot": slot, "fp": fp, "lineage": "REJECTED", "reason": why})
'''

_BINDING_NEW = '''    # 6. 上游 artifact 接受闸门（successor v1.2）
    # Hop 仍负责普通字段抽取，但它的投影文本永不再充当完整 artifact 的身份或正文。
    # 完整正文与身份只取 selector 的直接输出；正文只进入本轮 capability_call，
    # 不写入规范字段 F，也不产生第二份会话正文真源。
    slot_for_target = {
        "PRODUCTION_DIRECTOR": "script_or_equivalent_beats",
        "PUBLISHING_PACKAGING": "content_body_or_beats",
    }
    compatible = {
        "PRODUCTION_DIRECTOR": ["CREATIVE_SCRIPT"],
        "PUBLISHING_PACKAGING": ["PRODUCTION_DIRECTOR", "CREATIVE_SCRIPT"],
    }
    binding, rejected = [], []
    binding_status = "NO_UPSTREAM_REQUIRED"

    # 无条件移除 Hop 生成的 artifact 槽位；普通字段保持原样。
    for projected_slot in ARTIFACT_SLOTS:
        _drop(lines, found, projected_slot)

    slot = slot_for_target.get(cap)
    if slot:
        body = selector_delivery or ""
        nbody = _norm(body)
        sfp = (selector_fp or "").strip()
        sbfp = (selector_bfp or "").strip()
        scap = (selector_capability or "").strip()
        sstatus = (selector_status or "").strip()
        rec = None
        for a in st["artifacts"]:
            if a.get("fp") == sfp:
                rec = a
                break

        reason = ""
        if sstatus != "SELECTED":
            reason = "SELECTOR_NOT_SELECTED"
        elif not body:
            reason = "BODY_EMPTY"
        elif scap not in compatible.get(cap, []):
            reason = "CAPABILITY_INCOMPATIBLE"
        elif rec is None:
            reason = "NO_LEDGER_MATCH"
        elif (rec.get("task_key") or st.get("task_key") or "") != tk:
            reason = "CROSS_TASK"
        elif rec.get("cap") != scap:
            reason = "CAPABILITY_IDENTITY_CONFLICT"
        elif not rec.get("accepted"):
            reason = "NOT_ACCEPTED"
        elif rec.get("stale"):
            reason = "STALE"
        elif _fp(nbody[:256]) != sfp:
            reason = "FP_MISMATCH"
        elif not sbfp or _fp(nbody) != sbfp:
            reason = "BFP_MISMATCH"

        if reason:
            binding_status = "REJECTED"
            rejected.append(slot)
            binding.append({"slot": slot, "fp": sfp, "bfp": sbfp,
                            "upstream_capability": scap, "lineage": "REJECTED",
                            "reason": reason})
        else:
            # 单行 JSON 串保留原始正文的逐字节身份；下游可确定性解码回 selector 原文。
            injected = '"%s": %s' % (slot, json.dumps(body, ensure_ascii=False))
            lines.append(injected)
            found[slot] = {"i": len(lines) - 1, "ind": "", "v": body, "st": "JSON"}
            binding_status = "BOUND"
            binding.append({"slot": slot, "upstream_capability": scap,
                            "fp": sfp, "bfp": sbfp,
                            "artifact_norm_len": len(nbody),
                            "artifact_raw_len": len(body),
                            "produced_turn": rec.get("turn"),
                            "accepted_turn": rec.get("accepted_turn"),
                            "accepted_revision": rec.get("accepted_rev"),
                            "lineage": "BOUND", "identity_source": "SELECTOR_DIRECT"})
'''

_RETURN_OLD = '            "upstream_binding_json": json.dumps(binding, ensure_ascii=False),\n'
_RETURN_NEW = (
    '            "upstream_binding_json": json.dumps(binding, ensure_ascii=False),\n'
    '            "artifact_binding_status": binding_status,\n'
)


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


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


def patch_fields_code(code: str) -> str:
    anchors = [(_MAIN_OLD, _MAIN_NEW), (_BINDING_OLD, _BINDING_NEW), (_RETURN_OLD, _RETURN_NEW)]
    patched = code
    for old, new in anchors:
        if patched.count(old) != 1:
            raise RuntimeError(f"uapp_fields patch anchor count is {patched.count(old)}, expected 1")
        patched = patched.replace(old, new, 1)
    return patched


def build_candidate(draft: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    graph = json.loads(canonical(draft["graph"]))
    before_graph = json.loads(canonical(graph))
    before_nodes = before_graph["nodes"]
    before_edges = before_graph["edges"]
    nodes = {node["id"]: node for node in graph["nodes"]}
    if "uapp_pick_upstream" in nodes:
        raise RuntimeError("selector already exists; refusing to rebuild over a non-stable draft")

    persist = nodes["uapp_persist"]["data"]
    persist["code"] = PERSIST_CODE
    persist["desc"] = (
        "按指纹分格的有界产物存储；没有非空新产物时同时保留上一合法正文和能力标记"
    )
    persist["title"] = "闸门｜产物存储（按指纹分格）"
    persist["variables"] = [
        {"value_selector": ["uapp_seam_merge", "artifact", "output"], "variable": "new_artifact"},
        {"value_selector": ["uapp_route", "target_capability"], "variable": "new_capability"},
        {"value_selector": ["conversation", "uapp_last_artifact"], "variable": "prev_store"},
        {"value_selector": ["conversation", "uapp_last_capability"], "variable": "prev_capability"},
        {"value_selector": ["uapp_fields", "pending_state_json"], "variable": "pending_state_json"},
    ]
    persist["outputs"] = {
        key: {"children": None, "type": "string"}
        for key in (
            "store_to_persist",
            "capability_to_persist",
            "persist_action",
            "store_note",
            "store_item_count",
        )
    }

    for item in nodes["uapp_save"]["data"]["items"]:
        if item.get("variable_selector") == ["conversation", "uapp_last_artifact"]:
            item["value"] = ["uapp_persist", "store_to_persist"]

    hop = nodes["uapp_hop"]
    pick = {
        "id": "uapp_pick_upstream",
        "type": "custom",
        "position": {"x": hop["position"]["x"] - 320, "y": hop["position"]["y"] + 160},
        "positionAbsolute": {
            "x": hop["positionAbsolute"]["x"] - 320,
            "y": hop["positionAbsolute"]["y"] + 160,
        },
        "width": 244,
        "height": 98,
        "selected": False,
        "sourcePosition": "right",
        "targetPosition": "left",
        "zIndex": 0,
        "data": {
            "type": "code",
            "code_language": "python3",
            "title": "选择｜合法已接受上游产物",
            "desc": "同 task、已接受、未 STALE、能力兼容且正文指纹一致；失败时只返回精确缺口",
            "code": PICK_CODE,
            "variables": [
                {"value_selector": ["conversation", "uapp_last_artifact"], "variable": "store_json"},
                {"value_selector": ["conversation", "uapp_task_fields"], "variable": "state_json"},
                {"value_selector": ["uapp_route", "target_capability"], "variable": "target_capability"},
                {"value_selector": ["uapp_route", "user_request"], "variable": "user_request"},
                {"value_selector": ["conversation", "uapp_task"], "variable": "task_key"},
            ],
            "outputs": {
                key: {"children": None, "type": "string"}
                for key in (
                    "upstream_delivery",
                    "upstream_capability",
                    "selection_status",
                    "selected_fp",
                    "selected_bfp",
                    "selected_capability",
                    "selection_question",
                    "selection_note",
                )
            },
            "selected": False,
        },
    }
    graph["nodes"].append(pick)

    old_edge = next(
        (edge for edge in graph["edges"] if edge["source"] == "uapp_op_gate" and edge["target"] == "uapp_hop"),
        None,
    )
    if old_edge is None:
        raise RuntimeError("uapp_op_gate -> uapp_hop edge not found")
    new_edge = json.loads(json.dumps(old_edge))
    old_edge["target"] = "uapp_pick_upstream"
    old_edge["id"] = "uapp_op_gate-capability-uapp_pick_upstream"
    if isinstance(old_edge.get("data"), dict):
        old_edge["data"]["targetType"] = "code"
    new_edge["id"] = "uapp_pick_upstream-source-uapp_hop"
    new_edge["source"] = "uapp_pick_upstream"
    new_edge["sourceHandle"] = "source"
    new_edge["target"] = "uapp_hop"
    if isinstance(new_edge.get("data"), dict):
        new_edge["data"]["sourceType"] = "code"
        new_edge["data"]["targetType"] = "tool"
    graph["edges"].append(new_edge)

    tool_parameters = hop["data"]["tool_parameters"]
    if tool_parameters["upstream_delivery"]["value"] != "{{#conversation.uapp_last_artifact#}}":
        raise RuntimeError("unexpected Hop upstream_delivery baseline")
    if tool_parameters["upstream_capability"]["value"] != "{{#conversation.uapp_last_capability#}}":
        raise RuntimeError("unexpected Hop upstream_capability baseline")
    tool_parameters["upstream_delivery"]["value"] = "{{#uapp_pick_upstream.upstream_delivery#}}"
    tool_parameters["upstream_capability"]["value"] = "{{#uapp_pick_upstream.upstream_capability#}}"

    fields = nodes["uapp_fields"]["data"]
    fields["code"] = patch_fields_code(fields["code"])
    fields["desc"] = (
        "普通字段沿用 Hop 载体规则；完整 artifact 只按 selector 直接正文与身份元数据确定性绑定"
    )
    fields["variables"].extend(
        [
            {"value_selector": ["uapp_pick_upstream", "upstream_delivery"], "variable": "selector_delivery"},
            {"value_selector": ["uapp_pick_upstream", "selected_fp"], "variable": "selector_fp"},
            {"value_selector": ["uapp_pick_upstream", "selected_bfp"], "variable": "selector_bfp"},
            {
                "value_selector": ["uapp_pick_upstream", "selected_capability"],
                "variable": "selector_capability",
            },
            {"value_selector": ["uapp_pick_upstream", "selection_status"], "variable": "selector_status"},
        ]
    )
    fields["outputs"]["artifact_binding_status"] = {"children": None, "type": "string"}

    conversation_variables = json.loads(canonical(draft.get("conversation_variables") or []))
    changed_descriptions: list[str] = []
    for variable in conversation_variables:
        if isinstance(variable, dict) and variable.get("name") == "uapp_last_artifact":
            variable["description"] = (
                "本会话唯一正文存储：按指纹分格保存各能力 artifact；选择器直接取回并由 uapp_fields 复核"
            )
            changed_descriptions.append("uapp_last_artifact")

    before_map = {node["id"]: node for node in before_nodes}
    touched: list[str] = []
    for node in graph["nodes"]:
        previous = before_map.get(node["id"])
        if previous is None:
            touched.append(node["id"] + "(NEW)")
        elif canonical(previous) != canonical(node):
            touched.append(node["id"])
    touched = sorted(touched)

    protected_nodes = ["uapp_state", "uapp_seam", "uapp_m3", "uapp_route", "uapp_delivery", "m1_compiler"]
    after_map = {node["id"]: node for node in graph["nodes"]}
    protected_equal = {
        node_id: canonical(before_map[node_id]) == canonical(after_map[node_id]) for node_id in protected_nodes
    }
    if touched != EXPECTED_TOUCHED:
        raise RuntimeError(f"unexpected impact surface: {touched}")
    if not all(protected_equal.values()):
        raise RuntimeError(f"protected node drift: {protected_equal}")
    if len(graph["edges"]) != len(before_edges) + 1:
        raise RuntimeError("edge count delta is not exactly +1")

    report = {
        "document": {
            "id": "UAAB_BUILD_BINDING_FIX_v1.1",
            "task_id": "DIYU-V1-UAPP-ACCEPTED-ARTIFACT-BINDING-001",
            "model_calls": 0,
        },
        "graph_md5_before": STABLE_GRAPH_MD5,
        "nodes_touched": touched,
        "impact_surface_exact": True,
        "node_count": {"before": len(before_nodes), "after": len(graph["nodes"])},
        "edge_count": {"before": len(before_edges), "after": len(graph["edges"])},
        "conversation_variables_added": [],
        "conversation_variable_descriptions_updated": changed_descriptions,
        "pick_code_sha256": sha256_text(PICK_CODE),
        "persist_code_sha256": sha256_text(PERSIST_CODE),
        "fields_code_sha256": sha256_text(fields["code"]),
        "candidate_graph_canonical_sha256": sha256_text(canonical(graph)),
        "protected_nodes_equal": protected_equal,
        "hop_projection_retained_for_plain_fields": True,
        "artifact_identity_source": "uapp_pick_upstream direct outputs",
        "no_new_artifact_capability_guard": True,
        "applied": False,
    }
    payload = {
        "graph": graph,
        "features": draft.get("features") or {},
        "hash": draft.get("hash"),
        "environment_variables": draft.get("environment_variables") or [],
        "conversation_variables": conversation_variables,
    }
    return payload, report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    if not (args.dry_run or args.apply) or (args.dry_run and args.apply):
        raise SystemExit("Choose exactly one of --dry-run or --apply")

    published_md5 = psql(
        "select md5(w.graph) from workflows w join apps a on a.workflow_id=w.id "
        f"where a.id='{UAPP_APP_ID}';"
    )
    if published_md5 != STABLE_GRAPH_MD5:
        raise SystemExit(f"published UAPP is not the frozen stable graph: {published_md5}")

    console = DC.Console(env=DC.load_env(ENV_FILE))
    status, draft = console.call("GET", f"/console/api/apps/{UAPP_APP_ID}/workflows/draft", timeout=300)
    if status != 200:
        raise RuntimeError(f"draft read failed: {status} {str(draft)[:300]}")
    payload, report = build_candidate(draft)

    if args.apply:
        status, response = console.call(
            "POST", f"/console/api/apps/{UAPP_APP_ID}/workflows/draft", body=payload, timeout=900
        )
        if status != 200:
            raise RuntimeError(f"draft sync failed: {status} {str(response)[:400]}")
        read_status, readback = console.call(
            "GET", f"/console/api/apps/{UAPP_APP_ID}/workflows/draft", timeout=300
        )
        if read_status != 200:
            raise RuntimeError(f"draft readback failed: {read_status} {str(readback)[:300]}")
        if canonical(readback["graph"]) != canonical(payload["graph"]):
            raise RuntimeError("draft readback differs from the submitted candidate graph")
        report["applied"] = True
        report["draft_readback_equal"] = True
        report["draft_hash_after"] = readback.get("hash")

    os.makedirs(EVIDENCE_DIR, exist_ok=True)
    evidence_path = os.path.join(EVIDENCE_DIR, "UAAB_BUILD_BINDING_FIX_v1.1.json")
    with open(evidence_path, "w", encoding="utf-8") as handle:
        json.dump(report, handle, ensure_ascii=False, indent=1)
        handle.write("\n")
    logging.info("%s", json.dumps(report, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    raise SystemExit(main())
