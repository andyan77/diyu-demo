# Execution Prompt — M2 v1.1 Rebase / Errata 001

## 0. 任务身份与使用方式

本文件是现有 M2 工程任务的最小治理重对齐和验收收口补丁。

它不是新的 Root Execution Prompt，不建立新任务，不替代或重写原 M2 P0，不授权重建数据库、重新创建 Dify 候选、重跑全部工程施工或开启新一轮开放式审查。

本文件必须在现有任务身份、分支、worktree、数据库、Dify 候选、Manifest、Attempt、失败路径和外部副作用基础上执行。

```yaml
task_id: DIYU-V1-M2-BUSINESS-PERSISTENCE-VERSION-FEEDBACK-001
task_entry_mode: REBASE_TASK
task_type: MIXED
risk_level: HIGH

root_execution_prompt:
  path: decision-chain/docs/M2_ENGINEERING_EXECUTION_PROMPT_v1.1.md
  sha256: 8008bebd04b35037e16f5462ea1b7284db7dec943e954263762bbdb4688bb0c6

task_contract_payload:
  mode: REFERENCE
  contract_ref: decision-chain/docs/M2_ENGINEERING_EXECUTION_PROMPT_v1.1.md#3-稳定-task-contract
  contract_change: NONE
  previous_task_contract_hash: 4d14eb35c065b650b0380b0c309e0e08ec32e3aa608ece4d62e8d27b97450830
  task_contract_hash: 4d14eb35c065b650b0380b0c309e0e08ec32e3aa608ece4d62e8d27b97450830

invalid_declared_hash_in_root_prompt:
  value: e17b354b97d53bfa52eeb30ffca50970e5469acabee98b3cfc32a1031b1b90ca
  status: INVALID_SELF_DECLARED_HASH
  treatment: 保留原文作为历史，不得继续作为有效 Task Contract 哈希引用
Founder 将本文件准确版本放入仓库并明确通知执行，表示授权执行本文件定义的最小 Rebase/Errata 工作包；不扩大原 M2 v1.1 的产品范围、目标环境或受保护资产边界。
如果执行时同一任务已经继续推进，以目标系统、Git、账本和当前副作用为准重建现场，不得把本文件编译时观察值冒充当前值。
1. Rebase 原因与准确裁决
本次 Rebase 处理三类问题。
1.1 阶段基线发生后继变化
decision-chain/docs/V1_DECISION_CHAIN_STAGE_BASELINE_v0.2.md 仍将以下内容记录为当时状态：
- 单账号子合同 v0.1 尚未接受；
- 当前只授权 V1-REBASE-EP00-CURRENT 只读预检；
- 业务持久化和 Dify 工作流施工未授权；
- 下一步是两份 EP-00。
这些内容在该文件冻结时真实，但已经被后继、权威更高的事件更新：
- V1_SINGLE_ACCOUNT_SLICE_CONTRACT_v0.2.md 已被 Founder 接受；
- 两份 EP-00 已完成；
- M0.3 四份共享合同已接受；
- Phase 0 共享编译前言已生效；
- M2 v1.1 已采用进仓库；
- Founder 已就准确 task_id: DIYU-V1-M2-BUSINESS-PERSISTENCE-VERSION-FEEDBACK-001 明确答复“就是要启动，铁律适用”。
因此：
Stage Baseline v0.2 中的历史授权状态
≠ 当前 M2 授权状态
但 Stage Baseline v0.2 的以下约束继续有效：
- A/B 阶段的 PARTIAL 历史不得改写；
- 已部署主 Chatflow、对话编排修复和既有能力属于受保护基线；
- G-01～G-12 不得因为单个模块施工被整体宣称关闭；
- 不得声称 V1 已全面通过；
- 不得声称 Skill 集成后没有质量下降；
- 不得声称某模型或 Skill 普遍更优；
- 不得声称当前结果已跨品牌、跨行业泛化；
- 不得声称当前系统已经生产可用。
本任务不得修改或覆盖 V1_DECISION_CHAIN_STAGE_BASELINE_v0.2.md。后继 V1_DECISION_CHAIN_STAGE_BASELINE_v0.3 属于中央规划侧共同治理资产，不是 M2 工程执行侧的施工责任。
本 Rebase 仅负责让当前 M2 任务明确引用：
Stage Baseline v0.2 的继续有效约束
＋
后继合同、预检、共享合同和 Founder 授权
1.2 原 Root Prompt 的自证哈希错误
原 Prompt 把稳定 Task Contract 哈希写成：
e17b354b97d53bfa52eeb30ffca50970e5469acabee98b3cfc32a1031b1b90ca
但按原 Prompt 自己规定的边界，精确提取 TASK_CONTRACT_BEGIN 与 TASK_CONTRACT_END 之间 YAML 围栏内 UTF-8 字节，正确 SHA-256 为：
4d14eb35c065b650b0380b0c309e0e08ec32e3aa608ece4d62e8d27b97450830
Founder 已裁决按独立复算值登记。
本 Rebase 不修改原冻结文件，不建立新的业务合同内容；所有后继 Manifest、Checkpoint、验收记录和最终回执统一使用：
task_contract_hash
= 4d14eb35c065b650b0380b0c309e0e08ec32e3aa608ece4d62e8d27b97450830
1.3 连续性字段重新分层
原 Prompt 把 task_entry_mode: NEW_TASK 放入了稳定 Task Contract。
从本 Rebase 开始：
- 稳定 Task Contract 继续按正确哈希只读引用；
- task_entry_mode 只记录在 continuity overlay 和 Run Manifest；
- 当前模式是 REBASE_TASK；
- 后继正常续作使用 CONTINUE_TASK；
- 不因进入模式变化修改稳定 Task Contract 哈希。
2. 权威真源
执行前必须读取并核验准确版本：
source_of_truth:
  founder_decisions:
    - Founder 已接受单账号纵向切片合同 v0.2
    - Founder 已接受 M0.3 四份共享合同和 Phase 0 当前语义
    - Founder 已明确授权准确 M2 task_id 启动工程执行
    - Founder 当前投递本 Rebase/Errata Prompt，授权同一 task_id 完成最小重对齐和剩余 P0 收口

  governance_protocols:
    - /mnt/c/Users/Administrator/Documents/Codex/Diyu-V1-Planning/执行Prompt生成总则_规划侧约束框架_v1.2.md
    - /mnt/c/Users/Administrator/Documents/Codex/Diyu-V1-Planning/受边界约束的执行总负责人协议_v1.3.md

  frozen_product_contracts:
    - decision-chain/docs/V1_DECISION_CHAIN_REBASE_PRODUCT_CONTRACT_v0.1.md
    - decision-chain/docs/V1_SINGLE_ACCOUNT_SLICE_CONTRACT_v0.2.md
    - decision-chain/docs/V1_M0_SHARED_CONTRACT_TASK_CONTEXT_SNAPSHOT_v0.1.md
    - decision-chain/docs/V1_M0_SHARED_CONTRACT_EIGHT_CAPABILITIES_v0.1.md
    - decision-chain/docs/V1_M0_SHARED_CONTRACT_VERSION_PUBLISH_FEEDBACK_v0.1.md
    - decision-chain/docs/V1_M0_SHARED_CONTRACT_WRITE_PERMISSION_RECOVERY_v0.1.md
    - decision-chain/docs/V1_M1_M4_CONSTRUCTION_PROMPT_SHARED_PREAMBLE_v0.1.md

  historical_stage_baseline_with_current_constraints:
    - decision-chain/docs/V1_DECISION_CHAIN_STAGE_BASELINE_v0.2.md

  preflight_evidence:
    - decision-chain/docs/V1_REBASE_EP00_CURRENT_PREFLIGHT_v0.1.md
    - decision-chain/docs/V1_SINGLE_ACCOUNT_SLICE_EP00_PREFLIGHT_v0.1.md

  task_contract:
    - decision-chain/docs/M2_ENGINEERING_EXECUTION_PROMPT_v1.1.md
    - 本 Rebase/Errata Prompt

  current_state_authorities:
    - Git 远程默认分支与当前 refs
    - collab-ledger 当前任务记录
    - 现有 M2 worktree 和任务分支
    - PostgreSQL、应用容器和迁移实际状态
    - 当前 Dify 1.16.1 目标环境、准确候选对象和当前发布版本
    - 原始测试、运行、迁移、权限、Reviewer 和外部副作用证据
若 PROJECT_INDEX.md、README、Stage Baseline v0.2 与后继 Founder 授权记录存在状态冲突：
- 不得反向取消已经明确发生的 Founder 授权；
- 不得修改历史文件使其假装当时已经授权；
- 在当前 M2 Rebase 记录中写明旧状态、后继事件和当前有效状态；
- 把共同索引和 Stage Baseline v0.3 更新登记为中央规划侧后继事项。
3. 编译时观察基线
以下仅是本 Prompt 编译时观察值。执行侧必须重新 fetch、查询目标系统并记录 Delta。
observed_at_rebase_compile:
  repository: /home/faye/diyu-demo
  remote_default_branch: main
  origin_main: 78a4ad8a932592bac0b45e9ce835d3dc77ce7374

  m2_worktree: /home/faye/diyu-demo-worktrees/m2-business-persistence-version-feedback-v1
  m2_branch: task/m2-business-persistence-version-feedback-v1
  local_m2_head: f09e2923a7b57efbcb94cd83ed54c5b6cd94b3c4
  remote_m2_head: f09e2923a7b57efbcb94cd83ed54c5b6cd94b3c4

  m2_worktree_observed_untracked:
    - business-persistence/M2_ACCEPTANCE_EVIDENCE.md

  main_worktree_observed_unrelated_state:
    - modified: collab-ledger/L3_ATTEMPTS_AND_EVIDENCE.md
    - untracked: m3-account-content-operator-semantic-v1.0/

  stage_baseline_v0_3_present: false
这些未提交和未跟踪对象均可能属于当前执行或其他任务：
- 不得删除；
- 不得覆盖；
- 不得吸收到错误任务；
- 不得把 main 工作树的无关改动带入 M2 分支；
- M2_ACCEPTANCE_EVIDENCE.md 必须先核验、纠正，再决定是否作为本 task_id 证据提交；
- 文件自报 PASS 不构成正式验收结论。
4. 不变的稳定合同
本 Rebase 不改变以下内容：
task_id: DIYU-V1-M2-BUSINESS-PERSISTENCE-VERSION-FEEDBACK-001
task_contract_hash: 4d14eb35c065b650b0380b0c309e0e08ec32e3aa608ece4d62e8d27b97450830

p0: 完整继承原 M2 v1.1
p1:
  enabled: false

allowed_final_states:
  - DONE
  - BLOCKED
  - FAILED
  - INVALID

partial_allowed: false
next_stage_default: false
remote_target: origin/task/m2-business-persistence-version-feedback-v1
main_merge_authorized: false
production_authorized: false
real_social_publish_authorized: false
原 M2-AC-00 至 M2-AC-17 一条不删、一条不降级。
不得通过本 Rebase：
- 删除验收标准；
- 把失败项改成“不在范围”；
- 用“已知限制”替代原 P0；
- 将旧 Demo 兼容从 M2-AC-14 中移除；
- 将并发裸 500 从 M2-AC-12 中移除；
- 用 API 测试替代明确要求的当前 Dify 候选运行；
- 用 Founder Dify 实测替代技术验收；
- 把 M2-AC-16 的过期证据标为当前；
- 在 M2-AC-17 尚未通过时声称 DONE。
5. 本轮 Active Work Package
本轮只执行以下剩余和受 Rebase 影响的工作。
R-01：恢复同一任务现场
执行侧必须：
1. 核验同一 task_id 的 Manifest、Checkpoint、分支、worktree、数据库、迁移、容器、Dify候选和副作用；
2. 核验本地与远程 M2 ref；
3. 查询而不是猜测 PostgreSQL、应用和 Dify 当前状态；
4. 保存现有未提交证据文件，不覆盖、不删除；
5. 形成新的 Rebase Manifest 版本，引用原 Manifest、正确 Task Contract 哈希和本 Prompt；
6. 不建立新任务，不重复创建数据库、角色、迁移或 Dify候选。
R-02：登记治理 Errata
在现有 M2 任务分支内持久化最小 Rebase/Errata 记录，至少包含：
- 原 Prompt 文件和 SHA-256；
- 错误声明哈希 e17b...；
- 正确 Task Contract 哈希 4d14...；
- Founder按正确值登记的裁决引用；
- Stage Baseline v0.2 中继续有效的历史和能力边界；
- 被后继合同、预检和 Founder授权更新的状态字段；
- 当前 task_entry_mode = REBASE_TASK；
- 稳定合同内容未变化；
- Stage Baseline v0.3 和共同索引更新属于中央规划侧后继事项。
不得原地修改：
- M2_ENGINEERING_EXECUTION_PROMPT_v1.1.md；
- V1_DECISION_CHAIN_STAGE_BASELINE_v0.2.md；
- 产品合同；
- 四份共享合同；
- Phase 0 前言。
R-03：重新核验当前 main 对 M2 的影响
比较：
原 M2 起算基线
→ 当前 origin/main
→ 当前 M2任务分支
只回答：
- 当前 main 新增了哪些与 M2 授权、合同、接口、受保护资产有关的变化；
- 哪些已有 M2 证据仍为 CURRENT；
- 哪些证据因代码、迁移、容器、Dify或合同变化而 STALE；
- 哪些项目需要定向复验。
不得默认全量推倒重做，也不得静默继承旧 PASS。
R-04：关闭 M2-AC-12 的并发裸500缺口
现有执行记录披露：
create_version 使用 max(version_no)+1
同一 artifact 高并发创建时可能撞唯一约束并返回裸 500
该问题不能以“概率低”“重试即可”或“不在范围”关闭，因为原合同明确要求：
- 并发冲突不得静默覆盖；
- 冲突必须得到可恢复结果；
- 重试不得重复创建；
- 失败不得出现伪成功或无边界裸 500。
执行侧必须：
1. 在真实 PostgreSQL 上建立可稳定复现的并发测试；
2. 使用原 M2授权内的最小技术方案修复；
3. 让并发结果成为明确的成功、幂等命中或可恢复冲突；
4. 不把数据库异常栈直接暴露为普通 500；
5. 保留失败复现和修复后证据；
6. 只复验直接和传递影响范围。
具体锁、序列、原子分配、重试或约束处理方式由执行侧自主决定，不写入产品合同。
R-05：完整关闭 M2-AC-14 旧Demo兼容
原 Prompt 明确要求：
旧3槽/5槽快照和旧产物
可兼容读取或显式导入
当前证据只覆盖部分 5 槽任务状态快照，且 Founder Test Package 仍曾写“旧 Demo 兼容没做、不在本次验收范围”。
这与 M2-AC-14 冲突。
执行侧必须：
1. 只读定位仓库内真实存在的旧 3 槽、5 槽快照格式和历史 Matrix/Campaign/Brief/生产产物；
2. 对实际存在且可核验的旧格式完成最小兼容读取或显式导入；
3. 保留来源身份和导入 discriminator；
4. 不把测试身份、旧 Demo运行或缺失历史升级成真实业务历史；
5. 不修改 Dify旧会话、内部表或历史运行；
6. 对确实不存在、无法取得或无法确定格式的对象，提供穷尽检索证据并标记 NOT_VERIFIED，不得补造 fixture 后宣称旧兼容完成；
7. M2-AC-14 只有在合同要求的实际兼容面成立后才能 PASS。
R-06：纠正验收证据状态
逐项复核现有 M2_ACCEPTANCE_EVIDENCE.md，至少纠正以下逻辑：
- M2-AC-12 在并发裸 500 未关闭前不能 PASS；
- M2-AC-14 在 3 槽和旧产物兼容未关闭前不能 PASS；
- M2-AC-16 在 Dify候选证据对最终 commit、容器和配置已经过期时不能写成“PASS但有限制”；
- M2-AC-17 在 Founder尚未实际验收时必须为 NOT_VERIFIED；
- 测试数量、HTTP 200、文件存在、模型自评或“底层已实现”不等于验收通过；
- 所有证据必须绑定最终 commit、迁移 head、应用镜像、数据库状态、Dify候选版本和观察时间；
- 已过期证据明确标记 STALE，不得用说明文字掩盖。
纠正后的文件才允许提交。
R-07：更新Founder实测包
Founder Test Package 必须与最终候选一致。
执行侧必须：
- 删除或纠正“旧 Demo兼容不在本次验收范围”等违反原合同的表述；
- 更新最终 commit、测试身份、Dify app ID、版本和运行入口；
- 用自然语言说明六步场景；
- 明确 Founder只判断产品意图、跨会话恢复和业务价值；
- 不要求 Founder判断 Schema、迁移、并发、权限、Git或技术缺陷；
- 不把纯技术工作流描述成最终 M1自然交互体验；
- 不把测试发布或人工反馈描述成真实经营结果。
R-08：刷新真实Dify候选证据
M2-AC-16 要求当前最终候选在准确目标环境运行。
执行侧必须：
1. 确认目标是本项目实际使用的 Dify 1.16.1 环境；
2. 确认准确候选：
app_id = 8f34e8a3-fb49-4d3e-a222-3d666e767adf
若该对象已变化，以目标系统读回结果为准并记录 Delta；
3. 核验当前画布、发布版本、HTTP节点契约、测试身份、备份/导出和回滚条件；
4. 以最终应用代码、最终迁移 head、最终容器配置重新运行六步候选；
5. 保存准确运行 ID、节点状态、输入、输出、时间、候选版本和最终 commit绑定；
6. 必须包含至少一个权限或身份负向探针；
7. 不得使用指向其他 Dify版本或其他实例的工具结果冒充目标环境证据；
8. 如果当前无法访问准确目标 Dify，M2-AC-16 = NOT_VERIFIED，持久化可恢复 Checkpoint，不得用 API等价证据改判 PASS。
R-09：复验数据库权限、迁移和恢复
最终候选必须重新证明：
- diyu_app 不是超级用户，没有建库/建角色权限；
- diyu_app 对 dify、dify_plugin 的实际连接或读取被有效拒绝；
- 不只检查 SQL 文本或 TDR 声明，必须以该身份实际发起负向连接/读取；
- Dify内部表、结构和历史数据未被修改；
- 迁移 head 与最终代码一致；
- upgrade、允许范围内的 downgrade/rollback和重新 upgrade成立；
- 失败恢复不产生孤儿、重复记录或伪成功；
- 备份和恢复路径可定位。
R-10：审查预算纠偏
原 Prompt冻结：
independent_reviewer: one_context_isolated_read_only_agent
formal_review_budget: 1
repair_budget: 1
closing_verification: affected_scope_only
当前执行材料声称发生过多个独立审查单元。
本 Rebase：
- 不授权任何新的开放式正式 Reviewer；
- 不授权重新扫描全模块；
- 只允许执行负责人进行确定性自验和受影响范围收口；
- 必须保存已经发生的所有审查和发现，不得删除或重新命名以伪装成一次；
- 必须区分正式审查、并行子检查、修复验证和 affected-scope收口；
- 如果实际发生的正式审查数量超过预算，记录：
REVIEW_BUDGET_CONFORMANCE
= DEVIATION_REQUIRES_FOUNDER_ACKNOWLEDGEMENT
这不使已发现并修复的真实缺陷失效，也不阻止安全的剩余技术工作，但不得在最终回执中冒充“完全符合审查预算”。
不得由执行侧自行追认、豁免或重新解释历史审查事件。
R-11：定向回归
完成以上修复后，至少定向复验：
- 同一 artifact 高并发创建内容版本；
- 幂等重试和重复提交；
- 当前版本晋升与冲突；
- 旧 3 槽／5 槽及旧产物兼容；
- legacy import 命名空间隔离；
- 发布实例与反馈准确绑定；
- workspace和账号隔离；
- 素材撤回与发布竞态；
- Cycle N调整和有依据保持不变；
- M1/M3/M4接口边界；
- 迁移、回滚和恢复；
- 当前 Dify六步候选；
- 受影响的 Founder实测说明和验收证据。
未受影响的 Skill、M1、M3、M4生产链和历史 A/B不做开放式全量重跑。
R-12：远程收口
完成本轮 Delta 后：
- 只在现有 M2任务分支提交；
- 不创建第二个 M2分支；
- 不合并或推送 main；
- 不 force、amend、reset、squash或改写历史；
- 不吸收 main工作树和 M3目录的无关改动；
- 推送：
origin/task/m2-business-persistence-version-feedback-v1
- 核验本地最终 commit与远端 ref一致；
- 最终证据全部绑定远端可访问 commit；
- 工作树残留必须逐项说明归属，不得静默删除。
6. 授权范围
本 Rebase 允许：
- 在现有 M2 worktree和任务分支内修复原 P0未关闭项；
- 修改 business-persistence/ 下 M2代码、迁移、测试、文档和证据；
- 更新本 task_id对应的协作账本记录；
- 保存本 Rebase/Errata 记录；
- 在既有 diyu_business 开发/测试数据库边界内完成必要迁移、回滚和测试数据操作；
- 更新、发布和运行明确属于本 task_id的开发/测试 Dify候选；
- 推送现有远程 M2任务分支。
本 Rebase 不允许：
- 修改 V1_DECISION_CHAIN_STAGE_BASELINE_v0.2.md；
- 代替中央规划侧创建 Stage Baseline v0.3；
- 修改任何已接受产品合同、共享合同或 Phase 0前言；
- 修改六份 Skill、专业 Prompt或模型参数；
- 修改生产/共享 Dify应用；
- 修改 Dify内部数据库表或历史运行；
- 实现 M1自然语言路由；
- 实现 M3运营判断；
- 实现 M4生产能力；
- 自动发布、平台 OAuth、真实社交平台操作或全平台效果采集；
- 建立新数据库服务或通用数据平台；
- 合并或推送 main；
- 开启新一轮开放式 Reviewer审查；
- 把本 Rebase扩展成 M5集成验收。
7. 验收标准
criterion_id	必须成立的结果
M2-RB-01	同一 task_id、正确 Task Contract哈希、前序 Manifest、Attempt、副作用、分支和数据库状态完整继承，没有新建根任务或重复迁移
M2-RB-02	原错误哈希被明确登记为无效自证值，全部当前 Manifest和证据统一使用正确哈希 4d14...，原 Prompt未被原地修改
M2-RB-03	Stage Baseline v0.2继续有效约束与后继授权事实被明确分层；没有取消后继授权，也没有改写历史
M2-RB-04	当前 main相对 M2任务基线的影响已分析，证据 CURRENT/STALE/NOT_VERIFIED重新判定准确
M2-RB-05	create_version同一 artifact高并发不再产生无边界裸500，结果为成功、幂等命中或可恢复冲突
M2-RB-06	M2-AC-14要求的实际旧3槽/5槽及旧产物兼容面成立；缺失对象没有被补造
M2-RB-07	验收证据没有“PASS但证据过期”或“原P0未完成但不在范围”的矛盾
M2-RB-08	Founder实测包与最终候选一致，未要求Founder承担技术审查，未把测试数据冒充真实运营
M2-RB-09	准确Dify 1.16.1候选以最终代码、迁移和配置重新运行，证据绑定最终commit；否则AC-16诚实保持NOT_VERIFIED
M2-RB-10	数据库有效权限、Dify内部零改写、迁移/回滚/恢复以目标系统原始证据证明
M2-RB-11	审查历史和预算被如实分类，没有新增开放式审查，也没有删除超预算事实
M2-RB-12	原M2-AC-00～17重新获得一致、可复算的当前状态，没有删除或降低任何标准
M2-RB-13	最终本地与远端M2任务分支hash一致，未触碰main和无关工作树资产
M2-RB-14	在Founder尚未完成Dify验收时保持非终态，不声称DONE、不开放下一阶段


任一验收项没有完整证据时，只能是：
NOT_VERIFIED
不得使用：
PASS_WITH_LIMITATION
MOSTLY_PASS
BASICALLY_DONE
OUT_OF_SCOPE
规避原 P0。
8. 完成状态与停止条件
8.1 技术证据尚未收齐
如果 M2-AC-00～16 或 M2-RB-01～14 任一项仍为 NOT_VERIFIED：
execution_disposition = CONTINUE
task_final_status = null
module_delivery_state = IN_PROGRESS
next_stage_allowed = false
保存 Checkpoint、剩余项、解除条件和当前副作用后继续同一任务。
8.2 技术收口完成，等待Founder实测
只有以下全部成立：
- M2-RB-01～14 全部通过；
- M2-AC-00～16 全部对最终候选有 CURRENT证据；
- 当前Dify候选已按最终代码和配置真实运行；
- 远程任务分支收口完成；
- 没有未披露的权限、数据完整性或受保护资产问题；
才可以进入：
execution_disposition = CONTINUE
task_final_status = null
module_delivery_state = AWAITING_FOUNDER_DIFY_ACCEPTANCE
next_stage_allowed = false
然后停止功能扩张，向 Founder提交更新后的 Dify实测包。
8.3 DONE
只有 Founder实际完成 Dify画布产品与业务验收并明确接受，M2-AC-17 才能通过。
届时还必须确认：
- 没有仍未确认的正式审查预算偏差；
- 所有最终证据绑定远端最终 commit；
- M2-AC-00～17 和 M2-RB-01～14 全部通过；
- 没有用模拟/测试数据声称真实运营闭环；
- 没有声称经营结果提升、生产可用、M5完成或完整纵向链完成。
满足后才允许：
task_final_status = DONE
next_stage_allowed = false
M2 DONE 不授权：
- 合并 main；
- M5；
- 真实发布；
- 生产采用；
- 真实运营结论；
- 经营提升结论。
9. 最终回执
最终回执至少包含：
1. task_id 和 task_entry_mode；
2. 原 Root Prompt引用、SHA-256、错误自证哈希和正确 Task Contract哈希；
3. 前序 Manifest、当前 Rebase Manifest和Checkpoint；
4. 原起算基线、当前 main、当前任务分支和影响分析；
5. 本地与远端最终 commit；
6. PostgreSQL版本、数据库、角色、有效权限负向证据；
7. 最终迁移 head、upgrade/rollback/recovery结果；
8. Dify准确环境、app ID、候选版本、运行 ID、画布结果、备份和回滚证据；
9. create_version并发缺陷的失败复现、修复和回归；
10. 旧3槽/5槽和旧产物兼容的真实来源、适配结果和身份隔离；
11. M2-AC-00～17逐项最终状态；
12. M2-RB-01～14逐项最终状态；
13. Reviewer实际数量、角色、范围、发现、修复和预算符合性；
14. 全部失败Attempt和外部副作用；
15. Founder实测包和Founder接受/退回状态；
16. Stage Baseline v0.3与共同索引更新仍由中央规划侧承接的说明；
17. 明确声明：
ENGINEERING_VERTICAL_SLICE_VERIFIED = true/false
REAL_OPERATION_LOOP_VERIFIED = false/not_verified
BUSINESS_OUTCOME_IMPROVEMENT_VERIFIED = false/not_verified
M5_INTEGRATION_VERIFIED = false
PRODUCTION_READY = false
next_stage_allowed = false
不得用“代码已补”“测试通过”“基本完成”“大体可用”代替正式状态和逐项证据。
10. 强制停止
达到 AWAITING_FOUNDER_DIFY_ACCEPTANCE 后，执行侧必须停止功能扩张，只提交 Founder实测包。
达到合法 DONE 后必须立即停止，不得继续：
- 润色或改名；
- 顺手重构；
- 增加新表、新API或新平台能力；
- 启动新 Reviewer；
- 修改 Stage Baseline；
- 启动 M3、M4或M5；
- 合并 main；
- 操作真实平台。
M2_REBASE_ERRATA_PROMPT
= READY_FOR_EXECUTION

root_task_replaced
= false

new_task_created
= false

task_contract_changed
= false

task_contract_hash
= 4d14eb35c065b650b0380b0c309e0e08ec32e3aa608ece4d62e8d27b97450830

task_entry_mode
= REBASE_TASK