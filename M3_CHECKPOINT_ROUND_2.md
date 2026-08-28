# M3 工程执行 Checkpoint · 第 2 轮

> `task_id` = `DIYU-V1-M3-ACCOUNT-CONTENT-OPERATOR-001`
> `entry_mode` = `CONTINUE`（同一任务身份，合同哈希未变）
> `checkpoint_at_utc` = `2026-08-26T12:20Z`
> `terminal_state` = **不是终态**。本轮以 Checkpoint 收尾，不是 `DONE`。

```text
M3_ENGINEERING_EXECUTION   = IN_PROGRESS
M3_TECHNICAL_CANDIDATE     = IN_PROGRESS
M3_MODULE_PROFESSIONAL_GAIN= NOT_VERIFIED
M3_DIFY_CANDIDATE_APP      = NOT_VERIFIED (no console access)
M3_FOUNDER_DIFY_ACCEPTANCE = NOT_REACHED
M5_INTEGRATION_GAIN        = NOT_EVALUATED_BY_M3
REAL_BUSINESS_LIFT         = NOT_VERIFIED
M3-AC-00 ～ M3-AC-20       = 全部 NOT_VERIFIED（本轮仍无任何一条被判 PASS，理由见 §5）
```

---

## 1. 一句话

本轮把投影契约从**手工构造样本**换成了**运行中 M2 实例的真实响应**，真实数据当场
抓出 3 个手工样本永远抓不到的实现缺陷；并按判据原文重跑了全字段消融门，发现第 1 轮
的覆盖只是判据的一个真子集（11/141），补齐后从 53 条未挣到存在收敛到 6 条自由载荷。

**没有任何一条 M3-AC 达到 PASS。** 本轮把若干条从"未实现"推到"结构证据齐备、
只差运行时"，这是进度，不是通过。

---

## 2. 本轮 commit

```text
0f2240f  EP-04 用真实 M2 响应封住投影契约
f6d953c  EP-05 确定性、结构与负向验证
（本文件与 M3_ROLLBACK_PLAN_v1.0.md 随第 3 个 commit 落地）
```

入场 HEAD `ffac903` → 本轮 HEAD。相对 `main` 仍是 **31 个文件全部新增，0 修改**。

---

## 3. 产物哈希

| 文件 | SHA-256 | 本轮 |
|---|---|---|
| `M3_ACCEPTANCE_CRITERIA_FROZEN_v1.0.md` | `2d6d2f58…` | **未动**（判据冻结） |
| `M3_ARCHITECTURE_DESIGN_v1.0.md` | `f4ea3090…` | 未动 |
| `interfaces/M2_TO_M3_PROJECTION_v1.0.schema.json` | `1ce0440a…` | 改（`f200c5ea…`→） |
| `interfaces/M3_CONTENT_TASK_v1.0.schema.json` | `e45cc94e…` | 改（`b98e8d75…`→） |
| `interfaces/M3_TO_M2_WRITEBACK_CANDIDATE_v1.0.schema.json` | `b7e89225…` | 未动 |
| `interfaces/projection.py` | `1cb811f1…` | 改（`b0423f82…`→） |
| `tools/capture_m2_live_fixtures.py` | `fc1478d4…` | 新增 |
| `fixtures/m2_live_capture_v1.json` | `47a3ecfc…` | 新增 |
| `tests/test_projection_contract.py` | `282d4a18…` | 改 |
| `tests/test_live_m2_contract.py` | `c0e895fb…` | 新增 |
| `tests/test_field_ablation.py` | `2f2ad44d…` | 新增 |
| `tests/test_downstream_brief_consumption.py` | `5b08355f…` | 新增 |
| `tests/test_responsibility_reverse_search.py` | `6c607bbd…` | 新增 |
| `decision-chain/skills/Content_Brief_Architect_v0.1.md` | `a0268a21…` | **只读绑定，未改** |

判据文件哈希未变是**本轮最重要的一条自证**：看到结果之后没有回去改判据（A2）。

---

## 4. 从 static 升到 runtime 的证据（附命令）

### 4.1 取证方式

```console
$ docker exec -i diyu-m2-app python3 - < account-operations/tools/capture_m2_live_fixtures.py \
    > account-operations/fixtures/m2_live_capture_v1.json
```

真实建立：2 用户、1 workspace、2 账号、2 周期、1 Campaign overlay、3 市场观察、
1 task/artifact/version/publish、2 反馈、1 周期决策，并抓回 9 个读端点的原样响应
与 4 条真实拒绝响应（422×2、403、401）。

### 4.2 基线分歧（A3 影响面，不多算不少算）

运行中的 `diyu-m2-app:dev` **不等于**绑定基线 `main@df2c595`。逐文件实测：

```console
$ # 容器内 app/**.py 与 git show df2c595:business-persistence/<f> 逐一 diff
MODIFIED  app/api/knowledge.py
MODIFIED  app/models/knowledge.py
（其余全部逐字节相同）
```

正是第 1 轮预判的那条在途改动。据此**定向**划分证据等级：

| 证据族 | 等级 | 依据 |
|---|---|---|
| 周期 / 三类产能 / Campaign overlay / 周期决策 / 反馈 / 成员权限 | `runtime_verified @ main:df2c595` | 所打代码路径与基线逐字节相同 |
| 市场观察（含新增权限维度） | `runtime_verified @ diyu-m2-app:dev(在途)`；对绑定基线 **`STALE`** | 打的是未提交改动 |

不使不受影响的项失效，也不遗漏已知依赖。M2 那两个文件合入 `main` 后，**只**需定向
复验 AC-09 与 AC-12 的市场观察半。

### 4.3 真实数据抓出的 3 个缺陷（手工样本抓不到）

| # | 缺陷 | 为什么手工样本抓不到 |
|---|---|---|
| 1 | **过量读取**：`current_cycle`/`latest_cycle_decision` 把 M2 整行塞进 `value`，`row_version`（并发控制）与 `idempotency_key`（去重）一起投给模型 | 手工样本里根本没有这两个键 |
| 2 | **产能双真源**：整行还重复携带三类产能。把 `capacity.actual_capacity` 标成"用户拒绝提供"后，模型仍能从原始行读到那个数字——**防坍缩机制当场失效** | 同上 |
| 3 | **权限维度丢失**：M2 判定 `currently_usable=false / permission_unknown` 的观察，投影却标成 `PRESENT` 交给下游 | 手工样本没有权限字段 |

均已修复：周期/决策改为最小摘要 + schema `additionalProperties:false`；新增
`usage_permission` 与 `usable_for_inference`（单向不等式，永远 ≤ M2 自己的判断，
M2 未表达权限概念时行为逐字节不变，有专门的退化测试）。

另外，取证脚本自身的一次事故也已回归化：第一版无状态码断言，一条被 M2 以 422 拒绝的
`register_feedback` 把错误体当成记录写进了夹具。**静默失败伪装成证据**是取证脚本最
危险的失效模式，因为它不报错。

### 4.4 新登记的 M2 读侧缺口（不在本任务内修）

发布前评审记录挂 `content_version_id`、`publish_instance_id` 为 null；而 M2 唯一的
反馈读端点按 `publish_instance_id` 过滤 —— **该类证据写得进、读不出**。
后果如实承载：投影的 `feedback[]` 经 M2 读端点永远不含发布前评审，该类证据只能由
任务快照侧带入。属 M2 新任务候选。

---

## 5. AC 判定：为什么本轮仍然一条都不 PASS

逐条对冻结 ECC 卡核对，**不迁就**：

| AC | 本轮新增证据 | 判定 | 卡上还差什么 |
|---|---|---|---|
| **AC-12** | ①五类状态两两不等（真实 `null`）②`additionalProperties:false` ③**全字段消融门通过** | `NOT_VERIFIED` | 卡上冻结输入含「M2 实际响应样本」已满足；但市场观察半绑定在**在途构建**上，对 `main@df2c595` 为 `STALE`。**整条不判 PASS**：一半证据不在绑定基线上 |
| **AC-13** | ①无写调用/凭据 ②`candidate_status` 只能 `proposed` ③无自有持久化 | `NOT_VERIFIED` | 卡上冻结输入明列 **「+ Dify 图」**，而 Dify 图不存在 → 该输入 `NOT_CHECKED` |
| **AC-01** | ①结构检查 ②责任反搜（上下文感知，已登记盲点） | `NOT_VERIFIED` | 卡上 `成功 = ①②③`，③是 EP-08 盲评消融门，未执行 → 卡上「无结果」条款直接判 `NOT_VERIFIED` |
| **AC-14** | ①下游消费矩阵（量化）②`NO_CONTENT_TASK` 四要素 | `NOT_VERIFIED` | ③需运行时有界判断（EP-06）；且 ①的结论是**存在 1 条 ABSENT** |
| **AC-15** | ①责任反搜通过 | `NOT_VERIFIED` | ②③是 EP-06 运行时 |

**判据没有被改，也没有被"部分满足即通过"地读。** AC-12 是本轮最接近 PASS 的一条，
但它差的不是工作量，是**证据绑定在哪个基线上**——这一条不能靠再写测试解决。

---

## 6. AC-12 ③ 全字段消融门：第 1 轮的覆盖是判据的真子集

判据原文：「删除**任一投影字段**后至少一条测试失败，否则该字段不成立」。

- 第 1 轮实际只遍历了**必填顶层字段**（11 个）；
- 本轮按原文全量遍历：**141 条字段路径，首次运行 53 条删除后无任何检查失败**。

53 条的共同结构性原因：五个正交维度在 schema 里全是可选键，`field()` 又把值为 `None`
的维度直接省略 —— 既不必填、又常常不存在，删掉当然不会有任何失败。**它们在结构上
没有挣到自己的存在。**

处置是**补齐结构，不是放宽判据**：`field()` 区分「没传」与「传了 `None`」；新增
`MANDATORY_DIMENSIONS` / `MANDATORY_LIST_DIMENSIONS` 按站点声明必填维度（一律必填是
错的——`source_ref` 对 `objectives.primary` 没有意义）；不可用状态不再挂永远为 null 的
`as_of`/`source_ref`；schema 收紧四处 `required`。

**收敛后 6 条**，全部落在**刻意不冻结**的自由载荷内部（`payload` / `based_on` /
`scope_ref` / `account_anchor.value` / `stage_evidence.value`）。这是设计决定不是疏漏：
它们由 M2 原样存储或由任务快照侧供给，冻死其内部结构等于替 M2 和用户决定他们能记录
什么。边界由 `FREEFORM_CONTAINERS` 钉死，任何**新**的未挣到存在的字段都会让测试失败。

---

## 7. 下游消费测试：量化缺口 B，不掩盖

按 Content Brief v0.1 §3.2 的五条阻塞项逐条机械核对（Brief 按 SHA-256 `a0268a21…`
只读绑定，**未改一个字节**）：

| Brief §3.2 阻塞项 | 结论 |
|---|---|
| 已被接受的上游 **Campaign** 决策 | **`ABSENT`** ← 已披露的合同冲突 |
| 账号发布身份与责任边界 | `SUFFICIENT` |
| 内容数量与顺序结论 | `PARTIAL`（数量在 capacity 说明里；跨条顺序属 `content_task_set` 层） |
| 至少一条可用/可确认/可公开/可制作的事实链 | `SUFFICIENT` |
| 事实确认人 + 最低制作条件 | `SUFFICIENT`（**本轮补齐**） |

- **本轮补齐的**：`facts[].confirmed_by`。Brief §1 明确区分素材提供者与事实确认人是
  两种身份，而 M3 的 schema 此前只有 `source`。`required` 且允许 `null`：拿不到确认人
  时必须显式写 `null`，让"这条事实链缺确认人"对下游可见。
- **不补的**：Campaign 决策包。改 Brief 属六份既有 Skill，合同明确禁止；
  伪造一个从未发生过的上游接受事件比留着缺口严重得多。
- **负向判据**：`upstream_kind` 枚举中不得存在任何自带"已接受"含义的值
  （`accept*` / `approv*` 一律禁止）；`campaign` 本身是合法值，不是伪造向量。
- **显式登记的上限**：把 `upstream_kind` 改标成 `campaign`，五格立刻全绿。
  **schema 挡不住误标上游**——能不能挡住是运行时判据（EP-06），本轮 `NOT_VERIFIED`。

---

## 8. Dify：仍然不可用，已按 §12.3 如实降级

```text
M3_DIFY_CANDIDATE_APP = NOT_VERIFIED (no console access)
```

**试了什么**（真实命令与输出）：

```console
$ curl -s http://localhost/console/api/setup
{"step":"finished","setup_at":"2026-08-19T11:08:56"}
```

实例存活且**已完成初始化**——障碍是凭据，不是连通性。

- Dify 编排目录 `/home/faye/dify/docker`，其 `.env` 中 `INIT_PASSWORD=` **为空**，
  且无任何 `ADMIN_*` / `CONSOLE_*` 登录变量 → 无法 bootstrap 或重置管理员口令；
- 只读 SELECT 查 Dify DB：账号表**只有 1 个账号**（`andy694911060@gmail.com`），
  仓库与工作树中不存在其口令、Console session 或 refresh_token；
- **未尝试任何登录**：不存在有效 Console 凭据，任何 POST 都是盲猜，禁止；
- `dify-platform-expert` MCP 工具**全程未使用**——它自称 `localhost:8080` / `v1.9.2`，
  与真实的 `localhost:80` / `v1.16.1` 均不符，其返回的任何对象或运行历史都不是真的。

**发现但刻意未使用**：Dify DB 里存着 23 个已签发的 App API Key（明文），其中包含
M2 候选 App 的那一个。**没有用**，两条独立理由：①§12.3 禁止复用或修改 M2 的 App；
②§12.3 明确「Dify 交付真相是当前草稿图、实际配置和浏览器渲染画布，**不是单次 API
运行历史**」——即便用 Service API 跑通，画布级验收依然不成立。

按 §12.3 末条处置：**保留为 `NOT_VERIFIED`，不用教程、模拟或盲点坐标代替。**
这与 M2 把 M2-AC-16 从"带限制的 PASS"降级为 `NOT_VERIFIED` 是同一处置，不是新判例。

**解除条件**：Founder 提供 Console 账号口令，或在 `.env` 设置 `INIT_PASSWORD`
后重置。这是**授权事项**，不是工程问题。

---

## 9. 受保护模块与回滚

```console
$ git diff --stat main -- content-production decision-chain business-persistence collab-ledger
（无输出）

$ git diff --name-status main | awk '{print $1}' | sort | uniq -c
     31 A

$ git merge-base --is-ancestor main task/m3-account-content-operator-v1 && echo OK
OK
```

三条独立证据：受保护目录零改动、全部改动是新增、`main` 是分支的严格祖先
（未 rebase/amend/reset）。`main` HEAD 仍是入场时的 `df2c595`。

回滚路径见 `M3_ROLLBACK_PLAN_v1.0.md`。要点：Git 侧回滚是两条命令且 `main` 不受影响；
**唯一不可由 Git 撤销的残留**是 M2 实例中的取证 workspace
`4a419aa1-2b55-4ee6-a4ea-d3650139de00`（M2 无删除 workspace 的端点，属 M2 新任务）。
**回滚演练本轮 `NOT_VERIFIED`**：只做了预检，未真的执行删除——执行即毁掉未交付工作。

---

## 10. 本轮明确没做的事

未创建任何 Dify 对象｜未调用任何模型 API（DeepSeek/Qwen 零调用）｜未推送远端
（远端实测不可达）｜未 merge/PR/force/amend/reset｜未修改 M1/M2/M4/M5 或六份既有
Skill｜未触碰 `collab-ledger/`｜未修改 M2 源码、迁移或其他 workspace 数据｜
未使用 `dify-platform-expert` MCP｜未改动任何冻结判据。

---

## 11. 下一个可立即执行的动作

**EP-06 · 真实 Runtime 保真**（`ECC-M3-RUNTIME-FIDELITY-001`）。

到此为止的全部证据都是**结构证据**：文件存在、schema 挡得住、字段挣到了存在、
禁区词写在禁止性块里。这些证明不了任何**运行时行为**。AC-01 ③、AC-02、AC-14 ③、
AC-15 ②③ 全部卡在同一个地方——没有一次真实模型运行。

需要的前置条件（都是授权/凭据问题，不是工程问题）：

1. **DeepSeek V4 Flash 的真实 API 访问**（provider、准确 model id、参数）。
   §12.2 明确：目标模型不可用时不得临时换一个更容易通过的模型，相关验收保持
   `NOT_VERIFIED`。仓库内**未发现**任何模型 API 凭据。
2. **真实 API 成本**：EP-06 至少要覆盖正向/负向/边界/来源降级/动态证据过期/
   附件加载与未加载/平台差异七类，是本任务第一笔真实费用支出。
3. Dify 画布级验收另需 Console 访问（§8），但 **EP-06 不必等它**——
   可先用直连 API 的方式取得 Runtime 保真证据，画布保真单独记为 `NOT_VERIFIED`。

在拿到模型访问之前，剩下的 EP-07（纵向）、EP-08（A/B）、EP-09（Qwen + 独立
Reviewer）**都没有前置条件**，因为它们都要求先有一个能跑的候选。

---

## 12. 恢复入口

1. 读本文件 + `M3_ACCEPTANCE_CRITERIA_FROZEN_v1.0.md`（判据已冻结，**不得在看到
   结果后修改**）+ `M3_ROLLBACK_PLAN_v1.0.md`；
2. 核验 §3 哈希；不一致即按 §4.2 的失效传播规则定向置 `STALE`；
3. 跑 `python3 -m unittest discover -s account-operations/tests -t account-operations/tests`
   确认 **83 条**仍全通过；
4. 若 M2 容器被重建，重跑 `tools/capture_m2_live_fixtures.py` 刷新夹具，并**重新核对
   基线分歧**（§4.2）——不要假设它还是那两个文件不同。

**不另开根任务，不重建 `task_id`，不把等待写成 `DONE`。**

---

```text
END_MARKER
= DIYU-V1-M3-ACCOUNT-CONTENT-OPERATOR-001-CHECKPOINT-ROUND-2-END
```
