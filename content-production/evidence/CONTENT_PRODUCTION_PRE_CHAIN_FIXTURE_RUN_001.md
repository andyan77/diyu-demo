# 最小事实夹具 · 内容生产两段链运行记录 · `FIXTURE_RUN_001`

任务：`CONTENT-PRODUCTION-RUNTIME-P03R1`　｜　夹具：`CP-RUNTIME-FIXTURE-001`

---

## 一、最终状态

| 项 | 值 |
|---|---|
| 最终状态 | **BLOCKED** |
| 分支 | `` |
| 运行时 HEAD | `` |
| Stage 1（CS→PD） | **未成功** |
| Stage 2（PP PRE） | **未发起**（Stage 1 未成功，按第六节不调用下游） |
| `chain_status` | `TOOL_FAILED` |

结论：**基础设施阻塞**。按第八节，不再继续修改 Prompt，也不再缩小夹具。

失败点：**Creative Script 子流的单次 LLM 调用被 600 s 硬顶杀掉**（`PluginDaemonInternalServerError: killed by timeout`），两次均如此，产出 0 token。父流从输入校验到发起 Tool 调用为止全部正常，**接缝、传参、解析、拓扑都不是失败原因**——详见第十节。

---

## 二、基线与网络预检

### 2.1 基线核验（运行前）

| 项 | 结果 |
|---|---|
| 分支 | `feature/content-production-runtime-v1` |
| 起始 HEAD | `6f2fad1`（= 任务书预期） |
| 本地 vs 远端 | 一致 |
| 工作区 | 干净，0 项 |
| P03 两段父流文件 | `..._PRE_CHAIN_STAGE1_V0_1.yml` / `..._STAGE2_V0_1.yml` 均在 |
| 三个 Workflow Tool | `diyu_content_creative_script` / `diyu_content_production_director` / `diyu_content_publishing_packaging` 均在，绑定应用 `13ba9e70` / `4433b747` / `fa71a06d` |
| 三个 V1 旧 Tool | `diyu_v1_matrix_architect` / `diyu_v1_campaign_orchestrator` / `diyu_v1_content_brief_architect` 未被覆盖 |
| 三份 Skill 相对 `2ec2ba1` | **零改动**（`git diff --stat` 输出 0 字节） |
| references 相对 `2ec2ba1` | **零改动**（`git diff --stat` 输出 0 字节） |

另核验 Dify 线上子流与仓库 DSL 是否同一份（上一轮曾回退过一处 prompt 改动）：

| 子流 | System Prompt | User Prompt |
|---|---|---|
| Creative Script | 一致，13813 字 | 一致，1674 字 |
| Production Director | 一致，15285 字 | 一致，1773 字 |
| Publishing Packaging | 一致，12558 字 | 一致，1761 字 |

逐字节 SHA-256 比对，线上 == 仓库。上一轮回退的「直接誊写」改动确实未留在 Dify 上。

### 2.2 网络预检

范围：只做只读探测，未修改 Docker、DNS 或任何服务配置。

| 检查 | 方法 | 结果 | 判定 |
|---|---|---|---|
| provider 域名解析（plugin_daemon 容器内） | `docker exec docker-plugin_daemon-1 getent hosts api.deepseek.com ×10` | OOOOOOOXOO —— 10 次中 9 次解析成功，1 次失败 | 通过（存在间歇失败，已记录） |
| DeepSeek provider HTTPS 可达（plugin_daemon 容器内，不消耗模型） | `curl --max-time 20 https://api.deepseek.com/ ×3` | 401 total=2.57s ／ 000 total=20.00s（连接阶段挂住）／ 401 total=6.37s | 通过（401=服务端已应答，鉴权在实际调用时注入；3 次中 1 次连接挂住，已记录） |
| api → plugin_daemon | `docker exec docker-api-1 curl http://plugin_daemon:5002/health/check` | HTTP 200，0.0024s | 通过 |
| worker → api | `docker exec docker-worker-1 curl http://api:5001/health` | HTTP 200，0.0029s | 通过 |
| worker → redis / db_postgres / plugin_daemon（TCP） | `socket.create_connection 逐个连接` | redis:6379 OK；db_postgres:5432 OK；plugin_daemon:5002 OK | 通过 |
| 容器全部在线 | `docker ps` | api / worker / worker_beat / plugin_daemon / nginx / redis / db_postgres / sandbox 等 15 个容器均 Up，api、db_postgres、sandbox 报 healthy | 通过 |

**总判定**：预检通过 —— provider 可解析可达、服务间连通正常。网络存在间歇不稳定（DNS 1/10 失败、HTTPS 1/3 连接挂住），按第六节按基础设施失败重试一次处理，不修改任何配置。

容器解析器配置（`plugin_daemon`）：`nameserver 127.0.0.11；options timeout:2 attempts:2 single-request-reopen ndots:0；ExtServers [223.5.5.5 119.29.29.29 223.6.6.6]`

> 容器解析器总预算 2s×2=4s。上游 ExtServers 本轮为 223.5.5.5 等（与 P03 记录的 8.8.8.8 不同，宿主 resolv.conf 已变）。间歇失败与该 4s 预算相关，属环境层面，本轮按任务书要求未做任何修改。

更正一处探测口径：首次探测 worker→postgres 时用了主机名 db，报 Name or service not known；实际 compose 服务名为 db_postgres，改用正确主机名后连接正常。此为探测命令用错主机名，不是故障。

---

## 三、运行记录

### 3.1 应用与工具

| 角色 | 名称 | app_id | 说明 |
|---|---|---|---|
| Stage 1 父流 | DIYU Demo Content Production PRE Chain v0.1 · Stage 1 | `4eac6ab7-9d81-4af0-accf-740e3157f5ea` | CS → PD |
| Stage 2 父流 | DIYU Demo Content Production PRE Chain v0.1 · Stage 2 | `2c188608-0559-4ef4-8c76-18b4f48c3cd9` | PP（PRE） |
| Workflow Tool | `diyu_content_creative_script`（DIYU Creative Script） | tool `c9af3cc2` → app `13ba9e70` | 子流经 Tool 在 Dify 内部调用 |
| Workflow Tool | `diyu_content_production_director`（DIYU Production Director） | tool `34998db2` → app `4433b747` | 子流经 Tool 在 Dify 内部调用 |
| Workflow Tool | `diyu_content_publishing_packaging`（DIYU Publishing Packaging） | tool `154a3dd0` → app `fa71a06d` | 子流经 Tool 在 Dify 内部调用 |

### 3.2 本轮 Run 清单

| Run ID | 应用 | 状态 | 耗时 s | tokens | 起始 | 错误 |
|---|---|---|---|---|---|---|
| `890e225e` | Content Production PRE Chain v0.1 · Stage 1 | `partial-succeeded` | 600.6 | 0 | 08-23 07:47:35 | — |
| `91cca7e7` | Creative Script v0.1 | `failed` | 600.2 | 0 | 08-23 07:47:35 | [deepseek] Error: req_id: 4dbdf0d505 PluginDaemonInternalServerError: killed by timeout |
| `e2a9f29e` | Content Production PRE Chain v0.1 · Stage 1 | `partial-succeeded` | 601.1 | 0 | 08-23 07:57:36 | — |
| `0fed78c6` | Creative Script v0.1 | `failed` | 600.7 | 0 | 08-23 07:57:36 | [deepseek] Error: req_id: ac4c161cbe PluginDaemonInternalServerError: killed by timeout |

完整 Run ID：

| 阶段 | 父流 Run ID |
|---|---|
| Stage 1 | `e2a9f29e-92fa-4143-b3f2-1ebe39c99fdf` |
| Stage 2 | `（未发起）` |

重试记录：Stage 1 发起 2 次，Stage 2 发起 0 次。
控制器只重发一次，且重发是一次全新父流运行；第一次失败的 Run 原样保留在 Dify 里，未删除、未覆盖。**不因内容结果不理想重试。**

> 关于 600 s 超时算不算「可重试」：任务书第六节列的可重试项是 DNS／连接中断／provider 临时不可用，并未单列 600 s；但同节紧接着写「**如果再次发生：…单次 LLM 超过 600 秒…停止运行并报告 BLOCKED，不继续堆叠重试**」——「再次发生」意味着第一次 600 s 是走了那一次允许的重试的。本轮即按这个读法执行：第 1 次 600 s → 重发一次；第 2 次仍 600 s → 立即停止，报 BLOCKED，未调用 Stage 2。

### 3.3 节点轨迹

**Stage 1**（父流 `e2a9f29e`）

| # | 节点 | 类型 | 状态 | 耗时 s |
|---|---|---|---|---|
| 1 | 输入 | `start` | `succeeded` | 0.0 |
| 2 | Input Check | `code` | `succeeded` | 0.1 |
| 3 | 输入闸 | `if-else` | `succeeded` | 0.0 |
| 4 | Creative Script Tool | `tool` | `exception` | 600.9 |
| 5 | CS Tool 失败标记 | `code` | `succeeded` | 0.1 |
| 6 | CS Tool 失败结束 | `end` | `succeeded` | 0.0 |

**三个子流（经 Workflow Tool 在 Dify 内部调用）**

| Run ID | 子流 | 状态 | 耗时 s | tokens |
|---|---|---|---|---|
| `91cca7e7` | Creative Script v0.1 | `failed` | 600.2 | 0 |
| `0fed78c6` | Creative Script v0.1 | `failed` | 600.7 | 0 |

> 三段模型调用全部发生在**子流内部**，父流只有 Tool 节点与确定性 Code 节点。控制器不接触 Skill 正文，段间也没有任何人工搬运模型输出。

---

## 四、三段产物与哈希

### 4.1 三段正文哈希

| 段 | 长度（字符） | SHA-256 |
|---|---|---|
| Creative Script Final | — | **本轮未产出** |
| Production Director realization_plan | — | **本轮未产出** |
| Publishing & Packaging PRE | — | **本轮未产出** |

### 4.2 逐段一致性核对

哈希在三个互相独立的地方各算一次，三处对得上才算这一段传递无损：

| 口径 | 谁算的 | 算的是什么 |
|---|---|---|
| 父流侧 | Stage 1／Stage 2 的 Code 节点 | 绑定到下游 Tool 的那段文本 |
| **子流实收侧（权威）** | 从 Dify `workflow_runs.inputs` 取下游子流**实际收到**的入参再算 | 下游真正读到的文本 |
| 控制器侧 | 控制器拿到 Stage 1 输出后独立复算 | 段间搬运是否逐字无损 |

| 接缝 | 上游自报哈希 | 下游实收正文哈希 | 判定 |
|---|---|---|---|
| CS Final → PD 实收 `creative_script` | — | — | 该段本轮未运行，无产物可哈希 |
| CS Final → PP 实收 `cs_final` | — | — | 该段本轮未运行，无产物可哈希 |
| PD plan → PP 实收 `pd_final` | — | — | 该段本轮未运行，无产物可哈希 |

控制器侧独立复算：

| 段 | Stage 1 自报 | 控制器复算 | 判定 |
|---|---|---|---|
| — | — | — | Stage 1 未成功，控制器未进入复算 |

---

## 五、PD plan、PP PRE 与回改结果

### 5.1 PD 只生成 plan，未生成 manifest

Stage 1 未成功，PD 未产出，**无从核对**。

### 5.2 PP 自行推导 mode

Stage 2 未运行，PP 未推导 mode。**不填任何值，也不推测。**

### 5.3 回改汇总与 `chain_status`

| 数组 | 条数 |
|---|---|
| `return_to_script[]` | **未产生**（无成功子流，不是「0 条回改」） |
| `return_to_production[]` | **未产生**（无成功子流，不是「0 条回改」） |
| `advisory_notes[]` | **未产生**（无成功子流，不是「0 条回改」） |

`chain_status` = `TOOL_FAILED`

### 5.4 Returns Adapter 解析状态（确定性，无第二个 LLM）

| 子流 | `returns_status` | 说明 |
|---|---|---|
| Creative Script | — | 本轮无成功运行 |
| Production Director | — | 本轮无成功运行 |
| Publishing Packaging | — | 本轮无成功运行 |

解析器是纯字符串切分：以最后一个 `---RETURNS---` 标记切开正文与结构块，再按固定标签逐行取值。缺标记或缺标签一律返回 `RETURN_PARSE_FAILED`，**绝不把解析失败写成空数组**；标签写了 `NONE` 才是空数组。

---

## 六、六项验收

判定三态：**通过** ／ **未验证** ／ **未通过**。「未验证」指本轮没有可测的成功运行，**不等于测了不达标**。

| # | 验收项 | 判定 | 依据 |
|---|---|---|---|
| 1 | Stage 1 成功完成 CS→PD | **未通过** | Stage 1 父流 `e2a9f29e`，状态 `partial-succeeded` |
| 2 | Stage 2 成功完成 PP | **未验证** | Stage 1 未成功，按第六节未调用下游，本项无从验证 |
| 3 | CS→PD→PP 文本哈希逐段一致 | **未验证** | 三段接缝全部未运行，无产物可哈希，无从核对（**不等于核对不通过**） |
| 4 | PD 只生成 plan，PP 正确推导 PRE | **未验证** | PD 与 PP 本轮均未运行，无产物可判 |
| 5 | Returns 与 advisory 能确定性解析和汇总 | **未验证** | 本轮无成功子流，无从验证 |
| 6 | 产物无 think 泄漏，未把 FIXTURE_FACT 写成真实经营事实 | **未验证** | 本轮无产物，无从验证 |

**合计：通过 0 ／ 未验证 5 ／ 未通过 1。**

---

## 七、本轮输入

夹具：`content-production/fixtures/CONTENT_PRODUCTION_MINIMAL_CHAIN_FIXTURE_v0.1.md`，`fixture_id = CP-RUNTIME-FIXTURE-001`，全部事实标 `FIXTURE_FACT`。

| 槽位 | 长度 | 值（长文本只列摘要） |
|---|---|---|
| `content_brief` | 1083 | # 内容简报 · CP-RUNTIME-FIXTURE-001（测试夹具）  **本简报全部事实为 `FIXTURE_FACT`（测… |
| `production_profile` | 49 | SOLO_MOBILE；苏禾一人；一部手机；门店内拍摄；60 分钟拍摄；基础剪辑；不新增其他出镜者 |
| `expression_subject` | 19 | NATURAL_PERSON / 苏禾 |
| `content_origin_mode` | 2 | 现拍 |
| `subject_domain` | 9 | 服装 / 门店零售 |
| `duration_band` | 8 | 短档，≤60 秒 |
| `platform` | 35 | 小红书（TEST_ONLY：只用于工作流测试，不构成正式发布平台裁决） |
| `cta_contract` | 5 | 无 CTA |
| `account_positioning` | 59 | 陪伴试穿和比较，不做无条件推荐。用内部试穿和搭配调整，帮助顾客判断一件衣服怎样进入真实生活场景；不替顾客宣布统一答案。 |
| `constraints` | 99 | 1. 不把内部试穿人员包装成顾客； 2. 不从成分推导保暖、垂感或其他性能； 3. 不使用“必买”“闭眼入”； 4. 不声称这套组合… |
| `available_assets` | 22 | 无已确认成片素材；本轮全部属于待产出·可控。 |
| `fact_refs` | 229 | FIXTURE_INTERNAL｜夹具 CP-RUNTIME-FIXTURE-001 第 3 节： - 商品结构三项（雾蓝棉混衬衫 … |
| `example_reference_requested` | 5 | false |

`content_brief` 正文 SHA-256：`4c2bd241d0df4834761bfcef9a6867fd71974974ac48264523465ecc638c26ae`，长度 1083 字符。

对照：P02／P03 用的完整 Brief 为 4749 字符。本轮夹具为其 23%。

缩小输入是本轮的核心手段，**结果是它没有起作用** —— 见第十节 10.2。

`platform` 为 `TEST_ONLY`：只用于工作流测试，**不构成正式发布平台裁决**；据此产出的平台适配与包装结果一律为草案。

---

## 八、三份产物全文

### 8.1 Creative Script Final

**本轮未产出。** 该段未运行，不填任何内容，也不以其他来源顶替。

### 8.2 Production Director realization_plan

**本轮未产出。** 该段未运行，不填任何内容，也不以其他来源顶替。

### 8.3 Publishing & Packaging PRE

**本轮未产出。** 该段未运行，不填任何内容，也不以其他来源顶替。

---

## 九、交付物与结论

### 9.1 本轮文件

| 文件 | 动作 |
|---|---|
| `content-production/fixtures/CONTENT_PRODUCTION_MINIMAL_CHAIN_FIXTURE_v0.1.md` | 新增 |
| `content-production/evidence/CONTENT_PRODUCTION_PRE_CHAIN_FIXTURE_RUN_001.md` | 新增（本文件） |

### 9.2 未改动的东西

| 项 | 状态 |
|---|---|
| 三份 Skill 正文 | 未改（相对 `2ec2ba1` 零改动） |
| references 三份 | 未改（相对 `2ec2ba1` 零改动） |
| 模型与参数 | 未改（`deepseek-v4-flash`，`reasoning_effort=high`，`thinking=true`，`max_tokens=384000`，`top_p=0.8`） |
| Dify 服务配置 | 未改（`WORKFLOW_MAX_EXECUTION_TIME` / `PLUGIN_MAX_EXECUTION_TIMEOUT` 均原值） |
| Docker / DNS | 未改 |
| 两段父流 DSL | 未改 |
| 控制器 | 未改 |
| Returns Adapter | 未改 |
| 验收条件 | 未降 |

任务书第九节允许「只有发现真实工作流缺陷时」才改父流 DSL／控制器／Adapter。本轮的失败点是平台的单次 LLM 调用时限，**不是工作流缺陷**，故三者一字未动。

### 9.3 结论

最终状态 **BLOCKED**，结论是**基础设施阻塞**。

按任务书第八节：**不再继续修改 Prompt，也不再缩小夹具。**

### 9.4 下一步判断

（见第十节）

## 十、本轮结论与下一步判断

### 10.1 本轮真正验证到哪一步

| 环节 | 结果 |
|---|---|
| 网络预检 | 通过 |
| 基线（分支／HEAD／工作区／Skill 零改动／线上==仓库） | 通过 |
| 夹具组装、13 槽位注入 Stage 1 | 通过 |
| 父流 `输入` → `Input Check` → `输入闸` | 通过 |
| `Creative Script Tool` 发起子流调用 | 通过 |
| 子流 `输入` → `Reference Projection` → `Projection Record` | 通过 |
| 子流 LLM 节点 | **失败：单次调用被 600 s 硬顶杀掉** |
| 其后所有环节（PD／PP／哈希链／Returns 汇总／PRE 推导） | **未运行，无从验证** |

失败点是精确的：不是接缝、不是传参、不是解析、不是父流拓扑，而是**单个模型调用本身跑不完 600 秒**。父流到 Tool 调用为止的部分全部正常。

### 10.2 本轮证伪了什么（这是本轮最有价值的产出）

P03R1 的假设是：**把夹具缩小，让单次 LLM 调用挤进 600 秒。这个假设被本轮证伪。**

同一个 Creative Script 子流、同一套 Skill、同一组模型参数，只换输入大小：

| `content_brief` 字符 | 运行次数 | 成功 | 600 s 被杀 | 网络类失败 | 人工停止 |
|---|---|---|---|---|---|
| 4749（P02／P03 完整 Brief） | 13 | 3 | 7 | 2 | 1 |
| 1083（本轮最小夹具，为完整的 23%） | 2 | 0 | 2 | 0 | 0 |

把输入砍到不到四分之一，**CS 依然跑满 600 秒、被同一个错误杀掉、产出 0 token**。

原因在成功运行的数据里看得很清楚 —— CS 的耗时跟输出量根本不成正比：

| 成功运行 | 耗时 s | tokens | 折合吞吐 tok/s |
|---|---|---|---|
| `9f7b699e` | 505.5 | 63284 | 125 |
| `ff70e42f` | 562.9 | 50724 | 90 |
| `c6449144` | 478.0 | 68752 | 144 |

产出最多的那次（68752 tokens）反而最快（478.0 s），产出最少的那次（50724 tokens）反而最慢（562.9 s）。
吞吐在 90–144 tok/s 之间摆动 —— 这是**服务端速度的随机波动**，不是输入量的函数。
CS 这一段的自然耗时分布正好横跨 600 秒这条线，所以每次运行都是掷硬币，**而输入大小既不影响这条线，也不影响这枚硬币**。

### 10.3 还剩哪些路

三条，**都超出执行侧权限**——任务书第一节明写不修改模型参数和 Dify 服务配置：

| 选项 | 做什么 | 代价 |
|---|---|---|
| A | 调高 `PLUGIN_MAX_EXECUTION_TIMEOUT`（`.env` 一行，重启 plugin_daemon） | 改服务配置；需 Founder 授权。已知 CS 三次成功落在 478–563 s；被杀的那几次产出 0 token，**它们本来要跑多久无从得知**，所以调多高才够，只能调完再测 |
| B | 调低 `reasoning_effort`（`high` → 更低）或关掉 `thinking` | 改模型参数；产出质量会变，**与 P02 的对照关系就断了**；需 Founder 授权 |
| C | 保持不动，反复重试碰运气 | 完整 Brief 下成功率约 30%（3/10），且**三段都要碰对才算跑通**，整链一次成功的概率是三段成功率相乘；成本不可控 |

按任务书第八节，**本轮到此为止：不再继续修改 Prompt，也不再缩小夹具。**

### 10.4 本轮没有做、也不该做的事

| 没做的事 | 为什么 |
|---|---|
| 没有再缩夹具重试 | 第八节明令 |
| 没有改 Skill／references／Prompt | 第一节、第九节明令；且本轮已证伪「改输入能解决」 |
| 没有降模型参数 | 第一节明令；这属于选项 B，要 Founder 裁决 |
| 没有改 Dify 服务配置、Docker、DNS | 第一节、第三节明令；这属于选项 A |
| 没有改父流 DSL／控制器／Returns Adapter | 第九节只在「发现真实工作流缺陷」时才允许，本轮的失败是平台时限，不是工作流缺陷 |
| 没有删除任何失败 Run | 第六节要求保留 |
| 没有把上一轮的产物拿来充当本轮结果 | 未运行的段一律写「本轮未产出」 |
