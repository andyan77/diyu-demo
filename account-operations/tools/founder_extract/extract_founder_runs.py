#!/usr/bin/env python3
"""Founder 七场景实测运行的只读提取与绑定（CONTINUE_TASK，零模型调用）。

授权范围：只读取 Dify 后台记录。**不修改、不删除、不重放、不覆盖任何运行记录。**

绑定规则（Founder 授权 §2）：不得按「最近七次」选择。必须用
App ID + 已发布候选 + 七个冻结输入的逐字内容与 SHA-256 + 运行时间 +
三个输入框 + FREEZE_MANIFEST 场景绑定 + workflow run / node execution 交叉定位。
"""
import hashlib
import io
import json
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import dify_client as D  # noqa: E402

WORKTREE = "/home/faye/diyu-demo-worktrees/m3-account-content-operator-v1"
APP = "b7fb5b1a-9278-426c-bb8a-f9f288639548"
PACK = os.path.join(WORKTREE, "account-operations/founder-pack-v152")
INPUTS = os.path.join(PACK, "inputs")
OUT = os.path.join(WORKTREE, "account-operations/evidence/ep39-founder-seven-run-extraction")
FIELDS = ("account_context", "user_request", "loaded_references")


def sha(t):
    return hashlib.sha256(t.encode("utf-8")).hexdigest()


def canon(o):
    return json.dumps(o, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def read(p):
    with io.open(p, encoding="utf-8") as f:
        return f.read()


def write(p, t):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with io.open(p, "w", encoding="utf-8", newline="") as f:
        f.write(t)


def frozen_inputs():
    """冻结包七个场景的三段输入原文与哈希。"""
    out = {}
    for n in range(1, 8):
        s = "S%d" % n
        out[s] = {k: read(os.path.join(INPUTS, "%s_%s.txt" % (s, k))) for k in FIELDS}
    return out


def field_delta(frozen, actual):
    """逐字比较一个输入框。返回可机械复算的差异描述，不做主观判断。"""
    if frozen == actual:
        return {"verdict": "IDENTICAL", "detail": None}
    if frozen.strip() == actual.strip():
        return {"verdict": "WHITESPACE_ONLY",
                "detail": {"frozen_len": len(frozen), "actual_len": len(actual),
                           "frozen_lead": repr(frozen[:len(frozen) - len(frozen.lstrip())]),
                           "frozen_trail": repr(frozen[len(frozen.rstrip()):]),
                           "actual_lead": repr(actual[:len(actual) - len(actual.lstrip())]),
                           "actual_trail": repr(actual[len(actual.rstrip()):]),
                           "core_sha256": sha(frozen.strip())}}
    # 实质差异：给出第一个不同字符的位置，便于定向复核
    i = 0
    while i < min(len(frozen), len(actual)) and frozen[i] == actual[i]:
        i += 1
    return {"verdict": "SUBSTANTIVE_DIFF",
            "detail": {"first_diff_index": i,
                       "frozen_around": frozen[max(0, i - 40):i + 40],
                       "actual_around": actual[max(0, i - 40):i + 40],
                       "frozen_len": len(frozen), "actual_len": len(actual)}}


def main():
    os.makedirs(OUT, exist_ok=True)
    c = D.Console()
    extracted_at = time.strftime("%Y-%m-%dT%H:%M:%S%z")

    # ---- 1. 枚举全部 workflow-app-logs，按 created_from 分离，不按「最近 N 次」 ----
    rows, page = [], 1
    while True:
        st, r = c.call("GET",
                       "/console/api/apps/%s/workflow-app-logs?page=%d&limit=100" % (APP, page))
        assert st == 200, (st, r)
        rows += r.get("data") or []
        if not r.get("has_more"):
            break
        page += 1
    web = [x for x in rows if x.get("created_from") == "web-app"]
    web.sort(key=lambda y: y["workflow_run"]["created_at"])
    write(os.path.join(OUT, "app_logs_census.json"), json.dumps({
        "extracted_at": extracted_at, "transport": c.transport,
        "total_logs": len(rows),
        "by_created_from": {k: sum(1 for x in rows if x.get("created_from") == k)
                            for k in sorted({x.get("created_from") for x in rows})},
        "web_app_runs": [{"run_id": x["workflow_run"]["id"],
                          "created_at": x["workflow_run"]["created_at"],
                          "created_at_local": time.strftime(
                              "%Y-%m-%d %H:%M:%S", time.localtime(x["workflow_run"]["created_at"])),
                          "status": x["workflow_run"]["status"],
                          "elapsed_time": x["workflow_run"].get("elapsed_time"),
                          "end_user_session": (x.get("created_by_end_user") or {}).get("session_id")}
                         for x in web],
    }, ensure_ascii=False, indent=2))

    # ---- 2. 已发布版本谱系（只读） ----
    st, wfs = c.call("GET", "/console/api/apps/%s/workflows?page=1&limit=100" % APP)
    assert st == 200
    versions = [{"workflow_id": w.get("id"), "version": w.get("version"),
                 "marked_name": w.get("marked_name"), "created_at": w.get("created_at"),
                 "created_at_local": time.strftime("%Y-%m-%d %H:%M:%S",
                                                   time.localtime(w["created_at"]))}
                for w in wfs.get("items", [])]
    write(os.path.join(OUT, "published_version_lineage.json"),
          json.dumps({"extracted_at": extracted_at, "versions": versions},
                     ensure_ascii=False, indent=2))

    # ---- 3. 拉取每条运行的完整记录与节点执行记录 ----
    froz = frozen_inputs()
    froz_sig = {s: sha("\x00".join(froz[s][k] for k in FIELDS)) for s in froz}
    froz_sig_core = {s: sha("\x00".join(froz[s][k].strip() for k in FIELDS)) for s in froz}

    runs = []
    for x in web:
        rid = x["workflow_run"]["id"]
        st, run = c.call("GET", "/console/api/apps/%s/workflow-runs/%s" % (APP, rid))
        assert st == 200, (st, run)
        st, nx = c.call("GET", "/console/api/apps/%s/workflow-runs/%s/node-executions" % (APP, rid))
        assert st == 200, (st, nx)
        nodes = nx["data"]
        write(os.path.join(OUT, "raw", rid, "workflow_run.json"),
              json.dumps(run, ensure_ascii=False, indent=2))
        write(os.path.join(OUT, "raw", rid, "node_executions.json"),
              json.dumps(nodes, ensure_ascii=False, indent=2))

        inp = run["inputs"] if isinstance(run["inputs"], dict) else json.loads(run["inputs"])
        sig = sha("\x00".join(inp.get(k, "") for k in FIELDS))
        sig_core = sha("\x00".join(inp.get(k, "").strip() for k in FIELDS))
        exact = [s for s in froz_sig if froz_sig[s] == sig]
        core = [s for s in froz_sig_core if froz_sig_core[s] == sig_core]
        runs.append({
            "run_id": rid, "run": run, "nodes": nodes, "inputs": inp,
            "input_signature_sha256": sig, "input_core_signature_sha256": sig_core,
            "match_exact": exact, "match_core": core,
            "truncation_flags": sorted({(n.get("inputs_truncated"), n.get("outputs_truncated"),
                                         n.get("process_data_truncated")) for n in nodes}),
        })

    # ---- 4. 执行图与冻结图的逐字节比较 ----
    frozen_graph = json.load(io.open(os.path.join(
        WORKTREE, "account-operations/evidence/ep35-candidate-v152-freeze/"
                  "m3_app_draft_graph_v152.json"), encoding="utf-8"))
    fg = frozen_graph["graph"]
    fg_sha = sha(canon(fg))

    def graph_delta(g):
        """把「执行语义」与「画布外观」分开算。data 决定行为，几何不决定。"""
        an = {n["id"]: n for n in fg["nodes"]}
        bn = {n["id"]: n for n in g["nodes"]}
        node_data_same = (set(an) == set(bn) and
                          all(canon(an[i].get("data")) == canon(bn[i].get("data")) for i in an))

        def topo(e):
            return (e["source"], e["target"], e.get("sourceHandle"), e.get("targetHandle"))
        edge_topo_same = (sorted(map(topo, fg["edges"])) == sorted(map(topo, g["edges"])))

        def strip_ui(e):
            e = json.loads(json.dumps(e))
            e.get("data", {}).pop("isInLoop", None)
            return canon(e)
        edge_same_mod_isinloop = sorted(map(strip_ui, fg["edges"])) == sorted(map(strip_ui, g["edges"]))
        geom = {}
        for i in sorted(set(an) & set(bn)):
            d = {k: [an[i].get(k), bn[i].get(k)] for k in ("position", "positionAbsolute", "height", "width")
                 if canon(an[i].get(k)) != canon(bn[i].get(k))}
            if d:
                geom[i] = d
        return {
            "canon_sha256": sha(canon(g)),
            "byte_identical_to_frozen_graph": canon(g) == canon(fg),
            "all_node_data_byte_identical": node_data_same,
            "edge_topology_identical": edge_topo_same,
            "edges_identical_modulo_isInLoop_flag": edge_same_mod_isinloop,
            "viewport_frozen": fg.get("viewport"), "viewport_actual": g.get("viewport"),
            "node_geometry_deltas": geom,
        }

    for r in runs:
        r["graph_delta"] = graph_delta(r["run"]["graph"])

    write(os.path.join(OUT, "frozen_graph_reference.json"), json.dumps(
        {"source": "account-operations/evidence/ep35-candidate-v152-freeze/"
                   "m3_app_draft_graph_v152.json",
         "dify_hash": frozen_graph.get("hash"), "canon_sha256": fg_sha},
        ensure_ascii=False, indent=2))

    json.dump({"runs": [{k: v for k, v in r.items() if k not in ("run", "nodes")} for r in runs]},
              io.open(os.path.join(OUT, "_binding_intermediate.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    print("提取完成：%d 条 web-app 运行，%d 条日志总数" % (len(runs), len(rows)))
    print("传输路径:", c.transport)
    for r in runs:
        g = r["graph_delta"]
        print(" ", r["run_id"][:8], r["run"]["version"], "exact=", r["match_exact"],
              "core=", r["match_core"], "| node_data_same=", g["all_node_data_byte_identical"],
              "| edge_topo_same=", g["edge_topology_identical"])
    return runs


if __name__ == "__main__":
    main()
