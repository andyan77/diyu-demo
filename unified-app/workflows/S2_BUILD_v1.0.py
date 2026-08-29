#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Node S2｜在 S1 当前图上新增 M2 只读投影与任务域建域写入。

新增的唯一模块是 M2。业务事实、版本、幂等与副作用继续以现有 M2 FastAPI/PostgreSQL 为权威，
画布不复制业务语义、不建第二数据库。

分层纪律：
- 闲聊轮不进 M2（省一整条链）；只问一个的轮次也不进 M2（问一句话不需要业务事实）。
- 建域只在会话首轮发生；后续轮读会话变量，靠 needs_bootstrap 判定，天然幂等。
- M2 打不通或查不到，如实交出非 200 与空 body，由投影节点写「查不到」，
  **不把空响应升级成已知事实**；且只让依赖 M2 的那部分变未知，其余照常（A3 按依赖边切分）。
- 本层仍未接 M3/Hop/Seam，路线已定时继续如实交代，不承诺异步结果。
"""
import hashlib
import importlib.util
import io
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
ENV = "/home/faye/diyu-demo-worktrees/m3-account-content-operator-v1/.env"

S1 = importlib.util.spec_from_file_location("s1b", os.path.join(HERE, "S1_BUILD_v1.0.py"))
_S1 = importlib.util.module_from_spec(S1)
S1.loader.exec_module(_S1)

DC, NODES = _S1.DC, _S1.NODES
N, E, code, V, ifelse, answer = _S1.N, _S1.E, _S1.code, _S1.V, _S1.ifelse, _S1.answer
psql, m1_assets = _S1.psql, _S1.m1_assets

APP_ID = os.environ.get("S2_APP_ID", "85c01f85-a081-43e9-ab09-9993289cc200")
M2_BASE = "http://diyu-m2-app:8000"
M1_SOURCE_APP = _S1.M1_SOURCE_APP
M1_VERBATIM = _S1.M1_VERBATIM


def http(title, desc, method, url, body_tpl=None, actor=True, timeout_read=60,
         actor_tpl="{{#conversation.uapp_actor#}}"):
    # actor_tpl 的唯一理由：建域链跑到一半时 conversation.uapp_actor 还没写入
    # （写它的 boot_assign 是建域链最后一个节点），而 M2 对 workspace 内的写入
    # 依约要求 X-Actor-Ref，空值一律 401。建域中途改取本链第一步算出的 actor。
    d = {"type": "http-request", "title": title, "desc": desc, "method": method, "url": url,
         "authorization": {"type": "no-auth", "config": None},
         "headers": (("X-Actor-Ref:" + actor_tpl) if actor else ""),
         "params": "", "selected": False,
         "timeout": {"connect": 10, "read": timeout_read, "write": 20},
         # 打不通就如实交出空 body 和非 200，由下游写「查不到」。不进 fail-branch：
         # 「M2 没答」不该让整轮对话失败，它只让依赖 M2 的那部分变未知。
         "error_strategy": "default-value",
         "default_value": [{"key": "body", "type": "string", "value": ""},
                           {"key": "status_code", "type": "number", "value": 0},
                           {"key": "headers", "type": "object", "value": {}},
                           {"key": "files", "type": "array[file]", "value": []}],
         "body": {"type": "none", "data": []}}
    if body_tpl is not None:
        d["body"] = {"type": "json", "data": [{"key": "", "type": "text", "value": body_tpl}]}
    return d


def assigner(title, desc, items):
    return {"type": "assigner", "version": "2", "title": title, "desc": desc, "selected": False,
            "items": [{"input_type": it[0], "operation": "over-write", "write_mode": "over-write",
                       "value": it[1], "variable_selector": ["conversation", it[2]]} for it in items]}


# 本层唯一新增的产品行为：M2 投影已读到，但做判断的 M3 还没接。
# 关键约束在这里：读到什么说什么，**查不到就说查不到**，不把空响应说成"目前一切正常"。
S2_PENDING_SRC = r'''
import re


def _codes(note):
    """m2_note 形如 'cycles/current=200 decisions/latest=404 run-state=200'。

    这里解析真实状态码，而不是用 uapp_ctx 的 m2_reachable —— 那个值是
    (cycle 200 AND decision 200)，把「M2 打不通」和「查得到但还没有决策记录」
    压成了同一个 false。本层判据 3 要求的正是区分这两件事，所以在这里各算各的。
    uapp_ctx 本身没有错（它的 account_context 文本一直分得清），不改它。
    """
    out = {}
    for k, v in re.findall(r"([a-z\-/]+)=(\d+)", note or ""):
        out[k] = int(v)
    return out


def main(route_mode, triage_failed, m2_reachable, m2_note, registered_facts):
    if str(triage_failed).strip().lower() == "true":
        return {"pending_text": ("你这个问题我先记下了。这一版我还没能把它归到该走的那条线上，"
                                 "你把想解决的事再说具体一点，比如是哪个号、想让它有什么变化。"),
                "pending_kind": "triage_failed", "m2_state": "not_evaluated",
                "facts_present": "false"}

    c = _codes(m2_note)
    cyc, dec = c.get("cycles/current", 0), c.get("decisions/latest", 0)
    # 状态码 0 = http 节点的 default_value，代表根本没连上（传输层失败）。
    transport_down = (cyc == 0)
    answered = [v for v in (cyc, dec) if v != 0]
    # M2 答了「没有」（404）与 M2 答了内容（200）都算读到了；只有连不上才是读不到。
    has_decision = (dec == 200)
    facts = (registered_facts or "").strip()

    head = "你说的这件事我已经归到该走的那条线上了。\n\n"
    if transport_down:
        mid = ("不过实话说，我这会儿根本没连上记录系统——不是它里面是空的，是我没读到，"
               "这两件事不一样，我不替它打包票。\n\n")
        state = "unreachable"
    elif not has_decision:
        mid = ("我查过了：这个号目前在系统里还没有可用的经营记录。不是我没查，是确实还没有。"
               "所以后面任何判断都不该建立在「它其实还不错」这种假设上。\n\n")
        state = "reachable_no_record"
    else:
        mid = ("我已经把这个号目前在系统里记录在案的情况读出来了，后面做判断会以这些为准，"
               "不会替它补没发生过的事。\n\n")
        state = "reachable_with_record"

    tail = ("但真正做判断的那部分还没接进来，所以我现在给不了你分析结论。"
            "我也没有把它挂在后台跑——没跑就是没跑，不骗你等。\n\n"
            "等下一步接上，同样这句话就能直接出结果。")
    return {"pending_text": head + mid + tail,
            "pending_kind": "routed_not_wired",
            "m2_state": state,
            "facts_present": "true" if (has_decision or facts) else "false"}
'''



def build_graph():
    m1nodes, _cv, m1_features = m1_assets()
    # 本层不引入 M3 语义：参考资料信封显式传空，S3 接 M3 时才装载。
    ctx_src = (NODES.CTX_SRC_TEMPLATE
               .replace("__REFS_JSON__", json.dumps([]))
               .replace("__MANIFEST_LINES_JSON__", json.dumps([])))

    nodes, edges = [], []
    X, Y = 40, 300

    nodes.append(N("uapp_start", X, Y, {"type": "start", "title": "开始", "desc": "",
                                        "variables": [], "selected": False}))
    chain = ("m1_extract", "m1_join", "m1_shadow", "m1_compiler", "m1_save_snapshot")
    for i, nid in enumerate(chain):
        src = m1nodes[nid]
        nodes.append(N(nid, X + 320 * (i + 1), Y, json.loads(json.dumps(src["data"])),
                       src.get("width", 244), src.get("height", 98)))
    edges.append(E("uapp_start", "m1_extract"))
    for a, b in zip(chain, chain[1:]):
        edges.append(E(a, b))

    nodes.append(N("uapp_action", X + 1920, Y - 200, {
        "type": "llm", "title": "分诊｜本轮该进哪个能力、要登记哪类事",
        "desc": "把自然语言桥接到能力，并分类持久化动作；不产出任务上下文、不做专业判断、不写业务事实",
        "model": {"provider": "langgenius/deepseek/deepseek", "name": "deepseek-v4-flash",
                  "mode": "chat", "completion_params": {"max_tokens": 4000, "top_p": 0.8}},
        "prompt_template": [
            {"role": "system", "text": NODES.ACTION_SYSTEM_PROMPT + _S1.S1_AMBIGUITY_RULE,
             "id": "s1-act-sys"},
            {"role": "user", "text": NODES.ACTION_USER_PROMPT, "id": "s1-act-usr"}],
        "context": {"enabled": False, "variable_selector": []},
        "vision": {"enabled": False}, "selected": False,
        "structured_output_enabled": True, "reasoning_format": "separated",
        "structured_output": {"schema": NODES.ACTION_SCHEMA},
        "error_strategy": "default-value",
        "default_value": [{"key": "structured_output", "type": "object", "value": {}},
                          {"key": "text", "type": "string", "value": ""}],
        "retry_config": {"max_retries": 1, "retry_enabled": True, "retry_interval": 2000},
        "memory": {"query_prompt_template": "{{#sys.query#}}",
                   "window": {"enabled": True, "size": 4}}}))
    edges.append(E("m1_save_snapshot", "uapp_action"))

    nodes.append(N("uapp_route", X + 2240, Y, code(
        "路由｜把意图桥接到该进的那一个能力",
        "依据 Founder 裁定 UAPP-INTENT-ROUTING-001；本层只判路由，不执行能力",
        NODES.ROUTE_SRC,
        [V("call_intent_json", ["m1_compiler", "call_intent_json"]),
         V("snapshot_json", ["m1_compiler", "snapshot_json"]),
         V("user_query", ["sys", "query"]),
         V("ws_id", ["conversation", "uapp_ws"]),
         V("conv_id", ["sys", "conversation_id"]),
         V("action_patch", ["uapp_action", "structured_output"]),
         V("action_text", ["uapp_action", "text"])],
        ["tag", "action_source", "route_mode", "action", "has_capability", "runs_business",
         "runs_m3", "platform_text", "external_ref_text", "feedback_text",
         "withdraw_target_text", "target_capability", "intent", "intent_source",
         "triage_failed", "intent_reason", "decisive_question", "asks_one", "entry",
         "user_request", "needs_bootstrap", "route_note"]), 300, 120))
    edges.append(E("uapp_action", "uapp_route"))

    # ---- 三出口。只问一个在先：ASK_ONE 同样满足 runs_business，但问一句不需要业务事实。----
    nodes.append(N("uapp_s2_branch", X + 2620, Y, ifelse(
        "分流｜本层三条出口", "只问一个（不进 M2）/ 要业务事实 / 闲聊（不进 M2）",
        ("case_ask", ["uapp_route", "asks_one"], "true"),
        ("case_business", ["uapp_route", "runs_business"], "true")), 280, 180))
    edges.append(E("uapp_route", "uapp_s2_branch"))

    # 出口 1：只问一个
    nodes.append(N("uapp_ask_one", X + 3000, Y - 420, code(
        "收口｜只问一个决定性问题", "问题由分诊台给出；本节点只保证确实只有一个，不代拟",
        NODES.ASK_ONE_SRC,
        [V("question", ["uapp_route", "decisive_question"]),
         V("user_query", ["sys", "query"])],
        ["one_question", "question_count", "ask_note"])))
    nodes.append(N("uapp_answer_ask", X + 3320, Y - 420,
                   answer("回复｜只问一个", "{{#uapp_ask_one.one_question#}}")))
    edges.append(E("uapp_s2_branch", "uapp_ask_one", "case_ask"))
    edges.append(E("uapp_ask_one", "uapp_answer_ask"))

    # 出口 2：要业务事实 → 建域（仅首轮）→ M2 只读投影
    nodes.append(N("uapp_boot_gate", X + 3000, Y, ifelse(
        "闸门｜本会话是否还没有测试域", "只在首轮建域；后续轮读会话变量，天然幂等",
        ("boot", ["uapp_route", "needs_bootstrap"], "true")), 280, 140))
    edges.append(E("uapp_s2_branch", "uapp_boot_gate", "case_business"))

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
    prev, handle = "uapp_boot_gate", "boot"
    bx = X + 3320
    for i, (hid, hdata, pvars) in enumerate(boot_chain):
        pid = "boot_p%d" % (i + 1)
        if pid == "boot_p4":
            pvars = pvars + [V("account_id", ["boot_p3", "id"])]
        nodes.append(N(hid, bx + 320 * (2 * i), Y - 200, hdata))
        nodes.append(N(pid, bx + 320 * (2 * i + 1), Y - 200, code(
            "建域｜取回主键", "M2 每一步都把新对象主键放在 id 里；只取 id 和下一跳的 body",
            NODES.BOOT_SRC, pvars,
            ["id", "ok", "now", "actor", "ws_body", "acct_body", "cycle_body", "task_body"])))
        edges.append(E(prev, hid, handle))
        edges.append(E(hid, pid))
        prev, handle = pid, "source"

    nodes.append(N("boot_assign", bx + 320 * 10, Y - 200, assigner(
        "建域｜记住本会话的测试域", "会话级测试域标识写回会话变量，多轮不再重建",
        [("variable", ["boot_p2", "id"], "uapp_ws"),
         ("variable", ["boot_p3", "id"], "uapp_account"),
         ("variable", ["boot_p4", "id"], "uapp_cycle"),
         ("variable", ["boot_p5", "id"], "uapp_task"),
         ("variable", ["boot_p1", "actor"], "uapp_actor")])))
    edges.append(E("boot_p5", "boot_assign"))

    ws = "{{#conversation.uapp_ws#}}"
    acct = "{{#conversation.uapp_account#}}"
    task = "{{#conversation.uapp_task#}}"
    m2 = [("uapp_m2_cycle", "读 M2｜当前周期", "get",
           M2_BASE + "/workspaces/%s/accounts/%s/cycles/current" % (ws, acct)),
          ("uapp_m2_dec", "读 M2｜最近一次周期决策", "get",
           M2_BASE + "/workspaces/%s/accounts/%s/cycles/decisions/latest" % (ws, acct)),
          ("uapp_m2_run", "读 M2｜本任务运行状态", "get",
           M2_BASE + "/workspaces/%s/tasks/%s/run-state" % (ws, task))]
    prev2 = None
    for i, (nid, title, method, url) in enumerate(m2):
        nodes.append(N(nid, X + 3320 + 320 * i, Y + 200, http(title, "只读，不写", method, url)))
        if prev2:
            edges.append(E(prev2, nid))
        prev2 = nid
    # 建域分支与已建域分支在第一个 M2 读取节点汇合。
    edges.append(E("boot_assign", "uapp_m2_cycle"))
    edges.append(E("uapp_boot_gate", "uapp_m2_cycle", "false"))

    nodes.append(N("uapp_ctx", X + 4280, Y + 200, code(
        "组装｜M2 投影",
        "照抄 M2 字段；查不到写查不到，绝不把空响应升级成已知事实。本层参考资料信封显式传空",
        ctx_src,
        [V("cyc_raw", ["uapp_m2_cycle", "body"]), V("cyc_status", ["uapp_m2_cycle", "status_code"]),
         V("dec_raw", ["uapp_m2_dec", "body"]), V("dec_status", ["uapp_m2_dec", "status_code"]),
         V("run_raw", ["uapp_m2_run", "body"]), V("run_status", ["uapp_m2_run", "status_code"]),
         V("material_text", ["m1_join", "material_text"]),
         V("snapshot_json", ["m1_compiler", "snapshot_json"]),
         V("account_handle", ["uapp_route", "tag"])],
        ["account_context", "loaded_references", "registered_facts", "has_material",
         "m2_reachable", "m2_note"]), 300, 120))
    edges.append(E("uapp_m2_run", "uapp_ctx"))

    nodes.append(N("uapp_s2_pending", X + 4600, Y + 200, code(
        "如实交代｜投影已读、判断未接",
        "Rebase Prompt §6：查不到就说查不到；§5：不承诺异步结果",
        S2_PENDING_SRC,
        [V("route_mode", ["uapp_route", "route_mode"]),
         V("triage_failed", ["uapp_route", "triage_failed"]),
         V("m2_reachable", ["uapp_ctx", "m2_reachable"]),
         V("m2_note", ["uapp_ctx", "m2_note"]),
         V("registered_facts", ["uapp_ctx", "registered_facts"])],
        ["pending_text", "pending_kind", "m2_state", "facts_present"]), 280, 110))
    nodes.append(N("uapp_answer_pending", X + 4920, Y + 200,
                   answer("回复｜投影已读", "{{#uapp_s2_pending.pending_text#}}")))
    edges.append(E("uapp_ctx", "uapp_s2_pending"))
    edges.append(E("uapp_s2_pending", "uapp_answer_pending"))

    # 出口 3：闲聊，不进 M2
    src = m1nodes["m1_chat_llm"]
    nodes.append(N("m1_chat_llm", X + 3000, Y + 560, json.loads(json.dumps(src["data"])),
                   src.get("width", 244), src.get("height", 98)))
    nodes.append(N("uapp_chat_guard", X + 3320, Y + 560, code(
        "守卫｜本轮没真调能力就不许说得像调了",
        "Founder 裁定 UAPP-INTENT-ROUTING-001 第 4 点；整句删除，不改写",
        NODES.CHAT_GUARD_SRC,
        [V("text", ["m1_chat_llm", "text"]),
         V("capability_ran", ["uapp_route", "has_capability"]),
         V("target_capability", ["uapp_route", "target_capability"])],
        ["guarded_text", "promise_hits", "guard_note"])))
    nodes.append(N("uapp_answer_chat", X + 3640, Y + 560,
                   answer("回复｜对话", "{{#uapp_chat_guard.guarded_text#}}")))
    edges.append(E("uapp_s2_branch", "m1_chat_llm", "false"))
    edges.append(E("m1_chat_llm", "uapp_chat_guard"))
    edges.append(E("uapp_chat_guard", "uapp_answer_chat"))

    return {"nodes": nodes, "edges": edges,
            "viewport": {"x": 0, "y": 0, "zoom": 0.4}}, m1_features


def main():
    console = DC.Console(env=DC.load_env(ENV))
    graph, m1_features = build_graph()
    features = json.loads(json.dumps(m1_features))
    features["opening_statement"] = (
        "说说你现在要解决的经营问题就行——比如这周想让哪个账号做出什么变化。"
        "需要的资料可以直接上传，不用挑功能、不用填表格。")

    st, draft = console.call("GET", "/console/api/apps/%s/workflows/draft" % APP_ID)
    assert st == 200, ("read successor draft", st, draft)
    convvars = draft.get("conversation_variables") or []
    if isinstance(convvars, dict):
        convvars = list(convvars.values())

    dsl = {
        "app": {"name": _S1.APP_NAME, "mode": "advanced-chat", "icon_type": "emoji", "icon": "🎯",
                "icon_background": "#E4FBCC", "use_icon_as_answer_icon": False,
                "description": "笛语 V1 统一入口（渐进候选）：用自然语言完成经营判断、内容生产与反馈闭环。"},
        "kind": "app", "version": "0.7.0",
        "dependencies": [{"current_identifier": None, "type": "marketplace",
                          "value": {"marketplace_plugin_unique_identifier":
                                    "langgenius/deepseek:0.0.20@850efe73fb62bbe7ab2229116086596596"
                                    "297a77174fb86f73e1363b99a24116", "version": None}}],
        "workflow": {"graph": graph, "features": features,
                     "conversation_variables": convvars, "environment_variables": []},
    }
    import yaml
    dsl_text = yaml.safe_dump(dsl, allow_unicode=True, sort_keys=True, default_flow_style=False)
    dsl_path = os.path.join(HERE, "..", "dsl", "S2_PROGRESSIVE_CANVAS_v1.0.yml")
    with io.open(dsl_path, "w", encoding="utf-8") as fh:
        fh.write(dsl_text)

    st, imp = console.call("POST", "/console/api/apps/imports", body={
        "mode": "yaml-content", "yaml_content": dsl_text, "app_id": APP_ID}, timeout=600)
    assert st in (200, 201), ("import", st, json.dumps(imp, ensure_ascii=False)[:800])
    app_id = imp.get("app_id") or imp.get("id") or APP_ID
    assert app_id == APP_ID, ("导入创建了新应用，拒绝：只允许就地更新同一入口", app_id, APP_ID)
    if imp.get("status") not in ("completed", "completed-with-warnings"):
        raise SystemExit("导入未完成：%s" % imp.get("status"))

    st, pub = console.call("POST", "/console/api/apps/%s/workflows/publish" % app_id, body={
        "marked_name": "s2-m2-projection",
        "marked_comment": "S2：新增 M2 只读投影与任务域建域；闲聊与只问一个不进 M2；"
                          "查不到如实返回缺口；本层仍未接 M3/Hop/Seam"}, timeout=600)
    assert st in (200, 201), ("publish", st, json.dumps(pub, ensure_ascii=False)[:800])

    report = {
        "stage": "S2", "app_id": app_id, "import_status": imp.get("status"),
        "import_was_update_in_place": True,
        "node_count": len(graph["nodes"]), "edge_count": len(graph["edges"]),
        "node_ids": [n["id"] for n in graph["nodes"]],
        "graph_sha256": hashlib.sha256(json.dumps(graph, ensure_ascii=False, sort_keys=True)
                                       .encode("utf-8")).hexdigest(),
        "dsl_path": "unified-app/dsl/S2_PROGRESSIVE_CANVAS_v1.0.yml",
        "dsl_sha256": hashlib.sha256(dsl_text.encode("utf-8")).hexdigest(),
        "new_this_layer": ["uapp_boot_gate", "boot_user", "boot_p1", "boot_ws", "boot_p2",
                           "boot_acct", "boot_p3", "boot_cycle", "boot_p4", "boot_task",
                           "boot_p5", "boot_assign", "uapp_m2_cycle", "uapp_m2_dec",
                           "uapp_m2_run", "uapp_ctx", "uapp_s2_pending"],
        "m2_base": M2_BASE,
        "m3_references_loaded_this_layer": False,
        "layers_not_yet_wired": ["M3", "HOP", "SEAM", "six_capabilities"],
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    ev = os.path.join(HERE, "..", "evidence")
    n = 1
    while os.path.exists(os.path.join(ev, "S2_BUILD_%02d.json" % n)):
        n += 1
    report["build_attempt"] = n
    with io.open(os.path.join(ev, "S2_BUILD_%02d.json" % n), "w", encoding="utf-8") as fh:
        fh.write(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    return app_id


if __name__ == "__main__":
    main()
