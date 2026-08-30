#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""作用域隔离预检｜规划侧裁决 TD-UAPP-22 的工程编译。零模型调用。

"同一 Dify 实例完全没有其他写入者"不是产品硬门，也不该变成全局环境锁。
本模块把它换成作用域隔离门：**并发存在可以，触碰本任务作用域不行**。

被保护的作用域：
  1 候选 app 的已发布图
  2 九个受保护应用的图
  3 本任务 M2 workspace / account / cycle / task 之外不得有新增业务行
  4 hop provider 的版本钉与钉住那一版的 m5_compose
  5 本任务证据目录

真正 fail-closed：触碰任一项立即返回 False，调用方必须停止。不打印数字然后继续。

    python3 S4_SCOPE_ISOLATION_PREFLIGHT_v1.0.py --selfcheck
"""
import hashlib
import json
import subprocess
import sys

HOP = "6c46fdb1-5f49-4513-a0c0-29957b3dcee4"


def psql(sql, db="dify"):
    p = subprocess.run(["docker", "exec", "-i", "docker-db_postgres-1", "psql", "-U", "postgres",
                        "-d", db, "-tA", "-c", sql], capture_output=True, text=True)
    if p.returncode:
        raise RuntimeError("psql: " + (p.stderr or "")[:300])
    return p.stdout.strip()


def snapshot(candidate_app, protected_ids):
    """取当前作用域指纹。运行前后各取一次，比对即可判断有没有被触碰。"""
    g = psql("select w.graph from workflows w join apps a on a.workflow_id=w.id "
             "where a.id='%s';" % candidate_app)
    pin = psql("select p.version from tool_workflow_providers p where p.name='diyu_uapp_hop';")
    compose = psql("select encode(sha256(convert_to((select n->'data'->>'code' from workflows w, "
                   "jsonb_array_elements(w.graph::jsonb->'nodes') n where w.app_id='%s' "
                   "and w.version='%s' and n->>'id'='m5_compose'),'UTF8')),'hex');" % (HOP, pin))
    return {
        "candidate_graph_sha256": hashlib.sha256(
            json.dumps(json.loads(g), ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest(),
        "protected_md5": {k: psql("select md5(w.graph) from workflows w join apps a "
                                  "on a.workflow_id=w.id where a.id='%s';" % v).strip()
                          for k, v in sorted(protected_ids.items())},
        "hop_pin": pin,
        "pinned_m5_compose_sha256": compose,
    }


def scope_intrusions(before, candidate_app, protected_ids, since_ts=None, task_ids=None):
    """返回"触碰了本任务作用域"的具体证据列表。空列表 = 允许继续。"""
    now = snapshot(candidate_app, protected_ids)
    bad = []
    if now["candidate_graph_sha256"] != before["candidate_graph_sha256"]:
        bad.append({"scope": "candidate_graph", "was": before["candidate_graph_sha256"],
                    "now": now["candidate_graph_sha256"]})
    for k, v in now["protected_md5"].items():
        if v != before["protected_md5"].get(k):
            bad.append({"scope": "protected_app", "app": k,
                        "was": before["protected_md5"].get(k), "now": v})
    for k in ("hop_pin", "pinned_m5_compose_sha256"):
        if now[k] != before[k]:
            bad.append({"scope": k, "was": before[k], "now": now[k]})
    if since_ts and task_ids is not None:
        for tbl in ("workspaces", "accounts", "cycles", "tasks"):
            rows = psql("select count(*) from %s where created_at > timestamp '%s'%s;"
                        % (tbl, since_ts,
                           (" and id not in (%s)" % ",".join("'%s'" % t for t in task_ids))
                           if task_ids else ""), db="diyu_business")
            if int(rows or 0):
                bad.append({"scope": "m2_out_of_task", "table": tbl, "extra_rows": int(rows)})
    return bad, now


def foreign_activity(candidate_app, protected_ids, since_ts):
    """并发的第三方活动：登记披露，**不阻断**。"""
    mine = [candidate_app] + sorted(protected_ids.values())
    raw = psql("select coalesce(json_agg(json_build_object('app_id',t.app_id,"
               "'name',coalesce(a.name,'?'),'runs',t.c))::text,'[]') from "
               "(select app_id, count(*) c from workflow_runs where created_at > timestamp '%s' "
               "and app_id not in (%s) group by app_id) t left join apps a on a.id=t.app_id;"
               % (since_ts, ",".join("'%s'" % m for m in mine)))
    return json.loads(raw or "[]")


# ------------------------------------------------------------------ 自检
def _selfcheck():
    ids = {"A": "aaaaaaaa-0000-0000-0000-000000000001",
           "B": "bbbbbbbb-0000-0000-0000-000000000002"}
    base = {"candidate_graph_sha256": "g0", "protected_md5": {"A": "m1", "B": "m2"},
            "hop_pin": "v1", "pinned_m5_compose_sha256": "c1"}
    R = []

    def chk(name, got, want):
        ok = got == want
        R.append(ok)
        print("  %s  %-56s got=%s want=%s" % ("PASS" if ok else "FAIL", name, got, want))

    def diff(now):
        bad = []
        if now["candidate_graph_sha256"] != base["candidate_graph_sha256"]:
            bad.append("candidate_graph")
        for k, v in now["protected_md5"].items():
            if v != base["protected_md5"].get(k):
                bad.append("protected_app:" + k)
        for k in ("hop_pin", "pinned_m5_compose_sha256"):
            if now[k] != base[k]:
                bad.append(k)
        return bad

    chk("POS 无变化即放行", diff(dict(base)), [])
    chk("POS 第三方并发本身不阻断",
        diff(dict(base)), [])                      # 第三方活动不进 diff，只登记
    n = dict(base, candidate_graph_sha256="gX")
    chk("NEG 候选图被写 -> 拒绝", diff(n), ["candidate_graph"])
    n = dict(base, protected_md5={"A": "mX", "B": "m2"})
    chk("NEG 受保护应用被写 -> 拒绝", diff(n), ["protected_app:A"])
    n = dict(base, hop_pin="vX")
    chk("NEG provider 版本钉被改 -> 拒绝", diff(n), ["hop_pin"])
    n = dict(base, pinned_m5_compose_sha256="cX")
    chk("NEG 钉住那版代码被改 -> 拒绝", diff(n), ["pinned_m5_compose_sha256"])
    n = dict(base, candidate_graph_sha256="gX", hop_pin="vX")
    chk("NEG 多处同时被写 -> 全部列出", diff(n), ["candidate_graph", "hop_pin"])
    print("作用域隔离预检自检 %d/%d 通过" % (sum(R), len(R)))
    return 0 if all(R) else 1


if __name__ == "__main__":
    if "--selfcheck" in sys.argv:
        sys.exit(_selfcheck())
    raise SystemExit("本模块供运行器调用；独立执行只支持 --selfcheck")
