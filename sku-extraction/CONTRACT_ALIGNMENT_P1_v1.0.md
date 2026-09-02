# P1 内容创意总监 · 产品合同对齐表 v1.0（E1-2）

```yaml
task_id: DIYU-V1-THREE-SKU-EXTRACTION-001
sku: P1
gate_table_core_judgment: 这条内容到底值得怎么做
standard: Q-COMM-05_P1_内容创意总监商业化评价验收标准_v1.0.md（ec6871f0…9e6）
tested_object: products/p1-creative-director/DIYU_M4_TOOL_CREATIVE_SCRIPT_v1_3_TEST.yml（未修，代码层面一行未动）
note: 登记不修。P1 与 P0 v1_3 起点相同，尚未走过任何一轮阻断修复。
```

## §1 商业产品合同

| 标准条款 | 判定 | 实际做的事 / 出处 |
|---|---|---|
| 用户购买"值得怎么做→哪些真正不同的合法方向→选哪个→为什么→怎样兑现成脚本"的专业创意决策 | `MATCH` | CS-1（创意方向差异必须是机制差异，五轴判据）+ `creative_concept`（"选中的方向 + 为什么选它，指名具体判据"）+ CS-4 三区标注支撑脚本兑现 |
| 最低合法输入：内容任务 + 主要目标/受众 + 可用事实与素材 + 真正影响创意路线的边界 | `PARTIAL` | `envelope_check.REQUIRED`（`objective`/`expected_change`/`content_promise`/`expression_subject`/`content_origin_mode`/`facts_registered`）与标准四要素**命名不对齐**：`objective`≈主要目标，`facts_registered`≈可用事实，但"受众"对应哪个字面 key 不确定（`audience_shift` 不在 `REQUIRED` 六项里，只是「输入」表里的一个可选槽位）；"真正影响创意路线的边界" 在 `REQUIRED` 里没有直接对应字段（`explicit_non_promise` 更接近"不承诺什么"而非"创意路线边界"）。同 P0 的 §1.2 问题：字面英文 key 匹配可能与标准的自然语言描述脱节 |
| 支持三种合法入口 A（只做方向比较）/B（已有方向→脚本）/C（任务→取舍→脚本） | `MATCH` | 「运行模式」节 `cs_run_mode ∈ {TOURNAMENT_ONLY, SELECTED_DIRECTION_TO_SCRIPT, FULL}`，三种模式与标准 A/B/C 一一对应，且明文"系统里只有这一处锦标赛代码路径"（防止重复发散） |
| 不得强制所有任务固定数量候选；没有真实取舍则一个方向即可 | `MATCH` | CS-1"数量由是否存在真实取舍决定，不固定、不设上下限"；`creative_directions[]` 字段说明"不存在真实取舍时候选数=1，并写清为什么不存在真实取舍"；自检第 4 条同步要求候选数=1 时必须说明理由 |

## §2 明确不负责

| 标准条款 | 判定 | 说明 |
|---|---|---|
| 不负责实际摄影、分镜制片、剪辑、封面与发布包装、自动发布、长期账号经营 | `MATCH` | Skill 正文明文"不做：分镜、机位、剪辑节奏、封面、标题、发布文案。那是下游两段的事" |
| 若用当前市场稀缺度作推荐理由，须存在对应 Market Observation | `MISSING` | DSL 内无任何机制核验"当前市场稀缺度"类推荐理由是否真的挂着一条 Market Observation——`envelope_check`/`returns_adapter` 均不含此项检查；仅在 SKILL.md 提示词层面隐含"无市场证据不得声称当前热门"的一般性要求（见下一行），但没有针对"如果用了就必须带证据"这一条件句的专门核验 |

## §6 G1｜硬错误 Gate

| 标准条款 | 判定 | 实际做的事 / 出处 |
|---|---|---|
| Critical Error = 0（编造产品/人物/品牌事实） | `PARTIAL` | CS-7"不编造、也不删减输入里的取舍"在提示词层面极为详尽（列出 6 种比"编一个假事实"更难发现的编造方式：关联编造/位置搬错/编造沉默/补身份/单侧删除），但**代码层面没有任何独立核验**——P1 的 DSL 没有 `fact_verification` 或等价节点，`returns_adapter` 不解析事实字段。相较 P0 v1_4（有窄范围代码核验），P1 目前仍停留在"唯一把关者是模型自己"这一更早的架构状态 |
| UNKNOWN → FACT 不得发生 | `PARTIAL` | 同上，仅提示词层面的纪律（`KNOWN_UNKNOWN`/`fact_refs[].type` 分类体系），无代码级传播/核验机制 |
| 无市场证据声称"当前热门/稀缺/竞争机会" | `MISSING` | **P1 的 DSL 没有 `market_claim_scan` 或任何等价机制**——`returns_adapter.LEAK_PATTERNS` 三 SKU 逐字节相同，从未包含"当前最热""现在最流行"一类市场断言模式（这些模式目前只接入了 P0）。标准 §6 明文把这一条列为硬错误（Critical Error=0 的一部分），DSL 侧完全没有代码防线，纯靠模型自觉 |
| 方向违反明确品牌或事实边界 | `MATCH`（提示词层面） | `explicit_non_promise[]` 只读继承机制（「与统一能力接缝的对接」节） |
| 推荐理由依赖并不存在的资源 | `PARTIAL` | M8"现实可执行性"作为 G2 评分维度存在，但无对应的结构化输出字段或代码检查专门核验"资源是否真实存在" |

## OUT_OF_CONTRACT（DSL 做了标准不要求的事）

| 项 | 说明 |
|---|---|
| `return_from_downstream[]` 闭环三选一处置、`downstream_stale[]` | 与 P0 同一 M4 接缝残留基础设施，Q-COMM-05 全文未要求"向下游发出/接收结构化回改" |
| `binding_record`（AC-12 保真绑定记录） | 同 P0，纯工程可追溯性记录，非产品合同条款 |
| `entry`/`cs_run_mode` 的 `ENTRY-04`/`ENTRY-05` 显式协议字段 | 同 P0，统一能力路由协议残留 |

## 小计

`MATCH`: 5　`PARTIAL`: 4（最低输入命名不对齐、编造事实/UNKNOWN 无代码核验两项、推荐理由资源真实性无结构化核验）　`MISSING`: 2（市场稀缺度推荐理由未核验证据挂载、无市场证据当前热门断言零代码防线）　`OUT_OF_CONTRACT`: 3

**与 P0 对比的关键差异**：P0 在 S1-S4 之后，§6.1/§7 对应的两个硬错误（事实核验、市场断言）已各自获得一层窄范围代码核验；P1 完全没有走过这一轮，**两项均为 `MISSING`/`PARTIAL`**，且 `market_claim_scan` 类断言检测在 P1 上直接是 `MISSING`（零代码防线），比 P0 修复前的状态更彻底地暴露了同一类架构缺口。这印证了 THREE_WAY_COMPARISON 里"P0 已修、另两个未修"的判断——阶段二对 P1 做静态验证时，大概率会重新发现与 P0 首轮报告几乎相同的两条阻断。
