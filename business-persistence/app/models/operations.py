import uuid
from typing import Optional

from sqlalchemy import ForeignKey, Index, Numeric, String, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, CreatedAtMixin, OptimisticVersionMixin, UUIDPKMixin, tz_datetime_column


class Cycle(Base, UUIDPKMixin, CreatedAtMixin, OptimisticVersionMixin):
    """运营周期. History is kept by chaining versions through
    supersedes_cycle_id rather than mutating rows in place -- superseded rows
    stay readable forever, `is_current` marks the one active baseline.

    Capacity is deliberately kept three-way and each number carries its own
    provenance in *_source: baseline (team/账号能力上限), actual (this
    cycle's real available capacity), expected (what the user asked for).
    M2 stores and projects these; it never decides to cut, delay, or
    reallocate -- that's M3/user territory.
    """

    __tablename__ = "cycles"
    __table_args__ = (
        Index("ix_cycles_workspace_id", "workspace_id"),
        Index("ix_cycles_account_id", "account_id"),
        Index(
            "uq_cycle_current", "account_id", unique=True, postgresql_where=text("is_current")
        ),
        UniqueConstraint(
            "workspace_id", "idempotency_key", name="uq_cycle_workspace_idempotency"
        ),
    )

    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("workspaces.id"), nullable=False
    )
    account_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=False
    )
    label: Mapped[str] = mapped_column(String(255), nullable=False)
    start_at = tz_datetime_column(nullable=False)
    end_at = tz_datetime_column(nullable=True)
    idempotency_key: Mapped[Optional[str]] = mapped_column(String(255))

    baseline_capacity: Mapped[Optional[int]] = mapped_column(Numeric)
    baseline_capacity_source: Mapped[Optional[str]] = mapped_column(String(255))
    actual_capacity: Mapped[Optional[int]] = mapped_column(Numeric)
    actual_capacity_source: Mapped[Optional[str]] = mapped_column(String(255))
    expected_publish_count: Mapped[Optional[int]] = mapped_column(Numeric)
    expected_publish_count_source: Mapped[Optional[str]] = mapped_column(String(255))

    is_current: Mapped[bool] = mapped_column(default=True, nullable=False)
    supersedes_cycle_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cycles.id")
    )


class CampaignOverride(Base, UUIDPKMixin, CreatedAtMixin, OptimisticVersionMixin):
    """Campaign as a time/scope-bounded override layer on top of a cycle.
    Only occupies the content positions named in targeted_positions; every
    other position in the cycle keeps running on the cycle baseline. When it
    ends/cancels, the projection falls back to whatever cycle baseline is
    *currently* valid -- not a frozen snapshot from override-start time.
    """

    __tablename__ = "campaign_overrides"
    __table_args__ = (
        Index("ix_campaign_overrides_workspace_id", "workspace_id"),
        Index("ix_campaign_overrides_cycle_id", "cycle_id"),
    )

    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("workspaces.id"), nullable=False
    )
    account_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=False
    )
    cycle_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cycles.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    scope_start = tz_datetime_column(nullable=False)
    scope_end = tz_datetime_column(nullable=True)
    targeted_positions: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    rationale: Mapped[Optional[str]] = mapped_column(String)

    # free text: "active" | "ended" | "cancelled" -- not a physical enum
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="active")
    ended_at = tz_datetime_column(nullable=True)
