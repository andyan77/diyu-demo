#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""统一 Founder Canvas · 确定性预检。零模型调用、零写入。

每一项都是可复算的比对：图身份、载体副本同步、provider 绑定、保护面零漂移、
六能力路由可达、泄漏防线正负控制。**确定性检查失败不得靠模型多跑几次绕过。**
"""
import hashlib
import importlib.util
import io
import ast
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
APP_ID = "2448e4f9-818f-4b88-9311-d18546e97da9"

OLD_CANVAS = "f0b1c5f5-afc5-43e9-9ea4-ae36e25f33c8"
OLD_SEAM_PROVIDER = "2daa2d27-4305-4d24-95ec-3cb424eaeb2f"
# 建应用之前现场复算的保护面基线（本任务激活时与建应用前两次一致）。
PROTECTED_BASELINE = {
    "old_canvas_graph_md5": "67b717d1365c2fb75a3b8e761b0527da",
    "old_seam_provider_app": "de0cb1e9-2af8-415a-9762-31b6cf348c22",
    "old_seam_provider_version": "2026-08-27 20:36:22.268824",
    "fp_graph_md5": {
        "fd25ebfa-db67-40c3-82e5-202e1254facf": "6cdaeac9cacf69fbeea4bd25e1536ace",
        "1f9d65ea-8af5-45f0-a1d0-a80223d354e2": "4876dacc43a73741b41c5a3083796347",
        "b1dcf784-540e-4b3f-8ba2-3812f477f3ce": "0c841642a71feedfb327ffb76aec0ddd",
        "44b55f9d-3792-40c3-b095-f2696464b4ec": "a1cd859d5b88d0d025f336665ca94e51",
        "13cfabd5-f592-4354-a304-47098b765697": "964e9a947dc9790d1de82496469689ad",
        "c9cdea24-9df3-400b-9ecd-1d740e8c96df": "788c8555aca09e6fa6d979f237f70157",
        "5fca0162-e26b-4545-a00b-66b1a2a2a077": "db49a3da8973d4fdcbe9ecf63bdf7e2a",
        "a4c3b19b-243f-490b-9aca-3aa19767d6a5": "cd93757bcf8ad322f3b32fc43b2da3ff",
        "6c46fdb1-5f49-4513-a0c0-29957b3dcee4": "d230b62fc9ebea1c7ee2426f13f9d279",
    },
    "providers": {
        "diyu_uapp_m3": "a4c3b19b-243f-490b-9aca-3aa19767d6a5",
        "diyu_uapp_seam": "5fca0162-e26b-4545-a00b-66b1a2a2a077",
        "diyu_uapp_hop": "6c46fdb1-5f49-4513-a0c0-29957b3dcee4",
    },
}
CAP6 = ["MATRIX", "CAMPAIGN", "CONTENT_BRIEF", "CREATIVE_SCRIPT",
        "PRODUCTION_DIRECTOR", "PUBLISHING_PACKAGING"]
M3_REF_FILES = [("references/fashion-and-market.md", "fashion-and-market.md"),
                ("references/six-skill-methods.md", "six-skill-methods.md"),
                ("references/operations.md", "operations.md")]

RESULTS = []


def check(cid, desc, ok, detail):
    RESULTS.append({"id": cid, "desc": desc, "result": "PASS" if ok else "FAIL",
                    "detail": detail})


def psql(sql, db="dify"):
    p = subprocess.run(["docker", "exec", "-i", "docker-db_postgres-1", "psql", "-U", "postgres",
                        "-d", db, "-tA", "-c", sql], capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError("psql: " + (p.stderr or "")[:300])
    return p.stdout.strip()


def sha(b):
    return hashlib.sha256(b if isinstance(b, bytes) else b.encode("utf-8")).hexdigest()


def main():
    row = psql("select a.mode||'|'||a.status||'|'||a.enable_site::text||'|'||a.enable_api::text"
               "||'|'||md5(w.graph)||'|'||coalesce(w.marked_name,'') "
               "from apps a join workflows w on w.id=a.workflow_id where a.id='%s';" % APP_ID)
    mode, status, site, api, gmd5, marked = row.split("|")
    # psql 的 ::text 转换给出 true/false，裸列给出 t/f；两种都认，判据是布尔真值本身。
    truthy = ("t", "true")
    check("D-01", "新应用 mode=advanced-chat、已发布、Site/API 可用",
          mode == "advanced-chat" and status == "normal"
          and site in truthy and api in truthy,
          {"mode": mode, "status": status, "enable_site": site, "enable_api": api,
           "graph_md5": gmd5, "published_version_name": marked})

    graph = json.loads(psql("select w.graph from workflows w join apps a on a.workflow_id=w.id "
                            "where a.id='%s';" % APP_ID))
    nodes = {n["id"]: n for n in graph["nodes"]}
    ids = set(nodes)

    dangling = [e for e in graph["edges"] if e["source"] not in ids or e["target"] not in ids]
    adj = {}
    for e in graph["edges"]:
        adj.setdefault(e["source"], []).append(e["target"])
    seen, stack = {"uapp_start"}, ["uapp_start"]
    while stack:
        for t in adj.get(stack.pop(), []):
            if t not in seen:
                seen.add(t)
                stack.append(t)
    check("D-02", "图结构自洽：无悬空边、无不可达节点",
          not dangling and not (ids - seen),
          {"nodes": len(ids), "edges": len(graph["edges"]),
           "dangling": dangling, "unreachable": sorted(ids - seen)})

    # ---- 载体副本同步（A3）----
    repo_m1 = io.open(os.path.join(ROOT, "decision-chain", "workflows",
                                   "m1_context_compiler_v0.1.py"), "rb").read()
    graph_m1 = nodes["m1_compiler"]["data"]["code"]
    check("D-03", "图内 M1 编译器与仓库源码逐字节一致",
          sha(repo_m1) == sha(graph_m1),
          {"repo_sha256": sha(repo_m1), "graph_sha256": sha(graph_m1),
           "repo_bytes": len(repo_m1), "graph_bytes": len(graph_m1.encode("utf-8"))})

    ctx_code = nodes["uapp_ctx"]["data"]["code"]
    ref_dir = os.path.join(ROOT, "m3-account-content-operator-semantic-v1.0",
                           "skill-source", "references")
    embedded = re.search(r"^_REFS = (.+)$", ctx_code, re.M)
    emb = json.loads(embedded.group(1)) if embedded else []
    emb_map = {p: b for p, b in emb}
    ref_rows, ref_ok = [], True
    for manifest_path, fname in M3_REF_FILES:
        disk = io.open(os.path.join(ref_dir, fname), "rb").read()
        got = emb_map.get(manifest_path)
        same = got is not None and sha(got) == sha(disk)
        ref_ok = ref_ok and same
        ref_rows.append({"path": manifest_path, "repo_sha256": sha(disk),
                         "graph_sha256": sha(got) if got is not None else None, "same": same})
    check("D-04", "图内 M3 方法参考与仓库文件逐字节一致", ref_ok, ref_rows)
    declares_not_loaded = "acceptance-fixtures.md: NOT_LOADED" in ctx_code
    body_absent = not any("acceptance-fixtures" in p for p in emb_map)
    check("D-05", "M3 验收夹具如实声明未加载，且正文确实没有被嵌进输入",
          declares_not_loaded and body_absent,
          {"manifest_declares_not_loaded": declares_not_loaded,
           "acceptance_fixture_body_absent": body_absent,
           "embedded_bodies": list(emb_map)})

    # ---- provider 绑定 ----
    prov_rows, prov_ok = [], True
    for name, want_app in PROTECTED_BASELINE["providers"].items():
        got = psql("select p.id||'|'||p.app_id||'|'||p.version from tool_workflow_providers p "
                   "where p.name='%s';" % name)
        pid, papp, pver = (got.split("|") + ["", "", ""])[:3] if got else ("", "", "")
        cur = psql("select w.version::text from workflows w join apps a on a.workflow_id=w.id "
                   "where a.id='%s';" % want_app)
        ok = papp == want_app and pver == cur
        prov_ok = prov_ok and ok
        prov_rows.append({"provider": name, "id": pid, "bound_app": papp,
                          "provider_version": pver, "target_published_version": cur, "ok": ok})
    check("D-06", "三个任务 provider 仍绑定准确目标且版本与目标当前发布版一致",
          prov_ok, prov_rows)

    used = {}
    for nid in ("uapp_m3", "uapp_hop", "uapp_seam"):
        used[nid] = nodes[nid]["data"]["provider_id"]
    check("D-07", "新画布的三个工具节点使用的正是这三个任务 provider",
          set(used.values()) == {psql("select id from tool_workflow_providers where name='%s';" % n)
                                 for n in PROTECTED_BASELINE["providers"]},
          used)

    # ---- 保护面零漂移 ----
    now_old = psql("select md5(w.graph) from apps a join workflows w on w.id=a.workflow_id "
                   "where a.id='%s';" % OLD_CANVAS)
    op = psql("select p.app_id||'|'||p.version from tool_workflow_providers p where p.id='%s';"
              % OLD_SEAM_PROVIDER)
    op_app, op_ver = op.split("|")
    fp_now = {}
    for aid in PROTECTED_BASELINE["fp_graph_md5"]:
        fp_now[aid] = psql("select md5(w.graph) from apps a join workflows w "
                           "on w.id=a.workflow_id where a.id='%s';" % aid)
    drift = {k: (PROTECTED_BASELINE["fp_graph_md5"][k], v)
             for k, v in fp_now.items() if PROTECTED_BASELINE["fp_graph_md5"][k] != v}
    check("D-08", "旧 Canvas、旧 provider、最终 FP 八应用与 hop 适配器零漂移",
          now_old == PROTECTED_BASELINE["old_canvas_graph_md5"]
          and op_app == PROTECTED_BASELINE["old_seam_provider_app"]
          and op_ver == PROTECTED_BASELINE["old_seam_provider_version"] and not drift,
          {"old_canvas_md5": now_old, "old_provider_app": op_app, "old_provider_version": op_ver,
           "fp_drift": drift})

    # ---- 六能力路由可达 ----
    route_code = nodes["uapp_route"]["data"]["code"]
    seam_params = nodes["uapp_seam"]["data"]["tool_parameters"]
    routable = [c for c in CAP6 if ('"%s"' % c) in route_code]
    check("D-09", "六项能力都在统一路由的可达集合内，且 capability 来自路由输出",
          routable == CAP6
          and seam_params["capability"]["value"] == "{{#uapp_route.target_capability#}}",
          {"routable": routable,
           "seam_capability_binding": seam_params["capability"]["value"],
           "seam_entry_binding": seam_params["entry"]["value"]})

    check("D-10", "画布不固定全链：能力调用挂在条件分支后，不是无条件串行",
          any(n["data"]["type"] == "if-else" for n in graph["nodes"])
          and any(e["source"] == "uapp_op_gate" and e["sourceHandle"] == "capability"
                  and e["target"] == "uapp_hop" for e in graph["edges"]),
          {"if_else_nodes": [n["id"] for n in graph["nodes"]
                             if n["data"]["type"] == "if-else"]})

    # ---- 用户不填内部字段 ----
    check("D-11", "start 节点零用户输入变量；用户只说自然语言",
          nodes["uapp_start"]["data"].get("variables") == [],
          {"start_variables": nodes["uapp_start"]["data"].get("variables")})

    # ---- 泄漏防线正负控制（纯本地，零模型）----
    guard = nodes["uapp_delivery"]["data"]["code"]
    ns = {}
    exec(compile(guard, "<guard>", "exec"), ns)
    scrub = ns["_scrub"]
    dirty = ("状态 READY，business_delivery_outcome=DELIVERED，capability=CONTENT_BRIEF，"
             "见 ENTRY-03，节点 uapp_seam，app 5fca0162-e26b-4545-a00b-66b1a2a2a077，"
             "returns_json 为空，<think>内部</think>")
    clean_in = "这周先把主推商品定下来，我建议从秋冬新款里挑一件做主线，其余两条做辅助。"
    d_out, d_hits = scrub(dirty)
    c_out, c_hits = scrub(clean_in)
    leftovers = [t for t in ("READY", "DELIVERED", "CONTENT_BRIEF", "ENTRY-03", "uapp_seam",
                             "5fca0162", "returns_json", "<think>") if t in d_out]
    check("D-12", "泄漏防线双向可区分：脏输入被清干净，干净正文零改动",
          not leftovers and len(d_hits) > 0 and c_out == clean_in and c_hits == [],
          {"negative_control_leftovers": leftovers, "negative_control_hits": len(d_hits),
           "positive_control_unchanged": c_out == clean_in, "positive_control_hits": c_hits,
           "scrubbed_sample": d_out[:200]})

    # ---- 正常使用不依赖外部 Python ----
    blob = json.dumps(graph, ensure_ascii=False)
    forbidden = [t for t in ("DIYU_M5_INTEGRATION_RUNTIME", "docker exec", "M5_BIND",
                             "subprocess") if t in blob]
    check("D-13", "图内不引用任何外部手工编排运行时", not forbidden, {"hits": forbidden})

    # ---- 写回纪律 ----
    blob_nodes = {nid: json.dumps(n["data"], ensure_ascii=False) for nid, n in nodes.items()}
    prep = nodes["uapp_wb_prep"]["data"]["code"]
    # 取原始 body 模板串本身；json.dumps 过的整节点会把内层引号转义掉，比对必然假阴。
    fb_body = nodes["wb_feedback"]["data"]["body"]["data"][0]["value"]
    # 功能性验证：请求体现在由组装节点产出，光比字符串会假阴。直接把模板喂进组装函数，
    # 看 is_test / is_simulated 是否真的活到最终请求体里。
    ns_b = {}
    exec(compile(nodes["uapp_pub_body"]["data"]["code"], "<body>", "exec"), ns_b)
    ns_p = {}
    exec(compile(prep, "<prep>", "exec"), ns_p)
    tpl = ns_p["main"]("NONE", "x", "CONTENT_BRIEF", "", "", "观察到的反馈", "t", "acc",
                       "tg", "cyc", "DELIVERED")
    pub_final = json.loads(ns_b["main"](tpl["publish_body_template"], "ver-1", "",
                                        "content_version_id", "false")["body"])
    fb_final = json.loads(ns_b["main"](tpl["feedback_body_template"], "", "",
                                       "publish_instance_id", "true")["body"])
    check("D-14", "发布与反馈的最终请求体里 is_test / is_simulated 均为真，不靠 M2 默认值",
          pub_final.get("is_test") is True and pub_final.get("is_simulated") is True
          and fb_final.get("is_test") is True and fb_final.get("is_simulated") is True,
          {"publish_body_final": pub_final, "feedback_body_final": fb_final})

    check("D-20", "取不到跨轮 id 时字段被整个去掉，不填空串骗 M2",
          "publish_instance_id" not in fb_final
          and json.loads(ns_b["main"](tpl["feedback_body_template"], "", "pub-9",
                                      "publish_instance_id", "true")["body"]
                         ).get("publish_instance_id") == "pub-9",
          {"dropped_when_absent": "publish_instance_id" not in fb_final,
           "carried_when_present": json.loads(ns_b["main"](
               tpl["feedback_body_template"], "", "pub-9", "publish_instance_id",
               "true")["body"]).get("publish_instance_id")})

    ns2 = {}
    exec(compile(nodes["uapp_wb_prep"]["data"]["code"], "<wb>", "exec"), ns2)
    wb = ns2["main"]
    ART = "一份真实产物正文"
    got_del = wb("NONE", ART, "CONTENT_BRIEF", "", "", "", "t", "a", "tg", "c", "DELIVERED")
    got_rec = wb("NONE", ART, "CONTENT_BRIEF", "", "", "", "t", "a", "tg", "c",
                 "DELIVERED_AFTER_RECOVERY")
    got_undel = wb("NONE", ART, "CONTENT_BRIEF", "", "", "", "t", "a", "tg", "c", "UNKNOWN")
    got_empty = wb("NONE", "", "CONTENT_BRIEF", "", "", "", "t", "a", "tg", "c", "DELIVERED")
    check("D-15", "只有真交付且有产物才登记版本：未交付或空产物一律不登记",
          got_del["should_persist_artifact"] == "true"
          and got_rec["should_persist_artifact"] == "true"
          and got_undel["should_persist_artifact"] == "false"
          and got_empty["should_persist_artifact"] == "false",
          {"delivered_with_artifact": got_del["should_persist_artifact"],
           "delivered_after_recovery": got_rec["should_persist_artifact"],
           "not_delivered": got_undel["should_persist_artifact"],
           "empty_artifact": got_empty["should_persist_artifact"]})

    # 同键判定必须喂同一段正文；此前这里喂了两段不同正文，是判据自己写错了。
    same = wb("NONE", ART, "CONTENT_BRIEF", "", "", "", "t", "a", "tg", "c", "DELIVERED")
    other = wb("NONE", "另一份完全不同的产物", "CONTENT_BRIEF", "", "", "", "t", "a", "tg", "c",
               "DELIVERED")
    check("D-16", "幂等键由内容派生：同产物同键、异产物异键",
          json.loads(same["version_body"])["idempotency_key"]
          == json.loads(got_del["version_body"])["idempotency_key"]
          and json.loads(other["version_body"])["idempotency_key"]
          != json.loads(same["version_body"])["idempotency_key"],
          {"same_key": json.loads(same["version_body"])["idempotency_key"],
           "other_key": json.loads(other["version_body"])["idempotency_key"]})

    ns3 = {}
    exec(compile(nodes["uapp_side"]["data"]["code"], "<se>", "exec"), ns3)
    se = ns3["main"]
    ok_row = se("RECORD_PUBLISH", "200", "200", "200", "", "", "", "", "", "")
    bad_row = se("RECORD_PUBLISH", "404", "", "", "", "", "", "{}", "", "")
    nil_row = se("NONE", "", "", "", "", "", "", "", "", "")
    check("D-17", "副作用陈述可区分：写成了/没写成/本轮没走，三态互不混淆",
          ok_row["any_write_happened"] == "true" and ok_row["any_write_failed"] == "false"
          and bad_row["any_write_failed"] == "true"
          and bad_row["any_write_happened"] == "false"
          and nil_row["side_effect_text"] == "",
          {"ok": ok_row["write_ledger_json"], "bad": bad_row["write_ledger_json"],
           "nil_text_empty": nil_row["side_effect_text"] == ""})

    check("D-18", "撤回陈述把四件事分开：未来复用 / 已发布内容 / 平台操作 / 实际写入",
          all(k in se("WITHDRAW_MATERIAL", "", "", "", "", "", "200", "", "", "")[
              "side_effect_text"]
              for k in ("不再用于新的内容", "已经发出去的内容不受影响",
                        "没有对平台做任何操作")),
          {"text": se("WITHDRAW_MATERIAL", "", "", "", "", "", "200", "", "",
                      "")["side_effect_text"]})

    # Dify 会因为「返回了没声明的键」或「声明了没返回的键」整节点判失败，
    # 而这类错只有跑到那一步才炸。静态比对一次，省掉一整轮模型调用。
    mismatch = []
    for nid, n in nodes.items():
        d = n["data"]
        if d.get("type") != "code":
            continue
        declared = set((d.get("outputs") or {}).keys())
        tree = ast.parse(d["code"])
        returned = set()
        for fn in ast.walk(tree):
            if isinstance(fn, ast.FunctionDef) and fn.name == "main":
                for st_ in ast.walk(fn):
                    if isinstance(st_, ast.Return) and isinstance(st_.value, ast.Dict):
                        for k in st_.value.keys:
                            if isinstance(k, ast.Constant):
                                returned.add(k.value)
        if returned and returned != declared:
            mismatch.append({"node": nid, "declared_only": sorted(declared - returned),
                             "returned_only": sorted(returned - declared)})
    check("D-19", "每个代码节点声明的 outputs 与 main() 实际返回的键完全一致",
          not mismatch, mismatch)

    # M2 的合法枚举，抄自它自己的校验错误原文，不靠记忆。
    M2_FEEDBACK_KINDS = ("observation", "interpretation", "decision")
    fb_kind = json.loads(tpl["feedback_body_template"]).get("kind")
    check("D-21", "反馈 kind 落在 M2 接受的枚举内", fb_kind in M2_FEEDBACK_KINDS,
          {"kind": fb_kind, "allowed": list(M2_FEEDBACK_KINDS)})

    ns_s = {}
    exec(compile(nodes["uapp_side"]["data"]["code"], "<se2>", "exec"), ns_s)
    ran_failed = ns_s["main"]("RECORD_FEEDBACK", "", "", "", "0", "", "", "", "", "")
    never_ran = ns_s["main"]("RECORD_FEEDBACK", "", "", "", "", "", "", "", "", "")
    check("D-22", "「跑了但失败」不会被当成「本轮没走」而藏起来",
          ran_failed["any_write_failed"] == "true"
          and never_ran["side_effect_text"] == "",
          {"http_failed_status_0": ran_failed["write_ledger_json"],
           "never_ran_text_empty": never_ran["side_effect_text"] == ""})

    failed = [r for r in RESULTS if r["result"] != "PASS"]
    out = {"app_id": APP_ID, "graph_md5": gmd5, "graph_sha256": sha(json.dumps(
        graph, ensure_ascii=False, sort_keys=True)),
        "checks": RESULTS, "passed": len(RESULTS) - len(failed), "failed": len(failed)}
    path = os.path.join(HERE, "..", "evidence", "UAPP_DETERMINISTIC_CHECKS.json")
    with io.open(path, "w", encoding="utf-8") as fh:
        fh.write(json.dumps(out, ensure_ascii=False, indent=2) + "\n")
    for r in RESULTS:
        print("%-6s %-5s %s" % (r["id"], r["result"], r["desc"]))
    print("\n%d PASS / %d FAIL" % (out["passed"], out["failed"]))
    print("SAVED", path)
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
