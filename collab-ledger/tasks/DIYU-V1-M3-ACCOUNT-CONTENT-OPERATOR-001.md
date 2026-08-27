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

## L4 · 已排除路线（历史留痕，只加不改）

| 路线 | 根因假设 | 干预 | 关键前提 | 证据 |
|---|---|---|---|---|
| **用 `INIT_PASSWORD` 重置既有 Dify 账号口令** | 以为该变量能重置口令 | 读 `controllers/console/init_validate.py` 源码 | 该变量只在**首次**建管理员账号时校验；本实例 setup 早已 `finished` | 会话内源码核验；已改用官方 `flask reset-password` |
| **用 `dify-platform-expert` MCP 取 Dify 真相** | 以为它连的是本实例 | 核对其自述端点与版本 | 它自称 `localhost:8080` / `v1.9.2`，真实是 `localhost:80` / `v1.16.1` | `M3_CHECKPOINT_ROUND_2.md` §8 |
| **两个取证进程并发写同一证据目录** | 后台进程未被正确终止，与新进程同时写 | 杀掉两个进程、整目录作废、单进程重跑 | 证据来源可辨识性 > 已花掉的调用成本 | 本轮，见 `M3_CHECKPOINT_ROUND_4.md` |
| **目标模型不可用时改用工作区内其他模型** | 想绕过余额耗尽 | **未执行** | Prompt §12.2 明确禁止临时换更容易通过的模型；`tongyi`/`moonshot` provider 虽 active，一律未使用 | — |

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

**明确未发生的副作用**：未创建第二个 Dify App｜未修改任何非任务 App、凭据、知识库或运行记录｜未切换任何生产流量｜未 merge/直推 `main`｜未 force/amend/reset/squash｜未改写历史｜未发布到任何真实社交平台｜未在 M2 中新建 workspace（本轮复用第 2 轮已存在的取证 workspace，未新增）。

---

## L2 · 当前状态与下一动作（当前投影，变化时直接替换）

```text
进度        IN_PROGRESS（本合同不授权终态；本轮不输出任何终态词）
HEAD        见 git；本地领先远端，收口报告提交后推送
状态真源     account-operations/evidence/ep27-ac-recompute-v14/AC_STATE_v14.json
Checkpoint  M3_CHECKPOINT_ROUND_8.md
候选        M3 载体 v1.4.2 · Dify m3-cand-v1.4.2 · 图 3bc0950b…
实测包       v1.0 / v1.1 均 STALE；v1.2 本轮不生成（PAUSE 第 8 条）
```

**AC 汇总**（按绑定计，共 27 个绑定）：成立 8 · 部分成立 1 · `NOT_VERIFIED` 18。

**关键区分**：18 个 `NOT_VERIFIED` 里绝大多数**不是证据缺失，是证据齐备但独立判定被中止**。
行为 49 例、纵向 12 步、保真 9 次、A/B 12 份 + 36 份冻结提示词全部已落盘，
**判定不需要任何新的 DeepSeek 调用**。

**成立的 8 个绑定全部确定性可复算**，没有一个依赖模型判断，也没有一个由
`workflow succeeded` 推出。

**本轮查实、根因在执行侧的四条缺陷**：`DD-1` 补齐骨架不含新增位那一行（8 例纯误拒）；
`DD-2` `G-4` 槽位解析取错权威值；`DD-3` `G-4` 把取舍陈述读成速率主张；
`DD-4` 清单矛盾把账号事实缺口读成附件未加载（非本轮改动）。
最高失效节点：`gate_main.py` 的 `required_audit_lines` 生成。

**下一动作（等 Founder 或规划侧审查，执行侧不自选）**：
`M3_CHECKPOINT_ROUND_8.md` §9 给了三条路（甲 先修再跑一批取证 / 乙 先用现有证据跑判定 /
丙 提交产品级 Rebase），成本与污染面都已量化。**执行侧不选，也不设默认。**
未获新授权前不启动任何模型调用。

