# P0 内容发布包装助手 · 产品合同对齐表 v1.0（E1-2）

```yaml
task_id: DIYU-V1-THREE-SKU-EXTRACTION-001
sku: P0
gate_table_core_judgment: 这份成品应该怎样发布包装
standard: Q-COMM-04_P0_内容发布包装助手商业化评价验收标准_v1.0.md（55bcfa40…c397）
tested_object: products/p0-publishing-packaging/DIYU_M4_TOOL_PUBLISHING_PACKAGING_v1_4.yml（= 原 v1_4，82cadc34…20c3）
note: 登记不修。差距见对应行，修复不在本任务范围。
```

## §1 商业产品合同

| 标准条款 | 判定 | 实际做的事 / 出处 |
|---|---|---|
| §1.1 用户已拥有成片，产品负责转换为发布包装方案，不重新决定内容"应该做什么" | `MATCH` | `skill_llm` 系统提示词明文"本 Skill 不调用、不请求、不假设任何上游组件被运行过"，硬禁"有合法成片时不得强制补跑 CS 或 PD"（SKILL_v1.4.md「合法等价兑现证据与直达」节，「硬禁：有合法成片时强制补跑 CS 或 PD」小节） |
| §1.2 最低合法输入：已有内容 + 目标发布平台 + 必要事实 + 表达边界 + CTA/承接条件 | `PARTIAL` | `envelope_check.REQUIRED` 六项字面 key（`content_body_or_beats`/`content_promise`/`explicit_non_promise`/`facts_registered`/`cta_contract`/`asset_publish_permission`）与标准五要素**命名不对齐**：`content_promise`、`asset_publish_permission` 在标准 §1.2 的五要素定义里没有直接对应项；"表达边界"对应 `explicit_non_promise` 还是 `component_return.QUESTION_MAP` 里单列的 `expression_boundary`/`expression_subject_and_boundary` 不确定，后两者不在 `REQUIRED` 六项里。裸给标准定义的最低输入，若不恰好命中六个英文字面 key（或其三种写法之一），大概率被 `gate_sufficiency` 短路到 `component_return`，拿不到任何专业产出 |
| §1.2 信息不足时仅追问当前最能改变发布判断的一项缺口 | `MATCH` | `component_return` 节点 `QUESTION_MAP` 机制：`missing[0]` 转译为自然语言追问，一次只问一项（"只追问当前最具区分力的一项"，代码注释原文） |
| §1.3 标题 | `MATCH` | `titles[]`/`recommended_title`（SKILL_v1.4.md「输出」块） |
| §1.3 封面策略与封面文字 | `MATCH` | `cover` 字段（同上） |
| §1.3 首帧策略与首帧文字 | `MATCH` | `first_frame` 字段（同上） |
| §1.3 发布正文 | `MATCH` | `publish_copy` 字段（同上） |
| §1.3 字幕重点、断句、强调或展示规则 | `MATCH` | `caption_rules` 字段，非视频形态有专门字段映射表（SKILL_v1.4.md「非视频形态的字段映射」节） |
| §1.3 音乐/音效使用与落位建议 | `MATCH` | `sound_placement` 字段，同样有非视频形态映射 |
| §1.3 评论区首评/互动设计 | `MATCH` | `comment_design` 字段 |
| §1.3 CTA | `MATCH` | `cta_surface` 字段 + CTA 三级接缝机制（「CTA 三级接缝」节） |
| §1.3 标签/话题等平台元素 | `MATCH`（v1_4 新增，闭 B-05） | `hashtags_topics` 字段，`APPLICABLE|NOT_APPLICABLE` 判定，v1_4.yml 第 1877–1884 行（`skill_llm.prompt_template[0].text` 内） |
| §1.3 平台适配说明 | `MATCH` | `platform_variants[]` + `platform_spec_status`；Layer A 数据通路已在 v1_4 接入真实字节（见 THREE_WAY_COMPARISON b) 条） |
| §1.3 发布前检查 | `MATCH` | `release_check`（五条固定检查项） |
| §1.3 发布条件/不应发布条件 | `MATCH`（v1_4 新增单一汇聚字段，闭 B-06） | `release_decision` 字段（`READY_TO_PUBLISH\|HOLD_FOR_FIX\|DO_NOT_PUBLISH`），v1_4.yml 第 1907–1919 行；**但该字段是否真的出现在用户可读正文里，全架构无代码校验**（依赖模型遵守提示词，同型于其余大多数字段） |
| §1.2 不得要求用户先填写完整品牌数据库、账号历史或大型问卷 | `MATCH` | `envelope_check` 只做结构性在场检查，六项字段本身量级有限，非大型问卷 |

## §2 明确不负责

| 标准条款 | 判定 | 说明 |
|---|---|---|
| 不从零决定内容主题、不重做 Creative Tournament、不重写完整脚本、不做拍摄导演方案、不实际剪辑/设计、不自动发布 | `MATCH` | `skill_llm` 独有停止边界明文"不重写脚本或分镜"；无任何工具/HTTP/发布节点（全图 17 节点穷举核对，无外部发布调用） |

## §6/§7 G1 硬门与三层平台适配

| 标准条款 | 判定 | 说明 |
|---|---|---|
| §6.1 Critical Error = 0（含编造事实、UNKNOWN→FACT） | `PARTIAL` | v1_4 新增 `fact_verification` 提供窄范围代码级核验（只核验已登记条目的引用可解析性，不核验陈述真实性，也不能防止模型选择不登记某条陈述——见 S5 复验报告 P0-5/P0-6）。相比 v1_3 的"唯一把关者是模型自己"已有改善，但未达到"Critical Error = 0 由代码独立保证"的完整程度 |
| §7 Layer A 必须带版本、确定性 | `MATCH`（v1_4 新增，闭 B-03） | `ref_projection` 真实字节嵌入，`projection_record` 记录 `path`/`sha256`/`embedded_at` 三元组 |
| §7 不得用 Layer B 冒充 Layer C（无依据当前市场断言） | `MATCH`（v1_4 新增，闭 B-04） | `market_claim_scan` 节点，70 条模式命中即阻断 |

## OUT_OF_CONTRACT（DSL 做了标准不要求的事）

| 项 | 说明 |
|---|---|
| `return_to_script[]`/`return_to_production[]`/`stale_set[]`（Return 闭环与下游失效传播） | Q-COMM-04 §1-§20 全文未要求"向上游发起结构化回改建议"这件事——这是 M4 统一能力接缝的跨组件协作机制，服务的是"PP 发现问题时如何通知 Creative Script/Production Director"，而 Q-COMM-04 的产品合同里用户买的是**给定成片的包装方案**，不涉及是否要向不存在的上游发起回改。这套机制是 M4 工具形态的残留基础设施，不是 P0 作为独立商业 SKU 时用户会感知到的价值 |
| `binding_record`（AC-12 保真绑定记录：`envelope_hash`/`professional_input_hash`/`system_prompt_sha256`/`task_contract_hash` 等） | 纯工程可追溯性记录，不对应标准任何一条产品条款；是 M4 Runtime 集成任务（`V1-M4-CAPABILITY-SEAMS-RUNTIME-INTEGRATION-001`）遗留的治理基础设施 |
| `entry`/`run_mode` 的 `ENTRY-07`/`DERIVE_MODE_AND_PACKAGE` 显式接缝协议 | 服务于"统一能力调用外壳"跨 SKU 路由协议，用户购买 P0 时不会感知到这层协议存在，是 M4 平台层留下的接口形态 |

## 小计

`MATCH`: 13　`PARTIAL`: 2（§1.2 输入命名不对齐、§6.1 Critical Error 未完全代码化）　`MISSING`: 0　`OUT_OF_CONTRACT`: 3
