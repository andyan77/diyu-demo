import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import require_workspace
from app.api.serialize import row_to_dict
from app.db import get_db
from app.models.content import Artifact, ContentVersion, Task, TaskSnapshot
from app.models.identity import Workspace
from app.models.infra import TaskRunState

router = APIRouter(tags=["tasks"])


def utcnow():
    return datetime.now(timezone.utc)


class CreateTaskRequest(BaseModel):
    idempotency_key: str
    account_id: uuid.UUID | None = None
    cycle_id: uuid.UUID | None = None
    kind: str | None = None


@router.post("/workspaces/{workspace_id}/tasks")
def create_task(
    workspace_id: uuid.UUID,
    body: CreateTaskRequest,
    db: Session = Depends(get_db),
    _ws: Workspace = Depends(require_workspace),
):
    existing = db.execute(
        select(Task).where(Task.idempotency_key == body.idempotency_key)
    ).scalar_one_or_none()
    if existing:
        if existing.workspace_id != workspace_id:
            raise HTTPException(
                status_code=409,
                detail="idempotency_key already used in a different workspace",
            )
        return row_to_dict(existing)

    task = Task(
        workspace_id=workspace_id,
        account_id=body.account_id,
        cycle_id=body.cycle_id,
        kind=body.kind,
        idempotency_key=body.idempotency_key,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return row_to_dict(task)


class CreateSnapshotRequest(BaseModel):
    idempotency_key: str
    payload: dict = {}
    info_nature: str
    source: str | None = None
    confirmation_status: str = "confirmed"
    scope: dict = {}
    availability_status: str = "available"


@router.post("/workspaces/{workspace_id}/tasks/{task_id}/snapshots")
def create_snapshot(
    workspace_id: uuid.UUID,
    task_id: uuid.UUID,
    body: CreateSnapshotRequest,
    db: Session = Depends(get_db),
    _ws: Workspace = Depends(require_workspace),
):
    task = db.get(Task, task_id)
    if task is None or task.workspace_id != workspace_id:
        raise HTTPException(status_code=404, detail="task not found in this workspace")

    existing = db.execute(
        select(TaskSnapshot).where(TaskSnapshot.idempotency_key == body.idempotency_key)
    ).scalar_one_or_none()
    if existing:
        return row_to_dict(existing)

    snapshot = TaskSnapshot(
        task_id=task_id,
        payload=body.payload,
        info_nature=body.info_nature,
        source=body.source,
        confirmation_status=body.confirmation_status,
        scope=body.scope,
        availability_status=body.availability_status,
        idempotency_key=body.idempotency_key,
    )
    db.add(snapshot)
    db.commit()
    db.refresh(snapshot)
    return row_to_dict(snapshot)


class RunStateRequest(BaseModel):
    last_success_step: str | None = None
    failed_step: str | None = None
    resumable_from: str | None = None
    side_effects: dict = {}


@router.put("/workspaces/{workspace_id}/tasks/{task_id}/run-state")
def upsert_run_state(
    workspace_id: uuid.UUID,
    task_id: uuid.UUID,
    body: RunStateRequest,
    db: Session = Depends(get_db),
    _ws: Workspace = Depends(require_workspace),
):
    task = db.get(Task, task_id)
    if task is None or task.workspace_id != workspace_id:
        raise HTTPException(status_code=404, detail="task not found in this workspace")

    state = db.execute(
        select(TaskRunState).where(TaskRunState.task_id == task_id)
    ).scalar_one_or_none()
    if state is None:
        state = TaskRunState(task_id=task_id)
        db.add(state)
    state.last_success_step = body.last_success_step
    state.failed_step = body.failed_step
    state.resumable_from = body.resumable_from
    state.side_effects = body.side_effects
    db.commit()
    db.refresh(state)
    return row_to_dict(state)


@router.get("/workspaces/{workspace_id}/tasks/{task_id}/run-state")
def get_run_state(
    workspace_id: uuid.UUID,
    task_id: uuid.UUID,
    db: Session = Depends(get_db),
    _ws: Workspace = Depends(require_workspace),
):
    task = db.get(Task, task_id)
    if task is None or task.workspace_id != workspace_id:
        raise HTTPException(status_code=404, detail="task not found in this workspace")
    state = db.execute(
        select(TaskRunState).where(TaskRunState.task_id == task_id)
    ).scalar_one_or_none()
    if state is None:
        return {"task_id": str(task_id), "recovery_state": "none_recorded"}
    return row_to_dict(state)


@router.get("/workspaces/{workspace_id}/tasks/{task_id}/projection")
def get_task_projection(
    workspace_id: uuid.UUID,
    task_id: uuid.UUID,
    db: Session = Depends(get_db),
    _ws: Workspace = Depends(require_workspace),
):
    """The minimal-projection read seam (§5.11 item 1): everything a
    consuming module (M1/M3/M4) needs to pick up this task, and nothing
    from any other workspace/task. Snapshots whose availability_status is
    no longer "available" (e.g. withdrawn) are excluded from `latest_snapshot`.
    """

    task = db.get(Task, task_id)
    if task is None or task.workspace_id != workspace_id:
        raise HTTPException(status_code=404, detail="task not found in this workspace")

    latest_snapshot = db.execute(
        select(TaskSnapshot)
        .where(TaskSnapshot.task_id == task_id, TaskSnapshot.availability_status == "available")
        .order_by(TaskSnapshot.created_at.desc())
        .limit(1)
    ).scalar_one_or_none()

    current_versions = db.execute(
        select(ContentVersion)
        .join(Artifact, Artifact.id == ContentVersion.artifact_id)
        .where(Artifact.task_id == task_id, ContentVersion.is_current.is_(True))
    ).scalars().all()

    run_state = db.execute(
        select(TaskRunState).where(TaskRunState.task_id == task_id)
    ).scalar_one_or_none()

    return {
        "task": row_to_dict(task),
        "latest_snapshot": row_to_dict(latest_snapshot) if latest_snapshot else None,
        "current_content_versions": [row_to_dict(v) for v in current_versions],
        "run_state": row_to_dict(run_state) if run_state else None,
    }
