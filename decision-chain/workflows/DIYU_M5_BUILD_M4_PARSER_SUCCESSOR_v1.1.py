#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""M4 等价表达解析修复 · 任务命名的版本化 successor（RB-2 / F2）。

**不覆盖任何已接受的 M4 应用。** 已接受的八个应用一个字节都不动；这里另建
七个任务命名的 successor（六个能力 + 一个接缝），只把 `envelope_check` 里那一份
`_find_scalar` 换掉，其余节点原样照搬已发布 graph。改坏了就不绑定，随时可回退。

为什么是这七个而不是在下游打补丁：`_find_scalar` 在六个能力应用里逐字节同一份
（函数体 sha256 六比六全等），它就是最高共享失效节点。接缝之所以也要出 successor，
是因为接缝的 tool 节点按 provider_id 指向具体能力应用——不换接缝，换了的能力
根本不会被调用到。

旧解析器的三个缺陷（400 条真实语料 + 等价矩阵实测，见 RB-1 F2）：
  1. 值里含 ASCII 引号 → 整条正则不匹配，在场的字段被判成缺失；
  2. JSON 值里含转义引号 → 只取到第一个引号前的半截，**还判成功**（静默损坏）；
  3. `^\\s*key\\s*:\\s*` 里的 `\\s*` 会跨行 → **空字段把下一行当成自己的值**，
     必填闸门被静默绕过（真实语料里 3 处，方向是假 PASS）。
"""
import hashlib
import importlib.util
import json
import os
import re
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
_s = importlib.util.spec_from_file_location(
    "dc", os.path.join(ROOT, "account-operations", "tools", "dify_client.py"))
DC = importlib.util.module_from_spec(_s)
_s.loader.exec_module(DC)

ENV = "/home/faye/diyu-demo-worktrees/m3-account-content-operator-v1/.env"
MARKED_NAME = "m5rb-parser-v1.1"
MARKED_COMMENT = ("M5 AC-07 Rebase：等价表达解析修复。引号是包装不是分隔符；"
                  "键定位不跨行。等价 11/11 一致，负控制 5/5 仍失败，"
                  "400 条真实语料差分未解释项 0。")

SOURCE = [
    ("MATRIX", "d7c2cc11-9a59-47eb-93d7-a25ebc0b8cc3", "diyu_m4_matrix"),
    ("CAMPAIGN", "cfd48281-d2e6-4f77-b4a6-32f0fca98f2b", "diyu_m4_campaign"),
    ("CONTENT_BRIEF", "a3264c95-9b30-4ac8-833a-dc96ea8b7ee1", "diyu_m4_content_brief"),
    ("CREATIVE_SCRIPT", "8d518554-bfbc-4be0-8a57-3b1f04983edf", "diyu_m4_creative_script"),
    ("PRODUCTION_DIRECTOR", "57ebc138-ed9e-4202-bce2-38e44da0ec1d", "diyu_m4_production_director"),
    ("PUBLISHING_PACKAGING", "10056fcf-9237-4889-a3e3-81e3a695cae0", "diyu_m4_publishing_packaging"),
]
SEAM_SOURCE = "de0cb1e9-2af8-415a-9762-31b6cf348c22"

NEW_FIND_SCALAR = '''def _unescape(s):
    """只还原 JSON 串值里的转义。不做别的解释。"""
    out, i = [], 0
    while i < len(s):
        c = s[i]
        if c == "\\\\" and i + 1 < len(s):
            nx = s[i + 1]
            out.append({"n": "\\n", "t": "\\t", "r": "\\r", '"': '"', "'": "'",
                        "\\\\": "\\\\"}.get(nx, nx))
            i += 2
        else:
            out.append(c)
            i += 1
    return "".join(out)


def _unwrap(v):
    """剥掉**成对的**外层包裹引号。值内部的引号是内容，不是边界。"""
    v = (v or "").strip()
    if v.endswith(","):
        v = v[:-1].rstrip()
    for q in ('"', "'", "`"):
        if len(v) >= 2 and v[0] == q and v[-1] == q:
            return v[1:-1].strip()
    return v


def _find_scalar(text, key):
    """从外壳文本里取一个标量语义值。容忍 YAML / JSON / Markdown 三种写法，
    因为统一外壳**不强制物理字段名**（统一能力合同 1.1）。

    判在场的必须是业务语义，不是引号。旧版把引号当成值的边界，值里出现
    ASCII 引号时有两种坏法：整条不匹配，把在场的判成缺失；或者只取到第一个
    引号之前的半截还判成功——后者更坏，是静默损坏。旧版的 key 定位还会跨行，
    于是一个空字段能把下一行当成自己的值，必填闸门被静默绕过。

    现在分两步：先定位键（**不跨行**），再把值的整个剩余部分收下，
    只在首尾成对时剥掉一层包裹引号。
    """
    if not text:
        return ""
    esc = re.escape(key)
    m = re.search(r'"%s"\\s*[:：]\\s*"((?:[^"\\\\]|\\\\.)*)"' % esc, text)
    if m:
        return _norm(_unescape(m.group(1)))
    m = re.search(r'^[ \\t]*["\\'`]?%s["\\'`]?[ \\t]*[:：][ \\t]*(.+)$' % esc, text, re.MULTILINE)
    if m:
        return _norm(_unwrap(m.group(1)))
    m = re.search(r'`%s`\\s*[:：]\\s*([^\\n]+)' % esc, text)
    if m:
        return _norm(_unwrap(m.group(1)))
    return ""
'''


def psql(q, db="dify"):
    p = subprocess.run(["docker", "exec", "-i", "docker-db_postgres-1", "psql", "-U", "postgres",
                        "-d", db, "-t", "-A", "-c", q], capture_output=True, text=True, timeout=300)
    if p.returncode != 0:
        raise RuntimeError(p.stderr[:400])
    return p.stdout


def published_graph(app_id):
    g = psql("SELECT graph FROM workflows WHERE app_id='%s' AND version<>'draft' "
             "ORDER BY created_at DESC LIMIT 1;" % app_id).strip()
    if not g:
        raise RuntimeError("没有已发布 graph：%s" % app_id)
    return json.loads(g)


def provider_row(pid):
    out = psql("SELECT row_to_json(t) FROM (SELECT id,name,label,icon,description,"
               "parameter_configuration,privacy_policy FROM tool_workflow_providers "
               "WHERE id='%s') t;" % pid).strip()
    return json.loads(out)


def patch_envelope(graph):
    """把 envelope_check 的 _find_scalar 换掉。其他节点一律不动。"""
    hits = []
    for n in graph.get("nodes", []):
        d = n.get("data") or {}
        if d.get("type") != "code" or "def _find_scalar(" not in (d.get("code") or ""):
            continue
        code = d["code"]
        s = code.index("def _find_scalar(")
        e = code.index("def _present(")
        d["code"] = code[:s] + NEW_FIND_SCALAR.strip() + "\n\n\n" + code[e:]
        hits.append(n["id"])
    if len(hits) != 1:
        raise RuntimeError("期望恰好一个 envelope_check 节点，实得 %s" % hits)
    return graph, hits[0]


def upsert_app(c, name, desc, icon="🧩"):
    st, apps = c.call("GET", "/console/api/apps?page=1&limit=100")
    assert st == 200, (st, apps)
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
                     body={"marked_name": MARKED_NAME, "marked_comment": MARKED_COMMENT},
                     timeout=600)
    assert st in (200, 201), ("publish failed", st, json.dumps(pub, ensure_ascii=False)[:400])


def draft_features(app_id):
    r = psql("SELECT features FROM workflows WHERE app_id='%s' AND version<>'draft' "
             "ORDER BY created_at DESC LIMIT 1;" % app_id).strip()
    return json.loads(r) if r else {}


def main():
    c = DC.Console(env=DC.load_env(ENV))
    out = {"successors": {}, "providers": {}}

    for cap, src_app, prov_name in SOURCE:
        g = published_graph(src_app)
        before = hashlib.md5(json.dumps(g, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
        g, node = patch_envelope(g)
        st, meta = c.call("GET", "/console/api/apps/%s" % src_app)
        assert st == 200
        name = "DIYU M5 RB · %s" % meta["name"]
        app_id, created = upsert_app(c, name, "M5 AC-07 Rebase successor：只换 envelope_check "
                                              "的 _find_scalar，其余节点照搬 %s 的已发布 graph。" % meta["name"])
        sync_and_publish(c, app_id, g, draft_features(src_app))
        after = psql("SELECT md5(graph) FROM workflows WHERE app_id='%s' AND version<>'draft' "
                     "ORDER BY created_at DESC LIMIT 1;" % app_id).strip()
        out["successors"][cap] = {"source_app": src_app, "successor_app": app_id,
                                  "created": created, "patched_node": node,
                                  "graph_md5": after, "source_graph_md5_before_patch": before}
        print("%-22s successor=%s md5=%s" % (cap, app_id, after), flush=True)

        # 工具 provider：字段照抄原 provider，只换 name / label / app
        src_pid = {p[2]: p for p in SOURCE}  # noqa
        pr = psql("SELECT id FROM tool_workflow_providers WHERE name='%s';" % prov_name).strip()
        row = provider_row(pr)
        new_name = prov_name.replace("diyu_m4_", "diyu_m5rb_")
        exist = psql("SELECT id FROM tool_workflow_providers WHERE name='%s';" % new_name).strip()
        if not exist:
            st, r = c.call("POST", "/console/api/workspaces/current/tool-provider/workflow/create",
                           body={"workflow_app_id": app_id, "name": new_name,
                                 "label": "DIYU M5 RB · " + row["label"],
                                 "icon": json.loads(row["icon"]) if isinstance(row["icon"], str) else row["icon"],
                                 "description": row["description"],
                                 "parameters": json.loads(row["parameter_configuration"]),
                                 "privacy_policy": row.get("privacy_policy") or "", "labels": []})
            assert st in (200, 201), ("provider create failed", st, str(r)[:400])
            exist = psql("SELECT id FROM tool_workflow_providers WHERE name='%s';" % new_name).strip()
        out["providers"][cap] = {"source_provider": pr, "successor_provider": exist,
                                 "tool_name": new_name}
        print("%-22s provider=%s (%s)" % (cap, exist, new_name), flush=True)

    # ---- 接缝 successor：tool 节点改指新 provider ----
    sg = published_graph(SEAM_SOURCE)
    remap = {out["providers"][cap]["source_provider"]: out["providers"][cap]
             for cap in out["providers"]}
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
    seam_id, created = upsert_app(c, "DIYU M5 RB · %s" % meta["name"],
                                  "M5 AC-07 Rebase successor 接缝：只把 6 个 tool 节点改指"
                                  "修复后的能力 successor，路由与其余节点原样。", icon="🔗")
    sync_and_publish(c, seam_id, sg, draft_features(SEAM_SOURCE))
    seam_md5 = psql("SELECT md5(graph) FROM workflows WHERE app_id='%s' AND version<>'draft' "
                    "ORDER BY created_at DESC LIMIT 1;" % seam_id).strip()
    out["seam"] = {"source_app": SEAM_SOURCE, "successor_app": seam_id, "created": created,
                   "graph_md5": seam_md5, "tool_nodes_remapped": changed}
    print("SEAM successor=%s md5=%s" % (seam_id, seam_md5))

    # ---- 保护面复算：源应用必须一个字节都没动 ----
    untouched = {}
    for cap, src_app, _ in SOURCE + [("SEAM", SEAM_SOURCE, "")]:
        untouched[cap] = psql("SELECT md5(graph) FROM workflows WHERE app_id='%s' "
                              "AND version<>'draft' ORDER BY created_at DESC LIMIT 1;"
                              % src_app).strip()
    out["source_apps_graph_md5_after"] = untouched

    p = os.path.join(ROOT, "decision-chain", "evidence", "m5-rb", "M4_PARSER_SUCCESSOR_BUILD.json")
    with open(p, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print("SAVED", p)
    return 0


if __name__ == "__main__":
    sys.exit(main())
