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

### 2026-08-29 · 渐进候选 S4 后继窄验证前登记（当前投影，取代上一块；上一块原文保留不改）

> 上一块投影绑定的是**旧候选** `2448e4f9`／图 `40e45858…`。自 `657004c` 起本任务转入
> **REBASE 渐进候选**，在新建空白画布上逐层部署 M1→M5，账本此前未跟上——本次补齐。

```yaml
task_id: DIYU-V1-UNIFIED-DIFY-APPLICATION-001
task_entry_mode: CONTINUE_TASK
task_contract_hash: 279f80ba09f9ec4fea53c71c829054276b4baa30071df7305f2f3fbf921e869f
task_progress: IN_PROGRESS
terminal_state: UNSET
checkpoint: S4 Gate 4 定向链 1 PASS / 3 FAIL，停在 content_origin_mode 缺口；Founder 裁定 002 已登记，授权一次六轮连续验证
founder_adjudication: UAPP-FOUNDER-ADJUDICATION-002 = content_origin_mode 精确追问判 PASS（2026-08-29）
successor_app_id: 85c01f85-a081-43e9-ab09-9993289cc200
graph_sha256: f75555c0d6552a0894975242ef3fad7a5351ca63ce4404915c0ee1f71d8f3927
graph_nodes: 46
graph_edges: 48
branch: codex/v1-uapp-progressive-canvas-001
branch_pushed: NEVER
main: 01a42b0ed97344a67302ecb6778ae4a772eb28b2          # 未动
main_merge: NOT_ALLOWED
stage_status:
  S1: PASS / CURRENT
  S2: PASS / CURRENT
  S3: PASS / CURRENT
  S4.1: PASS / CURRENT
  S4.2: FAIL（v1.2 判据下 CONTENT_BRIEF-POS PASS，CS/PD/PP-POS 各 FAIL 10/11；五负例与 CAMPAIGN-POS 绑 v1.1，判定器标 OUT_OF_SCOPE_GATE_MISMATCH）
  S4_CONTENT_ORIGIN_CONTINUATION: NOT_RUN（本次授权范围）
  S5: NOT_STARTED / NOT_AUTHORIZED
```

**Founder 裁定 002 改变了什么、没改变什么。**
改变：`content_origin_mode` 的精确追问本身判 `PASS`，并给出本次场景的用户回答。
没改变：Gate 4 的历史 `FAIL` 一条不改绿，`S4_2_STAGE_GATE_v1.2.json` 一个字节不动，
S4／UAPP／M5 一律不上行。登记见
[`unified-app/docs/UAPP_FOUNDER_ADJUDICATION_002_CONTENT_ORIGIN_MODE.md`](../../unified-app/docs/UAPP_FOUNDER_ADJUDICATION_002_CONTENT_ORIGIN_MODE.md)。

**下一动作**（四样齐全）：

| 项 | 值 |
|---|---|
| 做什么 | 跑**一个全新会话、六轮冻结输入**，验证补齐 `content_origin_mode` 之后 CS→PD→PP 能否沿同一会话继续产出 |
| 对哪个对象 | `app_id = 85c01f85-a081-43e9-ab09-9993289cc200`，图 `f75555c0…`（本阶段禁止改图） |
| 输入／基线 | 判据 `S4_CONTENT_ORIGIN_CONTINUATION_GATE_v1.0.json`、冻结输入 `..._INPUTS_v1.0.json`，均冻结并提交于**首次调用之前** |
| 什么信号算做完 | 12 项条件全部成立 → `S4_CONTENT_ORIGIN_CONTINUATION = PASS / CURRENT`，**只**关闭「回答素材来源后是否续跑」这一窄问题；任一硬门失败 → 输出 FAILURE TRIAGE 并停，不启动第二轮 |

**明确未授权**：十例全套重跑、CAMPAIGN 重跑、v1.2 负例身份对齐回归、第二次接缝修复、
改图／Checker／Fixture、进入 S5、合并 `main`。

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


### `ATT-S4-CO-01` · 素材来源裁决后的连续链（**预登记，调用之前**）

| 项 | 值 |
|---|---|
| 授权 | `DIYU_V1_UAPP_S4_CONTENT_ORIGIN_CONTINUATION_EXECUTION_PROMPT_v1.0.md` + `UAPP-FOUNDER-ADJUDICATION-002` |
| 判据 | `unified-app/stages/S4_CONTENT_ORIGIN_CONTINUATION_GATE_v1.0.json` |
| 冻结输入 | `unified-app/stages/S4_CONTENT_ORIGIN_CONTINUATION_INPUTS_v1.0.json`（六轮逐字取自 Prompt §4，已确定性比对一致） |
| 运行器 | `unified-app/workflows/S4_CONTINUATION_RUN_v1.0.py`（只发起、只记录） |
| 判定器 | `unified-app/workflows/S4_CONTINUATION_ADJUDICATE_v1.0.py`（零模型调用） |
| 证据路径 | `unified-app/evidence/stages/s4_continuation01/S4-CO-T1..T6.json` |
| 调用上限 | 新会话 1 个、冻结轮次 6 轮、每轮 1 次；计划外追问 0；仅纯传输失败且无任何模型输出时最多重试一次 |
| 结果 | **待填**——本行在任何调用之前写入，不预写成功 |

**判定器判别力（运行之前，零模型调用）**：合成正控制 11/12 `PASS`
（`C12` 依赖真实 M2 行数，合成证据无法伪造，属已知覆盖缺口）；
11 个单点变异负控制**逐条触发对应条件**，`C03`/`C08` 与 `C07`/`C08` 的连带命中是语义重叠，不是误判。
控制件只存在于 scratchpad，从不进入仓库证据目录，也从不参与真实判定。

### S1–S4 渐进候选历次 Attempt（补登，只加不改）

| Attempt | 范围 | 图 | 结果 | 证据 |
|---|---|---|---|---|
| S1 | 空白画布 + M1 逐字节复用 | — | `PASS / CURRENT` | `unified-app/stages/S1_RESULT.json` |
| S2 | M1→M2 接缝 | — | `PASS / CURRENT`（判据 v1.1） | `S2_RESULT.json` |
| S3 | M2→M3→用户返回 | — | `PASS / CURRENT` | `S3_RESULT.json` |
| S4.1 | 一条完整能力链 | — | attempt01 `FAIL` → 定向修复后 `PASS / CURRENT`（判据 v1.1，零放宽） | `S4_1_RESULT.json` |
| S4.2 attempt01 | 十例逐能力 | `6f3d3e53…` | **十例全 `FAIL`** → 归因 `CHECKER_OR_FIXTURE`：夹具上传双重编码 | `evidence/stages/s4_2_attempt01/`、`docs/S4_2_FAILURE_TRIAGE_001.md` |
| S4.2 attempt02 | 十例逐能力 | `6f3d3e53…` | `FAIL` → 归因 `ORACLE_OR_CRITERION`（判据断言了未验证的 M1 内部机制）与「下游能力冷启动无『这条』」 | `s4_2_attempt02/`、`TRIAGE_002` |
| S4.2 attempt03 | 多轮链 + CAMPAIGN | `6f3d3e53…` | `FAIL` → 归因 `INPUT_ENVIRONMENT_OR_TOOL`：上传是轮次作用域，被测轮次实际未带夹具 | `s4_2_attempt03/`、`TRIAGE_003` |
| S4.2 attempt04（Gate 4） | 定向链 POS | `f75555c0…` | **1 `PASS` / 3 `FAIL`**：CONTENT_BRIEF-POS 11/11 通过；CS/PD/PP-POS 各 10/11，唯一未过项是「正例交付含实质内容」 | `s4_2_attempt04/`、`TRIAGE_004`、`S4_2_CHECKPOINT_001.md` |

**跨轮状态接缝最小修复（授权一次，已完成）**：画布缺 `uapp_save` 写入节点，
读方已接、写方未建，`uapp_last_artifact` 每轮为空。修复后 Gate 1 会话变量读写闭包 16/16 `PASS`、
Gate 2 跨轮载体检查通过、Gate 4 实测 `upstream_delivery` 由 0 变 5593、CREATIVE_SCRIPT 缺口由 7 项塌缩到 1 项。
影响面与**次序偏差的如实披露**见 `unified-app/docs/S4_ASSIGNER_REPAIR_IMPACT_v1.0.md` §0。


### `ATT-S4-CO-01` · 实际结果（追加，不改上面的预登记行）

```text
S4_CONTENT_ORIGIN_CONTINUATION = FAIL    6 PASS / 6 FAIL / 0 NOT_VERIFIED
```

判定书：[`unified-app/docs/S4_CONTENT_ORIGIN_CONTINUATION_ADJUDICATION_001.md`](../../unified-app/docs/S4_CONTENT_ORIGIN_CONTINUATION_ADJUDICATION_001.md)
（sha256 `c374b819…`）｜机器判定原文 `unified-app/stages/S4_CONTENT_ORIGIN_CONTINUATION_RESULT_v1.0.json`（`a987eeed…`）
｜六轮证据 `unified-app/evidence/stages/s4_continuation01/S4-CO-T1..T6.json`

| 项 | 值 |
|---|---|
| 成立 | C07 不暗跑、C08 Brief 不重做且事实不漂移、C09 无越权授权声明、C10 零泄漏、C11 受保护面零漂移、C12 幂等 |
| 不成立 | C01–C06，全部是**同一个根因的级联**：T2 的 Content Brief 没产出 artifact，下游逐层拿不到上游产物 |
| 窄问题 | **没测到**。链条没走到「补齐 `content_origin_mode` 之后能否续跑」那一步——T3 问的不是这一项 |
| 归因 | `SYSTEM_UNDER_TEST`：同一冻结话术、同一图 `f75555c0…`、同一夹具 `8c21d41d…`，attempt04 的 hop 缺口为「无」并产出 5593 字，本次缺口为 `facts_registered` 并产出 0 字。抽取层对「事实登记了没有」给出两种相反判断 |
| 具体失效节点 | `INSUFFICIENT_EVIDENCE`——两次运行不足以锁到具体节点，按内核只继续诊断、不扩大修改范围 |
| 实际成本 | 画布运行 6 次（与冻结六轮一一对应）／嵌套 24 次／DeepSeek LLM 节点成功 30 次、失败 0 次／计划外追问 0／重试 0 |
| 未动 | 图、Gate、冻结输入、判定器、夹具、M1/M2/M3/Hop/Seam/六能力、旧 Canvas 与 provider |

**运行中的一次执行侧故障（非被测对象）**：首跑在 T1 `http=200` 之后崩于运行器
`conv_vars()` 的错误 SQL（表上无 `name` 列）。归因 `CHECKER_OR_FIXTURE`。
**T1 未重跑**——已真实执行完毕，重跑会让同一冻结输入跑两次；改为从 Dify 真源只读取回
（`S4_CONTINUATION_RECOVER_T1_v1.0.py`，零模型调用，文件内标 `reconstructed_from_db: true`）。
只修运行器两处（SQL、断点续跑），该字段不被任何 pass_condition 读取，不改变任何判定。

**新增技术债 TD-UAPP-17**：判定器 `gaps()` 未按全角分号切分 `precise_gap` 复合串。
不改变本次任何判定（即使完美切分 C02 仍 `FAIL`），按 `checker_or_fixture_mutation_after_run: FORBIDDEN` 本轮不修。

**新增技术债 TD-UAPP-18**：Hop 抽取判定不稳定——同一份材料两次被判成「事实已登记」与
「事实未登记」。这是本轮 `FAIL` 的根因，处置需规划侧裁定，执行侧不自选。

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

### `ATT-S4-CO-01` 的真实外部副作用（2026-08-29，追加）

| 目标 | 操作 | 状态 | 怎么核 |
|---|---|---|---|
| Dify 候选 `85c01f85` | 6 次 chat-messages 调用（冻结六轮，每轮一次） | 全部 `http=200` | `workflow_runs` 窗口内该 app 恰好 6 行 |
| Dify 嵌套应用 | M3／Hop／Seam／各能力 24 次运行 | 真实发生 | 同上，窗口内非候选 app 24 行 |
| DeepSeek | LLM 节点尝试 30 次成功、0 次失败 | 真实发生 | `workflow_node_executions` 窗口内 `node_type='llm'` |
| Dify 文件上传 | 同一份夹具上传 6 次（每轮一次，用户上传通道） | 已上传 | `upload_files`，size 6119，文件名正常 |
| M2 `diyu_business` | 测试域：workspace／account／cycle／task 各新增 1 行 | 已写入 | 窗口内计数各为 1；`task_snapshots`／`artifacts`／`publish_instances` 各 0 |
| 受保护 11 应用 + 旧候选 `2448e4f9` | **零改动** | —— | C11 逐条 md5 比对 R0 基线，漂移 none |
| 候选图 | **零改动** | 仍为 `f75555c0…` | C11 运行后复算一致 |
| 真实内容平台 | **从未连接、从未发布** | —— | `publish_instances` 窗口内 0 行 |
| `main` / `origin/main` | **未动** | 停在 `01a42b0` | `main_merge = NOT_ALLOWED` |
| 任务分支 | 首次 push 到 `origin`（非 force，未建 PR） | 已 push | `origin/codex/v1-uapp-progressive-canvas-001` |
| 凭据 | 未落盘、未打印、未提交 | —— | 提交前扫描零命中 |

---

## L2 追加 · `ATT-S4-CO-01` 之后的 CHECKPOINT（2026-08-29，非终态）

```yaml
task_id: DIYU-V1-UNIFIED-DIFY-APPLICATION-001
task_progress: IN_PROGRESS
terminal_state: UNSET
next_state: CHECKPOINT
S4_CONTENT_ORIGIN_CONTINUATION: FAIL          # 6 PASS / 6 FAIL
narrow_question: NOT_REACHED                  # 链条没走到「补齐 content_origin_mode 之后能否续跑」
successor_app_id: 85c01f85-a081-43e9-ab09-9993289cc200
graph_sha256: f75555c0d6552a0894975242ef3fad7a5351ca63ce4404915c0ee1f71d8f3927   # 运行前后一致
registration_commit: cea08c9ddb5d83952593dcf774aa4fa2a37cb582
main: 01a42b0ed97344a67302ecb6778ae4a772eb28b2          # 未动
main_merge: NOT_ALLOWED
second_repair_iteration: NOT_AUTHORIZED
enter_s5: NOT_AUTHORIZED
```

**唯一下一动作：等规划侧裁定 TD-UAPP-18（Hop 抽取判定不稳定）怎么处置。**
执行侧不自选——三条路各自改变后续工作，且都超出本 Prompt 授权：

| 路 | 内容 | 为什么需要裁定 |
|---|---|---|
| ① 先定性再修 | 用同一冻结输入做 n 次重复运行，测抽取判定的稳定率 | 需要新增运行授权与新的取证判据；本 Prompt 明令不重跑、不加样本 |
| ② 认为「追问事实登记」是正确行为，改冻结场景 | 六轮脚本改成能覆盖系统可能提出的全部缺口 | 改的是验收设计，属规划侧权威，执行侧不得改判据 |
| ③ 先修 Hop 抽取的判定稳定性 | 定位并修改抽取层 | `graph_mutation: FORBIDDEN`、`second_repair_iteration: NOT_AUTHORIZED` |

**本轮不上行任何状态。** Gate 4 的历史记录、S4.2 判据 v1.2、五个负例与 CAMPAIGN-POS 的
`OUT_OF_SCOPE_GATE_MISMATCH`、S5 的 `NOT_AUTHORIZED` 全部原样保留。

---

## `ATT-UAPP-FACT-01`（2026-08-30）｜事实充分性根因定位、最小修复与 Phase C 点对点验证

**授权**：`DIYU_V1_UAPP_FACT_SUFFICIENCY_ROOT_CAUSE_AND_MINIMAL_REPAIR_CONTINUE_EXECUTION_PROMPT_v1.0.md`
（sha256 `5d4fcbe0d5e6915314e098dd41d251d61b58bc9575106dec7e42d8e1a97496f3`）
Founder 2026-08-30 追加授权：建立 FB-07 判据后继版本；对已落盘的同一份 C1 证据做零模型调用的定向重判。

### Phase A｜第一失效节点

| | |
|---|---|
| `confirmed_origin` | `SYSTEM_UNDER_TEST` |
| `highest_failing_node` | hop `6c46fdb1` 的 `m5_compose` 代码节点 |
| 决定性证据 | 同一条会话六轮，`uapp_ctx.registered_facts` 恒非空（2367/2459/2459/2541/2541/2541），外壳 `facts_registered` 却四轮在场两轮为空；**同一次 `m5_compose` 执行**把 `registered_facts` 原样写进 `professional_input`，同时把它判成缺口 |
| 未采纳的旧结论 | 上一轮"Hop 抽取判定不稳定"，其前提"同一输入两次结论不同"被复算推翻（两次 T2 输入在四个字段上不同）。按 Prompt §0 不采纳 |

判定书：`unified-app/docs/S4_FACT_SUFFICIENCY_FAILURE_TRIAGE_FINAL_v1.0.md`

### Phase B｜一份最小连通改动（第二次修复不允许）

1. hop `m5_compose`：`facts_registered` 建立确定性下限——来源非空而抽取器留空时按来源绑定据实标为在场；**来源为空一律不合成**，充分性闸门不放松
2. 候选画布：新增 `uapp_persist` 写回闸门，空产出不再覆盖上一轮已确认产物（47 节点／49 边）
3. hop provider 版本钉重新指向新发布版

> **第 3 项是本轮最关键的一次拦截。** Dify 的 workflow-as-tool 按版本钉死取图（`core/tools/workflow_as_tool/tool.py:_get_workflow`），不是取最新已发布。不重钉的话画布仍调旧代码——**修复发布了却够不着，会造成假通过**。

确定性验证：离线 18/18 PASS；对**线上钉住代码**的集成 17/17 PASS；11 例真实载荷重放中 T2/T3 的抹除消失、其余字段判定逐例不变；负控制（来源真空）仍精确停在 `facts_registered`；九个受保护应用零漂移。

### Phase C｜三层点对点验证（判据早于结果，冻结提交 `7e0e1d1`）

| 层 | 结果 | 关键数字 |
|---|---|---|
| C1 Content Brief 受影响模块单点 | **PASS 6/6** | artifact 7975 字，`delivery_outcome=DELIVERED`，`gate_sufficiency` 通过而未停在输入不足 |
| C2 M3 → Hop → Seam → Content Brief | **PASS 8/8** | `registered_facts` 2531 字逐跳保持，hop 缺口 `无`，artifact **6188** 字（修复前同场景为 0，交付 111 字缺口追问） |
| C3 CS → PD → PP 原窄链 | **FAIL 9/13** | T4/T5/T6 artifact 均为 0 |

C3 的四条 FAIL 分属两个原因，详见 `unified-app/docs/S4_PHASE_C_C3_FAILURE_TRIAGE_002.md`：

- **原因 A（真实缺陷）** `P3-04`/`P3-05`/`P3-06`：跨轮已确认字段没有承载体。T3 精确提问 `content_origin_mode` → T4 用户回答且 hop 确实抽到 → **T5 逐字重复同一个问题、该字段又变空**。同类丢失还有 `content_promise`（T4 起恒空）与 `primary_goal`（T6 变空）。`confirmed_origin = SYSTEM_UNDER_TEST`；`highest_failing_node =` 跨轮已确认字段无承载体（画布只有 `uapp_last_artifact`／`uapp_last_capability`，hop 每轮由 `m5_extract` 从零重抽）。**不指向 `m5_extract` 的 prompt**——那是下游统计补丁。
- **原因 B（判据侧陈旧）** `P3-12`：继承的 `C11` 比对 `UAPP_R0_PROTECTED_BASELINE.json`，那是 Phase B 修复之前的基线。九应用逐个复算：**Phase C 全程零漂移**。`confirmed_origin = ORACLE_OR_CRITERION`，是冻结规格缺陷。

### 判据侧变更（Founder 授权，旧版不覆盖）

| | |
|---|---|
| `S4_PHASE_C_POINT_VERIFICATION_FREEZE_v1.1.json` | 只重写 `FB-07` 一条探针；其余判据、预算、停止规则、继承 Gate 一字未改 |
| `FB-07` v1.0 的缺陷 | 抓"职务词前后 2–3 个汉字"当人名，把夹具自身的 `零售搭配负责人` 切成不存在的人名 |
| `FB-07` v1.1 的判据 | 候选人名必须以姓氏起头（单字姓氏表＋复姓表）、2–3 字、与职务词直接相邻；在白名单内／夹具原文中逐字出现／本身是职务词一部分者不计命中 |
| 四类控制 | 合成正控制、单点负控制、历史失败回放、**反过拟合对照**（同一份真实产物注入编造人名后仍 FAIL），31/31 |
| 旧记录 | `S4_PHASE_C_RESULT_v1.0.json` 的 `P1-05=FAIL` 原样保留，不覆盖、不改绿 |

### `ATT-UAPP-FACT-01` 的真实外部副作用

| 目标 | 操作 | 冻结预算 | 实际 |
|---|---|---|---|
| 顶层 Dify workflow run | 画布 6 + Content Brief 直调 1 | 7 | **7** |
| 嵌套应用 run | M3／Hop／Seam／各能力 | ≤24 | **24** |
| DeepSeek LLM 节点 | | 预期 35／上限 44 | **32 成功、0 失败** |
| 重试 | 仅纯传输失败时允许一次 | ≤1 | **0** |
| Dify 文件上传 | 同一份夹具，每轮一次，size 6119 | 6 | **6** |
| M2 `diyu_business` | workspace／account／cycle／task | 各 1 | **各 1**；`task_snapshots`／`artifacts`／`publish_instances` 各 0 |
| 重复幂等键 | | 0 | **0** |
| 九个受保护应用 | | 零漂移 | **零漂移**（预检 C2 前、C3 前各一次，判定后一次） |
| 候选图 | | 零变更 | 仍为 `8c9788f2…` |
| 真实内容平台 | | 从未连接 | **`publish_instances` 0 行** |
| `main` / `origin/main` | | 未动 | 停在 `01a42b0` |
| 任务分支 | | 三层全 PASS 才 push | **本轮未 push**（条件未达成） |
| 凭据 | | 不落盘 | 未落盘、未打印、未提交 |

**披露**：同一 Dify 实例中第三方应用 `FCVSS`（`18dd7b02`）在 Phase C 窗口内运行 44 次并上传无关文件。与本任务九个受保护应用、候选画布、`diyu_business` 均无交集；全部判定按 `app_id` 作用域取记录；32 次 LLM 节点逐条归属核过，`FCVSS` 零占用。但运行器预检项"窗口内没有其它写入者"只打印数字未把门，缺陷一并登记。

---

## L2 追加 · `ATT-UAPP-FACT-01` 之后的 CHECKPOINT（2026-08-30，非终态）

```yaml
task_id: DIYU-V1-UNIFIED-DIFY-APPLICATION-001
task_progress: IN_PROGRESS
terminal_state: UNSET
next_state: CHECKPOINT

PHASE_A_ROOT_CAUSE: PASS / CURRENT              # 第一失效节点已定位并有证据
PHASE_B_MINIMAL_REPAIR: PASS / CURRENT          # 离线 18/18、线上集成 17/17
PHASE_C_C1_MODULE: PASS / CURRENT               # 6/6
PHASE_C_C2_ADJACENT_SEAM: PASS / CURRENT        # 8/8
PHASE_C_C3_NARROW_CHAIN: FAIL                   # 9/13

FACT_SUFFICIENCY_CHAIN_REPAIR: NOT_UPGRADED     # 冻结规格要求三层全部成立
S4_CONTENT_ORIGIN_CONTINUATION: NOT_UPGRADED    # 同上；旧 FAIL 记录原样保留

successor_app_id: 85c01f85-a081-43e9-ab09-9993289cc200
graph_sha256: 8c9788f293fa7750bea451bd2195ddfb4df7c2647ca00c383ec7c096a4cdc2d1
hop_provider_pinned: "2026-08-30 03:38:31.449618"
pinned_m5_compose: 6474b902c81c7d91fe8f6143c0a3ece9bbde55dc58b64a822e595b088f2ee855
freeze_commit: 7e0e1d1b586c30b2251115b4dca7a3ac2d8c3d7b
main: 01a42b0ed97344a67302ecb6778ae4a772eb28b2      # 未动
main_merge: NOT_ALLOWED
task_branch_push: NOT_DONE_THIS_ROUND             # 条件是三层全 PASS
second_repair_iteration: NOT_AUTHORIZED
enter_s5: NOT_AUTHORIZED
```

**唯一下一动作：等规划侧对两件事各自裁定。**

| # | 事项 | 归因 | 为什么执行侧不自选 |
|---|---|---|---|
| 1 | 跨轮已确认字段的承载与合成规则 | `SYSTEM_UNDER_TEST` | `second_repair_iteration: NOT_AUTHORIZED`；且承载什么、由谁确认、能不能跨任务，是产品语义，属规划侧权威 |
| 2 | `P3-12` 继承判据引用的受保护基线陈旧 | `ORACLE_OR_CRITERION` | 改的是验收判据；且要先裁定 HOP 修复后的新 md5 是否成为新基线 |

### 技术债后继登记

| ID | 状态 | 内容 |
|---|---|---|
| `TD-UAPP-18` | 后继：`FACT_SUFFICIENCY_CHAIN_INCONSISTENCY` **已关闭** | 本轮定位到 `m5_compose` 并修复，C1/C2 实测验证。`confirmed_origin` 由 `INSUFFICIENT_EVIDENCE` 上行为 `SYSTEM_UNDER_TEST`，触发事件是 Phase A 的自足证据 |
| `TD-UAPP-19` | 新增 | Phase A 登记的放大器：`uapp_save` 无条件写回。本轮已由 `uapp_persist` 闸门修复，C2/C3 的 `P3-07` PASS 证实 |
| `TD-UAPP-20` | **新增，未修** | 跨轮已确认字段无承载体，多轮链路结构上无法走完。证据 `S4_PHASE_C_C3_FAILURE_TRIAGE_002.md` |
| `TD-UAPP-21` | **新增，未修** | `P3-12` 继承判据引用 Phase B 之前的受保护基线，与已授权修复自相矛盾 |
| `TD-UAPP-22` | **新增，未修** | 运行器预检"窗口内没有其它写入者"只打印数字未把门 |

---

## `ATT-UAPP-FIELD-01`（2026-08-30）｜TD-UAPP-20/21/22 最小修复与受影响连续链验证

**授权**：规划侧 CONTINUE_TASK 裁决（2026-08-30）。`second_repair_iteration = AUTHORIZED_ONCE_FOR_TD-UAPP-20_ONLY`；任务分支 push 不再以三层全 PASS 为前置。

### 修复内容（一次，最小连通）

| | |
|---|---|
| 会话载体 | `uapp_task_fields`——本内容任务已确认字段的结构化载体，按 `task_key` 作用域 |
| 确定性节点 | `uapp_fields`，接在 `uapp_hop` 与 `uapp_seam` 之间 |
| 权威顺序 | A（用户本轮答了系统上一轮问的那一项）> B（载体）> E（本轮模型抽取） |
| 确定性规则 | 空值／未提及／漏抽取不擦除已确认字段；用户明确纠正以新值更新并登记下游 `STALE`；新内容任务不继承内容级决定 |
| 恒等性 | 载体为空时是恒等变换，现有 C1/C2 的充分输入一个字节不变 |
| 候选画布 | 47/49 → **48/50**，`8998088ed9fa06d5b3582778eeaf535f67fc112d5e1a41aed0800be913df4a99` |
| 未动 | M1／M2／最终 FP M3／Seam／六能力语义；`m5_extract` 的 prompt、模型、参数 |

`TD-UAPP-21`：新建 `unified-app/evidence/UAPP_R1_PROTECTED_BASELINE_v1.0.json`（`db1b7a74…`），R0 原样保留。
`TD-UAPP-22`：`S4_SCOPE_ISOLATION_PREFLIGHT_v1.0.py`，第三方并发允许并登记、触碰任务作用域即 fail-closed，正负控制 7/7。

零模型调用验证 11/11（`FIELD_CARRIER_VERIFICATION.json`），主证据为真实 T2–T6 外壳的历史失败回放。

### 受影响连续链结果：**FAIL 13 PASS / 4 FAIL / 17**

判据 `S4_NARROW_CHAIN_GATE_v1.0.json`（`7ccb7e66…`），冻结提交 `dbc212a`。

**修复生效的部分**（同一场景，修复前 T4/T5/T6 的 artifact 全部为 0）：

| 轮 | 载体补齐 | 用户本轮确认 | 仍缺 | artifact |
|---|---|---|---|---|
| T2 | 无 | 4 项 | 无 | 6188+ |
| T3 | `primary_goal` `expected_change` `content_promise` | 无 | `content_origin_mode` `goal_family` | 0 |
| T4 | 3 项 | **`content_origin_mode`** | `goal_family` | **6843** |
| T5 | **`content_origin_mode`** `time_window` `content_promise` | 无 | `production_profile` | 0 |
| T6 | `cta_contract` | 无 | 无 | **9031** |

T5 的 hop 仍把 `content_origin_mode` 列为缺口，载体补齐了它，**用户没有被重复询问**——TD-UAPP-20 要解决的那件事成立了。

**四条 FAIL 的归因**（详见 `unified-app/docs/S4_NARROW_CHAIN_FAILURE_TRIAGE_003.md`）：

| 判据 | 归因 | 内容 |
|---|---|---|
| N-04 | `SYSTEM_UNDER_TEST` | 载体只认反引号字段，`goal_family`（外壳 `objective` 块内非反引号书写）在覆盖范围之外，跨轮仍会丢 |
| N-05 | `ORACLE_OR_CRITERION` | 判据要求 `content_origin_mode` 出现在 PP 的外壳里，但它不在该能力必填清单内；实质要求（载体保留＋不重复询问）已成立 |
| N-07 | `INSUFFICIENT_EVIDENCE` | PD 停在 `production_profile`。制作规模在夹具与六轮话术里一个字都没有；修复前那轮 hop 曾从上游对冲出一句话（来源标记 `UP`），本轮判为缺口 |
| N-15 | `CHECKER_OR_FIXTURE` | 负控制选了 T1（同轮自填），不是真实跨轮携带；正控制六轮全部成立 |

### `ATT-UAPP-FIELD-01` 的真实外部副作用

| 目标 | 冻结预算 | 实际 |
|---|---|---|
| 画布 workflow run | 6 | **6** |
| 嵌套应用 run | ≤24 | **24** |
| DeepSeek LLM 节点 | 预期 36／上限 44 | **33 成功、0 失败** |
| 重试 | ≤1 | **0** |
| 夹具上传 | 6 | **6** |
| M2 `diyu_business` | 各 1 | **各 1**；`task_snapshots`／`artifacts`／`publish_instances` 各 0 |
| 重复幂等键 | 0 | **0** |
| 第三方并发写入者 | 允许并登记 | **本轮为空** |
| 九受保护应用（R1 基线） | 零漂移 | **零漂移** |
| 真实内容平台 | 从未连接 | **0 行** |
| `main` / `origin/main` | 未动 | 停在 `01a42b0` |

---

## L2 追加 · `ATT-UAPP-FIELD-01` 之后的 CHECKPOINT（2026-08-30，非终态）

```yaml
task_id: DIYU-V1-UNIFIED-DIFY-APPLICATION-001
task_progress: IN_PROGRESS
terminal_state: UNSET
next_state: CHECKPOINT

TD_UAPP_20_REPAIR_DEPLOYED: true              # 载体 + 合成节点已上线并验证生效
S4_NARROW_CHAIN: FAIL                          # 13 PASS / 4 FAIL / 17
FACT_SUFFICIENCY_CHAIN_REPAIR: NOT_UPGRADED
S4_CONTENT_ORIGIN_CONTINUATION: NOT_UPGRADED
TD-UAPP-20: OPEN      # 覆盖范围不含非反引号声明字段
TD-UAPP-21: DONE_PENDING_CLOSURE   # R1 基线已建并通过 N-12，随本轮整体 FAIL 未 CLOSED
TD-UAPP-22: DONE_PENDING_CLOSURE   # 作用域隔离门已建并通过 N-13，随本轮整体 FAIL 未 CLOSED
TD-UAPP-23: NEW       # hop 同一次执行既写 primary_goal 值又报同名缺口，未确认未追查

successor_app_id: 85c01f85-a081-43e9-ab09-9993289cc200
graph_sha256: 8998088ed9fa06d5b3582778eeaf535f67fc112d5e1a41aed0800be913df4a99
node_edge_count: 48/50
protected_baseline: unified-app/evidence/UAPP_R1_PROTECTED_BASELINE_v1.0.json
gate: unified-app/stages/S4_NARROW_CHAIN_GATE_v1.0.json
freeze_commit: dbc212a240267dec15a39b47113354395a741bc3
main: 01a42b0ed97344a67302ecb6778ae4a772eb28b2      # 未动
main_merge: NOT_ALLOWED
third_repair_iteration: FORBIDDEN
enter_s5: NOT_AUTHORIZED
```

**唯一下一动作：等规划侧对五件事裁定**（`uapp_fields` 字段识别范围、N-05 判据改写、`production_profile` 归属、N-15 负控制选轮、`TD-UAPP-23`）。执行侧不自选。

---

# ATT-UAPP-CANON-01 · 规范任务状态载体与真实 CS→PD→PP 连续链根修复（2026-08-30）

授权：CONTINUE EXECUTION PROMPT v1.0（Founder 注入）。本段只追加，不改写上文任何既有 FAIL 记录。

## Phase A｜零模型根因复核

九条规划侧事实与现场逐条一致（9/9），零模型调用。
`confirmed_origin = SYSTEM_UNDER_TEST`：`uapp_fields` 把一行文本当作字段，同时缺身份、来源、作用域、可信等级。
证据：`unified-app/evidence/stages/s4_canonical_state/S4_PHASE_A_ROOT_CAUSE_RECHECK.json`；
归因：`unified-app/docs/S4_CANONICAL_STATE_FAILURE_TRIAGE_004.md`；commit `4034924`。

## Phase B｜模型调用之前冻结的新版判据

| 文件 | sha256 |
|---|---|
| `stages/S4_CANONICAL_TASK_STATE_INPUTS_v1.0.json` | `f19f5d1bc1dcba3061c578b42c43188484706eaa6e9dd265f3f5c37987ee17a6` |
| `stages/S4_CANONICAL_TASK_STATE_GATE_v1.0.json` | `724aace11b0a82213683c4dcb70b89090837b0db50ea09b7195b5d8937eefa19` |
| `stages/S4_CANONICAL_TASK_STATE_GATE_v1.1.json` | `a7986e477edc9f8c46a71983fd51fb7e358efa5442e0c1186fe3ebf98ca14e79` |
| `stages/S4_CANONICAL_TASK_STATE_CANDIDATE_MANIFEST_v1.0.json` | `3b8a7e9a59b56b9b6b93868bf762942ba343c789bec6bb8c3da044e277a3e468` |

v1.0 原样保留；v1.1 为后继版本，登记两处**发生在任何模型调用之前**的判据自纠（R-01 过度限定 `lvl=="D"`；R-02 误设矛盾集恒非空），归因均为 `ORACLE_OR_CRITERION`。commit `1f5004c` / `0355004`。

## Phase C｜一次最高失效节点根修复

`unified-app/workflows/S4_CANONICAL_STATE_NODES_v1.0.py`：显式 `SPEC` 规范字段表（20 项，每项带 `canonical_id / value / source_kind / source_ref / authority_level / scope / revision`），artifact 血缘账本节点 `uapp_state` 取代零消费者的 `stale_downstream`。
未做：未改 Hop Prompt、未写案例专用分支、未复制六能力规则、未建通用状态服务或数据库。

确定性正负控制 **14/14 PASS**（P-01..P-11 各带单变量负控制，R-01..R-03 用旧 T1–T6 真实载荷离线重放）：
`unified-app/evidence/stages/s4_canonical_state/S4_CANONICAL_STATE_VERIFY.json`。

候选发布：`graph_sha256 = 6bf7c8f5f050e0e831d0b4afe29b2835fb08f48da344a2df898d7ca081590852`，49 节点 / 51 边，版本 `2026-08-30 07:11:27.885795`。发布图与通过静态检查的离线构建图逐字节一致。

## Phase D｜唯一一次七轮真实运行

`end_user = s4ct-20260830001839`，`conversation_id = 5cfcaf57-8808-4fc7-8c66-d661e515d05a`，同一会话，每轮挂同一冻结夹具，每条输入只发一次。
证据目录：`unified-app/evidence/stages/s4_canonical_state/run/`（T1–T7 + `RUN_META.json`）。

| 轮 | 目标能力 | HTTP | 耗时 | Attempt | artifact 长度 | artifact sha256 |
|---|---|---|---|---|---|---|
| T1 | CONTENT_BRIEF | 200 | 121.68s | 1 | —（提问） | — |
| T2 | CONTENT_BRIEF | 200 | 321.94s | 1 | 6600 | `5912166572ff6e239278e00c0e14b934482a1d0811dbd6e8435bce94dac21dd0` |
| T3 | CREATIVE_SCRIPT | 200 | 100.50s | 1 | —（提问） | — |
| T4 | CREATIVE_SCRIPT | 200 | 226.22s | 1 | 6016 | `81635d887e13ef6e68280c6b388441c5a33d491b8531af67562b3d8d3360fef1` |
| T5 | PRODUCTION_DIRECTOR | 200 | 205.10s | 1 | —（提问） | — |
| T6 | PRODUCTION_DIRECTOR | 200 | 204.58s | 1 | 10121 | `b032cfd7cb6f1862cd207808caed52f2addb86b2f2679d454a1331880b3ac1bb` |
| T7 | PUBLISHING_PACKAGING | 200 | 238.99s | 1 | 14984 | `88909e875b0c4c692ddbb9453daf1150b5a6a9f25976a7073a36ffd5644b2de4` |

判定 **10/10 PASS**（V-01..V-09 + S-01，零模型调用）：`unified-app/stages/S4_CANONICAL_TASK_STATE_RESULT_v1.0.json`。
成本：画布 7/7，嵌套 28，LLM 节点 39 / 硬上限 48，重试 0，夹具上传 7。

### 完整链关键位（V-06）

T7 `uapp_hop.inputs.upstream_capability = PRODUCTION_DIRECTOR`；
`sha256(upstream_delivery) = b032cfd7cb6f1862cd207808caed52f2addb86b2f2679d454a1331880b3ac1bb`，与 T6 PD artifact sha256 **完全相等**；
`upstream_binding = [{slot: content_body_or_beats, upstream_capability: PRODUCTION_DIRECTOR, produced_turn: 6, accepted_turn: 7, lineage: BOUND}]`。
上一轮 PP 上游为 CS artifact（PRE 短入口），其证据原样保留，未被本轮改写。

### 作用域隔离（本轮活体证据）

终态载体同时持有 `operation.time_window = "四周内"`（E / MODEL_EXTRACTION / `TURN3.uapp_hop.CREATIVE_SCRIPT` / OPERATION）与 `production.time_window = "今天半天内"`（B / USER_UTTERANCE / `TURN6.user_request` / PRODUCTION`）。同名键未串。T5 因此正确把 `time_window` 留为缺口并追问。

### 等级纪律

终态 19 字段：12 项 B（`USER_UTTERANCE`，`ref` 均为 `TURNn.user_request`），7 项 E（`MODEL_EXTRACTION`，`ref` 均为 `TURNn.uapp_hop.<CAP>`）。
`missing_source_ref = []`，`level_ref_mismatch = []`，`placeholder_in_carrier = []`。无任何 E 值在没有用户轮次的情况下升为 B。

### 纠正与失效传播（如实记录，未完全验到）

真实运行发生两次纠正：T4 `facts.publish_permission`、T6 `production.profile`。两次 `stale_artifacts` 均为空，经查是**正确**行为——纠正时刻账本中已有 artifact 的 `dep` 集合都不含被纠正字段（`facts.publish_permission` 在 T3 才登记，T2 CB 不依赖它；`production.profile` 在 T5 才登记，T2/T4 均不依赖）。符合 A3「不多算」。
**但这意味着「纠正 → 依赖 artifact 置 STALE」这条通路在本次真实模型运行中没有被走到。** 其证据目前只到确定性正负控制层（P-xx / R-xx 离线），真实运行层记为 `NOT_VERIFIED (NOT_CHECKED)`，不上调。

### 判定器显示缺陷（不影响判定）

`S4_CANONICAL_STATE_ADJUDICATE_v1.0.py` 的 V-07 展示行 `sorted(k for k, v in last.items() if v == "E")` 把字段字典与字符串比较，恒为空。PASS 谓词为 `not bad_ref and not bad_kind and not ph`，不含该项，判定不受影响。真实 E 级字段 7 个：`content.explicit_non_promise`、`cta.level`、`delivery.platform`、`expression.boundary`、`expression.subject`、`facts.registered`、`operation.time_window`。

### 保护面

运行前后作用域快照逐项一致：候选 `graph_sha256` 未变，九个受保护应用 md5 零漂移，`hop_pin = 2026-08-30 03:38:31.449618` 未变，钉住的 `m5_compose sha256 = 6474b902c81c7d91fe8f6143c0a3ece9bbde55dc58b64a822e595b088f2ee855` 未变。隔离门未触发。
`M2 diyu_business`：`workspaces/accounts/cycles/tasks` 各 1，`task_snapshots/artifacts/publish_instances` 各 0，重复幂等键 0。
第三方并发写入者登记披露、不阻断：`FCVSS 18dd7b02-b661-4cad-a8db-23058e1bcb48`，79 runs，不在本任务十个 app 范围内。
`main` / `origin/main` 未动，停在 `01a42b0ed97344a67302ecb6778ae4a772eb28b2`。

## COMPLETION CHECK

- `real_behavior_verified`：是。七轮真实模型运行，CB/CS/PD/PP 四份真实产物，PP 上游哈希等于本轮 PD 产物。
- `validator_discrimination_verified`：是。P-01..P-11 每项带单变量负控制，14/14；判定器零模型调用、只按冻结 Gate 重算。
- `core_problem_solved`：**部分**。规范字段身份、来源、作用域、可信等级四项与完整链均在真实运行中成立；「纠正传播失效」只在离线控制层成立，真实运行未走到该分支。
- `protected_targets_unchanged_or_authorized`：是。运行前后快照逐项一致。
- `evidence_refs`：见上各 sha256、`RUN_META.json`、`COST_ACCOUNT.json`、`S4_CANONICAL_TASK_STATE_RESULT_v1.0.json`。
- `unnecessary_complexity_remaining`：`stale_downstream` 已被 `uapp_state` 取代；未发现其它删除后不影响 P0 的复杂度。

## 本轮允许上调的最窄结论

```yaml
CANONICAL_TASK_STATE_CARRIER: PASS/CURRENT
CS_PD_PP_NARROW_CHAIN: PASS/CURRENT
S4_CONTENT_ORIGIN_CONTINUATION: PASS/CURRENT
TD-UAPP-23: CLOSED/CURRENT
CROSS_TURN_CORRECTION_PROPAGATION: NOT_VERIFIED(NOT_CHECKED)   # 真实运行未走到；不上调
```

未声明、也不成立：UAPP 全部验收完成；M1–M5 全部生产就绪；所有 UAPP-AC 已全绿；可以自动合并 main。
旧 `N-04 / N-05 / N-07 / N-15` FAIL 原样保留，本轮 PASS 只作 successor 证据，不追溯改写历史。

```yaml
task_id: DIYU-V1-UNIFIED-DIFY-APPLICATION-001
task_progress: IN_PROGRESS
terminal_state: UNSET
next_state: CHECKPOINT
main_merge: NOT_ALLOWED
enter_s5: NOT_AUTHORIZED
```

---

# ATT-UAPP-EXT-REVIEW-01 · S4 证据真值纠偏与 PP 交付边界归因（2026-08-30）

`task_mode: CONTINUE`（同一 `task_id`，同一合同哈希，不是 REBASE）。
授权：CONTINUE EXECUTION PROMPT v1.0《DIYU V1 · UAPP S4 证据真值纠偏与 PP 交付边界归因》。
**本轮零模型调用、零 Dify 写入、零工作流发起、零数据库写入。** 只读 T1–T7 RAW、Dify 运行库与 Git。

## 一句话

**技术链是真的，交付内容不合格。** 上一段 `ATT-UAPP-CANON-01` 记录的链路结论未被推翻，
但 PP 的最终交付里同时出现「把未登记的人物长期行为写成事实」与「已收到 NO_CTA 仍生成评论互动引导」，
而旧 V-08 因为探针面根本不覆盖这两类，误报了 PASS。

```yaml
S4_OVERALL_ACCEPTANCE: FAIL / CURRENT
```

## 激活核验

`HEAD = a13a73458ee8e3008d67fc4b14758b80296a0df2`，与 `origin/codex/v1-uapp-progressive-canvas-001` 一致；
`main = origin/main = 01a42b0ed97344a67302ecb6778ae4a772eb28b2`；worktree clean；
`git diff a13a734 -- unified-app` 为空，八份绑定文件与 T1–T7 RAW 哈希全部与 `a13a734` 一致。

## 零模型独立复算（不采信既有摘要）

顶层 run 7/7、嵌套 28/28 全 succeeded、LLM 节点 39 succeeded / 0 failed（按窗口与十个 app_id 现查）、
单一会话、每轮 Seam 工具唯一；
四份 artifact 现算：CB 6600 `5912166572ff6e23…`、CS 6016 `81635d887e13ef6e…`、PD 10121 `b032cfd7cb6f1862…`、PP 14984 `88909e875b0c4c69…`；
T7 `upstream_capability = PRODUCTION_DIRECTOR` 且 `sha256(upstream_delivery)` 与 T6 PD artifact 逐字节相等；
复核时点重算九受保护应用 md5 9/9 一致、候选图 `6bf7c8f5f050e0e8…`（49 节点 / 51 边）一致、`hop_pin` 未变，
运行窗口之后候选画布与四个能力应用零新增 run。

## PP 输入约束：到位，归因排除

PP 真实运行 `15e2643a-7710-47d0-a162-40b13726219d`（app `c9cdea24…` = 受保护 PP，succeeded，103.45s）。
输入逐字包含 `cta_contract: 不做购买、到店、私信或领取引导，只保留内容本身`、`NO_CTA`、
`facts_registered`、`explicit_non_promise`、`expression_boundary`、`asset_publish_permission`，
且**整段逐字包含** T6 PD artifact（10121 字）。
「PP 没收到约束」这条归因不成立。

## 最高失效节点

```yaml
highest_confirmed_failing_node: PUBLISHING_PACKAGING delivery generation
```

九条冻结定位串全部在 `PP.raw_preserved`（PP 自己的原始模型输出）**首次出现**，在 PP 两路输入中**零命中**；
下游逐层 sha256 相等：`PP.artifact == SEAM.artifact`、`PP.user_delivery == SEAM.user_delivery == CANVAS.final_text == CANVAS.answer`。
Seam 与统一画布是纯透传，一个字没加。按 A3，**不得在投影层打补丁**。

## F1–F5 归因

| 编号 | `confirmed_origin` | 一句话 |
|---|---|---|
| F1 | `SYSTEM_UNDER_TEST`（PP 交付生成层） | 把未登记的「苏禾一直在用这套三问」写成事实；PP 自己已核对出夹具没写，仍然写入；加脚注标注推断不构成回指（A2：非事件的变换不改变阶梯位置） |
| F2 | `SYSTEM_UNDER_TEST`（PP 交付生成层） | 收到 NO_CTA 仍生成结尾互动提问与整段评论区设计；把「只保留内容本身」改写成「不做购买引导」，自造「低风险互动范畴」豁免（A4 下游缩小上游边界；A1 执行方不得改版边界） |
| F3 | `CHECKER_OR_FIXTURE` | V-08 报 `fabrication=[]`＋PASS，但 `fabrication_probes` 七项与 `leak/overclaim` 43 项**都不覆盖**这两类；苏禾在人名白名单内。PASS 是探针未命中，不是证据支持的通过 |
| F4 | `ORACLE_OR_CRITERION` / `EVIDENCE_BINDING` | Gate v1.1 的 `frozen_before_any_implementation_change` 与自身 `supersedes.when` 冲突；Manifest v1.0 与 VERIFY(v1.0) 仍绑 Gate v1.0，而正式 T1–T7 绑 Gate v1.1；V-07 展示行缺陷 |
| F5 | `INSUFFICIENT_EVIDENCE` | `CROSS_TURN_CORRECTION_PROPAGATION` 维持 `NOT_VERIFIED(NOT_CHECKED)`：两次真实纠正都没命中既有 artifact 的依赖字段，STALE 通路未被真实触发 |

## 版本化证据纠偏（全部新增，零覆盖）

| 新增文件 | 作用 |
|---|---|
| `unified-app/docs/S4_CANONICAL_TASK_STATE_FAILURE_TRIAGE_001_PP_BOUNDARY.md` | F1–F5 正式归因 |
| `unified-app/docs/S4_CANONICAL_TASK_STATE_EXTERNAL_ACCEPTANCE_REVIEW_v1.0.md` | 外部验收复核正文 |
| `unified-app/docs/S4_PP_BOUNDARY_MINIMAL_REPAIR_PLAN_v1.0.md` | 唯一一份最小后继修复计划（**只计划不实施**） |
| `unified-app/stages/S4_CANONICAL_TASK_STATE_BINDING_RECONCILIATION_v1.0.json` | BR-01…BR-05 绑定复算 |
| `unified-app/stages/S4_CANONICAL_TASK_STATE_RESULT_v1.1_EXTERNAL_REVIEW.json` | 拆分后的判定结果 |
| `unified-app/evidence/stages/s4_canonical_state/S4_CANONICAL_STATE_VERIFY_v1.1.json` | 14/14 在 **Gate v1.1** 下重绑定重算 ＋ 单点变异区分证明 |
| `unified-app/evidence/stages/s4_canonical_state/S4_EXTERNAL_REVIEW_EVIDENCE_v1.0.json` | 链事实、PP 逐层归属、绑定复算的原始证据 |
| `unified-app/workflows/S4_EXTERNAL_REVIEW_v1.0.py` | 零模型复算脚本 |
| `unified-app/workflows/S4_CANONICAL_STATE_VERIFY_v1.1.py` | Gate v1.1 重绑定 ＋ 变异区分 |
| `unified-app/workflows/S4_CANONICAL_STATE_ADJUDICATE_v1.1.py` | V-07 展示纠正 ＋ V-08 拆分 |

`git status --porcelain` 只有新增，**零修改、零删除、零重命名**。Gate v1.0/v1.1、Manifest v1.0、RESULT v1.0、
`S4_CANONICAL_STATE_VERIFY.json`、`COST_ACCOUNT.json`、T1–T7 RAW 一个字节未动。

## 14/14 在 Gate v1.1 下重新绑定

`criteria_sha256 = a7986e477edc9f8c46a71983fd51fb7e358efa5442e0c1186fe3ebf98ca14e79`，被测对象与检查逻辑均未改，
结果 **14/14 PASS**。
单点变异区分（预期在运行前写死）：8 条变异，MUT-03/04/05/06/07/08 均按预期翻掉对应检查，MUT-02 按预期被前一道独立防线遮蔽；
**MUT-01 未按冻结预期翻转，预期不回改**（A2）——追加 MUT-07（翻 P-08）与 MUT-08（翻 P-02/P-08/R-02）
定性为两道独立防线互相遮蔽，不是覆盖缺口；`all_as_expected` 保持 `false`，不改绿。

## V-08 拆分与 V-07 展示纠正

```yaml
V-08A: PASS / CURRENT     # 执行路由、无暗跑、无泄漏、无 M2 重复副作用 —— 机器可判，三个子项各自出结论
V-08B: FAIL / CURRENT     # 事实主张逐项可回指 —— BOUNDED_JUDGMENT_UNDER_FROZEN_RUBRIC
V-08C: FAIL / CURRENT     # CTA 与上游冻结边界一致 —— BOUNDED_JUDGMENT_UNDER_FROZEN_RUBRIC
S4_OVERALL_ACCEPTANCE: FAIL / CURRENT
```

V-08B/V-08C **绝不因 token 未命中而 PASS**。定位串标注 `evidence_locator_only, NOT_A_CHECKER`，
只用于在本次产出里定位已认定的违规，不得被改写成未来的校验器。

V-07 展示纠正后终态真值：**E 级 7 个**（`content.explicit_non_promise`、`cta.level`、`delivery.platform`、
`expression.boundary`、`expression.subject`、`facts.registered`、`operation.time_window`），**B 级 12 个**。
判定谓词一字未改，V-07 仍为 PASS。

## 状态继承

保留 `PASS / CURRENT`：四份 artifact 真实产生；PD→PP 哈希血缘成立；每轮只运行一个目标能力；
已确认字段未被空值擦除；E 级抽取值未自动升级为 B；作用域隔离成立；`S4_CONTENT_ORIGIN_CONTINUATION` 的窄结论；
九受保护应用零漂移。**不 blanket STALE。**

被下调：`S4_OVERALL_ACCEPTANCE` → **FAIL / CURRENT**；V-08 合一 PASS → 拆分后 V-08B/V-08C **FAIL**；
`S4_CANONICAL_STATE_VERIFY.json` 的 14/14 仅在 **Gate v1.0** 下成立。

不再可声明：S4 整体 PASS ／ Validator discrimination 全部成立 ／ PP 交付符合 PRD ／ 可以进入 S5 ／ 可以合并 main。

`ATT-UAPP-CANON-01` 段登记的 `CANONICAL_TASK_STATE_CARRIER`、`CS_PD_PP_NARROW_CHAIN`、
`S4_CONTENT_ORIGIN_CONTINUATION` 三项是**载体与链路**层面的窄结论，本轮证据未推翻，保持 CURRENT；
它们**从来不蕴含** PP 交付内容合格——本轮把这条区分显式写死。

## 唯一后继最小修复候选

```yaml
candidate_repair_node: PUBLISHING_PACKAGING 能力应用的交付生成层
app_id: c9cdea24-9df3-400b-9ecd-1d740e8c96df
```

影响面已登记：该 PP 是 **M5 FP 的 PP**，其 graph md5 `788c8555…` 被 7 处记录绑定
（含 M5 已完成验收证据与 M5 收口只读绑定），消费者是 M5 FP Seam `5fca0162…`。
**不得静默修改**；实施需独立 Execution Prompt 与 Founder 授权。计划见
`unified-app/docs/S4_PP_BOUNDARY_MINIMAL_REPAIR_PLAN_v1.0.md`。

## COMPLETION CHECK

- `real_behavior_verified`：**是**——既包含真实链路成功，也包含 PP 真实内容失败（逐字原文 ＋ 逐层首次出现位置）。
- `validator_discrimination_verified`：**只有 V-08A 可成立**。V-08B/V-08C 不得继续用旧 Checker 冒充成立。
- `core_problem_solved`：本 Prompt 只解决「证据与声明一致」，**不声称 PP 已修复**。
- `protected_targets_unchanged_or_authorized`：**true**（只增不改，Dify 侧复核时点重算全等）。
- `unnecessary_complexity_remaining`：无 A/B、无重复采样、无新架构层、零模型调用。

```yaml
task_id: DIYU-V1-UNIFIED-DIFY-APPLICATION-001
task_progress: IN_PROGRESS
terminal_state: UNSET
next_state: CHECKPOINT
S5: NOT_STARTED
main_merge: NOT_ALLOWED
CROSS_TURN_CORRECTION_PROPAGATION: NOT_VERIFIED(NOT_CHECKED)
S4_OVERALL_ACCEPTANCE: FAIL/CURRENT
```

---

# ATT-UAPP-CORRECTION-FREEZE-01 · UAAB successor 同步与跨轮纠正正式冻结（2026-08-30）

`task_mode: CONTINUE`；`task_id`、合同哈希与根任务保持不变。授权来源为 Founder《统一 Dify 应用跨轮纠正传播、S4 收口与 S5 最终验收 CONTINUE Execution Prompt v1.0》。本段只追加，不覆盖前述 PP 旧 FAIL、旧图身份、旧 Attempt 或 Founder RETURN。

## successor 状态同步

只读继承相关工作包 `DIYU-V1-UAPP-ACCEPTED-ARTIFACT-BINDING-001`：

```yaml
UAPP_ACCEPTED_UPSTREAM_ARTIFACT_BINDING: PASS / CURRENT
D3_SUCCESSOR: PASS / CURRENT
PP_BOUNDARY_SUCCESSOR_b2: PASS / CURRENT
V-08B_FACT_TRACEABILITY: PASS / CURRENT
V-08C_CTA_FIDELITY: PASS / CURRENT
CROSS_TURN_CORRECTION_PROPAGATION: NOT_VERIFIED(NOT_CHECKED)
S4_OVERALL_ACCEPTANCE: NOT_VERIFIED
S5: NOT_STARTED
UAPP-AC-12: NOT_VERIFIED
main_merge: NOT_ALLOWED
terminal_state: unset
```

当前发布面：UAPP `85c01f85-a081-43e9-ab09-9993289cc200` / graph md5 `91a3984b2c3797d6741165b116fa3cb1`；PP 与 provider `8366328bf827bd0f460455d750d45c4f`；Seam `db49a3da8973d4fdcbe9ecf63bdf7e2a`；Hop `e38378c3c2a66b75aa7e645368c9e1ce`。UAAB Gate v1.2 `dbe4c023…ea622`、Result v1.2 `fff7ab0c…bf91` 与 checker-scope triage `1823b3e0…2abc` 均现场复算一致。

## 零模型接管与影响面

- Git：`HEAD = origin/task = 729e528826f37cc36a2a38210eab1c93d7b4d917`；`main = origin/main = 01a42b0ed97344a67302ecb6778ae4a772eb28b2`；开始施工前 clean。
- Dify：运行中 workflow = 0；UAPP/PP/provider/Seam/Hop/M3 与六能力保护图现场一致。
- 会话：`5cfcaf57-8808-4fc7-8c66-d661e515d05a` / end_user `s4ct-20260830001839` / task `ec666086-dce5-4e79-ba0f-6ac88f04a0bb`；state rev 12。
- 当前已接受 PD：fp `559a204d7c4f1f2a`，9304 字，sha256 `8f91984b628da1c65250c7bb2f90e9a31c86233826ceee9271bcc46b77b2c21b`，accepted=true，stale=false，依赖 `production.profile@frev2`。
- 影响集：`PRODUCTION_DIRECTOR@t6:099061257c9677bd`、`PRODUCTION_DIRECTOR@t11:559a204d7c4f1f2a`。其余五条无该字段依赖的记录列入不受影响集，不 blanket STALE。
- M2：本 task 的 task_snapshots/artifacts/task_run_states 均 0；该测试账号 publish_instance=0；Schema 指纹 `25192c11562827efedfc3b2c22c3b4fd`。

## 正式冻结

```yaml
inputs_file: unified-app/stages/UAPP_CORRECTION_INPUTS_v1.0.json
inputs_file_sha256: eda84ad987a58e1db3fd79f028859d0ddbce9146d83dca7038ce5c804d2c9549
query_sha256: 949f7474a6ad5c0d57955c01c9b1daf03052fd5b1a7a5d08a871c1301785af2f
gate_file: unified-app/stages/UAPP_CORRECTION_GATE_v1.0.json
gate_sha256: 9220a7bd587ec030fa340892609addab15cb70432199924285e1b1fa634a95d7
controls: PASS 12/12
controls_script_sha256: fea625560b0ccc646338bac13a1bfdc9b505e3a89da94c3c2e4ccdbbaa5a7e6b
controls_evidence_sha256: c5fbf5139905c7cbce65300c6e8f1cf3b0d19a63f9776b3aaa7398fb57ed7d14
formal_top_level_turn_count: 1
reachable_llm_node_attempt_cap: 7
manual_retry: 0
repeat_sampling: 0
ab_tests: 0
reviewer_calls: 0
model_calls_before_freeze: 0
mutation_target: NONE
```

D-01…D-12 正例及单变量负例全部通过；保护面前后指纹相等。控制脚本只读取发布图和会话副本并在内存执行 code node，未调用模型、未写 Dify、未写 M2。

技术债唯一当前主表升级为 `unified-app/docs/UAPP_TECHNICAL_DEBT_REGISTER_v1.3.md`；v1.2 原文保留。v1.3 明确区分 successor 已关闭、仍有效、当前图 STALE、未验证及新披露但不阻断项。

下一动作仅有一个：在冻结会话中逐字运行一次冻结纠正原话；任一 C-01…C-08 非 PASS 即保留 RAW、FAILURE TRIAGE、停止，不进入 S4/S5，也不修改被测对象。

## ATT-UAPP-CORRECTION-01 · 一次真实纠正传播 FAIL（2026-08-30）

冻结原话只运行一次。顶层 run `592ba2d3-c6a4-41a7-a8e9-f33818be98c4`，HTTP 200，591.97s；LLM 节点 6，失败 0，人工重试 0，平台内部重放 0，重复采样/A-B/Reviewer 均 0。

**第一处硬门 C-01 FAIL。** M3 已识别“制作规模从一人改为两人”，但 Hop 的 PP 外壳没有输出 `production_profile`；`uapp_fields` 只更新 `facts.registered`，`production.profile` 仍为旧的一人值且 frev 仍为 2。两份依赖该字段的 PD 都保持非 STALE，最新 PD 9304 字正文以原 sha256 `8f91984b…c21b` 被 `BOUND` 到 PP。系统新增 PP@t13（7370 字，sha256 `ca5ca64e…43c9f`），并真实向用户交付了标题和封面。

```yaml
C-01: FAIL / CURRENT
C-02: FAIL / CURRENT
C-03: FAIL / CURRENT
C-04: FAIL / CURRENT
C-05: FAIL / CURRENT
C-06: FAIL / CURRENT
C-07: PASS / CURRENT
C-08: PASS / CURRENT
confirmed_origin: SYSTEM_UNDER_TEST
mutation_target: NONE
```

归因见 `unified-app/docs/UAPP_CORRECTION_FAILURE_TRIAGE_001.md`；结果见 `unified-app/stages/UAPP_CORRECTION_RESULT_v1.0.json`；RAW sha256 `cc2b0c9aed9d28ef440182bc5c32290f660dae4774f1cbdc5ead11e81a2642dc`。

保护面：六个专业能力中仅 PP 运行；UAPP、PP/provider、Seam、Hop、M3 与六能力图前后相等；M2 task 行、publish_instance 均 0→0；Schema 与非测试计数不变；main 未动。仅测试会话 state rev 12→13、旧 PP@t12 STALE、新 PP@t13 追加，失败状态原样保留，不直接改库。

新增 `TD-UAPP-24`，唯一当前技术债主表升级为 v1.4，v1.3 原文保留。

按冻结停止规则：不修改实现、不改 Gate/输入/Checker、不重跑、不进入 S4、不启动 S5。

```yaml
CROSS_TURN_CORRECTION_PROPAGATION: FAIL / CURRENT
S4_OVERALL_ACCEPTANCE: NOT_VERIFIED
S5: NOT_STARTED
UAPP-AC-12: NOT_VERIFIED
main_merge: NOT_ALLOWED
task_progress: IN_PROGRESS
terminal_state: unset
next_state: CHECKPOINT
unique_next_action: Founder 版本化授权 TD-UAPP-24 的最小 successor repair
```

---

# ATT-UAPP-TD24-SUCCESSOR-01 · 规范纠正传播最小后继修复与 S4 定向收口（2026-08-30）

`task_mode: REBASE_TASK`；合同语义无变化。授权来源为 Founder《TD-UAPP-24 规范纠正传播最小后继修复与 S4 定向收口 Execution Prompt v1.0》。本段只追加，不覆盖 `ATT-UAPP-CORRECTION-01` 的 FAIL、旧图、旧 Gate、旧 RAW 或旧 Result。

## 实现与零模型控制

- 最小修改面：统一应用内部能力中立纠正接缝、现有 artifact 账本的最小 `upstream_fp`、纠正后选择与绑定复核；未新增应用、数据库、状态服务或外部运行时。
- Candidate canonical sha256 `a39b72d5291ccdbc2d74837ec9041e4a2d9d7142cac0ccfcf808a6205d141ad1`，55 节点 / 57 边。
- Controls v1.1：11/11 PASS，11 正例 + 11 单变量负例；v1.0 的 10/11 与 `CHECKER_OR_FIXTURE` 归因保留。
- Gate `UAPP_TD24_GATE_v1.0.json` sha256 `fb040eb9fd3a27cdbe0a047fbd360055d0287baa335c12d1971092c61ea5ddb0`，冻结早于正式调用。

## 唯一正式运行

顶层 run `010fe130-d990-48ae-893b-13adaeb0b08e`；HTTP 200，172.67s；DeepSeek LLM 节点 5，失败 0；人工重试、平台内部重放、重复采样、A/B、Reviewer 均 0。

真实状态：

- `production.profile` 与 `production.capacity_or_owner` 同步从一人改为两人；task revision 13→14，两个字段 revision 各 +1，来源 `USER_UTTERANCE / TURN14.user_request`；
- `production.time_window` 与 `facts.registered` 值和 revision 不变；
- PD `099061257c9677bd`、`559a204d7c4f1f2a` 直接 STALE；PP `a7bf609e2dc9eecb` 经 `upstream_fp=559a204d7c4f1f2a` 传递 STALE；
- selector `NO_LEGAL_UPSTREAM`，binding `REJECTED`；Seam/PP 运行 0，新 PP 0；
- artifact 8→8，正文存储 sha256 保持 `8f8499a1594276ca8ae0e29428e4e3059f97411f244badcae3ccab042c843224`；
- M2 task 行、publish_instance、schema 和非测试计数不变，无真实发布。

正式结果 `UAPP_TD24_RESULT_v1.0.json`：C-01…C-12 **12/12 PASS / CURRENT**，sha256 `3284ce2be889041c8cec6d3cd9973c95f17a8efc649e2d89ac35d41b70aeadd2`。

## S4 定向收口

零模型重算现行八项必要条件，另对当前候选的非纠正产物绑定路径执行真实旧状态正例及错误 fp 单变量负例：8/8 PASS。结果 `UAPP_TD24_S4_CLOSEOUT_v1.0.json`，sha256 `2296dbc3821e8ae4d967960e8c9c6a96e9e26d926d6f535ade262bff41a5072b`。

```yaml
CROSS_TURN_CORRECTION_PROPAGATION: PASS / CURRENT
S4_OVERALL_ACCEPTANCE: PASS / CURRENT
S5: NOT_STARTED
S5_START: WAIT_FOUNDER_AUTHORIZATION
UAPP-AC-12: NOT_VERIFIED
main_merge: NOT_ALLOWED
task_progress: IN_PROGRESS
terminal_state: unset
unique_next_action: Founder 审阅本轮交付后决定是否另行授权 S5
```

技术债唯一当前主表升级为 `unified-app/docs/UAPP_TECHNICAL_DEBT_REGISTER_v1.5.md`；TD-UAPP-24 由 successor 关闭，v1.4 及其历史 FAIL 原文保留。

---

# ATT-UAPP-S5-F1-01 · 最终技术验收冻结与预检（2026-08-30，进行中）

Founder 事件 `UAPP-S5-FINAL-TECHNICAL-ACCEPTANCE-2026-08-30` 在原 task_id 下只授权 Prompt 1 的 F1/F2；Prompt 2/3、AC-12、main 合并和终态未授权。

激活现场：任务分支与远端均为 `e1ef78fa9637e7859598f2a453c3e0152a368caf`，main/origin/main 均为 `01a42b0ed97344a67302ecb6778ae4a772eb28b2`，活动 workflow 0；UAPP/PP/provider/Seam/Hop/M3 与 S4 当前锚点一致，M2 schema 和非测试计数未漂移。

F1 将合同来源场景逐字编译成 19 个冻结自然语言输入，计划上限 19 个顶层 run、114 个静态可达 DeepSeek 节点尝试。Checker 首轮暗跑负例错误加入了本例允许能力，独立归因 `CHECKER_OR_FIXTURE`；未调用模型、未改被测对象，只修该夹具后 19 个正例与 190 个逐判据单变量负例全部通过。该控制结果不构成任何 UAPP AC 的功能 PASS。

当前技术债主表升级为 v1.6。F1 最终 10/10 完成：Gate sha256 `d27254ff95ba47d4cd056c3697d658e463956382faa5cdbec0d07b187e3b358a`，冻结提交 `b1ff8ed7866b6dfb3cd29ca361d1585a34f178e4`（`2026-08-30T12:01:20-07:00`），已非 force push 且远端一致。F2 现在获准按冻结顺序开始；首个硬失败立即停止。

## F2 首个正式输入停止

CAP-01 顶层 run `b1f4485d-f921-4aac-a202-b3727f51f87e` 真实路由到 MATRIX，Seam/MATRIX 各 1 次、其他五能力 0，用户回复无内部泄漏。M3 首次 `gate_repair_llm` 发生 DeepSeek SSL EOF，Dify 自动重放 M3 一次；实际 7 个 LLM attempt，冻结每轮静态可达数为 6。

由于异常前已有 UAPP 模型输出，并已创建测试 workspace/cycle/task，本正式槽位不满足零输出、零状态写入、零副作用的传输重试例外。未手动重试，CAP-02～其余 18 个输入均未运行。归因 `INPUT_ENVIRONMENT_OR_TOOL`，`mutation_target=NONE`；UAPP-AC-01～11 全部保持 NOT_VERIFIED，S5 技术验收未通过也未证实系统 P0 失败。

技术债主表升级为 v1.7，新增 TD-UAPP-25 环境/平台重放披露。当前停在 CHECKPOINT，唯一下一动作是 Founder 裁决是否授权版本化后继正式槽位；Prompt 2/3、AC-12、main 合并和终态继续未授权。

## ATT-UAPP-S5-F2-SUCCESSOR-001 · Founder 启动授权

Founder 已明确授权在完全相同的候选、19 项输入、Gate、Runner、Checker 和顺序下建立唯一一次版本化后继正式槽位。旧 run `b1f4485d…` 保持 `INVALID_FOR_ACCEPTANCE`，不删除、不改判。

零模型激活核验：Git/远端一致、工作区起始 clean、冻结哈希一致、全部图一致、活动 workflow 0；Dify API 200，API/DB healthy、worker 运行，DeepSeek TLS 端点 401（网络与 TLS 可达，未调用模型）；旧 workspace/cycle/task 各保留 1 行。后继使用全新 `uapp-s5-succ-v1-*` 身份和会话，证据写入独立 namespace；原 Runner/Checker 文件不改，适配层仅重定向证据路径和首次测试身份。

后继预算 19/114，内部重放允许 0；生命周期上限 20/121。模型调用前先提交并推送 Successor Manifest/Slot。

## ATT-UAPP-S5-F2-SUCCESSOR-RESULT-001 · CAP-05 首个系统硬门失败

唯一后继槽位依冻结顺序运行 CAP-01…05；CAP-01…04 各自的冻结子检查均 PASS。CAP-05 顶层 run `d68493e9-f832-4b67-8bd5-36cd4541c273` 返回 HTTP 200，路由正确命中 Production Director，其他五能力零暗跑；但调用前上游闸门因无合法 `script_or_equivalent_beats` 拒绝，Seam 与 Production Director 均运行 0 次。冻结 Checker `CAP-02=FAIL`，独立归因 `SYSTEM_UNDER_TEST`。

后继累计顶层 run 5/19，DeepSeek LLM 尝试 25/114，节点失败 0，人工重试 0，平台内部重放 0；任务生命周期累计 6/20 和 32/121。CAP-06 及后续 14 个输入未运行。本轮没有 artifact、content version、publish instance 或 feedback record，也没有真实发布、非测试数据、schema、图或 main 变化。

```yaml
UAPP-AC-04: FAIL / CURRENT
UAPP-AC-05: FAIL / CURRENT
other_UAPP_AC_01_03_06_11: NOT_VERIFIED
F2: IN_PROGRESS / FAIL / CURRENT
S5_TECHNICAL_ACCEPTANCE: FAIL / CURRENT
F3: NOT_AUTHORIZED
UAPP-AC-12: NOT_VERIFIED(NOT_AUTHORIZED)
main_merge: NOT_ALLOWED
terminal_state: unset
next_state: CHECKPOINT
unique_next_action: Founder 裁决是否版本化授权 CAP-05 短入口与已接受上游绑定规则的最小后继修复
```

原环境失败 run `b1f4485d…` 仍为 `INVALID_FOR_ACCEPTANCE`，未删除、未改判。本次不修改被测实现、Gate、输入、Runner 或 Checker，不重跑，不建立第三个槽位，不进入 Prompt 2/3、Founder AC-12 或 main merge。

---

# REBASE-UAPP-S5-INLINE-ARTIFACT-001 · 当前轮合法产物直达专业能力（2026-08-30）

Founder 在原 `task_id` 下版本化解除上一 Active Work Package 的修复节点停止门，授权一个完整、
同根的 UAPP inline-artifact 接缝修复包。原合同哈希、PRD、19 项 S5 场景、UAPP-AC-01..11
产品含义与受保护对象不变；历史两次 CAP-05 FAIL、8 次顶层 run、44 次 LLM 尝试原样保留。

```yaml
task_id: DIYU-V1-UNIFIED-DIFY-APPLICATION-001
task_entry_mode: REBASE_TASK
task_contract_hash: 279f80ba09f9ec4fea53c71c829054276b4baa30071df7305f2f3fbf921e869f
task_progress: IN_PROGRESS
terminal_state: unset
core_problem: >
  用户本轮直接提供完整、明确确认可用的合法产物时，UAPP 必须识别其来源与类型，按当前
  task 和当前 turn 绑定原文身份，并把它逐字交给目标专业能力；不完整或歧义输入必须
  fail-closed，用户交付不得泄露内部标识。
allowed_delta:
  - UAPP current-turn inline artifact source classification and normalization
  - UAPP selector precedence, compatibility and task-scoped identity
  - UAPP fields binding verification and exact call-local injection
  - UAPP pre-Seam eligibility and blocked/delivered response scrubbing
protected_assets:
  - M1 / M2 / M3
  - Hop / Seam
  - six professional capability applications and PP b2 body/provider
  - database schema and non-test data
  - frozen PRD semantics, historical RAW, Gate, Result, Triage and workflow rows
  - main / origin/main
acceptance:
  - Phase A replays both historical CAP-05 RAWs across the whole seam with zero model calls
  - deterministic positive, single-variable negative and carrier-equivalence controls are 100% PASS
  - CAP-05 exact user script reaches Production Director and only that capability runs
  - CAP-06 valid realized content reaches Publishing & Packaging and only that capability runs
  - all 19 frozen scenarios obtain CURRENT evidence on one final candidate
  - UAPP-AC-01..11 are PASS / CURRENT before Founder AC-12 package is prepared
next_stage_default: false
founder_ac_12: NOT_AUTHORIZED
main_merge: NOT_ALLOWED
```

## Phase A 激活与统一归因

- Git 激活：`HEAD = origin/task = 7af7293a772c7ba3d1165669efea1c008fe0a68d`；
  `main = origin/main = 01a42b0ed97344a67302ecb6778ae4a772eb28b2`；worktree 起始 clean。
- 当前 UAPP graph md5 `16e10d84dcdf1deb4608d95fe30fb654`；模型调用 0；Dify 写入 0。
- 冻结 RAW：Gate v1.5 run `45c783b7-b7fc-47fa-80c0-639ce843ee55` 与 Gate v1.6 run
  `cbabab77-bbb3-4f07-a655-83d61bbd9b62`。
- 统一 triage：`unified-app/docs/UAPP_S5_INLINE_ARTIFACT_FAILURE_TRIAGE_v1.0.md`。
- 冻结重放与控制：`unified-app/workflows/UAPP_S5_INLINE_ARTIFACT_PHASE_A_REPLAY_v1.0.py`。

## L5 · 当前 REBASE 外部副作用

```yaml
event: GIT_TASK_BRANCH_FREEZE_PUSH_PHASE_A
state_before: PLANNED
target: origin/codex/v1-uapp-progressive-canvas-001
method: ordinary non-force push
content: Phase A triage, replay/control freeze and progress/ledger projection
real_publish: 0
dify_write: 0
model_calls: 0
main_write: 0
```

Phase A 冻结 push 已确认：`origin/codex/v1-uapp-progressive-canvas-001` 从 `7af7293` 快进到
`8fe6e056f534a036dc616ae7f2182e15a61595e2`，非 force，本地与远端一致。

Phase A 正式零模型结果：历史路径观察 `7/7 PASS`，正向/等价/单变量负控制 `14/14 PASS`；
结果 sha256 `034a9a6e15d476d31130471f5e98d17a5ba2fe5f4229b3ddefdbcd804c22752e`。

## Phase B/C 实现与机器硬门冻结

```yaml
implementation_package:
  - uapp_inline_artifact new deterministic source classifier
  - uapp_pick_upstream inline precedence plus historical selector preservation
  - uapp_fields exact call-local binding and injection
  - uapp_td24_block natural-language scrubbing
candidate_base_graph_md5: 16e10d84dcdf1deb4608d95fe30fb654
protected_uapp_nodes:
  - m1_shadow
  - m1_compiler
  - uapp_m3
  - uapp_hop
  - uapp_seam
  - uapp_state
  - uapp_persist
  - uapp_save
  - uapp_delivery
  - uapp_td24_correction
conversation_variables_added: 0
diagnostic_controls_before_freeze: 30/30 PASS
model_calls: 0
dify_writes: 0
next_action: commit implementation and frozen Phase C controls before writing formal control evidence
```

外部副作用预登记：下一次普通 push 仅冻结上述实现、Phase C 控制、Phase A 结果与进度投影；
不发布 Dify、不调用模型、不写 M2、不动 main。

实现/控制冻结 push 已确认：`origin/codex/v1-uapp-progressive-canvas-001` 从 `8fe6e05` 快进到
`8f870ec5ed2e4fbfc41b5ff81159688331c7eb22`，非 force，本地与远端一致。

Phase C 正式机器硬门：`30/30 PASS`。候选 canonical sha256
`2660128ad3f37cabe1976bc321bc825cf35cd3da9b1e1eb36994d63c67234a93`；CAP-05 原脚本与
注入正文 sha256 同为 `5e2447a…64894`，CAP-06 已实现内容与注入正文 sha256 同为
`00c3372f…e9fcd`；inline binding 明确 `persisted=false / accepted=false`。保护 UAPP 节点逐字相同，
模型调用 0，Dify/M2 写入 0。

下一外部副作用预登记：只把上述同一候选写入既有 UAPP draft 并发布测试候选，随后现场回读；
不修改任何专业应用/provider、M2、非测试数据或 main。状态 `PLANNED`，发布前活动 workflow 必须为 0。

候选发布已确认：Dify 返回 success；UAPP graph md5 `f7d9857323823b64d288455e1b67cf80`，
canonical sha256 `2660128ad3f37cabe1976bc321bc825cf35cd3da9b1e1eb36994d63c67234a93`，
56 节点 / 58 边，活动 workflow 回读 0。PP/provider、M3、Hop、Seam 和六能力绑定均未变化。

## Phase D 正式槽冻结

```yaml
gate: UAPP_S5_GATE_v1.7.json
gate_sha256: 6bbc1b66e7872f4440d888018c4f693b4d2b4945b0f53413edfb6660e97eb4a8
manifest: UAPP_S5_CANDIDATE_RUN_MANIFEST_v1.7.yaml
manifest_sha256: 3f028251b6eb3ad06db2e77b898d6196e55b29e010beb9e5ce7884884e1594bd
executor: UAPP_S5_EXEC_v1.8.py
executor_sha256: 3a6a5a8b5ceeef227c4794e4a7aad75b3bd4e630877a47ec31c4a301aa2fcdac
scenario_sha256: 896c5b0240f1e9c828889e38f7bad643bf523a451d5e3257318e70f54bf7c577
primary_formal_runs_max: 19
primary_llm_attempts_max: 114
same_scope_cap05_successor_max: 1
pure_transport_replay_max: 1
rebase_total_max: {top_level_runs: 21, llm_attempts: 126}
historical_cost: {top_level_runs: 8, llm_attempts: 44}
lifetime_max: {top_level_runs: 29, llm_attempts: 170}
manual_retry: 0
repeat_sampling: 0
ab_tests: 0
reviewer_calls: 0
execution_order_first: [UAPP-CAP-05, UAPP-CAP-06]
founder_ac_12: NOT_AUTHORIZED
main_merge: NOT_ALLOWED
```

CAP-05 零模型预检全部 PASS；DeepSeek 凭据仅确认存在，未读取或打印。下一 Git 外部副作用为
Gate/Manifest/Executor/发布证据普通 push，状态 `PLANNED`；完成后才允许 CAP-05 正式调用。

Gate/Manifest/Executor 冻结 push 已确认：远端任务分支快进到
`2cbe5013821752ceab0a3036cde2c8af429c0d5c`，非 force，本地与远端一致。

## Gate v1.7 CAP-05 Attempt

正式 run `3f5e2fa5-3fa8-4ce3-964d-d8da948a5e42`：HTTP 200，LLM 5，失败节点 0，平台内部
重放 0。UAPP inline/selector/fields binding 均 PASS，Production Director 收到的脚本正文与
冻结原文 sha256 同为 `5e2447a…64894`；Seam/Production Director 各运行 1 次，其他五能力 0。

目标专业能力的既有充分性闸准确 Return：缺 `content_origin_mode` 和 `content_promise`，因此
没有 artifact，也没有保存空产物。Checker 除 CAP-04 外全部通过；CAP-06 未启动。统一归因见
`unified-app/docs/UAPP_S5_INLINE_ARTIFACT_SUCCESSOR_FAILURE_TRIAGE_v1.0.md`。

该缺陷位于同一 inline-artifact 规范化接缝，且只有真实专业能力充分性闸可观察，符合 Founder
授权的唯一 same-scope successor 条件。successor 使用 `1/1`；若后继 CAP-05 仍失败，不建立
第三候选。

下一 Git push 只保全本 Attempt RAW/Check/Triage/进度，状态 `PLANNED`；不改图、不调模型、
不写 M2 或 main。当前成本：本 REBASE 1 run / 5 LLM；生命周期 9 runs / 49 LLM。

失败证据 push 已确认：远端任务分支快进到
`e6017d74e957a0b5390fbce8432a9ec3fc8c711e`，非 force，本地与远端一致。

## Inline-artifact successor Phase B/C

唯一 successor `1/1` 已实现于同一接缝包：来源节点从用户当前轮原话提取与完整正文同源的
`content.origin_mode` / `content.promise`，selector 只透明传递，fields 在 task/source turn/source
kind/body bfp/原话逐字支持全部通过后才登记 A 级普通字段并绑定正文。artifact 仍
`persisted=false`、`accepted=false`，正文不进入 canonical fields。

构建候选 sha256 `8034ddba7c2db320d31d301aadb1e88411542950dc9352d3d637f917706cb544`；
最终确定性控制 v1.1 `28/28 PASS`。v1.0 的 `27/28` 是 Checker 错读 Seam tool 参数位置，原文件
保留；v1.1 只修观察路径。py_compile/ruff/diff-check PASS；mypy launcher 缺包，记
NOT_VERIFIED(INPUT_ENVIRONMENT_OR_TOOL)，不算 PASS。

发布前 UAPP 仍为 `f7d9857323823b64d288455e1b67cf80`，active workflow 0，M2 schema
`25192c11562827efedfc3b2c22c3b4fd`，非测试 publish/feedback `1568/117`，main/origin-main
仍为 `01a42b0e…28b2`。下一 Git 外部副作用仅提交并普通 push 实现/控制冻结件，状态 `PLANNED`；
完成后才发布 successor，模型调用仍为 0。

successor 首次发布 API 因 `marked_name` 超过 20 字符返回 HTTP 400。candidate draft 已写入且
canonical sha256 为 `8034ddba…cb544`，但 published UAPP 仍为 `f7d98573…cf80`；active workflow
0，模型/正式 run/业务副作用均 0。归因 `INPUT_ENVIRONMENT_OR_TOOL`，见
`UAPP_S5_INLINE_ARTIFACT_SUCCESSOR_PUBLICATION_TRIAGE_001.md`。下一动作只版本化缩短发布标签，
不改候选图或冻结判据。

版本化发布器 v1.1 已发布完全相同的 frozen draft：UAPP graph md5
`07ea334bfcbe6e87ba8c5cd5d5dac380`，canonical sha256 `8034ddba…cb544`，56 nodes / 58
edges。M3/Hop/Seam/六能力/PP/provider 零漂移，active workflow 0。

successor Manifest v1.8 / Executor v1.9 / Gate v1.8 已在模型调用前形成；哈希依次为
`4e57aad6…9420` / `ed1aa91a…26a2` / `6c89f42a…88d3`。CAP-05 preflight exit 0。
下一 Git push 只冻结上述发布证据和正式载体，状态 `PLANNED`；远端确认后才使用唯一
successor CAP-05 槽位。

successor CAP-05 run `13eb198b-2f80-41e2-8209-6f9000b8c0bc` 正式 PASS：HTTP 200，LLM 6，
重放/重试 0。95 字脚本逐字绑定，两个同源 companion 字段进入规范状态；仅 Production Director
运行并生成 11,614 字 artifact（sha256 `cc30acac…950ad`），其他五能力 0。store/ledger/
last_capability 身份一致，M2 非测试计数、schema、UAPP 与全部保护应用零漂移。

当前本 REBASE 成本 `2 runs / 11 LLM`，生命周期 `10 runs / 55 LLM`。下一 Git push 只保全
CAP-05 RAW/Check/进度，状态 `PLANNED`；远端确认后才运行 CAP-06。

CAP-05 证据 push 已确认：远端任务分支快进到
`3d73664b9c42cf2f9864576befd3138de1c03966`，非 force。

CAP-06 run `e71e84af-e3e3-47ec-afc4-72bd02941540` 正式 FAIL：HTTP 200，LLM 5，重放/重试 0。
78 字成片正文、来源、task、fp/bfp 均完整绑定；只运行 Publishing & Packaging，其他五能力 0；
但 UAPP 未把“自然 CTA + 不写价格/折扣/站外购买承诺”规范为受限的 `cta.contract`，PP 准确
fail-closed 并只问一个自然缺口，artifact 为空。

confirmed highest failing node 为 `UAPP_INLINE_ARTIFACT_CTA_CONTRACT_NORMALIZATION`。唯一 successor
`1/1` 已消耗且 Gate v1.8 禁止第三候选，CAP-06 也已使用唯一正式输入；其余 17 项不得继续。
当前本 REBASE `3 runs / 16 LLM`，生命周期 `11 / 60`；所有 retry/replay/resampling/A-B/reviewer
为 0。S5 FAIL/CURRENT，AC-12 不授权，main 不允许，terminal unset。唯一下一动作是 Founder
版本化授权最窄 CAP-06 CTA normalization REBASE。

## CAP-06 semantic contract REBASE 与 post-CAP06 S5 Attempt

CAP-06 successor run `9f6ff2fe-b59a-4e46-85d5-c9577b1bd255`：`PASS / CURRENT`。只运行
Publishing & Packaging；正文 78 字、sha256 `00c3372f…e9fcd`；平台小红书；CTA 为低风险平台内
互动；六类包装齐全；artifact 5,115 字、sha256 `73bc661d…f5832`；LLM 6，重试/重放 0。
Checker v1.0 的 RAW 字段与否定语义误判保留，v1.1 对同一 RAW 判别后 PASS，未重跑模型。

随后按 Gate v1.9 开始剩余 S5。首个 `UAPP-GAP-01:G1` run
`347272fd-df0f-4ddd-aaea-cf904f0e3236`：系统自然地只问一个缺口且未生成 artifact，但问的是
“时间或阶段边界”；冻结 G2 只补商品与内容方向，不能回答该问题，故 AC-06 `FAIL / CURRENT`。
Checker 的“必须 uapp_ask_one/不得运行能力”属于过度编译，不作为 SUT FAIL 依据。其余 12 项按
停止规则未运行。本 CAP-06 REBASE 总计 2 runs / 11 LLM；所有重试、重放、A/B、重复采样、
Reviewer、真实发布和非测试变化为 0。当前唯一下一动作是 Founder 版本化授权最窄 GAP-01
决定性缺口/路由后继；AC-12、main、terminal 均不启动。

## GAP-01 与最终技术验收 REBASE 激活

Founder 已授权 GAP-01 最小修复、G1/G2 定向复验、剩余 11 项 S5、AC-01～11 收口及 AC-12
试用包。本轮不授权执行 AC-12、main 合并或终态。

激活现场本地/远端 HEAD 同为 `5c2aab4a96a3e5227647516d310e69df95c12892`，main/origin-main
同为 `01a42b0ed97344a67302ecb6778ae4a772eb28b2`，worktree clean，活动 workflow 0。旧 RAW
确定性回放确认 G1 被直接路由 CAMPAIGN、未产生决定性问题，最终追问冻结 G2 不回答的时间边界。

最小候选只改 UAPP `uapp_action` / `uapp_route`；其余 54 节点、58 条边、全部会话变量和受保护
应用不动。candidate canonical sha256 `65f46389…bcf2`；零模型控制 30/30 PASS，含等价表达、
明确 Campaign、明确单条内容、两问/错误缺口负例和 CAP-01～06 路由逐项等价。

下一外部副作用是发布该 UAPP 候选；发布前先提交并普通 push 当前实现/控制证据，状态
`PLANNED`。发布、回读和 Gate 冻结均不调用模型。

首次发布器运行在 Console 请求前因模块引用少一层而 AttributeError；publication 文件不存在，
线上图、draft、workflow、模型和数据副作用均为 0。归因 `INPUT_ENVIRONMENT_OR_TOOL`，只修发布器
引用，不改候选、输入、判据或预算；Triage 见 `GAP01_SUCCESSOR_PUBLICATION_TRIAGE_001.md`。

第二次运行在首个 HTTP helper 解析时发现同一父模块的 `console_call` 也少取一层；仍未发出
请求、publication 文件仍不存在、副作用 0。Triage 002 追加保留，只改该 helper 引用。

GAP-01 候选随后成功发布并回读：UAPP graph md5 `ff411f51a1916c1ea9dfbd96a9841f12`，
canonical sha256 `65f46389f8f1a1334050427acee5788769f9032342e4423ec03878af4b59bcf2`，
56 nodes / 58 edges；只改变 `uapp_action` / `uapp_route`，保护应用、M2 schema 与非测试计数零漂移。
后继产品语义 Checker 控制 `5/5 PASS`；Gate/Manifest/Executor 已在正式调用前形成，G1 preflight
PASS。当前模型调用 `0`；下一动作是冻结提交并普通 push，随后只运行冻结 G1 一次。

GAP-01 G1 successor run `d352c979-9caf-454a-b59a-a951a0385adf` 正式 PASS：系统只问一个
“一周整体节奏 vs 具体商品/内容方向”的决定性问题，冻结 G2 可直接回答；六项专业能力全为 0，
未生成 artifact。实际顶层运行 `1`、LLM 节点 `2`，重试、重放、真实发布和非测试变化均为 0。
下一动作是在同一 conversation `55411bec-87ed-442f-a524-bc489e9438df` 运行冻结 G2 一次。

G2 run `217fee1f-b6f1-4c1d-b189-f6c510564e31` 在同一 conversation 正确接上，唯一运行
CONTENT_BRIEF 且 Seam 真实执行，但 UAPP 外壳漏掉用户已说出的 content promise，最终重复追问
“她能拿到什么”，故正式 FAIL。Checker v1.0 同时额外要求 G2 立即产生 artifact，属于冻结判据外
的 Oracle 过编译。两项已在修改前分别确认；本轮使用 Prompt 预留的唯一同范围 successor，
mutation 仅限 UAPP `uapp_fields` 用户支持等价投影及 Checker 后继，不改任何保护模块。

唯一 GAP-01 successor 已完成零模型收敛并发布：实现控制 `8/8`、Checker 控制 `5/5`；UAPP
graph md5 `aa32b6385de0024d270ec9f85bd78179`，canonical sha256 `e1f01f08…18768`，只改
`uapp_fields`。Gate v1.1 sha256 `11d6ed2556e2ddbf2a82cc402467d66267efb2a75f3d146c36bdc9a157fa0d60`；
successor G1 preflight PASS。当前累计 `2 runs / 7 LLM`，下一动作只运行 successor G1 一次。

successor G1 run `52f7f504-1e02-4d65-8fe3-5dc63b765e3f` PASS：一个分叉问题、六项专业能力 0、
artifact 0；LLM `2`。累计 `3 runs / 9 LLM`，下一动作在 conversation
`b99eb7ef-4b80-402e-a50e-f797fac112ab` 运行 successor G2 一次。

successor G2 run `306c2e7f-2f8b-4eec-9b73-418ffca1ff86` 正式 PASS：同 conversation
`b99eb7ef-4b80-47f8-bed8-af2e0e05f4c7`，Seam 与 CONTENT_BRIEF 唯一运行，其他五能力 0；
artifact `7433` 字 / sha256 `1e91c208…40b29`。未重复询问 G1 或已表达的内容承诺；重试、重放、
非测试变化均 0。GAP-01 successor 累计 `4 runs / 15 LLM`，进入剩余 11 项正式顺序。

EQUIV-01a run `f033b774-f343-4070-acdb-6e350346b9e1` 正确路由、只运行 CONTENT_BRIEF，
但冻结输入没有给表达主体，能力精确询问该一项并未编造 artifact。Checker 的正例成品门因此 FAIL；
确认原因为 Fixture 与能力前置条件不等价，不修改 SUT、输入、Checker 或专业合同。EQUIV-01b/c
同依赖暂停；只版本化收窄 Runner 的依赖阻断，继续不依赖的 8 个冻结输入。累计 `5 runs / 20 LLM`。

EQUIV-01n run `b9bb4797-0d0f-4a20-bc11-a03bd43766b1` 同样只问一个真实缺口，但该负例同时
缺 expected change 与 expression subject，不是单变量 Fixture；旧 Checker 还冻结了 Seam 前停止的
物理位置。归因 `CHECKER_OR_FIXTURE`，不修改任何对象；AC-08 留 NOT_VERIFIED，继续 WITHDRAW/
FULL/RECOVERY。累计 `6 runs / 25 LLM`。

WITHDRAW-01 W0 run `c97d9b12-931b-473a-af43-f08507f01db1`：上传 HTTP 201，文件正文由
`m1_extract` 真实读取，但 UAPP 没有执行 M2 素材登记分支，task-scoped `materials=[]`。
确认最高失效节点为当前 UAPP 上传资料登记接缝；它不在本 GAP-01 Prompt 的允许修改面，故
`mutation_target=NONE`，W1 标 `NOT_RUN_DEPENDENT`。无真实发布、非测试变化、重试或重放。
累计 `7 runs / 30 LLM`，继续不依赖该失败的 FULL-01 / RECOVERY-01。
