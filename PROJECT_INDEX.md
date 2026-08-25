# 项目资产索引

本文件只做两件事：**说明东西放在哪**，以及**写清加新文件的规矩**。

---

## 〇、当前阶段与合同状态（先看这一段）

| 合同 | 状态 | 授权范围 |
|---|---|---|
| [V1 决策链改造产品合同（上位）](decision-chain/docs/V1_DECISION_CHAIN_REBASE_PRODUCT_CONTRACT_v0.1.md) | `PRODUCT_CONTRACT_ACCEPTED — REPO_PREFLIGHT_AUTHORIZED` | **仅 `V1-REBASE-EP00-CURRENT` 只读预检** |
| [单账号持续运营纵向切片子合同 v0.2](decision-chain/docs/V1_SINGLE_ACCOUNT_SLICE_CONTRACT_v0.2.md) | `ACCEPTED — SINGLE_ACCOUNT_SLICE_PREFLIGHT_AUTHORIZED` | 已被 Founder 接受（v0.1 为历史版本） |
| M0.3 四份共享合同（`decision-chain/docs/V1_M0_SHARED_CONTRACT_*_v0.1.md`） | `ACCEPTED` | 授权 M1—M4 施工规划编译，**不授权工程实现本身** |
| [M1–M4 Phase 0 共享编译前言](decision-chain/docs/V1_M1_M4_CONSTRUCTION_PROMPT_SHARED_PREAMBLE_v0.1.md) | `ACTIVE_ON_DEFAULT_BASELINE — FOUNDER_CONFIRMED` | 供规划侧编译 M1—M4 各自施工 Execution Prompt 的共同前言；**不构成任何工程实现授权**（`engineering_execution_authorized: false`） |
| [M1 施工 Execution Prompt v1.2](decision-chain/docs/M1_ENGINEERING_EXECUTION_PROMPT_v1.2.md) | `READY_FOR_FOUNDER_USE` | 规划侧已编译完成并落盘；**工程实现未获授权**（`engineering_execution_authorized_by_prompt_compilation: false`），需 Founder 就 `task_id: DIYU-V1-M1-NATURAL-CONTEXT-001` 另行明确授权执行 |
| [M2 施工 Execution Prompt v1.1](decision-chain/docs/M2_ENGINEERING_EXECUTION_PROMPT_v1.1.md) | `READY_FOR_FOUNDER_USE` | 规划侧已编译完成并落盘；**工程实现未获授权**（`engineering_execution_performed: false`），需 Founder 就 `task_id: DIYU-V1-M2-BUSINESS-PERSISTENCE-VERSION-FEEDBACK-001` 另行明确授权执行；文档自证 `task_contract_hash` 与实际内容字节不一致，已由 Founder 确认改以独立复算值 `4d14eb35c065b650b0380b0c309e0e08ec32e3aa608ece4d62e8d27b97450830` 登记（见 [L1 §T-010](collab-ledger/L1_TASK_MANIFESTS.md)） |

- **上位合同被接受 ≠ 子合同被接受 ≠ 授权施工。**
- 阶段为 **V1 决策链重对齐（Rebase）**；A/B 对照阶段已结束并按 `PARTIAL` 冻结。
- **决策链与内容生产链都在产品范围内**，都已建成并在运行；**不存在「唯一活跃主线」**。
- 「Matrix → Campaign → Brief → 生产」作为**唯一入口**的假设**已废止**；八项能力按需调用、可直接进入、可合法组合。

---

## 一、资产到哪里找

仓库按「两个业务模块 + 五类资产」组织。

| 模块 | 说明 |
|---|---|
| [decision-chain/](decision-chain/) | 决策链：Matrix Architect、Campaign Orchestrator、Content Brief Architect，以及**两份产品合同与阶段基线**。**在产品范围内** |
| [content-production/](content-production/) | 内容生产链：Creative Script、Production Director、Publishing & Packaging。**在产品范围内** |

> **内容生产链三 Skill v0.6 能力资产包**，由 Creative Script、Production Director、Publishing & Packaging 三份核心 Skill，以及配套的行业条件、平台事实和端到端案例参考资产组成。
>
> 正式运行资产就是这一个包：三份 `SKILL.md` ＋ `platforms.md` ＋ `industry-conditions.md` ＋ `examples.md`。
> 「6—8 张创意操作卡 ＋ 8—10 张视听实现卡 ＋ 4 个黄金案例 ＋ 动态平台参考包」只表示 v0.6 正向能力补强研究的**原始交付目标**，不是当前的独立文件清单。
> **不得再把 Skill 与 references 称为两套并列资产。**
| [tools/](tools/) | 通用辅助脚本 |
| [collab-ledger/](collab-ledger/) | **协作连续性账本**：规则正文 ＋ 五本账（L1–L5）。**不是业务模块**，不适用「五类资产」分类 |

每个模块下最多五类：

| 目录 | 放什么 |
|---|---|
| `docs/` | 合同、Golden、正式决策说明、状态说明、阶段基线、专家问答与研究材料 |
| `skills/` | Skill 正文 |
| `workflows/` | Dify 工作流 DSL |
| `fixtures/` | 品牌夹具、固定输入、场景输入 |
| `evidence/` | RAW、FINAL、TRACE、EVAL、Manifest、盲审材料、测试应用 |

### 常用入口

| 要找的东西 | 去哪 |
|---|---|
| 项目定位、阶段与 Founder 已裁决事项 | [笛语项目基线.md](笛语项目基线.md) |
| 协作规则与硬约束 | [CLAUDE.md](CLAUDE.md) |
| **换会话接手：任务做到哪／下一步／什么不能碰／哪条路走死** | [collab-ledger/COLLAB_CONTINUITY_PROTOCOL.md](collab-ledger/COLLAB_CONTINUITY_PROTOCOL.md) —— **规则唯一正文**；五本账 [L1](collab-ledger/L1_TASK_MANIFESTS.md)·[L2](collab-ledger/L2_TASK_STATE_AND_HANDOFF.md)·[L3](collab-ledger/L3_ATTEMPTS_AND_EVIDENCE.md)·[L4](collab-ledger/L4_FAILED_PATHS.md)·[L5](collab-ledger/L5_SIDE_EFFECTS.md) |
| **决策链改造产品合同（上位，最高真相源）** | [V1_DECISION_CHAIN_REBASE_PRODUCT_CONTRACT_v0.1.md](decision-chain/docs/V1_DECISION_CHAIN_REBASE_PRODUCT_CONTRACT_v0.1.md) —— `PRODUCT_CONTRACT_ACCEPTED — REPO_PREFLIGHT_AUTHORIZED`，**只授权 `V1-REBASE-EP00-CURRENT` 只读预检** |
| **单账号持续运营纵向切片子合同（已接受）** | [V1_SINGLE_ACCOUNT_SLICE_CONTRACT_v0.2.md](decision-chain/docs/V1_SINGLE_ACCOUNT_SLICE_CONTRACT_v0.2.md) —— `ACCEPTED — SINGLE_ACCOUNT_SLICE_PREFLIGHT_AUTHORIZED`；[v0.1](decision-chain/docs/V1_SINGLE_ACCOUNT_SLICE_CONTRACT_v0.1.md) 为历史版本，逐字保留 |
| **M0.3 四份共享合同（已接受）** | [任务上下文快照](decision-chain/docs/V1_M0_SHARED_CONTRACT_TASK_CONTEXT_SNAPSHOT_v0.1.md)／[八项能力合同](decision-chain/docs/V1_M0_SHARED_CONTRACT_EIGHT_CAPABILITIES_v0.1.md)／[版本发布反馈归属](decision-chain/docs/V1_M0_SHARED_CONTRACT_VERSION_PUBLISH_FEEDBACK_v0.1.md)／[写回权限幂等恢复](decision-chain/docs/V1_M0_SHARED_CONTRACT_WRITE_PERMISSION_RECOVERY_v0.1.md) —— 授权 M1—M4 施工规划编译，不授权工程实现本身 |
| **M1–M4 Phase 0 共享编译前言** | [V1_M1_M4_CONSTRUCTION_PROMPT_SHARED_PREAMBLE_v0.1.md](decision-chain/docs/V1_M1_M4_CONSTRUCTION_PROMPT_SHARED_PREAMBLE_v0.1.md) —— 实例化八项能力四类业务合同值 + Matrix 局部降级口径，供规划侧编译 M1—M4 各自施工 Execution Prompt；不是第五份共享合同，不构成工程实现授权 |
| **M1 施工 Execution Prompt（已落盘，未授权工程执行）** | [M1_ENGINEERING_EXECUTION_PROMPT_v1.2.md](decision-chain/docs/M1_ENGINEERING_EXECUTION_PROMPT_v1.2.md) —— W1-M1 窗口完整 P0 施工合同；`task_id: DIYU-V1-M1-NATURAL-CONTEXT-001` 尚未开工，需 Founder 另行明确授权工程执行；M2/M3/M4 施工 Execution Prompt 仍待编译 |
| **单账号纵向切片专项预检（已完成）** | [V1_SINGLE_ACCOUNT_SLICE_EP00_PREFLIGHT_v0.1.md](decision-chain/docs/V1_SINGLE_ACCOUNT_SLICE_EP00_PREFLIGHT_v0.1.md) |
| **决策链当前阶段基线** | [V1_DECISION_CHAIN_STAGE_BASELINE_v0.2.md](decision-chain/docs/V1_DECISION_CHAIN_STAGE_BASELINE_v0.2.md) |
| 决策链 A/B 阶段历史基线（`PARTIAL`，原样保留） | [V1_DECISION_CHAIN_STAGE_BASELINE_v0.1.md](decision-chain/docs/V1_DECISION_CHAIN_STAGE_BASELINE_v0.1.md) |
| **对话编排修复 001 运行证据（A-0～A-4 真实对话，`DONE`）** | [V1_DIALOGUE_ORCHESTRATION_REPAIR_001_EVIDENCE.md](decision-chain/evidence/V1_DIALOGUE_ORCHESTRATION_REPAIR_001_EVIDENCE.md) —— 测试目录的承接见 [V1_NATURAL_LANGUAGE_TEST_CATALOG_v0.1.md](decision-chain/docs/V1_NATURAL_LANGUAGE_TEST_CATALOG_v0.1.md) 承接附录 |
| **集成后的主 Chatflow DSL（56 节点，与 Dify 已发布版本逐节点一致）** | [DIYU_DEMO_V1_FULL_CHAIN_CHATFLOW_v0.2.yml](decision-chain/workflows/DIYU_DEMO_V1_FULL_CHAIN_CHATFLOW_v0.2.yml) |
| 任务快照 Schema（已增量补齐 `open_threads` / `last_acceptance`） | [V1_TASK_SNAPSHOT_SCHEMA_v0.1.json](decision-chain/docs/V1_TASK_SNAPSHOT_SCHEMA_v0.1.json) |
| 生产差距登记（G-01～G-12 全部未关闭，含"旧 Demo 不阻塞 / 持续运营成立条件"分档） | [V1_PRODUCTION_GAP_REGISTER_v0.1.md](decision-chain/docs/V1_PRODUCTION_GAP_REGISTER_v0.1.md) |
| **内容生产链入口（当前主线）** | [content-production/docs/CONTENT_PRODUCTION_CHAIN_PRD_v0.1.md](content-production/docs/CONTENT_PRODUCTION_CHAIN_PRD_v0.1.md) |
| 三份决策 Skill 正文 | [decision-chain/skills/](decision-chain/skills/) |
| **内容生产三份 Skill（活跃主线）** | Creative Script → [content-production/skills/writing-creative-scripts/](content-production/skills/writing-creative-scripts/)<br>Production Director → [content-production/skills/directing-content-production/](content-production/skills/directing-content-production/)<br>Publishing & Packaging → [content-production/skills/packaging-content-for-release/](content-production/skills/packaging-content-for-release/) |
| **共享 references 正式主本** | [content-production/references/](content-production/references/) |
| **内容生产运行合同（九槽位／人工回改／manifest／运行时限／回改结构化出口／chain_status）** | [content-production/docs/CONTENT_PRODUCTION_RUNTIME_CONTRACT_v0.1.md](content-production/docs/CONTENT_PRODUCTION_RUNTIME_CONTRACT_v0.1.md) |
| **拍摄前生产链（两段式父工作流 ＋ 控制器）** | Stage 1 CS→PD → [content-production/workflows/DIYU_DEMO_CONTENT_PRODUCTION_PRE_CHAIN_STAGE1_V0_1.yml](content-production/workflows/DIYU_DEMO_CONTENT_PRODUCTION_PRE_CHAIN_STAGE1_V0_1.yml)<br>Stage 2 发布包装（通用，PRE／MIXED／FINAL 三档）→ [content-production/workflows/DIYU_DEMO_CONTENT_PRODUCTION_PUBLISHING_STAGE2_V0_1.yml](content-production/workflows/DIYU_DEMO_CONTENT_PRODUCTION_PUBLISHING_STAGE2_V0_1.yml)<br>段间控制器 → [tools/content_production_pre_chain_controller.py](tools/content_production_pre_chain_controller.py) |
| **两条运行时限（1200 s 工作流 ／ 600 s 单次 LLM 调用）** | 运行合同 [第 7.1 节](content-production/docs/CONTENT_PRODUCTION_RUNTIME_CONTRACT_v0.1.md) —— **每次运行前必查，不得凭印象** |
| **Workflow Tool 钉版本（子应用改参数并发布 ≠ Tool 跟着变）** | 运行记录 002 [第 2.3 节](content-production/evidence/CONTENT_PRODUCTION_PRE_CHAIN_FIXTURE_RUN_002.md) —— **改完子应用参数必须同步三个 Tool 的版本绑定，否则父流静默跑旧版本、不报错** |
| **最小事实夹具（两段链集成测试专用，非真实经营事实）** | 夹具 → [content-production/fixtures/CONTENT_PRODUCTION_MINIMAL_CHAIN_FIXTURE_v0.1.md](content-production/fixtures/CONTENT_PRODUCTION_MINIMAL_CHAIN_FIXTURE_v0.1.md)<br>运行记录 001 → [content-production/evidence/CONTENT_PRODUCTION_PRE_CHAIN_FIXTURE_RUN_001.md](content-production/evidence/CONTENT_PRODUCTION_PRE_CHAIN_FIXTURE_RUN_001.md) —— **BLOCKED：已证伪「缩小输入可绕过 600 s」，见该文件第 10.2 节**<br>运行记录 002 → [content-production/evidence/CONTENT_PRODUCTION_PRE_CHAIN_FIXTURE_RUN_002.md](content-production/evidence/CONTENT_PRODUCTION_PRE_CHAIN_FIXTURE_RUN_002.md) —— **DONE：六项验收全通过，全链 9.5 分钟跑通** |
| **完整 Content Brief 全链（当前最新一轮）** | 运行证据 → [content-production/evidence/CONTENT_PRODUCTION_FULL_BRIEF_PRE_CHAIN_RUN_001.md](content-production/evidence/CONTENT_PRODUCTION_FULL_BRIEF_PRE_CHAIN_RUN_001.md) —— **运行层 DONE（§六 九项 9/9）；三组盲评已完成、4 处事实已核实，结果见第十四节。遗留项已由 P05 关闭：4 条事实登记进 [BRF-SUHE-001_FACT_ADDENDUM_v0.1.md](content-production/fixtures/BRF-SUHE-001_FACT_ADDENDUM_v0.1.md)，冻结 Brief 与其 SHA 未动**<br>质量对照包（盲评，先读它再读交付包）→ [content-production/evidence/CONTENT_PRODUCTION_FULL_BRIEF_QUALITY_REVIEW_PACK_v0.1.md](content-production/evidence/CONTENT_PRODUCTION_FULL_BRIEF_QUALITY_REVIEW_PACK_v0.1.md)<br>用户交付包（给出镜者／拍摄剪辑／拍板者三部分）→ [content-production/evidence/CONTENT_PRODUCTION_FULL_BRIEF_USER_DELIVERY_PACK_v0.1.md](content-production/evidence/CONTENT_PRODUCTION_FULL_BRIEF_USER_DELIVERY_PACK_v0.1.md) |
| **拍后 Manifest 分支（当前最新一轮）** | 运行证据 → [content-production/evidence/CONTENT_PRODUCTION_FINAL_CHAIN_RUN_001.md](content-production/evidence/CONTENT_PRODUCTION_FINAL_CHAIN_RUN_001.md) —— **PARTIAL：PP 自行推导出 `MIXED` 而非 `FINAL`，撞出 Skill v0.6「有，但不够」三值与 mode 两档未对齐的空白（见第五节，待版本裁决）；十项验证 9 过 2 未过 2 待裁决；命中 1 处无依据事实已标注未删**<br>事实增补件（P04 §5.1 遗留项的落地）→ [content-production/fixtures/BRF-SUHE-001_FACT_ADDENDUM_v0.1.md](content-production/fixtures/BRF-SUHE-001_FACT_ADDENDUM_v0.1.md)<br>模拟拍后 manifest 夹具（**SIMULATION_ONLY**，非真实素材）→ [content-production/fixtures/CONTENT_PRODUCTION_REALIZATION_MANIFEST_FIXTURE_v0.1.md](content-production/fixtures/CONTENT_PRODUCTION_REALIZATION_MANIFEST_FIXTURE_v0.1.md)<br>最终用户交付包（三部分）→ [content-production/evidence/CONTENT_PRODUCTION_FINAL_USER_DELIVERY_PACK_v0.1.md](content-production/evidence/CONTENT_PRODUCTION_FINAL_USER_DELIVERY_PACK_v0.1.md) —— **先读开头「口径更正」** |
| **PP v0.6.1 三档判据（当前最新一轮）** | 运行记录 → [content-production/evidence/CONTENT_PRODUCTION_P05R1_RUN.md](content-production/evidence/CONTENT_PRODUCTION_P05R1_RUN.md) —— **PARTIAL：mode 判据改成三级依次判（「有，但不够」不决定 mode，缺口有没有处置完才决定），PRE 静态 5/5、MIXED 8/8、FINAL 6 过 3 未过；FINAL 命中一处假绿——模型自称已删除、实际没删**<br>MIXED 夹具（S4 缺口未拍板）→ [content-production/fixtures/CONTENT_PRODUCTION_REALIZATION_MANIFEST_MIXED_FIXTURE_v0.1.md](content-production/fixtures/CONTENT_PRODUCTION_REALIZATION_MANIFEST_MIXED_FIXTURE_v0.1.md)<br>FINAL 夹具（完整覆盖）→ [content-production/fixtures/CONTENT_PRODUCTION_REALIZATION_MANIFEST_FINAL_FIXTURE_v0.1.md](content-production/fixtures/CONTENT_PRODUCTION_REALIZATION_MANIFEST_FINAL_FIXTURE_v0.1.md)<br>最终用户交付包 v0.2（由 FINAL 轮生成）→ [content-production/evidence/CONTENT_PRODUCTION_FINAL_USER_DELIVERY_PACK_v0.2.md](content-production/evidence/CONTENT_PRODUCTION_FINAL_USER_DELIVERY_PACK_v0.2.md) —— **先读首页横幅与 ⚠️ 标注** |
| **PP v0.6.2 事实纪律与假绿阻断（当前最新一轮）** | 运行记录 → [content-production/evidence/CONTENT_PRODUCTION_P05R2_RUN.md](content-production/evidence/CONTENT_PRODUCTION_P05R2_RUN.md) —— **PARTIAL：四道确定性闸建成并在真实运行中拦截成功；十二项自动验收 12/12 全过；但逐句人工核验查出一处无依据事实（「十几次试穿」——它挂着真实 fact_id，四道闸与两个扫描器全部放行）。按规则不生成 v0.3 交付包，问题句原样保留在证据第九节**<br>**最该看的一节**：第六节「确定性闸堵住了格式型与自述型问题，堵不住语义型编造」<br>新增运行状态 `USER_DELIVERY_BLOCKED_FACT_CHECK` → 运行合同 [第 9 节](content-production/docs/CONTENT_PRODUCTION_RUNTIME_CONTRACT_v0.1.md) |
| **独立语义事实核验（当前最新一轮）** | 运行记录 → [content-production/evidence/CONTENT_PRODUCTION_P05R3_RUN.md](content-production/evidence/CONTENT_PRODUCTION_P05R3_RUN.md) —— **`SEMANTIC_CHECKER_ACCEPTED_NO_REGRESSION`：PP 之后加了一个只读语义核验节点（qwen3.8-max，独立于内容生产的 DeepSeek）。负向探针正确 BLOCK 并抓出 P05R2 那句「十几次试穿」；正向探针正确 PASS 且零误报；十条非衰减判据 10/10。但正式运行被两层同时拦下（四道闸命中简写编号；语义层抓出「前一天」与「单穿也站得住」两处，后者踩的正是 A04 的「不得扩大」条款），按第六节不生成 v0.3 用户交付包，Artifact 与原交付块原样保留**<br>**最该看的两节**：第七节「两层各自拦的是什么，别混为一谈」、第九节「它的证据范围只有 4 样输入，账号结构类陈述判不稳」<br>新增运行状态 `USER_DELIVERY_MANUAL_FACT_REVIEW_REQUIRED` 与「语义事实核验节点」一节 → 运行合同 [第 9 节](content-production/docs/CONTENT_PRODUCTION_RUNTIME_CONTRACT_v0.1.md) |
| V1 集成合同（**旧 Demo 兼容基线，非 Rebase 目标架构**；未承接的四项变化见其更正附录） | [decision-chain/docs/V1_DEMO_INTEGRATION_CONTRACT_v0.1.md](decision-chain/docs/V1_DEMO_INTEGRATION_CONTRACT_v0.1.md) |
| **同一资产的多版本**（哪个是当前） | Matrix Architect → 部署运行的是 **v0.1.2**，v0.1／v0.1.1 对应 RUN_001／RUN_002 原样保留<br>Campaign 专家共同上下文 → **v0.2** 为当前，v0.1 保留<br>Campaign 六张专家问题卡 → **v0.3** 为当前，v0.2 保留 |
| **带口径更正块的文档**（原文未改，只加更正） | 候选数量固定值作废 → [构建规范](content-production/docs/内容生产三份%20Skill%20构建规范%20v1.0.md)、[验收标准](content-production/docs/内容生产三份%20Skill%20验收标准%20v1.0.md)、[context_pack](content-production/docs/context_pack.md)<br>固定线性调用不再是目标架构 → [CONTENT_BRIEF_CONTRACT](decision-chain/docs/CONTENT_BRIEF_CONTRACT_v0.1.md)、[生产链 PRD](content-production/docs/CONTENT_PRODUCTION_CHAIN_PRD_v0.1.md)、[生产链合同](content-production/docs/CONTENT_PRODUCTION_CHAIN_CONTRACT_v0.1.md) |
| `tools/` 脚本路径解析（目录重组后按文件名解析，判据未改） | [tools/_repo_paths.py](tools/_repo_paths.py) |
| 品牌夹具（序里集） | [decision-chain/fixtures/](decision-chain/fixtures/) |
| V1 全部运行证据与盲审材料 | [decision-chain/evidence/](decision-chain/evidence/) |

---

## 二、文档管理规则

1. 新文件**先按业务模块归类，再按 `docs` / `skills` / `workflows` / `fixtures` / `evidence` 归类**。
2. **根目录不再堆放业务文档。**
3. 同一个事实**只保留一个正式来源**，其他文件用链接，**不复制正文**。
4. RAW、FINAL、TRACE、EVAL、Manifest 和盲审材料属于**冻结证据，只能移动，不能改正文**。
5. 普通进度**直接更新模块现有状态文档**，不为每次工作新建总结。
6. 只有 **Skill、合同或正式能力发生实质变化**时才建立新版本。
7. 过程汇报、临时分析、重复总结**不进入仓库**。
8. **没有实际资产时不建立空目录。**
9. 修正历史证据**只能新增更正说明，不得修改原文件**。冻结合同同理——**另建后继版本或加更正说明，不覆盖原文**。
9.1 **不得由执行侧宣布合同「已接受」**，也不得自行把合同状态往上推一级。
10. 如果现有分类已经能够快速找到文件，**不再继续细分目录**。
11. `collab-ledger/` 是**治理区，不是业务模块**：只放协作连续性规则与五本账，**不放**任何产品资产；其写入时机与责任主体由 [规则正文](collab-ledger/COLLAB_CONTINUITY_PROTOCOL.md) 规定，本文件不复述。

**不建立**复杂的文档状态机、登记表、审批流或多层索引。历史依靠 Git 追溯，不建 archive 体系。

### Skill 与 references 维护

三份 Skill 各自保持自包含；共享 references 的正式主本位于 `content-production/references/`。修改 references 时，必须在同一提交中同步三个 Skill 内副本并核对哈希。
