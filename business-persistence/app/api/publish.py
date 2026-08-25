import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import MembershipContext, require_membership
from app.api.serialize import row_to_dict
from app.db import get_db
from app.models.content import Artifact, ContentVersion, Task
from app.models.identity import Account
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


@router.post("/workspaces/{workspace_id}/publish-instances")
def register_publish_instance(
    workspace_id: uuid.UUID,
    body: RegisterPublishRequest,
    db: Session = Depends(get_db),
    ctx: MembershipContext = Depends(require_membership),
):
    """发布实例. Requires the content_version to actually belong to a task in
    this workspace -- there is no way to register a publish instance for a
    draft/candidate you cannot see. is_test/is_simulated are required,
    explicit booleans (default False = real), never inferred from a string.
    idempotency_key is scoped per-workspace at the database level
    (uq_publish_instance_workspace_idempotency), so this lookup and the
    IntegrityError retry below both key off (workspace_id, idempotency_key)
    -- never a bare global idempotency_key lookup, which would let workspace
    A's retry return workspace B's row.
    """

    existing = db.execute(
        select(PublishInstance).where(
            PublishInstance.workspace_id == workspace_id,
            PublishInstance.idempotency_key == body.idempotency_key,
        )
    ).scalar_one_or_none()
    if existing:
        return row_to_dict(existing)

    version = _require_content_version_in_workspace(db, workspace_id, body.content_version_id)

    # Lock this content_version row for the rest of the transaction. Without
    # this, a concurrent withdraw_material invalidation (app/services/
    # versioning.py) can commit in the gap between this read and our INSERT
    # below -- the version ends up both published and invalidated. Taking
    # the row lock here means the two transactions serialize on this row:
    # whichever commits first is the one the other sees once it gets past
    # the lock wait.
    #
    # db.refresh(..., with_for_update=True) is required here, NOT
    # db.execute(select(...).with_for_update()) -- `version` is already in
    # this Session's identity map from the plain read above, and by default
    # SQLAlchemy's ORM returns the SAME cached Python object for an
    # already-identity-mapped primary key instead of overwriting its
    # attributes from a newly executed SELECT. That means a plain
    # `select(...).with_for_update()` call correctly acquires and waits for
    # the DB-level lock, but `.invalidated_at` on the object it returns can
    # still be the STALE pre-wait value -- which reintroduces exactly the
    # race this lock exists to close, just moved one layer up. refresh()
    # forces the object's attributes to be overwritten in place from the
    # locked row.
    db.refresh(version, with_for_update=True)
    if version.invalidated_at is not None:
        raise HTTPException(
            status_code=409,
            detail="cannot publish a content_version invalidated by a material withdrawal",
        )

    account = db.get(Account, body.account_id)
    if account is None or account.workspace_id != workspace_id:
        raise HTTPException(status_code=404, detail="account not found in this workspace")

    instance = PublishInstance(
        workspace_id=workspace_id,
        content_version_id=body.content_version_id,
        account_id=body.account_id,
        platform=body.platform,
        published_at=body.published_at,
        is_test=body.is_test,
        is_simulated=body.is_simulated,
        registered_by=ctx.user.external_ref,
        idempotency_key=body.idempotency_key,
    )
    db.add(instance)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        existing = db.execute(
            select(PublishInstance).where(
                PublishInstance.workspace_id == workspace_id,
                PublishInstance.idempotency_key == body.idempotency_key,
            )
        ).scalar_one_or_none()
        if existing:
            return row_to_dict(existing)
        raise
    db.refresh(instance)
    return row_to_dict(instance)


@router.get("/workspaces/{workspace_id}/content-versions/{content_version_id}/publish-instances")
def list_publish_instances_for_version(
    workspace_id: uuid.UUID,
    content_version_id: uuid.UUID,
    db: Session = Depends(get_db),
    ctx: MembershipContext = Depends(require_membership),
):
    _require_content_version_in_workspace(db, workspace_id, content_version_id)
    rows = db.execute(
        select(PublishInstance).where(PublishInstance.content_version_id == content_version_id)
    ).scalars().all()
    return [row_to_dict(p) for p in rows]


class RegisterFeedbackRequest(BaseModel):
    idempotency_key: str
    publish_instance_id: uuid.UUID | None = None
    content_version_id: uuid.UUID | None = None
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
    ctx: MembershipContext = Depends(require_membership),
):
    """反馈. Binds to exactly one of publish_instance_id (post-publish
    feedback, the common case) or content_version_id (发布前人工评价, §5.6 --
    a review that exists before any publish_instance does). Which one is
    required is determined by is_pre_publish_review, and exactly one of the
    two ids must be set -- a row that set both, or neither, would blur the
    "this happened after a real publish" evidence-tier boundary the kind/
    is_test/is_simulated fields exist to protect.

    A pre-publish review also cannot claim a stronger evidence tier than
    its content_version's own history: if that version was later invalidated,
    the review's is_test/is_simulated must already reflect the same or a
    weaker tier as when it was written; that is enforced simply by binding
    the review to a specific content_version_id row, not by inferring
    anything about the publish.
    """

    existing = db.execute(
        select(FeedbackRecord).where(
            FeedbackRecord.workspace_id == workspace_id,
            FeedbackRecord.idempotency_key == body.idempotency_key,
        )
    ).scalar_one_or_none()
    if existing:
        return row_to_dict(existing)

    if body.kind not in ("observation", "interpretation", "decision"):
        raise HTTPException(
            status_code=422, detail="kind must be one of: observation, interpretation, decision"
        )

    has_publish = body.publish_instance_id is not None
    has_version = body.content_version_id is not None
    if has_publish == has_version:
        raise HTTPException(
            status_code=422,
            detail="exactly one of publish_instance_id or content_version_id must be set",
        )
    if body.is_pre_publish_review != has_version:
        raise HTTPException(
            status_code=422,
            detail="is_pre_publish_review must be true iff content_version_id is set",
        )

    if has_publish:
        instance = db.get(PublishInstance, body.publish_instance_id)
        if instance is None or instance.workspace_id != workspace_id:
            raise HTTPException(status_code=404, detail="publish_instance not found in this workspace")
    else:
        _require_content_version_in_workspace(db, workspace_id, body.content_version_id)

    record = FeedbackRecord(
        workspace_id=workspace_id,
        publish_instance_id=body.publish_instance_id,
        content_version_id=body.content_version_id,
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
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        existing = db.execute(
            select(FeedbackRecord).where(
                FeedbackRecord.workspace_id == workspace_id,
                FeedbackRecord.idempotency_key == body.idempotency_key,
            )
        ).scalar_one_or_none()
        if existing:
            return row_to_dict(existing)
        raise
    db.refresh(record)
    return row_to_dict(record)


@router.get("/workspaces/{workspace_id}/publish-instances/{publish_instance_id}/feedback")
def list_feedback_for_publish_instance(
    workspace_id: uuid.UUID,
    publish_instance_id: uuid.UUID,
    db: Session = Depends(get_db),
    ctx: MembershipContext = Depends(require_membership),
):
    instance = db.get(PublishInstance, publish_instance_id)
    if instance is None or instance.workspace_id != workspace_id:
        raise HTTPException(status_code=404, detail="publish_instance not found in this workspace")
    rows = db.execute(
        select(FeedbackRecord).where(FeedbackRecord.publish_instance_id == publish_instance_id)
    ).scalars().all()
    return [row_to_dict(f) for f in rows]
