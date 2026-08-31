#!/usr/bin/env python3
"""Zero-model discrimination controls for the fresh S5 successor."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from types import ModuleType
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[2]
BUILD_PATH = ROOT / "unified-app/workflows/UAPP_S5_FRESH_FINAL_BUILD_v1.0.py"
SCENARIOS = ROOT / "unified-app/stages/UAPP_S5_FROZEN_SCENARIOS_v1.2.json"


def load_module(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


BUILD = load_module("uapp_s5_fresh_final_build", BUILD_PATH)


def function(source: str) -> Callable[..., dict[str, str]]:
    namespace: dict[str, Any] = {}
    exec(source, namespace)  # noqa: S102 - frozen code-node source is the test subject
    return namespace["main"]


def check(control_id: str, passed: bool, detail: Any) -> dict[str, Any]:
    return {"id": control_id, "result": "PASS" if passed else "FAIL", "detail": detail}


def fixture() -> tuple[str, str]:
    body = "这是一份当前内容正文。"
    state = {
        "task_key": "task-key-1", "rev": 3, "events": [],
        "artifacts": [{"fp": "fp-1", "task_key": "task-key-1",
                       "cap": "CONTENT_BRIEF", "accepted": False, "stale": False}],
    }
    store = {"v": 1, "items": [{"fp": "fp-1", "task_key": "task-key-1",
                                  "cap": "CONTENT_BRIEF", "body": body}]}
    return json.dumps(store, ensure_ascii=False), json.dumps(state, ensure_ascii=False)


def main() -> int:
    normalize = function(BUILD.NORMALIZE_SRC)
    publish = function(BUILD.PUBLISH_PREP_SRC)
    feedback = function(BUILD.FEEDBACK_PREP_SRC)
    cycle = function(BUILD.CYCLE_PREP_SRC)
    turns = {item["key"]: item["query"]
             for item in json.loads(SCENARIOS.read_text(encoding="utf-8"))["turns"]}
    controls: list[dict[str, Any]] = []

    plain = normalize(turns["UAPP-EQUIV-01a"])
    yaml_like = normalize(turns["UAPP-EQUIV-01b"])
    json_like = normalize(turns["UAPP-EQUIV-01c"])
    negative = normalize(turns["UAPP-EQUIV-01n"])
    controls.append(check("A-01_plain_byte_preserved",
                          plain["normalized_query"] == turns["UAPP-EQUIV-01a"]
                          and plain["format_mode"] == "PLAIN", plain))
    controls.append(check("A-02_yaml_values_preserved",
                          yaml_like["format_mode"] == "YAML_LIKE"
                          and yaml_like["pair_count"] == "6"
                          and all(value in yaml_like["normalized_query"] for value in
                                  ("28-38 岁城市通勤女性", "一件能压住整套的外套",
                                   "由品牌搭配师真实出镜表达", "秋冬新款廓形西装外套")),
                          yaml_like))
    controls.append(check("A-03_json_values_preserved",
                          json_like["format_mode"] == "JSON_LIKE"
                          and json_like["pair_count"] == "6"
                          and all(value in json_like["normalized_query"] for value in
                                  ("28-38 岁城市通勤女性", "一件能压住整套的外套",
                                   "由品牌搭配师真实出镜表达", "秋冬新款廓形西装外套")),
                          json_like))
    controls.append(check("A-04_missing_expected_change_not_invented",
                          negative["format_mode"] == "YAML_LIKE"
                          and negative["pair_count"] == "5"
                          and "希望她看完明白」是" not in negative["normalized_query"], negative))
    controls.append(check("A-05_format_variant_not_hardcoded",
                          "UAPP-EQUIV" not in BUILD.NORMALIZE_SRC
                          and "廓形西装" not in BUILD.NORMALIZE_SRC
                          and normalize("对象：通勤人群\n目标：理解搭配方法")["pair_count"] == "2",
                          "generic two-field variant"))
    controls.append(check("A-06_single_colon_sentence_stays_plain",
                          normalize("我想说的是：今天先不做内容")["format_mode"] == "PLAIN",
                          normalize("我想说的是：今天先不做内容")))

    store, state = fixture()
    args = ("RECORD_PUBLISH", turns["UAPP-FULL-01:T2"], store, state,
            "task-id-1", "account-id-1", "workspace-id-1", "小红书", "")
    created = publish(*args)
    controls.append(check("B-01_explicit_publish_selects_current_content",
                          created["mode"] == "CREATE" and created["selected_fp"] == "fp-1"
                          and len(created["content_hash"]) == 64, created))
    publish_body = json.loads(created["publish_template"])
    controls.append(check("B-02_test_flags_fail_closed",
                          publish_body["is_test"] is True
                          and publish_body["is_simulated"] is True
                          and "real_publish" not in publish_body, publish_body))
    planned = publish("RECORD_PUBLISH", "这条准备明天发出去。", store, state,
                      "task-id-1", "account-id-1", "workspace-id-1", "小红书", "")
    controls.append(check("B-03_planned_publish_rejected", planned["mode"] == "INVALID", planned))
    empty_store = publish("RECORD_PUBLISH", turns["UAPP-FULL-01:T2"],
                          json.dumps({"v": 1, "items": []}), state,
                          "task-id-1", "account-id-1", "workspace-id-1", "小红书", "")
    controls.append(check("B-04_no_content_rejected", empty_store["mode"] == "INVALID", empty_store))
    stale_state = json.loads(state)
    stale_state["artifacts"][0]["stale"] = True
    stale = publish("RECORD_PUBLISH", turns["UAPP-FULL-01:T2"], store,
                    json.dumps(stale_state), "task-id-1", "account-id-1",
                    "workspace-id-1", "小红书", "")
    controls.append(check("B-05_stale_content_rejected", stale["mode"] == "INVALID", stale))
    cross_store = json.loads(store)
    cross_store["items"][0]["task_key"] = "other-task"
    cross = publish("RECORD_PUBLISH", turns["UAPP-FULL-01:T2"],
                    json.dumps(cross_store), state, "task-id-1", "account-id-1",
                    "workspace-id-1", "小红书", "")
    controls.append(check("B-06_cross_task_rejected", cross["mode"] == "INVALID", cross))
    binding = json.dumps({"task_id": "task-id-1", "selected_fp": created["selected_fp"],
                          "content_hash": created["content_hash"], "version_id": "version-1",
                          "publish_id": "publish-1"})
    reused = publish(*args[:-1], binding)
    controls.append(check("B-07_publish_idempotent_reuse", reused["mode"] == "REUSE", reused))

    feedback_ok = feedback("RECORD_FEEDBACK", turns["UAPP-FULL-01:T3"], "publish-1")
    feedback_repeat = feedback("RECORD_FEEDBACK", turns["UAPP-FULL-01:T3"], "publish-1")
    controls.append(check("B-08_feedback_bound_to_publish",
                          feedback_ok["valid"] == "true"
                          and json.loads(feedback_ok["body"])["publish_instance_id"] == "publish-1",
                          feedback_ok))
    controls.append(check("B-09_feedback_idempotency_stable",
                          feedback_ok["body"] == feedback_repeat["body"], feedback_repeat))
    feedback_gap = feedback("RECORD_FEEDBACK", turns["UAPP-FULL-01:T3"], "")
    controls.append(check("B-10_feedback_without_publish_rejected",
                          feedback_gap["valid"] == "false", feedback_gap))

    cycle_ok = cycle("NEXT_CYCLE", turns["UAPP-FULL-01:T4"], "account-1", "cycle-1",
                     "publish-1", "feedback-1", "")
    controls.append(check("B-11_cycle_requires_full_chain", cycle_ok["mode"] == "CREATE", cycle_ok))
    cycle_gap = cycle("NEXT_CYCLE", turns["UAPP-FULL-01:T4"], "account-1", "cycle-1",
                      "publish-1", "", "")
    controls.append(check("B-12_cycle_without_feedback_rejected",
                          cycle_gap["mode"] == "INVALID", cycle_gap))
    prior = json.dumps({"request_fp": cycle_ok["request_fp"], "next_cycle_id": "cycle-2"})
    cycle_reuse = cycle("NEXT_CYCLE", turns["UAPP-FULL-01:T4"], "account-1", "cycle-2",
                        "publish-1", "feedback-1", prior)
    controls.append(check("B-13_cycle_repeat_reuses",
                          cycle_reuse["mode"] == "REUSE", cycle_reuse))

    current_graph = BUILD.published_graph()
    current_ids = {item["id"] for item in current_graph["nodes"]}
    if "uapp_format_normalize" in current_ids:
        graph = current_graph
        base_raw = BUILD.database_value(
            "select graph::text from workflows "
            f"where app_id='{BUILD.APP_ID}' and md5(graph)='{BUILD.BASE_GRAPH_MD5}' "
            "order by created_at desc limit 1;"
        )
        base_nodes = {item["id"]: item for item in json.loads(base_raw)["nodes"]}
        current_nodes = {item["id"]: item for item in graph["nodes"]}
        protected_equal = all(
            BUILD.canonical(base_nodes[key]) == BUILD.canonical(current_nodes[key])
            for key in ("uapp_m3", "uapp_hop", "uapp_seam")
        )
        report = {"post_publish": True,
                  "candidate_canonical_sha256": BUILD.digest(graph),
                  "protected_tool_nodes_unchanged": protected_equal}
    else:
        graph, report = BUILD.patch_graph(current_graph)
    node_ids = [item["id"] for item in graph["nodes"]]
    edge_ids = [item["id"] for item in graph["edges"]]
    controls.append(check("G-01_graph_ids_unique",
                          len(node_ids) == len(set(node_ids)) and len(edge_ids) == len(set(edge_ids)),
                          {"nodes": len(node_ids), "edges": len(edge_ids)}))
    controls.append(check("G-02_protected_tools_unchanged",
                          report["protected_tool_nodes_unchanged"], report))
    controls.append(check("G-03_no_real_publish_endpoint",
                          all("real" not in (item.get("data", {}).get("url") or "").lower()
                              and "platform" not in (item.get("data", {}).get("url") or "").lower()
                              for item in graph["nodes"] if item.get("data", {}).get("type") == "http-request"),
                          "all HTTP endpoints remain internal M2 or existing internal services"))

    failed = [item for item in controls if item["result"] != "PASS"]
    output = {"document": {"id": "UAPP_S5_FRESH_FINAL_CONTROLS_v1.0", "model_calls": 0},
              "summary": {"total": len(controls), "pass": len(controls) - len(failed),
                          "fail": len(failed)}, "controls": controls}
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
