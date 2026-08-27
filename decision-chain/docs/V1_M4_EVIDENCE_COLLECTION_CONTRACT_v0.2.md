# V1 M4 取证判据合同 v0.2（增量，冻结）

```yaml
document_id: "V1_M4_EVIDENCE_COLLECTION_CONTRACT"
version: "v0.2"
kind: "DELTA_CONTRACT"              # 只增 AC-31；v0.1 全文与全部历史裁定只读保留
task_id: "V1-M4-CAPABILITY-SEAMS-RUNTIME-INTEGRATION-001"
frozen_before_results: true         # 本合同在 AC-31 任何新运行之前冻结
authority_event: "规划侧 M4_TECHNICAL_ADJUDICATION_RESPONSE_v0.1 · T-03"
base: "V1_M4_EVIDENCE_COLLECTION_CONTRACT_v0.1.md"
base_sha256: "08c9c26fc213f2766bd68b36fa56d28cbc80938417588d5beb12164de0da0b54"
rebase_contract: "V1_M4_REBASE_DELTA_CONTRACT_v0.2.md"
rebase_contract_sha256: "e3f840b73d16129073e0963540e08af441160850f8537159d9adac40e5660ef7"
fixture_pack: "V1_M4_SEAM_FIXTURE_PACK_v0.2.md"
fixture_pack_sha256: "6506c6d650015bd7c1d31f9fc593dd93485bcaa84372c5e4dddb61d2783aa791"

inherits: "v0.1 §1–§10 全文逐字继承，包含 AC-01…30 判据正文、合取纪律与状态词"
changes_to_v0_1: "无。AC-01…30 判据正文一字未改。"
adds: ["AC-31"]
retroactive: false                  # 前瞻新增，不追溯改写任何旧结果
```

> **为什么另建 v0.2 而不改 v0.1**：v0.1 是冻结资产，其 sha256 被裁决答复引用为绑定值。
> 冻结合同承接变化只能另建后继版本（CLAUDE.md §6）。
> 改 v0.1 会同时破坏裁决绑定与 A2 判据先后。

---

## 1. 新增判据

### AC-31 · 产出完整性与显式失败

| 判据 | 取证对象 | Oracle（**通过条件**） | 失败条件 | V |
|---|---|---|---|---|
| AC-31 | 六能力代表性正式运行 + Founder 画布 | ① 每次正式运行的 `artifact` 与**适用的** `user_delivery` 均满足下述冻结的非空/最低完整性结构；② 两块**均不出现**对另一块的回指；③ 不满足时**必须**显式 `PARSE_FAIL` 或组件级 Return，**绝不以成功空串放行**；④ 恢复/重试保留原失败且不重复副作用 | 任一合取项不成立；或出现 `status=succeeded` 同时交付块为空或为回指 | D+S |

**合取纪律**（继承 v0.1）：四项全部核验通过才 `PASS`；任一 `NOT_VERIFIED` 则整条 `NOT_VERIFIED`。

### 1.1 冻结阈值（**结果前定，不因结果调整**）

```text
BACKREF_MARKERS    = 即上方 / 即以上 / 同上 / 上方即 / 见上文 / 内容同上 / 本区块与
MIN_ARTIFACT_CHARS = 400            # 去空白后字符数
CHECK_WINDOW       = 各块前 200 字

legit_block = returns_json 中存在合法组件级 Return
              （同时含非空 highest_damaged_layer 与非空 precise_gap）

违规项：
  ARTIFACT_EMPTY         artifact 去空白为空            且 not legit_block
  ARTIFACT_BELOW_MIN     len(artifact.strip()) < 400    且 not legit_block
  ARTIFACT_BACKREF       artifact 前 200 字命中 BACKREF_MARKERS
  USER_DELIVERY_EMPTY    user_delivery 去空白为空       （legit_block 时同样违规）
  USER_DELIVERY_BACKREF  user_delivery 前 200 字命中 BACKREF_MARKERS
```

### 1.2 适用性

合法组件级阻断（如 `FX-M4-THIN-FIELDS` 正确发 `ESCALATE` Return）时：

- `artifact` 允许为空 —— 阻断时没有专业产出可写；
- `user_delivery` **仍必须非空** —— 用户必须被告知阻断，这是本判据保护的核心；
- 该情形记 `APPLICABLE`，**不是** `NOT_APPLICABLE`。

### 1.3 证据来源限制

**AC-31 的正式证据只能来自本合同冻结之后、在新候选上产生的新运行。**
`0dcd66f` 候选下的 46 次正式运行与 12 份采样**只作缺陷发现与回归输入**，
不得倒填为 AC-31 的 PASS 证据。

---

## 2. 对 v0.1 判据的影响声明

```yaml
ac_01_to_30_text_changed: false
ac_01_to_30_verdicts_rewritten: false
ac_13_scope_expanded: false     # 明确不扩大 AC-13 合取项②的取证范围——
                                # 那是「看到结果后改判据」，A2 禁止。
                                # 产出完整性由新判据 AC-31 承接，不改旧判据。
note: |
  A4 验收充分性反查在 v0.1 集合上已失败（AC-01…30 全过仍可能有 18% 静默空交付），
  处置是**前瞻新增 AC-31**，不是回改旧判据、不是追溯翻绿、也不是让旧结果按原集合上行。
```

## 3. 验收充分性反查（A4，冻结前必做）

```text
问：AC-01…31 全部通过 == WHY 中的核心问题被解决？

WHY 核心问题 = 「用户可能收到空交付而系统报成功」

AC-31 ① 覆盖：交付块非空且达最低完整性
AC-31 ② 覆盖：不以回指冒充完整
AC-31 ③ 覆盖：不满足时必须显式失败，不静默放行  ← 直接对应「系统报成功」
AC-31 ④ 覆盖：恢复/重试不重复副作用

反查结论：成立。AC-31 四项合取覆盖 WHY 的全部构成要件。
```
