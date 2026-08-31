# FAILURE TRIAGE · S5 最后两个阻断

task_id: `DIYU-V1-UNIFIED-DIFY-APPLICATION-001`

## Track A · EQUIV YAML-like

observed_failure:
冻结 YAML-like 输入包含与 plain/JSON-like 相同的受众、问题、期望改变、表达主体、表达边界和商品，
但真实运行没有生成 Content Brief。

frozen_target:
三种表达只改变排版，业务在场判断与专业结果语义必须一致；真实缺项负例仍只缺期望改变。

candidate_sources:

- `SYSTEM_UNDER_TEST`
- `INPUT_ENVIRONMENT_OR_TOOL`
- `INSUFFICIENT_EVIDENCE`

confirmed_origin: `SYSTEM_UNDER_TEST`

evidence:

- run `c4a7cd78-8da0-4f97-b5a1-5beb89100041`，RAW sha256
  `0247a5b127b1e9b15ecd39a12d7efdca89ef166d21c01ae7c73e0eef961b34ba`；
- 输入逐字包含 `希望她看完明白`，但 M3 快照的 `goal_structure.primary_goal=null`、
  `business_goal_categories=[]`；Hop 外壳的 `primary_goal` 未声明，Content Brief 充分性闸最终只报
  `content_promise` 缺失；
- plain 与 JSON-like 同义正例在同一前序候选下已产出成品；差异首次出现在专业能力之前的业务语义判断入口，
  不是 Content Brief 输出层或 Checker。

mutation_target:
`用户输入 → UAPP 格式无关规范化/装配 → M3 业务语义判断入口` 中经控制确认的最高失效接缝。

protected_targets:
Hop、Seam、Content Brief 与其他专业能力、冻结输入和产品判据。

next_reverification:
先离线证明 plain/YAML-like/JSON-like 等价、缺项负例不等价和消融判别；冻结候选后按九项正式顺序只运行一次。

## Track B · FULL RECORD_PUBLISH

observed_failure:
用户原话被正确识别为已经发布，但没有创建测试发布记录，后续反馈、周期和恢复链因此无法开始。

frozen_target:
只在当前测试 workspace/cycle/task 存在合法、当前、可回指内容对象时创建一条
`is_test=true / is_simulated=true / real_platform_publish=false` 的幂等发布记录。

candidate_sources:

- `SYSTEM_UNDER_TEST`
- `INSUFFICIENT_EVIDENCE`

confirmed_origin: `SYSTEM_UNDER_TEST`

evidence:

- run `14d66ec7-09aa-4fd9-85ba-2dce90ec7c67`，RAW sha256
  `63796e15729c6640ad187818059802ee781c424fe644be75d3d710fa30f1f701`；
- `uapp_action.action=RECORD_PUBLISH`，`uapp_route.route_mode=WRITEBACK`；
- UAPP 随后仍进入 M3，未执行发布写回子图；运行后 `publish_instances=[]`、`uapp_last_publish=""`；
- T1 的 6,348 字 Content Brief 仍在同一会话 artifact store 中，失败不是内容正文物理丢失。

mutation_target:
`UAPP RECORD_PUBLISH → 合法内容选择 → M2 test publish API → 结果与会话绑定`。

protected_targets:
M2 schema/非测试数据/真实发布逻辑、M3、Hop、Seam、六项专业能力和历史运行。

next_reverification:
先用合法内容/无合法内容、已发布/准备发布、首次/同幂等键重复提交的确定性正负控制证明分支；
随后在同一冻结 FULL 会话依序验证 T1→T2→T3→T4→R1。

model_calls_before_failure: `本 REBASE 为 0；仅重放已保存 RAW。`

side_effects: `P0 零 Dify/M2 写入、零真实发布；保护计数 1568/117，schema 无漂移。`

## P1 · 完整链可达性硬门

observed_failure:
当前发布图 69 个节点中不仅没有测试发布写回分支，也没有 `REGISTER_FEEDBACK` 写回和
`CLOSE_CYCLE / 下一周期` 写回分支。修复本 Prompt 明确允许的 `RECORD_PUBLISH` 后，T3/T4/R1
仍无法形成冻结标准要求的数据库记录。

frozen_target:
FULL T1→T2→T3→T4 与 RECOVERY R1 必须形成发布、反馈、周期收口和幂等恢复的真实测试域闭环。

candidate_sources:

- `CONTRACT_OR_INTENT`
- `SYSTEM_UNDER_TEST`

confirmed_origin: `CONTRACT_OR_INTENT`

evidence:

- 只读 preflight `UAPP_S5_FINAL_TWO_BLOCKER_PREFLIGHT_v1.0.py` exit `2`；
- 当前图明确缺少发布、反馈、周期收口三类写回执行节点；
- 本 Prompt 的允许变化面只点名 `action=RECORD_PUBLISH → ... → M2 test publish API`，没有授权
  修改 `REGISTER_FEEDBACK` 或 `CLOSE_CYCLE / OPEN_NEXT_CYCLE`；
- M3 是受保护对象且其发布图本身不写 M2，不能把后续真实写回委托给 M3；
- P1 时模型调用为 0，保护计数仍为 `1568/117`。

mutation_target: `NONE`，直到 Founder 明确是否把两个缺失的 UAPP 写回接缝纳入本 REBASE。

protected_targets:
M2 schema/服务语义、M3、Hop、Seam、六项专业能力、冻结输入和判据。

next_reverification:
若授权扩展，仅在 UAPP 增加通用测试反馈写回与周期收口/下一周期最小接缝，并将它们纳入同一 P1
正负、反向、幂等和非测试保护控制；不增加正式输入或模型预算。

model_calls_before_failure: `0`

side_effects: `零 Dify/M2 写入，零真实发布。`
