import uuid

from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.identity import Workspace


def get_session(db: Session = Depends(get_db)) -> Session:
    return db


def require_workspace(workspace_id: uuid.UUID, db: Session = Depends(get_db)) -> Workspace:
    """Every path that touches business data is scoped by workspace_id in
    the URL; this dependency is the single choke point that turns a
    nonexistent/foreign workspace_id into 404 before any query runs. There
    is no code path that reads or writes across workspace_id.
    """

    ws = db.get(Workspace, workspace_id)
    if ws is None:
        raise HTTPException(status_code=404, detail="workspace not found")
    return ws
