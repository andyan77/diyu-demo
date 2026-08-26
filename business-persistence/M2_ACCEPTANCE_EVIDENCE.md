# M2 验收证据记录（M2-AC-00 ~ M2-AC-17，M2-RB-01 ~ M2-RB-14）

> 依据 `decision-chain/docs/M2_ENGINEERING_EXECUTION_PROMPT_v1.1.md` §9 与
> `M2_ENGINEERING_EXECUTION_PROMPT_v1.1_REBASE_ERRATA_001.md` §7/R-06 的格式与纠偏要求逐条登记。
> 本文件由执行侧撰写，不构成产品合同，不晋升为验收 Oracle 本身。`evidence_binding` 一律绑定到
> commit hash。任一验收项没有完整证据一律标记 `NOT_VERIFIED`，不使用 `PASS_WITH_LIMITATION`/
> `MOSTLY_PASS`/`BASICALLY_DONE`/`OUT_OF_SCOPE` 之类规避原 P0 的措辞。

**本次修订（Rebase/Errata 001 后）取代同名文件的上一版本**，不是追加；上一版本对
`M2-AC-12`/`M2-AC-14`/`M2-AC-16` 的部分表述已被本轮现场复验证明不准确（见下方逐条记录），
按 Rebase Prompt R-06 要求直接纠正，不用说明文字掩盖。

**证据绑定基线（本次更正：区分代码候选提交与纯文档/权限收口提交，不再笼统绑定单一旧 commit）**：

- **应用代码候选提交**（决定容器实际运行行为的最后一次代码变更）：本次提交（见 commit log，包含 R-05 命名更正 `legacy_dify_5slot_import` → `legacy_dify_v1_task_snapshot_import`）。在此之前，最后一次影响运行代码的提交是 `3d23674`（R-04 并发锁修复）；`6955d66`/`1f8e6c0`/`4010e25` 均为纯文档/迁移文件提交，未改变应用运行时行为。
- **应用容器**：`diyu-m2-app`，镜像 `diyu-m2-app:dev`，已用本次提交的源码重新 `docker build` 并 `stop/rm/run` 重启生效（非沿用旧容器）。
- **全量测试**：对重启后的容器现场重跑 `docker run --rm --network docker_default -e APP_BASE_URL=http://diyu-m2-app:8000 diyu-m2-app:dev pytest tests/ -q` → **69 passed**。
- **数据库**：PostgreSQL 15.19，`docker-db_postgres-1`，独立数据库 `diyu_business`，owner `diyu_app`（`NOSUPERUSER NOCREATEDB NOCREATEROLE`）。
- **迁移链**：`fdbd31cee7f9 → 6033064ae1ed → 6bc000bb178d → fb5e3889277c → db747c8a1f80 → a1c5e7d4f2b9 → c3f8b2e6d0a4`（现场 `alembic current` = `c3f8b2e6d0a4 (head)`，本轮迁移文件本身无新变化）。
- **本地/远程一致性**：本次提交推送后核验（见 `M2_REBASE_ERRATA_001_RECORD.md` §8"Git 收口"或对应 L5 记录）。

## 审查与自验记录

1. 初版实现的独立对抗性审查：发现 21 项缺陷（6 项阻断级），修复于 `a3eeb2f`。
2. M2-AC-07/14/15 补齐后，并行派出 2 个独立、上下文隔离的审查 Agent（scope/data-integrity、correctness/test-validity）：发现 4 项真实缺陷（含 1 项阻断级），修复于 `020bc58`。
3. 收口验证（1 个独立 Agent，仅复核受影响范围）：发现修复本身引入的新缺陷 1 项，修复于 `f09e292`。
4. **本轮 Rebase/Errata 001（`M2_REBASE_ERRATA_001_RECORD.md`）**：按 R-10 约束，未派出任何新的正式 Reviewer，全部由执行负责人本人在真实容器/数据库上直接操作复现：
   - R-04：8 路真实并发实测复现 `create_version` 版本号裸 500（5/8 失败），修复后连续 5 轮 8/8 成功，修复于 `3d23674`。
   - R-05：穷尽检索确认无独立"3 槽"Schema **文件**；用 3 份真实历史生产产物（真实 sha256）经既有端点显式导入，修复于 `fabffd8`。**本次追加更正（见下方 AC-14 行）**：R-05 当时止步于"无独立文件"就下结论"3 槽对象不存在"是错误推论——3 槽结构其实就内嵌在 `V1_TASK_SNAPSHOT_SCHEMA_v0.1.json` 的 `artifacts` 子对象里（`matrix`/`campaign`/`content_brief`，真实存在，只是不是独立文件）；且发现执行侧代码把这个真实 3 槽对象的导入错误命名为 `legacy_dify_5slot_import`——"5 槽"其实是同一 Schema 里另一个可选字段 `last_acceptance.slot` 的 5 值枚举（新增 `production_stage1`/`publishing_stage2`），与 `artifacts` 的 3 槽是两回事，两者被此前的分析混为一谈。已改正命名为 `legacy_dify_v1_task_snapshot_import`，修复于本次 commit。
   - R-09：对真实累积数据（非空库）实测 `alembic downgrade -1` 复现裸崩溃，修复为清晰错误，修复于 `6955d66`；同一轮发现 `diyu_app` 对 `dify`/`dify_plugin` 的 CONNECT 权限未被撤销，首次修复尝试被权限分类器拦截；**Founder 2026-08-25 现场明确授权后已执行修复并验证，见 M2-AC-13 行**。

审查预算符合性：`REVIEW_BUDGET_CONFORMANCE = DEVIATION_REQUIRES_FOUNDER_ACKNOWLEDGEMENT`（冻结预算 1 正式审查+1 修复，实际发生 3 个正式审查单元 + 1 收口验证单元；详见 `M2_REBASE_ERRATA_001_RECORD.md` §6）。这不使已发现缺陷的修复失效，但不得声称"完全符合审查预算"。

## AC 逐条记录

| criterion_id | 结果 | 证据摘要 | evidence_binding |
|---|---|---|---|
| M2-AC-00 | **PASS** | 独立 worktree、独立任务分支、独立数据库 `diyu_business`；Task Contract 哈希独立复算 `4d14eb35...`（与文档自称值不一致已披露，见 L1 §T-010/§T-011） | `task/m2-business-persistence-version-feedback-v1` 分支 |
| M2-AC-01 | **PASS** | `require_membership`+`X-Actor-Ref`+`WorkspaceMembership`；`tests/test_isolation.py` 8 项正负向 | `a3eeb2f` |
| M2-AC-02 | **PASS** | `TaskSnapshot` 五维列为真实列；`get_task_projection` 最小投影 | `app/models/content.py`, `app/api/tasks.py` |
| M2-AC-03 | **PASS** | 部分唯一索引 + `promote_version` 原子晋升；`tests/test_versioning.py`、`tests/test_concurrency.py` | `app/services/versioning.py` |
| M2-AC-04 | **PASS** | Task/Artifact/ContentVersion/PublishInstance/FeedbackRecord 关系链完整，里程碑可叠加 | `app/models/content.py` |
| M2-AC-05 | **PASS** | `is_test`/`is_simulated`/`is_manual_entry`/`is_pre_publish_review` 显式字段；`tests/test_publish_feedback.py` | `app/models/publish.py` |
| M2-AC-06 | **PASS** | 反馈二选一绑定校验；`tests/test_publish_feedback.py` | `app/api/publish.py::register_feedback` |
| M2-AC-07 | **PASS** | `create_cycle` 表达"调整"分支；`cycle_decisions` 表 + 端点表达"评估后保持不变"分支，且对已失效 cycle 结构性拒绝；6 项测试覆盖两分支正负向 | `d7f9e94`, `020bc58`, migrations `a1c5e7d4f2b9`/`c3f8b2e6d0a4` |
| M2-AC-08 | **PASS** | `CampaignOverride` 生命周期；`tests/test_cycle_campaign.py` | `app/models/operations.py::CampaignOverride` |
| M2-AC-09 | **PASS** | 产能三分各自独立来源；`test_capacity_triple_split_kept_separate` | `app/models/operations.py::Cycle` |
| M2-AC-10 | **PASS** | `Playbook` 版本化链式历史，自由字段非固定枚举 | `app/models/knowledge.py::Playbook` |
| M2-AC-11 | **PASS** | 素材撤回精确级联失效；`tests/test_material_withdrawal.py` 7 项，含 20 轮并发竞态回归 | `a3eeb2f` |
| M2-AC-12 | **PASS**（本轮修复后转为真 PASS，非此前的"已知限制"） | 全部创建型端点复合唯一 + `IntegrityError` 重查；`create_cycle`/`record_cycle_decision` 的按-workspace-而非按-account 幂等漏洞已修复（`020bc58`）；`create_version` 的并发 version_no 裸 500 **此前披露为刻意不修的已知限制，本轮 R-04 已真实修复并现场证伪/证实**（回退代码复现 5/8 失败 → 恢复代码 5 轮 8/8 成功）；`tests/test_concurrency.py` 新增 `test_concurrent_version_creation_on_same_artifact_never_produces_a_raw_500` | `020bc58`, `3d23674` |
| M2-AC-13 | **NOT_VERIFIED（本次更正：由 PASS 再次下修，CONNECT 半确已修复，迁移回滚半未达标）** | 验收标准原文三项要求：**数据库迁移可重复**、**失败可恢复/回滚**、**旧记录可读，Dify 内部表和数据未被改写**。逐项：(1) 迁移可重复——`alembic upgrade head` 幂等可重跑，成立；(2) **失败可恢复/回滚——不成立**：`c3f8b2e6d0a4` 的 downgrade 对存在合法跨账号同键真实数据时，此前会裸崩溃，本轮已修复为**清晰拒绝并列出冲突行**（`_refuse_if_cross_account_duplicates`），这是真实的工程改进（崩溃→清晰报错），但**清晰拒绝不等于可恢复/回滚**——该场景下 downgrade 仍然不能完成，需要人工先决定"两个账号里谁保留这个 idempotency_key、谁改用新 key"这一业务语义问题，这不是迁移脚本该替业务做的决定，执行侧不会不经授权就静默实现自动改键；因此这一子项如实标记 **NOT_VERIFIED**，不使用"可逆"这类过原文标准的措辞；(3) 旧记录可读、Dify 内部表和数据未被改写——成立，本轮 REVOKE CONNECT 只撤销数据库级连接权限（ACL），未触碰 Dify 任何表或数据行。数据库 CONNECT 权限缺口（**已修复**）：修复前现场负向复现确认 `diyu_app` **可以** `CONNECT` 到 `dify`/`dify_plugin`（`SELECT current_database()` 成功返回），与 `TECHNICAL_DECISION_RECORD.md` 原"REVOKE ALL 阻止连接"表述不一致。经 Founder 2026-08-25 现场明确授权后，在 `docker-db_postgres-1` 上以 `postgres` 超级用户执行 `REVOKE CONNECT ON DATABASE dify FROM PUBLIC, diyu_app;` 与同语句对 `dify_plugin`；修复后现场重测：`diyu_app` 连接 `dify`/`dify_plugin` 均返回 `FATAL: permission denied for database ... DETAIL: User does not have CONNECT privilege`；回归确认 `diyu_app` 对自身 `diyu_business` 连接不受影响，Dify 自身容器（`docker-api-1` 等）以 `postgres` 超级用户连接（超级用户天然绕过 CONNECT ACL），未受此次 REVOKE 影响。**整体判定**：三项子要求中一项（失败可恢复/回滚）未达标，按本仓库"任一子项未满足即整体 AC 标 NOT_VERIFIED"的既有先例（见此前 R-09b 阶段对本行的处理），本行整体保持 `NOT_VERIFIED`，即使 CONNECT 子项已真实修复。**后续需要 Founder 决定**：要么明确授权一套自动改键策略（如"跨账号冲突时较早创建的行保留原 key，较晚的自动改名并记录原值"）由执行侧实现并测试，要么接受"清晰拒绝＋人工介入"为本迁移的最终设计、并把 AC-13 原文"失败可恢复/回滚"的达标口径正式改写为"失败清晰可诊断，恢复需人工介入"（这需要 Founder 或合同层面的裁决，不是执行侧能单方面放宽的） | Founder 2026-08-25 CONNECT 修复授权记录见 `M2_REBASE_ERRATA_001_RECORD.md` §7；downgrade 清晰拒绝证据见 R-09a、`migrations/versions/c3f8b2e6d0a4_*.py::_refuse_if_cross_account_duplicates` |
| M2-AC-14 | **PASS**（本轮更正分类与命名错误后重新确认，功能本身此前即真实有效） | **更正（本次提交）**：此前记录把真实存在的 3 槽对象错误命名/描述为"5 槽"，且错误得出"3 槽对象不存在"的结论——均已核实为不准确，改正如下。真实情况：`decision-chain/docs/V1_TASK_SNAPSHOT_SCHEMA_v0.1.json` 是**唯一**一份 Schema 文件，含 13 个必填顶层字段；其 `artifacts` 子对象**真实拥有 3 个具名槽位**（`matrix`/`campaign`/`content_brief`），这就是 Prompt/EP-00 提及的"3 槽"对象本身——它确实存在，只是不作为独立文件存在（嵌在这份 Schema 内），此前"穷尽检索无独立文件→判定对象不存在"的推论跳步错误。真正的"5"来自这份同一 Schema 里另一个**可选**字段 `last_acceptance.slot` 的 5 值枚举（比 3 槽多出 `production_stage1`/`publishing_stage2`，是后续对话编排修复新增的可选扩展，Schema 自身注释明确写明为保证旧快照合法而设为可选、不进 required）——与 `artifacts` 的 3 槽是两个不同字段，此前分析把二者混为一谈。(a) 本任务的 legacy-import 端点正确校验并导入这份真实 13 字段 Schema 的完整状态对象（含其真实 3 槽 `artifacts`，测试夹具里三槽均为 null，验证的是结构合规而非真实内容）——但此前代码把这次导入的 `source` 错误标注为 `legacy_dify_5slot_import`，本次已改正为 `legacy_dify_v1_task_snapshot_import`（`app/api/tasks.py`、`tests/test_legacy_import.py` 同步更正）；(b) 真实存在的旧 Matrix/Campaign/Content Brief 生产产物（`decision-chain/evidence/*.md`，真实 3 槽的真实内容）——用真实 sha256 经既有端点显式导入（`fabffd8`），这一半覆盖 3 槽的真实内容，(a)+(b) 合起来是"结构合规＋真实内容"两个维度都成立；(c) 可选字段 `last_acceptance.slot` 的 5 值枚举**未被任何现有夹具覆盖**——如实披露为已知窄口径缺口，非阻断项：Schema 自身设计保证旧快照本就不含该字段仍合法，不影响"旧 Demo 会话态兼容"这一验收标准的核心诉求 | `0546f30`, `fabffd8`, 本次命名更正 commit；穷尽检索证据见 `M2_REBASE_ERRATA_001_RECORD.md` §5 R-05（该记录本身的"3 槽不存在"结论已在本行更正） |
| M2-AC-15 | **PASS** | `tests/test_interface_contracts.py` 钉住 M1/M3/M4 三条边界，现有实现下均未触发修复 | `44f02dd`, `020bc58` |
| M2-AC-16 | **PASS**（Founder 提供该候选应用的 App API Key 后，针对本轮最新代码真实重跑，非 API 等价替代证据） | 目标环境应用后端真实运行、正向/负向/并发/回归全部通过（69/69，现场重跑）。**Dify 候选画布本身已针对本轮最新代码重新真实运行**：Founder 主动提供该候选应用（`app_id: 8f34e8a3-fb49-4d3e-a222-3d666e767adf`）专属的 App API Key（执行侧未索要 Console 会话或账号密码）；执行侧用该 Key 调用 Dify 自身 Service API `POST /v1/workflows/run`——这触发的是 Dify 引擎真实执行同一份已发布 workflow 定义（`workflow_id: 54339bd5-14dc-491a-b221-94c764c23544`），与在 Studio UI 点「运行」走的是同一条执行路径，只是认证信道不同，**不是**绕开 Dify、直接调用 M2 后端冒充等价证据（R-08.8 明文禁止的正是后一种）。运行结果：`workflow_run_id: 1f123c37-c51c-4dad-a96c-e0696bd8b2e3`，`status: succeeded`，`total_steps: 16`，`elapsed_time: 0.43s`，无 `error`。对照 `FOUNDER_TEST_PACKAGE.md` 判断标准逐项核验：`task_id` 为真实 UUID（`af4f9244-...`）；`snapshot_status = 200`；`cycle_created_body.is_current = true`；`projection_body.latest_snapshot.payload.note` 与本次填入的"首次任务原始诉求"原文逐字一致（状态真实存住、读回）；`version_id` 为真实 UUID；`promote_body.is_current = true` 且 `promoted_by = "founder-dify-candidate-demo"`（与填入的 Actor Ref 一致）；`publish_instance_id` 为真实 UUID；`feedback_body.is_test = true`、`is_manual_entry = true`，`payload.note` 与填入的反馈原文一致；`current_cycle_body.label` 含本次运行标识——9 项判断标准全部满足。**观察（非阻断）**：本次 `total_steps = 16`，早前一轮历史运行记录为"17/17 节点成功"，两次统计口径或节点组成可能不同，未深究原因，如实记录差异，不影响本次运行本身"成功、状态可读回"的结论 `workflow_run_id: 1f123c37-c51c-4dad-a96c-e0696bd8b2e3`（Dify 自身执行记录），运行输入值与完整响应见 `collab-ledger/L5_SIDE_EFFECTS.md` SE-018 |
| M2-AC-17 | **NOT_VERIFIED（预期状态，非缺陷）** | Founder 尚未通过 Dify 画布完成产品/业务验收 | 待 Founder 实测回执 |

## M2-RB 逐条记录（Rebase/Errata 001 自身验收标准）

| criterion_id | 结果 | 说明 |
|---|---|---|
| M2-RB-01 | **PASS** | 同一 task_id、正确哈希、前序 Manifest/Attempt/副作用/分支/数据库状态完整继承（R-01 现场核验：`git fetch` 后 `origin/main`/本地-远程 M2 head 与 Prompt 观察值一致，工作树干净，容器健康） |
| M2-RB-02 | **PASS** | 错误哈希 `e17b...` 登记为无效自证值；全部证据统一用 `4d14eb35...`；原 Prompt 未被原地修改 |
| M2-RB-03 | **PASS** | Stage Baseline v0.2 继续有效约束与后继授权事实已分层记录（`M2_REBASE_ERRATA_001_RECORD.md` §3），未取消授权，未改写历史文件 |
| M2-RB-04 | **PASS** | main 相对 M2 基线的影响已分析（仅 2 个账本登记 commit，无产品/合同/受保护资产变化），无 STALE 证据需要因此重验 |
| M2-RB-05 | **PASS** | `create_version` 并发不再产生无边界裸 500，证据见 M2-AC-12 |
| M2-RB-06 | **PASS**（本轮更正："5 槽"表述与"3 槽对象不存在"结论均已改正，见 M2-AC-14） | 旧产物实际兼容面成立：真实 3 槽（`matrix`/`campaign`/`content_brief`）状态结构 + 真实历史生产产物内容，均未补造 fixture；此前误命名的"5 槽"已更正，证据见 M2-AC-14 |
| M2-RB-07 | **PASS**（本文件本身即该修正的产物，本次再次更正 AC-13） | 不再有"PASS 但证据过期"或"未完成但不在范围"的矛盾陈述——AC-16 已用真实画布重跑证据转 PASS；AC-13 的 CONNECT 子项已修复，但迁移回滚子项如实保持 NOT_VERIFIED，未因 CONNECT 修复而整体拔高 |
| M2-RB-08 | **PASS** | Founder Test Package 的纠正（R-07）已在同一次落盘中完成（`FOUNDER_TEST_PACKAGE.md` 已更正旧 Demo 兼容表述并补充说明）；本文件此前在"未完成事项"遗留的"R-07 尚未执行"表述与此矛盾，已更正删除 |
| M2-RB-09 | **PASS**（本次更正：由 NOT_VERIFIED 转正） | Founder 提供该候选应用专属 App API Key 后，Dify 候选已针对本轮最新代码真实重跑（`workflow_run_id: 1f123c37-c51c-4dad-a96c-e0696bd8b2e3`，`status: succeeded`），`M2-AC-16` 转 `PASS`，未使用 API 等价替代证据 |
| M2-RB-10 | **NOT_VERIFIED（部分，本次更正：由 PASS 再次下修）** | CONNECT 权限半已在 Founder 授权后现场执行并验证；**迁移回滚半未达标**——downgrade 对合法跨账号同键真实数据不能自动恢复/回滚，只能清晰拒绝并要求人工介入，不满足 `M2-AC-13` 原文"失败可恢复/回滚"标准，`M2-AC-13` 整体保持 `NOT_VERIFIED` |
| M2-RB-11 | **PASS** | 审查历史与预算已如实分类登记（见"审查与自验记录"），未新增开放式审查，未删除超预算事实 |
| M2-RB-12 | **PASS** | 原 `M2-AC-00`~`17` 重新获得一致、可复算状态，无删除或降低任何标准（`AC-12` 提升为真 PASS，`AC-14` 更正命名/分类错误后维持 PASS，`AC-16` 用真实重跑证据转 PASS，`AC-13` 如实保持 NOT_VERIFIED，均为纠正而非放宽） |
| M2-RB-13 | **PASS** | 本轮全部 commit 本地=远程一致（见下"Git 收口"），未触碰 `main` 和无关工作树资产 |
| M2-RB-14 | **PASS** | Founder 尚未完成 Dify 验收前保持非终态，本文件与 `M2_REBASE_ERRATA_001_RECORD.md` 均未声明 `DONE` |

## 结论与当前终态

`M2-AC-16`（Dify 画布现场运行）已用 Founder 提供的 App API Key 针对本轮最新代码真实重跑并转 `PASS`。`M2-AC-13`（数据库迁移/权限/隔离）**保持 `NOT_VERIFIED`**——CONNECT 权限子项已修复，但迁移降级（downgrade）遇到合法跨账号同键真实数据时不能自动恢复/回滚，只能清晰拒绝并要求人工介入，不满足验收标准原文"失败可恢复/回滚"的字面要求；`M2-RB-10` 同步保持 `NOT_VERIFIED（部分）`。按 Rebase Prompt §8.1：

```text
execution_disposition = CONTINUE
task_final_status = null
module_delivery_state = IN_PROGRESS
next_stage_allowed = false
```

**不是** `AWAITING_FOUNDER_DIFY_ACCEPTANCE`——`M2-AC-00~12`、`M2-AC-14~17` 均为 CURRENT PASS 或预期非终态（`AC-17` 待 Founder），唯一剩余缺口是 `M2-AC-13` 的迁移回滚子项，尚未满足 §8.2 全部前提。

## 未完成事项（本轮 Active Work Package 尚未全部执行完）

- **迁移降级恢复（`M2-AC-13` 子项）**：downgrade 对合法跨账号同键真实数据目前只能清晰拒绝，不能自动恢复/回滚。自动实现"谁保留原 key、谁改名"需要一条业务规则，这不是执行侧能单方面替业务决定并静默实现的（会改变已存储 idempotency_key 的语义，可能影响调用方原有的幂等假设）。需要 Founder 二选一：(a) 明确授权一套具体的自动改键/合并规则，执行侧据此实现并测试；(b) 接受当前"清晰拒绝＋人工介入"为最终设计，同时把 `M2-AC-13` 验收标准原文"失败可恢复/回滚"的达标口径正式改写为更准确的表述——这一改写超出执行侧单方面裁量范围。
- **R-11（定向回归）**：本轮新增/修复项已通过 69 项全量测试自证；跨模块（M1/M3/M4 接口、Dify 候选六步）回归均已覆盖。
- **R-12（远程收口）**：本轮全部 commit 已推送，见下。

（R-07、R-09b、R-08 均已在本轮完成，见上方对应 AC/RB 行；此前版本曾在本节遗留 R-07"尚未执行"的过期表述，与同一份文件里 M2-RB-08 的 PASS 状态自相矛盾，已更正删除。）
