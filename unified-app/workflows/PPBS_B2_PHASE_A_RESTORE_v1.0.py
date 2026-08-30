#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PP 边界后继 b2｜Phase A 恢复安全发布指针。**零模型调用。**

task_id: DIYU-V1-PP-BOUNDARY-SUCCESSOR-001（REBASE，沿用同一 task_id）
authority: b2 最小修复与收口执行 Prompt 第三节

把 PP app 的**当前发布行为**恢复为旧稳定图（graph_md5 788c8555…，
源版本 2026-08-29 03:34:58.999575）。走 Dify 支持的 draft-sync + publish，
**不直接 UPDATE 数据库**；b1 历史行原样保留；provider 钉不动。

    python3 PPBS_B2_PHASE_A_RESTORE_v1.0.py --dry-run
    python3 PPBS_B2_PHASE_A_RESTORE_v1.0.py --apply
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
STABLE_VERSION = "2026-08-29 03:34:58.999575"
STABLE_MD5 = "788c8555aca09e6fa6d979f237f70157"
B1_VERSION = "2026-08-30 09:05:41.729617"
B1_MD5 = "7940dc009d0bba06e1b5ca99dac61e2e"
PIN_MUST_STAY = STABLE_VERSION
HOP_PIN_MUST_STAY = "2026-08-30 03:38:31.449618"
CAND = "85c01f85-a081-43e9-ab09-9993289cc200"
CAND_MD5_FROZEN = "99c3edf7bd12172a4fb011b588f25e57"
PROTECTED = {"M1_HOST": ("a4c3b19b-243f-490b-9aca-3aa19767d6a5", "cd93757bcf8ad322f3b32fc43b2da3ff"),
             "HOP": ("6c46fdb1-5f49-4513-a0c0-29957b3dcee4", "e38378c3c2a66b75aa7e645368c9e1ce"),
             "SEAM": ("5fca0162-e26b-4545-a00b-66b1a2a2a077", "db49a3da8973d4fdcbe9ecf63bdf7e2a"),
             "MATRIX": ("fd25ebfa-db67-40c3-82e5-202e1254facf", "6cdaeac9cacf69fbeea4bd25e1536ace"),
             "CAMPAIGN": ("1f9d65ea-8af5-45f0-a1d0-a80223d354e2", "4876dacc43a73741b41c5a3083796347"),
             "CONTENT_BRIEF": ("b1dcf784-540e-4b3f-8ba2-3812f477f3ce", "0c841642a71feedfb327ffb76aec0ddd"),
             "CREATIVE_SCRIPT": ("44b55f9d-3792-40c3-b095-f2696464b4ec", "a1cd859d5b88d0d025f336665ca94e51"),
             "PRODUCTION_DIRECTOR": ("13cfabd5-f592-4354-a304-47098b765697", "964e9a947dc9790d1de82496469689ad")}

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


def cur_md5(app):
    return psql("select md5(w.graph) from workflows w join apps a on a.workflow_id=w.id "
                "where a.id='%s';" % app)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    if not (a.dry_run or a.apply):
        raise SystemExit("必须显式选择 --dry-run 或 --apply")

    rows = json.loads(psql(
        "select coalesce(json_agg(json_build_object('id',id,'version',version,'md5',md5(graph),"
        "'marked_name',marked_name,'created_at',created_at::text) order by created_at)::text,'[]') "
        "from workflows where app_id='%s';" % PP_APP))
    before_cur = cur_md5(PP_APP)
    stable = [r for r in rows if r["version"] == STABLE_VERSION]
    b1 = [r for r in rows if r["version"] == B1_VERSION]
    if len(stable) != 1 or stable[0]["md5"] != STABLE_MD5:
        raise SystemExit("旧稳定版行不唯一或 md5 不符，拒绝操作：%s" % stable)
    if len(b1) != 1 or b1[0]["md5"] != B1_MD5:
        raise SystemExit("b1 历史行不唯一或 md5 不符，拒绝操作：%s" % b1)
    if before_cur != B1_MD5:
        raise SystemExit("当前发布图不是 b1，现场与预期不一致，停：%s" % before_cur)

    # 旧稳定图（只读取出，不改一个字节）
    stable_graph = json.loads(psql("select graph from workflows where id='%s';" % stable[0]["id"]))
    stable_features = json.loads(psql("select coalesce(features,'{}') from workflows where id='%s';"
                                      % stable[0]["id"]) or "{}")
    def _aslist(raw):
        """DB 里三行的 environment_variables / conversation_variables 都存成 `{}`（空对象），
        而 SyncDraftWorkflow 要求 list。空对象与空列表在语义上都是"没有变量"，
        转成 [] 不改变任何一个变量的取值；非空对象则拒绝猜测，直接抛错。"""
        v = json.loads(raw or "[]")
        if isinstance(v, list):
            return v
        if isinstance(v, dict) and not v:
            return []
        raise SystemExit("变量列不是空对象也不是列表，拒绝猜测：%r" % v)

    stable_envs = _aslist(psql("select coalesce(environment_variables,'[]') from workflows "
                               "where id='%s';" % stable[0]["id"]))
    stable_convs = _aslist(psql("select coalesce(conversation_variables,'[]') from workflows "
                                "where id='%s';" % stable[0]["id"]))

    console = DC.Console(env=DC.load_env(ENV))
    st, draft = console.call("GET", "/console/api/apps/%s/workflows/draft" % PP_APP, timeout=300)
    assert st == 200, ("draft get", st, str(draft)[:300])

    rep = {"document": {"id": "PPBS_B2_PHASE_A_RESTORE_v1.0",
                        "task_id": "DIYU-V1-PP-BOUNDARY-SUCCESSOR-001",
                        "task_mode": "REBASE",
                        "authority": "b2 最小修复与收口执行 Prompt 第三节 Phase A",
                        "model_calls": 0, "direct_db_updates": 0},
           "why": "隔离失败候选 b1：把 PP app 的当前发布行为恢复为旧稳定图。"
                  "这不构成 PP 产品验收 PASS。",
           "mechanism": "console draft-sync + publish（Dify 支持的重新发布机制），"
                        "不执行任何 UPDATE/DELETE 语句",
           "pp_workflow_rows_before": rows,
           "pp_current_graph_md5_before": before_cur,
           "restore_source_row": stable[0],
           "b1_row_preserved_expected": b1[0],
           "graph_to_publish_md5_local": hashlib.md5(
               psql("select graph from workflows where id='%s';" % stable[0]["id"]
                    ).encode("utf-8")).hexdigest(),
           "applied": False}

    if a.apply:
        st, res = console.call("POST", "/console/api/apps/%s/workflows/draft" % PP_APP, body={
            "graph": stable_graph, "features": stable_features,
            "hash": draft.get("hash"),
            "environment_variables": stable_envs,
            "conversation_variables": stable_convs}, timeout=900)
        assert st == 200, ("draft sync", st, str(res)[:400])
        st, pub = console.call("POST", "/console/api/apps/%s/workflows/publish" % PP_APP, body={
            "marked_name": "restore-stable",
            "marked_comment": "b2 Phase A：把当前发布行为恢复为 2026-08-29 03:34:58.999575 旧稳定图，"
                              "隔离失败候选 b1；b1 行保留"}, timeout=900)
        assert st in (200, 201), ("publish", st, str(pub)[:400])
        rep["applied"] = True
        rep["publish_status"] = st

    after_rows = json.loads(psql(
        "select coalesce(json_agg(json_build_object('id',id,'version',version,'md5',md5(graph),"
        "'marked_name',marked_name,'created_at',created_at::text) order by created_at)::text,'[]') "
        "from workflows where app_id='%s';" % PP_APP))
    now_protected = {k: cur_md5(v[0]) for k, v in sorted(PROTECTED.items())}
    rep["recompute_after"] = {
        "pp_current_graph_md5": cur_md5(PP_APP),
        "pp_current_graph_md5_equals_stable": cur_md5(PP_APP) == STABLE_MD5,
        "pp_current_version": psql("select w.version from workflows w join apps a "
                                   "on a.workflow_id=w.id where a.id='%s';" % PP_APP),
        "pp_workflow_rows_after": after_rows,
        "b1_row_still_present": any(r["version"] == B1_VERSION and r["md5"] == B1_MD5
                                    for r in after_rows),
        "old_stable_row_still_present": any(r["version"] == STABLE_VERSION
                                            and r["md5"] == STABLE_MD5 for r in after_rows),
        "pp_provider_pin": psql("select p.version from tool_workflow_providers p "
                                "where p.name='diyu_m5fp_publishing_packaging';"),
        "hop_pin": psql("select p.version from tool_workflow_providers p "
                        "where p.name='diyu_uapp_hop';"),
        "candidate_md5": cur_md5(CAND),
        "protected_md5_now": now_protected,
        "protected_drift": {k: {"frozen": PROTECTED[k][1], "now": v}
                            for k, v in now_protected.items() if v != PROTECTED[k][1]},
    }
    r = rep["recompute_after"]
    r["all_clear"] = bool(r["pp_current_graph_md5_equals_stable"] and r["b1_row_still_present"]
                          and r["old_stable_row_still_present"]
                          and r["pp_provider_pin"] == PIN_MUST_STAY
                          and r["hop_pin"] == HOP_PIN_MUST_STAY
                          and r["candidate_md5"] == CAND_MD5_FROZEN
                          and not r["protected_drift"])
    os.makedirs(EVDIR, exist_ok=True)
    io.open(os.path.join(EVDIR, "PPBS_B2_PHASE_A_RESTORE.json"), "w",
            encoding="utf-8").write(json.dumps(rep, ensure_ascii=False, indent=1) + "\n")
    print("发布图 %s → %s（=旧稳定 %s）" % (before_cur, r["pp_current_graph_md5"],
                                          r["pp_current_graph_md5_equals_stable"]))
    print("当前发布版本：%s" % r["pp_current_version"])
    print("b1 行保留=%s  旧稳定行保留=%s  workflow 行数=%d"
          % (r["b1_row_still_present"], r["old_stable_row_still_present"], len(after_rows)))
    print("provider 钉=%s  hop 钉=%s  候选图=%s" % (r["pp_provider_pin"], r["hop_pin"],
                                                   r["candidate_md5"]))
    print("受保护八应用漂移：%s" % (r["protected_drift"] or "无"))
    print("ALL CLEAR:", r["all_clear"])
    return 0 if r["all_clear"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
