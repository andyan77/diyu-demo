# V1 M4 取证判据合同 v0.1（Evidence Collection Contract）

```yaml
document_id: "V1_M4_EVIDENCE_COLLECTION_CONTRACT"
version: "v0.1"
task_id: "V1-M4-CAPABILITY-SEAMS-RUNTIME-INTEGRATION-001"
task_contract_hash: "b3ceabcbe9bcd82dae2fae84161dce0f0aadd96e395a8d6fa06a3355138331c6"
frozen_before_any_result: true
fixture_pack_ref: "decision-chain/fixtures/m4/V1_M4_SEAM_FIXTURE_PACK_v0.1.md"
unified_contract_ref: "decision-chain/docs/V1_M4_UNIFIED_CAPABILITY_CONTRACT_v0.1.md"
run_manifest_ref: "decision-chain/docs/V1_M4_IMPLEMENTATION_MANIFEST_v0.1.md"
```

> **本文件在任何正式结果产生之前冻结。**
> 看到结果之后再改判据 ⇒ 该次运行降为 `DIAGNOSTIC`（探索），不产生正式 `PASS`；
> 判据必须版本化为 `v0.2` 并**重跑**（N-29）。

---

## 1. 通则

### 1.1 探索 vs 正式

| | `DIAGNOSTIC`（探索） | `FORMAL`（正式） |
|---|---|---|
| 包含 | 侦察、诊断、变量发现、根因假设、搜索方向调整 | 每一项正式测试、对照、评审、事实确认 |
| 可否自由进行 | 是 | 否，必须先冻结本文件对应条目 |
| 可否产生 PASS | **否** | 是 |
| 记录义务 | 保留在 L3 账本 | 保留全部尝试与原始输出 |

### 1.2 每个 `PASS` 必须绑定的十项

```yaml
pass_binding:
  artifact_hash:        # 产物内容 hash
  input_ref:            # 冻结输入（fixture id）
  oracle_ref:           # 本文件的判据条目 id + 冻结时间
  model_and_params:     # 模型、provider、完整 completion_params
  skill_workflow_provider:  # 源 Skill sha256 / workflow 版本 / tool provider 绑定
  environment:          # 目标环境标识（本机 Docker Dify 1.16.1）
  timestamp:
  attempt_id:
  verifier:             # 验证主体：确定性工具 / 结构检查 / 有界判断
  raw_evidence_path:    # 原始证据落盘路径
```

**缺关键绑定 ⇒ `NOT_VERIFIED`。绑定改变或依赖未知 ⇒ `STALE`。**

**不能单独产生技术 PASS 的东西**：文件存在、导入成功、发布成功、运行历史、执行者自述、模型自评、Founder 产品接受。

### 1.3 Attempt 预算与采样纪律

- 每个代表性 criterion，**同一机制最多两次正式终局 Attempt**；第二次必须有**根因、干预、关键前提或验证路径的实质变化**，否则不计。
- 瞬时故障可重放，但**保留全部尝试**。
- **预授权采样**：预先冻结 N 个候选、全部保留、一并盲评 ⇒ 算**一次**。
- **失败后盲目重抽、只留满意输出 ⇒ 禁止**（N-30）。

### 1.4 验证主体类型

`确定性工具`（脚本/字节比对/JSON schema）｜`结构检查`（结构比对、逐项映射）｜`有界判断`（受冻结 Rubric 约束的人）。
盲式人类判断只用于 AC-15 / AC-18 的专业方法保留，其余优先用前两类。

### 1.5 状态词

结果：`PASS | FAIL | NOT_VERIFIED`（后两者可带 `INSUFFICIENT / ABSENT / NOT_CHECKED / INCONCLUSIVE`）
时效旗标：`CURRENT | STALE`
适用性：`APPLICABLE | NOT_APPLICABLE`（**运行前**由权威依据定，失败后不得追溯填写）

---

## 2. AC-01…30 正式判据

> 「Oracle」列写的是**判定规则**；「失败条件」写的是**什么算 FAIL**。
> `V` = 验证主体：`D`=确定性工具，`S`=结构检查，`H`=有界判断（含盲评）。

| ID | 判据 | 冻结输入 | Oracle（成功条件） | 失败条件 | V |
|---|---|---|---|---|---|
| AC-01 | Rebase、worktree、回滚、连续性 | Run Manifest §1–§2 | ① 合同 hash 复算 == 声明值；② `actual_baseline` == 现场远端 `main`；③ worktree 独立且创建时 clean；④ 九个保护应用的 published `workflow_id` + `graph md5` 与 Run Manifest §2.5 逐行一致；⑤ 六 Skill sha256 与 §2.3 逐行一致；⑥ 共享 root 未跟踪资产未被吸收 | 任一行不一致 | D |
| AC-02 | 统一外壳保留能力差异 | 七个能力的 `professional_payload` 实际产出 | 去掉能力名后**两两互换**：下游消费失败或产出实质变化 ⇒ 差异成立。外壳字段总数 ≤ 统一合同 §1.1 语义组数，且**无任一能力的专业结构写进外壳** | 任意两能力 payload 互换后下游仍正常消费且产出无实质变化；或外壳内出现能力专属专业结构 | S+H |
| AC-03 | 非固定上游与按需组合 | ENTRY-03/05/06/07 各一次真实 run | 每次 run 的**实际调用链**中不含未被显式编排的上游能力；M4 六个能力应用之间**零 tool 调用边** | 出现暗跑；或应用间存在互相调用边 | D |
| AC-04 | 合法等价输入 | `FX-M4-CT-USER-DIRECT` / `FX-M4-CT-M3` / `FX-M4-CT-CAMPAIGN` / `FX-M4-SCRIPT-LEGAL` / `FX-M4-REALIZATION-FINAL` | 五类输入各自按统一合同 §4.3 的**业务语义**判定为充分并正常产出；`FX-M4-THIN-FIELDS` 判 `INSUFFICIENT` | 任一合法等价输入被拒；或极薄输入被当作等价 | S |
| AC-05 | M3/Campaign 同种 Content Task | `FX-M4-CT-M3` + `FX-M4-CT-CAMPAIGN` | Brief 消费的 12 项业务核心**逐项同义**；`provenance` 不同且可追溯；**只有一条 Brief 生产链** | 出现两套任务单/两条链；或核心项因来源不同而不同 | S |
| AC-06 | Matrix 局部 Return | `FX-M4-MATRIX-INSUFFICIENT-WITH-UNRELATED` | ① Matrix 分支输出七项齐全的组件级 Return，`precise_gap` 具体；② 同轮 PP 请求**正常产出**；③ 无任何假 Matrix 内容 | 全局硬停；或无关请求被阻断；或生成假 Matrix | S |
| AC-07 | Campaign 策划与 compile 保真 | `FX-M4-CAMPAIGN-UNCONFIRMED` + `FX-M4-CAMPAIGN-CONFIRMED-PACK` | 未确认输入 ⇒ `PLANNING`；已确认决定包 ⇒ `COMPILE_CONFIRMED_DECISIONS` 且**逐条不改写**已确认决定 | 未确认输入被强制 compile；或 compile 模式改写了已确认决定 | S |
| AC-08 | Brief/CS-1/CS 接缝 | `FX-M4-CT-USER-DIRECT` + `FX-M4-REAL-TRADEOFF` + `FX-M4-ACCEPTED-DIRECTION` | ① Brief 接受五类来源；② 有真实取舍才给候选；③ 已选方向可直达脚本且不重赛 | 来源被锁死；或无取舍时凑候选；或已选方向被要求重赛 | S |
| AC-09 | CS/PD 独立与局部重跑 | `FX-M4-SCRIPT-LEGAL` + `FX-M4-LOCAL-EDIT` | ① 合法脚本直达 PD；② 局部改动后未依赖单元**不重跑**；③ `plan` 与 `manifest` 字段与语义不混用 | 直达被拒；或全量重跑；或 plan 被当 manifest | S+D |
| AC-10 | PP 直达与三状态 | `FX-M4-REALIZATION-PLAN-ONLY / MIXED / FINAL / ASSET-LEVEL-ONLY` | 四例分别推导为 `PRE / MIXED / FINAL / PRE`，且各自写出**推导依据**（manifest 在不在、每条 beat 缺口状态） | 任一例判错；或缺失被伪装成 NONE；或资产级清单被当 manifest | D+S |
| AC-11 | 条件附件 | `FX-M4-IRRELEVANT-REFERENCE` + `FX-M4-NO-PLATFORM-EVIDENCE` | 实际加载的 reference 投影 ⊆ 统一合同 §12 加载矩阵允许集；过期/未核实项保留 `NOT_VERIFIED` 且未升级主张；无关全文未加载 | 加载了矩阵之外的内容；或凭记忆补数字；或示例变成模板/事实 | D+S |
| AC-12 | 源到 Runtime 保真 | 六个 M4 后继应用的实际发布态 | 逐能力七级回指全部可解析：源 Skill sha256 → Workflow system prompt 正文 + 适配 diff → reference 最小投影 → **已发布实际 Prompt 字节 sha256** → 模型/参数/reasoning → tool provider 与父 Workflow 绑定 → Formal Attempt 实际绑定与原始输出 | 任一级断链；或自报 hash ≠ 实际字节（N-19） | D |
| AC-13 | 内部与用户交付分离 | `FX-M4-USER-VIEW` | 用户交付块**不含**统一合同 §11.3 全部禁项；内部 Artifact **含**完整专业产出与未选候选；必要选择与成立条件**未被投影掉** | 出现任一禁项；或必要选择丢失 | D+S |
| AC-14 | Return/失效/恢复/幂等 | `FX-M4-RETURN-PARSE-FAIL / REJECTED / LOCAL-EDIT / IDEMPOTENT-RECOVERY` | ① 每条 Return 形成且仅形成一种处置；② 解析失败保留原文且局部阻断；③ 拒绝有权威/事实/边界理由；④ 只失效真实依赖项；⑤ 恢复前查目标系统 | 任一条不成立；或伪装成空数组/NONE；或全链失效；或重复副作用 | D+S |
| AC-15 | 六 Skill 专业非退化 | 固定对照集（同输入/同模型/同参数/同预算） | 每项能力的**关键专业行为**在后继版本上可达（Matrix 反岗位复述与重叠对象、Campaign 主讲由事实链产生、Brief 一问题一新判断 + 证据地图、CS-1 三轴差异、CS 三区与两问表、PD 七维与并置检查、PP 三级 mode 与 `used_fact_refs` 六处覆盖）；盲评**不劣于**源版本 | 任一关键专业行为不可达；或盲评显著劣于源版本 | S+H |
| AC-16 | Runtime、Founder、远程收口 | 全部 M4 后继应用 + 远程分支 | ① 后继应用真实运行（有 run_id）；② Founder 画布可达；③ 远端分支 commit 与本地一致；④ 九个保护应用绑定**零变化** | 任一不成立 | D |
| AC-17 | F-10 目标忠实（**硬门**） | `FX-M4-GOAL-COUNTERFACTUAL-A/B` | 只改 `objective` ⇒ 内容承诺、结构、CTA/承接**实质变化**；B 不被改写成长期价值；B 未因目标是 LEADS 而自动获得高风险 CTA | B 收敛回长期价值表达；或目标自动授权高风险 CTA | H（盲评）+S |
| AC-18 | 专业方法保留且非全链硬门 | `FX-M4-SHORT-ENTRY-METHOD`（N-35/36/37） | ① 短入口仍调用或无损承接适用方法；② 不适用 Skill 被跳过；③ 必要事实/风险/质量未降；④ 无固定全链、无统一硬门 | 短入口丢失适用方法；或出现固定全链/统一硬门 | H（盲评）+S |
| AC-19 | ENTRY-01 Matrix-only | `FX-M4-MATRIX-SUFFICIENT` + `FX-M4-MATRIX-INSUFFICIENT-WITH-UNRELATED` | 独立可达（独立 run_id）；专业输出正确；局部 Return 正确；**不启动下游** | 下游被启动；或无独立 run_id | D+S |
| AC-20 | ENTRY-02 Campaign-only | `FX-M4-CAMPAIGN-*` 四例 | 独立可达；策划/compile 正确；覆盖/退出正确；Content Task 出口正确；不越界 | 任一不成立 | D+S |
| AC-21 | ENTRY-03 Direct Brief | `FX-M4-CT-USER-DIRECT` + `FX-M4-MIXED-GOALS` | 可用；不暗跑上游；单条主目标收敛；混合目标显式取舍 | 暗跑；或周期全部目标塞进单条 | D+S |
| AC-22 | ENTRY-04 Direct Tournament | `FX-M4-REAL-TRADEOFF` + `FX-M4-NO-TRADEOFF` | 复用 CS-1（系统内只有一处锦标赛路径）；候选实质不同；数量不固定；无取舍时候选数=1 | 出现第二套锦标赛；或固定数量；或凑同义候选 | D+S |
| AC-23 | ENTRY-05 Direct CS | `FX-M4-ACCEPTED-DIRECTION` | 已选方向不重赛、不强制物理 Brief、不增确认闸 | 任一不成立 | S |
| AC-24 | ENTRY-06 Direct PD | `FX-M4-SCRIPT-LEGAL` | 不跑上游；`plan`/`manifest` 正确；局部修改正确 | 任一不成立 | D+S |
| AC-25 | ENTRY-07 Direct PP | `FX-M4-REALIZATION-FINAL` + `FX-M4-ASSET-WITHDRAWN` | 不跑上游；状态由证据推导；承诺不超兑现/权限；撤回只回退依赖项 | 任一不成立 | D+S |
| AC-26 | 共同质量底线 | 正向：`FX-M4-CT-M3`；负向：模板腔注入探针 | 适用质量维度不因目标/短入口退化；模板腔、无用废话、机械复制被拦；不适用维度允许 `NOT_APPLICABLE` | 退化未被拦；或不适用维度被当硬门 | H+S |
| AC-27 | 合法演绎与局部事实阻断 | `FX-M4-DRAMATIZATION` | 合法演绎不因无真实事件被拒；无依据事实**只阻断依赖支**；创意深度与成品质量不降 | 整项拒绝；或整条降为模板 | H+S |
| AC-28 | CTA 三级接缝 | `FX-M4-CTA-THREE` | 三例分别按目标/路径/事实/权限处理；高风险未授权即拒；目标不自动授权 | 任一例处理错；或目标自动授权 | S |
| AC-29 | 三层候选裁量 | `FX-M4-REAL-TRADEOFF` + `FX-M4-NO-TRADEOFF` + `FX-M4-MIXED-GOALS` | 周期/创意/包装三层不混写；真取舍才多方案；数量不固定；可逆调整无新闸 | 三层混写；或硬编码数量；或新增确认闸 | S |
| AC-30 | 治理与定向失效 | Run Manifest + `FX-M4-PARALLEL-CHANGE` | 绑定 `-005/rev2` 与实际基线；变化只使**直接/传递/未知影响项** `STALE`；有证据不受影响的项继续复用 | 多算（使有证据不受影响的项失效）或少算（遗漏已知依赖） | D+S |

### 2.1 AC 之间的依赖与失效传播

```text
AC-01 → 全部（基线不成立则全部 STALE）
AC-12 → AC-15 / AC-19..25（保真链断则专业与入口结论 STALE）
AC-02 → AC-15
AC-04 → AC-05 / AC-08 / AC-09 / AC-10 / AC-21..25
AC-14 → AC-06 / AC-09 / AC-25
AC-16 → 全部 Runtime 类（AC-19..25、AC-10、AC-12）
```

---

## 3. N-01…50 强制负向探针

> 全部探针在结果前冻结输入、适用性、Oracle、模型/参数、样本与失败条件。
> 「输入」列引用夹具包条目；未点名者用对应 AC 的冻结输入。

| ID | 场景 | 冻结输入 | 必须观察到（PASS） | FAIL |
|---|---|---|---|---|
| N-01 | 不需 Matrix/Campaign 的直接 Brief | `FX-M4-CT-USER-DIRECT` | 调用链不含 Matrix/Campaign | 出现任一 |
| N-02 | 合法脚本直达 PD | `FX-M4-SCRIPT-LEGAL` | 不补跑 Brief/锦标赛/CS | 出现补跑 |
| N-03 | 只包装且有合法兑现 | `FX-M4-REALIZATION-FINAL` | 不补跑上游；PP 消费等价输入 | 出现补跑或拒绝等价输入 |
| N-04 | Matrix 缺事实，同轮有无关请求 | `FX-M4-MATRIX-INSUFFICIENT-WITH-UNRELATED` | 局部 Return；无关请求继续；不造假 | 全局停 / 无关被阻 / 造假 |
| N-05 | Campaign 收未确认经营任务 | `FX-M4-CAMPAIGN-UNCONFIRMED` | 保持策划身份，不强制 compile | 被强制 compile |
| N-06 | Campaign 收已确认决定包 | `FX-M4-CAMPAIGN-CONFIRMED-PACK` | compile 可用且不改写决定 | 决定被改写 |
| N-07 | M3/Campaign 夹具表达同一任务 | `FX-M4-CT-M3` + `FX-M4-CT-CAMPAIGN` | Brief 核心同义、来源可追溯、非两套链 | 核心不同 / 两套链 |
| N-08 | 未采用 M3 物理候选可见 | 共享 root `m3-account-content-operator-semantic-v1.0/` 在场 | **不读其文件/Schema，不复制判断**；产物内零引用 | 出现引用或结构模仿 |
| N-09 | 用户已选创意方向 | `FX-M4-ACCEPTED-DIRECTION` | 不机械再给固定候选 | 再给固定候选 |
| N-10 | 确有创意取舍 | `FX-M4-REAL-TRADEOFF` | 候选机制实质不同且用户可见 | 同义替换 / 用户不可见 |
| N-11 | 只改脚本局部事实句 | `FX-M4-LOCAL-EDIT` | 不重跑不受影响组件 | 全量重跑 |
| N-12 | Return 解析错误 | `FX-M4-RETURN-PARSE-FAIL` | 不伪装空数组/NONE；局部阻断并保留失败 | 伪装 / 丢失 |
| N-13 | 下游 Return 被拒 | `FX-M4-RETURN-REJECTED` | 有权威/事实/边界理由，不沉默丢失 | 无理由 / 沉默 |
| N-14 | plan 有、素材未回 | `FX-M4-REALIZATION-PLAN-ONLY` + `ASSET-LEVEL-ONLY` | 不判 FINAL，不生成超兑现承诺 | 判 FINAL / 超兑现 |
| N-15 | 部分素材兑现 | `FX-M4-REALIZATION-MIXED` | 精确 MIXED，未兑现项仍受限 | 判错 / 未兑现项被当成兑现 |
| N-16 | 素材撤回/权限失效 | `FX-M4-ASSET-WITHDRAWN` | 只回退真实依赖项和承诺 | 整条推倒 / 不回退 |
| N-17 | 无当前平台/行业证据 | `FX-M4-NO-PLATFORM-EVIDENCE` | 不声称唯一/稀缺/避同质化，不猜数字 | 出现该类声称或自造数字 |
| N-18 | 无关附件存在 | `FX-M4-IRRELEVANT-REFERENCE` | 不加载全文，不让示例变模板/事实 | 加载全文 / 示例变模板 |
| N-19 | 自报 hash 与实际 Prompt 不同 | `FX-M4-HASH-MISMATCH` | 以实际字节为准并 FAIL，不覆盖历史 | 以自报值为准 / 改写历史 |
| N-20 | 子应用发布、父 provider 指旧版 | `FX-M4-PROVIDER-STALE` | 识别并重绑后继；未重绑不得 PASS | 未识别 / 未重绑仍 PASS |
| N-21 | reasoning 改变且更快 | `FX-M4-REASONING-CHANGE` | 不以能跑完宣称专业等价 | 宣称等价 |
| N-22 | 语义事实核验失败 | `FX-M4-SEMANTIC-CHECK-FAIL` | 阻止交付，保留原 Artifact/失败输出，不删句翻绿 | 删句翻绿 / 交付放行 |
| N-23 | 用户输出 | `FX-M4-USER-VIEW` | 不泄露内部信息；必要选择不丢 | 泄露 / 选择丢失 |
| N-24 | 保存瞬时失败后恢复 | `FX-M4-IDEMPOTENT-RECOVERY` | 先查副作用，不重复提交，保留原失败 | 盲重放 / 重复副作用 |
| N-25 | 并行 M1/M2/M3 资产变化 | `FX-M4-PARALLEL-CHANGE` | 不覆盖/吸收；只使受影响接缝 STALE | 覆盖 / 全盘 STALE |
| N-26 | Reviewer 提命名/排版/偏好 | Reviewer 实际 blocker 列表 | advisory，不阻断 | 被当作阻断 |
| N-27 | M4 运行成功 | 最终回执 | 不宣称完整纵向链、运营闭环、整体增益或经营提升 | 出现该类宣称 |
| N-28 | P0 仍有授权内路径 | 终态判定 | 不提前 PARTIAL/BLOCKED/FAILED | 提前收敛 |
| N-29 | 看到失败后改 Oracle | 判据变更记录 | 原运行降探索；版本化并重跑 | 就地改判据继续算 PASS |
| N-30 | 预授权候选与失败后重抽 | Attempt 账本 | 前者全保留盲评；后者拒绝 | 只留满意输出 |
| N-31 | 同事实资源，仅改目标 | `FX-M4-GOAL-COUNTERFACTUAL-A/B` | 内容承诺、结构、CTA/承接随目标实质变化 | 无实质变化 |
| N-32 | 混合目标进单条 Brief | `FX-M4-MIXED-GOALS` | 保留周期目标；单条收敛主工作和有限贡献；冲突显式取舍 | 塞入全部目标 / 压成综合分 |
| N-33 | Campaign 旧路径收窄目标为认知变化 | `FX-M4-CAMPAIGN-GOAL-NARROWING` | 识别目标忠实风险；无权改目标时局部 Return | 静默改写 |
| N-34 | 极薄「字段齐全」直达但缺专业语义 | `FX-M4-THIN-FIELDS` | 不冒充等价输入；只追问/阻断依赖支 | 被当作等价输入 |
| N-35 | 短入口完整，适用方法来自具体 Skill | `FX-M4-SHORT-ENTRY-METHOD` | 直达仍调用或无损承接适用方法 | 方法丢失 |
| N-36 | 保护专业价值方案要求六 Skill 全参与 | 同上 | 拒绝固定全链，只调适用组件 | 接受固定全链 |
| N-37 | 短快转化不适用完整叙事 | 同上 | 不把不适用维度变硬门，必要质量仍成立 | 变硬门 / 必要质量丢失 |
| N-38 | Matrix-only 资料充分 | `FX-M4-MATRIX-SUFFICIENT` | 只返 Matrix 诊断，不启下游 | 启下游 |
| N-39 | Matrix-only 缺必要事实 | `FX-M4-MATRIX-INSUFFICIENT-WITH-UNRELATED` | 组件 Return；不造假、不全局停、不启下游 | 任一违反 |
| N-40 | Campaign-only 独立经营任务 | `FX-M4-CAMPAIGN-UNCONFIRMED` | 保持策划，不要求周期/Matrix/确认包 | 要求前置 |
| N-41 | Campaign 周期覆盖结束 | `FX-M4-CAMPAIGN-OVERRIDE-END` | 返回仍有效基线或冲突/缺口；M4 不发明 M3 恢复 | 发明恢复逻辑 / 静默选上游 |
| N-42 | 明确选题直达 Brief | `FX-M4-CT-USER-DIRECT` | 不跑 Matrix/Campaign/M3；保留目标/事实/权限 | 出现补跑 / 丢失 |
| N-43 | 直接锦标赛有真实取舍 | `FX-M4-REAL-TRADEOFF` | 复用 CS-1；实质差异、数量不固定、无第二套 | 第二套 / 固定数量 |
| N-44 | 直接 CS 已选方向 | `FX-M4-ACCEPTED-DIRECTION` | 不重赛、不强制 Brief、不索要口令 | 任一违反 |
| N-45 | 直接 PD 有合法脚本 | `FX-M4-SCRIPT-LEGAL` | 不跑上游；正确 plan/manifest | 任一违反 |
| N-46 | 直接 PP 有成片/beat 兑现 | `FX-M4-REALIZATION-FINAL` | 不跑上游；推导状态；不超兑现承诺 | 任一违反 |
| N-47 | 合法演绎、无真实经营事件 | `FX-M4-DRAMATIZATION` | 不整项拒绝；区分演绎与事实且保持质量 | 整项拒绝 / 质量塌陷 |
| N-48 | 演绎稿含无依据品牌事实/结果暗示 | `FX-M4-DRAMATIZATION`（注入变体） | 只阻断/改写事实依赖支，不降为模板 | 整条降为模板 / 放行 |
| N-49 | 低风险、经营承接、高风险 CTA 各一例 | `FX-M4-CTA-THREE` | 按目标/路径/事实/权限分别处理；目标不自动授权 | 任一例处理错 |
| N-50 | 周期/创意/包装均可有候选 | `FX-M4-REAL-TRADEOFF` + `FX-M4-NO-TRADEOFF` + `FX-M4-MIXED-GOALS` | 三层不混；真取舍才多方案；数量不固定；无多余确认 | 混写 / 硬编码 / 新增闸 |

### 3.1 公平对照纪律（适用于 N-21 / N-31 / AC-15 / AC-17 / AC-18）

**不得**用不同模型、参数、事实、权限或输出预算制造胜利。
对照两侧必须共享：模型 + provider + 完整 `completion_params` + 输入事实集 + 权限集 + 输出预算 + 冻结 Oracle。
预授权多候选**必须全部保存并盲评**。

---

## 4. 受影响回归清单（§10.1 承接）

**必跑（定向复验）**：AC-02 / AC-03 / AC-04 / AC-08 / AC-11 / AC-12 / AC-13 / AC-15 / AC-16、F-10 双向、七入口、Campaign 目标忠实、Matrix Return、CS-1 差异、PP 确定性状态与事实核验、Brief 主目标、CTA、直接 CS/PD/PP、用户投影、完整保真链、M1/M2/M3 版本兼容。

**必跑一次**：一条**完整模块级 Runtime 主故事** + 六 Skill 保护门禁。

**不跑**：六 Skill / Workflow / reference 若刷新证明未变（Run Manifest §2.3 已证零漂移）⇒ 继续作保护基线，**不重写 Skill、不重建 Workflow、不重跑全部历史测试**。

**不得被预算排除**：已证明的专业退化、权限/安全破坏、数据完整性问题、保护资产变化。

---

## 5. 收敛回归夹具（SBC-RF）

> 用**现行规则**解释并运行，**不升格为新规则**。

| ID | 规则 | 本任务的执行方式 |
|---|---|---|
| `SBC-RF-01` | 流程性伪阻断只能 advisory | Reviewer 提出的命名、排版、「可更优雅」、无验收映射的重构、无基线能力下降的偏好实现、要求新证明但无冻结判据映射 ⇒ **记录为 advisory，不阻断、不升级、不全量重跑、不重新设计**（N-26） |
| `SBC-RF-02` | 证据身份不匹配 ⇒ 受影响 criterion `NOT_VERIFIED + STALE`，定向复验 | 夹具、Oracle、绑定或基线变化时，**只**把真实依赖它的 criterion 置 `NOT_VERIFIED + STALE`；不受影响证据**继续复用**；**禁止全盘清零** |
| `SBC-RF-03` | DONE 后出现新标准不重开已 DONE 任务 | 达到 DONE 后只允许记录、已授权收口与披露；改变结论或合同前提的新异常**登记为新任务候选**，不在 M4 内继续研究 |
| `SBC-RF-04` | 用户症状/目标 ≠ 已选择宪法升版或平台重建 | 先用当前规则与**最小有效层**处理；执行者与 Reviewer 必须**披露专业异议**，不得以迎合 Founder 为由过度工程化 |

**这四条当前的跨模型行为回归不能因为写进本文件就自称已验证**；执行阶段按冻结判据保留实际运行/审查证据。

---

## 6. 强制停止条件（只停受影响分支）

```text
未获准确 v1.3 独立施工授权
需要扩大权限或改变产品语义
必须猜 M3 物理结构 / 复制 M3 判断
必须改 M1/M2/M3 职责、数据库、生产或保护资产
Dify 无可靠回滚
源/Runtime/参数/provider 冲突无法解释且继续会覆盖未知专业价值
真实 Runtime 不可用
合理授权路径已穷尽仍不能满足 F-10 / 专业保真
任务分支无法安全推送
P0 必须越出白名单
```

**不是治理阻塞**：普通测试失败、工具报错、依赖冲突、实现复杂、质量不足、需要换路线。记录失败，换**有机制差异**的路线继续。

---

## 7. 终态判定顺序

```text
INVALID → DONE → PARTIAL → BLOCKED → FAILED
```

本任务**无 P1，`PARTIAL` 不可用**。

`DONE` 需要：AC-01…30 全部 `PASS/CURRENT` + 适用 completion checks + N-01…50 + 受影响回归通过 + Review 收口 + 远程一致 + Dify 副作用受控 + Founder 产品接受 + 无越界。

- **Founder 接受不替代技术 PASS；技术 PASS 不替代 Founder 接受。**
- 授权内合理路径**被证据排除**且无治理阻塞 ⇒ `FAILED`，不是 `BLOCKED`。
- 达到 DONE **立即停止**。

---

## 8. 更正说明 · M4-BLK-002 解锁后新增的负向探针（2026-08-26）

> **不覆盖原文**：§1—§7 一字未改。本节是按项目文档纪律「冻结合同加更正说明」追加的，
> 只新增探针行，不修改任何既有 AC / N 判据。

### 8.1 权威事件

| 项 | 值 |
|---|---|
| 事件 | Founder 授权拆除 M1 已落地 `v1_state` 中的两处线性锁（`UPSTREAM_OF`、`NEXT_SKILL`），按最佳工程实践执行 |
| 日期 | 2026-08-26 |
| 阻断编号 | `M4-BLK-002`（登记于验收索引 §2A） |
| 合同影响 | **无 REBASE**。拆锁本就在 M4 施工范围内（Phase 0 前言 §五：「M4 负责把现有 Skill／DSL／路由的全局终止改造成组件级或分支级返回」），`task_contract_hash` 不变 |

### 8.2 新增探针 N-51…N-56

**判据来源先于结果，A2 第 3 项成立。** 这六行新增的是**测量手段**，不是新判据。
它们检验的判据早已冻结在：

- 统一能力合同 §2：`REQUIRED_ALWAYS: []` / `DEFAULT_CALL: []` / `FIXED_ORDER: false` / `FULL_CHAIN_GATE: false`
- `CLAUDE.md` §3：「Campaign 既不默认调用，也不默认绕过」「不得为进入某组件暗中补跑前置组件」

| 编号 | 探针 | 冻结判据（oracle） | 结果 |
|---|---|---|---|
| N-51 | 上游产物一份都没有时，五个能力在画布路径上逐个直达 | 统一能力合同 §2 `REQUIRED_ALWAYS: []` | PASS ×5 |
| N-52 | 解锁前后**差分**：与 M1 原文同输入对跑 15 组，行为差异必须恰好等于 `EXECUTION_BLOCKED:UPSTREAM_*` → `EXECUTION_AUTHORIZED:*`，无第二种差异；完全没有任务时两版同时拦下；`MATRIX`（本就无上游锁的对照组）逐项一致 | M1 已发布上线的自身行为（预先存在，非本轮产生） | PASS ×3 |
| N-53 | 接受矩阵后说「继续」不再自动调用 Campaign | 统一能力合同 §2 `DEFAULT_CALL: []` | PASS |
| N-54 | 接受仍然生效，且落到既有回执分支而不是死路 | A5：解锁不得使既有能力消失 | PASS |
| N-55 | 撤销接受时的级联 STALE 未被误删（`DOWNSTREAM_OF_SLOT` 零改动） | A3：无法判断依赖者置 STALE，清空即少算 | PASS |
| N-56 | `v1_state` 相对 M1 原文的行级差异恰好 6 行、恰好属于两处定义；`v1_shadow` 逐字节零改动 | 本次授权范围本身 | PASS ×2 |

### 8.3 N-52 判据修正登记（如实记录，不掩盖）

N-52 初版把「用户授权门」写成「`confirmed_task` 为空就一定不执行」，跑出 3 条 `FAIL`。

定向复核结论：**是探针判据写错，不是补丁削弱了门。** M1 原文本来就允许在用户自己那句话里
确认任务（`notes` 里的 `TASK_CONFIRMED_BY_EXPLICIT_EXECUTION_REQUEST`），打补丁前后完全一致；
「`confirmed_task` 为空」不等于「没有任务」。

处置：换成**差分判据**——同输入对跑 M1 原文与解锁后两份 `v1_state`，
要求差异集恰好等于被授权拆掉的那把锁。新判据的 oracle 是 M1 自己已上线的行为，
**早于本轮全部结果**，且比原判据更强（不依赖执行侧对 M1 语义的猜测）。
按 §1.1，这次修正**不产生**对 N-52 原判据的追溯性 PASS，产生的是新判据下的 PASS。

### 8.4 探针执行环境说明

M1 已落地的 `v1_state` 正文里没有 `import json` 却直接使用 `json.dumps` —— 这是 M1 原文的
既有写法，在真实 Dify 代码节点沙箱里可运行（该 Chatflow 已发布且 Founder 已验收）。
本地探针不在 Dify 沙箱内，`load_node_code(..., preload={"json": json})` 把同名模块补进命名空间，
**这是复现运行环境，不是修改被测代码**——被执行的仍是将要导入 Dify 的那一份字节。
