# WITHDRAW Tool Failure Triage 001 — M2 Test Scope

task_id: `DIYU-V1-UNIFIED-DIFY-APPLICATION-001`
event_time_utc: `2026-08-31T01:17:25Z`
model_calls_before_failure: `0`
candidate_published: `false`

## FAILURE TRIAGE

- `observed_failure`: Track A 零模型回归调用 M2 仓库既有
  `test_material_withdrawal.py`。测试行为本身两次均为 `5 passed`，但其 bootstrapped fixture
  创建的 publish instance 没有设置 `is_test/is_simulated`，使全局非测试 publish 计数从激活时
  `1568` 变为 `1570`。
- `frozen_target`: 确定性控制不得改变非测试数据；UAPP 正式候选发布前，全局非测试
  publish/feedback 必须保持 `1568/117`，schema md5 必须保持
  `25192c11562827efedfc3b2c22c3b4fd`。
- `candidate_sources`: `CHECKER_OR_FIXTURE`、`INPUT_ENVIRONMENT_OR_TOOL`。
- `confirmed_origin`: `INPUT_ENVIRONMENT_OR_TOOL` — M2 自带测试使用当前共享数据库，且 fixture
  创建的发布记录默认 `is_test=false/is_simulated=false`。UAPP 候选从未发布，Dify 模型调用为 0，
  因此这两条变化不可能来自 SYSTEM_UNDER_TEST。
- `evidence`:
  - 第一次命令：宿主无 `pytest`，随后在 `diyu-m2-app` 容器运行，
    `5 passed, 2 deselected`；
  - 第二次由初版控制脚本调用相同测试，仍为 `5 passed`；
  - 新 publish rows：
    - `a68ae319-c689-4844-ace9-cf0b08590cd5`，workspace
      `ws-1b7de80f77144c0988168449ba2e6dd9`，created_at
      `2026-08-31T01:15:57.106879Z`；
    - `88bec000-e2b1-4bc8-a33c-3d0f8700e628`，workspace
      `ws-8d1c84525d594e7e9691b93e03450ebf`，created_at
      `2026-08-31T01:17:24.970546Z`；
  - 两次测试共创建 10 个 `ws-<uuidhex>` fixture workspace；每个均有 1 material、1 task、
    1 artifact，其中两个 workspace 各有 1 publish instance；
  - 当前 schema md5 与 feedback 计数未变：`25192c…b4fd` / `117`。
- `mutation_target`: 初版零模型控制工具已改为只读继承 M2 已接受 M2-AC-11 证据，并对共享
  数据库只做基线检查；不再在当前数据库执行 M2 写入型单元测试。
- `protected_targets`: 两条误标 publish row、10 个 fixture workspace 及其关联记录、M2 服务/schema、
  UAPP 候选、所有专业应用、历史证据、main。没有 Founder 新授权前不得删除、改标或覆盖。
- `next_reverification`: 在有权者明确选择如何处置这批可唯一定位的测试夹具数据后，重新只读核对
  `1568/117` 与 schema md5，再从 Track A 确定性控制继续。不得在当前状态冻结正式 Gate 或调用模型。

## Scope decision needed

当前授权不包含修改被标记为非测试的数据。建议 Founder 仅授权对上述 10 个唯一可定位的测试
fixture workspace 做一次可审计清理；若不授权清理，则本次 S5 不能满足“非测试数据零变化”硬门。

### Exact cleanup candidate set

以下集合由 `created_at >= 2026-08-31T01:15:50Z`、测试生成的 `ws-<uuidhex>` 名称和本次两次
pytest 时间窗三重绑定；不包含激活前 workspace：

| workspace id | workspace name | materials | tasks | artifacts | versions | publishes |
|---|---|---:|---:|---:|---:|---:|
| `94810adf-8429-4a13-b732-4d960db42267` | `ws-1b7de80f77144c0988168449ba2e6dd9` | 1 | 1 | 1 | 2 | 1 |
| `55dea141-7d27-488c-a498-06a0979d5c22` | `ws-304e9b70206f493e85a90fb6e725610a` | 1 | 1 | 1 | 0 | 0 |
| `e99346f8-d2ab-44f1-b2f0-ae94ecd559c1` | `ws-5d53c2af7a4f4afcab59337f3980afc1` | 1 | 1 | 1 | 0 | 0 |
| `99af9ef2-9afa-4839-be88-22d37cbc4f59` | `ws-f4ca2aef565d43269d5a9e19a3612ed7` | 1 | 1 | 1 | 1 | 0 |
| `008be683-9af2-4528-afde-9e6ef47be6cb` | `ws-1c0246ca0ae74f8ca6e5a3531c4aa780` | 1 | 1 | 1 | 0 | 0 |
| `7901c68c-a580-4a51-8dbe-47717668af37` | `ws-8d1c84525d594e7e9691b93e03450ebf` | 1 | 1 | 1 | 2 | 1 |
| `e90f3460-be8e-4490-827a-31ca7cd16312` | `ws-f5aed2c401864df8b965fae987755142` | 1 | 1 | 1 | 0 | 0 |
| `1b22bb7d-1f9b-49ea-8fe8-4e2b2e0968c2` | `ws-0ba81e9d485e49dcb05d3ed8eecf74bb` | 1 | 1 | 1 | 0 | 0 |
| `9a95cbe7-aa95-463a-8112-f15f235e8cc3` | `ws-9190d65ec52944eca4d06c3299963b20` | 1 | 1 | 1 | 1 | 0 |
| `8479b71e-59e1-43f3-80d3-a18a6fb6e7bc` | `ws-27a83567f08d41fea96eb04a416e75d9` | 1 | 1 | 1 | 0 | 0 |

