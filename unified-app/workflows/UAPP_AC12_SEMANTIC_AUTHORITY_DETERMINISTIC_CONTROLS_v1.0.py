#!/usr/bin/env python3
"""Deterministic source-authority controls for the AC-12 successor."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BUILD = ROOT / "unified-app/workflows/UAPP_AC12_SEMANTIC_AUTHORITY_BUILD_v1.0.py"


def load(path: Path):
    spec = importlib.util.spec_from_file_location("authority_build", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)
    return mod


def call(code: str, query: str, envelope: str, gaps: str = "无"):
    ns: dict[str, object] = {}
    exec(code, ns)
    return ns["main"]("", "task-1", envelope, gaps, "CONTENT_BRIEF", query, "{}",
                      "", "", "", "", "", "", "", "", "", "", "", "")


def check(name: str, value: bool, detail: str) -> dict[str, object]:
    return {"id": name, "result": "PASS" if value else "FAIL", "detail": detail}


def main() -> int:
    mod = load(BUILD)
    graph, build = mod.patch_graph(mod.published_graph())
    fields = next(n for n in graph["nodes"] if n["id"] == "uapp_fields")["data"]["code"]
    seam = next(n for n in graph["nodes"] if n["id"] == "uapp_seam")["data"]
    query = '''受众: "城市通勤女性"
希望她看完明白: "缺的不是衣服数量，而是一件能压住整套的外套"
表达主体: "品牌搭配师真实出镜"
表达边界: "只讲真实穿搭方法，不承诺改变身材"
主目标: "建立穿搭判断价值"
只做一条内容。'''
    old_wrong = '''objective:
  `primary_goal`: 促进购买决策
`expected_change`: 缺的不是衣服数量，而是一件能压住整套的外套
`content_promise`: 品牌搭配师真实出镜，只讲真实穿搭方法，不承诺改变身材
`expression_subject_and_boundary`: 品牌搭配师真实出镜；只讲真实穿搭方法，不承诺改变身材'''
    positive = call(fields, query, old_wrong, "content_promise")
    state = json.loads(positive["pending_state_json"])["fields"]
    cap = positive["capability_call"]
    negative_goal = call(fields, query.replace('主目标: "建立穿搭判断价值"\n', ""), old_wrong)
    negative_state = json.loads(negative_goal["pending_state_json"])["fields"]
    no_outcome = call(fields, "表达主体: 品牌搭配师真实出镜\n表达边界: 只讲真实方法",
                      old_wrong, "content_promise")
    no_outcome_cap = no_outcome["capability_call"]
    results = [
        check("A-01", state.get("audience.expected_change", {}).get("lvl") == "A",
              "用户期望改变以 A 级写入"),
        check("A-02", state.get("content.promise", {}).get("v") == state.get("audience.expected_change", {}).get("v"),
              "内容承诺取用户观看结果，不取表达主体或边界"),
        check("A-03", state.get("expression.subject", {}).get("v") == "品牌搭配师真实出镜" and
              state.get("expression.boundary", {}).get("v") == "只讲真实穿搭方法，不承诺改变身材",
              "表达主体与边界独立保存"),
        check("A-04", state.get("objective.primary_goal", {}).get("v") == "建立穿搭判断价值" and
              "促进购买决策" not in cap,
              "用户明确目标可进入；专业购买建议不能覆盖"),
        check("N-01", "objective.primary_goal" not in negative_state,
              "删除用户来源后，专业建议不能升级为用户主目标"),
        check("N-02", "品牌搭配师真实出镜，只讲真实穿搭方法" not in
              state.get("content.promise", {}).get("v", ""),
              "表达边界注入内容承诺会被检出"),
        check("N-03", "content_promise" not in no_outcome_cap or
              "缺的不是衣服数量" not in no_outcome_cap,
              "删除用户结果后不得由旧专业投影补造内容承诺"),
        check("A-05", state.get("content.quantity", {}).get("v") == "1",
              "用户明确的一条内容作为独立约束保存"),
        check("A-06", seam["tool_parameters"]["professional_input"]["value"] ==
              "{{#uapp_fields.professional_input_safe#}}",
              "Seam 调用只接收非权威专业参考投影"),
        check("A-07", "值得买" not in positive["professional_input_safe"] and
              "capability_call 为准" in positive["professional_input_safe"],
              "raw professional_input 无法作为业务决定旁路"),
        check("A-08", build["protected_nodes_unchanged"] and build["seam_routing_unchanged"],
              "路由、M3、Hop 与 Seam provider 未变"),
    ]
    report = {"document": "UAPP_AC12_SEMANTIC_AUTHORITY_DETERMINISTIC_CONTROLS_v1.0",
              "model_calls": 0, "build": build, "controls": results,
              "summary": "%d/%d PASS" % (sum(r["result"] == "PASS" for r in results), len(results))}
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if all(r["result"] == "PASS" for r in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
