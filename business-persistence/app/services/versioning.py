from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.content import (
    ContentVersion,
    ContentVersionMaterialDependency,
    Material,
)
from app.models.publish import PublishInstance


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def promote_version(
    db: Session,
    artifact_id,
    version_id,
    promoted_by: str,
    expected_row_version: int | None,
) -> ContentVersion:
    """Atomically make `version_id` the current version of `artifact_id`.

    Idempotent: promoting a version that is already current is a no-op and
    returns it unchanged. Optimistic-concurrency-safe: if the caller passes
    expected_row_version and it no longer matches, this raises 409 instead
    of silently overwriting a concurrent promotion (last-write-wins is
    never allowed here). The database's own partial unique index
    (uq_content_version_current) is the final backstop even if the
    application-level check above is bypassed.
    """

    target: ContentVersion | None = db.get(ContentVersion, version_id)
    if target is None or target.artifact_id != artifact_id:
        raise HTTPException(status_code=404, detail="content_version not found for artifact")

    if target.invalidated_at is not None:
        raise HTTPException(
            status_code=409,
            detail="cannot promote a version invalidated by a material withdrawal",
        )

    if target.is_current:
        return target

    if expected_row_version is not None and target.row_version != expected_row_version:
        raise HTTPException(
            status_code=409,
            detail="concurrent modification: version row_version does not match; re-read and retry",
        )

    now = utcnow()

    # Unset whatever is currently current for this artifact (there is at
    # most one such row thanks to uq_content_version_current).
    current_stmt = (
        update(ContentVersion)
        .where(
            ContentVersion.artifact_id == artifact_id,
            ContentVersion.is_current.is_(True),
        )
        .values(is_current=False, superseded_at=now, row_version=ContentVersion.row_version + 1)
    )

    # Flip the target on, guarded by the row_version we validated above so a
    # concurrent promote of the SAME target loses the race cleanly.
    where_clause = [ContentVersion.id == version_id, ContentVersion.is_current.is_(False)]
    if expected_row_version is not None:
        where_clause.append(ContentVersion.row_version == expected_row_version)

    target_stmt = (
        update(ContentVersion)
        .where(*where_clause)
        .values(
            is_current=True,
            promoted_by=promoted_by,
            promoted_at=now,
            row_version=ContentVersion.row_version + 1,
        )
    )

    # Postgres checks a non-deferrable unique index at statement-execution
    # time, not just at COMMIT -- so a concurrent-promotion UniqueViolation
    # can surface on either db.execute() call below, not only on commit.
    # Both statements and the commit must share one try/except.
    try:
        db.execute(current_stmt)
        result = db.execute(target_stmt)

        if result.rowcount == 0:
            db.rollback()
            raise HTTPException(
                status_code=409,
                detail="concurrent modification: another promotion won the race; re-read and retry",
            )

        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="concurrent modification: uq_content_version_current violated; re-read and retry",
        )

    db.refresh(target)
    return target


def withdraw_material(db: Session, material_id, withdrawn_by: str) -> dict:
    """Withdraw a material and cascade invalidation to whatever unpublished
    content depends on it. Idempotent: withdrawing an already-withdrawn
    material returns the same result without double-processing.

    "Unpublished" is checked by taking a row lock (SELECT ... FOR UPDATE) on
    every candidate content_version FIRST, and only reading whether a
    publish_instance exists for it AFTER that lock is held. This is what
    actually closes the race against register_publish_instance
    (app/api/publish.py), which takes the same row lock before it inserts a
    publish_instance: whichever call reaches a given content_version's lock
    first forces the other to wait, and the loser then observes the
    winner's fully-committed result rather than a stale read. A published
    version can therefore never be invalidated by a later withdrawal no
    matter how the two transactions interleave.
    """

    material: Material | None = db.get(Material, material_id)
    if material is None:
        raise HTTPException(status_code=404, detail="material not found")

    now = utcnow()
    already_withdrawn = material.withdrawn_at is not None
    if not already_withdrawn:
        db.execute(
            update(Material)
            .where(Material.id == material_id, Material.withdrawn_at.is_(None))
            .values(withdrawn_at=now, withdrawn_by=withdrawn_by)
        )
        db.commit()
        db.refresh(material)
        already_withdrawn = False
    withdrawn_at = material.withdrawn_at

    dependent_version_ids = [
        row[0]
        for row in db.execute(
            select(ContentVersionMaterialDependency.content_version_id).where(
                ContentVersionMaterialDependency.material_id == material_id
            )
        ).all()
    ]

    invalidated_version_ids: list = []
    if dependent_version_ids:
        # Lock every candidate content_version row FIRST, before asking
        # whether any of them is published. This is what actually
        # serializes against register_publish_instance's own
        # SELECT ... FOR UPDATE on the same row (app/api/publish.py): a
        # publish still in flight forces this call to block right here
        # until that publish commits or rolls back, and a publish that
        # starts after this lock is acquired blocks on ITS OWN lock
        # attempt until this transaction commits.
        #
        # An earlier version of this function expressed the "not published"
        # condition as a NOT EXISTS subquery inside a single UPDATE
        # statement. That looked atomic but wasn't: it does not reliably
        # force Postgres to wait for a concurrent publish's row lock or to
        # re-evaluate the subquery against fresh data once a wait does
        # happen, so the race it was meant to close kept reproducing under
        # concurrent load (confirmed after the fact by direct testing).
        # Locking first, then reading, then writing -- as three separate
        # statements -- is the pattern that's actually guaranteed correct.
        locked_ids = [
            row[0]
            for row in db.execute(
                select(ContentVersion.id)
                .where(ContentVersion.id.in_(dependent_version_ids))
                .with_for_update()
            ).all()
        ]

        # Only now, holding the locks, is it safe to ask "which of these are
        # already published" -- any publish that could still change the
        # answer has either already committed (and this SELECT sees it) or
        # is blocked waiting for the locks this call just took.
        published_ids = {
            row[0]
            for row in db.execute(
                select(PublishInstance.content_version_id).where(
                    PublishInstance.content_version_id.in_(locked_ids)
                )
            ).all()
        }
        eligible_ids = [vid for vid in locked_ids if vid not in published_ids]

        if eligible_ids:
            stmt = (
                update(ContentVersion)
                .where(
                    ContentVersion.id.in_(eligible_ids),
                    ContentVersion.invalidated_at.is_(None),
                )
                .values(
                    invalidated_at=now,
                    invalidation_reason=f"depends on withdrawn material {material_id}",
                )
                .returning(ContentVersion.id)
            )
            result = db.execute(stmt)
            invalidated_version_ids = [row[0] for row in result.fetchall()]
        db.commit()

    return {
        "material_id": str(material_id),
        "already_withdrawn": already_withdrawn,
        "withdrawn_at": withdrawn_at.isoformat(),
        "affected_content_version_ids": [str(v) for v in dependent_version_ids],
        "invalidated_version_ids": [str(v) for v in invalidated_version_ids],
    }
