# M1 候选环境 · 真实运行记录 001

`task_id: DIYU-V1-M1-NATURAL-CONTEXT-001`

## 一、环境

- Dify：本机自托管 1.16.1（`/home/faye/dify/docker/`），与 A-0～A-4 证据同一实例
- App：`DIYU V1 M1 Natural Context Candidate v0.1`，id `dd638b91-d39f-4e92-a984-6ad1ab809119`，advanced-chat
- 工作流版本：v0.2（`marked_comment`: "fix: chat layer no longer gives professional content-strategy opinions"），发布时间 `2026-08-25`
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
- 未覆盖 A-0～A-4 的受控等价输入回归（确认+授权句式、接受并继续、撤销接受等）——这是下一步工作，不在本轮范围内已完成。
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
