# CAP-06 FAILURE TRIAGE AND BINDING PROOF v1.0

task_id: `DIYU-V1-UNIFIED-DIFY-APPLICATION-001`

observed_failure: 原正式运行 `e71e84af-e3e3-47ec-afc4-72bd02941540` 已把用户本轮
78 字成片正文逐字绑定给 Publishing & Packaging，且只运行该能力，但最终只追问 CTA 缺口，
没有生成包装成品。线上 `platform` 仍为 `NOT_LOCKED`，`content.promise` 被错误填成整段成片正文。

frozen_target: 用户同轮提供完整已实现成片、明确“小红书”、请求标题/封面/首帧/发布文案/
话题/自然 CTA，并明确排除价格、折扣和站外购买承诺时，应直接形成完整发布包装。

confirmed_origin: `SYSTEM_UNDER_TEST`，最高失效接缝由两部分组成：

1. UAPP `uapp_inline_artifact → uapp_fields` 只携带了整段正文型 `content.promise`，遗漏平台与
   低风险 CTA 授权等级；
2. PP `envelope_check` 把 `cta_contract` 放入无条件必填清单，缺失判定先于 `NO_CTA` 缺省，
   使局部 CTA 缺口扩大为整包阻断。

independent_evidence:

- 原输入、正文与注入正文 sha256 均为
  `00c3372f5b38e5eca06a9cf97fa7acc09707b753deceea2e3f670f84051e9fcd`；
- 原 selector 为 `INLINE_SELECTED`，task/current-turn/type/fp/bfp 均通过；
- 原 PP 只运行一次，其他五能力为零，证明路由、正文选择与能力隔离不是本次最高失效点；
- 原 `uapp_fields` 输出 `platform: NOT_LOCKED`、整段 `content_promise`、`gaps_text=cta_contract`；
- PP 线上 `envelope_check` 代码 sha256 为
  `1bcf1be8f119c53e81301abc803f5b03ad1fe871d7d13fa67bffa2d1a7c325ac`，与仓库基础图加已接受
  `_find_scalar` successor 可逐字复算；其中 `cta_contract` 位于 `REQUIRED`，而缺省
  `NO_CTA` 在 missing 计算之后；
- PP 专业 LLM 节点与 Prompt 在候选构建前后逐字一致。

mutation_target:

- UAPP：`uapp_inline_artifact` 的同轮伴随语义编译、`uapp_fields` 的同源复核；
- PP：仅 `envelope_check` 的 CTA 可选/局部充分性外壳。

protected_targets: M1/M2/M3、Hop、Seam、PP 专业 Skill 与专业 LLM Prompt、其他五能力、
数据库 schema、非测试数据、历史 RAW/Gate/Result、main。

binding_proof_after_candidate_build:

- 成片正文长度 `78`，源/注入 sha256 完全相同；
- `content.promise = 依次展示搭直筒裤、半裙和薄针织三套通勤穿法`，为成片原文中的兑现点，
  不等于整段正文；
- `delivery.platform = 小红书`，来源等级为用户本轮原话；
- `cta.contract = 自然 CTA` 保留原文；`cta.level = LOW_RISK_INTERACTION` 仅由“自然 CTA”与
  明确商业禁区共同确定性编译，不生成具体 CTA 文案；
- 不自动接受或持久化同轮成片，不新增会话变量。

next_reverification: 冻结 Gate 后发布候选，只运行原冻结 CAP-06 一次；判定必须同时依赖真实
节点、正文 hash、能力计数、六类成品、商业禁区与副作用，不以 workflow succeeded 或模型自述放行。

