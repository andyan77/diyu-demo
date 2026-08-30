# FAILURE TRIAGE 001 · CAP-06 Checker polarity and LLM count

observed_failure: 正式 run `9f6ff2fe-b59a-4e46-85d5-c9577b1bd255` 返回 HTTP 200 并产生
5115 字包装 artifact，Checker v1.0 的两项谓词为 false：商业禁区、LLM 预算。

frozen_target: 不复活价格、折扣、站外购买等商业承诺；实际 DeepSeek 尝试数大于 0 且不超过 14。

candidate_sources: `CHECKER_OR_FIXTURE`, `SYSTEM_UNDER_TEST`, `INSUFFICIENT_EVIDENCE`。

confirmed_origin: `CHECKER_OR_FIXTURE`。

independent_evidence:

- Checker v1.0 把任意出现“站外购买”字样都判为商业承诺；真实 artifact 与用户交付中的两处
  均为否定边界：“不写价格、折扣或站外购买承诺”“不引导任何购买、到店、私信或领取动作”。
  这不是禁区复活，而是明确保持禁区。
- RAW 节点记录使用字段 `type=llm`；Checker v1.0 错读不存在的 `node_type`，因此把真实 6 次
  LLM 节点执行计为 0。
- 六个真实 LLM 节点为 UAPP 2、M3 2、Hop 1、PP 1；均 status=succeeded，合计 6 ≤ 14。
- 其余正式谓词均已通过：只运行 PP、正文 hash、平台、低风险 CTA、六类包装、自然交付、
  无真实发布、无非测试变化、无内部重放。

mutation_target: 仅建立版本化 Checker v1.1：LLM 计数读取 RAW 的真实 `type` 字段；商业禁区
谓词区分否定/拒绝边界与正向商业动作。原 Checker v1.0、Result v1.0 与 RAW 保留不改。

protected_targets: UAPP、PP、provider、M1/M2/M3、Hop、Seam、专业 Prompt、原输入、业务判据、
正式 RAW、数据库与 main。

next_reverification: 只对同一份 RAW 运行 Checker v1.1 正负控制与正式重判；模型调用 0，
不重跑 CAP-06。

