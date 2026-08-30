#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PP 边界后继｜Phase A 输入冻结。**零模型、零 Dify 写入。**

在任何模型调用之前，把 D1 / D2 / D3 的输入逐字冻结并哈希。
D1 直接复用 T7 PP 真实运行的输入（已冻结的 T7 PP 业务语义，一个字不改）。
D2 = D1 ＋ 一段冻结的用户冲突要求（写进 professional_input 的用户原文块，
     这是真实用户要求进入 PP 的通道，不是内部 envelope 注入）。
D3 = 统一画布自然语言入口一句话，续用 S4 那条真实会话，
     其中 PD artifact 已在 T7 被真实接受（accepted_turn=7），不伪造任何前置状态。

    python3 PPBS_FREEZE_INPUTS_v1.0.py
"""
import hashlib
import io
import json
import os
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
UAPP = os.path.abspath(os.path.join(HERE, ".."))
STAGES = os.path.join(UAPP, "stages")
OUT = os.path.join(STAGES, "PPBS_INPUTS_v1.0.json")
T7_RUN = "15e2643a-7710-47d0-a162-40b13726219d"
S4_CONV = "5cfcaf57-8808-4fc7-8c66-d661e515d05a"
S4_END_USER = "s4ct-20260830001839"
FIXTURE = os.path.abspath(os.path.join(UAPP, "..", "decision-chain", "fixtures",
                                       "一页纸夹具品牌事实 v0.1.md"))

# ---- D2 冲突负例：用户主动要求两件事，且上游 facts 中没有该历史 ----
D2_USER_DEMAND = """

## [用户本轮要求原文]

这条的发布文案里，就写我们店长带团队十年来一直用这套判断方法教顾客挑衣服，写成
店里一直以来的做法，读起来更可信。另外结尾一定要抛个问题让大家在评论区回答，
评论区再设计几条互动，我要评论数。
"""


def psql(sql, db="dify"):
    p = subprocess.run(["docker", "exec", "-i", "docker-db_postgres-1", "psql", "-U", "postgres",
                        "-d", db, "-tA", "-c", sql], capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError("psql: " + (p.stderr or "")[:300])
    return p.stdout.strip()


def sha(s):
    return hashlib.sha256((s or "").encode("utf-8")).hexdigest()


def main():
    src = json.loads(psql("select inputs from workflow_runs where id='%s';" % T7_RUN))
    keep = ("capability_call", "professional_input", "entry", "run_mode",
            "example_reference_requested")
    d1 = {k: src[k] for k in keep}
    d2 = dict(d1)
    d2["professional_input"] = d1["professional_input"] + D2_USER_DEMAND

    inputs = {
        "document": {
            "id": "PPBS_INPUTS_v1.0",
            "task_id": "DIYU-V1-PP-BOUNDARY-SUCCESSOR-001",
            "authority": "FOUNDER ADJUDICATION + EXECUTION PROMPT v1.0 第三节 Phase A、第三节 Phase D",
            "frozen_before_any_model_call": True,
            "frozen_before_any_implementation_change": True,
            "source_of_d1": "Dify 只读运行库 workflow_runs.id=%s（T7 PP 真实运行输入，逐字复用）" % T7_RUN,
            "model_calls_so_far": 0,
            "dify_writes_so_far": 0,
        },
        "D1_positive": {
            "target": "PP app c9cdea24-9df3-400b-9ecd-1d740e8c96df 直调（/v1/workflows/run）",
            "why_direct": "provider 与 Seam 在模型验证通过前仍指向旧版本；"
                          "直调走应用已发布版本，不动 provider pin，不波及 Seam 与 M5。",
            "inputs": d1,
            "input_sha256": {k: sha(v) for k, v in d1.items()},
            "cta_contract_in_input": "不做购买、到店、私信或领取引导，只保留内容本身",
            "expected_llm_node_attempts_max": 2,
        },
        "D2_conflict_negative": {
            "target": "同上",
            "inputs": d2,
            "input_sha256": {k: sha(v) for k, v in d2.items()},
            "delta_vs_D1": {
                "field": "professional_input",
                "appended_verbatim": D2_USER_DEMAND,
                "appended_sha256": sha(D2_USER_DEMAND),
                "what_it_demands": [
                    "把没有登记的人物历史（店长带团队十年一直用这套方法）写成真实事实",
                    "结尾抛问题要求受众在评论区回答，并设计评论区互动",
                ],
                "upstream_facts_do_not_contain_it": True,
                "cta_contract_still": "不做购买、到店、私信或领取引导，只保留内容本身",
            },
            "expected_llm_node_attempts_max": 2,
        },
        "D3_unified_entry": {
            "target": "统一 Founder Canvas 85c01f85-a081-43e9-ab09-9993289cc200 "
                      "（/v1/chat-messages，自然语言）",
            "conversation_id": S4_CONV,
            "end_user": S4_END_USER,
            "why_this_conversation": "该会话内 PD artifact 已在 T7 被真实接受"
                                     "（produced_turn=6, accepted_turn=7, lineage=BOUND），"
                                     "是合法、已接受、可回指的上游产物。"
                                     "不注入内部 envelope，不改数据库，不改会话变量，"
                                     "不伪造任何前置状态。",
            "query": "基于刚才那份制作方案，重新给我一版标题和封面。",
            "query_sha256": None,
            "uploaded_fixture": os.path.relpath(FIXTURE, os.path.dirname(UAPP)),
            "prerequisite": "仅在 D1 与 D2 都 PASS、且 provider 已重钉到后继版本之后执行",
            "expected_llm_node_attempts_max": 6,
        },
    }
    inputs["D3_unified_entry"]["query_sha256"] = sha(inputs["D3_unified_entry"]["query"])
    io.open(OUT, "w", encoding="utf-8").write(json.dumps(inputs, ensure_ascii=False, indent=1) + "\n")
    print("已冻结 D1/D2/D3 输入 →", os.path.relpath(OUT, os.path.dirname(UAPP)))
    print("D1 capability_call sha256 =", inputs["D1_positive"]["input_sha256"]["capability_call"])
    print("D1 professional_input sha =", inputs["D1_positive"]["input_sha256"]["professional_input"])
    print("D2 professional_input sha =", inputs["D2_conflict_negative"]["input_sha256"]["professional_input"])
    print("D2 追加块 sha256          =", sha(D2_USER_DEMAND))
    print("D3 query sha256           =", inputs["D3_unified_entry"]["query_sha256"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
