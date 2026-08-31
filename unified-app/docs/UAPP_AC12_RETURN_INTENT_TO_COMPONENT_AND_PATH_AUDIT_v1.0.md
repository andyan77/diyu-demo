# UAPP AC-12 RETURN · 意图到组件与路径审计 v1.0

`task_id: DIYU-V1-UNIFIED-DIFY-APPLICATION-001`

`scope: 只读既有 Founder AC-12 七个 Dify run 与 M2 测试域`

`新增 DeepSeek / Reviewer / 重跑: 0 / 0 / 0`

## 结论

Founder 的 `RETURN` 成立。两条失败均不是路由或组件不可达：二者都正确进入
`CONTENT_BRIEF`，且其他五个专业能力均未运行；组件也准确报告输入不足。

失败在语义交接：系统没有把用户已明确给出的“希望观众知道什么”作为
`content_promise` 交给 Content Brief。完整故事另有同层越权：M3 把用户的内容目标重写为
“促进购买决策”，Hop、状态和交付又错误宣称该目标由用户确定。

## 逐跳字段血缘

| 步骤 | YAML-like 内容依据 | GAP G2 补充方向 |
|---|---|---|
| S1 用户原话 | PASS：明确“希望她看完明白……三天不重样” | PASS：明确“想让她知道怎么把一件外套穿得更精神” |
| S2 M1 编译与来源 | PASS：`evidence_bundle.ev_001` 保留原文，`provenance=USER_DIRECT` | PASS：`evidence_bundle.ev_001` 保留本轮原文，`provenance=USER_DIRECT` |
| S3 canonical state | PASS：原文在 `snapshot_json`，但没有独立 `expected_change/content_promise` 字段 | PASS：原文在 `snapshot_json`，但没有独立 `expected_change/content_promise` 字段 |
| S4 下一轮读取 | NOT_APPLICABLE：YAML 是单轮 | PASS：G2 原文进入 M3；G1 的“方向分叉”没有造成这次缺失 |
| S5 Hop 映射 | FAIL：有 `expected_change`，无 `content_promise` | FAIL：`expected_change` 与 `content_promise` 都没有进入 capability call |
| S6 Seam 调用 | DEPENDENT FAIL：完整转交了缺少 promise 的合同 | DEPENDENT FAIL：完整转交了缺少 promise 的合同 |
| S7 Content Brief 消费 | PASS（可达）/ DEPENDENT FAIL（充分性）：准确返回 `content_promise` 缺口 | PASS（可达）/ DEPENDENT FAIL（充分性）：准确返回 `expected_change；content_promise` 缺口 |
| S8 用户交付 | FAIL：重复要求已给出的承诺 | FAIL：重复要求已给出的“看完知道什么” |
| S9 未授权商业目标 | NOT_APPLICABLE | NOT_APPLICABLE |

### 首次失效节点

两个重复追问的共同首次失效节点是 `uapp_hop` 的能力合同投影：它没有把已由用户直接提供、
并由 M1 快照保留的语义，映射为 Content Brief 消费的 `content_promise`。`uapp_fields`、
Seam 与 Content Brief 的失败均是这一缺失的后续级联，不建立第二个根因。

完整故事 T1 的越权首次出现在 `uapp_m3` 输出：M1 的 `goal_structure.primary_goal` 是用户的
观众结果；M3 将它改写为“促进购买决策”，并称“我按……来定”。随后 Hop 将该值带入
`primary_goal`，`uapp_fields` 又标为 `USER_UTTERANCE` 且回指 M1，形成错误来源归属。

## 分层归因

| 分类 | 裁决 | 依据 |
|---|---|---|
| INTENT_CLASSIFICATION | PASS / CURRENT | YAML、FULL T1、GAP G2 都识别为 `CONTENT_BRIEF`；写回三轮分别识别正确动作 |
| ROUTING | PASS / CURRENT | 目标能力与 route mode 正确；G1 是唯一自然语言问题出口 |
| COMPONENT_REACHABILITY | PASS / CURRENT | Content Brief 在三次相关 run 中真实执行；不相关五能力为零 |
| SEMANTIC_HANDOFF / SUFFICIENCY | FAIL / CURRENT | Hop 缺失内容承诺；组件的缺口回执由此触发 |
| AUTHORITY_ESCALATION | FAIL / CURRENT | FULL T1 的购买目标未由用户确认，却被写成用户来源 |
| WRITEBACK | PASS / CURRENT | T2/T3/T4 的 M2 行、关联与周期转换均已只读回查 |

## 写回只读核验

FULL T2 的 `aca7e5bd-930a-464a-8255-2b9ceb5ce7d9` 是唯一测试/模拟发布记录，绑定当前
Content Brief 版本；T3 的 `a2b3578e-e000-4739-b696-606d6a2ad189` 绑定该发布；T4 将旧周期
`83438b80-5cd9-46a9-86ab-0e7d0d9ee478` 置为非当前，并建立唯一当前后继周期
`5a0564c3-b5cb-46b7-9efc-689e1aa65594`。没有真实发布，非测试发布/反馈保护计数为 `0/0`。

## 最小修复对象与保护面

下一次修复只能定位到 UAPP 的语义边界：

1. `M1 snapshot/user original → uapp_hop` 的用户来源内容承诺投影；
2. `uapp_m3 → uapp_hop` 的主目标来源校验，禁止把推断的商业目标标为用户确认；
3. `uapp_fields` 的来源与等级守卫，拒绝与 M1 原始值不一致的 `USER_UTTERANCE` 回指。

不得修改已经通过的 `uapp_action` 意图分诊、`uapp_route` 路由、Provider 绑定、Seam、
Content Brief 或其他专业能力。M3 本体也不在本次审计授权内；若后继认为必须修改它，需要先
证明 UAPP 语义边界无法以来源锁定与 fail-closed 闭合。

原始 run、节点执行、M2 行及旧证据均保持原样；逐场景证据见
`UAPP_AC12_RETURN_ROUTE_MATRIX_v1.0.json` 与 `UAPP_AC12_RETURN_M2_WRITEBACK_READBACK_v1.0.json`。
