#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PP 边界后继｜Phase A 零模型现场核验与影响面。**零模型、零写入。**

task_id: DIYU-V1-PP-BOUNDARY-SUCCESSOR-001
authority: FOUNDER ADJUDICATION + EXECUTION PROMPT v1.0 第三节 Phase A

只读 Git、Dify 运行库与仓库文件，复算：分支/HEAD/origin、PP graph 与发布版本、
provider 与 Seam pin、全部 PP 基线绑定、worktree 状态；并按 A3 切出失效集与保持集。

    python3 PPBS_PHASE_A_SITE_CHECK_v1.0.py
"""
import hashlib
import io
import json
import os
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
UAPP = os.path.abspath(os.path.join(HERE, ".."))
REPO = os.path.abspath(os.path.join(UAPP, ".."))
EVDIR = os.path.join(UAPP, "evidence", "stages", "pp_boundary_successor")

PP_APP = "c9cdea24-9df3-400b-9ecd-1d740e8c96df"
PP_PROVIDER = "diyu_m5fp_publishing_packaging"
SEAM_APP = "5fca0162-e26b-4545-a00b-66b1a2a2a077"
CAND_APP = "85c01f85-a081-43e9-ab09-9993289cc200"
OTHER_PROTECTED = {"M1_HOST": "a4c3b19b-243f-490b-9aca-3aa19767d6a5",
                   "HOP": "6c46fdb1-5f49-4513-a0c0-29957b3dcee4",
                   "SEAM": SEAM_APP,
                   "MATRIX": "fd25ebfa-db67-40c3-82e5-202e1254facf",
                   "CAMPAIGN": "1f9d65ea-8af5-45f0-a1d0-a80223d354e2",
                   "CONTENT_BRIEF": "b1dcf784-540e-4b3f-8ba2-3812f477f3ce",
                   "CREATIVE_SCRIPT": "44b55f9d-3792-40c3-b095-f2696464b4ec",
                   "PRODUCTION_DIRECTOR": "13cfabd5-f592-4354-a304-47098b765697"}

PLANNING_OBSERVED = {
    "uapp_head": "2d70de0e7f567bdd0fbb421e0afa49f2f6d9bc4d",
    "pp_graph_md5": "788c8555aca09e6fa6d979f237f70157",
    "target_pp_app": PP_APP,
    "consumer_seam": SEAM_APP,
}


def psql(sql, db="dify"):
    p = subprocess.run(["docker", "exec", "-i", "docker-db_postgres-1", "psql", "-U", "postgres",
                        "-d", db, "-tA", "-c", sql], capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError("psql: " + (p.stderr or "")[:300])
    return p.stdout.strip()


def git(*a):
    return subprocess.run(["git", "-C", REPO] + list(a),
                          capture_output=True, text=True).stdout.strip()


def sha(s):
    return hashlib.sha256((s or "").encode("utf-8")).hexdigest()


def shaf(p):
    return hashlib.sha256(io.open(p, "rb").read()).hexdigest()


def main():
    subprocess.run(["git", "-C", REPO, "fetch", "origin"], capture_output=True, text=True)
    g = {"branch": git("rev-parse", "--abbrev-ref", "HEAD"),
         "head": git("rev-parse", "HEAD"),
         "origin_task_branch": git("rev-parse", "origin/codex/v1-uapp-progressive-canvas-001"),
         "origin_main": git("rev-parse", "origin/main"),
         "main": git("rev-parse", "main"),
         "porcelain": git("status", "--porcelain")}
    g["clean"] = g["porcelain"] == ""
    g["head_matches_planning_observed"] = g["head"] == PLANNING_OBSERVED["uapp_head"]

    ppgraph = psql("select w.graph from workflows w join apps a on a.workflow_id=w.id "
                   "where a.id='%s';" % PP_APP)
    ppg = json.loads(ppgraph)
    llm_nodes = {}
    for n in ppg["nodes"]:
        d = n.get("data", {})
        if d.get("type") == "llm":
            llm_nodes[n["id"]] = {
                "model": (d.get("model") or {}).get("name"),
                "prompts": [{"role": p.get("role"), "len": len(p.get("text") or ""),
                             "sha256": sha(p.get("text"))} for p in (d.get("prompt_template") or [])]}
    wf = psql("select coalesce(json_agg(json_build_object('id',id,'version',version,"
              "'md5',md5(graph),'created_at',created_at::text) order by created_at desc)::text,'[]') "
              "from workflows where app_id='%s';" % PP_APP)
    dify = {
        "pp_app_id": PP_APP,
        "pp_current_graph_md5": psql("select md5(w.graph) from workflows w join apps a "
                                     "on a.workflow_id=w.id where a.id='%s';" % PP_APP),
        "pp_app_points_at_workflow": psql("select a.workflow_id from apps a where a.id='%s';" % PP_APP),
        "pp_workflows": json.loads(wf),
        "pp_nodes": len(ppg["nodes"]), "pp_edges": len(ppg["edges"]),
        "pp_llm_nodes": llm_nodes,
        "pp_provider": psql("select p.id||'|'||p.name||'|'||p.version from "
                            "tool_workflow_providers p where p.name='%s';" % PP_PROVIDER),
        "seam_graph_md5": psql("select md5(w.graph) from workflows w join apps a "
                               "on a.workflow_id=w.id where a.id='%s';" % SEAM_APP),
        "seam_references_pp_by_provider_name": PP_PROVIDER in psql(
            "select (w.graph like '%%%s%%')::text from workflows w join apps a "
            "on a.workflow_id=w.id where a.id='%s';" % (PP_PROVIDER, SEAM_APP)).replace(
                "true", PP_PROVIDER),
        "candidate_graph_md5": psql("select md5(w.graph) from workflows w join apps a "
                                    "on a.workflow_id=w.id where a.id='%s';" % CAND_APP),
        "hop_pin": psql("select p.version from tool_workflow_providers p "
                        "where p.name='diyu_uapp_hop';"),
        "other_protected_md5": {k: psql("select md5(w.graph) from workflows w join apps a "
                                        "on a.workflow_id=w.id where a.id='%s';" % v).strip()
                                for k, v in sorted(OTHER_PROTECTED.items())},
    }
    dify["pp_md5_matches_planning_observed"] = (
        dify["pp_current_graph_md5"] == PLANNING_OBSERVED["pp_graph_md5"])
    drafts = [w for w in dify["pp_workflows"] if w["version"] == "draft"]
    pubs = [w for w in dify["pp_workflows"] if w["version"] != "draft"]
    dify["pp_draft_equals_published"] = bool(drafts and pubs and
                                             drafts[0]["md5"] == pubs[0]["md5"])

    # 现场枚举全部 PP md5 绑定
    binds = []
    for root, dirs, files in os.walk(REPO):
        if "/.git" in root:
            continue
        dirs[:] = [d for d in dirs if d != ".git"]
        for f in files:
            if not f.endswith((".json", ".md")):
                continue
            p = os.path.join(root, f)
            try:
                if PLANNING_OBSERVED["pp_graph_md5"] in io.open(p, encoding="utf-8",
                                                                errors="ignore").read():
                    binds.append(os.path.relpath(p, REPO))
            except Exception:
                pass
    binds = sorted(binds)

    # 皮肤对照：线上 system prompt 与仓库 Skill 的字节可回指
    live_sys = None
    for n in ppg["nodes"]:
        if n.get("data", {}).get("type") == "llm" and n["id"] == "skill_llm":
            for pt in n["data"].get("prompt_template") or []:
                if pt.get("role") == "system":
                    live_sys = pt.get("text")
    skill_p = os.path.join(REPO, "content-production/skills/"
                                 "packaging-content-for-release-m4/SKILL.md")
    repo_skill = io.open(skill_p, encoding="utf-8").read()
    tail = live_sys[len(repo_skill):] if live_sys and live_sys.startswith(repo_skill) else None
    provenance = {
        "repo_skill": os.path.relpath(skill_p, REPO),
        "repo_skill_sha256": shaf(skill_p), "repo_skill_len": len(repo_skill),
        "live_system_prompt_len": len(live_sys or ""),
        "live_system_prompt_sha256": sha(live_sys),
        "live_starts_with_repo_skill": bool(tail is not None),
        "injection_tail": tail, "injection_tail_len": len(tail or ""),
        "injection_tail_sha256": sha(tail),
    }

    impact = {
        "authorized_change": "PP app %s 的 skill_llm system prompt（后继 Skill 载体）；"
                             "发布新 workflow 版本；验证通过后重钉 provider" % PP_APP,
        "will_change_after_publish": ["apps.workflow_id → 新 workflow 行",
                                      "PP graph md5（由 %s 变为新值）"
                                      % PLANNING_OBSERVED["pp_graph_md5"]],
        "will_not_change": ["Seam graph（Seam 按 provider 名引用，不内嵌 PP 版本）",
                            "其余八个受保护应用 graph", "候选画布 graph", "hop_pin",
                            "旧 PP workflow 行（历史版本保留，不覆盖）"],
        "STALE_on_publish": [{"file": b, "why": "绑定 PP graph md5，PP 发布后该绑定过期，"
                                                "需建立 successor 记录，不覆盖原文"}
                             for b in binds],
        "M5_history": {"terminal_state": "DONE 原样保留，不改写",
                       "stale_subset": "仅『依赖 PP 输出内容』与『依赖 PP graph/provider 绑定』的结论",
                       "current_subset": "M1/M2/M3/Hop/Seam 路由结论、四份上游产物、无暗跑结论"},
        "CURRENT_kept": ["M1 任务上下文", "M2 持久化", "M3 单账号持续运营", "Hop 抽取与外壳",
                         "Seam 路由与透传", "四份上游 artifact（CB/CS/PD/PP-旧）已真实产生这一事实",
                         "每轮只运行一个目标能力、无暗跑",
                         "S4 载体侧 V-01…V-07、V-08A、V-09、S-01"],
        "not_stale": "不 blanket STALE：S4 载体结论与链路结论不依赖 PP 交付内容，保持 CURRENT。",
    }

    rep = {"document": {"id": "PPBS_PHASE_A_SITE_CHECK_v1.0",
                        "task_id": "DIYU-V1-PP-BOUNDARY-SUCCESSOR-001",
                        "parent_task_id": "DIYU-V1-UNIFIED-DIFY-APPLICATION-001",
                        "task_mode": "NEW_SUCCESSOR_TASK",
                        "authority": "FOUNDER ADJUDICATION + EXECUTION PROMPT v1.0 第三节 Phase A",
                        "model_calls": 0, "dify_writes": 0, "workflow_runs_started": 0},
           "planning_observed": PLANNING_OBSERVED,
           "git": g, "dify": dify,
           "pp_md5_bindings_found": binds,
           "pp_md5_binding_count": len(binds),
           "skill_provenance": provenance,
           "impact_surface": impact}
    os.makedirs(EVDIR, exist_ok=True)
    io.open(os.path.join(EVDIR, "PPBS_PHASE_A_SITE_CHECK.json"), "w",
            encoding="utf-8").write(json.dumps(rep, ensure_ascii=False, indent=1) + "\n")
    print("Git: %s @ %s  clean=%s  与规划侧一致=%s" % (g["branch"], g["head"][:12], g["clean"],
                                                     g["head_matches_planning_observed"]))
    print("origin/main = %s（未动）" % g["origin_main"][:12])
    print("PP graph md5 = %s  与规划侧一致=%s  draft==published=%s"
          % (dify["pp_current_graph_md5"], dify["pp_md5_matches_planning_observed"],
             dify["pp_draft_equals_published"]))
    print("PP provider = %s" % dify["pp_provider"])
    print("Seam md5 = %s  候选图 md5 = %s  hop_pin = %s"
          % (dify["seam_graph_md5"], dify["candidate_graph_md5"], dify["hop_pin"]))
    print("Skill 字节可回指：线上 system = 仓库 SKILL.md(%d) + 固定注入尾(%d) → %s"
          % (provenance["repo_skill_len"], provenance["injection_tail_len"],
             provenance["live_starts_with_repo_skill"]))
    print("PP md5 绑定处 %d：" % len(binds))
    for b in binds:
        print("   " + b)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
