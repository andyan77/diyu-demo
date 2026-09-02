# PP 架构复验报告 v1.0（S5 · 独立复验，非复读）

```yaml
task_id: DIYU-V1-PP-ARCHITECTURE-REVERIFICATION-001
report_date: "2026-09-02"
zero_model_calls: true
zero_dsl_or_code_changes: true
nature: 独立复验——BLOCKER_CLOSURE_v1.0.json 与 CHANGE_TRACE.md 只作"待验证声明"读取，
  不作证据；本报告全部结论重新从 v1_4 的图本身、插件包源码与仓库源文件独立推导；
  本轮复验与 S1-S4 施工同源（同一协作身份），独立性不靠换会话保证，改用逐条出处强制
  （节点名/字段路径/行号），指不到 v1_4 具体位置的结论一律记为 NOT_VERIFIED，不得记为 CLOSED。
scope: R0~R5（R5 为结转清单 CF-01~CF-05 逐条处置，追加于原 R0~R4 之后）
tested_source: content-production/workflows/DIYU_M4_TOOL_PUBLISHING_PACKAGING_v1_4.yml
tested_source_sha256: 82cadc343ecdf9bfd3d8346f94141403d9d2aa95b41b4866f3cd4f2b48f520c3
tested_source_bytes: 205504
acceptance_baseline: Q-COMM-04_P0_内容发布包装助手商业化评价验收标准_v1.0.md
acceptance_baseline_sha256: 55bcfa4001668dd23614459cb502aca30286e62894670a911a68de17528cb397
blocking_list_source: pp-architecture/BLOCKING_LIST_v1.0.json
blocking_list_sha256: 8407e363adcd6386a0ff1c5c7ae0767cfebbbdc799a8ceb22352204621237d94
frozen_v1_3_baseline: content-production/workflows/DIYU_M4_TOOL_PUBLISHING_PACKAGING_v1_3_TEST.yml
frozen_v1_3_baseline_sha256_at_open: daa8365de26f9b280e2ea72707aa85ce445edd2b8bcdaa54350ecce9797b635e
```

治理绑定核验（开工前现场复算）：Q-COMM-04 与 BLOCKING_LIST_v1.0.json 两份文件 sha256 与授权值逐字节一致（见落盘前的 shell 复算记录，无偏差，未触发停止条件）。

方法说明：全部结论来自对 v1_4 全文（3326 行）逐节点、逐边的 `yaml.safe_load` 结构化解析，对新增/变更节点的 Python 代码用**独立构造的测试向量**（不复用 BLOCKER_CLOSURE 已有测试用例）直接 `exec` 执行验证行为，对嵌入字节做逐文件 `diff`/`sha256` 核对，并读取本机实际部署的 `langgenius/deepseek:0.0.20@850efe73…` 插件包源码（非文档、非猜测）。零模型调用、零 DSL 或代码改动。

---

## R0 · 原样重跑 P0-1 ~ P0-8

### P0-1 冻结被测源

`content-production/workflows/DIYU_M4_TOOL_PUBLISHING_PACKAGING_v1_4.yml` 现场复算 sha256 = `82cadc343ecdf9bfd3d8346f94141403d9d2aa95b41b4866f3cd4f2b48f520c3`，205504 字节，与授权值逐字节一致；`Q-COMM-04` 与 `BLOCKING_LIST_v1.0.json` 同样复算一致。

**状态：DONE**

### P0-2 可抽取性清单

结构与 v1_3 基本一致（自包含 YAML、system prompt 为已烘焙静态字符串、无运行时上游硬依赖、`environment_variables` 仍为空数组、仍只经由 `langgenius/deepseek` 插件间接调用 DeepSeek）。**变化点**：构建期（非运行时）依赖从 1 份（`SKILL.md`）扩为 3 份——

| 构建时依赖 | 用途 |
|---|---|
| `content-production/skills/packaging-content-for-release-m4/SKILL_v1.4.md` | system prompt 派生源（`packaging-content-for-release-m4/SKILL.md` 的纯增量后继版，见 R1·B-05/B-06） |
| `content-production/skills/packaging-content-for-release/references/{platforms,industry-conditions,examples}.md` | `ref_projection` 构建期字节快照嵌入源（见 R1·B-03） |
| `content-production/shared/fact-and-market-guards/MARKET_CLAIM_PATTERNS_v1.0.json` | `market_claim_scan` 节点内嵌模式清单的字节快照源，且明确登记为可供 Matrix/Campaign/Content Brief/Creative Script 复用的共享资产（见 R1·B-04） |

两个新增节点（`fact_verification`／`market_claim_scan`）代码只用标准库（`json`/`re`），未引入新的运行时依赖或外部服务；Dify 平台特性依赖清单（workflow 图引擎／code 沙箱／template-transform／`completion_params` 直通／`{{#..#}}` 插值／YAML 锚点／Marketplace 插件）与 v1_3 相同,未新增。

**判定：`EXTRACTABLE_WITH_DELTA`（与 v1_3 相同判定，构建时依赖清单需相应更新）**

**状态：DONE**

### P0-3 架构一致性矩阵

**(a) §1.3 十二项标准输出对象**——相对 v1_3 报告的两处变化：

- 第 9 项「标签/话题等平台元素」：v1_3 全文穷举 grep 零命中；v1_4 **新增 `hashtags_topics` 字段**（`APPLICABLE|NOT_APPLICABLE` + 3–8 个标签/话题，各自标注平台机制），已独立确认写入 `skill_llm` 实际发送的 system prompt 文本（见 R1·B-05）。**原缺口关闭。**
- 第 12 项「发布条件/不应发布条件」：v1_3 判断结果分散在 `release_check`/`fact_check_status`/`missing[]`/`component_return` 分支，无单一字段；v1_4 **新增 `release_decision`** 单一显式汇聚字段（`READY_TO_PUBLISH|HOLD_FOR_FIX|DO_NOT_PUBLISH`），明文要求由三者推导且 `fact_check_status=FAIL` 时强制 `DO_NOT_PUBLISH`，并要求原样出现在用户交付块正文里；既有分散信号原样保留未删除（见 R1·B-06）。**原缺口在"是否存在单一汇聚字段"层面关闭；但该字段是否真的出现在最终用户可读正文，全架构范围内没有任何代码节点校验——完全依赖模型遵守提示词，与其余大多数专业判据字段（标题/封面/CTA 等）的执行方式一致，不是这一项独有的新缺口，但值得与"字段是否存在"分开记录。**

其余 10 项（含第 5/6/10 项已有的字段映射表判定机制）与 v1_3 报告核对结果一致，未发生变化。

**(b) §7 三层平台适配**——**最实质的变化**：

- **Layer A（Platform Hard Contract）**：v1_3 中 `ref_projection` 只产出"该不该加载"的规则文字，`references/platforms.md` 等文件从未被任何节点实际读取，`context.enabled: false`，全图无检索/HTTP/工具节点，导致 Layer A 结构性地永远落在 `PLATFORM_SPEC_UNVERIFIED` 分支。**v1_4 独立验证：`ref_projection` 模板现在真实、按字节嵌入 `platforms.md` 全文、`industry-conditions.md` 按 `subject_domain` 选段、`examples.md` 全文（仅显式请求时）**——经逐段 `diff` 核对，嵌入内容与仓库当前源文件**逐字节一致**（含 5 个行业段落逐一核对），`projection_record` 记录的三元组 sha256 与源文件当前 sha256 现场复算一致（详见 R1·B-03）。**Layer A 的"数据通路未接入图内"这一原始缺口已关闭**——这是本轮复验里唯一使 P0-3(b) 判定发生方向性变化的一项。
- **Layer B（Platform Native Heuristics）**：与 v1_3 相同，仍是提示词主体的一部分，未做成独立可寻址结构单元，未变。
- **Layer C（Current Market Signal）**：图内仍无法获取实时市场数据，"不运行"仍是结构性成立；但 v1_3 报告指出的关键缺口——"不得用 Layer B 冒充 Layer C"（即无依据当前市场断言）**没有任何代码级校验**——**v1_4 独立验证：新增 `market_claim_scan` 代码节点，对 `---M4_USER_DELIVERY---` 块做 70 条模式（中文 54 + 英文 16）命中检测，命中即改写正文为阻断说明并强制 `delivery_outcome` 变为未交付态**（独立单测见 R1·B-04）。**该缺口已关闭。**

**(c) 六项外壳必填（闸还是注释）**：`envelope_check`／`gate_sufficiency`／`component_return` 三个节点代码逐字节比对 v1_3 **完全相同**——仍是真实结构性硬闸（六个字面 key 在场检查，缺失即 `INSUFFICIENT` 并短路到 `component_return`，不进 `skill_llm`），语义单薄（`vacuity_flags`）仍降级为软判断、非硬门，判定与 v1_3 一致，未变。

**状态：DONE**

### P0-4 确定性配置审计

`skill_llm`/`recovery_llm` 共用 `completion_params`（YAML 锚点 `&id001`/`*id001`，全文档 grep 确认仅此一处定义、一处引用，两节点字节级共享）：

```yaml
max_tokens: 384000
reasoning_effort: low
temperature: 0        # v1_3 为未设置（零命中）
thinking: true
top_p: 1              # v1_3 为 0.8
```

`frequency_penalty`/`presence_penalty`/`seed`：全文档 grep 零命中，**独立核实**本机实际部署的 `langgenius/deepseek-0.0.20@850efe73…` 插件包 `models/llm/deepseek-v4-flash.yaml` 的 `parameter_rules` 只声明六项（`temperature`/`max_tokens`/`top_p`/`thinking`/`reasoning_effort`/`response_format`），确认这三项在此 provider/model 组合下**确实不是合法可配置项**，不存在"漏钉"的空间——这一核实独立于 BLOCKER_CLOSURE 的同一断言，直接读取插件包 yaml 得到相同结论。

**新发现（与 R2 共享同一根因，此处仅作 P0-4 范围内的交叉引用，完整分析见 R2）**：`temperature`/`top_p` 虽然在 DSL 层面被钉死为 `0`/`1`，但本机部署的插件包源码（`models/llm/llm.py`）在 `thinking` 被规范化为启用状态时，会在构造上游请求前将这两个参数从 `model_parameters` 中移除，从未发送给 DeepSeek API。**即：v1_4 对"确定性配置"这一项在 DSL 声明层面确有改善，但在插件运行时层面，这次配置改动对最终发给模型的请求没有可验证的实际效果**——这一点原始报告与 BLOCKER_CLOSURE 均未发现，详见 R2。

**状态：DONE（含一项对原判据"确定性配置已按 provider 支持范围钉死"的重要限定，见 R2）**

### P0-5 事实溯源链路审计

v1_3 结论：从"用户登记的事实"到"最终输出文案"之间**不存在任何独立于模型的强制性绑定、校验或阻断节点**——`returns_adapter` 只做格式校验，从不解析 `fact_check_status`/`used_fact_refs[]`。

**v1_4 独立验证的变化**：新增 `fact_verification` 代码节点，串在 `final_extract` 与 `market_claim_scan`/`returns_adapter` 之间（边：`final_extract → fact_verification → market_claim_scan → returns_adapter`，逐边核对与 v1_3 相比新增两段、无删除）。用**独立构造**（非复用 BLOCKER_CLOSURE 用例）的测试向量直接执行该节点代码，确认：

1. 它解析 `---M4_FACT_LEDGER---` 块，对每条登记的 `fact_id` 检查是否能在本次原始输入（`capability_call + professional_input`）文本中找到；
2. 找不到、或 `FACT_LEDGER` 块缺失/为空/解析失败，**代码判定** `fact_check_status_code = FAIL`，与模型自报的 `fact_check_status` 字段互相独立比对（不一致时置 `fact_check_mismatch`）；
3. 判定 FAIL 时，**代码真实改写** `---M4_USER_DELIVERY---` 块为阻断说明（`_replace_between`，非仅并列输出一个状态字段）；
4. 该阻断状态（`fact_gate_blocked`）继续向下游传递，`delivery_finalize` **独立执行验证**确认：命中时强制 `delivery_outcome = NOT_DELIVERED_FACT_CHECK_BLOCKED`（或两者皆中的合并态），不是"记一笔然后照常交付"。

**因此 P0-5 原有的"唯一把关者是模型自己"这一结论不再完全成立**——现在有一个真实的、独立于模型自报的代码判定环节。

**但需要精确限定这一改善的边界（避免读成"事实核验已被彻底代码化"）**：

- `fact_verification` 只做**引用可解析性**核验——判断 `fact_id` 字符串是否能在原始输入文本中被找到，**不判断、也无法判断该事实性陈述本身是否真实**；这一点节点自身的 `fact_check_scope_note` 字段明文披露，不是隐藏限制。
- 更重要的是：该核验**只审计模型主动登记进 `FACT_LEDGER` 的条目**。如果模型在正文里写了一句事实性陈述，但**没有把它登记进 `FACT_LEDGER`**（既不citation也不在 `used_fact_refs[]` 提及），`fact_verification` 完全不会检查这句话——它只查"已登记条目的编号是否可解析"，不查"正文里是否存在未登记的事实性陈述"。这意味着：**模型主动隐瞒登记，仍然是这套代码判定看不见的路径**，与 v1_3 时代同样无解。
- 好消息：`FACT_LEDGER` 块整体缺失或格式损坏（模型完全没有按格式产出）时，**默认按 fail-closed 处理**（`ledger_status = PARSE_FAILED` → `critical_error = True` → 阻断），比 v1_3 时代（无此概念，缺失什么都不会被察觉）更安全。

**状态：DONE（架构缺口部分关闭：新增一层真实的、窄范围的代码级事实核验；未关闭部分：模型可通过不登记的方式完全绕过核验，如实登记，不因新增节点而夸大改善幅度）**

### P0-6 UNKNOWN 传播审计

v1_3 结论：全文档穷举 `UNKNOWN` grep 仅一处命中（`envelope_check` 对 `platform` 字段的判断），UNKNOWN（事实缺失）状态没有被设计成可传播、可核验的第一等状态。

**v1_4 独立复核**：`UNKNOWN` 关键词命中位置未变（`envelope_check` 同一处，代码字节级未改）。`fact_verification` 节点新增后，对"UNKNOWN 被悄悄变成 FACT"这一具体子问题提供了**部分、非完整**的代码防线——见 P0-5 的边界限定：**只覆盖"编号对不上号"这一种造假方式，不覆盖"压根不登记"这一种**。这与 v1_3 报告的核心结论（UNKNOWN 不是第一等可传播状态）本质上仍然成立，只是"模型编造一个带假编号的事实"这一具体子路径现在会被拦，"模型编造一个不登记的事实"这一子路径仍然无解。

**状态：DONE（结论方向与 v1_3 一致，新增一条窄范围的部分缓解路径，非结构性解决）**

### P0-7 裸入口结构判定

`envelope_check`／`gate_sufficiency`／`component_return` 三个节点代码逐字节比对 v1_3 **完全相同**（Python 代码字符串相等性直接验证，非目测）。因此 v1_3 报告发现的问题——验收标准 §1.2 最低合法输入的中文自然语言五要素，与 `envelope_check` 实际做字面英文 key 匹配的六项 `REQUIRED`（`content_body_or_beats`/`content_promise`/`explicit_non_promise`/`facts_registered`/`cta_contract`/`asset_publish_permission`）**命名不对齐**，裸给 Q-COMM-04 定义的最低输入有较高概率被结构性拦在 `component_return`、打不到 `skill_llm`——**这一发现原样适用于 v1_4，未被本次改动触及，也未被修复**。

这不是 B-01~B-06 六条阻断清单里的项目（原报告把它作为"进入 P0-8 判定时需一并考虑"的输入契约对齐问题登记，未列为独立阻断），本轮复验同样不新开一条阻断，但需要在设计实测输入时保留这一提醒：**用 Q-COMM-04 §1.2 字面自然语言组织输入，需要额外做一次"中文语义 → 六个英文 key"的适配翻译，否则大概率在到达 `skill_llm` 之前就被短路**。

**状态：DONE（发现与 v1_3 相同，未变，非新增缺口）**

### P0-8 判定与阻断清单

见下方 R4。

**状态：DONE**

---

## R1 · B-01 ~ B-06 逐条独立复验

方法：不采信 BLOCKER_CLOSURE 的自述证据；对每条阻断，直接从 v1_4 的图结构（`yaml.safe_load` 解析节点/边/变量引用链）与代码逻辑（独立测试向量 `exec` 执行）重新推导。

### B-01 · 配置层（温度等采样参数未钉死）

| 项 | 独立复验结果 |
|---|---|
| DSL 声明 | `completion_params` 现场核对：`temperature: 0`、`top_p: 1`（较 v1_3 的未设置/`0.8` 确有改动）；`frequency_penalty`/`presence_penalty`/`seed` 未加入 |
| provider 支持性 | 独立读取本机部署的 `langgenius/deepseek-0.0.20@850efe73…/models/llm/deepseek-v4-flash.yaml`（该文件第 14–77 行 `parameter_rules` 全量），恰好六项，不含上述三项——**独立确认**该三项在此 provider/model 下确实不可配置，非漏钉 |
| 锚点共享 | `&id001`/`*id001` 全文档仅一次定义、一次引用，`skill_llm`/`recovery_llm` 字节级共享，非声称 |
| **新发现** | 本机部署的插件包源码 `models/llm/llm.py` 的 `_normalize_model_parameters()` 在 `thinking` 启用（v1_4 当前配置）时，**会把 `temperature`/`top_p`/`presence_penalty`/`frequency_penalty` 全部从请求参数里剔除，从不发给上游 API**（详见 R2）——这意味着 DSL 层面钉死的 `temperature=0`/`top_p=1` 在当前配置下对最终发给模型的请求**没有可验证的效果** |

**我的独立复验结论**：**状态标签维持 `CLOSED_AT_CONFIG_LAYER_ONLY`，与 BLOCKER_CLOSURE 一致**——配置本身确实已按声明写入且确实是 provider 支持范围内能做到的最大值，这一"配置层已尽力"的事实成立，标签不因新发现而改变。

**但与 BLOCKER_CLOSURE 存在一项实质性根因分歧，单独列出**：BLOCKER_CLOSURE／`DETERMINISM_SMOKE_v1.0.md` 把 2/3 次运行 31% 的篇幅差异归因于"温度=0 的贪心解码在这套 provider/model 栈上不保证字节级确定性……浮点非结合性 + `thinking` 推理段的已知成因"——这一表述暗示"`temperature=0` 确实被应用了，只是应用后仍有微小的浮点误差累积"。**我的独立复验（读插件源码，非猜测）证明实际情况更严重**：`temperature`/`top_p` 在当前 `thinking: true` 配置下**根本没有被发送到 DeepSeek API**，31% 的篇幅摆动源头很可能主要是 DeepSeek 服务端在完全不受 Dify 侧任何采样参数约束下的默认行为，而不是"钉死之后仍有的微小浮点误差"。这是一个更根本、更大幅度的解释，**不是同一件事的更精确表述，而是指向了一个 BLOCKER_CLOSURE 未曾提及的机制层**。详见 R2。

### B-02 · 事实核验代码判定

**独立复验方法**：从 v1_4 的图边直接确认 `fact_verification` 的位置（`final_extract → fact_verification → market_claim_scan → returns_adapter`），从 `returns_adapter.variables` 确认其 `final_text` 输入来自 `market_claim_scan.verified_text`（间接串联到 `fact_verification.verified_text`，非旁路）；用**独立构造**的 4 组测试向量（可解析引用/不可解析引用/正常文本不受影响/`market_claim_scan` 联动）直接 `exec` 执行 `fact_verification`、`market_claim_scan`、`delivery_finalize` 三个节点代码，实测验证：

- `fact_id` 可在原始输入中找到 → `fact_gate_blocked = false`（未误伤）；
- `fact_id` 无法找到 → `fact_gate_blocked = true`，且 `verified_text` 中 `---M4_USER_DELIVERY---` 块被真实替换为阻断说明；
- 该 `fact_gate_blocked` 信号继续传给 `delivery_finalize`（独立于 `returns_adapter` 之外单独接线：`delivery_finalize.variables` 直接引用 `fact_verification.fact_gate_blocked`），执行后确认 `delivery_outcome` 被强制改写为 `NOT_DELIVERED_FACT_CHECK_BLOCKED`。

**结论：CLOSED——独立确认，与 BLOCKER_CLOSURE 一致。** `returns_adapter` 本身仍不解析 `fact_check_status`（与 v1_3 相同，代码字节级比对确认未变），但 B-02 的修复方式是新增独立节点而非改造 `returns_adapter`，效果链路完整、真实生效，不是挂在图上的摆设。

**限定**（非"不一致"，是精度补充）：见 P0-5——只核验已登记条目的引用可解析性，不核验陈述真实性，也不能防止模型选择不登记某条陈述。BLOCKER_CLOSURE 的 `fact_check_scope_note` 证据段本身已如实披露此限定，我的独立复验确认这一自我披露准确，未发现夸大。

### B-03 · Layer A 参考文件真实接入

**独立复验方法**：不信任声称的 sha256 匹配，直接用 `yaml.safe_load` 解析出 `ref_projection` 模板字符串，提取三段 `---8<---` 标记之间的嵌入内容，与仓库当前源文件做**逐字节 `diff`**（非仅比对 hash）：

| 文件 | diff 结果 |
|---|---|
| `platforms.md`（全文） | 仅结尾换行符处理差异（提取方式产生的伪差异），内容逐字节一致 |
| `industry-conditions.md`（5 个行业段落，逐段独立提取比对） | 5 段全部逐字节一致，服装/餐饮/知识付费/动漫/户外无一遗漏或改写 |
| `examples.md`（全文） | 同 platforms.md，仅结尾换行符伪差异，内容逐字节一致 |

`projection_record` 节点记录的三元组（`path`/`sha256`/`embedded_at`）与仓库源文件**现场复算 sha256** 逐一核对：`86fc2cc7...` `b085f121...` `635c86e1...` 三个值均与 `find`+`sha256sum` 现场结果一致——**当前时刻嵌入内容与仓库源文件不仅"嵌了"，而且"嵌对了、没有过期"**（这同时是跟进项 FU-01 关注的"是否漂移"这一子问题在**本次复验时点**的答案：未漂移；FU-01 要解决的是"未来"是否会漂移而无人知道，不是当前是否已经漂移）。

**结论：CLOSED——独立确认，与 BLOCKER_CLOSURE 一致。**

### B-04 · 无依据当前市场断言检测

**独立复验方法**：不满足于"70 条模式测过"这句话，直接用 Python 把 `market_claim_scan` 节点代码里硬编码的 `MARKET_CLAIM_PATTERNS_ZH`（54 条）/`MARKET_CLAIM_PATTERNS_EN`（16 条）两个列表，与仓库外部文件 `content-production/shared/fact-and-market-guards/MARKET_CLAIM_PATTERNS_v1.0.json` 的 `patterns.zh`/`patterns.en` 数组做**列表级相等性比较**（非仅 sha256）：两份列表逐项相同，无缺漏、无窜改。另用独立构造的测试文本验证：命中模式的文本被正确阻断（`market_claim_blocked=true`，正文被替换），不含模式的干净文本不受影响（`market_claim_blocked=false`）。`delivery_finalize` 独立执行确认命中时 `delivery_outcome` 被强制改写为 `NOT_DELIVERED_MARKET_CLAIM_BLOCKED`。

**结论：CLOSED——独立确认，与 BLOCKER_CLOSURE 一致。**

### B-05 · 标签/话题字段

**独立复验方法**：不满足于"字段在 SKILL_v1.4.md 里"，直接用 `yaml.safe_load` 提取 `skill_llm.prompt_template[0].text`（即实际发给模型的 system prompt 全文，sha256 现场复算 = `df4a69b6...`，与 BLOCKER_CLOSURE 声称值一致），确认该文本**逐字节等于** `SKILL_v1.4.md` 全文 + `"\n---\n\n"` + 原尾部参考投影段说明（`sys_text.startswith(skill_md) == True`，且 `tail` 精确等于预期的过渡文本）——这证明 `hashtags_topics` 字段要求**确实进入了实际发给模型的 prompt**，不是只存在于一份未被引用的源文件里。另确认自检第 15 条同时存在。

**结论：CLOSED——独立确认，与 BLOCKER_CLOSURE 一致。**

### B-06 · 发布判断单一汇聚字段

**独立复验方法**：同 B-05 的 system prompt 逐字节核对，确认 `release_decision` 字段定义（三态枚举、推导规则、`fact_check_status=FAIL` 强制 `DO_NOT_PUBLISH`、明文要求"必须原样出现在用户交付块正文里"、明文声明不删除既有分散信号）**确实进入实际发给模型的 prompt**。自检第 16 条同时存在。用 `diff` 核对 `SKILL_v1.4.md` 相对冻结的 `packaging-content-for-release-m4/SKILL.md`（sha256 `c56fe9cd...` 未变）**只有纯增量**（除 1 行版本号字符串外，无任何删除/修改，全部改动为追加）。

**结论：CLOSED——独立确认，与 BLOCKER_CLOSURE 一致。**

**需要单独强调的一点，呼应任务给出的怀疑点"汇聚字段存在 ≠ 它出现在用户可读正文里"**：全文档搜索确认，**没有任何代码节点校验 `release_decision`（或其取值）是否真的出现在最终 `---M4_USER_DELIVERY---` 正文里**——"必须原样出现"这一要求只存在于提示词层面，一旦模型不遵守，架构里没有任何东西会发现或拦截。这与 B-02/B-04（都拿到了独立代码节点强制执行）形成明显反差。**这不构成"B-06 未关闭"的判断**——B-06 原始定义的缺口是"没有单一汇聚字段"，这一缺口已经关闭；但如果未来标准要求"汇聚结论必须真的出现在正文里"这件事本身要有代码保证，这仍然是一个待办项，只是不属于 B-06 的原始范围。

### R1 小结

| ID | 我的独立复验状态 | 与 BLOCKER_CLOSURE 状态标签是否一致 | 备注 |
|---|---|---|---|
| B-01 | `CLOSED_AT_CONFIG_LAYER_ONLY` | 一致 | **根因诊断存在实质分歧**，见上文与 R2 |
| B-02 | `CLOSED` | 一致 | 独立单测通过；范围限定已由节点自身披露 |
| B-03 | `CLOSED` | 一致 | 逐字节 diff 独立确认，非仅 hash |
| B-04 | `CLOSED` | 一致 | 模式清单列表级相等性独立确认 |
| B-05 | `CLOSED` | 一致 | system prompt 逐字节核对确认字段真实送达模型 |
| B-06 | `CLOSED` | 一致 | 同上；另指出"正文实际出现"仍无代码校验，非重新开放 B-06 |

**状态标签层面：0 条不一致。根因/精度层面：1 条实质分歧（B-01），2 处补充限定（B-02 范围、B-06 执行层面），均非推翻 BLOCKER_CLOSURE 已给出的状态，而是更精确的成因与边界刻画。**

### R1 附录 · 出处索引（逐条结论 → v1_4.yml 具体位置，当场读出，非引用 S1-S4 自述）

本表把 R0/R1 每一条关键结论指回 `content-production/workflows/DIYU_M4_TOOL_PUBLISHING_PACKAGING_v1_4.yml`（下称"本文件"）的节点名/字段路径/行号——三者任一即可定位，此处尽量三者并列。行号为本次复验用 `Read` 工具读取时的文件内行号（对同一份 sha256 已复算确认的文件，行号是稳定坐标，非概略估计）。

| 结论 | 出处（节点名 / 字段路径 / 行号） |
|---|---|
| `completion_params`：`temperature: 0`、`top_p: 1`、`thinking: true`、`reasoning_effort: low`、`max_tokens: 384000` | 本文件第 1216–1222 行，`model: &id001` 锚点定义（`skill_llm` 节点内） |
| `recovery_llm` 与 `skill_llm` 共用同一 `completion_params` | 本文件第 2795 行，`model: *id001`（`recovery_llm` 节点内） |
| 全文档 `temperature`/`top_p` 仅上述两处引用，`frequency_penalty`/`presence_penalty`/`seed` 零命中 | 本次复验对本文件全文 grep 现场执行，见 R0·P0-4 |
| 边：`final_extract → fact_verification` | 本文件第 154–160 行，边 id `final_extract-source-fact_verification-target` |
| 边：`fact_verification → market_claim_scan` | 本文件第 161–171 行，边 id `fact_verification-source-market_claim_scan-target` |
| 边：`market_claim_scan → returns_adapter` | 本文件第 172–182 行，边 id `market_claim_scan-source-returns_adapter-target` |
| `fact_verification` 节点：解析 `FACT_LEDGER`、判定 `fact_check_status_code`、命中时改写 `verified_text` | 本文件第 2290–2493 行（`id: fact_verification` 在第 2481 行） |
| `market_claim_scan` 节点：70 条模式扫描、命中改写 `verified_text` | 本文件第 2494–2630 行（`id: market_claim_scan` 在第 2618 行） |
| `returns_adapter.variables.final_text` 取自 `market_claim_scan.verified_text`（非 `final_extract.output`） | 本文件第 2742–2745 行 |
| `delivery_finalize.variables` 直接引用 `fact_verification.fact_gate_blocked` 与 `market_claim_scan.market_claim_blocked` | 本文件第 2944–2951 行 |
| `delivery_finalize` 代码：命中即强制 `delivery_outcome` 为 `NOT_DELIVERED_FACT_CHECK_BLOCKED`/`NOT_DELIVERED_MARKET_CLAIM_BLOCKED`/合并态 | 本文件第 2869–2897 行（`id: delivery_finalize` 在第 2953 行） |
| `ref_projection`：`platforms.md` 全文字节嵌入 | 本文件第 502–651 行（起止标记 `---8<--- platforms.md 全文开始/结束 ---8<---` 分别在第 518、651 行） |
| `ref_projection`：`industry-conditions.md` 按 `subject_domain` 五选一段落嵌入 | 本文件第 653–730 行 |
| `ref_projection`：`examples.md` 全文嵌入（仅显式请求时） | 本文件第 741–1087 行（起止标记在第 751、1087 行） |
| `projection_record`：`reference_provenance` 三元组（`path`/`sha256`/`embedded_at`） | 本文件第 1129–1210 行（`id: projection_record` 在第 1197 行） |
| `envelope_check.REQUIRED` 六项字面 key，与 v1_3 字节相同 | 本文件第 313–315 行（`id: envelope_check` 在第 455 行） |
| `gate_sufficiency` 条件：`envelope_check.can_run == 'true'` | 本文件第 469–477 行（`id: gate_sufficiency` 在第 484 行） |
| `hashtags_topics` 字段定义（`APPLICABLE|NOT_APPLICABLE` + 3–8 个标签） | 本文件第 1877–1884 行（`skill_llm.prompt_template[0].text` 内，即实际 system prompt） |
| `release_decision` 字段定义（三态枚举、`fact_check_status=FAIL` 强制 `DO_NOT_PUBLISH`、须原样出现在用户交付块正文） | 本文件第 1907–1919 行（同上，`skill_llm.prompt_template[0].text` 内） |
| 自检第 15 条（`hashtags_topics`）、第 16 条（`release_decision`） | 本文件第 2098–2106 行 |
| `M4_FACT_LEDGER` 四块产出结构定义（`output_location`/`factual_claim`/`fact_id`） | 本文件第 2213–2223 行（`skill_llm.prompt_template[1]`，`role: user`，起始于第 2132 行） |
| `skill_llm.prompt_template[0].text` 逐字节等于 `SKILL_v1.4.md` 全文 + 分隔符 + 参考投影尾段 | 本次复验用 `yaml.safe_load` 现场提取该字段并与 `content-production/skills/packaging-content-for-release-m4/SKILL_v1.4.md` 现场 `diff`，见 R1·B-05/B-06 |
| `MIN_ARTIFACT_CHARS = 400`（`returns_adapter` 内唯一长度常量） | 本文件第 2642 行 |
| `packaging_routes[]` "数量由是否存在真实取舍决定，不固定、不硬编码" | 本文件第 1850 行 |
| `caption_rules` 查表不到则写定性要求、不得自定数字 | 本文件第 1864–1866 行 |
| 数值型平台参数拿不到时"不得自己编一个数""不要留空，改用定性制作要求" | 本文件第 1507–1535 行（"三种拿不到的情况"表 + 后续说明）；同一规则在内嵌 `platforms.md` 文本中重复出现于第 610–628 行 |

（R2 的插件参数剔除发现，出处为本机部署文件而非 v1_4 本身，已在 R2(a) 正文标注完整路径与被剔除代码片段，此处不重复列入本表。）

---

## R2 · 采样参数是否真的生效（新增调查）

### a) thinking:true 时，temperature/top_p 是否仍被传递给上游 API？

**静态可判，结论明确：不会。**

独立读取本机实际部署、与 DSL `dependencies` 声明的 `marketplace_plugin_unique_identifier: langgenius/deepseek:0.0.20@850efe73fb62bbe7ab2229116086596596297a77174fb86f73e1363b99a24116` 完全一致（路径中的插件标识符逐字核对）的插件包源码 `models/llm/llm.py`（本机路径：`/home/faye/dify/docker/volumes/plugin_daemon/cwd/langgenius/deepseek-0.0.20@850efe73.../models/llm/llm.py`）：

- `_V4_MODELS`／`_THINKING_UNSUPPORTED_PARAMETERS` 声明：该文件第 25–31 行
- `_normalize_model_parameters()` 完整逻辑：该文件第 126–144 行
- `_invoke()` 无条件调用该方法：该文件第 46 行（`self._normalize_model_parameters(model, model_parameters)`，在构造请求、调用 `super()._invoke()` 之前）

```python
_V4_MODELS = ("deepseek-v4-flash", "deepseek-v4-pro")
_THINKING_UNSUPPORTED_PARAMETERS = (
    "temperature", "top_p", "presence_penalty", "frequency_penalty",
)

@classmethod
def _normalize_model_parameters(cls, model, model_parameters):
    if model not in cls._V4_MODELS:
        return
    thinking = model_parameters.get("thinking", True)
    if isinstance(thinking, bool):
        thinking = {"type": "enabled" if thinking else "disabled"}
        model_parameters["thinking"] = thinking
    if not isinstance(thinking, dict):
        return
    if thinking.get("type") == "disabled":
        model_parameters.pop("reasoning_effort", None)
        return
    if thinking.get("type") == "enabled":
        for parameter in cls._THINKING_UNSUPPORTED_PARAMETERS:
            model_parameters.pop(parameter, None)
```

`_invoke()` 在构造请求前无条件调用 `self._normalize_model_parameters(model, model_parameters)`。`deepseek-v4-flash` 在 `_V4_MODELS` 内；v1_4 的 `completion_params.thinking: true` 会被规范化为 `{"type": "enabled"}`；命中 `enabled` 分支后，`temperature`/`top_p`/`presence_penalty`/`frequency_penalty` **四项被逐个 `pop()` 移除**，此后这个被修改过的 `model_parameters` 才继续传给父类去构造对 `https://api.deepseek.com` 的实际请求。

**这不是文档声明，是这台机器上实际运行的插件包可执行代码本身**——可反复静态复核，不依赖任何一次真实调用。**结论：v1_4 DSL 里显式设置的 `temperature: 0`、`top_p: 1`，在当前 `thinking: true` 配置下，从未被发送到 DeepSeek API。**

### b) 插件包/provider 声明里，是否有关于推理段确定性的说明？

**静态可判，结论：没有找到任何此类说明。** 通读插件包 `README.md`、`provider/deepseek.py`、`models/llm/deepseek-v4-flash.yaml`，以及对 `determin`/`reproduc`/`random`/`stable`/`consisten` 等关键词的穷举 grep（排除 `.venv` 第三方库）：唯一相关文本是参数表里对 `temperature`/`top_p` 作用的常规说明（"控制生成结果的多样性和随机性"），**未提及**这两项在 `thinking` 模式下会被静默丢弃这件事。也就是说：`_normalize_model_parameters` 这一行为**只存在于代码里，没有任何面向 DSL 作者的文档披露**——按官方参数说明配置 `completion_params` 的人，无法从文档得知这两项会在 thinking 模式下失效。

### c) 该变异层如实登记与可选约束机制枚举

**如实登记**：R2(a) 已用代码证据确认，采样参数在 `thinking: true`（v1_4 当前实际配置）下确实不生效。**B-01 的配置层修复（`temperature=0`/`top_p=1`）对"31% 篇幅摆动"这一变异源无效**——这两个值从未到达模型侧。进一步推论：v1_4 与 v1_3（`temperature`/`top_p` 完全未设置，落到 provider 默认值）在**这条变异链路的运行时实际效果上几乎没有差异**——两者最终都是把采样行为完全交给 DeepSeek 服务端在 thinking 模式下自行决定，DSL 层面写不写这两个值，此刻对上游请求没有可验证的区别。

**该层变异可以怎么被约束——只列选项，不做取舍**：

| 层面 | 选项 | 代价/副作用 |
|---|---|---|
| 图内现成机制 | 无。当前图内没有任何节点对模型输出做归一化、截断或多样性抑制；`completion_params` 是唯一现成的"调节旋钮"，但已证实在当前模式下对此变异源不起作用 | — |
| 可配置项 | 关闭 `thinking`（`thinking: false`） | 按同一段代码逻辑，只有 `type == "enabled"` 分支会剔除采样参数，关闭后 `temperature`/`top_p` 会正常透传给上游；但 `reasoning_effort` 会在 disabled 分支被同时 pop 掉（两者不能同时保留），且会失去模型推理链路，SKILL_v1.4.md 现有判据是否依赖这条推理链路需要重新评估，属于会改变模型行为模式的选择 |
| 可配置项 | 更换 provider/model（如原生支持 `seed`、或不做参数剔除的模型/供应商） | 需要重新做一轮供应商可靠性核实（如本次对 `deepseek-v4-flash.yaml` 的核实）；可能改变可用能力面（工具调用、上下文长度等），涉及模型选型决策 |
| 结构性约束（输出契约） | 给 `master_package` 关键字段（如 `publish_copy`/`release_check` 展开细节）显式加篇幅上下界 | 由模型自觉遵守，无代码强制，效果取决于模型服从度（与 `hashtags_topics`/`release_decision` 等现有字段的执行水平相同）；上下界定得不合适可能反而压低专业判断质量 |
| 节点级后处理 | 新增 code 节点对 `---M4_ARTIFACT---`/`---M4_USER_DELIVERY---` 做篇幅归一化（截断/阈值判定） | 截断可能破坏语义完整性；若归一化目标是"多次生成取一致版本"，需要额外模型调用做多数表决，与"零模型调用"及实测预算冲突；新算法本身需要独立验证正确性 |

**不为回答本节调用模型；以上全部为静态代码/文档核实结果，非实测结论。**

---

## R3 · 计分门（G2）的篇幅稳定性缺口（新增调查）

### a) 输出篇幅是否有任何上下界约束？

**没有上限约束。唯一的下限约束形同虚设。**

全文档核对：`returns_adapter.MIN_ARTIFACT_CHARS = 400` 是图内唯一与"长度"相关的数值常量，但它只用于判断 `---M4_ARTIFACT---` 块是否"近乎空"（识别产出被截断或未生成），阈值极低，对一份完整发布包裹而言极易满足，不构成篇幅质量层面的上下界控制。除此之外：`packaging_routes[]` 明确"数量由是否存在真实取舍决定，不固定"；`caption_rules` 要求查 `platforms.md` 获取单屏字数上限，查不到则写定性要求、"不得自己定一个数"——即使查得到平台字数数据，也只落成措辞层面的"建议"，不是代码层硬约束；`publish_copy`、`release_check` 等字段均无字数或条目数上限声明。

### b) 哪些 G2 维度的评分会直接受篇幅影响（只列对应关系）

| G2 维度 | 与篇幅波动的关系 |
|---|---|
| M2 · 核心包装抓取能力（15分） | 标题/封面/首帧的展开程度不同，影响评审对"是否抓住了真正值得点击的信息"的感知 |
| M3 · 发布包内部一致性（15分） | 篇幅差异可能改变标题/封面/正文/评论区之间呼应细节的展开程度，影响"是否属于同一传播承诺"的可读判断 |
| M4 · 平台原生适配（20分） | 篇幅详略直接影响评审能否看出平台机制层面"有意义的差异"（如封面策略与首帧策略的展开程度） |
| M5 · 可直接发布程度与人工返工量（15分） | 受篇幅影响最直接的一项——更详尽的产出通常读起来"更接近直接可用"，更精简的产出容易被读成"还需要用户自己补充"，即使两次运行的专业判断本身并无实质差异 |
| M6 · 自然度、主体声音与 Anti-AI-Slop（10分） | 篇幅膨胀（更长）容易伴随套话、排比等注水迹象；篇幅收缩则可能显得生硬 |

（只列出对应关系，不打分、不预测分数，取舍与判据设计留给规则侧。）

### c) 图内是否存在可用于约束篇幅的现成机制（哪怕未启用）？

**只有一处、且需要改造才能派上用场**：`returns_adapter.MIN_ARTIFACT_CHARS`（当前值 400）是唯一现成的、可复用/可调的长度阈值变量，但其现有语义和实现都是"防止空产出"的下限判断，不是"控制篇幅波动区间"的机制——若要用于约束篇幅稳定性，需要改动其判断逻辑与阈值设计本身，不属于"零改动即可复用"的现成机制。除此之外，图内没有其他与篇幅相关的现成机制。

---

## R4 · 判定

### 判定口径复核（按冻结口径逐条对照，不放宽也不收紧）

| 判据 | 结果 |
|---|---|
| B-02~B-06 全部经独立复验确认关闭 | **满足**——见 R1，5 条状态标签与 BLOCKER_CLOSURE 一致，均为独立复验（非复读）后的 `CLOSED` |
| B-01 为 `CLOSED_AT_CONFIG_LAYER_ONLY` 是可接受状态 | **满足**——状态标签维持不变；R2 的更严重根因发现属于"给下一轮修复的输入"，按冻结口径不因此改变本轮判定 |
| R0 重跑是否发现新的架构缺口 | **未发现需要新增阻断 ID 的缺口**。P0-3(a)(b) 两处原有缺口方向性关闭（见上文）；P0-5/P0-6 各有一项窄范围、非结构性的部分缓解，已如实限定其边界，不构成新增独立阻断；P0-7 的输入契约命名不对齐问题原样存在、未修复，但这是 v1_3 报告已登记的既有观察（非 B-01~B-06 之一），本轮不新开阻断，仅在实测设计层面重申提醒 |
| R2/R3 结论是否单独构成 NOT_READY | **不构成**——按冻结判据，两节结论是下一轮修复与阶段三实测设计的输入 |

### 判定

```text
READY_FOR_EMPIRICAL_TESTING
```

**说明（不构成放宽判据，只是如实标注严重性）**：本轮独立复验确认 B-02~B-06 五条阻断的代码级修复真实生效（非表面存在），B-01 的配置层改动真实写入且是 provider 支持范围内能做到的最大值，因此满足冻结判据、可以开始花 token 做实测。但 R2 揭示的事实——**当前 `thinking: true` 配置下，B-01 声称已钉死的 `temperature`/`top_p` 从未到达模型侧，v1_4 与 v1_3 在这条变异链路上运行时效果几乎无差异**——是一项比 `DETERMINISM_SMOKE_v1.0.md` 已披露内容更根本的事实，**必须被下一轮修复与阶段三 k 次判据设计者看到**，否则容易在不知情的情况下把"已经钉过温度"当成"已经获得一定程度的确定性改善"，而实际改善为零。这一点连同 R3 揭示的"G2 计分门无任何篇幅上下界约束、且 M2/M3/M4/M5/M6 五个维度均直接受篇幅波动影响"，共同构成阶段三设计 k 次一致性判据时必须纳入的已知风险，而不是可以忽略的次要细节。

---

## R5 · 结转清单（CF-01 ~ CF-05）逐条处置

治理绑定：`笛语商业SKU验收体系_索引与启动规则_v1.0.md` §10（规则仓库只读，读当前版本，未复算 sha256——任务未要求）。以下逐条处置，遗漏或沉默不构成合法答案，"不适用"须说明理由。

### CF-01 · 每 Case 跑 k≥3 次（硬门结论须在 k 次上一致）

**处置：不适用于本任务，推迟到阶段三实测设计。** 理由：本任务零模型调用，不产生任何"跑 k 次"的实测数据，CF-01 要求的是实测协议本身（每个测试 Case 重复调用 k 次并核对硬门结论一致性），不是可以在 v1_4 的静态图结构里找到"是否已具备"的东西。架构层面的相关观察（已在 R2 交代）：每次调用相互独立、无状态，图结构本身不阻止重复调用 k 次，因此不构成执行 CF-01 的架构障碍；但 CF-01 要求本身的落实（k 值、判据表、失败处置）属于阶段三测试协议设计范畴。

### CF-02 · 同源对照位两侧各留一个

**处置：不适用于本任务。** 理由：CF-02 是评测样本/对照组设计方法论要求（同源素材的 Diyu 侧与对照侧配比），与 v1_4 的 DSL 架构本身无关——v1_4 不包含任何评测样本抽样或分组逻辑（这类逻辑存在于评测协议/评审流程里，不在 DSL 节点里）。**推迟到阶段三评测设计**。

### CF-03 · 计分门也要 k 次一致（G2 禁止用 k 次均分掩盖跨次骑线）

**处置：部分已处理（本任务 R3 已交付所需的静态事实输入）+ 判据设计本身推迟到阶段三。** 理由：CF-03 与本任务 R3 的调查范围高度重合——R3(a)(b)(c) 已经独立回答"v1_4 是否存在篇幅上下界约束"（无，仅一处形同虚设的 400 字符下限）、"哪些 G2 维度受篇幅波动直接影响"（M2/M3/M4/M5/M6）、"图内是否有可复用的现成机制"（仅 `MIN_ARTIFACT_CHARS` 一处，需改造才能派上篇幅稳定性用场）。但 CF-03 要求的"k 次各自评分、PASS/FAIL 判定在 k 次上一致、禁止均分掩盖骑线"是**评分判据设计**本身，评分是外部评审员的职能而非 DSL 节点职能，v1_4 图内不包含、也不应该包含评分逻辑——因此判据设计的落实**推迟到阶段三**，本任务只交付了静态事实输入（R3），不新增判据设计（判据设计是规则侧的事，与 R2(c) 的"只摆选项不做取舍"同一分工原则）。

### CF-04 · 参考文件防静默陈旧（原 FU-01）

**处置：推迟到 S6（阶段二目录重构），不阻断本任务、不阻断实测。** 理由：与参考文档 §10 CF-04 自身给出的时点（"阶段二目录重构 S6，与参考文件加载器搬进 `core/` 一并做"）与阻断判定（"是否阻断实测：否"）一致。本任务 R1·B-03 已独立确认：截至本次复验时点，`ref_projection` 内嵌字节与仓库源文件当前 sha256 逐一核对一致（未漂移），但**防陈旧的自动检测机制本身在 v1_4 图内确实不存在**——全文档核对确认，图内没有任何构建时/运行时的 sha256 比对或告警逻辑，只有静态的 `provenance` 记录（本文件第 1151–1181 行，`projection_record` 节点），记录了值但不比对、不告警。这一独立复核结果与 CF-04 的问题描述一致。

### CF-05 · 顾问性三条判据（曾在取代中丢失）

参考文档原文明确登记：`v1_4` 与六条阻断中**没有任何一处**为顾问性做承载，且**"是否阻断实测：是——没有承载机制，该门恒为无效"**，时点为"S5 判定之后、阶段三之前"。

**本任务独立静态检查（不评价做得好不好，只查有没有承载它的地方）**：

| 判据 | 双侧失败形态 | v1_4 图与提示词内独立检索结果 |
|---|---|---|
| ① 识别了错误的提问方式，但不拒绝回答 | A：识别出问题就拒答／B：不识别，照错的问法直接答 | **无承载**。全文档对"拒绝"/"拒答"/"提问方式"/"追问"等关键词穷举 grep：命中的"拒绝"均为素材领域内的案例文本（如餐饮/课程行业条件表里"拒绝一个高频需求"，本文件第 682/695 行），或 `component_return` 节点的缺项追问机制（本文件第 3054–3066 行，`QUESTION_MAP`）——后者处理的是"结构性字段缺失时问哪一项"，不是"识别输入的提问方式本身有问题（如把多个事实装进一个诱导性问句）后仍继续作答"这一判据。`examples.md` 内嵌案例（本文件第 905–940 行，"划掉输入专有名词"练习）触及类似情境，但 `examples.md` 仅在 `example_reference_requested=='YES'` 时加载（非默认路径），且其自身明文限定"只作形式与质量参考，不得变成事实、话术或模板"（本文件第 749 行），即被架构本身声明为非强制判定机制，不构成"承载" |
| ② 给出了具体方法，但不伪造精度 | A：给了方法但编造精度／B：怕编造而不给方法（对冲、堆免责） | **局部承载，范围窄**。本文件第 1507–1535 行（"三种拿不到的情况"表 + 后续说明，`skill_llm` 实际 system prompt 内）明确要求：数值型平台参数拿不到时，**不得**自造具体数字（失败侧 A 被禁止：第 1520/1531 行），但**必须**改用定性制作要求填写完整、不得留空（失败侧 B 被禁止：第 1524–1532 行，"定性要求不是留空"）；同一规则在内嵌 `platforms.md` 全文中重复出现（第 610–628 行）。**但此机制的适用范围仅限"平台数值参数"这一类事实**（标题长度、单屏字数等），不覆盖 SKU 判断面里其余需要"给方法又不伪造精度"的场景（如 CTA 强度建议、标题推荐力度等专业判断本身没有同类的双向禁止规则）——不构成覆盖整个判断面的通用"顾问性反向错误门" |
| ③ 有立场但不固执 | A：不表态（"都行""看你"）／B：表态后不认边界（说成唯一答案） | **无承载**。全文档对"表态"/"立场"/"边界条件"/"反转"等关键词穷举 grep：唯一命中的"表态"（本文件第 1728 行）是转发心理学的领域内容（社交带出型平台的转发驱动分析），与判据③无关。`platform_variants[]` 字段（本文件第 1887 行附近，"逐项：改了什么→应对什么机制/不变→为什么"）要求给出判断与理由，但不要求声明"这个判断在什么条件下会反转"——与参考文档表格里另一份标准 P1 的"M4 条件改变裁决会反转"机制（该判据不在 v1_4 范围内，出自其他 SKU 的标准文档）不是同一类机制。未发现任何字段/自检项要求模型在给出专业判断后同时声明其适用边界或反转条件 |

**结论：CF-05 尚无覆盖整个判断面的承载机制**（①③ 完全无承载；②仅在平台数值参数这一窄场景内有局部承载）。这与参考文档自身"v1_4 与六条阻断中没有任何一处为顾问性做承载"的判断方向一致，独立复验在此基础上进一步给出了②的窄范围例外这一更细粒度的发现，未发现参考文档判断有误。

**处置：不在本任务内建设，推迟到"S5 判定之后、阶段三之前"（与参考文档自身指定的时点一致）。** 本任务受"零改动"绝对约束（本任务的第 2 条绝对约束：不修改任何文件），即使认为有必要，也不得在本任务内顺手建立承载机制——发现问题登记为阻断，不顺手修，这正是本任务受到的同一条纪律（与 B-01～B-06 的处置原则相同）。

### R5 处置汇总

| 结转项 | 处置 |
|---|---|
| CF-01 | 不适用于本任务，推迟到阶段三实测设计 |
| CF-02 | 不适用于本任务，推迟到阶段三评测设计 |
| CF-03 | 部分已处理（R3 已交付静态事实输入），判据设计本身推迟到阶段三 |
| CF-04 | 推迟到 S6（阶段二目录重构），不阻断本任务/不阻断实测 |
| CF-05 | 已完成静态承载检查（本节），承载机制本身**未建设**，按参考文档声明推迟到"S5 判定之后、阶段三之前"，**该文档明确声明这构成阶段三实测的独立阻断** |

**与 R4 判定的关系（不回改 R4，另行披露）**：R4 的判定标准冻结于本任务的原始 Execution Prompt v1.0，其判据范围只覆盖 B-01～B-06、R0 新发现、R2/R3 结论，不包含 CF-05——因此 R4 给出的 `READY_FOR_EMPIRICAL_TESTING` 按其自身冻结的判据范围成立，不因 CF-05 的发现而回改。但 CF-05 是本轮 R5 新引入、由规则侧参考文档自身明文声明的独立阻断项（"是否阻断实测：是"），其指定生效时点（"S5 判定之后、阶段三之前"）意味着：**在 CF-05 的承载机制被建立之前，实际进入阶段三花 token 做实测这件事本身仍不成立**，即便 R4 在其自身范围内已经判定架构侧就绪。这不是两个判定互相矛盾，是两个不同范围的判据分别给出各自范围内的真实结论。

---

## COMPLETION CHECK

```yaml
real_behavior_verified:
  - 三份治理绑定文件（Q-COMM-04/BLOCKING_LIST/v1_4.yml）sha256 现场复算与授权值逐字节一致: PASS
  - v1_4 全部节点/边通过 yaml.safe_load 结构化解析核对，未抽样: PASS
  - fact_verification/market_claim_scan/delivery_finalize 三个节点代码用独立构造测试向量直接执行验证行为
    （非复用 BLOCKER_CLOSURE 已有用例，非仅阅读代码）: PASS
  - B-03 三份参考文件嵌入内容与仓库当前源文件逐字节 diff（非仅 sha256 比对）: PASS
  - B-04 嵌入模式清单与外部 JSON 文件做列表级相等性比较（非仅 sha256 比对）: PASS
  - B-05/B-06 字段通过提取实际 system prompt 文本逐字节核对确认真实送达模型: PASS
  - R2 的插件参数剔除行为通过读取本机实际部署插件包源码确认，非猜测非文档: PASS
  - R5·CF-05 三条判据的承载检查逐条给出 v1_4 内的具体行号或"无承载"结论，非泛泛而谈: PASS
  - R1/R0 全部关键结论均附 v1_4.yml 节点名/字段路径/行号出处（见 R1 附录出处索引），
    不依赖"S1-S4 里改过所以是对的"这一非法依据: PASS
validator_discrimination_verified:
  - fact_verification 独立测试同时覆盖"应放行"与"应阻断"两类用例且结果不同: PASS
  - market_claim_scan 独立测试同时覆盖命中文本与干净文本且结果不同: PASS
  - delivery_finalize 独立测试覆盖 fact_blocked/market_blocked/both/neither 四种组合且各自输出正确的 delivery_outcome: PASS
core_problem_solved:
  - 本任务核心问题"能不能开始花 token"已独立回答，按 R4 自身冻结判据: READY_FOR_EMPIRICAL_TESTING；
    但 R5·CF-05 发现独立于 R4 判据范围之外的另一项阻断（顾问性三条判据无覆盖整个判断面的承载机制），
    按参考文档自身声明须在实际进入阶段三之前解决，已在 R5 完整披露，不因 R4 判定而被掩盖
  - 未把"清单变绿"误当成"判定可信"——对 B-06 明确指出"字段存在"与"代码校验其出现在正文"是两件事，
    未因前者满足就模糊后者的缺失
protected_targets_unchanged_or_authorized:
  - v1_4.yml/Q-COMM-04/BLOCKING_LIST_v1.0.json: 全程只读，未修改
  - v1_3_TEST.yml 冻结基线: PASS（任务结束复算 sha256 = daa8365de26f9b280e2ea72707aa85ce445edd2b8bcdaa54350ecce9797b635e，与开工前逐字节一致）
  - 规则仓库 /mnt/c/...: 全程只读
  - 未新建/发布任何 Dify 应用、零模型调用: PASS
evidence_refs:
  - pp-architecture/REVERIFICATION_REPORT_v1.0.md（本文件）
  - pp-architecture/BLOCKER_RECLOSURE_v1.0.json
  - 本机插件包 langgenius/deepseek-0.0.20@850efe73.../models/llm/llm.py 与 deepseek-v4-flash.yaml
unnecessary_complexity_remaining:
  - 未发现。未新增评分器、知识库、RAG、第二套工作流引擎；两个独立测试脚本用后即弃，未落入仓库
disclosed_anomalies_not_hidden:
  - B-01 根因诊断与 BLOCKER_CLOSURE 存在实质分歧（插件层参数剔除，而非仅浮点非结合性），已在 R1/R2 完整披露
  - B-06 汇聚字段"是否真的出现在用户正文"无代码校验，已披露，未算作 B-06 重新开放
  - P0-7 输入契约命名不对齐问题原样未修复，已披露，未算作新增阻断
  - R5·CF-05 承载机制缺失是参考文档自身声明的阶段三独立阻断项，已在 R5 完整披露，未因不在 R4
    冻结判据范围内而淡化或省略
```

`task_final_status: DONE`
