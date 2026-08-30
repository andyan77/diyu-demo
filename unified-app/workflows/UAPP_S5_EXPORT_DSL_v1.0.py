#!/usr/bin/env python3
"""Export the current published UAPP graph as a credential-free evidence DSL."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import re
from types import ModuleType
from typing import Any

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
UAPP_ROOT = os.path.abspath(os.path.join(HERE, ".."))
REPO = os.path.abspath(os.path.join(UAPP_ROOT, ".."))
OUTPUT = os.path.join(UAPP_ROOT, "dsl", "UAPP_S5_FINAL_CANDIDATE_v1.0.yml")
APP_ID = "85c01f85-a081-43e9-ab09-9993289cc200"


def load_module(name: str, path: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


BASE = load_module("uapp_s5_export_base", os.path.join(HERE, "UAAB_SUCCESSOR_RUN_v1.2.py"))


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def main() -> int:
    app = BASE.app_state(APP_ID)
    graph = json.loads(BASE.psql(
        "select w.graph from workflows w join apps a on a.workflow_id=w.id "
        f"where a.id='{APP_ID}';"
    ))
    canonical = json.dumps(graph, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    document: dict[str, Any] = {
        "app": {
            "mode": "advanced-chat",
            "name": "笛语 V1 统一应用｜S5 最终候选",
            "description": "Current published graph exported for S5 technical acceptance evidence.",
        },
        "evidence_binding": {
            "app_id": app["app_id"],
            "workflow_id": app["workflow_id"],
            "published_version": str(app["version"]),
            "graph_md5": app["graph_md5"],
            "graph_canonical_sha256": sha256_text(canonical),
        },
        "workflow": {"graph": graph},
    }
    text = yaml.safe_dump(document, allow_unicode=True, sort_keys=True, default_flow_style=False)
    secret_patterns = {
        "bearer_token": r"Bearer\s+[A-Za-z0-9._-]{12,}",
        "openai_style_key": r"\bsk-[A-Za-z0-9_-]{12,}",
        "private_key": r"BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY",
        "password_assignment": r"(?im)^\s*password\s*:\s*[^\s'\"]+",
        "api_key_assignment": r"(?im)^\s*api[_-]?key\s*:\s*[^\s'\"]+",
    }
    hits = [name for name, pattern in secret_patterns.items() if re.search(pattern, text)]
    if hits:
        raise RuntimeError(f"Credential scan failed: {hits}")
    os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
    with open(OUTPUT, "x", encoding="utf-8") as handle:
        handle.write(text)
    print(json.dumps({"path": os.path.relpath(OUTPUT, REPO), "sha256": sha256_text(text), "credential_scan_hits": hits}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
