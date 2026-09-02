---
task_id: DIYU-V1-THREE-SKU-PRODUCTIZATION-001
section: T4 · 静态自查
note: 全部检查为零模型调用的确定性核验：sha256 比对、yaml.safe_load 结构解析、Python 代码直接执行
---

# T4 · STATIC_SELFCHECK v1.0

## 检查一：REMOVAL_TRACE.md 每条都能套上判据

`REMOVAL_TRACE.md` 逐条标注了"对应 OUT_OF_CONTRACT 项"列（①②③或对齐表第 3 项），每条删除都能回指到三张对齐表其中一行的 `OUT_OF_CONTRACT` 判定，或标注为"机械清理"（悬空引用修复，因上一条删除产生）。**PASS**——未发现任何一条删除找不到对应判据来源。

## 检查二：两个坑都没踩

| 坑 | 核验方法 | 结果 |
|---|---|---|
| 坑一：P1 三种运行模式（`TOURNAMENT_ONLY`/`SELECTED_DIRECTION_TO_SCRIPT`/`FULL`）仍在 | `grep` SKILL_v2.0.md 与 DSL 代码，确认 `ALLOWED_RUN_MODES`/`run_mode_resolved`/「运行模式」判据表与缺省推导逻辑逐字保留，只删了表格"对应入口"列的 `ENTRY-04`/`ENTRY-05` 标签 | **PASS** |
| 坑二：P0 的 CTA 仍在 | `grep -c "CTA 三级接缝"` SKILL_v2.0.md 命中 2 处（正文标题 1 + 历史改动日志提及 1）；`cta_surface`/三级判据表/硬规则五条完整保留 | **PASS** |

## 检查三：删除后三个 DSL 仍是结构完整的图

用 `yaml.safe_load` 解析三份 `*_v2_0.yml`，逐节点核验：(a) 每条 `edges` 的 `source`/`target` 都指向存在的节点；(b) 每个节点 `variables[].value_selector` 引用的上游节点与字段名都在该上游节点的声明输出里能找到（`start`/`llm`/`template-transform` 按各自隐式输出规则特判）；(c) 每个 `end` 节点的 `outputs[].value_selector` 同样核验。

```
P0:   nodes=16 edges=16  graph integrity OK
P1:   nodes=16 edges=16  graph integrity OK
P1_5: nodes=16 edges=16  graph integrity OK
```

三份文件均**无悬空引用、无断边**。**PASS**

## 检查四：T2 四条接线要求逐条实测

见 `PORT_TRACE.md`——正向控制 + 2 组独立构造的负向控制（伪造不可解析的 `fact_id`；`USER_DELIVERY` 里混入"当前最热"市场断言）对 P1、P1.5 均全部通过：结构不可旁路、下游读取关卡处理后的文本、命中即 `delivery_outcome` 真实变为 `NOT_DELIVERED_*`、P1/P1.5 均已有等价的事实登记格式（`fact_refs[].type`）。**PASS**

## 检查五：T3 新字段落地且已同步进 DSL

- `reversal_conditions[]` 在 `products/p1-creative-director/SKILL_v2.0.md`「输出」块与「自检」第 10 条各出现一次；
- `DIYU_M4_TOOL_CREATIVE_SCRIPT_v2_0.yml` 内 `grep -c "reversal_conditions\[\]"` = 2（系统提示词随 SKILL_v2.0.md 整体重新派生带入，未见遗漏）。

**PASS**

## 检查六：原树与 E1 六份基线逐字节未变

```
content-production/workflows/DIYU_M4_TOOL_PUBLISHING_PACKAGING_v1_4.yml           82cadc34...20c3  不变
content-production/workflows/DIYU_M4_TOOL_PUBLISHING_PACKAGING_v1_3_TEST.yml      daa8365d...b635e  不变
content-production/skills/packaging-content-for-release-m4/SKILL_v1.4.md         1e7a9f1a...776e   不变
content-production/workflows/DIYU_M4_TOOL_CREATIVE_SCRIPT_v1_3_TEST.yml          99e8ae5c...574b6  不变
content-production/skills/writing-creative-scripts-m4/SKILL.md                  442dc126...b08aa   不变
content-production/workflows/DIYU_M4_TOOL_PRODUCTION_DIRECTOR_v1_3_TEST.yml      a25788a3...faa1c4d 不变
content-production/skills/directing-content-production-m4/SKILL.md              b48b8840...b0dd02   不变
content-production/shared/fact-and-market-guards/MARKET_CLAIM_PATTERNS_v1.0.json dbdda0ac...874abbc 不变

products/p0-publishing-packaging/DIYU_M4_TOOL_PUBLISHING_PACKAGING_v1_4.yml       同上，不变
products/p0-publishing-packaging/SKILL_v1.4.md                                   同上，不变
products/p1-creative-director/DIYU_M4_TOOL_CREATIVE_SCRIPT_v1_3_TEST.yml         同上，不变
products/p1-creative-director/SKILL.md                                          同上，不变
products/p1_5-production-director/DIYU_M4_TOOL_PRODUCTION_DIRECTOR_v1_3_TEST.yml 同上，不变
products/p1_5-production-director/SKILL.md                                      同上，不变
```

`git status --short content-production/ account-operations/ decision-chain/` 输出为空，无任何修改标记。**PASS**

## 结论

四项检查全部 PASS。改动范围严格限制在 `products/` 下六个新增文件（三对 `SKILL_v2.0.md`/`*_v2_0.yml`），原树与 E1 六份基线逐字节未变。
