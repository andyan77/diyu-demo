#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""N1 · M3 successor v1.2：撤回影响面切分、副作用真实性、关键输入在场判断。

**不覆盖任何已接受应用，也不覆盖 v1.1.3 候选里的 rb M3。** 另建 successor，
只在两个既有小节末尾各补一段，其余节点、提示词、闸门原样照搬已发布 graph。

为什么补在这两处而不是新开小节：
  O-11 已经在讲影响面怎么切，撤回的影响面止于哪里是同一件事的下一句；
  O-9 已经在讲「决定是否生产」并定义了 NO_CONTENT_TASK 四要素，
  「缺关键输入就停在缺口」用的正是那四要素，不需要第二套停止机制。
不新增闸门、不新增状态词、不放松任何既有约束。

两条失败的证据见 decision-chain/docs/V1_M5_FINAL_P0_FAILURE_TRIAGE_v1.0.md：
  RB-01 —— 把已发布内容当成素材撤回的自动下游，且声称了未发生的写入；
  RB-02 变体 N —— 用户明说商品回头补，M3 自选三件商品并派发内容任务。
下游（hop 适配器、六个能力应用）在 RB-02 中忠实保留了「候选／待补充」，无证据有错，不改。
"""
import importlib.util, json, os, subprocess, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
_s = importlib.util.spec_from_file_location(
    "dc", os.path.join(ROOT, "account-operations", "tools", "dify_client.py"))
DC = importlib.util.module_from_spec(_s); _s.loader.exec_module(DC)

ENV = "/home/faye/diyu-demo-worktrees/m3-account-content-operator-v1/.env"
M3_SOURCE = "ca4c28aa-e0fd-4c54-bde3-a0918dc4c884"        # rb successor，本轮的源
APP_NAME = "DIYU M5 FP · M3 单账号持续运营（撤回影响面与在场判断）"
MARKED_NAME = "m5fp-m3-v1.2"
MARKED_COMMENT = ("M5 最后一轮最小修复 N1：O-11 补撤回影响面止于未发布产出＋副作用真实性；"
                  "O-9 补关键业务输入缺席时停在缺口、不自选商品。不新增闸门与状态词。")

ANCHOR_O11 = "偏好和技术必要性是两件事，写在一起就分不清了。"

ADD_O11 = """

**素材撤回的影响面止于依赖它的未发布产出。** 撤回一组素材，直接受影响的是**还没发出去的**、
把这组素材当依据的内容：停、换素材，或者重新取证。**已经发出去的内容不在这条自动下游里。**
已发布内容要不要补说明、要不要下架、系统内要不要标失效，是三件互相独立的经营决定；
用户即使在同一句话里顺带提了一嘴，也要把它拆出来单独确认，不和撤回打包处理。
代价不一样：撤回未发布的只损失产能，动已发布的会影响已经看过的人、已经产生的反馈，
以及已经存在的对外记录。

**没有发生的写入不能说成已经发生。** 「已标记」「已作废」「已完成」「已失效」这类完成态，
只有在运行状态投影里查得到对应的成功写入时才能写。查不到就照实说「这一步还没执行」
「需要一次写入」「我可以给出处置方案，等你确认后再执行」。当前这条路径有没有写权限也要讲清楚：
没有写权限时，能给的是方案，不是结果。**不得用「我已经处理了」来表示「我打算这样处理」。**"""

ANCHOR_O9 = "重新判断触发：门店给出可承接时段。」"

ADD_O9 = """

**关键业务输入缺席时，停在缺口，不替用户选。** 一条内容任务至少要有「讲哪个商品」或
「哪个明确的内容方向」。用户明说「这块我回头再补」，或者现有权威输入推不出唯一答案时，
这一项就是缺席——按上面 `NO_CONTENT_TASK` 的四要素停在这里，不需要第二套停止机制。
能定的照常定（账号、条数、周期、承接边界这些该给就给），只提一个最小问题，等用户补。

**不得从已登记商品表、上一周期、历史上下文或素材库里挑一个或几个具体商品来顶替。**
挑出来标成「候选」也不行——下游拿到的是一份字段齐全的任务，它没有义务替你把「候选」
再降回「缺席」。同理不得自行拟定内容方向、价格或素材组合。

这条不是让你变得难说话。信息完整的部分照常交付，**该停的是缺哪一项就停哪一项，不是整件事。**"""


def psql(q):
    p = subprocess.run(["docker", "exec", "-i", "docker-db_postgres-1", "psql", "-U", "postgres",
                        "-d", "dify", "-t", "-A", "-c", q], capture_output=True, text=True, timeout=300)
    if p.returncode != 0:
        raise RuntimeError(p.stderr[:400])
    return p.stdout


def main():
    g = json.loads(psql("SELECT graph FROM workflows WHERE app_id='%s' AND version<>'draft' "
                        "ORDER BY created_at DESC LIMIT 1;" % M3_SOURCE).strip())
    feats = json.loads((psql("SELECT features FROM workflows WHERE app_id='%s' AND version<>'draft' "
                             "ORDER BY created_at DESC LIMIT 1;" % M3_SOURCE).strip()) or "{}")

    hits = {"O11": [], "O9": []}
    for n in g.get("nodes", []):
        d = n.get("data") or {}
        if d.get("type") != "llm":
            continue
        for pt in d.get("prompt_template") or []:
            t = pt.get("text") or ""
            if ANCHOR_O11 in t:
                if t.count(ANCHOR_O11) != 1:
                    raise RuntimeError("O-11 锚点不唯一：%d" % t.count(ANCHOR_O11))
                t = t.replace(ANCHOR_O11, ANCHOR_O11 + ADD_O11, 1)
                hits["O11"].append(n["id"])
            if ANCHOR_O9 in t:
                if t.count(ANCHOR_O9) != 1:
                    raise RuntimeError("O-9 锚点不唯一：%d" % t.count(ANCHOR_O9))
                t = t.replace(ANCHOR_O9, ANCHOR_O9 + ADD_O9, 1)
                hits["O9"].append(n["id"])
            pt["text"] = t
    if len(hits["O11"]) != 1 or len(hits["O9"]) != 1:
        raise RuntimeError("两个锚点各须命中恰好一次，实得 %s" % hits)

    c = DC.Console(env=DC.load_env(ENV))
    st, apps = c.call("GET", "/console/api/apps?page=1&limit=100")
    assert st == 200
    hit = [a for a in apps["data"] if a.get("name") == APP_NAME]
    if hit:
        app_id, created = hit[0]["id"], False
    else:
        st, app = c.call("POST", "/console/api/apps", body={
            "name": APP_NAME, "mode": "workflow", "icon_type": "emoji", "icon": "🧭",
            "icon_background": "#E4FBCC",
            "description": "M5 最后一轮最小修复 N1：撤回影响面、副作用真实性、关键输入在场判断。"})
        assert st in (200, 201), (st, app)
        app_id, created = app["id"], True

    st, cur = c.call("GET", "/console/api/apps/%s/workflows/draft" % app_id)
    prev = cur.get("hash") if st == 200 else None
    st, res = c.call("POST", "/console/api/apps/%s/workflows/draft" % app_id, body={
        "graph": g, "features": feats, "hash": prev,
        "environment_variables": [], "conversation_variables": []}, timeout=600)
    assert st == 200, ("draft sync failed", st, json.dumps(res, ensure_ascii=False)[:400])
    st, pub = c.call("POST", "/console/api/apps/%s/workflows/publish" % app_id,
                     body={"marked_name": MARKED_NAME, "marked_comment": MARKED_COMMENT}, timeout=600)
    assert st in (200, 201), ("publish failed", st, json.dumps(pub, ensure_ascii=False)[:400])

    md5 = psql("SELECT md5(graph) FROM workflows WHERE app_id='%s' AND version<>'draft' "
               "ORDER BY created_at DESC LIMIT 1;" % app_id).strip()
    # 保护面复算：源与 legacy M3 必须一个字节都没动
    srcs = {"rb_m3_source": M3_SOURCE, "legacy_m3_accepted": "b7fb5b1a-9278-426c-bb8a-f9f288639548"}
    untouched = {k: psql("SELECT md5(graph) FROM workflows WHERE app_id='%s' AND version<>'draft' "
                         "ORDER BY created_at DESC LIMIT 1;" % v).strip() for k, v in srcs.items()}
    out = {"node": "N1", "source_app": M3_SOURCE, "successor_app": app_id, "created": created,
           "successor_graph_md5": md5, "patched_nodes": hits,
           "added_chars": {"O11": len(ADD_O11), "O9": len(ADD_O9)},
           "anchors": {"O11": ANCHOR_O11, "O9": ANCHOR_O9},
           "source_apps_graph_md5_after": untouched,
           "new_gates_added": 0, "new_state_words_added": 0}
    p = os.path.join(ROOT, "decision-chain", "evidence", "m5", "FINAL_P0_M3_SUCCESSOR_BUILD.json")
    json.dump(out, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print("N1 M3 successor=%s md5=%s created=%s" % (app_id, md5, created))
    print("源应用未变：", json.dumps(untouched, ensure_ascii=False))
    print("SAVED", p)
    return 0


if __name__ == "__main__":
    sys.exit(main())
