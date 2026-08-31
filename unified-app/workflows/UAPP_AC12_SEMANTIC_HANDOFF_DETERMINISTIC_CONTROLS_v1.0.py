#!/usr/bin/env python3
"""Zero-model controls for the AC-12 semantic-handoff successor."""

from __future__ import annotations

import json
import importlib.util
import subprocess
from pathlib import Path
from types import ModuleType
from typing import Any

ROOT = Path(__file__).resolve().parents[2]


def load_module(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


BUILD = load_module(
    "uapp_ac12_semantic_handoff_build",
    ROOT / "unified-app/workflows/UAPP_AC12_SEMANTIC_HANDOFF_BUILD_v1.0.py",
)

RUNS = {"yaml": "9da91e61-adf2-46a2-b6a0-2493bc492963",
        "g2": "03871811-eb66-45e6-a496-e6764e203463",
        "full": "0c603685-8a4e-4b50-bf97-92c71049cb79"}
FIELD_ARGS = ("prev_state_json", "task_key", "capability_call", "gaps_text", "target_capability",
              "user_request", "snapshot_json", "selector_delivery", "selector_fp", "selector_bfp",
              "selector_capability", "selector_status", "correction_status", "intent_reason",
              "selector_source_kind", "selector_source_turn", "selector_artifact_type",
              "selector_task_key", "selector_companion_json")
BT = chr(96)


def check(control_id: str, passed: bool, detail: Any) -> dict[str, Any]:
    return {"id": control_id, "result": "PASS" if passed else "FAIL", "detail": detail}


def sql_json(sql: str) -> Any:
    result = subprocess.run(
        ["docker", "exec", "-i", "docker-db_postgres-1", "psql", "-U", "postgres",
         "-d", "dify", "-tA", "-c", sql],
        check=True, text=True, capture_output=True)
    return json.loads(result.stdout)


def historical_fields_inputs() -> dict[str, dict[str, Any]]:
    ids = ",".join("'%s'" % value for value in RUNS.values())
    return sql_json(
        "select json_object_agg(workflow_run_id::text, inputs::jsonb)::text "
        "from workflow_node_executions where node_id='uapp_fields' "
        "and workflow_run_id::text in (%s);" % ids)


def field_main(source: str):
    namespace: dict[str, Any] = {}
    exec(compile(source, "<candidate-uapp-fields>", "exec"), namespace)  # noqa: S102
    return namespace["main"]


def run(fn, raw: dict[str, Any], **overrides: Any) -> dict[str, Any]:
    args = {key: raw.get(key, "") for key in FIELD_ARGS}
    args.update(overrides)
    return fn(**args)


def state(output: dict[str, Any]) -> dict[str, Any]:
    return json.loads(output["pending_state_json"])


def field(output: dict[str, Any], key: str) -> dict[str, Any] | None:
    return state(output).get("fields", {}).get(key)


def synthetic(user: str, call: str, gaps: str, snapshot: dict[str, Any],
              previous: dict[str, Any] | None = None, correction: str = "") -> dict[str, Any]:
    return {
        "prev_state_json": json.dumps(previous or {}, ensure_ascii=False), "task_key": "test-task",
        "capability_call": call, "gaps_text": gaps, "target_capability": "CONTENT_BRIEF",
        "user_request": user, "snapshot_json": json.dumps(snapshot, ensure_ascii=False),
        "selector_delivery": "", "selector_fp": "", "selector_bfp": "", "selector_capability": "",
        "selector_status": "", "correction_status": correction, "intent_reason": "",
        "selector_source_kind": "", "selector_source_turn": "", "selector_artifact_type": "",
        "selector_task_key": "", "selector_companion_json": ""}


def no_goal_snapshot() -> dict[str, Any]:
    return {"revision": 1, "goal_structure": {"primary_goal": None}, "evidence_bundle": []}


def main() -> int:
    graph = BUILD.published_graph()
    candidate, graph_report = BUILD.patch_graph(graph)
    source = next(node["data"]["code"] for node in candidate["nodes"] if node["id"] == "uapp_fields")
    fn = field_main(source)
    raw = historical_fields_inputs()
    controls: list[dict[str, Any]] = []

    yaml_out = run(fn, raw[RUNS["yaml"]])
    yaml_call = yaml_out["capability_call"]
    yaml_value = "缺的不是衣服数量，是一件能压住整套的外套，并且会用它三天不重样"
    controls.append(check(
        "P01_yaml_label_projects_exact_viewer_outcome",
        BT+"content_promise"+BT+": "+yaml_value in yaml_call
        and yaml_out["semantic_projection_status"] == "PROJECTED_DIRECT_USER_VIEWER_OUTCOME"
        and "content_promise" not in yaml_out["gaps_text"],
        {"status": yaml_out["semantic_projection_status"], "gaps": yaml_out["gaps_text"]}))
    controls.append(check(
        "P02_yaml_expected_change_is_not_overwritten",
        BT+"expected_change"+BT+": "+yaml_value in yaml_call, yaml_call))

    g2_out = run(fn, raw[RUNS["g2"]])
    g2_call = g2_out["capability_call"]
    outcome = "怎么把一件外套穿得更精神"
    controls.append(check(
        "P03_natural_turn_projects_when_hop_omits_both",
        BT+"expected_change"+BT+": "+outcome in g2_call
        and BT+"content_promise"+BT+": "+outcome in g2_call
        and "expected_change" not in g2_out["gaps_text"]
        and "content_promise" not in g2_out["gaps_text"],
        {"status": g2_out["semantic_projection_status"], "gaps": g2_out["gaps_text"]}))

    explicit = synthetic(
        "我想让她知道怎么把外套穿得更精神。",
        "target_capability: CONTENT_BRIEF\n"+BT+"content_promise"+BT+": 已有用户明确的承诺",
        "无", no_goal_snapshot())
    explicit_out = run(fn, explicit)
    controls.append(check(
        "P04_explicit_content_promise_wins",
        BT+"content_promise"+BT+": 已有用户明确的承诺" in explicit_out["capability_call"]
        and outcome not in explicit_out["capability_call"], explicit_out["capability_call"]))

    full_out = run(fn, raw[RUNS["full"]])
    full_call = full_out["capability_call"]
    controls.append(check(
        "P05_m3_commercial_goal_not_promoted_to_user",
        BT+"primary_goal"+BT+": 促进这件秋冬新款廓形西装外套的购买决策" not in full_call
        and field(full_out, "objective.primary_goal") is not None
        and field(full_out, "objective.primary_goal").get("kind") != "USER_UTTERANCE"
        and full_out["authority_guard_status"] == "REJECTED_UNSUPPORTED_PRIMARY_GOAL",
        {"guard": full_out["authority_guard_status"],
         "canonical": field(full_out, "objective.primary_goal")}))

    explicit_purchase = synthetic(
        "我希望促进购买决策，先做一条内容。",
        "target_capability: CONTENT_BRIEF\n"+BT+"primary_goal"+BT+": 促进购买决策",
        "无", {"revision": 1, "goal_structure": {"primary_goal": "促进购买决策"}})
    purchase_out = run(fn, explicit_purchase)
    controls.append(check(
        "P06_explicit_user_commercial_goal_is_preserved",
        field(purchase_out, "objective.primary_goal") is not None
        and field(purchase_out, "objective.primary_goal").get("kind") == "USER_UTTERANCE"
        and BT+"primary_goal"+BT+": 促进购买决策" in purchase_out["capability_call"],
        field(purchase_out, "objective.primary_goal")))

    negatives = {"N01_product_only": "主推一件廓形西装外套。",
                 "N02_audience_only": "内容给城市通勤女性看。",
                 "N03_pain_only": "她早上试很多套还是不够精神。",
                 "N04_make_content_only": "帮我做一条内容。"}
    for control_id, user in negatives.items():
        output = run(fn, synthetic(
            user, "target_capability: CONTENT_BRIEF",
            "expected_change；content_promise", no_goal_snapshot()))
        controls.append(check(
            control_id+"_does_not_invent_viewer_outcome",
            BT+"content_promise"+BT+":" not in output["capability_call"]
            and "content_promise" in output["gaps_text"],
            {"call": output["capability_call"], "gaps": output["gaps_text"]}))

    mismatch = synthetic(
        "主推秋冬新款廓形西装外套。",
        "target_capability: CONTENT_BRIEF\n"+BT+"primary_goal"+BT+": 促进购买决策",
        "无", {"revision": 1, "goal_structure": {"primary_goal": "提升自然触达"}})
    mismatch_out = run(fn, mismatch)
    controls.append(check(
        "N05_mismatched_m1_source_ref_rejected",
        BT+"primary_goal"+BT+":" not in mismatch_out["capability_call"]
        and mismatch_out["authority_guard_status"] == "REJECTED_UNSUPPORTED_PRIMARY_GOAL",
        mismatch_out["authority_guard_status"]))

    deny = synthetic(
        "我不希望促进购买决策，只讲真实穿搭方法。",
        "target_capability: CONTENT_BRIEF\n"+BT+"primary_goal"+BT+": 促进购买决策",
        "无", no_goal_snapshot())
    deny_out = run(fn, deny)
    controls.append(check(
        "N06_user_denial_rejects_inferred_commercial_goal",
        BT+"primary_goal"+BT+":" not in deny_out["capability_call"], deny_out["capability_call"]))

    corrected_previous = {
        "task_key": "test-task", "rev": 3, "asked": [], "artifacts": [], "events": [],
        "fields": {"objective.primary_goal": {
            "v": "只讲真实穿搭方法", "lvl": "A", "kind": "USER_UTTERANCE",
            "ref": "TURN3.user_request", "sc": "CONTENT_TASK", "frev": 2, "origin_turn": 3}}}
    corrected = synthetic(
        "不以购买为目标，只讲真实穿搭方法。",
        "target_capability: CONTENT_BRIEF\n"+BT+"primary_goal"+BT+": 促进购买决策",
        "无", no_goal_snapshot(), corrected_previous, "APPLIED")
    corrected_out = run(fn, corrected)
    controls.append(check(
        "N07_correction_does_not_restore_rejected_goal",
        BT+"primary_goal"+BT+":" not in corrected_out["capability_call"]
        and field(corrected_out, "objective.primary_goal").get("v") == "只讲真实穿搭方法",
        {"call": corrected_out["capability_call"],
         "canonical": field(corrected_out, "objective.primary_goal")}))

    declared = set(next(node["data"]["outputs"] for node in candidate["nodes"]
                        if node["id"] == "uapp_fields"))
    controls.append(check(
        "G01_fields_outputs_declared",
        set(yaml_out) <= declared and {"semantic_projection_status", "authority_guard_status"} <= declared,
        {"undeclared": sorted(set(yaml_out) - declared)}))
    controls.append(check(
        "G02_only_authorized_node_changed",
        graph_report["touched_nodes"] == ["uapp_fields"] and graph_report["protected_nodes_unchanged"],
        graph_report))
    controls.append(check(
        "G03_no_fixture_specific_branch",
        all(token not in source for token in ("UAPP-EQUIV", "秋冬新款廓形西装外套", "三天不重样")),
        "candidate fields source has no frozen-case literal"))

    failed = [row for row in controls if row["result"] == "FAIL"]
    report = {"document": {"id": "UAPP_AC12_SEMANTIC_HANDOFF_DETERMINISTIC_CONTROLS_v1.0",
                           "model_calls": 0},
              "candidate": graph_report,
              "summary": {"total": len(controls), "pass": len(controls)-len(failed),
                          "fail": len(failed)}, "controls": controls}
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
