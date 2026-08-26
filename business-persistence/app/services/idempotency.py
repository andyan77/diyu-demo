import hashlib
import json

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.infra import IdempotencyRecord


def request_hash(payload: dict) -> str:
    canonical = json.dumps(payload, sort_keys=True, default=str)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def check_or_reserve(db: Session, key: str, payload: dict) -> dict | None:
    """Look up an idempotency key.

    Returns the previously stored result if this exact (key, payload) was
    already handled -- the caller should return that immediately without
    redoing the write. Returns None if this is a fresh key -- the caller
    must call `store_result` once its write commits. Raises 409 if the key
    was reused with a *different* payload (a caller bug, never silently
    honored).
    """

    existing = db.get(IdempotencyRecord, key)
    if existing is None:
        return None
    if existing.request_hash != request_hash(payload):
        raise HTTPException(
            status_code=409,
            detail="idempotency_key reused with a different request body",
        )
    return existing.result_ref


def store_result(db: Session, key: str, payload: dict, result: dict) -> None:
    db.add(
        IdempotencyRecord(
            key=key,
            request_hash=request_hash(payload),
            result_ref=result,
        )
    )
