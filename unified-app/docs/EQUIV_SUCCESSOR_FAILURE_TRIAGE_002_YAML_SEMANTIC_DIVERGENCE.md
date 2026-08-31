# FAILURE TRIAGE · EQUIV-01b YAML-like semantic divergence

task_id: `DIYU-V1-UNIFIED-DIFY-APPLICATION-001`

observed_failure:
YAML-like 正例只运行 Content Brief 路径，但 M3 将经营主目标判为缺失；随后 Hop / UAPP fields 同时缺少 `objective.primary_goal`、`content.promise` 与 `objective.goal_family`，因此没有生成 Content Brief artifact。

frozen_target:
EQUIV-01a/b/c 的业务语义相同，只改变普通自然语言、YAML-like 和 JSON-like 表达形式；三者都应生成可用 Content Brief。不得以工作流成功代替成品。

candidate_sources:

- `SYSTEM_UNDER_TEST`
- `ORACLE_OR_CRITERION`

confirmed_origin: `SYSTEM_UNDER_TEST`

evidence:

- workflow run: `c4a7cd78-8da0-4f97-b5a1-5beb89100041`
- 路由为 `CONTENT_BRIEF`，Content Brief 专业应用运行 1 次，其他能力 0 次。
- M3 实际回复要求用户补“这一周的主目标”；Hop `extracted_json` 对 `primary_goal`、`goal_family`、`content_promise` 均为空。
- `uapp_fields.gaps_text = objective.primary_goal；content_promise；objective.goal_family`，artifact 长度为 0。
- 同业务语义的 plain 正例 run `fb0c71a3-30d7-45ac-9a3b-a0ad36220790` 已生成 3536 字 Content Brief；两者差异首先出现在 M3 对等价表达的业务语义判断，而非 Checker。
- 新 Checker 已正确读取 canonical `v` 字段；本次失败不是前一项 Checker schema 问题。

mutation_target: `NONE`

protected_targets:
M3、Hop、Seam、Content Brief 专业能力、冻结输入和业务判据均受当前 REBASE 保护，不得修改；UAPP 不得在下游伪造经营目标来掩盖上游差异。

next_reverification:
不重跑 EQUIV-01b。继续执行不依赖该失败的 EQUIV-01c、EQUIV-01n、FULL 与 RECOVERY，确定失效范围；S5 保持 FAIL / NOT COMPLETE，除非后续权威授权允许修复已确认的受保护语义节点。

model_calls_before_failure:
本包累计 5 个顶层正式运行、20 次 LLM 节点尝试；本次 1 个顶层运行、5 次 LLM 节点尝试。

side_effects:
仅测试域任务状态；无 artifact、无真实发布。非测试 publish/feedback 保护计数为 1568/117，schema 未变化。
