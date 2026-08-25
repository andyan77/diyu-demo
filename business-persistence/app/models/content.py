import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import ForeignKey, Index, String, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, CreatedAtMixin, OptimisticVersionMixin, UUIDPKMixin


class Task(Base, UUIDPKMixin, CreatedAtMixin, OptimisticVersionMixin):
    """内容任务."""

    __tablename__ = "tasks"
    __table_args__ = (
        Index("ix_tasks_workspace_id", "workspace_id"),
        Index("ix_tasks_cycle_id", "cycle_id"),
    )

    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("workspaces.id"), nullable=False
    )
    account_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("accounts.id")
    )
    cycle_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cycles.id")
    )
    kind: Mapped[Optional[str]] = mapped_column(String(64))
    # free text: "open" | "in_progress" | "done" | ... -- not a physical enum;
    # milestones like "generated/selected/produced/published/observed" are
    # NOT collapsed into this single field, see ContentVersion/PublishInstance
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="open")
    # caller-supplied idempotency key for task creation; a retry with the
    # same key returns the existing task instead of creating a duplicate
    idempotency_key: Mapped[Optional[str]] = mapped_column(String(255), unique=True)


class TaskSnapshot(Base, UUIDPKMixin, CreatedAtMixin):
    """任务上下文快照 -- persisted context for one task, at one point in time.

    The five frozen information dimensions (shared contract §一) are kept as
    real columns, not folded into payload, so they can be queried/tested
    without parsing JSON: info_nature / info_source / confirmation_status /
    scope / availability_status. payload carries the actual content
    (原话/资料引用/附带诉求 etc.) and is intentionally schema-light because
    its shape is task-kind-specific and not M2's to freeze.
    """

    __tablename__ = "task_snapshots"
    __table_args__ = (Index("ix_task_snapshots_task_id", "task_id"),)

    task_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tasks.id"), nullable=False
    )
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

    # dimension 1: fact | preference | reference | system_judgment
    info_nature: Mapped[str] = mapped_column(String(32), nullable=False)
    # dimension 2: where this came from (user message id, upstream artifact, etc.)
    source: Mapped[Optional[str]] = mapped_column(String(255))
    # dimension 3: confirmed | inferred | superseded | withdrawn
    confirmation_status: Mapped[str] = mapped_column(String(32), nullable=False, default="confirmed")
    # dimension 4: JSON so it can name workspace/account/task/time-window scope
    scope: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    # dimension 5: available | expired | withdrawn | unknown
    availability_status: Mapped[str] = mapped_column(String(32), nullable=False, default="available")

    idempotency_key: Mapped[Optional[str]] = mapped_column(String(255), unique=True)


class Material(Base, UUIDPKMixin, CreatedAtMixin):
    """资料/素材. Authorization is tracked per-action (analysis/generation/
    publish) because a material can be legal to analyze but not to publish
    from, etc. withdrawn_at is the single source of truth for withdrawal --
    once set, future projections must stop returning this material's content.
    """

    __tablename__ = "materials"
    __table_args__ = (Index("ix_materials_workspace_id", "workspace_id"),)

    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("workspaces.id"), nullable=False
    )
    source: Mapped[Optional[str]] = mapped_column(String(255))
    owner_ref: Mapped[Optional[str]] = mapped_column(String(255))
    analysis_authorized: Mapped[bool] = mapped_column(default=False, nullable=False)
    generation_authorized: Mapped[bool] = mapped_column(default=False, nullable=False)
    publish_authorized: Mapped[bool] = mapped_column(default=False, nullable=False)
    scope_ref: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    content_ref: Mapped[Optional[str]] = mapped_column(String(1024))

    withdrawn_at: Mapped[Optional[datetime]] = mapped_column()
    withdrawn_by: Mapped[Optional[str]] = mapped_column(String(255))


class Artifact(Base, UUIDPKMixin, CreatedAtMixin):
    """决策/生产产物. parent_artifact_id chains revisions; content_hash is the
    cheap way to tell "substantive change" from "wording/typo" without a
    full dependency graph.
    """

    __tablename__ = "artifacts"
    __table_args__ = (Index("ix_artifacts_task_id", "task_id"),)

    task_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tasks.id"), nullable=False
    )
    kind: Mapped[Optional[str]] = mapped_column(String(64))
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    parent_artifact_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("artifacts.id")
    )


class ContentVersionMaterialDependency(Base):
    """Which materials a specific content_version's content actually depends
    on -- the minimal edge needed to cascade a withdrawal into "this
    unpublished version just lost a dependency, needs re-check" without a
    full event sourcing / dependency-graph platform.

    Keyed by content_version_id, not artifact_id: two versions of the same
    artifact are independent candidates that may depend on different (or
    overlapping) materials, and invalidation must only ever hit the specific
    version that actually used the withdrawn material -- not every sibling
    version of the same artifact.
    """

    __tablename__ = "content_version_material_dependencies"
    __table_args__ = (
        Index("ix_content_version_material_dependencies_material_id", "material_id"),
    )

    content_version_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("content_versions.id"), primary_key=True
    )
    material_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("materials.id"), primary_key=True
    )


class ContentVersion(Base, UUIDPKMixin, CreatedAtMixin, OptimisticVersionMixin):
    """内容版本. Exactly one row per artifact may have is_current=True at a
    time (enforced by a partial unique index in the migration, plus the
    atomic promote_version service). Promotion never deletes or overwrites a
    prior current row -- it flips is_current off there and on here in one
    transaction, so history stays fully readable.
    """

    __tablename__ = "content_versions"
    __table_args__ = (
        UniqueConstraint("artifact_id", "version_no", name="uq_version_artifact_no"),
        Index("ix_content_versions_artifact_id", "artifact_id"),
        Index(
            "uq_content_version_current",
            "artifact_id",
            unique=True,
            postgresql_where=text("is_current"),
        ),
    )

    artifact_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("artifacts.id"), nullable=False
    )
    version_no: Mapped[int] = mapped_column(nullable=False)
    is_current: Mapped[bool] = mapped_column(default=False, nullable=False)
    content_ref: Mapped[Optional[str]] = mapped_column(String(1024))
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False)

    # who/what proposed this candidate -- distinct from who promoted it
    produced_by: Mapped[Optional[str]] = mapped_column(String(255))
    # human/user decision that promoted this version to current; a model's
    # own self-evaluation is never a valid promoted_by actor for this field
    promoted_by: Mapped[Optional[str]] = mapped_column(String(255))
    promoted_at: Mapped[Optional[datetime]] = mapped_column()
    superseded_at: Mapped[Optional[datetime]] = mapped_column()

    # milestones are additive flags, not one exclusive status:
    # "generated/selected/produced/published/observed" can all be true at once
    was_selected: Mapped[bool] = mapped_column(default=False, nullable=False)
    was_produced: Mapped[bool] = mapped_column(default=False, nullable=False)

    # cascading invalidation target: set when a material this version's
    # artifact depends on is withdrawn. Only ever set on a version that has
    # no publish_instances yet -- a published version is history and is
    # never invalidated by a later withdrawal.
    invalidated_at: Mapped[Optional[datetime]] = mapped_column()
    invalidation_reason: Mapped[Optional[str]] = mapped_column(String(1024))
