import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import require_workspace
from app.api.serialize import row_to_dict
from app.db import get_db
from app.models.identity import Workspace
from app.models.knowledge import MarketObservation, Playbook

router = APIRouter(tags=["knowledge"])


def utcnow():
    return datetime.now(timezone.utc)


class CreateMarketObservationRequest(BaseModel):
    source: str | None = None
    platform: str | None = None
    collected_at: datetime
    applicable_track: str | None = None
    scope_ref: dict = {}
    mechanism_summary: str | None = None
    layer: str = "raw"  # raw | analysis | homogeneous_judgment
    valid_until: datetime | None = None


@router.post("/workspaces/{workspace_id}/market-observations")
def create_market_observation(
    workspace_id: uuid.UUID,
    body: CreateMarketObservationRequest,
    db: Session = Depends(get_db),
    _ws: Workspace = Depends(require_workspace),
):
    if body.layer not in ("raw", "analysis", "homogeneous_judgment"):
        raise HTTPException(
            status_code=422, detail="layer must be one of: raw, analysis, homogeneous_judgment"
        )
    obs = MarketObservation(
        workspace_id=workspace_id,
        source=body.source,
        platform=body.platform,
        collected_at=body.collected_at,
        applicable_track=body.applicable_track,
        scope_ref=body.scope_ref,
        mechanism_summary=body.mechanism_summary,
        layer=body.layer,
        valid_until=body.valid_until,
    )
    db.add(obs)
    db.commit()
    db.refresh(obs)
    return row_to_dict(obs)


@router.get("/workspaces/{workspace_id}/market-observations")
def list_market_observations(
    workspace_id: uuid.UUID,
    db: Session = Depends(get_db),
    _ws: Workspace = Depends(require_workspace),
):
    """Returns every observation with an explicit is_expired flag computed
    against "now" -- a stale observation is never silently presented as
    current, and an empty list is a legitimate, honest "no comparison
    available yet" answer rather than something to paper over.
    """

    rows = db.execute(
        select(MarketObservation).where(MarketObservation.workspace_id == workspace_id)
    ).scalars().all()
    now = utcnow()
    out = []
    for obs in rows:
        d = row_to_dict(obs)
        d["is_expired"] = bool(obs.valid_until and obs.valid_until.replace(tzinfo=timezone.utc) < now)
        out.append(d)
    return out


class CreatePlaybookRequest(BaseModel):
    name: str
    proposed_by: str | None = None
    scope_ref: dict = {}
    observation_status: str | None = None
    rationale: str | None = None


@router.post("/workspaces/{workspace_id}/playbooks")
def create_or_version_playbook(
    workspace_id: uuid.UUID,
    body: CreatePlaybookRequest,
    db: Session = Depends(get_db),
    _ws: Workspace = Depends(require_workspace),
):
    """Creates a new playbook, or a new version of an existing one (matched
    by name within the workspace). The prior current version is chained via
    supersedes_playbook_id, never mutated or deleted -- 打法's professional
    content is whatever the caller (M3/user) proposes; M2 only versions and
    stores it.
    """

    prior = db.execute(
        select(Playbook).where(
            Playbook.workspace_id == workspace_id,
            Playbook.name == body.name,
            Playbook.is_current.is_(True),
        )
    ).scalar_one_or_none()

    playbook = Playbook(
        workspace_id=workspace_id,
        name=body.name,
        version_no=(prior.version_no + 1) if prior else 1,
        is_current=True,
        proposed_by=body.proposed_by,
        scope_ref=body.scope_ref,
        observation_status=body.observation_status,
        rationale=body.rationale,
        supersedes_playbook_id=prior.id if prior else None,
    )
    db.add(playbook)

    if prior is not None:
        db.execute(
            update(Playbook)
            .where(Playbook.id == prior.id, Playbook.is_current.is_(True))
            .values(is_current=False, superseded_at=utcnow(), row_version=Playbook.row_version + 1)
        )

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="concurrent modification: another playbook version won the race; retry",
        )
    db.refresh(playbook)
    return row_to_dict(playbook)


@router.get("/workspaces/{workspace_id}/playbooks/{name}/current")
def get_current_playbook(
    workspace_id: uuid.UUID,
    name: str,
    db: Session = Depends(get_db),
    _ws: Workspace = Depends(require_workspace),
):
    playbook = db.execute(
        select(Playbook).where(
            Playbook.workspace_id == workspace_id,
            Playbook.name == name,
            Playbook.is_current.is_(True),
        )
    ).scalar_one_or_none()
    if playbook is None:
        raise HTTPException(status_code=404, detail="no current playbook with this name")
    return row_to_dict(playbook)


@router.get("/workspaces/{workspace_id}/playbooks/{name}/versions")
def list_playbook_versions(
    workspace_id: uuid.UUID,
    name: str,
    db: Session = Depends(get_db),
    _ws: Workspace = Depends(require_workspace),
):
    rows = db.execute(
        select(Playbook)
        .where(Playbook.workspace_id == workspace_id, Playbook.name == name)
        .order_by(Playbook.version_no.asc())
    ).scalars().all()
    return [row_to_dict(p) for p in rows]
