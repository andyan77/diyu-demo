# A3 影响面核算：施工期间 `main` 前进了，而且动到了 M3 绑定的模块

> 这份不是可选的补充说明。A3 要求「绑定任一变化 ⇒ 其已知直接依赖、传递依赖，以及影响关系
> 无法可靠判断的项，一并置 `STALE`」，**多算和少算都是错**。下面把这次变化逐条算清。

## 1. 事实

```text
入场基线（本任务分支的 merge-base）  df2c5952551f386a0e9a509404357f23c1d223c9
当前 main                            a7b810109f43a4bf500acc285baab477d96796e3
本任务 HEAD                          6bbad987b5d22fbf5c8c8f15aa9aed48316ad119
```

本任务分支相对**入场基线**：373 个文件，**全部 `A`（新增）**，0 修改、0 删除。
受保护目录里只多了一个文件：`collab-ledger/tasks/DIYU-V1-M3-ACCOUNT-CONTENT-OPERATOR-001.md`
（本任务自己的账本条目）。**非本任务的 skills、content-production、decision-chain 零改动。**

`main` 在施工期间由 M1 落地工作推进，其中**动到了 `business-persistence/`**：

```text
M  business-persistence/app/api/knowledge.py                （+327）
M  business-persistence/app/models/knowledge.py             （+68）
A  business-persistence/migrations/.../market_observation_permission_semantics.py
M  business-persistence/tests/test_interface_contracts.py
M  business-persistence/tests/test_market_observation.py
```

`business-persistence/` 正是 `M3-AC-12`（M2→M3 最小投影）与 `M3-AC-13`（M3→M2 只写候选）
锁定变量里点名的那个模块。

## 2. 不多算：哪些证据**不**因此失效

`AC-12` 的锁定变量原文是「M2 接口版本（**绑定 `main@df2c595`** 的 `business-persistence/`）」。
这是一个**钉死的 commit**，不是"main 当前值"。本任务 worktree 里的 `business-persistence/`
仍然是 `df2c595` 那一版，本轮全部契约测试就是对着它跑的：

```text
test_projection_contract.py            30 tests  OK
test_field_ablation.py                  5 tests  OK
test_responsibility_reverse_search.py  12 tests  OK
test_downstream_brief_consumption.py    9 tests  OK
test_live_m2_contract.py               27 tests  OK
```

**因此 `AC-12` / `AC-13` 在其自身声明的绑定下证据成立，不置 `STALE`。**
把它们一并作废就是 A3 意义上的**多算**。

## 3. 不少算：哪些声明因此变成 `STALE`

「M3 的最小投影与写回候选，与 **M2 当前接口** 一致」这条**不再有证据**。
逐字对比新旧字段集，差异是实质的，不是改名：

| | M2 新接口（`a7b8101`） | M3 投影 schema（`v1.0`） |
|---|---|---|
| 来源 | `source` / `source_type` / `source_reference` / `source_provider` 四分 | 单一 `source` |
| 权限 | **`permission_status`（可否作为当前证据，默认 `unknown` 而非 `allowed`）与 `usage_limits`（可否对外发布）分成两道闸** | 单一 `usage_permission` |
| 适用范围 | `account_id` / `applicable_task_id` / `applicable_period_start` / `applicable_period_end` | 只有 `applicable_track` / `scope_ref` |
| 证据身份 | `evidence_digest`（调用方给，M2 不算） | 无 |

M2 的模型注释里写得很明确：**「being a workspace member never implies a right to use an
unknown-permission observation as current, and "viewable" never implies "publishable"」**。

**这两条差异各自指向一条已冻结判据：**

1. `AC-12` 的命题要求「保留来源、权限、时效……不坍缩为同一空值」——
   投影把 M2 现在明确分开的**可用性**与**可发布性**塌成了一个字段；
2. 适用范围缺 `account_id` / `applicable_task_id` / 期间窗，意味着一条属于**别的账号**
   的市场观察，在当前投影下无法被机械排除——这直接关系 `AC-09`（外部市场证据五方责任）。

## 4. 影响关系无法判断的项

**无。** 上述两条差异是逐字段比对出来的，不是推测；其余 M2 变更（幂等索引、workspace 成员校验）
不进入 M3 投影面，与 M3 无依赖边。

## 5. 本轮的处置，以及为什么不在本轮修

**不修**，理由两条，都不是"来不及"：

1. 改投影 schema 是**新增 WHAT**（M3 要开始区分可用性与可发布性、要按账号/任务/期间过滤），
   按 A1 执行侧不得自己创造产品语义，按 A4 需要独立授权；
2. 改了它会使 `AC-12` / `AC-13` 的全部结构证据再次失效，而本轮的变化面已经冻结在 `6bbad98`。

**按 Founder `CONTINUE_TASK` 第 5 条的分类，这条不是 `NOTE`：**
它绑定已冻结的 `AC-12`，并且落在**权限语义**上——第 5 条明写这两类可以阻断。
因此登记为**需要 Founder 决定的阻断类发现**，不自行降级为观察。

## 6. 状态怎么写

```text
M3-AC-12  对 df2c595 钉死绑定：证据成立
          对 main@a7b8101 当前接口：STALE —— 需定向复验，复验内容见 §3
M3-AC-13  同上
M3-AC-09  受 §3 第 2 条影响，其"适用范围可机械排除"这一半相对当前 M2 为 STALE
```

**不把 `STALE` 写成 `FAIL`**（它不是判定失败，是绑定过期），
**也不把它藏进"非阻断观察"**（它绑定冻结 AC 与权限语义）。

```text
END_MARKER = M3-A3-IMPACT-MAIN-MOVED-END
```
