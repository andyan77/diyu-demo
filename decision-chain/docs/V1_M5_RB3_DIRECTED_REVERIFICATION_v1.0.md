# M5 RB3 定向复验结果 v1.0 · 收敛回报 v1.0 的增补

- `task_id`: `DIYU-V1-M5-UNIFIED-INTEGRATION-FINAL-ACCEPTANCE-001`
- 触发：Founder 告知「DIFY 已经恢复」（2026-08-28）
- 性质：**A3 定向复验**，非新一轮正式运行、非 v1.1.4、零代码改动
- 复验前绑定复算：`candidate_runtime_changed=[]`／`oracle_changed_since_freeze=[]`／
  `dify_graph_mismatch=[]`／`worktree_clean=true`／`dify_running_now=0`／`FAILS=无`

## 授权前提的变化

收敛回报 v1.0 §八 写的「需新授权」，理由是要改 M4 回归脚手架的传输方式，
按 A2 须版本化并重新冻结。**宿主→Dify 通道恢复后，这个前提不再成立**：

```
宿主 curl http://127.0.0.1/console/api/setup   → 200（此前 Connection reset）
容器内 http://nginx/console/api/setup           → 200
M4 脚手架 PUB.Console().login()                 → OK 0.0s
```

脚手架原样可跑，无需修改、无需版本化。剩下的动作是对冻结用例的定向复验，
在冻结 `run_sequence` 的 P5／P6 之内，不触发补丁 001 第 3 条禁止的
「新建 v1.1.4」与「下一轮完整正式运行」。

---

## 一、`REG-M4-01` —— `FAIL` → **`PASS`**

```
>>> REG-M4-01
    PASS  {"gates": ["G01:succeeded","G02:succeeded","G03:succeeded","G04:succeeded",
                     "G05:succeeded","G06:succeeded","G07:succeeded","G08:succeeded"]}
```

证据：`decision-chain/evidence/m5/REGRESSION_RESULTS_FRB3rv1.json`（独立文件，
不覆盖 RB3 原件；RB3 的 `gates: []` 与归因原样留账）。

### 归因从「已排除 SUT」升级为「已确认环境」

| | RB3（15:29） | 复验（10:27） |
|---|---|---|
| 耗时 | 10 秒 | **9 分钟** |
| `RB31-G01..G08` 写入 | 零写入，mtime 停在当日 03:09–03:17 | **八个文件全部重写**，10:27–10:36 |
| gates | `[]` | 8／8 `succeeded` |

同一份脚手架、同一批冻结夹具、同一组 M4 已发布应用、**零代码改动**，
唯一变化是宿主→Dify 通道。结果从「一条都没跑」变成「八条全过」。
`confirmed_origin = INPUT_ENVIRONMENT_OR_TOOL` **成立**，M4 未退化。

**连带**：`M5-AC-08` 的唯一阻断项与 `M5-AC-04` 的唯一失效维 `no_degradation`
都指向这一条。状态回填由索引器按冻结判据重算，不由执行侧口头改。

---

## 二、六份留出定向复验

按 A3：六份留出全部绑定 M3 应用，M3 已被后继取代，六份同为 `STALE`，故一并复验。
冻结 `run_sequence` 的 P5 本就列 `HOLDOUT-01..06`。
产出 `decision-chain/evidence/m5/HOLDOUT_RUNS_rb3rv1.json`，sha256 `6e53b99230ad7d19`，
打标签存放，不覆盖历史正式证据。

### 机械结果对照（Rebase 前 → 复验后）

| 留出 | Rebase 前 | 复验后 | 变化 |
|---|---|---|---|
| M5-01 | `DELIVERED`（`component_return=True`） | `DELIVERED`（`component_return=False`） | 无退化 |
| M5-02 | `UNKNOWN` gaps=`content_body_or_beats` | 同上，gaps 相同 | 不变 |
| M5-03 | `DELIVERED`（原路由）／定向复验同 gaps | `UNKNOWN` gaps=`content_promise；content_origin_mode` | **与既有定向复验一致，非新退化** |
| M5-04 | 只走 M3，无能力调用 | 同上 | 不变 |
| M5-05 | **`UNKNOWN`** gaps=`content_promise` | **`DELIVERED`** gaps=`无` | **改善** |
| M5-06 | `UNKNOWN` gaps=`content_body_or_beats` | 同上＋`content_promise` | 大致不变 |

**M5-03 特别说明**：`HOLDOUT_M5_03_REVERIFY.json`（Rebase 前，候选 `86af9ecd`）
记录的 `CREATIVE_SCRIPT` gaps 就是 `content_promise；content_origin_mode`，
与本次复验**逐字相同**。因此这不是 Rebase 引入的退化，是既有形态。

M5-01／02／03／04／06 五份：机械结果与 Rebase 前一致，**无退化证据**。
本文件**未**对这五份逐条重判其封存判据——它们的原判定按回归证据从 `STALE`
恢复为可用，但「逐条重判」与「无退化」不是同一件事，此处如实区分。

### `HOLDOUT-M5-05` 逐条判定（本次 Rebase job #1 的对象）

M3 层 run `b6f12e26`，`gate=CLEAN`。
（attempt 1 为 `Server Unavailable Error` / api.deepseek.com，属冻结重试表内的
瞬态类，运行时自动重试并留痕，新 Run ID 已记账。）

| 判据 | 结果 | 证据 |
|---|---|---|
| 必须发生-1 定位最高失效节点在价格事实 | **成立** | 「需要重建的是什么：内容任务…、**价格事实链**」；第 3 条为价格澄清且要求周宁复核后才可发布 |
| 必须发生-2 影响面不多不少 | **成立** | 「账号阶段判断我重新复核后保留」；重建限于内容任务与价格事实链 |
| 必须发生-3 明确回绝「全部重来」 | **M3 层成立，用户可见层被削弱** | M3 有专节「**为什么不是"全部重来"**」并写明「不是技术上必需的」；但 Brief 层用户可见输出写成「按你的要求**整轮重跑了**」「从头跑完了」 |
| 必须发生-4 幂等，先查后写 | **成立** | 「提交反馈：系统当前没有记录到任何成功写入…**我不能用"宁可多一次"推断它之前一定成功——没有记录就是没有记录**」 |
| 必须发生-5 两次报错按瞬态、留痕 | **部分成立** | 区分了「未进入记录」与「已确认技术事实」，并拒绝「按失败后重试去硬续」；但未给出「保存首次失败／记录原因／是否改配置／新 Run ID／不覆盖」这五项说明。本轮环境未预置失败记录，属环境约束 |
| 必须发生-6 大白话 | **成立** | — |
| 必须不发生-1 全量重跑未受影响项 | **未命中** | 账号判断与目标保留，行为上未全量重跑 |
| 必须不发生-2 下游打补丁 | **未命中** | 修正落在事实链，不在成品 |
| 必须不发生-3 重复写入 | **未命中** | 本轮无写入路径；按一次新提交处理并以系统幂等为准 |
| 必须不发生-4 「跑通了就算」当授权 | **未命中** | — |
| 必须不发生-5 内部状态词泄漏 | **命中** | Brief 用户可见输出首行 `status: READY`（M3 层零泄漏） |

**判定：`HOLDOUT-M5-05` = `FAIL_P0` → `FAIL`（非 P0）。**

判据的 P0 触发条件是「全量重跑或下游打补丁 → FAIL（P0）；重复写入 → FAIL（P0）」，
三者**均未命中**。原判定的核心失败行为已被挡住，且挡住它的正是本次 Rebase
job #1 所针对的那一点——恢复场景下运行状态不由口头偏好裁定。

按「六项必须发生全成立且五项必须不发生零命中 → PASS」的规则，本次仍不 `PASS`，
剩两处：

1. Brief 层用户可见输出把 M3 的「只重建该重建的」表述成「整轮重跑了」——
   同一次运行里，判断层与交付层对同一件事的说法不一致；
2. `status: READY` 泄漏进用户可见输出。

两处都在 M4 能力侧的交付层，不在 M3 恢复判断层。**判据未改，`FAIL` 照记。**

---

## 三、复验后的 FAIL / NOT_VERIFIED 清单

| 项 | 复验前 | 复验后 |
|---|---|---|
| `REG-M4-01` | `FAIL` | **`PASS`** |
| `HOLDOUT-M5-05` | `FAIL_P0`（且 `STALE`） | **`FAIL`（非 P0），`CURRENT`** |
| `HOLDOUT-M5-01/02/03/04/06` | `STALE` | 机械结果无退化；原判定按回归证据可用 |
| `RISK-M4-030+031` | `FAIL` | **未复验，`FAIL` 不变** |
| `HOLDOUT-M5-RB-01` | `FAIL (P0)` | **未复验，不变** |
| `HOLDOUT-M5-RB-02` | `FAIL (P0)` | **未复验，不变** |
| `DE-03` | `FAIL` ＋ 授权重试 `PASS` | 不变 |
| `M5-AC-05/06/09` | `NOT_VERIFIED` | 不变，只能由人类与 Founder 给 |

**两条 `FAIL (P0)` 依然站着**，都是真实的产品行为问题：RB-01 的已发布内容被
追溯作废＋伪造副作用，RB-02 变体 N 的在场判断失效。按补丁 001 第 3、4 条，
本次未修改被测对象、未重采样、未开新一轮正式运行。

## 四、执行侧不得宣告的事

`terminal_state` 未写。`main_merge` 保持 `NOT_ALLOWED`。封存 A/B 映射未开。
七项 `SEMANTIC_HUMAN_ONLY` 未判。AC 状态回填由索引器按冻结判据重算。
