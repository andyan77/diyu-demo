# CLAUDE.md

本文件约束当前仓库中的执行代理。任何旧线程、旧文档或历史方案与本文件及《笛语项目基线》冲突时，以当前仓库真相源为准。

## 0. 上位治理与角色（2026-08-27 接入）

本节**只给指针，不复制任何正文**。与所引真源冲突时以真源为准，并把本节标 `STALE` 后定向修正。

| 层 | 真源位置 | 加载条件 |
|---|---|---|
| 通用宪法内核 | 用户级 `~/.claude/CLAUDE.md` 内核段 | 常驻，无条件 |
| 通用宪法运行层 / 推导表 | `/home/faye/governance/universal-ai-collaboration-governance/constitution/` | 按内核 §6 条件加载 |
| **项目 Profile（真源）** | `/mnt/c/Users/Administrator/Documents/Codex/Diyu-V1-Planning/projects/APP-DIYU-DEMO/PROJECT_PROFILE.md` | 开工前、进入模式判断、边界确认时读 |
| 执行侧协议 v1.3 | `/home/faye/governance/universal-ai-collaboration-governance/project-protocols/diyu/受边界约束的执行总负责人协议_v1.3.md` | 当前角色为 `EXECUTION` 且 Profile 采用该协议时 |
| 规划侧协议 v1.2 | `/home/faye/governance/universal-ai-collaboration-governance/project-protocols/diyu/执行Prompt生成总则_规划侧约束框架_v1.2.md` | 当前角色为 `PLANNING` 且 Profile 采用该协议时 |
| Review Contract 指定的项目协议 | 由当前 Review Contract 指明 | 当前角色为 `REVIEW` 时 |

**加载由角色触发，不由仓库或工具触发。** 未命中当前角色的协议不加载全文——承担 `PLANNING` 的执行单元不读 v1.3 全文，承担 `EXECUTION` 的不读 v1.2 全文。

- Constitution 分发身份：`tag=v0.3.1-revision-2` / `commit=34d10a052767fe5cbc2ceebc236e2ad17e2d1885`；激活事件 `RULESIDE-2026-08-25-005`
- 规则侧采用证据：`Diyu-V1-Planning` commit `45344f2`（activate constitution v0.3.1 revision 2）；该 Profile 已把 v1.2 / v1.3 列为本项目现行协议
- 若上述 `/mnt/c/...` 路径不可达，本节相关判断一律置 `STALE`，不得凭记忆复述 Profile 内容

### 0.1 角色装配（不由工具品牌决定）

> **ROLE IS SELECTED BY TASK AUTHORITY, NOT BY TOOL BRAND.**

- `/home/faye/diyu-demo` 是**执行事实仓库**：工程实现、Git、运行状态与原始证据的所在地。
- **执行事实仓库 ≠ 某个工具永久拥有 `EXECUTION` 角色。** 仓库身份是载体，不是角色分配。
- 最终角色只由三者决定：**Project Profile + 当前 Task Contract + 当前授权**。
- Claude Code、Codex 及未来兼容 Agent **都可以**承担 `PLANNING` / `EXECUTION` / `REVIEW`。
- 当前常用拓扑（**仅为当前任务装配，不是永久工具映射**）：Codex 当前规划窗口承担 `PLANNING`；Claude Code 当前项目窗口在拿到准确 Task Contract 与授权时承担 `EXECUTION`。下一个任务可以完全相反。
- 更换工具、窗口、模型或终端**本身**不产生新 `task_id`，不重置 Attempt，不清空失败历史，也不构成 `REBASE`。
- 承担 `EXECUTION` 的执行单元不得改 `WHAT / WHY / BOUNDARY / ACCEPTANCE`、产品语义、授权或冻结 Oracle——这些只能由规划侧编译、Founder 接受。本文件 §6「不得由执行侧宣布合同已接受」是同一条的项目表述。
- 角色未声明时按 [`AGENTS.md`](AGENTS.md) §4 的顺序判断，**不得凭工具品牌推断**。

### 0.2 与本仓库真相源的关系

通用宪法裁决**原则**（权威域、证据等级、状态词、失效传播、可消融性）；本仓库真相源裁决**产品事实与当前状态**。两者分属不同权威域，不互相覆盖（A1 跨域不覆盖）。本文件开头「以当前仓库真相源为准」继续有效，指的是产品与状态命题。

五本账（`collab-ledger/`）即宪法第 5 节「账本」在本项目的载体，字段与程序按项目协议，不改名、不另造第三套。

### 0.3 不在本仓库建第二份 Profile

`PROJECT_PROFILE.md` 的真源在规则侧且已存在。本仓库只指路、不复制——复制会制造第二套真源并触发 A3 的全量载体同步义务。

## 1. 当前项目阶段

阶段为 **V1 决策链重对齐（Rebase）**。Dify Demo A/B 对照阶段已结束并按 `PARTIAL` 冻结。

| 合同 | 状态 | 授权 |
|---|---|---|
| [V1 决策链改造产品合同（上位）](decision-chain/docs/V1_DECISION_CHAIN_REBASE_PRODUCT_CONTRACT_v0.1.md) | `PRODUCT_CONTRACT_ACCEPTED — REPO_PREFLIGHT_AUTHORIZED` | **只授权只读预检 `V1-REBASE-EP00-CURRENT`** |
| [单账号持续运营纵向切片子合同 v0.2](decision-chain/docs/V1_SINGLE_ACCOUNT_SLICE_CONTRACT_v0.2.md) | `ACCEPTED — SINGLE_ACCOUNT_SLICE_PREFLIGHT_AUTHORIZED` | Founder 已接受（v0.1 历史版本不再是当前指针）；授权 `SINGLE-ACCOUNT-SLICE-EP00` 只读预检 |
| M0.3 四份共享合同（任务上下文快照／八项能力／版本发布反馈归属／写回权限幂等恢复，`decision-chain/docs/V1_M0_SHARED_CONTRACT_*_v0.1.md`） | `ACCEPTED` | Founder 已接受，**授权 M1–M4 施工规划 Execution Prompt 编译**；**不授权** M1–M4 工程实现本身，工程实现需各自独立的 Execution Prompt |

- **上位合同被接受 ≠ 子合同被接受**，也 ≠ 授权施工。改 Skill、DSL、持久化、工作流一律需要新授权。
- 模型按能力选用（当前主模型 DeepSeek，语义事实核验 qwen3.8-max），**不再有 Qwen-only 约束**。
- 当前不做完整软件工程化。
- **当前任务状态与下一动作不写死在本文件**，按顺序读取：① [`collab-ledger/L2_TASK_STATE_AND_HANDOFF.md`](collab-ledger/L2_TASK_STATE_AND_HANDOFF.md) → ② [`collab-ledger/L1_TASK_MANIFESTS.md`](collab-ledger/L1_TASK_MANIFESTS.md) → ③ 当前 Task Contract / Execution Prompt → ④ 当前 Git、Dify、数据库与真实运行证据 → ⑤ 规则侧规划基线（**只作规划索引，不代替实时工程状态**）。本文件只保留长期稳定的项目边界与产品规则。

## 2. 真相源优先级

1. **V1 决策链改造产品合同**：产品方向、组件职责、验收与非目标。
2. 《笛语项目基线》**§〇**：当前阶段、状态与授权范围；§四长期裁决与§五产品标准继续有效。
3. 《一页纸夹具品牌事实 v0.1》：序里集夹具事实源，**只用于测试、回归、演示与验收，不是生产真源**。
4. 《笛语调研报告：全网 IP 矩阵》《笛语 Skill 专家问题库 v2.1》《笛语 Demo 核心判断采集 v0.1》：**参考性历史证据**。

不得从旧文件、旧线程或研究报告倒推当前产品规则。**子合同未被接受前，不得据其内容开工。**

## 3. 组件调用形态

**不存在唯一线性路径。** 「Matrix → Campaign → Brief → 生产」作为唯一入口的假设**已被上位合同废止**。

八项能力按需调用、可直接进入、可合法组合：

```text
账号架构与诊断（Matrix）｜单次经营任务策划（Campaign）｜单账号持续运营能力
Content Brief｜创意决策／创意锦标赛（CS-1 内部能力）
Creative Script｜Production Director｜Publishing & Packaging
```

- **Campaign 既不默认调用，也不默认绕过**——由用户意图及任务是否具有阶段性战役结构决定。
- 组件必须拥有所需业务输入，或存在合同允许的**等价替代输入**；**不得为进入某组件暗中补跑前置组件**。
- 不得并行扩建外围系统。

**当前下一步不写在本文件。** 按 §1 的顺序读取：L2 → L1 → 当前 Task Contract / Execution Prompt → 实时运行证据。

## 4. 防跑偏硬约束

- 不继续全网调研。
- 不制作 v2.2。
- 不要求 Founder 回答历史问题库的 58 项。
- 不把问题库当成开工门禁。
- 不把案例、数字和阈值直接写成规则。
- 不把通用模型常识冒充专家资产。
- 不向 IP 领域专家追问技术架构、Schema、状态机或实现方案。
- 不建设复杂意图本体、重型依赖图、第二套工作流引擎、多层 Judge 网络、固定数量候选生成器、全量事件溯源平台、通用数据库平台或数据中台。
- 不以缺少未来工程设施为理由阻塞当前阶段。
- 不让 Claude Code 或其他 LLM 评价哪份内容更好。
- 不新增自动评分器、领域知识库、RAG-first、全平台爬虫、自动发布或正式前端。
  （**口径更正**：运行链路已使用代码节点；持续运营需要**可恢复的业务持久化能力**，但这**不授权**建设通用数据库平台。）
- 不自动选择内容发布平台。
- 不预选序里集的四个账号。
- 不补写夹具未提供的商品、库存、价格、面料、顾客或经营事实。
- **资料不足时不得整任务拒绝**：只降低事实专属性和现实承诺，不降低创意与成品质量；阻止的是无依据的具体主张，不是整个任务。
- 流量、起号、GMV 目标**不得自动授权**剧情、二创、争议、强冲突、激进人设或高风险表达。
- **复用 Skill 不等于继承其价值判断**；不得把起号、吸粉、流量和 GMV 任务重新改写成长线价值内容。
- **候选数量不得硬编码**：只在存在真实取舍时给多个方向，不存在真实取舍时直接给推荐。
- 不把私域承接者强行建模为 IP 账号。
- 不要求每个账号都承担成交。
- 不要求每条内容都有强 CTA。
- 不允许通过暗号、藏码、诱导跳转等方式规避平台规则。
- 不因用户愿意承担风险而生成明确违规手法。

## 5. 业务表达原则

- 所有核心规则必须能用 Founder 可审计的大白话说明。
- 当前“承接”只回答三件事：
  1. 用户下一步做什么；
  2. 谁在哪里接；
  3. 当前接不接得住。
- Skill 不负责设计分钱，但发现利益明显不对齐时要提示 Founder。
- 内容发布平台不等于成交地点。
- 转化对象可以是商品，也可以是到店、预约、会员或咨询。
- 多个账号必须真正分工，不能只是同一内容换四种说法。
- 人设必须与真实组织角色、真实工作和真实素材来源相连。
- 事实不足时不得编造。
- 经营目标模糊时应先整理成可执行方向，不把未经整理的问题退回 Founder。
- 必须交人的决定要明确标出，但不要新增复杂节点。

## 6. 文档执行纪律

- 每次只执行当前 Prompt 授权范围。
- 不顺手重构仓库。
- 不新增同义文档。
- 不创造新的“最终版”。
- 修改后必须检查所有交叉引用。
- 发现版本错位时，以当前实际文件和《笛语项目基线》为准。
- 不根据历史对话记忆覆盖仓库当前真相源。
- 除非 Founder 明确授权，不 commit、不 push、不创建 PR。
- **不得由执行侧宣布合同「已接受」，也不得自行把合同状态往上推一级。**
- **冻结资产零改动**：evidence／skills／workflows／fixtures／references／运行合同／C1—C6／专家材料。需承接变化的冻结合同**另建后继版本或加更正说明**，不覆盖原文。
- 输出必须列明修改文件、删除或重命名文件、未决事项和一致性检查结果。

## 7. 协作连续性账本（换会话必读）

**开工前先读 [collab-ledger/COLLAB_CONTINUITY_PROTOCOL.md](collab-ledger/COLLAB_CONTINUITY_PROTOCOL.md)。** 它是本仓库协作连续性规则的**唯一正文**——五本账在哪、什么时候写、谁写、三类状态怎么分。**本文件只指路，不复制其规则正文。**

最短路径：canonical → [L2 状态与下一动作](collab-ledger/L2_TASK_STATE_AND_HANDOFF.md) → [L1 合同与边界](collab-ledger/L1_TASK_MANIFESTS.md) → [L4 已排除路线](collab-ledger/L4_FAILED_PATHS.md)。
