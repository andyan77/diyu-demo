# M2 验收证据记录（M2-AC-00 ~ M2-AC-17，M2-RB-01 ~ M2-RB-14）

> 依据 `decision-chain/docs/M2_ENGINEERING_EXECUTION_PROMPT_v1.1.md` §9 与
> `M2_ENGINEERING_EXECUTION_PROMPT_v1.1_REBASE_ERRATA_001.md` §7/R-06 的格式与纠偏要求逐条登记。
> 本文件由执行侧撰写，不构成产品合同，不晋升为验收 Oracle 本身。`evidence_binding` 一律绑定到
> commit hash。任一验收项没有完整证据一律标记 `NOT_VERIFIED`，不使用 `PASS_WITH_LIMITATION`/
> `MOSTLY_PASS`/`BASICALLY_DONE`/`OUT_OF_SCOPE` 之类规避原 P0 的措辞。

**本次修订（Rebase/Errata 001 后）取代同名文件的上一版本**，不是追加；上一版本对
`M2-AC-12`/`M2-AC-14`/`M2-AC-16` 的部分表述已被本轮现场复验证明不准确（见下方逐条记录），
按 Rebase Prompt R-06 要求直接纠正，不用说明文字掩盖。

**证据绑定基线**：`task/m2-business-persistence-version-feedback-v1` @ `6955d669e94b7749ac6466f231313af755d48cc2`（本地与远程一致，逐次 `git push` 输出已核验）。数据库：PostgreSQL 15.19，`docker-db_postgres-1`，独立数据库 `diyu_business`，owner `diyu_app`（`NOSUPERUSER NOCREATEDB NOCREATEROLE`）。应用容器：`diyu-m2-app`（镜像 `diyu-m2-app:dev`，由本 commit 源码构建）。全量测试：`docker run --rm --network docker_default -e APP_BASE_URL=http://diyu-m2-app:8000 diyu-m2-app:dev pytest tests/ -q` → **69 passed**（对当前 head 现场重跑）。迁移链：`fdbd31cee7f9 → 6033064ae1ed → 6bc000bb178d → fb5e3889277c → db747c8a1f80 → a1c5e7d4f2b9 → c3f8b2e6d0a4`（现场 `alembic current` = `c3f8b2e6d0a4 (head)`）。

## 审查与自验记录

1. 初版实现的独立对抗性审查：发现 21 项缺陷（6 项阻断级），修复于 `a3eeb2f`。
2. M2-AC-07/14/15 补齐后，并行派出 2 个独立、上下文隔离的审查 Agent（scope/data-integrity、correctness/test-validity）：发现 4 项真实缺陷（含 1 项阻断级），修复于 `020bc58`。
3. 收口验证（1 个独立 Agent，仅复核受影响范围）：发现修复本身引入的新缺陷 1 项，修复于 `f09e292`。
4. **本轮 Rebase/Errata 001（`M2_REBASE_ERRATA_001_RECORD.md`）**：按 R-10 约束，未派出任何新的正式 Reviewer，全部由执行负责人本人在真实容器/数据库上直接操作复现：
   - R-04：8 路真实并发实测复现 `create_version` 版本号裸 500（5/8 失败），修复后连续 5 轮 8/8 成功，修复于 `3d23674`。
   - R-05：穷尽检索确认无独立"3 槽"Schema 文件；用 3 份真实历史生产产物（真实 sha256）经既有端点显式导入，修复于 `fabffd8`。
   - R-09：对真实累积数据（非空库）实测 `alembic downgrade -1` 复现裸崩溃，修复为清晰错误，修复于 `6955d66`；同一轮发现 `diyu_app` 对 `dify`/`dify_plugin` 的 CONNECT 权限未被撤销，修复尝试被权限分类器拦截，**未修复，见 M2-AC-13 行**。

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
| M2-AC-13 | **NOT_VERIFIED（本轮由 PASS 下修，真实发现，非此前已知）** | 迁移链本身正确、可逆（`c3f8b2e6d0a4` 的 downgrade 对真实累积数据的裸崩溃已修复为清晰错误，见 R-09a）。**但**现场实际发起负向连接（而非只读 SQL 文本/TDR 声明）实测：`diyu_app` 角色**可以** `CONNECT` 到 `dify`/`dify_plugin` 数据库（表级 `SELECT` 被正确拒绝，`ERROR: permission denied for table accounts`，未读到任何真实数据），这与 `TECHNICAL_DECISION_RECORD.md` 声称的"REVOKE ALL 阻止连接"不一致——PUBLIC 默认 CONNECT 授权从未被显式撤销。修复动作被权限分类器拦截（触及非本任务独占的共享数据库 `dify`/`dify_plugin`），**未完成**，需要 Founder 或具备权限者手动执行 `REVOKE CONNECT ON DATABASE dify, dify_plugin FROM PUBLIC, diyu_app`，或明确授权后由执行侧重试 | `6955d66`（downgrade 修复）；CONNECT 权限修复未提交，见 `M2_REBASE_ERRATA_001_RECORD.md` §7 |
| M2-AC-14 | **PASS**（真实兼容面已成立，"3 槽"经穷尽检索确认不存在） | (a) 真实存在的旧 5 槽 `V1_TASK_SNAPSHOT_SCHEMA_v0.1.json` 形态快照——已导入并隔离命名空间（`0546f30`/`020bc58`/`f09e292`）；(b) 真实存在的旧 Matrix/Campaign/Content Brief 生产产物（`decision-chain/evidence/*.md`）——本轮用真实 sha256 经既有端点显式导入（`fabffd8`）；(c) Prompt 提及的"3 槽"Schema——穷尽检索仓库全部文件与 `*TASK_SNAPSHOT*` 的 git 全历史，只在 `V1_REBASE_EP00_CURRENT_PREFLIGHT_v0.1.md` §1.4 找到叙述性提及（"三槽旧 Schema 与五槽部署事实不一致"），从未存在过独立可核验的 3 槽 Schema 文件，判定该对象真实不存在，不补造 fixture | `0546f30`, `fabffd8`, 检索证据见 `M2_REBASE_ERRATA_001_RECORD.md` §5 R-05 |
| M2-AC-15 | **PASS** | `tests/test_interface_contracts.py` 钉住 M1/M3/M4 三条边界，现有实现下均未触发修复 | `44f02dd`, `020bc58` |
| M2-AC-16 | **NOT_VERIFIED（本轮由"PASS 但有限制"下修，按 R-08.8 明文要求，不用 API 等价证据改判 PASS）** | 目标环境应用后端真实运行、正向/负向/并发/回归全部通过（69/69，现场重跑）。**Dify 候选画布本身未在本轮代码变更后重新真实运行**：本会话无可用的已认证 Dify 1.16.1 Console 会话（无 refresh_token，未向用户索要/重建密码）；核验到的 `dify-platform-expert` MCP 连接指向 `Dify 1.9.2 @ localhost:8080`，与项目实际使用的 `Dify 1.16.1` 实例不是同一系统，判定不相关，未采用、未用其冒充目标环境证据；仓库内未发现任何已保存的 App API Key 可绕过 Console 会话直接调用。按 Rebase Prompt R-08.8"如果当前无法访问准确目标 Dify，M2-AC-16 = NOT_VERIFIED...不得用 API 等价证据改判 PASS"，本项**明确降级为 NOT_VERIFIED**，不再使用上一版本"PASS 但有限制"的表述 | 上一次真实画布运行（17/17 节点成功）早于本轮全部代码变更，已 STALE，不作为当前证据 |
| M2-AC-17 | **NOT_VERIFIED（预期状态，非缺陷）** | Founder 尚未通过 Dify 画布完成产品/业务验收 | 待 Founder 实测回执 |

## M2-RB 逐条记录（Rebase/Errata 001 自身验收标准）

| criterion_id | 结果 | 说明 |
|---|---|---|
| M2-RB-01 | **PASS** | 同一 task_id、正确哈希、前序 Manifest/Attempt/副作用/分支/数据库状态完整继承（R-01 现场核验：`git fetch` 后 `origin/main`/本地-远程 M2 head 与 Prompt 观察值一致，工作树干净，容器健康） |
| M2-RB-02 | **PASS** | 错误哈希 `e17b...` 登记为无效自证值；全部证据统一用 `4d14eb35...`；原 Prompt 未被原地修改 |
| M2-RB-03 | **PASS** | Stage Baseline v0.2 继续有效约束与后继授权事实已分层记录（`M2_REBASE_ERRATA_001_RECORD.md` §3），未取消授权，未改写历史文件 |
| M2-RB-04 | **PASS** | main 相对 M2 基线的影响已分析（仅 2 个账本登记 commit，无产品/合同/受保护资产变化），无 STALE 证据需要因此重验 |
| M2-RB-05 | **PASS** | `create_version` 并发不再产生无边界裸 500，证据见 M2-AC-12 |
| M2-RB-06 | **PASS** | 旧产物实际兼容面成立（5 槽快照+真实历史生产产物），缺失的 3 槽对象未被补造，证据见 M2-AC-14 |
| M2-RB-07 | **PASS**（本文件本身即该修正的产物） | 不再有"PASS 但证据过期"或"未完成但不在范围"的矛盾陈述——AC-13/AC-16 已如实下修为 NOT_VERIFIED |
| M2-RB-08 | **NOT_VERIFIED（本轮未处理，见下）** | Founder Test Package 的纠正（R-07）尚未在本轮完成，见文末"未完成事项" |
| M2-RB-09 | **NOT_VERIFIED** | 准确 Dify 1.16.1 候选未能以最终代码重新运行；`M2-AC-16` 诚实保持 `NOT_VERIFIED`，未违反本项要求 |
| M2-RB-10 | **NOT_VERIFIED（部分）** | 迁移/回滚/恢复已用目标系统原始证据证明（`M2-AC-13` 迁移半）；但数据库权限的 CONNECT 层面撤销未完成，`M2-AC-13` 整体为 `NOT_VERIFIED` |
| M2-RB-11 | **PASS** | 审查历史与预算已如实分类登记（见"审查与自验记录"），未新增开放式审查，未删除超预算事实 |
| M2-RB-12 | **PASS** | 原 `M2-AC-00`~`17` 重新获得一致、可复算状态，无删除或降低任何标准（`AC-12` 提升为真 PASS，`AC-13`/`AC-16` 如实下修，均为纠正而非放宽） |
| M2-RB-13 | **PASS** | 本轮全部 commit 本地=远程一致（见下"Git 收口"），未触碰 `main` 和无关工作树资产 |
| M2-RB-14 | **PASS** | Founder 尚未完成 Dify 验收前保持非终态，本文件与 `M2_REBASE_ERRATA_001_RECORD.md` 均未声明 `DONE` |

## 结论与当前终态

`M2-AC-13`（数据库 CONNECT 权限）与 `M2-AC-16`（Dify 画布现场运行）当前为 `NOT_VERIFIED`；`M2-RB-08`（Founder Test Package 纠正，见下）与 `M2-RB-09`/`M2-RB-10` 同样为 `NOT_VERIFIED`。按 Rebase Prompt §8.1：

```text
execution_disposition = CONTINUE
task_final_status = null
module_delivery_state = IN_PROGRESS
next_stage_allowed = false
```

**不是** `AWAITING_FOUNDER_DIFY_ACCEPTANCE`——本轮 Rebase 发现的真实问题比预期更多，尚未满足 §8.2 全部前提（`M2-AC-00~16` 全部 CURRENT PASS）。

## 未完成事项（本轮 Active Work Package 尚未全部执行完）

- **R-07（更新 Founder Test Package）**：尚未执行，`FOUNDER_TEST_PACKAGE.md` 中"旧 Demo 兼容没做、不在本次验收范围"等表述与当前 `M2-AC-14` 真实状态冲突，需要下一轮定向修正。
- **R-08（刷新 Dify 候选证据）**：受限于无可用 Dify Console 会话，本轮未完成，`M2-AC-16` 保持 `NOT_VERIFIED`。
- **R-09b（数据库 CONNECT 权限撤销）**：被权限分类器拦截，需要 Founder 决定由谁在什么时机执行。
- **R-11（定向回归）**：本轮新增/修复项已通过 69 项全量测试自证；跨模块（M1/M3/M4 接口、Dify 候选六步）的回归因 R-08 未完成而无法覆盖 Dify 画布这一环。
- **R-12（远程收口）**：本轮全部 commit 已推送，见下。
