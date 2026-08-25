import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, CreatedAtMixin, UUIDPKMixin


class PublishInstance(Base, UUIDPKMixin, CreatedAtMixin):
    """发布实例. Always points at one exact content_version -- there is no
    "publish the artifact" shortcut. is_test/is_simulated are real,
    independently-queryable columns (not a single overloaded status string)
    so evidence-tier queries can never accidentally merge real publishes
    with test/simulated ones by forgetting to filter a string value.
    """

    __tablename__ = "publish_instances"
    __table_args__ = (
        Index("ix_publish_instances_content_version_id", "content_version_id"),
        Index("ix_publish_instances_account_id", "account_id"),
    )

    content_version_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("content_versions.id"), nullable=False
    )
    account_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=False
    )
    platform: Mapped[str] = mapped_column(String(64), nullable=False)
    published_at: Mapped[datetime] = mapped_column(nullable=False)

    is_test: Mapped[bool] = mapped_column(default=False, nullable=False)
    is_simulated: Mapped[bool] = mapped_column(default=False, nullable=False)
    registered_by: Mapped[Optional[str]] = mapped_column(String(255))

    idempotency_key: Mapped[Optional[str]] = mapped_column(String(255), unique=True)


class FeedbackRecord(Base, UUIDPKMixin, CreatedAtMixin):
    """反馈. publish_instance_id is NOT NULL by design -- there is no code
    path that lets a draft/candidate/PRE/unpublished-FINAL version receive
    market effect. kind separates raw observation from interpretation from
    the adjust-or-not decision so M2 never collapses "what happened" into
    "what we think it means" into "what we'll do about it".
    """

    __tablename__ = "feedback_records"
    __table_args__ = (
        Index("ix_feedback_records_publish_instance_id", "publish_instance_id"),
    )

    publish_instance_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("publish_instances.id"), nullable=False
    )
    # observation | interpretation | decision
    kind: Mapped[str] = mapped_column(String(32), nullable=False)

    is_test: Mapped[bool] = mapped_column(default=False, nullable=False)
    is_simulated: Mapped[bool] = mapped_column(default=False, nullable=False)
    is_manual_entry: Mapped[bool] = mapped_column(default=False, nullable=False)
    is_pre_publish_review: Mapped[bool] = mapped_column(default=False, nullable=False)

    source: Mapped[Optional[str]] = mapped_column(String(255))
    observed_at: Mapped[Optional[datetime]] = mapped_column()
    window_start: Mapped[Optional[datetime]] = mapped_column()
    window_end: Mapped[Optional[datetime]] = mapped_column()
    goal_at_the_time: Mapped[Optional[str]] = mapped_column(String(1024))

    payload: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

    idempotency_key: Mapped[Optional[str]] = mapped_column(String(255), unique=True)
