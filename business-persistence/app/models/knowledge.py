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

    Workspace membership (access control) and permission_status (source
    usage permission) are deliberately two separate gates -- being a
    workspace member never implies a right to use an unknown-permission
    observation as current, and "viewable" never implies "publishable" (see
    usage_limits). permission_status defaults to "unknown", never "allowed":
    a missing permission decision must never be silently treated as one.
    account_id/applicable_task_id/applicable_period_* narrow which
    account/task/time window the observation actually applies to,
    independent from applicable_track (free-text track/object) and scope_ref
    (open-ended extra scope) which already existed. evidence_digest is
    caller-supplied (M2 never computes it, matching content_hash elsewhere)
    -- the row's own id is the citable evidence identity.

    Idempotency is enforced by a PARTIAL unique index on
    (workspace_id, account_id, idempotency_key) WHERE idempotency_key IS
    NOT NULL, with NULLS NOT DISTINCT on that subset (Postgres 15+):
    this repo already has one documented incident (see c3f8b2e6d0a4) of an
    idempotency key scoped by workspace alone letting two different
    accounts collide on the same key string and silently return each
    other's row -- plain NULL-distinct SQL semantics would reopen that
    exact class of bug for two different real accounts sharing a key (NULL
    is never equal to a concrete value, so that half is already safe), but
    would also let two *workspace-wide* (account_id IS NULL) creates with
    the same key silently create duplicates instead of deduping, since
    plain SQL treats NULL != NULL. NULLS NOT DISTINCT closes that second
    gap. The index must be PARTIAL (idempotency_key IS NOT NULL only) --
    applying NULLS NOT DISTINCT across the whole table would instead make
    every (workspace_id, account_id) pair's many legitimate no-key rows
    collide with each other, since idempotency_key is also NULL for all of
    them; only rows that actually supply a key need this uniqueness at all.
    """

    __tablename__ = "market_observations"
    __table_args__ = (
        Index("ix_market_observations_workspace_id", "workspace_id"),
        Index("ix_market_observations_workspace_account", "workspace_id", "account_id"),
        Index(
            "uq_market_observation_workspace_account_idempotency",
            "workspace_id",
            "account_id",
            "idempotency_key",
            unique=True,
            postgresql_where=text("idempotency_key IS NOT NULL"),
            postgresql_nulls_not_distinct=True,
        ),
    )

    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("workspaces.id"), nullable=False
    )
    source: Mapped[Optional[str]] = mapped_column(String(255))
    source_type: Mapped[Optional[str]] = mapped_column(String(64))
    source_reference: Mapped[Optional[str]] = mapped_column(String(1024))
    source_provider: Mapped[Optional[str]] = mapped_column(String(255))
    platform: Mapped[Optional[str]] = mapped_column(String(64))
    collected_at = tz_datetime_column(nullable=False)
    applicable_track: Mapped[Optional[str]] = mapped_column(String(255))
    account_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("accounts.id")
    )
    applicable_task_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tasks.id")
    )
    applicable_period_start = tz_datetime_column(nullable=True)
    applicable_period_end = tz_datetime_column(nullable=True)
    scope_ref: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    mechanism_summary: Mapped[Optional[str]] = mapped_column(String(4096))
    # raw | analysis | homogeneous_judgment
    layer: Mapped[str] = mapped_column(String(32), nullable=False, default="raw")
    valid_until = tz_datetime_column(nullable=True)

    # allowed | unknown | missing | denied | restricted -- see R-03/R-04.
    # Default "unknown", never "allowed": absence of a permission decision
    # must never be treated as one.
    permission_status: Mapped[str] = mapped_column(String(32), nullable=False, default="unknown")
    permission_basis: Mapped[Optional[dict]] = mapped_column(JSONB)
    usage_limits: Mapped[Optional[dict]] = mapped_column(JSONB)
    permission_confirmed_by: Mapped[Optional[str]] = mapped_column(String(255))
    permission_confirmed_at = tz_datetime_column(nullable=True)

    evidence_digest: Mapped[Optional[str]] = mapped_column(String(64))
    idempotency_key: Mapped[Optional[str]] = mapped_column(String(255))


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
