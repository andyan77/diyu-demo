# S4 受影响连续链 FAILURE TRIAGE 003

- `task_id`：`DIYU-V1-UNIFIED-DIFY-APPLICATION-001`
- 冻结判据：`S4_NARROW_CHAIN_GATE_v1.0.json`，sha256 `7ccb7e666273075ba8c93e8df44a52e0da099e1035b8c170fcaf702a3826c9e0`，冻结提交 `dbc212a`（判据早于结果）
- 判定书：`S4_NARROW_CHAIN_RESULT_v1.0.json`；证据：`unified-app/evidence/stages/s4_narrow_chain/S4-NC-T1…T6.json`
- 本文件只追加登记。**未改判据、未改检查器、未改被测对象、未重跑、未做第三次修复迭代。**

## 结果

**FAIL｜13 PASS / 4 FAIL / 17。** 四条 FAIL 分属四个不同原因，其中两条在被测对象、两条在我自己的判据与检查器。

| | | |
|---|---|---|
| N-01 | PASS | 首段真实经过 M3 → Hop → Seam → Content Brief |
| N-02 | PASS | Content Brief 非空 artifact |
| N-03 | PASS | `facts_registered` 来源可回指 |
| **N-04** | **FAIL** | T3 缺口是 `{content_origin_mode, goal_family}`，不是恰好一个 |
| **N-05** | **FAIL** | T6 外壳里没有 `content_origin_mode` 键 |
| N-06 | PASS | 已确认字段全任务不被抽空或改写 |
| **N-07** | **FAIL** | T5 Production Director artifact 为 0 |
| N-08 | PASS | 只运行目标能力，零暗跑 |
| N-09 | PASS | 无授权越界表述 |
| N-10 | PASS | 空返回未抹除成功上游产物 |
| N-11 | PASS | M2 无重复副作用 |
| N-12 | PASS | R1 新基线漂移判据 |
| N-13 | PASS | 作用域隔离判据 |
| N-14 | PASS | 零内部字段泄漏 |
| **N-15** | **FAIL** | 负控制选错了轮次 |
| N-16 | PASS | 新任务不继承内容级字段（正负控制） |
| N-17 | PASS | 零编造 |

## 修复确实生效的部分（可独立复核）

`uapp_fields` 逐轮的补齐记录（运行器原样打印，判定器独立重算一致）：

| 轮 | 目标能力 | 载体补齐 | 用户本轮确认 | 合成后仍缺 | artifact |
|---|---|---|---|---|---|
| T1 | CONTENT_BRIEF | `primary_goal` | 无 | 5 项 | 0 |
| T2 | CONTENT_BRIEF | 无 | `audience_problem` `content_promise` `expected_change` `expression_subject_and_boundary` | **无** | **6188+** |
| T3 | CREATIVE_SCRIPT | `primary_goal` `expected_change` `content_promise` | 无 | `content_origin_mode` `goal_family` | 0 |
| T4 | CREATIVE_SCRIPT | `expected_change` `content_promise` `expression_subject` | **`content_origin_mode`** | `goal_family` | **6843** |
| T5 | PRODUCTION_DIRECTOR | **`content_origin_mode`** `time_window` `content_promise` | 无 | `production_profile` | 0 |
| T6 | PUBLISHING_PACKAGING | `cta_contract` | 无 | 无 | **9031** |

对照修复之前的同一场景：T4/T5/T6 的 artifact 全部为 0，且系统在 T5 逐字重复了 T3 问过的素材来源问题。

**本轮 T5 的 hop 仍然把 `content_origin_mode` 列为缺口**（`hop_wanted_it_again: true`），但载体补齐了它，用户没有被重复询问（T5 问的是制作规模，不是素材来源）。这正是 TD-UAPP-20 修复要解决的那件事，它成立了。

---

## FAIL-1｜N-04：载体只认反引号字段，`goal_family` 在覆盖范围之外

### observed

T3 合成后缺口 = `{content_origin_mode, goal_family}`；判据要求恰好 `{content_origin_mode}`。T4 合成后仍缺 `goal_family`。

### 事实

`m5_compose` 组装外壳时，`goal_family` 写成**不带反引号**的一行，嵌在 `objective:` 块里：

```
objective:
  `primary_goal`: 让熟客建立……的判断方法
  goal_family: LONG_TERM_VALUE
```

`uapp_fields` 的字段识别正则是 `` ^(\s*)`([A-Za-z_]\w*)`\s*:\s*(.*)$ ``，只认反引号字段。于是 `goal_family` 永远进不了载体，也永远补不上；抽取器哪一轮没抽到它，它就重新变成缺口。

T2 抽取器抽到了它（T2 合成后缺口为 `无`），T3 又没抽到——正是跨轮丢失，但落在我的覆盖范围之外。

### confirmed_origin

`SYSTEM_UNDER_TEST`（本轮修复本身，覆盖不完整）。

`highest_failing_node`：`uapp_fields` 的字段识别范围。

规划侧裁决原文要求「不得只针对本次出现的三个字符串写专用分支，**应覆盖现有任务上下文和能力合同中已声明的决策相关字段**」。`goal_family` 是外壳 `objective` 块里已声明的决策相关字段，属于该范围。**这一条没做到。**

### mutation_target（本轮不执行）

字段识别范围：把外壳里所有已声明的决策相关字段纳入，而不是只认反引号书写形式。

---

## FAIL-2｜N-05：判据要求字段出现在不需要它的能力外壳里

### observed

`T5: value_len 51、未重复询问` ✅；`T6: value_len 0` ⇒ FAIL。

### 事实

`content_origin_mode` 不在 PUBLISHING_PACKAGING 的能力必填清单里，`m5_compose` 因此不把它写进 PP 的外壳。载体里它仍然在（T6 的载体含该字段，`lvl=A`），用户也没有被重复询问。

我的判据写成「T5/T6 的 `capability_call` 中该键非空」。要满足它，就得把非必填字段硬塞进能力外壳——那会破坏能力合同，方向是错的。

### confirmed_origin

`ORACLE_OR_CRITERION`（我的判据）。

这与 Phase C 的 F-03 是同一类错误，我在那里改对过一次，这里又犯了一次：**「保留」指的是留在任务载体里、不再重复询问，不是出现在每一个能力的外壳里。**

### 需要说明

裁决原文「该字段在 T5/T6 仍然存在，不再重复询问」的两个实质要求都成立：T5 外壳中该字段在场且取值来自载体；T5/T6 都没有重复询问素材来源。**但按冻结判据的字面写法，这一条是 FAIL，我不改判据、不追认。**

---

## FAIL-3｜N-07：Production Director 停在 `production_profile`

### observed

T5 artifact = 0，`business_delivery_outcome = UNKNOWN`，合成后仍缺 `production_profile`。用户看到的追问是：「这次是单人手机、一两个人、小团队，还是商业制作？」

T4 的 Creative Script 产出 6843 字、T6 的 Publishing & Packaging 产出 9031 字，都非空非占位。**只有 PD 这一跳没产出。**

### 事实

制作规模在输入里**根本不存在**：

| 来源 | 「单人」 | 「手机」 | 「小团队」 | 「商业制作」 |
|---|---|---|---|---|
| 一页纸夹具 | 无 | 无 | 无 | 无 |
| 六轮冻结话术 | 无 | 无 | 无 | 无 |

修复之前那一轮，hop 在 T5 给 `production_profile` 合成过一个值，来源标记 `UP`（取自上游）：

> 产能无记录：不排多条，只保证本条最低制作条件成立（苏禾可出镜、品类名称为例、周宁可复核涉及事实）

这是一句对冲说法，不是编造出来的拍摄规模。本轮 hop 改为判它是缺口，PD 于是追问用户。

### candidate_sources

| 候选 | 支持证据 | 反对证据 |
|---|---|---|
| `CONTRACT_OR_INTENT`：冻结场景六轮从未提供制作规模，而 PD 的能力合同要求该项 | 夹具与六轮话术里确实一个字都没有；在没有来源时追问优于编造 | 判据要求 PD 在这六轮内产出 |
| `SYSTEM_UNDER_TEST`：hop 对该字段的逐轮抽取在「从上游对冲出一个说法」与「判为缺口」之间不稳定 | 同一字段在修复前那一轮被合成、这一轮被判缺口 | 两轮的上游不同（前者上游是 Brief，本轮是 6843 字 CS 脚本），输入不同，不构成同输入不同结论 |

### confirmed_origin

`INSUFFICIENT_EVIDENCE`。一次运行无法区分这两者，而重复采样、追加场景、第三次修复迭代本轮都被明令禁止。

**不主张「追问是正确行为所以应该判过」**——冻结判据要求 PD 产出，它没产出，就是 FAIL。

---

## FAIL-4｜N-15：负控制选错了轮次

### observed

正控制六轮全部成立：每一轮「载体本可补的字段集合」与「实际补进外壳的集合」逐轮相等，且都出现在 `carried_fields` 里（T3/T4/T5/T6 各 2–3 项）。

负控制 FAIL：`with_empty_carrier_still_a_gap: false`。

### 事实

负控制的选法是「取第一个 `carried_fields` 非空的轮次」，选中了 **T1**，字段 `primary_goal`。而 T1 的 `primary_goal` 根本不是跨轮携带来的——它在 T1 自己的外壳里就是非空的，同一轮内被记进载体再用来补缺口。把载体清空重放，它当然还是能被同轮自填。

选 T3/T4/T5/T6 任一轮的真实跨轮携带字段，负控制才有判别力。

### confirmed_origin

`CHECKER_OR_FIXTURE`（我的判定器）。

### 顺带登记的被测对象疑点（未确认，不上行）

T1 的 hop 输出自相矛盾：外壳里 `` `primary_goal` `` 非空，`extraction_gaps_text` 里却同时列着 `objective.primary_goal`。同一次执行既写了值又报了缺口。本轮不追查、不修改，登记为 `TD-UAPP-23`。

---

## actual_cost（本轮实测）

| 项 | 冻结预算 | 实际 |
|---|---|---|
| 画布 workflow run | 6 | **6** |
| 嵌套应用 run | ≤24 | **24** |
| DeepSeek LLM 节点尝试 | 预期 36 / 上限 44 | **33 成功、0 失败** |
| 重试 | ≤1（仅纯传输失败） | **0** |
| 夹具上传 | 6 | **6**（窗口内计 5，T1 那次发生在窗口起点之前） |
| M2 `diyu_business` | workspace/account/cycle/task 各 1 | **各 1**；`task_snapshots`／`artifacts`／`publish_instances` 各 0 |
| 重复幂等键 | 0 | **0** |
| 第三方并发写入者 | 允许并登记 | **本轮为空** |
| 受保护面（R1 基线） | 零漂移 | **九项零漂移** |
| 候选图 | 零变更 | 仍为 `8998088e…` |
| 真实内容平台 | 从未连接 | **`publish_instances` 0 行** |

全部在预算内，无一项越界。

## 本轮处置

- **FAIL，立即停止。** 不修改、不重跑、不追加场景、不做第三次修复迭代。
- 五项允许上调的结论**一项都不上调**：`TD-UAPP-20/21/22` 不 CLOSED，`FACT_SUFFICIENCY_CHAIN_REPAIR` 与 `S4_CONTENT_ORIGIN_CONTINUATION` 不 PASS。
- 旧 C3 FAIL、旧 Gate、旧判定书、R0 基线全部原样保留。
- 根任务保持 `IN_PROGRESS`，`terminal_state` 未设，停在 CHECKPOINT。`main` 未动。
- 失败 Checkpoint 已 commit 并 push 任务分支。

## 需要规划侧裁决

| # | 事项 | 归因 |
|---|---|---|
| 1 | `uapp_fields` 的字段识别范围扩到外壳中全部已声明决策相关字段（含 `goal_family` 这类非反引号书写） | `SYSTEM_UNDER_TEST` |
| 2 | N-05 判据改写：「保留」判在任务载体与不重复询问，不判在每个能力外壳的键在场 | `ORACLE_OR_CRITERION` |
| 3 | `production_profile` 由谁提供：补进冻结场景、还是认定 PD 在无来源时追问即为正确终态 | `INSUFFICIENT_EVIDENCE` |
| 4 | N-15 负控制改选真实跨轮携带的轮次 | `CHECKER_OR_FIXTURE` |
| 5 | `TD-UAPP-23`：hop 同一次执行既写值又报缺口 | 新登记，未确认 |

以上均为判据侧或需要新授权的变更，执行侧不自行决定。
