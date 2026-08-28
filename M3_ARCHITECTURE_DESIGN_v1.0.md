# M3 架构侦察与最小实现设计 v1.0（EP-02 产物）

> `task_id` = `DIYU-V1-M3-ACCOUNT-CONTENT-OPERATOR-001`
> `document_role` = 工程 HOW 记录。产品语义不在本文件改变；本文件只决定"用什么最小物理形态承载已冻结的 WHAT"。
> `baseline_head` = `main @ df2c5952551f386a0e9a509404357f23c1d223c9`，分支 `task/m3-account-content-operator-v1`
> `written_at_utc` = `2026-08-26`

---

## 1. 现场侦察结论（本轮实测）

| 侦察项 | 实测结果 | 证据等级 |
|---|---|---|
| 既有物理 Skill 形态 | `content-production/skills/{writing-creative-scripts,directing-content-production,packaging-content-for-release}/` 三份，均为 `SKILL.md`（388/416/555 行）+ `references/{platforms,industry-conditions,examples}.md`；YAML frontmatter 只有 `name` + `description`；正文中文，含"判据／为什么／❌✅ 示例／输出块／自检／参考文件"固定骨架 | `static_verified` |
| 决策链 Skill 形态 | `decision-chain/skills/*.md` 为扁平带版本号文件（`Matrix_Architect_v0.1.2.md` 等），无 `references/` 子目录 | `static_verified` |
| 条件加载惯例 | 三份 Skill 均在正文写明"什么条件下读哪份 reference"，并写明"参考文件拿不到时：跳过、照常产出、写进 `missing[]`，不得凭记忆补" | `static_verified` |
| M2 实际接口 | FastAPI（`business-persistence/app/`），按 `workspace_id` 强制作用域，`X-Actor-Ref` 鉴权。M3 相关读端点：`GET /accounts/{id}/cycles/current`、`GET /accounts/{id}/cycles`、`GET /accounts/{id}/campaign-overrides/active`、`GET /accounts/{id}/cycles/decisions/latest`、`GET /market-observations`（带 `is_expired` 计算）、`GET /playbooks/{name}/current`、`GET /publish-instances/{id}/feedback`、`GET /tasks/{id}/projection` | `static_verified` |
| M2 实际写端点（M3 候选的落点） | `POST /cycles`、`POST /accounts/{id}/cycles/decisions`（`adjusted` / `kept_unchanged`）、`POST /playbooks`、`POST /campaign-overrides`、`POST /campaign-overrides/{id}/end` | `static_verified` |
| M2 边界测试 | `tests/test_interface_contracts.py::test_m3_boundary_m2_stores_playbook_and_cycle_values_verbatim_without_judging_them` 已钉死"M2 原样存储、不评判"——M3 是唯一做专业判断的一侧 | `static_verified` |
| Dify 编排形态 | `business-persistence/dify/m2_candidate.yaml`：`http-request` 节点直连 `http://diyu-m2-app:8000/...`，`code` 节点 `code_language: python3`，签名 `def main(...) -> dict`，只用标准库（`import json`） | `static_verified` |
| 仓库当前不存在的东西 | 没有独立"应用后端"服务；没有 M3 相关分支/worktree/目录；宿主 python 3.10.12 无 pytest、无 pydantic，`jsonschema` 为 3.2.0（仅 Draft7） | `static_verified` |

### 1.1 A3 影响面登记：M2 有在途未合并变更

`/home/faye/diyu-demo-worktrees/m2-business-persistence-version-feedback-v1` 上存在**未提交**的工作树改动：`app/api/knowledge.py`、`app/models/knowledge.py`、`tests/test_market_observation.py`、`tests/test_interface_contracts.py`，以及未跟踪的迁移 `17368b750d3b_market_observation_permission_semantics.py`。

- 本任务的 M2 绑定是 `main @ df2c595` 的 `business-persistence/`，**不是** M2 worktree 的在途状态；
- 该在途变更主题为"市场观察的权限语义"，一旦合入 main，**M3 投影中 `market_observations` 相关字段即置 `STALE`**，须定向复验 AC-09／AC-12，其余投影字段不受影响（不多算失效）；
- 本轮不读取、不依赖、不修改 M2 worktree 的在途内容。

---

## 2. 物理位置决策

### 2.1 结论

```text
account-operations/                     ← 新增顶层模块目录（M3 唯一落点）
  skills/
    operating-one-account/
      SKILL.md                          ← 唯一 M3 Skill
      references/
        fashion-and-market.md           ← 条件加载
        six-skill-methods.md            ← 条件加载
  interfaces/
    M2_TO_M3_PROJECTION_v1.0.schema.json
    M3_TO_M2_WRITEBACK_CANDIDATE_v1.0.schema.json
    M3_CONTENT_TASK_v1.0.schema.json
    projection.py                       ← 纯标准库；可直接贴进 Dify code 节点
  fixtures/
    M3_ACCEPTANCE_FIXTURES_v1.0.md      ← 夹具规格（运行时不加载）
  tests/
    test_projection_contract.py         ← stdlib unittest
  docs/                                 ← 预留：EP-05 起的证据索引
```

治理文档（`M3_ACCEPTANCE_CRITERIA_FROZEN_v1.0.md`、本文件、`M3_CHECKPOINT_ROUND_1.md`）留在仓库根，与已提交的 `M3_ENGINEERING_EXECUTION_PROMPT_v1.1.md` / `..._CONTRACT_v1.2.yaml` / `..._MANIFEST_v1.0.md` 同级，不打散同一类文档。

### 2.2 为什么不是别的位置（消融式论证）

| 候选位置 | 拿掉本方案换成它，会变什么 | 判定 |
|---|---|---|
| `decision-chain/skills/` | CLAUDE.md §6 冻结资产零改动明确列出 `decision-chain` 的 `skills／fixtures／references／evidence／workflows`。往里加目录会把 M3 的新增物混进冻结区，**回滚粒度与冻结边界同时失效** | 否决 |
| `content-production/skills/` | 该目录是生产链（写脚本/导演/包装）。M3 是决策能力不是生产能力；且会共享该模块已冻结的 `references/`，**责任接缝在文件系统层就被抹平**（AC-15 的反搜会因此失去意义） | 否决 |
| 仓库根平铺 `SKILL.md` | 与三份既有 Skill 的形态不一致；M3 的 interfaces／fixtures／tests 无处安放，只能继续污染根目录 | 否决 |
| 新顶层 `account-operations/` | 与 M2 的 `business-persistence/`、生产链的 `content-production/` 是同一条组织原则（一个模块一个顶层目录，内含 skills/docs/fixtures/tests）。回滚 = 删一个目录 | **采用** |

**消融检验**：删掉"独立顶层目录"这个决定，改放进任一既有模块 → 冻结资产边界被跨越、回滚粒度变粗、AC-15 责任反搜失去物理依据。结果改变，所以这个决定成立。

### 2.3 命名

规划侧工作名 `account-content-operator` → 项目内目录与 Skill `name` 采用 `operating-one-account`。

理由：三份既有 Skill 一律是"动名词 + 对象"（`writing-creative-scripts` / `directing-content-production` / `packaging-content-for-release`），`operating-one-account` 与之同形，也直接说出这份 Skill 干什么。`ENGINEERING_HANDOFF.md` §4 明确"Skill 源文件在项目内的具体路径和命名版本"属执行侧 HOW。

**可追溯性**：本文件与 SKILL.md 顶部均登记 `planning_source = m3-account-content-operator-semantic-v1.0/skill-source/SKILL.md (ccedd9a8…)`，规划名不丢失。

---

## 3. Skill 形态决策：一份 SKILL.md + 两份条件附件

### 3.1 四份规划 reference 的逐份消融

| 规划 reference | 加载条件 | 处置 | 消融依据 |
|---|---|---|---|
| `operations.md` | 诊断／周期规划／日常决策／复盘 —— 即**每次运行都要** | **合并进 SKILL.md** | 一份"每次都全量加载"的附件，与把 SKILL.md 拆成两个文件没有区别。删掉这个拆分，运行结果不变 ⇒ 按 A5 该拆分不成立。合并后正文变长，但省掉一次必然发生的加载跳转，且 `ENGINEERING_HANDOFF.md` §6.2"不得每次全量加载"本来就禁止这种附件 |
| `fashion-and-market.md` | 只在商品／库存／试穿／季节／门店／外部市场证据会改变决定时 | **保留为 `references/`** | 删掉它 → 服装局部失效（AC-07）与市场机会分层（AC-09）判断丢失；不加载它运行通用请求 → 结果不变。两个方向都成立 ⇒ 条件附件成立 |
| `six-skill-methods.md` | 只在形成下游内容任务、判断合法等价输入、或核对商业目标是否抹掉适用专业义务时 | **保留为 `references/`** | 纯诊断轮、纯复盘轮、`NO_CONTENT_TASK` 轮不需要它；产出内容任务的轮次删掉它 → AC-14／AC-15 的下游义务保留判断丢失 |
| `acceptance-fixtures.md` | **运行时永不加载**（规划稿原文："never load it in ordinary operation"） | **移出 references/，落到 `fixtures/`** | 放在 `references/` 里唯一的效果是"有概率在运行时被加载"，而那正是它禁止的事。落到 `fixtures/` 后，`ENGINEERING_HANDOFF.md` §6.4"不把夹具答案写进 Runtime"在文件系统层就成立 |

**结果**：Skill 树 = 1 份 SKILL.md + 2 份条件附件。不是四份 Skill，不是四个节点，也没有为对称保留第四份附件。

### 3.2 语言载体

正文中文，frontmatter `description` 英文（含中文触发词），与三份既有 Skill 完全同形；亦满足 CLAUDE.md §5"核心规则必须能用 Founder 可审计的大白话说明"。

**这是载体适配，不是语义改写。** `ENGINEERING_HANDOFF.md` §2 明确 `skill-source/SKILL.md`"可做载体适配，不可静默改语义"。为使"没有静默改语义"可被检查，SKILL.md 末尾附**语义回指表**：`ENGINEERING_HANDOFF.md` §5 列出的 16 项不可改 WHAT，逐项指向 SKILL.md 中承载它的小节。EP-05 的反搜会用这张表做回指检查（动作 1）。

---

## 4. M2 集成方式决策

### 4.1 结论：**投影载荷 + 候选信封**，M3 侧零网络、零数据库、零写权限

```text
读路径
  Dify http-request 节点 ── 调 M2 现有按 workspace 作用域的读端点
        ↓ 原始响应
  Dify code 节点（python3，标准库）── 运行 interfaces/projection.py::build_projection()
        ↓ 当轮最小投影 JSON（受 M2_TO_M3_PROJECTION_v1.0.schema.json 约束）
  LLM 节点（DeepSeek V4 Flash）── 加载 operating-one-account/SKILL.md [+ 条件附件]
        ↓ 结构化运营判断 + 内容任务 / NO_CONTENT_TASK
写路径
  Dify code 节点 ── 解析并校验为 M3_TO_M2_WRITEBACK_CANDIDATE_v1.0 信封
        ↓ candidate_status = "proposed"，永远只是候选
  Dify http-request 节点 ── POST 到 M2 现有端点（/cycles、/cycles/decisions、/playbooks、/campaign-overrides）
        ↓
  是否接受、哪个版本是当前有效版本 ── 由 M2 + 用户裁决，M3 不参与
```

### 4.2 为什么是它（否决路线与理由）

| 候选路线 | 否决理由 |
|---|---|
| M3 直连 PostgreSQL 读表 | 共享合同四 §一明确"Dify 不得自行读取整个租户数据库""Dify 不得获得数据库管理权限"，且"Skill 以统一任务快照为主要运行载荷，不依赖数据库物理结构"。直连即违约 |
| M3 Skill 正文内写 HTTP 调用与端点 | 会把网络 I/O、端点地址与鉴权头塞进一份提示词资产；Skill 变得依赖 M2 部署拓扑，M2 一改端点全部 Skill 失效（A3 影响面被人为放大）。且 Skill 无法被单元测试 |
| 新建一个"M3 应用后端"服务 | 合同非目标明确禁止建通用数据库平台/新平台；仓库当前没有应用后端，M3 也没有被授权建。属范围蔓延 |
| 文件投影（把 JSON 落盘再喂给 Dify） | 在 Dify 里没有可靠的共享文件系统入口；且引入一层与真实运行不同的"演示专用"路径，EP-06 保真会因此失去意义 |
| **投影载荷 + 候选信封（采用）** | 复用 M2 已有端点，M2 零改动；投影编译是一个**纯标准库函数**，同一份代码既能贴进 Dify code 节点（形态与 `m2_candidate.yaml` 已有的 `def main(...) -> dict` 一致）又能在仓库里被 unittest 覆盖；M3 侧不持有凭据、不写当前版本 |

**消融检验**：拿掉投影层，让 LLM 直接吃 M2 原始响应 → 会把整个账号历史与非当轮字段一并投给模型（违反 AC-12"最小必要"），且缺失/拒绝/暂定/过期/不适用五类状态会被 JSON 里的 `null` 坍缩成同一个值（AC-12 明确 `FAIL` 条件）。结果改变，投影层成立。

### 4.3 五类"空"不得坍缩（AC-12 的核心机制）

投影里每个可缺字段一律用**显式状态对象**而不是 `null`：

```json
{ "value": null, "availability": "REFUSED", "source": "user", "as_of": "2026-08-26T00:00:00Z" }
```

`availability ∈ { PRESENT, UNKNOWN, NOT_PROVIDED, NOT_APPLICABLE, REFUSED, EXPIRED }` —— 六个取值两两不等，直接对应共享合同一 §三"可用性状态"维度（已具备／未知／未提供／不适用／拒绝提供／已失效）。这不是新造枚举，是把已冻结的产品语义落成一个可测的载体。

### 4.4 三条接缝的实现分工

| 接缝 | 载体 | 本轮状态 |
|---|---|---|
| M2 → M3 最小投影 | `M2_TO_M3_PROJECTION_v1.0.schema.json` + `projection.py::build_projection()` + unittest | EP-04 已实现，`static_verified`（用依据 M2 模型/API 源码手工构造的样本，**不是**真实 M2 实例响应） |
| M3 → M2 候选写回 | `M3_TO_M2_WRITEBACK_CANDIDATE_v1.0.schema.json` + `validate_writeback_candidate()` | EP-04 已实现 schema 与校验，**尚未接 Dify、尚未 POST 到真实 M2** = `NOT_VERIFIED` |
| M3 → Content Brief 内容任务 | `M3_CONTENT_TASK_v1.0.schema.json` | EP-04 已实现 schema；**下游真实消费未测** = `NOT_VERIFIED`（另见 §7 缺口 B） |

---

## 5. Dify 拓扑设计（本轮只设计，不创建）

**本轮不创建任何 Dify 对象**（需真实平台 access，属 EP-04 后半与 EP-06）。以下是设计意图，等级 `inferred`。

一个 task-id 专用候选 App，一条 Workflow：

```text
start → [条件] 读节点组（cycles/current、campaign-overrides/active、
                      cycles/decisions/latest、market-observations、feedback）
      → code: build_projection            （1 个节点）
      → LLM: M3 Skill + 条件附件          （1 个节点）
      → code: parse + validate 输出        （1 个节点）
      → [条件] code+http: 候选写回          （按需）
      → end
```

**为什么不是四个节点／四个 Workflow**：四类业务行为（`ACCOUNT_STATE_DIAGNOSIS` / `CYCLE_PLANNING` / `DAILY_CONTENT_DECISION` / `REVIEW_UPDATE`）是**说明性标签**，一次调用可组合多个。做成四条路径后，"顺便把这周排一下 + 看看现在怎么样"这类组合请求要么走两遍要么被迫二选一——行为变差而不是变好。因此单条 Workflow，行为由 Skill 内部判断，标签不进 Runtime 枚举（AC-05 的直接依据）。

每个节点必须过消融：删掉读节点组 → M3 只能靠对话记忆（AC-17 `FAIL`）；删掉 `build_projection` → 见 §4.2；删掉 validate 节点 → 结构化输出无法被下游稳定消费（AC-13/14）；删掉写回节点 → M3 判断无法进入下一周期（AC-11/17）。四个都成立。

---

## 6. 依赖图与变更文件清单

### 6.1 依赖图

```text
规划侧唯一语义主稿 (732963af…)
  └── ENGINEERING_HANDOFF (b6bf5911…) ── 约束 ──┐
  └── skill-source/SKILL.md (ccedd9a8…)         │
  └── references/{operations, fashion-and-market, six-skill-methods, acceptance-fixtures}
            │                                    │
            ▼                                    ▼
  account-operations/skills/operating-one-account/SKILL.md + references/
            │
            ├── 消费 ◄── account-operations/interfaces/M2_TO_M3_PROJECTION_v1.0.schema.json
            │                └── 由 projection.py 从 M2 读端点编译
            │                        └── 依赖 business-persistence@main:df2c595 的 API 形状
            ├── 产出 ──► M3_CONTENT_TASK_v1.0.schema.json ──► Content Brief（缺口 B）
            └── 产出 ──► M3_TO_M2_WRITEBACK_CANDIDATE_v1.0.schema.json ──► M2 写端点

M3_ACCEPTANCE_CRITERIA_FROZEN_v1.0.md ── 判据 ──► 以上全部
```

**失效传播规则**：`business-persistence` 的 M3 相关端点/字段任一变化 ⇒ `projection.py` + 投影 schema + AC-12/13 置 `STALE`；语义主稿或 HANDOFF 变化 ⇒ SKILL.md + references + AC-01～15 置 `STALE`；Prompt/Contract 哈希变化 ⇒ **全部**置 `STALE` 并请求 Rebase。Skill 正文变化**不**使投影 schema 失效（无依赖边，不多算）。

### 6.2 本轮变更文件清单

**新增**（全部在本任务分支）：

```text
M3_ACCEPTANCE_CRITERIA_FROZEN_v1.0.md          （EP-01，已提交 f5a9aca）
M3_ARCHITECTURE_DESIGN_v1.0.md                 （本文件）
M3_CHECKPOINT_ROUND_1.md                       （本轮收尾）
account-operations/skills/operating-one-account/SKILL.md
account-operations/skills/operating-one-account/references/fashion-and-market.md
account-operations/skills/operating-one-account/references/six-skill-methods.md
account-operations/interfaces/M2_TO_M3_PROJECTION_v1.0.schema.json
account-operations/interfaces/M3_TO_M2_WRITEBACK_CANDIDATE_v1.0.schema.json
account-operations/interfaces/M3_CONTENT_TASK_v1.0.schema.json
account-operations/interfaces/projection.py
account-operations/interfaces/README.md
account-operations/fixtures/M3_ACCEPTANCE_FIXTURES_v1.0.md
account-operations/tests/test_projection_contract.py
```

**修改**：无。
**删除或重命名**：无。
**受保护资产改动**：无（`decision-chain/`、`content-production/`、`business-persistence/`、`collab-ledger/` 本轮零改动，见 §8 校验）。

---

## 7. 风险与回滚

| 风险 | 影响 | 处置 |
|---|---|---|
| **缺口 B**：现行 `Content_Brief_Architect_v0.1.md` 仍要求"已被接受的 Campaign 决策包"，与已接受共享合同二"持续运营决策是 Brief 第一合法上游"冲突 | AC-14 的下游消费半可能 `FAIL(ABSENT)` | 改 Brief 属六份既有 Skill，本合同禁止。M3 侧只保证内容任务携带 Brief 所需业务实质并标注 `upstream_kind`；EP-05 如实取证；若确认拒绝，作为**新任务候选**上报 Founder |
| M2 在途"市场观察权限语义"变更合入 main | `market_observations` 投影字段 `STALE` | 已在 §1.1 登记为定向复验触发；只失效 AC-09/AC-12 相关项，不整体失效 |
| 宿主无 pytest／pydantic，`jsonschema` 仅 3.2.0（Draft7） | 无法用 2020-12 校验器跑测试 | schema 文件按仓库既有惯例标 `$schema: draft/2020-12`，但**只使用 draft-7 与 2020-12 语义完全一致的关键字**；测试用 `Draft7Validator`，并加一条守卫测试断言 schema 中不出现 2020-12 专有关键字（`$defs`/`prefixItems`/`unevaluated*`/`dependentSchemas`），使降级校验保持可靠 |
| DeepSeek V4 Flash 不可得 | AC-16/18 无法取证 | 保持 `NOT_VERIFIED`，不临时换更容易通过的模型；需 Founder 授权并 Rebase 才可换 |
| 真实浏览器/画布核验能力不可得 | Dify 画布类验收 | 记 `BLOCKED` 或 `NOT_VERIFIED`，不用 API 日志冒充画布证据 |

### 回滚计划

1. **代码/文档**：本轮全部产出集中在一个新目录 `account-operations/` + 三份根级 `M3_*` 文档。回滚 = `git revert` 本分支相应 commit，或直接删除该目录；**不触碰 main，不 merge，不 force**。
2. **M2**：零改动，无需回滚。
3. **Dify**：本轮未创建任何对象，无回滚对象。EP-04 后半创建候选 App 前，须先保存当前对象清单、版本、图导出与回滚输入（Prompt §12.3）。
4. **回滚验证**：删除 `account-operations/` 后，仓库应回到 `f5a9aca` 的行为——`business-persistence` 测试、`content-production`、`decision-chain` 全部不受影响（无入边）。

---

## 8. 边界自检（本轮实测）

| 检查 | 结果 |
|---|---|
| 是否修改生产 Dify 对象 | 否——本轮未接触任何 Dify |
| 是否修改 M1/M2/M4/M5 或六份既有 Skill | 否 |
| 是否 merge/push main、建 PR、force、amend、reset | 否 |
| 是否有真实社交平台动作 | 否 |
| 是否重开外部多模型研究 | 否 |
| 是否新建第二套状态真源 | 否——M3 无自有持久化 |
| 是否触碰 `collab-ledger/` | 否 |
| 是否覆盖进入前未知/未跟踪文件 | 否——只新增 |

---

```text
END_MARKER
= DIYU-V1-M3-ARCHITECTURE-DESIGN-v1.0-END
```
