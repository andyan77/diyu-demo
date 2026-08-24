# 内容生产运行合同 v0.1

适用：内容生产链三份 Skill v0.6（基线提交 `2ec2ba1`）的真实运行。
本文件只定三件事：九个输入槽位、人工回改、plan 与 manifest。

---

## 4.1 九个输入槽位

### 槽位定义与缺失处置

| 槽位 | 主要提供方 | 缺失时 |
|---|---|---|
| `production_profile` | Production Profile | 询问 |
| `expression_subject` | Content Brief／账号责任 | 询问 |
| `content_origin_mode` | Production Profile | 询问，不默认现拍 |
| `subject_domain` | 品牌事实／Content Brief | 无法确定才询问 |
| `duration_band` | Content Brief／制作要求 | 询问 |
| `platform` | 用户本轮选择 | 询问，不自行选择 |
| `cta_contract` | Campaign／Content Brief | 缺失时不生成 CTA |
| `account_positioning` | Matrix／Content Brief | 询问 |
| `constraints[]` | Brief ＋ 品牌事实 ＋ Production Profile | 合并；阻塞项询问 |

### 实际覆盖表

核查对象：仓库现有正式 Content Brief
`decision-chain/evidence/CONTENT_BRIEF_DEEPSEEK_V4_FLASH_RUN_001_FINAL.md`
第 2 节第一份独立 Brief `BRF-SUHE-001`（苏禾｜真实使用验证）。

| 槽位 | 实际来源字段 | 状态 |
|---|---|---|
| `production_profile` | 无对应字段。`制作要求` 只给「一次 3 小时集中拍摄＋30 分钟补录」；`0. 运行结论 · 人员产能条件` 只给逐人工时。**均未给班底规模**（单人手机／1–2 人／小团队／商业制作） | `RUNTIME_REQUIRED` |
| `expression_subject` | `出镜人与事实确认人`：「出镜人为内部演示试穿人员，明确不是现实顾客；苏禾作为账号持续表达者可以出镜说明或旁白解释」→ 映射到五类中的 `NATURAL_PERSON` | `DETERMINISTIC_DERIVATION` |
| `content_origin_mode` | `必须使用的素材`：「VID-C01 中试穿记录一原始片段」（已有素材）＋ `制作要求`：「一次 3 小时集中拍摄＋30 分钟补录」（现拍）→ 按 CS-6 混合来源规则填多值：**现拍 ＋ 已有素材剪辑** | `DETERMINISTIC_DERIVATION` |
| `subject_domain` | `适用 Campaign`：序里集「初秋通勤衣橱」第一阶段；证据地图全部为商品事实、试穿记录与陈列 → 对应 `industry-conditions.md` 的「服装 / 门店零售」 | `DETERMINISTIC_DERIVATION` |
| `duration_band` | `制作要求` 明写「最终发布平台未确认前，**不进入平台规格的逐镜头、秒数与格式设计**」——秒数被显式推迟，Brief 不承载该值 | `RUNTIME_REQUIRED` |
| `platform` | `0. 运行结论 · 当前未成立条件`：「最终发布平台未确认」；`发布条件`：「最终发布平台由 Founder 锁定」 | `RUNTIME_REQUIRED` |
| `cta_contract` | `CTA 或无 CTA 的决定`：「本条无 CTA……更推荐本条不加」——是明确的「无 CTA」裁决，不是缺失 | `DIRECT` |
| `account_positioning` | `账号与本轮责任`：「苏禾，独立参战账号，零售搭配负责人；本轮负责……」＋ `账号关系姿态` | `DIRECT` |
| `constraints[]` | `明确不得表达`（10 条）＋ `发布条件` ＋ `降级条件` ＋ `取消或不发条件` ＋ `事实、观察、专业判断与待验证变量的区分` | `DIRECT` |

状态取值只使用：`DIRECT` / `DETERMINISTIC_DERIVATION` / `RUNTIME_REQUIRED` / `NOT_APPLICABLE` / `MISSING_BLOCKING`。

本次核查结果：`DIRECT` 3 项、`DETERMINISTIC_DERIVATION` 3 项、`RUNTIME_REQUIRED` 3 项、
`NOT_APPLICABLE` 0 项、`MISSING_BLOCKING` 0 项。

### 第一次真实生产运行的硬要求

九项必须**各有明确值或显式 `NOT_APPLICABLE`**。

不允许依靠隐藏默认值伪装完成。三份 Skill 自身带的默认值（如 Creative Script 输入表里的
「默认单人手机」「默认现拍」「默认短档」「默认平台中立母版」）在**工作流无人可问**时才允许使用，
且必须写进输出的 `assumptions[]`。生产运行不得把这些默认值当成上游已确认输入。

上表三项 `RUNTIME_REQUIRED`（`production_profile` / `duration_band` / `platform`）
在真实生产运行开始前必须由人给出。其中 `platform` 不得由任何 Skill 或工作流自行选择。

---

## 4.2 人工回改

### 下游可能发回什么

Production Director 可能输出：

```text
return_to_script[]
```

Publishing & Packaging 可能输出：

```text
return_to_script[]
return_to_production[]
```

**第一版只汇总建议，不自动回环。** 系统不得因为收到建议就重跑任何一段。

### 人的四个选项

- 全部拒绝；
- 接受部分；
- 全部接受；
- 暂停。

### 接受之后发生什么

接受 `return_to_script[]` 后：Creative Script 重新运行。

接受 `return_to_production[]`（且未接受 `return_to_script[]`）后：Production Director 重新运行。

### STALE 的触发点

**STALE 的触发点是「上游重跑后实际改了内容」，不是「人接受了建议」。**

依据：v0.6 的 Creative Script 输入表里，`return_from_downstream[]` 的处置写明
「**收到时必须逐条回应：接受并改写、或说明为什么不改。不得沉默**」——
也就是说，Creative Script 重跑后完全可能逐条回应「不改」，并给出理由。
这时下游产物仍然有效。若按「人接受建议」就置 STALE，会把两段仍然有效的产物白白作废。

因此：

| 上游重跑后的实际结果 | 下游产物状态 |
|---|---|
| Creative Script 改写了脚本内容 | 原 Production Director 与 Publishing & Packaging 产物转 `STALE` |
| Creative Script 逐条回应「不改」，脚本内容未变 | 下游产物**不转** `STALE`，保持原状态 |
| Production Director 改写了 `realization_plan` 或 `capture_plan` | 原 Publishing & Packaging 产物转 `STALE` |
| Production Director 回应「不改」，产物内容未变 | Publishing & Packaging 产物**不转** `STALE` |

「实际改了内容」以重跑前后产物正文的哈希比对为准，不以模型自述为准。
哈希相同即判定未改；哈希不同即判定已改。

### 被接受的建议写到哪里

写入：

```text
return_from_downstream[]
```

每条至少包含：

| 字段 | 内容 |
|---|---|
| `source_skill` | 建议来自哪一段（Production Director／Publishing & Packaging） |
| `target_location` | 要改的具体位置（哪一个 beat、哪一句） |
| `requested_change` | 要求改成什么 |
| `reason` | 为什么要改 |

### 重跑的发起

**每一次重跑必须再次由人发起。** 系统不得自动连跑，不得因为上一次接受而预授权下一次。

---

## 4.3 plan 与 manifest

### 拍摄前

拍摄前只有：

```text
realization_plan
```

`realization_plan` 是计划，不是兑现记录。它不得被当作 manifest 使用，
也不得据此声称任何 beat 已被覆盖。

### 素材回来之后

由 Production Director 按 beat 对位生成：

```text
realization_manifest
```

固定字段：

| 字段 | 内容 |
|---|---|
| `beat_id` | 脚本段落 ID |
| `covered_by_units[]` | 覆盖该 beat 的素材单元 |
| `asset_locator` | 时间码、图片序号或文件位置 |
| `fact_visual_support` | 有／没有／有，但不够 |
| `uncovered_part` | 未兑现部分 |
| `resolution` | 补拍／降级／删除／保留未完成 |

### 什么不是 manifest

**「拍了 42 分钟」「有 36 张图」不是 manifest。**

素材总量、素材清单、拍摄日志都不是 manifest。manifest 的最小单位是 **beat**：
没有逐 beat 的对位关系，就没有 manifest。

### 模式判断

| 条件 | 模式 |
|---|---|
| 全部 beat 都有对位覆盖 | `FINAL` |
| 部分 beat 有对位覆盖 | `MIXED` |
| 没有 beat 级 manifest | `PRE` |

Publishing & Packaging 在 `PRE` 模式下不得声称已验证 `realized_payoff`，
不得伪造 `realization_manifest`，不得把 PRE 包装写成正式成片已经完成。

---

## 5. reference 固定投影表

本节对应任务 `CONTENT-PRODUCTION-RUNTIME-P02` 第四节的 4.1／4.2／4.3。
因本文件第 4 节已占用 4.1—4.3 编号（九槽位／人工回改／plan 与 manifest），此处顺延为第 5 节，内容一致。

**这张表是确定性的。执行侧按表查，不作判断，不得自行扩大或缩小范围。**

### 5.1 platforms.md

| Skill | 固定加载 |
|---|---|
| Creative Script | 第二节「结构性参数」 |
| Production Director | 第三节「画面安全区」 |
| Publishing & Packaging | 第一节「入口形态」＋第四节「字数与展示长度」＋第五节「表里没有什么」 |

v0.6 的 `platforms.md` 小节标题本身即写明归属（「—— Creative Script 也读这一节」「—— Production Director 读这一节」
「—— Publishing & Packaging 读这一节」），本表与原文一致。未列出的小节一律排除。

### 5.2 industry-conditions.md

先按 `subject_domain` **精确字符串匹配**选出唯一行业块，未匹配则不加载任何行业段落，
**不得选择「最相近行业」**。选中行业块后，再按固定行名投影：

| 行名 | CS | PD | PP |
|---|---|---|---|
| 常见素材形态 | 加载 | 加载 | 排除 |
| 哪一类真的带信息 | 加载 | 加载 | 加载 |
| 可用的真实摩擦 | 加载 | 排除 | 排除 |
| 特有淘汰项 | 加载 | 加载 | 加载 |
| 拍摄条件 | 加载 | 加载 | 排除 |
| 包装差异 | 排除 | 排除 | 加载 |

**跨行业提醒**（`一条跨行业的提醒`）只有在输入**明确说明**表达主体属于 Founder 或个人 IP 时才加载。
**不得从 `expression_subject = NATURAL_PERSON` 自行推导**——自然人不等于 Founder 或个人 IP。

### 5.3 examples.md

三个 Workflow **默认均不加载**。只有显式输入 `example_reference_requested = true` 才允许加载。

### 5.4 投影必须可核验

每个 Workflow 的 Reference Projection 必须输出：
`loaded_reference_sections[]` / `excluded_reference_sections[]` / `reference_hashes{}` / `projection_reason[]`。

这些字段进运行证据，**不进入用户可见 Final**。

投影只能由确定性节点（Template Transform 或 If/Else）完成：
**不使用知识库，不由任何 LLM 决定加载范围。**
被排除的内容应当嵌在模板里再由查表排掉，使「排除」是真排除、可在后台逐字复核。

---

## 6. platform 的 PROBE_ONLY 口径

当 `platform` 取自 `PROBE_ONLY` 值（正式 Content Brief 记为 `RUNTIME_REQUIRED`、最终发布平台未确认、
由 Founder 锁定）时：

- 该值**只用于打通链路与验证 reference 投影**；
- **不构成正式发布平台裁决**；
- 据此产出的 `platform_variants[]` 与任何平台适配**一律为草案**，不得在后续轮次中被当作已确认的平台方案继续使用；
- 该口径必须写进运行证据，并随产物一起传递给下游。

---

## 7. 拍摄前生产链的串联形态

### 7.1 运行时限预检

本机实测值，来源逐项可复核，**不使用默认印象**：

| 时限项 | 实际值 | 来源 |
|---|---|---|
| Workflow 总执行时限 | **1200 s** | `.env` 未设置该项 → 走代码默认 `dify_config.WORKFLOW_MAX_EXECUTION_TIME`；api 与 worker 容器均无环境变量覆盖 |
| 超时判定方式 | **只在节点边界判定** | `graphon/graph_engine/layers/execution_limits.py`：仅在 `NodeRunSucceededEvent` / `NodeRunFailedEvent` 上检查，**不在节点执行中途中断** |
| Workflow Tool 单次调用时限 | **无独立时限**；子流经 `WorkflowAppGenerator.generate()` **进程内**调起，另获一份完整 1200 s 预算 | `core/tools/workflow_as_tool/tool.py` |
| **单次 LLM 调用时限** | **600 s，硬顶** —— 超时报 `PluginDaemonInternalServerError: killed by timeout` | `.env:240` `PLUGIN_MAX_EXECUTION_TIMEOUT=600`，compose 传给 `plugin_daemon`；Run 001 实测在 600.2 s 被杀，逐字复核 |
| Workflow Tool 调用本身是否经插件守护进程 | **否**（进程内）—— 但**子流内部的 LLM 节点经守护进程调模型，受上一行 600 s 约束** | `core/tools/workflow_as_tool/tool.py` |
| 调用深度上限 | `WORKFLOW_CALL_MAX_DEPTH = 5`（本链深度 1） | `dify_config` |
| 步数上限 | `WORKFLOW_MAX_EXECUTION_STEPS = 500`（本链 ≤ 12） | `dify_config` |
| 单变量大小上限 | `MAX_VARIABLE_SIZE = 204800`（最大产物 17,564 字符） | `dify_config` |
| API 请求时限 | `GUNICORN_TIMEOUT=360`，但 `SERVER_WORKER_CLASS=gevent` → 是 **worker 心跳超时**、不是请求超时 | `.env`；P02 已实证单次 505 s 请求成功 |
| 反向代理 | `NGINX_PROXY_READ_TIMEOUT` / `SEND_TIMEOUT` 均 `3600s` | `.env` |
| Worker（Celery） | blocking 模式的工作流运行不走 Celery | — |
| Code 节点 | `SANDBOX_WORKER_TIMEOUT=15`、`CODE_EXECUTION_READ_TIMEOUT=60`、`CODE_MAX_STRING_LENGTH=400000` | `.env` |

**任何修改 Dify 服务配置来放宽时限的做法，不在本合同授权范围内。**
**任何通过降低模型参数来压缩耗时以求「跑通」的做法，同样禁止。**

> **两条时限是并列的，不能只看一条：**
> 一条是 **1200 s 的工作流总时限**（决定一个父流能串几段），
> 另一条是 **600 s 的单次 LLM 调用硬顶**（决定单个 Skill 跑不跑得完）。
> 后者与分段方式无关——**再怎么拆父流，也拆不掉任何一次 LLM 调用头上的 600 s**。
>
> P02 三段的 LLM 节点实测 504.9 / 558.9 / 403.4 s，最紧的 PD **只剩 41 s 余量**，
> 当时没有被识别出来。P03 Run 001 的 CS 就撞上了这条线（600.2 s 被杀）。
> **这条约束必须写进每一次运行前的预检，不得再遗漏。**

### 7.2 为什么是两段，不是一条链

P02 三段实测墙钟：CS 505.7 s ＋ PD 559.6 s ＋ PP 403.9 s ＝ **1469.3 s**，超出 1200 s 上限。

因为超时只在节点边界判定，单链的实际结局是**最坏的一种**：

| 时点 | 事件 | 边界判定 |
|---|---|---|
| t ≈ 506 s | CS Tool 完成 | 506 < 1200，放行 |
| t ≈ 1066 s | PD Tool 完成 | 1066 < 1200，放行 |
| t ≈ 1470 s | PP Tool 完成 | **1470 > 1200 → abort** |

即：三段 token 全部烧完（P02 量级约 19 万），**汇总节点与 End 都不执行，产出为零**。
故不建设单链——建设一条明知跑不完的链，不是「尽力而为」，是把成本花在必然的失败上。

**两段式：**

| 段 | 内容 | 实测耗时 | 余量 |
|---|---|---|---|
| Stage 1 | CS → PD | 1065.4 s | 134.6 s（11.2%） |
| Stage 2 | PP（PRE） | 403.9 s | 796.1 s（66.3%） |

Stage 1 余量偏紧，须如实记录。两点缓解事实：

1. 即使 Stage 1 在 PD 完成后的边界被 abort，**两个子流各有独立预算、已各自跑完并落库**，
   产物与 run 记录不会丢失，可从 Dify 后台取回。
2. 因为单次 LLM 调用被 600 s 硬顶，Stage 1 的两段之和**在物理上就跨不过 1200 s 太多**
   （最坏 ≈ 600 ＋ 600）；真正的风险不是「慢慢超时」，而是**某一段单独撞上 600 s 被杀**。
   后者由 `fail-branch` 干净兜住，并由控制器发起一次全新运行重试。

切点同时对齐业务边界：**PP 本就要跑两次**——现在出 PRE，真实素材回来后出 FINAL。
把 PP 单独切出来不是为了凑时限，是这条链本来就该有的形状；父流少一段，失败处置也更简单。

### 7.3 两段的边界与各自输入

**Stage 1（CS → PD）Start 输入 13 项**：
`content_brief`、九槽位中的 `production_profile` / `expression_subject` / `content_origin_mode` /
`subject_domain` / `duration_band` / `platform` / `cta_contract` / `account_positioning` / `constraints[]`，
以及 `available_assets`、`fact_refs[]`、`example_reference_requested`。

**Stage 2（PP · PRE）Start 输入**，其中传给 PP Workflow Tool 的实际参数为 11 项：

| 参数 | 来源 | 缺了会怎样 |
|---|---|---|
| `cs_final` | Stage 1 产物，逐字 | 无上游 |
| `pd_final` | Stage 1 产物，逐字 | 无上游 |
| `content_brief` | 原始输入 | 无事实源 |
| `platform` | 原始输入（本轮 `PROBE_ONLY`） | 无入口形态判断 |
| `cta_contract` | 原始输入 | 无承接契约 |
| `account_positioning` | 原始输入 | 无账号口径 |
| **`subject_domain`** | 原始输入 | **Reference Projection 选不出行业块，投影节点空跑**（见 5.2：PP 需加载 industry-conditions 三行） |
| **`duration_band`** | 原始输入 | **PP-1 的候选取向只能反推**，并被迫在 `assumptions[]` 挂一条本不必要的假设 |
| `constraints[]` | 原始输入 | 禁令失效 |
| `fact_refs[]` | 原始输入 | 无事实锚点 |
| `example_reference_requested` | 固定 `false` | — |

> **`subject_domain` 与 `duration_band` 是 PP 的硬输入，不是可选项。**
> 这一条在 P02 已经裁定并落进 PP 的独立 Workflow（Start 变量与 user prompt 均含此二项）；
> P03 任务书 7.3 的清单是**文档侧回退**，运行侧未回退。
> 现已把它们焊进 `diyu_content_publishing_packaging` Workflow Tool 的**参数签名**——
> 少传即工具调用失败，不再依赖文档约定。

### 7.4 段间转运纪律

段间由确定性控制器搬运（`tools/content_production_pre_chain_controller.py`），规则：

- Stage 1 的 `creative_script_artifact` / `realization_plan_artifact` **逐字**进 Stage 2，不摘录、不重排、不改写；
- 数组以 JSON 编码原样转运；
- 控制器**独立复算** SHA-256 与 Stage 1 自报哈希比对，不一致即 `INPUT_BLOCKED`，不进 Stage 2；
- Stage 2 的 Input Check **再次独立复算**一遍，两侧都过才调用 PP Tool；
- 三份 Skill 一律经 Workflow Tool 在 Dify 内部调用，**控制器不接触 Skill 正文，也不在段间人工搬运模型输出**。

### 7.5 失败处置

| 情况 | 分支 | 输出 |
|---|---|---|
| 输入缺失／上游哈希不符 | `gate_input` false 分支 | `INPUT_BLOCKED` ＋ `missing_inputs[]`，**不调用任何 Tool** |
| Tool 调用失败 | 该 Tool 的 `fail-branch` | `TOOL_FAILED` ＋ `failed_stage`，**不调用下游**，已产生的上游产物保留在输出中 |
| 回改块解析失败 | 该段的 `gate_*` false 分支 | `RETURN_PARSE_FAILED`，**不调用下游**，产物保留 |

每个 Tool 节点配 `error_strategy: fail-branch`，但**不配节点级重试**（`retry_enabled: false`）。

**重试放在控制器层，不放在 Tool 节点上。** 理由是实测出来的，不是偏好：

节点级重试会把那 600 s 的失败**叠进父流同一份 1200 s 预算里**。
Run 001 即如此——CS 600.2 s 失败 → 节点内重试 → 父流跑到 1000 s 仍未进 PD，
成功路径已被物理挤掉。改由控制器重发后，重试是一次**全新的父流运行**，
另获完整 1200 s 预算，且第一次失败的 run 记录原样留在 Dify 里、不被覆盖。

控制器只重试一次，且**只针对基础设施失败**；
**不因内容原因重跑，也不因产生回改而重跑。**

**任一失败分支都不得输出「生产包已完成」。**

### 7.6 每次发起长链之前的两项现场检查

两项都过才发起。任一不过就等，不要硬发——发出去也是烧 token 换一个已知的失败。

**（一）容器内 DNS 是否处于健康窗口**

```
docker exec docker-plugin_daemon-1 sh -c \
  'for i in $(seq 1 10); do getent hosts api.deepseek.com >/dev/null 2>&1 \
   && echo -n O || echo -n x; done; echo'
```

要求 **`OOOOOOOOOO`（10/10）**。出现 `x` 就是抖动窗口，等过去再发。

本机实测过的故障形态：容器 `resolv.conf` 是 `nameserver 127.0.0.11` ＋
`options timeout:2 attempts:2`（**总预算恰好 4 s**），而宿主自己解析 `api.deepseek.com`
经常要 5–10 s。上游一慢，容器 4 s 就放弃，模型调用侧报
`NameResolutionError: Failed to resolve` 或 `Read timed out`，**几秒内就失败**。

**这不是 MTU 那一类故障**——宿主与各容器 MTU 实测均为 1420、四处一致。
区分判据：**几秒内失败且报解析／读超时 = DNS；600 s 整被杀 = 插件时限。**

**（二）上一轮各段耗时距 600 s 还剩多少**

`600 − 最近一次实测耗时`。低于 60 s 就要预期这一段随时会越线，
并在发起前想清楚越线之后怎么办（当前应对只有控制器那一次重试）。

---

## 8. 回改的结构化出口

### 8.1 不建解析器，改输出结构

v0.6 三份 Skill 输出的是 **Markdown 正文**，不是结构化数据。Skill 里写的是
「要输出 `return_to_script[]` 这个字段」，**没有规定它怎么序列化**。

若照原样上解析器，只有两条路，且都不可接受：

1. **正则捞自由文本**——模型换一种写法就 `RETURN_PARSE_FAILED`；
2. **执行侧偷偷上第二个 LLM 解析**——明令禁止。

因此采取第三条：**不加解析器，改输出结构**。

在三个 Workflow 的 **user prompt 末尾**追加一条格式要求。
**System Prompt 中的 Skill 正文一字不动**（三份的 System Prompt 相对基线 `2ec2ba1` 逐字节一致，可复核），
故这不构成修改 Skill。

### 8.2 `---RETURNS---` 块

```
---RETURNS---
mode: <仅 Publishing & Packaging 有此行；写该 Skill 自行推导出的值本身>
return_to_script: <逐条列出，每条独占一行以 `- ` 开头；无则写 NONE>
return_to_production: <同上>
advisory_notes: <同上>
```

- `---RETURNS---` 只出现一次，排在全部产出之后；解析取**最后一次**出现，防正文引用干扰。
- 标签必须全部出现、各占一行、顺序不变；**即使内容为 NONE 也不得省略标签行**。
- 本块之后不再输出任何内容。

`mode` 这一行**只要求写出结论，不给出结论**。PP 仍须在正文里自行推导并写出依据；
本块不得改变正文推导出的结果。推导出 PRE 以外的值，照实写，**不得被任何一侧掰成 PRE**。

### 8.2.1 标签作用域：每个 Skill 只判断指向它上游的那些标签

三个标签在三份 Workflow 里**全部出现、格式统一**（缺任一仍判 `RETURN_PARSE_FAILED`），
但**哪些需要真正判断，取决于该 Skill 在链中的位置**：

| Skill | `return_to_script` | `return_to_production` | `advisory_notes` |
|---|---|---|---|
| **Creative Script**（链头） | **恒 `NONE`** —— 「退回 Creative Script」，而它就是 CS | **恒 `NONE`** —— PD 在它**下游** | 需判断 |
| **Production Director** | 需判断 —— 可退回 CS | **恒 `NONE`** —— 「退回 Production Director」，而它就是 PD | 需判断 |
| **Publishing & Packaging** | 需判断 | 需判断 | 需判断 |

恒为 `NONE` 的标签，user prompt 里必须**明写「直接写 NONE，不要为这一项回看正文」**。

**这不是省事，是纠错。** 让一个 Skill 去判断它结构上不可能产生的东西，本身就是错的。
而且代价是实打实的：在 `reasoning_effort = high` 下，模型会为这些不可能的标签认真回看整篇产物再写下 `NONE`。

实测：CS 的产物 7,510 字符，为两个不可能的标签回看一趟约多花 95 s，
直接把 CS 从 P02 的 504.9 s 推过 **600 s 的单次 LLM 调用硬顶**——
三次运行（`a64e33b4` / `80da7ada` / `1269b6cb`）全部 `killed by timeout`。
PD 在 P02 为 558.9 s、仅余 41 s，加同样负担同样越线。

**任何为某个 Skill 新增输出要求之前，先确认它在链中的位置能不能产生这个东西。**

### 8.3 适配器：纯字符串切分

每个 Workflow 在 Final Extract 之后接一个 **Returns Adapter（Code 节点）**，
只做字符串切分与标签查找，**无判断、无第二个 LLM**：

| 情形 | 判定 | 理由 |
|---|---|---|
| 找不到 `---RETURNS---` | `RETURN_PARSE_FAILED` | 结构缺失 |
| 找到块，但缺任一必需标签 | `RETURN_PARSE_FAILED` | **解析失败不得当成空数组** |
| PP 的 `mode` 行在但取不出值 | `RETURN_PARSE_FAILED` | 同上 |
| 标签在，值为 `NONE` / `无` | **`OK` ＋ 空数组** | 显式声明「没有」是成功解析，不是失败 |

> 「**缺标签**」与「**显式写 NONE**」必须区分：前者是解析失败，后者是空数组。
> 二者混为一谈，等于把「没读到」伪装成「确实没有」。

适配器同时把 `---RETURNS---` 之前的正文切出来作为 `final_output`（产物）——
**下游收到的、以及被哈希的，都是这段正文**，不含结构块。

### 8.4 正式回改与普通备注不得互换

- `return_to_script[]` / `return_to_production[]` **只放正式回改项**：必须由上游改动才能解决的问题；
- 可选的、仅供参考的、不改也能交付的，一律进 `advisory_notes[]`；
- 汇总节点**只搬运不升格**，也不降格；条目按来源打标（`[creative_script]` / `[production_director]` / `[publishing_packaging]`）。

本轮到人工评审出口为止：**不自动接受回改、不自动重跑上游、不给任何产物盖 `USER_ACCEPTED`、
不因产生回改而立即把下游标 `STALE`。**
`STALE` 仍只在「上游重跑后正文哈希实际变化」时触发（见 4.2）。

---

## 9. chain_status

| 取值 | 条件 |
|---|---|
| `PRE_PACKAGE_READY_FOR_REVIEW` | 正式回改数组全空，且 `advisory_notes[]` 也为空，**且 PP 推导出的 mode 为 `PRE`** |
| `MIXED_PACKAGE_READY_FOR_REVIEW` | 同上，但 mode 为 `MIXED` |
| `FINAL_PACKAGE_READY_FOR_REVIEW` | 同上，但 mode 为 `FINAL` |
| 以上三个 ＋ ` (N advisory)` | 正式回改数组全空，但有 N 条普通备注 |
| `USER_DELIVERY_BLOCKED_FACT_CHECK` | **完整 Artifact 产出成功，但用户交付块未通过事实检查** |
| `USER_DELIVERY_MANUAL_FACT_REVIEW_REQUIRED` | **语义事实核验这一环自己没给出可用结论**——不声称自动核验通过，改由人逐句复核后交付 |
| `HUMAN_REVIEW_REQUIRED (N return)` | 有 N 条正式回改，无普通备注 |
| `HUMAN_REVIEW_REQUIRED (N return, M advisory)` | 有 N 条正式回改与 M 条普通备注 |
| `TOOL_FAILED` | 任一 Workflow Tool 调用失败 |
| `INPUT_BLOCKED` | 输入缺失，或上游产物与哈希核对不通过 |
| `RETURN_PARSE_FAILED` | 回改块解析失败 |

**前三个状态由 PP 自行推导出的 mode 决定**，不由调用方指定。
`PRE_PACKAGE_READY_FOR_REVIEW` 的字面值与本节登记之前完全一致，
已按该值登记过的历史运行不受影响。

### `USER_DELIVERY_BLOCKED_FACT_CHECK`

**它挡的是「产出成功」和「可以交付」之间的那一步。**
完整 Artifact 跑出来了、mode 也推对了，不等于那份用户交付块可以交到执行人手上。

触发条件（确定性检查，任一命中即阻断）：

| 检查 | 命中什么 |
|---|---|
| 事实编号 | `used_fact_refs[]` 里出现简写、自造编号、或 `fact_refs[]` 中不存在的编号 |
| 假绿 | 产出声称某句「已删除／已剔除」，但那句话仍出现在用户交付块里 |
| 内部过程语言 | 用户交付块出现「已删除」「审查发现」「修正后」「原方案」「上一版」「未核实，不得使用」等 |
| CTA 越界 | `cta_contract` 为无 CTA，而用户交付块出现奖励、领取、关注、私信、购买或预约引导 |
| 语义事实核验 | 独立模型逐句判定：交付块里被当成**已经发生过的事**来说的内容，在 `fact_refs[]` 里找不到支持（否定句暗含的前提同样算） |

**被阻断时**：完整 Artifact、`used_fact_refs[]`、失败的用户交付块与全部运行证据
**继续原样保存**，一个字都不删 —— 它们是判断问题出在哪儿的依据。

**被阻断时不得做的事**：不得把已知含错误的用户交付块当作正式交付；
不得人工删掉问题句之后，把同一次运行改判为通过。**要通过就重新跑一次。**

> **为什么单独设这个状态**：模型会在自检里写「已删除」「已核实」。
> 那是自述，不是证据。这个状态的存在，就是为了让「它说它处理好了」和
> 「确实处理好了」这两件事不再混为一谈 —— 判定只看用户交付块的实际文本。

**计数是必需的，不是装饰。** `advisory_notes[]` 非空却只报
`PRE_PACKAGE_READY_FOR_REVIEW`，字面意思是「可以评审了」，
而备注里其实有实质内容要看——状态名会让人以为没事了。计数把这件事摆到状态行上。

### 语义事实核验节点

前四道是确定性检查：查编号写法、查「说删了却还在」、查内部过程词、查 CTA 越界。
它们能挡住**格式型**和**自述型**的问题，挡不住**语义型编造**——
一句话挂着真实存在的编号、用词也干净，内容却是编的。
P05R2 那句「不是我们从十几次试穿里挑出来的」就是这样溜过去的：
四道闸和两个扫描器全部放行，最后是人逐句读出来的。

所以在 PP 之后加一个**只读**的核验节点：

| 它是什么 | 它不是什么 |
|---|---|
| PP 跑完之后才读用户交付块的独立判断 | 不参与内容生成，不影响 PP 怎么写 |
| 换一个模型来判（qwen3.8-max），只为拿一个独立意见 | 不改变 DeepSeek 作为内容生产主模型的口径 |
| 只回答「这句有没有依据」 | 不评分、不评价创意、不改写、不提优化方案、不重跑 PP |
| 只会让判定更严 | 永远不能把前四道闸已经判 BLOCKED 的翻回通过 |

**它只拿得到四样东西**：用户交付块、10 条完整 `fact_refs[]`、`cta_contract`、`realized_payoff`。
拿不到 PP 的自检结论，也拿不到 `used_fact_refs[]` 的「已核实／已删除」自述——
**那是模型说自己做过什么，不是证据**。

**判 BLOCK 时**：状态转 `USER_DELIVERY_BLOCKED_FACT_CHECK`，
完整 Artifact 与原用户交付块原样保留，不生成正式用户交付包，不自动重跑 PP。

**它自己失败时**（模型没返回、返回不是约定的 JSON、或 verdict 与条目自相矛盾）：
不阻断内部产物保存，状态转 `USER_DELIVERY_MANUAL_FACT_REVIEW_REQUIRED`，
改为人工事实复核后交付。**这种情况下不得声称自动事实核验通过。**

### 用户可见输出的边界

父工作流最终输出**不得包含**：`<think>` 内容、内部 reference 投影全文、
任何凭据、Dify 节点调试信息。

reference 投影的**记录**（`loaded_reference_sections[]` 等）按 5.4 进运行证据，
不进父工作流的用户可见输出。
