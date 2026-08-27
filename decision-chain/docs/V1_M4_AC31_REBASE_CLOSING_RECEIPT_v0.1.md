# 笛语 V1 · M4 AC-31 用户可见交付非空修复 · 收口回执 v0.1

```yaml
task_id: "V1-M4-CAPABILITY-SEAMS-RUNTIME-INTEGRATION-001"
task_entry_mode: "REBASE_TASK"

previous_task_contract_hash: "b3ceabcbe9bcd82dae2fae84161dce0f0aadd96e395a8d6fa06a3355138331c6"
current_task_contract_hash: "a5735c319402056f3c8552da229c816324a8a4ce56f36e0d781924114d68b40a"
manifest_hash: "V1-M4-CAPABILITY-SEAMS-RUNTIME-INTEGRATION-001-AC31-REBASE / v1.0"

baseline_before:
  repository: "/home/faye/diyu-demo"
  branch: "codex/v1-m4-capability-seams-runtime-integration-001"
  local_commit: "60eccfdf937dd8ab45a1774a001e45149eb5efcb"
  remote_commit: "60eccfdf937dd8ab45a1774a001e45149eb5efcb"
  dify_versions: ["8 个 M4 v1.3 TEST 对象的发布前 workflow_id / graph md5，见 M4_DIFY_PREFLIGHT.json"]

baseline_after:
  repository: "/home/faye/diyu-demo"
  branch: "codex/v1-m4-capability-seams-runtime-integration-001"
  engineering_content_commit: "82d7a9dba988a69dc8f9539efd8def66f884ed85"
  receipt_commit: "ca73a6151b050f32aa835147f7bbcc7cb5641e71"
  note: "工程内容基线为前者；本回执自身落在后者，回执不能自引用自己的提交哈希"
  worktree_clean: true
  dify_versions:
    - "Matrix        d7c2cc11 / wf d52435ac / graph 09de87ed"
    - "Campaign      cfd48281 / wf 18fda0d2 / graph a4983268"
    - "ContentBrief  a3264c95 / wf 23d23c45 / graph 780e15ca"
    - "CreativeScript 8d518554 / wf 244c0768 / graph b3043486"
    - "ProductionDir 57ebc138 / wf 1af7eef0 / graph ddd6241e"
    - "Publishing    10056fcf / wf 42ba7345 / graph 86fb6aa1"
    - "CapabilitySeam de0cb1e9 / wf 9895c761 / graph 4311a375"
    - "FounderCanvas f0b1c5f5 / wf 61c4ce01 / graph 67b717d1"
  provider_version_lag: []

founder_disposition:
  product_semantic_acceptance: "ACCEPTED"
  blind_review_disposition: "ADOPT_EXECUTION_SIDE_CONCLUSION"
  inconclusive_items_disposition: "FOUNDER_ONE_TIME_DEGRADED_ACCEPTANCE"
  technical_results_rewritten: false

ac31_repair:
  highest_damaged_layer: "输出合同没有兜底"
  implementation_summary: >
    三层，全部位于 skill_llm 之后：解析层判定「专业内容已生成但用户块缺失」并给出投影源；
    recovery_llm 做一次有界用户投影（不新增业务事实、不重做专业生产、不整份抄原文、
    不出现内部技术词、不省掉用户必须知道的结论与条件）；delivery_finalize 保证非空，
    并把 DELIVERED / DELIVERED_AFTER_RECOVERY / NOT_DELIVERED 三态分开。
    接缝 completeness_guard 增加 business_delivery_outcome / user_projection_used，
    NOT_DELIVERED 登记组件级 Return；接缝 END 零新增外壳字段。
  exact_replays:
    FA-10: "RB31-R10 / run a6…→新 run；用户正文 603 字；input_sha256 与冻结值相等"
    FA-27: "RB31-R27 / 用户正文 594 字；input_sha256 与冻结值相等"
    FA-32: "RB31-R32 / 用户正文 519 字；input_sha256 与冻结值相等"
  user_delivery_empty_count: "0 / 13 次新运行（修复前同三输入为 3 次空）"
  local_recovery_behavior: >
    最多一次；节点代码级取证覆盖投影成功 / 投影为空 / 投影泄漏三种返回；
    Runtime 级零触发（M4-FND-025，如实登记）。
  business_failure_behavior: >
    投影失败时 delivery_outcome=NOT_DELIVERED，用户仍得到非空自然语言说明，
    且明确「这次不算交付成功」；平台 succeeded 不代表业务交付成功。
  retry_and_idempotency: >
    11 次运行 raw_preserved 1708–10301 字全部保留；子应用 skill_llm 每次恰好 1 次；
    同输入重复提交（G01/G08）产生独立 run_id 且均正常交付。

affected_criteria:
  stale_before_reverification: ["AC-31", "AC-13", "AC-14", "AC-12", "AC-16"]
  reverified: ["AC-31", "AC-13", "AC-14", "AC-12", "AC-16"]
  reused_with_reason:
    - "M4_POST_REVIEW_VERDICTS.json 中其余 26 项：证据载体不依赖 user_delivery 生成路径，且生成层零变化"
  unresolved:
    - "AC-31④ 恢复/重试真实外部副作用场景（继承的既有 NOT_VERIFIED，v1.4 §8 明令不制造）"
    - "AC-31⑤ 判据措辞冲突 M4-FND-013（前序 Reviewer 指定交规划侧裁定）"
    - "RB31-03③ 其余五个能力的必要要素清单未冻结"
    - "M4-FND-024 RB31-05④ 长度阈值判别力"
    - "M4-FND-025 投影路径 Runtime 取证"

six_skill_fidelity:
  source_skill_zero_change: "6/6 sha256 与 v1.4 §7.1 编译观察值相等；Reviewer 独立重算一致"
  runtime_prompt_binding: >
    六份注入 Workflow 的专业正文修复前后逐字节相同（Reviewer 用 git show 独立验证：
    matrix 4bd2a634/16353、campaign 2f103d3d/22892、content_brief 5f77d460/18809、
    creative_script ccd48223/25330、production_director d5ac0e6f/25337、
    publishing_packaging be58fb42/33352）
  model_parameter_binding: "skill_llm 与新增 recovery_llm 使用同一 MODEL 常量，生成器 V5b 硬断言"
  representative_runs: ["RB31-G01..G08 六能力各一条 + Return 路径 + 幂等", "RB31-G09/G10 Canvas 端到端"]

protected_assets:
  six_source_skills: "零改动"
  nine_protected_apps: "零变化（发布前后由目标系统复算，差异 0 项）"
  m1_m2_m3_m5: "零越界变化（git diff 全部落在 M4 范围内）"
  main_branch: "未改变，a7b810109f43a4bf500acc285baab477d96796e3"

review:
  frozen_candidate_commit: "a8ba712c849bde4833c9e6c09606841e4b74eeeb（冻结记录 b80ee4e7）"
  reviewer_count: 1
  reviewer_read_only: true
  blocker_set: ["M4-RB31-R-01", "M4-RB31-R-02", "M4-RB31-R-03", "M4-RB31-R-04"]
  repair_count: 1
  closing_scope: "affected_scope_only —— 只覆盖四个阻断及其直接/传递影响面，零新 Runtime 运行"

technical_acceptance:
  AC31: "NOT_VERIFIED（①②③ PASS；④ 继承的既有 NOT_VERIFIED；⑤ 交规划侧裁定）"
  AC31_conjunct_1_M4_FND_020: "PASS + CURRENT —— 本轮 P0 已修复，经独立 Reviewer 复算"
  RB31: {"01": "PASS", "02": "PASS", "03": "NOT_VERIFIED", "04": "PASS",
         "05": "FAIL", "06": "PASS", "07": "PASS", "08": "PASS"}
  historical_not_verified_preserved: true
  technical_all_31_pass: false

founder_acceptance: "ACCEPTED_WITH_ONE_TIME_DEGRADED_EVIDENCE_ACCEPTANCE"
task_final_status: "BLOCKED"
next_stage_allowed: false
m5_engineering_execution_authorized: false

git:
  branch: "codex/v1-m4-capability-seams-runtime-integration-001"
  engineering_content_commit: "82d7a9dba988a69dc8f9539efd8def66f884ed85"
  receipt_commit: "ca73a6151b050f32aa835147f7bbcc7cb5641e71"
  remote_url: "https://github.com/andyan77/diyu-demo.git"
  remote_commit_matches_local: true
  main_unchanged: true
  pr_created: false

engineering_execution_performed: true
```

`END_MARKER: V1-M4-AC31-REBASE-CLOSING-RECEIPT-v0.1-END`
