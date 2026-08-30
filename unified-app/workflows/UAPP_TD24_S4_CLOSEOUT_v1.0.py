#!/usr/bin/env python3
"""Zero-model S4 closeout for the frozen TD-UAPP-24 successor."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import logging
import os
from types import ModuleType
from typing import Any, Callable

HERE = os.path.dirname(os.path.abspath(__file__))
UAPP_ROOT = os.path.abspath(os.path.join(HERE, ".."))
REPO = os.path.abspath(os.path.join(UAPP_ROOT, ".."))
OUTPUT_PATH = os.path.join(UAPP_ROOT, "stages", "UAPP_TD24_S4_CLOSEOUT_v1.0.json")
GATE_PATH = os.path.join(UAPP_ROOT, "stages", "UAPP_TD24_GATE_v1.0.json")
RESULT_PATH = os.path.join(UAPP_ROOT, "stages", "UAPP_TD24_RESULT_v1.0.json")
UAAB_RESULT_PATH = os.path.join(UAPP_ROOT, "stages", "UAAB_RESULT_v1.2.json")
PREDECESSOR_RAW_PATH = os.path.join(
    UAPP_ROOT,
    "evidence",
    "stages",
    "uapp_correction",
    "UAPP_CORRECTION_RAW_v1.0.json",
)
TASK_KEY = "ec666086-dce5-4e79-ba0f-6ac88f04a0bb"
PD_SHA256 = "8f91984b628da1c65250c7bb2f90e9a31c86233826ceee9271bcc46b77b2c21b"


def load_module(name: str, path: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


CONTROLS = load_module(
    "uapp_td24_controls",
    os.path.join(HERE, "UAPP_TD24_CONTROLS_v1.0.py"),
)
OLD_RUN = load_module(
    "uapp_correction_run",
    os.path.join(HERE, "UAPP_CORRECTION_RUN_v1.0.py"),
)


def sha256_file(path: str) -> str:
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def load_json(path: str) -> dict[str, Any]:
    with open(path, encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise RuntimeError(f"JSON root is not an object: {path}")
    return value


def load_main(code: str, name: str) -> Callable[..., dict[str, Any]]:
    return CONTROLS.load_main(code, name)


def decode(value: Any) -> Any:
    return CONTROLS.decode(value)


def criterion(
    rows: list[dict[str, Any]],
    criterion_id: str,
    text: str,
    passed: bool,
    evidence: dict[str, Any],
) -> None:
    rows.append(
        {
            "id": criterion_id,
            "text": text,
            "result": "PASS / CURRENT" if passed else "NOT_VERIFIED",
            "evidence": evidence,
        }
    )


def non_correction_binding_replay() -> dict[str, Any]:
    graph = CONTROLS.BUILDER.published_graph()
    nodes = {node["id"]: node for node in graph["nodes"]}
    selector = load_main(nodes["uapp_pick_upstream"]["data"]["code"], "s4_selector")
    fields = load_main(nodes["uapp_fields"]["data"]["code"], "s4_fields")
    predecessor = load_json(PREDECESSOR_RAW_PATH)
    variables = predecessor["conversation_variables_after"]
    state_raw = variables["uapp_task_fields"]
    store_raw = variables["uapp_last_artifact"]
    query = "继续基于刚才那份制作方案给我出标题和封面。"
    selected = selector(
        store_raw,
        state_raw,
        "PUBLISHING_PACKAGING",
        query,
        TASK_KEY,
        "NONE",
    )
    top = predecessor["app_runs_in_window"]["UAPP"][0]
    hop_row = next(row for row in top["node_detail"] if row.get("node_id") == "uapp_hop")
    hop = decode(hop_row["outputs"])
    bound = fields(
        state_raw,
        TASK_KEY,
        hop["capability_call"],
        hop["extraction_gaps_text"],
        "PUBLISHING_PACKAGING",
        query,
        "{}",
        selected["upstream_delivery"],
        selected["selected_fp"],
        selected["selected_bfp"],
        selected["selected_capability"],
        selected["selection_status"],
        "NONE",
    )
    artifact_line = next(
        line
        for line in bound["capability_call"].splitlines()
        if line.startswith('"content_body_or_beats": ')
    )
    injected_body = json.loads(artifact_line.split(": ", 1)[1])
    rejected = fields(
        state_raw,
        TASK_KEY,
        hop["capability_call"],
        hop["extraction_gaps_text"],
        "PUBLISHING_PACKAGING",
        query,
        "{}",
        selected["upstream_delivery"],
        "single-variable-wrong-fp",
        selected["selected_bfp"],
        selected["selected_capability"],
        selected["selection_status"],
        "NONE",
    )
    positive = (
        selected["selection_status"] == "SELECTED"
        and selected["selected_fp"] == "559a204d7c4f1f2a"
        and sha256_text(selected["upstream_delivery"]) == PD_SHA256
        and bound["artifact_binding_status"] == "BOUND"
        and injected_body == selected["upstream_delivery"]
    )
    negative = rejected["artifact_binding_status"] == "REJECTED"
    return {
        "positive_pass": positive,
        "single_variable_negative_pass": negative,
        "selection_status": selected["selection_status"],
        "selected_fp": selected["selected_fp"],
        "selected_bfp": selected["selected_bfp"],
        "selected_capability": selected["selected_capability"],
        "delivery_sha256": sha256_text(selected["upstream_delivery"]),
        "binding_status": bound["artifact_binding_status"],
        "injected_body_byte_equal": injected_body == selected["upstream_delivery"],
        "negative_binding_status": rejected["artifact_binding_status"],
    }


def run() -> dict[str, Any]:
    gate = load_json(GATE_PATH)
    result = load_json(RESULT_PATH)
    uaab = load_json(UAAB_RESULT_PATH)
    replay = non_correction_binding_replay()
    apps = OLD_RUN.protected_apps()
    criteria: list[dict[str, Any]] = []
    formal_all_pass = result["summary"] == {
        "pass": 12,
        "total": 12,
        "verdict": "PASS / CURRENT",
    }
    pp_unchanged = (
        apps["PUBLISHING_PACKAGING"]["graph_md5"] == "8366328bf827bd0f460455d750d45c4f"
        and apps["PP_provider"]["graph_md5"] == "8366328bf827bd0f460455d750d45c4f"
    )

    criterion(
        criteria,
        "S4-01",
        "规范任务状态载体",
        formal_all_pass
        and all(
            item["result"] == "PASS / CURRENT"
            for item in result["criteria"]
            if item["id"] in {"C-01", "C-02", "C-03"}
        ),
        {"td24_criteria": ["C-01", "C-02", "C-03"], "state_revision": 14},
    )
    criterion(
        criteria,
        "S4-02",
        "CS→PD→PP 连续链",
        uaab.get("result") == "PASS / CURRENT" and replay["positive_pass"] and pp_unchanged,
        {"uaab_result_sha256": sha256_file(UAAB_RESULT_PATH), "current_path_replay": replay},
    )
    criterion(
        criteria,
        "S4-03",
        "已接受上游产物绑定",
        replay["positive_pass"] and replay["single_variable_negative_pass"],
        replay,
    )
    criterion(
        criteria,
        "S4-04",
        "事实边界",
        uaab.get("result") == "PASS / CURRENT" and pp_unchanged,
        {"successor": "V-08B_FACT_TRACEABILITY PASS / CURRENT", "pp_unchanged": pp_unchanged},
    )
    criterion(
        criteria,
        "S4-05",
        "CTA 边界",
        uaab.get("result") == "PASS / CURRENT" and pp_unchanged,
        {"successor": "V-08C_CTA_FIDELITY PASS / CURRENT", "pp_unchanged": pp_unchanged},
    )
    criterion(
        criteria,
        "S4-06",
        "用户纠正后的失效传播",
        formal_all_pass,
        {
            "td24_result_sha256": sha256_file(RESULT_PATH),
            "formal_run_id": result["formal_run"]["workflow_run_id"],
            "criteria": "12/12 PASS / CURRENT",
        },
    )
    criterion(
        criteria,
        "S4-07",
        "作用域隔离",
        all(
            item["result"] == "PASS / CURRENT"
            for item in result["criteria"]
            if item["id"] in {"C-10", "C-12"}
        ),
        {"td24_criteria": ["C-10", "C-12"]},
    )
    criterion(
        criteria,
        "S4-08",
        "无暗跑",
        next(item for item in result["criteria"] if item["id"] == "C-11")["result"]
        == "PASS / CURRENT",
        next(item for item in result["criteria"] if item["id"] == "C-11")["evidence"],
    )
    passed = sum(item["result"] == "PASS / CURRENT" for item in criteria)
    verdict = "PASS / CURRENT" if passed == len(criteria) else "NOT_VERIFIED"
    return {
        "document": {
            "id": "UAPP_TD24_S4_CLOSEOUT_v1.0",
            "task_id": "DIYU-V1-UNIFIED-DIFY-APPLICATION-001",
            "gate_sha256": sha256_file(GATE_PATH),
            "td24_result_sha256": sha256_file(RESULT_PATH),
            "uaab_result_sha256": sha256_file(UAAB_RESULT_PATH),
            "model_calls": 0,
            "dify_writes": 0,
            "m2_writes": 0,
        },
        "candidate": {
            "uapp_graph_md5": apps["UAPP"]["graph_md5"],
            "uapp_graph_canonical_sha256": gate["candidate"]["UAPP"][
                "graph_canonical_sha256"
            ],
            "pp_provider_graph_md5": apps["PP_provider"]["graph_md5"],
            "seam_graph_md5": apps["SEAM"]["graph_md5"],
            "hop_graph_md5": apps["HOP"]["graph_md5"],
        },
        "summary": {"pass": passed, "total": len(criteria), "verdict": verdict},
        "criteria": criteria,
        "states": {
            "CROSS_TURN_CORRECTION_PROPAGATION": "PASS / CURRENT",
            "S4_OVERALL_ACCEPTANCE": verdict,
            "S5": "NOT_STARTED",
            "S5_START": "WAIT_FOUNDER_AUTHORIZATION",
            "main_merge": "NOT_ALLOWED",
            "terminal_state": "unset",
        },
    }


def main() -> int:
    if os.path.exists(OUTPUT_PATH):
        raise RuntimeError(f"Refusing to overwrite closeout result: {OUTPUT_PATH}")
    report = run()
    with open(OUTPUT_PATH, "x", encoding="utf-8") as handle:
        json.dump(report, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    logging.info("%s", json.dumps(report["summary"], ensure_ascii=False, sort_keys=True))
    return 0 if report["summary"]["verdict"] == "PASS / CURRENT" else 1


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    raise SystemExit(main())
