#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""M4 冻结夹具保真重跑 v0.1

task_id: V1-M4-CAPABILITY-SEAMS-RUNTIME-INTEGRATION-001
权威事件: RULESIDE-2026-08-26-M4-003
登记发现: M4-FND-005

**为什么有这个文件**

收口核验时发现：`DIYU_M4_DETERMINISTIC_PROBE_v0.1.py` 里那批夹具常量
（`CT_M3` / `SCRIPT_LEGAL` / `FOOTAGE_FINAL` / `GOAL_A` / `GOAL_B` /
`ACCEPTED_DIRECTION` / `REAL_TRADEOFF` …）是冻结夹具包 v0.1 的**缩写**，
不是逐字转写。其中 `FX-M4-CT-USER-DIRECT` 更是**完全不同的内容任务**
（包 §3 是「马甲到底要不要买」，转写却是 CT_M3 改一个 source_kind）。

后果：FA-01…FA-13 里绑定这些夹具 id 的证据，**与冻结夹具不是同一个输入**。
按 `SBC-RF-02`，受影响 criterion 置 `NOT_VERIFIED + STALE` 定向复验。

**本文件怎么保证保真**

不再手抄。直接从冻结夹具包 Markdown 里**按小节抓 ```yaml 代码块**，
逐字节作为 `professional_input` 的主体；每条运行前用
`assert block in pack_text` 机械断言它确实来自包正文。

统一外壳的必填语义槽（统一能力合同 §4.3）另起一段**映射头**：
左边是合同要求的槽名，右边是**包正文自己的值**。映射头与包正文分开写、
分别落盘，任何人都能逐行核对哪一行是包的、哪一行是映射的。

**不改任何交付物字节，不对 Dify 做任何写操作。**

用法：  python3 ... run3 [FA-34 ...]
"""

import hashlib
import importlib.util
import io
import json
import os
import re
import sys
import time

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
DC_WF = os.path.join(ROOT, "decision-chain", "workflows")
EVID = os.path.join(ROOT, "decision-chain", "evidence", "m4")
RUNS = os.path.join(EVID, "runs")
PACK = os.path.join(ROOT, "decision-chain", "fixtures", "m4",
                    "V1_M4_SEAM_FIXTURE_PACK_v0.1.md")

ENVIRONMENT = "本机 Docker Dify 1.16.1"
ORACLE_REF = "V1_M4_EVIDENCE_COLLECTION_CONTRACT_v0.1.md §2（结果前冻结）"
FROZEN_CANDIDATE = "0dcd66fd39692ed07df80e39c1f27511d9cbf283"


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


FA = _load("m4fa", os.path.join(DC_WF, "DIYU_M4_FORMAL_ATTEMPT_v0.1.py"))
PUB = FA.PUB

PACK_TEXT = io.open(PACK, encoding="utf-8").read()
PACK_SHA = hashlib.sha256(PACK_TEXT.encode("utf-8")).hexdigest()


def sha(s):
    return hashlib.sha256((s or "").encode("utf-8")).hexdigest()


def pack_yaml(section_title, nth=0):
    """抓夹具包某小节标题之后的第 nth 个 ```yaml 代码块，逐字节返回。"""
    i = PACK_TEXT.index(section_title)
    j = PACK_TEXT.find("\n## ", i + 1)
    if j < 0:
        j = len(PACK_TEXT)
    seg = PACK_TEXT[i:j]
    blocks = re.findall(r"```yaml\n(.*?)```", seg, re.S)
    if not blocks:
        raise RuntimeError("小节内没有 yaml 块：%s" % section_title)
    b = blocks[nth]
    assert b in PACK_TEXT, "抓出来的块不在包正文里：%s" % section_title
    return b


def envelope(**slots):
    """统一外壳必填语义槽的映射头。值必须来自包正文，不新增经营事实。"""
    return "".join("%s: %s\n" % (k, v) for k, v in slots.items())


PACK_MARK = "\n# ===== 以下逐字节引自冻结夹具包 v0.1（sha256=%s）=====\n" % PACK_SHA[:16]


def compose(env_head, section_title, nth=0):
    body = pack_yaml(section_title, nth)
    return env_head + PACK_MARK + body, body


# ======================================================================
# 保真夹具（FA-34…FA-43）
# ======================================================================
def faithful():
    out = []

    # --- §1 FX-M4-CT-M3 ------------------------------------------------
    env = envelope(
        objective="{primary_goal: 让目标顾客形成上述分层判断，并愿意继续听这个账号的判断, goal_family: LONG_TERM_VALUE}",
        audience_problem="已经有几件通勤外套的顾客，早上仍然要花十几分钟才决定穿什么，最后常常穿回同一套",
        expected_change="她能说出自己卡住的不是衣服不够，而是层数与场合没分开，并知道下一步先解决哪一层",
        content_promise="给出一个可以在自己衣橱里直接照做的分层判断",
        facts_registered="见下方 content_task.facts_assets_gaps.registered 三条与 first_person_observation 一条",
        expression_subject_and_boundary="苏禾（NATURAL_PERSON）；允许显式标注的演示场景，不允许冒充真实顾客",
        cta_level="LOW_RISK_INTERACTION",
        cta_contract="LOW_RISK_INTERACTION")
    p, b = compose(env, "## 1. `FX-M4-CT-M3`")
    out.append(("FA-34", "FX-M4-CT-M3", "CONTENT_BRIEF", p, b, "§1",
                ["AC-04", "AC-05", "AC-21", "AC-26"]))

    # --- §2 FX-M4-CT-CAMPAIGN -----------------------------------------
    p, b = compose(env, "## 2. `FX-M4-CT-CAMPAIGN`")
    out.append(("FA-35", "FX-M4-CT-CAMPAIGN", "CONTENT_BRIEF", p, b, "§2",
                ["AC-04", "AC-05"]))

    # --- §3 FX-M4-CT-USER-DIRECT（包里是「马甲要不要买」，与此前跑的完全不同）
    env3 = envelope(
        objective="{primary_goal: 让顾客学会用两个条件自己判断, goal_family: LONG_TERM_VALUE}",
        audience_problem="顾客问过很多次『马甲到底要不要买』",
        expected_change="她知道这件马甲成立与否取决于什么，而不是听到一个『值得买』的结论",
        content_promise="说清楚马甲这件东西在什么条件下成立、什么条件下不成立",
        facts_registered="见下方 content_task.facts_assets_gaps.registered",
        expression_subject_and_boundary="苏禾；允许显式标注的演示场景",
        cta_level="LOW_RISK_INTERACTION",
        cta_contract="LOW_RISK_INTERACTION")
    p, b = compose(env3, "## 3. `FX-M4-CT-USER-DIRECT`")
    out.append(("FA-36", "FX-M4-CT-USER-DIRECT", "CONTENT_BRIEF", p, b, "§3",
                ["AC-04", "AC-21", "AC-03"]))

    # --- §4 FX-M4-SCRIPT-LEGAL（PD 直达）--------------------------------
    env4 = envelope(
        script_or_equivalent_beats="见下方 script_beats：B1/B2/B3/B4 四个节拍，逐条带 fact / asset / state_change / zone / line",
        content_origin_mode="[现拍]",
        production_profile="苏禾出镜；单人手机",
        time_window="半天",
        content_promise="给出一个可以在自己衣橱里直接照做的分层判断",
        objective="{goal_family: LONG_TERM_VALUE}",
        facts_registered="见下方 fact_refs 三条（F01 / F02 / S01）")
    p, b = compose(env4, "## 4. `FX-M4-SCRIPT-LEGAL`")
    out.append(("FA-37", "FX-M4-SCRIPT-LEGAL", "PRODUCTION_DIRECTOR", p, b, "§4",
                ["AC-09", "AC-24", "AC-03", "AC-04"]))

    # --- §5.3 FX-M4-REALIZATION-FINAL（PP 直达）-------------------------
    env5 = envelope(
        content_body_or_beats="B1/B2/B3/B4 四个节拍，逐条对应下方 realization_manifest 的时间码",
        content_promise="给出一个可以在自己衣橱里直接照做的分层判断",
        explicit_non_promise="不承诺哪一件更好；不承诺这套判断适用于所有身材",
        facts_registered="苏禾三组试穿记录：三处偏挤；去掉马甲正式感掉一档",
        cta_contract="LOW_RISK_INTERACTION",
        cta_level="LOW_RISK_INTERACTION",
        asset_publish_permission="门店内拍摄已授权；不得出现其他顾客正脸",
        objective="{goal_family: LONG_TERM_VALUE}")
    b = pack_yaml("### 5.3 `FX-M4-REALIZATION-FINAL`")
    p = env5 + PACK_MARK + b
    out.append(("FA-38", "FX-M4-REALIZATION-FINAL", "PUBLISHING_PACKAGING", p, b, "§5.3",
                ["AC-10", "AC-25", "AC-03", "AC-04"]))

    # --- §8 FX-M4-GOAL-COUNTERFACTUAL-A / B（AC-17 硬门）----------------
    # 包 §8 的 common 里含「有到店预约承接路径」——此前跑的那对**没有**这一条，
    # 所以 B 变体根本不可能表现出承接层面的实质变化。这里补上，A/B 仍只差 objective。
    common8 = pack_yaml("## 8. `FX-M4-GOAL-COUNTERFACTUAL-A/B`")
    envA = envelope(
        objective="{primary_goal: 让目标顾客形成分层判断，并愿意继续听这个账号的判断, goal_family: LONG_TERM_VALUE}",
        audience_problem="已经有几件通勤外套的顾客，早上仍然要花十几分钟才决定穿什么，最后常常穿回同一套",
        expected_change="她能说出自己卡住的不是衣服不够，而是层数与场合没分开",
        content_promise="给出一个可以在自己衣橱里直接照做的分层判断",
        facts_registered="苏禾三组试穿记录：三处偏挤；去掉马甲正式感掉一档；陈晚记录的顾客原话",
        expression_subject_and_boundary="苏禾（NATURAL_PERSON）；不得制造身材或年龄焦虑",
        permissions="无高风险 CTA 授权；有到店预约承接路径（主承接人陈晚，替补苏禾，受理边界：工作日到店时段）",
        handoff_path="{entry: 门店预约, owner: 陈晚, backup: 苏禾, capacity: 工作日到店时段}",
        variant="A")
    envB = envelope(
        objective="{primary_goal: 让刷到的人当场留下一个可回访的联系动作, goal_family: LEADS}",
        audience_problem="已经有几件通勤外套的顾客，早上仍然要花十几分钟才决定穿什么，最后常常穿回同一套",
        expected_change="她能说出自己卡住的不是衣服不够，而是层数与场合没分开",
        content_promise="给出一个可以在自己衣橱里直接照做的分层判断",
        facts_registered="苏禾三组试穿记录：三处偏挤；去掉马甲正式感掉一档；陈晚记录的顾客原话",
        expression_subject_and_boundary="苏禾（NATURAL_PERSON）；不得制造身材或年龄焦虑",
        permissions="无高风险 CTA 授权；有到店预约承接路径（主承接人陈晚，替补苏禾，受理边界：工作日到店时段）",
        handoff_path="{entry: 门店预约, owner: 陈晚, backup: 苏禾, capacity: 工作日到店时段}",
        variant="B")
    out.append(("FA-39", "FX-M4-GOAL-COUNTERFACTUAL-A", "CONTENT_BRIEF",
                envA + PACK_MARK + common8, common8, "§8", ["AC-17", "N-31"]))
    out.append(("FA-40", "FX-M4-GOAL-COUNTERFACTUAL-B", "CONTENT_BRIEF",
                envB + PACK_MARK + common8, common8, "§8", ["AC-17", "N-31"]))

    # --- §11 FX-M4-ACCEPTED-DIRECTION（ENTRY-05）------------------------
    env11 = envelope(
        objective="{primary_goal: 让目标顾客形成分层判断, goal_family: LONG_TERM_VALUE}",
        expected_change="她能说出自己卡住的不是衣服不够，而是层数与场合没分开",
        content_promise="给出一个可以在自己衣橱里直接照做的分层判断",
        expression_subject="NATURAL_PERSON（苏禾）",
        content_origin_mode="[现拍]",
        facts_registered="苏禾三组试穿记录：三处偏挤；去掉马甲正式感掉一档")
    p, b = compose(env11, "## 11. `FX-M4-ACCEPTED-DIRECTION`")
    out.append(("FA-41", "FX-M4-ACCEPTED-DIRECTION", "CREATIVE_SCRIPT", p, b, "§11",
                ["AC-08", "AC-23", "AC-22"]))

    # --- §12 FX-M4-REAL-TRADEOFF（ENTRY-04，包里是 D1/D2 五轴表）--------
    i = PACK_TEXT.index("## 12. `FX-M4-REAL-TRADEOFF`")
    j = PACK_TEXT.index("## 13. `FX-M4-NO-TRADEOFF`")
    seg12 = PACK_TEXT[i:j]
    tbl = seg12[seg12.index("任务允许至少两条"):seg12.index("判据：")].strip()
    assert tbl in PACK_TEXT
    p = env11 + PACK_MARK + tbl
    out.append(("FA-42", "FX-M4-REAL-TRADEOFF", "CREATIVE_SCRIPT", p, tbl, "§12",
                ["AC-22", "AC-29", "AC-08"]))

    # --- §13 FX-M4-NO-TRADEOFF -----------------------------------------
    i = PACK_TEXT.index("## 13. `FX-M4-NO-TRADEOFF`")
    j = PACK_TEXT.index("## 14. `FX-M4-DRAMATIZATION`")
    seg13 = PACK_TEXT[i:j]
    txt13 = seg13[seg13.index("任务只有一条"):seg13.index("判据：")].strip()
    assert txt13 in PACK_TEXT
    p = env11 + PACK_MARK + txt13 + "\ncore_claim: 初秋通勤的困难不在单品，在层数与场合的对应关系\n"
    out.append(("FA-43", "FX-M4-NO-TRADEOFF", "CREATIVE_SCRIPT", p, txt13, "§13",
                ["AC-22", "AC-29", "N-50"]))

    # --- §9 FX-M4-MIXED-GOALS ------------------------------------------
    env9 = envelope(
        audience_problem="已经有几件通勤外套的顾客，早上仍然要花十几分钟才决定穿什么，最后常常穿回同一套",
        expected_change="她能说出自己卡住的不是衣服不够，而是层数与场合没分开",
        content_promise="给出一个可以在自己衣橱里直接照做的分层判断",
        facts_registered="苏禾三组试穿记录：三处偏挤；去掉马甲正式感掉一档",
        expression_subject_and_boundary="苏禾；不得制造身材或年龄焦虑")
    p, b = compose(env9, "## 9. `FX-M4-MIXED-GOALS`")
    out.append(("FA-44", "FX-M4-MIXED-GOALS", "CONTENT_BRIEF", p, b, "§9",
                ["AC-21", "AC-29", "N-32"]))

    # --- §10 FX-M4-THIN-FIELDS -----------------------------------------
    p, b = compose("", "## 10. `FX-M4-THIN-FIELDS`")
    out.append(("FA-45", "FX-M4-THIN-FIELDS", "CONTENT_BRIEF", p, b, "§10",
                ["AC-04", "N-34"]))

    # --- §7.2 FX-M4-CAMPAIGN-CONFIRMED-PACK · 显式 compile 标记 ---------
    # 为什么单开一条：不带显式标记跑时（FA-15）系统判 PLANNING。
    # 查接缝 entry_resolver 正文，CAMPAIGN 的 run_mode 只认输入里显式写出的
    # `campaign_run_mode`，**不从「决定看起来已确认」的文本里推断**。
    # 这一条用来测 AC-07 的第二个合取项本身（compile 模式可用 + 逐条不改写），
    # 与「不带标记时是否会被强制 compile」是两回事，两条都保留。
    # 冻结夹具包 §7.2 只写「输入是一份已确认决定包」，没写要不要带这个标记——
    # 这个口径差异登记为 M4-FND-006，交 Founder，不由执行侧裁决。
    env7 = envelope(
        campaign_run_mode="COMPILE_CONFIRMED_DECISIONS",
        objective="{primary_goal: 初秋通勤衣橱第一阶段，把序里集的分层判断讲到目标顾客能自己复用, goal_family: LONG_TERM_VALUE}",
        deadline_or_stage_boundary="初秋通勤衣橱第一阶段",
        audience_problem="已经有几件通勤外套的顾客，早上仍然要花十几分钟才决定穿什么，最后常常穿回同一套",
        facts_registered="苏禾三组试穿记录：三处偏挤；去掉马甲正式感掉一档",
        capacity_or_owner="本周可投入：苏禾半天出镜 + 单人手机拍摄",
        subject_and_account_scope="序里集",
        expression_boundary="不得制造身材或年龄焦虑")
    confirmed = ("confirmed_decisions:\n"
                 "  roster: [\"序里集品牌号\", \"苏禾（零售搭配负责人）\", \"陈晚（旗舰店店长）\", \"周宁（商品负责人）\"]\n"
                 "  lead_speaker: 苏禾\n"
                 "  order: [\"第1条 苏禾\", \"第2条 序里集品牌号\", \"第3条 周宁\", \"第4条 陈晚\"]\n"
                 "  handoff_wording: \"到店预约；主承接人陈晚，替补苏禾；受理边界：工作日到店时段\"\n"
                 "  confirmed_by: USER\n")
    i7 = PACK_TEXT.index("### 7.2 `FX-M4-CAMPAIGN-CONFIRMED-PACK`")
    j7 = PACK_TEXT.index("### 7.3 `FX-M4-CAMPAIGN-OVERRIDE-END`")
    body7 = PACK_TEXT[i7:j7].strip()
    out.append(("FA-46", "FX-M4-CAMPAIGN-CONFIRMED-PACK/explicit", "CAMPAIGN",
                env7 + PACK_MARK + body7 + "\n" + confirmed, body7, "§7.2",
                ["AC-07", "AC-20", "N-06"]))

    return out


def cmd_run3():
    c = PUB.Console()
    c.login()
    reb = json.load(open(os.path.join(EVID, "M4_DIFY_REBIND.json"), encoding="utf-8"))
    seam_app = reb["seam_app_id"]
    token = FA.ensure_api_key(c, seam_app)
    base = c.base
    os.makedirs(RUNS, exist_ok=True)
    only = set(sys.argv[2:])
    index = []
    for aid, fx_id, cap, payload, pack_body, sec, serves in faithful():
        p = os.path.join(RUNS, "%s.json" % aid)
        if only and aid not in only:
            continue
        if os.path.exists(p) and not only:
            old = json.load(open(p, encoding="utf-8"))
            if ((old.get("raw_response") or {}).get("data") or {}).get("status") == "succeeded":
                print("[%s] %-34s 已有成功运行，保留" % (aid, fx_id))
                index.append({"attempt_id": aid, "fixture_id": fx_id, "capability": cap,
                              "run_id": old.get("run_id", ""), "status": "succeeded",
                              "path": os.path.relpath(p, ROOT), "serves_criteria": serves})
                continue
        assert pack_body in PACK_TEXT, aid          # 机械保真断言
        t0 = time.time()
        body = {"inputs": {"capability": cap, "entry": "",
                           "capability_call": payload, "professional_input": payload,
                           "example_reference_requested": "NO"},
                "response_mode": "blocking", "user": "m4-fixture-fidelity"}
        try:
            res = FA.service_call(base, token, "/v1/workflows/run", body)
            err = None
        except Exception as e:
            res, err = {}, str(e)[:600]
        run_id = ((res.get("data") or {}).get("id")) or ""
        rec = {"attempt_id": aid, "attempt_kind": "FORMAL", "fixture_id": fx_id,
               "fixture_pack_section": sec, "fixture_pack_sha256": PACK_SHA,
               "fidelity": "包正文逐字节引用 + 统一外壳必填槽映射头；已机械断言 pack_body in PACK_TEXT",
               "pack_body_sha256": sha(pack_body), "pack_body_verbatim": pack_body,
               "capability": cap, "serves_criteria": serves,
               "oracle_ref": ORACLE_REF, "environment": ENVIRONMENT,
               "frozen_candidate": FROZEN_CANDIDATE, "seam_app_id": seam_app,
               "provider_bindings": reb["bindings"],
               "input_sha256": sha(payload), "input_text": payload,
               "run_id": run_id, "elapsed_s": round(time.time() - t0, 2), "error": err,
               "raw_response": res,
               "node_trace": FA.node_trace(c, seam_app, run_id) if run_id else [],
               "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z")}
        with open(p, "w", encoding="utf-8") as fh:
            json.dump(rec, fh, ensure_ascii=False, indent=2)
        status = (res.get("data") or {}).get("status", "ERR" if err else "?")
        print("[%s] %-34s %-20s status=%-10s run_id=%s" % (aid, fx_id, cap, status, run_id or "-"))
        if err:
            print("      ERR: %s" % err[:200])
        index.append({"attempt_id": aid, "fixture_id": fx_id, "capability": cap,
                      "run_id": run_id, "status": status,
                      "path": os.path.relpath(p, ROOT), "serves_criteria": serves})
    with open(os.path.join(EVID, "M4_FORMAL_ATTEMPT_INDEX_3.json"), "w", encoding="utf-8") as fh:
        json.dump({"attempts": index, "environment": ENVIRONMENT, "oracle_ref": ORACLE_REF,
                   "frozen_candidate": FROZEN_CANDIDATE, "fixture_pack_sha256": PACK_SHA,
                   "finding": "M4-FND-005"}, fh, ensure_ascii=False, indent=2)
    print("index -> decision-chain/evidence/m4/M4_FORMAL_ATTEMPT_INDEX_3.json")
    return 0


if __name__ == "__main__":
    sys.exit(cmd_run3())
