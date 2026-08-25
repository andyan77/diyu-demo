import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, CreatedAtMixin, UUIDPKMixin, utcnow


class IdempotencyRecord(Base):
    """Generic idempotency ledger for write endpoints whose effect is a
    *mutation* rather than a new row with its own idempotency_key column
    (e.g. version promotion, campaign-override end/cancel). A retry with the
    same key and the same request body returns the stored result instead of
    re-executing; a retry with the same key but a *different* body is a
    caller bug and must be rejected, not silently applied.
    """

    __tablename__ = "idempotency_records"

    key: Mapped[str] = mapped_column(String(255), primary_key=True)
    request_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    result_ref: Mapped[dict] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=utcnow, nullable=False)


class TaskRunState(Base, UUIDPKMixin):
    """Minimal recovery checkpoint per task -- not a full event-sourcing
    platform. Records the last step that actually committed, the step that
    failed (if any), and what side effects are already known to have
    happened, so a resume never re-runs an expensive already-succeeded step
    and never claims a side effect happened when it didn't.
    """

    __tablename__ = "task_run_states"

    task_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tasks.id"), nullable=False, unique=True
    )
    last_success_step: Mapped[Optional[str]] = mapped_column(String(255))
    failed_step: Mapped[Optional[str]] = mapped_column(String(255))
    resumable_from: Mapped[Optional[str]] = mapped_column(String(255))
    side_effects: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(default=utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        default=utcnow, onupdate=utcnow, nullable=False
    )
