# PP 模块架构抽取与验证报告 v1.0

```yaml
task_id: DIYU-V1-PP-ARCHITECTURE-EXTRACTION-AND-VERIFICATION-001
report_date: "2026-09-01"
zero_model_calls: true
zero_dsl_or_code_changes: true
scope: 只回答"架构工程角度是否达到可以进入 LLM 实测的标准"；不做产品判断、不评价效果好坏
tested_source: content-production/workflows/DIYU_M4_TOOL_PUBLISHING_PACKAGING_v1_3_TEST.yml
tested_source_sha256: daa8365de26f9b280e2ea72707aa85ce445edd2b8bcdaa54350ecce9797b635e
acceptance_baseline: Q-COMM-04_P0_内容发布包装助手商业化评价验收标准_v1.0.md
acceptance_baseline_sha256: 55bcfa4001668dd23614459cb502aca30286e62894670a911a68de17528cb397
```

方法说明：全部结论来自对 DSL YAML 全文（1616 行）的逐节点、逐边读取与对照，含对全部 15 个节点
`type`/`title`/`code`/`template`/`prompt_template`/`completion_params`/`variables` 字段的穷举核对，
以及对全文 `temperature`/`UNKNOWN`/`platforms.md` 等关键词的穷举 grep 核验（零命中即穷举确认，非抽样）。
未调用任何模型、未新建任何 Dify 应用、未修改 DSL 或任何代码。

---

## P0-1 冻结被测源

见 [FROZEN_SOURCE_v1.0.yaml](FROZEN_SOURCE_v1.0.yaml)。两份治理绑定文件 sha256 现场复算与授权值逐字节一致。

**状态：DONE**

---

## P0-2 可抽取性清单（关闭规则侧 PRE-02）

### 依赖仓库里的哪些文件

| 类别 | 依赖项 | 说明 |
|---|---|---|
| 运行时必需 | 无其它仓库文件 | DSL 自身是自包含 YAML：`skill_llm` 的 system prompt 是**已烘焙的静态字符串**，运行时不再读取 `content-production/skills/packaging-content-for-release-m4/SKILL.md` 或任何 `references/*.md` |
| 构建时依赖（非运行时） | `content-production/skills/packaging-content-for-release-m4/SKILL.md`（及其前身 `packaging-content-for-release/SKILL.md`） | system prompt 由某个**未包含在本 DSL 内的生成器**从该 SKILL 文件"派生"（DSL 注释原话："system prompt 由后继 SKILL 文件字节派生（生成器保证），不手工同步"）。这意味着：**修改专业逻辑必须回到 SKILL.md 源头重新生成 DSL，不能直接改 DSL 里的烘焙文本**，否则会与源头字节脱钩且无人发现 |
| 声明但从未在运行时被读取 | `references/platforms.md`、`references/industry-conditions.md`、`references/examples.md` | 详见 P0-3 Layer A 一节：图中不存在任何检索/HTTP/工具节点，`ref_projection` 模板只输出"这次该不该加载"的规则文字，不含文件真实内容；`skill_llm` 的 `context.enabled: false`。**这三个文件名只出现在提示词文本里，不是本图的运行时依赖** |

### 依赖哪些上游节点的输出（M1/M2/M3/M5）

**无运行时硬依赖。** 系统提示词明文：「本 Skill 不调用、不请求、不假设任何上游组件被运行过」「跳过物理组件只表示等价输入已经满足」。图结构上，`start` 节点只接收 `capability_call`/`professional_input`/`entry`/`run_mode`/`example_reference_requested` 五个纯文本变量，没有任何节点对 M1/M2/M3/M5 的 Dify 应用做 tool 调用或 HTTP 调用（全图 15 个节点无检索/HTTP/工具节点，见 P0-1 清单）。

判定：这一项对可抽取性是**利好**——PP 抽出去单独跑，不需要连带拆出 M1/M2/M3/M5。

### 依赖哪些环境变量、凭据、外部服务

| 项 | 现状 |
|---|---|
| `workflow.environment_variables` | 空数组，DSL 内**无**声明的环境变量 |
| LLM 凭据 | 不在 DSL 内。走 Dify Marketplace 插件 `langgenius/deepseek:0.0.20@850efe73…`，实际 API Key 配置在 **Dify 工作区的 Model Provider 设置**里，本 DSL 文件本身不含凭据 |
| 外部服务 | 仅 DeepSeek（`deepseek-v4-flash`，chat 模式），经由该插件间接调用；DSL 本身未声明任何其它外部服务地址 |

### 依赖哪些 Dify 平台特性（换平台会失效的那些）

| 特性 | 用途 | 换平台后果 |
|---|---|---|
| Workflow 图执行引擎（node/edge、if-else 分支、`sourceHandle`/`targetHandle`） | 承载 `envelope_check → gate_sufficiency → …` 全部路由 | 必须在目标平台重建等价的编排/路由逻辑，或改写成普通程序控制流（`if/else` 语句） |
| `code` 节点 python3 沙箱 | `envelope_check`／`returns_adapter`／`component_return`／`delivery_finalize`／`binding_record` 五个节点的确定性逻辑 | 代码本身只用标准库（`hashlib`/`json`/`re`），**移植成本低**，可作为普通 Python 函数在任意宿主环境运行 |
| `template-transform`（Jinja2）节点 | `ref_projection`／`projection_record`／`final_extract` | Jinja2 是通用模板引擎，移植成本低 |
| `llm` 节点 + `completion_params` 直通 | `skill_llm`／`recovery_llm` | 需要在目标平台/框架里找到等价的"模型节点 + 参数透传"能力；`completion_params` 里的字段名（`reasoning_effort`/`thinking`）是 Dify 对 DeepSeek 插件的适配层字段，未必在其它编排框架直接可用，需要按目标框架重新对齐参数名 |
| `{{#node_id.field#}}` 变量插值语法 | `skill_llm`/`recovery_llm` 的 prompt_template、`ref_projection` 等模板 | Dify 专有语法，移植时需要替换成目标框架的变量引用写法 |
| YAML 锚点复用（`&id001`/`*id001`） | `skill_llm` 与 `recovery_llm` 共用同一组 `completion_params` | 纯 DSL authoring 便利，非 Dify 运行时特性，移植不受影响，但要注意目标环境里两个 LLM 调用点必须继续共用同一套参数，不能只改一处 |
| Marketplace 插件系统 | DeepSeek provider 接入 | 换平台需要重新对接模型 provider，且该层目前**未钉死 `temperature` 等关键采样参数**（见 P0-4），移植时如果新平台的默认值与当前平台不同，行为会进一步漂移 |

### 判定

**`EXTRACTABLE_WITH_DELTA`**

无运行时上游硬依赖、无烘焙敏感凭据、核心业务逻辑（code 节点）标准库实现、可移植性较好；但独立抽出需要补齐：

1. 一个能承载「结构化输入闸 → LLM 调用 → 结构化输出闸 → 有界恢复」这条路由的宿主运行时（可以是精简版 Dify，也可以是自建的轻量编排层）；
2. 一个脱离 Dify Marketplace 插件系统、独立管理的 DeepSeek（或替代模型）凭据与调用层，并**在迁移时补上目前缺失的确定性采样参数**（不能原样照抄"未钉死"这件事）；
3. 一条把 `content-production/skills/packaging-content-for-release-m4/SKILL.md` 重新"生成"为运行时 system prompt 的构建流程（该生成器本身不在本 DSL 内，需要一并确认其位置与可用性，否则未来无法安全更新 system prompt）；
4. 若要满足 Layer A（平台硬契约）的真实语义，需要**新建**一个把 `references/platforms.md` 等文件内容真正接入运行时的机制——这不是"抽取时保留原样"就能得到的，因为当前图里这条线本来就没接（见 P0-3）。

**状态：DONE**

---

## P0-3 架构一致性矩阵

### (a) 标准 §1.3 的 12 项标准输出对象

| # | 标准项 | 图里是否有对应产出 | APPLICABLE/NOT_APPLICABLE 判定机制 |
|---|---|---|---|
| 1 | 标题 | 存在 —— `titles[]` / `recommended_title` | 无独立判定字段；隐含于"每种可用入口类型至少一个" |
| 2 | 封面策略与封面文字 | 存在 —— `cover` | 同上，无独立 APPLICABLE 字段 |
| 3 | 首帧策略与首帧文字 | 存在 —— `first_frame` | 同上 |
| 4 | 发布正文 | 存在 —— `publish_copy` | 同上 |
| 5 | 字幕重点、断句、强调或展示规则 | 存在 —— `caption_rules` | 非视频形态有专门的"字段映射表"把它显式改写为"图内文字规则"或标 `NOT_APPLICABLE`（这是全部 12 项里**唯一**明确写了"不适用要写 `NOT_APPLICABLE` 并说明，不要留空"的一项，见非视频形态字段映射表） |
| 6 | 音乐/音效使用与落位建议 | 存在 —— `sound_placement` | 同第 5 项的字段映射表：图文形态下按"是否带音轨"判 `NOT_APPLICABLE`，纯文字固定 `NOT_APPLICABLE` |
| 7 | 评论区首评/互动设计 | 存在 —— `comment_design` | 无独立 APPLICABLE 字段；受 `cta_contract=无CTA` 时的负向清单约束（"不得出现"），但那是内容约束，不是 APPLICABLE 判定 |
| 8 | CTA | 存在 —— `cta_surface` | 有三级判据（低风险互动/经营承接/高风险）与 `cta_contract` 只读继承机制，判定逻辑存在，但落在提示词层，非独立结构字段 |
| 9 | 标签/话题等平台元素 | **缺失** —— `master_package` 字段清单里没有任何标签/话题/hashtag 字段（全文穷举 grep 零命中） | 不适用——字段本身不存在，无从谈判定机制 |
| 10 | 平台适配说明 | 存在 —— `platform_variants[]` + `platform_spec_status` | 有明确判定：平台未锁定 ⇒ 只出母版；已锁定但主本条目不可得 ⇒ `PLATFORM_SPEC_UNVERIFIED`。**但见下方 Layer A 一节：这条判定逻辑虽然写在提示词里，图里没有任何机制能让它读到"主本条目"真正是否可得，实际运行只会永远走"不可得"分支** |
| 11 | 发布前检查 | 存在 —— `release_check`（五条） | 五条各自要求写"实际结论"，非布尔判定，但有固定检查项清单 |
| 12 | 发布条件/不应发布条件 | **部分存在，分散** —— 没有单一命名字段对应"发布条件/不应发布条件"，实际由 `fact_check_status`（PASS/FAIL/NOT_VERIFIED）＋ `release_check` ＋ `missing[]` ＋ `component_return` 分支（输入不足时的组件级 Return）共同承担这一职能 | `fact_check_status: FAIL` 时"阻止交付"是提示词层的明文规则，但**无任何代码节点核验这一状态是否被正确判定或正确执行**（见 P0-5） |

**小计**：12 项中 10 项在输出契约里有对应字段（第 9 项缺失，第 12 项分散无单一字段）；结构化 APPLICABLE/NOT_APPLICABLE 判定机制只在第 5/6/10 项有明确、可追踪的规则，其余各项要么无独立判定字段，要么判定逻辑完全依赖模型自觉遵守提示词。

### (b) 标准 §7 三层平台适配（Layer A / B / C）

| 层 | 图里是否分开 | 无实时数据时是否有"不运行"机制 |
|---|---|---|
| Layer A｜Platform Hard Contract（确定性、带版本） | **提示词层面有分层意识**（`platform_spec_status: VERIFIED/UNVERIFIED`），但**运行时数据源未接入**：`references/platforms.md` 从未被任何节点实际读取（`ref_projection` 只产出"该不该加载"的规则文字，不含文件真实内容；`skill_llm.context.enabled = false`；全图 15 个节点无检索/HTTP/工具节点，穷举核对确认）。**结果是 Layer A 在这套图里结构性地永远只能落在 `PLATFORM_SPEC_UNVERIFIED` 分支**，从未有机会真正拿到"带版本的确定性事实"，这不是某次运行缺数据，是这条数据通路本来就没被接进图里 | 不适用（Layer A 不是"实时数据"，是应当固定但目前接不到的版本化数据） |
| Layer B｜Platform Native Heuristics（专业判断） | 存在，且是提示词的主体部分（标题入口功能、首帧/封面分工、CTA 强弱、评论区承接方式等大段专业规则），但**不是一个独立可寻址的结构单元**——它和 Layer A、Layer C 的规则混在同一段系统提示词文本里，没有代码或提示词结构上的显式分层标记 | 不适用 |
| Layer C｜Current Market Signal（当前热点、实时数据） | **图里没有任何机制能获取实时市场数据**（同上：无检索/HTTP/工具节点） | **有**——因为图结构上根本无法执行 Layer C，客观效果等价于"没有实时数据时不运行 Layer C"；提示词也有对应的"数据用来提问，不用来下结论"式指导语。**但"不得用 Layer B 冒充 Layer C"（即不得输出无依据的当前市场断言）没有任何代码级校验**——`returns_adapter` 的 `LEAK_PATTERNS` 关键词表里不含"当前最流行""现在最少""最佳发布时间"一类措辞，这类断言若被模型说出来，不会被任何节点拦截 |

**小结**：三层在**提示词叙述层面**有分开意识，但没有做成三个独立、可分别校验的结构单元；Layer A 的数据通路缺失是全部发现里对"能不能进实测"影响最大的一条（详见 P0-8 B-03）；Layer C 的"不运行"是结构性成立的，但"不冒充"完全靠模型自律，无代码防线。

### (c) M4 冻结的六项外壳必填：闸还是注释？

`envelope_check` 节点 `REQUIRED = ["content_body_or_beats", "content_promise", "explicit_non_promise", "facts_registered", "cta_contract", "asset_publish_permission"]`，**恰好六项**，与 M4 冻结六项外壳必填对应。

**结论：是闸，不是注释。** 证据：

- `envelope_check` 逐项检查这六个 key 是否在 `capability_call + professional_input` 文本里"在场"（正则匹配 YAML/JSON/Markdown 三种写法），任一缺失 ⇒ `status = INSUFFICIENT` ⇒ `can_run = "false"`；
- 下游 `gate_sufficiency`（`if-else` 节点）直接读 `envelope_check.can_run`，`can_run != "true"` 时**整条路由走向 `component_return → end_component_return`，完全跳过 `ref_projection`/`skill_llm`**——即校验不通过时**流程会停**（不会调用 LLM，不会产生任何专业产出），不是"记一笔然后继续往下走"。

**但要素级说明**：这六项检查是**结构性在场检查**（key 在文本里出现过、非空、非"待定/无/n/a"类占位词），不是**语义充分性检查**——`vacuity_flags`（语义疑似单薄）不会被判 `INSUFFICIENT`，只会降级为 `SUFFICIENT_WITH_CONDITIONS` 并放行，把语义裁决甩给 `skill_llm` 自己判断（这是代码注释明文承认的设计："语义单薄的裁决交给 Skill 正文"）。所以准确说法是：**这是一道真实的结构性硬闸，但闸后面紧接着一道无代码校验、完全靠模型自觉的语义软判断**。

**状态：DONE**

---

## P0-4 确定性配置审计

`skill_llm` 与 `recovery_llm` 共用同一个 `completion_params`（YAML 锚点 `&id001`/`*id001`，两个 LLM 节点字节级相同）：

```yaml
model: deepseek-v4-flash
provider: langgenius/deepseek/deepseek
mode: chat
completion_params:
  max_tokens: 384000
  reasoning_effort: low
  thinking: true
  top_p: 0.8
```

| 参数 | 是否显式钉死 | 对"同一输入多次运行结果是否一致"的影响 |
|---|---|---|
| `max_tokens` | 是（384000） | 只限制输出长度上限，不影响采样随机性 |
| `top_p` | 是（0.8） | 钉死了核采样的概率质量阈值，**但 `top_p` 本身不能单独保证确定性**——它只是在（可能仍然是随机的）候选集合里做截断，真正决定"每次选哪个 token"的还是 `temperature`（或等价的采样温度） |
| `reasoning_effort` | 是（low） | 控制推理链路预算，不是采样参数，但 "thinking: true" 与 "reasoning_effort" 组合意味着模型在给出最终答案前会先走一段内部推理过程，**这段推理过程本身的路径也是采样出来的**，即使最终答案的采样被钉死，推理路径的分叉仍可能导致最终文字表达不同 |
| **`temperature`** | **否——全文档 `grep -n "temperature"` 零命中** | **未钉死。** 落到 `langgenius/deepseek` 插件 / DeepSeek API 的平台默认值（该默认值不在本 DSL 内声明，即便当前默认恰好较低，也可能随插件版本升级或 provider 一侧策略调整而改变，且改变时**本 DSL 不会有任何提示**）。这是本轮审计里对"稳定产生"影响最大的一项 |
| `frequency_penalty` / `presence_penalty` | 否——零命中 | 未钉死，同样落到平台默认值 |
| `seed` | 否——零命中 | 该插件/模型是否支持固定 seed 未在 DSL 内声明或使用；即使支持，当前也没有使用 |
| `stop` / `response_format` | 否——零命中 | 未使用，不构成额外随机性来源，但也意味着没有用 `response_format` 之类机制去约束输出结构，结构约束完全靠提示词里的 `---M4_ARTIFACT---` 等标记字符串 |

**对标验收标准 §21**：最终问题是"在同一 Frontier Model、同一输入和同一运行条件下，是否能够**稳定产生**……专业增量"。`temperature` 未钉死意味着"同一运行条件"这一前提本身在当前 DSL 里不成立——**同一输入的两次调用，运行条件其实不完全相同**（因为采样温度可以是平台默认的任意值，且不透明、不版本化）。在这个前提不成立的情况下，实测得到的任何"稳定/不稳定"结论都无法排除"只是这次采样运气"这个解释。

**状态：DONE**

---

## P0-5 事实溯源链路审计

**问题**：从"用户登记的事实"到"最终输出的文案"，中间是否存在任何强制性的绑定、校验或阻断节点？

**回答：不存在。**

证据链：

1. `envelope_check`（输入侧）只做**结构性在场检查**（六个必填 key 是否非空），不检查 `facts_registered` 的具体内容与后续文案的对应关系；
2. `skill_llm` 的系统提示词里有非常详细的事实纪律规则（`fact_refs[]`／`used_fact_refs[]` 三格结构、"找不到对应 `fact_id` 时，只有一条路：不生成它"、`fact_check_status: PASS|FAIL|NOT_VERIFIED` 且"FAIL 时阻止交付"），**这些规则全部只是文字指令，要求模型自己遵守、自己判断、自己在输出里如实填写**；
3. `returns_adapter`（输出侧唯一的代码校验节点）只做以下几类检查，逐条核对如下：
   - 三个标记块（`---M4_ARTIFACT---`/`---M4_USER_DELIVERY---`/`---M4_RETURNS---`）是否存在、非空、长度达标（`MIN_ARTIFACT_CHARS = 400`）；
   - 是否存在"回指"占位（`即上方`/`同上` 等 `BACKREF_MARKERS`）；
   - `USER_DELIVERY` 块是否包含内部术语泄漏关键词（`LEAK_PATTERNS`，检查的是"内部状态码/字段名有没有露出去"，不是"事实有没有编造"）；
   - `RETURNS` 块是否符合固定的八字段结构、`proposed_disposition` 是否属于三选一枚举；
   - **它把 `---M4_ARTIFACT---` 到 `---END_M4_ARTIFACT---` 之间的全部内容当成一个不透明字符串**，从不解析其中的 `fact_check_status`、`used_fact_refs[]`、`fact_refs[]` 等字段，因此**无法、也没有去核验模型自报的 `fact_check_status` 是否真实反映了事实核验结果**，更不会拿 `used_fact_refs[]` 回查 `professional_input` 里登记过的 `facts_registered` 是否真的存在对应事实。

4. `binding_record` 只记录哈希与运行元数据（模型名、参数、skill sha256 等"保真绑定"信息），同样不涉及事实内容核验；`delivery_finalize` 只处理"用户交付块是否非空"这一交付层问题。

**结论**：`facts_registered → 文案` 这条链路上，**唯一的把关者是模型自己**。系统在架构上没有任何独立于模型的代码节点，能够在模型编造了一个未登记事实、或错误地把 `fact_check_status` 判成 `PASS` 时把它拦下来。这直接对应验收标准 §6.1 "Critical Error = 0" 这一硬门要求——当前架构**无法**从代码层面为这条硬门提供任何独立保证，硬门是否成立完全系于模型这一次是否老实。

**状态：DONE（架构缺口已如实登记，未修复）**

---

## P0-6 UNKNOWN 传播审计

**问题**：当某项必要事实缺失时，UNKNOWN 这个状态在图里怎么流动？

全文穷举 `grep -n "UNKNOWN"`，仅命中**一处**：`envelope_check` 判断 `platform` 字段的值是否等于 `"UNKNOWN"`（与 `"未确认"` 同组，用于决定是否在 `conditionalized_text` 里追加"platform 未锁定"提示）。**除此之外，代码层面不存在任何针对"事实缺失"的 UNKNOWN 状态表示、传递或核验机制。**

- 对于 `facts_registered` 里没有登记、模型在写作时确实缺一项事实的情况，系统提示词给出的规则是"找不到对应 `fact_id` 时……不生成它"——即期望模型**直接不写**，而不是显式输出一个 `UNKNOWN` 标记再往下传。这意味着即使模型完全遵守指令，下游也**读不到**任何"这里本来该有一项事实但被跳过了"的显式信号，因为规则要求的是"消失"而不是"标注"；
- 一旦模型没有完全遵守指令（无论是疏忽还是被指令冲突干扰），把缺失事实悄悄换成了一个听起来合理的默认表述——`returns_adapter` 不解析 ARTIFACT 内部字段（见 P0-5），**没有任何机制能发现这次转换**；`LEAK_PATTERNS`／`BACKREF_MARKERS`／长度阈值这些检查都检测不出"一句听起来很像真事实、但其实没有 `fact_id` 支撑"的句子——系统提示词自己也承认这一点是"最容易漏的"："它读起来像叙述，不像事实陈述，但它断言了某件事发生过，和报一个价格是同一性质"。

**结论**：UNKNOWN（事实缺失）状态在这套架构里**没有被设计成一个可传播、可核验的第一等状态**——它要么在模型的写作决策里"消失"（合规情况），要么被模型悄悄替换成一个听起来是事实的表述（违规情况），而后一种情况**没有任何代码节点能够识别**。这直接对应验收标准 §6.1 最后一条"UNKNOWN 被悄悄变成 FACT"——当前架构对这条硬门同样**没有独立于模型的代码层防线**。

**状态：DONE（架构缺口已如实登记，未修复）**

---

## P0-7 裸入口结构判定（静态判定，未调用模型）

**给定条件**：只给验收标准 §1.2 的最低合法输入（已有内容 + 目标平台 + 必要事实 + 表达边界 + CTA 条件），不给 M1/M2/M3 任何上游产物。

**判定方法**：通读 `start` 节点变量声明、`envelope_check` 的 `REQUIRED` 列表与 `_find_scalar`/`_present` 的正则匹配逻辑、`gate_sufficiency` 的分支条件、以及下游各节点的 `variables:`/`value_selector` 引用链，人工追踪每个变量的来源是否在对应分支上一定已经执行过。**未发起任何实际调用。**

### 结构层面的结论

1. **不存在"结构性挂起"风险**：Dify 的 `if-else` 分支是互斥执行，`run` 分支（`ref_projection → … → skill_llm → …`）与 `false` 分支（`component_return`）里的每一个节点，其 `variables`/`value_selector` 引用的全部来源节点，都确认落在**同一条已执行分支**上（例如 `ref_projection` 只引用 `envelope_check` 的输出，而 `envelope_check` 是两条分支共同的上游，必然已执行）。逐节点核对未发现任何"引用了未执行分支的输出"的悬空引用。**不会因为结构问题而拿不到输入或崩溃**。

2. **`start` 节点表单层面**：只有 `capability_call` 与 `professional_input` 两个变量被标记 `required: true`；`entry`/`run_mode`/`example_reference_requested` 均可留空。只要这两个必填变量提交了**任意非空文本**，表单本身不会拒绝提交——真正的把关在 `envelope_check`。

3. **`envelope_check` 的结构性充分性判定，是按 6 个英文 key 的字面在场做正则匹配，不是语义理解**（`_find_scalar`/`_present` 搜索的是形如 `"content_promise": "..."` / `content_promise: ...` / `` `content_promise`：... `` 这类带**确切字面 key 名**的文本片段）。验收标准 §1.2 的最低合法输入用的是**中文自然语言描述**（"已有内容""目标发布平台""必要事实""表达边界""CTA/承接条件"），并不天然包含 `content_body_or_beats`/`content_promise`/`explicit_non_promise`/`facts_registered`/`cta_contract`/`asset_publish_permission` 这六个字面 key。

   逐项核对映射关系：
   - 已有内容 → 大致对应 `content_body_or_beats`（REQUIRED 内）
   - 必要事实 → 大致对应 `facts_registered`（REQUIRED 内）
   - CTA/承接条件 → 大致对应 `cta_contract`（REQUIRED 内）
   - 表达边界 → 对应关系**不确定**：REQUIRED 内是 `explicit_non_promise`（"明确不承诺什么"），而 `component_return` 的 `QUESTION_MAP` 里还单独列了 `expression_boundary`/`expression_subject_and_boundary` 两个近义但不同的 key——**这两个 key 都不在 REQUIRED 六项里**，即使调用方明确给了"表达边界"语义，只要没有恰好用对 `explicit_non_promise` 这个字面 key（或匹配它的三种写法之一），`envelope_check` 也可能判它缺失
   - 目标发布平台 → `platform` **不在** REQUIRED 六项里，缺失时优雅降级为 `NOT_LOCKED`（只出母版），不会造成 `INSUFFICIENT`
   - REQUIRED 里还有 `content_promise` 与 `asset_publish_permission` 两项，**在验收标准 §1.2 的最低合法输入定义里没有对应项**

   **推论**：如果调用方严格按 Q-COMM-04 §1.2 的字面五要素组织输入（用自然语言，不额外附加 `content_promise`/`asset_publish_permission` 这两个字面 key），`envelope_check` 的正则大概率会把 `content_promise`、`asset_publish_permission`（以及视表达边界的措辞而定，可能还有 `explicit_non_promise`）判为缺失 → `status = INSUFFICIENT` → `can_run = "false"` → 整条调用**在到达 `skill_llm` 之前，被 `gate_sufficiency` 短路到 `component_return`**，拿不到任何专业产出，只拿到一句"还差一项才能做判断"的追问。

4. **不存在"走空分支"的情况**——没有节点会在没有必需输入时静默产出空内容然后继续往下走；要么在 `gate_sufficiency` 就整体短路（拿不到 LLM 产出，这是设计如此，不是缺陷），要么进入 `skill_llm` 正常调用。

**结论**：从**结构**上看，PP **能够**独立于 M1/M2/M3 启动（不会因为缺上游产物而挂起或引用不到变量）；但从**输入契约对齐**上看，验收标准 §1.2 定义的"最低合法输入"与 `envelope_check` 实际检查的六个字面 key **不是同一套命名**，字面对齐度不完整，裸给 Q-COMM-04 定义的最低输入有较高概率被结构性拦在闸外而不是进入实测——这本身不是"架构挂了"，但会让"用 Q-COMM-04 最低输入做实测"这件事在没有额外适配（调用方把中文语义翻译成图里认的英文 key）的情况下**打不到 `skill_llm`**，需要在正式进入 P0-8 判定与后续实测设计时一并考虑。

**状态：DONE**

---

## P0-8 判定与阻断清单

### 判定

```text
NOT_READY
```

### 为什么不是 READY_FOR_EMPIRICAL_TESTING

架构里确实存在两道**真实**的代码级硬闸（P0-3(c) 的六项外壳必填闸、`returns_adapter` 的输出格式/泄漏关键词闸），说明这不是一个"完全没有工程约束、纯靠一段 Prompt 硬扛"的架构。但对照验收标准最看重的几条硬性判据——§21 的"同一运行条件下稳定产生"、§6.1 的"Critical Error = 0"与"UNKNOWN 不得悄悄变成 FACT"、§7 的"Layer A 必须带版本""不得用 Layer B 冒充 Layer C"——当前架构在**这几条硬判据对应的位置上，防线完全或几乎完全依赖模型自觉**，没有独立于模型的代码校验。在这种状态下开始花钱做 LLM 实测，测出来的"通过"或"不通过"都无法被架构本身的证据支撑，容易把"这批测试 Case 恰好没触发问题"读成"系统达标"。详见下表逐条说明。

### 阻断清单（6 条）

完整结构化清单见 [BLOCKING_LIST_v1.0.json](BLOCKING_LIST_v1.0.json)；以下为同一清单的可读版本。

| ID | 类别 | 缺什么 | 在哪个位置 | 不修的话实测会得到什么样的假信号 |
|---|---|---|---|---|
| B-01 | 配置 | `temperature`（及 `frequency_penalty`/`presence_penalty`/`seed`）未钉死，全文档零命中 | `skill_llm`/`recovery_llm` 共用的 `completion_params`（YAML 锚点 `&id001`） | 同一输入多次实测会出现分数/胜率波动；评审可能把这种波动误判为"素材本身难判"，也可能恰好一次采样"运气好"的输出通过评审，从而掩盖"系统本身不能稳定复现"这一事实——直接让 §21 的"是否能够稳定产生"这一最终问题变得无法被回答 |
| B-02 | 结构 | `returns_adapter` 只做输出**格式**校验（标记块/长度/回指/内部术语泄漏），不解析 `fact_check_status`／`used_fact_refs[]`／`fact_refs[]` 等字段内容，无法核验模型自报的事实核验结果是否真实 | `returns_adapter` 节点 ＋ `skill_llm` 系统提示词"语义事实核验"章节 | 如果测试这批素材恰好没诱发编造，会被读成"系统不会编造事实"；但这只证明"这次没编"，不证明"编了会被拦下来"——换一批素材或换一个模型版本，同样的编造可能直接流到用户面前而不被任何代码挡住，这正是"实测通过"最容易被误读成"架构达标"的一条 |
| B-03 | 依赖 | Layer A 数据源（`references/platforms.md` 等）从未被任何节点实际读取；`ref_projection` 只产出"该不该加载"的规则文字，不含文件真实内容；`context.enabled: false`；全图无检索/HTTP/工具节点 | `ref_projection` 模板节点 ＋ `skill_llm` 的 `context` 配置 | 实测中模型会稳定按提示词指令输出 `PLATFORM_SPEC_UNVERIFIED` 并用定性要求兜底，评审容易把"每次都规规矩矩降级"读成优点，而忽略更根本的问题：Layer A 在这套图里**从来没有机会被真正满足过**，因为承载它的数据通路根本没接进图里，不是测试素材没给够数据 |
| B-04 | 契约 | 对"当前最热""现在最少""最佳发布时间"一类无依据当前市场断言（G0-04 明文列为 Critical Failure），`returns_adapter` 的 `LEAK_PATTERNS` 不含这类措辞检测 | `returns_adapter` 的 `LEAK_PATTERNS` 列表 | 若测试 Case 恰好没诱发这类断言，会被记成"零命中"，但这只是"这批 Case 没诱发它说"，不是"系统结构性地不会说"；标准 §14 明确要求边界 Case 覆盖"用户要求声称当前趋势"，等真正跑到这类 Case 时才会发现——那已经是进入商业判断阶段之后，发现得太晚 |
| B-05 | 契约 | 标准 §1.3 的 12 项标准输出对象里，第 9 项"标签/话题等平台元素"在 `master_package` 输出契约里完全没有对应字段（全文穷举 grep 零命中），无从谈 APPLICABLE/NOT_APPLICABLE 判定 | `skill_llm` 系统提示词内的 `master_package` 字段清单 | 评审打 M2/M4 分时可能发现"这份产出没给标签"，如果不知道这是架构层面本来就没建这个字段，容易把这个空缺算成"模型这次漏做了"（可归因为执行偏差），而不是"这项能力这次评测范围里结构性地不产出"（需要先在架构层面补字段或给出显式 NOT_APPLICABLE 判据） |
| B-06 | 结构 | 标准 §1.3 第 12 项"发布条件/不应发布条件"没有单一显式输出字段，判断结果分散在 `release_check`／`fact_check_status`／`missing[]`／`component_return` 分支等多处，没有汇聚点 | `returns_adapter`／`delivery_finalize`／`component_return` 等多个节点共同构成，无单一承载字段 | 评审若只读 `master_package` 正文，容易漏看"这条不该发"的结论（该结论可能只体现在 Return 分支或 `fact_check_status=FAIL`，不在用户能直接读到的正文里），把"系统其实判断了不该发但没讲清楚"误记成"系统没有判断能力" |

### 分类分布

```text
配置：1（B-01）
结构：2（B-02、B-06）
契约：2（B-04、B-05）
依赖：1（B-03）
合计：6
```

**为什么这件事必须在实测之前做**：验收标准把最终问题定义为"在同一 Frontier Model、同一输入和同一运行条件下，是否能够稳定产生……专业增量"。B-01～B-06 六条里，有五条（除 B-06）直接对应验收标准里明文写出的硬性判据（§21 稳定产生、§6.1 Critical Error=0 与 UNKNOWN 不得变 FACT、§7 Layer A 必须带版本与不得用 Layer B 冒充 Layer C、§1.3 标准输出完整性）。在这些硬判据缺乏独立于模型的代码级保障之前就开始花钱做实测，得到的每一个"通过"都无法回答"是这次运气好，还是架构真的挡住了"这个问题——而这正是先看图、再花钱这件事本来要避免的。

**状态：DONE**

---

## COMPLETION CHECK

```yaml
real_behavior_verified:
  - 两份治理绑定文件 sha256 现场复算与授权值逐字节一致: PASS
  - DSL 全部 15 个节点、14 条边逐一读取，未抽样、未省略: PASS
  - 全文档对 temperature/UNKNOWN/references 等关键词做穷举 grep 复核: PASS
protected_targets_unchanged:
  - 未修改 DSL 文件: PASS（全程只读，任务结束前将复核 git diff 为空）
  - 未修改任何既有 Dify 应用、未新建 Dify 应用: PASS（零模型调用，零平台写操作）
  - 规则仓库零写入: PASS（全程只读）
side_effects_registered:
  - 零模型调用: PASS
  - pp-architecture/ 三个新文件为本任务唯一写入面: PASS
not_claimed:
  - 本任务不产生任何产品/商业结论、不评价 PP 效果好坏: 成立，全篇不出现打分或"好/不好"判断
  - 不代表本任务修复了任何缺口: 成立，全部发现均登记为缺口，未做任何代码/DSL 改动
disclosed_anomalies_not_hidden:
  - delivery_finalize 代码注释里自述的历史缺陷 M4-FND-029（recovery_llm 内部推理段曾被当成用户正文交付）：
    经核对，当前版本的 _strip_thinking() 已实现与 final_extract 等价的剥离逻辑，该缺陷在本次核对的
    版本里已修复，如实记录为"已解决的历史缺陷"，不计入 P0-8 阻断清单
  - returns_adapter 计算出的 local_block 字段只在 end_ok 的输出里被透出，未被图内任何节点用于路由或
    阻断决策；真正承担"业务交付成功与否"信号的是 delivery_finalize 的 delivery_outcome 字段
    （DELIVERED/DELIVERED_AFTER_RECOVERY/NOT_DELIVERED），已在 P0-3 正文说明，因其已有替代信号通路，
    未单独列入 P0-8 阻断清单
```

`task_final_status: DONE`
