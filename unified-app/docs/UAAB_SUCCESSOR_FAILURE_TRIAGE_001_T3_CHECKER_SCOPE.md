# UAAB Successor v1.2 · FAILURE TRIAGE 001 · T3 Checker Scope

- task_id: `DIYU-V1-UAPP-ACCEPTED-ARTIFACT-BINDING-001`
- frozen Gate: `UAAB_GATE_v1.2.json`
- Gate sha256: `dbe4c023256e378d93827094b5c762f7c1b67b1c7528fff92fbbb84b219ea622`
- T3 top-level run: `4751f9b1-ac88-41e4-b731-2fe6f9bf0cbc`
- first observed at: after the only authorized T3 run; no additional model call followed

## FAILURE TRIAGE

### observed_failure

`UAAB_SUCCESSOR_VERIFY_v1.2.py` reported `T3-05 = FAIL` while all other T3 checks passed.
The report is retained unchanged at
`unified-app/evidence/stages/uapp_artifact_binding/UAAB_SUCCESSOR_T3_VERIFY_v1.2.json`
(sha256 `7818b65ba7e97617ad0dcafe9525414e691a65e9d427becf6ac5d84cf8208532`).

The check observed an 8816-character artifact with sha256
`f52d24b8b40ed3990a8f750f7262666ffdc51ace5f19540059b3fc0f462166d3`, but rejected it
because PP returned `artifact_status = STRUCTURE_MISSING_RAW_PRESERVED` rather than `OK`.

### frozen_target

The authoritative Gate froze T3 item 5 as:

> `PP b2 emits a non-empty non-placeholder packaging product`

It did **not** require `artifact_status = OK`, complete M4 schema extraction, or D1-a structural
compliance. The same Gate separately required only the existing D1-b fact boundary and D1-c CTA
boundary. A checker cannot add D1-a after the Gate was frozen.

### candidate_sources

- `CONTRACT_OR_INTENT`: refuted — the Founder prompt and Gate both use the same narrow wording.
- `ORACLE_OR_CRITERION`: refuted at the Gate level — the criterion is unambiguous.
- `CHECKER_OR_FIXTURE`: confirmed — `substantive_artifact()` added `artifact_status == "OK"` and
  `delivery_outcome == "DELIVERED"`; the first condition is outside T3 item 5.
- `INPUT_ENVIRONMENT_OR_TOOL`: refuted — HTTP 200, all workflow runs succeeded, zero exceptions,
  one request, zero platform replay.
- `SYSTEM_UNDER_TEST`: not confirmed for this failure — the raw packaging product exists and is
  independently readable.
- `INSUFFICIENT_EVIDENCE`: refuted — raw artifact, user delivery, run records and storage records
  are all present.

### confirmed_origin

`CHECKER_OR_FIXTURE` — specifically, checker scope exceeded the pre-frozen Gate.

### evidence

- Raw T3 evidence sha256:
  `e9480929285aa180541714b2c334cb488b23ecd47f865393ed656092d9631c05`.
- PP run `1367a48d-412a-4528-9775-4cf58bdf4898`: `succeeded`, exceptions 0.
- `delivery_outcome = DELIVERED`, `sufficiency_status = SUFFICIENT`,
  `user_delivery_status = OK`, `recovery_used = false`.
- Artifact length 8816; it begins with `---M4_ARTIFACT---` and contains three title candidates,
  a recommended title, cover, first-frame direction, publish copy, two packaging routes,
  `used_fact_refs`, `fact_check_status`, release checks, failure cases, assumptions and missing items.
- User delivery length 1198 and is not a placeholder.
- The artifact does not begin with `这一步没有产出可以交给你的内容`.
- D1-b and D1-c checks both passed on the actual artifact and user delivery.

Applying only the frozen wording therefore gives T3 item 5 `PASS`: the product is non-empty,
non-placeholder, and substantively a packaging product. The structural parser status is retained
as a disclosed observation, but it is not an authorized blocking condition in this successor Gate.

### mutation_target

`NONE`. The checker, Gate, input and tested implementation are left unchanged. The false-failing
checker output is preserved rather than overwritten.

### protected_targets

UAPP candidate, PP b2, provider, M1/M2/M3, Hop, Seam, six professional Skills, prior Gates,
prior Checkers, old RAW evidence, frozen inputs and main.

### next_reverification

No model rerun and no fourth turn. Recompute only the literal frozen T3 item 5 from the already
retained raw artifact, then complete the Gate-authoritative closeout. This read-only adjudication
does not change the criterion and does not create a new sample.

## Gate-authoritative disposition

The checker failure is real and remains recorded, but it is not a failure of a frozen T3 item.
The Gate-authoritative result is T3 `PASS`: items 1–4 and 6–12 are unchanged `PASS`; item 5 is
`PASS` under its exact pre-frozen wording. Because no frozen item is non-PASS, the success rule
retains the successor UAPP / PP / provider binding rather than applying the failure-only rollback.
