# 笛语 V1 M4 取证合同 v0.5 · 最终窄收口

> 权威域：验收判据域。本文件在任何本轮 Formal Attempt 之前冻结。
> 冻结后不得原地修改；任何权威改版另建 v0.6，不覆盖本文件。
> 本文件**不修改、不覆盖、不追溯改写** v0.4 及其结果。

```yaml
contract_id: V1-M4-EVIDENCE-COLLECTION-v0.5
task_id: V1-M4-CAPABILITY-SEAMS-RUNTIME-INTEGRATION-001
task_entry_mode: REBASE_TASK
current_task_contract_hash: "8d73b4f157883eb422e6ae17ececcf87a64d98c6a51f35537b8446155fa85070"
previous_task_contract_hash: "a5735c319402056f3c8552da229c816324a8a4ce56f36e0d781924114d68b40a"
supersedes_document: false
predecessor_contract: decision-chain/docs/V1_M4_EVIDENCE_COLLECTION_CONTRACT_v0.4.md
predecessor_contract_sha256: "dd0edb1ed49b65ceecce0bcea53bb4fb68804f9c99f5923b1e736e4aad16942d"
```

## §0 冻结顺序声明

1. 本文件先于本轮任何实施后运行冻结（Prompt v1.5 §7、§10 步骤 3）。
2. §1 的故障注入夹具、注入输入与**运行前预期结果**与本文件同批冻结。
3. §2 的必保内容清单在**看到任何恢复输出之前**冻结（Prompt v1.5 §8 CL31-04 末句）。
4. 判据事件早于结果事件（宪法 A2）。看到结果后改判据 ⇒ 本轮只算探索，不产生正式 PASS。
5. 本合同**不设置任何「取最好一次」的取样条款**。失败即记录失败。

## §1 版本化替换声明（Prompt v1.5 §7 必填）

```yaml
supersedes_for_current_rebase:
  - "M4-RB31-03③ 的跨六能力必要要素判据"
  - "M4-RB31-05④ 的单次 artifact 长度 80% 判据"

historical_results_preserved:
  M4-RB31-03_v0_4: "NOT_VERIFIED"
  M4-RB31-05_v0_4: "FAIL"
  AC31_④: "NOT_VERIFIED"
  historical_AC31_⑤: "NOT_VERIFIED"

reason_for_versioning:
  - "判据适用范围没有冻结完整：v0.4 §3.1③ 只冻结了 CONTENT_BRIEF 一项必要要素清单，却要求判断六项能力。事后补写其余五项等于看到结果后造判据，A2 禁止。"
  - "单次 LLM 长度比较不能区分生成波动与专业能力退化：v0.4 §3 RB31-05④ 以一次非确定性输出的长度比另一次单次输出，量尺本身无判别力。"

old_results_retroactively_rewritten: false
```

**替换的边界**：v0.5 只替换上述两条**量尺**，不替换 v0.4 的其余判据，不替换 v0.4 已记录的任何结果。
v0.4 下的 `M4-RB31-03 = NOT_VERIFIED`、`M4-RB31-05 = FAIL` 永久保留，本文件不使其变绿。

## §2 冻结故障注入夹具

### §2.1 注入源定义

```yaml
injection_object_naming_prefix: "DIYU M4 AC31 FAULT INJECTION EVAL ONLY"
injection_source_node: "final_extract"
injection_rule: >
  隔离 EVAL 对象中，唯一与最终 M4 候选不同的是 final_extract 节点本身（节点 id、
  输出键 output 均不变，因此下游 returns_adapter / projection_gate / recovery_llm /
  delivery_finalize / binding_record / end_ok 的定义与连线逐字节不变）。
equivalence_check:
  method: "对 EVAL 对象与最终候选的恢复子图节点定义做逐字节比对"
  recovery_subgraph_nodes:
    - returns_adapter
    - projection_gate
    - recovery_llm
    - delivery_finalize
    - binding_record
    - end_ok
  required_result: "全部逐字节相同；差异仅允许出现在 final_extract"
```

### §2.2 三个冻结注入指令

注入指令通过 `capability_call` 文本中的哨兵串传递，由 `final_extract` 注入版读取。

```yaml
INJ-01:
  directive: "M4_FAULT_DIRECTIVE=TOOL_FAIL"
  behavior: "final_extract 抛出异常 ⇒ 子应用运行失败 ⇒ 接缝 tool 节点 fail-branch"
  target_criterion: M4-CL31-02
  expected_before_run:
    child_app_run_status: "failed"
    seam_reaches_node: "end_tool_fail"
    seam_user_delivery_nonempty: true
    seam_business_delivery_outcome: "NOT_DELIVERED"
    seam_returns_nonempty: true
    skill_llm_execution_count_in_child: 1
    recovery_llm_execution_count_in_child: 0
    other_capabilities_invoked: 0

INJ-02:
  directive: "M4_FAULT_DIRECTIVE=FROZEN_MARKERLESS"
  behavior: >
    final_extract 丢弃 skill_llm 的实时输出，改为输出 §2.3 的冻结专业产出，
    且**只保留 artifact 块标记，删除 user_delivery 块标记**。
  target_criterion: "M4-CL31-03 + M4-CL31-04"
  expected_before_run:
    returns_adapter_needs_projection: "true"
    recovery_llm_execution_count: 1
    skill_llm_execution_count: 1
    delivery_outcome: "DELIVERED_AFTER_RECOVERY"
    user_delivery_nonempty: true
    whole_artifact_copy: false
    internal_leak_count: 0
    unsupported_fact_count: 0
    must_preserve_all_present: true

INJ-03:
  directive: "M4_FAULT_DIRECTIVE=LIVE_MARKERLESS"
  behavior: "final_extract 保留 skill_llm 实时输出，只删除 user_delivery 块标记"
  target_criterion: "M4-CL31-03 补充证据（不承担 CL31-04 的必保内容判据，因为实时产出无法运行前冻结）"
  expected_before_run:
    returns_adapter_needs_projection: "true"
    recovery_llm_execution_count: 1
    skill_llm_execution_count: 1
    delivery_outcome: "DELIVERED_AFTER_RECOVERY"
    user_delivery_nonempty: true
    whole_artifact_copy: false
    internal_leak_count: 0
```

### §2.3 冻结专业产出（INJ-02 的注入 artifact 正文）

事实来源仅限已冻结夹具 `FX-M4-GOAL-COUNTERFACTUAL-A`（`CT_M3`）。不引入夹具之外的商品、价格、面料、顾客或经营事实。

```text
# 内容任务判断｜序里集 · 初秋通勤衣橱第一阶段

## 一、这条要解决的判断

这次的卡点不是衣服数量不够，而是层数与场合没有分开。目标顾客已经有几件通勤外套，
早上仍然要花十几分钟才决定穿什么——她缺的是一套可以自己复用的分层判断，不是再多一件。

## 二、面向谁

已经有几件通勤外套、每天早上仍在衣橱前反复取舍的通勤顾客。

## 三、这条内容对她的承诺

给出一个可以在她自己衣橱里直接照做的分层判断。看完之后，她能说出自己卡住的
不是衣服不够，而是层数与场合没分开。

## 四、可用的事实

苏禾三组试穿记录；三处偏挤；去掉马甲正式感掉一档。除此之外没有登记的事实，不补。

## 五、边界与不能说的

- 不得制造身材或年龄焦虑。
- 讲述人是苏禾，允许显式标注的演示场景，不允许冒充真实顾客。
- 平台尚未锁定，本次只产出平台中立母版，锁定平台之后再做适配。
- 本条不承诺哪一件更好，也不承诺适用于所有身材。

## 六、下一步

把这份判断交给创意脚本环节，按苏禾三组试穿排出节拍，每一节拍逐条对齐事实与素材。
```

### §2.4 冻结必保内容清单（CL31-04 判据，运行前冻结）

每项给出**关键词候选集**；恢复正文中出现该项任一候选（子串匹配）即判该项在场。

```yaml
CORE:                                   # 核心结论，必须全部在场
  CORE-1: ["不是衣服不够", "不是衣服数量不够", "层数与场合没有分开", "层数与场合没分开"]
  CORE-2: ["已经有几件通勤外套", "通勤外套"]
  CORE-3: ["分层判断"]
COND:                                   # 条件与限制，必须全部在场
  COND-1: ["平台", "母版"]
  COND-2: ["焦虑"]
NEXT:                                   # 用户下一步，必须全部在场
  NEXT-1: ["脚本", "节拍", "下一步"]

pass_rule: "CORE 3/3 且 COND 2/2 且 NEXT 1/1 全部在场 ⇒ 必保内容 PASS；任一缺失 ⇒ FAIL"
```

### §2.5 新增事实检测（CL31-04）

对恢复正文中出现的**具体数字、专有名词、商品名、地点、时间**逐项回查 `冻结 artifact ∪ 冻结注入输入`。
出现于恢复正文但两者皆无者计入 `unsupported_fact_count`。

```yaml
extractor_categories: ["具体数字", "专有名词", "商品名", "地点", "时间"]
excluded_categories: ["引号内整句", "泛指名词", "常识词"]
pass_rule: "unsupported_fact_count == 0"
```
> 纪律承接：v0.4 时期的 M4-FND-026（提取器超出冻结判据、把引号内整句也算专有名词）已修正，v0.5 沿用修正后的五类，不再扩张。

### §2.6 内部泄漏词表（CL31-01 / CL31-03 / CL31-04 共用）

```yaml
leak_terms:
  - PARSE_FAIL
  - NOT_APPLICABLE
  - STALE
  - NOT_VERIFIED
  - SEAM_COMPLETENESS_GUARD
  - returns_json
  - artifact_status
  - user_delivery_status
  - user_delivery
  - capability_call
  - professional_payload
  - goal_family
  - skill_llm
  - recovery_llm
  - returns_adapter
  - delivery_finalize
  - final_extract
  - binding_record
  - seam_tool_fail
  - end_tool_fail
  - system prompt
  - trace
  - sha256
  - Judge
  - M4_ARTIFACT
  - M4_USER_DELIVERY
  - M4_RETURNS
pass_rule: "用户可见正文中 leak_terms 命中数 == 0"
```

## §3 本轮验收判据（M4-CL31-01 … 08）

### M4-CL31-01 所有终止分支都有非空用户交付

执行者类型：确定性工具（图枚举 + 代码节点离线执行）。

```yaml
scope: "最终候选的 Capability Seam 全部 end 节点 + 六个能力子应用全部 end 节点"
conjuncts:
  ①: "枚举出的每一个 end 节点的 outputs 中存在变量 user_delivery"
  ②: "每一个 end 节点的 user_delivery 上游产出节点，在其全部返回路径上 trim 后非空"
  ③: "失败类终止分支的 user_delivery 为普通用户可理解的自然语言，命中 §2.6 泄漏词 0 次"
  ④: "失败类终止分支输出 business_delivery_outcome，且取值为 NOT_DELIVERED"
  ⑤: "平台技术状态与业务交付状态在输出中分离表达，不以 succeeded 冒充业务成功"
pass_rule: "①②③④⑤ 全部成立"
method: >
  ② 用离线执行代码节点全部分支的方式取证：对每个产出 user_delivery 的代码节点，
  枚举其所有 return 语句路径并以边界输入驱动，断言返回的 user_delivery 非空。
```

### M4-CL31-02 `end_tool_fail` 真实 Runtime 复验

执行者类型：真实运行取证。

```yaml
input: INJ-01（冻结）
conjuncts:
  ①: "Dify Runtime 中实际到达 end_tool_fail（node execution 可查）"
  ②: "该次运行返回的 user_delivery trim 后非空"
  ③: "business_delivery_outcome == NOT_DELIVERED"
  ④: "组件级 Return 完整：returns_json 可解析且含 §3.1 七项字段"
  ⑤: "没有重跑其他专业能力：本次运行 skill_llm 执行总数 <= 1，且仅出现在被注入的那一个能力子应用中"
  ⑥: "没有重复外部副作用：同一 call 未产生两次子应用运行（重试除外且必须留痕）"
  ⑦: "原始 run_id 与 node execution 可复核"
pass_rule: "①…⑦ 全部成立"
static_only_insufficient: true
```

### M4-CL31-03 恢复路径在 Runtime 中实际触发

执行者类型：真实运行取证。

```yaml
input: "INJ-02（主判据） + INJ-03（补充证据）"
conjuncts:
  ①: "Dify Runtime 实际执行 recovery_llm（node execution 存在且 status=succeeded）"
  ②: "同一运行内 recovery_llm 执行次数 == 1"
  ③: "同一运行内 skill_llm 执行次数 == 1（未因恢复而重复执行）"
  ④: "用户正文 trim 后非空"
  ⑤: "§2.6 泄漏词命中数 == 0"
  ⑥: "非整份 Artifact 复制：最长公共子串 < artifact 长度的 60% 且 user_delivery 长度 < artifact 长度的 80%"
  ⑦: "unsupported_fact_count == 0（判据见 §2.5）"
  ⑧: "§2.4 必保内容全部在场"
  ⑨: "原格式失败、原始产出与恢复动作全部留痕（returns_json 含 RECOVERED_ONCE，binding_record 保留 raw）"
  ⑩: "最终业务状态 == DELIVERED_AFTER_RECOVERY"
pass_rule: "①…⑩ 全部成立（⑦⑧ 只对 INJ-02 判定；INJ-03 判 ①②③④⑤⑥⑨⑩）"
offline_substitute_forbidden: true
recovery_failure_branch:
  note: "若恢复输出为空/泄漏/无法安全投影，则改判以下三项"
  conjuncts:
    F①: "用户得到非空自然语言失败说明"
    F②: "business_delivery_outcome == NOT_DELIVERED"
    F③: "不启动第二次恢复且不重跑专业生产"
```

### M4-CL31-04 恢复语义保真

```yaml
input: INJ-02（冻结 artifact，必保清单运行前冻结）
conjuncts:
  ①: "§2.4 CORE 3/3 在场"
  ②: "§2.4 COND 2/2 在场"
  ③: "§2.4 NEXT 1/1 在场"
  ④: "unsupported_fact_count == 0"
  ⑤: "§2.6 泄漏词命中数 == 0"
scope_limit: >
  本项只验证本次新增或变化的「恢复投影」。
  **不**对其他五个能力施加事后补写的 Content Brief 要素清单（这正是 v0.4 §3.1③ 被替换的原因）。
pass_rule: "①…⑤ 全部成立"
```

### M4-CL31-05 六 Skill 专业非退化后继判据

**本判据不使用任何单次输出长度比例。**

```yaml
conjuncts:
  ①: "六份源 Skill SHA-256 与冻结基线零差异"
  ②: "六份注入 Workflow 的专业正文修复前后逐字节零差异"
  ③: "六个 skill_llm 的 model/provider/completion_params 逐字段零差异"
  ④: "Git 影响面证明本轮代码变化位于专业生成之后，或只属于接缝失败终止路径"
  ⑤: "正常路径每次最多调用一个适用专业能力，不形成六 Skill 固定全链"
  ⑥: "同一次能力运行中 skill_llm 不因恢复而重复执行"
  ⑦: "原始专业输出完整保留（raw_preserved 非空）"
  ⑧: "六项能力各复用至少一条仍为 CURRENT 且绑定未受影响的代表性证据"
  ⑨: "若某项代表性证据绑定确实受本轮变化影响，只定向复验该项"
  ⑩: "Reviewer 未发现可回指到 Skill / 专业 Prompt / 模型参数 / 专业节点的能力削弱证据"
pass_rule: "①…⑩ 全部成立"
length_is_not_evidence: >
  输出更短或更长本身不构成 FAIL。主张专业退化必须同时提交：
  同输入 + 同模型参数 + 可比专业产出 + 冻结专业语义 Oracle + 明确缺失或错误的专业能力。
  缺任一项只能 NOT_VERIFIED，不得报能力退化。
```

### M4-CL31-06 旧技术未知与 Founder 风险接受分层

```yaml
conjuncts:
  ①: "AC-31④ 仍记为 NOT_VERIFIED，未被改写"
  ②: "M4-RB31-03 under v0.4 仍记为 NOT_VERIFIED，未被改写"
  ③: "M4-RB31-05 under v0.4 仍记为 FAIL，未被改写"
  ④: "AC-31④ 的 founder_disposition 记为 FOUNDER_ONE_TIME_DEGRADED_ACCEPTANCE，与技术结果分层存放"
  ⑤: "historical_AC31_⑤ 仍记为 NOT_VERIFIED；本轮后继证据记为 M4-CL31-01 + M4-CL31-02，不篡改旧项"
  ⑥: "M4_POST_REVIEW_VERDICTS.json 等旧证据文件 SHA-256 零变化"
pass_rule: "①…⑥ 全部成立"
```

### M4-CL31-07 保护资产与受影响回归

```yaml
conjuncts:
  ①: "六源 Skill 零变化"
  ②: "六专业 Prompt 零变化"
  ③: "模型参数零变化"
  ④: "九保护应用零变化（app + workflow graph sha256）"
  ⑤: "M1/M2/M3/M5 零越界变化"
  ⑥: "正常 Content Brief 路径可运行且交付非空"
  ⑦: "合法资料不足 Return 路径可运行且交付非空"
  ⑧: "恢复路径可运行（由 CL31-03 承担）"
  ⑨: "tool failure 路径可运行（由 CL31-02 承担）"
  ⑩: "Founder Canvas 用户可见结果没有因接缝修复退化"
  ⑪: "没有固定全链；没有第二套路由或生产链；没有生产环境变化"
pass_rule: "①…⑪ 全部成立"
affected_scope_only: true
```

### M4-CL31-08 Dify 与 Git 远程收口

```yaml
conjuncts:
  ①: "最终正式 M4 TEST 对象已发布"
  ②: "从目标系统读回的 graph / workflow / provider 与冻结候选一致"
  ③: "故障注入对象已删除，或取消发布并断开路由并标记 EVALUATION_ONLY_NOT_ROUTABLE"
  ④: "本地工作区干净"
  ⑤: "本地任务分支与远端任务分支 Commit Hash 相等"
  ⑥: "origin/main 未改变，仍为执行开始时现场观察值"
  ⑦: "无 PR"
  ⑧: "无生产发布"
  ⑨: "所有 Attempt、失败与临时外部副作用均已记录"
pass_rule: "①…⑨ 全部成立"
```

### §3.1 组件级 Return 七项字段

```yaml
required_fields: [return_id, source, highest_damaged_layer, precise_gap,
                  affected_objects, proposed_disposition, needs_user_decision]
```

## §4 强制负向测试（Prompt v1.5 §9）——运行前预期

| 编号 | 场景 | 运行前预期结果 |
|---|---|---|
| NEG-C01 | tool 节点直接失败 | 进 fail-branch，`user_delivery` 非空，`NOT_DELIVERED` |
| NEG-C02 | `end_tool_fail` 终止 | end 节点 outputs 含 `user_delivery` 且非空 |
| NEG-C03 | 专业内容存在但用户 marker 缺失 | `needs_projection=true`，走 `recovery_llm` |
| NEG-C04 | 恢复成功 | `DELIVERED_AFTER_RECOVERY`，正文非空 |
| NEG-C05 | 恢复输出为空 | `NOT_DELIVERED`，仍给非空失败说明，`recovery_used=attempted` |
| NEG-C06 | 恢复输出含内部技术词 | 判为不可用 ⇒ `NOT_DELIVERED` + 非空失败说明 |
| NEG-C07 | 恢复输出整份复制 Artifact | CL31-03⑥ 判 FAIL（不得判 PASS） |
| NEG-C08 | 恢复输出新增冻结输入与 Artifact 中不存在的事实 | `unsupported_fact_count > 0` ⇒ CL31-04④ FAIL |
| NEG-C09 | 同一运行试图执行第二次恢复 | 图上不存在第二次恢复边；执行计数恒 <= 1 |
| NEG-C10 | 恢复后试图重复执行 `skill_llm` | 图上 `skill_llm` 无回边；执行计数恒 == 1 |
| NEG-C11 | 合法资料不足 Return | `end_component_return`，`user_delivery` 非空，`is_task_terminal_state=false` |
| NEG-C12 | 正常不需要恢复的交付 | `DELIVERED`，`recovery_used=false`，`recovery_llm` 执行 0 次 |
| NEG-C13 | 不支持的能力 | `end_unsupported`，`user_delivery` 非空，`NOT_DELIVERED` |
| NEG-C14 | Founder Canvas 对失败说明的用户可见呈现 | Canvas 回复非空、无泄漏词、不冒充成功 |

> NEG-C05/06/07/08 为**判定器判别力测试**：以构造输入驱动判定器，验证它在这些情形下确实报 FAIL。
> 若判定器对上述任一情形报 PASS，则该判定器无判别力，对应 CL 项一律 `NOT_VERIFIED`，不得放行。

## §5 失败条件（任一命中 ⇒ 对应判据 FAIL，不得改判）

```yaml
F-01: "任一 end 节点缺少 user_delivery 输出"
F-02: "任一失败终止分支的 user_delivery 可为空"
F-03: "失败终止分支的用户正文命中 §2.6 泄漏词"
F-04: "以平台 succeeded 冒充业务交付成功"
F-05: "recovery_llm 在受控注入下仍未在 Runtime 执行"
F-06: "同一运行 recovery_llm 执行次数 > 1"
F-07: "同一运行 skill_llm 执行次数 > 1"
F-08: "恢复正文整份复制 Artifact（触发 Prompt v1.5 §13 回滚）"
F-09: "恢复正文新增冻结输入与 Artifact 中不存在的事实"
F-10: "必保内容任一项缺失"
F-11: "六 Skill / 专业 Prompt / 模型参数任一非零变化（触发回滚 + FAILED）"
F-12: "九保护应用任一非零变化"
F-13: "正式应用残留故障注入开关或入口"
F-14: "main 被改变，或创建 PR，或发布生产环境"
F-15: "取样重复直到出现满意结果（N-30）"
```

## §6 证据绑定

```yaml
evidence_root: decision-chain/evidence/m4/final_closure/
required_records:
  - ANCHOR_BEFORE.json           # Dify 回滚锚点与保护资产基线
  - CL31_01_BRANCH_ENUM.json     # 终止分支枚举与离线分支执行
  - CL31_02_TOOLFAIL_RUNTIME.json
  - CL31_03_RECOVERY_RUNTIME.json
  - CL31_04_FIDELITY.json
  - CL31_05_SKILL_FIDELITY.json
  - CL31_06_LAYERING.json
  - CL31_07_PROTECTED_AND_REGRESSION.json
  - CL31_08_CLOSURE.json
  - NEG_C01_C14.json
  - INJECTION_OBJECTS.json       # 创建 / 发布 / 运行 / 清理或隔离状态
  - CANDIDATE_FREEZE.json
binding_fields: [run_id, app_id, workflow_id, graph_sha256, input_sha256,
                 model, completion_params, node_executions]
```

## §7 影响面（宪法 A3）

```yaml
changed_bindings:
  - "接缝 seam_tool_fail / end_tool_fail 节点定义"
  - "接缝 unsupported / end_unsupported 节点定义"
  - "接缝 seam_finalize（fin_*）与六个 end_<cap> 节点定义"
  - "生成器 DIYU_M4_DSL_BUILD_v0.1.py 对应段落"
transitive_dependents:
  - "Capability Seam 应用的 graph 与已发布版本"
  - "Founder Canvas 对 tool_seam.user_delivery 的读取（依赖分析：接口未变，透传即可，无需修改）"
  - "AC-31 合取项①③⑤ 的后继证据"
unknown_dependency_items: []
not_invalidated:
  - "六个能力子应用的专业生成链（skill_llm 及其上游）——本轮零改动"
  - "v0.4 下已取得且绑定未受影响的代表性证据"
  - "M1 / M2 / M3 / M5 资产"
rule: "只使直接依赖、传递依赖与影响关系未知项 STALE；有证据不受影响的项继续复用"
```

## §8 本合同不证明什么

```yaml
does_not_prove:
  - "旧 NOT_VERIFIED 项被改成 PASS"
  - "完整纵向切片已验证"
  - "真实经营提升已发生"
  - "M5 已启动或已具备工程实施授权"
  - "六项能力的专业语义在冻结 Oracle 下被逐条验证（本轮不重开 31 项）"
  - "自然发生的空交付缺陷已在生产流量下复现——本轮是受控注入，不是自然采样"
```

`END_MARKER: V1-M4-EVIDENCE-COLLECTION-CONTRACT-v0.5-END`
