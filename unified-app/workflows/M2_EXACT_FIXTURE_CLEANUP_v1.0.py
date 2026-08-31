#!/usr/bin/env python3
"""Backup, dry-run, and transactionally remove ten exact M2 test workspaces."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
UAPP_ROOT = HERE.parent
OUTPUT = UAPP_ROOT / "evidence" / "stages" / "s5_final_convergence_v1_0" / "m2_cleanup"
EXPECTED_SCHEMA_MD5 = "25192c11562827efedfc3b2c22c3b4fd"
EXPECTED_PRE_PUBLISH = 1570
EXPECTED_POST_PUBLISH = 1568
EXPECTED_FEEDBACK = 117

TARGETS: tuple[tuple[str, str], ...] = (
    ("94810adf-8429-4a13-b732-4d960db42267", "ws-1b7de80f77144c0988168449ba2e6dd9"),
    ("55dea141-7d27-488c-a498-06a0979d5c22", "ws-304e9b70206f493e85a90fb6e725610a"),
    ("e99346f8-d2ab-44f1-b2f0-ae94ecd559c1", "ws-5d53c2af7a4f4afcab59337f3980afc1"),
    ("99af9ef2-9afa-4839-be88-22d37cbc4f59", "ws-f4ca2aef565d43269d5a9e19a3612ed7"),
    ("008be683-9af2-4528-afde-9e6ef47be6cb", "ws-1c0246ca0ae74f8ca6e5a3531c4aa780"),
    ("7901c68c-a580-4a51-8dbe-47717668af37", "ws-8d1c84525d594e7e9691b93e03450ebf"),
    ("e90f3460-be8e-4490-827a-31ca7cd16312", "ws-f5aed2c401864df8b965fae987755142"),
    ("1b22bb7d-1f9b-49ea-8fe8-4e2b2e0968c2", "ws-0ba81e9d485e49dcb05d3ed8eecf74bb"),
    ("9a95cbe7-aa95-463a-8112-f15f235e8cc3", "ws-9190d65ec52944eca4d06c3299963b20"),
    ("8479b71e-59e1-43f3-80d3-a18a6fb6e7bc", "ws-27a83567f08d41fea96eb04a416e75d9"),
)

TABLE_ORDER: tuple[str, ...] = (
    "workspaces",
    "users",
    "workspace_memberships",
    "subjects",
    "accounts",
    "cycles",
    "tasks",
    "materials",
    "playbooks",
    "campaign_overrides",
    "cycle_decisions",
    "market_observations",
    "legacy_import_records",
    "artifacts",
    "content_versions",
    "content_version_material_dependencies",
    "publish_instances",
    "feedback_records",
    "task_snapshots",
    "task_run_states",
    "idempotency_records",
)

TEMP_BY_TABLE: dict[str, str] = {
    "workspaces": "cleanup_workspaces",
    "users": "cleanup_users",
    "workspace_memberships": "cleanup_memberships",
    "subjects": "cleanup_subjects",
    "accounts": "cleanup_accounts",
    "cycles": "cleanup_cycles",
    "tasks": "cleanup_tasks",
    "materials": "cleanup_materials",
    "playbooks": "cleanup_playbooks",
    "campaign_overrides": "cleanup_campaign_overrides",
    "cycle_decisions": "cleanup_cycle_decisions",
    "market_observations": "cleanup_market_observations",
    "legacy_import_records": "cleanup_legacy_import_records",
    "artifacts": "cleanup_artifacts",
    "content_versions": "cleanup_versions",
    "content_version_material_dependencies": "cleanup_dependencies",
    "publish_instances": "cleanup_publish_instances",
    "feedback_records": "cleanup_feedback_records",
    "task_snapshots": "cleanup_task_snapshots",
    "task_run_states": "cleanup_task_run_states",
    "idempotency_records": "cleanup_idempotency_records",
}


def psql(sql: str) -> str:
    completed = subprocess.run(
        [
            "docker",
            "exec",
            "-i",
            "docker-db_postgres-1",
            "psql",
            "-U",
            "postgres",
            "-d",
            "diyu_business",
            "-tA",
            "-v",
            "ON_ERROR_STOP=1",
            "-c",
            sql,
        ],
        capture_output=True,
        check=False,
        text=True,
    )
    if completed.returncode != 0:
        raise RuntimeError((completed.stderr or completed.stdout)[:4000])
    return completed.stdout.strip()


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def target_values() -> str:
    return ",\n".join(
        f"('{workspace_id}'::uuid,'{name}')" for workspace_id, name in TARGETS
    )


def target_ctes() -> str:
    return f"""
target_ids(id, expected_name) AS (VALUES
{target_values()}
),
target_ws AS (
  SELECT w.* FROM workspaces w JOIN target_ids t ON t.id=w.id
),
target_memberships AS (
  SELECT wm.* FROM workspace_memberships wm JOIN target_ws t ON t.id=wm.workspace_id
),
target_users AS (
  SELECT DISTINCT u.* FROM users u JOIN target_memberships wm ON wm.user_id=u.id
),
target_subjects AS (SELECT s.* FROM subjects s JOIN target_ws t ON t.id=s.workspace_id),
target_accounts AS (SELECT a.* FROM accounts a JOIN target_ws t ON t.id=a.workspace_id),
target_cycles AS (SELECT c.* FROM cycles c JOIN target_ws t ON t.id=c.workspace_id),
target_tasks AS (SELECT x.* FROM tasks x JOIN target_ws t ON t.id=x.workspace_id),
target_materials AS (SELECT m.* FROM materials m JOIN target_ws t ON t.id=m.workspace_id),
target_playbooks AS (SELECT p.* FROM playbooks p JOIN target_ws t ON t.id=p.workspace_id),
target_campaign_overrides AS (
  SELECT x.* FROM campaign_overrides x JOIN target_ws t ON t.id=x.workspace_id
),
target_cycle_decisions AS (
  SELECT x.* FROM cycle_decisions x JOIN target_ws t ON t.id=x.workspace_id
),
target_market_observations AS (
  SELECT x.* FROM market_observations x JOIN target_ws t ON t.id=x.workspace_id
),
target_legacy_import_records AS (
  SELECT x.* FROM legacy_import_records x JOIN target_ws t ON t.id=x.workspace_id
),
target_artifacts AS (
  SELECT a.* FROM artifacts a JOIN target_tasks x ON x.id=a.task_id
),
target_versions AS (
  SELECT v.* FROM content_versions v JOIN target_artifacts a ON a.id=v.artifact_id
),
target_dependencies AS (
  SELECT d.* FROM content_version_material_dependencies d
  WHERE d.content_version_id IN (SELECT id FROM target_versions)
     OR d.material_id IN (SELECT id FROM target_materials)
),
target_publish_instances AS (
  SELECT p.* FROM publish_instances p JOIN target_ws t ON t.id=p.workspace_id
),
target_feedback_records AS (
  SELECT f.* FROM feedback_records f JOIN target_ws t ON t.id=f.workspace_id
),
target_task_snapshots AS (
  SELECT s.* FROM task_snapshots s JOIN target_tasks x ON x.id=s.task_id
),
target_task_run_states AS (
  SELECT s.* FROM task_run_states s JOIN target_tasks x ON x.id=s.task_id
),
target_object_refs AS (
  SELECT id::text ref FROM target_ws
  UNION SELECT id::text FROM target_accounts
  UNION SELECT id::text FROM target_cycles
  UNION SELECT id::text FROM target_tasks
  UNION SELECT id::text FROM target_materials
  UNION SELECT id::text FROM target_artifacts
  UNION SELECT id::text FROM target_versions
  UNION SELECT id::text FROM target_publish_instances
),
target_idempotency_records AS (
  SELECT i.* FROM idempotency_records i
  JOIN target_object_refs r ON r.ref=(i.result_ref #>> '{{}}')
)
""".strip()


def rows_expression(cte_name: str) -> str:
    return f"(SELECT coalesce(jsonb_agg(to_jsonb(x)), '[]'::jsonb) FROM {cte_name} x)"


def backup_query() -> str:
    table_to_cte = {
        "workspaces": "target_ws",
        "users": "target_users",
        "workspace_memberships": "target_memberships",
        "subjects": "target_subjects",
        "accounts": "target_accounts",
        "cycles": "target_cycles",
        "tasks": "target_tasks",
        "materials": "target_materials",
        "playbooks": "target_playbooks",
        "campaign_overrides": "target_campaign_overrides",
        "cycle_decisions": "target_cycle_decisions",
        "market_observations": "target_market_observations",
        "legacy_import_records": "target_legacy_import_records",
        "artifacts": "target_artifacts",
        "content_versions": "target_versions",
        "content_version_material_dependencies": "target_dependencies",
        "publish_instances": "target_publish_instances",
        "feedback_records": "target_feedback_records",
        "task_snapshots": "target_task_snapshots",
        "task_run_states": "target_task_run_states",
        "idempotency_records": "target_idempotency_records",
    }
    pairs = ",\n".join(
        f"'{table}', {rows_expression(table_to_cte[table])}" for table in TABLE_ORDER
    )
    return f"WITH {target_ctes()} SELECT jsonb_build_object({pairs})::text;"


def guard_query() -> str:
    return """
SELECT jsonb_build_object(
  'publish_guard', (SELECT count(*) FROM publish_instances WHERE NOT is_test OR NOT is_simulated),
  'feedback_guard', (SELECT count(*) FROM feedback_records WHERE NOT is_test OR NOT is_simulated),
  'schema_md5', (
    SELECT md5(string_agg(table_name||'.'||column_name||':'||data_type,','
                          ORDER BY table_name,ordinal_position))
    FROM information_schema.columns WHERE table_schema='public'
  )
)::text;
""".strip()


def violations_query() -> str:
    return f"""
WITH {target_ctes()}, violations AS (
  SELECT 'workspace_identity' kind, coalesce(w.id::text,t.id::text) detail FROM target_ids t
  LEFT JOIN workspaces w ON w.id=t.id WHERE w.id IS NULL OR w.name<>t.expected_name
  UNION ALL
  SELECT 'target_user_has_outside_membership', wm.user_id::text
  FROM target_memberships wm JOIN workspace_memberships other ON other.user_id=wm.user_id
  WHERE other.workspace_id NOT IN (SELECT id FROM target_ws)
  UNION ALL
  SELECT 'target_account_external_subject', a.id::text FROM target_accounts a
  WHERE a.subject_id IS NOT NULL AND a.subject_id NOT IN (SELECT id FROM target_subjects)
  UNION ALL
  SELECT 'target_cycle_external_ref', c.id::text FROM target_cycles c
  WHERE c.account_id NOT IN (SELECT id FROM target_accounts)
     OR (c.supersedes_cycle_id IS NOT NULL AND c.supersedes_cycle_id NOT IN (SELECT id FROM target_cycles))
  UNION ALL
  SELECT 'target_task_external_ref', x.id::text FROM target_tasks x
  WHERE x.account_id NOT IN (SELECT id FROM target_accounts)
     OR (x.cycle_id IS NOT NULL AND x.cycle_id NOT IN (SELECT id FROM target_cycles))
  UNION ALL
  SELECT 'target_artifact_external_parent', a.id::text FROM target_artifacts a
  WHERE a.parent_artifact_id IS NOT NULL
    AND a.parent_artifact_id NOT IN (SELECT id FROM target_artifacts)
  UNION ALL
  SELECT 'target_dependency_cross_scope', d.content_version_id::text||':'||d.material_id::text
  FROM target_dependencies d
  WHERE d.content_version_id NOT IN (SELECT id FROM target_versions)
     OR d.material_id NOT IN (SELECT id FROM target_materials)
  UNION ALL
  SELECT 'target_publish_external_ref', p.id::text FROM target_publish_instances p
  WHERE p.content_version_id NOT IN (SELECT id FROM target_versions)
     OR p.account_id NOT IN (SELECT id FROM target_accounts)
  UNION ALL
  SELECT 'target_feedback_external_ref', f.id::text FROM target_feedback_records f
  WHERE f.publish_instance_id NOT IN (SELECT id FROM target_publish_instances)
     OR f.content_version_id NOT IN (SELECT id FROM target_versions)
  UNION ALL
  SELECT 'outside_task_references_target', x.id::text FROM tasks x
  WHERE x.workspace_id NOT IN (SELECT id FROM target_ws)
    AND (x.account_id IN (SELECT id FROM target_accounts) OR x.cycle_id IN (SELECT id FROM target_cycles))
  UNION ALL
  SELECT 'outside_artifact_references_target', a.id::text FROM artifacts a
  WHERE a.id NOT IN (SELECT id FROM target_artifacts)
    AND (a.task_id IN (SELECT id FROM target_tasks) OR a.parent_artifact_id IN (SELECT id FROM target_artifacts))
  UNION ALL
  SELECT 'outside_version_references_target', v.id::text FROM content_versions v
  WHERE v.id NOT IN (SELECT id FROM target_versions) AND v.artifact_id IN (SELECT id FROM target_artifacts)
  UNION ALL
  SELECT 'outside_publish_references_target', p.id::text FROM publish_instances p
  WHERE p.workspace_id NOT IN (SELECT id FROM target_ws)
    AND (p.content_version_id IN (SELECT id FROM target_versions)
         OR p.account_id IN (SELECT id FROM target_accounts))
  UNION ALL
  SELECT 'outside_feedback_references_target', f.id::text FROM feedback_records f
  WHERE f.workspace_id NOT IN (SELECT id FROM target_ws)
    AND (f.publish_instance_id IN (SELECT id FROM target_publish_instances)
         OR f.content_version_id IN (SELECT id FROM target_versions))
)
SELECT coalesce(jsonb_agg(to_jsonb(v)), '[]'::jsonb)::text FROM violations v;
""".strip()


def count_rows(backup: dict[str, Any]) -> dict[str, int]:
    return {table: len(backup[table]) for table in TABLE_ORDER}


def restore_sql(backup: dict[str, Any]) -> str:
    statements = ["BEGIN;"]
    for table in TABLE_ORDER:
        rows = backup[table]
        if not rows:
            continue
        payload = json.dumps(rows, ensure_ascii=False, separators=(",", ":"))
        statements.append(
            f"INSERT INTO {table} SELECT * FROM jsonb_populate_recordset(NULL::{table}, "
            f"$backup${payload}$backup$::jsonb);"
        )
    statements.append("COMMIT;")
    return "\n".join(statements) + "\n"


def temp_tables_sql() -> str:
    return f"""
CREATE TEMP TABLE cleanup_workspaces ON COMMIT DROP AS
SELECT w.* FROM workspaces w JOIN (VALUES
{target_values()}
) t(id,expected_name) ON t.id=w.id AND t.expected_name=w.name;
CREATE TEMP TABLE cleanup_memberships ON COMMIT DROP AS
SELECT x.* FROM workspace_memberships x JOIN cleanup_workspaces w ON w.id=x.workspace_id;
CREATE TEMP TABLE cleanup_users ON COMMIT DROP AS
SELECT DISTINCT u.* FROM users u JOIN cleanup_memberships m ON m.user_id=u.id;
CREATE TEMP TABLE cleanup_subjects ON COMMIT DROP AS
SELECT x.* FROM subjects x JOIN cleanup_workspaces w ON w.id=x.workspace_id;
CREATE TEMP TABLE cleanup_accounts ON COMMIT DROP AS
SELECT x.* FROM accounts x JOIN cleanup_workspaces w ON w.id=x.workspace_id;
CREATE TEMP TABLE cleanup_cycles ON COMMIT DROP AS
SELECT x.* FROM cycles x JOIN cleanup_workspaces w ON w.id=x.workspace_id;
CREATE TEMP TABLE cleanup_tasks ON COMMIT DROP AS
SELECT x.* FROM tasks x JOIN cleanup_workspaces w ON w.id=x.workspace_id;
CREATE TEMP TABLE cleanup_materials ON COMMIT DROP AS
SELECT x.* FROM materials x JOIN cleanup_workspaces w ON w.id=x.workspace_id;
CREATE TEMP TABLE cleanup_playbooks ON COMMIT DROP AS
SELECT x.* FROM playbooks x JOIN cleanup_workspaces w ON w.id=x.workspace_id;
CREATE TEMP TABLE cleanup_campaign_overrides ON COMMIT DROP AS
SELECT x.* FROM campaign_overrides x JOIN cleanup_workspaces w ON w.id=x.workspace_id;
CREATE TEMP TABLE cleanup_cycle_decisions ON COMMIT DROP AS
SELECT x.* FROM cycle_decisions x JOIN cleanup_workspaces w ON w.id=x.workspace_id;
CREATE TEMP TABLE cleanup_market_observations ON COMMIT DROP AS
SELECT x.* FROM market_observations x JOIN cleanup_workspaces w ON w.id=x.workspace_id;
CREATE TEMP TABLE cleanup_legacy_import_records ON COMMIT DROP AS
SELECT x.* FROM legacy_import_records x JOIN cleanup_workspaces w ON w.id=x.workspace_id;
CREATE TEMP TABLE cleanup_artifacts ON COMMIT DROP AS
SELECT x.* FROM artifacts x JOIN cleanup_tasks t ON t.id=x.task_id;
CREATE TEMP TABLE cleanup_versions ON COMMIT DROP AS
SELECT x.* FROM content_versions x JOIN cleanup_artifacts a ON a.id=x.artifact_id;
CREATE TEMP TABLE cleanup_dependencies ON COMMIT DROP AS
SELECT x.* FROM content_version_material_dependencies x
WHERE x.content_version_id IN (SELECT id FROM cleanup_versions)
   OR x.material_id IN (SELECT id FROM cleanup_materials);
CREATE TEMP TABLE cleanup_publish_instances ON COMMIT DROP AS
SELECT x.* FROM publish_instances x JOIN cleanup_workspaces w ON w.id=x.workspace_id;
CREATE TEMP TABLE cleanup_feedback_records ON COMMIT DROP AS
SELECT x.* FROM feedback_records x JOIN cleanup_workspaces w ON w.id=x.workspace_id;
CREATE TEMP TABLE cleanup_task_snapshots ON COMMIT DROP AS
SELECT x.* FROM task_snapshots x JOIN cleanup_tasks t ON t.id=x.task_id;
CREATE TEMP TABLE cleanup_task_run_states ON COMMIT DROP AS
SELECT x.* FROM task_run_states x JOIN cleanup_tasks t ON t.id=x.task_id;
CREATE TEMP TABLE cleanup_idempotency_records ON COMMIT DROP AS
SELECT x.* FROM idempotency_records x WHERE (x.result_ref #>> '{{}}') IN (
  SELECT id::text FROM cleanup_workspaces UNION SELECT id::text FROM cleanup_accounts
  UNION SELECT id::text FROM cleanup_cycles UNION SELECT id::text FROM cleanup_tasks
  UNION SELECT id::text FROM cleanup_materials UNION SELECT id::text FROM cleanup_artifacts
  UNION SELECT id::text FROM cleanup_versions UNION SELECT id::text FROM cleanup_publish_instances
);
""".strip()


def fingerprint_select(table: str) -> str:
    temp = TEMP_BY_TABLE[table]
    if table == "content_version_material_dependencies":
        exclusion = (
            "NOT EXISTS (SELECT 1 FROM cleanup_dependencies c WHERE "
            "c.content_version_id=x.content_version_id AND c.material_id=x.material_id)"
        )
    elif table == "idempotency_records":
        exclusion = (
            "NOT EXISTS (SELECT 1 FROM cleanup_idempotency_records c WHERE c.key=x.key)"
        )
    else:
        exclusion = f"NOT EXISTS (SELECT 1 FROM {temp} c WHERE c.id=x.id)"
    return (
        f"SELECT '{table}', count(*), md5(coalesce(string_agg(md5(to_jsonb(x)::text),'' "
        f"ORDER BY md5(to_jsonb(x)::text)),'')) FROM {table} x WHERE {exclusion}"
    )


def expected_assertions(counts: dict[str, int]) -> str:
    clauses = [
        f"IF (SELECT count(*) FROM {TEMP_BY_TABLE[table]}) <> {counts[table]} THEN "
        f"RAISE EXCEPTION 'target count mismatch: {table}'; END IF;"
        for table in TABLE_ORDER
    ]
    return "\n  ".join(clauses)


def cleanup_sql(counts: dict[str, int]) -> str:
    fingerprints = "\nUNION ALL\n".join(
        fingerprint_select(table) for table in TABLE_ORDER
    )
    delete_order = (
        "feedback_records",
        "publish_instances",
        "content_version_material_dependencies",
        "task_snapshots",
        "task_run_states",
        "content_versions",
        "artifacts",
        "legacy_import_records",
        "market_observations",
        "campaign_overrides",
        "cycle_decisions",
        "tasks",
        "materials",
        "playbooks",
        "cycles",
        "accounts",
        "subjects",
        "workspace_memberships",
        "idempotency_records",
        "users",
        "workspaces",
    )
    deletes: list[str] = []
    for table in delete_order:
        temp = TEMP_BY_TABLE[table]
        if table == "content_version_material_dependencies":
            predicate = (
                "EXISTS (SELECT 1 FROM cleanup_dependencies c WHERE "
                "c.content_version_id=x.content_version_id AND c.material_id=x.material_id)"
            )
        elif table == "idempotency_records":
            predicate = (
                "EXISTS (SELECT 1 FROM cleanup_idempotency_records c WHERE c.key=x.key)"
            )
        else:
            predicate = f"EXISTS (SELECT 1 FROM {temp} c WHERE c.id=x.id)"
        deletes.append(
            f"WITH d AS (DELETE FROM {table} x WHERE {predicate} RETURNING 1) "
            f"INSERT INTO cleanup_deleted VALUES ('{table}', (SELECT count(*) FROM d));"
        )
    deleted_assertions = "\n  ".join(
        f"IF coalesce((SELECT n FROM cleanup_deleted WHERE table_name='{table}'),0) <> "
        f"{counts[table]} THEN RAISE EXCEPTION 'deleted count mismatch: {table}'; END IF;"
        for table in TABLE_ORDER
    )
    return f"""
BEGIN;
SET LOCAL lock_timeout='5s';
SET LOCAL statement_timeout='60s';
{temp_tables_sql()}
DO $$ BEGIN
  IF (SELECT count(*) FROM cleanup_workspaces) <> 10 THEN
    RAISE EXCEPTION 'exact workspace identity mismatch';
  END IF;
  IF (SELECT count(*) FROM publish_instances WHERE NOT is_test OR NOT is_simulated)
       <> {EXPECTED_PRE_PUBLISH} THEN RAISE EXCEPTION 'pre publish guard mismatch'; END IF;
  IF (SELECT count(*) FROM feedback_records WHERE NOT is_test OR NOT is_simulated)
       <> {EXPECTED_FEEDBACK} THEN RAISE EXCEPTION 'pre feedback guard mismatch'; END IF;
  IF (SELECT md5(string_agg(table_name||'.'||column_name||':'||data_type,','
       ORDER BY table_name,ordinal_position)) FROM information_schema.columns
       WHERE table_schema='public') <> '{EXPECTED_SCHEMA_MD5}' THEN
    RAISE EXCEPTION 'pre schema guard mismatch';
  END IF;
  IF EXISTS (
    SELECT 1 FROM cleanup_memberships m JOIN workspace_memberships other ON other.user_id=m.user_id
    WHERE other.workspace_id NOT IN (SELECT id FROM cleanup_workspaces)
  ) THEN RAISE EXCEPTION 'target user has outside membership'; END IF;
  IF EXISTS (
    SELECT 1 FROM cleanup_dependencies d
    WHERE d.content_version_id NOT IN (SELECT id FROM cleanup_versions)
       OR d.material_id NOT IN (SELECT id FROM cleanup_materials)
  ) THEN RAISE EXCEPTION 'cross-scope material dependency'; END IF;
  IF EXISTS (
    SELECT 1 FROM publish_instances p WHERE p.workspace_id NOT IN (SELECT id FROM cleanup_workspaces)
      AND (p.content_version_id IN (SELECT id FROM cleanup_versions)
           OR p.account_id IN (SELECT id FROM cleanup_accounts))
  ) THEN RAISE EXCEPTION 'outside publish references target'; END IF;
  IF EXISTS (
    SELECT 1 FROM feedback_records f WHERE f.workspace_id NOT IN (SELECT id FROM cleanup_workspaces)
      AND (f.publish_instance_id IN (SELECT id FROM cleanup_publish_instances)
           OR f.content_version_id IN (SELECT id FROM cleanup_versions))
  ) THEN RAISE EXCEPTION 'outside feedback references target'; END IF;
  {expected_assertions(counts)}
END $$;
CREATE TEMP TABLE cleanup_non_target_guard(
  table_name text PRIMARY KEY, row_count bigint NOT NULL, row_md5 text NOT NULL
) ON COMMIT DROP;
INSERT INTO cleanup_non_target_guard
{fingerprints};
CREATE TEMP TABLE cleanup_deleted(table_name text PRIMARY KEY, n bigint NOT NULL) ON COMMIT DROP;
{" ".join(deletes)}
DO $$ BEGIN
  {deleted_assertions}
  IF (SELECT count(*) FROM publish_instances WHERE NOT is_test OR NOT is_simulated)
       <> {EXPECTED_POST_PUBLISH} THEN RAISE EXCEPTION 'post publish guard mismatch'; END IF;
  IF (SELECT count(*) FROM feedback_records WHERE NOT is_test OR NOT is_simulated)
       <> {EXPECTED_FEEDBACK} THEN RAISE EXCEPTION 'post feedback guard mismatch'; END IF;
  IF (SELECT md5(string_agg(table_name||'.'||column_name||':'||data_type,','
       ORDER BY table_name,ordinal_position)) FROM information_schema.columns
       WHERE table_schema='public') <> '{EXPECTED_SCHEMA_MD5}' THEN
    RAISE EXCEPTION 'post schema guard mismatch';
  END IF;
  IF EXISTS (
    SELECT table_name,row_count,row_md5 FROM cleanup_non_target_guard
    EXCEPT
    SELECT * FROM ({fingerprints}) post_fingerprint
  ) OR EXISTS (
    SELECT * FROM ({fingerprints}) post_fingerprint
    EXCEPT
    SELECT table_name,row_count,row_md5 FROM cleanup_non_target_guard
  ) THEN RAISE EXCEPTION 'non-target data drift'; END IF;
END $$;
SELECT jsonb_build_object(
  'deleted', (SELECT jsonb_object_agg(table_name,n) FROM cleanup_deleted),
  'publish_guard', (SELECT count(*) FROM publish_instances WHERE NOT is_test OR NOT is_simulated),
  'feedback_guard', (SELECT count(*) FROM feedback_records WHERE NOT is_test OR NOT is_simulated),
  'schema_md5', (SELECT md5(string_agg(table_name||'.'||column_name||':'||data_type,','
      ORDER BY table_name,ordinal_position)) FROM information_schema.columns WHERE table_schema='public'),
  'non_target_data_drift', false
)::text;
COMMIT;
""".strip()


def prepare() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    paths = {
        "backup": OUTPUT / "M2_EXACT_FIXTURE_BACKUP_v1.0.json",
        "restore": OUTPUT / "M2_EXACT_FIXTURE_RESTORE_v1.0.sql",
        "dry_run": OUTPUT / "M2_EXACT_FIXTURE_DRY_RUN_v1.0.json",
        "cleanup_sql": OUTPUT / "M2_EXACT_FIXTURE_CLEANUP_v1.0.sql",
    }
    if any(path.exists() for path in paths.values()):
        raise FileExistsError("Cleanup evidence already exists")
    guard = json.loads(psql(guard_query()))
    backup_rows = json.loads(psql(backup_query()))
    counts = count_rows(backup_rows)
    violations = json.loads(psql(violations_query()))
    backup = {
        "document": "M2_EXACT_FIXTURE_BACKUP_v1.0",
        "task_id": "DIYU-V1-UNIFIED-DIFY-APPLICATION-001",
        "exact_workspace_ids": [workspace_id for workspace_id, _ in TARGETS],
        "pre_guard": guard,
        "counts": counts,
        "rows": backup_rows,
    }
    backup_text = json.dumps(backup, ensure_ascii=False, indent=2) + "\n"
    restore = restore_sql(backup_rows)
    dry_run = {
        "document": "M2_EXACT_FIXTURE_DRY_RUN_v1.0",
        "selection_method": "ten literal workspace UUIDs only",
        "target_count": counts["workspaces"],
        "counts": counts,
        "violations": violations,
        "guard": guard,
        "backup_sha256": sha256_text(backup_text),
        "restore_sql_sha256": sha256_text(restore),
        "pass": counts["workspaces"] == 10
        and not violations
        and guard
        == {
            "publish_guard": EXPECTED_PRE_PUBLISH,
            "feedback_guard": EXPECTED_FEEDBACK,
            "schema_md5": EXPECTED_SCHEMA_MD5,
        },
    }
    if not dry_run["pass"]:
        raise RuntimeError(dry_run)
    cleanup = cleanup_sql(counts) + "\n"
    paths["backup"].write_text(backup_text, encoding="utf-8")
    paths["restore"].write_text(restore, encoding="utf-8")
    paths["dry_run"].write_text(
        json.dumps(dry_run, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    paths["cleanup_sql"].write_text(cleanup, encoding="utf-8")
    print(json.dumps(dry_run, ensure_ascii=False, sort_keys=True))


def execute() -> None:
    dry_path = OUTPUT / "M2_EXACT_FIXTURE_DRY_RUN_v1.0.json"
    sql_path = OUTPUT / "M2_EXACT_FIXTURE_CLEANUP_v1.1.sql"
    post_path = OUTPUT / "M2_EXACT_FIXTURE_CLEANUP_RESULT_v1.1.json"
    if post_path.exists():
        raise FileExistsError(post_path)
    dry_run = json.loads(dry_path.read_text(encoding="utf-8"))
    if dry_run.get("pass") is not True:
        raise RuntimeError("Dry-run is not PASS")
    output_lines = psql(sql_path.read_text(encoding="utf-8")).splitlines()
    result_lines = [line for line in output_lines if line.startswith("{")]
    if len(result_lines) != 1:
        raise RuntimeError(f"Expected one transaction result row: {output_lines[-5:]}")
    result = json.loads(result_lines[0])
    post_guard = json.loads(psql(guard_query()))
    remaining = int(
        psql(
            "select count(*) from workspaces where id in ("
            + ",".join(f"'{workspace_id}'::uuid" for workspace_id, _ in TARGETS)
            + ");"
        )
    )
    report = {
        "document": "M2_EXACT_FIXTURE_CLEANUP_RESULT_v1.1",
        "transaction_result": result,
        "post_guard": post_guard,
        "remaining_target_workspaces": remaining,
        "pass": result["publish_guard"] == EXPECTED_POST_PUBLISH
        and result["feedback_guard"] == EXPECTED_FEEDBACK
        and result["schema_md5"] == EXPECTED_SCHEMA_MD5
        and result["non_target_data_drift"] is False
        and post_guard
        == {
            "publish_guard": EXPECTED_POST_PUBLISH,
            "feedback_guard": EXPECTED_FEEDBACK,
            "schema_md5": EXPECTED_SCHEMA_MD5,
        }
        and remaining == 0,
    }
    if not report["pass"]:
        raise RuntimeError(report)
    post_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))


def record_committed_cleanup() -> None:
    backup_path = OUTPUT / "M2_EXACT_FIXTURE_BACKUP_v1.0.json"
    sql_path = OUTPUT / "M2_EXACT_FIXTURE_CLEANUP_v1.1.sql"
    post_path = OUTPUT / "M2_EXACT_FIXTURE_CLEANUP_RESULT_v1.1.json"
    if post_path.exists():
        raise FileExistsError(post_path)
    backup = json.loads(backup_path.read_text(encoding="utf-8"))
    post_guard = json.loads(psql(guard_query()))
    remaining = int(
        psql(
            "select count(*) from workspaces where id in ("
            + ",".join(f"'{workspace_id}'::uuid" for workspace_id, _ in TARGETS)
            + ");"
        )
    )
    report = {
        "document": "M2_EXACT_FIXTURE_CLEANUP_RESULT_v1.1",
        "transaction_status": "COMMITTED",
        "recorder_note": (
            "The transaction returned success and COMMIT, but the initial recorder selected "
            "the trailing COMMIT line instead of the JSON result row. No cleanup was replayed."
        ),
        "transaction_sql_sha256": sha256_text(sql_path.read_text(encoding="utf-8")),
        "deleted": backup["counts"],
        "post_guard": post_guard,
        "remaining_target_workspaces": remaining,
        "transaction_assertions": {
            "exact_target_counts": "PASS",
            "foreign_key_scope": "PASS",
            "publish_guard": "PASS",
            "feedback_guard": "PASS",
            "schema_drift": "none",
            "non_target_data_drift": "none",
        },
        "pass": post_guard
        == {
            "publish_guard": EXPECTED_POST_PUBLISH,
            "feedback_guard": EXPECTED_FEEDBACK,
            "schema_md5": EXPECTED_SCHEMA_MD5,
        }
        and remaining == 0,
    }
    if not report["pass"]:
        raise RuntimeError(report)
    post_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))


def repair_cleanup_sql() -> None:
    backup_path = OUTPUT / "M2_EXACT_FIXTURE_BACKUP_v1.0.json"
    old_sql_path = OUTPUT / "M2_EXACT_FIXTURE_CLEANUP_v1.0.sql"
    new_sql_path = OUTPUT / "M2_EXACT_FIXTURE_CLEANUP_v1.1.sql"
    triage_path = OUTPUT / "M2_EXACT_FIXTURE_CLEANUP_SQL_TRIAGE_v1.0.json"
    if new_sql_path.exists() or triage_path.exists():
        raise FileExistsError("Cleanup SQL successor already exists")
    backup = json.loads(backup_path.read_text(encoding="utf-8"))
    new_sql = cleanup_sql(backup["counts"]) + "\n"
    old_sql = old_sql_path.read_text(encoding="utf-8")
    triage = {
        "document": "M2_EXACT_FIXTURE_CLEANUP_SQL_TRIAGE_v1.0",
        "observed_failure": "transaction rolled back at non-target data drift postcondition",
        "confirmed_origin": "CHECKER_OR_FIXTURE",
        "evidence": {
            "target_workspaces_after_rollback": 10,
            "publish_guard_after_rollback": 1570,
            "feedback_guard_after_rollback": 117,
            "old_sql_sha256": sha256_text(old_sql),
        },
        "root_cause": (
            "EXCEPT consumed an unparenthesized UNION ALL chain left-associatively, "
            "making unchanged later table fingerprints appear as drift"
        ),
        "mutation_target": "post-delete fingerprint comparison only",
        "new_sql_sha256": sha256_text(new_sql),
        "protected_targets_unchanged": True,
    }
    new_sql_path.write_text(new_sql, encoding="utf-8")
    triage_path.write_text(
        json.dumps(triage, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(triage, ensure_ascii=False, sort_keys=True))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("prepare", "repair", "execute", "record"))
    args = parser.parse_args()
    if args.mode == "prepare":
        prepare()
    elif args.mode == "repair":
        repair_cleanup_sql()
    elif args.mode == "record":
        record_committed_cleanup()
    else:
        execute()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
