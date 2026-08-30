# UAPP S5 Bounded Convergence Checkpoint v1.0

`task_id: DIYU-V1-UNIFIED-DIFY-APPLICATION-001`

`recorded_at: 2026-08-30T13:52:49-07:00`

`next_state: FOUNDER_BUDGET_REBASE_REQUIRED`

## 结论

当前 S5 技术验收尚未完成。CAP-01～04 已在 Gate v1.4 下取得有效正式
`PASS / CURRENT`，但继续完成其余 15 个冻结输入至少需要把本 Active Work Package 的
顶层运行总数从当前 6 次增加到 21 次，超过冻结上限 20 次。

该事实在 CAP-05 调用前即可确定，因此未启动 CAP-05，也未为消耗预算而继续运行。
这不是新的产品失败，不降低已经取得的 CAP-01～04 结论。

## 当前绑定

- Gate v1.4 sha256: `a5660c3c3d7d9a6d26b6d39dab6df28d510f3f103ff0d1f4744a3ceaf8d601e5`
- scenarios v1.1 sha256: `896c5b0240f1e9c828889e38f7bad643bf523a451d5e3257318e70f54bf7c577`
- UAPP graph md5: `02610a77c3ce86f46f7a80de6d47ac2e`
- UAPP graph canonical sha256: `726b1d196717bb4e68b43fe9e6a3b9b85734a5db4611cf4d10bac19ee213dad5`
- PP/provider: `8366328bf827bd0f460455d750d45c4f`
- Seam: `db49a3da8973d4fdcbe9ecf63bdf7e2a`
- Hop: `e38378c3c2a66b75aa7e645368c9e1ce`
- M3: `cd93757bcf8ad322f3b32fc43b2da3ff`

## 已确认最高失效节点与处理

1. UAPP 投影接缝遗漏用户原话已支持的 `applicability_reason`：已通过一个最小 SUT 修复节点关闭；发布后确定性控制 `10/10 PASS`。
2. Checker 将专业能力最小可执行 smoke 错误绑定为每能力必须产生 M2 artifact/content_version：已使用本 Prompt 唯一一次 post-result Checker rebase 关闭；判别力控制 `7/7 PASS`。
3. 当前没有新的已确认 SUT、Checker、Fixture 或环境失败；唯一阻断是冻结预算不足以容纳剩余正式输入。

## 正式证据保留

| 场景 | run_id | 唯一能力 | artifact length | artifact sha256 | 结果 |
|---|---|---|---:|---|---|
| UAPP-CAP-01 | `23d56cf5-1aba-416b-a2ce-da33166126a8` | MATRIX | 2473 | `0c78a39684cd76cf5a58f64dfdbf88f6cc1a154b6c3b7dc4545b0de8cca9b3e0` | PASS / CURRENT |
| UAPP-CAP-02 | `77aae6ad-817f-4a15-ac8a-d01c6f35dabe` | CAMPAIGN | 8250 | `4ac7c0fc4880f97b06e35a97b6a4763ab7630067dfa29952ad8471807b736ae6` | PASS / CURRENT |
| UAPP-CAP-03 | `670ec687-d216-4c6e-b15d-a83eed7abd4a` | CONTENT_BRIEF | 4727 | `a30d8614c6f06560edd680fa527acca237b85d8ddea96ce2b7d21a4f832e1b78` | PASS / CURRENT |
| UAPP-CAP-04 | `9a5f8aee-0594-4f19-82af-d1e41541efc7` | CREATIVE_SCRIPT | 4584 | `6dbf6f7997ba0ab93ea10346bd99c06c9dfb4a18f229d3fb6a074d02cc370911` | PASS / CURRENT |

四个正式场景均为其他五能力零暗跑、失败节点 0、平台内部重放 0、真实发布 0。

CAP-05 零模型预检 PASS：活动 workflow 为 0，候选图、Provider、Runner、Gate、输入哈希、
M2 schema 与非测试计数均与冻结值一致；本次只执行预检，没有创建 RAW 或 run。

## 成本与下界证明

```text
actual_top_level_runs                 = 6
frozen_top_level_runs_max             = 20
actual_llm_node_attempts              = 34
frozen_llm_node_attempts_max          = 120
valid_formal_scenarios                = 4
remaining_frozen_scenarios            = 15
minimum_additional_top_level_runs      = 15
minimum_final_top_level_runs           = 6 + 15 = 21
budget_gate                            = 21 > 20
```

LLM 的最坏静态上界同样不足：当前 34 次，加上 15 个剩余输入各自最多 6 次为 124，
高于冻结上限 120。即使某些场景实际低于 6 次，顶层运行上限仍然确定不足。

## 已尝试的实质不同路径

- 保留首次 SUT 失败 Attempt，并在独立证据确认后修复 UAPP 自身最高失效接缝。
- 保留 Checker 不合合同的 Attempt，并完成唯一一次版本化 Checker rebase。
- 对修复后的候选逐项运行 CAP-01～04，均取得真实正式结果。
- 未使用 A/B、重复采样、Reviewer、盲重跑或结果驱动改写输入。

## 保留状态

- CAP-01～04: `PASS / CURRENT`
- F2 / UAPP-AC-01..11 overall: `IN_PROGRESS / NOT_VERIFIED`
- Founder AC-12: `NOT_AUTHORIZED / NOT_VERIFIED`
- main merge: `NOT_ALLOWED`
- terminal_state: `unset`

## 推荐与唯一裁决问题

建议将本 Active Work Package 的上限版本化调整为：

```text
MAX_NEW_TOP_LEVEL_RUNS_TOTAL     = 22
MAX_NEW_LLM_NODE_ATTEMPTS_TOTAL = 130
```

理由：从当前状态完成 15 个剩余正式输入，顶层运行至少需总计 21 次；按每个剩余输入的
冻结静态上限分配，LLM 尝试额度需达到 124 次。`22 / 130` 额外仅容纳一次本 Prompt
已授权的 CAP-05 失败后最小修复复验，不改变样本、场景、判据、应用保护面或其他收敛上限。

Founder 只需裁决一个问题：是否批准把本 Active Work Package 的顶层运行 / LLM 尝试上限
版本化调整为 `22 / 130`，其余合同保持不变？
