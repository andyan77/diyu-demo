import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import MembershipContext, require_membership
from app.api.serialize import row_to_dict
from app.db import get_db
from app.models.content import (
    Artifact,
    ContentVersion,
    ContentVersionMaterialDependency,
    Material,
    Task,
)
from app.services.versioning import promote_version, withdraw_material

router = APIRouter(tags=["content"])


class CreateArtifactRequest(BaseModel):
    kind: str | None = None
    content_hash: str
    parent_artifact_id: uuid.UUID | None = None


@router.post("/workspaces/{workspace_id}/tasks/{task_id}/artifacts")
def create_artifact(
    workspace_id: uuid.UUID,
    task_id: uuid.UUID,
    body: CreateArtifactRequest,
    db: Session = Depends(get_db),
    ctx: MembershipContext = Depends(require_membership),
):
    task = db.get(Task, task_id)
    if task is None or task.workspace_id != workspace_id:
        raise HTTPException(status_code=404, detail="task not found in this workspace")

    artifact = Artifact(
        task_id=task_id,
        kind=body.kind,
        content_hash=body.content_hash,
        parent_artifact_id=body.parent_artifact_id,
    )
    db.add(artifact)
    db.commit()
    db.refresh(artifact)
    return row_to_dict(artifact)


def _require_artifact_in_workspace(db: Session, workspace_id: uuid.UUID, artifact_id: uuid.UUID) -> Artifact:
    artifact = db.get(Artifact, artifact_id)
    if artifact is None:
        raise HTTPException(status_code=404, detail="artifact not found")
    task = db.get(Task, artifact.task_id)
    if task is None or task.workspace_id != workspace_id:
        raise HTTPException(status_code=404, detail="artifact not found in this workspace")
    return artifact


class CreateVersionRequest(BaseModel):
    idempotency_key: str
    content_ref: str | None = None
    content_hash: str
    produced_by: str | None = None
    material_ids: list[uuid.UUID] = []


@router.post("/workspaces/{workspace_id}/artifacts/{artifact_id}/versions")
def create_version(
    workspace_id: uuid.UUID,
    artifact_id: uuid.UUID,
    body: CreateVersionRequest,
    db: Session = Depends(get_db),
    ctx: MembershipContext = Depends(require_membership),
):
    """Create a new candidate version. Never touches is_current -- promotion
    is a separate, explicit, auditable action (see promote_content_version).

    Every material_id must belong to this workspace AND not be withdrawn --
    without that second check a version could be created (or a withdrawn
    material silently re-used) after withdrawal, bypassing the whole
    withdraw-cascades-to-invalidation mechanism in withdraw_material.
    """

    _require_artifact_in_workspace(db, workspace_id, artifact_id)

    existing = db.execute(
        select(ContentVersion).where(
            ContentVersion.artifact_id == artifact_id,
            ContentVersion.idempotency_key == body.idempotency_key,
        )
    ).scalar_one_or_none()
    if existing:
        return row_to_dict(existing)

    materials = []
    for material_id in body.material_ids:
        material = db.get(Material, material_id)
        if material is None or material.workspace_id != workspace_id:
            raise HTTPException(
                status_code=404, detail=f"material {material_id} not found in this workspace"
            )
        if material.withdrawn_at is not None:
            raise HTTPException(
                status_code=409, detail=f"material {material_id} has been withdrawn"
            )
        materials.append(material)

    # Lock the artifact row for the rest of this transaction before reading
    # max(version_no). Without this, two concurrent create_version calls on
    # the SAME artifact (different idempotency_key each -- the idempotency
    # branch above only protects a *repeated* key, not two genuinely
    # different concurrent creates) can both read the same max and both
    # attempt to insert the same version_no, so the loser's INSERT violates
    # uq_version_artifact_no. That IntegrityError used to propagate as a
    # raw 500 -- the except-IntegrityError block below only re-checks by
    # idempotency_key, which is different for each caller here, so it never
    # found a match and just re-raised. A column-only select (not the full
    # ORM object) is used deliberately -- it never populates the identity
    # map, so there's no risk of a stale cached object being read after the
    # lock is acquired (the earlier _require_artifact_in_workspace() call
    # above already loaded a plain, unlocked Artifact into the identity
    # map). We don't need any of the artifact's own columns here; the lock
    # itself is the point -- it serializes the read-max-then-insert critical
    # section so the second transaction only proceeds after the first
    # commits, and by then sees the correct new max.
    db.execute(select(Artifact.id).where(Artifact.id == artifact_id).with_for_update())

    next_no = (
        db.execute(
            select(func.coalesce(func.max(ContentVersion.version_no), 0)).where(
                ContentVersion.artifact_id == artifact_id
            )
        ).scalar_one()
        + 1
    )

    version = ContentVersion(
        artifact_id=artifact_id,
        version_no=next_no,
        is_current=False,
        content_ref=body.content_ref,
        content_hash=body.content_hash,
        produced_by=body.produced_by,
        idempotency_key=body.idempotency_key,
    )
    db.add(version)
    db.flush()

    for material in materials:
        db.add(
            ContentVersionMaterialDependency(
                content_version_id=version.id, material_id=material.id
            )
        )

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        existing = db.execute(
            select(ContentVersion).where(
                ContentVersion.artifact_id == artifact_id,
                ContentVersion.idempotency_key == body.idempotency_key,
            )
        ).scalar_one_or_none()
        if existing:
            return row_to_dict(existing)
        raise
    db.refresh(version)
    return row_to_dict(version)


@router.get("/workspaces/{workspace_id}/artifacts/{artifact_id}/versions")
def list_versions(
    workspace_id: uuid.UUID,
    artifact_id: uuid.UUID,
    db: Session = Depends(get_db),
    ctx: MembershipContext = Depends(require_membership),
):
    _require_artifact_in_workspace(db, workspace_id, artifact_id)
    rows = db.execute(
        select(ContentVersion)
        .where(ContentVersion.artifact_id == artifact_id)
        .order_by(ContentVersion.version_no.asc())
    ).scalars().all()
    return [row_to_dict(v) for v in rows]


@router.get("/workspaces/{workspace_id}/artifacts/{artifact_id}/versions/current")
def get_current_version(
    workspace_id: uuid.UUID,
    artifact_id: uuid.UUID,
    db: Session = Depends(get_db),
    ctx: MembershipContext = Depends(require_membership),
):
    _require_artifact_in_workspace(db, workspace_id, artifact_id)
    version = db.execute(
        select(ContentVersion).where(
            ContentVersion.artifact_id == artifact_id, ContentVersion.is_current.is_(True)
        )
    ).scalar_one_or_none()
    if version is None:
        raise HTTPException(status_code=404, detail="no current version for this artifact")
    return row_to_dict(version)


class PromoteVersionRequest(BaseModel):
    expected_row_version: int | None = None


@router.post("/workspaces/{workspace_id}/artifacts/{artifact_id}/versions/{version_id}/promote")
def promote_content_version(
    workspace_id: uuid.UUID,
    artifact_id: uuid.UUID,
    version_id: uuid.UUID,
    body: PromoteVersionRequest,
    db: Session = Depends(get_db),
    ctx: MembershipContext = Depends(require_membership),
):
    """promoted_by is always the authenticated actor (X-Actor-Ref), never a
    free-text request field -- a caller could otherwise write any string,
    including a bare "model:*" self-evaluation, into the audit trail of who
    promoted a version. A viewer-role member can read everything but may not
    promote.
    """

    if ctx.role == "viewer":
        raise HTTPException(status_code=403, detail="viewer role cannot promote a version")
    _require_artifact_in_workspace(db, workspace_id, artifact_id)
    version = promote_version(
        db, artifact_id, version_id, ctx.user.external_ref, body.expected_row_version
    )
    return row_to_dict(version)


class CreateMaterialRequest(BaseModel):
    source: str | None = None
    owner_ref: str | None = None
    analysis_authorized: bool = False
    generation_authorized: bool = False
    publish_authorized: bool = False
    scope_ref: dict = {}
    content_ref: str | None = None


@router.post("/workspaces/{workspace_id}/materials")
def create_material(
    workspace_id: uuid.UUID,
    body: CreateMaterialRequest,
    db: Session = Depends(get_db),
    ctx: MembershipContext = Depends(require_membership),
):
    material = Material(
        workspace_id=workspace_id,
        source=body.source,
        owner_ref=body.owner_ref,
        analysis_authorized=body.analysis_authorized,
        generation_authorized=body.generation_authorized,
        publish_authorized=body.publish_authorized,
        scope_ref=body.scope_ref,
        content_ref=body.content_ref,
    )
    db.add(material)
    db.commit()
    db.refresh(material)
    return row_to_dict(material)


@router.get("/workspaces/{workspace_id}/materials/{material_id}")
def get_material(
    workspace_id: uuid.UUID,
    material_id: uuid.UUID,
    db: Session = Depends(get_db),
    ctx: MembershipContext = Depends(require_membership),
):
    material = db.get(Material, material_id)
    if material is None or material.workspace_id != workspace_id:
        raise HTTPException(status_code=404, detail="material not found in this workspace")
    if material.withdrawn_at is not None:
        # withdrawn content must not be servable through this path
        payload = row_to_dict(material)
        payload["content_ref"] = None
        return payload
    return row_to_dict(material)


@router.post("/workspaces/{workspace_id}/materials/{material_id}/withdraw")
def withdraw_material_endpoint(
    workspace_id: uuid.UUID,
    material_id: uuid.UUID,
    db: Session = Depends(get_db),
    ctx: MembershipContext = Depends(require_membership),
):
    """withdrawn_by is always the authenticated actor (X-Actor-Ref), never a
    free-text request field -- same rationale as promoted_by above.
    """

    material = db.get(Material, material_id)
    if material is None or material.workspace_id != workspace_id:
        raise HTTPException(status_code=404, detail="material not found in this workspace")
    return withdraw_material(db, material_id, ctx.user.external_ref)
