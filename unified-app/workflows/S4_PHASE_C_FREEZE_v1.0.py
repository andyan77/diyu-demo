#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Phase C 冻结生成器｜零模型调用。

产出两样东西，都必须在任何一次模型调用之前落盘并提交：
  1. S4_PHASE_C_C1_INPUT_v1.0.json —— C1 层（Content Brief 受影响模块单点）的逐字机器输入。
     capability_call / professional_input 不是执行侧代写的，而是把**线上钉住的**
     hop m5_compose 代码，在冻结的 S4-CO-T2 真实载荷上确定性重放一次得到的字节。
     entry / run_mode / example_reference_requested 逐字取自 T2 那次真实运行的 entry_resolver。
  2. S4_PHASE_C_BINDING_v1.0.json —— 冻结时刻的候选绑定现场（图、代码、受保护基线、Git）。

本文件不判定、不调用模型、不写 Dify。
"""
import hashlib
import importlib.util
import io
import json
import os
import subprocess
import types

HERE = os.path.dirname(os.path.abspath(__file__))
UAPP = os.path.abspath(os.path.join(HERE, ".."))
REPO = os.path.abspath(os.path.join(UAPP, ".."))
STAGES = os.path.join(UAPP, "stages")
EVID = os.path.join(UAPP, "evidence")

CANVAS = "85c01f85-a081-43e9-ab09-9993289cc200"
HOP = "6c46fdb1-5f49-4513-a0c0-29957b3dcee4"
SEAM = "5fca0162-e26b-4545-a00b-66b1a2a2a077"
CB = "b1dcf784-540e-4b3f-8ba2-3812f477f3ce"
T2_SEAM_RUN = "51c0b815-3bd1-4770-be7a-ddd6291b297c"

PROTECTED = {
    "M1_HOST": "a4c3b19b-243f-490b-9aca-3aa19767d6a5",
    "HOP": "6c46fdb1-5f49-4513-a0c0-29957b3dcee4",
    "SEAM": "5fca0162-e26b-4545-a00b-66b1a2a2a077",
    "MATRIX": "fd25ebfa-db67-40c3-82e5-202e1254facf",
    "CAMPAIGN": "1f9d65ea-8af5-45f0-a1d0-a80223d354e2",
    "CONTENT_BRIEF": "b1dcf784-540e-4b3f-8ba2-3812f477f3ce",
    "CREATIVE_SCRIPT": "44b55f9d-3792-40c3-b095-f2696464b4ec",
    "PRODUCTION_DIRECTOR": "13cfabd5-f592-4354-a304-47098b765697",
    "PUBLISHING_PACKAGING": "c9cdea24-9df3-400b-9ecd-1d740e8c96df",
}


def psql(sql, db="dify"):
    p = subprocess.run(["docker", "exec", "-i", "docker-db_postgres-1", "psql", "-U", "postgres",
                        "-d", db, "-tA", "-c", sql], capture_output=True, text=True)
    if p.returncode:
        raise RuntimeError("psql: " + (p.stderr or "")[:300])
    return p.stdout.strip()


def sha(s):
    return hashlib.sha256(s.encode("utf-8") if isinstance(s, str) else s).hexdigest()


def git(*a):
    return subprocess.run(["git", "-C", REPO] + list(a), capture_output=True,
                          text=True).stdout.strip()


def pinned_hop_graph():
    """provider 钉住的那一版 hop 图——这才是画布真正会调用的代码。"""
    ver = psql("select p.version from tool_workflow_providers p where p.name='diyu_uapp_hop';")
    g = psql("select w.graph from workflows w where w.app_id='%s' and w.version='%s';" % (HOP, ver))
    return ver, json.loads(g)


def load_mod(src, name):
    m = types.ModuleType(name)
    exec(compile(src, name, "exec"), m.__dict__)
    return m


def main():
    # ---------- 1. 冻结绑定 ----------
    hop_ver, hop_graph = pinned_hop_graph()
    HN = {n["id"]: n for n in hop_graph["nodes"]}
    compose_src = HN["m5_compose"]["data"]["code"]

    canvas_graph = json.loads(psql(
        "select w.graph from workflows w join apps a on a.workflow_id=w.id where a.id='%s';" % CANVAS))
    canvas_sha = sha(json.dumps(canvas_graph, ensure_ascii=False, sort_keys=True))

    binding = {
        "document": {
            "id": "S4_PHASE_C_BINDING_v1.0",
            "task_id": "DIYU-V1-UNIFIED-DIFY-APPLICATION-001",
            "generated_by": "S4_PHASE_C_FREEZE_v1.0.py",
            "model_calls": 0, "dify_writes": 0,
            "purpose": "Phase C 调用之前的候选绑定现场；调用开始后本文件不再变更",
        },
        "candidate_canvas": {
            "app_id": CANVAS,
            "published_graph_sha256": canvas_sha,
            "node_count": len(canvas_graph["nodes"]),
            "edge_count": len(canvas_graph["edges"]),
            "published_version": psql(
                "select w.version from workflows w join apps a on a.workflow_id=w.id "
                "where a.id='%s';" % CANVAS),
        },
        "hop_pinned_by_provider": {
            "app_id": HOP,
            "provider_name": "diyu_uapp_hop",
            "pinned_version": hop_ver,
            "app_published_version": psql(
                "select w.version from workflows w join apps a on a.workflow_id=w.id "
                "where a.id='%s';" % HOP),
            "m5_compose_sha256": sha(compose_src),
            "other_nodes_sha256": {k: sha(json.dumps(HN[k], ensure_ascii=False, sort_keys=True))
                                   for k in sorted(HN) if k != "m5_compose"},
        },
        "all_uapp_provider_pins": json.loads(psql(
            "select coalesce(json_agg(json_build_object('name',p.name,'pinned',p.version,"
            "'app_published',w.version,'aligned',p.version=w.version))::text,'[]') "
            "from tool_workflow_providers p join apps a on a.id=p.app_id "
            "join workflows w on w.id=a.workflow_id where p.name like 'diyu_uapp%';")),
        "protected_apps_graph_md5": {
            k: psql("select md5(w.graph) from workflows w join apps a on a.workflow_id=w.id "
                    "where a.id='%s';" % v) for k, v in sorted(PROTECTED.items())},
        "git": {
            "branch": git("rev-parse", "--abbrev-ref", "HEAD"),
            "head_at_generation": git("rev-parse", "HEAD"),
            "porcelain_at_generation": git("status", "--porcelain").splitlines(),
        },
    }

    # ---------- 2. C1 逐字机器输入（确定性重放，零模型） ----------
    t2 = json.load(io.open(os.path.join(
        EVID, "stages", "s4_continuation01", "S4-CO-T2.json"), encoding="utf-8"))
    N = {n["node_id"]: n for n in t2["node_detail"]}
    hi = json.loads(N["uapp_hop"]["inputs"])
    ho = json.loads(N["uapp_hop"]["outputs"])
    raw = json.dumps({"fields": json.loads(ho["extracted_json"]),
                      "_sources": json.loads(ho["source_map_json"])}, ensure_ascii=False)

    M = load_mod(compose_src, "pinned_compose")
    out = M.main(raw, hi["target_capability"], hi["m3_judgment"], hi["upstream_delivery"],
                 hi["upstream_capability"], hi["registered_facts"], hi["account_context"],
                 hi["user_request"], hi["focus_fields"])

    gaps = [x.strip() for x in (out["extraction_gaps_text"] or "").split("；")
            if x.strip() and x.strip() != "无"]
    if gaps:
        raise SystemExit("重放仍有缺口，C1 输入不成立，拒绝冻结：%s" % gaps)

    er = json.loads(psql("select outputs from workflow_node_executions "
                         "where workflow_run_id='%s' and node_id='entry_resolver';" % T2_SEAM_RUN))
    cb_in = json.loads(psql("select inputs from workflow_node_executions "
                            "where workflow_run_id='%s' and node_id='tool_content_brief';"
                            % T2_SEAM_RUN))

    c1 = {
        "document": {
            "id": "S4_PHASE_C_C1_INPUT_v1.0",
            "task_id": "DIYU-V1-UNIFIED-DIFY-APPLICATION-001",
            "layer": "C1｜Content Brief 受影响模块单点",
            "frozen_before_any_model_run": True,
            "model_calls_to_produce_this_file": 0,
            "provenance": {
                "capability_call/professional_input":
                    "把 provider 钉住的 hop m5_compose（%s）在冻结载荷 S4-CO-T2 的真实 uapp_hop "
                    "入参上确定性重放一次得到，执行侧一字未改、未增、未删" % sha(compose_src)[:16],
                "entry/run_mode/example_reference_requested":
                    "逐字取自 T2 真实运行 %s 的 entry_resolver 与 tool_content_brief 入参" % T2_SEAM_RUN,
                "no_executor_authored_business_content":
                    "本文件不含任何执行侧代写的经营事实、专业产物或用户决定",
            },
        },
        "target": {"app_id": CB, "app_mode": "workflow", "endpoint": "/v1/workflows/run",
                   "published_version": psql(
                       "select w.version from workflows w join apps a on a.workflow_id=w.id "
                       "where a.id='%s';" % CB)},
        "replay_source": {
            "evidence_file": "unified-app/evidence/stages/s4_continuation01/S4-CO-T2.json",
            "hop_inputs_sha256": sha(json.dumps(hi, ensure_ascii=False, sort_keys=True)),
            "registered_facts_len": len(hi["registered_facts"] or ""),
            "pinned_m5_compose_sha256": sha(compose_src),
            "replayed_gaps": gaps,
            "replayed_source_map": json.loads(out["source_map_json"]),
        },
        "inputs": {
            "capability_call": out["capability_call"],
            "professional_input": out["professional_input"],
            "entry": cb_in.get("entry") or er.get("entry_resolved"),
            "run_mode": er.get("run_mode") or "",
            "example_reference_requested": cb_in.get("example_reference_requested") or "NO",
        },
    }
    c1["inputs_sha256"] = {k: sha(str(v)) for k, v in c1["inputs"].items()}

    os.makedirs(STAGES, exist_ok=True)
    for name, doc in (("S4_PHASE_C_BINDING_v1.0.json", binding),
                      ("S4_PHASE_C_C1_INPUT_v1.0.json", c1)):
        p = os.path.join(STAGES, name)
        if os.path.exists(p):
            raise SystemExit("拒绝覆盖已冻结文件：" + p)
        io.open(p, "w", encoding="utf-8").write(json.dumps(doc, ensure_ascii=False, indent=1) + "\n")
        print("WROTE %s  sha256=%s" % (name, sha(io.open(p, "rb").read())))

    print(json.dumps({
        "canvas_graph_sha256": canvas_sha,
        "canvas_nodes_edges": [len(canvas_graph["nodes"]), len(canvas_graph["edges"])],
        "hop_pinned_version": hop_ver,
        "pinned_m5_compose_sha256": sha(compose_src),
        "c1_gaps": gaps,
        "c1_facts_registered_in_envelope": "`facts_registered`" in out["capability_call"],
        "c1_capability_call_len": len(out["capability_call"]),
        "c1_professional_input_len": len(out["professional_input"]),
        "git_head": binding["git"]["head_at_generation"],
    }, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
