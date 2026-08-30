# UAPP S5 inline artifact successor · implementation and Phase C

task_id: `DIYU-V1-UNIFIED-DIFY-APPLICATION-001`  
successor_iteration: `1/1`  
model_calls_during_implementation_and_controls: `0`

## Confirmed mutation target

Only the already-confirmed seam
`UAPP_CURRENT_TURN_INLINE_ARTIFACT_SOURCE_TO_BINDING_AND_DELIVERY` changed:

- `uapp_inline_artifact`: derives call-companion values from the same current-turn user text;
- `uapp_pick_upstream`: transports the source-bound companion record without interpreting it;
- `uapp_fields`: validates task/source turn/source kind/body fingerprint and exact user support before
  registering the two ordinary canonical fields and binding the unchanged artifact body.

No edge, conversation variable, artifact ledger rule, acceptance rule or professional application changed.
The complete artifact body remains call-local, `persisted=false`, `accepted=false`, and absent from canonical
fields.

## Frozen deterministic result

- base UAPP graph md5: `f7d9857323823b64d288455e1b67cf80`
- candidate canonical sha256: `8034ddba7c2db320d31d301aadb1e88411542950dc9352d3d637f917706cb544`
- nodes: `56 → 56`; edges: `58 → 58`; conversation variables added: `0`
- final controls: `28/28 PASS`
- CAP-05 body: length `95`, source/injected sha256
  `5e2447a1401c404abdf621f92d5279bcd02228fe2c13f6ba5cada56e93b64894`
- CAP-05 current-turn companions:
  - `content.origin_mode = 室内门店拍摄`
  - `content.promise = 我们只展示真实上身效果，不承诺显瘦。`
- CAP-06 body: length `78`, source/injected sha256
  `00c3372f5b38e5eca06a9cf97fa7acc09707b753deceea2e3f670f84051e9fcd`
- single-variable negatives reject missing origin, missing promise, cross-task, wrong source, wrong turn,
  wrong body fingerprint and values unsupported by the user text.

The first controls file recorded `27/28` because its checker looked for a tool-node input in the code-node
`variables` collection. That file is preserved. Versioned checker v1.1 reads
`tool_parameters.capability_call.value` and obtains `28/28`; this changes only the observation path, not the
business predicate or candidate.

## Tool checks

- Python bytecode compilation: PASS (`python3`)
- ruff: PASS
- `git diff --check`: PASS
- mypy: NOT_VERIFIED(INPUT_ENVIRONMENT_OR_TOOL); the installed launcher cannot import the `mypy` package.
  This command did not execute the checker and is not counted as PASS.

## Protected surface

Byte-identical UAPP nodes: `m1_shadow`, `m1_compiler`, `uapp_m3`, `uapp_hop`, `uapp_seam`, `uapp_state`,
`uapp_persist`, `uapp_save`, `uapp_delivery`, `uapp_td24_correction`, `uapp_td24_block`.

Pre-publication live guards:

- active workflows: `0`
- M2 schema md5: `25192c11562827efedfc3b2c22c3b4fd`
- non-test publish rows: `1568`
- non-test feedback rows: `117`
- main / origin/main: `01a42b0ed97344a67302ecb6778ae4a772eb28b2`

## Next gate

Commit and push this implementation plus deterministic evidence before publishing. After publication, create
a new Gate/Manifest/Runner binding for the exact successor graph. Only then may the one authorized successor
CAP-05 formal slot run.
