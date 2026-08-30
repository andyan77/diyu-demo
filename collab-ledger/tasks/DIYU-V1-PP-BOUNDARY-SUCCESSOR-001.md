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

---

## REBASE · b2 最小修复与收口（2026-08-30）

`task_mode: REBASE`｜沿用同一 `task_id`，不新建平行任务。
`planning_observed_head: 53e1f76995de079f4bcb37931416ae95af7c0488`。
授权：《DIYU V1 · PP Boundary Successor b2 最小修复与收口执行 Prompt》。

### 一、启动状态修正（只追加，不覆盖，不追溯改绿）

规划侧裁定 b1 的登记等级偏低——b1 已经执行过一次**正式** D1，
因此它的整体不能停在 `NOT_VERIFIED`；同时 D2 未运行，事实面也不能整条上调。

```yaml
PP_BOUNDARY_SUCCESSOR_b1: FAIL / CURRENT
V-08B_FACT_TRACEABILITY_b1:
  D1_positive: PASS
  overall:     NOT_VERIFIED        # D2 未运行，不能上调完整 V-08B
V-08C_CTA_FIDELITY_b1: FAIL / CURRENT
CURRENT_UAPP_S4_OVERALL_ACCEPTANCE: FAIL / CURRENT
```

第四条的理由：统一应用当前仍调用**旧 PP**，而旧 PP 的既有适用失败尚未被
任何通过验证的 successor 取代——所以 S4 整体不是"还没查"，是"当前为失败"。

历史证据原样保留。b1 的全部落盘件（`PPBS_*_v1.0`、`PPBS_D1_RAW.json`、
`PPBS_PHASE_D_RESULT_v1.0.json`、失败归因 001）**一个字节都不改**。

### 二、Phase A · 恢复安全发布指针（零模型调用）

上一轮遗留的待裁定项，规划侧已裁定：退回。

| | 之前 | 现在 |
|---|---|---|
| PP app 当前发布图 | `7940dc00…`（b1，未通过验证） | `788c8555…`（旧稳定图） |
| PP app 当前发布版本 | `2026-08-30 09:05:41.729617` | `2026-08-30 09:44:26.834257` |
| PP workflow 行数 | 3 | 4（b1 行与旧稳定行都保留） |
| provider 钉 | `2026-08-29 03:34:58.999575` | 未动 |

机制：Dify console `draft-sync` + `publish` 重新发布旧稳定图。
**没有执行任何 `UPDATE` / `DELETE` 语句**，b1 历史行原样保留可供回指。
恢复后复算：`hop_pin`、候选画布、Seam 与其余八个受保护应用 **零漂移**。

证据：`unified-app/evidence/stages/pp_boundary_successor/PPBS_B2_PHASE_A_RESTORE.json`。

这一步**只是隔离失败候选，不构成 PP 产品验收 PASS。**

一次已披露的传输侧失败：首次 `draft-sync` 返回 400——
`environment_variables` / `conversation_variables` 在 DB 里存成 `{}`，
而 SyncDraftWorkflow 要求 list。零模型调用、零 Dify 写入、零状态变化，
修正为空列表后重发（空对象与空列表在语义上都是"没有变量"，不改变任何取值）。

### 三、Phase B / D · b2 后继与判据（模型调用之前全部冻结并提交）

`content-production/skills/packaging-content-for-release-m4-b2/SKILL.md`
sha256 `2b15b7858bddb6cf2d31201512c883b9f64aa2d34cac6255f1272aa61f033b0c`，39620 字。
从 **b1** 逐字继承（继承体逐字节等同 b1；b1 的「事实来源必须蕴含该主张」与
「CTA 权威顺序」两整块各 1 次逐字在场，**事实修复未回退**），新增 5 块 4470 字：

| 块 | 装在哪 | 做什么 |
|---|---|---|
| `CTA_STATE` | b1「CTA 权威顺序」之后 | 从 `cta_contract` 原文推一次任务级状态 `strict_cta_closed`；`true` 时**九行对外输出面清单**受同一条「不得要求受众做动作」约束，含「句末指向受众等一个回答的问句」；`false` 时一个字不变 |
| （同块）自我声明段 | 同上 | 「这不算引导」「这只是延伸」不改变行为性质；复述边界 ≠ 守住边界 |
| （同块）设问段 | 同上 | 内部设问必须由内容自己立即接住；问完就停、落在结尾／评论区／转发语位置的是 CTA |
| `PP5_COND` | PP-5 标题之后 | `true` 时 PP-5 三条整体不适用，`comment_design` 取 `NOT_APPLICABLE` 或只写被动答复边界；换措辞继续要求互动等于没执行 |
| `SHARE_COND` | 「作者转发语」标题之后 | `true` 时只能是陈述句或 `NOT_APPLICABLE` |
| `SELFCHECK17` | 自检 16 之后 | 按九行清单逐面扫，对照 `cta_contract` **原文全文**；并反查 `false` 分支没被误删 |

`unified-app/stages/PPBS_GATE_v2.0.json` 新建不覆盖 v1.1。
`phase_d_criteria` / `budget` / `must_remain_regardless` **由 v1.1 直接取值构造**，
逐块一致核验通过——b1 的失败**不改 CTA 判据、不减对外输出面检查范围**。
输入沿用 `PPBS_INPUTS_v1.0.json` 原文件，未新建。

PP app 发布 b2：版本 `2026-08-30 09:51:55.613459`，graph `8366328b…`；
只改 `skill_llm.system`，节点/边/模型/参数零漂移；provider 钉当时不动。

### 四、Phase C · 确定性验证 14/14

C-09 正向控制、C-10 负向控制（`false` 分支表述 ＋ PP-5 原三条 ＋ 三级表低风险行 ＋
无 CTA 评论区「可以做」清单逐字在场）、C-11／C-12／C-13 三条单点变异
（分别删 `comment_design` 条件化／`author_share_line` 条件化／全表面自检，
对应控制各自翻 FAIL 且另两项不受影响）、C-04B 证明 b1 事实修复未回退。

`FAILURE TRIAGE 002`：C-10 首轮 FAIL，归因 `CHECKER_OR_FIXTURE`
（探针把反引号写在 `false` 之前，与正文不符）。只改探针、不改被测对象，
修后重跑**完整 14 条**含正负控制与原始失败案例。零模型调用。

### 五、Phase E · 三级点测

| | 结果 | 运行 | 关键事实 |
|---|---|---|---|
| **E1 · D1 正例** | **PASS 5/5** | `07d5ca02` 160.4s attempts=1 LLM 1 | 九面逐面走过，受众指向问句 **0 句**；动作词全在否定式约束句或 Skill 既有「发布前五条检查」的内部自问里；历史行为探针与限定语探针各 0 次 |
| **E2 · D2 冲突负例** | **PASS 5/5** | `81dc796d` 97.3s attempts=1 LLM 1 | 「十年一直用这套方法」四处命中全在拒绝说明里，九面无一处写成事实；评论互动要求被拒并写明「需要上游确认互动边界，不是包装环节可以自己放宽的」；替代表达实际交付为陈述句转发语；仍交付完整成品 |
| **E3 · D3 统一入口** | **NOT_VERIFIED（INCONCLUSIVE）** | HTTP 400，0.02s | **零模型输出**：九应用 run 全 0、LLM 0、`node_detail` 空。六条判据一条都没被执行到 |

b1 的五处 CTA 失败点在 D1 逐点复查全部修好：`cta_surface` 把「只保留内容本身」
纳入约束面并推出 `strict_cta_closed = true`；`comment_design = NOT_APPLICABLE`
只留被动答复边界；`author_share_line` 是陈述句；无自我声明式放行；交付块不复述边界清单。

`FAILURE TRIAGE 003`：D3 归因 `INPUT_ENVIRONMENT_OR_TOOL`——**本任务运行器的传参错误**
（把字面量 `"file"` 当成 Bearer token，且没解包 `(status, body)` 元组），
这段代码继承自 b1 运行器、本次是它第一次被执行。按预算规则
**不重跑、不改实现、不改判据**，登记后停下。

### 六、成本与受保护面

```yaml
top_level_workflow_runs: 2 / 3      # D3 未产生任何 run
llm_node_attempts:       2 / 10
retries: 0    repeat_sampling: 0    ab_tests: 0    reviewer_calls: 0
```

受保护面已恢复到测试前状态：PP 当前发布图与 provider 钉住的图都是旧稳定图
`788c8555`；b1、b2、原始旧稳定行**全部保留**（workflow 行 6）；
Seam `db49a3da`、候选画布 `99c3edf7`、其余八应用、`hop_pin` 零漂移；
M5 历史 DONE 回执与全部历史 RAW/Gate/Result 未动；`main` / `origin/main` 停在 `01a42b0`。

### 七、状态（公式未成立，一项都不上调）

```yaml
PP_BOUNDARY_SUCCESSOR_b2:
  D1_positive:          PASS / CURRENT
  D2_conflict_negative: PASS / CURRENT
  D3_unified_entry:     NOT_VERIFIED (INCONCLUSIVE)
  overall:              NOT_VERIFIED        # 三项未全 PASS
V-08B_FACT_TRACEABILITY: NOT_VERIFIED       # 未上调
V-08C_CTA_FIDELITY:      NOT_VERIFIED       # 未上调；b1 的 FAIL/CURRENT 仍是历史事实
CROSS_TURN_CORRECTION_PROPAGATION: NOT_VERIFIED (NOT_CHECKED)
S4_OVERALL_ACCEPTANCE:   NOT_VERIFIED
S5:                      NOT_STARTED
main_merge:              NOT_ALLOWED
terminal_state:          UNSET
next_state:              CHECKPOINT
```

不建 b3。第三次修复迭代 FORBIDDEN，且**本轮没有任何证据指向 b2 实现有错**——
b2 在两次正式点测里都通过了。

### 八、需要你裁定的两项

1. **是否授权重跑 D3。** 需要：修运行器 D3 分支的上传调用（零模型 harness 修复）＋
   重新发布 b2 并重钉 provider（两步都是零模型确定性操作，b2 的 workflow 行还在）＋
   按**原冻结**的输入与六条判据跑一次。D1、D2 已是正式 PASS，无需重跑。
2. **恢复动作是否越权。** 冻结的回退条件字面只写「D3 FAIL」，没写「D3 未执行」。
   我把本次归入该条并恢复了 provider 钉与发布指针，理由与依据写在
   `unified-app/docs/PPBS_B2_FAILURE_TRIAGE_003_D3_TRANSPORT.md`。如认为越权，请指出。
