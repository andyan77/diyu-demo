#!/usr/bin/env python3
"""Publish the Gate-bound TD-UAPP-24 candidate to the existing UAPP only."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import logging
import os
from types import ModuleType
from typing import Any

HERE = os.path.dirname(os.path.abspath(__file__))
UAPP_ROOT = os.path.abspath(os.path.join(HERE, ".."))
GATE_PATH = os.path.join(UAPP_ROOT, "stages", "UAPP_TD24_GATE_v1.0.json")
OUTPUT_PATH = os.path.join(
    UAPP_ROOT,
    "evidence",
    "stages",
    "uapp_td24",
    "UAPP_TD24_PUBLISH_v1.0.json",
)


def load_module(name: str, path: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


BUILD = load_module("uapp_td24_build_v11", os.path.join(HERE, "UAPP_TD24_BUILD_v1.1.py"))
BASE = BUILD.BASE
OLD_RUN = load_module("uapp_correction_run", os.path.join(HERE, "UAPP_CORRECTION_RUN_v1.0.py"))


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def sha256_file(path: str) -> str:
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


def call_or_raise(
    console: Any,
    method: str,
    path: str,
    body: dict[str, Any] | None = None,
) -> dict[str, Any]:
    status, response = console.call(method, path, body=body, timeout=900)
    if status not in (200, 201):
        raise RuntimeError(f"{method} {path} failed: {status} {str(response)[:500]}")
    if not isinstance(response, dict):
        raise RuntimeError(f"{method} {path} returned a non-object response")
    return response


def main() -> int:
    if os.path.exists(OUTPUT_PATH):
        raise RuntimeError(f"Refusing to overwrite publication evidence: {OUTPUT_PATH}")
    with open(GATE_PATH, encoding="utf-8") as handle:
        gate = json.load(handle)

    candidate, build = BASE.build_candidate(BASE.published_graph())
    candidate_sha256 = sha256_text(canonical(candidate))
    expected = gate["candidate"]["UAPP"]
    if BASE.graph_md5() != gate["base"]["UAPP"]["graph_md5"]:
        raise RuntimeError("Published UAPP no longer matches the frozen base")
    if candidate_sha256 != expected["graph_canonical_sha256"]:
        raise RuntimeError("Rebuilt candidate differs from the frozen Gate")
    if int(BASE.psql("select count(*) from workflow_runs where status='running';")) != 0:
        raise RuntimeError("Active workflows exist before publication")

    before = OLD_RUN.protected_apps()
    for name, graph_md5 in gate["protected_surface_before"]["graph_md5"].items():
        if before[name]["graph_md5"] != graph_md5:
            raise RuntimeError(f"Protected app drifted before publication: {name}")

    console = BASE.DC.Console(env=BASE.DC.load_env(BASE.ENV_FILE))
    status, draft = console.call(
        "GET", f"/console/api/apps/{BASE.UAPP_APP_ID}/workflows/draft", timeout=300
    )
    if status != 200 or not isinstance(draft, dict):
        raise RuntimeError(f"Draft read failed: {status} {str(draft)[:500]}")
    draft_payload = {
        "graph": candidate,
        "features": draft.get("features") or {},
        "hash": draft.get("hash"),
        "environment_variables": draft.get("environment_variables") or [],
        "conversation_variables": draft.get("conversation_variables") or [],
    }
    call_or_raise(
        console,
        "POST",
        f"/console/api/apps/{BASE.UAPP_APP_ID}/workflows/draft",
        draft_payload,
    )
    readback = call_or_raise(
        console,
        "GET",
        f"/console/api/apps/{BASE.UAPP_APP_ID}/workflows/draft",
    )
    if sha256_text(canonical(readback["graph"])) != candidate_sha256:
        raise RuntimeError("Draft readback differs from the frozen candidate")

    publish_response = call_or_raise(
        console,
        "POST",
        f"/console/api/apps/{BASE.UAPP_APP_ID}/workflows/publish",
        {
            "marked_name": "uapp-td24-v10",
            "marked_comment": "TD-UAPP-24 frozen targeted verification candidate",
        },
    )
    published = BASE.published_graph()
    published_sha256 = sha256_text(canonical(published))
    if published_sha256 != candidate_sha256:
        raise RuntimeError("Published UAPP differs from the frozen candidate")
    if int(BASE.psql("select count(*) from workflow_runs where status='running';")) != 0:
        raise RuntimeError("Active workflows exist after publication")

    after = OLD_RUN.protected_apps()
    for name, graph_md5 in gate["protected_surface_after"]["graph_md5"].items():
        if after[name]["graph_md5"] != graph_md5:
            raise RuntimeError(f"Protected app drifted during publication: {name}")

    evidence = {
        "document": {
            "id": "UAPP_TD24_PUBLISH_v1.0",
            "task_id": "DIYU-V1-UNIFIED-DIFY-APPLICATION-001",
            "gate_sha256": sha256_file(GATE_PATH),
            "publisher_sha256": sha256_file(__file__),
        },
        "candidate": {
            "graph_canonical_sha256": candidate_sha256,
            "node_count": build["node_count"],
            "edge_count": build["edge_count"],
        },
        "before": before,
        "draft_hash_after": readback.get("hash"),
        "publish_response": publish_response,
        "published": {
            "graph_md5": BASE.graph_md5(),
            "graph_canonical_sha256": published_sha256,
            "app": after["UAPP"],
        },
        "after": after,
        "protected_surface_unchanged": all(
            after[name]["graph_md5"] == graph_md5
            for name, graph_md5 in gate["protected_surface_after"]["graph_md5"].items()
        ),
    }
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "x", encoding="utf-8") as handle:
        json.dump(evidence, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    logging.info(
        "published graph_sha256=%s graph_md5=%s",
        published_sha256,
        evidence["published"]["graph_md5"],
    )
    return 0


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    raise SystemExit(main())
