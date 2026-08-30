#!/usr/bin/env python3
"""Build and optionally publish the bounded UAPP inline-artifact seam repair."""

from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
import logging
import subprocess
from pathlib import Path
from types import ModuleType
from typing import Any

LOGGER = logging.getLogger(__name__)
HERE = Path(__file__).resolve().parent
UAPP = HERE.parent
REPO = UAPP.parent
ENV_FILE = "/home/faye/diyu-demo-worktrees/m3-account-content-operator-v1/.env"
UAPP_APP_ID = "85c01f85-a081-43e9-ab09-9993289cc200"
BASE_GRAPH_MD5 = "16e10d84dcdf1deb4608d95fe30fb654"
OUTPUT_DIR = UAPP / "evidence" / "stages" / "uapp_s5_inline_artifact_v1_0" / "build"


def load_module(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


NODES = load_module("uapp_s5_inline_nodes", HERE / "UAPP_S5_INLINE_ARTIFACT_NODES_v1.0.py")
DC = load_module("dify_client_uapp_inline", REPO / "account-operations" / "tools" / "dify_client.py")


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def psql(sql: str) -> str:
    result = subprocess.run(
        [
            "docker", "exec", "-i", "docker-db_postgres-1", "psql", "-U", "postgres",
            "-d", "dify", "-tA", "-v", "ON_ERROR_STOP=1", "-c", sql,
        ],
        capture_output=True,
        check=False,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError((result.stderr or result.stdout)[:1000])
    return result.stdout.strip()


def graph_md5() -> str:
    return psql(
        "select md5(w.graph) from workflows w join apps a on a.workflow_id=w.id "
        f"where a.id='{UAPP_APP_ID}';"
    )


def published_graph() -> dict[str, Any]:
    graph = json.loads(
        psql(
            "select w.graph from workflows w join apps a on a.workflow_id=w.id "
            f"where a.id='{UAPP_APP_ID}';"
        )
    )
    if not isinstance(graph, dict):
        raise RuntimeError("Published graph is not an object")
    return graph


def code_node(position: dict[str, float]) -> dict[str, Any]:
    outputs = (
        "inline_status", "inline_reason", "inline_question", "inline_body",
        "inline_artifact_type", "inline_upstream_capability", "inline_source_kind",
        "inline_source_turn", "inline_task_key", "inline_fp", "inline_bfp",
    )
    return {
        "id": "uapp_inline_artifact",
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
            "title": "来源｜本轮完整产物",
            "desc": "只识别当前任务、当前轮、用户明确确认可用的完整原文；不自动持久化",
            "code": NODES.INLINE_CODE,
            "variables": [
                {"value_selector": ["uapp_route", "user_request"], "variable": "user_request"},
                {"value_selector": ["uapp_route", "target_capability"], "variable": "target_capability"},
                {"value_selector": ["conversation", "uapp_task"], "variable": "task_key"},
                {"value_selector": ["uapp_td24_correction", "correction_status"], "variable": "correction_status"},
            ],
            "outputs": {name: {"children": None, "type": "string"} for name in outputs},
            "selected": False,
        },
    }


def patch_selector(node: dict[str, Any]) -> None:
    data = node["data"]
    old_signature = (
        "def main(store_json, state_json, target_capability, user_request, task_key, correction_status):"
    )
    new_signature = (
        "def main(store_json, state_json, target_capability, user_request, task_key, correction_status,\n"
        "         inline_status, inline_body, inline_artifact_type, inline_upstream_capability,\n"
        "         inline_source_kind, inline_source_turn, inline_task_key, inline_fp, inline_bfp,\n"
        "         inline_question):"
    )
    if data["code"].count(old_signature) != 1:
        raise RuntimeError("selector signature anchor mismatch")
    data["code"] = data["code"].replace(old_signature, new_signature, 1)

    fail_anchor = (
        '    return {"upstream_delivery": "", "upstream_capability": "",\n'
        '            "selection_status": status, "selected_fp": "", "selected_bfp": "",\n'
        '            "selected_capability": "", "selection_question": question,\n'
        '            "selection_note": note}\n'
    )
    fail_replacement = (
        '    return {"upstream_delivery": "", "upstream_capability": "",\n'
        '            "selection_status": status, "selected_fp": "", "selected_bfp": "",\n'
        '            "selected_capability": "", "selected_source_kind": "",\n'
        '            "selected_source_turn": "", "selected_artifact_type": "",\n'
        '            "selected_task_key": "", "selection_question": question,\n'
        '            "selection_note": note}\n'
    )
    if data["code"].count(fail_anchor) != 1:
        raise RuntimeError("selector fail anchor mismatch")
    data["code"] = data["code"].replace(fail_anchor, fail_replacement, 1)

    guard_anchor = (
        '    if (correction_status or "").strip() == "REJECTED":\n'
        '        return _fail("CORRECTION_REJECTED",\n'
        '                     "这次修改还不能准确对应到当前记录，先不继续使用旧方案。",\n'
        '                     "明确纠正未通过确定性复核")\n\n'
    )
    inline_branch = guard_anchor + '''    istatus = (inline_status or "").strip()
    if istatus == "INLINE_REJECTED":
        return _fail("INLINE_INVALID", (inline_question or "").strip(),
                     "本轮直接提供的产物未通过完整性或来源复核")
    if istatus == "INLINE_READY":
        body = inline_body or ""
        compact = _norm(body)
        upstream = (inline_upstream_capability or "").strip()
        expected = {"PRODUCTION_DIRECTOR": ["CREATIVE_SCRIPT"],
                    "PUBLISHING_PACKAGING": ["USER_REALIZED_CONTENT"]}
        artifact_types = {"PRODUCTION_DIRECTOR": "SCRIPT_OR_EQUIVALENT_BEATS",
                          "PUBLISHING_PACKAGING": "CONTENT_BODY_OR_BEATS"}
        reason = ""
        if not body:
            reason = "BODY_EMPTY"
        elif upstream == tgt:
            reason = "SELF_UPSTREAM_FORBIDDEN"
        elif upstream not in expected.get(tgt, []):
            reason = "CAPABILITY_INCOMPATIBLE"
        elif (inline_task_key or "").strip() != tk or not tk:
            reason = "CROSS_TASK"
        elif (inline_source_kind or "").strip() != "USER_INLINE_CONFIRMED":
            reason = "SOURCE_NOT_CONFIRMED"
        elif (inline_artifact_type or "").strip() != artifact_types.get(tgt):
            reason = "ARTIFACT_TYPE_MISMATCH"
        elif _fp(compact[:256]) != (inline_fp or "").strip():
            reason = "FP_MISMATCH"
        elif _fp(compact) != (inline_bfp or "").strip():
            reason = "BFP_MISMATCH"
        if reason:
            return _fail("INLINE_INVALID",
                         "这份内容的来源或完整性还不能准确确认，请重新提供本次要直接采用的完整版本。",
                         reason)
        return {"upstream_delivery": body, "upstream_capability": upstream,
                "selection_status": "INLINE_SELECTED", "selected_fp": inline_fp,
                "selected_bfp": inline_bfp, "selected_capability": upstream,
                "selected_source_kind": inline_source_kind,
                "selected_source_turn": inline_source_turn,
                "selected_artifact_type": inline_artifact_type,
                "selected_task_key": inline_task_key, "selection_question": "",
                "selection_note": "本轮用户直接提供并确认可用的完整产物；仅供当前调用"}

'''
    if data["code"].count(guard_anchor) != 1:
        raise RuntimeError("selector correction guard anchor mismatch")
    data["code"] = data["code"].replace(guard_anchor, inline_branch, 1)

    return_anchor = (
        '            "selected_capability": sel["cap"],\n'
        '            "selection_question": "",\n'
        '            "selection_note": note}\n'
    )
    return_replacement = (
        '            "selected_capability": sel["cap"],\n'
        '            "selected_source_kind": "HISTORICAL_ACCEPTED_ARTIFACT",\n'
        '            "selected_source_turn": str(sel["turn"]),\n'
        '            "selected_artifact_type": sel["cap"],\n'
        '            "selected_task_key": tk, "selection_question": "",\n'
        '            "selection_note": note}\n'
    )
    if data["code"].count(return_anchor) != 1:
        raise RuntimeError("selector return anchor mismatch")
    data["code"] = data["code"].replace(return_anchor, return_replacement, 1)

    inline_vars = {
        "inline_status": "inline_status", "inline_body": "inline_body",
        "inline_artifact_type": "inline_artifact_type",
        "inline_upstream_capability": "inline_upstream_capability",
        "inline_source_kind": "inline_source_kind", "inline_source_turn": "inline_source_turn",
        "inline_task_key": "inline_task_key", "inline_fp": "inline_fp", "inline_bfp": "inline_bfp",
        "inline_question": "inline_question",
    }
    for variable, output in inline_vars.items():
        data["variables"].append(
            {"value_selector": ["uapp_inline_artifact", output], "variable": variable}
        )
    for output in (
        "selected_source_kind", "selected_source_turn", "selected_artifact_type", "selected_task_key"
    ):
        data["outputs"][output] = {"children": None, "type": "string"}
    data["desc"] = "历史 accepted 与本轮用户确认完整产物双来源；共同执行 task/type/fp/bfp fail-closed"


def patch_fields(node: dict[str, Any]) -> None:
    data = node["data"]
    old_signature = (
        "         selector_capability, selector_status, correction_status, intent_reason):"
    )
    new_signature = (
        "         selector_capability, selector_status, correction_status, intent_reason,\n"
        "         selector_source_kind, selector_source_turn, selector_artifact_type,\n"
        "         selector_task_key):"
    )
    if data["code"].count(old_signature) != 1:
        raise RuntimeError("fields signature anchor mismatch")
    data["code"] = data["code"].replace(old_signature, new_signature, 1)

    start = data["code"].index("    slot = slot_for_target.get(cap)\n")
    end = data["code"].index("    # 7. 用载体补本轮缺口。", start)
    replacement = '''    slot = slot_for_target.get(cap)
    if slot:
        body = selector_delivery or ""
        nbody = _norm(body)
        sfp = (selector_fp or "").strip()
        sbfp = (selector_bfp or "").strip()
        scap = (selector_capability or "").strip()
        sstatus = (selector_status or "").strip()
        source_kind = (selector_source_kind or "").strip()
        source_turn = (selector_source_turn or "").strip()
        source_task = (selector_task_key or "").strip()
        source_type = (selector_artifact_type or "").strip()
        rec = None
        for artifact in st["artifacts"]:
            if artifact.get("fp") == sfp:
                rec = artifact
                break

        reason = ""
        is_inline = sstatus == "INLINE_SELECTED"
        if sstatus not in ("SELECTED", "INLINE_SELECTED"):
            reason = "SELECTOR_NOT_SELECTED"
        elif not body:
            reason = "BODY_EMPTY"
        elif source_task != tk or not tk:
            reason = "CROSS_TASK"
        elif _fp(nbody[:256]) != sfp:
            reason = "FP_MISMATCH"
        elif not sbfp or _fp(nbody) != sbfp:
            reason = "BFP_MISMATCH"
        elif is_inline:
            inline_compatible = {"PRODUCTION_DIRECTOR": ["CREATIVE_SCRIPT"],
                                 "PUBLISHING_PACKAGING": ["USER_REALIZED_CONTENT"]}
            inline_types = {"PRODUCTION_DIRECTOR": "SCRIPT_OR_EQUIVALENT_BEATS",
                            "PUBLISHING_PACKAGING": "CONTENT_BODY_OR_BEATS"}
            if source_kind != "USER_INLINE_CONFIRMED":
                reason = "SOURCE_NOT_CONFIRMED"
            elif source_turn != "CURRENT_TURN":
                reason = "SOURCE_TURN_MISMATCH"
            elif scap == cap:
                reason = "SELF_UPSTREAM_FORBIDDEN"
            elif scap not in inline_compatible.get(cap, []):
                reason = "CAPABILITY_INCOMPATIBLE"
            elif source_type != inline_types.get(cap):
                reason = "ARTIFACT_TYPE_MISMATCH"
        else:
            if scap not in compatible.get(cap, []):
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

        if reason:
            binding_status = "REJECTED"
            rejected.append(slot)
            binding.append({"slot": slot, "fp": sfp, "bfp": sbfp,
                            "upstream_capability": scap, "lineage": "REJECTED",
                            "reason": reason, "identity_source": source_kind})
        else:
            injected = '"%s": %s' % (slot, json.dumps(body, ensure_ascii=False))
            lines.append(injected)
            found[slot] = {"i": len(lines) - 1, "ind": "", "v": body, "st": "JSON"}
            binding_status = "BOUND"
            binding.append({"slot": slot, "upstream_capability": scap,
                            "fp": sfp, "bfp": sbfp,
                            "artifact_norm_len": len(nbody), "artifact_raw_len": len(body),
                            "produced_turn": None if is_inline else rec.get("turn"),
                            "accepted_turn": None if is_inline else rec.get("accepted_turn"),
                            "accepted_revision": None if is_inline else rec.get("accepted_rev"),
                            "source_turn": source_turn, "task_key": source_task,
                            "artifact_type": source_type, "persisted": not is_inline,
                            "accepted": False if is_inline else True,
                            "lineage": "BOUND",
                            "identity_source": "USER_INLINE_CURRENT_TURN" if is_inline
                            else "SELECTOR_DIRECT"})

'''
    data["code"] = data["code"][:start] + replacement + data["code"][end:]
    gap_anchor = (
        "    remaining_names = [gap_raw.get(c, c) for c in remaining] + unresolved + rejected\n"
    )
    gap_replacement = (
        "    if binding_status == \"BOUND\":\n"
        "        unresolved = [item for item in unresolved if item not in ARTIFACT_SLOTS]\n"
        + gap_anchor
    )
    if data["code"].count(gap_anchor) != 1:
        raise RuntimeError("fields gap anchor mismatch")
    data["code"] = data["code"].replace(gap_anchor, gap_replacement, 1)
    for variable in (
        "selected_source_kind", "selected_source_turn", "selected_artifact_type", "selected_task_key"
    ):
        data["variables"].append(
            {"value_selector": ["uapp_pick_upstream", variable], "variable": "selector_" + variable[9:]}
        )
    data["desc"] = "复核历史或当前轮原文身份；完整正文仅注入当前调用，不进入规范字段或自动持久化"


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


def patch_graph(graph: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    candidate = copy.deepcopy(graph)
    before = {node["id"]: node for node in graph["nodes"]}
    nodes = {node["id"]: node for node in candidate["nodes"]}
    if "uapp_inline_artifact" in nodes:
        raise RuntimeError("inline artifact node already exists")

    patch_selector(nodes["uapp_pick_upstream"])
    patch_fields(nodes["uapp_fields"])
    nodes["uapp_td24_block"]["data"]["code"] = NODES.BLOCK_CODE
    nodes["uapp_td24_block"]["data"]["desc"] = "停支回复只保留一个自然缺口并清除内部标识"

    selector_position = nodes["uapp_pick_upstream"]["position"]
    inline = code_node({"x": selector_position["x"] - 280, "y": selector_position["y"] + 145})
    candidate["nodes"].append(inline)

    edge = next(
        item for item in candidate["edges"]
        if item["source"] == "uapp_td24_correction" and item["target"] == "uapp_pick_upstream"
    )
    edge["id"] = "uapp_td24_correction-source-uapp_inline_artifact"
    edge["target"] = "uapp_inline_artifact"
    candidate["edges"].append(
        clone_edge(
            edge,
            "uapp_inline_artifact-source-uapp_pick_upstream",
            "uapp_inline_artifact",
            "uapp_pick_upstream",
        )
    )

    after = {node["id"]: node for node in candidate["nodes"]}
    touched = sorted(
        [node_id for node_id in before if canonical(before[node_id]) != canonical(after[node_id])]
        + [node_id + "(NEW)" for node_id in after if node_id not in before]
    )
    expected = sorted(
        ["uapp_pick_upstream", "uapp_fields", "uapp_td24_block", "uapp_inline_artifact(NEW)"]
    )
    if touched != expected:
        raise RuntimeError(f"Unexpected node impact: {touched}")
    protected_ids = [
        "m1_shadow", "m1_compiler", "uapp_m3", "uapp_hop", "uapp_seam", "uapp_state",
        "uapp_persist", "uapp_save", "uapp_delivery", "uapp_td24_correction",
    ]
    protected = {node_id: canonical(before[node_id]) == canonical(after[node_id]) for node_id in protected_ids}
    if not all(protected.values()):
        raise RuntimeError(f"Protected UAPP node drift: {protected}")
    return candidate, {
        "document": {
            "id": "UAPP_S5_INLINE_ARTIFACT_BUILD_v1.0",
            "task_id": "DIYU-V1-UNIFIED-DIFY-APPLICATION-001",
            "model_calls": 0,
        },
        "base_graph_md5": BASE_GRAPH_MD5,
        "nodes_touched": touched,
        "protected_nodes_equal": protected,
        "node_count": {"before": len(graph["nodes"]), "after": len(candidate["nodes"])},
        "edge_count": {"before": len(graph["edges"]), "after": len(candidate["edges"])},
        "conversation_variables_added": [],
        "candidate_graph_canonical_sha256": sha256_text(canonical(candidate)),
    }


def console_call(console: Any, method: str, path: str, body: dict[str, Any] | None = None) -> dict[str, Any]:
    status, response = console.call(method, path, body=body, timeout=900)
    if status not in (200, 201) or not isinstance(response, dict):
        raise RuntimeError(f"{method} {path}: {status} {str(response)[:500]}")
    return response


def publish(candidate: dict[str, Any], report: dict[str, Any]) -> None:
    if int(psql("select count(*) from workflow_runs where status='running';")) != 0:
        raise RuntimeError("Active workflows exist")
    console = DC.Console(env=DC.load_env(ENV_FILE))
    draft = console_call(console, "GET", f"/console/api/apps/{UAPP_APP_ID}/workflows/draft")
    console_call(
        console,
        "POST",
        f"/console/api/apps/{UAPP_APP_ID}/workflows/draft",
        {
            "graph": candidate,
            "features": draft.get("features") or {},
            "hash": draft.get("hash"),
            "environment_variables": draft.get("environment_variables") or [],
            "conversation_variables": draft.get("conversation_variables") or [],
        },
    )
    readback = console_call(console, "GET", f"/console/api/apps/{UAPP_APP_ID}/workflows/draft")
    if canonical(readback["graph"]) != canonical(candidate):
        raise RuntimeError("Draft readback differs")
    response = console_call(
        console,
        "POST",
        f"/console/api/apps/{UAPP_APP_ID}/workflows/publish",
        {"marked_name": "uapp-s5-inline-v1", "marked_comment": "current-turn confirmed artifact binding"},
    )
    current = published_graph()
    if canonical(current) != canonical(candidate):
        raise RuntimeError("Published graph differs")
    report.update(
        {
            "published": True,
            "publish_response": response,
            "published_graph_md5": graph_md5(),
            "published_graph_canonical_sha256": sha256_text(canonical(current)),
        }
    )


def write_report(report: dict[str, Any], mode: str) -> Path:
    output = OUTPUT_DIR / f"UAPP_S5_INLINE_ARTIFACT_BUILD_v1.0_{mode}.json"
    if output.exists():
        raise FileExistsError(f"Refusing to overwrite {output}")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return output


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--publish", action="store_true")
    args = parser.parse_args()
    if args.dry_run == args.publish:
        raise SystemExit("Choose exactly one mode")
    if graph_md5() != BASE_GRAPH_MD5:
        raise RuntimeError("Published UAPP differs from the frozen base")
    candidate, report = patch_graph(published_graph())
    mode = "DRY_RUN"
    if args.publish:
        publish(candidate, report)
        mode = "PUBLISHED"
    output = write_report(report, mode)
    LOGGER.info("%s %s", mode, output)
    return 0


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    raise SystemExit(main())
