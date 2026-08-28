#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""M5 扩展完整主故事 · FULL-01 / FULL-02。

FULL-01  自然语言经营诉求 → M1 任务上下文 → M2 最小当前投影 → M3 周期判断与内容任务
         → Content Brief → 当前任务适用的专业 Skill 子集 → Creative Script
         → Production Director → Publishing & Packaging → 测试发布记录
FULL-02  测试/模拟反馈采集 → M2 按版本幂等写入 → M3 复盘更新 → Cycle N+1

三条设计要点，都是合同硬约束不是风格选择：

1. **M1 的 account_anchor_supplied 是本次真正接上的接缝。** M1 编译器把它写成
   「留给未来『持续运营且 M2 有当前合法锚点』这条路径的消费入口」，并注明当时
   M2 尚不存在、Dify 图里没有任何节点会传它。M5 就是它等的那个调用方：
   账号锚点由 M2 最小投影提供，不靠本轮自然语言重新提取。

2. **专业能力按需调用，不拼固定全链。** 走哪几个能力由本轮任务决定；
   跳过是合法的，跳过要如实记进 skipped 并说明理由。

3. **测试发布必须显式标记。** M2 的 is_test / is_simulated 是必填布尔且默认
   False=真实，本文件一律显式传 True —— 「测试反馈 ≠ 真实平台经营增益」
   这条非承诺在数据层就被钉住，不靠文档措辞。

运行本文件默认是**诊断**；正式运行由 Candidate Run Manifest 冻结后的 runner 驱动。
"""
import importlib.util
import json
import os
import subprocess
import uuid

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))


def _load(n, p):
    s = importlib.util.spec_from_file_location(n, p)
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m


RT = _load("m5_rt", os.path.join(ROOT, "decision-chain", "workflows",
                                 "DIYU_M5_INTEGRATION_RUNTIME_v0.1.py"))
M1 = RT.M1


def _now_iso():
    """时间来自数据库，不用宿主本地时钟，避免跨时区解释。"""
    p = subprocess.run(["docker", "exec", "-i", "docker-db_postgres-1", "psql", "-U", "postgres",
                        "-d", "diyu_business", "-t", "-A", "-c",
                        "SELECT to_char(now() AT TIME ZONE 'UTC','YYYY-MM-DD\"T\"HH24:MI:SS\"+00:00\"');"],
                       capture_output=True, text=True)
    return p.stdout.strip()


# ---------------------------------------------------------------- 测试工作区
def bootstrap(tag):
    """建立任务域测试工作区。只写测试数据，不触碰任何既有非测试数据。"""
    u = tag[:8]
    st, user = RT.m2("POST", "/users", {"external_ref": "m5-%s" % u})
    assert st == 200, ("create user", st, user)
    actor = user["external_ref"]
    st, ws = RT.m2("POST", "/workspaces",
                   {"name": "ws-m5-%s" % u, "kind": "personal", "owner_user_id": user["id"]})
    assert st == 200, ("create ws", st, ws)
    st, acct = RT.m2("POST", "/workspaces/%s/accounts" % ws["id"],
                     {"platform": "test-platform", "handle": "xuli-%s" % u}, actor=actor)
    assert st == 200, ("create account", st, acct)
    now = _now_iso()
    st, cyc = RT.m2("POST", "/workspaces/%s/cycles" % ws["id"], {
        "idempotency_key": "cycle-%s" % u, "account_id": acct["id"],
        "label": "M5 Cycle N", "start_at": now,
        "baseline_capacity": 4, "baseline_capacity_source": "fixture:序里集素材与资源夹具",
        "expected_publish_count": 4, "expected_publish_count_source": "fixture:同上",
    }, actor=actor)
    assert st == 200, ("create cycle", st, cyc)
    st, task = RT.m2("POST", "/workspaces/%s/tasks" % ws["id"], {
        "idempotency_key": "task-%s" % u, "account_id": acct["id"],
        "cycle_id": cyc["id"], "kind": "m5-full-story"}, actor=actor)
    assert st == 200, ("create task", st, task)
    return {"actor": actor, "user": user, "ws": ws["id"], "account": acct["id"],
            "cycle": cyc["id"], "task": task["id"], "tag": u}


def projection_text(boot):
    """M2 最小当前投影 → M3 的 account_context。字段照抄，不代为解释。"""
    p = RT.current_projection(boot["ws"], boot["actor"], boot["account"])
    cyc = (p["cycle_current"] or {}).get("body") or {}
    dec = (p["decision_latest"] or {}).get("body") or {}
    lines = [
        "【账号最小当前投影 · 来源 M2 服务实时读取】",
        "账号：序里集 XULI SELECT 品牌号（测试账号 handle=%s，平台=test-platform）" % boot["tag"],
        "当前周期：%s" % (cyc.get("label") or "（M2 未返回周期标签）"),
        "周期起始：%s" % (cyc.get("start_at") or "（空）"),
        "基线产能：%s（来源：%s）" % (cyc.get("baseline_capacity"), cyc.get("baseline_capacity_source")),
        "预期发布条数：%s" % (cyc.get("expected_publish_count"),),
        "最近一次周期决策：%s" % (dec.get("decision") or "（本周期尚无决策记录）"),
        "已发布内容与反馈：%s" % (dec.get("based_on") or "（本周期尚无发布与反馈）"),
    ]
    return "\n".join(str(x) for x in lines), p


# ---------------------------------------------------------------- 已登记事实
# 这三份夹具是 M4 后三个能力必填项的**真源**：产能班底、时间窗口、出镜与引用授权、
# 明确的不承诺，M3 的运营判断里没有也不该有——它们是资源事实，不是运营判断。
FIXTURES = [
    "序里集_Campaign当前素材与资源夹具_v0.1.md",
    "序里集_Campaign最小承接条件夹具_v0.1.md",
    "一页纸夹具品牌事实 v0.1.md",
]


def registered_facts():
    """读取已登记事实夹具原文。照抄，不摘要、不改写、不代为解释。"""
    parts = []
    for name in FIXTURES:
        path = os.path.join(ROOT, "decision-chain", "fixtures", name)
        with open(path, encoding="utf-8") as fh:
            parts.append("===== 夹具：%s =====\n%s" % (name, fh.read()))
    return "\n\n".join(parts)


# ---------------------------------------------------------------- FULL-01
def full_story_01(rt, boot, nl_request, applicable=("CONTENT_BRIEF", "CREATIVE_SCRIPT",
                                                    "PRODUCTION_DIRECTOR", "PUBLISHING_PACKAGING"),
                  facts=None):
    """一次自然使用：自然语言诉求 → 落到可发布的成品包。

    每进一个专业能力之前先过一次**跨能力接缝适配**，因为六个能力的必填清单
    实测互不相同（现场从已发布 graph 读出）。适配器只抽取、不推断；抽不到就留空，
    由能力侧自己判 INSUFFICIENT——离线反向控制 11/11 证明闸门仍然咬得住。
    """
    facts = registered_facts() if facts is None else facts
    rec = {"case": "FULL-01", "steps": [], "skipped": [], "boot": boot,
           "registered_facts_chars": len(facts)}

    # 1. M1 任务上下文 —— 账号锚点由 M2 投影供给（M1 预留的 account_anchor_supplied 入口）
    acct_text, raw_proj = projection_text(boot)
    m1_out = M1.main(user_query=nl_request, snapshot_json="", shadow_patch={},
                     material_text="",
                     account_anchor_supplied={
                         "identity_text": "序里集 XULI SELECT 品牌号（测试账号，平台 test-platform）",
                         "confirmation": "M2_CURRENT_PROJECTION"})
    rec["steps"].append({"step": "M1_context", "ok": isinstance(m1_out, dict),
                         "account_anchor_source": ((m1_out.get("snapshot") or {}).get("account_anchor") or {}).get("source")
                         if isinstance(m1_out, dict) else None})

    # 2. M2 最小当前投影
    rec["steps"].append({"step": "M2_projection",
                         "cycle_http": raw_proj["cycle_current"]["status"],
                         "decision_http": raw_proj["decision_latest"]["status"],
                         "account_context_chars": len(acct_text)})

    # 3. M3 周期判断与内容任务（夹具作为可加载参考进入，不由本文件代抄事实）
    m3 = rt.m3_operate(account_context=acct_text, user_request=nl_request,
                       loaded_references=facts)
    rec["steps"].append({"step": "M3_operate", "platform_status": m3["platform_status"],
                         "run_id": m3["run_id"], "elapsed": m3["elapsed_seconds"],
                         "gate_status": (m3["outputs"] or {}).get("gate_status"),
                         "judgment_chars": len((m3["outputs"] or {}).get("operating_judgment") or "")})
    judgment = (m3["outputs"] or {}).get("operating_judgment") or ""
    if not judgment:
        rec["blocked_at"] = "M3_operate produced empty operating_judgment"
        return rec, m3

    # 4-7. 按需进入专业能力，一次一个；跳过如实登记
    upstream = ""
    last_delivered = None
    for cap in RT.CAPABILITIES:
        if cap not in applicable:
            rec["skipped"].append({"capability": cap,
                                   "reason": "本轮任务不适用；合法跳过，不暗跑"})
            continue

        h = rt.hop(cap, m3_judgment=judgment, upstream_delivery=upstream,
                   registered_facts=facts, account_context=acct_text,
                   user_request=nl_request)
        ho = h["outputs"] or {}
        rec["steps"].append({
            "step": "hop:%s" % cap, "platform_status": h["platform_status"],
            "run_id": h["run_id"], "elapsed": h["elapsed_seconds"],
            "extraction_gaps": ho.get("extraction_gaps_text"),
            "extraction_gaps_count": ho.get("extraction_gaps_count"),
            "source_map": ho.get("source_map_json"),
            "envelope_chars": len(ho.get("capability_call") or ""),
        })
        call = ho.get("capability_call") or ""
        prof = ho.get("professional_input") or ""
        if not call:
            rec["steps"].append({"step": "seam:%s" % cap, "not_run": "适配器未产出外壳，本跳不发起调用"})
            continue

        r = rt.seam(cap, capability_call=call, professional_input=prof)
        rec["steps"].append({
            "step": "seam:%s" % cap,
            "platform_status": r["platform_status"],
            "business_delivery_outcome": r["business_delivery_outcome"],
            "delivered": RT.delivered(r),
            "component_return": RT.is_component_return(r),
            "run_id": r["run_id"], "elapsed": r["elapsed_seconds"],
            "user_delivery_chars": len(r["user_delivery"] or ""),
        })
        # 组件级 Return 是本分支结果，不是整任务硬停：记录后继续，由调用方决定
        if RT.delivered(r) and (r["user_delivery"] or "").strip():
            upstream = r["user_delivery"]
            last_delivered = cap
            rec.setdefault("deliveries", {})[cap] = r["user_delivery"]
    rec["last_delivered_step"] = last_delivered
    rec["final_text"] = upstream
    return rec, m3


# ---------------------------------------------------------------- 发布与写回
def record_publish_and_feedback(boot, final_text, tag):
    """测试/模拟发布 + 反馈幂等写回。两次同 idempotency_key 写入，证明不制造双份事实。"""
    a = boot["actor"]; ws = boot["ws"]
    ch = __import__("hashlib").sha256((final_text or "").encode()).hexdigest()
    st, art = RT.m2("POST", "/workspaces/%s/tasks/%s/artifacts" % (ws, boot["task"]),
                    {"kind": "final", "content_hash": ch}, actor=a)
    assert st == 200, ("artifact", st, art)
    st, ver = RT.m2("POST", "/workspaces/%s/artifacts/%s/versions" % (ws, art["id"]),
                    {"idempotency_key": "ver-%s" % tag, "content_hash": ch,
                     "produced_by": "M5 integration candidate"}, actor=a)
    assert st == 200, ("version", st, ver)
    now = _now_iso()
    st, pub = RT.m2("POST", "/workspaces/%s/publish-instances" % ws, {
        "idempotency_key": "pub-%s" % tag, "content_version_id": ver["id"],
        "account_id": boot["account"], "platform": "test-platform",
        "published_at": now, "is_test": True, "is_simulated": True}, actor=a)
    assert st == 200, ("publish", st, pub)

    fb_body = {"idempotency_key": "fb-%s" % tag, "publish_instance_id": pub["id"],
               "kind": "observation", "is_test": True, "is_simulated": True,
               "is_manual_entry": True, "source": "M5 模拟反馈",
               "observed_at": now,
               "payload": {"views": 1200, "saves": 41, "comments": 7,
                           "note": "模拟测试反馈，非真实平台数据"}}
    st1, fb1 = RT.m2("POST", "/workspaces/%s/feedback" % ws, fb_body, actor=a)
    st2, fb2 = RT.m2("POST", "/workspaces/%s/feedback" % ws, fb_body, actor=a)
    return {"artifact": art["id"], "version": ver["id"], "publish_instance": pub["id"],
            "publish_is_test": pub.get("is_test"), "publish_is_simulated": pub.get("is_simulated"),
            "feedback_first": (st1, fb1.get("id")), "feedback_repeat": (st2, fb2.get("id")),
            "idempotent_same_row": fb1.get("id") == fb2.get("id")}


# ---------------------------------------------------------------- FULL-02
def full_story_02(rt, boot, pubrec):
    rec = {"case": "FULL-02", "steps": []}
    a = boot["actor"]; ws = boot["ws"]
    st, fbs = RT.m2("GET", "/workspaces/%s/publish-instances/%s/feedback"
                    % (ws, pubrec["publish_instance"]), actor=a)
    rec["steps"].append({"step": "M2_feedback_readback", "http": st,
                         "rows": len(fbs) if isinstance(fbs, list) else fbs})
    acct_text, _ = projection_text(boot)
    acct_text += ("\n【本周期已发生】测试发布 1 条（is_test=true, is_simulated=true），"
                  "模拟反馈：views 1200 / saves 41 / comments 7。"
                  "该反馈为测试模拟，不等于真实平台经营结果。")
    m3 = rt.m3_operate(account_context=acct_text,
                       user_request="上一条内容已按测试发布并拿到模拟反馈，请据此复盘，"
                                    "并给出下一周期怎么走。")
    rec["steps"].append({"step": "M3_review", "platform_status": m3["platform_status"],
                         "run_id": m3["run_id"], "elapsed": m3["elapsed_seconds"],
                         "gate_status": (m3["outputs"] or {}).get("gate_status"),
                         "judgment_chars": len((m3["outputs"] or {}).get("operating_judgment") or "")})
    now = _now_iso()
    st, nxt = RT.m2("POST", "/workspaces/%s/cycles" % ws, {
        "idempotency_key": "cycle-next-%s" % boot["tag"], "account_id": boot["account"],
        "label": "M5 Cycle N+1", "start_at": now,
        "baseline_capacity": 4, "baseline_capacity_source": "carried from Cycle N"}, actor=a)
    rec["steps"].append({"step": "M2_cycle_next", "http": st, "cycle_id": nxt.get("id")})
    st, dec = RT.m2("POST", "/workspaces/%s/accounts/%s/cycles/decisions" % (ws, boot["account"]), {
        "idempotency_key": "dec-%s" % boot["tag"], "cycle_id": boot["cycle"],
        "decision": "adjusted", "source": "M3 复盘（M5 集成候选）",
        "rationale": "依据本周期测试发布的模拟反馈作出，测试反馈不等于真实经营结果",
        "based_on": {"publish_instance_id": pubrec["publish_instance"],
                     "feedback_is_test": True, "feedback_is_simulated": True},
        "resulting_cycle_id": nxt.get("id")}, actor=a)
    rec["steps"].append({"step": "M2_cycle_decision", "http": st,
                         "decision_id": dec.get("id"),
                         "resulting_cycle_id": dec.get("resulting_cycle_id")})
    return rec, m3
