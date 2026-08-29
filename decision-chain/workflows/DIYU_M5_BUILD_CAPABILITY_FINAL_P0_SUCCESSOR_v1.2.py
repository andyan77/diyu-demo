#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""N2＋N3 · 六个能力 successor ＋ 接缝 successor：交付层泄漏与保真。

**不覆盖任何已接受应用，也不覆盖 v1.1.3 候选里的 rb 应用。** 另建七个任务命名的
successor，只动下面四处，其余节点原样照搬已发布 graph。

为什么是六个而不是只改 CONTENT_BRIEF：三处缺陷都落在**六能力逐字节共享**的同一份
资产上（见 decision-chain/evidence/m5/FINAL_P0_TRIAGE_NODE_BINDING.json）：
  returns_adapter 归一化后六比六全等；LEAK_PATTERNS 全等；delivery_finalize 全等；
  `status: READY | NEEDS_DECISION | BLOCKED_LOCAL` 模板行六个能力各出现一次。
只改一个能力等于把共享节点叉成两份，其余五个继续漏。

P1 —— 泄漏的最高节点：模板自己要求写 `status:`。
    USER_DELIVERY 块的规格里先写「status: READY | NEEDS_DECISION | BLOCKED_LOCAL」，
    紧接着又写「禁止出现：内部术语与状态码」。模型照字面执行了前一句。
    现场核验：NEEDS_DECISION / BLOCKED_LOCAL 在每张能力图里都只出现这一次，
    接缝与 M5 运行侧零引用 —— 没有任何下游消费它，删掉不丢信息（运行状态在 Artifact 块里）。

P2 —— 判断层→交付层保真。上游 professional_input 逐字带着 M3 的「只重建该重建的」，
    交付正文仍写成「整轮重跑了」。规则写在同一块规格里，与 P1 同处一个共享节点。

P3 —— returns_adapter 的状态词泄漏检查。原表只覆盖 STALE 与 NOT_VERIFIED 两个状态词，
    READY 等 14 个不在表内。补成宪法 §4 全集 ＋ `key: VALUE` 结构行检测。
    **不是案例白名单**：不针对任何具体串，按状态词全集与字段行形态判。

P4 —— delivery_finalize 的那份 LEAK 表只在恢复分支生效，正常分支根本不执行。
    补同一份状态词全集，两条路径口径一致。

不新增闸门、不新增状态词本体。READY 只作为「禁止出现在用户可见输出」的泄漏标记。
"""
import hashlib, importlib.util, json, os, re, subprocess, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
_s = importlib.util.spec_from_file_location(
    "dc", os.path.join(ROOT, "account-operations", "tools", "dify_client.py"))
DC = importlib.util.module_from_spec(_s); _s.loader.exec_module(DC)

ENV = "/home/faye/diyu-demo-worktrees/m3-account-content-operator-v1/.env"
MARKED_NAME = "m5fp-delivery-v1.2"
MARKED_COMMENT = ("M5 最后一轮最小修复 N2+N3：删除 USER_DELIVERY 块规格里的 status 行、"
                  "补判断层保真条款、补状态词泄漏检查全集与结构行检测。不新增闸门与状态词。")

SOURCE = [
    ("MATRIX",               "47e52165-f6cb-48ff-93be-6c6a8ea5cecf", "diyu_m5rb_matrix"),
    ("CAMPAIGN",             "7d10e28d-30e6-4c4a-950b-88dcbb5fd0fc", "diyu_m5rb_campaign"),
    ("CONTENT_BRIEF",        "cbbeab61-a4de-4a21-a6be-7dc2385dd6f3", "diyu_m5rb_content_brief"),
    ("CREATIVE_SCRIPT",      "4fbcfea8-48a3-41b3-b2b5-cdb50276eeb2", "diyu_m5rb_creative_script"),
    ("PRODUCTION_DIRECTOR",  "07e99f7b-71a3-40af-85f3-fc43b68e774a", "diyu_m5rb_production_director"),
    ("PUBLISHING_PACKAGING", "0fb7636a-55e8-49a9-92f7-3d11ad0a35fa", "diyu_m5rb_publishing_packaging"),
]
SEAM_SOURCE = "9e1b1fd8-f696-436d-9d42-54700a29a4dd"

# ---------------------------------------------------------------- P1 + P2
OLD_UD = ("---M4_USER_DELIVERY---\n"
          "status: READY | NEEDS_DECISION | BLOCKED_LOCAL\n"
          "（自然、完整、可直接使用的结果；")
NEW_UD = ("---M4_USER_DELIVERY---\n"
          "（**这一块是给用户看的正文，不是记账。不要写 `status:`，也不要写任何"
          "`字段名: 值` 形式的字段行**——运行状态、结论强度这类记账信息属于上面的 Artifact 块。\n"
          " **忠实于上游判断。** `professional_input` 里的上游判断说了只重建受影响的部分、"
          "或者明确拒绝了用户的某个要求时，本块必须保留那个范围和那个拒绝理由："
          "说清实际做了什么、哪些保留了、为什么保留。**不得把用户的原话当成已执行的事实回述**"
          "（例如上游判定只需局部重建，正文却写成「整轮重跑了」「从头跑完了」）。"
          "用户当然可以坚持，但那是下一步要他确认的选择，不是本轮已经发生的事。\n"
          " 自然、完整、可直接使用的结果；")

# ---------------------------------------------------------------- P3
RA_ANCHOR = ('    "INPUT_INSUFFICIENT", "STALE", "NOT_VERIFIED", "fact_refs[]", "used_fact_refs",\n]')
RA_ADD = '''    "INPUT_INSUFFICIENT", "STALE", "NOT_VERIFIED", "fact_refs[]", "used_fact_refs",
]

# 统一状态词（宪法 §4）。它们是内部记账词，不是用户交付语言。
# 这里只把它们当作「禁止出现在用户可见输出」的泄漏标记，不新增任何状态词本体。
STATE_WORDS = ("NOT_VERIFIED", "NOT_APPLICABLE", "NOT_STARTED", "IN_PROGRESS",
               "COMPLETED", "APPLICABLE", "FAILED", "BLOCKED", "PARTIAL",
               "INVALID", "CURRENT", "STALE", "READY", "PASS", "FAIL", "DONE")

# 结构性泄漏：`key: VALUE` 这种字段行本身就是内部记账形态。
# 不枚举键名——枚举一定漏，形态不会。这也是上一轮 `status: READY` 漏检的原因：
# 旧表只列了两个状态词，READY 不在表里，于是整行被判为 OK。
_STATE_LINE = re.compile(
    r"^[ \\t]*[A-Za-z_][A-Za-z0-9_]*[ \\t]*[:\\uff1a][ \\t]*[A-Z][A-Z0-9_]{2,}[ \\t]*$", re.M)
_STATE_TOKEN = re.compile(
    r"(?<![A-Za-z0-9_])(?:%s)(?![A-Za-z0-9_])" % "|".join(STATE_WORDS))


def _state_leaks(text):
    """通用状态词泄漏检查。不针对任何具体案例串，不设白名单。"""
    t = text or ""
    out = []
    if _STATE_LINE.search(t):
        out.append("STATE_FIELD_LINE")
    out += sorted({"STATE_WORD:" + m.group(0) for m in _STATE_TOKEN.finditer(t)})
    return out'''

RA_OLD_CALL = "    leaks = [p for p in LEAK_PATTERNS if user_delivery and p in user_delivery]"
RA_NEW_CALL = ("    leaks = [p for p in LEAK_PATTERNS if user_delivery and p in user_delivery]\n"
               "    leaks = sorted(set(leaks) | set(_state_leaks(user_delivery)))")

# ---------------------------------------------------------------- P4
DF_ANCHOR = ('        "<think>", "</think>", "dify-deepseek-reasoning"]')
DF_ADD = '''        "<think>", "</think>", "dify-deepseek-reasoning"]

# 与 returns_adapter 同一份状态词全集。两条路径口径必须一致：
# 上一轮 delivery_finalize 的 LEAK 表只在恢复分支生效，正常分支根本不执行，
# 于是「正常路径产出的泄漏」两道检查都没拦住。
STATE_WORDS = ("NOT_VERIFIED", "NOT_APPLICABLE", "NOT_STARTED", "IN_PROGRESS",
               "COMPLETED", "APPLICABLE", "FAILED", "BLOCKED", "PARTIAL",
               "INVALID", "CURRENT", "STALE", "READY", "PASS", "FAIL", "DONE")
LEAK = LEAK + list(STATE_WORDS)'''


def psql(q):
    p = subprocess.run(["docker", "exec", "-i", "docker-db_postgres-1", "psql", "-U", "postgres",
                        "-d", "dify", "-t", "-A", "-c", q], capture_output=True, text=True, timeout=300)
    if p.returncode != 0:
        raise RuntimeError(p.stderr[:400])
    return p.stdout


def published_graph(app_id):
    return json.loads(psql("SELECT graph FROM workflows WHERE app_id='%s' AND version<>'draft' "
                           "ORDER BY created_at DESC LIMIT 1;" % app_id).strip())


def draft_features(app_id):
    r = psql("SELECT features FROM workflows WHERE app_id='%s' AND version<>'draft' "
             "ORDER BY created_at DESC LIMIT 1;" % app_id).strip()
    return json.loads(r) if r else {}


def patch(g):
    """四处修改，每处都断言命中次数，漏改必须报错而不是安静通过。"""
    done = {"P1P2": 0, "P3_list": 0, "P3_call": 0, "P4": 0}
    for n in g.get("nodes", []):
        d = n.get("data") or {}
        if d.get("type") == "llm":
            for pt in d.get("prompt_template") or []:
                t = pt.get("text") or ""
                if OLD_UD in t:
                    if t.count(OLD_UD) != 1:
                        raise RuntimeError("USER_DELIVERY 规格块不唯一")
                    pt["text"] = t.replace(OLD_UD, NEW_UD, 1)
                    done["P1P2"] += 1
        if d.get("type") == "code":
            c = d.get("code") or ""
            if n["id"] == "returns_adapter":
                if RA_ANCHOR not in c or c.count(RA_OLD_CALL) != 1:
                    raise RuntimeError("returns_adapter 锚点未命中")
                c = c.replace(RA_ANCHOR, RA_ADD, 1)
                done["P3_list"] += 1
                c = c.replace(RA_OLD_CALL, RA_NEW_CALL, 1)
                done["P3_call"] += 1
                d["code"] = c
            elif n["id"] == "delivery_finalize":
                if c.count(DF_ANCHOR) != 1:
                    raise RuntimeError("delivery_finalize 锚点未命中")
                c = c.replace(DF_ANCHOR, DF_ADD, 1)
                if not c.lstrip().startswith("import json"):
                    raise RuntimeError("delivery_finalize 头部与预期不符")
                done["P4"] += 1
                d["code"] = c
    if done != {"P1P2": 1, "P3_list": 1, "P3_call": 1, "P4": 1}:
        raise RuntimeError("四处修改必须各命中一次，实得 %s" % done)
    return g, done


def upsert_app(c, name, desc, icon="🧩"):
    st, apps = c.call("GET", "/console/api/apps?page=1&limit=100")
    assert st == 200
    hit = [a for a in apps["data"] if a.get("name") == name]
    if hit:
        return hit[0]["id"], False
    st, app = c.call("POST", "/console/api/apps", body={
        "name": name, "mode": "workflow", "icon_type": "emoji", "icon": icon,
        "icon_background": "#E4FBCC", "description": desc})
    assert st in (200, 201), (st, app)
    return app["id"], True


def sync_and_publish(c, app_id, graph, features):
    st, cur = c.call("GET", "/console/api/apps/%s/workflows/draft" % app_id)
    prev = cur.get("hash") if st == 200 else None
    st, res = c.call("POST", "/console/api/apps/%s/workflows/draft" % app_id, body={
        "graph": graph, "features": features, "hash": prev,
        "environment_variables": [], "conversation_variables": []}, timeout=600)
    assert st == 200, ("draft sync failed", st, json.dumps(res, ensure_ascii=False)[:400])
    st, pub = c.call("POST", "/console/api/apps/%s/workflows/publish" % app_id,
                     body={"marked_name": MARKED_NAME, "marked_comment": MARKED_COMMENT}, timeout=600)
    assert st in (200, 201), ("publish failed", st, json.dumps(pub, ensure_ascii=False)[:400])


def provider_row(pid):
    r = psql("SELECT row_to_json(t) FROM (SELECT label, icon, description, parameter_configuration, "
             "privacy_policy FROM tool_workflow_providers WHERE id='%s') t;" % pid).strip()
    return json.loads(r)


def main():
    c = DC.Console(env=DC.load_env(ENV))
    out = {"node": "N2+N3", "successors": {}, "providers": {}, "patches": {}}

    for cap, src, prov in SOURCE:
        g = published_graph(src)
        g, done = patch(g)
        st, meta = c.call("GET", "/console/api/apps/%s" % src)
        assert st == 200
        app_id, created = upsert_app(
            c, "DIYU M5 FP · %s" % meta["name"],
            "M5 最后一轮最小修复：交付块规格去 status 行＋保真条款，泄漏检查补状态词全集。")
        sync_and_publish(c, app_id, g, draft_features(src))
        md5 = psql("SELECT md5(graph) FROM workflows WHERE app_id='%s' AND version<>'draft' "
                   "ORDER BY created_at DESC LIMIT 1;" % app_id).strip()
        out["successors"][cap] = {"source_app": src, "successor_app": app_id,
                                  "created": created, "graph_md5": md5}
        out["patches"][cap] = done
        print("%-22s successor=%s md5=%s %s" % (cap, app_id, md5, done), flush=True)

        pid = psql("SELECT id FROM tool_workflow_providers WHERE name='%s';" % prov).strip()
        row = provider_row(pid)
        new_name = prov.replace("diyu_m5rb_", "diyu_m5fp_")
        exist = psql("SELECT id FROM tool_workflow_providers WHERE name='%s';" % new_name).strip()
        if not exist:
            st, r = c.call("POST", "/console/api/workspaces/current/tool-provider/workflow/create",
                           body={"workflow_app_id": app_id, "name": new_name,
                                 "label": "DIYU M5 FP · " + row["label"],
                                 "icon": json.loads(row["icon"]) if isinstance(row["icon"], str) else row["icon"],
                                 "description": row["description"],
                                 "parameters": json.loads(row["parameter_configuration"]),
                                 "privacy_policy": row.get("privacy_policy") or "", "labels": []})
            assert st in (200, 201), ("provider create failed", st, str(r)[:400])
            exist = psql("SELECT id FROM tool_workflow_providers WHERE name='%s';" % new_name).strip()
        out["providers"][cap] = {"source_provider": pid, "successor_provider": exist,
                                 "tool_name": new_name}
        print("%-22s provider=%s (%s)" % (cap, exist, new_name), flush=True)

    # ---- 接缝 successor：只把 6 个 tool 节点改指新 provider
    sg = published_graph(SEAM_SOURCE)
    remap = {out["providers"][k]["source_provider"]: out["providers"][k] for k in out["providers"]}
    changed = []
    for n in sg.get("nodes", []):
        d = n.get("data") or {}
        if d.get("type") != "tool":
            continue
        pid = d.get("provider_id")
        if pid not in remap:
            raise RuntimeError("接缝 tool 节点指向未知 provider：%s (%s)" % (n["id"], pid))
        r = remap[pid]
        d["provider_id"] = r["successor_provider"]
        d["provider_name"] = r["successor_provider"]
        d["tool_name"] = r["tool_name"]
        d["tool_label"] = r["tool_name"]
        changed.append(n["id"])
    if len(changed) != 6:
        raise RuntimeError("期望改 6 个 tool 节点，实得 %d" % len(changed))
    st, meta = c.call("GET", "/console/api/apps/%s" % SEAM_SOURCE)
    seam_id, created = upsert_app(c, "DIYU M5 FP · %s" % meta["name"],
                                  "M5 最后一轮最小修复接缝：只把 6 个 tool 节点改指新能力 successor。",
                                  icon="🔗")
    sync_and_publish(c, seam_id, sg, draft_features(SEAM_SOURCE))
    seam_md5 = psql("SELECT md5(graph) FROM workflows WHERE app_id='%s' AND version<>'draft' "
                    "ORDER BY created_at DESC LIMIT 1;" % seam_id).strip()
    out["seam"] = {"source_app": SEAM_SOURCE, "successor_app": seam_id, "created": created,
                   "graph_md5": seam_md5, "tool_nodes_remapped": changed}
    print("SEAM successor=%s md5=%s" % (seam_id, seam_md5))

    # ---- 保护面复算：源应用一个字节都不许动
    src_after = {}
    for cap, s, _ in SOURCE:
        src_after[cap] = psql("SELECT md5(graph) FROM workflows WHERE app_id='%s' AND version<>'draft' "
                              "ORDER BY created_at DESC LIMIT 1;" % s).strip()
    src_after["SEAM"] = psql("SELECT md5(graph) FROM workflows WHERE app_id='%s' AND version<>'draft' "
                             "ORDER BY created_at DESC LIMIT 1;" % SEAM_SOURCE).strip()
    out["source_apps_graph_md5_after"] = src_after

    p = os.path.join(ROOT, "decision-chain", "evidence", "m5", "FINAL_P0_CAPABILITY_SUCCESSOR_BUILD.json")
    json.dump(out, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print("SAVED", p)
    return 0


if __name__ == "__main__":
    sys.exit(main())
