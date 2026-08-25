import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import MembershipContext, require_membership
from app.api.serialize import row_to_dict
from app.db import get_db
from app.models.identity import Account, Subject, User, Workspace, WorkspaceMembership

router = APIRouter(tags=["identity"])


class CreateUserRequest(BaseModel):
    external_ref: str
    display_name: str | None = None


@router.post("/users")
def create_user(body: CreateUserRequest, db: Session = Depends(get_db)):
    existing = db.execute(
        select(User).where(User.external_ref == body.external_ref)
    ).scalar_one_or_none()
    if existing:
        return row_to_dict(existing)
    user = User(external_ref=body.external_ref, display_name=body.display_name)
    db.add(user)
    db.commit()
    db.refresh(user)
    return row_to_dict(user)


class CreateWorkspaceRequest(BaseModel):
    name: str
    kind: str = "personal"
    owner_user_id: uuid.UUID


@router.post("/workspaces")
def create_workspace(body: CreateWorkspaceRequest, db: Session = Depends(get_db)):
    if db.get(User, body.owner_user_id) is None:
        raise HTTPException(status_code=404, detail="owner_user_id not found")
    ws = Workspace(name=body.name, kind=body.kind)
    db.add(ws)
    db.flush()
    db.add(WorkspaceMembership(user_id=body.owner_user_id, workspace_id=ws.id, role="owner"))
    db.commit()
    db.refresh(ws)
    return row_to_dict(ws)


@router.get("/users/{user_id}/workspaces")
def list_user_workspaces(user_id: uuid.UUID, db: Session = Depends(get_db)):
    """Cross-session recovery entry point: given an authenticated user,
    return exactly the workspaces they have a membership row for -- no
    other workspace is ever visible through this path.
    """

    if db.get(User, user_id) is None:
        raise HTTPException(status_code=404, detail="user not found")
    rows = db.execute(
        select(Workspace, WorkspaceMembership.role)
        .join(WorkspaceMembership, WorkspaceMembership.workspace_id == Workspace.id)
        .where(WorkspaceMembership.user_id == user_id)
    ).all()
    return [{**row_to_dict(ws), "role": role} for ws, role in rows]


class CreateSubjectRequest(BaseModel):
    name: str
    kind: str | None = None


@router.post("/workspaces/{workspace_id}/subjects")
def create_subject(
    workspace_id: uuid.UUID,
    body: CreateSubjectRequest,
    db: Session = Depends(get_db),
    _ctx: MembershipContext = Depends(require_membership),
):
    subject = Subject(workspace_id=workspace_id, name=body.name, kind=body.kind)
    db.add(subject)
    db.commit()
    db.refresh(subject)
    return row_to_dict(subject)


class CreateAccountRequest(BaseModel):
    platform: str
    handle: str
    subject_id: uuid.UUID | None = None


@router.post("/workspaces/{workspace_id}/accounts")
def create_account(
    workspace_id: uuid.UUID,
    body: CreateAccountRequest,
    db: Session = Depends(get_db),
    _ctx: MembershipContext = Depends(require_membership),
):
    if body.subject_id is not None:
        subject = db.get(Subject, body.subject_id)
        if subject is None or subject.workspace_id != workspace_id:
            raise HTTPException(status_code=404, detail="subject_id not found in this workspace")

    existing = db.execute(
        select(Account).where(
            Account.workspace_id == workspace_id,
            Account.platform == body.platform,
            Account.handle == body.handle,
        )
    ).scalar_one_or_none()
    if existing:
        return row_to_dict(existing)
    account = Account(
        workspace_id=workspace_id,
        platform=body.platform,
        handle=body.handle,
        subject_id=body.subject_id,
    )
    db.add(account)
    db.commit()
    db.refresh(account)
    return row_to_dict(account)


@router.get("/workspaces/{workspace_id}/accounts")
def list_accounts(
    workspace_id: uuid.UUID,
    db: Session = Depends(get_db),
    _ctx: MembershipContext = Depends(require_membership),
):
    rows = db.execute(select(Account).where(Account.workspace_id == workspace_id)).scalars().all()
    return [row_to_dict(a) for a in rows]
