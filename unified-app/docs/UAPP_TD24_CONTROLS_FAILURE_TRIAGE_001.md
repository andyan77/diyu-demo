# FAILURE TRIAGE · TD24 控制 A-02 负例被合法兜底遮蔽

`task_id: DIYU-V1-UNIFIED-DIFY-APPLICATION-001`

`failed_control: UAPP_TD24_CONTROLS_v1.0 / A-02`
`model_calls: 0`

## observed_failure

确定性控制首次运行结果为 `10/11 PASS`。A-02 正例通过，但把 `source_quote` 单变量改成无效值后，整条用户输入仍含完整“从一人改为两人”结构，候选的确定性原话兜底据此合法形成 delta，所以负例没有翻转。

## frozen_target

A-02 要证明“模型纠正提议只有在逐字用户证据成立时才能升级为用户确认值”。负例应只破坏提议的逐字证据，同时不能被另一条独立、合法的确定性提取路径重新证明同一事实。

## candidate_sources

- `CONTRACT_OR_INTENT`：未发现问题。
- `ORACLE_OR_CRITERION`：A-02 目标本身有效。
- `CHECKER_OR_FIXTURE`：确认成立；负例输入同时满足另一条合法提取路径，未隔离单变量。
- `INPUT_ENVIRONMENT_OR_TOOL`：未发现问题；纯内存代码节点执行。
- `SYSTEM_UNDER_TEST`：未确认失效；正式原话路径及 A-02 正例都通过。
- `INSUFFICIENT_EVIDENCE`：不成立。

## confirmed_origin

`CHECKER_OR_FIXTURE`。

## evidence

- `unified-app/evidence/stages/uapp_td24/UAPP_TD24_CONTROLS_v1.0.json`
- summary: `10/11 PASS`
- A-02 positive: `pass=true`
- A-02 negative: mutated `source_quote`, observed `correction_status=APPLIED`
- 原因复算：负例仍保留 `把制作规模从一人改为两人`，命中 `EXPLICIT_CHANGE` 的独立确定性兜底。

## mutation_target

只版本化修正 A-02 的负例夹具：使用仍含明确修改关系、可支持正例提议、但不命中 `从…改为…` 兜底形态的等价原话；随后只改单变量 `source_quote`。不修改候选实现、Builder、旧 v1.0 控制或旧证据。

## protected_targets

UAPP candidate、纠正/选择/字段/血缘实现、M1/M2/M3、Hop、Seam、PP、六能力、旧 v1.0 控制及证据、Dify、M2、main 均不得修改。

## next_reverification

新建 `UAPP_TD24_CONTROLS_v1.1.py`，重跑全部 11 项正例与单变量负例；A-02 使用隔离后的负例，同时复跑原始正式失败形态 B-01 和全部保护面检查。

## side_effects

无 Dify/M2 写入，无模型调用。仅新增本地控制证据；候选尚未写 Dify draft。
