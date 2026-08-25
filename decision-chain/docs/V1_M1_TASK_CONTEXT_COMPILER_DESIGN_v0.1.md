# M1 任务上下文编译器 · 设计 v0.1

`task_id: DIYU-V1-M1-NATURAL-CONTEXT-001`

本文件是 M1 的工程设计文档，不是新合同。物理字段、Schema、代码组织由本设计自由决定；业务语义边界由以下真源冻结，本设计不得与其冲突：

- `decision-chain/docs/V1_M0_SHARED_CONTRACT_TASK_CONTEXT_SNAPSHOT_v0.1.md`（14 条快照语义 + 5 个正交维度）
- `decision-chain/docs/V1_M1_M4_CONSTRUCTION_PROMPT_SHARED_PREAMBLE_v0.1.md` §三／§四／§五
- `decision-chain/docs/M1_ENGINEERING_EXECUTION_PROMPT_v1.2.md`（本任务 Task Contract 与 P0 范围）

---

## 一、两个不同粒度的对象，不要混

侦察发现仓库里两个概念经常被混用，必须先分清：

| 对象 | 定位 | 冻结来源 |
|---|---|---|
| **任务上下文快照**（本设计的主体） | M1 从自然语言编译出的完整上下文，14 条业务语义 + 5 维度 | 共享合同一 |
| **统一内容任务**（Content Task） | 快照的一个**投影**，只在把工作交给 Content Brief 时使用，两份文档定义不完全一致 | 前言 §四 CAP-03（12 项）／切片合同 §5.8（13 项） |

`Content Task` 不是快照的替代品，是快照对 Content Brief 这一个下游的**精简视图**。两份定义取并集（见 §四），不新造第三份列表。

---

## 二、任务上下文快照：14 条语义 → 物理字段

以下每条给出：冻结语义原文（缩述）、本设计选用的字段名、取值形状。**字段名不冻结，可在实现中调整**，但字段承载的语义边界必须与右列一致。

| # | 冻结语义（共享合同一 §二） | 字段名 | 形状 |
|---|---|---|---|
| 1 | 用户、工作空间、表达主体、账号范围 | `subject_scope` | `{workspace_id, account_ids[], expression_subject_hint}` |
| 2 | 当前任务属于本条／本周期／长期 | `current_task` | `{text, temporal_scope: ONE_ITEM｜CYCLE｜LONG_TERM, source_ref}` |
| 3 | 主目标、次目标、优先级、不可牺牲条件 | `goal_structure` | `{primary_goal, secondary_goals[], priority_order[], non_sacrifice_constraints[]}` |
| 4 | 经营目标类别及混合 | `business_goal_categories[]` | 枚举集合，非单值：`LONG_TERM_VALUE｜ACCOUNT_GROWTH｜FOLLOWER_GROWTH｜TRAFFIC｜GMV｜LEADS｜STORE_VISIT` |
| 5 | 账号阶段 | `account_stage` | 自由文本 + `confirmation` 维度（见 §三） |
| 6 | 表达裁量与风险边界 | `expression_discretion` | `{plot_allowed, remix_allowed, conflict_allowed, controversy_allowed, notes}`，每项可为 `ALLOWED｜NOT_ALLOWED｜UNSTATED` |
| 7 | 期望发布量／当前周期可用产能／基线产能（三者分别承载） | `capacity_triad` | `{desired_output, cycle_available, baseline}`，**不得只取一个覆盖三个** |
| 8 | 当前运营周期 | `cycle_ref` | `{cycle_id｜null, applicable: BOOL}` |
| 9 | 可用事实/偏好/参考/系统判断及缺口 | `evidence_bundle[]` | 每条见 §三 五维度 |
| 10 | 市场观察 | `market_observations[]` | `{source, platform, observed_at, applicable_niche, mechanism_summary, validity}` |
| 11 | 缺失信息与已降级项 | `gaps[]` | `{field_ref, status: MISSING｜DEGRADED, degraded_to}` |
| 12 | 本轮允许调用的能力（集合，非单值） | `allowed_capabilities[]` | `{capability_id, reachable: BOOL, block_reason｜null}`，覆盖 CAP-01～CAP-08 |
| 13 | 附带诉求 | `open_threads[]` | `{id, text, raised_at_revision, status: OPEN｜SURFACED｜HANDLED}`（**在 v1_state 的 OPEN／SURFACED 二值基础上补终态 HANDLED，解决侦察发现的"永不消失"缺陷；本对象与 v1_state 的 open_threads 是两个独立实现，互不覆盖**） |
| 14 | 运行中新增的联网/外部证据 | `runtime_evidence[]` | `{source, obtained_at, applicable_scope, snapshot_version}` |

### 五个正交维度（§三，适用于 #9 evidence_bundle 及其他标注"见五维度"的字段）

```text
nature        : FACT | PREFERENCE | REFERENCE | SYSTEM_INFERENCE
provenance     : USER_DIRECT | SOURCED_MATERIAL | VALID_HISTORICAL_ARTIFACT | AUTHORIZED_EXTERNAL | SYSTEM_DERIVED
confirmation   : USER_CONFIRMED | SYSTEM_TENTATIVE | REJECTED | SUPERSEDED | EXPIRED
scope          : THIS_ITEM_ONLY | THIS_CYCLE_ONLY | THIS_ACCOUNT | LONG_TERM_SUBJECT
availability   : AVAILABLE | UNKNOWN | NOT_PROVIDED | DECLINED | STALE
```

冻结硬约束（共享合同一 §三 末段，逐字保留）：
- 「系统推断不因为被写入持久化就升级为用户确认事实」
- 「参考资料和历史产物不得覆盖用户已经确认的事实」
- 不要求每条记录机械具备五个物理字段——本设计里 `evidence_bundle[]` 每条**必须**携带全部五维度（因为它就是该规则的直接落地对象），但 `market_observations[]`／`runtime_evidence[]` 等其他数组按各自需要选用，不强求。

---

## 三、Content Task 投影（并集定义）

前言 §四 CAP-03（12 项）∪ 切片合同 §5.8（13 项）的并集，共 14 项唯一语义（去重后）：

```text
source                      来源标识（周期计划／Campaign／用户直接任务／合法历史产物——不是封闭枚举）
cycle_role                  本条在周期组合中的角色，不适用时明确标注，不得虚构周期
primary_goal                一个主目标
secondary_goals[]           允许兼顾的有限次目标
priority_order[]
non_sacrifice_constraints[]
audience_problem_scene      受众问题／场景／机会
audience_shift               希望观众发生的变化
content_promise             内容承诺／核心命题／待验证判断
account_stage
expression_discretion       表达裁量与风险边界
evidence_and_gaps           事实素材与缺口
platform_and_form           平台／内容类型，或明确未确认
available_capacity          本条可占用的产能
post_publish_observation    发布后希望观察什么结果
```

投影函数 `project_content_task(snapshot) -> content_task`：

- `source` ← `current_task.source_ref` 或调用方显式传入（M3／Campaign／用户直接任务／历史产物）
- `cycle_role` ← 若 `current_task.temporal_scope != CYCLE`，写 `NOT_APPLICABLE`，不得从 `cycle_ref` 编造
- `primary_goal`／`secondary_goals`／`priority_order`／`non_sacrifice_constraints` ← 直接取自 `goal_structure`
- `audience_problem_scene`／`audience_shift`／`content_promise` ← 快照 14 条本身**没有专列字段**，属于 Content Task 独有的更细粒度语义，**由调用方（Campaign 决策包，或 M3 未来自己的判断）在投影时补入，M1 不替这三项做专业判断**（越界进入 CAP-02/CAP-04 的专业判断范围）
- `account_stage` ← `account_stage`
- `expression_discretion` ← `expression_discretion`
- `evidence_and_gaps` ← `evidence_bundle[]` + `gaps[]` 中与本条相关的子集，**保留来源与确认状态，不摊平**
- `platform_and_form` ← 若未确认，写 `PLATFORM_UNCONFIRMED`（与生产运行时合同 `platform` 槽位的禁自选原则一致，见 §五）
- `available_capacity` ← `capacity_triad.cycle_available`（不是三者之一随便取，是明确取"当前周期实际可用"这一项，因为 Content Task 只关心这一条内容能占用多少）
- `post_publish_observation` ← 快照没有对应字段，同样是 Content Task 独有，由 Campaign／未来 M3 判断补入

**M1 只实现这个投影函数和它的输入/输出形状；不产出 `audience_problem_scene`／`audience_shift`／`content_promise`／`post_publish_observation` 的内容本身**——那是 CAP-02/CAP-04/未来 CAP-03 的专业判断，M1 越界会违反前言 §六.1「M1 只决定当前需要哪项能力，不替专业组件作深度判断」。

---

## 四、调用意图对象（M1 → M4 唯一语义真源）

```text
call_intent := {
  needed_capabilities: [CAP_ID],       # 零个、一个或多个，非线性
  per_capability: {
    CAP_ID: {
      status: DIRECT_ENTRY_ELIGIBLE | DEGRADED_INPUT | BLOCKED,
      required_input_present: {...},   # 对照该 CAP 的"必需业务输入"逐项标记 available/missing/degraded
      legal_equivalent_input_used: [...],
      block_reason: str | null,        # 只有 status=BLOCKED 才有
    }
  },
  continuation: {
    open_threads_to_surface: [...],
    non_blocking_gaps: [...],
  },
}
```

**已知限制（本任务 §3.3 决定不做的事，写在这里而不是代码注释里，供 Reviewer 与 Founder 核对）**：

- `status: DIRECT_ENTRY_ELIGIBLE` 表示"按业务语义应当可以直接进入"，**不代表**已部署的主 Chatflow（`v1_state` 的 `UPSTREAM_OF` 线性锁）会真的放行——那把锁前言暂定归 M4 施工范围，本任务不触碰。M1 候选 App 里对 `call_intent` 的验证走 M1 自己新建的候选环境，不经过主 Chatflow 的 `v1_state`。
- Matrix 的 `INPUT_INSUFFICIENT` 整任务硬停（Skill 正文行为，受保护资产）在 `per_capability.MATRIX.status` 判定时会被如实预测为 `BLOCKED`，但 M1 不修改 Matrix Skill 正文本身。
- Content Brief 冻结合同要求 Campaign 决策包为必需输入 #1；`call_intent` 对"M3 或用户直接任务 → Content Brief"路径如实标记 `DEGRADED_INPUT` 并注明"需要 Content Brief 合同后继版本或 M4 适配层，不在本任务范围"，不伪造等价 Campaign 输入。

---

## 五、与生产运行时合同的接缝

`platform`／`production_profile`／`duration_band` 三个槽位在生产运行时合同（`CONTENT_PRODUCTION_RUNTIME_CONTRACT_v0.1.md` §4.1）里明确"不得自动选择、必须询问"。`task_context_snapshot` 和 `content_task` 投影里出现的 `platform_and_form`／`available_capacity` 即使有值，**也不能被生产链侧当作已经满足运行时门禁**——M1 只是把用户已经说过的话如实投影，不代表用户在"这条内容用什么平台"这个具体运行时问题上已经被问过。这条边界写死在投影函数注释里，作为 M1→M4 接缝的显式约束。

---

## 六、与 `v1_state`（已部署主 Chatflow）的关系

M1 不修改、不复用 `v1_state` 的代码本体（受保护资产）。M1 候选 App 是独立实现，但**继承其已验证的工程纪律**（侦察 §一已详细记录，不重复）：

1. 只有确定性代码节点能产出最终 `call_intent`／`task_context_snapshot`，LLM 只提议结构化 patch（模仿 `v1_shadow`／`v1_state` 分工，避免把执行决定放进模型）。
2. Patch 整体拒绝：任一未知字段或非法枚举值，拒绝整个 patch，不局部采纳（对应 `validate_patch()` 的失败即整体拒绝语义，是 A-4 失败不伪装的机制基础，也是 AU-05 的通过判据）。
3. 失败必须诚实：产出对用户可读的说明，不编造"可能是网络问题"一类原因（前言与 A-4 已冻结的措辞，M1 沿用同一纪律）。
4. `open_threads` 补终态 `HANDLED`，修复侦察发现的现网缺陷（v1_state 的 SURFACED 永不消失问题）——这是 M1 自己新对象的独立改进，**不回写、不修改** v1_state 本体。

---

## 七、待验证事项（不在本文件里裁决，留给实现自验与 Reviewer）

- `evidence_bundle[]` 五维度是否会让候选 LLM 的结构化输出过于复杂而不稳定（`v1_shadow` 的设计说明里提到过 DeepSeek V4 Flash 只能稳定处理扁平字符串/枚举，不支持嵌套对象）——如果稳定性不够，需要考虑"LLM 只出粗粒度信号，五维度由确定性代码从上下文/历史推导默认值"这条降级路径。
- `call_intent.per_capability` 覆盖 CAP-01～CAP-08 共 8 项，其中 CAP-03（M3）与 CAP-05（创意锦标赛）目前没有物理路由入口——这两项在 M1 候选环境里只能产出 `status: BLOCKED, block_reason: "NO_PHYSICAL_ENTRY_YET"`，不能伪造一个入口。
