# 笛语 / diyu

服装零售内容生产的 Skill 系统。

## 当前状态

| | |
|---|---|
| **当前阶段** | **V1 决策链重对齐（Rebase）**。Dify Demo A/B 对照阶段已结束并按 `PARTIAL` 冻结 |
| **上位合同** | [V1 决策链改造产品合同](decision-chain/docs/V1_DECISION_CHAIN_REBASE_PRODUCT_CONTRACT_v0.1.md) —— `PRODUCT_CONTRACT_ACCEPTED — REPO_PREFLIGHT_AUTHORIZED`，**只授权只读预检，不授权施工** |
| **纵向切片子合同** | [单账号持续内容运营](decision-chain/docs/V1_SINGLE_ACCOUNT_SLICE_CONTRACT_v0.1.md) —— `CONTRACT_REVISION_REQUIRED`，**尚未被 Founder 接受，不构成授权** |
| **两条能力链** | 决策链与内容生产链**都在产品范围内**，都已建成并在运行；**不存在「唯一活跃主线」** |
| **下一步** | `V1-REBASE-EP00-CURRENT`（上位合同已授权的只读仓库预检） |

**上位合同被接受 ≠ 子合同被接受，也 ≠ 授权 Skill、DSL、持久化或工作流施工。**

## 从哪里开始

- **[PROJECT_INDEX.md](PROJECT_INDEX.md)** —— 资产索引与文档管理规则
- **[V1 决策链改造产品合同](decision-chain/docs/V1_DECISION_CHAIN_REBASE_PRODUCT_CONTRACT_v0.1.md)** —— 当前产品方向、组件职责、验收与非目标（**最高真相源**）
- **[单账号持续运营纵向切片子合同](decision-chain/docs/V1_SINGLE_ACCOUNT_SLICE_CONTRACT_v0.1.md)** —— 第一纵向切片，待接受
- **[决策链当前阶段基线 v0.2](decision-chain/docs/V1_DECISION_CHAIN_STAGE_BASELINE_v0.2.md)** —— 当前阶段状态；旧 [v0.1](decision-chain/docs/V1_DECISION_CHAIN_STAGE_BASELINE_v0.1.md) 原样保留为历史
- **[内容生产链 PRD](content-production/docs/CONTENT_PRODUCTION_CHAIN_PRD_v0.1.md)** —— 生产链入口
- **[决策链三份 Skill](decision-chain/skills/)** —— Matrix Architect、Campaign Orchestrator、Content Brief Architect
- **[内容生产三份 Skill](content-production/skills/)** —— Creative Script（`writing-creative-scripts`）、Production Director（`directing-content-production`）、Publishing & Packaging（`packaging-content-for-release`），各自自包含，可独立安装
- [笛语项目基线.md](笛语项目基线.md) —— §〇 当前阶段与生效口径；§一起为历史沿革与长期裁决
- [CLAUDE.md](CLAUDE.md) —— 协作规则与硬约束
