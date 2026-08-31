# UAPP S5 双阻断有界收敛 Prompt v1.0 · ERRATA 001

```yaml
authority_event: FOUNDER_S5_FULL_CHAIN_WRITEBACK_SCOPE_CONFIRMATION_001
applies_to: UAPP_S5_FINAL_TWO_BLOCKER_BOUNDED_CONVERGENCE_REBASE_EXECUTION_PROMPT_v1.0
task_id: DIYU-V1-UNIFIED-DIFY-APPLICATION-001
task_entry_mode: REBASE_TASK_CONTINUATION
errata_nature: AUTHORIZATION_SCOPE_CORRECTION
new_product_semantics: NONE
acceptance_change: NONE
frozen_input_change: NONE
model_budget_change: NONE
```

## Founder 裁决

原始授权目标包含完整测试闭环：内容成果 → 测试发布登记 → 测试反馈登记 → 当前周期结束 →
下一周期开启 → 重复反馈幂等恢复。上一版 `allowed_delta` 遗漏了完成冻结 FULL/RECOVERY 链所需的
两个执行面。本 Errata 明确把以下 UAPP 最小写回接缝纳入同一个 Active Work Package：

- `REGISTER_FEEDBACK`
- `CLOSE_CYCLE / OPEN_NEXT_CYCLE`

这不是新增 P0、产品规则或独立任务；原任务、冻结输入、验收和预算保持不变。

## 修正后的完整允许修改范围

1. `RECORD_PUBLISH`：当前已接受内容 → M2 测试发布记录；
2. `REGISTER_FEEDBACK`：用户反馈 → 当前测试发布记录 → M2 测试/模拟反馈记录；
3. `CLOSE_CYCLE`：用户明确结束当前周期 → 当前周期合法收口；
4. `OPEN_NEXT_CYCLE`：当前周期合法结束 → 建立下一周期最小可恢复状态；
5. `RECOVERY / IDEMPOTENCY`：同一反馈、发布或周期动作重复提交时不重复写入，不破坏已有状态。

执行侧可自主决定 UAPP 节点与接线、确定性选择器、现有 M2 API 调用、幂等键、测试身份、候选
发布/回退、零模型控制和必要局部重构。这些技术 HOW 不再上推 Founder。

## 仍然禁止

- 修改 M2 schema、绕过 M2 API 直接写库或修改非测试数据；
- 真实发布或调用真实平台；
- 修改 M1、M3、Hop、Seam、六项专业能力或 PP 专业语义；
- 改写冻结 FULL/RECOVERY 输入或验收标准；
- 新增第二状态层、数据库或运行时；
- 清理历史 RAW/FAIL；
- 合并 main。

所有新增发布和反馈记录必须 `is_test=true`、`is_simulated=true`、`real_publish=false`。非测试保护
计数保持 publish `1568`、feedback `117`。

## 继续与停止

从现有 P1 Checkpoint 继续，不重做 P0：P1 → P2 → P3 → P4 → P5 → Founder AC-12 交接包。
普通实现、Runner/Fixture/Checker、节点接线、API 使用或换路问题不得再上推 Founder。只有产品语义、
冻结验收、M2 schema、非测试数据、真实外部动作、M2 API 无法承载模块责任或权威真源冲突才可升级。

若候选版本、路径或硬预算耗尽仍失败，直接交付：

```text
S5_TECHNICAL_ACCEPTANCE = FAIL / CURRENT
FOUNDER_AC_12 = NOT_AUTHORIZED
```

## 预算（不变）

```yaml
planned_top_level_workflow_runs: 9
top_level_workflow_runs_hard_cap: 10
deepseek_llm_node_attempts_hard_cap: 60
candidate_publication_versions_hard_cap: 2
manual_retry_hard_cap: 1
platform_internal_replay_plus_manual_retry_hard_cap: 1
repeat_sampling: 0
ab_tests: 0
reviewer_calls: 0
```

第 10 个顶层槽位只用于符合原条件的纯传输替补，不用于 Runner、Fixture 或 Checker 错误。

## P1 追加硬门

- 已经发布 + 合法当前内容 → 一条测试发布；准备发布或无合法内容 → 零发布；
- 合法测试发布 + 反馈 → 一条测试反馈；无发布 → 精确缺口；重复同一反馈 → 不增加；
- 当前周期可关闭 → 关闭并建立下一周期；重复关闭 → 不重复建周期；前置不足 → fail-closed。

全部控制通过后才允许 DeepSeek 调用。

## 完成标准

EQUIV a/b/c/n、FULL T1/T2/T3/T4、RECOVERY R1 全部 `PASS / CURRENT`，其他十项保持有效
CURRENT，UAPP-AC-01..11 全部 `PASS / CURRENT`，非测试保护 `1568/117`，schema、保护模块无漂移，
真实发布为 0。成功后只上调 S5 技术验收并准备 Founder AC-12；main 不合并，terminal_state unset。

`END OF ERRATA 001`
