# M1 候选环境 · 真实运行记录 001

`task_id: DIYU-V1-M1-NATURAL-CONTEXT-001`

## 一、环境

- Dify：本机自托管 1.16.1（`/home/faye/dify/docker/`），与 A-0～A-4 证据同一实例
- App：`DIYU V1 M1 Natural Context Candidate v0.1`，id `dd638b91-d39f-4e92-a984-6ad1ab809119`，advanced-chat
- 工作流版本：v0.3（`marked_comment`: "fix: no more raw enum leak into user-facing text"），发布时间 `2026-08-25`；历史版本 v0.1/v0.2 未删除，可随时回退
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
