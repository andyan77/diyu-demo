import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import MembershipContext, require_membership
from app.api.serialize import row_to_dict
from app.db import get_db
from app.models.content import Task
from app.models.identity import Account
from app.models.knowledge import MarketObservation, Playbook

router = APIRouter(tags=["knowledge"])

# allowed/restricted are permitted for current use (restricted still carries
# usage_limits downstream); unknown/missing/denied are not -- see R-03/R-04.
PERMISSION_STATUSES = ("allowed", "unknown", "missing", "denied", "restricted")
CURRENTLY_USABLE_PERMISSION_STATUSES = ("allowed", "restricted")


def utcnow():
    return datetime.now(timezone.utc)


def _aware(dt: datetime | None) -> datetime | None:
    """Values read back from Postgres can come back naive even though the
    column is TIMESTAMPTZ; compare only after normalizing to aware UTC."""

    if dt is None:
        return None
    return dt if dt.tzinfo is not None else dt.replace(tzinfo=timezone.utc)


def _is_expired(obs: MarketObservation, at: datetime) -> bool:
    valid_until = _aware(obs.valid_until)
    return bool(valid_until and valid_until < at)


def _permission_exclusion_reason(obs: MarketObservation, at: datetime) -> str | None:
    """Permission/expiry only -- no scope, since "scope" is only meaningful
    relative to a specific requested filter (see _scope_exclusion_reason).

    Fail-closed allow-list, not a deny-list: only a status explicitly in
    CURRENTLY_USABLE_PERMISSION_STATUSES can pass. A future/unexpected
    status value (schema drift, a bug elsewhere) is excluded by default
    instead of silently treated as usable.
    """

    if obs.permission_status not in CURRENTLY_USABLE_PERMISSION_STATUSES:
        return f"permission_{obs.permission_status}"
    if _is_expired(obs, at):
        return "expired"
    return None


def _scope_exclusion_reason(
    obs: MarketObservation,
    at: datetime,
    account_id: uuid.UUID | None,
    applicable_track: str | None,
    task_id: uuid.UUID | None,
) -> str | None:
    """An observation with no value set for a given dimension is treated as
    workspace-wide (matches any filter on that dimension); a dimension it
    HAS narrowed itself to must match the requested filter exactly."""

    if account_id is not None and obs.account_id is not None and obs.account_id != account_id:
        return "scope_mismatch"
    if (
        applicable_track is not None
        and obs.applicable_track is not None
        and obs.applicable_track != applicable_track
    ):
        return "scope_mismatch"
    if task_id is not None and obs.applicable_task_id is not None and obs.applicable_task_id != task_id:
        return "scope_mismatch"
    period_start = _aware(obs.applicable_period_start)
    period_end = _aware(obs.applicable_period_end)
    if period_start is not None and at < period_start:
        return "scope_mismatch"
    if period_end is not None and at > period_end:
        return "scope_mismatch"
    return None


def _minimal_projection_fields(obs: MarketObservation) -> dict:
    """Deliberately narrower than row_to_dict: excludes permission_basis,
    permission_confirmed_by/at, created_at, and idempotency_key -- those are
    audit detail for the list endpoint, not part of what M3/M4 need to
    consume a usable observation. permission_status/usage_limits ARE
    included so a "restricted" observation's limits travel with it."""

    return {
        "id": str(obs.id),
        "source_type": obs.source_type,
        "source": obs.source,
        "source_reference": obs.source_reference,
        "source_provider": obs.source_provider,
        "platform": obs.platform,
        "collected_at": obs.collected_at.isoformat() if obs.collected_at else None,
        "applicable_track": obs.applicable_track,
        "account_id": str(obs.account_id) if obs.account_id else None,
        "applicable_task_id": str(obs.applicable_task_id) if obs.applicable_task_id else None,
        "mechanism_summary": obs.mechanism_summary,
        "layer": obs.layer,
        "valid_until": obs.valid_until.isoformat() if obs.valid_until else None,
        "permission_status": obs.permission_status,
        "usage_limits": obs.usage_limits,
        "evidence_digest": obs.evidence_digest,
    }


class CreateMarketObservationRequest(BaseModel):
    source: str | None = None
    source_type: str | None = None
    source_reference: str | None = None
    source_provider: str | None = None
    platform: str | None = None
    collected_at: datetime
    applicable_track: str | None = None
    account_id: uuid.UUID | None = None
    applicable_task_id: uuid.UUID | None = None
    applicable_period_start: datetime | None = None
    applicable_period_end: datetime | None = None
    scope_ref: dict = {}
    mechanism_summary: str | None = None
    layer: str = "raw"  # raw | analysis | homogeneous_judgment
    valid_until: datetime | None = None
    permission_status: str = "unknown"  # allowed | unknown | missing | denied | restricted
    permission_basis: dict | None = None
    usage_limits: dict | None = None
    permission_confirmed_by: str | None = None
    permission_confirmed_at: datetime | None = None
    evidence_digest: str | None = None
    idempotency_key: str | None = None


@router.post("/workspaces/{workspace_id}/market-observations")
def create_market_observation(
    workspace_id: uuid.UUID,
    body: CreateMarketObservationRequest,
    db: Session = Depends(get_db),
    ctx: MembershipContext = Depends(require_membership),
):
    if body.layer not in ("raw", "analysis", "homogeneous_judgment"):
        raise HTTPException(
            status_code=422, detail="layer must be one of: raw, analysis, homogeneous_judgment"
        )
    if body.permission_status not in PERMISSION_STATUSES:
        raise HTTPException(
            status_code=422,
            detail=f"permission_status must be one of: {', '.join(PERMISSION_STATUSES)}",
        )
    period_start = _aware(body.applicable_period_start)
    period_end = _aware(body.applicable_period_end)
    if period_start is not None and period_end is not None and period_start > period_end:
        raise HTTPException(
            status_code=422, detail="applicable_period_start must not be after applicable_period_end"
        )
    if body.account_id is not None:
        account = db.get(Account, body.account_id)
        if account is None or account.workspace_id != workspace_id:
            raise HTTPException(status_code=404, detail="account_id not found in this workspace")
    if body.applicable_task_id is not None:
        task = db.get(Task, body.applicable_task_id)
        if task is None or task.workspace_id != workspace_id:
            raise HTTPException(
                status_code=404, detail="applicable_task_id not found in this workspace"
            )

    if body.idempotency_key is not None:
        # account_id must be part of the lookup, not just workspace_id -- the
        # unique constraint is (workspace_id, account_id, idempotency_key);
        # matching on workspace_id alone here would let a retry with the
        # same key but a DIFFERENT account_id incorrectly return that other
        # account's row instead of hitting the constraint at all.
        existing = db.execute(
            select(MarketObservation).where(
                MarketObservation.workspace_id == workspace_id,
                MarketObservation.account_id == body.account_id,
                MarketObservation.idempotency_key == body.idempotency_key,
            )
        ).scalar_one_or_none()
        if existing:
            return row_to_dict(existing)

    obs = MarketObservation(
        workspace_id=workspace_id,
        source=body.source,
        source_type=body.source_type,
        source_reference=body.source_reference,
        source_provider=body.source_provider,
        platform=body.platform,
        collected_at=body.collected_at,
        applicable_track=body.applicable_track,
        account_id=body.account_id,
        applicable_task_id=body.applicable_task_id,
        applicable_period_start=body.applicable_period_start,
        applicable_period_end=body.applicable_period_end,
        scope_ref=body.scope_ref,
        mechanism_summary=body.mechanism_summary,
        layer=body.layer,
        valid_until=body.valid_until,
        permission_status=body.permission_status,
        permission_basis=body.permission_basis,
        usage_limits=body.usage_limits,
        permission_confirmed_by=body.permission_confirmed_by,
        permission_confirmed_at=body.permission_confirmed_at,
        evidence_digest=body.evidence_digest,
        idempotency_key=body.idempotency_key,
    )
    db.add(obs)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        if body.idempotency_key is not None:
            existing = db.execute(
                select(MarketObservation).where(
                    MarketObservation.workspace_id == workspace_id,
                    MarketObservation.account_id == body.account_id,
                    MarketObservation.idempotency_key == body.idempotency_key,
                )
            ).scalar_one_or_none()
            if existing:
                return row_to_dict(existing)
        raise HTTPException(
            status_code=409,
            detail="concurrent modification: another create with the same idempotency_key won the race; retry",
        )
    db.refresh(obs)
    return row_to_dict(obs)


@router.get("/workspaces/{workspace_id}/market-observations")
def list_market_observations(
    workspace_id: uuid.UUID,
    db: Session = Depends(get_db),
    ctx: MembershipContext = Depends(require_membership),
):
    """Returns every observation with explicit is_expired/currently_usable/
    excluded_reason flags -- a stale or not-yet-permitted observation is
    never silently presented as current, and an empty list is a legitimate,
    honest "no comparison available yet" answer rather than something to
    paper over. This is the full audit history; see the /current endpoint
    for the scope-matched minimal projection M3/M4 actually consume.
    """

    rows = db.execute(
        select(MarketObservation).where(MarketObservation.workspace_id == workspace_id)
    ).scalars().all()
    now = utcnow()
    out = []
    for obs in rows:
        d = row_to_dict(obs)
        d["is_expired"] = _is_expired(obs, now)
        reason = _permission_exclusion_reason(obs, now)
        d["excluded_reason"] = reason
        d["currently_usable"] = reason is None
        out.append(d)
    return out


@router.get("/workspaces/{workspace_id}/market-observations/current")
def get_current_market_observations(
    workspace_id: uuid.UUID,
    account_id: uuid.UUID | None = Query(default=None),
    applicable_track: str | None = Query(default=None),
    task_id: uuid.UUID | None = Query(default=None),
    at: datetime | None = Query(default=None),
    db: Session = Depends(get_db),
    ctx: MembershipContext = Depends(require_membership),
):
    """The minimal, scope-matched projection: only observations with
    sufficient permission (allowed/restricted), not expired, and matching
    every requested scope filter are "usable". Every OTHER observation in
    the workspace is still accounted for in `excluded`, each with its own
    reason -- never silently dropped. M2 only saves and projects here -- it
    never fabricates a comparison, and it never emits a "platform is
    scarce/unique/we've already avoided homogeneity" style conclusion; when
    nothing qualifies it returns an explicit, honest gap instead of an
    ambiguous empty list.

    `at` lets a caller ask "what was/would be usable as of this reference
    time" (e.g. re-deriving what was known at a past decision point), not
    just "right now" -- it defaults to the current time when omitted.
    """

    if account_id is not None:
        account = db.get(Account, account_id)
        if account is None or account.workspace_id != workspace_id:
            raise HTTPException(status_code=404, detail="account_id not found in this workspace")
    if task_id is not None:
        task = db.get(Task, task_id)
        if task is None or task.workspace_id != workspace_id:
            raise HTTPException(status_code=404, detail="task_id not found in this workspace")

    at = _aware(at) or utcnow()
    rows = db.execute(
        select(MarketObservation).where(MarketObservation.workspace_id == workspace_id)
    ).scalars().all()

    usable = []
    excluded = []
    for obs in rows:
        reason = _scope_exclusion_reason(obs, at, account_id, applicable_track, task_id)
        if reason is None:
            reason = _permission_exclusion_reason(obs, at)
        if reason is not None:
            excluded.append({"id": str(obs.id), "reason": reason})
            continue
        usable.append(_minimal_projection_fields(obs))

    if usable:
        gap_reason = None
    elif not rows:
        gap_reason = "no_observation_recorded"
    elif all(e["reason"] == "scope_mismatch" for e in excluded):
        gap_reason = "no_observation_in_scope"
    else:
        gap_reason = "all_observations_excluded"

    return {
        "workspace_id": str(workspace_id),
        "queried_at": at.isoformat(),
        "filters": {
            "account_id": str(account_id) if account_id else None,
            "applicable_track": applicable_track,
            "task_id": str(task_id) if task_id else None,
        },
        "available": bool(usable),
        "observations": usable,
        "excluded": excluded,
        "gap_reason": gap_reason,
    }


class ConfirmMarketObservationPermissionRequest(BaseModel):
    permission_status: str  # allowed | unknown | missing | denied | restricted
    confirmed_by: str
    permission_basis: dict | None = None
    usage_limits: dict | None = None


@router.post("/workspaces/{workspace_id}/market-observations/{observation_id}/permission")
def confirm_market_observation_permission(
    workspace_id: uuid.UUID,
    observation_id: uuid.UUID,
    body: ConfirmMarketObservationPermissionRequest,
    db: Session = Depends(get_db),
    ctx: MembershipContext = Depends(require_membership),
):
    """Records a permission decision made after creation ("适用时" in R-03 --
    confirmation need not happen at create time). Access control (workspace
    membership, already enforced above) and source-usage permission (this
    decision) remain two separate gates: this endpoint only ever narrows or
    corrects the permission_status a human/process has actually decided,
    never infers one from membership.

    permission_basis/usage_limits are updated only when the caller actually
    includes them in the request body (checked via model_fields_set, not
    "is it None") -- a later call that only corrects confirmed_by, or
    re-confirms the same status, must not silently wipe a previously
    recorded usage_limits/permission_basis back to null. To deliberately
    clear one, the caller includes it explicitly as null.
    """

    if body.permission_status not in PERMISSION_STATUSES:
        raise HTTPException(
            status_code=422,
            detail=f"permission_status must be one of: {', '.join(PERMISSION_STATUSES)}",
        )
    obs = db.execute(
        select(MarketObservation).where(
            MarketObservation.id == observation_id, MarketObservation.workspace_id == workspace_id
        )
    ).scalar_one_or_none()
    if obs is None:
        raise HTTPException(status_code=404, detail="market observation not found in this workspace")

    fields_set = body.model_fields_set
    obs.permission_status = body.permission_status
    if "permission_basis" in fields_set:
        obs.permission_basis = body.permission_basis
    if "usage_limits" in fields_set:
        obs.usage_limits = body.usage_limits
    obs.permission_confirmed_by = body.confirmed_by
    obs.permission_confirmed_at = utcnow()
    db.commit()
    db.refresh(obs)
    return row_to_dict(obs)


class CreatePlaybookRequest(BaseModel):
    idempotency_key: str
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
    ctx: MembershipContext = Depends(require_membership),
):
    """Creates a new playbook, or a new version of an existing one (matched
    by name within the workspace). The prior current version is chained via
    supersedes_playbook_id, never mutated or deleted -- 打法's professional
    content is whatever the caller (M3/user) proposes; M2 only versions and
    stores it. idempotency_key is scoped per-workspace
    (uq_playbook_workspace_idempotency): a retry with the same key returns
    the row that retry already created instead of creating a second version.
    """

    existing = db.execute(
        select(Playbook).where(
            Playbook.workspace_id == workspace_id, Playbook.idempotency_key == body.idempotency_key
        )
    ).scalar_one_or_none()
    if existing:
        return row_to_dict(existing)

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
        idempotency_key=body.idempotency_key,
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
        existing = db.execute(
            select(Playbook).where(
                Playbook.workspace_id == workspace_id,
                Playbook.idempotency_key == body.idempotency_key,
            )
        ).scalar_one_or_none()
        if existing:
            return row_to_dict(existing)
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
    ctx: MembershipContext = Depends(require_membership),
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
    ctx: MembershipContext = Depends(require_membership),
):
    rows = db.execute(
        select(Playbook)
        .where(Playbook.workspace_id == workspace_id, Playbook.name == name)
        .order_by(Playbook.version_no.asc())
    ).scalars().all()
    return [row_to_dict(p) for p in rows]
