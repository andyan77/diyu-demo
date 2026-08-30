#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Phase C 实际消耗核算｜零模型调用，只读线上执行记录与落盘证据。

登记冻结预算与实际的逐项对照：Dify workflow runs、nested app runs、
DeepSeek LLM 节点成功/失败尝试数、重试数、M2 写入、真实平台发布。
不判定通过与否，只报数。
"""
import glob
import io
import json
import os
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
UAPP = os.path.abspath(os.path.join(HERE, ".."))
# 证据目录、判据与产出路径可由环境变量切换，这样同一套核算口径可以复用到
# 后继的受影响连续链，而不是复制第二份统计逻辑（避免两套口径各算各的）。
EV = os.environ.get("COST_EV") or os.path.join(UAPP, "evidence", "stages", "s4_phase_c")
FREEZE = os.environ.get("COST_FREEZE") or os.path.join(
    UAPP, "stages", "S4_PHASE_C_POINT_VERIFICATION_FREEZE_v1.1.json")
OUT = os.environ.get("COST_OUT") or os.path.join(EV, "PHASE_C_COST_ACCOUNT.json")
CASE_GLOB = os.environ.get("COST_GLOB") or "S4-PC-*.json"

CANVAS = "85c01f85-a081-43e9-ab09-9993289cc200"
# 本任务的全部应用。计数必须按应用作用域，不能按时间窗口全实例统计——
# 同一个 Dify 实例里可能有别人的应用在并发跑，那不是本任务的消耗。
MY_APPS = [CANVAS,
           "a4c3b19b-243f-490b-9aca-3aa19767d6a5", "6c46fdb1-5f49-4513-a0c0-29957b3dcee4",
           "5fca0162-e26b-4545-a00b-66b1a2a2a077", "fd25ebfa-db67-40c3-82e5-202e1254facf",
           "1f9d65ea-8af5-45f0-a1d0-a80223d354e2", "b1dcf784-540e-4b3f-8ba2-3812f477f3ce",
           "44b55f9d-3792-40c3-b095-f2696464b4ec", "13cfabd5-f592-4354-a304-47098b765697",
           "c9cdea24-9df3-400b-9ecd-1d740e8c96df"]
IN_MINE = "app_id in (%s)" % ",".join("'%s'" % a for a in MY_APPS)
LLM_NODES = ("m1_chat_llm", "m1_shadow", "uapp_action", "m5_extract", "gate_repair_llm",
             "operating_one_account_llm", "skill_llm", "recovery_llm")


def psql(sql, db="dify"):
    p = subprocess.run(["docker", "exec", "-i", "docker-db_postgres-1", "psql", "-U", "postgres",
                        "-d", db, "-tA", "-c", sql], capture_output=True, text=True)
    if p.returncode:
        raise RuntimeError("psql: " + (p.stderr or "")[:300])
    return p.stdout.strip()


def main():
    fz = json.load(io.open(FREEZE, encoding="utf-8"))
    docs = []
    for p in sorted(glob.glob(os.path.join(EV, CASE_GLOB))):
        docs.append((os.path.basename(p)[:-5], json.load(io.open(p, encoding="utf-8"))))
    if not docs:
        raise SystemExit("无证据")

    w0 = min(d["window_start"] for _, d in docs)
    per, tot_llm_ok, tot_llm_fail, retries = {}, 0, 0, 0
    for name, d in docs:
        start = d["window_start"]
        later = sorted(x["window_start"] for _, x in docs if x["window_start"] > start)
        cond = "created_at > timestamp '%s'" % start
        if later:
            cond += " and created_at < timestamp '%s'" % later[0]
        rows = [r for r in psql(
            "select node_id||'~'||status from workflow_node_executions where %s and node_id in (%s);"
            % (cond + " and " + IN_MINE, ",".join("'%s'" % x for x in LLM_NODES))).splitlines() if r.strip()]
        ok = len([r for r in rows if r.endswith("~succeeded")])
        bad = len(rows) - ok
        runs = int(psql("select count(*) from workflow_runs where %s and %s;" % (cond, IN_MINE)) or 0)
        canvas_runs = int(psql("select count(*) from workflow_runs where %s and app_id='%s';"
                               % (cond, CANVAS)) or 0)
        per[name] = {"layer": d.get("layer"), "elapsed_seconds": d.get("elapsed_seconds"),
                     "http_status": d.get("http_status"), "attempts": d.get("attempts"),
                     "retries": d.get("attempts", 1) - 1,
                     "dify_workflow_runs_total": runs, "canvas_runs": canvas_runs,
                     "nested_app_runs": runs - canvas_runs,
                     "deepseek_llm_node_succeeded": ok, "deepseek_llm_node_failed": bad,
                     "llm_nodes": sorted(set(rows))}
        tot_llm_ok += ok
        tot_llm_fail += bad
        retries += d.get("attempts", 1) - 1

    total_runs = int(psql("select count(*) from workflow_runs where created_at > timestamp '%s' and %s;"
                          % (w0, IN_MINE)) or 0)
    canvas_total = int(psql("select count(*) from workflow_runs where created_at > timestamp '%s' "
                            "and app_id='%s';" % (w0, CANVAS)) or 0)
    m2 = {t: int(psql("select count(*) from %s where created_at > timestamp '%s';" % (t, w0),
                      db="diyu_business") or 0)
          for t in ("workspaces", "accounts", "cycles", "tasks", "task_snapshots",
                    "artifacts", "publish_instances")}
    dup = psql("select coalesce(json_agg(x)::text,'[]') from (select key, count(*) c from "
               "idempotency_records where created_at > timestamp '%s' group by key "
               "having count(*) > 1) x;" % w0, db="diyu_business")
    # 只数本任务上传的夹具：文件名与大小都对得上，排除同实例其它应用的上传
    uploads = int(psql("select count(*) from upload_files where created_at > timestamp '%s' "
                       "and name = '一页纸夹具品牌事实 v0.1.md' and size = 6119;" % w0) or 0)
    foreign = json.loads(psql("select coalesce(json_agg(json_build_object('app_id',w.app_id,"
                              "'name',coalesce(a.name,'?'),'runs',c))::text,'[]') from ("
                              "select w.app_id, count(*) c from workflow_runs w where "
                              "w.created_at > timestamp '%s' and not (%s) group by w.app_id) w "
                              "left join apps a on a.id=w.app_id;" % (w0, IN_MINE)) or "[]")

    budget = fz["cost_budget"]
    if "total" not in budget:   # 新 Gate 的预算是平铺的
        budget = {"total": {
            "dify_workflow_runs": budget.get("canvas_workflow_runs", 0)
                                  + budget.get("direct_capability_runs", 0),
            "nested_app_runs_max": budget.get("nested_app_runs_max"),
            "deepseek_llm_node_attempts_expected": budget.get("deepseek_llm_node_attempts_expected"),
            "deepseek_llm_node_attempts_max": budget.get("deepseek_llm_node_attempts_max")}}
    # C1 是对 Content Brief 应用的直调，属"我发起的顶层 run"，不是画布触发的嵌套 run。
    c1_direct = 1 if os.path.exists(os.path.join(EV, "S4-PC-C1.json")) else 0
    top_level = canvas_total + c1_direct
    rep = {"window_start": w0, "per_case": per,
           "actual_total": {"dify_workflow_runs_all_my_apps": total_runs,
                            "dify_workflow_runs": top_level,
                            "canvas_workflow_runs": canvas_total,
                            "direct_capability_runs": c1_direct,
                            "nested_app_runs": total_runs - top_level,
                            "deepseek_llm_node_succeeded": tot_llm_ok,
                            "deepseek_llm_node_failed": tot_llm_fail,
                            "retries": retries, "fixture_uploads": uploads},
           "frozen_budget": {"dify_workflow_runs": budget["total"]["dify_workflow_runs"],
                             "nested_app_runs_max": budget["total"]["nested_app_runs_max"],
                             "deepseek_llm_node_attempts_expected":
                                 budget["total"]["deepseek_llm_node_attempts_expected"],
                             "deepseek_llm_node_attempts_max":
                                 budget["total"]["deepseek_llm_node_attempts_max"]},
           "m2_rows_created_in_window": m2,
           "duplicate_idempotency_keys": json.loads(dup or "[]"),
           "concurrent_foreign_writers": foreign,
           "concurrent_foreign_writers": foreign,
           "real_platform_publish": {"publish_instances_created": m2["publish_instances"],
                                     "note": "0 即从未连接真实内容平台、从未发布"}}
    a, b = rep["actual_total"], rep["frozen_budget"]
    rep["within_budget"] = {
        "dify_workflow_runs": a["dify_workflow_runs"] <= b["dify_workflow_runs"],
        "nested_app_runs": a["nested_app_runs"] <= b["nested_app_runs_max"],
        "deepseek_llm_node_attempts": (a["deepseek_llm_node_succeeded"] +
                                       a["deepseek_llm_node_failed"]) <= b["deepseek_llm_node_attempts_max"]}
    io.open(OUT, "w", encoding="utf-8").write(json.dumps(rep, ensure_ascii=False, indent=1) + "\n")
    print(json.dumps({k: rep[k] for k in ("actual_total", "frozen_budget", "within_budget",
                                          "m2_rows_created_in_window",
                                          "duplicate_idempotency_keys",
                                          "concurrent_foreign_writers",
                                          "real_platform_publish")},
                     ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
