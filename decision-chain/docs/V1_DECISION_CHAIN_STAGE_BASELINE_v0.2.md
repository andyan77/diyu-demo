# 决策链当前阶段基线 v0.2

> **本文件是决策链的当前阶段基线。** 旧 [`V1_DECISION_CHAIN_STAGE_BASELINE_v0.1.md`](V1_DECISION_CHAIN_STAGE_BASELINE_v0.1.md) **原样保留为历史，不修改、不废弃**——它记录的是 A/B 对照阶段的 `PARTIAL` 结论，那段历史仍然成立。
>
> 本文件只回答一件事：**现在处在哪个阶段、什么已被接受、授权到哪里为止。**

---

## 一、当前状态

| 项 | 值 |
|---|---|
| 阶段 | **V1 决策链重对齐（Rebase）** |
| 上位合同 | [`V1_DECISION_CHAIN_REBASE_PRODUCT_CONTRACT_v0.1.md`](V1_DECISION_CHAIN_REBASE_PRODUCT_CONTRACT_v0.1.md) |
| 上位合同状态 | `PRODUCT_CONTRACT_ACCEPTED — REPO_PREFLIGHT_AUTHORIZED` |
| 纵向切片子合同 | [`V1_SINGLE_ACCOUNT_SLICE_CONTRACT_v0.1.md`](V1_SINGLE_ACCOUNT_SLICE_CONTRACT_v0.1.md) |
| 子合同状态 | `CONTRACT_REVISION_REQUIRED`——**尚未被 Founder 接受** |
| 当前授权范围 | **只读仓库预检 `V1-REBASE-EP00-CURRENT`** |
| 明确未授权 | Skill 修改、DSL 改造、业务持久化建设、Dify 工作流施工、子合同专项预检 |

**三条不能混淆的事实：**

1. 上位合同**已被接受**，但它授权的**只有只读预检**；
2. 上位合同被接受**不等于**子合同被接受；
3. 文档语义对齐**不等于**授权施工。

---

## 二、A/B 对照阶段的结论（继续有效，不重复展开）

该阶段结论**原样保留在 [v0.1](V1_DECISION_CHAIN_STAGE_BASELINE_v0.1.md)**：状态 `PARTIAL`，10 个重点场景 7 过 3 未过，40 类场景 25 过 9 未过 6 未运行，能力边界六条禁止声明**继续有效**。

**v0.1「阶段转移」一节所写的「项目唯一活跃建设主线正式切换为内容生产链」已被本基线取代**：决策链与内容生产链**都在产品范围内**，不存在唯一主线。v0.1 原文不修改。

---

## 三、A/B 阶段之后已经发生的运行变化

以下变化**已经部署并有运行证据**，不是计划：

| 变化 | 证据 |
|---|---|
| 决策链三 Skill 与内容生产两段链**集成进同一条主 Chatflow**（56 节点、9 个会话变量） | [`../workflows/DIYU_DEMO_V1_FULL_CHAIN_CHATFLOW_v0.2.yml`](../workflows/DIYU_DEMO_V1_FULL_CHAIN_CHATFLOW_v0.2.yml) |
| **对话编排修复 001**：确认＋授权句式可落定任务；假「已经记下」claim 已消除；新增一轮多诉求（`side_question` / `open_threads`）与撤销最近一次接受（`last_acceptance`） | [`../evidence/V1_DIALOGUE_ORCHESTRATION_REPAIR_001_EVIDENCE.md`](../evidence/V1_DIALOGUE_ORCHESTRATION_REPAIR_001_EVIDENCE.md) —— 状态 `DONE`，A-0～A-4 与最小回归全部在真实 Dify 对话中跑过 |
| 三份决策 Skill 的产物**对用户可见**（生成即展示，不再只存会话变量） | 同上 DSL 的 `fin_matrix` / `fin_campaign` / `fin_content_brief` 节点 |

**这三项都不修改 v0.1 的历史结论**，它们发生在 v0.1 冻结之后。

---

## 四、已登记但仍未关闭的事项

| 类别 | 位置 |
|---|---|
| 生产差距 G-01～G-12，**12 项全部未关闭** | [`V1_PRODUCTION_GAP_REGISTER_v0.1.md`](V1_PRODUCTION_GAP_REGISTER_v0.1.md) |
| A/B 阶段「未完成」七项 | [v0.1 第 34—42 行](V1_DECISION_CHAIN_STAGE_BASELINE_v0.1.md) |
| 「I-03」 | 全仓库与全部提交穷尽检索**查无此项**，如实登记，不强行对应 |

---

## 五、能力边界（继续禁止声称）

沿用 v0.1，一条不减：

- V1 已全面通过；
- 三份 Skill 集成后质量没有下降；
- DeepSeek 普遍优于 Qwen；
- Skill 普遍优于无 Skill；
- 当前结果可跨品牌、跨行业推广；
- 当前系统已经具备生产可用性。

**追加两条（Rebase 阶段新增）：**

- 不得声称子合同已被接受；
- 不得声称已完成 `V1-REBASE-EP00-CURRENT` 预检——**它尚未开展**。

---

## 六、下一步

`V1-REBASE-EP00-CURRENT`：基于当前 `main`、真实 Dify 与当前部署的**只读**预检。核验清单见上位合同「授权状态与下一步」一节。

子合同专项预检 `SINGLE-ACCOUNT-SLICE-EP00` **必须等子合同被 Founder 接受之后**才能开展。

历史初步侦察 `AO-EP00-HISTORICAL`（`feature/account-operation-v1 @ df94ed1`）**只作参考，不得冒充当前预检，也不得直接合入 `main`**。
