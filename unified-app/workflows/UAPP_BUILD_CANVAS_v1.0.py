#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""构建并发布「DIYU V1 · Unified Founder Canvas」（advanced-chat）。

task_id: DIYU-V1-UNIFIED-DIFY-APPLICATION-001

三条构建纪律，都是合同硬约束不是风格选择：

1. **M1 子图逐字节复用。** m1_extract / m1_join / m1_shadow / m1_compiler /
   m1_save_snapshot 直接从已发布的 M1 候选应用图里原样取出（节点 id 一并保留，
   于是节点内部所有 value_selector 无需改写就仍然有效）。这就是 H2 的成立方式：
   等价性由**构造**保证，不是由再实现之后的行为比对保证。

2. **专业语义不进画布。** 六个能力的路由与判断留在最终 FP Seam；周期判断留在
   最终 FP M3；本画布只做「读 M1 已算出的 call_intent → 挑一个能力 → 传给接缝」。

3. **旧资产零改动。** 旧 Founder Canvas、旧 provider、最终 FP 八应用只读不写。
"""
import hashlib
import importlib.util
import io
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
ENV = "/home/faye/diyu-demo-worktrees/m3-account-content-operator-v1/.env"


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


DC = _load("uapp_dify_client", os.path.join(ROOT, "account-operations", "tools", "dify_client.py"))
NODES = _load("uapp_nodes", os.path.join(HERE, "UAPP_CANVAS_NODES_v1.0.py"))

APP_NAME = "DIYU V1 · Unified Founder Canvas"
M1_SOURCE_APP = "dd638b91-d39f-4e92-a984-6ad1ab809119"     # M1 候选，只读取节点
M2_BASE = "http://diyu-m2-app:8000"

PROVIDER_M3 = "9ea86217-8791-489c-9a96-b880ae558ac5"
PROVIDER_HOP = "fd3f6f29-237f-4bbe-a820-5d38076ab52e"
PROVIDER_SEAM = "f8d63527-8c45-4823-8159-443cef37240d"
TOOL_M3, TOOL_HOP, TOOL_SEAM = "diyu_uapp_m3", "diyu_uapp_hop", "diyu_uapp_seam"

# M3 的方法参考。构建时读仓库、嵌进图；哈希记进 Manifest，由确定性检查比对两份载体。
M3_REF_DIR = os.path.join(ROOT, "m3-account-content-operator-semantic-v1.0",
                          "skill-source", "references")
M3_REFERENCES = [
    ("references/fashion-and-market.md", "fashion-and-market.md", True),
    ("references/six-skill-methods.md", "six-skill-methods.md", True),
    ("references/operations.md", "operations.md", True),
    # M3 自己的验收夹具，含期望答案；加载进正式运行会污染取证。如实声明未加载。
    ("references/acceptance-fixtures.md", "acceptance-fixtures.md", False),
]


def psql(sql, db="dify"):
    p = subprocess.run(["docker", "exec", "-i", "docker-db_postgres-1", "psql", "-U", "postgres",
                        "-d", db, "-tA", "-c", sql], capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError("psql failed: " + (p.stderr or "")[:400])
    return p.stdout.strip()


def m1_assets():
    """从已发布的 M1 候选应用取出可逐字节复用的子图、会话变量与 features。"""
    g = json.loads(psql("select w.graph from workflows w join apps a on a.workflow_id=w.id "
                        "where a.id='%s';" % M1_SOURCE_APP))
    cv = json.loads(psql("select w.conversation_variables from workflows w "
                         "join apps a on a.workflow_id=w.id where a.id='%s';" % M1_SOURCE_APP))
    ft = json.loads(psql("select w.features from workflows w join apps a on a.workflow_id=w.id "
                         "where a.id='%s';" % M1_SOURCE_APP))
    nodes = {n["id"]: n for n in g["nodes"]}
    return nodes, cv, ft


def build_refs():
    """返回 (清单行, [(path, body)], 逐项哈希)。"""
    lines, bodies, digests = [], [], []
    for manifest_path, fname, load in M3_REFERENCES:
        fp = os.path.join(M3_REF_DIR, fname)
        raw = io.open(fp, "rb").read()
        sha = hashlib.sha256(raw).hexdigest()
        lines.append("%s: %s" % (manifest_path, "LOADED" if load else "NOT_LOADED"))
        digests.append({"path": manifest_path, "file": fname, "status": "LOADED" if load else "NOT_LOADED",
                        "sha256": sha, "bytes": len(raw)})
        if load:
            bodies.append([manifest_path, raw.decode("utf-8")])
    return lines, bodies, digests


# ================================================================ 画布原语
_TYPES = {}


def N(id_, x, y, data, w=244, h=98):
    _TYPES[id_] = data["type"]
    return {"id": id_, "position": {"x": x, "y": y}, "positionAbsolute": {"x": x, "y": y},
            "selected": False, "sourcePosition": "right", "targetPosition": "left",
            "type": "custom", "width": w, "height": h, "zIndex": 0, "data": data}


def E(s, t, handle="source"):
    return {"id": "%s-%s-%s" % (s, handle, t), "type": "custom", "source": s, "target": t,
            "sourceHandle": handle, "targetHandle": "target", "zIndex": 0,
            "data": {"isInIteration": False, "isInLoop": False,
                     "sourceType": _TYPES.get(s, "code"), "targetType": _TYPES.get(t, "code")}}


def code(title, desc, src, variables, outputs):
    return {"type": "code", "title": title, "desc": desc, "code_language": "python3",
            "code": src, "variables": variables,
            "outputs": {k: {"type": "string", "children": None} for k in outputs},
            "selected": False}


def V(name, selector):
    return {"variable": name, "value_selector": selector}


def http(title, desc, method, url, body_tpl=None, actor=True, timeout_read=60,
         actor_tpl="{{#conversation.uapp_actor#}}"):
    # actor_tpl 存在的唯一理由：建域链跑到一半时 conversation.uapp_actor 还没被写入
    # （写它的 boot_assign 是建域链的最后一个节点），而 M2 对 workspace 作用域内的
    # 写入依约要求 X-Actor-Ref，空值一律 401。建域中途改取本链第一步算出的 actor。
    d = {"type": "http-request", "title": title, "desc": desc, "method": method, "url": url,
         "authorization": {"type": "no-auth", "config": None},
         "headers": (("X-Actor-Ref:" + actor_tpl) if actor else ""),
         "params": "", "selected": False,
         "timeout": {"connect": 10, "read": timeout_read, "write": 20},
         # 打不通就如实交出空 body 和非 200，由下游写「查不到」。
         # 不进 fail-branch，是因为「M2 没答」不该让整轮对话失败——它只让依赖 M2
         # 的那部分变成未知，其余照常（A3 按依赖边切分）。
         "error_strategy": "default-value",
         "default_value": [{"key": "body", "type": "string", "value": ""},
                           {"key": "status_code", "type": "number", "value": 0},
                           {"key": "headers", "type": "object", "value": {}},
                           {"key": "files", "type": "array[file]", "value": []}],
         "body": {"type": "none", "data": []}}
    if body_tpl is not None:
        d["body"] = {"type": "json", "data": [{"key": "", "type": "text", "value": body_tpl}]}
    return d


def tool(title, desc, provider_id, tool_name, params, retries=1):
    return {"type": "tool", "title": title, "desc": desc,
            "provider_id": provider_id, "provider_name": provider_id, "provider_type": "workflow",
            "tool_label": tool_name, "tool_name": tool_name, "tool_node_version": "2",
            "tool_configurations": {}, "selected": False,
            "error_strategy": "fail-branch",
            "retry_config": {"max_retries": retries, "retry_enabled": True, "retry_interval": 2000},
            "tool_parameters": {k: {"type": "mixed", "value": v} for k, v in params.items()}}


def ifelse(title, desc, case_id, selector, value):
    return {"type": "if-else", "title": title, "desc": desc, "selected": False,
            "logical_operator": "and",
            "cases": [{"case_id": case_id, "logical_operator": "and",
                       "conditions": [{"comparison_operator": "is", "value": value,
                                       "variable_selector": selector}]}]}


def answer(title, tpl):
    return {"type": "answer", "title": title, "desc": "", "answer": tpl,
            "variables": [], "selected": False}


def assigner(title, desc, items):
    return {"type": "assigner", "version": "2", "title": title, "desc": desc, "selected": False,
            "items": [{"input_type": it[0], "operation": "over-write", "write_mode": "over-write",
                       "value": it[1], "variable_selector": ["conversation", it[2]]} for it in items]}


# ================================================================ 画布
def build_graph():
    m1nodes, m1_convvars, m1_features = m1_assets()
    ref_lines, ref_bodies, ref_digests = build_refs()

    ctx_src = (NODES.CTX_SRC_TEMPLATE
               .replace("__REFS_JSON__", json.dumps(ref_bodies))
               .replace("__MANIFEST_LINES_JSON__", json.dumps(ref_lines)))

    nodes, edges = [], []
    X, Y = 40, 280

    # ---- 起点 + M1 子图（逐字节复用，节点 id 保持不变）----
    nodes.append(N("uapp_start", X, Y, {"type": "start", "title": "开始", "desc": "",
                                        "variables": [], "selected": False}))
    for i, nid in enumerate(("m1_extract", "m1_join", "m1_shadow", "m1_compiler",
                             "m1_save_snapshot")):
        src = m1nodes[nid]
        nodes.append(N(nid, X + 320 * (i + 1), Y, json.loads(json.dumps(src["data"])),
                       src.get("width", 244), src.get("height", 98)))
    for a, b in (("uapp_start", "m1_extract"), ("m1_extract", "m1_join"),
                 ("m1_join", "m1_shadow"), ("m1_shadow", "m1_compiler"),
                 ("m1_compiler", "m1_save_snapshot")):
        edges.append(E(a, b))

    # ---- 路由（只读 M1 已算出的 call_intent）----
    nodes.append(N("uapp_route", X + 1920, Y, code(
        "路由｜取 M1 已给出的能力调用意图",
        "只读 call_intent.needed_capabilities 挑一个能力；不做意图识别、不替用户选能力",
        NODES.ROUTE_SRC,
        [V("call_intent_json", ["m1_compiler", "call_intent_json"]),
         V("snapshot_json", ["m1_compiler", "snapshot_json"]),
         V("user_query", ["sys", "query"]),
         V("ws_id", ["conversation", "uapp_ws"]),
         V("conv_id", ["sys", "conversation_id"])],
        ["tag", "route_mode", "has_capability", "runs_m3", "target_capability", "entry",
         "user_request", "needs_bootstrap", "route_note"])))
    edges.append(E("m1_save_snapshot", "uapp_route"))

    # ---- 主闸门：要不要动业务链 ----
    nodes.append(N("uapp_gate", X + 2240, Y, ifelse(
        "本轮要动业务链吗", "M1 给出经营/能力诉求才进业务链；否则自然对话。这里不做意图识别。",
        "business", ["uapp_route", "runs_m3"], "true")))
    edges.append(E("uapp_route", "uapp_gate"))

    # ---- 自然对话分支 ----
    chat = json.loads(json.dumps(m1nodes["m1_chat_llm"]["data"]))
    chat["title"] = "回复｜自然对话"
    nodes.append(N("uapp_chat_llm", X + 2560, Y + 320, chat))
    nodes.append(N("uapp_chat_answer", X + 2880, Y + 320,
                   answer("回复｜对话", "{{#uapp_chat_llm.text#}}")))
    edges.append(E("uapp_gate", "uapp_chat_llm", "false"))
    edges.append(E("uapp_chat_llm", "uapp_chat_answer"))

    # ---- 测试域建域（只在本会话尚未建域时执行）----
    nodes.append(N("uapp_boot_gate", X + 2560, Y - 320, ifelse(
        "本会话已经有测试工作区了吗", "没有就建一个会话级测试域；有就直接用，不重复建。",
        "boot", ["uapp_route", "needs_bootstrap"], "true")))
    edges.append(E("uapp_gate", "uapp_boot_gate", "business"))

    boot_chain = [
        ("boot_user", http("建域｜登记使用者", "M2 用户", "post", M2_BASE + "/users",
                           '{"external_ref": "uapp-{{#uapp_route.tag#}}"}', actor=False),
         [V("raw", ["boot_user", "body"]), V("tag", ["uapp_route", "tag"])]),
        ("boot_ws", http("建域｜创建测试工作区", "M2 workspace", "post", M2_BASE + "/workspaces",
                         "{{#boot_p1.ws_body#}}", actor=False),
         [V("raw", ["boot_ws", "body"]), V("tag", ["uapp_route", "tag"])]),
        ("boot_acct", http("建域｜登记测试账号", "M2 account", "post",
                           M2_BASE + "/workspaces/{{#boot_p2.id#}}/accounts",
                           "{{#boot_p1.acct_body#}}", actor_tpl="{{#boot_p1.actor#}}"),
         [V("raw", ["boot_acct", "body"]), V("tag", ["uapp_route", "tag"])]),
        ("boot_cycle", http("建域｜开一个周期", "M2 cycle", "post",
                            M2_BASE + "/workspaces/{{#boot_p2.id#}}/cycles",
                            "{{#boot_p3.cycle_body#}}", actor_tpl="{{#boot_p1.actor#}}"),
         [V("raw", ["boot_cycle", "body"]), V("tag", ["uapp_route", "tag"])]),
        ("boot_task", http("建域｜开一个任务", "M2 task", "post",
                           M2_BASE + "/workspaces/{{#boot_p2.id#}}/tasks",
                           "{{#boot_p4.task_body#}}", actor_tpl="{{#boot_p1.actor#}}"),
         [V("raw", ["boot_task", "body"]), V("tag", ["uapp_route", "tag"]),
          V("account_id", ["boot_p3", "id"])]),
    ]
    prev = "uapp_boot_gate"
    handle = "boot"
    bx = X + 2560
    for i, (hid, hdata, pvars) in enumerate(boot_chain):
        pid = "boot_p%d" % (i + 1)
        if pid == "boot_p4":
            pvars = pvars + [V("account_id", ["boot_p3", "id"])]
        nodes.append(N(hid, bx + 320 * (2 * i), Y - 320, hdata))
        nodes.append(N(pid, bx + 320 * (2 * i + 1), Y - 320, code(
            "建域｜取回主键", "M2 每一步都把新对象主键放在 id 里；只取 id 和下一跳的 body",
            NODES.BOOT_SRC, pvars,
            ["id", "ok", "now", "actor", "ws_body", "acct_body", "cycle_body", "task_body"])))
        edges.append(E(prev, hid, handle))
        edges.append(E(hid, pid))
        prev, handle = pid, "source"

    nodes.append(N("boot_assign", bx + 320 * 10, Y - 320, assigner(
        "建域｜记住本会话的测试域", "会话级测试域标识写回会话变量，多轮不再重建",
        [("variable", ["boot_p2", "id"], "uapp_ws"),
         ("variable", ["boot_p3", "id"], "uapp_account"),
         ("variable", ["boot_p4", "id"], "uapp_cycle"),
         ("variable", ["boot_p5", "id"], "uapp_task"),
         ("variable", ["boot_p1", "actor"], "uapp_actor")])))
    edges.append(E("boot_p5", "boot_assign"))

    # ---- M2 只读当前投影（两条分支在此汇合，都读会话变量）----
    ws = "{{#conversation.uapp_ws#}}"
    acct = "{{#conversation.uapp_account#}}"
    task = "{{#conversation.uapp_task#}}"
    m2 = [
        ("uapp_m2_cycle", "读 M2｜当前周期", "get",
         M2_BASE + "/workspaces/%s/accounts/%s/cycles/current" % (ws, acct)),
        ("uapp_m2_dec", "读 M2｜最近一次周期决策", "get",
         M2_BASE + "/workspaces/%s/accounts/%s/cycles/decisions/latest" % (ws, acct)),
        ("uapp_m2_run", "读 M2｜本任务运行状态", "get",
         M2_BASE + "/workspaces/%s/tasks/%s/run-state" % (ws, task)),
    ]
    prev2 = None
    for i, (nid, title, method, url) in enumerate(m2):
        nodes.append(N(nid, X + 2880 + 320 * i, Y, http(title, "只读，不写", method, url)))
        if prev2:
            edges.append(E(prev2, nid))
        prev2 = nid
    # 建域分支与已建域分支在第一个 M2 读取节点汇合。
    edges.append(E("boot_assign", "uapp_m2_cycle"))
    edges.append(E("uapp_boot_gate", "uapp_m2_cycle", "false"))

    # ---- 组装 M3 的输入 ----
    nodes.append(N("uapp_ctx", X + 3840, Y, code(
        "组装｜M2 投影 → M3 输入", "照抄 M2 字段并按 M3 契约组装参考清单；查不到写查不到",
        ctx_src,
        [V("cyc_raw", ["uapp_m2_cycle", "body"]), V("cyc_status", ["uapp_m2_cycle", "status_code"]),
         V("dec_raw", ["uapp_m2_dec", "body"]), V("dec_status", ["uapp_m2_dec", "status_code"]),
         V("run_raw", ["uapp_m2_run", "body"]), V("run_status", ["uapp_m2_run", "status_code"]),
         V("material_text", ["m1_join", "material_text"]),
         V("snapshot_json", ["m1_compiler", "snapshot_json"]),
         V("account_handle", ["uapp_route", "tag"])],
        ["account_context", "loaded_references", "registered_facts", "m2_reachable", "m2_note"])))
    edges.append(E("uapp_m2_run", "uapp_ctx"))

    # ---- 最终 FP M3：周期判断 ----
    nodes.append(N("uapp_m3", X + 4160, Y, tool(
        "调用｜最终 FP M3 单账号持续运营", "周期判断与内容任务；专业判断在 M3 内，不在本画布",
        PROVIDER_M3, TOOL_M3,
        {"account_context": "{{#uapp_ctx.account_context#}}",
         "user_request": "{{#uapp_route.user_request#}}",
         "loaded_references": "{{#uapp_ctx.loaded_references#}}"})))
    edges.append(E("uapp_ctx", "uapp_m3"))

    # ---- 本轮要不要进专业能力 ----
    nodes.append(N("uapp_op_gate", X + 4480, Y, ifelse(
        "本轮要进专业能力吗", "只有 M1 点名了六项能力之一才进接缝；否则交付 M3 的运营判断。",
        "capability", ["uapp_route", "has_capability"], "true")))
    edges.append(E("uapp_m3", "uapp_op_gate"))

    # ---- 跨能力抽取 + 统一能力接缝 ----
    nodes.append(N("uapp_hop", X + 4800, Y, tool(
        "调用｜跨能力抽取适配", "按目标能力的必填清单从已登记来源抽取；只抽取不推断",
        PROVIDER_HOP, TOOL_HOP,
        {"target_capability": "{{#uapp_route.target_capability#}}",
         "m3_judgment": "{{#uapp_m3.operating_judgment#}}",
         "upstream_delivery": "{{#conversation.uapp_last_artifact#}}",
         "upstream_capability": "{{#conversation.uapp_last_capability#}}",
         "registered_facts": "{{#uapp_ctx.registered_facts#}}",
         "account_context": "{{#uapp_ctx.account_context#}}",
         "user_request": "{{#uapp_route.user_request#}}",
         "focus_fields": ""})))
    edges.append(E("uapp_op_gate", "uapp_hop", "capability"))

    nodes.append(N("uapp_seam", X + 5120, Y, tool(
        "调用｜最终 FP 统一能力接缝", "一次只进一个专业能力；入口由接缝自己的充分性规则推导",
        PROVIDER_SEAM, TOOL_SEAM,
        {"capability": "{{#uapp_route.target_capability#}}",
         "entry": "{{#uapp_route.entry#}}",
         "capability_call": "{{#uapp_hop.capability_call#}}",
         "professional_input": "{{#uapp_hop.professional_input#}}",
         "example_reference_requested": "NO"})))
    edges.append(E("uapp_hop", "uapp_seam"))

    # ---- 用户投影 ----
    nodes.append(N("uapp_delivery", X + 5440, Y, code(
        "投影｜只交自然语言，挡内部泄漏", "只呈现 user_delivery；状态词/字段/ID/节点名一律不出对话",
        NODES.DELIVERY_SRC,
        [V("capability", ["uapp_route", "target_capability"]),
         V("seam_user_delivery", ["uapp_seam", "user_delivery"]),
         V("seam_outcome", ["uapp_seam", "business_delivery_outcome"]),
         V("seam_returns_json", ["uapp_seam", "returns_json"]),
         V("m3_judgment", ["uapp_m3", "operating_judgment"]),
         V("m3_gate_status", ["uapp_m3", "gate_status"]),
         V("route_mode", ["uapp_route", "route_mode"]),
         V("m2_note", ["uapp_ctx", "m2_note"]),
         V("hop_gaps_text", ["uapp_hop", "extraction_gaps_text"])],
        ["final_text", "delivered_flag", "modules_actually_run", "leak_hits_json",
         "leak_hit_count", "m2_note"])))
    edges.append(E("uapp_seam", "uapp_delivery"))
    edges.append(E("uapp_op_gate", "uapp_delivery", "false"))

    nodes.append(N("uapp_save", X + 5760, Y, assigner(
        "记住｜本轮产物与能力", "供下一跳作为上游产出使用；不写业务真源，业务真源在 M2",
        [("variable", ["uapp_seam", "artifact"], "uapp_last_artifact"),
         ("variable", ["uapp_route", "target_capability"], "uapp_last_capability")])))
    edges.append(E("uapp_delivery", "uapp_save"))
    nodes.append(N("uapp_answer", X + 6080, Y,
                   answer("回复｜业务交付", "{{#uapp_delivery.final_text#}}")))
    edges.append(E("uapp_save", "uapp_answer"))

    # ---- 组件级传输失败：只影响这一支 ----
    nodes.append(N("uapp_toolfail", X + 5120, Y + 320, code(
        "组件失败｜只影响这一支", "不猜原因、不把传输失败说成业务结论",
        NODES.TOOLFAIL_SRC,
        [V("which", ["uapp_route", "target_capability"]),
         V("error_text", ["uapp_route", "route_note"])],
        ["final_text", "failed_stage", "error_kept"])))
    nodes.append(N("uapp_fail_answer", X + 5440, Y + 320,
                   answer("回复｜这一步没跑完", "{{#uapp_toolfail.final_text#}}")))
    for src in ("uapp_m3", "uapp_hop", "uapp_seam"):
        edges.append(E(src, "uapp_toolfail", "fail-branch"))
    edges.append(E("uapp_toolfail", "uapp_fail_answer"))

    graph = {"nodes": nodes, "edges": edges, "viewport": {"x": 0, "y": 0, "zoom": 0.4}}
    return graph, m1_convvars, m1_features, ref_digests


# ================================================================ 会话变量
def conversation_variables(console):
    """M1 的 snapshot_json 逐字节沿用；再加本任务自己的会话级测试域标识。

    形状不自己造：从 M1 已发布应用的 draft 里取回真实形状，只在同一形状上追加。
    """
    st, draft = console.call("GET", "/console/api/apps/%s/workflows/draft" % M1_SOURCE_APP)
    assert st == 200, ("read m1 draft", st, draft)
    base = draft.get("conversation_variables") or []
    if isinstance(base, dict):
        base = list(base.values())
    out = [json.loads(json.dumps(v)) for v in base]
    extra = [
        ("uapp_ws", "本会话测试工作区 id（M2）。业务真源在 M2，这里只存标识。"),
        ("uapp_account", "本会话测试账号 id（M2）。"),
        ("uapp_cycle", "本会话当前周期 id（M2）。"),
        ("uapp_task", "本会话任务 id（M2）。"),
        ("uapp_actor", "本会话调用者标识，作为 M2 的 X-Actor-Ref。"),
        ("uapp_last_artifact", "上一跳专业能力交付的产物本体，只作为下一跳的上游输入。"),
        ("uapp_last_capability", "上一跳交付产物的能力身份。"),
    ]
    for name, desc in extra:
        out.append({"id": str(__import__("uuid").uuid5(
            __import__("uuid").NAMESPACE_URL, "diyu-uapp-" + name)),
            "name": name, "value_type": "string", "value": "",
            "description": desc, "selector": ["conversation", name]})
    return out


# ================================================================ 部署
def main():
    console = DC.Console(env=DC.load_env(ENV))
    graph, _cv, m1_features, ref_digests = build_graph()
    convvars = conversation_variables(console)

    st, apps = console.call("GET", "/console/api/apps?page=1&limit=100")
    assert st == 200, (st, apps)
    hit = [a for a in apps["data"] if a.get("name") == APP_NAME]
    if hit:
        app_id = hit[0]["id"]
        action = "REUSED"
    else:
        st, app = console.call("POST", "/console/api/apps", body={
            "name": APP_NAME, "mode": "advanced-chat", "icon_type": "emoji", "icon": "🎯",
            "icon_background": "#E4FBCC",
            "description": "笛语 V1 统一入口：用自然语言完成经营判断、内容生产与反馈闭环。"})
        assert st in (200, 201), ("create app", st, app)
        app_id = app["id"]
        action = "CREATED"

    features = json.loads(json.dumps(m1_features))
    features["opening_statement"] = (
        "说说你现在要解决的经营问题就行——比如这周想让哪个账号做出什么变化。"
        "需要的资料可以直接上传，不用挑功能、不用填表格。")

    st, cur = console.call("GET", "/console/api/apps/%s/workflows/draft" % app_id)
    prev_hash = cur.get("hash") if st == 200 else None
    st, res = console.call("POST", "/console/api/apps/%s/workflows/draft" % app_id, body={
        "graph": graph, "features": features, "hash": prev_hash,
        "environment_variables": [], "conversation_variables": convvars}, timeout=600)
    assert st == 200, ("draft sync", st, json.dumps(res, ensure_ascii=False)[:800])

    st, pub = console.call("POST", "/console/api/apps/%s/workflows/publish" % app_id, body={
        "marked_name": os.environ.get("UAPP_MARK", "uapp-thin-slice-v1.0"),
        "marked_comment": "统一 Founder Canvas 最薄纵向切片：M1 子图逐字节复用 + M2 只读投影 "
                          "+ 最终 FP M3 + hop + 最终 FP Seam + 用户投影"}, timeout=600)
    assert st in (200, 201), ("publish", st, json.dumps(pub, ensure_ascii=False)[:800])

    report = {
        "app_name": APP_NAME, "app_id": app_id, "app_action": action,
        "transport": console.transport,
        "node_count": len(graph["nodes"]), "edge_count": len(graph["edges"]),
        "graph_sha256": hashlib.sha256(json.dumps(
            graph, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest(),
        "m1_subgraph_reused_verbatim": ["m1_extract", "m1_join", "m1_shadow", "m1_compiler",
                                        "m1_save_snapshot", "m1_chat_llm(as uapp_chat_llm)"],
        "providers": {"m3": PROVIDER_M3, "hop": PROVIDER_HOP, "seam": PROVIDER_SEAM},
        "m3_reference_digests": ref_digests,
        "conversation_variables": [v["name"] for v in convvars],
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    # 每次构建单独落一份，不覆盖历史构建证据。
    ev = os.path.join(HERE, "..", "evidence")
    n = 1
    while os.path.exists(os.path.join(ev, "UAPP_CANVAS_BUILD_%02d.json" % n)):
        n += 1
    report["build_attempt"] = n
    out = os.path.join(ev, "UAPP_CANVAS_BUILD_%02d.json" % n)
    with io.open(out, "w", encoding="utf-8") as fh:
        fh.write(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    return app_id


if __name__ == "__main__":
    main()
