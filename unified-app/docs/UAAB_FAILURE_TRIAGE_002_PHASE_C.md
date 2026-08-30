# FAILURE TRIAGE 002 · Phase C 首轮两条 FAIL（夹具缺陷 ＋ 一处真实健壮性缺口）

`task_id: DIYU-V1-UAPP-ACCEPTED-ARTIFACT-BINDING-001`
发生时点：**任何模型调用之前**。模型调用 0，Dify 写入 0（当时 draft 尚未同步）。

## observed_failure

Phase C 首轮 10/12，`C-04` 与 `C-11` FAIL。

## C-04 · `CHECKER_OR_FIXTURE`

我给「未点名上游能力」这一支写的用例是「接着把这条的口播稿再顺一遍。」——
但「口播稿」本身就在 `MENTION` 表里，映射到 `CREATIVE_SCRIPT`。
所以选择器**正确地**解析成了 CS，是我的断言（期望 PD）写错了：那根本不是未点名用例。

**修复**：未点名用例改为「再给我一版标题和封面。」（不含任何能力词），
并把原用例保留为**第三个**子用例，断言点名 CS 时确实解析到 CS。
实现一个字未改。

## C-11 · 两个问题叠在一起

### (a) 变异被另一条独立条件遮蔽 —— `CHECKER_OR_FIXTURE`

`compatible_and_not_self` 的负控制夹具用的是 `PP_NEW`（未接受的 PP 产物）。
去掉自上游禁令后，它仍然被 `NOT_ACCEPTED` 拦住，所以没有翻转——
**遮蔽，不是覆盖缺口**。

**修复**：夹具换成 `PP_ACC`（已接受、未 STALE 的 PP 产物），
让兼容性成为唯一拦阻理由。

### (b) 隔离该条件必须双点变异 —— 冗余，如实记录

兼容性由两道守卫实现，且对任意 `cap` 二者必然同时命中（`COMPAT[tgt]` 永不含 `tgt`）：

```
if   cap == tgt:        why = "SELF_UPSTREAM_FORBIDDEN"
elif cap not in order:  why = "CAPABILITY_INCOMPATIBLE"
```

单独去掉任一道，拒绝**仍然成立**，只是留下的证据不同：

| 变异 | 结果 | 拒绝理由 |
|---|---|---|
| 基线 | 拒绝 | `SELF_UPSTREAM_FORBIDDEN` |
| 只去掉自上游禁令 | 仍拒绝 | 变为 `CAPABILITY_INCOMPATIBLE` |
| 只放宽兼容清单 | 仍拒绝 | 仍是 `SELF_UPSTREAM_FORBIDDEN` |
| 两道同时去掉 | **放行** | —— |

按 A5，这两道守卫**不可互换**（去掉任一道，产出的证据串会变，而 C-09 正是靠
`SELF_UPSTREAM_FORBIDDEN` 这条证据判定的），因此都不删；
但隔离该条件必须双点变异。这一点连同上表一起落在
`UAAB_PHASE_C_CONTROLS.json` 的 `guard_redundancy_probe` 里，不藏。

### (c) 一处真实的健壮性缺口 —— `SYSTEM_UNDER_TEST`（我自己新写的节点）

做双点变异时崩了：

```
ValueError: max() arg is an empty sequence
```

原因：`cands` 非空但没有一条的能力在优先级清单 `order` 里时，
`best_cap` 为 `None` → `pool` 为空 → `max()` 抛错。
未变异的代码走不到这条路径，但**一个 fail-closed 组件里不该留崩溃路径**。

**修复**（在我本轮新增的 `uapp_pick_upstream` 内，模型调用之前）：

```python
if best_cap is None:
    return _fail("NO_LEGAL_UPSTREAM", "…", "候选存在但均不在兼容优先级清单内：…")
```

这是本轮唯一一处**实现侧**改动，来自变异测试的发现，不是为了让某条控制变绿——
它让 fail-closed 变成真正无死角。

## 重新验证

修完后重跑**完整 12 条**（含正向控制、五条单点/双点变异、原始失败用例、保护面回归）：
**12/12 PASS**。证据：
`unified-app/evidence/stages/uapp_artifact_binding/UAAB_PHASE_C_CONTROLS.json`。

## protected_targets（未改）

`uapp_fields` 血缘门、`uapp_state` 账本、Hop 抽取 Prompt、Seam、M1/M2/M3、
其余五能力、PP b2、M2 schema 与 API、`main`。
