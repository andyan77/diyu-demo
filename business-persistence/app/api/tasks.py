import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import MembershipContext, require_membership
from app.api.serialize import row_to_dict
from app.db import get_db
from app.models.content import Artifact, ContentVersion, Task, TaskSnapshot
from app.models.identity import Account
from app.models.infra import TaskRunState
from app.models.operations import Cycle

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
    ctx: MembershipContext = Depends(require_membership),
):
    existing = db.execute(
        select(Task).where(
            Task.workspace_id == workspace_id, Task.idempotency_key == body.idempotency_key
        )
    ).scalar_one_or_none()
    if existing:
        return row_to_dict(existing)

    if body.account_id is not None:
        account = db.get(Account, body.account_id)
        if account is None or account.workspace_id != workspace_id:
            raise HTTPException(status_code=404, detail="account_id not found in this workspace")
    if body.cycle_id is not None:
        cycle = db.get(Cycle, body.cycle_id)
        if cycle is None or cycle.workspace_id != workspace_id:
            raise HTTPException(status_code=404, detail="cycle_id not found in this workspace")

    task = Task(
        workspace_id=workspace_id,
        account_id=body.account_id,
        cycle_id=body.cycle_id,
        kind=body.kind,
        idempotency_key=body.idempotency_key,
    )
    db.add(task)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        existing = db.execute(
            select(Task).where(
                Task.workspace_id == workspace_id, Task.idempotency_key == body.idempotency_key
            )
        ).scalar_one_or_none()
        if existing:
            return row_to_dict(existing)
        raise
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
    ctx: MembershipContext = Depends(require_membership),
):
    task = db.get(Task, task_id)
    if task is None or task.workspace_id != workspace_id:
        raise HTTPException(status_code=404, detail="task not found in this workspace")

    existing = db.execute(
        select(TaskSnapshot).where(
            TaskSnapshot.task_id == task_id, TaskSnapshot.idempotency_key == body.idempotency_key
        )
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
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        existing = db.execute(
            select(TaskSnapshot).where(
                TaskSnapshot.task_id == task_id,
                TaskSnapshot.idempotency_key == body.idempotency_key,
            )
        ).scalar_one_or_none()
        if existing:
            return row_to_dict(existing)
        raise
    db.refresh(snapshot)
    return row_to_dict(snapshot)


class RunStateRequest(BaseModel):
    last_success_step: str | None = None
    failed_step: str | None = None
    resumable_from: str | None = None
    side_effects: dict | None = None


@router.put("/workspaces/{workspace_id}/tasks/{task_id}/run-state")
def upsert_run_state(
    workspace_id: uuid.UUID,
    task_id: uuid.UUID,
    body: RunStateRequest,
    db: Session = Depends(get_db),
    ctx: MembershipContext = Depends(require_membership),
):
    """Merge, not replace: only fields the caller actually sent
    (``exclude_unset``) overwrite last_success_step/failed_step/
    resumable_from, and side_effects keys are unioned into the existing
    dict rather than replacing it wholesale. A resume that only reports a
    new failed_step must never erase a previously-recorded successful step
    or the side effects that step already produced.
    """

    task = db.get(Task, task_id)
    if task is None or task.workspace_id != workspace_id:
        raise HTTPException(status_code=404, detail="task not found in this workspace")

    fields_set = body.model_fields_set

    state = db.execute(
        select(TaskRunState).where(TaskRunState.task_id == task_id)
    ).scalar_one_or_none()
    if state is None:
        state = TaskRunState(
            task_id=task_id,
            last_success_step=body.last_success_step,
            failed_step=body.failed_step,
            resumable_from=body.resumable_from,
            side_effects=body.side_effects or {},
        )
        db.add(state)
        try:
            db.commit()
        except IntegrityError:
            # Two concurrent first-writes for the same task_id both took the
            # "no row yet" branch; task_run_states.task_id is unique, so the
            # loser's INSERT violates it. Re-fetch what the winner just
            # created and fall through to the merge-update path below instead
            # of surfacing a raw 500 -- the loser's own request still gets
            # applied, merged onto the winner's row, not silently dropped.
            db.rollback()
            state = db.execute(
                select(TaskRunState).where(TaskRunState.task_id == task_id)
            ).scalar_one()
        else:
            db.refresh(state)
            return row_to_dict(state)

    expected_row_version = state.row_version
    if "last_success_step" in fields_set:
        state.last_success_step = body.last_success_step
    if "failed_step" in fields_set:
        state.failed_step = body.failed_step
    if "resumable_from" in fields_set:
        state.resumable_from = body.resumable_from
    if "side_effects" in fields_set and body.side_effects:
        state.side_effects = {**state.side_effects, **body.side_effects}

    result = db.execute(
        update(TaskRunState)
        .where(TaskRunState.id == state.id, TaskRunState.row_version == expected_row_version)
        .values(
            last_success_step=state.last_success_step,
            failed_step=state.failed_step,
            resumable_from=state.resumable_from,
            side_effects=state.side_effects,
            updated_at=utcnow(),
            row_version=TaskRunState.row_version + 1,
        )
    )
    if result.rowcount == 0:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="concurrent modification: run-state changed since read; re-read and retry",
        )
    db.commit()
    db.refresh(state)
    return row_to_dict(state)


@router.get("/workspaces/{workspace_id}/tasks/{task_id}/run-state")
def get_run_state(
    workspace_id: uuid.UUID,
    task_id: uuid.UUID,
    db: Session = Depends(get_db),
    ctx: MembershipContext = Depends(require_membership),
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
    ctx: MembershipContext = Depends(require_membership),
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
