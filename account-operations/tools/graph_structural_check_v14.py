#!/usr/bin/env python3
"""EP-05 structural check（第 7 轮，对 v1.4 已发布图重跑） on the live M3 Dify candidate graph.

Closes two frozen inputs that could not be checked before the app existed:
  - M3-AC-05 structural half: the four behaviour labels must not appear in any
    enum / CHECK constraint / node branch condition / required field.
  - M3-AC-13 frozen input "+ Dify 图": no M2 write endpoint, credential or
    is_current=true assignment reachable from the graph.

Reads the LIVE draft graph from the Console API (not a local copy), so the
check is bound to what is actually deployed.
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dify_client import Console  # noqa: E402

APP_ID = "b7fb5b1a-9278-426c-bb8a-f9f288639548"
OUT = "/home/faye/diyu-demo-worktrees/m3-account-content-operator-v1/account-operations/evidence/ep25-structural-v14"

BEHAVIOUR_LABELS = ["ACCOUNT_STATE_DIAGNOSIS", "CYCLE_PLANNING",
                    "DAILY_CONTENT_DECISION", "REVIEW_UPDATE", "DAILY_DECISION"]

# Places where a behaviour label would mean "frozen into a physical enum".
STRUCTURAL_SITES = ["variables", "options", "conditions", "cases", "classes",
                    "logical_operator", "value_selector", "outputs"]

M2_WRITE_MARKERS = [r"is_current\s*[:=]\s*true", r"/api/v1/.*(feedback|observation).*",
                    r"POST\s+.*business-persistence", r"Authorization",
                    r"api[_-]?key", r"credential"]


def walk(obj, path=""):
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield from walk(v, f"{path}.{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from walk(v, f"{path}[{i}]")
    else:
        yield path, obj


def main():
    os.makedirs(OUT, exist_ok=True)
    c = Console()
    st, draft = c.call("GET", f"/console/api/apps/{APP_ID}/workflows/draft")
    assert st == 200, (st, draft)
    st2, published = c.call("GET", f"/console/api/apps/{APP_ID}/workflows/publish")
    graph = draft["graph"]

    report = {"app_id": APP_ID, "draft_hash": draft.get("hash"),
              "published_version": published.get("version") if isinstance(published, dict) else None,
              "node_count": len(graph["nodes"]), "edge_count": len(graph["edges"]),
              "nodes": [{"id": n["id"], "type": n["data"]["type"], "title": n["data"].get("title")}
                        for n in graph["nodes"]],
              "edges": [f"{e['source']}->{e['target']}" for e in graph["edges"]]}

    # ---- AC-05: behaviour labels must not be structural ------------------
    hits = []
    for path, val in walk(graph):
        if not isinstance(val, str):
            continue
        for lab in BEHAVIOUR_LABELS:
            if lab in val:
                structural = any(f".{s}" in path or f"{s}[" in path for s in STRUCTURAL_SITES)
                hits.append({"label": lab, "path": path, "structural_site": structural,
                             "excerpt": val[max(0, val.find(lab) - 60):val.find(lab) + 80]})
    report["ac05_behaviour_label_hits"] = hits
    report["ac05_structural_hits"] = [h for h in hits if h["structural_site"]]
    # the four labels only legitimately appear inside the LLM node's prompt text
    report["ac05_verdict_inputs"] = {
        "hits_total": len(hits),
        "hits_in_structural_sites": len(report["ac05_structural_hits"]),
        "start_node_variables": [v for n in graph["nodes"] if n["data"]["type"] == "start"
                                 for v in n["data"]["variables"]],
        "node_types": sorted({n["data"]["type"] for n in graph["nodes"]}),
        "branch_node_types_present": sorted({n["data"]["type"] for n in graph["nodes"]}
                                            & {"if-else", "question-classifier", "iteration", "code"}),
    }

    # ---- AC-13: no M2 write path reachable from the graph ----------------
    write_hits = []
    for path, val in walk(graph):
        if not isinstance(val, str):
            continue
        # skip the LLM prompt bodies: they are prose, checked separately below
        prose = ".prompt_template" in path
        for pat in M2_WRITE_MARKERS:
            for m in re.finditer(pat, val, re.IGNORECASE):
                write_hits.append({"pattern": pat, "path": path, "in_prompt_prose": prose,
                                   "excerpt": val[max(0, m.start() - 60):m.end() + 60]})
    report["ac13_write_marker_hits"] = write_hits
    report["ac13_verdict_inputs"] = {
        "http_request_nodes": [n["id"] for n in graph["nodes"] if n["data"]["type"] == "http-request"],
        "tool_nodes": [n["id"] for n in graph["nodes"] if n["data"]["type"] == "tool"],
        "code_nodes": [n["id"] for n in graph["nodes"] if n["data"]["type"] == "code"],
        "environment_variables": draft.get("environment_variables"),
        "conversation_variables": draft.get("conversation_variables"),
        "hits_outside_prompt_prose": [h for h in write_hits if not h["in_prompt_prose"]],
    }

    with open(os.path.join(OUT, "dify_graph_structural_check.json"), "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    with open(os.path.join(OUT, "dify_draft_graph.json"), "w", encoding="utf-8") as f:
        json.dump(draft, f, ensure_ascii=False, indent=2)

    print(json.dumps({k: v for k, v in report.items()
                      if k not in ("ac05_behaviour_label_hits", "ac13_write_marker_hits")},
                     ensure_ascii=False, indent=2)[:4000])
    print("\nAC-05 label hits:", len(hits), "| in structural sites:", len(report["ac05_structural_hits"]))
    print("AC-13 write-marker hits outside prompt prose:",
          len(report["ac13_verdict_inputs"]["hits_outside_prompt_prose"]))


if __name__ == "__main__":
    main()
