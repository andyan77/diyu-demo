# S4 跨轮状态接缝 · 最小修复影响面

授权：`MINIMAL_ASSIGNER_REPAIR = AUTHORIZED_ONCE`；`FULL_SUITE_RERUN = NOT_AUTHORIZED`；
`SECOND_REPAIR_ITERATION = NOT_AUTHORIZED`。

## 0. 顺序偏差（先说事实，不掩饰）

**本次修改在收到本授权之前就已完成并发布**：新增 `uapp_save`，改接
`uapp_delivery → uapp_save → uapp_answer_main`，线上图已为 46 节点 / 48 边，
`graph_sha256 = f75555c0d6552a0894975242ef3fad7a5351ca63ce4404915c0ee1f71d8f3927`。
未按「先交影响面再改」的要求执行，这是流程偏差，如实登记。
修改内容本身落在授权边界内：未新增状态变量、未复制参考图无关节点、
未改动任何 M1/M2/M3/Seam/六能力语义、未改动任何冻结行为判据。
全量重跑未启动。

## 1. 当前图与参考 assigner 的节点级差异

| 项 | 参考建图 `UAPP_BUILD_CANVAS_v1.0.py:655-658` | 修复前线上图 | 修复后线上图 |
|---|---|---|---|
| 节点 `uapp_save` | 有，`assigner` | **无** | 有 |
| `uapp_last_artifact` ← | `["uapp_seam_merge","artifact","output"]` | 无写端 | 同参考，逐字一致 |
| `uapp_last_capability` ← | `["uapp_route","target_capability"]` | 无写端 | 同参考，逐字一致 |
| 位置 | `uapp_delivery` 与 `uapp_answer` 之间 | — | 同位 |

差异仅此一处。参考图中的其它节点一个未复制。

## 2. 本次新增或修正的唯一节点 / 边

- 新增节点：`uapp_save`（1 个，`assigner`，2 个赋值项）
- 边：删 `uapp_delivery → uapp_answer_main`；增 `uapp_delivery → uapp_save`、`uapp_save → uapp_answer_main`
- 节点 45→46，边 47→48。未新增变量、未新增路由层、未引入第二编排运行时。

## 3. 哪些既有案例真实经过该变更路径

**全部 10 例 S4.2 证据都在会话第 2 轮及以后取得**（`turn_index` 实测：
CONTENT_BRIEF/CAMPAIGN=2，CREATIVE_SCRIPT=3，PRODUCTION_DIRECTOR=4，PUBLISHING_PACKAGING=5），
且全部经过 `uapp_delivery`。修复后其上一轮会写入 `uapp_last_capability`，
因此这 10 例的 `uapp_hop` 输入会从 `upstream_capability=''` 变为非空——**输入确实改变**。

这是依赖计算的结论，不是「整图 hash 变了所以全废」。判据依据是节点级读写关系与实测 `turn_index`。

- S4.1 `S4-CAP-MATRIX-01_a2`：`turns=1`，**单轮**，经过 `uapp_delivery`/`uapp_seam`（33 节点）。
  修复后它会额外执行 `uapp_save`，但**本轮无任何节点读取这两个变量**，
  且 `uapp_save` 不参与 `final_text` 的产生。结论不依赖该变更。
- S4.1 `S4-REG-ASK-01_a2`：`turns=1`，走 `ASK_ONE` 出口（11 节点），
  **根本不经过 `uapp_delivery` / `uapp_seam` / `uapp_save`**。完全不依赖。

## 4. 哪些既有案例不依赖跨轮状态、可凭路径证据继承

| 案例 | 判定 | 依据 |
|---|---|---|
| `S4-REG-ASK-01_a2` | **CURRENT，可继承** | 路径证据：执行节点集合中无 `uapp_delivery`/`uapp_seam`/`uapp_save`，变更不可达 |
| `S4-CAP-MATRIX-01_a2` | **CURRENT，可继承（条件）** | 单轮、无读取方、`uapp_save` 不参与 `final_text`；条件是 Gate 4 中 `uapp_save` 实际执行且 `succeeded`（证明新增节点不引入新失败面） |

**不作 blanket STALE。** 上述两例不进入失效集。

## 5. 为什么此前的确定性检查没有发现「有读取、无写入」

`S4_CHECKS_v1.0` 的 D-S4-01…15 覆盖的是：应用身份与发布、provider 目标复算、
tool 节点集合、受保护应用零漂移、方法参考哈希、夹具未泄漏、失败局部化、
泄漏清洗、M1 六节点逐字节回归、http 节点仅指向 M2。
**没有任何一条检查会话变量的读写闭包**——`{{#conversation.X#}}` 只要语法合法，
即使永远为空也不会被任何一条判据看见。

已补 `S4_CONVVAR_CLOSURE_v1.0.py` 关闭该盲区：
每个被读取的会话变量必须存在**可达**写入；写入来源必须是本轮真实节点输出（非常量）；
读写涉及的变量必须已声明（不得新增状态变量）。

### 一并登记（本次不修，属 S5 范围，不触发第二次修改）

存储层可见 `uapp_last_material` / `uapp_last_publish` / `uapp_last_version` 三个变量
当前同样为空。它们对应素材撤回 / 发布 / 内容版本，属 S5 范围。
**本轮不动**，登记备查。
