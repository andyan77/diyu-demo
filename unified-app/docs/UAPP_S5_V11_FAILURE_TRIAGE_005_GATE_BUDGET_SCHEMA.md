# UAPP S5 v1.1 Failure Triage 005 — inherited Runner budget schema

```yaml
observed_failure: >
  Gate v1.2 preflight stopped with KeyError before any workflow run because the
  inherited Runner requires total-budget aliases that v1.2 expressed only as used
  and remaining values.
frozen_target: Preflight the repaired candidate under the unchanged 19-turn/114-attempt formal plan.
candidate_sources:
  - CHECKER_OR_FIXTURE
confirmed_origin: CHECKER_OR_FIXTURE
evidence:
  - KeyError: formal_top_level_turn_count
  - workflow runs created: 0
  - model calls: 0
mutation_target: Versioned Gate/Manifest/Executor adapter only
protected_targets:
  - Gate v1.2 and all earlier frozen records
  - scenarios and acceptance criteria
  - repaired UAPP candidate and protected applications
next_reverification: >
  Freeze Gate v1.3 with the inherited total-budget aliases plus the already frozen
  used/remaining accounting, then rerun preflight before any model call.
model_calls_before_failure: 0
side_effects: none
```

