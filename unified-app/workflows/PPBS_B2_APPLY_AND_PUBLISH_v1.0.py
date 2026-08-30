#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PP 边界后继 b2｜把 b2 后继 Skill 载入 PP app 并发布新版本。**零模型调用。**

只改一个地方：PP app 的 `skill_llm` 节点 system prompt 文本。
注入尾巴与旧版**逐字相同**（从线上现取，不重写）。其余节点、边、features 一字不动。

发布**不重钉 provider**：Dify 的 workflow-as-tool 按版本钉取图，
provider 仍指向 2026-08-29 03:34:58.999575，Seam 与 M5 在 D1/D2 期间仍走旧 PP。

    python3 PPBS_B2_APPLY_AND_PUBLISH_v1.0.py --dry-run
    python3 PPBS_B2_APPLY_AND_PUBLISH_v1.0.py --apply
"""
import argparse
import hashlib
import importlib.util
import io
import json
import os
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
UAPP = os.path.abspath(os.path.join(HERE, ".."))
REPO = os.path.abspath(os.path.join(UAPP, ".."))
EVDIR = os.path.join(UAPP, "evidence", "stages", "pp_boundary_successor")
ENV = "/home/faye/diyu-demo-worktrees/m3-account-content-operator-v1/.env"
PP_APP = "c9cdea24-9df3-400b-9ecd-1d740e8c96df"
PP_PROVIDER_PIN_MUST_STAY = "2026-08-29 03:34:58.999575"
SUCCESSOR = os.path.join(REPO, "content-production/skills/"
                               "packaging-content-for-release-m4-b2/SKILL.md")
M4_SRC = os.path.join(REPO, "content-production/skills/"
                            "packaging-content-for-release-m4/SKILL.md")
EXPECT_GRAPH_MD5_BEFORE = "788c8555aca09e6fa6d979f237f70157"

_s = importlib.util.spec_from_file_location(
    "dc", os.path.join(REPO, "account-operations/tools/dify_client.py"))
DC = importlib.util.module_from_spec(_s)
_s.loader.exec_module(DC)


def psql(sql, db="dify"):
    p = subprocess.run(["docker", "exec", "-i", "docker-db_postgres-1", "psql", "-U", "postgres",
                        "-d", db, "-tA", "-c", sql], capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError("psql: " + (p.stderr or "")[:300])
    return p.stdout.strip()


def sha(s):
    return hashlib.sha256((s or "").encode("utf-8")).hexdigest()


def canon(o):
    return json.dumps(o, ensure_ascii=False, sort_keys=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    if not (a.dry_run or a.apply):
        raise SystemExit("必须显式选择 --dry-run 或 --apply")

    before_md5 = psql("select md5(w.graph) from workflows w join apps a "
                      "on a.workflow_id=w.id where a.id='%s';" % PP_APP)
    if before_md5 != EXPECT_GRAPH_MD5_BEFORE:
        raise SystemExit("现场 PP graph 与冻结基线不一致，拒绝修改（A3 先算影响面）：%s" % before_md5)

    console = DC.Console(env=DC.load_env(ENV))
    st, draft = console.call("GET", "/console/api/apps/%s/workflows/draft" % PP_APP, timeout=300)
    assert st == 200, ("draft get", st, str(draft)[:300])
    graph = draft["graph"]
    before_nodes = json.loads(canon(graph["nodes"]))
    before_edges = json.loads(canon(graph["edges"]))

    node = None
    for n in graph["nodes"]:
        if n.get("id") == "skill_llm":
            node = n
    assert node is not None, "skill_llm 节点不存在"
    pts = node["data"]["prompt_template"]
    sys_idx = [i for i, p in enumerate(pts) if p.get("role") == "system"]
    assert len(sys_idx) == 1, ("system prompt 不唯一", sys_idx)
    old_sys = pts[sys_idx[0]]["text"]

    m4 = io.open(M4_SRC, encoding="utf-8").read()
    assert old_sys.startswith(m4), "线上 system 不是以 M4 源 Skill 开头，拒绝改写"
    tail = old_sys[len(m4):]                      # 固定注入尾，逐字沿用
    new_skill = io.open(SUCCESSOR, encoding="utf-8").read()
    new_sys = new_skill + tail

    rep = {"document": {"id": "PPBS_B2_APPLY_AND_PUBLISH_v1.0",
                        "task_id": "DIYU-V1-PP-BOUNDARY-SUCCESSOR-001",
                        "model_calls": 0},
           "pp_app": PP_APP,
           "graph_md5_before": before_md5,
           "system_prompt_before": {"len": len(old_sys), "sha256": sha(old_sys)},
           "system_prompt_after": {"len": len(new_sys), "sha256": sha(new_sys)},
           "injection_tail": {"len": len(tail), "sha256": sha(tail),
                              "reused_verbatim_from_live": True},
           "successor_skill": {"file": os.path.relpath(SUCCESSOR, REPO),
                               "sha256": sha(new_skill), "len": len(new_skill)},
           "m4_source_skill": {"file": os.path.relpath(M4_SRC, REPO), "sha256": sha(m4)},
           "provider_pin_must_stay": PP_PROVIDER_PIN_MUST_STAY,
           "applied": False}

    pts[sys_idx[0]]["text"] = new_sys
    after_nodes = json.loads(canon(graph["nodes"]))
    touched = []
    for i, n in enumerate(after_nodes):
        if canon(n) != canon(before_nodes[i]):
            touched.append(n.get("id"))
    rep["nodes_touched"] = touched
    rep["edges_unchanged"] = canon(after_edges := graph["edges"]) == canon(before_edges)
    rep["node_count"] = len(graph["nodes"])
    rep["edge_count"] = len(graph["edges"])
    # 该节点内除 system prompt 外无其它变化
    b = [n for n in before_nodes if n.get("id") == "skill_llm"][0]
    aft = [n for n in after_nodes if n.get("id") == "skill_llm"][0]
    b2, a2 = json.loads(canon(b)), json.loads(canon(aft))
    for o in (b2, a2):
        for p in o["data"]["prompt_template"]:
            if p.get("role") == "system":
                p["text"] = "<SYSTEM>"
    rep["skill_llm_only_system_text_changed"] = canon(b2) == canon(a2)

    if touched != ["skill_llm"]:
        raise SystemExit("影响面超出单节点，拒绝写入：%s" % touched)
    if not rep["skill_llm_only_system_text_changed"]:
        raise SystemExit("skill_llm 节点除 system prompt 外还有变化，拒绝写入")
    if not rep["edges_unchanged"]:
        raise SystemExit("边集发生变化，拒绝写入")

    if a.apply:
        st, res = console.call("POST", "/console/api/apps/%s/workflows/draft" % PP_APP, body={
            "graph": graph, "features": draft.get("features") or {},
            "hash": draft.get("hash"),
            "environment_variables": draft.get("environment_variables") or [],
            "conversation_variables": draft.get("conversation_variables") or []}, timeout=900)
        assert st == 200, ("draft sync", st, str(res)[:400])
        st, pub = console.call("POST", "/console/api/apps/%s/workflows/publish" % PP_APP, body={
            "marked_name": "pp-b2-boundary",
            "marked_comment": "b2：strict_cta_closed 一次判定全面适用；PP-5 与作者转发语条件化；自检 17 全表面扫描"},
            timeout=900)
        assert st in (200, 201), ("publish", st, str(pub)[:400])
        rep["applied"] = True
        rep["publish_status"] = st
        rep["graph_md5_after"] = psql("select md5(w.graph) from workflows w join apps a "
                                      "on a.workflow_id=w.id where a.id='%s';" % PP_APP)
        rep["new_published_version"] = psql("select w.version from workflows w join apps a "
                                            "on a.workflow_id=w.id where a.id='%s';" % PP_APP)
        rep["provider_pin_now"] = psql("select p.version from tool_workflow_providers p "
                                       "where p.name='diyu_m5fp_publishing_packaging';")
        rep["provider_pin_unchanged"] = rep["provider_pin_now"] == PP_PROVIDER_PIN_MUST_STAY
        rep["old_workflow_rows_preserved"] = int(psql(
            "select count(*) from workflows where app_id='%s';" % PP_APP))

    os.makedirs(EVDIR, exist_ok=True)
    io.open(os.path.join(EVDIR, "PPBS_B2_APPLY_AND_PUBLISH.json"), "w",
            encoding="utf-8").write(json.dumps(rep, ensure_ascii=False, indent=1) + "\n")
    print(json.dumps(rep, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
