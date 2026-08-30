# FAILURE TRIAGE · S5 post-CAP06 GAP-01 wrong decisive gap

task_id: `DIYU-V1-UNIFIED-DIFY-APPLICATION-001`

observed_failure: `UAPP-GAP-01:G1` 对原冻结输入“这周想发点东西，你看着办吧。”返回了一个
自然、单一且未编造的追问，但所问的是“时间或阶段边界”。冻结的同会话下一轮 G2 只补充主推
商品、受众问题、期望改变和表达边界，不回答时间边界；因此 G1 的追问无法由冻结 G2 补齐，
`UAPP-AC-06` 的“补齐缺口后同会话继续”不成立。

frozen_target: 根合同要求关键商品/内容方向缺失时精确停下，不替用户挑选；Gate v1.9 继承
`UAPP-AC-06`，要求真实缺口轮在用户补齐该缺口后于同会话继续。G1/G2 原文及顺序均早于本次
运行冻结，Scenario v1.1 sha256 为
`896c5b0240f1e9c828889e38f7bad643bf523a451d5e3257318e70f54bf7c577`。

candidate_sources:

- `SYSTEM_UNDER_TEST`
- `CHECKER_OR_FIXTURE`

confirmed_origin: `SYSTEM_UNDER_TEST`，最高已确认失效接缝为 UAPP 的“模糊周期请求 → 决定性
缺口/能力选择”接缝。UAPP 将 G1 直接路由到 CAMPAIGN，并把 `decisive_question_text` 留空；
CAMPAIGN 的受保护充分性外壳按自己的输入合同优先选择 `deadline_or_stage_boundary`。这不是
冻结 G2 会补充的缺口。不得通过修改受保护的 CAMPAIGN、Seam 或后续交付文字掩盖该上游选择。

evidence:

- workflow run：`347272fd-df0f-4ddd-aaea-cf904f0e3236`，HTTP 200；
- RAW sha256：`19e2c25b0da620724ab58faaf39a0d00a5d618ca9744477b981f7b6edf6143ec`；
- Check sha256：`844d6302e529e4770461a5fc7ff3792eff2aa114a0f6e5c80cd4c6acca0dd91d`；
- `uapp_action.intent=CAMPAIGN`、`decisive_question_text=""`；
- `uapp_fields` 同时记录多个缺口；CAMPAIGN `component_return` 选择
  `deadline_or_stage_boundary`；
- 最终答复无内部泄漏、无 artifact、无其他五能力暗跑；
- G2 原文只补商品/内容方向等信息，不含截止时间或阶段边界；
- M2 非测试 publish/feedback 保持 `1568/117`，schema md5 保持
  `25192c11562827efedfc3b2c22c3b4fd`。

checker_scope_note: 当前 Checker 的 `GAP-01/GAP-02` 还要求必须走 `uapp_ask_one`、不得调用
Seam 或任何专业能力。根合同只冻结“精确停在缺口并能继续”，没有独立冻结“必须在哪个节点
提问”。这部分属于 `CHECKER_OR_FIXTURE` 过度编译，不能用来证明 SUT 失败，也不能在看到结果后
原地改绿。本次 SUT FAIL 只依据“所问缺口与冻结 G2 不相接”这一真实产品行为。

mutation_target: `NONE`。当前 CAP-06 REBASE 只授权 CAP-06 的平台/CTA/成片语义接缝以及其后
一次性运行剩余场景，不授权修改新的 GAP-01 路由/缺口产品行为。

protected_targets: M1、M2、M3、Hop、Seam、CAMPAIGN 及其专业合同、其他五项专业能力、PP、
数据库 schema、非测试数据、冻结 Scenario/Gate/Checker、历史 RAW、main。

next_reverification: Founder 若版本化授权最窄 GAP-01 后继，应先冻结“G1 必须问出 G2 能回答的
关键商品/内容方向缺口”的正负控制，再只运行 G1；G1 PASS 后才在同一会话运行一次原冻结 G2。

model_calls_before_failure: 顶层运行 `1`，DeepSeek 节点尝试 `5`。

side_effects: 无真实发布、无非测试数据变化、无 schema 变化、无重试、无内部重放、无 A/B、
无重复采样、无 Reviewer；后续 12 个冻结输入未运行。
