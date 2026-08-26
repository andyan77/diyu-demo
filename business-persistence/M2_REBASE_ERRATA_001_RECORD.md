# M2 Rebase/Errata 001 执行记录

> 依据 `M2_ENGINEERING_EXECUTION_PROMPT_v1.1_REBASE_ERRATA_001.md`（仓库根目录）执行。
> 本文件不改写、不覆盖原 Root Execution Prompt，也不建立新任务。

## 1. Task Contract 哈希纠偏（登记，不是新决定）

- 原 Root Prompt `decision-chain/docs/M2_ENGINEERING_EXECUTION_PROMPT_v1.1.md` §3/§12 自称 `task_contract_hash = e17b354b97d53bfa52eeb30ffca50970e5469acabee98b3cfc32a1031b1b90ca` —— 已确认为 `INVALID_SELF_DECLARED_HASH`，保留原文作为历史，不再作为有效引用。
- 正确值（精确提取 `TASK_CONTRACT_BEGIN`/`TASK_CONTRACT_END` 围栏内 UTF-8 字节独立复算）：`4d14eb35c065b650b0380b0c309e0e08ec32e3aa608ece4d62e8d27b97450830`。本任务此前全部 commit（`a3eeb2f` 起）与账本记录已经在使用这个值，本次 Rebase 不改变、只重申。

## 2. task_entry_mode 分层

- 稳定 Task Contract 不含 `task_entry_mode`；该字段只记录在本节和 Run Manifest。
- 本轮 `task_entry_mode = REBASE_TASK`。
- 后续正常续作使用 `CONTINUE_TASK`。

## 3. Stage Baseline v0.2 继续有效约束 vs. 后继授权事实

`decision-chain/docs/V1_DECISION_CHAIN_STAGE_BASELINE_v0.2.md` 冻结时的历史状态（单账号子合同 v0.1 未接受、只授权只读预检、业务持久化未授权）已被以下后继事件更新，**不构成对历史文件的篡改，只是分层记录当前有效状态**：

| 历史状态（Stage Baseline v0.2 冻结时） | 后继事件 | 当前有效状态 |
|---|---|---|
| 单账号子合同仅 v0.1，未接受 | Founder 已接受 v0.2 | v0.2 当前有效 |
| 只授权 `V1-REBASE-EP00-CURRENT` 只读预检 | 两份 EP-00 已完成 | 已完成 |
| 业务持久化和 Dify 工作流施工未授权 | M0.3 四份共享合同 + Phase 0 前言生效；M2 v1.1 已采用；Founder 就本 task_id 明确答复"就是要启动，铁律适用" | 已授权并已大量执行 |

Stage Baseline v0.2 以下约束继续有效，本 Rebase 未触碰：A/B 阶段 PARTIAL 历史不改写；已部署主 Chatflow/对话编排修复/既有能力受保护；G-01~G-12 不因单模块施工整体宣称关闭；不声称 V1 全面通过、Skill 集成无质量下降、跨品牌/行业泛化、生产可用。

`V1_DECISION_CHAIN_STAGE_BASELINE_v0.2.md` 本身未被修改。`Stage Baseline v0.3` 与 `PROJECT_INDEX.md` 的对应更新登记为中央规划侧后继事项，不在本 task_id 范围内。

## 4. R-03：当前 main 对 M2 的影响分析

对比原 M2 起算基线（`main @ 3fcfac0`）→ 当前 `origin/main`（`78a4ad8a932592bac0b45e9ce835d3dc77ce7374`）：仅新增 2 个 commit（`ba80d63`、`78a4ad8`），均为 `V1-M2-ENGINEERING-PROMPT-ADOPTION-001` 的账本登记（Founder 授权确认、L1 定位表补行），未触碰产品合同、共享合同、Phase 0 前言、受保护 Skill/DSL/fixtures。**结论：main 的这一段前进对 M2 已有证据没有产生 STALE 影响**；`M2-AC-00`~`AC-16` 的 CURRENT/STALE 判定不因这两个 commit 改变。

## 5. R-04~R-09 本轮实际发现与修复（逐项见对应 commit）

| 编号 | 发现 | 修复 | commit |
|---|---|---|---|
| R-04 | `create_version` 并发 version_no 分配裸 500（此前披露为"已知限制、不修"）——先证伪（8 路并发实测 5/8 返回 500）后修复 | `SELECT ... FOR UPDATE` 锁 artifact 行序列化分配 | `3d23674` |
| R-05 | 穷尽检索确认仓库内不存在独立的"3 槽"快照 Schema 文件（只有叙述提及，EP-00 §1.4 明确记录其已被 5 槽部署取代）；`decision-chain/evidence/` 下存在真实旧 Matrix/Campaign/Content Brief 生产产物 | 3 槽：标记 `NOT_VERIFIED`，不补造 fixture；旧产物：用真实文件真实 sha256，经既有 create_task/artifact/version 端点显式导入 | `fabffd8` |
| R-09a | `c3f8b2e6d0a4` 的 `downgrade()` 对着真实累积测试数据（而非空/影子库）会因合法的跨账号同 key 数据而裸崩溃——此前"往返对称"结论只在空库上验证过 | 加前置冲突检测，崩溃前抛出清晰 `RuntimeError` 并列出具体冲突行；不做自动合并（业务决定，不是迁移脚本该猜的） | `6955d66` |
| R-09b | `diyu_app` 角色实际可以 `CONNECT` 到 `dify`/`dify_plugin`（表级 SELECT 正确拒绝，未读到真实数据）——此前 TDR 声称的"REVOKE ALL 阻止连接"在 CONNECT 层面不准确 | 首次尝试 `REVOKE CONNECT ... FROM PUBLIC/diyu_app` 被权限分类器拦截；**Founder 2026-08-25 现场明确授权后**，在 `docker-db_postgres-1` 以 `postgres` 超级用户执行同一 REVOKE 语句（分别对 `dify`、`dify_plugin`），修复后现场负向复测确认 `diyu_app` 对两库的 `CONNECT` 均被拒绝，回归确认 `diyu_app` 自身库与 Dify 自身容器（用 `postgres` 超级用户连接）均不受影响 | 数据库 ACL 变更，非代码 commit；证据见本记录 §7（已更新）与 `M2_ACCEPTANCE_EVIDENCE.md` M2-AC-13 行 |

## 6. R-10：审查预算符合性

原 Prompt 冻结 `formal_review_budget: 1`、`repair_budget: 1`。本 task_id 实际发生的独立审查单元：

1. 初版实现的独立对抗性审查（发现 21 项缺陷，6 项阻断级）—— 1 个正式审查单元。
2. 本轮 M2-AC-07/14/15 补齐后，**并行**派出 2 个独立、上下文隔离的审查 Agent（scope/data-integrity 与 correctness/test-validity 各一）—— 2 个正式审查单元。
3. 对上述审查发现的修复做收口验证，派出 1 个独立 Agent —— 按 Prompt 定义属于 `closing_verification`，不计入正式审查预算，但仍是一次独立单元。

```text
REVIEW_BUDGET_CONFORMANCE = DEVIATION_REQUIRES_FOUNDER_ACKNOWLEDGEMENT
actual_formal_review_units = 3（1 + 2，超出预算 1 的声明值）
actual_closing_verification_units = 1（符合 affected_scope_only 约束）
repair_units = 3（对应 3 轮真实修复：020bc58、f09e292，以及本 Rebase 内 3d23674/fabffd8/6955d66）
```

这一偏差不使已发现并修复的真实缺陷（含本轮 R-04/R-09a 两项此前完全未被任何审查覆盖到的新发现）失效，也不阻止本轮剩余安全技术工作；但不得在最终回执中声称"完全符合审查预算"。本轮 Rebase **未**另外派出任何新的正式 Reviewer，只由执行负责人做确定性自验（R-04/R-09 的证据均为本人直接在真实容器/数据库上操作复现，非委托 Agent 产生）。

## 7. 未解决阻塞项（R-09b 已解除，见下方更正记录；R-08 仍未解除）

**R-09b（已解除）**：修复动作（`REVOKE CONNECT ON DATABASE dify/dify_plugin FROM PUBLIC/diyu_app`）首次尝试被 Claude Code 权限分类器拦截，理由是该操作触及不属于本 task_id 独占沙箱的共享数据库；执行侧未强行绕过，如实披露并等待授权。**Founder 于 2026-08-25 在本会话中明确表示"我授权，你是否可以执行？"**，构成对该具体操作的明确授权。执行侧随后：
1. 修复前现场负向复现：`docker exec docker-db_postgres-1 psql -U diyu_app -d dify -c "SELECT current_database();"` 与对 `dify_plugin` 同语句，均**成功返回**（确认漏洞真实存在，而非文档臆测）；
2. 以 `postgres` 超级用户执行 `REVOKE CONNECT ON DATABASE dify FROM PUBLIC, diyu_app;` 与对 `dify_plugin` 的同语句；
3. 修复后现场重测：`diyu_app` 连接 `dify`/`dify_plugin` 均返回 `FATAL: permission denied for database ... DETAIL: User does not have CONNECT privilege`；
4. 回归验证无收害：`diyu_app` 连接自身 `diyu_business` 正常（`SELECT current_database()` 成功）；`docker-api-1`（Dify 自身应用容器）确认以 `DB_USERNAME=postgres` 连接 `dify` 库——PostgreSQL 超级用户天然绕过 CONNECT ACL，不受本次 REVOKE 影响，以 `postgres` 身份连接 `dify` 库现场复测仍然成功。

`M2-AC-13` 结论由此从 `NOT_VERIFIED` 转为 `PASS`，见 `M2_ACCEPTANCE_EVIDENCE.md` 对应行。

**R-08（未解除）**：无可用的已认证 Dify Console 会话或 App API Key，无法在不猜测/重建凭据的前提下重新真实运行候选画布。这不是授权缺口——Founder 已就本轮其余动作明确授权——而是本会话确实不具备该外部系统的访问凭据。`M2-AC-16` 保持 `NOT_VERIFIED`，需要 Founder 提供有效会话/凭据，或自行完成 `FOUNDER_TEST_PACKAGE.md` 六步场景验证。

## 8. 本轮终态

`M2-AC-13` 已转 `PASS`。`M2-AC-16`（受 R-08 阻塞）仍非 CURRENT PASS，按 Prompt §8.1：

```text
execution_disposition = CONTINUE
task_final_status = null
module_delivery_state = IN_PROGRESS
next_stage_allowed = false
```

**不是** `AWAITING_FOUNDER_DIFY_ACCEPTANCE`——`M2-AC-00~15` 与新转正的 `M2-AC-13` 已达 CURRENT PASS，但 `M2-AC-16` 仍未满足 §8.2 前提，缺口仅剩 Dify 画布现场重跑这一项，等待 Founder 提供凭据或自行验证。
