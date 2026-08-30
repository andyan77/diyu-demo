# FAILURE TRIAGE 002 · CAP-06 CTA contract normalization

task_id: `DIYU-V1-UNIFIED-DIFY-APPLICATION-001`
formal_run_id: `e71e84af-e3e3-47ec-afc4-72bd02941540`
candidate_graph_md5: `07ea334bfcbe6e87ba8c5cd5d5dac380`

observed_failure: CAP-06 correctly routed only to Publishing & Packaging and bound the exact 78-character
realized-content body, but `uapp_fields` left `cta_contract` missing. The accepted professional capability
therefore returned one natural CTA question and produced no packaging artifact.

frozen_target: An already realized, legal content body directly reaches Publishing & Packaging and produces
usable title/cover/post/topic/natural-CTA packaging under the user's stated boundary: Xiaohongshu; no price,
discount or off-platform purchase promise.

candidate_sources:

- `CONTRACT_OR_INTENT`
- `ORACLE_OR_CRITERION`
- `CHECKER_OR_FIXTURE`
- `INPUT_ENVIRONMENT_OR_TOOL`
- `SYSTEM_UNDER_TEST`
- `INSUFFICIENT_EVIDENCE`

confirmed_origin: `SYSTEM_UNDER_TEST` at the current-turn inline-artifact companion normalization portion of
the UAPP seam.

evidence:

- input/body source: `inline_status=INLINE_READY`, type `CONTENT_BODY_OR_BEATS`, body length `78`, body hash
  and task/current-turn source metadata validated;
- selector: `INLINE_SELECTED`, upstream `USER_REALIZED_CONTENT`, not self-upstream;
- fields: body `BOUND`, `content.promise` registered, but final `gaps_text=cta_contract`;
- Seam and Publishing & Packaging each ran once; the other five professional capabilities ran zero times;
- professional Return: precise gap asks whether the user wants an audience action and how it is received;
- artifact length `0`; no state artifact/store record was fabricated;
- HTTP 200, LLM attempts `5`, failed nodes `0`, platform replay `0`, manual retry `0`;
- M2 non-test publish/feedback `1568/117` and schema md5 `25192c…b4fd` unchanged;
- all protected graph hashes equal Gate v1.8.

Contract back-reference:

- M0–M5 acceptance plan v1.1 §9.3: “已有成片/素材，只做 Publishing & Packaging” is a required legal
  short entry;
- §5.5: platform-internal follow/comment/save is a low-risk CTA candidate when goal and expression allow;
- the frozen user text explicitly asks for a natural CTA and explicitly excludes price, discount and
  off-platform purchase promises.

The UAPP may therefore normalize the existing user meaning into a bounded platform-internal low-risk CTA
contract without choosing a business-conversion goal or access path. It may not invent purchase, inquiry,
lead, store-visit or off-platform actions.

mutation_target: None in this Attempt. The independently confirmed minimal successor candidate would extend
the same source-bound companion record with a user-supported `cta.contract`, validate task/turn/body digest
and exact source support in `uapp_fields`, and keep the professional app unchanged.

protected_targets: M1/M2/M3, Hop, Seam, all six professional applications, PP b2, schema, non-test data,
Scenario v1.1, Gate v1.8, Checker, historical RAW and main.

next_reverification: A newly authorized, versioned CAP-06-only successor would first run zero-model positive
and single-variable negative controls, then one CAP-06 formal run. CAP-05 remains PASS/CURRENT if impact
analysis proves its PD-only branch unchanged.

stop_basis: The Founder-authorized same-scope successor `1/1` was consumed before CAP-05, and Gate v1.8
prohibits a third candidate iteration. CAP-06 was allowed one formal input and has used it. No rerun or graph
change is authorized in this package.

model_calls_before_failure: current REBASE `3` top-level / `16` LLM attempts; lifetime `11` / `60`.

side_effects: Test-scoped workspace/cycle/task rows only. No artifact, publish instance, feedback, real
platform action, non-test data change, schema change, credential read, main change or protected-app change.
