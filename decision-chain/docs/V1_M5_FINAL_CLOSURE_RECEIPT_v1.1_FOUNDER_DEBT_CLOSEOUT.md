# M5 最终收口回执 v1.1 · Founder 接受技术债

- `task_id`: `DIYU-V1-M5-UNIFIED-INTEGRATION-FINAL-ACCEPTANCE-001`
- `entry_mode`: `REBASE_TASK`（同一 `task_id`，未新建、未重置失败历史）
- 收口合同：`M5_ENGINEERING_TASK_CONTRACT_v1.2_FOUNDER_TECHNICAL_DEBT_CLOSEOUT.yaml`
  sha256 `35ccf590…de9df0e`
- 收口 Prompt：`M5_FOUNDER_ACCEPTED_TECHNICAL_DEBT_FINAL_CLOSEOUT_EXECUTION_PROMPT_v1.0.md`
  sha256 `e384df3d…49397cc`
- **不覆盖** `V1_M5_FINAL_CLOSURE_RECEIPT_v1.0.md` 与其历史段。

---

## 一、技术结果（只写证据支持的，不写裁决）

### 1.1 本轮修复的三处目标行为

| 目标行为 | 结果 | 证据 |
|---|---|---|
| 撤回影响面不得自动延伸到已发布内容 | 不复现 | `HOLDOUT_RB_RUNS_fp1.json`；现场查库 `invalidated_at IS NULL` 且系统未声称已写入 |
| 缺关键输入时停在缺口、不自选商品 | 不复现 | 同上，变体 N `delivered=false`，全文 SKU 0 处、价格 0 处 |
| 交付层不得改写上游判断、不得泄漏状态词 | 不复现 | `HOLDOUT_RUNS_fp1.json`：`status: READY` 0、状态词 0、「整轮／重跑／从头」0 |

### 1.2 正负判别力

| 项 | 结果 | 证据 |
|---|---|---|
| 正向等价表达（三形式 + 引号形式） | 四格全部真实交付，产物 3150–4695 字 | `RISK_PROBE_SUITE_riskfp1.json` |
| 负控制（同一引号形式，抽掉 `audience_problem`） | `UNKNOWN`／`component_return=true`／`artifact=0`；`precise_gap` 精确等于 `audience_problem`；`parse_status: OK` | `R4_NEGATIVE_CONTROL_RUN.json`，`run_id eb2364a5-e740-4679-ad07-02909663965c` |

判据与预期在调用之前冻结（`V1_M5_R4_NEGATIVE_CONTROL_FROZEN_SPEC_v1.0.md`
sha256 `d62ad5d0…c37091c9`，提交 `47dfa4c` 早于调用；运行器启动时现场复算哈希）。
授权 1 次，实跑 1 次，无重试，无重复采样。

### 1.3 未被误挡与保护面

| 项 | 结果 | 证据 |
|---|---|---|
| 正常主路径 | 四能力全交付、零泄漏、发布反馈幂等成立 | `FULL_STORY_RUN_full01fp1.json` |
| 确定性测试 | 11／11，含负控制与假阳性控制 | `FINAL_P0_DETERMINISTIC_TESTS.json` |
| `rb` / `legacy` 与候选 graph | 零漂移 | 同上 T4／T5；收口只读刷新 8/8 一致 |

### 1.4 仍未验证的（不得说全绿）

`M5-AC-03` `STALE`｜`M5-AC-04` `STALE`｜`M5-AC-05` `NOT_VERIFIED`｜
`M5-AC-06` `NOT_VERIFIED`｜`M5-AC-07` `NOT_VERIFIED`｜`M5-AC-08` `STALE`。

`applicable_p0_failures = 0`。

---

## 二、Founder disposition（产品裁决，不是技术 `PASS`）

```yaml
founder_adjudication_id: M5-FOUNDER-ADJUDICATION-003
founder_product_acceptance: PASS/CURRENT
acceptance_type: ACCEPTED_WITH_DISCLOSED_TECHNICAL_DEBT
all_original_m5_ac_pass: false
```

Founder 原话：「我认为两项P0收口后，暂时忽略剩余问题项，作为技术债登记，推进M5后续收口」。

**它改变的是这些项对 v1.2 收口公式的阻断资格，不是它们自己的技术结果或证据时效。**
详见 `V1_M5_FOUNDER_ADJUDICATION_003_TECHNICAL_DEBT_CLOSEOUT.md`。

前置裁决：001（`H01-A3 = PASS`，关闭两项原 P0）、002（`RISK-M4-030+031` 权威判据归属）。

---

## 三、技术债（8 项，主表唯一）

主表：`V1_M5_ACCEPTED_TECHNICAL_DEBT_REGISTER_v1.0.md`（全仓唯一一份，其余文档只引用）。

| id | 内容 | 原结果 / 时效 |
|---|---|---|
| `TD-M5-01` | 四项非 P0 语义人判未决（含 `H01-A1` 影响面少算，两次稳定复现） | `NOT_VERIFIED` / `PENDING_HUMAN` |
| `TD-M5-02` | 十类短入口未在当前候选复验（"无依赖项可复用"经核对为空集） | `STALE` |
| `TD-M5-03` | 十九维两维时效缺口；十七维 `CURRENT` 是"有代表性"非"全覆盖" | `STALE` |
| `TD-M5-04` | 独立 A/B 盲评未做，且盲评在本仓库内不成立、需隔离交付 | `NOT_VERIFIED` |
| `TD-M5-05` | `M5-AC-07` 因四项非 P0 人判未决而不得 `PASS` | `NOT_VERIFIED` |
| `TD-M5-06` | `REG-M3-01` 未在改后的 M3 successor 上重跑 | `STALE` |
| `TD-M5-07` | 冻结十九维映射把「质量」维绑到不存在的用例 id | `KNOWN_DEFECT` |
| `TD-M5-08` | 检查器枚举过严；负控制运行器 `returns_json` 取值路径错 | `KNOWN_DEFECT` |

`open_debt_items_p0: 0`。重开触发条件见主表 `reopening_triggers`。

---

## 四、Git 事实

> 本节按事件顺序追加。**push 尚未发生时不写成已发生。**

```yaml
repository: /home/faye/diyu-demo
worktree: /home/faye/diyu-demo-worktrees/m5-unified-integration-final-acceptance-v1
branch: codex/v1-m5-unified-integration-final-acceptance-001
head_at_activation: 76a1ff80942aa322afa0b7caa620043e5ecc5188
origin_main_at_activation: f6eb86c076c47bd9f7c9323caac6c0ba1fc5098e
origin_branch_at_activation: 9bf57246834a30f99f7a45abeea82ee5471a6fe8
candidate_commit: 5f84d94d542693f143faab0444525618ab21a4e9
diff_vs_origin_main: {added: 592, modified: 2, deleted: 0}
modified_paths_are_append_only: true      # 两份共享账本，删除行 0
live_main_untracked_files: 10
live_main_untracked_collision_with_merge_paths: 0
enclosing_receipt_commit: SELF_RESOLVED_BY_GIT
task_branch_push: DONE
main_closeout: DONE
remote_verification: DONE
```

---

## 五、Dify 绑定

收口前一次**只读**刷新（v1.2 授权 `AUTHORIZED_ONCE`）：

```yaml
apps_checked: 8
graph_md5_match: 8/8
node_count_match: 8/8
llm_models_match: 8/8
drift: none
workflow_or_model_calls: 0
evidence: decision-chain/evidence/m5-final-p0/CLOSEOUT_READONLY_BINDING_REFRESH.json
```

候选自 `5f84d94d…` 冻结以来**无未授权运行时变化**。

---

## 六、外部副作用

```yaml
new_model_calls_this_closeout: 0
new_workflow_runs_this_closeout: 0
real_external_publish: NONE
non_test_data_mutation: NONE
dify_app_deleted: NONE
remote_branch_deleted: NONE
force_push: NONE
sealed_ab_mapping_opened: NONE
live_main_untracked_files_touched: NONE
```

本轮唯一一次真实模型调用发生在**收口之前**的定向负控制（`run_id eb2364a5…`），
由 Founder 裁决 002 §四单独授权，已计入 §1.2。收口阶段本身零调用。

---

## 七、非承诺（禁止外推）

- M5 `DONE` 只表示 **v1.2 收口合同**完成，**不**表示父合同的原始全绿公式成立；
- **不**表示 `ALL_ORIGINAL_M5_AC_PASS`；
- **不**表示 `PRODUCTION_READY`；
- **不**表示 `REAL_OPERATION_LOOP_VERIFIED`；
- **不**表示 `OPERATIONAL_UPLIFT_PROVEN`；
- 测试／模拟发布**不**等于真实发布（本轮所有发布与反馈 `is_test = true`、`is_simulated = true`）；
- 技术集成可用**不**等于真实运营闭环或经营提升；
- 技术债被接受**不**等于技术债不重要——其后续处理必须由新的优先级与任务授权触发。

---

## 八、终态

> 按 `stop_rule`，`DONE` 公式首次成立后立即停止。本节在 Git／远端收口真实完成后追加。

```yaml
task_progress: COMPLETED
terminal_state: DONE
delivery_disposition: ACCEPTED_WITH_DISCLOSED_TECHNICAL_DEBT
all_original_m5_ac_pass: false
applicable_p0_failures: 0
next_stage_default: false
```

---

## 九、Git／远端收口实际发生的事实（事件之后追加）

```yaml
closeout_commit: bc660498af24afe1cc3e800459246cc1f954003b
task_branch_push:
  ref: refs/heads/codex/v1-m5-unified-integration-final-acceptance-001
  before: 9bf57246834a30f99f7a45abeea82ee5471a6fe8
  after: bc660498af24afe1cc3e800459246cc1f954003b
  method: fast-forward, non-force
main_closeout:
  ref: refs/heads/main
  before: f6eb86c076c47bd9f7c9323caac6c0ba1fc5098e
  after: bc660498af24afe1cc3e800459246cc1f954003b
  method: git merge --ff-only, then non-force push
remote_verification:
  method: git ls-remote + git fetch
  origin_main: bc660498af24afe1cc3e800459246cc1f954003b
  origin_task_branch: bc660498af24afe1cc3e800459246cc1f954003b
  local_main: bc660498af24afe1cc3e800459246cc1f954003b
  three_way_identical: true
live_main_untracked_files_after: 10
live_main_tracked_dirty_after: none
force_push: NONE
enclosing_receipt_commit: SELF_RESOLVED_BY_GIT
```

本节全部为**已发生并经 `ls-remote` / `fetch` 复核**的事实，无预填。
本文件自身的后继提交哈希由 Git 解析，实际 40 位提交在终端最终回报中给出。

## 十、`CLOSE-AC-07`

```yaml
CLOSE-AC-07:
  pass: true
  evidence: 任务分支非 force fast-forward push；main 以 --ff-only 收口后非 force push；
            origin/main 与本地 main、任务分支三方一致；Final Receipt 与 COMPLETION CHECK 已落盘
```

`done_formula_v1_2` 首次成立。

## 十一、COMPLETION CHECK

```yaml
real_behavior_verified:
  - 两项原 P0 在旧例重跑与新鲜留出中均已关闭（applicable_p0_failures = 0）
  - R4 同一带引号形式：正例四格真实交付（3150–4695 字），负例精确阻断（artifact 0，precise_gap = audience_problem）
  - R5 正常主路径四能力全交付、零泄漏、幂等成立，未被最小修复误挡
validator_discrimination_verified:
  - R4 单次冻结负控制 PASS；判据与输入冻结提交 47dfa4c 早于调用
  - R6 11/11 含负控制（旧检查器漏检）与假阳性控制（干净正文零命中）
core_problem_solved:
  - 当前候选达到 v1.2 的可用技术集成交付目标
  - 原始 M5 全绿目标未宣称成立；all_original_m5_ac_pass = false
protected_targets_unchanged_or_authorized:
  - 候选 8 应用 graph/node/model 零漂移（只读刷新 8/8）
  - live main 十个未跟踪文件零触碰；与 594 条待合并路径交集 0
  - 相对 origin/main 592 新增 / 2 修改 / 0 删除，两处修改均为账本只追加
evidence_refs:
  - 逐项文件 sha256 见证据索引 v1.2
  - Dify 绑定：CLOSEOUT_READONLY_BINDING_REFRESH.json（drift none）
  - 负控制 run_id: eb2364a5-e740-4679-ad07-02909663965c
  - Git: bc660498af24afe1cc3e800459246cc1f954003b（分支 = main = origin/main）
unnecessary_complexity_remaining:
  - 本任务不再增加测试轮、人判、盲评、检查器修复或治理文档
  - 技术债 8 项已登记，后续只能由新任务/新授权打开
```
