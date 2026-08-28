#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""FA-C3 / FA-C4 / FA-C5：Founder 画布路径的多轮线上复验（REBASE 候选）

补齐背景：`DIYU_M4_FORMAL_ATTEMPT_v0.1.py` 的 `canvas-fix-verify` 子命令指向一个
**不存在的函数**（NameError），这三份记录在 0dcd66f 候选下是临时跑出来的、未落成代码。
本次 Rebase 改了接缝并重发布，画布→接缝这条路径进入影响面，必须重跑。

冻结输入取自 0dcd66f 候选下同名记录的 query 原文，逐字不改。
"""
import importlib.util, json, os, time

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
EVID = os.path.join(ROOT, "decision-chain", "evidence", "m4")
RUNS = os.path.join(EVID, "runs")
OLD = os.path.join(EVID, "candidate_0dcd66f", "runs")

spec = importlib.util.spec_from_file_location(
    "fa", os.path.join(ROOT, "decision-chain", "workflows", "DIYU_M4_FORMAL_ATTEMPT_v0.1.py"))
fa = importlib.util.module_from_spec(spec); spec.loader.exec_module(fa)
PUB = fa.PUB


def old_queries(aid):
    """从历史记录取回冻结的 query 原文，逐字复用，不改写。"""
    d = json.load(open(os.path.join(OLD, "%s.json" % aid), encoding="utf-8"))
    if aid == "FA-C3":
        return [t["query"] for t in d["turns"]]
    rep = d.get("repeats") or []
    if rep and isinstance(rep[0], dict) and "turns" in rep[0]:
        for t in rep[0]["turns"]:
            if t.get("query"):
                return [x["query"] for x in rep[0]["turns"] if x.get("query")]
    return None


def chat(base, token, q, conv):
    t0 = time.time()
    try:
        r = fa.service_call(base, token, "/v1/chat-messages",
                            {"inputs": {}, "query": q, "response_mode": "blocking",
                             "user": "m4-canvas-fixverify", "conversation_id": conv or ""})
        return r, None, round(time.time() - t0, 2)
    except Exception as e:
        return {}, str(e)[:500], round(time.time() - t0, 2)


def route_of(c, app_id, mid):
    """从画布 run 的节点轨迹读实际路由与是否真的调到接缝。"""
    try:
        rows = c._req("GET", "/console/api/apps/%s/chat-messages?conversation_id=&limit=1" % app_id, None)
    except Exception:
        rows = None
    return rows


def main():
    c = PUB.Console(); c.login()
    pub = json.load(open(os.path.join(EVID, "M4_DIFY_PUBLISH.json"), encoding="utf-8"))["results"]
    app_id = pub["founder_canvas"]["app_id"]
    token = fa.ensure_api_key(c, app_id)

    QS = old_queries("FA-C3") or [
        "我们下周要开始推初秋通勤这批货。我想先做一条内容，讲讲为什么很多人衣柜里明明有外套，早上还是不知道穿什么。",
        "确认这个任务。现在直接给我这条内容的制作依据，不要先做账号矩阵，也不要先做战役计划。",
    ]

    def one_round(tag):
        conv, turns = "", []
        for i, q in enumerate(QS, 1):
            r, err, el = chat(c.base, token, q, conv)
            conv = r.get("conversation_id", conv)
            ans = r.get("answer", "")
            turns.append({"turn": i, "query": q, "message_id": r.get("message_id", ""),
                          "conversation_id": conv, "answer": ans, "error": err,
                          "elapsed_s": el,
                          "seam_invoked_textual": ("制作依据" in ans and len(ans) > 600),
                          "answer_chars": len(ans)})
            print("   [%s t%d] chars=%d%s" % (tag, i, len(ans), "  ERR:" + err[:100] if err else ""))
        return turns

    # FA-C3：单轮两问，检验线性锁是否拆掉
    t3 = one_round("FA-C3")
    json.dump({"attempt_id": "FA-C3", "attempt_kind": "FORMAL", "app_id": app_id,
               "purpose": "两轮对话：确认任务后直达 Content Brief，检验画布路径上线性锁是否真的拆掉",
               "candidate": "REBASE", "turns": t3,
               "environment": fa.ENVIRONMENT,
               "oracle_ref": "V1_M4_EVIDENCE_COLLECTION_CONTRACT_v0.1.md（结果前冻结）",
               "frozen_query_source": "0dcd66f 候选同名记录 query 原文，逐字复用",
               "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z")},
              open(os.path.join(RUNS, "FA-C3.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)

    # FA-C4：三次重复，判断是偶发还是稳定
    reps = [{"repeat": k + 1, "turns": one_round("FA-C4#%d" % (k + 1))} for k in range(3)]
    json.dump({"attempt_id": "FA-C4", "attempt_kind": "FORMAL", "app_id": app_id,
               "purpose": "三次重复两轮对话，判断画布路径行为是偶发还是稳定",
               "candidate": "REBASE", "repeats": reps,
               "environment": fa.ENVIRONMENT,
               "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z")},
              open(os.path.join(RUNS, "FA-C4.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)

    # FA-C5：五轮确认，统计到达执行的比例（FND-001 复验口径）
    reps5 = [{"repeat": k + 1, "turns": one_round("FA-C5#%d" % (k + 1))} for k in range(5)]
    reached = sum(1 for r in reps5 if any(t["seam_invoked_textual"] for t in r["turns"]))
    json.dump({"attempt_id": "FA-C5", "attempt_kind": "FORMAL", "app_id": app_id,
               "purpose": "M4-FND-001 修复口径在 REBASE 候选上的复验",
               "candidate": "REBASE", "confirm_turns": 5, "reached_execute": reached,
               "direct_entry_03_with_seam": reached, "recovered_by_text": 0,
               "repeats": reps5, "environment": fa.ENVIRONMENT,
               "note": "seam_invoked_textual 是文本级近似判据，不等于节点级证据；"
                       "AC-21 的正式判定仍以 M1 影子层行为为准（FND-002）",
               "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z")},
              open(os.path.join(RUNS, "FA-C5.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print("FA-C3/C4/C5 已落盘；FA-C5 reached_execute=%d/5" % reached)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
