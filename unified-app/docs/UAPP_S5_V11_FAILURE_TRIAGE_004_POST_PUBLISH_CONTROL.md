# UAPP S5 v1.1 Failure Triage 004 — post-publish control mode

```yaml
observed_failure: >
  The first post-publish control wrapper attempted to apply the repair a second time
  to the already repaired published graph and rejected its own signature anchor.
frozen_target: Read-only revalidation of the published repaired candidate before model calls.
candidate_sources:
  - CHECKER_OR_FIXTURE
confirmed_origin: CHECKER_OR_FIXTURE
evidence:
  - RuntimeError: uapp_fields signature anchor mismatch
  - published UAPP remains canonical sha256 726b1d196717bb4e68b43fe9e6a3b9b85734a5db4611cf4d10bac19ee213dad5
  - no workflow run or model call occurred
mutation_target: UAPP_S5_PROJECTION_CONTROLS_v1.1.py only
protected_targets:
  - published UAPP candidate
  - frozen scenarios and acceptance criteria
  - all protected applications and data
next_reverification: >
  Execute the same positive and single-variable negative controls directly against
  the read-only published uapp_fields code and bind the result to publication evidence.
model_calls_before_failure: 0
side_effects: none
```

