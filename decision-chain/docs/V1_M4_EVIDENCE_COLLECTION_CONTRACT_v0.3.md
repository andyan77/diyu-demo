# V1 M4 取证判据合同 v0.3（增量，冻结）

```yaml
document_id: "V1_M4_EVIDENCE_COLLECTION_CONTRACT"
version: "v0.3"
kind: "DELTA_CONTRACT"
supersedes: "V1_M4_EVIDENCE_COLLECTION_CONTRACT_v0.2.md"
supersedes_sha256: "544bf1dfa19229161115174a59af81b976baf2ec385554d8c043279d3d34fcbe"
amendment_scope: "只改 §1.1 的 BACKREF_MARKERS 取值表；AC-31 判据正文、四项合取、
                  §1.2 适用性、§1.3 证据来源限制、§2、§3 逐字继承"
base_v0_1: "V1_M4_EVIDENCE_COLLECTION_CONTRACT_v0.1.md"
base_v0_1_sha256: "08c9c26fc213f2766bd68b36fa56d28cbc80938417588d5beb12164de0da0b54"
task_id: "V1-M4-CAPABILITY-SEAMS-RUNTIME-INTEGRATION-001"
frozen_before_results: true
ac31_runs_so_far: 0            # 修订时 AC-31 零运行，A2 判据先后未被破坏
retroactive: false
```

## 1. 为什么修订

`BACKREF_MARKERS` 在 v0.2 冻结后、**AC-31 任何运行之前**，用旧运行作**回归输入**
（v0.2 §1.3 明确允许：「旧运行只作缺陷发现与回归输入」）对量尺做了一次离线回归：

```text
捕获 9/10 已知塌陷 ｜ 误报 0 ｜ 正常放行 47 ｜ 合法阻断 FA-45 正确放行
漏报 1：FA-03，回指写法为「与上方交付实体一致」
```

v0.2 的表里有 `本区块与`，但没有 `与上方`，因此漏掉这一种写法。

**这不是「看到结果后改判据」**：

- AC-31 到此为止**零次运行**，无任何 AC-31 结果存在；
- FA-03 产自 `0dcd66f` 候选，按 v0.2 §1.3 是**回归输入**，不是 AC-31 证据；
- 改的是**量尺**（marker 取值表），**判据正文与四项合取一字未改**；
- 按 v0.2「冻结后不原地改」的规则版本化，不覆盖原文。

登记为**第 7 次量尺更正**（前 6 次见任务账本 `instrument_corrections`）。

## 2. §1.1 修订版（取代 v0.2 §1.1 的 BACKREF_MARKERS 一行）

```text
BACKREF_MARKERS = 即上方 / 即以上 / 同上 / 同上文 / 上方即 / 上文即
                  / 见上文 / 如上所述 / 内容同上 / 本区块与
                  / 与上方 / 与上文 / 与以上          ← v0.3 新增六项

MIN_ARTIFACT_CHARS = 400            # 未变
CHECK_WINDOW       = 200            # 未变
legit_block 定义                     # 未变
违规项五种（ARTIFACT_EMPTY / ARTIFACT_BELOW_MIN / ARTIFACT_BACKREF /
           USER_DELIVERY_EMPTY / USER_DELIVERY_BACKREF）  # 未变
```

**新增项的取舍依据**（57 次已有成功运行上实测）：

| 标记 | 命中塌陷 | 命中正常（误报） | 取舍 |
|---|---|---|---|
| `与上方` | 2 | 0 | **收** —— 补上 FA-03 这一类 |
| `与上文` / `与以上` / `上文即` / `如上所述` / `同上文` | 0 | 0 | **收** —— 同类写法的合理覆盖，零误报 |
| `上方交付` | 1 | 0 | **不收** —— 贴合 FA-03 单例措辞，属过拟合 |

**收「零命中」项而不收「命中 1 项」，理由**：判据要拦的是**一类写法**，不是一条具体句子。
按单例措辞造标记是把量尺贴到已知数据上；按同类写法补齐才是量尺该有的样子。

## 3. 修订后回归结果（确定性节点核验，**不构成任何 criterion PASS**）

```text
捕获 10/10 ｜ 漏报 0 ｜ 误报 0 ｜ 正常放行 47 ｜ FA-45 合法阻断正确放行
evidence_grade: DETERMINISTIC_NODE_VERIFIED
note: 本回归在冻结判据的量尺上运行，只证明量尺按定义工作，
      不产生 AC-31 的正式证据。AC-31 正式证据只能来自新候选上的新运行（v0.2 §1.3）。
```

## 4. 未变更条款

v0.2 的 §1 AC-31 判据正文与四项合取、§1.2 适用性、§1.3 证据来源限制、
§2 对 v0.1 判据的影响声明、§3 验收充分性反查 —— **全部逐字继承，不改。**
