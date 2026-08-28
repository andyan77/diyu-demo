# 笛语 V1 · M5 AC-07 Rebase · RB-1 FAILURE TRIAGE v1.0

`task_id`: `DIYU-V1-M5-UNIFIED-INTEGRATION-FINAL-ACCEPTANCE-001`
`entry_mode`: `REBASE_TASK`
Rebase Prompt sha256 `9b988027438f498b25421cecd73cd9d9d302bddcf15876c6b9833eaf624ddecb`
Rebase Contract sha256 `a13b5651c2065eb8ffd70c1cdbf4bf1de09fbc39f7bb5693b31231f2da2ce7dc`

四项归因**都在改正式被测对象之前完成**。三项的最高失效节点与规划侧的预判不同，
两项比规划侧记录的更严重。下面每一条的 `confirmed_origin` 都有独立证据，
不是「测试报错所以被测对象有错」。

---

## F1 · M3 恢复状态权威（`HOLDOUT-M5-05`）

### observed_failure
原始正式留出运行中，系统接受了三次对**技术状态**的口头改写：全量重跑并作废旧草稿；
未查幂等即「宁可多一次」登记反馈；两次报错「跑通了就算」。

### frozen_target
原封存判据三条「必须发生」：只重跑受影响面并列出重跑/保留清单；写入前先查幂等；
保留失败、原因与新 Run ID。判据继续有效，本轮不改判据。

### candidate_sources
`SYSTEM_UNDER_TEST`（M3 行为）｜`INPUT_ENVIRONMENT_OR_TOOL`（M5 给 M3 的输入）｜
`ORACLE_OR_CRITERION`｜`CHECKER_OR_FIXTURE`

### 判别实验（这是本项的关键，不是复述原结论）
同一段留出原文、同一个 M3 已发布应用、同一份参考信封，**只改一个变量**：
`account_context` 里有没有 M2 真实存在的恢复状态。

- `CTRL-A` = M5 现在实际传的 `projection_text()`，**实测 217 字符**，零运行状态
- `CTRL-B` = 同上再加 M2 现场读出的 `run-state`（`last_success_step` /
  `failed_step` / `resumable_from` / `side_effects`）、按幂等键存在的反馈行、两次传输失败明细

两臂各多次取样（A 共 3 次，含原始正式留出那次；B 共 4 次），因为单次结果不足以定归因
——A 臂本身就观察到轮间波动。

| 原判据 | CTRL-A（无运行状态） | CTRL-B（有运行状态） |
|---|---|---|
| ① 拒绝全量重跑、给重跑/保留清单 | **0/3 PASS** | **3/4 实质 PASS**，1 次明确 FAIL |
| ② 先查幂等再写，拒绝「宁可多一次」 | 不稳定：1 次明确违规，2 次诚实说「我看不到」 | **4/4 PASS** |
| ③ 保留失败证据，不「跑通就算」 | **0/3 保留** | **4/4 PASS** |

CTRL-B 原话（②③ 稳定成立）：

> 「系统里已经有登记记录，不用再提交一遍，重复提交反而可能造成重复处理。」
> 「系统里已经登记过了（幂等键存在），不用再提交，重复提交会被拦下来，不会产生两条。」
> 「昨天两次超时错误已经记录在案，不影响本次恢复；如果重试时再出现，回到内容任务这一步继续。」

CTRL-B 第 4 次（① 明确 FAIL，如实记录）：

> 「**按你要求全部重跑，代价是重复了一次周期判断**」「这次是从头重跑。」

它当时拿到的投影明写 `最后成功步骤=M3_CYCLE_JUDGMENT`、`可恢复起点=CONTENT_BRIEF`。
信息在场而未被用上，这一条不能推给输入。

### evidence
- `decision-chain/evidence/m5-rb/F1_TRIAGE_PROBE.json`（两臂全文与 run_id）
- `decision-chain/evidence/m5-rb/F1_REPEAT.json`（5 次重复采样全文与 run_id）
- M3 已发布提示词第 426 行：**「永远不做……处理 M2 的并发、幂等、权限、版本晋升或恢复内部实现」**
- M3 「要恢复的东西」槽位表：**没有任何运行/技术状态槽位**
- M2 实际暴露 `GET /workspaces/{ws}/tasks/{id}/run-state` 与
  `GET /workspaces/{ws}/publish-instances/{id}/feedback`；
  `DIYU_M5_INTEGRATION_RUNTIME_v0.1.py::current_projection` **两个都没调**

### confirmed_origin（分裂，不是单一节点）
1. **判据 ② ③：`INPUT_ENVIRONMENT_OR_TOOL` → M5 调用方漏投影。**
   M3 被要求判断它拿不到的技术事实，而它的契约明确把幂等与恢复内部实现划给 M2。
   补上投影后 4/4 成立。**最高失效节点是 M5 的 M2→M3 投影，不是 M3。**
2. **判据 ①：`SYSTEM_UNDER_TEST` → M3 行为，残余 1/4。**
   投影补齐后仍有一次把用户偏好当技术必要性。这落在合同 `in_scope` 的
   「M3 恢复场景的技术状态权威」内，需要最小版本化 successor。

原验收报告写的「三条共享同一个根因」**不成立**，本轮据实更正。

### mutation_target
- `DIYU_M5_INTEGRATION_RUNTIME_v0.1.py::current_projection` 与
  `DIYU_M5_FULL_STORY_v0.1.py::projection_text`：补 M2 运行状态与幂等身份投影
- M3 **任务命名的版本化 successor 应用**：只加技术状态权威一条，不动其他

### protected_targets
M3 已接受的运营责任、目标忠实、事实边界、模块责任、参考资料闸门；
M2 的幂等与恢复实现（不在 M3 里重建第二套）；原留出与原判据。

### next_reverification
旧 `HOLDOUT-M5-05` 三条按原判据做确定性回归（多次取样，不取单次）；
新 `HOLDOUT-M5-RB-01`；`FULL-01/02`；恢复/幂等探针；M3 受影响回归。

---

## F2 · M4 等价表达解析（`RISK-M4-030+031`）

### observed_failure
同一业务语义，因书写形式不同得到不同的「在场／交付」结论。

### 直接测共享节点（不经模型）
`envelope_check` 节点里的 `_find_scalar`，在六个能力应用里是**完全同一份**
（函数体 sha256 全等，六比六）。把已发布代码原样载入离线跑：

| 写法 | 旧版 | 新版 |
|---|---|---|
| JSON 键值都带引号 / YAML 裸值 / 双引号值 / 单引号值 / 反引号键 / 块写法 | 在场 | 在场 |
| **值内部含 ASCII 双引号** | **判为不在场** | 在场 |
| **值内部含 ASCII 单引号** | **判为不在场** | 在场 |
| **JSON 值内含转义引号** | 判为在场，但值被截成 `讲清\` | 完整取到 `讲清"梭织"的差别` |

端到端只改一个引号：`SUFFICIENT` → `INSUFFICIENT`。

**比规划侧记录的多一个缺陷**：转义引号那一支不是漏判，是**静默损坏**——
取到半截值还判成功。漏判会被看见，静默损坏不会。

**还多一个此前没人记过的缺陷**：旧正则 `^\s*key\s*:\s*...` 里的 `\s*` 会跨行。
于是一个**空字段**可以把**下一行**当成自己的值。真实语料里逮到 3 处：
`facts_registered:` 后面什么都没有，旧版取到下一行的 `objective:` 并判为在场。
这个方向是**假 PASS**——必填闸门被静默绕过。

### evidence
- `decision-chain/evidence/m5-rb/F2_PARSER_DIFF.json`（等价矩阵、正负控制、400 条真实语料差分）
- 真实回归语料：从 `workflow_node_executions` 取最近 400 条 `envelope_check` 实际输入

### confirmed_origin
`SYSTEM_UNDER_TEST`；最高失效节点 = 六个能力应用共用的 `_find_scalar`。
不在六个下游 Skill 打补丁，也不在 M5 输出层包装。

### mutation_target
`_find_scalar`（连同 `_unwrap` / `_unescape` 两个新助手），**六处同一改法**，
落在任务命名的版本化 successor 应用里，不覆盖已接受的 M4 应用。

### protected_targets
六份 Skill 源文件与专业语义；M4 八个已发布应用；`_present` 的块写法分支；
`REQUIRED` 清单；空值/缺字段仍须可靠失败。

### next_reverification
等价表达矩阵；正负控制；400 条真实语料新旧差分逐条解释；
旧 `RISK-M4-030+031` 回归；新 `HOLDOUT-M5-RB-02`；六个能力的受影响回归。

---

## F3 · M5→M3 参考信封不一致

### observed_failure
完整主故事经 `m3_loaded_references()` 组了合法 `<<REFERENCE_MANIFEST>>`，
但 `DIYU_M5_DIRECT_ENTRY_SUITE_v1.0.py`（两处）与
`DIYU_M5_RISK_PROBE_SUITE_v1.0.py`（一处）把裸夹具正文直接当 `loaded_references`。

### 判别实验
同一请求、同一 M3 应用，只改参考资料的**形式**：

- `ARM-1` 裸夹具（短入口现状）→ M3 原话：
  > 「本轮输入没有附参考资料清单，所以我不判断专业参考文件是否加载；
  > 这里只依据当前提供的品牌、商品、选品、试穿和承接事实做判断，**不引用行业惯例或季节结论**。」
- `ARM-2` 合法清单 → 正常引用，并正确声明唯一未加载项：
  > 「与验收夹具相关的参考资料这轮没有附上，所以我不引用那部分验收细节。」

裸夹具那一路不报错，只是安静地少掉整个专业方法层（11071 字 → 33522 字之差），
跑出来的证据看着正常但不成立。

### evidence
`decision-chain/evidence/m5-rb/F3_TRIAGE_PROBE.json`（两臂全文、run_id、信封哈希）

### confirmed_origin
`INPUT_ENVIRONMENT_OR_TOOL` → **M5 调用方**。M3 在无清单时拒绝宣称已加载是**正确行为**，
是它的规范要求。**不得为让测试通过而放松 M3 闸门。**

### mutation_target
三处调用点统一走唯一 canonical builder；并在
`DIYU_M5_INTEGRATION_RUNTIME_v0.1.py::m3_operate` 加**结构性拒绝**：
`loaded_references` 非空却没有清单 → 直接抛错。让这类错误从「安静地出假证据」
变成「当场拒绝」。

### protected_targets
M3 的参考资料闸门与全部其他闸门，一个字不动。

### next_reverification
闸门区分度自测（已过：裸夹具被拦、合法清单放行、显式空放行）；
`FULL-01`、依赖 M3 的全部短入口、F-10 风险路径各至少一条真实引用证据。

---

## F4 · M5 正式证据误绑定

### observed_failure
规划侧记的是「盲评包用 `glob + sorted[-1]` 选到了 `AB_BLIND_aba.json`」。
实际是**系统性反选**，不是选错一个文件。

正式产物统一带大写 `F` 标签，ASCII 排序里大写排在小写前面，于是
`sorted(glob(...))[-1]` **永远选不到正式文件**：

| 模式 | `[-1]` 实际选到 | 本次正式产物 |
|---|---|---|
| `AB_BLIND_*` | `aba` | `abF` |
| `DIRECT_ENTRY_SUITE_*` | `deb` | `deF` |
| `RISK_PROBE_SUITE_*` | `riskd` | `riskF` |
| `FULL_STORY_RUN_*` | `full01i` | `full01F1` |

后果：`V1_M5_FORMAL_ACCEPTANCE_EVIDENCE_INDEX_v1.0.yaml` 里出现的证据文件是
`dea`×20、`full01i`×18、`m2pb`×9、`riskd`×4、`riska`×4、`deb`×3 —— **没有一个是正式文件**，
且顶部仍写 `candidate_frozen: false`。

**因此 `M5-AC-04`「19/19 CURRENT」不成立**：它是从冻结前诊断跑算出来的。
`AC-02/03/08` 的数字取自 `FORMAL_RUN_LOG.json` 里正式运行的原始输出，那部分绑定成立。

另外两处同族缺陷：
- `DIYU_M5_BUILD_FOUNDER_PACKAGE_v1.0.py::best_full_story()` 在**所有历史**运行里
  「挑交付能力最多的一次」——那是**择优保留**，用挑样本代替证据；
- `DIYU_M5_REGRESSION_SUITE_v1.0.py` 输出 `REGRESSION_RESULTS.json` **不带标签且合并历史**：
  跑一次子集，旧条目原样留在结果里，看起来像本轮全跑过。

### evidence
`decision-chain/evidence/m5-rb/F4_BINDING_DIAGNOSIS.json`

### confirmed_origin
`CHECKER_OR_FIXTURE` → M5 的证据构建器与索引，不是产品结果本身。
产品结果没被重新解释，只是被指向了错的文件。

### mutation_target
新增 `DIYU_M5_EVIDENCE_BINDING_v1.1.py`（显式路径 + sha256，取不到即非零退出）；
三个构建器改为清单驱动，`glob` 选择全部删除；回归套件改显式输入 + 带标签输出；
正式运行器声明每步产出并生成 Formal Evidence Manifest；
索引出 `v1.1` 后继文件，**保留 v1.0 不删**。

### protected_targets
全部历史证据、失败记录、诊断件与执行侧自我纠错记录；v1.0 索引与回执原文。

---

## 本轮不改的东西（写出来是为了可反查）

- 不改 M3 的目标、事实、权限、模块责任与参考闸门
- 不改六份 Skill 源文件与专业语义
- 不覆盖 M4 八个已发布应用与 M3 已发布应用
- 不改任何封存判据；不因为结果不好看而调判据
- 不删、不覆盖 v1.0 的任何证据、索引、回执与失败记录
