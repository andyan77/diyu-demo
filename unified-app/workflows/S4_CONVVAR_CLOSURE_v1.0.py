#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""会话变量读写闭包检查｜零模型调用，只读线上图。

每一个被读取的 conversation 变量必须存在可达写入；
写入来源必须来自本轮真实节点输出（Seam 产物 / 路由结果），不接受常量与模型自述。
"""
import importlib.util, io, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
ENV = "/home/faye/diyu-demo-worktrees/m3-account-content-operator-v1/.env"
APP = "85c01f85-a081-43e9-ab09-9993289cc200"


def _load(n, p):
    s = importlib.util.spec_from_file_location(n, p); m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m); return m


import subprocess


def psql(sql, db="dify"):
    p = subprocess.run(["docker", "exec", "-i", "docker-db_postgres-1", "psql", "-U", "postgres",
                        "-d", db, "-tA", "-c", sql], capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError("psql: " + (p.stderr or "")[:300])
    return p.stdout.strip()


# 只认已发布图（workflows.graph），不认草稿、不认模型自述。
g = json.loads(psql("select w.graph from workflows w join apps a on a.workflow_id=w.id "
                    "where a.id='%s';" % APP))
nodes = g["nodes"]; edges = g["edges"]
blob = json.dumps(g, ensure_ascii=False)

# 会话变量声明在 workflows 表的列上，不在 graph 里——早先版本在 graph 内找，
# 因此 declared 恒为空、这条检查没有判别力。改读真源列。
_cv = psql("select coalesce(w.conversation_variables::text,'[]') from workflows w "
           "join apps a on a.workflow_id=w.id where a.id='%s';" % APP)
_cvj = json.loads(_cv or "{}") or {}
# Dify 1.16 用「名字 → 定义」的对象存；早期版本用列表。两种都认。
declared = (set(_cvj.keys()) if isinstance(_cvj, dict)
            else {c.get("name") for c in _cvj if isinstance(c, dict)})

# 读：模板引用 {{#conversation.X#}} 与 value_selector ["conversation","X"]
reads = set(re.findall(r"\{\{#conversation\.([A-Za-z0-9_]+)#\}\}", blob))
for m in re.finditer(r'\["conversation",\s*"([A-Za-z0-9_]+)"\]', blob):
    pass
for n in nodes:
    d = n.get("data") or {}
    for k in ("variables", "vars"):
        for v in (d.get(k) or []):
            # code 节点用 [name, selector] 的二元组，其它节点用 dict
            sel = v.get("value_selector") if isinstance(v, dict) else (
                v[1] if len(v) > 1 and isinstance(v[1], list) else [])
            sel = sel or []
            if len(sel) >= 2 and sel[0] == "conversation":
                reads.add(sel[1])

# 写：assigner 节点的 items
writes = {}
for n in nodes:
    d = n.get("data") or {}
    if d.get("type") != "assigner":
        continue
    for it in (d.get("items") or []):
        sel = it.get("variable_selector") or []
        if len(sel) == 2 and sel[0] == "conversation":
            writes.setdefault(sel[1], []).append(
                {"node": n["id"], "input_type": it.get("input_type"), "value": it.get("value")})

ids = {n["id"] for n in nodes}
adj = {}
for e in edges:
    adj.setdefault(e["source"], set()).add(e["target"])


def reachable(src):
    seen, st = set(), [src]
    while st:
        x = st.pop()
        for y in adj.get(x, ()):
            if y not in seen:
                seen.add(y); st.append(y)
    return seen


start = [n["id"] for n in nodes if (n.get("data") or {}).get("type") == "start"]
live = set(start)
for s in start:
    live |= reachable(s)

checks = []
for v in sorted(reads):
    w = writes.get(v) or []
    reach = [x for x in w if x["node"] in live]
    ok = bool(reach)
    checks.append(("每个被读取的会话变量存在可达写入：%s" % v, ok,
                   {"writers": [x["node"] for x in w], "reachable_writers": [x["node"] for x in reach]}))
for v, w in sorted(writes.items()):
    for x in w:
        src_ok = x["input_type"] == "variable" and isinstance(x["value"], list) and x["value"][0] in ids
        checks.append(("写入来源为本轮真实节点输出（非常量）：%s ← %s" % (v, x["value"]), src_ok,
                       {"node": x["node"], "input_type": x["input_type"], "value": x["value"]}))
undeclared = sorted((reads | set(writes)) - declared)
checks.append(("读写涉及的会话变量均已声明，未新增状态变量", not undeclared, {"undeclared": undeclared}))

npass = sum(1 for c in checks if c[1])
print(json.dumps({"pass": npass, "fail": len(checks) - npass, "total": len(checks),
                  "node_count": len(nodes), "edge_count": len(edges),
                  "declared_conversation_variables": sorted(declared)},
                 ensure_ascii=False, indent=2))
for desc, ok, obs in checks:
    print("  [%s] %s | %s" % ("PASS" if ok else "FAIL", desc, json.dumps(obs, ensure_ascii=False)))
sys.exit(0 if npass == len(checks) else 1)
