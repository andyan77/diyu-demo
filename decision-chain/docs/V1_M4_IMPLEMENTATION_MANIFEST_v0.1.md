# V1 M4 Run Manifest v0.1

> 本文件是 `V1-M4-CAPABILITY-SEAMS-RUNTIME-INTEGRATION-001` 的运行清单（Run Manifest）。
> 它记录**首次写入前**的现场刷新结果、合同绑定、保护资产、触碰清单、证据时窗与回滚锚点。
> 它是索引，不是状态真源；状态见 §7 与 `V1_M4_ACCEPTANCE_INDEX_v0.1.md`。

---

## 1. 任务与合同绑定

```yaml
task_id: "V1-M4-CAPABILITY-SEAMS-RUNTIME-INTEGRATION-001"
task_entry_mode: "REBASE_TASK"
task_prompt_version: "v1.3"
task_prompt_file: "M4_ENGINEERING_EXECUTION_PROMPT_v1.3.md"
task_prompt_file_sha256: "653b9bcc00aff8a0f7bae272b58639497fab622177a6aaf67e5eb619ca84e9ce"
task_contract_hash_declared: "b3ceabcbe9bcd82dae2fae84161dce0f0aadd96e395a8d6fa06a3355138331c6"
task_contract_hash_recomputed: "b3ceabcbe9bcd82dae2fae84161dce0f0aadd96e395a8d6fa06a3355138331c6"
task_contract_hash_match: true
hash_scope_verified: "M4_ENGINEERING_EXECUTION_PROMPT_v1.3.md 第 95-215 行（BEGIN/END 标记行之间，含末行换行），8391 bytes"
governance_protocol_ref: "UNIVERSAL-BOUNDED-EVIDENCE-AI-COLLABORATION v0.3.1 revision 2"
governance_authority: "RULESIDE-2026-08-25-005"
execution_protocol_ref: "DIYU-BOUNDED-EXECUTION-OWNER-PROTOCOL v1.3"
resume_checkpoint_ref: "NONE_ENGINEERING_NEVER_STARTED"
predecessor_engineering_manifest_ref: "NONE"
activation_event: "Founder 于本会话注入准确 v1.3 全文并明确表达『沿用原 task_id 启动 M4 全部 P0 工程施工、严格持续执行至规定终态、不重写 Prompt、不启动 M5』"
activation_verified_by_executor: true
```

**Rebase 依据复核**：`task_id`、M4 模块责任、核心 P0 未变；治理权威（-005/rev2）、Git 起算点与验收充分性发生变化；无任何 M4 工程 Checkpoint / Formal Attempt / Dify 副作用存在，故不是 `RECOVERY_TASK`，也不得伪装成 `NEW_TASK`。

---

## 2. 首次写入前的现场刷新（AS_OF 2026-08-26，执行端自盘，零子 Agent）

### 2.1 Git

| 项 | 刷新值 | 时窗 |
|---|---|---|
| 远端 `origin/HEAD` 符号引用 | `ref: refs/heads/main`（`git ls-remote --symref origin HEAD` 现场返回） | 15 min |
| 远端 `refs/heads/main` | `ca5281aee70943f02cf5b3be50c8c139ebfd15d4` | 15 min |
| 本地 `main` / `origin/main` | `ca5281aee70943f02cf5b3be50c8c139ebfd15d4`（三者一致） | 15 min |
| 规划观察 commit 对照 | 与 Prompt §1.2 `planning_observed_commit` **一致**，无前移 | — |
| 远端是否已存在 M4 任务分支 | **否**（`git ls-remote origin 'refs/heads/codex/v1-m4*'` 返回空） | 15 min |

`actual_baseline = ca5281aee70943f02cf5b3be50c8c139ebfd15d4`

### 2.2 专用 worktree

```yaml
worktree_path: "/home/faye/diyu-demo-worktrees/m4-capability-seams-runtime-integration-v1"
branch: "codex/v1-m4-capability-seams-runtime-integration-001"
created_from: "ca5281aee70943f02cf5b3be50c8c139ebfd15d4"
initial_status: "clean（git status --short 空）"
shared_root_used_for_construction: false
```

共享 root `/home/faye/diyu-demo` 存在 14 项未提交/未跟踪资产（其他模块 Prompt、规划文件、`m3-account-content-operator-semantic-v1.0/`、`route1.json`、`route2.json` 等）。**全部受保护，本任务不吸收、不提交、不改写。**

### 2.3 六份源 Skill 现场复算（保护基线）

| 能力 | 源文件 | 现场 SHA-256 | 与 Prompt §4.1 绑定 |
|---|---|---|---|
| Matrix Architect | `decision-chain/skills/Matrix_Architect_v0.1.2.md` | `7a6afa3cf1a7b2e4793bd2b3dde6edddf20f75a5b8ed9f7aeb6a456d06acd838` | 一致 |
| Campaign Orchestrator | `decision-chain/skills/Campaign_Orchestrator_v0.1.md` | `c7ef284e40e7c4cd0d4081632fca7df17bd1a80fbd3f3b5267be4aea1040a0fb` | 一致 |
| Content Brief Architect | `decision-chain/skills/Content_Brief_Architect_v0.1.md` | `a0268a211a235b5b4df5e517f085db1f3b4948ae5add3346f2c15a426b63395f` | 一致 |
| Creative Script | `content-production/skills/writing-creative-scripts/SKILL.md` | `d0f78a480f58d494a29d3a34e35106ba0ff48719052361748ed513c721fc7b6a` | 一致 |
| Production Director | `content-production/skills/directing-content-production/SKILL.md` | `87acc4a082500190f3b4454c088d95c6a60dce4062e5be120bb6f5b3adfdae3c` | 一致 |
| Publishing & Packaging | `content-production/skills/packaging-content-for-release/SKILL.md` | `0c91a8efb0583523af8abc80dd1238b24d15791c1d0b0cef425eade6b277cc07` | 一致 |

**六 Skill 刷新差异 = 零。** 依 Prompt §10.1，继续作为保护基线复用，不重写 Skill、不重建 Workflow、不重跑全部历史测试。

### 2.4 仓库 Workflow DSL 现场 SHA-256（新增绑定，Prompt §4.1 未给出该列）

| 文件 | 现场 SHA-256 |
|---|---|
| `decision-chain/workflows/DIYU_DEMO_V1_TOOL_MATRIX_v0.1.yml` | `dbc6b400aa1d7d7d1f43a374ab9cc1e7cb00eb5b7834576c2e38639453e451cc` |
| `decision-chain/workflows/DIYU_DEMO_V1_TOOL_CAMPAIGN_v0.1.yml` | `6468223b40c1d56f8c192e5f2548371715c1522d60ca3379eb0e7c6a443b7c89` |
| `decision-chain/workflows/DIYU_DEMO_V1_TOOL_CONTENT_BRIEF_v0.1.yml` | `b703a0cb690855ae76bac9483208a70f06cf3d96b24171e8e274397b31749265` |
| `content-production/workflows/DIYU_DEMO_CREATIVE_SCRIPT_V0_1.yml` | `ca470d1e02e2c3b43de46966c50eed0b6d53156d76c7f79672287263e2d821c5` |
| `content-production/workflows/DIYU_DEMO_PRODUCTION_DIRECTOR_V0_1.yml` | `04ea73191557a700afbabb47750cdf7c325871aa57955a886ae8153b35adf6a3` |
| `content-production/workflows/DIYU_DEMO_PUBLISHING_PACKAGING_V0_1.yml` | `47c548af14c5890ad1ca530b788b515f7c5197f535a614f79acf5ec3424f6b1c` |
| `content-production/workflows/DIYU_DEMO_CONTENT_PRODUCTION_PRE_CHAIN_STAGE1_V0_1.yml` | `ac312b49c61361a1276c50bc72b7e106183973014c7e81326c86b2a69c0cc30e` |
| `content-production/workflows/DIYU_DEMO_CONTENT_PRODUCTION_PUBLISHING_STAGE2_V0_1.yml` | `07cc032412ac4491bb3ed1a95ce094e380d41798ff272237fc5965f4a2ff6bfe` |

### 2.5 本机 Dify 1.16.1 现场

```yaml
health:
  containers_up: true            # docker-nginx-1 / api-1(healthy) / worker-1 / db_postgres-1(healthy) / redis-1(healthy) / plugin_daemon-1 ...
  console_api_http: 200          # GET http://127.0.0.1/console/api/setup
  as_of_window: "5 min"
apps_total: 28
protected_apps_present: 9        # Prompt §4.2 九个 app_id 现场逐一命中
m4_successor_apps_present: 0     # 名称含 "M4 v1.3 TEST" 的对象：当前为 0
```

九个受保护应用的**当前已发布 workflow 绑定**（写前锚点，用于回滚与 N-20 复验）：

| 应用 | app_id | published workflow_id | 发布时间 | graph md5 |
|---|---|---|---|---|
| V1 Main Chatflow v0.1 | `310ddfcf-e0fb-4211-af98-3d101725e07a` | `055b7bbe-172f-4456-8459-951ae3e14ce7` | 2026-08-24 00:19:40 | `8def6c4f436ad989557992c59d029958` |
| Tool Matrix Architect v0.1 | `f8d2be15-2f71-4765-a482-fb62c0e1f3a0` | `612c8080-a952-4925-b17b-73205f89cdd8` | 2026-08-21 07:04:04 | `698882cb607c4e9a5837a1f7fbeee6d9` |
| Tool Campaign Orchestrator v0.1 | `a0d92232-0afe-4b77-abb4-5356fd04bc7b` | `1f5505a6-c9e9-480a-9979-0435fa4af229` | 2026-08-21 07:04:04 | `d58979e4e03cdb4e966510cfa73d78f7` |
| Tool Content Brief Architect v0.1 | `eadf8867-6e00-48b8-b3b9-2cb8b89d8834` | `8248fc80-08ff-4852-9812-598b263ef728` | 2026-08-21 07:04:04 | `3899602de5df3821fe1efc64016fd038` |
| Creative Script v0.1 | `13ba9e70-2193-4217-9ac8-32bfda2a7822` | `18668db6-8faa-4151-8cbd-aab74e4ed15c` | 2026-08-23 14:21:26 | `7aedc2221e83b7e8cc24b1e42de3811d` |
| Production Director v0.1 | `4433b747-4216-44d6-b8bb-e6664d3cf4fb` | `9342e31b-c342-466a-8604-ec076cd6e6d5` | 2026-08-23 14:21:26 | `f10feb365a209196f20ca8adb7b68907` |
| Publishing Packaging v0.1 | `fa71a06d-2b0d-4d09-b580-ca8e2db5f0a6` | `dcf428ee-8469-4e45-adf6-2016a1824fab` | 2026-08-23 19:01:29 | `053a5e4ed6a9c9b1970d7c206ce65dd7` |
| PRE Chain Stage 1 v0.1 | `4eac6ab7-9d81-4af0-accf-740e3157f5ea` | `762c23cd-226d-45f2-8126-009132565010` | 2026-08-23 14:21:26 | `cf8b4de9e33036d24059c8bfa8515b7b` |
| Publishing Stage 2 v0.1 | `2c188608-0559-4ef4-8c76-18b4f48c3cd9` | `993afbd8-e5f7-418d-827c-394389a13efd` | 2026-08-24 01:45:38 | `263efc104513463a1988c0698dd995ed` |

上表既是**保护资产完整性基线**（收口时逐行复算，任一变化即 AC-01/AC-16 FAIL），也是 N-20（子应用发布后父 provider 指旧版）的对照锚点。

**取证方式**：`docker exec docker-db_postgres-1 psql -U postgres -d dify -tAc "SELECT ..."`，**只读 SELECT**，无 UPDATE/INSERT/DELETE。属 Prompt §2 `authorized_scope.read` 明确授权的
「本机 Docker Dify 1.16.1 当前应用、草稿、发布态、provider、运行记录与健康状态的只读侦察」。**不通过 SQL 修改 Dify**（§13 硬禁）。

---

## 3. Prompt §4.3 漂移事实的现场刷新结果

Prompt §4.3 全部标 `STALE_UNTIL_EXECUTION_REFRESH`。本节是刷新后的结论，**取代**该节的历史观察值。

| §4.3 条目 | 刷新结论 | 现场证据 |
|---|---|---|
| 旧主 Chatflow 以 `requested_skill` 六值枚举 + 固定分支 | **CONFIRMED，且需更正指针**：当前**已发布**主 Chatflow 不是仓库 `DIYU_DEMO_V1_MAIN_CHATFLOW_v0.1.yml`（39 节点），而是与 `DIYU_DEMO_V1_FULL_CHAIN_CHATFLOW_v0.2.yml` **逐字段零漂移**的 56 节点版本 | 56/56 节点同名；`prompt_template`/`code`/`template`/`model` 四类字段逐节点比对 drift=0 |
| 枚举实际取值 | `MATRIX｜CAMPAIGN｜CONTENT_BRIEF｜PRODUCTION_STAGE1｜PUBLISHING_STAGE2｜NONE`（5 能力 + NONE = 六值），`v1_route` 固定五分支 | `v1_shadow.prompt_template` system 段；`v1_route.cases` |
| 七入口现状 | **ENTRY-04（直接创意锦标赛）、ENTRY-05（直接 CS）、ENTRY-06（直接 PD）、ENTRY-07（直接 PP）在当前 Runtime 均无独立入口**：CS+PD 被物理压成 `PRODUCTION_STAGE1`，PP 被压成 `PUBLISHING_STAGE2` | 同上 |
| Matrix 资料不足全局停止 | **CONFIRMED**：`Matrix_Architect_v0.1.2.md` §0「输出后立即停止。不得附加建议、询问、结束语…」 | 源 Skill 正文 |
| Campaign 被压成 `COMPILE_CONFIRMED_DECISIONS` | **CONFIRMED**（兼容模式合法，但当前是唯一产品身份） | 共享合同二 §三；Campaign Tool DSL |
| Content Brief 把 Campaign 当唯一上游 | **CONFIRMED**：`Content_Brief_Architect_v0.1.md` §0/§2/§3.2 硬要求「已被接受的 Campaign 决策包」 | 源 Skill 正文 |
| CS 已含 CS-1，固定三方向 | **CONFIRMED**：CS-1「生成 **3 个高差异方向**」为硬编码数量 | 源 Skill CS-1 |
| CS/PD 可独立调用但 Stage 1 物理融合 | **CONFIRMED**：Stage1 DSL 内 `cs_tool → cs_extract → gate_cs → cs_handoff → pd_tool` 串死 | Stage1 DSL 19 节点 |
| PP 硬要求 `cs_final + pd_final` | **CONFIRMED**：PP Workflow start 变量 `cs_final`/`pd_final` 均 `required: true` | PP DSL start 节点 |
| live `returns_adapter` 领先仓库 DSL | **CONFIRMED**：PP 已发布 `returns_adapter.code` 11092 字符 vs 仓库 10833 字符，**内容不同** | live/repo 逐字段比对 |
| 自报 hash 含 stale 常量 | 待 Formal Attempt 时逐条以实际运行字节复核（N-19） | — |
| CS 仓库/草稿 `reasoning_effort=max`，发布 Runtime `low` | **CONFIRMED**：仓库 DSL `max`；已发布 Runtime `low`。**PD/PP 仓库与发布一致，均为 `low`** | live/repo `model.completion_params` 比对 |
| 六 Skill 主 Runtime `deepseek-v4-flash` / `top_p=0.8`；PP 后事实核验 `qwen3.8-max` | **CONFIRMED**：六个 Skill LLM 节点全部 `langgenius/deepseek/deepseek` + `deepseek-v4-flash` + `top_p=0.8`；Stage2 `semantic_check` = `tongyi/qwen3.8-max` + `enable_search:false` + `top_p=0.8` | live graph |

### 3.1 刷新新增发现（Prompt §4.3 未登记）

| ID | 发现 | 影响 |
|---|---|---|
| `M4-DRIFT-N1` | 仓库同时存在 `DIYU_DEMO_V1_MAIN_CHATFLOW_v0.1.yml`（39 节点）与 `DIYU_DEMO_V1_FULL_CHAIN_CHATFLOW_v0.2.yml`（56 节点）；**已发布 Runtime 等于后者**。以 v0.1 为「当前主 Chatflow」的任何判断都是过期指针 | M4 一切「当前 Runtime 行为」判断必须绑定 v0.2/live，不得引用 v0.1 |
| `M4-DRIFT-N2` | 主 Chatflow live 与仓库 v0.1 之间有 6 处字段级漂移（`v1_state.code` 25214→37799、`v1_shadow.prompt_template`、`v1_chat_llm.prompt_template`、`fin_*.code` ×3、`v1_toolfail*`），全部由 v0.2 承接 | 不构成 FAIL；证明 v0.1 是历史快照 |
| `M4-DRIFT-N3` | PP 的 `returns_adapter` 是**唯一**仍存在 live-领先-仓库漂移的节点 | M4 后继 PP 必须先理解并保留 live 版语义，不得用仓库旧版覆盖（Prompt §4.3 明确要求） |

---

## 4. 受保护资产与触碰清单

### 4.1 受保护（本任务零改动）

- 六份源 Skill、九个旧 Dify 应用、现有已发布 DSL、`content-production/references/`（及三份 Skill 各自 `references/` 副本）
- 现行合同、共享前言、两份 EP-00、Runtime 合同、Golden、夹具、历史原始证据
- M1/M2/M3 合同、职责、在途分支、候选文件、Dify 应用、容器、数据与证据
- 共享 root 的未提交改动与未跟踪文件；`main` 与其他任务分支历史
- 用户资料、凭据、API Key、数据库数据、生产环境、外部内容平台

### 4.2 本任务允许触碰（白名单，全部在专用 worktree 内）

| 路径 | 动作 |
|---|---|
| `decision-chain/skills/*_v0.2_M4.md` | 新增（清晰后继版本，不覆盖旧版） |
| `content-production/skills/*-m4/SKILL.md` | 新增 |
| `decision-chain/workflows/DIYU_M4_*.yml` | 新增 |
| `content-production/workflows/DIYU_M4_*.yml` | 新增 |
| `decision-chain/docs/V1_M4_*.md` | 新增 |
| `content-production/docs/V1_M4_*.md` | 新增 |
| `decision-chain/fixtures/m4/**` | 新增 |
| `decision-chain/evidence/m4/**`、`content-production/evidence/m4/**` | 新增原始证据 |
| `collab-ledger/tasks/V1-M4-CAPABILITY-SEAMS-RUNTIME-INTEGRATION-001.md` | 新增 |
| `collab-ledger/L1/L2/L3/L5` | 最小追加/当前指针 |
| 本机 Dify 名称含 `M4 v1.3 TEST` 的后继对象 | 创建/更新/发布 |

### 4.3 明确不触碰的「可见但禁读用途」资产

`m3-account-content-operator-semantic-v1.0/`（共享 root 未跟踪目录）与 M3 任务 worktree 的设计资产：
**其存在被登记为保护对象；其文件、节点、Schema、输出结构不被读取用于推断 M3 物理实现**（N-08）。
M4 只使用 Phase 0 共享前言 §四 CAP-03 与共享合同二冻结的 **Content Task 业务语义**，以及本任务自建的冻结业务夹具。

> 例外披露：本任务从 M3 worktree 读取过**一条基础设施记录**（Founder 已解除 Dify Console 凭据并写入该 worktree 的 `.env`，gitignored）。该读取只涉及目标环境访问方式，不涉及 M3 的运营判断、文件结构、Schema 或输出，不构成 N-08 违规。凭据本身未写入任何文件、commit 或账本。

---

## 5. 证据时窗

| 类别 | 时窗 | 过期处置 |
|---|---|---|
| Git / 远端 | 15 min | `STALE`，定向刷新 |
| Dify 健康与绑定 | 5 min | `STALE` |
| 模型 / 参数 / provider | 每个 Formal Attempt | 每次 Attempt 前重绑 |
| Skill / Workflow / reference | 当前 worktree 版本 | 以 worktree 字节为准 |
| 授权与副作用 | 单次动作 | 不跨动作复用 |
| 动态附件 | 按自身 `as_of` | 过期不升级主张 |

`STALE` 是旗标不是结果；过期不等于自动 FAIL。

---

## 6. 回滚锚点

| 对象 | 回滚方式 |
|---|---|
| Git | 任务分支独立；`main` 与其他分支不被触碰。任何回退在本分支内 revert，不 force push、不改写已推送历史 |
| Dify 后继应用 | 每个 M4 后继对象写前登记 `object / content_hash / idempotency_key / rollback_anchor`，写后由目标系统确认。九个保护应用的 published `workflow_id` + `graph md5`（§2.5 表）为不可变对照锚点 |
| `STARTED/UNKNOWN` 外部动作 | 先查目标系统副作用，不盲重放（N-24） |

---

## 7. 当前进度指针

```text
M4_CONTRACT_BOUND              = TRUE   (hash 复算一致)
M4_BASELINE_REFRESHED          = TRUE   (ca5281a, 六 Skill 零漂移)
M4_WORKTREE_ESTABLISHED        = TRUE
M4_DRIFT_REFRESH               = COMPLETED (§3, 含 3 项新增发现)
M4_CONSTRUCTION                = IN_PROGRESS
M4_ENGINEERING_PASS            = NONE
DIYU_V1_SINGLE_ACCOUNT_VERTICAL_SLICE = NOT_DONE
```

唯一下一动作见 `V1_M4_ACCEPTANCE_INDEX_v0.1.md` 末节。
