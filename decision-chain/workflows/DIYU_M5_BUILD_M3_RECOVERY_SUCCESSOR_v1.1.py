#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""M3 恢复场景技术状态权威 · 任务命名的版本化 successor（RB-2 / F1 残余项）。

**不覆盖 M3 已接受的应用。** 另建一个 successor，只在 `O-11 · 限定影响面`
末尾补一段，其余节点、提示词、闸门原样照搬已发布 graph。

为什么只补这一段：RB-1 的判别实验证明，`HOLDOUT-M5-05` 三条失败里有两条
（幂等、失败证据）的最高失效节点是 **M5 漏投影**——M3 拿不到运行状态，而它的
契约明写不处理 M2 的幂等与恢复内部实现。补上投影后那两条 4/4 成立，**不需要动 M3**。
剩下的一条（把「全部重来」当技术必要性）在投影补齐后仍有 1/4 失败，
那部分才是 M3 行为，落在合同 in_scope 的「M3 恢复场景技术状态权威」内。

补的这段完全用 M3 自己已有的词汇：上面「证据身份不得混写」表已经写了
「用户陈述 → 不能单独支持客观事实」，O-11 已经写了影响面怎么切。
缺的只是把两者接起来的那一句——恢复场景下运行状态属于客观事实那一栏。
不新增闸门、不新增状态、不放松任何既有约束。
"""
import importlib.util
import json
import os
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
_s = importlib.util.spec_from_file_location(
    "dc", os.path.join(ROOT, "account-operations", "tools", "dify_client.py"))
DC = importlib.util.module_from_spec(_s)
_s.loader.exec_module(DC)

ENV = "/home/faye/diyu-demo-worktrees/m3-account-content-operator-v1/.env"
M3_SOURCE = "b7fb5b1a-9278-426c-bb8a-f9f288639548"
APP_NAME = "DIYU M5 RB · M3 单账号持续运营（恢复状态权威）"
MARKED_NAME = "m5rb-m3-recov-v1.1"
MARKED_COMMENT = ("M5 AC-07 Rebase：只在 O-11 末尾补「恢复场景下运行状态不由口头偏好裁定」。"
                  "幂等与失败证据两条由 M5 补投影解决，不在此处改。")

ANCHOR = ("**判据**：既不多算（让有证据、不受影响的判断失效），也不少算（漏掉已知依赖）。"
          "影响关系判断不了的，标 `STALE` 待定向复验，**不假装知道依赖图**。")

ADDITION = """

**恢复场景下，运行状态不由口头偏好裁定。** 「全部重来我心里踏实点」「宁可多一次别漏了」
「跑通了就算」都是**用户陈述**——按上面「证据身份不得混写」那张表，它们支持用户的目标与偏好，
**不支持客观事实**。上一轮哪一步真的成功过、哪些写入真的已经发生、失败有没有被记录，
这些由输入里的运行状态投影裁定：投影在场就照它算，投影不在场就直说查不到。
两者都不等于「按用户说的算」。

所以收到「全部重来」时，照 O-11 切分：**给出重跑清单与保留清单**，
并说明不重跑的那部分为什么仍然成立。用户当然可以坚持全量重做，那是他的经营决定，
是一次被记录的选择；但**不得把它写成「按依赖图算下来本来就该全部重跑」**——
偏好和技术必要性是两件事，写在一起就分不清了。"""


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
    hits = []
    for n in g.get("nodes", []):
        d = n.get("data") or {}
        if d.get("type") != "llm":
            continue
        for pt in d.get("prompt_template") or []:
            t = pt.get("text") or ""
            if ANCHOR in t:
                pt["text"] = t.replace(ANCHOR, ANCHOR + ADDITION, 1)
                hits.append(n["id"])
    if len(hits) != 1:
        raise RuntimeError("期望恰好命中一个提示词锚点，实得 %s" % hits)

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
            "description": "M5 AC-07 Rebase successor：只在 O-11 末尾补恢复场景的技术状态权威。"})
        assert st in (200, 201), (st, app)
        app_id, created = app["id"], True

    st, cur = c.call("GET", "/console/api/apps/%s/workflows/draft" % app_id)
    prev = cur.get("hash") if st == 200 else None
    st, res = c.call("POST", "/console/api/apps/%s/workflows/draft" % app_id, body={
        "graph": g, "features": feats, "hash": prev,
        "environment_variables": [], "conversation_variables": []}, timeout=600)
    assert st == 200, ("draft sync failed", st, json.dumps(res, ensure_ascii=False)[:400])
    st, pub = c.call("POST", "/console/api/apps/%s/workflows/publish" % app_id,
                     body={"marked_name": MARKED_NAME, "marked_comment": MARKED_COMMENT},
                     timeout=600)
    assert st in (200, 201), ("publish failed", st, json.dumps(pub, ensure_ascii=False)[:400])

    md5 = psql("SELECT md5(graph) FROM workflows WHERE app_id='%s' AND version<>'draft' "
               "ORDER BY created_at DESC LIMIT 1;" % app_id).strip()
    src_md5 = psql("SELECT md5(graph) FROM workflows WHERE app_id='%s' AND version<>'draft' "
                   "ORDER BY created_at DESC LIMIT 1;" % M3_SOURCE).strip()
    out = {"source_app": M3_SOURCE, "source_graph_md5_after": src_md5,
           "successor_app": app_id, "created": created, "successor_graph_md5": md5,
           "patched_node": hits[0], "added_chars": len(ADDITION),
           "anchor_section": "O-11 · 限定影响面"}
    p = os.path.join(ROOT, "decision-chain", "evidence", "m5-rb", "M3_RECOVERY_SUCCESSOR_BUILD.json")
    json.dump(out, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print("M3 successor=%s md5=%s（源 %s 保持 %s）" % (app_id, md5, M3_SOURCE, src_md5))
    print("SAVED", p)
    return 0


if __name__ == "__main__":
    sys.exit(main())
