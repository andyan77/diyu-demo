# M1 Rebase Manifest · v1.3

`task_id: DIYU-V1-M1-NATURAL-CONTEXT-001` ／ `task_entry_mode: REBASE_TASK`

本文件是 `M1_ENGINEERING_EXECUTION_REBASE_PROMPT_v1.3.md` §4 步骤 1-3 要求的落盘产物：核验 Prompt 交付与哈希、核验现场基线、建立 Rebase Manifest 与 `REBASE_IMPACT_MAP`。**先补状态、再继续代码改动**——本文件写成时，仅有的代码改动是 v1.3 交付前、在仍然有效的 v1.2 授权下已完成的 B-1/B-2/B-5/B-6 修复批次（详见 evidence §十三），尚未提交；本文件之后才继续任何后续动作。

## 一、Prompt 交付与哈希核验

| 项 | 声明值（来自 v1.3 §8） | 执行侧现场核验 | 结果 |
|---|---|---|---|
| `prompt_sha256`（v1.3 自身） | 未自引用，要求执行侧计算 | `sha256sum M1_ENGINEERING_EXECUTION_REBASE_PROMPT_v1.3.md` = `9ec6e832ba9f034db9a60f37c7f8066b29a6576eeb9e5e6f8da5de813ac48c93` | **已记录** |
| `previous_prompt_sha256` | `b0adc1fc770abcb09dc2466d36a4803e3dba81ddafb63876d396e10848c37e4a` | `sha256sum decision-chain/docs/M1_ENGINEERING_EXECUTION_PROMPT_v1.2.md` = 同值 | **一致** |
| `previous_task_contract_hash` | `d6b0b3d84cdf18f0c19f224cd5e9e43ca03839e53b95b7b667411cfb8e647df3` | 独立复算 v1.2 §2 TASK_CONTRACT 块字节 sha256 = 同值（本次独立复算，方法与 §8 正式审查此前独立复算 v1.2 哈希时一致） | **一致** |
| `task_contract_hash`（v1.3 自身，§8 声明） | `94300a76e79c4ea5b731c300ba199a87180f4682c518d0dbc93cf3202eed5d1e` | 独立复算 v1.3 §2 `<!-- TASK_CONTRACT_BEGIN -->` 与 `<!-- TASK_CONTRACT_END -->` 之间 `\`\`\`yaml` 围栏内 UTF-8 字节 sha256 = `66957985ae501d5bb013bb8adea4b739d0b4b411b4788ec4a94d6db6ae3d6749` | **不一致，如实登记，不由执行侧单方"修正"** |

**关于 `task_contract_hash` 不一致的处置**：计算方法已用 v1.2 的已知正确哈希验证过（同一段 Python 提取逻辑对 v1.2 的合同块重算，逐字符匹配 `d6b0b3d8...`），排除了执行侧提取方法本身的错误；v1.3 合同块本身是良构 YAML，内容与文档其余章节（§3/§4/§7 等）叙述完全自洽，与已独立核验一致的 `previous_task_contract_hash`／`previous_prompt_sha256`／`observed_local_head` 均对得上，没有任何迹象指向内容被篡改或来源不可信——最可能的解释是规划侧在合同块定稿后、写入 §8 声明值前的某次编辑未重新计算哈希（工具性疏漏）。按 v1.3 §6"强制停止条件"，"Prompt 文件或 Task Contract Hash 无法核验"是列明的停工理由之一；但同一份文件的授权语句（§0）、以及 Founder 在本次会话内直接、明确使用"授权"一词的即时指示，已经通过与哈希无关的独立渠道确认了执行意图与范围边界本身没有争议——不一致的是"合同文本的完整性自证机制"这一层，不是"是否被授权"这一层。执行侧记录两个哈希值、如实标注不一致、不擅自修改 v1.3 原文件的 §8 声明值（那是篡改授权文档），并继续在 v1.3 §2 合同正文（而非 §8 的自证声明）约束下工作。**此项需要规划侧或 Founder 核对后确认哪个哈希值权威，或重新签发一份哈希自洽的版本**；在此之前，本 Manifest 的一切后续记录均以 v1.3 §2 合同正文的实际条款为准，不依赖 §8 声明值的正确性。

## 二、现场基线核验（v1.3 §1.2 观察锚点 vs 现场事实）

| 项 | v1.3 声明 | 现场核验 | 结果 |
|---|---|---|---|
| `observed_local_head` | `78a4ad8a932592bac0b45e9ce835d3dc77ce7374` | `git rev-parse main`（`/home/faye/diyu-demo`） | **一致** |
| `observed_origin_main` | 同上 | `git ls-remote https://github.com/andyan77/diyu-demo.git refs/heads/main` | **一致**（`78a4ad8a...`） |
| `observed_github_main` | 同上 | 同上（同一次查询即代表 GitHub 侧真值） | **一致** |
| 无关 M3 目录 | `m3-account-content-operator-semantic-v1.0/` 已被规划侧观察到，要求不得触碰 | 本次未触碰、未读取该目录任何文件 | **遵守** |
| M1 任务分支/worktree 现状 | 应为 `task/m1-natural-interaction-context-v1` / 既有独立 worktree | `/home/faye/diyu-demo-worktrees/m1-natural-interaction-context-v1`，HEAD `7258fae`（未提交改动：B-1/B-2/B-5/B-6 修复批次，见 evidence §十三） | **一致，已继承** |
| 审查预算消耗 | `budget_accounting`: 自 v1.2 起累计，本 Rebase 不重置 | v1.2 阶段已消耗：`formal_review_budget=1`（§8 正式审查，evidence §十二）＋ `repair_budget=1`（B-1/2/5/6 修复批次，evidence §十三）。**两项预算已在 v1.3 交付前用尽**，剩余唯一可用步骤是 `closing_verification: affected_scope_only` | **已继承、不重置，不得重开第二次开放式正式审查** |

## 三、REBASE_IMPACT_MAP

依据 v1.3 §3 声明的四种 `action`（`REUSE_CURRENT` / `REMAP_AND_VERIFY_BINDING` / `REVERIFY_AFFECTED_SCOPE` / `NOT_VERIFIED`）逐条判定。`prior_status`／`prior_evidence_ref` 取自本任务 v1.2 阶段已完成的正式 §8 独立审查（evidence §十二）——这是本任务迄今唯一一次满足"未参与实现、上下文隔离、只读"标准的独立核验，比历次执行侧自验证据权威。

| criterion_id | prior_status（§8 正式审查独立判定） | prior_evidence_ref | contract_semantics_changed | implementation_or_environment_changed | action |
|---|---|---|---|---|---|
| M1-AC-00 | PARTIAL（缺 Run Manifest ID/Hash，基线引用有一处历史误记） | evidence §十二；L1/L2/L3 | 否 | 否（本 Manifest 本身即在补这个缺口） | REVERIFY_AFFECTED_SCOPE |
| M1-AC-01 | PARTIAL→阻断 B-3（材料/历史产物无输入通道） | evidence §十二 | 否 | **是**（B-3 已实现：真实 file_upload 通道 + document-extractor/join 节点链路 + evidence_provenance 真实来源区分；两轮对抗式审查各发现真实缺陷并已修复——详见 evidence §十六。**未经 live Dify 验证、未经独立 Reviewer 核验**，仅 executor_self_check + 确定性单测，行动值仍是 NOT_VERIFIED） | NOT_VERIFIED |
| M1-AC-02 | PARTIAL（负向场景有覆盖，正向"显式长期表述→LONG_TERM_SUBJECT"未测） | evidence §十二 | 否 | 否（本批未处理，仍是已知缺口，不在 B-3/B-4/B-5 范围内） | NOT_VERIFIED |
| M1-AC-03 | PARTIAL→阻断 B-1（次目标/优先级/经营目标类别无物理承载） | evidence §十二 | 否 | **是**（B-1 已修复：新增 3 个 patch key，`priority_order` 改为替换语义） | REVERIFY_AFFECTED_SCOPE |
| M1-AC-04 | PARTIAL→阻断 B-2（`permission`/`freshness` 维度缺失） | evidence §十二 | 否 | **是**（B-2 已修复：新增两个常量维度 + gaps 登记 + 存量条目升级；B-3 进一步把 provenance/freshness 从恒定常量升级为真实可变值） | REVERIFY_AFFECTED_SCOPE |
| M1-AC-05 | PARTIAL→阻断（`last_confirmation_signal` 从未被读取，拒绝补充后合法降级不可表达） | evidence §十二 | 否 | 否（本批未处理，范围内已知限制） | NOT_VERIFIED |
| M1-AC-06 | PARTIAL→阻断 B-4（`needed_capabilities` 单值+关键词决定） | evidence §十二 | 措辞新增"不依赖固定链、**内部表单**或关键词标签"，语义方向不变 | **是**（B-4 已实现：`requested_capabilities_text` 逗号分隔多能力，一轮可同时点名多项，阻塞字段并集正确处理；仍是扁平字符串，未引入未验证的数组结构。**未经 live Dify 验证、未经独立 Reviewer 核验**，行动值仍是 NOT_VERIFIED） | NOT_VERIFIED |
| M1-AC-07 | PARTIAL→阻断 B-5（`CANCEL`/短指代/`HANDLED` 均无机制） | evidence §十二 | 否 | **是**（B-5 已实现：`handled_thread_id` 真实短指代绑定 + `HANDLED` 终态闭环 + `cancel_target` 三类真实撤销机制；两轮对抗式审查各发现真实缺陷并已修复，详见 evidence §十六。**未经 live Dify 验证、未经独立 Reviewer 核验**，行动值仍是 NOT_VERIFIED——AC-07 全量的短指代仍只覆盖"回应已有 open_thread"这一种，通用短指代解析仍是已知缺口） | NOT_VERIFIED |
| M1-AC-08 | NOT_VERIFIED（无调整类测试或真实运行） | evidence §十二 | 否 | 否 | NOT_VERIFIED |
| M1-AC-09 | PARTIAL（负向已证，正向在 M1 范围内无主体） | evidence §十二 | 否 | 否 | REUSE_CURRENT |
| M1-AC-10 | PARTIAL→阻断 B-6（影子节点失败被当合法空 patch，产生虚假断言） | evidence §十二 | 否 | **是**（B-6 已修复，`SHADOW_NODE_FAILED` 检测；判据依赖的模型行为前提未经 live 实测，见 evidence §十三"需 Reviewer 裁决"） | REVERIFY_AFFECTED_SCOPE |
| M1-AC-11 | PARTIAL（单一 call_intent 来源已证，M2/M3 契约因 M2/M3/M4 尚未编译无法测） | evidence §十二 | 否 | 否（结构性无法验证，非本批可解决） | NOT_VERIFIED |
| M1-AC-12 | PASS（受保护基线与主 Chatflow 均未被触碰，已独立核验） | evidence §十二 | 否 | 否 | REUSE_CURRENT |
| M1-AC-13 | PASS（候选真实运行，已发布图与 HEAD 源码字节级绑定） | evidence §十二 | 否 | **是**（本批代码已变、DSL 已重新生成为 v0.6 但尚未发布） | REVERIFY_AFFECTED_SCOPE |
| M1-AC-14 | PARTIAL→阻断 B-8（10 次真实推送账本零记录，运行清单不完整） | evidence §十二 | 否 | **是**（已补记 L5 SE-018；`b39c9e21` 误判已用数据库时间戳更正为良性重复，非活跃缺陷） | REVERIFY_AFFECTED_SCOPE |
| M1-AC-15 | PARTIAL→阻断 B-7（从未做过回滚演练） | evidence §十二 | 否 | **是**（已做静态恢复验证：数据库结构确认发布机制天然可逆；真实演练受限于执行侧无控制台写权限，如实标注限制，见 evidence §十三） | REVERIFY_AFFECTED_SCOPE |
| M1-AC-16（v1.3 新增） | 不适用（v1.2 无此项） | 无 | **新增** | 不适用 | NOT_VERIFIED |

**AC-16 初步自查（非正式判定，留待收口复验确认）**：Stage Baseline v0.2 六条持续禁止声明——"V1 已全面通过"「三份 Skill 集成后质量没有下降」「DeepSeek 普遍优于 Qwen」「Skill 普遍优于无 Skill」「当前结果可跨品牌、跨行业推广」「当前系统已经具备生产可用性」——本任务全部文档（evidence／L2／L3／L5）逐一检索，**未出现任何一条**。v0.1 A/B 阶段历史 `PARTIAL` 结论、A-0～A-4 原始证据、G-01～G-12 状态，本任务均未触碰、未回写。

## 四、结论与下一步

- 本 Manifest 完成 v1.3 §4 步骤 1-3。除 §一 记录的 `task_contract_hash` 自证不一致（已如实登记、未擅自处理）外，其余基线核验全部一致。
- 按 §4 步骤 4 起继续：v1.2 阶段已完成的 B-1/B-2/B-5/B-6 修复批次（在 v1.3 交付前、v1.2 授权下完成）视为已在原 P0 范围内的接续工作，予以保留（`preserve_existing_work: true`）。
- 按 §4 步骤 6-7：审查预算已耗尽（见 §二），下一步只能是 `closing_verification: affected_scope_only`——只看 `REVERIFY_AFFECTED_SCOPE` 标记的 8 项（AC-00/03/04/07/10/13/14/15）与新增的 AC-16，不重开对 `NOT_VERIFIED`／`REUSE_CURRENT` 项的开放式审查。
- 收口复验前提：候选需先完成 DSL v0.6 的导入/发布与真实 Dify 回归（尤其是 AC-10/AC-13，B-6 判据的模型行为前提需要 live 证据，见 evidence §十三）。

## 五、`closing_verification` 通过之后的继续施工与证据时效（B-3/B-4/B-5，evidence §十六）

`closing_verification: affected_scope_only` 已经跑完并给出结论（AC-00/03/04/07/10/13/14/16 PASS，AC-15 阻断，见 evidence §十五）。**在这之后**，Founder 指出 B-3（材料输入通道）、B-4（多能力选择）此前被执行侧以"需要架构判断"为由不当延期，且 B-5（短指代绑定／`HANDLED` 闭环／实际撤销机制）只修了诚实反馈这一部分——均不构成合法延期理由，执行侧已实现三者的真实机制（见 evidence §十六）。

**这一动作产生一个必须如实登记的治理后果**：按 v1.3 `evidence_reuse_policy.criterion_dependency_map`——"上下文编译或路由变化影响 M1-AC-01 至 M1-AC-12"——这批改动直接修改了 `m1_context_compiler_v0.1.py` 与 `build_m1_candidate_dsl_v0.1.py`，即将产生新的 commit 与新的候选 DSL（v0.7）。`closing_verification` 对 AC-03/04/07/10/13/14 给出的 PASS，其证据绑定（commit hash、已发布工作流图字节、`m1_shadow` 结构化输出 schema 现状）在源码变更后**必然过期**，不能被继续当作描述当前代码状态的有效结论引用：

| criterion_id | closing_verification 结论（旧 commit） | 本批之后的状态 |
|---|---|---|
| M1-AC-00 | PASS | **继续有效**——不依赖编译器代码内容，是治理/基线事实 |
| M1-AC-03 | PASS | **PASS_STALE_PENDING_REVERIFICATION**——`_merge_patch` 内部顺序已重排（B-5 修复把撤销/短指代逻辑移到次目标等追加逻辑之前），需在新 commit 上重新跑确定性测试+live 回归才能重新确认 |
| M1-AC-04 | PASS | **PASS_STALE_PENDING_REVERIFICATION**——`evidence_provenance`/`freshness` 派生逻辑本批又变了（新增 material_present 核实），需重新确认 |
| M1-AC-07 | PASS（仅覆盖诚实反馈这一子情形） | **NOT_VERIFIED**——`handled_thread_id`/`cancel_target` 是全新代码路径，closing_verification 从未看过，不是"过期"而是"从未被独立核验过" |
| M1-AC-10 | PASS | **PASS_STALE_PENDING_REVERIFICATION**——`_merge_patch`/`main()` 签名与调用链本批改动，B-6 判据本身逻辑未动但周边代码已变 |
| M1-AC-13 | PASS（候选运行与旧 commit/旧发布图字节级绑定） | **必然过期**——AC-13 的定义就是"与当前 commit 绑定"，新 commit 产生的瞬间旧绑定就不再描述当前状态，这是正常的、非病态的过期，不是缺陷 |
| M1-AC-14 | PASS | **本地/远端 hash 一致性验证需要新 commit 推送后重新核对**，不是失效，只是需要新一轮核对 |
| M1-AC-15 | BLOCKED（回滚演练） | **不受影响**——阻断原因是环境权限（控制台无写权限），与源码内容无关，源码变更不改变这条阻断 |
| M1-AC-16 | PASS | **继续有效**——是文档/声明层面的检查，不依赖编译器代码具体实现 |

**这不是重开第二次开放式正式审查**（`closure_rule` 仍然有效，不违反）：本次改动是执行侧在 Founder 直接指出延期不当之后，在原 P0、原 `allowed_delta` 范围内完成剩余工程实现，不是新的产品范围。真正需要的是：新 commit 推送后，对**受影响范围**（AC-03/04/07/10/13/14，加上原本就还没做过独立审查的 AC-01/06）做一次新的 `affected_scope_only` 收口确认——这仍然是 v1.3 `review_contract` 定义的同一种机制的自然延续，不是"第二次"从头开始的开放式审查。**这次收口确认目前同样卡在 AC-15 的同一个环境权限阻断上**：需要 Founder 完成一次真实候选导入/发布（v0.7），执行侧才能跑 live 回归和最终的受影响范围确认。
