#!/usr/bin/env python3
"""Deterministic UAPP upload-to-M2 material registration functions."""

from __future__ import annotations

import hashlib
import inspect
import json
from typing import Any


def _as_dict(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return dict(value)
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
        except (TypeError, ValueError):
            return {}
        return dict(parsed) if isinstance(parsed, dict) else {}
    model_dump = getattr(value, "model_dump", None)
    if callable(model_dump):
        parsed = model_dump()
        return dict(parsed) if isinstance(parsed, dict) else {}
    return {}


def _as_files(value: Any) -> list[dict[str, Any]]:
    parsed = value
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
        except (TypeError, ValueError):
            return []
    if not isinstance(parsed, list):
        return []
    return [_as_dict(item) for item in parsed]


def prepare_material(
    files: Any,
    material_text: str,
    workspace_id: str,
    account_id: str,
    task_id: str,
    actor_ref: str,
    previous_binding_json: str,
) -> dict[str, str]:
    text = (material_text or "").strip()
    file_rows = _as_files(files)
    empty = {
        "decision": "NONE",
        "request_body": "{}",
        "binding_seed": "{}",
        "idempotency_key": "",
        "file_hash": "",
        "file_name": "",
        "upload_id": "",
        "detail": "",
    }
    if not text and not file_rows:
        return empty
    if not text or len(file_rows) != 1:
        return {**empty, "decision": "INVALID", "detail": "UPLOAD_IDENTITY_INCOMPLETE"}
    file_row = file_rows[0]
    upload_id = str(
        file_row.get("related_id")
        or file_row.get("id")
        or file_row.get("file_id")
        or ""
    ).strip()
    file_name = str(file_row.get("filename") or file_row.get("name") or "").strip()
    if not upload_id or not file_name or not workspace_id or not account_id or not task_id or not actor_ref:
        return {**empty, "decision": "INVALID", "detail": "UPLOAD_SCOPE_INCOMPLETE"}
    file_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()
    idempotency_key = hashlib.sha256(
        f"{task_id}|{upload_id}|{file_hash}".encode("utf-8")
    ).hexdigest()
    previous = _as_dict(previous_binding_json)
    if (
        previous.get("idempotency_key") == idempotency_key
        and previous.get("material_id")
        and previous.get("task_id") == task_id
    ):
        return {
            **empty,
            "decision": "REUSE",
            "idempotency_key": idempotency_key,
            "file_hash": file_hash,
            "file_name": file_name,
            "upload_id": upload_id,
        }
    scope_ref = {
        "is_test": True,
        "is_simulated": True,
        "account_id": account_id,
        "task_id": task_id,
        "file_name": file_name,
        "dify_upload_id": upload_id,
        "extracted_text_sha256": file_hash,
        "idempotency_key": idempotency_key,
    }
    request = {
        "source": "founder_upload",
        "owner_ref": actor_ref,
        "analysis_authorized": True,
        "generation_authorized": True,
        "publish_authorized": False,
        "scope_ref": scope_ref,
        "content_ref": f"dify-upload:{upload_id}#sha256={file_hash}",
    }
    binding_seed = {
        **scope_ref,
        "workspace_id": workspace_id,
        "owner_ref": actor_ref,
        "content_ref": request["content_ref"],
        "publish_authorized": False,
    }
    return {
        "decision": "REGISTER",
        "request_body": json.dumps(request, ensure_ascii=False, sort_keys=True),
        "binding_seed": json.dumps(binding_seed, ensure_ascii=False, sort_keys=True),
        "idempotency_key": idempotency_key,
        "file_hash": file_hash,
        "file_name": file_name,
        "upload_id": upload_id,
        "detail": "",
    }


def parse_registration(raw: Any, status: Any, binding_seed_json: str) -> dict[str, str]:
    body = _as_dict(raw)
    seed = _as_dict(binding_seed_json)
    response_scope = body.get("scope_ref") if isinstance(body.get("scope_ref"), dict) else {}
    status_ok = str(status) in {"200", "201"}
    identity_ok = bool(body.get("id")) and body.get("workspace_id") == seed.get("workspace_id")
    scope_ok = (
        response_scope.get("task_id") == seed.get("task_id")
        and response_scope.get("account_id") == seed.get("account_id")
        and response_scope.get("idempotency_key") == seed.get("idempotency_key")
        and response_scope.get("extracted_text_sha256") == seed.get("extracted_text_sha256")
        and response_scope.get("dify_upload_id") == seed.get("dify_upload_id")
        and response_scope.get("is_test") is True
        and response_scope.get("is_simulated") is True
    )
    permissions_ok = (
        body.get("analysis_authorized") is True
        and body.get("generation_authorized") is True
        and body.get("publish_authorized") is False
    )
    ok = status_ok and identity_ok and scope_ok and permissions_ok
    binding = {
        **seed,
        "material_id": str(body.get("id") or "") if ok else "",
        "registration_status": str(status),
    }
    return {
        "ok": "true" if ok else "false",
        "material_id": str(body.get("id") or "") if ok else "",
        "binding_json": json.dumps(binding, ensure_ascii=False, sort_keys=True) if ok else "{}",
        "detail": "" if ok else "MATERIAL_REGISTRATION_NOT_CONFIRMED",
    }


_HEADER = "from __future__ import annotations\nimport hashlib\nimport json\nfrom typing import Any\n\n"
PREPARE_SRC: str = (
    _HEADER
    + inspect.getsource(_as_dict)
    + "\n"
    + inspect.getsource(_as_files)
    + "\n"
    + inspect.getsource(prepare_material)
    + "\n\ndef main(files, material_text, workspace_id, account_id, task_id, actor_ref, "
    "previous_binding_json):\n"
    "    return prepare_material(files, material_text, workspace_id, account_id, task_id, "
    "actor_ref, previous_binding_json)\n"
)
PARSE_SRC: str = (
    _HEADER
    + inspect.getsource(_as_dict)
    + "\n"
    + inspect.getsource(parse_registration)
    + "\n\ndef main(raw, status, binding_seed_json):\n"
    "    return parse_registration(raw, status, binding_seed_json)\n"
)

