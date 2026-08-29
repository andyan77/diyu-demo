# 统一 Founder Canvas · H2 裁定与最薄纵向切片设计 v1.0

`task_id: DIYU-V1-UNIFIED-DIFY-APPLICATION-001` ｜ `task_entry_mode: CONTINUE_TASK` ｜ `task_progress: IN_PROGRESS`

本文件记录 Node C2 的两件事：H2 怎么成立的，以及最薄切片为什么长这样。
不复制合同正文，不改验收语义。

---

## 一、H2｜M1 的上下文编译行为可在 Dify 内等价表达

### 结论

`H2 = PASS / CURRENT`。**等价性由构造保证，不是由再实现之后的行为比对保证。**

### 证据

1. **已发布的 M1 候选应用里，编译器就是仓库那份源码本身。**

   | 载体 | sha256 |
   |---|---|
   | 仓库 `decision-chain/workflows/m1_context_compiler_v0.1.py` | `326d08880b3520b93b70edd68b67d8ea3986364325787b57b2b270c2f29f1e3b` |
   | Dify app `dd638b91…` 的 `m1_compiler` 代码节点正文 | `326d08880b3520b93b70edd68b67d8ea3986364325787b57b2b270c2f29f1e3b` |

   两者长度同为 73804 字节，逐字节相同。M1 从设计上就是「独立源码 + 以字符串嵌入 Dify Code 节点」，
   `build_m1_candidate_dsl_v0.1.py` 就是这么装的。

2. **新画布不是"照着 M1 再写一遍"，是把 M1 子图整段搬过来。**
   `m1_extract` / `m1_join` / `m1_shadow` / `m1_compiler` / `m1_save_snapshot` 五个节点的
   `data` 直接取自已发布的 M1 图，**节点 id 一并保留**——于是节点内部所有 `value_selector`
   （`m1_shadow` 的提示词模板、`m1_compiler` 的四个入参、`m1_save_snapshot` 的写回目标）
   无需改写就仍然有效。构建脚本对这五个节点逐个做 `json.dumps(sort_keys=True)` 比对，
   五个全部 `VERBATIM`。自然对话节点 `m1_chat_llm` 同样逐字节复用（仅改标题）。

3. **仓库夹具套件在同一份源码上通过。**
   `python3 decision-chain/workflows/test_m1_context_compiler_v0.1.py` → `Ran 216 tests … OK`。
   覆盖输入归一化、task/account context 核心字段、事实与权限边界、缺口、能力路由输入
   （`compute_call_intent` 的 `needed_capabilities` / `per_capability` / `non_blocking_gaps`）。

### 这条结论不覆盖什么

- 它说的是**编译行为**等价，不是「新应用的对话体验等于 M1 候选应用」。新画布在 M1 之后接了
  路由、M2、M3 与接缝，那是新增行为，不在 H2 范围内。
- 载体是两份（仓库源码 + 图内字符串）。二者当前一致，但这是**副本关系**，
  按 A3 必须持续同步——已登记为确定性检查项（图内 `m1_compiler` 正文 sha256 必须等于仓库源码 sha256）。

---

## 二、最薄切片的形状

```text
自然语言 → M1 子图（逐字节复用）→ 路由（只读 call_intent）
        → [会话级测试域建域，仅首轮] → M2 只读投影 ×3
        → 最终 FP M3 周期判断 → 跨能力抽取 hop → 最终 FP 统一能力接缝
        → 用户投影（防泄漏）→ 自然语言回复
```

35 个节点 / 38 条边，全部从 `uapp_start` 可达，无孤立节点、无重复 id。

### 三个必须写下来的设计裁定

**裁定一：路由责任在 Canvas，能力选择不在 Canvas。**
`uapp_route` 只做一件事——读 M1 已经算好的 `call_intent.needed_capabilities`，按 M1 给的顺序
取第一个落在六项能力内的。它不做自然语言理解（那是 M1 的 `m1_shadow`），不推导 entry
（`entry` 恒传空，由最终 FP Seam 自己的确定性充分性规则推导）。
在这里再算一次 entry，就是把「哪些算合法等价输入」复制成第二套真源。

**裁定二：`SINGLE_ACCOUNT_OPERATION` 的 `NO_PHYSICAL_ENTRY_YET` 是环境事实，不是产品禁令。**
M1 源码把 M3 标成 `BLOCKED / NO_PHYSICAL_ENTRY_YET`，理由写在注释里：M1 施工当时没有物理入口。
现在有了（最终 FP M3 `a4c3b19b…`）。**物理入口存不存在属于路由层的事实，不属于产品语义**，
所以由统一 Canvas 认定，不回头改 M1 源码——改了 H2 当场失效，也动了受保护资产。

**裁定三：业务事实来自用户与 M2，系统不预置任何品牌事实。**
M5 的运行时把仓库里的序里集夹具当作 `[FACT]` 直接注入 hop。那在取证脚本里成立，
在交给 Founder 的产品里不成立——它会让任何账号都凭空拿到序里集的商品与素材。
新画布的已登记事实只有两个来源：用户本轮上传的资料原文（走 M1 既有的
`document-extractor → m1_join` 通道），以及 M1 快照里 `evidence_bundle` 已登记的条目。
没有就是没有，由下游按缺口精确停——这正是 `UAPP-AC-06` 要的行为。

**M3 的方法参考是另一类东西，照旧注入。** `references/fashion-and-market.md`、
`six-skill-methods.md`、`operations.md` 是 M3 这个能力自带的专业方法层，与账号无关、
对谁都一样，M3 的图里只写了路径没带正文。构建时从仓库读入嵌进 `uapp_ctx`，
按 M3 契约组装 `<<REFERENCE_MANIFEST>>`。`acceptance-fixtures.md` 含期望答案，
如实标 `NOT_LOADED`，不加载。四份的 sha256 记进构建证据，由确定性检查比对仓库与图内两份载体。

### 失败按依赖边切分

- **M2 打不通**：HTTP 节点走 `default-value`（空 body + status 0），`uapp_ctx` 照实写
  「M2 未取到，因此本轮不声称任何写入已经发生」。不依赖 M2 的部分继续。
- **M3 / hop / Seam 传输失败**：走 `fail-branch` 进 `uapp_toolfail`，只影响这一支，
  不猜原因、不把传输失败说成业务结论。
- **能力返回组件级 Return**：`uapp_delivery` 从 `returns_json` 取能力自己写的 `precise_gap`，
  按缺口停，不替用户补。

---

## 三、外部副作用登记（只追加）

| 时间 | 副作用 | 标识 |
|---|---|---|
| 本轮 | 新建并发布 Dify advanced-chat 应用 | `2448e4f9-818f-4b88-9311-d18546e97da9` |
| 本轮 | M2 测试域数据（会话级 workspace/account/cycle/task） | 由运行产生，`platform=test-platform` |

保护面在建应用前后各复算一次，全部逐字节未变：

- 旧 Founder Canvas `f0b1c5f5…` graph md5 = `67b717d1365c2fb75a3b8e761b0527da`
- 旧 Seam provider `2daa2d27…` → `de0cb1e9…`，version `2026-08-27 20:36:22.268824`
- 最终 FP 八应用 + hop 适配器共 9 个 graph md5 全部未变
