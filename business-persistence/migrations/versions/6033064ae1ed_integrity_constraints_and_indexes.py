"""integrity constraints and indexes

Revision ID: 6033064ae1ed
Revises: fdbd31cee7f9
Create Date: 2026-08-25 17:22:09.167279

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '6033064ae1ed'
down_revision: Union[str, None] = 'fdbd31cee7f9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Exactly one current row per parent -- enforced in Postgres, not just
    # in application code, so a bug or a concurrent writer can never leave
    # two "current" rows for the same artifact/account/playbook name.
    op.execute(
        "CREATE UNIQUE INDEX uq_content_version_current "
        "ON content_versions (artifact_id) WHERE is_current"
    )
    op.execute(
        "CREATE UNIQUE INDEX uq_cycle_current "
        "ON cycles (account_id) WHERE is_current"
    )
    op.execute(
        "CREATE UNIQUE INDEX uq_playbook_current "
        "ON playbooks (workspace_id, name) WHERE is_current"
    )

    # Foreign-key columns are not auto-indexed by Postgres; every one of
    # these is on the hot path of a workspace-scoped read or a cascade
    # lookup (e.g. "what depends on this material").
    op.create_index("ix_subjects_workspace_id", "subjects", ["workspace_id"])
    op.create_index("ix_accounts_workspace_id", "accounts", ["workspace_id"])
    op.create_index("ix_cycles_workspace_id", "cycles", ["workspace_id"])
    op.create_index("ix_cycles_account_id", "cycles", ["account_id"])
    op.create_index("ix_campaign_overrides_workspace_id", "campaign_overrides", ["workspace_id"])
    op.create_index("ix_campaign_overrides_cycle_id", "campaign_overrides", ["cycle_id"])
    op.create_index("ix_tasks_workspace_id", "tasks", ["workspace_id"])
    op.create_index("ix_tasks_cycle_id", "tasks", ["cycle_id"])
    op.create_index("ix_task_snapshots_task_id", "task_snapshots", ["task_id"])
    op.create_index("ix_materials_workspace_id", "materials", ["workspace_id"])
    op.create_index("ix_artifacts_task_id", "artifacts", ["task_id"])
    op.create_index(
        "ix_artifact_material_dependencies_material_id",
        "artifact_material_dependencies",
        ["material_id"],
    )
    op.create_index("ix_content_versions_artifact_id", "content_versions", ["artifact_id"])
    op.create_index(
        "ix_publish_instances_content_version_id", "publish_instances", ["content_version_id"]
    )
    op.create_index("ix_publish_instances_account_id", "publish_instances", ["account_id"])
    op.create_index(
        "ix_feedback_records_publish_instance_id", "feedback_records", ["publish_instance_id"]
    )
    op.create_index("ix_market_observations_workspace_id", "market_observations", ["workspace_id"])
    op.create_index("ix_playbooks_workspace_id", "playbooks", ["workspace_id"])


def downgrade() -> None:
    op.drop_index("ix_playbooks_workspace_id", table_name="playbooks")
    op.drop_index("ix_market_observations_workspace_id", table_name="market_observations")
    op.drop_index("ix_feedback_records_publish_instance_id", table_name="feedback_records")
    op.drop_index("ix_publish_instances_account_id", table_name="publish_instances")
    op.drop_index("ix_publish_instances_content_version_id", table_name="publish_instances")
    op.drop_index("ix_content_versions_artifact_id", table_name="content_versions")
    op.drop_index(
        "ix_artifact_material_dependencies_material_id",
        table_name="artifact_material_dependencies",
    )
    op.drop_index("ix_artifacts_task_id", table_name="artifacts")
    op.drop_index("ix_materials_workspace_id", table_name="materials")
    op.drop_index("ix_task_snapshots_task_id", table_name="task_snapshots")
    op.drop_index("ix_tasks_cycle_id", table_name="tasks")
    op.drop_index("ix_tasks_workspace_id", table_name="tasks")
    op.drop_index("ix_campaign_overrides_cycle_id", table_name="campaign_overrides")
    op.drop_index("ix_campaign_overrides_workspace_id", table_name="campaign_overrides")
    op.drop_index("ix_cycles_account_id", table_name="cycles")
    op.drop_index("ix_cycles_workspace_id", table_name="cycles")
    op.drop_index("ix_accounts_workspace_id", table_name="accounts")
    op.drop_index("ix_subjects_workspace_id", table_name="subjects")
    op.execute("DROP INDEX uq_playbook_current")
    op.execute("DROP INDEX uq_cycle_current")
    op.execute("DROP INDEX uq_content_version_current")
