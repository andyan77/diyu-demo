#!/usr/bin/env python3
"""Build the only authorized successor for the UAPP inline-artifact seam."""

from __future__ import annotations

import argparse
import copy
import importlib.util
import json
import logging
from pathlib import Path
from types import ModuleType
from typing import Any

LOGGER = logging.getLogger(__name__)
HERE = Path(__file__).resolve().parent
UAPP = HERE.parent
BASE_GRAPH_MD5 = "f7d9857323823b64d288455e1b67cf80"
OUTPUT_DIR = UAPP / "evidence" / "stages" / "uapp_s5_inline_artifact_successor_v1_0" / "build"


def load_module(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


BASE = load_module("uapp_s5_inline_base_build", HERE / "UAPP_S5_INLINE_ARTIFACT_BUILD_v1.0.py")
NODES = load_module(
    "uapp_s5_inline_successor_nodes",
    HERE / "UAPP_S5_INLINE_ARTIFACT_SUCCESSOR_NODES_v1.0.py",
)


def patch_inline(node: dict[str, Any]) -> None:
    data = node["data"]
    data["code"] = NODES.INLINE_CODE
    data["outputs"]["inline_companion_json"] = {"children": None, "type": "string"}
    data["desc"] = "本轮完整产物与原话支持的调用伴随字段同源绑定；不自动持久化"


def patch_selector(node: dict[str, Any]) -> None:
    data = node["data"]
    old_signature = (
        "         inline_source_kind, inline_source_turn, inline_task_key, inline_fp, inline_bfp,\n"
        "         inline_question):"
    )
    new_signature = (
        "         inline_source_kind, inline_source_turn, inline_task_key, inline_fp, inline_bfp,\n"
        "         inline_question, inline_companion_json):"
    )
    if data["code"].count(old_signature) != 1:
        raise RuntimeError("selector successor signature anchor mismatch")
    data["code"] = data["code"].replace(old_signature, new_signature, 1)

    fail_anchor = (
        '            "selected_source_turn": "", "selected_artifact_type": "",\n'
        '            "selected_task_key": "", "selection_question": question,\n'
    )
    fail_replacement = (
        '            "selected_source_turn": "", "selected_artifact_type": "",\n'
        '            "selected_task_key": "", "selected_companion_json": "",\n'
        '            "selection_question": question,\n'
    )
    if data["code"].count(fail_anchor) != 1:
        raise RuntimeError("selector successor fail anchor mismatch")
    data["code"] = data["code"].replace(fail_anchor, fail_replacement, 1)

    inline_anchor = (
        '                "selected_artifact_type": inline_artifact_type,\n'
        '                "selected_task_key": inline_task_key, "selection_question": "",\n'
    )
    inline_replacement = (
        '                "selected_artifact_type": inline_artifact_type,\n'
        '                "selected_task_key": inline_task_key,\n'
        '                "selected_companion_json": inline_companion_json,\n'
        '                "selection_question": "",\n'
    )
    if data["code"].count(inline_anchor) != 1:
        raise RuntimeError("selector successor inline return anchor mismatch")
    data["code"] = data["code"].replace(inline_anchor, inline_replacement, 1)

    historical_anchor = (
        '            "selected_artifact_type": sel["cap"],\n'
        '            "selected_task_key": tk, "selection_question": "",\n'
    )
    historical_replacement = (
        '            "selected_artifact_type": sel["cap"],\n'
        '            "selected_task_key": tk, "selected_companion_json": "",\n'
        '            "selection_question": "",\n'
    )
    if data["code"].count(historical_anchor) != 1:
        raise RuntimeError("selector successor historical return anchor mismatch")
    data["code"] = data["code"].replace(historical_anchor, historical_replacement, 1)
    data["variables"].append(
        {
            "value_selector": ["uapp_inline_artifact", "inline_companion_json"],
            "variable": "inline_companion_json",
        }
    )
    data["outputs"]["selected_companion_json"] = {"children": None, "type": "string"}
    data["desc"] = "历史正文或本轮同源完整产物；伴随字段元数据逐跳保真并在 fields 复核"


def patch_fields(node: dict[str, Any]) -> None:
    data = node["data"]
    old_signature = (
        "         selector_source_kind, selector_source_turn, selector_artifact_type,\n"
        "         selector_task_key):"
    )
    new_signature = (
        "         selector_source_kind, selector_source_turn, selector_artifact_type,\n"
        "         selector_task_key, selector_companion_json):"
    )
    if data["code"].count(old_signature) != 1:
        raise RuntimeError("fields successor signature anchor mismatch")
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
        companion_values = {}
        companion_record = {}
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
                try:
                    companion_record = json.loads(selector_companion_json or "{}")
                except Exception:
                    companion_record = {}
                raw_values = companion_record.get("values") \
                    if isinstance(companion_record, dict) else None
                required = ["content.origin_mode", "content.promise"] \
                    if cap == "PRODUCTION_DIRECTOR" else []
                if companion_record.get("task_key") != tk:
                    reason = "COMPANION_CROSS_TASK"
                elif companion_record.get("source_kind") != source_kind:
                    reason = "COMPANION_SOURCE_MISMATCH"
                elif companion_record.get("source_turn") != source_turn:
                    reason = "COMPANION_TURN_MISMATCH"
                elif companion_record.get("artifact_bfp") != sbfp:
                    reason = "COMPANION_BFP_MISMATCH"
                elif not isinstance(raw_values, dict):
                    reason = "COMPANION_VALUES_INVALID"
                else:
                    for cid, val in raw_values.items():
                        if cid in ("content.origin_mode", "content.promise") and \
                                isinstance(val, str) and _norm(val):
                            companion_values[cid] = _norm(val)
                    missing_companions = [cid for cid in required
                                          if cid not in companion_values]
                    unsupported = [cid for cid, val in companion_values.items()
                                   if _norm(val) not in _norm(uq)]
                    if missing_companions:
                        reason = "COMPANION_MISSING:" + ",".join(missing_companions)
                    elif unsupported:
                        reason = "COMPANION_UNSUPPORTED:" + ",".join(unsupported)
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
            if is_inline:
                for cid in sorted(companion_values):
                    val = companion_values[cid]
                    offered = offer(cid, val, "A", "USER_UTTERANCE",
                                    "TURN%d.user_request" % rev)
                    if offered in ("NEW", "UPDATED", "SAME", "REFINED"):
                        answered.append(cid)
                    _set(lines, found, cid, val)
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
                            "companion_fields": sorted(companion_values),
                            "lineage": "BOUND",
                            "identity_source": "USER_INLINE_CURRENT_TURN" if is_inline
                            else "SELECTOR_DIRECT"})

'''
    data["code"] = data["code"][:start] + replacement + data["code"][end:]
    data["variables"].append(
        {
            "value_selector": ["uapp_pick_upstream", "selected_companion_json"],
            "variable": "selector_companion_json",
        }
    )
    data["desc"] = "同源复核完整正文和调用伴随字段；正文不入规范字段且不自动持久化"


def patch_graph(graph: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    candidate = copy.deepcopy(graph)
    before = {node["id"]: node for node in graph["nodes"]}
    nodes = {node["id"]: node for node in candidate["nodes"]}
    patch_inline(nodes["uapp_inline_artifact"])
    patch_selector(nodes["uapp_pick_upstream"])
    patch_fields(nodes["uapp_fields"])
    after = {node["id"]: node for node in candidate["nodes"]}
    touched = sorted(
        node_id for node_id in before
        if BASE.canonical(before[node_id]) != BASE.canonical(after[node_id])
    )
    expected = ["uapp_fields", "uapp_inline_artifact", "uapp_pick_upstream"]
    if touched != expected:
        raise RuntimeError(f"Unexpected successor impact: {touched}")
    protected_ids = [
        "m1_shadow", "m1_compiler", "uapp_m3", "uapp_hop", "uapp_seam", "uapp_state",
        "uapp_persist", "uapp_save", "uapp_delivery", "uapp_td24_correction",
        "uapp_td24_block",
    ]
    protected = {
        node_id: BASE.canonical(before[node_id]) == BASE.canonical(after[node_id])
        for node_id in protected_ids
    }
    if not all(protected.values()):
        raise RuntimeError(f"Protected UAPP node drift: {protected}")
    return candidate, {
        "document": {
            "id": "UAPP_S5_INLINE_ARTIFACT_SUCCESSOR_BUILD_v1.0",
            "task_id": "DIYU-V1-UNIFIED-DIFY-APPLICATION-001",
            "model_calls": 0,
            "successor_iteration": "1/1",
        },
        "base_graph_md5": BASE_GRAPH_MD5,
        "nodes_touched": touched,
        "protected_nodes_equal": protected,
        "node_count": {"before": len(graph["nodes"]), "after": len(candidate["nodes"])},
        "edge_count": {"before": len(graph["edges"]), "after": len(candidate["edges"])},
        "conversation_variables_added": [],
        "candidate_graph_canonical_sha256": BASE.sha256_text(BASE.canonical(candidate)),
    }


def publish(candidate: dict[str, Any], report: dict[str, Any]) -> None:
    if int(BASE.psql("select count(*) from workflow_runs where status='running';")) != 0:
        raise RuntimeError("Active workflows exist")
    console = BASE.DC.Console(env=BASE.DC.load_env(BASE.ENV_FILE))
    draft = BASE.console_call(console, "GET", f"/console/api/apps/{BASE.UAPP_APP_ID}/workflows/draft")
    BASE.console_call(
        console,
        "POST",
        f"/console/api/apps/{BASE.UAPP_APP_ID}/workflows/draft",
        {
            "graph": candidate,
            "features": draft.get("features") or {},
            "hash": draft.get("hash"),
            "environment_variables": draft.get("environment_variables") or [],
            "conversation_variables": draft.get("conversation_variables") or [],
        },
    )
    readback = BASE.console_call(
        console, "GET", f"/console/api/apps/{BASE.UAPP_APP_ID}/workflows/draft"
    )
    if BASE.canonical(readback["graph"]) != BASE.canonical(candidate):
        raise RuntimeError("Draft readback differs")
    response = BASE.console_call(
        console,
        "POST",
        f"/console/api/apps/{BASE.UAPP_APP_ID}/workflows/publish",
        {
            "marked_name": "uapp-s5-inline-successor-v1",
            "marked_comment": "same-source companion normalization for current-turn artifact",
        },
    )
    current = BASE.published_graph()
    if BASE.canonical(current) != BASE.canonical(candidate):
        raise RuntimeError("Published graph differs")
    report.update(
        {
            "published": True,
            "publish_response": response,
            "published_graph_md5": BASE.graph_md5(),
            "published_graph_canonical_sha256": BASE.sha256_text(BASE.canonical(current)),
        }
    )


def write_report(report: dict[str, Any], mode: str) -> Path:
    output = OUTPUT_DIR / f"UAPP_S5_INLINE_ARTIFACT_SUCCESSOR_BUILD_v1.0_{mode}.json"
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
    if BASE.graph_md5() != BASE_GRAPH_MD5:
        raise RuntimeError("Published UAPP differs from the frozen successor base")
    candidate, report = patch_graph(BASE.published_graph())
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
