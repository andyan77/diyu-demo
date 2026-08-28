# M3 · Founder 证据绑定裁定登记 + Dify 恢复阻断 v1.0

- `task_id`：`DIYU-V1-M3-ACCOUNT-CONTENT-OPERATOR-001`
- `entry_mode`：`RECOVERY_TASK`（不建 NEW_TASK，合同不变）
- 合同：`M3_ENGINEERING_TASK_CONTRACT_v1.3_FOUNDER_SINGLE_SET_REBASE.yaml`
  sha256 `49021e601658194bc734285830d531352c19c1fa4416855c1f524efb073bff49`
- 授权事件：`FOUNDER_EVIDENCE_BINDING_AND_RECOVERY_DECISION = ACCEPTED`
- **本轮执行侧模型调用：0**

---

## 1. 三项 Founder 裁定已登记，依据由执行侧独立复算

证据：`account-operations/evidence/ep41-founder-binding-decisions/FOUNDER_BINDING_DECISIONS.json`

### 1.1 未命名重新发布版本 = `EXECUTION_CONTENT_EQUIVALENT_TO_M3_V1.5.2`

Founder 接受它作为 S2–S7 的**执行内容等价载体**，**不宣称版本标签与
`m3-cand-v1.5.2` 相同**；`marked_name` 为空这条真实历史记录原样保留。

等价依据六项，全部由执行侧确定性比对算出（Founder 只接受其证据身份，
**不代替执行侧自证技术等价**）：

| 依据 | 结果 |
|---|---|
| 七个节点 `data` 逐字节相同 | 7/7 运行成立 |
| 六条边的执行拓扑相同 | 7/7 运行成立 |
| 系统提示词 SHA-256 相同 | 全部 = `3a3c657d82d45e96dfbf9abdcb88adf66c58bb74f69f1e1e0412591242898028` |
| Skill 绑定相同 | 同一提示词 ⇒ 同一 `SKILL.md` `90596da5…` |
| 模型 / provider / temperature 相同 | 全部 `deepseek-v4-flash` / `langgenius/deepseek/deepseek` / `0.4` |
| `gate` / `assemble` / `post_gate` 离线重算与线上记录逐字节相同 | 8/8 三节点全部成立 |

记为**非执行语义差异**：节点 `position` / `positionAbsolute` / `height`、
边的前端标记 `isInLoop`、画布 `viewport` 平移与缩放。

绑定归属：**S1** → 发布前的具名 `m3-cand-v1.5.2`（`706fdce0…`）；
**S2–S7** → 未命名但执行内容等价的重新发布版本（`ff801653…`）。

### 1.2 S6 重复提交

```text
official_S6_run_id = 55eb0a6b-44ac-4370-bc8a-478cf5fc7d07   （正式，绑定验收证据）
extra_S6_run_id    = 0a0f406d-d4d3-4c4e-9596-2f0c936f5117   （UNAUTHORIZED_EXTRA_SUBMISSION）

S6_FIRST_OUTPUT_PRODUCT_ACCEPTANCE  = PASS
S6_SECOND_OUTPUT_PRODUCT_ACCEPTANCE = PASS

FOUNDER_OFFICIAL_TEST_RUNS   = 7
DISCLOSED_EXTRA_SUBMISSIONS  = 1
```

第二次完整保留、不删除、不覆盖、**不作为正式重试**、不替换第一份、两份之间不择优。
该产品接受确认**不把第二次运行改写成符合「一次运行」协议**。

### 1.3 结尾换行 = `DIFY_UI_CARRIER_NORMALIZATION_ACCEPTED`

机械复算结果（八条运行逐条算过）：

| 检查 | 结果 |
|---|---|
| `account_context` 八条逐字节相同 | 成立 |
| `loaded_references` 八条逐字节相同 | 成立 |
| `user_request` 每条**最多只去掉一个**结尾 LF | 成立 |
| 去掉后与冻结输入**逐字节相同** | 成立 |
| 除结尾 LF 外存在任何其他字符差异 | 无 |

原始 SHA-256 与归一化后 SHA-256 **两套都保留**在证据里。
**不得写成「输入逐字节完全相同」。** 该豁免不得套用到其他空白、标点、字段或内容差异。

---

## 2. Dify 恢复：**未完成，阻断**

证据：`account-operations/evidence/ep40-dify-recovery-v152/RECOVERY_PRECHECK_AND_BLOCKER.json`

### 2.1 恢复前六项只读核验

| 项 | 结果 |
|---|---|
| 4.1 PostgreSQL 确为新初始化 | 成立（容器日志走了 initdb；PGDATA 内全部文件为启动时刻） |
| 4.2 `apps` 表 0 行 | 成立 |
| 4.3 活库内无需保护资产 | 活库成立（`tenants` / `accounts` / `datasets` / `workflows` / `workflow_runs` / `messages` / `upload_files` 全 0）；**但宿主卷上仍有原租户资产，见 2.2** |
| 4.4 ep37 DSL 存在、哈希正确、内容完整 | 成立（`bd676f29…`、7 节点 6 边、提示词 `3a3c657d…`、无 `http_request` / `tool` 节点） |
| 4.5 恢复不会覆盖其他项目或生产 Dify | **不成立 —— 阻断点** |
| 4.6 凭据不写入仓库或日志 | 成立 |

### 2.2 阻断：容器的 bind mount 没有解析到 WSL 宿主路径

`DIFY-BIND-MOUNT-NOT-RESOLVING-TO-WSL-HOST`

三条互相独立的证据：

**① 同一个 bind source，宿主与容器的目录元数据不同**

| | 目录元数据 |
|---|---|
| 宿主 `/home/faye/dify/docker/volumes/db/data` | `drwxr-xr-x 3 root root 4096 Aug 19 03:49` |
| 容器 `/var/lib/postgresql/data`（同一 bind source） | `drwxr-xr-x 3 root root **60** Aug 27 **21:39**` |

size 与 mtime 都不同 ⇒ **不是同一个目录**。

**② app storage 同理，且宿主上的原租户资产完好**

- 宿主 `/home/faye/dify/docker/volumes/app/storage`：含 `.dify_secret_key`、
  `privkeys/09758721-a8d3-4f01-b0f2-c69c82a11568/private.pem`、
  `upload_files/09758721-…`，**共 34 MB**
- 容器 `/app/api/storage`：**空目录，root 所有**（容器以 uid 1001 运行）

**③ setup 的失败信息暴露了租户 id 不一致**

```text
PermissionDenied at write => privkeys/9f32db4d-472f-432c-b401-5f87431a1c7a/private.pem
```

容器侧要新建的是租户 `9f32db4d…`，宿主上的原租户是 `09758721…`。

### 2.3 为什么停在这里，不硬推

1. 授权 §4.5 要求恢复动作不会覆盖其他项目或生产 Dify。当前写入落在 Docker VM 内的
   临时位置，**下次容器重建即消失** —— 那不是恢复，把它记成 `RECOVERED_AND_CURRENT`
   是假闭合。
2. 授权 §4 的停止条款：宿主卷上仍有原租户 `09758721…` 的 privkeys 与 34 MB 上传文件，
   属于「需要保护的资产」；在挂载错位状态下建第二个租户，可能在挂载修复后与其冲突。
3. 修复挂载要重启 Docker Desktop / 重设 WSL 集成 —— 会停掉你全部容器，
   不在本任务授权范围内，是你自己的决定。

### 2.4 失败尝试的残留：零

那次 `POST /console/api/setup` 返回 500 之后：`accounts` = 0、`tenants` = 0、`apps` = 0，
容器侧 storage 未被写入。**Dify 上没有成功的写操作。**

### 2.5 一条必须先说清楚的事

即使挂载修复后用 DSL 重建，Dify 的导入会生成**新的 App UUID**，
原 `b7fb5b1a-9278-426c-bb8a-f9f288639548` **不可由 DSL 还原**。
七次 Founder 运行的历史绑定仍指向原 App ID，不得与重建后的活体 App 混为一谈。

宿主 `pgdata` 为 root 所有、本机无免密 sudo，执行侧读不到，
因此**不能断言**原数据库文件完好 —— 只能说宿主 storage 卷完好且仍是原租户。
原库是否幸存，挂载修复后一测便知。

---

## 3. 解除阻断的动作（归 Founder）

1. 在 Docker Desktop 里重启或重设 WSL 集成
   （Settings → Resources → WSL Integration，确认 `Ubuntu-22.04` 已勾选），
   或直接重启 Docker Desktop。**会停掉全部容器。**
2. 重启后先只读测一句：

   ```bash
   docker exec docker-db_postgres-1 psql -U postgres -d dify -tAc "select count(*) from apps;"
   ```

   若回到**非 0**，说明原库连同 641 条运行记录一并回来了，
   **根本不需要用 DSL 重建**，本轮 §4 的恢复目标可直接用原 App 达成。
3. 若仍为 0 且挂载已正确解析到宿主卷，再授权执行侧用 ep37 的 DSL 导入重建
   （届时 App UUID 会变，按 2.5 披露）。

---

## 4. 终态

```text
M3_ENGINEERING_TASK
= BLOCKED

M3_FOUNDER_PRODUCT_ACCEPTANCE
= PASS

FOUNDER_OFFICIAL_TEST_RUNS
= 7/7_BOUND_AND_PRESERVED

DISCLOSED_EXTRA_SUBMISSIONS
= 1

EXECUTOR_MODEL_CALLS_AFTER_REBASE
= 0

BLIND_REVIEW
= NOT_APPLICABLE_BY_FOUNDER_REBASE

MODULE_AB_GAIN_VS_GOOD_PROMPT
= NOT_CLAIMED

DIFY_TASK_APP
= NOT_RECOVERED_BLOCKED_ON_HOST_MOUNT

MAIN_MERGE
= NOT_AUTHORIZED_NOT_PERFORMED

M5
= NOT_STARTED_NOT_AUTHORIZED

REAL_BUSINESS_LIFT
= NOT_VERIFIED
```

`BLOCKED` 的合同依据：`blocked: a required external fact, access or Founder run cannot
proceed after all authorized in-scope work is complete.` —— 本轮授权范围内能做的全部做完了
（三项裁定登记并复算、六项恢复前核验、阻断定性到根因），
剩下的那一步需要执行侧无权做的外部访问修复。

### AC 重算

| 验收项 | 状态 | 依据 |
|---|---|---|
| `M3-AC-00` | `NOT_VERIFIED` (ABSENT) | 内容等价裁定已成立并复算通过；**最终活体 App 绑定与恢复证据缺失**（授权 §6.1 要求三者共同重算） |
| `M3-AC-01`–`M3-AC-17` | `PASS` | 保持 Founder 七场景 PASS + 确定性证据；不受恢复阻断影响 |
| `M3-AC-18` | `NOT_APPLICABLE_BY_FOUNDER_REBASE` | 历史 `NOT_VERIFIED` 原样保留 |
| `M3-AC-19` | `NOT_APPLICABLE_BY_FOUNDER_REBASE` | 同上 |
| `M3-AC-20` | `NOT_VERIFIED` (ABSENT) | Founder PASS、七场景证据、回滚 DSL、远端任务分支均成立；**活体 Dify 恢复缺失** |

### 五条不得改写（授权 §6，全部遵守）

- 未命名版本**没有**被写成具名版本
- 结尾换行**没有**被写成原始字节一致
- S6 第二次提交**没有**被写成合法重试
- Dify 重建**没有**被写成历史数据库恢复（本轮根本没重建）
- Founder 接受**没有**被写成技术证据自证

### 声明上限

本轮只能说：三项证据绑定裁定已登记且依据经执行侧独立复算成立；
Dify 任务专用 App 未恢复，阻断原因已定位到根因并给出解除动作。
不得声称优于一份好提示词、M5 成品增益、已生产上线、真实经营提升或因果增益。
