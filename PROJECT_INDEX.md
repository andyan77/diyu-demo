# 项目资产索引

本文件只做两件事：**说明东西放在哪**，以及**写清加新文件的规矩**。

---

## 一、资产到哪里找

仓库按「两个业务模块 + 五类资产」组织。

| 模块 | 说明 |
|---|---|
| [decision-chain/](decision-chain/) | 决策链：Matrix Architect、Campaign Orchestrator、Content Brief Architect。**已冻结，非活跃主线** |
| [content-production/](content-production/) | 内容生产链：Creative Script、Production Director、Publishing & Packaging。**当前唯一活跃主线** |

> **内容生产链三 Skill v0.6 能力资产包**，由 Creative Script、Production Director、Publishing & Packaging 三份核心 Skill，以及配套的行业条件、平台事实和端到端案例参考资产组成。
>
> 正式运行资产就是这一个包：三份 `SKILL.md` ＋ `platforms.md` ＋ `industry-conditions.md` ＋ `examples.md`。
> 「6—8 张创意操作卡 ＋ 8—10 张视听实现卡 ＋ 4 个黄金案例 ＋ 动态平台参考包」只表示 v0.6 正向能力补强研究的**原始交付目标**，不是当前的独立文件清单。
> **不得再把 Skill 与 references 称为两套并列资产。**
| [tools/](tools/) | 通用辅助脚本 |

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
| **决策链 V1 当前状态（含已知问题与能力边界）** | [decision-chain/docs/V1_DECISION_CHAIN_STAGE_BASELINE_v0.1.md](decision-chain/docs/V1_DECISION_CHAIN_STAGE_BASELINE_v0.1.md) |
| **内容生产链入口（当前主线）** | [content-production/docs/CONTENT_PRODUCTION_CHAIN_PRD_v0.1.md](content-production/docs/CONTENT_PRODUCTION_CHAIN_PRD_v0.1.md) |
| 三份决策 Skill 正文 | [decision-chain/skills/](decision-chain/skills/) |
| **内容生产三份 Skill（活跃主线）** | Creative Script → [content-production/skills/writing-creative-scripts/](content-production/skills/writing-creative-scripts/)<br>Production Director → [content-production/skills/directing-content-production/](content-production/skills/directing-content-production/)<br>Publishing & Packaging → [content-production/skills/packaging-content-for-release/](content-production/skills/packaging-content-for-release/) |
| **共享 references 正式主本** | [content-production/references/](content-production/references/) |
| **内容生产运行合同（九槽位／人工回改／manifest／运行时限／回改结构化出口／chain_status）** | [content-production/docs/CONTENT_PRODUCTION_RUNTIME_CONTRACT_v0.1.md](content-production/docs/CONTENT_PRODUCTION_RUNTIME_CONTRACT_v0.1.md) |
| **拍摄前生产链（两段式父工作流 ＋ 控制器）** | Stage 1 CS→PD → [content-production/workflows/DIYU_DEMO_CONTENT_PRODUCTION_PRE_CHAIN_STAGE1_V0_1.yml](content-production/workflows/DIYU_DEMO_CONTENT_PRODUCTION_PRE_CHAIN_STAGE1_V0_1.yml)<br>Stage 2 PP·PRE → [content-production/workflows/DIYU_DEMO_CONTENT_PRODUCTION_PRE_CHAIN_STAGE2_V0_1.yml](content-production/workflows/DIYU_DEMO_CONTENT_PRODUCTION_PRE_CHAIN_STAGE2_V0_1.yml)<br>段间控制器 → [tools/content_production_pre_chain_controller.py](tools/content_production_pre_chain_controller.py) |
| **两条运行时限（1200 s 工作流 ／ 600 s 单次 LLM 调用）** | 运行合同 [第 7.1 节](content-production/docs/CONTENT_PRODUCTION_RUNTIME_CONTRACT_v0.1.md) —— **每次运行前必查，不得凭印象** |
| **Workflow Tool 钉版本（子应用改参数并发布 ≠ Tool 跟着变）** | 运行记录 002 [第 2.3 节](content-production/evidence/CONTENT_PRODUCTION_PRE_CHAIN_FIXTURE_RUN_002.md) —— **改完子应用参数必须同步三个 Tool 的版本绑定，否则父流静默跑旧版本、不报错** |
| **最小事实夹具（两段链集成测试专用，非真实经营事实）** | 夹具 → [content-production/fixtures/CONTENT_PRODUCTION_MINIMAL_CHAIN_FIXTURE_v0.1.md](content-production/fixtures/CONTENT_PRODUCTION_MINIMAL_CHAIN_FIXTURE_v0.1.md)<br>运行记录 001 → [content-production/evidence/CONTENT_PRODUCTION_PRE_CHAIN_FIXTURE_RUN_001.md](content-production/evidence/CONTENT_PRODUCTION_PRE_CHAIN_FIXTURE_RUN_001.md) —— **BLOCKED：已证伪「缩小输入可绕过 600 s」，见该文件第 10.2 节**<br>运行记录 002 → [content-production/evidence/CONTENT_PRODUCTION_PRE_CHAIN_FIXTURE_RUN_002.md](content-production/evidence/CONTENT_PRODUCTION_PRE_CHAIN_FIXTURE_RUN_002.md) —— **DONE：六项验收全通过，全链 9.5 分钟跑通** |
| **完整 Content Brief 全链（当前最新一轮）** | 运行证据 → [content-production/evidence/CONTENT_PRODUCTION_FULL_BRIEF_PRE_CHAIN_RUN_001.md](content-production/evidence/CONTENT_PRODUCTION_FULL_BRIEF_PRE_CHAIN_RUN_001.md) —— **运行层 DONE（§六 九项 9/9）；三组盲评已完成、4 处事实已核实，结果见第十四节。遗留项已由 P05 关闭：4 条事实登记进 [BRF-SUHE-001_FACT_ADDENDUM_v0.1.md](content-production/fixtures/BRF-SUHE-001_FACT_ADDENDUM_v0.1.md)，冻结 Brief 与其 SHA 未动**<br>质量对照包（盲评，先读它再读交付包）→ [content-production/evidence/CONTENT_PRODUCTION_FULL_BRIEF_QUALITY_REVIEW_PACK_v0.1.md](content-production/evidence/CONTENT_PRODUCTION_FULL_BRIEF_QUALITY_REVIEW_PACK_v0.1.md)<br>用户交付包（给出镜者／拍摄剪辑／拍板者三部分）→ [content-production/evidence/CONTENT_PRODUCTION_FULL_BRIEF_USER_DELIVERY_PACK_v0.1.md](content-production/evidence/CONTENT_PRODUCTION_FULL_BRIEF_USER_DELIVERY_PACK_v0.1.md) |
| **拍后 Manifest 分支（当前最新一轮）** | 运行证据 → [content-production/evidence/CONTENT_PRODUCTION_FINAL_CHAIN_RUN_001.md](content-production/evidence/CONTENT_PRODUCTION_FINAL_CHAIN_RUN_001.md) —— **PARTIAL：PP 自行推导出 `MIXED` 而非 `FINAL`，撞出 Skill v0.6「有，但不够」三值与 mode 两档未对齐的空白（见第五节，待版本裁决）；十项验证 9 过 2 未过 2 待裁决；命中 1 处无依据事实已标注未删**<br>事实增补件（P04 §5.1 遗留项的落地）→ [content-production/fixtures/BRF-SUHE-001_FACT_ADDENDUM_v0.1.md](content-production/fixtures/BRF-SUHE-001_FACT_ADDENDUM_v0.1.md)<br>模拟拍后 manifest 夹具（**SIMULATION_ONLY**，非真实素材）→ [content-production/fixtures/CONTENT_PRODUCTION_REALIZATION_MANIFEST_FIXTURE_v0.1.md](content-production/fixtures/CONTENT_PRODUCTION_REALIZATION_MANIFEST_FIXTURE_v0.1.md)<br>最终用户交付包（三部分）→ [content-production/evidence/CONTENT_PRODUCTION_FINAL_USER_DELIVERY_PACK_v0.1.md](content-production/evidence/CONTENT_PRODUCTION_FINAL_USER_DELIVERY_PACK_v0.1.md) —— **先读开头「口径更正」** |
| V1 集成合同 | [decision-chain/docs/V1_DEMO_INTEGRATION_CONTRACT_v0.1.md](decision-chain/docs/V1_DEMO_INTEGRATION_CONTRACT_v0.1.md) |
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
9. 修正历史证据**只能新增更正说明，不得修改原文件**。
10. 如果现有分类已经能够快速找到文件，**不再继续细分目录**。

**不建立**复杂的文档状态机、登记表、审批流或多层索引。历史依靠 Git 追溯，不建 archive 体系。

### Skill 与 references 维护

三份 Skill 各自保持自包含；共享 references 的正式主本位于 `content-production/references/`。修改 references 时，必须在同一提交中同步三个 Skill 内副本并核对哈希。
