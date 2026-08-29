#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Node S2｜确定性检查。零模型调用。含 S1 层的必要回归。"""
import hashlib
import io
import json
import os
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
APP = os.environ.get("S2_APP_ID", "85c01f85-a081-43e9-ab09-9993289cc200")
M1_SOURCE_APP = "dd638b91-d39f-4e92-a984-6ad1ab809119"
LEGACY = "2448e4f9-818f-4b88-9311-d18546e97da9"
M2_BASE = "http://diyu-m2-app:8000"
BASELINE = os.path.join(HERE, "..", "evidence", "UAPP_R0_PROTECTED_BASELINE.json")


def psql(sql, db="dify"):
    p = subprocess.run(["docker", "exec", "-i", "docker-db_postgres-1", "psql", "-U", "postgres",
                        "-d", db, "-tA", "-c", sql], capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError("psql: " + (p.stderr or "")[:300])
    return p.stdout.strip()


def graph_of(app_id):
    raw = psql("select w.graph from workflows w join apps a on a.workflow_id=w.id "
               "where a.id='%s';" % app_id)
    return json.loads(raw) if raw else None


R = []


def check(cid, desc, ok, detail):
    R.append({"id": cid, "desc": desc, "result": "PASS" if ok else "FAIL", "detail": detail})


g = graph_of(APP)
nodes = {n["id"]: n for n in g["nodes"]}
edges = g["edges"]

# ---------- 身份与发布 ----------
row = psql("select a.mode||'|'||a.name from apps a where a.id='%s';" % APP)
mode = row.split("|", 1)[0]
pub = psql("select w.id||'|'||coalesce(w.marked_name,'') from workflows w where w.app_id='%s' "
           "and w.version <> 'draft' order by w.created_at desc limit 1;" % APP)
check("D-S2-01", "仍是同一个 successor 应用、advanced-chat，且已发布新版本",
      mode == "advanced-chat" and APP != LEGACY and bool(pub),
      {"app_id": APP, "mode": mode, "latest_published": pub})

# ---------- 本层新增节点齐备 ----------
NEW = ["uapp_boot_gate", "boot_user", "boot_p1", "boot_ws", "boot_p2", "boot_acct", "boot_p3",
       "boot_cycle", "boot_p4", "boot_task", "boot_p5", "boot_assign",
       "uapp_m2_cycle", "uapp_m2_dec", "uapp_m2_run", "uapp_ctx", "uapp_s2_pending"]
check("D-S2-02", "本层新增的 M2 建域链与只读投影节点齐备",
      all(k in nodes for k in NEW), {"missing": [k for k in NEW if k not in nodes],
                                     "node_count": len(nodes), "edge_count": len(edges)})

# ---------- S1 回归：M1 六节点仍逐字节一致 ----------
m1n = {n["id"]: n for n in graph_of(M1_SOURCE_APP)["nodes"]}
VERBATIM = ("m1_extract", "m1_join", "m1_shadow", "m1_compiler", "m1_save_snapshot", "m1_chat_llm")
diffs = {nid: True for nid in VERBATIM
         if json.dumps(m1n[nid]["data"], ensure_ascii=False, sort_keys=True)
         != json.dumps(nodes[nid]["data"], ensure_ascii=False, sort_keys=True)}
check("D-S2-03", "回归·M1 六个复用节点仍与 M1 源应用逐字节一致", not diffs,
      {"compared": list(VERBATIM), "diffs": list(diffs)})

# ---------- S1 回归：start 零输入变量 ----------
check("D-S2-04", "回归·start 节点仍零用户输入变量",
      (nodes["uapp_start"]["data"].get("variables") or []) == [],
      {"variables": nodes["uapp_start"]["data"].get("variables")})

# ---------- 分层门禁：本层不得出现 M3/Hop/Seam/能力 ----------
tools = {nid: n["data"].get("tool_name") for nid, n in nodes.items()
         if n["data"].get("type") == "tool"}
check("D-S2-05", "S2 层仍不含任何 M3/Hop/Seam/能力调用节点", not tools, {"tool_nodes": tools})

# ---------- 网络面：所有 http 只打 M2，不连外部 ----------
urls = {nid: n["data"].get("url") for nid, n in nodes.items()
        if n["data"].get("type") == "http-request"}
bad = {k: v for k, v in urls.items() if not (v or "").startswith(M2_BASE)}
check("D-S2-06", "全部 http 节点只指向 M2 容器地址，无外部网络", not bad,
      {"http_nodes": len(urls), "offenders": bad})

# ---------- 闲聊与只问一个不进 M2 ----------
out_edges = {}
for e in edges:
    out_edges.setdefault(e["source"], []).append((e.get("sourceHandle"), e["target"]))


def reaches(start, targets, seen=None):
    seen = seen or set()
    if start in seen:
        return False
    seen.add(start)
    for _h, t in out_edges.get(start, []):
        if t in targets or reaches(t, targets, seen):
            return True
    return False


M2_NODES = {"boot_user", "boot_ws", "boot_acct", "boot_cycle", "boot_task",
            "uapp_m2_cycle", "uapp_m2_dec", "uapp_m2_run"}
br = {h: t for h, t in out_edges.get("uapp_s2_branch", [])}
check("D-S2-07", "只问一个与闲聊两条出口都不经过任何 M2 节点（省链且不产生副作用）",
      not reaches(br.get("case_ask", ""), M2_NODES) and not reaches(br.get("false", ""), M2_NODES),
      {"branch": br,
       "ask_reaches_m2": reaches(br.get("case_ask", ""), M2_NODES),
       "chat_reaches_m2": reaches(br.get("false", ""), M2_NODES)})

# ---------- 建域只在首轮：boot 分支由 needs_bootstrap 把门 ----------
bg = nodes["uapp_boot_gate"]["data"]
cond = (bg.get("cases") or [{}])[0].get("conditions", [{}])[0]
check("D-S2-08", "建域链由 needs_bootstrap 把门；已建域的轮次直连 M2 只读，天然幂等",
      cond.get("variable_selector") == ["uapp_route", "needs_bootstrap"]
      and cond.get("value") == "true"
      and ("false", "uapp_m2_cycle") in out_edges.get("uapp_boot_gate", []),
      {"gate_condition": cond, "boot_gate_out": out_edges.get("uapp_boot_gate")})

# ---------- M2 读取节点为只读 GET ----------
ro = {nid: nodes[nid]["data"].get("method") for nid in ("uapp_m2_cycle", "uapp_m2_dec", "uapp_m2_run")}
check("D-S2-09", "三个 M2 投影节点全部是 GET，只读不写",
      all(v == "get" for v in ro.values()), {"methods": ro})

# ---------- 本层不引入 M3 语义 ----------
ctx_code = nodes["uapp_ctx"]["data"].get("code") or ""
check("D-S2-10", "本层投影节点的参考资料信封显式为空，未装载任何 M3 方法参考",
      "_REFS = []" in ctx_code and "_REF_MANIFEST_LINES = []" in ctx_code,
      {"refs_empty": "_REFS = []" in ctx_code,
       "manifest_empty": "_REF_MANIFEST_LINES = []" in ctx_code})

# ---------- 受保护面零漂移 ----------
base = json.load(io.open(BASELINE, encoding="utf-8"))
drift = []
for row_ in base["protected_dify_apps"]:
    got = psql("select md5(w.graph) from workflows w join apps a on a.workflow_id=w.id "
               "where a.id='%s';" % row_["app_id"]).strip()
    if got != row_["graph_md5"]:
        drift.append({"key": row_["key"], "baseline": row_["graph_md5"], "now": got})
check("D-S2-11", "11 个受保护应用 graph 相对 R0 基线零漂移", not drift,
      {"checked": len(base["protected_dify_apps"]), "drift": drift})

legacy_now = psql("select md5(w.graph) from workflows w join apps a on a.workflow_id=w.id "
                  "where a.id='%s';" % LEGACY).strip()
check("D-S2-12", "旧候选 app 2448e4f9 零改动",
      legacy_now == base["legacy_diagnostic_candidate"]["draft_graph_md5"],
      {"baseline": base["legacy_diagnostic_candidate"]["draft_graph_md5"], "now": legacy_now})

out = {"stage": "S2", "app_id": APP,
       "graph_sha256": hashlib.sha256(json.dumps(g, ensure_ascii=False, sort_keys=True)
                                      .encode("utf-8")).hexdigest(),
       "node_count": len(g["nodes"]), "edge_count": len(g["edges"]), "model_calls": 0,
       "checks": R,
       "summary": {"pass": sum(1 for r in R if r["result"] == "PASS"),
                   "fail": sum(1 for r in R if r["result"] == "FAIL"), "total": len(R)}}
print(json.dumps(out["summary"], ensure_ascii=False))
for r in R:
    print("  [%s] %s | %s" % (r["result"], r["id"], r["desc"]))
    if r["result"] == "FAIL":
        print("        detail:", json.dumps(r["detail"], ensure_ascii=False)[:400])
p = os.path.join(HERE, "..", "evidence",
                 os.environ.get("S2_CHECK_OUT", "S2_DETERMINISTIC_CHECKS.json"))
with io.open(p, "w", encoding="utf-8") as fh:
    fh.write(json.dumps(out, ensure_ascii=False, indent=2) + "\n")
