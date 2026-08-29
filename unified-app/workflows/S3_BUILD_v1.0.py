#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Node S3｜在 S2 当前图上接入最终 FP M3，验证 M2→M3→用户返回。

只绑定最终 FP M3 `a4c3b19b-243f-490b-9aca-3aa19767d6a5` 的任务 provider。
**不修改 M3 的 graph / model / prompt / Skill** —— 只调用。

本层图以 S2 的 build_graph() 为基底就地扩展，不复制 S1+S2 那一段：
S1/S2 的节点定义只有一个真源，改一处两层同时生效。
"""
import hashlib
import importlib.util
import io
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
ENV = "/home/faye/diyu-demo-worktrees/m3-account-content-operator-v1/.env"


def _load(n, p):
    s = importlib.util.spec_from_file_location(n, p)
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m


_S2 = _load("s2b", os.path.join(HERE, "S2_BUILD_v1.0.py"))
_S1, DC, NODES = _S2._S1, _S2.DC, _S2.NODES
N, E, code, V, ifelse, answer = _S1.N, _S1.E, _S1.code, _S1.V, _S1.ifelse, _S1.answer
tool_node = None

APP_ID = os.environ.get("S3_APP_ID", "85c01f85-a081-43e9-ab09-9993289cc200")
PROVIDER_M3 = "9ea86217-8791-489c-9a96-b880ae558ac5"
TOOL_M3 = "diyu_uapp_m3"
M3_APP = "a4c3b19b-243f-490b-9aca-3aa19767d6a5"

# M3 的方法参考。构建时读仓库、嵌进图；哈希记进 Stage Gate，由确定性检查比对两份载体。
M3_REF_DIR = os.path.join(ROOT, "m3-account-content-operator-semantic-v1.0",
                          "skill-source", "references")
M3_REFERENCES = [
    ("references/fashion-and-market.md", "fashion-and-market.md", True),
    ("references/six-skill-methods.md", "six-skill-methods.md", True),
    ("references/operations.md", "operations.md", True),
    # M3 自己的验收夹具，含期望答案。加载进正式运行会污染取证。如实声明未加载。
    ("references/acceptance-fixtures.md", "acceptance-fixtures.md", False),
]


def tool(title, desc, provider_id, tool_name, params, retries=1):
    return {"type": "tool", "title": title, "desc": desc,
            "provider_id": provider_id, "provider_name": provider_id, "provider_type": "workflow",
            "tool_label": tool_name, "tool_name": tool_name, "tool_node_version": "2",
            "tool_configurations": {}, "selected": False,
            # 组件失败只影响这一支：走 fail-branch 如实交代，不当成整轮失败，也不假装完成。
            "error_strategy": "fail-branch",
            "retry_config": {"max_retries": retries, "retry_enabled": True, "retry_interval": 2000},
            "tool_parameters": {k: {"type": "mixed", "value": v} for k, v in params.items()}}


def build_refs():
    lines, bodies, digests = [], [], []
    for manifest_path, fname, load in M3_REFERENCES:
        raw = io.open(os.path.join(M3_REF_DIR, fname), "rb").read()
        sha = hashlib.sha256(raw).hexdigest()
        lines.append("%s: %s" % (manifest_path, "LOADED" if load else "NOT_LOADED"))
        digests.append({"path": manifest_path, "file": fname,
                        "status": "LOADED" if load else "NOT_LOADED",
                        "sha256": sha, "bytes": len(raw)})
        if load:
            bodies.append([manifest_path, raw.decode("utf-8")])
    return lines, bodies, digests


# 本层交付节点。泄漏清洗**直接复用** DELIVERY_SRC 的前言（_STATE_WORDS / _IDENTIFIERS /
# _CAP_CN / _scrub），构建时截取拼接，不另抄一份——泄漏口径只有一个真源。
_DELIV_PRELUDE = NODES.DELIVERY_SRC[:NODES.DELIVERY_SRC.index("def main(capability")]

S3_DELIVER_MAIN = r'''
# 与 S2 的 pending 同一套判定口径：有没有记录看**载荷**，不看状态码。
# M2 无决策时返回 200 {"decision":"none_recorded"}，只看状态码会把哨兵值当成真记录。
_NO_RECORD = ("", "none", "null", "none_recorded", "not_recorded", "no_record", "unknown")


def _m2_state(m2_note, dec_raw):
    codes = {}
    for k, v in re.findall(r"([a-z\-/]+)=(\d+)", m2_note or ""):
        codes[k] = int(v)
    if codes.get("cycles/current", 0) == 0 and codes.get("decisions/latest", 0) == 0:
        return "unreachable"
    try:
        b = json.loads(dec_raw) if isinstance(dec_raw, str) else (dec_raw or {})
    except Exception:
        b = {}
    d = str((b or {}).get("decision") or "").strip() if isinstance(b, dict) else ""
    return "reachable_with_record" if (d and d.lower() not in _NO_RECORD) else "reachable_no_record"


def main(m3_judgment, m3_gate_status, route_mode, target_capability, m2_note, dec_raw):
    m2_state = _m2_state(m2_note, dec_raw)
    """把 M3 的运营判断投影成自然语言交付。

    本层与最终形态的差别只有一处：Seam 与六能力还没接，所以当本轮路由指向某个专业能力时，
    必须**如实说明那一步还没接通**，而不是把 M3 的判断冒充成该能力的产物。
    M3 判断本身照常交付——它是真跑出来的，不因为下游没接就藏起来。
    """
    body = (m3_judgment or "").strip()

    if not body:
        # M3 跑了但没有产出正文：如实说，不编、不把「跑完了」说成「做好了」。
        final = ("这一步没有产出可以交给你的内容。原始运行记录已经保留，"
                 "没有被删掉，也没有被改写成完成。")
        delivered = False
    else:
        final = body
        delivered = True
        if route_mode == "CAPABILITY":
            final += ("\n\n——以上是对这个号当前经营状况的判断。你这件事按理还要再往下走一步，"
                      "交给对应的专业能力出具体产物；那一步这一版还没接上，所以我没有替你跑，"
                      "也没有挂在后台。等接上了，同样这句话就能一路走到底。")

    if m2_state == "reachable_no_record":
        final += ("\n\n另外说明一句：上面这些判断，是在系统里还没有这个号任何经营记录的前提下做的。"
                  "等你把实际情况补进来，结论可能会变。")
    elif m2_state == "unreachable":
        final += ("\n\n另外说明一句：这一轮我没连上记录系统，所以上面没有任何一条是基于"
                  "这个号已登记的历史情况。")

    final, hits = _scrub(final)
    if not final:
        final = "这一步没有产出可以交给你的内容，原始记录已保留。"

    modules = ["M1 任务上下文", "M2 当前投影", "M3 单账号持续运营"]
    return {
        "final_text": final,
        "delivered_flag": "true" if delivered else "false",
        "m3_gate_status_seen": str(m3_gate_status or ""),
        "m2_state": m2_state,
        "modules_actually_run": json.dumps(modules, ensure_ascii=False),
        "leak_hits_json": json.dumps(hits, ensure_ascii=False),
        "leak_hit_count": str(len(hits)),
    }
'''
S3_DELIVER_SRC = _DELIV_PRELUDE + S3_DELIVER_MAIN


def build_graph():
    graph, features = _S2.build_graph()
    ref_lines, ref_bodies, ref_digests = build_refs()

    nodes = {n["id"]: n for n in graph["nodes"]}
    # ---- 本层把 M3 方法参考装进投影节点（S2 层显式为空）----
    nodes["uapp_ctx"]["data"]["code"] = (
        NODES.CTX_SRC_TEMPLATE
        .replace("__REFS_JSON__", json.dumps(ref_bodies))
        .replace("__MANIFEST_LINES_JSON__", json.dumps(ref_lines)))
    nodes["uapp_ctx"]["data"]["desc"] = "照抄 M2 字段；查不到写查不到。本层装载 M3 方法参考，验收夹具显式未加载"

    # ---- 摘掉 S2 的「投影已读、判断未接」直连，改由 M3 闸门分流 ----
    graph["edges"] = [e for e in graph["edges"]
                      if not (e["source"] == "uapp_ctx" and e["target"] == "uapp_s2_pending")]

    X, Y = 40, 300
    add, edges = [], graph["edges"]

    add.append(N("uapp_m3_gate", X + 4600, Y + 200, ifelse(
        "闸门｜本轮是否需要 M3 运营判断",
        "要产出、要复盘、要开下一周期才进 M3；单纯问系统记住了什么不进",
        ("m3", ["uapp_route", "runs_m3"], "true")), 280, 140))
    edges.append(E("uapp_ctx", "uapp_m3_gate"))

    add.append(N("uapp_m3", X + 4920, Y + 200, tool(
        "调用｜最终 FP M3 单账号持续运营",
        "周期判断与内容任务；专业判断在 M3 内，本画布不复制其语义，也不修改它",
        PROVIDER_M3, TOOL_M3,
        {"account_context": "{{#uapp_ctx.account_context#}}",
         "user_request": "{{#uapp_route.user_request#}}",
         "loaded_references": "{{#uapp_ctx.loaded_references#}}"})))
    edges.append(E("uapp_m3_gate", "uapp_m3", "m3"))

    add.append(N("uapp_s3_deliver", X + 5240, Y + 200, code(
        "投影｜M3 判断 → 自然语言交付",
        "本层未接 Seam 与六能力，路由指向能力时如实说明那一步未接通，不冒充其产物",
        S3_DELIVER_SRC,
        [V("m3_judgment", ["uapp_m3", "operating_judgment"]),
         V("m3_gate_status", ["uapp_m3", "gate_status"]),
         V("route_mode", ["uapp_route", "route_mode"]),
         V("target_capability", ["uapp_route", "target_capability"]),
         V("m2_note", ["uapp_ctx", "m2_note"]),
         V("dec_raw", ["uapp_m2_dec", "body"])],
        ["final_text", "delivered_flag", "m3_gate_status_seen", "m2_state",
         "modules_actually_run", "leak_hits_json", "leak_hit_count"]), 300, 120))
    add.append(N("uapp_answer_main", X + 5560, Y + 200,
                 answer("回复｜运营判断", "{{#uapp_s3_deliver.final_text#}}")))
    edges.append(E("uapp_m3", "uapp_s3_deliver"))
    edges.append(E("uapp_s3_deliver", "uapp_answer_main"))

    # M3 这一支失败时的局部 Return：不当成整轮失败，也不假装完成。
    add.append(N("uapp_m3_fail", X + 5240, Y + 420, code(
        "局部 Return｜M3 调用失败", "只影响这一支；不猜原因、不把失败说成业务结论",
        NODES.TOOLFAIL_SRC,
        [V("which", ["uapp_route", "route_mode"]),
         V("error_text", ["uapp_m3", "error"])],
        ["final_text", "failed_stage", "error_kept"])))
    add.append(N("uapp_answer_m3fail", X + 5560, Y + 420,
                 answer("回复｜这一步没跑完", "{{#uapp_m3_fail.final_text#}}")))
    edges.append(E("uapp_m3", "uapp_m3_fail", "fail-branch"))
    edges.append(E("uapp_m3_fail", "uapp_answer_m3fail"))

    # 不进 M3 的业务轮（如只问系统记住了什么）仍走 S2 的如实交代节点。
    edges.append(E("uapp_m3_gate", "uapp_s2_pending", "false"))

    graph["nodes"].extend(add)
    return graph, features, ref_digests


def main():
    console = DC.Console(env=DC.load_env(ENV))
    graph, features, ref_digests = build_graph()

    st, draft = console.call("GET", "/console/api/apps/%s/workflows/draft" % APP_ID)
    assert st == 200, ("read draft", st, draft)
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
    with io.open(os.path.join(HERE, "..", "dsl", "S3_PROGRESSIVE_CANVAS_v1.0.yml"), "w",
                 encoding="utf-8") as fh:
        fh.write(dsl_text)

    st, imp = console.call("POST", "/console/api/apps/imports", body={
        "mode": "yaml-content", "yaml_content": dsl_text, "app_id": APP_ID}, timeout=600)
    assert st in (200, 201), ("import", st, json.dumps(imp, ensure_ascii=False)[:800])
    app_id = imp.get("app_id") or imp.get("id") or APP_ID
    assert app_id == APP_ID, ("导入创建了新应用，拒绝", app_id)
    if imp.get("status") not in ("completed", "completed-with-warnings"):
        raise SystemExit("导入未完成：%s %s" % (imp.get("status"),
                         json.dumps(imp.get("leaked_dependencies"), ensure_ascii=False)[:300]))

    st, pub = console.call("POST", "/console/api/apps/%s/workflows/publish" % app_id, body={
        "marked_name": "s3-m3-wired",
        "marked_comment": "S3：接入最终 FP M3（只调用不修改）；装载 M3 方法参考，验收夹具未加载；"
                          "M3 失败走局部 Return；本层仍未接 Hop/Seam/六能力"}, timeout=600)
    assert st in (200, 201), ("publish", st, json.dumps(pub, ensure_ascii=False)[:800])

    report = {
        "stage": "S3", "app_id": app_id, "import_status": imp.get("status"),
        "import_was_update_in_place": True,
        "node_count": len(graph["nodes"]), "edge_count": len(graph["edges"]),
        "node_ids": sorted(n["id"] for n in graph["nodes"]),
        "graph_sha256": hashlib.sha256(json.dumps(graph, ensure_ascii=False, sort_keys=True)
                                       .encode("utf-8")).hexdigest(),
        "dsl_sha256": hashlib.sha256(dsl_text.encode("utf-8")).hexdigest(),
        "new_this_layer": ["uapp_m3_gate", "uapp_m3", "uapp_s3_deliver", "uapp_answer_main",
                           "uapp_m3_fail", "uapp_answer_m3fail"],
        "m3_binding": {"provider_id": PROVIDER_M3, "tool_name": TOOL_M3, "target_app": M3_APP},
        "m3_reference_digests": ref_digests,
        "leak_scrub_source": "复用 NODES.DELIVERY_SRC 前言（_STATE_WORDS/_IDENTIFIERS/_scrub），未另抄副本",
        "layers_not_yet_wired": ["HOP", "SEAM", "six_capabilities"],
    }
    print(json.dumps({k: report[k] for k in
                      ("stage", "app_id", "import_status", "node_count", "edge_count",
                       "graph_sha256", "dsl_sha256", "new_this_layer", "m3_binding")},
                     ensure_ascii=False, indent=2))
    ev = os.path.join(HERE, "..", "evidence")
    n = 1
    while os.path.exists(os.path.join(ev, "S3_BUILD_%02d.json" % n)):
        n += 1
    report["build_attempt"] = n
    with io.open(os.path.join(ev, "S3_BUILD_%02d.json" % n), "w", encoding="utf-8") as fh:
        fh.write(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    return app_id


if __name__ == "__main__":
    main()
