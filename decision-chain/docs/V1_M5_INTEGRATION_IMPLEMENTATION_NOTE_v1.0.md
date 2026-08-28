# 笛语 V1 · M5 统一集成实现说明 v1.0

`task_id`: `DIYU-V1-M5-UNIFIED-INTEGRATION-FINAL-ACCEPTANCE-001`
状态：`IN_PROGRESS`（本文件记录已完成的实现与已定位的问题，不宣布任何验收结论）

---

## 一、M5 到底补了什么

一句话：**M1–M4 四个模块各自 DONE，把它们摆在一起系统仍然不工作，因为没有人负责接缝。**

M5 不是第五个模块，也不是第二套工作流引擎。它只做一件事：把四段各自成立的能力，
接成一条 Founder 能用自然语言从头走到尾的路，并在走的过程中把断掉的地方一处处指出来。

本任务**没有**新建能力、没有改任何一个已发布应用、没有改六份专业 Skill 源文件。
相对 `main` 的差异是 458 个新增文件、**零修改、零删除**（`git diff --diff-filter=MD` 为空）。

---

## 二、四条接缝，以及每一条上真实发生了什么

### 接缝 1：M2 → M3（账号最小当前投影）

M1 的上下文编译器早就留了 `account_anchor_supplied` 这个消费入口，并在注释里写明
「留给未来『持续运营且 M2 有当前合法锚点』这条路径」——当时 M2 还不存在，Dify 图里
没有任何节点会传它。M5 就是它等的那个调用方：账号锚点由 M2 的实时投影提供，
不靠本轮自然语言重新提取，也不靠运行脚本手抄。

**结果**：接上了，投影读取 HTTP 200，`account_context` 由 M2 实时生成。

### 接缝 2：M3 的参考加载（本任务最高价值发现）

见 `M5_NODE3_DIAGNOSTIC_FINDINGS_v1.0.md` 的 **M5-DIAG-009**。

M3 的确定性闸门要求 `loaded_references` 带 `<<REFERENCE_MANIFEST>>` 标记与
`path.md: LOADED` 条目；没有清单时它按自己的规范写「本轮输入没有附参考资料清单，
所以我不判断参考文件是否加载」并**拒绝引用任何参考内容**。

裸拼接夹具正文送进去，M3 收到了 11071 字却一条商品事实都不敢用，
并明写「事实确认人：本轮没有确认人」。下游四个能力随即全部 `INPUT_INSUFFICIENT`。

**M3 没有做错任何事。** 错的是调用方。而这条接缝之所以四个模块的验收都没覆盖到，
是因为 M4 的正式运行**直接向 Capability Seam 注入扁平夹具、根本不过 M3**，
M3 的正式运行又是单独跑的、用它自己的参考清单。
`M3 → 参考加载 → M4` 不在任何单模块的验收面内——不是没测到，是结构上看不见。

**处置**：按 M3 的真实契约组装清单。两个刻意决定记录在案——
`acceptance-fixtures.md` 如实声明 `NOT_LOADED` 且确实不加载（那是 M3 自己的验收夹具，
含期望答案，进正式运行会污染取证）；夹具路径在清单里写作无空格形式，
因为闸门正则 `[\w./-]+\.md` 会被空格打断，这是书写形式规范化，不改变加载与否这一事实。

### 接缝 3：M3 → M4（跨能力外壳适配）

M4 冻结了「六个能力之间零调用边」，并给六个能力**各自不同**的确定性外壳必填清单
（现场从六个已发布 graph 的 `外壳校验` 节点读出，不是推测）：

| 能力 | 必填 |
|---|---|
| MATRIX | applicability_reason / subject_and_account_scope / objective / facts_registered / expression_boundary |
| CAMPAIGN | objective / deadline_or_stage_boundary / audience_problem / facts_registered / capacity_or_owner |
| CONTENT_BRIEF | objective / audience_problem / expected_change / content_promise / facts_registered / expression_subject_and_boundary |
| CREATIVE_SCRIPT | objective / expected_change / content_promise / expression_subject / content_origin_mode / facts_registered |
| PRODUCTION_DIRECTOR | script_or_equivalent_beats / content_origin_mode / production_profile / time_window / content_promise |
| PUBLISHING_PACKAGING | content_body_or_beats / content_promise / explicit_non_promise / facts_registered / cta_contract / asset_publish_permission |

谁把上一跳的产出接成下一跳的外壳，M4 没有规定，**也不该由 M4 规定**——那正是 M5 的活。

**处置**：新建 M5 测试候选应用「跨能力接缝适配器（能力感知抽取）」
`6c46fdb1-5f49-4513-a0c0-29957b3dcee4`。它只抽取与格式化，**不做业务判断，
不调用任何能力应用**。按 `target_capability` 各自的清单，从四类已登记来源抽取：
`[M3]` 运营判断 / `[UP]` 上游能力已交付产出 / `[FACT]` 已登记事实夹具 /
`[ASK]` 用户原话与账号投影。每个字段必须报出来自哪一个来源，不得跨源拼接。

后三个能力要的产能班底、时间窗口、出镜与引用授权，**在 M3 的运营判断里没有也不该有**
——它们是资源事实，不是运营判断，真源是已登记事实夹具。

**唯一一条允许的合成规则**：`expression_subject_and_boundary` 的定义就是
「出镜者＋表达边界」，两个部件都已抽到时拼成复合字段，并在 `source_map` 里标为
`DERIVED(...)`。任一部件缺失一律不合成，照旧计入缺口。

### 接缝 4：M4 → M2（版本、发布身份与反馈写回）

测试发布与反馈按版本幂等写回 M2，再由 M3 复盘进入 Cycle N+1。
`is_test` / `is_simulated` 在数据层为必填布尔且显式传 `True`——
「测试反馈 ≠ 真实平台经营增益」这条非承诺被钉在数据里，不靠文档措辞。

### 适配器不可能调用能力应用——这是结构上成立的，不是承诺

「M5 只做抽取与格式化，不调用任何能力」这句话如果只是我说的，就不值钱。
直接查它**已发布的** graph：

- 节点类型只有 `start` / `llm` / `code` / `end` 四种；
- `tool` / `http-request` / `workflow` / `agent` / `iteration` 节点数 = **0**；
- graph 全文搜索八个 M4 应用 id 与 M3 应用 id，命中数 = **0**。

因此它在结构上就不具备调用任何能力的能力。M4 冻结的「六个能力之间零调用边」
不会被这个适配器破坏——不是因为它守规矩，是因为它做不到。

---

## 三、两处我自己犯的错，都已改正并留痕

### 3.1 把 artifact 当成不能给下一跳用的东西

M4 的语义是「`user_delivery` 是唯一可**直接呈现给用户**的字段」。
我把它错读成「唯一可传给**下一跳**的字段」，于是往下游只传了用户投影。
结果 Production Director 拿不到脚本节拍，报缺 `script_or_equivalent_beats`——
而 Creative Script 返回的 `artifact` 里明明有 5042 字的完整脚本。

**不给用户看**和**不给下一跳用**是两件事。现已改为下传 `artifact`，
用户可见面仍只有 `user_delivery`，并记录能力侧自算的 `artifact_sha256`，不另起一套哈希。

### 3.2 M2 探针写错了表名与字段名

`RISK-PUBLISH-ID-01` 与 `RISK-RECOVERY-01` 首轮 FAIL，是我把表名写成 `feedback`
（实为 `feedback_records`）、把恢复字段写成 `cursor`（实为 `resumable_from`）。
**不是 M2 缺陷。** 修的是观测手段，判据语义一字未改。
按 A2「判据必须早于结果」，改在看到结果之后，故那一轮记为探索，候选冻结后重跑。

---

## 四、四个已定位、尚未修复的缺陷

| 编号 | 性质 | 归属 | 本任务处置 |
|---|---|---|---|
| **GAP-B** | `Content_Brief_Architect` §3.2 仍要求已接受的 Campaign 决策包，而共享合同二已把持续运营决策冻结为第一合法上游 | 合同层 | 已披露、未消除、**未涂绿**。用 `source_kind: M3_OPERATION` 走确定性外壳校验，**没有**把 `upstream_kind` 改标成 `campaign`（一条负向测试明写那样改会让五条全绿） |
| **M4-ENVELOPE-QUOTE-FALSE-NEGATIVE** | 六个能力共用的 `_find_scalar`，YAML 分支捕获组排除 ASCII 引号；值里引用一句话该字段就隐形，硬门给出**假阴性** | M4 | M5 侧改用 M4 自己就接受的第三种形状 `` `key`: value `` 绕开，值一字不改。**M4 未修复**，任何未来用 YAML 平铺写法的调用方都会再次踩中 |
| **D-2** | Founder Canvas 在 `business_delivery_outcome = UNKNOWN` 且 `artifact` 为空时，仍对用户宣称进度（「内容 Brief 现在开始做」） | M4 | **未修复**。Canvas 属受保护面，任何修复须进 M5 测试候选克隆且需新授权 |
| **M5-HOP-RECALL** | 跨能力适配器对 `expression_subject` 的抽取召回不稳，同一输入连跑 4 次 4/4 抽不到 | M5 自身 | 已确认不是随机波动。根因多在上游（M3 判断里本就没有该声明），补了定向重入；仍抽不到时**停下把问题交给用户，不代答不编造** |

---

## 五、防涂绿：适配器有没有替能力侧放松闸门

这是必须回答的问题，因为一个「让什么都能过」的适配器毫无价值。

**反向控制**：逐项删除必填字段，用能力侧**已发布的原始代码**离线重算
（直接 `exec` 真源，未改一字）——**11/11 全部仍判 `INSUFFICIENT`，
且 `missing` 精确命中被删项**。适配器只是让在场的字段可被看见，没有放松任何判据。

---

## 六、绑定与冻结

全部绑定写入 `V1_M5_CANDIDATE_RUN_MANIFEST_v1.0.yaml`。冻结前的一切运行都是**诊断**，
不产生正式 `PASS`。冻结后改动任一绑定，本次正式运行降级为探索，受影响验收项置 `STALE`。

**执行侧不得自裁的项**：两级 A/B 的盲评结论（模型自评无效，实现者知道映射的评分无效）、
Founder 产品验收、任何合同状态自升。
