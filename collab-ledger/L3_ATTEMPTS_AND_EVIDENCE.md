# L3 · 正式尝试与验收证据

> 规则正文见 [COLLAB_CONTINUITY_PROTOCOL.md](COLLAB_CONTINUITY_PROTOCOL.md)。追加式：只加不改，更正另起一条。
>
> **起算基线 `main @ 6ae78abf5967535bda81392255b8ee3e79e4bcb5`。**
> 基线**之前**的运行只在 §二 建索引，**不追认**为 Formal Attempt，**不重新认证**。

---

## 一、正式尝试（自起算基线起）

> **按 `task_id` 分区。** 并行任务多起来时，各任务的 Attempt 写进 `collab-ledger/tasks/<task_id>.md`，本文件只留索引行。

| Attempt | 所属 task_id | 结果 |
|---|---|---|
| `ATT-001` | `COLLAB-LEDGER-BOOTSTRAP-001` | 见 §ATT-001.2 |

### ATT-001 · `COLLAB-LEDGER-BOOTSTRAP-001` / attempt 1

| 项 | 值 |
|---|---|
| attempt identity | `COLLAB-LEDGER-BOOTSTRAP-001 / attempt-1` |
| 任务与输入引用 | [L1 §T-001.1 Task Contract](L1_TASK_MANIFESTS.md) · [§T-001.2 Run Manifest](L1_TASK_MANIFESTS.md) |
| 起算基线 | `6ae78abf5967535bda81392255b8ee3e79e4bcb5`（本地 == 远端，工作区干净） |
| 实现引用 | `collab-ledger/` 下 6 个 Markdown；`CLAUDE.md` / `PROJECT_INDEX.md` / `README.md` 三处极薄指针 |
| 工作流／模型／Checker | **不适用** —— 纯文档治理任务，交付物不由任何受控模型配置产出（见 Manifest `fixed_configuration_run_reason`）。A2 隔离测试所用执行单元的标识记录在 §ATT-001.3 |
| 环境 | 本机 WSL2；`git 2.x`；`python3`（仅用于哈希与既有校验脚本，**未向仓库新增脚本**） |
| 与上一 Attempt 的实质差异 | **无上一 Attempt** —— `task_entry_mode = NEW_TASK`，全仓库检索无同名 `task_id` 的既有 Manifest／Attempt／Checkpoint |

#### ATT-001.1 冻结与哈希登记

| 项 | 值 |
|---|---|
| `task_contract_hash` | `d5ee949a9dd61af3a40fbf67bb0f185c04ae05d6f8f6008f2c2e9bfcdc22f380` |
| `manifest_hash` | `35a67aa54052ca34e2de726e4d993b4b79e8287d06f42e6f02668bcd0c5fa870` |
| 重算方法 | 取 [L1](L1_TASK_MANIFESTS.md) 中**第 1 个** ```yaml 块的块内字节 → `task_contract_hash`；**第 2 个** ```yaml 块的块内字节 → `manifest_hash`。围栏行本身不计入 |
| tested functional hash | `TESTED_FUNCTIONAL_PLACEHOLDER` |
| closing evidence hash | `CLOSING_EVIDENCE_PLACEHOLDER` |

#### ATT-001.2 验收结果（A1–A9）

`PENDING_AT_FREEZE` —— 本节由**收工时唯一一次 evidence-only 增量**写入。冻结时刻尚未产生，**不留假结论**。

#### ATT-001.3 A2 原始问答（真正隔离的新执行单元）

`PENDING_AT_FREEZE` —— 完整原始问答由收口增量原样写入，**不摘要、不改写**。

#### ATT-001.4 回归与负向测试

| 测试 | 基线结果（改动前实测） | 冻结后结果 |
|---|---|---|
| `python3 tools/v1_demo_verify.py` | **冻结资产不符 0 项；静态检查失败 0 项；单元测试失败 0 项**（exit 0） | `PENDING_AT_FREEZE` |
| 受保护路径零改动（`git diff 6ae78ab..HEAD --stat` 对受保护路径为空） | 基线即自身 | `PENDING_AT_FREEZE` |
| 负向：隔离单元不得据本账本得出「子合同已接受／施工已授权／预检已完成」 | —— | `PENDING_AT_FREEZE` |
| 负向：隔离单元不得把 57 份历史证据当成本基线后的 Formal Attempt | —— | `PENDING_AT_FREEZE` |

#### ATT-001.5 收口

`PENDING_AT_FREEZE` —— 分支、合并提交、远端 `main` HEAD 与 URL 由收口增量写入；对应副作用见 [L5](L5_SIDE_EFFECTS.md)。

---

## 二、历史证据目录（legacy evidence catalog）

> **共 57 份**（`git ls-files` 实测：`decision-chain/evidence` 43 ＋ `content-production/evidence` 14），**全部早于起算基线**。
> 本节**只做定位**：保留各文件**自报**状态、给出原始链接。
> **一律标 `NOT_VERIFIED_BEFORE_BASELINE`** —— 不反向补造 Formal Attempt，不重新认证，原文件一字不动。
> 经过策展的说明性描述在 [PROJECT_INDEX.md](../PROJECT_INDEX.md) 「常用入口」，**本目录不复制**。
>
> 注：`decision-chain/evidence/` 下另有一个 **gitignore 的本地残留目录 `.claude/`**，不属于仓库资产，不计入 57。

### 二.1 文件**自己**显式声明了状态的（9 份，原文摘录）

| 文件 | 原文自报状态（逐字摘录） |
|---|---|
| [CONTENT_PRODUCTION_CS_REFERENCE_PROBE_RUN_001.md](../content-production/evidence/CONTENT_PRODUCTION_CS_REFERENCE_PROBE_RUN_001.md) | `状态 → succeeded` |
| [CONTENT_PRODUCTION_P05R3_RUN.md](../content-production/evidence/CONTENT_PRODUCTION_P05R3_RUN.md) | `结论：SEMANTIC_CHECKER_ACCEPTED_NO_REGRESSION` |
| [CONTENT_PRODUCTION_PRE_CHAIN_FIXTURE_RUN_001.md](../content-production/evidence/CONTENT_PRODUCTION_PRE_CHAIN_FIXTURE_RUN_001.md) | `最终状态 → BLOCKED` |
| [CONTENT_PRODUCTION_PRE_CHAIN_FIXTURE_RUN_002.md](../content-production/evidence/CONTENT_PRODUCTION_PRE_CHAIN_FIXTURE_RUN_002.md) | `状态 → DONE` |
| [CAMPAIGN_QWEN_RUN_001_RAW.md](../decision-chain/evidence/CAMPAIGN_QWEN_RUN_001_RAW.md) | `状态 → SUCCESS` |
| [CONTENT_BRIEF_DEEPSEEK_V4_FLASH_RUN_001_RAW.md](../decision-chain/evidence/CONTENT_BRIEF_DEEPSEEK_V4_FLASH_RUN_001_RAW.md) | `运行状态 → succeeded` |
| [CONTENT_BRIEF_NEGATIVE_PROBES_RUN_001_RAW.md](../decision-chain/evidence/CONTENT_BRIEF_NEGATIVE_PROBES_RUN_001_RAW.md) | `运行状态 → succeeded` |
| [MATRIX_QWEN_RUN_002_RAW.md](../decision-chain/evidence/MATRIX_QWEN_RUN_002_RAW.md) | `状态 → SUCCESS` |
| [MATRIX_QWEN_RUN_003_RAW.md](../decision-chain/evidence/MATRIX_QWEN_RUN_003_RAW.md) | `状态 → SUCCESS` |

**以上 9 条自报状态一律 `NOT_VERIFIED_BEFORE_BASELINE`。** 摘录只表示「原文这么写」，**不表示本账本认定其成立**。

### 二.2 其余 48 份（无显式状态字段，仅索引）

全部 `NOT_VERIFIED_BEFORE_BASELINE`：

[CONTENT_PRODUCTION_FINAL_CHAIN_RUN_001.md](../content-production/evidence/CONTENT_PRODUCTION_FINAL_CHAIN_RUN_001.md) · [CONTENT_PRODUCTION_FINAL_USER_DELIVERY_PACK_v0.1.md](../content-production/evidence/CONTENT_PRODUCTION_FINAL_USER_DELIVERY_PACK_v0.1.md) · [CONTENT_PRODUCTION_FINAL_USER_DELIVERY_PACK_v0.2.md](../content-production/evidence/CONTENT_PRODUCTION_FINAL_USER_DELIVERY_PACK_v0.2.md) · [CONTENT_PRODUCTION_FULL_BRIEF_PRE_CHAIN_RUN_001.md](../content-production/evidence/CONTENT_PRODUCTION_FULL_BRIEF_PRE_CHAIN_RUN_001.md) · [CONTENT_PRODUCTION_FULL_BRIEF_QUALITY_REVIEW_PACK_v0.1.md](../content-production/evidence/CONTENT_PRODUCTION_FULL_BRIEF_QUALITY_REVIEW_PACK_v0.1.md) · [CONTENT_PRODUCTION_FULL_BRIEF_USER_DELIVERY_PACK_v0.1.md](../content-production/evidence/CONTENT_PRODUCTION_FULL_BRIEF_USER_DELIVERY_PACK_v0.1.md) · [CONTENT_PRODUCTION_P05R1_RUN.md](../content-production/evidence/CONTENT_PRODUCTION_P05R1_RUN.md) · [CONTENT_PRODUCTION_P05R2_RUN.md](../content-production/evidence/CONTENT_PRODUCTION_P05R2_RUN.md) · [CONTENT_PRODUCTION_PRE_CHAIN_RUN_001.md](../content-production/evidence/CONTENT_PRODUCTION_PRE_CHAIN_RUN_001.md) · [CONTENT_PRODUCTION_STANDALONE_RUN_001.md](../content-production/evidence/CONTENT_PRODUCTION_STANDALONE_RUN_001.md) · [CAMPAIGN_DEEPSEEK_V4_FLASH_COMPILE_RUN_001_EVAL.md](../decision-chain/evidence/CAMPAIGN_DEEPSEEK_V4_FLASH_COMPILE_RUN_001_EVAL.md) · [CAMPAIGN_DEEPSEEK_V4_FLASH_COMPILE_RUN_001_FINAL.md](../decision-chain/evidence/CAMPAIGN_DEEPSEEK_V4_FLASH_COMPILE_RUN_001_FINAL.md) · [CAMPAIGN_DEEPSEEK_V4_FLASH_COMPILE_RUN_001_RAW.md](../decision-chain/evidence/CAMPAIGN_DEEPSEEK_V4_FLASH_COMPILE_RUN_001_RAW.md) · [CAMPAIGN_DEEPSEEK_V4_FLASH_RUN_001_RAW.md](../decision-chain/evidence/CAMPAIGN_DEEPSEEK_V4_FLASH_RUN_001_RAW.md) · [CAMPAIGN_DEEPSEEK_V4_FLASH_RUN_002_RAW.md](../decision-chain/evidence/CAMPAIGN_DEEPSEEK_V4_FLASH_RUN_002_RAW.md) · [CAMPAIGN_DEEPSEEK_V4_PRO_RUN_001_RAW.md](../decision-chain/evidence/CAMPAIGN_DEEPSEEK_V4_PRO_RUN_001_RAW.md) · [CAMPAIGN_DEEPSEEK_V4_PRO_RUN_002_RAW.md](../decision-chain/evidence/CAMPAIGN_DEEPSEEK_V4_PRO_RUN_002_RAW.md) · [CAMPAIGN_DIFY_RUN_MANIFEST_v0.1.md](../decision-chain/evidence/CAMPAIGN_DIFY_RUN_MANIFEST_v0.1.md) · [CAMPAIGN_QWEN37PLUS_RUN_001_RAW.md](../decision-chain/evidence/CAMPAIGN_QWEN37PLUS_RUN_001_RAW.md) · [CAMPAIGN_QWEN38MAX_RUN_001_RAW.md](../decision-chain/evidence/CAMPAIGN_QWEN38MAX_RUN_001_RAW.md) · [CONTENT_BRIEF_DEEPSEEK_V4_FLASH_RUN_001_EVAL.md](../decision-chain/evidence/CONTENT_BRIEF_DEEPSEEK_V4_FLASH_RUN_001_EVAL.md) · [CONTENT_BRIEF_DEEPSEEK_V4_FLASH_RUN_001_FINAL.md](../decision-chain/evidence/CONTENT_BRIEF_DEEPSEEK_V4_FLASH_RUN_001_FINAL.md) · [CONTENT_BRIEF_DIFY_RUN_MANIFEST_v0.1.md](../decision-chain/evidence/CONTENT_BRIEF_DIFY_RUN_MANIFEST_v0.1.md) · [MATRIX_QWEN_RUN_001_RAW.md](../decision-chain/evidence/MATRIX_QWEN_RUN_001_RAW.md) · [NEGATIVE_PROBE_INSUFFICIENT_FIXTURE_002_RAW.md](../decision-chain/evidence/NEGATIVE_PROBE_INSUFFICIENT_FIXTURE_002_RAW.md) · [TEST_CAMPAIGN_NOSKILL.yml](../decision-chain/evidence/TEST_CAMPAIGN_NOSKILL.yml) · [TEST_CAMPAIGN_QWEN38MAX.yml](../decision-chain/evidence/TEST_CAMPAIGN_QWEN38MAX.yml) · [TEST_CONTENT_BRIEF_NOSKILL.yml](../decision-chain/evidence/TEST_CONTENT_BRIEF_NOSKILL.yml) · [TEST_CONTENT_BRIEF_QWEN38MAX.yml](../decision-chain/evidence/TEST_CONTENT_BRIEF_QWEN38MAX.yml) · [TEST_MATRIX_NOSKILL.yml](../decision-chain/evidence/TEST_MATRIX_NOSKILL.yml) · [TEST_MATRIX_QWEN38MAX.yml](../decision-chain/evidence/TEST_MATRIX_QWEN38MAX.yml) · [V1_DIALOGUE_ORCHESTRATION_REPAIR_001_EVIDENCE.md](../decision-chain/evidence/V1_DIALOGUE_ORCHESTRATION_REPAIR_001_EVIDENCE.md) · [V1_DIFY_RUN_MANIFEST_v0.1.md](../decision-chain/evidence/V1_DIFY_RUN_MANIFEST_v0.1.md) · [V1_E2E_CASES_v0.1.json](../decision-chain/evidence/V1_E2E_CASES_v0.1.json) · [V1_E2E_QUALITY_VALIDATION_MANIFEST_v0.1.md](../decision-chain/evidence/V1_E2E_QUALITY_VALIDATION_MANIFEST_v0.1.md) · [V1_E2E_QUALITY_VALIDATION_PLAN_v0.1.md](../decision-chain/evidence/V1_E2E_QUALITY_VALIDATION_PLAN_v0.1.md) · [V1_E2E_RUN_002_EVAL.md](../decision-chain/evidence/V1_E2E_RUN_002_EVAL.md) · [V1_E2E_RUN_002_RAW.md](../decision-chain/evidence/V1_E2E_RUN_002_RAW.md) · [V1_E2E_RUN_002_TRACE.md](../decision-chain/evidence/V1_E2E_RUN_002_TRACE.md) · [V1_QUALITY_BLIND_MAPPING_v0.1.json](../decision-chain/evidence/V1_QUALITY_BLIND_MAPPING_v0.1.json) · [V1_QUALITY_BLIND_REVIEW_PACK_v0.1.md](../decision-chain/evidence/V1_QUALITY_BLIND_REVIEW_PACK_v0.1.md) · [V1_QUALITY_COMPARISON_INPUTS_v0.1.md](../decision-chain/evidence/V1_QUALITY_COMPARISON_INPUTS_v0.1.md) · [V1_QUALITY_COMPARISON_RUN_001_RAW.md](../decision-chain/evidence/V1_QUALITY_COMPARISON_RUN_001_RAW.md) · [V1_QUALITY_FOUNDER_REVIEW_v0.1.md](../decision-chain/evidence/V1_QUALITY_FOUNDER_REVIEW_v0.1.md) · [V1_RUN_001_EVAL.md](../decision-chain/evidence/V1_RUN_001_EVAL.md) · [V1_RUN_001_FINAL.md](../decision-chain/evidence/V1_RUN_001_FINAL.md) · [V1_RUN_001_RAW.md](../decision-chain/evidence/V1_RUN_001_RAW.md) · [V1_RUN_001_TRACE.md](../decision-chain/evidence/V1_RUN_001_TRACE.md)

---

## 三、本基线之后的其他任务

`NONE_VERIFIED_SINCE_BASELINE` —— 除 `ATT-001` 外，自 `6ae78ab` 起没有第二个任务产生过 Formal Attempt。
