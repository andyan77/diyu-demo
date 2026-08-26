import uuid
from typing import Optional

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, OptimisticVersionMixin, UUIDPKMixin, tz_datetime_column, utcnow


class IdempotencyRecord(Base):
    """Generic idempotency ledger for write endpoints whose effect is a
    *mutation* rather than a new row with its own idempotency_key column
    (e.g. version promotion, campaign-override end/cancel). A retry with the
    same key and the same request body returns the stored result instead of
    re-executing; a retry with the same key but a *different* body is a
    caller bug and must be rejected, not silently applied. Used by
    promote_content_version and end_campaign_override in app/api/.
    """

    __tablename__ = "idempotency_records"

    key: Mapped[str] = mapped_column(String(255), primary_key=True)
    request_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    result_ref: Mapped[dict] = mapped_column(JSONB, nullable=False)
    created_at = tz_datetime_column(default=utcnow, nullable=False)


class TaskRunState(Base, UUIDPKMixin, OptimisticVersionMixin):
    """Minimal recovery checkpoint per task -- not a full event-sourcing
    platform. Records the last step that actually committed, the step that
    failed (if any), and what side effects are already known to have
    happened, so a resume never re-runs an expensive already-succeeded step
    and never claims a side effect happened when it didn't.

    Updates are a MERGE, not a replace: app/api/tasks.py's upsert_run_state
    only overwrites fields the caller actually sent (Pydantic
    ``exclude_unset``) and unions new side_effects keys into the existing
    dict, so a partial update recording only a new failed_step can never
    erase a previously-recorded successful step or its side effects.
    """

    __tablename__ = "task_run_states"

    task_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tasks.id"), nullable=False, unique=True
    )
    last_success_step: Mapped[Optional[str]] = mapped_column(String(255))
    failed_step: Mapped[Optional[str]] = mapped_column(String(255))
    resumable_from: Mapped[Optional[str]] = mapped_column(String(255))
    side_effects: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    created_at = tz_datetime_column(default=utcnow, nullable=False)
    updated_at = tz_datetime_column(default=utcnow, onupdate=utcnow, nullable=False)
