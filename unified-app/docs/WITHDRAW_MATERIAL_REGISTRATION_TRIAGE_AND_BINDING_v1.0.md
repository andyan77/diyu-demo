# WITHDRAW Material Registration Triage and Binding v1.0

task_id: `DIYU-V1-UNIFIED-DIFY-APPLICATION-001`
mode: `REBASE_TASK`
model_calls_before_triage: `0`

## FAILURE TRIAGE

- `observed_failure`: W0 文件上传 HTTP 201，M1 `m1_extract` 真实读取文件，但当前发布 UAPP 的
  node execution 在 `uapp_ctx` 后直接进入 `uapp_m3_gate`，没有执行素材登记；M2 `materials=[]`。
- `frozen_target`: 一个当前轮上传文件应经 UAPP 真实业务路径登记为 task-scoped 测试素材，
  并由同一会话的 W1 精确撤回。
- `candidate_sources`: `SYSTEM_UNDER_TEST`、`CHECKER_OR_FIXTURE`。
- `confirmed_origin`: `SYSTEM_UNDER_TEST` — 当前发布 UAPP 图缺失上传资料识别、登记、解析和
  会话绑定节点及接线；M1 与 M2 服务均未被证明失效。
- `evidence`:
  - W0 run `c97d9b12-931b-473a-af43-f08507f01db1`；
  - 上传 HTTP 201，文件 sha256
    `8c21d41d471deed8e169055a37288e1f29b769fe5f7a7296dff4274b8bb6d53a`；
  - `m1_extract` succeeded，当前 UAPP 41 个实际节点中没有 material registration；
  - 当前发布图 56 nodes / 58 edges，存在 `uapp_ctx → uapp_m3_gate` 直连；
  - M2 create/withdraw API 与历史 M2 单元测试已存在，不需要修改 M2 或 schema。
- `mutation_target`: 当前 UAPP 图中 `uapp_ctx` 与 `uapp_m3_gate` 之间的上传识别、幂等准备、
  test-scoped M2 POST、结果复核、会话 material id/binding 保存及 fail-closed 分支。
- `protected_targets`: M1、M2 服务/schema、M3、Hop、Seam、六专业能力、PP、历史 RAW、
  CAP-01～06 与 GAP-01 当前 PASS、非测试数据、main。
- `next_reverification`: 先执行 14 项确定性正负/单变量控制和无文件路径等价控制；全部通过并
  冻结 successor Scenario/Gate/Checker 后，才发布候选并按 W0→W1 正式验证。

## Binding contract

登记记录只使用现有 M2 `materials` 表和 `scope_ref/content_ref` 承载可回指元数据，不改 schema：

- `source = founder_upload`
- `owner_ref = conversation.uapp_actor`
- `analysis_authorized = true`
- `generation_authorized = true`
- `publish_authorized = false`
- `scope_ref.is_test = true`
- `scope_ref.is_simulated = true`
- `scope_ref.account_id/task_id/file_name/dify_upload_id/extracted_text_sha256/idempotency_key`
- `content_ref = dify-upload:<upload_id>#sha256=<extracted_text_sha256>`

幂等键由 task id、Dify upload id 与提取正文 hash 确定性计算；同一会话保存 material id 与绑定
元数据。无文件路径不执行任何素材节点；POST 非 2xx 时直接自然语言 fail-closed，不进入能力链，
也不声称素材已登记。

