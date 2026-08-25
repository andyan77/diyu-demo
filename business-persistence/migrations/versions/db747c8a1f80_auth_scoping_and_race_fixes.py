"""auth_scoping_and_race_fixes

Revision ID: db747c8a1f80
Revises: fb5e3889277c
Create Date: 2026-08-25 19:36:04.594065

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = 'db747c8a1f80'
down_revision: Union[str, None] = 'fb5e3889277c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('campaign_overrides', 'scope_start',
               existing_type=postgresql.TIMESTAMP(),
               type_=sa.DateTime(timezone=True),
               existing_nullable=False)
    op.alter_column('campaign_overrides', 'scope_end',
               existing_type=postgresql.TIMESTAMP(),
               type_=sa.DateTime(timezone=True),
               existing_nullable=True)
    op.alter_column('campaign_overrides', 'ended_at',
               existing_type=postgresql.TIMESTAMP(),
               type_=sa.DateTime(timezone=True),
               existing_nullable=True)
    op.add_column('content_versions', sa.Column('idempotency_key', sa.String(length=255), nullable=True))
    op.alter_column('content_versions', 'promoted_at',
               existing_type=postgresql.TIMESTAMP(),
               type_=sa.DateTime(timezone=True),
               existing_nullable=True)
    op.alter_column('content_versions', 'superseded_at',
               existing_type=postgresql.TIMESTAMP(),
               type_=sa.DateTime(timezone=True),
               existing_nullable=True)
    op.alter_column('content_versions', 'invalidated_at',
               existing_type=postgresql.TIMESTAMP(),
               type_=sa.DateTime(timezone=True),
               existing_nullable=True)
    op.create_unique_constraint('uq_content_version_artifact_idempotency', 'content_versions', ['artifact_id', 'idempotency_key'])
    op.add_column('cycles', sa.Column('idempotency_key', sa.String(length=255), nullable=True))
    op.alter_column('cycles', 'start_at',
               existing_type=postgresql.TIMESTAMP(),
               type_=sa.DateTime(timezone=True),
               existing_nullable=False)
    op.alter_column('cycles', 'end_at',
               existing_type=postgresql.TIMESTAMP(),
               type_=sa.DateTime(timezone=True),
               existing_nullable=True)
    op.create_unique_constraint('uq_cycle_workspace_idempotency', 'cycles', ['workspace_id', 'idempotency_key'])

    # publish_instances.workspace_id is backfilled BEFORE feedback_records
    # below, which derives its own workspace_id from publish_instances --
    # order matters here even though both blocks are in one migration.
    op.add_column('publish_instances', sa.Column('workspace_id', sa.UUID(), nullable=True))
    op.execute(
        """
        UPDATE publish_instances pi
        SET workspace_id = t.workspace_id
        FROM content_versions cv
        JOIN artifacts a ON a.id = cv.artifact_id
        JOIN tasks t ON t.id = a.task_id
        WHERE cv.id = pi.content_version_id
        """
    )
    op.alter_column('publish_instances', 'workspace_id', existing_type=sa.UUID(), nullable=False)
    op.alter_column('publish_instances', 'published_at',
               existing_type=postgresql.TIMESTAMP(),
               type_=sa.DateTime(timezone=True),
               existing_nullable=False)
    op.drop_constraint('publish_instances_idempotency_key_key', 'publish_instances', type_='unique')
    op.create_index('ix_publish_instances_workspace_id', 'publish_instances', ['workspace_id'], unique=False)
    op.create_unique_constraint('uq_publish_instance_workspace_idempotency', 'publish_instances', ['workspace_id', 'idempotency_key'])
    op.create_foreign_key('fk_publish_instances_workspace_id', 'publish_instances', 'workspaces', ['workspace_id'], ['id'])

    op.add_column('feedback_records', sa.Column('workspace_id', sa.UUID(), nullable=True))
    op.add_column('feedback_records', sa.Column('content_version_id', sa.UUID(), nullable=True))
    op.alter_column('feedback_records', 'publish_instance_id',
               existing_type=sa.UUID(),
               nullable=True)
    op.alter_column('feedback_records', 'observed_at',
               existing_type=postgresql.TIMESTAMP(),
               type_=sa.DateTime(timezone=True),
               existing_nullable=True)
    op.alter_column('feedback_records', 'window_start',
               existing_type=postgresql.TIMESTAMP(),
               type_=sa.DateTime(timezone=True),
               existing_nullable=True)
    op.alter_column('feedback_records', 'window_end',
               existing_type=postgresql.TIMESTAMP(),
               type_=sa.DateTime(timezone=True),
               existing_nullable=True)
    op.drop_constraint('feedback_records_idempotency_key_key', 'feedback_records', type_='unique')
    op.create_index('ix_feedback_records_content_version_id', 'feedback_records', ['content_version_id'], unique=False)
    op.create_index('ix_feedback_records_workspace_id', 'feedback_records', ['workspace_id'], unique=False)
    # every pre-existing row has publish_instance_id set (it only becomes
    # optional above), and publish_instances.workspace_id was already
    # backfilled above -- so this covers every row that predates this
    # migration.
    op.execute(
        """
        UPDATE feedback_records fr
        SET workspace_id = pi.workspace_id
        FROM publish_instances pi
        WHERE pi.id = fr.publish_instance_id
        """
    )
    op.alter_column('feedback_records', 'workspace_id', existing_type=sa.UUID(), nullable=False)
    op.create_unique_constraint('uq_feedback_workspace_idempotency', 'feedback_records', ['workspace_id', 'idempotency_key'])
    op.create_foreign_key('fk_feedback_records_workspace_id', 'feedback_records', 'workspaces', ['workspace_id'], ['id'])
    op.create_foreign_key('fk_feedback_records_content_version_id', 'feedback_records', 'content_versions', ['content_version_id'], ['id'])

    op.alter_column('idempotency_records', 'created_at',
               existing_type=postgresql.TIMESTAMP(),
               type_=sa.DateTime(timezone=True),
               existing_nullable=False)
    op.alter_column('market_observations', 'collected_at',
               existing_type=postgresql.TIMESTAMP(),
               type_=sa.DateTime(timezone=True),
               existing_nullable=False)
    op.alter_column('market_observations', 'valid_until',
               existing_type=postgresql.TIMESTAMP(),
               type_=sa.DateTime(timezone=True),
               existing_nullable=True)
    op.alter_column('materials', 'withdrawn_at',
               existing_type=postgresql.TIMESTAMP(),
               type_=sa.DateTime(timezone=True),
               existing_nullable=True)
    op.add_column('playbooks', sa.Column('idempotency_key', sa.String(length=255), nullable=True))
    op.alter_column('playbooks', 'superseded_at',
               existing_type=postgresql.TIMESTAMP(),
               type_=sa.DateTime(timezone=True),
               existing_nullable=True)
    op.create_unique_constraint('uq_playbook_workspace_idempotency', 'playbooks', ['workspace_id', 'idempotency_key'])
    op.add_column('task_run_states', sa.Column('row_version', sa.Integer(), nullable=False, server_default='1'))
    op.alter_column('task_run_states', 'row_version', server_default=None)
    op.alter_column('task_run_states', 'created_at',
               existing_type=postgresql.TIMESTAMP(),
               type_=sa.DateTime(timezone=True),
               existing_nullable=False)
    op.alter_column('task_run_states', 'updated_at',
               existing_type=postgresql.TIMESTAMP(),
               type_=sa.DateTime(timezone=True),
               existing_nullable=False)
    op.drop_constraint('task_snapshots_idempotency_key_key', 'task_snapshots', type_='unique')
    op.create_unique_constraint('uq_task_snapshot_task_idempotency', 'task_snapshots', ['task_id', 'idempotency_key'])
    op.drop_constraint('tasks_idempotency_key_key', 'tasks', type_='unique')
    op.create_unique_constraint('uq_task_workspace_idempotency', 'tasks', ['workspace_id', 'idempotency_key'])


def downgrade() -> None:
    op.drop_constraint('uq_task_workspace_idempotency', 'tasks', type_='unique')
    op.create_unique_constraint('tasks_idempotency_key_key', 'tasks', ['idempotency_key'])
    op.drop_constraint('uq_task_snapshot_task_idempotency', 'task_snapshots', type_='unique')
    op.create_unique_constraint('task_snapshots_idempotency_key_key', 'task_snapshots', ['idempotency_key'])
    op.alter_column('task_run_states', 'updated_at',
               existing_type=sa.DateTime(timezone=True),
               type_=postgresql.TIMESTAMP(),
               existing_nullable=False)
    op.alter_column('task_run_states', 'created_at',
               existing_type=sa.DateTime(timezone=True),
               type_=postgresql.TIMESTAMP(),
               existing_nullable=False)
    op.drop_column('task_run_states', 'row_version')
    op.drop_constraint('uq_playbook_workspace_idempotency', 'playbooks', type_='unique')
    op.alter_column('playbooks', 'superseded_at',
               existing_type=sa.DateTime(timezone=True),
               type_=postgresql.TIMESTAMP(),
               existing_nullable=True)
    op.drop_column('playbooks', 'idempotency_key')
    op.alter_column('materials', 'withdrawn_at',
               existing_type=sa.DateTime(timezone=True),
               type_=postgresql.TIMESTAMP(),
               existing_nullable=True)
    op.alter_column('market_observations', 'valid_until',
               existing_type=sa.DateTime(timezone=True),
               type_=postgresql.TIMESTAMP(),
               existing_nullable=True)
    op.alter_column('market_observations', 'collected_at',
               existing_type=sa.DateTime(timezone=True),
               type_=postgresql.TIMESTAMP(),
               existing_nullable=False)
    op.alter_column('idempotency_records', 'created_at',
               existing_type=sa.DateTime(timezone=True),
               type_=postgresql.TIMESTAMP(),
               existing_nullable=False)

    op.drop_constraint('fk_feedback_records_content_version_id', 'feedback_records', type_='foreignkey')
    op.drop_constraint('fk_feedback_records_workspace_id', 'feedback_records', type_='foreignkey')
    op.drop_constraint('uq_feedback_workspace_idempotency', 'feedback_records', type_='unique')
    op.drop_index('ix_feedback_records_workspace_id', table_name='feedback_records')
    op.drop_index('ix_feedback_records_content_version_id', table_name='feedback_records')
    op.create_unique_constraint('feedback_records_idempotency_key_key', 'feedback_records', ['idempotency_key'])
    op.alter_column('feedback_records', 'window_end',
               existing_type=sa.DateTime(timezone=True),
               type_=postgresql.TIMESTAMP(),
               existing_nullable=True)
    op.alter_column('feedback_records', 'window_start',
               existing_type=sa.DateTime(timezone=True),
               type_=postgresql.TIMESTAMP(),
               existing_nullable=True)
    op.alter_column('feedback_records', 'observed_at',
               existing_type=sa.DateTime(timezone=True),
               type_=postgresql.TIMESTAMP(),
               existing_nullable=True)
    op.alter_column('feedback_records', 'publish_instance_id',
               existing_type=sa.UUID(),
               nullable=False)
    op.drop_column('feedback_records', 'content_version_id')
    op.drop_column('feedback_records', 'workspace_id')

    op.drop_constraint('fk_publish_instances_workspace_id', 'publish_instances', type_='foreignkey')
    op.drop_constraint('uq_publish_instance_workspace_idempotency', 'publish_instances', type_='unique')
    op.drop_index('ix_publish_instances_workspace_id', table_name='publish_instances')
    op.create_unique_constraint('publish_instances_idempotency_key_key', 'publish_instances', ['idempotency_key'])
    op.alter_column('publish_instances', 'published_at',
               existing_type=sa.DateTime(timezone=True),
               type_=postgresql.TIMESTAMP(),
               existing_nullable=False)
    op.drop_column('publish_instances', 'workspace_id')

    op.drop_constraint('uq_cycle_workspace_idempotency', 'cycles', type_='unique')
    op.alter_column('cycles', 'end_at',
               existing_type=sa.DateTime(timezone=True),
               type_=postgresql.TIMESTAMP(),
               existing_nullable=True)
    op.alter_column('cycles', 'start_at',
               existing_type=sa.DateTime(timezone=True),
               type_=postgresql.TIMESTAMP(),
               existing_nullable=False)
    op.drop_column('cycles', 'idempotency_key')
    op.drop_constraint('uq_content_version_artifact_idempotency', 'content_versions', type_='unique')
    op.alter_column('content_versions', 'invalidated_at',
               existing_type=sa.DateTime(timezone=True),
               type_=postgresql.TIMESTAMP(),
               existing_nullable=True)
    op.alter_column('content_versions', 'superseded_at',
               existing_type=sa.DateTime(timezone=True),
               type_=postgresql.TIMESTAMP(),
               existing_nullable=True)
    op.alter_column('content_versions', 'promoted_at',
               existing_type=sa.DateTime(timezone=True),
               type_=postgresql.TIMESTAMP(),
               existing_nullable=True)
    op.drop_column('content_versions', 'idempotency_key')
    op.alter_column('campaign_overrides', 'ended_at',
               existing_type=sa.DateTime(timezone=True),
               type_=postgresql.TIMESTAMP(),
               existing_nullable=True)
    op.alter_column('campaign_overrides', 'scope_end',
               existing_type=sa.DateTime(timezone=True),
               type_=postgresql.TIMESTAMP(),
               existing_nullable=True)
    op.alter_column('campaign_overrides', 'scope_start',
               existing_type=sa.DateTime(timezone=True),
               type_=postgresql.TIMESTAMP(),
               existing_nullable=False)
