# UAPP S5 Failure Triage 002 · EQUIV positive fixture insufficiency

- `task_id`: `DIYU-V1-UNIFIED-DIFY-APPLICATION-001`
- `attempt`: `f033b774-f343-4070-acdb-6e350346b9e1`
- `mutation_status`: `NONE_AT_TRIAGE_TIME`

## FAILURE TRIAGE

- `observed_failure`: EQUIV-01a 正确路由并只运行 CONTENT_BRIEF，Seam 返回一个精确缺口，未生成
  artifact；冻结 Checker 的正例产物硬门 FAIL。
- `frozen_target`: 普通自然语言、条列、JSON 三种等价正例应形成相同的合法 CONTENT_BRIEF 成品；
  真实缺项负例应精确询问。
- `candidate_sources`: `CHECKER_OR_FIXTURE`, `SYSTEM_UNDER_TEST`。
- `confirmed_origin`: `CHECKER_OR_FIXTURE`。EQUIV-01a 原文给出了受众、问题、期望改变、表达边界、
  商品和库存，但没有说明“由谁表达”；当前 CONTENT_BRIEF 合同要求
  `expression_subject_and_boundary`。真实节点只询问“这条由谁来讲？她能讲的和不能讲的边界是什么？”，
  没有编造主体。CAP-03 正例则明确包含“由品牌搭配师真实出镜”，二者并非等价充分输入。
- `evidence`: run `f033b774-f343-4070-acdb-6e350346b9e1`；UAPP route `CONTENT_BRIEF`；
  CONTENT_BRIEF runs `1`、其他五能力 `0`；`uapp_fields.gaps_text=expression_subject_and_boundary`；
  Seam `COMPONENT_RETURN`；artifact 为空；LLM `5`；非测试计数/schema/图零漂移。
- `mutation_target`: 不修改 SUT、场景、Checker 或能力合同。只版本化修复 Runner 的全局
  `all_prior_pass` 过度阻断，使与本失败无依赖的冻结场景仍可一次性运行。
- `protected_targets`: UAPP 候选、M1/M2/M3、Hop、Seam、六能力、PP、Scenario v1.1、业务 Checker、
  EQUIV-01a RAW/FAIL、main。
- `next_reverification`: EQUIV-01b/01c 因同一 fixture 缺口置 NOT_RUN_DEPENDENT；EQUIV-01n、
  WITHDRAW、FULL、RECOVERY 按各自 conversation 依赖继续，输入和判据不变。
- `model_calls_before_failure`: 本 Prompt 累计顶层 `5`，DeepSeek 节点 `20`。
- `side_effects`: 测试作用域 bootstrap；真实发布 `0`，非测试变化 `0`，重试/重放 `0`。

