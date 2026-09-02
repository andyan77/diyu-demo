---
task_id: DIYU-V1-THREE-SKU-PRODUCTIZATION-001
section: T1 · 拆掉三样客户用不上的东西
note: 拆的是机制、协议、字段，不是判断——判断因机制被拆而失去落点时，改写为面向用户的等价表述，本表逐条标注
---

# T1 · REMOVAL_TRACE v1.0

判据（唯一判据，逐条套）：这一条服务的是**客户**，还是**产品之间的协作**？服务客户 → 留；服务产品间协作 → 拆；两者都沾/分不清 → 停下来问。

拆除范围以三张对齐表（`sku-extraction/CONTRACT_ALIGNMENT_{P0,P1,P1_5}_v1.0.md`）的 `OUT_OF_CONTRACT` 条目为准，正文①②③是举例不是穷举（Founder 澄清，见本文档末「本轮澄清」一节）。

---

## 一、P0（Publishing & Packaging）

对齐表 OUT_OF_CONTRACT 三项：① `return_to_script[]`/`return_to_production[]`/`stale_set[]`（Return 闭环与下游失效传播）② `binding_record` ③ `entry`/`run_mode` 的 `ENTRY-07`/`DERIVE_MODE_AND_PACKAGE` 接缝协议。

### SKILL_v1.4.md → SKILL_v2.0.md

| # | 删除位置 | 删了什么 | 对应 OUT_OF_CONTRACT | 为什么服务的不是客户 |
|---|---|---|---|---|
| 1 | 「输出」块 | `return_to_script[]`／`return_to_production[]` 两行字段定义（含七项结构说明） | ① | Q-COMM-04 全文未要求"给定成片的包装方案"之外，再向 Creative Script/Production Director 发起结构化回改建议——这是通知另一组件重做，不是客户买的包装方案本身 |
| 2 | 「输出」块 | `stale_set[]` 字段定义 | ① | 本次变化使哪些下游判断失效，纯粹服务"下一个组件要不要重算"，客户看不到也用不上这份清单 |
| 3 | 整节「Return 是闭环，不是一句建议」 | 七项字段表、处置三选一表、"Return 不自动回环"、"解析失败 ≠ NONE" 三个子节 | ① | 全节讲的是"PP 发现问题时如何结构化通知别的组件"，无一句是客户可感知的包装判断 |
| 4 | 「局部失效与不反向传播」节的表格部分（"包装自身的变化不反向使 Script/Brief/PD 失效"一句 + "上游变了什么→失效的是/不失效的是"表 + 段末说明） | 整段删除；子节「发布实例纪律」**保留**并提升为独立 `##` 节 | ① | 表格描述的是"上游/下游哪个组件的判断该失效"——多组件增量重算协调，客户不需要知道这件事；「发布实例纪律」讲的是"PP 自己交付过的东西不因后续变化被悄悄改写"，这是 PP 对**客户**的版本诚信承诺，不涉及通知别的组件，予以保留（本轮澄清事项，见文末） |
| 5 | 自检第 13 条 | "每条 `return_to_script[]`/`return_to_production[]` 都写全七项了吗……" | ① | 检查的是已删除机制的完整性，机制不存在，检查随之失效；原 14/15/16 条依次改编号为 13/14/15 |
| 6 | 「用户交付块的事实纪律」段 | "、Return 的七个字段名" 短语（原句："不出现内部分级术语与内部状态码：PRE/MIXED/FINAL、KNOWN_BUT_NOT_AUTHORIZED、PLATFORM_SPEC_UNVERIFIED、STALE、Return 的七个字段名——这些留在完整 Artifact 里"） | ① | 字段名指向已删除机制，其余状态码（PRE/MIXED/FINAL 等）不受影响原样保留 |
| 7 | 「与统一能力接缝的对接」节"独有停止边界"句 | "需要改正文语义的，走 `Return`，不在这里改" → 改写为"这不是本 Skill 的职责范围——必须在交付里明确说明这一点，不在这里改" | ① | **悬空引用修复**：判断本身（"改正文语义不是 PP 的职责，PP 不能自己动手改"）保留，机制名（走 Return）去掉 |
| 8 | 「只读继承的两项」节 | "无权改目标时只做局部 `Return`，不静默改写" → 改写为"无权改目标时不得自行决定，必须在交付里明确说明这处冲突，不静默改写" | ① | **悬空引用修复**：判断（无权时不能静默改写）保留 |
| 9 | 「包装候选：数量由真实取舍决定」节 | "要改题材、钩子或叙事机制的，走 `Return`，不在包装层用换标题的方式假装解决" → 改写为"这不属于本 Skill 的职责范围，需要在交付里明确说明该回到内容制作环节处理，不在包装层用换标题的方式假装解决" | ① | 同上 |
| — | 「本版改了什么」「v1.4 在 v1.3 基础上改了什么」两张历史改动日志表 | **不动**（表内仍有 `return_to_script[]` 等字样） | — | 历史记录，不是现行机制说明；日志描述"v1.3→v1.4 曾经改了什么"这一事实本身不因 v2.0 的删除而失真，改写日志等于篡改历史 |

### DSL（`DIYU_M4_TOOL_PUBLISHING_PACKAGING_v1_4.yml` → `_v2_0.yml`）

| # | 节点/位置 | 改了什么 | 对应项 |
|---|---|---|---|
| 10 | `binding_record` 节点 | 整节点删除；`delivery_finalize → end_ok` 直接重新布线 | ② |
| 11 | `envelope_check` 代码 | 删除 `ALLOWED_ENTRIES`/`ALLOWED_RUN_MODES`/`DEFAULT_RUN_MODE` 常量、`entry`/`run_mode` 解析逻辑、"entry 不匹配即 INSUFFICIENT" 状态分支；`main()` 签名去掉 `entry`/`run_mode` 两个参数；输出字典去掉 `entry_resolved`/`run_mode_resolved` | ③（P0 的 `entry`/`run_mode` 都被点名，且 P0 只有一个入口一个模式、正文从未对其分支，全删不影响任何客户可见行为） |
| 12 | `envelope_check` 节点 `variables`/`outputs` schema | 去掉 `entry`/`run_mode` 两项输入绑定；去掉 `entry_resolved`/`run_mode_resolved` 两项输出声明 | ③ |
| 13 | 起始节点（`1788000000001`）`variables` | 去掉 `entry`/`run_mode` 两个顶层输入声明 | ③ |
| 14 | `component_return` 代码 | 去掉 `main()` 里从未被函数体使用的 `entry_resolved` 参数及其变量绑定 | 机械清理——该参数在原代码里本来就是死代码（`grep` 确认整个函数体只出现这一次，即形参声明本身），只是因为 ⑪ 删除了 `envelope_check.entry_resolved` 而产生悬空引用；`component_return` 承担的"结构缺项→自然语言追问"功能（对齐表 §1.2 判 `MATCH`，非 OUT_OF_CONTRACT）**完全未改** |
| 15 | `returns_adapter` 代码 | 删除 `R_OPEN`/`R_CLOSE`/`RET_FIELDS`/`DISPOSITIONS`/`_parse_returns()`/`_legit_block()`；`_artifact_status()` 去掉对 `rets` 的依赖；`blocked` 公式去掉 `ret_status == "PARSE_FAILED"` 一项；返回字典去掉 `returns_json`/`returns_status`/`returns_parse_note`/`returns_raw` | ①（发现"Return 闭环"不只是 SKILL.md 里的文字说明，`returns_adapter` 里确有真实代码解析 `---M4_RETURNS---` 分隔块、并据此计算 `blocked`/交付状态——只删文字不删代码会让机制"名亡实存"，删除范围据此扩大到运行时代码，理由见下方「过程记录」） |
| 16 | `returns_adapter` 节点 `outputs` schema | 去掉 `returns_json`/`returns_status`/`returns_parse_note`/`returns_raw` 四项声明 | ① |
| 17 | `delivery_finalize` 代码 | `main()` 去掉 `returns_json` 参数；两处成功/失败返回分支去掉往 `rets` 里追加 `M4-RET-PROJECTION-RECOVERED`/`M4-RET-PROJECTION-FAILED` 这两条 Return 形状记录的逻辑；四处 `return` 语句都去掉 `returns_json` 键 | ① |
| 18 | `delivery_finalize` 节点 `variables`/`outputs` | 去掉 `returns_json` 输入绑定与输出声明 | ① |
| 19 | `end_ok` 节点 `outputs` | 去掉 `binding_json`（②）、`entry`/`run_mode`（③）、`returns_json`/`returns_status`/`returns_parse_note`/`returns_raw`（①）共 6 项 API 输出声明 | ①②③ |
| 20 | `skill_llm` 用户角色提示词「接缝控制」块 | 删除 `- entry：{{#envelope_check.entry_resolved#}}` 与 `- run_mode：{{#envelope_check.run_mode_resolved#}}` 两行 | ③ |
| 21 | 同上「接缝硬约束」第 2 条 | "确有冲突时只发一条局部 Return" → "确有冲突时不得自行决定，必须在交付里明确说明这处冲突" | ①（悬空引用修复） |
| 22 | 同上「产出结构」块 | 删除 `---M4_RETURNS---...---END_M4_RETURNS---` 整块规格说明；标题"四块"改"三块" | ① |
| 23 | 同上自检块 | 第 1 条"四对标记行"改"三对标记行" | ① |
| 24 | `skill_llm` 系统角色提示词 | 随 SKILL_v2.0.md 重新派生（即 1-9 的改动自动带入，未单独二次编辑） | — |

**两个已知坑核对**：P0 的 CTA 三级接缝（「与统一能力接缝的对接」节，SKILL_v2.0.md 第 250 行起）**一字未删**，`cta_surface` 字段与三级判据表完整保留。

---

## 二、P1（Creative Script）

对齐表 OUT_OF_CONTRACT 三项：① `return_from_downstream[]`/`downstream_stale[]` ② `binding_record` ③ `entry`/`cs_run_mode` 的 `ENTRY-04`/`ENTRY-05` 显式协议字段。

### SKILL.md → SKILL_v2.0.md

| # | 删除位置 | 删了什么 | 对应项 | 为什么服务的不是客户 |
|---|---|---|---|---|
| 1 | 「运行模式」表格 | "对应入口" 列（`ENTRY-04`/`ENTRY-05` 标签），**表格其余三列（`cs_run_mode`/跑什么/输出到哪停）完整保留** | ③ | 客户只需要知道"这次要不要办锦标赛/直接进脚本"，不需要知道 M4 内部给这条路径起的协议代号 |
| 2 | 「输入」表格 | 删除 `return_from_downstream[]` 整行（"下游发回的回改建议……收到时必须逐条回应"） | ① | 首轮排查漏检，二次残留排查发现；描述的是接收另一组件结构化反馈的协议，客户不提供也不消费这一行 |
| 3 | CS-6 节 | "收到 `return_from_downstream[]` 时：逐条回应……" 段落 + 段末"完整闭环见下面「合法等价输入与局部回改」一节"交叉引用句 | ① | 同上 |
| 4 | CS-6 节内一句 | "答案回来后由 Creative Script 重新调用产出逐字稿——回改建议通过 `return_from_downstream[]` 回到这里" → 保留前半句，删除"回改建议通过……回到这里" | ①（悬空引用修复，判断"答案回来后要重新产出逐字稿"保留） |
| 5 | 「合法等价输入与局部回改」节 | 子节「`return_from_downstream[]` 的闭环处置」整节删除（处置三选一表、"不得沉默"等四条硬规则） | ① | 通知另一组件闭环处置，非客户可见 |
| 6 | 同节 | 子节「局部修改只影响真实依赖项」整节删除 | ①（同属"下游实际消费的语义键"这套下游失效传播机制，只是换了个位置表述） |
| 7 | 「与统一能力接缝的对接」节 | "从 `ENTRY-04` 或 `ENTRY-05` 直接进来，跳过了物理上游组件" → "跳过了物理上游组件直接进入本 Skill"，**后续"以下照做，一条都不减"的五条专业方法义务清单完整保留** | ③ | 跳过组件不降低质量是客户买的承诺（Q-COMM-05 §7），入口协议代号不是 |
| 8 | 「与统一能力接缝的对接」节 | "目标与事实、权限或边界冲突时只做局部 `Return`，不静默改写" → "……不得自行决定，必须在交付里明确说明这处冲突，不静默改写" | ①（悬空引用修复） |
| 9 | CS-4 节 | "回改走 `return_to_script`" → "这类回改不属于本 Skill 职责范围，需要在交付里明确说明" | ①（悬空引用修复，二次排查发现） |
| 10 | 整节「下游失效」 | 表格（内容承诺/节拍/事实引用等变化→PD/PP 哪部分失效）+ "已发布内容保留为历史，不因上游后来变化而失效或被改写" 一句，全部删除 | ① | 表格是纯粹的跨组件失效传播路由；"已发布内容"指的是 Publishing 的发布历史（P1 本身不发布任何东西），保护另一组件的历史记录属跨组件协作，不是 P1 对自己客户的承诺 |
| — | 「本版改了什么」历史改动日志表 | 不动 | — | 历史记录 |

### DSL（`DIYU_M4_TOOL_CREATIVE_SCRIPT_v1_3_TEST.yml` → `_v2_0.yml`）

| # | 节点/位置 | 改了什么 | 对应项 |
|---|---|---|---|
| 11 | `envelope_check` 代码 | 只删 `ALLOWED_ENTRIES` 常量与 `entry` 解析逻辑、"entry 不匹配即 INSUFFICIENT" 分支、`main()` 的 `entry` 参数、输出字典的 `entry_resolved`；`ALLOWED_RUN_MODES`/`DEFAULT_RUN_MODE`/`run_mode` 解析/`run_mode_resolved` 输出**完整保留**（坑一） | ③ |
| 12 | `envelope_check` 节点 `variables`/`outputs` | 去掉 `entry` 输入绑定与 `entry_resolved` 输出声明；`run_mode`/`run_mode_resolved` 保留 | ③ |
| 13 | 起始节点 `variables` | 去掉 `entry` 输入声明；`run_mode` 保留 | ③ |
| 14 | `component_return` 代码 | 去掉死参数 `entry_resolved`（与 P0 同型机械清理） | 同 P0 表 #14 |
| 15 | `binding_record` 节点 | 整节点删除；`delivery_finalize → end_ok` 重新布线 | ② |
| 16 | `returns_adapter` 代码 | 与 P0 相同重构（去 Return 块解析），仅 `CAPABILITY` 常量改为 `"CREATIVE_SCRIPT"` | ① |
| 17 | `delivery_finalize` 代码 | 与 P0 相同重构（去 `returns_json`/Return 形状记录），另加 T2 的 `fact_gate_blocked`/`market_claim_blocked` 分支（见 PORT_TRACE.md） | ① |
| 18 | `end_ok` 节点 `outputs` | 去掉 `binding_json`（②）、`entry`（③）、`returns_json`/`returns_status`/`returns_parse_note`/`returns_raw`（①）共 5 项；`run_mode` 保留 | ①②③ |
| 19 | `skill_llm` 用户角色提示词 | 删除"接缝控制"块里的 `entry` 行（`run_mode` 保留）；"接缝硬约束"第 2 条同 P0 改写；删除 `---M4_RETURNS---` 块（T2 换成 `---M4_FACT_LEDGER---`，见 PORT_TRACE.md） | ①③ |
| 20 | `skill_llm` 系统角色提示词 | 随 SKILL_v2.0.md 重新派生 | — |

**坑一核对**：`cs_run_mode ∈ {TOURNAMENT_ONLY, SELECTED_DIRECTION_TO_SCRIPT, FULL}` 三种模式、DSL 里 `ALLOWED_RUN_MODES`/`run_mode_resolved`、SKILL.md「运行模式」节的判据表与缺省推导逻辑**全部原样保留**，只删了表格里"对应入口"那一列的 `ENTRY-04`/`ENTRY-05` 标签文字。

---

## 三、P1.5（Production Director）

对齐表 OUT_OF_CONTRACT 三项：① `return_to_script[]`（七项闭环）② `binding_record` ③ `subject_domain`/`content_origin_mode[]` 原样透传给下游（**任务正文①②③未列出此项，经询问 Founder 确认本轮一并拆**，见文末「本轮澄清」）。

**P1.5 的 `entry`（`ENTRY-06`）/`run_mode`（`PLAN`/`MANIFEST`）未出现在对齐表 OUT_OF_CONTRACT 里，本轮完全不动**——这是 P1.5 自己"可以被直接进入"的合法能力，不是路由残留。

### SKILL.md → SKILL_v2.0.md

| # | 删除位置 | 删了什么 | 对应项 | 为什么服务的不是客户 |
|---|---|---|---|---|
| 1 | 「输出」块 | `subject_domain 原样透传给下游` 与 `content_origin_mode[] 原样透传给下游` 两行；**`subject_domain` 在"输入"表里"由上游原样透传，决定加载 `industry-conditions.md` 哪一段"的用途未受影响，原样保留** | 对齐表第 3 项 | "透传给下游"服务的是"本段和 Publishing 都要按同一个值加载参考文件"这件跨组件协调，不是客户看得到的产出；`subject_domain` 自身用于选择本段该读哪份行业参考资料，这是客户买的专业判断的一部分，两者是同一字段的两种用途，只拆前者 |
| 2 | 「输出」块 | `return_to_script[]` 七项字段定义整段删除 | ① | 同 P0/P1 |
| 3 | 整节「Return 闭环」 | 处置三选一表、四条硬规则，全部删除 | ① | 同上 |
| 4 | 「不重复执行，不推翻历史」子节 | "已发布内容与旧 manifest 保留为历史，不因上游后来的变化而失效或被改写" → 删去"已发布内容"（Publishing 的发布历史，P1.5 本身不发布），改为"旧 manifest 保留为历史"；"修复指向最高失效层：上游那句事实本身有问题，就回上游（走 `Return`），不在下游单元里打补丁绕过去" → 改写为"……就在产出里明确指出这是上游事实问题、需要回到内容制作环节处理，不在下游单元里打补丁绕过去" | ①（悬空引用修复 + 跨组件历史保护剥离） |
| 5 | 整节「下游失效」 | 表格（局部制作单元变化→包装受影响等）+ "已发布内容及其准确发布实例保留为历史"一句，全部删除 | ① | 表格是纯跨组件失效传播路由；"已发布内容"同 #4，指向 Publishing 的历史 |
| 6 | PD-4 核心判断 | "操作失败了也留——那是真实结果，走 `return_to_script[]`，不是重拍到成功为止" → "……需要在方案里如实反映，不是重拍到成功为止" | ①（悬空引用修复，二次排查发现） |
| 7 | 「默认失败模式对照」表 | 删除两行："发出回改建议之后，自动把上游重跑一遍 \| Return 闭环"、"Return 解析失败，输出一个空数组当作'没有回改' \| Return 闭环" | ① | 这两条失败模式描述的正是被删除的 Return 协议本身如何被误用，机制不存在，失败模式随之不适用（二次排查发现） |
| 8 | 自检第 16 条（原为最后一条，删除后无需改编号） | "每条 `return_to_script[]` 七项都写满了吗……" | ①（二次排查发现） |
| 9 | 「与统一能力接缝的对接」节 | "本段无权改目标，冲突时只做局部 `Return`，不静默改写" → "……冲突时不得自行决定，必须在交付里明确说明这处冲突，不静默改写" | ①（悬空引用修复） |
| — | 「本版改了什么」历史改动日志表 | 不动 | — | 历史记录 |
| — | 「与统一能力接缝的对接」节"本段不调用任何其它能力应用。组合由上层接缝按显式计划编排" | **不动** | — | 未被对齐表点名；陈述的是"本段自己不会去调别的能力"这一边界事实，即便"上层接缝"字面提到编排层，句子本身对客户是有效信息（本组件不会暗自串联别的组件），删除会制造误导 |

### DSL（`DIYU_M4_TOOL_PRODUCTION_DIRECTOR_v1_3_TEST.yml` → `_v2_0.yml`）

| # | 节点/位置 | 改了什么 | 对应项 |
|---|---|---|---|
| 10 | `envelope_check`/`component_return` 代码 | **完全不动**（`entry`/`run_mode` 未被对齐表列为 OUT_OF_CONTRACT） | — |
| 11 | `binding_record` 节点 | 整节点删除；`delivery_finalize → end_ok` 重新布线 | ② |
| 12 | `returns_adapter` 代码 | 与 P0 相同重构，`CAPABILITY` 改为 `"PRODUCTION_DIRECTOR"` | ①（对齐表第 3 项的 `subject_domain`/`content_origin_mode[]` 透传不在 `returns_adapter` 代码里出现，无需改动） |
| 13 | `delivery_finalize` 代码 | 与 P0 相同重构，另加 T2 的 `fact_gate_blocked`/`market_claim_blocked` 分支 | ① |
| 14 | `end_ok` 节点 `outputs` | 只去掉 `binding_json`（②）、`returns_json`/`returns_status`/`returns_parse_note`/`returns_raw`（①）共 5 项；`entry`/`run_mode` **保留** | ①② |
| 15 | `skill_llm` 用户角色提示词 | "接缝控制"块 `entry`/`run_mode` 两行**均保留不变**；"接缝硬约束"第 2 条同前改写；`---M4_RETURNS---` 块删除，换成 `---M4_FACT_LEDGER---`（见 PORT_TRACE.md） | ① |
| 16 | `skill_llm` 系统角色提示词 | 随 SKILL_v2.0.md 重新派生 | — |

---

## 触发「停下来问」的条目

本轮共 1 次调用 `AskUserQuestion`，一次问了 3 个具体点，均在开始任何文件编辑前提出：

1. **P1.5 对齐表第 3 项**（`subject_domain`/`content_origin_mode[]` 透传）是否本轮一并拆——正文①②③未列出，拿不准是否算"自行扩大"。
2. P0「局部失效与不反向传播」节，`stale_set[]`/失效传播表 vs.「发布实例纪律」子节如何切分——对齐表只点名了前者。
3. 删除 `return_to_script[]` 等字段后，正文里依赖它作为解决路径的判断规则（如 PP-3 第 3 步）变成断链引用，如何处理。

**Founder 裁决**：三项均按本文档的处理方式执行；并给出两条通用口径：① 对齐表本身才是拆除清单的权威来源，正文①②③是举例不是穷举，凡对齐表标了 `OUT_OF_CONTRACT` 的都在本轮范围内；② 拆的是机制/协议/字段，不是判断——判断因此失去落点时改写为面向用户的等价表述，不随机制一起删，每处这样的改写记入本文档。

## 本轮澄清（供下一次同类判断复用）

- 判断某段文字是否 OUT_OF_CONTRACT，不看它是否恰好落在某个带"下游"/"Return"字样的小节标题下，而要看它保护的对象是"本 SKU 自己对客户的承诺"还是"另一个组件的状态"——P0「发布实例纪律」保护的是 P0 自己已交付内容的版本诚信，保留；P1/P1.5「下游失效」节里同样出现的"已发布内容保留为历史"，保护的是 **Publishing**（另一组件）的发布历史，删除。
- 一个字段可能同时有"内部专业判断输入"与"跨组件透传输出"两种用途（如 P1.5 的 `subject_domain`）：只拆输出用途那一行，不動该字段在其他地方的合法输入用途。
- 悬空引用（判断规则原本靠"走 Return"这类机制名给出落点）一律改写为面向用户的等价表述，不随机制一起删；每处改写在本文档逐条记录「原判断是什么 → 改成了什么」。
- 「默认失败模式对照」这类举例表格里，如果某个失败案例本身就是"如何误用被删除的机制"，案例连同其失效同伴一起删，不保留空对照。
