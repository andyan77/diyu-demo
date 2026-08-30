# S4 Phase C · C1 层 FAILURE TRIAGE 001

- `task_id`：`DIYU-V1-UNIFIED-DIFY-APPLICATION-001`
- 冻结规格：`unified-app/stages/S4_PHASE_C_POINT_VERIFICATION_FREEZE_v1.0.json`，sha256 `38025c9da2540729eb95ba98a2f0cfc0efdff59dee8b50713f29a02fb3afcc05`
- 冻结提交：`7e0e1d1b586c30b2251115b4dca7a3ac2d8c3d7b`（判据早于结果）
- 原始判定书：`unified-app/stages/S4_PHASE_C_RESULT_v1.0.json`，**原样保留、不改绿**
- 原始证据：`unified-app/evidence/stages/s4_phase_c/S4-PC-C1.json`
- 本文件性质：只追加登记，不修改任何判据、检查器、冻结输入或被测对象

## observed_failure

C1 六条判据 5 PASS / 1 FAIL。唯一 FAIL 是 `P1-05 没有编造夹具未提供的事实`，命中四条 `FB-07 夹具未提供的人物`：

| 命中串 | 原文上下文 |
|---|---|
| `售搭配负责人` | `苏禾（零售搭配负责人，非账号锚点）` |
| `售搭配负责人` | `账号关系姿态：苏禾＝零售搭配负责人的专业姿态` |
| `导购推荐或` | `导购推荐或临场感觉无法迁移到下一次买` |
| `负责人的专业` | `苏禾＝零售搭配负责人的专业姿态` |

## frozen_target

`P1-05`：对产物全文跑 `fabrication_probes`，任一命中即 FAIL。`FB-07 人物只能来自夹具`：白名单 `[林序, 周宁, 苏禾, 陈晚]`，抽取"紧邻职务词的 2–3 字人名"，不在白名单即 FAIL。

## candidate_sources

- `SYSTEM_UNDER_TEST`：能力真的编造了夹具外的人物
- `CHECKER_OR_FIXTURE`：FB-07 探针无法区分"人名"与"职务词旁边的任意汉字"

## confirmed_origin

`CHECKER_OR_FIXTURE`。三条独立证据：

1. **命中串是夹具自己的职务名的一部分。** `零售搭配负责人` 在夹具第五节逐字存在（`in_fixture=True`）。FB-07 的正则 `([一-龥]{2,3})\s*(创始人|店长|负责人|导购|主理人)` 只会抓职务词前面的 2–3 个字，于是把 `零售搭配负责人` 切成 `售搭配` + `负责人`，把不存在的"人名"造出来。反向那条 `(职务词)\s*([一-龥]{2,3})` 同理，把 `导购推荐或`、`负责人的专业` 当成人名。
2. **产物里出现的人物全部在白名单内。** `周宁`、`苏禾` 在场，二者都是夹具第五节的角色；`林序`、`陈晚` 未出现；没有任何白名单外的真实人名。
3. **其余五个探针零命中。** `FB-01 面料成分百分比`、`FB-02 库存销量`、`FB-03 货号 SKU`、`FB-05 预约时段` 均为空；`FB-06 价格数字` 抽出 0 个数字，"全部在夹具中"平凡成立。

即：被测对象在这一层没有编造事实，是探针把夹具原有的职务称谓误判成编造人名。

## 自检为什么没抓到

`S4_PHASE_C_SELFCHECK_v1.0.py` 的 FB-07 负控制用的是 `由店长赵婷出镜讲解`（真人名，正确翻 FAIL），但**正控制里没有一句包含夹具自己的多字职务名**（`零售搭配负责人`、`商品负责人`、`门店导购团队`）。39/39 全绿是真的，覆盖面不够也是真的——这是自检设计缺陷，不是自检执行缺陷。

## mutation_target（本轮不执行，等规划侧裁决）

`unified-app/workflows/S4_PHASE_C_ADJUDICATE_v1.0.py` 的 `FB-07` 与 `S4_PHASE_C_SELFCHECK_v1.0.py` 的正控制覆盖面。

## protected_targets（尚未证明有错，不得修改）

- 修复后的 hop `m5_compose`（`6474b902…`）与候选画布（`8c9788f2…`）
- 六个专业能力、SEAM、M1 宿主等九个受保护应用
- `S4_PHASE_C_C1_INPUT_v1.0.json` 与冻结话术
- 继承 Gate `01405ebf…` 的 C01–C12
- `P1-01` … `P1-04`、`P1-06` 五条已 PASS 的判据

## 本轮处置（按冻结停止规则）

冻结规格 `stop_rules.executor_side_defect_after_call` 原文：

> 若调用之后才发现 Runner、冻结输入、Fixture 或 Checker 有错：本轮不得重跑求 PASS。登记执行侧缺陷（含证据），把该层判为 `NOT_VERIFIED`，停在 CHECKPOINT，等规划侧裁决。

因此：

- **C1 向上登记为 `NOT_VERIFIED`**，原因 `EXECUTOR_SIDE_CHECKER_DEFECT`。不是 `PASS`，也不是被测对象的 `FAIL`。
- 机器判定书里的 `P1-05 = FAIL` 原样保留，不改绿、不覆盖。
- **不修改探针后重判求 PASS**，不重跑调用，不进入 C2、C3。
- 停在 CHECKPOINT。

## 已成立的事实（可独立复核，不依赖 P1-05）

以下五条在同一次真实调用中由确定性记录成立，与探针缺陷无关：

- `P1-01`：Content Brief 应用 `workflow_run.status=succeeded`，`skill_llm` 真实执行成功。
- `P1-02`：`capability_call` 含 `` `facts_registered` ``；其取值与 `S4-CO-T2` 的 `uapp_ctx.registered_facts` 在同一空白归一下逐字相同；`source_map` 标记 `DERIVED(registered_facts)`。
- `P1-03`：重放缺口为空；CONTENT_BRIEF 必填六项全部在场且非空。
- `P1-04`：`artifact` 7975 字，非占位；`delivery_outcome = DELIVERED`。
- `P1-06`：`user_delivery` 零内部状态词泄漏。

节点轨迹：`envelope_check → gate_sufficiency → ref_projection → projection_record → skill_llm → final_extract → returns_adapter → projection_gate → delivery_finalize → binding_record → end_ok`，全部 `succeeded`。

**`gate_sufficiency` 通过而没有停在输入不足**，是修复后事实真正抵达能力的直接行为证据——修复之前，这条链在这一步就停住并返回空产物。

这五条**不构成** C1 的 `PASS`：`P1-05` 未被有效判定，六条判据没有全部成立。

## actual_cost（C1 层实测）

| 项 | 预算 | 实际 |
|---|---|---|
| Dify workflow runs | 1 | 1 |
| nested app runs | 0 | 0 |
| DeepSeek LLM 节点尝试 | 预期 1 / 上限 2 | 1（`skill_llm` 成功） |
| 失败尝试 | — | 0 |
| 重试 | ≤1（仅纯传输失败） | 0 |
| 耗时 | — | 73.32s |

C2、C3 未发起，累计消耗 = C1 单层消耗。

## 需要规划侧裁决的事项

1. 是否授权建立 `FB-07` 的后继版本（新版本号，旧版不覆盖），使其能区分人名与职务称谓，并在自检正控制中补入夹具自身的多字职务名；
2. 若授权，是否允许对**已经落盘的同一份 C1 证据**做零模型调用的定向重判（不重跑调用、不改冻结输入、不改被测对象），再按原顺序继续 C2、C3。

两项均为判据侧变更，执行侧不自行决定。
