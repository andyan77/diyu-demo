# UAPP S5 v1.1 Failure Triage 003 — publish label validation

```yaml
observed_failure: >
  The Dify publish endpoint rejected marked_name before publication because the
  string exceeded its 20-character limit.
frozen_target: Publish the deterministically verified UAPP repair candidate with zero model calls.
candidate_sources:
  - INPUT_ENVIRONMENT_OR_TOOL
confirmed_origin: INPUT_ENVIRONMENT_OR_TOOL
evidence:
  - HTTP 400 invalid_param
  - PublishWorkflowPayload.marked_name String should have at most 20 characters
  - published UAPP graph remained 89bbfeade1f149ccce12a768bed6e94a
  - draft readback equals candidate sha256 726b1d196717bb4e68b43fe9e6a3b9b85734a5db4611cf4d10bac19ee213dad5
mutation_target: UAPP_S5_PROJECTION_BUILD_v1.0.py marked_name only
protected_targets:
  - candidate graph
  - Gate / Scenario / Checker
  - UAPP published graph until the valid publish request
  - all protected applications and data
next_reverification: >
  Reissue the same publish operation with a <=20-character label, then compare
  published canonical graph sha256 byte-for-byte with the verified candidate.
model_calls_before_failure: 0
side_effects:
  draft_candidate_written: true
  published_graph_changed: false
  workflow_runs: 0
  data_writes: 0
```

