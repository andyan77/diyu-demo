# Node R0 · 新终端安全接管与 WIP 保全 · pre-rebase diagnostic checkpoint v1.0

`task_id: DIYU-V1-UNIFIED-DIFY-APPLICATION-001` ｜ `entry_mode: REBASE_TASK`
`task_contract_hash: 279f80ba09f9ec4fea53c71c829054276b4baa30071df7305f2f3fbf921e869f`
`contract_semantic_delta: NONE` ｜ `task_progress: IN_PROGRESS` ｜ `terminal_state: unset`

本文件登记新执行终端接管现场时**实际观察到**的事，以及在此之前 WIP 的原样保全。
不判定旧候选终态，不把历史失败改绿，不代 Founder 裁决。

---

## 一、现场核验（不复述规划侧观察值）

### 1.1 稳定合同 hash 复算一致

| 文件 | 声明 sha256 | 复算 | 结果 |
|---|---|---|---|
| Root Execution Prompt v1.0 | `4b72d4ec…a893` | `4b72d4ec…a893` | 一致 |
| Task Contract v1.0 | `279f80ba…e869f` | `279f80ba…e869f` | 一致 |
| Continue Execution Prompt v1.0 | `c2cb867b…d092` | `c2cb867b…d092` | 一致 |

Rebase Prompt 自身 sha256 = `53546a8b4c1f67b040eed70b722ccb109ac510538461ccff937e29db02b9f783`
（该值不在 Prompt 内自含，由本终端首次落盘）。

### 1.2 Git 现场

`worktree=/home/faye/diyu-demo-worktrees/v1-unified-dify-application`
`branch=codex/v1-unified-dify-application-001`
`HEAD=fdc8cff807d930be52be1568fb0f1c9695a256e5`（与 `origin/` 同名分支一致）
`origin/main=01a42b0ed97344a67302ecb6778ae4a772eb28b2`

### 1.3 规划侧观察值已漂移 —— 不得当作激活时成立的事实

规划侧观察时间为 2026-08-29 07:18（America/Los_Angeles）；本终端首次核验为 07:23。

| 锚点 | Prompt 观察值 | 07:23 复算 | 07:29 旧写入者退出后 |
|---|---|---|---|
| `tracked_modified_files` | 6 | 6 | **7** |
| `untracked_task_files` | 13 | **15** | **17** |
| `tracked_diff_sha256` | `c403601895a8…` | `62786cc99a30…` | 见提交本身 |
| `untracked_set_sha256` | `4a33cf37e4bc…` | `ce3c92547bd1…` | 见提交本身 |
| `active_writer_observed` | `NONE_AT_OBSERVATION_TIME` | **ACTIVE，2 个正式运行进行中** | 已退出 |

漂移原样登记，不回退、不覆盖、不假装没有发生。

---

## 二、并发写入者处置（Rebase Prompt §3.2 硬门）

接管时旧执行终端仍存活并正在写同一 worktree、同一 Dify app、同一 evidence 路径：

| 项 | 值 |
|---|---|
| 旧终端 | Claude Code PID `403572`，session `6bb46c51-0946-489c-89d7-9fc2bd21f894`，启动于 2026-08-28 18:24 |
| 活跃子进程 | `859836` = `UAPP_FORMAL_RUN_v1.0.py UAPP-INTENT-01`（起 07:19:37）<br>`859889` = `UAPP_FORMAL_RUN_v1.0.py UAPP-INTENT-02N`（起 07:19:44） |
| 冻结环境变量 | `UAPP_ATTEMPT=40e45858`，`UAPP_SCENARIOS_VERSION=v2.0` |
| 旧终端自身等待器 | `860176`，`until [ -f …attempt40e45858.json ]; do sleep 15; done` |

本终端处置，逐条对应 §3.2：

- **未启动第二写入者**：R0 完成前对 Git、Dify、M2 零写入。
- **未 kill 任何未获授权的进程**：全程只读 `ps` / `/proc/<pid>/cwd` / `kill -0` 存活探测。
- **只读观察其运行至结束**：`859889` 退出于 07:24 前后（证据 07:24:27 落盘），
  `859836` 退出于 **07:29:12**；两次正式运行**均自然跑完并落盘**，
  非中断、非超时、非本终端干预。
- **但旧终端本体未结束**：会话 `403572` 在子进程退出后继续工作，
  于 07:36:34 提交并推送。详见 §5.1。

### 2.1 本终端零成本声明

`workflow_runs_initiated_this_terminal = 0`
`deepseek_llm_attempts_initiated_this_terminal = 0`

`attempt 40e45858` 的 3 个 workflow run 与其模型调用**全部由旧终端发起**，
本终端只读取其落盘结果，未重试、未重采样。

---

## 三、保全内容

### 3.1 凭据与缓存扫描

- 变更与未跟踪任务文件全量扫描 `sk-*` / `api_key=` / `Bearer` / `app-*` / `password=`：**零命中**。
- `__pycache__/` 已由仓库 `.gitignore:25` 覆盖，porcelain 中零 `.pyc`：非证据缓存不会混入交付。

### 3.2 受保护面基线冻结

落盘 `unified-app/evidence/UAPP_R0_PROTECTED_BASELINE.json`，含 11 个 Dify 应用的
`graph_md5` / 节点数 / 边数，作为 successor 每层 Stage Gate 的比对锚点。

**零漂移复核**：受保护旧 Founder Canvas `f0b1c5f5…` 的 `graph_md5 = 67b717d1365c2fb75a3b8e761b0527da`，
与 `UAPP_PROVIDERS_CREATED.json` 内先前登记的 `old_canvas_graph_md5` **逐字节一致**。

**任务 provider 目标复算**：`diyu_uapp_m3 → a4c3b19b…`、`diyu_uapp_seam → 5fca0162…`，
与 Task Contract `source_of_truth.final_fp_bindings` 一致，可作 successor 复用输入。

### 3.3 旧候选原样保留

app `2448e4f9…`（69 节点 / 81 边，最新发布版本 `b342cde3…`）**不删除、不覆盖**，
`disposition = LEGACY_DIAGNOSTIC_CANDIDATE_NOT_ACCEPTED`，不再作为最终候选施工面。

---

## 四、FAILURE TRIAGE · 旧候选自然语言路由（诊断域）

本节结论**只作为 successor 的设计输入**，不占 successor 任何正式验收位；
按 Rebase Prompt §2.3，旧图上的 UAPP-AC 对 successor 一律 `STALE` 或 `NOT_VERIFIED`。

### 4.1 observed_failure

由 `attempt 40e45858` 与 `attempt 00d9dcdd` 的 `workflow_node_executions` 重推，
非模型自述、非"跑通了"：

| 用例 | attempt 00d9dcdd (graph `5888f71b…`) | attempt 40e45858 (graph `2e608e4d…`) |
|---|---|---|
| INTENT-01 T1 | `CAPABILITY/MATRIX`，来源 `canvas_triage`，`uapp_m3`+`uapp_hop`+`uapp_seam` succeeded，泄漏 0 | 同左 |
| INTENT-01 T2 | 同上，未退回对话 | 同上；正文与 T1 **逐字相同** |
| INTENT-02N N1 | `DIALOGUE`，`intent=""`，`intent_source=none`，**无任何能力执行** | `CAPABILITY/CREATIVE_SCRIPT`，**跑了 m3+hop+seam** |

对照 `UAPP_FROZEN_SCENARIOS_v2.0.json` 的冻结判据：

- INTENT-01：两轮均满足「能力真实执行 + 落点在 `accepted_capabilities_T1` 内 + 零泄漏」→ 判据成立。
- INTENT-02N：判据明写 `本轮不调用任何专业能力`。`40e45858` 调用了 → **该负例判据不成立**。

### 4.2 frozen_target

「明确意图直接执行；真正歧义只问一个决定性问题」
（Founder 裁定 `UAPP_INTENT_ROUTING_001` 第 3 点）。

### 4.3 confirmed_origin

`SYSTEM_UNDER_TEST` —— 具体为**统一 Canvas 的分诊台 `uapp_action` 的结构化输出**，
有独立证据，不是 Checker、不是 Fixture、不是环境：

`attempt 00d9dcdd` 的 `uapp_action.structured_output` 原文里，
`last_route_intent` 字段被整段英文推理串占据（"…That might be an internal routing state.
We can't rely on it. … Now intent: Could be AMBIGUOUS? …"），
而 schema 要求的 `action` / `intent` **一个都没输出**。
`uapp_route` 因此取到 `intent=""`、`action` 缺失，`_salvage_action` 亦无可捞，落 `DIALOGUE`。

模型当时正在推理向 `AMBIGUOUS`，但决定字段从未产出。

把 `max_tokens` 由 800 提到 4000 后（`40e45858`），输出不再被截断，
却改为**自信地判定 `CREATIVE_SCRIPT`**。**失败面被搬了位置，没有被消除。**

### 4.4 由此确定的两条 successor 必须证明的事

| 编号 | 事实 | 当前状态 |
|---|---|---|
| R0-F1 | `intent = AMBIGUOUS` → `uapp_ask_one` 这条路径，在**任何一次正式运行中从未触发过** | 未经证明的代码 |
| R0-F2 | 空头支票守卫 `CHAT_GUARD_SRC` 的「要不要请对应的专业能力」两条模式，源码内已修正（本终端对当前源码离线实测，两条模式均命中）；但 `40e45858` 走了 CAPABILITY 分支，守卫**自修正后从未被执行过** | 源码已修，运行未验证 |

R0-F1 直接决定 Rebase Prompt §5 的 `S1-NEG-01` 判据设计：
successor 的负控制必须真正把 `uapp_ask_one` 跑起来，否则该层负例没有判别力。

### 4.5 次要观察

`attempt 40e45858` 三轮全部返回同形缺口问句，无一轮给出有内容的账号经营诊断。
成因是每个正式运行新建测试域，M2 内无可支撑诊断的业务事实。
这决定 successor 的 S3：`§7` 通过条件 4「信息充分时返回有内容的账号经营诊断」
需要先备好可支撑诊断的 M2 投影，否则该条永远只能落在「信息不足」一侧。

### 4.6 mutation_target / protected_targets

本 R0 节点的 `mutation_target` 为 **空**：未修改任何被测对象。
`protected_targets`（M1 源、M2、最终 FP M3/Seam/六能力、Hop、旧 Canvas、旧 provider、main）
本节点零改动，`§3.2` 基线可复算。

---

## 五、R0 处置与解除

### 5.1 本终端一度成为第二写入者，已原样撤回

07:29:12 三个 `UAPP_FORMAL_RUN` 子进程退出后，本终端据此判定「旧写入者已结束」，
并向该 worktree 写入本文件与 `UAPP_R0_PROTECTED_BASELINE.json`、执行了 `git add -A`。

**该判定是错的。** 子进程退出不等于终端结束：写入者是 Claude Code 会话 `403572` 本身，
它随后于 **07:36:34 提交 `65a94d9` 并 push 到 `origin/codex/v1-unified-dify-application-001`**。

处置：`git reset` 撤销暂存，两个文件移出该 worktree，
`/home/faye/diyu-demo-worktrees/v1-unified-dify-application` 恢复为 `65a94d9` 干净状态，
**未提交、未覆盖任何文件、零残留**。

### 5.2 Founder 裁决解除并发阻塞

Founder 于本轮明确指示：

> 你可以新建空白画布应用进行渐进式集成，所有模块都有对应的 DSL 文件，你后台导入，即可；**在独立工作区执行**

解除方式不是旧终端退出，而是**空间隔离**：新终端在独立 worktree 与独立分支上施工，
旧终端继续持有它自己的 worktree 与分支，两者不再写同一路径。

`403572` 在本文件落盘时**仍存活**，其 worktree 与分支归它，本终端不再触碰。

### 5.3 独立工作区

```text
worktree = /home/faye/diyu-demo-worktrees/v1-uapp-progressive-canvas
branch   = codex/v1-uapp-progressive-canvas-001
base     = 65a94d9bdaa75e7c6a7c7dbb282d894b5049de1a（继承全部任务资产与旧终端最新提交）
legacy   = /home/faye/diyu-demo-worktrees/v1-unified-dify-application @ codex/v1-unified-dify-application-001（旧终端持有，本终端只读）
```

Dify 侧共享，因此**受保护面基线（§3.2）继续是硬约束**：successor 施工全程不得改动
旧 Canvas、旧候选 app `2448e4f9…`、FP 八应用、Hop 与 M1 源应用；每层 Stage Gate 与
`UAPP_R0_PROTECTED_BASELINE.json` 比对。

### 5.4 结论

```text
r0_concurrent_writer_gate = CLEARED_BY_FOUNDER_WORKSPACE_ISOLATION
r0_old_terminal_alive     = TRUE（403572；其 worktree 与分支不属本终端）
r0_wip_preserved          = TRUE（旧终端自行提交 65a94d9；本终端零覆盖）
r0_credentials_scanned    = CLEAN
r0_protected_baseline     = FROZEN（11 个应用 graph_md5）
r0_old_candidate          = RETAINED_AS_DIAGNOSTIC
execution_disposition     = CONTINUE
task_final_status         = null
next_stage_allowed        = true（进入 Node S1）
```

R0 通过，下一动作为 **Node S1：新建空白 advanced-chat successor 画布，部署 M1 与自然语言路由契约**。
构建方式按 Founder 指示走 DSL 导入（`POST /console/api/apps/imports`，带 `app_id` 就地更新同一应用）。
