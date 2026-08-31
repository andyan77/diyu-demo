# FAILURE TRIAGE · FULL-01:T2 publish writeback

task_id: `DIYU-V1-UNIFIED-DIFY-APPLICATION-001`

observed_failure:
T2 在同一 conversation 正确识别 `RECORD_PUBLISH`，但没有创建测试发布记录；流程继续进入 M3，向用户重新询问主目标与内容方向。

frozen_target:
T1 产生真实 Content Brief 后，T2“这条我已经发出去了。”必须登记一个 `is_test=true / is_simulated=true` 的发布实例，并绑定同任务的内容版本；不得连接真实平台。

candidate_sources:

- `SYSTEM_UNDER_TEST`
- `CHECKER_OR_FIXTURE`

confirmed_origin: `SYSTEM_UNDER_TEST`

evidence:

- T1 run `2e5b9488-96d6-4167-88dc-5e0561e232c9` PASS，Content Brief artifact length `6348`，sha256 `a6aaa69f2af96ddbbda4b24a6567a8f91c4769bb22edf58412050fec8d5ce1dd`。
- T2 run `14d66ec7-09aa-4fd9-85ba-2dce90ec7c67` 与 T1 conversation 均为 `c38dc32e-837f-4a7b-ba6b-80ae5eb09945`。
- `uapp_route.action=RECORD_PUBLISH`、`route_mode=WRITEBACK`，说明自然语言动作识别正确。
- T2 的 `publish_instances=[]`、`content_versions=[]`；`FULL-T2-BINDING` 与 `FULL-02` 均 FAIL。
- T1 artifact 正文仍存在于有界存储，但 T2 的 writeback 路径未把它绑定为测试发布实例，并错误落回 M3。

mutation_target: `NONE`

protected_targets:
当前 REBASE 只授权上传资料登记接缝与 Fixture successor；发布 writeback 接缝、M3、M2、Hop、Seam、专业能力及 schema 未获修改授权。

next_reverification:
T3/T4/RECOVERY 依赖 T2，全部停止。需要后继 REBASE 授权 UAPP `RECORD_PUBLISH` 的测试域内容版本与发布登记接缝，再从 T2 定向复验。

model_calls_before_failure:
本包累计 9 个顶层正式运行、41 次 LLM 节点尝试；T2 本次 1 个顶层运行、4 次 LLM 节点尝试。

side_effects:
没有 publish instance、feedback、真实发布或非测试写入；保护计数仍为 1568/117，schema 无漂移。
