# 笛语 V1 · M5 最终收口回执 v1.0

`task_id`: `DIYU-V1-M5-UNIFIED-INTEGRATION-FINAL-ACCEPTANCE-001`

> **本文件当前是空回执模板，`status = NOT_CLOSED`。**
> 每一行都必须由**已发生的事件**填写。任何一行没有对应事件，就留 `PENDING`，
> 不允许用「预计」「应当」「理论上」填。回执不是承诺，是记账。

---

## 一、终态

| 项 | 值 |
|---|---|
| 终态 | `PENDING`（允许值：`INVALID` / `DONE` / `BLOCKED` / `FAILED`；**`PARTIAL` 不是 M5 的合法终态**） |
| 判定依据 | `done_formula` = `M5-AC-00..10` 全部 `PASS`/`CURRENT` **AND** Founder 产品验收接受 **AND** 无适用 P0 硬门失败 **AND** Git/远端收口完成 |
| 判定时间（UTC） | `PENDING` |

---

## 二、十一项验收

| 验收项 | 状态 | 证据 | 备注 |
|---|---|---|---|
| `M5-AC-00` 激活、实时基线与保护面 | `PENDING` | | |
| `M5-AC-01` 集成候选与最终 Manifest | `PENDING` | | |
| `M5-AC-02` 扩展完整主故事 | `PENDING` | | |
| `M5-AC-03` 要求的合法短入口 | `PENDING` | | |
| `M5-AC-04` 十九维轻量全覆盖 | `PENDING` | | |
| `M5-AC-05` M3 A/B | `PENDING` | | **执行侧不得自裁**：需独立人类盲评 |
| `M5-AC-06` 最终成品 A/B | `PENDING` | | **执行侧不得自裁**：需独立人类盲评 |
| `M5-AC-07` 留出与高风险探针 | `PENDING` | | |
| `M5-AC-08` 不退化与受影响回归 | `PENDING` | | |
| `M5-AC-09` Founder 产品验收 | `PENDING` | | **只能由 Founder 填**；该接受不替代技术硬门 |
| `M5-AC-10` Git、远端与最终回执 | `PENDING` | | |

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

`END_OF_RECEIPT_TEMPLATE`
