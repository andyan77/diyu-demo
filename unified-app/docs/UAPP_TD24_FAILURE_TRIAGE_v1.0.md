# FAILURE TRIAGE · TD-UAPP-24 规范纠正传播接缝

`task_id: DIYU-V1-UNIFIED-DIFY-APPLICATION-001`

`authority: Founder TD-UAPP-24 Execution Prompt v1.0 / GRANTED_2026-08-30`
`predecessor_gate: UAPP_CORRECTION_GATE_v1.0.json / 9220a7bd587ec030fa340892609addab15cb70432199924285e1b1fa634a95d7`

## observed_failure

用户明确把制作规模从一人改为两人。M3 在真实运行中识别到了这项纠正，但统一应用没有把它写进规范任务状态：`production.profile` 及字段版本保持旧值，两份依赖旧值的 Production Director 产物仍可用，最新旧 PD 又被绑定给 Publishing & Packaging，并产生了新的包装产物。

## frozen_target

自然语言中的明确纠正必须先于 artifact 选择和能力调用进入现有规范任务状态；依赖旧值的直接与传递产物必须失效；无合法新上游时受影响分支精确停下，不生成新包装；无关字段、产物和保护面不变化。

## candidate_sources

- `CONTRACT_OR_INTENT`：已由 Founder 新 Prompt 冻结，未发现语义缺口。
- `ORACLE_OR_CRITERION`：正式标准直接检查真实会话变量、artifact 账本、节点输入和产物，不以模型自述判定。
- `CHECKER_OR_FIXTURE`：旧正式失败由相邻真实节点和会话前后状态独立复算；新 Checker 尚未作为结论依据。
- `INPUT_ENVIRONMENT_OR_TOOL`：旧正式运行 HTTP 200，6 个 LLM 节点均成功，零重试、零内部重放。
- `SYSTEM_UNDER_TEST`：成立。
- `INSUFFICIENT_EVIDENCE`：不成立；最高失效接缝可定位。

## confirmed_origin

`SYSTEM_UNDER_TEST`。

最高失效节点是统一应用内部的“自然语言纠正 → 规范状态更新 → artifact 失效传播”接缝：

1. 当前字段更新只消费 Hop 面向目标能力生成的 capability envelope；
2. PP envelope 不需要 `production_profile`，因此用户明确纠正没有形成能力中立的规范 delta；
3. 当前 selector 在纠正状态建立前读取旧账本，旧 PD 仍被视为 CURRENT；
4. artifact 账本只有字段依赖，没有记录下游产物对上游 artifact 的直接引用，无法做可靠的传递失效；
5. 后置字段门看到的仍是旧规范状态，因此没有阻止旧 PD 下传。

M3 已真实识别纠正；Hop 只按现有职责投影目标能力需要的字段；Seam 与 PP 消费收到的合法外壳。没有独立证据证明这些保护对象失效。

## 三个盲区的接口结论

### A. 能力中立纠正

在 UAPP 内新增一条通用 `correction_delta` 提议与确定性复核接缝。提议可由现有分诊模型同轮给出，但只有用户原话逐字支持、字段属于现有规范表、task/scope/旧值/新值均可复算时才升级为用户确认 delta。该判断不读取 Hop envelope，也不依赖当前目标能力需要哪些字段。

### B. 产物血缘

沿用现有 `uapp_task_fields.artifacts` 账本，在每条下游 artifact 记录中增加最小直接 `upstream_fp` 引用；不新增会话变量、数据库或第二状态层。对既有无引用记录，只在同 task、能力兼容、产生时间和接受时间能够唯一确定最近合法上游时做确定性回填；有歧义即不猜。

### C. TOCTOU

顺序固定为：先复核并应用 correction delta、计算直接及传递失效，再让 selector 读取更新后的状态。`uapp_fields` 仍对 selector 身份和最新状态做第二次复核。未绑定时在 Seam/专业能力调用前转入精确停支，并只保存规范状态变化。

## 字段关系回指

现行规范字段表把 `production.profile` 与 `production.capacity_or_owner` 登记为两个独立字段，二者同属 `PRODUCTION` scope；现行合同没有把其中一个声明成另一个的别名或派生字段。当前真实状态中二者均来自同一 `TURN6.user_request`，且 `capacity_or_owner` 的正文是 `production.profile` 的逐字子集。

因此本轮不合并字段身份，也不自行建立永久派生规则。若同一用户纠正对一个字段形成可验证的最小文本替换，则只在另一字段满足“同 scope、同既有用户来源、包含同一旧片段、替换后仍由同一原话支持”时同步形成第二条用户来源 delta。当前“一人 → 两人”满足该条件；`facts.registered` scope 与来源均不同，必须保持不变。

## evidence

- old formal run: `592ba2d3-c6a4-41a7-a8e9-f33818be98c4`
- M3: `dca3cc1f-d1e0-409a-8967-4da81e866d00`
- Hop: `396cee36-13a2-4d02-a965-e5775223b353`
- Seam: `36923827-2138-410a-9613-f982af032b00`
- PP: `213101ba-cb9e-4585-b9f6-befdf3c8f9e0`
- old RAW sha256: `cc2b0c9aed9d28ef440182bc5c32290f660dae4774f1cbdc5ead11e81a2642dc`
- current failure state: rev 13 / sha256 `1ab76c1521ab46a48dbcafedcbcddd0325f73b6abb838151d06521a913caf8c8`
- current Git: `2d0668c723d49fa377a23722cdb7bd0af3c925ca` = upstream; worktree was clean before this successor record.
- current online graphs: UAPP `91a3984b2c3797d6741165b116fa3cb1`; PP/provider `8366328bf827bd0f460455d750d45c4f`; Seam `db49a3da8973d4fdcbe9ecf63bdf7e2a`; Hop `e38378c3c2a66b75aa7e645368c9e1ce`.

## mutation_target

最小允许修改对象：

- UAPP 现有分诊输出中的通用 correction proposal；
- UAPP 新增的确定性 correction delta 复核/状态更新节点及接线；
- 现有 artifact 账本的最小 `upstream_fp` 直接血缘；
- selector 与字段门读取纠正后状态的接线；
- 无合法上游时、Seam 之前的精确停支与单点状态保存；
- 直接构建、确定性控制、Gate、Runner、Checker、证据与只追加账本。

## protected_targets

M1、M2、M3、Hop、Seam、PP b2/provider、其余五项专业能力、M2 schema/业务数据、历史 Gate/RAW/Result/Triage/workflow 行、PRD/任务合同、main/origin-main 均不得修改。

## next_reverification

先在当前发布图的只读副本上构建 successor candidate，并完成能力中立纠正、字段版本、来源等级、同值/模糊/跨 task、直接与传递失效、TOCTOU、无新 PP、保护面和 Checker 区分力的正负控制。全部通过并冻结新 Gate 后，才发布候选并执行唯一一次正式自然语言验证。

## model_calls_before_failure

继承旧正式失败：顶层 1；LLM 节点 6；失败 0；人工重试 0；平台内部重放 0。当前 successor 施工至本记录：模型调用 0。

## side_effects

当前 successor 尚未发布候选、未运行模型、未写 M2。只在任务分支新增本记录和派生进度快照。旧失败会话、旧 RAW、历史 workflow 行与线上图均未改。
