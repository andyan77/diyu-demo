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
from app.models.operations import CampaignOverride, Cycle

router = APIRouter(tags=["operations"])


def utcnow():
    return datetime.now(timezone.utc)


class CreateCycleRequest(BaseModel):
    account_id: uuid.UUID
    label: str
    start_at: datetime
    end_at: datetime | None = None
    baseline_capacity: float | None = None
    baseline_capacity_source: str | None = None
    actual_capacity: float | None = None
    actual_capacity_source: str | None = None
    expected_publish_count: float | None = None
    expected_publish_count_source: str | None = None


@router.post("/workspaces/{workspace_id}/cycles")
def create_cycle(
    workspace_id: uuid.UUID,
    body: CreateCycleRequest,
    db: Session = Depends(get_db),
    _ws: Workspace = Depends(require_workspace),
):
    """Create a new cycle and atomically make it the current baseline for
    this account. The previous current cycle (if any) is chained via
    supersedes_cycle_id -- never mutated in place, never deleted, always
    readable. This is the mechanism a Cycle N -> N+1 transition uses.
    """

    prior = db.execute(
        select(Cycle).where(Cycle.account_id == body.account_id, Cycle.is_current.is_(True))
    ).scalar_one_or_none()

    cycle = Cycle(
        workspace_id=workspace_id,
        account_id=body.account_id,
        label=body.label,
        start_at=body.start_at,
        end_at=body.end_at,
        baseline_capacity=body.baseline_capacity,
        baseline_capacity_source=body.baseline_capacity_source,
        actual_capacity=body.actual_capacity,
        actual_capacity_source=body.actual_capacity_source,
        expected_publish_count=body.expected_publish_count,
        expected_publish_count_source=body.expected_publish_count_source,
        is_current=True,
        supersedes_cycle_id=prior.id if prior else None,
    )
    db.add(cycle)

    if prior is not None:
        db.execute(
            update(Cycle)
            .where(Cycle.id == prior.id, Cycle.is_current.is_(True))
            .values(is_current=False, row_version=Cycle.row_version + 1)
        )

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="concurrent modification: another cycle transition won the race; retry",
        )
    db.refresh(cycle)
    return row_to_dict(cycle)


@router.get("/workspaces/{workspace_id}/accounts/{account_id}/cycles/current")
def get_current_cycle(
    workspace_id: uuid.UUID,
    account_id: uuid.UUID,
    db: Session = Depends(get_db),
    _ws: Workspace = Depends(require_workspace),
):
    cycle = db.execute(
        select(Cycle).where(
            Cycle.workspace_id == workspace_id,
            Cycle.account_id == account_id,
            Cycle.is_current.is_(True),
        )
    ).scalar_one_or_none()
    if cycle is None:
        raise HTTPException(status_code=404, detail="no current cycle for this account")
    return row_to_dict(cycle)


@router.get("/workspaces/{workspace_id}/accounts/{account_id}/cycles")
def list_cycles(
    workspace_id: uuid.UUID,
    account_id: uuid.UUID,
    db: Session = Depends(get_db),
    _ws: Workspace = Depends(require_workspace),
):
    rows = db.execute(
        select(Cycle)
        .where(Cycle.workspace_id == workspace_id, Cycle.account_id == account_id)
        .order_by(Cycle.created_at.desc())
    ).scalars().all()
    return [row_to_dict(c) for c in rows]


class CreateCampaignOverrideRequest(BaseModel):
    account_id: uuid.UUID
    cycle_id: uuid.UUID
    name: str
    scope_start: datetime
    scope_end: datetime | None = None
    targeted_positions: list = []
    rationale: str | None = None


@router.post("/workspaces/{workspace_id}/campaign-overrides")
def create_campaign_override(
    workspace_id: uuid.UUID,
    body: CreateCampaignOverrideRequest,
    db: Session = Depends(get_db),
    _ws: Workspace = Depends(require_workspace),
):
    cycle = db.get(Cycle, body.cycle_id)
    if cycle is None or cycle.workspace_id != workspace_id:
        raise HTTPException(status_code=404, detail="cycle not found in this workspace")

    override = CampaignOverride(
        workspace_id=workspace_id,
        account_id=body.account_id,
        cycle_id=body.cycle_id,
        name=body.name,
        scope_start=body.scope_start,
        scope_end=body.scope_end,
        targeted_positions=body.targeted_positions,
        rationale=body.rationale,
        status="active",
    )
    db.add(override)
    db.commit()
    db.refresh(override)
    return row_to_dict(override)


@router.post("/workspaces/{workspace_id}/campaign-overrides/{override_id}/end")
def end_campaign_override(
    workspace_id: uuid.UUID,
    override_id: uuid.UUID,
    db: Session = Depends(get_db),
    _ws: Workspace = Depends(require_workspace),
):
    """Ends (or cancels) an override. Idempotent: ending an already-ended
    override just returns its current state. Does NOT touch the cycle
    baseline -- callers should read get_current_cycle afterwards to see
    whatever baseline is *currently* valid, which may have changed while
    the override was active.
    """

    override = db.get(CampaignOverride, override_id)
    if override is None or override.workspace_id != workspace_id:
        raise HTTPException(status_code=404, detail="campaign_override not found")
    if override.status != "active":
        return row_to_dict(override)
    override.status = "ended"
    override.ended_at = utcnow()
    override.row_version += 1
    db.commit()
    db.refresh(override)
    return row_to_dict(override)


@router.get("/workspaces/{workspace_id}/accounts/{account_id}/campaign-overrides/active")
def get_active_overrides(
    workspace_id: uuid.UUID,
    account_id: uuid.UUID,
    db: Session = Depends(get_db),
    _ws: Workspace = Depends(require_workspace),
):
    rows = db.execute(
        select(CampaignOverride).where(
            CampaignOverride.workspace_id == workspace_id,
            CampaignOverride.account_id == account_id,
            CampaignOverride.status == "active",
        )
    ).scalars().all()
    return [row_to_dict(o) for o in rows]
