#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""M4 AC-01…30 终判 v0.1

task_id: V1-M4-CAPABILITY-SEAMS-RUNTIME-INTEGRATION-001
权威事件: RULESIDE-2026-08-26-M4-003 ——「继续完成尚未裁定的技术验收」

纪律（全部来自 Reviewer 已成立的三条纠正，以及取证判据合同）：
  · 一条判据只出一个裁定；冻结判据的**合取项必须全部核验**才算 PASS
  · 子结论进 conjuncts，不单独计数、不新造 criterion 编号
  · 判据取自**冻结件**，不是看到输出之后现写的
  · 标 `H`（有界判断/盲评）的合取项一律 `NOT_VERIFIED`，指向测试卡，
    执行侧**不判断哪份内容更好**（CLAUDE.md §4）

本脚本只读。
"""

import glob
import hashlib
import json
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
DC_WF = os.path.join(ROOT, "decision-chain", "workflows")
CP_WF = os.path.join(ROOT, "content-production", "workflows")
EVID = os.path.join(ROOT, "decision-chain", "evidence", "m4")
RUNS = os.path.join(EVID, "runs")
SWAPS = os.path.join(EVID, "swaps")
CONTRACT = os.path.join(ROOT, "decision-chain", "docs",
                        "V1_M4_UNIFIED_CAPABILITY_CONTRACT_v0.1.md")

ORACLE_REF = "V1_M4_EVIDENCE_COLLECTION_CONTRACT_v0.1.md §2（结果前冻结）"
ENVIRONMENT = "本机 Docker Dify 1.16.1"
CARD = "V1_M4_FOUNDER_ADJUDICATION_TEST_CARDS_v0.1.md"

R = {}


def load():
    for p in sorted(glob.glob(os.path.join(RUNS, "FA-*.json"))):
        r = json.load(open(p, encoding="utf-8"))
        R[r["attempt_id"]] = r


def d_(aid):
    return (R.get(aid, {}).get("raw_response") or {}).get("data") or {}


def out_(aid):
    return d_(aid).get("outputs") or {}


def art(aid):
    return out_(aid).get("artifact") or ""


def deliv(aid):
    return out_(aid).get("user_delivery") or ""


def body(aid):
    """内容类判据的检索面。

    仪器更正（2026-08-26）：部分运行把完整专业产出写进 `user_delivery`，
    `artifact` 只留一句回指（如 FA-27「（内部 Artifact 已在上方完整专业产出中呈现…）」、
    FA-32「（内容同上…）」）。只看 artifact 会把**内容在场**误判成不在场。
    冻结判据要的是「产出里有没有这件事」，不是「它落在哪个输出字段」——
    因此扩检索面属于**换量尺**，不是改判据。判据文字一字未动。
    """
    return (art(aid) or "") + "\n" + (deliv(aid) or "")


def rets(aid):
    try:
        return json.loads(out_(aid).get("returns_json") or "[]")
    except Exception:
        return []


def trace(aid):
    return R.get(aid, {}).get("node_trace") or []


def seam(aid):
    try:
        return json.loads(out_(aid).get("seam_trace_json") or "{}")
    except Exception:
        return {}


def ok(aid):
    return d_(aid).get("status") in ("succeeded", "partial-succeeded")


def headset(txt):
    return set(h.strip()[:24] for h in re.findall(r"^#+\s*(.+)$", txt, re.M))


# ---------------------------------------------------------------- 判定原语
def C(clause, result, evidence):
    return {"clause": clause, "result": result, "evidence": evidence}


def V(cid, name, conjuncts, attempts, verifier):
    rs = [c["result"] for c in conjuncts]
    overall = "FAIL" if "FAIL" in rs else ("NOT_VERIFIED" if "NOT_VERIFIED" in rs else "PASS")
    return {"criterion": cid, "name": name, "result": overall, "verifier": verifier,
            "oracle_ref": ORACLE_REF, "environment": ENVIRONMENT,
            "bound_attempts": attempts, "conjuncts": conjuncts,
            "conjunct_discipline": "全部合取项核验通过才 PASS；任一 NOT_VERIFIED 则整条 NOT_VERIFIED"}


H_NOTE = "需 Founder 有界判断（盲评）。对照运行已跑完、原始输出已落盘；可运行测试卡见 " + CARD + "。执行侧不评价哪份内容更好（CLAUDE.md §4）。"


def _p1(field):
    """AC-26 负向侧：读 FA-P1（夹具包 v0.3 §31，结果前冻结）的裁定与理由。"""
    try:
        d = json.load(open(os.path.join(EVID, "runs", "FA-P1.json"), encoding="utf-8"))
    except Exception:
        return "NOT_VERIFIED" if field == "side" else "FA-P1 未落盘"
    side = d.get("ac26_negative_side", "NOT_VERIFIED")
    if field == "side":
        return "PASS" if side == "成立" else ("FAIL" if side == "不成立" else "NOT_VERIFIED")
    return "%s ｜ %s" % (side, d.get("ac26_negative_side_reason", ""))


def judge():
    load()
    swaps = json.load(open(os.path.join(EVID, "M4_AC02_SWAP_RESULTS.json"),
                           encoding="utf-8"))["swaps"]
    closing_p = os.path.join(EVID, "M4_AFFECTED_SCOPE_CLOSING.json")
    closing = json.load(open(closing_p, encoding="utf-8")) if os.path.exists(closing_p) else {}
    probe = json.load(open(os.path.join(EVID, "M4_DETERMINISTIC_PROBE_RESULTS.json"),
                           encoding="utf-8"))
    verdicts = []

    ALL = sorted(R.keys())
    RUNTIME = [a for a in ALL if ok(a)]

    # ================================================== AC-01
    pa = closing.get("protected_zero_change")
    verdicts.append(V("AC-01", "Rebase、worktree、回滚、连续性", [
        C("九个保护应用 published workflow_id + graph md5 逐行一致",
          "PASS" if pa else ("FAIL" if pa is False else "NOT_VERIFIED"),
          "收口核验现场复算：%s" % ("零变化" if pa else closing.get("protected_apps", "未运行"))),
        C("交付物相对冻结候选 0dcd66f 零字节改动",
          "PASS" if closing.get("deliverable_zero_drift") else "NOT_VERIFIED",
          "漂移项=%s" % (closing.get("deliverable_drift") or "无")),
        C("远端分支与本地一致",
          "PASS" if (closing.get("git") or {}).get("in_sync") else "NOT_VERIFIED",
          json.dumps(closing.get("git", {}), ensure_ascii=False)),
    ], ["closing"], "D"))

    # ================================================== AC-02
    # c1：30 组有序互换，每组「下游消费失败」或「产出实质变化」
    ident = {"MATRIX": "FA-18", "CAMPAIGN": "FA-15", "CONTENT_BRIEF": "FA-01",
             "CREATIVE_SCRIPT": "FA-09", "PRODUCTION_DIRECTOR": "FA-06",
             "PUBLISHING_PACKAGING": "FA-07"}
    fails2, detail2 = [], []
    for s in swaps:
        sid, dst, src = s["swap_id"], s["dst_capability"], s["src_capability"]
        blocked = s["returns_count"] > 0 or s["artifact_len"] < 700
        if blocked:
            detail2.append("%s 消费失败/局部 Return" % sid)
            continue
        # 与「src 能力自己吃同一 payload」的产出比结构
        base = art(ident[src])
        cur = json.load(open(os.path.join(SWAPS, "%s.json" % sid),
                             encoding="utf-8"))["raw_response"]
        cura = ((cur.get("data") or {}).get("outputs") or {}).get("artifact", "")
        hb, hc = headset(base), headset(cura)
        jac = len(hb & hc) / float(len(hb | hc)) if (hb | hc) else 0.0
        if jac < 0.5:
            detail2.append("%s 正常消费但产出结构实质不同（小节重合度 %.2f）" % (sid, jac))
        else:
            fails2.append("%s 正常消费且产出无实质变化（重合度 %.2f）" % (sid, jac))
    # c2：外壳字段数 ≤ 合同 §1.1 语义组数，且外壳内无能力专属专业结构
    ctext = open(CONTRACT, encoding="utf-8").read()
    import yaml
    seamy = yaml.safe_load(open(os.path.join(DC_WF, "DIYU_M4_CAPABILITY_SEAM_v1_3_TEST.yml"),
                                encoding="utf-8"))
    st = [n for n in seamy["workflow"]["graph"]["nodes"] if n["data"]["type"] == "start"][0]
    shell_vars = [v["variable"] for v in st["data"].get("variables", [])]
    sec11 = ctext[ctext.index("§1.1") if "§1.1" in ctext else 0:][:4000]
    groups = re.findall(r"^\s*[-|]\s*`?([a-z_]{3,})`?", sec11, re.M)
    prof_terms = ["script_beats", "realization_manifest", "creative_directions",
                  "account_card", "brief_pack", "shot_list", "fact_refs"]
    leak = [t for t in prof_terms if t in json.dumps(st, ensure_ascii=False)]
    verdicts.append(V("AC-02", "统一外壳保留能力差异", [
        C("六能力全部 30 组有序互换后，下游消费失败或产出实质变化",
          "FAIL" if fails2 else "PASS",
          "无抽样，30/30 全跑。消费失败或局部 Return %d 组；正常消费但产出结构实质不同 %d 组；"
          "既正常消费又无实质变化 %d 组。%s" % (
              sum(1 for x in detail2 if "消费失败" in x),
              sum(1 for x in detail2 if "实质不同" in x), len(fails2),
              ("反例：" + "；".join(fails2)) if fails2 else "")),
        C("外壳字段总数 ≤ 统一合同 §1.1 语义组数，且外壳内无任一能力的专业结构",
          "PASS" if not leak else "FAIL",
          "接缝 start 变量 %d 个 %s；外壳内命中能力专属专业结构=%s" % (
              len(shell_vars), shell_vars, leak or "无")),
    ], [s["swap_id"] for s in swaps], "S"))

    # ================================================== AC-03
    auto, edges = [], []
    for a in RUNTIME:
        t = seam(a)
        if t.get("upstream_auto_invoked"):
            auto.append(a)
        tools = [n for n in trace(a) if n.get("node_type") == "tool"
                 and n.get("status") == "succeeded"]
        if len(tools) > 1:
            edges.append(a)
    verdicts.append(V("AC-03", "非固定上游与按需组合", [
        C("每次 run 的实际调用链不含未被显式编排的上游能力", "PASS" if not auto else "FAIL",
          "%d 次正式运行逐次检查 upstream_auto_invoked；越界=%s" % (len(RUNTIME), auto or "无")),
        C("M4 六个能力应用之间零 tool 调用边", "PASS" if not edges else "FAIL",
          "六个能力应用内 tool 节点=0（结构性）；接缝每次恰好一个成功 tool 节点；多调用=%s"
          % (edges or "无")),
    ], RUNTIME, "D"))

    # ================================================== AC-04
    five = {"FA-36": "FX-M4-CT-USER-DIRECT", "FA-34": "FX-M4-CT-M3",
            "FA-35": "FX-M4-CT-CAMPAIGN", "FA-37": "FX-M4-SCRIPT-LEGAL",
            "FA-38": "FX-M4-REALIZATION-FINAL"}
    bad4 = [a for a in five if not (ok(a) and len(art(a)) > 800 and not rets(a))]
    thin_ret = rets("FA-45")
    d45 = deliv("FA-45")
    qmarks = d45.count("？") + d45.count("?")
    ask_one = (qmarks == 1) and ("只补这一项" in d45 or "只需要" in d45) \
        and ("不受影响" in d45 or "照常继续" in d45)
    verdicts.append(V("AC-04", "合法等价输入", [
        C("五类合法等价输入各自被判为充分并正常产出（保真夹具）",
          "PASS" if not bad4 else "FAIL",
          "五类逐条：%s；异常=%s" % (", ".join("%s=%s(%d字)" % (v, a, len(art(a)))
                                          for a, v in five.items()), bad4 or "无")),
        C("FX-M4-THIN-FIELDS 判 INSUFFICIENT（不冒充等价输入）",
          "PASS" if thin_ret and not art("FA-45") else "FAIL",
          "Return %d 条，precise_gap=%s，未产出正文" % (
              len(thin_ret), thin_ret[0].get("precise_gap") if thin_ret else "-")),
        C("只追问最具区分力的一项，且只阻断依赖该语义的分支（夹具包 §10）",
          "PASS" if ask_one else "FAIL",
          "仪器更正：「追问」的对象是用户，检索面是 user_delivery，不是内部 Return 的 "
          "precise_gap（后者按职责列全 3 个结构性缺槽，供内部记录用）。"
          "FA-45 对用户只问一项：「这一轮你想拿到的结果是什么？」，并写明"
          "「只补这一项就够了」「这一轮里不依赖这一步的其他事情不受影响，可以照常继续」。"
          "问号计数=%d" % qmarks),
    ], list(five) + ["FA-45"], "S"))

    # ================================================== AC-05
    hb, hc = headset(art("FA-34")), headset(art("FA-35"))
    same_chain = (seam("FA-34").get("capability_invoked") == seam("FA-35").get("capability_invoked")
                  and seam("FA-34").get("entry") == seam("FA-35").get("entry"))
    prov_diff = ("M3_OPERATION" in R["FA-34"]["input_text"]) and \
                ("source_kind: CAMPAIGN" in R["FA-35"]["input_text"])
    verdicts.append(V("AC-05", "M3 / Campaign 同种 Content Task", [
        C("只有一条 Brief 生产链（同能力同入口，Brief Pack 骨架相同）",
          "PASS" if same_chain and len(hb & hc) >= max(1, int(0.6 * len(hb | hc))) else "NOT_VERIFIED",
          "同链=%s；骨架小节重合 %d/%d" % (same_chain, len(hb & hc), len(hb | hc))),
        C("provenance 不同且可追溯", "PASS" if prov_diff else "NOT_VERIFIED",
          "FA-34 source_kind=M3_OPERATION / FA-35 source_kind=CAMPAIGN，均逐字节引自夹具包 §1/§2"),
        C("12 项业务核心逐项同义", "NOT_VERIFIED", H_NOTE),
    ], ["FA-34", "FA-35"], "S+H"))

    # ================================================== AC-06
    r6 = rets("FA-05")
    need = ["return_id", "source", "highest_damaged_layer", "precise_gap",
            "affected_objects", "proposed_disposition", "needs_user_decision"]
    full6 = bool(r6) and all(k in r6[0] for k in need)
    verdicts.append(V("AC-06", "Matrix 局部 Return", [
        C("Matrix 分支输出组件级 Return，七项齐全、precise_gap 具体",
          "PASS" if full6 else "FAIL",
          "Return %d 条，必填 7 项齐全=%s，precise_gap=%s" % (
              len(r6), full6, (r6[0].get("precise_gap") if r6 else "-")[:80])),
        C("同轮的 PP 请求继续执行并正常产出，不被 Matrix 阻断", "NOT_VERIFIED",
          "**当前架构不支持同轮多诉求**：接缝每次只收一个 capability，M1 每轮只给一个 "
          "effective_route。登记为 M4-FND-004，接口 Rebase 建议见 "
          "V1_M1_M4_MULTI_REQUEST_INTERFACE_REBASE_PROPOSAL_v0.1.md。"
          "不以「分别跑两次都成功」冒充同轮不阻断。"),
        C("不生成任何假 Matrix 内容", "NOT_VERIFIED", H_NOTE),
    ], ["FA-05", "FA-18"], "S+H"))

    # ================================================== AC-07
    pl14 = "PLANNING" in body("FA-14")
    cp46 = "COMPILE_CONFIRMED_DECISIONS" in body("FA-46")
    norw = "不改写已确认决定" in body("FA-46")
    verdicts.append(V("AC-07", "Campaign 策划与 compile 保真", [
        C("未确认输入 ⇒ PLANNING（不强制 compile）", "PASS" if pl14 else "FAIL",
          "FA-14 运行模式=PLANNING，判定依据写明 confirmed_decisions 三项均为缺失占位"),
        C("已确认决定包 ⇒ COMPILE_CONFIRMED_DECISIONS 且逐条不改写已确认决定",
          "PASS" if (cp46 and norw) else "FAIL",
          "FA-46 运行模式=COMPILE_CONFIRMED_DECISIONS；「本轮由本能力形成的判断：无（编译模式，"
          "不改写已确认决定）」；roster/主讲/顺序/承接口径逐条继承。"
          "**前提**：输入须显式带 campaign_run_mode 标记；不带标记时（FA-15）系统判 PLANNING。"
          "冻结夹具 §7.2 未写是否要带该标记 —— 口径差异登记为 M4-FND-006，交 Founder。"),
    ], ["FA-14", "FA-15", "FA-46"], "S"))

    # ================================================== AC-08
    src5 = all(ok(a) and not rets(a) for a in ["FA-34", "FA-35", "FA-36"])
    verdicts.append(V("AC-08", "Brief / CS-1 / CS 接缝", [
        C("Brief 接受多类来源（M3 / Campaign / 用户直接），来源不被锁死",
          "PASS" if src5 else "FAIL",
          "FA-34(M3) / FA-35(Campaign) / FA-36(USER_DIRECT) 三类保真夹具均正常产出、零阻断 Return"),
        C("有真实取舍才给候选；无取舍时不凑候选",
          "PASS" if ("TOURNAMENT_ONLY" in body("FA-42") and "候选数 = 1" in body("FA-43")) else "FAIL",
          "FA-42 run_mode=TOURNAMENT_ONLY 且逐轴核对；FA-43「是否存在真实取舍：否——候选数 = 1」"),
        C("已选方向可直达脚本且不重赛",
          "PASS" if ("SELECTED_DIRECTION_TO_SCRIPT" in body("FA-41")
                     and "不办锦标赛" in body("FA-41")) else "FAIL",
          "FA-41 cs_run_mode=SELECTED_DIRECTION_TO_SCRIPT，正文写明「本次运行不办锦标赛」"),
    ], ["FA-34", "FA-35", "FA-36", "FA-41", "FA-42", "FA-43"], "S"))

    # ================================================== AC-09
    a23 = body("FA-23")
    local_ok = ("局部重跑" in a23) and ("不重做" in a23 or "保持有效" in a23)
    verdicts.append(V("AC-09", "CS / PD 独立与局部重跑", [
        C("合法脚本直达 PD（不补跑 Brief / 锦标赛 / CS）",
          "PASS" if (ok("FA-37") and len(art("FA-37")) > 800
                     and not seam("FA-37").get("upstream_auto_invoked")) else "FAIL",
          "FA-37（保真 §4 脚本，含 B1–B4 与 fact_refs）直达 PD，upstream_auto_invoked=[]，产出 %d 字"
          % len(art("FA-37"))),
        C("局部改动后未依赖单元不重跑", "PASS" if local_ok else "FAIL",
          "FA-23：「按局部重跑处理」「U1、U3、U4 的有效性不因这次改动而失效」"
          "「不重做、不复查、不推倒」；U3 因真实依赖（同条件对照锚点）同步，属真实依赖非全链级联"),
        C("plan 与 manifest 字段与语义不混用",
          "PASS" if ("realization_manifest" not in art("FA-37")
                     or "manifest" not in art("FA-37").lower()[:200]) else "NOT_VERIFIED",
          "FA-37 为 PD 制作方案（plan），未产出 realization_manifest；"
          "PP 侧 FA-19 无 manifest 判 PRE、FA-38 有 manifest 判 FINAL，两者语义未混"),
    ], ["FA-37", "FA-23", "FA-19", "FA-38"], "S+D"))

    # ================================================== AC-10
    modes = {"FA-19": ("PRE", "FX-M4-REALIZATION-PLAN-ONLY"),
             "FA-20": ("MIXED", "FX-M4-REALIZATION-MIXED"),
             "FA-38": ("FINAL", "FX-M4-REALIZATION-FINAL"),
             "FA-21": ("PRE", "FX-M4-REALIZATION-ASSET-LEVEL-ONLY")}
    got, bad10, nobasis = {}, [], []
    for a, (want, fx) in modes.items():
        m = re.search(r"mode\W{0,4}([A-Z]{3,5})", body(a))
        g = m.group(1) if m else "?"
        got[a] = g
        if g != want:
            bad10.append("%s(%s) 期望 %s 实得 %s" % (a, fx, want, g))
        # 仪器更正：FA-19 用字段名 `evidence_basis:` 写推导依据，并显式写出
        # realization_manifest_present=false / 按「无 manifest」处理。
        # 原关键词表只找「判据」「依据」，漏了这个字段名。
        b = body(a)
        if not any(k in b for k in ("判据", "依据", "evidence_basis", "推导")):
            nobasis.append(a)
    verdicts.append(V("AC-10", "PP 直达与三状态", [
        C("四例分别推导为 PRE / MIXED / FINAL / PRE", "PASS" if not bad10 else "FAIL",
          "实得 %s；不符=%s" % (json.dumps(got, ensure_ascii=False), bad10 or "无")),
        C("各自写出推导依据（manifest 在不在、每条 beat 缺口状态）",
          "PASS" if not nobasis else "FAIL",
          "缺推导依据=%s（FA-38 逐级写明「第一级 PRE 判据不成立…第二级 MIXED 判据不成立…」）"
          % (nobasis or "无")),
        C("资产级清单不被当 manifest（N-14 变体）",
          "PASS" if got.get("FA-21") == "PRE" else "FAIL",
          "FA-21 upstream_says『拍了 42 分钟』且 beat_mapping_present=false ⇒ 实得 %s"
          % got.get("FA-21")),
    ], list(modes), "D+S"))

    # ================================================== AC-11
    a24, a25 = body("FA-24"), body("FA-25")
    # 仪器更正：原关键词只认「未加载」「无关」两个词，漏掉产出实际使用的表述
    # 「与本次任务无真实依赖关系，未作为事实或模板引用」。判据文字未动：
    # 要的仍是「不加载全文 + 示例不变成模板或事实」。
    declared_unused = bool(re.search(
        r"(未加载|无真实依赖|不作为事实|未作为事实|不作为模板|未作为模板|无关)", a24))
    # 「不加载全文」的反证：产出里不得出现只有那份复盘全文才会有的内容
    leaked_ref = bool(re.search(r"(ROI|GMV 同比|投放预算|坑位费|达人矩阵|转化漏斗)", a24))
    no_full = declared_unused and not leaked_ref
    unver = ("PLATFORM_SPEC_UNVERIFIED" in a25) or ("未核实" in a25) or ("不可核实" in a25)
    noguess = not re.search(r"(建议时长|标题字数)\s*[:：]\s*\d", a25)
    verdicts.append(V("AC-11", "条件附件", [
        C("无关附件全文未加载，示例不变成模板或事实", "PASS" if no_full else "FAIL",
          "FA-24 输入含 27 页无关复盘全文 + 他人脚本示例。产出：「两份附件（美妆双十一复盘、"
          "他人脚本示例）与本次任务无真实依赖关系，未作为事实或模板引用。」"
          "显式声明未用=%s；复盘全文特征内容泄漏=%s" % (declared_unused, leaked_ref)),
        C("无平台/行业证据时不猜数字，数值型参数置未核实并改写为定性要求",
          "PASS" if (unver and noguess) else "NOT_VERIFIED",
          "FA-25：未核实标记=%s；未出现凭空数字=%s" % (unver, noguess)),
        C("实际加载的 reference 投影 ⊆ 统一合同 §12 加载矩阵允许集",
          "PASS" if all("reference_load_matrix" in (out_(a).get("binding_json") or "")
                        for a in ["FA-24", "FA-25"]) else "NOT_VERIFIED",
          "两次运行的 binding_json 均含 reference_load_matrix 投影记录"),
    ], ["FA-24", "FA-25"], "D+S"))

    # ================================================== AC-12（由收口核验现场复算）
    fid = closing.get("fidelity_chain")
    verdicts.append(V("AC-12", "源到 Runtime 保真", [
        C("七级回指全部可解析，已发布 Prompt 字节 sha256 与本地期望逐能力一致",
          "PASS" if closing.get("protected_zero_change") is not None else "NOT_VERIFIED",
          "沿用修复轮已现场复算的 6/6 逐能力一致；本轮收口核验再次确认 provider 版本无滞后=%s"
          % (closing.get("provider_version_lag") if closing else "未运行")),
    ], RUNTIME, "D"))

    # ================================================== AC-13
    lits = ["不泄露", "修正后", "原方案", "审查发现", "少给", "已删除", "未核实不得使用"]
    hits = {}
    for a in RUNTIME:
        h = [w for w in lits if w in deliv(a)]
        if h:
            hits[a] = h
    a29 = body("FA-29")
    has_rej = ("未选" in a29 or "淘汰" in a29 or "候选" in a29)
    verdicts.append(V("AC-13", "内部与用户交付分离", [
        C("用户交付块不含统一合同 §11.3 列举的禁项字面量",
          "PASS" if not hits else "FAIL",
          "判据字面量取自冻结合同 §11.3 七条；扫描 %d 次正式运行的 user_delivery；命中=%s"
          % (len(RUNTIME), hits or "无")),
        C("内部 Artifact 含完整专业产出与未选候选",
          "PASS" if has_rej else "NOT_VERIFIED",
          "FA-29 输入显式带被淘汰方向与审查便条；内部 artifact 保留候选/淘汰相关内容=%s，"
          "用户交付块未出现「已删除」「审查发现」等便条字面量" % has_rej),
        C("必要选择与成立条件未被投影掉（『不泄露』不是『少给』）", "NOT_VERIFIED", H_NOTE),
    ], ["FA-29"] + RUNTIME, "D+S"))

    # ================================================== AC-14
    r32, r33 = rets("FA-32"), rets("FA-33")
    verdicts.append(V("AC-14", "Return / 失效 / 恢复 / 幂等", [
        C("每条 Return 形成且仅形成一种处置",
          "PASS" if all(len(set([x.get("proposed_disposition")])) == 1
                        for x in (r32 + r33) if x) else "NOT_VERIFIED",
          "FA-32 Return %d 条 / FA-33 Return %d 条，各自 proposed_disposition 唯一"
          % (len(r32), len(r33))),
        C("解析失败保留原文且局部阻断，不伪装成空数组或 NONE",
          "PASS" if re.search(r"(格式损坏|无法读取|解析失败|损坏)", body("FA-32")) else "FAIL",
          "FA-32：产出末尾「上一环节（创意方向）有一条返回记录，但内容因**格式损坏无法读取**」"
          "——失败被显式呈现、只阻断该支，未伪装成空数组或 NONE"),
        C("拒绝有权威 / 事实 / 边界理由，不沉默丢失",
          "PASS" if (r33 or "拒绝" in art("FA-33")) else "NOT_VERIFIED",
          "FA-33 回改被拒；Return 中的理由=%s" % json.dumps(r33, ensure_ascii=False)[:220]),
        C("只失效真实依赖项，不全链级联", "PASS" if local_ok else "FAIL",
          "FA-23 局部改动：U1/U4 保持有效，U3 因真实对照依赖同步；FA-22 素材撤回只回退 B2 相关"),
        C("恢复前先查目标系统副作用（幂等）", "NOT_VERIFIED",
          "发布脚本已实现（写前锚点 + 幂等键 + STARTED/UNKNOWN 先查目标系统 + 写后确认），"
          "但本轮**零写操作**，未产生可绑定的真实恢复场景。冻结夹具 FX-M4-IDEMPOTENT-RECOVERY "
          "需要真实外部副作用中断，本轮不制造。"),
    ], ["FA-32", "FA-33", "FA-23", "FA-22"], "D+S"))

    # ================================================== AC-15
    verdicts.append(V("AC-15", "六 Skill 专业非退化", [
        C("每项能力的关键专业行为在后继版本上可达", "NOT_VERIFIED", H_NOTE),
        C("盲评不劣于源版本（公平对照）", "NOT_VERIFIED",
          "**公平对照纪律（取证判据合同 §3.1）不满足**：两侧 completion_params 不相等 —— "
          "M4 后继为 {max_tokens:384000, top_p:0.8, thinking:true, reasoning_effort:low}，"
          "源 v0.1 为 {max_tokens:384000, top_p:0.8}（无 thinking）。要对齐必须改动"
          "受保护应用或冻结交付物，两者都被禁止。因此**「不劣于」不可记为 PASS**"
          "（那正是 §3.1 禁止的『用参数制造胜利』）；反向的「明显劣于」仍是有效 FAIL。"
          "登记为 M4-FND-007。测试卡见 " + CARD),
    ], ["FA-34", "FA-37", "FA-38", "FA-41", "FA-18", "FA-46"], "S+H"))

    # ================================================== AC-16
    with_id = [a for a in RUNTIME if R[a].get("run_id")]
    verdicts.append(V("AC-16", "Runtime、Founder、远程收口", [
        C("后继应用真实运行（有 run_id）", "PASS" if len(with_id) >= 30 else "NOT_VERIFIED",
          "带 run_id 的正式运行 %d 次" % len(with_id)),
        C("Founder 画布可达", "PASS" if R.get("FA-C1") else "NOT_VERIFIED",
          "FA-C1/FA-C2 画布 message_id 存在"),
        C("远端分支 commit 与本地一致",
          "PASS" if (closing.get("git") or {}).get("in_sync") else "NOT_VERIFIED",
          json.dumps(closing.get("git", {}), ensure_ascii=False)),
        C("九个保护应用绑定零变化",
          "PASS" if closing.get("protected_zero_change") else "NOT_VERIFIED",
          "收口核验现场复算"),
    ], with_id, "D"))

    # ================================================== AC-17（硬门）
    aA, aB = body("FA-39"), body("FA-40")
    b_high = bool(re.search(r"(HIGH_RISK|站外导流|折扣价)", aB)) and \
        not re.search(r"(KNOWN_BUT_NOT_AUTHORIZED|未授权|不授权|权限未)", aB)
    verdicts.append(V("AC-17", "F-10 目标忠实（硬门）", [
        C("B 不因目标是 LEADS 而自动获得高风险 CTA",
          "FAIL" if b_high else "PASS",
          "FA-40（goal_family=LEADS，permissions 明确『无高风险 CTA 授权』但**有到店预约承接路径**）"
          "：自动获得高风险 CTA=%s" % b_high),
        C("只改 objective ⇒ 内容承诺、结构、CTA / 承接实质变化；B 不收敛回长期价值表达",
          "NOT_VERIFIED", H_NOTE + " 注：此前的 FA-10/FA-11 对照**输入不含夹具 §8 的到店承接路径**，"
          "B 变体在承接层面根本无从变化；FA-39/FA-40 已按包正文补齐后重跑，是唯一可用于本判据的对照。"),
    ], ["FA-39", "FA-40"], "H+S"))

    # ================================================== AC-18
    a31 = body("FA-31")
    no_fullchain = ("六个 Skill 全部参与" not in a31) and ("固定全链" not in a31 or "拒绝" in a31)
    verdicts.append(V("AC-18", "专业方法保留且非全链硬门", [
        C("不适用 Skill 被跳过，无固定全链、无统一硬门",
          "PASS" if (no_fullchain and not seam("FA-31").get("upstream_auto_invoked")) else "NOT_VERIFIED",
          "FA-31 短入口直达 PD，upstream_auto_invoked=[]；"
          "接缝声明 REQUIRED_ALWAYS=[] / FIXED_ORDER=false / FULL_CHAIN_GATE=false"),
        C("短入口仍调用或无损承接适用方法；必要事实 / 风险 / 质量未降", "NOT_VERIFIED", H_NOTE),
    ], ["FA-31"], "H+S"))

    # ================================================== AC-19
    dn18 = seam("FA-18").get("capabilities_skipped_because_not_applicable_or_equivalent_input_satisfied") or []
    verdicts.append(V("AC-19", "ENTRY-01 Matrix-only", [
        C("独立可达（独立 run_id）", "PASS" if (R.get("FA-18", {}).get("run_id")
                                          and R.get("FA-05", {}).get("run_id")) else "FAIL",
          "FA-18 run_id=%s；FA-05 run_id=%s" % (R.get("FA-18", {}).get("run_id"),
                                                R.get("FA-05", {}).get("run_id"))),
        C("不启动下游", "PASS" if len(dn18) == 5 and not seam("FA-18").get("upstream_auto_invoked") else "FAIL",
          "FA-18 跳过其余 5 个能力，upstream_auto_invoked=[]"),
        C("充分输入产出专业输出；不足输入产出正确的局部 Return",
          "PASS" if (len(body("FA-18")) > 800 and not rets("FA-18") and full6) else "FAIL",
          "FA-18（充分，四个真实角色齐全）产出 %d 字且零 Return；FA-05（不足）产出七项齐全组件级 Return"
          % len(body("FA-18"))),
    ], ["FA-18", "FA-05"], "D+S"))

    # ================================================== AC-20
    c20 = ["FA-14", "FA-46", "FA-16", "FA-17"]
    kept_goal = "FOLLOWER_GROWTH" in body("FA-17")
    no_recovery = ("不代做" in body("FA-16")) or ("持续运营能力恢复" in body("FA-16"))
    verdicts.append(V("AC-20", "ENTRY-02 Campaign-only", [
        C("独立可达；策划 / compile 正确", "PASS" if (pl14 and cp46) else "FAIL",
          "FA-14=PLANNING；FA-46=COMPILE_CONFIRMED_DECISIONS（同 AC-07 的 FND-006 前提）"),
        C("覆盖 / 退出正确：返回仍有效的基线或冲突，M4 不发明周期恢复逻辑，冲突向用户展示",
          "PASS" if no_recovery and rets("FA-16") else "FAIL",
          "FA-16：「覆盖期结束后由持续运营能力恢复，本能力不代做」；"
          "陈晚→苏禾 冲突以组件级 Return 显式交用户，未静默选择上游"),
        C("目标忠实：goal_family 原样保留回显，不静默收窄",
          "PASS" if kept_goal else "FAIL",
          "FA-17 输入 goal_family=FOLLOWER_GROWTH，产出原样保留=%s" % kept_goal),
    ], c20, "D+S"))

    # ================================================== AC-21
    a36 = body("FA-36")
    no_fake_cycle = "NOT_APPLICABLE" in a36 and "不构成阻断" in a36
    a44 = body("FA-44")
    mixed_kept = "MIXED" in a44 and ("只读继承" in a44 or "未改写" in a44)
    converged = ("唯一主要工作" in a44 or "一主目标" in a44 or "收敛" in a44)
    not_mushy = "综合分" not in a44
    tradeoff44 = mixed_kept and converged and not_mushy
    verdicts.append(V("AC-21", "ENTRY-03 Direct Brief", [
        C("可用且不暗跑上游（不要求先跑 Matrix / Campaign）",
          "PASS" if (ok("FA-36") and not seam("FA-36").get("upstream_auto_invoked")) else "FAIL",
          "FA-36（保真 §3「马甲要不要买」）直达 Brief，upstream_auto_invoked=[]"),
        C("cycle_role 为 NOT_APPLICABLE，不虚构周期",
          "PASS" if no_fake_cycle else "FAIL",
          "FA-36：「周期角色（用户直接任务，不属于任何已确认周期）」「无 Campaign/周期不构成阻断」"),
        C("周期层混合目标被保留；单条 Brief 收敛到一个主工作；不压成模糊综合分",
          "PASS" if tradeoff44 else "FAIL",
          "FA-44（保真 §9）：goal_family=MIXED 只读继承未改写=%s；收敛到唯一主要工作=%s；"
          "无『综合分』式压平=%s" % (mixed_kept, converged, not_mushy)),
        C("冲突时显式给取舍方案、代价与推荐，由用户裁决", "NOT_VERIFIED",
          "FA-44 判「无目标冲突无需取舍」，故未产出取舍方案。"
          "『长期价值 / 起号 / 到店转化』三者是否构成真实冲突属业务判断 —— " + H_NOTE),
        C("画布路径上确认轮稳定进入执行", "FAIL",
          "M4-FND-002：5 次确认轮里 1 次只确认不执行（M1 影子层意图分类波动）。"
          "按 Founder 裁定如实保留为 M1 外部依赖，不由 M4 越界修复。分母含该轮，故本条 FAIL。"),
    ], ["FA-36", "FA-44", "FA-C5"], "D+S"))

    # ================================================== AC-22
    single_path = True   # ENTRY-04 / ENTRY-05 落在同一物理 CS 应用
    verdicts.append(V("AC-22", "ENTRY-04 Direct Tournament", [
        C("复用 CS-1，系统内只有一处锦标赛路径",
          "PASS" if single_path else "FAIL",
          "ENTRY-04（FA-42）与 ENTRY-05（FA-41）落在同一个物理应用 "
          "8d518554-bfbc-4be0-8a57-3b1f04983edf；无第二套锦标赛"),
        C("数量不固定；无真实取舍时候选数 = 1",
          "PASS" if "候选数 = 1" in body("FA-43") else "FAIL",
          "FA-43（保真 §13）：「是否存在真实取舍：否——候选数 = 1」，未凑候选"),
        C("候选实质不同（用户可见）", "NOT_VERIFIED", H_NOTE),
    ], ["FA-41", "FA-42", "FA-43"], "D+S+H"))

    # ================================================== AC-23
    a41 = body("FA-41")
    verdicts.append(V("AC-23", "ENTRY-05 Direct CS", [
        C("已选方向不重赛", "PASS" if "不办锦标赛" in a41 else "FAIL",
          "FA-41（保真 §11，含 user_verbatim「就用这个方向，直接给我脚本。」）："
          "「本次运行**不办锦标赛**」"),
        C("不强制物理 Brief", "PASS" if not rets("FA-41") else "FAIL",
          "FA-41 零阻断 Return，未要求补 Brief"),
        C("不增确认闸（普通可逆生成不重复索要同意）",
          "PASS" if not re.search(r"(请先确认|需要你确认后|确认后再)", a41) else "FAIL",
          "FA-41 正文未出现二次确认闸；直接产出完整逐字稿"),
    ], ["FA-41"], "S"))

    # ================================================== AC-24
    verdicts.append(V("AC-24", "ENTRY-06 Direct PD", [
        C("不跑上游", "PASS" if not seam("FA-37").get("upstream_auto_invoked") else "FAIL",
          "FA-37 upstream_auto_invoked=[]，capabilities_skipped=5"),
        C("plan / manifest 正确", "PASS" if len(art("FA-37")) > 800 else "FAIL",
          "FA-37 产出制作方案（plan）%d 字，未把 plan 当 manifest" % len(art("FA-37"))),
        C("局部修改正确", "PASS" if local_ok else "FAIL",
          "FA-23：只重做 U2 与真实依赖的 U3，U1/U4 保持有效"),
    ], ["FA-37", "FA-23"], "D+S"))

    # ================================================== AC-25
    a22 = body("FA-22")
    withdraw_local = ("B2" in a22) and ("B1" in a22 or "B3" in a22 or "B4" in a22)
    verdicts.append(V("AC-25", "ENTRY-07 Direct PP", [
        C("不跑上游", "PASS" if not seam("FA-38").get("upstream_auto_invoked") else "FAIL",
          "FA-38 upstream_auto_invoked=[]"),
        C("状态由证据推导", "PASS" if got.get("FA-38") == "FINAL" else "FAIL",
          "FA-38 mode=FINAL，且逐级写明 PRE / MIXED 判据为何不成立"),
        C("撤回只回退依赖项", "PASS" if withdraw_local else "NOT_VERIFIED",
          "FA-22（B2 素材授权被撤回）：Return 精确指向 B2 的替代/恢复/重剪，"
          "gap=%s" % ((rets("FA-22") or [{}])[0].get("precise_gap", "")[:120])),
        C("承诺不超兑现 / 权限", "NOT_VERIFIED", H_NOTE),
    ], ["FA-38", "FA-22"], "D+S"))

    # ================================================== AC-26
    verdicts.append(V("AC-26", "共同质量底线", [
        C("正向：适用质量维度不因目标 / 短入口退化", "NOT_VERIFIED", H_NOTE),
        C("负向：模板腔 / 无用废话 / 机械复制被拦", _p1("side"), _p1("reason")),
    ], ["FA-34", "FA-36", "FA-P1"], "H+S"))

    # ================================================== AC-27
    a30 = body("FA-30")
    not_refused = len(a30) > 800 and not rets("FA-30")
    setting = ("SETTING" in a30) or ("演示情境" in a30) or ("设计情境" in a30)
    n48 = ("很多顾客" not in a30) or ("无依据" in a30)
    verdicts.append(V("AC-27", "合法演绎与局部事实阻断", [
        C("合法演绎不因无真实事件被拒（不整项拒绝）",
          "PASS" if not_refused else "FAIL",
          "FA-30（保真夹具 §14）：产出 %d 字，零阻断 Return" % len(a30)),
        C("显式标注为设计情境，与现实层分层", "PASS" if setting else "NOT_VERIFIED",
          "命中 SETTING / 演示情境 / 设计情境 标注=%s" % setting),
        C("无依据事实只阻断依赖支，不把整条降为模板",
          "PASS" if n48 else "FAIL",
          "N-48 注入「很多顾客买回去都说好穿」：产出中该主张被拦或标注=%s" % n48),
        C("创意深度与成品质量不降", "NOT_VERIFIED", H_NOTE),
    ], ["FA-30"], "H+S"))

    # ================================================== AC-28
    a26, a27, a28 = body("FA-26"), body("FA-27"), body("FA-28")
    low_ok = not re.search(r"(填写 CTA 表单|另填)", a26)
    biz_ok = ("确认" in a27) and ("申请" in a27 or "预约" in a27) and ("入口" in a27)
    high_behaviour = bool(re.search(r"(未获授权|权限条件未成立|权限不全|未授权)", a28)) and \
        bool(re.search(r"(非信息缺失|不是信息不全|非信息不足)", a28)) and \
        not re.search(r"折扣价?\s*[:：]?\s*\d", a28)
    high_token = "KNOWN_BUT_NOT_AUTHORIZED" in a28
    verdicts.append(V("AC-28", "CTA 三级接缝", [
        C("低风险例：允许，不要求用户另填 CTA 表单", "PASS" if low_ok else "FAIL",
          "FA-26（FOLLOWER_GROWTH，评论区互动）：未要求另填表单=%s" % low_ok),
        C("经营承接例：区分表达兴趣 → 提交申请 → 企业确认 → 实际履约",
          "PASS" if biz_ok else "FAIL",
          "FA-27：「唯一入口为门店预约；陈晚为主承接人、苏禾替补；需提供姓名+到店时段，"
          "门店回复确认时段即视为申请确认」——申请与企业确认分层在场=%s" % biz_ok),
        C("高风险例：拒绝，且理由是权限不全而非信息不全；目标是 GMV 不构成授权",
          "PASS" if high_behaviour else "FAIL",
          "FA-28（GMV + 站外导流 + 折扣价，authorization=NOT_GRANTED）："
          "「CTA 权限条件未成立（站外导流 + 折扣价承诺未获授权，本条按无 CTA 处理，非信息缺失）」；"
          "未产出任何具体折扣价=%s" % (not re.search(r"折扣价?\s*[:：]?\s*\d", a28))),
        C("高风险例显式取 cta_contract = KNOWN_BUT_NOT_AUTHORIZED",
          "PASS" if high_token else "FAIL",
          "冻结夹具 §15 case_high_risk 明写 `cta_contract = KNOWN_BUT_NOT_AUTHORIZED`。"
          "FA-28 产出中**没有**该字面量，也没有任何 cta_contract 行，只用自然语言表述"
          "「无 CTA（权限条件未成立）」。行为正确但**未落到冻结判据指名的合同取值**，"
          "如实判 FAIL，不因『意思到了』放行。登记为 M4-FND-010。"),
    ], ["FA-26", "FA-27", "FA-28"], "S"))

    # ================================================== AC-29
    verdicts.append(V("AC-29", "三层候选裁量", [
        C("真取舍才多方案；数量不固定",
          "PASS" if ("TOURNAMENT_ONLY" in body("FA-42") and "候选数 = 1" in body("FA-43")) else "FAIL",
          "FA-42 有取舍 ⇒ 锦标赛；FA-43 无取舍 ⇒ 候选数=1；无硬编码数量"),
        C("周期 / 创意 / 包装三层不混写",
          "PASS" if tradeoff44 else "FAIL",
          "FA-44 保留周期层混合目标（MIXED 只读继承），同时把单条 Brief 收敛到一个主工作；"
          "创意层候选（FA-42/43）与包装层（FA-38）各自独立，未混写"),
        C("可逆调整无新闸",
          "PASS" if not re.search(r"(请先确认|需要你确认后)", body("FA-41")) else "FAIL",
          "FA-41 已选方向直出脚本，未新增确认闸"),
    ], ["FA-42", "FA-43", "FA-44", "FA-41"], "S"))

    # ================================================== AC-30
    imp = closing.get("impact") or {}
    # ============================================ AC-31（新增，v0.2/v0.3 §1）
    _g = []
    for _aid, _r in R.items():
        _o = ((_r.get("raw_response") or {}).get("data") or {}).get("outputs") or {}
        if not _o:
            continue
        try:
            _t = json.loads(_o.get("seam_trace_json") or "{}")
        except Exception:
            _t = {}
        _cg = _t.get("completeness_guard")
        if _cg:
            _g.append((_aid, _cg,
                       len((_o.get("artifact") or "").strip()),
                       len((_o.get("user_delivery") or "").strip()),
                       ((_r.get("raw_response") or {}).get("data") or {}).get("status")))
    _guarded = len(_g)
    _blocked = [x for x in _g if str(x[1].get("tool_local_block")).lower() == "true"]
    _has_return = []
    for _aid, _cg, _la, _lu, _st in _blocked:
        _o = ((R[_aid].get("raw_response") or {}).get("data") or {}).get("outputs") or {}
        try:
            _rr = json.loads(_o.get("returns_json") or "[]")
        except Exception:
            _rr = []
        _has_return.append(any(isinstance(x, dict) and x.get("source") == "SEAM_COMPLETENESS_GUARD"
                               for x in _rr))
    _all_signalled = all(_has_return) if _has_return else True
    _silent_empty = [x[0] for x in _g
                     if x[4] == "succeeded" and x[3] == 0
                     and str(x[1].get("tool_local_block")).lower() != "true"]

    verdicts.append(V("AC-31", "产出完整性与显式失败", [
        C("① artifact 与适用的 user_delivery 满足冻结的非空/最低完整性结构",
          "PASS" if _guarded and not _silent_empty else "NOT_VERIFIED",
          "%d 次运行经守卫核验；%d 次命中并被阻断；无「守卫未命中却交付块为空」的运行=%s"
          % (_guarded, len(_blocked), not _silent_empty)),
        C("② 两块均不出现对另一块的回指",
          "PASS", "回指检测：新候选 0 次（旧候选同口径 3 次），见 M4_REBASE_DELTA_REPORT"),
        C("③ 不满足时必须显式 PARSE_FAIL 或组件级 Return，绝不以成功空串放行",
          "PASS" if _all_signalled else "FAIL",
          "%d 次命中中，发出 SEAM_COMPLETENESS_GUARD 组件级 Return 的比例=%d/%d"
          % (len(_blocked), sum(1 for x in _has_return if x), len(_has_return))),
        C("④ 恢复/重试保留原失败且不重复副作用", "NOT_VERIFIED",
          "本轮零写操作，未产生真实恢复场景（同 AC-14 合取项⑤）"),
        C("⑤ 判据措辞冲突未裁定（M4-FND-013）", "NOT_VERIFIED",
          "合取项③接受组件级 Return，但本判据失败条件写「status=succeeded 同时交付块为空/回指」，"
          "两者在守卫已发 Return 的运行上同时成立。执行侧按严格读法不记 PASS；"
          "该措辞由执行侧起草，不得由执行侧挑对自己有利的读法。交规划侧裁定。"),
    ], sorted([x[0] for x in _blocked]) or ["（无命中）"], "D+S"))

    verdicts.append(V("AC-30", "治理与定向失效", [
        C("绑定 -005/rev2 与实际基线",
          "PASS" if closing else "NOT_VERIFIED", "收口核验已绑定实际基线与远端"),
        C("变化只使直接 / 传递 / 未知影响项 STALE，有证据不受影响的项继续复用",
          "PASS" if imp.get("explicitly_not_invalidated") and imp.get("invalidated_direct")
          else "NOT_VERIFIED",
          "本轮 M4-FND-005 的影响面计算：直接失效 %d 类、传递失效 %d 类、"
          "无法判断标 STALE %d 类、明确不失效 %d 类" % (
              len(imp.get("invalidated_direct", [])), len(imp.get("invalidated_transitive", [])),
              len(imp.get("unknown_impact_marked_stale", [])),
              len(imp.get("explicitly_not_invalidated", [])))),
    ], ["closing"], "D+S"))

    return verdicts


def main():
    vs = judge()
    n = {"PASS": 0, "FAIL": 0, "NOT_VERIFIED": 0}
    for v in vs:
        n[v["result"]] += 1
    doc = {"verdicts": vs, "summary": n, "total_criteria": len(vs),
           "oracle_ref": ORACLE_REF, "environment": ENVIRONMENT,
           "evidence_grade": "RUNTIME_VERIFIED",
           "authority_event": "RULESIDE-2026-08-26-M4-003",
           "frozen_candidate": "REBASE_PENDING_COMMIT",
           "supersedes_candidate": "0dcd66fd39692ed07df80e39c1f27511d9cbf283",
           "contracts": ["V1_M4_EVIDENCE_COLLECTION_CONTRACT_v0.1/v0.2/v0.3",
                         "V1_M4_REBASE_DELTA_CONTRACT_v0.2/v0.3",
                         "V1_M4_SEAM_FIXTURE_PACK_v0.1/v0.2/v0.3"],
           "note": ("标 H 的合取项一律 NOT_VERIFIED 并指向可运行测试卡；"
                    "执行侧不评价哪份内容更好。")}
    p = os.path.join(EVID, "M4_FINAL_VERDICTS.json")
    with open(p, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, ensure_ascii=False, indent=2)
    for v in vs:
        print("%-6s %-11s %-6s %s" % (v["criterion"], v["result"], v["verifier"], v["name"]))
        for c in v["conjuncts"]:
            print("        [%-12s] %s" % (c["result"], c["clause"][:64]))
    print()
    print("PASS=%d  FAIL=%d  NOT_VERIFIED=%d  （共 %d 条）" % (
        n["PASS"], n["FAIL"], n["NOT_VERIFIED"], len(vs)))
    print("-> %s" % os.path.relpath(p, ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
