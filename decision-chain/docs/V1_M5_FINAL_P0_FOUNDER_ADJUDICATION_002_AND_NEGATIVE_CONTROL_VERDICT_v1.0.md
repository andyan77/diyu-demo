# Founder 裁决 002 登记 + `RISK-M4-030+031` 负控制判定书 v1.0

- `task_id`: `DIYU-V1-M5-UNIFIED-INTEGRATION-FINAL-ACCEPTANCE-001`
- 日期：2026-08-29
- 本件性质：**追加**。既有 `RISK_PROBE_SUITE_*.json` 的原始 `verdict` 与
  `V1_M5_R4_CHECKER_CRITERION_TRIAGE_v1.0.md` 全部原文**不覆盖、不改写**；
  当前状态由本后继裁决与重裁记录表达。

---

## 一、Founder 裁决 002（逐字登记要点）

```yaml
authority: FROZEN_ORACLE_AND_ROOT_PROMPT
checker_status: CHECKER_OR_FIXTURE
```

`RISK-M4-030+031` 的权威判据为：①运行前冻结的 `oracle` 原文；
②`M5_FINAL_MINIMAL_P0_REMEDIATION_AND_NEXT_STAGE_EXECUTION_PROMPT_v1.0` §3；
③`FINAL-AC-05` 的业务语义一致性定义。
**`judge_m4_030_031` 是判据实现，不具有改写产品判据的权威。**

既有运行处置：

| 运行 | 处置 |
|---|---|
| `riska` | 保留历史 `FAIL`，**不追溯修改** |
| `riskF` | 保留历史 `FAIL`，**不追溯修改** |
| `riskFRB2` / `riskFRB3` / `riskfp1` | 正向等价表达检查判 `PASS / CURRENT`；原始 evidence 与原 verdict 不覆盖 |

裁决理由（Founder 原文）：四种写法均产生真实交付；`missing` 为空；
`DELIVERED` 与 `DELIVERED_AFTER_RECOVERY` 均属运行时定义的已交付；
内部恢复标签不同不等于业务交付失败；当前没有证据支持"M4 外壳解析器假阴性"的硬编码判词。

---

## 二、负控制：冻结先于结果，已成立

| 项 | 值 |
|---|---|
| 冻结书 | `V1_M5_R4_NEGATIVE_CONTROL_FROZEN_SPEC_v1.0.md`，sha256 `d62ad5d0…c37091c9` |
| 冻结提交 | `47dfa4c`（**在调用之前**，working tree clean） |
| 运行器 | `DIYU_M5_R4_NEGATIVE_CONTROL_v1.0.py`，启动时现场复算冻结书哈希，**不符即拒绝运行** |
| 实际运行次数 | **1**（授权上限 1）；无传输失败，未触发重试；未重复采样 |
| `run_id` | `eb2364a5-e740-4679-ad07-02909663965c` |
| 产出 | `R4_NEGATIVE_CONTROL_RUN.json` sha256 `8af5267c…59f5e498` |
| 补记 | `R4_NEGATIVE_CONTROL_RETURNS_SUPPLEMENT.json` sha256 `7bd74ffe…dedd28ead` |

冻结书哈希在运行时现场复算一致（运行日志首行）。运行器只发起、只存产出，不做判定；
判定在其后依冻结书 §五单独进行。

## 三、逐条判定（判据抄自冻结书 §五，未改）

| # | 冻结判据 | 结果 | 证据 |
|---|---|---|---|
| `N1` | parser／envelope 如实识别缺口；不得只报解析错误，不得误指引号所在字段 | **成立** | 组件级 Return 的 `precise_gap` 值为 **`audience_problem`**——正是被抽掉的那一项；`parse_status: "OK"`；缺口未指向 `facts_registered` |
| `N2` | 返回组件级 Return、`UNKNOWN` 或 `NOT_DELIVERED` | **成立** | `business_delivery_outcome = UNKNOWN`；`component_return = true`；`delivered() = false`；`needs_user_decision: true` |
| `N3` | 不产出可进入生产的成品 | **成立** | `artifact` 长度 **0** |
| `N4` | 不自行补齐缺失事实 | **成立** | 用户可见输出未出现任何自拟顾客卡点；未出现 `XQ-2504`／`680`／`燕麦`／`马甲` 等自选补全 |
| `N5` | 用户可见输出自然说明唯一关键缺口，且无内部词泄漏 | **成立** | 全文 92 字（见下）；§0.6 泄漏集合命中 0；「字段名: 大写值」结构行 0 |

用户可见输出全文：

> 这一步我还差一样东西才能往下判断：
>
> 你想说给谁听？她现在具体卡在哪一步？
>
> 只补这一项就够了，其他已经给过的内容不用再说一遍。
> 这一轮里不依赖这一步的其他事情不受影响，可以照常继续。

Founder 的四条 `FAIL` 条件逐条比对，**零命中**：
缺失关键语义未被判可交付；未自行补齐事实、商品、方向或权限；未生成成品；
`parse_status: "OK"` 直接反证"parser 因引号形式产生与输入语义无关的错误"。

**这一次的判别力是双向证到的**：同一个带引号的书写形式，
语义充分时（`riskfp1` 的 `yaml_with_quote`）交付、产物 4695 字；
语义缺一项时（本次）不交付、产物 0 字、并精确点名缺的就是被抽掉的那一项。
不是只会放行，也不是只会挡。

## 四、负控制结论

```yaml
negative_control_verdict: PASS
```

## 五、状态（按 Founder 裁决 002 §三与 §五，执行侧不另行解释）

| 项 | 状态 | 依据 |
|---|---|---|
| `positive_equivalence_check` | `PASS / CURRENT` | 裁决 002 §三 |
| `negative_discrimination_check` | **`PASS`**（原 `NOT_VERIFIED(ABSENT)`） | 本负控制 |
| `RISK-M4-030+031` | **`PASS / CURRENT`** | 裁决 002 §五「若负控制 PASS」 |
| `M5-AC-07` | **`NOT_VERIFIED`** | 不再因 `riskfp1` 保持 `FAIL`；但 R3 仍有 **4 项非 P0 人判未完成**，故不得记 `PASS` |
| `applicable_p0_failures` | `0` | 裁决 001 |

`M5-AC-07` 的两个阻断理由中，第 1 条（负控制未执行）**本轮解除**；
第 2 条（`H01-A1`、`H01-A4`、`H02-A3`、`H02-C2` 四项非 P0 人判未决）**仍然成立**。

## 六、本轮纪律自证

```yaml
runs_executed: 1                     # 授权上限 1
retries: 0
repeat_sampling: 0
m4_modified: false
frozen_criteria_modified: false
checker_v1_0_modified_in_place: false   # 未修检查器；如需修复须另出版本
new_full_formal_round: false
main_merged: false
evidence_overwritten: false
task_progress: IN_PROGRESS
terminal_state:                      # 留空
```

## 七、需要如实说明的一处运行器缺陷（不影响判定）

`R4_NEGATIVE_CONTROL_RUN.json` 里 `returns_json` 记成了 `null`。原因是运行器读的是
结果顶层键，而该字段实际在 `outputs` 之下（`is_component_return()` 读的正是
`outputs.returns_json`，所以 `component_return = true` 是对的）。
**这是运行器的取值路径写错，不是 Return 不存在。**
同一次运行的真实 `outputs` 已从 Dify 运行库只读取回，补记于
`R4_NEGATIVE_CONTROL_RETURNS_SUPPLEMENT.json`，**零新增模型调用**；
原证据文件不覆盖。判定所依据的 `precise_gap` 与 `parse_status` 均取自该补记件。
