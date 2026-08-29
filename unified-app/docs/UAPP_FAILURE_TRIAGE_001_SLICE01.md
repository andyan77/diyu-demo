# FAILURE TRIAGE 001 · 最薄切片首轮 slice01

`task_id: DIYU-V1-UNIFIED-DIFY-APPLICATION-001` ｜ 证据：`unified-app/evidence/UAPP_RUN_slice01.json`
（run `823f5fbe-70a4-411a-8b58-497b679ffc9f`，HTTP 200，31 个节点实际执行）

```yaml
observed_failure:
  - "boot_acct / boot_cycle / boot_task 三个 M2 写入节点被 Dify 报为『blocked by SSRF protection』"
  - "uapp_m2_cycle / uapp_m2_dec / uapp_m2_run 三个只读节点返回 404"
  - "最终回复把内部字段名原样交给用户：audience_problem；expected_change；content_promise；expression_subject_and_boundary"
frozen_target: "薄切片通过条件第 3 条（M2 真实返回测试 workspace 当前投影）与第 6 条（零内部字段泄漏）"
candidate_sources:
  - INPUT_ENVIRONMENT_OR_TOOL   # Dify 的 SSRF 保护 / squid 真的在拦
  - SYSTEM_UNDER_TEST           # 新画布自己接线错了
  - CHECKER_OR_FIXTURE          # 运行器读错了
confirmed_origin: "SYSTEM_UNDER_TEST（两处，都是新画布自己的接线，与 M1-M5 既有资产无关）"
```

## 归因一：不是 SSRF，是 M2 的权限校验，被 Dify 的错误分类掩盖了

**Dify 的报错是误导性的。** `core/helper/ssrf_proxy.py:251` 的判定是：响应码属于 `(401, 403)`
且响应头里有 squid 标识，就报「blocked by SSRF protection」。而 squid 会给**每一个**经过它的响应
都盖上 `via: 1.1 … (squid/6.13)`，所以**任何来自源站的 401/403 都会被贴上 SSRF 的标签**。

现场分别控制变量证伪与证实（都经 `ssrf_proxy:3128`，与 Dify HTTP 节点同一条路）：

| 探针 | 结果 |
|---|---|
| 空 `X-Actor-Ref` + `GET /healthz` | `200`（→ 空头本身不被 squid 拦，SSRF 假说证伪） |
| `POST /workspaces/{ws}/accounts`，空 `X-Actor-Ref` | `401 {"detail":"X-Actor-Ref header is required"}` |
| 同上，不带该头 | `401` 同上 |
| 同上，带合法 actor | `200`，账号建成 |

**真实原因**：新画布的建域链把 `X-Actor-Ref` 绑到了 `conversation.uapp_actor`，
而这个会话变量由建域链**最后一个**节点 `boot_assign` 才写入——建域进行中它一直是空的。
`boot_user`（`POST /users`）与 `boot_ws`（`POST /workspaces`）不在任何 workspace 之内、
不需要 actor，所以这两个成功了；从 `boot_acct` 开始进入 workspace 作用域，M2 依约要求 actor，
于是 401。

**404 是它的下游后果，不是独立故障**：账号没建成 → `conversation.uapp_account` 为空 →
只读 URL 退化成 `/workspaces/{ws}/accounts//cycles/current` → 404。修上游即消失，
不在下游打补丁。

## 归因二：用户投影盖掉了接缝已经写好的自然语言

接缝这一轮**做对了**：`business_delivery_outcome = UNKNOWN` + 组件级 Return，
并且它自己写了给用户看的 `user_delivery`：

> 「这一步我还差一样东西才能往下判断：你想说给谁听？她现在具体卡在哪一步？只补这一项就够了，
> 其他已经给过的内容不用再说一遍。这一轮里不依赖这一步的其他事情不受影响，可以照常继续。」

这句话是合格的用户交付。`uapp_delivery` 的分支顺序把它跳过了：只要 `delivered` 为假且
`returns_json` 里有 `precise_gap`，就直接用 `precise_gap` 原文拼消息——而 `precise_gap`
是给机器看的字段名清单。**内部字段泄漏是这个分支顺序造成的，不是接缝的问题。**

`user_delivery` 是唯一可直接呈现给用户的字段（M5 运行时 `USER_VISIBLE` 的同一条纪律）；
它非空时就该用它，不该由本画布另写一份。

## 归因三：M3 没有失败（更正首读）

`uapp_m3` 的 `error` 字段里有一条 DeepSeek `SSLEOFError`，但那是**被重试掉的一次尝试**；
节点 `status = succeeded`，`outputs.operating_judgment` 是完整的中文运营判断，
并且如实写明了两个硬缺口以及「M2 的周期、已发布内容和反馈查询都没成功」。
**M3 的行为正确**，它甚至替我们把 M2 的失败如实报了出来。这一条登记为一次传输层 Attempt，
不计入失败，不修改 M3。

```yaml
mutation_target:
  - "unified-app 新画布的建域链 HTTP 头绑定（boot_acct / boot_cycle / boot_task）"
  - "unified-app 新画布的 uapp_delivery 分支顺序与标识符黑名单"
protected_targets:
  - "M1 子图与 m1_context_compiler_v0.1.py（逐字节复用，未证明有错，不改）"
  - "最终 FP M3 / hop / Seam 与六个能力应用（本轮行为正确，不改）"
  - "M2 服务本身（401 是它按约定做的权限校验，正确行为，不改）"
  - "旧 Founder Canvas、旧 provider、main、非测试数据"
next_reverification:
  - "重跑同一条自然语言输入，要求：建域五步全部 2xx；三个只读投影 200；"
  - "最终回复中不出现任何 snake_case 内部字段名；"
  - "确定性检查 D-12 泄漏防线正负控制仍通过。"
```

**未修改 Dify 的 SSRF 误分类。** 那是平台的错误归类，属于 `INPUT_ENVIRONMENT_OR_TOOL`，
不阻断本任务；如实记在这里，避免下一个人再被这条报错带偏一次。
