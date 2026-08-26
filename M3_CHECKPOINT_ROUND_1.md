# M3 工程执行 Checkpoint · 第 1 轮

> `task_id` = `DIYU-V1-M3-ACCOUNT-CONTENT-OPERATOR-001`
> `entry_mode` = `NEW_TASK`（本轮延续，未重建任务身份）
> `checkpoint_at_utc` = `2026-08-26T11:44:06Z`
> `terminal_state` = **不是终态**。本轮以 Checkpoint 收尾，不是 `DONE`。

```text
M3_ENGINEERING_EXECUTION   = IN_PROGRESS
M3_TECHNICAL_CANDIDATE     = IN_PROGRESS
M3_MODULE_PROFESSIONAL_GAIN= NOT_VERIFIED
M3_FOUNDER_DIFY_ACCEPTANCE = NOT_REACHED
M5_INTEGRATION_GAIN        = NOT_EVALUATED_BY_M3
REAL_BUSINESS_LIFT         = NOT_VERIFIED
M3-AC-00 ～ M3-AC-20       = 全部 NOT_VERIFIED（本轮无任何一条被判 PASS）
```

---

## 1. 合同引用

| 项 | 值 |
|---|---|
| Prompt | `M3_ENGINEERING_EXECUTION_PROMPT_v1.1.md` · `9d3388e8…` |
| Contract | `M3_ENGINEERING_TASK_CONTRACT_v1.2.yaml` · `1d4163fc…` |
| 语义主稿 | `M3_ACCOUNT_CONTENT_OPERATOR_SEMANTIC_COMPILATION_v1.0.md` · `732963af…` |
| 入场 Manifest | `M3_ENGINEERING_TASK_MANIFEST_v1.0.md` |
| 冻结验收判据 | `M3_ACCEPTANCE_CRITERIA_FROZEN_v1.0.md`（本轮 EP-01 产出） |
| 分支 / worktree | `task/m3-account-content-operator-v1` / `/home/faye/diyu-demo-worktrees/m3-account-content-operator-v1` |
| 基线 | `main @ df2c5952551f386a0e9a509404357f23c1d223c9` |
| 本轮 HEAD | `e5f945dd2a89cd8ee0e6ea3bab29dd05a3a277d1`（**仅本地，未推送远端**） |

规划侧唯一入口（`aa5997c3…`）不在本仓库路径下，本轮 `NOT_CHECKED`。全部本地哈希已实测比对，与 Prompt §1.2/§1.3 与 Manifest 声明一致。

---

## 2. 本轮 commit

```text
f5a9aca  EP-01 冻结 M3-AC-00~20 验收判据与充分性反查
69f598c  EP-02 架构侦察与最小实现设计
c327f98  EP-03 实现单账号持续运营 Skill 与两份条件附件
e5f945d  EP-04（起）落地三条接缝的 Schema 与投影编译器
```

相对入场 commit：**12 个文件全部为新增，0 修改、0 删除、0 重命名**。`decision-chain/`、`content-production/`、`business-persistence/`、`collab-ledger/`、`tools/`、`CLAUDE.md`、`笛语项目基线.md` 零改动（`git diff --name-only` 实测为空）。

---

## 3. 产物与哈希

| 文件 | SHA-256 | 阶段 |
|---|---|---|
| `M3_ACCEPTANCE_CRITERIA_FROZEN_v1.0.md` | `2d6d2f58…` | EP-01 |
| `M3_ARCHITECTURE_DESIGN_v1.0.md` | `f4ea3090…` | EP-02 |
| `account-operations/skills/operating-one-account/SKILL.md` | `1716260d…` | EP-03 |
| `…/references/fashion-and-market.md` | `cee04bea…` | EP-03 |
| `…/references/six-skill-methods.md` | `e3798308…` | EP-03 |
| `account-operations/interfaces/M2_TO_M3_PROJECTION_v1.0.schema.json` | `f200c5ea…` | EP-04 |
| `…/M3_TO_M2_WRITEBACK_CANDIDATE_v1.0.schema.json` | `b7e89225…` | EP-04 |
| `…/M3_CONTENT_TASK_v1.0.schema.json` | `b98e8d75…` | EP-04 |
| `…/projection.py` | `b0423f82…` | EP-04 |
| `account-operations/fixtures/M3_ACCEPTANCE_FIXTURES_v1.0.md` | `cba0da88…` | EP-03 |
| `account-operations/tests/test_projection_contract.py` | `0dbd3497…` | EP-04 |

---

## 4. 实际做了什么

### EP-01 · 验收判据冻结与充分性反查 —— 完成

21 张 ECC 卡（M3-AC-00～20），字段固定为**命题｜冻结输入｜候选｜锁定变量｜Oracle｜成功｜不足｜无结果｜失败｜反证探针｜取证阶段｜本轮状态**。另冻结：28 条夹具身份（含 3 条留出）、A/B 五项非补偿硬门与七维盲评 Rubric、ECC 通用协议（判据先于结果、候选预冻结、Holdout 退出规则、四级证据用词、动态证据时效、模型自评无效）。

反查结论：**全绿 = WHY 被解决，成立**。WHY 的每个组成都有至少一条**可失败**的判据覆盖，且三类"全绿但没解决问题"的漏洞被单独堵住（只有文档没运行→AC-16/17；能跑但没价值→AC-01 消融门 + AC-18 盲评门；有价值但越界→AC-13/15 反搜）。

### EP-02 · 架构侦察与最小设计 —— 完成

侦察实测了既有 Skill 形态、M2 全部读写端点、M2 的 M3 边界契约测试、Dify 的 `http-request` + `python3 code` 节点形态、宿主 Python 环境。

三个决定，都做了消融论证：

1. **新增顶层 `account-operations/`**——`decision-chain/` 与 `content-production/` 是 CLAUDE.md §6 明列的冻结资产区，往里加会同时破坏冻结边界和回滚粒度；
2. **1 份 SKILL.md + 2 份条件附件**——`operations.md` 每次都全量加载，等于把 SKILL.md 拆成两个文件（拆分可消融，已合并）；`acceptance-fixtures.md` 运行时永不加载，留在 `references/` 唯一的效果就是有概率被误加载（已移到 `fixtures/`）；
3. **投影载荷 + 候选信封**——否决了直连数据库（违反共享合同四）、Skill 内写 HTTP（把网络 I/O 和端点塞进提示词资产）、新建应用后端（范围蔓延）、文件投影（制造演示专用路径，让 EP-06 保真失去意义）。

### EP-03 · Skill 实现 —— 完成

`account-operations/skills/operating-one-account/SKILL.md`（468 行）：判断主链 O-1～O-11 与语义主稿 §5 的九步一一对应，另加 CTA 三层权限、共同质量底线、Brief 交接字段块与停止边界、M2 候选边界、输出与自检。文末〈语义回指表〉把 `ENGINEERING_HANDOFF.md` §5 的 **16 项不可改 WHAT** 逐项指向承载它的小节，供 EP-05 做回指检查（宪法动作 1）。

两份条件附件按加载条件写明触发条件与"拿不到时怎么办"（跳过、照常产出、写进 `missing[]`，不凭记忆补）。

载体适配为中文正文 + 英文 frontmatter，与三份既有 Skill 完全同形。**夹具答案未写进 Runtime**：SKILL.md 里的示例刻意避开了 `FX-M3-*` 夹具场景。

### EP-04（起）· 三条接缝 —— 部分完成

**已实现且有实跑证据**：

- 六种"没有值"（已具备/未知/未提供/不适用/拒绝提供/已失效）用显式状态信封承载，两两不等。五个正交维度按共享合同一 §三落成载体，不新增语义；
- 候选信封**在语法层表达不出"已接受"**：`candidate_status` 只有 `proposed`；整树键名反搜拒绝 `is_current`/`accepted`/`promote`/`overwrite`/`feedback_override`/`source_override` 等 17 个键；`suggested_m2_endpoint` 枚举内**没有任何**反馈或市场观察写端点；
- 内容任务 schema：`primary_job` 单值、`downstream_freedom` 非空、`additionalProperties:false` 挡住 `hook`/`script`/`shot_list`/`title`/`cover_copy` 夹带；
- `projection.py` 纯标准库，与 `m2_candidate.yaml` 现有 code 节点同形，可直接贴进 Dify。

**测试**：30 条 stdlib unittest 全通过（`python3 -m unittest discover -s account-operations/tests -t account-operations/tests`），含 `FX-M3-ABL-02` 字段消融（删任一必填顶层字段必须校验失败）。

**另做了 3 次变异验证**，证明这些测试真的会失败而不是形同虚设：

| 变异 | 结果 |
|---|---|
| 让 `_resolve` 把一切缺失塌成 UNKNOWN | 2 条测试失败 ✓ |
| 把过期市场观察直接丢弃 | 1 失败 + 1 错误 ✓ |
| 让 `none_recorded` 变成 PRESENT | 1 条测试失败 ✓ |

---

## 5. 已验证 / 未验证 / 打桩

| 项 | 状态 | 说明 |
|---|---|---|
| 全部绑定哈希比对 | `static_verified` | 本机 `sha256sum` 实测，与 Prompt/Manifest 声明一致 |
| 投影 schema + 编译器 + 跨字段不变量 | `static_verified` | 30 条 unittest 实跑通过 + 3 次变异验证 |
| 字段消融（AC-12 的 ③） | `static_verified` | 机械遍历必填字段，逐个删除逐个断言失败 |
| 候选信封禁区反搜（AC-13 的 ①②） | `static_verified` | 键名反搜 + 枚举限制，实跑通过 |
| 内容任务结构（AC-14 的 schema 半） | `static_verified` | 实跑通过 |
| 样本来源 | `static_verified`，**不是** `runtime_verified` | 样本依据 M2 源码手工构造，**未从运行中的 M2 实例抓取真实响应** |
| M3→M2 真实 POST | `NOT_VERIFIED` | 未接 Dify、未打真实 M2 |
| M3→Content Brief 下游真实消费 | `NOT_VERIFIED` | **见 §7 缺口 B** |
| Dify 对象、Workflow、图 | **未创建** | 本轮明确不创建；拓扑只是设计，等级 `inferred` |
| DeepSeek / Qwen 真实调用 | **未发生** | 本轮零模型调用，未伪造任何 API 结果 |
| Skill 的运行时行为（AC-01～11、15、16） | `NOT_VERIFIED` | Skill 文件存在**不构成**任何行为判据 |
| 远端推送 | 未发生 | 本轮不推远端 |
| `collab-ledger/` | 未触碰 | 按指令由另一条线处理 |

**没有任何一条 M3-AC 在本轮被判为 `PASS`。** 正式取证从 EP-05 开始。

---

## 6. 下一个可立即执行的动作

按 Prompt 自身的 EP 序列：

```text
EP-04 后半 —— 需要真实 Dify 平台 access
  1. 保存当前 Dify 对象清单、版本、截图/DOM、图导出与回滚输入（Prompt §12.3 前置）
  2. 创建带 task_id 标识的唯一 M3 候选/测试 App
  3. 把 projection.py 贴进 code 节点，接上 M2 读端点与写端点
  4. 核验 provider、准确 model id、参数，并绑定 commit
```

**在此之前不需要 Dify 也能做的一件事**（若本轮预算不足，这是最高性价比的下一步）：用运行中的 M2 实例抓取真实响应样本，把投影测试从 `static_verified` 升到贴近真实的契约测试。M2 的测试打 `http://diyu-m2-app:8000`，需要它的 Docker 环境起来。

EP-06（Runtime 保真）、EP-07（纵向）、EP-08（A/B）、EP-09（Qwen + 独立 Reviewer）**都需要先有一个能跑的候选**，本轮未触。

---

## 7. 阻塞项与判断取舍

### 缺口 B（真实合同冲突，需要 Founder 知情）—— 未解决

已接受的[共享合同二](decision-chain/docs/V1_M0_SHARED_CONTRACT_EIGHT_CAPABILITIES_v0.1.md)冻结了「持续运营决策」是 Content Brief 的**第一条合法上游**；但仓库现行 `decision-chain/skills/Content_Brief_Architect_v0.1.md` §1／§3.2 仍把"已被接受的 Campaign 决策包"写成**必需输入**，缺失时输出 `INPUT_INSUFFICIENT`。

- 这是**已接受合同与现行 Skill 正文之间的错位**，不是 M3 的实现缺陷；
- 改 Content Brief Architect 属六份既有 Skill，本合同 `never_authorized_by_this_contract` 明确禁止；
- 本轮处置：M3 侧义务收窄为"内容任务携带 Brief §1 要求识别的全部业务实质 + 显式标注 `upstream_kind = continuous_operation_decision`"，并**明确不为迎合旧正文伪造 Campaign 决策包**；
- **AC-14 的下游消费半保持 `NOT_VERIFIED`**。EP-05 如实取证；若确认 Brief v0.1 拒绝，作为**新任务候选**上报，不在本任务内改 Brief。

### M2 能力缺口（已登记，不需要修 M2）

`cycles` 表把三类产能存成可空数字，**没有字段能区分"用户拒绝提供"与"我们不知道"**。处置：该区分由任务快照侧经 `declared_absences` 带进投影；没带进来时降级为 `UNKNOWN`，**绝不猜成 `REFUSED`**。若判定必须落库，属 M2 新任务。

### A3 影响面（已登记）

M2 的任务分支上有**未提交**的"市场观察权限语义"改动（`app/api/knowledge.py`、`app/models/knowledge.py`、迁移 `17368b750d3b`）。本任务绑定的是 `main @ df2c595`，不依赖在途内容。它合入 main 后，**只**使 `market_observations` 相关投影字段与 AC-09/AC-12 置 `STALE`，其余不受影响——不多算失效，也不少算。

### 判断取舍（HOW，未上推）

| 取舍 | 选了什么 | 为什么 |
|---|---|---|
| Skill 落点 | 新顶层 `account-operations/` | 既有两个模块目录都是冻结资产区；新目录让回滚 = 删一个目录 |
| 附件数量 | 4 → 2 | `operations.md` 每次全量加载（拆分可消融，已并入正文）；`acceptance-fixtures.md` 运行时永不加载（已移到 `fixtures/`） |
| 命名 | `operating-one-account` | 与三份既有 Skill 的"动名词+对象"同形；规划名在文档与 SKILL 头部登记，不丢失 |
| 正文语言 | 中文 | 与三份既有 Skill 及 CLAUDE.md §5 一致；用〈语义回指表〉让"没有静默改语义"可被机械检查 |
| M2 集成 | 投影载荷 + 候选信封 | M2 零改动；同一份纯标准库代码既可 unittest 又可进 Dify code 节点 |
| 测试栈 | stdlib unittest + `jsonschema` 3.2.0 Draft7 | 宿主无 pytest/pydantic；M2 的测试要 Docker + live HTTP。加了守卫测试禁止 2020-12 专有关键字，使降级校验保持可靠 |
| 四类行为的物理形态 | **不做**四节点/四 Workflow/四 Skill | 组合请求（"看看现在怎么样，顺便把这周排一下"）在四条路径下要么跑两遍要么被迫二选一——行为变差 |

### 本轮明确没做的事

未创建任何 Dify 对象｜未调用任何模型 API｜未推送远端｜未 merge/PR/force/amend/reset｜未修改 M1/M2/M4/M5 或六份既有 Skill｜未触碰 `collab-ledger/`｜未做任何真实平台动作｜未重开外部多模型研究｜未建第二套状态真源｜未覆盖任何进入前未跟踪的文件。

---

## 8. 恢复入口

换会话重入时，从这里接：

1. 读本文件 + `M3_ACCEPTANCE_CRITERIA_FROZEN_v1.0.md`（判据已冻结，**不得在看到结果后修改**）+ `M3_ARCHITECTURE_DESIGN_v1.0.md`；
2. 核验 §3 的产物哈希是否仍然一致；不一致即按 §7 的失效传播规则定向置 `STALE`；
3. 跑 `python3 -m unittest discover -s account-operations/tests -t account-operations/tests` 确认 30 条仍通过；
4. 按 §6 继续 EP-04 后半。

**不另开根任务，不重建 `task_id`，不把等待写成 `DONE`。**

---

```text
END_MARKER
= DIYU-V1-M3-ACCOUNT-CONTENT-OPERATOR-001-CHECKPOINT-ROUND-1-END
```
