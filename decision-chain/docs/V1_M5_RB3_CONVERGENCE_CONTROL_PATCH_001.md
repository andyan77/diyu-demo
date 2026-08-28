# M5 RB3 收敛控制补丁 001 · 接收登记

- `task_id`: `DIYU-V1-M5-UNIFIED-INTEGRATION-FINAL-ACCEPTANCE-001`
- 权威域：**有权者决定**（Founder）
- 接收时间（UTC）：2026-08-28T14:56Z
- 接收时 RB3 状态：**运行中**，停在 `>>> P1 完整主故事`
- 适用绑定：`V1_M5_CANDIDATE_RUN_MANIFEST_v1.1.3_AC07_REBASE.yaml`／candidate `d4b26f2`／`run_tag=RB3`
- 补丁性质：不改已冻结候选、Oracle、夹具、运行顺序；不追溯改变任何已发生的
  `PASS` / `FAIL` / `NOT_VERIFIED`。只约束 RB3 当前批次结束后的执行动作。

## 执行侧承接的七条

| # | 约束 | 执行侧动作 |
|---|---|---|
| 1 | 跑完当前 RB3，不中断、不换样、不选择性重试 | 不干预运行；纯传输失败才允许一次授权重试，且必须无模型输出、原失败完整保留、新 Run ID 记账 |
| 2 | 技术套件完成后按已冻结保管规则跑两份新鲜留出 | 跑前复算候选／Oracle／Dify graph／模型／参数，任一变化则**禁止解封** |
| 3 | 批次完成后停在 `CHECKPOINT` | 不自动出 v1.1.4、不开 RB4、不为取得 PASS 重采样或择优保留 |
| 4 | 硬门不成立时盲评包 `INVALID_FOR_SCORING` | sealed mapping 保持封存；不提交人类评分；记正式 `FAIL`／`NOT_VERIFIED`；只做 `FAILURE TRIAGE` |
| 5 | `RISK-M4-030+031` 按冻结判据如实记 | 归因证据单独附，不追溯改判据，不把归因说明改写成 `PASS` |
| 6 | 只交一份收敛回报 | 按补丁第 6 条的九项清单出 |
| 7 | Founder 裁决前的状态锁 | `task_progress=IN_PROGRESS`／`terminal_state=unset`／`main_merge=NOT_ALLOWED`／`new_formal_round=NOT_AUTHORIZED` |

## 第 4 条的实现方式（不改 Oracle）

`DIYU_M5_BUILD_BLIND_PACKAGE_v1.1.py` 属于 v1.1.3 已绑定的判据集合，
本批次内**不得修改**。因此第 4 条的硬门判定由执行侧在收敛回报中依据
`AB_SUITE_RAW_*` 原始证据直接作出，不通过改构包器实现。

硬门清单（逐条对证据复算）：

1. `AB-FINAL-01` 的 B 组产出非空；
2. B 组链路上每个必要能力的 `outcome` 不为 `UNKNOWN`；
3. `artifact` 非空。

任一不成立 → 本次盲评包标 `INVALID_FOR_SCORING`，封条不动。

## 接收时已知的相关事实（RB2，EXPLORATORY，不作正式结论）

RB2 的 `AB_SUITE_RAW_abFRB2.json` 中 `AB-FINAL-01` 的 B 组
`text` 长度为 0，链路三个能力全部 `outcome=UNKNOWN`、`artifact_chars=0`：

```
CONTENT_BRIEF        UNKNOWN  gaps=expression_subject_and_boundary
CREATIVE_SCRIPT      UNKNOWN  gaps=content_origin_mode
PUBLISHING_PACKAGING UNKNOWN  gaps=content_body_or_beats
```

这正是补丁第 4 条设想的那种硬门不成立。登记在此只为说明第 4 条不是空条款；
**RB3 的对应结果以 RB3 自己的证据为准，不由 RB2 预判。**

## 第 1 条例外的行使记录：DE-03 一次授权传输重试

RB3 的 DE-03 以平台 `failed` 结束，`judgment_chars=0`：

```
run_id      b11a98e1-8116-4419-bc4c-16ab8aee64b4
elapsed     286.67s
error_type  ChunkedEncodingError
message     Response ended prematurely
root        urllib3.exceptions.ProtocolError（DeepSeek 流式响应中途截断）
```

四项条件逐条核对：

| 条件 | 核对结果 |
|---|---|
| 纯传输失败 | ✓ `ChunkedEncodingError` / `ProtocolError`，HTTP 流中断，非业务结论 |
| 无模型输出 | ✓ `judgment_chars=0`，`operating_judgment` 为空 |
| 原失败完整保留 | ✓ `DIRECT_ENTRY_SUITE_deFRB3.json` 与 Dify `workflow_runs` 双份留存，不覆盖不删除 |
| 新 Run ID 明确记录 | ✓ 见下 |

重试结果（tag `deFRB3r1`，独立证据文件，不覆盖 RB3 原件）：

```
run_id           52fbfbab-0088-4d1a-bd76-1ce6ca5dc2c2
m3_gate_status   CLEAN
judgment_chars   885
verdict          PASS
window           2026-08-28 16:11:27 → 16:12:49
```

说明：候选运行时的有界重试表只认 SSL EOF / 502 / 503 / 504 / 读超时，
`ChunkedEncodingError` 不在表内，所以运行时自身没有重试（`attempts` 只有一条）。
**这张表本批次内不改。** 本次重试依据补丁第 1 条的授权执行，只此一次。
