# 笛语 V1 M4 最终窄收口 · 收口回执 v0.1

> 权威域：当前状态证据域。本回执不改 WHAT / WHY / BOUNDARY / ACCEPTANCE，不宣布任何合同「已接受」。
> 执行侧不得自行把状态往上推一级。

## 一、先用自然语言回答 Prompt §16 的九问

**1. `end_tool_fail` 是否还能返回空正文？**
不能。修复前 `end_tool_fail` 与 `end_unsupported` 的输出里**根本没有 `user_delivery` 这个字段**，
调用方拿到的必然是空。修复后两者都输出非空正文，并且我把接缝与六个能力子应用的**全部 20 个终止节点**
枚举出来逐一驱动了 27 条返回路径，没有一条能返回空。这条是静态取证，不依赖已被销毁的 Dify 环境，
现在仍然成立。

**2. 受控 Runtime 中是否真实触发了 `recovery_llm`？**
触发了。在隔离故障注入对象里跑，`recovery_llm` 实际执行、每次运行恰好 1 次、`skill_llm` 也恰好 1 次，
业务状态是 `DELIVERED_AFTER_RECOVERY`。另外有一次**完全没有注入**的正常 MATRIX 运行也自然走到了恢复路径。
但这些运行记录随目标系统整库销毁，现在**无法再复核**，所以这条证据被标为失效（`STALE`）。

**3. 恢复成功时用户实际看到了什么？**
一份 444 字的正常中文正文：先说这次要解决的不是衣服不够而是层数和场合没分开，再说写给谁、
承诺是什么、用到哪些事实、有哪些不能说的边界、下一步交给谁。没有内部字段名、状态码、节点名或模型术语。
和内部产出的最长公共子串只占 4.9%，不是把产出整份抄给用户。

**4. 恢复失败时用户实际看到了什么？**
一段非空的自然语言说明：这一次没有成功给出可用的结果；内部判断做出来了但整理成给你看的那一份时出了问题；
**这不算一次成功交付**，别把空白当成没有结论；你可以把同样的需求再提一次。
业务状态记 `NOT_DELIVERED`，不启动第二次恢复，也不重跑专业生产。

**5. 是否重复调用专业 `skill_llm`？**
没有。图上 `skill_llm` 只有一条入边（来自 `projection_record`），恢复节点没有任何回边；
Runtime 记录里每次子应用运行的 `skill_llm` 都恰好 1 次。
有一处需要说清楚：接缝的 tool 节点带一次冻结的基础设施重试，重试会产生第二次子应用运行，
因此「整次调用」的 `skill_llm` 累计为 2。这与我自己写的判据措辞冲突，见第三节 M4-FND-027。

**6. 六份 Skill、专业 Prompt 和模型参数是否变化？**
零变化。六份源 Skill 的 SHA-256 逐一相同；六份注入 Workflow 的专业正文逐字节相同；
六个 `skill_llm` 的 provider、模型名、`max_tokens`、`reasoning_effort`、`thinking`、`top_p` 逐字段相同。
独立 Reviewer 自己重算了一遍，结论一致。每个能力子应用本轮唯一变化的节点是 `delivery_finalize`，
它位于专业生成之后。

**7. 临时故障注入对象是否已清理或隔离？**
**没有按合同清理，也没有按合同隔离——它们随整个 Dify 数据库被销毁了。**
这不是我执行的清理动作，是环境事故 M4-ENV-001 的附带后果。如实记为「被销毁」，不记为「已删除」。

**8. M4 是否达到本 Prompt 的 DONE？**
**没有。终态是 `BLOCKED`。**
两条判据在冻结判据下实打实没过（CL31-03、CL31-04），两条无法核验（CL31-02、CL31-05），
两条因目标系统销毁而不成立（CL31-07、CL31-08）。

**9. 是否只开放 M5 交接、没有启动 M5？**
M5 **既没有启动，也没有取得交接资格**。`next_stage_allowed = false`。

## 二、这一轮真正抓到的东西

`recovery_llm` 在 v1.4 的 13 次 Runtime 运行中触发 0 次，所以它带的缺陷一直看不见。
这一轮把它逼出来跑，第一次运行就暴露了 **M4-FND-029**：

> 恢复路径没有剥离模型的 thinking 段，`<think>` 里的整段内部推理被当成用户正文交付出去。
> 用户会看到「不能出现『记录』这类内部词」「不抄原文，不新增事实，直接开始写」这类模型自述。

专业链的 `final_extract` 一直在做这个剥离，v1.4 新增的恢复路径漏了。已修复（`_strip_thinking`
+ 泄漏词表补入 `<think>`/`</think>` + 生成器 V5e 硬断言），六个能力子应用同步生效，
重跑后用户正文从 1062 字降到 444 字，`<think>` 命中 1 → 0。

**这是本轮最有价值的产出**：一个躲过了 13 次运行的用户可见缺陷被真实取证抓住并修掉了。

## 三、我这一轮做错的事

1. **我把一条同型缺陷写进了消灭它的合同里。** 本轮 P0-D 就是「以有效保真量尺替换无判别力的长度阈值」，
   我在 CL31-05 里确实替换掉了旧的 `RB31-05④`，却在 `CL31-03⑥` 里**重新写了一条 80% 长度阈值**。
   对 468 字的短 artifact，任何可读的自然语言投影都难以低于 374 字。P0-D 未达成。（M4-FND-030）
2. **必保内容判据用精确子串匹配中文自由文本。** 我冻的是「层数**与**场合」，模型写的是「层数**和**场合」，
   还插了引号 → 假阴性。正文里核心结论实际出现了两次。（M4-FND-031）
3. **事实回查提取器几乎没有判别力。** 只有数字正则、写死的时间词表和 17 个硬编码实体词；
   Reviewer 用只含虚构专名不含数字的文本实测得空结果。我原来据此判的 PASS 已降为 `NOT_VERIFIED`。（M4-FND-033）
4. **我既升级给规划侧、又替规划侧把结论填成了 PASS。** CL31-02⑤ 我按「Prompt 原文」判 PASS，
   但我自己冻结的任务合同里 `ACCEPTANCE.oracle_ref` 明写指向 v0.5——v0.5 就是被合同指定的冻结 Oracle。
   我的免责论证被我自己冻结的合同推翻。已改判 `NOT_VERIFIED`。（M4-FND-027）
5. **证据收集器静默丢行。** 分隔符切分遇到含换行的 `error` 字段会错位，首行错位时整批被丢且不报错，
   INJ-01 的两条子运行一度被误报为 0。（M4-FND-028）
6. **CL31-02⑥ 的取证是短路。** 判定器只断言运行次数上限，并把重试配置写成硬编码字符串塞进证据，
   没有验证第二次运行确实是平台重试。

第 1、2、3、6 条都是同一类毛病：**判定器写得比判据松或比判据脆，看起来全绿其实没验到东西。**
这一轮能收住，主要是独立 Reviewer 拦下来的。

## 四、环境事故 M4-ENV-001

冻结候选提交在 `2026-08-27T21:11:25Z`。约 27 分钟后：

```
21:38:31 UTC  database system is shut down
              The files belonging to this database system will be owned by user "postgres"
              initdb …
21:39:54 UTC  ready to accept connections     ← 全新空集群
```

`setup={"step":"not_started"}`；`apps / workflows / workflow_runs / accounts / tenants` 全部为 0；
`pgdata` mtime = 21:38 UTC；卷目录下无任何备份。全部 Dify 容器同时重启。

**成因不作归属。** 本执行会话对 Dify 只发出过 `SELECT`、Console 登录、`import_dsl`、`publish`
与 workflow tool 注册，没有任何 `down -v` / `rm` / `dropdb` / `initdb`；但执行侧无法证明成因。

**后果**：九个受保护应用不复存在，无法核验零变化也无权重建；全部 Runtime 证据无法复核；
两个注入对象被销毁；`CL31-08②` 结构上已不可能满足。按 A3，依赖目标系统的判定全部标 `STALE`。

**需要 Founder 决定**：重建 Dify 环境重取 `CL31-02/03/04/05⑧⑨/07/08`，还是就按 `BLOCKED` 收口。
执行侧不替 Founder 定，也不自行重建。

## 五、结构化回执

```yaml
task_id: "V1-M4-CAPABILITY-SEAMS-RUNTIME-INTEGRATION-001"
task_entry_mode: "REBASE_TASK"

previous_task_contract_hash: "a5735c319402056f3c8552da229c816324a8a4ce56f36e0d781924114d68b40a"
current_task_contract_hash: "8d73b4f157883eb422e6ae17ececcf87a64d98c6a51f35537b8446155fa85070"
manifest_hash: "8d73b4f157883eb422e6ae17ececcf87a64d98c6a51f35537b8446155fa85070"

baseline_before:
  local_commit: "c7682a2e045ae4c3df5cebeb840e5b480af44748"
  remote_commit: "c7682a2e045ae4c3df5cebeb840e5b480af44748"
  remote_main: "a7b810109f43a4bf500acc285baab477d96796e3"
  worktree: "CLEAN"
  dify_bindings:
    - "CAPABILITY_SEAM wf=9895c761 graph=bd37ac73d0d6…"
    - "CONTENT_BRIEF   wf=23d23c45 graph=be8c9b7b3e4c…"
    - "MATRIX          wf=d52435ac graph=807bdb5166e8…"
    - "CAMPAIGN        wf=18fda0d2 graph=1d5ae1e9addf…"
    - "CREATIVE_SCRIPT wf=244c0768 graph=ca9fc920087f…"
    - "PRODUCTION_DIRECTOR  wf=1af7eef0 graph=8fe3596b33c0…"
    - "PUBLISHING_PACKAGING wf=42ba7345 graph=515f10bb0e39…"
    - "FOUNDER_CANVAS  wf=61c4ce01 graph=27f6aa48fce0…"
  note: "以上绑定已随 M4-ENV-001 销毁，不可复核"

baseline_after:
  engineering_commit: "3bf324ec616a80f669e9764bf5dfc4f77f22c5b5"
  receipt_commit: "EXECUTOR_FILLS_AFTER_COMMIT"
  remote_commit: "EXECUTOR_FILLS_AFTER_PUSH"
  remote_main: "a7b810109f43a4bf500acc285baab477d96796e3"
  worktree_clean: true
  dify_bindings: []
  dify_bindings_note: "目标系统已被整库重建，现无任何应用（M4-ENV-001）"

successor_contract:
  ref: "decision-chain/docs/V1_M4_EVIDENCE_COLLECTION_CONTRACT_v0.5.md"
  hash: "5c45e8c732c8b88913ea423641f5f00efb5ce8adfb250cec9906e5723bce2c6f"
  frozen_before_run: true
  frozen_at_commit: "9122fbbee6b60a9998f232202d00d941b7218ea2"
  superseded_clauses:
    - "M4-RB31-03③ 的跨六能力必要要素判据"
    - "M4-RB31-05④ 的单次 artifact 长度 80% 判据"
  historical_results_preserved: true

end_tool_fail:
  runtime_run_id: "见 CL31_RUNTIME_RAW.json（目标系统已销毁，不可复核）"
  user_delivery_length: 200
  user_delivery_excerpt: "这一次没有把结果做出来。「内容任务判断」这一步在运行中没有跑通…**这不算一次成功交付**"
  business_delivery_outcome: "NOT_DELIVERED"
  returns_ref: "组件级 Return 七项字段齐全，1 条"
  flag: "STALE"

recovery_runtime:
  evaluation_app_ids:
    - "c733f426-6e54-4c09-8ad7-8192b426ac38"
    - "86ba24e1-ae01-4b29-af04-fbeffc499bb3"
  injected_input_hash: "三条注入输入 input_sha256 在 Attempt 1 与 Attempt 2 之间逐条相等"
  final_subgraph_hash: "returns_adapter 122fc8d5… / projection_gate bef4ddf2… / recovery_llm 04b990e3… / delivery_finalize 02453101… / binding_record 722a35df… / end_ok 2439b1ff…（修复前快照）"
  evaluation_subgraph_hash: "与最终候选逐节点相等，Reviewer 独立复算确认"
  subgraphs_equivalent: true
  runtime_run_ids: "见 CL31_RUNTIME_RAW.json / CL31_RUNTIME_RAW_A1.json"
  recovery_llm_execution_count: 1
  skill_llm_execution_count: 1
  user_delivery_length: 444
  user_delivery_excerpt: "这条内容要解决的，不是“衣服不够”的问题，而是“层数和场合没有分开”的问题。"
  unsupported_fact_count: "0（但提取器判别力不足，该项已降为 NOT_VERIFIED）"
  internal_leak_count: 0
  whole_artifact_copy: false
  lcs_ratio: 0.0491
  len_ratio: 0.9487
  original_failure_preserved: true
  flag: "STALE"

recovery_failure:
  user_delivery_length: "非空（离线全分支驱动验证）"
  business_delivery_outcome: "NOT_DELIVERED"
  second_recovery_triggered: false

six_skill_fidelity:
  source_skill_zero_change: true
  professional_prompt_zero_change: true
  model_parameter_zero_change: true
  professional_rerun_caused_by_recovery: false
  independently_verified_by_reviewer: true

affected_acceptance:
  M4_CL31_01: "PASS（④带限定）"
  M4_CL31_02: "NOT_VERIFIED (INCONCLUSIVE) · STALE"
  M4_CL31_03: "FAIL · STALE"
  M4_CL31_04: "FAIL · STALE"
  M4_CL31_05: "NOT_VERIFIED · STALE"
  M4_CL31_06: "PASS · CURRENT"
  M4_CL31_07: "FAIL · STALE"
  M4_CL31_08: "FAIL"

historical_results:
  AC31_④: "NOT_VERIFIED"
  historical_AC31_⑤: "NOT_VERIFIED"
  RB31_03_v0_4: "NOT_VERIFIED"
  RB31_05_v0_4: "FAIL"
  rewritten: false

founder_disposition:
  product_acceptance: "ACCEPTED"
  degraded_risk_acceptance: "ACCEPTED"
  additional_founder_judgment_requested: true
  what_is_requested: "只有一件：重建 Dify 环境重取证，还是按 BLOCKED 收口。不请求技术方案裁决。"

review:
  candidate_commit: "3bf324ec616a80f669e9764bf5dfc4f77f22c5b5"
  reviewer_count: 1
  reviewer_read_only: true
  first_attempt_interrupted_no_conclusion: true
  blockers:
    - "BLK-1 M4-CL31-03（⑥⑧）未达冻结判据"
    - "BLK-2 M4-CL31-04① 必保内容缺失"
    - "BLK-3 目标系统数据完整性（M4-ENV-001）"
    - "BLK-4 M4-CL31-08 ⑤⑨ 收口未完成"
  blockers_accepted: 4
  repair_count: 1
  closing_scope: "affected_scope_only"

protected_assets:
  six_skills: "零变化（仓库内哈希，Reviewer 独立复算）"
  nine_apps: "取证当时零变化；现已随 M4-ENV-001 不存在，当前无法核验"
  m1_m2_m3_m5: "零越界变化（35 个变更文件全部落在 M4 授权范围）"
  main: "未改变"

temporary_dify_objects:
  created:
    - "c733f426-6e54-4c09-8ad7-8192b426ac38"
    - "86ba24e1-ae01-4b29-af04-fbeffc499bb3"
  deleted: []
  retained_unpublished_not_routable: []
  destroyed_by_environment_incident:
    - "c733f426-6e54-4c09-8ad7-8192b426ac38"
    - "86ba24e1-ae01-4b29-af04-fbeffc499bb3"

task_final_status: "BLOCKED"
next_stage_allowed: false
next_stage_scope: "NONE"
m5_engineering_execution_authorized: false
technical_all_31_pass: false
historical_technical_results_preserved: true
partial_used: false

git:
  branch: "codex/v1-m4-capability-seams-runtime-integration-001"
  local_commit: "EXECUTOR_FILLS_AFTER_COMMIT"
  remote_commit: "EXECUTOR_FILLS_AFTER_PUSH"
  remote_matches_local: "EXECUTOR_FILLS_AFTER_PUSH"
  main_unchanged: true
  pr_created: false

engineering_execution_performed: true
```

## 六、交规划侧裁定的事项（执行侧无权自决）

| 编号 | 事项 |
|---|---|
| M4-FND-027 | `CL31-02⑤` 与⑥在发生基础设施重试时互斥，冻结 Oracle 内部自相矛盾 |
| M4-FND-030 | `CL31-03⑥` 的 80% 长度半边与本轮受命替换的 `RB31-05④` 同型无判别力，对短 artifact 不可满足 |
| M4-FND-031 | `CL31-04` 必保内容用精确子串匹配中文自由文本，同义改写与标点插入即假阴性 |
| M4-FND-033 | 事实回查提取器对专有名词、商品名、地点召回接近零 |
| M4-FND-032 | 部分能力的用户可见正文以 `status: READY_WITH_CONDITIONS` 开头，内部状态词外露；来自专业产出格式（受保护资产），本轮无权改 |
| M4-ENV-001 | Dify 目标系统被整库重建，重取证与否需要授权 |

`END_MARKER: V1-M4-FINAL-CLOSURE-RECEIPT-v0.1-END`
