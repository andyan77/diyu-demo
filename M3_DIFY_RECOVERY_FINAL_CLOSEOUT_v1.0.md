# M3 · Dify 宿主挂载恢复与整体收口 v1.0

- `task_id`：`DIYU-V1-M3-ACCOUNT-CONTENT-OPERATOR-001`
- `entry_mode`：`REBASE_TASK`
- Execution Prompt：`M3_DIFY_RECOVERY_AND_FINAL_CLOSEOUT_EXECUTION_PROMPT_v1.0.md` sha256 `258d16b788f5ce053b0f3d669e6ff640cfce6a502d3ec51cebca420c75c5a573`
- 后继合同：`M3_ENGINEERING_TASK_CONTRACT_v1.4_DIFY_RECOVERY_CLOSEOUT_REBASE.yaml` sha256 `787243cf82d7246bb090d0a0c9ff6f64168c964ed1d9a2ab3ef163c75aee6220`
- **执行侧模型调用：0；执行侧触发的工作流运行：0**
- 生成时间：`2026-08-27T16:02:38-0700`

## 1. 采用路径 A：原数据库与原 App 一并返回

阶段 A 冻结现场时发现**宿主挂载已经自行恢复**：

| | 目录元数据 |
|---|---|
| 宿主 `/home/faye/dify/docker/volumes/db/data` | `directory|4096|root:root|755|2026-08-19 03:49:57.292667948 -0700` |
| 容器 `/var/lib/postgresql/data` | `directory|4096|root:root|755|2026-08-19 10:49:57.292667948 +0000` |

size、owner、mode 与**纳秒级 mtime 完全相同**（`-0700` 与 `+0000` 是同一时刻的两种时区表述），
与上一轮「size 4096 对 60、mtime 差 8 天」的错位形成直接对照。挂载已正确解析到 WSL 宿主卷。

| 只读判路 | 值 |
|---|---|
| `apps` | 50 |
| `accounts` / `tenants` | 1 / 1 |
| `workflows` / `workflow_runs` | 279 / 2264 |
| Dify setup | `{"step":"finished","setup_at":"2026-08-19T11:08:56"}` |
| 数据库租户 | `09758721-a8d3-4f01-b0f2-c69c82a11568` |
| 宿主 storage 租户目录 | `09758721-a8d3-4f01-b0f2-c69c82a11568`（一致） |
| 原 M3 App `b7fb5b1a…` | 存在，`mode=workflow`，名称含 task_id 与 `CANDIDATE TEST ONLY` |
| 该 App 历史运行 | **641 条**（与丢失前一致） |
| 八条 Founder 运行 | id、状态、时间戳逐条一致，全部在 |

按 §8.1，**未导入 ep37**，未生成新 UUID。

```text
RECOVERY_PATH = ORIGINAL_DATABASE_AND_APP
CURRENT_APP_ID = b7fb5b1a-9278-426c-bb8a-f9f288639548
HISTORICAL_FOUNDER_RUN_APP_ID = b7fb5b1a-9278-426c-bb8a-f9f288639548
IDENTITY_RELATION = SAME_APP_NO_DUAL_IDENTITY
```

### 1.1 没有重启 Docker Desktop

§6 授权的是「**最多**一次」，不是必须一次。挂载在冻结现场时已经正确，
重启的差异效果为零，按 A5 不执行 —— 也就不必停掉你正在跑的其他容器。

```text
docker_desktop_restarts_performed = 0
```

## 2. 活体候选恢复为冻结 v1.5.2（§8.4）

恢复前当前已发布的仍是那条 `marked_name` 为空、带画布几何漂移的重发版。
按 §8.4 把草稿还原成 ep35 冻结图并具名发布，让**当前活体候选**的绑定不再依赖等价论证。

| 项 | 值 |
|---|---|
| 已发布版本名 | `m3-cand-v1.5.2-live` |
| 已发布时间 | `2026-08-27 22:50:25.321384` |
| 已发布图 == 冻结图（逐字节） | **True** |
| 草稿 == 已发布 | True |
| 节点 / 边 | 7 / 6 |
| 系统提示词 sha256 | `3a3c657d82d45e96dfbf9abdcb88adf66c58bb74f69f1e1e0412591242898028` == 冻结值 |
| `SKILL.md` 工作区 == git HEAD == 冻结值 | True（`90596da5…`） |
| 模型 / provider / 温度 | `deepseek-v4-flash` / `langgenius/deepseek/deepseek` / `0.4` |
| `http_request` / `tool` 节点 | 无 |

发布名刻意用 `m3-cand-v1.5.2-live`，**不复用历史具名发布 `m3-cand-v1.5.2`**
（`706fdce0…`，`2026-08-27 19:46:47.281053`）—— 历史那条原样保留在版本谱系里，不冒充。

### 2.1 浏览器渲染画布实证

用真实登录态打开画布，从**渲染出来的 DOM** 读：7 个节点、6 条连线、七个节点标题全在、
画布上无 `http_request` / `tool` 节点、LLM 节点面板上挂着 SKILL 正文。两张截图带 sha256。

### 2.2 回滚入口当前有效

恢复后从活体 App 导出 DSL：

```text
导出 sha256      = bd676f291b8e108c906b606549da357f0dfc5153e3ccccb3ca15d97670811620
ep37 冻结件 sha256 = bd676f291b8e108c906b606549da357f0dfc5153e3ccccb3ca15d97670811620
逐字节相同        = True
```

## 3. 持久性复核（§8.8）

对 Dify compose 做一次**普通** `stop` → `start`（未用 `down`、`-v`、`prune`、
未第二次重启 Docker Desktop）。重启后：

| 项 | 值 |
|---|---|
| App 仍在 | True |
| 已发布版本名 / 时间 | `m3-cand-v1.5.2-live` / `2026-08-27 22:50:25.321384` |
| 已发布图 == 冻结图 | True |
| 系统提示词 == 冻结值 | True |
| 该 App 历史运行 | 641 条 |
| 数据库租户 == 宿主 storage 租户 | True |

### 3.1 一件必须披露的事：这台 Dify 上有别人的活儿在跑

停机窗口内这台实例上有**其他 App** 的工作流在运行（不是本任务的 App）。核查结果：

- `22:40`–`23:00` 之间全部 15 条运行**状态均为 `succeeded`**
- `22:00` 之后**零条** `failed` 或卡在 `running`
- 本任务 App 的运行数始终是 **641**，执行侧触发的运行数为 **0**

即：这次停机没有打断任何在途运行。但我在阶段 A 的「无不可中断写入」判断只看了容器层，
没有查在途 workflow run —— 这是我那一步的疏漏，结果无害，如实记下。

## 4. AC-00 与 AC-20 重算

### M3-AC-00 · `PASS`

| 需要同时成立 | 结果 |
|---|---|
| 原 `task_id`、任务分支与当前远端 commit 绑定 | 成立（远端哈希见 §6） |
| 当前持久活体 M3 App 存在 | True，且名称标着 `CANDIDATE TEST ONLY` |
| 当前 App 的 v1.5.2 Skill / Prompt / 图 / 模型 / provider / 温度绑定成立 | 全部成立，见 §2 |
| 当前 App 在普通 compose 重启后仍存在 | True |
| 历史 App 与新恢复 App 身份没有混写 | 路径 A 未生成新 UUID，同一个 App，无双重身份 |

### M3-AC-20 · `PASS`

| 需要同时成立 | 结果 |
|---|---|
| Founder 七场景 PASS 与证据继续绑定历史输出 | 7 条正式 + 1 条披露的额外提交，641 条运行行仍在库 |
| 当前活体候选与 v1.5.2 恢复证据成立 | 见 §2 |
| 回滚导出与恢复入口当前有效 | 导出与 ep37 冻结件**逐字节相同** |
| 最终证据索引完整 | `ep44/FINAL_EVIDENCE_INDEX.json` |
| 任务分支推送并 `git ls-remote` 核验 | 见 §6 |
| worktree 干净 | 见 §6 |
| 声明上限准确 | 见 §7 |
| main / PR / M5 / 生产均未改变 | 未 merge、未建 PR、未启 M5；本轮只写了任务专用 App |

### 完整 AC 矩阵

| 验收项 | 状态 |
|---|---|
| `M3-AC-00` 授权、身份与基线回指 | **`PASS`** |
| `M3-AC-01`–`M3-AC-17` | `PASS`（保持；本轮恢复未引入依赖失效） |
| `M3-AC-18` 公平同模型 A/B | `NOT_APPLICABLE_BY_FOUNDER_REBASE`（历史 `NOT_VERIFIED` 原样保留） |
| `M3-AC-19` Qwen 隔离、独立 Review、留出分轨 | `NOT_APPLICABLE_BY_FOUNDER_REBASE` |
| `M3-AC-20` 收口、回滚、远端与 Founder 接受 | **`PASS`** |

## 5. 三项证据身份裁定继续有效，未被恢复改写

- S1 绑具名 v1.5.2；S2–S7 绑执行内容等价的未命名重发版。**没有写成标签相同。**
- S6 正式运行是 `55eb0a6b`；`0a0f406d` 仍是 `UNAUTHORIZED_EXTRA_SUBMISSION`，保留、不替换、不择优。
- `user_request` 只接受最多一个结尾 LF 的载体归一化，原始字节不等**继续披露**。
- 七场景产品结果已 Founder PASS，本轮未重跑、未再评。

## 6. Git 与远端

完整远端哈希、worktree 状态与凭据扫描结果见本文件末尾的收口回执与 `ep44/FINAL_EVIDENCE_INDEX.json`。

## 7. 终态与声明上限

```text
M3_ENGINEERING_TASK
= DONE

M3_FOUNDER_PRODUCT_ACCEPTANCE
= PASS

M3-AC-00
= PASS

M3-AC-20
= PASS

DIFY_RECOVERY_PATH
= ORIGINAL_DATABASE_AND_APP

DIFY_TASK_APP
= RECOVERED_PERSISTENT_AND_CURRENT

FOUNDER_OFFICIAL_TEST_RUNS
= 7/7_BOUND_AND_PRESERVED

DISCLOSED_EXTRA_SUBMISSIONS
= 1

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

**`DONE` 能说明的**：存在一个持久的、当前可运行的 v1.5.2 M3 候选，适用确定性技术门全部成立，
且 Founder 已接受被完整保留的七份历史输出。

**不能说明的**：那七次运行发生在一个新重建的 UUID 上（它们就发生在同一个 App 上，未重建）｜
已盲评证明优于一份好提示词｜已完成 M5 成品集成增益｜已生产上线｜
已产生真实 GMV／线索／到店／增长｜测试结果证明真实因果增益｜
那两句新 Skill 规则已被证明修好了 B09-5（仍是**推断**，只多了 1 次未退化的观察）。

