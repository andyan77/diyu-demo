#!/usr/bin/env python3
"""最终候选 v1.5.2 · 导出与恢复演练（Execution Prompt v1.2 §4.4 末条）。零模型调用。

只在任务专用候选 App 内做，**不碰已发布版本、不碰生产**：

  1 导出 DSL 全文并落盘（这是回滚入口）
  2 快照当前草稿图
  3 故意损坏草稿（把边删到只剩一条）
  4 核实确实坏了
  5 用快照恢复
  6 核实恢复后与快照**逐字节相同**
  7 核实已发布版本全程未变

任何一步失败都如实落盘，不隐藏。恢复失败时脚本非零退出，且 DSL 导出件仍在，
可用 `POST /console/api/apps/imports` 重建。
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
WT = os.path.dirname(os.path.dirname(TOOLS))
sys.path.insert(0, TOOLS)
from dify_client import Console                                    # noqa: E402
from create_m3_app import APP_ID                                   # noqa: E402

OUT = os.path.join(WT, "account-operations/evidence/ep37-rollback-drill-v152")


def _sha(o):
    return hashlib.sha256(json.dumps(o, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def main():
    os.makedirs(OUT, exist_ok=True)
    c = Console()
    steps, ok = [], True

    st, exp = c.call("GET", f"/console/api/apps/{APP_ID}/export?include_secret=false")
    assert st == 200, (st, exp)
    dsl = exp["data"] if isinstance(exp, dict) else str(exp)
    open(os.path.join(OUT, "m3_candidate_app_v152.dsl.yaml"), "w", encoding="utf-8").write(dsl)
    steps.append({"step": "1_export_dsl", "chars": len(dsl),
                  "sha256": hashlib.sha256(dsl.encode()).hexdigest(),
                  "saved_to": "m3_candidate_app_v152.dsl.yaml"})

    st, pub_before = c.call("GET", f"/console/api/apps/{APP_ID}/workflows/publish")
    assert st == 200
    pub_ver = pub_before.get("version")
    pub_sha = _sha(pub_before["graph"])

    st, snap = c.call("GET", f"/console/api/apps/{APP_ID}/workflows/draft")
    assert st == 200
    backup_graph, backup_hash = snap["graph"], snap.get("hash")
    steps.append({"step": "2_snapshot_draft", "graph_sha256": _sha(backup_graph),
                  "node_count": len(backup_graph["nodes"]),
                  "edge_count": len(backup_graph["edges"]), "dify_hash": backup_hash})

    damaged = json.loads(json.dumps(backup_graph))
    damaged["edges"] = damaged["edges"][:1]
    st, r = c.call("POST", f"/console/api/apps/{APP_ID}/workflows/draft",
                   body={"graph": damaged, "features": snap.get("features") or {},
                         "hash": backup_hash, "environment_variables": [],
                         "conversation_variables": []}, timeout=180)
    steps.append({"step": "3_damage_draft", "status": st, "result": json.dumps(r, ensure_ascii=False)[:120]})
    cur_hash = (r or {}).get("hash")

    st, d2 = c.call("GET", f"/console/api/apps/{APP_ID}/workflows/draft")
    steps.append({"step": "4_verify_damage", "graph_sha256": _sha(d2["graph"]),
                  "differs_from_backup": _sha(d2["graph"]) != _sha(backup_graph),
                  "edge_count": len(d2["graph"]["edges"])})
    ok = ok and steps[-1]["differs_from_backup"]

    st, r = c.call("POST", f"/console/api/apps/{APP_ID}/workflows/draft",
                   body={"graph": backup_graph, "features": snap.get("features") or {},
                         "hash": cur_hash or d2.get("hash"), "environment_variables": [],
                         "conversation_variables": []}, timeout=180)
    steps.append({"step": "5_restore_draft", "status": st, "result": json.dumps(r, ensure_ascii=False)[:120]})

    st, d3 = c.call("GET", f"/console/api/apps/{APP_ID}/workflows/draft")
    identical = _sha(d3["graph"]) == _sha(backup_graph)
    steps.append({"step": "6_verify_restore", "graph_sha256": _sha(d3["graph"]),
                  "identical_to_backup": identical,
                  "node_count": len(d3["graph"]["nodes"]),
                  "edge_count": len(d3["graph"]["edges"]),
                  "dify_hash": d3.get("hash")})
    ok = ok and identical

    st, pub_after = c.call("GET", f"/console/api/apps/{APP_ID}/workflows/publish")
    untouched = (pub_after.get("version") == pub_ver and _sha(pub_after["graph"]) == pub_sha)
    steps.append({"step": "7_published_untouched", "status": st,
                  "published_version": pub_after.get("version"),
                  "published_graph_sha256": _sha(pub_after["graph"]),
                  "untouched": untouched})
    ok = ok and untouched

    rep = {"what": "最终候选 v1.5.2 导出与恢复演练", "app_id": APP_ID,
           "zero_model_calls": True, "production_touched": False,
           "restore_succeeded": ok, "steps": steps,
           "rollback_entry": ("account-operations/evidence/ep37-rollback-drill-v152/"
                              "m3_candidate_app_v152.dsl.yaml —— "
                              "POST /console/api/apps/imports 可重建整个 App；"
                              "草稿单独回滚用第 2 步快照里的 graph 直接 PUT 回 draft")}
    json.dump(rep, open(os.path.join(OUT, "ROLLBACK_DRILL_V152.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    json.dump({"graph": backup_graph, "features": snap.get("features") or {}},
              open(os.path.join(OUT, "draft_snapshot_v152.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    for s in steps:
        print(" ", s["step"], {k: v for k, v in s.items() if k != "step"})
    print("restore_succeeded", ok)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
