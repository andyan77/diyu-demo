#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PP 边界后继 b2｜测试范围 provider 重钉。**零模型调用。**

授权条件（Gate v2.0 · test_scoped_publish_and_auto_revert）：
**仅在 D1 与 D2 都 PASS 之后、D3 之前**执行。本脚本自己复核该前置条件，
不成立即拒绝执行。

走 console `/console/api/workspaces/current/tool-provider/workflow/update`
把 provider 钉对齐到 PP app 的当前发布版本（= b2）。
**不执行任何 UPDATE / DELETE 语句。** Seam 图按 provider 名引用 PP，
不内嵌版本，重钉不改 Seam graph md5——脚本会复算证明这一点。

    python3 PPBS_B2_PROVIDER_REPIN_v1.0.py --dry-run
    python3 PPBS_B2_PROVIDER_REPIN_v1.0.py --apply
"""
import argparse
import importlib.util
import io
import json
import os
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
UAPP = os.path.abspath(os.path.join(HERE, ".."))
REPO = os.path.abspath(os.path.join(UAPP, ".."))
EVDIR = os.path.join(UAPP, "evidence", "stages", "pp_boundary_successor")
RESULT = os.path.join(UAPP, "stages", "PPBS_B2_PHASE_E_RESULT_v1.0.json")
ENV = "/home/faye/diyu-demo-worktrees/m3-account-content-operator-v1/.env"
PP_APP = "c9cdea24-9df3-400b-9ecd-1d740e8c96df"
PP_PROVIDER = "diyu_m5fp_publishing_packaging"
SEAM_APP = "5fca0162-e26b-4545-a00b-66b1a2a2a077"
SEAM_MD5_FROZEN = "db49a3da8973d4fdcbe9ecf63bdf7e2a"
STABLE_VERSION = "2026-08-29 03:34:58.999575"
B2_MD5 = "8366328bf827bd0f460455d750d45c4f"

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


def state():
    ver = psql("select version from tool_workflow_providers where name='%s';" % PP_PROVIDER)
    return {"provider_pinned_version": ver,
            "provider_pinned_graph_md5":
                psql("select md5(graph) from workflows where app_id='%s' and version='%s';"
                     % (PP_APP, ver)),
            "app_published_version":
                psql("select w.version from workflows w join apps a on a.workflow_id=w.id "
                     "where a.id='%s';" % PP_APP),
            "app_published_graph_md5":
                psql("select md5(w.graph) from workflows w join apps a on a.workflow_id=w.id "
                     "where a.id='%s';" % PP_APP),
            "seam_graph_md5":
                psql("select md5(w.graph) from workflows w join apps a on a.workflow_id=w.id "
                     "where a.id='%s';" % SEAM_APP)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    if not (a.dry_run or a.apply):
        raise SystemExit("必须显式选择 --dry-run 或 --apply")

    # 前置条件：D1 与 D2 都已判定 PASS
    res = json.load(io.open(RESULT, encoding="utf-8"))
    d1v, d2v = res["E1_D1"]["verdict"], res["E2_D2"]["verdict"]
    if not (d1v == "PASS" and d2v == "PASS"):
        raise SystemExit("前置条件不成立（D1=%s D2=%s），拒绝重钉" % (d1v, d2v))

    before = state()
    if before["app_published_graph_md5"] != B2_MD5:
        raise SystemExit("app 当前发布图不是 b2，拒绝重钉：%s"
                         % before["app_published_graph_md5"])
    if before["seam_graph_md5"] != SEAM_MD5_FROZEN:
        raise SystemExit("Seam 图已漂移，拒绝重钉：%s" % before["seam_graph_md5"])

    console = DC.Console(env=DC.load_env(ENV))
    st, tool = console.call("GET", "/console/api/workspaces/current/tool-provider/workflow/get"
                                   "?workflow_app_id=%s" % PP_APP, timeout=300)
    assert st == 200, ("get provider", st, str(tool)[:400])
    payload = {"workflow_tool_id": tool["workflow_tool_id"], "name": tool["name"],
               "label": tool["label"], "icon": tool["icon"],
               "description": tool["description"], "parameters": tool["parameters"],
               "privacy_policy": tool.get("privacy_policy") or "",
               "labels": [x["name"] if isinstance(x, dict) else x
                          for x in (tool.get("tool") or {}).get("labels", [])] or []}

    rep = {"document": {"id": "PPBS_B2_PROVIDER_REPIN_v1.0",
                        "task_id": "DIYU-V1-PP-BOUNDARY-SUCCESSOR-001",
                        "authority": "PPBS_GATE_v2.0.json · test_scoped_publish_and_auto_revert"
                                     " · provider_repin_condition",
                        "model_calls": 0, "direct_db_updates": 0},
           "precondition": {"D1": d1v, "D2": d2v, "satisfied": True},
           "scope": "测试范围重钉。D3 FAIL ⇒ 按冻结规则立即钉回旧稳定图。",
           "provider_id_from_api": tool["workflow_tool_id"],
           "fields_echoed_verbatim": sorted(k for k in payload if k != "workflow_tool_id"),
           "parameter_names": [p.get("name") for p in payload["parameters"]],
           "revert_target": {"version": STABLE_VERSION,
                             "graph_md5": "788c8555aca09e6fa6d979f237f70157"},
           "before": before, "applied": False}

    if a.apply:
        st, r = console.call("POST",
                             "/console/api/workspaces/current/tool-provider/workflow/update",
                             body=payload, timeout=300)
        assert st in (200, 201), ("update provider", st, str(r)[:400])
        rep["applied"] = True
        rep["update_status"] = st

    after = state()
    after["pin_matches_published"] = (after["provider_pinned_version"]
                                      == after["app_published_version"])
    after["pinned_graph_is_b2"] = after["provider_pinned_graph_md5"] == B2_MD5
    after["seam_graph_unchanged"] = after["seam_graph_md5"] == SEAM_MD5_FROZEN
    rep["after"] = after
    os.makedirs(EVDIR, exist_ok=True)
    io.open(os.path.join(EVDIR, "PPBS_B2_PROVIDER_REPIN.json"), "w",
            encoding="utf-8").write(json.dumps(rep, ensure_ascii=False, indent=1) + "\n")
    print("provider 钉：%s → %s" % (before["provider_pinned_version"],
                                    after["provider_pinned_version"]))
    print("钉住的图 md5：%s（= b2 %s）" % (after["provider_pinned_graph_md5"],
                                          after["pinned_graph_is_b2"]))
    print("Seam graph md5：%s（未变 %s）" % (after["seam_graph_md5"],
                                            after["seam_graph_unchanged"]))
    ok = after["pinned_graph_is_b2"] and after["seam_graph_unchanged"]
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
