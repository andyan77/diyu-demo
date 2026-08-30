#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PP 边界后继 b2｜D3 绑定回指。**零模型调用、只读。**

从**真实节点运行记录**把 UAPP → Seam → PP 这条链逐跳指出来，并证明
本次 PP 执行用的确实是 b2 后继版本（按 workflow 行 id 与 graph md5 回指，
不看名字、不看时间巧合）。

    python3 PPBS_B2_D3_BINDING_TRACE_v1.0.py
"""
import io
import json
import os
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
UAPP = os.path.abspath(os.path.join(HERE, ".."))
EVDIR = os.path.join(UAPP, "evidence", "stages", "pp_boundary_successor")
PP_APP = "c9cdea24-9df3-400b-9ecd-1d740e8c96df"
SEAM_APP = "5fca0162-e26b-4545-a00b-66b1a2a2a077"
CAND = "85c01f85-a081-43e9-ab09-9993289cc200"
B2_MD5 = "8366328bf827bd0f460455d750d45c4f"
STABLE_MD5 = "788c8555aca09e6fa6d979f237f70157"
B1_MD5 = "7940dc009d0bba06e1b5ca99dac61e2e"
OTHER_FIVE = {"MATRIX": "fd25ebfa-db67-40c3-82e5-202e1254facf",
              "CAMPAIGN": "1f9d65ea-8af5-45f0-a1d0-a80223d354e2",
              "CONTENT_BRIEF": "b1dcf784-540e-4b3f-8ba2-3812f477f3ce",
              "CREATIVE_SCRIPT": "44b55f9d-3792-40c3-b095-f2696464b4ec",
              "PRODUCTION_DIRECTOR": "13cfabd5-f592-4354-a304-47098b765697"}


def psql(sql, db="dify"):
    p = subprocess.run(["docker", "exec", "-i", "docker-db_postgres-1", "psql", "-U", "postgres",
                        "-d", db, "-tA", "-c", sql], capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError("psql: " + (p.stderr or "")[:300])
    return p.stdout.strip()


def runs_in(app, t0, t1):
    raw = psql("select coalesce(json_agg(json_build_object('id',r.id,'status',r.status,"
               "'created_at',r.created_at::text,'elapsed',r.elapsed_time,"
               "'workflow_id',r.workflow_id,'workflow_version',w.version,"
               "'workflow_graph_md5',md5(w.graph)) order by r.created_at)::text,'[]') "
               "from workflow_runs r left join workflows w on w.id=r.workflow_id "
               "where r.app_id='%s' and r.created_at between timestamp '%s' "
               "and timestamp '%s';" % (app, t0, t1))
    return json.loads(raw or "[]")


def main():
    raw = json.load(io.open(os.path.join(EVDIR, "PPBS_B2_D3_RAW.json"), encoding="utf-8"))
    t0, t1 = raw["window_start"], raw["window_end"]
    pp = runs_in(PP_APP, t0, t1)
    seam = runs_in(SEAM_APP, t0, t1)
    cand = runs_in(CAND, t0, t1)
    others = {k: runs_in(v, t0, t1) for k, v in sorted(OTHER_FIVE.items())}

    md5s = sorted({r["workflow_graph_md5"] for r in pp})
    rep = {"document": {"id": "PPBS_B2_D3_BINDING_TRACE_v1.0",
                        "task_id": "DIYU-V1-PP-BOUNDARY-SUCCESSOR-001",
                        "model_calls": 0, "read_only": True},
           "window": {"start": t0, "end": t1},
           "chain": {"UAPP_candidate_canvas": cand, "SEAM": seam, "PUBLISHING_PACKAGING": pp},
           "pp_graph_md5_used": md5s,
           "pp_used_b2_only": md5s == [B2_MD5],
           "reference_md5": {"b2": B2_MD5, "b1": B1_MD5, "old_stable": STABLE_MD5},
           "other_five_capabilities": {k: {"runs": len(v), "detail": v}
                                       for k, v in others.items()},
           "other_five_zero_shadow_runs": all(len(v) == 0 for v in others.values()),
           "seam_graph_md5_now": psql("select md5(w.graph) from workflows w join apps a "
                                      "on a.workflow_id=w.id where a.id='%s';" % SEAM_APP),
           "provider_pin_now": psql("select version from tool_workflow_providers "
                                    "where name='diyu_m5fp_publishing_packaging';"),
           "provider_pinned_graph_md5_now": psql(
               "select md5(graph) from workflows where app_id='%s' and version="
               "(select version from tool_workflow_providers where "
               "name='diyu_m5fp_publishing_packaging');" % PP_APP)}
    io.open(os.path.join(EVDIR, "PPBS_B2_D3_BINDING_TRACE.json"), "w",
            encoding="utf-8").write(json.dumps(rep, ensure_ascii=False, indent=1) + "\n")
    print("窗口 %s → %s" % (t0, t1))
    print("UAPP 画布 run=%d  Seam run=%d  PP run=%d" % (len(cand), len(seam), len(pp)))
    for r in pp:
        print("   PP run %s %s ver=%s md5=%s" % (r["id"][:8], r["status"],
                                                 r["workflow_version"],
                                                 r["workflow_graph_md5"]))
    print("PP 本次只用 b2：", rep["pp_used_b2_only"])
    print("其余五能力零暗跑：", rep["other_five_zero_shadow_runs"],
          {k: len(v) for k, v in others.items()})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
