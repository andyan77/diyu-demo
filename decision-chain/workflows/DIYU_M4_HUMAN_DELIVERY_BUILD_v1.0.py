#!/usr/bin/env python3
"""Versioned shared user-delivery successor for the six M4 capability apps."""

from __future__ import annotations

import copy
import importlib.util
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE_PATH = ROOT / "decision-chain/workflows/DIYU_M4_DSL_BUILD_v0.1.py"


def load():
    spec = importlib.util.spec_from_file_location("m4_human_base", BASE_PATH)
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)
    return mod


NEW_COMPONENT_RETURN = r'''
import json
import re

CAPABILITY = "__CAPABILITY__"
LAYER = "__RETURN_LAYER__"

QUESTION_MAP = {
    "applicability_reason": "这次是要调整长期定位，还是先处理眼下这一条内容？",
    "subject_and_account_scope": "这次要处理的是哪个品牌或账号？",
    "objective": "这一轮最想拿到什么结果？",
    "audience_problem": "这条想说给谁听，她现在卡在哪？",
    "expected_change": "看完后，你希望她多明白什么？",
    "content_promise": "这条内容准备给观众一个什么具体收获？",
    "expression_boundary": "这条有哪些明确不能说的边界？",
    "expression_subject_and_boundary": "这条由谁来讲，并且有哪些表达边界？",
    "expression_subject": "这条由谁来讲？",
    "facts_registered": "有哪些已经确认、可以放进内容里的真实事实？",
    "deadline_or_stage_boundary": "这件事需要在什么时间或阶段前完成？",
    "capacity_or_owner": "这一轮由谁出镜或确认事实，能投入多少时间？",
    "content_origin_mode": "这条准备现拍、用已有素材剪，还是访谈？",
    "script_or_equivalent_beats": "把脚本或每一段要讲什么告诉我。",
    "production_profile": "这次按单人手机、小团队，还是商业制作来做？",
    "time_window": "这次大概有多少时间可用？",
    "content_body_or_beats": "把成片内容或每一段实际拍到什么告诉我。",
    "explicit_non_promise": "这条明确不承诺什么？",
    "cta_contract": "这条要不要引导观众做什么？",
    "asset_publish_permission": "这些素材可以公开发布吗？",
}


def _known_context(call):
    text = call or ""
    for key, lead in (("expected_change", "你希望观众看完明白的方向，我已经记住了"),
                      ("audience_problem", "你说的受众困扰，我会继续沿用"),
                      ("facts_registered", "已经确认的内容事实，我会按原样保留")):
        if key in text:
            return lead + "。"
    return "你已经提供的信息我会继续沿用。"


def main(status, note, missing, entry_resolved, envelope_hash, capability_call):
    miss = missing or []
    ask_key = miss[0] if miss else ""
    ask_one = QUESTION_MAP.get(ask_key) or "还需要确认一件事，才能继续。"
    ret = {
        "return_id": "M4-RET-%s-%s" % (CAPABILITY, (envelope_hash or "0" * 8)[:8]),
        "source": CAPABILITY, "highest_damaged_layer": LAYER,
        "precise_gap": "；".join(miss) if miss else (note or "未指明"),
        "affected_objects": ["仅本次 %s 调用及其真实依赖分支" % CAPABILITY],
        "proposed_disposition": "ESCALATE", "needs_user_decision": True,
        "downstream_stale": ["仅真实依赖本次 %s 结论的下游项" % CAPABILITY],
        "parse_status": "OK",
    }
    # The structure varies with known context and the real gap; it has no
    # status words and never claims unrelated work continued.
    user_text = "%s\n\n还想确认一件事：%s\n\n确认后，我就按这个方向继续。" % (_known_context(capability_call), ask_one)
    leaked = [k for k in QUESTION_MAP if k in user_text]
    return {"returns_json": json.dumps([ret], ensure_ascii=False),
            "user_delivery_leaks": leaked, "return_status": "COMPONENT_RETURN",
            "branch_result": "INPUT_INSUFFICIENT", "is_task_terminal_state": "false",
            "triggers_downstream_invalidation": "false",
            "single_most_discriminating_question": ask_one, "user_delivery": user_text,
            "fabricated_artifact_produced": "false", "downstream_invoked": "false"}
'''


def configure(mod):
    mod.CAPABILITIES = copy.deepcopy(mod.CAPABILITIES)
    for cap in mod.CAPABILITIES:
        cap["out_file"] = cap["out_file"].replace("v1_3_TEST", "v1_4_HUMAN_DELIVERY")
    mod.CAP_BY_KEY = {c["key"]: c for c in mod.CAPABILITIES}
    mod.COMPONENT_RETURN_CODE = NEW_COMPONENT_RETURN
    mod.USER_PROMPT_TMPL = mod.USER_PROMPT_TMPL.replace(
        "status: READY | NEEDS_DECISION | BLOCKED_LOCAL\n", ""
    ).replace(
        "- `objective.goal_family`（**只读继承，你无权改写**）：{{{{#envelope_check.goal_family#}}}}",
        "- `objective.goal_family`（**只读继承，你无权改写**）：{{{{#envelope_check.goal_family#}}}}\n"
        "- 用户若明确写出内容数量，必须按该数量交付；想扩展时只能作为清楚标出的可选建议。"
    )
    return mod


def build_all() -> int:
    mod = configure(load())
    for cap in mod.CAPABILITIES:
        dsl, _ = mod.build_capability_app(cap)
        path = os.path.join(cap["out_dir"], cap["out_file"])
        mod._dump(path, dsl)
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(build_all())
