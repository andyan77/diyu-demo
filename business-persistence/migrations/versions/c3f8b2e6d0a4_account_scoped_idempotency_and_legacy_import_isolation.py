"""account-scoped cycle idempotency + isolated legacy-import namespace

Independent review after M2-AC-07/14/15 gap closure found: (1) create_cycle
and record_cycle_decision scoped idempotency by workspace only, so two
different accounts in the same workspace picking the same idempotency_key
by coincidence could collide -- one account's call would silently return
the other account's row; (2) the legacy-import endpoint reused
Task.idempotency_key directly, so a live task-creation caller and a
legacy-import caller could collide the same way, confirmed live to produce
a false-success response and a legacy/live identity merge.

Revision ID: c3f8b2e6d0a4
Revises: a1c5e7d4f2b9
Create Date: 2026-08-25 19:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'c3f8b2e6d0a4'
down_revision: Union[str, None] = 'a1c5e7d4f2b9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint('uq_cycle_workspace_idempotency', 'cycles', type_='unique')
    op.create_unique_constraint(
        'uq_cycle_workspace_account_idempotency',
        'cycles',
        ['workspace_id', 'account_id', 'idempotency_key'],
    )

    op.drop_constraint('uq_cycle_decision_workspace_idempotency', 'cycle_decisions', type_='unique')
    op.create_unique_constraint(
        'uq_cycle_decision_workspace_account_idempotency',
        'cycle_decisions',
        ['workspace_id', 'account_id', 'idempotency_key'],
    )

    op.create_table(
        'legacy_import_records',
        sa.Column('workspace_id', sa.UUID(), nullable=False),
        sa.Column('idempotency_key', sa.String(length=255), nullable=False),
        sa.Column('task_id', sa.UUID(), nullable=False),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ['task_id'], ['tasks.id'], name='fk_legacy_import_records_task_id'
        ),
        sa.ForeignKeyConstraint(
            ['workspace_id'], ['workspaces.id'], name='fk_legacy_import_records_workspace_id'
        ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint(
            'workspace_id', 'idempotency_key', name='uq_legacy_import_workspace_idempotency'
        ),
    )


def _refuse_if_cross_account_duplicates(bind, table: str) -> None:
    """This downgrade widens (workspace_id, account_id, idempotency_key)
    back down to (workspace_id, idempotency_key). Confirmed live against
    the real diyu_business database (not a throwaway/empty copy): once the
    upgraded constraint is in place, it is legitimate and expected for two
    different accounts in the same workspace to share an idempotency_key
    (that's the entire point of the upgrade) -- but exactly that data makes
    the narrower downgrade constraint un-creatable, and Alembic surfaces
    that as a raw IntegrityError stack trace with no guidance. Failing
    fast here with the actual conflicting rows is strictly better than
    letting the ALTER TABLE throw. There is no safe *automatic* resolution
    -- collapsing two different accounts' rows onto one key is a data
    decision, not a schema decision -- so this is a genuine, disclosed
    forward-only point once real cross-account key reuse has occurred, not
    something this migration can silently paper over.
    """

    rows = bind.execute(
        sa.text(
            f"""
            SELECT workspace_id, idempotency_key, count(*) AS n
            FROM {table}
            WHERE idempotency_key IS NOT NULL
            GROUP BY workspace_id, idempotency_key
            HAVING count(*) > 1
            """
        )
    ).fetchall()
    if rows:
        raise RuntimeError(
            f"cannot downgrade {table}: {len(rows)} (workspace_id, idempotency_key) group(s) are "
            "shared by more than one account, which is legitimate under the current "
            "(workspace_id, account_id, idempotency_key) constraint but cannot satisfy the older "
            "(workspace_id, idempotency_key)-only constraint this downgrade would restore. "
            "Resolve which row per group should keep the key (e.g. by moving one to a new key) "
            "before downgrading -- this migration will not guess for you. "
            f"Conflicting groups: {[(str(r.workspace_id), r.idempotency_key, r.n) for r in rows]}"
        )


def downgrade() -> None:
    bind = op.get_bind()
    _refuse_if_cross_account_duplicates(bind, "cycles")
    _refuse_if_cross_account_duplicates(bind, "cycle_decisions")

    op.drop_table('legacy_import_records')

    op.drop_constraint(
        'uq_cycle_decision_workspace_account_idempotency', 'cycle_decisions', type_='unique'
    )
    op.create_unique_constraint(
        'uq_cycle_decision_workspace_idempotency',
        'cycle_decisions',
        ['workspace_id', 'idempotency_key'],
    )

    op.drop_constraint('uq_cycle_workspace_account_idempotency', 'cycles', type_='unique')
    op.create_unique_constraint(
        'uq_cycle_workspace_idempotency', 'cycles', ['workspace_id', 'idempotency_key']
    )
