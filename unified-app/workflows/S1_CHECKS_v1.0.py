#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Node S1｜确定性检查。零模型调用，全部可复算。

先跑这个，再跑正例负例（Rebase Prompt §4.2：先冻结 → 先跑确定性检查 → 正例 → 负例 → 回归）。
"""
import hashlib
import io
import json
import os
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
APP = os.environ.get("S1_APP_ID", "85c01f85-a081-43e9-ab09-9993289cc200")
M1_SOURCE_APP = "dd638b91-d39f-4e92-a984-6ad1ab809119"
LEGACY = "2448e4f9-818f-4b88-9311-d18546e97da9"
BASELINE = os.path.join(HERE, "..", "evidence", "UAPP_R0_PROTECTED_BASELINE.json")


def psql(sql, db="dify"):
    p = subprocess.run(["docker", "exec", "-i", "docker-db_postgres-1", "psql", "-U", "postgres",
                        "-d", db, "-tA", "-c", sql], capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError("psql: " + (p.stderr or "")[:300])
    return p.stdout.strip()


def graph_of(app_id, published=False):
    if published:
        raw = psql("select w.graph from workflows w where w.app_id='%s' "
                   "and w.version <> 'draft' order by w.created_at desc limit 1;" % app_id)
    else:
        raw = psql("select w.graph from workflows w join apps a on a.workflow_id=w.id "
                   "where a.id='%s';" % app_id)
    return json.loads(raw) if raw else None


R = []


def check(cid, desc, ok, detail):
    R.append({"id": cid, "desc": desc, "result": "PASS" if ok else "FAIL", "detail": detail})


# ---------- D-S1-01 应用身份与发布 ----------
row = psql("select a.mode||'|'||a.name from apps a where a.id='%s';" % APP)
mode, name = (row.split("|", 1) + ["", ""])[:2]
check("D-S1-01", "successor 是 advanced-chat 且独立于旧候选",
      mode == "advanced-chat" and APP != LEGACY, {"mode": mode, "name": name, "app_id": APP})

pub = psql("select w.id||'|'||w.version||'|'||coalesce(w.marked_name,'') from workflows w "
           "where w.app_id='%s' and w.version <> 'draft' order by w.created_at desc limit 1;" % APP)
check("D-S1-02", "successor 已发布出一个非 draft 版本", bool(pub), {"published": pub})

site = psql("select count(*) from sites where app_id='%s';" % APP)
check("D-S1-03", "successor 存在 Site 入口（用户可直接打开）", site.strip() not in ("", "0"),
      {"site_rows": site})

# ---------- D-S1-04 起点零用户输入变量 ----------
g = graph_of(APP)
nodes = {n["id"]: n for n in g["nodes"]}
start_vars = nodes["uapp_start"]["data"].get("variables") or []
check("D-S1-04", "start 节点零用户输入变量：用户只说自然语言", start_vars == [],
      {"variables": start_vars})

# ---------- D-S1-05 M1 子图逐字节一致 ----------
m1g = graph_of(M1_SOURCE_APP)
m1n = {n["id"]: n for n in m1g["nodes"]}
VERBATIM = ("m1_extract", "m1_join", "m1_shadow", "m1_compiler", "m1_save_snapshot", "m1_chat_llm")
diffs = {}
for nid in VERBATIM:
    a = json.dumps(m1n[nid]["data"], ensure_ascii=False, sort_keys=True)
    b = json.dumps(nodes[nid]["data"], ensure_ascii=False, sort_keys=True)
    if a != b:
        diffs[nid] = {"m1_sha": hashlib.sha256(a.encode()).hexdigest()[:16],
                      "s1_sha": hashlib.sha256(b.encode()).hexdigest()[:16]}
check("D-S1-05", "M1 六个复用节点与 M1 源应用逐字节一致（节点 id 亦保留）", not diffs,
      {"compared": list(VERBATIM), "diffs": diffs})

# ---------- D-S1-06 本层不得出现下游模块 ----------
forbidden = []
for nid, n in nodes.items():
    d = n["data"]
    if d.get("type") == "tool":
        forbidden.append({nid: d.get("tool_name")})
    if d.get("type") == "http-request":
        forbidden.append({nid: d.get("url")})
check("D-S1-06", "S1 层不含任何 M2/M3/Seam/能力调用节点（分层门禁）", not forbidden,
      {"found": forbidden, "node_count": len(nodes)})

# ---------- D-S1-07 三条出口齐备且各自独立 ----------
edges = g["edges"]
by_handle = {}
for e in edges:
    if e["source"] == "uapp_s1_branch":
        by_handle[e.get("sourceHandle")] = e["target"]
check("D-S1-07", "分流三出口：只问一个 / 路线已定未接 / 闲聊，各自到达独立回复节点",
      by_handle.get("case_ask") == "uapp_ask_one"
      and by_handle.get("case_routed") == "uapp_s1_pending"
      and by_handle.get("false") == "m1_chat_llm",
      {"branch_targets": by_handle})

# ---------- D-S1-08 受保护面零漂移 ----------
base = json.load(io.open(BASELINE, encoding="utf-8"))
drift = []
for row_ in base["protected_dify_apps"]:
    got = psql("select md5(w.graph) from workflows w join apps a on a.workflow_id=w.id "
               "where a.id='%s';" % row_["app_id"]).strip()
    if got != row_["graph_md5"]:
        drift.append({"key": row_["key"], "app_id": row_["app_id"],
                      "baseline": row_["graph_md5"], "now": got})
check("D-S1-08", "11 个受保护应用 graph 相对 R0 基线零漂移", not drift,
      {"checked": len(base["protected_dify_apps"]), "drift": drift})

# ---------- D-S1-09 旧候选未被继续施工 ----------
legacy_now = psql("select md5(w.graph) from workflows w join apps a on a.workflow_id=w.id "
                  "where a.id='%s';" % LEGACY).strip()
check("D-S1-09", "旧候选 app 2448e4f9 自 R0 起零改动（只作诊断参考）",
      legacy_now == base["legacy_diagnostic_candidate"]["draft_graph_md5"],
      {"baseline": base["legacy_diagnostic_candidate"]["draft_graph_md5"], "now": legacy_now})

# ---------- D-S1-10 歧义补充规则确实进了图，且未改动原提示词 ----------
sys_prompt = ""
for p in nodes["uapp_action"]["data"].get("prompt_template") or []:
    if p.get("role") == "system":
        sys_prompt = p.get("text") or ""
NODES_SRC = io.open(os.path.join(HERE, "UAPP_CANVAS_NODES_v1.0.py"), encoding="utf-8").read()
orig_start = NODES_SRC.index('ACTION_SYSTEM_PROMPT = """') + len('ACTION_SYSTEM_PROMPT = """')
orig = NODES_SRC[orig_start:NODES_SRC.index('"""', orig_start)]
check("D-S1-10", "原 ACTION 提示词一字未改，补充规则以追加方式生效",
      sys_prompt.startswith(orig) and "修改类请求缺少" in sys_prompt,
      {"original_preserved": sys_prompt.startswith(orig),
       "supplement_present": "修改类请求缺少" in sys_prompt,
       "orig_len": len(orig), "now_len": len(sys_prompt)})

out = {
    "stage": "S1", "app_id": APP,
    "graph_sha256": hashlib.sha256(json.dumps(g, ensure_ascii=False, sort_keys=True)
                                   .encode("utf-8")).hexdigest(),
    "node_count": len(g["nodes"]), "edge_count": len(g["edges"]),
    "model_calls": 0,
    "checks": R,
    "summary": {"pass": sum(1 for r in R if r["result"] == "PASS"),
                "fail": sum(1 for r in R if r["result"] == "FAIL"), "total": len(R)},
}
print(json.dumps(out, ensure_ascii=False, indent=2))
p = os.path.join(HERE, "..", "evidence", os.environ.get("S1_CHECK_OUT", "S1_DETERMINISTIC_CHECKS.json"))
with io.open(p, "w", encoding="utf-8") as fh:
    fh.write(json.dumps(out, ensure_ascii=False, indent=2) + "\n")
