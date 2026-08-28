#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""冻结 Candidate Run Manifest（Gate 2）。

**冻结是一次不可原地撤销的权威事件**，因此这里只做一件事：把「此刻现场的真实绑定」
一次性写进清单并把 status 置 FROZEN。写进去的每一个值都是**现场读出来的**，
不是从任何草稿里抄的。

拒绝冻结的条件（任何一条命中就不冻）：
  - git 工作树不干净 —— 冻结的必须是一棵确定的树；
  - Dify 有运行中的工作流 —— 现场还在变，读出来的哈希可能下一秒就不是它了；
  - 清单已经是 FROZEN —— 不允许原地改冻结件，要改就出新版本。
"""
import json, os, subprocess, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
MANIFEST = os.path.join(ROOT, "decision-chain", "docs",
                        "V1_M5_CANDIDATE_RUN_MANIFEST_v1.0.yaml")


def psql(db, q):
    p = subprocess.run(["docker", "exec", "-i", "docker-db_postgres-1", "psql", "-U", "postgres",
                        "-d", db, "-t", "-A", "-F", "|", "-c", q],
                       capture_output=True, text=True, timeout=90)
    return [l for l in (p.stdout or "").strip().splitlines() if l.strip()]


def sh(cmd):
    p = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    return (p.stdout or "").strip()


def main():
    import yaml
    m = yaml.safe_load(open(MANIFEST, encoding="utf-8"))

    if m.get("status") == "FROZEN":
        print("清单已是 FROZEN。冻结件不得原地修改；要改请出新版本。")
        return 2
    dirty = sh(["git", "status", "--porcelain"])
    if dirty:
        print("拒绝冻结：工作树不干净。冻结的必须是一棵确定的树。\n" + dirty[:600])
        return 2
    running = psql("dify", "SELECT count(*) FROM workflow_runs WHERE status='running';")
    if running and running[0] not in ("0", ""):
        print("拒绝冻结：Dify 当前有 %s 个运行中的工作流，现场还在变。" % running[0])
        return 2

    head = sh(["git", "rev-parse", "HEAD"])
    now = psql("dify", "SELECT to_char(now() AT TIME ZONE 'UTC','YYYY-MM-DD\"T\"HH24:MI:SS\"Z\"');")[0]

    # 现场读每一个已发布 graph 的 md5 与 marked_name
    rows = psql("dify", """
        SELECT a.id, md5(w.graph), coalesce(w.marked_name,''), w.created_at
        FROM apps a JOIN workflows w ON w.app_id=a.id
        WHERE w.version<>'draft'
          AND w.created_at=(SELECT max(created_at) FROM workflows w2
                            WHERE w2.app_id=a.id AND w2.version<>'draft');""")
    live = {}
    for r in rows:
        parts = r.split("|")
        if len(parts) >= 4:
            live[parts[0]] = {"graph_md5": parts[1], "marked_name": parts[2],
                              "published_at": parts[3]}

    changed = []
    for a in (m.get("dify") or {}).get("apps") or []:
        aid = a.get("app_id")
        if aid in live:
            if a.get("graph_md5") in (None, "PENDING_FREEZE"):
                a["graph_md5"] = live[aid]["graph_md5"]
                a["published_at"] = live[aid]["published_at"]
                if live[aid]["marked_name"]:
                    a["marked_name"] = live[aid]["marked_name"]
                changed.append(("填入", a.get("role")))
            elif a["graph_md5"] != live[aid]["graph_md5"]:
                a["graph_md5_at_draft"] = a["graph_md5"]
                a["graph_md5"] = live[aid]["graph_md5"]
                a["published_at"] = live[aid]["published_at"]
                if live[aid]["marked_name"]:
                    a["marked_name"] = live[aid]["marked_name"]
                changed.append(("现场已变，按现场为准", a.get("role")))

    # A/B 基线应用：跑过 A/B 之后才存在，存在就一并登记
    names = psql("dify", "SELECT id, name FROM apps WHERE name LIKE 'DIYU M5 AB%%' "
                         "OR name LIKE 'DIYU M5 PROBE%%';")
    known = {a.get("app_id") for a in (m.get("dify") or {}).get("apps") or []}
    for r in names:
        aid, nm = r.split("|", 1)
        if aid in known or aid not in live:
            continue
        m["dify"]["apps"].append({
            "role": "M5 新建 · " + nm, "app_id": aid,
            "graph_md5": live[aid]["graph_md5"],
            "marked_name": live[aid]["marked_name"],
            "published_at": live[aid]["published_at"],
            "protected": False,
            "note": "A/B 对照基线或可用性探针；不参与产品能力，只用于取证"})
        changed.append(("新登记", nm))

    m["git"]["candidate_commit"] = head
    m["frozen_at"] = now
    m["status"] = "FROZEN"
    m["freeze_preconditions_verified"] = {
        "worktree_clean": True,
        "no_running_dify_workflows": True,
        "graph_hashes_read_live_at_freeze": True,
    }

    with open(MANIFEST, "w", encoding="utf-8") as f:
        yaml.safe_dump(m, f, allow_unicode=True, sort_keys=False, width=100)
    print("已冻结。")
    print("  candidate_commit =", head)
    print("  frozen_at        =", now)
    for what, who in changed:
        print("  %-16s %s" % (what, who))
    return 0


if __name__ == "__main__":
    sys.exit(main())
