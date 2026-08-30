#!/usr/bin/env python3
"""Deterministic controls for the only authorized inline-artifact successor."""

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
OUTPUT = (
    UAPP
    / "evidence"
    / "stages"
    / "uapp_s5_inline_artifact_successor_v1_0"
    / "controls"
    / "UAPP_S5_INLINE_ARTIFACT_SUCCESSOR_CONTROLS_v1.0.json"
)


def load_module(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


BUILD = load_module(
    "uapp_s5_inline_successor_build_controls",
    HERE / "UAPP_S5_INLINE_ARTIFACT_SUCCESSOR_BUILD_v1.0.py",
)
BASE_CONTROLS = load_module(
    "uapp_s5_inline_base_controls",
    HERE / "UAPP_S5_INLINE_ARTIFACT_CONTROLS_v1.0.py",
)


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def turn(case_id: str) -> dict[str, Any]:
    document = json.loads(SCENARIOS.read_text(encoding="utf-8"))
    return next(item for item in document["turns"] if item["case_id"] == case_id)


def selector_call(
    function: Callable[..., dict[str, Any]],
    inline: dict[str, Any],
    query: str,
    target: str,
    task_key: str = "task-a",
    store_json: str = "",
    state_json: str = "{}",
) -> dict[str, Any]:
    return function(
        store_json,
        state_json,
        target,
        query,
        task_key,
        "NONE",
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
        inline.get("inline_companion_json", ""),
    )


def fields_call(
    function: Callable[..., dict[str, Any]],
    selected: dict[str, Any],
    query: str,
    target: str,
    capability_call: str,
    gaps_text: str,
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
        "{}",
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
        selected.get("selected_companion_json", ""),
    )


def field_value(capability_call: str, key: str) -> str:
    match = re.search(rf"^`{re.escape(key)}`:\s*(.+)$", capability_call, re.MULTILINE)
    return match.group(1).strip() if match else ""


def json_body(capability_call: str, slot: str) -> str:
    return BASE_CONTROLS.injected_body(capability_call, slot)


def mutate_companion(selected: dict[str, Any], mutation: Callable[[dict[str, Any]], None]) -> dict[str, Any]:
    changed = dict(selected)
    companion = json.loads(str(selected.get("selected_companion_json") or "{}"))
    mutation(companion)
    changed["selected_companion_json"] = json.dumps(
        companion, ensure_ascii=False, sort_keys=True
    )
    return changed


def build_report() -> dict[str, Any]:
    base = BUILD.BASE.published_graph()
    candidate, build_report = BUILD.patch_graph(base)
    nodes = {node["id"]: node for node in candidate["nodes"]}
    inline = BASE_CONTROLS.node_main(nodes["uapp_inline_artifact"]["data"]["code"], "inline")
    selector = BASE_CONTROLS.node_main(nodes["uapp_pick_upstream"]["data"]["code"], "selector")
    fields = BASE_CONTROLS.node_main(nodes["uapp_fields"]["data"]["code"], "fields")

    cap05 = turn("UAPP-CAP-05")
    cap06 = turn("UAPP-CAP-06")
    cap05_query = str(cap05["query"])
    cap06_query = str(cap06["query"])
    script_inline = inline(cap05_query, "PRODUCTION_DIRECTOR", "task-a", "NONE")
    script_selected = selector_call(
        selector, script_inline, cap05_query, "PRODUCTION_DIRECTOR"
    )
    base_call = (
        "provenance:\n  target_capability: PRODUCTION_DIRECTOR\n"
        "`production_profile`: 两个人制作，室内门店拍摄，半天完成\n"
        "`time_window`: 半天\n"
        "`explicit_non_promise`: 不承诺显瘦"
    )
    script_fields = fields_call(
        fields,
        script_selected,
        cap05_query,
        "PRODUCTION_DIRECTOR",
        base_call,
        "content_origin_mode；content_promise；script_or_equivalent_beats",
    )
    script_body = str(script_inline.get("inline_body") or "")
    script_input = json_body(script_fields["capability_call"], "script_or_equivalent_beats")
    origin = field_value(script_fields["capability_call"], "content_origin_mode")
    promise = field_value(script_fields["capability_call"], "content_promise")
    pending = json.loads(script_fields["pending_state_json"])
    binding = json.loads(script_fields["upstream_binding_json"])

    content_inline = inline(cap06_query, "PUBLISHING_PACKAGING", "task-a", "NONE")
    content_selected = selector_call(
        selector, content_inline, cap06_query, "PUBLISHING_PACKAGING"
    )
    content_fields = fields_call(
        fields,
        content_selected,
        cap06_query,
        "PUBLISHING_PACKAGING",
        "provenance:\n  target_capability: PUBLISHING_PACKAGING\nplatform: xiaohongshu",
        "content_body_or_beats",
    )
    content_body = str(content_inline.get("inline_body") or "")
    content_input = json_body(content_fields["capability_call"], "content_body_or_beats")

    missing_origin = mutate_companion(
        script_selected,
        lambda value: value["values"].pop("content.origin_mode"),
    )
    missing_promise = mutate_companion(
        script_selected,
        lambda value: value["values"].pop("content.promise"),
    )
    wrong_task = mutate_companion(
        script_selected,
        lambda value: value.__setitem__("task_key", "task-b"),
    )
    wrong_source = mutate_companion(
        script_selected,
        lambda value: value.__setitem__("source_kind", "MODEL_EXTRACTION"),
    )
    wrong_turn = mutate_companion(
        script_selected,
        lambda value: value.__setitem__("source_turn", "PRIOR_TURN"),
    )
    wrong_bfp = mutate_companion(
        script_selected,
        lambda value: value.__setitem__("artifact_bfp", "0000000000000000"),
    )
    unsupported_origin = mutate_companion(
        script_selected,
        lambda value: value["values"].__setitem__("content.origin_mode", "户外街拍"),
    )
    unsupported_promise = mutate_companion(
        script_selected,
        lambda value: value["values"].__setitem__("content.promise", "保证显瘦"),
    )

    historical_body = "这是已接受的完整脚本正文，包含明确的内容承诺、表达边界、开头、主体和自然收尾。"
    store_json, state_json = BASE_CONTROLS.historical_fixture(historical_body)
    no_inline = inline(
        "这版口播稿可以，基于它告诉我这条该怎么制作。",
        "PRODUCTION_DIRECTOR",
        "task-a",
        "NONE",
    )
    historical_selected = selector_call(
        selector,
        no_inline,
        "这版口播稿可以，基于它告诉我这条该怎么制作。",
        "PRODUCTION_DIRECTOR",
        store_json=store_json,
        state_json=state_json,
    )
    historical_fields = fields_call(
        fields,
        historical_selected,
        "这版口播稿可以，基于它告诉我这条该怎么制作。",
        "PRODUCTION_DIRECTOR",
        "provenance:\n  target_capability: PRODUCTION_DIRECTOR",
        "script_or_equivalent_beats",
        state_json=state_json,
    )

    seam_vars = nodes["uapp_seam"]["data"].get("variables") or []
    seam_call_binding = any(
        item.get("variable") == "capability_call"
        and item.get("value_selector") == ["uapp_fields", "capability_call"]
        for item in seam_vars
    )
    controls = {
        "P01_cap05_inline_ready": script_inline.get("inline_status") == "INLINE_READY",
        "P02_companion_same_task": json.loads(script_inline["inline_companion_json"])["task_key"] == "task-a",
        "P03_origin_exact_user_text": origin == "室内门店拍摄" and origin in cap05_query,
        "P04_promise_exact_user_text": (
            promise == "我们只展示真实上身效果，不承诺显瘦。" and promise in cap05_query
        ),
        "P05_selector_preserves_companion": (
            script_selected.get("selected_companion_json") == script_inline.get("inline_companion_json")
        ),
        "P06_fields_bound": script_fields.get("artifact_binding_status") == "BOUND",
        "P07_script_byte_identity": script_input == script_body and bool(script_body),
        "P08_script_sha_identity": sha256_text(script_input) == sha256_text(script_body),
        "P09_pd_actual_input_path_bound": seam_call_binding,
        "P10_companion_gaps_removed": not any(
            key in script_fields.get("gaps_text", "")
            for key in ("content_origin_mode", "content_promise", "script_or_equivalent_beats")
        ),
        "P11_companion_user_source_level": all(
            pending["fields"][key].get("lvl") == "A"
            and pending["fields"][key].get("kind") == "USER_UTTERANCE"
            and pending["fields"][key].get("ref") == "TURN1.user_request"
            for key in ("content.origin_mode", "content.promise")
        ),
        "P12_artifact_not_auto_persisted": (
            pending.get("artifacts") == []
            and binding[0].get("persisted") is False
            and binding[0].get("accepted") is False
        ),
        "P13_artifact_body_not_canonical_field": (
            "script_or_equivalent_beats" not in pending.get("fields", {})
        ),
        "P14_cap06_inline_ready": content_inline.get("inline_status") == "INLINE_READY",
        "P15_cap06_bound": content_fields.get("artifact_binding_status") == "BOUND",
        "P16_cap06_body_identity": content_input == content_body and bool(content_body),
        "P17_historical_path_unchanged": (
            historical_selected.get("selection_status") == "SELECTED"
            and historical_fields.get("artifact_binding_status") == "BOUND"
            and json_body(historical_fields["capability_call"], "script_or_equivalent_beats")
            == historical_body
        ),
        "P18_protected_nodes_unchanged": all(build_report["protected_nodes_equal"].values()),
        "N01_missing_origin_rejected": fields_call(
            fields, missing_origin, cap05_query, "PRODUCTION_DIRECTOR", base_call,
            "content_origin_mode；content_promise；script_or_equivalent_beats",
        ).get("artifact_binding_status") == "REJECTED",
        "N02_missing_promise_rejected": fields_call(
            fields, missing_promise, cap05_query, "PRODUCTION_DIRECTOR", base_call,
            "content_origin_mode；content_promise；script_or_equivalent_beats",
        ).get("artifact_binding_status") == "REJECTED",
        "N03_companion_task_mismatch_rejected": fields_call(
            fields, wrong_task, cap05_query, "PRODUCTION_DIRECTOR", base_call,
            "content_origin_mode；content_promise；script_or_equivalent_beats",
        ).get("artifact_binding_status") == "REJECTED",
        "N04_companion_source_mismatch_rejected": fields_call(
            fields, wrong_source, cap05_query, "PRODUCTION_DIRECTOR", base_call,
            "content_origin_mode；content_promise；script_or_equivalent_beats",
        ).get("artifact_binding_status") == "REJECTED",
        "N05_companion_turn_mismatch_rejected": fields_call(
            fields, wrong_turn, cap05_query, "PRODUCTION_DIRECTOR", base_call,
            "content_origin_mode；content_promise；script_or_equivalent_beats",
        ).get("artifact_binding_status") == "REJECTED",
        "N06_companion_bfp_mismatch_rejected": fields_call(
            fields, wrong_bfp, cap05_query, "PRODUCTION_DIRECTOR", base_call,
            "content_origin_mode；content_promise；script_or_equivalent_beats",
        ).get("artifact_binding_status") == "REJECTED",
        "N07_unsupported_origin_rejected": fields_call(
            fields, unsupported_origin, cap05_query, "PRODUCTION_DIRECTOR", base_call,
            "content_origin_mode；content_promise；script_or_equivalent_beats",
        ).get("artifact_binding_status") == "REJECTED",
        "N08_unsupported_promise_rejected": fields_call(
            fields, unsupported_promise, cap05_query, "PRODUCTION_DIRECTOR", base_call,
            "content_origin_mode；content_promise；script_or_equivalent_beats",
        ).get("artifact_binding_status") == "REJECTED",
        "N09_target_not_self_upstream": script_selected.get("selected_capability") != "PRODUCTION_DIRECTOR",
        "N10_no_new_conversation_variables": build_report["conversation_variables_added"] == [],
    }
    pairings = {
        "P03_origin_exact_user_text": "N07_unsupported_origin_rejected",
        "P04_promise_exact_user_text": "N08_unsupported_promise_rejected",
        "P05_selector_preserves_companion": "N04_companion_source_mismatch_rejected",
        "P06_fields_bound": "N01_missing_origin_rejected",
        "P07_script_byte_identity": "N06_companion_bfp_mismatch_rejected",
        "P11_companion_user_source_level": "N05_companion_turn_mismatch_rejected",
        "P12_artifact_not_auto_persisted": "N03_companion_task_mismatch_rejected",
    }
    return {
        "document": {
            "id": "UAPP_S5_INLINE_ARTIFACT_SUCCESSOR_CONTROLS_v1.0",
            "task_id": "DIYU-V1-UNIFIED-DIFY-APPLICATION-001",
            "model_calls": 0,
            "dify_writes": 0,
            "successor_iteration": "1/1",
        },
        "candidate_graph_canonical_sha256": build_report["candidate_graph_canonical_sha256"],
        "controls": controls,
        "positive_negative_pairings": pairings,
        "passed": sum(controls.values()),
        "total": len(controls),
        "all_pass": all(controls.values()),
        "cap05": {
            "source_body_length": len(script_body),
            "source_body_sha256": sha256_text(script_body),
            "injected_body_length": len(script_input),
            "injected_body_sha256": sha256_text(script_input),
            "content_origin_mode": origin,
            "content_promise": promise,
            "binding": binding,
        },
        "cap06": {
            "source_body_length": len(content_body),
            "source_body_sha256": sha256_text(content_body),
            "injected_body_length": len(content_input),
            "injected_body_sha256": sha256_text(content_input),
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
