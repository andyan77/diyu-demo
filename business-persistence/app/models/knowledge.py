import uuid
from typing import Optional

from sqlalchemy import ForeignKey, Index, String, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, CreatedAtMixin, OptimisticVersionMixin, UUIDPKMixin, tz_datetime_column


class MarketObservation(Base, UUIDPKMixin, CreatedAtMixin):
    """市场观察. layer distinguishes raw capture from analysis from a
    "everyone already says this" homogeneous judgment -- callers must know
    which they're looking at before treating it as evidence. valid_until
    lets a stale observation be recognized as stale instead of silently
    treated as current.
    """

    __tablename__ = "market_observations"
    __table_args__ = (Index("ix_market_observations_workspace_id", "workspace_id"),)

    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("workspaces.id"), nullable=False
    )
    source: Mapped[Optional[str]] = mapped_column(String(255))
    platform: Mapped[Optional[str]] = mapped_column(String(64))
    collected_at = tz_datetime_column(nullable=False)
    applicable_track: Mapped[Optional[str]] = mapped_column(String(255))
    scope_ref: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    mechanism_summary: Mapped[Optional[str]] = mapped_column(String(4096))
    # raw | analysis | homogeneous_judgment
    layer: Mapped[str] = mapped_column(String(32), nullable=False, default="raw")
    valid_until = tz_datetime_column(nullable=True)


class Playbook(Base, UUIDPKMixin, CreatedAtMixin, OptimisticVersionMixin):
    """打法 -- a pattern verified as repeatable across multiple content
    tasks. M2 only stores/versions/projects these; the professional
    definition, proposal, revision, and retirement judgment belongs to
    M3/the user, not to M2. Field values are deliberately free text, not a
    frozen physical enum of "known playbooks".
    """

    __tablename__ = "playbooks"
    __table_args__ = (
        Index("ix_playbooks_workspace_id", "workspace_id"),
        Index(
            "uq_playbook_current",
            "workspace_id",
            "name",
            unique=True,
            postgresql_where=text("is_current"),
        ),
        UniqueConstraint(
            "workspace_id", "idempotency_key", name="uq_playbook_workspace_idempotency"
        ),
    )

    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("workspaces.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    version_no: Mapped[int] = mapped_column(nullable=False, default=1)
    is_current: Mapped[bool] = mapped_column(default=True, nullable=False)
    proposed_by: Mapped[Optional[str]] = mapped_column(String(255))
    scope_ref: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    observation_status: Mapped[Optional[str]] = mapped_column(String(1024))
    rationale: Mapped[Optional[str]] = mapped_column(String(4096))
    idempotency_key: Mapped[Optional[str]] = mapped_column(String(255))

    supersedes_playbook_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("playbooks.id")
    )
    superseded_at = tz_datetime_column(nullable=True)
