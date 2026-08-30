# FAILURE TRIAGE 004｜规范任务状态载体（Phase A 零模型根因复核）

- `task_id`: `DIYU-V1-UNIFIED-DIFY-APPLICATION-001`
- 授权：CONTINUE EXECUTION PROMPT v1.0（规范任务状态载体与真实 CS→PD→PP 连续链根修复）
- 阶段：Phase A，**模型调用 0，Dify 写入 0**
- 判据与证据：`unified-app/evidence/stages/s4_canonical_state/S4_PHASE_A_ROOT_CAUSE_RECHECK.json`
- 复核脚本：`unified-app/workflows/S4_PHASE_A_ROOT_CAUSE_RECHECK_v1.0.py`
- 结果：**A-01…A-09 全部 PASS（9/9）**，九条现场事实与规划侧描述一致，允许进入 Phase B

## observed_failure

上一轮受影响连续链 FAIL 13/17。表面症状三条：PD 停在 `production_profile` 未产出；
`goal_family` 反复成为缺口；PP 产出 9031 字却不是 PD 的下游。

## frozen_target

TD-UAPP-20 的工程编译：跨轮已确认字段不被抽空、不被改写、不重复询问。
上一轮的载体只做到「不擦除」，没有做到「字段有身份、有来源、有作用域、有可信等级」。

## confirmed_origin

**最高失效节点 = `uapp_fields` 载体的字段模型本身**，不是 Hop、不是六能力、不是 Checker。
载体把「一行文本」当字段，因此同时缺四样东西：身份、来源、作用域、可信等级。
九条复核逐条落实：

| # | 事实 | 证据 |
|---|---|---|
| A-01 | T6 的 PP 上游是 **CREATIVE_SCRIPT**，不是 PD | T5 后 `uapp_last_capability`=CREATIVE_SCRIPT、`uapp_last_artifact` 仍是 6843 字 CS；T5 seam artifact 长度 0；T6 外壳 `content_body_or_beats` 以「# Creative Script 完整产出」开头。9031 字 PP 属 **PRE 短入口**，不是完整 PD→PP 血缘 |
| A-02 | 字段靠文本正则识别，无规范字段表 | `FIELD_LINE = re.compile(r"^(\s*)`([A-Za-z_][A-Za-z0-9_]*)`\s*:\s*(.*)$")`；源码中无 `FIELD_SPECS` / `canonical_id` |
| A-03 | E 级（模型抽取）字段能补后续轮次缺口 | T3 用 t1 的 E 级 `primary_goal` 补缺口；T5 用 t1 的 E 级 `time_window` 补缺口；T4 用 t3 的 `expression_subject`；T6 用 t2 的 `cta_contract` |
| A-04 | 缺失占位符被当成真实值 | `primary_goal` = 「（已登记来源中未明确写出）」，t1 入载体、t1–t5 一直在，且在 T3 被当作真值补进 CREATIVE_SCRIPT 外壳 |
| A-05 | 别名没有规范身份 | `objective.primary_goal` 被 `rsplit(".",1)` 削成 `primary_goal`（启发式，不是登记）；`goal_family` 在外壳里是**非反引号**写法（T2 出现），载体六轮从未收录，T1/T3/T4 一直是缺口；`expression_subject` 与 `expression_subject_and_boundary` 作为两个独立槽位并存 |
| A-06 | 运营周期时间窗直接当生产时间窗 | 载体 `time_window` = 「四周内」（来自夹具「当前经营任务……四周内目标」，t1 E 级），在 T5 `PRODUCTION_DIRECTOR` 被补进 `time_window` 缺口。没有任何作用域区分 |
| A-07 | 用户主动纠正未被询问的字段时旧值覆盖新值 | 用 T5 后的真实载体 + 当前线上源码确定性重放：新值「改口：这条只讲怎么判断……」被丢弃，外壳与载体都保留旧值，`held_fields=content_promise`，`stale_downstream` 为空 |
| A-08 | `stale_downstream` 无下游消费者 | 已发布候选图中只有 `uapp_fields` 一个节点出现该串；没有任何变量赋值、条件分支或下游入参引用它 ⇒ 它不能阻止旧 artifact 继续下传 |
| A-09 | PD 合同确实要求追问 | 运行合同逐字命中四处：「\| `production_profile` \| Production Profile \| 询问 \|」「在真实生产运行开始前必须由人给出」「在**工作流无人可问**时才允许使用」「生产运行不得把这些默认值当成上游已确认输入」 |

## candidate_sources 与排除

- `SYSTEM_UNDER_TEST` — **成立**。载体字段模型缺身份/来源/作用域/等级，A-02…A-08 全部落在这一个节点上。
- `CONTRACT_OR_INTENT` — 部分成立但**已由本次 Prompt 解决**：上一轮冻结场景没人提供 `production_profile`，PD 追问是合同正确行为（A-09）。新场景 T5→T6 已补上这一问一答。
- `ORACLE_OR_CRITERION` — 上一轮 N-05 判据把「保留」判在「键出现在每个能力外壳里」，这次改判在载体与是否重复询问（B3/B4）。
- `CHECKER_OR_FIXTURE` — 上一轮 N-15 负控制选轮错误，这次负控制必须选真实跨轮携带的轮次。
- `INPUT_ENVIRONMENT_OR_TOOL`、`INSUFFICIENT_EVIDENCE` — 排除：九条全部由已有原始 `node_detail` 与只读 select 复算得到，零新增调用。

## mutation_target（本轮允许修改的最小对象）

统一候选画布的任务字段载体（`uapp_fields`）与其直接对应的持久化/接受闸门；
新版判据、输入、证据与只追加账本；确定性验证器。

## protected_targets（尚未证明有错，不得修改）

M1、M2、最终 FP M3、Hop 目标应用与已钉 provider、最终 FP Seam、
六个专业能力应用及其 Skill/Prompt/模型参数、旧 Gate 旧输入旧结果旧 FAIL 证据、main。

## next_reverification

Phase B 先冻结新版判据与输入并提交；Phase C 一次根修复 + 全套零模型正负控制；
Phase D 唯一一次七轮真实连续会话。

## 附：本次复核自身暴露的一个检查器细节

A-04 的占位符正则是**子串搜索**，因此在 `script_or_equivalent_beats` 这种整篇 artifact 字段上
命中了正文里的 `UNDECLARED` 一词，属误报。它不影响 A-04 的成立（`primary_goal` 是真占位符），
但直接约束 Phase C 的实现：**缺失语义判定必须是整值匹配，不能是子串搜索**，否则会把
正文里提到 UNDECLARED 的合法长文本误判为缺失。
