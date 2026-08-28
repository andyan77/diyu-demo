# M5 Node 3 诊断发现 · v1.0

> **证据等级：DIAGNOSTIC。** 这些运行发生在 Candidate Run Manifest 冻结**之前**，
> 按 Root Prompt Node 3.8 一律只作诊断，**不产生任何正式 PASS/FAIL**。
> 记录时间（UTC）：`2026-08-28T05:34:36Z`

## M5-DIAG-001 · 完整主故事当前不成立，最高失效节点已定位

**现象（可复现，非偶发）**

用 M4 Founder Canvas 作自然语言入口（advanced-chat，`f0b1c5f5`），三轮真实对话：

| 轮次 | 输入要点 | Canvas 回答 | 底层运行 |
|---|---|---|---|
| 1 | 完整经营诉求，**明确写了目标**「验证这个角度能不能打中人，先不追求到店或成交」 | 「任务我已经记下了」+ 让用户选能力 | Canvas run `4b98104b` |
| 2 | 「就做内容 Brief。」 | 「我还差一样东西…**这一轮你想拿到的结果是什么？**」 | Canvas run `4e3a8d0f` |
| 3 | **再次明确给出目标** | 「已按你说的目标来…**内容 Brief 现在开始做，做完后会给你确认**」 | Canvas `64e13072` → Seam `3b259648` → Content Brief Architect `e38c97da` |

**第 3 轮 Seam 运行 `3b259648` 的真实输出：**

```text
business_delivery_outcome = UNKNOWN
artifact                  = 0 字（空）
user_delivery             = 110 字，内容是「我还差一样东西…这一轮你想拿到的结果是什么？」
capabilities_skipped      = [MATRIX, CAMPAIGN, CREATIVE_SCRIPT, PRODUCTION_DIRECTOR, PUBLISHING_PACKAGING]
platform status           = succeeded
```

**两个独立缺陷**

**D-1 目标事实抽取召回不足（对应已登记风险 `RISK-M4-033`）。**
用户在第 1 轮与第 3 轮**两次**明确陈述本轮目标，能力侧仍报「缺目标」。
说明 Canvas 的意图层没有把已陈述的目标带进 `capability_call` / `professional_input`。

**D-2 用户可见层宣称的进度，与业务层结论相矛盾（新发现，比 D-1 严重）。**
同一时刻：业务真相是 `business_delivery_outcome = UNKNOWN`、`artifact` 为空、
能力侧正在回问缺失项；而 Canvas 对用户说的是「已按你说的目标来」「内容 Brief 现在开始做」。
这直接违反 M4 交接契约里被列为 **M5 必须遵守**的语义：

> 读业务结果看 `business_delivery_outcome`，不要拿平台 status 当交付成功。

平台 status 确实是 `succeeded`，但业务没有交付。用户被告知「在做了」，实际什么都没产出。
这不是措辞问题：它会让 Founder 以为拿到了 Brief，而系统其实停在回问。

**影响面**

- `M5-AC-02`（扩展完整主故事）：**当前不成立**。故事在 Content Brief 这一步就断了，
  后面的 Creative Script / Production Director / Publishing & Packaging 全部 `capabilities_skipped`。
- `M5-AC-03`（合法短入口）：`DE-05` Direct Content Brief 受同一根因影响，标 `STALE` 待复验。
- `RISK-M4-033`：诊断阶段已观察到复现证据。
- `RISK-M4-032`（内部状态泄漏）：**未**观察到泄漏；D-2 是反向问题——不是泄漏内部状态，
  而是对外宣称了业务层不支持的进度。

**最高失效节点**

Canvas 意图层 → `capability_call` 组装环节。不是 Content Brief Architect 本身：
该能力在收到形状正确的输入时工作正常——同一 Seam、同一能力，用 M4 冻结夹具
`FX-M4-CT-M3` 调用返回 `business_delivery_outcome = DELIVERED`、
`user_delivery` 2449 字的完整 Content Brief Pack（诊断运行 `175a3329`）。
**所以能力侧是好的，坏的是上游把业务实质组装成统一能力外壳这一步。**

**修复边界**

M4 的八个已发布应用受合同保护：`overwrite_or_delete_existing_m1_m4_apps = PROHIBITED`。
因此**不改** `f0b1c5f5` 等既有应用，改法只能是按
`create_or_update_task_named_m5_test_candidate = AUTHORIZED_REVERSIBLE`
另建 M5 测试候选对象，在候选里修组装环节。

## M5-DIAG-002 · M1 编译器不能脱离 Dify 影子节点单独驱动

`m1_context_compiler_v0.1.py::main()` 传 `shadow_patch={}` 时返回
`patch_ok=false`、`reject_reason=SHADOW_NODE_FAILED`。
该 Python 文件只是**确定性校验与合并器**，自然语言理解由 Dify 图里的 LLM 影子节点完成。
因此 M5 的完整故事必须以 Canvas 为自然语言入口，不能用 Python 直接编排 M1 绕过它。
（这不是缺陷，是架构事实，登记以免后续误用。）

## M5-DIAG-003 · 已成立的部分（同轮诊断中确实跑通的）

以下在同一诊断里真实成立，构成后续正式运行的基础：

- **M2 服务可用且与候选同源**：容器内应用代码哈希 `b6cd1688…` 与 M5 候选树逐字节一致。
- **反馈幂等成立**：同一 `idempotency_key` 连写两次，返回同一行
  `6dab42dc-29d5-4a8a-902c-ab0c290207c7`，未制造双份事实。
- **测试发布身份正确**：`is_test = true`、`is_simulated = true` 显式写入，
  未被伪装成真实发布。
- **Cycle N+1 成立**：`M2_cycle_next` 与 `M2_cycle_decision` 均 200，
  决策绑定 `resulting_cycle_id`，且 `based_on` 记录了反馈为测试模拟。
- **M3 两次真实运行**：`a5cc38dc`（周期判断，`gate_status=CLEAN`，1275 字）与
  `378ffd5c`（复盘，`gate_status=CLEAN`，822 字）。
- **能力可合法跳过**：MATRIX / CAMPAIGN 未被暗跑，`capabilities_skipped` 如实记录。
- **一次只进一个能力**：Seam 每次调用只落一个能力应用，六能力之间零调用边。

## 下一动作

按 Root Prompt Node 3.7「只修集成所需的最高失效节点」，在 M5 测试候选对象中修复
Canvas 意图层 → `capability_call` 的组装；既有 M4/M3 应用零改动。
修复后重跑完整主故事，仍属诊断；正式运行一律等 Candidate Run Manifest 冻结之后。
