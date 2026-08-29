# FAILURE TRIAGE 001 · S4.1 attempt01

`task_id: DIYU-V1-UNIFIED-DIFY-APPLICATION-001` ｜ stage `S4.1` ｜ 2026-08-29

绑定判据 `S4_1_STAGE_GATE_v1.0`（sha256 `83718259…f9f4`），绑定图 `149c593f…`。
判定：`S4-CAP-MATRIX-01 FAIL` / `S4-REG-ASK-01 PASS`。

---

## observed_failure

画布运行 `936e334c-476d-47e0-aef3-e1d61c15a858` **failed**，
`uapp_delivery` 代码节点抛：

```text
AttributeError: 'dict' object has no attribute 'strip'
```

对外表现为 `/v1/chat-messages` 返回 `HTTP 400`、无 `message_id`、无交付正文。

**但上游整条链是成功的**（这一点必须先说清楚，否则会误判成能力链没打通）：

| 节点 / 应用 | 结果 |
|---|---|
| 画布 `uapp_m3` → `uapp_op_gate` → `uapp_hop` → `uapp_seam` → `uapp_seam_merge` | 全部 `succeeded` |
| Seam 应用自身运行 | `entry_resolver` → `seam_dispatch` → **`tool_matrix`** → `fin_matrix` → `end_matrix` 全部 `succeeded` |
| MATRIX 能力应用 | 1 次运行，`succeeded` @ 16:07:51 |
| 其余五个能力应用 | **runs = 0**，未暗跑 |

也就是说：**目标能力真的执行了，组件 Return 也真的产出了**
（`returns_json` 含 `precise_gap: applicability_reason；expression_boundary`，
`business_delivery_outcome: UNKNOWN`——MATRIX 在输入不足时给的是精确缺口，没有编造产物）。
失败只发生在最后一步：把这些东西投影成自然语言。

## frozen_target

Rebase Prompt §8.1：`M3 决策 → Hop/Seam → 目标能力真实执行 → 组件 Return → 自然语言交付`。
前四段成立，第五段断。

## confirmed_origin

`SYSTEM_UNDER_TEST`，最高失效节点 = **`uapp_delivery` 的入参绑定**，是我在 S4 接线时引入的。

独立证据，自证且不需要另做实验——就在失败节点自己的 `inputs` 里：

```text
seam_user_delivery : {"output": "这一步我还差一样东西才能往下判断：…"}   ← dict
seam_outcome       : {"output": "UNKNOWN"}                              ← dict
seam_returns_json  : {"output": "[{…precise_gap…}]"}                    ← dict
m3_judgment        : "**结论**\n\n就目前的信息…"                          ← 干净字符串
```

同一个节点里，**经聚合器来的值全被包了一层 `{"output": …}`，直接绑到 tool 节点的值没有**。
Dify 的分组变量聚合器（`group_enabled: true`）每个 group 的输出自带 `output` 包装层，
选择器必须写三段 `["uapp_seam_merge", "<group>", "output"]`；我写了两段，
拿到的是那个 dict 本身，`DELIVERY_SRC` 的 `(seam_user_delivery or "").strip()` 当场抛。

**`DELIVERY_SRC` 没有错**——旧候选用的正是同一份代码、同一个聚合器，
它那边写的就是三段选择器。错的是我这一层的绑定。

## mutation_target

`S4_BUILD_v1.0.py` 中 `uapp_delivery` 的四个聚合器来源绑定，各加一段 `"output"`：
`seam_user_delivery` / `seam_outcome` / `seam_returns_json` / `hop_gaps_text`。

`m3_judgment` 与 `m3_gate_status` 保持直接绑到 `uapp_m3`，不改：
`uapp_delivery` 只可能在 `uapp_m3` 之后到达（`uapp_op_gate` 两条分支都在它下游），
直接绑更准，也少一组聚合（A5：不为对称而增加单元）。

## protected_targets

本轮零改动，因为没有证据证明它们有错：

- `DELIVERY_SRC`（旧候选同款代码在三段选择器下工作正常）
- `uapp_seam_merge` 的分组定义本身（包装层是 Dify 的行为，不是它的缺陷）
- Hop / Seam / 六能力应用、M3、M2、M1 六节点、旧 Canvas、旧候选 app
- `S4_1_STAGE_GATE_v1.0` 的 `cases` / `leak_forbidden_tokens` / `gate_rule` /
  `representative_capability` 四个块

## next_reverification

判据不放宽，按原冻结目标定向复验：

1. 正向控制：`S4-CAP-MATRIX-01` 同输入重跑，必须走完到自然语言交付；
2. 负向控制：`S4-REG-ASK-01` 同输入重跑（见下方影响面，它必须重跑）；
3. 原始失败案例：即第 1 条；
4. 原冻结验收：`S4_1_STAGE_GATE_v1.1`，判据四块与 v1.0 逐字节相同；
5. 受影响回归：确定性检查 17 项。

## 影响面（A3）

图从 `149c593f` 变为 `6f3d3e53`，因此 attempt01 的**两份结论一并置 `STALE`**——
包括原判 `PASS` 的 `S4-REG-ASK-01`。它绑定的图变了，不因为"那条没坏"就免于复验。

上游层结论不失效：S1/S2/S3 各自绑定自己的图与判据，
且其行为主张已由本层的回归用例在新图上另行覆盖。

attempt01 的原始证据保留在 `evidence/stages/s4_attempt01/`，不删除、不覆盖、不改绿。

## 附带确认（不属于本次失败，但本轮取到了）

- **不暗跑成立**：Seam 内其余五个能力节点未执行，五个能力应用 `runs = 0`。
- **MATRIX 在输入不足时给精确缺口，不编造产物**：
  `precise_gap: applicability_reason；expression_boundary`，`needs_user_decision: true`。
  这两条是 attempt01 就已成立的事实，与本次修复无关，复验时应继续成立。
