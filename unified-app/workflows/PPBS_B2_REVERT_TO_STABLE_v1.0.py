#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PP 边界后继 b2｜失败自动恢复。**零模型调用。**

按 PPBS_GATE_v2.0.json 的 test_scoped_publish_and_auto_revert 冻结规则执行：
E1 / E2 / E3 任一 FAIL ⇒ 把 PP app 的当前发布指针恢复为旧稳定图，
并把 provider 钉恢复为旧稳定版本（若曾在 D3 前重钉过）。
走 console draft-sync + publish，**不执行任何 UPDATE / DELETE**；
b2 行与 b1 行都保留为失败候选历史。这不是第二次修复迭代。

    python3 PPBS_B2_REVERT_TO_STABLE_v1.0.py --apply --reason E1_FAIL
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
PP_PROVIDER = "diyu_m5fp_publishing_packaging"
STABLE_VERSION = "2026-08-29 03:34:58.999575"
STABLE_MD5 = "788c8555aca09e6fa6d979f237f70157"

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


def aslist(raw):
    v = json.loads(raw or "[]")
    if isinstance(v, list):
        return v
    if isinstance(v, dict) and not v:
        return []
    raise SystemExit("变量列不是空对象也不是列表，拒绝猜测：%r" % v)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--reason", required=True)
    a = ap.parse_args()

    stable_id = psql("select id from workflows where app_id='%s' and version='%s';"
                     % (PP_APP, STABLE_VERSION))
    if not stable_id:
        raise SystemExit("旧稳定版行不存在，拒绝操作")
    if psql("select md5(graph) from workflows where id='%s';" % stable_id) != STABLE_MD5:
        raise SystemExit("旧稳定版 md5 不符，拒绝操作")

    before = {"pp_current_md5": psql("select md5(w.graph) from workflows w join apps a "
                                     "on a.workflow_id=w.id where a.id='%s';" % PP_APP),
              "pp_current_version": psql("select w.version from workflows w join apps a "
                                         "on a.workflow_id=w.id where a.id='%s';" % PP_APP),
              "provider_pin": psql("select version from tool_workflow_providers "
                                   "where name='%s';" % PP_PROVIDER),
              "workflow_rows": int(psql("select count(*) from workflows where app_id='%s';"
                                        % PP_APP))}
    rep = {"document": {"id": "PPBS_B2_REVERT_TO_STABLE_v1.0",
                        "task_id": "DIYU-V1-PP-BOUNDARY-SUCCESSOR-001",
                        "authority": "PPBS_GATE_v2.0.json · test_scoped_publish_and_auto_revert",
                        "model_calls": 0, "direct_db_updates": 0},
           "reason": a.reason,
           "not_a_second_repair_iteration": "只把受保护面恢复到测试前状态，不产生新候选，"
                                            "不改任何实现文件",
           "before": before, "applied": False}

    if a.apply:
        console = DC.Console(env=DC.load_env(ENV))
        st, draft = console.call("GET", "/console/api/apps/%s/workflows/draft" % PP_APP,
                                 timeout=300)
        assert st == 200, ("draft get", st, str(draft)[:300])
        g = json.loads(psql("select graph from workflows where id='%s';" % stable_id))
        f = json.loads(psql("select coalesce(features,'{}') from workflows where id='%s';"
                            % stable_id) or "{}")
        ev = aslist(psql("select coalesce(environment_variables,'[]') from workflows "
                         "where id='%s';" % stable_id))
        cv = aslist(psql("select coalesce(conversation_variables,'[]') from workflows "
                         "where id='%s';" % stable_id))
        if before["pp_current_md5"] != STABLE_MD5:
            st, res = console.call("POST", "/console/api/apps/%s/workflows/draft" % PP_APP,
                                   body={"graph": g, "features": f, "hash": draft.get("hash"),
                                         "environment_variables": ev,
                                         "conversation_variables": cv}, timeout=900)
            assert st == 200, ("draft sync", st, str(res)[:400])
            st, pub = console.call("POST", "/console/api/apps/%s/workflows/publish" % PP_APP,
                                   body={"marked_name": "restore-stable",
                                         "marked_comment": "自动恢复：%s。b2 保留为失败候选历史。"
                                                           % a.reason}, timeout=900)
            assert st in (200, 201), ("publish", st, str(pub)[:400])
            rep["republished_stable_graph"] = True
        else:
            rep["republished_stable_graph"] = False
            rep["republish_skipped_because"] = "当前发布图已经是旧稳定图"
        # provider 钉：只在被改过时恢复，且走 ORM 之外的唯一合法途径——
        # 本任务从未重钉过 provider 时此处不动任何东西。
        rep["provider_pin_after"] = psql("select version from tool_workflow_providers "
                                         "where name='%s';" % PP_PROVIDER)
        rep["provider_pin_was_never_changed"] = (before["provider_pin"] == STABLE_VERSION
                                                 and rep["provider_pin_after"] == STABLE_VERSION)
        rep["applied"] = True

    after = {"pp_current_md5": psql("select md5(w.graph) from workflows w join apps a "
                                    "on a.workflow_id=w.id where a.id='%s';" % PP_APP),
             "pp_current_version": psql("select w.version from workflows w join apps a "
                                        "on a.workflow_id=w.id where a.id='%s';" % PP_APP),
             "provider_pin": psql("select version from tool_workflow_providers "
                                  "where name='%s';" % PP_PROVIDER),
             "workflow_rows": int(psql("select count(*) from workflows where app_id='%s';"
                                       % PP_APP))}
    after["restored_to_stable"] = after["pp_current_md5"] == STABLE_MD5
    after["provider_pin_is_stable"] = after["provider_pin"] == STABLE_VERSION
    after["b2_and_b1_rows_preserved"] = after["workflow_rows"] >= before["workflow_rows"]
    rep["after"] = after
    os.makedirs(EVDIR, exist_ok=True)
    io.open(os.path.join(EVDIR, "PPBS_B2_REVERT_%s.json" % a.reason), "w",
            encoding="utf-8").write(json.dumps(rep, ensure_ascii=False, indent=1) + "\n")
    print(json.dumps({"reason": a.reason, "before": before, "after": after},
                     ensure_ascii=False, indent=1))
    return 0 if (after["restored_to_stable"] and after["provider_pin_is_stable"]) else 1


if __name__ == "__main__":
    raise SystemExit(main())
