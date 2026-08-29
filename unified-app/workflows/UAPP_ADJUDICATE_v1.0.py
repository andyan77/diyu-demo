#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""按**冻结判据**裁定正式证据。只读证据与数据库，不重跑任何东西。

纪律：
  · 只认可复算的东西——Dify 节点执行记录、节点输出、M2 数据行。模型自述不算证据。
  · 判据哈希必须与证据里记的那一份一致；不一致就整份置 STALE，不硬判。
  · 机器判不了的留 NEEDS_HUMAN，**不猜、不填成 PASS**。
"""
import hashlib
import io
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
EV = os.path.join(HERE, "..", "evidence", "formal")
DOCS = os.path.join(HERE, "..", "docs")
SCEN = os.path.join(DOCS, "UAPP_FROZEN_SCENARIOS_v1.0.json")

CAP6 = ["MATRIX", "CAMPAIGN", "CONTENT_BRIEF", "CREATIVE_SCRIPT",
        "PRODUCTION_DIRECTOR", "PUBLISHING_PACKAGING"]


def m2(sql):
    p = subprocess.run(["docker", "exec", "-i", "docker-db_postgres-1", "psql", "-U", "postgres",
                        "-d", "diyu_business", "-tA", "-c", sql], capture_output=True, text=True)
    return p.stdout.strip()


def node_out(turn, node_id):
    for n in turn.get("node_detail") or []:
        if n.get("node_id") == node_id:
            o = n.get("outputs")
            if isinstance(o, str):
                try:
                    return json.loads(o)
                except Exception:
                    return {}
            return o or {}
    return None


def executed(turn, node_id):
    return any(n.get("node_id") == node_id for n in turn.get("nodes_executed") or [])


# M5 运行时的同一份传输层故障标记，抄过来不改口径。
_TRANSPORT = ("Server Unavailable", "SSLEOF", "UNEXPECTED_EOF", "Max retries exceeded",
              "Connection aborted", "Read timed out", "Remote end closed", "Bad gateway",
              "502", "503", "504", "HTTPSConnectionPool")


def _is_transport(err):
    e = err or ""
    return any(t in e for t in _TRANSPORT)


def _scrubber():
    """用**已发布图里那一份**投影节点源码的清洗函数来扫，判据与运行时同源。"""
    g = json.loads(subprocess.run(
        ["docker", "exec", "-i", "docker-db_postgres-1", "psql", "-U", "postgres", "-d", "dify",
         "-tA", "-c", "select w.graph from workflows w join apps a on a.workflow_id=w.id "
         "where a.id='2448e4f9-818f-4b88-9311-d18546e97da9';"],
        capture_output=True, text=True).stdout)
    src = [n for n in g["nodes"] if n["id"] == "uapp_delivery"][0]["data"]["code"]
    ns = {}
    exec(compile(src, "<delivery>", "exec"), ns)
    return ns["_scrub"]


def adjudicate(case_id):
    path = os.path.join(EV, "%s.json" % case_id)
    if not os.path.exists(path):
        return {"case_id": case_id, "verdict": "NOT_VERIFIED",
                "reason": "ABSENT：没有这一例的正式证据"}
    ev = json.load(io.open(path, encoding="utf-8"))

    frozen_sha = hashlib.sha256(io.open(SCEN, "rb").read()).hexdigest()
    if ev["frozen_criteria"]["sha256"] != frozen_sha:
        return {"case_id": case_id, "verdict": "NOT_VERIFIED", "freshness": "STALE",
                "reason": "证据绑定的判据哈希与当前判据文件不一致，需定向复验",
                "evidence_bound": ev["frozen_criteria"]["sha256"], "current": frozen_sha}

    checks = []

    def C(cid, desc, ok, detail):
        checks.append({"id": cid, "desc": desc,
                       "result": "PASS" if ok is True else ("FAIL" if ok is False
                                                            else "NEEDS_HUMAN"),
                       "detail": detail})

    turns = ev["turns"]

    # 本例自己的测试工作区。**所有 M2 行数判定都必须限定在这个 workspace 内**——
    # 库里有 1568 条 M0-M5 时期留下的非测试发布行，那是别的任务的数据，
    # 拿全库计数来判本例，等于用别人的数据给本例定罪或脱罪。
    # 这是修检查器的实现口径，不是改冻结判据：判据说的一直是"本例登记的发布记录"。
    conv = (ev.get("conversation_id") or "")
    tag = "".join(ch for ch in conv if ch.isalnum())[:12]
    ws = m2("select id from workspaces where name='ws-uapp-%s';" % tag) if tag else ""
    ws_scope = ("'%s'" % ws) if ws else "'00000000-0000-0000-0000-000000000000'"
    C("X-00", "全部轮次平台层返回 200",
      all(t["http_status"] == 200 for t in turns),
      [{"turn": t["turn_id"], "http": t["http_status"]} for t in turns])

    # 直接扫**真正回给用户的那段文本**，而不是只信投影节点的自述计数。
    # 组件失败走 fail-branch 时根本没有 uapp_delivery 输出，只看计数会把
    # 「没测到」当成「没泄漏」——那是把未验证填成通过。
    scrub = _scrubber()
    leaks = []
    for t in turns:
        d = node_out(t, "uapp_delivery") or {}
        ans = t.get("answer") or ""
        _, hits = scrub(ans) if ans else ("", [])
        leaks.append({"turn": t["turn_id"], "node_reported_count": d.get("leak_hit_count"),
                      "answer_scanned_hits": hits, "answer_len": len(ans)})
    C("X-01", "回给用户的正文经同一套判据扫描后零命中",
      all(not l["answer_scanned_hits"] for l in leaks) and any(l["answer_len"] for l in leaks),
      leaks)

    failed_nodes, transport_failures = [], []
    for t in turns:
        for n in t.get("nodes_executed") or []:
            if n.get("status") not in ("succeeded", "retry", None):
                row = {"turn": t["turn_id"], "node": n["node_id"], "status": n["status"],
                       "error": (n.get("error") or "")[:300]}
                (transport_failures if _is_transport(n.get("error")) else failed_nodes).append(row)
    C("X-02", "没有节点因业务原因失败", not failed_nodes, failed_nodes)
    if transport_failures:
        C("X-03", "存在纯传输层失败：按冻结取样规则允许重试一次，本 Attempt 如实保留",
          None, transport_failures)

    if case_id.startswith("UAPP-CAP-"):
        want = ev["frozen_criteria"]["expected_capability"]
        t = turns[0]
        r = node_out(t, "uapp_route") or {}
        got = r.get("target_capability")
        C("CAP-01", "路由到冻结判据预期的那一个能力", got == want,
          {"expected": want, "got": got, "route_note": r.get("route_note")})
        # 上游有纯传输层故障时，接缝没跑是**故障传播的后果**，不是被测对象的业务失败。
        # 把它判成 FAIL 等于把环境故障算到系统头上（A3：不多算）。判为未验证，按规则补 Attempt。
        up_transport = any(_is_transport(n.get("error"))
                           for n in (t.get("nodes_executed") or []))
        C("CAP-02", "统一能力接缝实际执行",
          True if executed(t, "uapp_seam") else (None if up_transport else False),
          {"seam_executed": executed(t, "uapp_seam"),
           "upstream_transport_failure": up_transport})
        d = node_out(t, "uapp_delivery") or {}
        mods = d.get("modules_actually_run") or "[]"
        others = [c for c in CAP6 if c != want and c in mods]
        C("CAP-03", "同一例里没有跑其余五个能力（无暗跑、无固定全链）",
          (not others) if (mods and mods != "[]") else None,
          {"modules_actually_run": mods, "other_capabilities_seen": others,
           "note": "" if (mods and mods != "[]") else "本轮没有投影输出，无法评判，不填成通过"})

    if case_id == "UAPP-FULL-01":
        t1 = turns[0]
        wb = node_out(t1, "uapp_wb_prep") or {}
        ch = wb.get("content_hash") or ""
        C("FULL-01", "T1 真实交付且产物被登记进 M2",
          wb.get("should_persist_artifact") == "true" and bool(ch)
          and m2("select count(*) from artifacts where content_hash='%s';" % ch) == "1",
          {"should_persist": wb.get("should_persist_artifact"), "content_hash": ch[:16],
           "artifact_rows": m2("select count(*) from artifacts where content_hash='%s';" % ch),
           "version_rows": m2("select count(*) from content_versions "
                              "where content_hash='%s';" % ch)})
        if len(turns) > 1:
            pub = m2("select count(*) from publish_instances where workspace_id=%s "
                     "and is_test=true and is_simulated=true;" % ws_scope)
            realpub = m2("select count(*) from publish_instances where workspace_id=%s "
                         "and (is_test=false or is_simulated=false);" % ws_scope)
            C("FULL-02", "本例登记了测试发布，且本例工作区内没有任何非测试发布",
              pub != "0" and realpub == "0",
              {"workspace_id": ws, "test_publish_rows": pub,
               "non_test_publish_rows_in_this_workspace": realpub,
               "note": "限定本例工作区；库内其余非测试行属 M0-M5 既有数据，与本例无关"})
        if len(turns) > 2:
            fb = m2("select count(*) from feedback_records where workspace_id=%s;" % ws_scope)
            C("FULL-03", "本例的反馈已写回 M2", fb != "0",
              {"workspace_id": ws, "feedback_rows_in_this_workspace": fb})
        if len(turns) > 3:
            cyc = m2("select count(*) from cycles where workspace_id=%s;" % ws_scope)
            C("FULL-04", "本例工作区内出现了第二个周期（下一个周期已开）",
              cyc.isdigit() and int(cyc) >= 2,
              {"workspace_id": ws, "cycle_rows_in_this_workspace": cyc,
               "note": "建域时建了第 1 个周期；T4 之后应当出现第 2 个"})

    if case_id == "UAPP-WITHDRAW-01":
        wt = turns[-1]
        se = node_out(wt, "uapp_side") or {}
        txt = se.get("side_effect_text") or ""
        C("WD-01", "撤回把四件事分开说",
          all(k in txt for k in ("不再用于新的内容", "已经发出去的内容不受影响",
                                 "没有对平台做任何操作")),
          {"side_effect_text": txt})
        wd = m2("select count(*) from materials where workspace_id=%s "
                "and withdrawn_at is not null;" % ws_scope)
        C("WD-02", "本例工作区内确实存在已撤回的素材行", wd != "0",
          {"workspace_id": ws, "withdrawn_rows_in_this_workspace": wd,
           "note": "限定本例工作区；库内其余撤回行属既有数据"})

    if case_id == "UAPP-RECOVERY-01":
        keys = m2("select idempotency_key, count(*) from feedback_records "
                  "where workspace_id=%s group by idempotency_key;" % ws_scope)
        dup = [l for l in keys.splitlines() if l.strip() and not l.strip().endswith("|1")]
        C("REC-01", "同一幂等键没有产生第二行反馈", not dup,
          {"workspace_id": ws, "feedback_key_counts": keys.splitlines(), "duplicates": dup})

    bad = [c for c in checks if c["result"] == "FAIL"]
    human = [c for c in checks if c["result"] == "NEEDS_HUMAN"]
    transport_only = (not bad) and any(c["id"] == "X-03" for c in checks)
    if bad:
        verdict = "FAIL"
    elif transport_only:
        # 传输层挂掉不是被测对象的业务失败，但也**不能算通过**。
        # 如实报未验证并说明可按冻结规则补一次 Attempt。
        verdict = "NOT_VERIFIED"
    elif human:
        verdict = "NEEDS_HUMAN"
    else:
        verdict = "PASS"
    return {"case_id": case_id, "verdict": verdict, "freshness": "CURRENT",
            "frozen_criteria_sha256": frozen_sha, "checks": checks,
            "conversation_id": ev.get("conversation_id"), "turns": len(turns)}


def main():
    ids = sys.argv[1:] or sorted(
        f[:-5] for f in os.listdir(EV) if f.endswith(".json"))
    out = [adjudicate(i) for i in ids]
    for r in out:
        print("%-18s %s" % (r["case_id"], r["verdict"]))
        for c in r.get("checks", []):
            if c["result"] != "PASS":
                print("     %-8s %-14s %s" % (c["id"], c["result"], c["desc"]))
    p = os.path.join(HERE, "..", "evidence", "UAPP_ADJUDICATION.json")
    with io.open(p, "w", encoding="utf-8") as fh:
        fh.write(json.dumps(out, ensure_ascii=False, indent=2) + "\n")
    print("SAVED", p)


if __name__ == "__main__":
    main()
