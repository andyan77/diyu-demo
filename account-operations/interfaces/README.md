# M3 接口契约

三条接缝的载体。产品语义在 `M3_ACCOUNT_CONTENT_OPERATOR_SEMANTIC_COMPILATION_v1.0.md`
与四份已接受的共享合同里；**这里只是把它们落成可测的形状，不新增产品义务**。

| 文件 | 是什么 | 本轮状态 |
|---|---|---|
| `M2_TO_M3_PROJECTION_v1.0.schema.json` | M2 → M3 当轮最小投影 | schema + 编译器 + 30 条测试 `static_verified` |
| `M3_TO_M2_WRITEBACK_CANDIDATE_v1.0.schema.json` | M3 → M2 候选写回信封 | schema + 校验 `static_verified`；**未接 Dify、未 POST 真实 M2** = `NOT_VERIFIED` |
| `M3_CONTENT_TASK_v1.0.schema.json` | M3 → Content Brief 内容任务（含合法无任务结论） | schema `static_verified`；**下游真实消费未测** = `NOT_VERIFIED` |
| `projection.py` | 投影编译与两个校验函数；纯标准库 | 30 条 unittest 全通过（含 3 次变异验证） |

## 跑测试

```bash
python3 -m unittest discover -s account-operations/tests -t account-operations/tests -v
```

不需要数据库、不需要 Docker、不需要 pytest。`jsonschema` 用宿主已有的 3.2.0（Draft7）。

## 两条设计约束，以及为什么

### 1. 六种「没有值」不得坍缩

M2 用 `null` 表达一切缺失。产品语义要求区分：**已具备／未知／未提供／不适用／拒绝提供／已失效**。
把它们映射成同一个 `null` 是 `M3-AC-12` 明确的 `FAIL` 条件——因为下游读到 `null` 时会自己
补一个解释，而补出来的那个解释看起来和真的一模一样。

`projection.py::_resolve()` 是唯一防线，规则是刻意排序的：

1. 调用方**显式声明**了缺失原因 → 用它；
2. 否则 M2 给了 `None` → `UNKNOWN`；
3. 否则 → `PRESENT`。

**第 2 条永远不会升级成 `REFUSED` 或 `NOT_PROVIDED`。** 猜一个等于凭空伪造证据身份。

### 2. 候选信封在语法层就表达不出「已接受」

`candidate_status` 只有一个合法取值 `proposed`；`validate_writeback_candidate()` 对整棵树
做键名反搜，`is_current` / `accepted` / `promote` / `overwrite` / `feedback_override` 等
一律拒绝；`suggested_m2_endpoint` 的枚举里**没有任何**指向反馈或市场观察的写端点。

接受与当前有效版本属于 M2 和用户（共享合同四 §二）。靠模型自觉不算机制。

## 已登记的 M2 能力缺口（`static_verified`，不是缺陷指控）

`business-persistence@main:df2c595` 的 `cycles` 表把三类产能存成可空数字 + 各自的
`*_source` 文本，**没有字段能表达「用户拒绝提供」与「我们不知道」的区别**。

- 后果：这个区分只能由任务快照侧通过 `requested.declared_absences` 带进投影；
- 没带进来时，投影**降级为 `UNKNOWN`**，绝不猜成 `REFUSED`；
- 这是 M2 当前设计的自然边界，**不需要也不授权修改 M2**。若后续判定该区分必须落库，
  属于 M2 的新任务，不在 `DIYU-V1-M3-ACCOUNT-CONTENT-OPERATOR-001` 范围内。

## 失效传播

`business-persistence` 的下列端点或字段任一变化 → 本目录全部内容 + `M3-AC-12/13` 置 `STALE`：

```text
GET  /workspaces/{ws}/accounts/{acc}/cycles/current
GET  /workspaces/{ws}/accounts/{acc}/campaign-overrides/active
GET  /workspaces/{ws}/accounts/{acc}/cycles/decisions/latest
GET  /workspaces/{ws}/market-observations
GET  /workspaces/{ws}/publish-instances/{id}/feedback
POST /workspaces/{ws}/cycles
POST /workspaces/{ws}/accounts/{acc}/cycles/decisions
POST /workspaces/{ws}/playbooks
POST /workspaces/{ws}/campaign-overrides
```

**已知在途变更**：M2 的任务分支上有未提交的「市场观察权限语义」改动（`app/api/knowledge.py`、
`app/models/knowledge.py`、迁移 `17368b750d3b`）。它合入 main 后，**只**使
`market_observations` 相关投影字段与 `M3-AC-09 / AC-12` 置 `STALE`，其余字段不受影响——
不多算失效，也不少算。
