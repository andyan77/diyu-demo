# FAILURE TRIAGE · EQUIV-01n physical-node overconstraint

task_id: `DIYU-V1-UNIFIED-DIFY-APPLICATION-001`

observed_failure:
EQUIV-01n 没有生成 artifact，只精确追问被删除的期望改变，且没有重复询问表达主体；旧 Checker 仍因 Content Brief 物理应用运行 1 次把 `EQUIV-N1` 判 FAIL。

frozen_target:
负例必须不生成成品，只询问 expected change，不询问已经存在的表达主体。现行 Gate 明确不冻结必须由哪个物理节点提问，也不以 Seam / 专业能力是否执行作为输入充分性的唯一依据。

candidate_sources:

- `ORACLE_OR_CRITERION`
- `CHECKER_OR_FIXTURE`

confirmed_origin: `CHECKER_OR_FIXTURE`

evidence:

- workflow run: `f3d3ac80-366b-4ef6-905f-57a54b689607`
- `artifacts=[]`、`content_versions=[]`，没有成品。
- 用户回复只问“看完之后，希望她多知道什么、或者能做什么决定”，并明确其他信息不用重复。
- `EQUIV-N2` 已 PASS；唯一失败的 `EQUIV-N1` 把“所有能力运行数为 0”与“不生成成品”错误合并。

mutation_target:
版本化 Checker 将 EQUIV-N1 恢复为冻结的业务谓词“无新 artifact / content version”，保留 EQUIV-N2 的精确问题与不重复主体判定。

protected_targets:
UAPP、M3、Hop、Seam、Content Brief、冻结输入、业务判据、历史 RAW 与旧 FAIL。

next_reverification:
运行正负判别控制；使用同一 RAW 重新裁定，不进行模型重跑。

model_calls_before_failure:
本包累计 7 个顶层正式运行、31 次 LLM 节点尝试；本次 1 个顶层运行、5 次 LLM 节点尝试。

side_effects:
仅测试域任务状态；无成品、无真实发布，保护计数保持 1568/117，schema 未变化。
