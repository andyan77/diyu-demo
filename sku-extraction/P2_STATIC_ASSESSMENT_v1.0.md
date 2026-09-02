# P2 账号经营决策助手 · 静态评估 v1.0（E1-4，不摘）

```yaml
task_id: DIYU-V1-THREE-SKU-EXTRACTION-001
sku: P2
scope: 只评估 Mode A（冷启动诊断）。Mode B 上下文依赖前三个 SKU 的沉淀（Q-COMM-07 §2 已载明），本轮不评估。
standard: Q-COMM-07_P2_账号经营决策助手商业化评价验收标准_v1.0.md（f5f79b3e…63dd7，未列入本任务治理绑定，只读参考）
inspected_objects:
  - account-operations/skills/operating-one-account/SKILL.md（54518 字节，中文，"载体适配"版）
  - m3-account-content-operator-semantic-v1.0/skill-source/SKILL.md（11508 字节，英文，"语义真源"版）
action: 不摘、不建目录，只回答两个问题。
```

## 背景核实

`operating-one-account/SKILL.md` 文件头自述：

```text
planning_source = m3-account-content-operator-semantic-v1.0/skill-source/SKILL.md（ccedd9a8…）
semantic_truth  = M3_ACCOUNT_CONTENT_OPERATOR_SEMANTIC_COMPILATION_v1.0.md（732963af…）
本文件是载体适配，不改产品语义。
```

即：这两份文件**不是两个竞争的 SKILL**，而是同一套专业判断的两层——`skill-source` 是紧凑的英文语义核心，`operating-one-account` 是从它编译出的、更完整的中文生产版本。评估时按同一套产品语义对待，不重复计两次差距。

---

## a) 与 Q-COMM-07 产品合同的差距

### 已经贴合的部分

| Q-COMM-07 条款 | 现状 |
|---|---|
| Mode A"账号经营诊断与基线建立"——"先告诉我现在是什么状态、最值得解决什么、接下来应该观察和验证什么" | `operating-one-account/SKILL.md`「本轮在做哪件事」表里的"运营状态诊断"行直接对应："这个号现在什么状态，主要机会、约束、未知是什么"→"阶段解释、目标适配、证据与缺口、建议动作或需返回的上游"，语义高度贴合 |
| Mode A"没有长期历史也可以工作，但不得声称'根据你过去长期表现……'" | SKILL.md「输入」表逐槽位都设计了"缺了怎么办"的降级路径（如 `stage_evidence` 缺失时"按证据不足处理，给暂定解释+一条区分性观察"），且有专门的"证据身份不得混写"十类分级表，"未知项"单列为一类（"这里是空的"≠"这里本该有什么"）——这套证据纪律本身就是为了防止在证据不足时假装有长期历史 |
| 商业价值公式中的"状态理解" | O-1 至 O-11 判断主链里 O-1（冻结任务权威）/O-2（解释阶段不套标签）与诊断职能直接对应 |

### 明显的差距

| Q-COMM-07 条款 | 差距 |
|---|---|
| §1"本 SKU 必须拆成两个商业成熟状态……禁止用一个 Gate 同时验收" | **现状不满足**：SKILL.md 的"本轮在做哪件事"表把"运营状态诊断"（Mode A 性质）与"周期规划"/"日常决策"/"复盘更新"（更接近 Mode B 性质，依赖历史投影）列为**同一份 Skill 内可任意组合触发的四类行为**，明文"不要求用户选模式""它们不是四个互斥状态"——这与标准要求的"两个状态分开验收、不得混用一个 Gate"在结构上正相反。要满足标准，需要在架构层面（不只是文档层面）划出一条 Mode A/B 边界，而不是让四类行为在一次对话里自由组合 |
| 无 M4 tool DSL | **完全缺失**——没有 `envelope_check`/`gate_sufficiency`/`returns_adapter`/`binding_record`/`component_return` 等统一能力接缝的任何一层，无法承接另外三个 SKU 已经统一使用的"结构性充分性闸→专业生成→交付适配→保真绑定"这套确定性外壳。当前完全靠一份长文本 Skill 提示词自我约束，没有任何代码级校验 |
| G0 模式 Gate（§7，只读，未详细核对但从命名看必然要求"识别当前请求属于 Mode A 还是 Mode B 并分别验收"） | **无对应机制**——SKILL.md 没有输出一个"本次判定为 Mode A 还是 Mode B"的显式字段 |

### 结论

Mode A 的**专业判断内容**（诊断逻辑、证据分级纪律、O-1~O-11 判断主链）已经相当成熟，甚至比 P0/P1/P1.5 三者的"证据身份"处理更精细（十类证据身份表，M4 三兄弟没有对应的细粒度分级）；但**产品形态**（Mode A/B 结构性分离、M4 统一能力接缝、代码级充分性闸）与另外三个 SKU 已经采用的商品形态差距很大——本质上是"有专业判断，没有商品外壳"。

---

## b) 重建 M4 形态 vs 另起：两条路各自要做什么、代价在哪（不做取舍）

### 路径一：重建一个 M4 形态的工具（复用 P0/P1/P1.5 已验证的骨架）

**要做什么**：

1. 把 `operating-one-account/SKILL.md` 的内容拆成"Mode A 专属"与"Mode B 专属"两部分，Mode B 部分本轮不启用；
2. 为 Mode A 设计一份 `envelope_check.REQUIRED` 字段集合（对应 Q-COMM-07 Mode A 的最低输入，需另行定义——本轮未评估）；
3. 复用本任务已验证 100% 共用的五个节点（`envelope_check`/`gate_sufficiency`/`returns_adapter`/`projection_gate`+`recovery_llm`+`delivery_finalize`/`binding_record`/`component_return`）的代码骨架，只替换 SKU 专属配置常量；
4. 把 O-1~O-11 判断主链、十类证据身份表迁移进新 SKILL 文件的"核心判断"节，比照 PP-x/CS-x/PD-x 的组织方式；
5. 设计"输出"字段契约（当前 SKILL.md 已有"输出"/"必填项闸门"/"审计块"等概念，需要重新对齐成 M4 的"标记块"格式）。

**代价**：

- **好处**：五个共用节点已经过 P0/P1/P1.5 三方交叉验证，代码本身不含任何 P0/P1/P1.5 专属语义，移植风险低；`QUESTION_MAP`/`VACUOUS`/`GOAL_FAMILIES`/`CTA_LEVELS` 等共用常量可以直接复用大部分（`GOAL_FAMILIES`/`CTA_LEVELS` 与账号经营目标高度相关，可能不需要改动）。
- **代价**：`operating-one-account/SKILL.md` 是四份 SKILL 里最大的一份（54518 字节，接近 P0/P1/P1.5 三者之和），且其英文语义源（`m3-.../SKILL.md`）用词体系（Establish/Preserve/Compile/Run/Decide/Review/Bound）与另外三份 M4 SKILL 的中文体系（核心判断/输出/自检/参考文件）差异较大，重新组织的工作量不小；
- **架构缺口**：M4 骨架本身完全是**无状态**的单次请求-响应模型（`start`→…→`end_ok`），而 Mode A 虽然"没有长期历史也可以工作"，但 Q-COMM-07 §2 描述的 Mode B 最低上下文（账号历史/历史内容/发布结果/团队产能等）意味着这个 SKU 迟早需要一层**持久化状态**——M4 骨架完全没有为此设计任何东西（无数据库读写节点、无会话记忆机制）。即使先只做 Mode A，若不及早考虑这层扩展点，Mode B 落地时可能要回头改造刚建好的 Mode A 骨架。

### 路径二：另起（不套用 M4 骨架，针对两态设计专属架构）

**要做什么**：

1. 从 Q-COMM-07 §1/§2 出发单独设计架构，明确区分 Mode A（无状态诊断）与 Mode B（有状态持续决策）两条路径，可能是"共用 Skill 正文 + 两套不同的运行时外壳"；
2. Mode A 路径可以先做成接近 M4 骨架的无状态调用（复用与否是设计选择，不强制沿用 P0/P1/P1.5 的具体代码）；
3. Mode B 路径单独设计状态持久化层（账号历史/发布结果的存储与恢复机制），这是当前四份 SKILL 都没有先例的新增基础设施；
4. G0 模式 Gate 单独实现，作为两条路径的分流点。

**代价**：

- **好处**：不被 M4 骨架的无状态假设束缚，可以从一开始就为 Mode B 的持久化需求留出正确的架构位置，避免"先按 M4 无状态模式建好 Mode A，再回头改造"的返工；十类证据身份表这类已经比另三个 SKU 更精细的部分可以原样保留，不需要削足适履塞进 M4 的"外壳校验"六字段结构里。
- **代价**：放弃了 P0/P1/P1.5 三方交叉验证过的共用节点（`envelope_check`/`returns_adapter`/`delivery_finalize` 等），这些节点里已经沉淀的"结构性充分性判断""交付格式校验""保真绑定"等通用能力需要重新设计或重新对齐，失去了"复用已验证代码"这一路径一的核心优势；且脱离统一能力接缝协议后，未来若要与 Matrix/Campaign/Content Brief 等能力互通，需要单独设计对接方式，不能直接沿用另外三个 SKU 已经共用的接口形态（`capability_call`/`professional_input`/`entry`/`run_mode` 五变量输入 schema）。

**两条路都未评估**：具体 `REQUIRED` 字段集合、G0 模式 Gate 的判据设计、Mode B 状态层的技术选型——均超出本轮静态评估范围，需要各自的独立 Execution Prompt。
