# V1 M1→M4 多诉求接口 Rebase 建议 v0.1

```yaml
document_id: "V1_M1_M4_MULTI_REQUEST_INTERFACE_REBASE_PROPOSAL"
version: "v0.1"
role: "REBASE_PROPOSAL"          # 建议，不是合同；未被 Founder 接受前不得据此开工
raised_by_task: "V1-M4-CAPABILITY-SEAMS-RUNTIME-INTEGRATION-001"
raised_finding: "M4-FND-004"
authority_event: "RULESIDE-2026-08-26-M4-003"
status: "PROPOSED — 待 Founder 裁决"
proposes_work_in: "M1（接口生产侧）+ M4（接口消费侧），各自独立 Execution Prompt"
does_not_propose_work_in: "M4 单独完成"
```

> **一句话**：M1 每轮只能吐出**一个** `effective_route`，所以「一句话里两件事」在**接口层**就已经丢了一件，
> 不是 M4 实现得不够好。要么改这个接口，要么冻结判据里那一条永远不可能 `PASS`。

---

## 1. 为什么这是必须处理的，而不是可选增强

这不是执行侧提出的新需求。它是**已经冻结的两处判据**要求的行为：

| 来源 | 冻结时点 | 原文要求 |
|---|---|---|
| 取证判据合同 §2 `AC-06` | 结果之前 | 「② 同轮 PP 请求**正常产出**」——`FX-M4-MATRIX-INSUFFICIENT-WITH-UNRELATED` 的三条合取项之一 |
| 夹具包 v0.1 §6.2 | 结果之前 | `same_round_unrelated_request: {capability: PUBLISHING_PACKAGING, ...}`，判据写明「三条同时成立才 PASS」 |
| Founder 实测包 §场景 2b | 结果之前 | 「**判断点（这一条最重要）**……标题封面那一半：应该照常做出来，不应该被账号那半边卡住」 |

`AC-06` 的另外两条合取项已取得证据（组件级 Return 七项齐全、`precise_gap` 具体）。
**只有第 ② 条因为接口层缺口而不可能成立。** 按合取项纪律，`AC-06` 整条只能是 `NOT_VERIFIED`。

**这不是「要不要支持」的问题。** 行为已由上述三处冻结，本文件只回答**在哪一层、用多小的改动**支持它。

---

## 2. 根因：接口是标量，不是实现不够好

### 2.1 当前实际形状（现场读出，非设计文档转述）

```text
M1 v1_state (743 行，线上 graph md5 = 8def6c4f436ad989557992c59d029958)
  └─ 每轮产出：effective_route : str        ← 标量，五值枚举之一
                candidate_skill : str        ← 标量
                confirmed_task  : dict|None  ← 单条
                pending_action  : dict|None  ← 单条
                blocking_gap    : dict|None  ← 单条

M4 m4_intent_adapter (113 行)
  └─ ROUTE_TO_CAP[effective_route] → 一个 capability
  └─ 再按输入充分性落到七个入口之一

M4 capability_seam (start 节点变量)
  └─ capability : text-input, required     ← 标量
  └─ seam_dispatch : if-else → 恰好一个 tool 节点 → 恰好一个 end 节点
```

**信息在 M1 内部就已经坍缩成一个值。** 到 M4 手上时，第二件诉求已经不存在了——
不是被 M4 丢掉的，是从来没有被传过来。

### 2.2 为什么 M4 单独修不了（两条都成立，各自独立充分）

**其一，越权（A1 权威域）。** 要从「我想让苏禾和陈晚各开一个号……另外，上次那条马甲的片子素材我拿回来了」
这句话里认出**两个**诉求，必须做自然语言理解与跨诉求路由。统一能力合同 §2.2／§5.5 把这三件事
（自然语言理解、跨诉求路由、最小追问判断）明确归 M1。M4 的适配器正文里逐字写着「本节点**不做**这三件事」。

**其二，Founder 已明令禁止（RULESIDE-2026-08-26-M4-003）。** 「不得在 M4 建第二套路由」。
在 M4 里补一个能拆分诉求的东西，无论叫适配器、分流器还是编排器，都是第二套路由。

### 2.3 为什么现在这种「分别跑两次都成功」不能冒充

已有证据能证明：Matrix 单独跑会给出组件级 Return（`FA-05`），PP 单独跑会正常出标题封面（`FA-07`）。
**这两件事加起来不等于「同一轮里不互相阻断」。** 冻结判据要的是同轮不阻断，
分两轮各跑一次连这个问题都没碰到。执行侧不以此冒充 `PASS`，已在证据里如实登记。

---

## 3. 建议的接口改动（最小充分集）

### 3.1 M1 侧：把标量出口改成**有序独立项列表**

```yaml
# 现在
effective_route: "EXECUTE_MATRIX"

# 建议
effective_routes:
  - route_id: "R1"
    effective_route: "EXECUTE_MATRIX"
    independence: INDEPENDENT        # 与其他项之间**有无真实依赖**，由 M1 判定
    depends_on: []
  - route_id: "R2"
    effective_route: "EXECUTE_PUBLISHING_STAGE2"
    independence: INDEPENDENT
    depends_on: []
```

**只加三样东西**：列表化、`route_id`、`depends_on`。没有新枚举值，没有新意图类型，没有本体。

**向后兼容**：`len(effective_routes) == 1` 时行为与今天逐字节相同。
建议保留 `effective_route` 作为 `effective_routes[0].effective_route` 的只读回显，
让所有现有消费方零改动继续工作（A3：不使有证据不受影响的项失效）。

### 3.2 M1 侧：把单条状态改成按 `route_id` 分槽

`blocking_gap` / `pending_action` 今天是单条。多诉求下必须能同时表达
「R1 缺东西、R2 不缺」，否则 R1 的缺口会再次污染 R2：

```yaml
blocking_gaps:
  R1: {precise_gap: "这两个人各自平时经手哪些事、哪些是她们亲自看到的"}
  R2: null
```

`confirmed_task` / `authorization` 同理按 `route_id` 分槽。**这是本建议里唯一有实质工作量的一处。**

### 3.3 M4 侧：接缝按项 fan-out，**纯传输**

```text
m4_intent_adapter：  for item in effective_routes:  查表 → capability，按输入充分性定 entry
                     ——仍然只做「查表 + 等价输入判定」，不看用户原话，不做理解，不做路由
capability_seam：    start 变量 capability 由标量改为项列表；dispatch 由「一次一个」
                     改为「按项各走各的分支」；每项独立产出 artifact / Return / seam_trace
m4_canvas_fin：      按项汇总；**任一项的 Return 只使该项及其真实依赖项 STALE**（A3）
```

**关键纪律**：M4 侧**不新增任何判断诉求归属的代码**。`route_id` 是 M1 给的，M4 只按它分发和归集。
这是 A5 意义上的「同一套锦标赛路径」在路由上的对应物——系统内只有一处决定「这句话里有几件事」，
那一处在 M1。

### 3.4 一句话说清边界

| 谁 | 管什么 | 不管什么 |
|---|---|---|
| **M1** | 这句话里有几件事、分别是什么、彼此有没有真实依赖、每件缺什么 | 每件事内部怎么做、走哪个入口、专业产出长什么样 |
| **M4** | 每一件事内部：等价输入判定、入口解析、专业执行、局部 Return、按项失效 | 这句话里有几件事（**永远不问这个问题**） |

---

## 4. 明确**不**建议的（防跑偏）

- **不**在 M4 建第二套路由、分流器、编排器或任何等价物（Founder 明令）。
- **不**建复杂意图本体、意图分类器网络或多层 Judge（`CLAUDE.md` §4）。
- **不**建第二套工作流引擎（`CLAUDE.md` §4）。
- **不**改 M1 的自然语言理解质量、不动 `v1_shadow`——本建议只动**出口结构**，不动理解本身。
  （`M4-FND-002` 的意图分类波动是**另一件事**，本建议不捎带解决，也不因本建议而被视为已处理。）
- **不**要求诉求数量有上限或下限，**不**硬编码「一句话最多几件事」。
- **不**为了这一条重开已 `DONE` 的 M1 任务（`SBC-RF-03`）——按新任务或 M1 REBASE 处理。

---

## 5. 影响面（A3，供 Founder 判断代价）

**改了会失效的**（改动后必须定向复验，不是全盘清零）：

| 项 | 为什么 |
|---|---|
| M1 已落地 chatflow 的 `v1_state` 出口结构 | 直接改动对象 |
| 所有读 `effective_route` 的下游 | 直接依赖；保留只读回显可让这一类**零改动继续复用** |
| M4 `m4_intent_adapter` / `capability_seam` / `m4_canvas_fin` | 直接依赖 |
| `AC-06` / `AC-19` / `AC-25` 的同轮相关部分 | 判据绑定变化 |
| M2 的写回与版本反馈（按 `route_id` 分槽后，归属键变了） | **影响关系无法可靠判断 ⇒ 标 `STALE` 待定向复验**，不假装已知 |

**不会失效的**（继续复用，不重跑）：六份后继 Skill 正文、六个能力应用内部、
七个直接入口的单诉求行为、保真链 `AC-12`、九个保护应用。

**工作量诚实估计**：M1 侧 §3.2 的分槽是主要部分；§3.1 与 M4 侧 §3.3 都是机械改造。
本估计是**执行侧判断**（`推断/专业判断` 级），不是实测，不得被当作已验证。

---

## 6. 如果 Founder 决定不做

那么**必须同步做的**是把冻结判据改到与之一致，而不是让它挂着：

- `AC-06` 的合取项 ② 与夹具包 §6.2 的 `same_round_unrelated_request` 需要**版本化**为 `v0.2` 并说明理由；
- Founder 实测包 §场景 2b 需要相应修订；
- **不允许**的做法：把 `AC-06` 的判据名收窄成只剩已通过的两条然后判 `PASS`（这正是本任务
  修复轮里已被 Reviewer 判为违规、并已纠正的那一类操作）。

`AC-06` 在此之前一律 `NOT_VERIFIED`，不因为「其余两条都过了」而上推。

---

## 7. 本文件的权威等级

`推断/专业判断`。这是执行侧的建议，**不是合同，也不是已被接受的方案**。
未经 Founder 以权威事件接受前，M1 与 M4 都不得据此开工。
本文件不修改任何现有合同、判据或状态，也不把 `M4-FND-004` 从 `OPEN` 推向任何其他状态。
