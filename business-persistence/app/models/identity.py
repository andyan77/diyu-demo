import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import ForeignKey, Index, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, CreatedAtMixin, UUIDPKMixin


class User(Base, UUIDPKMixin, CreatedAtMixin):
    """A real, distinguishable person or service identity.

    external_ref is where the identity actually came from (e.g. a Dify
    end-user id, an operator account). We never invent users -- every row
    here must trace back to a real authenticated caller.
    """

    __tablename__ = "users"

    external_ref: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    display_name: Mapped[Optional[str]] = mapped_column(String(255))

    memberships: Mapped[list["WorkspaceMembership"]] = relationship(back_populates="user")


class Workspace(Base, UUIDPKMixin, CreatedAtMixin):
    """Isolation boundary. Every read/write elsewhere in the schema is scoped
    to exactly one workspace_id -- there is no cross-workspace query path.
    """

    __tablename__ = "workspaces"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    # free text, not a frozen enum: "personal" | "enterprise" today, more later
    kind: Mapped[str] = mapped_column(String(64), nullable=False, default="personal")

    memberships: Mapped[list["WorkspaceMembership"]] = relationship(
        back_populates="workspace"
    )


class WorkspaceMembership(Base, UUIDPKMixin, CreatedAtMixin):
    """A user's access relation to a workspace. A user may belong to several
    workspaces; every request must carry an explicit workspace_id and this
    table is the only place that grants access to it.
    """

    __tablename__ = "workspace_memberships"
    __table_args__ = (UniqueConstraint("user_id", "workspace_id", name="uq_membership_user_ws"),)

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("workspaces.id"), nullable=False
    )
    # free text: "owner" | "member" | ... -- not a physical enum
    role: Mapped[str] = mapped_column(String(64), nullable=False, default="member")

    user: Mapped["User"] = relationship(back_populates="memberships")
    workspace: Mapped["Workspace"] = relationship(back_populates="memberships")


class Subject(Base, UUIDPKMixin, CreatedAtMixin):
    """表达主体 -- the persona/voice a piece of content speaks as."""

    __tablename__ = "subjects"
    __table_args__ = (Index("ix_subjects_workspace_id", "workspace_id"),)

    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("workspaces.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    kind: Mapped[Optional[str]] = mapped_column(String(64))


class Account(Base, UUIDPKMixin, CreatedAtMixin):
    """单账号 -- one publishing account on one platform, owned by a workspace
    and (optionally) speaking as one subject.
    """

    __tablename__ = "accounts"
    __table_args__ = (
        UniqueConstraint("workspace_id", "platform", "handle", name="uq_account_platform_handle"),
        Index("ix_accounts_workspace_id", "workspace_id"),
    )

    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("workspaces.id"), nullable=False
    )
    subject_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("subjects.id")
    )
    platform: Mapped[str] = mapped_column(String(64), nullable=False)
    handle: Mapped[str] = mapped_column(String(255), nullable=False)
