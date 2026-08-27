# M3 Founder 七场景实测 · 只读提取与绑定收口 v1.0

- `task_id`：`DIYU-V1-M3-ACCOUNT-CONTENT-OPERATOR-001`
- `entry_mode`：`CONTINUE_TASK`（非 NEW_TASK，不修改合同）
- 后继合同：`M3_ENGINEERING_TASK_CONTRACT_v1.3_FOUNDER_SINGLE_SET_REBASE.yaml` sha256 `49021e601658194bc734285830d531352c19c1fa4416855c1f524efb073bff49`
- 本轮执行侧模型调用：**0**（只读 Console API + 本地确定性重算）
- 生成时间：`2026-08-27T14:55:09-0700`

## 1. Founder 裁决（原文引用，不改写）

```text
M3_FOUNDER_ACCEPTANCE = PASS
accepted_candidate = v1.5.2
accepted_test_set = S1-S7
founder_observed_all_outputs = true
founder_test_runs_completed = 7/7
```

执行侧不得重新做产品裁决，也不得推翻该 PASS。以下只核验绑定、完整性与确定性行为。

## 2. 运行识别：不按「最近七次」，按逐字输入哈希交叉定位

该 App 全部 workflow 日志 **641 条**，按 `created_from` 分离：`web-app` **8 条**、`service-api` **633 条**（执行侧历史运行，全部排除）。
`web-app` 八条全部来自同一浏览器会话 `69f92e79…`，时间窗 `2026-08-27 13:42:47` – `2026-08-27 13:52:32`。

| 场景 | run_id | 角色 | 起 | 用时 | tokens | 闸门 | 路径 | 周期状态 | 终稿字数 |
|---|---|---|---|---|---|---|---|---|---|
| S1 | `591d3e80-6dc3-436b-8e0b-fdc90e896f9c` | 正式 | 13:42:47 | 160.0s | 35962 | NEEDS_FIX | gate_repaired | ACCEPTABLE_AS_NEW_BASELINE | 1985 |
| S2 | `41e1fa39-beca-4deb-b158-5ab36ae78aad` | 正式 | 13:47:55 | 164.4s | 37739 | CLEAN | draft_verbatim | ACCEPTABLE_AS_NEW_BASELINE | 1972 |
| S3 | `136f7212-36ec-4366-99d1-e8dc4c9836a0` | 正式 | 13:48:18 | 270.8s | 52870 | NEEDS_FIX | gate_repaired | ACCEPTABLE_AS_NEW_BASELINE | 2018 |
| S4 | `8eab421c-1133-453b-9383-acf4e9d269ed` | 正式 | 13:48:42 | 191.1s | 39582 | CLEAN | draft_verbatim | ACCEPTABLE_AS_NEW_BASELINE | 2680 |
| S5 | `fef43015-e54a-47ce-853e-4a2f522b9187` | 正式 | 13:49:04 | 152.1s | 44366 | NEEDS_FIX | gate_repaired | ACCEPTABLE_AS_NEW_BASELINE | 2360 |
| S6 | `55eb0a6b-44ac-4370-bc8a-478cf5fc7d07` | 正式 | 13:50:45 | 90.7s | 26758 | CLEAN | draft_verbatim | ACCEPTABLE_AS_NEW_BASELINE | 1468 |
| S6 | `0a0f406d-d4d3-4c4e-9596-2f0c936f5117` | **重复提交** | 13:52:14 | 100.6s | 28421 | CLEAN | draft_verbatim | ACCEPTABLE_AS_NEW_BASELINE | 1484 |
| S7 | `aa92b3ca-a3a8-4125-9314-3d84ce6cf85a` | 正式 | 13:52:32 | 206.7s | 41731 | CLEAN | draft_verbatim | ACCEPTABLE_AS_NEW_BASELINE | 2758 |

绑定依据（每条都逐条算过，不是按时间挑的）：App ID、已发布版本、三个输入框的逐字内容与 SHA-256、Founder 运行时间、`FREEZE_MANIFEST.json` 场景绑定、workflow run 与 node execution 记录。**七个场景各自唯一命中，无一靠时间顺序推定。**

## 3. 九项核验

| 项 | 结果 | 关键数 |
|---|---|---|
| 七个场景是否全部存在 | `PASS` | S1–S7 全在 |
| 每个场景是否只绑定一次正式运行 | **`FAIL`** | S6 提交了两次，两次都成功 |
| 输入是否与冻结包逐字一致 | **`FAIL`** | `account_context` / `loaded_references` 八条全部逐字节相同；`user_request` 八条一律多一个结尾换行 |
| 运行是否来自 v1.5.2 已发布候选 | **`FAIL`** | 可执行内容绑定成立、版本标签绑定不成立（见 §4） |
| 是否存在未披露的纯传输失败或重试 | **`FAIL`** | 纯传输失败 0 次；节点错误 0 个；但存在 1 次未披露的重复提交 |
| 最终输出是否完整落盘 | `PASS` | 零截断；终稿字数 1985, 1972, 2018, 2680, 2360, 1468, 2758；三层输出逐字节一致 |
| Founder 裁决是否准确绑定这七次输出 | `PASS` | 7 条正式运行全部落盘可回指，终稿均非空 |
| 闸门或补齐节点是否代写实质交付 | `PASS` | 8/8 无代写（含 3 条补齐路）；仓库 v1.5.2 代码重算 8/8 逐字节一致 |
| 是否出现会使裁决对象失真的错绑 | `PASS` | 全部运行自报 `gate_version` / `post_gate_version` = `v1.5.2` |

### 3.1 V8 的分量：补上了零模型证不到的那一层

`ep34` 的 Z7 当时**显式声明**过覆盖不到补齐路：「补齐路的终稿由补齐 LLM 产出，零模型拿不到，不在本项覆盖内」。
本轮 Founder 的七次运行里有 3 条真的走了补齐路（S1 / S3 / S5），补齐节点的原始输出已落盘，所以这一层现在**有实物可验**：

- 判据：终稿里每个字符必须来自模型产物（直发路取草稿、补齐路取补齐输出），或来自 `render_body` 那张封闭替换表；子序列判定，**只许删、不许插**。
- 结果：8/8 通过。确定性节点没有给交付物添过一个字。
- 另加一道更强的：用**仓库里的 v1.5.2 代码**对同一份草稿重算 `gate` / `assemble` / `post_gate`，与线上记录比对 —— 8/8 三个节点全部**逐字节相同**。线上跑的确定性代码与仓库代码行为等同，这是实测不是声明。

## 4. 四个真实缺口（精确差异，不做闭合）

### 缺口 1 · 七条运行跑在一个**未命名的重新发布版本**上

Founder 运行期间，App 被重新发布了一次：

| | workflow_id | version | marked_name |
|---|---|---|---|
| 冻结候选 | `706fdce0-9a0d-42ec-8a8c-e4f6a3071173` | `2026-08-27 19:46:47.281053` | `m3-cand-v1.5.2` |
| 实际承载 S2–S7 | `ff801653-ba58-48c9-bbfe-e77c144c9b1d` | `2026-08-27 20:46:36.695260` | **（空）** |

- S1（`591d3e80`，`13:42:47`）跑在冻结候选上。
- 新版本发布于 `2026-08-27 13:46:36`（本地），在 S1 结束之后、S2 开始之前。
- 其余 7 条（S2–S7 + 那次重复提交）跑在新版本上。

**差异逐项算过，全部落在画布外观层：**

| 维度 | 是否相同 |
|---|---|
| 七个节点的 `data`（系统提示词、代码节点源码、模型配置、变量） | **逐字节相同** |
| 六条边的 source / target / handle 拓扑 | **完全相同** |
| 系统提示词 SHA-256 | 八条运行全部 = `3a3c657d82d45e96dfbf9abdcb88adf6` = 冻结值 |…
| 模型 / provider / 温度 | 八条全部 = `deepseek-v4-flash` / `langgenius/deepseek/deepseek` / `0.4` |
| 节点 `position` / `positionAbsolute` / `height` | 不同（画布重排） |
| 边 `data.isInLoop` | 新版本多了这个前端标记 |
| 画布 `viewport` 平移与缩放 | 不同 |

推断（**不是观察**）：打开画布这个动作触发了自动保存并重排了节点坐标，随后有人在画布上点了「发布」，把这个只含几何改动的草稿发成了新版本。我没有该次点击的直接记录，所以这条只到**推断**级。

**结论分成两半，不合并：**

```text
可执行内容绑定 = 成立（系统提示词 + 全部节点 data + 边拓扑，八条全部逐字节相同）
已发布版本标签绑定 = 不成立（7/8 条不在 m3-cand-v1.5.2 这条版本记录上）
```

按授权 §4：Founder 实际运行的已发布版本记录不是冻结的 `m3-cand-v1.5.2`，因此**受影响项标为 `NOT_VERIFIED`**。可执行内容绑定成立这件事**不得自动上推**成版本标签绑定成立 —— 那需要有权者裁定，不是执行侧能给的。

### 缺口 2 · S6 提交了两次，无法唯一确定 Founder 判的是哪一份

- `55eb0a6b-44ac-4370-bc8a-478cf5fc7d07` · 2026-08-27 13:50:45 · 用时 90.7s · 终稿 1468 字 · sha256 `e5fb113a99553e0c…`（本报告记为正式）
- `0a0f406d-d4d3-4c4e-9596-2f0c936f5117` · 2026-08-27 13:52:14 · 用时 100.6s · 终稿 1484 字 · sha256 `15de69800399dd4e…`（重复提交）

两次输入逐字节相同、都成功、都产出了正文，因此**第二次不属于合同允许的重跑**（合同只允许「无任何模型输出的纯传输故障」重跑一次）。
按 Founder 自己定的「按第一次的真实结果算」，本报告把先发生的那条记为正式，**两条全部原样保留，一条都不删**。
但 Founder 声明的是 `7/7`，实际提交是 8 次 —— **Founder 到底看的是哪一份 S6 输出，后台证据不能唯一确定**。按授权 §2，这是需要精确报告的场景级证据歧义，执行侧不得择优选择。

### 缺口 3 · `user_request` 八条一律多一个结尾换行

| 输入框 | 结果 |
|---|---|
| `account_context` | 八条**全部逐字节相同** |
| `loaded_references` | 八条**全部逐字节相同** |
| `user_request` | 八条一律 = 冻结原文 + 一个结尾 `\n` |

形态统一、只在结尾、不含任何内容差异，是从代码块复制粘贴的机械痕迹。语义上不改变任何东西，但**逐字不等于冻结包**，据实记为差异，不当作一致。

### 缺口 4 · Dify 实例的数据库在提取完成后被清空

提取完成之后、写本报告之前，Dify 整个容器栈重启，PostgreSQL 走了 **initdb 全新初始化**：`apps` 表 0 行，`setup` 回到 `not_started`，`PGDATA` 里每个文件都是新建时刻的。该 App、641 条运行记录与全部版本谱系**已不在这个实例上**。

- 本轮执行侧对 Dify 只发过 **GET**，未修改、未删除、未重放、未覆盖任何运行记录。
- 起因不在本任务范围内，也不是本任务能裁定的，据实记录为外部事实。
- **七场景全部原始证据已在此事件之前落盘**，不受影响（见 §5）。
- 受影响的是**往后**的动态绑定复验：合同 `dynamic_dify_binding_requires_refresh: true` 这一条现在无法再满足；线上回滚入口也不再可对活体演练。
- 重建路径仍在盘上：`account-operations/evidence/ep37-rollback-drill-v152/m3_candidate_app_v152.dsl.yaml`（sha256 `bd676f291b8e108c906b606549da357f0dfc5153e3ccccb3ca15d97670811620`，含 v1.5.2 全部改动），可导入重建；本轮**未**执行重建，未获授权。

## 5. 证据落盘

### 5.1 原始提取（提取方法：Dify Console API 只读）

`account-operations/evidence/ep39-founder-seven-run-extraction/`

| 文件 | 内容 |
|---|---|
| `app_logs_census.json` | 全部 641 条日志普查、按来源分离、八条 web-app 运行清单 |
| `published_version_lineage.json` | 已发布版本谱系（提取时刻的完整快照） |
| `frozen_graph_reference.json` | 冻结图基准哈希 |
| `raw/<run_id>/workflow_run.json` | 八条运行的完整记录，含执行时的整张图 |
| `raw/<run_id>/node_executions.json` | 八条运行的全部 7 个节点执行记录 |
| `FOUNDER_RUN_VERIFICATION.json` | 九项核验的全部中间量与结论 |

### 5.2 逐场景结果目录

`account-operations/founder-pack-v152/results/S1..S7/`，每个含：

`input_account_context.txt`｜`input_user_request.txt`｜`input_loaded_references.txt`｜`final_output.txt`｜`draft_raw.txt`｜`gate_report.json`｜`post_gate_report.json`｜`positions_final.json`｜`final_audit.txt`｜`node_executions.json`｜`run_meta.json`（补齐路另有 `gate_repair_raw.txt`）

S6 的第二次提交完整存放在 `results/S6/extra_second_submission_0a0f406d/`，结构相同，**不删不改**。

`run_meta.json` 含：场景、run_id、App、版本、与冻结候选的图差异全量、状态、起止时间、用时、token、模型与 provider、系统提示词哈希及是否等于冻结值、三段输入哈希与逐字差异、闸门与周期状态、终稿与草稿哈希、Founder PASS 引用、提取方法与提取时间。

## 6. 七场景实际结果

| 场景 | 主要验收目的 | 闸门 | 路径 | 周期状态 | 终稿 |
|---|---|---|---|---|---|
| S1 | 暂定锚点、无正式定位时能否继续作有边界周期判断 | NEEDS_FIX | gate_repaired | ACCEPTABLE_AS_NEW_BASELINE | 1985 字 |
| S2 | 三类转化不被压成一个「转化」，长期基线不被目标切换冲掉 | CLEAN | draft_verbatim | ACCEPTABLE_AS_NEW_BASELINE | 1972 字 |
| S3 | 产能掉到 1 条时是否做真取舍 | NEEDS_FIX | gate_repaired | ACCEPTABLE_AS_NEW_BASELINE | 2018 字 |
| S4 | 无市场资料下拒绝无证据断言、同时仍完成不依赖市场证据的判断 | CLEAN | draft_verbatim | ACCEPTABLE_AS_NEW_BASELINE | 2680 字 |
| S5 | 冲突反馈下形成解释假设并选择处置，持续位一个不丢 | NEEDS_FIX | gate_repaired | ACCEPTABLE_AS_NEW_BASELINE | 2360 字 |
| S6 | 产出能被 Content Brief 直接消费且只有一个主要工作 | CLEAN | draft_verbatim | ACCEPTABLE_AS_NEW_BASELINE | 1468 字 |
| S7 | 拒绝越界并正确路由，同时继续完成仍属 M3 的部分 | CLEAN | draft_verbatim | ACCEPTABLE_AS_NEW_BASELINE | 2758 字 |

### 6.1 S4：历史上翻过车的那一格，这次没有退化

`8eab421c-1133-453b-9383-acf4e9d269ed`：闸门 `CLEAN`、路径 `draft_verbatim`、终稿 **2680 字**、`finish_reason = stop`。

历史上 446 次有草稿的运行里有 3 次只吐审计块、正文 0 字，其中 2 次就发生在这个输入上。v1.5.2 为此在 Skill 里加了两句硬规则。**这一次它没有退化。**

声明上限：这是 **1 次观察**，n=1。它证明了那两句规则在这一次运行下没有失效，**不能**证明退化率已被降低到某个水平，也**不能**把「两句规则修好了 B09-5」从推断上推成已确认 —— 那需要多次运行的统计证据，本轮没有，也不授权去取。

## 7. 适用验收项矩阵（按后继合同 v1.3 重算）

| 验收项 | 状态 | 依据 |
|---|---|---|
| M3-AC-00 授权、身份与基线回指 | **`NOT_VERIFIED` (INSUFFICIENT)** | 任务身份、分支、远端、Skill、系统提示词、模型、App 全部绑定成立；**已发布候选版本标签**对 7/8 条运行不成立，`user_request` 逐字不等于冻结包。可执行内容绑定成立，但不得据此上推 |
| M3-AC-01 | `PASS` | 确定性证据（`ep34` 零模型闭合、`ep36` 结构与提示词、`ep38` 包核验）+ Founder 七场景整体 PASS；本轮 `ep39` 另加八条运行的仓库代码重算一致与无代写核验 |
| M3-AC-02 | `PASS` | 确定性证据（`ep34` 零模型闭合、`ep36` 结构与提示词、`ep38` 包核验）+ Founder 七场景整体 PASS；本轮 `ep39` 另加八条运行的仓库代码重算一致与无代写核验 |
| M3-AC-03 | `PASS` | 确定性证据（`ep34` 零模型闭合、`ep36` 结构与提示词、`ep38` 包核验）+ Founder 七场景整体 PASS；本轮 `ep39` 另加八条运行的仓库代码重算一致与无代写核验 |
| M3-AC-04 | `PASS` | 确定性证据（`ep34` 零模型闭合、`ep36` 结构与提示词、`ep38` 包核验）+ Founder 七场景整体 PASS；本轮 `ep39` 另加八条运行的仓库代码重算一致与无代写核验 |
| M3-AC-05 | `PASS` | 确定性证据（`ep34` 零模型闭合、`ep36` 结构与提示词、`ep38` 包核验）+ Founder 七场景整体 PASS；本轮 `ep39` 另加八条运行的仓库代码重算一致与无代写核验 |
| M3-AC-06 | `PASS` | 确定性证据（`ep34` 零模型闭合、`ep36` 结构与提示词、`ep38` 包核验）+ Founder 七场景整体 PASS；本轮 `ep39` 另加八条运行的仓库代码重算一致与无代写核验 |
| M3-AC-07 | `PASS` | 确定性证据（`ep34` 零模型闭合、`ep36` 结构与提示词、`ep38` 包核验）+ Founder 七场景整体 PASS；本轮 `ep39` 另加八条运行的仓库代码重算一致与无代写核验 |
| M3-AC-08 | `PASS` | 确定性证据（`ep34` 零模型闭合、`ep36` 结构与提示词、`ep38` 包核验）+ Founder 七场景整体 PASS；本轮 `ep39` 另加八条运行的仓库代码重算一致与无代写核验 |
| M3-AC-09 | `PASS` | 确定性证据（`ep34` 零模型闭合、`ep36` 结构与提示词、`ep38` 包核验）+ Founder 七场景整体 PASS；本轮 `ep39` 另加八条运行的仓库代码重算一致与无代写核验 |
| M3-AC-10 | `PASS` | 确定性证据（`ep34` 零模型闭合、`ep36` 结构与提示词、`ep38` 包核验）+ Founder 七场景整体 PASS；本轮 `ep39` 另加八条运行的仓库代码重算一致与无代写核验 |
| M3-AC-11 | `PASS` | 确定性证据（`ep34` 零模型闭合、`ep36` 结构与提示词、`ep38` 包核验）+ Founder 七场景整体 PASS；本轮 `ep39` 另加八条运行的仓库代码重算一致与无代写核验 |
| M3-AC-12 | `PASS` | 确定性证据（`ep34` 零模型闭合、`ep36` 结构与提示词、`ep38` 包核验）+ Founder 七场景整体 PASS；本轮 `ep39` 另加八条运行的仓库代码重算一致与无代写核验 |
| M3-AC-13 | `PASS` | 确定性证据（`ep34` 零模型闭合、`ep36` 结构与提示词、`ep38` 包核验）+ Founder 七场景整体 PASS；本轮 `ep39` 另加八条运行的仓库代码重算一致与无代写核验 |
| M3-AC-14 | `PASS` | 确定性证据（`ep34` 零模型闭合、`ep36` 结构与提示词、`ep38` 包核验）+ Founder 七场景整体 PASS；本轮 `ep39` 另加八条运行的仓库代码重算一致与无代写核验 |
| M3-AC-15 | `PASS` | 确定性证据（`ep34` 零模型闭合、`ep36` 结构与提示词、`ep38` 包核验）+ Founder 七场景整体 PASS；本轮 `ep39` 另加八条运行的仓库代码重算一致与无代写核验 |
| M3-AC-16 | `PASS` | 确定性证据（`ep34` 零模型闭合、`ep36` 结构与提示词、`ep38` 包核验）+ Founder 七场景整体 PASS；本轮 `ep39` 另加八条运行的仓库代码重算一致与无代写核验 |
| M3-AC-17 | `PASS` | 确定性证据（`ep34` 零模型闭合、`ep36` 结构与提示词、`ep38` 包核验）+ Founder 七场景整体 PASS；本轮 `ep39` 另加八条运行的仓库代码重算一致与无代写核验 |
| M3-AC-18 公平同模型 A/B | `NOT_APPLICABLE_BY_FOUNDER_REBASE` | 盲评/AB 路径按 Founder REBASE 取消；历史 `NOT_VERIFIED` 记录原样保留，不改写为 PASS |
| M3-AC-19 Qwen 隔离、独立 Review、留出分轨 | `NOT_APPLICABLE_BY_FOUNDER_REBASE` | 同上 |
| M3-AC-20 收口、回滚、远端与 Founder 接受 | **`NOT_VERIFIED` (ABSENT)** | 远端任务分支收口成立、Founder PASS 已记录、回滚 DSL 完整在盘；但线上 Dify 实例数据库已被清空，`dynamic_dify_binding_requires_refresh` 无法再满足，活体回滚入口不可复演 |

**AC-01–AC-17 判 `PASS` 的失效面说明**：缺口 1 只影响版本标签，不影响 Founder 所观察内容由哪套逻辑产出 —— 系统提示词、七个节点 data、边拓扑、确定性代码行为，八条运行全部被证明与冻结候选相同。因此这些产品语义项**不随缺口 1 失效**（A3：不多算）。缺口 2 只使 S6 的**产物身份**存疑，两份都在，都非退化，不改变 Founder 的整体 PASS 覆盖。

## 8. 终态与声明上限

```text
M3_ENGINEERING_TASK
= IN_PROGRESS

M3_FOUNDER_PRODUCT_ACCEPTANCE
= PASS

FOUNDER_TEST_RUNS
= 7/7_BOUND_AND_PRESERVED（另有 1 次 S6 重复提交，一并保留并披露）

EXECUTOR_MODEL_CALLS_AFTER_REBASE
= 0

BLIND_REVIEW
= NOT_APPLICABLE_BY_FOUNDER_REBASE

MODULE_AB_GAIN_VS_GOOD_PROMPT
= NOT_CLAIMED

MAIN_MERGE
= NOT_AUTHORIZED_NOT_PERFORMED

M5
= NOT_STARTED_NOT_AUTHORIZED

REAL_BUSINESS_LIFT
= NOT_VERIFIED
```

**为什么不是 `DONE`**：授权 §7 要求「所有适用确定性技术门成立」才推导 DONE，并在 §4 明确「如果发现 Founder 实际看到的不是冻结 v1.5.2、输入不是冻结 S1-S7，必须将受影响项标记为 `NOT_VERIFIED` 并报告精确差异，不得伪造闭合」。M3-AC-00 与 M3-AC-20 现为 `NOT_VERIFIED`，DONE 不可推导。按授权「如果证据绑定尚有真实缺口，保持 `IN_PROGRESS`」，本轮停在 `IN_PROGRESS`。

**这次核验能说明什么**：绑定 v1.5.2 可执行内容的 M3 候选，在一组事前冻结的七个 Dify 输入上真实运行并获得 Founder 产品接受；七次运行的全部原始证据完整保留、可逐条回指；确定性组件在这八次真实运行中没有代写过任何交付内容。

**不能说明**：已盲评证明优于一份好提示词｜已完成 M5 成品集成增益｜已生产上线｜已产生真实 GMV／线索／到店／增长｜测试结果证明真实因果增益｜两句新 Skill 规则已被证明修好了 B09-5（仍是**推断**，本轮只多了 1 次未退化的观察）。

