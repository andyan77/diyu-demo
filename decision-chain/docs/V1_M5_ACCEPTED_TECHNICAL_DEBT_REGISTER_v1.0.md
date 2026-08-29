# M5 已接受技术债登记表 v1.0（全仓唯一主表）

- `task_id`: `DIYU-V1-M5-UNIFIED-INTEGRATION-FINAL-ACCEPTANCE-001`
- 授权：`M5-FOUNDER-ADJUDICATION-003`（2026-08-29），合同 `v1.2`
- **本表是 M5 技术债的唯一主表。** 其它文档只引用本表，不得复制第二份。
- `result_preservation_rule`：每项原 `result` 与 `freshness` **原样保留**，
  另加 `founder_disposition`；**`disposition` 不是 `PASS`。**

## 读法（先说清楚，免得表被误读）

`founder_disposition = ACCEPTED_TECHNICAL_DEBT_FOR_V1_CLOSEOUT` 的意思只有一条：
**这一项不再阻断 v1.2 收口公式。** 它不改变该项的技术结果，不改变证据时效，
也不表示问题已解决。要把任何一项变成 `PASS/CURRENT`，需要新的任务与新的授权。

---

## `TD-M5-01`｜四项非 P0 语义人判未决

| 项 | 内容 |
|---|---|
| `source_items` | `H01-A1`、`H01-A4`、`H02-A3`、`H02-C2` |
| `source_result` | `NOT_VERIFIED` | 
| `freshness` | `PENDING_HUMAN` |
| `classification` | `NON_P0_SEMANTIC_HUMAN_ONLY` |
| `founder_disposition` | `ACCEPTED_TECHNICAL_DEBT_FOR_V1_CLOSEOUT` |
| `evidence_ref` | `V1_M5_FINAL_P0_R3_HOLDOUT_VERDICT_v1.0.md` §1.4／§2.1／§2.2；判据 `SEALED_ORACLES_FINAL_P0_v1.0.md` §0.7 |

**用户影响**：四项都关系到"系统说得够不够清楚"，不关系到"系统会不会做错事"。
最具体的一条是 `H01-A1`：素材撤回时，系统没有主动指出那条轻量图文的唯一来源同样是
被撤回的记录，而是顺着用户的判断给了相反的事实断言。**该行为在两次运行中稳定复现，
不是抖动。** 后果是用户可能带着一条本该停下的内容继续往下走。

**当前缓解**：判据本身把该项归为非 P0；同轮系统另附了条件化提醒
（"如果草稿里其实引用了同一位顾客的具体描述，就需要一并修正"），
不构成拦截，但留下了人工发现的机会。`H01-A4`／`H02-A3`／`H02-C2` 三项只影响表述完整度。

**限制**：执行侧**无权**自判这四项（`SEMANTIC_HUMAN_ONLY`），也不得用脚本或模型代判。

**后继触发**：Founder 或独立评审人做一次人判即可关闭；`H01-A1` 若被判 FAIL，
按判据仍是非 P0，但应作为 M3 影响面切分的改进输入。

---

## `TD-M5-02`｜十类合法短入口未在当前候选上复验

| 项 | 内容 |
|---|---|
| `source_items` | `M5-AC-03`（`DE-01`…`DE-10`） |
| `source_result` | 原 `PASS`（`DE-03` 原 `FAIL`） |
| `freshness` | **`STALE`** |
| `classification` | `AFFECTED_DIRECT_ENTRY_REVERIFICATION_NOT_RUN` |
| `founder_disposition` | `ACCEPTED_TECHNICAL_DEBT_FOR_V1_CLOSEOUT` |
| `evidence_ref` | `V1_M5_FINAL_P0_R7_INDEX_RECOMPUTE_v1.0.md` §二；`DIRECT_ENTRY_SUITE_deFRB3.json` |

**用户影响**：十条短入口是"用户可以直接进入某个能力"的路径。它们最后一次通过验证
是在被本轮替换的应用之前，因此**当前候选上这些入口的行为未经验证**。

**必须点名的一条**：冻结清单写"十类短入口中无依赖项可复用"，逐条查 `apps_actually_run`
后**为空集**——十条全部穿过被改应用。所以这里不是"复用了一部分"，是**一条都不能复用**。

**当前缓解**：`R5` 的完整主路径在当前候选上通过，四个能力均交付，说明主链路可用；
短入口与主路径共用同一批应用与接缝，但**共用不等于已验证**。

**后继触发**：新的正式轮授权。

---

## `TD-M5-03`｜十九维中两维时效缺口

| 项 | 内容 |
|---|---|
| `source_items` | `M5-AC-04`、`homogenization`、`dramatization_derivative_creation` |
| `source_result` | 两维 `STALE`；其余十七维 `CURRENT` |
| `freshness` | **`STALE`** |
| `classification` | `NINETEEN_DIMENSION_FRESHNESS_GAP` |
| `founder_disposition` | `ACCEPTED_TECHNICAL_DEBT_FOR_V1_CLOSEOUT` |
| `evidence_ref` | `V1_M5_FINAL_P0_R7_INDEX_RECOMPUTE_v1.0.md` §三；`FINAL_P0_R7_INDEX_RECOMPUTE.json` |

**用户影响**：同质化（四个账号是不是同一内容换四种说法）与演绎／二创边界，
这两维在当前候选上没有当期证据。它们绑定的 `DE-06`／`DE-07` 是 `STALE`，`AB-FINAL-01` 未评。

**必须点名的一条**：那十七维记 `CURRENT` 用的是"一维只要有一条当期 PASS 证据即 CURRENT"
的口径，**同一维下仍可能挂着 STALE 证据**（权限维的 `RISK-PERM-CTA-01`、
恢复维的 `DE-10`、不退化维的 `REG-M3-01`）。逐行 `freshness` 在 JSON 里。
**`CURRENT` 在这里是"有代表性的当期证据"，不是"该维已全覆盖"。**

**后继触发**：新的正式轮授权。

---

## `TD-M5-04`｜独立 A/B 盲评未做，且盲评在本仓库内不成立

| 项 | 内容 |
|---|---|
| `source_items` | `M5-AC-05`、`M5-AC-06` |
| `source_result` | `NOT_VERIFIED` |
| `freshness` | `NOT_VERIFIED` |
| `classification` | `INDEPENDENT_AB_BLIND_REVIEW_DEFERRED_AND_IN_REPO_BLINDNESS_INVALID` |
| `founder_disposition` | `ACCEPTED_TECHNICAL_DEBT_FOR_V1_CLOSEOUT` |
| `evidence_ref` | `V1_M5_FINAL_P0_AB_REBUILD_AND_STALE_MARKING_v1.0.md` §四 |

**用户影响**：没有任何独立证据说明"走专业能力的产出比好 Prompt 更好"。
这是 M5 最核心的产品主张之一，**当前没有被验证过**。

**必须点名的两条**：
1. `AB_SUITE_RAW_*.json` 带显式 `A`／`B` 键，与盲评包 `甲`／`乙` 同目录并存，
   任何拿到本仓库的人都能用正文或字数还原映射。**封存的 mapping 保护不了什么。**
   盲评包必须**脱离本仓库**单独交给独立评审人，否则该盲评无效。
2. 运行器把 `A=4199字 B=1944字` 打进了日志，盲评包里 `甲=1944`／`乙=4199`——
   **执行侧已经知道 `AB-M3-01` 的映射，对该案例的任何评分意见一律无效。**

**当前状态**：受影响案例已在当前候选上重建（`AB_*_abFfp1.json`），
新 sealed mapping 已生成且**未打开**；旧包 `abFRB3` 标 `STALE / INVALID_FOR_FINAL_SCORING`
原样保留。

**后继触发**：安排隔离交付的独立人类盲评。

---

## `TD-M5-05`｜`M5-AC-07` 因四项非 P0 人判未决而不得记 `PASS`

| 项 | 内容 |
|---|---|
| `source_items` | `M5-AC-07` |
| `source_result` | `NOT_VERIFIED` |
| `freshness` | `NOT_VERIFIED` |
| `classification` | `FOUR_NON_P0_HUMAN_SUBITEMS_REMAIN` |
| `founder_disposition` | `ACCEPTED_TECHNICAL_DEBT_FOR_V1_CLOSEOUT` |
| `evidence_ref` | `V1_M5_FINAL_P0_FOUNDER_ADJUDICATION_002_AND_NEGATIVE_CONTROL_VERDICT_v1.0.md` §五 |

**已关闭的部分（不重复登记为开放债务）**：`RISK-M4-030+031` 已 `PASS / CURRENT`
（正向等价 + 一次冻结负控制双向成立）；两项原 P0 已由裁决 001 关闭；
`applicable_p0_failures = 0`。

**仍开放的部分**：`TD-M5-01` 的四项。本项与 `TD-M5-01` 是同一根因的两个层次，
不是两笔独立债务——`TD-M5-01` 关闭即本项关闭。

---

## `TD-M5-06`｜受影响回归的时效缺口

| 项 | 内容 |
|---|---|
| `source_items` | `M5-AC-08`、`REG-M3-01`、受影响 A/B |
| `source_result` | `REG-M1-01`／`REG-M2-01`／`REG-M4-01`／`REG-SKILLS-01` 为 `PASS / CURRENT`；`REG-M3-01` 原 `PASS` |
| `freshness` | `REG-M3-01` **`STALE`**；A/B 两例 `NOT_RUN` |
| `classification` | `AFFECTED_REGRESSION_FRESHNESS_GAP` |
| `founder_disposition` | `ACCEPTED_TECHNICAL_DEBT_FOR_V1_CLOSEOUT` |
| `evidence_ref` | `V1_M5_FINAL_P0_R7_INDEX_RECOMPUTE_v1.0.md` §三、§五 |

**用户影响**：`REG-M3-01` 是 M3 的不退化回归，而 M3 successor 正是本轮被改的对象之一，
**改了 M3 却没有在改后跑一次 M3 的不退化回归**。这是本表里与本轮改动关系最直接的一条。

**当前缓解**：`R6` 11／11 确定性测试在当前候选上通过，含负控制与假阳性控制，
并逐字节核对 M3 successor 的四条新增条款各存在一次；
`R2` 三份原留出在当前候选上重跑、三处 P0／残留均不复现；
`R5` 完整主路径通过。这些覆盖了 M3 的改动面，但**不等于** `REG-M3-01` 本身已复验。

**后继触发**：新的正式轮授权。

---

## `TD-M5-07`｜冻结十九维映射里有一个查不到的用例 id

| 项 | 内容 |
|---|---|
| `source_items` | R7 「质量」维映射 |
| `source_result` | `KNOWN_DEFECT` |
| `freshness` | `CURRENT`（缺陷本身已确认） |
| `classification` | `RISK-M4-030_ID_MISMATCH_IN_FROZEN_INDEX` |
| `founder_disposition` | `ACCEPTED_TECHNICAL_DEBT_FOR_V1_CLOSEOUT` |
| `evidence_ref` | `V1_M5_FINAL_P0_R7_INDEX_RECOMPUTE_v1.0.md` §四 |

**缺陷**：映射把「质量」维绑到 `RISK-M4-030`，实际用例 id 是 `RISK-M4-030+031`。
字符串不等，该行恒为 `NOT_RUN`。

**用户影响**：当时唯一一条当期 `FAIL` 在「质量」维上完全不可见，
该维靠 `FULL-01` 单独记成 `CURRENT`。**同类 id 不匹配会让任何 FAIL 静默消失。**

**为什么本轮不修**：映射来自规划侧冻结件，构建器里写着"改这里等于改判据，
属于合同层动作，执行侧无权"。v1.2 合同亦把此项列入 `non_goals`。

**后继触发**：规划侧修正冻结映射。

---

## `TD-M5-08`｜检查器过严与运行器取值路径缺陷

| 项 | 内容 |
|---|---|
| `source_items` | `judge_m4_030_031` v1.0、R4 负控制运行器 |
| `source_result` | `KNOWN_CHECKER_OR_HARNESS_DEFECTS_WITH_SUCCESSOR_EVIDENCE` |
| `freshness` | `CURRENT` |
| `classification` | `CHECKER_ENUM_OVERSTRICT_AND_RETURNS_JSON_PATH_BUG` |
| `founder_disposition` | `ACCEPTED_TECHNICAL_DEBT_FOR_V1_CLOSEOUT` |
| `evidence_ref` | `V1_M5_R4_CHECKER_CRITERION_TRIAGE_v1.0.md`；`R4_NEGATIVE_CONTROL_RETURNS_SUPPLEMENT.json` |

**缺陷一（检查器过严）**：`judge_m4_030_031` 测枚举字符串逐格相等，
而冻结判据说的是"等价表达不被误判为**失败**"。按运行时 `delivered()`，
`DELIVERED` 与 `DELIVERED_AFTER_RECOVERY` 均属已交付。
该检查器还把一句已过期的根因断言（"M4 外壳解析器假阴性"）硬编码进判词。
Founder 裁决 002 已定：检查器是判据实现，不具改写产品判据的权威。

**缺陷二（运行器取值路径）**：负控制运行器把 `returns_json` 读成结果顶层键，
实际在 `outputs` 之下，导致证据文件里记成 `null`。
**是取值路径写错，不是 Return 不存在**——`component_return = true` 是对的。
真实 `outputs` 已只读取回并补记，零新增调用，原证据不覆盖。

**用户影响**：都不影响产品行为，影响的是**验证结论的可信度**——
过严的检查器会制造假 FAIL，取错的路径会让证据文件看起来缺东西。

**为什么本轮不修**：v1.2 合同 `non_goals` 明确排除；检查器修复必须另出版本，
不得原地改 v1.0。

**后继触发**：下一版检查器与运行器。

---

## `carry_forward`（现有证据已披露、未被后继证据关闭的其他限制）

按 `carry_forward_rule`，只登记已披露且未关闭的，不展开新审计：

| 限制 | 出处 | 状态 |
|---|---|---|
| `RB-01` 第 4 轮把「三条旧报错记录全部转为已处理／归档」写在计划表里，完成态词有歧义 | `V1_M5_FINAL_P0_R2_DIRECTED_REVERIFICATION_v1.0.md` §1.5 | 观察，待人类复核（并入 `TD-M5-01` 的人判面） |
| `M5-05` 中 M3 索要的那条反馈内容未出现在能力层用户交付里 | 同上 §3.2 | 观察，两轮结构相同，非本轮退化 |
| `HOLDOUT-02` 变体 B 交付首句「已经成型，可以直接进入本周制作」与末节三项待定并存，口径不一致 | `V1_M5_FINAL_P0_R3_HOLDOUT_VERDICT_v1.0.md` §2.2 | 按 §2.8 四条 P0 触发条件逐条比对**不命中**；并入 `H02-C2` 的人判面 |
| 一次重复运行新鲜留出（执行侧误判进程已死所致），第二次产出未评分 | `HOLDOUT_FINAL_P0_ATTEMPT2_NOT_SCORED.json` | 已按判据 §0.2-4 登记，`status: NOT_SCORED`，不删除 |

**已被裁决 001／002 与负控制关闭的项不在本表**：两项原 P0、`H01-A3`、
`RISK-M4-030+031` 的正负控制——按 `carry_forward_rule` 不得重复登记为开放债务。

---

## `reopening_triggers`（任一命中即须重新打开）

1. 准备真实平台发布或生产化；
2. 修改当前 M3／M4／M5 successor 或其关键绑定；
3. 出现与上述债务对应的真实用户损害、事实／权限错误或经营风险；
4. Founder 重新提升优先级并建立新的 `task_id`／合同。

## 计数

```yaml
technical_debt_registry_count: 1        # 全仓唯一主表
open_debt_items: 8                      # TD-M5-01..08
open_debt_items_p0: 0
closed_by_adjudication_not_listed: ["两项原 P0", "H01-A3", "RISK-M4-030+031"]
```
