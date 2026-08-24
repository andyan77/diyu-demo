# V1 对话编排修复 001 —— 运行证据

> 对应任务：`DIYU-V1-DIALOGUE-ORCHESTRATION-REPAIR-001`。
> 本文件是本次修复唯一的集中运行证据，覆盖版本一致性、根因、修复内容、离线单测与 A-0～A-4 真实 Dify 对话结果。

---

## 1. 版本一致性说明

| 维度 | 值 |
|---|---|
| 仓库 | `/home/faye/diyu-demo` |
| 分支 / HEAD | `feature/v1-full-chain-runtime` @ `0bdfa5d` |
| 施工基线 DSL | [`decision-chain/workflows/DIYU_DEMO_V1_FULL_CHAIN_CHATFLOW_v0.2.yml`](../workflows/DIYU_DEMO_V1_FULL_CHAIN_CHATFLOW_v0.2.yml) |
| Dify 版本 | `1.16.1`（自托管 Docker Compose，`docker-api-1` / `docker-web-1` 等） |
| 主 Chatflow app_id | `310ddfcf-e0fb-4211-af98-3d101725e07a`（DIYU Demo V1 Main Chatflow v0.1） |

**修复前**：Dify 已发布 workflow `7f0eb8f7-6e60-46d3-a553-a1ee545450f0` 的 `graph` 字段，与仓库当时的 DSL 文件（会话开始时已存在于工作区、尚未提交）逐字节完全一致（对解析后的 JSON 结构做 SHA-256 比对，结果相同）。`conversation_variables` 按变量名比对也逐字段一致。即施工前仓库与 Dify 运行版本一致，无漂移。

**修复后**：本次改动只写入并发布了一次新版本 `055b7bbe-172f-4456-8459-951ae3e14ce7`（`apps.workflow_id` 现指向它），其 `graph` 与修复后的仓库 DSL 文件逐字节完全一致。与修复前的 Dify 图做节点级 SHA-256 比对，56 个节点中只有 3 个不同：`v1_state`、`v1_shadow`、`v1_chat_llm`；`edges` 与节点 id 集合完全未变。历史发布版本（含 `7f0eb8f7` 及更早的全部版本）未被删除或覆盖，`apps.workflow_id` 可随时指回旧版本。

草稿版本（`8a11d4ad-ed1b-45a3-a00c-4f72ecebefad`）已同步更新为同一份 `graph`，与新发布版本内容一致。

发布方式：本次未走 Dify 控制台网页操作，而是用与 Dify 自身 `WorkflowService.publish_workflow()` 完全等价的 SQL 事务完成（更新草稿 `graph` → 复制草稿为新的已发布 `workflows` 行 → 把 `apps.workflow_id` 指向新行），执行前先用 `ROLLBACK` 空跑一次验证语句无误，执行前已征得 Founder 明确批准。

---

## 2. 根因（`runtime_verified`，取自会话开始前约 3 小时的真实 Dify 对话）

会话 `71ab01d6-0571-4008-80b9-d5b5bd662b00`（2026-08-24，本次修复施工前）完整复现了任务书描述的两个问题。

### 2.1 根因一：确认+授权句式永远拿不到「经营目标」，授权永远无法成立

状态机原逻辑：只有当 `draft_task.goal` 非空时，才允许「同一轮执行请求」把任务标记为已确认。但 `change_goal` 的判定口径明确要求「只有用户说出经营问题才填，执行命令不算」——而这正是任务书 A-0 给出的确认句式的真实性质：它是一句命令/授权声明，不是经营问题陈述。三次真实尝试全部因此卡死：

| Run ID | 用户原话 | Shadow 输出 | v1_state 结果 |
|---|---|---|---|
| `816e1918` | “我确认启动账号策划任务，并授权系统调用专业模块开始生成。” | `change_goal=""`, `requested_skill=MATRIX`, `route_intent=EXECUTE_REQUEST` | `effective_route=HUMAN_DECISION`，`notes=[EXECUTION_REFUSED_NO_AUTH]`，回复要求用户改用系统指定句式 |
| `851431b9` | “确认，就按这个做。现在跑账号矩阵。” | 同上 | 同上 |
| `d55e8bf5` | “我确认账号策划任务的内容和范围，并授权系统调用专业模块开始生成账号矩阵。” | 同上 | 同上 |

### 2.2 根因二：一个回复分支无条件宣称「已经记下」，不管有没有真记下

`run 2ea714b9`（用户原话：“我确认当前账号策划任务的内容无误，请开始。”）这一轮 Shadow 输出 `requested_skill=NONE`，落入 `v1_state` 里 `elif ri == "EXECUTE_REQUEST":` 这条兜底分支。该分支**无条件**生成指令文本「先用一句话回执当前任务已经记下」，而此时 `confirmed_task` 与 `draft_task.goal` 其实都是 `null`。下游对话 LLM 据此回复：

> “你说的这句确认我已经记下了，但后台的记录里，任务仍然停在'未确认'状态……可能是确认信息落库的时候没成功，建议你稍等一会儿……”

这正是任务书描述的「一边声称已经记下确认，一边继续读取未确认状态」——且模型进一步自行编造了「落库没成功」这个从未发生过的技术原因。

---

## 3. 修复内容（3/56 节点）

只改了 `v1_state`（Code）、`v1_shadow`（LLM + 结构化输出 schema）、`v1_chat_llm`（LLM 系统提示词）三个节点，其余 53 个节点字节级未变（含 Stage1/Stage2 内容生产链、三份核心 Skill 的 Tool/precheck/Judge/finalize/save/answer 全部节点）。

为保证 diff 最小，采用「先证明 `yaml.dump(d, allow_unicode=True)` 与 Dify 自身 `export_dsl()` 的调用逐字节等价」的方式：改动前对仓库文件原文做一次 `yaml.safe_load` → `yaml.dump` 往返测试，确认输出与原文件 **逐字节相同**，之后再对解析出的 dict 做定点字段替换、重新 dump，因此未触碰的节点在文本层面也不会产生无谓 diff。

### 3.1 「无独立经营目标陈述」也能成立确认（根因一的修复）

`v1_state` 新增一条路径：当 `route_intent=EXECUTE_REQUEST`、`requested_skill` 已点名、尚无 `confirmed_task`，且 `draft_task.goal` 始终为空时——若用户本轮原话（不是 `change_goal`，是完整 `sys.query`）长度 ≥ 12 字符（复用既有的 `MIN_SAME_TURN_GOAL` 反空令阈值），直接把用户原话记为任务并同轮确认+授权。「把矩阵跑一下」（6 字符）这类裸命令仍按原逻辑拦截，不受影响。

### 3.2 假「已经记下」claim 修复（根因二的修复）

`elif ri == "EXECUTE_REQUEST":` 兜底分支现在先判断 `confirmed_task` 或 `draft_task.goal` 是否真的存在：存在才说「已经记下」；不存在则改为如实告知「当前系统这边确实还没有记录任何任务内容（不是用户表达得不够清楚，也不是落库失败，就是还没有形成任务）」，并明确禁止编造技术故障原因。

### 3.3 一轮多诉求：`side_question` + `open_threads`

`v1_shadow` 结构化输出新增字段 `side_question`（第 10 个字段，纯字符串，无布尔、无嵌套对象，保持既有的 DeepSeek V4 Flash 结构化输出约束）。`v1_state` 把非空 `side_question` 记入新快照字段 `open_threads`（`[{id, text, raised_at_revision, status}]`），与本轮其余处理（接受、确认、执行……）并行、不互斥。若本轮能触达自然对话节点（非 `EXECUTE_*` 路由），当场在回复里一并回应；若本轮恰好是执行路由（无自然语言出口），该条目保持 `OPEN`，顺延到下一个自然对话轮次自动浮现一次（浮现后标记 `SURFACED`，不再反复提醒）。

### 3.4 撤销最近一次接受

`acceptance_signal` 新增第三个取值 `REVOKE_LAST_ACCEPTANCE`。新快照字段 `last_acceptance` 只记录单一「最近一次接受」（`{slot, revision}`）。撤销时把该产物从 `USER_ACCEPTED` 退回 `VALIDATED`（合同 5.1 定义的「待接受」态），并复用三份核心 Skill 既有的 `DOWNSTREAM` 级联 STALE 语义（新增 `DOWNSTREAM_OF_SLOT` 映射覆盖全部 5 个槽位）标记已经建立在其上的下游产物；随后清空 `last_acceptance`，因此撤销范围天然只到最近一次，不会连环回溯到更早、无关的接受。没有可撤销对象时如实拒绝，不假装生效。

### 3.5 `v1_chat_llm`：不编造失败原因

新增一条系统提示约束：指令没有解释某事失败的原因时，不得自行编造原因（如「可能是网络问题」）。直接针对根因二里模型自行编出「落库没成功」的行为。

---

## 4. 离线单元测试：41/41 通过

测试脚本直接从已改动的仓库 DSL 里取出 `v1_state` 的 `code` 字符串编译执行，测的是即将上线的原文，不是脚本自带副本。六组：

- **A（4 项）**：三条真实失败句式原样重放，全部改判 `EXECUTE_MATRIX`。
- **B（4 项）**：`把矩阵跑一下`（6 字符裸命令）仍被拦截；取消后即便说出很长的确认+授权句式仍需重新单独确认，不被绕过。
- **C（3 项）**：无记录时不再说「已经记下」；有真实任务记录时该说法原样保留（防止过度修正）。
- **D（10 项）**：接受+捎带问题同轮两件事都被记录；同轮若走执行路由则问题延后到下一自然对话轮浮现且只浮现一次。
- **E（11 项）**：撤销正常路径、级联 STALE、无可撤销时如实拒绝、撤销范围只到最近一次（用两个不同槽位验证更早的接受不受影响）。
- **F（9 项）**：纯讨论不建任务、「接受并继续」原有行为不退化、`SIDE_TOPIC` 不动任务状态、补丁损坏时 fail open 不冒领执行。

---

## 5. A-0 至 A-4：真实 Dify 对话结果

全部运行在修复后已发布的 `055b7bbe` 版本上，经 `/v1/chat-messages` 真实调用产生，Run ID / Message ID / Conversation ID 均可在 Dify 数据库中复核。

### A-0｜明确确认并授权 —— **PASS**

- Conversation `d0014fa1-1bc8-4b60-8cb5-f22d7ecd1840`，Message `4d42a47c-d3e7-4d4f-9a97-79c6417ee75e`，Run `8cf65925-8803-4d65-9cbd-20c7e85ff7a3`
- 用户原话：“我确认启动账号策划任务，并授权系统调用专业模块开始生成。”（与任务书 A-0 用例逐字一致）
- `v1_state.turn_report.notes = ["TASK_CONFIRMED_FROM_OWN_WORDS_NO_SEPARATE_GOAL", "SKILL_AUTHORIZED_BY_EXPLICIT_REQUEST:MATRIX", "EXECUTION_AUTHORIZED:MATRIX"]`，`effective_route=EXECUTE_MATRIX`
- 完整节点链路真实执行：`v1_shadow → v1_state → v1_route → tool_matrix（真实调用账号矩阵 Skill Tool）→ pre_matrix（precheck_ok=true）→ gate_matrix → judge_matrix（judge_ok=true，真实 Judge 理由："产物基于夹具真实角色与初秋通勤任务构建四账号矩阵，没有上游可漂移，也未出现夹具外的商品、价格、库存或顾客事实"）→ fin_matrix（status=VALIDATED）→ artsave_matrix → snapsave_matrix → answer_matrix`
- 真实产出账号矩阵（林序/周宁/苏禾/陈晚四账号，7440 字符），回复明确写出「已通过确定性合同检查与轻量 Judge（状态 VALIDATED），但还没有被你接受」，未再次索要确认或改用其他句式。

### A-1｜原有接受继续不退化 —— **PASS**

- 同一 Conversation，Message `c9c92565-6f03-457e-84c0-843addb1e134`
- 用户原话：“接受并继续”
- 结果：`effective_route=EXECUTE_CAMPAIGN`；Matrix 产物转 `USER_ACCEPTED`（`last_acceptance={"slot":"matrix"}`）；真实调用 Campaign Orchestrator Skill Tool，产出 `VALIDATED` 的 Campaign 决策包（内容提及「苏禾 1 条主要短视频 + 周宁 1 条主要短视频」，为 A-2 提供真实上下文）。

### A-2｜一轮两件事 —— **PASS**（第二次尝试；第一次真实撞见模型分类抖动，被 fail-open 正确拦下）

**第一次尝试**（Message `5628a58c-f5a2-4b50-ac02-8e1db36cc051`，Run `19bed136-8490-4af7-af5c-5e42378831df`）：Shadow 这一轮输出的 `structured_output` 是 `{"slot":"matrix","revision":1}`——完全不符合自己的 schema（自然发生的 DeepSeek V4 Flash 分类抖动，与本次代码改动无关）。`v1_state` 正确判定 `patch_ok=false`（`PATCH_UNKNOWN_FIELDS:revision,slot`），fail open：旧状态原样保留，Campaign 依旧是 `VALIDATED`（没有被误判为已接受），回复也没有声称任何确认/授权已生效。因为「接受」这一半本轮并未真正生效，此次不计为 A-2 通过，但计为 A-4 的真实证据（见下）。

**重试**（Message `b098c669-b29d-4978-86c0-11a301465041`，Run `669da12a-15f7-4abf-8d2b-677c6f97e345`）：同一句话：“接受，但我想先看看不做周宁主讲会怎样”。
- `acceptance_signal=ACCEPT_CURRENT_ARTIFACT` 正确识别 → Campaign 转 `USER_ACCEPTED`（`last_acceptance={"slot":"campaign","revision":2}`）
- 「不做周宁主讲」这部分，Shadow 本轮走的是既有的 `route_intent=CORRECT` + `change_target_object="不做周宁主讲"` 通道，而不是本次新增的 `side_question` 字段——**这是模型分类的真实波动**（`side_question` 的提示词说明里逐字覆盖了「如果不做 X 会怎样」这种句式，但模型这一轮没有套用），不是代码缺陷。
- 结果：两件事都成立且都被回应——回复原文：「Campaign 决策包已确认接受。下一步：您可以授权系统继续生成 Content Brief。关于'不做周宁主讲'的调整，当前尚未生成任何替代方案；如确有需要，需要您重新明确授权后再单独处理，目前不展开。」
- **诚实说明**：`side_question`/`open_threads` 这条新机制本身，在这次真实对话里没有被这一轮选中，因此不算被真实 Dify 对话直接验证；但该机制已由第 4 节离线单测 D 组 10/10 独立验证，包括「同轮执行路由时问题被延后到下一自然对话轮浮现」这一真实对话难以按需复现的场景。

### A-3｜撤销最近一次接受 —— **PASS**

- 同一 Conversation，Message `a6b0c30e-04f8-46be-a9c3-33ce36af7c2c`，Run `a3bfd987-6d73-4071-b4fb-45e8e280bbdc`
- 用户原话：“我刚才不是让你接受”
- Shadow 正确输出 `acceptance_signal=REVOKE_LAST_ACCEPTANCE`（对新增枚举值的真实分类）
- `v1_state.notes=["ACCEPTANCE_REVOKED:campaign"]`；Campaign 退回 `VALIDATED`；**Matrix（更早、不相关的接受）原样保持 `USER_ACCEPTED` 不受影响**——用两个真实存在、互不相同的槽位验证了「只撤销最近一次」；`last_acceptance` 清空。
- 回复原文：「撤销已生效。账号矩阵……不，Campaign 决策包的接受已撤销，回到'已生成、等你接受'的状态……当前这版还是已生成但未确认接受，没有进入下一步。」

### A-4｜失败不能伪装成用户表达问题 —— **PASS**（两个安全、非破坏性的真实子场景）

**(a) Shadow 分类失败 → fail open，不冒领成功**：主证据即上文 A-2 第一次尝试（Run `19bed136`，修复后的代码上真实自然发生）——`patch_ok=false` → `DISCUSS` 路由 → 旧状态原样保留 → 未声称任何确认/授权/执行生效。辅证：修复前同一会话里的 `run 941b4d8f`（deepseek 插件真实 `PluginInvokeError` 导致 `structured_output` 为空 → `PATCH_NOT_OBJECT` → fail open，指令文本「保持旧任务状态不变，正常回答用户，不要声称任何确认、授权或执行已经生效」），证明这条 fail-open 路径本次改动未触碰、且在改动前后行为一致。

**(b) 撤销无对象时如实拒绝**：全新 Conversation `c1cf3f83-b2f1-497f-86bc-d8c55968522b`，Message `ea3aba42-7798-4d37-a9ee-77c4db733f7a`，Run `b40ab49c-4d62-4773-b71b-c066fe2411e3`。作为会话第一句话直接说：“我刚才不是让你接受”（当前确无任何接受记录）。`v1_state.notes=["REVOKE_REFUSED_NOTHING_TO_REVOKE"]`，节点链路里没有任何 `tool_*` 节点被触发。回复原文：「根据当前记录，没有可撤销的'最近一次接受'——也就是说，系统这边没有查到你已经接受的记录。所以这次撤销没有实际生效，原本就没有需要撤销的操作。」——没有声称成功，没有要求用户换句话，没有编造原因。

---

## 6. 最小回归

| 检查项 | 证据 | 结果 |
|---|---|---|
| 普通咨询不误触发专业模块 | 全新 Conversation `0a2bc758-e5f5-4222-87d9-5a8740b283db`，Message `0335f8cb-2e82-43ed-b7ba-f9e2b45050c8`，Run `b9665c15-0840-4d69-886d-64dfbf9f7942`；用户原话「我们最近想调整一下会员折扣，你怎么看？」；`effective_route=DISCUSS`，`skill_slot=none`，节点链路里没有出现任何 `tool_*` 节点 | PASS |
| 没有明确授权时不越权执行 | 同上；另见 A-4(b)：意图明确但无有效授权时同样没有触达任何 `tool_*` 节点 | PASS |
| 既有专业模块 / 内容生产路由 / 用户交付字段未丢失 | 第 1 节的节点级 SHA-256 比对：56 个节点中除 `v1_state`/`v1_shadow`/`v1_chat_llm` 外，其余 53 个（含 `tool_stage1`/`tool_stage2`/`fin_stage1`/`fin_stage2` 等内容生产链全部节点、三份核心 Skill 各自的 Tool/precheck/Judge/finalize/save/answer 全部节点）逐字节未变 | PASS |
| 原有会话不因本次改动被重置 | 修复前既有 Conversation `aab9fa9d-1235-453b-a81a-11dbff4978ce`（创建于 2026-08-22，早于本次修复）在发布新版本后续接：Message `faa246ce-e071-48f1-b27a-5da87344eb8c`，Run `e4b1bd8d-788f-4dd1-b0d4-ad61b876e41f`。`revision` 原样延续为 `2`（未回零），`phase` 原样延续为其真实历史状态 `FAILED`，五个产物槽位状态原样保留（四个 `USER_ACCEPTED`、发布包 `FAILED`），新增的 `open_threads`/`last_acceptance` 字段被安全地默认填充为 `[]`/`None`，未报错、未重置 | PASS |

---

## 7. I-03 状态（与本次修复结果分开登记）

对仓库全量文件（含未追踪文件）与全部 49 个提交（覆盖 `main`、`feature/v1-full-chain-runtime`、`feature/v1-demo-e2e-quality-validation`、`feature/content-production-chain-v1`、`feature/content-production-runtime-v1`、`chore/v1-baseline-closeout-content-production-handoff` 及全部 `origin/*`）做穷尽检索（`grep`、`git grep --all`、`git log -p -S` pickaxe），**未找到任何名为「I-03」的验收项或编号体系**，也没有 I-01 / I-02。

实际存在、仍处于未完成状态的登记项：

- `G-01` 至 `G-12`——[`V1_PRODUCTION_GAP_REGISTER_v0.1.md`](../docs/V1_PRODUCTION_GAP_REGISTER_v0.1.md) 第 11—113 行，12 项全部标记「否／未关闭」。
- [`V1_DECISION_CHAIN_STAGE_BASELINE_v0.1.md`](../docs/V1_DECISION_CHAIN_STAGE_BASELINE_v0.1.md) 第 34—42 行「未完成」一节，散文形式，无编号。

按仓库真相源优先级，「I-03」在当前仓库里查无此项，如实登记，不强行对应到上述任一编号，也不代替判断其含义。

---

## 8. 结论

`A-0`、`A-1`、`A-2`、`A-3`、`A-4` 与最小回归全部在真实 Dify 对话中成立（A-2 的接受+双诉求本身通过真实对话验证成立，其中 `side_question` 新字段这一具体实现路径改由第 4 节离线单测独立验证——见第 5 节该条目的诚实说明）。

**状态：`DONE`**
