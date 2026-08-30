#!/usr/bin/env python3
"""Full-seam deterministic controls for the UAPP inline-artifact candidate."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import logging
import re
from collections.abc import Callable
from pathlib import Path
from types import ModuleType
from typing import Any

LOGGER = logging.getLogger(__name__)
HERE = Path(__file__).resolve().parent
UAPP = HERE.parent
SCENARIOS = UAPP / "stages" / "UAPP_S5_FROZEN_SCENARIOS_v1.1.json"
RAW_V16 = UAPP / "evidence" / "stages" / "uapp_s5_v1_6" / "raw" / "UAPP-CAP-05.json"
OUTPUT = (
    UAPP
    / "evidence"
    / "stages"
    / "uapp_s5_inline_artifact_v1_0"
    / "controls"
    / "UAPP_S5_INLINE_ARTIFACT_CONTROLS_v1.0.json"
)


def load_module(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


BUILD = load_module("uapp_s5_inline_build_controls", HERE / "UAPP_S5_INLINE_ARTIFACT_BUILD_v1.0.py")


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def normalized(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def fnv1a64(value: str) -> str:
    result = 0xCBF29CE484222325
    for byte in value.encode("utf-8"):
        result = ((result ^ byte) * 0x100000001B3) & 0xFFFFFFFFFFFFFFFF
    return f"{result:016x}"


def node_main(code: str, name: str) -> Callable[..., dict[str, Any]]:
    namespace: dict[str, Any] = {}
    exec(compile(code, f"<{name}>", "exec"), namespace)
    function = namespace.get("main")
    if not callable(function):
        raise RuntimeError(f"{name} has no callable main")
    return function


def node_row(raw: dict[str, Any], node_id: str) -> dict[str, Any]:
    rows = raw["app_runs_in_window"]["UAPP"][0]["node_detail"]
    row = next(item for item in rows if item.get("node_id") == node_id)
    return {
        "inputs": json.loads(row["inputs"]),
        "outputs": json.loads(row["outputs"]),
    }


def turn(case_id: str) -> dict[str, Any]:
    document = json.loads(SCENARIOS.read_text(encoding="utf-8"))
    return next(item for item in document["turns"] if item["case_id"] == case_id)


def inline_call(
    function: Callable[..., dict[str, Any]],
    query: str,
    target: str,
    task_key: str = "task-a",
    correction_status: str = "NONE",
) -> dict[str, Any]:
    return function(query, target, task_key, correction_status)


def selector_call(
    function: Callable[..., dict[str, Any]],
    inline: dict[str, Any],
    query: str,
    target: str,
    task_key: str = "task-a",
    store_json: str = "",
    state_json: str = "{}",
    correction_status: str = "NONE",
) -> dict[str, Any]:
    return function(
        store_json,
        state_json,
        target,
        query,
        task_key,
        correction_status,
        inline.get("inline_status", ""),
        inline.get("inline_body", ""),
        inline.get("inline_artifact_type", ""),
        inline.get("inline_upstream_capability", ""),
        inline.get("inline_source_kind", ""),
        inline.get("inline_source_turn", ""),
        inline.get("inline_task_key", ""),
        inline.get("inline_fp", ""),
        inline.get("inline_bfp", ""),
        inline.get("inline_question", ""),
    )


def fields_call(
    function: Callable[..., dict[str, Any]],
    selected: dict[str, Any],
    query: str,
    target: str,
    capability_call: str,
    gaps_text: str,
    snapshot_json: str = "{}",
    state_json: str = "{}",
    task_key: str = "task-a",
) -> dict[str, Any]:
    return function(
        state_json,
        task_key,
        capability_call,
        gaps_text,
        target,
        query,
        snapshot_json,
        selected.get("upstream_delivery", ""),
        selected.get("selected_fp", ""),
        selected.get("selected_bfp", ""),
        selected.get("selected_capability", ""),
        selected.get("selection_status", ""),
        "NONE",
        "用户明确要求执行目标能力",
        selected.get("selected_source_kind", ""),
        selected.get("selected_source_turn", ""),
        selected.get("selected_artifact_type", ""),
        selected.get("selected_task_key", ""),
    )


def injected_body(capability_call: str, slot: str) -> str:
    match = re.search(rf'^"{re.escape(slot)}": (.+)$', capability_call, re.MULTILINE)
    if not match:
        return ""
    value = json.loads(match.group(1))
    return value if isinstance(value, str) else ""


def historical_fixture(body: str, task_key: str = "task-a", stale: bool = False) -> tuple[str, str]:
    compact = normalized(body)
    fp = fnv1a64(compact[:256])
    bfp = fnv1a64(compact)
    state = {
        "task_key": task_key,
        "rev": 2,
        "fields": {},
        "asked": [],
        "events": [],
        "artifacts": [
            {
                "fp": fp,
                "cap": "CREATIVE_SCRIPT",
                "turn": 1,
                "task_key": task_key,
                "accepted": True,
                "accepted_turn": 2,
                "accepted_rev": 2,
                "stale": stale,
                "dep": {},
            }
        ],
    }
    store = {
        "items": [
            {"fp": fp, "bfp": bfp, "cap": "CREATIVE_SCRIPT", "body": body, "task_key": task_key}
        ]
    }
    return json.dumps(store, ensure_ascii=False), json.dumps(state, ensure_ascii=False)


def build_report() -> dict[str, Any]:
    base = BUILD.published_graph()
    candidate, build_report = BUILD.patch_graph(base)
    nodes = {node["id"]: node for node in candidate["nodes"]}
    inline = node_main(nodes["uapp_inline_artifact"]["data"]["code"], "inline")
    selector = node_main(nodes["uapp_pick_upstream"]["data"]["code"], "selector")
    fields = node_main(nodes["uapp_fields"]["data"]["code"], "fields")
    block = node_main(nodes["uapp_td24_block"]["data"]["code"], "block")
    delivery = node_main(nodes["uapp_delivery"]["data"]["code"], "delivery")

    cap05 = turn("UAPP-CAP-05")
    cap06 = turn("UAPP-CAP-06")
    raw = json.loads(RAW_V16.read_text(encoding="utf-8"))
    hop = node_row(raw, "uapp_hop")
    route = node_row(raw, "uapp_route")
    hop_outputs = hop["outputs"]
    route_inputs = route["inputs"]

    script_inline = inline_call(inline, cap05["query"], "PRODUCTION_DIRECTOR")
    script_selected = selector_call(selector, script_inline, cap05["query"], "PRODUCTION_DIRECTOR")
    script_fields = fields_call(
        fields,
        script_selected,
        cap05["query"],
        "PRODUCTION_DIRECTOR",
        str(hop_outputs.get("capability_call") or ""),
        str(hop_outputs.get("extraction_gaps_text") or ""),
        str(route_inputs.get("snapshot_json") or "{}"),
    )
    script_body = str(script_inline.get("inline_body") or "")
    script_injected = injected_body(script_fields["capability_call"], "script_or_equivalent_beats")

    content_inline = inline_call(inline, cap06["query"], "PUBLISHING_PACKAGING")
    content_selected = selector_call(selector, content_inline, cap06["query"], "PUBLISHING_PACKAGING")
    content_fields = fields_call(
        fields,
        content_selected,
        cap06["query"],
        "PUBLISHING_PACKAGING",
        "provenance:\n  target_capability: PUBLISHING_PACKAGING\nplatform: NOT_LOCKED",
        "content_body_or_beats",
    )
    content_body = str(content_inline.get("inline_body") or "")
    content_injected = injected_body(content_fields["capability_call"], "content_body_or_beats")

    historical_body = "这是已经接受并保存在同一任务里的完整脚本正文，包含开头、主要内容、承诺边界和自然收尾。"
    store_json, state_json = historical_fixture(historical_body)
    historical_query = "这版口播稿可以，基于它告诉我这条该怎么制作。"
    none_inline = inline_call(inline, historical_query, "PRODUCTION_DIRECTOR")
    historical_selected = selector_call(
        selector,
        none_inline,
        historical_query,
        "PRODUCTION_DIRECTOR",
        store_json=store_json,
        state_json=state_json,
    )
    historical_fields = fields_call(
        fields,
        historical_selected,
        historical_query,
        "PRODUCTION_DIRECTOR",
        "provenance:\n  target_capability: PRODUCTION_DIRECTOR",
        "script_or_equivalent_beats",
        state_json=state_json,
    )

    unconfirmed_query = cap05["query"].replace("确认可用", "待讨论").replace("已确认脚本", "这份脚本")
    incomplete_query = cap05["query"].replace(script_body, "稍后补完整脚本", 1)
    ambiguous_query = cap05["query"].replace(
        f"“{script_body}”", f"“{script_body}”\n另一份脚本：“{script_body}”", 1
    )
    tampered_task = dict(script_selected)
    tampered_task["selected_task_key"] = "task-b"
    tampered_fp = dict(script_selected)
    tampered_fp["selected_fp"] = "0000000000000000"
    tampered_bfp = dict(script_selected)
    tampered_bfp["selected_bfp"] = "0000000000000000"
    tampered_type = dict(script_selected)
    tampered_type["selected_artifact_type"] = "CONTENT_BODY_OR_BEATS"

    stale_store, stale_state = historical_fixture(historical_body, stale=True)
    stale_selected = selector_call(
        selector,
        none_inline,
        historical_query,
        "PRODUCTION_DIRECTOR",
        store_json=stale_store,
        state_json=stale_state,
    )
    cross_store, cross_state = historical_fixture(historical_body, task_key="task-b")
    cross_selected = selector_call(
        selector,
        none_inline,
        historical_query,
        "PRODUCTION_DIRECTOR",
        store_json=cross_store,
        state_json=cross_state,
    )

    scrubbed_block = block(
        "NONE",
        "",
        "缺少 script_or_equivalent_beats，不能调用 PRODUCTION_DIRECTOR，状态是 STALE。",
        "script_or_equivalent_beats",
    )
    scrubbed_delivery = delivery(
        "PRODUCTION_DIRECTOR",
        "PRODUCTION_DIRECTOR 已完成，script_or_equivalent_beats 状态 PASS。",
        "DELIVERED",
        "[]",
        "",
        "",
        "CAPABILITY",
        "",
        "",
        "",
        "",
    )

    controls = {
        "P01_cap05_source_ready": script_inline.get("inline_status") == "INLINE_READY",
        "P02_cap05_source_metadata_complete": all(
            script_inline.get(key)
            for key in (
                "inline_body", "inline_artifact_type", "inline_source_kind", "inline_source_turn",
                "inline_task_key", "inline_fp", "inline_bfp",
            )
        ),
        "P03_cap05_selector_inline_selected": script_selected.get("selection_status") == "INLINE_SELECTED",
        "P04_cap05_target_not_self_upstream": script_selected.get("selected_capability") == "CREATIVE_SCRIPT",
        "P05_cap05_fields_bound": script_fields.get("artifact_binding_status") == "BOUND",
        "P06_cap05_exact_body_injected": script_injected == script_body and bool(script_body),
        "P07_cap05_input_sha256_exact": sha256_text(script_injected) == sha256_text(script_body),
        "P08_cap05_artifact_gap_removed": "script_or_equivalent_beats" not in script_fields.get("gaps_text", ""),
        "P09_cap05_not_auto_persisted": (
            json.loads(script_fields["pending_state_json"]).get("artifacts") == []
            and json.loads(script_fields["upstream_binding_json"])[0].get("persisted") is False
            and json.loads(script_fields["upstream_binding_json"])[0].get("accepted") is False
        ),
        "P10_artifact_not_in_canonical_fields": "script_or_equivalent_beats"
        not in json.loads(script_fields["pending_state_json"]).get("fields", {}),
        "P11_cap06_source_ready": content_inline.get("inline_status") == "INLINE_READY",
        "P12_cap06_selector_inline_selected": content_selected.get("selection_status") == "INLINE_SELECTED",
        "P13_cap06_fields_bound": content_fields.get("artifact_binding_status") == "BOUND",
        "P14_cap06_exact_body_injected": content_injected == content_body and bool(content_body),
        "P15_historical_accepted_path_preserved": (
            historical_selected.get("selection_status") == "SELECTED"
            and historical_fields.get("artifact_binding_status") == "BOUND"
            and injected_body(historical_fields["capability_call"], "script_or_equivalent_beats")
            == historical_body
        ),
        "P16_ordinary_hop_fields_preserved": "`production_profile`:" in script_fields["capability_call"],
        "P17_pre_seam_eligibility": script_fields.get("artifact_binding_status") != "REJECTED",
        "P18_protected_uapp_nodes_unchanged": all(build_report["protected_nodes_equal"].values()),
        "N01_unconfirmed_rejected": inline_call(
            inline, unconfirmed_query, "PRODUCTION_DIRECTOR"
        ).get("inline_reason")
        == "NOT_CONFIRMED",
        "N02_incomplete_rejected": inline_call(
            inline, incomplete_query, "PRODUCTION_DIRECTOR"
        ).get("inline_reason")
        == "BODY_INCOMPLETE",
        "N03_ambiguous_rejected": inline_call(
            inline, ambiguous_query, "PRODUCTION_DIRECTOR"
        ).get("inline_reason")
        == "AMBIGUOUS",
        "N04_correction_rejected": inline_call(
            inline, cap05["query"], "PRODUCTION_DIRECTOR", correction_status="REJECTED"
        ).get("inline_reason")
        == "CORRECTION_REJECTED",
        "N05_task_mismatch_rejected_by_fields": fields_call(
            fields, tampered_task, cap05["query"], "PRODUCTION_DIRECTOR", "", "script_or_equivalent_beats"
        ).get("artifact_binding_status")
        == "REJECTED",
        "N06_fp_mismatch_rejected_by_fields": fields_call(
            fields, tampered_fp, cap05["query"], "PRODUCTION_DIRECTOR", "", "script_or_equivalent_beats"
        ).get("artifact_binding_status")
        == "REJECTED",
        "N07_bfp_mismatch_rejected_by_fields": fields_call(
            fields, tampered_bfp, cap05["query"], "PRODUCTION_DIRECTOR", "", "script_or_equivalent_beats"
        ).get("artifact_binding_status")
        == "REJECTED",
        "N08_type_mismatch_rejected_by_fields": fields_call(
            fields, tampered_type, cap05["query"], "PRODUCTION_DIRECTOR", "", "script_or_equivalent_beats"
        ).get("artifact_binding_status")
        == "REJECTED",
        "N09_stale_historical_rejected": stale_selected.get("selection_status") == "NO_LEGAL_UPSTREAM",
        "N10_cross_task_historical_rejected": cross_selected.get("selection_status") == "NO_LEGAL_UPSTREAM",
        "N11_block_response_scrubbed": not any(
            token in scrubbed_block["final_text"]
            for token in ("PRODUCTION_DIRECTOR", "script_or_equivalent_beats", "STALE")
        ),
        "N12_delivery_response_scrubbed": not any(
            token in scrubbed_delivery["final_text"]
            for token in ("PRODUCTION_DIRECTOR", "script_or_equivalent_beats", "PASS", "DELIVERED")
        ),
    }
    return {
        "document": {
            "id": "UAPP_S5_INLINE_ARTIFACT_CONTROLS_v1.0",
            "task_id": "DIYU-V1-UNIFIED-DIFY-APPLICATION-001",
            "model_calls": 0,
            "dify_writes": 0,
        },
        "candidate_graph_canonical_sha256": build_report["candidate_graph_canonical_sha256"],
        "controls": controls,
        "passed": sum(controls.values()),
        "total": len(controls),
        "all_pass": all(controls.values()),
        "cap05": {
            "source_body_length": len(script_body),
            "source_body_sha256": sha256_text(script_body),
            "injected_body_length": len(script_injected),
            "injected_body_sha256": sha256_text(script_injected),
            "binding": json.loads(script_fields["upstream_binding_json"]),
        },
        "cap06": {
            "source_body_length": len(content_body),
            "source_body_sha256": sha256_text(content_body),
            "injected_body_length": len(content_injected),
            "injected_body_sha256": sha256_text(content_injected),
            "binding": json.loads(content_fields["upstream_binding_json"]),
        },
        "protected_nodes_equal": build_report["protected_nodes_equal"],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    report = build_report()
    LOGGER.info("controls %d/%d", report["passed"], report["total"])
    failed = [name for name, passed in report["controls"].items() if not passed]
    if failed:
        LOGGER.error("failed controls: %s", ", ".join(failed))
    if args.write:
        if OUTPUT.exists():
            raise FileExistsError(f"Refusing to overwrite {OUTPUT}")
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0 if report["all_pass"] else 1


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    raise SystemExit(main())
