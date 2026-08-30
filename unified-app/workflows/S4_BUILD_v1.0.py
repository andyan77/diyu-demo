#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Node S4｜在 S3 当前图上接入 Hop 与最终 FP Seam，打通到六项专业能力。

复用现有 Hop 与最终 FP Seam；六能力的 graph / model / prompt / Skill 保持只读。
画布只负责把已经确定的任务路由给 Seam，并把组件 Return 投影成自然用户交付。

一条与「渐进」有关的事实，写在这里免得后面被误读：
**六项能力全部在 Seam 内部由它自己分派**（seam_dispatch → tool_matrix / tool_campaign / …）。
所以画布侧的接线是**一次性的一条**，不是六条；
§8.2 的「逐项开放六能力」在这一层体现为**验证顺序**，不是节点数量。
"""
import hashlib
import importlib.util
import io
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ENV = "/home/faye/diyu-demo-worktrees/m3-account-content-operator-v1/.env"


def _load(n, p):
    s = importlib.util.spec_from_file_location(n, p)
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m


_S3 = _load("s3b", os.path.join(HERE, "S3_BUILD_v1.0.py"))
_S1, DC, NODES = _S3._S1, _S3.DC, _S3.NODES
N, E, code, V, ifelse, answer, tool = (_S1.N, _S1.E, _S1.code, _S1.V, _S1.ifelse,
                                       _S1.answer, _S3.tool)
assigner = _S3._S2.assigner

APP_ID = os.environ.get("S4_APP_ID", "85c01f85-a081-43e9-ab09-9993289cc200")
PROVIDER_HOP = "fd3f6f29-237f-4bbe-a820-5d38076ab52e"
PROVIDER_SEAM = "f8d63527-8c45-4823-8159-443cef37240d"
TOOL_HOP, TOOL_SEAM = "diyu_uapp_hop", "diyu_uapp_seam"
HOP_APP = "6c46fdb1-5f49-4513-a0c0-29957b3dcee4"
SEAM_APP = "5fca0162-e26b-4545-a00b-66b1a2a2a077"


# 写回闸门源码。**本层自有，不改共享的 DELIVERY_SRC**——后者同时被旧 Canvas 建图脚本
# 与 S3 复用，改它会把变化推到不该动的保护面上（A3：只沿依赖传播，不多算）。
#
# 为什么需要这个闸门：uapp_save 是无条件 assigner，能力停在缺口返回空 artifact 时
# 同样写入，于是用空串覆盖上一轮已确认的有效产物。实测 conv 637ac1a6：
# turn 2 的 5593 字 Content Brief 被 turn 3（CS 停在 content_origin_mode 缺口）抹掉，
# turn 4 的 upstream_delivery 归零。见 S4_FACT_SUFFICIENCY_FAILURE_TRIAGE_FINAL_v1.0.md §2.4。
#
# 为什么 artifact 与 capability 必须一起动：只保产物不保身份，会让下一跳把
# 「上一个能力是 CREATIVE_SCRIPT」和「上一个产物是 Content Brief 正文」配成一对，
# hop 的 ARTIFACT_IS_FIELD 规则会据此把 Brief 正文当成脚本本体——那是编造。
PERSIST_SRC = r"""
def main(new_artifact, new_capability, prev_artifact, prev_capability):
    new_a = (new_artifact or "").strip()
    if new_a:
        return {"artifact_to_persist": new_artifact or "",
                "capability_to_persist": new_capability or "",
                "persist_action": "WRITE_NEW"}
    return {"artifact_to_persist": prev_artifact or "",
            "capability_to_persist": prev_capability or "",
            "persist_action": "KEEP_PREVIOUS"}
"""


def build_graph():
    graph, features, ref_digests = _S3.build_graph()
    nodes = {n["id"]: n for n in graph["nodes"]}

    # 摘掉 S3 的「M3 → 交付」直连，改由「本轮要不要进专业能力」闸门分流。
    graph["edges"] = [e for e in graph["edges"]
                      if not (e["source"] == "uapp_m3" and e["target"] == "uapp_s3_deliver")]
    # S3 的交付节点与它的 answer 在本层被完整交付取代，一并摘除。
    for dead in ("uapp_s3_deliver", "uapp_answer_main"):
        graph["nodes"] = [n for n in graph["nodes"] if n["id"] != dead]
        graph["edges"] = [e for e in graph["edges"]
                          if e["source"] != dead and e["target"] != dead]

    X, Y = 40, 300
    add, edges = [], graph["edges"]

    add.append(N("uapp_op_gate", X + 5560, Y + 200, ifelse(
        "闸门｜本轮要进专业能力吗",
        "只有路由确定了六项能力之一才进接缝；否则不进，不暗跑",
        ("capability", ["uapp_route", "has_capability"], "true")), 280, 140))
    edges.append(E("uapp_m3", "uapp_op_gate"))

    add.append(N("uapp_hop", X + 5880, Y + 200, tool(
        "调用｜跨能力抽取适配",
        "按目标能力的必填清单从已登记来源抽取；只抽取不推断，不补造事实",
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

    add.append(N("uapp_seam", X + 6200, Y + 200, tool(
        "调用｜最终 FP 统一能力接缝",
        "一次只进一个专业能力；入口由接缝自己的确定性充分性规则推导，本画布不再算一遍",
        PROVIDER_SEAM, TOOL_SEAM,
        {"capability": "{{#uapp_route.target_capability#}}",
         "entry": "{{#uapp_route.entry#}}",
         "capability_call": "{{#uapp_hop.capability_call#}}",
         "professional_input": "{{#uapp_hop.professional_input#}}",
         "example_reference_requested": "NO"})))
    edges.append(E("uapp_hop", "uapp_seam"))

    add.append(N("uapp_noseam", X + 5880, Y + 440, code(
        "占位｜本轮不进专业能力", "只提供空值，不代替判断",
        NODES.NOSEAM_SRC, [V("route_mode", ["uapp_route", "route_mode"])],
        ["empty", "empty_arr", "note"])))
    edges.append(E("uapp_op_gate", "uapp_noseam", "false"))

    groups = [
        ("artifact", ["uapp_seam", "artifact"], ["uapp_noseam", "empty"]),
        ("user_delivery", ["uapp_seam", "user_delivery"], ["uapp_noseam", "empty"]),
        ("outcome", ["uapp_seam", "business_delivery_outcome"], ["uapp_noseam", "empty"]),
        ("returns_json", ["uapp_seam", "returns_json"], ["uapp_noseam", "empty_arr"]),
        ("hop_gaps", ["uapp_hop", "extraction_gaps_text"], ["uapp_noseam", "empty"]),
    ]
    add.append(N("uapp_seam_merge", X + 6520, Y + 200, {
        "type": "variable-aggregator", "title": "汇合｜能力分支与非能力分支",
        "desc": "哪一支跑了就取哪一支；两支都没有就是空。不代替判断，只做取值。",
        "selected": False, "output_type": "string",
        "variables": [["uapp_seam", "user_delivery"], ["uapp_noseam", "empty"]],
        "advanced_settings": {"group_enabled": True, "groups": [
            {"group_name": g, "output_type": "string", "variables": [a, b]}
            for g, a, b in groups]}}, 280, 160))
    edges.append(E("uapp_seam", "uapp_seam_merge"))
    edges.append(E("uapp_noseam", "uapp_seam_merge"))

    # 完整用户投影：本层起改用共享的 DELIVERY_SRC（S3 的薄交付节点已被摘除）。
    add.append(N("uapp_delivery", X + 6840, Y + 200, code(
        "投影｜组件 Return → 自然用户交付",
        "user_delivery 非空就用它；能力没写正文才由本节点按缺口兜底。内部字段一律清洗",
        NODES.DELIVERY_SRC,
        # 分组变量聚合器的每个 group 输出带一层 output 包装，选择器必须写三段。
        # 写两段拿到的是 {"output": ...} 这个 dict，下游 .strip() 当场抛
        # AttributeError（attempt01 实测）。m3_* 不走聚合器：uapp_delivery 只可能在
        # uapp_m3 之后到达（两条分支都在它下游），直接绑更准，也少一组聚合。
        [V("capability", ["uapp_route", "target_capability"]),
         V("seam_user_delivery", ["uapp_seam_merge", "user_delivery", "output"]),
         V("seam_outcome", ["uapp_seam_merge", "outcome", "output"]),
         V("seam_returns_json", ["uapp_seam_merge", "returns_json", "output"]),
         V("m3_judgment", ["uapp_m3", "operating_judgment"]),
         V("m3_gate_status", ["uapp_m3", "gate_status"]),
         V("route_mode", ["uapp_route", "route_mode"]),
         V("m2_note", ["uapp_ctx", "m2_note"]),
         V("hop_gaps_text", ["uapp_seam_merge", "hop_gaps", "output"]),
         V("account_context", ["uapp_ctx", "account_context"]),
         V("side_effect_text", ["uapp_noseam", "empty"])],
        ["final_text", "delivered_flag", "modules_actually_run", "leak_hits_json",
         "leak_hit_count", "m2_note"]), 300, 130))
    # 本轮产物写回会话，供下一跳当上游用。
    # 读端在上面（uapp_hop 的 upstream_delivery / upstream_capability），
    # 但 S4 首版只建了读端没建写端，于是 upstream_capability 恒为空、
    # 能力产出的 artifact 转手被丢弃——CREATIVE_SCRIPT / PRODUCTION_DIRECTOR /
    # PUBLISHING_PACKAGING 三项因此结构上永远拿不到上游产物（TRIAGE 004）。
    # 赋值项与继承参考建图 UAPP_BUILD_CANVAS_v1.0.py:655-658 逐字一致。
    # 写回闸门：真有产出才覆盖；空产出保留上一轮已确认的产物与能力身份。
    add.append(N("uapp_persist", X + 6920, Y + 320, code(
        "闸门｜只有真产出才写回",
        "能力停在缺口返回空产物时，保留上一轮已确认的产物与能力，不用空值覆盖",
        PERSIST_SRC,
        [V("new_artifact", ["uapp_seam_merge", "artifact", "output"]),
         V("new_capability", ["uapp_route", "target_capability"]),
         V("prev_artifact", ["conversation", "uapp_last_artifact"]),
         V("prev_capability", ["conversation", "uapp_last_capability"])],
        ["artifact_to_persist", "capability_to_persist", "persist_action"])))
    add.append(N("uapp_save", X + 7000, Y + 200, assigner(
        "记住｜本轮产物与能力", "供下一跳作为上游产出使用；业务真源在 M2，不在会话里",
        [("variable", ["uapp_persist", "artifact_to_persist"], "uapp_last_artifact"),
         ("variable", ["uapp_persist", "capability_to_persist"], "uapp_last_capability")])))
    add.append(N("uapp_answer_main", X + 7160, Y + 200,
                 answer("回复｜交付", "{{#uapp_delivery.final_text#}}")))
    edges.append(E("uapp_seam_merge", "uapp_delivery"))
    edges.append(E("uapp_delivery", "uapp_persist"))
    edges.append(E("uapp_persist", "uapp_save"))
    edges.append(E("uapp_save", "uapp_answer_main"))

    # 组件失败只影响这一支：Hop 与 Seam 各自的 fail-branch 归到同一个如实交代节点。
    add.append(N("uapp_cap_fail", X + 6520, Y + 440, code(
        "局部 Return｜能力链失败", "只影响这一支；不猜原因，不把失败说成业务结论",
        NODES.TOOLFAIL_SRC,
        [V("which", ["uapp_route", "target_capability"]),
         V("error_text", ["uapp_seam", "error"])],
        ["final_text", "failed_stage", "error_kept"])))
    add.append(N("uapp_answer_capfail", X + 6840, Y + 440,
                 answer("回复｜这一步没跑完", "{{#uapp_cap_fail.final_text#}}")))
    edges.append(E("uapp_seam", "uapp_cap_fail", "fail-branch"))
    edges.append(E("uapp_hop", "uapp_cap_fail", "fail-branch"))
    edges.append(E("uapp_cap_fail", "uapp_answer_capfail"))

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
    with io.open(os.path.join(HERE, "..", "dsl", "S4_PROGRESSIVE_CANVAS_v1.0.yml"), "w",
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
        "marked_name": "s4-seam-wired",
        "marked_comment": "S4：接入 Hop 与最终 FP Seam，打通六项专业能力；"
                          "Hop/Seam 失败走局部 Return；本层仍未接 M5 写回与闭环"}, timeout=600)
    assert st in (200, 201), ("publish", st, json.dumps(pub, ensure_ascii=False)[:800])

    report = {
        "stage": "S4", "app_id": app_id, "import_status": imp.get("status"),
        "import_was_update_in_place": True,
        "node_count": len(graph["nodes"]), "edge_count": len(graph["edges"]),
        "node_ids": sorted(n["id"] for n in graph["nodes"]),
        "graph_sha256": hashlib.sha256(json.dumps(graph, ensure_ascii=False, sort_keys=True)
                                       .encode("utf-8")).hexdigest(),
        "dsl_sha256": hashlib.sha256(dsl_text.encode("utf-8")).hexdigest(),
        "new_this_layer": ["uapp_op_gate", "uapp_hop", "uapp_seam", "uapp_noseam",
                           "uapp_seam_merge", "uapp_delivery", "uapp_persist", "uapp_save",
                           "uapp_answer_main",
                           "uapp_cap_fail", "uapp_answer_capfail"],
        "removed_this_layer": ["uapp_s3_deliver", "uapp_answer_main(S3 薄交付版)"],
        "bindings": {"hop": {"provider": PROVIDER_HOP, "target_app": HOP_APP},
                     "seam": {"provider": PROVIDER_SEAM, "target_app": SEAM_APP}},
        "six_capabilities_dispatch": "在 Seam 内部（seam_dispatch），画布只传 capability；"
                                     "画布侧接线一条，不是六条",
        "m3_reference_digests": ref_digests,
        "layers_not_yet_wired": ["M5 写回与闭环"],
    }
    print(json.dumps({k: report[k] for k in
                      ("stage", "app_id", "import_status", "node_count", "edge_count",
                       "graph_sha256", "dsl_sha256", "new_this_layer", "removed_this_layer",
                       "bindings")}, ensure_ascii=False, indent=2))
    ev = os.path.join(HERE, "..", "evidence")
    n = 1
    while os.path.exists(os.path.join(ev, "S4_BUILD_%02d.json" % n)):
        n += 1
    report["build_attempt"] = n
    with io.open(os.path.join(ev, "S4_BUILD_%02d.json" % n), "w", encoding="utf-8") as fh:
        fh.write(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    return app_id


if __name__ == "__main__":
    main()
