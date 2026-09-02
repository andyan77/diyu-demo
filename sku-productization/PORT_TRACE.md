---
task_id: DIYU-V1-THREE-SKU-PRODUCTIZATION-001
section: T2 · 把防编造关卡照搬给 P1 与 P1.5
note: 移植的两道代码关卡对 P0/P1/P1.5 逐字节相同（仅 CAPABILITY 常量不同），机械移植前逐个确认四条接线要求，独立构造测试向量执行节点代码验证，未复用 P0 的用例
---

# T2 · PORT_TRACE v1.0

## 移植内容

从 P0（`DIYU_M4_TOOL_PUBLISHING_PACKAGING_v1_4.yml`）逐字节复制两个 code 节点到 P1、P1.5：

- `fact_verification`（B-02，事实核验：核验 `---M4_FACT_LEDGER---` 块里每个 `fact_id` 能否在本次输入原文（`capability_call`+`professional_input`）里找到，找不到即 `fact_gate_blocked=true` 并改写 `---M4_USER_DELIVERY---` 为阻断说明）
- `market_claim_scan`（B-04，市场断言检测：命中 `core/guards/MARKET_CLAIM_PATTERNS_v1.0.json` 的 70 条模式即 `market_claim_blocked=true` 并改写用户交付块）

两节点代码在 P0/P1/P1.5 三份源文件里逐字节相同（无 `CAPABILITY` 或其他 SKU 专属常量），复制时未作任何修改。

## 接线位置

```
final_extract → fact_verification → market_claim_scan → returns_adapter → projection_gate → {recovery_llm→}delivery_finalize → end_ok
```

P1、P1.5 原图为 `final_extract → returns_adapter` 直连；插入两节点后改为上述链路，`returns_adapter` 的输入从 `final_extract.output` 改读 `market_claim_scan.verified_text`；`delivery_finalize` 新增 `fact_gate_blocked`（读 `fact_verification.fact_gate_blocked`）、`market_claim_blocked`（读 `market_claim_scan.market_claim_blocked`）两个输入，据此在 `fact_blocked or market_blocked` 时强制 `delivery_outcome` 为 `NOT_DELIVERED_FACT_CHECK_BLOCKED`/`NOT_DELIVERED_MARKET_CLAIM_BLOCKED`/`NOT_DELIVERED_FACT_AND_MARKET_CLAIM_BLOCKED`（与 P0 完全同型，代码取自 P0 移植）。

DSL 用户角色提示词同步新增 `---M4_FACT_LEDGER---...---END_M4_FACT_LEDGER---` 输出格式规格（三行：`output_location`/`factual_claim`/`fact_id`），并把原有的自检"三条"改"四条"，新增第 4 条核对 `FACT_LEDGER` 完整性——与 P0 现有格式同型，措辞按各自 SKU 的字段命名调整（P1 对照自身 `fact_refs[]`；P1.5 对照上游给的 `fact_refs[]`，见下方 (d)）。

## 四条接线要求逐条实测（独立构造用例，直接执行节点代码）

测试脚本：从 P1/P1.5 的 `DIYU_M4_TOOL_*_v2_0.yml` 里用 `yaml.safe_load` 取出四个节点的 `code` 字符串，`exec()` 后直接调用其 `main()`，构造与 S1-S4/P0 报告完全独立的测试文本（`QA-TEST-FACT-777`/`当前最热` 等，未出现在任何既往测试用例中）。

| 要求 | P1 结果 | P1.5 结果 |
|---|---|---|
| (a) 关卡必须夹在"专业产出"与"最终交付"之间，不能旁路 | **PASS**（结构核验）——`edges` 列表里唯一路径为 `final_extract→fact_verification→market_claim_scan→returns_adapter→...→delivery_finalize→end_ok`，无绕过两节点直达 `returns_adapter`/`delivery_finalize`/`end_ok` 的边 | 同 P1，**PASS** |
| (b) 下游读的必须是关卡处理后的文本 | **PASS**（代码执行核验）——`returns_adapter.variables` 唯一输入 `final_text` 绑定的是 `market_claim_scan.verified_text`（非 `final_extract.output`）；负向控制中人为在 `fact_verification` 输出里插入阻断文案后，`market_claim_scan`/`returns_adapter` 收到的都是被改写后的文本，非原文 | 同 P1，**PASS** |
| (c) 命中时交付状态必须真的变成未交付，不是记一笔照常输出 | **PASS**——负向控制 A（伪造一个不在输入里的 `fact_id`）：`fact_gate_blocked="true"` → `delivery_finalize` 返回 `delivery_outcome="NOT_DELIVERED_FACT_CHECK_BLOCKED"`；负向控制 B（`USER_DELIVERY` 里混入"当前最热"）：`market_claim_blocked="true"` → `delivery_outcome="NOT_DELIVERED_MARKET_CLAIM_BLOCKED"`；正向控制（合法 `fact_id`、无市场断言）：两项均 `false` → `delivery_outcome="DELIVERED"` | 同上三组控制结果完全一致，**PASS** |
| (d) P1 已有 `fact_refs[]`（含 `type`），P1.5 有没有等价物？ | P1 本就有 `fact_refs[].type`（EXTERNAL/INTERNAL/SUBJECTIVE/KNOWN_UNKNOWN/SETTING），无需新增格式 | **P1.5 已有等价物**：P1.5「输入」表第 `fact_refs[]` 行本就写着"含 `type`：按 type 区别对待……"（继承自 Creative Script 的两问表 type 分类体系，作为上游输入接收），本轮**未新增**任何事实登记格式；只在「输出」块新增了 `fact_check_status` 一个新字段（见下方"允许的必要改动"） |

四组测试（正向控制 + 2 组负向控制 + 结构核验）对 P1、P1.5 均全部通过，测试脚本与四组断言见 `/tmp` 会话脚本 `t2_verify.py`（未落盘进仓库，运行记录见本文档）。

## 允许的必要改动（T2(d) 范围内）

只做了一处"为使契约可被代码强制执行而必需"的 SKILL.md 改动，两个 SKU 相同性质：

- P1：「输出」块 `fact_refs[]` 行后新增 `fact_check_status` 字段（PASS/FAIL/NOT_VERIFIED），自检新增第 11 条；
- P1.5：「输出」块 `missing[]` 之前新增 `fact_check_status` 字段，自检新增第 16 条。

两处新增字段单纯是把 `fact_verification` 代码判定的结果显式暴露给客户（照抄 P0 既有 `fact_check_status` 字段的先例），**没有**对任何一条既有专业判据、提示词措辞做提升文案质量目的的改动。

## 未复用 P0 测试用例的说明

测试向量（`objective: 独立构造测试输入 A9X7`、`fact_id: QA-TEST-FACT-777`/`QA-TEST-FACT-DOES-NOT-EXIST-999`、"当前最热的赛道就是这个方向"）均为本轮任务内新写，未引用 S1-S4/S5/E1 报告中出现过的任何测试字符串或 fixture。
