import uuid
from typing import Optional

from sqlalchemy import ForeignKey, Index, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, CreatedAtMixin, UUIDPKMixin, tz_datetime_column


class PublishInstance(Base, UUIDPKMixin, CreatedAtMixin):
    """发布实例. Always points at one exact content_version -- there is no
    "publish the artifact" shortcut. is_test/is_simulated are real,
    independently-queryable columns (not a single overloaded status string)
    so evidence-tier queries can never accidentally merge real publishes
    with test/simulated ones by forgetting to filter a string value.

    workspace_id is denormalized here (derivable via
    content_version -> artifact -> task) purely so idempotency_key can be
    scoped per-workspace at the database level, the same way every other
    idempotent table in this schema is scoped.
    """

    __tablename__ = "publish_instances"
    __table_args__ = (
        Index("ix_publish_instances_content_version_id", "content_version_id"),
        Index("ix_publish_instances_account_id", "account_id"),
        Index("ix_publish_instances_workspace_id", "workspace_id"),
        UniqueConstraint(
            "workspace_id", "idempotency_key", name="uq_publish_instance_workspace_idempotency"
        ),
    )

    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("workspaces.id"), nullable=False
    )
    content_version_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("content_versions.id"), nullable=False
    )
    account_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=False
    )
    platform: Mapped[str] = mapped_column(String(64), nullable=False)
    published_at = tz_datetime_column(nullable=False)

    is_test: Mapped[bool] = mapped_column(default=False, nullable=False)
    is_simulated: Mapped[bool] = mapped_column(default=False, nullable=False)
    registered_by: Mapped[Optional[str]] = mapped_column(String(255))

    idempotency_key: Mapped[Optional[str]] = mapped_column(String(255))


class FeedbackRecord(Base, UUIDPKMixin, CreatedAtMixin):
    """反馈. Binds to exactly one of publish_instance_id (post-publish
    feedback -- the common case) or content_version_id (发布前人工评价, the
    one identity §5.6 names that has no publish instance yet). Application
    code (app/api/publish.py) enforces "exactly one, matching
    is_pre_publish_review" -- there is no code path that lets a
    draft/candidate/unpublished-FINAL version receive *post-publish* market
    effect, because that path always requires a real publish_instance_id.
    kind separates raw observation from interpretation from the
    adjust-or-not decision so M2 never collapses "what happened" into "what
    we think it means" into "what we'll do about it".
    """

    __tablename__ = "feedback_records"
    __table_args__ = (
        Index("ix_feedback_records_publish_instance_id", "publish_instance_id"),
        Index("ix_feedback_records_content_version_id", "content_version_id"),
        Index("ix_feedback_records_workspace_id", "workspace_id"),
        UniqueConstraint(
            "workspace_id", "idempotency_key", name="uq_feedback_workspace_idempotency"
        ),
    )

    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("workspaces.id"), nullable=False
    )
    publish_instance_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("publish_instances.id")
    )
    # only set for is_pre_publish_review=True rows (§5.6 发布前人工评价)
    content_version_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("content_versions.id")
    )
    # observation | interpretation | decision
    kind: Mapped[str] = mapped_column(String(32), nullable=False)

    is_test: Mapped[bool] = mapped_column(default=False, nullable=False)
    is_simulated: Mapped[bool] = mapped_column(default=False, nullable=False)
    is_manual_entry: Mapped[bool] = mapped_column(default=False, nullable=False)
    is_pre_publish_review: Mapped[bool] = mapped_column(default=False, nullable=False)

    source: Mapped[Optional[str]] = mapped_column(String(255))
    observed_at = tz_datetime_column(nullable=True)
    window_start = tz_datetime_column(nullable=True)
    window_end = tz_datetime_column(nullable=True)
    goal_at_the_time: Mapped[Optional[str]] = mapped_column(String(1024))

    payload: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

    idempotency_key: Mapped[Optional[str]] = mapped_column(String(255))
