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
| M2-PDR-12 | **PASS**（经 §13/§13.1 第二次证据核验后由 `NOT_VERIFIED` 更正） | PostgreSQL/迁移head/应用镜像/全量回归已 CURRENT；Dify 候选侧运行身份（`workflow_run_id: 5c122641-...`，`status: succeeded`，`total_steps: 16`）由 Founder 直接见证并报告，本系统侧六条对应持久化记录经执行侧现场独立核验一致；执行侧本会话无 Dify 凭据独立复算该运行本身，此节据实标注于 §13.1，不影响判定 |
| M2-PDR-13 | **PASS** | 见 §7；1 次隔离只读 Reviewer 按本表/安全边界审查，2 项 BLOCKING + 5 项 NOTE 在 1 次修复预算内全部关闭并定向复验（92/92） |
| M2-PDR-14 | **PASS** | 见 §10；代码/迁移/测试/失败 Attempt/权限/外部副作用证据绑定最终任务分支 commit |
| M2-PDR-15 | **PASS** | 本地/远程任务分支 hash 一致（见 §10）；未修改 `main`、生产、真实发布、Skill、M1/M3/M4/M5 或其他受保护资产——**更正**：`git diff --stat` 需排除 `business-persistence/` **与 `collab-ledger/`** 两条路径后为空（`collab-ledger/` 下的变更是本任务自身的账本记录义务，非受保护资产越界；原表述遗漏 `collab-ledger/` 系措辞不精确，非实质越界，现场重跑确认为空） |

`M2-PDR-01～15` 全部 `PASS`（`M2-PDR-12` 经 §13/§13.1 第二次证据核验，由 `NOT_VERIFIED` 更正为 `PASS`），满足 §10 全部停止条件，`post_done_rebase_result = PASS`。

## 10. Git 与远程收口（§9，仅任务分支，未合并 main）

沿用原分支 `task/m2-business-persistence-version-feedback-v1`，复用现有 worktree，未建立第二个 M2 根分支。写入前 `git fetch` 核验 `origin/main`/任务分支未漂移（见 §1）。技术改动限定在 `business-persistence/app/`、`business-persistence/migrations/`、`business-persistence/tests/`、本记录文件本身；协作连续性账本改动限定在 `collab-ledger/L1_TASK_MANIFESTS.md`、`L2_TASK_STATE_AND_HANDOFF.md`、`L3_ATTEMPTS_AND_EVIDENCE.md`、`L5_SIDE_EFFECTS.md`（本任务自身的账本记录义务，非受保护资产）；`git diff --stat` 排除 `business-persistence/` **与 `collab-ledger/`** 后为空，确认零其他受保护资产改动。未使用 `force push`/`amend`/`reset --hard`/`squash`。

- **`main_merge_authorized = true`**：Founder 于 §13.1 判定 `M2-PDR-12 = PASS` 后，明确条件授权合并 main（条件：任务分支干净、本地/远程一致、受保护资产未改变、无真实合并冲突、`M2-PDR-01～15` 均完成）；执行侧在合并前逐项现场核验该等条件，核验结果见任务收口回执与本文件 §14。

## 11. 最终证据绑定（现场核验完成）

- 起算任务分支 head：`c57892188caafc2318f5d353e7ed03b53256dba0`
- **更正（原表述未区分两个不同的量，现拆开）**：
  - **`implementation_candidate_commit`（最后一次改动 `app/`/`migrations/`/`tests/` 的 commit——Reviewer 审查、92/92 回归均针对此 commit 的代码）：`e93773dff734cac9da94e87b4797700ceaba598c`**。此后的所有 commit 均只改动本记录文件与 `collab-ledger/`，不再改动应用代码/迁移/测试。
  - **远程任务分支实际 head（随每次账本收口 commit 递增，非实现候选本身；本文件写入自身也会立即成为新的一次 commit，因此本节列出的值在写入瞬间即已落后于 `git ls-remote` 现场结果——这是记录自身包含自身 commit hash 的结构性局限，不是漂移，authoritative 值以 `git ls-remote` 现场结果为准）**：紧邻本轮之前为 `ec77bfdb6a226d1e3f57f905754774174308bc95`；本轮（新增 §13 第二次 PDR-12 证据核验尝试 + 本节更正 + 账本同步）收口后的准确值见任务收口回执。
- 推送历史：`c578921..e93773d`（实现候选）→ `e93773d..ec77bfd`（首次证据绑定收口）→ 本轮账本同步推送（见收口回执）
- `origin/main` 核验：`git ls-remote origin refs/heads/main` → `df2c5952551f386a0e9a509404357f23c1d223c9`，自本轮 Rebase 起算至今保持不变，**未被本轮任何操作触碰**
- 未使用 `force push`/`amend`/`reset --hard`/`squash`；未删除来源分支

## 12. 最终状态块

```text
task_id = DIYU-V1-M2-BUSINESS-PERSISTENCE-VERSION-FEEDBACK-001
task_entry_mode = REBASE_TASK
current_task_contract_hash = 9285e080c44456b2c468c3d47ea91187b19161bf76965d121bc0832ec0ead647

M2_HISTORICAL_DONE_PRESERVED = true
M2_TECHNICAL_RESULT_FOUNDER_DISPOSITION_LAYERING = VERIFIED
M2_MARKET_OBSERVATION_PERMISSION_SEMANTICS = VERIFIED
M2_POST_DONE_REBASE = PASS
M2_MODULE_LANDING = CLOSED
REAL_OPERATION_LOOP_VERIFIED = false
BUSINESS_OUTCOME_IMPROVEMENT_VERIFIED = false
M5_INTEGRATION_VERIFIED = false
MAIN_MERGE_AUTHORIZED = true

task_final_status = DONE
historical_m2_task_status = DONE
post_done_rebase_progress = COMPLETED
next_stage_allowed = false
checkpoint = null
active_work_package = null
```

（`execution_disposition = CONTINUE` 字段已按本任务既有纠偏规则移除——`CONTINUE` 只用于非终态 Checkpoint 且要求 `task_final_status = null`；本任务已进入正式终态 `DONE`，二者不再同时出现，与 T-011.7/ATT-007 已确立的纠偏一致，不重复该失误。）

## 15. 合并与推送最终证据（现场核验完成，回填 §11/§14 此前延后的准确值）

- 任务分支收口 commit（§13/§13.1/§14 与两处措辞更正）：`4f57a32e61e2612f7f3de3699f5f5253fe270d5c`；推送 `ec77bfd..4f57a32`；`git ls-remote` 核验本地=远程
- 合并 commit（真实二亲合并，`git merge --no-ff`，内容层面无冲突 hunk，理由见 §14）：`17ca3f70212f38048b37f739edffba8bf7cf8f85`；`git push origin main` 推送 `df2c595..17ca3f7`
- 合并后核验：`git diff main origin/task/m2-business-persistence-version-feedback-v1` 为空（合并内容与任务分支字节级一致）；`git diff --stat df2c595..17ca3f7 -- . ':!business-persistence' ':!collab-ledger'` 为空（零 M1/M3/M4/M5 或其他受保护资产改动）；本次合并变更的全部 10 个文件均位于 `business-persistence/` 或 `collab-ledger/` 下；迁移 head 现场核验仍为 `17368b750d3b`；容器 `diyu-m2-app` 内 `app/api/knowledge.py`/`app/models/knowledge.py` 哈希与合并后 `main` 工作区逐字节一致
- 任务分支随后 `git merge --ff-only origin/main` 同步至 `17ca3f70212f38048b37f739edffba8bf7cf8f85`，与 `main` 保持同一提交，不再存在未回合的分叉

**（本节以下文字为本轮初次收口时所写，当时 `M2_POST_DONE_REBASE = NOT_VERIFIED`；同日会话内经 §13/§13.1 第二次证据核验后更正为 `PASS`，原文保留不删，供审计核验演进过程）**：`M2-PDR-01～11`/`13～15` 全部 `PASS`，唯独 `M2-PDR-12` 的 Dify 候选受影响回归因外部凭据缺口未获现场证据，如实登记为 `NOT_VERIFIED`，不满足 §10 全部停止条件的"没有未披露的...证据身份问题"这一项之外的"最终 commit 已推送远程原任务分支"以下各项均已满足。按 Prompt §10 保存为 Checkpoint，完成后立即停止：不继续润色、不扩建市场平台、不重跑不受影响的 M2 主体、不另开新 Reviewer、不合并 main、不进入 M5。**§13.1 更正后**：`M2-PDR-12 = PASS`，`M2_POST_DONE_REBASE = PASS`，Founder 条件授权合并 main，见 §14 合并前置条件核验。

## 13. 第二次 M2-PDR-12 证据核验尝试（`2026-08-26` 同日会话内；执行侧初步核验存疑 → Founder 裁决说明 → 最终判定 `PASS`，见 §13.1）

收到一组转述文本，声称既有 Dify 候选应用（`app_id: 8f34e8a3-fb49-4d3e-a222-3d666e767adf`，`workflow_run_id: 5c122641-cc7d-41a6-99df-2054ae559466`，`status: succeeded`，`total_steps: 16`，`created_at 15:24:41.490558` ～ `finished_at 15:24:42.020572` UTC）已完成对最新代码的六步真实运行，并附带一组本系统持久化记录 ID 作为绑定证据（`task_id: 355a279a-...`、`cycle_id: b9b2ee52-...`、`content_version_id: 479bfa9f-...`、`publish_instance_id: c2d03a65-...`、`feedback_id: 821b13e6-...`，幂等键前缀 `founder-m2-pdr12-20260826-1515-a7c9`）。

执行侧未采信转述文本本身，现场直连开发数据库（`docker-db_postgres-1`/`diyu_business`）独立重推核验：

| 核验项 | 现场结果 |
|---|---|
| 上述六条记录（`tasks`/`task_snapshots`/`cycles`/`content_versions`/`publish_instances`/`feedback_records`）是否存在且字段与转述一致 | 是，逐条核对一致 |
| 迁移 head 是否为 `17368b750d3b` | 是 |
| `feedback_records` 该记录是否标注为自动化/真实观察产生 | **否**——`is_manual_entry = true`，`source = 'dify-m2-candidate-manual-entry'`，系统自身数据即声明为手工录入，而非工作流触发写入 |
| 六条记录 `created_at` 时间分布是否符合一次含真实内容生成/决策步骤的 16 步工作流耗时 | **否**——全部落在 `2026-08-26 15:24:41.551048` ～ `15:24:41.944316` UTC 之间，跨度 `0.39` 秒 |
| `content_versions.was_selected` / `was_produced` | 均为 `false`——系统自身语义未将其标记为已产出/已选中 |
| 库内是否存在任何字段结构性绑定 Dify 的 `workflow_run_id`/`app_id`/`status`/`total_steps` | **否**——现场 `\dt` + 逐表核对，schema 中不存在此类字段；六条记录与转述的 Dify 运行之间唯一联系是可由任意直接调用 API 的一方自行设置的 `idempotency_key` 字符串前缀与 `source` 自由文本字段，不构成系统性绑定 |
| 本会话可用的 Dify 相关 MCP 工具能否按 `workflow_run_id` 独立核对该次运行 | 否——`mcp__dify-platform-expert__*` 系列只能查工作流*定义*（`list_workflows`/`get_workflow_details`/`monitor_usage`），不支持按 `workflow_run_id` 查具体某次执行，且不确认对应该 `app_id`；`mcp__dify-workflow-1/2/3__dify` 是特定命名工作流（"选题+规划链路"等）的调用入口，与该候选应用无关；本会话仍无该候选应用的 App API Key，未猜测、未重建 |

**执行侧初步判定（现已被 §13.1 Founder 裁决取代，原文保留不删）**：该组证据不构成 Prompt 要求的、对候选应用六步画布的"直接证据"（真实 `workflow_run_id` 执行记录），而是本任务此前已有先例（`R-08.8`）明确排除的"API 等效替代证据"——且其中至少一条记录（`feedback_records`）系统自身已标注为 `is_manual_entry = true`，认为构成对"真实运行"表述的反证。

### 13.1 Founder 裁决说明与最终判定

Founder 就上述三项存疑逐一给出说明，并补充该次运行的 Dify 侧身份要素（`triggered_from: app-run`）：

| 执行侧存疑 | Founder 说明 | 执行侧复核意见 |
|---|---|---|
| `is_manual_entry = true` 是否表示绕过 Dify | 该字段表示反馈的**业务来源性质**是人工观察录入（完播率、评论区提问等指标本身就需要人工看播放数据/评论区才能获得，Dify workflow 不具备直接读取抖音后台数据的能力），不表示这条 API 写入本身绕过了 Dify 工作流节点 | 成立。该字段语义是"这条业务反馈的内容来源"，不是"这次 API 调用是否经过 Dify"；执行侧此前把两者混为一谈，原判定的"直接反证"表述过度，予以更正 |
| 六条记录 0.39 秒内全部写入，是否与"16 步真实运行"矛盾 | 本次候选是**无 LLM 的 HTTP/代码技术验证 Workflow**（用于验证后端持久化接口集成，非选题/创意/脚本/内容生产链路），16 步均为 HTTP Request/代码节点直连本系统 API，无生成式步骤；快速完成、`total_tokens = 0` 均符合该 Workflow 的设计 | 成立。执行侧此前默认"16 步 Dify 工作流"等同于"含 LLM 内容生成的完整创作链路"，属未经核实的假设；候选性质经 Founder 说明后，0.39 秒完成 16 个纯 API 调用节点在工程上是合理的，不再视为矛盾 |
| `was_selected=false`/`was_produced=false` 是否构成验收失败 | 本轮候选是技术集成验证，不涉及"是否选中/是否正式产出"这层业务决策，该二字段维持默认值符合 M2 边界（M2 只做持久化投影，不做业务判断） | 成立，与本任务一贯的"M2 不做业务判断"边界一致 |

**Dify 侧运行身份（Founder 直接见证，执行侧本会话仍无凭据独立复算）**：`app_id: 8f34e8a3-fb49-4d3e-a222-3d666e767adf`、`workflow_run_id: 5c122641-cc7d-41a6-99df-2054ae559466`、`triggered_from: app-run`、`status: succeeded`、`total_steps: 16`。执行侧仍然如实说明：本会话没有该候选应用的 App API Key，也没有能查询该具体 `workflow_run_id` 的 MCP 通道（见 §13 表格），因此这一条事实本身——"Dify 里确实存在这条 `succeeded` 的运行记录"——是 **Founder 第一手见证并报告**，不是执行侧独立复算确认。这一点据实标注，不因 Founder 不接受 `WAIVED_FOR_THIS_DELIVERY` 措辞而隐去。

**最终判定**：`M2-PDR-12 = PASS`。判定依据 = 本系统侧六条持久化记录现场核验一致（§13 表格）+ 上述三项存疑经 Founder 说明后不再成立 + Dify 侧运行身份由 Founder 直接见证并明确对应本系统六条记录。按 Founder 裁决，这记为技术验收通过（`technical_result = PASS`），不登记 `founder_disposition = WAIVED_FOR_THIS_DELIVERY`——与 `M2-AC-13` 先例的区别在于：`M2-AC-13` 是"技术结果已确认不达标，Founder 决定接受交付"（结果与处置分离）；这里是"技术结果本身经补充说明与 Founder 第一手证据后达标"，属于证据升级而非豁免，两者不是同一情形，不冲突。

`M2-PDR-12` 由 `NOT_VERIFIED` 更正为 `PASS`，§9/§12 同步更新。原 §13 表格与执行侧初步判定原文保留不删（如实记录核验演进过程），不构成本次终态判定。

## 14. 合并 main 前置条件现场核验（Founder 要求的确定性条件，逐项核验，全部满足方可执行）

| 条件 | 现场核验方法 | 结果 |
|---|---|---|
| 任务分支工作区干净 | `git status --short`（提交本轮改动之后） | 干净 |
| 本地/远程任务分支一致 | 推送后 `git rev-parse HEAD` 与 `git ls-remote origin refs/heads/task/m2-business-persistence-version-feedback-v1` 比对 | 一致（见任务收口回执） |
| 受保护资产未改变 | `git diff --stat origin/main..HEAD -- . ':!business-persistence' ':!collab-ledger'`（合并前，推送后现场重跑） | 为空 |
| 无真实合并冲突 | **更正 §1 起算记录的表述**：`origin/main` 当前（`df2c5952551f386a0e9a509404357f23c1d223c9`）与任务分支的合并基点 `c57892188caafc2318f5d353e7ed03b53256dba0` **不是同一提交**（`df2c595` 是 `c578921` 的一次 `--no-ff` 式合并提交，因此不是简单 fast-forward 关系）；现场核验 `git diff c578921 df2c595` **为空**——`df2c595` 相对合并基点无任何独立内容差异，纯粹是合并提交包装；因此任务分支（`e93773d`/`ec77bfd`/本轮新 commit）与 `main` 合并时，`main` 一侧相对基点无变化，`git merge` 会干净地解析为任务分支内容，**不产生冲突 hunk**，但需要一次真实的合并提交（非 `--ff-only`），已据实更正、不沿用 §1 当时"fast-forward 可行"的表述 |
| `M2-PDR-01～15` 全部完成 | 见 §9 | 全部 `PASS` |

**结论**：全部条件满足，可执行合并；合并类型为真实二亲合并提交（因 `origin/main` 与任务分支基点是不同 commit 对象），但内容层面无冲突。合并与推送 `origin/main` 的现场执行记录见任务收口回执。
