import uuid
from dataclasses import dataclass

from fastapi import Depends, Header, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.identity import User, Workspace, WorkspaceMembership


def get_session(db: Session = Depends(get_db)) -> Session:
    return db


@dataclass
class MembershipContext:
    workspace: Workspace
    user: User
    role: str


def require_membership(
    workspace_id: uuid.UUID,
    db: Session = Depends(get_db),
    x_actor_ref: str | None = Header(default=None, alias="X-Actor-Ref"),
) -> MembershipContext:
    """The single choke point every workspace-scoped path goes through.

    Checking that workspace_id merely *exists* is not isolation -- a caller
    who has ever seen any workspace's UUID (they're returned in every API
    response) could otherwise read or write it. This additionally requires
    the caller to identify itself via X-Actor-Ref (resolved to a User) and
    verifies that user has a WorkspaceMembership row for this exact
    workspace. No downstream handler may skip this and trust workspace_id
    alone.
    """

    ws = db.get(Workspace, workspace_id)
    if ws is None:
        raise HTTPException(status_code=404, detail="workspace not found")

    if not x_actor_ref:
        raise HTTPException(status_code=401, detail="X-Actor-Ref header is required")

    user = db.execute(select(User).where(User.external_ref == x_actor_ref)).scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=401, detail="unknown actor")

    membership = db.execute(
        select(WorkspaceMembership).where(
            WorkspaceMembership.workspace_id == workspace_id,
            WorkspaceMembership.user_id == user.id,
        )
    ).scalar_one_or_none()
    if membership is None:
        raise HTTPException(status_code=403, detail="actor is not a member of this workspace")

    return MembershipContext(workspace=ws, user=user, role=membership.role)
