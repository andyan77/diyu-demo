# 统一 Dify 应用 · 激活记录与 FAILURE TRIAGE v1.0

- `task_id`: `DIYU-V1-UNIFIED-DIFY-APPLICATION-001`
- `entry_mode`: `NEW_TASK`（新任务，不重开、不改写已 `DONE` 的 M5）
- `task_progress`: `IN_PROGRESS`；`terminal_state`: 留空
- 日期：2026-08-29

## 一、激活复算（全部现场核验，规划观察值只作交接锚点）

| 项 | 期望 | 现场 | 结果 |
|---|---|---|---|
| Root Prompt sha256 | `4b72d4ec…6e11a893` | 同 | 一致 |
| Task Contract sha256 | `279f80ba…921e869f` | 同 | 一致 |
| `origin/main` | `01a42b0ed97344a67302ecb6778ae4a772eb28b2` | 同 | 一致（未前进） |
| M5 Final Receipt | `ba001edd…94f9fa29` | 同 | 一致 |
| M5 Manifest v1.1.4 | `f8757bc7…3fdb8fb148` | 同 | 一致 |
| M5 Runtime 参考 | `833d4f68…4b54ee45` | 同 | 一致 |
| 十个受保护未跟踪文件 | 10 | 10 | 在位 |
| live main tracked dirty | 无 | 无 | 干净 |

Dify 与服务现场：

| 项 | 现场 |
|---|---|
| 旧 Founder Canvas `f0b1c5f5…` | 存在，`advanced-chat`，`enable_site=t`，`enable_api=t` —— **只读参考** |
| 最终 FP M3 `a4c3b19b…` | 存在，`workflow`，site/api 均启用 |
| 最终 FP Seam `5fca0162…` | 存在，`workflow`，site/api 均启用 |
| 六能力应用 | 六个全部存在，site/api 均启用 |
| M2 服务 `diyu-m2-app` | Up；从 `docker-api-1` 访问 `http://diyu-m2-app:8000/openapi.json` 返回 **200** |
| 控制台凭据 | `~/.dify-console.env` 存在（只查存在性，未读内容） |

**激活成立**，无 `INVALID` 条件。

## 二、任务现场

```text
branch   = codex/v1-unified-dify-application-001
worktree = /home/faye/diyu-demo-worktrees/v1-unified-dify-application
base     = 01a42b0ed97344a67302ecb6778ae4a772eb28b2
```

未复用 M5 已完成分支施工；未触碰 main 工作区的十个未跟踪文件。

## 三、FAILURE TRIAGE

```yaml
observed_failure: "没有一个最终 Dify App 能独立承接完整 M1-M5 用户体验"
frozen_target: "一个自然语言 Dify 入口；内部按需复用已验证模块；无需外部脚本"
candidate_sources:
  - CONTRACT_OR_INTENT
  - ORACLE_OR_CRITERION
  - CHECKER_OR_FIXTURE
  - INPUT_ENVIRONMENT_OR_TOOL
  - SYSTEM_UNDER_TEST
  - INSUFFICIENT_EVIDENCE
confirmed_origin: SYSTEM_UNDER_TEST（缺件，非缺陷）
mutation_target: "新的统一 Canvas 与其专属薄编排/适配层"
protected_targets: "旧 Canvas 与旧 provider、最终 FP 八应用、M1-M5 已接受资产、M2 非测试数据"
next_reverification: "同一新应用的单入口主故事、六能力可达性、P0 负例与恢复"
```

### 归因依据（现场证据，不是复述规划）

**其一，旧 Canvas 绑的不是最终 Seam。** 现场查库确认旧 Canvas 仍指向 legacy Seam
`de0cb1e9…`，而最终 FP Seam 是 `5fca0162…`。所以旧 Canvas 即便能打开，
跑的也不是本轮已验证的那一套。**不得把它改名冒充最终交付。**

**其二，编排在应用外。** M1 上下文编译、M2 调用、M3→Seam 路由、用户投影、
发布/反馈写回与 Cycle N+1 目前由 `DIYU_M5_INTEGRATION_RUNTIME_v0.1.py` 在 Dify 之外完成。
`M5_BIND` 这类环境变量本身就是"用户要懂内部"的证据。

**结论：这是缺件，不是缺陷。** M1–M5 的模块行为已被 M5 轮证明；缺的是把已验证的
编排责任搬进一个用户可见的 Dify 应用。因此 `mutation_target` 只有新建的统一 Canvas 与
其薄适配层，**不含**任何已接受资产。

### 已识别、需在最薄切片中先证伪的技术前提

按 A2，以下是**假设**，不是已观察：

| # | 假设 | 为什么必须先证 | 证伪方式 |
|---|---|---|---|
| H1 | Dify HTTP 节点能从容器网络访问 `http://diyu-m2-app:8000` | M5 Runtime 里写着「宿主没有到 diyu-m2-app 的端口映射」，走的是 docker exec relay；Dify 的 HTTP 请求节点还要过 `ssrf_proxy`，未必放行 | 在薄切片里放一个 HTTP 节点实调 M2 只读端点，看返回码 |
| H2 | M1 的上下文编译行为可在 Dify 内等价表达 | 现行实现是仓库里的 Python（`m1_context_compiler_v0.1.py`）；若从旧 Canvas 复用代码节点，必须证明与当前 M1 源等价，否则形成漂移副本 | 用既有 fixture 对比新旧输出 |
| H3 | 任务命名 provider 能绑定最终 FP M3/Seam 且不影响旧 provider | 旧 provider `2daa2d27…` 必须原样不动 | 建新 provider 后复算旧 provider 与旧 Canvas graph |

**H1 未成立前不扩架构。** 若 H1 为假，最高失效节点是网络能力，
届时按 `INPUT_ENVIRONMENT_OR_TOOL` 归因并另找 Dify 内可靠表达，
而不是先把六能力堆进画布。

## 四、本轮不做的事（合同 `non_goals`，逐条继承）

不重做 M1–M5；不偿还 M5 八项技术债；不固定串行全链；不建第二套数据库/状态机/路由器；
不做真实发布；不把旧 Canvas 改名冒充新交付；不要求用户填 capability/entry/权限/状态词/JSON。

---

## 五、H1 已证成立（2026-08-29，确定性检查，零模型调用）

Dify 容器网络到 M2 的可达性实测：

| 路径 | 结果 |
|---|---|
| `docker-worker-1` → `http://diyu-m2-app:8000/openapi.json` | **200** |
| `docker-api-1` 经 `ssrf_proxy:3128` → 同上 | **200** |

M2 与 Dify 同在 `docker_default` 网络（M2 容器 IP `172.18.0.15`）。
**结论**：统一 Canvas 可以用原生 HTTP 请求节点直连 M2，
不需要 M5 Runtime 那套 `docker exec` relay，也不需要新增第二运行时。
`H1` 由假设升为**已观察**。

## 六、任务命名 provider 已建（只新建，不改既有）

| 用途 | 目标应用 | provider | 参数（从目标应用当前已发布 start 节点派生，未硬编码） |
|---|---|---|---|
| M3 | `a4c3b19b…`（最终 FP M3） | `9ea86217-8791-489c-9a96-b880ae558ac5` | `account_context` / `user_request` / `loaded_references` |
| 六能力接缝 | `5fca0162…`（最终 FP Seam） | `f8d63527-8c45-4823-8159-443cef37240d` | `capability` / `entry` / `capability_call` / `professional_input` / `example_reference_requested` |
| 跨能力抽取适配 | `6c46fdb1…`（hop v0.2） | `fd3f6f29-237f-4bbe-a820-5d38076ab52e` | `target_capability` / `m3_judgment` / `upstream_delivery` / `upstream_capability` / `registered_facts` / `account_context` / `user_request` / `focus_fields` |

**保护面复算**：旧 Seam provider `2daa2d27…` 的 `app_id` 与 `version` 未变
（仍绑 legacy `de0cb1e9…`，version `2026-08-27 20:36:22.268824`）；
旧 Founder Canvas graph md5 = `67b717d1365c2fb75a3b8e761b0527da`。
证据：`unified-app/evidence/UAPP_PROVIDERS_CREATED.json`。

**为什么 provider 只建三个**：六个能力应用由 Seam 内部调用，统一 Canvas 不直接绑它们——
直接绑六个等于把「谁来接这一跳」的责任从 Seam 搬到 Canvas，那是复制专业语义，
合同 `non_goals` 明确禁止。
