#!/usr/bin/env python3
"""Publish the frozen successor draft with a platform-valid version label."""

from __future__ import annotations

import importlib.util
import json
import logging
from pathlib import Path
from types import ModuleType

LOGGER = logging.getLogger(__name__)
HERE = Path(__file__).resolve().parent
UAPP = HERE.parent
OUTPUT = (
    UAPP
    / "evidence"
    / "stages"
    / "uapp_s5_inline_artifact_successor_v1_0"
    / "build"
    / "UAPP_S5_INLINE_ARTIFACT_SUCCESSOR_BUILD_v1.1_PUBLISHED.json"
)


def load_module(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


V10 = load_module(
    "uapp_s5_inline_successor_build_v10",
    HERE / "UAPP_S5_INLINE_ARTIFACT_SUCCESSOR_BUILD_v1.0.py",
)


def main() -> int:
    if V10.BASE.graph_md5() != V10.BASE_GRAPH_MD5:
        raise RuntimeError("Published UAPP differs from the frozen predecessor")
    if int(V10.BASE.psql("select count(*) from workflow_runs where status='running';")) != 0:
        raise RuntimeError("Active workflows exist")
    candidate, report = V10.patch_graph(V10.BASE.published_graph())
    console = V10.BASE.DC.Console(env=V10.BASE.DC.load_env(V10.BASE.ENV_FILE))
    draft = V10.BASE.console_call(
        console, "GET", f"/console/api/apps/{V10.BASE.UAPP_APP_ID}/workflows/draft"
    )
    if V10.BASE.canonical(draft["graph"]) != V10.BASE.canonical(candidate):
        raise RuntimeError("Frozen successor draft differs from the candidate")
    response = V10.BASE.console_call(
        console,
        "POST",
        f"/console/api/apps/{V10.BASE.UAPP_APP_ID}/workflows/publish",
        {
            "marked_name": "uapp-inline-succ-v1",
            "marked_comment": "same-source companion normalization",
        },
    )
    current = V10.BASE.published_graph()
    if V10.BASE.canonical(current) != V10.BASE.canonical(candidate):
        raise RuntimeError("Published graph differs from the frozen successor")
    report["document"]["id"] = "UAPP_S5_INLINE_ARTIFACT_SUCCESSOR_BUILD_v1.1"
    report["document"]["parent"] = "UAPP_S5_INLINE_ARTIFACT_SUCCESSOR_BUILD_v1.0"
    report.update(
        {
            "published": True,
            "publish_response": response,
            "published_graph_md5": V10.BASE.graph_md5(),
            "published_graph_canonical_sha256": V10.BASE.sha256_text(
                V10.BASE.canonical(current)
            ),
            "publication_label": "uapp-inline-succ-v1",
            "predecessor_failure": "HTTP_400_MARKED_NAME_TOO_LONG",
        }
    )
    if OUTPUT.exists():
        raise FileExistsError(f"Refusing to overwrite {OUTPUT}")
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    LOGGER.info("PUBLISHED %s", OUTPUT)
    return 0


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    raise SystemExit(main())
