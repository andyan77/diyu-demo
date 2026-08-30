#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Phase C 运行器｜只发起、只记录，不判定。

判据在 S4_PHASE_C_POINT_VERIFICATION_FREEZE_v1.0.json，调用之前已冻结并提交；
本文件不读通过条件，也不产生任何 PASS/FAIL 结论。

三层严格串行，层间硬停：C2 只有在判定书里 C1=PASS 时才允许发起，C3 同理。
运行器判断的不是"这一层好不好"，只是"上一层的判定书说没说 PASS"——判定由判定器做。

用法：
    python3 S4_PHASE_C_RUN_v1.0.py --layer C1
    python3 S4_PHASE_C_RUN_v1.0.py --layer C2
    python3 S4_PHASE_C_RUN_v1.0.py --layer C3
"""
import argparse
import hashlib
import importlib.util
import io
import json
import os
import subprocess
import time

HERE = os.path.dirname(os.path.abspath(__file__))
UAPP = os.path.abspath(os.path.join(HERE, ".."))
REPO = os.path.abspath(os.path.join(UAPP, ".."))
STAGES = os.path.join(UAPP, "stages")
FREEZE = os.path.join(STAGES, "S4_PHASE_C_POINT_VERIFICATION_FREEZE_v1.0.json")
BINDING = os.path.join(STAGES, "S4_PHASE_C_BINDING_v1.0.json")
C1_INPUT = os.path.join(STAGES, "S4_PHASE_C_C1_INPUT_v1.0.json")
CONT_INPUTS = os.path.join(STAGES, "S4_CONTENT_ORIGIN_CONTINUATION_INPUTS_v1.0.json")
RESULT = os.path.join(STAGES, "S4_PHASE_C_RESULT_v1.0.json")
EV = os.path.join(UAPP, "evidence", "stages", "s4_phase_c")
CONV = os.path.join(EV, "CONVERSATION.json")

_s = importlib.util.spec_from_file_location("s42run", os.path.join(HERE, "S4_2_RUN_v1.0.py"))
R = importlib.util.module_from_spec(_s)
_s.loader.exec_module(R)

TRANSIENT = ("Connection reset", "timed out", "timeout", "Bad Gateway", "502", "504",
             "Remote end closed")


def sha_file(p):
    return hashlib.sha256(io.open(p, "rb").read()).hexdigest()


def sha(s):
    return hashlib.sha256(s.encode("utf-8") if isinstance(s, str) else s).hexdigest()


def git(*a):
    return subprocess.run(["git", "-C", REPO] + list(a), capture_output=True, text=True).stdout.strip()


# ---------------------------------------------------------------- 调用前复核
def preflight(fz, layer):
    b = json.load(io.open(BINDING, encoding="utf-8"))
    if sha_file(BINDING) != fz["binding"]["sha256"]:
        raise SystemExit("绑定文件已变动，拒绝执行")

    # 冻结提交之后，工作区只允许出现本层运行自己产生的证据与判定书。
    ALLOW = ("unified-app/evidence/stages/s4_phase_c",
             "unified-app/stages/S4_PHASE_C_RESULT_v1.0.json")
    unclean = [l for l in git("status", "--porcelain").splitlines()
               if not any(x in l for x in ALLOW)]
    if unclean:
        raise SystemExit("工作区不干净，冻结提交之外还有改动，拒绝执行：\n" + "\n".join(unclean))

    live = json.loads(R.psql("select w.graph from workflows w join apps a on a.workflow_id=w.id "
                             "where a.id='%s';" % fz["binding"]["candidate_app_id"]))
    gsha = sha(json.dumps(live, ensure_ascii=False, sort_keys=True))
    if gsha != fz["binding"]["candidate_published_graph_sha256"]:
        raise SystemExit("候选图漂移，拒绝执行：%s" % gsha)

    pin = R.psql("select p.version from tool_workflow_providers p where p.name='diyu_uapp_hop';")
    if pin != fz["binding"]["hop_provider_pinned_version"]:
        raise SystemExit("hop provider 钉已变动，拒绝执行：%s" % pin)
    csha = R.psql("select encode(sha256(convert_to((select n->'data'->>'code' from workflows w, "
                  "jsonb_array_elements(w.graph::jsonb->'nodes') n where w.app_id='%s' "
                  "and w.version='%s' and n->>'id'='m5_compose'),'UTF8')),'hex');"
                  % (R.APPS["HOP"], pin))
    if csha != fz["binding"]["pinned_m5_compose_sha256"]:
        raise SystemExit("钉住那一版的 m5_compose 已变动，拒绝执行：%s" % csha)

    drift = {}
    for k, m in b["protected_apps_graph_md5"].items():
        now = R.psql("select md5(w.graph) from workflows w join apps a on a.workflow_id=w.id "
                     "where a.id='%s';" % R.APPS[k]).strip()
        if now != m:
            drift[k] = {"frozen": m, "now": now}
    if drift:
        raise SystemExit("受保护应用漂移，拒绝执行：" + json.dumps(drift, ensure_ascii=False))

    newer = R.psql("select count(*) from workflows w where w.created_at > "
                   "(select max(created_at) from workflows where app_id='%s');"
                   % fz["binding"]["candidate_app_id"])
    print("PREFLIGHT ok | graph=%s | pin=%s | 受保护面 %d/%d 无漂移 | 候选发布之后的新 workflow 版本数=%s"
          % (gsha[:16], pin, len(b["protected_apps_graph_md5"]), len(b["protected_apps_graph_md5"]), newer))

    if layer in ("C2", "C3"):
        prev = "C1" if layer == "C2" else "C2"
        if not os.path.exists(RESULT):
            raise SystemExit("上一层判定书不存在，%s 未获准发起" % layer)
        res = json.load(io.open(RESULT, encoding="utf-8"))
        v = (res.get("layers") or {}).get(prev, {}).get("verdict")
        if v != "PASS":
            raise SystemExit("%s 的判定不是 PASS（当前 %s），按停止规则不得发起 %s" % (prev, v, layer))
        print("层间硬门：%s = PASS，允许发起 %s" % (prev, layer))
    return b


# ---------------------------------------------------------------- C1
def run_c1(fz):
    d = json.load(io.open(C1_INPUT, encoding="utf-8"))
    if sha_file(C1_INPUT) != fz["layers"][0]["frozen_input"]["sha256"]:
        raise SystemExit("C1 冻结输入已变动，拒绝执行")
    out = os.path.join(EV, "S4-PC-C1.json")
    if os.path.exists(out):
        raise SystemExit("拒绝覆盖已有证据：" + out)

    app = d["target"]["app_id"]
    console = R.DC.Console(env=R.DC.load_env(R.ENV))
    key = console.app_api_key(app)
    user = "s4pc-c1-" + time.strftime("%Y%m%d%H%M%S")
    t0 = R.psql("select now()::text;")

    attempts, res = 0, None
    while attempts < 2:
        attempts += 1
        t = time.time()
        r = R.DC.http_json("POST", "/v1/workflows/run",
                           headers={"Authorization": "Bearer " + key},
                           body={"inputs": d["inputs"], "response_mode": "blocking", "user": user},
                           timeout=1800)
        try:
            body = json.loads(r["body"])
        except Exception:
            body = {"raw": r["body"][:4000]}
        res = {"http_status": r["status"], "elapsed_seconds": round(time.time() - t, 2),
               "body": body}
        blob = json.dumps(body, ensure_ascii=False)
        got_run = bool(((body.get("data") or {}).get("id")))
        if not (r["status"] != 200 and any(x in blob for x in TRANSIENT) and not got_run):
            break
        print("   纯传输失败且无模型输出，按纪律重试一次")

    rid = ((res["body"].get("data") or {}).get("workflow_run_id")
           or (res["body"].get("data") or {}).get("id") or "")
    runs = R.runs_since(app, t0)
    if not rid and runs:
        rid = runs[0]["id"]
    nodes = node_detail(rid)

    doc = {"case_id": "S4-PC-C1", "layer": "C1", "stage": "S4_PHASE_C",
           "freeze_sha256": sha_file(FREEZE), "input_sha256": sha_file(C1_INPUT),
           "app_id": app, "end_user": user, "window_start": t0,
           "http_status": res["http_status"], "elapsed_seconds": res["elapsed_seconds"],
           "attempts": attempts, "workflow_run_id": rid,
           "response_body": res["body"], "runs_during_case": runs,
           "nodes_executed": [{"idx": n.get("idx"), "node_id": n.get("node_id"),
                               "type": n.get("type"), "status": n.get("status"),
                               "error": n.get("error")} for n in nodes],
           "node_detail": nodes,
           "note": "运行器只发起与记录，不判定。"}
    write(out, doc)
    print("   SAVED S4-PC-C1 | http=%s %ss | nodes=%d"
          % (res["http_status"], res["elapsed_seconds"], len(nodes)))


def node_detail(run_id):
    if not run_id:
        return []
    raw = R.psql("select json_agg(json_build_object('idx',e.index,'node_id',e.node_id,"
                 "'title',e.title,'type',e.node_type,'status',e.status,'error',e.error,"
                 "'inputs',e.inputs,'outputs',e.outputs) order by e.index) "
                 "from workflow_node_executions e where e.workflow_run_id='%s';" % run_id)
    try:
        return json.loads(raw or "[]") or []
    except Exception:
        return []


# ---------------------------------------------------------------- C2 / C3
def conv_vars(cid):
    if not cid:
        return {}
    raw = R.psql("select json_agg(json_build_object('name', v.data::jsonb->>'name', "
                 "'len', length(coalesce(v.data::jsonb->>'value','')), "
                 "'head', left(coalesce(v.data::jsonb->>'value',''),240))) "
                 "from workflow_conversation_variables v where v.conversation_id='%s';" % cid)
    try:
        rows = json.loads(raw or "[]") or []
    except Exception:
        rows = []
    return {r["name"]: {"len": r["len"], "head": r["head"]} for r in rows}


def run_turns(fz, layer, idxs):
    plan = json.load(io.open(CONT_INPUTS, encoding="utf-8"))
    want = [l for l in fz["layers"] if l["id"] == layer][0]["frozen_input"]["sha256"]
    if sha_file(CONT_INPUTS) != want:
        raise SystemExit("冻结话术文件已变动，拒绝执行")

    fx = R.FIXTURE
    fx_sha = sha_file(fx)
    if fx_sha != fz["fixture"]["sha256"]:
        raise SystemExit("夹具 hash 与冻结不一致，拒绝执行：%s" % fx_sha)

    app = fz["binding"]["candidate_app_id"]
    console = R.DC.Console(env=R.DC.load_env(R.ENV))
    key = console.app_api_key(app)

    if os.path.exists(CONV):
        st = json.load(io.open(CONV, encoding="utf-8"))
        user, conv = st["end_user"], st["conversation_id"]
        print("续用同一会话：end_user=%s conv=%s" % (user, conv))
    else:
        user, conv = "s4pc-" + time.strftime("%Y%m%d%H%M%S"), ""
        print("全新会话：end_user=%s" % user)

    for t in plan["conversation"]["turns"]:
        if t["idx"] not in idxs:
            continue
        cid = "S4-PC-T%d" % t["idx"]
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

        doc = {"case_id": cid, "layer": layer, "stage": "S4_PHASE_C",
               "turn_index": t["idx"], "expect_capability": t["expect_capability"],
               "with_fixture": True, "freeze_sha256": sha_file(FREEZE),
               "inputs_sha256": sha_file(CONT_INPUTS),
               "graph_sha256_at_run": fz["binding"]["candidate_published_graph_sha256"],
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
        write(out, doc)
        write(CONV, {"end_user": user, "conversation_id": conv}, allow_overwrite=True)
        seam = [n["node_id"] for n in (nested.get("SEAM") or {}).get("latest_run_nodes") or []
                if n["node_id"].startswith("tool_")]
        print("   SAVED %s | http=%s %ss ans=%d | seam=%s"
              % (cid, res["http_status"], res["elapsed_seconds"], len(bj.get("answer") or ""), seam))


def write(path, doc, allow_overwrite=False):
    if os.path.exists(path) and not allow_overwrite:
        raise SystemExit("拒绝覆盖：" + path)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    io.open(path, "w", encoding="utf-8").write(json.dumps(doc, ensure_ascii=False, indent=2) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--layer", required=True, choices=["C1", "C2", "C3"])
    a = ap.parse_args()
    fz = json.load(io.open(FREEZE, encoding="utf-8"))
    os.makedirs(EV, exist_ok=True)
    preflight(fz, a.layer)
    if a.layer == "C1":
        run_c1(fz)
    elif a.layer == "C2":
        run_turns(fz, "C2", [1, 2])
    else:
        run_turns(fz, "C3", [3, 4, 5, 6])


if __name__ == "__main__":
    main()
