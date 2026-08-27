# 笛语 V1 · M3 v1.5.2 与 Founder 单组 Dify 验收 Execution Prompt v1.2

> `prompt_status`: `READY_FOR_EXACT_FOUNDER_AUTHORIZATION`  
> `planning_task_id`: `01a038f4-000b-7cd0-9dd2-d2dac022bf70`  
> `engineering_task_id`: `DIYU-V1-M3-ACCOUNT-CONTENT-OPERATOR-001`  
> `entry_mode`: `REBASE_TASK`  
> `engineering_execution_performed_by_planning_window`: `false`  
> `construction_authority_created_by_prompt`: `false`  
> `governance`: `RULESIDE-2026-08-25-005 / v0.3.1 revision 2`  
> `contract`: `M3_ENGINEERING_TASK_CONTRACT_v1.3_FOUNDER_SINGLE_SET_REBASE.yaml`  
> `contract_sha256`: `49021e601658194bc734285830d531352c19c1fa4416855c1f524efb073bff49`

---

## 0. 给执行窗口的直接指令

你继续的是同一个 M3 工程任务，不是新任务：

```text
task_id = DIYU-V1-M3-ACCOUNT-CONTENT-OPERATOR-001
entry_mode = REBASE_TASK
```

本次只完成四件事：

1. 在已冻结 v1.5.1 与历史证据上形成最终候选 v1.5.2；
2. 只做零模型确定性验证、Dify 最终候选部署与绑定；
3. 编制并冻结唯一一组七个 Founder Dify 测试输入；
4. 等 Founder 本人在 Dify 中每条运行一次后，记录其唯一 `PASS` 或 `FAIL`。

本 Prompt **不授权执行侧再调用任何模型**，不授权盲评、A/B、G1-A 补跑、多轮评测、主干合并或 M5。

只有 Founder 明确表示“授权执行此准确 Prompt 和合同哈希”后才可写入项目仓库或 Dify。没有准确授权时，只报告：

```text
M3_REBASE_EXECUTION
= AWAITING_EXACT_FOUNDER_AUTHORIZATION
```

## 1. 必须读取和核验的准确输入

### 1.1 规划侧唯一入口

```text
/mnt/c/Users/Administrator/Documents/Codex/Diyu-V1-Planning/
DIYU_V1_PLANNING_DELIVERY_BASELINE_v1.0.md

SHA-256
= aa5997c36e2bf17a565b972c858ec03a58fec6ecb6d9ae6b4845d62bf7a3d640
```

### 1.2 本轮后继合同

```text
M3_ENGINEERING_TASK_CONTRACT_v1.3_FOUNDER_SINGLE_SET_REBASE.yaml

SHA-256
= 49021e601658194bc734285830d531352c19c1fa4416855c1f524efb073bff49
```

旧合同 `M3_ENGINEERING_TASK_CONTRACT_v1.2.yaml` 保留历史身份，不再作为当前验收合同；不得覆盖或删除。

### 1.3 当前工程真源

真实项目仓库：

```text
/home/faye/diyu-demo
remote = https://github.com/andyan77/diyu-demo.git
```

任务 worktree 最近观察：

```text
/home/faye/diyu-demo-worktrees/m3-account-content-operator-v1
branch = task/m3-account-content-operator-v1
remote task head = 5e1b6ee9b8d3d5e2f144814f26dac906a2ceae93
remote main = a7b810109f43a4bf500acc285baab477d96796e3
```

以上 Git 值是本 Prompt 编译时的动态观察。启动时必须 `fetch` 并现场重核；如已变化，只对受影响项计算 `STALE`，不得从头重做或静默覆盖。

### 1.4 三份冻结工程报告

| 文件 | SHA-256 |
|---|---|
| `M3_STAGE2_V15_REPORT_AND_REBASE_v1.0.md` | `7c7bdf69a1100e6b88cb594733b2111bb0cd5e41dc8b4b2f7604b1ad63d3c296` |
| `M3_B09_5_HIGHEST_FAILING_NODE_v1.0.md` | `7ffa3ebfe2a3ddf06f47d30c775122e93abe6985dd6076e7c24a3472ee51f346` |
| `M3_REBIND_007_FROZEN_v1.0.md` | `04f3578c3ce9ddde3dcfc8fe327660c8bf3f25848612e56b48208f8c02a88c11` |

三份文件必须从任务分支读取。叙述与原始运行记录冲突时，以原始运行记录、节点记录、代码和哈希为准。

## 2. 重入时先报告

在任何写入前，先用自然语言报告：

- 实际 cwd、Git 根、分支、本地 HEAD、远端任务分支和远端 main；
- 实际加载的全局、规则根、项目与任务区 `AGENTS.md`；
- 原 `task_id` 和进入模式；
- 旧合同哈希与本轮合同哈希；
- 当前 Dify 任务 App、已发布候选和图版本；
- 可复用集合、`STALE` 集合、失败路径；
- 本轮执行侧模型调用预算为 `0`；
- 唯一下一动作。

报告后继续执行，不把无冲突的现场信息变成 Founder 问卷。

## 3. 本轮已经由 Founder 冻结的决定

执行侧不得再次请求 Founder 从甲乙丙中选择：

### 3.1 最终候选

```text
FINAL_CANDIDATE = v1.5.2
```

批准在 M3 `SKILL.md` 的“用户可见正文的硬要求”加入：

1. `审计块只能出现在正文之后；正文不存在时不许单独输出审计块。`
2. `审计块不加代码围栏，前后不加任何三个反引号标记。`

同时移除审计块模板外层的代码围栏，使模板与第二条硬规则一致。审计字段、顺序和产品语义不得改变；不得再添加一条 AC-09 同义提醒。

候选 v1.5.2 同时继承 `M3_REBIND_007_FROZEN_v1.0.md` 已冻结的 DD-5 修复。除必要的版本号、哈希和图绑定更新外，不扩大 Skill 或闸门变化面。

这两句能否降低 B09-5 失效率，目前仍是**推断**。不得在 Founder 亲测前写成已观察、已修复或 PASS。

### 3.2 G1-A

```text
G1-A_TRANSPORT_FAILURE_RERUN = CANCELLED
```

不补跑，不调用模型。保留失败记录和“本轮保真只有 8 组有效草稿”的准确表述。

### 3.3 验收方法

```text
BLIND_TEST = CANCELLED
BLIND_REVIEW = CANCELLED
MODULE_AB = CANCELLED
EXECUTOR_MODEL_CALLS = 0
FOUNDER_SINGLE_DIFY_SET = 7 INPUTS × 1 RUN
FINAL_PRODUCT_RESULT = PASS | FAIL
```

旧 AC-18 盲评路径保持历史 `NOT_VERIFIED`；本合同中为 `NOT_APPLICABLE`。不得宣称 M3 已证明优于一份好提示词。

## 4. 第一阶段：形成 v1.5.2，零模型完成技术闭合

### 4.1 写入边界

只在现有 M3 任务分支/worktree 和唯一任务 App 内写入。保护用户已有改动和未知文件，不得触及生产、其他 App、数据库、凭据、M1/M2/M4/M5 或 main。

把本 Prompt 与其合同作为不可改写的规划输入保存在任务分支根目录；若同名文件已存在，先逐字节核验，禁止覆盖不同内容。

### 4.2 Skill 与候选版本

完成以下最小变化：

1. 加入两句批准的输出形状硬规则；
2. 去掉审计块模板的代码围栏展示；
3. 保持审计字段和其余 Skill 正文不变；
4. 继承 DD-5；
5. 将候选、闸门、自报、Manifest、图版本和证据统一绑定为 v1.5.2；
6. 对实际变化做逐行 diff 和消融说明。

如果发现实现这两句必须改变产品语义、审计字段、M3职责或 Content Brief 合同，停止并报告精确冲突；不得自行扩大。

### 4.3 零模型验证

不得启动 Dify 模型节点。使用历史原始输入/草稿完成：

- v1.5.1 DD-5 全量确定性回放；
- v1.5.2 Skill/template 静态一致性检查；
- 审计块不得单独构成完整交付的结构检查；
- 旧 E07/E08 真拒不变性；
- B15-DIR-02 不再误拒；
- 新增误拒与确定性新漏检检查；
- 输入、模型草稿、闸门判断、最终结果各层分离；
- 凭据逐字节和通用形态扫描，输出中不得出现密钥内容。

历史69份模型草稿只能作为历史/诊断输入，不能冒充 v1.5.2 的产品运行证据。零模型回放只能证明确定性组件行为，不能证明两句 Skill 规则已经被模型执行。

### 4.4 部署与绑定

只部署到：

```text
App ID = b7fb5b1a-9278-426c-bb8a-f9f288639548
purpose = M3 task-specific candidate/test App
```

部署后零模型完成：

- 草稿图与已发布图读取；
- 节点、边、变量、系统提示词、参数和输出引用结构检查；
- 已发布系统提示词全文落盘并与 v1.5.2 Skill 派生文本逐字节比对；
- 浏览器渲染画布及 LLM 节点面板核验；
- App ID、版本、图哈希、Skill 哈希、Prompt 哈希、Git commit 绑定；
- 无 `http_request`、工具写入、生产对象、未知凭据或非任务 App 引用；
- 导出与恢复演练，不修改生产。

结构检查失败时，可以在本轮授权 Delta 内修复确定性实现并复验；若需要新模型调用或超出批准 Delta，则停止，不得另开评测轮。

## 5. 第二阶段：编制唯一 Founder Dify 测试组

### 5.1 七个场景冻结

只允许以下七个场景，每个只有一个主要验收目的：

| ID | 场景 | 主要观察 |
|---|---|---|
| S1 | 刚接手的账号，只有明确暂定锚点、没有正式定位 | 能否继续作有边界的周期判断，而不是强制先跑 Matrix 或退回要输入 |
| S2 | 同一账号同时存在 GMV、线索、到店三类有效路径；此前周期偏长期价值，本周期明确以到店为主要目标 | 是否保留长期基线、按到店组织本周期任务，并把 GMV、线索、到店分别处理而不是统称“转化” |
| S3 | 用户期望与基线均为 3 条/周，本周期真实产能降到 1 条/周 | 是否明确只保留一个主要任务、说清让掉什么收益，而不是把全部目标塞进一条 Brief |
| S4 | 没有任何外部市场资料，用户询问平台竞争位置 | 是否拒绝无证据的稀缺/唯一断言，同时仍完成全部不依赖市场证据的运营判断；不得零正文或只要求补输入 |
| S5 | 上一轮存在持续位，本轮收到来源和版本明确、但彼此冲突的反馈 | 是否形成解释假设并选择保持、调整、暂停或重新设计；持续位不得无声消失，原始反馈仍归 M2 |
| S6 | 输入是一个已经成形且合法的选题，要求形成 Content Brief 可直接消费的内容任务 | 是否输出一个主要工作、有限次要贡献、事实/权限/观察边界，并保留下游创意与生产自由 |
| S7 | 用户同时要求 M3 改长期定位、指定具体创意机制并把脚本写完 | 是否拒绝越界部分并正确路由，同时继续完成仍属于 M3 的周期判断或内容任务，不得以空拒绝冒充守边界 |

不得增加第八个场景。若发现某场景输入无法从已接受合同和冻结夹具无歧义编译，先完成其他六个，只对该精确缺口报告；不得自行编造业务事实。

### 5.2 每个场景的实测材料

每个场景必须提供：

1. 场景编号和自然语言名称；
2. 真实运营问题和唯一主要验收目的；
3. 对应产品义务与硬门；
4. 完整、可逐字复制的输入；
5. 输入真源路径、文件 SHA-256、复制文本 SHA-256 和逐字一致机械核验；
6. Dify App 名称、App ID、候选版本和如何确认 v1.5.2 已加载；
7. 从打开应用到运行完成的逐步操作；
8. 不得改变的参数、输入和设置；
9. 正常完成、纯传输失败和产品失败如何区分；
10. 需要保存的完整原始输出、运行 ID、时间、模型、token 和截图；
11. Founder 需要观察的自然语言问题；
12. 执行侧基于既有证据给出的初步专业判断；
13. 结果回交路径和证据文件命名；
14. 该场景是否触发整体硬失败。

七条完整输入、候选哈希、App/图/Skill/Prompt 哈希和验收问题必须在 Founder 运行 S1 前一次性冻结。看到任一输出后不得修改测试组、候选、输入或判据。

### 5.3 Founder 操作规则

执行侧不得代跑。Founder 在真实 Dify 应用中每条只运行一次。

以下不是重试理由：

- 输出不好、为空或遗漏；
- 模型违反产品义务；
- 闸门拒收；
- Founder 不满意；
- 与预期不同。

只有请求未进入模型节点且没有任何模型输出的纯传输失败，允许同一输入重试一次；第一次失败和重试必须同时保留。

## 6. 第三阶段：Founder 亲测前停止

完成 v1.5.2、零模型技术闭合、Dify 部署和七场景实测包后：

1. commit 并 push 任务分支；
2. 用 `git ls-remote` 核验远端完整哈希；
3. 输出完整证据索引和回滚入口；
4. 确认没有运行中的模型、Runner、盲评或后台评测进程；
5. 保持进度 `IN_PROGRESS`；
6. 不输出任何终态；
7. 交付一个 Founder 首先打开的实测说明文件。

回执：

```text
M3_FOUNDER_DIFY_SINGLE_SET
= READY_TO_RUN

executor_model_calls_after_rebase
= 0

founder_test_runs_completed
= 0/7

task_progress
= IN_PROGRESS
```

## 7. Founder 返回结果后的同任务接续

Founder 亲测后，在同一任务中接收：

- 七条实际原始输出；
- 运行 ID、时间、模型、token 和截图；
- 必要的纯传输失败记录；
- Founder 整体 `PASS` 或 `FAIL`。

执行侧只做零模型证据绑定、技术核验和记录，不得重新调用模型。

### 7.1 Founder PASS

只有同时满足以下条件才能判 `DONE`：

- 所有适用确定性技术硬门成立；
- 七个输入证据绑定准确；
- Founder 明确整体 `PASS`；
- 回滚、远端任务分支和声明上限闭合。

完成后输出：

```text
M3_ENGINEERING_TASK
= DONE

M3_FOUNDER_PRODUCT_ACCEPTANCE
= PASS

BLIND_REVIEW
= NOT_APPLICABLE_BY_FOUNDER_REBASE

MODULE_AB_GAIN_VS_GOOD_PROMPT
= NOT_CLAIMED

M5
= NOT_STARTED_NOT_AUTHORIZED

REAL_BUSINESS_LIFT
= NOT_VERIFIED
```

不得合并 main；后续合并和 M5 必须取得独立授权。

### 7.2 Founder FAIL

Founder 整体 `FAIL` 后：

- 当前候选记录为 `FAILED`；
- 保存 Founder 自然语言原因及绑定输出；
- 不自动修复、不重跑、不建立下一候选；
- 不请求立即进行第二轮测试；
- 输出持久化 Checkpoint 后停止。

回执：

```text
M3_ENGINEERING_TASK
= FAILED

M3_FOUNDER_PRODUCT_ACCEPTANCE
= FAIL

AUTOMATIC_REPAIR_OR_RETEST
= NOT_AUTHORIZED
```

## 8. 不得再向 Founder 上推的事项

以下均已决定，执行侧不得再次要求 Founder 选择：

- 是否改两句审计块输出形状规则：已批准；
- 最终候选版本：v1.5.2；
- 是否补跑 G1-A：不补；
- 是否做 A/B、盲测、盲评或多轮评测：全部取消；
- 是否允许执行侧调用 DeepSeek：不允许；
- 测试组数量：七个；
- 每个输入运行次数：一次；
- B09-5 是否进入测试组：必须进入 S4；
- 结果形态：Founder 整体 `PASS` 或 `FAIL`；
- FAIL 后是否自动修复重测：不允许。

执行侧必须自行承担代码、Dify、版本、证据、回滚、哈希和技术判断，不得把技术 HOW 或内部 AC 状态推给 Founder。

## 9. 声明上限

即使 Founder 最终 PASS，也只能声明：

> 绑定 v1.5.2 的 M3 候选通过了适用确定性技术门，并在一组事前冻结的七个 Dify 输入上获得 Founder 产品接受。

不得声明：

- 已盲评证明优于一份好提示词；
- 已完成 M5 成品集成增益；
- 已生产上线；
- 已产生真实 GMV、线索、到店、增长或经营提升；
- 测试结果证明真实因果增益。

`END_MARKER: M3-ENGINEERING-EXECUTION-PROMPT-v1.2-FOUNDER-SINGLE-SET-REBASE-END`
