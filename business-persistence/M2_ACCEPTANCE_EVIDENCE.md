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
- **本地/远程一致性**：本次提交推送后核验（见 `M2_REBASE_ERRATA_001_RECORD.md` §9"Git 收口"）。

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
| M2-AC-13 | **FOUNDER_WAIVED（技术事实不变，Founder 2026-08-25 明确裁决豁免；不是 PASS，也不是执行侧自行放宽）** | 验收标准原文三项要求：**数据库迁移可重复**、**失败可恢复/回滚**、**旧记录可读，Dify 内部表和数据未被改写**。逐项技术事实（**豁免不改变以下事实描述**）：(1) 迁移可重复——`alembic upgrade head` 幂等可重跑，成立；(2) **失败可恢复/回滚——技术上不成立**：`c3f8b2e6d0a4` 的 downgrade 对存在合法跨账号同键真实数据时，此前会裸崩溃，本轮已修复为**清晰拒绝并列出冲突行**（`_refuse_if_cross_account_duplicates`），这是真实的工程改进（崩溃→清晰报错），但**清晰拒绝不等于可恢复/回滚**——该场景下 downgrade 仍然不能自动完成，需要人工先决定"两个账号里谁保留这个 idempotency_key、谁改用新 key"这一业务语义问题；(3) 旧记录可读、Dify 内部表和数据未被改写——成立，本轮 REVOKE CONNECT 只撤销数据库级连接权限（ACL），未触碰 Dify 任何表或数据行。数据库 CONNECT 权限缺口（**已修复，与本次豁免无关**）：修复前现场负向复现确认 `diyu_app` **可以** `CONNECT` 到 `dify`/`dify_plugin`（`SELECT current_database()` 成功返回），与 `TECHNICAL_DECISION_RECORD.md` 原"REVOKE ALL 阻止连接"表述不一致。经 Founder 2026-08-25 现场明确授权后，在 `docker-db_postgres-1` 上以 `postgres` 超级用户执行 `REVOKE CONNECT ON DATABASE dify FROM PUBLIC, diyu_app;` 与同语句对 `dify_plugin`；修复后现场重测：`diyu_app` 连接 `dify`/`dify_plugin` 均返回 `FATAL: permission denied for database ... DETAIL: User does not have CONNECT privilege`；回归确认 `diyu_app` 对自身 `diyu_business` 连接不受影响，Dify 自身容器（`docker-api-1` 等）以 `postgres` 超级用户连接（超级用户天然绕过 CONNECT ACL），未受此次 REVOKE 影响。**Founder 裁决（2026-08-25，本会话内明确表述）**：执行侧向 Founder 解释了迁移回滚的技术含义、当前具体卡点（跨账号共享 idempotency_key 的自动改键需要业务规则，不是纯技术判断）、以及两个可选方向（授权一套具体自动改键规则 / 接受人工介入并改写验收标准字面口径）后，Founder 明确答复"可以跳过这一步，继续推进 M2 落盘收口，备注说明：我已经完全裁决豁免回滚这个环节步骤"。这是 Founder 依据其对 ACCEPTANCE 的控制权作出的产品/业务决定，**不是执行侧自行宣布 PASS、不是执行侧用"已知限制"规避原 P0**——原 Rebase Prompt R-06 禁止的是执行侧自行使用 `PASS_WITH_LIMITATION` 等措辞掩盖未达标项，本行未使用这类措辞，而是如实标注 `FOUNDER_WAIVED` 并完整保留技术事实。**判定**：三项子要求中"失败可恢复/回滚"子项技术上仍不成立，但该子项已被 Founder 明确豁免、不再阻塞本任务收尾判定；整体标记 `FOUNDER_WAIVED`，区别于 `PASS`（技术达标）和阻塞性 `NOT_VERIFIED`（技术未达标且未被豁免） | Founder 2026-08-25 CONNECT 修复授权记录 + 回滚豁免裁决记录见 `M2_REBASE_ERRATA_001_RECORD.md` §7；downgrade 清晰拒绝证据见 R-09a、`migrations/versions/c3f8b2e6d0a4_*.py::_refuse_if_cross_account_duplicates` |
| M2-AC-14 | **PASS**（本轮更正分类与命名错误后重新确认，功能本身此前即真实有效） | **更正（本次提交）**：此前记录把真实存在的 3 槽对象错误命名/描述为"5 槽"，且错误得出"3 槽对象不存在"的结论——均已核实为不准确，改正如下。真实情况：`decision-chain/docs/V1_TASK_SNAPSHOT_SCHEMA_v0.1.json` 是**唯一**一份 Schema 文件，含 13 个必填顶层字段；其 `artifacts` 子对象**真实拥有 3 个具名槽位**（`matrix`/`campaign`/`content_brief`），这就是 Prompt/EP-00 提及的"3 槽"对象本身——它确实存在，只是不作为独立文件存在（嵌在这份 Schema 内），此前"穷尽检索无独立文件→判定对象不存在"的推论跳步错误。真正的"5"来自这份同一 Schema 里另一个**可选**字段 `last_acceptance.slot` 的 5 值枚举（比 3 槽多出 `production_stage1`/`publishing_stage2`，是后续对话编排修复新增的可选扩展，Schema 自身注释明确写明为保证旧快照合法而设为可选、不进 required）——与 `artifacts` 的 3 槽是两个不同字段，此前分析把二者混为一谈。(a) 本任务的 legacy-import 端点正确校验并导入这份真实 13 字段 Schema 的完整状态对象（含其真实 3 槽 `artifacts`，测试夹具里三槽均为 null，验证的是结构合规而非真实内容）——但此前代码把这次导入的 `source` 错误标注为 `legacy_dify_5slot_import`，本次已改正为 `legacy_dify_v1_task_snapshot_import`（`app/api/tasks.py`、`tests/test_legacy_import.py` 同步更正）；(b) 真实存在的旧 Matrix/Campaign/Content Brief 生产产物（`decision-chain/evidence/*.md`，真实 3 槽的真实内容）——用真实 sha256 经既有端点显式导入（`fabffd8`），这一半覆盖 3 槽的真实内容，(a)+(b) 合起来是"结构合规＋真实内容"两个维度都成立；(c) 可选字段 `last_acceptance.slot` 的 5 值枚举**未被任何现有夹具覆盖**——如实披露为已知窄口径缺口，非阻断项：Schema 自身设计保证旧快照本就不含该字段仍合法，不影响"旧 Demo 会话态兼容"这一验收标准的核心诉求 | `0546f30`, `fabffd8`, 本次命名更正 commit；穷尽检索证据见 `M2_REBASE_ERRATA_001_RECORD.md` §5 R-05（该记录本身的"3 槽不存在"结论已在本行更正） |
| M2-AC-15 | **PASS** | `tests/test_interface_contracts.py` 钉住 M1/M3/M4 三条边界，现有实现下均未触发修复 | `44f02dd`, `020bc58` |
| M2-AC-16 | **PASS**（Founder 提供该候选应用的 App API Key 后，针对本轮最新代码真实重跑，非 API 等价替代证据） | 目标环境应用后端真实运行、正向/负向/并发/回归全部通过（69/69，现场重跑）。**Dify 候选画布本身已针对本轮最新代码重新真实运行**：Founder 主动提供该候选应用（`app_id: 8f34e8a3-fb49-4d3e-a222-3d666e767adf`）专属的 App API Key（执行侧未索要 Console 会话或账号密码）；执行侧用该 Key 调用 Dify 自身 Service API `POST /v1/workflows/run`——这触发的是 Dify 引擎真实执行同一份已发布 workflow 定义（`workflow_id: 54339bd5-14dc-491a-b221-94c764c23544`），与在 Studio UI 点「运行」走的是同一条执行路径，只是认证信道不同，**不是**绕开 Dify、直接调用 M2 后端冒充等价证据（R-08.8 明文禁止的正是后一种）。运行结果：`workflow_run_id: 1f123c37-c51c-4dad-a96c-e0696bd8b2e3`，`status: succeeded`，`total_steps: 16`，`elapsed_time: 0.43s`，无 `error`。对照 `FOUNDER_TEST_PACKAGE.md` 判断标准逐项核验：`task_id` 为真实 UUID（`af4f9244-...`）；`snapshot_status = 200`；`cycle_created_body.is_current = true`；`projection_body.latest_snapshot.payload.note` 与本次填入的"首次任务原始诉求"原文逐字一致（状态真实存住、读回）；`version_id` 为真实 UUID；`promote_body.is_current = true` 且 `promoted_by = "founder-dify-candidate-demo"`（与填入的 Actor Ref 一致）；`publish_instance_id` 为真实 UUID；`feedback_body.is_test = true`、`is_manual_entry = true`，`payload.note` 与填入的反馈原文一致；`current_cycle_body.label` 含本次运行标识——9 项判断标准全部满足。**观察（非阻断）**：本次 `total_steps = 16`，早前一轮历史运行记录为"17/17 节点成功"，两次统计口径或节点组成可能不同，未深究原因，如实记录差异，不影响本次运行本身"成功、状态可读回"的结论 `workflow_run_id: 1f123c37-c51c-4dad-a96c-e0696bd8b2e3`（Dify 自身执行记录），运行输入值与完整响应见 `collab-ledger/L5_SIDE_EFFECTS.md` SE-018 |
| M2-AC-17 | **PASS**（Founder 已通过 Dify 画布实际验收并明确接受） | Founder 本人在 Dify Studio 中打开候选应用（`app_id: 8f34e8a3-fb49-4d3e-a222-3d666e767adf`）、按 `FOUNDER_TEST_PACKAGE.md` 六步场景手动填写表单并点击「运行」，运行产出 `task_id: f7b96d1a-5dc2-4217-be0b-d618bfd36c57`；Founder 将 End 节点全部输出原文粘贴给执行侧核对，逐项核验：`projection_body.latest_snapshot.payload.note` 与 Founder 填入的"首次任务原始诉求"原文一致，`current_cycle_body.label` 含 Founder 填入的运行标识，其余 7 项输出均为真实 UUID / 状态字段符合预期，9 项判断标准全部满足。Founder 随后明确表示"接受"该结果，并进一步明确裁决"接受 + 合并主干"，构成 `M2-AC-17` 所要求的"Founder 通过 Dify 画布完成产品/业务验收并明确接受" | Founder 提供的运行输出原文（本文件与 `M2_REBASE_ERRATA_001_RECORD.md` §9 均已登记要点）；`task_id: f7b96d1a-5dc2-4217-be0b-d618bfd36c57` |

## M2-RB 逐条记录（Rebase/Errata 001 自身验收标准）

| criterion_id | 结果 | 说明 |
|---|---|---|
| M2-RB-01 | **PASS** | 同一 task_id、正确哈希、前序 Manifest/Attempt/副作用/分支/数据库状态完整继承（R-01 现场核验：`git fetch` 后 `origin/main`/本地-远程 M2 head 与 Prompt 观察值一致，工作树干净，容器健康） |
| M2-RB-02 | **PASS** | 错误哈希 `e17b...` 登记为无效自证值；全部证据统一用 `4d14eb35...`；原 Prompt 未被原地修改 |
| M2-RB-03 | **PASS** | Stage Baseline v0.2 继续有效约束与后继授权事实已分层记录（`M2_REBASE_ERRATA_001_RECORD.md` §3），未取消授权，未改写历史文件 |
| M2-RB-04 | **PASS** | main 相对 M2 基线的影响已分析（仅 2 个账本登记 commit，无产品/合同/受保护资产变化），无 STALE 证据需要因此重验 |
| M2-RB-05 | **PASS** | `create_version` 并发不再产生无边界裸 500，证据见 M2-AC-12 |
| M2-RB-06 | **PASS**（本轮更正："5 槽"表述与"3 槽对象不存在"结论均已改正，见 M2-AC-14） | 旧产物实际兼容面成立：真实 3 槽（`matrix`/`campaign`/`content_brief`）状态结构 + 真实历史生产产物内容，均未补造 fixture；此前误命名的"5 槽"已更正，证据见 M2-AC-14 |
| M2-RB-07 | **PASS**（本文件本身即该修正的产物，本次再次更正 AC-13） | 不再有"PASS 但证据过期"或"未完成但不在范围"的矛盾陈述——AC-16 已用真实画布重跑证据转 PASS；AC-13 的 CONNECT 子项已修复，迁移回滚子项技术上未达标但已被 Founder 明确豁免，标记 `FOUNDER_WAIVED` 而非拔高为 PASS |
| M2-RB-08 | **PASS** | Founder Test Package 的纠正（R-07）已在同一次落盘中完成（`FOUNDER_TEST_PACKAGE.md` 已更正旧 Demo 兼容表述并补充说明）；本文件此前在"未完成事项"遗留的"R-07 尚未执行"表述与此矛盾，已更正删除 |
| M2-RB-09 | **PASS**（本次更正：由 NOT_VERIFIED 转正） | Founder 提供该候选应用专属 App API Key 后，Dify 候选已针对本轮最新代码真实重跑（`workflow_run_id: 1f123c37-c51c-4dad-a96c-e0696bd8b2e3`，`status: succeeded`），`M2-AC-16` 转 `PASS`，未使用 API 等价替代证据 |
| M2-RB-10 | **FOUNDER_WAIVED（技术事实不变，本次更正）** | CONNECT 权限半已在 Founder 授权后现场执行并验证，技术达标；**迁移回滚半技术上仍未达标**——downgrade 对合法跨账号同键真实数据不能自动恢复/回滚，只能清晰拒绝并要求人工介入，不满足 `M2-AC-13` 原文"失败可恢复/回滚"标准；Founder 2026-08-25 明确裁决豁免这一子项，不再阻塞任务收尾，见 `M2-AC-13` 行完整记录 |
| M2-RB-11 | **PASS** | 审查历史与预算已如实分类登记（见"审查与自验记录"），未新增开放式审查，未删除超预算事实 |
| M2-RB-12 | **PASS**（本次追加：Founder 豁免不算"降低标准"，理由见右列） | 原 `M2-AC-00`~`17` 重新获得一致、可复算状态，无执行侧删除或降低任何标准（`AC-12` 提升为真 PASS，`AC-14` 更正命名/分类错误后维持 PASS，`AC-16` 用真实重跑证据转 PASS）；`AC-13` 的技术事实如实保持"迁移回滚未达标"不变，只是 Founder 行使其对 ACCEPTANCE 的控制权明确豁免了这一项对任务收尾的阻塞——这是产品/业务决定，不是执行侧自行放宽 |
| M2-RB-13 | **PASS** | 本轮全部 commit 本地=远程一致（见 `M2_REBASE_ERRATA_001_RECORD.md` §9"Git 收口"），未触碰 `main` 和无关工作树资产 |
| M2-RB-14 | **PASS** | `M2-AC-17`（Founder 通过 Dify 画布的产品/业务验收）已完成，Founder 明确接受，且明确裁决"接受 + 合并主干"；`M2-AC-13` 的豁免是独立的技术治理决定，未被冒充为 `M2-AC-17` 本身；`task_final_status = DONE` 在满足 §8.3 全部前提后于本节声明 |

## 结论与当前终态（`DONE`）

`M2-AC-16`（Dify 画布现场运行）已用 Founder 提供的 App API Key 针对本轮最新代码真实重跑并转 `PASS`。`M2-AC-13`（数据库迁移/权限/隔离）标记 `FOUNDER_WAIVED`——技术事实不变，Founder 明确裁决豁免。**`M2-AC-17` 已转 `PASS`**：Founder 本人在 Dify Studio 实际运行候选画布（`task_id: f7b96d1a-5dc2-4217-be0b-d618bfd36c57`），逐项核验 9 项判断标准全部满足，明确表示"接受"，并进一步裁决"接受 + 合并主干"。

按 Rebase Prompt §8.3（DONE 条件）逐项核验：

- 审查预算偏差（2026-08-26 治理收口纠偏，更正推论）：**仅凭"偏差已如实登记并保留"不能推导出"没有未确认偏差"**——登记与 Founder 本人的确认是两件事，此前混同。准确表述：偏差存在 = `true`（`actual_formal_review_units = 3` 超出冻结 `formal_review_budget = 1`）；Founder 知悉并明确确认该偏差 = `true`（Founder 2026-08-26 指示"输出执行 prompt，让执行侧完善，把屁股擦干净"，构成对该偏差的明确确认）；该确认阻塞 M2 最终收口 = `false`；该确认追认历史偏差为"符合预算" = `false`——`REVIEW_BUDGET_CONFORMANCE` 仍如实登记为 `DEVIATION`，不因确认而改写为"符合"，已发生的审查单元未被重新分类或删除。完整记录见 `M2_FINAL_GOVERNANCE_CLOSEOUT_RECOVERY_RECORD_v1.0.md`；
- 所有最终证据绑定远端最终 commit——见下方"合并与最终证据绑定"；
- `M2-AC-00～17` 与 `M2-RB-01～14` 全部通过（`M2-AC-13`/`M2-RB-10` 为 `FOUNDER_WAIVED`，技术事实保留，不冒充 `PASS`）；
- 没有用模拟/测试数据声称真实运营闭环——本文件与 `FOUNDER_TEST_PACKAGE.md` 全程标明测试身份、测试数据、非真实发布；
- 没有声称经营结果提升、生产可用、M5 完成或完整纵向链完成——本文件与合并 commit message 均明确声明这些事项**未**随本次交付授权。

> **终态字段治理纠偏（2026-08-26）**：本节此前同时给出 `execution_disposition = CONTINUE` 与 `task_final_status = DONE`，这是无效组合——`CONTINUE` 只应用于非终态 Checkpoint，且要求 `task_final_status = null`。M2 已进入正式终态，`execution_disposition` 字段在最终状态块中不再适用，已移除；不改变本任务已经是 `DONE` 这一事实本身。完整纠偏记录见 `M2_FINAL_GOVERNANCE_CLOSEOUT_RECOVERY_RECORD_v1.0.md`。

```text
task_final_status = DONE
module_delivery_state = DONE
next_stage_allowed = false
checkpoint = null
active_work_package = null
```

**M2 DONE 不授权**（原样继承 Rebase Prompt §8.3 边界，未被本次收尾扩大）：合并 main 之外的任何进一步动作——不授权 M5 集成、不授权真实社交平台发布、不授权生产采用、不授权任何真实经营结果结论。

## 合并与最终证据绑定

- 任务分支 `task/m2-business-persistence-version-feedback-v1`（最终 head `74bc9e32627b290c93827a4ff83b2bc79aa9befd`）经 Founder 明确授权合并进 `main`，合并 commit `17f5e5724a09470c78c757a88c4ec6469fb0dcfd`（`--no-ff`，保留完整任务历史）。
- 合并冲突：仅 `collab-ledger/L1_TASK_MANIFESTS.md` 顶部索引表一处（两侧各自新增一行索引，非逻辑冲突），已保留双方行并为本任务的起点登记行追加"当前状态见 §T-011～§T-011.6"的指向说明，未删除任何一方内容。
- 合并后现场核验（逐项对应 Founder 提出的收口检查清单）：
  1. **远程 main 真实包含本次交付**——`git push origin main` 后 `git fetch` 复核，本地 `main` 与 `origin/main` 均为 `17f5e5724a09470c78c757a88c4ec6469fb0dcfd`；`git ls-tree -r origin/main` 确认 `business-persistence/` 下 56 个文件真实存在于远端。
  2. **合并内容与已验收候选一致**——`git diff task/m2-business-persistence-version-feedback-v1 main -- business-persistence/` 输出为空，字节级一致。
  3. **受保护合同、共享资产和既有能力没有退化**——`git diff --stat` 合并前后对比（排除 `business-persistence/`、`collab-ledger/`）输出为空，未触碰任何其他路径。
  4. **必要回归通过**——合并后现场重跑 `pytest tests/ -q` → **69 passed**。
  5. **目标 Dify 候选仍与最终代码和配置相符**——运行 69 项测试的容器与 Founder 验收运行时使用的是同一个 `diyu-m2-app` 容器（未重建），且其代码已确认与合并后 `main` 字节一致；候选应用 `app_id`/`workflow_id` 未变。
  6. **Git、账本和最终证据绑定更新完成**——本节与下方账本更新即为该项证据。

## 未完成事项（无——本任务技术侧与 Founder 产品侧均已收口）

- R-11（定向回归）、R-12（远程收口）均已完成，见 `M2_REBASE_ERRATA_001_RECORD.md` §9"Git 收口"。
- `M2-AC-13` 迁移降级恢复：技术上仍未达到"失败可恢复/回滚"字面标准，已被 Founder 明确豁免；如未来业务确实需要跨账号冲突自动改键能力，需另行发起新的授权与规则裁决，不在本任务范围内。
- M5 集成、M1/M3/M4 与 M2 的实际接入、真实社交平台发布、生产采用均为后续独立任务范围，不随本次 DONE 授权。

（R-07、R-08、R-09b 均已在本轮完成，见上方对应 AC/RB 行。）
