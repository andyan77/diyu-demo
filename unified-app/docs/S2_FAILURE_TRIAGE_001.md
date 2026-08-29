# FAILURE TRIAGE 001 · S2 attempt01

`task_id: DIYU-V1-UNIFIED-DIFY-APPLICATION-001` ｜ stage `S2` ｜ 2026-08-29

绑定判据 `S2_STAGE_GATE_v1.0`（sha256 `2a10cd97…a951`），绑定图 `f099ac7a…`。
判定结果：`S2-POS-01 FAIL` / `S2-NEG-01 FAIL` / `S2-REG-ASK-01 PASS`。

---

## observed_failure

两处，各有独立证据，互不派生。

**A. 夹具写入失败。** `POST /workspaces/{ws}/accounts/{acct}/cycles/decisions` 返回 `422`，
原文 `decision must be 'adjusted' or 'kept_unchanged'`；
`diyu_business.cycle_decisions` 中该 `idempotency_key` 行数 = `0`。
证据：`evidence/stages/attempt01/S2-POS-01.json` → `seed.write`。

**B. 无记录被报成有记录。** 在一条决策都没有的任务域里，
`uapp_s2_pending.m2_state = reachable_with_record`，回复正文说
「我已经把这个号目前在系统里记录在案的情况读出来了」。
同一轮 `uapp_ctx.account_context` 却写着 `最近一次周期决策：none_recorded`。
证据：`evidence/stages/attempt01/S2-NEG-01.json` → `N1/N2` 两轮均如此。

## frozen_target

Rebase Prompt §6 判据 3：**查不到就如实返回缺口，不把空响应升级成已知事实。**

## candidate_sources

`CONTRACT_OR_INTENT` / `ORACLE_OR_CRITERION` / `CHECKER_OR_FIXTURE` /
`INPUT_ENVIRONMENT_OR_TOOL` / `SYSTEM_UNDER_TEST` / `INSUFFICIENT_EVIDENCE`

## confirmed_origin

**A = `CHECKER_OR_FIXTURE`。** 独立证据：M2 返回的 422 正文直接指名约束
（`decision` 是枚举，只接受 `adjusted` / `kept_unchanged`），夹具传了散文。
被测对象没有参与这次失败——请求根本没被接受。

**B = `SYSTEM_UNDER_TEST`，最高失效节点 = `uapp_s2_pending`（本层新增节点）。**
独立证据链，三条互相印证：

1. `seed.before` 显示 M2 在无决策时返回 **`200 {"decision": "none_recorded"}`**
   —— 用哨兵值，而不是 404。这是环境的既有行为，不是缺陷。
2. `uapp_ctx.account_context` 如实渲染出 `最近一次周期决策：none_recorded`
   —— **`uapp_ctx` 判对了**，它读的是载荷。
3. `uapp_s2_pending` 只解析 `m2_note` 里的状态码，`decisions/latest=200` 即判「有记录」
   —— 判错的是它，它读的是状态码。

因此最高失效节点是我本层新增的 `uapp_s2_pending`，**不是** `uapp_ctx`，
也不是 M2，也不是判定器。

### 一条自我更正

`uapp_s2_pending` 的这版逻辑，本来就是我在建 S2 时为了修正
`uapp_ctx.m2_reachable = (cycle 200 AND decision 200)` 的混同而写的。
我当时把「不能用合成 flag」改对了，却把「改用状态码」这一步做错了——
**状态码和 flag 一样都不是载荷。** 正确的判据来源自始至终只有一个：M2 返回的 `decision` 值本身。

## mutation_target

本轮允许修改的最小对象，两个，各自对应一条已确认的失效：

- `S2_RUN_v1.0.py::do_seed` 的请求体 —— 对应 A；
- `S2_BUILD_v1.0.py::S2_PENDING_SRC` 及其入参 —— 对应 B。

另修判定器一处硬编码期望值：原先写死夹具散文 `"收敛到一条主线"`，
夹具修正后该串不再出现。改为**从 SEED 实际写入的 `decision` 值反查投影**，
期望由被写入的事实自己决定，无法通过「改期望迁就结果」凑过。
并给 `S2-NEG-01` 增补一条判据：无记录判定必须来自载荷——
要求 `decisions/latest=200` 成立**且** `decision_seen` 为哨兵值，
这条恰好把 attempt01 的错误方式排除在外。

## protected_targets

以下对象本轮**零改动**，因为没有任何证据证明它们有错：

- `uapp_ctx`（它判对了，见证据链第 2 条）
- M1 六个复用节点、M1 源应用
- M2 服务与既有数据
- 最终 FP M3 / Seam / 六能力 / Hop、旧 Canvas、旧候选 app
- `S1_STAGE_GATE_v1.0` 与 S1 的全部结论
- `S2_STAGE_GATE_v1.0` 的 `cases` / `leak_forbidden_tokens` / `gate_rule` /
  `applicability_rulings` 四个块 —— v1.1 与 v1.0 逐字节一致，已用哈希证明

## next_reverification

按原冻结目标执行定向复验，判据不放宽：

1. 正向控制：`S2-POS-01`，SEED 写入必须 `200/201` 且数据库有行，T2 必须读到该值；
2. 负向控制：`S2-NEG-01`，必须判 `reachable_no_record`，且该判定必须来自载荷；
3. 原始失败案例：以上两例即 attempt01 的原始失败案例，同输入重跑；
4. 原冻结验收：`S2_STAGE_GATE_v1.1`，判据四块与 v1.0 哈希相同；
5. 受影响范围回归：S1 三例（由 `S2-NEG-01` 两轮与 `S2-REG-ASK-01` 承担）+
   确定性检查 12 项。

## 影响面（A3）

图从 `f099ac7a` 变为 `780503f5`，因此：

- attempt01 的三份结论**全部置 `STALE`**——包括原判 `PASS` 的 `S2-REG-ASK-01`，
  它绑定的图已变，不因为"那条没坏"就免于复验；
- S1 层结论**不失效**：S1 的判据绑定 `S1_STAGE_GATE_v1.0` 与图 `d36cc01d`，
  但 S1 三例已由 S2 层的回归用例在**新图上**重新覆盖，故 S1 的行为主张在新图上另有独立证据；
- 受保护面零漂移，11 个应用 `graph_md5` 与 R0 基线一致（D-S2-11 复算）。

attempt01 的原始证据保留在 `evidence/stages/attempt01/`，**不删除、不覆盖、不改绿**。
