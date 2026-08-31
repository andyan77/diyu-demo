# UAPP S5 Final Two-Blocker Failure Triage 002 — Environment Reinitialized

`task_id: DIYU-V1-UNIFIED-DIFY-APPLICATION-001`

`confirmed_origin: INPUT_ENVIRONMENT_OR_TOOL`

## observed_failure

ERRATA 001 冻结并推送后，P1 重新读取运行环境时，当前 Dify PostgreSQL 不再包含冻结候选：
`apps=0`、`workflows=0`、`workflow_runs=0`、`tenants=0`。容器日志明确记录该 PostgreSQL
集群在 `2026-08-31T04:08:50Z` 执行了初始化。原 `diyu_business` 数据库不存在，
`diyu-m2-app` 同时已退出，因此 `1568/117` 保护计数当前不可观察。

## frozen_target

- UAPP graph md5 `6ac5a45f3953683339f4ea77ebcc00c6`；
- M2 非测试 publish/feedback `1568/117`；
- 活动 workflow `0`；
- 在该准确候选、Provider、输入、Checker 和测试数据基线上完成 P1→P5。

## candidate_sources

- `INPUT_ENVIRONMENT_OR_TOOL`：已确认；
- `SYSTEM_UNDER_TEST`：无证据，本次不得填写；
- `INSUFFICIENT_EVIDENCE`：不适用于“当前库为空”这一确定性事实，但适用于数据目录为何被重建。

## confirmed_origin

`INPUT_ENVIRONMENT_OR_TOOL`。Dify 数据库为空及 M2 数据库缺失发生在候选代码或正式模型调用之前；
不能归因给 EQUIV、写回接缝、Runner、Checker 或专业能力。

## evidence

- `docker inspect docker-db_postgres-1`：StartedAt
  `2026-08-31T04:08:48.974659525Z`，绑定
  `/home/faye/dify/docker/volumes/db/data`；
- PostgreSQL 日志：`PostgreSQL init process complete; ready for start up`；
- Dify SQL：`apps=0`、`workflows=0`、`workflow_runs=0`、`tenants=0`；
- PostgreSQL catalog：`diyu_business_exists=0`；
- `docker inspect diyu-m2-app`：`exited`，exit `255`，结束于
  `2026-08-31T04:08:45.714547332Z`；
- Docker 中另两套 PostgreSQL volume 只包含 `scratch` 或 FCVSS 数据，不是冻结 Dify/M2 真源；
- 原始机器证据：
  `unified-app/evidence/stages/s5_final_two_blocker_rebase_v1_0/P1_ENVIRONMENT_REINITIALIZATION_EVIDENCE_v1.0.json`。

## mutation_target

`NONE`。没有准确备份时，禁止直接构造 Dify/M2 数据库、改 app/workflow/provider 身份或写入
1568/117 占位数据来制造基线。当前候选实现、Runner、Checker、Fixture 和冻结 Gate 均不修改。

## protected_targets

- M1/M2/M3、Hop、Seam、六项专业能力及 PP；
- 历史 RAW、FAIL 与 14 项 CURRENT 证据；
- 非测试数据与 schema；
- main/origin-main；
- 冻结输入、判据和 10/60 预算。

## next_reverification

先从可验证备份恢复 **准确的** pre-restart Dify 与 M2 volumes。恢复后依次重算：

1. UAPP/M3/Hop/Seam/PP/provider 图身份；
2. Dify active workflow 数；
3. M2 schema 与 `1568/117`；
4. 19 项证据绑定和测试 workspace 前状态；
5. P1 全链零模型正负控制。

任何身份无法精确恢复时，不得把新建环境视作原候选继续正式取证。

## cost_and_side_effects

- 本 REBASE 顶层正式运行：`0/10`；
- DeepSeek：`0/60`；
- 重试、内部重放、重复采样、A/B、Reviewer：`0`；
- 检测后 Dify/M2 写入、真实发布：`0`。

