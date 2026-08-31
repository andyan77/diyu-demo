# FAILURE TRIAGE · Executor preflight binding

task_id: `DIYU-V1-UNIFIED-DIFY-APPLICATION-001`

observed_failure:
`UAPP-EQUIV-01b` 的 `--run` 在发起 HTTP / 模型调用前退出；Runner 仍调用 v1.2 模块内的 preflight，并拒绝 v2.3 Gate 身份。

frozen_target:
使用 Gate v2.3、Scenario v1.2、Checker v1.1 和相同 UAPP 候选，对 EQUIV-01b 运行一次。

candidate_sources:

- `INPUT_ENVIRONMENT_OR_TOOL`

confirmed_origin: `INPUT_ENVIRONMENT_OR_TOOL`

evidence:

- 退出码 1，异常为 `Unexpected W1 successor Gate`。
- EQUIV-01b successor RAW 与 Check 均不存在。
- 活动运行仍为 0；没有 HTTP 响应、模型输出、状态写入或业务副作用。
- v1.3 的独立 `--preflight` 已通过全部 12 项硬门，错误仅发生在 Runner 内部的函数绑定。

mutation_target:
版本化 Executor 的 Runner preflight 函数绑定，以及由新 Executor 哈希直接引起的 Gate 绑定。

protected_targets:
冻结输入、业务判据、Checker v1.1、UAPP 候选及所有受保护应用、历史证据和数据。

next_reverification:
零模型复核 v2.4 绑定与 EQUIV-01b preflight；通过后执行原冻结输入一次。

model_calls_before_failure:
本次 0；累计保持 4 个顶层正式运行、15 次 LLM 节点尝试。

side_effects: none

