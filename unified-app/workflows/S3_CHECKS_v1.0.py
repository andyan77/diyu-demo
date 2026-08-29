#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Node S3｜确定性检查。零模型调用。含 S1/S2 层的必要回归。"""
import hashlib
import io
import json
import os
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
APP = os.environ.get("S3_APP_ID", "85c01f85-a081-43e9-ab09-9993289cc200")
M1_SRC = "dd638b91-d39f-4e92-a984-6ad1ab809119"
M3_APP = "a4c3b19b-243f-490b-9aca-3aa19767d6a5"
PROVIDER_M3 = "9ea86217-8791-489c-9a96-b880ae558ac5"
LEGACY = "2448e4f9-818f-4b88-9311-d18546e97da9"
M2_BASE = "http://diyu-m2-app:8000"
BASELINE = os.path.join(HERE, "..", "evidence", "UAPP_R0_PROTECTED_BASELINE.json")
REFDIR = os.path.join(ROOT, "m3-account-content-operator-semantic-v1.0",
                      "skill-source", "references")


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


def check(cid, desc, okv, detail):
    R.append({"id": cid, "desc": desc, "result": "PASS" if okv else "FAIL", "detail": detail})


g = graph_of(APP)
nodes = {n["id"]: n for n in g["nodes"]}
edges = g["edges"]
ctx_code = nodes["uapp_ctx"]["data"].get("code") or ""

# ---------- 身份 ----------
pub = psql("select w.id||'|'||coalesce(w.marked_name,'') from workflows w where w.app_id='%s' "
           "and w.version <> 'draft' order by w.created_at desc limit 1;" % APP)
check("D-S3-01", "仍是同一个 successor 应用且已发布新版本", bool(pub) and APP != LEGACY,
      {"app_id": APP, "latest_published": pub})

# ---------- M3 绑定现场复算 ----------
tgt = psql("select p.app_id from tool_workflow_providers p where p.id='%s';" % PROVIDER_M3).strip()
m3_nodes = [nid for nid, n in nodes.items() if n["data"].get("type") == "tool"]
m3n = nodes.get("uapp_m3", {}).get("data", {})
check("D-S3-02", "M3 provider 目标现场复算 = 合同 final_fp_bindings.M3",
      tgt == M3_APP, {"provider": PROVIDER_M3, "target_now": tgt, "contract": M3_APP})
check("D-S3-03", "图内唯一的 tool 节点是 M3，且指向该 provider（本层未接 Hop/Seam）",
      m3_nodes == ["uapp_m3"] and m3n.get("provider_id") == PROVIDER_M3
      and m3n.get("tool_name") == "diyu_uapp_m3",
      {"tool_nodes": m3_nodes, "provider_id": m3n.get("provider_id"),
       "tool_name": m3n.get("tool_name")})

# ---------- M3 应用零漂移（只调用不修改）----------
base = json.load(io.open(BASELINE, encoding="utf-8"))
m3base = [x for x in base["protected_dify_apps"] if x["app_id"] == M3_APP][0]["graph_md5"]
m3now = psql("select md5(w.graph) from workflows w join apps a on a.workflow_id=w.id "
             "where a.id='%s';" % M3_APP).strip()
check("D-S3-04", "最终 FP M3 的 graph 零改动（只调用不修改）", m3now == m3base,
      {"baseline": m3base, "now": m3now})

# ---------- M3 方法参考：载体两份一致 + 验收夹具未加载 ----------
# 正文是经 json.dumps 转义后嵌进代码的，原文子串匹配必然匹配不上（第一版检查器就栽在这里）。
# 正确做法：把图内的 _REFS 解析回来，按 sha256 与仓库逐份比对。
# 这同时让「夹具未加载」这一条真正具备判别力——夹具若被嵌进去，它的 sha256 会出现在这里。
def _embedded_refs(src):
    i = src.index("_REFS = ")
    j = src.index("\n_REF_MANIFEST_LINES", i)
    return {path: body for path, body in json.loads(src[i + len("_REFS = "):j].strip())}


embedded = _embedded_refs(ctx_code)
digs, bad, fixture_leak = [], [], []
for fname, should_load in (("fashion-and-market.md", True), ("six-skill-methods.md", True),
                           ("operations.md", True), ("acceptance-fixtures.md", False)):
    raw = io.open(os.path.join(REFDIR, fname), "rb").read()
    repo_sha = hashlib.sha256(raw).hexdigest()
    key = "references/" + fname
    got = embedded.get(key)
    got_sha = hashlib.sha256(got.encode("utf-8")).hexdigest() if got is not None else None
    digs.append({"file": fname, "repo_sha256": repo_sha, "in_graph_sha256": got_sha,
                 "declared": "LOADED" if should_load else "NOT_LOADED",
                 "identical": got_sha == repo_sha})
    if should_load and got_sha != repo_sha:
        bad.append({"file": fname, "repo": repo_sha, "graph": got_sha})
    if (not should_load) and got is not None:
        fixture_leak.append(fname)
    # 夹具正文也可能被塞进别的地方，不只 _REFS。整段图文本再查一次它的独有片段。
    if not should_load:
        marker = raw.decode("utf-8").strip().splitlines()[0][:60]
        if marker and json.dumps(marker, ensure_ascii=False)[1:-1] in json.dumps(
                g, ensure_ascii=False):
            fixture_leak.append(fname + "(found_elsewhere_in_graph)")

check("D-S3-05", "三份方法参考按 sha256 与仓库逐份一致（图内载体解码后比对，非子串匹配）",
      not bad and len([d for d in digs if d["declared"] == "LOADED" and d["identical"]]) == 3,
      {"mismatched": bad, "digests": digs})
check("D-S3-06", "M3 验收夹具（含期望答案）未进入图任何位置，且清单声明 NOT_LOADED",
      not fixture_leak and "acceptance-fixtures.md: NOT_LOADED" in ctx_code,
      {"leaked": fixture_leak,
       "manifest_declares_not_loaded": "acceptance-fixtures.md: NOT_LOADED" in ctx_code})

# ---------- 组件失败局部 Return ----------
fb = [(e.get("sourceHandle"), e["target"]) for e in edges if e["source"] == "uapp_m3"]
check("D-S3-07", "M3 调用失败走局部 Return，不让整轮失败",
      m3n.get("error_strategy") == "fail-branch"
      and ("fail-branch", "uapp_m3_fail") in fb,
      {"error_strategy": m3n.get("error_strategy"), "m3_out_edges": fb})

# ---------- 回归 S1：M1 六节点逐字节 + start 零变量 ----------
m1n = {n["id"]: n for n in graph_of(M1_SRC)["nodes"]}
VERB = ("m1_extract", "m1_join", "m1_shadow", "m1_compiler", "m1_save_snapshot", "m1_chat_llm")
diffs = [nid for nid in VERB
         if json.dumps(m1n[nid]["data"], ensure_ascii=False, sort_keys=True)
         != json.dumps(nodes[nid]["data"], ensure_ascii=False, sort_keys=True)]
check("D-S3-08", "回归·M1 六节点仍逐字节一致，且 start 零用户输入变量",
      not diffs and (nodes["uapp_start"]["data"].get("variables") or []) == [],
      {"diffs": diffs, "start_vars": nodes["uapp_start"]["data"].get("variables")})

# ---------- 回归 S2：http 仍只打 M2 ----------
urls = {nid: n["data"].get("url") for nid, n in nodes.items()
        if n["data"].get("type") == "http-request"}
badu = {k: v for k, v in urls.items() if not (v or "").startswith(M2_BASE)}
check("D-S3-09", "回归·全部 http 节点仍只指向 M2，无外部网络", not badu,
      {"http_nodes": len(urls), "offenders": badu})

# ---------- 只问一个 / 闲聊两支仍不触碰 M2 与 M3 ----------
oe = {}
for e in edges:
    oe.setdefault(e["source"], []).append((e.get("sourceHandle"), e["target"]))


def reaches(start, targets, seen=None):
    seen = seen or set()
    if start in seen:
        return False
    seen.add(start)
    for _h, t in oe.get(start, []):
        if t in targets or reaches(t, targets, seen):
            return True
    return False


HEAVY = {"boot_user", "boot_ws", "boot_acct", "boot_cycle", "boot_task",
         "uapp_m2_cycle", "uapp_m2_dec", "uapp_m2_run", "uapp_m3"}
br = {h: t for h, t in oe.get("uapp_s2_branch", [])}
check("D-S3-10", "只问一个与闲聊两条出口仍不触碰任何 M2 或 M3 节点",
      not reaches(br.get("case_ask", ""), HEAVY) and not reaches(br.get("false", ""), HEAVY),
      {"branch": br, "ask_hits": reaches(br.get("case_ask", ""), HEAVY),
       "chat_hits": reaches(br.get("false", ""), HEAVY)})

# ---------- 泄漏清洗单一真源 ----------
dsrc = nodes["uapp_s3_deliver"]["data"].get("code") or ""
check("D-S3-11", "本层交付节点的泄漏清洗复用 DELIVERY_SRC 前言，未另抄一套词表",
      "_STATE_WORDS" in dsrc and "_IDENTIFIERS" in dsrc and "def _scrub(" in dsrc,
      {"has_state_words": "_STATE_WORDS" in dsrc, "has_scrub": "def _scrub(" in dsrc})

# ---------- 受保护面零漂移 ----------
drift = []
for row in base["protected_dify_apps"]:
    got = psql("select md5(w.graph) from workflows w join apps a on a.workflow_id=w.id "
               "where a.id='%s';" % row["app_id"]).strip()
    if got != row["graph_md5"]:
        drift.append({"key": row["key"], "baseline": row["graph_md5"], "now": got})
check("D-S3-12", "11 个受保护应用 graph 相对 R0 基线零漂移", not drift,
      {"checked": len(base["protected_dify_apps"]), "drift": drift})
legacy_now = psql("select md5(w.graph) from workflows w join apps a on a.workflow_id=w.id "
                  "where a.id='%s';" % LEGACY).strip()
check("D-S3-13", "旧候选 app 2448e4f9 零改动",
      legacy_now == base["legacy_diagnostic_candidate"]["draft_graph_md5"],
      {"now": legacy_now})

out = {"stage": "S3", "app_id": APP, "model_calls": 0,
       "graph_sha256": hashlib.sha256(json.dumps(g, ensure_ascii=False, sort_keys=True)
                                      .encode("utf-8")).hexdigest(),
       "node_count": len(g["nodes"]), "edge_count": len(g["edges"]),
       "m3_reference_digests": digs, "checks": R,
       "summary": {"pass": sum(1 for r in R if r["result"] == "PASS"),
                   "fail": sum(1 for r in R if r["result"] == "FAIL"), "total": len(R)}}
print(json.dumps(out["summary"], ensure_ascii=False))
for r in R:
    print("  [%s] %s | %s" % (r["result"], r["id"], r["desc"]))
    if r["result"] == "FAIL":
        print("        ", json.dumps(r["detail"], ensure_ascii=False)[:400])
p = os.path.join(HERE, "..", "evidence",
                 os.environ.get("S3_CHECK_OUT", "S3_DETERMINISTIC_CHECKS.json"))
with io.open(p, "w", encoding="utf-8") as fh:
    fh.write(json.dumps(out, ensure_ascii=False, indent=2) + "\n")
