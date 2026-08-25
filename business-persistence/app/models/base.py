import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


def new_uuid() -> uuid.UUID:
    return uuid.uuid4()


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def tz_datetime_column(**kwargs):
    """Every business datetime column must be TIMESTAMPTZ, never the bare
    Python ``datetime`` mapping (which Postgres stores as TIMESTAMP WITHOUT
    TIME ZONE and silently drops the offset). Use this everywhere instead of
    a bare ``mapped_column()`` for a datetime field.
    """
    return mapped_column(DateTime(timezone=True), **kwargs)


class UUIDPKMixin:
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=new_uuid
    )


class CreatedAtMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False
    )


class OptimisticVersionMixin:
    """Row-level optimistic concurrency token.

    Every mutating write must read this value, include it in the update's
    WHERE clause, and increment it. A write whose WHERE clause matches zero
    rows means someone else updated first -> caller must re-read and retry
    (or surface a 409 conflict), never silently last-write-wins.
    """

    row_version: Mapped[int] = mapped_column(default=1, nullable=False)
