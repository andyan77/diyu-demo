# `REBIND-004` 冻结件 · 载体 v1.3（修 G-2/G-3/G-4 + M2 接口兼容）

> `task_id` = `DIYU-V1-M3-ACCOUNT-CONTENT-OPERATOR-001`（不变，未建新根任务）
> 权威事件：Founder 2026-08-26 `CONTINUE_TASK`（七条）。
> **本文件在任何一次本轮正式取证运行之前提交，提交顺序即时序自证。**
> `REBIND_003` 与其 `ADDENDUM_001`、`ADDENDUM_002`、`ADDENDUM_003` 原文一律不覆盖、不删除。

---

## 0. 这一轮改什么，一句话

**把"用词面正则去认产品语义"整段拆掉，换成结构化对象 + 确定性比对。**

第 5 轮四条自伤缺陷（`G-1`～`G-4`）共同的上游根因就是这一件事：
词面收紧就漏检（`G-2`）、词面放宽就误报（`G-1`）、词面认不出的对象就整批丢（`G-3`）、
词面只看"有没有"不看"值对不对"（`G-4`）。**四条不是四个 bug，是同一个方法错误的四个方向。**

---

## 1. 允许变化面（超出这个面的变化本轮不做）

| 允许改 | 具体 |
|---|---|
| `SKILL.md` v1.2 → v1.3 | 只在〈必填项闸门〉内增加**审计块的一段机器行**（持续位声明）与两条已有要求的机械化措辞。**产品语义零新增**——不新增任何一项"必须回答的问题" |
| 闸门源码 `account-operations/tools/gate_v12/` → `gate_v13/` | 新目录，v12 原文保留不动 |
| `account-operations/interfaces/M2_TO_M3_PROJECTION_v1.0.schema.json` | **不改原文**；新增 `..._v1.1.schema.json` 后继版本 |
| `account-operations/interfaces/projection.py` | 就地演进（它是 v1.0 与 v1.1 的共同编译器，双版本并存由 `schema_version` 分派） |
| `account-operations/fixtures/` | 新增六族确定性夹具 + 新的 M2 实况抓取 |
| `account-operations/tests/` | 新增/扩充测试 |
| 候选 Dify App `b7fb5b1a-9278-426c-bb8a-f9f288639548` 的**草稿与新发布版本** | 只此一个 App |

| 禁止改（受保护基线） | 依据 |
|---|---|
| `business-persistence/`（M2 真源与 M2 责任） | Founder 第 1 条逐字 |
| `main` 分支 | Founder 第 1 条逐字 |
| 生产 Dify（本 App 之外的任何 App、凭据、知识库、运行记录） | 第 4 轮起的既有约束 |
| 六份既有 Skill（`content-production/skills/` 3 份 + `decision-chain/skills/` 3 份） | 上位合同 |
| 已冻结的 21 条 AC 判据本体（`M3_ACCEPTANCE_CRITERIA_FROZEN_v1.0.md` §3） | A2 |
| `M3_ECC_*_FROZEN_*.md` 的既有条款 | A2 |

**非目标**：不建通用数据库平台、不建第二套工作流引擎、不做浏览器自动化、不改 M2 合同。

---

## 2. 四条缺陷的修法，写成可被机械核对的判据

### 2.1 `G-3` · 持续位不再从散文里正则抠

**根因（重跑轮判定者定位，比执行侧原写的更准）**：`P1/P2/P3` 这个编号在产品语义里**没有任何依据**，
是执行侧从某一次输出里看到就当成通例写进了正则。`v1.1 §3` 的保护分支因此 12 步 **0 次生效**；
而 `dropped_without_notice` 全程为 `[]` 的同时，8 个对象真丢了 7 个。

**改法**：引入**结构化持续位** `standing_positions[]`，端到端全程结构化，任何一环都不经过散文。

```text
输入侧   account_context 增加一个槽位 standing_positions，值是 JSON 数组，
         由上一步的投影写出，本步用 json.loads 读入。不是自然语言，不需要正则。

输出侧   模型在审计块里增加一段机器行，对输入里的**每一个** position_id 逐条声明：
             POS :: <position_id> :: <continued|disposed|superseded> :: <正文原句锚点>
         新建的持续位用 NEW:<slug> 作为 id，并额外声明 kind。

闸门     确定性比对，零正则：
           a. 输入 standing_positions 的 id 集合  vs  声明覆盖的 id 集合
              少一个 ⇒ 阻断（这一条就是 G-3 的正面挡板）
           b. 每条声明的锚点必须逐字出现在正文里、≥12 字、非空洞、与其他锚点字符区间不相交
              （复用已被 5 轮实证的锚点机制）
           c. 声明了输入里不存在的 id ⇒ 阻断（防编造）

投影     新基线的 standing_positions 由**声明**生成，不由散文重建：
           continued  → 保留该位，last_restated 更新为本步
           disposed / superseded → 移出活动集，写进 disposed_log（不删，可回指）
           NEW:*      → 新增
```

**`dropped_without_notice` 这个字段名与它的旧语义一并废弃。** 新记录字段是
`positions_unaccounted[]`（= 输入里有、声明里没有的 id），**它非空即阻断**，
因此不会再出现"字段全程为空而内容全丢"这种事——空与不空这次真的有区别。

**自证循环也一并堵死**：补齐节点若在正文里引入了原稿没有的概括性延续句
（「其余判断保持不变」一类），投影侧记 `blanket_introduced_by_gate=true`，
**该句不计入模型的连续性履行**。判据能被闸门自己满足，就对模型没有约束力。

### 2.2 `G-2` · 探索触发改由结构判定，且这次两个方向都量

**根因**：为压掉第 4 轮 67/70 误报，把触发收紧成"动作性措辞"；**收紧后量了误报（0/70），没量漏检**。
方法漏，不是运气差。留出场景 03 上「核心命题是……观察窗口至少一周」整句逃逸。

**改法两层**：

```text
第一层（结构，优先）  模型声明的持续位里出现 kind=exploration ⇒ 探索六项必答。
                      这是结构事实，不是措辞匹配。

第二层（措辞，兜底）  仅在第一层未命中时启用，且判据扩为"提案形态"而非"动作词"：
                      同一句段内同时出现 { 假设|核心命题|想验证|观察窗|观察窗口|试点|小范围 }
                      与 { 时长|条数|截止|到期|至少 N 天/周 } ⇒ 判为探索提案。
                      否定极性与条件式否决继续有效（G-1 的修法不回退）。
```

**冻结的方法义务**：本轮夹具必须**同时**给出误报族与漏检族，两族都跑，两个数字都写进记录。
**只报其中一个数字的收紧，本轮不接受。**

### 2.3 `G-4` · 旧值压过当轮权威输入

**根因**：三套机制的方向全是"少了没有"，没有一套管"多了不该多的"。
`E04` 输入槽位逐字 `actual_capacity: 3 条/周`，交付正文写「当前实际产能只有一条（苏禾请假）」，
并以此为承重依据压着两条任务不排。

**改法**：新增 `check_stale_value_override(slots, body)`，只对**能从输入确定性算出值**的槽位生效：

```text
受管槽位   expected_publish_count / baseline_capacity / actual_capacity
主语锚     实际产能|当前产能|本周产能 → actual_capacity
           基线产能|常态产能|正常产能 → baseline_capacity
           目标|期望发布|计划发布     → expected_publish_count
阻断条件   同一句段内  { 主语锚 } + { 现时性词：当前|本周|这周|现在|目前|眼下 } + { 数量 }
           且该数量 ≠ 槽位里的数量
豁免       同句段出现历史性词（上周|上一轮|之前|原来|曾|此前）⇒ 不阻断
           同句段同时逐字引用了槽位原值 ⇒ 不阻断（那是在做对比）
单位换算   按 §3 的等价换算表归一后再比；换算本身不是矛盾
```

**这一条只挡"用旧值压当轮输入"，不挡"解释为什么产能会变"**——后者必须写在输入里才算数。

### 2.4 `G-1` 的修法不回退

`ABSENCE_NEAR` 的双向夹具继续有效并扩充。**"槽位没送到"与"槽位内容里没有某个话题"这两件事，
本轮仍然分得清；任何新判据不得重新把它们混起来。**

---

## 3. `M2-AC-06` 判据的等价换算口径（Founder 第 3 条，逐字落地）

```text
允许   把「每天 3 条」等价换算为「每周约 21 条」，用于同单位比较。目标量不变。
禁止   把「每天 3 条」改写成「每周 3 条」；
       或以其他方式缩小目标量（含把 21 条/周说成 3 条/周、
       把用户目标默认替换为基线产能而不点名这是一次取舍）。
```

更正后的 Oracle 落在**新版本文件** `account-operations/evidence/_oracle/BEHAVIOR_CASES_v2.json`，
带 `oracle_version` 与自哈希，**先冻结、后重跑**。
**第 3 轮与第 5 轮按旧口径产生的运行记录一条不删、一条不改，也不追溯变成正式 `PASS`**——
`AC-06` 的正式判定只由本轮在新 Oracle 冻结之后产生的新运行给出。

---

## 4. M2 接口兼容（Founder 第 2 条）

### 4.1 实测基线

```text
运行中的 diyu-m2-app        /srv/app/app/api/knowledge.py    sha256 69f12b79f72c…
                            /srv/app/app/models/knowledge.py sha256 c39df6296727…
git a7b8101 同两文件         逐字节相同  ⇒ 容器 = main@a7b8101
worktree business-persistence/  仍为 df2c595（**不动它**，M2 真源受保护）
```

`m2_interface_baseline` 由 `main@df2c595` 改绑 **`main@a7b8101`**。

### 4.2 必须保留、不得坍缩的五组语义

| 组 | M2 侧字段 | M3 投影 v1.1 的承载 |
|---|---|---|
| 来源四分 | `source` / `source_type` / `source_reference` / `source_provider` | 四个键分别承载，**不合并成一个 `source`** |
| 当前可用性 | `permission_status` ∈ {allowed, unknown, missing, denied, restricted}，默认 `unknown`，**允许清单制**（只有 allowed/restricted 可用） | `permission.status` 原值 + `permission.currently_usable`（≤ M2 判断） |
| 对外发布权限 | `usage_limits` | `permission.usage_limits` 原值 + `permission.publishable_externally`（**独立第二道闸，永远不由第一道推出**） |
| 适用范围 | `account_id` / `applicable_task_id` / `applicable_period_start` / `applicable_period_end` / `applicable_track` | `applicable_scope` 对象，五键齐全；期间窗取不到时记 `UNKNOWN`，**不记 null** |
| 证据身份 | `evidence_digest`（调用方给，M2 不算） | 原值承载；`null` 与"未知"仍然可区分 |

**另加一条 M2 已经做了而 v1.0 丢掉的**：`/current` 的 `excluded[]` 与 `gap_reason`
（`no_observation_recorded` / `no_observation_in_scope` / `all_observations_excluded`）
必须原样带进投影。丢掉它，"一条都没登记"与"全被排除"就塌成同一个空数组——
这正是 `AC-12` 明确写的 `FAIL` 形态。

### 4.3 边界声明（Founder 第 2 条后半）

本次适配**只改 M3 侧的读取形状**：M2 的接口、字段语义、责任、默认值一个都不动，不发任何写请求。
**若实测证明必须改变 M2 合同或跨出 M3 授权范围，携带具体冲突与最小影响面请求 Rebase，不自行动手。**

---

## 5. A3 影响面核算（不多算，不少算）

### 5.1 因本轮变化而 `STALE` 的

| 项 | 为什么 |
|---|---|
| 第 5 轮全部 82 次运行 | `SKILL.md` v1.2 → v1.3 + 闸门 v12 → v13，模型输入与判定链路都变了 |
| 第 5 轮四份 ECC 判定 | 同上 |
| `AC-12` / `AC-13` 对 `df2c595` 的结构证据 | 投影 schema 由 v1.0 变 v1.1，绑定改绑 `a7b8101`；**旧证据不删**，作为 v1.0 绑定下的历史记录保留 |
| `AC-06` 第 3/5 轮判定 | Oracle 换版本 |

### 5.2 **不**因此失效的（多算即是错）

| 项 | 为什么 |
|---|---|
| `M3_INDEPENDENT_CLOSEOUT_REVIEW_V12_v1.0.md` 的 `R-4`（边界与受保护资产） | 判的是分支变动形态与受保护目录，与闸门实现无依赖边 |
| `R-5`（失败路径只追加不删除） | 同上 |
| 回滚演练 `dify_rollback_drill.json` | 判的是 Dify 对象的备份/恢复能力，不依赖闸门内容 |
| 41 名判定者隔离性核验 | 判的是判定者读了什么，与被判对象无关 |
| `_CASES_PROVENANCE.md` 的七项机械声明 | 关于既有文件哈希的陈述，本轮不改那些文件 |
| `ADDENDUM_003` | 它本身就是为下一轮 A/B 预冻结的判据，本轮生效 |

### 5.3 影响关系无法判断的项

**无。** 上述两栏是按依赖边逐条枚举的，不是推测。

---

## 6. 本轮的运行顺序（Founder 第 5 条，冻结为程序义务）

```text
1. 冻结：本文件 + BEHAVIOR_CASES_v2.json（Oracle v2）      ← 先于任何取证运行
2. 实现：schema v1.1 + projection.py + gate_v13 + SKILL v1.3
3. 六族确定性夹具全部通过：正向 / 负向 / 误报 / 漏检 / 连续性 / 旧值覆盖
   —— 误报与漏检两个数字都必须有，只报一个不接受
4. 冻结最终候选：Dify 发布 + 全部哈希落盘
5. 一次完整正式重跑（保真 9 + 行为 49 + 纵向 12 + A/B 12 = 82）+ 独立判定
6. 对 AC-00～AC-20 按冻结判据与证据重算完整状态
7. 生成与最终 Dify 版本、候选哈希完全绑定的 Founder 实测包
```

**看到正式结果之后不得原地修改判据。** 本轮如再发生一次，按 A2 该轮只算探索。

**上报门槛（Founder 第 5 条逐字）**：新发现只有在**真正改变冻结 AC 结论**或**超出授权边界**时才上报；
其余登记 `NOTE`，不自动开启新一轮。

---

## 7. 事先声明的风险（写在前面，事后不许改口）

1. **`standing_positions` 是新增载体，模型可能不照格式写。** 那就是阻断，交付无效——
   这正是要它的原因。但它会不会把交付质量拖下去，本轮实测才知道。
2. **第二层措辞兜底仍是措辞判据。** 它只在结构层未命中时启用，误报与漏检两个数字都会公开。
3. **投影 schema v1.1 会让 `AC-12`/`AC-13` 的全部结构证据重跑。** 这是预期代价，不是意外。
4. **M2 期间窗（`applicable_period_*`）在 `/current` 的最小投影里不返回。** 取不到就记 `UNKNOWN`，
   不猜、不填 null。这会让"期间适用范围"这一条在 `/current` 路径上只能部分成立——如实记，不美化。

```text
END_MARKER = M3-ECC-REBIND-004-FROZEN-v1.0-END
```
