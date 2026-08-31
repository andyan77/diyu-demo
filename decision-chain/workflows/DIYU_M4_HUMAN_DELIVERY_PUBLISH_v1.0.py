#!/usr/bin/env python3
"""Publish only the six versioned M4 user-delivery successors and rebind tools."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PUB = ROOT / "decision-chain/workflows/DIYU_M4_PUBLISH_AND_REBIND_v0.1.py"
PATHS = {
    "matrix": ROOT / "decision-chain/workflows/DIYU_M4_TOOL_MATRIX_v1_4_HUMAN_DELIVERY.yml",
    "campaign": ROOT / "decision-chain/workflows/DIYU_M4_TOOL_CAMPAIGN_v1_4_HUMAN_DELIVERY.yml",
    "content_brief": ROOT / "decision-chain/workflows/DIYU_M4_TOOL_CONTENT_BRIEF_v1_4_HUMAN_DELIVERY.yml",
    "creative_script": ROOT / "content-production/workflows/DIYU_M4_TOOL_CREATIVE_SCRIPT_v1_4_HUMAN_DELIVERY.yml",
    "production_director": ROOT / "content-production/workflows/DIYU_M4_TOOL_PRODUCTION_DIRECTOR_v1_4_HUMAN_DELIVERY.yml",
    "publishing_packaging": ROOT / "content-production/workflows/DIYU_M4_TOOL_PUBLISHING_PACKAGING_v1_4_HUMAN_DELIVERY.yml",
}
NAME_LIKE = {
    "matrix": "%Matrix Architect", "campaign": "%Campaign Orchestrator",
    "content_brief": "%Content Brief Architect", "creative_script": "%Creative Script%",
    "production_director": "%Production Director", "publishing_packaging": "%Publishing & Packaging",
}
TOOL_NAME = {"matrix": "diyu_m4_matrix", "campaign": "diyu_m4_campaign",
             "content_brief": "diyu_m4_content_brief", "creative_script": "diyu_m4_creative_script",
             "production_director": "diyu_m4_production_director",
             "publishing_packaging": "diyu_m4_publishing_packaging"}


def load():
    spec = importlib.util.spec_from_file_location("m4_delivery_pub", PUB)
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)
    return mod


def graph_hash(pub, app_id: str) -> str:
    rows = pub.psql("SELECT a.workflow_id||'|'||md5(w.graph) FROM apps a JOIN workflows w ON w.id=a.workflow_id WHERE a.id='%s';" % app_id)
    return rows[0] if rows else "ABSENT"


def current_bindings(pub):
    result = {}
    for key, like in NAME_LIKE.items():
        rows = pub.psql("SELECT id FROM apps WHERE name LIKE '%s' ORDER BY updated_at DESC LIMIT 1;" % like)
        if not rows:
            raise RuntimeError("current %s app is absent" % key)
        app_id = rows[0]
        providers = pub.psql("SELECT id FROM tool_workflow_providers WHERE app_id='%s' AND name='%s';" %
                             (app_id, TOOL_NAME[key]))
        if len(providers) != 1:
            raise RuntimeError("current %s provider is ambiguous/absent" % key)
        result[key] = {"app_id": app_id, "provider_id": providers[0], "tool_name": TOOL_NAME[key]}
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--publish", action="store_true")
    args = parser.parse_args()
    pub = load()
    bindings = current_bindings(pub)
    before = {key: graph_hash(pub, bindings[key]["app_id"]) for key in PATHS}
    result = {"document": "DIYU_M4_HUMAN_DELIVERY_PUBLISH_v1.0", "model_calls": 0,
              "mode": "publish" if args.publish else "preflight", "apps": {}}
    if not args.publish:
        for key, path in PATHS.items():
            result["apps"][key] = {"app_id": bindings[key]["app_id"], "before": before[key],
                                   "dsl_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                                   "provider_id": bindings[key]["provider_id"]}
        print(json.dumps(result, ensure_ascii=False, indent=2)); return 0
    console = pub.Console(); console.login()
    tools = console.list_workflow_tools()
    tool_rows = tools if isinstance(tools, list) else tools.get("data", [])
    by_app = {item.get("workflow_app_id"): item for item in tool_rows if item.get("workflow_app_id")}
    for key, path in PATHS.items():
        app_id, text = bindings[key]["app_id"], path.read_text(encoding="utf-8")
        console.import_dsl(text, app_id=app_id)
        console.publish(app_id)
        provider = by_app.get(app_id) or {}
        provider_id = provider.get("id") or bindings[key]["provider_id"]
        params = pub.params_from_start(str(path))
        label = provider.get("label") or key
        if isinstance(label, dict):
            label = label.get("en_US") or label.get("zh_Hans") or next(iter(label.values()), key)
        console.update_workflow_tool(provider_id, bindings[key]["tool_name"], label, params)
        after = graph_hash(pub, app_id)
        result["apps"][key] = {"app_id": app_id, "before": before[key], "after": after,
                               "graph_changed": before[key] != after,
                               "provider_id": provider_id,
                               "dsl_sha256": hashlib.sha256(text.encode()).hexdigest()}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if all(item["graph_changed"] for item in result["apps"].values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
