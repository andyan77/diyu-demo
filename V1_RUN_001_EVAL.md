# 笛语 V1 Demo 集成与验收评估 RUN_001

```text
milestone            = V1_DEMO_DONE
production_readiness = NOT_IN_SCOPE
```

> 本文件的每一条判定都来自确定性核对：Dify 后台的 `workflow_runs`、`workflow_node_executions`、`workflow_conversation_variables`，以及仓库文件的 SHA-256。
> **没有任何一条结论由模型给出。** 轻量 Judge 只参与单份产物的合同判定，不参与本文件的验收结论。

---

## A. Demo Hard Gate 1—20

| # | 门 | 结果 | 证据 |
|---|---|---|---|
| 1 | 三份正式 Skill 和历史资产零修改 | **通过** | 执行前 tracked 文件 70 份，逐份 SHA-256 比对，变更 0 份  |
| 2 | 三份 Workflow Tool 在目标 Dify 中可调用 | **通过** | 三个 tool_provider 均已注册；本轮真实被调用的 Skill：['campaign', 'content_brief', 'matrix'] |
| 3 | 主 Chatflow 在真实 Dify 中导入并运行 | **通过** | 10 个 conversation 共 40 轮，全部 HTTP 200 |
| 4 | task_snapshot_json 能跨轮保存和读回 | **通过** | 10/10 个多轮会话的快照在后续轮次被成功读回并推进（phase 序列见逐场景表） |
| 5 | 10 个多轮场景全部通过 | **通过** | 通过 10/10；未通过：无 |
| 6 | Golden 三 Skill 链真实跑通 | **通过** | S08 最终 Artifact 状态：{"matrix": "USER_ACCEPTED", "campaign": "USER_ACCEPTED", "content_brief": "VALIDATED"}；Skill 调用顺序：['matrix', 'campaign', 'content_brief'] |
| 7 | 未授权 Skill 调用为 0 | **通过** | 6 个「不应执行」场景（S01、S02、S04、S05、S06、S10）的 Skill 调用次数分别为 [0, 0, 0, 0, 0, 0] |
| 8 | Matrix 未接受时 Campaign 调用为 0 | **通过** | S07 Skill 调用 ['matrix']；Matrix 终态 VALIDATED；阻塞原因 UPSTREAM_NOT_ACCEPTED:matrix:VALIDATED |
| 9 | Campaign 未接受时 Content Brief 调用为 0 | **通过** | S10 末轮要求直接做 Content Brief；Skill 调用 []；阻塞原因 UPSTREAM_MISSING:campaign |
| 10 | 上游修改后下游正确进入 STALE | **通过** | S09 重跑 Matrix 后最终 Artifact 状态：{"matrix": "VALIDATED", "campaign": "STALE", "content_brief": "STALE"} |
| 11 | 状态失败后没有误执行 Skill | **通过** | 补丁校验失败一律降级 DISCUSS 且不进入执行分支；确定性单元测试 9 个非法补丁形态全部拦下，真实运行中所有非执行场景 Skill 调用为 0 |
| 12 | Tool、校验或 Artifact 保存失败时没有伪装完成 | **通过** | 见 EVAL 第 E 节逐条失败记录：所有失败路径的用户可见文本均由确定性代码生成，统一写明「本轮任务未完成」；FAILED 的 Artifact 一律不进入 VALIDATED |
| 13 | SIDE_TOPIC 没有修改任务核心字段 | **通过** | S04 逐轮 route：['FOCUS', 'FOCUS', 'DISCUSS', 'SIDE_TOPIC', 'CONFIRM_TASK'] |
| 14 | <think> 与内部状态进入用户输出为 0 | **通过** | 对 10 个场景全部用户可见输出扫描 9 类标记，命中：无 |
| 15 | 完整产物未进入普通对话 Memory | **通过** | 对话节点与影子节点的 Memory 窗口 size=6，且二者的提示词均不引用任何 *_artifact 会话变量；完整产物只经由 Tool 参数模板进入 Skill 调用 |
| 16 | 运行输入、输出、Run ID、Trace、状态和参数完整归档 | **通过** | 已归档：['V1_RUN_001_RAW.md', 'V1_RUN_001_FINAL.md', 'V1_RUN_001_TRACE.md', 'V1_DIFY_RUN_MANIFEST_v0.1.md'] |
| 17 | 40 类测试目录已冻结 | **通过** | 目录中 case_id 行数 = 40 |
| 18 | Git 变更范围符合白名单 | **通过** | 新增 15 份（越界 无）；已跟踪文件修改 0 份 |
| 19 | 工作区干净 | 待提交后核验 | 提交后核验 |
| 20 | 本地与 origin/main 一致 | 待提交后核验 | 推送后核验 |

---

## B. 十个多轮场景逐项结果

| 场景 | 标题 | 风险 | 轮数 | 逐轮 route | Skill 调用 | 最终 Artifact | 结果 |
|---|---|---|---|---|---|---|---|
| S01 | 泛讨论，不形成任务，不调用 Skill | low | 3 | DISCUSS → DISCUSS → DISCUSS | 0  | {} | **通过** |
| S02 | 模糊自然语言逐步聚焦为 Matrix 任务（形成任务但不执行） | medium | 4 | FOCUS → FOCUS → FOCUS → CONFIRM_TASK | 0  | {} | **通过** |
| S03 | 用户一次给出完整明确任务并要求执行，系统不再要求多余确认 | medium | 2 | EXECUTE_MATRIX → DISCUSS | 1 matrix | {"matrix": "VALIDATED"} | **通过** |
| S04 | 中途跑题，SIDE_TOPIC 后返回原任务 | medium | 5 | FOCUS → FOCUS → DISCUSS → SIDE_TOPIC → CONFIRM_TASK | 0  | {} | **通过** |
| S05 | 用户纠正目标，旧确认与旧授权失效 | high | 4 | FOCUS → CONFIRM_TASK → FOCUS → DISCUSS | 0  | {} | **通过** |
| S06 | 用户取消任务，之后不再调用 Skill | high | 4 | FOCUS → FOCUS → CONFIRM_TASK → HUMAN_DECISION | 0  | {} | **通过** |
| S07 | Matrix 仅 VALIDATED 未被接受时，Campaign 不得运行 | high | 3 | FOCUS → EXECUTE_MATRIX → HUMAN_DECISION | 1 matrix | {"matrix": "VALIDATED"} | **通过** |
| S08 | Golden 全链：接受并继续，依次完成 Matrix → Campaign → Content Brief | high | 4 | FOCUS → EXECUTE_MATRIX → EXECUTE_CAMPAIGN → EXECUTE_CONTENT_BRIEF | 3 matrix、campaign、content_brief | {"matrix": "USER_ACCEPTED", "campaign": "USER_ACCEPTED", "content_brief": "VALIDATED"} | **通过** |
| S09 | 上游 Matrix 重出后，Campaign 与 Content Brief 进入 STALE | high | 6 | FOCUS → EXECUTE_MATRIX → EXECUTE_CAMPAIGN → EXECUTE_CONTENT_BRIEF → EXECUTE_MATRIX → HUMAN_DECISION | 4 matrix、campaign、content_brief、matrix | {"matrix": "VALIDATED", "campaign": "STALE", "content_brief": "STALE"} | **通过** |
| S10 | 异常语义：对话 Fail Open、执行 Fail Closed、无推理泄漏 | high | 5 | HUMAN_DECISION → HUMAN_DECISION → OUT_OF_SCOPE → FOCUS → HUMAN_DECISION | 0  | {} | **通过** |

逐场景详细事实：

| 场景 | conversation_id | phase 序列 | blocking_gap | 状态机 notes |
|---|---|---|---|---|
| S01 | `3c413b39-5b2f-4bdc` | IDLE → IDLE → IDLE | — | — |
| S02 | `9dc28339-b07f-4c81` | IDLE → IDLE → AWAITING_CONFIRMATION → READY | — | TASK_CONFIRMED |
| S03 | `1b017375-b8aa-433d` | RUNNING → COMPLETED | — | EXECUTION_AUTHORIZED:MATRIX、SKILL_AUTHORIZED_BY_EXPLICIT_REQUEST:MATRIX、TASK_CONFIRMED_BY_EXPLICIT_EXECUTION_REQUEST |
| S04 | `382c6684-5d44-40af` | IDLE → AWAITING_CONFIRMATION → AWAITING_CONFIRMATION → AWAITING_CONFIRMATION → READY | — | SIDE_TOPIC_NO_TASK_WRITE、TASK_CONFIRMED |
| S05 | `7dbfd631-6bc2-4127` | AWAITING_CONFIRMATION → READY → AWAITING_CONFIRMATION → None | — | PRIOR_CONFIRMATION_AND_AUTH_INVALIDATED、TASK_CONFIRMED |
| S06 | `9e9d4275-465e-4de8` | IDLE → AWAITING_CONFIRMATION → CANCELLED → CANCELLED | NO_VALID_AUTHORIZATION | EXECUTION_REFUSED_NO_AUTH、TASK_CANCELLED |
| S07 | `371c1158-9707-473c` | IDLE → RUNNING → READY | UPSTREAM_NOT_ACCEPTED:matrix:VALIDATED | ACCEPT_REFUSED_NO_VALIDATED_ARTIFACT、EXECUTION_AUTHORIZED:MATRIX、EXECUTION_BLOCKED:UPSTREAM_NOT_ACCEPTED:matrix:VALIDATED、SKILL_AUTHORIZED_BY_EXPLICIT_REQUEST:CAMPAIGN、SKILL_AUTHORIZED_BY_EXPLICIT_REQUEST:MATRIX、TASK_CONFIRMED_BY_EXPLICIT_EXECUTION_REQUEST |
| S08 | `a13098a0-3f9f-4d94` | IDLE → RUNNING → RUNNING → RUNNING | — | ARTIFACT_ACCEPTED:campaign、ARTIFACT_ACCEPTED:matrix、EXECUTION_AUTHORIZED:CAMPAIGN、EXECUTION_AUTHORIZED:CONTENT_BRIEF、EXECUTION_AUTHORIZED:MATRIX、SKILL_AUTHORIZED_BY_EXPLICIT_REQUEST:CAMPAIGN、SKILL_AUTHORIZED_BY_EXPLICIT_REQUEST:CONTENT_BRIEF、SKILL_AUTHORIZED_BY_EXPLICIT_REQUEST:MATRIX |
| S09 | `adf10a68-299c-4cb8` | AWAITING_CONFIRMATION → RUNNING → RUNNING → RUNNING → RUNNING → READY | UPSTREAM_STALE:campaign | ARTIFACT_ACCEPTED:campaign、ARTIFACT_ACCEPTED:matrix、EXECUTION_AUTHORIZED:CAMPAIGN、EXECUTION_AUTHORIZED:CONTENT_BRIEF、EXECUTION_AUTHORIZED:MATRIX、EXECUTION_BLOCKED:UPSTREAM_STALE:campaign、SKILL_AUTHORIZED_BY_EXPLICIT_REQUEST:CAMPAIGN、SKILL_AUTHORIZED_BY_EXPLICIT_REQUEST:CONTENT_BRIEF |
| S10 | `4d009a36-d4e5-42a3` | IDLE → IDLE → IDLE → FORMING → READY | UPSTREAM_MISSING:campaign | EXECUTION_BLOCKED:UPSTREAM_MISSING:campaign、EXECUTION_REFUSED_NO_AUTH、SKILL_AUTHORIZED_BY_EXPLICIT_REQUEST:CONTENT_BRIEF、TASK_CONFIRMED |

---

## C. 跨轮状态、授权与 Artifact

| 场景 | 快照字符数 | 产物会话变量字符数 | 授权消费 | 上游接受门 |
|---|---|---|---|---|
| S01 | 457 | {} | — | 未触发 |
| S02 | 523 | {} | — | 未触发 |
| S03 | 1517 | {"matrix_artifact": 7926} | EXECUTION_AUTHORIZED:MATRIX、SKILL_AUTHORIZED_BY_EXPLICIT_REQUEST:MATRIX、TASK_CONFIRMED_BY_EXPLICIT_EXECUTION_REQUEST | 未触发 |
| S04 | 533 | {} | — | 未触发 |
| S05 | 620 | {} | — | 未触发 |
| S06 | 484 | {} | EXECUTION_REFUSED_NO_AUTH | NO_VALID_AUTHORIZATION |
| S07 | 1519 | {"matrix_artifact": 6998} | EXECUTION_AUTHORIZED:MATRIX、EXECUTION_BLOCKED:UPSTREAM_NOT_ACCEPTED:matrix:VALIDATED、SKILL_AUTHORIZED_BY_EXPLICIT_REQUEST:CAMPAIGN、SKILL_AUTHORIZED_BY_EXPLICIT_REQUEST:MATRIX、TASK_CONFIRMED_BY_EXPLICIT_EXECUTION_REQUEST | UPSTREAM_NOT_ACCEPTED:matrix:VALIDATED |
| S08 | 3492 | {"campaign_artifact": 8526, "matrix_artifact": 6484, "content_brief_artifact": 11358} | EXECUTION_AUTHORIZED:CAMPAIGN、EXECUTION_AUTHORIZED:CONTENT_BRIEF、EXECUTION_AUTHORIZED:MATRIX、SKILL_AUTHORIZED_BY_EXPLICIT_REQUEST:CAMPAIGN、SKILL_AUTHORIZED_BY_EXPLICIT_REQUEST:CONTENT_BRIEF、SKILL_AUTHORIZED_BY_EXPLICIT_REQUEST:MATRIX、TASK_CONFIRMED_BY_EXPLICIT_EXECUTION_REQUEST | 未触发 |
| S09 | 3430 | {"matrix_artifact": 6785, "campaign_artifact": 9640, "content_brief_artifact": 10909} | EXECUTION_AUTHORIZED:CAMPAIGN、EXECUTION_AUTHORIZED:CONTENT_BRIEF、EXECUTION_AUTHORIZED:MATRIX、EXECUTION_BLOCKED:UPSTREAM_STALE:campaign、SKILL_AUTHORIZED_BY_EXPLICIT_REQUEST:CAMPAIGN、SKILL_AUTHORIZED_BY_EXPLICIT_REQUEST:CONTENT_BRIEF、SKILL_AUTHORIZED_BY_EXPLICIT_REQUEST:MATRIX | UPSTREAM_STALE:campaign |
| S10 | 533 | {} | EXECUTION_BLOCKED:UPSTREAM_MISSING:campaign、EXECUTION_REFUSED_NO_AUTH、SKILL_AUTHORIZED_BY_EXPLICIT_REQUEST:CONTENT_BRIEF | UPSTREAM_MISSING:campaign |

`task_snapshot_json` 全程保持在 457—3492 字符之间，**完整产物一次都没有进入快照**；产物只存在于三个独立会话变量里。

---

## D. 确定性单元测试覆盖

`v1_demo_verify.py` 从**已发布的 DSL 里取出 Code 节点原文**，按 Dify 沙箱的调用形态执行。测的是仓库里真正会被导入 Dify 的那份代码，不是脚本自带的副本。

| 分组 | 覆盖内容 |
|---|---|
| A 状态机基础 | 空快照、模糊需求成型、确认落地 |
| B 授权与执行门 | 已确认任务执行、无上游拦截、仅 VALIDATED 拦截、接受并继续、只接受不继续 |
| C 纠正/取消/跑题 | 旧确认与旧授权作废、过期授权不自发、取消清空、跑题零改动、跑题后返回 |
| D 补丁失败 | 9 种非法补丁形态（空对象、非法枚举、未知字段、直接写授权、非 JSON、None、列表、未知子字段、坏快照）全部降级 DISCUSS 且不执行 |
| E 合同检查 | 无 Final、含 think、状态非法、Skill SHA 不符、夹具 SHA 不符、合法停机、超出保存上限、上游继承、零重合漂移、状态字误判正反两向 |
| F 产物落定 | VALIDATED 落盘、产物不进快照、逐字一致、STALE 双级传播、Judge 漂移判负、Judge 缺席 Fail Closed、字符串枚举与布尔兼容、Tool 失败不写产物 |
| G/H/I 回归 | build2 / build6 / build7 三轮实测缺陷的定点回归 |

运行方式：`python3 v1_demo_verify.py`。本轮结果：冻结资产 0 项不符、静态检查 0 项失败、单元测试 0 项失败。

---

## E. Workflow Tool 接缝兼容性探针（任务书第九节）

社区历史 Issue `#31449`、`#19989` 只作为回归风险登记，**未预设当前版本存在同样问题**；以下七项全部实测。

| 探针项 | 实测结果 |
|---|---|
| 短文本输出 | Content Brief 停机状态输出 855 字符 / 2285 字节，六个字段齐全 |
| 正常完整输出 | Matrix 输出 7073 字符 / 19511 字节 |
| 大体量真实输出 | Content Brief 输出 12024 字符 / 32637 字节 |
| 状态型输出 | `INPUT_INSUFFICIENT` 正确回传，未被截断 |
| Tool 输出字段是否完整 | 三次探针 `final_output` / `final_present` / `skill_name` / `skill_sha` / `model_used` / `fixture_bundle_sha` 均 6/6 存在 |
| Tool 失败是否进入正确错误分支 | 两类真实失败均命中 `fail-branch`：参数超限（`task_context in input form must be less than 100000 characters`）与上游模型不可用（`api.deepseek.com` DNS 解析失败） |
| 调用方能否逐字取得 Final | `text` 与 `json` 两条通道均与 `final_output` **逐字相等**（`text_carries_final_verbatim` / `json_carries_final_verbatim` 均为 true） |

结论：**Workflow-as-Tool 接缝在 Dify 1.16.1 上可用**，无需绕过接缝伪装集成。
机制依据：`core/tools/workflow_as_tool/tool.py` 对每个非保留名输出发出一条 variable message，`graphon/nodes/tool/tool_node.py` 把它们直接并入节点输出；`text` 是 `json.dumps(outputs)`。因此本轮三份适配 Workflow 的输出字段刻意避开了 `text` / `json` / `files` 三个保留名。

---

## F. 构建变更与失败记录

本轮主 Chatflow 共发布 8 个版本。**每一次改动都是被真实运行打出来的**，不是先想到再改。所有历史版本、失败运行与失败证据全部保留，未删除、未覆盖、未选择性保留成功样本。

| 版本 | 改了什么 | 被什么实测缺陷触发 | 根因 |
|---|---|---|---|
| build1 | 首版主 Chatflow 导入并发布 | —（基线） | — |
| build2 | 明确执行请求当场确认任务；取消时清空 draft_task | S03 实测：用户已说「就按这个做，不用再跟我确认了」，系统仍要求形式主义确认 | 违反任务书第十七节「用户表达已经明确时不得再次要求形式主义确认」 |
| build3 | 影子结构化输出 schema 拍平为 `change_goal` / `change_target_object`；裸 `EXECUTE_REQUEST` 路由到 `CONFIRM_TASK` | S08 实测：影子只返回了嵌套子对象 `{"goal":…,"target_object":…}`，补丁被整体拒绝；未点名 Skill 的执行请求掉进 `DISCUSS` | 嵌套对象在 prompt-based 结构化输出下不可靠 |
| build4 | 顶层状态判定改为「整行状态声明」，不再做子串扫描 | 实测：Matrix 正文里的「因此不进入 `INPUT_INSUFFICIENT`」被误判为停机声明，一份完整的四张责任卡被当作停机丢弃 | 确定性合同检查自身的假阳性 |
| build5 | 结构化输出去掉 boolean、改字符串枚举；`max_tokens` 影子 2048→16000、对话 3000→12000、Judge 1200→32000；新增两条静态门禁 | 实测 `JUDGE_VERDICT_MISSING`：Dify 的 prompt-based 模板明令 「Do not output boolean value, use string type instead」，与 boolean schema 直接冲突；Judge 的 1200 token 预算被推理块吃光，正文为空 | `core/llm_generator/prompts.py :: STRUCTURED_OUTPUT_PROMPT` |
| build6 | 把三份产物的当前状态喂进自然对话节点的上下文 | 实测：对话节点把一份已经 `VALIDATED` 的矩阵说成「没有通过系统校验」 | 反向失真——把成功说成失败，同样是误导用户 |
| build7 | 取消后必须重新说清经营问题并单独确认；同轮新建目标须 ≥12 字；影子提示词禁止把提问判为执行请求、禁止把命令当目标 | S06 实测 Hard Gate 缺口：用户取消后，一句「那你还是把矩阵跑一下吧」被当成新任务目标，Skill 真的跑了 | 违反任务书第二十二节场景 6 与第二十四节第 7 项 |
| build8 | `change_goal` 非空即视为任务陈述，不再依赖 `task_action`；影子提示词补上输出纪律 | S03 / S07 实测：影子填了 `change_goal` 却把 `task_action` 标成 `NONE`，任务建不起来，后续所有执行请求被拒 | `task_action` 与目标是否存在本就冗余，以目标为准 |
| build9 | 把冻结夹具原文交给三个轻量 Judge；Judge 失败原因改用同一套字符串枚举读取器 | S08 实测：Campaign 产物被 Judge 判为「事实越界」而作废，但被点名的「六件必买」「否决」与素材编号 A01/B01/C01/D01 **全部逐字存在于 Campaign 冻结夹具与 C2/C3/C4 中**；同时失败原因被错标成 `JUDGE_CONTRACT_NOT_MET` | Judge 被要求判断「事实有没有被编造」，却没有拿到事实——看不到输入就无法判断越界；失败原因用 `is True` 去比字符串枚举，永远为假 |

### F.1 运行期模型侧偶发（未做任何配置修改）

| 现象 | 证据 | 系统的处置 |
|---|---|---|
| Campaign Skill 一次运行只产出推理块、正文 0 字 | `finish_reason=stop`，completion_tokens 20189 全部落在 reasoning，text 长度 0；同一配置的另外 4 次运行正文为 7855—9928 字 | 确定性合同检查判 `NO_FINAL` → Artifact `FAILED` → 明确告知「本轮任务未完成」→ 下游被上游接受门拦下。**没有伪装完成** |
| DeepSeek `api.deepseek.com` DNS 解析失败 | 探针与 Judge 节点各命中一次 | 探针进入 Tool 失败分支；Judge 节点由 `retry=1` 重试后成功，首次失败保留在 `error` 字段 |

两类偶发都**没有**被当作理由去修改配置、放宽验收或重跑掩盖。

---

## G. 推理内容与内部状态泄漏扫描

扫描对象：10 个场景**全部用户可见输出**（不是抽样）。扫描项 9 类。

| 扫描项 | 命中次数 |
|---|---|
| `<think>` | 0 |
| `</think>` | 0 |
| `task_snapshot` | 0 |
| `schema_version` | 0 |
| `effective_route` | 0 |
| `影子状态节点` | 0 |
| `系统提示词开头` | 0 |
| `fixture_bundle_sha` | 0 |
| `skill_sha` | 0 |

隔离手段：影子、对话、三份 Skill 与三个 Judge 全部设置 `reasoning_format: separated`；三份适配 Workflow 另有一道 Jinja2 推理块剥离模板作为第二道防线；执行分支的用户可见文本 100% 由确定性代码生成，不引用任何模型原始 `text`。

长 Memory 回归（社区 Issue `#36717`）：普通对话与影子节点的 Memory 窗口均为 6；两者的提示词都不引用任何 `*_artifact` 会话变量，**完整产物不进入普通 Memory**；只有执行 Skill 时才通过 Tool 参数模板加载完整上游产物。

---

## H. 本轮不能证明的事项

以下每一条都**没有**被本轮证据覆盖，不得据此推断系统具备该能力：

1. **并发安全**。所有测试请求顺序发送，同一 conversation 同一时间只有一个在途 Run。并发条件下的原子消费、exactly-once、CAS 与事务级授权**全部未验证**，见生产差距 G-01—G-04。
2. **跨会话恢复与隔离**。40 类目录中的 `CT-05`、`CT-06` 要求在新 conversation 中验证「上一段会话的授权与产物不得渗漏」，本轮**未执行**。
3. **完整 40 类回归**。本轮只真实执行 10 个多轮场景，覆盖 40 类中的 15 类；其余 25 类只设计冻结。其中 7 类的等价逻辑由确定性单元测试覆盖，但**单元测试不等于多轮 conversation 真实执行**。
4. **Artifact 保存失败的真实注入**。会话变量写入失败会让整轮中止（用户收到 Dify 错误、不会收到任何完成声明），这是设计语义，本轮**没有真实注入过这种故障**。
5. **Skill 产物的专业质量**。本轮验收的是集成层：调用顺序、状态、授权、接受门、失败语义与证据可追溯。三份 Skill 输出的**业务质量没有被重新评审**，轻量 Judge 只判合同符合、上游漂移与明显事实越界，不打分、不比较。
6. **Matrix Skill 在 DeepSeek 上的质量等价性**。Matrix v0.1.2 的专业质量是在 `qwen-max` 上于 RUN_003 验收的；本轮按任务书第二十七节统一使用 DeepSeek V4 Flash。四张责任卡的角色与 RUN_003 一致（林序 / 周宁 / 苏禾 / 陈晚），但**这不构成质量等价性证明**。
7. **生产就绪**。见 [`V1_PRODUCTION_GAP_REGISTER_v0.1.md`](V1_PRODUCTION_GAP_REGISTER_v0.1.md) 全部 11 项。

---

## I. 是否允许进入完整 40 类自然语言 E2E

**判定：允许**

进入完整 40 类之前建议先补上的两件事（不阻塞本轮 `DONE`，但会显著影响 40 类的效率）：

1. **把 10 个场景固化为可重放的自动化回归**。本轮 8 次构建里有 7 次是靠人工读 trace 才发现缺陷的；没有自动回归，40 类跑一遍的成本会高到无法重复。
2. **影子节点的稳定性**。本轮实测到影子在极少数轮次会把推理文本混进结构化输出（补丁被整体拒绝、系统 Fail Open，安全性未受影响，但那一轮用户体验为空转）。40 类中有 27 类是安全关键类，需要先把这个尾部概率量化。
