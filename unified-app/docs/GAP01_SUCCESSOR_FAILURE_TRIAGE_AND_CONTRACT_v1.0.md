# GAP-01 successor failure triage and interface contract v1.0

task_id: `DIYU-V1-UNIFIED-DIFY-APPLICATION-001`

## FAILURE TRIAGE

observed_failure: 冻结 G1 表达“这周想发点东西”并把选择交给系统。UAPP 直接锁定 CAMPAIGN，
`decisive_question_text` 为空；CAMPAIGN 外壳按自身合同追问时间/阶段边界。冻结 G2 提供商品、
受众问题、期望改变和表达边界，不提供截止时间，因此两轮不能连续。

frozen_target: 只问一个会改变路线或产品结果的问题；问题可由冻结 G2 自然回答；不得替用户选择
商品、内容方向或整体 Campaign。Checker 不冻结物理提问节点，也不因某能力运行单独判失败。

candidate_sources: `SYSTEM_UNDER_TEST`、`CHECKER_OR_FIXTURE`。

confirmed_origin: `SYSTEM_UNDER_TEST` 的 UAPP 能力选择前决定性分叉接缝；旧 Checker 另有
`CHECKER_OR_FIXTURE` 过度编译，但不是本次 SUT FAIL 的依据。

evidence: run `347272fd-df0f-4ddd-aaea-cf904f0e3236`；RAW sha256
`19e2c25b0da620724ab58faaf39a0d00a5d618ca9744477b981f7b6edf6143ec`；旧 Check sha256
`844d6302e529e4770461a5fc7ff3792eff2aa114a0f6e5c80cd4c6acca0dd91d`。

mutation_target: UAPP `uapp_action` 的能力选择语义与 `uapp_route` 的决定性问题薄适配。

protected_targets: M1/M2/M3、Hop、Seam、CAMPAIGN 与其他专业应用、PP、CAP-06 接缝、数据库
schema、非测试数据、历史 RAW/Gate/Checker、main。

next_reverification: 先通过原句、等价表达、明确 Campaign、明确单条内容、两问、错误缺口及
CAP-01～06 路由等价控制；再使用冻结 G1/G2 各一次真实运行。

## 接口合同

- 模糊内容委托只有在“整体周期安排”和“具体商品/内容方向”会产生不同结果时才问一个分叉。
- 时间词“这周”不能独立授权整体 Campaign，也不能把截止时间排在商品/方向之前。
- 明确整周排期/节奏继续进入 CAMPAIGN；明确商品或题目继续进入适用内容能力。
- G2 是对“具体商品/内容方向”分支的有效回答；同会话继续，不重复 G1。
- 产品验收只看真实问题语义与连续性；不冻结 `uapp_ask_one`、Seam 或其他物理节点位置。

## 零模型结果

- predecessor replay：5/5 事实检查 PASS；
- successor 正负与影响面控制：30/30 PASS；
- CAP-01～06 逐项通过受影响路由函数前后输出等价；
- 候选只改 `uapp_action`、`uapp_route`，其余 54 个节点和全部 58 条边不变；
- candidate canonical sha256：
  `65f46389f8f1a1334050427acee5788769f9032342e4423ec03878af4b59bcf2`。
