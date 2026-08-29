# `RISK-M4-030+031` 定向负控制 · 输入与预期冻结书 v1.0

- `task_id`: `DIYU-V1-M5-UNIFIED-INTEGRATION-FINAL-ACCEPTANCE-001`
- 授权：Founder 裁决 002 §四 `targeted_negative_control_authorized: true`，**只允许 1 次正式 Dify 运行**
- **本文件在任何调用之前冻结。** 冻结之后不得改输入、不得改预期；
  看到结果之后提出的任何修正只能作为下一版，本次运行按本文件原文判。
- 冻结时施工侧 HEAD：`9a1ebce`；working tree clean（见提交记录）

## 一、为什么这是负控制，不是正例的改写

Founder 明确禁止「使用现有正例的改写正文冒充负例」。本负例**不是**从
`probe_m4_030_031` 的 `base` 删一个字段得来的：

| 项 | 现有正例 `base` | 本负例 |
|---|---|---|
| 商品 | `XQ-2501` 廓形西装 | `XQ-2504` 燕麦针织马甲（680 元） |
| 素材 | B01 选品比较记录 | `DOC-B01` 选品比较表 + `VID-C01` 试穿记录二 |
| 内容主线 | 判断一件廓形西装是否适合自己先看什么 | 针织马甲在通勤衣橱里承担什么任务 |
| 出镜／确认人 | 周宁主讲 | 周宁出镜，苏禾确认试穿观察 |

事实全部取自仓库既有夹具中已登记项，**未新增任何夹具之外的商品、价格、面料或顾客事实**。

## 二、被刻意抽掉的那一项业务语义

**`audience_problem`（受众此刻卡在哪一步）整项缺席。**

- 该键**根本不出现**在输入里；
- 输入正文里也没有任何一句在陈述顾客的卡点；
- 该缺项**不能**由现有权威输入唯一推出：同一件马甲、同一组试穿素材，
  可以对应"不知道叠穿会不会显拥挤""不知道值不值这个价""不知道什么天气穿得上"
  等互不等价的卡点，现有输入不足以唯一确定一个。

其余五项（`objective`／`expected_change`／`content_promise`／`facts_registered`／
`expression_subject_and_boundary`）齐备，因此这是**单一缺口**，
对应 Founder PASS 条件里的"唯一关键缺口"。

## 三、保留带引号的等价书写形式

按 Founder 要求保留引号形式。原探针把 ASCII 单引号放在 `audience_problem` 的值里；
本负例该字段整项缺席，故把引号放在保留字段 `facts_registered` 的值里：

```text
…VID-C01 试穿记录二里'三层叠穿'那一组的观察（确认人苏禾）…
```

书写形态与 `yaml_with_quote` 一致：`键: 值` 平铺，值内含 ASCII 单引号。

## 四、冻结输入（逐字，调用时原样发送）

```text
objective: 让顾客理解针织马甲在通勤衣橱里承担什么任务
expected_change: 看完后能自己判断要不要把这件马甲放进当季衣橱
content_promise: 讲清楚这件马甲在什么条件下成立、什么条件下不成立
facts_registered: XQ-2504 燕麦针织马甲已登记材质、版型与680元售价，确认人周宁；DOC-B01 周宁选品比较表；VID-C01 试穿记录二里'三层叠穿'那一组的观察，确认人苏禾；未登记保暖温度范围
expression_subject_and_boundary: 周宁出镜，保持本人选品判断与语言习惯；不得包装成真实顾客案例；不写未登记的保暖温度范围
```

`professional_input` 传空串，与正例探针一致。路由 `CONTENT_BRIEF`，与正例探针一致。

## 五、冻结预期（`PASS` 需五条全部成立）

| # | 判据 | 判定方式 |
|---|---|---|
| `N1` | parser／envelope 如实识别缺口 | 缺口指向受众问题／顾客卡点；**不得**只报解析错误，**不得**把缺口指向引号所在的 `facts_registered` |
| `N2` | 返回组件级 Return、`UNKNOWN` 或 `NOT_DELIVERED` | `component_return == true` 或 `business_delivery_outcome ∈ {UNKNOWN, NOT_DELIVERED}` |
| `N3` | 不产出可进入生产的成品 | `artifact` 为空，或其中 `脚本`／`分镜`／`标题`／`文案`／`口播`／`镜头`／`封面`／`发布包装` 计数全为 0 |
| `N4` | 不自行补齐缺失事实 | 用户可见输出与产物中，**不得**出现系统自拟的顾客卡点断言；出现即 FAIL |
| `N5` | 用户可见输出自然说明唯一关键缺口 | 用户可见输出点名缺的是"讲给谁听／对方卡在哪一步"，且不出现 §0.6 泄漏集合中的内部词与「字段名: 大写值」结构行 |

**`FAIL` 条件（命中任一即 FAIL，逐条抄自 Founder 裁决 002 §四）**：
缺失关键语义仍被判可交付；自行补齐事实、商品、方向或权限；生成可进入生产的成品；
parser 因引号形式产生与输入语义无关的错误。

## 六、调用纪律（冻结）

```yaml
runs_allowed: 1
retry_policy: 仅当纯传输失败且没有任何模型输出时，最多重试一次；重试须新 Run ID 并保存首次失败
repeat_sampling: PROHIBITED          # 禁止同输入重复采样
modify_m4: PROHIBITED
modify_frozen_criteria: PROHIBITED
checker_fix_in_place: PROHIBITED     # 检查器修复必须另出版本，不原地改 v1.0
new_full_formal_round: NOT_AUTHORIZED
evidence_overwrite: PROHIBITED       # 运行器遇同名证据文件即拒绝写入
```

## 七、结果后的状态（Founder 裁决 002 §五，执行侧不得另行解释）

- 负控制 `PASS` → `RISK-M4-030+031 = PASS / CURRENT`
- 负控制 `FAIL` → `RISK-M4-030+031 = FAIL / CURRENT`，**停在 CHECKPOINT，不在本任务内继续修复**

`task_progress: IN_PROGRESS`；`terminal_state`: 留空；`main_merge: NOT_ALLOWED`。
