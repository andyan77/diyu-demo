# M5 RB3 收敛回报 v1.0 · CHECKPOINT

- `task_id`: `DIYU-V1-M5-UNIFIED-INTEGRATION-FINAL-ACCEPTANCE-001`
- `entry_mode`: `REBASE_TASK`（原 task_id 下继续，未重开任务）
- 依据：收敛控制补丁 001 第 6 条
- `task_progress`: `IN_PROGRESS`ㅤ`terminal_state`: **unset**ㅤ`main_merge`: `NOT_ALLOWED`ㅤ`new_formal_round`: `NOT_AUTHORIZED`

## 一、绑定身份

| 项 | 值 |
|---|---|
| 冻结清单 | `V1_M5_CANDIDATE_RUN_MANIFEST_v1.1.3_AC07_REBASE.yaml`（`FROZEN`） |
| 候选 commit | `d4b26f29ed3d8bb91235170e3c5810e23d98e3e8` |
| 回报时 HEAD | `d322eede01b303051c5599b1eed10573e43a9c38` |
| 绑定开关 | `M5_BIND=rb`ㅤSEAM `9e1b1fd8`ㅤM3 `ca4c28aa` |
| 运行前复算 | `candidate_runtime_changed=[]`ㅤ`oracle_changed_since_freeze=[]`ㅤ`dify_graph_mismatch=[]`ㅤ`worktree_clean=true`ㅤ`dify_running_now=0` |
| 受保护面 | 9 个已接受应用 `graph_md5` 与 v1.0 逐条一致，零漂移 |
| 判据集合 | 8 份，sha256 写入清单 `oracle_files`；其中回归与盲评包为 v1.1（版本化原因见 §六） |

## 二、每个正式套件的状态

| 套件 | 结果 | 证据（sha256 前 16 位） |
|---|---|---|
| P1 完整主故事 FULL-01／02 | **PASS** | `1306a7eaa73eb199` `FULL_STORY_RUN_full01FRB3.json` |
| P2 合法短入口 DE-01..10 | **9/10**，DE-03 `FAIL`（传输）→ 授权重试 `PASS` | `af990c134f3a5ac1` ／重试 `faeb453ad58a2948` |
| P5a 生成侧风险探针 | 2 `PASS` ＋ 2 `PASS_DECIDABLE_PART_ONLY` ＋ 1 **`FAIL`** | `02e24159a584227c` |
| P5b 持久化侧探针 | **3/3 PASS** | `a73ea11973d35041` |
| P6 不退化与受影响回归 | **4/5**，REG-M4-01 `FAIL`，返回码 1 | `ea3e51863b6f15be` |
| P4 两级 A/B | 盲评包与封存映射产出，**未评分** | 原始 `2a37853c70f8df0b`／盲评 `24ebaee88ba8dbbe`／封存 `546468f932e75c3c` |
| P3 十九维回填 | 18 `CURRENT` ／ 0 未覆盖 ／ 1 `FAIL` | `V1_M5_FORMAL_ACCEPTANCE_EVIDENCE_INDEX_v1.1_AC07_REBASE.yaml` |

## 三、两份新鲜留出的状态

保管哈希三项现场复算一致（正文 ×2 ＋ 封存判据）；**先跑、后读判据**——产出于 commit
`2bcd015` 冻结入账，判据在其后才打开。判定书：`V1_M5_RB_HOLDOUT_VERDICT_v1.0.md`。

| 留出 | 判定 | 命中 |
|---|---|---|
| `HOLDOUT-M5-RB-01` | **`FAIL (P0)`** | §1.2-3 影响面多算 ＋ §0.3 伪造副作用（同一处行为） |
| `HOLDOUT-M5-RB-02` | **`FAIL (P0)`** | §2.4-11／12／13 ＋ §2.7 在场判断失效（变体 N） |

产出 `9ed0c7304d3c6a38` `HOLDOUT_RB_RUNS_formal.json`。

**RB-01 有八项风险面成立**：恢复状态以记录为准、影响面不少算（主动补出用户未点名的
第一条）、第二条未被牵连、先查后写、两类失败分离、拒绝删除失败记录、接受经营裁量、
内部状态词零泄漏；`task_run_states` 三个 task 逐字段未被清空或缩减。
失败集中在一处：把上周**已发布**内容作为素材撤回的自动下游标记失效，并声称已完成，
而查库 `content_versions.invalidated_at` 四条全部为 `NULL`。

**RB-02 的形式不变性成立且重要**：A／B／C 三种写法在六行机器可比项上完全一致——
C 段没给 SKU 编号、价格写成「七百八」、素材写成口语描述，系统仍绑到 XQ-2503、
认到 780 元、绑到第二组三层叠穿。§2.7 中「靠编号识别商品」「靠阿拉伯数字识别价格」
「靠精确子串识别入口」三种 FAIL 模式**均未出现**。
失败在变体 N：真空输入下 `DELIVERED` 而非停在缺口，自行补齐内容方向，
下游 artifact 选定 `XQ-2501/2502/2503`。

`SEMANTIC_HUMAN_ONLY` 七项（`RB-01-S1..S3`、`RB-02-S1..S4`）**全部未判**，交独立人类。

## 四、AC 当前状态

| AC | 状态 | 阻断 |
|---|---|---|
| M5-AC-00 激活与保护面 | `SEE_NOTE` | 保护面零漂移，15 个 graph 哈希逐条一致 |
| M5-AC-01 候选与清单 | `SEE_NOTE` | 清单 `FROZEN` |
| M5-AC-02 扩展完整主故事 | **`PASS`** | — |
| M5-AC-03 合法短入口 | `FAIL` | DE-03（传输；授权重试已 `PASS`，是否消解由裁决方定） |
| M5-AC-04 十九维覆盖 | `FAIL` | `no_degradation` ← REG-M4-01 |
| M5-AC-05 M3 A/B | `NOT_VERIFIED` | `EXECUTION_SIDE_MAY_NOT_DECIDE` |
| M5-AC-06 最终成品 A/B | `NOT_VERIFIED` | `EXECUTION_SIDE_MAY_NOT_DECIDE` |
| M5-AC-07 留出与风险探针 | `FAIL` | RISK-M4-030+031、**RB-01**、**RB-02**、HOLDOUT-M5-05（`STALE`） |
| M5-AC-08 不退化回归 | `FAIL` | REG-M4-01 |
| M5-AC-09 Founder 产品验收 | `NOT_VERIFIED` | 只能由 Founder 给 |
| M5-AC-10 Git 与最终回执 | `SEE_NOTE` | 条件化，未触发 |

`RB-AC-01..08`：本执行侧未收到以该编号命名的独立验收项定义；Rebase 的四项工作按
M5-AC-03／04／07／08 承接。**此处不代填，登记为 `NOT_VERIFIED(ABSENT)`，请裁决方确认
编号映射。**

## 五、全部 `FAIL` 与 `NOT_VERIFIED`

### FAIL

1. **`RISK-M4-030+031`** — `json=DELIVERED_AFTER_RECOVERY` 对 `yaml_plain/markdown_backtick=DELIVERED`。
   引号假阴性（本次 Rebase 的修复目标）**已消失**：`yaml_with_quote` 现等于 `yaml_plain`。
   剩余差异归因证据：同形式重复取样 6 次（yaml_plain 3／json 3）**全部 `DELIVERED`**
   （`d17798b6a5236c8a` `F2_OUTCOME_VARIANCE.json`），且能力侧 `envelope_check` 四种写法
   均为 `SUFFICIENT`／`can_run=true`／`missing=[]`。判据未改，`FAIL` 照记。
2. **`REG-M4-01`** — 见 §六，`confirmed_origin = INPUT_ENVIRONMENT_OR_TOOL`。
3. **`HOLDOUT-M5-RB-01`** `FAIL (P0)` — 见 §三。
4. **`HOLDOUT-M5-RB-02`** `FAIL (P0)` — 见 §三。
5. **`DE-03`** `FAIL`（原始）— `ChunkedEncodingError: Response ended prematurely`，
   `judgment_chars=0`，run `b11a98e1`。按补丁第 1 条行使一次授权传输重试：
   run `52fbfbab`，`gate=CLEAN`，885 字，`PASS`。原失败双份留存，不覆盖。

### NOT_VERIFIED

- `RISK-FACT-01`、`RISK-PERM-CTA-01` 的语义部分 `NOT_VERIFIED(INCONCLUSIVE)`，
  35 个上下文交人类盲评；
- 十九维中 `cta`、`permission` 的语义部分同上；
- `M5-AC-05`／`06`／`09` `NOT_VERIFIED — EXECUTION_SIDE_MAY_NOT_DECIDE`；
- 七项 `SEMANTIC_HUMAN_ONLY` 留出子项；
- **`HOLDOUT-M5-05` 现为 `STALE`**：其 `FAIL_P0` 判定绑定的是被后继取代前的 M3 应用。
  按 A3，绑定变化 ⇒ 依赖它的结论失效。本批次未复验（见 §七）。
- `RB-AC-01..08` 编号映射 `NOT_VERIFIED(ABSENT)`。

## 六、`REG-M4-01` 的 FAILURE TRIAGE

- `observed_failure`：`verdict=FAIL`，`gates=[]`。
- `frozen_target`：M4 非固定入口、局部 Return、PRE/MIXED/FINAL、条件附件、业务结果与平台状态分离。
- `candidate_sources`：`CHECKER_OR_FIXTURE` ／ `INPUT_ENVIRONMENT_OR_TOOL` ／ `SYSTEM_UNDER_TEST`。
- `evidence`：
  1. P6 全阶段五条用例总耗时 **10 秒**；同一批夹具当日 03:09→03:17 真实跑完需 **8 分钟**。
  2. `decision-chain/evidence/m4/rebase_ac31/` 中八个 `RB31-Gxx.json` 的 mtime 仍为
     03:09–03:17，RB3 期间**零写入** ⇒ 一条 M4 调用都没发生。
  3. 五个依赖模块导入全部正常。
  4. `PUB.Console().login()` 在 Dify 空载（`running=0`）时连续三次 **0.0 秒**失败：
     `ConnectionResetError [Errno 104]`。
  5. 宿主 `curl http://127.0.0.1/console/api/setup` → `Connection reset by peer`；
     容器内 `http://nginx/console/api/setup` → **200**，`http://api:5001/...` → **200**。
- `confirmed_origin`：**`INPUT_ENVIRONMENT_OR_TOOL`**。宿主→Dify 的 HTTP 通道不可用；
  Dify 本身健康。M4 回归脚手架是运行序列里**唯一**从宿主直连 Console 的组件；
  M5 运行时走的是 `docker exec docker-api-1` 的 relay 形态，因此不受影响。
- **`SYSTEM_UNDER_TEST` 已排除**：M4 从未被调用，这条 `FAIL` 不构成 M4 退化的任何证据。
- `mutation_target`：**本批次为空**。按补丁第 3、4 条不自动修改、不重跑。
- `protected_targets`：M4 已发布的八个应用、六份专业 Skill、全部判据文件。
- 判据自身的弱点（登记，不改）：`reg_m4` 用 `capture_output=True` 抓取子进程输出后
  **丢弃 stdout、stderr 与返回码**，只留 `gates: []`。因此一次 10 秒的硬崩塌在证据里
  长得像一个业务判定。修它属于改判据，需版本化并重新冻结。
- `next_reverification`：把 M4 回归脚手架的传输改为与 M5 运行时同一条 relay 通道，
  或恢复宿主→Dify 通道；然后按原冻结目标定向复跑 REG-M4-01。**需新授权。**

## 七、哪些结果可进入盲评，哪些不可

**可进入评分：**

补丁第 4 条三条硬门逐条复算，本次全部成立：

```
AB-FINAL-01   A=6008字   B=7371字
  CONTENT_BRIEF        DELIVERED  artifact=6741  gaps=无
  CREATIVE_SCRIPT      DELIVERED  artifact=8387  gaps=无
  PUBLISHING_PACKAGING DELIVERED  artifact=7371  gaps=无
AB-M3-01      A=3620字   B=3543字   gate_status=CLEAN
```

B 组非空 ✓ ／ 必要能力无 `UNKNOWN` ✓ ／ artifact 非空 ✓。
故 `V1_M5_HUMAN_BLIND_REVIEW_PACKAGE_v1.0.md` **可进入两级 A/B 人类盲评**，
封存映射 `546468f932e75c3c` 保持未开。

对照：RB2 同一位置 B 组 0 字、三能力全 `UNKNOWN`，按第 4 条应标
`INVALID_FOR_SCORING`；RB2 全批已按 `EXPLORATORY` 留存，不占正式判据位。

**可交人类判定：** 风险探针语义部分 35 个上下文；留出七项 `SEMANTIC_HUMAN_ONLY`。

**不可进入盲评：** `REG-M4-01`（归因为环境，不是产品行为，评它没有意义）；
`HOLDOUT-M5-05`（`STALE`，需先复验）。

## 八、唯一建议的下一动作

**恢复宿主→Dify 的 HTTP 通道（或把 M4 回归脚手架改走与 M5 运行时同一条 relay），
然后定向复跑 `REG-M4-01` 与 `HOLDOUT-01..06`。**

理由：当前四条技术 `FAIL` 里，`REG-M4-01` 是唯一**归因已确认且与产品行为无关**的一条；
`HOLDOUT-M5-05` 是唯一**状态为 `STALE`、复验代价明确**的一条，且它正是本次 Rebase
第一项工作要修的对象——不复验，Rebase 的 job #1 就没有结论。两者都卡在同一个环境问题上。

其余三条（`RISK-M4-030+031`、`RB-01`、`RB-02`）是真实的产品行为问题，
**不建议在 Founder 裁决前改动**：它们指向的是恢复语义、在场判断与副作用真实性，
属于产品语义范畴，修法需要规划侧与 Founder 先定方向。

本动作**需新授权**：它涉及修改一份判据脚手架的传输方式，按 A2 必须版本化并重新冻结，
按补丁第 3 条不得由执行侧自行发起。

## 九、执行侧不得宣告的事

`terminal_state` 未写。`PARTIAL` 不是本任务的合法终态。`main_merge` 保持 `NOT_ALLOWED`。
未开新一轮正式运行。未为取得 `PASS` 重采样或择优保留。
封存映射未开。七项 `SEMANTIC_HUMAN_ONLY` 未判。
