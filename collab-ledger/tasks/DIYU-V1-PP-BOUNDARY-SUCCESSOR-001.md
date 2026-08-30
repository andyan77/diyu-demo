# `DIYU-V1-PP-BOUNDARY-SUCCESSOR-001` · 共享 PP 交付边界后继

- `parent_task_id`: `DIYU-V1-UNIFIED-DIFY-APPLICATION-001`
- `task_mode`: `NEW_SUCCESSOR_TASK`
- `constitution`: `UNIVERSAL-BOUNDED-EVIDENCE-AI-COLLABORATION v0.3.1-kernel revision 2`
- 授权：FOUNDER ADJUDICATION + EXECUTION PROMPT v1.0

---

## ATT-PPBS-01 · 第一次实施与验证（2026-08-30）

### 终态

```yaml
D1: FAIL          # D1-c CTA 边界
D2: NOT_STARTED   # D1 FAIL 后按停止规则不执行
D3: NOT_STARTED
PP_BOUNDARY_SUCCESSOR:   NOT_VERIFIED
V-08B_FACT_TRACEABILITY: NOT_VERIFIED   # D1-b 单点 PASS，但 D1 整体未通过，不上调
V-08C_CTA_FIDELITY:      FAIL
task_progress: IN_PROGRESS
terminal_state: UNSET
next_state: CHECKPOINT
```

保持不变（与 D1 结果无关）：

```yaml
CROSS_TURN_CORRECTION_PROPAGATION: NOT_VERIFIED(NOT_CHECKED)
S4_OVERALL_ACCEPTANCE: NOT_VERIFIED
S5: NOT_STARTED
main_merge: NOT_ALLOWED
```

### Phase A（零模型）

现场复算与规划侧观测逐项一致：HEAD `2d70de0`、`origin/main` `01a42b0`、
PP graph md5 `788c8555…`、provider 钉 `2026-08-29 03:34:58.999575`、
Seam md5 `db49a3da…`、候选图 md5 `99c3edf7…`、`hop_pin 2026-08-30 03:38:31.449618`，worktree clean。
线上 PP system prompt 字节可回指：= 仓库 M4 SKILL.md(30541) + 固定注入尾(123)。

**PP md5 绑定处实测 10 个**（上一任务报告里写的 7 个偏少：漏算
`S4_PHASE_C_BINDING_v1.0.json`，另两处是那之后才产生的文件）。

Founder 三项裁决落盘 `PPBS_FOUNDER_ADJUDICATION_v1.0.md`（`32ae33c9…`）；
D1/D2/D3 输入与判据在**任何模型调用与任何实现改动之前**冻结并提交（commit `33318ff`）。

### Phase B（一次最小修复）

后继 Skill `content-production/skills/packaging-content-for-release-m4-b1/SKILL.md`：
继承体**逐字节等同** M4 源，新增 4 块共 4055 字——
「事实来源必须蕴含该主张」、「CTA 权威顺序」、「无 CTA 评论区」前置条件句、自检 15/16。
零案例专用字符串（构建过程中删掉了一处误写入的旧违规原句「低风险互动范畴」，改为通用表述）。

PP app `c9cdea24` 只改 `skill_llm.system`；节点集、边集、其余节点逐字节不变；
注入尾巴逐字沿用旧版；发布新版本 `2026-08-30 09:05:41.729617`，
graph md5 `788c8555…` → `7940dc00…`，旧 workflow 行保留（共 3 行）。
**provider 钉全程未动**，Seam / M5 FP / 统一画布在整个 Phase D 期间调用的仍是旧 PP。

### Phase C（确定性验证 9/9）

C-01 字节可回指、C-02 除 `skill_llm.system` 外零变化、C-03 其余八应用与候选图零漂移、
C-04A 新增文本零案例专用串、C-04B 继承体逐字等同源、
C-05/C-06 单点变异（删掉任一规则块 ⇒ 对应规则装载控制翻 FAIL，且互不影响）、
C-07 provider 仍指旧版、C-08 判据与输入哈希早于任何模型结果。

Gate 在实现之前版本化为 v1.1，把 C-04 拆成 C-04A/C-04B——
源 Skill 本来就带两处 `BRF-SUHE-001-XXX` 编号格式示例，后继版按裁决 1 必然逐字继承，
整文件扫描会把它误判成本轮引入。**不放宽业务含义**，新增文本仍零容忍。v1.0 原样保留。

### Phase D · D1 = FAIL

run `53b90396-eb9a-47ab-8250-92cf117df814`，succeeded，60.14s，attempts=1，
输入五项 sha256 与冻结件全等，LLM 节点 `skill_llm` × 1。

| | 结果 |
|---|---|
| D1-a 完整可用交付 | PASS（artifact 9732 / user_delivery 1674） |
| **D1-b 事实主张可回指** | **PASS** |
| **D1-c CTA 边界** | **FAIL** |
| D1-d 不空交付、不整项拒绝 | PASS |
| D1-e `used_fact_refs` | PASS |

**事实边界确实修好了。** 十个历史行为探针（`一直在用`/`常用`/`长期以来`/`十年`/`历来`/
`向来`/`一贯`/`多年来`/`一直以来`/`从来都`）在 artifact 与 user_delivery 中命中 **0 次**；
旧版同场景写的「教顾客挑衣服时一直在用这套『三问』」＋推断脚注，本次不存在。

**CTA 边界没修好。** 产出仍有：`cta_surface` 逐字引用 `cta_contract` 原文后，
自检面只剩四项业务动作，「只保留内容本身」被丢掉；`comment_design` 置顶首条自述是
「**被追问的**」；`author_share_line` 是一句句末指向受众的问题；
`comment_design` 末行自判「以上预埋问答均为判断方法的延伸，不构成 CTA」。
「闭合」「权威顺序」「要求受众」三词在产出中各 **0 次**——新规则在推理里零痕迹。

### `confirmed_origin`

```yaml
confirmed_origin: SYSTEM_UNDER_TEST
failing_node: 本轮 b1 后继 Skill 的修复覆盖面不足（不是 PP 应用本身坏了）
```

新规则装在「CTA 三级接缝」之后与「无 CTA 评论区」小节前，但
**PP-5「评论区是设计出来的，不是等来的」整节未被约束**——它无条件要求
「第一条自己写，写一条**能被追问的**」，产出用的正是这个原词；
`author_share_line` 一节同样未被覆盖。**本轮修复的影响面算少了（A3「少算」）。**

归因排除：`INPUT_ENVIRONMENT_OR_TOOL` 不成立（输入哈希全等、`cta_contract` 原文完整在输入内）；
`ORACLE_OR_CRITERION` 不成立（D1-c 逐条列举动作面，早于结果冻结）；
`CHECKER_OR_FIXTURE` 不成立（判定读产出原文逐字，不靠 token 放行）。

详见 `unified-app/docs/PPBS_FAILURE_TRIAGE_001_D1_CTA.md`。

### 停止与成本

第一次正式 FAIL 出现后**立即停止**：不重试、不改实现、不改判据、不补输入、
不执行 D2/D3、不开启第二次修复迭代。

```yaml
top_level_workflow_runs: 1 / 3
llm_node_attempts:       1 / 10
retries: 0    repeat_sampling: 0    ab_tests: 0    reviewer_calls: 0
```

### 受保护面现状

- provider 钉 `2026-08-29 03:34:58.999575` **未改动** ⇒ Seam、M5 FP、统一画布调用的仍是旧 PP；
  b1 只作为 PP app 的已发布版本存在，**未被任何消费者引用**。
- 其余八个受保护应用、候选画布、`hop_pin` 零漂移。
- 旧 PP Skill 两份、旧 PP Workflow 版本行、M5 历史 DONE 回执、历史 RAW/Gate/Result 均未覆盖。
- `main` / `origin/main` 停在 `01a42b0`。

### 需要规划侧裁定的一项披露

Founder §五 写「只有 D1、D2、D3 全部 PASS，才允许：1. 发布 PP 后继版本」。
本轮在 Phase B 就发布了新版本——因为 D1 必须调用到后继版本才能验证它，
而 Phase C-07 又要求「provider/Seam 在模型验证通过前仍指向旧版本」，
两者只有「先发布、后重钉」这一种排法。该排法在 Phase A 的 Gate 里
（`test_scoped_binding_change`）**先于任何模型调用**写死并说明了理由。

结果是：`apps.workflow_id` 现在指向 b1，PP graph md5 已变为 `7940dc00…`，
但**没有任何消费者引用它**。如需把 PP app 的已发布指针也退回旧版本，
请明确授权——这是一次超出已冻结回退条件（该条件只覆盖 provider 钉）的写操作，
执行侧不自行决定。

### M5 历史结论处置

- `terminal_state = DONE` **原样保留**，不改写。
- 置 `STALE` 的只有「依赖 PP graph md5 绑定」的记录（10 处），且**尚未建立 successor**——
  因为后继版本未通过验证，现在建立 successor 基线会把未验证状态上行。
- 保持 `CURRENT`：M1/M2/M3/Hop/Seam 路由结论、四份上游产物、无暗跑结论、
  S4 载体侧 V-01…V-07 / V-08A / V-09 / S-01。**不 blanket STALE。**
