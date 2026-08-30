# UAPP S5 v1.1 Failure Triage 006 — capability artifact oracle

`run_id: 7d88a44f-6fc4-44ac-b51f-a664d16b546e`

```yaml
observed_failure: >
  The repaired CAP-01 run executed MATRIX exactly once and produced a 5,868-byte
  professional artifact, but Checker v1.1 reported CAP-04 FAIL. Its result details
  referenced the earlier f40f... run and the old 89bb... graph, and its added CAP-04
  predicate required M2 artifacts/content_versions rows.
frozen_target: >
  UAPP-AC-04 requires each professional capability to complete one minimum executable
  smoke from the unified app. UAPP-AC-11 requires the run, module execution, relevant
  M2 writes, graph/hash, and evidence to be traceable.
candidate_sources:
  - ORACLE_OR_CRITERION
  - CHECKER_OR_FIXTURE
confirmed_origin: CHECKER_OR_FIXTURE
evidence:
  - actual run_id=7d88a44f-6fc4-44ac-b51f-a664d16b546e
  - uapp_fields.applicability_projection_status=PROJECTED_USER_SUPPORTED_ROUTE_REASON
  - MATRIX app runs=1; other five professional app runs=0
  - uapp_seam artifact length=5868
  - conversation.uapp_last_artifact contains a separate MATRIX record with the exact body
  - conversation.uapp_last_capability=MATRIX
  - platform_internal_replays=0; failed nodes=0
  - Checker result T-03 refers to stale run_id=f40f6779-c115-41cb-be06-e819aa848af5
  - Checker result T-07 compares against stale UAPP graph=89bbfeade1f149ccce12a768bed6e94a
  - Task Contract UAPP-AC-04 says minimum executable smoke, not mandatory M2 artifact rows
mutation_target: >
  One versioned post-result Checker rebase: bind the current evidence namespace and
  validate the actual professional node artifact against the bounded conversation
  artifact store. Preserve M2 checks where the scenario contract requires an M2 side effect.
protected_targets:
  - repaired UAPP candidate
  - all frozen earlier Checkers, Gates, RAW, and checks
  - scenarios and UAPP-AC-01..11 product meaning
  - M1/M2/M3/Hop/Seam/six professional apps/PP/provider/main
next_reverification: >
  Run deterministic positive and single-variable negative controls, freeze the
  versioned Checker/Gate before results, then execute CAP-01 once in a new formal slot.
model_calls_before_failure:
  total_top_level_runs: 2
  total_llm_node_attempts: 10
side_effects:
  test_workspace_only: true
  new_conversation_artifact_records: 1
  m2_artifact_rows: 0
  real_publish: 0
  non_test_writes: 0
```

The MATRIX user delivery correctly disclosed that the formal matrix still needs real
people and real work facts. That conditional professional result is not a placeholder:
the internal artifact contains a complete fact inventory, dependency-local Return,
provisional matrix skeleton, and exact next fact. UAPP-AC-04 tests reachability and a
minimum executable smoke, not whether Founder has supplied enough facts to finalize a
real business matrix.

