"""market observation permission semantics

M2_POST_DONE_REBASE v1.2 (R-03/R-04/R-05): market_observations previously
recorded source/platform/collected_at/applicable_track/scope_ref/
mechanism_summary/layer/valid_until, but had no way to express whether the
observation is actually *permitted* to be used, by whom, under what limits,
or which specific account/task/time-window it applies to -- workspace
membership was the only gate, which conflates "can this actor see the
workspace" with "is this specific observation allowed to be used". This
migration adds those fields without touching any existing column, table, or
Dify-facing contract.

permission_status is added NOT NULL with server_default='unknown' so every
pre-existing row is backfilled to "unknown" (never retroactively defaulted
to "allowed" -- an absent permission decision must never be treated as one,
per R-05.2). The server_default is dropped after backfill so future inserts
must go through the model's Python-side default instead of a drifting
DB-side one (same pattern as task_run_states.row_version in
db747c8a1f80).

idempotency_key + a PARTIAL unique index (WHERE idempotency_key IS NOT
NULL) on (workspace_id, account_id, idempotency_key) are added so the
create/import path can satisfy this task_id's standing idempotency/
concurrency requirement -- retry-safe, no cross-workspace key collision,
and (per independent review) no cross-account key collision either,
matching the bug class already fixed once for cycles/cycle_decisions in
c3f8b2e6d0a4. The index uses NULLS NOT DISTINCT (Postgres 15+) on that
subset specifically so two workspace-wide (account_id IS NULL) creates
with the same key still dedupe as a retry -- plain SQL NULL-distinct
semantics would otherwise let those silently create duplicates instead.
The index must stay partial: with 61 pre-existing rows all backfilled to
account_id=NULL, idempotency_key=NULL, applying NULLS NOT DISTINCT
without the WHERE clause made every one of those rows collide with every
other as a "duplicate" of (workspace_id, NULL, NULL) -- confirmed live,
this is exactly what happened on first attempt (UniqueViolation on
upgrade, cleanly rolled back by Alembic's transactional DDL, no partial
schema left behind). Existing rows keep idempotency_key=NULL and are
excluded from the index entirely, unaffected.

Revision ID: 17368b750d3b
Revises: c3f8b2e6d0a4
Create Date: 2026-08-26 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = '17368b750d3b'
down_revision: Union[str, None] = 'c3f8b2e6d0a4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('market_observations', sa.Column('source_type', sa.String(length=64), nullable=True))
    op.add_column(
        'market_observations', sa.Column('source_reference', sa.String(length=1024), nullable=True)
    )
    op.add_column(
        'market_observations', sa.Column('source_provider', sa.String(length=255), nullable=True)
    )
    op.add_column('market_observations', sa.Column('account_id', sa.UUID(), nullable=True))
    op.add_column('market_observations', sa.Column('applicable_task_id', sa.UUID(), nullable=True))
    op.add_column(
        'market_observations',
        sa.Column('applicable_period_start', sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        'market_observations',
        sa.Column('applicable_period_end', sa.DateTime(timezone=True), nullable=True),
    )

    op.add_column(
        'market_observations',
        sa.Column(
            'permission_status', sa.String(length=32), nullable=False, server_default='unknown'
        ),
    )
    op.alter_column('market_observations', 'permission_status', server_default=None)
    op.add_column(
        'market_observations', sa.Column('permission_basis', postgresql.JSONB(), nullable=True)
    )
    op.add_column(
        'market_observations', sa.Column('usage_limits', postgresql.JSONB(), nullable=True)
    )
    op.add_column(
        'market_observations',
        sa.Column('permission_confirmed_by', sa.String(length=255), nullable=True),
    )
    op.add_column(
        'market_observations',
        sa.Column('permission_confirmed_at', sa.DateTime(timezone=True), nullable=True),
    )

    op.add_column(
        'market_observations', sa.Column('evidence_digest', sa.String(length=64), nullable=True)
    )
    op.add_column(
        'market_observations', sa.Column('idempotency_key', sa.String(length=255), nullable=True)
    )

    op.create_foreign_key(
        'fk_market_observations_account_id', 'market_observations', 'accounts', ['account_id'], ['id']
    )
    op.create_foreign_key(
        'fk_market_observations_applicable_task_id',
        'market_observations',
        'tasks',
        ['applicable_task_id'],
        ['id'],
    )
    op.create_index(
        'ix_market_observations_workspace_account',
        'market_observations',
        ['workspace_id', 'account_id'],
    )
    # Partial unique index, not a plain constraint: applying NULLS NOT
    # DISTINCT across the whole table would make every (workspace_id,
    # account_id) pair's many legitimate no-idempotency-key rows collide
    # with each other, since idempotency_key is NULL for all of them too --
    # only rows that actually supply a key need this uniqueness.
    op.create_index(
        'uq_market_observation_workspace_account_idempotency',
        'market_observations',
        ['workspace_id', 'account_id', 'idempotency_key'],
        unique=True,
        postgresql_where=sa.text('idempotency_key IS NOT NULL'),
        postgresql_nulls_not_distinct=True,
    )


def downgrade() -> None:
    op.drop_index('uq_market_observation_workspace_account_idempotency', table_name='market_observations')
    op.drop_index('ix_market_observations_workspace_account', table_name='market_observations')
    op.drop_constraint(
        'fk_market_observations_applicable_task_id', 'market_observations', type_='foreignkey'
    )
    op.drop_constraint('fk_market_observations_account_id', 'market_observations', type_='foreignkey')

    op.drop_column('market_observations', 'idempotency_key')
    op.drop_column('market_observations', 'evidence_digest')
    op.drop_column('market_observations', 'permission_confirmed_at')
    op.drop_column('market_observations', 'permission_confirmed_by')
    op.drop_column('market_observations', 'usage_limits')
    op.drop_column('market_observations', 'permission_basis')
    op.drop_column('market_observations', 'permission_status')
    op.drop_column('market_observations', 'applicable_period_end')
    op.drop_column('market_observations', 'applicable_period_start')
    op.drop_column('market_observations', 'applicable_task_id')
    op.drop_column('market_observations', 'account_id')
    op.drop_column('market_observations', 'source_provider')
    op.drop_column('market_observations', 'source_reference')
    op.drop_column('market_observations', 'source_type')
