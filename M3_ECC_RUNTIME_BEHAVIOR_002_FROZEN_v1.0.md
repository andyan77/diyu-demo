# ECC-M3-RUNTIME-BEHAVIOR-002 · 冻结判据（EP-06 行为半）

> `task_id`: `DIYU-V1-M3-ACCOUNT-CONTENT-OPERATOR-001`
> `bound_ac`: `M3-AC-01`（反证探针半）、`M3-AC-02`、`M3-AC-03`、`M3-AC-04`、`M3-AC-05`（运行时半）、`M3-AC-06`、`M3-AC-07`、`M3-AC-08`、`M3-AC-09`、`M3-AC-10`、`M3-AC-14`、`M3-AC-15`
> `frozen_at`: 本 commit（**先于本 ECC 任何一次运行**，见 §0 时序声明）
> `frozen_by`: 执行侧（非独立判定者）；判定由未参与本文件撰写与 Skill 实现的独立读者执行
> `case_file`: [`account-operations/evidence/ep06b-runtime-behavior/_cases.json`](account-operations/evidence/ep06b-runtime-behavior/_cases.json)
> `case_file_sha256`: `1da81ea61cd2357dc893fd5bd228adc84e1dc3f97a35090388584aaac9e9eb75`
> `total_cases`: `49`

## 0. 时序声明（A2 先后）

本文件与 `_cases.json`（含全部 49 条的**准确输入**与**逐条 Oracle**）在本 ECC 的任何一次运行**之前**写成并作为独立 commit 提交。判据、输入、Oracle 三者一并冻结。

判据晚于结果、或看到结果后原地修改判据的，本轮只算探索，不产生正式 PASS。确需改判据只能新开版本化修订（v1.1）并写明触发事件。

**为什么另起一份 ECC 而不是扩写 `ECC-M3-RUNTIME-FIDELITY-001`**：后者已经冻结并已产出两轮结果。在它上面追加判据等于"看到结果之后改判据"。本文件是**新判据、新绑定、新一轮取证**，与前者不共享任何结论。

## 1. 与 `ECC-M3-RUNTIME-FIDELITY-001` 的分工

| | FIDELITY-001 | BEHAVIOR-002（本文件） |
|---|---|---|
| 问的问题 | 唯一专业语义经工程化后**有没有丢** | 这份语义在真实运行中**做不做得对** |
| 绑定 AC | `M3-AC-16` | AC-01/02/03/04/05/06/07/08/09/10/14/15 |
| 组数 | 7 组 9 例 | 49 例 |
| 载体 | 轮 1–2：直连 DeepSeek；轮 3：Dify 画布链路 | Dify 画布链路 |

两份互不覆盖：前者全过也不能推出后者任一条 PASS，反之亦然。

## 2. 运行绑定（锁定变量）

```text
carrier      = Dify Workflow 候选 App b7fb5b1a-9278-426c-bb8a-f9f288639548
                （task-id 专用候选/测试 App，图 = start → llm → end 三节点）
provider     = langgenius/deepseek/deepseek
model_id     = deepseek-v4-flash
temperature  = 0.4
skill_commit = SKILL.md 于 commit af61b82 冻结，本轮零改动
service_api  = POST http://localhost/v1/workflows/run（response_mode=blocking）
```

任一锁定变量变化 ⇒ 本 ECC 全部结果对新绑定置 `STALE`，须整轮重跑，**不是只重跑受影响的那几例**（A3：Skill/图/模型是所有例的共同绑定）。

## 3. 事实来源（不新增任何未登记事实）

| 来源 | 用途 |
|---|---|
| `decision-chain/fixtures/一页纸夹具品牌事实 v0.1.md` | 品牌、人物、品类、价格带、渠道、当前经营任务、表达边界 |
| `M3_ECC_RUNTIME_FIDELITY_001_FROZEN_v1.0.md` §2 | 锁定账号上下文（周宁账号、视频号、针织马甲事实、权限层级） |

`_cases.json` 中出现的全部商品、颜色、价格、人物、门店与经营事实均可回指上述两处。**未新增任何商品、库存、价格、面料、顾客或经营事实。**

## 4. 上下文模板与变量纪律

每例的 `account_context` 由同一模板生成，15 个槽位固定顺序：

```text
account_anchor / positioning / platform / current_task / stage_evidence
expected_publish_count / baseline_capacity / actual_capacity
facts_and_assets / market_observations / feedback / campaign_overlay
expression_permission / primary_objective / secondary_objectives
```

**默认值锁定为 FIDELITY-001 §2 的账号上下文。** 每例只在 `context_overrides` 中显式列出它改动的槽位，其余逐字不变——这是 AC-03（八目标反事实）与 AC-06（三产能）能成立的前提：变量必须唯一。

`include_fashion_ref` 为真时，`loaded_references` 传入 `references/fashion-and-market.md` 全文；为假时传空串。**条件加载由调用方（M4 职责，见 Prompt §10.3）承担，不由 M3 自己决定读不读文件**——这是把 Skill 的"条件加载"语义搬到 Dify 载体上的唯一忠实做法。

## 5. 判定协议

1. 执行侧**只运行、只如实记录**原始请求与原始响应，**不得在本文件或任何 commit message 中对任一例做 PASS/FAIL 判定**。
2. 判定由**未参与本文件撰写与 Skill 实现**、且**未看过本任务任何 Checkpoint 与执行侧摘要**的独立读者执行，写入 `M3_ECC_RUNTIME_BEHAVIOR_002_VERDICT_v1.0.md`。
3. 判定者只被提供：本文件、`_cases.json`、原始 transcript、`SKILL.md`、语义主稿。
4. 判定用词只允许 `成功` / `不足` / `失败` / `无结果`，逐例给出可核查的引用位置。
5. 原始 transcript 逐字保留（含全部 workflow 输入、Dify run id、模型原始响应、token 用量、时间戳），存放于 `account-operations/evidence/ep06b-runtime-behavior/`。
6. `.env` 与其中的任何凭据值不得出现在任何 transcript 或提交文件中。

## 6. 逐 AC 的通过条件（对应 `M3_ACCEPTANCE_CRITERIA_FROZEN_v1.0.md` 的 ECC 卡，不放宽）

| AC | 本 ECC 覆盖的例 | 该 AC 在本 ECC 内成立的条件 |
|---|---|---|
| AC-01（反证探针半） | `B01-P` | 该例 `成功`。AC-01 整条仍需 EP-05 的①②与 EP-08 的③消融门，本 ECC 不单独闭合它 |
| AC-02 | `B02-1/2/2P/3/4` | 五例全部 `成功`，且无一例把暂定锚点写成已确认定位 |
| AC-03 | `B03-1…8` + `B03-N2` + `B03-N3` | 八个目标变体**两两**满足四轴中至少两轴实质差异；两条负向探针均 `成功` |
| AC-04 | `B04-1/1P/N1/N7` | 四例全部 `成功` |
| AC-05（运行时半） | `B05-1/2` | 两例全部 `成功`。结构半（枚举/节点/分支反搜）另由 EP-05 与 Dify 图静态检查承担 |
| AC-06 | `B06-1/P` | 两例全部 `成功` |
| AC-07 | `B07-1/2/3/P` | 四例全部 `成功` |
| AC-08 | `B08-1/P` | 两例全部 `成功` |
| AC-09 | `B09-1…5` + `B09-N5` | 六例全部 `成功` |
| AC-10 | `B10-1/2/3/4/P` | 五例全部 `成功`，且四情形处理**实质不同**（①与②处理相同即 `FAIL`） |
| AC-14 | `B14-1/2/3` | 三例全部 `成功`。AC-14 的下游消费半已在 EP-05 取证（含一条已披露的 `ABSENT`），本 ECC 不改变它 |
| AC-15 | `B15-DIR-01/02/03` + `B15-CTA` + `B15-N6` | 五例全部 `成功` |

**"有但不够"一律记 `不足` = `FAIL(INSUFFICIENT)`，不得填成 `成功`。** 任一例 `不足` 或 `失败`，其绑定 AC 在本轮不得 `PASS`。

## 7. 声明上限

本 ECC 全部 49 例通过，只能建立上表所列 AC 在**本绑定、本冻结夹具集**下的行为证据。**不能**建立：

- `M3-AC-16` 的任何结论（由 FIDELITY-001 承担）；
- `M3-AC-17` 纵向可复现（由 LONGITUDINAL-001 承担）；
- `M3-AC-18` 模块专业增益（由 MODULE-AB-001 承担，本 ECC 无对照臂）；
- 任何真实经营提升、生产就绪或 M5 集成结论。

单模型、单温度、单轮采样：**同一例换一次采样可能得到不同结果**，本 ECC 不做重复采样，因此其结论强度是"在该绑定下的一次观察"，不是"稳定行为分布"。这一上限如实记录，不用样本量措辞掩盖。

```text
END_MARKER
= ECC-M3-RUNTIME-BEHAVIOR-002-FROZEN-v1.0-END
```
