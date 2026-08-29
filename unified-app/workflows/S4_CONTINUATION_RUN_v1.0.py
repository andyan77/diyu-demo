#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""S4 后继窄验证运行器｜素材来源裁决之后，同一会话能否继续跑完 CS→PD→PP。

只发起、只记录、不判定。判据是 S4_CONTENT_ORIGIN_CONTINUATION_GATE_v1.0.json，
在任何模型调用之前冻结并提交；本文件不读、也不改判据里的通过条件。

一个全新 conversation，六个逐字冻结的用户输入，每个输入只跑一次。
正例每一轮都附同一份夹具（上传是轮次作用域，见 S4_2_FAILURE_TRIAGE_003.md）。
"""
import hashlib
import importlib.util
import io
import json
import os
import time

HERE = os.path.dirname(os.path.abspath(__file__))
GATE = os.path.join(HERE, "..", "stages", "S4_CONTENT_ORIGIN_CONTINUATION_GATE_v1.0.json")
INPUTS = os.path.join(HERE, "..", "stages", "S4_CONTENT_ORIGIN_CONTINUATION_INPUTS_v1.0.json")
EV = os.path.join(HERE, "..", "evidence", "stages", "s4_continuation01")

spec = importlib.util.spec_from_file_location("s42run", os.path.join(HERE, "S4_2_RUN_v1.0.py"))
R = importlib.util.module_from_spec(spec)
spec.loader.exec_module(R)

APP = "85c01f85-a081-43e9-ab09-9993289cc200"


def sha(path):
    return hashlib.sha256(io.open(path, "rb").read()).hexdigest()


def live_graph_sha():
    g = json.loads(R.psql("select w.graph from workflows w join apps a on a.workflow_id=w.id "
                          "where a.id='%s';" % APP))
    return hashlib.sha256(json.dumps(g, ensure_ascii=False, sort_keys=True)
                          .encode("utf-8")).hexdigest()


def conv_vars(conversation_id):
    """跨轮状态载体的真源：workflow_conversation_variables。不认模型自述。"""
    if not conversation_id:
        return {}
    raw = R.psql("select json_agg(json_build_object('name',v.name,'len',length(v.data),"
                 "'head',left(v.data,240))) from workflow_conversation_variables v "
                 "where v.conversation_id='%s';" % conversation_id)
    try:
        rows = json.loads(raw or "[]") or []
    except Exception:
        rows = []
    return {r["name"]: {"len": r["len"], "head": r["head"]} for r in rows}


def chat(key, query, user, files, conv):
    body = {"inputs": {}, "query": query, "response_mode": "blocking", "user": user}
    if files:
        body["files"] = files
    if conv:
        body["conversation_id"] = conv
    t0 = time.time()
    r = R.DC.http_json("POST", "/v1/chat-messages",
                       headers={"Authorization": "Bearer " + key}, body=body, timeout=1800)
    try:
        b = json.loads(r["body"])
    except Exception:
        b = {"raw": r["body"][:4000]}
    return {"http_status": r["status"], "elapsed_seconds": round(time.time() - t0, 2), "body": b}


def main():
    if not os.path.exists(GATE) or not os.path.exists(INPUTS):
        raise SystemExit("判据或冻结输入缺失，拒绝执行")
    gate = json.load(io.open(GATE, encoding="utf-8"))
    plan = json.load(io.open(INPUTS, encoding="utf-8"))
    gate_sha, plan_sha = sha(GATE), sha(INPUTS)

    # 运行前把图身份钉死：本阶段禁止图变更。
    gsha = live_graph_sha()
    if gsha != gate["identity"]["graph_sha256"]:
        raise SystemExit("线上图与判据绑定的身份不一致，拒绝执行：%s" % gsha)

    fx = R.FIXTURE
    fx_sha = sha(fx)
    if fx_sha != gate["sufficiency_source"]["sha256"]:
        raise SystemExit("夹具与判据绑定的 hash 不一致，拒绝执行：%s" % fx_sha)

    console = R.DC.Console(env=R.DC.load_env(R.ENV))
    key = console.app_api_key(APP)

    os.makedirs(EV, exist_ok=True)
    # 全新 conversation：新的 end_user，绝不复用任何既往会话。
    user = "s4co-" + time.strftime("%Y%m%d%H%M%S")
    conv = ""
    print("end_user =", user)

    for t in plan["conversation"]["turns"]:
        cid = t["case_id"]
        out = os.path.join(EV, cid + ".json")
        if os.path.exists(out):
            raise SystemExit("拒绝覆盖已有证据：" + out)

        st, b = R.upload(key, fx, user)
        fid = (b or {}).get("id")
        if st not in (200, 201) or not fid:
            raise SystemExit("夹具上传失败：%s %s" % (st, str(b)[:200]))
        up = {"http_status": st, "file_id": fid, "name": os.path.basename(fx), "sha256": fx_sha}
        files = [{"type": "document", "transfer_method": "local_file", "upload_file_id": fid}]

        t_start = R.psql("select now()::text;")
        print("[T%d %s] %s" % (t["idx"], t["expect_capability"], t["text"][:40]))
        res = chat(key, t["text"], user, files, conv)
        body = res["body"] or {}
        conv = body.get("conversation_id") or conv
        ans = body.get("answer") or ""
        print("   http=%s %ss ans_len=%d" % (res["http_status"], res["elapsed_seconds"], len(ans)))

        mid = body.get("message_id") or ""
        rid, nodes = R.trace(mid) if mid else ("", [])
        nested = {}
        for k, aid in R.APPS.items():
            rs = R.runs_since(aid, t_start)
            item = {"app_id": aid, "runs_during_case": rs}
            if k == "SEAM" and rs:
                item["latest_run_nodes"] = R.nodes_of(rs[0]["id"])
            nested[k] = item

        doc = {"case_id": cid, "stage": "S4_CONTENT_ORIGIN_CONTINUATION",
               "turn_index": t["idx"], "expect_capability": t["expect_capability"],
               "with_fixture": True, "attempt": "s4_continuation01",
               "gate_sha256": gate_sha, "inputs_sha256": plan_sha,
               "graph_sha256_at_run": gsha, "app_id": APP, "end_user": user,
               "query": t["text"], "uploaded_fixture": up, "window_start": t_start,
               "http_status": res["http_status"], "elapsed_seconds": res["elapsed_seconds"],
               "attempts": 1, "message_id": mid, "workflow_run_id": rid,
               "conversation_id": conv, "answer": ans,
               "nodes_executed": [{"idx": n.get("idx"), "node_id": n.get("node_id"),
                                   "type": n.get("type"), "status": n.get("status"),
                                   "error": n.get("error")} for n in nodes],
               "node_detail": nodes, "nested_app_runs": nested,
               "conversation_variables_after_turn": conv_vars(conv),
               "note": "运行器只发起与记录，不判定。判定由 S4_CONTINUATION_ADJUDICATE 按冻结判据独立执行。"}
        with io.open(out, "w", encoding="utf-8") as fh:
            fh.write(json.dumps(doc, ensure_ascii=False, indent=2) + "\n")
        seam = [n["node_id"] for n in (nested.get("SEAM") or {}).get("latest_run_nodes") or []
                if n["node_id"].startswith("tool_")]
        print("   SAVED %s | seam=%s" % (cid, seam))


if __name__ == "__main__":
    main()
