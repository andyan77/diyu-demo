# WITHDRAW Successor Failure Triage 001 — W1 Branch

- `observed_failure`: W1 的 `uapp_action/uapp_route` 均输出 `WITHDRAW_MATERIAL`，但执行节点从
  `uapp_material_gate(false)` 直接进入 `uapp_m3_gate`，未调用 M2 撤回接口；素材仍未撤回。
- `frozen_target`: 同一会话精确撤回 W0 登记的 material，保留历史，不产生发布或专业能力暗跑。
- `candidate_sources`: `SYSTEM_UNDER_TEST`。
- `confirmed_origin`: `SYSTEM_UNDER_TEST` — 当前 UAPP 图缺少从 no-file 分支到 material withdrawal
  的任何节点和边；M2 既有撤回 API 与回归合同存在且受保护。
- `evidence`: W1 run `e135f463-00a5-4d47-a3d4-fadf91194e96`；action/route 均为
  `WITHDRAW_MATERIAL`；M2 material `dfebe06b-bc0b-41b4-8d36-e3a04ff9eeb3` 的
  `withdrawn_at=null`；其他能力、发布、非测试漂移均为 0。
- `mutation_target`: UAPP 的 no-file 后继增加 action gate、M2 withdraw POST、响应身份复核和
  成功/失败自然回复；同一 Track A 接缝的唯一 successor。
- `protected_targets`: M1/M2/M3/Hop/Seam/六能力/PP/schema/非测试数据/历史 RAW/main。
- `next_reverification`: 零模型正负控制后，只重跑冻结 W1 一次，不重跑 W0。
