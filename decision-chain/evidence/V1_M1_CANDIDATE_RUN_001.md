# M1 候选环境 · 真实运行记录 001

`task_id: DIYU-V1-M1-NATURAL-CONTEXT-001`

## 一、环境

- Dify：本机自托管 1.16.1（`/home/faye/dify/docker/`），与 A-0～A-4 证据同一实例
- App：`DIYU V1 M1 Natural Context Candidate v0.1`，id `dd638b91-d39f-4e92-a984-6ad1ab809119`，advanced-chat
- 工作流版本：v0.5（快照扩展 evidence_bundle[]／gaps[]，Founder 本人 2026-08-25 在控制台完成导入与发布）；历史版本 v0.1～v0.4 未删除，可随时回退
- 节点：`m1_start → m1_shadow(llm) → m1_compiler(code) → m1_save_snapshot(assigner) → m1_chat_llm(llm) → m1_answer`
- 源码：`decision-chain/workflows/m1_context_compiler_v0.1.py`（编译器）＋ `decision-chain/workflows/build_m1_candidate_dsl_v0.1.py`（DSL 生成脚本，可重新生成同一份 DSL）

## 二、RUN-001：任务陈述 + 点名能力

| 项 | 值 |
|---|---|
| 输入 | 「我想为账号规划一下长期人设和分工」 |
| conversation_id | `9f9922aa-8114-448a-a032-ee7dd642cee7` |
| message_id | `523e30c1-c998-4297-8daa-8444c97010b6` |
| 影子节点判定 | `route_intent=FOCUS`／`current_task_text` 原话捕获／`temporal_scope=LONG_TERM`／`requested_capability=MATRIX` |
| 编译器判定 | `call_intent.needed_capabilities=["MATRIX"]`，`MATRIX.status=DEGRADED_INPUT`（如实：只有任务文本，Matrix 六类必需输入未采集，未伪装满足） |
| 回复要点 | 正确说明"这是候选环境的意图判定，不代表主流程已放行或开始执行"；未声称已执行；自然追问账号方向 |
| 结果 | **PASS** |

## 三、RUN-002：首次侧问测试（发现真实缺陷）

| 项 | 值 |
|---|---|
| 输入 | 「主要是做女装穿搭内容，另外顺便问一下——如果不做剧情类的内容会不会不好起量？」 |
| message_id | `7e7d74cc-89b7-4061-b58e-aa51416cfb73` |
| **缺陷** | `m1_chat_llm` 直接给出了具体的内容策略专业判断（"不做剧情类，不会不好起量……应该做单品一衣多穿、场景化内容……"），越界进入 Creative Script / Content Brief 的专业判断范围，违反设计文档"M1 只决定需要哪项能力，不替专业组件作深度判断" |
| 根因 | `m1_chat_llm` 系统提示词只约束了"不编造失败原因""不暴露内部字段"，未显式禁止给出专业内容策略判断 |
| 处置 | 系统提示词新增边界段落，明确禁止给专业策略结论，改为引导"是否要交给专业能力判断"；重新导入（DSL v0.2）、重新发布 |

## 四、RUN-003：修复后复验（同一场景）

| 项 | 值 |
|---|---|
| 输入 | 与 RUN-002 完全相同 |
| conversation_id | `37fb3665-1739-465a-ab51-0351bb3093f4` |
| message_id | `a5d19eaa-5c9d-4098-b402-02a3861e6df6` |
| 回复要点 | "这属于内容方向和起量策略上的专业判断，不是我这个环节能直接给结论的……要不要现在就帮你把这个问题提给专业能力，让它来给个判断？" |
| 结果 | **PASS**——不再给出专业判断，正确引导至能力调用 |

## 五、已知限制（如实记录，不是遗漏）

- 本轮只覆盖 P0 最小切片（9 个扁平信号字段），未实现设计文档 §二 完整 14 条语义 × 5 维度；后续需要更多真实运行来扩展和验证。
- `call_intent` 的 `DEGRADED_INPUT` 判据目前只能识别"是否有任务文本/目标"，未对照 CAP-01 六类必需输入逐项判断——如实标注，不冒充已满足。
- A-0～A-4 受控等价输入回归：**部分覆盖**，见 §七～§九。A-1（接受并继续）／A-3（撤销最近一次接受）／A-4(b)（撤销无对象如实拒绝）依赖"按槽位跟踪产物接受状态、可撤销"这一概念，M1 P0 的 9 字段扁平快照里完全没有这个概念（`confirmation_signal` 只是单一的全局 AFFIRM/DECLINE，不是按 slot 的 `last_acceptance`/`REVOKE`）——这不是遗漏，是 Founder 已裁决的范围边界的结构性后果（该状态机属于 `v1_state`，M1 不复用不重建）。如实记录为 M1-AC-12 当前无法在 M1 候选环境里被满足的部分，留给评估方判断。
- 未做独立审查（Reviewer）；本记录属于执行侧自验证据。

## 六、正式化单测时发现的真实问题（新增，非遗漏）

将口头验证固化为 `decision-chain/workflows/test_m1_context_compiler_v0.1.py`（17 个用例，全绿）过程中，
发现一处此前未被观察到的行为，如实记录，不当场重新设计：

- **现象**：`open_threads` 的 `OPEN → SURFACED` 状态转换目前只在"同一轮内"发生，从未观察到跨轮仍为 `OPEN`
  的情形。根因是 `PATCH_KEYS` 每轮只支持一个 `side_question` 字段——新线程诞生时必然是当轮唯一的
  `OPEN` 线程，会在同一次 `main()` 调用内被 `_dialogue_directive` 立即标记为 `SURFACED` 后才序列化输出。
- **后果**："先记录用户的追问、留到下一轮系统主动重提"这一设计意图（呼应 `v1_state` 的 OPEN/SURFACED
  二值语义）目前在持久化快照里没有被观察到的实际效果——每个线程都是"当场创建、当场表面化"。
- **是否阻塞**：不阻塞。当场把线程写进本轮 `dialogue_directive` 并不违反任何已冻结约束（不是伪造完成、
  不是越界给专业判断），只是没有实现"跨轮延迟提醒"这个更完整的语义。
- **处置**：不在本次测试形式化范围内擅自改动生成逻辑（是否应该改成"确认对话 LLM 真的说出口了才转
  SURFACED"，或"至少跨一轮再表面化"，属于设计判断）；留作后续迭代的已知限制，测试文件
  `test_new_thread_each_turn_gets_surfaced_same_turn_real_finding` 锁定当前真实行为，防止后续改动
  在无感知的情况下改变这一语义。

## 七、A-0～A-4 受控等价输入回归（第一轮，v0.2 上运行，发现真实缺陷）

A-0～A-4 原始定义与真实证据见 [`V1_DIALOGUE_ORCHESTRATION_REPAIR_001_EVIDENCE.md`](V1_DIALOGUE_ORCHESTRATION_REPAIR_001_EVIDENCE.md) §5——那是**主 Chatflow**（`v1_state`/`v1_shadow`/`v1_chat_llm`）的受保护行为基线，包含按槽位跟踪产物接受状态（`USER_ACCEPTED`/`VALIDATED`）、真实调用 Skill Tool 等 M1 P0 完全不涉及的机制。M1 候选环境是独立评估环境，不复用、不重建该状态机（见 §四已知限制）。因此这里做的是**受控等价**，不是逐字重放：只对 M1 自己 9 字段快照里真实存在的语义（`route_intent`／`confirmation_signal`／`requested_capability`／`side_question`）设计对应场景，A-1/A-3/A-4(b) 因为依赖 M1 没有的"按槽位接受/撤销"概念，结构性地无法在这里做等价回归（见 §五）。

| 场景 | 对应 A-0～A-4 | 输入 | conversation_id / message_id | 结果 |
|---|---|---|---|---|
| CE-A0 | A-0 明确确认并授权 | 「我确认要为账号规划长期人设和分工，请调用账号矩阵能力开始。」 | `20cba09c-f6ff-4042-87ed-043184d1eba2` / `f13784b2-fd0a-4e9e-bd5f-880b776d6302` | **发现真实缺陷**（见下） |
| CE-A2 | A-2 一轮两件事 | 「我想为账号规划人设和分工，另外顺便问一下——如果几个账号完全不发布日常内容会不会显得不真实？」 | `fa32f2cd-e76b-465a-a894-bbcc1af23f78` / `60149fe4-8a7f-4d81-b251-2a7e5c871afc` | **发现同一真实缺陷**（见下） |

**缺陷（真实发现）**：`m1_compiler._dialogue_directive` 把内部枚举代码原样拼进给 `m1_chat_llm` 的指令文本（如 `"用户点名的能力（MATRIX）……"`）。CE-A0 的回复把它转述成"账号矩阵（MATRIX）"（尚可读，但仍是内部代码泄漏）；CE-A2 的回复直接写成"你提到'MATRIX'这个能力"——**用户在原话里从未出现过"MATRIX"这个词**，`requested_capability=MATRIX` 是影子节点从"人设和分工"语义推断出来的，不是用户点名说出的字面内容。这既违反 `m1_chat_llm` 系统提示词自己的边界（"不要出现……Prompt 内部字段名"），也构成对用户说过什么的不实归因。证据来源：两次运行 `metadata.reasoning.m1_shadow` 字段完整记录了影子节点的推理过程与最终字段取值（Dify 对 DeepSeek 推理模型会把思维链一并返回），可与最终回复文本对照核实。

**根因**：`_dialogue_directive` 里两处字符串拼接直接使用 `requested_capability`（枚举值）和 `info["block_reason"]`（枚举值），没有做人类可读的中文标签转换，且用"用户点名的能力"这一措辞默认了"点名"一定是用户逐字说出，未考虑该字段也可能来自语义推断。

**处置**：见 §八。

## 八、修复与复验（v0.3）

`decision-chain/workflows/m1_context_compiler_v0.1.py` 新增 `CAPABILITY_LABEL_ZH`／`BLOCK_REASON_LABEL_ZH` 两个人话标签映射表；`_dialogue_directive` 改用标签而非原始枚举代码，措辞从"用户点名的能力（X）"改为"当前识别到你想调用的能力是 X"，不再断言该内容一定是用户逐字说出。`call_intent_json`（机器可读、不面向用户展示）里的原始代码不受影响，仍原样保留。新增单测 `TestDialogueDirectiveNoRawCodeLeak`（4 个用例）锁定：枚举代码不进入 `dialogue_directive`、不再断言"用户点名"、`block_reason` 代码同理有人话标签、`call_intent_json` 的机器可读代码不受修复影响。重新生成 DSL（`build_m1_candidate_dsl_v0.1.py`），`POST /console/api/apps/imports` 定向导入同一 `app_id`（非新建），`POST .../workflows/publish` 发布为 v0.3。

同一枚 API Key 对同样两个场景发起全新对话复验，并新增一个"普通咨询不误触发专业模块"的受控等价检查（对应主证据文档 §6 最小回归的同名检查项）：

| 场景 | 输入 | conversation_id / message_id | 内部代码泄漏扫描 | 结果 |
|---|---|---|---|---|
| CE-A0 复验 | 同 §七 CE-A0 | `3cc7f72e-d79e-4800-9462-c8aa2375fd59` / `b911d9a2-ea83-4caf-966c-4253aea2253e` | 无 | **PASS**——回复用「账号矩阵」而非「MATRIX」，且未声称已执行 |
| CE-A2 复验 | 同 §七 CE-A2 | `158c2457-2919-43c4-ac25-237f3a63b9ca` / `aab90399-d9ab-433b-ba0f-6e2ca2ef74a6` | 无 | **PASS**——两件事都被回应，侧问未被当场给出专业结论，也未出现内部代码 |
| CE-general（新增） | 「我们现在什么任务都还没定，先随便聊聊行业趋势吧。」 | `8564c2a7-e888-4ff6-9af1-8e9ddbe5efac` / `1d13e824-be36-4723-b7ec-8321c72c5e9e` | 无 | **PASS**——保持 DISCUSS，未误判为任何能力调用请求，未给专业策略结论 |

（关键词扫描覆盖 `MATRIX`/`CAMPAIGN`/`CONTENT_BRIEF`/`CREATIVE_SCRIPT`/`PRODUCTION_DIRECTOR`/`PUBLISHING_PACKAGING`/`NO_PHYSICAL_ENTRY_YET`/`NO_CURRENT_TASK_STATED`/`NO_TASK_OR_GOAL_STATED`/`DEGRADED_INPUT`/`BLOCKED`，三次回复均未命中。）

## 九、M1-AC-12 当前诚实状态（不代表最终验收结论，供评估方判断）

- **可满足部分**：A-0/A-2 的受控等价语义、以及"普通咨询不误触发专业模块"最小回归，已在 M1 自己的候选 App 上真实运行验证，见 §七、§八。
- **结构性无法满足部分**：A-1（接受并继续）／A-3（撤销最近一次接受）／A-4(b)（撤销无对象如实拒绝）依赖按槽位的产物接受状态机，这是 `v1_state` 的机制，M1 P0 设计上明确不复用、不重建（见设计文档 §四已知限制、`known_limitation` 字段）。在 M1 现在的 9 字段快照上，这三项**无法**做出真正意义上的等价回归——勉强映射只会制造"看起来测过"的假象。
- **未自然复现部分**：A-4(a)（Shadow 分类失败 fail-open）的等价保证已由 17 个单测里的 `TestWholePatchRejection`（3 个用例）在编译器层面**确定性**证明；但"影子 LLM 在真实对话里自然产生一次非法输出"这件事本身不可控制地复现（原始证据文档也是"自然撞见"，不是人为构造），M1 自己的 5 次真实运行（RUN-001~003 + CE-A0/A2 及复验）至今未自然撞见过一次。
- **结论**：M1-AC-12 目前处于**部分满足**状态，不宜标记全绿 PASS；A-1/A-3/A-4(b) 那部分的满足与否，取决于 Founder/独立审查如何理解"M1 候选环境"与"最终真正接入主决策链后的产物"之间的验收边界——这是需要评估方判断的问题，执行侧不越权替其下结论。

## 十、快照 v0.2 扩展：account_stage／expression_discretion／capacity_triad（单测 + live 均已验证）

- **代码变化**：`m1_context_compiler_v0.1.py` 新增 8 个扁平 patch 字段（`account_stage_text`／`plot_allowed`／`remix_allowed`／`conflict_allowed`／`controversy_allowed`／`desired_output_text`／`cycle_available_text`／`baseline_text`），对应设计文档 §二 #5/#6/#7（账号阶段、表达裁量、产能三分）。刻意只选扁平字符串/枚举承载，未触碰 `evidence_bundle[]`/`market_observations[]`/`gaps[]`/`runtime_evidence[]` 等数组型、多维度语义——那部分是设计文档 §七 登记的"嵌套结构可能让候选 LLM 结构化输出不稳定"未决风险，本批不处理。
- **向前兼容**：新增 `main()` 内的快照顶层键补齐逻辑，确保 v0.3 及更早持久化的旧会话快照（缺少这三个新字段）能被正常读取、补齐、继续合并新 patch，不丢旧数据、不抛异常。
- **`content_task` 投影同步更新**：`account_stage`／`expression_discretion`／`available_capacity` 三项从原先的 `NOT_CAPTURED_IN_P0_SNAPSHOT` 占位改为真实透传快照值；`evidence_and_gaps` 仍标占位（未落地）。
- **单测验证**：新增 14 个用例（`TestV0_2SnapshotExpansion` 5 个、`TestContentTaskProjection` 内 1 个替换 + 1 个新增），全部文件合计 **35 个用例，全绿**（`python3 decision-chain/workflows/test_m1_context_compiler_v0.1.py -v`）。
- **live Dify 复验阻塞的解除**：执行侧的控制台会话因本机 Docker 容器重启失效（见下方"曾经阻塞"记录），且未持有 Founder 明文密码，不重新索取；改为把重新生成的 DSL 文件（`m1_candidate_dsl_v0.4.yml`）交给 Founder，由 **Founder 本人在浏览器里登录控制台、完成导入与发布**（2026-08-25，Founder 直接操作，执行侧全程未接触登录凭证）。发布完成后，执行侧继续用既有的 App 级 API Key（`app-fHRsI6...`，非控制台会话）跑真实回归。
- **CE-v0.2-01（真实运行，`conversation_id 86d9a2fa-6176-48b2-b0d8-f62619dd9946`）**：
  - 第一轮 `message_id bfa61aa3-e6ec-4964-b9c3-1a3ca53b63f0`：用户一次性说出账号阶段、剧情裁量、争议裁量、周期产能、基线产能五项信息。`m1_shadow` 推理轨迹显示其正确抽取：`account_stage_text="刚起号，还没有稳定粉丝"`、`plot_allowed=NOT_ALLOWED`、`remix_allowed=UNSTATED`、`conflict_allowed=UNSTATED`、`controversy_allowed=ALLOWED`、`desired_output_text=""`（用户未提及，正确留空，未编造）、`cycle_available_text`／`baseline_text` 分别贴合原话。回复诚实说明"系统这边还没有记录任何具体任务内容"，未泄漏内部字段，未越界给专业判断。
  - 第二轮 `message_id`（同会话，`query: "好，那就先按这些情况，帮我规划一下账号的长期人设和分工。"`）：**`m1_shadow` 的推理轨迹直接逐字复述了第一轮持久化后的 `snapshot_json` 内容**——`账号阶段：刚起号，还没有稳定粉丝，confirmation: SYSTEM_TENTATIVE`／`表达裁量：plot_allowed: NOT_ALLOWED, remix_allowed: UNSTATED, conflict_allowed: UNSTATED, controversy_allowed: ALLOWED`／`产能三元组：desired_output: null, cycle_available: "这个周期我们团队人手紧张，大概只能做2条", baseline: "长期稳定产出能到每周4条"`——与第一轮写入值逐项一致，**证明三组新字段确实被正确持久化、跨轮次未丢失未损坏**；`confirmation` 也如预期原样保持 `SYSTEM_TENTATIVE`，未被伪造成 `USER_CONFIRMED`。回复正确识别用户在提出执行请求，如实说明"具体规划需要交给专业能力"，未越界给出人设/分工结论，未泄漏内部字段。
- **结论**：v0.2 快照扩展现已同时具备单测证据（35/35）与真实 Dify 端到端证据（CE-v0.2-01 两轮），候选 App 当前运行版本为 v0.4。

### （历史记录，问题已解决，保留过程）live 复验曾被阻塞

DSL 用 `build_m1_candidate_dsl_v0.1.py` 重新生成后，执行侧尝试用已保存的控制台会话导入/发布，但本机 Docker 里的 `docker-api-1` 等容器在会话过程中发生过一次重启（`docker ps` 显示 created 3 天前、Up 8 小时），推断服务端会话/刷新令牌存储被清空——用于免密码续期的 `refresh_token` 机制（`POST /console/api/refresh-token`）虽返回 `{"result":"success"}`，但用刷新后的 `access_token` 访问 `/console/api/apps` 仍返回 `401`。执行侧未持有 Founder 明文密码，按既定的凭据最小暴露原则不重新索取，也未尝试绕过——改为交给 Founder 本人操作，见上方"解除"记录。

## 十一、快照 v0.3 扩展：evidence_bundle[]／gaps[]（实现）＋ market_observations[]／runtime_evidence[]（如实 DEFER）

本轮处理设计文档 §二 表格第 9/10/11/14 行，即 v0.2 之后剩余的四个数组型、多维度快照字段。做法：先用独立的设计→对抗审查两步产出方案（对抗审查逐字核对了 worktree 内三份源码、设计文档全文、共享合同一 §三 全文，以及 §七 引用的 `v1_shadow` 既有证据行，纠正了原方案里两处会实际违反冻结硬约束/仓库红线的地方和三处会当场出错的实现细节），再落地实现，再用三路独立复核（重新跑单测、对抗式合规审查、DSL 同步核对）验证实现——过程本身不在这里复述，只记录会影响验收判断的结论。

**四个字段的处置**：

- `evidence_bundle[]`（#9，可用事实/偏好/参考/系统判断及缺口）：**实现**。采用设计文档 §七 官方登记的降级路径——`v1_shadow`（同类组件）设计说明已记录 DeepSeek V4 Flash 不支持嵌套对象（`V1_DIALOGUE_ORCHESTRATION_REPAIR_001_EVIDENCE.md:68`），本批不重新验证这个已有先例的风险，直接采用"LLM 只出扁平粗粒度信号，五维度由确定性代码组装"。新增 3 个 patch 字段：`evidence_text`（用户原话，不润色不补充）、`evidence_nature`（FACT｜PREFERENCE｜REFERENCE｜UNSTATED，刻意不含 `SYSTEM_INFERENCE`——系统推断只能由代码写入，模型不得给自己的复述贴系统判断标签）、`evidence_scope`（比合同词表多一个 `UNSTATED` 哨兵，不替用户推断适用层级）。写入是纯追加，永不修改既有条目；五维度里 `provenance` 恒 `USER_DIRECT`、`confirmation` 恒 `SYSTEM_TENTATIVE`、`availability` 恒 `AVAILABLE`（三者在 P0 环境里结构性为真：无 Tool 节点、无联网、`file_upload.enabled=False`，写成其他值即伪造来源）。两条冻结硬约束的落实方式：约束一（系统推断不因持久化升级为用户确认事实）靠 `confirmation` 是字面常量、代码无任何路径写入 `USER_CONFIRMED`；约束二（参考资料和历史产物不得覆盖已确认事实）靠"纯追加、永不修改既有条目"这个结构本身天然满足，**不需要一个独立的运行时守卫**——首版实现为此写了一个 45 行、生产代码零调用方的 `_may_modify_existing_evidence` 守卫函数，被对抗式合规审查判定违反"不得为未来想象增加无必要结构"（宪法第12条），已删除。
- `gaps[]`（#11，缺失信息与已降级项）：**实现，零新增 LLM 字段**。完全由确定性代码（`_compute_gaps`）从既有快照状态推导——None 值、`UNSTATED` 哨兵、本批明确不实现的结构性语义清单（`subject_scope`／`business_goal_categories`／`cycle_ref`／两个 DEFER 数组／确认与可用性维度的单值限制）。`compute_call_intent` 里此前硬编码为 `[]` 的 `continuation.non_blocking_gaps` 首次有了真实计算，是共享合同一 §五"只追问真正阻塞的一项，其余带缺口继续跑"第一次有机制载体而非只有注释声明。
- `market_observations[]`（#10，市场观察）／`runtime_evidence[]`（#14，运行中新增的外部证据）：**本批 DEFER，不实现**，理由是结构性的、不是"没时间做"：M1 候选 DSL 没有 Tool 节点、`file_upload.enabled=False`、无联网（已逐节点核对），这两项语义的消费者 CAP-03/CAP-05 又正是当前 `NO_PHYSICAL_ENTRY_YET`；且关键子字段（`observed_at`／`obtained_at`／`validity`）如果由编译器代填，要么是伪造采集时间，要么是新增自动评分器，两者都是仓库红线。处置：两个字段的快照值恒为 `[]`，同时由 `gaps[]` 恒定登记一条 `DEGRADED / NOT_CAPTURED_IN_P0_SNAPSHOT`（不能只留空数组——孤立的 `[]` 会被下游读成"查过了，没有"，是不实主张，已由单测锁定这条"空数组必须配缺口条目"的口径，不只是注释）。

**对抗式合规审查发现并已修复的问题**（不是走过场，逐条列出）：

1. **派生数据被冗余持久化**：`gaps[]` 空快照上共 20 条，其中 8 条（`P0_STRUCTURAL_GAPS`）内容永远不变，却在首版实现里每轮都被序列化进 Dify 会话变量，实测占某次持久化快照总字节数的 73%。修复：`_compute_gaps(snapshot, include_structural=True|False)` 拆成两档——`main()` 只持久化随对话状态真正变化的动态子集（空快照 12 条），`project_content_task()` 等需要完整合规视图的调用点仍取全部 20 条（设计文档 §三 要求 `evidence_and_gaps` 完整、不摊平，这个要求在这里被保留，不因为持久化优化而丢信息）。
2. **零调用方的守卫代码**：见上方 `_may_modify_existing_evidence` 的删除记录。
3. **执行侧在代码注释里给验收判据写解释，未同步设计文档**：首版实现在模块 docstring 里新增"纪律 5"，主张"整体拒绝"规则不适用于 `evidence_nature=UNSTATED` 这种情况（改为只丢这一条证据，本轮其余内容照常合并——这个**行为**本身是对的，和共享合同一 §五、CLAUDE.md"资料不足时不得整任务拒绝"一致，继续保留）。但这处解释断言时的措辞把它当成了既定新纪律来写，而设计文档 `V1_M1_TASK_CONTEXT_COMPILER_DESIGN_v0.1.md:142`（"纪律 2"，逐字是 AU-05 的通过判据原文）并未同步。已改为在代码里明确标注"未决、需 Reviewer/Founder 核对，不由执行侧单方认定为新纪律"，行为不变，只改措辞的确定性程度。**这一条需要 Reviewer/Founder 核对**：是否需要把这处收窄补进设计文档 §六.2，还是维持现状作为已知的表达简化。
4. 一处防御风格不一致（`_merge_evidence_item` 未对 `evidence_bundle` 做防御性取值，和文件里其他函数风格不一致）：已修复，无实质影响（P0 里该字段不可能缺失）。

**本批不擅自处理、明确留给 Reviewer/Founder 的事项**：

- `market_observations`／`runtime_evidence` 的 DEFER 判断本身——这两项是共享合同一 §二 冻结的 14 条语义之一，"用 gaps[] 机器可读登记为已降级"是否构成本批可接受的 P0 状态，属于治理判断，不由执行侧单方宣布"已完成"。
- 每轮只能捕获一条证据（`evidence_text` 单值）：用户一轮说三件事会丢两件，是否需要加 `evidence_text_2`/`_3`（仍是扁平字段，不引入嵌套）是取舍题，本批不擅自扩展。
- 设计文档 §三 的五维度取值空间与共享合同一 §三 有两处既有的不完全对齐（可用性维度合同列 6 值、设计文档只落 5 值，缺"不适用"；作用域维度合同末尾还有"生效时间是否仍有效"，设计文档四值枚举未承载）。两处都是设计文档 v0.1 既有取舍，不是本批引入，但 `evidence_bundle[]` 正是这组枚举的直接落地对象，从本批起开始承压。本批未改动真相源枚举，如实登记，交 Reviewer 裁决是否需要补进设计文档。
- "用户明确拒绝提供某项"场景（EP §6 场景 5／M1-AC-05 的"拒绝补充后合法降级"）在本批仍不可表达，因为轮级 `confirmation_signal` 无法归因到具体字段，而按字段确认状态机是 v0.2 已裁决"需要设计判断、不擅自决定"的事项，本批延续同一裁决，不新增一个半截状态机。

**测试**：35 → 88（首版实现）→ 83（对抗审查修复后，删除 8 个只测已删除守卫函数的用例，净增 48）。`python3 decision-chain/workflows/test_m1_context_compiler_v0.1.py -v` → `Ran 83 tests ... OK`，独立复核过两次（对抗审查阶段一次、修复后本次一次），均 0 失败。

**live 验证（CE-v0.3-01，真实运行，`conversation_id 11d69307-d3c9-4505-b64e-604280493667`）**：Founder 本人在浏览器控制台完成 v0.5 导入与发布（覆盖 v0.4，见 L5 SE-017）后，执行侧用既有 App API Key 跑了两轮真实对话：

- 第一轮 `message_id 9c3e51f7-a91c-4a3b-9803-8c6c5a0b8032`：用户陈述「我们家是杭州本地的女装买手店，已经开了三年，主要卖设计师联名款」。`m1_shadow` 推理轨迹显示正确判定 `evidence_nature=FACT`、`evidence_text` 贴合原话；`evidence_scope` 推理轨迹显示模型确有认真权衡（"用户没有明确说明适用到哪一层……但'我们家'inherently 指向本账号"），最终选了 `THIS_ACCOUNT` 而非默认 `UNSTATED`——这是模型基于"这是在描述自己账号"这一语境做出的合法枚举取值，不是编造，但比设计口径鼓励的保守默认更主动，记录为一个真实观察，供 Reviewer 判断这条界线是否需要收紧提示词。回复正确说明尚未形成具体任务，未越界给专业判断（"如果涉及账号定位、内容方向这类专业判断，那需要交给对应的专业能力"），未泄漏内部字段。
- 第二轮 `message_id ae2ead36-b4fc-4d52-bdf4-8bb05e63b4df`（同会话）：用户陈述「另外，我个人比较喜欢参考@设计师薇薇安 的选品逻辑，他家风格跟我们很像」。**`m1_shadow` 的推理轨迹逐字复述了第一轮持久化后的证据条目**——"之前还有一条证据 ev_001：我们家是杭州本地的女装买手店，已经开了三年，主要卖设计师联名款……账号阶段'已经开了三年'是 SYSTEM_TENTATIVE"，与第一轮写入值完全一致，`id` 命名规则（`ev_%03d`）与 `confirmation` 值均如实持久化、未被伪造成 `USER_CONFIRMED`；本轮新证据被正确判定为 `evidence_nature=REFERENCE`（而非 FACT 或 PREFERENCE，推理轨迹显示模型认真区分了三者的边界），`evidence_scope` 这次正确留了 `UNSTATED`，推理原文明确写"不能把'喜欢参考'推断为长期规则，所以 scope 应该为 UNSTATED"——与共享合同一 §三 反例逐字对应，证明降级路径的口径确实被模型学到并正确应用，不是巧合。同时验证了"account_stage_text 只取本轮新说的内容，不从历史复制"这条 merge 语义在真实模型侧也被正确理解（推理轨迹："本轮没有描述，但上下文里有历史……本轮没说，所以留空。注意不要从上下文复制"）。回复正确拒绝给出选品逻辑的专业判断，未泄漏内部字段。
- 两轮 `answer` 字段经关键词扫描（`FACT`/`PREFERENCE`/`REFERENCE`/`UNSTATED`/`evidence_bundle`/`SYSTEM_TENTATIVE`/`SYSTEM_INFERENCE`/`ev_00`/`DISCUSS`/`FOCUS`/`THIS_ACCOUNT`/`NOT_CAPTURED_IN_P0_SNAPSHOT`）均未命中。

**结论**：`evidence_bundle[]` 的降级路径（LLM 只出扁平信号）在真实 DeepSeek V4 Flash 结构化输出下工作正常，`nature` 三个可选分支里 FACT／REFERENCE 均已在真实运行中触发过（PREFERENCE 尚未自然触发，不构成缺陷，只是这两轮对话没有恰好说出偏好句式）；纯追加、跨轮持久化、`confirmation` 不被伪造升级，均有真实证据而非仅单测证据。`gaps[]` 的 `include_structural` 拆分（8 条常量是否逐轮持久化）不影响对话层可观察行为，此前已由确定性单测覆盖，本次 live 验证未重复验证这一点。`_may_modify_existing_evidence` 相关的 `NOT_VERIFIED_IN_LIVE` 标注因该函数已删除而不再适用。候选 App 当前运行版本为 v0.5。
