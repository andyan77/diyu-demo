#!/usr/bin/env python3
"""Zero-model positive and single-variable negative controls for CAP-06."""

from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
import logging
import re
from pathlib import Path
from types import ModuleType
from typing import Any, Callable

LOGGER = logging.getLogger(__name__)
HERE = Path(__file__).resolve().parent
UAPP_ROOT = HERE.parent
SCENARIOS = UAPP_ROOT / "stages" / "UAPP_S5_FROZEN_SCENARIOS_v1.1.json"
RAW = (
    UAPP_ROOT / "evidence" / "stages" / "uapp_s5_inline_artifact_successor_v1_0"
    / "formal" / "raw" / "UAPP-CAP-06.json"
)
OUTPUT = (
    UAPP_ROOT / "evidence" / "stages" / "cap06_semantic_contract_v1_0"
    / "CAP06_DETERMINISTIC_CONTROLS_v1.0.json"
)


def load_module(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


BUILD = load_module("cap06_build_controls", HERE / "CAP06_SEMANTIC_CONTRACT_BUILD_v1.0.py")
HELPERS = load_module(
    "cap06_inline_helpers", HERE / "UAPP_S5_INLINE_ARTIFACT_SUCCESSOR_CONTROLS_v1.0.py"
)


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def parsed(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    if not isinstance(value, str):
        return {}
    result = json.loads(value)
    return result if isinstance(result, dict) else {}


def node_output(raw: dict[str, Any], node_id: str) -> dict[str, Any]:
    runs = raw["app_runs_in_window"]["UAPP"]
    executions = runs[-1]["node_detail"]
    matches = [row for row in executions if row.get("node_id") == node_id]
    if len(matches) != 1:
        raise RuntimeError(f"Expected one {node_id}, got {len(matches)}")
    return parsed(matches[0].get("outputs"))


def mutate_selected(
    selected: dict[str, Any], mutation: Callable[[dict[str, Any]], None]
) -> dict[str, Any]:
    changed = copy.deepcopy(selected)
    record = parsed(changed["selected_companion_json"])
    mutation(record)
    changed["selected_companion_json"] = json.dumps(
        record, ensure_ascii=False, sort_keys=True
    )
    return changed


def field_value(capability_call: str, key: str) -> str:
    match = re.search(
        rf"^(?:`{re.escape(key)}`|{re.escape(key)})\s*:\s*(.+)$",
        capability_call,
        re.MULTILINE,
    )
    return match.group(1).strip() if match else ""


def envelope(
    function: Callable[..., dict[str, Any]], body: str
) -> dict[str, Any]:
    return function(body, "", "ENTRY-07", "DERIVE_MODE_AND_PACKAGE", "NO")


def build_report() -> dict[str, Any]:
    uapp_graph, uapp_touched = BUILD.patch_uapp(BUILD.published_graph(BUILD.UAPP_APP_ID))
    pp_graph, pp_touched = BUILD.patch_pp(BUILD.published_graph(BUILD.PP_APP_ID))
    uapp_nodes = {node["id"]: node for node in uapp_graph["nodes"]}
    pp_nodes = {node["id"]: node for node in pp_graph["nodes"]}
    inline = HELPERS.BASE_CONTROLS.node_main(
        uapp_nodes["uapp_inline_artifact"]["data"]["code"], "cap06-inline"
    )
    selector = HELPERS.BASE_CONTROLS.node_main(
        uapp_nodes["uapp_pick_upstream"]["data"]["code"], "cap06-selector"
    )
    fields = HELPERS.BASE_CONTROLS.node_main(
        uapp_nodes["uapp_fields"]["data"]["code"], "cap06-fields"
    )
    pp_check = HELPERS.BASE_CONTROLS.node_main(
        pp_nodes["envelope_check"]["data"]["code"], "cap06-pp-envelope"
    )

    scenarios = json.loads(SCENARIOS.read_text(encoding="utf-8"))
    turn = next(row for row in scenarios["turns"] if row["key"] == "UAPP-CAP-06")
    query = str(turn["query"])
    historical_raw = json.loads(RAW.read_text(encoding="utf-8"))
    hop = node_output(historical_raw, "uapp_hop")
    task_key = "cap06-control-task"
    inline_result = inline(query, "PUBLISHING_PACKAGING", task_key, "NONE")
    selected = HELPERS.selector_call(
        selector, inline_result, query, "PUBLISHING_PACKAGING", task_key=task_key
    )
    fields_result = HELPERS.fields_call(
        fields,
        selected,
        query,
        "PUBLISHING_PACKAGING",
        str(hop["capability_call"]),
        str(hop["extraction_gaps_text"]),
        task_key=task_key,
    )
    call = str(fields_result["capability_call"])
    body = str(inline_result["inline_body"])
    injected = HELPERS.json_body(call, "content_body_or_beats")
    promise = field_value(call, "content_promise")
    platform = field_value(call, "platform")
    cta_contract = field_value(call, "cta_contract")
    cta_level = field_value(call, "cta_level")
    state = parsed(fields_result["pending_state_json"])

    wrong_request = mutate_selected(
        selected, lambda record: record.__setitem__("request_bfp", "0" * 16)
    )
    wrong_platform = mutate_selected(
        selected, lambda record: record["values"].__setitem__("delivery.platform", "抖音")
    )
    wrong_cta_rule = mutate_selected(
        selected,
        lambda record: record["derived_values"]["cta.level"].__setitem__(
            "derivation_rule", "UNAUTHORIZED_RULE"
        ),
    )
    body_drift = dict(selected)
    body_drift["upstream_delivery"] = str(selected["upstream_delivery"]) + "改"

    base = (
        '"content_body_or_beats": "已完成成片正文"\n'
        '`content_promise`: 展示三套通勤穿法\n'
        '`explicit_non_promise`: 不承诺显瘦，不写价格折扣和站外购买\n'
        '`facts_registered`: 已完成真实试穿，库存充足\n'
        '`asset_publish_permission`: 本次发小红书\n'
        'platform: 小红书\n'
    )
    low_risk = envelope(pp_check, base + '`cta_contract`: 自然 CTA\ncta_level: LOW_RISK_INTERACTION')
    no_cta = envelope(pp_check, base + 'cta_level: NO_CTA')
    omitted = envelope(pp_check, base)
    handoff_missing = envelope(pp_check, base + 'cta_level: BUSINESS_HANDOFF')
    high_risk = envelope(pp_check, base + 'cta_level: HIGH_RISK')
    missing_body = envelope(
        pp_check, base.replace('"content_body_or_beats": "已完成成片正文"\n', "")
    )
    wrong_low_risk = envelope(
        pp_check, base + 'cta_level: KNOWN_BUT_NOT_AUTHORIZED'
    )
    handoff_complete = envelope(
        pp_check,
        base
        + 'cta_level: BUSINESS_HANDOFF\ncta_target: 已确认目标\n'
        + 'cta_reception_path: 平台内已确认路径\ncta_authorized_facts: 已确认事实',
    )

    wrong_request_result = HELPERS.fields_call(
        fields, wrong_request, query, "PUBLISHING_PACKAGING",
        str(hop["capability_call"]), str(hop["extraction_gaps_text"]), task_key=task_key,
    )
    wrong_platform_result = HELPERS.fields_call(
        fields, wrong_platform, query, "PUBLISHING_PACKAGING",
        str(hop["capability_call"]), str(hop["extraction_gaps_text"]), task_key=task_key,
    )
    wrong_cta_result = HELPERS.fields_call(
        fields, wrong_cta_rule, query, "PUBLISHING_PACKAGING",
        str(hop["capability_call"]), str(hop["extraction_gaps_text"]), task_key=task_key,
    )
    body_drift_result = HELPERS.fields_call(
        fields, body_drift, query, "PUBLISHING_PACKAGING",
        str(hop["capability_call"]), str(hop["extraction_gaps_text"]), task_key=task_key,
    )

    checks = {
        "P01_original_cap06_inline_ready": inline_result["inline_status"] == "INLINE_READY",
        "P02_body_byte_identity": injected == body and bool(body),
        "P03_body_sha_identity": sha256_text(injected) == sha256_text(body),
        "P04_platform_xiaohongshu": platform == "小红书",
        "P05_platform_user_source": state["fields"]["delivery.platform"]["lvl"] == "A",
        "P06_low_risk_cta_bound": cta_level == "LOW_RISK_INTERACTION",
        "P07_cta_contract_source_text": cta_contract.replace(" ", "") == "自然CTA",
        "P08_promise_is_realized_payoff": bool(promise) and promise in body and promise != body,
        "P09_no_commercial_cta_injection": not any(
            token in cta_contract for token in ("咨询", "私信", "到店", "购买", "站外")
        ),
        "P10_inline_not_persisted": state.get("artifacts") == [],
        "P11_pp_low_risk_runs": low_risk["can_run"] == "true"
        and low_risk["cta_level"] == "LOW_RISK_INTERACTION",
        "P12_pp_explicit_no_cta_runs": no_cta["can_run"] == "true"
        and no_cta["cta_level"] == "NO_CTA",
        "P13_pp_omitted_cta_defaults_without_block": omitted["can_run"] == "true"
        and omitted["cta_level"] == "NO_CTA",
        "P14_pp_business_gap_local_only": handoff_missing["can_run"] == "true"
        and handoff_missing["cta_level"] == "NO_CTA"
        and handoff_missing["cta_policy_status"] == "HELD_MISSING_HANDOFF_CONTRACT",
        "P15_pp_high_risk_refused_package_runs": high_risk["can_run"] == "true"
        and high_risk["cta_level"] == "NO_CTA"
        and high_risk["cta_policy_status"] == "REJECTED_HIGH_RISK",
        "N01_request_digest_mismatch_rejected": wrong_request_result["artifact_binding_status"]
        == "REJECTED",
        "N02_platform_not_in_source_rejected": wrong_platform_result["artifact_binding_status"]
        == "REJECTED",
        "N03_unauthorized_cta_derivation_not_bound": field_value(
            str(wrong_cta_result["capability_call"]), "cta_level"
        ) != "LOW_RISK_INTERACTION",
        "N04_body_hash_drift_rejected": body_drift_result["artifact_binding_status"] == "REJECTED",
        "N05_missing_body_blocks": missing_body["can_run"] == "false"
        and "content_body_or_beats" in missing_body["missing"],
        "N06_not_authorized_not_low_risk": wrong_low_risk["cta_level"] == "NO_CTA"
        and wrong_low_risk["cta_policy_status"] == "HELD_NOT_AUTHORIZED",
        "N07_business_handoff_requires_contract": handoff_complete["cta_level"]
        == "BUSINESS_HANDOFF" and handoff_complete["cta_policy_status"] == "AUTHORIZED",
        "N08_only_expected_nodes_changed": uapp_touched == ["uapp_fields", "uapp_inline_artifact"]
        and pp_touched == ["envelope_check"],
    }
    pairings = {
        "P02_body_byte_identity": "N04_body_hash_drift_rejected",
        "P04_platform_xiaohongshu": "N02_platform_not_in_source_rejected",
        "P06_low_risk_cta_bound": "N03_unauthorized_cta_derivation_not_bound",
        "P11_pp_low_risk_runs": "N06_not_authorized_not_low_risk",
        "P13_pp_omitted_cta_defaults_without_block": "N05_missing_body_blocks",
        "P14_pp_business_gap_local_only": "N07_business_handoff_requires_contract",
    }
    return {
        "document": {
            "id": "CAP06_DETERMINISTIC_CONTROLS_v1.0",
            "task_id": "DIYU-V1-UNIFIED-DIFY-APPLICATION-001",
            "model_calls": 0,
            "dify_writes": 0,
        },
        "checks": checks,
        "positive_negative_pairings": pairings,
        "passed": sum(checks.values()),
        "total": len(checks),
        "all_pass": all(checks.values()),
        "binding": {
            "body_length": len(body),
            "body_sha256": sha256_text(body),
            "injected_sha256": sha256_text(injected),
            "content_promise": promise,
            "platform": platform,
            "cta_contract": cta_contract,
            "cta_level": cta_level,
        },
        "pp_cases": {
            "low_risk": low_risk,
            "no_cta": no_cta,
            "omitted": omitted,
            "business_missing": handoff_missing,
            "high_risk": high_risk,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    report = build_report()
    if args.write:
        if OUTPUT.exists():
            raise FileExistsError(OUTPUT)
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    LOGGER.info("%s/%s", report["passed"], report["total"])
    return 0 if report["all_pass"] else 1


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    raise SystemExit(main())
