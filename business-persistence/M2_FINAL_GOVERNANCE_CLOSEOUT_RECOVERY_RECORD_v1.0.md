# M2 最终治理收尾纠偏记录 v1.0

`task_id: DIYU-V1-M2-BUSINESS-PERSISTENCE-VERSION-FEEDBACK-001`

> 本记录由 `M2_FINAL_GOVERNANCE_CLOSEOUT_RECOVERY_EXECUTION_PROMPT_v1.0`（Founder 2026-08-26 授权）驱动产生。
> 本次是纯治理收口 `RECOVERY_TASK`，不是新一轮 M2 工程实施，不是 M5 集成；不改变 M2 产品语义、不修改
> M2 代码/迁移/测试/Dify DSL，不写数据库和 Dify。

## 1. task_id 与进入依据

- `task_id`：`DIYU-V1-M2-BUSINESS-PERSISTENCE-VERSION-FEEDBACK-001`（沿用，未新建）
- `task_entry_mode`：`RECOVERY_TASK`
- 采用 `RECOVERY_TASK` 而非 `NEW_TASK` 的理由：(1) 原 `task_id`、P0、产品合同、Task Contract 均未变；(2) M2 工程实现已完成并已进入远程 `main`（合并 commit `17f5e5724a09470c78c757a88c4ec6469fb0dcfd`，`main` 登记提交 `a903e49ab175eab8acf4b4e62b9dedea87eff901`）；(3) 当前不足是终态记录、审查预算确认与副作用账本存在可定位的治理矛盾，不是工程能力缺口；(4) 不建立新 `task_id`，不把本次治理恢复伪装成 M2 新功能或新工程阶段。

## 2. Root Prompt / Rebase Prompt / Task Contract 哈希（本次现场重算，非引用历史值）

| 项 | 值 | 核验方式 |
|---|---|---|
| Root Prompt | `decision-chain/docs/M2_ENGINEERING_EXECUTION_PROMPT_v1.1.md` | `sha256sum` 现场重算 = `8008bebd04b35037e16f5462ea1b7284db7dec943e954263762bbdb4688bb0c6`，与历史记录一致，未漂移 |
| Rebase/Errata Prompt | `business-persistence/M2_ENGINEERING_EXECUTION_PROMPT_v1.1_REBASE_ERRATA_001.md` | `sha256sum` 现场重算 = `fbb65e1dcdb405a435f03fc8efa8f9828926d9881850aa7c86237bf267ef7c5d`，与主工作区未跟踪原件（`/home/faye/diyu-demo/M2_ENGINEERING_EXECUTION_PROMPT_v1.1_REBASE_ERRATA_001.md`）字节一致，均未漂移 |
| Task Contract Hash | `4d14eb35c065b650b0380b0c309e0e08ec32e3aa608ece4d62e8d27b97450830` | 沿用既有独立复算值（原 Prompt 自证哈希与实际内容不一致，已由 Founder 裁决改用此独立复算值登记，见 L1 §T-010.2 DA-02）；本次未发现导致其失效的绑定变化——Prompt 原文与 Task Contract 字段均未修改 |

`p0_change = false`；`product_contract_change = false`；`acceptance_oracle_change = false`；`engineering_reimplementation_authorized = false`。

## 3. 现场侦察（§8.1，本次实测，不使用历史观察值冒充当前基线）

| 检查项 | 现场实测结果 |
|---|---|
| `pwd` / Git 根 | `/home/faye/diyu-demo`（主工作区），任务分支独立 worktree `/home/faye/diyu-demo-worktrees/m2-business-persistence-version-feedback-v1` |
| 适用的 CLAUDE.md | 全局 `/home/faye/.claude/CLAUDE.md`；项目 `/home/faye/diyu-demo/CLAUDE.md`；任务 worktree 内同一项目 CLAUDE.md 副本。未发现 `AGENTS.md` |
| `git ls-remote --symref origin HEAD` | `ref: refs/heads/main HEAD`，`a903e49ab175eab8acf4b4e62b9dedea87eff901` |
| `git ls-remote origin refs/heads/main` | `a903e49ab175eab8acf4b4e62b9dedea87eff901` —— 与规划侧观察值 `observed_origin_main` 一致，未漂移 |
| `git ls-remote origin refs/heads/task/m2-business-persistence-version-feedback-v1` | `74bc9e32627b290c93827a4ff83b2bc79aa9befd` —— 与规划侧观察值 `observed_m2_task_branch_head` 一致 |
| `git merge-base --is-ancestor <task_head> <origin_main>` | 通过——任务分支确为当前 `origin/main` 祖先 |
| 主工作区 `git status --short --branch` | `## main...origin/main`，6 个既有未跟踪文件（`M1_ENGINEERING_EXECUTION_REBASE_PROMPT_v1.3.md`、本任务的 Rebase/Errata Prompt 未跟踪原件、`m3-account-content-operator-semantic-v1.0/`、三份笛语规划文档）——均为本任务之外的用户既有工作产物，本次未触碰、未删除、未移动 |
| 现有 worktree | 7 个（`main` 主工作区 + 6 个任务/功能 worktree），均与本任务无关，未新建第二个 M2 分支或 worktree |
| 任务分支 worktree 状态 | `git fetch` 后确认落后 `origin/main` 3 个提交（`78a4ad8`/`17f5e57`/`a903e49`，均为 M2 自身收口提交），按 §8.2 非破坏性 `git merge --ff-only origin/main` 快进，无冲突 |
| 运行容器只读核验 | `diyu-m2-app` 容器 `Up`；`healthz` = `{"status":"ok"}`；`alembic current` = `c3f8b2e6d0a4 (head)`；容器内 `/srv/app/app/api/tasks.py` 与任务分支 worktree 同文件 `sha256` 完全一致（`6d8bb0216653d6ba9806f7b0e1479ceff083519c408ce6fdc061a722147ce3b2`）——均与规划侧观察值一致，未漂移 |
| Dify 候选身份 | 本次会话内无可用 App API Key 或 Console 会话，未做现场 Dify 只读查询；本次未修改 Dify、未触发任何画布运行，无证据表明规划侧观察的候选身份（`app_id`/`workflow_id`/`founder_run_id`）自上次记录以来发生变化，此项标记为"沿用既有已验证记录，本次未重新现场核验" |

无现场值漂移，未触发 §十强制停止条件。

## 4. 恢复前远程 main 与任务分支 hash

- 恢复前 `origin/main`：`a903e49ab175eab8acf4b4e62b9dedea87eff901`
- 恢复前 `origin/task/m2-business-persistence-version-feedback-v1`：`74bc9e32627b290c93827a4ff83b2bc79aa9befd`（本次先非破坏性快进至 `a903e49...` 再叠加 Recovery Delta，过程见本记录 §11）

## 5. Founder 审查预算偏差确认（G-01）

| 字段 | 值 |
|---|---|
| 偏差是否存在 | `true`——`actual_formal_review_units = 3`（1 个初版独立对抗性审查 + 2 个并行审查 Agent）超出原 Prompt 冻结 `formal_review_budget = 1`；另有 `actual_closing_verification_units = 1`（收口验证，按 Prompt 定义不计入正式审查预算） |
| Founder 是否知悉并确认其不再阻塞本次收口 | `true`——Founder 2026-08-26 明确指示"输出执行 prompt，让执行侧完善，把屁股擦干净"，构成对该已披露偏差的明确确认 |
| 该确认是否追认为符合预算 | `false`——`REVIEW_BUDGET_CONFORMANCE` 仍如实登记为 `DEVIATION`，不改写为"符合" |
| 是否删除、合并或重新分类已发生的审查单元 | 否——3 个正式审查单元 + 1 个收口验证单元的历史记录原样保留 |
| 是否拔高任何技术验收结果 | 否——本次确认不改变任何 `M2-AC-*`/`M2-RB-*` 的技术判定 |
| 是否构成对未来超预算审查的通用授权 | 否——本次确认仅解除"本次 M2 收口的该项偏差尚未获 Founder 确认"这一具体治理缺口 |

统一登记口径：`review_budget_conformance = DEVIATION`；`founder_acknowledgement = CONFIRMED`；`founder_acknowledgement_effect = NON_BLOCKING_FOR_FINAL_CLOSEOUT`；`historical_review_count_preserved = true`；`retrospective_budget_conformance_claimed = false`；`new_review_authorized = false`。

同步登记位置：`business-persistence/M2_ACCEPTANCE_EVIDENCE.md`（结论与当前终态一节）、`business-persistence/M2_REBASE_ERRATA_001_RECORD.md`（§6 R-10）、`collab-ledger/L1_TASK_MANIFESTS.md`（§T-011.7）、`collab-ledger/L3_ATTEMPTS_AND_EVIDENCE.md`（§ATT-007）。

## 6. `M2-AC-13` 准确技术事实（继续 `FOUNDER_WAIVED`，未改写为 `PASS`）

| 字段 | 值 |
|---|---|
| `technical_result` | `NOT_FULLY_MET`——迁移升级（`alembic upgrade head`）可重复、幂等，成立；但 `c3f8b2e6d0a4` 的 `downgrade()` 遇到真实存在的跨账号同 `idempotency_key` 冲突数据时，只能清晰拒绝（`_refuse_if_cross_account_duplicates`）并列出冲突行，**不能自动完成回滚**，需要人工先决定业务语义（两个账号里谁保留原 key） |
| `founder_disposition` | `WAIVED`——Founder 2026-08-25 在本任务原会话中明确答复"可以跳过这一步，继续推进 M2 落盘收口……我已经完全裁决豁免回滚这个环节步骤" |
| `blocking_effect` | `false`——该子项不再阻塞 M2 最终收口 |

本次治理纠偏（Recovery Task）**未**改变以上任何一项技术事实，**未**将 `M2-AC-13`/`M2-RB-10` 改写为技术 `PASS`。

## 7. 终态字段纠偏（G-02）

修正前的无效组合：`execution_disposition = CONTINUE` 与 `task_final_status = DONE` 同时出现于 `M2_ACCEPTANCE_EVIDENCE.md`、`M2_REBASE_ERRATA_001_RECORD.md`、`collab-ledger/L2_TASK_STATE_AND_HANDOFF.md`（§一.15）、`collab-ledger/L3_ATTEMPTS_AND_EVIDENCE.md`（ATT-006 任务终态行）。

修正后统一登记（`execution_disposition` 字段在最终状态块中省略，不发明 `FINAL`/`STOP` 等未经协议定义的新枚举）：

```text
task_final_status: DONE
module_delivery_state: DONE
next_stage_allowed: false
checkpoint: null
active_work_package: null
```

历史上出现过的 `CONTINUE + DONE` 组合已通过后继更正（本记录 + 上述四份文件的追加/更正块）明确声明该组合无效、不再代表当前状态，历史文本未被删除，仅前向更正。

## 8. L5 副作用账本纠偏（G-03）

- 已在 `collab-ledger/L5_SIDE_EFFECTS.md` 新增：(1) 状态值规范映射（`ATTEMPTED`→`STARTED`、`BLOCKED`→`FAILED_NO_EFFECT`、`EXECUTED`→`CONFIRMED`，不删除历史原文）；(2) SE-015 状态追加，更正"全部迁移均有对称 `downgrade()`"的过度声明，分离陈述"upgrade 可重复"（成立）与"特定 downgrade 冲突不能自动恢复"（`FOUNDER_WAIVED`）；(3) §四"其他外部系统"追加更正块，前向更正"Dify/业务数据库均无写入"的过期结论——`DIYU-V1-M2-BUSINESS-PERSISTENCE-VERSION-FEEDBACK-001` 任务下 SE-015/SE-017（数据库真实写入）与 SE-018/SE-020（Dify 真实 workflow 运行）均为真实写入，均在候选专属测试范围内，非生产经营数据。
- 原 `NONE_VERIFIED_SINCE_BASELINE` 结论作为历史时点结论保留，标注不再是当前有效结论。
- 本次纯文档纠偏本身**未**被登记为新的 Dify 或数据库写入。

## 9. 本次允许修改的文件（实际发生改动的子集）

- `business-persistence/M2_FINAL_GOVERNANCE_CLOSEOUT_RECOVERY_RECORD_v1.0.md`（新增，本文件）
- `business-persistence/M2_ACCEPTANCE_EVIDENCE.md`
- `business-persistence/M2_REBASE_ERRATA_001_RECORD.md`
- `collab-ledger/L1_TASK_MANIFESTS.md`
- `collab-ledger/L2_TASK_STATE_AND_HANDOFF.md`
- `collab-ledger/L3_ATTEMPTS_AND_EVIDENCE.md`
- `collab-ledger/L5_SIDE_EFFECTS.md`

`business-persistence/FOUNDER_TEST_PACKAGE.md` 未发现需要纠偏的实质问题（该文件已准确记录迁移回滚限制与 Founder 豁免事实），本次未改动，未为填满允许列表而制造改动。

## 10. 本次没有修改的对象

代码（`business-persistence/app/**`）、迁移（`business-persistence/migrations/**`）、测试（`business-persistence/tests/**`）、Dify DSL（`business-persistence/dify/**`）、`requirements.txt`、`Dockerfile`、`decision-chain/docs/**`、四份 M0.3 共享合同、两份 EP-00 报告、Phase 0 共享编译前言、M1/M3/M4 文件、Skill 源文件、Dify 应用/工作流/DSL/发布状态、PostgreSQL 数据库/角色/权限/Schema/业务记录、容器/镜像/运行配置、生产环境、真实社交平台——**均零变化**（证据见 §14）。未执行 Alembic upgrade/downgrade，未重建容器，未重新导入或发布 Dify 工作流，未重新运行六步 Dify 场景。

## 11. Git 执行（§8.3/§8.4，现场核验完成）

1. 任务分支 worktree 非破坏性快进：`git merge --ff-only origin/main`，`task/m2-business-persistence-version-feedback-v1` 从 `74bc9e32627b290c93827a4ff83b2bc79aa9befd` 快进至 `a903e49ab175eab8acf4b4e62b9dedea87eff901`（零冲突，纯快进，未产生新提交）。
2. 在快进后的任务分支上提交 Recovery Delta（本记录 §9 所列 7 个文件），提交前 `git diff --name-only` 核验只包含允许路径；提交后推送：`74bc9e3..894211b task/m2-business-persistence-version-feedback-v1 -> task/m2-business-persistence-version-feedback-v1`。远端核验：`git ls-remote origin refs/heads/task/m2-business-persistence-version-feedback-v1` → `894211bb025228eb69c50b7c415c4f9de3c6c8dd`，与本地 `git rev-parse HEAD` 一致。
3. 合并前重新 `git fetch origin main` 核验 `origin/main` 仍为 `a903e49...`，未漂移。在主工作区执行 `git merge --no-ff task/m2-business-persistence-version-feedback-v1`，**零冲突**（未触发第五节之外的任何冲突处理路径），产生合并 commit `03a94ca5eb6ec713c223c62a9c67d01fd7070ff0`。
4. `git push origin main`：`a903e49..03a94ca main -> main`。远端核验：`git ls-remote origin refs/heads/main` → `03a94ca5eb6ec713c223c62a9c67d01fd7070ff0`，与本地 `git rev-parse HEAD` 一致。
5. 双向祖先核验：`git merge-base --is-ancestor 894211b HEAD` 通过；`git merge-base --is-ancestor a903e49 HEAD` 通过——历史未被改写，旧 `main` tip 仍是新 `main` 的祖先。
6. 任务分支 `task/m2-business-persistence-version-feedback-v1` 保留未删除。本次全程未使用 `force`/`reset --hard`/`amend`/`rebase`/`squash`。

**最终 hash 绑定**：`recovery_commit = 894211bb025228eb69c50b7c415c4f9de3c6c8dd`；`merge_commit = 03a94ca5eb6ec713c223c62a9c67d01fd7070ff0`；`final_origin_main = 03a94ca5eb6ec713c223c62a9c67d01fd7070ff0`（本节即完成本记录 §12/§13 的绑定要求）。

## 12.（并入 §11 最终证据绑定）

## 13.（并入 §11 最终证据绑定）

## 14. 受保护资产零变化证据

合并前后（`a903e49ab175eab8acf4b4e62b9dedea87eff901` → `03a94ca5eb6ec713c223c62a9c67d01fd7070ff0`）现场核验：

- `git diff a903e49 03a94ca --stat -- business-persistence/app/ business-persistence/migrations/ business-persistence/tests/ business-persistence/dify/ decision-chain/docs/ business-persistence/requirements.txt business-persistence/Dockerfile` → **输出为空**，零变化。
- `git diff a903e49 03a94ca --stat -- . ':!business-persistence' ':!collab-ledger'` → **输出为空**——仓库内除 `business-persistence/` 与 `collab-ledger/` 之外的全部路径零变化，四份 M0.3 共享合同、两份 EP-00 报告、Phase 0 前言、M1/M3/M4 文件、Skill 源文件均未受影响。
- 主工作区既有 6 个未跟踪文件（`M1_ENGINEERING_EXECUTION_REBASE_PROMPT_v1.3.md`、Rebase/Errata Prompt 未跟踪原件、`m3-account-content-operator-semantic-v1.0/`、三份笛语规划文档）合并前后均原样保留，未被删除、覆盖或误提交。
- 未执行 `docker build`/`stop`/`rm`/`run`；未执行 `alembic upgrade`/`downgrade`；未调用任何 Dify API；PostgreSQL 数据库内容未变。

## 15. 本次未重新运行的、会产生业务数据的 Dify 验收场景

本次治理纠偏**未**重新运行 `FOUNDER_TEST_PACKAGE.md` 六步候选画布场景，**未**触发任何新的 Dify workflow 执行，**未**产生任何新的候选测试业务对象（task/cycle/content version/publish instance/feedback record）。`M2-AC-16`/`M2-AC-17` 沿用既有真实运行证据（`workflow_run_id: 1f123c37-c51c-4dad-a96c-e0696bd8b2e3`；Founder 本人运行 `task_id: f7b96d1a-5dc2-4217-be0b-d618bfd36c57`），不重新验收。

## 16. 当前正式终态

```text
task_id = DIYU-V1-M2-BUSINESS-PERSISTENCE-VERSION-FEEDBACK-001
task_entry_mode = RECOVERY_TASK

review_budget_conformance = DEVIATION
founder_acknowledgement = CONFIRMED
retrospective_budget_conformance_claimed = false

task_final_status = DONE
module_delivery_state = DONE
next_stage_allowed = false
checkpoint = null
active_work_package = null

m2_engineering_reopened = false
m2_engineering_code_changed = false
database_write_performed = false
dify_write_performed = false
m2_governance_closeout_complete = true

M2_ENGINEERING_IMPLEMENTATION_LANDED = true
M2_MERGED_TO_REMOTE_MAIN = true
M2_STRICT_GOVERNANCE_CLOSEOUT = COMPLETE

REAL_OPERATION_LOOP_VERIFIED = false
BUSINESS_OUTCOME_IMPROVEMENT_VERIFIED = false
M5_INTEGRATION_VERIFIED = false
PRODUCTION_ADOPTION_AUTHORIZED = false
```

§11/§14 的 Git 收口现场核验已完成（`recovery_commit = 894211bb025228eb69c50b7c415c4f9de3c6c8dd`；`merge_commit = 03a94ca5eb6ec713c223c62a9c67d01fd7070ff0`；`final_origin_main = 03a94ca5eb6ec713c223c62a9c67d01fd7070ff0`，本地/远程一致，受保护资产零变化），`M2_STRICT_GOVERNANCE_CLOSEOUT = COMPLETE` 生效。完成后立即停止，不继续润色、重构、扩建、重跑开放式审查，不启动 M3/M4/M5，不修改 Dify 或处理任何其他模块问题。
