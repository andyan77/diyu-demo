# 任务分区账本 · `DIYU-V1-M5-UNIFIED-INTEGRATION-FINAL-ACCEPTANCE-001`

> 规则正文见 [../COLLAB_CONTINUITY_PROTOCOL.md](../COLLAB_CONTINUITY_PROTOCOL.md)。本文件是 canonical §一
> 所说的**任务分区**：五本账里只应留一行定位，任务的高频运行状态写在这里。
>
> 与 M3 分区同理：本任务分支基于刷新后的 `origin/main`，分支内五本账为该基线副本；
> 本任务只新增这一份分区文件（纯新增、零冲突），五本账的一行定位留待 Node 6 收口合并时
> 对着当时的当前版本补写。

---

## L1 · 合同与边界（历史留痕，只加不改）

| 项 | 值 |
|---|---|
| `task_id` | `DIYU-V1-M5-UNIFIED-INTEGRATION-FINAL-ACCEPTANCE-001` |
| `entry_mode` / `task_type` / `risk_level` | `NEW_TASK` / `MIXED` / `HIGH` |
| Root Execution Prompt | `M5_ROOT_EXECUTION_PROMPT_v1.0.md`，`sha256 = a18d3076146402afd77d7c8f11e43d48361270eb5f35671118a207aee002e75d`（**现场复算通过**） |
| Task Contract | `M5_ENGINEERING_TASK_CONTRACT_v1.0.yaml`，`sha256 = e2dc0a4cbe09d32e268a516fdbe45d18aa0050b6416402109a8dc256678aaa43`（**现场复算通过**） |
| Prestart Run Manifest | `M5_PRESTART_RUN_MANIFEST_v1.0.yaml`，`sha256 = 92eec1446040b27ffd110e66e1bcda61235b91f894709742577551a7f196f676`（自身不自引用，由执行侧复算并绑定） |
| Fixture / 19D Index | `M5_ACCEPTANCE_FIXTURE_AND_19D_COVERAGE_INDEX_v1.0.yaml`，`sha256 = dba03d4839c5d14ea19bbee7ac7d650d77e8f10deef9ae03616d0978cd89ca7d`（**现场复算通过**） |
| 授权事件 | Founder 于 2026-08-27 表达「我以授权启动M5」；准确四文件包被注入工程执行终端且 SHA-256 全部校验通过 —— **该接收事件即本 task_id 的工程激活事件**（Root Prompt §1.3、Task Contract `authorization.activation_event`） |
| 激活时间（UTC） | `2026-08-28T04:56:51Z` |
| 治理协议 | 内核 `UNIVERSAL-BOUNDED-EVIDENCE-AI-COLLABORATION v0.3.1 revision 2`；执行侧 `DIYU-BOUNDED-EXECUTION-OWNER-PROTOCOL v1.3`；权威事件 `RULESIDE-2026-08-25-005` |
| 起算基线 | 刷新后的 `origin/main @ f6eb86c076c47bd9f7c9323caac6c0ba1fc5098e` |
| 任务分支 | `codex/v1-m5-unified-integration-final-acceptance-001` |
| worktree | `/home/faye/diyu-demo-worktrees/m5-unified-integration-final-acceptance-v1` |
| 允许变化面 | 从刷新 main 形成 M5 集成候选（语义整合 M4）｜最小接口修复｜Dify M5 测试候选（可逆）｜任务域测试工作区数据｜验收夹具、证据、回归与本分区账本｜任务分支提交与常规推送｜**条件化**的 main 合并与常规远端推送 |
| 受保护资产 | M1–M4 已接受的产品职责／历史证据／失败／限制／Founder disposition／原 task_id｜六份专业 Skill 的专业价值、源文件与已发布应用｜`main`、其他任务分支、共享工作区未提交/未跟踪文件、非测试数据库数据、凭据、真实内容平台｜M2 历史窄技术未达项不得被追溯涂绿 |
| 验收口径 | `M5-AC-00…10`（Task Contract `acceptance_contract`），`done_formula` = 全部 PASS/CURRENT AND Founder 产品验收接受 AND 无适用 P0 硬门失败 AND Git/远端收口完成 |
| 允许终态 | `INVALID` / `DONE` / `BLOCKED` / `FAILED`（**不得用 `PARTIAL` 作为 M5 终态**） |
| `main_merge_and_push` | `CONDITIONALLY_AUTHORIZED` —— 仅在全部技术硬门 PASS 且 Founder 产品接受之后 |
| `force_push` / `remote_branch_delete` | `PROHIBITED` |
| `real_external_publish` | `NOT_AUTHORIZED`（测试/模拟发布记录已授权） |

---

## L2 · 当前状态与下一动作（当前投影，可替换）

| 项 | 值 |
|---|---|
| 进度 | `IN_PROGRESS` |
| 当前节点 | **NODE-5 已完成**（冻结后正式运行全套跑完，留出已解封判定）；NODE-6 待 Founder 输入 |
| 候选 | `86af9ecd5a313ff55aff1874d29eb342299d65ff`，Candidate Run Manifest 冻结于 `2026-08-28T09:14:06Z` |
| 终态 | **未判定，留空**。`done_formula` 不成立 |
| 下一个可立即执行的动作 | **无。执行侧到此为止**，等 Founder 完成三件事（见下） |

### 正式验收结果（冻结后运行，非诊断）

| 验收项 | 状态 |
|---|---|
| `M5-AC-00` 激活、实时基线与保护面 | 成立 |
| `M5-AC-01` 集成候选与最终 Manifest | 成立 |
| `M5-AC-02` 扩展完整主故事 | **PASS** |
| `M5-AC-03` 要求的合法短入口 | **PASS**（10/10） |
| `M5-AC-04` 十九维轻量全覆盖 | **CURRENT**（19/19；`cta`、`permission` 两维带已披露的未判定语义部分） |
| `M5-AC-05` M3 A/B | `NOT_VERIFIED` — 执行侧无权自裁 |
| `M5-AC-06` 最终成品 A/B | `NOT_VERIFIED` — 执行侧无权自裁 |
| **`M5-AC-07` 留出与高风险探针** | **FAIL** |
| `M5-AC-08` 不退化与受影响回归 | **PASS**（5/5） |
| `M5-AC-09` Founder 产品验收 | `NOT_VERIFIED` — 只能 Founder 给 |
| `M5-AC-10` Git、远端与最终回执 | 未开始 |

### `M5-AC-07` 的两个阻断项：都在 M1–M4，不是 M5 引入的

| 阻断项 | 根因 | 处置 |
|---|---|---|
| `HOLDOUT-M5-05`（P0） | **M3** 在恢复场景下接受了 Founder 对**技术状态**的三次口头改写：全量重跑、「宁可多一次」重复写入、「跑通了就算」 | 受保护面，无授权改动，待 Founder 裁定 |
| `RISK-M4-030+031` | **M4** 外壳解析器对含 ASCII 引号的值判为不在场，等价表达被误判为失败 | 受保护面，无授权改动，待 Founder 裁定 |

### 六份新鲜留出（解封后判定，逐条附原文引用）

`4 PASS / 1 FAIL(P0) / 1 项 NOT_VERIFIED`。详见 `V1_M5_HOLDOUT_VERDICTS_v1.0.md`。
留出正文七个 sha256 在解封当刻现场复算，与保管清单**逐条一致**——正文一字未动，
候选没有对着留出调过参。

### 交出的四份材料

| 文件 | 用途 |
|---|---|
| `V1_M5_FOUNDER_ACCEPTANCE_PACKAGE_v1.0.md` | `M5-AC-09`，大白话，含系统**拒绝**做的事与四条未修复缺陷 |
| `V1_M5_HUMAN_BLIND_REVIEW_PACKAGE_v1.0.md` | `M5-AC-05/06`，甲乙盲评 + 两段执行侧判不了的语义问题 |
| `V1_M5_HOLDOUT_VERDICTS_v1.0.md` | `M5-AC-07`，逐条附原文引用 |
| `V1_M5_FORMAL_ACCEPTANCE_EVIDENCE_INDEX_v1.0.yaml` | 十九维与 AC-00..10 的证据绑定 |

### 需要 Founder 做的三件事（执行侧做了都不算数）

1. **两级 A/B 盲评** —— 模型自评无效；实现者知道映射的评分无效。
   **盲评前不要打开** `AB_MAPPING_SEALED_*.json`，打开即作废。
2. **对 `M5-AC-07` 两个阻断项的处置裁定** —— 两者都在受保护面，改动需新授权。
3. **Founder 产品验收** —— 合同规定只能由 Founder 给。

## L3 · 正式尝试与证据（历史留痕，只加不改）

### `ATT-M5-NODE2-001` 现场预检事实快照（判据 = Root Prompt Node 2 八项 + Prestart 强制刷新项）

**Git（`git fetch --prune` + `git ls-remote` 均成功，取代规划编译时 HTTP 408 的 `NOT_VERIFIED`）**

```text
git_root                      = /home/faye/diyu-demo
remote                        = https://github.com/andyan77/diyu-demo.git
remote_default_branch         = refs/heads/main（ls-remote --symref 实测）
origin/main                   = f6eb86c076c47bd9f7c9323caac6c0ba1fc5098e
local main / HEAD             = f6eb86c076c47bd9f7c9323caac6c0ba1fc5098e（与远端一致）
M1 task/m1-natural-interaction-context-v1                  = b3ac43f0d1752051b24860092c2e668ce2de139a
M2 task/m2-business-persistence-version-feedback-v1        = ca5281aee70943f02cf5b3be50c8c139ebfd15d4
M3 task/m3-account-content-operator-v1                     = 00158d9ab9cb1064ec7ceccd346b6bea08a4765a
M4 codex/v1-m4-capability-seams-runtime-integration-001    = 5a318533ee0939a96e3406f20778ef476158fcaa
M1/M2/M3 是 origin/main 祖先 = true
M4 是 origin/main 祖先        = false
M4 与 main 的 merge-base      = ca5281aee70943f02cf5b3be50c8c139ebfd15d4（= M2 分支尖端）
M4 独有提交数                 = 29
main 独有提交数               = 109
```

四项模块分支哈希与 Prestart `module_branch_candidates` **逐项一致**；祖先关系与 `planning_observed_ancestry` **一致**。

**保护面（用户未跟踪文件，10 项，零改动）**

```text
M1_ENGINEERING_EXECUTION_REBASE_DELTA_v1.4.1_AUDITED_READY_FOR_FOUNDER_USE.md
M1_ENGINEERING_EXECUTION_REBASE_PROMPT_v1.3.md
M2_ENGINEERING_EXECUTION_PROMPT_v1.1_REBASE_ERRATA_001.md
M2_POST_DONE_REBASE_EXECUTION_PROMPT_v1.2.md
M4_ENGINEERING_EXECUTION_PROMPT_v1.3.md
route1.json
route2.json
笛语_V1_M0-M5_统一项目构建与验收方案_v1.0.md
笛语_V1_M0-M5_统一项目构建与验收方案_v1.1.md
笛语_V1_单账号持续内容运营纵向切片统一构建规划_v0.3.md
```

与 Prestart `protected_untracked_files_observed_in_live_root` **逐项一致**；未清理、未移动、未覆盖、未 stage。
`git stash list` 为空；其余 9 个既有 worktree 全部保持原分支与原提交，未触碰。

**M1–M4 receipt / handoff 现场复算（全部与 Prestart 绑定一致）**

| 文件 | 现场 `sha256` | 与 Prestart |
|---|---|---|
| `decision-chain/evidence/V1_M1_MODULE_LANDING_RECEIPT_v1.0.md` | `95d0f89244d20afc4199472097e8c123a56298c2388d9bb4fc31e9677c52798c` | 一致 |
| `business-persistence/M2_POST_DONE_REBASE_v1.2_RECORD.md` | `51b95058ea317d880b61955384d1f8d6e01f3bf75cde69a3eaaa2ca8021eba65` | 一致 |
| `M3_DIFY_RECOVERY_FINAL_CLOSEOUT_v1.0.md` | `6a15990d19b4c13cab8daf9ead1db9348d80841f5f5919e7de0a4cbd0089e61e` | 一致 |
| `…/m4…/decision-chain/docs/V1_M4_POST_RESTORE_FINAL_CLOSURE_RECEIPT_v1.0.md` | `de7c24c482ecd2c2ac62eaeccc77016aca6114e330ac9eaa58536317467213a9` | 一致 |
| `…/m4…/decision-chain/docs/V1_M4_M5_HANDOFF_MAP_v0.1.yaml` | `f1600de64b51784da6e7c3c6e68535423e1b120823cd6a42e413725c860ea45c` | 一致 |

**六份专业 Skill 源文件现行哈希（Node 4 冻结用；本节点零改动）**

```text
decision-chain/skills/Matrix_Architect_v0.1.2.md                  7a6afa3cf1a7b2e4793bd2b3dde6edddf20f75a5b8ed9f7aeb6a456d06acd838
decision-chain/skills/Campaign_Orchestrator_v0.1.md               c7ef284e40e7c4cd0d4081632fca7df17bd1a80fbd3f3b5267be4aea1040a0fb
decision-chain/skills/Content_Brief_Architect_v0.1.md             a0268a211a235b5b4df5e517f085db1f3b4948ae5add3346f2c15a426b63395f
content-production/skills/writing-creative-scripts/SKILL.md       d0f78a480f58d494a29d3a34e35106ba0ff48719052361748ed513c721fc7b6a
content-production/skills/directing-content-production/SKILL.md   87acc4a082500190f3b4454c088d95c6a60dce4062e5be120bb6f5b3adfdae3c
content-production/skills/packaging-content-for-release/SKILL.md  0c91a8efb0583523af8abc80dd1238b24d15791c1d0b0cef425eade6b277cc07
（M3 单账号持续运营能力）account-operations/skills/operating-one-account/SKILL.md  90596da5170730b90bfa87089d456e7a2f4d670c46f98ea6ae60138e1f4d3c41
```

**Dify 现场只读确认（`AUTHORIZED_READ_ONLY`，本节点零写入）**

```text
version            = 1.16.1（langgenius/dify-api:1.16.1），EDITION = SELF_HOSTED
health             = 15 个容器 Up，console /console/api/setup -> 200 @ http://127.0.0.1
db_now / tz        = UTC（宿主本地为 -0700，无时钟异常）
providers          = langgenius/deepseek/deepseek (is_valid=t)，langgenius/tongyi/tongyi (is_valid=t)
M4 六能力应用模型   = langgenius/deepseek/deepseek · deepseek-v4-flash（= 合同 preferred 目标模型/供应商）
近 12 小时 workflow_runs = 158（succeeded 147 / partial-succeeded 2 / failed 9）—— 模型链路当前实际可调用
```

M4 八个应用 published `workflow_id` 与 published graph `sha256` 现场复算，**与 Prestart 的 graph 前缀逐项一致**：

| 应用 | published `workflow_id` | published graph `sha256` | Prestart 前缀 |
|---|---|---|---|
| Founder Canvas | `61c4ce01-8924-4330-90ef-d9d1dd78b5ff` | `27f6aa48fce03c2e775727e417beec6ecc9c45f17a81a2de76f1c81a8bfed502` | `27f6aa` ✓ |
| Capability Seam | `4c5e2bab-9a4b-47f0-8ab0-1b844df4bb9d` | `9aec7d10bebd3260475c45cd6408868642d05e9d19bae99a9af4919548e805bf` | `9aec7d` ✓ |
| Matrix Architect | `3a9e0d8b-8151-4922-acd7-0926a6af49fd` | `9eded1bdc1dfe4d5b1013b640549557a53208de8f90d95bde25fbc669d1ec3dd` | `9eded1` ✓ |
| Campaign Orchestrator | `2da44fc7-09f0-4ed3-a000-addc641e077a` | `21817761588b1efe09f30e89cf2372156a8885b66761f13d6fe271853b9d5097` | `218177` ✓ |
| Content Brief Architect | `7f7fe5d1-3217-43e6-a3ed-7450b64b070b` | `e8e4268d2692a74f8f8c90a32e78e5d75d7b53abf2ff1877e34d362ff7fcc863` | `e8e426` ✓ |
| Creative Script (CS-1 + Script) | `3341b4de-e658-42a8-bc49-26fcf7e30bf7` | `a04c33276a7c833bff34df9c0165a2d352eb457e7c60bf7de797459f27a198a8` | `a04c33` ✓ |
| Production Director | `9a81b5c9-3773-44a6-af19-6255f8f30dce` | `89e7b6207e3aeebafd3b1d17b53aa041e821bfbee1afaa975f64aa3bf4256ef8` | `89e7b6` ✓ |
| Publishing & Packaging | `d838536b-6779-4d1e-951f-4cdabffa50d7` | `f3f0ed03e665be5738db6ce3acdcd31bad5ce347194537154b5779da6fff6f65` | `f3f0ed` ✓ |

八个应用均 `published_status = true`，且各自另有一个 `draft` 版本（未动）。

M3 候选应用 `b7fb5b1a-9278-426c-bb8a-f9f288639548`：published `workflow_id = 1fa7454e-1ce5-4202-b69f-ab371d9bf54a`，
`marked_name = m3-cand-v1.5.2-live`（**与 Prestart `published_version_candidate` 一致**），
published graph `sha256 = b7926795f2306b1ff2c735dd390acdd90ce028817498c989fd65265c054f8da5`。

> **口径说明**：Prestart 记的 `system_prompt_sha256_prefix_candidate = 3a3c657d` 是 M3 侧按其自有口径计算的系统提示词摘要，
> 本节点未复现该口径，因此**不据此宣布一致，也不据此宣布漂移**；Node 4 一律改用上面这条完整 published graph `sha256` 作为正式绑定。

**数据与测试权限现场确认**

```text
M2 持久化 = FastAPI 服务 business-persistence/，Postgres 库 diyu_business（存在）
alembic_version = 17368b750d3b（迁移态 CURRENT）
表 22 张，含 accounts / cycles / cycle_decisions / tasks / content_versions /
   publish_instances / feedback_records / idempotency_records / materials /
   playbooks / market_observations / task_snapshots / workspaces …
现有数据 = 测试域数据（workspaces 2222 条，均为 ws-<hex> 形态的测试工作区）
工作区隔离机制存在 => 任务域测试工作区写入可用，且不触碰非测试数据
M2 测试套件覆盖面 = idempotency / versioning / publish_feedback / material_withdrawal /
   recovery_and_playbooks / isolation / concurrency / interface_contracts / cycle_campaign / market_observation
   —— 与 M5 的 RISK-PUBLISH-ID-01 / RISK-RECOVERY-01 风险探针面直接对应
Dify 九个相关应用各有 1 个 service API key => 测试调用权限具备（未读取密钥值）
真实内容平台 = 未连接，且本任务不授权连接
```

**Node 2 判定**：第 1–6 项与第 8 项 `PASS/CURRENT`；第 7 项（新鲜留出保管）`IN_PROGRESS`。
无 `BLOCKED` 依赖缺口：远端可达、目标模型可用、M4 handoff 完整可读、测试数据与调用权限具备、留出隔离可实现。

---

## L5 · 外部副作用（只追加，不删不改）

| # | 时间（UTC） | 副作用 | 可逆性 | 说明 |
|---|---|---|---|---|
| 1 | `2026-08-28T04:56:51Z` | `git fetch --prune origin` | 只读性质 | 仅更新本地远端跟踪引用；未改任何本地分支 |
| 2 | `2026-08-28T04:56:51Z` | 新建分支 `codex/v1-m5-unified-integration-final-acceptance-001` @ `f6eb86c0` | 可逆 | 仅本地；未推送 |
| 3 | `2026-08-28T04:56:51Z` | 新建 worktree `/home/faye/diyu-demo-worktrees/m5-unified-integration-final-acceptance-v1` | 可逆 | 目录此前不存在，无冲突，未删除任何已有目录 |
| 4 | `2026-08-28T04:56:51Z` | **删除 `/home/faye/diyu-demo/.git/config.lock`** | 不可逆但无损 | 陈旧锁：0 字节、只读、`mtime 2026-08-27 14:17`，早于当次操作数小时；`lsof`/`fuser` 确认无进程持有；`.git/config`（`mtime 09:41`）完整可读，早于锁文件，证明没有中断中的写入。该锁使**任何** git config 写入失败（首次 `worktree add` 即因此半途失败）。删除后 `git config -l` 68 行正常、`remote.origin.url` 完好。**属 HOW 决定，已如实登记。** |
| 5 | `2026-08-28T04:56:51Z` | `git branch --set-upstream-to=origin/main`（M5 分支） | 可逆 | 副作用 4 之后补齐首次失败的 upstream 配置 |
| 6 | `2026-08-28T04:56:51Z` | Dify / `diyu_business` 只读查询 | 只读 | 全部为 SELECT；未创建、未修改、未删除任何应用、工作流、数据行或凭据 |

> 本节点**零**写入 Dify、零写入业务数据库、零改动六份 Skill 源文件、零改动 M1–M4 既有资产、零改动用户未跟踪文件。

---

## L4 · 已排除路线

（本任务暂无）
