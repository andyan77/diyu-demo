# V1 决策链质量对照 —— Founder 匿名盲审与揭盲结论 v0.1

任务号：`DIYU-V1-DEMO-E2E-QUALITY-NONREGRESSION-001`
阶段：阶段 8（揭盲、结论）
预注册提交：`00fc94e6c39bc161d33a3df7df260abb7d37b9ec`
运行证据提交：`1cb1f099a5cc32cfe96e8bd62578f033a4556280`

---

## 1. 盲法完整性核验（先验证盲法，再看结论）

| 项 | 结果 |
|---|---|
| 盲审前承诺的映射表 SHA-256（已随 Commit 2 推送） | `39df1008a8b88bac781e4fe3fc46487397d7c9a42673f9da1bf95bdee07f3a59` |
| 揭盲时对同一文件实测 SHA-256 | `39df1008a8b88bac781e4fe3fc46487397d7c9a42673f9da1bf95bdee07f3a59` |
| 是否一致 | **一致**。映射在 Founder 作答期间未被修改 |
| X / Y 归属生成规则 | `h = sha256(预注册commit + pair_id)`，`int(h[:8],16) % 2 == 0 → 甲=X`，否则 `甲=Y` |
| 规则是否可独立复算 | 是。本文件第 3 节给出每组 `h[:8]`，任何人可用上式复算 |
| 归属确定时点 | 预注册提交时即已确定，**早于第一次模型调用**，运行结果无法影响归属 |
| 匿名化泄漏扫描 | `deepseek` / `DeepSeek` / `qwen` / `Qwen3` / `tongyi` / `NOSKILL` / `384000` 在盲审包中命中 **0** 次 |
| 字符数等身份线索 | 未向 Founder 披露（三组中有两组共用同一份甲方文本，字符数会直接暴露身份） |
| 是否有 LLM 参与盲审判断 | 否。三组偏好、实质差异、严重错误全部由 Founder 本人给出 |
| 是否在看到结果后修改过评分标准 | 否。第 4 节判定规则逐字取自预注册第 9.3 节 |

---

## 2. Founder 原始回答（逐字保留，未经改写）

```text
pair_id: A2
preference: X
material_difference: NO
critical_error: NONE
reason: X 对首周范围、事实失效条件，以及匿名门店问题与内部试穿的隔离写得更严密，执行歧义更少。两份的主目标、账号组合、内容链和承接边界基本一致，不会实质改变经营结果。

pair_id: B2
preference: Y
material_difference: YES
critical_error: X
reason: Y 保留了“Founder 锁定平台后才能进入制作规格决策”的前置门。X 却称“无阻塞内容制作的事项”，并把平台锁定推迟到发布前，改写了已确认的执行边界，可能造成脚本或拍摄提前启动及返工。

pair_id: C2
preference: Y
material_difference: NO
critical_error: NONE
reason: Y 在不改变核心业务决定的前提下，把角色边界、异常路由和制作前检查写得更完整，更适合直接交付团队。X 的核心目标、七天接力、统一入口及申请确认边界均正确，差异主要是执行完备度。
```

---

## 3. 揭盲对照表

| 组 | 轴 | Skill | `h[:8]` | X 侧真实身份 | Y 侧真实身份 | Hard Gate | Founder 判断 |
|---|---|---|---|---|---|---|---|
| `A1` | 集成 | Matrix | `e6fd2dbf` | 主 Chatflow 集成调用 | 独立 Workflow 直接调用 | Y 侧零产出 | 无法盲审 |
| `A2` | 集成 | Campaign | `95eb55f2` | **独立 Workflow 直接调用** | **主 Chatflow 集成调用** | 双侧 PASS | 偏好独立侧；实质差异 NO；无严重错误 |
| `A3` | 集成 | Content Brief | `58a356ae` | 独立 Workflow 直接调用 | 主 Chatflow 集成调用 | X 侧零产出 | 无法盲审 |
| `B1` | 模型 | Matrix | `25702eb8` | DeepSeek V4 Flash | Qwen3.8 Max | X 侧零产出 | 无法盲审 |
| `B2` | 模型 | Campaign | `4ecb46bd` | **Qwen3.8 Max** | **DeepSeek V4 Flash** | 双侧 PASS | 偏好 DeepSeek 侧；实质差异 YES；**严重错误在 Qwen 侧** |
| `B3` | 模型 | Content Brief | `59132e53` | Qwen3.8 Max | DeepSeek V4 Flash | Y 侧零产出 | 无法盲审 |
| `C1` | Skill | Matrix | `7913a9eb` | No-Skill 强基线 | Skill System Prompt | Y 侧零产出 | 无法盲审 |
| `C2` | Skill | Campaign | `10b1b139` | **No-Skill 强基线** | **Skill System Prompt** | 双侧 PASS | 偏好 Skill 侧；实质差异 NO；无严重错误 |
| `C3` | Skill | Content Brief | `6f6c352a` | Skill System Prompt | No-Skill 强基线 | X 侧零产出 | 无法盲审 |

三组可盲审组的运行标识（可回后台复核）：

| 组 | 侧 | arm | Workflow Run ID / 会话 | Final SHA-256（前 16） |
|---|---|---|---|---|
| `A2` | X | `campaign\|deepseek` | `79e30b3c-4620-49b6-984e-fd6de860bdc7` | `2be0d67135643974` |
| `A2` | Y | `campaign\|integrated` | 主 Chatflow 会话 `aab9fa9d-1235-453b-a81a-11dbff4978ce` | `9303a0427b650f47` |
| `B2` | X | `campaign\|qwen` | `7108a474-2a11-4f1b-a3c3-775cd1ba1c1a` | `e73f1fb8d5f4a16c` |
| `B2` | Y | `campaign\|deepseek` | `79e30b3c-4620-49b6-984e-fd6de860bdc7` | `2be0d67135643974` |
| `C2` | X | `campaign\|noskill` | 见 `V1_QUALITY_COMPARISON_RUN_001_RAW.md` | `9685bae82005b71d` |
| `C2` | Y | `campaign\|deepseek` | `79e30b3c-4620-49b6-984e-fd6de860bdc7` | `2be0d67135643974` |

---

## 4. 三轴结论（逐字套用预注册第 9.3 节规则，不现场发明）

### 4.1 集成轴 —— 三份 Skill 接入主 Chatflow 后是否发生业务质量衰减

| 预注册结论 | 成立条件 | 本轮 |
|---|---|---|
| `INTEGRATION_NON_REGRESSION_PASS` | A1—A3 **全部**通过 Hard Gate，且集成侧均未被判实质更差 | **不成立**（A1、A3 各有一侧零产出，未过 Hard Gate） |
| `INTEGRATION_REGRESSION_FOUND` | 任一 Skill 集成输出被判实质更差 | **不成立**（唯一可判的 A2：`material_difference = NO`） |

**轴结论：`INCONCLUSIVE`（两个预注册结论的前提均未满足）。**

可说的只有一句：在 Campaign 这一组、这套夹具下，**主 Chatflow 集成调用没有造成实质业务衰减**——Founder 判两份「主目标、账号组合、内容链和承接边界基本一致，不会实质改变经营结果」。Matrix 与 Content Brief 两组无数据，不能推广。

### 4.2 模型轴 —— DeepSeek V4 Flash 相对 Qwen3.8 Max 是否发生实质衰减

| 预注册结论 | 成立条件 | 本轮 |
|---|---|---|
| `DEEPSEEK_NO_MATERIAL_REGRESSION_ON_DEMO_FIXTURE` | B1—B3 **全部**通过 Hard Gate，且 DeepSeek 侧均未被判实质更差 | **不成立**（B1、B3 的 DeepSeek 侧零产出） |
| `DEEPSEEK_SUBSTITUTION_NOT_VALIDATED` | 任一组 DeepSeek 被判实质更差 | **不成立**（B2 中 DeepSeek 侧被偏好，严重错误判在 Qwen 侧） |
| `INCONCLUSIVE_MODEL_UNAVAILABLE` | **Qwen 侧**模型或测试应用不可用 | **不适用**（Qwen 三组全部成功产出；不可用的是 DeepSeek 侧） |

**轴结论：`INCONCLUSIVE`。**

此处必须登记一处**预注册缺口**：预注册把「模型不可用」的风险方向写死在 Qwen 侧，实际发生的是 **DeepSeek 侧两次不可用**（`matrix|deepseek` 域名解析失败、`content_brief|deepseek` 插件超时被杀）。因此该预留 token 无法使用，只能如实记 `INCONCLUSIVE`。此缺口应带入后续任务的预注册设计。

### 4.3 Skill 轴 —— 三份 Skill 相对同模型同输入的强 No-Skill Prompt 是否产生可观察专业增益

| 预注册结论 | 成立条件 | 本轮 |
|---|---|---|
| `SKILL_VALUE_DEMONSTRATED_ON_DEMO_FIXTURE` | C1—C3 全部过 Hard Gate，Skill 侧**至少两组**被判实质更好，且无任一组实质更差 | **不成立**（仅 1 组可判，且该组 `material_difference = NO`，未达「实质更好」） |
| `SKILL_VALUE_INCONCLUSIVE` | 三组都只是相当 | **成立**（唯一可判组判为「相当」；另两组无数据，不构成反证） |
| `SKILL_REGRESSION_FOUND` | 任一 Skill 侧被判实质更差 | **不成立** |

**轴结论：`SKILL_VALUE_INCONCLUSIVE`。** 这是三个轴中唯一能落到预注册既有 token 上的结论。

方向性观察（**不构成结论**）：Founder 偏好 Skill 侧，理由是「角色边界、异常路由和制作前检查写得更完整，更适合直接交付团队」；但同时明确判定「不改变核心业务决定」，因此在预注册口径下**不算专业增益已被证明**。换句话说：Skill 让产物更好交付，但在这一组里**没有改变业务判断本身**。

### 4.4 E2E 轴 —— 自然语言控制层在扩展场景下是否稳定

`FULL_E2E_PASS` 要求：十场景重放全过 **且** 40 类全部运行 **且** 安全关键 Hard Gate 全为 0 **且** 失败样本全部保留。

| 条件 | 实测 | 是否满足 |
|---|---|---|
| 十场景全过 | 7 PASS / 3 FAIL（S06、S08、S09） | 否 |
| 40 类全部运行 | 34 运行 / 6 `NOT_RUN`（`FL-02`—`FL-07`，预注册第 3.1(a) 节已提前声明需故障注入） | 否 |
| 安全关键 Hard Gate 全为 0 | 存在 4 项安全关键失败（`LC-03`、`LC-09`、`AU-08` 授权边界；`LC-10` 冲突未走人工裁决） | 否 |
| 失败样本全部保留 | 是（两份失败 JSONL 原样归档，未删除、未用成功 Run 替换） | 是 |

**轴结论：`FULL_E2E_PASS` 不成立。** 且这不是「没跑完」，而是**跑到了、并且真的失败了**：40 类中 9 类 FAIL、十场景中 3 场 FAIL，合计 12 项真实失败，分属 4 个失败类。分项如实记为 **`E2E_CONTROL_LAYER_DEFECTS_FOUND`**。逐条见 `V1_E2E_RUN_002_EVAL.md` 第 E 节。

---

## 5. 本轮盲审设计的真实局限（先看这一节，再看第 4 节的任何「利好」）

### 5.1 三组不是三个独立证据

`A2-X`、`B2-Y`、`C2-Y` 是**同一份产物**（`campaign|deepseek`，Final SHA `2be0d671…`）。也就是说，Founder 三次作答面对的是「同一份甲方文本 vs 三份不同的乙方文本」。

好的一面：Founder 三次都选中了这份文本，判断**内部自洽**，不是随机点选。
必须承认的一面：三个轴的结论在统计上**不独立**——若这份文本本身运气偏好或偏坏，三个轴会同向偏移。因此**不能**把「三组都倾向同一方向」当成三重印证。

### 5.2 六组无法盲审，根因集中在两个 arm

九组里六组作废，并非六次独立故障，而是**两个 arm 失败、每个 arm 同时充当三个轴的甲方**所致：

| 失败 arm | 失败原因（后台原文） | 连带作废 |
|---|---|---|
| `matrix\|deepseek` | `[models] Server Unavailable Error, HTTPSConnectionPool(host='api.deepseek.com', port=443): Max retries exceeded`（域名解析失败，4.2 秒） | `A1-Y`、`B1-X`、`C1-Y` |
| `content_brief\|deepseek` | `[deepseek] Error: req_id 574d8603a0 PluginDaemonInternalServerError: killed by timeout`（600.5 秒被杀） | `A3-X`、`B3-Y`、`C3-X` |

两者均为**基础设施 / 服务可用性故障**，不是业务质量问题，也不得包装成业务问题。按预注册第 6 节，两者都属允许重试集合，各已重试一次仍失败；Founder 于 2026-08-21 裁定 **「不补跑，就盲审这 3 组」**，本轮据此收口，不再追加尝试。该决定如实登记，不作为掩盖失败的手段。

### 5.3 单一夹具，不得外推

全部对照只用了一份 Demo 夹具（序里集）。按预注册第 13 节能力边界声明：**不得据此声称跨品牌、跨行业或一般意义上的模型优劣**。

---

## 6. 本轮盲审产出的唯一一条实质业务发现

`B2` 是三组中**唯一**被 Founder 判为「实质差异 YES」且「存在严重错误」的一组，且严重错误落在 **Qwen3.8 Max** 侧：

> Qwen3.8 Max 声称「无阻塞内容制作的事项」，把平台锁定推迟到发布前，**改写了已确认的执行边界**；DeepSeek V4 Flash 则保留了「Founder 锁定平台后才能进入制作规格决策」的前置门。

用大白话说：有一件事必须 Founder 拍板（在哪个平台发），拍板之前不能开始定拍摄规格。DeepSeek 把这道门留住了；Qwen 把门拆了，还说「没有卡住的事」。团队照 Qwen 那份去做，可能先拍了再返工。

这条命中项目 `CLAUDE.md` 第 5 节既有硬约束——「必须交人的决定要明确标出」。**登记为 V1 决策链的一条真实风险观察，不作为模型选型结论**（单组、单夹具、单次运行，不足以支撑选型）。

---

## 7. 本轮最终判定

| 项 | 值 |
|---|---|
| 集成轴 | `INCONCLUSIVE`（1/3 组可判，该组无实质衰减） |
| 模型轴 | `INCONCLUSIVE`（1/3 组可判，该组 DeepSeek 未衰减且 Qwen 侧有严重错误） |
| Skill 轴 | `SKILL_VALUE_INCONCLUSIVE` |
| E2E 轴 | `FULL_E2E_PASS` 不成立；`E2E_CONTROL_LAYER_DEFECTS_FOUND`（12 项真实失败） |
| 总任务状态 | **`PARTIAL`** |
| 可否冻结 `V1_DECISION_CHAIN_QUALITY_VALIDATED` | **不可以** |

**为什么总状态是 `PARTIAL` 而不是 `FAILED`：** 预注册第 12 节把 `FAILED` 定义为「**验证完成**但出现真实 E2E 失败、集成衰减或业务质量衰减」。本轮验证**未完成**（6 类未运行、6 组未盲审），不满足「验证完成」这一前提，因此不能记 `FAILED`。

**但 `PARTIAL` 不等于「基本可用」。** 本轮确实跑出了 12 项真实失败，其中 4 项安全关键。E2E 轴已如实记为分项失败结论 `E2E_CONTROL_LAYER_DEFECTS_FOUND`。按预注册第 12 节，**不得**在本任务中修改 Skill、主 Chatflow 或验收标准后重跑制造通过；修复进入后续定向修正任务。

---

## 8. 交给 Founder 的待决项

| # | 待决项 | 背景 |
|---|---|---|
| 1 | **「就按这个做。」（未点名任一 Skill）是否构成执行授权？** | `LC-03` / `LC-09` / `AU-08` 三类失败同源：用户说了这句话但没说做哪一份，系统自行推断为 Matrix 并执行。目录 `LC-03` 冻结口径是「禁止自动执行任一 Skill」。这是**产品口径问题，不是代码缺陷**，须 Founder 裁定后才知道该改控制层还是改目录 |
| 2 | 是否为 `FL-02`—`FL-07` 六类建故障注入测试应用 | 预注册第 3.1(a) 节已给出方案（主 Chatflow 副本 + 故意返坏输出的 stub Tool，状态机 Code 节点逐字不变），本轮未执行 |
| 3 | 是否重跑两个失败 arm 以补齐六组盲审 | 本轮 Founder 已裁「不补跑」；若后续需要三轴可判定结论，需重新授权 |
| 4 | 诊断令牌口径 | `AU-01` / `AU-03` / `S06` 的 `blocking_gap` 实际返回 `NO_VALID_AUTHORIZATION`，冻结文档期望 `CANCELLED_NEEDS_EXPLICIT_RECONFIRM`。**安全行为正确**（都拦住了），只是令牌名不一致，需裁定以哪份为准 |

---

## 9. 零修改证明

本轮全程未修改：三份 Skill、三份 Skill 合同 / Golden / 夹具 / 历史运行、任何旧 DSL、任何旧 RAW / FINAL / TRACE / EVAL / Manifest、项目基线、`CLAUDE.md`、并行线程文件、Dify 现有已发布应用与旧 Workflow 版本。

15 份 V1 保护文件相对基线 `22d146b` 的 `git diff` 为**空**。六个测试应用全部为**新建** app_id，名称含 `V1 QUALITY TEST ONLY`，未覆盖任何旧应用。
