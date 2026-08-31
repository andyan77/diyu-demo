# FAILURE TRIAGE · EQUIV-01a checker field schema

task_id: `DIYU-V1-UNIFIED-DIFY-APPLICATION-001`

observed_failure:
`UAPP-EQUIV-01a` 的真实运行只调用了 Content Brief，并生成 3536 字非占位产物；旧 Checker 的 `EQUIV-P3` 却把表达主体和期望改变都读成空值。

frozen_target:
三种等价正例必须把同义的表达主体和期望改变带入规范任务字段，并真实生成 Content Brief。业务判据不要求特定内部字段编码。

candidate_sources:

- `CHECKER_OR_FIXTURE`
- `SYSTEM_UNDER_TEST`

confirmed_origin: `CHECKER_OR_FIXTURE`

evidence:

- workflow run: `fb0c71a3-30d7-45ac-9a3b-a0ad36220790`
- `uapp_fields.pending_state_json.fields` 中，`expression.subject_and_boundary.v` 包含“品牌搭配师”，`audience.expected_change.v` 包含“三天不重样”。
- Content Brief 成品中逐字保留表达主体和期望改变，artifact sha256 为 `56ac6910924a32194ef6aab7b1b4a8f00c68d2054f574c53acd9da9d9d518464`。
- 旧 Checker 的 `field_value` 只读取 `value` / `value_text`，未读取当前 UAPP 规范字段载体实际使用的 `v`。
- 因此失败发生在证据解码层；当前证据不支持修改 UAPP 或专业能力。

mutation_target:
版本化 Checker 的字段值解码薄适配，以及由新 Checker 哈希直接引起的 Gate / Executor 绑定。

protected_targets:
UAPP 候选图、M1/M2/M3、Hop、Seam、六项专业能力、PP/provider、冻结自然语言、业务判据、历史 RAW 与历史 FAIL。

next_reverification:
先用正例及单变量负例证明新解码器能区分 `v`、缺失和错误值；再用同一已冻结 RAW 重新裁定 EQUIV-01a。不得重跑模型。

model_calls_before_failure:
本包累计 4 个顶层运行、15 次 LLM 节点尝试；本次 EQUIV-01a 为 1 个顶层运行、6 次 LLM 节点尝试。

side_effects:
仅测试域任务状态与 Content Brief artifact；非测试 publish/feedback 保护计数仍为 1568/117，schema 未变化，无真实发布。
