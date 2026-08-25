import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import require_workspace
from app.api.serialize import row_to_dict
from app.db import get_db
from app.models.content import Artifact, ContentVersion, Task
from app.models.identity import Account, Workspace
from app.models.publish import FeedbackRecord, PublishInstance

router = APIRouter(tags=["publish"])


def _require_content_version_in_workspace(
    db: Session, workspace_id: uuid.UUID, content_version_id: uuid.UUID
) -> ContentVersion:
    version = db.get(ContentVersion, content_version_id)
    if version is None:
        raise HTTPException(status_code=404, detail="content_version not found")
    artifact = db.get(Artifact, version.artifact_id)
    task = db.get(Task, artifact.task_id) if artifact else None
    if task is None or task.workspace_id != workspace_id:
        raise HTTPException(status_code=404, detail="content_version not found in this workspace")
    return version


class RegisterPublishRequest(BaseModel):
    idempotency_key: str
    content_version_id: uuid.UUID
    account_id: uuid.UUID
    platform: str
    published_at: datetime
    is_test: bool = False
    is_simulated: bool = False
    registered_by: str | None = None


@router.post("/workspaces/{workspace_id}/publish-instances")
def register_publish_instance(
    workspace_id: uuid.UUID,
    body: RegisterPublishRequest,
    db: Session = Depends(get_db),
    _ws: Workspace = Depends(require_workspace),
):
    """发布实例. Requires the content_version to actually belong to a task in
    this workspace -- there is no way to register a publish instance for a
    draft/candidate you cannot see. is_test/is_simulated are required,
    explicit booleans (default False = real), never inferred from a string.
    """

    existing = db.execute(
        select(PublishInstance).where(PublishInstance.idempotency_key == body.idempotency_key)
    ).scalar_one_or_none()
    if existing:
        return row_to_dict(existing)

    _require_content_version_in_workspace(db, workspace_id, body.content_version_id)

    account = db.get(Account, body.account_id)
    if account is None or account.workspace_id != workspace_id:
        raise HTTPException(status_code=404, detail="account not found in this workspace")

    instance = PublishInstance(
        content_version_id=body.content_version_id,
        account_id=body.account_id,
        platform=body.platform,
        published_at=body.published_at,
        is_test=body.is_test,
        is_simulated=body.is_simulated,
        registered_by=body.registered_by,
        idempotency_key=body.idempotency_key,
    )
    db.add(instance)
    db.commit()
    db.refresh(instance)
    return row_to_dict(instance)


@router.get("/workspaces/{workspace_id}/content-versions/{content_version_id}/publish-instances")
def list_publish_instances_for_version(
    workspace_id: uuid.UUID,
    content_version_id: uuid.UUID,
    db: Session = Depends(get_db),
    _ws: Workspace = Depends(require_workspace),
):
    _require_content_version_in_workspace(db, workspace_id, content_version_id)
    rows = db.execute(
        select(PublishInstance).where(PublishInstance.content_version_id == content_version_id)
    ).scalars().all()
    return [row_to_dict(p) for p in rows]


class RegisterFeedbackRequest(BaseModel):
    idempotency_key: str
    publish_instance_id: uuid.UUID
    kind: str  # observation | interpretation | decision
    is_test: bool = False
    is_simulated: bool = False
    is_manual_entry: bool = False
    is_pre_publish_review: bool = False
    source: str | None = None
    observed_at: datetime | None = None
    window_start: datetime | None = None
    window_end: datetime | None = None
    goal_at_the_time: str | None = None
    payload: dict = {}


@router.post("/workspaces/{workspace_id}/feedback")
def register_feedback(
    workspace_id: uuid.UUID,
    body: RegisterFeedbackRequest,
    db: Session = Depends(get_db),
    _ws: Workspace = Depends(require_workspace),
):
    """反馈. publish_instance_id is required and validated to exist in this
    workspace -- there is no code path to attach feedback to a draft,
    candidate, PRE, or unpublished FINAL version. kind separates raw
    observation from interpretation from the adjust-or-not decision.
    """

    existing = db.execute(
        select(FeedbackRecord).where(FeedbackRecord.idempotency_key == body.idempotency_key)
    ).scalar_one_or_none()
    if existing:
        return row_to_dict(existing)

    instance = db.get(PublishInstance, body.publish_instance_id)
    if instance is None:
        raise HTTPException(status_code=404, detail="publish_instance not found")
    # walk publish_instance -> content_version -> artifact -> task -> workspace
    _require_content_version_in_workspace(db, workspace_id, instance.content_version_id)

    if body.kind not in ("observation", "interpretation", "decision"):
        raise HTTPException(
            status_code=422, detail="kind must be one of: observation, interpretation, decision"
        )

    record = FeedbackRecord(
        publish_instance_id=body.publish_instance_id,
        kind=body.kind,
        is_test=body.is_test,
        is_simulated=body.is_simulated,
        is_manual_entry=body.is_manual_entry,
        is_pre_publish_review=body.is_pre_publish_review,
        source=body.source,
        observed_at=body.observed_at,
        window_start=body.window_start,
        window_end=body.window_end,
        goal_at_the_time=body.goal_at_the_time,
        payload=body.payload,
        idempotency_key=body.idempotency_key,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return row_to_dict(record)


@router.get("/workspaces/{workspace_id}/publish-instances/{publish_instance_id}/feedback")
def list_feedback_for_publish_instance(
    workspace_id: uuid.UUID,
    publish_instance_id: uuid.UUID,
    db: Session = Depends(get_db),
    _ws: Workspace = Depends(require_workspace),
):
    instance = db.get(PublishInstance, publish_instance_id)
    if instance is None:
        raise HTTPException(status_code=404, detail="publish_instance not found")
    _require_content_version_in_workspace(db, workspace_id, instance.content_version_id)
    rows = db.execute(
        select(FeedbackRecord).where(FeedbackRecord.publish_instance_id == publish_instance_id)
    ).scalars().all()
    return [row_to_dict(f) for f in rows]
