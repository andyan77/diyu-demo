# 笛语 V1 · M3 Dify 持久卷恢复与整体收口 Execution Prompt v1.0

> `prompt_status`: `READY_FOR_EXACT_FOUNDER_AUTHORIZATION`  
> `planning_task_id`: `01a038f4-000b-7cd0-9dd2-d2dac022bf70`  
> `engineering_task_id`: `DIYU-V1-M3-ACCOUNT-CONTENT-OPERATOR-001`  
> `entry_mode`: `REBASE_TASK`  
> `engineering_execution_performed_by_planning_window`: `false`  
> `construction_authority_created_by_prompt`: `false`  
> `governance`: `RULESIDE-2026-08-25-005 / v0.3.1 revision 2`  
> `contract`: `M3_ENGINEERING_TASK_CONTRACT_v1.4_DIFY_RECOVERY_CLOSEOUT_REBASE.yaml`  
> `contract_sha256`: `787243cf82d7246bb090d0a0c9ff6f64168c964ed1d9a2ab3ef163c75aee6220`

---

## 0. 直接任务

继续同一 M3 工程任务，解除宿主挂载阻断并完成整体收口：

```text
task_id = DIYU-V1-M3-ACCOUNT-CONTENT-OPERATOR-001
entry_mode = REBASE_TASK
starting_status = BLOCKED
target_status = DONE if and only if all applicable gates pass
```

本轮先恢复 Docker Desktop 对 Ubuntu-22.04 宿主持久卷的正确连接；优先找回原 Dify 数据库、原 M3 App ID 和641条历史运行。只有在挂载已经证明正确、原持久数据库仍为空且不会覆盖受保护资产时，才允许使用 ep37 DSL 重建一个**新 UUID**的 M3 当前候选。

本轮模型调用预算固定为 `0`。不得重跑 Founder 七场景，不得修改 main，不得启动 M5。

本 Prompt 和后继合同只有在 Founder 明确授权准确文件名与哈希后才可执行。没有准确授权时保持 `BLOCKED`。

## 1. 准确合同与起点

### 1.1 当前合同

```text
file = M3_ENGINEERING_TASK_CONTRACT_v1.4_DIFY_RECOVERY_CLOSEOUT_REBASE.yaml
SHA-256 = 787243cf82d7246bb090d0a0c9ff6f64168c964ed1d9a2ab3ef163c75aee6220
```

前序合同保留历史身份：

```text
M3_ENGINEERING_TASK_CONTRACT_v1.3_FOUNDER_SINGLE_SET_REBASE.yaml
SHA-256 = 49021e601658194bc734285830d531352c19c1fa4416855c1f524efb073bff49
```

### 1.2 最近冻结现场

```text
worktree = /home/faye/diyu-demo-worktrees/m3-account-content-operator-v1
branch = task/m3-account-content-operator-v1
task remote head = 26ca3601b8d2bdd83f9b2f405b112d7d706b6986
observed remote main = a7b810109f43a4bf500acc285baab477d96796e3
```

启动时必须 fetch 并重新核验。若 task 分支已前进，按实际证据恢复；不得重置、回退或覆盖。

### 1.3 必读阻断证据

| 文件 | SHA-256 |
|---|---|
| `M3_DIFY_RECOVERY_BLOCKER_v1.0.md` | `b1c49993159d0b657cd2be61d2aff9b5c61ae6ca4f634ac3e954dbd6d7e9f400` |
| `account-operations/evidence/ep41-founder-binding-decisions/FOUNDER_BINDING_DECISIONS.json` | `0837d3ad6adb90d51a618a2538a9dfa0791e2635475203d9c6408c3d8f2c63ff` |
| `account-operations/evidence/ep40-dify-recovery-v152/RECOVERY_PRECHECK_AND_BLOCKER.json` | `bdc9af3d66a75ae94874639030721dbf756dcccc1855c14c84a3d58be41f6061` |

同时读取 ep37 完整 DSL 导出、v1.5.2冻结Manifest、七场景提取证据、最终回滚索引和当前任务账本。先核哈希，再使用。

## 2. 已接受且不得重开的结论

```text
M3_FOUNDER_PRODUCT_ACCEPTANCE = PASS
FOUNDER_OFFICIAL_TEST_RUNS = 7
DISCLOSED_EXTRA_SUBMISSIONS = 1
EXECUTOR_MODEL_CALLS_AFTER_REBASE = 0
M3-AC-01..M3-AC-17 = PASS
M3-AC-18 = NOT_APPLICABLE_BY_FOUNDER_REBASE
M3-AC-19 = NOT_APPLICABLE_BY_FOUNDER_REBASE
M3-AC-00 = NOT_VERIFIED_ABSENT
M3-AC-20 = NOT_VERIFIED_ABSENT
```

以下证据身份裁定已经成立，不得再次请求 Founder 选择：

1. S1 绑定具名 v1.5.2；S2-S7 绑定执行内容等价的未命名重发版；不得写成标签相同。
2. S6 正式运行是 `55eb0a6b`；`0a0f406d` 是 `UNAUTHORIZED_EXTRA_SUBMISSION`，保留但不替换、不择优。
3. `user_request` 只接受最多一个结尾 LF 的载体归一化；原始字节不等必须继续披露。
4. 七场景产品结果已经 Founder PASS；不重跑、不再评一次。

## 3. 写入前重入报告

先只读报告：

- cwd、Git 根、分支、本地/远端 HEAD、远端 main、工作树；
- 实际加载的 `CLAUDE.md` / `AGENTS.md` 链；
- 当前 Docker context、Docker Desktop版本、WSL发行版和Dify compose项目；
- 当前容器、状态、挂载、卷、网络和端口清单；
- 当前 Dify `apps/accounts/tenants` 计数；
- 宿主 db/storage 路径和容器实际挂载源；
- 是否存在其他正在执行或写入的容器任务；
- ep37 DSL路径、哈希、节点/边、Skill/Prompt绑定；
- 本轮允许变化面、受保护资产和唯一下一动作。

报告后在授权范围内自主继续。只有真实的受保护资产冲突才停止。

## 4. 强制安全边界

绝对禁止：

```text
docker system prune
docker volume prune
docker container prune
docker image prune
docker network prune
docker builder prune
docker compose down -v
docker volume rm
Docker Desktop factory reset
删除/移动/覆盖宿主 db 或 storage 目录
修改未知目录 owner/mode
```

不得卸载或重装 Docker Desktop，不得删除 ext4.vhdx，不得用新的空目录覆盖旧挂载源。

如果支持的 Docker Desktop UI/CLI 无法安全修改 WSL Integration，不得直接改内部 settings JSON。此时只向 Founder 提供一次准确 GUI 操作：

```text
Docker Desktop
→ Settings
→ Resources
→ WSL Integration
→ 启用 Ubuntu-22.04
→ Apply & Restart
```

Founder完成后从本 Prompt同一任务继续，不建立新任务。

## 5. 阶段A：重启前冻结现场

在重启 Docker Desktop 前：

1. 保存 `docker context ls`、`docker info`、`docker version`；
2. 保存 `docker ps -a`、`docker compose ls`；
3. 对 Dify 全部容器保存 inspect，但对输出做凭据形态扫描；
4. 保存容器挂载的 type/source/destination/read-write 信息；
5. 保存宿主 `/home/faye/dify/docker/volumes/db/data` 与 `app/storage` 的只读元数据；
6. 保存当前容器内对应目录的只读元数据；
7. 记录 `apps/accounts/tenants` 当前计数；
8. 确认当前没有其他任务正在依赖容器持续运行或执行不可中断写入；
9. 确认 Git任务分支干净或精确登记既有变更；
10. 生成重启前证据Manifest。

本阶段不得读取或输出私钥正文、数据库密码、API key或令牌。

## 6. 阶段B：恢复 WSL Integration 并重启一次

本 Prompt 的准确 Founder 授权允许：

- 确认/启用 Docker Desktop 对 `Ubuntu-22.04` 的 WSL Integration；
- 执行最多一次正常 `Apply & Restart`；
- 该重启会停止并重新启动当前 Docker 容器。

优先使用 Docker Desktop受支持的 UI 或受支持 CLI。不得通过杀进程、删锁、改虚拟磁盘或编辑内部配置绕过。

重启完成后等待 Docker Engine 与 Dify compose服务恢复健康；一次轮询不超过60秒，持续记录状态并保持面向Founder的进展更新。

如果 compose栈没有自动启动，允许使用既有 compose文件正常启动；不得创建第二套未记录栈。

## 7. 阶段C：重启后只读判路

先只读运行并落盘：

```bash
docker exec docker-db_postgres-1 \
  psql -U postgres -d dify -tAc "select count(*) from apps;"
```

同时读取：

- `accounts`计数；
- `tenants`计数；
- M3原App ID是否存在；
- 641条workflow历史是否恢复；
- 宿主/容器 db与storage身份是否一致；
- 原租户ID、storage目录和数据库租户是否一致；
- Dify setup状态。

不得只看 `apps` 一个数字就写入。按以下决策树执行。

## 8. 路径A：原数据库和原App返回

进入条件：

- `apps > 0`；
- 原租户、storage与数据库身份一致；
- 原 M3 App ID `b7fb5b1a-9278-426c-bb8a-f9f288639548`存在；
- 历史运行和当前Dify对象不存在明显错库证据。

动作：

1. **不得导入 ep37**；
2. 只读核验原 M3 App、641条历史日志和七条Founder运行；
3. 核验当前草稿/已发布图、系统提示词、Skill、模型/provider/温度；
4. 若当前发布版本不是可恢复的 v1.5.2，但App身份正确，允许用冻结v1.5.2/ep37内容恢复当前候选并发布，仍不得运行模型；
5. 记录发布前后图与Prompt哈希；
6. 浏览器核验当前真实画布；
7. 做一次当前DSL导出，与冻结v1.5.2逐项比对；
8. 对当前Dify compose做一次普通停止/启动或等价持久性复核，证明App没有因容器重建消失；不得重启Docker Desktop第二次；
9. 重新核验App、版本和图仍在。

成功后：

```text
RECOVERY_PATH = ORIGINAL_DATABASE_AND_APP
CURRENT_APP_ID = b7fb5b1a-9278-426c-bb8a-f9f288639548
```

## 9. 路径B：正确挂载后数据库仍为空

只有同时满足以下条件才进入：

- 已证明Docker Desktop当前正确解析到预期持久宿主卷；
- `apps = 0`、`accounts = 0`、`tenants = 0`；
- 没有原数据库可安全恢复的证据；
- 宿主storage中的旧租户资产不会被新租户覆盖、误认或修改；
- 当前空数据库、宿主db/storage和Dify配置已做只读备份/快照；
- ep37 DSL哈希和结构全部正确；
- 不需要删除、移动、改权或覆盖受保护目录。

若宿主storage保留旧租户资产但无法证明与新环境安全隔离，**不得初始化新租户或导入DSL**，转路径C。

满足全部条件后，允许：

1. 通过Dify正常setup流程建立一个明确标记为M3恢复用途的非生产租户；
2. 从精确 ep37 DSL导入一个 M3任务专用 App；
3. 接受Dify生成新的App UUID；
4. App名称必须含任务ID、`RECOVERED CANDIDATE TEST ONLY`和非生产警示；
5. 发布名使用 `m3-cand-v1.5.2-recovered`，不得冒充历史具名发布记录；
6. 不导入、伪造或回填641条历史运行到新数据库；
7. 不把新UUID写成历史Founder七场景App；
8. 不运行工作流，不调用模型；
9. 读回图、Prompt、模型参数和所有确定性代码；
10. 与冻结 v1.5.2逐项比对；
11. 浏览器核验真实画布；
12. 导出恢复后DSL并与ep37作语义/结构和允许载体差异比对；
13. 对Dify compose做一次普通停止/启动持久性复核；
14. 重启后再次确认新App、发布版本和图仍在。

双重身份必须写明：

```text
HISTORICAL_FOUNDER_RUN_APP_ID
= b7fb5b1a-9278-426c-bb8a-f9f288639548

CURRENT_RECOVERED_APP_ID
= <new UUID>

IDENTITY_RELATION
= CONTENT_ADDRESSED_V1.5.2_RECOVERY_NOT_HISTORICAL_APP_ID
```

Founder产品PASS仍只绑定历史七条输出；新App只承担当前可运行候选和回滚恢复证明。

## 10. 路径C：仍不安全或无法判定

以下任一成立，停止：

- 挂载是否正确仍无法证明；
- 原db/storage存在但当前权限不足以只读确认；
- 旧租户资产与新setup可能碰撞；
- 恢复需要删卷、改权、覆盖目录或重置Docker；
- ep37与v1.5.2哈希/结构不符；
- 发现其他项目资产或正在运行的无关任务会被恢复动作影响。

输出 `BLOCKED`，只报告精确缺口、证据和解除主体。不得导入DSL，不得重跑七场景，不得调用模型。

## 11. AC-00与AC-20收口

路径A或安全完成的路径B都必须重算：

### M3-AC-00

需要同时成立：

- 原 `task_id`、任务分支和当前远端commit绑定；
- 当前持久活体M3 App存在；
- 当前App的v1.5.2 Skill、Prompt、图、模型/provider/温度绑定成立；
- 当前App在普通compose重启后仍存在；
- 历史App与新恢复App（如有）身份没有混写。

### M3-AC-20

需要同时成立：

- Founder七场景PASS和证据继续绑定历史输出；
- 当前活体候选与v1.5.2恢复证据成立；
- 回滚导出与恢复入口当前有效；
- 最终证据索引完整；
- 任务分支推送并用 `git ls-remote`核验；
- worktree干净；
- 声明上限准确；
- main、PR、M5和生产均未改变。

不得因为Founder PASS自动将技术门写成PASS；也不得要求Founder重新跑模型来关闭技术门。

## 12. 证据和文件

至少新增并落盘：

```text
M3_DIFY_RECOVERY_FINAL_CLOSEOUT_v1.0.md
account-operations/evidence/ep42-dify-host-mount-recovery/
account-operations/evidence/ep43-dify-live-candidate-binding/
account-operations/evidence/ep44-m3-final-closeout/
```

保存：

- 重启前后Docker/context/container/mount清单；
- apps/accounts/tenants计数；
- 采用路径及排除另一条路径的证据；
- 原App或新UUID身份；
- 当前图、Prompt、Skill、模型参数和DSL哈希；
- compose持久性复核；
- AC最终真源；
- rollback入口；
- 凭据扫描结果；
- Git本地/远端完整哈希；
- 所有失败尝试和外部副作用。

任何含凭据的原始输出不得进入Git；只保存脱敏结构、哈希和检查结果。

## 13. Git与远端收口

1. 只修改M3任务worktree；
2. 不覆盖既有历史证据；
3. 新证据只追加；
4. 提交前做凭据逐字节和通用形态扫描；
5. commit并push `task/m3-account-content-operator-v1`；
6. 用 `git ls-remote`核验完整远端哈希；
7. 核验worktree干净；
8. 核验远端main未因本任务变化；
9. 不建PR，不合并main。

## 14. 终态回执

若全部适用门成立，输出：

```text
M3_ENGINEERING_TASK
= DONE

M3_FOUNDER_PRODUCT_ACCEPTANCE
= PASS

M3-AC-00
= PASS

M3-AC-20
= PASS

DIFY_RECOVERY_PATH
= ORIGINAL_DATABASE_AND_APP | NEW_CONTENT_ADDRESSED_APP

DIFY_TASK_APP
= RECOVERED_PERSISTENT_AND_CURRENT

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

MAIN_MERGE
= NOT_AUTHORIZED_NOT_PERFORMED

M5
= NOT_STARTED_NOT_AUTHORIZED

REAL_BUSINESS_LIFT
= NOT_VERIFIED
```

同时附当前/历史App ID、恢复路径、任务分支完整远端commit、Dify/Skill/Prompt/图/DSL哈希、AC矩阵、回滚入口、Founder PASS记录、持久性复核和凭据扫描结果。

如果无法安全恢复，输出：

```text
M3_ENGINEERING_TASK
= BLOCKED

M3_FOUNDER_PRODUCT_ACCEPTANCE
= PASS

DIFY_TASK_APP
= NOT_RECOVERED

EXECUTOR_MODEL_CALLS_AFTER_REBASE
= 0
```

并只列真实阻断，不新增模型测试或验收轮次。

`END_MARKER: M3-DIFY-RECOVERY-AND-FINAL-CLOSEOUT-EXECUTION-PROMPT-v1.0-END`
