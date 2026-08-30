# PP 交付边界 · 最小后继修复计划 v1.0（**只输出计划，不实施**）

- `task_id`: `DIYU-V1-UNIFIED-DIFY-APPLICATION-001`
- `authority`: CONTINUE EXECUTION PROMPT v1.0《UAPP S4 证据真值纠偏与 PP 交付边界归因》第六节
- 本文件**不授权**任何实施，也**不授权**任何模型调用。实施需要独立的 Execution Prompt。
- 归因真源：`unified-app/docs/S4_CANONICAL_TASK_STATE_FAILURE_TRIAGE_001_PP_BOUNDARY.md`

---

## 一、唯一候选修复节点

```yaml
candidate_repair_node: PUBLISHING_PACKAGING 能力应用的交付生成层
app_id: c9cdea24-9df3-400b-9ecd-1d740e8c96df
provider: diyu_m5fp_publishing_packaging（pin 2026-08-29 03:34:58.999575）
```

**唯一。** 不并列第二候选，不做 A/B。

---

## 二、为什么不是 M1、M2、M3、Hop、Seam 或统一画布投影

按 A3「修复指向最高失效节点，不在下游打补丁」，逐条排除，每条都有确定性证据：

| 节点 | 为什么不是它 | 证据 |
|---|---|---|
| **M1 任务上下文** | 载体字段全部有 `ref`，等级与来源一致（V-07 PASS，`missing_source_ref=[]`、`level_ref_mismatch=[]`、`placeholder_in_carrier=[]`） | RESULT v1.1 · V-07 |
| **M2 持久化** | `workspaces/accounts/cycles/tasks` 各 1 行，`boot_turns=[1]`，重复幂等键 `[]` | RESULT v1.1 · V-08A |
| **M3 单账号持续运营** | 七轮各 1 次 run，全 succeeded，无暗跑 | RAW `nested_app_runs` |
| **Hop** | T7 `upstream_capability=PRODUCTION_DIRECTOR`，`upstream_delivery` 与 T6 artifact 逐字节相等；`cta_contract` 等六项约束**逐字**出现在 PP 输入里 | 外部复核证据 `input_constraints` 全 `true` |
| **Seam** | `PP.artifact == SEAM.artifact`（14984）、`PP.user_delivery == SEAM.user_delivery`（1632），sha256 相等，**一个字都没加** | 外部复核证据 `downstream_is_passthrough` |
| **统一画布投影层** | `CANVAS.final_text == CANVAS.answer == PP.user_delivery`，sha256 相等 | 同上 |

九条违规定位串在 **PP 输入中零命中**，在 **`PP.raw_preserved`（PP 自己的原始模型输出）中首次出现**。
在投影层过滤，等于在下游遮盖上游产出的问题——违反 A3，且会让 PP 的 `artifact`（14984 字，下游可能继续消费）继续携带问题内容。

---

## 三、为什么「在文案后标注这是推断」不能合法化无来源事实

1. **A2**：加限定语是**非事件的变换**。改写、补一句说明、语气软化都不改变声明在可信度阶梯上的位置。
   「苏禾一直在用这套三问」在正文里是 `已观察` 级别的事实陈述；脚注不产生任何合法上行事件，也不产生下行事件。
2. **受众不同**：发布文案的读者是顾客，脚注在「需要你确认的三件事」里，不随内容进入受众视野。
   对受众而言，交付物中呈现的仍然是「门店搭配师一直用这个方法」这条既成事实。
3. **PP 自己已经核对出没有依据**：`used_fact_refs` 原文写着「夹具原文写的是『长期接触门店陈列、顾客试穿和成套搭配』，没有写『常用三问』」。
   知道没有依据、仍然写进交付物、再加一句声明——这是把披露当成许可。
4. **合同侧已经写死了正确做法**：`expression_boundary` 原文「如任务确需演绎人物或事件，必须**显式标注为虚构**，
   且不得借演绎改写商品或品牌事实」。「标注为推断」不等于「标注为虚构」，也不解除「不得改写人物事实」。

**正确的降级方向不是加脚注，是改写主张本身**：把「苏禾一直在用这套三问」降成不指向具体真人既往行为的表述
（例如把三问作为这条内容自己提出的方法，而不是某人既有的习惯）。这不降低成品质量，只去掉无依据的具体主张。

---

## 四、NO_CTA 的正确覆盖面

`cta_contract` 原文：**「不做购买、到店、私信或领取引导，只保留内容本身」**。

`只保留内容本身` 是兜底句，覆盖**一切要求受众采取动作的表达**，至少包括：

```
购买 · 下单 · 到店 · 预约 · 咨询 · 私信 · 领取 · 关注 · 评论 · 回复 · 收藏 · 转发 · 分享 · 点赞 · 参与话题
```

- 「你自己买衣服前，会先问自己哪个问题？」是索取评论动作，在边界之外。
- 「评论区设计」整段以引导评论互动为目的，在边界之外。
- 把「只保留内容本身」读成「不做购买引导」，是**下游缩小上游边界**（A4：非承诺只读向下继承，任何形式都不得复活）。
- 自造豁免类目（「低风险互动范畴」）无效：边界只能由有权者改版，执行方不得在产出里改写（A1 跨域不覆盖）。

**注意区分**：内容**内部**的自问句（口播里的「我该不该买」）是内容本身的一部分，不是向受众索取动作；
边界管的是**要求受众做动作**的表达。修复必须能区分这两者，不能一刀切掉所有问号。

---

## 五、不得写专用字符串分支

**禁止**为「苏禾」「三问」「评论区」写任何 case 专用字符串分支、关键词黑名单或正则。理由：

- A5：一个只在这一个案例上生效的分支，换一个品牌、换一个人物、换一种互动措辞就失效，等于没有；
- 它会让下一次验证在同一夹具上「看起来通过」，制造第二次 F3；
- 上一轮 FB-07 已经付过一次学费：v1.0 的正则在真实产物上误报四条，是靠**姓氏锚**这类结构规则修好的，不是靠加词。

修复必须在**规则层**成立：事实主张必须能回指到已登记来源；CTA 边界按上游原文的**兜底句**判定，
而不是按一张可以被绕开的动词表。

---

## 六、影响面与最小定向回归（修改共享 PP 应用会波及已完成 M5）

PP app `c9cdea24-9df3-400b-9ecd-1d740e8c96df` 是 **M5 FP 的 PP**，不是本任务私有副本。当前 graph md5 `788c8555aca09e6fa6d979f237f70157` 被以下 7 处记录绑定：

| # | 绑定文件 | 性质 |
|---|---|---|
| 1 | `decision-chain/evidence/m5/FINAL_P0_CAPABILITY_SUCCESSOR_BUILD.json` | **M5 已完成验收证据** |
| 2 | `decision-chain/evidence/m5-final-p0/CLOSEOUT_READONLY_BINDING_REFRESH.json` | **M5 收口只读绑定** |
| 3 | `unified-app/evidence/UAPP_R0_PROTECTED_BASELINE.json` | 历史受保护基线 |
| 4 | `unified-app/evidence/UAPP_R1_PROTECTED_BASELINE_v1.0.json` | 当前受保护基线 |
| 5 | `unified-app/stages/S4_CANONICAL_TASK_STATE_CANDIDATE_MANIFEST_v1.0.json` | 本轮漂移判据 |
| 6 | `unified-app/evidence/stages/s4_canonical_state/run/RUN_META.json` | 本轮运行前后快照 |
| 7 | `unified-app/evidence/stages/s4_narrow_chain/RUN_META.json` | 上一轮运行快照 |

消费者：`diyu_m5fp_publishing_packaging` provider → **M5 FP Seam `5fca0162-e26b-4545-a00b-66b1a2a2a077`** → UAPP 候选画布。

**因此不得静默修改。** 实施前必须由规划侧显式授权，且实施时至少满足：

1. 修改 PP graph ⇒ md5 必然变化 ⇒ 上述 7 处绑定按 A3 一并置 `STALE`，逐条定向复验，**不 blanket STALE 其它无关项**；
2. M5 FP 的既有验收结论中，**依赖 PP 输出内容**的部分置 `STALE` 待复验；**不依赖 PP 输出内容**的部分（如 M1/M2/M3/Hop/Seam 的接缝结论）保持 `CURRENT`；
3. 新建后继基线文件（R2），**不覆盖** R0 / R1；
4. Seam 与 provider 的 pin 是否需要重发布、重发布是否改变 Seam graph md5，必须在实施前先只读确认，作为影响面的一部分登记；
5. 若规划侧判断不能动 M5 FP 的 PP，替代路线是**在同一 workspace 新建 PP 后继应用**并只让 UAPP 候选画布指向它——
   代价是 UAPP 与 M5 FP 从此不共享 PP，这是一个产品级取舍，**必须由 Founder 裁决，执行侧不得自选**。

---

## 七、修复后的验证设计（点对点，先确定性后模型）

严格按顺序，前一层不过不进下一层：

### 第 0 层 · 零模型（先做，不花任何 token）
- 修复对象的确定性自检：规则层是否只依赖「来源可回指」与「上游边界兜底句」，**不含任何案例专用字符串**；
- 单点变异区分：拆掉事实回指规则 ⇒ 正例必须翻；拆掉 CTA 兜底规则 ⇒ 负例必须翻；
- 判据在任何模型调用之前冻结并落盘，版本化，不原地改。

### 第 1 层 · 一个 PP 正例（1 次调用）
- 输入：事实充分、`cta_contract = NO_CTA`；
- 通过条件：产出可用，且**不**因为规则收紧而拒答或降级成空壳。

### 第 2 层 · 一个冲突负例（1 次调用）
- 输入：**主动要求**编造人物历史（例如「就说这是店长十年一直在用的方法」）**并且**要求做评论互动；
- 通过条件：PP 明确拒绝这两项、给出可执行的替代表达，且仍然交付完整成品——
  按 CLAUDE.md「资料不足时不得整任务拒绝」，阻止的是无依据的具体主张，不是整个任务。

### 第 3 层 · 受影响的统一应用端到端复验（1 次，且仅当 1、2 层都过）
- 只跑受影响的那一条链路，不重跑全部七轮；
- 不做 A/B，不重复采样，**不为凑 PASS 增加轮次**；
- 第一项正式 FAIL 出现后立即停止，不改实现、不改判据、不补输入。

### 预算上限（供规划侧冻结时参考）
```yaml
deterministic_checks: 不限（零模型）
pp_positive_case: 1
pp_negative_case: 1
end_to_end_after_both_pass: 1
ab_tests: 0
repeat_sampling: 0
```

---

## 八、本计划不授权什么

不授权实施上述任何一步；不授权模型调用；不授权修改 PP 或任何受保护应用；不授权改 Seam / provider / 候选画布；
不授权进入 S5；不授权合并 main；不授权把 `S4_OVERALL_ACCEPTANCE` 从 FAIL 上调。
