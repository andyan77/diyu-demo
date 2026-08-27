# V1-M4 Rebase Delta 合同 v0.2（冻结）

> **本文件在任何实施与任何新运行之前冻结。** A2：判据事件必须早于结果事件。
> 冻结后不原地改；确需变更另建 v0.3 并说明理由。

## 0. 身份与授权

```yaml
task_id: "V1-M4-CAPABILITY-SEAMS-RUNTIME-INTEGRATION-001"   # 不变（A4：REBASE 同 task_id 建新哈希，继承旧证据）
contract_kind: "REBASE_TASK"
supersedes_contract: "M4_ENGINEERING_EXECUTION_PROMPT_v1.3.md（WHAT/WHY/BOUNDARY 继承，ACCEPTANCE 增补 AC-31）"
authority_event: "规划侧 M4_TECHNICAL_ADJUDICATION_RESPONSE_v0.1（T-01…T-08 八项裁决），经 Founder 转交"
founder_directive: "保持原 task_id；唯一一次最小 REBASE_TASK；完成技术 Delta、定向复验、冻结新 Runtime 后一次性交付十张卡"

historical_frozen_candidate: "0dcd66fd39692ed07df80e39c1f27511d9cbf283"   # 只读保留，不原地改写
new_candidate: "PENDING"                                                  # Delta 实施并复验后填入

binding_verification:            # 四项 sha256 已现场逐字符复算一致
  source_request:     "44458f3df5f512b52bab6afc6a043346e9d58774f80b3556a7dc82b9add20b02"
  evidence_contract:  "08c9c26fc213f2766bd68b36fa56d28cbc80938417588d5beb12164de0da0b54"
  fixture_pack_v0_1:  "9ac684d27acec7572934bd4f4c179212be7f196f5b7c81d9c4af6e2b48367a5a"
  final_verdicts:     "4be7eb0209f6ce8302efafd2da1b87339b894d25222865a354528208ca8663ee"
  result: "ALL_MATCH"

terminal_state_now: "IN_PROGRESS / REBASE_TASK"    # T-08：PARTIAL 禁用；不得现在判 BLOCKED
```

## 1. WHAT / WHY / BOUNDARY / ACCEPTANCE

**WHAT**：修复 `M4-FND-011`（接缝无产出完整性守卫），并按裁决补齐 AC-28 冻结取值、
新增前瞻判据 AC-31、补 v0.2 具名夹具、建立 AC-15 隔离等参对照。

**WHY**：57 次成功运行中约 18% 出现 `artifact` 或 `user_delivery` 塌陷，
且缺失被静默转为空串并按成功放行 —— 用户可能收到空交付而系统报成功。
这是 P0 交付缺陷。原验收集合 AC-01…30 全过仍可能有 18% 静默空交付，
**A4 验收充分性反查已失败**，故必须在本 Rebase 内补 AC-31。

**BOUNDARY**

```yaml
allowed_change_surface:            # 穷举，超出即越权
  - "DIYU_M4_CAPABILITY_SEAM_v1_3_TEST.yml 的六个「接缝收口｜*」code 节点"
  - "六份 DIYU_M4_TOOL_*_v1_3_TEST.yml 的产出结构节与 §7 自检追加项"
  - "DIYU_M4_TOOL_CONTENT_BRIEF_v1_3_TEST.yml 的 cta_contract 内部取值要求（T-07）"
  - "新增 V1_M4_SEAM_FIXTURE_PACK_v0.2.md（只增一个具名模板腔注入探针，T-05）"
  - "新增 AC-31 判据行（T-03，前瞻，不追溯）"
  - "新建隔离对照对象 M4 v1.3 TEST · AC15 EVAL（T-04，evaluation-only，可回滚）"

protected_baseline:                # 零改动，写前写后逐行复算
  - "九个保护应用（app_id | published workflow_id | md5(graph) 三元组）"
  - "六份源 Skill 正文与 sha256"
  - "M1 / M2 / M3 正式资产"
  - "main 分支、生产入口、真实发布平台"
  - "0dcd66f 历史冻结候选（只读保留）"
  - "AC-01…30 判据正文（AC-28 的判据不改，只补被判据指名的产出取值）"
  - "旧 Attempt 与旧裁定（不回写、不倒填、不追溯翻绿）"

non_goals:
  - "不在 M4 建第二套路由（FND-004 只出独立 M1→M4 接口 Rebase 提案）"
  - "不改采样参数（top_p / thinking / reasoning_effort / temperature）—— 放大器非根因"
  - "不改业务判断与 Skill 专业正文"
  - "不启动第二轮开放 Reviewer，不做第二个 repair cycle"
  - "不全盘重测；只复验直接、传递与未知影响项"

non_promises:
  - "不承诺 AC-21（M1 外部依赖 FND-002）在 M4 内被解除"
  - "不承诺 AC-06 合取项②（FND-004 架构缺口）在 M4 内被解除"
  - "不承诺任何现有 NOT_VERIFIED / FAIL 因本 Delta 自动晋升 PASS"
```

**ACCEPTANCE**：AC-01…30 判据正文不变 + 新增 AC-31。终态不在本合同内宣告。

## 2. 冻结 Delta 清单（穷举，实施后逐条复算）

### D-01 · 接缝收口非空/完整性守卫（T-01）

**对象**：`DIYU_M4_CAPABILITY_SEAM_v1_3_TEST.yml` 六个 `接缝收口｜{MATRIX, CAMPAIGN,
CONTENT_BRIEF, CREATIVE_SCRIPT, PRODUCTION_DIRECTOR, PUBLISHING_PACKAGING}` code 节点。

**改法**：新增 `_completeness_guard()`，替换 `tool_artifact or ""` 的静默兜底。

```text
守卫判据（冻结阈值，实施前定，不因结果调整）：
  BACKREF_MARKERS = 即上方 / 即以上 / 同上 / 上方即 / 见上文 / 内容同上 / 本区块与
  MIN_ARTIFACT_CHARS = 400          # 去空白后
  检查窗口 = 各块前 200 字

  legit_block = returns_json 中存在合法组件级 Return（含 highest_damaged_layer 与 precise_gap）

  ARTIFACT_EMPTY          : artifact 去空白为空          且 not legit_block
  ARTIFACT_BELOW_MIN      : len(artifact.strip()) < 400  且 not legit_block
  ARTIFACT_BACKREF        : artifact 前 200 字命中 BACKREF_MARKERS
  USER_DELIVERY_EMPTY     : user_delivery 去空白为空     （legit_block 时仍必须非空——用户必须被告知）
  USER_DELIVERY_BACKREF   : user_delivery 前 200 字命中 BACKREF_MARKERS
```

**命中处置**：不再静默放行。写入 `returns_json` 一条组件级 Return
（`source=SEAM_COMPLETENESS_GUARD`、`highest_damaged_layer=CAPABILITY_OUTPUT_COMPLETENESS`、
`precise_gap=` 具体命中项、`proposed_disposition=ESCALATE`、`needs_user_decision=true`），
并在 `seam_trace_json` 记 `completeness_guard: {checked:true, violations:[...]}`。

**外壳字段零新增** —— 复用既有 `returns_json` / `seam_trace_json`。
理由：新增外壳字段会命中 `AC-02` 失败条件「外壳字段总数 ≤ 统一合同 §1.1 语义组数」，
即修一个缺陷会打破一个现行 PASS。

### D-02 · Prompt 禁止两块互相回指（T-01）

**对象**：六份 `DIYU_M4_TOOL_*_v1_3_TEST.yml` 的 LLM 节点 prompt。

**改法**：在「产出结构（三块…）」节追加互引禁令；在 `§7 输出前内部检查` **追加**新条，
**原有十二条全文逐字保留、不改序、不挤掉**。

**为什么六个都改**（不是只改出问题的两个）：
塌陷实测分布 CONTENT_BRIEF 8/33（24%）、PRODUCTION_DIRECTOR 2/4（50%），
其余四个能力样本量仅 2–7 次 —— **样本不足不等于不会塌**。
根因（无互引禁令 + 无非空下限）在六份 prompt 中完全同构。

### D-03 · AC-28 冻结取值补齐（T-07）

**对象**：`DIYU_M4_TOOL_CONTENT_BRIEF_v1_3_TEST.yml` 产出结构节的 `---M4_ARTIFACT---` 块。

**改法**：要求内部 Artifact 显式写出 `cta_contract: <取值>`，取值集合取自冻结夹具 §15。
**用户可见交付仍只用自然语言，不得出现内部状态码**（否则命中 AC-13 合取项①失败条件）。

**判据不改** —— AC-28 判据正文原样保留。补的是被判据指名、而产出未落的取值。

### D-04 · 夹具包 v0.2（T-05）

**新增** `V1_M4_SEAM_FIXTURE_PACK_v0.2.md`，**只增一个**具名 `FX-M4-TEMPLATE-TONE-PROBE`。
v0.1 及其全部历史结果只读保留、不改。v0.2 运行产生新 Attempt。

### D-05 · AC-31 前瞻新增（T-03）

见 §3。**正式证据只能来自本判据冻结后的新运行**；旧运行只作缺陷发现与回归输入。

### D-06 · AC-15 隔离等参对照（T-04）

新建 `M4 v1.3 TEST · AC15 EVAL` 对照对象，A/B 分别装源 Skill 与 M4 后继 Skill，
`model / thinking / reasoning_effort / top_p / max_tokens / 输入 / 输出预算` **逐项相同**。
运行前冻结配置 hash，全部输出保留并盲评，写前写后登记 Dify 对象与回滚锚点。
**保留为 evaluation-only 对象，不删除**（避免未授权副作用），最终回执中披露。

**降级条件**：若不改保护资产与冻结运行候选就建不成公平对照，
`AC-15` 保持 `NOT_VERIFIED`，**不得降低公平口径，不得用现有不等参结果证明「不劣于」**。

## 3. AC-31 · 产出完整性与显式失败（冻结判据）

| 判据 | 取证对象 | Oracle（**通过条件**） | 失败条件 | V |
|---|---|---|---|---|
| AC-31 | 六能力代表性正式运行 + Founder 画布 | ① 每次正式运行的 `artifact` 与**适用的** `user_delivery` 均满足 §2 D-01 冻结的非空/最低完整性结构；② 两块**均不出现**对另一块的回指；③ 不满足时**必须**显式 `PARSE_FAIL` 或组件级 Return，**绝不以成功空串放行**；④ 恢复/重试保留原失败且不重复副作用 | 任一合取项不成立；或出现 `status=succeeded` 同时交付块为空/回指 | D+S |

**合取纪律**：四项全部核验通过才 `PASS`；任一 `NOT_VERIFIED` 则整条 `NOT_VERIFIED`。

**适用性说明**：合法组件级阻断（如 `FX-M4-THIN-FIELDS` 正确发 `ESCALATE` Return）时，
`artifact` 允许为空，但 `user_delivery` **仍必须非空** —— 用户必须被告知阻断。
该情形按 `APPLICABLE` 处理，不是 `NOT_APPLICABLE`。

## 4. 影响面（A3，冻结于实施前）

**规则**（引自裁决 T-01 第 5 点）：只有绑定到变化的 Prompt、收口节点、published
version/provider 和对应 Runtime 输出的 criterion/证据置 `STALE`；源 Skill、九个保护应用、
不依赖该变化的合同/静态证据继续复用。**不多算，不少算。**

```yaml
stale_count: 28        # 绑定 Runtime 输出，需定向复验
stale: [AC-02, AC-03, AC-04, AC-05, AC-06, AC-07, AC-08, AC-09, AC-10, AC-11,
        AC-12, AC-13, AC-14, AC-15, AC-16, AC-17, AC-18, AC-19, AC-20, AC-21,
        AC-22, AC-23, AC-24, AC-25, AC-26, AC-27, AC-28, AC-29]

reused_count: 2        # 仅绑定静态资产，证据不受本 Delta 影响
reused: [AC-01, AC-30]
reused_reason: "AC-01 绑合同 hash / baseline / worktree / 保护应用锚点 / 六 Skill sha256；
                AC-30 绑静态资产。均不依赖 Prompt 字节或 Runtime 输出。"

why_stale_is_broad: |
  D-02 改的是六份 Tool prompt —— 这是**共享绑定**：AC-12 的七级回指以「已发布实际
  Prompt 字节 sha256」为准，全部 Runtime 输出都产自这些 prompt。
  因此 28/30 落入影响面**不是范围扩张，是被授权改动的诚实影响**。
  这与裁决「不全盘重测」不矛盾：AC-01 / AC-30 及其静态证据继续复用，
  源 Skill sha256 与九个保护应用锚点继续复用，不重新取证。

not_stale_assets:
  - "六份源 Skill 正文与 sha256（本 Delta 不碰源 Skill）"
  - "九个保护应用绑定（写前写后复算，预期零变化；若非零即为越权，须回退）"
  - "V1_M4_SEAM_FIXTURE_PACK_v0.1 及其全部历史 Attempt（只读保留）"
  - "0dcd66f 候选及其 M4_FINAL_VERDICTS.json（只读保留为历史）"
```

## 5. 执行顺序（冻结）

```text
1. 冻结本合同 + 夹具 v0.2 + AC-31          ← 必须先于一切实施与运行（A2）
2. 实施 D-01 / D-02 / D-03                 ← 只在 §2 穷举面内
3. 发布 → 重绑 provider → 从 Dify 目标系统读回实际 published version 确认
4. 九个保护应用逐行复算零变化              ← 非零即越权，立即回退
5. 定向复验 28 项 STALE（含 AC-26 用 v0.2 新夹具、AC-28 用原高风险夹具重跑）
6. AC-31 新运行取证                        ← 判据已于第 1 步冻结
7. D-06 AC-15 隔离等参对照
8. 一次隔离只读收口核验                    ← 唯一一次，不再开第二轮
9. 冻结新候选 commit + Dify published version + 证据 hash
10. 一次性重建并交付十张 Founder 测试卡    ← 此前不让 Founder 跑任何卡
```

**第 9 步之后**：Founder 测试期间**禁止继续改代码或重新发布**。
Founder 退回若只影响特定语义则定向处理；若改变合同/授权/基线则另建版本，
**不在同一证据上移动判据**。

## 6. 预授权采样合规性（T-02）

现有 N=3 采样须逐项证明后方可认定 `ELIGIBLE_FORMAL_EVIDENCE`（**不是自动 PASS**）：

```text
[ ] N 在运行前冻结                    → 脚本常量 N=3，注释「跑之前冻结，跑完不改」
[ ] 输入/模型/参数/环境绑定            → input_sha256 断言 + binding_json
[ ] 全部样本保留                      → 12 份齐全，塌陷样本未删
[ ] 塌陷样本进入审查                  → 必须与完整样本一并向 Founder 披露
[ ] 不挑完整或满意输出                → N-30
[ ] 整体视为一个 Formal Attempt 的 N 个样本
```

**AC-05 不加采**。若 Founder 在全部样本披露下认为证据不足，
结果是 `NOT_VERIFIED(INSUFFICIENT)`，**不是失败后继续抽到满意**。

**注**：本采样产自 `0dcd66f` 候选，D-02 改 prompt 后其绑定进入 `STALE`。
是否需在新候选下重采，由第 5 步定向复验时按 A3 逐项判定并如实记录。
