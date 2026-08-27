#!/usr/bin/env python3
"""路径 A §8.4：把活体候选恢复为冻结 v1.5.2 的图，并以具名版本发布（零模型调用）。

原库与原 App 已经随宿主挂载一起回来，所以**不导入 ep37**（§8.1）。
这里只做一件事：当前已发布版本是那条 `marked_name` 为空、且带画布几何漂移的
重发版；把草稿还原成 ep35 冻结图（逐字节），再以具名版本发布，
让**当前活体候选**的绑定不再依赖等价论证。

发布名用 `m3-cand-v1.5.2-live`，**不复用历史具名发布记录的名字**——
历史那条 `m3-cand-v1.5.2`（706fdce0…，2026-08-27 19:46:47.281053）原样保留。

不运行工作流，不调用模型。
"""
import hashlib
import io
import json
import os
import sys
import time

WT = "/home/faye/diyu-demo-worktrees/m3-account-content-operator-v1"
sys.path.insert(0, os.path.join(WT, "account-operations/tools"))
sys.path.insert(0, os.path.join(WT, "account-operations/tools/runners_v14"))

from dify_client import Console                    # noqa: E402
from create_m3_app import FEATURES, APP_ID         # noqa: E402

OUT = os.path.join(WT, "account-operations/evidence/ep43-dify-live-candidate-binding")
FROZEN = os.path.join(WT, "account-operations/evidence/ep35-candidate-v152-freeze/"
                          "m3_app_draft_graph_v152.json")
MARKED_NAME = "m3-cand-v1.5.2-live"
MARKED_COMMENT = ("Live candidate restored to frozen v1.5.2 graph after host-mount "
                  "recovery; no model run")
HIST_NAMED = {"workflow_id": "706fdce0-9a0d-42ec-8a8c-e4f6a3071173",
              "version": "2026-08-27 19:46:47.281053", "marked_name": "m3-cand-v1.5.2"}


def canon(o):
    return json.dumps(o, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha(t):
    return hashlib.sha256(t.encode("utf-8")).hexdigest()


def write(n, t):
    os.makedirs(OUT, exist_ok=True)
    io.open(os.path.join(OUT, n), "w", encoding="utf-8", newline="").write(t)


def main():
    assert len(MARKED_NAME) <= 20, len(MARKED_NAME)
    assert len(MARKED_COMMENT) <= 100, len(MARKED_COMMENT)
    fg = json.load(io.open(FROZEN, encoding="utf-8"))["graph"]

    c = Console()
    st, cur = c.call("GET", f"/console/api/apps/{APP_ID}/workflows/draft")
    assert st == 200, (st, cur)
    before = {"draft_hash": cur.get("hash"), "draft_graph_canon": sha(canon(cur["graph"]))}

    st, res = c.call("POST", f"/console/api/apps/{APP_ID}/workflows/draft", {
        "graph": fg, "features": FEATURES, "hash": cur.get("hash"),
        "environment_variables": [], "conversation_variables": []})
    assert st == 200, (st, res)

    st, pub = c.call("POST", f"/console/api/apps/{APP_ID}/workflows/publish",
                     {"marked_name": MARKED_NAME, "marked_comment": MARKED_COMMENT})
    assert st in (200, 201), (st, pub)

    st, d2 = c.call("GET", f"/console/api/apps/{APP_ID}/workflows/draft")
    st, p2 = c.call("GET", f"/console/api/apps/{APP_ID}/workflows/publish")
    write("after_draft_graph.json", json.dumps(d2, ensure_ascii=False, indent=2))
    write("after_published_graph.json", json.dumps(p2, ensure_ascii=False, indent=2))

    llm = {n["id"]: n for n in p2["graph"]["nodes"]}["operating_one_account_llm"]["data"]
    sys_sha = sha("".join(x.get("text", "") for x in (llm.get("prompt_template") or [])
                          if x.get("role") == "system"))
    rep = {
        "phase": "路径 A §8.4 · 活体候选恢复为冻结 v1.5.2 图并具名发布",
        "at": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "executor_model_calls": 0,
        "workflow_runs_executed": 0,
        "app_id": APP_ID,
        "ep37_dsl_imported": False,
        "reason_no_import": "原数据库与原 App 已随宿主挂载恢复，按 §8.1 不得导入 ep37",
        "before": before,
        "after": {"draft_hash": d2.get("hash"),
                  "published_workflow_id": p2["id"], "published_version": p2["version"],
                  "published_marked_name": p2.get("marked_name"),
                  "published_dify_hash": p2.get("hash"),
                  "published_graph_canon": sha(canon(p2["graph"]))},
        "frozen_graph_canon": sha(canon(fg)),
        "published_graph_byte_identical_to_frozen": canon(p2["graph"]) == canon(fg),
        "draft_equals_published": canon(d2["graph"]) == canon(p2["graph"]),
        "nodes": len(p2["graph"]["nodes"]), "edges": len(p2["graph"]["edges"]),
        "system_prompt_sha256": sys_sha,
        "system_prompt_matches_frozen": sys_sha == ("3a3c657d82d45e96dfbf9abdcb88adf66"
                                                    "c58bb74f69f1e1e0412591242898028"),
        "model": llm.get("model"),
        "unauthorized_node_types": sorted({n["data"]["type"] for n in p2["graph"]["nodes"]}
                                          & {"http-request", "tool"}),
        "historical_named_publish_preserved": HIST_NAMED,
        "naming_note": ("本次发布名 `m3-cand-v1.5.2-live` 与历史具名发布 `m3-cand-v1.5.2` "
                        "刻意不同名，避免冒充历史发布记录；历史那条原样保留在版本谱系里。"),
    }
    write("RESTORE_LIVE_CANDIDATE.json", json.dumps(rep, ensure_ascii=False, indent=2))
    for k in ("published_graph_byte_identical_to_frozen", "draft_equals_published",
              "system_prompt_matches_frozen", "nodes", "edges", "unauthorized_node_types"):
        print(f"  {k} = {rep[k]}")
    print("  published =", p2["version"], repr(p2.get("marked_name")))
    return rep


if __name__ == "__main__":
    main()
