# UAPP S5 Inline Artifact Seam — Unified Failure Triage v1.0

`task_id: DIYU-V1-UNIFIED-DIFY-APPLICATION-001`

`task_entry_mode: REBASE_TASK`

`model_calls_before_triage: 0`

## FAILURE TRIAGE

```yaml
observed_failure: >
  两次 CAP-05 RAW 形成一条连续失效链。首次运行把空会话且无纠正信号误判为任务身份冲突；
  修复该上游分支后，第二次运行把用户本轮所说的目标 Production Director 误当成它自己的
  上游产物能力。用户原文中的完整确认脚本只进入 Hop 模型投影，且被投到
  content_body_or_beats；selector 没有 current-turn inline artifact 来源，fields 又只接受历史
  accepted ledger，因此调用前绑定被拒绝，Seam 与专业能力未运行，停支回复还泄露内部枚举。
frozen_target: >
  用户本轮直接提供完整、明确确认可用、类型与目标能力兼容的产物时，UAPP 必须在当前 task
  和当前轮内绑定原文及可复算身份，调用目标专业能力；不自动接受或持久化为历史产物。
  不完整、歧义、跨 task、错误类型、STALE 或摘要/hash 不一致时必须 fail-closed；用户回复
  不得出现内部能力名、字段名或状态码。
candidate_sources:
  - CONTRACT_OR_INTENT
  - ORACLE_OR_CRITERION
  - CHECKER_OR_FIXTURE
  - INPUT_ENVIRONMENT_OR_TOOL
  - SYSTEM_UNDER_TEST
  - INSUFFICIENT_EVIDENCE
confirmed_origin: SYSTEM_UNDER_TEST
evidence:
  - Gate v1.5 RAW run 45c783b7-b7fc-47fa-80c0-639ce843ee55
  - Gate v1.6 RAW run cbabab77-bbb3-4f07-a655-83d61bbd9b62
  - v1.5 correction=REJECTED/TASK_IDENTITY_MISMATCH
  - v1.6 correction=NONE/NEW_TASK_NO_CORRECTION
  - v1.6 selector=NAMED_UPSTREAM_INCOMPATIBLE
  - v1.6 Hop extraction_gaps includes script_or_equivalent_beats while the script appears as content_body_or_beats
  - v1.6 fields=REJECTED; binding reason SELECTOR_NOT_SELECTED; Seam=0; Production Director=0
  - v1.6 block answer contains the literal internal identifier PRODUCTION_DIRECTOR
mutation_target: >
  One complete UAPP-owned seam package: current-turn inline artifact source classification and normalization,
  selector precedence and compatibility, fields binding verification/injection, pre-Seam eligibility, and
  blocked/delivered user-text scrubbing.
protected_targets:
  - M1 / M2 / M3
  - Hop / Seam
  - six professional capability applications and PP b2 body/provider
  - M2 schema and non-test data
  - frozen Scenario v1.1 and UAPP-AC-01..11 meaning
  - historical Gate, RAW, Result, Triage and workflow rows
  - main / origin/main
next_reverification: >
  Run the frozen full-seam deterministic positive, single-variable negative and carrier-equivalence controls.
  Only after 100% PASS, bind and publish a successor candidate and execute CAP-05 once.
```

## 最高失效接缝

最高失效点不是 M3、Hop、Seam 或 Production Director，而是 UAPP 自己缺少“当前轮用户直接
提供的完整合法产物”这一来源类型。其后 selector、fields 与停支交付都建立在“只能从历史 accepted
ledger 取正文”的旧假设上，因此必须作为一条完整接缝修复，不能只改单个字符串判断。

## 冻结实现边界

- inline artifact 只对当前 task、当前 turn、当前调用有效；不自动写成 `accepted=true`，不加入历史产物账本。
- 原文、类型、来源、task scope、fp/bfp 必须一起绑定；目标能力永远不能成为自身上游。
- 历史 accepted / STALE / task / capability / fp / bfp 的 fail-closed 规则必须原样保留。
- Hop 仍只处理普通字段；其摘要或改写不得成为 inline artifact 正文身份。
- 不完整或歧义输入只问一个自然语言缺口；任何内部枚举、字段名或状态码都不得交给用户。
