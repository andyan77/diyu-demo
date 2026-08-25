"""content version invalidation fields

Revision ID: 6bc000bb178d
Revises: 6033064ae1ed
Create Date: 2026-08-25 17:25:04.628825

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '6bc000bb178d'
down_revision: Union[str, None] = '6033064ae1ed'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('content_versions', sa.Column('invalidated_at', sa.DateTime(), nullable=True))
    op.add_column(
        'content_versions', sa.Column('invalidation_reason', sa.String(length=1024), nullable=True)
    )


def downgrade() -> None:
    op.drop_column('content_versions', 'invalidation_reason')
    op.drop_column('content_versions', 'invalidated_at')
