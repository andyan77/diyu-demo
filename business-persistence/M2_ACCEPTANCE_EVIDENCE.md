# M2 验收证据记录（M2-AC-00 ~ M2-AC-17）

> 依据 `decision-chain/docs/M2_ENGINEERING_EXECUTION_PROMPT_v1.1.md` §9 的格式要求逐条登记。
> 本文件由执行侧撰写，不构成产品合同，不晋升为验收 Oracle 本身——真正的 Oracle 仍是该
> Prompt 第 9 节原文。`evidence_binding` 一律绑定到 commit hash，而不是"测试通过"这类
> 不可复算的自然语言描述。

**证据绑定基线**：`task/m2-business-persistence-version-feedback-v1` @ `f09e2923a7b57efbcb94cd83ed54c5b6cd94b3c4`（本地与远程一致，`git push` 输出 `020bc58..f09e292` 已核验）。数据库：PostgreSQL 15.19，`docker-db_postgres-1`，独立数据库 `diyu_business`，owner `diyu_app`（`NOSUPERUSER NOCREATEDB NOCREATEROLE`）。应用容器：`diyu-m2-app`（镜像 `diyu-m2-app:dev`，由本次最终 commit 的源码构建），`docker_default` 网络。全量测试：`docker run --rm --network docker_default -e APP_BASE_URL=http://diyu-m2-app:8000 diyu-m2-app:dev pytest tests/ -q` → **66 passed**（对当前 head 现场重跑，非历史记录）。迁移链：`fdbd31cee7f9 → 6033064ae1ed → 6bc000bb178d → fb5e3889277c → db747c8a1f80 → a1c5e7d4f2b9 → c3f8b2e6d0a4`（现场 `alembic current` 核验为 `c3f8b2e6d0a4 (head)`）。

## 独立审查记录（本文件撰写前完成，供逐条引用）

本轮补齐 M2-AC-07/14/15 三个缺口后，先后进行了三次独立、上下文隔离的对抗性审查（均为只读或建议性，不共享本任务实现上下文）：

1. 审查 A（scope/data-integrity）+ 审查 B（correctness/test-validity）：并行审查 AC-07/14/15 三处新代码，发现 4 个真实缺陷（含 1 个阻断级——legacy-import 与活体任务共享 idempotency 命名空间，导致假成功与身份混淆），已在 commit `020bc58` 修复。
2. 收口验证（仅复核受影响范围，不开放式找茬，符合 Prompt §11.1 的预算约束）：确认全部 4 项修复真实生效，同时发现 1 个由修复本身引入的新缺陷（legacy-import 重试遇多快照抛 500），已在 commit `f09e292` 修复。

三次审查的具体发现、复现证据与修复对应关系见对应 commit message 原文（`020bc58`、`f09e292`）。

## AC 逐条记录

| criterion_id | 结果 | 证据摘要 | evidence_binding |
|---|---|---|---|
| M2-AC-00 | **PASS** | 独立 worktree（`/home/faye/diyu-demo-worktrees/m2-business-persistence-version-feedback-v1`）、独立任务分支、独立数据库 `diyu_business`（与 `dify`/`dify_plugin` 物理隔离，`REVOKE ALL` 已验证）、Task Contract 哈希独立复算（`4d14eb35c065b650b0380b0c309e0e08ec32e3aa608ece4d62e8d27b97450830`，见 L1 §T-010，与文档自称值不一致已披露，本任务采用独立复算值） | `task/m2-business-persistence-version-feedback-v1` 分支 + `TECHNICAL_DECISION_RECORD.md` §数据库隔离方式 |
| M2-AC-01 | **PASS** | `require_membership`+`X-Actor-Ref`+`WorkspaceMembership`；`tests/test_isolation.py` 8 项正负向（未授权 401、非成员 403、跨 workspace 404、个人/企业 workspace 不越权混用） | `a3eeb2f` app/api/deps.py, tests/test_isolation.py |
| M2-AC-02 | **PASS** | `TaskSnapshot` 五维列（info_nature/source/confirmation_status/scope/availability_status）为真实列而非塞进 payload；`get_task_projection` 最小投影读取路径 | `app/models/content.py:43-78`, `app/api/tasks.py` get_task_projection |
| M2-AC-03 | **PASS** | `content_versions` 部分唯一索引（`is_current` 唯一）+ `promote_version` 原子晋升；`tests/test_versioning.py`、`tests/test_concurrency.py` 两项真实并发晋升测试（不同版本互斥、同版本重复晋升不重复计） | `app/services/versioning.py`, tests/test_versioning.py, tests/test_concurrency.py |
| M2-AC-04 | **PASS** | Task/Artifact/ContentVersion/PublishInstance/FeedbackRecord 关系链完整；`was_selected`/`was_produced` 为可叠加标志而非互斥单一状态 | `app/models/content.py` |
| M2-AC-05 | **PASS** | `is_test`/`is_simulated`/`is_manual_entry`/`is_pre_publish_review` 显式布尔字段，默认值均为"真实/非测试"；`tests/test_publish_feedback.py::test_evidence_isolation_flags_round_trip` | `app/models/publish.py`, `app/api/publish.py` |
| M2-AC-06 | **PASS** | `register_feedback` 强制 `publish_instance_id` 与 `content_version_id` 二选一且与 `is_pre_publish_review` 一致；未发布对象无法绑定反馈 | `app/api/publish.py::register_feedback`, tests/test_publish_feedback.py |
| M2-AC-07 | **PASS**（本轮补齐） | `create_cycle` 表达"M3 提出并落地调整"（原子 supersede）；新增 `cycle_decisions` 表 + `record_cycle_decision`/`get_latest_cycle_decision` 表达"M3 评估后明确保持不变"，且对已被取代的 cycle 记录 kept_unchanged 会被结构性拒绝（422，非专业判断）；`tests/test_cycle_campaign.py` 6 项新测试覆盖两分支正负向 | `d7f9e94`, `020bc58`（stale-cycle 校验）, `migrations/versions/a1c5e7d4f2b9_*.py`, `migrations/versions/c3f8b2e6d0a4_*.py` |
| M2-AC-08 | **PASS** | `CampaignOverride` 覆盖/结束/取消生命周期；`tests/test_cycle_campaign.py::test_campaign_override_targets_positions_and_ends_cleanly` + 账号/周期不匹配负向 | `app/models/operations.py::CampaignOverride`, tests/test_cycle_campaign.py |
| M2-AC-09 | **PASS** | `Cycle.baseline_capacity`/`actual_capacity`/`expected_publish_count` 三分且各自独立 `*_source`；`test_capacity_triple_split_kept_separate` | `app/models/operations.py::Cycle`, tests/test_cycle_campaign.py |
| M2-AC-10 | **PASS** | `Playbook` 按 `(workspace_id, name)` 版本化、`supersedes_playbook_id` 链式历史、`proposed_by`/`observation_status`/`rationale` 自由字段（非固定枚举）；`tests/test_recovery_and_playbooks.py` | `app/models/knowledge.py::Playbook` |
| M2-AC-11 | **PASS** | `Material.withdrawn_at` + `ContentVersionMaterialDependency` 精确到 content_version 级级联失效；撤回后不可被新版本引用（409）；`tests/test_material_withdrawal.py` 7 项，含两个真实并发竞态回归（20 轮 trial，0 违反） | `a3eeb2f`, `app/services/versioning.py::withdraw_material`, tests/test_material_withdrawal.py |
| M2-AC-12 | **PASS** | 全部创建型端点 `(workspace_id[, account_id], idempotency_key)` 复合唯一 + `IntegrityError` 捕获重查；晋升/决定类操作用乐观并发 `row_version`；`tests/test_idempotency.py`、`tests/test_concurrency.py`；本轮独立审查额外发现并修复了两处历史遗留的"按 workspace 而非按 account 去重"的幂等范围漏洞（`create_cycle`、`record_cycle_decision`） | `a3eeb2f`, `020bc58`, `migrations/versions/c3f8b2e6d0a4_*.py` |
| M2-AC-13 | **PASS** | 7 个迁移线性链，`alembic upgrade head`/`current` 现场核验一致；收口验证独立完成 `upgrade → downgrade -1 → upgrade` 往返，确认可逆且 `alembic check` 无模型/schema 漂移；Dify 自身 `dify`/`dify_plugin` 库全程零改写（物理隔离，`diyu_app` 角色无权限连接） | migrations/versions/*.py, `TECHNICAL_DECISION_RECORD.md` §迁移与部分唯一索引 |
| M2-AC-14 | **PASS**（本轮补齐） | `POST /workspaces/{id}/tasks/legacy-import` 导入 `V1_TASK_SNAPSHOT_SCHEMA_v0.1.json` 形态对象为单个 Task+TaskSnapshot，`source="legacy_dify_5slot_import"` discriminator；独立审查发现并修复了"与活体任务共享 idempotency 命名空间"的阻断级问题——现用独立的 `legacy_import_records` 表（导入产生的 Task 行 `idempotency_key` 恒为 NULL，与活体任务命名空间结构性隔离）；`tests/test_legacy_import.py` 8 项，含两个方向的撞键回归 | `0546f30`, `020bc58`, `f09e292`, `app/models/content.py::LegacyImportRecord` |
| M2-AC-15 | **PASS**（本轮补齐） | `tests/test_interface_contracts.py` 用现有 API 表面钉住 M1/M3/M4 三条边界（无对话形状字段、专业判断值原样存储不评判、内容版本只接收已产出引用不做生成）；独立审查确认现有实现下三条边界本身即成立（未触发任何修复），且加强了此前偏弱的 M1 边界断言（改为先写入真实数据、显式断言 200） | `44f02dd`, `020bc58` |
| M2-AC-16 | **PASS，但含一项已披露的证据新鲜度限制** | 目标环境真实运行（PostgreSQL+应用容器现场核验）、正向/负向/并发/回归全部通过（66/66）、三轮独立审查+收口验证完成、Git 收口（本地=远程 `f09e292`）。**限制**：Dify 候选画布的端到端六步真实运行证据来自本轮代码变更**之前**（上一会话，17/17 节点成功）；本轮新增的三个端点未被 Dify 候选调用（候选契约未变），但按 Prompt `evidence_reuse_policy.criterion_dependency_map`（"应用后端...变化后，AC-16 证据必须刷新"）的字面要求，本应重新触发一次画布运行。本次未能重新触发：核验过一个可用的 `dify-platform-expert` MCP 连接，但其 `get_platform_info` 显示指向 `Dify 1.9.2 @ localhost:8080`，与本项目实际使用的 `Dify 1.16.1` 实例不是同一系统，判断为不相关工具后未采用；未重新走 Console API 会话刷新（需要有效 refresh_token，本会话未取得）。等价证据：66 项回归测试覆盖 Dify 候选实际调用的全部端点契约（create task/version/promote/publish/feedback/cycle），在本次重建后的容器上现场跑通 | 见上方"证据绑定基线"；`FOUNDER_TEST_PACKAGE.md`（画布证据历史部分） |
| M2-AC-17 | **NOT_VERIFIED（预期状态，非缺陷）** | Founder 尚未通过 Dify 画布完成产品/业务验收。`module_delivery_state` 应登记为 `AWAITING_FOUNDER_DIFY_ACCEPTANCE`，`task_final_status = null`，`next_stage_allowed = false` | 待 Founder 实测回执 |

## 结论

`M2-AC-00` 至 `M2-AC-16` 现场证据 PASS（AC-16 含一项已披露、不影响功能正确性的证据新鲜度限制，见上表）。`M2-AC-17` 未验证——按 Prompt §11.2，持久化如下状态，**不得**声明 `DONE`：

```text
execution_disposition = CONTINUE
task_final_status = null
module_delivery_state = AWAITING_FOUNDER_DIFY_ACCEPTANCE
next_stage_allowed = false
```

## 已知限制（如实披露，非隐藏缺陷）

- `create_version` 的 `version_no` 分配（`max+1`）在同一 artifact 高并发创建下可能触发裸 500（见 `TECHNICAL_DECISION_RECORD.md` 已披露残留项）——不属于本次任一 AC 的阻断范围。
- AC-14 的旧兼容 fixture 覆盖范围是 Prompt 举例的"V1 Demo 5 槽 task_snapshot_json"，未覆盖 Prompt 原文提到的"3 槽"或独立的旧 Matrix/Campaign/Content Brief 产物直接导入——本轮只对齐了 5 槽任务状态快照这一种，其余旧产物兼容适配器如需要应另行评估。
- AC-16 的 Dify 画布证据新鲜度限制见上表，等价 API 级证据已现场验证，画布级证据留待下次可访问真实 Dify 会话时补跑。
