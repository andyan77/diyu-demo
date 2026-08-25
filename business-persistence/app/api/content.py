import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import require_workspace
from app.api.serialize import row_to_dict
from app.db import get_db
from app.models.content import (
    Artifact,
    ContentVersion,
    ContentVersionMaterialDependency,
    Material,
    Task,
)
from app.models.identity import Workspace
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
    _ws: Workspace = Depends(require_workspace),
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
    _ws: Workspace = Depends(require_workspace),
):
    """Create a new candidate version. Never touches is_current -- promotion
    is a separate, explicit, auditable action (see promote_content_version).
    """

    _require_artifact_in_workspace(db, workspace_id, artifact_id)

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
    )
    db.add(version)
    db.flush()

    for material_id in body.material_ids:
        if db.get(Material, material_id) is None:
            raise HTTPException(status_code=404, detail=f"material {material_id} not found")
        db.add(
            ContentVersionMaterialDependency(
                content_version_id=version.id, material_id=material_id
            )
        )

    db.commit()
    db.refresh(version)
    return row_to_dict(version)


@router.get("/workspaces/{workspace_id}/artifacts/{artifact_id}/versions")
def list_versions(
    workspace_id: uuid.UUID,
    artifact_id: uuid.UUID,
    db: Session = Depends(get_db),
    _ws: Workspace = Depends(require_workspace),
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
    _ws: Workspace = Depends(require_workspace),
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
    promoted_by: str
    expected_row_version: int | None = None


@router.post("/workspaces/{workspace_id}/artifacts/{artifact_id}/versions/{version_id}/promote")
def promote_content_version(
    workspace_id: uuid.UUID,
    artifact_id: uuid.UUID,
    version_id: uuid.UUID,
    body: PromoteVersionRequest,
    db: Session = Depends(get_db),
    _ws: Workspace = Depends(require_workspace),
):
    _require_artifact_in_workspace(db, workspace_id, artifact_id)
    version = promote_version(
        db, artifact_id, version_id, body.promoted_by, body.expected_row_version
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
    _ws: Workspace = Depends(require_workspace),
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
    _ws: Workspace = Depends(require_workspace),
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


class WithdrawMaterialRequest(BaseModel):
    withdrawn_by: str


@router.post("/workspaces/{workspace_id}/materials/{material_id}/withdraw")
def withdraw_material_endpoint(
    workspace_id: uuid.UUID,
    material_id: uuid.UUID,
    body: WithdrawMaterialRequest,
    db: Session = Depends(get_db),
    _ws: Workspace = Depends(require_workspace),
):
    material = db.get(Material, material_id)
    if material is None or material.workspace_id != workspace_id:
        raise HTTPException(status_code=404, detail="material not found in this workspace")
    return withdraw_material(db, material_id, body.withdrawn_by)
