# Acceptance Fixtures

Use this file only for construction, review, regression, or disputed-rule validation. Freeze inputs, acceptance statements, model, tools, parameters, and output budget before seeing results.

## 1. Test protocol

For every formal run record:

- fixture version and hash;
- Skill/source/reference versions;
- Dify workflow and node versions;
- actual model and parameters;
- tool permissions and source availability;
- acceptance criteria frozen before output;
- structured result plus concise user-facing result;
- PASS, FAIL, or NOT_VERIFIED with evidence.

Use the same model, input, tool access, parameter class, output budget, and candidate opportunity for comparative tests. A baseline must be a competent generic operating prompt, not an intentionally weak prompt.

## 2. Goal counterfactual family

Freeze one account, facts, platform, capacity, identity, products, and expression permission. Change only the primary objective across:

- long-term value;
- cold-start;
- follower growth;
- traffic;
- GMV;
- leads;
- store visits.

Pass when content roles, resource order, validation target, or fulfillment path change materially and correctly while identity and facts remain stable. Fail when only CTA/labels change, goals collapse into “quality content,” or GMV/leads/store visits become interchangeable.

### Negative probe

Give a traffic objective plus a strong long-term-value reference asset. Fail if the output silently rewrites traffic as long-term education. Give a GMV objective with no valid sales path. Fail if it fabricates purchase CTA instead of degrading locally.

### Ablation

Remove the objective-fidelity section. The outputs should become materially less distinct; otherwise the section is not earning its complexity.

## 3. Same goal, different stage

Freeze the same follower-growth objective and account identity. Vary only maturity evidence across cold-start, direction validation, growth, and stable operation.

Pass when exploration scope, commitment, cadence, and proof requirements differ without changing the objective. Fail when stage is inferred from one metric or uses fixed thresholds.

Add an ambiguous variant with evidence compatible with growth or stable operation. Pass when the Skill gives a provisional interpretation and one discriminating observation.

## 4. Conversion overlay and decline hypothesis

Case A: a direction-validation account receives a bounded conversion sprint with real inventory and a valid path. Pass when conversion is treated as an overlay rather than false maturity.

Case B: views fall 40% while inquiries and store visits remain stable; distribution conditions changed. Pass when decline remains a hypothesis and the plan avoids account-wide redesign without stronger evidence.

## 5. Capacity conflict

User asks for three posts per day; current people/assets can complete two. Provide three candidate business jobs with unequal value.

Pass when the Skill selects two, explains the displaced benefit, and defers/replaces/drops the third. Fail when it converts the request to three per week, degrades all three, or asks the user to solve ordinary prioritization.

## 6. Stable delivery versus exploration

Provide one repeatedly supported mechanism, one single-hit mechanism, and one untested but account-fit opportunity.

Pass when evidence maturity and current-use decision are separated, a bounded exploration has support/refutation/expiry, and a single hit does not become an account-wide template. Fail when it enforces a fixed ratio or requires exploration in all conditions.

## 7. Apparel local invalidation

Use one product with two colors; one color becomes unavailable, price remains current, material facts remain confirmed, and no try-on media exists.

Pass when affected sellability/CTA/tasks change locally, material facts remain usable, and only on-body claims requiring evidence are blocked. Fail when the entire product or all apparel content becomes invalid, or when unavailable stock remains in a purchase CTA.

## 8. GMV, leads, and store-visit distinction

Use the same apparel account and product facts with three valid but distinct paths: purchase, consultation, and store visit. Run three objective variants.

Pass when each creates a different customer decision problem, fulfillment check, task mix, and observation target. Fail when the system uses one generic “conversion” plan.

## 9. Market opportunity versus trend chasing

Provide:

- a strong category signal with poor account fit;
- a moderate scoped signal with strong account/product/path fit;
- a crowded topic with no positive demand signal;
- stale broad evidence.

Pass when the first is screened out or only observed, the second receives a reversible validation, the third is treated as homogeneity defense rather than opportunity, and the fourth cannot support a current claim.

### Negative probe

Fail if popularity alone authorizes production, if any external evidence becomes account causality, or if M3 writes the hook/creative mechanism.

## 10. Feedback local impact

Provide one exact publication with sufficient scoped feedback affecting a single hypothesis, plus unrelated cycle tasks.

Pass when the affected judgment changes locally and unrelated core decisions remain stable, allowing a small adjacent resource adjustment if its cost is explicit. Fail when the entire cycle is rewritten or nothing can change because “one item is never enough.”

Add conflicting/insufficient evidence. Pass when the Skill keeps the decision unchanged with an explicit reason and observation need.

## 11. Campaign overlay and return

Start with a current cycle baseline, apply a time-bounded Campaign to two named slots, change one uncovered baseline task legitimately during the Campaign, then expire it.

Pass when only named slots are occupied, uncovered slots remain M3-owned, and expiry returns to the current baseline without resurrecting the stale task.

## 12. Column shrink, pause, and exit

Provide three variants:

- high historic frequency but no current promise/dependence;
- an unclosed public forward promise;
- current column-specific audience reliance and a valid business path.

Pass when history alone does not create permanence, transition effort is proportional, no recovery date is invented, and long-term identity conflicts return to Matrix rather than Founder for ordinary operations.

## 13. Legal direct entry

Give the user a complete existing script, then request production preparation; separately give a sufficiently complete single-content task directly to Content Brief.

Pass when M3 is skipped where it adds no decision, valid equivalent inputs are accepted, and downstream necessary semantics remain. Fail when the system forces Matrix→Campaign→M3→Brief or fabricates cycle fields for a direct task.

## 14. No-task outcome

Provide a candidate whose necessary product fact is unavailable, no lawful alternative promise exists, and the correct result is to wait.

Pass when the Skill emits defer/no-task with one blocking fact. Fail when it manufactures alternatives or a Brief task to fill the output schema.

## 15. Six-Skill professional preservation

Compare, on the same accepted task set:

- A: competent generic operating baseline or direct M3-only prompt;
- B: M3 candidate plus applicable method inheritance.

At M3 module level assess:

- objective fidelity;
- stage interpretation;
- content-mix logic;
- capacity trade-off;
- experiment discipline;
- feedback discipline;
- handoff usability;
- boundary preservation.

At M5 integration level, and only where applicable, assess:

- identity recognizability;
- creative difference;
- human specificity;
- narrative/empathy;
- shootability;
- conversion naturalness;
- factual discipline;
- final completion.

Allow NOT_APPLICABLE per content type. Use blind human comparison. Do not use model self-score.

## 16. Longitudinal run

Run at least one continuous fixture:

```text
diagnosis
→ cycle plan
→ several daily decisions
→ one Campaign overlay
→ publication/test feedback
→ review
→ next-cycle update or justified no-change
```

Pass only if state is carried through the defined data projection, evidence identities remain distinct, changes are local, and no step silently rewrites Matrix or downstream creative responsibility.

## 17. Claim ceilings

Successful fixtures may establish:

```text
M3_MODULE_SEMANTICS_VERIFIED
M3_PROFESSIONAL_VALUE_VALIDATED_ON_ACCEPTANCE_SET
ENGINEERING_VERTICAL_SLICE_VERIFIED
```

Only when each definition’s evidence is independently met. They do not establish:

```text
REAL_OPERATION_LOOP_VERIFIED
CAUSAL_BUSINESS_LIFT_PROVEN
UNIVERSAL_SUPERIORITY
```

