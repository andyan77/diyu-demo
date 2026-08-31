# UAPP S5 Failure Triage 004 — WITHDRAW W0 material not persisted

## FAILURE TRIAGE

- `observed_failure`: 冻结 W0 文件上传 HTTP 201，UAPP 顶层 workflow 成功读取完整上传文件，
  但本轮没有执行素材登记分支，task-scoped M2 `materials` 仍为空；因此不存在可供 W1 撤回的合法素材。
- `frozen_target`: W0 必须把真实上传资料登记为测试域素材；W1 才能在同一会话撤回该素材，
  并证明撤回只改变未来复用资格。
- `candidate_sources`:
  - `SYSTEM_UNDER_TEST`
  - `CHECKER_OR_FIXTURE`
- `confirmed_origin`: `SYSTEM_UNDER_TEST` — UAPP 上传资料到 M2 素材登记接缝未进入当前运行路径。
- `evidence`:
  - run_id `c97d9b12-931b-473a-af43-f08507f01db1`，HTTP 200，节点错误 0，LLM 5；
  - Dify 文件上传 HTTP 201，文件 sha256
    `8c21d41d471deed8e169055a37288e1f29b769fe5f7a7296dff4274b8bb6d53a`；
  - `m1_extract` 成功读取 `sys.files`，证明文件真实进入目标系统而非 Runner 伪造；
  - UAPP node execution 1..41 中不存在素材登记 HTTP 节点；
  - task-scoped M2 `materials=[]`；冻结 Checker `WITHDRAW-01=FAIL`；
  - 当前画布自身说明“有上传资料才登记成 M2 素材；素材是撤回对象”，与冻结 W0/W1 合同一致。
- `mutation_target`: `NONE`。本轮授权只允许 GAP-01 决定性问题接缝；素材登记接缝不在允许变化面。
- `protected_targets`: 冻结 W0/W1、Checker、M1/M2/M3、Hop、Seam、专业能力、M2 schema、
  历史 RAW、main、非测试数据。
- `next_reverification`: 后继授权若修复 UAPP 上传资料登记接缝，应先零模型证明上传资料产生
  task-scoped 测试素材，再按相同冻结 W0/W1 各运行一次；本 Prompt 不执行该修复或 W1。

## Side effects and scope

- 新建测试 workspace/cycle/task 属冻结 Runner 的正常测试域写入；无非测试数据变化。
- 非测试 publish/feedback 仍为 `1568/117`，schema md5 仍为
  `25192c11562827efedfc3b2c22c3b4fd`。
- 没有真实发布、撤回、删除、权限变化、重试或平台内部重放。
- W1 依赖 W0 产生合法素材，故标 `NOT_RUN_DEPENDENT`；不消耗第二个正式输入。

