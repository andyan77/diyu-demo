# M1 候选环境 · 真实运行记录 001

`task_id: DIYU-V1-M1-NATURAL-CONTEXT-001`

## 一、环境

- Dify：本机自托管 1.16.1（`/home/faye/dify/docker/`），与 A-0～A-4 证据同一实例
- App：`DIYU V1 M1 Natural Context Candidate v0.1`，id `dd638b91-d39f-4e92-a984-6ad1ab809119`，advanced-chat
- 工作流版本：v0.5（快照扩展 evidence_bundle[]／gaps[]，Founder 本人 2026-08-25 在控制台完成导入与发布）；v0.6（§8 正式审查阻断修复批次）已生成待导入，见 §十三；历史版本 v0.1～v0.4 未删除，可随时回退
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

## 十二、Execution Prompt §8 正式独立审查（第一次，隔离上下文、只读、无先前记忆）

首次对本任务运行设计文档规定的正式独立审查流程（区别于之前各批次执行侧自己发起的对抗式合规检查——那些都是实现方自己安排的自验手段，不满足 §8 "未参与实现"这条硬性要求）。审查员：全新 Agent 会话，无本任务任何先前上下文，只读权限，被要求"逐条独立核验，找不到证据就判未证实，发现相反证据就判与事实不符，不许只信文档自述"。

**审查方法（不是自述，逐条列出）**：实际重跑 `python3 decision-chain/workflows/test_m1_context_compiler_v0.1.py -v`；独立重算 Execution Prompt v1.2 §14 的 Task Contract Hash 并与文档比对；直连本机 Dify Postgres（只读查询）逐条核对 11 个证据引用的 `conversation_id`/`message_id` 是否真实存在、`query` 文本是否与证据文件引述一致；从数据库提取已发布工作流图，与从 HEAD 重新生成的 DSL 逐节点比对字节级是否一致；`git diff --name-status` 核对受保护资产是否被触碰。

**结论（M1-AC-00～15 逐条独立判定，非自述）**：3 项相对扎实（`AC-12` 真实无退化——受保护基线与主 Chatflow 均未被触碰；`AC-13` 候选真实运行且与 commit/发布图字节级绑定），其余全部为 `PARTIAL`，其中 **8 项构成阻断**（§8.2 唯一允许的两类理由之一：明确违反某条 `M1-AC`；未发现任何受保护资产/安全边界类阻断）：

| 编号 | 违反的 AC | 一句话证据 |
|---|---|---|
| B-1 | AC-03 | `secondary_goals[]`／`priority_order[]`／`business_goal_categories` 从无物理承载能被写入，永远空数组 |
| B-2 | AC-04 | Prompt §4.3 要求的 `permission`／`freshness` 两个维度全仓零出现 |
| B-3 | AC-01 | "合法资料""有效历史产物"两类输入渠道在候选环境里完全不存在（无文件上传、无工具节点） |
| B-4 | AC-06 | `needed_capabilities` 结构上只能容纳一个值，且由影子提示词里的关键词映射表单一决定 |
| B-5 | AC-07 | `route_intent=CANCEL`／短指代无任何机制或反馈，`open_threads` 终态 `HANDLED` 全仓从未被赋值过 |
| B-6 | AC-10 | 影子节点真实失败（Dify `error_strategy: default-value` 降级为 `{}`）时被当作合法空 patch 处理，对话断言"确实不是落库失败"——真实失败场景下这是假话 |
| B-7 | AC-15 | 从未做过一次回滚/恢复演练，无回滚包 |
| B-8 | AC-14 | `git reflog` 显示 10 次真实远程推送，账本 `L5` 一条 Git 副作用记录都没有；真实运行清单不完整 |

**一处审查报告本身需要更正的表述（执行侧独立复核，已用数据库时间戳证实）**：审查报告把 `b39c9e21`（17:19:48）描述为"与 RUN-002 相同缺陷的第二次未记录实例"，读起来像修复后又复发的活跃缺陷。直连数据库核对时间线：候选 App 工作流发布记录显示 v0.1 于 17:16:00 发布、v0.2（RUN-002 缺陷的修复版本）于 17:27:36 发布；`b39c9e21` 发生在 17:19:48，比 v0.2 发布早了近 8 分钟，且查询文本与 `7e7d74cc`（即证据文件记录的 RUN-002）逐字相同——这是同一句测试话在 v0.2 发布前被重复发送了两次，只有一条被写入证据文件，**不是修复失效后的复发**。真实性质是运行清单完整性问题（B-8 的一部分：16 条真实消息，证据文件只记录了约 12 条，另外几条包括两次连通性探测和一次模型身份探测，均为良性、非缺陷），不是活跃缺陷。

**执行侧对三个此前自行提出的问题的处理，经审查确认**：
- `evidence_nature=UNSTATED` 局部跳过而非整批拒绝——行为正确，符合"资料不足时不得整任务拒绝"；措辞已改为"未决、需核对"是恰当姿态。
- `market_observations`／`runtime_evidence` 的 DEFER——诚实、被单测锁定，是治理判断非工程判断，正确未由执行侧单方宣布。
- `evidence_scope` 被模型主动推断为 `THIS_ACCOUNT`——合法但比口径鼓励的保守默认更主动，收紧提示词与否不是任何 AC 硬性要求，留作可选项。

## 十三、B-1／B-2／B-5／B-6 修复 + 修复后二次对抗式审查发现的新问题 + 执行侧自行收口

按 §8.1 步骤 4"执行负责人只修阻断项，自验直接/传递影响"，本轮只修 B-1/B-2/B-5/B-6（均为 HOW 层面、已授权范围内的工程缺口）。**B-3（材料/历史产物输入通道）与 B-4（多能力路由）本批明确不做**：两者都需要真正的架构判断（B-3 涉及在候选 Dify App 上开放新的外部输入面，B-4 涉及重新设计 `call_intent` 的多值语义与稳定性风险），仓促补一个半吊子实现的风险高于暂缓——与此前 v0.2/v0.3 批次对"按字段确认状态机"的同一类范围裁定一致，留作独立批次处理。

**四项修复**（`decision-chain/workflows/m1_context_compiler_v0.1.py` 等三个源文件，单测 83→116）：
- B-1：新增扁平 patch 字段 `secondary_goal_text`／`priority_order_text`／`business_goal_category`（PATCH_KEYS 20→23），`business_goal_categories` 新增顶层快照键。
- B-2：`EVIDENCE_DIMENSION_VOCAB` 新增 `permission`（恒 `OWNED_BY_USER`）／`freshness`（恒 `FRESH`）两个常量维度，`P0_STRUCTURAL_GAPS` 同步登记单值限制，不新增 LLM patch key。
- B-5：`route_intent=CANCEL` 增加诚实反馈（本轮没有其他状态变化时，明确告知"没有把撤回绑定到任何具体动作"），不新建撤销状态机。
- B-6（最关键，真实 bug，已用真实调用独立复现）：新增 `SHADOW_NODE_FAILED` 检测——patch 缺少任一必需 key（含影子节点失败后 Dify 降级产出的 `{}`）时判定为节点失败，区别于"patch 合法但内容平淡"，避免继续对话时断言"确实不是落库失败"这类在真实失败场景下的假话。判据依据的不变量：DSL 的 `structured_output.schema.required` 覆盖全部 `PATCH_KEYS`，真正的合法输出无论内容多平淡都会带满全部 key，只有失败降级路径才产出缺 key 的字典。

**修复后独立对抗式审查（同一批次内的第二轮，非 §8 正式审查）发现 6 个新问题，均已核实为真实、非误报**：

1. `priority_order` 追加语义会累积互相矛盾的排序（"涨粉优先于转化"和"转化优先于涨粉"同时留在数组里）——**已修复**：改为替换语义，只保留用户最近一次的完整表述，新增单测锁定矛盾场景。
2. 存量（v0.4 及更早）持久化会话里的 `evidence_bundle[]` 条目缺 `permission`／`freshness` 两个新键，此前的顶层键升级循环不会补条目内部字段，下游按新设计文档"每条必须携带全部维度"读取会 KeyError——**已修复**：`main()` 新增条目级 `setdefault`，只补缺失键、不覆盖已有值，新增单测覆盖升级场景与"已有值不被覆盖"两种情况。
3. `route_intent=CANCEL` 与同轮真实状态变化并存时（例如"算了，改成做家居内容"），断言"没有任何内容被撤销或删除"是假话——**已修复**：`_dialogue_directive` 新增 `changed` 形参，只在本轮确实没有其他状态变化时才发出这句断言；同时把"请说清楚具体想撤回哪一项"这句系统本身接不住答案的追问改为如实说明限制、正常继续对话，新增单测锁定"CANCEL+真实变更"场景不再产生假断言。
4. `secondary_goals`／`priority_order`／`business_goal_categories` 的去重都是逐字匹配，改述会被当成新增，长会话下可能无界增长——**未处理**：与 `non_sacrifice_constraints` 早已存在的同类风险同一性质，模糊去重需要语义相似度判断，本身有误判风险，不在本批新增语义匹配逻辑，登记为已知限制。
5. `business_goal_categories` 没有"改主意/撤销某个类别"的通道，且这条限制没有像 permission/freshness 那样登记进 `gaps[]`——**未处理**，口径不一致已如实记录，留待下一批一并处理经营目标类别与次目标/优先级的"撤销"语义（如果需要的话，本身也是 B-5 那类需要设计判断的范畴）。
6. `PATCH_UNKNOWN_FIELDS`／`ILLEGAL_ENUM:*`／`PATCH_NOT_OBJECT` 三类内部码仍然原样拼进 `dialogue_directive`（`V1_M1_CANDIDATE_RUN_001.md:78` 记录的 CE-A2 那类缺陷的另一处未修分支）——**确认为本批之前就存在、非本批引入的回归**（经 `git show HEAD:` 逐行比对确认改动前后该分支代码相同），但 B-1 新增的 8 值枚举 `business_goal_category` 客观上给这条老泄漏路径新增了一个自然触发口。是否借这次机会一并收口，留待下一批或 Reviewer 裁决，不在本批擅自扩大范围顺手处理。

**需要 Reviewer/Founder 裁决的一处真实取舍（B-6 判据的可靠性前提）**：SHADOW_NODE_FAILED 判据完全建立在"Dify + DeepSeek V4 Flash 会严格执行 `schema.required`"这一前提上——这是**声明的**（DSL 配置如此要求），不是**实测的**：仓库现有证据只记录过该模型不支持嵌套对象，5 次真实运行至今未自然撞见过一次影子非法输出，从未验证过"缺 1-2 个字段、其余都对"这种部分失败模式是否会真实出现。如果这个前提不成立，本次修复是把"沉默的假话"换成了"沉默的内容丢失"（一份 22/23 键都对的高质量 patch 会被整轮丢弃）。这需要真实 live 回归提供实测证据，不能停留在单测层面自证；本批暂不擅自放宽判据（比如"只有全空才算失败，缺 1-2 个字段宽松合并"），先如实登记这一前提待验证，见下方"尚待 live 验证"。

**B-7（回滚演练）静态验证（未做真实演练，如实标注限制）**：执行侧当前无控制台写权限（`console/api/apps` 返回 401，与此前 SE-015 记录的会话失效一致），无法安全地在候选 App 上执行真实的"发布回退再重新发布"演练；按设计文档 §9.2 允许的替代路径，改为**静态恢复验证**：直连数据库确认 `apps.workflow_id` 是指向 `workflows` 表某一行的单一外键，该 App 的 5 个历史发布版本（v0.1～v0.4 对应的行）全部完整存在、未被删除；Dify 的"发布"动作在数据库层面就是新建一行 `workflows` 并把 `apps.workflow_id` 指过去——这是单列更新，不删除任何历史行，结构上天然可逆。**限制**：这条链路的验证止于"结构上确认可逆"，未真实执行过一次"指回旧版本→确认候选 App 真的按旧版本运行→再指回新版本"的完整演练，也没有做过"仓库候选变更"这一侧的恢复点验证（该侧本身就是 git，`git log`/`git revert` 天然可用，风险远低于 Dify 侧）。

**本批未 commit 前状态**：四项修复 + 六项修复后问题里的三项已处理完毕，`python3 decision-chain/workflows/test_m1_context_compiler_v0.1.py -v` → `Ran 120 tests ... OK`。DSL 已重新生成为 `m1_candidate_dsl_v0.6.yml`，**尚未导入/发布，尚未 live 验证**——尤其是 B-6 判据依赖的前提，必须有真实运行证据才能真正认定"已解决"。

## 十四、v0.6 live 验证（Founder 2026-08-25 导入并发布后，真实调用，B-6 前提实测）

**候选对象核验**：直连数据库确认 `dd638b91-d39f-4e92-a984-6ad1ab809119` 当前 `workflow_id` 指向 `2cdd034f-b4ae-4dde-a43e-ede5a09ff804`（发布时间 2026-08-26 03:36:38 UTC），图字节长度 118772；提取该图逐字节核对，`m1_shadow` 节点 `structured_output.schema.required` 确为 23 项且与本次修复新增的 `secondary_goal_text`／`priority_order_text`／`business_goal_category` 一致，"二十三个字段"字样在系统提示词中出现——确认发布对象即本批 v0.6，非误发旧版本。

**B-6 判据前提实测（此前状态：仅是 DSL 声明要求，从未实测；本次目标：用真实调用检验"缺 1-2 个字段、其余都对"这种部分失败模式是否会自然出现）**：通过既有 App API Key 对候选 App 发起 6 次真实调用，覆盖新任务（含主目标+次目标+优先级+硬约束+经营类别五个新/相关字段同时非空的复合场景）、含糊表达、单轮内自我纠正的冲突陈述、跨轮真实矛盾优先级（两轮）、取消。直连数据库读取每次调用 `m1_shadow` 节点的原始 `outputs`（不经过下游 `dialogue_directive` 转述，避免自证）：

| 场景 | message_id | status | 23 键齐全 |
|---|---|---|---|
| 复合新任务（提升到店/顺带涨粉/涨粉次于到店/价格不能打太低/STORE_VISIT） | `adb194c3` | succeeded | 是，23/23 |
| 含糊表达（"先这样吧，随便弄弄"） | `40955a0c` | succeeded | 是，23/23 |
| 单轮自纠正冲突（"涨粉最重要，不对，其实转化更重要"） | `eb385da8` | succeeded | 是，23/23 |
| 取消（"算了，刚才说的不用改了"） | `73a15660` | succeeded | 是，23/23 |
| 跨轮矛盾优先级·第一轮（"涨粉优先于转化"） | `b0d3c431` | succeeded | 是，23/23 |
| 跨轮矛盾优先级·第二轮（"不对，转化优先于涨粉，按转化来"，同会话） | `7a207029` | succeeded | 是，23/23 |

6/6 真实调用全部 23 键齐全、零缺失，未观察到"部分失败"模式。**这不是形式概率证明**（样本量小，不能排除低概率部分失败场景存在），但结合结构性事实——Dify 的 `structured_output` 是通过约束模型输出格式（而非事后校验再重试）实现的，模型在 API 层面就不能生成不满足 `required` 的 JSON，节点要么产出满足 schema 的完整对象，要么在无法满足时整体判定节点失败——6/6 的经验结果与这一结构性机制预期一致，支持"部分失败"在当前实现下不是一个真实存在的中间状态，B-6 判据成立的前提**从"仅声明"升级为"有真实调用支持，非形式化证明"。**

**跨轮矛盾优先级测试同时验证了本批 B-6 修复批次内的 follow-up 修复（优先级替换语义）在真实模型 + 真实 Dify 执行环境下同样生效**：直连 `m1_compiler` 代码节点输出，第一轮压缩后 `goal_structure.priority_order = ["涨粉优先于转化"]`，第二轮（同一 `conversation_id f1f270bd-d6a8-4267-b5d8-5f877d23b7d6`）压缩后 `goal_structure.priority_order = ["转化优先于涨粉"]`——旧值被替换而非累积，与单测断言一致，且是单测从未覆盖过的真实模型输出路径（单测用手工构造的 patch，不经过真实 LLM 的自然语言到枚举/文本字段的转写）。

**未在本轮验证范围内、如实标注**：6 次调用均未真实触发 Dify 侧的 `error_strategy: default-value` 降级（即真实 SHADOW_NODE_FAILED 路径本身未被真实复现，B-6 的原始 bug 复现记录仍以此前的独立审查阶段的复现为准）；`permission`／`freshness` 恒定值在真实运行下的落库未单独复核（属确定性常量赋值，风险低，此前单测已覆盖）；`business_goal_category` 枚举其余取值（`LONG_TERM_VALUE`/`ACCOUNT_GROWTH`/`FOLLOWER_GROWTH`/`TRAFFIC`/`LEADS`）未在本轮自然触发，不构成缺陷。

**结论**：v0.6 候选与本批四项修复+三项 follow-up 修复的源码状态一致，B-6 判据前提首次获得真实调用支持，可视为本批修复的收口证据完整。下一步：Execution Prompt v1.3 `review_contract.closing_verification: affected_scope_only` 收口确认。
