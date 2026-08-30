#!/usr/bin/env python3
"""Publish and read back the frozen CAP-06 UAPP/PP candidate."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from types import ModuleType

HERE = Path(__file__).resolve().parent
UAPP_ROOT = HERE.parent
OUTPUT = (
    UAPP_ROOT / "evidence" / "stages" / "cap06_semantic_contract_v1_0"
    / "publication.json"
)


def load_module(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


BUILD = load_module("cap06_publish_build", HERE / "CAP06_SEMANTIC_CONTRACT_BUILD_v1.0.py")


def main() -> int:
    if OUTPUT.exists():
        raise FileExistsError(OUTPUT)
    if BUILD.graph_md5(BUILD.UAPP_APP_ID) != BUILD.BASE_UAPP_MD5:
        raise RuntimeError("UAPP predecessor drift")
    if BUILD.graph_md5(BUILD.PP_APP_ID) != BUILD.BASE_PP_MD5:
        raise RuntimeError("PP predecessor drift")
    if int(BUILD.BASE.psql("select count(*) from workflow_runs where status='running';")) != 0:
        raise RuntimeError("Active workflow exists")
    uapp, uapp_touched = BUILD.patch_uapp(BUILD.published_graph(BUILD.UAPP_APP_ID))
    pp, pp_touched = BUILD.patch_pp(BUILD.published_graph(BUILD.PP_APP_ID))
    responses = {
        "UAPP": BUILD.publish(BUILD.UAPP_APP_ID, uapp, "cap06-contract-v1"),
        "PP": BUILD.publish(BUILD.PP_APP_ID, pp, "cap06-shell-v1"),
    }
    readback_uapp = BUILD.published_graph(BUILD.UAPP_APP_ID)
    readback_pp = BUILD.published_graph(BUILD.PP_APP_ID)
    if BUILD.canonical(readback_uapp) != BUILD.canonical(uapp):
        raise RuntimeError("UAPP publication readback mismatch")
    if BUILD.canonical(readback_pp) != BUILD.canonical(pp):
        raise RuntimeError("PP publication readback mismatch")
    report = {
        "document": {"id": "CAP06_PUBLICATION_v1.0", "model_calls": 0},
        "responses": responses,
        "published_graph_md5": {
            "UAPP": BUILD.graph_md5(BUILD.UAPP_APP_ID),
            "PP": BUILD.graph_md5(BUILD.PP_APP_ID),
        },
        "canonical_sha256": {
            "UAPP": BUILD.sha256_text(BUILD.canonical(readback_uapp)),
            "PP": BUILD.sha256_text(BUILD.canonical(readback_pp)),
        },
        "touched": {"UAPP": uapp_touched, "PP": pp_touched},
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
