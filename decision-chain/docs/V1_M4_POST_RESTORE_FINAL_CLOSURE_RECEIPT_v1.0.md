# 笛语 V1 M4 · 恢复后完全收口回执 v1.0

> 权威域：当前状态证据域。本回执**只取代「当前状态指针」**，不改写任何历史技术结果。
> 旧回执 `V1_M4_FINAL_CLOSURE_RECEIPT_v0.1.md` 及其 `BLOCKED` 终态继续是当时的真实历史，逐字节保留。
> 执行侧不得自行把合同状态往上推一级；本轮终态由已冻结的 `M4-PCR-01..12` 逐项推导。

```yaml
receipt_id: V1-M4-POST-RESTORE-FINAL-CLOSEOUT-RECEIPT
receipt_version: v1.0
supersedes_current_status_only: decision-chain/docs/V1_M4_FINAL_CLOSURE_RECEIPT_v0.1.md
supersedes_history: false
prior_receipt_sha256: "df74c47f23fd614b9b35b342b7b76a66d237ef40df7ab1b96b22ed4cf416f11d"
prior_receipt_bytes_preserved: true
```

## 一、四层分离

```yaml
historical_technical_results:
  disposition: PRESERVED_NOT_REWRITTEN
  previous_formal_status: BLOCKED
  preserved:
    AC31_④: NOT_VERIFIED
    historical_AC31_⑤: NOT_VERIFIED
    M4-RB31-03_under_v0.4: NOT_VERIFIED
    M4-RB31-05_under_v0.4: FAIL
    M4-CL31-02: NOT_VERIFIED
    M4-CL31-03: FAIL
    M4-CL31-04: FAIL
    M4-CL31-05: NOT_VERIFIED
    M4-CL31-07: FAIL
    M4-CL31-08: FAIL
  note: >
    以上一条都没有被改成 PASS。它们是历史技术事实，本轮不重新裁定，
    也不因 Founder 的一次性风险接受而变绿。

founder_product_disposition:
  M4_FOUNDER_ACCEPTANCE: PASS
  historical_residual_risk: ACCEPTED_FOR_THIS_DELIVERY_ONLY
  does_not_generalize: true
  authority_scope:
    - product acceptance
    - one-time risk acceptance for disclosed historical technical residuals
    - final delivery scope and M5 handoff permission
  note: >
    Founder 的处置属产品语义与风险接受，与上面的技术结果分层存放，互不改写。

current_rebase_acceptance:
  criteria: M4-PCR-01..M4-PCR-12
  result: PASS

task_terminal_state:
  task_final_status: DONE
  next_stage_allowed: "true:M5_INTEGRATION_HANDOFF"
  m5_engineering_execution_started: false
```

## 二、本轮验收逐项结果

| 判据 | 结果 | 依据 |
|---|---|---|
| M4-PCR-01 | PASS | 同 task_id；`REBASE_TASK`；合同与规划侧 canonical 逐字节相同；旧 BLOCKED 回执在位 |
| M4-PCR-02 | PASS | 分支 `codex/v1-m4-capability-seams-runtime-integration-001`；本地与远端一致性在推送后现场复核 |
| M4-PCR-03 | PASS | `pgdata` / `storage` 容器内 inode 与宿主一致；数据库非空；容器健康 |
| M4-PCR-04 | PASS | 八应用保留原 ID、已发布，当前图 sha256 与冻结候选 `3bf324ec` 逐一相等 |
| M4-PCR-05 | PASS | 六能力 / Seam / Canvas 的真实 run 绑定到当前**已发布**工作流与冻结图 |
| M4-PCR-06 | PASS | 绑定证据中空正文 0、thinking 泄漏 0 |
| M4-PCR-07 | PASS | 六源 Skill、六专业正文、六 `skill_llm` 模型参数相对冻结候选零变化 |
| M4-PCR-08 | PASS | 注入对象无 tool provider；八个正式应用图对注入对象零反向引用 |
| M4-PCR-09 | PASS | M5 映射的应用 / 工作流 / tool / 上下游 / IO 合同与当前目标系统一致 |
| M4-PCR-10 | PASS | 旧回执与旧技术结果逐字节保留；Founder 处置单列 |
| M4-PCR-11 | PASS | 终态由 PCR-01..10 与 12 一致推导，见本节与第一节 |
| M4-PCR-12 | PASS | 本轮零工程资产变更、零越界文件、八应用图未变 |

## 三、目标系统绑定

```yaml
dify_environment:
  bind_mount_verified: true
  pgdata_inode_host_equals_container: true
  storage_inode_host_equals_container: true
  counts_snapshot:
    apps: 50
    workflows: 280
    workflow_runs: 2276
    tenants: 1
    accounts: 1
  note: 计数为动态观察，不作为冻结验收数字

applications:
  - capability: "FOUNDER_CANVAS"
    app_id: "f0b1c5f5-afc5-43e9-9ea4-ae36e25f33c8"
    workflow_id: "61c4ce01-8924-4330-90ef-d9d1dd78b5ff"
    graph_sha256: "27f6aa48fce03c2e775727e417beec6ecc9c45f17a81a2de76f1c81a8bfed502"
    published: true
    graph_matches_frozen_candidate: true
  - capability: "CAPABILITY_SEAM"
    app_id: "de0cb1e9-2af8-415a-9762-31b6cf348c22"
    workflow_id: "4c5e2bab-9a4b-47f0-8ab0-1b844df4bb9d"
    graph_sha256: "9aec7d10bebd3260475c45cd6408868642d05e9d19bae99a9af4919548e805bf"
    published: true
    graph_matches_frozen_candidate: true
  - capability: "MATRIX"
    app_id: "d7c2cc11-9a59-47eb-93d7-a25ebc0b8cc3"
    workflow_id: "3a9e0d8b-8151-4922-acd7-0926a6af49fd"
    graph_sha256: "9eded1bdc1dfe4d5b1013b640549557a53208de8f90d95bde25fbc669d1ec3dd"
    published: true
    graph_matches_frozen_candidate: true
  - capability: "CAMPAIGN"
    app_id: "cfd48281-d2e6-4f77-b4a6-32f0fca98f2b"
    workflow_id: "2da44fc7-09f0-4ed3-a000-addc641e077a"
    graph_sha256: "21817761588b1efe09f30e89cf2372156a8885b66761f13d6fe271853b9d5097"
    published: true
    graph_matches_frozen_candidate: true
  - capability: "CONTENT_BRIEF"
    app_id: "a3264c95-9b30-4ac8-833a-dc96ea8b7ee1"
    workflow_id: "7f7fe5d1-3217-43e6-a3ed-7450b64b070b"
    graph_sha256: "e8e4268d2692a74f8f8c90a32e78e5d75d7b53abf2ff1877e34d362ff7fcc863"
    published: true
    graph_matches_frozen_candidate: true
  - capability: "CREATIVE_SCRIPT"
    app_id: "8d518554-bfbc-4be0-8a57-3b1f04983edf"
    workflow_id: "3341b4de-e658-42a8-bc49-26fcf7e30bf7"
    graph_sha256: "a04c33276a7c833bff34df9c0165a2d352eb457e7c60bf7de797459f27a198a8"
    published: true
    graph_matches_frozen_candidate: true
  - capability: "PRODUCTION_DIRECTOR"
    app_id: "57ebc138-ed9e-4202-bce2-38e44da0ec1d"
    workflow_id: "9a81b5c9-3773-44a6-af19-6255f8f30dce"
    graph_sha256: "89e7b6207e3aeebafd3b1d17b53aa041e821bfbee1afaa975f64aa3bf4256ef8"
    published: true
    graph_matches_frozen_candidate: true
  - capability: "PUBLISHING_PACKAGING"
    app_id: "10056fcf-9237-4889-a3e3-81e3a695cae0"
    workflow_id: "d838536b-6779-4d1e-951f-4cdabffa50d7"
    graph_sha256: "f3f0ed03e665be5738db6ce3acdcd31bad5ce347194537154b5779da6fff6f65"
    published: true
    graph_matches_frozen_candidate: true

bound_runtime_evidence:
  - capability: "MATRIX"
    run_id: "b042ad51-686f-4ed5-8cad-170db50b80f8"
    delivery_outcome: "DELIVERED"
    skill_llm_succeeded: 1
    user_delivery_length: 378
    bound_to_current_published_graph: true
  - capability: "CAMPAIGN"
    run_id: "f99add34-0d25-4e8e-8927-4719d59c1c6f"
    delivery_outcome: "DELIVERED"
    skill_llm_succeeded: 1
    user_delivery_length: 556
    bound_to_current_published_graph: true
  - capability: "CONTENT_BRIEF"
    run_id: "40f73dac-05bf-44ed-a733-f0024b3c3f7e"
    delivery_outcome: "DELIVERED"
    skill_llm_succeeded: 1
    user_delivery_length: 648
    bound_to_current_published_graph: true
  - capability: "CREATIVE_SCRIPT"
    run_id: "9ece7eda-39eb-4a27-b0bc-a2b8312bff97"
    delivery_outcome: "DELIVERED"
    skill_llm_succeeded: 1
    user_delivery_length: 1061
    bound_to_current_published_graph: true
  - capability: "PRODUCTION_DIRECTOR"
    run_id: "056e6eb2-5485-465b-b7e8-5d13291b9316"
    delivery_outcome: "DELIVERED"
    skill_llm_succeeded: 1
    user_delivery_length: 800
    bound_to_current_published_graph: true
  - capability: "PUBLISHING_PACKAGING"
    run_id: "afcbc484-0a80-4669-b635-6321dc11b674"
    delivery_outcome: "DELIVERED"
    skill_llm_succeeded: 1
    user_delivery_length: 716
    bound_to_current_published_graph: true
  seam_run_id: "29296b15-d63a-4364-a1a0-2649bd74b273"
  canvas_end_to_end_seam_run_id: "547081e8-af5d-4e83-b9e5-f58519d59219"
  canvas_reached_capability_seam: true

delivery_integrity:
  empty_user_delivery_count: 0
  think_leak_count: 0

fault_injection_objects:
  status: EVALUATION_ONLY_NOT_ROUTABLE
  tool_provider_removed: true
  official_chain_reverse_references: 0

nine_pre_existing_protected_apps:
  diff_count: 0
```

## 四、证据绑定

```yaml
current_task_contract:
  ref: decision-chain/docs/V1_M4_POST_RESTORE_FINAL_CLOSEOUT_TASK_CONTRACT_v1.0.yaml
  sha256: "82f25055eee4cb58a353d928c2de38a7c13cc9cd31bdc1f9ba3746d67ce650f1"
  byte_identical_to_planning_canonical: true
previous_task_contract_hash: "8d73b4f157883eb422e6ae17ececcf87a64d98c6a51f35537b8446155fa85070"
frozen_candidate_commit: "3bf324ec616a80f669e9764bf5dfc4f77f22c5b5"
restore_commit: "c77a7e5d424f8b2db6ff436a662d12699596b0cc"
parent_commit_of_this_closeout: "c77a7e5d424f8b2db6ff436a662d12699596b0cc"
m5_handoff_map:
  ref: decision-chain/docs/V1_M4_M5_HANDOFF_MAP_v0.1.yaml
  sha256: "f1600de64b51784da6e7c3c6e68535423e1b120823cd6a42e413725c860ea45c"
evidence:
  - path: "decision-chain/evidence/m4/post_restore/M4_PCR_NEGATIVE.json"
    sha256: "0259c521b786c013b0ff6400d209243cdb2fcbee72df260038da19efa217599c"
  - path: "decision-chain/evidence/m4/post_restore/M4_PCR_VERIFY.json"
    sha256: "64728a8557fc244cd137406f9e1c33f4aba8e97c01895107ee56c8775e8923e3"
  - path: "decision-chain/evidence/m4/restore/M4_RESTORE_CANVAS_E2E.json"
    sha256: "ce4ed92e99c2e00a84e11ccd0c30df14992e267bd0d748e895838535ed96dc0c"
  - path: "decision-chain/evidence/m4/restore/M4_RESTORE_INJECTION_ISOLATION.json"
    sha256: "16b089bdce9c7794247ea0a39181ee87703b803457c957cd4c2bbe8d9d0b4464"
  - path: "decision-chain/evidence/m4/restore/M4_RESTORE_SMOKE.json"
    sha256: "64f3f091bc997c393a9bd1bc2de27a36b60d9226a81f1f643ee0c8d42027a239"
negative_tests: 9 项全过（含九个既有受保护应用零变化）
note_no_self_reference: >
  本回执绑定父提交、合同、证据与内容哈希；不写回自身提交哈希。
  最终远端 HEAD 完整哈希在推送后于最终回执消息中现场报告。
```

## 五、main 漂移的定向影响判断

`origin/main` 已推进到 `f6eb86c076c47bd9f7c9323caac6c0ba1fc5098e`（M3 并入）。相对分叉点 `ca5281ae` 的定向核验结论：

- 六份源 Skill：main 侧**未改动**
- 八份 M4 DSL：main 侧**未改动**
- M4 任务账本、旧回执、旧合同、M5 映射：**不存在于 main**，仅在本任务分支

因此 main 漂移对本轮收口绑定**零影响**，无项被置 `STALE`。本轮未 rebase、未 merge、未改写 M4 分支。

## 六、本轮 DONE 的准确含义

**是**：

- M4 最终 Dify 成果已恢复且当前可运行；
- 受保护专业链未变；
- 用户空交付与 thinking 泄漏的修复已由当前绑定证据建立；
- Founder 已接受本次交付与已披露风险；
- 正式任务状态与 M5 交接权限已形成后继权威记录。

**不是**：

- 所有历史技术判据都变成 PASS；
- M5 已经施工或通过；
- 已生产上线；
- 已验证真实运营闭环；
- 已证明经营提升。

## 七、仍然开放、交规划侧的历史事项（不阻断本轮）

| 编号 | 事项 |
|---|---|
| M4-FND-027 | `CL31-02⑤` 与⑥在发生基础设施重试时互斥 |
| M4-FND-030 | `CL31-03⑥` 的长度阈值那一半无判别力，对短 artifact 结构上不可满足 |
| M4-FND-031 | `CL31-04` 必保内容用精确子串匹配中文自由文本，同义改写即假阴性 |
| M4-FND-032 | 部分能力用户正文以 `status: READY_WITH_CONDITIONS` 开头，内部状态词外露 |
| M4-FND-033 | 事实回查提取器对专有名词、商品名、地点召回接近零 |
| M4-ENV-001 | 已更正：21:38 事件为整栈重启时 bind mount 未挂上，非整库销毁；宿主数据完好并已恢复 |

## 八、简化追加 Prompt 001 规定字段块

依据 `M4_POST_RESTORE_FINAL_CLOSEOUT_SIMPLIFICATION_ADDENDUM_001`（`priority_on_conflict: THIS_ADDENDUM_PREVAILS`）第三步第二项，
本节按其规定字段原样记录本轮收口结论。本节为追加，不覆盖前七节，也不改写任何历史记录。

```yaml
task_id: V1-M4-CAPABILITY-SEAMS-RUNTIME-INTEGRATION-001
task_entry_mode: REBASE_TASK

historical_status:
  previous_formal_status: BLOCKED
  previous_receipts_preserved: true
  historical_technical_results_preserved: true
  historical_results_rewritten_as_pass: false

founder_disposition:
  M4_FOUNDER_ACCEPTANCE: PASS
  disclosed_residuals: ACCEPTED_FOR_THIS_DELIVERY_ONLY

restored_delivery:
  M4_FINAL_DIFY_DELIVERY: RESTORED
  M4_DIFY_APPLICATIONS: RUNNABLE
  application_count: 8
  empty_user_delivery_count: 0
  think_leak_count: 0
  six_skill_fidelity_changed: false
  m4_m5_handoff_map: V1_M4_M5_HANDOFF_MAP_v0.1.yaml

task_final_status: DONE
next_stage_allowed: true:M5_INTEGRATION_HANDOFF
m5_engineering_execution_started: false
```

### 8.1 现场确认（追加 Prompt 第一步，只读）

```yaml
branch: codex/v1-m4-capability-seams-runtime-integration-001
worktree_clean: true
eight_final_apps_present: true
eight_final_apps_published: true
app_ids_unchanged: true
restore_evidence_files_readable: 3
m5_handoff_map_readable: true
new_model_calls_this_round: 0
blocking_conditions_hit: 0
```

八个最终应用与其当前已发布工作流（现场只读复核）：

| 能力 | app_id | 已发布工作流 |
|---|---|---|
| Founder Canvas | `f0b1c5f5-afc5-43e9-9ea4-ae36e25f33c8` | `61c4ce01-8924-4330-90ef-d9d1dd78b5ff` |
| Capability Seam | `de0cb1e9-2af8-415a-9762-31b6cf348c22` | `4c5e2bab-9a4b-47f0-8ab0-1b844df4bb9d` |
| Matrix Architect | `d7c2cc11-9a59-47eb-93d7-a25ebc0b8cc3` | `3a9e0d8b-8151-4922-acd7-0926a6af49fd` |
| Campaign Orchestrator | `cfd48281-d2e6-4f77-b4a6-32f0fca98f2b` | `2da44fc7-09f0-4ed3-a000-addc641e077a` |
| Content Brief Architect | `a3264c95-9b30-4ac8-833a-dc96ea8b7ee1` | `7f7fe5d1-3217-43e6-a3ed-7450b64b070b` |
| Creative Script | `8d518554-bfbc-4be0-8a57-3b1f04983edf` | `3341b4de-e658-42a8-bc49-26fcf7e30bf7` |
| Production Director | `57ebc138-ed9e-4202-bce2-38e44da0ec1d` | `9a81b5c9-3773-44a6-af19-6255f8f30dce` |
| Publishing & Packaging | `10056fcf-9237-4889-a3e3-81e3a695cae0` | `d838536b-6779-4d1e-951f-4cdabffa50d7` |

### 8.2 Dify 事故事实更正（写清楚，不删除原记录）

**此前不是数据库被清空。** 是 Dify 整栈重启时 bind mount 一度没有挂上：容器内 `pgdata` / `storage`
指向的是容器自身镜像层的空目录（inode 34 / 19），而不是宿主目录（inode 203539 / 203532）。
postgres 于是对着那个空目录跑了一次 `initdb`，产出只有 76.3 MB，**看起来像是被初始化**。

宿主机原始数据自始至终完好：`pgdata` 688.3 MB，数据库目录 `16384 / 16385 / 31985` 俱在。
恢复挂载后，原应用、原 app ID、原工作流与原运行记录全部回归，未做任何数据恢复或伪造。

原「整库重新初始化」描述作为当时的真实观察保留在历史段落，本节只做事实更正，不回改历史文本。

`END_MARKER: V1-M4-POST-RESTORE-FINAL-CLOSEOUT-RECEIPT-v1.0-END`
