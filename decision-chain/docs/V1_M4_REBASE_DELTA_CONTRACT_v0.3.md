# V1-M4 Rebase Delta 合同 v0.3（冻结，取代 v0.2 的 §2 D-01）

```yaml
version: "v0.3"
supersedes: "V1_M4_REBASE_DELTA_CONTRACT_v0.2.md"
supersedes_sha256: "e3f840b73d16129073e0963540e08af441160850f8537159d9adac40e5660ef7"
amendment_scope: "只改 §2 D-01 的实施位置；其余 §0/§1/§2 D-02…D-06/§3/§4/§5/§6 逐字继承"
amended_before_any_result: true    # амend 时零新运行、零实施；A2 判据先后未被破坏
reason: "实施勘察发现更精确、更小的缺口位置；不静默偏离冻结 Delta，按 v0.2 §0『确需变更另建 v0.3 并说明理由』处理"
task_id: "V1-M4-CAPABILITY-SEAMS-RUNTIME-INTEGRATION-001"
terminal_state_now: "IN_PROGRESS / REBASE_TASK"
```

## 1. 为什么修订

v0.2 的 D-01 把守卫放在**接缝六个收口 code 节点**。实施勘察发现两件事：

**（一）真正的解析点在 Tool 应用内，不在接缝。**
`DIYU_M4_DSL_BUILD_v0.1.py :: RETURNS_ADAPTER_CODE` 是把 LLM 单次输出按
`---M4_ARTIFACT---` / `---M4_USER_DELIVERY---` 标记切成两块的地方，
且**已经存在 N-12 纪律**（解析失败 != NONE，结构损坏置 `PARSE_FAILED`、保留原文、局部阻断）。

其缺口精确到三处，均为「块存在但内容无效」：

```text
artifact is None        → 已有处置（artifact_status = STRUCTURE_MISSING_RAW_PRESERVED）
artifact 是回指          → 无检查
artifact 过短            → 无检查
user_delivery 为空字符串 → _between() 返回 "" 而非 None
                          → user_status = "OK"  ← 空交付正是从这里被放行的
```

**（二）Tool 已算出的阻断信号，在接缝被整体丢弃。**

Tool END 节点导出 `local_block` / `artifact_status` / `user_delivery_status` /
`structure_notes`；接缝收口节点的 `variables` **只取** `artifact` / `user_delivery` /
`returns_json` / `binding_json`，**四个状态信号一个都不消费**。

即：**现有 N-12 纪律算出来后没有端到端生效。** 登记为 `M4-FND-012`。

**结论**：把守卫只放在接缝，是在下游打补丁（A3 明令「修复指向最高失效节点，不在下游打补丁」）。
正确位置是解析点本身 + 接缝消费其结论。修订后的 Delta **更小**（复用既有 N-12 机制，
不新造机制），且**更接近最高失效节点**。

## 2. D-01 修订版（取代 v0.2 §2 D-01）

### D-01a · 解析点补齐「块存在但内容无效」（最高失效节点）

**对象**：`DIYU_M4_DSL_BUILD_v0.1.py :: RETURNS_ADAPTER_CODE`（生成器，六能力共用一份模板）

**改法**：扩展既有 `artifact_status` / `user_status` 判定，**不新增机制、不新增输出字段**。

```text
新增状态取值（复用既有字段）：
  artifact_status      += BACKREF_COLLAPSED | BELOW_MIN
  user_delivery_status += EMPTY | BACKREF_COLLAPSED

判定按 V1_M4_EVIDENCE_COLLECTION_CONTRACT_v0.2 §1.1 冻结阈值：
  BACKREF_MARKERS / MIN_ARTIFACT_CHARS = 400 / CHECK_WINDOW = 200 / legit_block

既有 blocked 表达式已含 `artifact_status != "OK" or user_status != "OK"`，
因此新状态自动汇入 local_block="true"，无需改 blocked 逻辑。
```

**外壳字段零新增** —— 保护 `AC-02` 合取项②不被打破。

### D-01b · 接缝消费阻断信号（端到端生效）

**对象**：`DIYU_M4_DSL_BUILD_v0.1.py` 中生成六个 `接缝收口｜*` code 节点的模板。

**改法**：

1. `variables` 追加 `tool_local_block` / `tool_artifact_status` / `tool_user_delivery_status`
   （**这是节点入参，不是外壳输出字段**，不影响 AC-02）
2. `local_block == "true"` 时，不再 `tool_artifact or ""` 静默放行，
   而是写入组件级 Return 到既有 `returns_json`：

```yaml
return_id: "M4-RET-SEAM-COMPLETENESS-<call_hash[:8]>"
source: "SEAM_COMPLETENESS_GUARD"
highest_damaged_layer: "CAPABILITY_OUTPUT_COMPLETENESS"
precise_gap: "<artifact_status> | <user_delivery_status>"
affected_objects: ["本次 <capability> 调用的产出块"]
proposed_disposition: "ESCALATE"
needs_user_decision: true
downstream_stale: ["仅真实依赖本次 <capability> 产出的下游项"]
parse_status: "PARSE_FAIL"
```

3. `seam_trace_json` 记 `completeness_guard: {checked: true, tool_local_block: <值>,
   artifact_status: <值>, user_delivery_status: <值>}`

**外壳输出字段零新增** —— 复用既有 `returns_json` / `seam_trace_json`。

### D-01 修订对影响面的作用

**无变化。** v0.2 §4 冻结的影响面（`STALE 28` / `复用 2` = AC-01、AC-30）继续有效：
D-01a 改的是 Tool 应用内的 code 节点，D-01b 改的是接缝 code 节点，
两者都进入「变化的收口节点 + published version/provider」绑定，
与 D-02 改 prompt 的影响面**完全重叠，不扩大**。

## 3. 新增发现登记

```yaml
- id: "M4-FND-012"
  what: "Tool 应用已计算并导出的 local_block / artifact_status / user_delivery_status /
         structure_notes 四个阻断信号，接缝收口节点全部不消费"
  severity: "HIGH"
  status: "FIXED_IN_THIS_REBASE"          # 由 D-01b 承接
  discovered_by: "本 Rebase D-01 实施勘察"
  relation_to_FND_011: "同一根因链的第 5 环 —— 不只是缺守卫，是既有守卫的结论被丢弃"
  consequence_if_unfixed: |
    即使 D-01a 把塌陷判出来，接缝仍会 tool_artifact or "" 静默放行，
    修了等于没修。这是 D-01 必须分 a/b 两半的原因。
```

## 4. 未变更条款

v0.2 的 §0 身份与授权、§1 WHAT/WHY/BOUNDARY/ACCEPTANCE、§2 D-02…D-06、
§3 AC-31、§4 影响面、§5 执行顺序、§6 预授权采样合规性 —— **全部逐字继承，不改。**
