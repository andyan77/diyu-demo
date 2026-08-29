# 统一 Founder Canvas · 任务分支收口记录 v1.0

`task_id: DIYU-V1-UNIFIED-DIFY-APPLICATION-001`
依据：Founder 2026-08-29 指令「登记为技术债，继续收口，完成项目 DIFY 集成全部模块的单一应用交付」

**收口范围＝任务分支收口，不含 `main` 收口。** 原因见第一节：
合同把 `main` 合并的授权条件写死在「AC-01..12 之后」，该条件当前不成立。
**本文件不落终态，也不代 Founder 判 `ACCEPT`。**

---

## 一、终态：**不落终态**（`task_progress = IN_PROGRESS`）

合同 `DIYU_V1_UNIFIED_DIFY_APPLICATION_TASK_CONTRACT_v1.0.yaml`
（sha256 `279f80ba…`，现场复算通过）有两条硬约束：

```yaml
allowed_final_states: [INVALID, DONE, BLOCKED, FAILED]
completion_and_stop:
  task_progress_until_formula: "IN_PROGRESS"
  done_formula: "UAPP-AC-01..12 全部 PASS/CURRENT AND Founder ACCEPT AND 无适用 P0 FAIL
                 AND Git/远端/Dify/DSL/回执一致"
  no_terminal_state_before_formula: true
```

因此：

- **不是 `DONE`**：done 公式不成立。AC-03 / AC-06 / AC-07 为 `FAIL`，
  AC-08 / AC-09 从未运行，AC-12 未实测，Founder 未给出 `ACCEPT`。
- **不能写 `PARTIAL`**：`PARTIAL` **不在本合同允许的终态集内**。
  （M5 落的是 `DONE`，依据是它自己合同经 Founder 裁决 003 改写后的验收口径；
  本任务的合同没有发生过这种改写，不能照搬。）
- **不写 `BLOCKED`**：本任务没有走死。两项未决事项都在 Founder 的裁决域内，
  一句裁定即可推进，不构成阻断。
- **按合同不落任何终态**：`task_progress = IN_PROGRESS`，`terminal_state` 留空。

**Founder 授权收口 ≠ 验收全部通过，也不等于 done 公式成立。**
这份记录不把任何一项未验证项提升为通过，也不代 Founder 落终态。

### 关于 main 合并：合同的条件没有满足，本轮不做

```yaml
authorized_actions_after_activation.git:
  normal_commit_and_push_task_branch: "AUTHORIZED"
  main_merge_and_push: "CONDITIONALLY_AUTHORIZED_AFTER_UAPP_AC_01_TO_12"
```

`main` 合并的授权条件写得很死：**在 AC-01..12 之后**。当前六项成立、三项 `FAIL`、
两项从未运行、AC-12 未实测——**条件不成立**。

执行侧在条件未成立时合并 `main`，等于自行把合同状态往上推一级，
这正是项目 `CLAUDE.md` §6 与协议 v1.3 明令禁止的。**所以本轮做到任务分支为止**：
提交与推送任务分支是无条件授权的，已完成；`main` 与 `origin/main` 一个字节未动。

**解除这道门只有两条合规路径，都在 Founder 手上**：
① 把 AC-01..12 补齐；② Founder 明确豁免该条件或对合同做 `REBASE` 出新版本。
**执行侧不得代选。**

## 二、交付了什么：一个应用，全部模块在内

`app_id = 2448e4f9-818f-4b88-9311-d18546e97da9`，`mode = advanced-chat`，已发布，
65 节点 / 77 边。**用户只对着一个对话框说自然语言**，start 节点零用户输入变量（D-11）。

| 模块 | 在图里的形态 | 事实依据 |
|---|---|---|
| M1 任务上下文编译 | 5 个节点**逐字节复用**原 M1 子图，节点 id 未改，内部引用全部保持有效 | D-03：图内编译器源码与仓库源码逐字节一致 |
| 六项能力（Matrix / Campaign / Content Brief / Creative Script / Production Director / Publishing & Packaging） | 经 `uapp_seam` 一个工具节点按路由参数进入，**不复制六份专业语义到画布** | 六例定向复验全部 PASS；D-09 能力枚举来自路由输出 |
| M3 单账号持续运营 | `uapp_m3` 工具节点 | D-04：图内方法参考与仓库文件逐字节一致 |
| 跳转适配 | `uapp_hop` 工具节点 | D-07：三个工具节点用的正是三个任务 provider |
| M2 业务持久化 | 15 个 HTTP 节点：5 个引导 + 3 个读取 + 7 个写回（素材／产物／版本／发布／反馈／周期／撤回） | D-14 请求体 `is_test`＋`is_simulated` 均为真；D-23 无注定 422 的请求 |
| 用户投射与防泄漏 | `uapp_delivery` 代码节点 | D-12 正负双向可区分 |

**没有第二个应用、没有外部编排运行时**（D-13：图内零外部编排引用）。
**没有新建第二业务数据库、第二长期运行时、外部工作流引擎或 Agent swarm。**

**旧资产零漂移**：旧 Canvas、旧 provider、最终 FP 八应用与 hop 适配器全部未被改动（D-08）。

### 同一张图的两个哈希口径

| 口径 | 值 |
|---|---|
| 构建脚本 `json.dumps(sort_keys=True)`（Manifest / 文档用） | `c95ffbe4b8a80c4a7c38ba3a7b229a58831d4f7b402a1e3b2e82af5ae44e09bd` |
| 数据库原文 `psql -tA` 字节（运行器 / 裁定器用） | `2349143f8ce8c4af87ebd0feeefab95da8babc49658dbd24e4be9242e238472d` |

两者是**同一张图**，已复算确认，65 节点 / 77 边一致。见 TD-UAPP-10。

---

## 三、本轮做了什么

### 3.1 定向复验：六项能力（偿还 TD-UAPP-07）

六个 `CAP` 结论原本绑定在图 `e8819f5b…` 上，此后图被改动四次，按 A3 一律 `STALE`。
本轮在当前图上重跑六例，**同一输入在同一张图上仍然只跑一次**——这是 A3 的失效后复验，
不是 Founder 叫停的那种「重复采样求 PASS」。

| 用例 | 预期能力 | 结果 | 节点数 |
|---|---|---|---|
| UAPP-CAP-01 | MATRIX | `PASS` | 39 |
| UAPP-CAP-02 | CAMPAIGN | `PASS` | 39 |
| UAPP-CAP-03 | CONTENT_BRIEF | `PASS` | 39 |
| UAPP-CAP-04 | CREATIVE_SCRIPT | `PASS` | 39 |
| UAPP-CAP-05 | PRODUCTION_DIRECTOR | `PASS` | 39 |
| UAPP-CAP-06 | PUBLISHING_PACKAGING | `PASS` | 39 |

判据为「路由到点名的那一个能力、接缝实际执行、其余五个未被调用」，
判在 Dify 节点执行记录上，不认模型自述。旧证据一字未动，新证据另存 `_attemptc95ffbe4`。

**AC-04 / AC-05 由 `NOT_VERIFIED (STALE)` 恢复为 `PASS / CURRENT`。**

### 3.2 修掉一个真实的检查器缺陷（TD-UAPP-09）

裁定器只比对判据哈希，**从不比对证据绑定的图**。判据不变而图改动时，
它会把绑在旧图上的证据报成 `CURRENT`。之前那六个 `STALE` 是我人工认定的，机器当时并不会拦。

修复后做了双向控制：
- **负向控制**：八份旧证据全部由「可读成 `CURRENT`」变为 `NOT_VERIFIED / STALE`，
  并各自指出所绑旧图（`f36e788d…` / `e509b550…` / 空）。
- **正向控制**：当前图上的六份新证据读成 `CURRENT` 且判 `PASS`。

检查器能区分正例与负例，不是只会说 PASS。

### 3.3 确定性面

D-01..D-24 在当前图上 **24 PASS / 0 FAIL**，零模型调用。

### 3.4 DSL 导出

`unified-app/dsl/UAPP_UNIFIED_FOUNDER_CANVAS_v1.0.yml`，
sha256 `57f035c46477fcb75a539d79f72341e43bce1d28bb0e2ccec8d8f34aae7bae0e`。
回读校验：65 节点 / 77 边与线上一致，11 个会话变量齐全，M1 子图逐字在内。
按 `include_secret=false` 导出，并做了凭据扫描——**零命中**，可安全入库。

---

## 四、没做到的，逐条列明

| 项 | 状态 | 为什么 |
|---|---|---|
| AC-03 完整主故事 | `FAIL` | TD-UAPP-01：同一冻结输入的首轮交付不稳定，处置须 Founder 裁定 |
| AC-06 缺口精确停 | `FAIL` | TD-UAPP-03：根因在逐字复用的 M1 对话节点，**本任务一个字都没改过它**，属产品语义域 |
| AC-07 撤回与副作用真实性 | `FAIL`（最后实测）／修复已部署**未复验** | TD-UAPP-04：撤回轮不再进 M3 的修复已上线，但没做过端到端复验。**部署 ≠ 验证** |
| AC-08 等价表达 | `NOT_VERIFIED (ABSENT)` | 四例从未运行 |
| AC-09 多轮与幂等 | `NOT_VERIFIED (ABSENT)` | RECOVERY-01 从未运行，且它必须接在一次**成功的** FULL-01 之后才有意义，依赖 TD-UAPP-01 先有结论 |
| AC-12 Founder 实测 | `NOT_VERIFIED` | Founder 选择在已披露债务下收口，**未在新应用里实际运行过**。执行侧不代判 |
| TD-M5-01..08 | 未偿还 | 本任务从未声称偿还，M5 的 `DONE` 未被改动 |

**`STALE` 不洗失败**：GAP-01 与 WITHDRAW-01 的归档证据现被机器标为 `STALE`（绑旧图），
但那两次失败确实发生过，AC-06 / AC-07 仍按最后一次实测记 `FAIL`。详见技术债主表 v1.1。

---

## 五、边界遵守情况

本任务全程未做以下任何一项（合同 §4.2 禁止项）：

- 未修改、删除、改名旧 Founder Canvas 或旧 provider
- 未修改 final FP M3、final FP Seam 或六能力应用的 graph / model / prompt / Skill
- 未重做 M1-M5，未修改 M5 的 `DONE`，未声称偿还 TD-M5-01..08
- 未把六份专业语义复制进画布，未固定串行调用全部模块
- 未新建第二业务数据库、第二长期运行时、外部工作流引擎或 Agent swarm
- 未做真实平台发布；写入全部显式 `is_test=true / is_simulated=true`
- 凭据未落盘、未打印、未提交（DSL 按 `include_secret=false` 导出并已扫描）
- 未 force push、未删除远端分支、未覆盖历史 evidence / Attempt / FAIL
- 未用「App 存在」「workflow succeeded」「DSL 导出」或模型自述冒充验收通过

---

## 六、真源索引

| 内容 | 位置 |
|---|---|
| 技术债主表（当前） | `docs/UAPP_TECHNICAL_DEBT_REGISTER_v1.1.md` |
| 技术债主表（历史，保留不改） | `docs/UAPP_TECHNICAL_DEBT_REGISTER_v1.0.md` |
| Founder 试用裁定包 | `docs/UAPP_FOUNDER_TRIAL_PACKAGE_v1.0.md` |
| 冻结判据（全程未改） | `docs/UAPP_FROZEN_SCENARIOS_v1.0.json` sha256 `c45c4668…` |
| 冻结 Manifest | `docs/UAPP_CANDIDATE_RUN_MANIFEST_v1.5.yaml` sha256 `7d6b2efd…` |
| 正式运行证据（当前图） | `evidence/formal/UAPP-CAP-0N_attemptc95ffbe4.json` |
| 正式运行证据（历史各代，按 Manifest 版本归档） | `evidence/formal_v1.0_stale/` … `formal_v1.3_stale/` |
| 裁定结果 | `evidence/UAPP_ADJUDICATION.json` |
| 确定性判据结果 | `evidence/UAPP_DETERMINISTIC_CHECKS.json` |
| DSL | `dsl/UAPP_UNIFIED_FOUNDER_CANVAS_v1.0.yml` |
| 证据索引（逐文件哈希） | `docs/UAPP_EVIDENCE_INDEX_v1.1.json` |

---

## 七、下一步（不在本任务内）

按依赖顺序，不是按工作量：

1. **TD-UAPP-03 与 TD-UAPP-01 需 Founder 裁定**，两者都落在产品语义／判据设计域，执行侧不得自行处置。
2. TD-UAPP-01 有结论后，AC-03 与 AC-09 才谈得上偿还（AC-09 依赖一次成功的 FULL-01）。
3. TD-UAPP-02 与 TD-UAPP-04 的修复需要一次端到端复验才能从「已部署」升到「已验证」。
4. AC-08 的四例只需运行，无前置依赖。

以上任一项都需要新的授权与新的判据版本。

**本任务在此停在 Checkpoint，不落终态。** 续跑点：
- **做什么**：按 Founder 对 TD-UAPP-03 / TD-UAPP-01 的裁定，补齐或重定 AC-03 / AC-06 / AC-07 / AC-08 / AC-09
- **对哪个对象**：`app_id = 2448e4f9-818f-4b88-9311-d18546e97da9`，当前图 `c95ffbe4…`
- **输入或基线**：分支 `codex/v1-unified-dify-application-001` 本次提交；冻结判据 `c45c4668…`；Manifest v1.5 `7d6b2efd…`
- **什么信号算做完**：AC-01..12 全部 `PASS/CURRENT` 且 Founder `ACCEPT`，
  此时 `main_merge_and_push` 的条件才成立，done 公式才成立

---

## 更正说明（2026-08-29 意图路由轮追加，正文以上一字未改）

Founder 于本文件写成后给出裁定
`FOUNDER_ADJUDICATION_UAPP_INTENT_ROUTING_001` = **`RETURN`**。
本文件多处**已被超越**，当前真相以后继文件为准：

| 本文件内容 | 已变成 | 当前真源 |
|---|---|---|
| 图 `c95ffbe4…`，65 节点 / 77 边 | 图 `40e45858…`，**69 节点 / 81 边** | `UAPP_CANDIDATE_RUN_MANIFEST_v1.8.yaml` |
| 确定性面 24 条 | **32 条** | `evidence/UAPP_DETERMINISTIC_CHECKS.json` |
| `AC-02` / `AC-05` 记为 `PASS / CURRENT` | **Founder 裁定下调为 `FAIL`** | 技术债主表 v1.2 第一节 |
| `AC-12` 记为 `NOT_VERIFIED` | **`RETURN`**（Founder 已实测并退回） | 同上 |
| `AC-04` 记为 `PASS / CURRENT` | **`NOT_VERIFIED (STALE)`**（本轮改图后重新失效） | 同上 |
| 技术债 10 条 | **16 条** | `UAPP_TECHNICAL_DEBT_REGISTER_v1.2.md` |
| DSL sha256 `57f035c4…` | `a63d6675a6c8c965d0dac0109e921746e84b37acb076f4243174cf5a15a2218b` | `dsl/UAPP_UNIFIED_FOUNDER_CANVAS_v1.0.yml` |

**没有变化的**（本节不推翻这几条）：

- **`main` 与 `origin/main` 仍停在 `01a42b0`，一个字节未动。** 合并条件依旧不成立，
  且 Founder 裁定明确重申「`main` 合并继续禁止」。
- **仍不落终态**：`task_progress = IN_PROGRESS`，`terminal_state` 留空。
- **`AC-12` 仍未被代判。**
- 第五节「边界遵守情况」逐条仍然成立；本轮另加一条：
  **M1 编译器、M2、最终 M3、Seam、六能力应用一个字未改**（D-03/04/06/07/08）。

**本文件第二节「交付了什么」的模块清单仍然准确**，只是节点数从 65 增到 69——
新增的四个节点全部是本轮桥接层自己的（`uapp_ask_gate`／`uapp_ask_one`／
`uapp_ask_answer`／`uapp_chat_guard`），没有引入第二应用或第二运行时。
