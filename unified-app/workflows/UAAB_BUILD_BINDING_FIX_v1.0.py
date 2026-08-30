#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""UAPP 已接受上游产物绑定｜Phase B 最小实现构建器。**零模型调用。**

只改 Phase A 确认的最高失效节点及其直接引用：

  1. uapp_persist        写入侧：单槽位无条件覆盖 → 按指纹分格的有界产物存储
  2. conversation.uapp_last_artifact   由「上一跳正文」改为该存储本身（仍然只有一处正文）
  3. uapp_pick_upstream  新增：确定性选择器，按冻结的合法性条件挑上游产物并现场复算摘要
  4. uapp_hop            取回接线由 conversation.uapp_last_artifact 改指选择器输出

不动 uapp_fields 的血缘门、不动 uapp_state 的账本、不动 Hop 抽取 Prompt、
不动 Seam、不动 M1/M2/M3、不动其余五能力、不动 PP。

为什么不新增会话变量：本会话已存在的 12 个变量与图里声明的 12 个一一对应，
新声明的变量不会为既有会话补建行，取回会 fail-open —— 风险不可接受。

    python3 UAAB_BUILD_BINDING_FIX_v1.0.py --dry-run
    python3 UAAB_BUILD_BINDING_FIX_v1.0.py --apply
"""
import argparse
import hashlib
import importlib.util
import io
import json
import os
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
UAPP = os.path.abspath(os.path.join(HERE, ".."))
REPO = os.path.abspath(os.path.join(UAPP, ".."))
EVDIR = os.path.join(UAPP, "evidence", "stages", "uapp_artifact_binding")
ENV = "/home/faye/diyu-demo-worktrees/m3-account-content-operator-v1/.env"
CAND = "85c01f85-a081-43e9-ab09-9993289cc200"
EXPECT_MD5_BEFORE = "99c3edf7bd12172a4fb011b588f25e57"

_s = importlib.util.spec_from_file_location(
    "dc", os.path.join(REPO, "account-operations/tools/dify_client.py"))
DC = importlib.util.module_from_spec(_s)
_s.loader.exec_module(DC)

# ---------------------------------------------------------------- 写入侧

PERSIST_CODE = r'''
import json
import re

MAX_ITEMS = 10
MAX_CHARS = 220000


def _norm(s):
    return re.sub(r"\s+", " ", s or "").strip()


def _fp(s):
    """与 uapp_state / uapp_fields 的 _fp 逐字相同：FNV-1a 64。沙箱里不用 hashlib。"""
    h = 0xcbf29ce484222325
    for b in (s or "").encode("utf-8"):
        h = ((h ^ b) * 0x100000001b3) & 0xFFFFFFFFFFFFFFFF
    return "%016x" % h


def _load_store(raw, prev_cap):
    """解析产物存储。容忍旧格式：整段裸正文按一条 legacy 条目收进来，不丢历史。"""
    s = (raw or "").strip()
    if not s:
        return {"v": 1, "items": []}, "EMPTY"
    if s.startswith("{"):
        try:
            o = json.loads(s)
            if isinstance(o, dict) and o.get("v") and isinstance(o.get("items"), list):
                return {"v": 1, "items": o["items"]}, "STORE"
        except Exception:
            pass
    n = _norm(s)
    return ({"v": 1, "items": [{"fp": _fp(n[:256]), "bfp": _fp(n), "cap": (prev_cap or "").strip(),
                                "turn": None, "task_key": None, "len": len(s), "nlen": len(n),
                                "body": s, "legacy": True}]}, "LEGACY_RAW")


def main(new_artifact, new_capability, prev_store, prev_capability, pending_state_json):
    store, load_mode = _load_store(prev_store, prev_capability)
    items = list(store["items"])

    try:
        st = json.loads(pending_state_json) if (pending_state_json or "").strip() else {}
    except Exception:
        st = {}
    if not isinstance(st, dict):
        st = {}
    rev = int(st.get("rev") or 0)
    ledger = {a.get("fp"): a for a in (st.get("artifacts") or []) if a.get("fp")}
    task_key = st.get("task_key")

    a = (new_artifact or "").strip()
    cap = (new_capability or "").strip()
    action = "NO_NEW_ARTIFACT"
    if a and cap:
        n = _norm(a)
        fp = _fp(n[:256])
        if any(it.get("fp") == fp for it in items):
            action = "ALREADY_PRESENT"
        else:
            items.append({"fp": fp, "bfp": _fp(n), "cap": cap, "turn": rev,
                          "task_key": task_key, "len": len(a), "nlen": len(n), "body": a})
            action = "APPENDED"

    # 保序裁剪：账本里 accepted 且未 STALE 的先保住，其余按新到旧保留。
    def protected(it):
        r = ledger.get(it.get("fp"))
        return bool(r and r.get("accepted") and not r.get("stale"))

    keep, spill = [], []
    for it in items:
        (keep if protected(it) else spill).append(it)
    room = max(0, MAX_ITEMS - len(keep))
    keep = keep + spill[-room:] if room else keep
    order = {id(it): i for i, it in enumerate(items)}
    keep.sort(key=lambda it: order.get(id(it), 0))
    dropped_for_count = len(items) - len(keep)

    total = sum(len(it.get("body") or "") for it in keep)
    dropped_for_size = 0
    while total > MAX_CHARS and len(keep) > 1:
        victim = None
        for it in keep:
            if not protected(it):
                victim = it
                break
        if victim is None:
            victim = keep[0]
        total -= len(victim.get("body") or "")
        keep.remove(victim)
        dropped_for_size += 1

    out = json.dumps({"v": 1, "items": keep}, ensure_ascii=False)
    note = ("存储 rev=%d 动作=%s 能力=%s 载入=%s 条目=%d 正文合计=%d 裁剪(条数)=%d 裁剪(体积)=%d"
            % (rev, action, cap or "-", load_mode, len(keep), total,
               dropped_for_count, dropped_for_size))
    return {"store_to_persist": out,
            "capability_to_persist": cap or (prev_capability or ""),
            "persist_action": action,
            "store_note": note,
            "store_item_count": str(len(keep))}
'''

# ---------------------------------------------------------------- 选择侧

PICK_CODE = r'''
import json
import re

# 与 uapp_fields 逐字相同的接受词与否定词。选择器**不写账本**，
# 只为本轮绑定决策镜像同一条权威规则；账本的唯一写入者仍是 uapp_fields + uapp_state。
ACCEPT = ["可以", "行", "没问题", "通过", "认可", "就按这个", "照这个", "就这个", "定了", "OK", "ok"]
NEGATE = "不别未没无"

# 目标能力 → 允许的上游能力（按优先级）。永不含目标能力自身。
COMPAT = {
    "PUBLISHING_PACKAGING": ["PRODUCTION_DIRECTOR", "CREATIVE_SCRIPT"],
    "PRODUCTION_DIRECTOR": ["CREATIVE_SCRIPT"],
    "CREATIVE_SCRIPT": ["CONTENT_BRIEF"],
}
# 用户原话点名某个上游时，只认该能力
MENTION = [
    (["制作方案", "拍摄方案", "制作安排", "拍摄安排", "怎么拍", "导演"], "PRODUCTION_DIRECTOR"),
    (["口播稿", "逐字稿", "脚本"], "CREATIVE_SCRIPT"),
    (["制作依据", "内容简报"], "CONTENT_BRIEF"),
]


def _norm(s):
    return re.sub(r"\s+", " ", s or "").strip()


def _fp(s):
    h = 0xcbf29ce484222325
    for b in (s or "").encode("utf-8"):
        h = ((h ^ b) * 0x100000001b3) & 0xFFFFFFFFFFFFFFFF
    return "%016x" % h


def _accepts(uq):
    """与 uapp_fields._accepts 逐字相同。"""
    s = _norm(uq)
    bound = "，。；！？,.;!? 、：:"
    for t in ACCEPT:
        i = 0
        while True:
            i = s.find(t, i)
            if i < 0:
                break
            pre_ok = (i == 0) or (s[i - 1] not in NEGATE)
            if len(t) == 1:
                pre_ok = pre_ok and (i == 0 or s[i - 1] in bound)
                nxt = s[i + 1:i + 2]
                pre_ok = pre_ok and (nxt == "" or nxt in bound)
            if pre_ok:
                return t
            i += 1
    return ""


def _fail(status, question, note):
    return {"upstream_delivery": "", "upstream_capability": "",
            "selection_status": status, "selected_fp": "", "selected_bfp": "",
            "selected_capability": "", "selection_question": question,
            "selection_note": note}


def main(store_json, state_json, target_capability, user_request, task_key):
    tgt = (target_capability or "").strip()
    uq = user_request or ""
    tk = (task_key or "").strip()

    try:
        store = json.loads(store_json) if (store_json or "").strip().startswith("{") else {}
    except Exception:
        store = {}
    items = store.get("items") if isinstance(store, dict) else None
    items = items if isinstance(items, list) else []

    try:
        st = json.loads(state_json) if (state_json or "").strip() else {}
    except Exception:
        st = {}
    arts = (st.get("artifacts") or []) if isinstance(st, dict) else []
    ledger_task = (st.get("task_key") or "").strip()

    allowed = COMPAT.get(tgt, [])
    if not allowed:
        return _fail("NO_UPSTREAM_REQUIRED", "",
                     "目标能力 %s 不从上游产物取正文" % (tgt or "-"))

    # 1. 本轮接受事件：镜像 uapp_fields 第 4 节 —— 接受词标记**最近一份未接受**的产物
    tok = _accepts(uq)
    accepted_now_fp = ""
    if tok:
        for a in reversed(arts):
            if not a.get("accepted"):
                accepted_now_fp = a.get("fp") or ""
                break

    # 2. 用户点名了哪个上游能力
    n_uq = _norm(uq)
    named = ""
    for words, capname in MENTION:
        if any(w in n_uq for w in words):
            named = capname
            break
    if named and named not in allowed:
        return _fail("NAMED_UPSTREAM_INCOMPATIBLE",
                     "你说的是 %s 的产物，但这一步要的是能作为 %s 输入的上游产物。"
                     "要我先回到 %s 吗？" % (named, tgt, named),
                     "点名能力 %s 不在 %s 的兼容清单 %s 内" % (named, tgt, allowed))
    order = [named] if named else allowed

    # 3. 逐条判合法性
    bodies = {}
    for it in items:
        if it.get("fp"):
            bodies[it["fp"]] = it
    cands, rej = [], []
    for a in arts:
        fp = a.get("fp") or ""
        cap = a.get("cap") or ""
        why = ""
        if cap == tgt:
            why = "SELF_UPSTREAM_FORBIDDEN"
        elif cap not in order:
            why = "CAPABILITY_INCOMPATIBLE"
        elif tk and (a.get("task_key") or ledger_task) and \
                (a.get("task_key") or ledger_task) != tk:
            why = "CROSS_TASK"
        elif not (a.get("accepted") or fp == accepted_now_fp):
            why = "NOT_ACCEPTED"
        elif a.get("stale"):
            why = "STALE"
        elif fp not in bodies:
            why = "BODY_UNRETRIEVABLE"
        else:
            it = bodies[fp]
            body = it.get("body") or ""
            nb = _norm(body)
            if _fp(nb[:256]) != fp:
                why = "FP_MISMATCH"
            elif it.get("bfp") and _fp(nb) != it.get("bfp"):
                why = "BODY_DIGEST_MISMATCH"
            elif it.get("cap") and it.get("cap") != cap:
                why = "CAPABILITY_IDENTITY_CONFLICT"
        if why:
            rej.append({"fp": fp, "cap": cap, "turn": a.get("turn"), "why": why})
        else:
            cands.append({"fp": fp, "cap": cap, "turn": a.get("turn") or 0,
                          "accepted_now": fp == accepted_now_fp})

    if not cands:
        gap = "content_body_or_beats" if tgt == "PUBLISHING_PACKAGING" \
            else "script_or_equivalent_beats"
        want = "／".join(order)
        return _fail("NO_LEGAL_UPSTREAM",
                     "这一步要用到已经确认过的%s产物，但我这边取不到它的正文。"
                     "把它给我，或者说一句「上一版可以」让我用已有的那份。" % want,
                     "无合法候选。逐条拒绝原因：%s；缺口=%s"
                     % (json.dumps(rej, ensure_ascii=False), gap))

    # 4. 按能力优先级取，再取最近一份（§6.2.2）
    best_cap = None
    for capname in order:
        if any(c["cap"] == capname for c in cands):
            best_cap = capname
            break
    if best_cap is None:
        # 候选非空但没有一条属于优先级清单：仍然 fail-closed，不猜、不崩。
        return _fail("NO_LEGAL_UPSTREAM",
                     "这一步要用到已经确认过的上游产物，但现有的几份都不能作为它的输入。"
                     "把需要的那份给我，或者告诉我先回到哪一步。",
                     "候选存在但均不在兼容优先级清单内：%s"
                     % json.dumps(cands, ensure_ascii=False))
    pool = [c for c in cands if c["cap"] == best_cap]
    top = max(c["turn"] for c in pool)
    tie = [c for c in pool if c["turn"] == top]
    if len(tie) > 1:
        return _fail("AMBIGUOUS",
                     "同一轮里有不止一份%s产物，我不替你挑。你要用哪一份？" % best_cap,
                     "并列候选：%s" % json.dumps(tie, ensure_ascii=False))

    sel = tie[0]
    it = bodies[sel["fp"]]
    note = ("选中 %s@turn%s fp=%s bfp=%s 正文 %d 字｜接受来源=%s｜点名=%s｜"
            "候选 %d 拒绝 %d｜拒绝原因=%s"
            % (sel["cap"], sel["turn"], sel["fp"], it.get("bfp"), len(it.get("body") or ""),
               ("本轮用户原话「%s」" % tok) if sel["accepted_now"] else "账本已接受",
               named or "无", len(cands), len(rej),
               json.dumps(rej, ensure_ascii=False)))
    return {"upstream_delivery": it.get("body") or "",
            "upstream_capability": sel["cap"],
            "selection_status": "SELECTED",
            "selected_fp": sel["fp"],
            "selected_bfp": it.get("bfp") or "",
            "selected_capability": sel["cap"],
            "selection_question": "",
            "selection_note": note}
'''


def psql(sql, db="dify"):
    p = subprocess.run(["docker", "exec", "-i", "docker-db_postgres-1", "psql", "-U", "postgres",
                        "-d", db, "-tA", "-c", sql], capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError("psql: " + (p.stderr or "")[:300])
    return p.stdout.strip()


def sha(s):
    return hashlib.sha256((s or "").encode("utf-8")).hexdigest()


def canon(o):
    return json.dumps(o, ensure_ascii=False, sort_keys=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    if not (a.dry_run or a.apply):
        raise SystemExit("必须显式选择 --dry-run 或 --apply")

    before_md5 = psql("select md5(w.graph) from workflows w join apps a on a.workflow_id=w.id "
                      "where a.id='%s';" % CAND)
    if before_md5 != EXPECT_MD5_BEFORE:
        raise SystemExit("现场候选画布图与冻结基线不一致，拒绝修改：%s" % before_md5)

    console = DC.Console(env=DC.load_env(ENV))
    st, draft = console.call("GET", "/console/api/apps/%s/workflows/draft" % CAND, timeout=300)
    assert st == 200, ("draft get", st, str(draft)[:300])
    graph = draft["graph"]
    before_nodes = json.loads(canon(graph["nodes"]))
    before_edges = json.loads(canon(graph["edges"]))
    N = {n["id"]: n for n in graph["nodes"]}
    assert "uapp_pick_upstream" not in N, "选择器已存在，拒绝重复构建"

    # ---- 1. 写入侧 ----
    p = N["uapp_persist"]["data"]
    p["code"] = PERSIST_CODE
    p["desc"] = ("按指纹分格的有界产物存储写入者。未接受的新产物不再覆盖已接受的旧正文；"
                 "账本里 accepted 且未 STALE 的条目优先保留")
    p["title"] = "闸门｜产物存储（按指纹分格）"
    p["variables"] = [
        {"value_selector": ["uapp_seam_merge", "artifact", "output"], "variable": "new_artifact"},
        {"value_selector": ["uapp_route", "target_capability"], "variable": "new_capability"},
        {"value_selector": ["conversation", "uapp_last_artifact"], "variable": "prev_store"},
        {"value_selector": ["conversation", "uapp_last_capability"],
         "variable": "prev_capability"},
        {"value_selector": ["uapp_fields", "pending_state_json"], "variable": "pending_state_json"},
    ]
    p["outputs"] = {k: {"children": None, "type": "string"}
                    for k in ("store_to_persist", "capability_to_persist", "persist_action",
                              "store_note", "store_item_count")}

    # uapp_save 的赋值来源改指新输出名
    for it in N["uapp_save"]["data"]["items"]:
        if it.get("variable_selector") == ["conversation", "uapp_last_artifact"]:
            it["value"] = ["uapp_persist", "store_to_persist"]

    # ---- 2. 选择器节点 ----
    hop = N["uapp_hop"]
    pick = {
        "id": "uapp_pick_upstream", "type": "custom",
        "position": {"x": hop["position"]["x"] - 320, "y": hop["position"]["y"] + 160},
        "positionAbsolute": {"x": hop["positionAbsolute"]["x"] - 320,
                             "y": hop["positionAbsolute"]["y"] + 160},
        "width": 244, "height": 98, "selected": False,
        "sourcePosition": "right", "targetPosition": "left", "zIndex": 0,
        "data": {
            "type": "code", "code_language": "python3",
            "title": "选择｜合法已接受上游产物",
            "desc": ("确定性选择：同 task、已接受、未 STALE、能力兼容、正文可取回且摘要现场复算一致。"
                     "取不到就 fail-closed 只问一个问题，不用最近一次任意产物顶替"),
            "code": PICK_CODE,
            "variables": [
                {"value_selector": ["conversation", "uapp_last_artifact"],
                 "variable": "store_json"},
                {"value_selector": ["conversation", "uapp_task_fields"], "variable": "state_json"},
                {"value_selector": ["uapp_route", "target_capability"],
                 "variable": "target_capability"},
                {"value_selector": ["uapp_route", "user_request"], "variable": "user_request"},
                {"value_selector": ["conversation", "uapp_task"], "variable": "task_key"},
            ],
            "outputs": {k: {"children": None, "type": "string"}
                        for k in ("upstream_delivery", "upstream_capability", "selection_status",
                                  "selected_fp", "selected_bfp", "selected_capability",
                                  "selection_question", "selection_note")},
            "selected": False,
        },
    }
    graph["nodes"].append(pick)

    # ---- 3. 边：uapp_op_gate --capability--> uapp_pick_upstream --> uapp_hop ----
    old_edge = None
    for e in graph["edges"]:
        if e["source"] == "uapp_op_gate" and e["target"] == "uapp_hop":
            old_edge = e
    assert old_edge is not None, "未找到 uapp_op_gate → uapp_hop 的边"
    tmpl = json.loads(json.dumps(old_edge))
    old_edge["target"] = "uapp_pick_upstream"
    old_edge["id"] = "uapp_op_gate-capability-uapp_pick_upstream"
    if isinstance(old_edge.get("data"), dict):
        old_edge["data"]["targetType"] = "code"
    e2 = tmpl
    e2["id"] = "uapp_pick_upstream-source-uapp_hop"
    e2["source"] = "uapp_pick_upstream"
    e2["sourceHandle"] = "source"
    e2["target"] = "uapp_hop"
    if isinstance(e2.get("data"), dict):
        e2["data"]["sourceType"] = "code"
        e2["data"]["targetType"] = "tool"
    graph["edges"].append(e2)

    # ---- 4. 取回接线 ----
    tp = hop["data"]["tool_parameters"]
    assert tp["upstream_delivery"]["value"] == "{{#conversation.uapp_last_artifact#}}"
    assert tp["upstream_capability"]["value"] == "{{#conversation.uapp_last_capability#}}"
    tp["upstream_delivery"]["value"] = "{{#uapp_pick_upstream.upstream_delivery#}}"
    tp["upstream_capability"]["value"] = "{{#uapp_pick_upstream.upstream_capability#}}"

    # ---- 5. 会话变量语义更新（不新增变量）----
    cvs = draft.get("conversation_variables") or []
    cv_changed = []
    for v in cvs:
        if isinstance(v, dict) and v.get("name") == "uapp_last_artifact":
            v["description"] = ("本会话的产物存储（JSON）：按指纹分格保存各能力交付的正文本体，"
                                "是正文的唯一真源。合法性由账本 uapp_task_fields 裁定，"
                                "取回由 uapp_pick_upstream 确定性选择并现场复算摘要。")
            cv_changed.append("uapp_last_artifact")

    # ---- 影响面核算 ----
    after_nodes = json.loads(canon(graph["nodes"]))
    touched = []
    bmap = {n["id"]: n for n in before_nodes}
    for n in after_nodes:
        b = bmap.get(n["id"])
        if b is None:
            touched.append(n["id"] + "(NEW)")
        elif canon(b) != canon(n):
            touched.append(n["id"])
    expect = sorted(["uapp_persist", "uapp_save", "uapp_hop", "uapp_pick_upstream(NEW)"])
    edge_ids_before = sorted(e["id"] for e in before_edges)
    edge_ids_after = sorted(e["id"] for e in graph["edges"])
    rep = {"document": {"id": "UAAB_BUILD_BINDING_FIX_v1.0",
                        "task_id": "DIYU-V1-UAPP-ACCEPTED-ARTIFACT-BINDING-001",
                        "model_calls": 0},
           "graph_md5_before": before_md5,
           "nodes_touched": sorted(touched),
           "nodes_touched_expected": expect,
           "impact_surface_exact": sorted(touched) == expect,
           "node_count": {"before": len(before_nodes), "after": len(graph["nodes"])},
           "edge_count": {"before": len(before_edges), "after": len(graph["edges"])},
           "edges_added": [i for i in edge_ids_after if i not in edge_ids_before],
           "edges_removed": [i for i in edge_ids_before if i not in edge_ids_after],
           "conversation_variables_added": [],
           "conversation_variables_description_updated": cv_changed,
           "persist_code_sha256": sha(PERSIST_CODE),
           "pick_code_sha256": sha(PICK_CODE),
           "hop_rewired": {"upstream_delivery": tp["upstream_delivery"]["value"],
                           "upstream_capability": tp["upstream_capability"]["value"]},
           "untouched_assert": {
               "uapp_fields": canon(bmap["uapp_fields"]) == canon(
                   [n for n in after_nodes if n["id"] == "uapp_fields"][0]),
               "uapp_state": canon(bmap["uapp_state"]) == canon(
                   [n for n in after_nodes if n["id"] == "uapp_state"][0]),
               "uapp_seam": canon(bmap["uapp_seam"]) == canon(
                   [n for n in after_nodes if n["id"] == "uapp_seam"][0]),
               "uapp_m3": canon(bmap["uapp_m3"]) == canon(
                   [n for n in after_nodes if n["id"] == "uapp_m3"][0]),
               "uapp_route": canon(bmap["uapp_route"]) == canon(
                   [n for n in after_nodes if n["id"] == "uapp_route"][0]),
               "uapp_delivery": canon(bmap["uapp_delivery"]) == canon(
                   [n for n in after_nodes if n["id"] == "uapp_delivery"][0]),
               "m1_compiler": canon(bmap["m1_compiler"]) == canon(
                   [n for n in after_nodes if n["id"] == "m1_compiler"][0])},
           "applied": False}

    if sorted(touched) != expect:
        raise SystemExit("影响面超出预期，拒绝写入：%s" % sorted(touched))
    if not all(rep["untouched_assert"].values()):
        raise SystemExit("受保护节点被动过，拒绝写入：%s" % rep["untouched_assert"])
    if len(graph["edges"]) != len(before_edges) + 1:
        raise SystemExit("边数变化超出预期，拒绝写入")

    if a.apply:
        st, res = console.call("POST", "/console/api/apps/%s/workflows/draft" % CAND, body={
            "graph": graph, "features": draft.get("features") or {},
            "hash": draft.get("hash"),
            "environment_variables": draft.get("environment_variables") or [],
            "conversation_variables": cvs}, timeout=900)
        assert st == 200, ("draft sync", st, str(res)[:400])
        rep["applied"] = True
        rep["draft_synced"] = True

    os.makedirs(EVDIR, exist_ok=True)
    io.open(os.path.join(EVDIR, "UAAB_BUILD_BINDING_FIX.json"), "w",
            encoding="utf-8").write(json.dumps(rep, ensure_ascii=False, indent=1) + "\n")
    print(json.dumps({k: v for k, v in rep.items() if k != "document"},
                     ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
