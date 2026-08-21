# 笛语三 Skill 自然语言决策系统 V1 Demo 集成合同 v0.1

> **文档角色：V1 Demo 集成层的唯一合同。**
> 本文件规定对话编排层、状态控制层、Skill 调用层与 Demo 级结果追溯的行为边界。
> 本文件**不是第四份业务 Skill**，不修改三份专业 Skill 的任何专业判断，也不新增业务规则。
> 三份 Skill、Golden、夹具、账号责任卡、历史运行与《笛语项目基线》全部只读。

---

## 0. 里程碑与能力边界

```text
milestone            = V1_DEMO_DONE
production_readiness = NOT_IN_SCOPE
```

本轮的 `DONE` 只表示 V1 Demo 达标，**不得**被表述为 `PRODUCTION_BASELINE_DONE`、`PRODUCTION_READY`、`MULTI_TENANT_READY` 或 `TRANSACTION_SAFE`。

固定运行边界：

| 维度 | V1 Demo 边界 |
|---|---|
| 品牌 | 单一序里集夹具品牌 |
| 用户 | 单用户测试 |
| 并发 | 同一 conversation 同一时间最多一个在途 Run；测试请求顺序发送 |
| 消息 | 不支持并发消息 |
| 恢复 | 不支持跨会话长期任务恢复 |
| 租户 | 不支持生产级多租户 |
| 事务 | 不支持数据库事务级原子提交 |
| 投递 | 不声称 exactly-once |
| 就绪 | 不声称生产就绪 |

---

## 1. 分层与不可协商的结构语义

```text
用户输入
→ 影子状态节点（LLM，只提候选补丁）
→ 状态机（Code，唯一能产生有效执行路由的节点）
→ 会话变量写入
→ 固定路由（If/Else）
   ├─ 三条专业执行分支（Workflow Tool，固定映射）
   └─ 一条自然对话分支（统一 LLM 节点）
→ 确定性合同检查 → 轻量 Judge → 产物落定
→ 会话变量写入
→ 用户可见输出
```

以下五条是结构语义，实现方式可调整，语义不可改：

1. **影子 LLM 只能提出状态补丁**，不能产生有效执行授权、Artifact 状态、执行成功结论、企业事实或权限字段。
2. **只有 Code 节点能产生 `effective_route`。** 模型不能自行选择调用哪份 Skill。
3. **三份 Skill 使用固定分支**，映射写死：`EXECUTE_MATRIX → Matrix Workflow Tool`、`EXECUTE_CAMPAIGN → Campaign Workflow Tool`、`EXECUTE_CONTENT_BRIEF → Content Brief Workflow Tool`。
4. **上游接受门必须成立**才能执行下游。
5. **结果保存成功之后才能声称完成。**

第六条同样不可改：**普通对话与专业执行失败语义不同**——对话 Fail Open，执行 Fail Closed（见第 7 节）。

---

## 2. 三份 Skill 的接入方式

三份 Skill 各自保持为**独立 Workflow 应用**，分别发布为**固定 Workflow Tool**，由主 Chatflow 用确定性分支调用。**不使用 Agent 自由选择工具。**

每个 Tool 由一份**薄适配 Workflow** 承载。适配层被严格限定为三件事：

- **输入映射**：把冻结夹具 bundle 与本轮会话上游产物拼装成 Skill 已验证过的输入形态；
- **Final 提取**：剥离推理块，取出正文；
- **输出字段标准化**：统一为下表六个字段。

适配层**不增加任何业务判断**。每份适配 Workflow 的 LLM System 提示词与仓库中对应 Skill 的 `.md` 文件**逐字一致**（SHA-256 相同，见第 9 节）。

### 2.1 Tool 输入

| 参数 | 类型 | 说明 |
|---|---|---|
| `task_context` | paragraph，上限 100000 字符 | 由主 Chatflow 组装：本轮已确认的经营任务 + 已被用户接受的上游产物原文 |

冻结夹具 bundle **不经过 Tool 参数**，而是内嵌在适配 Workflow 的用户提示词中，因此不占用会话变量、不进入对话 Memory、也不可能被用户输入改写。

### 2.2 Tool 输出

| 字段 | 说明 |
|---|---|
| `final_output` | Skill 正文，已剥离推理块 |
| `final_present` | `true` / `false`，是否取到正文 |
| `skill_name` | Skill 标识，如 `Matrix Architect v0.1.2` |
| `skill_sha` | Skill 正文 SHA-256 |
| `model_used` | 实际模型标识 |
| `fixture_bundle_sha` | 本次实际使用的冻结夹具 bundle SHA-256 |

六个字段**都不叫** `text` / `json` / `files`——Dify 的 Workflow-as-Tool 实现会把这三个保留名从工具输出结构中剔除，并且不为它们发出逐变量消息。

---

## 3. 状态对象 `task_snapshot_json`

完整字段定义见 [`V1_TASK_SNAPSHOT_SCHEMA_v0.1.json`](V1_TASK_SNAPSHOT_SCHEMA_v0.1.json)。

`task_snapshot_json` 是一个字符串会话变量，整体持久化。**完整产物不进快照**，只存引用、hash、状态、父 hash 和简短摘要。

### 3.1 `phase`

```text
IDLE  FORMING  AWAITING_CONFIRMATION  READY  RUNNING  COMPLETED  FAILED  CANCELLED
```

### 3.2 `effective_route`

```text
DISCUSS  FOCUS  CONFIRM_TASK  SIDE_TOPIC
EXECUTE_MATRIX  EXECUTE_CAMPAIGN  EXECUTE_CONTENT_BRIEF
HUMAN_DECISION  OUT_OF_SCOPE
```

本轮 route **不写入长期任务状态**。`FACT_LOOKUP` 本轮不实现。

### 3.3 影子节点可以提出的候选补丁

```json
{
  "route_intent": "FOCUS",
  "task_action": "UPDATE",
  "change_goal": "减少多个账号内容重复",
  "change_target_object": "",
  "confirmation_signal": "NONE",
  "requested_skill": "MATRIX",
  "acceptance_signal": "NONE",
  "continue_signal": "NO",
  "user_message_summary": "用户说几个号发的内容重复"
}
```

**这份 schema 是扁平的，而且不含任何 boolean。** 两条都不是风格选择：

- DeepSeek V4 Flash 未声明原生结构化输出，Dify 会退回 prompt-based 模式（`core/llm_generator/output_parser/structured_output.py`）。实测中，嵌套子对象会让模型**只返回那个子对象**，整份补丁因此被拒。
- 该模式注入的提示词模板明写 `Do not output boolean value, use string type instead`（`core/llm_generator/prompts.py`）。schema 里再声明 `boolean` 就是自相矛盾，实测中模型会把整个 token 预算花在纠结这个矛盾上，正文为空。

因此所有取值都是字符串枚举。静态检查把这两条固化为门禁。

`route_intent` 的取值中**没有** `EXECUTE_MATRIX` 一类的有效路由；影子节点最多只能提出 `EXECUTE_REQUEST` + `requested_skill`，是否成为有效执行由状态机判定。

影子节点**不得**输出：有效执行授权、Artifact 状态、Skill 执行成功、企业事实、用户没有表达过的 `confirmed`、tenant 或权限字段。补丁中出现任何未知字段一律整体拒绝。

### 3.4 状态机（Code 节点）职责

1. 解析旧 snapshot；`schema_version` 或 `phase` 非法时从初始状态重建；
2. 校验影子补丁 JSON；
3. 拒绝未知字段与非法枚举（整体拒绝，不做部分采纳）；
4. 限制字段长度（`goal` ≤ 400 字符，`target_object` ≤ 200 字符，摘要 ≤ 300 字符）；
   另有两条**执行前置**约束：与执行请求同一轮新建的任务目标必须 ≥ 12 字符（一句执行命令不是任务目标）；
   任务被取消后，必须重新说清经营问题并单独确认，才能再次执行；
5. 合并允许的状态变化；
6. 保证 `SIDE_TOPIC` 不修改任务；
7. 处理取消、纠正与切换；
8. 更新 `revision`；
9. 管理 `pending_action`；
10. 校验顺序执行条件下的授权；
11. 校验上游 Artifact 接受状态；
12. 产生 `effective_route`；
13. 生成下游 Tool 使用的 Task Packet（`task_goal`）；
14. 输出状态更新结果与拒绝原因（`turn_report`）。

状态机**不重做**任何 Matrix / Campaign / Content Brief 的专业判断、内容创意或品牌经营判断。

---

## 4. Demo 级授权

```json
{
  "skill": "CAMPAIGN",
  "task_revision": 4,
  "confirmation_id": "confirm_004",
  "granted": true,
  "consumed": false
}
```

规则：

- 授权只对**当前 `task_revision` 和指定 Skill** 有效；
- 任务发生**实质变化**（`goal` 或 `target_object` 改变）后，旧确认与旧授权同时失效；
- 用户取消后授权失效；
- 执行开始后逻辑上标记 `consumed = true`；
- **未授权不得执行**；
- 「接受并继续」可以在同一轮同时完成当前 Artifact 接受与下一 Skill 的明确授权；
- **不允许系统自动连续跑完三份 Skill**——每一次执行都必须由用户在该轮明确提出；
- **取消后不能用一句执行命令重启**。`phase = CANCELLED` 时 `draft_task` 一并清空，
  且「同轮说清任务即可执行」这条通道被关闭，必须重新陈述并单独确认。

授权成立的三条路径，任一成立即可，且都必须以本轮用户输入为触发：

| 路径 | 触发 |
|---|---|
| A | `route_intent = EXECUTE_REQUEST` 且 `requested_skill ≠ NONE` 且任务已确认，或用户在**同一轮**里说清了经营目标（≥ 12 字符）并要求执行 |
| B | 用户对 `pending_action.kind = AUTHORIZE_SKILL` 回答 `AFFIRM` |
| C | `acceptance_signal = ACCEPT_CURRENT_ARTIFACT` 且 `continue_signal = true`，授权链条中的下一份 Skill |

本合同**只在「同一 conversation 串行运行」的前提下**验证上述逻辑。不声称并发条件下原子消费、exactly-once、数据库事务级授权或多进程竞争安全。

---

## 5. Artifact 合同

### 5.1 状态

```text
DRAFT  VALIDATED  USER_ACCEPTED  STALE  FAILED
```

`DRAFT` 在 V1 中不落盘：Tool 返回之前不存在 Artifact，Tool 返回之后立即进入 `VALIDATED` 或 `FAILED`。

### 5.2 最小元数据

`artifact_id`、`artifact_type`、`revision`、`status`、`content_hash`、`parent_artifact_id`、`parent_hash`、`skill_name`、`skill_sha`、`run_id`、`accepted_turn_id`，另加 V1 追溯字段 `summary`、`ref`、`status_token`、`model_used`、`fixture_bundle_sha`。

### 5.3 存储

完整产物分别保存在独立会话变量：`matrix_artifact`、`campaign_artifact`、`content_brief_artifact`。

`task_snapshot_json` 只保存 ref、hash、status、parent hash 和简短摘要。

**会话变量是 V1 Demo 的产物存储方式，不是正式 Artifact Store。**

### 5.4 输出校验：确定性合同检查 + 轻量 Judge

**先跑确定性合同检查，不合格直接判负，不浪费 Judge 调用。** 检查 8 项：

1. `final_present` 为 `true` 且正文非空；
2. 正文不含 `<think>` / `</think>`；
3. `skill_sha` 与该 Skill 的冻结 SHA 逐字相符；
4. `fixture_bundle_sha` 与该 Skill 的冻结 bundle SHA 逐字相符；
5. `skill_name` 相符；
6. 顶层状态**按整行声明**判定，落在该 Skill 声明的合法状态集内；
7. 该 Skill 的必需章节齐全；
8. 正文体积 ≤ 200 KB，可写入会话变量。

第 6 项之所以要求「整行声明」而不是子串扫描：Skill 正文里完全可能出现「因此**不**进入 `INPUT_INSUFFICIENT`」这类**说明自己没有停机**的句子，子串扫描会把一份完整产物误判成停机。

确定性检查通过、且输出不是合法停机状态时，才调用**轻量 Judge**。Judge 只回答三件事：合同符合、上游决定漂移、明显事实越界。

**Judge 必须看到该 Skill 实际看到的冻结夹具原文。** 让它判断「事实有没有被编造」却不给它事实，它只能把「我没见过」当成「被编造」——实测中它据此作废了一份合格的 Campaign 产物，而被点名的事实全部逐字存在于夹具里。因此三个 Judge 节点各自内嵌与对应适配 Workflow **完全相同**的 bundle，一致性由静态检查逐字比对（比对 `fixture_bundle_sha`）。

Judge 结论缺失、超出枚举或判为漂移/越界时，一律 **Fail Closed**：产物进入 `FAILED`，不进 `VALIDATED`，不声称完成。

### 5.5 状态迁移规则

- Tool 正常返回**且确定性合同检查通过且轻量 Judge 通过**后进入 `VALIDATED`；
- 用户明确接受后进入 `USER_ACCEPTED`；
- Campaign 只能消费 `USER_ACCEPTED` 的 Matrix；
- Content Brief 只能消费 `USER_ACCEPTED` 的 Campaign；
- Matrix 重新产出后，Campaign 与 Content Brief 标记为 `STALE`；
- Campaign 重新产出后，Content Brief 标记为 `STALE`；
- `STALE` 产物**不得**继续作为下游依据，也不能被直接「接受」，必须重跑；
- 结果保存失败时不得进入有效完成状态。

---

## 6. 夹具接入

序里集夹具作为**单品牌、只读、版本化、SHA 冻结的 Demo 可信输入**，以固定 `fixture_bundle` 提供给三份 Workflow Tool。

| Skill | bundle 组成（按拼接顺序） |
|---|---|
| Matrix | `一页纸夹具品牌事实 v0.1.md` |
| Campaign | `一页纸夹具品牌事实 v0.1.md`、`序里集_Campaign当前素材与资源夹具_v0.1.md`、`序里集_Campaign最小承接条件夹具_v0.1.md`、`C1`—`C6_FOUNDER_CONFIRMED_v0.1.md` |
| Content Brief | `一页纸夹具品牌事实 v0.1.md`、`序里集_Campaign当前素材与资源夹具_v0.1.md`、`序里集_Campaign最小承接条件夹具_v0.1.md` |

每份文件的 SHA、拼接顺序与 bundle 总 SHA 记录在 [`V1_DIFY_RUN_MANIFEST_v0.1.md`](V1_DIFY_RUN_MANIFEST_v0.1.md)。每次运行实际使用的 bundle SHA 由 Tool 回传，并被确定性合同检查逐字比对。

**为什么 Campaign 与 Content Brief 的 bundle 里没有 `序里集_四张账号责任卡_CONFIRMED_v0.1.md`**：在 V1 链路中，这一位置由**本轮会话中已被用户接受的 Matrix 产物**占据。这样 Matrix→Campaign 的衔接才是真实的机器对机器传递，而不是两份并存的真源。适配层只做了这一处引用替换，`版本优先级` 段落的其余文字与已验证运行逐字相同。

本轮不建立生产知识库。正式多租户知识库、服务端身份、权限审计与租户隔离进入生产差距清单，不阻塞 `V1_DEMO_DONE`。

---

## 7. 失败语义

### 7.1 普通对话：Fail Open

```text
影子结构化输出失败 或 补丁校验不通过
→ 保留旧 snapshot（一字不改）
→ effective_route 降为 DISCUSS
→ 用户仍获得正常回复
→ 明确告知本轮没有任何确认、授权或执行生效
```

**若本轮是确认、取消、纠正或执行授权，而状态未保存成功，必须告诉用户本次状态没有成功保存，不得假装确认已经生效。**

### 7.2 专业执行：Fail Closed

以下任一发生，**一律不得声称完成**：

```text
Tool 调用失败  或  Tool 输出缺失  或  确定性合同检查失败
或  轻量 Judge 失败或缺席  或  Artifact 保存失败
```

### 7.3 错误分支清单与预期语义

| # | 错误分支 | 实现 | 预期语义 |
|---|---|---|---|
| 1 | 影子结构化输出失败 | 影子节点 `error_strategy = default-value`，`structured_output` 缺省为 `{}` | 补丁校验判负 → Fail Open |
| 2 | snapshot 解析失败 | 状态机内 `normalise_snapshot` | 从初始状态重建，且本轮拒绝执行任何 Skill |
| 3 | Workflow Tool 调用失败 | Tool 节点 `error_strategy = fail-branch` → 共用失败节点 | `phase = FAILED`，写 `last_error`，不写任何 Artifact |
| 4 | Workflow Tool 无 Final | `final_present = false` → 确定性检查 `NO_FINAL` | Artifact `FAILED`，不保存产物 |
| 5 | Tool 输出合同不合格 | 确定性检查 8 项 | Artifact `FAILED`，逐条列出未通过项 |
| 6 | Judge 失败或结论缺失 | 落定节点 `judge_present = false` | Fail Closed，Artifact `FAILED` |
| 7 | Artifact 保存失败 | 赋值节点无 `error_strategy`，整轮中止 | 用户收到 Dify 错误，**不会**收到任何完成声明 |
| 8 | Answer 输出清洗失败 | 用户可见出口只引用确定性节点输出，不引用模型原始 `text` | 执行分支的用户可见文本 100% 由代码生成 |

本轮**不要求**对所有基础设施故障逐项做真实故障注入。真实测试聚焦三条：状态失败时不误执行 Skill；Tool 或校验失败时不声称完成；Artifact 未保存时不声称完成。

---

## 8. 自然对话行为

所有非专业执行路由**共用同一个自然对话 LLM 节点**。该节点的本轮行为由状态机生成的确定性指令驱动。

| route | 行为 |
|---|---|
| `DISCUSS` | 正常回答，不急于形成任务 |
| `FOCUS` | 回答并**最多追问一个**真正阻塞的问题；没有真正阻塞的问题就不追问 |
| `CONFIRM_TASK` | 只确认当前待确认事项 |
| `SIDE_TOPIC` | 正常回答，**不反复提醒**未完成任务 |
| `HUMAN_DECISION` | 说明冲突、选项和影响 |
| `OUT_OF_SCOPE` | 说明边界，**不修改任务** |

- 用户表达已经明确（例如「就按这个矩阵继续做 Campaign」）时，**不得再次要求形式主义确认**。
- 用户只说「是」「继续」「就这个」时，**必须绑定当前 `pending_action`**，不能泛化为对任意旧任务的授权。

---

## 9. 推理内容隔离与输出清洗

影子节点、自然对话节点、三份 Skill 的 LLM 节点与 Judge **全部**设置 `reasoning_format: separated`。三份适配 Workflow 在此之外还保留一道 Jinja2 推理块剥离模板作为第二道防线。

所有用户可见出口必须满足：

- `<think>` 计数为 0；
- `</think>` 计数为 0；
- `reasoning_content` 不进入 Answer；
- `task_snapshot` 不进入 Answer；
- Tool 内部参数不进入 Answer；
- System Prompt 不进入 Answer。

长 Memory 回归纪律：

- 普通自然对话只使用**小窗口 Memory（window size = 6）**；
- **完整 Artifact 不进入普通 Memory**——产物只存在于会话变量与 Tool 参数模板中，对话节点与影子节点都读不到；
- 执行 Skill 时才通过 Tool 参数模板加载所需完整上游 Artifact。

---

## 10. 冻结声明

| 资产 | SHA-256 |
|---|---|
| `Matrix_Architect_v0.1.2.md` | `7a6afa3cf1a7b2e4793bd2b3dde6edddf20f75a5b8ed9f7aeb6a456d06acd838` |
| `Campaign_Orchestrator_v0.1.md` | `c7ef284e40e7c4cd0d4081632fca7df17bd1a80fbd3f3b5267be4aea1040a0fb` |
| `Content_Brief_Architect_v0.1.md` | `a0268a211a235b5b4df5e517f085db1f3b4948ae5add3346f2c15a426b63395f` |
| `一页纸夹具品牌事实 v0.1.md` | `8c21d41d471deed8e169055a37288e1f29b769fe5f7a7296dff4274b8bb6d53a` |
| `序里集_Campaign当前素材与资源夹具_v0.1.md` | `53ea76e93c6529d211bcc41161e9771f7cc5818fe99caf54c4af5f7539ae0074` |
| `序里集_Campaign最小承接条件夹具_v0.1.md` | `17b41d3ae37635fcd1e97f6af1136c71afa6310a9c51e1db12948b0b2e1e2b06` |
| `序里集_四张账号责任卡_CONFIRMED_v0.1.md` | `8e21454f53a34b7dce13b7eab547727bb1ce8bce9bac5f86df6d7dc3078f503f` |
| `序里集_CONTENT_BRIEF_GOLDEN_v0.1.md` | `3b6cbcd7c79d49815ec1de8db472950ab84ac04a754b3342355285d706fe04bd` |

以上资产在本轮**零修改**。Golden 只用于运行后评测，绝对不得进入 Skill、System Prompt、User Prompt、正向输入、负向输入、DSL 模板或任何模型可访问变量。

本合同随 V1 Demo 一同冻结。任何后续改动必须新开版本号，不得就地覆盖。
