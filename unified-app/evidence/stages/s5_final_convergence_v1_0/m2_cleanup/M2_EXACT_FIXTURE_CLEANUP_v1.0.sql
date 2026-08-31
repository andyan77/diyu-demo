BEGIN;
SET LOCAL lock_timeout='5s';
SET LOCAL statement_timeout='60s';
CREATE TEMP TABLE cleanup_workspaces ON COMMIT DROP AS
SELECT w.* FROM workspaces w JOIN (VALUES
('94810adf-8429-4a13-b732-4d960db42267'::uuid,'ws-1b7de80f77144c0988168449ba2e6dd9'),
('55dea141-7d27-488c-a498-06a0979d5c22'::uuid,'ws-304e9b70206f493e85a90fb6e725610a'),
('e99346f8-d2ab-44f1-b2f0-ae94ecd559c1'::uuid,'ws-5d53c2af7a4f4afcab59337f3980afc1'),
('99af9ef2-9afa-4839-be88-22d37cbc4f59'::uuid,'ws-f4ca2aef565d43269d5a9e19a3612ed7'),
('008be683-9af2-4528-afde-9e6ef47be6cb'::uuid,'ws-1c0246ca0ae74f8ca6e5a3531c4aa780'),
('7901c68c-a580-4a51-8dbe-47717668af37'::uuid,'ws-8d1c84525d594e7e9691b93e03450ebf'),
('e90f3460-be8e-4490-827a-31ca7cd16312'::uuid,'ws-f5aed2c401864df8b965fae987755142'),
('1b22bb7d-1f9b-49ea-8fe8-4e2b2e0968c2'::uuid,'ws-0ba81e9d485e49dcb05d3ed8eecf74bb'),
('9a95cbe7-aa95-463a-8112-f15f235e8cc3'::uuid,'ws-9190d65ec52944eca4d06c3299963b20'),
('8479b71e-59e1-43f3-80d3-a18a6fb6e7bc'::uuid,'ws-27a83567f08d41fea96eb04a416e75d9')
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
SELECT x.* FROM idempotency_records x WHERE (x.result_ref #>> '{}') IN (
  SELECT id::text FROM cleanup_workspaces UNION SELECT id::text FROM cleanup_accounts
  UNION SELECT id::text FROM cleanup_cycles UNION SELECT id::text FROM cleanup_tasks
  UNION SELECT id::text FROM cleanup_materials UNION SELECT id::text FROM cleanup_artifacts
  UNION SELECT id::text FROM cleanup_versions UNION SELECT id::text FROM cleanup_publish_instances
);
DO $$ BEGIN
  IF (SELECT count(*) FROM cleanup_workspaces) <> 10 THEN
    RAISE EXCEPTION 'exact workspace identity mismatch';
  END IF;
  IF (SELECT count(*) FROM publish_instances WHERE NOT is_test OR NOT is_simulated)
       <> 1570 THEN RAISE EXCEPTION 'pre publish guard mismatch'; END IF;
  IF (SELECT count(*) FROM feedback_records WHERE NOT is_test OR NOT is_simulated)
       <> 117 THEN RAISE EXCEPTION 'pre feedback guard mismatch'; END IF;
  IF (SELECT md5(string_agg(table_name||'.'||column_name||':'||data_type,','
       ORDER BY table_name,ordinal_position)) FROM information_schema.columns
       WHERE table_schema='public') <> '25192c11562827efedfc3b2c22c3b4fd' THEN
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
  IF (SELECT count(*) FROM cleanup_workspaces) <> 10 THEN RAISE EXCEPTION 'target count mismatch: workspaces'; END IF;
  IF (SELECT count(*) FROM cleanup_users) <> 10 THEN RAISE EXCEPTION 'target count mismatch: users'; END IF;
  IF (SELECT count(*) FROM cleanup_memberships) <> 10 THEN RAISE EXCEPTION 'target count mismatch: workspace_memberships'; END IF;
  IF (SELECT count(*) FROM cleanup_subjects) <> 0 THEN RAISE EXCEPTION 'target count mismatch: subjects'; END IF;
  IF (SELECT count(*) FROM cleanup_accounts) <> 10 THEN RAISE EXCEPTION 'target count mismatch: accounts'; END IF;
  IF (SELECT count(*) FROM cleanup_cycles) <> 0 THEN RAISE EXCEPTION 'target count mismatch: cycles'; END IF;
  IF (SELECT count(*) FROM cleanup_tasks) <> 10 THEN RAISE EXCEPTION 'target count mismatch: tasks'; END IF;
  IF (SELECT count(*) FROM cleanup_materials) <> 10 THEN RAISE EXCEPTION 'target count mismatch: materials'; END IF;
  IF (SELECT count(*) FROM cleanup_playbooks) <> 0 THEN RAISE EXCEPTION 'target count mismatch: playbooks'; END IF;
  IF (SELECT count(*) FROM cleanup_campaign_overrides) <> 0 THEN RAISE EXCEPTION 'target count mismatch: campaign_overrides'; END IF;
  IF (SELECT count(*) FROM cleanup_cycle_decisions) <> 0 THEN RAISE EXCEPTION 'target count mismatch: cycle_decisions'; END IF;
  IF (SELECT count(*) FROM cleanup_market_observations) <> 0 THEN RAISE EXCEPTION 'target count mismatch: market_observations'; END IF;
  IF (SELECT count(*) FROM cleanup_legacy_import_records) <> 0 THEN RAISE EXCEPTION 'target count mismatch: legacy_import_records'; END IF;
  IF (SELECT count(*) FROM cleanup_artifacts) <> 10 THEN RAISE EXCEPTION 'target count mismatch: artifacts'; END IF;
  IF (SELECT count(*) FROM cleanup_versions) <> 6 THEN RAISE EXCEPTION 'target count mismatch: content_versions'; END IF;
  IF (SELECT count(*) FROM cleanup_dependencies) <> 4 THEN RAISE EXCEPTION 'target count mismatch: content_version_material_dependencies'; END IF;
  IF (SELECT count(*) FROM cleanup_publish_instances) <> 2 THEN RAISE EXCEPTION 'target count mismatch: publish_instances'; END IF;
  IF (SELECT count(*) FROM cleanup_feedback_records) <> 0 THEN RAISE EXCEPTION 'target count mismatch: feedback_records'; END IF;
  IF (SELECT count(*) FROM cleanup_task_snapshots) <> 0 THEN RAISE EXCEPTION 'target count mismatch: task_snapshots'; END IF;
  IF (SELECT count(*) FROM cleanup_task_run_states) <> 0 THEN RAISE EXCEPTION 'target count mismatch: task_run_states'; END IF;
  IF (SELECT count(*) FROM cleanup_idempotency_records) <> 0 THEN RAISE EXCEPTION 'target count mismatch: idempotency_records'; END IF;
END $$;
CREATE TEMP TABLE cleanup_non_target_guard(
  table_name text PRIMARY KEY, row_count bigint NOT NULL, row_md5 text NOT NULL
) ON COMMIT DROP;
INSERT INTO cleanup_non_target_guard
SELECT 'workspaces', count(*), md5(coalesce(string_agg(md5(to_jsonb(x)::text),'' ORDER BY md5(to_jsonb(x)::text)),'')) FROM workspaces x WHERE NOT EXISTS (SELECT 1 FROM cleanup_workspaces c WHERE c.id=x.id)
UNION ALL
SELECT 'users', count(*), md5(coalesce(string_agg(md5(to_jsonb(x)::text),'' ORDER BY md5(to_jsonb(x)::text)),'')) FROM users x WHERE NOT EXISTS (SELECT 1 FROM cleanup_users c WHERE c.id=x.id)
UNION ALL
SELECT 'workspace_memberships', count(*), md5(coalesce(string_agg(md5(to_jsonb(x)::text),'' ORDER BY md5(to_jsonb(x)::text)),'')) FROM workspace_memberships x WHERE NOT EXISTS (SELECT 1 FROM cleanup_memberships c WHERE c.id=x.id)
UNION ALL
SELECT 'subjects', count(*), md5(coalesce(string_agg(md5(to_jsonb(x)::text),'' ORDER BY md5(to_jsonb(x)::text)),'')) FROM subjects x WHERE NOT EXISTS (SELECT 1 FROM cleanup_subjects c WHERE c.id=x.id)
UNION ALL
SELECT 'accounts', count(*), md5(coalesce(string_agg(md5(to_jsonb(x)::text),'' ORDER BY md5(to_jsonb(x)::text)),'')) FROM accounts x WHERE NOT EXISTS (SELECT 1 FROM cleanup_accounts c WHERE c.id=x.id)
UNION ALL
SELECT 'cycles', count(*), md5(coalesce(string_agg(md5(to_jsonb(x)::text),'' ORDER BY md5(to_jsonb(x)::text)),'')) FROM cycles x WHERE NOT EXISTS (SELECT 1 FROM cleanup_cycles c WHERE c.id=x.id)
UNION ALL
SELECT 'tasks', count(*), md5(coalesce(string_agg(md5(to_jsonb(x)::text),'' ORDER BY md5(to_jsonb(x)::text)),'')) FROM tasks x WHERE NOT EXISTS (SELECT 1 FROM cleanup_tasks c WHERE c.id=x.id)
UNION ALL
SELECT 'materials', count(*), md5(coalesce(string_agg(md5(to_jsonb(x)::text),'' ORDER BY md5(to_jsonb(x)::text)),'')) FROM materials x WHERE NOT EXISTS (SELECT 1 FROM cleanup_materials c WHERE c.id=x.id)
UNION ALL
SELECT 'playbooks', count(*), md5(coalesce(string_agg(md5(to_jsonb(x)::text),'' ORDER BY md5(to_jsonb(x)::text)),'')) FROM playbooks x WHERE NOT EXISTS (SELECT 1 FROM cleanup_playbooks c WHERE c.id=x.id)
UNION ALL
SELECT 'campaign_overrides', count(*), md5(coalesce(string_agg(md5(to_jsonb(x)::text),'' ORDER BY md5(to_jsonb(x)::text)),'')) FROM campaign_overrides x WHERE NOT EXISTS (SELECT 1 FROM cleanup_campaign_overrides c WHERE c.id=x.id)
UNION ALL
SELECT 'cycle_decisions', count(*), md5(coalesce(string_agg(md5(to_jsonb(x)::text),'' ORDER BY md5(to_jsonb(x)::text)),'')) FROM cycle_decisions x WHERE NOT EXISTS (SELECT 1 FROM cleanup_cycle_decisions c WHERE c.id=x.id)
UNION ALL
SELECT 'market_observations', count(*), md5(coalesce(string_agg(md5(to_jsonb(x)::text),'' ORDER BY md5(to_jsonb(x)::text)),'')) FROM market_observations x WHERE NOT EXISTS (SELECT 1 FROM cleanup_market_observations c WHERE c.id=x.id)
UNION ALL
SELECT 'legacy_import_records', count(*), md5(coalesce(string_agg(md5(to_jsonb(x)::text),'' ORDER BY md5(to_jsonb(x)::text)),'')) FROM legacy_import_records x WHERE NOT EXISTS (SELECT 1 FROM cleanup_legacy_import_records c WHERE c.id=x.id)
UNION ALL
SELECT 'artifacts', count(*), md5(coalesce(string_agg(md5(to_jsonb(x)::text),'' ORDER BY md5(to_jsonb(x)::text)),'')) FROM artifacts x WHERE NOT EXISTS (SELECT 1 FROM cleanup_artifacts c WHERE c.id=x.id)
UNION ALL
SELECT 'content_versions', count(*), md5(coalesce(string_agg(md5(to_jsonb(x)::text),'' ORDER BY md5(to_jsonb(x)::text)),'')) FROM content_versions x WHERE NOT EXISTS (SELECT 1 FROM cleanup_versions c WHERE c.id=x.id)
UNION ALL
SELECT 'content_version_material_dependencies', count(*), md5(coalesce(string_agg(md5(to_jsonb(x)::text),'' ORDER BY md5(to_jsonb(x)::text)),'')) FROM content_version_material_dependencies x WHERE NOT EXISTS (SELECT 1 FROM cleanup_dependencies c WHERE c.content_version_id=x.content_version_id AND c.material_id=x.material_id)
UNION ALL
SELECT 'publish_instances', count(*), md5(coalesce(string_agg(md5(to_jsonb(x)::text),'' ORDER BY md5(to_jsonb(x)::text)),'')) FROM publish_instances x WHERE NOT EXISTS (SELECT 1 FROM cleanup_publish_instances c WHERE c.id=x.id)
UNION ALL
SELECT 'feedback_records', count(*), md5(coalesce(string_agg(md5(to_jsonb(x)::text),'' ORDER BY md5(to_jsonb(x)::text)),'')) FROM feedback_records x WHERE NOT EXISTS (SELECT 1 FROM cleanup_feedback_records c WHERE c.id=x.id)
UNION ALL
SELECT 'task_snapshots', count(*), md5(coalesce(string_agg(md5(to_jsonb(x)::text),'' ORDER BY md5(to_jsonb(x)::text)),'')) FROM task_snapshots x WHERE NOT EXISTS (SELECT 1 FROM cleanup_task_snapshots c WHERE c.id=x.id)
UNION ALL
SELECT 'task_run_states', count(*), md5(coalesce(string_agg(md5(to_jsonb(x)::text),'' ORDER BY md5(to_jsonb(x)::text)),'')) FROM task_run_states x WHERE NOT EXISTS (SELECT 1 FROM cleanup_task_run_states c WHERE c.id=x.id)
UNION ALL
SELECT 'idempotency_records', count(*), md5(coalesce(string_agg(md5(to_jsonb(x)::text),'' ORDER BY md5(to_jsonb(x)::text)),'')) FROM idempotency_records x WHERE NOT EXISTS (SELECT 1 FROM cleanup_idempotency_records c WHERE c.key=x.key);
CREATE TEMP TABLE cleanup_deleted(table_name text PRIMARY KEY, n bigint NOT NULL) ON COMMIT DROP;
WITH d AS (DELETE FROM feedback_records x WHERE EXISTS (SELECT 1 FROM cleanup_feedback_records c WHERE c.id=x.id) RETURNING 1) INSERT INTO cleanup_deleted VALUES ('feedback_records', (SELECT count(*) FROM d)); WITH d AS (DELETE FROM publish_instances x WHERE EXISTS (SELECT 1 FROM cleanup_publish_instances c WHERE c.id=x.id) RETURNING 1) INSERT INTO cleanup_deleted VALUES ('publish_instances', (SELECT count(*) FROM d)); WITH d AS (DELETE FROM content_version_material_dependencies x WHERE EXISTS (SELECT 1 FROM cleanup_dependencies c WHERE c.content_version_id=x.content_version_id AND c.material_id=x.material_id) RETURNING 1) INSERT INTO cleanup_deleted VALUES ('content_version_material_dependencies', (SELECT count(*) FROM d)); WITH d AS (DELETE FROM task_snapshots x WHERE EXISTS (SELECT 1 FROM cleanup_task_snapshots c WHERE c.id=x.id) RETURNING 1) INSERT INTO cleanup_deleted VALUES ('task_snapshots', (SELECT count(*) FROM d)); WITH d AS (DELETE FROM task_run_states x WHERE EXISTS (SELECT 1 FROM cleanup_task_run_states c WHERE c.id=x.id) RETURNING 1) INSERT INTO cleanup_deleted VALUES ('task_run_states', (SELECT count(*) FROM d)); WITH d AS (DELETE FROM content_versions x WHERE EXISTS (SELECT 1 FROM cleanup_versions c WHERE c.id=x.id) RETURNING 1) INSERT INTO cleanup_deleted VALUES ('content_versions', (SELECT count(*) FROM d)); WITH d AS (DELETE FROM artifacts x WHERE EXISTS (SELECT 1 FROM cleanup_artifacts c WHERE c.id=x.id) RETURNING 1) INSERT INTO cleanup_deleted VALUES ('artifacts', (SELECT count(*) FROM d)); WITH d AS (DELETE FROM legacy_import_records x WHERE EXISTS (SELECT 1 FROM cleanup_legacy_import_records c WHERE c.id=x.id) RETURNING 1) INSERT INTO cleanup_deleted VALUES ('legacy_import_records', (SELECT count(*) FROM d)); WITH d AS (DELETE FROM market_observations x WHERE EXISTS (SELECT 1 FROM cleanup_market_observations c WHERE c.id=x.id) RETURNING 1) INSERT INTO cleanup_deleted VALUES ('market_observations', (SELECT count(*) FROM d)); WITH d AS (DELETE FROM campaign_overrides x WHERE EXISTS (SELECT 1 FROM cleanup_campaign_overrides c WHERE c.id=x.id) RETURNING 1) INSERT INTO cleanup_deleted VALUES ('campaign_overrides', (SELECT count(*) FROM d)); WITH d AS (DELETE FROM cycle_decisions x WHERE EXISTS (SELECT 1 FROM cleanup_cycle_decisions c WHERE c.id=x.id) RETURNING 1) INSERT INTO cleanup_deleted VALUES ('cycle_decisions', (SELECT count(*) FROM d)); WITH d AS (DELETE FROM tasks x WHERE EXISTS (SELECT 1 FROM cleanup_tasks c WHERE c.id=x.id) RETURNING 1) INSERT INTO cleanup_deleted VALUES ('tasks', (SELECT count(*) FROM d)); WITH d AS (DELETE FROM materials x WHERE EXISTS (SELECT 1 FROM cleanup_materials c WHERE c.id=x.id) RETURNING 1) INSERT INTO cleanup_deleted VALUES ('materials', (SELECT count(*) FROM d)); WITH d AS (DELETE FROM playbooks x WHERE EXISTS (SELECT 1 FROM cleanup_playbooks c WHERE c.id=x.id) RETURNING 1) INSERT INTO cleanup_deleted VALUES ('playbooks', (SELECT count(*) FROM d)); WITH d AS (DELETE FROM cycles x WHERE EXISTS (SELECT 1 FROM cleanup_cycles c WHERE c.id=x.id) RETURNING 1) INSERT INTO cleanup_deleted VALUES ('cycles', (SELECT count(*) FROM d)); WITH d AS (DELETE FROM accounts x WHERE EXISTS (SELECT 1 FROM cleanup_accounts c WHERE c.id=x.id) RETURNING 1) INSERT INTO cleanup_deleted VALUES ('accounts', (SELECT count(*) FROM d)); WITH d AS (DELETE FROM subjects x WHERE EXISTS (SELECT 1 FROM cleanup_subjects c WHERE c.id=x.id) RETURNING 1) INSERT INTO cleanup_deleted VALUES ('subjects', (SELECT count(*) FROM d)); WITH d AS (DELETE FROM workspace_memberships x WHERE EXISTS (SELECT 1 FROM cleanup_memberships c WHERE c.id=x.id) RETURNING 1) INSERT INTO cleanup_deleted VALUES ('workspace_memberships', (SELECT count(*) FROM d)); WITH d AS (DELETE FROM idempotency_records x WHERE EXISTS (SELECT 1 FROM cleanup_idempotency_records c WHERE c.key=x.key) RETURNING 1) INSERT INTO cleanup_deleted VALUES ('idempotency_records', (SELECT count(*) FROM d)); WITH d AS (DELETE FROM users x WHERE EXISTS (SELECT 1 FROM cleanup_users c WHERE c.id=x.id) RETURNING 1) INSERT INTO cleanup_deleted VALUES ('users', (SELECT count(*) FROM d)); WITH d AS (DELETE FROM workspaces x WHERE EXISTS (SELECT 1 FROM cleanup_workspaces c WHERE c.id=x.id) RETURNING 1) INSERT INTO cleanup_deleted VALUES ('workspaces', (SELECT count(*) FROM d));
DO $$ BEGIN
  IF coalesce((SELECT n FROM cleanup_deleted WHERE table_name='workspaces'),0) <> 10 THEN RAISE EXCEPTION 'deleted count mismatch: workspaces'; END IF;
  IF coalesce((SELECT n FROM cleanup_deleted WHERE table_name='users'),0) <> 10 THEN RAISE EXCEPTION 'deleted count mismatch: users'; END IF;
  IF coalesce((SELECT n FROM cleanup_deleted WHERE table_name='workspace_memberships'),0) <> 10 THEN RAISE EXCEPTION 'deleted count mismatch: workspace_memberships'; END IF;
  IF coalesce((SELECT n FROM cleanup_deleted WHERE table_name='subjects'),0) <> 0 THEN RAISE EXCEPTION 'deleted count mismatch: subjects'; END IF;
  IF coalesce((SELECT n FROM cleanup_deleted WHERE table_name='accounts'),0) <> 10 THEN RAISE EXCEPTION 'deleted count mismatch: accounts'; END IF;
  IF coalesce((SELECT n FROM cleanup_deleted WHERE table_name='cycles'),0) <> 0 THEN RAISE EXCEPTION 'deleted count mismatch: cycles'; END IF;
  IF coalesce((SELECT n FROM cleanup_deleted WHERE table_name='tasks'),0) <> 10 THEN RAISE EXCEPTION 'deleted count mismatch: tasks'; END IF;
  IF coalesce((SELECT n FROM cleanup_deleted WHERE table_name='materials'),0) <> 10 THEN RAISE EXCEPTION 'deleted count mismatch: materials'; END IF;
  IF coalesce((SELECT n FROM cleanup_deleted WHERE table_name='playbooks'),0) <> 0 THEN RAISE EXCEPTION 'deleted count mismatch: playbooks'; END IF;
  IF coalesce((SELECT n FROM cleanup_deleted WHERE table_name='campaign_overrides'),0) <> 0 THEN RAISE EXCEPTION 'deleted count mismatch: campaign_overrides'; END IF;
  IF coalesce((SELECT n FROM cleanup_deleted WHERE table_name='cycle_decisions'),0) <> 0 THEN RAISE EXCEPTION 'deleted count mismatch: cycle_decisions'; END IF;
  IF coalesce((SELECT n FROM cleanup_deleted WHERE table_name='market_observations'),0) <> 0 THEN RAISE EXCEPTION 'deleted count mismatch: market_observations'; END IF;
  IF coalesce((SELECT n FROM cleanup_deleted WHERE table_name='legacy_import_records'),0) <> 0 THEN RAISE EXCEPTION 'deleted count mismatch: legacy_import_records'; END IF;
  IF coalesce((SELECT n FROM cleanup_deleted WHERE table_name='artifacts'),0) <> 10 THEN RAISE EXCEPTION 'deleted count mismatch: artifacts'; END IF;
  IF coalesce((SELECT n FROM cleanup_deleted WHERE table_name='content_versions'),0) <> 6 THEN RAISE EXCEPTION 'deleted count mismatch: content_versions'; END IF;
  IF coalesce((SELECT n FROM cleanup_deleted WHERE table_name='content_version_material_dependencies'),0) <> 4 THEN RAISE EXCEPTION 'deleted count mismatch: content_version_material_dependencies'; END IF;
  IF coalesce((SELECT n FROM cleanup_deleted WHERE table_name='publish_instances'),0) <> 2 THEN RAISE EXCEPTION 'deleted count mismatch: publish_instances'; END IF;
  IF coalesce((SELECT n FROM cleanup_deleted WHERE table_name='feedback_records'),0) <> 0 THEN RAISE EXCEPTION 'deleted count mismatch: feedback_records'; END IF;
  IF coalesce((SELECT n FROM cleanup_deleted WHERE table_name='task_snapshots'),0) <> 0 THEN RAISE EXCEPTION 'deleted count mismatch: task_snapshots'; END IF;
  IF coalesce((SELECT n FROM cleanup_deleted WHERE table_name='task_run_states'),0) <> 0 THEN RAISE EXCEPTION 'deleted count mismatch: task_run_states'; END IF;
  IF coalesce((SELECT n FROM cleanup_deleted WHERE table_name='idempotency_records'),0) <> 0 THEN RAISE EXCEPTION 'deleted count mismatch: idempotency_records'; END IF;
  IF (SELECT count(*) FROM publish_instances WHERE NOT is_test OR NOT is_simulated)
       <> 1568 THEN RAISE EXCEPTION 'post publish guard mismatch'; END IF;
  IF (SELECT count(*) FROM feedback_records WHERE NOT is_test OR NOT is_simulated)
       <> 117 THEN RAISE EXCEPTION 'post feedback guard mismatch'; END IF;
  IF (SELECT md5(string_agg(table_name||'.'||column_name||':'||data_type,','
       ORDER BY table_name,ordinal_position)) FROM information_schema.columns
       WHERE table_schema='public') <> '25192c11562827efedfc3b2c22c3b4fd' THEN
    RAISE EXCEPTION 'post schema guard mismatch';
  END IF;
  IF EXISTS (
    SELECT table_name,row_count,row_md5 FROM cleanup_non_target_guard
    EXCEPT
    SELECT 'workspaces', count(*), md5(coalesce(string_agg(md5(to_jsonb(x)::text),'' ORDER BY md5(to_jsonb(x)::text)),'')) FROM workspaces x WHERE NOT EXISTS (SELECT 1 FROM cleanup_workspaces c WHERE c.id=x.id)
UNION ALL
SELECT 'users', count(*), md5(coalesce(string_agg(md5(to_jsonb(x)::text),'' ORDER BY md5(to_jsonb(x)::text)),'')) FROM users x WHERE NOT EXISTS (SELECT 1 FROM cleanup_users c WHERE c.id=x.id)
UNION ALL
SELECT 'workspace_memberships', count(*), md5(coalesce(string_agg(md5(to_jsonb(x)::text),'' ORDER BY md5(to_jsonb(x)::text)),'')) FROM workspace_memberships x WHERE NOT EXISTS (SELECT 1 FROM cleanup_memberships c WHERE c.id=x.id)
UNION ALL
SELECT 'subjects', count(*), md5(coalesce(string_agg(md5(to_jsonb(x)::text),'' ORDER BY md5(to_jsonb(x)::text)),'')) FROM subjects x WHERE NOT EXISTS (SELECT 1 FROM cleanup_subjects c WHERE c.id=x.id)
UNION ALL
SELECT 'accounts', count(*), md5(coalesce(string_agg(md5(to_jsonb(x)::text),'' ORDER BY md5(to_jsonb(x)::text)),'')) FROM accounts x WHERE NOT EXISTS (SELECT 1 FROM cleanup_accounts c WHERE c.id=x.id)
UNION ALL
SELECT 'cycles', count(*), md5(coalesce(string_agg(md5(to_jsonb(x)::text),'' ORDER BY md5(to_jsonb(x)::text)),'')) FROM cycles x WHERE NOT EXISTS (SELECT 1 FROM cleanup_cycles c WHERE c.id=x.id)
UNION ALL
SELECT 'tasks', count(*), md5(coalesce(string_agg(md5(to_jsonb(x)::text),'' ORDER BY md5(to_jsonb(x)::text)),'')) FROM tasks x WHERE NOT EXISTS (SELECT 1 FROM cleanup_tasks c WHERE c.id=x.id)
UNION ALL
SELECT 'materials', count(*), md5(coalesce(string_agg(md5(to_jsonb(x)::text),'' ORDER BY md5(to_jsonb(x)::text)),'')) FROM materials x WHERE NOT EXISTS (SELECT 1 FROM cleanup_materials c WHERE c.id=x.id)
UNION ALL
SELECT 'playbooks', count(*), md5(coalesce(string_agg(md5(to_jsonb(x)::text),'' ORDER BY md5(to_jsonb(x)::text)),'')) FROM playbooks x WHERE NOT EXISTS (SELECT 1 FROM cleanup_playbooks c WHERE c.id=x.id)
UNION ALL
SELECT 'campaign_overrides', count(*), md5(coalesce(string_agg(md5(to_jsonb(x)::text),'' ORDER BY md5(to_jsonb(x)::text)),'')) FROM campaign_overrides x WHERE NOT EXISTS (SELECT 1 FROM cleanup_campaign_overrides c WHERE c.id=x.id)
UNION ALL
SELECT 'cycle_decisions', count(*), md5(coalesce(string_agg(md5(to_jsonb(x)::text),'' ORDER BY md5(to_jsonb(x)::text)),'')) FROM cycle_decisions x WHERE NOT EXISTS (SELECT 1 FROM cleanup_cycle_decisions c WHERE c.id=x.id)
UNION ALL
SELECT 'market_observations', count(*), md5(coalesce(string_agg(md5(to_jsonb(x)::text),'' ORDER BY md5(to_jsonb(x)::text)),'')) FROM market_observations x WHERE NOT EXISTS (SELECT 1 FROM cleanup_market_observations c WHERE c.id=x.id)
UNION ALL
SELECT 'legacy_import_records', count(*), md5(coalesce(string_agg(md5(to_jsonb(x)::text),'' ORDER BY md5(to_jsonb(x)::text)),'')) FROM legacy_import_records x WHERE NOT EXISTS (SELECT 1 FROM cleanup_legacy_import_records c WHERE c.id=x.id)
UNION ALL
SELECT 'artifacts', count(*), md5(coalesce(string_agg(md5(to_jsonb(x)::text),'' ORDER BY md5(to_jsonb(x)::text)),'')) FROM artifacts x WHERE NOT EXISTS (SELECT 1 FROM cleanup_artifacts c WHERE c.id=x.id)
UNION ALL
SELECT 'content_versions', count(*), md5(coalesce(string_agg(md5(to_jsonb(x)::text),'' ORDER BY md5(to_jsonb(x)::text)),'')) FROM content_versions x WHERE NOT EXISTS (SELECT 1 FROM cleanup_versions c WHERE c.id=x.id)
UNION ALL
SELECT 'content_version_material_dependencies', count(*), md5(coalesce(string_agg(md5(to_jsonb(x)::text),'' ORDER BY md5(to_jsonb(x)::text)),'')) FROM content_version_material_dependencies x WHERE NOT EXISTS (SELECT 1 FROM cleanup_dependencies c WHERE c.content_version_id=x.content_version_id AND c.material_id=x.material_id)
UNION ALL
SELECT 'publish_instances', count(*), md5(coalesce(string_agg(md5(to_jsonb(x)::text),'' ORDER BY md5(to_jsonb(x)::text)),'')) FROM publish_instances x WHERE NOT EXISTS (SELECT 1 FROM cleanup_publish_instances c WHERE c.id=x.id)
UNION ALL
SELECT 'feedback_records', count(*), md5(coalesce(string_agg(md5(to_jsonb(x)::text),'' ORDER BY md5(to_jsonb(x)::text)),'')) FROM feedback_records x WHERE NOT EXISTS (SELECT 1 FROM cleanup_feedback_records c WHERE c.id=x.id)
UNION ALL
SELECT 'task_snapshots', count(*), md5(coalesce(string_agg(md5(to_jsonb(x)::text),'' ORDER BY md5(to_jsonb(x)::text)),'')) FROM task_snapshots x WHERE NOT EXISTS (SELECT 1 FROM cleanup_task_snapshots c WHERE c.id=x.id)
UNION ALL
SELECT 'task_run_states', count(*), md5(coalesce(string_agg(md5(to_jsonb(x)::text),'' ORDER BY md5(to_jsonb(x)::text)),'')) FROM task_run_states x WHERE NOT EXISTS (SELECT 1 FROM cleanup_task_run_states c WHERE c.id=x.id)
UNION ALL
SELECT 'idempotency_records', count(*), md5(coalesce(string_agg(md5(to_jsonb(x)::text),'' ORDER BY md5(to_jsonb(x)::text)),'')) FROM idempotency_records x WHERE NOT EXISTS (SELECT 1 FROM cleanup_idempotency_records c WHERE c.key=x.key)
  ) OR EXISTS (
    SELECT 'workspaces', count(*), md5(coalesce(string_agg(md5(to_jsonb(x)::text),'' ORDER BY md5(to_jsonb(x)::text)),'')) FROM workspaces x WHERE NOT EXISTS (SELECT 1 FROM cleanup_workspaces c WHERE c.id=x.id)
UNION ALL
SELECT 'users', count(*), md5(coalesce(string_agg(md5(to_jsonb(x)::text),'' ORDER BY md5(to_jsonb(x)::text)),'')) FROM users x WHERE NOT EXISTS (SELECT 1 FROM cleanup_users c WHERE c.id=x.id)
UNION ALL
SELECT 'workspace_memberships', count(*), md5(coalesce(string_agg(md5(to_jsonb(x)::text),'' ORDER BY md5(to_jsonb(x)::text)),'')) FROM workspace_memberships x WHERE NOT EXISTS (SELECT 1 FROM cleanup_memberships c WHERE c.id=x.id)
UNION ALL
SELECT 'subjects', count(*), md5(coalesce(string_agg(md5(to_jsonb(x)::text),'' ORDER BY md5(to_jsonb(x)::text)),'')) FROM subjects x WHERE NOT EXISTS (SELECT 1 FROM cleanup_subjects c WHERE c.id=x.id)
UNION ALL
SELECT 'accounts', count(*), md5(coalesce(string_agg(md5(to_jsonb(x)::text),'' ORDER BY md5(to_jsonb(x)::text)),'')) FROM accounts x WHERE NOT EXISTS (SELECT 1 FROM cleanup_accounts c WHERE c.id=x.id)
UNION ALL
SELECT 'cycles', count(*), md5(coalesce(string_agg(md5(to_jsonb(x)::text),'' ORDER BY md5(to_jsonb(x)::text)),'')) FROM cycles x WHERE NOT EXISTS (SELECT 1 FROM cleanup_cycles c WHERE c.id=x.id)
UNION ALL
SELECT 'tasks', count(*), md5(coalesce(string_agg(md5(to_jsonb(x)::text),'' ORDER BY md5(to_jsonb(x)::text)),'')) FROM tasks x WHERE NOT EXISTS (SELECT 1 FROM cleanup_tasks c WHERE c.id=x.id)
UNION ALL
SELECT 'materials', count(*), md5(coalesce(string_agg(md5(to_jsonb(x)::text),'' ORDER BY md5(to_jsonb(x)::text)),'')) FROM materials x WHERE NOT EXISTS (SELECT 1 FROM cleanup_materials c WHERE c.id=x.id)
UNION ALL
SELECT 'playbooks', count(*), md5(coalesce(string_agg(md5(to_jsonb(x)::text),'' ORDER BY md5(to_jsonb(x)::text)),'')) FROM playbooks x WHERE NOT EXISTS (SELECT 1 FROM cleanup_playbooks c WHERE c.id=x.id)
UNION ALL
SELECT 'campaign_overrides', count(*), md5(coalesce(string_agg(md5(to_jsonb(x)::text),'' ORDER BY md5(to_jsonb(x)::text)),'')) FROM campaign_overrides x WHERE NOT EXISTS (SELECT 1 FROM cleanup_campaign_overrides c WHERE c.id=x.id)
UNION ALL
SELECT 'cycle_decisions', count(*), md5(coalesce(string_agg(md5(to_jsonb(x)::text),'' ORDER BY md5(to_jsonb(x)::text)),'')) FROM cycle_decisions x WHERE NOT EXISTS (SELECT 1 FROM cleanup_cycle_decisions c WHERE c.id=x.id)
UNION ALL
SELECT 'market_observations', count(*), md5(coalesce(string_agg(md5(to_jsonb(x)::text),'' ORDER BY md5(to_jsonb(x)::text)),'')) FROM market_observations x WHERE NOT EXISTS (SELECT 1 FROM cleanup_market_observations c WHERE c.id=x.id)
UNION ALL
SELECT 'legacy_import_records', count(*), md5(coalesce(string_agg(md5(to_jsonb(x)::text),'' ORDER BY md5(to_jsonb(x)::text)),'')) FROM legacy_import_records x WHERE NOT EXISTS (SELECT 1 FROM cleanup_legacy_import_records c WHERE c.id=x.id)
UNION ALL
SELECT 'artifacts', count(*), md5(coalesce(string_agg(md5(to_jsonb(x)::text),'' ORDER BY md5(to_jsonb(x)::text)),'')) FROM artifacts x WHERE NOT EXISTS (SELECT 1 FROM cleanup_artifacts c WHERE c.id=x.id)
UNION ALL
SELECT 'content_versions', count(*), md5(coalesce(string_agg(md5(to_jsonb(x)::text),'' ORDER BY md5(to_jsonb(x)::text)),'')) FROM content_versions x WHERE NOT EXISTS (SELECT 1 FROM cleanup_versions c WHERE c.id=x.id)
UNION ALL
SELECT 'content_version_material_dependencies', count(*), md5(coalesce(string_agg(md5(to_jsonb(x)::text),'' ORDER BY md5(to_jsonb(x)::text)),'')) FROM content_version_material_dependencies x WHERE NOT EXISTS (SELECT 1 FROM cleanup_dependencies c WHERE c.content_version_id=x.content_version_id AND c.material_id=x.material_id)
UNION ALL
SELECT 'publish_instances', count(*), md5(coalesce(string_agg(md5(to_jsonb(x)::text),'' ORDER BY md5(to_jsonb(x)::text)),'')) FROM publish_instances x WHERE NOT EXISTS (SELECT 1 FROM cleanup_publish_instances c WHERE c.id=x.id)
UNION ALL
SELECT 'feedback_records', count(*), md5(coalesce(string_agg(md5(to_jsonb(x)::text),'' ORDER BY md5(to_jsonb(x)::text)),'')) FROM feedback_records x WHERE NOT EXISTS (SELECT 1 FROM cleanup_feedback_records c WHERE c.id=x.id)
UNION ALL
SELECT 'task_snapshots', count(*), md5(coalesce(string_agg(md5(to_jsonb(x)::text),'' ORDER BY md5(to_jsonb(x)::text)),'')) FROM task_snapshots x WHERE NOT EXISTS (SELECT 1 FROM cleanup_task_snapshots c WHERE c.id=x.id)
UNION ALL
SELECT 'task_run_states', count(*), md5(coalesce(string_agg(md5(to_jsonb(x)::text),'' ORDER BY md5(to_jsonb(x)::text)),'')) FROM task_run_states x WHERE NOT EXISTS (SELECT 1 FROM cleanup_task_run_states c WHERE c.id=x.id)
UNION ALL
SELECT 'idempotency_records', count(*), md5(coalesce(string_agg(md5(to_jsonb(x)::text),'' ORDER BY md5(to_jsonb(x)::text)),'')) FROM idempotency_records x WHERE NOT EXISTS (SELECT 1 FROM cleanup_idempotency_records c WHERE c.key=x.key)
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
