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
from app.models.identity import Account
from app.models.operations import CampaignOverride, Cycle, CycleDecision

router = APIRouter(tags=["operations"])


def utcnow():
    return datetime.now(timezone.utc)


def _require_account_in_workspace(db: Session, workspace_id: uuid.UUID, account_id: uuid.UUID) -> Account:
    account = db.get(Account, account_id)
    if account is None or account.workspace_id != workspace_id:
        raise HTTPException(status_code=404, detail="account not found in this workspace")
    return account


class CreateCycleRequest(BaseModel):
    idempotency_key: str
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
    ctx: MembershipContext = Depends(require_membership),
):
    """Create a new cycle and atomically make it the current baseline for
    this account. The previous current cycle (if any) is chained via
    supersedes_cycle_id -- never mutated in place, never deleted, always
    readable. This is the mechanism a Cycle N -> N+1 transition uses.
    """

    _require_account_in_workspace(db, workspace_id, body.account_id)

    # scoped by account, not just workspace: two different accounts in the
    # same workspace picking the same idempotency_key by coincidence must
    # never collide and hand one account back the other's cycle.
    existing = db.execute(
        select(Cycle).where(
            Cycle.workspace_id == workspace_id,
            Cycle.account_id == body.account_id,
            Cycle.idempotency_key == body.idempotency_key,
        )
    ).scalar_one_or_none()
    if existing:
        return row_to_dict(existing)

    prior = db.execute(
        select(Cycle).where(
            Cycle.workspace_id == workspace_id,
            Cycle.account_id == body.account_id,
            Cycle.is_current.is_(True),
        )
    ).scalar_one_or_none()

    cycle = Cycle(
        workspace_id=workspace_id,
        account_id=body.account_id,
        label=body.label,
        start_at=body.start_at,
        end_at=body.end_at,
        idempotency_key=body.idempotency_key,
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
        existing = db.execute(
            select(Cycle).where(
                Cycle.workspace_id == workspace_id,
                Cycle.account_id == body.account_id,
                Cycle.idempotency_key == body.idempotency_key,
            )
        ).scalar_one_or_none()
        if existing:
            return row_to_dict(existing)
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
    ctx: MembershipContext = Depends(require_membership),
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
    ctx: MembershipContext = Depends(require_membership),
):
    rows = db.execute(
        select(Cycle)
        .where(Cycle.workspace_id == workspace_id, Cycle.account_id == account_id)
        .order_by(Cycle.created_at.desc())
    ).scalars().all()
    return [row_to_dict(c) for c in rows]


class RecordCycleDecisionRequest(BaseModel):
    idempotency_key: str
    cycle_id: uuid.UUID
    decision: str  # "adjusted" | "kept_unchanged"
    source: str | None = None
    rationale: str | None = None
    based_on: dict = {}
    resulting_cycle_id: uuid.UUID | None = None


@router.post("/workspaces/{workspace_id}/accounts/{account_id}/cycles/decisions")
def record_cycle_decision(
    workspace_id: uuid.UUID,
    account_id: uuid.UUID,
    body: RecordCycleDecisionRequest,
    db: Session = Depends(get_db),
    ctx: MembershipContext = Depends(require_membership),
):
    """Records M3's verdict after evaluating a cycle -- M2 never makes this
    call itself, it only persists what the caller (M3, or a contract-test
    stand-in for it) asserts. decision="adjusted" must be paired with a
    cycle that was actually created via POST .../cycles and supersedes the
    evaluated cycle; decision="kept_unchanged" must not reference a
    resulting cycle at all -- the current cycle stays exactly what it was,
    this call only makes the evaluate-and-hold decision observable instead
    of leaving it invisible.
    """

    _require_account_in_workspace(db, workspace_id, account_id)

    # scoped by account, not just workspace -- same reasoning as
    # create_cycle's idempotency lookup above.
    existing = db.execute(
        select(CycleDecision).where(
            CycleDecision.workspace_id == workspace_id,
            CycleDecision.account_id == account_id,
            CycleDecision.idempotency_key == body.idempotency_key,
        )
    ).scalar_one_or_none()
    if existing:
        return row_to_dict(existing)

    cycle = db.get(Cycle, body.cycle_id)
    if cycle is None or cycle.workspace_id != workspace_id or cycle.account_id != account_id:
        raise HTTPException(status_code=404, detail="cycle not found for this account")

    if body.decision not in ("adjusted", "kept_unchanged"):
        raise HTTPException(
            status_code=422, detail="decision must be 'adjusted' or 'kept_unchanged'"
        )

    if body.decision == "adjusted":
        if body.resulting_cycle_id is None:
            raise HTTPException(
                status_code=422, detail="decision='adjusted' requires resulting_cycle_id"
            )
        resulting = db.get(Cycle, body.resulting_cycle_id)
        if (
            resulting is None
            or resulting.workspace_id != workspace_id
            or resulting.account_id != account_id
            or resulting.supersedes_cycle_id != body.cycle_id
        ):
            raise HTTPException(
                status_code=422,
                detail="resulting_cycle_id must be a cycle for this account that supersedes cycle_id",
            )
    else:
        if body.resulting_cycle_id is not None:
            raise HTTPException(
                status_code=422, detail="decision='kept_unchanged' must not set resulting_cycle_id"
            )
        # Purely structural, not a judgment call: "kept unchanged" only
        # makes sense as a verdict on whatever cycle was current at
        # decision time. A cycle that's already been superseded by the
        # time this call arrives means some OTHER decision already moved
        # things on -- recording "kept unchanged" against it now would
        # make decisions/latest and /cycles/current visibly disagree about
        # what happened to that cycle.
        if not cycle.is_current:
            raise HTTPException(
                status_code=422,
                detail="cycle_id is no longer the current cycle; kept_unchanged must reference "
                "the cycle that was current at decision time",
            )

    record = CycleDecision(
        workspace_id=workspace_id,
        account_id=account_id,
        cycle_id=body.cycle_id,
        decision=body.decision,
        source=body.source,
        rationale=body.rationale,
        based_on=body.based_on,
        resulting_cycle_id=body.resulting_cycle_id,
        idempotency_key=body.idempotency_key,
    )
    db.add(record)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        existing = db.execute(
            select(CycleDecision).where(
                CycleDecision.workspace_id == workspace_id,
                CycleDecision.account_id == account_id,
                CycleDecision.idempotency_key == body.idempotency_key,
            )
        ).scalar_one_or_none()
        if existing:
            return row_to_dict(existing)
        raise
    db.refresh(record)
    return row_to_dict(record)


@router.get("/workspaces/{workspace_id}/accounts/{account_id}/cycles/decisions/latest")
def get_latest_cycle_decision(
    workspace_id: uuid.UUID,
    account_id: uuid.UUID,
    db: Session = Depends(get_db),
    ctx: MembershipContext = Depends(require_membership),
):
    record = db.execute(
        select(CycleDecision)
        .where(CycleDecision.workspace_id == workspace_id, CycleDecision.account_id == account_id)
        .order_by(CycleDecision.created_at.desc())
        .limit(1)
    ).scalar_one_or_none()
    if record is None:
        return {"decision": "none_recorded"}
    return row_to_dict(record)


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
    ctx: MembershipContext = Depends(require_membership),
):
    _require_account_in_workspace(db, workspace_id, body.account_id)

    cycle = db.get(Cycle, body.cycle_id)
    if cycle is None or cycle.workspace_id != workspace_id:
        raise HTTPException(status_code=404, detail="cycle not found in this workspace")
    if cycle.account_id != body.account_id:
        raise HTTPException(
            status_code=422, detail="cycle_id does not belong to the given account_id"
        )

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
    ctx: MembershipContext = Depends(require_membership),
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

    result = db.execute(
        update(CampaignOverride)
        .where(CampaignOverride.id == override_id, CampaignOverride.status == "active")
        .values(status="ended", ended_at=utcnow(), row_version=CampaignOverride.row_version + 1)
    )
    if result.rowcount == 0:
        db.rollback()
        db.refresh(override)
        return row_to_dict(override)
    db.commit()
    db.refresh(override)
    return row_to_dict(override)


@router.get("/workspaces/{workspace_id}/accounts/{account_id}/campaign-overrides/active")
def get_active_overrides(
    workspace_id: uuid.UUID,
    account_id: uuid.UUID,
    db: Session = Depends(get_db),
    ctx: MembershipContext = Depends(require_membership),
):
    rows = db.execute(
        select(CampaignOverride).where(
            CampaignOverride.workspace_id == workspace_id,
            CampaignOverride.account_id == account_id,
            CampaignOverride.status == "active",
        )
    ).scalars().all()
    return [row_to_dict(o) for o in rows]
