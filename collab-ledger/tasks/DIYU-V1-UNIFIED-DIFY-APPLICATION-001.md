# 任务分区账本 · `DIYU-V1-UNIFIED-DIFY-APPLICATION-001`

> 规则正文见 [../COLLAB_CONTINUITY_PROTOCOL.md](../COLLAB_CONTINUITY_PROTOCOL.md)。本文件是 canonical §一
> 所说的**任务分区**：五本账里只留一行定位，任务的高频运行状态写在这里。

---

## L1 · 合同与边界（历史留痕，只加不改）

| 项 | 值 |
|---|---|
| `task_id` | `DIYU-V1-UNIFIED-DIFY-APPLICATION-001` |
| `entry_mode` / `task_type` / `risk_level` | `NEW_TASK` / `MIXED` / `HIGH` |
| Root Execution Prompt | `DIYU_V1_UNIFIED_DIFY_APPLICATION_ROOT_EXECUTION_PROMPT_v1.0.md`，`sha256 = 4b72d4ec84814fff9bf7a861f75f63c7351af01bb64bb81ea0d8dd296e11a893`（**现场复算通过**） |
| Task Contract | `DIYU_V1_UNIFIED_DIFY_APPLICATION_TASK_CONTRACT_v1.0.yaml`，`sha256 = 279f80ba09f9ec4fea53c71c829054276b4baa30071df7305f2f3fbf921e869f`（**现场复算通过**） |
| Continue Prompt | `DIYU_V1_UNIFIED_DIFY_APPLICATION_CONTINUE_EXECUTION_PROMPT_v1.0.md`，`sha256 = c2cb867bfca68ef0d8ab56d2a4ae5a4a366f2a1572887ac948c14317cfc8d092` |
| 授权事件 | Founder 2026-08-29「要集成在一个应用中；基于最佳工程实践，输出执行 prompt」→ 注入 Root Prompt 与 Task Contract；后续「推进后续集成，输出执行 prompt」注入 Continue Prompt |
| 父任务 | `DIYU-V1-M5-UNIFIED-INTEGRATION-FINAL-ACCEPTANCE-001`，`DONE`，final commit `01a42b0` |
| 起算基线 | `origin/main @ 01a42b0ed97344a67302ecb6778ae4a772eb28b2` |
| 任务分支 | `codex/v1-unified-dify-application-001` |
| worktree | `/home/faye/diyu-demo-worktrees/v1-unified-dify-application` |
| 允许变化面 | 新建并发布统一 Dify 应用｜新建任务命名 provider｜任务域测试数据写入｜测试/模拟发布记录｜验收判据、证据与本分区账本｜任务分支提交与常规推送 |
| 受保护资产 | 旧 Founder Canvas 与旧 provider｜final FP M3／Seam／六能力应用的 graph/model/prompt/Skill｜M1–M5 已接受产物与 M5 的 `DONE`｜`main` 与 `origin/main`｜非测试数据｜凭据｜真实内容平台 |
| 验收口径 | `UAPP-AC-01..12`（Task Contract `acceptance_contract`） |
| `allowed_final_states` | `INVALID` / `DONE` / `BLOCKED` / `FAILED`　**`PARTIAL` 不在集内** |
| `done_formula` | `UAPP-AC-01..12 全部 PASS/CURRENT AND Founder ACCEPT AND 无适用 P0 FAIL AND Git/远端/Dify/DSL/回执一致` |
| `no_terminal_state_before_formula` | `true` |
| `normal_commit_and_push_task_branch` | `AUTHORIZED` |
| `main_merge_and_push` | `CONDITIONALLY_AUTHORIZED_AFTER_UAPP_AC_01_TO_12` —— **条件当前不成立** |
| `force_push` / `remote_branch_delete` | `PROHIBITED` |
| `real_external_publish` | `PROHIBITED`（测试/模拟发布记录已授权） |
| `blind_resampling_allowed` | `false` |

---

## L2 · 当前状态与下一动作（当前投影，可替换）

```yaml
task_id: DIYU-V1-UNIFIED-DIFY-APPLICATION-001
task_progress: IN_PROGRESS
terminal_state: UNSET            # 合同 no_terminal_state_before_formula=true，公式不成立
checkpoint: 意图路由桥接已修并复验；歧义负例未成立，停在 Founder 裁决门
founder_adjudication: FOUNDER_ADJUDICATION_UAPP_INTENT_ROUTING_001 = RETURN（2026-08-29）
app_id: 2448e4f9-818f-4b88-9311-d18546e97da9
graph_sha256_manifest: 40e4585825bb7d211f357d89136cb2294936ca54287333fef49b6f74e5b64f2b
graph_nodes: 69
graph_edges: 81
deterministic_checks: 32 PASS / 0 FAIL
ac_pass_current:   [UAPP-AC-01, UAPP-AC-10, UAPP-AC-11]
ac_fail:           [UAPP-AC-02, UAPP-AC-03, UAPP-AC-05, UAPP-AC-06, UAPP-AC-07]
ac_return:         [UAPP-AC-12]
ac_not_verified:   [UAPP-AC-04, UAPP-AC-08, UAPP-AC-09]
open_technical_debt: 16          # TD-UAPP-01..16，主表 v1.2
main: 01a42b0ed97344a67302ecb6778ae4a772eb28b2          # 未动
origin_main: 01a42b0ed97344a67302ecb6778ae4a772eb28b2    # 未动
force_push: NONE
```

**Founder 裁定的解禁条件未成立。** 裁定点名三条用例，过了两条：
`UAPP-INTENT-01` 的 T1／T2 双双 `PASS`（意图路由真的通了），
`UAPP-INTENT-02N` 能力歧义负例 `FAIL`。按裁定原文
「`AC-02`、`AC-05`、`AC-06` 和 `AC-12` 保持 `FAIL`/`RETURN`，直到上述路径复验成立」，
四项照旧保持，**执行侧不因为主路通了就把它们提上去**。

**AC-04 重新变回 `STALE`**：六项能力的 `PASS` 绑在图 `c95ffbe4…`，本轮为修路由改了图。
每改一次图，绑定旧图的模型面结论都要重算；现在有 TD-UAPP-09 的图绑定检查会自己拦。

**下一动作**（四样齐全）：

| 项 | 值 |
|---|---|
| 做什么 | 取得 Founder 对 **TD-UAPP-16** 的裁决：「这条我想再打磨一下」到底算不算「确实存在能力歧义」。① 若不算 → 需另出判据版本换一条真有歧义的输入；② 若算 → 分诊台压反问压得过头，需调其倾向。两条路都改变后续工作，执行侧无权自选 |
| 对哪个对象 | `app_id = 2448e4f9-818f-4b88-9311-d18546e97da9`，图 `40e45858…` |
| 输入／基线 | 分支 `codex/v1-unified-dify-application-001` 本次提交；判据 `518eac03…`（v2.0）；Manifest v1.8 `5041c515…` |
| 什么信号算做完 | 三条定向用例全部 `PASS` → Founder 裁定的解禁条件成立 → AC-02/05/06 可回升；AC-12 仍须 Founder 在 UI 重新实测后自行判定 |

**同时未决（继承自上一轮，未被本轮触碰）**：TD-UAPP-01（FULL-01 首轮不稳定）、
TD-UAPP-03（是否改 M1 已接受的对话语义）。**TD-UAPP-03 本轮是被绕开，不是被解决**——
`uapp_ask_one` 让 Canvas 自己出那一个问题，M1 对话节点一个字未改，缺陷原样存在。

---

## L3 · 正式尝试与验收证据（历史留痕，只加不改）

判据 `UAPP_FROZEN_SCENARIOS_v1.0.json` sha256 `c45c46686aedc7f4c5971653496aa8038460147ae097f8bc335a26cfd1b1b7f6`，
**全程一字未改**，且**先于**每一次正式运行冻结。Manifest 历次版本 v1.0…v1.5，各代证据按版本归档。

| Attempt | 用例 | 图（psql 口径） | 结果 | 证据 |
|---|---|---|---|---|
| A1 | `UAPP-CAP-01..06` | `f36e788d…` | 六例 `PASS` → 图改动后按 A3 置 `STALE` | `unified-app/evidence/formal/UAPP-CAP-0N.json` |
| A2 | `UAPP-FULL-01` ×4 代 | 各代不同 | `FAIL`（T1 交付不稳定；T2/T4 曾 HTTP 400） | `unified-app/evidence/formal_v1.0_stale/` … `formal_v1.3_stale/` |
| A3 | `UAPP-GAP-01` | `f36e788d…` | 机器初判 `PASS` → **人工读正文推翻**，判 `FAIL` | `unified-app/evidence/formal/UAPP-GAP-01.json` |
| A4 | `UAPP-WITHDRAW-01` | `e509b550…` | 机器初判 `PASS` → **裁定器补 WD-03 后更正为 `FAIL`**，原记录保留 | `unified-app/evidence/formal/UAPP-WITHDRAW-01.json` |
| A5 | `UAPP-CAP-01..06` 定向复验 | `2349143f…`（当前图） | **六例全部 `PASS`** | `unified-app/evidence/formal/UAPP-CAP-0N_attemptc95ffbe4.json` |
| A6 | `UAPP-INTENT-01` / `02N` | 图 `00d9dcdd…`（首跑） | **三轮全 HTTP 400**：代码节点输出类型不符（TD-UAPP-12） | `unified-app/evidence/formal/UAPP-INTENT-0*.json` |
| A7 | `UAPP-INTENT-01` | 图 `00d9dcdd…` | **`PASS`**（IR-01…07 全过） | `..._attempt00d9dcdd.json` |
| A8 | `UAPP-INTENT-02N` | 图 `00d9dcdd…` | `FAIL`：分诊台被截断，静默落到对话（TD-UAPP-13） | `..._attempt00d9dcdd.json` |
| A9 | `UAPP-INTENT-01` 定向复验 | 图 `40e45858…`（最终图） | **`PASS`**，与 A7 结论一致 | `..._attempt40e45858.json` |
| A10 | `UAPP-INTENT-02N` 定向复验 | 图 `40e45858…` | **`FAIL`**：直判 `CREATIVE_SCRIPT` 就跑，未走「只问一个」（TD-UAPP-16） | `..._attempt40e45858.json` |

- 确定性判据 D-01..D-32：当前图上 **32 PASS / 0 FAIL**，零模型调用，`unified-app/evidence/UAPP_DETERMINISTIC_CHECKS.json`
  （本轮新增 D-25…D-32，逐条对应 Founder 裁定的四条硬要求，且每条都在修复前的图上先报过 FAIL）
- 第二份冻结判据：`unified-app/docs/UAPP_FROZEN_SCENARIOS_v2.0.json` sha256 `518eac03…`，
  冻结于本轮任何一次运行之前，全程一字未改
- Founder 裁定登记：`unified-app/docs/UAPP_FOUNDER_ADJUDICATION_001_INTENT_ROUTING.md`
- 裁定结果：`unified-app/evidence/UAPP_ADJUDICATION.json`
- 证据索引（逐文件哈希，74 个文件）：`unified-app/docs/UAPP_EVIDENCE_INDEX_v1.1.json`
- 技术债主表：`unified-app/docs/UAPP_TECHNICAL_DEBT_REGISTER_v1.2.md`（v1.0 / v1.1 为历史版本，保留不改）
- 任务分支收口记录：`unified-app/docs/UAPP_CLOSEOUT_RECORD_v1.0.md`
- DSL：`unified-app/dsl/UAPP_UNIFIED_FOUNDER_CANVAS_v1.0.yml` sha256 `57f035c4…`

**从未运行**：`UAPP-EQUIV-01a/b/c/n`、`UAPP-RECOVERY-01` —— `NOT_VERIFIED (ABSENT)`，不是通过也不是失败。

**A5 不是重复采样**：它是 A3（失效传播）要求的定向复验——绑定对象（图）变了，
旧结论按律置 `STALE`，须在新对象上重算。同一输入在同一张图上仍然只跑一次。
`blind_resampling_allowed = false` 未被违反。

---

## L4 · 已排除路线（历史留痕，只加不改）

| 路线 | 为什么排除 | 证据 |
|---|---|---|
| 在画布里重新实现 M1 编译逻辑 | 会产生第二份语义真源。改为**逐字节复用 M1 子图并保留节点 id**，内部 `value_selector` 全部继续有效 | D-03 图内源码与仓库源码逐字节一致 |
| 把六份专业语义复制进画布 | 合同明令禁止，且会与 final FP 应用形成双真源 | 合同 §4.2 |
| 预置序里集夹具为「已登记业务事实」 | 会给每个账号塞进别家品牌的商品。事实只来自用户上传与 M1 `evidence_bundle` | 项目 `CLAUDE.md` §4「不预选序里集的四个账号」「不补写夹具未提供的经营事实」 |
| 靠重复采样把 `UAPP-FULL-01 / T1` 刷成通过 | `blind_resampling_allowed = false`；根因未定位前加样本量只是掩盖 | 合同 `retry_and_cost_policy` |
| 用 assigner 节点直接引用条件分支里的变量 | Dify 代码节点容忍缺失上游变量，**assigner 不容忍**，直接抛 `Variable not found` 并 HTTP 400 | `UAPP-FULL-01` T2/T4 400；修复为 `variable-aggregator` 汇合 |
| 撤回轮调用 M3 | M3 手上没有素材事实，会诚实地报「查不到」，与画布随后真实执行的撤回**正好相反**，拼成自相矛盾的交付 | TD-UAPP-04 |
| 用「节点自述的泄漏计数」判 AC-10 | 失败分支上投影节点根本不运行，「没测到」会被读成「没泄漏」 | 裁定器 X-01 改为扫真实答复正文 |
| 用全库行数判本任务的写入 | 库内有 1568 条 M0-M5 既有非测试发布行，等于拿别的任务的数据给本任务定罪或脱罪 | 裁定器改为限定本任务 workspace |
| 让路由只读 M1 的 `needed_capabilities` | 那是「用户点名了哪个」的登记表，不是意图分类器。用户不点名就永远进不了能力 | Founder 实测 + `evidence/UAPP_RUN_diag_intent01.json` |
| 为了让自然语言能路由而去改 M1 编译器 | 根因不在 M1：它已经在 `per_capability` 里给出六项 `reachable_if_requested: true`，信息足够，缺的是桥 | 同上；Founder 裁定明令未证明必要前不得改 M1 |
| 靠 M1 对话节点来实现「只问一个问题」 | 该节点实测会自行扩写成一次问三件事（TD-UAPP-03），且改它属产品语义域 | 改为 Canvas 自己出题的 `uapp_ask_one`，绕开而非修改 |
| 只用键名比对来守代码节点的输出契约 | 类型不符同样会让整轮 HTTP 400，而 D-19 只比键名，放行过一次真缺陷 | TD-UAPP-12；补 D-30 |

---

## L5 · 外部副作用（历史留痕，只加不改）

| 目标 | 操作 | 状态 | 怎么核 |
|---|---|---|---|
| Dify（自托管） | 新建并发布应用 `DIYU V1 · Unified Founder Canvas` | 已发布 | `app_id = 2448e4f9-818f-4b88-9311-d18546e97da9`，65 节点 / 77 边 |
| Dify | 新建三个任务命名 provider：`diyu_uapp_m3` / `diyu_uapp_hop` / `diyu_uapp_seam` | 已建 | `unified-app/evidence/UAPP_PROVIDERS_CREATED.json`；D-06 / D-07 |
| Dify | 旧 Canvas、旧 provider、final FP 八应用、hop 适配器 | **零改动** | D-08 逐条比对 `PROTECTED_BASELINE`，漂移 `none` |
| M2 `diyu_business` 库 | 任务域测试写入：工作区 / 账号 / 周期 / 任务 / 素材 / 产物 / 版本 / 发布 / 反馈 / 撤回 | 部分成功、部分失败，全部如实记录 | 写入全部显式 `is_test=true` + `is_simulated=true`（D-14）；行数限定在 `ws-uapp-*` 工作区内统计 |
| M2 库既有的 1568 条非测试发布行 | **未触碰** | 属 M0-M5 既有数据 | 与本任务无关，裁定器已把统计限定在本任务 workspace |
| 真实内容平台 | **从未连接、从未发布** | —— | 合同 `real_external_publish: PROHIBITED` |
| `main` / `origin/main` | **未动** | 停在 `01a42b0` | `main_merge_and_push` 条件不成立 |
| 凭据 | 未落盘、未打印、未提交 | —— | DSL 按 `include_secret=false` 导出并做过凭据扫描，零命中 |
