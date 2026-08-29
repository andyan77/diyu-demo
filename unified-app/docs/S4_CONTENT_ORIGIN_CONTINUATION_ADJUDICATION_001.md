# S4 素材来源裁决后的连续链 · 判定书 001

`task_id: DIYU-V1-UNIFIED-DIFY-APPLICATION-001` ｜ 判定日期：2026-08-29
判据：`unified-app/stages/S4_CONTENT_ORIGIN_CONTINUATION_GATE_v1.0.json`，sha256
`01405ebfdc24f106b2673465002c307360e31ed4cc89a5793ac8776f1099996d`，**冻结并提交于任何调用之前**（commit `cea08c9`）。
机器判定原文：`unified-app/stages/S4_CONTENT_ORIGIN_CONTINUATION_RESULT_v1.0.json`。

```text
S4_CONTENT_ORIGIN_CONTINUATION = FAIL
6 PASS / 6 FAIL / 0 NOT_VERIFIED
```

**窄问题没有被回答。** 冻结的窄问题是「补齐 `content_origin_mode` 之后 CS→PD→PP 能不能继续跑完」。
本次链条**根本没走到那一步**——T2 的 Content Brief 就没产出，T3 问的也不是 `content_origin_mode`。
所以本次既不能说该问题成立，也不能说它不成立，只能说**这一轮没测到**。

---

## 一、12 项逐条结果

| 条件 | 结果 | 关键观测 |
|---|---|---|
| C01 T1/T2 真实进入 Content Brief，产生非空 artifact | **FAIL** | 两轮 `tool_content_brief` 都真跑且 succeeded，但 **T2 artifact 长度 0**；T1 缺口 `expression_subject_and_boundary`，T2 缺口 `facts_registered` |
| C02 T3 精确提出 `content_origin_mode`，不新增无关缺口 | **FAIL** | `tool_creative_script` 真跑，但缺口是 `objective.primary_goal`／`expected_change`／`content_promise`／`expression_subject`／`facts_registered`／`content_origin_mode` 一大串，不是单点 |
| C03 T4 继承同一待办与 Brief，再次进入 CS，不重做 Brief | **FAIL** | `tool_creative_script` 真跑且未重做 Brief，但 `primary_goal` 由「让熟客获得可迁移判断方法」退化成「把这条的口播稿写出来」，`audience_problem` 为空 |
| C04 T4 后 `content_origin_mode` 不再是缺口，产出非空脚本 | **FAIL** | 该项已不在缺口里，但缺口换成 `expected_change`／`content_promise`／`goal_family`；artifact 长度 0，`outcome=UNKNOWN` |
| C05 T5 上游为 CREATIVE_SCRIPT 且非空，产出制作 artifact | **FAIL** | `upstream_capability=CREATIVE_SCRIPT` ✅，但 `upstream_delivery` 长度 **0**；`tool_production_director` 真跑，artifact 0 |
| C06 T6 上游为 PRODUCTION_DIRECTOR 且非空，产出包装 artifact | **FAIL** | `upstream_capability=PRODUCTION_DIRECTOR` ✅，`upstream_delivery` 长度 **0**；`tool_publishing_packaging` 真跑，artifact 0 |
| C07 每轮只跑目标能力，不暗跑 | **PASS** | 六轮 Seam 记录各只有一个 `tool_*`，与目标能力逐轮吻合 |
| C08 已完成的 Brief 不重做，已确认事实不丢失、不被改写 | **PASS** | T3–T6 均未再出现 `tool_content_brief`；T3 基线字段无漂移 |
| C09 不声称任何具体素材已获授权 | **PASS** | 六轮交付对越权授权词表零命中 |
| C10 用户交付零内部词泄漏 | **PASS** | 判定侧独立复算零命中；画布自报 `leak_hit_count` 六轮均为 0 |
| C11 受保护面零未授权漂移 | **PASS** | 11 个受保护应用 md5 与 R0 基线一致；旧候选 `2448e4f9` 未动；候选图仍为 `f75555c0…` |
| C12 同一幂等行为不产生重复业务写入 | **PASS** | `boot_*` 只在首轮执行；M2 窗口内 workspace／account／cycle／task 各新增 1 行；幂等键零重复 |

**路由这一层是干净的。** 六轮全部落到正确能力，包括 T4——Founder 那句素材来源的回答被正确
识别为「接着上一轮的创意脚本」，没有重启、没有跑回 Content Brief。`C07`／`C08` 同时成立，
说明跨轮任务语义**没有丢**。失败不在路由，也不在跨轮接缝。

---

## 二、FAILURE TRIAGE

```yaml
observed_failure: "T2 的 Content Brief 未产出 artifact（长度 0），停在缺口 facts_registered；此后 T3–T6 全部拿不到上游产物，缺口逐层扩散"
frozen_target: "S4_CONTENT_ORIGIN_CONTINUATION_GATE_v1.0.json（01405ebf…），12 项条件，冻结于调用之前"
candidate_sources:
  - SYSTEM_UNDER_TEST
  - INPUT_ENVIRONMENT_OR_TOOL
  - CHECKER_OR_FIXTURE
  - ORACLE_OR_CRITERION
confirmed_origin: "SYSTEM_UNDER_TEST（抽取判定不稳定）；但具体失效节点 = INSUFFICIENT_EVIDENCE"
```

### 2.1 三个候选源被独立证据排除

| 候选 | 排除依据 |
|---|---|
| `INPUT_ENVIRONMENT_OR_TOOL`（夹具没进去） | 夹具**每轮都到位**：`uapp_hop.registered_facts` 六轮长度 2367／2459／2459／2541／2541／2541，`m1_extract` 每轮抽出 2451 字；attempt04 对照值 2501，同量级 |
| `CHECKER_OR_FIXTURE` | 夹具文件 sha256 与 attempt04 逐字节相同（`8c21d41d…`）；判定器在运行前用合成正负控制验过判别力，且本轮判定 100% 由确定性记录得出 |
| `ORACLE_OR_CRITERION` | 判据冻结在调用之前并已提交，运行后一字未改；C05／C06 的上游能力断言是上游 Prompt §4 原文，不是执行侧新增 |

### 2.2 确认的事实：同一输入、同一张图、同一份夹具，两次结论不同

| | attempt04（Gate 4） | 本次 |
|---|---|---|
| T2 用户话术 | 逐字相同（已确定性比对，`True`） | 同左 |
| 图 | `f75555c0…` | `f75555c0…` |
| 夹具 sha256 | `8c21d41d…` | `8c21d41d…` |
| 夹具进 hop 的长度 | 2501 | 2459 |
| **hop 抽取缺口** | **无** | **`facts_registered`** |
| **Content Brief artifact** | **5593 字** | **0 字** |

抽取层对「事实到底登记了没有」给出了**两种相反的判断**，输入却是同一份。
这是 Hop 抽取判定的**不稳定性**，不是夹具问题、不是路由问题、不是跨轮接缝问题。

**「不替用户补事实」本身是正确行为**（项目 `CLAUDE.md` §4 明令不得补写夹具未提供的经营事实）。
出问题的是**同一份材料两次被判成不同结论**，而不是它选择了追问。

### 2.3 为什么不再往下定位

两次运行不足以把失效点锁到具体节点（`m1_shadow`？hop 的抽取 LLM？Seam 内部？）。
按内核规则，未以独立证据确认具体失效节点时**只继续诊断、不扩大修改范围**——
何况本 Prompt §5 已明令 `second_repair_iteration: NOT_AUTHORIZED`、`graph_mutation: FORBIDDEN`。

```yaml
mutation_target: "本轮无。不改图、不改输入、不改 Checker、不改 Fixture、不改能力。"
protected_targets: "画布图 f75555c0、Gate v1.0、冻结输入、判定器、夹具、M1/M2/M3/Hop/Seam/六能力、旧 Canvas 与 provider —— 全部未动，C11 已确定性复核"
next_reverification: "待规划侧裁定后再定。执行侧不自选。"
```

---

## 三、运行中发生的一次执行侧故障（已如实登记，非被测对象）

首跑在 T1 返回 `http=200`（308.15s）之后崩溃：运行器的 `conv_vars()` 用了
`workflow_conversation_variables.name`，而该表没有这个列（真实列为 `id / conversation_id / app_id / data / created_at / updated_at`，
变量名在 `data` 的 JSON 里）。归因 `CHECKER_OR_FIXTURE`（证据记录器），被测系统同轮正常。

处置：

- **不重跑 T1**——它已真实执行完毕，重跑会让同一冻结输入跑两次，违反 `samples_per_turn: 1`。
  改为从 Dify 真源（`messages` / `workflow_runs` / `workflow_node_executions`）只读取回，
  零模型调用，文件内带 `reconstructed_from_db: true` 与原因，不冒充实时抓取。
- 只修运行器两处：`conv_vars()` 的 SQL、断点续跑。**判定器、夹具、判据、图一律未动。**
- 崩掉的那个字段 `conversation_variables_after_turn` **不被任何一条 pass_condition 读取**，
  只作跨轮状态旁证，因此这次修复不改变任何一项判定结果。

---

## 四、披露一项判定器的不精确（不改，登记）

`gaps()` 把 Seam `returns_json` 里的 `precise_gap` 整串收进集合，未按全角分号再切分，
于是 C02 的观测里出现了 `"expected_change；content_promise；expression_subject；content_origin_mode；facts_registered"`
这样的复合项。**它不改变本次任何一条判定**——即使完美切分，C02 仍因缺口远多于一项而 `FAIL`。
按 `checker_or_fixture_mutation_after_run: FORBIDDEN`，本轮**不修**，登记为技术债。

---

## 五、本次真实成本

```yaml
canvas_workflow_runs: 6            # 与冻结的六轮一一对应，无多余
nested_app_runs: 24
deepseek_llm_node_attempts_succeeded: 30
deepseek_llm_node_attempts_failed: 0
unplanned_followups: 0
retries: 0
```

`END_MARKER: S4-CONTENT-ORIGIN-CONTINUATION-ADJUDICATION-001-END`
