# M3 Engineering Execution Prompt v1.1 · Delivery Manifest

> 日期：2026-08-26  
> 规划任务：`01a038f4-000b-7cd0-9dd2-d2dac022bf70`  
> 工程任务：`DIYU-V1-M3-ACCOUNT-CONTENT-OPERATOR-001`  
> 规划进入模式：`REBASE_TASK`  
> 工程执行：未发生

## 1. 当前正式交付

| 文件 | SHA-256 | 身份 |
|---|---|---|
| `M3_ENGINEERING_EXECUTION_PROMPT_v1.1.md` | `9d3388e8619d02042fda79c222fdf7bfb2570d0cd855d17ad1ea5d6122c40f59` | 单文件、自包含、可交 Founder/执行窗口的正式 Execution Prompt |
| `M3_ENGINEERING_TASK_CONTRACT_v1.2.yaml` | `1d4163fc8bbc54e37adb2070f337994795595d7b696eac37e61ffb2089cb6839` | 稳定工程任务合同 |

准确语义包仍是 `m3-account-content-operator-semantic-v1.0/`，其主稿、来源清单和工程交接哈希分别为：

```text
732963af796fd8d61521fb5b481dccc8430ac18043fe2d365e84d6048b4d91e3
42553fb4fce0285aef19de3c6e7d0c9591095b970287846ae2cca1aa25e1cae0
b6bf591183b818bea6cfd550b87e7996d2332d8b873730a7b6165a7ab3ff14f0
```

## 2. 基线绑定

| 权威输入 | SHA-256 | 结果 |
|---|---|---|
| `DIYU_V1_PLANNING_DELIVERY_BASELINE_v1.0.md` | `aa5997c36e2bf17a565b972c858ec03a58fec6ecb6d9ae6b4845d62bf7a3d640` | PASS |
| `笛语_V1_M0-M5_统一项目构建与验收方案_v1.1.md` | `50262cc169afc91f8b49b38e071f7a4288e193af3eafc193d53e0daa5122442b` | PASS |
| `DIYU_V1_M1_M4_UNIFIED_BASELINE_ADOPTION_AND_DELTA_REVIEW_v1.1.md` | `4cdc920918019a59c83f1a78aed20720623b91ef84d1d043746b1ac276e58913` | PASS |

## 3. 版本关系

`M3_ENGINEERING_EXECUTION_PROMPT_v1.1.md` 是完整、自包含的后继正式版本。执行窗口不需要拼接：

- `M3_ENGINEERING_EXECUTION_PROMPT_v1.0.md`；
- `M3_ENGINEERING_EXECUTION_PROMPT_v1.0_REBASE_ERRATA_001.md`；
- `M3_ENGINEERING_EXECUTION_PROMPT_v1.0_PRESTART_DELTA_v1.0_CANDIDATE.md`；
- 旧 v1.0/v1.1 工程合同。

这些文件保留历史身份，不覆盖、不删除。其旧 READY、自证或过时基线结论不再作为当前工程输入。

## 4. 验收记录

```text
YAML_PARSE = PASS
M3_AC_00_TO_20_UNIQUE_COUNT = 21
REQUIRED_SEMANTICS_SCAN = PASS
UNIQUE_BASELINE_HASH = PASS
UNIFIED_PLAN_HASH = PASS
DELTA_REVIEW_HASH = PASS
SEMANTIC_PACKAGE_IDENTITY = PASS
PROJECT_REPOSITORY_WRITE_BY_PLANNING_WINDOW = false
DIFY_WRITE_BY_PLANNING_WINDOW = false
ENGINEERING_BRANCH_CREATED_BY_PLANNING_WINDOW = false
ENGINEERING_EXECUTION_PERFORMED = false
```

正式 Prompt 已覆盖：治理 -005/rev2、四类行为非物理状态、八类目标、一主有限次、三类产能、共同质量底线、合法演绎/二创、最小可恢复锚点、M2/M3 反馈边界、Campaign 默认恢复、市场五方责任、CTA 三层权限、周期策略候选、`NO_CONTENT_TASK`、DeepSeek/Qwen/fallback、A/B 硬门与增益门、M3/M5 分层、正式/探索证据边界和 AC-00～20。

## 5. 实时仓库观察

交付核验时：

```text
/home/faye/diyu-demo
HEAD = origin/main = df2c5952551f386a0e9a509404357f23c1d223c9
```

项目工作树仍有既存未跟踪对象。本轮后段新观察到 `M2_POST_DONE_REBASE_EXECUTION_PROMPT_v1.2.md`，其正文明确自身只是 M2 后继规划 Prompt、未自动启动 M2 工程。该文件不证明 M2 接口已经变化；M3 执行侧仍须在入场时核验 M2 的真实当前接口和状态。

## 6. 授权与唯一下一动作

本 Prompt 已可由 Founder 使用或转交，但文件存在和转交不自动授权施工。启动 M3 时，Founder 应将以下两个准确哈希与明确工程执行指令一并交给 M3 执行窗口：

```text
Prompt  = 9d3388e8619d02042fda79c222fdf7bfb2570d0cd855d17ad1ea5d6122c40f59
Contract = 1d4163fc8bbc54e37adb2070f337994795595d7b696eac37e61ffb2089cb6839
```

执行窗口随后先做只读重入、判定工程任务进入模式，再决定是否可以写入；不得从本 Manifest 推定授权。

```text
M3_ENGINEERING_EXECUTION_PROMPT
= READY_FOR_FOUNDER_USE

engineering_execution_performed
= false
```
