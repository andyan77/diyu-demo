#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""S4.2 第三次取证：按冻结的输入计划，正负两侧各走一遍多轮会话。

只发起、只记录，不判定。判据仍为 S4_2_STAGE_GATE_v1.1.json，一字未动。
正负两侧用逐字相同的用户话术，唯一差别是正例上传夹具。
下游能力拿到的上游产物由系统自己上一轮产出，执行侧不代写脚本、不代写成片。
"""
import hashlib
import importlib.util
import io
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
PLAN = os.path.join(HERE, "..", "stages", "S4_2_POS_INPUT_PLAN_v1.1.json")

spec = importlib.util.spec_from_file_location("s42run", os.path.join(HERE, "S4_2_RUN_v1.0.py"))
R = importlib.util.module_from_spec(spec)
spec.loader.exec_module(R)


def chat(key, query, user, files=None, conv=""):
    body = {"inputs": {}, "query": query, "response_mode": "blocking", "user": user}
    if files:
        body["files"] = files
    if conv:
        body["conversation_id"] = conv
    t0 = time.time()
    r = R.DC.http_json("POST", "/v1/chat-messages",
                       headers={"Authorization": "Bearer " + key}, body=body, timeout=1200)
    try:
        b = json.loads(r["body"])
    except Exception:
        b = {"raw": r["body"][:4000]}
    return {"http_status": r["status"], "elapsed_seconds": round(time.time() - t0, 2), "body": b}


def snapshot(d_case, side, cap, query, res, t_start, up, conv, turn_idx, plan_sha, gsha):
    body = res["body"] or {}
    mid = body.get("message_id") or ""
    rid, nodes = R.trace(mid) if mid else ("", [])
    nested = {}
    for k, aid in R.APPS.items():
        rs = R.runs_since(aid, t_start)
        item = {"app_id": aid, "runs_during_case": rs}
        if k == "SEAM" and rs:
            item["latest_run_nodes"] = R.nodes_of(rs[0]["id"])
        nested[k] = item
    return {"case_id": d_case, "stage": "S4.2", "capability": cap, "with_fixture": side == "POS",
            "attempt": "attempt03_chain", "turn_index": turn_idx,
            "input_plan_sha256": plan_sha, "stage_gate_sha256": gsha,
            "app_id": "85c01f85-a081-43e9-ab09-9993289cc200", "end_user": None,
            "query": query, "uploaded_fixture": up, "window_start": t_start,
            "http_status": res["http_status"], "elapsed_seconds": res["elapsed_seconds"],
            "attempts": 1, "message_id": mid, "workflow_run_id": rid,
            "conversation_id": body.get("conversation_id"), "answer": body.get("answer"),
            "nodes_executed": [{"idx": n.get("idx"), "node_id": n.get("node_id"),
                                "type": n.get("type"), "status": n.get("status"),
                                "error": n.get("error")} for n in nodes],
            "node_detail": nodes, "nested_app_runs": nested,
            "note": "多轮链路取证。运行器只发起与记录，不判定。"}


def main():
    g = R.gate()
    plan = json.load(io.open(PLAN, encoding="utf-8"))
    plan_sha = hashlib.sha256(io.open(PLAN, "rb").read()).hexdigest()
    console = R.DC.Console(env=R.DC.load_env(R.ENV))
    key = console.app_api_key(g["identity"]["successor_app_id"])
    fx_sha = hashlib.sha256(io.open(R.FIXTURE, "rb").read()).hexdigest()

    only_side = sys.argv[1] if len(sys.argv) > 1 else ""
    for side in ("POS", "NEG"):
        if only_side and side != only_side:
            continue
        for conv_spec in plan["conversations"]:
            name = conv_spec["name"]
            user = "s42c-%s-%s" % (name.lower(), side.lower())
            conv = ""
            up = None
            files = None
            # 每项能力的证据取「最后一次以该能力为目标的轮次」
            last_turn = {}
            for t in conv_spec["turns"]:
                last_turn[t["expect_capability"]] = t["idx"]
            print("\n########## %s / %s ##########" % (name, side))
            for t in conv_spec["turns"]:
                cap = t["expect_capability"]
                cid = "S4-CAP-%s-%s" % (cap, side)
                out = os.path.join(R.EV, cid + ".json")
                is_case = (t["idx"] == last_turn[cap])
                if is_case and os.path.exists(out):
                    print("[skip 已有证据] %s" % cid)
                # 上传素材是轮次作用域（见 TRIAGE 003）：只挂第一轮会让被测轮次
                # 实际不带夹具，正负两侧因此逐字相同。正例每一轮都附。
                if side == "POS":
                    st, b = R.upload(key, R.FIXTURE, user)
                    fid = (b or {}).get("id")
                    if st not in (200, 201) or not fid:
                        raise SystemExit("夹具上传失败：%s %s" % (st, str(b)[:200]))
                    up = {"http_status": st, "file_id": fid,
                          "name": os.path.basename(R.FIXTURE), "sha256": fx_sha}
                    files = [{"type": "document", "transfer_method": "local_file",
                              "upload_file_id": fid}]
                else:
                    files = None
                t_start = R.psql("select now()::text;")
                print("[T%d %s] %s" % (t["idx"], cap, t["text"][:44]))
                res = chat(key, t["text"], user, files=files, conv=conv)
                conv = (res["body"] or {}).get("conversation_id") or conv
                ans = (res["body"] or {}).get("answer") or ""
                print("   http=%s %ss ans_len=%d" % (res["http_status"], res["elapsed_seconds"],
                                                     len(ans)))
                if not is_case:
                    continue
                doc = snapshot(cid, side, cap, t["text"], res, t_start, up, conv,
                               t["idx"], plan_sha, g["_sha256"])
                doc["end_user"] = user
                if os.path.exists(out):
                    raise SystemExit("拒绝覆盖已有证据：" + out)
                with io.open(out, "w", encoding="utf-8") as fh:
                    fh.write(json.dumps(doc, ensure_ascii=False, indent=2) + "\n")
                seam = [n["node_id"] for n in (doc["nested_app_runs"].get("SEAM") or {})
                        .get("latest_run_nodes") or [] if n["node_id"].startswith("tool_")]
                print("   SAVED %s | seam=%s" % (cid, seam))


if __name__ == "__main__":
    main()
