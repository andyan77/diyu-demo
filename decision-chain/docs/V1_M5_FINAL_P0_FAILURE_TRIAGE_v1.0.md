# M5 最后一轮最小修复 · Step 1 FAILURE TRIAGE v1.0

```yaml
document_id: V1_M5_FINAL_P0_FAILURE_TRIAGE_v1.0
task_id: DIYU-V1-M5-UNIFIED-INTEGRATION-FINAL-ACCEPTANCE-001
entry_mode: REBASE_TASK
step: STEP_1_FAILURE_TRIAGE
task_progress: IN_PROGRESS
terminal_state: unset
main_merge: NOT_ALLOWED

prompt:
  path: /mnt/c/Users/Administrator/Documents/Codex/Diyu-V1-Planning/M5_FINAL_MINIMAL_P0_REMEDIATION_AND_NEXT_STAGE_EXECUTION_PROMPT_v1.0.md
  sha256: 94b73c096e726d3ab8edd5a0331a175dc1f477dd933f30f0e6adb81e5c736558
parent_prompt_sha256: 9b988027438f498b25421cecd73cd9d9d302bddcf15876c6b9833eaf624ddecb   # 现场复算一致
parent_contract_sha256: a13b5651c2065eb8ffd70c1cdbf4bf1de09fbc39f7bb5693b31231f2da2ce7dc # 现场复算一致
handoff_evidence_sha256:
  V1_M5_RB3_DIRECTED_REVERIFICATION_v1.0.md: dd2d49d9814c275c8f63a4fd7a16fdf636e192a78c4133c310312eda4a023c7b
  V1_M5_RB_HOLDOUT_VERDICT_v1.0.md:          cc6460168654ba09b78279de0927923380b713074660154b5513c9bf8270188b
  V1_M5_CANDIDATE_RUN_MANIFEST_v1.1.3_AC07_REBASE.yaml: 2dba81e9d16d9085dc8720edb859091f5296558ec950e4bdec1fdaa8a27cd7f0

git:
  branch: codex/v1-m5-unified-integration-final-acceptance-001
  head_at_triage: 502c97f7b10fa62504472b57634b8f0d6dcc2c5b
  worktree_clean_at_triage: true
  candidate_commit: d4b26f29ed3d8bb91235170e3c5810e23d98e3e8

app_binding: M5_BIND=rb
  M3:                   ca4c28aa-e0fd-4c54-bde3-a0918dc4c884
  SEAM:                 9e1b1fd8-f696-436d-9d42-54700a29a4dd
  HOP_ADAPTER:          6c46fdb1-5f49-4513-a0c0-29957b3dcee4
  CONTENT_BRIEF:        cbbeab61-a4de-4a21-a6be-7dc2385dd6f3
  MATRIX:               47e52165-f6cb-48ff-93be-6c6a8ea5cecf
  CAMPAIGN:             7d10e28d-30e6-4c4a-950b-88dcbb5fd0fc
  CREATIVE_SCRIPT:      4fbcfea8-48a3-41b3-b2b5-cdb50276eeb2
  PRODUCTION_DIRECTOR:  07e99f7b-71a3-40af-85f3-fc43b68e774a
  PUBLISHING_PACKAGING: 0fb7636a-55e8-49a9-92f7-3d11ad0a35fa

node_binding_evidence: decision-chain/evidence/m5/FINAL_P0_TRIAGE_NODE_BINDING.json
node_binding_generator: decision-chain/workflows/DIYU_M5_TRIAGE_NODE_BINDING_v1.0.py
dify_apps_modified_in_step_1: []
model_calls_in_step_1: 0
```

本文件只做归因。**未修改任何被测对象、判据、夹具或已发布应用；Step 1 内零模型调用。**

---

## 0. 归因结论先行：节点分布与 Prompt 的分组不同

Prompt §5 Step 1 把 `HOLDOUT-M5-RB-01` 与 `HOLDOUT-M5-05` 交付层残余合为 Group A。
按独立证据，**这两者的最高失效节点不是同一个**：

```text
Prompt 分组              实际最高失效节点
────────────────────────────────────────────────────────────────
Group A · RB-01     →   M3 successor         ca4c28aa
Group A · M5-05 残余 →   CONTENT_BRIEF 应用    cbbeab61（经 returns_adapter 共享节点）
Group B · RB-02     →   M3 successor         ca4c28aa
```

按 Prompt「不得因为两个现象看起来相似就假定同一根因……证据不足时分开处理」，
本文件**不合并** Group A 的两支，改按节点重分组：

```text
节点 N1 = M3 successor ca4c28aa           承担 RB-01 与 RB-02
节点 N2 = 六能力共享 returns_adapter        承担 M5-05 的内部状态词泄漏
节点 N3 = CONTENT_BRIEF 的 skill_llm 提示词  承担 M5-05 的判断层→交付层变形
```

N2 与 N3 都落在 M5-05 这一支，但**是两个不同缺陷**：一个是确定性检查表漏项，
一个是模型表达失真。分开修，分开验。

---

## 1. Group A（Prompt 定义）· 第一支：HOLDOUT-M5-RB-01

```yaml
observed_failure: |
  第 2 轮 M3 输出「上周已发那条『西装配裤子还是配半裙』同样来自这组试穿，也一并标记失效」；
  第 3 轮「继续标记失效」；第 4 轮「系统内保持失效」。
  两个问题：
  (a) 把已发布内容的系统内失效当作素材撤回的下游一并处理，未作为独立经营决定；
  (b) 用完成态陈述一个从未发生的写入 —— 本轮 M3 无写权限，
      content_versions.invalidated_at 对四个版本全部为 NULL。

frozen_target: |
  HOLDOUT-M5-RB-01 封存判据（custody sha256
  5d0f9902369acc0afff68212bda028230ddc27e2146095e5cda779e213393371，解封时哈希一致）
  §1.2-3 影响面不得扩大到已发布内容；§0.3 不得声称未发生的副作用。
  判据在运行前冻结，本轮未改。

candidate_sources:
  CONTRACT_OR_INTENT:        排除 —— 判据与 Prompt §3.A 口径一致，无歧义
  ORACLE_OR_CRITERION:       排除 —— 同一判据下该留出的其余八个风险面全部成立
  CHECKER_OR_FIXTURE:        排除 —— 四轮输入逐字来自封存正文，隔离核验通过
  INPUT_ENVIRONMENT_OR_TOOL: 排除 —— 四轮 gate_status 全 CLEAN，无传输失败
  SYSTEM_UNDER_TEST:         【确认成立】
  INSUFFICIENT_EVIDENCE:     不适用

confirmed_origin: SYSTEM_UNDER_TEST
highest_failing_node: M3 successor ca4c28aa-e0fd-4c54-bde3-a0918dc4c884

evidence:
  file: decision-chain/evidence/m5-rb/HOLDOUT_RB_RUNS_formal.json
  route_caps: []            # 本留出只跑 M3，未进入任何能力应用
  dify_runs:
    turn_1: 7fae3d9c-e232-4f00-ac53-ba9ba96c3eec
    turn_2: 4a4ea263-15cb-4322-976f-03696cf65659   # 失败句所在
    turn_3: cbe26464-fc65-4a43-a10d-bbd31688b585
    turn_4: 2463ce4a-d74e-4be6-9c93-d5950caacae2
  attribution_logic: |
    本轮只有 M3 一个应用运行，输出文本即 M3 自身产物，不存在下游改写的可能。

mutation_target: M3 successor 的运营判断提示词（撤回影响面切分 + 副作用真实性）
protected_targets: |
  M3 已接受应用 b7fb5b1a（legacy）字节不动；本留出其余八个风险面已成立的行为不得回退；
  封存判据不改；HOLDOUT_RB_RUNS_formal.json 只增不覆盖。
next_reverification: 原留出重跑 + FINAL-P0-HOLDOUT-01（Step 2 冻结）
```

**已成立、不得回退的八个风险面**（同一份输出中同时成立，是最小修复必须保住的基线）：
记录优先于记忆的恢复、影响面不少算（主动补上用户未点名的第一条）、第二条原样保留、
写前核对、传输失败与语义失败分离、拒绝删除失败记录、接受经营自主权、
零内部状态词泄漏；`task_run_states` 字段级一致。

---

## 2. Group A（Prompt 定义）· 第二支：HOLDOUT-M5-05 交付层残余

```yaml
observed_failure: |
  同一次运行里两层说法互相矛盾，且内部状态词进入用户可见输出：
  M3 层：「只重建该重建的」，并有独立小节「为什么不是『全部重来』」；
  用户可见层：以「status: READY」开头，正文「从头跑完了。」「按你的要求整轮重跑了。」

frozen_target: |
  Prompt §3.C 与 FINAL-AC-03：M4 用户交付须忠实保留 M3 的影响范围与拒绝理由，
  不得把「只重建受影响项」改写为「整轮重跑／从头跑完」；
  用户可见输出不得泄漏 READY／STALE／PASS／FAIL 等内部状态词。

candidate_sources:
  CONTRACT_OR_INTENT:        排除
  ORACLE_OR_CRITERION:       排除
  CHECKER_OR_FIXTURE:        部分成立 —— 见下方 N2，泄漏检查表本身漏项
  INPUT_ENVIRONMENT_OR_TOOL: 排除 —— 运行成功，无传输失败
  SYSTEM_UNDER_TEST:         【确认成立】
  INSUFFICIENT_EVIDENCE:     不适用

confirmed_origin: SYSTEM_UNDER_TEST（两个不同节点，见下）

evidence:
  file: decision-chain/evidence/m5/HOLDOUT_RUNS_rb3rv1.json
  hop_run:        2d7d1a2b-bf72-45ca-b953-f8fc4f9129cf
  seam_run:       3b8a88f2-84f6-49f3-bc9d-e3732a4136b8   app 9e1b1fd8（接缝）
  capability_run: a742d63a-6990-476b-9fff-9add3564f52f   app cbbeab61（CONTENT_BRIEF）
  authorship_proof: |
    带泄漏与变形的 user_delivery 是 **CONTENT_BRIEF 应用**的输出，不是接缝的。
    markers_in_capability_user_delivery = {status: READY: true, 整轮重跑: true, 从头跑完: true}
  upstream_negative_control: |
    同三串在 hop 适配器 outputs 中全部为 false；
    professional_input 逐字含 M3 判断全文，含「为什么不是」小节。
    ⇒ 上游把正确语义完整交到了能力侧，变形发生在能力侧。
  self_report_contradiction: |
    该运行自报 user_delivery_leaks=[]、user_delivery_status=OK、recovery_used=false。
    检查器说没有泄漏，而 `status: READY` 就在正文第一行。
```

### 2.1 节点 N2 —— 六能力共享 `returns_adapter` 的泄漏检查表漏项

```yaml
highest_failing_node: returns_adapter 代码节点（六个能力应用共享同一份）
identity_proof: 归一化后（仅替换 CAPABILITY 常量）六个能力逐字节同一份
  returns_adapter_sha256_normalized = 3108bd58455ae2db…（MATRIX / CAMPAIGN /
  CONTENT_BRIEF / CREATIVE_SCRIPT / PRODUCTION_DIRECTOR / PUBLISHING_PACKAGING 六比六全等）
  LEAK_PATTERNS 同一份；delivery_finalize 同一份
defect: |
  按宪法 §4 统一状态词逐项核对 LEAK_PATTERNS：
    已覆盖 2 个：NOT_VERIFIED、STALE
    缺失 14 个：PASS、FAIL、CURRENT、APPLICABLE、NOT_APPLICABLE、NOT_STARTED、
               IN_PROGRESS、COMPLETED、INVALID、DONE、PARTIAL、BLOCKED、FAILED、READY
  `READY` 不在表内，故 `status: READY` 未被拦下，user_delivery_status 记为 OK。
second_defect: |
  delivery_finalize 里另有一份 LEAK 表，但只在**恢复分支**生效；
  M5-05 走的是正常分支（recovery_used=false），该表根本没执行。
  两份表并存且覆盖面不同，本身就是可消融的重复。
mutation_target: returns_adapter 的状态词检查（补全状态词表 + 结构性状态行检测）
why_this_is_the_highest_node: |
  它是六个能力的共享失效节点，与当年 `_find_scalar` 解析器修复同构（6+1 successor）。
  只改 CONTENT_BRIEF 一个能力属于在下游打补丁，其余五个能力同样漏。
not_a_case_whitelist: |
  修复必须是通用状态词规则（宪法 §4 全集 + `key: VALUE` 状态行结构检测），
  不得写成针对 `status: READY` 这一串的专用分支。
```

### 2.2 节点 N3 —— CONTENT_BRIEF 的判断层→交付层保真

```yaml
highest_failing_node: CONTENT_BRIEF successor cbbeab61 的 skill_llm 用户交付段
defect: |
  professional_input 逐字含 M3 的「只重建该重建的」与「为什么不是『全部重来』」，
  能力侧仍写出「按你的要求整轮重跑了」「从头跑完了」——
  把用户的原始要求当成已执行事实，覆盖了上游的明确拒绝。
mutation_target: 用户交付段的保真约束（忠实保留上游影响范围与拒绝理由）
disclosure: |
  N3 是提示词层的表达失真，无法用确定性检查完全拦住；
  N2 的状态词检查拦不住它。两者必须分别验，不得用其中一个的通过替另一个背书。
```

---

## 3. Group B：HOLDOUT-M5-RB-02

```yaml
observed_failure: |
  变体 N（「商品那块我回头再补，先把能定的定了」）在关键商品身份缺失时
  仍走完内容生产链，business_delivery_outcome = DELIVERED，
  产出含 XQ-2501/2502/2503 具体款、材质、价格与拍摄安排的完整简报。

frozen_target: |
  HOLDOUT-M5-RB-02 封存判据（custody sha256
  b30af78d…3264b38，解封时哈希一致）在场判别；
  Prompt §3.B：缺商品身份或内容方向且权威输入不能唯一推出时停止内容生产链，
  不得从旧周期或历史上下文挑 SKU 代替用户决定。

candidate_sources:
  CONTRACT_OR_INTENT:        排除
  ORACLE_OR_CRITERION:       排除 —— 同判据下 A/B/C 三个等价变体六行机器判定全部通过
  CHECKER_OR_FIXTURE:        排除 —— 四变体各自独立 bootstrap、独立 M2 工作区、各只发一次
  INPUT_ENVIRONMENT_OR_TOOL: 排除 —— m3_gate_status = CLEAN
  SYSTEM_UNDER_TEST:         【确认成立】
  INSUFFICIENT_EVIDENCE:     不适用

confirmed_origin: SYSTEM_UNDER_TEST
highest_failing_node: M3 successor ca4c28aa-e0fd-4c54-bde3-a0918dc4c884

evidence:
  file: decision-chain/evidence/m5-rb/HOLDOUT_RB_RUNS_formal.json
  variant_N:
    m3_run:   97325da6-7236-4093-8664-5069d774685b   gate CLEAN
    hop_run:  632d6c7b-90f9-4b29-bf02-178cce5e528f   extraction_gaps = 无
    seam_run: 04b2d1e3-de08-4a24-beba-2ff08df0ebd3   outcome DELIVERED
  variants_ABC_m3_runs:
    A: 0b23a904-0e87-4898-b27e-fb0613f3e368
    B: d71c2597-1f64-4b0b-814c-f218271db331
    C: d9fc39a6-c3be-4695-9d74-df255cc1508a
```

### 3.1 关键判别：下游没有篡改，猜测发生在 M3

M3 自己既点明了缺口，又同时把缺口填上并派发：

```text
M3 承认缺口：  「定不了的：…具体商品组合等你补的商品信息确认」
M3 自行填补：  「我先按已登记的西装、阔腿裤、衬衫三件候选准备」
M3 派发下游：  「可以往内容简报环节派发一条内容任务」
```

下游**忠实保留了限定，没有把候选升级为已确认**：

```text
hop source_map:      facts_registered = "M3"（来源标注正确）
hop capability_call: 「西装、阔腿裤、衬衫三件候选，已有材质、价格和版型登记」
Brief artifact:      「商品信息细节待用户补充（西装、阔腿裤、衬衫三件候选…）」
                     当前状态：BRIEF_READY_WITH_CONDITIONS（平台未锁定、商品细节待用户补充）
```

⇒ **hop 与 CONTENT_BRIEF 未违反各自合同**，`extraction_gaps=无` 是对 M3 已填满字段的忠实反映。
最高失效节点唯一，在 M3。

### 3.2 停止机制存在，只是没被触发

运行器有 `if capability_call 非空` 的停止分支，能力侧另有 envelope 充分性闸。
若 M3 停在缺口不填字段，该链路本就会停下。因此**不需要新增停止机制**，
只需 M3 不替用户选商品。

```yaml
mutation_target: M3 successor 的关键业务输入在场判断（停在缺口，不自选商品／方向）
protected_targets: |
  A/B/C 三个等价变体的一致可交付性必须保持 —— 修复不得把系统改成「什么都拒绝」；
  hop 适配器与六个能力应用在本组无证据证明有错，不修改。
next_reverification: 原留出重跑（含 A/B/C 等价性）+ FINAL-P0-HOLDOUT-02（Step 2 冻结）
```

---

## 4. 汇总：修改面与保护面

```yaml
allowed_mutation_targets:
  N1: M3 successor 提示词 —— 撤回影响面切分、副作用真实性、关键输入在场判断
  N2: 六能力共享 returns_adapter —— 状态词泄漏检查（successor，不覆盖已接受应用）
  N3: CONTENT_BRIEF successor skill_llm —— 用户交付对上游的保真

no_evidence_of_defect_do_not_touch:
  - hop 适配器 6c46fdb1（RB-02 中忠实抽取，RB-02 与 M5-05 上游均正确）
  - 接缝 9e1b1fd8（M5-05 中只透传，未产生变形）
  - M1/M2 全部；M4 解析器修复；参考 Manifest 与证据显式绑定
  - 十九维定义；49 个夹具；M3 已冻结闸门
  - 六份受保护 Skill；M1–M4 已发布应用（legacy 绑定字节不动）
  - 历史运行、原留出、原判定、原 Manifest、原盲评包与全部失败记录

known_limitation_disclosed: |
  N2 的确定性检查修好后仍不能保证 N3 成立：状态词不泄漏 ≠ 表达忠实。
  两者必须各自有正例与负例，不得互相背书。
```

## 5. Step 1 结论

```yaml
step_1_status: COMPLETED
groups_confirmed: 3 个节点（N1 / N2 / N3），与 Prompt 的两组划分不同，已按证据分开
model_calls: 0
dify_apps_modified: []
next_step: STEP_2 —— 由上下文隔离 custodian 冻结两个新鲜微型留出
task_progress: IN_PROGRESS
terminal_state: unset
main_merge: NOT_ALLOWED
```
