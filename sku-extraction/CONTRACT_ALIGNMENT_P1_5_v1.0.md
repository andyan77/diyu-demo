# P1.5 内容制作导演 · 产品合同对齐表 v1.0（E1-2）

```yaml
task_id: DIYU-V1-THREE-SKU-EXTRACTION-001
sku: P1.5
gate_table_core_judgment: 这个脚本在我的条件下到底怎么拍
standard: Q-COMM-06_P1.5_内容制作导演商业化评价验收标准_v1.0.md（9a063c6d…772）
tested_object: products/p1_5-production-director/DIYU_M4_TOOL_PRODUCTION_DIRECTOR_v1_3_TEST.yml（未修，代码层面一行未动）
note: 登记不修。P1.5 与 P1 同为 v1_3 起点，尚未走过任何一轮阻断修复。
```

## §1 商业产品合同

| 标准条款 | 判定 | 实际做的事 / 出处 |
|---|---|---|
| 把已确定的脚本/内容结构，转换成当前真实资源条件下能拍出来、剪出来、交付出去的制作决策方案；不是"AI 给我列一个分镜表" | `MATCH` | `director_approaches[]`（3 套高差异方案，"什么条件下失败"）+ `capture_plan.units[]`（逐单元含目的、事实、素材）+ PD-3"先问哪些东西不能只靠说"——判断深度超过纯列表 |
| 最低合法输入：脚本/可制作内容结构 + 人员条件 + 设备条件 + 时间窗口 + 已有素材 + 制作边界 | `PARTIAL` | `envelope_check.REQUIRED`（`script_or_equivalent_beats`/`content_origin_mode`/`production_profile`/`time_window`/`content_promise`）覆盖脚本、时间窗口、部分制作边界；`production_profile` 把"人员条件"与"设备条件"合并为一个字面 key（标准里是两个独立要素），"已有素材"对应 `available_assets`——**不在 `REQUIRED` 六项里**（是「输入」表的一个槽位，缺失时可默认推进，不构成结构性阻断），与标准"已有素材"作为最低合法输入组成部分的定位不完全一致 |

## §2 标准输出（十四项）

| 标准条款 | 判定 | 实际做的事 / 出处 |
|---|---|---|
| 场景 | `MATCH` | `scene_and_action`（在哪拍） |
| 动作 | `MATCH` | `scene_and_action`（人在里面做什么）+ `capture_plan.units[]` |
| 镜头 | `MATCH` | `capture_plan.units[]`（`unit_type` 含 `SHOT` 等七种） |
| 每个镜头的目的 | `MATCH` | `capture_plan.units[]` 逐单元"这个单元的目的"字段 |
| 表演指导 | `MATCH` | `performance_direction`（七维度齐全，PD-1 明文"必须具体到能照做"） |
| 拍摄顺序 | `MATCH` | `shooting_order` |
| 素材清单 | `MATCH` | `asset_list[]`（含"素材"四态标注） |
| 声音设计 | `MATCH` | `sound_design` |
| 剪辑节奏 | `MATCH` | `edit_structure`（段落划分/转折点秒数/平均镜头长度/呼吸位） |
| 必拍/可删区分 | `PARTIAL` | 无独立的"必拍/可删"布尔字段；靠 PD-2"每个镜头为什么存在？如果删除镜头后没有任何影响：应删"这一提示词层面的判断规则实现，`capture_plan.units[]` 没有为此单列一个可机读的枚举值 |
| 关键连续性要求 | `PARTIAL` | 图内有"并置检查"机制（自检第 11 条"相邻的两个单元、同屏的两块内容……观众读出的那条关系，有来源吗"），但**这检查的是"相邻单元间是否暗示了无来源的事实关联"（PD-2 附加①的编造问题），不是经典意义上的"道具/服装/位置跨镜头一致性"**——未找到后者的专门检查机制，两者是相关但不同的概念，不应互相顶替 |
| 补拍要求 | `MATCH` | `pickup_list[]`（"必须留到剪辑后补拍/补录的"） |
| 资源不足时的替代方案 | `MATCH` | `low_resource_version`（明文"完整，不是差异说明"）+ PD-7"低资源版不是降级，是换打法" |
| 开拍前仍需确认的阻塞项 | `MATCH` | `missing[]`（"还缺什么才能继续"） |

## §7 G1｜制作可行性硬门

| 标准条款 | 判定 | 实际做的事 / 出处 |
|---|---|---|
| 使用不存在的人员/未提供设备/时间计划物理不可能/人员时间冲突/场景矛盾/必需素材未拍却假设存在/UNKNOWN 被当成已具备资源 | `PARTIAL` | `envelope_check` 对 `production_profile`/`time_window`/`available_assets` 做结构性在场检查（防止完全缺失），但**这些冲突/矛盾的检测（"同一人员同一时间承担冲突角色""场景条件互相矛盾"）依赖模型的专业判断（PD-3"先问哪些东西不能只靠说"），没有独立于模型的代码级交叉校验**——例如没有代码检查"两个 `unit_id` 是否声称同一人员同时出现在两个场景" |
| 明显安全风险未识别 | `MISSING` | 未找到专门的安全风险关键词扫描或结构化字段；完全依赖模型在 `constraints[]`/`failure_case` 里主动识别 |

## OUT_OF_CONTRACT（DSL 做了标准不要求的事）

| 项 | 说明 |
|---|---|
| `return_to_script[]`（七项闭环回改建议） | 同 P0/P1，M4 接缝残留基础设施；标准 Q-COMM-06 全文未要求向 Creative Script 发起结构化回改 |
| `binding_record`（AC-12 保真绑定记录） | 同上，纯工程可追溯性记录 |
| `subject_domain`/`content_origin_mode[]` 原样透传给下游 | 服务于 M4 跨组件数据流转协议（Publishing 也要按同一 `subject_domain` 加载 industry-conditions.md），标准本身只关心 P1.5 自己的制作决策产出，不要求它承担"为下游透传字段"这一职能——这是统一能力链设计的产物，不是 Q-COMM-06 明确要求的商品价值 |

## 小计

`MATCH`: 12　`PARTIAL`: 4（最低输入"已有素材"未入结构性必填、必拍可删无独立字段、关键连续性概念不完全对应、制作可行性冲突检测无代码交叉校验）　`MISSING`: 1（安全风险识别无结构化机制）　`OUT_OF_CONTRACT`: 3

**与另两个 SKU 对比**：P1.5 在 §2 标准输出十四项上的覆盖率最高（12/14 `MATCH`），说明其输出契约相对标准定义最贴合；但 §7 G1 硬门（制作可行性冲突检测、安全风险识别）与 P1/P0 面临同一类问题——专业判断规则详尽，但缺乏独立于模型的代码级交叉校验，这与 P0 v1_3 时代"唯一把关者是模型自己"的架构状态一致。
