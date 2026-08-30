# FAILURE TRIAGE 003 · E3 · D3 未能执行（纯传输失败，零模型输出）

`task_id: DIYU-V1-PP-BOUNDARY-SUCCESSOR-001`｜`task_mode: REBASE`
判据真源：`unified-app/stages/PPBS_GATE_v2.0.json`
证据：`unified-app/evidence/stages/pp_boundary_successor/PPBS_B2_D3_RAW.json`

## observed_failure

统一画布 `/v1/chat-messages` 返回 **HTTP 400**，耗时 **0.02 秒**。

```
workflow_run_id      = None
message_id           = None
node_detail          = []（空）
九个应用时间窗内 run  = 0 / 0 / 0 / 0 / 0 / 0 / 0 / 0 / 0
窗口内 LLM 节点执行   = 0 次
uploaded_fixture     = [401, {"code":"unauthorized","message":"Access token is invalid"}]
```

**零模型输出。** 请求在参数校验阶段就被拒，任何工作流都没有启动。

## frozen_target

Gate v2.0 `phase_d_criteria.D3`：D3-a 至 D3-f 六条。

## candidate_sources

| 候选 | 判定 | 依据 |
|---|---|---|
| `INPUT_ENVIRONMENT_OR_TOOL`（运行器 harness） | **成立** | 见下 |
| `SYSTEM_UNDER_TEST`（b2 / PP / 画布 / Seam） | 排除 | 被测对象一次都没被调用到；零 run、零节点、零 LLM |
| `ORACLE_OR_CRITERION` | 排除 | D3 六条判据没有被执行到，无从谈对错 |
| `CHECKER_OR_FIXTURE`（判定器） | 排除 | 判定器本轮未参与，运行器只发起不判定 |
| `CONTRACT_OR_INTENT` | 排除 | D3 输入与判据未变 |

## confirmed_origin

`INPUT_ENVIRONMENT_OR_TOOL` —— **本任务运行器的传参错误**。

```python
# S4_2_RUN_v1.0.py 的签名
def upload(key, path, user):      # 第一参是 API Key
    ...
    headers={"Authorization": "Bearer " + key, ...}
    return r["status"], b          # 返回 (status, body) 元组

# 运行器里的调用（PPBS_D_RUNNER_v1.0.py 原样继承到 PPBS_B2_D_RUNNER_v1.0.py）
fx = R.upload("file", FIXTURE, spec["end_user"])
#              ^^^^^^ 把字面量 "file" 当成了 Bearer token → 401
```

两级后果：

1. `Authorization: Bearer file` → `/v1/files/upload` 返回 **401**；
2. `upload()` 返回的是 `(401, {...})` 元组、**非空即为真**，于是
   `{"upload_file_id": [401, {...}]}` 被塞进 `/v1/chat-messages` 的 `files[]`
   → 服务端参数校验拒绝，**400**。

这段代码是 b1 运行器写下的，b1 从未走到 D3 分支，因此**这次是它第一次被执行**。

## mutation_target

`PPBS_B2_D_RUNNER_v1.0.py` 里 D3 分支的 `R.upload(...)` 调用（传 Key、解包元组、
上传失败即中止而不是继续发起）。

**本轮不改、不重跑。** 执行 Prompt 第八节与 Gate v2.0 `transport_failure_rule`：

> 纯传输失败如未产生模型输出，也不得自行重试；登记后停下请示。

## protected_targets（未改，且无证据证明有错）

b2 SKILL.md、PP graph、Gate v2.0、Inputs、D1/D2 的运行与判定、b1 全部历史件、
Seam、候选画布、其余八个受保护应用、`hop_pin`、`main`。

## 受保护面已恢复到测试前状态

| | D3 尝试前 | 现在 |
|---|---|---|
| PP 当前发布图 | `8366328b`（b2） | `788c8555`（旧稳定图） |
| provider 钉住的图 | `8366328b`（b2） | `788c8555`（旧稳定图） |
| PP workflow 行 | 5 | 6（b1、b2、原始旧稳定行**全部保留**） |
| Seam / 候选画布 / 其余八应用 / hop_pin | 冻结值 | 冻结值，零漂移 |

**一处需要你确认的判断**：冻结的回退条件字面写的是「D3 FAIL ⇒ 钉回旧稳定版」，
没有写「D3 未执行」。我把本次归入该条执行了恢复，理由是——

- provider 钉到 b2 在 Gate 里是**测试范围**变更，只为执行 D3；D3 没能执行，授权窗口就关闭了；
- 执行 Prompt 第九节要求三项全 PASS 才允许把 provider 正式钉到 b2；
- 留着未过 D3 的版本对外供 Seam / M5 FP / 统一画布调用，风险高于恢复到测试前状态；
- Gate 已写明「恢复受保护面到测试前状态不是修复迭代」。

如果你认为这一步越权，请指出，可再行处置。

## next_reverification（需要新授权才能执行）

重跑 D3 需要：

1. 修运行器 D3 分支的上传调用（零模型、纯 harness 修复）；
2. 重新发布 b2 为 PP 当前版本 ＋ 把 provider 钉到 b2（两步都是零模型的确定性操作，
   b2 的 workflow 行还在，不需要重建）；
3. 按**原冻结**的 D3 输入与六条判据跑一次，不改判据、不改 b2 实现。

D1 与 D2 已是正式 PASS，无需重跑。
