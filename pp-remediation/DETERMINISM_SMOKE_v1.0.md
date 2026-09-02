---
task_id: DIYU-V1-PP-BLOCKER-REMEDIATION-S1-S4-001
blocker: B-01
model_calls_budget: 3
model_calls_used: 3
status: CLOSED_AT_CONFIG_LAYER_ONLY
byte_determinism: NOT_ACHIEVABLE_ON_THIS_STACK
downgraded_criterion: OUTCOME_STABILITY
authorized_by: PP_阻断修复_S1-S4_EXECUTION_PROMPT_v1.0_ERRATA_001.md (sha256 cd07b33843b09752dd63626f97a41ed3f1717dec70b0e074c0a9db00a5f4c72b)
---

# S1 确定性冒烟 · 结果记录

## 配置层（已完成，勘误 001 前即已就绪，未变）

`skill_llm` / `recovery_llm` 共用的 `completion_params`（YAML 锚点 `&id001`）：

| 参数 | v1.3 值 | v1.4 值 | provider 是否支持 |
|---|---|---|---|
| `temperature` | 未设置（落到平台默认 `1`） | `0` | 支持（`parameter_rules` 声明 `min:0.0 max:2.0 default:1`） |
| `top_p` | `0.8` | `1` | 支持（`parameter_rules` 声明 `min:0.01 max:1.00 default:1`） |
| `frequency_penalty` | 未设置 | **未加入**（不支持） | **不支持**——`langgenius/deepseek:0.0.20` 的 `deepseek-v4-flash.yaml` `parameter_rules` 未声明此参数 |
| `presence_penalty` | 未设置 | **未加入**（不支持） | **不支持**，同上 |
| `seed` | 未设置 | **未加入**（不支持） | **不支持**，同上 |
| `thinking` | `true` | `true`（不变，本已显式设值） | 支持 |
| `reasoning_effort` | `low` | `low`（不变，本已显式设值） | 支持 |
| `max_tokens` | `384000` | `384000`（不变） | 支持 |

**核实方法**：直接读取本机真实运行的 Docker Dify 实例（`docker-plugin_daemon-1`，`langgenius/dify-plugin-daemon:0.6.3-local`）挂载的插件包文件
`.../langgenius/deepseek-0.0.20@850efe73.../models/llm/deepseek-v4-flash.yaml`，其 `parameter_rules` 字段只列出六项：`temperature`/`max_tokens`/`top_p`/`thinking`/`reasoning_effort`/`response_format`。不是猜测、不是查文档，是这台机器上实际部署的插件包字节本身。

## 勘误 001 §2 授权的 empirical 冒烟（已执行）

**执行路径**：`account-operations/tools/dify_client.py` 新增 `Console.import_dsl` / `Console.publish_workflow`
（方法体内注明了路由核实来源：本机 `docker-api-1` 容器内 `controllers/console/app/app_import.py` 与
`controllers/console/app/workflow.py` 的实际源码，不是查文档）。用这两个方法从
`content-production/workflows/DIYU_M4_TOOL_PUBLISHING_PACKAGING_v1_4.yml`（导入前现场复算 sha256
`82cadc343ecdf9bfd3d8346f94141403d9d2aa95b41b4866f3cd4f2b48f520c3`，与本任务交付的 v1.4 文件一致）
新建**一个**独立测试应用并发布，未改动、未删除、未发布任何既有应用（含 v1.3 已发布应用）。

| 项 | 值 |
|---|---|
| 新建测试应用 `app_id` | `06a7cde6-9462-41b5-a4fd-f44c90740445` |
| 应用名 | `DIYU-M4-PP-v1_4-DETERMINISM-SMOKE-B01-20260902` |
| 传输路径 | `direct`（本次宿主到 nginx 的端口代理可用，未走 `docker exec` relay） |
| Service API key | 仅存在于本次驱动脚本进程内存，未写入任何文件、未提交仓库 |
| 同一输入 | 一组合法输入（`content_body_or_beats`/`content_promise`/`explicit_non_promise`/`facts_registered`/`cta_contract`/`asset_publish_permission` 六项必需字段齐全，另含 `FACT-001`/`FACT-002` 两条可解析事实登记），`response_mode=blocking` |

### 三次调用结果

| 次序 | HTTP 状态 | workflow 状态 | 耗时(s) | 说明 |
|---|---|---|---|---|
| 第 1 次 | 200 | `failed` | 3.04 | **传输层故障，非模型行为**：`[models] Server Unavailable Error, HTTPSConnectionPool(host='api.deepseek.com', ...): SSLError(SSLEOFError(...))`。`total_tokens: 0`——模型从未接到请求，未产出任何可比较内容。 |
| 第 2 次 | 200 | `succeeded` | 144.81 | 正常产出，四对标记块（ARTIFACT/USER_DELIVERY/RETURNS/FACT_LEDGER）各恰好出现一次，结构良好 |
| 第 3 次 | 200 | `succeeded` | 271.56 | 正常产出，四对标记块同样各恰好出现一次，结构良好 |

**`model_calls_used` 记为 `3`**：三次 HTTP 调用均已发出，用满勘误 001 授权的 `3` 次上限。第 1 次
在到达模型前即因外部网络故障失败（`total_tokens: 0`），**不产出可比较的输出**——这不是本次改动
造成的，是 `docker-api-1` 到 `api.deepseek.com` 之间的一次瞬时 TLS 故障（`FAILURE TRIAGE` 归因：
`INPUT_ENVIRONMENT_OR_TOOL`，非 `SYSTEM_UNDER_TEST`）。因此实际可比较的成功产出只有 **2 组**（第 2、3 次），
不是勘误 001 §3 预设判据表所假定的 3 组——这是判据表未覆盖的情形，如实登记，不强行凑成"3 组都比过"。

**为什么这不影响"情形 A / 情形 B"的判定，因此未消耗第 4 次调用去补第 3 组**：
情形 A（三次逐字节相同）要求**全部**样本互相一致；但第 2、3 次已经互相不一致（见下表），
即"至少存在两组不同的样本"这一事实已经成立，无论假设中的第三个成功样本长什么样，
都不可能让"全部三组相同"重新成立。因此第 2、3 次的比较结果已足以排除情形 A、
直接进入情形 B 的处置，一次额外调用不会改变结论，遂未发起（也已用满 `3` 次上限，
无授权可用的第 4 次）。

### 字节级比对（第 2 次 vs 第 3 次，唯二可比较的成功产出）

| 字段 | 第 2 次 | 第 3 次 | 是否相同 |
|---|---|---|---|
| `raw_preserved`（完整原文，四块合一） | 4777 字节 | 6272 字节 | **否**（长度相差 1495 字节，sha256 不同） |
| `artifact`（`---M4_ARTIFACT---` 块） | 3482 字节 | 4566 字节 | **否**（长度相差 1084 字节，约 31%，sha256 不同） |
| `user_delivery`（`---M4_USER_DELIVERY---` 块） | 818 字节 | 934 字节 | **否**（长度相差 116 字节，约 14%，sha256 不同） |

**结论：三次逐字节相同 —— 不成立。`temperature=0` 的贪心解码在这套 provider/model 栈上不保证字节级确定性，与开工前已如实登记的边界判断一致（浮点非结合性 + `thinking` 推理段的已知成因，非本次改动引入）。**

### 差异位置与差异性质（结构性描述，不贴输出正文，供阶段三设计 k 次判据使用）

- **结构骨架完全一致**：两次都恰好产出四对标记块（`M4_ARTIFACT`/`M4_USER_DELIVERY`/`M4_RETURNS`/`M4_FACT_LEDGER`），各闭合一次，无缺失、无重复。
- **门控结论完全一致**：`sufficiency_status=SUFFICIENT`、`artifact_status=OK`、`user_delivery_status=OK`、`returns_status=NONE`、`delivery_outcome=DELIVERED`、`recovery_used=false`、`local_block=false`——两次都通过了 B-02（事实核验）与 B-04（市场断言检测）两道代码判定关，未触发任何阻断分支，说明本次差异**不是**来自 B-02/B-04 新增节点的行为不一致，两次走的是完全相同的路由路径。
- **差异出现在正文内容本身，且不是"仅措辞不同、字段值全同"这一较轻量级**：`ARTIFACT` 块与 `USER_DELIVERY` 块两次的字节长度都有实质性差异（分别约 31% 与 14%），说明模型两次生成的**内容详略程度不同**（例如候选点位、支撑细节的展开量不同），不是同一段内容的同义改写。这一差异幅度比勘误 001 §3 举例的"仅 USER_DELIVERY 块措辞不同、ARTIFACT 块字段值全同"更大，如实登记，不淡化。
- `M4_RETURNS` 块两次均为 `NONE`（无回改）——这一项在两次运行中保持一致。

## 处置（按勘误 001 §3 预先写死的判据，事后未放宽）

```yaml
b01_status: CLOSED_AT_CONFIG_LAYER_ONLY
byte_determinism: NOT_ACHIEVABLE_ON_THIS_STACK
downgraded_criterion: OUTCOME_STABILITY
```

判据从"字节一致"降为"结果一致"：验收标准 §21 要的是能否**稳定产生**用户愿意付费的专业增量，
是结果稳定，不是字节相同。B-01 的真实收尾方式是把稳定性判据搬到阶段三——每 Case 跑 k≥3 次，
要求硬门结论（本次冒烟里即 `sufficiency_status`/`artifact_status`/`user_delivery_status`/
`returns_status`/`delivery_outcome` 这一组）在 k 次上一致（全过或全不过），而非字节一致。
该要求已写在 `P0_推进路线图_v1.0.md` 阶段三 S7/S8——本次两组样本的门控结论恰好就是"全过一致"的
一个正例数据点，可作为阶段三设计该判据时的参考，但两组不构成统计意义上的验证，不据此宣称阶段三判据已验证。

**不回改为 `CLOSED`**——按勘误 001 预先写死的规则，此结果不允许改判为字节级 `CLOSED`。

## 未使用的补充动作（不擅自执行）

第 1 次调用的传输层失败使实际可比较样本少于协议假设的 3 组；如 Founder 认为需要补一组成功样本
以获得更完整的三方对比数据（用于阶段三 k 次判据设计，而非改变本文件已给出的处置结论——
该结论在数学上已被第 2/3 次的不一致锁定，见上文），需另行授权第 4 次调用（超出勘误 001
`model_calls_max: 3` 的既有上限），执行侧不擅自视为已获授权。
