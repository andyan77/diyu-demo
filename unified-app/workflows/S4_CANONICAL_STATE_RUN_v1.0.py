#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""规范任务状态载体｜七轮真实连续链运行器。只发起、只记录，不判定。

判据 S4_CANONICAL_TASK_STATE_GATE_v1.0/v1.1 与 Candidate Manifest v1.0 在调用之前已冻结并提交；
本文件不读通过条件。一个全新会话、七个逐字冻结的用户输入、每个输入只跑一次。
预检是作用域隔离门，真正 fail-closed：第三方并发允许，
触碰候选图／九受保护应用／provider 钉／钉住代码／本任务 M2 作用域一律停止。
"""
import hashlib
import importlib.util
import io
import json
import os
import time

HERE = os.path.dirname(os.path.abspath(__file__))
UAPP = os.path.abspath(os.path.join(HERE, ".."))
REPO = os.path.abspath(os.path.join(UAPP, ".."))
GATE = os.path.join(UAPP, "stages", "S4_CANONICAL_TASK_STATE_GATE_v1.1.json")
MANIFEST = os.path.join(UAPP, "stages", "S4_CANONICAL_TASK_STATE_CANDIDATE_MANIFEST_v1.0.json")
INPUTS = os.path.join(UAPP, "stages", "S4_CANONICAL_TASK_STATE_INPUTS_v1.0.json")
EV = os.path.join(UAPP, "evidence", "stages", "s4_canonical_state", "run")

_s = importlib.util.spec_from_file_location("s42run", os.path.join(HERE, "S4_2_RUN_v1.0.py"))
R = importlib.util.module_from_spec(_s)
_s.loader.exec_module(R)
_s2 = importlib.util.spec_from_file_location("scope", os.path.join(HERE, "S4_SCOPE_ISOLATION_PREFLIGHT_v1.0.py"))
SC = importlib.util.module_from_spec(_s2)
_s2.loader.exec_module(SC)

PROTECTED = {"M1_HOST": "a4c3b19b-243f-490b-9aca-3aa19767d6a5",
             "HOP": "6c46fdb1-5f49-4513-a0c0-29957b3dcee4",
             "SEAM": "5fca0162-e26b-4545-a00b-66b1a2a2a077",
             "MATRIX": "fd25ebfa-db67-40c3-82e5-202e1254facf",
             "CAMPAIGN": "1f9d65ea-8af5-45f0-a1d0-a80223d354e2",
             "CONTENT_BRIEF": "b1dcf784-540e-4b3f-8ba2-3812f477f3ce",
             "CREATIVE_SCRIPT": "44b55f9d-3792-40c3-b095-f2696464b4ec",
             "PRODUCTION_DIRECTOR": "13cfabd5-f592-4354-a304-47098b765697",
             "PUBLISHING_PACKAGING": "c9cdea24-9df3-400b-9ecd-1d740e8c96df"}
TRANSIENT = ("Connection reset", "timed out", "timeout", "Bad Gateway", "502", "504",
             "Remote end closed")


def shaf(p):
    return hashlib.sha256(io.open(p, "rb").read()).hexdigest()


def sha(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def node_detail(rid):
    if not rid:
        return []
    raw = R.psql("select json_agg(json_build_object('idx',e.index,'node_id',e.node_id,"
                 "'title',e.title,'type',e.node_type,'status',e.status,'error',e.error,"
                 "'inputs',e.inputs,'outputs',e.outputs) order by e.index) "
                 "from workflow_node_executions e where e.workflow_run_id='%s';" % rid)
    try:
        return json.loads(raw or "[]") or []
    except Exception:
        return []


def conv_vars(cid):
    if not cid:
        return {}
    raw = R.psql("select json_agg(json_build_object('name', v.data::jsonb->>'name', "
                 "'len', length(coalesce(v.data::jsonb->>'value','')), "
                 "'head', left(coalesce(v.data::jsonb->>'value',''),400))) "
                 "from workflow_conversation_variables v where v.conversation_id='%s';" % cid)
    try:
        rows = json.loads(raw or "[]") or []
    except Exception:
        rows = []
    return {r["name"]: {"len": r["len"], "head": r["head"]} for r in rows}


def preflight(g):
    import subprocess
    porcelain = subprocess.run(["git", "-C", REPO, "status", "--porcelain"],
                               capture_output=True, text=True).stdout.splitlines()
    dirty = [l for l in porcelain
             if "unified-app/evidence/stages/s4_canonical_state" not in l
             and "unified-app/stages/S4_CANONICAL_TASK_STATE_RESULT_v1.0.json" not in l]
    if dirty:
        raise SystemExit("工作区不干净，冻结提交之外还有改动，拒绝执行：\n" + "\n".join(dirty))

    m = json.load(io.open(MANIFEST, encoding="utf-8"))
    if shaf(MANIFEST) != g["candidate_manifest"]["sha256"]:
        raise SystemExit("Candidate Manifest 已变动，拒绝执行")
    app = m["candidate_canvas"]["app_id"]
    snap = SC.snapshot(app, PROTECTED)
    if snap["candidate_graph_sha256"] != m["candidate_canvas"]["graph_sha256"]:
        raise SystemExit("候选图与冻结 Manifest 不一致，拒绝执行：%s" % snap["candidate_graph_sha256"])
    if snap["hop_pin"] != m["hop_provider"]["pinned_version"]:
        raise SystemExit("hop provider 钉已变动，拒绝执行：%s" % snap["hop_pin"])
    if snap["pinned_m5_compose_sha256"] != m["hop_provider"]["pinned_m5_compose_sha256"]:
        raise SystemExit("钉住那版的 m5_compose 已变动，拒绝执行")
    drift = {k: {"manifest": v, "now": snap["protected_md5"][k]}
             for k, v in m["protected_apps_graph_md5"].items() if snap["protected_md5"][k] != v}
    if drift:
        raise SystemExit("受保护应用漂移，拒绝执行：" + json.dumps(drift, ensure_ascii=False))
    fx_sha = shaf(R.FIXTURE)
    if fx_sha != g["fixture"]["sha256"]:
        raise SystemExit("夹具 hash 不一致，拒绝执行：%s" % fx_sha)
    print("PREFLIGHT ok | graph=%s | 节点%d边%d | pin=%s | 受保护面 %d/%d 一致 | 隔离门 fail-closed"
          % (snap["candidate_graph_sha256"][:16], m["candidate_canvas"]["node_count"],
             m["candidate_canvas"]["edge_count"], snap["hop_pin"],
             len(m["protected_apps_graph_md5"]), len(m["protected_apps_graph_md5"])))
    return snap, m


def main():
    g = json.load(io.open(GATE, encoding="utf-8"))
    plan = json.load(io.open(INPUTS, encoding="utf-8"))
    os.makedirs(EV, exist_ok=True)
    snap0, m = preflight(g)
    if shaf(INPUTS) != m["document"]["inputs_ref"]["sha256"]:
        raise SystemExit("冻结话术已变动，拒绝执行：%s" % shaf(INPUTS))
    if len(plan["conversation"]["turns"]) != m["run_binding"]["canvas_workflow_runs"]:
        raise SystemExit("轮次数与冻结预算不符，拒绝执行")
    t_all = R.psql("select now()::text;")

    app = m["candidate_canvas"]["app_id"]
    console = R.DC.Console(env=R.DC.load_env(R.ENV))
    key = console.app_api_key(app)
    user = "s4ct-" + time.strftime("%Y%m%d%H%M%S")
    conv = ""
    print("全新会话：end_user=%s" % user)
    fx, fx_sha = R.FIXTURE, shaf(R.FIXTURE)

    for t in plan["conversation"]["turns"]:
        cid = "S4-CT-T%d" % t["idx"]
        out = os.path.join(EV, cid + ".json")
        if os.path.exists(out):
            raise SystemExit("拒绝覆盖已有证据：" + out)

        st, b = R.upload(key, fx, user)
        fid = (b or {}).get("id")
        if st not in (200, 201) or not fid:
            raise SystemExit("夹具上传失败：%s %s" % (st, str(b)[:200]))
        files = [{"type": "document", "transfer_method": "local_file", "upload_file_id": fid}]

        t0 = R.psql("select now()::text;")
        print("[%s %s] %s" % (cid, t["expect_capability"], t["text"][:36]))
        attempts, res = 0, None
        while attempts < 2:
            attempts += 1
            tt = time.time()
            body = {"inputs": {}, "query": t["text"], "response_mode": "blocking",
                    "user": user, "files": files}
            if conv:
                body["conversation_id"] = conv
            r = R.DC.http_json("POST", "/v1/chat-messages",
                               headers={"Authorization": "Bearer " + key}, body=body, timeout=1800)
            try:
                bj = json.loads(r["body"])
            except Exception:
                bj = {"raw": r["body"][:4000]}
            res = {"http_status": r["status"], "elapsed_seconds": round(time.time() - tt, 2),
                   "body": bj}
            blob = json.dumps(bj, ensure_ascii=False)
            if not (r["status"] != 200 and any(x in blob for x in TRANSIENT)
                    and not bj.get("message_id")):
                break
            print("   纯传输失败且无模型输出，按纪律重试一次")

        bj = res["body"] or {}
        conv = bj.get("conversation_id") or conv
        mid = bj.get("message_id") or ""
        rid, nodes = R.trace(mid) if mid else ("", [])
        nested = {}
        for k, aid in R.APPS.items():
            rs = R.runs_since(aid, t0)
            item = {"app_id": aid, "runs_during_case": rs}
            if k == "SEAM" and rs:
                item["latest_run_nodes"] = R.nodes_of(rs[0]["id"])
                item["latest_run_detail"] = node_detail(rs[0]["id"])
            nested[k] = item

        doc = {"case_id": cid, "stage": "S4_CANONICAL_TASK_STATE", "turn_index": t["idx"],
               "expect_capability": t["expect_capability"], "with_fixture": True,
               "gate_sha256": shaf(GATE), "inputs_sha256": shaf(INPUTS),
               "graph_sha256_at_run": m["candidate_canvas"]["graph_sha256"],
               "manifest_sha256": shaf(MANIFEST),
               "app_id": app, "end_user": user, "query": t["text"],
               "uploaded_fixture": {"http_status": st, "file_id": fid, "sha256": fx_sha},
               "window_start": t0, "http_status": res["http_status"],
               "elapsed_seconds": res["elapsed_seconds"], "attempts": attempts,
               "message_id": mid, "workflow_run_id": rid, "conversation_id": conv,
               "answer": bj.get("answer") or "",
               "nodes_executed": [{"idx": n.get("idx"), "node_id": n.get("node_id"),
                                   "type": n.get("type"), "status": n.get("status"),
                                   "error": n.get("error")} for n in nodes],
               "node_detail": nodes, "nested_app_runs": nested,
               "conversation_variables_after_turn": conv_vars(conv),
               "note": "运行器只发起与记录，不判定。"}
        with io.open(out, "w", encoding="utf-8") as fh:
            fh.write(json.dumps(doc, ensure_ascii=False, indent=2) + "\n")

        bad, _ = SC.scope_intrusions(snap0, app, PROTECTED)
        if bad:
            io.open(os.path.join(EV, "SCOPE_INTRUSION.json"), "w", encoding="utf-8").write(
                json.dumps({"after_turn": t["idx"], "intrusions": bad}, ensure_ascii=False, indent=1))
            raise SystemExit("作用域隔离门触发，立即停止：" + json.dumps(bad, ensure_ascii=False))

        seam = [n["node_id"] for n in (nested.get("SEAM") or {}).get("latest_run_nodes") or []
                if n["node_id"].startswith("tool_")]
        nf = next((n for n in nodes if n.get("node_id") == "uapp_fields"), None)
        ns = next((n for n in nodes if n.get("node_id") == "uapp_state"), None)
        note = json.loads(nf["outputs"]).get("merge_note") if nf and nf.get("outputs") else ""
        lnote = json.loads(ns["outputs"]).get("ledger_note") if ns and ns.get("outputs") else ""
        print("   SAVED %s | http=%s %ss ans=%d | seam=%s\n     %s\n     %s"
              % (cid, res["http_status"], res["elapsed_seconds"],
                 len(bj.get("answer") or ""), seam, note, lnote))

    foreign = SC.foreign_activity(app, PROTECTED, t_all)
    io.open(os.path.join(EV, "RUN_META.json"), "w", encoding="utf-8").write(json.dumps(
        {"end_user": user, "conversation_id": conv, "window_start": t_all,
         "scope_snapshot_before": snap0,
         "scope_snapshot_after": SC.snapshot(app, PROTECTED),
         "concurrent_foreign_writers_disclosed_not_blocking": foreign},
        ensure_ascii=False, indent=1))
    print("\n第三方并发（只登记披露，不阻断）：%s" % json.dumps(foreign, ensure_ascii=False))


if __name__ == "__main__":
    main()
