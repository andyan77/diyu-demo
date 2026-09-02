---
task_id: DIYU-V1-PP-BLOCKER-REMEDIATION-S1-S4-001
based_on_branch: task/pp-architecture-verification-v1
frozen_baseline: content-production/workflows/DIYU_M4_TOOL_PUBLISHING_PACKAGING_v1_3_TEST.yml
frozen_baseline_sha256: daa8365de26f9b280e2ea72707aa85ce445edd2b8bcdaa54350ecce9797b635e
frozen_baseline_sha256_recomputed_at_close: daa8365de26f9b280e2ea72707aa85ce445edd2b8bcdaa54350ecce9797b635e
frozen_baseline_unchanged: true
new_dsl: content-production/workflows/DIYU_M4_TOOL_PUBLISHING_PACKAGING_v1_4.yml
new_dsl_sha256: 82cadc343ecdf9bfd3d8346f94141403d9d2aa95b41b4866f3cd4f2b48f520c3
---

# 改动追溯表

规则：每一处改动必须能说出它关闭的是哪一条 B-xx；说不出就是越界，必须撤销。本表逐条列出，**说不出理由的一处都没有**。

## 冻结资产核验（改动之前先确认哪些不能碰）

| 资产 | 类别 | sha256（改动前 = 改动后） | 结论 |
|---|---|---|---|
| `content-production/workflows/DIYU_M4_TOOL_PUBLISHING_PACKAGING_v1_3_TEST.yml` | workflows | `daa8365d...b635e` | 逐字节未改动 |
| `content-production/skills/packaging-content-for-release-m4/SKILL.md`（m4-v1.3 后继版） | skills | `c56fe9cd...f5574` | 逐字节未改动 |
| `content-production/skills/packaging-content-for-release/SKILL.md`（源 Skill） | skills | `0c91a8ef...7cc07` | 未触碰 |
| `content-production/skills/packaging-content-for-release/references/*.md`（platforms/industry-conditions/examples） | references | 三份文件本身未写入，只读取字节做嵌入投影 | 逐字节未改动 |

三份被列为冻结的资产（workflows、skills、references）均按 CLAUDE.md §6「冻结资产零改动」处理：**需要变化的一律另建新文件承接，不覆盖原文**。这是本次改动布局（v1_4.yml 新文件、SKILL_v1.4.md 新文件、MARKET_CLAIM_PATTERNS_v1.0.json 新文件）的直接原因，不是随意的文件组织选择。

---

## S1 · B-01（配置层）

| # | 文件 | 改了什么 | 关闭哪条 | 为什么必须改 |
|---|---|---|---|---|
| 1 | `DIYU_M4_TOOL_PUBLISHING_PACKAGING_v1_4.yml`，`skill_llm`/`recovery_llm` 共用的 `model.completion_params`（YAML 锚点 `&id001`） | `top_p: 0.8` → `top_p: 1`；新增 `temperature: 0` | B-01 | 把两个可复现性采样参数从"落到隐性默认/部分随机"改为显式钉死。改一次锚点，`recovery_llm` 的 `*id001` 别名自动同步，不用改两处 |
| 2 | 同上，`binding_record.RECORD.completion_params` | `top_p: 0.8` → `1`，新增 `temperature: 0` | B-01（追溯一致性） | `binding_record` 里自报的 `completion_params` 若不同步，会自己撒谎说钉的是旧值；这处改动只是让"自报值"如实反映真实配置，不是新判断 |

**未做、且如实登记为不支持的部分**：`frequency_penalty` / `presence_penalty` / `seed` **未加入** `completion_params`。原因见 `DETERMINISM_SMOKE_v1.0.md`——已从本机真实运行的 `langgenius/deepseek:0.0.20` 插件包（`/models/llm/deepseek-v4-flash.yaml`）核实，该 provider/model 的 `parameter_rules` 只声明了 `temperature`/`max_tokens`/`top_p`/`thinking`/`reasoning_effort`/`response_format` 六项，不含这三项——它们在 Dify LLM 节点层面根本不是这个 provider/model 的合法可配置项，写进 `completion_params` 不会被接受，不存在"钉死"的空间。

---

## S2 · B-02（事实核验代码判定）

| # | 文件 | 改了什么 | 关闭哪条 | 为什么必须改 |
|---|---|---|---|---|
| 3 | `DIYU_M4_TOOL_PUBLISHING_PACKAGING_v1_4.yml` | 新增 code 节点 `fact_verification`，串在 `final_extract` 与 `market_claim_scan`/`returns_adapter` 之间 | B-02 | 现状 `returns_adapter` 只做格式校验，从不解析 `fact_check_status`/`used_fact_refs[]` 内容。新节点是唯一新增的、专门做"引用可解析性"核验的独立单元，可被其余 SKU 复用（见节点内注释与仓库归属提示） |
| 4 | 同上 | 边改写：`final_extract -> fact_verification -> market_claim_scan -> returns_adapter`（原 `final_extract -> returns_adapter` 一条边拆成三段） | B-02 + B-04（结构前提） | 两个新守卫节点必须真正处在专业产出与最终交付之间，否则只是挂在图上的摆设，不构成"阻断" |
| 5 | 同上，`returns_adapter.variables` | `final_text` 的输入源由 `final_extract.output` 改为 `market_claim_scan.verified_text` | B-02 + B-04（结构前提） | 让 `returns_adapter` 解析的是**经过两道守卫处理后**的文本，而不是模型的原始输出——阻断发生在它看到之前 |
| 6 | 同上，`delivery_finalize` | `main()` 新增入参 `fact_gate_blocked`/`market_claim_blocked`（来自 `fact_verification`/`market_claim_scan`），命中时提前返回，`delivery_outcome` 置为 `NOT_DELIVERED_FACT_CHECK_BLOCKED` / `NOT_DELIVERED_MARKET_CLAIM_BLOCKED` / 两者皆中的合并态；`variables` 追加两条对应引用 | B-02(d) + B-04 | 只改 `user_delivery` 文本不够——`delivery_outcome` 本身也必须能被程序化识别为"未交付"，不能让原本判断"技术运行是否成功"的字段继续读成 `DELIVERED`。这是"阻断，不是记一笔然后照常输出"的具体落实 |
| 7 | `skill_llm` 的 **user 角色**消息（`prompt_template[1]`，DSL 自身编写、不派生自任何 `skills/` 冻结资产） | ①「产出结构（三块…）」→「四块」；②在 `---END_M4_RETURNS---` 之后新增 `---M4_FACT_LEDGER---` 块的格式定义（`output_location`/`factual_claim`/`fact_id`，多条空行分隔，无事实性陈述时写 `NONE`）；③「自检三条」→「四条」，新增第 4 条核对 FACT_LEDGER 与 `used_fact_refs[]` 一致 | B-02(a) | 属于第 3 条允许的提示词改动：**为使契约可被代码强制执行而必需**——`fact_verification` 节点要核验引用，前提是模型把 `used_fact_refs[]` 里已有的判断**同时**以机器可解析的格式再登记一遍。没有改变 `used_fact_refs[]` 本身的判据一个字（那部分在 `SKILL_v1.4.md` 里完全未动），只是多要求一份格式化输出 |

**边界说明**：第 7 条动到的是 `prompt_template[1]`（DSL 自己写的运行时接缝契约），**不是** `packaging-content-for-release-m4/SKILL.md`（冻结资产）。核实方法：逐字比对确认 `skill_llm.prompt_template[0].text`（system 角色）在拼接 `SKILL_v1.4.md` 全文 + `"\n---\n\n"` + 原有的"本次运行注入的参考文件片段"投影段之后与 DSL 实际值完全相等（见下方"生成一致性核验"）。

---

## S2 · B-04（无依据市场断言检测）

| # | 文件 | 改了什么 | 关闭哪条 | 为什么必须改 |
|---|---|---|---|---|
| 8 | 新建 `content-production/shared/fact-and-market-guards/MARKET_CLAIM_PATTERNS_v1.0.json` | 独立、带版本号（`1.0`）的模式清单文件，中文 54 条 + 英文 16 条，附 `sync_discipline`/`reuse_note` 字段 | B-04 | 用户明确要求"模式清单外置成独立的、带版本的文件，不要硬编码进节点"。清单覆盖标准 §7 Layer C / G0-04 给出的全部三个反例（"这是目前小红书最流行的标题结构"「现在同类内容很少」「晚上 8:30 是当前最佳发布时间」的同类表述） |
| 9 | `DIYU_M4_TOOL_PUBLISHING_PACKAGING_v1_4.yml` | 新增 code 节点 `market_claim_scan`，内嵌上一条文件此版本号下的字节快照（节点注释里写明来源路径 + sha256 + 同步纪律） | B-04 | Dify code 节点沙箱不能在运行时读取仓库文件（已核实：`dify-sandbox`/`dify-agent-local-sandbox` 均为无出站网络、无仓库文件系统访问的隔离容器），"零改图更新清单"在这套平台上做不到——**如实登记这一限制**，能做到的是"图内清单是仓库真源某个已知版本的完整快照，不允许内容分叉" |
| 10 | 同上 | 命中即改写 `---M4_USER_DELIVERY---` 块为阻断说明（不改 `---M4_ARTIFACT---`），并把 `market_claim_blocked` 一路传到 `delivery_finalize` 强制改写 `delivery_outcome` | B-04 | 与 B-02 第 6 条同一套阻断落实机制，两个守卫节点的返回值形状刻意保持一致，便于以后合并复用 |

---

## S3 · B-05（标签/话题字段）

| # | 文件 | 改了什么 | 关闭哪条 | 为什么必须改 |
|---|---|---|---|---|
| 11 | 新建 `content-production/skills/packaging-content-for-release-m4/SKILL_v1.4.md`（`packaging-content-for-release-m4/SKILL.md` 的后继版本，逐字节保留原文，只增补） | frontmatter 追加 `m4_v1_3_successor`/`remediation_task_id`/`remediates` 字段（版本号 `successor_version: "m4-v1.4"`）；「输出」块在 `author_share_line` 之后新增 `hashtags_topics` 字段（APPLICABLE \| NOT_APPLICABLE + 3–8 个标签／话题，各自标注对应平台机制，禁止编造"当前热门话题"）；「自检」新增第 15 条 | B-05 | 标准 §1.3 第 9 项"标签/话题等平台元素"在 v1.3 的输出契约里全文 grep 零命中。新增字段满足"必须能给出 APPLICABLE/NOT_APPLICABLE 判定"的要求，`NOT_APPLICABLE` 是合法结论、不是漏做 |
| 12 | `DIYU_M4_TOOL_PUBLISHING_PACKAGING_v1_4.yml`，`skill_llm.prompt_template[0].text`（system 角色） | 由 `SKILL.md`（v1.3 后继版）派生改为由 `SKILL_v1.4.md` 派生；尾部"本次运行注入的参考文件片段"投影段一字未改 | B-05 + B-06（承载第 11/13 条改动） | DSL 的 system 角色文本必须实际包含新字段，否则模型永远看不到这个要求 |

---

## S3 · B-06（发布判断单一汇聚字段）

| # | 文件 | 改了什么 | 关闭哪条 | 为什么必须改 |
|---|---|---|---|---|
| 13 | `SKILL_v1.4.md`（同第 11 条文件） | 「输出」块在 `fact_check_status` 之后新增 `release_decision` 字段（`READY_TO_PUBLISH \| HOLD_FOR_FIX \| DO_NOT_PUBLISH`，由 `release_check`/`fact_check_status`/`missing[]` 推导，`fact_check_status = FAIL` 时强制 `DO_NOT_PUBLISH`，**必须原样出现在用户交付块正文里**，明确声明不删除/不顶替既有三个分散信号）；「自检」新增第 16 条 | B-06 | 标准 §1.3 第 12 项"发布条件/不应发布条件"此前判断结果分散在多处、没有汇聚点，且可能只出现在 Return 分支或状态码，用户读不到。新字段只加一个汇聚点，不删除任何既有分散信号 |

---

## S4 · B-03（Layer A 参考文件真实接入）

| # | 文件 | 改了什么 | 关闭哪条 | 为什么必须改 |
|---|---|---|---|---|
| 14 | `DIYU_M4_TOOL_PUBLISHING_PACKAGING_v1_4.yml`，`ref_projection`（template-transform） | 整个 Jinja 模板重写：`platforms.md` 无条件整份字节嵌入；`industry-conditions.md` 按 `subject_domain` 五选一嵌入对应段落（保留原判据的选段粒度，只是把"该不该加载"的描述换成真实字节）；`examples.md` 保留原有的"仅显式请求时加载"门控，整份字节嵌入；每节附 `provenance`（path/sha256/embedded_at） | B-03(a)(b)(d) | 现状 `ref_projection` 只产出"该不该加载"的规则文字，`context.enabled: false`，全图无检索/HTTP/工具节点——Layer A 从未被真正满足过。三份文件均逐字节确认无 `{`/`{{`/`{%` 等 Jinja 特殊字符冲突后直接嵌入原文，未做任何转写 |
| 15 | 同上，`projection_record`（template-transform） | JSON 结构新增 `reference_embedding_method` 字段（如实说明"DSL 构建期字节快照嵌入，非运行时检索"）+ `reference_provenance` 对象（三份文件各自的 path/sha256/embedded_at/loaded_this_run，行业段落额外记 `loaded_section`），`second_attachment_library_built`/`rag_first_layer_built` 继续为 `false` | B-03(b)(c) | 这是"供 AC-11 机器核验"的机读记录，必须真实反映三元组，不能只在 system prompt 的自然语言里写 |

**未做、如实登记的限制**：requirement (c)「读不到时给显式的 UNVERIFIED 并说明原因，不要静默降级」在本设计下的准确含义——因为是构建期快照嵌入（与 system prompt 自身的生成方式同构），"读不到"的失败模式发生在 **DSL 构建/更新阶段**（源文件缺失时生成必须失败、不得产出假装带了引用内容的产物），而不是运行阶段（字节已经烘焙进图里，运行时不存在"读不到"这件事）。这一点已在 `BLOCKER_CLOSURE_v1.0.json` 里如实注明，不假装两个阶段的风险是同一件事。

---

## 生成一致性核验（不是新判断，是核对第 12 条改动做对了没有）

```
skill_llm.prompt_template[0].text  ==  SKILL_v1.4.md 全文 + "\n---\n\n" + 原尾部参考投影段
                                    （sha256 = df4a69b64ba630d31b49d49ece81a7a737451246e29a5bc6ea1652528c7c4f5c）
```
用 `yaml.safe_load` 读出该字段实际值、逐字节比对，结果一致（见 `BLOCKER_CLOSURE_v1.0.json` 的 B-05/B-06 证据段）。

---

## 越界嫌疑（分不清算不算允许的提示词改动，单独列出来问）

以下改动**不追溯到任何单一 B-xx**，但没有它们，"新文件"这个交付形态本身就立不住；判断这些算不算越界，请求 Founder 裁定：

1. **`app.name` / `app.description` 改名**（`DIYU M4 v1.3 TEST` → `DIYU M4 v1.4`，并在 description 里追加一句指向本任务 task_id 与 CHANGE_TRACE 的指针）。理由：同一个 Dify 工作区里两份内容不同却同名的应用会造成误用风险；但这确实是纯标识改动，不是任何一条 B-xx 要求的。
2. **`skill_llm` 节点自身的显示标题**（同上，从 `v1.3 TEST` 改成 `v1.4`）——同一顾虑，纯 UI 标签。
3. **`binding_record.RECORD` 新增 `remediation_task_id` / `remediates_blockers` / `v1_3_frozen_baseline_path` / `v1_3_frozen_baseline_sha256` 四个字段**。理由：这四个字段服务的是"这份自报绑定记录本身能不能被追溯回本次任务与冻结基线"，间接服务全部六条 B-xx 的可审计性，但不是任何单一一条明确要求的产物字段。

---

## 勘误 001 裁定与后续（2026-09-02）

裁定文件：`PP_阻断修复_S1-S4_EXECUTION_PROMPT_v1.0_ERRATA_001.md`
（sha256 `cd07b33843b09752dd63626f97a41ed3f1717dec70b0e074c0a9db00a5f4c72b`，现场复算一致）。

**上述 3 处越界嫌疑：全部判定不越界，保留，不必回退。** 裁定理由：三处均派生自母 Prompt 绝对约束
第 1 条（冻结基线不动、修改写进新文件），且是主动列出请求裁定而非默默纳入——这正是该规则想要
产生的行为。使用边界：`binding_record.RECORD.v1_3_frozen_baseline_sha256` 是**自报值**，
**不得**作为"基线未改动"的证据；该证据只能来自现场复算（本任务开工前/收尾两次复算均为
`daa8365de26f9b280e2ea72707aa85ce445edd2b8bcdaa54350ecce9797b635e`，规则侧亦已独立复算确认一致）。

**S4／B-03 构建期快照：规则侧认定已满足 B-03，不必改。** 防陈旧机制列为跟进项 `FU-01`
（比对图内 `reference_provenance` 记录的 sha256 与仓库源文件当前 sha256，不一致即构建失败或
显式告警），排入阶段二目录重构（S6）随参考文件加载器搬进 `core/` 一并做，不阻断本任务，
不影响本轮实测读数可信度。

**B-01 empirical 冒烟结果**：见 `DETERMINISM_SMOKE_v1.0.md` 勘误 001 补验部分；结论与差异性质
描述均登记在该文件，本文件不重复。

以上三处如果判定越界，撤销方式很直接：`app.name`/`app.description`/`skill_llm.title` 三处回退成 v1.3 原文；`binding_record.RECORD` 删除这四个新增字段（不影响其余任何逻辑，因为它们只是自报声明，不参与任何路由或阻断判断）。
