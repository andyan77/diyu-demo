# `DIYU-V1-UAPP-ACCEPTED-ARTIFACT-BINDING-001` · 统一应用已接受上游产物绑定修复

`task_mode: NEW_TASK`｜`parent_task: DIYU-V1-UAPP-PROGRESSIVE-CANVAS-001`
`related_task_read_only: DIYU-V1-PP-BOUNDARY-SUCCESSOR-001`
`branch: codex/v1-uapp-progressive-canvas-001`｜`planning_observed_head: 405cc3d`
授权：《统一应用已接受上游产物绑定修复与 D3 收口 Execution Prompt》（Founder 2026-08-30）

## 状态：`CHECKPOINT`（Phase A–D 完成，Phase E 未执行）

**结论一句话：修好了，也在离线控制上验证了 12/12，但正式集成验证跑不了——
冻结预算给了 2 个顶层回合，现场证据显示最短链需要 3 个。**

## 一、Phase A · 根因（零模型、可复算）

`confirmed_origin = SYSTEM_UNDER_TEST · 统一画布产物持久化接缝`
`highest_failing_node = uapp_persist + uapp_save 单槽位无条件覆盖`

账本知道 PD 合法，正文却没了：

| 能力 | turn | accepted | stale | fp | len |
|---|---|---|---|---|---|
| CONTENT_BRIEF | 2 | true | **true** | `2e41c4b7…` | 6600 |
| CREATIVE_SCRIPT | 4 | true | **true** | `95ecee48…` | 6016 |
| **PRODUCTION_DIRECTOR** | **6** | **true** | **false** | `099061257c9677bd` | **10121** |
| PUBLISHING_PACKAGING | 7 | **false** | true | `757af420…` | 14984 |

唯一正文槽位 `conversation.uapp_last_artifact` 装的是 **PP@t7** 的产物
（14984 字，指纹精确命中账本第 4 条）。`uapp_persist` 只要新产物非空就整体覆盖，
不看 accepted、不看 stale、不按能力分格。

四候选根因：①正文从未持久化 **CONFIRMED**（M2 本任务 `artifacts=0` `snapshots=0`，
且 `artifacts` 与 `content_versions` 两张表**都没有正文列**）；②已持久化无引用 REFUTED；
③选择器只读单槽位 **CONFIRMED_BUT_DOWNSTREAM**；④取到后被丢弃 REFUTED——
被取到的是 PP 自己的旧产物，`uapp_fields` 血缘门**正确拒绝**了它
（`REJECTED / NO_LEDGER_MATCH`）。

影响面：全图 49 节点里只有 `uapp_persist`、`uapp_save`、`uapp_hop` 三处引用该槽位。

## 二、Phase B · 最小实现（零模型，只同步 draft，**未发布**）

| # | 改了什么 | 为什么 |
|---|---|---|
| 1 | `uapp_persist` → 按指纹分格的有界产物存储写入者 | 未接受的新产物不再覆盖已接受的旧正文；账本里 accepted 且非 STALE 的条目优先保留 |
| 2 | `conversation.uapp_last_artifact` → 该存储本身 | 正文仍然**只有一处**，不产生平行副本 |
| 3 | **新增** `uapp_pick_upstream` 确定性选择器 | 同 task／已接受／非 STALE／能力兼容／正文可取回且摘要现场复算一致；任一不成立 fail-closed 只问一个问题 |
| 4 | `uapp_hop` 取回接线改指选择器输出 | 不再直连单槽位 |

节点 49→50，边 51→52。`uapp_fields`、`uapp_state`、`uapp_seam`、`uapp_m3`、
`uapp_route`、`uapp_delivery`、`m1_compiler` 逐字节未动。**未新增会话变量**——
既有会话的 12 个变量与图里声明一一对应，新声明不会为既有会话补建行，取回会 fail-open。

**M2 没被用作正文真源**：它有完整的 artifact/version API，但两张表只存
`content_hash` / `content_ref`，没有正文列。要它充当就必须改 schema —— 不自行扩大授权。

## 三、Phase C · 确定性正负控制 **12/12**

C-01 已接受 PD + 后续未接受 PP → 选 PD｜C-02 摘要一致才放行｜C-03 隔轮仍可取回｜
C-04 点名解析｜C-05 未接受不选｜C-06 STALE 不选｜C-07 跨 task 不选｜
C-08 摘要不符 fail-closed｜C-09 只有未接受 PP → 精确询问不自循环｜C-10 并列 → 问用户｜
C-11 五条单点/双点变异各自翻转｜C-12 保护面零漂移。

`FAILURE TRIAGE 002`：首轮 10/12。C-04 是我夹具写错（把点名用例当成未点名）；
C-11 一是夹具被另一条独立条件遮蔽、二是兼容性由两道不可互换的守卫实现需双点变异隔离、
三是**变异暴露了我新节点里一处真实崩溃路径**（候选非空但都不在优先级清单时
`max()` 抛错），已补 fail-closed 守卫。实现侧本轮仅此一处改动。

## 四、Phase D · 判据已冻结（早于任何模型结果）

`unified-app/stages/UAAB_GATE_v1.0.json`
sha256 `51219a56ef0bd96d74f5651ecf70fac8f9a53dc383b4ca5e106805e1ae0108c4`
含 E-01…E-10 原文、候选图哈希、选择规则、失败自动回退规则与预算。

## 五、Phase E 未执行 —— 现场证据推翻了 2 回合的前提

**场景 A 已排除**：历史已接受的 PD 正文**没有任何合法可取回真源**。
会话槽位被 PP 产物覆盖；M2 不存正文且本任务 0 行；
候选画布**全部会话**的 `uapp_last_capability` 逐个枚举过，
**没有一个是 `PRODUCTION_DIRECTOR`**。从 Dify 执行日志取回再写进会话变量属直接写库，FORBIDDEN。

**场景 B 需要 3 个回合，不是 2**：

- `PRODUCTION_DIRECTOR` 的 `envelope_check` REQUIRED 含 `script_or_equivalent_beats`（artifact 槽位）；
- `CONTENT_BRIEF` 与 `CREATIVE_SCRIPT` 的 REQUIRED **只有字段、没有 artifact 槽位**；
- 本会话 CB@t2 与 CS@t4 **都已 STALE**（`FIELD_CHANGED:facts.registered`，D3 那轮上传夹具触发的更正）；
- 所以没有非 STALE 的已接受 CS，PD 一轮产不出 artifact。

最短链（已冻结在 Gate 里）：

| 回合 | 目标 | 自然语言原文 |
|---|---|---|
| 1 | CREATIVE_SCRIPT | 这条的口播稿再给我一版。 |
| 2 | PRODUCTION_DIRECTOR | 这版口播稿可以，基于它告诉我这条该怎么制作。 |
| 3 | PUBLISHING_PACKAGING | 刚才那份制作方案可以，基于它给这条出标题和封面。 |

会话 `5cfcaf57`、`end_user s4ct-20260830001839`、`inputs={}`、**不再上传夹具**
（再传会再次触发 `facts.registered` 更正，把本轮新产的 CS 在下一轮置 STALE，自己毁掉链路）。

**我没有开跑**：超预算不自行做；也不把上游换成 CS 来凑——那会让 E-02 / E-03 按字面不成立。

## 六、成本与保护面

```yaml
top_level_workflow_runs: 0 / 2
deepseek_llm_node_attempts: 0 / 12
retries: 0    repeat_sampling: 0    ab_tests: 0    reviewer_calls: 0
```

候选画布**已发布图仍是 `99c3edf7`**（只同步了 draft `1aba8d45`，未发布）；
PP 已发布图与 provider 钉住的图都是旧稳定图 `788c8555`；
Seam `db49a3da`、其余八应用、`hop_pin` 零漂移；b1/b2 版本行保留；
M2 schema 与数据未动；`main` / `origin/main` 停在 `01a42b0`。

## 七、状态

```yaml
UAAB_ROOT_CAUSE:                      CONFIRMED / CURRENT
UAAB_DETERMINISTIC_CONTROLS:          PASS 12/12 / CURRENT
UAPP_ACCEPTED_UPSTREAM_ARTIFACT_BINDING: NOT_VERIFIED (NOT_CHECKED)   # 未做正式集成验证
D3_SUCCESSOR:                         NOT_STARTED
PP_BOUNDARY_SUCCESSOR_b2:             NOT_VERIFIED    # 维持
V-08B_FACT_TRACEABILITY:              NOT_VERIFIED    # 维持
V-08C_CTA_FIDELITY:                   NOT_VERIFIED    # 维持
CROSS_TURN_CORRECTION_PROPAGATION:    NOT_VERIFIED (NOT_CHECKED)
S4_OVERALL_ACCEPTANCE:                NOT_VERIFIED
S5: NOT_STARTED   main_merge: NOT_ALLOWED   terminal_state: UNSET   next_state: CHECKPOINT
```

## 八、唯一下一步

把 `top_level_workflow_runs` 从 2 提到 **3**（`deepseek_llm_node_attempts` 相应到 18），
按 Gate 里已冻结的三句自然语言原文跑一次，按已冻结的 E-01…E-10 判定。
判据、输入、实现都已冻结并提交，不需要任何其它改动。

## 九、REBASE v1.1 启动记录（2026-08-30）

Founder 已授权把三轮正式链预算版本化为 `3 / 18 / 0 retries`，任务身份保持
`DIYU-V1-UAPP-ACCEPTED-ARTIFACT-BINDING-001`。Gate v1.1 已在任何模型调用前冻结：
`sha256 069a5af02cfcd173e024c4cfd66c38f74005c1c6d26afdf8e7b19ba81d74d6a6`，
提交 `ee679e4d4623e0b98cac2e7190e2a5bf80bf1fc4`。

零模型预检结果 `PASS`：12/12 确定性控制复算通过，候选 draft 仍为 `1aba8d45`，
保护节点、M2 schema / 数据、PP / provider / Seam / Hop 均未漂移，运行中 workflow 为 0；
三轮不可压缩的现场前提仍成立。原始复算见
`unified-app/evidence/stages/uapp_artifact_binding/UAAB_REBASE_PREFLIGHT_v1.1.json`。

外部副作用状态：`PLANNED`——下一动作仅为发布 UAPP `1aba8d45`、重新发布 PP b2
`8366328b`、把 PP provider 对齐 b2；任一正式验收非 PASS 按 Gate v1.1 自动恢复稳定图。

## 十、REBASE v1.1 发布记录（模型调用前）

测试候选发布与重钉均已 `CONFIRMED`：UAPP 发布版 `1aba8d45`（50 节点 / 52 边），
PP 发布版 `8366328b`（15 节点 / 15 边），PP provider 实际钉住同一 `8366328b`；
Seam `db49a3da`、Hop `e38378c3` 未变。首次 UAPP 发布请求因标记名超过 20 字符返回
HTTP 400，现场回读证明 `FAILED_NO_EFFECT` 后仅缩短发布元数据再次提交，未改图、Gate、
Checker 或输入。完整回读见
`unified-app/evidence/stages/uapp_artifact_binding/UAAB_REBASE_PUBLISH_v1.1.json`。

当前成本仍为：顶层 workflow `0 / 3`，DeepSeek LLM 节点 `0 / 18`，模型重试 `0`。
下一动作：在冻结 conversation / end_user 下只运行 T1 原句一次，随后先判定 T1，
未满足预期即停止，不进入 T2。

## 十一、REBASE v1.1 · T1 正式运行与逐轮判定

T1 顶层 run `ec4b6bfe-2bc7-49f3-963b-7ffcf06dd376`，只运行一次、无上传、无重试。
真实路由为 `CREATIVE_SCRIPT`；六个专业能力中仅 CS 运行 1 次，其余五个均为 0。
CS artifact 长 3497，sha256
`65f58acb09de20b77ff1deb669e2210e5f128a4b06fbaab14fbf31cf9955b938`，以
`CREATIVE_SCRIPT@turn9` 独立追加进存储，账本 fp `3d7342e36d939c31`，非空、非占位。

T1 判定：`PASS / CURRENT`。累计成本：顶层 run `1 / 3`，LLM 节点 `6 / 18`，
失败 0，重试 0。原始与复算证据：
`unified-app/evidence/UAPP_RUN_UAAB_V11_T1.json`、
`unified-app/evidence/stages/uapp_artifact_binding/UAAB_T1_VERIFY_v1.1.json`。
下一动作：只运行冻结 T2 原句一次；T2 未通过即停止，不进入 T3。

## 十二、REBASE v1.1 · T2 正式失败与停止

T2 顶层 run `499acf64-4a71-48f1-9a7f-449b3d5a4fef` 只发起一次，原句、同一
conversation / end_user、`inputs={}`、无上传。选择器正确选中 T1 CS：同 task、
本轮原话「可以」构成接受、非 STALE，正文长 3497，sha256
`65f58acb09de20b77ff1deb669e2210e5f128a4b06fbaab14fbf31cf9955b938`。

正式失败发生在 `uapp_hop → uapp_fields` 绑定接缝：Hop 把完整 CS 正文抽取成较短的
`script_or_equivalent_beats`，指纹从 `3d7342e36d939c31` 变成
`95acca37e2df6679`；`uapp_fields` 按完整产物血缘门正确 fail-closed 为
`REJECTED / NO_LEDGER_MATCH`。因此 PD 虽真实运行一次，却没有收到合法绑定正文，
未产生 PD artifact，`uapp_persist` 为 `NO_NEW_ARTIFACT`。

同一工具节点第一次嵌套运行 `e8567fbd-b5dd-44cd-a098-84791579926d` 还发生 DeepSeek
SSL EOF；Dify 随后内部重放为 `0b411c1e-0698-4cb3-afd4-8a047e392057` 并成功。
人工／顶层重试为 0，但平台内部重放为 1，故冻结的 `retries=0` 也未满足。

按首个失败停止：T3 未启动，不重跑、不改 Gate / Checker / Fixture / 输入 / 实现，
E-01…E-11 均不得上调。累计成本：顶层 run `2 / 3`，LLM 节点 `12 / 18`，失败 1，
平台内部重放 1，重复采样 0。

## 十三、自动恢复与 CHECKPOINT

测试发布面已恢复并回读确认：UAPP `99c3edf7bd12172a4fb011b588f25e57`，PP 与 provider
均为 `788c8555aca09e6fa6d979f237f70157`；Seam `db49a3da`、Hop `e38378c3` 未变，
活动 workflow 为 0，候选与 b1/b2 历史 workflow 行保留。

T2 后测试会话存储只含旧 PP 正文与 T1 CS 正文，没有 PD，也没有 T3 PP；账本中的
T1 CS 已接受且非 STALE。`uapp_last_capability` 已推进为 `PRODUCTION_DIRECTOR`，但没有
对应正文；本合同不授权直接改写会话状态，故原样留证，不再复用该状态继续正式链。

当前状态：`FAIL → CHECKPOINT`。`UAPP_ACCEPTED_UPSTREAM_ARTIFACT_BINDING` 维持
`NOT_VERIFIED(INSUFFICIENT)`；D3 successor、PP b2、V-08B/C、S4 均不上调；
S5 未启动，main 不合并，terminal 未设置。完整证据见
`unified-app/evidence/stages/uapp_artifact_binding/UAAB_T2_FAILURE_AND_REVERT_v1.1.json`
与 `unified-app/stages/UAAB_RESULT_v1.1.json`。

**唯一下一步：** Founder 裁定是否建立新的版本化续行，授权修复
`uapp_hop → uapp_fields` 完整产物绑定不一致，并明确平台内部重放的处置规则；
当前合同不授权第二次修复或再次运行。

## 十四、Successor REBASE v1.2 · 模型调用前冻结

Founder 已授权同一 task 进入 successor REBASE v1.2。现场 fetch 后，branch / origin
均为 `225436d69cff68c76a0bb0bbe12dc519cf2fea09`，main / origin/main 均为
`01a42b0ed97344a67302ecb6778ae4a772eb28b2`；UAPP、PP/provider、Seam、Hop 稳定图与父合同
完全一致，活动 workflow 为 0。

最小候选从恢复后的稳定 draft 重新构建，不复用失败候选：只改 `uapp_fields`、
`uapp_hop` 取回接线、`uapp_persist`、`uapp_save`，新增 `uapp_pick_upstream`。
完整正文身份改为 selector 直接输出；Hop 仍只处理普通字段；没有非空新 artifact 时能力标记
保持上一合法值。候选 50 节点 / 52 边，canonical graph sha256
`75c0afbeb6f9bacba514b221702d113cbca7dcfb5dd857b594945f552e9d3ef7`。

零模型确定性控制最终 `12/12 PASS`，含 12 个正例与 13 个单变量负例。首次夹具把
`accepted=false` 与含「可以」的话术放在一起，第二次夹具用序列化文本搜索多行正文，均确认是
Checker 夹具／检测器问题；只修对应夹具后全量重跑，未修改被测实现或冻结业务判据。

影响面证明 successor 的新绑定分支只适用于 PD / PP，T1 的 CREATIVE_SCRIPT 无上游路径不可达；
现场 T1 正文 3497 字、sha256 `65f58acb…5b938`、fp `3d7342e36d939c31`、bfp
`4af627e012e74e3a`，store / ledger 身份、accepted / stale 状态全部保持。因此路径在任何模型调用前
冻结为 **A：继承 T1，只跑 T2、T3**；预算 2 个顶层 run / 12 次 LLM 节点尝试。

Successor Gate：`unified-app/stages/UAAB_GATE_v1.2.json`，sha256
`dbe4c023256e378d93827094b5c762f7c1b67b1c7528fff92fbbb84b219ea622`；输入文件 sha256
`f669c5163533807e47c827f9c08792f014ce4743e0df35ef23adb9b9b3ac29ca`。下一动作仅为提交冻结，
随后发布候选并运行 T2 一次；T2 非 PASS 即停止且不运行 T3。

## 十五、Successor REBASE v1.2 · 测试候选发布（模型调用前）

Gate 已先于发布提交于 `5aedf67`，其后发布动作仍为零模型调用、零数据库直接写入。
UAPP 候选已发布为 workflow `28059850-1745-4e6d-bfac-0fbe278c5615`，canonical graph
sha256 `75c0afbeb6f9bacba514b221702d113cbca7dcfb5dd857b594945f552e9d3ef7`，
50 节点 / 52 边。Dify 存储图 md5 为 `91a3984b2c3797d6741165b116fa3cb1`。

PP b2 已原样重发为 workflow `da7311a2-76b3-4077-8024-1537f803cd76`，图 md5
`8366328bf827bd0f460455d750d45c4f`；provider 实际钉住同一版本与同一图。Seam
`db49a3da8973d4fdcbe9ecf63bdf7e2a`、Hop `e38378c3c2a66b75aa7e645368c9e1ce`
保持不变，活动 workflow 为 0。完整发布前后回读见
`unified-app/evidence/stages/uapp_artifact_binding/UAAB_SUCCESSOR_PUBLISH_v1.2.json`。

当前 successor 正式成本仍为顶层 run `0 / 2`、LLM 节点尝试 `0 / 12`、人工重试 0、
平台内部重放 0。下一动作只运行冻结 T2 原句一次；逐轮判定非 PASS 时立即停止并恢复稳定发布面。
