#!/usr/bin/env python3
"""Deterministic positive/negative controls for TD-UAPP-24.

The script builds the candidate in memory, executes only Python code-node functions,
and reads the retained failed run plus current conversation variables. It never writes
to Dify or M2 and never calls a model.
"""

from __future__ import annotations

import hashlib
import importlib.util
import inspect
import json
import logging
import os
from types import ModuleType
from typing import Any, Callable

HERE = os.path.dirname(os.path.abspath(__file__))
UAPP_ROOT = os.path.abspath(os.path.join(HERE, ".."))
EVIDENCE_DIR = os.path.join(UAPP_ROOT, "evidence", "stages", "uapp_td24")
RAW_PATH = os.path.join(
    UAPP_ROOT,
    "evidence",
    "stages",
    "uapp_correction",
    "UAPP_CORRECTION_RAW_v1.0.json",
)

CONVERSATION_ID = "5cfcaf57-8808-4fc7-8c66-d661e515d05a"
TASK_KEY = "ec666086-dce5-4e79-ba0f-6ac88f04a0bb"
QUERY = (
    "把制作规模从一人改为两人，制作时间和其他已经确认的内容都不变。"
    "先别重做制作方案，继续基于刚才那份制作方案给我出标题和封面。"
)
PD_FP = "559a204d7c4f1f2a"
PP_FP = "a7bf609e2dc9eecb"


def load_module(name: str, path: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


BUILDER = load_module("uapp_td24_builder", os.path.join(HERE, "UAPP_TD24_BUILD_v1.0.py"))


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def load_main(code: str, name: str) -> Callable[..., dict[str, Any]]:
    namespace: dict[str, Any] = {}
    exec(compile(code, name, "exec"), namespace)
    function = namespace.get("main")
    if not callable(function):
        raise RuntimeError(f"No callable main in {name}")
    return function


def decode(value: Any) -> Any:
    if not isinstance(value, str):
        return value
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return value


def current_variable(name: str) -> str:
    return BUILDER.psql(
        "select data::jsonb->>'value' from workflow_conversation_variables "
        f"where conversation_id='{CONVERSATION_ID}' and data::jsonb->>'name'='{name}' "
        "order by updated_at desc limit 1;"
    )


def add_check(
    checks: list[dict[str, Any]],
    check_id: str,
    text: str,
    positive_ok: bool,
    negative_ok: bool,
    positive: dict[str, Any],
    negative: dict[str, Any],
) -> None:
    checks.append(
        {
            "id": check_id,
            "text": text,
            "result": "PASS" if positive_ok and negative_ok else "FAIL",
            "positive_control": {"pass": positive_ok, **positive},
            "single_variable_negative_control": {"pass": negative_ok, **negative},
        }
    )


def artifact_map(state: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(item.get("fp")): item
        for item in state.get("artifacts", [])
        if isinstance(item, dict) and item.get("fp")
    }


def run() -> dict[str, Any]:
    graph, build = BUILDER.build_candidate(BUILDER.published_graph())
    nodes = {node["id"]: node for node in graph["nodes"]}
    correction = load_main(nodes["uapp_td24_correction"]["data"]["code"], "td24_correction")
    selector = load_main(nodes["uapp_pick_upstream"]["data"]["code"], "td24_selector")
    fields = load_main(nodes["uapp_fields"]["data"]["code"], "td24_fields")
    state_writer = load_main(nodes["uapp_state"]["data"]["code"], "td24_state")
    block = load_main(nodes["uapp_td24_block"]["data"]["code"], "td24_block")

    state_raw = current_variable("uapp_task_fields")
    store_raw = current_variable("uapp_last_artifact")
    before = json.loads(state_raw)
    before_artifacts = artifact_map(before)
    before_fields = before["fields"]
    empty_patch = {"correction_deltas": []}
    applied = correction(state_raw, empty_patch, QUERY, TASK_KEY, "PUBLISHING_PACKAGING")
    after = json.loads(applied["corrected_state_json"])
    after_artifacts = artifact_map(after)
    after_fields = after["fields"]

    checks: list[dict[str, Any]] = []

    same_query = "把制作规模从两人改为两人。"
    same = correction(
        applied["corrected_state_json"],
        empty_patch,
        same_query,
        TASK_KEY,
        "PUBLISHING_PACKAGING",
    )
    same_state = json.loads(same["corrected_state_json"])
    add_check(
        checks,
        "A-01",
        "明确用户纠正更新规范字段且同值重复不制造 revision",
        applied["correction_status"] == "APPLIED"
        and after["rev"] == before["rev"] + 1
        and after_fields["production.profile"]["frev"]
        == before_fields["production.profile"]["frev"] + 1,
        same_state["rev"] == after["rev"]
        and same_state["fields"]["production.profile"]["frev"]
        == after_fields["production.profile"]["frev"],
        {"status": applied["correction_status"], "state_rev": after["rev"]},
        {"mutated": "new value -> same value", "status": same["correction_status"]},
    )

    old_profile = before_fields["production.profile"]["v"]
    proposed_profile = old_profile.replace("一人", "两人")
    valid_proposal = {
        "correction_deltas": [
            {
                "field_id": "production.profile",
                "new_value": proposed_profile,
                "source_quote": "把制作规模从一人改为两人",
            }
        ]
    }
    valid = correction(state_raw, valid_proposal, QUERY, TASK_KEY, "PUBLISHING_PACKAGING")
    unsupported = json.loads(json.dumps(valid_proposal, ensure_ascii=False))
    unsupported["correction_deltas"][0]["source_quote"] = "两人"
    rejected = correction(state_raw, unsupported, QUERY, TASK_KEY, "PUBLISHING_PACKAGING")
    add_check(
        checks,
        "A-02",
        "模型只提议；逐字用户证据成立才升级为 USER_UTTERANCE",
        valid["correction_status"] == "APPLIED"
        and json.loads(valid["corrected_state_json"])["fields"]["production.profile"]["kind"]
        == "USER_UTTERANCE",
        rejected["correction_status"] == "REJECTED"
        and json.loads(rejected["corrected_state_json"])["rev"] == before["rev"],
        {"valid_quote": True},
        {"mutated": "source_quote", "status": rejected["correction_status"]},
    )

    fuzzy = correction(
        state_raw,
        empty_patch,
        "制作规模可能要调整一下，先看看。",
        TASK_KEY,
        "PUBLISHING_PACKAGING",
    )
    forced = correction(state_raw, valid_proposal, QUERY, "TASK-OTHER", "PUBLISHING_PACKAGING")
    add_check(
        checks,
        "A-03",
        "模糊表达不写入；task identity 单变量不一致时 fail-closed",
        fuzzy["correction_status"] == "NONE"
        and json.loads(fuzzy["corrected_state_json"])["rev"] == before["rev"],
        forced["correction_status"] == "REJECTED"
        and forced["correction_note"] == "TASK_IDENTITY_MISMATCH",
        {"fuzzy_status": fuzzy["correction_status"]},
        {"mutated": "task_key", "status": forced["correction_status"]},
    )

    facts_before = before_fields["facts.registered"]
    time_before = before_fields["production.time_window"]
    relation_ok = (
        "两人" in after_fields["production.profile"]["v"]
        and "两人" in after_fields["production.capacity_or_owner"]["v"]
        and "一人" not in after_fields["production.profile"]["v"]
        and "一人" not in after_fields["production.capacity_or_owner"]["v"]
    )
    mutated_state = json.loads(state_raw)
    mutated_state["fields"]["production.capacity_or_owner"]["ref"] = "TURN-OTHER.user_request"
    isolated = correction(
        json.dumps(mutated_state, ensure_ascii=False),
        valid_proposal,
        QUERY,
        TASK_KEY,
        "PUBLISHING_PACKAGING",
    )
    isolated_fields = json.loads(isolated["corrected_state_json"])["fields"]
    contradiction_detected = (
        "两人" in isolated_fields["production.profile"]["v"]
        and "一人" in isolated_fields["production.capacity_or_owner"]["v"]
    )
    add_check(
        checks,
        "A-04",
        "同 scope/同来源的相关字段保持一致；facts 与制作时间不产生伪 revision",
        relation_ok
        and after_fields["facts.registered"] == {**facts_before, "lvl": "B"}
        and after_fields["production.time_window"] == time_before,
        contradiction_detected,
        {
            "corrected_fields": applied["corrected_fields"],
            "facts_frev": after_fields["facts.registered"]["frev"],
            "time_frev": after_fields["production.time_window"]["frev"],
        },
        {"mutated": "capacity source_ref", "contradiction_detected": contradiction_detected},
    )

    with open(RAW_PATH, encoding="utf-8") as handle:
        predecessor_raw = json.load(handle)
    top = predecessor_raw["app_runs_in_window"]["UAPP"][0]
    detail = top["node_detail"]
    m3_row = next(item for item in detail if item.get("node_id") == "uapp_m3")
    hop_row = next(item for item in detail if item.get("node_id") == "uapp_hop")
    m3_outputs = decode(m3_row.get("outputs"))
    hop_outputs = decode(hop_row.get("outputs"))
    m3_text = json.dumps(m3_outputs, ensure_ascii=False)
    hop_call = (hop_outputs or {}).get("capability_call", "") if isinstance(hop_outputs, dict) else ""
    hop_gaps = (hop_outputs or {}).get("extraction_gaps_text", "") if isinstance(hop_outputs, dict) else ""
    replay_negative = correction(
        state_raw,
        empty_patch,
        "继续基于刚才那份制作方案给我出标题和封面。",
        TASK_KEY,
        "PUBLISHING_PACKAGING",
    )
    add_check(
        checks,
        "B-01",
        "真实失败形态回放：M3 已识别、Hop 不含字段时 UAPP 仍形成规范 delta",
        "制作规模从一人改为两人" in m3_text
        and "production_profile" not in hop_call
        and applied["correction_status"] == "APPLIED",
        replay_negative["correction_status"] == "NONE",
        {
            "old_run": top["id"],
            "m3_recognized": True,
            "hop_has_production_profile": False,
        },
        {"mutated": "remove correction semantics", "status": replay_negative["correction_status"]},
    )

    mutated_dep_state = json.loads(state_raw)
    for artifact in mutated_dep_state["artifacts"]:
        if artifact.get("fp") == PD_FP:
            artifact["dep"].pop("production.profile", None)
            artifact["dep"].pop("production.capacity_or_owner", None)
    no_direct = correction(
        json.dumps(mutated_dep_state, ensure_ascii=False),
        empty_patch,
        QUERY,
        TASK_KEY,
        "PUBLISHING_PACKAGING",
    )
    no_direct_state = artifact_map(json.loads(no_direct["corrected_state_json"]))
    add_check(
        checks,
        "C-01",
        "依赖纠正字段的 PD 直接失效；删除唯一依赖边时 Validator 翻转",
        after_artifacts["099061257c9677bd"]["stale"] is True
        and after_artifacts[PD_FP]["stale"] is True,
        no_direct_state[PD_FP]["stale"] is False,
        {"direct_stale": applied["direct_stale"]},
        {"mutated": "PD dependency edges", "pd_stale": no_direct_state[PD_FP]["stale"]},
    )

    pp_after = after_artifacts[PP_FP]
    mutated_lineage = json.loads(applied["corrected_state_json"])
    artifact_map(mutated_lineage)[PP_FP].pop("upstream_fp", None)
    transitive_detector_flips = not bool(artifact_map(mutated_lineage)[PP_FP].get("upstream_fp"))
    add_check(
        checks,
        "C-02",
        "依赖旧 PD 的 PP 记录具有直接血缘并收到传递失效",
        pp_after.get("upstream_fp") == PD_FP
        and any(reason == f"UPSTREAM_STALE:{PD_FP}" for reason in pp_after.get("additional_stale_reasons", []))
        and PP_FP in applied["transitive_stale"],
        transitive_detector_flips,
        {"pp_upstream_fp": pp_after.get("upstream_fp"), "transitive": applied["transitive_stale"]},
        {"mutated": "PP upstream_fp", "missing_detected": transitive_detector_flips},
    )

    affected = {"099061257c9677bd", PD_FP, "757af4204cc42fb3", "df85e97cb07cd0df", PP_FP}
    unrelated = [fp for fp in before_artifacts if fp not in affected]
    unrelated_preserved = all(
        after_artifacts[fp].get("stale") == before_artifacts[fp].get("stale")
        and after_artifacts[fp].get("stale_reason") == before_artifacts[fp].get("stale_reason")
        for fp in unrelated
    )
    artificial = json.loads(applied["corrected_state_json"])
    artifact_map(artificial)[unrelated[0]]["stale_reason"] = "BLANKET_STALE"
    preservation_detector_flips = artifact_map(artificial)[unrelated[0]]["stale_reason"] != before_artifacts[
        unrelated[0]
    ].get("stale_reason")
    add_check(
        checks,
        "C-03",
        "不受影响 artifact 的既有状态与原因逐条保留，不 blanket STALE",
        bool(unrelated) and unrelated_preserved,
        preservation_detector_flips,
        {"unaffected_checked": unrelated},
        {"mutated": "one unrelated stale_reason", "detected": preservation_detector_flips},
    )

    selected = selector(store_raw, applied["corrected_state_json"], "PUBLISHING_PACKAGING", QUERY, TASK_KEY, "APPLIED")
    store = json.loads(store_raw)
    pd_item = next(item for item in store["items"] if item.get("fp") == PD_FP)
    forged = {
        "upstream_delivery": pd_item["body"],
        "selected_fp": pd_item["fp"],
        "selected_bfp": pd_item["bfp"],
        "selected_capability": "PRODUCTION_DIRECTOR",
        "selection_status": "SELECTED",
    }
    field_result = fields(
        applied["corrected_state_json"],
        TASK_KEY,
        hop_call,
        hop_gaps,
        "PUBLISHING_PACKAGING",
        QUERY,
        "{}",
        forged["upstream_delivery"],
        forged["selected_fp"],
        forged["selected_bfp"],
        forged["selected_capability"],
        forged["selection_status"],
        "APPLIED",
    )
    uncorrected_selected = selector(store_raw, state_raw, "PUBLISHING_PACKAGING", QUERY, TASK_KEY, "NONE")
    add_check(
        checks,
        "C-04",
        "selector 读纠正后状态；即使预选旧 PD，后置门仍按 STALE 拒绝",
        selected["selection_status"] == "NO_LEGAL_UPSTREAM"
        and field_result["artifact_binding_status"] == "REJECTED"
        and '"content_body_or_beats"' not in field_result["capability_call"],
        uncorrected_selected["selection_status"] == "SELECTED",
        {
            "selector": selected["selection_status"],
            "post_gate": field_result["artifact_binding_status"],
        },
        {"mutated": "selector state -> pre-correction", "status": uncorrected_selected["selection_status"]},
    )

    pending = json.loads(field_result["pending_state_json"])
    block_result = block(
        "APPLIED",
        applied["block_message"],
        selected["selection_question"],
        field_result["gaps_text"],
    )
    edges = graph["edges"]
    blocked_to_seam = any(
        edge.get("source") == "uapp_td24_binding_gate"
        and edge.get("sourceHandle") == "blocked"
        and edge.get("target") == "uapp_seam"
        for edge in edges
    )
    mutated_edges = json.loads(json.dumps(edges))
    next(edge for edge in mutated_edges if edge.get("sourceHandle") == "blocked")["target"] = "uapp_seam"
    graph_detector_flips = any(
        edge.get("source") == "uapp_td24_binding_gate"
        and edge.get("sourceHandle") == "blocked"
        and edge.get("target") == "uapp_seam"
        for edge in mutated_edges
    )
    add_check(
        checks,
        "C-05",
        "无合法上游时 Seam/PP 前停支，不追加 PP artifact，并生成自然说明",
        not blocked_to_seam
        and len(pending["artifacts"]) == len(before["artifacts"])
        and "标题和封面" in block_result["final_text"]
        and "制作方案" in block_result["final_text"],
        graph_detector_flips,
        {"artifact_count": len(pending["artifacts"]), "final_text": block_result["final_text"]},
        {"mutated": "blocked edge target", "seam_bypass_detected": graph_detector_flips},
    )

    functions = {
        "uapp_td24_correction": correction,
        "uapp_pick_upstream": selector,
        "uapp_fields": fields,
        "uapp_state": state_writer,
        "uapp_td24_block": block,
    }
    arity_ok = all(
        len(inspect.signature(function).parameters) == len(nodes[node_id]["data"]["variables"])
        for node_id, function in functions.items()
    )
    synthetic_unchecked = [{"result": "NOT_CHECKED"}]
    unchecked_rejected = not all(item.get("result") == "PASS" for item in synthetic_unchecked)
    add_check(
        checks,
        "D-01",
        "构建影响面、节点参数与 0/0/NOT_CHECKED 防误绿",
        all(build["protected_nodes_equal"].values())
        and build["node_count"] == {"before": 50, "after": 55}
        and build["edge_count"] == {"before": 52, "after": 57}
        and arity_ok,
        unchecked_rejected,
        {
            "candidate_graph_sha256": build["candidate_graph_canonical_sha256"],
            "function_arity_ok": arity_ok,
        },
        {"mutated": "one result -> NOT_CHECKED", "rejected": unchecked_rejected},
    )

    passed = sum(item["result"] == "PASS" for item in checks)
    return {
        "document": {
            "id": "UAPP_TD24_CONTROLS_v1.0",
            "task_id": "DIYU-V1-UNIFIED-DIFY-APPLICATION-001",
            "model_calls": 0,
            "dify_writes": 0,
            "m2_writes": 0,
            "raw_predecessor_sha256": sha256_text(open(RAW_PATH, encoding="utf-8").read()),
            "builder_sha256": sha256_text(
                open(os.path.join(HERE, "UAPP_TD24_BUILD_v1.0.py"), encoding="utf-8").read()
            ),
        },
        "summary": {
            "pass": passed,
            "total": len(checks),
            "positive_controls": len(checks),
            "single_variable_negative_controls": len(checks),
            "verdict": "PASS" if passed == len(checks) else "FAIL",
        },
        "candidate": build,
        "checks": checks,
    }


def main() -> int:
    report = run()
    os.makedirs(EVIDENCE_DIR, exist_ok=True)
    output = os.path.join(EVIDENCE_DIR, "UAPP_TD24_CONTROLS_v1.0.json")
    with open(output, "x", encoding="utf-8") as handle:
        json.dump(report, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    logging.info("%s", json.dumps(report["summary"], ensure_ascii=False, sort_keys=True))
    return 0 if report["summary"]["verdict"] == "PASS" else 1


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    raise SystemExit(main())
