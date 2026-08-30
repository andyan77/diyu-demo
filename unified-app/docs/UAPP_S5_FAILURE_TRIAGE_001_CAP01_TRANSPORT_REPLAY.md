# UAPP S5 FAILURE TRIAGE 001 · CAP-01 transport replay

`task_id: DIYU-V1-UNIFIED-DIFY-APPLICATION-001`

`gate_sha256: d27254ff95ba47d4cd056c3697d658e463956382faa5cdbec0d07b187e3b358a`

## FAILURE TRIAGE

```yaml
observed_failure: >-
  CAP-01 的顶层请求返回 HTTP 200，且真实路由到 MATRIX、Seam 和 MATRIX 各运行一次、其余五能力零运行；
  但 M3 的 gate_repair_llm 首次发生 DeepSeek SSL EOF，Dify 随后内部重放 M3 一次。
  本轮因此出现 7 个 LLM 节点 attempt，超过冻结的每轮静态可达数 6；冻结 Checker 的 T-04、T-08 FAIL。
frozen_target: >-
  每个冻结输入只运行一次；CAP-01 只运行 MATRIX；无业务节点失败；单轮静态可达 LLM 节点不超过 6；
  只有整条正式槽位零模型输出、零状态写入、零副作用时，纯传输异常才有资格技术重试。
candidate_sources:
  - INPUT_ENVIRONMENT_OR_TOOL
  - SYSTEM_UNDER_TEST
  - INSUFFICIENT_EVIDENCE
confirmed_origin: INPUT_ENVIRONMENT_OR_TOOL
evidence:
  raw_sha256: 48ae72ff486dfbf1ce7f78fd82cdfc23dc0ba9ed013c583cca9c641c2e55b513
  checker_sha256: 76da19c49c361b00194749042d2dc27f8fd7b7b61407d3ce3aa1f25ebf107ff1
  top_run_id: b1f4485d-f921-4aac-a202-b3727f51f87e
  failed_m3_run_id: 71a6e161-deb7-4533-ab55-9c98a6a99471
  replayed_m3_run_id: 55a232c4-c4a0-4141-bd7d-808eac6f7469
  exact_error: "[SSL: UNEXPECTED_EOF_WHILE_READING] EOF occurred in violation of protocol"
  business_route_checks: CAP-01/CAP-02/CAP-03 all PASS
mutation_target: NONE
protected_targets:
  - UAPP current published graph
  - M1 / M2 / M3
  - Hop / Seam / PP provider
  - six professional capabilities
  - frozen inputs / Gate / Runner / Checker
  - M2 schema / non-test data / main
next_reverification: >-
  当前授权不允许重试。只有 Founder 新的版本化授权才能在相同候选、输入、Gate 与判据下建立后继正式槽位；
  不得把本次环境失败改判成系统 PASS 或 FAIL。
model_calls_before_failure: 7
side_effects: >-
  已有 UAPP 模型输出；测试域创建了 1 个 workspace、1 个 cycle、1 个 task；
  artifacts/content_versions/publish_instances/feedback_records 均为 0；非测试计数和 schema 未变。
```

## 为什么不能使用传输重试例外

失败的那个 M3 子运行本身没有可用模型输出，但整条 CAP-01 正式槽位在它之前已有 UAPP 模型输出并已创建测试域；Dify 还自动启动了第二个 M3 run。冻结例外要求整条正式槽位同时满足零输出、零状态写入和零副作用，本次不满足。因此不手动重试、不运行 CAP-02。

## 被测行为边界

本次已观察到的业务行为不支持把故障归因到统一应用：`target_capability=MATRIX`，Seam 与 MATRIX 各一次，其他五能力均为 0，用户回复无内部泄漏。由于正式全集在第一个输入即失去证据资格，UAPP-AC-01～11 均不得据此上调。
