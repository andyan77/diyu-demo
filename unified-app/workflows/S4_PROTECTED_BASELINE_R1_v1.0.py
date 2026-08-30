#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TD-UAPP-21｜建立 Phase B 后继受保护基线 R1。零模型调用、零 Dify 写入。

规划侧裁决：接受 Phase B 修复后的 HOP 版本作为下一轮新受保护基线，
但必须是**新的版本化基线文件**。旧 UAPP_R0_PROTECTED_BASELINE.json 原样保留。

新基线只是下一轮的漂移判据，不等于整个 S4 已验收。
"""
import hashlib
import io
import json
import os
import subprocess
import time

HERE = os.path.dirname(os.path.abspath(__file__))
UAPP = os.path.abspath(os.path.join(HERE, ".."))
REPO = os.path.abspath(os.path.join(UAPP, ".."))
OUT = os.path.join(UAPP, "evidence", "UAPP_R1_PROTECTED_BASELINE_v1.0.json")
OLD = os.path.join(UAPP, "evidence", "UAPP_R0_PROTECTED_BASELINE.json")

CANVAS = "85c01f85-a081-43e9-ab09-9993289cc200"
HOP = "6c46fdb1-5f49-4513-a0c0-29957b3dcee4"
PROTECTED = {"M1_HOST": "a4c3b19b-243f-490b-9aca-3aa19767d6a5", "HOP": HOP,
             "SEAM": "5fca0162-e26b-4545-a00b-66b1a2a2a077",
             "MATRIX": "fd25ebfa-db67-40c3-82e5-202e1254facf",
             "CAMPAIGN": "1f9d65ea-8af5-45f0-a1d0-a80223d354e2",
             "CONTENT_BRIEF": "b1dcf784-540e-4b3f-8ba2-3812f477f3ce",
             "CREATIVE_SCRIPT": "44b55f9d-3792-40c3-b095-f2696464b4ec",
             "PRODUCTION_DIRECTOR": "13cfabd5-f592-4354-a304-47098b765697",
             "PUBLISHING_PACKAGING": "c9cdea24-9df3-400b-9ecd-1d740e8c96df"}


def psql(sql, db="dify"):
    p = subprocess.run(["docker", "exec", "-i", "docker-db_postgres-1", "psql", "-U", "postgres",
                        "-d", db, "-tA", "-c", sql], capture_output=True, text=True)
    if p.returncode:
        raise RuntimeError("psql: " + (p.stderr or "")[:300])
    return p.stdout.strip()


def sha(x):
    return hashlib.sha256(x.encode("utf-8") if isinstance(x, str) else x).hexdigest()


def git(*a):
    return subprocess.run(["git", "-C", REPO] + list(a), capture_output=True, text=True).stdout.strip()


def app_detail(aid):
    graw = psql("select w.graph from workflows w join apps a on a.workflow_id=w.id "
                "where a.id='%s';" % aid)
    g = json.loads(graw)
    ver = psql("select w.version from workflows w join apps a on a.workflow_id=w.id "
               "where a.id='%s';" % aid)
    md5 = psql("select md5(w.graph) from workflows w join apps a on a.workflow_id=w.id "
               "where a.id='%s';" % aid)
    models, prompts, params, codes = {}, {}, {}, {}
    for n in g["nodes"]:
        d = n.get("data") or {}
        nid = n["id"]
        if d.get("model"):
            models[nid] = {"provider": d["model"].get("provider"),
                           "name": d["model"].get("name"),
                           "completion_params_sha256": sha(json.dumps(
                               d["model"].get("completion_params") or {}, sort_keys=True,
                               ensure_ascii=False))}
        if d.get("prompt_template"):
            prompts[nid] = sha(json.dumps(d["prompt_template"], sort_keys=True, ensure_ascii=False))
        if d.get("tool_parameters"):
            params[nid] = sha(json.dumps(d["tool_parameters"], sort_keys=True, ensure_ascii=False))
        if d.get("code"):
            codes[nid] = sha(d["code"])
    return {"app_id": aid, "name": psql("select name from apps where id='%s';" % aid),
            "published_version": ver, "graph_md5": md5,
            "graph_sha256": sha(json.dumps(g, ensure_ascii=False, sort_keys=True)),
            "node_count": len(g["nodes"]), "edge_count": len(g["edges"]),
            "model_hashes": models, "prompt_hashes": prompts,
            "tool_parameter_hashes": params, "code_node_hashes": codes}


def main():
    if os.path.exists(OUT):
        raise SystemExit("拒绝覆盖已存在的基线：" + OUT)
    pin = psql("select p.version from tool_workflow_providers p where p.name='diyu_uapp_hop';")
    # 必须从整图 JSON 解析取代码，不能用 psql 文本直取——后者会吞掉尾部换行，
    # 算出的哈希与冻结绑定对不上（实测差 2 个字符）。这里同时用 SQL 内部算一次交叉校验。
    _pg = json.loads(psql("select w.graph from workflows w where w.app_id='%s' and w.version='%s';"
                          % (HOP, pin)))
    compose = [n for n in _pg["nodes"] if n["id"] == "m5_compose"][0]["data"]["code"]
    _sql_sha = psql("select encode(sha256(convert_to((select n->'data'->>'code' from workflows w, "
                    "jsonb_array_elements(w.graph::jsonb->'nodes') n where w.app_id='%s' "
                    "and w.version='%s' and n->>'id'='m5_compose'),'UTF8')),'hex');" % (HOP, pin))
    assert sha(compose) == _sql_sha, ("m5_compose 哈希两种口径不一致", sha(compose), _sql_sha)
    doc = {
        "document": {
            "id": "UAPP_R1_PROTECTED_BASELINE_v1.0",
            "task_id": "DIYU-V1-UNIFIED-DIFY-APPLICATION-001",
            "authority": "规划侧裁决 TD-UAPP-21：接受 Phase B 修复后的 HOP 版本作为下一轮新受保护基线",
            "supersedes_for_drift_check_only": {
                "file": "unified-app/evidence/UAPP_R0_PROTECTED_BASELINE.json",
                "sha256": sha(io.open(OLD, "rb").read()),
                "not_overwritten": "R0 原样保留、不覆盖、不改写；它仍是 Phase B 之前那一轮的历史基线"},
            "scope_limit": "新基线只是下一轮的漂移判据，**不等于整个 S4 已验收**，"
                           "也不改变任何既有 AC 状态。",
            "model_calls": 0, "dify_writes": 0,
            "frozen_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "git_branch": git("rev-parse", "--abbrev-ref", "HEAD"),
            "git_head": git("rev-parse", "HEAD"),
            "git_porcelain": git("status", "--porcelain").splitlines(),
        },
        "hop_post_repair_identity": {
            "app_id": HOP, "provider_name": "diyu_uapp_hop", "provider_pinned_version": pin,
            "m5_compose_sha256": sha(compose),
            "m5_compose_sha256_cross_checked_in_sql": _sql_sha,
            "repair_ref": "unified-app/workflows/S4_HOP_FACT_FLOOR_REPAIR_v1.0.py",
            "pre_repair_m5_compose_sha256":
                "f444166c7beef5f78045a7708857698a51ba6c14623c06a48798dcb696c1e171"},
        "candidate_canvas": app_detail(CANVAS),
        "protected_apps": {k: app_detail(v) for k, v in sorted(PROTECTED.items())},
        "protected_apps_graph_md5": {k: psql(
            "select md5(w.graph) from workflows w join apps a on a.workflow_id=w.id "
            "where a.id='%s';" % v) for k, v in sorted(PROTECTED.items())},
        "all_uapp_provider_pins": json.loads(psql(
            "select coalesce(json_agg(json_build_object('name',p.name,'pinned',p.version,"
            "'app_published',w.version,'aligned',p.version=w.version))::text,'[]') "
            "from tool_workflow_providers p join apps a on a.id=p.app_id "
            "join workflows w on w.id=a.workflow_id where p.name like 'diyu_uapp%';")),
    }
    io.open(OUT, "w", encoding="utf-8").write(json.dumps(doc, ensure_ascii=False, indent=1) + "\n")
    print("WROTE %s sha256=%s" % (os.path.basename(OUT), sha(io.open(OUT, "rb").read())))
    print(json.dumps({"candidate_graph_sha256": doc["candidate_canvas"]["graph_sha256"],
                      "candidate_nodes_edges": [doc["candidate_canvas"]["node_count"],
                                                doc["candidate_canvas"]["edge_count"]],
                      "hop_pin": pin, "m5_compose_sha256": doc["hop_post_repair_identity"]["m5_compose_sha256"],
                      "protected_md5": doc["protected_apps_graph_md5"],
                      "git_head": doc["document"]["git_head"]}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
