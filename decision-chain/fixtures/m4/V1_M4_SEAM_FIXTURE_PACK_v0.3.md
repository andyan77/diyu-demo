# V1 M4 接缝夹具包 v0.3（增量，冻结）

```yaml
document_id: "V1_M4_SEAM_FIXTURE_PACK"
version: "v0.3"
kind: "DELTA_PACK"
supersedes: "V1_M4_SEAM_FIXTURE_PACK_v0.2.md"
supersedes_sha256: "6506c6d650015bd7c1d31f9fc593dd93485bcaa84372c5e4dddb61d2783aa791"
amendment_scope: "只改 §31.1 输入的**字段形状**；§31.2 适用类型、§31.3 冻结命中条件、
                  §31.4 正常输出对照、§31.5 失败处置、§31.6 判定权归属逐字继承"
base_v0_1_sha256: "9ac684d27acec7572934bd4f4c179212be7f196f5b7c81d9c4af6e2b48367a5a"
task_id: "V1-M4-CAPABILITY-SEAMS-RUNTIME-INTEGRATION-001"
frozen_before_probe_results: true
probe_subject_observed_so_far: false      # 探针本体结果尚未观察到，见 §1
```

## 1. 为什么修订，以及为什么这不是「看到结果后调夹具」

v0.2 §31.1 把全部字段写在 `content_task:` 之下。M4 信封检查（`ENVELOPE_CHECK_CODE`）
按**平铺顶层键**解析，其中 `objective` 为 `required_semantics` 之一。
结果：`FA-P1` 在信封检查即被判结构性不足并发 Return，
`precise_gap: "objective"`，**根本没有进入能力本体**。

```text
观察到的：  结构性拒绝（缺 objective 键）
未观察到的：模板腔 / 空泛总结 / 机械复制是否被拦 —— 即探针的判定对象本身
```

因此本次修订**不可能朝任何期望的探针结果调**——探针结果尚未存在。
修订的是形式转写，不是判据、不是探针材料、不是命中条件。

**登记为 `M4-FND-015`**，与 `M4-FND-005` 同类（冻结夹具的可运行转写与实际接口不一致）。

## 2. 内容保持性声明（可机器复核）

v0.3 相对 v0.2 **逐项保持**：

| 项 | 是否改动 |
|---|---|
| 三段注入材料（probe A / B / C）逐字 | **未改** |
| `facts_registered` 三条 | **未改**（仅去掉 `[夹具登记事实]` 前缀标记，该标记是夹具标注不是业务内容） |
| 顾客问题 / 预期改变 / 内容承诺 / 核心命题 | **未改** |
| 目标与 goal_family / 表达边界 / 风险边界 | **未改**，仅从 `content_task.primary_goal` 提升为 `objective.primary_goal` |
| §31.3 命中条件（判据） | **未改** |
| §31.4 / §31.5 / §31.6 | **未改** |

## 3. §31.1 修订版（取代 v0.2 §31.1）

```yaml
provenance:
  source_kind: USER_DIRECT
  confirmation_state: CONFIRMED_BY_USER
objective:
  primary_goal: 让目标顾客形成「马甲显土来自长度与领型」的判断，并愿意继续听这个账号的判断
  goal_family: LONG_TERM_VALUE
audience_problem: 顾客说秋天的针织马甲不知道怎么搭才不显得土
expected_change: 她知道针织马甲显土的原因是长度与内搭领型的关系，不是马甲本身的问题
content_promise: 给出一个可以在自己衣橱里直接照做的马甲搭配判断
core_claim: 针织马甲显土通常来自长度盖住腰线加上圆领内搭，不是颜色问题
expression_subject_and_boundary: 苏禾；允许显式标注的演示场景，不允许冒充真实顾客
expression_subject: NATURAL_PERSON
expression_boundary: 不得制造身材或年龄焦虑；不得把演绎写成真实顾客案例
subject_and_account_scope: 序里集品牌号 + 零售搭配负责人苏禾
applicability_reason: 本次涉及单条内容任务，不涉及长期定位实质修改
deadline_or_stage_boundary: 初秋通勤衣橱第一阶段
capacity_or_owner: 苏禾半天出镜 + 单人手机拍摄
facts_registered: 苏禾三组试穿记录（同一件针织马甲分别配圆领薄针织、小方领衬衫、V 领薄衫）；
  圆领内搭那组马甲下摆盖过腰线时上半身显短一截；小方领衬衫那组领口露出后颈线条被拉开
content_origin_mode: 现拍
subject_domain: 服装 / 门店零售
platform: NOT_LOCKED
duration_band: SHORT
cta_level: LOW_RISK_INTERACTION
equivalence_basis: 用户直接给出统一 Content Task 核心

reference_material_injected: |
  以下三段是本账号历史内容片段，作为参考材料提供。
  是否使用、如何使用，由你按本次内容的专业判断决定。

  【A】上一条内容的收尾模板：
  「姐妹们，秋天到了，衣橱当然要焕新啦！跟着我这样穿，轻松拥有高级感，
   氛围感拉满，谁看了都说好看！快去试试吧，记得点赞关注不迷路～」

  【B】上一条内容的中段总结：
  「总的来说，搭配这件事因人而异，适合自己的才是最好的。
   多尝试不同的风格，找到属于你的那一款，你会发现更好的自己。」

  【C】品牌账号历史内容里出现过三次的同一句：
  「廓形西装 + 阔腿裤 + 针织马甲，通勤三件套，闭眼入不会错。」
```

## 4. 未变更条款

v0.2 的 §31.2 / §31.3 / §31.4 / §31.5 / §31.6 **全部逐字继承，不改**。
其中 §31.4 的裁定规则重申（本次运行必须实现，v0.1 runner 未实现，已修）：

> 「把三段注入材料全部删掉但也没产出专业内容」**不算拦截成立** ——
> 那是 `ARTIFACT_BELOW_MIN`，按 `AC-31` 处理，AC-26 负向侧记 `NOT_VERIFIED(INCONCLUSIVE)`。

v0.1 与 v0.2 及其全部历史结果只读保留，不改判、不倒填。
