# Founder 裁定登记 · `UAPP-FOUNDER-ADJUDICATION-002`｜`content_origin_mode`

`task_id: DIYU-V1-UNIFIED-DIFY-APPLICATION-001` ｜ 登记日期：2026-08-29
上游权威载体：`DIYU_V1_UAPP_S4_CONTENT_ORIGIN_CONTINUATION_EXECUTION_PROMPT_v1.0.md`

**本文件只登记裁定与它授权了什么。不复述、不加工、不替 Founder 补充理由，也不由执行侧把任何状态往上推。**

---

## 一、裁定登记（结构化，字段按上游 Prompt §3）

```yaml
adjudication_id: UAPP-FOUNDER-ADJUDICATION-002
task_id: DIYU-V1-UNIFIED-DIFY-APPLICATION-001
authority: FOUNDER
subject: content_origin_mode
decision:
  missing_behavior: "精确询问，不替用户默认"
  adjudicated_result: PASS
  scenario_value: EXISTING_MATERIAL_EDIT
  scenario_user_text: "这条使用门店已有素材剪辑，不安排重新拍摄；具体素材仍按系统里的授权记录选择，未获授权的不要使用或发布。"
  scope: "仅本次冻结测试场景与当前内容任务"
  not_a_default: true
  not_material_authorization: true
  not_a_long_term_brand_fact: true
historical_evidence:
  gate4_result: "1 PASS / 3 FAIL，原记录不覆盖、不追溯改绿"
  content_brief: "PASS；artifact 5593 字，跨轮状态写入已验证"
  creative_script: "因 content_origin_mode 缺失精确停止"
remaining_claim: "回答后 CS→PD→PP 能否继续仍为 NOT_VERIFIED"
authorized_next_action: "一次新会话六轮冻结连续验证"
```

---

## 二、这条裁定改变了什么（权威事件，不是执行侧的判断）

### 2.1 一项行为判定被有权者裁为 PASS

Creative Script 在缺少 `content_origin_mode` 时**精确追问、不替用户默认**，
此前在 `S4_2_STAGE_GATE_v1.2.json` 的「正例交付含实质内容」一项下被记为 `FAIL`。
Founder 裁定：**该追问本身是正确产品行为**，`content_origin_mode` 属于
Creative Script 开始前才可能成立的**单条内容经营决策**，当前输入未提供时不得擅自默认。

这是产品语义域（A1）的有权者事件，执行侧照单登记。

### 2.2 但裁定同时明确限制了它能推出什么

裁定第 2 条写死：**该追问不证明整条生产链已经完成。**
回答之后能否沿同一会话继续消费既有 Content Brief，**仍为 `NOT_VERIFIED`**，
必须用一次新鲜的、判据冻结在前的连续场景验证。

因此本裁定**不**触发以下任何一项（A2：非事件的变换不改变位置）：

- 不把 `S4-CAP-CREATIVE_SCRIPT-POS` 的历史 `FAIL` 改绿；
- 不把 `S4-CAP-PRODUCTION_DIRECTOR-POS` / `S4-CAP-PUBLISHING_PACKAGING-POS` 的 `FAIL` 改绿；
- 不宣告 S4、UAPP 或 M5 `DONE`；
- 不修改 `S4_2_STAGE_GATE_v1.2.json`（`c6d9d859…`）一个字节。

Gate 4 的历史记录原样保留在 `evidence/stages/s4_2_attempt04/`，**不覆盖、不追溯改绿**。

### 2.3 场景决定的边界（逐条，不得放宽）

本次冻结测试中的用户决定为：
**「使用门店已有素材剪辑，不安排重新拍摄；具体素材仍按系统现有授权记录选择，未获授权的不得使用或发布。」**

该决定：

| 是什么 | 不是什么 |
|---|---|
| 本次场景 + 当前内容任务的一次性经营决定 | **不是**系统默认值 |
| 一句 Founder 明确提供的用户输入 | **不是**长期品牌事实 |
| 对「素材从哪来」这一问的回答 | **不等于**任何具体素材已经获得授权 |

运行中**不允许**把它改写成「素材已获授权」。未获授权的素材不得被选择或发布。

---

## 三、本裁定授权的下一动作（唯一一条）

```text
一次全新 conversation，六个逐字冻结的自然语言输入，每个输入运行一次。
判据先冻结（S4_CONTENT_ORIGIN_CONTINUATION_GATE_v1.0.json），再发起调用。
运行结束落盘、提交、停在 CHECKPOINT。
```

明确 **NOT_AUTHORIZED**：十例全套重跑、CAMPAIGN 重跑、v1.2 负例身份对齐回归、
第二次接缝修复、图/Checker/Fixture 任何变更、进入 S5、合并 main。

---

## 四、与既有登记的关系

- 与 [`UAPP_FOUNDER_ADJUDICATION_001_INTENT_ROUTING.md`](UAPP_FOUNDER_ADJUDICATION_001_INTENT_ROUTING.md) 同类：
  都是产品语义域的有权者事件，执行侧只登记不辩驳。
- 承接 [`S4_2_CHECKPOINT_001.md`](S4_2_CHECKPOINT_001.md)（`760f4cad…`）中登记的三条候选下一步：
  本裁定选定并收窄了其中第 1 条，同时明确 §8.2 的行为判据**不由执行侧改动**；
  第 3 条（v1.2 负例身份对齐）仍 `NOT_AUTHORIZED`。

`END_MARKER: UAPP-FOUNDER-ADJUDICATION-002-END`
