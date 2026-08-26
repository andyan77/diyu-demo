"""cycle decisions (M2-AC-07: M3 adjust-vs-kept-unchanged recording)

Revision ID: a1c5e7d4f2b9
Revises: db747c8a1f80
Create Date: 2026-08-25 18:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = 'a1c5e7d4f2b9'
down_revision: Union[str, None] = 'db747c8a1f80'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'cycle_decisions',
        sa.Column('workspace_id', sa.UUID(), nullable=False),
        sa.Column('account_id', sa.UUID(), nullable=False),
        sa.Column('cycle_id', sa.UUID(), nullable=False),
        sa.Column('decision', sa.String(length=32), nullable=False),
        sa.Column('source', sa.String(length=255), nullable=True),
        sa.Column('rationale', sa.String(length=4096), nullable=True),
        sa.Column('based_on', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('resulting_cycle_id', sa.UUID(), nullable=True),
        sa.Column('idempotency_key', sa.String(length=255), nullable=True),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['account_id'], ['accounts.id'], name='fk_cycle_decisions_account_id'),
        sa.ForeignKeyConstraint(['cycle_id'], ['cycles.id'], name='fk_cycle_decisions_cycle_id'),
        sa.ForeignKeyConstraint(
            ['resulting_cycle_id'], ['cycles.id'], name='fk_cycle_decisions_resulting_cycle_id'
        ),
        sa.ForeignKeyConstraint(
            ['workspace_id'], ['workspaces.id'], name='fk_cycle_decisions_workspace_id'
        ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint(
            'workspace_id', 'idempotency_key', name='uq_cycle_decision_workspace_idempotency'
        ),
    )
    op.create_index(
        'ix_cycle_decisions_workspace_id', 'cycle_decisions', ['workspace_id'], unique=False
    )
    op.create_index(
        'ix_cycle_decisions_account_id', 'cycle_decisions', ['account_id'], unique=False
    )


def downgrade() -> None:
    op.drop_index('ix_cycle_decisions_account_id', table_name='cycle_decisions')
    op.drop_index('ix_cycle_decisions_workspace_id', table_name='cycle_decisions')
    op.drop_table('cycle_decisions')
