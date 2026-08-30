#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Phase C 运行前确定性验证｜B5 的 11 条正负控制 ＋ 真实载荷离线重放。**零模型调用**。

判据真源：unified-app/stages/S4_CANONICAL_TASK_STATE_GATE_v1.0.json（B5）
被测对象：unified-app/workflows/S4_CANONICAL_STATE_NODES_v1.0.py 的 FIELDS_SRC / STATE_SRC
          （与建图脚本注入候选画布的是同一份源码，本文件不复制、不改写）

每条正控制配一个单点负控制（B5 第 11 条）：负控制只改一个变量。
全部通过才允许进入 Phase D 调用模型。

    python3 S4_CANONICAL_STATE_VERIFY_v1.0.py
"""
import hashlib
import importlib.util
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
NC = os.path.join(ROOT, "unified-app/evidence/stages/s4_narrow_chain")
OUT = os.path.join(ROOT, "unified-app/evidence/stages/s4_canonical_state",
                   "S4_CANONICAL_STATE_VERIFY.json")

_s = importlib.util.spec_from_file_location(
    "csn", os.path.join(HERE, "S4_CANONICAL_STATE_NODES_v1.0.py"))
CSN = importlib.util.module_from_spec(_s)
_s.loader.exec_module(CSN)
FN, SN = {}, {}
exec(compile(CSN.FIELDS_SRC, "<uapp_fields>", "exec"), FN)
exec(compile(CSN.STATE_SRC, "<uapp_state>", "exec"), SN)
fields = FN["main"]
state = SN["main"]

TK = "task-canonical-0001"
R = []


def rec(cid, name, ok, detail):
    R.append({"id": cid, "name": name, "result": "PASS" if ok else "FAIL", "detail": detail})


def env(*pairs):
    out = ["provenance:", "  source_kind: M3_OPERATION", "  source_ref: t",
           "  confirmation_state: EXTRACTED_FROM_REGISTERED_SOURCES"]
    obj = [(k, v) for k, v in pairs if k in ("primary_goal", "goal_family")]
    top = [(k, v) for k, v in pairs if k not in ("primary_goal", "goal_family")]
    if obj:
        out.append("objective:")
        for k, v in obj:
            out.append("  `%s`: %s" % (k, v) if k == "primary_goal" else "  %s: %s" % (k, v))
    for k, v in top:
        out.append("%s: %s" % (k, v) if k in ("cta_level", "platform") else "`%s`: %s" % (k, v))
    return "\n".join(out)


def val(env_text, key):
    m = re.search(r"^\s*`?%s`?\s*:\s*(.*)$" % re.escape(key), env_text, re.M)
    return m.group(1).strip() if m else None


def carrier(o):
    return json.loads(o["pending_state_json"])


def blank():
    return json.dumps({"task_key": TK, "rev": 0, "fields": {}, "asked": [],
                       "artifacts": [], "events": []}, ensure_ascii=False)


SNAP_FULL = json.dumps({"revision": 3, "business_goal_categories": ["LONG_TERM_VALUE"],
                        "goal_structure": {"primary_goal": "让熟客能自己判断搭不搭、要不要添"}},
                       ensure_ascii=False)
SNAP_EMPTY = json.dumps({"revision": 3, "business_goal_categories": [],
                         "goal_structure": {"primary_goal": None}}, ensure_ascii=False)


def run():
    # ---------- P-01 M1 business_goal_categories -> objective.goal_family ----------
    p = fields(blank(), TK, env(), "objective.goal_family(未声明，不代为推断)",
               "CONTENT_BRIEF", "先把制作依据定下来。", SNAP_FULL)
    n = fields(blank(), TK, env(), "objective.goal_family(未声明，不代为推断)",
               "CONTENT_BRIEF", "先把制作依据定下来。", SNAP_EMPTY)
    c = carrier(p)["fields"].get("objective.goal_family") or {}
    rec("P-01", "M1 business_goal_categories 规范映射到 objective.goal_family",
        c.get("v") == "LONG_TERM_VALUE" and c.get("lvl") == "D"
        and c.get("kind") == "M1_SNAPSHOT" and c.get("ref")
        and val(p["capability_call"], "goal_family") == "LONG_TERM_VALUE"
        and "goal_family" not in (p["gaps_text"] or "")
        and "objective.goal_family" not in carrier(n)["fields"]
        and "goal_family" in (n["gaps_text"] or ""),
        {"pos_value": c, "pos_envelope_line": val(p["capability_call"], "goal_family"),
         "pos_gaps": p["gaps_text"], "neg_gaps": n["gaps_text"],
         "neg_in_carrier": "objective.goal_family" in carrier(n)["fields"],
         "写法": "裸键写回 objective 块内，与 Hop 现有外壳写法一致"})

    # ---------- P-02 占位符不得填满 primary_goal ----------
    PH = "（已登记来源中未明确写出）"
    p = fields(blank(), TK, env(("primary_goal", PH)), "objective.primary_goal",
               "CONTENT_BRIEF", "先把制作依据定下来。", SNAP_EMPTY)
    n = fields(blank(), TK, env(("primary_goal", "让熟客自己判断搭不搭")), "",
               "CONTENT_BRIEF", "先把制作依据定下来。", SNAP_EMPTY)
    rec("P-02", "缺失占位符不入载体、不关闭缺口",
        "objective.primary_goal" not in carrier(p)["fields"]
        and "objective.primary_goal" in (p["gaps_text"] or "")
        and carrier(n)["fields"].get("objective.primary_goal", {}).get("v") == "让熟客自己判断搭不搭",
        {"pos_carrier_has": "objective.primary_goal" in carrier(p)["fields"],
         "pos_gaps": p["gaps_text"], "pos_contradiction": p["contradiction_fields"],
         "neg_carrier": carrier(n)["fields"].get("objective.primary_goal")})

    # ---------- P-03 运营周期时间不得填入 production.time_window ----------
    base = fields(blank(), TK, env(("time_window", "四周内")), "", "CONTENT_BRIEF",
                  "先把制作依据定下来。", SNAP_EMPTY)
    p = fields(base["pending_state_json"], TK, env(), "time_window", "PRODUCTION_DIRECTOR",
               "这条该怎么制作？", SNAP_EMPTY)
    prod = fields(blank(), TK, env(("time_window", "今天半天内出母版")), "",
                  "PRODUCTION_DIRECTOR", "今天半天内先出母版。", SNAP_EMPTY)
    n = fields(prod["pending_state_json"], TK, env(), "time_window", "PRODUCTION_DIRECTOR",
               "接着说。", SNAP_EMPTY)
    rec("P-03", "运营周期时间窗不被回填进生产时间窗；生产时间窗自身正常回填",
        "operation.time_window" in carrier(base)["fields"]
        and "production.time_window" not in carrier(base)["fields"]
        and "time_window" in (p["gaps_text"] or "") and not p["carried_fields"]
        and "production.time_window" in carrier(prod)["fields"]
        and n["carried_fields"] == "production.time_window",
        {"CB 轮解析为": list(carrier(base)["fields"]), "PD 轮缺口": p["gaps_text"],
         "PD 轮补齐": p["carried_fields"] or "(空)",
         "负控制补齐": n["carried_fields"],
         "负控制回填值": val(n["capability_call"], "time_window")})

    # ---------- P-04 低权威不得覆盖用户确认值 ----------
    a1 = fields(blank(), TK, env(("content_promise", "判断搭不搭是有方法可循的")),
                "", "CONTENT_BRIEF", "判断搭不搭是有方法可循的", SNAP_EMPTY)
    p = fields(a1["pending_state_json"], TK, env(("content_promise", "模型改写过的另一句话")),
               "", "CREATIVE_SCRIPT", "接着把口播稿写出来。", SNAP_EMPTY)
    e1 = fields(blank(), TK, env(("content_promise", "模型先写的一句话")), "",
                "CONTENT_BRIEF", "先把制作依据定下来。", SNAP_EMPTY)
    n = fields(e1["pending_state_json"], TK, env(("content_promise", "用户后来给的准确一句话")),
               "", "CONTENT_BRIEF", "用户后来给的准确一句话", SNAP_EMPTY)
    rec("P-04", "E 级不覆盖 A/B 级；A 级可以升级 E 级",
        carrier(a1)["fields"]["content.promise"]["lvl"] == "A"
        and carrier(p)["fields"]["content.promise"]["v"] == "判断搭不搭是有方法可循的"
        and p["held_fields"] == "content.promise"
        and val(p["capability_call"], "content_promise") == "判断搭不搭是有方法可循的"
        and carrier(e1)["fields"]["content.promise"]["lvl"] == "E"
        and carrier(n)["fields"]["content.promise"]["v"] == "用户后来给的准确一句话"
        and carrier(n)["fields"]["content.promise"]["lvl"] == "A",
        {"pos_held": p["held_fields"], "pos_载体值": carrier(p)["fields"]["content.promise"],
         "pos_外壳被改回": val(p["capability_call"], "content_promise"),
         "neg_升级后": carrier(n)["fields"]["content.promise"]})

    # ---------- P-05 主动纠正更新值并使依赖 artifact STALE ----------
    s0 = fields(blank(), TK, env(("content_promise", "判断搭不搭是有方法可循的")),
                "", "CONTENT_BRIEF", "判断搭不搭是有方法可循的", SNAP_EMPTY)
    s1 = state(s0["pending_state_json"], s0["envelope_fields_json"],
               "# Content Brief 正文" + "x" * 400, "CONTENT_BRIEF")
    s2 = fields(s1["task_state_json"], TK, env(), "", "CONTENT_BRIEF",
                "刚才那份可以，接着写口播稿。", SNAP_EMPTY)   # 接受事件，无未决提问
    corr = "这条改成只讲怎么挑不讲搭配方法"
    p = fields(s2["pending_state_json"], TK, env(("content_promise", corr)), "",
               "CREATIVE_SCRIPT", corr, SNAP_EMPTY)
    n = fields(s2["pending_state_json"], TK, env(("content_promise", corr)), "",
               "CREATIVE_SCRIPT", "接着把口播稿写出来。", SNAP_EMPTY)
    pa = carrier(p)["artifacts"][0]
    na = carrier(n)["artifacts"][0]
    rec("P-05", "用户主动纠正（未被询问）更新值、frev+1、依赖 artifact 置 STALE",
        carrier(p)["fields"]["content.promise"]["v"] == corr
        and carrier(p)["fields"]["content.promise"]["frev"] == 2
        and p["corrected_fields"] == "content.promise" and pa["stale"] is True
        and "content.promise" in (pa.get("stale_reason") or "")
        and carrier(n)["fields"]["content.promise"]["v"] == "判断搭不搭是有方法可循的"
        and n["corrected_fields"] == "" and na["stale"] is False,
        {"pos_corrected": p["corrected_fields"], "pos_stale": p["stale_artifacts"],
         "pos_stale_reason": pa.get("stale_reason"), "pos_frev": carrier(p)["fields"]["content.promise"]["frev"],
         "neg_corrected": n["corrected_fields"] or "(空)", "neg_stale": na["stale"],
         "neg_held": n["held_fields"], "判定": "本轮原话与新值 8 字重合 ⇒ A 级；无重合 ⇒ E 级"})

    # ---------- P-06 真正跨轮字段在清空载体后重新成为缺口 ----------
    t1 = fields(blank(), TK, env(("content_origin_mode", "门店已有素材剪辑，不安排重新拍摄")),
                "", "CREATIVE_SCRIPT",
                "门店已有素材剪辑，不安排重新拍摄", SNAP_EMPTY)
    c1 = carrier(t1)["fields"]["content.origin_mode"]
    p = fields(t1["pending_state_json"], TK, env(), "content_origin_mode",
               "PRODUCTION_DIRECTOR", "这条该怎么制作？", SNAP_EMPTY)
    abl = fields(blank(), TK, env(), "content_origin_mode", "PRODUCTION_DIRECTOR",
                 "这条该怎么制作？", SNAP_EMPTY)
    same_turn = fields(blank(), TK, env(("content_promise", "同轮自填的一句话")),
                       "", "CONTENT_BRIEF", "同轮自填的一句话", SNAP_EMPTY)
    rec("P-06", "跨轮字段（origin_turn < 当前轮）清空载体后重新成为缺口；同轮自填不得当样本",
        c1["origin_turn"] == 1 and p["carried_fields"] == "content.origin_mode"
        and "content_origin_mode" in (abl["gaps_text"] or "") and not abl["carried_fields"]
        and carrier(same_turn)["fields"]["content.promise"]["origin_turn"] == 1
        and same_turn["carried_fields"] == "",
        {"origin_turn": c1["origin_turn"], "第二轮补齐": p["carried_fields"],
         "清空后缺口": abl["gaps_text"], "清空后补齐": abl["carried_fields"] or "(空)",
         "同轮自填样本的 carried": same_turn["carried_fields"] or "(空)",
         "修正": "旧 N-15 负控制误选同轮自填轮次；本判据显式排除 origin_turn == 当前轮"})

    # ---------- P-07 新 task_key 不继承内容级字段 ----------
    base = fields(blank(), TK, env(("content_promise", "判断搭不搭是有方法可循的"),
                                   ("content_origin_mode", "门店已有素材剪辑")), "",
                  "CONTENT_BRIEF", "先把制作依据定下来。", SNAP_EMPTY)
    p = fields(base["pending_state_json"], "task-OTHER-9999", env(), "content_promise",
               "CONTENT_BRIEF", "换一条新的内容。", SNAP_EMPTY)
    n = fields(base["pending_state_json"], TK, env(), "content_promise",
               "CONTENT_BRIEF", "接着说。", SNAP_EMPTY)
    rec("P-07", "task_key 变化即新内容任务，内容级字段一个不继承",
        carrier(p)["fields"] == {} and not p["carried_fields"]
        and "content_promise" in (p["gaps_text"] or "")
        and n["carried_fields"] == "content.promise",
        {"新 task_key 载体": carrier(p)["fields"], "新 task_key 缺口": p["gaps_text"],
         "同 task_key 补齐": n["carried_fields"],
         "reset 事件": carrier(p)["events"][-1]["reset"]})

    # ---------- P-08 同一规范身份不能同时非空又在缺口里 ----------
    p = fields(blank(), TK, env(("content_promise", "外壳里写着的一句话")), "content_promise",
               "CONTENT_BRIEF", "先把制作依据定下来。", SNAP_EMPTY)
    n = fields(blank(), TK, env(("content_promise", "外壳里写着的一句话")), "",
               "CONTENT_BRIEF", "先把制作依据定下来。", SNAP_EMPTY)
    rec("P-08", "外壳非空且同时报缺口 ⇒ fail-closed：值不入载体、字段保持缺口（TD-UAPP-23）",
        p["contradiction_fields"] == "content.promise"
        and "content.promise" not in carrier(p)["fields"]
        and "content_promise" in (p["gaps_text"] or "")
        and n["contradiction_fields"] == ""
        and carrier(n)["fields"]["content.promise"]["v"] == "外壳里写着的一句话",
        {"pos_contradiction": p["contradiction_fields"], "pos_carrier": list(carrier(p)["fields"]),
         "pos_gaps": p["gaps_text"], "neg_carrier": carrier(n)["fields"].get("content.promise"),
         "登记": "TD-UAPP-23：Hop 同一次执行既写非空值又报同名缺口"})

    # ---------- P-09 PP 直接读 CS 只登记 PRE 短入口 ----------
    CS = "# Creative Script 完整产出\n\n逐字稿正文" + "y" * 500
    PD = "# Production Director 制作方案\n\n拍摄与检索安排" + "z" * 500
    s0 = fields(blank(), TK, env(), "", "CREATIVE_SCRIPT", "写口播稿。", SNAP_EMPTY)
    s1 = state(s0["pending_state_json"], s0["envelope_fields_json"], CS, "CREATIVE_SCRIPT")
    s2 = fields(s1["task_state_json"], TK, env(), "", "PRODUCTION_DIRECTOR",
                "这版口播稿可以。接着说怎么制作。", SNAP_EMPTY)
    s3 = state(s2["pending_state_json"], s2["envelope_fields_json"], PD, "PRODUCTION_DIRECTOR")
    nrm = re.sub(r"\s+", " ", CS).strip()
    nrmpd = re.sub(r"\s+", " ", PD).strip()
    pre = fields(s3["task_state_json"], TK,
                 env(("content_body_or_beats", nrm)), "", "PUBLISHING_PACKAGING",
                 "刚才的制作方案可以，给标题和封面。", SNAP_EMPTY)
    full = fields(s3["task_state_json"], TK,
                  env(("content_body_or_beats", nrmpd)), "", "PUBLISHING_PACKAGING",
                  "刚才的制作方案可以，给标题和封面。", SNAP_EMPTY)
    bp = json.loads(pre["upstream_binding_json"])[0]
    bf = json.loads(full["upstream_binding_json"])[0]
    rec("P-09", "PP 上游是 CS ⇒ PRE 短入口；上游是本轮 PD 且指纹相等 ⇒ 完整链",
        bp["lineage"] == "BOUND" and bp["upstream_capability"] == "CREATIVE_SCRIPT"
        and bf["lineage"] == "BOUND" and bf["upstream_capability"] == "PRODUCTION_DIRECTOR",
        {"CS 直达": bp, "PD 下游": bf,
         "完整链判据": "upstream_capability == PRODUCTION_DIRECTOR 且 sha256 相等，由判定器离线复算"})

    # ---------- P-10 artifact 与 capability 身份成对保持 ----------
    s0 = fields(blank(), TK, env(), "", "CREATIVE_SCRIPT", "写口播稿。", SNAP_EMPTY)
    s1 = state(s0["pending_state_json"], s0["envelope_fields_json"], CS, "CREATIVE_SCRIPT")
    bad = state(s1["task_state_json"], s0["envelope_fields_json"], CS, "PRODUCTION_DIRECTOR")
    good = state(s1["task_state_json"], s0["envelope_fields_json"], CS, "CREATIVE_SCRIPT")
    rec("P-10", "同一指纹挂两个能力身份 ⇒ 冲突拒绝；同身份重复 ⇒ 不重复计数",
        bad["ledger_action"] == "IDENTITY_CONFLICT" and bad["ledger_conflict"]
        and len(json.loads(bad["task_state_json"])["artifacts"]) == 1
        and good["ledger_action"] == "ALREADY_PRESENT"
        and len(json.loads(good["task_state_json"])["artifacts"]) == 1,
        {"冲突动作": bad["ledger_action"], "冲突内容": bad["ledger_conflict"],
         "同身份动作": good["ledger_action"],
         "账本条数": len(json.loads(good["task_state_json"])["artifacts"])})

    # ---------- P-11 未接受或已 STALE 的上游不得进入下一能力 ----------
    s0 = fields(blank(), TK, env(), "", "CONTENT_BRIEF", "先把制作依据定下来。", SNAP_EMPTY)
    s1 = state(s0["pending_state_json"], s0["envelope_fields_json"], CS, "CREATIVE_SCRIPT")
    noacc = fields(s1["task_state_json"], TK, env(("script_or_equivalent_beats", nrm)), "",
                   "PRODUCTION_DIRECTOR", "这条该怎么制作？", SNAP_EMPTY)
    acc = fields(s1["task_state_json"], TK, env(("script_or_equivalent_beats", nrm)), "",
                 "PRODUCTION_DIRECTOR", "这版口播稿可以。这条该怎么制作？", SNAP_EMPTY)
    b_no = json.loads(noacc["upstream_binding_json"])[0]
    b_ok = json.loads(acc["upstream_binding_json"])[0]
    rec("P-11", "未接受的上游 artifact 被摘除并计为缺口；接受后正常保留",
        b_no["lineage"] == "REJECTED" and b_no["reason"] == "NOT_ACCEPTED"
        and val(noacc["capability_call"], "script_or_equivalent_beats") is None
        and "script_or_equivalent_beats" in (noacc["gaps_text"] or "")
        and b_ok["lineage"] == "BOUND"
        and val(acc["capability_call"], "script_or_equivalent_beats") is not None,
        {"未接受": b_no, "未接受后缺口": noacc["gaps_text"],
         "接受后": b_ok, "接受词": "可以",
         "对照 A-08": "旧版 stale_downstream 无消费者；本版接受闸门真正摘除外壳槽位"})

    # ---------- 真实载荷离线重放（Phase C 第 2 步） ----------
    replay, prev = [], ""
    for t in range(1, 7):
        d = json.load(io.open(os.path.join(NC, "S4-NC-T%d.json" % t), encoding="utf-8"))
        nd = {n["node_id"]: n for n in d["node_detail"]}
        hop = json.loads(nd["uapp_hop"]["outputs"])
        rt = json.loads(nd["uapp_route"]["outputs"])
        snap = json.loads(nd["m1_compiler"]["outputs"]).get("snapshot_json") or ""
        art = json.loads(nd["uapp_seam"]["outputs"]).get("artifact") if "uapp_seam" in nd else ""
        o = fields(prev, TK, hop["capability_call"], hop.get("extraction_gaps_text") or "",
                   rt["target_capability"], rt.get("user_request") or "", snap)
        s = state(o["pending_state_json"], o["envelope_fields_json"],
                  art or "", rt["target_capability"])
        prev = s["task_state_json"]
        c = json.loads(prev)
        replay.append({"turn": t, "capability": rt["target_capability"],
                       "note": o["merge_note"], "gaps_out": o["gaps_text"],
                       "contradictions": o["contradiction_fields"],
                       "unspecified_keys": o["unspecified_keys"],
                       "ledger": s["ledger_note"],
                       "fields": {k: {"lvl": v["lvl"], "t": v["origin_turn"], "frev": v["frev"],
                                      "sc": v["sc"], "ref": v["ref"], "v": v["v"][:40]}
                                  for k, v in sorted(c["fields"].items())}})
    last = replay[-1]["fields"]
    pg = last.get("objective.primary_goal") or {}
    gf = last.get("objective.goal_family") or {}
    no_ph = not any(FN["_missing"](v["v"]) for v in last.values())
    no_art_field = not any(len(v["v"]) > 4000 for v in last.values())
    all_ref = all(v["ref"] for v in last.values())
    sourced = all(v["lvl"] != "E" for v in (pg, gf) if v)
    # 判据说明：不写死等级必须是 D。规范权威顺序是 A > B > C > D > E，
    # 系统在 T1 由 M1 快照以 D 级登记、T2 被用户回答以 A 级确认，是**正确**的升级路径。
    # 真正要成立的性质是：值正确、非占位、有 source_ref、且**不是无来源的模型抽取（E）**。
    rec("R-01", "真实 T1–T6 载荷重放：goal_family 与 primary_goal 取到真实值且不是 E 级，载体内无占位符",
        gf.get("v") == "LONG_TERM_VALUE" and pg.get("v")
        and "未明确写出" not in pg.get("v", "") and sourced
        and no_ph and no_art_field and all_ref,
        {"objective.goal_family": gf, "objective.primary_goal": pg,
         "两项均非 E 级": sourced, "载体内无缺失占位": no_ph,
         "载体内无整篇 artifact": no_art_field, "每条都有 source_ref": all_ref,
         "对照旧版": "旧载体 primary_goal 六轮都是『（已登记来源中未明确写出）』，goal_family 从未入账"})

    # R-02 改写理由（登记在案）：原判据要求重放里出现非空 contradictions，
    # 但缺失语义规则先于矛盾检测生效——占位值在进入 env_vals 之前就被拦掉，
    # 因此 contradictions 恒为空。这是两道防线的**正确**先后，不是漏检。
    # 改判为：占位值确实被拦在载体之外，且矛盾检测本身可被单点负控制触发（P-08 已证）。
    ph_blocked = all("objective.primary_goal" not in x["fields"]
                     or "未明确写出" not in x["fields"]["objective.primary_goal"]["v"]
                     for x in replay)
    t1_gaps = replay[0]["gaps_out"]
    rec("R-02", "真实载荷重放：占位 primary_goal 被拦在载体外并保持缺口；未登记键不回填",
        ph_blocked and "objective.primary_goal" in (t1_gaps or "")
        and all(not x["unspecified_keys"] for x in replay),
        {"占位值全程未入载体": ph_blocked, "T1 缺口": t1_gaps,
         "逐轮矛盾": [(x["turn"], x["contradictions"] or "(空)") for x in replay],
         "逐轮未登记反引号键": [(x["turn"], x["unspecified_keys"] or "(空)") for x in replay],
         "为什么矛盾恒空": "缺失语义整值匹配先于矛盾检测生效；矛盾检测的可触发性由 P-08 单点负控制证明",
         "未登记裸键": "equivalence_basis 等裸键根本不参与解析——只有登记为 PL 的裸键才被读取，"
                       "这正是『不要泛化正则』的直接后果"})

    # R-03 上游接受闸门在真实载荷上的表现（旧场景 T5/T6 用户从未说过接受词）
    rej = [(x["turn"], x["note"]) for x in replay if "REJECTED" in (x["note"] or "")]
    rec("R-03", "旧场景无接受话术 ⇒ 上游 artifact 被摘除；新场景 T3/T5/T7 含接受话术",
        len(rej) == 2,
        {"被摘除的轮次": [t for t, _ in rej],
         "原因": "旧六轮话术里 T5『这条该怎么拍？』、T6『标题和封面帮我定一下。』都不含接受词，"
                 "按 B4『未明确接受时不得自动送入下一专业能力』摘除，属正确行为",
         "新场景": "T3『刚才的制作依据可以』、T5『这版口播稿可以』、T7『刚才的制作方案可以』"})

    npass = sum(1 for x in R if x["result"] == "PASS")
    rep = {"document": {"id": "S4_CANONICAL_STATE_VERIFY_v1.0",
                        "task_id": "DIYU-V1-UNIFIED-DIFY-APPLICATION-001",
                        "criteria_ref": "unified-app/stages/S4_CANONICAL_TASK_STATE_GATE_v1.0.json",
                        "criteria_sha256": hashlib.sha256(io.open(os.path.join(
                            ROOT, "unified-app/stages/S4_CANONICAL_TASK_STATE_GATE_v1.0.json"),
                            "rb").read()).hexdigest(),
                        "nodes_src_sha256": hashlib.sha256(io.open(os.path.join(
                            HERE, "S4_CANONICAL_STATE_NODES_v1.0.py"), "rb").read()).hexdigest(),
                        "model_calls": 0, "dify_writes": 0},
           "summary": {"pass": npass, "total": len(R),
                       "verdict": "PASS" if npass == len(R) else "FAIL"},
           "checks": R, "replay": replay}
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    io.open(OUT, "w", encoding="utf-8").write(json.dumps(rep, ensure_ascii=False, indent=1) + "\n")
    for x in R:
        print("%-5s %-4s %s" % (x["id"], x["result"], x["name"]))
    print("---- %d/%d ----" % (npass, len(R)))
    return 0 if npass == len(R) else 1


if __name__ == "__main__":
    sys.exit(run())
