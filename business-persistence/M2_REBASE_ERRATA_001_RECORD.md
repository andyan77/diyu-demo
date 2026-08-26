# M2 Rebase/Errata 001 执行记录

> 依据 `M2_ENGINEERING_EXECUTION_PROMPT_v1.1_REBASE_ERRATA_001.md`（原始位置：主仓库根目录，`sha256 = fbb65e1dcdb405a435f03fc8efa8f9828926d9881850aa7c86237bf267ef7c5d`）执行。
> 本文件不改写、不覆盖原 Root Execution Prompt，也不建立新任务。
>
> **更正（本次提交）**：该 Prompt 文件此前只在主工作区作为未跟踪文件存在，未进入本 M2
> 任务分支或远程——脱离本分支单独审计时无法追溯到实际授权本轮工作的文件。已按§6 授权
> 范围内的 `business-persistence/` 目录，原样字节复制（保留原 CRLF 换行、未改一字）进本
> 任务分支：[`M2_ENGINEERING_EXECUTION_PROMPT_v1.1_REBASE_ERRATA_001.md`](M2_ENGINEERING_EXECUTION_PROMPT_v1.1_REBASE_ERRATA_001.md)，
> `diff` 核验与原文件字节完全一致（哈希同为 `fbb65e1d...`）。**顺带发现**：该文件本身
> Markdown 结构有一处未闭合代码围栏（第 11 行开 ` ```yaml `，全文只有这一处围栏标记，
> 此后不再闭合），后续章节的类 YAML 片段也不带围栏——外观上像复制/转存时遗漏了闭合
> 标记，与该文件 CRLF 换行（提示原始编辑环境为 Windows）一致。**但逐行读到第 486 行
> 确认内容本身连续、完整、以正常的最终声明块结束（`task_entry_mode = REBASE_TASK`），
> 不是内容被截断——只是 Markdown 渲染格式有缺陷，不影响文件实际授权内容的可读性和完整
> 性。未修改原文件一字（不属于执行侧可裁量范围），仅如实记录这一格式缺陷。

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
| R-05 | 穷尽检索确认仓库内不存在独立的"3 槽"快照 Schema **文件**（只有叙述提及，EP-00 §1.4 提到"三槽旧 Schema 与五槽部署事实不一致"）；`decision-chain/evidence/` 下存在真实旧 Matrix/Campaign/Content Brief 生产产物。**更正（本轮补充授权后）**：当时止步于"无独立文件"就判定"3 槽对象不存在"是错误推论——直接读取 `V1_TASK_SNAPSHOT_SCHEMA_v0.1.json` 后确认其 `artifacts` 子对象真实拥有 3 个具名槽位（`matrix`/`campaign`/`content_brief`），对象本身真实存在，只是不作为独立文件存在；"5 槽"实际指同一 Schema 里可选字段 `last_acceptance.slot` 的 5 值枚举（后续扩展新增 `production_stage1`/`publishing_stage2`），与 `artifacts` 的 3 槽是两个不同字段，此前混为一谈 | 3 槽（`artifacts`）：结构已被 legacy-import 端点正确校验导入，此前错误标注为 `legacy_dify_5slot_import`，已更正为 `legacy_dify_v1_task_snapshot_import`；旧产物真实内容：用真实文件真实 sha256，经既有 create_task/artifact/version 端点显式导入；可选字段 `last_acceptance.slot`（5 值枚举）未被任何现有夹具覆盖，如实标记为已知窄口径缺口，非阻断项 | `fabffd8`（内容导入）；命名更正见本次 commit |
| R-09a | `c3f8b2e6d0a4` 的 `downgrade()` 对着真实累积测试数据（而非空/影子库）会因合法的跨账号同 key 数据而裸崩溃——此前"往返对称"结论只在空库上验证过 | 加前置冲突检测，崩溃前抛出清晰 `RuntimeError` 并列出具体冲突行；不做自动合并（业务决定，不是迁移脚本该猜的）。**更正（本轮补充授权后）**：此前把这一修复描述为"迁移链本身正确、可逆"是过度声明——崩溃变清晰拒绝是真实改进，但清晰拒绝时 downgrade **仍不能完成**，不满足 AC-13 原文"失败可恢复/回滚"字面要求。已将 `M2-AC-13` 此维度的结论如实更正为 `NOT_VERIFIED`（而非此前误写的"迁移链可逆"），见 `M2_ACCEPTANCE_EVIDENCE.md` AC-13 行；是否要为此另行实现一套自动改键策略，需要 Founder 就"跨账号冲突时如何处理共享 idempotency_key"给出业务裁决，执行侧不会不经授权自行发明这条规则 | `6955d66` |
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

`M2-AC-13` 的 CONNECT 权限子维度由此从"可以连接"转为"正确拒绝"，但 `M2-AC-13` **整体**结论保持 `NOT_VERIFIED`——见上方 R-09a 更正：迁移降级恢复维度未达标，任一子维度不达标即整体不判 PASS，见 `M2_ACCEPTANCE_EVIDENCE.md` AC-13 行。

**R-08（已解除）**：Founder 主动提供该候选应用（`app_id: 8f34e8a3-fb49-4d3e-a222-3d666e767adf`）专属的 App API Key（未索要 Console 会话或账号密码）。执行侧用该 Key 调用 Dify 自身 Service API `POST /v1/workflows/run`，真实触发 Dify 引擎执行同一份已发布 workflow 定义——这是真实画布重跑，不是绕开 Dify 直接调用 M2 后端的"API 等价证据"（R-08.8 明文禁止的正是后者）。运行结果：`workflow_run_id: 1f123c37-c51c-4dad-a96c-e0696bd8b2e3`，`status: succeeded`，`total_steps: 16`，对照 `FOUNDER_TEST_PACKAGE.md` 的 9 项判断标准逐项核验全部满足（详见 `M2_ACCEPTANCE_EVIDENCE.md` AC-16 行）。`M2-AC-16` 由 `NOT_VERIFIED` 转为 `PASS`。

## 8. 本轮终态

`M2-AC-16` 已转 `PASS`。`M2-AC-13`（受迁移降级恢复维度未达标阻塞）仍非 CURRENT PASS——CONNECT 权限子维度已修复，但这不足以让整体 AC 判 PASS。按 Prompt §8.1：

```text
execution_disposition = CONTINUE
task_final_status = null
module_delivery_state = IN_PROGRESS
next_stage_allowed = false
```

**不是** `AWAITING_FOUNDER_DIFY_ACCEPTANCE`——`M2-AC-00~12`、`M2-AC-14~16` 已达 CURRENT PASS（`AC-17` 为预期非终态），但 `M2-AC-13` 的迁移降级恢复维度仍未满足 §8.2 前提。剩余缺口需要 Founder 决定：(a) 明确授权一套具体的跨账号冲突自动改键/合并规则，由执行侧实现并测试；或 (b) 接受"清晰拒绝＋人工介入"为最终设计，并同意将 `M2-AC-13` 原文"失败可恢复/回滚"的达标口径正式改写——这一改写超出执行侧单方面裁量范围，需要 Founder 或合同层面裁决。
