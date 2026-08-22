# 内容生产三份 Skill · Phase 1 启动上下文包 context_pack

```yaml
package_id: CONTENT-PRODUCTION-3SKILL-CONTEXT-PACK
status: READY_FOR_PHASE1_ARCHITECTURE_DESIGN
revision: 1.0
revised_on: 2026-08-22
covers_skills:
  - creative-script-architect
  - production-director
  - publishing-packaging-architect
production_model_status: PRODUCTION_MODEL_UNCONFIRMED
skill_host: Dify
architecture_requirement: MODEL_AGNOSTIC
```

---

# 0. AUTHORITY_MODEL

三份制度文件按**领域分权**，不是全局覆盖。任何一份在自己的领域内最高权威，
在他人领域内不得重新定义。

## 0.1 领域分权表

| 领域 | 最高权威 |
|---|---|
| 三份 Skill 应具备什么专业能力 | 《构建规范 v1.0》 |
| `Observe → Generate → Eliminate → Select → Deepen → Check → Return/Degrade` 决策循环 | 《构建规范 v1.0》 |
| Creative Family 的专业定义 | 《构建规范 v1.0》 |
| 三份 Skill 职责边界 | 《构建规范 v1.0》 |
| 纵向继承原则 | 《构建规范 v1.0》 |
| 专业知识如何编译 | 《构建规范 v1.0》 |
| SKILL.md / references / scripts / Runtime Input 的知识路由 | 《构建规范 v1.0》 |
| 规则冲突优先级 | 《构建规范 v1.0》 |
| Skill 构建完成定义 | 《构建规范 v1.0》 |
| Hard Gate | 《验收标准 v1.0》 |
| Layer 0—4 验收结构 | 《验收标准 v1.0》 |
| 专业评分与分数门槛 | 《验收标准 v1.0》 |
| Skill / No-Skill Lift | 《验收标准 v1.0》 |
| 泛化覆盖 | 《验收标准 v1.0》 |
| 多模型一致性 | 《验收标准 v1.0》 |
| Dify / 生产环境测试 | 《验收标准 v1.0》 |
| 全链测试 | 《验收标准 v1.0》 |
| 最终 ACCEPT / REJECT 条件 | 《验收标准 v1.0》 |
| 当前声明的产品服务范围（六轴） | 本包 |
| 运行时输入语义 | 本包 |
| Production Profile 当前字段候选 | 本包 |
| Content Origin Mode | 本包 |
| 项目统一字段命名 | 本包 |
| 当前运行环境事实 | 本包 |
| 上下游已有业务合同与技术约束 | 本包 |
| 脱敏 Fixture / 示例格式 | 本包 |

## 0.2 两条边界

1. **本包不得重新定义《构建规范》的专业方法**，也不得重新定义《验收标准》的合格门槛。
2. **《验收标准》不得反向变成 Skill 运行时逐项评分 Prompt。**
   它用于验收 Skill，不用于每条内容运行时自评。

## 0.3 冲突处理

1. 先按 0.1 的领域权威裁决；
2. **不允许静默融合两个不同定义**；
3. 现有材料无法裁决的，显式标记 `FOUNDER_DECISION_REQUIRED`；
4. **未裁决内容不得伪装成已冻结事实。**

## 0.4 对应文件

| 简称 | 仓库实际文件名 |
|---|---|
| 《构建规范 v1.0》 | `内容生产三份 Skill 构建规范 v1.0.md` |
| 《验收标准 v1.0》 | `内容生产三份 Skill 验收标准 v1.0.md` |
| 本包 | `context_pack.md` |

---

# 0.5 PHASE1_USAGE_CONTRACT

**本包与《构建规范 v1.0》共同提供给 GPT / Claude 执行 Phase 1。**
《验收标准 v1.0》可同时提供，用于保证设计出来的能力将来可被测试；但：

> **Phase 1 不执行正式验收，也不得为了通过评分表把 Skill 设计成检查表。**

## Phase 1 的产出

1. `Cross-Skill Architecture Proposal`
2. `Creative Script Design Package`
3. `Production Director Design Package`
4. `Publishing & Packaging Design Package`

## Phase 1 不得生成

`SKILL.md`、`references/`、`scripts/`、三份 Skill 的实际方案、Dify DSL / Workflow。

## 每份 Design Package 至少覆盖

```text
Mission
Scope
Non-Scope
Professional Decision Map
Observe → Generate → Eliminate → Select → Deepen → Check → Return/Degrade
Inputs
Outputs
Cross-Skill Contract
Inherited Fields
Conflict Resolution
Return / Hold / Degrade
Knowledge Routing
Candidate Compilation Routes
Testable Capability Hypotheses
Founder Decisions Required
```

## 权限边界

Phase 1 模型对第 7 节每一项**必须提出建议方案和理由**，
但**不得自行宣布 Founder 已冻结**。最终冻结权限属于下一阶段的人工 Architecture Freeze。

---

# 1. 六轴服务范围声明

> 本节是三份 Skill 服务范围的权威定义。轴名与《验收标准》Layer 3H 的六轴一一对应。

| 本包轴名 | 验收标准轴名 |
|---|---|
| 行业 / 赛道 | Subject Domain |
| 内容形态 | Delivery Form |
| 素材来源 | Content Origin |
| 资源档 | Resource Tier |
| 服务对象 | Service Object |
| 平台 | Platform |

## 1.1 轴一：行业 / 赛道（Subject Domain）

| 轴值 | 包含范围 | 状态 |
|---|---|---|
| 服装 | 女装、男装、童装、鞋包配饰 | 已声明 |
| 美妆日化 | 护肤、彩妆、个护清洁、家清 | 已声明 |
| 餐饮 | 堂食门店、烘焙茶饮、预制菜与食品零售 | 已声明 |
| 兴趣赛道 | 运动健身、宠物、手作、旅行户外、家居生活、收藏与二次元 | 已声明 |
| 知识付费 | 职业技能、考试培训、认知成长、企业内训 | 已声明 |
| 本地生活服务 | 美业、口腔齿科、健身房、亲子教育、维修与家政 | 补充 |
| 家居家装 | 建材、家具、软装、装修服务 | 补充 |
| 母婴 | 孕产、婴童用品、育儿服务 | 补充 |
| 3C 与数码配件 | 消费电子、周边配件 | 补充 |
| 健康营养 | 保健食品、功能性食品、健康管理服务 | 补充 |
| B2B 与专业服务 | 供应链、企业软件、财税法咨询 | 补充 |

### 1.1.1 必须观察的三类行业差异

设计三份 Skill 时，**至少必须观察**以下三类差异：

1. 谁能确认事实；
2. 什么构成有效 Evidence；
3. 用户下一步实际可以被承接到哪里。

### 1.1.2 允许形成 `CONDITIONAL_DOMAIN_REFERENCE`

三类之外，如果某行业确实存在下列任一情况，允许形成条件化的领域参考：

* 独特生产约束；
* 独特演示方式；
* 独特 Evidence Obligation；
* 独特人物权威；
* 独特权属问题；
* 独特内容实现方式。

**约束**：`CONDITIONAL_DOMAIN_REFERENCE` 进入 `references/` 条件加载层，
**不得升格为所有行业的稳定规则**，也不得写入 `SKILL.md` 稳定内核。

## 1.2 轴二：内容形态（Delivery Form）

八个已声明轴值分属两类，两类可自由交叉组合。

| 分类 | 轴值 | 说明 | 状态 |
|---|---|---|---|
| 表现形式 | 口播 | 出镜人对着镜头把判断说出来 | 已声明 |
| 表现形式 | 演示试穿 | 通用形态为**实物或服务使用演示**；服装表现为试穿，餐饮为试吃，知识付费为试听 | 已声明 |
| 表现形式 | vlog | 跟随真实过程记录，时间线驱动 | 已声明 |
| 表现形式 | 对话访谈 | 两人及以上问答，判断在交锋中产生 | 已声明 |
| 表现形式 | 图文 | 图片 + 正文，无视频成片 | 已声明 |
| 题材类型 | 企业叙事 | 组织自身的选择、取舍与经营判断 | 已声明 |
| 题材类型 | 职场成长 | 个人在工作中的方法、判断与进阶 | 已声明 |
| 题材类型 | 生活类题材 | 家庭、日常、消费与生活方式 | 已声明 |
| 表现形式 | 教程演示 | 步骤化教学，结果可复现 | 补充 |
| 表现形式 | 开箱评测 | 拆解与横向比较 | 补充 |
| 表现形式 | 街头采访 | 随机对象采集真实反应 | 补充 |
| 表现形式 | 答疑合集 | 集中回答多个真实问题 | 补充 |

## 1.3 轴三：素材来源（Content Origin Mode）

字段：`content_origin_mode`

| 轴值 | 含义（大白话） | 关键约束 | 状态 |
|---|---|---|---|
| 现拍 | 为这条内容专门去拍，现场事件真实发生 | 拍摄前必须确认出镜人与事实确认人到位 | 已声明 |
| 已有素材剪辑 | 用已经存在的照片、录像、录音重新组织 | 必须先确认素材权属与可用范围；**不得因缺镜头而默认改成现拍** | 已声明 |
| 访谈提取 | 从一段真实对话里提取判断 | 提取不得改写受访人原意；引用需保留来源 | 已声明 |
| 评论回应 | 回应真实提出过的问题 | 原始问题必须真实存在且可追溯；不得虚构提问 | 已声明 |
| 脚本先行 | 先定表达再组织画面 | **不是默认模式** | 补充 |
| 视觉先行 | 先有一个画面或瞬间，再决定说什么 | 表达不得超出该画面能支撑的范围 | 补充 |
| 外部参考改编 | 参考公开可用素材再自制 | 只可参考方法，不得搬运他人素材与他人亲历 | 补充 |

**两条纪律**：

1. **未声明来源模式时，不得默认按「脚本先行」处理。**
   默认写稿会把「本来已有素材、只需剪辑」的任务错误地变成一次新拍摄。
   未声明时按 `NEED_ONE_RESOURCE` 处理并向人询问。
2. **采集类模式必须先回素材，再进入编辑类模式。**
   现拍 / 访谈提取 / 视觉先行属采集类；素材没回来之前，
   不得先产出依赖该素材的成品表达。

## 1.4 轴四：资源档（Resource Tier）

档位由**人声明**，系统不得从行业或品牌规模推断填上去。

| 轴值 | 典型配置 | 能做 | 明确做不到 | 状态 |
|---|---|---|---|---|
| 单人手机 | 1 人，手机，自然光，无收音设备 | 口播、图文、单机位演示、简单 vlog | 多机位、复杂调度、同期多人收音 | 已声明 |
| 小团队 | 2—4 人，手机或微单，补光、领夹麦 | 对话访谈、多场景、基础剪辑包装 | 大场地、复杂灯光、专业调色 | 已声明 |
| 有制作班底 | 5 人以上，专业设备、专职后期 | 分工拍摄、复杂调度、成套包装 | —— | 已声明 |
| 零拍摄档 | 0 人到场，只用已有素材与图文 | 已有素材剪辑、图文、评论回应 | 任何需要新拍的内容 | 补充 |
| 外部合作档 | 拍摄或后期外包 | 视外包范围而定 | 外包未确认交付期前不得承诺发布时间 | 补充 |

## 1.5 轴五：服务对象（Service Object）

不同服务对象的真正差别在**授权链**——谁能确认事实、谁能代表组织说话、谁承担对外承诺。

| 轴值 | 事实确认人 | 可代表谁说话 | 特别约束 | 状态 |
|---|---|---|---|---|
| 个人博主 | 本人 | 只代表自己 | 不得以专家或机构口吻作专业结论 | 已声明 |
| 小团队 | 团队内明确分工人 | 团队 | 成员各自经历不得互相挪用 | 已声明 |
| 企业 | 岗位负责人 | 企业 | 对外政策、时效、承诺必须已确认 | 已声明 |
| 多品牌集团 | 各品牌各自负责人 | 单个品牌，**不自动跨品牌** | 跨品牌引用需保留原品牌来源与责任 | 已声明 |
| 个体工商户 | 经营者本人 | 自己的店 | 不得使用其不具备的资质与服务能力表述 | 已声明 |
| 原创 IP 版权方 | 版权方指定人 | IP 本体 | 授权范围、期限、可改编程度必须写明 | 已声明 |
| 创始人个人 IP（含家庭生活） | 创始人本人 | 本人 + 有限代表企业 | **家庭成员出镜需单独授权**；家庭内容与企业承诺必须可区分 | 已声明 |
| 代运营服务商 | 委托方指定人，**不是服务商** | 委托方 | 服务商不得自行确认委托方事实 | 补充 |

## 1.6 轴六：平台（Platform）

**必须区分两个概念，它们不是冲突。**

### A. Supported Platform Scope（能力覆盖范围）

Skill 产品声明必须能够适配：

| 轴值 | 状态 |
|---|---|
| 抖音 | 已声明 |
| 视频号 | 已声明 |
| 小红书 | 已声明 |

这是**产品能力范围**，属于验收要覆盖的对象。

### B. Runtime Selected Platform（运行时锁定平台）

字段：`runtime_selected_platform`

* 每个具体内容单元的实际发布平台，**必须由人或合法上游输入锁定**；
* **Skill 不得自行选择平台**；
* 未锁定时取值：`PLATFORM_UNCONFIRMED`。

> **「三平台属于支持范围」与「具体任务的平台尚未锁定」不是冲突。**
> 前者是产品能力声明，后者是单次运行的输入状态。

### C. 平台知识约束

* 本包**不预填任何平台的算法机制、推荐逻辑、时长阈值或规则细节**；
* 带日期的平台资料进入 `DATED_REFERENCE`，不进入稳定内核；
* 平台适配只输出**需要分别决定哪些维度**（见 4.D），取值由人在锁定后填入。

## 1.7 六轴之外的行为

**不采用「六轴之外一律拒绝」。** 统一规则如下：

| 情形 | 处理 |
|---|---|
| 六轴之内 | 属于 v1.0 **必须通过验收的正式支持范围** |
| 六轴之外 | 不属于 v1.0 已验证支持范围；**Skill 不得声称已经验证** |
| 六轴之外但稳定内核理论上可处理 | 输出 `OUTSIDE_VALIDATED_SCOPE`，说明未验证点，并要求额外验证 |

**红线**：不得为了处理新领域，把行业特例偷偷写入稳定核心。
新领域的特殊知识只能进入 `CONDITIONAL_DOMAIN_REFERENCE`。

---

# 2. Production Profile

**定位**：三份 Skill 的**共享前置条件**，不是第四份 Skill，本身不产生任何内容判断。

本节分为两部分，**性质不同**：
2.A 是**冻结语义要求**，Phase 1 不得改；
2.B 是**候选字段 Schema**，Phase 1 可以改，但必须满足 2.A。

## 2.A FROZEN_SEMANTIC_REQUIREMENTS（冻结语义要求）

### A1. 五种模式必须相互区分

| 语义 | 含义（大白话） |
|---|---|
| Requested | 用户希望怎么做 |
| Available | 现在真实能调动的人、设备、时间、场地、素材 |
| Minimum Viable | 最低能跑起来的做法 |
| Recommended | 系统建议的做法（**建议，不是裁决**） |
| Accepted | 用户最终接受的做法 |

**五者不得合并、不得省略、不得互相替代。**

### A2. 必须覆盖的十二类生产条件

```text
People            人员
On-camera people  出镜人员
Assets            可用素材
Time              拍摄时间
Equipment         设备
Location          场地
Budget            预算级别
Postproduction    后期能力
Deadline          截止时间
Rights/Permission 素材权属与使用权限
Quality Expectation 质量要求
Downgrade Path    可接受降级路径
```

任何候选 Schema 都必须能表达这十二类，**缺一即不合格**。

### A3. 四条冻结原则

1. **未声明 ≠ 缺少。**
   未声明按 `NEED_ONE_RESOURCE` 处理并向人询问，
   不得默认判为不可执行，也不得凭行业惯例推断一个值填上去。
2. **Accepted 只能由人确认。** 系统可以给建议，把证据折算成结论必须由人拍板。
3. **资源改变必须能够实质改变方案。**
   Production Profile 变了而方案不变，等于该字段没有生效。
4. **降级必须记录牺牲了什么、承诺随之发生什么变化。**

## 2.B CANDIDATE_SCHEMA_FOR_PHASE1（候选字段 Schema）

```yaml
schema_status: CANDIDATE_SCHEMA_FOR_PHASE1
```

以下具体 JSON key、object 结构与枚举**不是冻结字段**。
Phase 1 可以保留 / 精简 / 拆分 / 合并，但每次修改必须：

1. 保持 2.A 全部冻结语义；
2. 给出**字段 Delta**（增了什么、删了什么、改了什么、为什么）；
3. 不得造成下游语义缺失。

### B1. 模式字段

| 字段名 | 类型 | 含义 | 示例值 |
|---|---|---|---|
| `requested_mode` | string | 用户希望怎么做 | `"想拍一条门店实拍的对话访谈"` |
| `available_mode` | string | 真实能调动什么 | `"只有周三下午 2 小时，1 个人 + 手机，门店营业中"` |
| `minimum_viable_mode` | string | 最低能跑起来的做法 | `"单人手机口播 + 已有货架照片"` |
| `recommended_mode` | string | 系统建议 | `"单机位口播，访谈延到下周有第二人时再拍"` |
| `accepted_mode` | string | 人最终接受 | `"接受单机位口播版本"` |

### B2. 资源字段

| 字段名 | 类型 | 对应冻结语义 | 示例值 |
|---|---|---|---|
| `people` | object | People | `{"total": 2, "roles": {"拍摄": 1, "出镜": 1, "后期": "同拍摄人"}}` |
| `on_camera_people` | array\<object\> | On-camera people | `[{"code": "R1", "real_role": "选品负责人", "authorized": "YES", "identity_disclosure_required": "YES"}]` |
| `available_assets` | array\<object\> | Assets | `[{"asset_id": "A-001", "type": "照片", "count": 12, "shot_on": "2026-08-15", "usable": "YES"}]` |
| `shooting_time` | object | Time | `{"windows": ["2026-08-26 14:00-16:00"], "total_hours": 2, "declared": "YES"}` |
| `equipment` | array\<string\> | Equipment | `["手机", "三脚架", "领夹麦"]` |
| `location` | object | Location | `{"places": ["门店营业区"], "constraints": ["营业中不可清场"], "permission": "内部场地"}` |
| `budget_band` | enum | Budget | `NONE` / `LOW` / `MEDIUM` / `HIGH` |
| `postproduction_capacity` | object | Postproduction | `{"editor": "同拍摄人", "skills": ["粗剪", "自动字幕"], "not_available": ["调色"], "turnaround_days": 2}` |
| `deadline` | object | Deadline | `{"date": "2026-08-30", "hard": "YES", "reason": "上新首周"}` |
| `asset_rights` | object | Rights/Permission | `{"owner": "委托方", "scope": ["自有账号发布"], "third_party_faces": "NO", "music_licensed": "UNKNOWN"}` |
| `quality_expectation` | enum | Quality Expectation | `ROUGH_OK` / `STANDARD` / `POLISHED` |
| `acceptable_downgrade_path` | array\<string\> | Downgrade Path | `["减少镜头数量", "改单机位", "改图文", "延期一周"]` |

### B3. 判定字段

| 字段名 | 类型 | 说明 |
|---|---|---|
| `production_feasibility` | enum | 见 3.5 B 作用域 |
| `feasibility_reason` | string | 用大白话说明依据 |
| `missing_resource` | string\|null | 仅 `NEED_ONE_RESOURCE` 时填，**只列区分力最高的一项** |
| `downgrade_applied` | array\<object\> | 削减了什么、承诺与证据强度是否随之变化 |
| `undeclared_fields` | array\<string\> | 哪些字段用户尚未声明（不等于缺少） |

## 2.C 降级顺序（冻结）

```text
删除 → 降级 → 改题 → 延期或不发
```

* **删除**：先去掉无法由事实负责人确认的细节与结论；
* **降级**：把表达收窄到现有证据真正支持的范围；
* **改题**：把题目改到现有事实能完整回答的位置；
* **延期或不发**：以上都不成立时取消这一条。

生产层降级**只削减覆盖面、数量与制作复杂度**，不削减事实确认、判断完整性与观众价值。
「已经投入拍摄」「账号需要保持活跃」「计划已经写好」都**不构成必须发布的理由**。

---

# 3. 统一术语表

**使用方式**：左列是唯一用词，三份 Skill 的字段名、提示词、输出正文一律用它；
「禁用同义词」列出的词不得作为该概念的替代名称出现。

## 3.1 核心术语

| 唯一用词 | 字段名 | 定义 | 禁用同义词 |
|---|---|---|---|
| **开场** | `opening` | 内容最先被用户感知的表达单元 | 抓手、引子 |
| **开场承诺** | `opening_promise` | 开场向用户建立的、正文需要兑现的继续消费理由 | —— |
| **内容承诺** | `content_promise` | 内容向用户建立的、正文必须兑现的预期。原则：**包装承诺 ≤ 正文兑现 ≤ 可证明事实与真实素材能力** | 卖点、主张、核心信息、价值主张 |
| **落点** | `landing_point` | 内容结束时观众必须带走的那一个判断 | 结尾、收尾、升华、点题 |
| **观众变化** | `audience_shift` | 观众消费内容前后应发生的主要认知、判断、情绪或行动准备变化 | 用户变化、受众转变、心智改变 |
| **张力** | `tension` | 见 3.2 | 见 3.2 |
| **创意家族** | `creative_family` | 见 3.3 | 创意方向、创意角度、大创意 |
| **创意变体** | `creative_variant` | 见 3.3 | 小创意、版本、改写 |
| **叙事发动机** | `narrative_engine` | 正文依靠什么推进：问题、任务、比较、过程、发现、人物关系、决策、变化 | 主线、驱动力 |
| **证据** | `evidence` | 使一个内容判断、变化、结果或承诺可信的事实、原话、行动、画面、过程、对比或可核实材料 | 依据、数据支撑 |
| **镜头** | `shot` | 一次连续拍摄的单位，**可编号、可计划、可清点**。「画面」只作为镜头内部的描述项 `visual_content`，不得单独作为可编号单位 | 分镜、镜次、cut |
| **字幕** | `caption` | 把**说出来的话**逐句转成的文字 | 台词条、对白字 |
| **屏幕文字** | `screen_text` | **没有人说出口**、只出现在画面上的补充文字 | 花字、贴纸字、字卡 |
| **旁白** | `voiceover` | 声音不来自画面里当下这个人。出镜人对着镜头讲话叫**口播**，不叫旁白 | 独白、画外音、OS、VO、解说 |
| **制作条件（Production Profile）** | `production_profile` | 决定方案实际可执行性的生产条件集合 | 资源包、产能表、制作能力 |

### 3.1.1 关于 Hook

> **Hook 只作为行业通俗叫法。制度字段与正式合同统一使用 `opening` / `opening_promise`。**

`Hook`、`钩子` 不得作为正式字段名出现。正文中出现 `Hook` 时，
必须能明确指向 `opening` 或 `opening_promise` 之一，不得含义不清地并存。

### 3.1.2 关于字幕与屏幕文字

两者**不合并**。字幕出错是转写错误；屏幕文字出错是新增了没人说过的主张——
后者会凭空造出一条无人负责的对外承诺。二者各有唯一用词，不得互相替代。

## 3.2 张力 `tension`

> **张力是推动用户继续消费内容的「尚未完成状态」。**

可以来自：

```text
未解决的问题 · 真实取舍 · 任务 · 比较 · 变化 · 过程
发现 · 人物关系 · 风险 · 预期差 · 信息差 · 尚未兑现的结果
```

张力**不等于**：争吵、高刺激、戏剧冲突、固定悬念句、固定秒点。

**允许任务判断**：当前内容不需要强张力，而主要依靠
`Utility` / `Identity` / `Aesthetic` / `Humor` / `Information Value`
等继续消费理由——但必须存在**某种**合理的继续消费理由。

**不得为了证明 Skill 有创意而强行制造冲突。**

> 「悬念」是一种**具体叙事机制**，可以正常使用；
> 它不再作为「张力」的禁用同义词处理。被禁的只是「固定悬念句」这类模板化写法。

## 3.3 创意家族 `creative_family` 与创意变体 `creative_variant`

### A. 创意家族判据（3/5）

两个候选方向**至少在以下五项中的三项不同**，才能认定为两个不同的 Creative Family：

1. 核心问题或核心矛盾；
2. 叙事发动机（Narrative Engine）；
3. 人物角色或人物关系；
4. 信息释放顺序；
5. 视觉前提或最终回报。

### B. 以下变化不得单独构成新的 Creative Family

```text
换标题 · 换第一句话 · 换语气 · 换修辞 · 换案例 · 换平台名称
「故事版 / 干货版 / 情绪版」等标签变化
```

### C. 创意变体 `creative_variant`

> 同一个 Creative Family 内，**不改变核心结构**，
> 只改变进入角度、具体表达、开场或语言实现。

**`creative_variant` ≠ `creative_family`。** 两者不得混用，不得互相顶替。
任何候选集合必须显式标明每一项是 family 还是 variant。

### D. 数量规则

> **默认生成 4 个 Creative Families。**

当且仅当出现以下情况，可减少到 **2 个以上**（即 ≥2），并**必须写明减少理由**：

* 任务复杂度低；
* 合法候选空间有限；
* 已有方向高度冻结。

**不得**：为满足数量制造伪 Family；不得强制所有任务永远生成 4 个；
不得用「3—5 个」一类模糊区间替代「默认 4 个 + 明确降级逻辑」。

### E. 与「标题家族」的区分

`title_family`（标题家族）是 Publishing 阶段同一条内容的多个标题入口，
**与 `creative_family` 不是同一概念**，不得互相套用判据。

## 3.4 证据等级（逐条继承，不得升格）

| 等级 | 含义 | 表达约束 |
|---|---|---|
| `REGISTERED_FACT` 已登记事实 | 已正式记录在案 | 可直接陈述 |
| `FIRSTHAND_OBSERVATION` 亲历观察 | 本人经手看到的 | 必须标明是谁看到的 |
| `PROFESSIONAL_JUDGMENT` 专业判断 | 从业者经验判断 | 必须说成判断，**不得写成已登记事实** |
| `LABELED_SCENARIO` 明确标注的设计情境 | 为说明问题而设计 | 标注**不得在脚本、字幕、发布文案中丢失** |
| `OPEN_VARIABLE` 待验证变量 | 还没有答案 | **不得写成已解决** |

## 3.5 状态枚举的作用域

**四个作用域互不通用。** 同一个词出现在不同作用域时，
必须用字段名限定（如 `gap_action: HOLD` 与 `release_decision: HOLD`），不得裸用。

### A. Artifact / Stage Status（产物阶段状态）

字段：`stage_status` —— 描述**当前 Skill 产物能否进入下一阶段**。

```text
READY
READY_WITH_CONDITIONS
INPUT_INSUFFICIENT
INPUT_CONFLICT_REQUIRES_FOUNDER
PRODUCTION_NOT_FEASIBLE
```

### B. Production Feasibility（制作可执行性）

字段：`production_feasibility` —— **只描述 Production Profile 的可执行性**。

```text
EXECUTABLE
EXECUTABLE_WITH_DOWNGRADE
NEED_ONE_RESOURCE
NOT_FEASIBLE
```

**与 A 的唯一映射关系（消除 `not_feasible` / `PRODUCTION_NOT_FEASIBLE` 的重名歧义）**：

```text
production_feasibility == NOT_FEASIBLE
    ⟹ stage_status = PRODUCTION_NOT_FEASIBLE
```

两者不是同义词：前者描述**条件**，后者描述**产物**。
全部枚举统一为 UPPER_SNAKE，不再出现小写变体。

### C. Release Decision（发布结论）

字段：`release_decision` —— **只描述最终 Publishing 的发布状态**。

```text
RELEASE
HOLD
```

### D. Gap Handling Action（缺口处理动作）

字段：`gap_action` —— 决策循环 `Return / Degrade` 环节的动作，
语义以《构建规范 v1.0》为准。

```text
RETURN    返回负责该缺口的正确上游角色
DEGRADE   降低制作或表达复杂度，但保留核心价值
HOLD      缺少关键事实或资源，当前无法继续
CANCEL    核心承诺在当前条件下无法成立
```

> `HOLD` 同时出现在 C 与 D 两个作用域，**由字段名区分**：
> `release_decision: HOLD` 指「成片不发布」；`gap_action: HOLD` 指「流程停下等关键输入」。

### E. 验收结论（不属于 Skill 运行时）

`ACCEPTED_FOR_PRODUCTION` 等验收状态由《验收标准 v1.0》定义，
**只用于验收 Skill，不得作为 Skill 运行时输出状态**。

## 3.6 补充术语

| 唯一用词 | 字段名 | 定义 |
|---|---|---|
| **内容单元** | `content_unit` | 一条独立发布的内容，是三份 Skill 的处理单位 |
| **成片** | `footage` | 已拍完并剪好的视频；图文形态下指已定稿的图片组 |
| **补录** | `pickup` | 主要拍摄结束后，为补齐缺口再拍的少量内容 |
| **人工接受** | `acceptance` | 由人明确接受某份产物；**只有被接受的产物才能进入下一段** |
| **平台适配差异** | `platform_adaptation_diff` | 同一条内容为不同平台分别做的调整 |

---

# 4. Cross-Skill Interface

本节分为两部分，**性质不同**：
4.A 是**冻结不变量**，Phase 1 不得改；
4.B 是**候选接口 Schema**，Phase 1 必须据此提出建议的最终接口。

## 4.A FROZEN_CROSS_SKILL_INVARIANTS（冻结不变量）

1. **Script 决定「内容说什么」。**
2. **Director 决定「怎样用视觉与声音实现」。**
3. **Packaging 决定「怎样对外第一触达与发布」。**
4. **下游不得重新选择上游业务含义。**
5. **任何 Skill 不得新增事实。**
6. **缺口必须返回正确职责角色**（`gap_action: RETURN`），同一缺口返回后仍无法消除应进入 `HOLD`，不得无限往返。
7. **人工 Acceptance 必须保留**：未被接受的产物一律不得作为下游输入。
8. **以下对象必须纵向保持**：
   `Audience Shift` / `Creative Concept` / `Promise` / `Tension` / `Evidence` / `Production Profile`。
9. **下游不得使 Promise 强度高于上游真实 Payoff。**

## 4.B CANDIDATE_INTERFACE_FOR_PHASE1（候选接口）

```yaml
interface_status: CANDIDATE_INTERFACE_FOR_PHASE1
```

以下字段表**不是最终冻结字段**。
Phase 1 Architecture Design **必须输出建议的最终接口**，
由下一阶段人工 Architecture Freeze 决定是否接受。

### B0. 三段共用字段

| 字段名 | 类型 | 说明 |
|---|---|---|
| `content_unit_id` | string | 内容单元标识，全链唯一 |
| `brief_id` | string | 来源 Brief 标识 |
| `inherited_locks` | object | 上游锁定项整体透传：观众问题、核心判断、必须表达、明确不得表达、CTA 决定、事实确认人等 |
| `production_profile` | object | 见第 2 节 |
| `content_origin_mode` | enum | 见 1.3 |
| `content_form` | object | `{"format": "口播", "topic": "企业叙事"}` |
| `runtime_selected_platform` | array\|string | 平台列表，或 `PLATFORM_UNCONFIRMED` |
| `acceptance_record` | object | `{"accepted_artifact", "upstream_artifact", "accepted_by", "accepted_at"}` |
| `stage_status` | enum | 见 3.5 A |
| `open_conditions` | array\<object\> | 每条写明：未成立的是什么、影响哪一条内容 |
| `gap_action` | enum | 见 3.5 D |
| `must_confirm_before_next_stage` | array\<string\> | 进入下一段前必须由人确认的事项 |

### B1. Creative Script Architect

**输入**

| 字段名 | 类型 | 说明 |
|---|---|---|
| `content_brief` | object | 已接受的 Brief 全文 |
| `content_brief.customer_problem` | string | 唯一观众情境与问题 |
| `content_brief.customer_blocker` | string | 观众当前卡点 |
| `content_brief.required_new_judgment` | string | 这条内容后必须形成的唯一新判断 |
| `content_brief.core_judgment` | string | 核心内容判断 |
| `content_brief.evidence_map` | array\<object\> | `{"content", "grade", "confirmer"}`，grade 见 3.4 |
| `content_brief.tension` | string | 上游已识别的张力 |
| `content_brief.relationship_stance` | string | 账号关系姿态 |
| `content_brief.must_use_assets` / `optional_assets` | array | 必须使用 / 可选素材 |
| `content_brief.on_camera_person` / `fact_confirmer` | string | 出镜人 / 事实确认人 |
| `content_brief.must_express` / `must_not_express` | array\<string\> | 必须表达 / 明确不得表达 |
| `content_brief.cta_decision` | object | CTA 或无 CTA 的决定 |
| `content_brief.publish_conditions` / `downgrade_conditions` / `cancel_conditions` | array | 发布 / 降级 / 取消条件 |
| （共用字段） | —— | 见 B0 |

**输出**

| 字段名 | 类型 | 说明 |
|---|---|---|
| `audience_shift` | object | `{"from", "to"}` |
| `core_problem` | string | 核心问题 |
| `creative_concept` | string | 主 Creative Concept |
| `creative_family_candidates` | array\<object\> | `{"family_id", "name", "differs_on": [五项中命中的项], "one_line"}`，**默认 4 个**，减少必须填 `reduction_reason` |
| `creative_family_reduction_reason` | string\|null | 少于 4 个时必填 |
| `creative_family_selected` | string | 选定的 `family_id` |
| `elimination_reasons` | array\<object\> | `{"family_id", "mechanism_reason"}`，**必须是机制性原因**，「没感觉」不合格 |
| `creative_variants` | array\<object\> | `{"variant_id", "of_family", "what_changes"}`，同族内的进入角度差异 |
| `content_promise` | string | 内容承诺，有且只有一条 |
| `opening` | object | `{"first_perceived_visual", "first_expression_unit"}` |
| `opening_promise` | string | 开场承诺 |
| `narrative_engine` | string | 叙事发动机 |
| `content_structure` | array\<object\> | `{"beat_id", "beat_name", "state_change", "content"}`，每个主要段落必须至少改变一项状态 |
| `tension` | object | `{"type", "what_is_unfinished", "or_alternative_reason"}`，无强张力时填替代的继续消费理由 |
| `character_expression` | object | 人物、关系、语言与可表演性 |
| `must_be_accurate` / `free_to_improvise` | array | 必须准确表达部分 / 可自然发挥部分 |
| `full_expression_deliverable` | object | **完整表达成品**。按形态取一：`spoken_script` / `dialogue_outline` / `article_body` / `vlog_narration` |
| `landing_point` | string | 落点 |
| `visual_opportunities` | array\<object\> | `{"beat_id", "what_can_be_seen", "why_it_matters"}`。**不写景别机位秒数** |
| `evidence_requirements` | array\<object\> | `{"claim", "required_grade", "confirmer", "status"}` |
| `production_profile_dependencies` | array\<object\> | `{"expression_ref", "depends_on_field", "if_absent"}` |
| `gaps_and_return_conditions` | array\<object\> | `{"gap", "blocks_what", "gap_action", "return_to"}` |
| （共用字段） | —— | 原样透传 |

**不得越权**：重新选择上游经营目标 / 目标顾客 / 账号使命；输出完整摄影分镜作为主体；
为戏剧性虚构事实；资源明显不成立时输出不可执行大片方案；写最终标题、封面文案、发布文案。

### B2. Production Director

**输入**：`creative_script`（B1 全部输出，已被接受）+ `footage_status` + 共用字段。

**输出**

| 字段名 | 类型 | 说明 |
|---|---|---|
| `director_concept` | string | 导演概念 |
| `visual_premise` | array\<object\> | `{"premise", "from_visual_opportunity", "must_hold"}` |
| `scene_structure` | array\<object\> | `{"scene_id", "place", "time", "who", "covers_beats"}` |
| `evidence_to_shot_map` | array\<object\> | `{"evidence_ref", "shot_id", "how_it_is_proven"}` |
| `shot_plan` | array\<object\> | `{"shot_id", "scene_id", "beat_id", "visual_content", "framing", "camera", "sound", "function", "priority"}`，每个镜头必须承担新的事实、变化、反应、关系、对比或转场功能 |
| `character_action` | array\<object\> | 人物行动 |
| `performance_direction` | array\<object\> | `{"person_code", "how_to_deliver", "what_to_avoid"}` |
| `sound_design` | object | `{"live_sound", "voiceover", "ambient", "music_slots", "risk"}` |
| `edit_logic` | object | `{"order", "cut_principles", "pace_principle", "what_must_not_be_cut"}` |
| `must_shoot_assets` | array\<object\> | 必拍素材 |
| `optional_assets` | array\<object\> | 可选素材 |
| `alternative_assets` | array\<object\> | 替代素材 |
| `pickup_assets` | array\<object\> | `{"pickup_id", "what", "why", "deadline"}` |
| `schedule` | array\<object\> | 拍摄 / 制作调度 |
| `production_profile_fit` | object | Production Profile 适配说明 |
| `standard_version` / `downgrade_plan` | object / array | 标准版本与必要降级方案，`{"level", "action", "what_is_cut", "promise_change", "evidence_strength_change"}` |
| `packaging_usable_assets` | array\<object\> | `{"asset_ref", "type": "COVER_CANDIDATE/FIRST_FRAME_CANDIDATE/QUOTABLE_LINE/STILL", "from_shot"}` |
| `production_feasibility` | enum | 见 3.5 B |
| （共用字段） | —— | 原样透传 |

**终端字段**（供现场执行，不进入第三段，不算孤儿字段）：
`performance_direction`、`character_action`、`schedule`、`scene_structure`、`director_concept`。

**不得越权**：重选主题、重写 Creative Concept、重新定义目标用户、
用制作规模替代创意质量、用随机 B-roll 填补缺乏视觉证据的问题、为镜头效果伪造真实过程。

### B3. Publishing & Packaging Architect

**两种合法工作状态**（以《构建规范 v1.0》为准）：
`PRE_PRODUCTION_PACKAGING_REQUIREMENTS`（拍摄前包装需求）与
`FINAL_RELEASE_PACKAGE`（最终发布包）。字段：`packaging_mode`。

**输入**：`production_package`（B2 全部输出，已被接受）+ 透传的 `content_promise` /
`full_expression_deliverable` + `footage_status` + 共用字段。

**输出**

| 字段名 | 类型 | 说明 |
|---|---|---|
| `packaging_mode` | enum | 见上 |
| `single_distribution_promise` | string | 唯一传播承诺，必须能追溯到 `content_promise`，**不得强于正文真实 Payoff** |
| `content_core` | string | 内容核心提炼 |
| `title_family` | array\<object\> | `{"title_id", "text", "entry_type", "supported_by"}`，入口可为信息 / 矛盾 / 身份 / 结果 / 情境 |
| `recommended_title` | string | 推荐标题的 `title_id` |
| `recommended_title_reason` | string | 必须指向正文哪一处支撑它 |
| `cover_plan` | object | `{"source_asset", "visual", "text_on_cover", "why"}` |
| `first_frame_plan` | object | `{"source_shot", "what_is_visible", "why"}` |
| `title_cover_frame_coherence` | string | 标题—封面—首帧协同说明 |
| `publish_copy` | object | `{"body", "topics", "mentions"}` |
| `caption_and_voice_placement` | object | `{"caption_policy", "screen_text_items": [{"text","at_beat","who_is_responsible"}], "voiceover_placement"}` |
| `comment_entry` | object | `{"pinned_comment", "expected_questions", "who_replies"}` |
| `cta` | object | `{"has_cta": "YES/NO", "action", "entry", "inherited_from_brief": "YES"}` |
| `platform_neutral_part` | object | 平台中性部分 |
| `platform_adaptation_diff` | array\<object\> | 平台差异部分，见 4.D |
| `testable_variables` | array\<object\> | 可测试变量 |
| `pickup_requirements` | array\<object\> | `{"pickup_id", "what", "blocks_release": "YES/NO"}`，与 `pickup_assets` 同 id |
| `release_decision` | enum | `RELEASE` / `HOLD` |
| `release_reason` | string | `HOLD` 必须写明缺什么、谁来补 |
| （共用字段） | —— | 原样透传 |

**不得越权**：重写核心脚本、为标题制造不存在的事实、用包装补偿内容根本不足、
破坏人物人格、修改已确认的业务任务、把平台适配变成重新选题。

## 4.C 衔接检查（孤儿字段 0 / 缺口字段 0）

| 上游输出 | 下游输入 | 消费方 |
|---|---|---|
| Brief `core_judgment` / `evidence_map` / `must_express` / `must_not_express` / `cta_decision` | `inherited_locks` | 三段全程透传 |
| CSA `full_expression_deliverable` | `creative_script.full_expression_deliverable` | Director（只读）→ Packaging（只读） |
| CSA `content_structure.beat_id` | `shot_plan.beat_id` | Director |
| CSA `visual_opportunities` | `visual_premise.from_visual_opportunity` | Director |
| CSA `evidence_requirements` | `evidence_to_shot_map` / `must_shoot_assets` | Director |
| CSA `production_profile_dependencies` | `production_feasibility` | Director |
| CSA `content_promise` | `single_distribution_promise` | Packaging（跨段透传） |
| CSA `tension` | `shot_plan` / `sound_design` → `content_core` | Director → Packaging |
| PD `packaging_usable_assets` | `cover_plan.source_asset` / `first_frame_plan.source_shot` | Packaging |
| PD `edit_logic` / `sound_design` | `caption_and_voice_placement` | Packaging |
| PD `pickup_assets.pickup_id` | `pickup_requirements.pickup_id` | Packaging（同 id 对齐） |
| PD `downgrade_plan` | `release_decision` | Packaging |
| PD `performance_direction` / `character_action` / `schedule` / `scene_structure` / `director_concept` | —— | **终端字段** |

**外部输入**：`footage_status` 由人在第二、三段入口填入，不由上游产出。
**缺失处理**：每个 Required Input 缺失时都必须有 `gap_action` 路径，不得静默猜测。

## 4.D 平台适配：只定维度，不预填取值

`platform_adaptation_diff` 每个平台一条，只回答下列维度是否需要改：

| 维度 | 字段名 |
|---|---|
| 画幅与安全区 | `frame_and_safe_area` |
| 封面规格与可读性 | `cover_spec` |
| 文案形态 | `copy_shape` |
| 字幕呈现 | `caption_style` |
| 承接入口形态 | `entry_form` |
| 合规口径 | `compliance_note` |

**填写纪律**：`runtime_selected_platform == PLATFORM_UNCONFIRMED` 时，
每个维度写 `PENDING_PLATFORM_LOCK`，不得猜测填值。
平台差异必须是**有理由的实质差异**，不得只是换个平台名称。

---

# 5. 运行环境约束

| 维度 | 取值 |
|---|---|
| Skill 宿主平台 | Dify |
| 生产模型 | `PRODUCTION_MODEL_UNCONFIRMED` |
| 架构要求 | `MODEL_AGNOSTIC` |
| 文件结构 | `SKILL.md` / `references/` / `scripts/` |
| 输出格式 | JSON 为主，结构化 Markdown 为辅 |
| 上下文长度限制 | 未在本仓库实测登记 |
| 脚本执行 | 允许，仅限确定性检查 |

## 5.1 生产模型：为什么是 UNCONFIRMED

```yaml
production_model_status: PRODUCTION_MODEL_UNCONFIRMED
skill_host: Dify
architecture_requirement: MODEL_AGNOSTIC
```

仓库中三条记录互不相容，且没有任何一条同时满足「明确 + 更新 + 权威」：

| 记录 | 文件 | 版本 / 提交 | 日期 | 说法 |
|---|---|---|---|---|
| 长期不变的 Founder 裁决 | `笛语项目基线.md` 第四节 | 文件截至 2026-08-19；末次提交 `a857af4` | 2026-08-20 | 当前 Demo、演示及当前业务验证**统一使用 Qwen 系列** |
| 生产链 PRD 第 6.3 节 模型策略 | `CONTENT_PRODUCTION_CHAIN_PRD_v0.1.md`（分支 `feature/content-production-chain-v1`） | 提交 `3438517` | 2026-08-21 | 主测试 **deepseek-v4-flash**，fallback qwen3.8-max |
| 实际画布 provider | `DIYU_DEMO_V1_MAIN_CHATFLOW_v0.1.yml` | 主分支 | —— | `langgenius/deepseek/deepseek` |

**裁决依据**：

* 基线的说法**更权威**（真源第一位，且明确归入「长期不变的 Founder 裁决」），但**日期更早**；
* 生产链 PRD 的说法**日期更新**，但**没有 Decision ID、没有裁决人与裁决日期戳**，
  且按生产链自身的真源优先级，项目基线排在 PRD 之上；
* **旧画布仍在使用某模型，不构成业务裁决**。

**因此**：

> **Phase 1 不得把某一模型的特殊行为写成 Skill 专业架构。**
> 具体目标生产模型在进入多模型验收与真实运行验收之前冻结。
> 不得自行选择 Qwen 或 DeepSeek。

`FOUNDER_DECISION_REQUIRED`：目标生产模型。

## 5.2 知识路由：四层，各自作用不同

### SKILL.md —— 稳定固定入口（Stable Entry Point）

**每次调用时加载**，负责：

```text
职责 · 判断顺序 · 条件路由 · 输出合同 · Return/Degrade · 最小自检
```

> **不得再表述为「唯一模型输入」**——`references/` 会在条件命中时同样进入模型上下文。

### references/ —— 条件加载模型上下文

**仅在条件命中时加载**：

```text
CONDITIONAL_DOMAIN_REFERENCE   行业条件知识
DATED_REFERENCE                带日期的平台资料、趋势、工具能力
长示例
形式条件资料
```

**不得全部默认加载。**

### scripts/ —— 非模型推理的确定性检查

```text
Schema · 必填字段 · 枚举 · 路径 · 接口 · 返回码 · 文件结构
```

**不进入创作推理上下文。** 不得让语言模型去做纯机械检查。

### Runtime Input —— 每次任务事实

```text
Brief · 品牌事实 · 人物权限 · 素材 · Production Profile
平台 · 当前产物 · 目标 · 承接能力
```

**不得写死进通用 Skill。**

### Governance Docs —— 不得作为运行时固定 Prompt

```text
context_pack · 构建规范 · 验收标准 · 评审报告 · 研究 memo
```

它们用于**构建与验收 Skill**，不用于每条内容运行。

## 5.3 COMPILATION_ROUTE

所有候选规则必须归入且**只能归入一项**：

```text
SKILL_MD                稳定决策内核
CONDITIONAL_REFERENCE   条件命中才加载的领域 / 形式知识
DATED_REFERENCE         带日期的平台与趋势资料
SCRIPT_CHECK            确定性机械检查
RUNTIME_INPUT           每次任务提供的事实
REJECT                  不进入最终 Skill
```

**不得使用**：「暂时放 Skill 里以后再说」「可能放 reference」「视情况」。

## 5.4 输出格式

1. **不使用 boolean 类型。** Dify 的结构化输出模板明令要求不要输出 boolean、改用 string，
   与 boolean schema 直接冲突——本仓已有一次真实运行因此产出空正文。
   所有是非字段一律用字符串枚举：`YES` / `NO` / `UNKNOWN`。
2. **状态枚举原样返回**，不翻译、不加标点，作用域见 3.5。
3. **长文本字段用结构化 Markdown 承载**，JSON 只放字符串。
4. **最终输出不得出现内部思维链**或 `<think>` 等价内容。

## 5.5 输出预算

* 本仓库未登记当前生产模型的上下文长度上限，**不写具体数值，不按型号名猜测**；
* 已登记的可复用教训：**输出预算必须为长结构化产物单独放大**；
  本仓曾出现输出预算被推理块吃光、正文为空的真实运行失败；
* 三份 Skill 输出体量差异大（第一段含完整表达成品，最大），
  必须**逐节点设定输出预算**；`stage_status` / `open_conditions` /
  `gap_action` / `must_confirm_before_next_stage` 任何情况下不得被截断。

---

# 6. 脱敏示例任务（格式演示，不代表范围）

> **本节唯一用途是演示输入输出的结构长什么样。**
> 适用范围以第 1 节六轴声明为准。
> **示例不得成为 Phase 1 输出的默认答案。**
> **两个示例的节拍结构刻意不同**——不得据此认为所有任务必须使用同一 beat 结构。

## 6.1 示例 A：口播（服装行业夹具）

> ⚠️ **该示例为服装行业夹具，仅用于理解格式，不代表 Skill 的行业覆盖范围。**
> ⚠️ **示例中的行业特定逻辑（试穿、版型、面料、搭配）不得泛化为通用规则。**
> 品牌、人物、货号、经营数据均已脱敏。

**输入 Brief 摘要（脱敏）**

```yaml
brief_id: BRIEF-A-001
content_unit_id: CU-A-001
account: ACC-01（选品负责人账号）
content_form: {format: 口播, topic: 企业叙事}
content_origin_mode: 现拍
customer_problem: 通勤外套买回来只能配一种场合，利用率低
customer_blocker: 分不清是款式选错了，还是搭配方式不对
required_new_judgment: 有些问题能靠搭配解决，有些只能靠选择阶段提前排除
core_judgment: 选择阶段能提前比较的事，不要留到搭配阶段补救
evidence_map:
  - {content: 内部演示试穿中出现的层次偏正式问题, grade: FIRSTHAND_OBSERVATION, confirmer: R2}
  - {content: 该品类已登记的基础信息, grade: REGISTERED_FACT, confirmer: R1}
  - {content: 不同体型的表现差异, grade: OPEN_VARIABLE, confirmer: null}
must_express: [内部试穿人员不是真实顾客]
must_not_express: [年龄或身材焦虑, 未登记的面料与功能结论]
cta_decision: {has_cta: "YES", action: 预约到店试穿, entry: 已确认的唯一正式入口}
```

**制作条件（脱敏）**

```yaml
requested_mode: 门店实拍对话访谈
available_mode: 单人 + 手机，周三下午 2 小时，门店营业中
minimum_viable_mode: 单机位口播
recommended_mode: 单机位口播，访谈延后
accepted_mode: 单机位口播
budget_band: LOW
quality_expectation: STANDARD
acceptable_downgrade_path: [减少镜头数量, 改单机位, 延期一周]
production_feasibility: EXECUTABLE_WITH_DOWNGRADE
```

**期望输出骨架**

```yaml
# ---------- 第一段 Creative Script Architect ----------
audience_shift: {from: 觉得是自己不会搭, to: 知道哪些问题在选择阶段就该排除}
core_problem: 顾客把"选择失误"误判成"搭配能力不足"
creative_concept: 把一次自己人的误判摊开，划出可补救与不可补救的分界

creative_family_candidates:
  - family_id: F1
    name: 一次真实误判的复盘
    differs_on: [核心矛盾, 叙事发动机, 信息释放顺序, 视觉前提]
    one_line: 我们自己也选错过——先给结果，再倒推原因
  - family_id: F2
    name: 两件同框的当场比较
    differs_on: [核心矛盾, 叙事发动机, 人物关系, 信息释放顺序, 视觉前提]
    one_line: 两件看起来差不多，差别在哪——双人并列比较后判定
  - family_id: F3
    name: 高频问题的逐条回答
    differs_on: [核心矛盾, 叙事发动机, 人物关系, 信息释放顺序, 视觉前提]
    one_line: 顾客问的和我们答的不是一回事——先问后答
  - family_id: F4
    name: 选择阶段与搭配阶段的分界
    differs_on: [核心矛盾, 叙事发动机, 信息释放顺序]
    one_line: 先立分界再举例，把问题归到两个阶段
# 四个 family 两两之间至少三项不同，满足 3/5 判据
creative_family_reduction_reason: null
creative_family_selected: F1
elimination_reasons:
  - {family_id: F2, mechanism_reason: 当前 accepted_mode 为单机位单人，两件同框与双人关系无法实现}
  - {family_id: F3, mechanism_reason: 逐条问答不产生状态推进，无法形成可迁移判断}
  - {family_id: F4, mechanism_reason: 先立分界导致证据后置，亲历观察失去入场位置}

creative_variants:
  - {variant_id: F1-V1, of_family: F1, what_changes: 从"错误本身"开场}
  - {variant_id: F1-V2, of_family: F1, what_changes: 从"当时以为没问题"开场}
# 注意：F1-V1 与 F1-V2 只改开场与进入角度，核心结构不变，
#       因此是 creative_variant，不是新的 creative_family

content_promise: 看完能分清哪些穿着问题该在买之前解决
opening:
  first_perceived_visual: 出镜人手里拿着那件被讨论的外套
  first_expression_unit: 这件是我自己选错的
opening_promise: 接下来会说清楚错在哪一步
narrative_engine: 发现（从结果倒推原因）
tension:
  type: 未解决的问题
  what_is_unfinished: 已经出现的问题里，哪些还能补救没有定论
content_structure:
  - {beat_id: B1, beat_name: 结果先行, state_change: 情境}
  - {beat_id: B2, beat_name: 摩擦还原, state_change: 信息}
  - {beat_id: B3, beat_name: 分界建立, state_change: 判断}
  - {beat_id: B4, beat_name: 落点, state_change: 预期}
full_expression_deliverable: {spoken_script: "（口播全文，逐句可念）"}
landing_point: 选择阶段能比较的事，不要留到搭配阶段补救
visual_opportunities:
  - {beat_id: B2, what_can_be_seen: 层次叠加后领口区域的实际状态, why_it_matters: 让摩擦被看见而不是被描述}
evidence_requirements:
  - {claim: 层次偏正式, required_grade: FIRSTHAND_OBSERVATION, confirmer: R2, status: CONFIRMED}
gaps_and_return_conditions:
  - {gap: 不同体型差异无证据, blocks_what: 任何群体性结论, gap_action: DEGRADE, return_to: 保留为 OPEN_VARIABLE}
stage_status: READY_WITH_CONDITIONS

# ---------- 第二段 Production Director ----------
director_concept: 单机位近景，让说话的人和被讨论的实物始终在同一画面里
visual_premise:
  - {premise: 实物必须可辨认, from_visual_opportunity: B2, must_hold: "YES"}
evidence_to_shot_map:
  - {evidence_ref: 层次偏正式, shot_id: S2, how_it_is_proven: 领口区域特写呈现实际状态}
shot_plan:
  - {shot_id: S1, beat_id: B1, visual_content: 出镜人持物开口, framing: 近景, camera: 固定, function: 建立人物与对象, priority: MUST}
  - {shot_id: S2, beat_id: B2, visual_content: 领口区域特写, framing: 特写, camera: 固定, function: 证据呈现, priority: MUST}
downgrade_plan:
  - {level: 1, action: 删除, what_is_cut: 无法由 R2 确认的细节, promise_change: 无, evidence_strength_change: 无}
  - {level: 2, action: 降级, what_is_cut: 收窄到单件观察, promise_change: 承诺收窄, evidence_strength_change: 下降}
packaging_usable_assets:
  - {asset_ref: S2, type: COVER_CANDIDATE, from_shot: S2}
pickup_assets: []
production_feasibility: EXECUTABLE_WITH_DOWNGRADE
stage_status: READY_WITH_CONDITIONS

# ---------- 第三段 Publishing & Packaging ----------
packaging_mode: FINAL_RELEASE_PACKAGE
single_distribution_promise: 分清哪些穿着问题该在买之前解决
title_family:
  - {title_id: T1, text: 有些问题搭配救不回来, entry_type: 矛盾, supported_by: B3}
  - {title_id: T2, text: 这件是我自己选错的, entry_type: 身份, supported_by: B1}
  - {title_id: T3, text: 买之前该比的三件事, entry_type: 信息, supported_by: B3}
recommended_title: T1
recommended_title_reason: 正文 B3 明确区分了可补救与不可补救，标题不超出该结论
cover_plan: {source_asset: S2, text_on_cover: 能补救 / 不能补救, why: 直接指向落点}
first_frame_plan: {source_shot: S1, what_is_visible: 人与实物同框, why: 与标题的身份入口一致}
caption_and_voice_placement:
  caption_policy: 全片烧录字幕
  screen_text_items: [{text: 内部演示，非顾客, at_beat: B1, who_is_responsible: R2}]
cta: {has_cta: "YES", action: 预约到店试穿, entry: 已确认的唯一正式入口, inherited_from_brief: "YES"}
platform_adaptation_diff:
  - {platform: PENDING_PLATFORM_LOCK, frame_and_safe_area: PENDING_PLATFORM_LOCK}
pickup_requirements: []
release_decision: RELEASE
stage_status: READY_WITH_CONDITIONS
```

## 6.2 示例 B：图文（知识付费 · 虚构示例）

> ⚠️ **虚构示例**。品牌、人物、课程、销量均为虚构，仅用于演示格式。
> 本例演示 **Creative Family 数量降级** 的合法用法。

**输入 Brief 摘要**

```yaml
brief_id: BRIEF-B-001
content_unit_id: CU-B-001
account: ACC-02（主讲人账号）
content_form: {format: 图文, topic: 职场成长}
content_origin_mode: 评论回应
customer_problem: 学完课程记不住，不知道是方法问题还是自己不适合
customer_blocker: 把"记不住"当成能力问题，而不是复习安排问题
required_new_judgment: 记不住多数是复习间隔问题，不是理解力问题
core_judgment: 先改复习安排，再判断适不适合
evidence_map:
  - {content: 学员在评论区反复提出的同一问题, grade: REGISTERED_FACT, confirmer: 助教}
  - {content: 主讲人带班过程中的观察, grade: FIRSTHAND_OBSERVATION, confirmer: 主讲人}
  - {content: 该方法对不同基础学员的效果差异, grade: OPEN_VARIABLE, confirmer: null}
must_express: [该建议只针对复习安排, 不承诺学习结果]
must_not_express: [通过率、涨薪幅度等未登记数据, 任何效果保证]
cta_decision: {has_cta: "NO", reason: 本条只做认知澄清}
```

**制作条件**

```yaml
requested_mode: 图文长文
available_mode: 1 人，无拍摄，只有历史课件截图
minimum_viable_mode: 纯文字 + 2 张已有截图
recommended_mode: 图文，配 3 张自制示意图
accepted_mode: 图文，配 3 张自制示意图
equipment: []
asset_rights: {owner: 自有课件, scope: [自有账号发布], third_party_faces: "NO"}
production_feasibility: EXECUTABLE
```

**期望输出骨架**

```yaml
# ---------- 第一段 ----------
audience_shift: {from: 怀疑自己不适合学, to: 先去改复习间隔再判断}
core_problem: 学员把"安排问题"归因成"能力问题"

creative_family_candidates:
  - family_id: F1
    name: 直接回应那条原始提问
    differs_on: [核心矛盾, 叙事发动机, 信息释放顺序]
    one_line: 从真实提问进入，逐步把归因掰过来
  - family_id: F2
    name: 两种复习安排的对照
    differs_on: [核心矛盾, 叙事发动机, 信息释放顺序, 视觉前提]
    one_line: 并列两种安排，让差别自己说话
creative_family_reduction_reason: >
  合法候选空间有限：来源模式为评论回应，原始提问已锁定核心矛盾入口；
  且 accepted_mode 无拍摄、无人物出镜，人物关系与视觉前提两轴不可用，
  能构成 3/5 差异的合法方向只有两个。按默认 4 个降级至 2 个。
creative_family_selected: F1
elimination_reasons:
  - {family_id: F2, mechanism_reason: 对照结构需要两组真实学员数据，当前证据只有 OPEN_VARIABLE，无法支撑}

creative_variants:
  - {variant_id: F1-V1, of_family: F1, what_changes: 以提问原文开场}
  - {variant_id: F1-V2, of_family: F1, what_changes: 以结论开场再回补提问}

content_promise: 看完知道"记不住"该先改什么
opening:
  first_perceived_visual: 首图为复习间隔安排的对比示意
  first_expression_unit: 有人问，学完就忘是不是不适合
opening_promise: 这条会给出先改哪一步的具体判断
narrative_engine: 问题（归因纠正）
tension:
  type: 信息差
  what_is_unfinished: 学员用错误归因解释现象，正确解释尚未给出
content_structure:
  - {beat_id: B1, beat_name: 提问原样, state_change: 情境}
  - {beat_id: B2, beat_name: 归因拆解, state_change: 理解}
  - {beat_id: B3, beat_name: 可执行安排, state_change: 判断}
# 注意：本例只有三个节拍，与示例 A 的四节拍不同，不存在通用 beat 模板
full_expression_deliverable: {article_body: "（图文正文全文）"}
landing_point: 先改复习安排，再判断适不适合
visual_opportunities:
  - {beat_id: B2, what_can_be_seen: 复习间隔安排前后的对比, why_it_matters: 让抽象建议可执行}
evidence_requirements:
  - {claim: 学员反复提出同一问题, required_grade: REGISTERED_FACT, confirmer: 助教, status: CONFIRMED}
stage_status: READY

# ---------- 第二段（图文形态：无镜头，只有图片计划）----------
director_concept: 三张示意图承担正文里最难用文字说清的三处
shot_plan:
  - {shot_id: P1, beat_id: B2, visual_content: 复习间隔前后对比示意图, framing: 图片, camera: 无, function: 证据呈现, priority: MUST}
must_shoot_assets: [{asset: P1, why: 缺此图 B2 不成立}]
pickup_assets: []
downgrade_plan: [{level: 2, action: 降级, what_is_cut: 示意图减到 1 张, promise_change: 无, evidence_strength_change: 无}]
packaging_usable_assets: [{asset_ref: P1, type: COVER_CANDIDATE, from_shot: P1}]
production_feasibility: EXECUTABLE
stage_status: READY

# ---------- 第三段 ----------
packaging_mode: FINAL_RELEASE_PACKAGE
single_distribution_promise: 记不住先改复习安排，不是先怀疑自己
title_family:
  - {title_id: T1, text: 记不住，多半不是理解力的问题, entry_type: 矛盾, supported_by: B2}
  - {title_id: T2, text: 学完就忘的人，先改这一步, entry_type: 结果, supported_by: B3}
recommended_title: T1
recommended_title_reason: 正文只支撑归因纠正，不支撑任何效果承诺
cta: {has_cta: "NO", inherited_from_brief: "YES"}
release_decision: RELEASE
stage_status: READY
```

## 6.3 Example Isolation 声明

1. 示例 A 的行业逻辑（试穿、版型、面料、搭配）**只属于服装行业**，
   不得抽象成任何通用规则、通用节拍或通用检查项。
2. 示例 B 为虚构，其中的教学方法不构成任何专业建议。
3. **两个示例的节拍数量与结构不同，是刻意的**——不存在通用 beat 模板。
4. 示例中的 `creative_family` 已按 3/5 判据校验；同族内的表达差异已标为 `creative_variant`。
5. **删除本节后，全包规则仍然成立。** 示例不得成为 Phase 1 输出的默认答案。

---

# 7. PHASE1_REQUIRED_ARCHITECTURE_DECISIONS

> 以下每一项，Phase 1 模型**必须提出建议方案和理由**。
> **不得自行宣布 Founder 已冻结。** 最终冻结权限属于下一阶段的人工 Architecture Freeze。

| # | 必答事项 | 建议须包含 |
|---|---|---|
| 1 | 片内 CTA 与发布层 CTA 的职责分工 | 谁产出、谁可改、冲突时谁优先 |
| 2 | 封面 / 首帧需求由谁提出、最终由谁决定 | 需求方与决定方分离方案 |
| 3 | 图文主体与发布文案的边界 | 图文形态下二者是否合一 |
| 4 | Caption 与 Screen Text 的职责归属 | 谁写、谁担责、谁校对 |
| 5 | Pickup / 补录需求如何跨 Skill 返回 | 返回路径与 id 对齐机制 |
| 6 | Production 降级导致 Evidence / Promise 强度变化时返回谁 | 触发条件与返回角色 |
| 7 | Production Profile 最终字段 Schema | 相对 2.B 的字段 Delta |
| 8 | 三 Skill 最终接口字段 | 相对 4.B 的字段 Delta，孤儿 / 缺口均为 0 |
| 9 | 哪些判断进入 `SKILL_MD` | 逐条列出与理由 |
| 10 | 哪些判断进入 `CONDITIONAL_REFERENCE` | 触发条件写明 |
| 11 | 哪些进入 `DATED_REFERENCE` | 日期与失效机制 |
| 12 | 哪些进入 `SCRIPT_CHECK` | 可机械判定的依据 |
| 13 | 哪些保持 `RUNTIME_INPUT` | 为什么不能写死 |
| 14 | 哪些内容必须 `REJECT`，不进入最终 Skill | 拒绝理由 |

**附加必答项（本轮新增，来自跨文件核对）**：

| # | 事项 | 状态 |
|---|---|---|
| 15 | 目标生产模型 | `FOUNDER_DECISION_REQUIRED`，见 5.1。Phase 1 只能按 `MODEL_AGNOSTIC` 设计 |

---

# 8. 本轮跨文件核对结论

| 检查项 | 结论 |
|---|---|
| Creative Family 定义 | 三份文件已统一为 3/5 判据 |
| Creative Variant | 已作为独立术语分出，与 Family 不再混用 |
| Tension 定义 | 已统一为「尚未完成状态」，允许无强张力 |
| 开场 / Hook 术语 | `opening` / `opening_promise` 为正式字段，Hook 仅为通俗叫法 |
| Production Profile | 冻结语义与候选 Schema 已分开 |
| Cross-Skill Interface | 冻结不变量与候选接口已分开 |
| 生产模型 | `PRODUCTION_MODEL_UNCONFIRMED`，证据见 5.1 |
| 平台 | 支持范围与运行时锁定已分离 |
| 六轴之外 | 改为 `OUTSIDE_VALIDATED_SCOPE`，不再一律拒绝 |
| SKILL.md / references | 已改为稳定入口 + 条件加载，不再称「唯一模型输入」 |
| 状态枚举 | 已分四个作用域，`NOT_FEASIBLE` 与 `PRODUCTION_NOT_FEASIBLE` 已给出映射 |
| 示例 | 已按新定义重校 |

**尚未消除、需 Founder 裁决的事项**：目标生产模型（见 5.1 与第 7 节第 15 项）。
该项**不阻塞** Phase 1——Phase 1 按 `MODEL_AGNOSTIC` 设计即可。
