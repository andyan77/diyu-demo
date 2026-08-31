# UAPP S5 Failure Triage 003 · EQUIV negative fixture is not single-variable

## FAILURE TRIAGE

- `observed_failure`: EQUIV-01n 只运行 CONTENT_BRIEF 并精确询问表达主体，但冻结 Checker 要求
  Seam 不执行、专业能力全为 0，且问题必须包含“希望/看完/明白/改变/期望”。
- `frozen_target`: 真实缺项负例应只定位被删除的 expected change，不编造产物。
- `candidate_sources`: `CHECKER_OR_FIXTURE`, `SYSTEM_UNDER_TEST`。
- `confirmed_origin`: `CHECKER_OR_FIXTURE`。EQUIV-01n 不只删除 expected change；与能力合同对照，
  它也没有 expression subject。目标系统询问的是另一个真实缺口，故该 Fixture 不能唯一判别
  expected change。Checker 的“必须在 Seam 前停”是实现位置命题，不是自然产品结果本身。
- `evidence`: run `b9bb4797-0d0f-4a20-bc11-a03bd43766b1`；CONTENT_BRIEF `1`、其余五能力 `0`；
  answer 仅一问；artifact `0`；LLM `5`；重试/重放/非测试变化 `0`。
- `mutation_target`: `NONE`。输入、Checker、候选和能力合同均受当前冻结保护。
- `protected_targets`: 全部 SUT、Scenario、Gate、Checker、历史 RAW、main。
- `next_reverification`: 等价表达组保持 NOT_VERIFIED(ORACLE_OR_CRITERION)；继续独立 WITHDRAW、
  FULL、RECOVERY 冻结场景。
- `model_calls_before_failure`: 累计顶层 `6`，DeepSeek 节点 `25`。
- `side_effects`: 仅测试作用域；真实发布/非测试变化/重试/重放均 `0`。

