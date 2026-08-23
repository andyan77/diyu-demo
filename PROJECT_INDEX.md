# 项目资产索引

本文件只做两件事：**说明东西放在哪**，以及**写清加新文件的规矩**。

---

## 一、资产到哪里找

仓库按「两个业务模块 + 五类资产」组织。

| 模块 | 说明 |
|---|---|
| [decision-chain/](decision-chain/) | 决策链：Matrix Architect、Campaign Orchestrator、Content Brief Architect。**已冻结，非活跃主线** |
| [content-production/](content-production/) | 内容生产链：Creative Script、Production Director、Publishing & Packaging。**当前唯一活跃主线** |
| [tools/](tools/) | 通用辅助脚本 |

每个模块下最多五类：

| 目录 | 放什么 |
|---|---|
| `docs/` | 合同、Golden、正式决策说明、状态说明、阶段基线、专家问答与研究材料 |
| `skills/` | Skill 正文 |
| `workflows/` | Dify 工作流 DSL |
| `fixtures/` | 品牌夹具、固定输入、场景输入 |
| `evidence/` | RAW、FINAL、TRACE、EVAL、Manifest、盲审材料、测试应用 |

### 常用入口

| 要找的东西 | 去哪 |
|---|---|
| 项目定位、阶段与 Founder 已裁决事项 | [笛语项目基线.md](笛语项目基线.md) |
| 协作规则与硬约束 | [CLAUDE.md](CLAUDE.md) |
| **决策链 V1 当前状态（含已知问题与能力边界）** | [decision-chain/docs/V1_DECISION_CHAIN_STAGE_BASELINE_v0.1.md](decision-chain/docs/V1_DECISION_CHAIN_STAGE_BASELINE_v0.1.md) |
| **内容生产链入口（当前主线）** | [content-production/docs/CONTENT_PRODUCTION_CHAIN_PRD_v0.1.md](content-production/docs/CONTENT_PRODUCTION_CHAIN_PRD_v0.1.md) |
| 三份决策 Skill 正文 | [decision-chain/skills/](decision-chain/skills/) |
| **内容生产三份 Skill（活跃主线）** | Creative Script → [content-production/skills/writing-creative-scripts/](content-production/skills/writing-creative-scripts/)<br>Production Director → [content-production/skills/directing-content-production/](content-production/skills/directing-content-production/)<br>Publishing & Packaging → [content-production/skills/packaging-content-for-release/](content-production/skills/packaging-content-for-release/) |
| **共享 references 正式主本** | [content-production/references/](content-production/references/) |
| **内容生产运行合同（九槽位／人工回改／manifest）** | [content-production/docs/CONTENT_PRODUCTION_RUNTIME_CONTRACT_v0.1.md](content-production/docs/CONTENT_PRODUCTION_RUNTIME_CONTRACT_v0.1.md) |
| V1 集成合同 | [decision-chain/docs/V1_DEMO_INTEGRATION_CONTRACT_v0.1.md](decision-chain/docs/V1_DEMO_INTEGRATION_CONTRACT_v0.1.md) |
| 品牌夹具（序里集） | [decision-chain/fixtures/](decision-chain/fixtures/) |
| V1 全部运行证据与盲审材料 | [decision-chain/evidence/](decision-chain/evidence/) |

---

## 二、文档管理规则

1. 新文件**先按业务模块归类，再按 `docs` / `skills` / `workflows` / `fixtures` / `evidence` 归类**。
2. **根目录不再堆放业务文档。**
3. 同一个事实**只保留一个正式来源**，其他文件用链接，**不复制正文**。
4. RAW、FINAL、TRACE、EVAL、Manifest 和盲审材料属于**冻结证据，只能移动，不能改正文**。
5. 普通进度**直接更新模块现有状态文档**，不为每次工作新建总结。
6. 只有 **Skill、合同或正式能力发生实质变化**时才建立新版本。
7. 过程汇报、临时分析、重复总结**不进入仓库**。
8. **没有实际资产时不建立空目录。**
9. 修正历史证据**只能新增更正说明，不得修改原文件**。
10. 如果现有分类已经能够快速找到文件，**不再继续细分目录**。

**不建立**复杂的文档状态机、登记表、审批流或多层索引。历史依靠 Git 追溯，不建 archive 体系。

### Skill 与 references 维护

三份 Skill 各自保持自包含；共享 references 的正式主本位于 `content-production/references/`。修改 references 时，必须在同一提交中同步三个 Skill 内副本并核对哈希。
