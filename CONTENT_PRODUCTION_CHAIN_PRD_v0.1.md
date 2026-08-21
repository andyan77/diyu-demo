# CONTENT_PRODUCTION_CHAIN_PRD v0.1

> 本文件是笛语「内容生产链 V1」的产品定义，由任务 `CONTENT-PRODUCTION-P01` 落盘，
> 作为 P02—P09 的唯一上游施工基线。
>
> 本文件是治理文件，不是模型输入。它不进入 Skill、不进入 Dify System Prompt、
> 不进入 User Prompt、不进入任何固定运行输入。
>
> 本文件不修改、不替代、不重新解释已经落盘的 `Matrix Architect`、`Campaign Orchestrator`
> 与 `Content Brief Architect` 三份 Skill 及其合同。
>
> 配套文件：
> [`CONTENT_PRODUCTION_CHAIN_CONTRACT_v0.1.md`](CONTENT_PRODUCTION_CHAIN_CONTRACT_v0.1.md)、
> [`CONTENT_PRODUCTION_RESEARCH_PROTOCOL_v0.1.md`](CONTENT_PRODUCTION_RESEARCH_PROTOCOL_v0.1.md)。

---

## 1. 文档身份、状态与适用阶段

| 项 | 值 |
|---|---|
| 文件名 | `CONTENT_PRODUCTION_CHAIN_PRD_v0.1.md` |
| 版本 | `v0.1` |
| 状态 | `FROZEN_FOR_P02_P09` |
| 落盘任务 | `CONTENT-PRODUCTION-P01` |
| 落盘日期 | `2026-08-21` |
| 适用阶段 | `P01`—`P09` |
| 文件性质 | 治理文件 / 产品定义，非模型输入、非运行时工程设施 |
| 落盘分支 | `feature/content-production-chain-v1` |
| 基线 Commit | `349673b76fc46a3ffc5170344956297d24017e7c` |

### 1.1 本文件负责什么

定义内容生产链 V1 的目标、边界、职责划分、共享前置合同、产物关系与完成标准，
使 P02—P09 的执行者不必从聊天记录、历史线程或研究报告中推测产品定义。

### 1.2 本文件不负责什么

- 不编写任何一份 Skill；
- 不定义 Dify 节点编排、DSL、模型参数；
- 不给出任何一条具体脚本、分镜、标题、封面或发布文案；
- 不代替 P02—P04 的行业研究结论；
- 不代替 Founder 对 P02—P04 研究结果的集中裁决。

### 1.3 真源优先级

本文件依据以下顺序成立，低优先级不得覆盖高优先级：

1. `CONTENT-PRODUCTION-P01` Prompt 中列出的 Founder 已确认决定；
2. 仓库中已冻结的正式产品合同（`CONTENT_BRIEF_CONTRACT_v0.1.md`）；
3. 已确认的 `Matrix Architect`、`Campaign Orchestrator`、`Content Brief Architect`
   三份 Skill 及 `C1`—`C6` Founder 确认稿、四张账号责任卡与两份夹具；
4. 任务开始时有效的 `origin/main`；
5. 本任务要求；
6. 历史讨论、参考材料与旧版本文件。

---

## 2. 背景与当前能力断点

### 2.1 当前已经具备的能力

仓库已经落盘并真实运行过三份内容决策 Skill，构成一条可用的编译链：

```text
企业事实与夹具
→ Matrix Architect        企业该设哪些 IP 账号、每个人设为什么存在
→ Campaign Orchestrator   一次经营任务里谁说什么、怎么配合
→ Content Brief Architect 单条内容的顾客问题、证据链、必须形成的新判断
```

该链条已经有真实运行证据：`CONTENT_BRIEF_DEEPSEEK_V4_FLASH_RUN_001_FINAL.md`
在 `deepseek-v4-flash` 上产出了两条独立 Brief（`BRF-SUHE-001`、`BRF-ZHOUNING-002`），
顶层状态 `READY_WITH_CONDITIONS`，并配有负向探针与运行 Manifest。

### 2.2 断点一：Content Brief 之后没有承接者

`Content Brief Architect v0.1` 第 5 节明确规定它**不得输出**：

> 完整逐句口播稿、完整对白、逐镜头编号、每个镜头的景别机位运动与秒数、
> 最终标题、最终封面文案、完整图文正文、最终发布文案、成片字幕全文。

它的每条 Brief 以第 25 个字段 `进入脚本与拍摄设计前必须确认的事项` 结束。

也就是说：编译链在「制作依据已经写清楚、但没有任何能力接手把它变成可拍可发的东西」处停止。
这不是缺陷，是当时的正确边界；但它意味着**当前系统交付的最后一件东西不是可执行物**。

真实运行也已经把这个断点量化出来。
`CONTENT_BRIEF_DEEPSEEK_V4_FLASH_RUN_001_EVAL.md` 记录：10 个 Hard Gate 全数通过、
七维质量总分 86（阈值 80）判为 `ACCEPT`，其中**最低分维度是「创意张力与叙事推进」15/20**，
扣分理由 verbatim：

> 张力偏概念化，缺少能被观众记住的具体对峙点；“下班接孩子”这一最有生活质感的情境
> 在 Brief 中基本停留为场景标签，没有被用作叙事燃料；两条的进入点都是“事实陈述式”，
> 未给出更有代入感的进入方式建议。

这正是 Content Brief **按合同不该做**、而目前**没有任何能力接手**的那一层。
它是内容生产链要补的第一个能力，也是 P02 研究的直接靶子。

### 2.3 断点二：制作条件从未被建模

现有 Brief 的「制作要求」只是一句自然语言，例如
「一次 3 小时集中拍摄＋30 分钟补录」「周宁两次各 1 小时集中拍摄」。

系统没有统一口径回答：

- 用户希望怎么做，与当前真实能做到什么，差在哪里；
- 最低能跑起来的方式是什么；
- 条件不足时应当降级到哪一档，而不是直接失败；
- 一份脚本是否已经超出当前可执行范围。

结果是创意与制作资源脱钩：要么生成纸面大片，要么把资源限制当成事后借口。

同一份 `_EVAL` 的「6. 制作可执行性」维度（15 分得 13）也记录了这一层的缺口，
扣分理由 verbatim：

> 制作要求未给出任何内容体量或结构密度的量级判断（平台未确认并不妨碍给出这一层）；
> “周宁出镜时是否仅讲解或结合商品实物”本属制作层可决策事项，被推给了下一步确认。

「本属制作层可决策事项，被推给了下一步确认」——而下一步当前**不存在**。
这是 P03 Production Director 的直接靶子。

### 2.4 断点三：平台、行业与趋势知识没有承载体

平台官方规则、头部与同类 IP 做法、当前有效的内容基准、未来趋势判断，
目前既没有分级，也没有存放位置。

只有两条同样错误的出路：塞进 `SKILL.md` 变成硬规则，或依赖通用模型常识冒充专家资产。
《笛语项目基线》已经明确：普通文案知识与短视频常识**不因被提及就成为专家资产**。

### 2.5 断点四：产物之间的关系不可追踪

脚本、制作包、发布包三者存在真实依赖：上游变了，下游可能已经失效。
当前没有任何口径说明「哪一份还算数、哪一份必须重看」。

---

## 3. 产品目标

内容生产链 V1 要达成五件事：

1. **归属确定**：Content Brief 之后的三段制作决策各有唯一负责 Skill，职责不可互换、不可代做。
2. **资源前置**：制作条件在创意开始前被声明为合同，成为创意的约束，而不是事后解释。
3. **知识分级**：平台规则、行业观察、专家判断、模型推演与未来趋势按等级分开存放，
   按需读取，不自动进入正式事实，也不自动变成 Skill 硬规则。
4. **关系可追**：脚本、制作包、发布包形成父子引用与失效传播，人能判断哪一份还算数。
5. **成立可验**：「内容生产链 V1 是否成立」有可验收的完成定义，而不是感觉上完成。

### 3.1 生死题

依《笛语项目基线》第一节的新功能生死题——「企业为什么不能直接用 GPT 项目文件夹完成？」——
内容生产链的回答是：

- 生产链继承的是**本企业已经确认的经营决策与事实责任链**，不是一次性提示词；
- 它受**本企业当前真实制作资源**约束，会主动降级而不是生成纸面大片；
- 它的表达边界来自**已确认的账号人格与承接口径**，不是通用文案风格；
- 上游改变时，它知道**哪一份产物失效**。

以上四点通用工具无法稳定提供。若某项能力答不上这道题，该能力不做。

---

## 4. 用户与核心使用流程

### 4.1 用户

| 角色 | 在生产链中的位置 |
|---|---|
| 经营决策人（Founder） | 提供并确认经营决定、正式品牌立场与对外承诺；裁决升级事项；接受或退回产物 |
| 内容负责人 | 提供账号一手事实；确认脚本与包装是否符合本账号判断责任 |
| 事实确认人 | 确认内容涉及事实的准确性与可公开范围 |
| 制作执行（拍摄／剪辑） | 声明真实可用制作条件；执行制作包；反馈条件变化 |

系统不替上述任何角色承担责任。是否拍、是否发、是否回复评论，仍由人决定。

### 4.2 核心使用流程

```text
已被接受的 Content Brief（单条内容单元）
→ 声明 Production Profile（用户希望什么 / 当前真实有什么）
→ Production Feasibility Gate（可行 / 降级可行 / 需补资源 / 不可行）
→ Creative Script Architect      → 可接受的完整脚本
→ Production Director            → 可执行的拍摄、声音、剪辑制作包
→ Publishing & Packaging Architect → 与成片状态匹配的发布包装
→ 人工确认与接受
→ 人执行拍摄、剪辑、发布（系统不自动执行）
```

三段之间不是自由跳转：后一段只能消费前一段已被接受的产物，
不能跳过、不能倒写、不能替前一段重做判断。

### 4.3 永不自动发布

依《笛语项目基线》第四节长期裁决：**永不自动发布，人在回路**。
内容生产链 V1 的终点是「可发布的包装」，不是「已发布」。

---

## 5. 内容决策链与内容生产链的关系

### 5.1 完整业务主链

```text
Matrix Architect
→ Campaign Orchestrator
→ Content Brief Architect
→ Production Profile 与 Production Feasibility Gate
→ Creative Script Architect
→ Production Director
→ Publishing & Packaging Architect
```

前三份是**内容决策编译链**（已落盘，本轮不修改）。
后三份是**内容生产链核心 Skill**（本轮待建设）。
中间的 Production Profile 与可行性门是三份生产 Skill 的**共享前置合同**，不是第四份 Skill。

### 5.2 两条链的分工

| | 内容决策链 | 内容生产链 |
|---|---|---|
| 回答 | 做不做、做什么、为什么、由谁做、接不接得住 | 怎么说出来、怎么拍出来、怎么发出去 |
| 产物 | 责任卡、Campaign 决策包、Content Brief Pack | 脚本、制作包、发布包装 |
| 对事实的关系 | 选择、确认与分配事实责任 | 使用已确认事实，不新增事实 |
| 对资源的关系 | 判断资源是否支持发布决定 | 在已声明资源内完成制作决策 |

### 5.3 生产链只能继承，不能重开决策

生产链**不得重新决定**决策链已经确认的任何一项。发现更优方案时，
只能写入产物的「进入下一环节前必须确认的事项」，由人决定是否回到上游。

需要回到上游时，沿用 `C6_FOUNDER_CONFIRMED_v0.1.md` 已确认的
**最上游实际失效结论回退原则**：先判断新事实究竟破坏了哪一个已确认结论，
再返回其中最上游的一项重新判断，只重新判断实际受影响的下游结论，
不从头重跑全部上游。

---

## 6. 三份生产 Skill 与不可互换职责

### 6.1 职责总表

| Skill | 唯一任务 | 输入 | 产物 |
|---|---|---|---|
| Creative Script Architect | 把一条已接受的 Content Brief 编译成可拍摄的完整脚本 | Content Brief + 已接受 Production Profile | Creative Script |
| Production Director | 把一份已接受的脚本编译成可执行的制作包 | Creative Script + 已接受 Production Profile | Production Package |
| Publishing & Packaging Architect | 把已完成或已确定状态的成片编译成可发布的包装 | Production Package + 成片状态或成片夹具 | Publishing Package |

### 6.2 Creative Script Architect

**负责**：核心创意命题；内容钩子；叙事结构；真实摩擦；逐句口播；对白、旁白与屏幕文字；
账号人格与关系姿态；口语化；事实引用位置；内容节奏；可拍摄脚本。

内容形态为轻量图文时，同一职责表现为**完整图文正文**——它与逐句口播同层，
都是「这条内容本身要说什么」。形态适配见
[`CONTENT_PRODUCTION_CHAIN_CONTRACT_v0.1.md`](CONTENT_PRODUCTION_CHAIN_CONTRACT_v0.1.md) 第 2.6 节。

**不得**：

- 改变已经确认的 Campaign 或 Content Brief 决定；
- 重新选择主讲人或目标顾客变化；
- 负责详细分镜与现场执行；
- 负责最终标题、封面与发布包装。

### 6.3 Production Director

**负责**：分镜与镜头清单；人物动作与表演提示；场景、商品与道具；收音、配音、音乐与音效；
字幕与屏幕信息；剪辑节奏；必拍、可选与可删除素材；拍摄日执行计划；制作条件不足时的降级方案。

**不得**：

- 重写脚本核心判断；
- 补写企业事实；
- 自动增加人员、场地、设备或预算；
- 生成明显超出 Production Profile 的纸面大片。

### 6.4 Publishing & Packaging Architect

**负责**：候选标题及适用条件；封面信息层级；发布文案；关键词、话题与必要标签；置顶评论；
CTA；平台规格适配；发布前检查；包装与真实成片状态不匹配时的退回意见。

**不得**：

- 改写核心事实；
- 改变品牌立场；
- 以夸张包装弥补正文不足；
- 在平台未确认时伪装成平台定制；
- 新增未经确认的承接承诺。

### 6.5 三条排他性判据

职责划分成立与否，用以下三条检验，任一不成立即为越界：

1. **口播归脚本，镜头归导演**：逐句说什么由 Creative Script 决定；这句话怎么拍、几个镜头、
   什么景别由 Production Director 决定。Creative Script 写出景别机位秒数即越界；
   Production Director 改写台词判断即越界。
2. **正文归前两段，包装归第三段**：内容本身说了什么由脚本与制作包决定；
   标题、封面、发布文案、标签、以及 CTA 的**具体措辞与位置**由
   Publishing & Packaging 决定。
   前两段写最终标题即越界；第三段改正文事实或立场即越界。

   注意：**有没有 CTA 是 Content Brief 已锁定的上游决定**，
   Publishing & Packaging 只能在该决定之内写措辞，不得自行改成有或没有。
   易混交付项的完整切分见
   [`CONTENT_PRODUCTION_CHAIN_CONTRACT_v0.1.md`](CONTENT_PRODUCTION_CHAIN_CONTRACT_v0.1.md)
   第 2.7.1 节。
3. **谁都不能新增事实**：三份 Skill 都只能使用上游已确认事实。任何一份补写
   商品性能、顾客反馈、经营结果或对外承诺，都是同一类越界，不因所处环节不同而被允许。

### 6.6 与已落盘 Skill 的边界

`Content Brief Architect v0.1` 第 5 节拒绝输出的九项，正是**三份生产 Skill** 的职责范围：
逐句口播、对白与图文正文归 Creative Script；逐镜头编号、景别机位秒数与成片字幕全文归
Production Director；最终标题、最终封面文案与最终发布文案归 Publishing & Packaging。

九项逐项归属对照见
[`CONTENT_PRODUCTION_CHAIN_CONTRACT_v0.1.md`](CONTENT_PRODUCTION_CHAIN_CONTRACT_v0.1.md)
第 2.7 节，该表要求九项零遗漏、零重叠。

两条链不重叠、不冲突，是同一条边界的两侧。本轮不修改 Content Brief Architect 的任何表述。

---

## 7. Production Profile 与 Production Feasibility Gate

### 7.1 它不是第四份 Skill

Production Profile 与 Production Feasibility Gate 是三份生产 Skill 的**共享前置合同**，
不单独建设为大型 Skill。理由：

- 它不产生内容判断，只声明条件与判断条件是否成立；
- 三份 Skill 都要读它，如果做成独立 Skill 就会出现四段串行、三次重复解释；
- 它的内容主要由**人声明**（真实有几个人、几台设备、多少小时），不由模型推断。

### 7.2 五个模式字段

| 字段 | 含义 | 由谁给出 |
|---|---|---|
| `requested_mode` | 用户希望的制作方式 | 用户声明 |
| `available_mode` | 当前真实可用条件 | 用户／制作执行声明 |
| `minimum_viable_mode` | 最低可运行方式 | 系统据已声明证据给出建议，人确认后写入 |
| `recommended_mode` | 系统推荐方式 | 系统据已声明证据给出建议，人确认后写入 |
| `accepted_mode` | 用户最终接受方式 | 用户裁决 |

`accepted_mode` 是三份 Skill 生成时唯一可以据以工作的模式。

未形成 `accepted_mode`（记为 `NOT_ACCEPTED`）时，各段的门不同，
以 [`CONTENT_PRODUCTION_CHAIN_CONTRACT_v0.1.md`](CONTENT_PRODUCTION_CHAIN_CONTRACT_v0.1.md)
第 5 节为准：

- Creative Script **可以**生成，但顶层状态最高为 `READY_WITH_CONDITIONS`；
- Production Director **不得**生成详细分镜与拍摄日执行计划；
- Publishing & Packaging **不得**生成发布包装。

### 7.3 双轴制作模式

**Capture Mode（拍摄方式轴）**

| 值 | 含义 |
|---|---|
| `ASSET_REUSE` | 不新增拍摄，只使用已有素材 |
| `SOLO_MOBILE` | 一人自拍自录 |
| `LEAN_MOBILE_TEAM` | 小规模团队 |
| `STANDARD_TEAM` | 常规制作团队与常规设备 |
| `CAMPAIGN_PRODUCTION` | 战役级制作，含外部人员、场地或预算 |

**Augmentation Mode（增强方式轴）**

| 值 | 含义 |
|---|---|
| `NONE` | 不使用生成式增强 |
| `AI_ASSISTED` | 使用生成式能力辅助，不替代真实素材 |
| `AI_HYBRID` | 真实素材与生成素材混合成片 |

两轴独立取值，组合使用。`Augmentation Mode` 不为 `NONE` 时，
必须同时声明生成内容的标注方式与不得生成的对象；不得用生成素材冒充真实拍摄事实。

### 7.3.1 这两套枚举是本轮新增建模词

`Production Profile`、`Capture Mode`、`Augmentation Mode`、`Production Feasibility Gate`
及其全部取值，以及 `Artifact`／「产物」这一说法与五个 Artifact 状态
（`DRAFT`／`VALIDATED`／`USER_ACCEPTED`／`STALE`／`FAILED`），
在本任务之前的仓库中**零命中**，没有任何既有真源。

仓库既有的近义词是「冻结件」「归档文件」「提取件」「证据」「资产」，
它们描述的是归档形态，不描述新鲜度，无法承担失效传播。

以上词由 `CONTENT-PRODUCTION-P01` 的 Founder 已确认决定引入，属**新增建模词**，
不得被描述为既有约定，也不得回写进任何历史文件。

**重要口径**：夹具从未登记拍摄设备、器材、灯光、收音或可拍摄场地。
因此枚举名中的「MOBILE」只是档位名称，**不构成「已确认使用手机拍摄」的事实**。

由此产生一条硬规则：

> `requested_mode` 与 `available_mode` 是**事实声明**，必须由人声明，
> 不得由系统从夹具推断。
>
> `minimum_viable_mode` 与 `recommended_mode` 是**据已声明事实的推导建议**，
> 系统可以给出，但要由人确认后才写入 Profile。
>
> `accepted_mode` 是**人的裁决**，只能由人给出。

系统可以据已登记事实提示证据（例如资源夹具第八节登记了
「1 名拍摄与现场执行」「1 名剪辑，可同时承担基础字幕和封面」
「当前没有额外预算用于外部演员、场地和大型制作」），
但把这些证据折算成哪一档 `Capture Mode`，是人的声明，不是系统的结论。

未获声明时，`available_mode` 记为未声明，可行性门按 `NEEDS_RESOURCE` 处理，
不得默认取任何一档。

### 7.4 可行性状态

| 状态 | 含义 | 后续动作 |
|---|---|---|
| `FEASIBLE` | 在 `accepted_mode` 下可完整执行 | 正常进入下一段 |
| `FEASIBLE_WITH_REDUCTION` | 降级后可执行 | 必须写明降级到哪一档、删除了什么、结论强度是否下降 |
| `NEEDS_RESOURCE` | 缺一项明确资源即可执行 | 只提出一项区分力最高的资源缺口，等待人补齐；补齐后重新过门，仍不成立则转 `BLOCKED` |
| `BLOCKED` | 当前条件下不可执行 | 不得生成纸面产物；顶层状态 `PRODUCTION_NOT_FEASIBLE` |

`BLOCKED` 不等于整条 Campaign 失败。它只作用于当前内容单元，
其余不依赖该条件的内容单元继续有效。

### 7.5 变化传播

Production Profile 变化后，相关脚本、制作包与发布包必须按影响范围
进入 `STALE` 或重新检查，规则见第 9 节与
[`CONTENT_PRODUCTION_CHAIN_CONTRACT_v0.1.md`](CONTENT_PRODUCTION_CHAIN_CONTRACT_v0.1.md) 第 9 节。

### 7.6 与既有降级纪律的一致性

可行性降级不得越过 `C6_FOUNDER_CONFIRMED_v0.1.md` 已确认的顺序：

> 删除无依据内容 → 降低结论强度 → 改到现有事实能够完整回答的位置 → 延期或取消
> → 返回最上游实际失效的结论

生产链的降级**只削减覆盖面、数量与制作复杂度**，
不削减事实确认、判断完整性与顾客价值。

---

## 8. 共享知识资产

### 8.1 四项资产（本轮定义，不建设）

| 资产 | 承载什么 | 谁读取 |
|---|---|---|
| Platform Intelligence Pack | 平台官方规则、规格、明确禁止项及其生效日期 | 主要 Publishing & Packaging，其余按需 |
| Current Content Benchmark Pack | 当前有效的内容基准与可观察做法 | 三份 Skill 按需 |
| Voice & Expression Profile | 账号人格在表达层的可执行口径（口语化、语气、禁用话术） | 主要 Creative Script |
| Creative & Production Quality Gate | 三份 Skill 共同的质量底线检查项 | 三份 Skill 全部 |

本轮**只在合同中定义其存在、边界与读取方式，不实际建设、不填充内容**。
填充由 P02—P04 研究与 Founder 集中裁决之后决定。

**装载路径**：四项资产建成后，作为运行输入的一项进入
（见 [`CONTENT_PRODUCTION_CHAIN_CONTRACT_v0.1.md`](CONTENT_PRODUCTION_CHAIN_CONTRACT_v0.1.md)
第 1.1 节第 8 项与第 11.4 节），形态是**已裁决、已抽象的判断条目**，
不是研究过程记录。研究过程资产永不进入运行输入。

### 8.2 知识资产不得与 Skill 争夺决策权

- 知识资产是**被读取的参考**，不是裁决者；
- 知识资产不得覆盖企业已确认事实、上游锁定项或 Founder 裁决；
- 知识资产与已确认事实冲突时，以已确认事实为准；
- 不得把全部行业研究历史直接塞进 `SKILL.md`。

### 8.3 平台信息与行业观察分级

任何进入知识资产的条目必须标注等级：

| 等级 | 含义 | 可否作为硬规则 |
|---|---|---|
| `OFFICIAL_RULE` | 平台官方公开规则 | 可，须带生效日期与复查日期 |
| `OBSERVED_PATTERN` | 可观察到的做法与规律 | 否，只能作为条件性建议 |
| `EXPERT_JUDGMENT` | 领域专家判断 | 否，须标注适用条件 |
| `MODEL_HYPOTHESIS` | 模型推演 | 否，不得进入正式事实 |
| `FUTURE_HYPOTHESIS` | 未来趋势判断 | 否，须带完整复查字段 |
| `INSTANCE_DECISION` | 单次实例决定 | 否，不得升级为通用规则 |

平台观察、头部 IP 做法、模型判断与未来趋势
**不得自动进入正式事实，也不得自动变成 Skill 硬规则**。

`FUTURE_HYPOTHESIS` 必须同时包含：来源、适用条件、复查日期、失效条件、后续验证方式。
缺任一项即不得登记。

### 8.4 两套证据分级不得混用

系统中存在**两条不同的分级轴**，必须严格区分：

| 轴 | 分级 | 用在哪 | 出处 |
|---|---|---|---|
| 内容证据 | 已登记事实／亲历观察／专业判断／明确标注的设计情境／待验证变量 | 单条内容里出现的每一条信息 | `Content Brief Architect v0.1` 第 1 节、第 4 节步骤三 |
| 知识资产 | `OFFICIAL_RULE` 等六级 | 平台、行业与趋势知识条目 | 本文件第 8.3 节 |

**禁止跨轴改写**：一条 `OBSERVED_PATTERN` 或 `EXPERT_JUDGMENT` 不得在内容中被表达为
「已登记事实」；一条企业「已登记事实」也不得被登记为平台知识条目。

---

## 9. Artifact 生命周期与上游变化传播

### 9.1 它不是状态机工程

以下状态是**人可读的业务状态词**，写在产物文件里，由人判断与标注。

本轮**不建设**：状态机、自动回退系统、自动异常分级器、工作流引擎、数据库或任何运行时校验服务。
这与 `C6_FOUNDER_CONFIRMED_v0.1.md` 第十一节、`CLAUDE.md` 第 4 节的
「不建设 Contract、Gate、Schema、状态机」一致——那里禁止的是把业务判断实现成复杂工程流程，
不是禁止用大白话把业务规则写清楚。详见附录 A。

### 9.2 五个 Artifact 状态

| 状态 | 含义 |
|---|---|
| `DRAFT` | 已生成，未经检查 |
| `VALIDATED` | 已通过硬门与一致性检查，尚未经人接受 |
| `USER_ACCEPTED` | 已由对应负责人接受，可作为下游输入 |
| `STALE` | 上游发生变化，本产物需重新检查 |
| `FAILED` | 明确不成立，不得作为下游输入 |

只有 `USER_ACCEPTED` 的产物可以作为下游 Skill 的输入。

### 9.3 父子引用与版本

每份产物必须记录：产物类型、产物编号、版本、父产物编号与版本、父产物内容 Hash、
所依据的 `accepted_mode`、当前状态、状态变更原因。字段定义见合同第 8 节。

### 9.4 上游变化传播

| 上游变化 | 直接影响 | 传播规则 |
|---|---|---|
| Content Brief 变更 | Creative Script | 脚本转 `STALE`，其下游制作包与发布包同时转 `STALE` |
| Production Profile 的 `accepted_mode` 变更 | 视变更方向而定 | 见 9.5 |
| Creative Script 变更 | Production Package | 制作包转 `STALE`，发布包转 `STALE` |
| Production Package 变更 | Publishing Package | 发布包转 `STALE` |
| 成片实际状态与制作包不符 | Publishing Package | 发布包转 `STALE`，并由 Publishing & Packaging 输出退回意见 |
| 平台由未确认变为已确认 | Publishing Package | 发布包转 `STALE`（需补平台规格适配） |

`STALE` 的含义是**必须重新检查**，不是必须重做。
重新检查后可以确认仍然成立并恢复原状态，但必须记录该判断。

### 9.5 accepted_mode 变更的两个方向

- **收紧**（条件下降）：脚本、制作包、发布包全部转 `STALE`，必须重新过可行性门；
- **放宽**（条件提升）：制作包与发布包转 `STALE`；脚本可保持原状态，
  但必须记录「未因条件放宽而重写」这一判断，不得自动扩写成更大制作规模。

---

## 10. 失败处理

### 10.1 沿用既有停止口径

三份生产 Skill 沿用编译链已有的两个停止口径，不新造同义词：

- `INPUT_CONFLICT_REQUIRES_FOUNDER`：两条同等效力的正式确认结论不兼容，
  且输入未提供更高优先级裁决。不得自行选择其一。
- `INPUT_INSUFFICIENT`：缺少形成产物所必需的上游正式决定、事实链或最低条件。

### 10.2 本轮新增一个顶层状态

- `PRODUCTION_NOT_FEASIBLE`：输入完整，但可行性门判定为 `BLOCKED`。

这是本合同**新增**的枚举，此前仓库中不存在，不得被描述为既有约定。
新增理由：输入齐全但资源不足，与「输入不足」不是同一件事，
用 `INPUT_INSUFFICIENT` 表达会掩盖真实原因。

### 10.3 Fail-Open 与 Fail-Closed

**Fail-Open（继续，但写成条件）**

- 发布平台未确认；
- 部分素材未就位；
- 承接入口、人员、受理边界或确认方式未确认；
- 产能存在不确定性；
- 成片尚未拍摄，但成片状态可由制作包与夹具确定。

**Fail-Closed（停止，不得生成）**

- 缺少已被接受的上游产物；
- 同等效力正式结论冲突；
- 没有任何一条可确认、可公开、可制作的事实链；
- 可行性门为 `BLOCKED`；
- 继续生成必须依靠编造事实、越权承诺或包装成平台定制；
- 继续生成必然超出 `accepted_mode`。

判据：**缺条件可以条件化，缺事实与缺授权不能条件化。**

### 10.4 普通执行问题与 Founder 升级边界

沿用 `C6_FOUNDER_CONFIRMED_v0.1.md` 第九节，不新增升级路径。

由对应负责人处理，不交 Founder：拍摄窗口变化、剪辑延期、发布时间调整、
镜头缺失、单条内容删改、普通负面评论与事实误解、一般容量波动。

必须交 Founder：正式品牌立场；品牌级公开回应；重大经营取舍；长期账号使命；
组织权责变化；重大资源投入；新增或改变对外政策与承诺。

「可能影响声誉」或「评论较负面」本身不足以触发 Founder。

---

## 11. 平台未确认时的处理

发布平台（`D49`）当前仍未由 Founder 锁定，状态为 `PLATFORM_UNCONFIRMED`。
这不阻塞内容生产链运行。

| Skill | 平台未确认时的行为 |
|---|---|
| Creative Script Architect | 输出平台中立脚本；不使用平台特有形式；不写平台专属钩子与时长惯例 |
| Production Director | 输出平台中立制作包；不锁定画幅、时长、字幕规格；把平台规格列为待适配项 |
| Publishing & Packaging Architect | 输出平台中立包装，附「平台规格待适配清单」；顶层状态 `READY_WITH_CONDITIONS` |

统一禁止：

- 自动选择视频号、抖音或任何平台；
- 使用平台特有挂载、评论、私信、链接或尺寸能力；
- 在平台未确认时把包装描述为某平台定制；
- 通过暗号、藏码、诱导跳转等方式规避平台规则；
- 因用户愿意承担风险而生成明确违规手法。

平台锁定后，相关发布包按第 9.4 节转 `STALE` 并补做平台规格适配。

---

## 12. V1 范围与非目标

### 12.1 范围内

- 三份生产 Skill 的研究、对抗、施工与纵向 E2E；
- Production Profile 与可行性门作为共享前置合同；
- 四项共享知识资产的**定义**；
- Artifact 状态、父子引用与失效传播口径；
- Dify 上的真实运行与验收证据；
- P09 独立只读收口审查。

### 12.2 非目标

- 不修改已落盘的三份决策 Skill 及其合同、DSL、RAW／FINAL／EVAL 与 Manifest；
- 不修改正在并行建设的自然交互层；
- 不建设发布反馈学习层（见第 14 节）；
- 不真实拍摄成片、不自动剪辑或导出视频；
- 不自动发布平台内容；
- 不证明内容已获得良好数据；
- 不证明系统已从发布结果中学习；
- 不新增自动评分器、RAG、数据库、代码节点或正式前端；
- 不建设 CRM、排班系统、预约状态机或预约前端；
- 不接入账号搜索、平台数据或反馈工具；
- 不让 Claude Code 或其他 LLM 评价哪份内容更好。

### 12.3 模型策略

| 项 | 值 |
|---|---|
| 当前主测试模型 | `deepseek-v4-flash` |
| Fallback | `qwen3.8-max`，仅用于已明确的 Fallback、能力缺失或后续受控多模型测试 |
| 明确禁止 | 自行切换到 `qwen-max` 或 `qwen3.7-plus` |
| 对照要求 | 有 Skill 与无 Skill 对照必须使用相同模型、相同参数、相同输入 |
| P01 本身 | 不调用任何模型，不运行 Dify |

---

## 13. P01—P09 里程碑

| 阶段 | 内容 | 产出 | 状态 |
|---|---|---|---|
| `P01` | 共享 PRD、合同与研究协议 | 本文件、合同、研究协议 | 本轮 |
| `P02` | Creative Script 研究与对抗 | 研究资产＋Founder 裁决卡 | 待启动 |
| `P03` | Production Director 研究与对抗 | 研究资产＋Founder 裁决卡 | 待启动 |
| `P04` | Publishing & Packaging 研究与对抗 | 研究资产＋Founder 裁决卡 | 待启动 |
| — | **Founder 集中裁决** | 裁决结论 | 待启动 |
| `P05` | Creative Script Skill 施工 | `SKILL.md`＋DSL＋运行证据 | 待启动 |
| `P06` | Production Director Skill 施工 | `SKILL.md`＋DSL＋运行证据 | 待启动 |
| `P07` | Publishing & Packaging Skill 施工 | `SKILL.md`＋DSL＋运行证据 | 待启动 |
| `P08` | 三 Skill 纵向 E2E | 端到端运行与验收证据 | 待启动 |
| `P09` | 独立只读收口审查 | 审查结论 | 待启动 |
| 条件 | 条件修正 Prompt | 仅在 P09 发现明确问题时使用 | 条件性 |

**不得提前建设 P05—P07。** P02—P04 可以并行；P05—P07 必须在 Founder 集中裁决之后。

---

## 14. 发布反馈学习延期裁决

```text
Decision ID：PRD-DECISION-FEEDBACK-LEARNING-DEFERRED-V1
状态：DEFERRED
```

### 14.1 当前不建设

- 发布后账号搜索；
- 公开内容监测；
- 发布表现复盘；
- 评论与指标分析；
- 经营结果回流；
- Candidate Learning；
- Skill 自动或人工写回流程；
- 平台授权数据接口；
- 搜索工具产品化接入。

### 14.2 后续可以建设的路径

```text
公开账号搜索
＋自有账号授权数据
＋企业承接结果
＋产物谱系
→ Candidate Learning
→ 多实例验证
→ 专家审查
→ Founder 批准
→ Benchmark 或 Skill 版本更新
```

### 14.3 本轮纪律

本轮**只记录该延期决定**：不施工、不测试、不计入 DONE 标准、不作为验收项。

执行代理在 P02—P04 中**仍可以使用合法网络搜索开展项目研究**；
这不等于把搜索工具接入产品，也不构成对本裁决的突破。

---

## 15. V1 完成定义

内容生产链 V1 在**同时满足**以下六条时成立：

1. 三份生产 Skill 全部落盘，职责排他性通过检验；
2. 至少一条已接受的 Content Brief 内容单元，产出**可接受的完整脚本**；
3. 同一内容单元产出**可执行的拍摄、声音、剪辑制作包**，且不超出 `accepted_mode`；
4. 同一内容单元产出**与真实成片状态或成片夹具匹配的发布包装**；
5. 三份产物具备完整谱系：父子引用、版本、内容 Hash、状态与状态变更原因齐备；
6. 具备 **Dify 真实运行与验收证据**：运行 Manifest、原始输出、输入 Hash、DSL Hash 与负向探针。

### 15.1 明确不要求

- 真实拍摄成片；
- 自动剪辑或导出视频；
- 自动发布平台内容；
- 内容已获得良好数据；
- 系统已从发布结果中学习。

### 15.2 不得制造通过

不得通过修改既有文件消除冲突、修改验收标准、删除失败或冲突证据、
把假设写成事实、新增无关文档制造完成感，或以文档数量替代合同质量。

---

## 16. 已知限制

1. **夹具是模拟的**：序里集全部素材标记为 `SIMULATED_DEMO_FACT`，
   不能对外描述为现实企业事实；产能与承接数字是人为设定，不是真实测算。
2. **平台未锁定**：`D49` 未决，本轮全部产物只能是平台中立的，
   平台规格适配无法在本轮完成验收。
3. **无成片**：V1 终点是发布包装，`Publishing & Packaging` 只能对
   「已确定状态的成片或成片夹具」工作，不能验证真实成片。
4. **共享知识资产为空**：四项资产本轮只定义不建设，
   因此 P05—P07 施工时其内容仍需依赖 P02—P04 研究结论。
5. **单人裁决**：沿用《笛语项目基线》的流程简化定案，
   Founder 一人裁决即可；结论口径相应收窄，不得写成「有市场价值」。
6. **无发布反馈**：系统不知道内容发布后发生了什么，
   任何「有效」判断都只能来自人的判断，不能来自数据。
7. **模型能力未验证**：`deepseek-v4-flash` 在脚本、分镜与包装三类任务上的
   稳定性尚未测试；能力缺失时的 Fallback 触发条件需在 P05—P08 中确定。
8. **Production Profile 依赖人诚实声明**：系统无法核实用户声明的
   `available_mode` 是否属实；声明失真会直接导致产物不可执行。

---

## 17. 进入 P02—P04 的条件

P02、P03、P04 可以在以下条件**全部成立**后并行启动：

1. 本文件、合同与研究协议三份文件已落盘并提交；
2. 三份生产 Skill 的职责边界无冲突（第 6 节检验通过）；
3. Production Profile 字段、双轴模式与四种可行性状态已冻结；
4. Artifact 五状态与失效传播规则已冻结；
5. 证据六级分类已冻结；
6. 发布反馈学习延期裁决已记录；
7. 研究协议的六轮流程、输出分类与分歧路由已冻结；
8. 未修改任何既有 Skill、DSL、RAW／FINAL／EVAL／Manifest 与夹具。

P02—P04 各自**只研究自己那一份 Skill 的职责范围**，
不得跨界研究其他两份，不得提前编写任何 `SKILL.md`。

三者的研究结论汇总后，进入 **Founder 集中裁决**，
裁决通过前不得进入 P05—P07。

---

## 附录 A：口径校准与真源关系

本附录记录本文件与仓库既有表述之间需要说明的三处口径关系。
均**不构成同优先级不可兼容冲突**，因此不触发 `INPUT_CONFLICT_REQUIRES_FOUNDER`。

### A.1 关于「不建设 Contract、Gate、Schema、状态机」

- **既有表述**：`CLAUDE.md` 第 4 节 verbatim
  「不建设 Contract、Gate、Schema、状态机、版本治理或规则激活流水线。」
  `C6_FOUNDER_CONFIRMED_v0.1.md` 第十一节 verbatim 列出同类清单。

- **决定性事实**：《笛语项目基线》第三节「第一版明令不接」的对应句**自带解禁条款**，verbatim：

  > 当前 Demo 不建设 Contract、Gate、Schema、状态机、版本治理和规则激活流水线。
  > 未来是否需要，必须由真实运行问题和 Founder 新授权决定；
  > 不得把未来工程可能性变成当前开工门槛，也不得因为缺少这些设施把 Dify Demo 判定为 `BLOCKED`。

  《笛语项目基线》是 `CLAUDE.md` 第 2 节列明的第 1 优先真源，
  因此该解禁条款同样管辖 `CLAUDE.md` 第 4 节的同类表述。

- **解禁的两个条件，本轮均已满足，逐条列证**：

  1. **真实运行问题**：Matrix `RUN_001`—`RUN_003`、Campaign 多模型与 Compile 多轮运行、
     Content Brief `RUN_001` 及两个负向探针（分别跑出 `INPUT_INSUFFICIENT` 与
     `INPUT_CONFLICT_REQUIRES_FOUNDER`）均已归档。已暴露的问题包括：
     Content Brief 之后无承接者；制作条件只是自然语言、无统一口径；
     产物之间的依赖与失效无法追踪；创意张力维度得分最低（15/20）。
  2. **Founder 新授权**：`CONTENT-PRODUCTION-P01` 第 4 节列明的 Founder 已确认决定。

- **既有先例**：`CONTENT_BRIEF_CONTRACT_v0.1.md` 已作为**治理文件**落盘并冻结，
  明确声明「不是模型输入」，其 SHA-256 已被 `CONTENT_BRIEF_DIFY_RUN_MANIFEST_v0.1.md`
  登记为运行证据。本文件与配套合同沿用完全相同的性质与声明。

- **范围切分**：禁止的是**面向模型运行时的工程设施**——状态机、校验服务、
  自动回退系统、自动异常分级器、自动评分器、数据库、代码节点、规则激活流水线。
  本轮产出的是**用大白话写、Founder 可逐句审计的业务规则文件**。
  `C6` 原文紧接着写明「本 Demo 只需要用业务语言说明：什么事实变了、哪项结论因此失效、
  谁重新判断、哪些后续内容需要复核」——这正是本文件第 9 节所做的事，
  措辞与结构均沿用该句，不另起工程术语。

- **本轮不改变 `C6_FOUNDER_CONFIRMED_v0.1.md` 第十一节的非建设范围。**
  该节的作用域被其首句「本原则只是业务判断路由」锁定在 C6 异常回退原则上，
  本文件不触碰该原则，也不把它实现成流程。

- **反面先例与自我约束**：《笛语项目基线》第七节 verbatim 记录
  「M2 由 Founder 主动挂起，根因是治理装置变成了工作本身
  （49 判据 / 616 夹具 / 697 错误码，真交付物 0 件）」。

  据此，本轮三份文件受以下自我约束：
  只定义**三份生产 Skill 施工所必需**的字段与状态，不建判据库、不建错误码表、
  不建注册表、不为完整性增设层级。若 P02—P09 出现「治理文件变成工作本身」的迹象，
  应削减本文件，而不是继续扩建。

### A.2 关于当前主模型

- **既有表述**：`CLAUDE.md` 第 1 节写「当前业务模型统一使用 Qwen 系列」。
- **仓库实测**：`DIYU_DEMO_CAMPAIGN_DEEPSEEK_V4_FLASH_COMPILE_V0_1.yml` 与
  `DIYU_DEMO_CONTENT_BRIEF_DEEPSEEK_V4_FLASH_V0_1.yml` 均指向 `deepseek-v4-flash`；
  `DIYU_DEMO_CAMPAIGN_QWEN38_FALLBACK_COMPILE_V0_1.yml` 明确命名为 Fallback；
  两份运行 Manifest 各自**最新一次**运行的实际模型均为 `deepseek-v4-flash`：
  `CONTENT_BRIEF_DIFY_RUN_MANIFEST_v0.1.md` 三条记录全部为 `deepseek-v4-flash`；
  `CAMPAIGN_DIFY_RUN_MANIFEST_v0.1.md` 八条记录含早期多模型对照运行
  （`qwen-max`、`deepseek-v4-pro`、`qwen3.8-max`、`qwen3.7-plus`），
  这些是已冻结的历史对照证据，不改变当前主模型结论。
- **结论**：`CLAUDE.md` 该句相对仓库现状已经陈旧，
  由 `CONTENT-PRODUCTION-P01` 第 4.8 节的 Founder 已确认决定取代。
  本轮**不修改** `CLAUDE.md`；该文件的更新由 Founder 另行决定。

### A.3 关于「生产层切出产品范围」

- **既有表述**：《笛语项目基线》第二节市场进入方案写
  「笛语做上层……生产层切出产品范围，组织自行生产」。
- **本文件口径**：该句的对象是**实际生产执行**——拍摄、剪辑、出片、发布由组织自行完成。
  本轮内容生产链的终点是**可拍、可剪、可发布的生产包**，不是代替组织拍摄剪辑发布。
  第 12.2 节与第 15.1 节已明确排除真实拍摄、自动剪辑与自动发布。
- **结论**：范围一致，不构成冲突。

---

## 附录 B：术语对照

| 术语 | 英文／枚举 | 定义位置 |
|---|---|---|
| 内容决策编译链 | Content Decision Chain | 本文件 5.1 |
| 内容生产链 | Content Production Chain | 本文件 5.1 |
| 制作条件档案 | Production Profile | 本文件 7.2、合同 5 |
| 可行性门 | Production Feasibility Gate | 本文件 7.4、合同 7 |
| 拍摄方式轴 | Capture Mode | 本文件 7.3、合同 6 |
| 增强方式轴 | Augmentation Mode | 本文件 7.3、合同 6 |
| 产物状态 | Artifact Status | 本文件 9.2、合同 8 |
| 共享知识资产 | Shared Knowledge Asset | 本文件 8.1、合同 11.4 |
| 证据等级（知识资产轴） | Evidence Level | 本文件 8.3、合同 11.2、研究协议 4 |
| 内容证据分级（内容轴） | — | 本文件 8.4、合同 11.1 |
| 结论处置分类 | Output Classification | 研究协议 9 |
| 分歧路由 | Divergence Routing | 研究协议 10 |
| 共同 Hard Gate | — | 合同 12 |
| 模型专家视角审查 | `MODEL_PANEL_REVIEWED` | 研究协议 15 |
| 真实领域专家验证 | `DOMAIN_EXPERT_VALIDATED` | 研究协议 15 |

---

## 附录 C：本文件不能证明的事项

- 不证明三份生产 Skill 可以做出好内容：本轮未编写任何 Skill，未运行任何模型。
- 不证明本 PRD 的职责划分在真实运行中成立：职责排他性目前只经过文档级检验，
  未经 Dify 真实运行验证，验证发生在 P08。
- 不证明 Production Profile 的双轴与四状态够用：五个 `Capture Mode` 取值
  在当前夹具下只有一部分有对应证据，其余未被任何真实条件检验过。
- 不证明 Artifact 五状态与失效传播在多内容单元、多版本并发时仍然清晰：
  当前只推演过单链场景。
- 不证明 `deepseek-v4-flash` 能稳定完成脚本、分镜与包装三类任务：本轮未调用模型。
- 不证明内容会带来任何经营结果：未拍摄、未发布、无真实顾客、无平台。
- 不证明系统能从发布结果中学习：发布反馈学习已延期，本轮未建设。
- 不证明四项共享知识资产的划分正确：本轮只定义名称与边界，内容为空。
