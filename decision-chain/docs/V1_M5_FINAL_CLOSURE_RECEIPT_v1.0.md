# 笛语 V1 · M5 最终收口回执 v1.0

`task_id`: `DIYU-V1-M5-UNIFIED-INTEGRATION-FINAL-ACCEPTANCE-001`

> **本文件当前是空回执模板，`status = NOT_CLOSED`。**
> 每一行都必须由**已发生的事件**填写。任何一行没有对应事件，就留 `PENDING`，
> 不允许用「预计」「应当」「理论上」填。回执不是承诺，是记账。

---

## 一、终态

| 项 | 值 |
|---|---|
| 终态 | **尚未判定**。任务保持 `IN_PROGRESS`。允许终态为 `INVALID` / `DONE` / `BLOCKED` / `FAILED`；**`PARTIAL` 不是 M5 的合法终态** |
| `done_formula` 是否成立 | **否** |
| 不成立的原因 | ① `M5-AC-07` `FAIL`（存在适用 P0 硬门失败）；② `M5-AC-05` / `M5-AC-06` / `M5-AC-09` 三项执行侧无权自裁，需你完成 |
| 候选 | `86af9ecd5a313ff55aff1874d29eb342299d65ff`，清单冻结于 `2026-08-28T09:14:06Z` |

### 为什么不是 `BLOCKED` 也不是 `FAILED`

`BLOCKED` 与 `FAILED` 都是**终态**，一旦写下就意味着本任务在此结束。
现在还不到那一步：两个阻断项都需要你先做处置裁定，A/B 盲评与产品验收也还没做。
在你给出这些之前把终态写死，是执行侧替你做了决定。所以此处留空，任务保持
`IN_PROGRESS`，并把需要你做的事列在第七节。

---

## 二、十一项验收

| 验收项 | 状态 | 证据 |
|---|---|---|
| `M5-AC-00` 激活、实时基线与保护面 | **成立** | 相对 `main` 零修改零删除（`git diff --diff-filter=MD` 为空）；12 份 Skill 运行时自报哈希与候选树**逐字节一致** |
| `M5-AC-01` 集成候选与最终 Manifest | **成立** | 清单 `FROZEN`；正式运行前置现场复算 15 个应用 graph 哈希**逐条一致** |
| `M5-AC-02` 扩展完整主故事 | **PASS** | `FULL_STORY_RUN_full01F1.json`：四能力 4/4 交付、发布双真、反馈幂等、Cycle N+1 绑定 |
| `M5-AC-03` 要求的合法短入口 | **PASS** | `DIRECT_ENTRY_SUITE_deF.json`：**10/10**，不暗跑由台账与接缝自报两条独立证据同时成立 |
| `M5-AC-04` 十九维轻量全覆盖 | **CURRENT** | 19/19 CURRENT；`cta`、`permission` 两维带**已披露**的未判定语义部分 |
| `M5-AC-05` M3 A/B | `NOT_VERIFIED` | 盲评包已出、映射封存**未开**。**执行侧不得自裁** |
| `M5-AC-06` 最终成品 A/B | `NOT_VERIFIED` | 同上 |
| **`M5-AC-07` 留出与高风险探针** | **FAIL** | 阻断项两个：`HOLDOUT-M5-05`（P0）、`RISK-M4-030+031` |
| `M5-AC-08` 不退化与受影响回归 | **PASS** | 5/5：M1 216 tests、M2 92 passed（候选镜像内）、M3 全套、M4 真实 Dify 八闸门、六份 Skill 不强制全调用 |
| `M5-AC-09` Founder 产品验收 | `NOT_VERIFIED` | **只能由 Founder 给**；该接受不替代技术硬门 |
| `M5-AC-10` Git、远端与最终回执 | 未开始 | `main` 合并为条件化授权，前置条件未满足 |

### `M5-AC-07` 的两个阻断项：都不是 M5 引入的

| 阻断项 | 根因所在 | 说明 |
|---|---|---|
| `HOLDOUT-M5-05` | **M3** | 恢复场景下接受了 Founder 对**技术状态**的三次口头改写：全量重跑、「宁可多一次」重复写入、「跑通了就算」。封存判据 §〇.7 明写这类改写不构成事实上行 |
| `RISK-M4-030+031` | **M4** | 外壳解析器对含 ASCII 引号的值判为不在场，等价表达被误判为失败。同一语义只因 `audience_problem` 值里多一个引号就判 `INPUT_INSUFFICIENT` |

两者都在受保护面（M3 应用、M4 八个应用），**本任务无授权改动**，需你裁定是否开后继任务。

---

## 三、Git 与远端

| 项 | 值 |
|---|---|
| 任务分支 | `codex/v1-m5-unified-integration-final-acceptance-001` |
| 分支最终 commit | `PENDING` |
| 分支推送 | `PENDING` |
| `main` 合并 | `PENDING` —— `CONDITIONALLY_AUTHORIZED`，仅在全部技术硬门 `PASS` 且 Founder 产品接受之后 |
| `main` 最终 commit | `PENDING` |
| `origin/main` 远端核验哈希 | `PENDING` |
| `force_push` | `NOT_USED`（`PROHIBITED`） |
| `remote_branch_delete` | `NOT_USED`（`PROHIBITED`） |

---

## 四、外部副作用清单（只追加，不删不改）

> 凡是**离开本仓库**或**改变了共享环境**的动作，一律登记在此。
> 「可逆」也要登记——可逆不等于没发生。

| # | 副作用 | 可逆性 | 状态 |
|---|---|---|---|
| 1 | 新建 Dify M5 测试候选应用（抽取适配 `e1013ce2`、跨能力接缝适配 `6c46fdb1`、模型可用性探针、A/B 基线应用） | 可删除，未覆盖任何既有应用 | 已发生 |
| 2 | 新建 M2 候选镜像 `diyu-m2-app:m5-candidate` 并替换运行容器 | 旧容器保留为 `diyu-m2-app-pre-m5`，未删除，可回退 | 已发生 |
| 3 | 在 `diyu_business` 写入任务域测试数据（工作区、账号、周期、任务、产物、版本、发布、反馈） | 全部显式 `is_test=true` / `is_simulated=true`；未触碰任何非测试数据 | 已发生 |
| 4 | 建立任务专用 worktree 与分支 | 可删除 | 已发生 |
| 5 | 移除一个陈旧的 `.git/config.lock`（0 字节、无持有者、`.git/config` 完好） | 不可逆但无损 | 已发生 |
| 6 | Dify 模型调用消耗账户额度 | 不可逆 | 已发生 |

**未发生**：真实内容平台发布（`real_external_publish` 未授权，全程未连接任何真实内容平台）。

---

## 五、已定位但未修复的缺陷（收口时必须一并交出，不得省略）

| 编号 | 归属 | 状态 | 后继 |
|---|---|---|---|
| `GAP-B` Brief §3.2 仍要求 Campaign 决策包 | 合同层 | 已披露、未消除、**未涂绿** | 待合同层处理，不在本任务内解决 |
| `M4-ENVELOPE-QUOTE-FALSE-NEGATIVE` | M4 | M5 侧绕开，**M4 未修复** | 待 Founder 裁定是否开 M4 后继任务 |
| `D-2` Canvas 业务未交付仍宣称进度 | M4 | 未修复 | 受保护面，需新授权 |
| `M5-HOP-RECALL` 适配器个别字段召回不稳 | M5 自身 | 已补定向重入与两条可审计合成规则 | 仍抽不到时停下交用户，不代答 |

---

## 六、执行侧声明

- 本任务**未**改动 M4 八个已发布应用、M3 已发布应用、六份专业 Skill 源文件。
  相对 `main` 的差异经 `git diff --diff-filter=MD` 复算为**零修改、零删除**。
- 本任务**未**做静默模型替换。DeepSeek 余额耗尽期间按合同判 `BLOCKED` 并上报 Founder，
  由 Founder 充值后经可用性探针实测恢复再继续。
- 本任务**未**由执行侧宣布任何合同「已接受」，**未**自行把状态往上推一级。
- `M5-AC-05` / `M5-AC-06` / `M5-AC-09` 三项执行侧不给结论：
  模型自评无效；实现者知道 A/B 映射的评分无效；Founder 验收只能由 Founder 给。

---

---

## 七、需要你做的三件事

执行侧到此为止。下面三件我做了都不算数，原因写在各自后面。

| # | 事项 | 为什么必须你做 | 材料 |
|---|---|---|---|
| 1 | 两级 A/B 盲评 | 合同明写模型自评无效、实现者知道映射的评分无效。我既是实现者又知道映射 | `V1_M5_HUMAN_BLIND_REVIEW_PACKAGE_v1.0.md`（含两段执行侧判不了的语义问题） |
| 2 | 对 `M5-AC-07` 两个阻断项的处置裁定 | 两者都在受保护面，改动需新授权；是否开后继任务是产品与优先级判断 | `V1_M5_HOLDOUT_VERDICTS_v1.0.md` |
| 3 | Founder 产品验收 | 合同规定只能由 Founder 给 | `V1_M5_FOUNDER_ACCEPTANCE_PACKAGE_v1.0.md` |

**盲评前不要打开** `decision-chain/evidence/m5/AB_MAPPING_SEALED_*.json`——打开即作废本次盲评。

---

`END_OF_RECEIPT`
