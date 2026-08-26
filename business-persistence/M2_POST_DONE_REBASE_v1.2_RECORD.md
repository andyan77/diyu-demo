# M2 post-DONE 定向 Rebase v1.2 记录

`task_id: DIYU-V1-M2-BUSINESS-PERSISTENCE-VERSION-FEEDBACK-001`

> 依据 `M2_POST_DONE_REBASE_EXECUTION_PROMPT_v1.2.md`（Founder 2026-08-26 明确授权，
> `sha256 = c4f5e2de896320acaa82af40d0025f0fef8c43da3490a4f8d2e58787a18865c8`，现场
> 重算一致）驱动。`task_entry_mode = REBASE_TASK`；沿用同一 `task_id`；不改变历史
> `DONE` 已经发生这一事实；不重做 M2 主体；不启动 M1/M3/M4/M5。

## 1. 权威输入核验（现场重算，未使用历史观察值冒充当前基线）

| 文件 | SHA-256（现场重算） | 结果 |
|---|---|---|
| `M2_POST_DONE_REBASE_EXECUTION_PROMPT_v1.2.md` | `c4f5e2de896320acaa82af40d0025f0fef8c43da3490a4f8d2e58787a18865c8` | 与 Founder 授权值一致 |
| `/mnt/c/Users/Administrator/Documents/Codex/Diyu-V1-Planning/DIYU_V1_PLANNING_DELIVERY_BASELINE_v1.0.md` | `aa5997c36e2bf17a565b972c858ec03a58fec6ecb6d9ae6b4845d62bf7a3d640` | 与 Prompt 声明一致 |
| `笛语_V1_M0-M5_统一项目构建与验收方案_v1.1.md` | `50262cc169afc91f8b49b38e071f7a4288e193af3eafc193d53e0daa5122442b` | 与 Prompt 声明一致 |
| `DIYU_V1_M1_M4_UNIFIED_BASELINE_ADOPTION_AND_DELTA_REVIEW_v1.1.md` | `4cdc920918019a59c83f1a78aed20720623b91ef84d1d043746b1ac276e58913` | 与 Prompt 声明一致 |
| M2 根 Prompt v1.1 | `8008bebd04b35037e16f5462ea1b7284db7dec943e954263762bbdb4688bb0c6` | 与 Prompt 声明一致 |

现场 Git/运行时核验（起始于本轮 Rebase 之前）：

| 项 | 现场值 | 与规划侧观察值比对 |
|---|---|---|
| `origin` 默认分支 | `main` | 一致 |
| `origin/main`（起算） | `df2c5952551f386a0e9a509404357f23c1d223c9` | 一致 |
| 原 M2 任务分支 head（起算） | `c57892188caafc2318f5d353e7ed03b53256dba0` | 一致 |
| 任务分支是否为 `origin/main` 祖先 | 是（`git merge-base --is-ancestor` 通过） | 一致 |
| 运行容器 `diyu-m2-app` | `healthz = {"status":"ok"}` | 一致 |
| 迁移 head（起算） | `c3f8b2e6d0a4` | 一致 |
| Dify 候选身份 | 沿用既有记录（`app_id: 8f34e8a3-...`），本次会话无凭据，未做现场只读查询 | 未重新核验（见 §7 披露） |

无现场值漂移；未触发 §10 强制停止条件。

## 2. Task Contract

```yaml
previous_task_contract_hash: 4d14eb35c065b650b0380b0c309e0e08ec32e3aa608ece4d62e8d27b97450830
current_task_contract_hash: 9285e080c44456b2c468c3d47ea91187b19161bf76965d121bc0832ec0ead647
task_entry_mode: REBASE_TASK
new_task: false
historical_done_preserved: true
```

## 3. STALE / 复用集合

按 Prompt §3 冻结的失效集合执行：`M2-AC-13`/`M2-RB-10` 的技术结果表达、"AC-00～17 全部技术通过"汇总结论、市场观察权限字段落盘声明均置 `STALE` 并本轮重新核验（见 §4/§5）。用户/工作空间/账号/周期/任务、任务快照、版本晋升与历史、测试/模拟/人工/真实隔离、发布实例与反馈绑定、Cycle/Campaign、三类产能、打法版本化、素材撤回、旧 Demo 兼容、M1/M3/M4 既有接口边界、历史 Dify Founder 验收、审查预算偏差确认——本轮现场复核（全量回归 92/92 通过，含全部既有测试）确认均未受影响，按 Prompt 规定继续复用，未全量推倒。

## 4. 技术结果与 Founder 处置分层（R-02）

```yaml
criterion_id: M2-AC-13
technical_result: NOT_MET
technical_evidence_currency: CURRENT
founder_disposition: WAIVED_FOR_THIS_DELIVERY
blocking_effect: false
historical_task_status: DONE
```

`M2-RB-10` 同步。前向更正了此前把 `FOUNDER_WAIVED` 直接放进"结果"列、以及"AC-00～17 全部技术通过"这类汇总表述——`M2-AC-13` 的技术事实（跨账号同键 downgrade 不能自动恢复）与 Founder 的豁免决定是两个正交维度，本记录起同一份文档内两者分列，不再合并成一个词。历史文件与旧 commit 保留不删。

## 5. 市场观察权限语义（R-03/R-04）

### 5.1 新增字段（`market_observations`，向后兼容扩展，未删除/收窄任何既有字段）

`source_type`（自由值，非封闭枚举）、`source_reference`、`source_provider`、`account_id`（FK `accounts`）、`applicable_task_id`（FK `tasks`）、`applicable_period_start`/`applicable_period_end`、`permission_status`（`allowed|unknown|missing|denied|restricted` 五态，默认 `unknown`，**绝不**默认 `allowed`）、`permission_basis`（JSONB，自由值或结构化对象）、`usage_limits`（JSONB）、`permission_confirmed_by`/`permission_confirmed_at`、`evidence_digest`（调用方提供，M2 不计算，与既有 `content_hash` 同一约定）、`idempotency_key`。

### 5.2 访问控制与来源使用权限分离

`require_membership`（workspace 成员关系）完全未改动，继续是唯一的访问门；`permission_status` 是完全独立的第二道门——成员身份从不推导出使用权限，"可见"从不推导出"可发布/可复制/可当品牌事实"（`usage_limits` 携带具体限制，"restricted" 与纯 "allowed" 是可区分的两个状态，限制会随投影一起传递，不会在确认动作的部分更新中被静默清空，见 §7 独立审查修复 2）。

### 5.3 最小投影（`GET /market-observations/current`）

只有 `permission_status ∈ {allowed, restricted}` 且未过期且匹配全部请求范围（account/赛道/task/时间窗）的观察被标记"当前可用"；其余每一条都会出现在 `excluded` 列表并附带具体原因（`permission_unknown`/`permission_missing`/`permission_denied`/`expired`/`scope_mismatch`），不会被静默丢弃（见 §7 独立审查修复 1）。无可用观察时返回明确的 `gap_reason`（`no_observation_recorded`/`no_observation_in_scope`/`all_observations_excluded`），不伪造观察，响应体不含任何因果/对话/竞争性结论字段（结构上不存在能承载"平台稀缺/唯一/已避免同质化"这类断言的字段）。三层（`raw`/`analysis`/`homogeneous_judgment`）原样存储，代码路径中没有任何地方相互改写。

### 5.4 M2/M3/M4 边界

M2 只保存与投影；`tests/test_interface_contracts.py` 新增合同测试钉死 `/current` 响应不含对话/因果形状字段。

## 6. 兼容迁移、幂等、并发（R-05）

新迁移 `17368b750d3b_market_observation_permission_semantics.py`（`Revises: c3f8b2e6d0a4`）：仅新增列/索引，未改写任何既有迁移文件，未触碰 Dify 自身数据库表。

- `permission_status` 以 `NOT NULL, server_default='unknown'` 新增（同一 commit 内验证：现场 61→123 条既有记录全部回填为 `unknown`，从未出现 `allowed`），随后丢弃 server_default，改由模型 Python 侧 default 承接（同 `db747c8a1f80` 对 `task_run_states.row_version` 的既有模式）。
- 幂等由 **部分唯一索引**（`WHERE idempotency_key IS NOT NULL`）承载，键为 `(workspace_id, account_id, idempotency_key)`，对该子集使用 Postgres 15+ 的 `NULLS NOT DISTINCT`：
  - 同一 workspace 不同真实账号共享同一 `idempotency_key` 字符串**不再**互相覆盖（复现并修复了与 `c3f8b2e6d0a4` 文档记录的同一类缺陷，见 §7 独立审查发现 3）；
  - 同一 workspace 内多条"不挂账号"（`account_id IS NULL`）的观察复用同一 `idempotency_key` 时仍正确去重为同一行；
  - 索引必须是**部分**索引：现场实测过（见下）"不加 WHERE、对全表应用 NULLS NOT DISTINCT"会让 61 条既有记录（均为 `account_id=NULL, idempotency_key=NULL`）互相判定为同一 `(workspace_id, NULL, NULL)` 的"重复"，`upgrade` 直接 `UniqueViolation` 失败——Alembic 事务性 DDL 保证失败当场完整回滚（现场核验 `alembic current` 退回 `c3f8b2e6d0a4`，表结构逐列核对与迁移前完全一致），未产生任何半成品 schema，这是这次迁移唯一真实触发的失败场景及其确认可安全恢复的证据；加上 `WHERE idempotency_key IS NOT NULL` 后同一批数据 `upgrade` 干净通过。
- 现场对真实累积数据库（非空库/非影子库）完成 `upgrade → downgrade → upgrade` 往返验证两次（首次错误版本 + 修正后版本），`alembic check` 均报告 `No new upgrade operations detected`（无模型漂移）。

创建路径：重试同一 `idempotency_key`（含并发竞态）返回既有行，不产生重复、不产生裸 500（`test_concurrent_create_with_same_idempotency_key_never_5xxs_and_persists_exactly_one_row`，8 路并发）；读取严格 workspace 成员关系约束，一个 workspace 的观察不可被另一个 workspace 读取或使用（含 `/current` 端点）。

## 7. 独立审查（§7 预算：1 次正式审查 + 1 次修复，本轮如实用尽，未另开新审查）

按 Prompt §7 授权，派出 1 个上下文隔离、只读的独立 Reviewer Agent 审查本轮全部 diff。审查发现 2 项 BLOCKING、5 项 NOTE：

| # | 严重级 | 发现 | 处置 |
|---|---|---|---|
| 1 | BLOCKING | `/current` 计算了 `scope_mismatch` 原因但从未在响应中暴露；混合场景下（一条命中范围可用、另一条范围不匹配）后者会无声消失，无处可查 | 已修复：响应新增 `excluded` 列表，逐条记录 id+reason，范围排除也纳入其中；新增 `test_current_projection_states_a_reason_for_every_non_usable_record_mixed_case` 钉死"每条都被计入一次" |
| 2 | BLOCKING | 权限确认端点无条件覆盖 `usage_limits`/`permission_basis`；省略这两个字段的二次确认会把它们静默清空为 `null`，"restricted 携带限制"这一要求被破坏 | 已修复：改用 `model_fields_set` 只更新调用方实际传入的字段，省略即保留、显式传 `null` 才清空；新增 `test_permission_confirmation_partial_update_preserves_omitted_fields` |
| 3 | NOTE（本次按 §6 执行自主权主动修复，未降低任何标准） | 幂等唯一约束只到 workspace 粒度，未含 account_id——与本仓库 `c3f8b2e6d0a4` 已记录修复过的同一类缺陷（不同账号共享 key 会互相覆盖）同源复现 | 已修复为 §6 所述的部分唯一索引方案；新增两条测试覆盖跨账号不串扰与"无账号"场景仍去重 |
| 4 | NOTE（主动修复） | `_permission_exclusion_reason` 是"拒绝清单"而非"允许清单"，已声明的 `CURRENTLY_USABLE_PERMISSION_STATUSES` 常量未被引用，对未知未来状态值默认放行 | 已改为对该常量做允许清单判断（fail-closed），常量随之被实际使用 |
| 5 | NOTE（主动修复） | `applicable_period_start`/`applicable_period_end` 比较未做时区归一化，naive/aware 混用输入会抛未捕获异常，产生裸 500 而非 422 | 已改用既有 `_aware()` 归一化后再比较；新增测试覆盖"混合但合法"通过、"混合且非法"仍是 422 而非 500 |
| 6 | NOTE（主动修复） | `/current` 的 `account_id`/`task_id` 过滤参数未校验属于当前 workspace（create 端点已校验） | 已补齐同等校验（404），与 create 端点一致；新增测试覆盖跨 workspace 过滤参数与本 workspace 内合法参数两种情形 |
| 7 | NOTE（主动补测） | `at` 参数语义未在文档中说明、无测试覆盖 | 补充端点文档说明 + `test_at_parameter_evaluates_usability_as_of_a_reference_time` |

修复全部在本次 1 次修复预算内一次性完成，未另开第二轮独立审查，未降低任何验收标准，未拔高任何技术结论。修复后现场重跑全量测试：**92/92 通过**（较修复前的 85/85 新增 7 条，覆盖上述 7 项发现）。

## 8. 应用、数据库与 Dify 受影响收口（R-07）

- 已授权开发/测试环境应用新迁移（见 §6），`alembic check` 无漂移。
- 已重建并重启 `diyu-m2-app` 镜像（`docker build` + `stop/rm/run`），`healthz = {"status":"ok"}`，容器内 `app/api/knowledge.py`/`app/models/knowledge.py` 哈希与本地任务分支 worktree 逐字节一致。
- 正向/负向/并发/兼容/全量回归：**92/92 通过**（现场重跑，非自报）。
- **Dify 候选受影响回归（R-07.5）：未完成，如实披露**——本轮改动完全限定在 `knowledge.py`（`market_observations`/`playbooks`），`FOUNDER_TEST_PACKAGE.md` 六步候选场景实际调用的端点（`tasks.py`/`content.py`/`operations.py`/`publish.py`）本轮零改动，且全量回归覆盖这些端点的既有测试全部通过——这是本轮改动未破坏六步主链的**间接证据**，但不是 Prompt 要求的"对现有六步候选做一次回归运行"这一**直接证据**。本会话内没有该候选应用（`app_id: 8f34e8a3-fb49-4d3e-a222-3d666e767adf`）的可用 App API Key 或 Console 会话；未索要、未猜测、未重建任何凭据。按 Prompt R-07.6/R-07.7，本次**未**因此修改/重新导入/重新发布 Dify 应用，**未**要求 Founder 重新做产品/业务验收（候选交互和产品含义均未变化）——缺口仅限于"用真实凭据触发一次六步画布运行、拿到真实 `workflow_run_id` 作为 `M2-PDR-12` 的直接证据"这一件事，需要 Founder 提供该候选应用的 App API Key（或明确裁决豁免这一项直接证据、接受间接证据）。

## 9. `M2-PDR-01～15` 逐项结果

| criterion_id | 结果 | 说明 |
|---|---|---|
| M2-PDR-01 | **PASS** | 见 §1；同一 task_id、`REBASE_TASK`、新旧合同哈希、历史 DONE、当前 main/任务分支与副作用完整继承 |
| M2-PDR-02 | **PASS** | 见 §3；仅技术结果/Founder处置、市场观察权限及其影响项置 STALE，未受影响证据（92 项既有+新增回归）复用确认 |
| M2-PDR-03 | **PASS** | 见 §4；`M2-AC-13` 技术结果单列为 `NOT_MET`，Founder 处置单列为 `WAIVED_FOR_THIS_DELIVERY`，未再用 `FOUNDER_WAIVED` 冒充结果列 |
| M2-PDR-04 | **PASS** | 见 §5.1；来源/平台/时间/范围/权限/时效/层级/证据身份全部可无损表达，访问授权（workspace 成员）与来源使用权限（`permission_status`）分离实现 |
| M2-PDR-05 | **PASS** | 见 §5.3；`excluded` 列表逐条给出未知/缺失/拒绝/过期/范围不匹配的排除原因，历史仍可通过 `list` 端点追溯 |
| M2-PDR-06 | **PASS** | 见 §5.3；`gap_reason` 三态明确区分"无记录/无范围内记录/全部被排除"，响应体结构上不存在可承载稀缺/唯一/已避同质化结论的字段 |
| M2-PDR-07 | **PASS** | M2 只保存/投影，未新增任何解释性字段或判断逻辑；`test_interface_contracts.py` 新增合同测试钉死 |
| M2-PDR-08 | **PASS** | 见 §6；既有记录未被追溯默认授权（回填 `unknown`），新迁移可重复（upgrade/downgrade/upgrade 两轮验证），Dify 内部表零改写 |
| M2-PDR-09 | **PASS** | 见 §6/§7 发现 3；幂等/并发/失败恢复语义完整，跨 workspace 与跨 account 均不串扰 |
| M2-PDR-10 | **PASS** | 见 §7；代表性来源、权限五态、时效、范围、层级、无观察、竞争结论禁止、隔离、并发、旧记录测试全部通过（92/92） |
| M2-PDR-11 | **PASS** | `test_m3_m4_boundary_market_observation_projection_is_a_plain_minimal_projection` 钉死 `/current` 无对话/因果形状字段 |
| M2-PDR-12 | **NOT_VERIFIED（部分）** | PostgreSQL/迁移head/应用镜像/全量回归已重新获得 CURRENT 证据；**Dify 候选**这一项因本会话无可用凭据未能重新获得 CURRENT 证据，见 §8 如实披露 |
| M2-PDR-13 | **PASS** | 见 §7；1 次隔离只读 Reviewer 按本表/安全边界审查，2 项 BLOCKING + 5 项 NOTE 在 1 次修复预算内全部关闭并定向复验（92/92） |
| M2-PDR-14 | **PASS** | 见 §10；代码/迁移/测试/失败 Attempt/权限/外部副作用证据绑定最终任务分支 commit |
| M2-PDR-15 | **PASS** | 本地/远程任务分支 hash 一致（见 §10）；未修改 `main`、生产、真实发布、Skill、M1/M3/M4/M5 或其他受保护资产（`git diff --stat` 排除 `business-persistence/` 后为空） |

`M2-PDR-01～11`、`13～15` 全部 `PASS`；`M2-PDR-12` 因外部凭据缺口部分 `NOT_VERIFIED`，不满足 §10 全部停止条件，因此本轮登记为 **Checkpoint**，不宣告 `post_done_rebase_result = PASS`。

## 10. Git 与远程收口（§9，仅任务分支，未合并 main）

沿用原分支 `task/m2-business-persistence-version-feedback-v1`，复用现有 worktree，未建立第二个 M2 根分支。写入前 `git fetch` 核验 `origin/main`/任务分支未漂移（见 §1）。全部改动限定在 `business-persistence/app/`、`business-persistence/migrations/`、`business-persistence/tests/`、本记录文件本身；`git diff --stat` 排除 `business-persistence/` 后为空，确认零受保护资产改动。未使用 `force push`/`amend`/`reset --hard`/`squash`。

- 任务分支提交（本轮）：见下方"最终证据绑定"（提交后现场核验补齐）。
- **`main_merge_authorized = false`**：Founder 本次明确不授权合并 main；本记录完成、提交、推送任务分支后立即停止，等待 Founder 对准确最终 commit 另行裁决是否合并。

<!-- 最终证据绑定：提交与推送完成后现场核验并登记于此 -->
