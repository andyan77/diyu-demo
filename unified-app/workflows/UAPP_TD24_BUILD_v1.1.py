#!/usr/bin/env python3
"""Frozen successor wrapper for the final TD24 candidate implementation.

The v1.0 build evidence captured an earlier in-memory candidate before transitive
invalidation metadata was completed. This wrapper preserves that record and writes a
new v1.1 build record for the candidate bound by the formal Gate.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import logging
import os
from types import ModuleType
from typing import Any

HERE = os.path.dirname(os.path.abspath(__file__))
UAPP_ROOT = os.path.abspath(os.path.join(HERE, ".."))
EVIDENCE_DIR = os.path.join(UAPP_ROOT, "evidence", "stages", "uapp_td24")


def load_module(name: str, path: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


BASE = load_module("uapp_td24_builder_v10", os.path.join(HERE, "UAPP_TD24_BUILD_v1.0.py"))


def sha256_file(path: str) -> str:
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


def apply_draft(candidate: dict[str, Any], report: dict[str, Any]) -> None:
    console = BASE.DC.Console(env=BASE.DC.load_env(BASE.ENV_FILE))
    status, draft = console.call(
        "GET", f"/console/api/apps/{BASE.UAPP_APP_ID}/workflows/draft", timeout=300
    )
    if status != 200:
        raise RuntimeError(f"Draft read failed: {status} {str(draft)[:300]}")
    payload = {
        "graph": candidate,
        "features": draft.get("features") or {},
        "hash": draft.get("hash"),
        "environment_variables": draft.get("environment_variables") or [],
        "conversation_variables": draft.get("conversation_variables") or [],
    }
    write_status, response = console.call(
        "POST",
        f"/console/api/apps/{BASE.UAPP_APP_ID}/workflows/draft",
        body=payload,
        timeout=900,
    )
    if write_status != 200:
        raise RuntimeError(f"Draft write failed: {write_status} {str(response)[:400]}")
    read_status, readback = console.call(
        "GET", f"/console/api/apps/{BASE.UAPP_APP_ID}/workflows/draft", timeout=300
    )
    if read_status != 200 or BASE.canonical(readback["graph"]) != BASE.canonical(candidate):
        raise RuntimeError("Draft readback differs from candidate")
    report["applied_to_draft"] = True
    report["draft_readback_equal"] = True
    report["draft_hash_after"] = readback.get("hash")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--apply-draft", action="store_true")
    args = parser.parse_args()
    if args.dry_run == args.apply_draft:
        raise SystemExit("Choose exactly one of --dry-run or --apply-draft")
    if BASE.graph_md5() != BASE.BASE_GRAPH_MD5:
        raise RuntimeError("Published UAPP graph differs from the frozen TD24 base")
    candidate, report = BASE.build_candidate(BASE.published_graph())
    report["document"]["id"] = "UAPP_TD24_BUILD_v1.1"
    report["document"]["parent_builder"] = "UAPP_TD24_BUILD_v1.0.py"
    report["document"]["parent_builder_sha256"] = sha256_file(
        os.path.join(HERE, "UAPP_TD24_BUILD_v1.0.py")
    )
    report["document"]["nodes_source_sha256"] = sha256_file(
        os.path.join(HERE, "UAPP_TD24_NODES_v1.0.py")
    )
    if args.apply_draft:
        apply_draft(candidate, report)
    os.makedirs(EVIDENCE_DIR, exist_ok=True)
    output = os.path.join(EVIDENCE_DIR, "UAPP_TD24_BUILD_v1.1.json")
    with open(output, "x", encoding="utf-8") as handle:
        json.dump(report, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    logging.info("%s", json.dumps(report, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    raise SystemExit(main())
