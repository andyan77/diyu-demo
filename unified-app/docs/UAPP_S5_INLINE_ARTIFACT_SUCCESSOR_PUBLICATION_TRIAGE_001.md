# FAILURE TRIAGE · successor publication label

observed_failure: `POST .../workflows/publish` returned HTTP 400 because `marked_name` exceeded the
platform's 20-character limit. The candidate draft was written and read back, but the published pointer did
not move.

frozen_target: Publish candidate canonical sha256
`8034ddba7c2db320d31d301aadb1e88411542950dc9352d3d637f917706cb544` without changing its graph,
acceptance criteria or protected surface.

candidate_sources:

- `CHECKER_OR_FIXTURE`
- `INPUT_ENVIRONMENT_OR_TOOL`

confirmed_origin: `INPUT_ENVIRONMENT_OR_TOOL` at the version-label parameter of the publication builder.

evidence:

- platform response: HTTP 400 `marked_name String should have at most 20 characters`;
- published UAPP graph remains `f7d9857323823b64d288455e1b67cf80`;
- draft canonical sha256 is the frozen candidate `8034ddba…cb544`;
- active workflows `0`; model calls `0`; formal runs `0`; business side effects `0`.

mutation_target: a versioned publication wrapper whose only semantic difference is a label no longer than 20
characters.

protected_targets: candidate graph, Gate/Scenario/Checker meaning, UAPP nodes, M1/M2/M3, Hop, Seam, six
professional applications, PP/provider, schema, non-test data, main and all prior RAW.

next_reverification: Verify draft canonical hash, publish with the shortened label, then read back the exact
published graph and all protected bindings. This is not a formal scenario retry and consumes no model budget.
