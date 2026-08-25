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

    "Unpublished" is defined structurally: a content_version with zero
    publish_instances. Published versions are history and are never
    touched, even if they depended on this material.
    """

    material: Material | None = db.get(Material, material_id)
    if material is None:
        raise HTTPException(status_code=404, detail="material not found")

    now = utcnow()
    already_withdrawn = material.withdrawn_at is not None
    if not already_withdrawn:
        material.withdrawn_at = now
        material.withdrawn_by = withdrawn_by

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
        published_version_ids = {
            row[0]
            for row in db.execute(
                select(PublishInstance.content_version_id).where(
                    PublishInstance.content_version_id.in_(dependent_version_ids)
                )
            ).all()
        }
        candidates = db.execute(
            select(ContentVersion).where(
                ContentVersion.id.in_(dependent_version_ids),
                ContentVersion.invalidated_at.is_(None),
            )
        ).scalars().all()
        for version in candidates:
            if version.id in published_version_ids:
                continue
            version.invalidated_at = now
            version.invalidation_reason = f"depends on withdrawn material {material_id}"
            invalidated_version_ids.append(version.id)

    db.commit()

    return {
        "material_id": str(material_id),
        "already_withdrawn": already_withdrawn,
        "withdrawn_at": material.withdrawn_at.isoformat(),
        "affected_content_version_ids": [str(v) for v in dependent_version_ids],
        "invalidated_version_ids": [str(v) for v in invalidated_version_ids],
    }
