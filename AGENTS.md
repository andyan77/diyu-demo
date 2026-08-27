# AGENTS.md — /home/faye/diyu-demo

> **ROLE IS SELECTED BY TASK AUTHORITY, NOT BY TOOL BRAND.**

本仓库是笛语 Demo 的**执行事实仓库**：工程实现、Git、运行状态与原始证据的所在地。
仓库身份是载体，**不分配角色**。Claude Code、Codex 及未来兼容 Agent 都可能被当前
Task Contract 指派为 `PLANNING`、`EXECUTION` 或 `REVIEW`。

角色只由 **Project Profile + 当前 Task Contract + 当前授权** 决定。
更换工具、窗口、模型或终端本身不产生新 `task_id`，不重置 Attempt，不构成 `REBASE`。

## 1. 当前 Task Contract 指定 `PLANNING`

- 对 `/home/faye/diyu-demo` **只读**。
- 可以：核验实现、读取证据与账本、生成或审查规划交付。
- 不得：修改本仓库任何文件、Git 状态、分支、项目账本，或修改 Dify、数据库、运行环境。
- 不得把 Prompt 编译说成工程施工。
- 加载 v1.2（当 Profile 采用该协议时），不加载 v1.3 全文。

## 2. 当前 Task Contract 指定 `REVIEW`

- 按当前 Review Contract 与**冻结**标准评审。
- 不得新增产品语义、验收标准、授权或 HOW。
- **是否允许写评审记录，由当前合同明确规定**；合同未授权即不得写入本仓库。
- 加载 Review Contract 指明的项目协议，不加载无关角色协议全文。

## 3. 当前 Task Contract 指定 `EXECUTION`

- 加载：项目 Profile、v1.3（当 Profile 采用该协议时）、准确的 Task Contract。
- 可以：在授权 BOUNDARY 内自主选择 HOW，修改、测试、换路、留证。
- 不得改变 `WHAT / WHY / BOUNDARY / ACCEPTANCE`、产品语义、授权或冻结 Oracle。

## 4. 当前角色未声明

- **不得仅根据 Codex / Claude Code 品牌推断角色。**
- 依次判断：① Project Profile → ② 当前 Task Contract → ③ Execution Prompt / Review Contract
  → ④ 前序任务身份与明确交接 → ⑤ 当前授权措辞。
- 若上述信息能唯一推出角色，执行侧自行装配，不问卷。
- 只有在无法无歧义判断，**且不同角色会改变权限、验收或授权范围**时，才提一个决定性问题。

## 5. 治理指针

完整真源指针、加载条件与边界依据见本仓库 [`CLAUDE.md`](CLAUDE.md) §0，此处不重复。

规划与执行边界的正文在规则侧 `PROJECT_PROFILE.md`（真源，位于
`/mnt/c/Users/Administrator/Documents/Codex/Diyu-V1-Planning/projects/APP-DIYU-DEMO/`），
本文件不复制其正文。

Constitution 分发身份：`tag=v0.3.1-revision-2` / `commit=34d10a052767fe5cbc2ceebc236e2ad17e2d1885`
激活事件：`RULESIDE-2026-08-25-005`
