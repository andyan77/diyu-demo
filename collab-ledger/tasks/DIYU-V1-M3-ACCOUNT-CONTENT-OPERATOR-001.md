# 任务分区账本 · `DIYU-V1-M3-ACCOUNT-CONTENT-OPERATOR-001`

> 规则正文见 [../COLLAB_CONTINUITY_PROTOCOL.md](../COLLAB_CONTINUITY_PROTOCOL.md)。本文件是 canonical §一
> 所说的**任务分区**：五本账里只应留一行定位，任务的高频运行状态写在这里。
>
> **为什么本分支没有去改 L1/L2/L3/L5 正文**：`main` 已在本任务施工期间前进到 `a7b8101`
> （M1 落地），其 `L5_SIDE_EFFECTS.md` 由 45,448 字节增长到 84,436 字节。本任务分支基于
> `df2c595`，分支内的五本账是**旧副本**。L2 与 canonical 属于协议定义的**当前投影**，
> 在旧副本上"更新替换"当前投影是错的。因此本任务只新增这一份分区文件（纯新增、零冲突），
> **五本账的一行定位留待合并时对着当时的当前版本补写**——这一步写进下面的"下一动作"。

---

## L1 · 合同与边界（历史留痕，只加不改）

| 项 | 值 |
|---|---|
| `task_id` | `DIYU-V1-M3-ACCOUNT-CONTENT-OPERATOR-001` |
| 合同 | [`M3_ENGINEERING_TASK_CONTRACT_v1.2.yaml`](../../M3_ENGINEERING_TASK_CONTRACT_v1.2.yaml)，`sha256 = 1d4163fc8bbc54e37adb2070f337994795595d7b696eac37e61ffb2089cb6839` |
| Execution Prompt | [`M3_ENGINEERING_EXECUTION_PROMPT_v1.1.md`](../../M3_ENGINEERING_EXECUTION_PROMPT_v1.1.md)，`sha256 = 9d3388e8619d02042fda79c222fdf7bfb2570d0cd855d17ad1ea5d6122c40f59` |
| 授权事件 | Founder 在执行窗口内以准确哈希明确授权工程执行；并在本轮明确授权真实模型调用与真实 Dify 候选 App 创建 |
| 起算基线 | `main @ df2c5952551f386a0e9a509404357f23c1d223c9` |
| 任务分支 | `task/m3-account-content-operator-v1` |
| worktree | `/home/faye/diyu-demo-worktrees/m3-account-content-operator-v1` |
| 允许变化面 | 新增 `account-operations/`；新增根级 `M3_*` 治理文档；新增本分区账本；一个 task-id 专用 Dify 候选 App；本分支提交与远端任务分支推送 |
| 受保护资产 | Matrix 定位权威｜Campaign 权限｜M2 的原始观测/反馈/版本/权限/恢复权威｜Content Brief／创意锦标赛／Creative Script／Production Director／Publishing & Packaging 职责｜六份既有 Skill｜`decision-chain/`、`content-production/`、`business-persistence/`、`collab-ledger/` 既有内容｜全部生产系统、凭据、其他任务的分支/worktree/Dify 对象/账本条目 |
| 验收口径 | `M3_ACCEPTANCE_CRITERIA_FROZEN_v1.0.md`（AC-00～20），冻结于 `f5a9aca` |
| `partial_delivery_authorized` | `false` |
| `merge_main` | `NOT_AUTHORIZED` |

**验收方法 REBASE（2026-08-27，Founder 权威事件 `SINGLE_FROZEN_DIFY_TEST_SET_ACCEPTANCE`）**
—— 同一 `task_id` 下的验收方法改版，合同哈希随之更新；**不建 `NEW_TASK`**，
不改产品职责、产品语义、模块边界与既有硬性要求，不覆盖历史合同、历史证据与历史 Checkpoint。

| 项 | 值 |
|---|---|
| 取消 | 盲测｜盲评｜36 名盲评者｜A/B 四臂比较｜揭盲与盲评推导｜多轮模型评测｜同一候选反复修复反复调用反复验收｜执行侧调 DeepSeek 做正式产品评测｜「相比一份好提示词形成可识别增益」作为交付前置条件 |
| 改为 | 执行侧提供**一组**冻结测试输入（≤7）与完整 Dify 操作方法；Founder 本人在指定 App 逐条运行、直接观察真实输出，对当前冻结候选给出 `PASS` 或 `FAIL`；不设第二轮 |
| 历史证据 | 全部保留原文与哈希，不删不覆盖不改写；可用于诊断与工程修复；**不再是产品接受的必经流程**；**不得追溯改写为 Founder 亲测结果**；**不得因取消盲评而宣布旧 AC-18 已 PASS** |
| `AC-18` 盲评路径 | 历史记录保持 `NOT_VERIFIED`；后继验收合同中记 `NOT_APPLICABLE` |
| 不再作出的承诺 | 「M3 已经通过盲评证明优于一份好提示词。」 |

**后继合同与准确 Execution Prompt（Founder 于 2026-08-27 以准确哈希授权执行）**

| 项 | 值 |
|---|---|
| 后继合同 | [`M3_ENGINEERING_TASK_CONTRACT_v1.3_FOUNDER_SINGLE_SET_REBASE.yaml`](../../M3_ENGINEERING_TASK_CONTRACT_v1.3_FOUNDER_SINGLE_SET_REBASE.yaml)，`sha256 = 49021e601658194bc734285830d531352c19c1fa4416855c1f524efb073bff49`（**现场核验通过**） |
| Execution Prompt | [`M3_ENGINEERING_EXECUTION_PROMPT_v1.2_FOUNDER_SINGLE_SET_REBASE.md`](../../M3_ENGINEERING_EXECUTION_PROMPT_v1.2_FOUNDER_SINGLE_SET_REBASE.md)，`sha256 = 4b456c70a49699b904b0c6017c7d3d945c1245e2eb17686e463b0e2778e92148`（**现场核验通过**） |
| 旧合同 v1.2 | 保留历史身份，不再是当前验收合同；未覆盖、未删除 |
| 规划侧唯一入口 | `DIYU_V1_PLANNING_DELIVERY_BASELINE_v1.0.md`，`sha256 = aa5997c3…`（**现场核验通过**） |
| 最终候选 | `v1.5.2` = 两句批准的审计块输出形状硬规则（SKILL.md）+ 继承的 DD-5 |
| 执行侧模型调用预算 | **0**（DeepSeek／Qwen／其他，一律不许） |
| 验收出口 | Founder 本人在任务专用 Dify App 逐条运行 7 个输入、每个 1 次，给出唯一整体 `PASS` 或 `FAIL` |
| `merge_main` | `NOT_AUTHORIZED`；`M5` = `NOT_STARTED_NOT_AUTHORIZED` |
| 每个输入运行次数 | 原则上 **1 次**；只有纯传输故障（网络失败／SSL 错误／Dify 明确服务不可用／请求没进模型节点／没有任何模型输出）允许原输入重试一次，且传输故障与重试记录必须同时保存 |
| 明确**不属于**传输故障、不得重跑 | 输出内容不好｜输出为空但模型已正常完成｜遗漏必填内容｜违反产品要求｜闸门正确拒收｜Founder 不满意｜与预期不同 |

---

## L3 · 正式尝试与证据（历史留痕，只加不改）

| Attempt | 判据（冻结在先） | 结果 | 原始证据 |
|---|---|---|---|
| `ATT-EP05-001` 确定性/结构/负向 | `M3_ACCEPTANCE_CRITERIA_FROZEN_v1.0.md` | 83 条测试全通过（本轮 EP-10 复跑仍 83/83） | `account-operations/tests/` |
| `ATT-EP06-R1` Runtime 保真第 1 轮（直连） | `M3_ECC_RUNTIME_FIDELITY_001_FROZEN_v1.0.md`（`c64d762`） | **6/7 成功，组 6 不足** —— 未删除、未覆盖 | `evidence/ep06-runtime-fidelity/`（`874bea1`）；判定 `22e1600` |
| `ATT-EP06-FIX` 定向修复 | 同上 | `SKILL.md` O-6 与文末两处修改（`af61b82`）。按 A3，全部 9 组前序证据对新版本置 `STALE` | — |
| `ATT-EP06-R2` 第 2 轮（直连，修复后） | 同上，判据零改动 | **7/7 成功**（另一名独立判定者） | `evidence/ep06-runtime-fidelity-v2/`（`a990d68`）；判定 `de13ec1` |
| `ATT-EP06-R3` 第 3 轮（Dify 画布链路） | 同上，判据零改动，只换绑定 | **7/7 成功** | `evidence/ep06-runtime-fidelity-dify/`；判定 `M3_ECC_RUNTIME_FIDELITY_001_VERDICT_DIFY_v1.0.md` |
| `ATT-EP06B-001` 行为 49 例 | `M3_ECC_RUNTIME_BEHAVIOR_002_FROZEN_v1.0.md`（`4bcaaa0`，先于运行） | 35 例 succeeded、**14 例 402 失败**（余额耗尽） | `evidence/ep06b-runtime-behavior/` |
| `ATT-EP07-001` 纵向 12 步 | `M3_ECC_LONGITUDINAL_001_FROZEN_v1.0.md`（`4bcaaa0`，先于运行） | 12/12 跑通；独立判定 **10/12 成功，E04 与 E07 不足，整体 `FAIL(INSUFFICIENT)`** | `evidence/ep07-longitudinal/`；判定 `M3_ECC_LONGITUDINAL_001_VERDICT_v1.0.md` |
| `ATT-EP08-001` 四臂 A/B | `M3_ECC_MODULE_AB_001_FROZEN_v1.0.md`（`7564896`，先于运行） | 12 次中 6 次 succeeded、**6 次 402 失败**；**未跑完，不判定** | `evidence/ep08-module-ab/` |
| `ATT-EP10-001` 结构反搜与回滚演练 | Rubric 见 `M3_INDEPENDENT_REVIEWER_RUBRIC_FROZEN_v1.0.md` | Dify 图四类行为标签 0 命中；Dify 导出→损坏→恢复图 sha256 逐字节一致；Git 非破坏式重建索引一致 | `evidence/ep10-closeout/` |

**取证成本（真实计费）**：本轮 DeepSeek 实花约 143 万 token，账户余额耗尽于 `ATT-EP06B-001` 与 `ATT-EP08-001` 运行中途。

---

### 第 7 轮（载体 v1.3）

```text
授权     Founder 2026-08-26 第二次 CONTINUE_TASK（七条）
判据     REBIND-004（70a121b）+ ADDENDUM_003 + Oracle v2.0，全部**先冻结后取证**
运行     保真 9/9 · 行为 49/49 · 纵向 12/12 · A/B 12/12，全部 succeeded
判定     40 名独立判定者，隔离核验全部 CLEAN
终态     PARTIAL · AC-20 输出 AWAITING_FOUNDER
```

两次被丢弃的尝试如实在案，不并进"一次完整重跑"的叙述：
`evidence/ep07-longitudinal-v13-aborted/`（字段漏改，执行侧已看过那份 E01）、
`evidence/ep08-module-ab-v13-aborted/`（沙箱只读，12 份产出未落盘即丢失，一份未看）。

### 第 8 轮（载体 v1.4.2 · 一次正式取证 + 两次批次作废 · 判定被 Founder 暂停）

**授权**：Founder `CONTINUE_TASK`（2026-08-27，八条）→ `PAUSE_NEW_MODEL_CALLS`（同日，九条）。

**判据**：`REBIND_005` + `ERRATA_001` + `ERRATA_002`，三份逐级后继，均不覆盖前作。
`G-4` 的方法义务从此写死：不许再用执行侧自己撰写的夹具量误报，必须在真实语料上量双向。

**两次批次作废，都在花完之前停、都原样保留**：
- A/B 臂规格沿用第 7 轮 JSON，B 臂 `system_prompt` 是那一轮**快照进去的 v1.3 全文**，
  等于拿旧候选跟自己比。跑到 3/12 发现。
- 为 `AC-09` 加的那句「基线为空 ⇒ 一行 `POS ::` 都不要写」把**新增持续位**一起禁掉了。
  跑到保真 9/9、行为 19/49、纵向 8/12 发现。机械计量：新增位命中 12/61 → 0/19，
  结构性探索位 11/61 → 0/19。`ERRATA_001` 修了一句没修回来，`ERRATA_002` 才发现
  同一节里还有两句在做同样的事（一句是我加的，一句是原文一直就有的）。

**正式批次**（候选 v1.4.2）：保真 9/9、行为 49/49、纵向 12/12、A/B 12/12，
两例传输故障各重跑一次（`SSL EOF`、`IncompleteRead`），失败那次原样保留，
A/B 另外 11 份逐字节沿用。85 次调用、3,126,151 tokens。

**修对的**：`G-4` 误报 11→0（第 7 轮那 5 例误拒本轮全部 `CLEAN`）；
新增持续位 12/61→26/61；结构性探索位 11/61→18/61；
`D-3` 两例真检测（`E07`／`E08`）在 v1.3 下都会被放行并承载为新基线；
`AC-16` 两处证据缺口用确定性证据关掉（系统提示词全文从 publish 端点读回、
浏览器画布用 chromium + 自写 CDP 客户端实证）。

**修坏的**：拒收 12 例里 **10 例误拒**，其中 **9 例出自本轮自己的修法**。
误拒数从第 7 轮的 6 涨到 10。四条缺陷 `DD-1`～`DD-4` 见
`evidence/ep26-gate-v14-defects/`，最高失效节点是 `gate_main` 的骨架生成。

**被中止、未产出**：三名 ECC 独立判定、36 名盲评 + 揭盲、判定者隔离核验、独立收口审查。

---

### A-09 · 第 9 轮：确定性修复 + 零模型预检（`CONTINUE_TASK_NO_MODEL_PREFLIGHT`，2026-08-27）

- **模型调用 0 次。** DeepSeek、ECC 判定者、36 名盲评者、Founder 产品验收，一个都没启动。
- 版本化冻结 `M3_ECC_REBIND_006_FROZEN_v1.0.md`（后继版本；REBIND-004 / 005 及其 ERRATA 一字未动）。
- 改三个文件：`gate_main.py`（DD-1 骨架义务集改并集）、`shared_checks.py`（DD-2 `_slot_authority`、
  DD-3a `PARTITIVE_PREFIX`、DD-3b `NEG_AFTER`、DD-3 连带 `NEG_CLAUSE_CUT`、DD-4 `REF_NEG_ATTACHED`）、
  `post_gate_main.py`（仅版本号）。`SKILL.md` **一字未改**，sha256 仍为 `245ee2ab…`。
- 零模型重放 64 次真实运行（行为 49 + 纵向 12 + A/B B 臂 3）：**拒收 13 → 2**。
  11 例误拒全清、0 例新增拒收；`E07` / `E08` 两个真拒仍被拒收，且经**穷举证明**与补齐节点怎么写无关。
- **第 8 轮拒收台账漏了一例**：`FX-M3-HOLD-02__B`（A/B 的 B 臂）第 8 轮就被误拒，台账只覆盖
  行为与纵向。误拒实数是 **11 例，不是 10 例**。
- 128 份正文上的阻断命中 7 → 0，全部判读为误报；新引入阻断 0；三族探针共 138 个，新漏检 0。
- 按 A5 删掉三处自己先写出来、量不出差别的东西：`SLOT_ASIDE`、`TRADEOFF_VERB`、全角斜杠支持
  （最后一处回退成如实披露的已知漏检 R-1）。
- 预检跑三轮，前两轮 FAIL 全部只靠改确定性代码收口，未调用模型。
- REBIND-005 的三个既有验证器在 v1.5 下重跑全部仍 PASS。其中两个把 ep22 目录下自己的
  json 重写了一遍，但逐文件与 `HEAD` 比对**三个都逐字节相同**——历史记录未被改动，
  变的只有 mtime；这本身也是「v1.5 原样复现 REBIND-005 全部结论」的独立证据。
- 证据：`account-operations/evidence/ep28-rebind006-precheck/`
  （`REPLAY_V15.json` / `REBIND006_FP_AND_MISS.json` / `E07_E08_INVARIANCE.json` /
  `IMPACT_SURFACE_V15.json`）；报告 `M3_PRECHECK_ROUND_9.md`。
- **AC 状态本轮一项未动**——零模型意味着没有任何新的运行证据，不具备上行事件。
- 查实的前置缺口：部署与运行脚本依赖的 `dify_client.py` / `create_m3_app.py` / `manifest.py` /
  `ep06_runtime_fidelity_v2.py` 存放在上一会话 scratchpad，**已随会话消失**，
  现在无法部署也无法发起正式取证。已列为重跑预算第 0 段。

### A-10 · 第 10 轮：v1.5 正式取证 + DD-5 修法 + 验收方法 REBASE（2026-08-27）

**第 0／1 段（`fc63add`）**：重建四个丢失模块（逐个对已落盘现实机械核验：`build_refs` 70/70
逐字节相同；EP-06 用例在 5 个独立轮次上 5×9 零差异；`MODEL`／`FEATURES` 与线上草稿逐字节相同），
部署 v1.5 到任务专用 App，图哈希 `3bc0950b…` → `aeb2bb86…`，形状仍 7 节点 6 边，
`SKILL.md` 字节未变（`245ee2ab…`），已发布提示词与 `SKILL.md` + 占位符逐字节相等。

**第 2 段正式取证**：70 次真实运行、**2,937,367 tokens**（预算 290 万，+1.3%）。

| 组 | 尝试 | 有草稿 | tokens | 拒收 |
|---|---|---|---|---|
| EP-06 保真 | 9 | 8 | 410,685 | 0 |
| EP-06b 行为 | 49 | 49 | 2,049,876 | 2 |
| EP-07 纵向 | 12 | 12 | 476,806 | 0 |

- **行为组拒收 10 → 2**，第 8 轮由 DD-1 造成的 10 例误拒**真运行下全部消失**。
- **DD-1 真运行结论：成立，等级已观察**。69 次运行里 36 例声明了 65 个新持续位，
  骨架零删除，终稿 `positions_dropped_new` 与 `positions_introduced_by_gate` 全空。
  第 9 轮挂在推断级前提 R-4 上的那一条，本轮兑现。
- 剩下 2 例逐例查清，**没有拿「数字降了」当结论**：
  - `B15-DIR-02-topic-to-brief` = **误报**。`本周期` 里的 `本周` 被当成周期词，
    「本周期最重要的一条」这个选择性量词被读成 `1 条/周`。修法 DD-5，版本化冻结于
    `M3_REBIND_007_FROZEN_v1.0.md`（后继版本，不覆盖 REBIND-006）。
  - `B09-5-no-market-data` = **真拒**，闸门行为正确，属独立的产品行为失败，见下。
- **DD-5 零模型全量重放**：主轴（本轮 v1.5 落盘草稿 69 次）拒收 2 → 1、新增 0；
  回归轴（第 9 轮 64 次）拒收 13 → 2（`E07`/`E08`）、新增 0。预检五项全过：
  误报 6→4 新增 0；漏检丢失 64 处 **64/64 机械判定为旧判据自身的误抓**、真漏检 0；
  具名族负例 3/3、正例 6/6；消融两轴都变；`E07`/`E08` 穷举不变性 4/4、8/8 无反例。
- 按 A5 又删掉一处自己写出来、量不出差别的守卫：`SELECTIVE_PREFIX`（`最…的` 紧贴数字不计速率）。
  在 133 次运行 × 2 份正文上改变**零个**阻断结论，退回成如实披露的已知漏检 **R-5**。
- `G1-A-goal-long-term-value` 一次传输失败**未产出草稿**，本轮**未重跑**（重跑是模型调用）。
  按 `diyu-infra` 判据查过 MTU：宿主与全部容器都是 1420，**该病因排除**。保真组因此是 8 组不是 9 组。
- 一处自我更正：先前说 B15 的误报"多花了一次补齐调用"，核对节点级记录后**不成立**——
  该草稿本来就缺整个审计块、漏了参考文件加载状态、还泄漏了内部字段名 `primary_job`，
  补齐调用无论如何都会发生。
- 收到 Founder 权威事件 `SINGLE_FROZEN_DIFY_TEST_SET_ACCEPTANCE` 后**立即停止全部模型调用**：
  A/B B 臂未启动、36 名盲评者未启动、无任何其他 DeepSeek 调用。
- 证据：`evidence/ep06-runtime-fidelity-dify-v15/`、`evidence/ep06b-runtime-behavior-v15/`、
  `evidence/ep07-longitudinal-v15/`、`evidence/ep32-formal-v15/`、`evidence/ep33-rebind007-v151/`；
  报告 `M3_STAGE2_V15_REPORT_AND_REBASE_v1.0.md`、`M3_B09_5_HIGHEST_FAILING_NODE_v1.0.md`。

**B09-5 最高失效节点（零模型定位，读的是 Dify 已存的节点级执行明细）**：

- **失效节点 = 主生成 LLM 节点「单账号持续运营决策」**。
  `completion_tokens=133`、`finish_reason=stop`、`reasoning_content` 长度 0、latency 4.22s。
  不是传输、不是截断、不是闸门误判、不是下游节点吃掉正文。
- **闸门与补齐节点没有代写正文**：`needs_fix=no` ⇒ 补齐节点返回 `NO_CHANGE`；
  `确定性取稿` 的 `final_text` 长度 **0**；路径 `hard_fail_no_repair`。
- 失效签名跨版本一致：推理通道里只有一个反引号，然后一个（有时被代码围栏包住的）
  `<<AUDIT>>` 块，没有正文。446 次有草稿的运行里命中 3 次
  （`B09-5` 在 v1.3、v1.5 各一次；`E09` 在 v1.2 一次）。
  `B09-5` 这一格 **2/6**，95% CI `[4.3%, 77.7%]`；其余全部运行 1/440。区间很宽，
  **不能说 33% 是稳定失效率**；能说的是它不是一次性偶发，且这一格显著高于其余。
- **SKILL.md 需不需要改**：`O-6` 已经写死「外部市场资料整格为空时照常给出完整判断」
  并附了 ❌/✅ 例——**不是没写，是没被执行**。需要加的是**输出形状**硬规则
  （审计块只能在正文之后、正文不存在时不许单独输出；审计块不加代码围栏），
  因为 SKILL.md 里唯一的围栏模板就是审计块。**这条因果是推断级，本轮不改，等新授权。**


### A-11 · 第 11 轮：最终候选 v1.5.2 + 零模型技术闭合 + Founder 七场景实测包（2026-08-27）

**执行侧模型调用：0 次。** DeepSeek、Qwen、A/B、盲测、盲评、多轮评测、G1-A 补跑，一个都没启动。

**重入核验（写入前先做）**：Prompt 与合同哈希逐字节相符；三份冻结报告哈希相符；
规划侧唯一入口哈希相符；远端任务分支 `5e1b6ee`、远端 main `a7b8101` 与合同记录一致。

**v1.5.2 的 Skill 变化面 —— 恰好两处，一行不多**（`Z1` 机械判定）：

- 新增两条硬规则，逐字取自合同 `final_candidate.approved_skill_delta`：
  `审计块只能出现在正文之后；正文不存在时不许单独输出审计块。`
  `审计块不加代码围栏，前后不加任何三个反引号标记。`
- 删掉审计块模板外层的 ```` ```text ```` 与 ```` ``` ```` 两行，让模板与第二条规则一致。
- 审计块字段清单逐字节未变；`O-6` 整节逐字节未变（**没有新增 AC-09 同义提醒**）；全文其余部分逐字节未变。
- `SKILL.md` sha256 `245ee2ab…` → `90596da5…`。

**零模型技术闭合六项全过**（`ep34-candidate-v152-closure/ZERO_MODEL_CLOSURE_V152.json`）：

| 项 | 结果 |
|---|---|
| Z1 Skill 静态一致性 | 变化面恰好是批准的两处 |
| Z2/Z5/Z6 全量重放 | 主轴 69 次 2→1、回归轴 64 次 13→2；`B15-DIR-02` 不再误拒；**新增拒收 0** |
| Z3 审计块不得单独构成交付 | 7/7 —— 3 份**真实退化草稿** + 4 份机械构造变体，全部硬门开火、`hard_fail_no_repair`、周期状态拒收、且交付里没有一个字是代写的 |
| Z4 E07/E08 真拒不变性 | 穷举 4/4、8/8，无反例 |
| Z7 四层分离 | 133 份正文：闸门正文里每个字符要么来自草稿、要么来自 `render_body` 那张封闭替换表；直发路装配逐字返回；两次跑逐字节相同 |
| Z8 凭据扫描 | 逐字节精确 + 通用形态，0 命中 |

> Z3 与 Z7 的判据在第一版写错过，两条都是**我把判据写严了**而不是闸门有缺陷：
> Z3 曾要求 `final_text` 长度为 0 —— 但模型自己留下的 ``` 或一句寒暄本来就该原样留着，
> 抹掉它们反而是执行侧在改模型输出；Z7 曾要求"闸门一个字都不许加" ——
> 但 `render_body` 的设计就是把参考文件路径和 `LOADED` 换成人话。
> 两处都改成了机械可判的正确形式，改的是判据不是实现。

**部署**：只部署到任务专用 App `b7fb5b1a…`。图哈希 `aeb2bb86…` → `91980f1a…`，
形状仍 7 节点 6 边，模型与温度未变，已发布版本名 `m3-cand-v1.5.2`。
已发布系统提示词全文读回，与 `SKILL.md` + 参考占位符**逐字节相等**（`3a3c657d…`）。
浏览器渲染画布核验：7 节点 6 边、七个标题全在、无 `http_request`／`tool` 节点。

**导出与恢复演练**（`ep37-rollback-drill-v152/`）：导出 DSL 19.8 万字符 → 快照草稿 →
故意把边删到只剩一条 → 核实确实坏了 → 用快照恢复 → 恢复后与快照**逐字节相同** →
已发布版本全程未变。生产未触及。

**Founder 七场景实测包**（`account-operations/founder-pack-v152/`）：

- 七条输入里**五条逐字取自已落盘的真实运行记录**（S1=B02-3、S3=B04-1P、S4=B09-5、
  S5=E07、S6=B15-DIR-02），两条由冻结记录**机械改写**（S2 只替换两行目标槽位、
  S7 的 `account_context` 一个字未改），改写处逐条列明、可复算，
  **没有新增任何商品／库存／价格／面料／顾客／经营事实**。
- 每个场景给足 14 项材料：真实问题、唯一验收目的、产品义务、硬失败条款、
  逐字可复制输入、真源路径与 SHA-256、逐字核验、App 与候选确认方法、逐步操作、
  不得改动项、三种结局怎么区分、要保存什么、Founder 的自然语言观察问题、
  执行侧初步专业判断、结果回交路径。
- 独立复算七项全过（`ep38-founder-pack-verify-v152/`），含**对线上实物**的绑定核验
  与 A5 两两消融（任一场景都不被另一个单独场景包住）。
- `S4` 的初步判断里如实写明：446 次历史运行里 3 次只吐审计块、其中 2 次就在这个输入上
  （6 次里 2 次，95% CI `[4.3%, 77.7%]`）；两句新规则**有没有用只有 Founder 这一次运行能给出观察**，
  零模型验证证不到。

**声明上限（本轮不得越过）**：`v1.5.2` 的两句规则对 B09-5 的效果等级是**推断**，
不是已观察、不是已修复、不是 PASS。历史 69 份模型草稿只作诊断历史，
不冒充 v1.5.2 的产品运行证据。


### A-12 · 第 12 轮：Founder 七场景实测的只读提取与绑定（`CONTINUE_TASK`，2026-08-27）

**授权事件**：Founder 给出 `M3_FOUNDER_ACCEPTANCE = PASS`（`accepted_candidate = v1.5.2`、
`accepted_test_set = S1-S7`、`founder_observed_all_outputs = true`、
`founder_test_runs_completed = 7/7`），并授权执行侧从任务专用 Dify App 后台
**只读提取**七次运行，完成剩余收口。**本轮执行侧模型调用：0 次。**

**做了什么**

- 枚举该 App 全部 **641 条** workflow 日志，按 `created_from` 分离：
  `web-app` **8 条**（Founder 本人）、`service-api` **633 条**（执行侧历史运行，全部排除）。
  **没有按「最近七次」选记录。**
- 绑定用逐字输入哈希交叉定位：App ID + 已发布版本 + 三段输入的逐字内容与 SHA-256 +
  运行时间 + `FREEZE_MANIFEST` 场景绑定 + workflow run / node execution 记录。
  七个场景各自唯一命中。
- 八条运行的完整记录与全部 7 个节点执行记录落盘
  （`evidence/ep39-founder-seven-run-extraction/raw/<run_id>/`），零截断。
- 逐场景结果目录落盘（`founder-pack-v152/results/S1..S7/`，98 个文件），
  含输入三段、终稿、原始草稿、闸门与复检报告、持续位、审计块、节点记录、`run_meta.json`。

**核验结果（九项）**：`V1` `V6` `V7` `V8` `V9` PASS；`V2` `V3` `V4` `V5` FAIL。

**两项实测新证据**

- `ep34` 的 `Z7` 当时显式声明零模型覆盖不到补齐路。本轮 Founder 的七次运行里有 **3 条真走了
  补齐路**（S1/S3/S5），补齐节点原始输出已落盘，这一层现在有实物可验：
  **8/8 无代写**（判据：终稿每个字符必须来自模型产物或 `render_body` 那张封闭替换表，
  子序列判定、只许删不许插）。
- 用**仓库里的 v1.5.2 代码**对同一份草稿重算 `gate` / `assemble` / `post_gate`，
  与线上记录比对：**8/8 三个节点逐字节相同**。线上确定性代码与仓库代码行为等同，
  这是实测不是声明。
- `S4`（历史退化那一格）本次**未退化**：闸门 `CLEAN`、直发路、终稿 2680 字、
  `finish_reason = stop`。**n=1**，只证明这一次没失效，不上推成「已修好」。

**四个真实缺口（全部据实记录，不做闭合）**

1. **7/8 条运行跑在一个未命名的重新发布版本上。** Founder 运行期间 App 被重新发布：
   冻结候选 `706fdce0…`（`m3-cand-v1.5.2`）→ 实际承载 S2–S7 的
   `ff801653…`（`marked_name` 为空）。差异逐项算过，**全部落在画布外观层**：
   节点 `position`/`height`、边多了前端标记 `isInLoop`、`viewport` 平移缩放。
   **七个节点的 `data`、六条边的拓扑、系统提示词 SHA-256（八条全部 `3a3c657d…` = 冻结值）、
   模型/provider/温度，全部逐字节相同。**
   结论分两半、不合并：可执行内容绑定**成立**，已发布版本标签绑定**不成立**。
2. **S6 提交了两次**（`55eb0a6b…` 与 `0a0f406d…`），输入逐字节相同、都成功、都产出正文，
   因此第二次不属合同允许的重跑。两条全部保留。Founder 声明 `7/7` 而实际提交 8 次，
   **Founder 判的是哪一份 S6 输出，后台证据不能唯一确定** —— 场景级证据歧义，不择优。
3. **`user_request` 八条一律多一个结尾换行**（`account_context` 与 `loaded_references`
   八条全部逐字节相同）。形态统一、只在结尾、无内容差异，是从代码块复制的机械痕迹，
   但逐字不等于冻结包，据实记为差异。
4. **提取完成后 Dify 实例数据库被清空**：容器栈重启、PostgreSQL 走 initdb 全新初始化、
   `apps` 表 0 行、`setup` 回到 `not_started`。**本轮对 Dify 只发过 GET。**
   七场景全部原始证据已在此事件之前落盘，不受影响；受影响的是往后的动态绑定复验
   与活体回滚演练。重建路径仍在盘上（`ep37` 的完整 DSL 导出件）。

**产出**：`M3_FOUNDER_SEVEN_RUN_CLOSEOUT_v1.0.md`、
`evidence/ep39-founder-seven-run-extraction/`（含 `FOUNDER_RUN_VERIFICATION.json`）、
`founder-pack-v152/results/S1..S7/`、
`tools/founder_extract/`（`extract_founder_runs.py` / `verify_founder_runs.py` /
`make_closeout_v153.py`）。

**本轮不判 `DONE`**：授权 §4 要求「Founder 实际看到的不是冻结 v1.5.2 …… 必须将受影响项
标记为 `NOT_VERIFIED` 并报告精确差异，不得伪造闭合」。`M3-AC-00` 与 `M3-AC-20`
现为 `NOT_VERIFIED`，DONE 不可推导，按授权保持 `IN_PROGRESS`。

---

## L4 · 已排除路线（历史留痕，只加不改）

| 路线 | 根因假设 | 干预 | 关键前提 | 证据 |
|---|---|---|---|---|
| **用 `INIT_PASSWORD` 重置既有 Dify 账号口令** | 以为该变量能重置口令 | 读 `controllers/console/init_validate.py` 源码 | 该变量只在**首次**建管理员账号时校验；本实例 setup 早已 `finished` | 会话内源码核验；已改用官方 `flask reset-password` |
| **用 `dify-platform-expert` MCP 取 Dify 真相** | 以为它连的是本实例 | 核对其自述端点与版本 | 它自称 `localhost:8080` / `v1.9.2`，真实是 `localhost:80` / `v1.16.1` | `M3_CHECKPOINT_ROUND_2.md` §8 |
| **两个取证进程并发写同一证据目录** | 后台进程未被正确终止，与新进程同时写 | 杀掉两个进程、整目录作废、单进程重跑 | 证据来源可辨识性 > 已花掉的调用成本 | 本轮，见 `M3_CHECKPOINT_ROUND_4.md` |
| **目标模型不可用时改用工作区内其他模型** | 想绕过余额耗尽 | **未执行** | Prompt §12.2 明确禁止临时换更容易通过的模型；`tongyi`/`moonshot` provider 虽 active，一律未使用 | — |
| **在闸门或补齐节点里给零正文兜底** | 以为可以让确定性节点替模型补一段正文，保住交付 | **未执行** | SKILL.md〈最低实质产出〉已记过代价：曾有一次模型零正文、补齐环节写了一句话、复检据此宣布"缺口已闭合"，23 个字符的空交付拿到合规章。防护装置制造虚假信心比没有防护更危险。Founder 第八节第 14 条同样列为不得 PASS | 本轮 `B09-5` 记录：`final_text` 长度 0、`hard_fail_no_repair` |
| **取消盲评后把旧 `AC-18` 追溯判成 PASS** | 想用"路径已取消"换一个通过 | **未执行** | Founder 第二节第 5、6 条逐字禁止追溯改写与追溯上推；A2 棘轮律同向 | 历史 `AC-18` 保持 `NOT_VERIFIED`，后继合同记 `NOT_APPLICABLE` |
| **`SELECTIVE_PREFIX`（`最…的` 紧贴数字不计速率）** | 以为「本周最重要的一条」这族需要专门守卫 | **写出来后按 A5 删除** | 在 133 次运行 × 2 份正文上改变零个阻断结论：`B15-DIR-02` 已被 DD-5 清掉，`FX-M3-HOLD-02__B` 已被 DD-3b 清掉。没有差别的单元不该存在 | 退回成披露 R-5，见 `M3_REBIND_007_FROZEN_v1.0.md` §5 |
| **把「可执行内容逐字节相同」当成「版本标签绑定成立」** | 想用已证明的内容一致换掉标签不符这个缺口 | **未执行** | A2 棘轮律：等级不能因为改写、并置或自述往上走；授权 §4 明确要求把受影响项标 `NOT_VERIFIED`。版本标签属有权者裁定，不是执行侧能给的 | `ep39` 把 V4 拆成两半分别记数：可执行内容绑定成立、标签绑定不成立 |
| **在 S6 两条运行里择优选一条当作 Founder 判过的那份** | 想把 `7/7` 凑齐 | **未执行** | 授权 §2 逐字禁止择优选择输出；两条输入逐字节相同、都成功，无法用证据区分 Founder 读的是哪一份 | 两条全部原样保留，第二次存 `results/S6/extra_second_submission_0a0f406d/`，歧义据实上报 |
| **重建被清空的 Dify 实例以补做动态绑定复验** | 想让 `dynamic_dify_binding_requires_refresh` 重新可满足 | **未执行** | 本轮授权只含只读提取与收口，不含重建；重建会产生新的 App 与新的运行记录，制造第二个绑定对象 | `ep37` 的完整 DSL 导出件在盘上可随时重建，等授权 |

---

## L5 · 外部副作用（历史留痕，只加不改）

| 时间 | 目标 | 操作 | 标识 | 状态 | 回滚 |
|---|---|---|---|---|---|
| 2026-08-26 | Dify（本机 `localhost:80`，`v1.16.1`） | 创建 **一个** task-id 专用候选 App | `b7fb5b1a-9278-426c-bb8a-f9f288639548` | 已创建并发布，版本 `2026-08-26 17:06:34.276971`（workflow id `92784dcb-06ac-4274-96c6-ed9e4cba964d`） | DSL 已导出至 `evidence/ep10-closeout/m3_candidate_app.dsl.yaml`；导出→损坏→恢复演练通过 |
| 2026-08-26 | 同上 | 为该 App 签发 **一个** Service API Key | 值只存在于 scratch，**未进仓库**（已 grep 核验） | 有效 | 删除该 key 即失效；不影响其他 App |
| 2026-08-26 | 同上 | 该 App 的 draft 被**故意损坏后恢复**（回滚演练） | 见 `evidence/ep10-closeout/dify_rollback_drill.json` | 已恢复，图 sha256 与备份逐字节一致 | 已完成 |
| 2026-08-26 | DeepSeek API | 约 143 万 token 真实计费调用 | 逐次 `workflow_run_id` / `id` 记在各 `evidence/*/​_run_index.json` | 账户余额耗尽（`-1.06 CNY`，`is_available:false`） | 不可回滚（已发生的计费） |
| 2026-08-26 | Dify 口令 | Founder 本人在宿主机执行 `flask reset-password` 重置 Console 口令 | — | 成功 | 由 Founder 自行处置 |
| 2026-08-26 | 远端 `origin` | **推送任务分支：未执行** —— 被本机权限分类器拦截两次 | — | `NOT_DONE` | 无需回滚 |
| 2026-08-27 | Dify 任务专用 App `b7fb5b1a…` | 部署候选 **v1.5**（三个代码节点源码内联更新），发布 | 图哈希 `3bc0950b…` → `aeb2bb86…`，已发布版本 `2026-08-27 16:56:46.979840`，形状仍 7 节点 6 边 | 已发布 | 旧 DSL 已导出留存；回滚 = 重新内联上一版代码节点并发布 |
| 2026-08-27 | DeepSeek API | 第 2 段正式取证 **2,937,367 tokens** 真实计费调用（保真 9 + 行为 49 + 纵向 12 = 70 次） | 逐次 `workflow_run_id` 记在各 `evidence/*-v15/*.json` | 已发生 | 不可回滚（已发生的计费） |
| 2026-08-27 | Dify Console API | 读取 `B09-5` 那次运行的**节点级执行明细**（`GET …/workflow-runs/…/node-executions`） | run `8a58d1d6-2635-4d6f-aedc-19719ef249fb` | 只读，无写入 | 无需回滚 |
| 2026-08-27 | Dify 任务专用 App `b7fb5b1a…` | 部署最终候选 **v1.5.2** 并发布 | 图哈希 `aeb2bb86…` → `91980f1a…`，已发布版本名 `m3-cand-v1.5.2`，发布时间 `2026-08-27 19:46:47.281053`，形状仍 7 节点 6 边 | 已发布 | DSL 全量导出件 + 草稿快照见 `evidence/ep37-rollback-drill-v152/`；演练已证明可逐字节还原 |
| 2026-08-27 | 同上 | 导出与恢复演练：故意损坏草稿后用快照恢复 | 恢复后草稿图 sha256 与快照**逐字节相同**；已发布版本全程未变 | 已恢复 | 已完成 |
| 2026-08-27 | DeepSeek / Qwen / 其他模型 | **本轮执行侧模型调用：0 次** | — | 未发生 | 无需回滚 |
| 2026-08-27 | Dify Console API（App `b7fb5b1a…`） | **只读**提取 Founder 七场景实测：`workflow-app-logs` 全量枚举、8 条 `workflow-runs`、8×7 条 `node-executions`、已发布版本谱系 | 641 条日志普查；8 个 run_id 见 `ep39` | 只读，无写入、无修改、无删除、无重放 | 无需回滚 |
| 2026-08-27 | Dify 本机实例（外部事件，**非本任务操作**） | 容器栈重启后 PostgreSQL 走 initdb 全新初始化，`apps` 表 0 行、`setup` = `not_started`，该 App 与 641 条运行记录已不在该实例上 | PGDATA 内每个文件均为 `2026-08-27 21:39` UTC 新建 | 已发生；起因不在本任务范围内 | 重建路径：`evidence/ep37-rollback-drill-v152/m3_candidate_app_v152.dsl.yaml`（sha256 `bd676f29…`，含 v1.5.2 全部改动），**本轮未执行重建，未获授权** |
| 2026-08-27 | DeepSeek / Qwen / 其他模型 | **本轮（第 12 轮）执行侧模型调用：0 次** | — | 未发生 | 无需回滚 |

**明确未发生的副作用**：未创建第二个 Dify App｜未修改任何非任务 App、凭据、知识库或运行记录｜未切换任何生产流量｜未 merge/直推 `main`｜未 force/amend/reset/squash｜未改写历史｜未发布到任何真实社交平台｜未在 M2 中新建 workspace（本轮复用第 2 轮已存在的取证 workspace，未新增）。

---

## L2 · 当前状态与下一动作（当前投影，变化时直接替换）

```text
进度        IN_PROGRESS（存在真实证据缺口，DONE 不可推导；按授权保持 IN_PROGRESS）
进入模式     CONTINUE_TASK —— 同一 task_id，不建 NEW_TASK，不修改合同
当前合同     M3_ENGINEERING_TASK_CONTRACT_v1.3_FOUNDER_SINGLE_SET_REBASE.yaml（49021e60…）
最终候选     v1.5.2 · SKILL.md 90596da5… · 系统提示词 3a3c657d…
Founder 裁决 M3_FOUNDER_ACCEPTANCE = PASS（accepted_candidate = v1.5.2，S1-S7，7/7）
七次运行     8 条 web-app 运行全部提取并唯一绑定；证据见 ep39 与 results/S1..S7
执行侧模型调用 本轮 0
Dify 实例    数据库已被清空（外部事件，非本任务操作）；证据已在此之前落盘
```

**回执**：

```text
M3_ENGINEERING_TASK              = IN_PROGRESS
M3_FOUNDER_PRODUCT_ACCEPTANCE    = PASS
FOUNDER_TEST_RUNS                = 7/7_BOUND_AND_PRESERVED（另有 1 次 S6 重复提交，一并保留并披露）
EXECUTOR_MODEL_CALLS_AFTER_REBASE = 0
BLIND_REVIEW                     = NOT_APPLICABLE_BY_FOUNDER_REBASE
MODULE_AB_GAIN_VS_GOOD_PROMPT    = NOT_CLAIMED
MAIN_MERGE                       = NOT_AUTHORIZED_NOT_PERFORMED
M5                               = NOT_STARTED_NOT_AUTHORIZED
REAL_BUSINESS_LIFT               = NOT_VERIFIED
```

**AC 汇总**：`M3-AC-01`–`M3-AC-17` 判 `PASS`（确定性证据 + Founder 七场景整体 PASS）；
`M3-AC-00` `NOT_VERIFIED (INSUFFICIENT)`（已发布候选版本标签对 7/8 条不成立、
`user_request` 逐字不等于冻结包）；`M3-AC-20` `NOT_VERIFIED (ABSENT)`（Dify 实例已清空，
动态绑定复验与活体回滚入口不可复演）；`M3-AC-18` / `M3-AC-19`
`NOT_APPLICABLE_BY_FOUNDER_REBASE`，历史 `NOT_VERIFIED` 记录原样保留。

**失效面（A3，不多算不少算）**：缺口 1 只影响版本标签，不影响 Founder 所观察内容由哪套逻辑
产出 —— 系统提示词、七个节点 `data`、边拓扑、确定性代码行为八条全部证明与冻结候选相同，
故 `AC-01`–`AC-17` 不随之失效。缺口 2 只使 S6 的**产物身份**存疑，两份都在、都非退化。

**下一动作（需 Founder 裁定，执行侧不得自裁）**：

1. 那次未命名的重新发布（只含画布几何与一个前端标记的差异）算不算同一个冻结候选？
   算 ⇒ `M3-AC-00` 可闭合，`DONE` 可推导；不算 ⇒ 本次实测的绑定对象不是冻结候选。
2. S6 的两份输出中，Founder 当时读的是哪一份？（两份都已保留，执行侧不择优。）
3. Dify 实例已清空，是否授权用 `ep37` 的 DSL 导出件重建以恢复动态绑定复验能力？

**声明上限**：本轮只能说「绑定 v1.5.2 可执行内容的 M3 候选，在一组事前冻结的七个 Dify 输入上
真实运行并获得 Founder 产品接受；七次运行原始证据完整保留可逐条回指；确定性组件在这八次
真实运行中没有代写过任何交付内容」。不得声称优于一份好提示词、M5 成品增益、已生产上线、
真实经营提升或因果增益；也不得把「两句新 Skill 规则修好了 B09-5」从**推断**上推 —— 本轮只
多了 1 次未退化的观察。
