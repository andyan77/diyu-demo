# 笛语 V1 · M4 取证判据合同 v0.4

> **本版性质**：本轮 AC-31 用户可见交付非空修复 REBASE 的**新版本取证合同**。
> **不修改 v0.2 / v0.3**——两者继续作为前序冻结事实存在。
> 本版只新增 `M4-RB31-01…08` 的取证判据；v0.2/v0.3 中未被本版影响的 Oracle 继续有效。

```yaml
contract_id: "V1-M4-EVIDENCE-COLLECTION-CONTRACT"
version: "v0.4"
status: "FROZEN"
task_id: "V1-M4-CAPABILITY-SEAMS-RUNTIME-INTEGRATION-001"
task_entry_mode: "REBASE_TASK"
supersedes_scope: "仅新增 M4-RB31-01…08；不覆盖 v0.2/v0.3 既有条款"
previous_task_contract_hash: "b3ceabcbe9bcd82dae2fae84161dce0f0aadd96e395a8d6fa06a3355138331c6"
current_task_contract_hash: "a5735c319402056f3c8552da229c816324a8a4ce56f36e0d781924114d68b40a"
current_task_contract_hash_rule: >
  载体 = M4_ENGINEERING_EXECUTION_PROMPT_v1.4 第 3 节起至第 11 节前一行止的全部文本行，
  逐行去行尾空白、丢弃纯空行、以 \n 连接并以单个 \n 收尾，UTF-8 编码后取 SHA-256。
  规范化后 355 行 / 17108 字节。
frozen_before_any_new_formal_attempt: true
```

---

## 0. 冻结顺序声明（A2 先后律）

本合同**在任何 `M4-RB31-*` 新 Formal Attempt 运行之前**冻结。冻结时刻的现场事实：

```yaml
frozen_at_branch_head: "60eccfdf937dd8ab45a1774a001e45149eb5efcb"
frozen_at_remote_task_branch: "60eccfdf937dd8ab45a1774a001e45149eb5efcb"
frozen_at_remote_main: "a7b810109f43a4bf500acc285baab477d96796e3"
six_source_skill_fingerprint_recheck: "6/6 与 v1.4 编译观察值一致，零差异"
```

看到结果之后再改本合同判据，本轮运行即降级为探索，不产生正式 PASS。

---

## 1. 输入

### 1.1 三次精确重放输入（M4-RB31-01）

不改写、不补充、不挑选。输入正文来自既有冻结夹具常量，**以 `input_sha256` 相等作为「同一输入」的机械证明**；不相等即视为重放无效。

| 新 Attempt | 重放对象 | 冻结夹具 | 能力 | 输入正文来源 | 冻结 `input_sha256` |
|---|---|---|---|---|---|
| `RB31-R10` | `FA-10` | `FX-M4-GOAL-COUNTERFACTUAL-A` | `CONTENT_BRIEF` | `DIYU_M4_DETERMINISTIC_PROBE_v0.1.GOAL_A` | `9f313e92e8bebe25d579365921b0187ef700ada71a254bda56ce25cdd0fcfbd8` |
| `RB31-R27` | `FA-27` | `FX-M4-CTA-THREE/case_business_handoff` | `CONTENT_BRIEF` | `DIYU_M4_CLOSING_VERIFICATION_v0.1.CTA_BUSINESS_HANDOFF` | `513f1134015b…`（运行时以记录值断言） |
| `RB31-R32` | `FA-32` | `FX-M4-RETURN-PARSE-FAIL` | `CONTENT_BRIEF` | `DIYU_M4_CLOSING_VERIFICATION_v0.1.RETURN_PARSE_FAIL` | `c00c7657396b…`（运行时以记录值断言） |

调用参数与原运行一致：

```text
entry                        = ""（由确定性充分性规则推导）
example_reference_requested  = "NO"
response_mode                = "blocking"
```

### 1.2 输出合同负向测试输入（M4-RB31-02）

十种情况全部以**离线注入**方式对解析与交付收口层取证，不靠碰运气等模型产生特定畸形输出。注入对象为生成器中的 `RETURNS_ADAPTER_CODE` 与 `DELIVERY_FINALIZE_CODE` 两段真实节点代码，**逐字取自当轮已发布 DSL**，不另写一份等价实现。

```text
NEG-01  完整专业内容存在，三类区块 marker 全部缺失
NEG-02  Artifact 存在，用户正文 marker 缺失
NEG-03  用户正文存在，Artifact 缺失
NEG-04  用户正文只有空白字符
NEG-05  用户正文只有回指（见上文／同上／见内部产出）
NEG-06  Returns 块格式损坏
NEG-07  模型输出被整体包裹在代码块中
NEG-08  模型服务瞬时失败后重试成功
NEG-09  有专业内容但无法安全投影（投影结果为空或泄漏内部词）
NEG-10  合法资料不足 Return
```

`NEG-08` 为 Runtime 级取证（读取真实 `node_trace` 的 retry 记录），其余为节点代码级取证。

### 1.3 受影响回归输入（M4-RB31-05）

```text
六项能力各一条代表性直接调用   （复用既有冻结夹具，不新造业务事实）
Founder Canvas 至少一条端到端用户可见运行
PRE / MIXED / FINAL 受影响路径
Return 与局部回退路径
合法等价输入与跳过不适用组件
```

---

## 2. 环境与模型参数（保真绑定，禁止本轮调整）

```yaml
environment: "本机 Docker Dify 1.16.1（http://127.0.0.1）"
model_provider: "langgenius/deepseek/deepseek"
model_name: "deepseek-v4-flash"
model_mode: "chat"
completion_params:
  max_tokens: 384000
  reasoning_effort: "low"
  thinking: true
  top_p: 0.8
```

新增的 `recovery_llm` 节点**必须使用与 `skill_llm` 完全相同的 MODEL 常量**，不得为提高成功率单独调参。生成器自检项 `nodes["recovery_llm"]["data"]["model"] == MODEL` 为硬断言。

v1.4 §8-9「不得修改模型参数来碰运气」与 §7.2「不得通过削弱 Prompt、削减专业产出、降低推理参数来降低空交付概率」在本合同中转化为可机械核验的判据：**本轮 `MODEL` 常量与六份能力 Skill 注入正文的 SHA-256 必须与修复前一致。**

---

## 3. 成功条件（冻结 Oracle）

### M4-RB31-01 三次精确重放

`PASS` 需同时成立（合取，缺一即 FAIL）：

```text
① 三次运行的 input_sha256 == 冻结值
② 三次 user_delivery 去空白后长度 > 0
③ 三次 user_delivery 不落入 {占位符, 纯回指, 内部状态码}
   —— 回指判定沿用 v0.3 的 13 项 BACKREF_MARKERS
   —— 内部状态码判定见 §3 的 LEAK_TERMS
④ 三次 user_delivery 可被普通用户直接阅读
   —— 机械近似：非空自然语言、无 JSON/YAML 整块、无内部字段名
⑤ 三次内部 Artifact 仍被保留（artifact 或 raw 非空）
⑥ 原输入/模型/参数/环境/实际 published workflow 绑定完整落盘
⑦ FA-10 / FA-27 / FA-32 原失败记录文件未被修改（SHA-256 与重放前相等）
⑧ 未重跑不相关上游或整条生产链（node_trace 中不出现额外能力调用）
```

### M4-RB31-02 输出合同负向测试

每种情况必须落入且仅落入以下两类之一：

```text
A. delivery_outcome ∈ {DELIVERED, DELIVERED_AFTER_RECOVERY} 且 user_delivery 非空自然语言
B. delivery_outcome == NOT_DELIVERED 且 user_delivery 非空自然语言且明确说明未成功交付
```

**禁止出现的第三类**：`delivery_outcome` 表示成功而 `user_delivery` 为空串或纯空白。出现即该项 `FAIL`。

### M4-RB31-03 用户可见与内部语义分离

```text
① user_delivery 不含 LEAK_TERMS 任一项
② user_delivery 不是 artifact 的整体复制
   —— 机械判据：user_delivery 与 artifact 的最长公共子串 < artifact 长度的 60%
      且 user_delivery 长度 < artifact 长度的 80%
③ user_delivery 保留必要事实、结论、限制、选择与下一步
   —— 有界语义检查，判据在结果前冻结见 §3.1
④ 投影未新增 artifact 中不存在的业务事实（有界语义检查）
⑤ artifact 与 user_delivery 均不存在对另一块的空洞回指
```

`LEAK_TERMS`（冻结，取自 v1.4 §5.2 列举 + 现有内部状态词）：

```text
PARSE_FAIL / PARSE_FAILED / SEAM_COMPLETENESS_GUARD / STRUCTURE_MISSING
BACKREF_COLLAPSED / BELOW_MIN / NOT_APPLICABLE / NOT_VERIFIED / STALE
artifact_status / user_delivery_status / returns_status / local_block
needs_projection / projection_source / delivery_outcome / recovery_used
seam_trace / call_hash / binding_record / node_trace / workflow_run_id
system prompt / 系统提示词 / Judge / 判定器 / sha256 / commit
---M4_ARTIFACT--- / ---M4_USER--- / ---M4_RETURNS---
```

#### 3.1 有界语义检查的冻结判据

`③④` 由**确定性抽取 + 冻结清单比对**执行，不由自由裁量的「哪份更好」判断执行（`CLAUDE.md` §4）：

```text
③ 必要要素清单（按能力冻结）：
   CONTENT_BRIEF → {内容要做什么, 面向谁, 关键信息或卖点, 边界或不能说的, 下一步}
   判据：五项中至少四项在 user_delivery 中有可定位对应文字。
④ 新增事实检测：
   对 user_delivery 中出现的**具体数字、专有名词、商品名、地点、时间**逐项回查 artifact；
   任一项在 artifact 中无对应即判 FAIL。
```

### M4-RB31-04 恢复、Return 与幂等

```text
① 首次格式失败被保留：返回体或 returns_json 中仍能读到原始格式失败登记
② 最多一次局部恢复：node_trace 中 recovery_llm 至多出现一次
③ 恢复不重新触发上游生产链：node_trace 中 skill_llm 只出现一次
④ transient retry 与用户投影不产生重复外部副作用
⑤ 同一 Attempt 重复提交不生成重复业务动作
⑥ 无法恢复时业务交付状态不是成功（delivery_outcome == NOT_DELIVERED）
⑦ Dify 技术状态（succeeded/partial-succeeded）与 M4 业务交付状态在输出中被分开表达
```

### M4-RB31-05 六 Skill 与业务语义无退化

```text
① 六份源 Skill SHA-256 零差异
② 六份能力 Skill 注入 Workflow 的正文 SHA-256 零差异
③ MODEL 常量零差异
④ 六项能力代表性运行的 artifact 长度不低于修复前同夹具基线的 80%
   —— 「不因修复用户投影而削弱专业产出」的机械化表述
⑤ Founder Canvas 端到端运行用户可见输出非空
⑥ Return 与局部回退路径行为与修复前一致（同输入同判定）
```

### M4-RB31-06 影响面与旧证据复用

```text
① 依赖图显式给出：直接依赖 + 传递依赖 + 无法可靠判断项
② 受影响项标 STALE 并定向复验
③ 有证据证明不受影响的旧结果注明复用理由
④ 至少重新判断 AC-31 / AC-12 / AC-13 / AC-14 / AC-16
⑤ 不得默认全部 31 项推倒重来，也不得遗漏已知影响项
```

### M4-RB31-07 Founder 裁决入账

```text
① 追加记录五个字段，值与 v1.4 §9 逐字相等
② technical_results_rewritten == false
③ AC31_waived == false
④ 历史 PASS=16 / FAIL=1 / NOT_VERIFIED=14 作为前序技术事实保留
⑤ M4_POST_REVIEW_VERDICTS.json 的 SHA-256 与 v1.4 §2 记录值相等（未被修改）
```

### M4-RB31-08 保护资产、Dify 与 Git 收口

```text
① 六份源 Skill 零改动
② 九个保护应用零变化（published workflow id / graph hash 相等）
③ M1/M2/M3/M5 资产零越界变化
④ 当前 M4 Dify 对象实际发布版本与 provider 绑定可读回
⑤ 新 Formal Attempt 绑定最终冻结候选
⑥ 分支工作区干净
⑦ 本地任务分支 == 远端任务分支 Commit Hash
⑧ main 未改变
⑨ 无 PR
⑩ 无生产发布
```

---

## 4. 失败条件

出现以下任一，对应验收项即 `FAIL`，不得以「多跑几次」「换个夹具」规避：

```text
F-01  任一重放仍出现 user_delivery 为空          → M4-RB31-01 FAIL
F-02  任一负向情况产生「成功 + 空串」            → M4-RB31-02 FAIL
F-03  user_delivery 通过复制全部 Artifact 变非空  → M4-RB31-03 FAIL 且触发 v1.4 §11 回滚
F-04  recovery_llm 在一次运行中出现两次及以上    → M4-RB31-04 FAIL
F-05  skill_llm 在一次运行中被重复触发           → M4-RB31-04 FAIL 且构成第二条生产链
F-06  六份源 Skill 或注入正文或 MODEL 出现差异    → M4-RB31-05 FAIL 且触发回滚
F-07  代表性运行 artifact 长度低于基线 80%       → M4-RB31-05 FAIL（专业产出被削弱）
F-08  已知受影响 criterion 未复验                → M4-RB31-06 FAIL
F-09  技术 NOT_VERIFIED 被改写为 PASS            → M4-RB31-07 FAIL
F-10  保护资产任一项发生变化                     → M4-RB31-08 FAIL 且触发回滚
```

**N-30 继续有效**：失败后盲目重抽、只留满意输出，禁止。本合同不设置任何「取最好一次」的取样条款。

---

## 5. 证据绑定

每次新 Attempt 落盘必须包含：

```yaml
attempt_id: "RB31-*"
attempt_kind: "REBASE_FORMAL"
replays: "被重放的原 attempt_id（仅 RB31-R* 有）"
contract_ref: "V1_M4_EVIDENCE_COLLECTION_CONTRACT_v0.4.md"
current_task_contract_hash: "a5735c319402056f3c8552da229c816324a8a4ce56f36e0d781924114d68b40a"
candidate_commit: "本次运行所绑定的仓库 commit"
dify_app_id / dify_workflow_id / dify_published_version
provider_bindings
model_provider / model_name / completion_params
input_sha256
run_id
elapsed_s
raw_response
node_trace
outputs:
  user_delivery / user_delivery_status / delivery_outcome / recovery_used
  artifact / artifact_status / returns_json / seam_trace_json
timestamp
```

落盘位置：`decision-chain/evidence/m4/rebase_ac31/`。**新目录，不覆盖既有 `runs/`、`swaps/`、`samples/`、`ac15_eval/` 与 `candidate_0dcd66f/`。**

---

## 6. 影响面（结果前声明）

```yaml
changed_bindings:
  - "RETURNS_ADAPTER_CODE（新增 needs_projection / projection_source 两个输出）"
  - "SEAM 图结构（新增 projection_gate / recovery_llm / delivery_finalize 三个节点及连线）"
  - "END 输出来源（user_delivery / user_delivery_status / returns_json 改由 delivery_finalize 提供；新增 delivery_outcome / recovery_used）"
  - "六个能力 TEST DSL 与接缝 DSL 的 published graph"

direct_dependents:
  - "AC-31 用户可见交付非空"
  - "AC-13 内部 Artifact 与用户交付分离"
  - "AC-14 Return、恢复与幂等"
  - "AC-12 Runtime 保真绑定"
  - "AC-16 Runtime 与远程收口"

transitive_dependents:
  - "所有以 user_delivery 为证据来源的 criterion"
  - "Founder Canvas 端到端用户可见路径"

unknown_dependency_items:
  - "以 outputs 字段名做键读取的历史判定脚本（新增字段是否影响其取值需现场核验）"

not_affected_with_reason:
  - "六份源 Skill 专业判断：注入正文 SHA-256 不变，且修复层位于 LLM 之后"
  - "路由与能力选择：capability_resolved / entry_resolved 计算路径未改"
  - "九个保护应用：本轮不导入、不发布、不修改"
```

不多算、不少算；无法判断者标 `STALE` 待定向复验，不为求精确假装已知依赖图。

---

## 7. 本合同不证明什么

- 不证明真实经营提升；
- 不证明完整纵向链已验证；
- 不证明 M5 已完成或已授权；
- 不把 Founder 一次性降级风险接受表述为技术全通过；
- 不判断「哪份内容更好」——AC-15 类比较仍由 Founder 权威域裁决，本轮不重开。

---

`END_MARKER: V1-M4-EVIDENCE-COLLECTION-CONTRACT-v0.4-FROZEN`
