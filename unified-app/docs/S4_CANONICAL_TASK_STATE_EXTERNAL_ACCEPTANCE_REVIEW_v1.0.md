# S4 规范任务状态载体 · 外部验收复核 v1.0

- `task_id`: `DIYU-V1-UNIFIED-DIFY-APPLICATION-001`
- `authority`: CONTINUE EXECUTION PROMPT v1.0《DIYU V1 · UAPP S4 证据真值纠偏与 PP 交付边界归因》
- `task_mode`: `CONTINUE`（同一 `task_id`，同一合同哈希，不是 REBASE）
- `model_calls`: 0 ｜ `dify_writes`: 0 ｜ `workflow_runs_started`: 0 ｜ `reviewer_calls`: 0
- `git_head`: `a13a73458ee8e3008d67fc4b14758b80296a0df2`（复核开始时 == `origin/codex/v1-uapp-progressive-canvas-001`）
- `origin/main`: `01a42b0ed97344a67302ecb6778ae4a772eb28b2`（未动）

本文件是**新增**文件。不覆盖、不改写任何 v1.0 / v1.1 历史件。

---

## 一、一句话结论

**技术链是真的，交付内容不合格。**
CB → CS → PD → PP 的真实连续链一次走通、哈希血缘成立、受保护面零漂移，这些结论保留为 `PASS / CURRENT`；
但 PP 的最终交付里同时出现「把未登记的人物长期行为写成事实」与「已收到 NO_CTA 仍生成评论互动引导」两类问题，
而旧 V-08 因为探针面根本不覆盖这两类，误报了 PASS。

```yaml
S4_OVERALL_ACCEPTANCE: FAIL / CURRENT
```

---

## 二、激活核验（现场重算，不采信记忆）

| 项 | 值 |
|---|---|
| 仓库根 | `/home/faye/diyu-demo-worktrees/v1-uapp-progressive-canvas` |
| 分支 | `codex/v1-uapp-progressive-canvas-001` |
| HEAD | `a13a73458ee8e3008d67fc4b14758b80296a0df2` |
| `origin/<任务分支>` | `a13a73458ee8e3008d67fc4b14758b80296a0df2`（一致） |
| `origin/main` / `main` | `01a42b0ed97344a67302ecb6778ae4a772eb28b2` |
| worktree | clean（`git status --porcelain` 空） |

绑定文件哈希（与 `a13a734` 一致，`git diff a13a734 -- unified-app` 为空）：

| 文件 | sha256 |
|---|---|
| `S4_CANONICAL_TASK_STATE_GATE_v1.0.json` | `724aace11b0a82213683c4dcb70b89090837b0db50ea09b7195b5d8937eefa19` |
| `S4_CANONICAL_TASK_STATE_GATE_v1.1.json` | `a7986e477edc9f8c46a71983fd51fb7e358efa5442e0c1186fe3ebf98ca14e79` |
| `S4_CANONICAL_TASK_STATE_CANDIDATE_MANIFEST_v1.0.json` | `3b8a7e9a59b56b9b6b93868bf762942ba343c789bec6bb8c3da044e277a3e468` |
| `S4_CANONICAL_TASK_STATE_INPUTS_v1.0.json` | `f19f5d1bc1dcba3061c578b42c43188484706eaa6e9dd265f3f5c37987ee17a6` |
| `S4_CANONICAL_TASK_STATE_RESULT_v1.0.json` | `f068dfe84b5e224bcb54056d15d6e4358226b6523fbe6f44a732a48e560e0f12` |
| `S4_CANONICAL_STATE_VERIFY.json` | `78004a8fa3512b96b548e3502f5b58ae1f111cde99f0853fbe48e26467893355` |
| `S4_CANONICAL_STATE_ADJUDICATE_v1.0.py` | `c0cfa4d548554916ca3c2a4a9cce216143f510a334c15230138bfd23767be73a` |
| `run/S4-CT-T1.json` … `T7.json` | `06b5d033…` `e6d03950…` `fc17fc78…` `a97fa43e…` `30273998…` `e95b0861…` `d9b39d8a…` |

Dify 侧复核时点重算：候选图 `6bf7c8f5f050e0e831d0b4afe29b2835fb08f48da344a2df898d7ca081590852`（49 节点 / 51 边），
九个受保护应用 md5 9/9 与 `RUN_META.scope_snapshot_before` 逐项相同，`hop_pin = 2026-08-30 03:38:31.449618`。
运行窗口之后，候选画布与四个能力应用**零新增 run**。

---

## 三、PP 输入约束是否真实到位 —— 到位

Publishing & Packaging 真实运行 `15e2643a-7710-47d0-a162-40b13726219d`
（app `c9cdea24-9df3-400b-9ecd-1d740e8c96df` = 受保护 PP，`succeeded`，103.45s，inputs 90 811 字节 / outputs 151 481 字节）。

只读证明其输入**已经包含**：

| 约束 | 在输入中 | 原文 |
|---|---|---|
| `cta_contract` | ✅ 逐字 | 「不做购买、到店、私信或领取引导，只保留内容本身」 |
| `NO_CTA` 状态 | ✅ | `capability_call` 与 `professional_input` 合计 4 处 |
| `facts_registered` | ✅ | 序里集品牌事实全文 |
| `content.explicit_non_promise` | ✅ | 「所有具体 SKU 的商品声明只能引用已经登记的商品事实……」 |
| `expression_boundary` | ✅ | 「品牌内容禁止：制造年龄、身材和身份焦虑……如任务确需演绎人物或事件，必须显式标注为虚构……」 |
| `asset_publish_permission` | ✅ | 「具体素材仍按系统里的授权记录选择，未获授权的不要使用或发布」 |
| T6 Production Director artifact | ✅ **逐字整段包含** | 10 121 字，`b032cfd7cb6f1862…` |

**结论：「PP 没收到约束」这条归因不成立，已排除。**

---

## 四、违规文字首次出现的准确节点

九条冻结定位串，逐层计数（层序：PP 输入 → PP 原始输出 → PP artifact → PP user_delivery → Seam → Seam merge → 画布 answer）：

| 定位串 | 首次出现层 | 在 PP 输入内 |
|---|---|---|
| 一直在用这套三问 | `PP.raw_preserved` | 否 |
| 门店做搭配服务 | `PP.raw_preserved` | 否 |
| 常用这套思路 | `PP.raw_preserved` | 否 |
| 你自己买衣服前 | `PP.raw_preserved` | 否 |
| 哪个问题 | `PP.raw_preserved` | 否 |
| 评论区 | `PP.raw_preserved` | 否 |
| 只有内容讨论和问题回应 | `PP.raw_preserved` | 否 |
| 低风险互动范畴 | `PP.raw_preserved` | 否 |
| 不含购买引导 | `PP.raw_preserved` | 否 |

下游透传证明（逐层 sha256 相等）：

```
PP.artifact       == SEAM.artifact                                    True  (14984)
PP.user_delivery  == SEAM.user_delivery == CANVAS.final_text == CANVAS.answer   True  (1632)
```

```yaml
highest_confirmed_failing_node: PUBLISHING_PACKAGING delivery generation
```

Seam 与统一画布投影层**一个字都没加**。按 A3，不得在投影层打补丁。

---

## 五、14/14 在 Gate v1.1 下的重新绑定

`S4_CANONICAL_STATE_VERIFY_v1.1.json`：

- `criteria_ref` = `S4_CANONICAL_TASK_STATE_GATE_v1.1.json`，`criteria_sha256` = `a7986e47…`（Gate v1.1 真实哈希，不再引用 v1.0 冒充）
- 被测对象未改：`S4_CANONICAL_STATE_NODES_v1.0.py` 的 `FIELDS_SRC` / `STATE_SRC`
- 检查逻辑未改：沿用 v1.0 脚本，只重定向输出
- 结果：**14/14 PASS**（P-01…P-11、R-01…R-03）

### 区分证明：单点变异

预期在运行之前写死在 `MUTATIONS` 表里，变异只作用于内存副本，磁盘文件不变。

| 变异 | 冻结预期 | 观察 | 符合 |
|---|---|---|---|
| MUT-01 缺失语义词表整体失效 | FLIP | 未翻掉 | ❌ |
| MUT-02 只拆 offer 内第二道占位闸门 | MASKED（env 解析先生效） | 未翻掉 | ✅ |
| MUT-03 等级闸门失效 | FLIP | 翻掉 P-04、P-05 | ✅ |
| MUT-04 同轮细化与跨轮纠正不分 | FLIP | 翻掉 P-05 | ✅ |
| MUT-05 生产时间窗作用域限定去掉 | FLIP | 翻掉 P-03 | ✅ |
| MUT-06 依赖变化不再置 STALE | FLIP | 翻掉 P-05 | ✅ |
| MUT-07 P-08 fail-closed 矛盾闸门失效 | FLIP | 翻掉 P-08 | ✅ |
| MUT-08 两道占位防线同时拆掉（两点探针） | FLIP | 翻掉 P-02、P-08、R-02 | ✅ |

**MUT-01 的偏差不回改预期**（A2：判据不因结果而改）。改为追加 MUT-07 / MUT-08 两条新探针定性：
MUT-07 单独拆掉矛盾闸门即翻 P-08，MUT-08 两道同时拆掉即翻 P-02/P-08/R-02——
说明占位保证**确实**被这 14 条覆盖，MUT-01 未翻是**两道独立防线互相遮蔽**，不是覆盖缺口。
`all_as_expected` 保持 `false`，不因这条解释改绿。

---

## 六、V-08 拆分结果

`S4_CANONICAL_TASK_STATE_RESULT_v1.1_EXTERNAL_REVIEW.json`，判定器 `S4_CANONICAL_STATE_ADJUDICATE_v1.1.py`，零模型调用。

```yaml
V-08A: PASS / CURRENT     # 执行路由、无暗跑、无泄漏、无 M2 重复副作用 —— 机器可判
V-08B: FAIL / CURRENT     # 事实主张逐项可回指 —— 有界判定
V-08C: FAIL / CURRENT     # CTA 与上游冻结边界一致 —— 有界判定
S4_OVERALL_ACCEPTANCE: FAIL / CURRENT
```

V-08A 的三个子项各自出结论，不再由一个 PASS 代表多件事：

| 子项 | 结果 | 依据 |
|---|---|---|
| 执行路由与单能力 | PASS | 七轮 Seam 工具节点逐轮唯一，`shadow_runs = []` |
| 无泄漏 | PASS | `leak_forbidden_tokens` 43 项逐轮零命中 |
| 无 M2 重复副作用 | PASS | `workspaces/accounts/cycles/tasks` 各 1 行，`boot_turns = [1]`，重复幂等键 `[]` |

V-08B / V-08C 是**有界判定**（`BOUNDED_JUDGMENT_UNDER_FROZEN_RUBRIC`），不是自动判定，也不是模型判定：
Rubric 只表述边界、不针对具体案例；结论由 PP 输出原文逐字支撑；
定位串标注为 `evidence_locator_only, NOT_A_CHECKER`——它们只用于在本次产出里定位已认定的违规，**不得被改写成未来的校验器**。

**V-08B / V-08C 绝不因 token 未命中而 PASS。** 旧探针面里根本没有这两类判定项（见 FAILURE TRIAGE F3），未命中不是证据。

### V-07 展示纠正

v1.0 的 `sorted(k for k, v in last.items() if v == "E")` 拿字段字典与字符串比较，恒为 `[]`。
v1.1 改为 `v.get("lvl") == "E"`，**判定谓词一字未改**，V-07 仍为 PASS。终态真值：

- **E 级 7 个**：`content.explicit_non_promise`、`cta.level`、`delivery.platform`、`expression.boundary`、`expression.subject`、`facts.registered`、`operation.time_window`
- **B 级 12 个**：`audience.expected_change`、`audience.problem`、`content.origin_mode`、`content.promise`、`cta.contract`、`expression.subject_and_boundary`、`facts.publish_permission`、`objective.goal_family`、`objective.primary_goal`、`production.capacity_or_owner`、`production.profile`、`production.time_window`

---

## 七、状态继承

### 保留为 PASS / CURRENT（不 blanket STALE）

- 四份 artifact 已真实产生：CB 6600、CS 6016、PD 10121、PP 14984
- PD→PP 哈希血缘成立（T7 `upstream_delivery` 与 T6 artifact 逐字节相等）
- 每轮只运行一个目标能力，无暗跑
- 已确认字段未被空值擦除
- E 级抽取值没有自动升级为 B（终态 12 B 全部 `ref = TURNn.user_request`，7 E 全部 `ref = TURNn.uapp_hop.<CAP>`）
- 作用域隔离成立（`operation.time_window = 四周内` 与 `production.time_window = 今天半天内` 同名不串）
- `S4_CONTENT_ORIGIN_CONTINUATION` 的窄结论
- 九个受保护应用零漂移（复核时点重算 9/9 一致）

### 被下调 / 不再可声明

| 项 | 之前 | 现在 |
|---|---|---|
| `S4_OVERALL_ACCEPTANCE` | 由 RESULT v1.0 的 `verdict=PASS` 隐含 | **FAIL / CURRENT** |
| V-08（合一） | PASS | 拆分：V-08A PASS，**V-08B FAIL**，**V-08C FAIL** |
| `S4_CANONICAL_STATE_VERIFY.json` 的 14/14 | 被当作「已验证」 | 仅在 **Gate v1.0** 下成立；Gate v1.1 下的 14/14 见 VERIFY_v1.1 |
| Validator discrimination | 未声明过全绿，现明确 | 只有 V-08A 成立；V-08B/V-08C 不得用旧 Checker 冒充成立 |
| `CROSS_TURN_CORRECTION_PROPAGATION` | 已是 NOT_VERIFIED | 维持 **NOT_VERIFIED(NOT_CHECKED)**，不上调 |

不再可声明：S4 整体 PASS ／ Validator discrimination 全部成立 ／ PP 交付符合 PRD ／ 可以进入 S5 ／ 可以合并 main。

上一轮登记的三项上调中，`CANONICAL_TASK_STATE_CARRIER`、`CS_PD_PP_NARROW_CHAIN`、`S4_CONTENT_ORIGIN_CONTINUATION` 描述的都是**载体与链路**层面的窄结论，本轮证据未推翻，保持 CURRENT；
但它们**从来不蕴含**「PP 交付内容合格」，本轮把这条区分显式写死，避免被合并读成 S4 已验收。

---

## 八、本轮不做什么

不改 Dify 画布、不改 PP 或任何被测应用、不改数据库、不重跑任何工作流、不重复采样、不做 A/B、
不覆盖任何历史 RAW/Gate/Manifest/Result、不进入 S5、不合并 main、不填根任务终态。

---

## 九、COMPLETION CHECK

- `real_behavior_verified`：**是**。既包含真实链路成功（7/7 run、28/28 嵌套、39 LLM、链哈希相等），
  也包含 PP 真实内容失败（F1/F2 的逐字原文与逐层首次出现位置）。
- `validator_discrimination_verified`：**只有 V-08A 可成立**。V-08B/V-08C 不得继续用旧 Checker 冒充成立——
  旧探针面里没有这两类判定项。载体侧的 14 条在 Gate v1.1 下重绑定并通过单点变异区分（8 条变异，7 条符合冻结预期，
  MUT-01 的偏差已由 MUT-07/MUT-08 定性为冗余遮蔽而非覆盖缺口，`all_as_expected` 保持 false 不改绿）。
- `core_problem_solved`：本 Prompt 只解决「**证据与声明一致**」。**不声称 PP 已修复。**
- `protected_targets_unchanged_or_authorized`：**true**。`git status --porcelain` 只有新增文件，零修改、零删除、零重命名；
  Dify 侧九个受保护应用 md5 与候选图 sha256 复核时点重算全等。
- `unnecessary_complexity_remaining`：无 A/B、无重复采样、无新架构层、零模型调用、零工作流发起、零数据库写入。
