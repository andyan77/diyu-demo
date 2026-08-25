# 笛语 / diyu

服装零售内容生产的 Skill 系统。

## 当前状态

| | |
|---|---|
| **当前阶段** | **V1 决策链重对齐（Rebase）**。Dify Demo A/B 对照阶段已结束并按 `PARTIAL` 冻结 |
| **上位合同** | [V1 决策链改造产品合同](decision-chain/docs/V1_DECISION_CHAIN_REBASE_PRODUCT_CONTRACT_v0.1.md) —— `PRODUCT_CONTRACT_ACCEPTED — REPO_PREFLIGHT_AUTHORIZED`，**只授权只读预检，不授权施工** |
| **纵向切片子合同** | [单账号持续内容运营 v0.2](decision-chain/docs/V1_SINGLE_ACCOUNT_SLICE_CONTRACT_v0.2.md) —— `ACCEPTED — SINGLE_ACCOUNT_SLICE_PREFLIGHT_AUTHORIZED`，已被 Founder 接受（v0.1 为历史版本） |
| **M0.3 四份共享合同** | [任务上下文快照](decision-chain/docs/V1_M0_SHARED_CONTRACT_TASK_CONTEXT_SNAPSHOT_v0.1.md)／[八项能力合同](decision-chain/docs/V1_M0_SHARED_CONTRACT_EIGHT_CAPABILITIES_v0.1.md)／[版本发布反馈归属](decision-chain/docs/V1_M0_SHARED_CONTRACT_VERSION_PUBLISH_FEEDBACK_v0.1.md)／[写回权限幂等恢复](decision-chain/docs/V1_M0_SHARED_CONTRACT_WRITE_PERMISSION_RECOVERY_v0.1.md) —— 均 `ACCEPTED`，授权 M1—M4 施工规划编译，**不授权工程实现本身** |
| **两条能力链** | 决策链与内容生产链**都在产品范围内**，都已建成并在运行；**不存在「唯一活跃主线」** |
| **下一步** | M0 已全部完成（通用预检 → 专项预检 → 四份共享合同）；下一步由规划侧编译 M1—M4 施工 Execution Prompt |

**上位合同被接受 ≠ 子合同被接受，也 ≠ 授权 Skill、DSL、持久化或工作流施工。**

## 从哪里开始

- **[协作连续性账本 · 规则正文](collab-ledger/COLLAB_CONTINUITY_PROTOCOL.md)** —— **换一个新会话来接手，先读这份**：任务做到哪、下一步做什么、什么不能碰、哪条路已走死
- **[PROJECT_INDEX.md](PROJECT_INDEX.md)** —— 资产索引与文档管理规则
- **[V1 决策链改造产品合同](decision-chain/docs/V1_DECISION_CHAIN_REBASE_PRODUCT_CONTRACT_v0.1.md)** —— 当前产品方向、组件职责、验收与非目标（**最高真相源**）
- **[单账号持续运营纵向切片子合同 v0.2](decision-chain/docs/V1_SINGLE_ACCOUNT_SLICE_CONTRACT_v0.2.md)** —— 第一纵向切片，已被 Founder 接受
- **[决策链当前阶段基线 v0.2](decision-chain/docs/V1_DECISION_CHAIN_STAGE_BASELINE_v0.2.md)** —— 当前阶段状态；旧 [v0.1](decision-chain/docs/V1_DECISION_CHAIN_STAGE_BASELINE_v0.1.md) 原样保留为历史
- **[内容生产链 PRD](content-production/docs/CONTENT_PRODUCTION_CHAIN_PRD_v0.1.md)** —— 生产链入口
- **[决策链三份 Skill](decision-chain/skills/)** —— Matrix Architect、Campaign Orchestrator、Content Brief Architect
- **[内容生产三份 Skill](content-production/skills/)** —— Creative Script（`writing-creative-scripts`）、Production Director（`directing-content-production`）、Publishing & Packaging（`packaging-content-for-release`），各自自包含，可独立安装
- [笛语项目基线.md](笛语项目基线.md) —— §〇 当前阶段与生效口径；§一起为历史沿革与长期裁决
- [CLAUDE.md](CLAUDE.md) —— 协作规则与硬约束
