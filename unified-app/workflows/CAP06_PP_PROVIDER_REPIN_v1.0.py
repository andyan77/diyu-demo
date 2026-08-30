#!/usr/bin/env python3
"""Repin the existing PP workflow provider to the frozen current publication."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from types import ModuleType

HERE = Path(__file__).resolve().parent
UAPP_ROOT = HERE.parent
PP_APP_ID = "c9cdea24-9df3-400b-9ecd-1d740e8c96df"
PP_PROVIDER = "diyu_m5fp_publishing_packaging"
EXPECTED_PP_MD5 = "99287feadcd784e86bf4c298bea555fc"
EXPECTED_SEAM_MD5 = "db49a3da8973d4fdcbe9ecf63bdf7e2a"
OUTPUT = UAPP_ROOT / "evidence" / "stages" / "cap06_semantic_contract_v1_0" / "provider_repin.json"


def load_module(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


BUILD = load_module("cap06_repin_build", HERE / "CAP06_SEMANTIC_CONTRACT_BUILD_v1.0.py")


def provider_state() -> dict[str, str]:
    version = BUILD.BASE.psql(
        f"select version from tool_workflow_providers where name='{PP_PROVIDER}';"
    )
    return {
        "version": version,
        "graph_md5": BUILD.BASE.psql(
            "select md5(graph) from workflows "
            f"where app_id='{PP_APP_ID}' and version='{version}';"
        ),
    }


def main() -> int:
    if OUTPUT.exists():
        raise FileExistsError(OUTPUT)
    if BUILD.graph_md5(PP_APP_ID) != EXPECTED_PP_MD5:
        raise RuntimeError("PP publication drift")
    seam_md5 = BUILD.graph_md5("5fca0162-e26b-4545-a00b-66b1a2a2a077")
    if seam_md5 != EXPECTED_SEAM_MD5:
        raise RuntimeError("Seam drift")
    before = provider_state()
    console = BUILD.BASE.DC.Console(env=BUILD.BASE.DC.load_env(BUILD.ENV_FILE))
    status, tool = console.call(
        "GET",
        f"/console/api/workspaces/current/tool-provider/workflow/get?workflow_app_id={PP_APP_ID}",
        timeout=300,
    )
    if status != 200 or not isinstance(tool, dict):
        raise RuntimeError(f"provider GET failed: {status}")
    payload = {
        "workflow_tool_id": tool["workflow_tool_id"],
        "name": tool["name"],
        "label": tool["label"],
        "icon": tool["icon"],
        "description": tool["description"],
        "parameters": tool["parameters"],
        "privacy_policy": tool.get("privacy_policy") or "",
        "labels": [
            item["name"] if isinstance(item, dict) else item
            for item in (tool.get("tool") or {}).get("labels", [])
        ],
    }
    status, response = console.call(
        "POST",
        "/console/api/workspaces/current/tool-provider/workflow/update",
        body=payload,
        timeout=300,
    )
    if status not in (200, 201):
        raise RuntimeError(f"provider update failed: {status}")
    after = provider_state()
    if after["graph_md5"] != EXPECTED_PP_MD5:
        raise RuntimeError("Provider did not pin to frozen PP graph")
    if BUILD.graph_md5("5fca0162-e26b-4545-a00b-66b1a2a2a077") != EXPECTED_SEAM_MD5:
        raise RuntimeError("Seam changed during provider repin")
    report = {
        "document": {"id": "CAP06_PP_PROVIDER_REPIN_v1.0", "model_calls": 0},
        "before": before,
        "after": after,
        "provider_id": tool["workflow_tool_id"],
        "update_status": status,
        "update_response": response,
        "seam_graph_md5": EXPECTED_SEAM_MD5,
    }
    OUTPUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

