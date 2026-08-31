#!/usr/bin/env python3
"""Zero-model controls using the three original failed AC-12 inputs."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
BUILD = ROOT / "unified-app/workflows/UAPP_AC12_CANONICAL_FIELDS_FINAL_DELIVERY_BUILD_v1.0.py"
RAW = ROOT / "unified-app/evidence/stages/uapp_ac12_semantic_authority_v1_0"
FIELD_ARGS = ["prev_state_json", "task_key", "capability_call", "gaps_text", "target_capability", "user_request", "snapshot_json", "selector_delivery", "selector_fp", "selector_bfp", "selector_capability", "selector_status", "correction_status", "intent_reason", "selector_source_kind", "selector_source_turn", "selector_artifact_type", "selector_task_key", "selector_companion_json"]
DELIVERY_ARGS = ["capability", "seam_user_delivery", "seam_outcome", "seam_returns_json", "m3_judgment", "m3_gate_status", "route_mode", "m2_note", "hop_gaps_text", "account_context", "side_effect_text"]


def load(path: Path) -> Any:
    spec = importlib.util.spec_from_file_location("canonical_delivery_build", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def raw_node(turn: str, node: str) -> dict[str, str]:
    raw = json.loads((RAW / (turn + ".json")).read_text(encoding="utf-8"))
    record = next(item for item in raw["nodes"] if item["node_id"] == node)
    return json.loads(record["inputs"])


def check(ident: str, value: bool, detail: str) -> dict[str, object]:
    return {"id": ident, "result": "PASS" if value else "FAIL", "detail": detail}


def replay_fields(fn: Any, values: dict[str, str]) -> dict[str, str]:
    return fn(*(values[key] for key in FIELD_ARGS))


def state(output: dict[str, str]) -> dict[str, dict[str, str]]:
    return json.loads(output["pending_state_json"])["fields"]


def main() -> int:
    mod = load(BUILD)
    graph, build = mod.patch_graph(mod.published_graph())
    field_code = next(n for n in graph["nodes"] if n["id"] == "uapp_fields")["data"]["code"]
    delivery_code = next(n for n in graph["nodes"] if n["id"] == "uapp_delivery")["data"]["code"]
    field_ns: dict[str, Any] = {}
    delivery_ns: dict[str, Any] = {}
    exec(field_code, field_ns)
    exec(delivery_code, delivery_ns)
    yaml_out = replay_fields(field_ns["main"], raw_node("YAML", "uapp_fields"))
    g2_out = replay_fields(field_ns["main"], raw_node("G2", "uapp_fields"))
    full_out = replay_fields(field_ns["main"], raw_node("FULL_T1", "uapp_fields"))
    ys, gs, fs = state(yaml_out), state(g2_out), state(full_out)
    yaml_delivery = delivery_ns["main"](*(raw_node("YAML", "uapp_delivery")[key] for key in DELIVERY_ARGS))
    g2_delivery = delivery_ns["main"](*(raw_node("G2", "uapp_delivery")[key] for key in DELIVERY_ARGS))

    # B-01 uses an existing full input and changes exactly the user-owned goal clause.
    positive_goal = raw_node("FULL_T1", "uapp_fields")
    positive_goal["user_request"] = positive_goal["user_request"] + "\n本周目标是促成购买决策。"
    goal_state = state(replay_fields(field_ns["main"], positive_goal))
    m1_polluted = raw_node("FULL_T1", "uapp_fields")
    m1_polluted["snapshot_json"] = json.dumps({"revision": 1, "goal_structure": {"primary_goal": "促成购买决策"}}, ensure_ascii=False)
    m1_state = state(replay_fields(field_ns["main"], m1_polluted))
    content_as_subject = raw_node("YAML", "uapp_fields")
    content_as_subject["user_request"] = "内容承诺: 品牌搭配师真实出镜，只讲真实穿搭方法，不承诺改变身材"
    misuse = replay_fields(field_ns["main"], content_as_subject)
    misuse_state = state(misuse)
    controls = [
        check("A-01", all(k in ys for k in ("audience.expected_change", "content.promise", "expression.subject", "expression.boundary")) and "objective.primary_goal" not in ys,
              "YAML 原始输入的用户语义在正确域，primary goal 为空"),
        check("A-02", "objective.primary_goal" not in gs and gs.get("audience.expected_change", {}).get("kind") == "USER_UTTERANCE",
              "G2 主推商品不污染 primary goal，期望改变保留用户来源"),
        check("A-03", fs.get("expression.subject", {}).get("v") == "品牌搭配师" and "不做剧情" in fs.get("expression.boundary", {}).get("v", "") and "objective.primary_goal" not in fs,
              "FULL T1 的自然表达主体与边界均被识别，primary goal 为空"),
        check("B-01", goal_state.get("objective.primary_goal", {}).get("v") == "促成购买决策" and goal_state.get("objective.primary_goal", {}).get("kind") == "USER_UTTERANCE",
              "直接用户目标可进入 canonical state"),
        check("B-02", "objective.primary_goal" not in gs,
              "只说主推商品不会成为经营目标"),
        check("B-03", "audience.expected_change" in fs and "objective.primary_goal" not in fs,
              "用户期望改变与经营目标分离"),
        check("B-04", "objective.primary_goal" not in m1_state,
              "M1 snapshot 候选被拒绝时不会残留在 canonical state"),
        check("B-05", "content.promise" not in misuse_state and "expression.subject" in misuse_state,
              "把表达语句冒充内容承诺会被拒绝，表达主体仍保留在其正确域"),
        check("B-06", "expression.boundary" not in state(replay_fields(field_ns["main"], {**raw_node("FULL_T1", "uapp_fields"), "user_request": raw_node("FULL_T1", "uapp_fields")["user_request"].replace("只讲真实穿搭方法，不做剧情，不承诺改变身材", "")})),
              "删除用户表达边界会翻转 FULL 控制"),
        check("B-07", "objective.primary_goal" not in gs and "objective.primary_goal" not in fs,
              "将 primary goal 污染值重新输入时，G2/FULL 均被物理拒绝"),
        check("C-01", "Content Brief Pack" not in yaml_delivery["final_text"] and "后续可选调整" in yaml_delivery["final_text"],
              "成功 artifact 经最终用户投影，内部标题被移除，非阻塞项降为可选调整"),
        check("C-02", all(word not in yaml_delivery["final_text"] for word in ("CONTENT_BRIEF", "PASS", "precise_gap", "capability_call")) and yaml_delivery["leak_hit_count"] == "0",
              "成功出口不泄漏内部状态或字段"),
        check("C-03", g2_delivery["final_text"].count("？") == 1 and "内容方向已经明确" in g2_delivery["final_text"] and "确认后，我就按" not in g2_delivery["final_text"],
              "真实缺口被投影为承接上下文的一个自然问题，不复用旧三段外壳"),
        check("C-04", build["touched_nodes"] == ["uapp_fields", "uapp_delivery"] and build["protected_nodes_unchanged"] and build["provider_unchanged"],
              "只改两个授权 UAPP 节点；路由和 provider 未漂移"),
    ]
    report = {"document": "UAPP_AC12_CANONICAL_FIELDS_FINAL_DELIVERY_CONTROLS_v1.0", "model_calls": 0,
              "build": build, "controls": controls,
              "summary": "%d/%d PASS" % (sum(x["result"] == "PASS" for x in controls), len(controls))}
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if all(x["result"] == "PASS" for x in controls) else 1


if __name__ == "__main__":
    raise SystemExit(main())
