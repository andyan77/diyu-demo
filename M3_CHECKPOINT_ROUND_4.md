# M3 工程执行 Checkpoint · 第 4 轮（EP-04 收尾 / EP-06b / EP-07 / EP-08 / EP-09 / EP-10）

> `task_id` = `DIYU-V1-M3-ACCOUNT-CONTENT-OPERATOR-001`
> `entry_mode` = `CONTINUE`（同一任务身份，合同哈希未变）
> `checkpoint_at` = 2026-08-26 EP-10 时点
> `terminal_state` = **不是终态**。本轮被**外部资源**阻断（DeepSeek 账户余额耗尽），以 Checkpoint 收尾。

```text
M3_ENGINEERING_TASK        = IN_PROGRESS
M3_TECHNICAL_CANDIDATE     = RUNNABLE_BUT_NOT_FULLY_VERIFIED
M3_MODULE_PROFESSIONAL_GAIN= NOT_VERIFIED（A/B 只跑完 6/12）
M3_DIFY_CANDIDATE_APP      = CREATED_AND_PUBLISHED (b7fb5b1a-9278-426c-bb8a-f9f288639548)
M3_FOUNDER_DIFY_ACCEPTANCE = AWAITING_FOUNDER
M5_INTEGRATION_GAIN        = NOT_EVALUATED_BY_M3
REAL_BUSINESS_LIFT         = NOT_VERIFIED
```

---

## 1. 一句话

本轮把 Dify 候选 App 建起来并跑通，把三份新判据（行为 49 例、纵向 12 步、四臂 A/B）**先冻结后运行**，共完成 82 次真实模型调用；**跑到一半 DeepSeek 账户余额耗尽**，14 例行为用例与 6 次 A/B 运行拿到 402。五名独立判定者的结论是：**保真两条链路各 7/7 通过，纵向 `FAIL(INSUFFICIENT)`，行为 29 成功/5 不足/1 失败/14 无结果**。独立收口 Reviewer 报了 2 条阻断项，**本轮全部闭合，且都是补证据关闭而不是降级措辞关闭**。

**没有把跑通的部分拿去凑结论。** A/B 一条也没判，因为它没跑完。

---

## 2. 本轮 commit

```text
4bcaaa0  冻结 ECC-M3-RUNTIME-BEHAVIOR-002 与 ECC-M3-LONGITUDINAL-001（先于运行）
7564896  冻结 ECC-M3-MODULE-AB-001（先于运行）
8673be2  Dify 画布链路保真证据、纵向 12 步、结构反搜与回滚演练
a715687  行为 49 例与 A/B 12 次的原始记录（含余额耗尽的失败记录）+ 冻结 Reviewer Rubric
b1a1d35  独立判定 ECC-M3-LONGITUDINAL-001 —— FAIL(INSUFFICIENT)
8d8a381  Founder 自然语言产品验收包 + 任务分区账本
（本 commit）行为判定、独立收口审查、两条阻断项的闭合、AC 状态矩阵更新、Checkpoint 4
```

**判据文件的哈希在其结果产出后一个字未改**——这是本轮最重要的一条自证，`git log -p` 可验。唯一的判据变更是 `M3_ECC_MODULE_AB_001_FROZEN_v1.0_ADDENDUM_001.md`，它是**收紧**、且发生在 A/B 判定**开跑之前**（判定一次都没做过），触发事件写在文件里。

---

## 3. 真实成本与外部阻断

```text
本轮真实调用   ≈ 82 次
本轮 token     ≈ 1,430,000（行为 818k + 纵向 234k + 保真-Dify 179k + A/B ≈ 184k）
阻断           GET /user/balance → {"is_available": false, "total_balance": "-1.06" CNY}
失败请求        402 Insufficient Balance
影响面          直连 API 与 Dify 链路用的是同一个 key，两边同时失败
```

按 Prompt §12.2「目标模型不可用时不得临时选择更容易通过的模型」：Dify 工作区内 `langgenius/tongyi/tongyi` 与 `langgenius/moonshot/moonshot` 两个 provider 都是 `active` 状态，**本轮一次都没用**。

---

## 4. 本轮新建的外部对象

| 对象 | 标识 | 状态 |
|---|---|---|
| Dify 候选 App（**唯一一个**） | `b7fb5b1a-9278-426c-bb8a-f9f288639548` | 已创建并发布，版本 `2026-08-26 17:06:34.276971`，workflow id `92784dcb-06ac-4274-96c6-ed9e4cba964d` |
| 图 | `start → llm → end`，3 节点 2 边 | 草稿 hash `689df355ec10d530f64d98ec798c8cbb37dd8e397588583e35264efce41fe29c` |
| 模型绑定 | `langgenius/deepseek/deepseek` / `deepseek-v4-flash` / `temperature=0.4` | 与合同 §12.2 一致 |
| Service API Key | 只存在于 scratch，**未进仓库**（已 grep 核验） | 有效 |

写入前的对象清单已保存（入场时 27 个 App，无同 task_id 对象）。**未复用、未修改、未发布任何其他 App**；未切换任何生产流量。

---

## 5. 我本人做的独立复核（不是转述判定者结论）

| 判定者结论 | 我复核了什么 | 结果 |
|---|---|---|
| Dify 链路 `G7-A` 自述附件未加载 | 直接读 `workflow_inputs.loaded_references`：2799 字符，sha256 与其余 7 组**完全相同** | 属实。这是同一失效模式的**第二次复现** |
| 纵向 `E04` 缺反证与到期 | 全文 687 字符，"四周/复验/到期/推翻/反证/停止/窗口"出现次数**全部为 0** | 属实 |
| 纵向 `E07` 冲突分支被打包带过 | 全文 1196 字符，"冲突/矛盾" 0 次，"人工/口头/陈晚" 0 次，L5/L6 只出现一次且是打包引用 | 属实 |
| 行为 `B02-1` 锚点未标暂定 | 全文 5280 字符，"锚点" 0 次、"复验" 0 次、"不确定" 0 次；两处"暂定"说的是**阶段**不是锚点 | 属实 |
| 行为 `B08-1` 探索提案缺反证 | "反证" 0 次、"复验" 0 次（"到期"有 2 次） | 属实 |
| 行为 `B06-1` 触发失败条款 | 输出逐字含"约 21 条/周"，输入 `expected_publish_count` 逐字是"每天 3 条（用户口径）" | 属实，见 §7 的判据措辞问题 |
| 收口 Reviewer B-1（Checkpoint 3 自证与事实不符） | `git log --date` 与 `git reflog show main --date` 交叉核对：Checkpoint 3 落盘 09:18:10，`main` 已于 09:08:51 前进 | 属实 |
| 五名判定者的隔离性 | 解析各自执行记录，只扫会造成文件访问的参数（不扫 Write/Edit 正文） | **全部 CLEAN、零违规** |

**凭据泄漏扫描**：DeepSeek key / Dify Console 口令 / App API Key 在全部提交内容中均为 `NO LEAK FOUND`。

---

## 6. 独立收口 Reviewer 的两条阻断项 —— 本轮闭合方式

### B-1（R-3 FAIL）· `M3_CHECKPOINT_ROUND_3.md` 有一句与事实不符的自证，且更正范围少算

**闭合方式**：追加 `evidence/ep10-closeout/BASELINE_DRIFT_IMPACT_v1.0_CORRECTION_001.md`。
**不回去改 Checkpoint 3 原文**（canonical §三：历史留痕只加不改）。更正内容：载体范围由"前两轮"改为**三轮全部**；点名 Round 3 §4 的"本轮未变"与 §8 的"复核"抬头为过时且写下时即为假；正确口径统一为对共同祖先 `df2c595` 比对。

**顺带在该更正里主动披露了一处超出冻结「允许变化面」的新增**：`collab-ledger/tasks/<task_id>.md`。理由、为什么不侵犯受保护资产、以及"Founder 认为不该写就删掉这一个文件"的处置口径，都写在里面。执行侧**不自行**把它算作"本来就允许"。

### B-2（R-7 NOT_CHECKED）· 判定者隔离性只有自述、从未核验

**闭合方式（选了补证据这条，不是降级措辞）**：`evidence/ep10-closeout/judge_isolation_verification.json`。
五名判定者逐一解析执行记录，**只扫会造成文件访问的参数**（`Read.file_path` / `Bash.command` / `Grep`/`Glob` 的 pattern 与 path），**不扫 `Write`/`Edit` 的正文**——判定者在自己文件里提到某个文件名是"提及"不是"读取"。结果：五名全部 `CLEAN`，零 forbidden 命中。

**B-2 的附带发现（更要紧的一条）**：Reviewer 实测证明 A/B 盲评包可被**平凡去盲**——`blind/<case>/{甲乙丙丁}.md` 与父目录 `<case>__{A,Aplus,B,Bprime}.json` 的 `answer_text` 逐段对应，读一层兄弟文件就能还原映射，`SALT` 在不在仓库都不影响。**A/B 判定一次都还没跑**，所以此刻修补成本为零。已发 `M3_ECC_MODULE_AB_001_FROZEN_v1.0_ADDENDUM_001.md`：判定者改为只拿仓库外的独立包；事后核验范围扩到整个 `ep08-module-ab/` 目录与 `SKILL.md`；核验结果必须落成仓库内产物而不是只写在 commit message 里。硬门、增益门、结果空间**一个字未动**。

### Reviewer 的第三条（非阻断但必须处置）· Founder 包把 AC-16 的画布半提到了 ✅

**属实，已更正。** 区分清楚了两件事：
- **Workflow 图链路**的语义保真——成立（新绑定、判据零改动、独立判定 7/7）；
- **§12.3 意义上的画布验收**——**没做**。本机无 playwright / chromium，而 §12.3 明写"Dify 交付真相是草稿图、实际配置和浏览器渲染画布，不是单次 API 运行历史"。草稿图与实际配置已逐项核验，浏览器渲染那一层没有。

更正落在 `M3_FOUNDER_ACCEPTANCE_PACKAGE_v1.0.md` §0/§13 与 `M3_ACCEPTANCE_CRITERIA_FROZEN_v1.0.md` 的 AC-16 卡。

---

## 7. 一条必须自曝的判据措辞问题（AC-06 的 `失败`）

我在 `ECC-M3-RUNTIME-BEHAVIOR-002` 里把失败条款写成「把'每天 3 条'**换算成其他时间单位**」。模型把"每天 3 条"折成"约 21 条/周"，判定者按字面判 `失败`，并**明确拒绝**替我把条款收窄——收窄属于看到结果后放宽判据，不允许。

但语义主稿（`SKILL.md` O-3）禁止的原本是「把'每天三条'换算成'**每周三条**'（用用户自己的时间单位）」——那是偷偷把目标缩小。模型做的 3×7=21 是**保幅度**的，而且是为了和"基线 3 条/周、实际 2 条"同单位比较，**冲突因此被放大而不是被掩盖**。

**我的判据措辞比语义主稿宽。** 处置：`失败` 本轮照记，不放宽；措辞问题登记为 **v1.1 修订事项，只对未来轮次生效**。这条自曝写在这里，是因为把它藏起来等于让一个我自己造的判据缺陷去污染对实现的判断。

---

## 8. AC 状态

见 `M3_ACCEPTANCE_CRITERIA_FROZEN_v1.0.md` §7.2 的完整矩阵。摘要：

```text
PASS               AC-05（结构+运行时）｜AC-12｜AC-13｜AC-16 的 Workflow 图半
FAIL               AC-06
FAIL(INSUFFICIENT) AC-02｜AC-03｜AC-08｜AC-09｜AC-17
NOT_VERIFIED       其余 12 条（含 AC-10/14/15 因余额耗尽零证据，AC-18 未跑完，
                   AC-20 未推远端、Founder 未验收）
```

**AC-12 本轮从 `STALE` 升到 `CURRENT`**：`main` 前进后，逐文件实测证明运行中的 M2 容器 `app/` 与 `migrations` 与 `main@a7b8101` **逐字节一致**且容器自取证以来未重启。这是上行，因此有事件支撑（在途改动被合入且内容未变），不是靠"应该没变"推断。

---

## 9. 受保护模块与回滚（用**正确口径**，对共同祖先比对）

```console
$ git diff --stat df2c595 HEAD -- content-production decision-chain business-persistence
（无输出）

$ git diff --stat df2c595 HEAD -- collab-ledger
 collab-ledger/tasks/DIYU-V1-M3-ACCOUNT-CONTENT-OPERATOR-001.md | 106 +++++++++++++
 （唯一一处：本任务自己的分区账本，未改动任何既有行；已在 CORRECTION_001 中主动披露）

$ git diff --name-status df2c595 HEAD | awk '{print $1}' | sort | uniq -c
     （全部为 A —— 新增，无修改无删除）
```

**回滚演练已完成，不是预检**：

- **Dify 侧**：导出 DSL → 故意损坏草稿（改节点标题、删一条边）→ 从备份恢复 → 恢复后图 sha256 与备份**逐字节一致**，Dify 内容 hash 回到 `689df355…`；**已发布版本全程未被演练触碰**（演练后复读，published graph sha256 与恢复后的草稿一致）。
- **Git 侧（非破坏式）**：从任务分支 tip 重建独立工作树 → 树对象与索引逐字节一致 → 删除演练工作树 → `main` 复查未受影响。

**M2 侧唯一不可由 Git 撤销的残留**仍是第 2 轮的取证 workspace（M2 无删除 workspace 端点，属 M2 新任务）。**本轮未新增 M2 workspace。**

---

## 10. 本轮明确没做的事

未 merge/rebase/cherry-pick `main` 进任务分支｜未直推 `main`｜未创建 PR｜未 force/amend/reset/squash｜未改写历史｜未修改任何非任务 Dify App、凭据、知识库或运行记录｜未切换任何生产流量｜未修改 M1/M2/M4/M5 或六份既有 Skill｜未改动任何既有账本文件的任何一行｜未使用 `dify-platform-expert` MCP｜未使用 Qwen/Moonshot｜**未推送远端**（被本机权限分类器拦截两次，未绕过）｜未修改 `SKILL.md`（它是四份 ECC 的共同锁定变量）。

---

## 11. 登记为新任务候选（不在本任务内处理）

1. **`missing[]` 自述不可靠**——附件已加载却自称未加载，两条链路各复现一次，两名不同判定者独立发现。已从"一次性观察"升级为"**可复现失效**"。
2. **必填项没有结构性强制**——同一份 Skill 在不同轮次里会跳过它自己规定的必填项（探索六项的反证与到期、暂定锚点的四要素、冲突反馈的依据），而跳过的恰好是它自检清单里点名"最容易被省掉"的那几项。这是**稳定性**问题，不是能力缺失。
3. **`ECC-M3-RUNTIME-BEHAVIOR-002` 的 AC-06 失败条款措辞需版本化修订到 v1.1**（见 §7）。
4. **Content Brief v0.1 的上游错位**——已接受的《八项能力合同》把"持续运营决策"定为 Brief 第一条合法上游，而现行 `Content_Brief_Architect_v0.1.md` 仍要求"已被接受的 Campaign 决策包"。改 Brief 属六份既有 Skill，本合同禁止。
5. **M2 读侧缺口**（第 2 轮登记）：发布前评审记录写得进、读不出。

---

## 12. 下一个可立即执行的动作

| # | 动作 | 对象 | 输入/基线 | 什么信号算做完 |
|---|---|---|---|---|
| 1 | **Founder 为 DeepSeek 充值** | DeepSeek 账户 | 当前 `-1.06 CNY` | `GET /user/balance` → `is_available: true` |
| 2 | 补跑行为 ECC 的 14 例 | `ECC-M3-RUNTIME-BEHAVIOR-002` | `_cases.json`（`1da81ea6…`）中 `failed` 列出的 14 例，绑定不变 | 49 例全 `succeeded` + 独立判定 |
| 3 | **整轮重跑** A/B 十二次 | `ECC-M3-MODULE-AB-001` + `ADDENDUM_001` | `_arms_and_holdouts.json`（`961e74f6…`），四臂哈希不变 | 12 次全 `200` + 三名判定者盲评 + 隔离核验落成仓库内产物 |
| 4 | 推送任务分支并复读远端完整 hash | `origin/task/m3-account-content-operator-v1` | 本地 HEAD | `git ls-remote` 与本地 HEAD 一致 |
| 5 | 合并时补写五本账的一行定位 | `L1`/`L2`/`L3`/`L5` 的**当时当前版本** | `collab-ledger/tasks/<task_id>.md` | 四本账各有一行指向分区文件 |

**需要 Founder 决定、执行侧不得自行推进**：

1. `missing[]` 缺陷与"必填项无结构强制"修不修（修 `SKILL.md` ⇒ 四份 ECC 全部作废重跑）；
2. 要不要新开任务修 Content Brief Architect 的上游错位；
3. Qwen 跳不跳——**技术阻碍已经不存在**（Dify 工作区 `tongyi` provider 是 `active`），现在跳过它的唯一原因是 Founder 的明确指示。按契约原文跳过它 `AC-19` 到不了完整 `PASS`；
4. 远端推送权限；
5. `collab-ledger/tasks/<task_id>.md` 这处超出冻结允许变化面的新增，认不认。

---

## 13. 恢复入口

1. 读本文件 + `M3_ACCEPTANCE_CRITERIA_FROZEN_v1.0.md` §7.2 + `collab-ledger/tasks/DIYU-V1-M3-ACCOUNT-CONTENT-OPERATOR-001.md`；
2. 核验四份 ECC 冻结件与其证据的时序（`git log --format='%h %ad %s'`），确认判据 commit 早于结果 commit；
3. 跑 `python3 -m unittest discover -s account-operations/tests -t account-operations/tests` 确认 **83 条**仍全通过；
4. 核验 `main` 当前 HEAD——**不要**假设它还是 `a7b8101`；若又前进，按 `evidence/ep10-closeout/BASELINE_DRIFT_IMPACT_v1.0.md` 的方法重做定向影响面核算，**不要整批置 STALE**；
5. 核验 Dify App `b7fb5b1a-…` 的草稿 hash 仍是 `689df355…`；若不是，说明有人动过图，全部 Runtime 证据置 `STALE`。

**不另开根任务，不重建 `task_id`，不把等待写成 `DONE`，不把外部资源阻断写成 `FAILED`。**

```text
END_MARKER
= DIYU-V1-M3-ACCOUNT-CONTENT-OPERATOR-001-CHECKPOINT-ROUND-4-END
```
