#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""冻结统一 Founder Canvas 的候选 Manifest。

**Manifest 必须早于正式结果**（A2：判据事件必须早于结果事件）。本脚本只读现场、
只写一份新文件，且**拒绝覆盖已存在的 Manifest**——冻结过的东西不原地改，
要改就出新版本号。
"""
import hashlib
import io
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
APP_ID = "2448e4f9-818f-4b88-9311-d18546e97da9"
VERSION = os.environ.get("UAPP_MANIFEST_VERSION", "v1.0")


def psql(sql, db="dify"):
    p = subprocess.run(["docker", "exec", "-i", "docker-db_postgres-1", "psql", "-U", "postgres",
                        "-d", db, "-tA", "-c", sql], capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError("psql: " + (p.stderr or "")[:300])
    return p.stdout.strip()


def sha(b):
    return hashlib.sha256(b if isinstance(b, bytes) else b.encode("utf-8")).hexdigest()


def git(*args):
    return subprocess.run(["git", "-C", ROOT] + list(args),
                          capture_output=True, text=True).stdout.strip()


FP = {
    "M3": "a4c3b19b-243f-490b-9aca-3aa19767d6a5",
    "SEAM": "5fca0162-e26b-4545-a00b-66b1a2a2a077",
    "HOP_ADAPTER": "6c46fdb1-5f49-4513-a0c0-29957b3dcee4",
    "MATRIX": "fd25ebfa-db67-40c3-82e5-202e1254facf",
    "CAMPAIGN": "1f9d65ea-8af5-45f0-a1d0-a80223d354e2",
    "CONTENT_BRIEF": "b1dcf784-540e-4b3f-8ba2-3812f477f3ce",
    "CREATIVE_SCRIPT": "44b55f9d-3792-40c3-b095-f2696464b4ec",
    "PRODUCTION_DIRECTOR": "13cfabd5-f592-4354-a304-47098b765697",
    "PUBLISHING_PACKAGING": "c9cdea24-9df3-400b-9ecd-1d740e8c96df",
}


def main():
    out_path = os.path.join(HERE, "..", "docs",
                            "UAPP_CANDIDATE_RUN_MANIFEST_%s.yaml" % VERSION)
    if os.path.exists(out_path):
        raise SystemExit("拒绝覆盖已冻结的 Manifest：%s（要改就出新版本号）" % out_path)

    graph_raw = psql("select w.graph from workflows w join apps a on a.workflow_id=w.id "
                     "where a.id='%s';" % APP_ID)
    graph = json.loads(graph_raw)
    row = psql("select a.mode||'|'||a.status||'|'||w.id||'|'||w.version::text||'|'"
               "||coalesce(w.marked_name,'') from apps a join workflows w "
               "on w.id=a.workflow_id where a.id='%s';" % APP_ID)
    mode, status, wf_id, wf_version, marked = row.split("|")
    nodes = {n["id"]: n for n in graph["nodes"]}

    models = {}
    for nid, n in nodes.items():
        if n["data"].get("type") == "llm":
            m = n["data"]["model"]
            models[nid] = {"provider": m["provider"], "name": m["name"],
                           "completion_params": m.get("completion_params")}

    providers = {}
    for name in ("diyu_uapp_m3", "diyu_uapp_seam", "diyu_uapp_hop"):
        got = psql("select p.id||'|'||p.app_id||'|'||p.version from tool_workflow_providers p "
                   "where p.name='%s';" % name)
        pid, papp, pver = got.split("|")
        providers[name] = {"provider_id": pid, "bound_app_id": papp, "pinned_version": pver}

    fp_bind = {}
    for k, aid in FP.items():
        fp_bind[k] = {"app_id": aid,
                      "graph_md5": psql("select md5(w.graph) from apps a join workflows w "
                                        "on w.id=a.workflow_id where a.id='%s';" % aid)}

    m1_repo = io.open(os.path.join(ROOT, "decision-chain", "workflows",
                                   "m1_context_compiler_v0.1.py"), "rb").read()
    ref_dir = os.path.join(ROOT, "m3-account-content-operator-semantic-v1.0",
                           "skill-source", "references")
    refs = {}
    for f in ("fashion-and-market.md", "six-skill-methods.md", "operations.md",
              "acceptance-fixtures.md"):
        refs[f] = sha(io.open(os.path.join(ref_dir, f), "rb").read())

    node_srcs = {}
    for nid in ("uapp_route", "uapp_ctx", "uapp_delivery", "uapp_wb_prep", "uapp_side",
                "m1_compiler"):
        if nid in nodes:
            node_srcs[nid] = sha(nodes[nid]["data"]["code"])

    man = {
        "document": {
            "id": "UAPP_CANDIDATE_RUN_MANIFEST_%s" % VERSION,
            "task_id": "DIYU-V1-UNIFIED-DIFY-APPLICATION-001",
            "frozen_before_formal_runs": True,
            "hash_rule": "外部引用绑定本文件完整 UTF-8 字节的 SHA-256；本文件不自含 hash",
        },
        "application": {
            "name": "DIYU V1 · Unified Founder Canvas", "app_id": APP_ID,
            "workflow_id": wf_id, "mode": mode, "app_status": status,
            "published_version": wf_version, "published_version_name": marked,
            "graph_sha256": sha(json.dumps(graph, ensure_ascii=False, sort_keys=True)),
            "graph_md5": psql("select md5(w.graph) from apps a join workflows w "
                              "on w.id=a.workflow_id where a.id='%s';" % APP_ID),
            "node_count": len(graph["nodes"]), "edge_count": len(graph["edges"]),
        },
        "models": models,
        "task_providers": providers,
        "final_fp_bindings": fp_bind,
        "m1_source": {
            "repo_path": "decision-chain/workflows/m1_context_compiler_v0.1.py",
            "repo_sha256": sha(m1_repo),
            "in_graph_sha256": node_srcs.get("m1_compiler"),
            "verbatim": sha(m1_repo) == node_srcs.get("m1_compiler"),
        },
        "m3_method_references_sha256": refs,
        "canvas_own_node_sources_sha256": node_srcs,
        "m2_service": {
            "base_url": "http://diyu-m2-app:8000",
            "reached_from": "Dify HTTP 节点经 ssrf_proxy:3128",
            "test_domain_policy": "会话级 workspace/account/cycle/task；"
                                  "publish/feedback 恒 is_test=true 且 is_simulated=true",
        },
        "git": {"commit": git("rev-parse", "HEAD"),
                "branch": git("rev-parse", "--abbrev-ref", "HEAD"),
                "tracked_clean": git("status", "--porcelain") == ""},
        "sampling_rule": "每个正式输入一次；纯传输失败且无模型输出时最多重试一次并保留两个 "
                         "Attempt；不得重复采样追求 PASS",
        "evidence_policy": "只追加。运行证据文件名一旦存在即拒绝覆盖（见 UAPP_RUN_v1.0.py）。",
    }

    with io.open(out_path, "w", encoding="utf-8") as fh:
        fh.write(json.dumps(man, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"written": out_path,
                      "manifest_sha256": sha(io.open(out_path, "rb").read()),
                      "app_graph_sha256": man["application"]["graph_sha256"],
                      "m1_verbatim": man["m1_source"]["verbatim"],
                      "nodes": man["application"]["node_count"]},
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
