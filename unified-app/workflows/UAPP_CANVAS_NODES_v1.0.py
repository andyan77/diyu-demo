#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""统一 Founder Canvas 的自有代码节点源码（本任务新增部分）。

**这个文件里没有专业语义。** 六个能力的专业判断在最终 FP Seam 与六个能力应用里，
M3 的周期判断在最终 FP M3 里，M1 的上下文编译在 m1_context_compiler_v0.1.py 里
（新画布逐字节复用，不重写）。本文件只做三件统一 Canvas 该做的事：

  1. `ROUTE_SRC`    读 M1 已经算出的 call_intent，挑出本轮要进的那一个能力。
                    不做自然语言理解、不做意图识别、不替用户选能力。
  2. `CTX_SRC`      把 M2 的只读响应照抄成 M3 认得的 account_context，并按 M3 契约
                    组装 <<REFERENCE_MANIFEST>>。查不到就写「查不到」，不留空。
  3. `DELIVERY_SRC` 只投影 user_delivery，并挡住内部状态词/字段/ID 泄漏。

节点源码以字符串形式嵌入 Dify Code 节点，与 M1 的做法一致。
"""

# ---------------------------------------------------------------- 1. 路由
ROUTE_SRC = r'''
import json
import re

# M4 冻结的六项能力。这份清单不是本节点的产品判断，是最终 FP Seam 的入参约束
# （capability 必须是六项之一），照抄。
CAP6 = ["MATRIX", "CAMPAIGN", "CONTENT_BRIEF", "CREATIVE_SCRIPT",
        "PRODUCTION_DIRECTOR", "PUBLISHING_PACKAGING"]

# M1 把它标成 BLOCKED / NO_PHYSICAL_ENTRY_YET，那是 M1 施工当时的**环境事实**：
# 那时候没有 M3 应用可调。现在有了（最终 FP M3）。物理入口存不存在属于路由层的
# 事实，不属于产品语义，所以在这里由统一 Canvas 认定，不回头改 M1 源码。
OPERATION = "SINGLE_ACCOUNT_OPERATION"


def main(call_intent_json, snapshot_json, user_query, ws_id, conv_id):
    try:
        ci = json.loads(call_intent_json or "{}")
    except Exception:
        ci = {}
    try:
        snap = json.loads(snapshot_json or "{}")
    except Exception:
        snap = {}

    needed = ci.get("needed_capabilities") or []
    if not isinstance(needed, list):
        needed = []

    # 保序取第一个落在六项之内的能力。M1 已经排好序，这里不重新排序、不加权、
    # 不"挑更合适的那个"——那是替用户做选择。
    picked = ""
    for c in needed:
        if c in CAP6:
            picked = c
            break

    wants_operation = OPERATION in needed

    task_text = ((snap.get("current_task") or {}).get("text")) or ""
    user_request = (user_query or "").strip()
    if task_text and task_text.strip() not in user_request:
        user_request = user_request + "\n\n【本任务已登记的诉求】" + task_text

    if picked:
        mode = "CAPABILITY"
    elif wants_operation:
        mode = "OPERATION_ONLY"
    else:
        mode = "DIALOGUE"

    # 会话级测试域标签。同一会话稳定，跨会话不同——测试数据因此天然按会话隔离。
    tag = re.sub(r"[^0-9a-zA-Z]", "", str(conv_id or ""))[:12] or "nosession"

    return {
        "tag": tag,
        "route_mode": mode,
        "has_capability": "true" if mode == "CAPABILITY" else "false",
        "runs_m3": "true" if mode in ("CAPABILITY", "OPERATION_ONLY") else "false",
        "target_capability": picked,
        # entry 故意留空：最终 FP Seam 自带确定性充分性规则来推导入口。
        # 在这里再算一遍就是把「哪个入口算合法等价输入」复制成第二套真源。
        "entry": "",
        "user_request": user_request,
        "needs_bootstrap": "true" if not (ws_id or "").strip() else "false",
        "route_note": "capability=%s；来源=M1.call_intent.needed_capabilities；"
                      "本节点未做意图识别、未替用户选择能力。" % (picked or "（本轮无）"),
    }
'''

# ---------------------------------------------------------------- 2. 上下文
CTX_SRC_TEMPLATE = r'''
import json

# M3 的方法参考正文。逐字节取自仓库，构建时嵌入，sha256 记在候选 Manifest 里，
# 由确定性检查比对仓库与图内两份是否仍然一致（载体副本的同步义务）。
_REFS = __REFS_JSON__
_REF_MANIFEST_LINES = __MANIFEST_LINES_JSON__


def _f(v, empty):
    """M2 返回什么就抄什么。查不到写「查不到」，不留空——
    「M2 里没有」和「这一侧没去问」是两件事，混在一起恢复场景就分不清。"""
    if v is None or v == "":
        return empty
    return v


def _body(raw):
    if isinstance(raw, dict):
        return raw
    try:
        return json.loads(raw or "{}")
    except Exception:
        return {}


def main(cyc_raw, cyc_status, dec_raw, dec_status, run_raw, run_status,
         material_text, snapshot_json, account_handle):
    cyc = _body(cyc_raw)
    dec = _body(dec_raw)
    run = _body(run_raw)
    try:
        snap = json.loads(snapshot_json or "{}")
    except Exception:
        snap = {}

    ok_c = str(cyc_status) == "200"
    ok_d = str(dec_status) == "200"
    ok_r = str(run_status) == "200"

    lines = [
        "【账号最小当前投影 · 来源 M2 服务实时读取】",
        "账号：测试账号 handle=%s，平台=test-platform" % (account_handle or "（未登记）"),
        "当前周期：%s" % (_f(cyc.get("label"), "（M2 未返回周期标签）") if ok_c
                     else "（M2 周期查询未成功，HTTP %s）" % cyc_status),
        "周期起始：%s" % (_f(cyc.get("start_at"), "（空）") if ok_c else "（未取到）"),
        "基线产能：%s（来源：%s）" % (_f(cyc.get("baseline_capacity"), "（空）"),
                              _f(cyc.get("baseline_capacity_source"), "（空）")),
        "预期发布条数：%s" % (_f(cyc.get("expected_publish_count"), "（空）"),),
        "最近一次周期决策：%s" % (_f(dec.get("decision"), "（本周期尚无决策记录）") if ok_d
                          else "（M2 决策查询未成功，HTTP %s）" % dec_status),
        "已发布内容与反馈：%s" % (_f(dec.get("based_on"), "（本周期尚无发布与反馈）") if ok_d
                          else "（未取到）"),
    ]
    if ok_r:
        lines += [
            "【本任务运行状态 · 来源 M2】",
            "上一步成功到：%s" % _f(run.get("last_success_step"), "（尚无成功步骤记录）"),
            "失败步骤：%s" % _f(run.get("failed_step"), "（无）"),
            "可从此处恢复：%s" % _f(run.get("resumable_from"), "（无）"),
            "已发生的写入副作用：%s" % json.dumps(run.get("side_effects") or [], ensure_ascii=False),
        ]
    else:
        lines.append("【本任务运行状态】（M2 运行状态查询未成功，HTTP %s；"
                     "因此本轮不声称任何写入已经发生）" % run_status)

    account_context = "\n".join(str(x) for x in lines)

    # 已登记事实：只来自用户这一轮真实提供的东西——上传资料原文，以及 M1 已登记的
    # 证据条目。系统不预置任何品牌事实；没有就是没有，由下游按缺口停。
    facts = []
    mt = (material_text or "").strip()
    if mt:
        facts.append("===== 用户本轮上传资料原文 =====\n" + mt)
    ev = snap.get("evidence_bundle") or []
    if isinstance(ev, list) and ev:
        rows = []
        for e in ev:
            if not isinstance(e, dict):
                continue
            rows.append("- [%s/%s] %s" % (e.get("nature") or "UNSTATED",
                                          e.get("scope") or "UNSTATED",
                                          e.get("text") or ""))
        if rows:
            facts.append("===== 用户在对话中说出口、已登记的事实与偏好 =====\n" + "\n".join(rows))
    registered_facts = "\n\n".join(facts)

    # M3 的参考资料信封闸门：要么给合法清单，要么显式传空。
    manifest = list(_REF_MANIFEST_LINES)
    bodies = []
    for path, body in _REFS:
        bodies.append("===== %s =====\n%s" % (path, body))
    if mt:
        manifest.append("user-material/uploaded-material.md: LOADED")
        bodies.append("===== user-material/uploaded-material.md =====\n" + mt)
    loaded_references = ("<<REFERENCE_MANIFEST>>\n" + "\n".join(manifest)
                        + "\n<<END_REFERENCE_MANIFEST>>\n\n"
                        + "\n\n".join(bodies))

    return {
        "account_context": account_context,
        "loaded_references": loaded_references,
        "registered_facts": registered_facts,
        "m2_reachable": "true" if (ok_c and ok_d) else "false",
        "m2_note": "cycles/current=%s decisions/latest=%s run-state=%s" % (
            cyc_status, dec_status, run_status),
    }
'''

# ---------------------------------------------------------------- 3. 用户投影
DELIVERY_SRC = r'''
import json
import re

# 只有 user_delivery 能直接给用户看（M5 运行时 USER_VISIBLE 的同一条纪律）。
# artifact / binding / trace / 枚举 / 节点名 / app_id 一律不出现在对话里。

# 内部状态词。命中就换成大白话，不是删掉——删掉会让"没查到"看起来像"没问题"。
_STATE_WORDS = [
    (r"\bDELIVERED_AFTER_RECOVERY\b", "（已完成，中途恢复过一次）"),
    (r"\bDELIVERED\b", "（已完成）"),
    (r"\bINPUT_INSUFFICIENT\b", "（输入还不够）"),
    (r"\bNOT_VERIFIED\b", "（还没核实）"),
    (r"\bNOT_APPLICABLE\b", "（这一项用不上）"),
    (r"\bNOT_STARTED\b", "（还没开始）"),
    (r"\bIN_PROGRESS\b", "（进行中）"),
    (r"\bCOMPLETED\b", "（已完成）"),
    (r"\bREADY\b", "（可以往下走了）"),
    (r"\bSTALE\b", "（需要重新确认）"),
    (r"\bCURRENT\b", "（是最新的）"),
    (r"\bBLOCKED\b", "（卡住了）"),
    (r"\bPARTIAL\b", "（只完成了一部分）"),
    (r"\bUNKNOWN\b", "（不确定）"),
    (r"\bPASS\b", "（通过）"),
    (r"\bFAIL(ED)?\b", "（没通过）"),
]
# 内部标识：能力枚举、入口号、节点名、UUID、内部字段名。一律不该出现在用户面前。
_IDENTIFIERS = [
    r"\bENTRY-\d{2}\b",
    r"\b(MATRIX|CAMPAIGN|CONTENT_BRIEF|CREATIVE_SCRIPT|PRODUCTION_DIRECTOR|"
    r"PUBLISHING_PACKAGING|SINGLE_ACCOUNT_OPERATION|CREATIVE_TOURNAMENT)\b",
    r"\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b",
    r"\b(uapp_[a-z_]+|m1_[a-z_]+|boot_[a-z_]+)\b",
    r"\b(capability_call|professional_input|business_delivery_outcome|user_delivery|"
    r"returns_json|binding_json|seam_trace_json|snapshot_json|call_intent_json|"
    r"loaded_references|account_context|operating_judgment|cycle_state_carry|"
    r"gate_status|extraction_gaps_text|registered_facts)\b",
    # 通用兜底：裸 snake_case 一律是内部字段名，不是中文交付正文该有的东西。
    # 具体触发例：audience_problem / expected_change / content_promise /
    # expression_subject_and_boundary（TRIAGE-001 实测泄漏）。
    r"\b[a-z][a-z0-9]*(?:_[a-z0-9]+)+\b",
    r"<think>|</think>",
    r"<<REFERENCE_MANIFEST>>|<<END_REFERENCE_MANIFEST>>",
]

_CAP_CN = {
    "MATRIX": "账号架构与诊断",
    "CAMPAIGN": "单次经营任务策划",
    "CONTENT_BRIEF": "内容契约（Content Brief）",
    "CREATIVE_SCRIPT": "创意与脚本",
    "PRODUCTION_DIRECTOR": "拍摄与制作方案",
    "PUBLISHING_PACKAGING": "发布包装",
}


def _scrub(text):
    """返回 (清洗后的文本, 命中清单)。命中清单只进内部通道，不给用户看。"""
    hits = []
    out = text or ""
    for pat, repl in _STATE_WORDS:
        found = re.findall(pat, out)
        if found:
            hits.append(pat)
            out = re.sub(pat, repl, out)
    for pat in _IDENTIFIERS:
        found = re.findall(pat, out)
        if found:
            hits.append(pat)
            out = re.sub(pat, "", out)
    # 清洗可能留下多余空白，收一下；不改动正文内容本身。
    out = re.sub(r"[ \t]{2,}", " ", out)
    out = re.sub(r"\n{3,}", "\n\n", out)
    return out.strip(), hits


def main(capability, seam_user_delivery, seam_outcome, seam_returns_json,
         m3_judgment, m3_gate_status, route_mode, m2_note, hop_gaps_text):
    modules = ["M1 任务上下文"]
    if route_mode in ("CAPABILITY", "OPERATION_ONLY"):
        modules += ["M2 当前投影", "M3 单账号持续运营"]
    if route_mode == "CAPABILITY":
        modules += ["M5 跨能力接缝抽取", "M4 统一能力接缝 → " + (_CAP_CN.get(capability) or capability)]

    # 组件级 Return：这一支停了，说清楚缺什么，不当成整任务失败，也不假装完成。
    gaps = []
    try:
        arr = json.loads(seam_returns_json or "[]")
        if isinstance(arr, list):
            for r in arr:
                if isinstance(r, dict) and r.get("precise_gap"):
                    gaps.append(str(r.get("precise_gap")))
    except Exception:
        pass

    delivered = seam_outcome in ("DELIVERED", "DELIVERED_AFTER_RECOVERY")
    body = (seam_user_delivery or "").strip()

    if route_mode == "OPERATION_ONLY":
        body = (m3_judgment or "").strip()
        delivered = bool(body)

    # user_delivery 是能力侧唯一指定给用户看的字段。它非空就用它——本画布再写一份
    # "缺口说明"，只会把能力已经组织好的自然语言换成给机器看的字段名（TRIAGE-001）。
    if body and (delivered or gaps):
        final = body
    elif body:
        # 有正文、既没交付判定也没缺口：如实说，不把「跑完了」说成「做好了」。
        final = body + "\n\n（上面这部分我还没能确认已经完整完成，先给你看当前结果。）"
    elif gaps:
        # 能力没写面向用户的正文，才由这里兜底。字段名一律经 _scrub 清洗后再出。
        final = ("这一步先停在这里，因为还差一件关键的事：\n\n" + "\n".join("· " + g for g in gaps)
                 + "\n\n补上之后我接着往下做，前面已经完成的部分不用重来。")
    else:
        final = ("这一步没有产出可以交给你的内容。原始运行记录已经保留，"
                 "没有被删掉，也没有被改写成完成。"
                 + (("\n还缺：" + hop_gaps_text) if (hop_gaps_text or "").strip() else ""))

    final, hits = _scrub(final)
    if not final:
        final = "这一步没有产出可以交给你的内容，原始记录已保留。"

    return {
        "final_text": final,
        "delivered_flag": "true" if delivered else "false",
        "modules_actually_run": json.dumps(modules, ensure_ascii=False),
        # 内部通道：泄漏命中如实登记，不面向用户。零命中才算 AC-10 成立。
        "leak_hits_json": json.dumps(hits, ensure_ascii=False),
        "leak_hit_count": str(len(hits)),
        "m2_note": m2_note or "",
    }
'''

# ---------------------------------------------------------------- 4. 组件失败
TOOLFAIL_SRC = r'''
def main(which, error_text):
    # 传输/平台故障。不猜原因，不说"可能是网络问题"，也不把失败说成业务结论。
    return {
        "final_text": "这一步没能跑完，是系统这边的调用出了问题，不是你的输入有问题。"
                      "已经完成的部分都还在，你可以直接说一声我就从这里接着做。",
        "failed_stage": which,
        "error_kept": (error_text or "")[:500],
    }
'''

# ---------------------------------------------------------------- 5. 测试域建域
# 一份源码给五个解析节点共用：M2 每一步都把新对象的主键放在 `id` 里，所以
# "取 id + 拼下一跳的 body" 这件事五步是同一件事，写五遍只会多五份漂移风险。
# 各节点只声明自己能看见的上游变量，看不见的用默认值补齐（A5：没差别就不该存在）。
BOOT_SRC = r'''
import json
import time


def main(raw, tag, ws_id="", account_id="", cycle_id=""):
    try:
        b = json.loads(raw or "{}")
    except Exception:
        b = {}
    oid = b.get("id") or ""
    now = time.strftime("%Y-%m-%dT%H:%M:%S+00:00", time.gmtime())
    return {
        "id": oid,
        "ok": "true" if oid else "false",
        "now": now,
        "actor": "uapp-" + tag,
        "ws_body": json.dumps({
            "name": "ws-uapp-" + tag, "kind": "personal", "owner_user_id": oid,
        }, ensure_ascii=False),
        "acct_body": json.dumps({
            "platform": "test-platform", "handle": "uapp-" + tag,
        }, ensure_ascii=False),
        # oid 在这一步是账号 id（上一跳建的就是账号）。
        "cycle_body": json.dumps({
            "idempotency_key": "cyc-" + tag, "account_id": oid,
            "label": "本周期", "start_at": now,
        }, ensure_ascii=False),
        # oid 在这一步是周期 id；账号 id 由更早那一步透传进来。
        "task_body": json.dumps({
            "idempotency_key": "task-" + tag, "account_id": account_id,
            "cycle_id": oid, "kind": "uapp-session",
        }, ensure_ascii=False),
    }
'''
