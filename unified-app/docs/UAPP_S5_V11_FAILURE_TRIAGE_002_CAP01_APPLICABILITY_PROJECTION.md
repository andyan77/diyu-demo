# UAPP S5 v1.1 Failure Triage 002 — CAP-01 applicability projection

`task_id: DIYU-V1-UNIFIED-DIFY-APPLICATION-001`

`attempt_run_id: f40f6779-c115-41cb-be06-e819aa848af5`

## FAILURE TRIAGE

```yaml
observed_failure: >
  CAP-01 correctly routed only to MATRIX, but MATRIX returned the precise gap
  applicability_reason and produced no artifact. The user had already stated that
  this was a formal long-term four-account redesign, not a single-content request.
frozen_target: >
  UAPP-CAP-01 must execute MATRIX under a valid long-term matrix request, produce a
  non-empty artifact, and run no other professional capability.
candidate_sources:
  - CHECKER_OR_FIXTURE
  - SYSTEM_UNDER_TEST
confirmed_origin: SYSTEM_UNDER_TEST
evidence:
  - run_id=f40f6779-c115-41cb-be06-e819aa848af5
  - uapp_route.target_capability=MATRIX
  - uapp_route.intent_reason explicitly classifies the request as long-term account governance
  - uapp_hop.capability_call omits applicability_reason
  - MATRIX return precise_gap=applicability_reason
  - MATRIX artifact is empty and no content_version is created
mutation_target: >
  UAPP-owned deterministic projection between the route decision and the current
  capability call. Carry the user-supported route applicability reason into the
  MATRIX call without changing Hop, Seam, MATRIX, M3, or canonical task state.
protected_targets:
  - M1 / M2 / M3
  - Hop / Seam
  - MATRIX and the other five professional applications
  - PP/provider
  - M2 schema and non-test data
  - historical Gate, Scenario, RAW, Result, and Attempt
  - main / origin/main
next_reverification: >
  First run deterministic positive and single-variable negative controls, then bind
  a versioned successor Gate to the repaired UAPP graph and rerun only CAP-01 once.
model_calls_before_failure:
  top_level_runs: 1
  llm_node_attempts: 5
side_effects:
  new_artifacts: 0
  new_content_versions: 0
  real_publish: 0
  non_test_writes: 0
```

The failure does not prove a defect in the protected MATRIX application. MATRIX
correctly rejected a call that omitted one of its declared input-contract fields.
The highest confirmed failing node is the UAPP-owned projection seam that dropped
an already available, user-supported applicability reason.

