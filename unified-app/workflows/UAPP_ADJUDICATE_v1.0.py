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
    C("X-00", "全部轮次平台层返回 200",
      all(t["http_status"] == 200 for t in turns),
      [{"turn": t["turn_id"], "http": t["http_status"]} for t in turns])

    leaks = []
    for t in turns:
        d = node_out(t, "uapp_delivery") or {}
        leaks.append({"turn": t["turn_id"], "count": d.get("leak_hit_count"),
                      "hits": d.get("leak_hits_json")})
    counted = [l for l in leaks if l["count"] is not None]
    C("X-01", "用户可见输出零内部泄漏（机器可判部分）",
      bool(counted) and all(l["count"] == "0" for l in counted), leaks)

    failed_nodes = []
    for t in turns:
        for n in t.get("nodes_executed") or []:
            if n.get("status") not in ("succeeded", "retry", None):
                failed_nodes.append({"turn": t["turn_id"], "node": n["node_id"],
                                     "status": n["status"], "error": (n.get("error") or "")[:200]})
    C("X-02", "没有节点以失败态结束", not failed_nodes, failed_nodes)

    if case_id.startswith("UAPP-CAP-"):
        want = ev["frozen_criteria"]["expected_capability"]
        t = turns[0]
        r = node_out(t, "uapp_route") or {}
        got = r.get("target_capability")
        C("CAP-01", "路由到冻结判据预期的那一个能力", got == want,
          {"expected": want, "got": got, "route_note": r.get("route_note")})
        C("CAP-02", "统一能力接缝实际执行", executed(t, "uapp_seam"),
          {"seam_executed": executed(t, "uapp_seam")})
        d = node_out(t, "uapp_delivery") or {}
        mods = d.get("modules_actually_run") or "[]"
        others = [c for c in CAP6 if c != want and c in mods]
        C("CAP-03", "同一例里没有跑其余五个能力（无暗跑、无固定全链）",
          not others, {"modules_actually_run": mods, "other_capabilities_seen": others})

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
            pub = m2("select count(*) from publish_instances where is_test=true "
                     "and is_simulated=true;")
            realpub = m2("select count(*) from publish_instances where is_test=false "
                         "or is_simulated=false;")
            C("FULL-02", "测试发布已登记，且系统内不存在任何非测试发布",
              pub != "0" and realpub == "0",
              {"test_publish_rows": pub, "non_test_publish_rows": realpub})
        if len(turns) > 2:
            C("FULL-03", "反馈已按版本写回 M2",
              m2("select count(*) from feedback_records;") != "0",
              {"feedback_rows": m2("select count(*) from feedback_records;")})
        if len(turns) > 3:
            C("FULL-04", "出现下一个周期", None,
              {"cycle_rows_total": m2("select count(*) from cycles;"),
               "note": "需人工核对新周期属于本会话账号"})

    if case_id == "UAPP-WITHDRAW-01":
        wt = turns[-1]
        se = node_out(wt, "uapp_side") or {}
        txt = se.get("side_effect_text") or ""
        C("WD-01", "撤回把四件事分开说",
          all(k in txt for k in ("不再用于新的内容", "已经发出去的内容不受影响",
                                 "没有对平台做任何操作")),
          {"side_effect_text": txt})
        C("WD-02", "M2 中确实存在已撤回的素材行",
          m2("select count(*) from materials where withdrawn_at is not null;") != "0",
          {"withdrawn_rows": m2("select count(*) from materials "
                                "where withdrawn_at is not null;")})

    if case_id == "UAPP-RECOVERY-01":
        C("REC-01", "重复提交未产生第二行反馈（幂等）", None,
          {"note": "需与 FULL-01 提交前后的 feedback_records 行数对比",
           "feedback_rows_now": m2("select count(*) from feedback_records;")})

    bad = [c for c in checks if c["result"] == "FAIL"]
    human = [c for c in checks if c["result"] == "NEEDS_HUMAN"]
    verdict = "FAIL" if bad else ("NEEDS_HUMAN" if human else "PASS")
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
