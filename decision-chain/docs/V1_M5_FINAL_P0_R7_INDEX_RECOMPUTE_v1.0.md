# M5 十九维索引与 AC 状态机械重算 v1.0（R7）

- `task_id`: `DIYU-V1-M5-UNIFIED-INTEGRATION-FINAL-ACCEPTANCE-001`
- 候选：`5f84d94d…` / 清单 `v1.1.4` / `M5_BIND=fp`
- 产出：`decision-chain/evidence/m5-final-p0/FINAL_P0_R7_INDEX_RECOMPUTE.json`
- 脚本：`decision-chain/workflows/DIYU_M5_FINAL_P0_R7_INDEX_RECOMPUTE_v1.0.py`
- 十九维映射：从 `DIYU_M5_BUILD_EVIDENCE_INDEX_v1.0.py` **原样 import**，未复写、未改动。
  该映射来自规划侧冻结件，执行侧无权改。
- **不新增十九维案例。**

## 一、本轮多做的唯一一件事：按 A3 算失效面

本轮替换了 M3 successor、六个能力应用与接缝。规则：

```text
证据来自本轮 fp 运行            → CURRENT
证据来自轮前，且穿过被改应用      → STALE，verdict 降为 NOT_VERIFIED
证据来自轮前，不穿过被改应用      → CURRENT，保持原判
依赖关系无法从证据判断           → STALE 待定向复验（不算少算）
```

不多算：只碰 M1 / M2 / 六份 Skill 哈希的用例不受影响。

## 二、`reuse_without_rerun` 的一条与证据不符

冻结清单写「十类短入口中**无依赖项**可复用」。逐条查 `apps_actually_run`：

| 用例 | 穿过的应用 |
|---|---|
| DE-01 | MATRIX, SEAM |
| DE-02 | CAMPAIGN, SEAM |
| DE-03 | M3 |
| DE-04 | M5_HOP_ADAPTER, SEAM, CONTENT_BRIEF |
| DE-05 | SEAM, CONTENT_BRIEF |
| DE-06 / DE-07 | CREATIVE_SCRIPT, SEAM |
| DE-08 | PRODUCTION_DIRECTOR, SEAM |
| DE-09 / DE-10 | PUBLISHING_PACKAGING, SEAM |

**十条全部穿过本轮被改的应用，"无依赖项"是空集。** 十条一律 `STALE`。
这不是判据错，是冻结时的预期与实际证据不符；如实登记，不改清单。

## 三、十九维重算结果

| 维 | 状态 |
|---|---|
| 自然交互 / 目标 / 平台 / 账号 / 持久化 / 版本 / 发布反馈 / 质量 / 产能 / 外部市场 / CTA / 用户裁量 / 生产 / 权限 / 恢复 / 不退化 / 跨周期 | `CURRENT` |
| 同质化 | `STALE` |
| 演绎/二创 | `STALE` |

**这张表必须配一句限定才算如实**：沿用冻结构建器的语义，一维只要有**一条**
CURRENT 的 PASS 证据就记 `CURRENT`，哪怕同一维下还挂着 STALE 证据。例如：

| 维 | 记 CURRENT 的依据 | 同一维下仍 STALE 的证据 |
|---|---|---|
| 权限 | FULL-01（fp）、RISK-PUBLISH-ID-01（纯 M2） | RISK-PERM-CTA-01 |
| 恢复 | RISK-RECOVERY-01（纯 M2） | DE-10 |
| 不退化 | REG-M1-01 / REG-M2-01 / REG-M4-01 / REG-SKILLS-01 | REG-M3-01；AB 两例未跑 |

逐行 `freshness` 已写进 JSON。**`CURRENT` 在这里的含义是"有代表性的当期证据"，
不是"该维已全覆盖"。**

## 四、一处必须点名的索引缺陷（不修，交规划侧）

冻结映射把「质量」维绑到用例 `RISK-M4-030`，而风险探针实际产出的用例 id 是
**`RISK-M4-030+031`**。两者不相等，映射查不到，该行恒为 `NOT_RUN`。

后果是具体的：**本轮唯一一条 CURRENT 且 FAIL 的用例（`RISK-M4-030+031`），
在「质量」维上完全不可见**；该维靠 FULL-01 单独记成了 `CURRENT`。

这条在 `DIYU_M5_BUILD_EVIDENCE_INDEX_v1.0.py` 里就写着「照抄不改。改这里等于改判据，
属于合同层动作，执行侧无权」。**所以本轮不修**，作为缺陷登记，交规划侧裁定。
`M5-AC-07` 走的是自己的用例清单（含 `RISK-M4-030+031`），因此该 FAIL 在 AC 层没有被漏掉。

## 五、AC 状态

| AC | 状态 | 依据 |
|---|---|---|
| `M5-AC-00` 激活与保护面 | `NOT_RECOMPUTED_HERE` | 静态项，R7 只重算由用例推出的状态 |
| `M5-AC-01` 候选与 Manifest | `NOT_RECOMPUTED_HERE` | 同上 |
| `M5-AC-02` 扩展完整主故事 | `CURRENT` | FULL-01、FULL-02 均本轮 fp 且 PASS |
| `M5-AC-03` 合法短入口 | `STALE` | 十条短入口全部未在本轮重跑，全部 STALE |
| `M5-AC-04` 十九维全覆盖 | `STALE` | 两维 STALE |
| `M5-AC-05` M3 A/B | `NOT_VERIFIED` | 只能由独立人类盲评给；映射封存未开 |
| `M5-AC-06` 最终成品 A/B | `NOT_VERIFIED` | 同上 |
| **`M5-AC-07` 留出与高风险探针** | **`FAIL`** | `RISK-M4-030+031` 本轮 CURRENT 且 FAIL；另有三份留出各含未决人判子项 |
| `M5-AC-08` 不退化与受影响回归 | `STALE` | REG-M3-01 未重跑；AB 两例未跑 |
| `M5-AC-09` Founder 产品验收 | `NOT_VERIFIED` | 只能由 Founder 给 |
| `M5-AC-10` Git 与最终回执 | `NOT_RECOMPUTED_HERE` | 收口时填 |

## 六、这张表说明什么，不说明什么

**说明**：本轮三处目标行为的修复，在其直接对应的证据面上成立（R2 三处不复现、
R3 执行侧可判 P0 零命中、R5 正常主路径未被误挡、R6 11/11）。

**不说明**：候选整体可验收。`M5-AC-07` 是 `FAIL`，`AC-03`／`AC-04`／`AC-08` 是 `STALE`，
四项 A/B 与 Founder 验收是 `NOT_VERIFIED`。

`STALE` 的成因是**本轮授权范围**：冻结清单 `allowed_reverification_only` 只允许 R1–R7，
`new_formal_round = NOT_AUTHORIZED`。所以这些维不是"漏跑"，是"按授权没跑"。
要把它们变回 `CURRENT`，需要一次新的正式轮授权——**不属于执行侧可以自行发起的动作**。
