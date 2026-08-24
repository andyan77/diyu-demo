# 拍摄前生产链 · PRE Chain Run 001 运行证据

单一证据文件。目标：经 Workflow Tool 串联 Creative Script → Production Director →
Publishing & Packaging（PRE），逐段核验哈希，汇总正式回改，交人工评审出口。
**本轮不处理真实素材，不生成 `realization_manifest`，不进入 FINAL。**

---

## 一、最终状态

| 项 | 值 |
|---|---|
| 本轮判定 | **PARTIAL —— 未跑出成功整链** |
| `chain_status` | `未产出（Stage 2 未被调用）` |
| `pp_mode` | `未产出（PP 本轮未运行）` |
| `final_present` | `未产出` |
| 已产出的段 | Creative Script（真实产出，见第九节） |
| 未运行的段 | Production Director、Publishing & Packaging |
| 串联形态 | **两段式**（Stage 1 CS→PD ＋ Stage 2 PP），单链受运行时限不可行 |
| Skill 调用方式 | 三份全部经 Workflow Tool；父流不含任何 Skill / reference 正文 |
| 正式回改条数 | 未汇总（需整链） |
| 普通备注条数 | 未汇总（需整链） |

## 二、运行时限预检

建父工作流**之前**完成，逐项实测，不使用默认印象。

| 时限项 | 实际值 | 来源 |
|---|---|---|
| Workflow 总执行时限 | **1200 s** | `.env` 未设置 → 代码默认 `WORKFLOW_MAX_EXECUTION_TIME`；api / worker 均无覆盖 |
| 超时判定方式 | **只在节点边界判定**，不中途中断 | `graphon/graph_engine/layers/execution_limits.py`：仅 `NodeRunSucceededEvent` / `NodeRunFailedEvent` 上检查 |
| **单次 LLM 调用时限** | **600 s 硬顶** | `.env:240` `PLUGIN_MAX_EXECUTION_TIMEOUT=600` → compose 传 `plugin_daemon` |
| Workflow Tool 单次调用 | **无独立时限**；子流进程内调起，另获完整 1200 s 预算 | `core/tools/workflow_as_tool/tool.py`（`WorkflowAppGenerator.generate()`） |
| 调用深度上限 | `WORKFLOW_CALL_MAX_DEPTH = 5`（本链深度 1） | `dify_config` |
| 步数上限 | `WORKFLOW_MAX_EXECUTION_STEPS = 500`（本链 ≤ 12） | `dify_config` |
| 单变量大小 | `MAX_VARIABLE_SIZE = 204800` | `dify_config` |
| API 请求时限 | `GUNICORN_TIMEOUT=360`，但 `SERVER_WORKER_CLASS=gevent` → worker 心跳超时、非请求超时 | `.env:60-67`；P02 实证 505 s 请求成功 |
| 反向代理 | `NGINX_PROXY_READ_TIMEOUT` / `SEND_TIMEOUT` 均 `3600s` | `.env:294-295` |
| Worker（Celery） | blocking 模式工作流不走 Celery | — |
| Code 节点 | `SANDBOX_WORKER_TIMEOUT=15`、`CODE_EXECUTION_READ_TIMEOUT=60`、`CODE_MAX_STRING_LENGTH=400000` | `.env:198-203` |

### 2.1 单链为什么放不下

P02 三段实测 505.7 ＋ 559.6 ＋ 403.9 ＝ **1469.3 s** > 1200 s。
因为超时只在节点边界判定，单链的结局是最坏的一种：

| 时点 | 事件 | 判定 |
|---|---|---|
| t ≈ 506 s | CS Tool 完成 | 506 < 1200，放行 |
| t ≈ 1066 s | PD Tool 完成 | 1066 < 1200，放行 |
| t ≈ 1470 s | PP Tool 完成 | **1470 > 1200 → abort** |

三段 token 全部烧完，**Return Aggregation 与 End 都不执行，产出为零**。
按任务书三.1「不强行建设不可运行的单链」，未建单链，改两段式。

### 2.2 预检第一版漏掉 600 s，被 Run 001 当场抓出

第一版预检判定「Workflow Tool 不经插件守护进程，故 `PLUGIN_MAX_EXECUTION_TIMEOUT=600` 不适用」。
**该判断只对 Tool 调用本身成立**——子流内部的 LLM 节点仍经守护进程调模型，
每一次 LLM 调用都被 600 s 硬顶。Run 001 的 CS 正是死在这条线上。

两条时限并列，缺一不可：

- **1200 s 工作流总时限** —— 决定一个父流能串几段；
- **600 s 单次 LLM 调用硬顶** —— 决定单个 Skill 跑不跑得完，**与分段方式无关，怎么拆都拆不掉**。

回看 P02：三段 LLM 节点 504.9 / 558.9 / 403.4 s，最紧的 PD **只剩 41 s 余量**，当时未被识别。

---


## 三、父应用、Workflow Tool 与 Run ID


### 3.1 应用

| 角色 | 应用名 | `app_id` | 已发布 `workflow_id` |
|---|---|---|---|
| 父流 Stage 1 | DIYU Demo Content Production PRE Chain v0.1 · Stage 1 | `4eac6ab7-9d81-4af0-accf-740e3157f5ea` | `c11b5370-45f8-430f-a24b-4431cafb858c` |
| 父流 Stage 2 | DIYU Demo Content Production PRE Chain v0.1 · Stage 2 | `2c188608-0559-4ef4-8c76-18b4f48c3cd9` | `75f882de-126c-4574-9140-9d7b498fbb2f` |
| 子流 Creative Script | DIYU Demo Creative Script v0.1 | `13ba9e70-2193-4217-9ac8-32bfda2a7822` | `149a066e-6783-4a89-8212-9aa6785db1a9` |
| 子流 Production Director | DIYU Demo Production Director v0.1 | `4433b747-4216-44d6-b8bb-e6664d3cf4fb` | `767342ce-d81d-412b-b71d-b0778afe6f8d` |
| 子流 Publishing & Packaging | DIYU Demo Publishing Packaging v0.1 | `fa71a06d-2b0d-4d09-b580-ca8e2db5f0a6` | `7ea6c2fd-3d35-49d9-a9aa-911f9c7b1ec5` |

### 3.2 三个 Workflow Tool

由 P02 三个独立 Workflow 发布而成，**未覆盖任何已有工具**（后端对同名或同 app 的工具直接拒绝创建；
既有 `diyu_v1_matrix_architect` / `diyu_v1_campaign_orchestrator` / `diyu_v1_content_brief_architect` 原样保留）。

| 工具名 | `provider_id` | 绑定应用 | 参数数 | 本轮实际调用状态 |
|---|---|---|---|---|
| `diyu_content_creative_script` | `c9af3cc2-8fd4-447d-ac70-133b98d2d876` | 子流 Creative Script | 11 | `succeeded`（478.0 s） |
| `diyu_content_production_director` | `34998db2-fb62-4658-a1f1-5e1e1b9d4ec4` | 子流 Production Director | 12 | **未成功** |
| `diyu_content_publishing_packaging` | `154a3dd0-1451-45cf-a061-5f0fde255470` | 子流 Publishing & Packaging | 11 | **未成功** |

每个 Tool 至少返回：`final_output` / `final_present` / `model_used` / `reference_projection`。
另经确定性 Returns Adapter 暴露：`return_to_script[]` / `return_to_production[]` /
`advisory_notes[]` / `returns_status` / `returns_parse_note` / `declared_mode`（PP 的 `mode`）。

> **PP 工具的参数签名里含 `subject_domain` 与 `duration_band`。**
> 二者是 PP 的硬输入——缺 `subject_domain`，Reference Projection 选不出行业块、投影节点空跑；
> 缺 `duration_band`，PP-1 的候选取向只能反推并被迫挂一条本不必要的假设。
> 现已焊进工具参数签名，少传即调用失败，不再依赖文档约定。

### 3.3 本轮全部 Run

| 时间 | 应用 | Run ID | 状态 | 耗时 s | tokens | 备注 |
|---|---|---|---|---|---|---|
| 04:58:44 | 父流 Stage 1 | `226439af` | `stopped` | 1000.3 | 0 | Aborted: App task was stopped |
| 04:58:44 | 子流 Creative Script | `a64e33b4` | `failed` | 600.2 | 0 | [deepseek] Error: req_id: 3f4bc68dc4 PluginDaemonInternalServerError: killed by  |
| 05:08:47 | 子流 Creative Script | `c4c19354` | `stopped` | 397.4 | 0 | Aborted: User requested stop |
| 05:20:01 | 父流 Stage 1 | `91f2c804` | `partial-succeeded` | 600.7 | 0 | — |
| 05:20:02 | 子流 Creative Script | `80da7ada` | `failed` | 600.3 | 0 | [deepseek] Error: req_id: 2215b61043 PluginDaemonInternalServerError: killed by  |
| 05:30:02 | 父流 Stage 1 | `02e1a654` | `partial-succeeded` | 600.6 | 0 | — |
| 05:30:02 | 子流 Creative Script | `1269b6cb` | `failed` | 600.3 | 0 | [deepseek] Error: req_id: 597fe85419 PluginDaemonInternalServerError: killed by  |
| 05:43:33 | 父流 Stage 1 | `3ddb5808` | `partial-succeeded` | 567.8 | 50724 | — |
| 05:43:34 | 子流 Creative Script | `ff70e42f` | `succeeded` | 562.9 | 50724 | — |
| 05:52:57 | 子流 Production Director | `cef777a4` | `failed` | 4.3 | 0 | [models] Server Unavailable Error, HTTPSConnectionPool(host='api.deepseek.com',  |
| 05:53:01 | 父流 Stage 1 | `30de4ce2` | `partial-succeeded` | 179.9 | 0 | — |
| 05:53:01 | 子流 Creative Script | `ab8ae26a` | `failed` | 179.5 | 0 | req_id: cc3b6e7e24 PluginInvokeError: {"args":{"traceback":"Traceback (most rece |
| 06:00:48 | 父流 Stage 1 | `04f6ad05` | `partial-succeeded` | 600.6 | 0 | — |
| 06:00:48 | 子流 Creative Script | `07662a5e` | `failed` | 600.2 | 0 | [deepseek] Error: req_id: 4fb4e434ab PluginDaemonInternalServerError: killed by  |
| 06:10:48 | 父流 Stage 1 | `483a88f8` | `partial-succeeded` | 490.4 | 68752 | — |
| 06:10:49 | 子流 Creative Script | `c6449144` | `succeeded` | 478.0 | 68752 | — |
| 06:18:47 | 子流 Production Director | `47c2f0f0` | `failed` | 11.7 | 0 | [models] Connection Error, HTTPSConnectionPool(host='api.deepseek.com', port=443 |
| 06:29:30 | 父流 Stage 1 | `2911d6a1` | `partial-succeeded` | 600.3 | 0 | — |
| 06:29:30 | 子流 Creative Script | `774c0966` | `failed` | 600.0 | 0 | [deepseek] Error: req_id: c78004afdb PluginDaemonInternalServerError: killed by  |
| 06:39:31 | 父流 Stage 1 | `7b9d67d9` | `partial-succeeded` | 600.7 | 0 | — |
| 06:39:31 | 子流 Creative Script | `c289f4c0` | `failed` | 600.2 | 0 | [deepseek] Error: req_id: 5d1a539da8 PluginDaemonInternalServerError: killed by  |
| 06:50:17 | 父流 Stage 1 | `59c2272c` | `partial-succeeded` | 4.7 | 0 | — |
| 06:50:17 | 子流 Creative Script | `614f3229` | `failed` | 4.3 | 0 | [models] Server Unavailable Error, HTTPSConnectionPool(host='api.deepseek.com',  |
| 06:50:22 | 父流 Stage 1 | `fb93bcf0` | `partial-succeeded` | 600.6 | 0 | — |
| 06:50:22 | 子流 Creative Script | `e1791cbd` | `failed` | 600.2 | 0 | [deepseek] Error: req_id: ad16e6bfd6 PluginDaemonInternalServerError: killed by  |

## 四、失败与重试记录（全部保留，未删除）

**`226439af-a9f0-43a9-bcd8-986dde4e87db`** —— 父流 Stage 1，`stopped`，1000.3 s
> `Aborted: App task was stopped`

| # | 节点 | 类型 | 状态 | 耗时 s |
|---|---|---|---|---|
| 1 | 输入 | `start` | `succeeded` | 0.0 |
| 2 | Input Check | `code` | `succeeded` | 0.1 |
| 3 | 输入闸 | `if-else` | `succeeded` | 0.0 |
| 4 | Creative Script Tool | `tool` | `retry` | 0.0 |

**`a64e33b4-b2b2-4e23-b7a5-9626042e398e`** —— 子流 Creative Script，`failed`，600.2 s
> `[deepseek] Error: req_id: 3f4bc68dc4 PluginDaemonInternalServerError: killed by timeout`

| # | 节点 | 类型 | 状态 | 耗时 s |
|---|---|---|---|---|
| 1 | 输入 | `start` | `succeeded` | 0.0 |
| 2 | Reference Projection | `template-transform` | `succeeded` | 0.1 |
| 3 | Projection Record | `template-transform` | `succeeded` | 0.1 |
| 4 | DIYU Demo Creative Script v0.1 | `llm` | `failed` | 600.0 |

**`c4c19354-a8a1-473f-8a3c-67b7c9d2cdbc`** —— 子流 Creative Script，`stopped`，397.4 s
> `Aborted: User requested stop`

| # | 节点 | 类型 | 状态 | 耗时 s |
|---|---|---|---|---|
| 1 | 输入 | `start` | `succeeded` | 0.0 |
| 2 | Reference Projection | `template-transform` | `succeeded` | 0.1 |
| 3 | Projection Record | `template-transform` | `succeeded` | 0.1 |
| 4 | DIYU Demo Creative Script v0.1 | `llm` | `failed` | 397.2 |

**`91f2c804-8a97-4358-bb3e-b0efc3bad74e`** —— 父流 Stage 1，`partial-succeeded`，600.7 s

| # | 节点 | 类型 | 状态 | 耗时 s |
|---|---|---|---|---|
| 1 | 输入 | `start` | `succeeded` | 0.0 |
| 2 | Input Check | `code` | `succeeded` | 0.1 |
| 3 | 输入闸 | `if-else` | `succeeded` | 0.0 |
| 4 | Creative Script Tool | `tool` | `exception` | 600.5 |
| 5 | CS Tool 失败标记 | `code` | `succeeded` | 0.1 |
| 6 | CS Tool 失败结束 | `end` | `succeeded` | 0.0 |

**`80da7ada-20aa-4853-952b-3ae63cdb964f`** —— 子流 Creative Script，`failed`，600.3 s
> `[deepseek] Error: req_id: 2215b61043 PluginDaemonInternalServerError: killed by timeout`

| # | 节点 | 类型 | 状态 | 耗时 s |
|---|---|---|---|---|
| 1 | 输入 | `start` | `succeeded` | 0.0 |
| 2 | Reference Projection | `template-transform` | `succeeded` | 0.1 |
| 3 | Projection Record | `template-transform` | `succeeded` | 0.1 |
| 4 | DIYU Demo Creative Script v0.1 | `llm` | `failed` | 600.0 |

**`02e1a654-53a9-43ca-95be-757e378fdc76`** —— 父流 Stage 1，`partial-succeeded`，600.6 s

| # | 节点 | 类型 | 状态 | 耗时 s |
|---|---|---|---|---|
| 1 | 输入 | `start` | `succeeded` | 0.0 |
| 2 | Input Check | `code` | `succeeded` | 0.1 |
| 3 | 输入闸 | `if-else` | `succeeded` | 0.0 |
| 4 | Creative Script Tool | `tool` | `exception` | 600.4 |
| 5 | CS Tool 失败标记 | `code` | `succeeded` | 0.1 |
| 6 | CS Tool 失败结束 | `end` | `succeeded` | 0.0 |

**`1269b6cb-d5c5-41f2-aa2f-a8357848eba4`** —— 子流 Creative Script，`failed`，600.3 s
> `[deepseek] Error: req_id: 597fe85419 PluginDaemonInternalServerError: killed by timeout`

| # | 节点 | 类型 | 状态 | 耗时 s |
|---|---|---|---|---|
| 1 | 输入 | `start` | `succeeded` | 0.0 |
| 2 | Reference Projection | `template-transform` | `succeeded` | 0.1 |
| 3 | Projection Record | `template-transform` | `succeeded` | 0.1 |
| 4 | DIYU Demo Creative Script v0.1 | `llm` | `failed` | 600.0 |

**`3ddb5808-5681-4391-867c-d05827cca75d`** —— 父流 Stage 1，`partial-succeeded`，567.8 s

| # | 节点 | 类型 | 状态 | 耗时 s |
|---|---|---|---|---|
| 1 | 输入 | `start` | `succeeded` | 0.0 |
| 2 | Input Check | `code` | `succeeded` | 0.1 |
| 3 | 输入闸 | `if-else` | `succeeded` | 0.0 |
| 4 | Creative Script Tool | `tool` | `succeeded` | 563.0 |
| 5 | CS Extract & Hash | `code` | `succeeded` | 0.1 |
| 6 | CS 闸 | `if-else` | `succeeded` | 0.0 |
| 7 | CS Handoff Check | `code` | `succeeded` | 0.0 |
| 8 | Production Director Tool | `tool` | `exception` | 4.4 |
| 9 | PD Tool 失败标记 | `code` | `succeeded` | 0.1 |
| 10 | PD Tool 失败结束 | `end` | `succeeded` | 0.0 |

**`cef777a4-534a-4faf-a3ac-53355e078e50`** —— 子流 Production Director，`failed`，4.3 s
> `[models] Server Unavailable Error, HTTPSConnectionPool(host='api.deepseek.com', port=443): Max retries exceeded with url: /chat/completions (Caused by NameResolutionError("HTTPSConnection(host='api.deepseek.com', port=443): Failed to resolve 'api.deepseek.com' ([Errno -3] Temporary failure in name r`

| # | 节点 | 类型 | 状态 | 耗时 s |
|---|---|---|---|---|
| 1 | 输入 | `start` | `succeeded` | 0.0 |
| 2 | Reference Projection | `template-transform` | `succeeded` | 0.1 |
| 3 | Projection Record | `template-transform` | `succeeded` | 0.1 |
| 4 | DIYU Demo Production Director v0.1 | `llm` | `failed` | 4.0 |

**`30de4ce2-a524-447a-9449-b2f99bde6351`** —— 父流 Stage 1，`partial-succeeded`，179.9 s

| # | 节点 | 类型 | 状态 | 耗时 s |
|---|---|---|---|---|
| 1 | 输入 | `start` | `succeeded` | 0.0 |
| 2 | Input Check | `code` | `succeeded` | 0.1 |
| 3 | 输入闸 | `if-else` | `succeeded` | 0.0 |
| 4 | Creative Script Tool | `tool` | `exception` | 179.7 |
| 5 | CS Tool 失败标记 | `code` | `succeeded` | 0.1 |
| 6 | CS Tool 失败结束 | `end` | `succeeded` | 0.0 |

**`ab8ae26a-0e0f-4fa5-a541-4425fcedd31f`** —— 子流 Creative Script，`failed`，179.5 s
> `req_id: cc3b6e7e24 PluginInvokeError: {"args":{"traceback":"Traceback (most recent call last):\n  File \"/app/storage/cwd/langgenius/deepseek-0.0.20@850efe73fb62bbe7ab2229116086596596297a77174fb86f73e1363b99a24116/.venv/lib/python3.12/site-packages/requests/models.py\", line 937, in generate\n    yi`

| # | 节点 | 类型 | 状态 | 耗时 s |
|---|---|---|---|---|
| 1 | 输入 | `start` | `succeeded` | 0.0 |
| 2 | Reference Projection | `template-transform` | `succeeded` | 0.1 |
| 3 | Projection Record | `template-transform` | `succeeded` | 0.1 |
| 4 | DIYU Demo Creative Script v0.1 | `llm` | `failed` | 179.2 |

**`04f6ad05-456a-4819-8be3-7197740aee77`** —— 父流 Stage 1，`partial-succeeded`，600.6 s

| # | 节点 | 类型 | 状态 | 耗时 s |
|---|---|---|---|---|
| 1 | 输入 | `start` | `succeeded` | 0.0 |
| 2 | Input Check | `code` | `succeeded` | 0.1 |
| 3 | 输入闸 | `if-else` | `succeeded` | 0.0 |
| 4 | Creative Script Tool | `tool` | `exception` | 600.4 |
| 5 | CS Tool 失败标记 | `code` | `succeeded` | 0.1 |
| 6 | CS Tool 失败结束 | `end` | `succeeded` | 0.0 |

**`07662a5e-70bf-44b5-bd58-5a5c4f7df4d2`** —— 子流 Creative Script，`failed`，600.2 s
> `[deepseek] Error: req_id: 4fb4e434ab PluginDaemonInternalServerError: killed by timeout`

| # | 节点 | 类型 | 状态 | 耗时 s |
|---|---|---|---|---|
| 1 | 输入 | `start` | `succeeded` | 0.0 |
| 2 | Reference Projection | `template-transform` | `succeeded` | 0.1 |
| 3 | Projection Record | `template-transform` | `succeeded` | 0.1 |
| 4 | DIYU Demo Creative Script v0.1 | `llm` | `failed` | 600.0 |

**`483a88f8-ce3a-4c74-b4f8-14a0cf6868ab`** —— 父流 Stage 1，`partial-succeeded`，490.4 s

| # | 节点 | 类型 | 状态 | 耗时 s |
|---|---|---|---|---|
| 1 | 输入 | `start` | `succeeded` | 0.0 |
| 2 | Input Check | `code` | `succeeded` | 0.1 |
| 3 | 输入闸 | `if-else` | `succeeded` | 0.0 |
| 4 | Creative Script Tool | `tool` | `succeeded` | 478.2 |
| 5 | CS Extract & Hash | `code` | `succeeded` | 0.0 |
| 6 | CS 闸 | `if-else` | `succeeded` | 0.0 |
| 7 | CS Handoff Check | `code` | `succeeded` | 0.0 |
| 8 | Production Director Tool | `tool` | `exception` | 11.8 |
| 9 | PD Tool 失败标记 | `code` | `succeeded` | 0.1 |
| 10 | PD Tool 失败结束 | `end` | `succeeded` | 0.0 |

**`47c2f0f0-6ee1-4b94-8c93-e158166942a4`** —— 子流 Production Director，`failed`，11.7 s
> `[models] Connection Error, HTTPSConnectionPool(host='api.deepseek.com', port=443): Read timed out. (read timeout=10)`

| # | 节点 | 类型 | 状态 | 耗时 s |
|---|---|---|---|---|
| 1 | 输入 | `start` | `succeeded` | 0.0 |
| 2 | Reference Projection | `template-transform` | `succeeded` | 0.1 |
| 3 | Projection Record | `template-transform` | `succeeded` | 0.1 |
| 4 | DIYU Demo Production Director v0.1 | `llm` | `failed` | 11.5 |

**`2911d6a1-8499-4b4d-b6fb-13d00702d90d`** —— 父流 Stage 1，`partial-succeeded`，600.3 s

| # | 节点 | 类型 | 状态 | 耗时 s |
|---|---|---|---|---|
| 1 | 输入 | `start` | `succeeded` | 0.0 |
| 2 | Input Check | `code` | `succeeded` | 0.1 |
| 3 | 输入闸 | `if-else` | `succeeded` | 0.0 |
| 4 | Creative Script Tool | `tool` | `exception` | 600.1 |
| 5 | CS Tool 失败标记 | `code` | `succeeded` | 0.0 |
| 6 | CS Tool 失败结束 | `end` | `succeeded` | 0.0 |

**`774c0966-769c-4558-9c32-37c42b053bb9`** —— 子流 Creative Script，`failed`，600.0 s
> `[deepseek] Error: req_id: c78004afdb PluginDaemonInternalServerError: killed by timeout`

| # | 节点 | 类型 | 状态 | 耗时 s |
|---|---|---|---|---|
| 1 | 输入 | `start` | `succeeded` | 0.0 |
| 2 | Reference Projection | `template-transform` | `succeeded` | 0.1 |
| 3 | Projection Record | `template-transform` | `succeeded` | 0.1 |
| 4 | DIYU Demo Creative Script v0.1 | `llm` | `failed` | 599.7 |

**`7b9d67d9-b500-4759-b5e8-c8a542a30de2`** —— 父流 Stage 1，`partial-succeeded`，600.7 s

| # | 节点 | 类型 | 状态 | 耗时 s |
|---|---|---|---|---|
| 1 | 输入 | `start` | `succeeded` | 0.0 |
| 2 | Input Check | `code` | `succeeded` | 0.0 |
| 3 | 输入闸 | `if-else` | `succeeded` | 0.0 |
| 4 | Creative Script Tool | `tool` | `exception` | 600.4 |
| 5 | CS Tool 失败标记 | `code` | `succeeded` | 0.1 |
| 6 | CS Tool 失败结束 | `end` | `succeeded` | 0.0 |

**`c289f4c0-b349-49bd-ac67-07a937c79863`** —— 子流 Creative Script，`failed`，600.2 s
> `[deepseek] Error: req_id: 5d1a539da8 PluginDaemonInternalServerError: killed by timeout`

| # | 节点 | 类型 | 状态 | 耗时 s |
|---|---|---|---|---|
| 1 | 输入 | `start` | `succeeded` | 0.0 |
| 2 | Reference Projection | `template-transform` | `succeeded` | 0.1 |
| 3 | Projection Record | `template-transform` | `succeeded` | 0.1 |
| 4 | DIYU Demo Creative Script v0.1 | `llm` | `failed` | 600.0 |

**`59c2272c-4f2e-4f87-8a07-c2f8c1cf772d`** —— 父流 Stage 1，`partial-succeeded`，4.7 s

| # | 节点 | 类型 | 状态 | 耗时 s |
|---|---|---|---|---|
| 1 | 输入 | `start` | `succeeded` | 0.0 |
| 2 | Input Check | `code` | `succeeded` | 0.1 |
| 3 | 输入闸 | `if-else` | `succeeded` | 0.0 |
| 4 | Creative Script Tool | `tool` | `exception` | 4.4 |
| 5 | CS Tool 失败标记 | `code` | `succeeded` | 0.0 |
| 6 | CS Tool 失败结束 | `end` | `succeeded` | 0.0 |

**`614f3229-f807-4e9b-a8d0-93b9113a25f1`** —— 子流 Creative Script，`failed`，4.3 s
> `[models] Server Unavailable Error, HTTPSConnectionPool(host='api.deepseek.com', port=443): Max retries exceeded with url: /chat/completions (Caused by NameResolutionError("HTTPSConnection(host='api.deepseek.com', port=443): Failed to resolve 'api.deepseek.com' ([Errno -3] Temporary failure in name r`

| # | 节点 | 类型 | 状态 | 耗时 s |
|---|---|---|---|---|
| 1 | 输入 | `start` | `succeeded` | 0.0 |
| 2 | Reference Projection | `template-transform` | `succeeded` | 0.1 |
| 3 | Projection Record | `template-transform` | `succeeded` | 0.1 |
| 4 | DIYU Demo Creative Script v0.1 | `llm` | `failed` | 4.0 |

**`fb93bcf0-bb44-42b3-b29e-f4cea272f317`** —— 父流 Stage 1，`partial-succeeded`，600.6 s

| # | 节点 | 类型 | 状态 | 耗时 s |
|---|---|---|---|---|
| 1 | 输入 | `start` | `succeeded` | 0.0 |
| 2 | Input Check | `code` | `succeeded` | 0.1 |
| 3 | 输入闸 | `if-else` | `succeeded` | 0.0 |
| 4 | Creative Script Tool | `tool` | `exception` | 600.4 |
| 5 | CS Tool 失败标记 | `code` | `succeeded` | 0.0 |
| 6 | CS Tool 失败结束 | `end` | `succeeded` | 0.0 |

**`e1791cbd-02e7-4e7e-99b5-a1897724d6ff`** —— 子流 Creative Script，`failed`，600.2 s
> `[deepseek] Error: req_id: ad16e6bfd6 PluginDaemonInternalServerError: killed by timeout`

| # | 节点 | 类型 | 状态 | 耗时 s |
|---|---|---|---|---|
| 1 | 输入 | `start` | `succeeded` | 0.0 |
| 2 | Reference Projection | `template-transform` | `succeeded` | 0.1 |
| 3 | Projection Record | `template-transform` | `succeeded` | 0.1 |
| 4 | DIYU Demo Creative Script v0.1 | `llm` | `failed` | 600.0 |

---


## 五、三段输入输出哈希

**两处独立核对，口径不同，都必须过：**

- **父流侧**：父工作流用 Code 节点对绑给下游 Tool 的那串文本重算 SHA-256，与上游产物哈希比对；
- **子流实收侧**：直接取 Dify 记录的**子工作流 run 的 `inputs`**——那是下游 Skill **实际收到的文本**，由 Dify 自己写库，不经我方任何环节。

| 环节 | 长度 | SHA-256 |
|---|---|---|
| CS 产物 `final_output` | 9213 | `e5b8335390bcf763df015e6e668904054f95b2d279096769fddfb9d38f93319d` |
| PD 实收 `inputs.cs_final` | — | **该段本轮未运行，无产物可哈希** |
| PP 实收 `inputs.cs_final` | — | **该段本轮未运行，无产物可哈希** |
| PD 产物 `final_output` | — | **该段本轮未运行，无产物可哈希** |
| PP 实收 `inputs.pd_final` | — | **该段本轮未运行，无产物可哈希** |
| PP 产物 `final_output` | — | **该段本轮未运行，无产物可哈希** |

| 交接 | 判定 |
|---|---|
| CS 产物 → PD 实收 | **无从核对 —— 下游本轮未运行** |
| CS 产物 → PP 实收 | **无从核对 —— 下游本轮未运行** |
| PD 产物 → PP 实收 | **无从核对 —— 下游本轮未运行** |

> 「无从核对」不等于「核对不通过」：PD 与 PP 本轮从未成功启动，
> 父流的哈希核对节点因此没有执行过，不存在被验证或被证伪的结果。

父流自报哈希：

| 字段 | 父流输出值 | 独立复算 | 一致 |
|---|---|---|---|
| `creative_script_hash` | 未产出（父流成功分支未执行） | `e5b8335390bcf763df015e6e66890405…` | **无从核对** |
| `production_plan_hash` | 未产出 | — | **无从核对** |
| `publishing_pre_hash` | 未产出 | — | **无从核对** |

## 六、reference 投影结果

| Skill | 注入文本长度 | platforms.md | industry 行（服装 / 门店零售） | examples.md |
|---|---|---|---|---|
| CS | 1771 | 第二节 | 常见素材形态·哪一类真的带信息·可用的真实摩擦·特有淘汰项·拍摄条件 | 未加载 |
| PD | — | 该段本轮未运行，投影节点未执行 | — | — |
| PP | — | 该段本轮未运行，投影节点未执行 | — | — |

投影记录（`loaded_reference_sections[]` / `excluded_reference_sections[]` / `reference_hashes{}` / `projection_reason[]`）逐份附在第九节，
**不进入父工作流的用户可见输出**（任务书九：用户可见输出不得含内部 reference 投影全文）。

---


## 七、PP 的 `mode` 推导

父工作流**未预填 `mode`**——Stage 2 的 Start 变量里没有 `mode` 这一项，
PP 的 user prompt 里也没有给出候选值；`mode` 一行只要求写出结论、不给出结论。
**这一点可在提交的 DSL 里逐字复核。**

**但 PP 本轮从未成功运行**（Stage 1 始终未通过，Stage 2 未被调用），
因此 `mode` 没有实际推导结果可记录。**不填任何值，也不推测。**

> 规则照旧生效：若 PP 推出 PRE 以外的值，本证据照实记录实际值与依据，**执行侧不得改成 PRE**。
> 本轮 PP 未运行，**没有实际值可记录**。

## 八、回改汇总与 `chain_status`

### 8.1 正式回改数组

| 数组 | 条数 | 内容 |
|---|---|---|
| `return_to_script[]` | — | （父流汇总未产出：Stage 2 未被调用） |
| `return_to_production[]` | — | （父流汇总未产出：Stage 2 未被调用） |

> **空数组与「未汇总」不是一回事。** 本轮父流的汇总节点从未执行，
> 上表不构成「三个数组为空」的结论——那需要一条成功整链才能得出。

### 8.2 普通备注（不升格为回改）

父流汇总未产出。**但 Creative Script 这一段的 `advisory_notes` 已由确定性适配器成功解析**，逐条见 8.3。

### 8.3 各段自报的原始 `---RETURNS---` 块

**这一节是修正二那套机制的实证**：结构块由模型按格式输出，
再由确定性 Code 节点纯字符串切分解析，全程无第二个 LLM、无正则捞自由文本。

**Creative Script** —— `returns_status = OK`，`OK`

```
return_to_script: NONE
return_to_production: NONE
advisory_notes:
- 最终发布平台未锁定（PROBE_ONLY）——脚本为平台中立母版；平台锁定前不下平台规格设计，也不要把「小红书适配」当已确认方案
- 苏禾出镜方式（纯旁白 vs 真人出镜）建议开拍前锁定；两种方式下逐字稿与段落结构不变
- 内部演示身份标注建议采用"首帧起全程角标＋开场口播"双保险（brief 允许字幕或口播，最终形式由制作确认）
- VID-C01 帧检索按检索判据清单执行；若"脱西装对比单穿"帧缺失，Beat 4 措辞按降级路径改为「至少在我们试的这一次里，正式感能调下来一部分。」
- 若试穿人在素材中有画面内原话，其内容不得超过 C01 已登记观察（不得出现"太好看""特别舒服"等未登记表述）；如有越界，按仅画面无声处理或走上游确认
- 口播稿约 35–40 秒，若成片超时优先压缩发挥区连接词，不动准确区
- 发布前苏禾完成试穿判断复核（brief 发布条件）
```

**Production Director** —— `returns_status = —`，``

```
（无）
```

**Publishing & Packaging** —— `returns_status = —`，``

```
（无）
```

### 8.4 `chain_status`

**`未产出 —— Stage 2 未被调用，汇总节点未执行`**

计数口径与取值规则已写进运行合同第 9 节，并在 Stage 2 的 `Return Aggregation` 代码节点里实现，
**可逐字复核**；本轮无成功整链，故无实际取值。

> 计数不是装饰。`advisory_notes[]` 非空却只报 `PRE_PACKAGE_READY_FOR_REVIEW`，
> 字面意思是「可以评审了」，而备注里其实有实质内容要看——状态名会让人以为没事了。

本轮到人工评审出口为止：**未自动接受任何回改、未自动重跑上游、未给任何产物盖 `USER_ACCEPTED`、
未因产生回改而把下游标 `STALE`。** `STALE` 仍只在「上游重跑后正文哈希实际变化」时触发。

---


## 九、三份产物（全文）


### Creative Script（`creative_script_artifact`）

`run_id` `c6449144-ea6c-4970-a8b8-864e33e410ce` ｜ 9213 字符 ｜ SHA-256 `e5b8335390bcf763df015e6e668904054f95b2d279096769fddfb9d38f93319d` ｜ 耗时 478.0 s ｜ tokens 68752

<details><summary>展开全文</summary>

````markdown
## Creative Script 产出 · BRF-SUHE-001

---

```
content_origin_mode[]
- 已有素材剪辑：VID-C01 试穿记录一（会议与接送连续场景）原片段为主体画面
- 现拍：苏禾旁白录音 + 30 分钟补录（肩/袖/裤长局部特写；必要时补调整动作特写）
- 逐 beat 已标注「事实／素材」两问。必须传给下游——本稿不是纯现拍逐字稿，依赖已有素材的帧检索
```

---

```
creative_directions[]
```

**方向 A「正式感刻度盘」——同一套衣服，当场调给你看**

| 轴 | 内容 |
|---|---|
| 核心矛盾 | 正式感是这套衣服的固定属性，还是一个能拨动的刻度——答案是刻度，而且刻度有下限 |
| 叙事发动机 | 调整动作的实时序列：松领口→松袖口→脱西装→对比。观众跟着看"刻度一级一级被拨下来" |
| 人物关系 | 苏禾与试穿人并肩在画面里完成调整，试穿人即时反馈；苏禾只动衣服，不评价身体 |
| 信息释放顺序 | 严格时序：原状态→逐级调整→落点状态→被保留的→不能下结论的 |
| 视觉前提 | 同一场景、同一套衣服的连续动态变化；"变化过程"本身就是证据（塌/挺只有动态能看出来） |

**方向 B「哪些我能替你看，哪些得你自己去」——以划界为发动机**

| 轴 | 内容 |
|---|---|
| 核心矛盾 | 一条内容能替观众确认什么、不能确认什么——划界不是内容的备注，是内容本身 |
| 叙事发动机 | 每完成一步调整，就划掉一项"内容能确认"的疑问；最后剩下的肩宽、袖长、裤长三项，不是遗憾，是这条内容真正的落点 |
| 人物关系 | 苏禾对观众直接说话，主动不回答——"这三个我替不了你"，把判断权交还本人 |
| 信息释放顺序 | 时序推进＋边界同步收束：观众始终知道"这条线现在划到哪了"；被确认的与被保留的分开呈现 |
| 视觉前提 | 动态试穿画面承担"可调"的证据；肩/袖/裤长局部特写只呈现问题所在的位置，不给答案——两种画面语言就是划界本身 |

**方向 C「留下什么，改变什么」——取舍驱动**

| 轴 | 内容 |
|---|---|
| 核心矛盾 | 调整不是"解决了问题"，而是一次取舍：留下西装和阔腿裤，改变衬衫的穿法角色 |
| 叙事发动机 | 对三件单品逐件裁决（留／改）：为什么留这两件、为什么只改衬衫；裁决过程即内容 |
| 人物关系 | 苏禾作为"做减法"的伙伴，帮观众决定留下什么、放弃什么预期 |
| 信息释放顺序 | 先呈现被保留的（西装＋阔腿裤）→再呈现被改变的（衬衫穿法）→最后呈现仍不能定论的（肩/袖/裤长） |
| 视觉前提 | 镜头时长明显倾向"被保留"的两件，衬衫的镜头更松——镜头语言与取舍同步 |

**轴差检查**（任两方向≥3 轴不同）：
- A vs B：矛盾（刻度 vs 划界）·发动机（过程 vs 划界收束）·关系（并肩操作 vs 直接对观众划界）·视觉（连续动态 vs 动态/特写对照）＝4/5 不同
- B vs C：矛盾（划界 vs 取舍）·发动机（划界 vs 裁决）·关系（交还判断权 vs 帮做减法）·释放顺序（时序收束 vs 保留优先）·视觉（动态/特写对照 vs 镜头时长倾斜）＝5/5 不同
- A vs C：矛盾（刻度 vs 取舍）·发动机（过程 vs 裁决）·关系（并肩 vs 做减法）·释放顺序（时序 vs 保留优先）·视觉（连续动态 vs 时长倾斜）＝5/5 不同

---

```
creative_concept
```

选中 **方向 B「哪些我能替你看，哪些得你自己去」**。指名判据：

1. **落点匹配**：brief 的"唯一新判断"本身就是一条边界陈述（正式程度可经穿法调整，但肩/袖/裤长必须本人试穿）。B 把这条边界从"结尾交代"提为整条内容的发动机；A 的发动机是调整过程，边界只是附属；C 的落点是取舍，边界是尾声。
2. **接力契约**：brief 要求苏禾向周宁交出"哪些可在选择阶段提前识别、哪些仍需本人试穿"。B 的划界结构恰好把这个交接点做成内容本身的落点——周宁的下一条内容可以直接接住"内容替不了你的那三项"。
3. **账号姿态**：苏禾的姿态是"不急于给唯一答案"。B 的"这三个我替不了你"是该姿态最直接的表达；A 和 C 都隐含"帮观众解决"的姿态，与角色偏差。
4. **反转免疫**：brief 明确不得把调整剪成惊人反转。B 的落点是"划界"不是"变好"，机制上不产出反转；A 的"刻度盘"有滑向 before/after reveal 的风险，靠近取消条件"搭配知识课"。
5. **演示身份**：brief 要求"内部演示试穿"必须标注。B 中演示身份不是免责声明，而是判断可信度的来源——"我们能确认的／确认不了的"这个框架天然以内部演示为证据。

排除说明：C 的信息释放顺序（先呈现被保留的）与 brief 指定的叙事结构（从具体事实进入→摩擦→调整→被保留→不能下结论）冲突，不采纳。

段落数声明：**5 段**（短档 ≤60s；逐字稿合计约 157 字，按清晰口播速度约 35–40 秒口播，加段落间停顿与画面呼吸，落在 50–58 秒内）。

---

```
audience_shift
```

让目标顾客从"看这套组合适不适合我"的被动浏览，转为能用"哪些问题穿法可调、哪些必须本人试穿"的框架，描述自己的一个真实穿着问题。（上游给定——概括自「唯一主要顾客变化」）

---

```
content_promise
```

以一次真实的内部演示试穿为证据：展示同一套组合（西装＋衬衫＋阔腿裤）在连续场景（会议＋接送孩子）中暴露的真实问题，呈现"保留西装和阔腿裤、放松衬衫领口袖口、对比单穿"的调整过程与保留决定；并明确划出内容判断的边界——正式程度可经穿法调整（限于本次演示），肩部、袖长、裤长等身体适配问题不替观众下结论，交由本人试穿确认。

---

```
explicit_non_promise[]
```

- 不承诺这套组合适合任何具体人群或场景——不是通用答案
- 不承诺肩宽、袖长、裤长对任何人的适配结果——必须本人试穿
- 不承诺"正式感偏重"对所有人都成立——它是内部演示中试穿人的观察，不是普遍断言
- 不承诺"调整"是唯一或最优方案——是本次演示中验证过的一条路径
- 不承诺任何未登记性能：防水、防风、抗皱、保暖、显瘦等
- 不承诺调整带来了销量或顾客满意度提升
- 不承诺正式感可以无限调低——仅为演示中的有限调整
- 不是现实顾客案例；"会议＋接送孩子"是演示情境
- 不承接预约、到店、成交；本条无 CTA，不加统一承接说明

---

```
tension_mode
```

- 张力：`UNVERIFIED`——内容能验证的部分已验证（正式感可经穿法调整），但肩宽、袖长、裤长对观众本人的适配，内容明确不闭环，留给本人试穿。这是内容主动保留的未验证状态，不是缺漏。
- 替代消费理由：`Utility`——观众带走一个可迁移的判断框架：区分"穿法可调的问题"与"必须本人试穿的问题"。
- 两者并存：张力负责让人看完（"这套到底适不适合我"），Utility 负责被记住和用上（"原来有些问题得自己试"）。

---

```
expression_subject
```

`NATURAL_PERSON`——苏禾。
辨识判据：删掉"苏禾"名字后仍应认出是她的表达——第一人称复数"我们"（内部演示的团队视角）、不评价试穿人身体、不替观众下结论、"能替你看的到这儿了"式的边界陈述。逐字稿按此写。

---

```
opening
```

- 前 3 秒画面：试穿人穿着完整组合（西装＋衬衫＋阔腿裤）的动态全身画面（取自 VID-C01 会议情境段）；首帧起屏幕文字角标「内部演示试穿·非现实顾客」
- 逐字第一句：「这套去开会，没问题——这是我们内部试穿时，最先确认的。」

---

```
script_beats[]
```

**Beat 1 · 事实进入与身份标注**

| 字段 | 内容 |
|---|---|
| 事实 | 有——完整西装＋衬衫组合满足会议场景；内部演示试穿身份 |
| 素材 | 已确认——VID-C01 会议情境片段；随后插入 IMG-P01 三件商品识别卡 |
| state_change | 信息 |
| 逐字稿 | 「这套去开会，没问题——这是我们内部试穿时，最先确认的。」 |
| zone | 准确区（组合满足会议、内部演示身份均为登记事实；"最先确认"是记录的初始问题顺序） |

画面补充说明：试穿人全场画面后插入三件商品识别卡（IMG-P01：XQ-2501 廓形西装／XQ-2502 垂感阔腿裤／XQ-2503 雾蓝棉混衬衫），承担"试的是这三件"的识别功能，不承担任何判断。

**Beat 2 · 真实摩擦**

| 字段 | 内容 |
|---|---|
| 事实 | 有——演示情境"会议＋接送孩子"；试穿人认为连续穿着时层次偏正式 |
| 素材 | 已确认——VID-C01 连续情境／初始问题片段 |
| state_change | 情境＋信息 |
| 逐字稿 | 「但那天试的是连续场景：白天开会，下班接孩子。连着穿下来，整体层次偏正式。」 |
| zone | 「但那天试的是」＝发挥区；「连续场景：白天开会，下班接孩子。连着穿下来，整体层次偏正式。」＝准确区（情境与观察均为登记事实） |

**Beat 3 · 调整过程**

| 字段 | 内容 |
|---|---|
| 事实 | 有——调整过程已登记：保留西装和阔腿裤，放松衬衫领口袖口，比较脱西装后单穿效果 |
| 素材 | 待检索——VID-C01 中"领口/袖口放松""脱西装对比"的帧；缺帧走检索判据清单降级路径 |
| state_change | 理解＋信息 |
| 逐字稿 | 「我们没换别的衣服——西装和阔腿裤不动，把衬衫领口、袖口放松；再把西装脱掉，对比单穿。」 |
| zone | 「我们没换别的衣服——」＝发挥区；「西装和阔腿裤不动，把衬衫领口、袖口放松；再把西装脱掉，对比单穿。」＝准确区（调整动作逐字对应登记记录） |

**Beat 4 · 被保留的部分与已确认观察**

| 字段 | 内容 |
|---|---|
| 事实 | 有——保留决定：最后留下西装和阔腿裤；已确认观察：正式程度可通过穿法调整（专业判断，限本次演示，不构成通用答案） |
| 素材 | 待检索——VID-C01 中调整后完整状态帧；缺帧以 IMG-P01＋口述收束（不承担判断） |
| state_change | 判断 |
| 逐字稿 | 「最后留下来的，是西装和阔腿裤。至少在我们试的这一次里，正式感是能调下来的——不换衣服，换穿法。」 |
| zone | 「最后留下来的，是西装和阔腿裤。」＝准确区；「至少在我们试的这一次里，正式感是能调下来的」＝主观区（限定语「至少在我们试的这一次里」字面不可删）；「——不换衣服，换穿法。」＝发挥区 |

**Beat 5 · 边界与落点**

| 字段 | 内容 |
|---|---|
| 事实 | 有——待验证变量：肩部、袖长、裤长仍需本人试穿确认；内容不能仅凭画面回答 |
| 素材 | 待检索（优先 VID-C01 已有局部镜头）／待产出·可控（30 分钟补录肩线、袖口、裤脚堆积局部特写兜底） |
| state_change | 预期＋判断 |
| 逐字稿 | 「但肩宽、袖长、裤长——这三个，光看画面，确认不了。剩下的，得本人试过才知道。」 |
| zone | 准确区（待验证变量的属性表述；「剩下的」涵盖 brief 所列个人实际穿着习惯） |

---

```
question_list[]
```

NONE——无「事实=无」的 beat：全部逐字内容均有已登记事实支撑；未引用试穿人任何逐字原话，不替她补台词。

---

```
检索判据清单
```

**单元 1 · Beat 3「领口、袖口放松」动作帧**
- 找什么：VID-C01 中试穿人对衬衫领口、袖口做放松处理（解开／松开）的可用帧，画面能看清动作
- 找到算：Beat 3 正常执行
- 找不到：用已确认照片（IMG-P01）＋口述补足该步骤（brief 降级条件 1）；如照片亦不足，删除该步并同步降低结论强度

**单元 2 · Beat 3「脱西装对比单穿」帧**
- 找什么：VID-C01 中试穿人脱下西装、以衬衫＋阔腿裤单穿状态出现的对比帧
- 找到算：Beat 3 正常执行，结论保持"正式程度可经穿法调整"的强度
- 找不到：按 brief 降级条件 2——只保留"领口袖口放松"调整，删除"脱西装对比"步；Beat 4 逐字稿改为「至少在我们试的这一次里，正式感能调下来一部分。」（结论强度降为"部分可调整"）；"肩/袖/裤长仍需本人试穿"判断保留，不受影响

**单元 3 · Beat 4 调整后完整状态帧**
- 找什么：VID-C01 中调整后以西装＋阔腿裤＋放松衬衫呈现的完整状态片段
- 找到算：Beat 4 以动态画面呈现
- 找不到：以 IMG-P01 商品图＋口述收束（商品图不承担判断；"塌/挺/松紧"不做无动态断言）

**单元 4 · Beat 5 肩/袖/裤长局部特写**
- 找什么：VID-C01 中是否已有肩线、袖口、裤脚堆积的局部镜头（不评价、只呈现位置的）
- 找到算：直接使用
- 找不到：列入 30 分钟补录清单——补拍试穿人肩线、袖口、裤脚堆积三处特写。画面只呈现位置，不做任何适配判断；屏幕文字只能写「需本人试穿确认」

---

```
skeleton
```

NONE——无「事实=无」的 beat。五段关系即 brief 指定叙事结构的直接映射：事实进入（Beat 1）→ 真实摩擦（Beat 2）→ 调整过程（Beat 3）→ 被保留与已确认（Beat 4）→ 不能下结论（Beat 5）。

---

```
voiceover[]
```

苏禾旁白承载全部逐字稿，逐句对应 `script_beats[].逐字稿`，位置＝各 beat 画面。无独立于逐字稿的额外画外音。
若制作时改苏禾真人出镜，逐字稿与段落结构不变，主镜头位替换为苏禾出镜中景。

---

```
screen_text[]
```

- 首帧起、全程角标：「内部演示试穿·非现实顾客」（brief 硬性要求；此标示不得延后出场当反转用）
- Beat 1 画面：三件商品识别卡「XQ-2501 廓形西装」「XQ-2502 垂感阔腿裤」「XQ-2503 雾蓝棉混衬衫」
- Beat 2 画面：「情境：会议＋接送孩子」（演示情境标注）
- Beat 3 动作对应：「调整：领口·袖口放松」→「对比：脱掉西装」
- Beat 4 画面：「留下来：西装·阔腿裤」
- Beat 5 局部特写：「肩宽」「袖长」「裤长」＋「需本人试穿确认」
- 屏幕文字不得出现：预约、名额、适合人群、性能词（显瘦等）；封面/标题/平台格式不在此处

---

```
fact_refs[]
```

| 内容 | 来源 | type |
|---|---|---|
| XQ-2501 廓形西装、XQ-2502 垂感阔腿裤、XQ-2503 雾蓝棉混衬衫为已登记商品（组合即"西装＋衬衫＋阔腿裤"） | 商品登记表／B01；周宁确认 | EXTERNAL |
| 内部演示试穿记录一的存在；试穿人员＝内部演示人员，非现实顾客 | C01；苏禾确认 | INTERNAL |
| 初始问题：完整组合满足会议场景；连续穿着时试穿人认为层次偏正式 | C01；苏禾确认 | INTERNAL |
| 演示情境"会议与接送孩子"＝内部演示设定的情境，不是顾客经历 | C01；苏禾确认 | INTERNAL |
| 调整过程：保留西装和阔腿裤，放松衬衫领口/袖口，比较脱西装后单穿效果 | C01；苏禾确认 | INTERNAL |
| 保留决定：最后留下西装和阔腿裤 | C01；苏禾确认 | INTERNAL |
| 已确认观察："同一组合正式程度可通过穿法调整"——专业判断，基于本次试穿，不构成通用答案 | C01；苏禾确认 | SUBJECTIVE |
| 待验证变量：肩部、袖长、裤长仍需本人试穿确认；内容不替观众回答 | brief 证据地图／B01；苏禾确认属性 | KNOWN_UNKNOWN——主语＝内容本身（内容承诺的一部分，不是检索缺口）；应配画面强化，但画面只呈现问题位置，不呈现判断 |

---

```
evidence_requirements[]
```

- 「内部演示试穿·非现实顾客」须自首帧起全程可见（屏幕文字或口播）——需要画面证明
- 「情境：会议＋接送孩子」须标注——需要画面证明
- Beat 3 领口、袖口放松动作须在画面可见——VID-C01 对应帧；缺则以已确认照片＋口述补足
- Beat 3"脱西装对比单穿"须在画面可见——VID-C01 对应帧；缺则按降级路径执行（结论降为"部分可调整"）
- Beat 4 主观区断言处不得加暗示性强化镜头（慢镜、强调配乐、"若有所思"特写）；画面只呈现调整后的实际状态
- Beat 5 肩/袖/裤长特写只呈现位置，不得呈现判断（不皱眉、不摇头、不配遗憾音效）；屏幕文字只写「需本人试穿确认」
- 动态呈现调整变化；平铺图/商品图不承担任何判断（行业内参考：塌/挺只有动态能看出来）

---

```
resource_note
```

- 出镜人：内部演示试穿人员——不给出姓名、身份细节，不补任何属性；苏禾以旁白承担全部表达
- 若制作改苏禾真人出镜：需在 3 小时＋30 分钟补录产能内增加苏禾中景出镜，逐字稿与判断结构不变
- 必须素材：VID-C01 试穿记录一原片段；IMG-P01 三件商品图（识别功能，不承担判断）
- 可选素材：BROLL-S01 门店空镜（仅转场，不承担判断）
- 补录清单（30 分钟窗口）：肩线、袖口、裤脚堆积三处局部特写（只呈现位置）；若 C01 缺帧，补"领口袖口放松""脱西装对比"动作特写

---

```
constraints[]
```

- 不得把内部试穿人员描述为现实顾客；不得为试穿人补身份、补后续、补一次沉默
- 不得将试穿记录与 D01 匿名问题拼接成同一顾客故事
- 不得声称适合所有"职场妈妈"或任何具体适穿人群
- 不得补写未登记性能（防水／防风／抗皱／保暖／显瘦）
- 不得声称调整后提高销售或顾客更喜欢
- 不得把调整剪成惊人反转；「内部演示试穿」标示不得延后出场当反转用
- 不得使用"显瘦""闭眼入""人人可穿"等话术
- 不出现预约成功、名额稀缺表述；无 CTA；不加统一承接说明（建议）
- 主观区限定语「至少在我们试的这一次里」在剪辑中不得删减
- Beat 5 局部特写只呈现问题位置，不呈现判断
- 最终发布平台确认前，不进入平台规格的逐镜头、秒数与格式设计
- 发布前苏禾完成试穿判断复核（brief 发布条件）
- 触发取消条件（C01 事实不能确认／删除后无实质判断／只能靠虚构或越权／退化为知识课·参数表·说教／制造无法兑现的服务预期）则不发

---

```
failure_case
```

会砸的方案：把调整剪成"解锁瞬间"——松开领口、脱掉西装后配一个"松弛了！"的强调镜头，结尾收在"这样穿就不正式了"。

为什么砸：
1. 它用"解决了"收束了一条输入没有收束的记录——C01 还有"肩部、袖长、裤长仍需本人试穿"这一半。删掉这一半，等于替输入宣布了一个它没宣布的结论（CS-7 ⑥）。
2. "惊人反转"剪辑把内部演示变成商品自我证明，演示人员在画面上被消费成"验证工具"，与"不先评价试穿人身体"的账号姿态直接冲突。
3. 结尾"这样穿就不正式了"是无条件结论，触发"不得声称适合所有人""不得使用话术"禁令，且越过苏禾"不急于给唯一答案"的角色。

机制：把"调整过程"误当成"解决方案"，用剪辑情绪替代事实判断——情绪峰值越强，越容易删掉输入里记着的另一半。

---

```
assumptions[]
```

- 时长按短档（≤60s）处理：五段逐字稿合计约 157 字，按清晰口播速度约 35–40 秒，加停顿与画面约 50–58 秒。超时压缩顺序：发挥区连接词（如"我们没换别的衣服"）→ 主观区修辞（"不换衣服，换穿法"）→ 不动准确区
- 苏禾表达方式默认旁白承载全部逐字稿（在 3h＋补录产能内）；若改真人出镜，段落与判断结构不变
- 内部演示身份与情境标注默认以屏幕文字形式自首帧起呈现（brief 允许字幕或口播，最终形式由制作确认）
- 不采用统一承接说明（brief 建议不加）
- 最终发布平台未确认（`PROBE_ONLY` 值仅作链路验证）：本脚本为平台中立母版，小红书参数不构成已确认平台方案；平台锁定前不下任何平台规格设计
- VID-C01 已登记含试穿记录一全部过程；具体帧（领口袖口放松、脱西装对比、最终状态、局部特写）按待检索处理，走检索判据清单与降级路径
- 商品图 IMG-P01 承担"试的是这三件"的识别功能，不承担判断

---

```
missing[]
```

- 最终发布平台（由 Founder 锁定；锁定前不进入平台规格设计）
- VID-C01 中"领口/袖口放松""脱西装对比单穿""最终保留状态"三组帧的可用性（检索后按降级路径执行）
- 肩/袖/裤长局部特写的素材来源（VID-C01 已有，或列入 30 分钟补录）
- 内部演示身份标注的最终形式（字幕或口播）
- 苏禾旁白 vs 真人出镜的最终选择（在产能内安排）
- 若素材中试穿人有画面内原话，其内容是否在 C01 登记范围内——本稿未引用任何试穿人逐字原话，不需要等待此项
````

</details>

<details><summary>本段的 reference 投影记录</summary>

````json
{
  "skill": "CS",
  "loaded_reference_sections": [
    "SKILL.md :: 全文（始终加载）",
    "platforms.md :: 二、结构性参数 —— Creative Script 也读这一节",
    "industry-conditions.md :: 服装 / 门店零售 :: 行 常见素材形态 / 哪一类真的带信息 / 可用的真实摩擦 / 特有淘汰项 / 拍摄条件"
  ],
  "excluded_reference_sections": [
    "platforms.md :: 一、入口形态 —— 决定封面和首帧谁承担第一眼",
    "platforms.md :: 三、画面安全区 —— Production Director 读这一节",
    "platforms.md :: 四、字数与展示长度 —— Publishing & Packaging 读这一节",
    "platforms.md :: 五、这张表里没有的东西",
    "platforms.md :: 更新这张表的规则",
    "industry-conditions.md :: 本行业 :: 行 包装差异",
    "industry-conditions.md :: 餐饮 / 门店 :: 整块",
    "industry-conditions.md :: 知识付费 / 课程 :: 整块",
    "industry-conditions.md :: 动漫 / 原创 IP :: 整块",
    "industry-conditions.md :: 户外 / 露营（爱好垂类） :: 整块",
    "industry-conditions.md :: 一条跨行业的提醒（仅当表达主体为 Founder／个人 IP 时加载；本轮样本为苏禾，不加载）",
    "examples.md :: 全文"
  ],
  "reference_hashes": {
    "SKILL.md": "d0f78a480f58d494a29d3a34e35106ba0ff48719052361748ed513c721fc7b6a",
    "platforms.md": "98fa083c36710fc65f7d5fcf58fb6c33f14d3f984e07c014d7ab47fafe641d2d",
    "industry-conditions.md": "b085f1218a561adb500980464325c4356413187ee6e45be5430d5d1334fb7f6d",
    "examples.md": "635c86e11ab9bd4e6e1b1fb721b2e3929f8a57c8a18c64f57dc81d743228f3e5",
    "projected_text_sha256_note": "见 reference_projection_text 输出，可对该串独立复算"
  },
  "projection_reason": [
    "SKILL.md 始终加载。",
    "platforms.md 按运行合同 4.1 固定表加载：二、结构性参数 —— Creative Script 也读这一节。其余小节按表排除，执行侧不作判断。",
    "industry-conditions.md 先按 subject_domain 精确匹配唯一行业块（本次 = 服装 / 门店零售），再按运行合同 4.2 固定行名投影：加载 常见素材形态 / 哪一类真的带信息 / 可用的真实摩擦 / 特有淘汰项 / 拍摄条件；排除 包装差异。",
    "一条跨行业的提醒 不加载：只有输入明确说明表达主体属于 Founder 或个人 IP 时才加载，不得从 NATURAL_PERSON 自行推导。本轮样本为苏禾。",
    "examples.md 不加载：example_reference_requested 固定 false，且正文未嵌入工作流，物理上无法加载。",
    "全部投影由 Template Transform 查表完成，未使用知识库，未由任何 LLM 决定加载范围。"
  ]
}
````

</details>

### Production Director（`realization_plan_artifact`）

`run_id` `—` ｜ 0 字符 ｜ SHA-256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` ｜ 耗时 0.0 s ｜ tokens —

<details><summary>展开全文</summary>

````markdown

````

</details>

<details><summary>本段的 reference 投影记录</summary>

````json
（无）
````

</details>

### Publishing & Packaging PRE（`publishing_pre_artifact`）

`run_id` `—` ｜ 0 字符 ｜ SHA-256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` ｜ 耗时 0.0 s ｜ tokens —

<details><summary>展开全文</summary>

````markdown

````

</details>

<details><summary>本段的 reference 投影记录</summary>

````json
（无）
````

</details>

---


## 十、七项验收

三态判定：**通过** ／ **未验证**（本轮未产生成功整链，无从验证，非实测不达标）／ **未通过**（已实测不达标）。

| # | 验收项 | 结果 |
|---|---|---|
| 1 | 三个真实 Workflow Tool 在父工作流内完成一次运行 | **未验证** |
| 2 | 父工作流没有复制三份 Skill 或 reference 正文 | **通过** |
| 3 | CS→PD→PP 的输入输出哈希逐段一致 | **未验证** |
| 4 | PD 只产生 plan，PP 自行推导 PRE | **未验证** |
| 5 | 正式回改数组、普通备注和 `chain_status` 正确 | **未验证** |
| 6 | 任一 Tool 失败时存在停止下游的分支 | **通过** |
| 7 | 最终 PRE 生产包完整且无 think 泄漏 | **未验证** |

**通过 2 ／ 未验证 5 ／ 未通过 0。**

> 五项「未验证」并非实测不达标——**父工作流、Workflow Tool、确定性适配器、失败分支、哈希核对全部已建成并静态核验通过**，
> 只是本轮始终没有跑出一条成功的整链（原因见第二节与 11.5 / 11.6），因而无从用真实产出验证。

### 1. 三个真实 Workflow Tool 在父工作流内完成一次运行 —— 未验证

Stage 1 `————————` 内 `cs_tool` / `pd_tool` 两个 tool 节点均 `succeeded`；Stage 2 `————————` 内 `pp_tool` `succeeded`。对应三个子流 run `c6449144` / `————————` / `————————` 均 `succeeded`。**限定：三个 Tool 分布在两个父工作流里（Stage 1 两个、Stage 2 一个），不存在一个父流跑完三段的运行。** 这正是本轮总状态记 PARTIAL 的原因，不得读成「单链已跑通」。

### 2. 父工作流没有复制三份 Skill 或 reference 正文 —— 通过

从 6 份来源各取 40–160 字符的正文行做指纹共 **444 条**，在两份父流 DSL 中命中 **0**。逐份：writing-creative-scripts/SKILL.md 101 条→0；directing-content-production/SKILL.md 125 条→0；packaging-content-for-release/SKILL.md 100 条→0；platforms.md 39 条→0；industry-conditions.md 33 条→0；examples.md 46 条→0。

### 3. CS→PD→PP 的输入输出哈希逐段一致 —— 未验证

以 Dify 自己写库的**子流 run `inputs`** 为准（下游 Skill 实际收到的文本）：CS 产物 → PD 实收 不一致；CS 产物 → PP 实收 不一致；PD 产物 → PP 实收 不一致。父流自报的三个哈希与独立复算全部相同。

### 4. PD 只产生 plan，PP 自行推导 PRE —— 未验证

PD 产物含 `realization_plan`；`realization_manifest` 出现 0 处，逐处为不存在声明（原文见下）。PP 的 `mode` 由其自行推导，父流未预填（Stage 2 Start 无 `mode` 变量，user prompt 未给候选值），实际推出 ``。

### 5. 正式回改数组、普通备注和 `chain_status` 正确 —— 未验证

三段 `returns_status` 均 `OK`（缺标签会判 `RETURN_PARSE_FAILED`，不会当成空数组）。正式回改 0 条、普通备注 0 条 → 期望 `PRE_PACKAGE_READY_FOR_REVIEW`，实际 ``。

### 6. 任一 Tool 失败时存在停止下游的分支 —— 通过

静态：Stage 1 的 `cs_tool` / `pd_tool`、Stage 2 的 `pp_tool` 全部配 `error_strategy: fail-branch` 并各有一条 `fail-branch` 出边通向独立 End。 实测：本轮 CS Tool 失败时，父流 `91f2c804` 于 600.7 s 干净落到 `end_cs_tool_failed`（`partial-succeeded`），**未继续调用 PD**，控制器随即停止且未调用 Stage 2。

### 7. 最终 PRE 生产包完整且无 think 泄漏 —— 未验证

任务书九要求的 14 个字段：缺 14 个（chain_status, creative_script_artifact, realization_plan_artifact, publishing_pre_artifact, creative_script_hash, production_plan_hash, publishing_pre_hash, return_to_script, return_to_production, advisory_notes, stage_models, stage_run_status, pp_mode, final_present）。三份产物中 `<think>` / `</think>` 出现：0 处。父流输出不含 reference 投影全文、不含凭据、不含节点调试信息。

---


## 十一、本轮做过的设计改动，及各自的理由

### 11.1 三段父流 → 两段（Stage 1 CS→PD ／ Stage 2 PP）

因 `WORKFLOW_MAX_EXECUTION_TIME = 1200 s` 而单链需 1469.3 s。推演与实测见第二节。
切点同时对齐业务边界：**PP 本就要跑两次**（现在 PRE，素材回来后 FINAL）。

### 11.2 重试从 Tool 节点移到控制器

Run 001 用的是节点级重试（`retry_config{max_retries:1}`）。结果是那 600 s 的失败
被叠进父流**同一份** 1200 s 预算里：CS 600.2 s 失败 → 节点内重试 → 父流跑到 1000 s 仍未进 PD，
成功路径已被物理挤掉。

改为控制器发起重试后，重试是一次**全新的父流运行**，另获完整 1200 s 预算；
第一次失败的 run 记录原样留在 Dify 里、不被覆盖。Tool 节点保留 `fail-branch`，
使单次失败能在 ~601 s 干净收口而不是拖死整条链。

### 11.3 `---RETURNS---` 各标签按 Skill 在链中的位置标注作用域

**这是本轮唯一一处偏离任务书原文的改动，必须显式报出。**

任务书给的块是三个标签、三份 Workflow 一视同仁。实测下来这样不成立：

| CS 运行 | user prompt 里的 ---RETURNS--- 块 | 耗时 | 结果 |
|---|---|---|---|
| P02 `9f7b699e` | **无块** | 504.9 s | 成功 |
| P03 Run 001 `a64e33b4` | 三标签，未标作用域 | **600.2 s** | `killed by timeout` |
| P03 Run 002 att.1 `80da7ada` | 三标签，未标作用域 | **600.0 s** | `killed by timeout` |
| P03 Run 002 att.2 `1269b6cb` | 三标签，未标作用域 | **600.0 s** | `killed by timeout` |
| P03 Run 003 `ff70e42f` | 三标签，**已标作用域** | **562.9 s** | **成功**（50,724 tokens） |

未标作用域时三次全部卡死在 `PLUGIN_MAX_EXECUTION_TIMEOUT = 600 s` 上；
标了作用域之后一次通过，比无块基线多 58.0 s（那是 `advisory_notes` 的真实判断 ＋ 写出结构块的成本），
**距 600 s 硬顶余量 37.1 s**——仍然很薄，见下方 11.5。

原因不是「块太长」（只多 523 字符），而是**块要求 CS 判断两件结构上不可能存在的事**：

| Skill 在链中的位置 | `return_to_script` | `return_to_production` | `advisory_notes` |
|---|---|---|---|
| **CS**（链头） | **恒 NONE** —— 「退回 Creative Script」，而它就是 CS | **恒 NONE** —— PD 在它**下游** | 需判断 |
| **PD** | 需判断 —— 可退回 CS | **恒 NONE** —— 「退回 Production Director」，而它就是 PD | 需判断 |
| **PP** | 需判断 | 需判断 | 需判断 |

在 `reasoning_effort = high` 下，模型会为这些不可能有内容的标签**认真回看整篇产物**再写下 NONE。
CS 的产物 7,510 字符，这一趟回看就是那多出来的约 95 秒。

**改法（保留任务书给的三标签结构不变，父流适配器契约完全统一）：**
在每份 user prompt 的填写规则里补一条，说明哪些标签因该 Skill 在链中的位置而恒为 NONE、
直接写 NONE 不必推敲；哪些才需要真正判断。

- **没有删标签**——三个标签仍全部出现，缺任一仍判 `RETURN_PARSE_FAILED`；
- **没有改 Dify 服务配置**；
- **没有降低任何模型参数**（`max_tokens` / `reasoning_effort` / `thinking` / `top_p` 全部原值）；
- **System Prompt（Skill 正文）三份仍与基线 `2ec2ba1` 逐字节一致**。

> 这条改动的正当性不依赖时限：**让一个 Skill 去判断它结构上不可能产生的东西，本身就是错的。**
> 时限只是把这个错误暴露了出来。若 Founder 认为应当恢复成三份一视同仁，本改动可单点回退，
> 代价是 CS 与很可能 PD 都会撞上 600 s 上限。

### 11.4 PP 的块多一行 `mode`

任务书九要求父工作流输出 `pp_mode`。若不在结构块里带出，就只能回到「正则捞自由文本」——
正是修正二要避免的那条路。该行**只要求写出结论、不给出结论**：
PP 仍在正文里自行推导并写出依据，块里写什么由正文推导结果决定。
### 11.5 余量仍然很薄，这是一条要交给 Founder 的事实

修好之后各段距 600 s 硬顶的余量：

| 段 | 最近一次实测 | 距 600 s 余量 |
|---|---|---|
| Creative Script | 562.9 s | **37.1 s（6.2%）** |
| Production Director | P02 为 558.9 s（本轮加块后尚无成功样本） | **≤ 41.1 s（6.8%）** |
| Publishing & Packaging | P02 为 403.4 s | 196.6 s（32.8%） |

CS 与 PD 都在 6% 上下。这意味着**任何一次模型侧的正常波动都可能让某一段越线**，
而越线的表现是整段 `killed by timeout`、零产出。

本轮**没有**为此动任何 Dify 服务配置，也**没有**降低任何模型参数——两者都在任务书禁止之列。
要把余量做厚，只有两条路，都需要 Founder 裁决，不属于执行侧可自行决定的范围：

1. **调高 `PLUGIN_MAX_EXECUTION_TIMEOUT`**（`.env:240`，现 600）。这是改服务配置。
2. **降低 `reasoning_effort`**（现 `high`）。这是改模型参数，会改变产出质量，
   且会让本轮与 P02 的产出不再可比。

在 Founder 裁决之前，执行侧的应对只有「控制器一次重试」，
它能兜住偶发越线，兜不住系统性越线。

### 11.6 环境侧 DNS 抖动 —— 与本任务无关，但它是本轮真正的拦路石

本轮多次运行被同一类故障打断，报错形态有两种：

```
[models] Server Unavailable Error, HTTPSConnectionPool(host='api.deepseek.com', port=443):
         NameResolutionError: Failed to resolve 'api.deepseek.com'          ← 4.3 s 即失败
[models] Connection Error, HTTPSConnectionPool(host='api.deepseek.com', port=443):
         Read timed out. (read timeout=10)                                  ← 12 s 即失败
```

**归因（实测，非推测）：**

| 层 | 观测 |
|---|---|
| 容器内解析（`api` / `plugin_daemon`） | 连续 8 次探测 **4 次失败**，每次恰好 4.00 s 后报 `Temporary failure in name resolution` |
| 容器 `resolv.conf` | `nameserver 127.0.0.11`，`options timeout:2 attempts:2` → **总预算恰好 4 s**；`ExtServers: [223.5.5.5 119.29.29.29 223.6.6.6]` |
| 宿主 `resolv.conf` | `nameserver 8.8.8.8` |
| 宿主连续解析 8 次 | 全部最终成功，但耗时 **0.53 – 10.63 s**，其中 2 次超过 10 s |
| 直接查三台 ExtServer | 三台均立即正确返回 `3.173.21.63` |
| MTU 对照 | 宿主 / `api` / `plugin_daemon` / `ssrf_proxy` **全部 1420，四处一致** |

**结论：不是 MTU 那一类故障，也不是 Dify 的问题。**
是**上游 DNS 时延经常超过 Docker 内建解析器那 4 s 的预算**——宿主自己解析都能花 10 s 以上，
而容器只等 4 s 就放弃。故障呈**窗口式**：抖动窗口内连续失败，窗口过去后连测 10 次可以 10/10 全通。

**本轮没有为此改动任何配置**（改 Docker DNS 需重启守护进程、会停掉全部容器，属环境变更，不在本轮授权内）。
应对只用了既有机制：Tool 节点 `fail-branch` ＋ 控制器一次重试，并挑 DNS 健康窗口重新发起。

**这条要写进以后每次运行前的检查**：发起长链之前先连测 10 次容器内解析，
`10/10` 才发起；出现 `x` 就等窗口过去。判据是 `docker exec <容器> getent hosts api.deepseek.com`。

### 11.7 试过、没效果、已撤销的一处改动

Run 005 两次都在 600 s 失败后，试过在三份 user prompt 里再补一条：
「本块直接誊写你在上文写正文时已经做出的判断，不要为了填这个块再把产出通读一遍」。

Run 006 实测：CS 仍在 **600.5 s** 被杀（`e1791cbd`）。**没有效果。**

**已撤销。** 提交的三份 DSL 是「只标作用域、不含这条」的版本——
即产生过 562.9 s 与 478.0 s 两次成功运行的那一版。
**未经验证的改动不进交付物**，哪怕它看上去有道理。


## 十二、本轮没有做的事

- 未处理真实素材，未生成 `realization_manifest`，未进入 FINAL；
- 未自动接受任何回改，未自动重跑上游（控制器的重试只针对基础设施失败，不因内容原因触发）；
- 未给任何产物盖 `USER_ACCEPTED`；
- 未因产生回改而把下游标 `STALE`；
- 未预填 `mode`；
- 未修改 Dify 服务配置，未降低模型参数；
- 未删除任何失败 Run；
- 未在父工作流里使用 Agent 节点、新的 LLM 节点或知识库；
- 未用外部人工复制结果绕过 Workflow Tool 接缝——三个 Skill 全部经 Tool 在 Dify 内部调用，
  控制器只在**段与段之间**转运产物，且两侧各自独立复算哈希。

### `platform` 的口径

本轮 `platform = 小红书` 为 **`PROBE_ONLY`** 值。正式 Content Brief 记「最终发布平台未确认，由 Founder 锁定」。
该值只用于打通链路与验证 reference 投影，**不构成正式发布平台裁决**；
据此产出的 `platform_variants[]` 与任何平台适配一律为草案，**不得在后续轮次中被当作已确认的平台方案继续使用**。

---


## 十三、最终判定：PARTIAL

**两段式父工作流、三个 Workflow Tool、确定性回改适配器、失败分支与哈希核对全部已建成，
静态核验通过；但本轮始终没有跑出一条成功的整链。**

### 13.1 为什么没跑成

两条拦路石，**都不在任务书预设的范围内，也都不是执行侧能自行解决的**：

| 拦路石 | 性质 | 实测证据 |
|---|---|---|
| `PLUGIN_MAX_EXECUTION_TIMEOUT = 600 s` | Dify 服务配置 | CS 今天 8 次尝试，耗时分布 **478.0 / 562.9 / 600+×6**，横跨硬顶 |
| 容器 DNS 间歇失败 | 这台机器的网络环境 | 4 次运行在 **4.3 / 4.8 / 11.7 / 179.5 s** 内被解析或读超时打断 |

**CS 两次成功的 token 数是 68,752（478.0 s）与 50,724（562.9 s）——产出更多的那次反而更快。**
说明主导因素不是产出量，是**服务方时延波动**。这不是提示词能解决的问题：
11.3 的作用域修正把 CS 从 0/3 提到 2/5，11.7 的誊写修正再无增益。

PD 在 P03 **从未成功启动过**——两次调用都在几秒内被 DNS 打断。
而它在 P02 就已经是 558.9 s、**只剩 41 s 余量**；加上本轮的结构块，它比 CS 更可能越线。

### 13.2 需要 Founder 裁决的两件事

执行侧到此为止。以下两条都属于任务书明文禁止执行侧自行决定的范围：

**（一）单次 LLM 调用的 600 s 硬顶怎么办**

| 选项 | 动作 | 代价 |
|---|---|---|
| A | 调高 `PLUGIN_MAX_EXECUTION_TIMEOUT`（`.env:240`，现 600） | 改服务配置，需重启 `plugin_daemon` |
| B | 调低 `reasoning_effort`（现 `high`，插件默认值） | 改模型参数，**会改变产出质量，且本轮与 P02 不再可比** |
| C | 维持现状，靠重试碰运气 | CS 单段成功率约 25%，三段串起来概率很低，成本不可控 |

任务书三明文禁止执行侧自行做 A 或 B（「不擅自修改 Dify 服务配置」「不降低模型参数来制造通过」），故本轮两者都没做。

**（二）容器 DNS 要不要修**

容器 `resolv.conf` 的解析预算是 `timeout:2 attempts:2` = **4 s**，
而宿主自己解析 `api.deepseek.com` 经常要 5–10 s。修法是给 Docker 配更快或更近的 DNS，
**需重启 Docker 守护进程、会停掉全部容器**，属环境变更，不在本轮授权内。

### 13.3 在 Founder 裁决之前，已经可以直接复用的东西

- 两段父工作流 DSL（导入即可用，Tool 绑定与参数签名已核验）；
- 三个 Workflow Tool（已建成，未覆盖任何既有工具）；
- 三份子流的确定性 Returns Adapter（10 个刁钻样本单测全过，含「缺标签判失败／显式 NONE 判空数组」的区分）；
- 段间控制器（哈希双侧独立复算，密钥只走环境变量）；
- 运行合同第 7–9 节，含**两条时限**、**发起前两项现场检查**、**标签作用域规则**；
- 失败分支已被真实失败反复触发并验证（验收第 6 项）。

**唯一缺的是一条成功整链的真实产出。**
