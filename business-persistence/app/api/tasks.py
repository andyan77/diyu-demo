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
from app.models.content import Artifact, ContentVersion, LegacyImportRecord, Task, TaskSnapshot
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


LEGACY_SNAPSHOT_REQUIRED_KEYS = {
    "schema_version",
    "task_id",
    "revision",
    "phase",
    "candidate_skill",
    "draft_task",
    "confirmed_task",
    "pending_action",
    "authorization",
    "artifacts",
    "blocking_gap",
    "last_result_ref",
    "last_error",
}


class LegacyImportRequest(BaseModel):
    idempotency_key: str
    account_id: uuid.UUID | None = None
    legacy_snapshot: dict


def _legacy_import_result(db: Session, record: LegacyImportRecord) -> dict:
    task = db.get(Task, record.task_id)
    # Nothing stops a caller from adding further snapshots to a
    # legacy-imported task afterwards via the normal snapshots endpoint --
    # scalar_one_or_none() would then raise MultipleResultsFound (a 500) on
    # a legacy-import retry. Order by recency instead of assuming exactly
    # one row will ever exist.
    snapshot = db.execute(
        select(TaskSnapshot)
        .where(TaskSnapshot.task_id == record.task_id)
        .order_by(TaskSnapshot.created_at.desc())
        .limit(1)
    ).scalar_one_or_none()
    return {"task": row_to_dict(task), "snapshot": row_to_dict(snapshot) if snapshot else None}


@router.post("/workspaces/{workspace_id}/tasks/legacy-import")
def import_legacy_snapshot(
    workspace_id: uuid.UUID,
    body: LegacyImportRequest,
    db: Session = Depends(get_db),
    ctx: MembershipContext = Depends(require_membership),
):
    """Imports one V1 Demo task_snapshot_json object (the old Dify 5-slot
    session-state mechanism -- see decision-chain/docs/
    V1_TASK_SNAPSHOT_SCHEMA_v0.1.json) as a single historical Task +
    TaskSnapshot representing exactly what was observed at import time --
    the old mechanism kept no version history, so none is fabricated here.

    Idempotency is tracked in LegacyImportRecord, a namespace of its own,
    NOT via Task.idempotency_key -- an earlier version of this endpoint
    reused Task.idempotency_key directly, which meant a live task-creation
    caller and a legacy-import caller choosing the same key string by
    coincidence would collide: whichever wrote second got back the first's
    row, reporting false success while importing nothing (or attaching a
    live user-confirmed fact onto what looked like a legacy record). The
    Task row created here always gets idempotency_key=NULL -- Postgres
    never treats two NULLs as a UNIQUE-constraint collision -- so it is
    structurally impossible for a legacy import to collide with, return, or
    be returned by a live task's row. Task + TaskSnapshot + the idempotency
    record are created in a single transaction, so a failure between them
    can never leave a Task with no snapshot stuck in that state forever.

    `source` on the snapshot is always "legacy_dify_v1_task_snapshot_import" so
    it can never be mistaken for a live, real-time user confirmation. This
    imports the full V1_TASK_SNAPSHOT_SCHEMA_v0.1.json state object, whose
    `artifacts` sub-object has 3 named slots (matrix/campaign/content_brief) --
    not 5, see M2_ACCEPTANCE_EVIDENCE.md AC-14 for the corrected terminology.
    """

    missing = LEGACY_SNAPSHOT_REQUIRED_KEYS - body.legacy_snapshot.keys()
    if missing:
        raise HTTPException(
            status_code=422,
            detail=f"legacy_snapshot missing required V1 schema keys: {sorted(missing)}",
        )

    existing_record = db.execute(
        select(LegacyImportRecord).where(
            LegacyImportRecord.workspace_id == workspace_id,
            LegacyImportRecord.idempotency_key == body.idempotency_key,
        )
    ).scalar_one_or_none()
    if existing_record:
        return _legacy_import_result(db, existing_record)

    if body.account_id is not None:
        account = db.get(Account, body.account_id)
        if account is None or account.workspace_id != workspace_id:
            raise HTTPException(status_code=404, detail="account_id not found in this workspace")

    confirmed_task = body.legacy_snapshot.get("confirmed_task")
    draft_task = body.legacy_snapshot.get("draft_task") or {}
    # the SAME truthiness check must drive both which goal to read and how
    # to classify it -- an earlier version used isinstance() for one and
    # truthiness for the other, so confirmed_task={} (present but empty)
    # read its (nonexistent) goal from the empty dict while classifying
    # itself as confirmed, silently losing draft_task's real goal.
    goal_source = confirmed_task if confirmed_task else draft_task
    note = goal_source.get("goal") if isinstance(goal_source, dict) else None
    if confirmed_task:
        info_nature, confirmation_status = "fact", "confirmed"
    else:
        info_nature, confirmation_status = "preference", "inferred"

    task = Task(
        workspace_id=workspace_id,
        account_id=body.account_id,
        kind="legacy_import",
        idempotency_key=None,
    )
    db.add(task)
    db.flush()

    snapshot = TaskSnapshot(
        task_id=task.id,
        payload={"note": note, "legacy_snapshot": body.legacy_snapshot},
        info_nature=info_nature,
        source="legacy_dify_v1_task_snapshot_import",
        confirmation_status=confirmation_status,
        scope={
            "imported_from": "v1_demo_task_snapshot_v1",
            "schema_version": body.legacy_snapshot.get("schema_version"),
            "legacy_task_id": body.legacy_snapshot.get("task_id"),
        },
        availability_status="available",
        idempotency_key=body.idempotency_key,
    )
    db.add(snapshot)

    record = LegacyImportRecord(
        workspace_id=workspace_id, idempotency_key=body.idempotency_key, task_id=task.id
    )
    db.add(record)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        existing_record = db.execute(
            select(LegacyImportRecord).where(
                LegacyImportRecord.workspace_id == workspace_id,
                LegacyImportRecord.idempotency_key == body.idempotency_key,
            )
        ).scalar_one_or_none()
        if existing_record:
            return _legacy_import_result(db, existing_record)
        raise
    db.refresh(task)
    db.refresh(snapshot)
    return {"task": row_to_dict(task), "snapshot": row_to_dict(snapshot)}


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
