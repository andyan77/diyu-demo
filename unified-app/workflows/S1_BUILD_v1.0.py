#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Node S1｜在**空白** advanced-chat 画布上部署 M1 与自然语言路由契约。

task_id: DIYU-V1-UNIFIED-DIFY-APPLICATION-001 ｜ entry_mode: REBASE_TASK

Founder 裁决（本轮）：新建空白画布渐进集成，模块走 DSL 后台导入，在独立工作区执行。

三条纪律，写进代码不是写进文档：

1. **M1 子图逐字节复用。** m1_extract / m1_join / m1_shadow / m1_compiler /
   m1_save_snapshot / m1_chat_llm 从已发布的 M1 候选应用原样取出，**节点 id 一并保留**，
   于是节点内部所有 value_selector 无需改写就仍然有效。等价性由构造保证。

2. **本层只到路由，不假装有能力。** S1 尚未接 M2/M3/Seam。凡路由判为要进能力的轮次，
   UI 必须如实说明专业分析尚未接通，**不得承诺异步结果**（Rebase Prompt §5）。

3. **旧资产零改动。** 旧 Canvas、旧候选 app、FP 八应用、Hop、M1 源应用只读不写。
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


DC = _load("s1_dify_client", os.path.join(ROOT, "account-operations", "tools", "dify_client.py"))
NODES = _load("s1_nodes", os.path.join(HERE, "UAPP_CANVAS_NODES_v1.0.py"))

APP_NAME = "DIYU V1 · Unified Founder Canvas · Progressive Candidate"
M1_SOURCE_APP = "dd638b91-d39f-4e92-a984-6ad1ab809119"     # 只读取节点，绝不写
M1_VERBATIM = ("m1_extract", "m1_join", "m1_shadow", "m1_compiler",
               "m1_save_snapshot", "m1_chat_llm")


def psql(sql, db="dify"):
    p = subprocess.run(["docker", "exec", "-i", "docker-db_postgres-1", "psql", "-U", "postgres",
                        "-d", db, "-tA", "-c", sql], capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError("psql failed: " + (p.stderr or "")[:400])
    return p.stdout.strip()


def m1_assets():
    g = json.loads(psql("select w.graph from workflows w join apps a on a.workflow_id=w.id "
                        "where a.id='%s';" % M1_SOURCE_APP))
    cv = json.loads(psql("select w.conversation_variables from workflows w "
                         "join apps a on a.workflow_id=w.id where a.id='%s';" % M1_SOURCE_APP))
    ft = json.loads(psql("select w.features from workflows w join apps a on a.workflow_id=w.id "
                         "where a.id='%s';" % M1_SOURCE_APP))
    return {n["id"]: n for n in g["nodes"]}, cv, ft


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


def ifelse(title, desc, *cases):
    return {"type": "if-else", "title": title, "desc": desc, "selected": False,
            "logical_operator": "and",
            "cases": [{"case_id": cid, "logical_operator": "and",
                       "conditions": [{"comparison_operator": "is", "value": val,
                                       "variable_selector": sel}]}
                      for cid, sel, val in cases]}


def answer(title, tpl):
    return {"type": "answer", "title": title, "desc": "", "answer": tpl,
            "variables": [], "selected": False}


# ================================================================ S1 专属节点
# 本层唯一新增的产品行为：路由已定、能力未接时如实交代。
# 它存在的理由是 Rebase Prompt §5 最后一条硬判据——不得承诺异步结果。
# S3 接上 M3 之后，本节点连同它的 answer 一起被真实调用链取代。
S1_PENDING_SRC = r'''
def main(route_mode, target_capability, triage_failed, user_request):
    """本层已经判出该进哪条线，但专业能力还没接上。只说实话。

    不说「已转交」「正在推进」「稍后给你结果」——本层没有任何后台任务在跑，
    说了就是空头支票（Founder 裁定 UAPP-INTENT-ROUTING-001 第 4 点）。
    也不报能力枚举名、不报节点名、不报内部状态词。
    """
    if str(triage_failed).strip().lower() == "true":
        body = ("你这个问题我先记下了。这一版我还没能把它归到该走的那条线上，"
                "你把想解决的事再说具体一点，比如是哪个号、想让它有什么变化。")
        return {"pending_text": body, "pending_kind": "triage_failed"}

    body = ("你说的这件事我已经归到该走的那条线上了。\n\n"
            "不过实话说，这一版只装到了「听懂你要什么」这一步，真正做判断的那部分还没接进来，"
            "所以我现在给不了你分析结论。我也没有把它挂在后台跑——没跑就是没跑，不骗你等。\n\n"
            "等下一步接上，同样这句话就能直接出结果。")
    return {"pending_text": body, "pending_kind": "routed_not_wired"}
'''


def build_graph():
    m1nodes, _cv, m1_features = m1_assets()
    missing = [k for k in M1_VERBATIM if k not in m1nodes]
    if missing:
        raise SystemExit("M1 源应用缺少待复用节点，拒绝建图：%s" % missing)

    nodes, edges = [], []
    X, Y = 40, 300

    # ---- 起点：零用户输入变量。用户只说自然语言（UAPP-AC-02）----
    nodes.append(N("uapp_start", X, Y, {"type": "start", "title": "开始", "desc": "",
                                        "variables": [], "selected": False}))

    # ---- M1 子图：逐字节复用，节点 id 保留 ----
    chain = ("m1_extract", "m1_join", "m1_shadow", "m1_compiler", "m1_save_snapshot")
    for i, nid in enumerate(chain):
        src = m1nodes[nid]
        nodes.append(N(nid, X + 320 * (i + 1), Y, json.loads(json.dumps(src["data"])),
                       src.get("width", 244), src.get("height", 98)))
    edges.append(E("uapp_start", "m1_extract"))
    for a, b in zip(chain, chain[1:]):
        edges.append(E(a, b))

    # ---- 分诊台：把自然语言桥接到能力 ----
    nodes.append(N("uapp_action", X + 1920, Y - 200, {
        "type": "llm", "title": "分诊｜本轮该进哪个能力、要登记哪类事",
        "desc": "把自然语言桥接到能力，并分类持久化动作；不产出任务上下文、不做专业判断、不写业务事实",
        # 4000 有实测依据：800 时本节点 finish_reason=length，推理把预算烧光，
        # 九个必填字段一个没输出，structured_output 全 null，路由静默落 DIALOGUE。
        "model": {"provider": "langgenius/deepseek/deepseek", "name": "deepseek-v4-flash",
                  "mode": "chat", "completion_params": {"max_tokens": 4000, "top_p": 0.8}},
        "prompt_template": [
            {"role": "system", "text": NODES.ACTION_SYSTEM_PROMPT + S1_AMBIGUITY_RULE,
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

    # ---- 路由：用户点名 > 待登记 > 分诊台意图 > 兜底闲聊 ----
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

    # ---- 本层分支：只有三条。歧义在先——ASK_ONE 也满足 runs_business。----
    nodes.append(N("uapp_s1_branch", X + 2620, Y, ifelse(
        "分流｜本层三条出口",
        "只问一个 / 已定路线但能力未接 / 闲聊",
        ("case_ask", ["uapp_route", "asks_one"], "true"),
        ("case_routed", ["uapp_route", "runs_business"], "true")), 280, 180))
    edges.append(E("uapp_route", "uapp_s1_branch"))

    # 出口 1：确有歧义 → 只问一个
    nodes.append(N("uapp_ask_one", X + 3000, Y - 220, code(
        "收口｜只问一个决定性问题",
        "问题由分诊台给出；本节点只保证确实只有一个，不代拟",
        NODES.ASK_ONE_SRC,
        [V("question", ["uapp_route", "decisive_question"]),
         V("user_query", ["sys", "query"])],
        ["one_question", "question_count", "ask_note"])))
    nodes.append(N("uapp_answer_ask", X + 3320, Y - 220,
                   answer("回复｜只问一个", "{{#uapp_ask_one.one_question#}}")))
    edges.append(E("uapp_s1_branch", "uapp_ask_one", "case_ask"))
    edges.append(E("uapp_ask_one", "uapp_answer_ask"))

    # 出口 2：路线已定但本层未接能力 → 如实交代，不承诺异步
    nodes.append(N("uapp_s1_pending", X + 3000, Y, code(
        "如实交代｜路线已定、能力未接",
        "Rebase Prompt §5：本层尚未接 M3 时只能如实说明，不得承诺异步结果",
        S1_PENDING_SRC,
        [V("route_mode", ["uapp_route", "route_mode"]),
         V("target_capability", ["uapp_route", "target_capability"]),
         V("triage_failed", ["uapp_route", "triage_failed"]),
         V("user_request", ["uapp_route", "user_request"])],
        ["pending_text", "pending_kind"])))
    nodes.append(N("uapp_answer_pending", X + 3320, Y,
                   answer("回复｜路线已定", "{{#uapp_s1_pending.pending_text#}}")))
    edges.append(E("uapp_s1_branch", "uapp_s1_pending", "case_routed"))
    edges.append(E("uapp_s1_pending", "uapp_answer_pending"))

    # 出口 3：闲聊 → M1 对话节点 + 空头支票守卫
    src = m1nodes["m1_chat_llm"]
    nodes.append(N("m1_chat_llm", X + 3000, Y + 240, json.loads(json.dumps(src["data"])),
                   src.get("width", 244), src.get("height", 98)))
    nodes.append(N("uapp_chat_guard", X + 3320, Y + 240, code(
        "守卫｜本轮没真调能力就不许说得像调了",
        "Founder 裁定 UAPP-INTENT-ROUTING-001 第 4 点；整句删除，不改写",
        NODES.CHAT_GUARD_SRC,
        [V("text", ["m1_chat_llm", "text"]),
         V("capability_ran", ["uapp_route", "has_capability"]),
         V("target_capability", ["uapp_route", "target_capability"])],
        ["guarded_text", "promise_hits", "guard_note"])))
    nodes.append(N("uapp_answer_chat", X + 3640, Y + 240,
                   answer("回复｜对话", "{{#uapp_chat_guard.guarded_text#}}")))
    edges.append(E("uapp_s1_branch", "m1_chat_llm", "false"))
    edges.append(E("m1_chat_llm", "uapp_chat_guard"))
    edges.append(E("uapp_chat_guard", "uapp_answer_chat"))

    graph = {"nodes": nodes, "edges": edges,
             "viewport": {"x": 0, "y": 0, "zoom": 0.55}}
    return graph, m1_features


# 对 ACTION_SYSTEM_PROMPT 的**唯一**增补。理由不是为了让某一条测试通过，而是补一条
# 结构性规则：修改类动词本身不标识产物维度。
# 「打磨/改/优化/调整」在本系统里对应三种实质不同的产物——口播稿（文案）、拍法（呈现）、
# 标题封面（包装）。用户只说"改一下"而没说改哪一面时，三条路都说得通且产物不同，
# 正是原提示词第 3 条自己定义的 AMBIGUOUS。原提示词没有把这一类点出来，
# 实测两次都落到「自信地猜一个」或「分类失败」，从未判出 AMBIGUOUS。
S1_AMBIGUITY_RULE = """

────────── 补充规则（与上文同级，不覆盖上文）──────────

5. **修改类请求缺少「改哪一面」时判 `AMBIGUOUS`。**
   用户说的是把某个东西「打磨 / 改 / 优化 / 调整 / 再弄弄」，但没有说清要改的是哪一面，
   而且上文也没有确定过具体是哪一份产物时 —— 判 `AMBIGUOUS`。

   理由是结构性的，不是措辞问题：修改类动词本身不标识产物维度。「改一下」至少对应
   三种实质不同的产物 —— 文案措辞、拍法呈现、标题封面 —— 分别归三个不同能力，
   产出物完全不同，选错等于让用户白做一遍。这正是第 3 条所说的 `AMBIGUOUS`。

   `decisive_question_text` 就问这一件事：要改的是哪一面。只问这一个。

   **反向边界（同样是硬约束）**：上文已经确定过具体产物，或用户已经点明了哪一面
   （说了「稿子」「文案」「怎么拍」「封面」「标题」等），就**照常直接判**对应能力，
   不许反问 —— 那不是歧义，那是明确意图，反问就是失职。"""


def main():
    console = DC.Console(env=DC.load_env(ENV))
    graph, m1_features = build_graph()

    features = json.loads(json.dumps(m1_features))
    features["opening_statement"] = (
        "说说你现在要解决的经营问题就行——比如这周想让哪个账号做出什么变化。"
        "需要的资料可以直接上传，不用挑功能、不用填表格。")

    # 会话变量：M1 的形状逐字节沿用，再加本任务自己的会话级测试域标识。
    st, draft = console.call("GET", "/console/api/apps/%s/workflows/draft" % M1_SOURCE_APP)
    assert st == 200, ("read m1 draft", st, draft)
    base = draft.get("conversation_variables") or []
    if isinstance(base, dict):
        base = list(base.values())
    convvars = [json.loads(json.dumps(v)) for v in base]
    import uuid as _uuid
    for name, desc in (
            ("uapp_ws", "本会话测试工作区 id（M2）。业务真源在 M2，这里只存标识。"),
            ("uapp_account", "本会话测试账号 id（M2）。"),
            ("uapp_cycle", "本会话当前周期 id（M2）。"),
            ("uapp_task", "本会话任务 id（M2）。"),
            ("uapp_actor", "本会话调用者标识，作为 M2 的 X-Actor-Ref。"),
            ("uapp_last_artifact", "上一跳专业能力交付的产物本体，只作为下一跳的上游输入。"),
            ("uapp_last_capability", "上一跳交付产物的能力身份。"),
            ("uapp_last_material", "本会话最近登记的素材 id（M2），撤回时定位用。"),
            ("uapp_last_version", "本会话最近登记的内容版本 id（M2），发布登记引用它。"),
            ("uapp_last_publish", "本会话最近的测试发布记录 id（M2），反馈按它幂等写回。")):
        convvars.append({"id": str(_uuid.uuid5(_uuid.NAMESPACE_URL, "diyu-uapp-" + name)),
                         "name": name, "value_type": "string", "value": "",
                         "description": desc, "selector": ["conversation", name]})

    dsl = {
        "app": {"name": APP_NAME, "mode": "advanced-chat", "icon_type": "emoji", "icon": "🎯",
                "icon_background": "#E4FBCC", "use_icon_as_answer_icon": False,
                "description": "笛语 V1 统一入口（渐进候选）：用自然语言完成经营判断、内容生产与反馈闭环。"},
        "kind": "app", "version": "0.7.0",
        "dependencies": [{
            "current_identifier": None, "type": "marketplace",
            "value": {"marketplace_plugin_unique_identifier":
                      "langgenius/deepseek:0.0.20@850efe73fb62bbe7ab2229116086596596297a77174fb"
                      "86f73e1363b99a24116", "version": None}}],
        "workflow": {"graph": graph, "features": features,
                     "conversation_variables": convvars, "environment_variables": []},
    }

    import yaml
    dsl_text = yaml.safe_dump(dsl, allow_unicode=True, sort_keys=True, default_flow_style=False)
    dsl_dir = os.path.join(HERE, "..", "dsl")
    dsl_path = os.path.join(dsl_dir, "S1_PROGRESSIVE_CANVAS_v1.0.yml")
    with io.open(dsl_path, "w", encoding="utf-8") as fh:
        fh.write(dsl_text)

    target_app = os.environ.get("S1_APP_ID", "").strip()
    body = {"mode": "yaml-content", "yaml_content": dsl_text}
    if target_app:
        body["app_id"] = target_app          # 就地更新同一应用，不新建第二个入口
    st, imp = console.call("POST", "/console/api/apps/imports", body=body, timeout=600)
    assert st in (200, 201), ("import", st, json.dumps(imp, ensure_ascii=False)[:800])
    app_id = imp.get("app_id") or imp.get("id")
    assert app_id, imp
    if imp.get("status") not in ("completed", "completed-with-warnings"):
        raise SystemExit("导入未完成，拒绝继续：%s %s" % (
            imp.get("status"), json.dumps(imp.get("leaked_dependencies"), ensure_ascii=False)[:400]))

    st, pub = console.call("POST", "/console/api/apps/%s/workflows/publish" % app_id, body={
        "marked_name": os.environ.get("S1_MARK", "s1-m1-routing"),
        "marked_comment": "S1：空白画布 + M1 子图逐字节复用 + 自然语言路由契约；"
                          "本层未接 M2/M3/Seam，路由已定时如实交代不承诺异步"}, timeout=600)
    assert st in (200, 201), ("publish", st, json.dumps(pub, ensure_ascii=False)[:800])

    report = {
        "stage": "S1", "app_name": APP_NAME, "app_id": app_id,
        "import_status": imp.get("status"),
        "import_was_update_in_place": bool(target_app),
        "transport": console.transport,
        "node_count": len(graph["nodes"]), "edge_count": len(graph["edges"]),
        "node_ids": [n["id"] for n in graph["nodes"]],
        "graph_sha256": hashlib.sha256(json.dumps(
            graph, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest(),
        "dsl_path": "unified-app/dsl/S1_PROGRESSIVE_CANVAS_v1.0.yml",
        "dsl_sha256": hashlib.sha256(dsl_text.encode("utf-8")).hexdigest(),
        "m1_subgraph_reused_verbatim": list(M1_VERBATIM),
        "m1_source_app": M1_SOURCE_APP,
        "published_version": pub.get("id") or pub.get("version"),
        "conversation_variables": [v["name"] for v in convvars],
        "layers_not_yet_wired": ["M2", "M3", "HOP", "SEAM", "six_capabilities"],
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    ev = os.path.join(HERE, "..", "evidence")
    n = 1
    while os.path.exists(os.path.join(ev, "S1_BUILD_%02d.json" % n)):
        n += 1
    report["build_attempt"] = n
    with io.open(os.path.join(ev, "S1_BUILD_%02d.json" % n), "w", encoding="utf-8") as fh:
        fh.write(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    return app_id


if __name__ == "__main__":
    main()
