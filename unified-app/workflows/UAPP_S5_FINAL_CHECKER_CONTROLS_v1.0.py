#!/usr/bin/env python3
"""Zero-model positive and single-variable controls for the final S5 checker."""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import os
from types import ModuleType
from typing import Any

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
SCENARIOS = os.path.join(ROOT, "stages", "UAPP_S5_FROZEN_SCENARIOS_v1.2.json")
OUTPUT = os.path.join(
    ROOT,
    "evidence",
    "stages",
    "s5_final_convergence_v1_0",
    "preflight",
    "UAPP_S5_FINAL_CHECKER_CONTROLS_v1.0.json",
)
GRAPHS = {
    "UAPP": "40a436cdbc11823eca16d2f1c5ecb037",
    "M3": "cd93757bcf8ad322f3b32fc43b2da3ff",
    "HOP": "e38378c3c2a66b75aa7e645368c9e1ce",
    "SEAM": "db49a3da8973d4fdcbe9ecf63bdf7e2a",
    "MATRIX": "6cdaeac9cacf69fbeea4bd25e1536ace",
    "CAMPAIGN": "4876dacc43a73741b41c5a3083796347",
    "CONTENT_BRIEF": "0c841642a71feedfb327ffb76aec0ddd",
    "CREATIVE_SCRIPT": "a1cd859d5b88d0d025f336665ca94e51",
    "PRODUCTION_DIRECTOR": "964e9a947dc9790d1de82496469689ad",
    "PUBLISHING_PACKAGING": "99287feadcd784e86bf4c298bea555fc",
    "PP_provider": "99287feadcd784e86bf4c298bea555fc",
}


def load_module(name: str, path: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


CHECKER = load_module(
    "uapp_s5_final_checker_controls",
    os.path.join(HERE, "UAPP_S5_FINAL_CHECKER_v1.0.py"),
)


def loaded(path: str) -> dict[str, Any]:
    with open(path, encoding="utf-8") as handle:
        result = json.load(handle)
    return result


def fnv(value: str) -> str:
    number = 0xCBF29CE484222325
    for byte in value.encode("utf-8"):
        number = ((number ^ byte) * 0x100000001B3) & 0xFFFFFFFFFFFFFFFF
    return f"{number:016x}"


def execution(
    node_id: str, outputs: dict[str, Any] | None = None, node_type: str = "code"
) -> dict[str, Any]:
    return {
        "node_id": node_id,
        "type": node_type,
        "status": "succeeded",
        "error": None,
        "outputs": json.dumps(outputs or {}, ensure_ascii=False),
    }


def app_run(name: str) -> dict[str, Any]:
    return {
        "id": f"run-{name}",
        "status": "succeeded",
        "node_detail": [execution(f"{name.lower()}-llm", node_type="llm")],
    }


def artifact(raw: dict[str, Any], capability: str) -> None:
    body = "这是一份用于确定性判别的真实专业产物正文。" * 20
    normalized = body.strip()
    record = {
        "cap": capability,
        "body": body,
        "len": len(body),
        "nlen": len(normalized),
        "fp": fnv(normalized[:256]),
        "bfp": fnv(normalized),
    }
    raw["conversation_variables_after"].update(
        {
            "uapp_last_artifact": json.dumps({"items": [record]}, ensure_ascii=False),
            "uapp_task_fields": json.dumps(
                {"artifacts": [{"cap": capability, "fp": record["fp"]}]},
                ensure_ascii=False,
            ),
            "uapp_last_capability": capability,
        }
    )
    raw["app_runs_in_window"]["UAPP"][0]["node_detail"].append(
        execution("uapp_seam", {"artifact": body})
    )
    raw["app_runs_in_window"][capability] = [app_run(capability)]
    raw["m2_after"]["artifacts"] = [{"id": "artifact-1"}]
    raw["m2_after"]["content_versions"] = [{"id": "version-1"}]


def ideal(turn: dict[str, Any], gate: dict[str, Any]) -> dict[str, Any]:
    key = turn["key"]
    rows = {
        name: []
        for name in (
            "workspace",
            "cycles",
            "tasks",
            "materials",
            "artifacts",
            "content_versions",
            "publish_instances",
            "feedback_records",
            "task_snapshots",
            "task_run_states",
        )
    }
    rows["workspace"] = [{"id": "workspace-1"}]
    rows["tasks"] = [{"id": "task-1", "workspace_id": "workspace-1"}]
    runs = {name: [] for name in ["UAPP", "M3", "HOP", "SEAM", *CHECKER.CAPABILITIES]}
    top = [
        execution("top-llm", node_type="llm"),
        execution("uapp_route", {"target_capability": ""}),
    ]
    raw: dict[str, Any] = {
        "turn_key": key,
        "request": {"query": turn["query"], "inputs": {}},
        "request_attempts_by_runner": 1,
        "http_status": 200,
        "transport_error": "",
        "workflow_run_id": "top-run",
        "answer": "已按你提供的信息处理。",
        "conversation_id": f"conversation-{turn['conversation_group']}",
        "app_runs_in_window": runs,
        "m2_after": rows,
        "global_m2_after": copy.deepcopy(gate["protected_surface"]["global_m2_before"]),
        "protected_apps_after": {
            name: {"graph_md5": value} for name, value in GRAPHS.items()
        },
        "conversation_variables_after": {},
    }
    runs["UAPP"] = [{"id": "top-run", "status": "succeeded", "node_detail": top}]
    if key == "UAPP-WITHDRAW-01:W0":
        text = "品牌真实资料正文"
        digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
        upload_id = "upload-1"
        material = {
            "id": "material-1",
            "workspace_id": "workspace-1",
            "withdrawn_at": None,
            "publish_authorized": False,
            "content_ref": f"dify-upload:{upload_id}#sha256={digest}",
            "scope_ref": {
                "task_id": "task-1",
                "account_id": "account-1",
                "is_test": True,
                "is_simulated": True,
                "dify_upload_id": upload_id,
                "file_name": "fixture.md",
                "extracted_text_sha256": digest,
            },
        }
        rows["materials"] = [material]
        binding = {
            **material["scope_ref"],
            "workspace_id": "workspace-1",
            "material_id": "material-1",
            "publish_authorized": False,
        }
        raw["upload"] = {
            "http_status": 201,
            "sha256": "fixture-hash",
            "response": {"id": upload_id},
        }
        raw["conversation_variables_after"] = {
            "uapp_last_material": "material-1",
            "uapp_material_binding": json.dumps(binding, ensure_ascii=False),
        }
        top.extend(
            [
                execution("m1_join", {"material_text": text}),
                execution(
                    "uapp_material_prepare",
                    {
                        "decision": "REGISTER",
                        "file_hash": digest,
                        "upload_id": upload_id,
                        "file_name": "fixture.md",
                    },
                ),
                execution(
                    "uapp_material_parse", {"ok": "true", "material_id": "material-1"}
                ),
            ]
        )
    elif key == "UAPP-WITHDRAW-01:W1":
        digest = hashlib.sha256("品牌真实资料正文".encode("utf-8")).hexdigest()
        rows["materials"] = [
            {
                "id": "material-1",
                "workspace_id": "workspace-1",
                "withdrawn_at": "2026-08-30T00:00:00Z",
                "publish_authorized": False,
                "content_ref": f"dify-upload:upload-1#sha256={digest}",
            }
        ]
    elif turn.get("equivalence", "").startswith("positive"):
        top[1] = execution("uapp_route", {"target_capability": "CONTENT_BRIEF"})
        top.append(
            execution(
                "uapp_fields",
                {
                    "pending_state_json": json.dumps(
                        {
                            "fields": {
                                "expression.subject_and_boundary": {
                                    "value": "由品牌搭配师真实出镜表达"
                                },
                                "audience.expected_change": {
                                    "value": "知道如何用外套三天不重样"
                                },
                            }
                        },
                        ensure_ascii=False,
                    ),
                    "gaps_text": "无",
                },
            )
        )
        artifact(raw, "CONTENT_BRIEF")
    elif turn.get("equivalence", "").startswith("negative"):
        raw["answer"] = "还需要确认希望受众看完明白什么或发生什么改变？"
    elif key == "UAPP-FULL-01:T1":
        rows["cycles"] = [{"id": "cycle-1"}]
        top[1] = execution("uapp_route", {"target_capability": "CONTENT_BRIEF"})
        top.append(
            execution(
                "uapp_fields",
                {
                    "pending_state_json": json.dumps(
                        {
                            "fields": {
                                "expression.subject_and_boundary": {
                                    "value": "由品牌搭配师真实出镜表达"
                                }
                            }
                        },
                        ensure_ascii=False,
                    )
                },
            )
        )
        artifact(raw, "CONTENT_BRIEF")
    elif key == "UAPP-FULL-01:T2":
        rows["content_versions"] = [{"id": "version-1"}]
        rows["publish_instances"] = [
            {
                "id": "publish-1",
                "content_version_id": "version-1",
                "is_test": True,
                "is_simulated": True,
            }
        ]
        raw["answer"] = "已登记为测试模拟记录，没有操作真实平台。"
    elif key == "UAPP-FULL-01:T3":
        rows["feedback_records"] = [
            {
                "id": "feedback-1",
                "publish_instance_id": "publish-1",
                "is_test": True,
                "is_simulated": True,
            }
        ]
    elif key == "UAPP-FULL-01:T4":
        rows["cycles"] = [{"id": "cycle-1"}, {"id": "cycle-2"}]
        rows["feedback_records"] = [{"id": "feedback-1"}]
    elif key == "UAPP-RECOVERY-01:R1":
        rows["feedback_records"] = [{"id": "feedback-1"}]
    return raw


def mutate(raw: dict[str, Any], check_id: str) -> None:
    top = raw["app_runs_in_window"]["UAPP"][0]["node_detail"]
    if check_id == "T-01":
        raw["request"]["query"] += "x"
    elif check_id == "T-02":
        raw["request"]["inputs"] = {"x": 1}
    elif check_id == "T-03":
        raw["http_status"] = 500
    elif check_id == "T-04":
        top.append(
            {
                "node_id": "bad",
                "type": "code",
                "status": "failed",
                "error": "x",
                "outputs": "{}",
            }
        )
    elif check_id == "T-05":
        raw["answer"] += " uapp_internal"
    elif check_id == "T-06":
        raw["global_m2_after"]["non_test_publish_instances"] += 1
    elif check_id == "T-07":
        raw["protected_apps_after"]["UAPP"]["graph_md5"] = "drift"
    elif check_id == "T-08":
        for app_rows in raw["app_runs_in_window"].values():
            for run in app_rows:
                for node in run["node_detail"]:
                    if node.get("type") == "llm":
                        node["type"] = "code"
    elif check_id == "WITHDRAW-W0-01":
        raw["m2_after"]["materials"] = []
    elif check_id == "WITHDRAW-W0-02":
        top[:] = [node for node in top if node["node_id"] != "uapp_material_parse"]
    elif check_id == "WITHDRAW-W0-03":
        raw["m2_after"]["materials"][0]["scope_ref"]["extracted_text_sha256"] = "bad"
    elif check_id == "WITHDRAW-W0-04":
        raw["m2_after"]["materials"][0]["scope_ref"]["dify_upload_id"] = "bad"
    elif check_id == "WITHDRAW-W0-05":
        raw["m2_after"]["materials"][0]["scope_ref"]["task_id"] = "bad"
    elif check_id == "WITHDRAW-W0-06":
        raw["m2_after"]["materials"][0]["publish_authorized"] = True
    elif check_id == "WITHDRAW-W1-01":
        raw["m2_after"]["materials"][0]["withdrawn_at"] = None
    elif check_id == "WITHDRAW-W1-02":
        raw["m2_after"]["materials"][0]["content_ref"] = "changed"
    elif check_id == "WITHDRAW-W1-03":
        raw["app_runs_in_window"]["MATRIX"] = [app_run("MATRIX")]
    elif check_id == "EQUIV-P1":
        top[1]["outputs"] = json.dumps({"target_capability": "WRONG"})
    elif check_id == "EQUIV-P2" or check_id == "FULL-01":
        raw["conversation_variables_after"]["uapp_last_artifact"] = "{}"
    elif check_id == "EQUIV-P3" or check_id == "FULL-T1-SUBJECT":
        for node in top:
            if node["node_id"] == "uapp_fields":
                node["outputs"] = json.dumps({"pending_state_json": '{"fields":{}}'})
    elif check_id == "EQUIV-N1":
        raw["app_runs_in_window"]["CONTENT_BRIEF"] = [app_run("CONTENT_BRIEF")]
    elif check_id == "EQUIV-N2":
        raw["answer"] = "请补充由谁出镜。"
    elif check_id == "FULL-02":
        raw["m2_after"]["publish_instances"][0]["is_test"] = False
    elif check_id == "FULL-02B":
        raw["answer"] = "已登记。"
    elif check_id == "FULL-T2-BINDING":
        raw["m2_after"]["publish_instances"][0]["content_version_id"] = "bad"
    elif check_id == "FULL-03":
        raw["m2_after"]["feedback_records"] = []
    elif check_id == "FULL-T3-BINDING":
        raw["m2_after"]["feedback_records"][0]["publish_instance_id"] = "bad"
    elif check_id == "FULL-04":
        raw["m2_after"]["cycles"] = raw["m2_after"]["cycles"][:1]
    elif check_id == "FULL-T4-CONTINUITY" or check_id == "RECOVERY-01":
        raw["conversation_id"] = "wrong"
    elif check_id == "RECOVERY-IDEMPOTENCY":
        raw["m2_after"]["feedback_records"][0]["id"] = "new"
    else:
        raise RuntimeError(f"No mutation for {check_id}")


def main() -> int:
    scenarios = loaded(SCENARIOS)
    authorized = {
        "UAPP-WITHDRAW-01:W0",
        "UAPP-WITHDRAW-01:W1",
        "UAPP-EQUIV-01a",
        "UAPP-EQUIV-01b",
        "UAPP-EQUIV-01c",
        "UAPP-EQUIV-01n",
        "UAPP-FULL-01:T1",
        "UAPP-FULL-01:T2",
        "UAPP-FULL-01:T3",
        "UAPP-FULL-01:T4",
        "UAPP-RECOVERY-01:R1",
    }
    turns = [turn for turn in scenarios["turns"] if turn["key"] in authorized]
    gate = {
        "candidate": {"graph_md5": GRAPHS},
        "protected_surface": {
            "global_m2_before": {
                "non_test_publish_instances": 1568,
                "non_test_feedback_records": 117,
                "schema_md5": "25192c11562827efedfc3b2c22c3b4fd",
            }
        },
        "budget": {"per_turn_static_reachable_llm_nodes": 6},
    }
    predecessors: dict[str, dict[str, Any]] = {}
    controls: list[dict[str, Any]] = []
    for turn in turns:
        raw = ideal(turn, gate)
        key = turn["key"]
        if key == "UAPP-WITHDRAW-01:W1":
            before_turn = next(
                item for item in turns if item["key"] == "UAPP-WITHDRAW-01:W0"
            )
            before = ideal(before_turn, gate)
            before["conversation_id"] = raw["conversation_id"]
            predecessors["UAPP-WITHDRAW-01:W0"] = before
            CHECKER.raw_path = lambda unused: ""
        elif key == "UAPP-FULL-01:T3":
            before = ideal(
                next(item for item in turns if item["key"] == "UAPP-FULL-01:T2"), gate
            )
            before["conversation_id"] = raw["conversation_id"]
            predecessors["UAPP-FULL-01:T2"] = before
        elif key == "UAPP-FULL-01:T4":
            before = ideal(
                next(item for item in turns if item["key"] == "UAPP-FULL-01:T3"), gate
            )
            before["conversation_id"] = raw["conversation_id"]
            predecessors["UAPP-FULL-01:T3"] = before
        elif key == "UAPP-RECOVERY-01:R1":
            before = ideal(
                next(item for item in turns if item["key"] == "UAPP-FULL-01:T4"), gate
            )
            before["conversation_id"] = raw["conversation_id"]
            predecessors["UAPP-FULL-01:T4"] = before
        positive = CHECKER.evaluate_turn(raw, turn, gate, predecessors)
        if positive["verdict"] != "PASS":
            raise RuntimeError(f"Positive failed {key}: {positive}")
        controls.append({"turn_key": key, "control": "positive", "result": "PASS"})
        for check in positive["checks"]:
            changed = copy.deepcopy(raw)
            mutate(changed, check["id"])
            negative = CHECKER.evaluate_turn(changed, turn, gate, predecessors)
            matches = [item for item in negative["checks"] if item["id"] == check["id"]]
            flipped = len(matches) == 1 and matches[0]["result"] == "FAIL"
            if not flipped:
                raise RuntimeError(f"Negative failed {key}/{check['id']}: {negative}")
            controls.append(
                {
                    "turn_key": key,
                    "control": f"single_variable_negative:{check['id']}",
                    "result": "PASS",
                }
            )
    report = {
        "document": {
            "id": "UAPP_S5_FINAL_CHECKER_CONTROLS_v1.0",
            "task_id": "DIYU-V1-UNIFIED-DIFY-APPLICATION-001",
        },
        "model_calls": 0,
        "positive_controls": len(turns),
        "single_variable_negative_controls": len(controls) - len(turns),
        "all_pass": True,
        "controls": controls,
    }
    os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
    with open(OUTPUT, "x", encoding="utf-8") as handle:
        json.dump(report, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    print(
        json.dumps(
            {
                key: report[key]
                for key in (
                    "positive_controls",
                    "single_variable_negative_controls",
                    "all_pass",
                )
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
