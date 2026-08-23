# Creative Script 参考投影探针 · RUN_001
> 本轮只验证 references 是否按确定性规则按需加载。**不是**内容质量评测，**不**对 Creative Script 的产出好坏作任何判断。

---

## 1. 运行标识

| 项 | 值 |
|---|---|
| 应用名 | DIYU Demo Creative Script Reference Projection Probe v0.1 |
| `app_id` | `4745fe5f-d279-4b12-9486-04541f9c8107` |
| `workflow_id`（已发布） | `2e3cdb74-d3cd-4ea0-b505-52544fd812e4` |
| Run ID | `920a1355-d006-402a-b3ae-fe59303a93ed` |
| 状态 | `succeeded` |
| 墙钟 | 331.0 秒 |
| tokens | 49918 |
| 运行次数 | **1 次，直接成功，无重试** |

本应用为**全新创建**，未覆盖任何已有 Dify 应用。

### 关于一次客户端超时

首次 HTTP 调用在本地执行器的 2 分钟上限处被切断（客户端连接中断），但服务端该次运行**未失败、未重启、未重发**，继续执行至 330.97 秒成功结束。后台 `workflow_runs` 中该 app 名下**只有一条记录**且状态为 `succeeded`——即本轮**没有发生任务书第八节所指的基础设施失败重试**，因此没有需要保留的失败记录。

---

## 2. 实际模型与参数（执行前从插件定义与后台读取，非按任务书硬填）

| 项 | 值 | 来源 |
|---|---|---|
| provider | `langgenius/deepseek/deepseek` | 后台 `workflows.graph` |
| model | `deepseek-v4-flash` | 同上 |
| 插件版本 | `deepseek-0.0.20` | `plugin_daemon` 内 `storage/cwd/langgenius/deepseek-0.0.20@850efe73…` |
| `max_tokens` | `384000` | 插件模型定义 `deepseek-v4-flash.yaml`：`max_tokens` 的 `min: 1 / max: 384000 / default: 4096` |
| `top_p` | `0.8` | 沿用最近一次成功运行的 `completion_params` |
| `thinking` | `true` | 插件定义中的 boolean 参数，默认 true |
| `reasoning_effort` | `high` | 插件定义 options：low / high / max，默认 high |
| `temperature` | **未设置** | 按要求不自行补 |
| Fallback | 未触发。主模型可用，未使用 Qwen3.8 Max | — |

**关于 `384000`：** 它是插件为 `max_tokens` 声明的**上限值**，是合法的输出长度参数，不是上下文窗口——同一份模型定义里上下文是 `model_properties.context_size: 1000000`。现有工作流沿用的 `max_tokens: 384000` 因此成立，本次继续沿用。

后台实际落地的参数原文：

```json
completion_params": {"max_tokens": 384000, "reasoning_effort": "high", "thinking": true, "top_p": 0.8}, "mode": "chat", "name": "d
```

**reasoning 分离**：LLM 原始输出 102464 字符（含 `<think>` 段），经 `Final Extract` 节点按 `</think>` 切分后 Final 为 7416 字符。**Final 中不含任何 think 内容**（第 6 项验收已机器核验）。

---

## 3. 输入与 Skill 哈希

### 3.1 基线

| 项 | SHA-256 |
|---|---|
| `writing-creative-scripts/SKILL.md` | `d0f78a480f58d494a29d3a34e35106ba0ff48719052361748ed513c721fc7b6a` |
| `references/platforms.md` | `98fa083c36710fc65f7d5fcf58fb6c33f14d3f984e07c014d7ab47fafe641d2d` |
| `references/industry-conditions.md` | `b085f1218a561adb500980464325c4356413187ee6e45be5430d5d1334fb7f6d` |
| `references/examples.md` | `635c86e11ab9bd4e6e1b1fb721b2e3929f8a57c8a18c64f57dc81d743228f3e5` |

以上四份与基线提交 `2ec2ba1` 逐份一致；九份 Skill 内 references 副本与共享主本同哈希。**本轮未修改三份 Skill 与三份 references 的任何一个字节。**

### 3.2 探针输入

| 项 | 值 |
|---|---|
| 输入夹具 | `content-production/fixtures/CONTENT_PRODUCTION_CS_REFERENCE_PROBE_INPUT_v0.1.md` |
| `content_brief` 取自 | `decision-chain/evidence/CONTENT_BRIEF_DEEPSEEK_V4_FLASH_RUN_001_FINAL.md` 第 0 节＋第 2 节 `BRF-SUHE-001` |
| `content_brief` 正文 SHA-256 | `4eb15a687e01f4f7844f1b925c60a302b290b43fe7b39d7963a9fadd24c028af` |
| `content_brief` 长度 | 4749 字符 |

九槽位实际取值（CONFIRMED_INPUT / PROBE_ONLY 分开标注）：

| 槽位 | 值 | 标注 |
|---|---|---|
| `production_profile` | 小团队 | PROBE_ONLY |
| `expression_subject` | NATURAL_PERSON | CONFIRMED_INPUT |
| `content_origin_mode` | 现拍 ＋ 已有素材剪辑 | CONFIRMED_INPUT |
| `subject_domain` | 服装 / 门店零售 | CONFIRMED_INPUT |
| `duration_band` | 短（≤60s） | PROBE_ONLY |
| `platform` | 小红书 | PROBE_ONLY |
| `cta_contract` | NO_CTA | CONFIRMED_INPUT |
| `account_positioning` | 苏禾＝独立参战账号／零售搭配负责人（含账号关系姿态） | CONFIRMED_INPUT |
| `constraints[]` | Brief 内五个约束字段全部生效 | CONFIRMED_INPUT |
| `example_reference_requested` | `false` | 任务书固定 |

三项 `PROBE_ONLY` 值**不代表业务已确认，未回写任何正式业务资产**。

`decision-chain/docs/序里集_CONTENT_BRIEF_GOLDEN_v0.1.md` 带 `GOLDEN_CANARY` 泄漏探针，文件本身写明不得进入任何模型可见内容，**已排除，未作输入**；本证据与探针输入均扫描确认 0 命中。

---

## 4. 投影加载结果

### 4.1 加载

- ✅ `content-production/skills/writing-creative-scripts/SKILL.md :: 全文（始终加载）`
- ✅ `content-production/references/platforms.md :: 二、结构性参数 —— Creative Script 也读这一节`
- ✅ `content-production/references/industry-conditions.md :: 服装 / 门店零售`

### 4.2 排除

- ⛔ `content-production/references/platforms.md :: 一、入口形态 —— 决定封面和首帧谁承担第一眼`
- ⛔ `content-production/references/platforms.md :: 三、画面安全区 —— Production Director 读这一节`
- ⛔ `content-production/references/platforms.md :: 四、字数与展示长度 —— Publishing & Packaging 读这一节`
- ⛔ `content-production/references/platforms.md :: 五、这张表里没有的东西`
- ⛔ `content-production/references/platforms.md :: 更新这张表的规则`
- ⛔ `content-production/references/industry-conditions.md :: 餐饮 / 门店`
- ⛔ `content-production/references/industry-conditions.md :: 知识付费 / 课程`
- ⛔ `content-production/references/industry-conditions.md :: 动漫 / 原创 IP`
- ⛔ `content-production/references/industry-conditions.md :: 户外 / 露营（爱好垂类）`
- ⛔ `content-production/references/industry-conditions.md :: 一条跨行业的提醒`
- ⛔ `content-production/references/examples.md :: 全文`

### 4.3 哈希

| 项 | SHA-256 |
|---|---|
| `SKILL.md` | `d0f78a480f58d494a29d3a34e35106ba0ff48719052361748ed513c721fc7b6a` |
| `platforms.md` | `98fa083c36710fc65f7d5fcf58fb6c33f14d3f984e07c014d7ab47fafe641d2d` |
| `industry-conditions.md` | `b085f1218a561adb500980464325c4356413187ee6e45be5430d5d1334fb7f6d` |
| `examples.md` | `635c86e11ab9bd4e6e1b1fb721b2e3929f8a57c8a18c64f57dc81d743228f3e5` |
| `platforms.md::loaded_section` | `f2c4a44097a6c22331e6ddcd5c3b79c3ab8adf1054db1ea2e53bd98d4bf1f49d` |
| `industry-conditions.md::loaded_section` | `6f968705682b1cad` |

### 4.4 投影理由

- SKILL.md 始终加载：Creative Script 的工作方法本体。
- platforms.md 只加载「二、结构性参数 —— Creative Script 也读这一节」：该节标题在 v0.6 原文中即写明由 Creative Script 读；一节入口形态、四节字数与展示长度归 Publishing & Packaging，三节画面安全区归 Production Director，均按表排除，不作判断。
- industry-conditions.md 按 subject_domain 精确字符串匹配加载单一行业块；未匹配则不加载，不选择最相近行业。本次 subject_domain = 服装 / 门店零售。
- examples.md 不加载：example_reference_requested = false；其正文未嵌入本工作流，物理上无法被加载。
- 投影全部由 Template Transform 查表完成，未使用知识库，未由任何 LLM 决定加载内容。

### 4.5 实际注入 LLM 的参考文本（1845 字符）

```markdown
## 参考投影 · platforms.md（只取「二、结构性参数」一节）
## 二、结构性参数 —— Creative Script 也读这一节

**这些数字改的不是包装，是内容能有几段。** 到包装阶段才发现超上限，是回退上游改结构，不是在这里删图。

| 平台 | 图文张数上限 | 长文字数上限 | 视频时长上限 | `as_of` | 来源 |
|---|---|---|---|---|---|
| **抖音** | **30 张**（长图文） | **8000 字**（长图文；2025-12-26 由内测 4000 字上调） | — | 变更 2025-12-26<br>核对 2026-08-22 | 中新网、新浪财经报道 |
| **小红书** | **18 张** | 未核实（常见说法 1000 字，另有 6000 字长文的说法，**两者都未核实，不要采用**） | 视频笔记 15 分钟 | 2026-05-30 | 色彩韵设计规格文档 |
| **视频号** | **20 张**（手机端；PC 端助手上传 18 张） | 未核实 | 手机端 3 秒–60 分钟（旧机型 30 分钟）；PC 端 3 秒–8 小时 | 变更 2024-04-08（官方帮助页更新日）<br>核对 2026-08-22 | 微信视频号官方帮助中心《视频号发表视频/图文有什么格式要求？》 |

**开放平台（OpenAPI）上传限制 —— 和 App 发布器不是同一件事：**

| 场景 | 单文件大小 | 视频时长 | `as_of` | 来源 |
|---|---|---|---|---|
| 第三方应用经**抖音开放平台**上传 | **≤128MB**（>50MB 建议分片、>128MB 必须分片；分片方式总文件 **≤4GB**） | **≤15 分钟** | 核对 2026-08-22 | 抖音开放平台《上传视频》`open.douyin.com/platform/resource/docs/openapi/video-management/douyin/create/upload/` |

**这一格只约束调接口发布的场景。抖音 App 端的视频时长上限仍然是「未核实」，不要拿这个 15 分钟去替。**
同页另写明「带品牌 logo 或品牌水印的视频……有比较大的概率导致分享视频推荐降权」——**这条直接约束封面与首帧选帧**。

**抖音那一格是近一年变化最大的一项。** 「抖音只能发短视频」这个默认前提在 2025-12 之后不成立了——同一批事实在抖音上可以走 30 张图 ＋ 8000 字，这会改变 Creative Script 的方向选择，不只是改变发布方式。

## 参考投影 · industry-conditions.md（只取 subject_domain 精确匹配的行业）## 服装 / 门店零售

| | |
|---|---|
| **常见素材形态** | 试穿视频（长、未剪、未编目）｜商品图（棚拍，干净但不带信息）｜陈列照｜空镜 |
| **哪一类真的带信息** | **只有试穿视频**。棚拍商品图在信息流里和所有服装广告长得一样，基本只能当背景 |
| **可用的真实摩擦** | 选品会上被否掉的款｜顾客原话｜同一件在不同体型上的结果差异｜退货理由｜"想留但成本算不过来" |
| **特有淘汰项** | **① 用成分推性能**——"70% 羊毛所以垂感好、不起球"。成分是事实，性能是结论，中间那一步没有来源。要说垂感，只能用试穿时观察到的动作（手一松塌不塌）<br>**② 无条件推荐**——"必买""闭眼入"<br>**③ 把条件句写成否决句**——"取决于内搭体积"不是"我劝你别买" |
| **拍摄条件** | 门店光是混色温的（射灯 ＋ 自然光），白平衡容易翻车｜试衣间退不开，广角畸变｜**"塌"和"挺"只有动态能看出来**，平铺图拍不出来，必须穿着状态下拍 |
| **包装差异** | 封面用**穿着状态**不用平铺；在点击型平台上，封面里那件衣服要能一眼看出是什么品类——认不出品类的封面等于没有封面 |## 参考投影 · examples.md

（本次 example_reference_requested = false；examples.md 未加载，其正文也未嵌入本工作流。）
```

**投影机制**：`Reference Projection` 与 `Projection Record` 两个 Template Transform 节点，按小节标题查表选取。未使用知识库，未由任何 LLM 决定加载内容。`platforms.md` 全部六个小节、`industry-conditions.md` 全部六个小节都嵌在模板里，由查表只选中该选的——因此「排除」是**真排除**，可在后台逐字复核。`examples.md` 正文**未嵌入工作流**，物理上无法被加载。

---

## 5. 六项验收结论

| # | 验收项 | 结果 | 判据 |
|---|---|---|---|
| 1 | 工作流成功运行并产生非空 Final | **通过** | status=succeeded final=7416 字符 |
| 2 | 只加载目标行业 reference 段落 | **通过** | 加载 ['content-production/references/industry-conditions.md :: 服装 / 门店零售']；其余四行业+跨行业提醒在实际 prompt 中 0 出现 |
| 3 | examples.md 没有加载 | **通过** | 投影与实际 prompt 中 examples 特征串 0 出现；正文未嵌入 DSL |
| 4 | Publishing 专属平台段落没有加载 | **通过** | platforms 的一/四节（PP）与三节（PD）在实际 prompt 中 0 出现 |
| 5 | 投影清单完整且可追溯 | **通过** | 四字段齐全；loaded 3 / excluded 11 / hashes 6 / reason 5；文件级哈希与基线 2ec2ba1 一致 |
| 6 | Final 未引用未加载内容，且未输出 Publishing 交付物 | **通过** | 未加载段落 0 引用；PP 交付物 0 出现；Final 无 think |

**6 / 6 通过。**

> 第 4 项的判据说明：`platforms.md` 的「一、入口形态」「四、字数与展示长度」两节在 v0.6 原文标题中即写明归 Publishing & Packaging，「三、画面安全区」归 Production Director。三节在**实际送入 LLM 的 prompt 全文**中 0 出现。

---

## 6. Final（用户可见产出，7416 字符）

```markdown
content_origin_mode[]         `["现拍", "已有素材剪辑"]` —— 逐 beat 见 script_beats 的「事实／素材」两栏；必须传给下游，PD 不得按纯现拍处理

creative_directions[]

**方向 A「过程复盘」（选中）**
- 核心矛盾：同一套组合在「会议成立」与「连续穿着偏正式」之间——C01 登记的真实不满足感
- 叙事发动机：调整过程本身的重演（保留 → 放松 → 脱西装比较），观众跟着走一遍
- 人物关系：苏禾带观众复盘记录；试穿人员是过程里的共同尝试者
- 信息释放顺序：身份边界 → 原始方案 → 摩擦 → 调整 → 保留 → 未验证
- 视觉前提：VID-C01 试穿素材为主体，苏禾旁白贯穿

**方向 B「摩擦先行」**
- 核心矛盾：正式与放松同时被需要，压在同一件衬衫上
- 叙事发动机：试穿中「觉得太正式」的那个瞬间作为引力点，再往回拆原因与解法
- 人物关系：试穿者（内部演示人员）第一人称在场，苏禾画外陪伴
- 信息释放顺序：感受先行 → 回拆 → 解法尝试 → 部分保留 → 边界
- 视觉前提：动作／反应特写优先，情绪在场感更强

**方向 C「边界先行」**
- 核心矛盾：内容能替你判断什么，与必须本人试过才知道什么——把「答不了」摆到最前面
- 叙事发动机：边界划线：先亮能力边界，再举证能答的部分
- 人物关系：苏禾对镜头直接声明，姿态是坦白的边界告知者
- 信息释放顺序：边界结论 → 证据 → 点名未验证变量 → 交给本人
- 视觉前提：苏禾正面出镜为主，试穿片段作证据插页

三轴判据：A 与 B 五轴全差；A 与 C 差四轴（仅「苏禾为口播主体」相近，但姿态不同：复盘引领者 vs 边界声明者）；B 与 C 五轴全差。

creative_concept

选中方向 A「过程复盘」，理由（指名判据，非「更抓人」）：
- **与 brief 强制叙事结构同构**：事实→摩擦→调整→保留→未验证，A 的发动机就是这条线；B 需把感受前置、C 需把边界前置，都违反 brief 给定的结构顺序。
- **接力需要**：下一条周宁要引用的是「苏禾的试穿观察」本身——A 让过程完整可见可引；B 压成感受、C 压成证据，都会让周宁失去可引用的过程。
- **账号姿态**：陪伴尝试、不急于给唯一答案——A 把结论压到最后一拍；B、C 都让结论前置，与姿态相反。
- **素材效率与风险**：主素材是 VID-C01 记录，A 全程以它为载体；C 依赖苏禾正面出镜（出镜方式未确认，风险高）；B 的最优剪辑是试穿者特写（被误读为真实顾客的风险最高，撞 brief 硬禁）。
- **落点一致**：A 的落点即 brief 的「唯一新判断」——正式程度可调，但肩部/袖长/裤长只能本人试穿确认。

audience_shift

让目标顾客从按单件新品和表面风格被动浏览，进展为能够用自己的一个真实穿着问题，套用「哪些问题能靠穿法调整、哪些必须本人试穿」的判断，作出初步比较或排除，并识别下一步需本人试穿确认什么。（上游给定）

content_promise

这条内容承诺：让观众看到一个已登记试穿记录里的调整过程，并明确切分出「能通过穿法调整」与「只能由本人试穿确认」两类问题。不承诺回答个人适配，不承诺这套组合适合所有人。

explicit_non_promise[] —— 全链只读继承，任何一段不得加东西回来
- 不承诺给出「这套组合适不适合你」的答案
- 不承诺肩部、袖长、裤长的适配判断
- 不承诺该组合适合所有会议、所有连续场景或任何具体人群（不适用于所有「职场妈妈」）
- 不承诺任何性能表现（防水／防风／抗皱／保暖／显瘦）
- 不承诺这是顾客见证或真实顾客经历
- 不承诺调整带来任何销售、偏好或经营结果
- 无 CTA：不承诺预约、到店、名额或其他行动结果

tension_mode

`UNVERIFIED`（六类强张力）——「试过了，还没定论」：试穿验证了正式感可调，但肩部/袖长/裤长的个人适配仍无定论，这是内容末尾刻意保留的未完成状态。
＋ 替代理由（与张力并存）：`Utility`（判断框架可复用：先分清「能靠穿法调」与「必须本人试」）＋ `Identity`（「白天开会、下班接孩子」正是目标顾客的连续一天）。
两个并存，不是二选一：张力负责看完，Utility 负责值得存，Identity 负责愿意转。

expression_subject

`NATURAL_PERSON` —— 苏禾（账号持续表达者，口播主体）＋ 内部演示试穿人员（画面主体，非表达主体）。
为什么：苏禾是 C01 事实确认人，判断有出处；试穿人员承担行动、不承担表达，避免她被误读为顾客。账号声音与观察记录分离。

opening

- 前 3 秒画面：VID-C01 中试穿人入镜的第一个有效镜头（选片判据：能看清「有人在试衣服」；不选任何可能被读成「顾客在抱怨」的表情或动作）；画面角落同帧出现「内部演示试穿 · 非顾客故事」标注。
- 逐字第一句（苏禾，画外）：「先说清楚——这是内部演示试穿，不是顾客故事。」

script_beats[]

本条 ≤60s，实际 4 段。brief 必表达为五步，身份标注并入 B1；每段状态变化见段内标注。无「停驻」段——结尾是向前交接的边界陈述，不是停下来的未完成。

**B1｜开场与身份边界**
- 事实：`有`——内部演示试穿，试穿人非现实顾客；「会议＋接送」为演示情境（brief 制作要求；C01 登记）
- 素材：`已确认`——VID-C01 试穿记录一开场可用段；苏禾出镜＝`待产出·可控`（可选，不阻塞本稿）
- state_change：**情境**（观众先知道这段是什么，防止把演示人员读成顾客）
- 逐字稿（苏禾）：「先说清楚——这是内部演示试穿，不是顾客故事。」「情境设定：白天开会，下班接孩子。」
- zone：准确区（身份与情境标注，逐字成立）

**B2｜原始搭法与真实摩擦**
- 事实：`有`——原始组合＝廓形西装＋垂感阔腿裤＋雾蓝棉混衬衫（B01/商品登记表）；初始问题＝完整组合满足会议场景，但连续穿着时层次偏正式（C01）
- 素材：`已确认`——VID-C01 完整组合／试穿过程片段 ＋ IMG-P01 三件商品图（识别用）
- state_change：**信息**（观众知道原始方案与已登记的摩擦；预期被轻微打断——这组合不是静态成立的）
- 逐字稿（苏禾）：「原本搭的是：廓形西装、垂感阔腿裤、雾蓝棉混衬衫。」「开会，成立。」「但试穿记录里记了一笔：连续穿下来，层次偏正式。」
- zone：准确区（组合与记录陈述）；「原本搭的是」「但」为发挥区连接

**B3｜调整过程与本次观察**
- 事实：`有`——调整过程＝保留西装和阔腿裤，放松衬衫领口袖口，比较脱下西装后的单穿效果（C01）；已确认观察＝同一组合正式程度可通过穿法调整（苏禾专业判断，基于 C01）
- 素材：`待检索`——VID-C01 内「放松领口袖口」「脱下西装单穿」两个子场景的可用性（记录整体已确认，具体子场景本环节未过片）；检索判据清单见下
- state_change：**理解**（正式与否不只由单品决定，穿法能调）＋ **判断**（同一组合可覆盖正式到放松的区间）
- 逐字稿（苏禾）：「调整不是换单品。」「西装和阔腿裤留着，只把衬衫领口、袖口放松一点。」「再脱掉西装，比了一下单穿效果。」「这组衣服的正式感，可以靠穿法往下调——但这是这次试穿里的观察，不是对所有人、所有场景的通用答案。」
- zone：动作事实＝准确区；「正式感可以靠穿法往下调」＝主观区（专业判断）；「这次试穿里」「不是对所有人、所有场景的通用答案」＝主观区限定语，**一个字都不能删**

**B4｜保留、未验证与接手**
- 事实：`有`——被保留＝西装和阔腿裤（C01）；待验证变量＝肩部、袖长、裤长仍需本人试穿，不能由内容直接回答（brief/C01）
- 素材：`已确认`——VID-C01 单穿效果或试穿人镜前检查片段；结论强度随 B3 检索结果联动（降级路径见检索判据清单）
- state_change：**判断**（什么成立了、什么没成立被明确切分）＋ **预期**（观众对「内容能回答什么」的预期被重置——这正是本条内容承诺）
- 逐字稿（苏禾）：「最后留下来的：西装，和阔腿裤。」「没被回答的：肩部、袖长、裤长。」「这三处合不合适，这条视频回答不了——得本人试穿。」「内容能把判断做到这儿。再往下，只能本人试过才知道。」
- zone：前两句＝准确区（C01 保留项与待验证变量点名）；第三句＝主观区判断，但按 `KNOWN_UNKNOWN` 处理（显式声明「这条内容不知道」是本条承诺的一部分，压过 `SUBJECTIVE`）；第四句＝发挥区收束，不改变事实边界

question_list[]

`NOT_APPLICABLE` —— 无「事实=无」的 beat。C01 记录完整，无需向人追问即能写死逐字稿。

检索判据清单（指向 B3 素材）

- 找什么：
  ① VID-C01 中「放松衬衫领口、袖口」的前后动作或可辨认的状态帧；
  ② VID-C01 中「脱下西装后单穿」的有效片段（能看到整体层次，正身或半侧身均可）。
- 找到算什么：
  ①②都在 → B3 逐字稿整体成立，「正式感可调」以完整观察呈现；B4「西装和阔腿裤被保留」由同段素材支撑。
  只有① → 执行 brief 降级：只保留「领口袖口放松」的调整，B4 结论强度降为「部分可调整」。
- 找不到怎么办：
  ①②都缺 → 用已确认照片＋口述补足调整过程（brief 降级条件）。
  无论降级与否，「肩部、袖长、裤长仍需本人试穿」（B4）必须保留——它是本条的判断落点。

skeleton

`NOT_APPLICABLE` —— 无「事实=无」的 beat，不需要等答案回来再重写。段落关系已由逐字稿锁定：B1 立身份边界 → B2 立事实与摩擦 → B3 走调整并给出有边界的观察 → B4 切分保留与未验证并交给本人。

voiceover[]

- VO-B1｜B1 全程｜苏禾（画外）：「先说清楚——这是内部演示试穿，不是顾客故事。」「情境设定：白天开会，下班接孩子。」
- VO-B2｜B2 全程｜苏禾（画外）：「原本搭的是：廓形西装、垂感阔腿裤、雾蓝棉混衬衫。」「开会，成立。」「但试穿记录里记了一笔：连续穿下来，层次偏正式。」
- VO-B3｜B3 全程｜苏禾（画外）：「调整不是换单品。」「西装和阔腿裤留着，只把衬衫领口、袖口放松一点。」「再脱掉西装，比了一下单穿效果。」「这组衣服的正式感，可以靠穿法往下调——但这是这次试穿里的观察，不是对所有人、所有场景的通用答案。」
- VO-B4｜B4 全程｜苏禾（画外）：「最后留下来的：西装，和阔腿裤。」「没被回答的：肩部、袖长、裤长。」「这三处合不合适，这条视频回答不了——得本人试穿。」「内容能把判断做到这儿。再往下，只能本人试过才知道。」
- 附注：B1/B4 可选真人出镜（对镜讲述同一逐字稿），口播与出镜共用文本，在 3 小时拍摄＋补录产能内安排。

screen_text[]

- S1｜B1 全程角落（不得晚于试穿人正面清晰入镜的画面）｜「内部演示试穿 · 非顾客故事」
- S2｜B2 三件商品图切换时，图内／图下｜「廓形西装」「垂感阔腿裤」「雾蓝棉混衬衫」
- S3｜B4 最后两句期间，屏幕下方｜「肩部 · 袖长 · 裤长 → 需本人试穿」

fact_refs[]

| 内容 | 来源 | type |
|---|---|---|
| 三件单品名称与品类（廓形西装／垂感阔腿裤／雾蓝棉混衬衫） | 商品登记表／B01，确认人周宁 | `EXTERNAL`（品类与登记事实可对实物核验） |
| C01 初始问题：完整组合满足会议场景，但试穿人认为连续穿着时层次偏正式 | C01 内部登记，确认人苏禾 | `INTERNAL`（有记录可查、外部核验不了） |
| 调整过程：保留西装和阔腿裤，放松衬衫领口袖口，比较脱下西装后的单穿效果 | C01，确认人苏禾 | `INTERNAL` |
| 已确认观察：同一组合正式程度可通过穿法调整（含不构成通用答案的边界） | C01，苏禾专业判断 | `SUBJECTIVE`（有出处，但不是外部事实；不得用画面强化） |
| 被保留：西装和阔腿裤 | C01 | `INTERNAL` |
| 待验证变量：肩部、袖长、裤长仍需本人试穿，不能由内容直接回答 | brief/C01，苏禾专业判断 | `KNOWN_UNKNOWN`（显式声明「内容不知道」是本条承诺的一部分，压过 `SUBJECTIVE`；主语＝这条内容／苏禾，非角色） |
| 内部演示身份与「会议＋接送」演示情境 | Content Brief 制作要求 | `INTERNAL`（有记录可查、外部核验不了；属制作指令层） |

evidence_requirements[] —— 交给 Production Director

1. B1：试穿画面首次出现时必须同帧或同段出现「内部演示试穿 · 非顾客故事」标注，不得晚于试穿人正面清晰入镜。
2. B2：IMG-P01 三件商品图只承担「被识别」，不得用商品图承载任何穿着效果或性能判断；「开会，成立」是已登记观察，画面不得用「会议成功」类示意把它放大成普遍结论。
3. B3：`SUBJECTIVE` 判断「正式感可调」——画面只呈现已登记动作（放松领口袖口、脱西装单穿）；禁止用音乐骤起、前后对比分屏、慢镜高亮等手段「证明」该判断；禁止把调整剪成惊人反转（brief 硬禁）。
4. B4：`KNOWN_UNKNOWN` 边界——画面只能呈现「这里没有答案」（如试穿人镜前查看肩部／袖长的动作），不得呈现「答案本该是什么」；不给试穿人的身体下任何评价（「肩宽不合适」「袖长刚好」一类一律不得出现）。
5. 全程：试穿人的可闻话语（如有）只允许来自 C01 已登记内容；C01 未登记的语句不得进入成片，剪辑前先核对。

resource_note

- 出镜与声音：内部演示试穿人员（画面主体，来自 VID-C01 已有素材）；苏禾（口播全程；若出镜，B1 或 B4 对镜讲述，在 3 小时拍摄＋30 分钟补录内安排）。
- 现有素材：VID-C01 试穿记录一原始片段（必须使用）、IMG-P01 三件商品图（必须使用）、BROLL-S01 门店空镜（仅转场，不承担判断）。
- 待产出：苏禾口播录音（3 小时拍摄内或补录完成）；（可选）苏禾出镜镜头。
- 接力说明：本条结尾的边界陈述即向周宁交出的问题（哪些需本人试穿）——成片中不得添加预告下一条或跨账号指引（无 CTA）。

constraints[]

- 不得把内部试穿人员描述为现实顾客；「会议＋接送」是演示情境不是真实顾客经历（B1 标注 + 全片不得违背）
- 不得将 C01 试穿记录与 D01 匿名问题拼接成同一顾客故事（本条只用 C01）
- 不得声称适合所有「职场妈妈」或任何具体适穿人群
- 不得补写防水／防风／抗皱／保暖／显瘦等未登记性能
- 不得声称调整后提高了销售或顾客更喜欢
- 不得把调整剪成惊人反转
- 不使用「显瘦」「闭眼入」「人人可穿」等话术
- 不出现预约成功、名额稀缺表述；本条无 CTA——不出现任何行动召唤（预约、到店、私信、评论引导）；统一承接说明不采用（如制作方坚持，先走上游确认，且不得替代判断价值）
- 不给试穿人身体下判断（肩部／袖长／裤长只说「需本人试穿」，不说「她合适／不合适」）
- 试穿人语音如与 C01 未登记内容冲突，不得使用

failure_case

会砸的那条方案：「惊喜改造版」——把 B3 的调整剪成一个前后对比的改造反转，结尾收成「这样就不正式了」。
为什么砸：输入只登记了「正式程度可以调整」，没登记「调整后就解决了」；收尾一旦删掉「肩部、袖长、裤长仍需本人试穿」那一半，等于替 C01 宣布了一个它没宣布的结论（CS-7 ⑥ 删掉记录的另一半）。同时「惊喜反转」结构会用画面把 `SUBJECTIVE` 判断（一次试穿里的观察）坐实成客观事实，恰好撞上 brief 的硬禁「不得把调整剪成惊人反转」。机制：CS-4 主观区被画面强化 ＋ CS-7 ⑥ 删减输入记录的后半段。

assumptions[]

- platform：输入槽位为小红书，但 brief 明确「最终发布平台未确认，由 Founder 锁定」——本稿按平台中立母版处理，时长 ≤60s 对所有候选平台成立；不进入平台规格设计。
- 苏禾出镜方式未定：本稿按「口播为主线、B1/B4 可选真人出镜」设计，两版共用同一逐字稿。
- 无真实顾客原话可用：C01 为内部演示记录，不是顾客故事；试穿人语音默认视为未登记，除非与 C01 核对。
- 单穿比较子场景的素材可用性按「待检索」处理，检索判据已给出。
- duration_band 短档（≤60s），实际使用 4 段。
- 出镜人身体信息不进入内容（不给试穿人身体下判断）。
- 无 `return_from_downstream[]` 回改建议。

missing[]

- 最终发布平台（Founder 锁定中；锁定前下游不做平台规格）
- 苏禾出镜方式（真人出镜或旁白）——brief 列在「进入脚本与拍摄设计前必须确认」事项
- 是否采用统一承接说明（建议不采用；如需，走上游确认）
- VID-C01 中「脱下西装单穿」子场景的可用性（检索判据清单已给；结果决定 B3/B4 结论强度）
```

---

## 7. 原始输出（含 reasoning，102464 字符）

> 以下为 LLM 节点未经切分的原始文本。Final 由 `</think>` 之后的部分提取，本段仅作证据保留，**不进入任何用户可见产物**。

````text
<think>
<!--dify-deepseek-reasoning-->The user needs me to produce a Creative Script for a short video (≤60s) for Xiaohongshu, with production_profile = 小团队 (small team), expression_subject = NATURAL_PERSON, content_origin_mode = 现拍 + 已有素材剪辑 (live shooting + existing material editing), subject_domain = 服装/门店零售, platform = 小红书, duration_band = 短 (≤60s), NO_CTA.

Let me analyze the Content Brief carefully:

- Account: 苏禾 (Su He), independent participating account, retail styling lead. This round: bring product judgment into real bodies and continuous life scenarios, verify/adjust/correct initial choices, explain which issues can be handled and which still need the person's own try-on. Account attitude: companion trying-on styling partner, doesn't judge the model's body first, doesn't rush to give a single answer.
- The brief is BRF-SUHE-001
- Content type: main short video, days 2-3
- Core narrative: Starting from specific facts — complete suit + shirt combo works for meeting scenarios; real friction appears — the try-on person feels the overall layering is too formal in continuous meeting + pickup scenarios; show adjustments — keep blazer and wide-leg pants, loosen shirt collar and cuffs, compare effect of taking off blazer; point out what's kept — blazer and wide-leg pants; point out what still can't be concluded — shoulder, sleeve length, pants length still need personal try-on.
- Key message: The formality of the same combination can be adjusted through styling, but body-fit issues (shoulder, sleeve length, pants length) cannot be confirmed via content alone, must be confirmed by personal try-on.
- Must express: This is an internal demo try-on; meeting + pickup is a demo scenario; how it was originally worn — blazer + shirt + wide-leg pants; what actual problem appeared — too formal in continuous wear; what adjustments — keep blazer and wide-leg pants, loosen collar and cuffs, compare single-wear effect without blazer; what's kept — blazer and wide-leg pants; what still can't be concluded — shoulder/sleeve/pants length need own try-on.
- Must NOT express: describe internal try-on person as real customer; splice C01 try-on record with D01 anonymous question into same customer story; claim suitable for all "working moms" or any specific group; add unregistered performance claims (waterproof, windproof, wrinkle-resistant, warm, slimming); claim adjustments increased sales or customers like it more; cut adjustment as shocking reversal; use "显瘦" "闭眼入" "人人可穿" catchphrases; no reservation success or scarcity expressions.
- No CTA. Optional: unified reception explanation as optional ending, but recommended not to add.
- The "会议与接送" scenario is an internal demo scenario, not a real customer story — must be clearly labeled in content.

Constraints from the brief:
- 明确不得表达 (must not express)
- 发布条件 (release conditions)
- 降级条件 (degradation conditions)
- 取消或不发条件 (cancel conditions)
- 事实、观察、专业判断与待验证变量的区分 (distinction between facts, observations, professional judgments, and variables to be verified)

Now let me think about the Creative Script output:

**Core judgments:**

CS-1: Creative directions — need 3 high-difference directions, each differing on at least 3 of 5 axes (核心矛盾｜叙事发动机｜人物关系｜信息释放顺序｜视觉前提)

Let me think about what's possible given constraints:
- The evidence chain is C01 try-on record one (meeting + pickup continuous scenario) + B01 comparison table
- Core: formality adjustable via styling, but body-fit (shoulder/sleeve/pants length) requires personal try-on
- No CTA, no "surprising reversal", internal demo try-on labeled clearly

Possible directions:

Direction A: 苏禾 herself walks through the try-on record — "reconstructing the adjustment process" — she narrates: originally we thought this combo works, then in continuous wear it felt too formal, so we adjusted. Engine = replay/demonstration of adjustment process. Relationship = 苏禾 explains to viewer like a colleague sharing process notes. Visual = try-on footage with voiceover.

Direction B: Focus on the specific moment of dissatisfaction — the try-on person's feeling "too formal" as the starting point. The "二选一" tradeoff: meeting formality vs. not-overly-formal pickup. Engine = unresolved tradeoff (UNRESOLVED_TRADEOFF). Carried by the try-on person herself (internal demo staff, not 苏禾). Relationship = companion trying with her.

Direction C: 苏禾 explains what CAN'T be concluded — the "what still requires your own try-on" angle. Inverting: instead of showing how it works, focus on the boundary of the content itself. Engine = knowledge boundary / known-unknown. This is interesting because the content's core judgment is precisely "some things can't be answered by content."

Let me evaluate these on 5 axes:

Direction A (调整过程重演):
- 核心矛盾: 完整组合在连续场景中偏正式 vs. 需要满足会议需要
- 叙事发动机: 重新演示调整过程（记录重演）
- 人物关系: 苏禾对观众——过程揭秘/复盘式
- 信息释放顺序: 原始方案 → 问题 → 调整 → 保留 → 待验证
- 视觉前提: 试穿视频 + 旁白

Direction B (那个"偏正式"的具体时刻):
- 核心矛盾: 同一组合两头难——正式 vs 放松
- 叙事发动机: 不满足感的现场体验（moment of discomfort）
- 人物关系: 试穿者本人视角（内部演示人员）——观众代入
- 信息释放顺序: 问题感受 → 尝试解法 → 部分成功 → 部分无解
- 视觉前提: 试穿者在镜头前，把"觉得太正式"的过程演出来

Direction C (内容不能回答什么):
- 核心矛盾: 内容能判断什么 vs 必须本人试穿才能判断什么
- 叙事发动机: 边界划定（boundary-setting）
- 人物关系: 苏禾对观众——诚实的边界声明
- 信息释放顺序: 先给结论边界 → 用试穿记录佐证 → 说明哪些可调整哪些不行
- 视觉前提: 试穿片段 + 苏禾面对镜头直接说

Hmm, let me check if these differ on at least 3 axes:

A vs B: 
- 核心矛盾: A is "formality vs meeting needs", B is "formal vs relaxed" — arguably similar but A is about the combo failing in one scenario, B is about the inherent tradeoff. A and B could be seen as close.
- 叙事发动机: A = replay/process, B = live experience of discomfort — different
- 人物关系: A = 苏禾 explains, B = try-on person's perspective — different
- 信息释放顺序: A = linear process, B = starts from feeling — different
- 视觉前提: A = voiceover over footage, B = try-on person present — different

That's 4 axes different, OK.

A vs C:
- 核心矛盾: A = combo too formal in continuous wear, C = what content can vs cannot determine — different
- 叙事发动机: A = process replay, C = boundary delineation — different
- 人物关系: A = 苏禾复盘, C = 苏禾对观众做诚实声明 — similar-ish (苏禾 to audience in both), but the posture differs (companion vs honest declarer). Hmm.
- 信息释放顺序: A = chronological process, C = claim-first then evidence — different
- 视觉前提: A = voiceover, C = 苏禾 face-to-camera + footage as evidence — somewhat different

At least 3 axes, probably OK.

B vs C:
- 核心矛盾: B = formal vs relaxed tradeoff, C = content vs body verification — different
- 叙事发动机: B = live discomfort experience, C = boundary-setting — different
- 人物关系: B = try-on person's perspective, C = 苏禾 direct address — different
- 信息释放顺序: B = feeling first, C = boundary first — different
- 视觉前提: B = try-on person POV, C = 苏禾 direct — different

Good.

Now, which to select? Given the brief's narrative structure explicitly ordered: from specific facts (combo works for meeting) → real friction (too formal in continuous wear) → show adjustments → what's kept → what can't be concluded, Direction A matches best. Also the manual explicitly says "叙事结构：从具体事实进入...出现真实摩擦...展示调整...指出被保留的部分...指出仍不能下结论的部分". So the brief prescribes a structure close to A. But wait — CS-1 says directions must be high-difference. Direction A is basically the brief's prescribed structure. B and C are alternatives that differ. But the brief is quite prescriptive. Let me think about whether B or C could be selected while still honoring the brief's requirements.

Actually, the brief's "叙事结构" is mandatory content order essentially. The must-express list requires: ① internal demo label, ② original plan, ③ problem, ④ adjustments, ⑤ what's kept, ⑥ what can't be concluded. That's a fairly fixed content skeleton. So the three directions must contain all these elements but arrange them differently (信息释放顺序 axis) — that's where the difference can be.

Let me refine:

Direction A "过程重演 / 复盘式": Starts with original plan → continuous wear problem → adjustment attempts → what stayed → what remains unverified. This is the brief's structure. 苏禾 as voice guiding through footage. The engine is "watch the process of us figuring it out."

Direction B "把不舒服的时刻放在最前面": Start with the try-on person's moment of dissatisfaction ("到了下午觉得整套太正式了") — actually convey the feeling first, then work backward: how we tried to fix it, what worked, what didn't. Engine = the felt problem as a portal. Carried by the try-on person (internal demo staff) front and center, 苏禾 as companion in frame. This differs in 信息释放顺序 (problem first, not plan first) and 人物关系 (try-on person primary).

Direction C "边界先行 / 先说不能回答什么": Open with the conclusion: "这条视频不会告诉你这件西装适不适合你" — because shoulder/sleeve/pants length can't be verified from content. Then use the try-on record as evidence of what CAN be judged (formality adjustability) vs what can't. Engine = honesty as the hook — the content's own boundary becomes the content. 苏禾 to camera, direct. This inverts the information release: instead of building to the boundary, start with it and prove it.

Now select: The brief's narrative structure matches A most directly. But is A the best? Let me think about what makes this content work for the audience, and the account positioning (陪伴尝试的搭配伙伴，不先评价试穿人身体，不急于给唯一答案).

The audience shift: from passively browsing new items, to being able to use the store's judgment framework (real-life scenarios, fit conditions, wardrobe efficiency) to describe their own real wear problem, make preliminary comparisons/exclusions, and identify what still needs personal try-on confirmation.

The core judgment to land: "同一组合的正式程度可以通过穿法调整，但肩部、袖长、裤长等身体适配问题不能仅凭内容确认，必须由本人试穿继续确认。"

The audience's卡点: they only see single-item photos or static styling, don't know what problems arise in continuous scenarios, which problems can be solved by styling, which must be confirmed by own try-on.

So the content's job is NOT to sell, NOT to show a perfect styling result, but to demonstrate a thought process: try → hit a problem → adjust → partial resolution → boundary. The "product" here is the judgment framework itself.

Which direction serves this best? Direction A does — it's a process narrative that models the judgment framework. B risks making the discomfort itself the product (which is closer to identity content, and could drift toward "职场妈妈太难了" territory which is forbidden). C risks being too meta/abstract for ≤60s, and the brief forbids "把调整剪成惊人反转" — C's "honesty as hook" could edge toward that.

Also consider: the try-on person is an internal demo staff member, NOT a real customer. The relationship axis must be handled carefully: the audience shouldn't be made to think this is a real customer's story. Direction A (苏禾 as protagonist/narrator, try-on footage showing the demo) naturally supports the labeling — the try-on person is the internal demo staff, 苏禾 is the one walking through her own observation. Direction B (try-on person primary) risks the viewer mistaking her for a real customer. Actually the brief says the try-on person must be labeled — both directions can handle it, but A makes it cleaner.

So: Direction A selected.

Why: The brief's own narrative structure, plus the "给周宁交问题" handoff needs the process to be visible, and the account positioning (not evaluating the body, not rushing to a single answer) is best embodied by accompanying the try-on person through the process rather than presenting a verdict.

Hmm wait, but CS-1 says don't just make direction A the brief's structure and B/C variants. Let me make sure the three directions are genuinely different.

Actually, let me reconsider. The 5 axes:

A "记录重演·苏禾复盘":
- 核心矛盾: 完整组合在连续场景中偏正式（需要正式的会议 vs 不想过于用力）
- 叙事发动机: 调整过程的逐步重演（keep-cut: 保留西装阔腿裤、放松领口袖口、脱西装单穿）
- 人物关系: 苏禾作为复盘者带观众看过程；试穿人员在镜头内是"被观察的对象+共同尝试者"
- 信息释放顺序: 初始方案 → 摩擦 → 调整 → 保留 → 未验证
- 视觉前提: 素材剪辑为主，苏禾旁白或出镜串场

B "摩擦先行·那一瞬间的不满足":
- 核心矛盾: 两件都想要（正式与松弛）不可兼得
- 叙事发动机: 试穿者亲口说出"太正式了"的那一刻，作为整个内容的引力点
- 人物关系: 试穿者（内部演示人员）第一人称主体；苏禾是画外/画面内的陪伴者
- 信息释放顺序: 问题感受 → 往回找原因 → 试解法 → 部分成立 → 边界
- 视觉前提: 试穿者面部/身体反应特写优先，苏禾陪伴出镜

C "边界先行·这条视频不回答什么":
- 核心矛盾: 内容能替你判断什么 vs 必须本人试过才知道
- 叙事发动机: 边界划线——先亮出"肩部袖长裤长我答不了"，再展示哪些能答
- 人物关系: 苏禾直接对镜头，以专业身份做诚实声明；试穿素材作为证据出现
- 信息释放顺序: 结论边界 → 能答的部分（试穿过程） → 不能答的部分点名 → 交给本人
- 视觉前提: 苏禾正面出镜为主，试穿片段作为插页证据

Check pair differences:

A vs B:
- 核心矛盾: "组合在场景中偏正式" vs "正式与松弛不可兼得" — these are subtly different: A frames it as a scenario-fit problem (combo vs continuous scenario), B frames it as an inherent tradeoff. Different.
- 叙事发动机: 复盘/重演 vs 现场不满足感 — different.
- 人物关系: 苏禾主导复盘 vs 试穿者第一人称 — different.
- 信息释放顺序: 原始方案起点 vs 问题起点 — different.
- 视觉前提: 素材+旁白 vs 试穿者特写+陪伴 — different.
5 axes differ. Good.

A vs C:
- 核心矛盾: different (scenario fit vs content boundary)
- 叙事发动机: different (process replay vs boundary marking)
- 人物关系: 苏禾复盘 vs 苏禾直接声明 — arguably similar (both 苏禾 to audience); but posture differs: A is "let me show you what we found", C is "I'm telling you what I can't tell you". I'd call this different enough.
- 信息释放顺序: different (process-liner vs boundary-first)
- 视觉前提: different (voiceover over footage vs face-to-camera)
≥3 axes. Good.

B vs C:
- 核心矛盾: different
- 叙事发动机: different
- 人物关系: 试穿者主体 vs 苏禾主体 — different
- 信息释放顺序: different
- 视觉前提: different
Good.

Selection: A. Rationale needs to cite specific criteria: the brief's required narrative structure (事实→摩擦→调整→保留→未验证) is itself the process-engine; B risks the audience reading the internal demo staff as a real customer (identity confusion conflicts with mandatory labeling); C's boundary-first needs the audience to already trust 苏禾's judgment before the evidence arrives — in a 60s single video, the boundary claim without the process would feel like a disclaimer, and the brief forbids presenting the adjustment as a reversal ("不得把调整剪成惊人反转"), which C's honesty-as-hook could drift toward. A best serves the handoff to 周宁 (the process must be visible for 周宁 to reference).

Actually, I should be careful: the brief says 不得把调整剪成惊人反转 — Direction C isn't necessarily a reversal, but its "先说不能回答什么" could be read as a twist-y structure. Fine.

CS-2: Tension.

The real friction: 试穿人在连续场景中觉得"完整西装＋衬衫"偏正式。这是已登记的真实调整起点；不是虚构反转，只是试穿过程中实际出现的不满足感。

Tension types: This is... 未验证的判断? UNVERIFIED: "试过了，还没定论" — yes, the try-on was done, the adjustment was tried, but the final verdict is explicitly NOT given (shoulder/sleeve/pants length still need personal try-on). Also there's an element of UNSETTLED_DEBT? No. UNRESOLVED_TRADEOFF (formal vs relaxed both desired)? The brief says "完整西装+衬衫组合能满足会议场景，但在连续穿着中层次偏正式" — and the resolution was partial: adjust formality but body-fit questions remain. The tradeoff IS resolved to a degree (formal enough for meetings after adjustment), but the body-fit issue is left open. 

Which is primary? The brief says the decisive tension is: "试穿人在连续场景中觉得'完整西装＋衬衫'偏正式" — this is a mismatch between intent (formal enough) and experience (too formal), which the adjustment resolves partially. The remaining open state is: 肩部/袖长/裤长仍需本人试穿 — this is "tried a bit but cannot be concluded from here" = UNVERIFIED. I'll fill UNVERIFIED as the tension mode. 

And the alternative consumption reason: Identity (这说的是我 — the target audience's exact situation: meeting + pickup, wanting formal but not overly stiff) and/or Utility (the adjustment method is actionable). The brief's audience卡点: they don't know what problems arise and which can be resolved by styling. Utility: they can reuse the judgment framework (formality adjustable via styling, fit issues need try-on). Identity: the specific scenario (白天会议、下班接送孩子) is the target customer's own life.

I'll fill both: tension = UNVERIFIED, alternative = Utility (primary, because the brief's唯一顾客变化 is about enabling them to judge/compare/exclude) + Identity as secondary. Actually the schema says "两个可以并存" — 张力 + 替代理由. Within 替代理由 I can note both Utility and Identity. Let me list tension_mode: UNVERIFIED (tension) + Utility &amp; Identity (alternative reasons). Hmm, format: "tension_mode 六类强张力之一，和／或五类替代理由之一；两个可并存". I'll write something like: `UNVERIFIED`（试过了，调整后正式程度有结论，但肩部/袖长/裤长仍无定论）＋ `Utility`（可复用的判断框架）`Identity`（这就是目标顾客的连续场景）.

CS-3: Beat structure with state changes.

Given ≤60s. Let me design beats. The brief's narrative structure: ①具体事实进入（组合在会议场景成立）②真实摩擦（连续场景偏正式）③展示调整（保留西装阔腿裤，放松领口袖口，比较脱西装单穿）④被保留的部分（西装和阔腿裤）⑤仍不能下结论（肩部、袖长、裤长）。

Also must include: 内部演示标注 — where does the "内部演示" label go? Probably early (opening beat) and/or repeated. The brief says 内部演示试穿身份与情境设定需以字幕或口播形式标注.

Let me draft a beat structure for ≤60s. 4-5 beats maybe. Short档 typically 2-3 beats per the skill, but "不设固定段落数量...以内容需要为准". For 60s, I'd say 4 beats max.

Let me draft:

Beat 1 — 起点与身份标注 (state change: 情境 — establishes that this is an internal demo, not a real customer story):
- 事实: 内部演示试穿；演示情境为"会议＋接送"连续场景
- 素材: 已确认 (VID-C01 试穿记录一原始片段)
- State change: 情境 (viewer knows what this is and the frame)
- Content: Must clearly mark: 内部演示试穿人员 + 演示情境. Voiceover or on-screen text.
- Zone: 准确区 (the label must be accurate word-for-word in meaning)

Draft: 苏禾口播/字幕:「不是顾客见证。这是我们内部的试穿记录——演示的是一位白天开会、下班要接孩子的状态。」

Hmm wait — should I be careful about "演示的是一位白天开会、下班要接孩子的状态"? The brief says "'会议与接送'是演示情境，不是真实顾客经历". So saying "演示的是…状态" is fine. But "一位白天开会、下班要接孩子的状态" — the try-on person may not herself be a parent; it's a scenario being simulated. So phrase: 「这是我们内部演示试穿。演示情境：白天开会、下班接孩子。」 That's fine.

Beat 2 — 初始方案与摩擦 (state change: 信息 + 预期 maybe):
- 事实: 完整西装＋衬衫组合满足会议场景；试穿人认为连续穿着时层次偏正式
- 素材: VID-C01
- State change: 信息 (viewer learns original plan + the unexpected friction) — and 预期 (viewer might expect static styling to work; here it's shown to have a problem)
- Zone: 准确区 for the friction claim (it's a registered observation from C01)

Draft: 苏禾:「原先的思路是完整一套——廓形西装、垂感阔腿裤、雾蓝衬衫。会议场景成立。但连续穿着到下午，试穿人的真实反应是:层次偏正式了。」

Wait — "连续穿着到下午" — is "下午" in the input? The brief says "会议与接送连续场景" and "连续穿着时层次偏正式". No time of day specified. Don't add 下午. Just: 「但放进'开完会再去接孩子'这个连续场景里，试穿人觉得整套偏正式了。」

Actually careful: the scenario is 会议→接送. The friction: 连续穿着时整体层次偏正式. So: 「试穿记录里原话：'会议场景成立，但连续穿着时层次偏正式。'」 Hmm, is that a real quote from C01? The brief says "试穿记录一'会议与接送连续场景'的存在及初始问题（完整西装＋衬衫组合满足会议场景，但试穿人认为连续穿着时层次偏正式）". So the initial problem is registered as this. I can paraphrase: 完整西装＋衬衫，会议没问题；但试穿人自己的感受是，连续穿下来这一身偏正式。 That's a fact (registered observation), zone 准确区.

Beat 3 — 调整过程 (state change: 理解 + 判断):
- 事实: 调整过程——保留西装和阔腿裤，将衬衫袖口与领口处理得更放松，比较脱下西装后的单穿效果
- 素材: VID-C01 (调整过程原始片段)
- State change: 理解 (viewer understands that formality is adjustable via styling choices) + 判断 (same combo can be both formal and more relaxed depending on styling)
- Zone: 准确区 for the adjustment actions (registered), 主观区/发挥区 for how 苏禾 frames it

Draft: 「我们没换衣服。保留西装和阔腿裤，只把衬衫领口解开一颗、袖口翻松一点；再比较脱掉西装单穿的效果。同一个组合，正式的程度确实可以调。」

Wait — "领口解开一颗" — is that in the input? The brief says "放松衬衫领口和袖口". "解开一颗" adds specificity not in the input. Don't add. Just: 「只放松了衬衫的领口和袖口」。Also "我们没换衣服" — is that accurate? The adjustment kept blazer and pants, so shirt remained, blazer stayed on? Actually it says "保留西装和阔腿裤，将衬衫袖口与领口处理得更放松，并比较脱下西装后的单穿效果" — so the blazer was kept (worn), pants kept, shirt adjusted, and additionally compared the effect of taking off the blazer. So "没换衣服" is roughly right but hmm — "没换衣服" might imply they kept the same outfit throughout which is true (same three pieces, just adjusted). But to be safe, don't say "没换衣服" as a dramatic claim; say what actually happened.

Beat 4 — 保留与边界 (state change: 判断 + 预期):
- 事实: 被保留的部分——西装和阔腿裤；仍不能下结论——肩部、袖长、裤长仍需本人试穿
- 素材: VID-C01 (脱西装单穿效果) / 已确认商品图 maybe
- State change: 判断 (what's kept, what's the limit) + 预期 (viewer now knows that this content can't answer fit questions — and that's the point; reframes expectations about what content can do)
- Zone: 准确区 for the unverifiable variables; the "仍需本人试穿" is a待验证变量 — it's a professional judgment (from 苏禾) that these cannot be confirmed via content. Type: SUBJECTIVE or INTERNAL? Let me think. "肩部、袖长、裤长仍需本人试穿" — this is stated in the brief as 待验证变量；不能由内容直接回答. Its source: professional judgment by 苏禾. It's not externally verifiable, it's not an observation from the try-on record per se... Actually it's a professional judgment: "待验证变量'肩部、袖长、裤长仍需本人试穿'：待验证变量；不能由内容直接回答。" So fact_refs type: SUBJECTIVE (本人/专业判断) — it's 苏禾's professional judgment with a source (the brief), not an external fact. Hmm, but wait — is it "本人的感受或判断"? It's 苏禾's professional judgment. The INTERNAL type is "有记录可查、但外部核验不了". The brief is the record. Hmm. Actually let me look at the brief's 证据地图: "待验证变量...：待验证变量；不能由内容直接回答。" This is essentially a professional conclusion from C01 — 苏禾 observed that during the try-on, the formality was adjustable via styling, but shoulder/sleeve/pants fit can't be judged from content. I'd type it SUBJECTIVE (professional judgment with source, not external fact) — and per the skill, 不得用画面强化. Actually wait — should the statement "肩部、袖长、裤长仍需本人试穿确认" be strengthened by images? It's a claim about what can't be known — the skill says SUBJECTIVE 不得用画面强化. But also it's kind of a KNOWN_UNKNOWN: 苏禾 knowingly states these variables cannot be determined from content. Hmm. KNOWN_UNKNOWN is "显式声明'我不知道 X'". Here the content explicitly declares that shoulder/sleeve/pants fit cannot be confirmed by content — that IS an explicit declaration of "we can't know from here". The brief says "待验证变量". 

Hmm, per the skill: KNOWN_UNKNOWN "允许且应当用画面强化——这是内容的一部分，不是缺失" and priority rule: KNOWN_UNKNOWN 压过 SUBJECTIVE. But wait, is this 苏禾 saying "我不知道具体数据", or is it a professional judgment "these require personal try-on"? Let me parse: "肩部、袖长、裤长仍需本人试穿" = for these three fit dimensions, this content cannot determine the right answer; the wearer must try on. This is both a declared limit of knowledge AND a professional judgment. Per priority rule, KNOWN_UNKNOWN wins because "我不知道" (content can't answer) is part of the content promise. But the 边界 rule: 画面只能呈现"这里是空的"，不得呈现"空的地方本来该有什么". So for the beat where we say shoulder/sleeve/pants length need personal try-on: the image can show... hmm, what? The try-on person gesturing at her shoulder? No — that could be seen as presenting the empty space with content. The safe image: the try-on person checking the shoulder seam in the mirror (looking, not concluding), or simply the footage ending, or 苏禾 hands gesturing "these I can't answer". Actually — showing the shoulder of the garment on the person: is that "presenting where the verification is needed"? The skill says KNOWN_UNKNOWN should be strengthened by image — "这是内容的一部分". The boundary is: don't show "空的地方本来该有什么" meaning don't have the image imply a conclusion. Showing footage of the try-on person looking at her own shoulder fit — that's presenting the locus of the unknown, not filling it. Actually, strictly: "呈现'这是空的'" — the image should show that this is undetermined. A shot of the try-on person tugging/mirror-checking the shoulder, with the voiceover "肩部到底合不合适，这条视频回答不了" — the image shows the act of checking, the VO states it's unanswered. That seems fine and even desirable.

Hmm, let me reconsider. The brief says "待验证变量'肩部、袖长、裤长仍需本人试穿'：待验证变量；不能由内容直接回答。" and the 强制 requirement is "什么仍不能下结论——肩部、袖长、裤长仍需本人试穿". So the content must express this. The type: I'll go KNOWN_UNKNOWN (压制 SUBJECTIVE) — with the boundary note. Actually, wait. Let me re-read the priority: "「我到现在也说不清，是 A 还是 B」既是本人的判断，也是显式的不知声明——按 KNOWN_UNKNOWN 处理". This fits: "肩部、袖长、裤长仍需本人试穿" is both 苏禾's professional judgment and an explicit "content cannot know this". So KNOWN_UNKNOWN. Good.

But careful: the KNOWN_UNKNOWN subject rule: "虚拟内容里 KNOWN_UNKNOWN 的主语必须写明" — this is not fictional, it's real-life content. Still, I should make clear WHO doesn't know: 苏禾/这条内容 doesn't know; the wearer's own body fit can only be determined by trying on. Fine.

Now also: is the adjustment process a 准确区 or 发挥区? The registered facts: 调整过程 = keep blazer + wide-leg pants, loosen shirt collar &amp; cuffs, compare blazer-off effect. These are registered observations from C01 — INTERNAL facts, must be stated accurately. The narration around them (how to phrase, connecting words) is 发挥区. The observed result "正式程度可以通过穿法调整" is 已确认观察 = 专业判断 from C01 — SUBJECTIVE per the brief's own classification ("已确认观察...：专业判断，基于 C01 已登记试穿观察；确认人苏禾"). So it's SUBJECTIVE — 不得用画面强化. Hmm, but the footage of the adjustment IS the evidence... Wait, the distinction: the ADJUSTMENT (what was done) is an INTERNAL fact (registered observation of actions). The CONCLUSION "formality can be adjusted by styling" is a professional judgment based on that observation — SUBJECTIVE. So when I show footage of the adjustment and say "正式的程度确实可以调" — the conclusion itself must not be image-strengthened beyond showing the actions. Actually the actions are shown (that's fine, the fact), and the VO states the conclusion. The skill says SUBJECTIVE 不得用画面强化 — i.e., don't add a dramatic cut/emphasis that turns the subjective judgment into an objective-looking fact. Showing the actual registered actions is showing the facts; the VO carries the judgment. I'll note this in evidence_requirements: the conclusion "formality adjustable" is a professional judgment — do not add image emphasis (e.g., no dramatic "voilà" moment, no before/after split-screen with music swell). The brief reinforces: 不得把调整剪成惊人反转.

Now beats. Let me think about duration: ≤60s, Xiaohongshu. 4 beats might be tight but doable. Actually the skill says 短档 usually 2-3 segments. Let me see if I can do 3 beats:

Beat 1 (情境 + 信息): Internal demo label + original plan (blazer + shirt + wide-leg pants) + the friction (meeting OK, continuous wear feels too formal). State changes: 情境 (frame established), 信息 (original plan + registered friction).
Beat 2 (理解 + 判断): The adjustment — keep blazer &amp; pants, loosen collar &amp; cuffs, compare blazer-off. State: 理解 (formality is in the styling, not just the pieces) + 判断 (same combo adjusts).
Beat 3 (判断 + 预期): What's kept (blazer &amp; wide-leg pants survive), what's not concluded (shoulder/sleeve/pants length need own try-on), and the meta-point: some questions content can't answer — which reframes the viewer's expectation (预期) and gives them the framework. 

Hmm, but the meta-point "有些问题无法仅凭内容回答" is the core of the content's 唯一新判断. Let me make beat 3 carry it. Actually, is 4 beats better? Let me consider: Beat 1: label + plan. Beat 2: friction. Beat 3: adjustment. Beat 4: kept + boundary + handoff. That's cleaner for state-change accounting. At ~12-15s per beat in a 60s video, 4 beats is fine. The skill says "通常 2–3 段" for short but "以内容需要为准，在输出里声明实际用了几段". Four beats with the brief's explicit 5-part structure compressed. Actually let me think about whether to merge label into beat 1 and friction into beat 2 or keep them separate.

Let me go with 4 beats:

B1 — 情境 (frame): Internal demo try-on, demo scenario = meeting + pickup. State change: 情境.
B2 — 信息 (original plan + registered friction): Full blazer+shirt+pants for meeting works; the try-on person's own reaction: too formal in continuous wear. State change: 信息 (and arguably 预期 — the viewer learns the combo isn't a static slam-dunk).
B3 — 理解+判断 (adjustment): Keep blazer &amp; pants; loosen shirt collar &amp; cuffs; compare blazer-off. State change: 理解 (formality is adjustable through styling), 判断 (the same combo spans formality levels).
B4 — 判断+预期 (boundary + handoff): What's kept (blazer &amp; wide-leg pants); what can't be concluded (shoulder, sleeve, pants length — personal try-on required); and the reframe: this content can take you to the door but not through it — which resets expectations and hands the viewer a framework. State changes: 判断, 预期.

No 停驻 (Pause) needed — the ending is not an unresolved aesthetic ending; it's a deliberate forward-pointing boundary. Fine.

CS-4: Zones per beat.

B1: 准确区 — the internal demo label. Exact phrasing matters (it's a compliance/authenticity marker). Must not be paraphrased into something that sounds like a real customer.
B2: 准确区 for facts (original combo, registered friction). The connecting transition can be 发挥区. E.g., 「先说原本的搭法」 is 发挥区 connective; the fact statements are 准确.
B3: 准确区 for the adjustment actions (registered). The framing/evaluation is 主观区/发挥区. The conclusion "正式程度可调" is SUBJECTIVE — 措辞可改，理由不可改. The reason: the observed comparison (collar/cuffs loosened + blazer-off still read as appropriate for the scenario). Hmm, the exact "理由" — what makes it subjective-zone? The judgment "正式程度可以通过穿法调整" is the professional judgment; its basis is the registered try-on observation. When voicing it, the 限定语 matters: it's based on this one try-on, "这一次里" / "在这组试穿里". The skill's SUBJECTIVE rule: 限定语算"理由"，不算"措辞" — "至少在我们自己这一次里" 这类词一个字都不能删. So I must include hedges like 「在这次试穿里」「至少在我们这一组里」. Good — that also aligns with the brief: "这并不构成对所有人和所有场景的通用答案".

B4: 准确区 for "保留西装和阔腿裤"; KNOWN_UNKNOWN for "肩部、袖长、裤长仍需本人试穿". The statement "这条视频回答不了你肩部合不合适" — that's the content's promise boundary, 准确区/主观区. Its source is 苏禾's professional judgment (待验证变量) — SUBJECTIVE→KNOWN_UNKNOWN priority. When saying it, the限定语: "仅凭这一条内容" is essential.

CS-5: 口语化 — natural short sentences, pauses, corrections, no template phrases, no 书面词. I'll write the draft script accordingly.

CS-6: content_origin_mode = 现拍 + 已有素材剪辑.
- 事实: mostly 有 (registered facts from C01, B01). 
- 素材: VID-C01 原始片段 = 已确认 ("必须使用的素材：VID-C01 中试穿记录一原始片段"). IMG-P01 商品图 = 已确认? The brief says 必须使用: IMG-P01 中 XQ-2501/2502/2503 已整理商品图. Are they "已确认"? They're 已整理 (organized), specified as required. I'd mark as 已确认 (they exist and are specified). Maybe mark as 待检索 if unviewed — but brief says 已整理, and required. I'll default to 已确认 with a note.
- Are there any beats with 事实=无? The 苏禾 出镜方式 (真人出镜或旁白) is listed as "进入脚本与拍摄设计前必须确认的事项" — so the delivery format isn't fully locked. Hmm. The brief says "苏禾出镜方式（真人出镜或旁白）需在现有 3 小时拍摄＋补录产能内安排". This is an open parameter. In the script I should design for voiceover/PIP hybrid perhaps, or flag it. Since content_origin_mode includes 现拍, and 苏禾 can be shot (she's the account's ongoing voice and the shooting is within her capacity), I can assume she can do a short face-to-camera opening/closing as part of the 3-hour shoot. But the brief explicitly lists it as "必须确认的事项" — meaning it's not decided. I'll design the script to work in a flexible way: 苏禾 as voiceover throughout + optional brief face-to-camera in B1 or B4, and note in resource_note/assumptions that the camera presence is conditional. Actually — wait, "必须确认" means before shooting it must be confirmed. For the Creative Script, I can either ask or proceed with a default while flagging. Per input rules: "缺了不要卡住，但也不要闷头猜" — 对话里被调用, ask if the guess being wrong would redo the whole thing. Would the 出镜方式 choice break the script? If 苏禾 is VO-only, the script works (VO + footage). If she's on camera, the script works too (she speaks to camera in intro/outro). Both work — the script can be written to work either way with a small adjustment. So I don't need to block; I'll note it in assumptions/missing and design for VO-first with optional camera presence noted. Actually the brief says "苏禾作为账号持续表达者可以出镜说明或旁白解释调整与判断" — so both are permissible. I'll write the script primarily as VO (since test footage VID-C01 is the visual skeleton) with B1 optionally face-to-camera. I'll flag it.

Also: 最终发布平台未确认 — but platform slot says 小红书. Wait, the input has platform: 小红书, but the brief says "最终发布平台未确认；最终发布平台由 Founder 锁定". The input's platform field says 小红书. Hmm. The upstream status says READY_WITH_CONDITIONS with 最终发布平台未确认. The platform field given to me says 小红书 — but the brief explicitly says the final platform is NOT confirmed and "最终发布平台未确认前，不进入平台规格的逐镜头、秒数与格式设计" (that's a PD concern mostly). Also CS-6/CS-7: the production gate says "进入脚本与拍摄设计前必须确认的事项：最终发布平台". Since platform is listed as 小红书 in my input but the brief says unconfirmed, I should honor the brief's condition: don't do platform-specific beat/shot design; treat as platform-neutral master that happens to be under 60s (which fits 小红书 anyway). I'll note: platform applied 小红书 as given, but final platform is Founder-locked per brief; no platform-specific specs in this script. Actually — the platform: 小红书 from input. The 结构性参数 say 小红书 has no strict short limit for video, 15-min cap for video notes. ≤60s is fine. But since the brief says not confirmed, I'll flag in assumptions that I treated 小红书 as target but kept master platform-neutral. Hmm, the instructions say: "platform: 抖音／视频号／小红书，或未锁定 — 默认平台中立母版". Given the conflict (input says 小红书, brief says unconfirmed), the safest: treat as platform-neutral master with 小红书 as likely target; note that per brief, final platform pending Founder. Since duration ≤60s fits all, no structural impact. I'll put it in assumptions.

Now — the "苏禾出镜方式"待确认 and platform待确认 are the two 待确认事项 that matter for script. Both are noted; neither blocks the script.

CS-7: No fabrication. Let me check my draft lines for fabricated specifics:
- Don't add "下午", "一颗扣子", "三家店", customer identities, times, etc.
- The "会议与接送" scenario is a demo scenario — label it.
- The try-on person is internal staff — don't call her 顾客, 职场妈妈, etc.
- No performance claims (no 显瘦, no wrinkle-resistance).
- No "调整后客人更喜欢了" or sales claims.
- The tradeoff/partial resolution: the brief's registered record says formality adjusted; body-fit left open. So tension_mode should NOT be UNRESOLVED_TRADEOFF in the sense of "we couldn't resolve" — the formality tradeoff WAS partially resolved (kept blazer+pants, adjusted shirt, compared off). The unresolved part is the fit variables → UNVERIFIED. Good, consistent with brief: "只要...仍能被事实支持，就应保留". 

Wait, CS-7 ⑥: "输入记录了两侧结果的，删掉一侧和编造一侧是同一件事" — the C01 record includes both the success (meeting scenario works, adjustment works for formality) AND the not-success (body fit unverified). My script keeps both. Good. Also "不得用「解决了」收束" — my script must not say "所以这个问题解决了". It must say formality partially adjusted, fit remains for本人试穿.

Also禁止比较级评价 when not in input: "正式程度可以通过穿法调整" is in input as 已确认观察. Fine. "更值得" — no.

Also 不得把 D01 匿名问题与试穿记录拼接成同一顾客故事 — my script only uses C01. Good. Don't quote D01.

Also 不出现预约成功或名额稀缺表述 — no CTA, no scarcity. Good.

Also 账号关系姿态: "不先评价试穿人身体" — my script must not say "你肩宽所以选这个" or judge the try-on person's body. When mentioning shoulder/sleeve/pants length, frame as "这些要看个人身体，不是内容能替你判断的" — NOT "这位试穿人员肩部哪里不合适". Good. Actually the VO should be careful: don't say "试穿人肩宽袖子短" — no diagnosis of her body. Only: these variables require personal try-on to confirm. The footage may show her checking the shoulder in the mirror (the act of checking), but no VO diagnosing her fit. I'll note this in constraints/evidence_requirements.

Now let me think about the actual script text. ≤60s, Xiaohongshu, 苏禾 VO + VID-C01 footage.

Let me draft:

B1 (~8s) — 情境:
画面: VID-C01 中试穿人整理衣领的镜头 / 或苏禾出镜(可选).
字幕/口播: 「先说明：这不是顾客见证。是内部演示试穿——演示的情境：白天开完会，再去接孩子。」
Zone: 准确区 (identity label exact).

Hmm, "顾客见证" — the brief says 不得把内部试穿人员描述为现实顾客. The label could be: 「这段不是顾客故事。」「是内部演示试穿——试穿人是我们自己人，场景是演示出来的：会议＋接送。」 "我们自己人" — accurate (内部演示人员). Let me refine: 「先说清楚：这是我们内部的演示试穿，不是顾客故事。」「演示情境：白天有会，下班接孩子。」 That's clean. The try-on person's identity: 内部演示试穿人员 — don't need to name her. She's not 苏禾 presumably (苏禾 is the account, 出镜人或旁白; the try-on person is a separate internal demo person). Actually re-read: "出镜人为内部演示试穿人员，明确不是现实顾客；苏禾作为账号持续表达者可以出镜说明或旁白解释调整与判断". So two people potentially: the try-on person (in footage, not the account voice) and 苏禾 (VO or on-camera). The try-on person might speak in the footage — is there a registered quote from her? The brief doesn't quote her directly — C01's initial problem is paraphrased ("试穿人认为连续穿着时层次偏正式"). I cannot invent her saying anything verbatim. So in the footage, she can be seen doing things (试穿记录 footage exists), but any 原话 must come from C01's registered content. Since no verbatim quote is provided, I should NOT write dialogue for the try-on person. All spoken lines are 苏禾's VO. The try-on person appears in footage performing the registered actions (trying on, adjusting collar/cuffs, comparing blazer-off). Her audio, if any, comes from existing raw footage — but I can't script it. I'll note in resource_note: any audible speech in VID-C01 needs verification against C01 before use (or use it only if it's a registered quote). Safer: use footage with her actions; 苏禾's VO carries the narration. If the raw footage has her speaking unregistered lines, that's a downstream verification item. I'll flag.

B2 (~12s) — 信息:
「原本的搭法：廓形西装、垂感阔腿裤、雾蓝棉混衬衫。开会，完全成立。」「但试穿记录里真实记了一笔：连续穿着——从会议到接送——她觉得整身偏正式了。」
Wait — "从会议到接送" is the demo scenario, fine. "真实记了一笔" — connects to "已登记内部演示试穿记录" — accurate (it IS a registered record). Zone: 准确区 facts; "完全成立" — hmm, is "完全成立" overclaiming? The brief: "完整西装＋衬衫组合能满足会议场景" — so saying it meets/satisfies meeting scenario is accurate. "完全成立" is fine-ish but let me use "会议场景，成立。" cleaner. Then the friction: "但连续穿下来，她觉得层次偏正式。" — "连续穿下来" is a phrasing of 连续穿着, fine. "她觉得" attributes to the try-on person — accurate.

Actually, can I show the original still (西装+衬衫+阔腿裤) as B-roll from the footage, or use IMG-P01? The brief's must-use: VID-C01 + IMG-P01. The 商品图 can be used — where? Maybe in B2 as the static "original plan" visual, or in B3. Actually商品图 (studio flat) — the industry reference says studio product photos are low-info, use only as background. Here the brief mandates using them (必须使用), so I'll place them as brief cutaways when naming the three items, but the real information is in the try-on footage. In B2 when naming the combo, cut to the three product images quickly (also gives the viewer the SKUs) OR keep footage. The requirement is they must be used somewhere in the edit. I'll put: B2 naming → quick cuts of IMG-P01 for XQ-2501/2502/2503 (as product identification, not judgment), then back to footage. I'll note in evidence_requirements/pd that product images carry identification only, not claims.

B3 (~18s) — 理解+判断:
「我们没换单品。保留西装和阔腿裤，只把衬衫领口、袖口放松了一点。」「再脱掉西装，比了一下单穿。」「结果是：同一组衣服，正式的程度可以被穿法调出来——但这是这次试穿里的观察，不是标准答案。」

Hmm, "我们" — 苏禾 says "我们" referring to the internal team; the brief's 调整过程 is the registered process. OK. "只把衬衫领口、袖口放松了一点" — the action registered: "将衬衫袖口与领口处理得更放松". Fine. "比了一下单穿" covers "比较脱下西装后的单穿效果". Fine.

The conclusion "正式的程度可以被穿法调出来" with hedge "这是这次试穿里的观察，不是标准答案" — hedges are required (subjective zone, 限定语不可删: "这次试穿里"). Also the brief: "不构成对所有人和所有场景的通用答案". So the hedge is essential. Good.

Zone breakdown: the actions (kept, loosened, compared) = 准确区/INTERNAL facts; "正式的程度可以被穿法调出来" = 主观区 (professional judgment, must keep hedge); the connecting "我们没换单品" is 发挥区 — actually wait, is "没换单品" strictly true? The adjustment kept blazer + pants and adjusted the shirt — same three pieces. Yes, no pieces swapped. But "没换单品" could be read as "didn't change any item" — accurate. Hmm, but it might be risky: if in the footage she put on/took off items, "没换" means across the comparison they stayed with the same three garment types. I'll keep phrasing gentle: 「单品一件没换。」Hmm, or avoid the dramatics: 「调整不是换单品。」 Either fine. Let me use: 「调整不是换单品——」 then list. Clean.

B4 (~15s) — 判断+预期:
「最后留下来的：西装，和阔腿裤。」「没被回答的：肩、袖长、裤长——这几处合不合适，这条视频答不了，要你自己上身试。」「有些结论，内容能替你先走到门口；门里面是什么，得本人试。」

Hmm, "肩、袖长、裤长" — the brief says 肩部、袖长、裤长. "肩" vs "肩部" — keep "肩部" for precision. Let me: 「没被回答的：肩部、袖长、裤长——这几处适不适合你，这条视频答不了，得本人试穿。这是待验证的，不是已经解决的。」

The last line — "要你自己上身试" / "得本人试穿" — accurate. Adding "这是待验证的，不是已经解决的" reinforces the boundary and prevents the "解决了" trap — good. Actually is that line needed? The brief wants viewers to understand "哪些问题仍需通过真实试穿或搭配咨询继续确认". So stating "这条内容不能回答这些，需要本人试穿" is exactly the point. Maybe end with a slightly more conversational version:

「肩部、袖长、裤长——这三处合不合适，一条视频回答不了。」「得你本人试。」 

Hmm, but wait — the non-promise boundary. The explicit_non_promise: this content does NOT promise to answer fit questions, does not promise the combo works for everyone, is not a customer testimony. That's a key output field.

Total: ~53-60s. Good. Let me trim to be safe under 60s. B1 ~8s, B2 ~12s, B3 ~18s, B4 ~17s = 55s. Fine.

Now — the 口播 needs to be 口语化. My drafts have some 书面 phrases: "演示情境" — acceptable for a label? It's precise; on-screen text can carry it while VO says it more naturally. "层次偏正式" — this is from the record; it's a bit jargon-y but it's the registered observation; VO can say it naturally: 「她记的是：整体层次偏正式。」hmm. Or 「她的原话是——整身下来，正式感偏重。」Wait, "她的原话" — do I have her exact words? The brief: "试穿人认为连续穿着时层次偏正式" — this is a paraphrase, not marked as verbatim quote. So I must NOT say "原话". Say: 「试穿记录里记的是：连续穿着时，层次偏正式。」 That's accurate — the record registers this as the initial problem.

Also "正式感偏重" vs "层次偏正式" — use the record's wording closely: 层次偏正式. Fine.

Let me also think about the on-screen text (screen_text[]) — brief requires 内部演示身份与情境设定需以字幕或口播形式标注. I'll specify screen text for the label. Also maybe for the three garment names. And the final boundary line. But keep minimal.

screen_text:
- S1 (B1): 「内部演示试穿 · 非顾客故事」 top or bottom label.
- S2 (B2): names: 廓形西装 XQ-2501 / 垂感阔腿裤 XQ-2502 / 雾蓝棉混衬衫 XQ-2503 — hmm, should I include SKUs on screen? They're registered facts (XQ-2501 etc. are the product codes). On-screen might be useful for product recognition. But 小红书 — product codes on screen could be fine or clutter. The brief mandates using the 商品图 of these three. Screen text could include names. I'll include the three names as screen text where the商品图 cut in, without SKU codes (codes feel like internal stuff; names suffice). Actually the fact_refs can include SKU codes; screen text can just show the names. Fine.
- S3 (B4): 「肩部 · 袖长 · 裤长 —— 需本人试穿」 as a persistent end card? That's arguably a "last frame" which borders on cover/包装 — but screen text within the video is CS's job; end-title screen text is still within the video body. I'll include it but keep it as in-video text (not a cover design).

Wait, the instructions at the end: "本次只做 Creative Script 这一段：不得输出标题、封面、首帧、发布文案、字幕规则、平台适配等 Publishing &amp; Packaging 交付物。" So: no title, no cover, no first-frame design, no publish copy, no subtitle rules (字幕规则 — the systematic subtitle specs), no platform adaptation. But screen_text[] as in-script on-screen text is part of CS (the output contract includes screen_text[]). 字幕规则 (like "字幕字体、字号、描边统一规则") is PP. I'll provide screen_text content and positions but not subtitle styling rules. Good.

Hmm — "首帧" is forbidden. My B1 includes the first moment of the video — but the output contract has "opening: 视频＝前 3 秒画面＋逐字第一句". That's the opening scene unit, distinct from 封面/首帧 design. The opening field specifies the first 3 seconds' image + first line. The instruction says don't output 封面/首帧 — but the opening field is part of the CS contract. I'll keep opening minimal: first 3s image description + first line (from B1). Not designing a cover. I think that's the intended reading — the CS contract mandates opening, and the platform-packaging fields (title/cover etc.) are what's forbidden.

CS-2 check on tension again: The registered friction is the too-formal feeling. That's the drive. Tension = UNVERIFIED (the fit variables — tried some things, but no conclusion for fit; the formality question was verified as adjustable within this try-on, but the fit question explicitly remains a known-unknown that content can't resolve). Actually let me reconsider: is the tension the friction (too formal) or the open fit variables? The brief says: "真实摩擦或决定性张力：试穿人在连续场景中觉得'完整西装＋衬衫'偏正式，这是已登记的真实调整起点；不是虚构反转，只是试穿过程中实际出现的不满足感。" So the decisive tension is the discomfort. The discomfort gets partially resolved. What remains open at the end is the fit question. The "state not completed" at the end = fit verification. UNVERIFIED fits: "试过了，还没定论" — the try-on demonstrated the formality adjustability, but the overall question (does this work for YOU) remains unverified precisely because shoulder/sleeve/pants can't be content-verified. Yes. I'll fill: tension = UNVERIFIED（肩部、袖长、裤长——试穿中能看、但无法凭这条内容定论的个人适配）; alternative consumption reason = Utility（可复用的判断层：先分清'能用穿法调整'与'必须本人试穿'）＋ Identity（演示情境正是目标顾客的连续一天）.

Hmm, actually is Identity a strong consumption reason here? The target customer sees "白天开会、下班接孩子" — yes that's literally her life. OK.

Now creative_directions — let me write them out properly with the five axes each, then the selection rationale.

Direction A: 过程复盘 · 调整是被看见的
- 核心矛盾: 完整组合在连续场景中偏正式——"会议成立"与"连续穿着不放松"在同一套衣服上
- 叙事发动机: 调整过程本身的重演（保留→放松→比较），观众跟着苏禾的复盘一步步走
- 人物关系: 苏禾作为复盘者对观众；试穿人员是过程里的共同尝试者
- 信息释放顺序: 原始方案 → 摩擦 → 调整 → 保留 → 未验证
- 视觉前提: VID-C01 试穿素材为主，苏禾旁白/出镜串场

Direction B: 摩擦先行 · 从"太正式了"那一刻进入
- 核心矛盾: 正式与放松不可兼得，两头的诉求同一时刻压在同一件衬衫上
- 叙事发动机: 那个具体不满足的时刻（连续到后半段觉得整身偏正式）作为引力点，再往回拆
- 人物关系: 试穿者（内部演示人员）第一人称在场；苏禾是画外的陪伴者
- 信息释放顺序: 感受先行 → 原因 → 解法尝试 → 部分保留 → 边界
- 视觉前提: 试穿者反应/动作特写优先，情绪在场感更强

Direction C: 边界先行 · 这条视频不回答什么
- 核心矛盾: 内容能替你判断什么 vs 必须本人试过才知道——把"答不了"放在最前面
- 叙事发动机: 边界划线：先亮出内容的能力边界，再用试穿记录证明哪些能答
- 人物关系: 苏禾对镜头直接声明，姿态是专业且诚实的边界告知者
- 信息释放顺序: 结论边界 → 证据 → 点名未验证变量 → 交给本人
- 视觉前提: 苏禾正面出镜为主，试穿片段作为证据插页

Check A vs B: 核心矛盾 (scenario-fit vs inherent tradeoff) — different; 发动机 (replay vs felt moment) — different; 人物关系 (苏禾 leads vs try-on person first-person) — different; 信息释放 (plan-first vs feeling-first) — different; 视觉 (VO-over-footage vs reaction close-ups) — different. 5 axes. ✓
A vs C: 核心矛盾 different; 发动机 different; 人物关系 (苏禾复盘 vs 苏禾声明 — hmm, same speaker). Let me differentiate: A's 苏禾 is a guide walking through recorded process with the viewer; C's 苏禾 is a declarant making a boundary statement. Posture differs. 信息释放 different (chronological vs boundary-first). 视觉 different (footage-led vs face-led). I'll claim ≥3 with explicit notes.
B vs C: all five differ. ✓

Selection: A. Reasons:
- The brief's 叙事结构 is process-liner: 事实→摩擦→调整→保留→未验证 — Direction A is the only one that preserves this mandated sequence as its engine.
- The account handoff to 周宁 requires the process to be visible/quotable — B compresses it into a feeling, C compresses it into evidence; A keeps the process itself as the content, which is what makes 周宁 able to reference "苏禾的试穿观察" in the next piece.
- B risks the viewer reading the internal demo person as a real customer (the mandatory label fights the emotional-first construction), and drifts toward Identity-heavy "职场妈妈太难" which the brief forbids ("不得声称适合所有'职场妈妈'").
- C's boundary-first requires prior trust in 苏禾's judgment before evidence; in a 60s piece, opening with "这条视频回答不了" reads as a disclaimer rather than a value proposition; the brief also forbids presenting the adjustment as a reversal ("不得把调整剪成惊人反转"), and C's construction edges toward meta-reversal.
- A best embodies the account posture: 陪伴尝试，不急于给唯一答案 — because it accompanies the try-on person through the process rather than delivering a verdict.

Also worth noting: A is NOT "the default option that just follows the brief" — it's the one where the process is maximally foregrounded and the conclusion maximally deferred, which is precisely the brand behavior the account wants (不急于给唯一答案). Good.

Now let me build the script_beats table. Each beat needs: beat_id | 事实 | 素材 | state_change | 逐字稿 | zone.

Beat IDs: B1-B4.

B1 — 开场与身份边界
- 事实: 有 — "内部演示试穿，试穿人非现实顾客；演示情境＝会议＋接送连续场景"（C01 登记事实；brief 明确标注要求）
- 素材: 已确认 — VID-C01 中试穿人整理/入镜的原始片段；苏禾出镜(待确认，可选)
- state_change: 情境（观众进场前先知道这段是什么，防误读）
- 逐字稿: 苏禾 VO：「先说清楚——这是内部演示试穿，不是顾客故事。」「演示的情境：白天有会，下班接孩子。」
  Wait — "下班接孩子" — the demo scenario is 会议＋接送. "下班接孩子" is a natural phrasing of 接送孩子. The brief: "会议与接送连续场景"、"下班接送孩子". Earlier in audience description: "下班接送孩子" appears ("尤其担心..."; the 唯一顾客情境 says "白天会议、下班接送孩子"). So "下班接孩子" is consistent with the brief's language. Fine. Also the screen text label: 「内部演示试穿 · 非顾客故事」.
- zone: 准确区（身份与情境标注逐字成立）

B2 — 原始搭法与真实摩擦
- 事实: 有 — 原始组合（XQ-2501 廓形西装 + XQ-2502 垂感阔腿裤 + XQ-2503 雾蓝棉混衬衫）；C01 初始问题（完整组合满足会议场景，但连续穿着时层次偏正式）
- 素材: 已确认 — IMG-P01 三件商品图（识别用）；VID-C01 中完整组合/试穿过程片段
- state_change: 信息（观众知道原始方案与已登记的摩擦）
- 逐字稿: 「原本搭的是：廓形西装、垂感阔腿裤、雾蓝衬衫。」「进会议室，成立。」「但试穿记录里记了一笔：连续穿着时，层次偏正式。」
  Hmm "进会议室，成立。" — terse, good for 口语化. Keep.
- zone: 准确区（组合与记录陈述）; 连接词可发挥

B3 — 调整过程与本次结论
- 事实: 有 — 调整过程（保留西装和阔腿裤，放松衬衫领口袖口，比较脱下西装后的单穿效果）；已确认观察（同一组合正式程度可通过穿法调整——专业判断，基于 C01）
- 素材: 已确认 — VID-C01 调整过程原始片段（领口袖口放松动作、单穿比较）
- state_change: 理解（"正式与否不只由单品决定，穿法能调"）＋ 判断（同一组合可覆盖正式到放松的区间）
- 逐字稿: 「调整不是换单品。」「西装和阔腿裤留着，只把衬衫领口、袖口放松一点。」「再脱掉西装，比较单穿的效果。」「结论是：同一组衣服，正式的程度能被穿法调出来——但这是这次试穿里的观察，不是所有人的标准答案。」
  Zone: 动作事实=准确区；「结论是……调出来」=主观区（专业判断，保留「这次试穿里」限定语）；「不是所有人的标准答案」=主观区限定语，不可删。
  Hmm — "不是所有人的标准答案" — the brief: "不构成对所有人和所有场景的通用答案". My phrasing is a压缩 but keeps the hedge. Good.
- 素材/画面限制: 不得把"调整"剪成惊人反转（无音乐骤起、无前后对比特效）; 判断句不得用画面强化（即：画面只呈现动作，不替"调出来了"这句话加特写高亮）— put in evidence_requirements.

B4 — 保留、未验证与接手
- 事实: 有 — 被保留（西装和阔腿裤）；待验证变量（肩部、袖长、裤长仍需本人试穿——待验证变量，不能由内容直接回答）
- 素材: 已确认 — VID-C01 单穿效果片段（或试穿人整理肩部/镜前确认的片段，需 C01 支持）
- state_change: 判断（什么成立了、什么没成立被明确切分）＋ 预期（观众对"内容能回答什么"的预期被重置——这正是本条内容承诺）
- 逐字稿: 「最后留下来的：西装，和阔腿裤。」「没被回答的：肩部、袖长、裤长。」「这三处合不合适，一条视频回答不了——要本人试穿。」「有些判断，内容能替你走到门口；门里面，得自己试。」
  Wait — "要本人试穿" — for the viewer, "要你本人试穿" (address the viewer directly) or "要本人试穿" (general)? The brand posture is not-rushing, and the viewer is the target customer. Direct address "你" is stronger: 「得你本人上身试。」 Hmm, "上身" vs "试穿" — keep "本人试穿" to match the brief's language. "得本人试过才知道。" Direct but not pushy. Let me use: 「这三处合不合适，这条视频回答不了——得本人试穿。」 Then the closing: 「能把判断做到这儿的，内容先替你做了；再往下的，留给你的身体。」Hmm, that's a bit literary. The account posture: 陪伴尝试的搭配伙伴. Let me try: 「走到这里，判断能替你做的部分就到这儿了。再往下，是你的身体说了算。」 — this is Identity-affirming and non-rushing, and it's the content's核心 promise (有些问题无法仅凭内容回答). But is it too abstract? For a 60s closing, it's fine — it's the beat that hands over. Zone: these statements are 主观区 (苏禾's framing of the boundary — professional judgment) with the facts (shoulder/sleeve/pants) in 准确区. The "内容能替你判断到门口" metaphor is 发挥区/主观区.
  
  Actually, careful with CS-4 SUBJECTIVE zone: "措辞可改，理由不可改...限定语算理由". The closing metaphor is framing — it's fine as subjective/发挥. The hard limit: don't say "解决了" or "调整后就好了". My B4 says explicitly what remains unanswered. Good.

  One more check: "最后留下来的：西装，和阔腿裤。" — the decision to keep blazer and pants: is this a registered outcome? The brief: 调整过程（保留西装和阔腿裤...）; 被保留的部分——西装和阔腿裤. Yes, it's a must-express. Zone: 准确区 (registered).

Let me reconsider B4's length and whether the "门口" metaphor is too much for ≤60s. Current total: B1 ~8 + B2 ~12 + B3 ~18 + B4 ~17 = 55s. OK.

Also — should the 无 CTA thing appear in the script? CTA is "本条无 CTA" — so no call-to-action in the script. The optional 统一承接说明 was recommended against; I'll mark CTA: 无（建议不加统一承接说明）. This is consistent with cta_contract = NO_CTA. I could also mention in constraints: 不出现"私信""评论区扣1""预约"等任何行动召唤. Good.

Now — question_list[]: required if there are beats with 事实=无. All my beats have 事实=有. But wait — are there any 事实=无 beats? The 苏禾 出镜方式 (VO vs 真人出镜) is undecided — that's a production parameter, not a beat fact. The try-on person's original audio if present in VID-C01 — that's a 素材 待检索/待确认 issue, not a fact. Hmm, also: in B3/B4, do I reference any beat that needs material not confirmed? The 补录 (30min) — the brief allows 补录 for 苏禾. If 苏禾 goes face-to-camera in B1, that's 待产出·可控 (scheduled in the 3h shoot). Let me check each beat's 素材:

- B1: VID-C01 原始片段 (已确认, required by brief). 苏禾出镜(可选) = 待产出·可控 but optional. I'll design B1 as footage-led with VO; the on-camera option is a variant, flagged.
- B2: VID-C01 + IMG-P01 (已确认).
- B3: VID-C01 调整过程片段 (已确认 — the brief says "必须使用：VID-C01 中试穿记录一原始片段" and the 降级条件 mentions "如果视频片段不足以完整呈现调整过程，可用已确认照片＋口述补足" — so there's a degradation path if the adjustment footage is insufficient. Should I mark B3 as 素材=待检索? The brief's must-use states VID-C01 contains the record; the degradation path suggests footage may be insufficient for the full adjustment sequence. Hmm. I'll mark: 素材=已确认（记录一原始片段存在且须使用；但"调整过程是否完整可见"有降级路径——见 evidence_requirements/degradation）). Actually the two-question table: 素材=已确认 means "看过，确定可用". Have we "seen" the footage? In this pipeline, the brief asserts VID-C01 试穿记录一 exists and is the must-use material. I'll treat it as 已确认 per brief, with a note that completeness of the adjustment-visible sequence carries the brief's registered degradation path (photos + narration), handled at PD. OK.
- B4: VID-C01 单穿效果/镜前检查片段 — is the blazer-off comparison footage guaranteed? The 降级条件: "如果'比较脱下西装后的单穿效果'无法完整呈现，可只保留'领口袖口放松'的调整，但结论强度需同步降低为'部分可调整'". So the blazer-off comparison is the potentially missing piece! This means B4 (or B3) has a 素材 uncertainty with a registered degradation. So B4's 素材 = 待检索/待确认? Hmm — "已确认" for the existence of VID-C01 record, but the specific sub-scene (blazer-off comparison) has a known degradation condition. I'll mark B4 素材: 已确认（若单穿比较片段不足，按 brief 降级条件：仅保留领口袖口放松，结论降为"部分可调整"——但"肩部/袖长/裤长仍需本人试穿"必须保留）. This is important to carry into PD.

So no 事实=无 beats, no question_list[] needed. But wait — should I double-check? The try-on person's registered words: C01 records the initial problem, but no verbatim quote is in the brief. My script doesn't quote her, so no 事实=无. Good. question_list: NOT_APPLICABLE. 

skeleton: required only if 事实=无 beats exist. Not needed. But the skill says "skeleton: 有「事实=无」的 beat 时必填" — so NOT_APPLICABLE. However, I might still include a brief note of the beat relationships? The output contract lists it; I'll write NOT_APPLICABLE (no 事实=无 beats).

检索判据清单: required if 素材=待检索 units exist. My B4 has a conditional risk but is marked 已确认 with degradation — not 待检索. So 检索判据清单: NOT_APPLICABLE. Hmm, but the degradation path needs somewhere to live — I'll put it in evidence_requirements or resource_note. Actually, let me reconsider B4: the brief's 降级条件 explicitly anticipates "无法完整呈现" — meaning before edit, someone must check whether the blazer-off comparison footage exists/works. That's a检索/确认 action. I could make B4 素材=待检索 with a 检索判据清单: 找什么（单穿效果可用的原始片段）／找到算什么（保留完整结论"正式程度可以通过穿法调整"）／找不到怎么办（按降级：只保留领口袖口放松，结论降为"部分可调整"，肩部/袖长/裤长判断仍保留）. Hmm — that's actually more honest and operationally useful. But the brief says VID-C01 是"必须使用的素材"，且记录一"包含调整过程"。 The uncertainty is about completeness of the specific sub-scene, not the whole record. Let me mark B3 (调整过程) as 已确认 with the degradation noted, and B4's 单穿比较子场景 as 待检索? That splits oddly. Alternatively: mark B3/B4 together as the "调整过程单元" with 素材=已确认（记录一存在）＋ 一个"检索判据"只在素材层面：确认单穿比较片段可用性。The skill says 检索判据清单 is for 素材=待检索 units. To be precise: VID-C01 is a corpus (原始片段), and the specific shots needed have not been verified by the script stage. The honest marking: 素材=待检索 for the specific sub-scene, 已确认 for the record's existence. But the two-question table has one value per beat. I think the cleanest: 
- B3 素材: 已确认（记录一整体；调整过程动作是否完整可见，按 brief 降级路径在剪辑前核实）
- B4 素材: 待检索（"脱下西装后的单穿效果"片段——brief 明确给了"无法完整呈现"的降级条件，说明该子场景的存在性在制作时需核实）→ 检索判据清单: 找什么：VID-C01 中"脱下西装后单穿"的有效片段（正身/侧面，能看清整体层次）；找到算什么：保留完整结论，B4 可直接引用；找不到怎么办：执行 brief 降级——只保留"领口袖口放松"的调整，结论强度降为"部分可调整"；"肩部/袖长/裤长仍需本人试穿"不论如何保留。

Hmm wait — if B3's adjustment includes "比较脱下西装后的单穿效果" as one of its registered actions, and B4 relies on the blazer-off result, maybe the 客观 partition is: B3 covers 保留+放松 (已确认), B4 covers 单穿比较结果 + 边界. Actually in my current structure, B3 = adjustment process (保留+放松+比较单穿), B4 = kept/unverified. The blazer-off comparison is B3's action. So B3's素材 is the one with the sub-scene risk. Let me re-assign: B3 素材: 待检索（具体子场景"脱下西装单穿"的可用性需核实；整体记录已确认）→ 检索判据清单 under B3. And B4 素材: 已确认（单穿效果若不可得，按降级路径处理结论）。

Hmm, this is getting complicated. Let me simplify: the skill allows "部分有｜混合" rows with per-beat marking. I'll mark:
- B1: 事实=有, 素材=已确认
- B2: 事实=有, 素材=已确认
- B3: 事实=有, 素材=待检索（VID-C01 内"放松领口袖口"与"脱下西装单穿"两个子场景的可用性——记录存在但本环节未过片；brief 自带降级条件，见检索判据清单）
- B4: 事实=有, 素材=已确认（若 B3 降级，B4 结论相应降级）

And 检索判据清单 (for B3):
- 找什么：① 衬衫领口、袖口被放松的前后动作/状态帧；② 脱下西装后单穿（阔腿裤+衬衫）的有效片段，正身或半侧身，能看清整体层次
- 找到算什么：B3 逐字稿成立，"正式程度可通过穿法调整"可作为完整观察呈现；B4"西装和阔腿裤被保留"由同段素材支撑
- 找不到怎么办：①若只有②缺——执行 brief 降级：B3 只保留"领口袖口放松"的调整，B4 结论降为"部分可调整"；②若①缺——用已确认照片＋口述补足调整过程（brief 降级条件）；③无论怎么降级，B4"肩部/袖长/裤长仍需本人试穿"必须保留

That's operational. Good.

Now fact_refs[] — let me list:

1. 三件商品事实（XQ-2501 廓形西装、XQ-2502 垂感阔腿裤、XQ-2503 雾蓝棉混衬衫的材质/版型/价格/库存）— type INTERNAL? The brief: "已登记商品事实；原始来源为商品登记表／B01；事实确认人周宁". Hmm — product facts from 商品登记表: are they EXTERNAL (externally verifiable: price, composition, etc.)? The type table: EXTERNAL = "外部核验得了：数字、成分、价格、公开发表过的话". Product registration data (fabric composition, price) IS externally verifiable in principle (one could look at the product). But — is it public? The 商品登记表 is the store's internal registry. Price/composition are externally verifiable against the actual product. I'd type these EXTERNAL (numbers, composition, price) — verifiable — with the source being 商品登记表/B01, confirmant 周宁. Actually, hmm: "外部核验得了" means an outsider could verify. Product price and fabric on a retail item: yes, verifiable. I'll mark the product facts EXTERNAL. But the brief's source is internal (登记表) — the type is about verifiability, not source classification. I'll set type=EXTERNAL for the product facts (composition/price are objectively checkable), noting source = 商品登记表/B01 (周宁). Hmm, but the skill's type table says EXTERNAL = 无来源者不得用画面强化. These have sources. OK.

Actually wait — do I even reference price/composition in the script? My draft mentions the three garment names but not price/composition. The brief's must-express list doesn't include price/composition. The script references: combo = 廓形西装+垂感阔腿裤+雾蓝衬衫. That's product identity, not the full registration. fact_refs should list what the script actually asserts. Let me list:

f1: 三件单品及其品类名（廓形西装/垂感阔腿裤/雾蓝棉混衬衫）— source 商品登记表/B01 — type EXTERNAL（商品登记事实，可核验）— used in B2
f2: C01 试穿记录一存在；初始问题＝完整组合满足会议场景但连续穿着时层次偏正式 — source C01（内部登记），确认人苏禾 — type INTERNAL（内部记录可查，外部核验不了）— B2
f3: 调整过程（保留西装和阔腿裤、放松衬衫领口袖口、比较脱下西装后单穿）— source C01，确认人苏禾 — type INTERNAL — B3
f4: 已确认观察：同一组合正式程度可通过穿法调整 — source C01（苏禾专业判断）— type SUBJECTIVE — B3
f5: 被保留：西装和阔腿裤 — source C01 — INTERNAL — B4
f6: 待验证变量：肩部、袖长、裤长仍需本人试穿，不能由内容回答 — source brief/C01（苏禾专业判断）— type KNOWN_UNKNOWN（显式声明内容无法回答；压制 SUBJECTIVE）— B4
f7: "内部演示试穿，非现实顾客；会议＋接送为演示情境" — source Content Brief 制作要求 — type INTERNAL（是制作指令/已登记边界，不是可核验的外部事实）— B1. Hmm — is this INTERNAL or EXTERNAL? It's an identity/authenticity frame. It's "upstream-locked instruction". I'd say INTERNAL (有记录可查——brief/C01 登记)。Or EXTERNAL? The fact "this is an internal demo try-on" is the production decision recorded in the brief; externally verifiable? Not really — an outsider couldn't verify who the try-on person is. INTERNAL fits: "有记录可查、但外部核验不了". OK.
f8: 演示情境="会议＋接送" — same as f7, or merge. I'll merge into f7.

Also b-roll 门店空镜 (可选, 仅转场) — not a fact. IMG-P01 已整理商品图 — material, not fact.

evidence_requirements[]:
- B1 身份标注的画面证明：试穿画面出现前或同帧必须有"内部演示试穿"标注（字幕或口播）——这是画面与声明同现的要求，交给 PD
- B2: 三件商品图只承担识别，不承担性能判断；试穿场景画面用于支撑"连续穿着"这一演示情境，但"会议成立"这一判断不依赖画面证明（它是登记观察）——画面不得反向强化为"这身衣服在任何会议都成立"
- B3: "正式程度可调"是专业判断（SUBJECTIVE）——画面只呈现调整动作本身，不得用特效、音乐、前后对比分屏去"证明"这个结论；不得剪成惊人反转（brief 硬禁）
- B4: "肩部、袖长、裤长仍需本人试穿"是 KNOWN_UNKNOWN——画面只能呈现"这里还没答案"（如试穿人镜前查看肩部、把玩袖长的动作），不得呈现"答案本该是什么"（不得用画面暗示她的肩部/袖长有问题或没问题）；更不得给试穿人做身体评价

constraints[]: (from brief + CS)
- 不得把内部试穿人员表述为现实顾客；"会议＋接送"是演示情境，须字幕或口播标注
- 不得拼接 C01 与 D01 成同一顾客故事
- 不得声称适合所有"职场妈妈"或任何具体人群
- 不得补写防水/防风/抗皱/保暖/显瘦等未登记性能
- 不得声称提高了销售或顾客更喜欢
- 不得把调整剪成惊人反转
- 不使用"显瘦""闭眼入""人人可穿"等话术
- 不出现预约成功或名额稀缺表述；无 CTA（建议不加统一承接说明）
- VO 不得给试穿人的身体下判断（肩宽、袖长不合等）——只陈述"这些需本人试穿验证"
- 试穿人若有可见说话画面，其话语必须来自 C01 已登记内容；未登记的原话不得使用（若无则剪辑中规避其面部说话口型）— hmm, this is a good constraint. VID-C01 was shot; if the try-on person speaks in the footage, using her unregistered words would be fabrication-by-assembly. I'll add: 使用 VID-C01 时，试穿人的任何可闻话语须先与 C01 登记内容核对；C01 未登记的语句不得进入成片.
- 不输出平台规格的秒数/格式设计（待平台锁定）— that's more of an assumption.

resource_note:
- 出镜：内部演示试穿人员（画面主体，来自 VID-C01 已有素材）；苏禾（口播为主；如需真人出镜，在 3 小时拍摄＋补录内安排，B1 或 B4 可选，不阻塞本稿）
- 需要现在还不存在的素材：苏禾口播录音（3h 拍摄内完成或补录）；如 B1/B4 出镜，需苏禾正面镜头（可选）
- IMG-P01 三件商品图已整理，待检索核对?? — brief says 已整理 and 必须使用. I'll say: 已确认存在，剪辑时定位。

assumptions[]:
- expression_subject = NATURAL_PERSON（苏禾，账号持续表达者，口播主体）——上游已定
- platform：输入给小红书；但 brief 明确"最终发布平台未确认，由 Founder 锁定"，本稿按平台中立母版处理，时长 ≤60s 满足所有候选平台；不进入平台规格设计
- 苏禾出镜方式未定：本稿按"口播为主线、出镜为可选"设计，两种方式都成立
- 单穿比较子场景素材状态按"待检索"处理，并附带 brief 既有降级路径
- duration_band 短档（≤60s），4 个 beat
- 无真实顾客原话可用（C01 是内部演示记录，非顾客故事）

missing[]:
- 最终发布平台（Founder 锁定中）
- 苏禾出镜方式（真人出镜或旁白）
- 是否使用统一承接说明（建议不使用——已按无 CTA 处理）
- VID-C01 中"脱下西装单穿"子场景的可用性（已给检索判据）

Now — the opening field:
opening: 视频＝前 3 秒画面＋逐字第一句
- 前 3 秒画面: VID-C01 试穿人整理衣领/入镜的短镜头（或试穿过程中一个"觉得不对"的瞬间），画面角落即时打出「内部演示试穿 · 非顾客故事」标注
- 逐字第一句: 「先说清楚——这是内部演示试穿，不是顾客故事。」

Hmm wait — is "整理衣领" a fabricated micro-action? I said earlier to be careful. The footage is VID-C01's raw; I'm describing what the edit should find, not inventing a specific registered action. As an opening image instruction for the editor: "选一个 VID-C01 里试穿人入镜/调整衣着的短镜头" — better to phrase as selection criterion, not specific invented action. Let me phrase: 前 3 秒: VID-C01 中试穿人入镜的第一个有效镜头（选：能让人看清"有人在试衣服"的画面，不选任何可能被读成"顾客在抱怨"的瞬间）；同帧标注「内部演示试穿 · 非顾客故事」。 That's safer.

content_promise: 这条内容承诺兑现什么: 让观众看到一个真实试穿记录里的调整过程，并明确切分"哪些问题能通过穿法调整"与"哪些只能由本人试穿确认"——不承诺回答个人适配，不承诺这件组合适合所有人。

explicit_non_promise[]:
- 不承诺给出"这套组合适不适合你"的答案
- 不承诺肩部/袖长/裤长的适配判断
- 不承诺该组合适合所有会议或所有人群（不适用于所有"职场妈妈"）
- 不承诺任何性能表现（防水/防风/抗皱/保暖/显瘦）
- 不承诺这是顾客见证或真实顾客经历
- 不承诺调整带来任何销售/偏好结果
- 无 CTA：不承诺预约、到店或名额

audience_shift: 从"按单件新品和表面风格被动浏览"到"能用自己的一个真实穿着问题，套用'哪些问题可调整、哪些需本人试穿'的判断，做出初步比较或排除，并识别下一步需本人试穿确认什么"。(上游给定)

creative_concept: selected A + why（指名判据）— I'll write it as above. Also note: concept name. Direction A: 「调整过程被看见：一套衣服的正式程度，是试出来的」 or simpler.

Also per CS-1 requirement: "选 1 个深化" — and I should 逐轴写清怎么不同 for the three directions. In output, creative_directions[] with 3 entries each containing the five axes. Let me make sure each direction's five axes are explicit.

Now, one more consideration: the 苏禾出镜方式 — the flow says if in 对话 be called with missing params, ask. But the brief's must-confirm list includes it. However, my script works either way (VO-first design). The return_from_downstream[] is empty. I'll note in assumptions and move on. Also the platform conflicts — same treatment.

Another check: the beat state changes — B1 情境, B2 信息, B3 理解+判断, B4 判断+预期. CS-3 wants every beat to change at least one state; each has refs. B4 has 判断 (what's kept vs not concluded) — but B3 already changed 判断. Different object though: B3's judgment = formality is styling-adjustable; B4's judgment = which parts are settled vs not. Hmm, maybe B4's primary is 预期 (expectation reset: "content can't answer everything — and that's the point") + 关系? Not 关系. I'll say B4: 判断（保留/未验证的切分）+ 预期（观众对"这条内容能回答什么"的预期被重置）。 Fine.

Also — for CS-3, the 停驻 (pause) is not used; note as not applicable (content ends with a forward-pointing handoff, not an unresolved aesthetic stop).

Everything must be in Chinese? The skill file is Chinese; the user input is Chinese. The output contract field names are English. I'll write the content in Chinese with English field labels, mirroring the skill's examples.

Let me also double-check the CS-7 ⑥ rule for C01's record: does C01 record "两侧结果"? The registered record: initial problem (too formal in continuous wear) → adjustment → 已确认观察 (formality adjustable) → 待验证变量 (shoulder/sleeve/pants). There are two sides: what worked (formality adjustable, meeting-scenario OK) and what didn't get answered (fit). My script keeps both. ✓. Also 不得用"解决了" — my B4 explicitly says 未回答/需本人试穿. ✓. tension_mode not set to 已解决-style. ✓. Also no 比较级 like "更松" — do I use any? "放松了一点" — "一点" is a degree, not a comparative vs another option. The record says "处理得更放松" — comparative in the source! "将衬衫袖口与领口处理得更放松" — comparing to the original tight/standard state. Using "放松一点" (change from original) is faithful to the record. Fine — it's a registered comparison (adjustment vs original), not an invented comparison between options.

Also: "正式的程度能被穿法调出来" — is "调出来" implying it became less formal? Yes, the adjustment's direction: from 偏正式 to 可调整. The brief: "通过保留西装和阔腿裤、放松衬衫领口和袖口...正式程度可以调整". So the registered direction is reducing formality while keeping the suit elements. My phrasing "正式的程度能被穿法调出来" without specifying direction — hmm, it says formality level can be adjusted (which direction? both?). The registered observation: the组合 was too formal; adjustment relaxed it. To stay precise: 「正式感是可以往下调的」 — wait, "往下调" implies it became less formal. Is that registered? The adjustment (loosen collar/cuffs, compare blazer-off) resulted in... the brief says "正式程度可以调整" — the confirmed observation is that formality is adjustable, and the account judgment: "完整西装＋衬衫组合能满足会议场景，但在连续穿着中层次偏正式；通过...正式程度可以调整". The direction: making it less formal for the continuous scenario. I'll phrase to match: 「同一组衣服，正式的程度是可以调的——这次是靠穿法往下调。」 Strictly, "往下调" (reduce formality) matches the record's direction. Let me use: 「结论是：这组衣服的正式程度，能靠穿法调——但这是这次试穿里的观察，不是标准答案。」 Hmm, "能靠穿法调" without direction. Then the next beat shows the kept pieces. Actually maybe: 「这组衣服的正式感，能靠穿法往下调。」 That matches: the problem was 偏正式, the adjustment 放松了, result 正式感降下来但仍成立. I'll phrase: 「这组衣服的正式感，可以靠穿法往下调——但这是这次试穿里的观察，不是所有人的标准答案。」 The "往下调" phrasing is faithful to the record direction (调整 from too formal toward more relaxed). Good.

Let me also sanity-check the script doesn't violate "不先评价试穿人身体": B4 mentions 肩部/袖长/裤长 as things needing personal try-on — this is NOT evaluating the try-on person's body; it's naming variables. The registered C01 record notes these as待验证变量 (the try-on itself showed these variables matter). Good. Also B4's footage direction: if showing the try-on person checking her shoulder — that's her action, not 苏禾 judging her. And my VO doesn't diagnose "她的肩部不合适" — it says these need本人试穿. ✓.

Another point: CS-5 口语化 — my draft lines are short with pauses. Let me smooth them:

B1 VO:
「先说清楚——这是内部演示试穿，不是顾客故事。」
「演示的情境：白天有会，下班接孩子。」
Hmm "演示的情境" is slightly formal but it's a label — acceptable; alternatively: 「试的是这样一个情境：白天开会，下班接孩子。」 More natural. Let me use natural: 「我们试的是一个情境：白天有会，下班接孩子。」 Wait — but "我们" and the labellity... B1 must clearly state 内部演示. Natural version: 「先说明一下：这是内部演示试穿，不是顾客故事。」「情境是演出来的——白天开会，下班接孩子。」 "演出来的" — hmm, "演示" not "演戏". "情境是演示的" reads awk. 「情境设定是：白天开会、下班接孩子。」 — "情境设定" is fine and precise. I'll go:
L1: 「先说清楚——这是内部演示试穿，不是顾客故事。」
L2: 「情境设定：白天开会，下班接孩子。」
Screen text: 内部演示试穿 · 非顾客故事
~8s. ✓

B2 VO:
「原本搭的是：廓形西装、垂感阔腿裤、雾蓝棉混衬衫。」
「开会，成立。」
「但试穿记录里记了一笔：连续穿下来，层次偏正式。」
~14s. "记了一笔" — natural, and it correctly frames the record (已登记). "连续穿下来" natural. "层次偏正式" is the record's phrase — good. Screen text: 三件商品名（商品图切入时）.

B3 VO:
「调整不是换单品。」
「西装和阔腿裤留着，只把衬衫领口、袖口放松一点。」
「再脱掉西装，比了一下单穿。」
「这组衣服的正式感，可以靠穿法往下调——但这是这次试穿里的观察，不是所有人的标准答案。」
~20s. ✓

B4 VO:
「最后留下来的：西装，和阔腿裤。」
「没被回答的：肩部、袖长、裤长。」
「这三处合不合适，一条视频回答不了——得本人试穿。」
「内容能把判断做到这儿。再往下，是你自己试过才算数。」
~17s.

Total ~59s. Tight — maybe trim B3's last line or B4's. Let me count more carefully:
B1: L1 ~4s, L2 ~3s → 7s
B2: L1 ~4s, L2 ~2s, L3 ~5s → 11s
B3: L1 ~2s, L2 ~5s, L3 ~4s, L4 ~8s → 19s
B4: L1 ~3s, L2 ~3s, L3 ~5s, L4 ~5s → 16s
Total 53s. Good, under 60 with room for pauses.

Screen text (in-video):
- S1 (B1 start, persistent through B1): 内部演示试穿 · 非顾客故事
- S2 (B2, when product images show): 廓形西装 / 垂感阔腿裤 / 雾蓝棉混衬衫
- S3 (B4, on the final boundary line): 肩部 · 袖长 · 裤长 — 需本人试穿
Positions: top for S1 (label), lower-third for S2, bottom for S3. These are placements, not styling rules — OK per contract.

voiceover[]: 苏禾口播贯穿 4 段（B1–B4），画面为 VID-C01/IMG-P01；另 B1 可选真人出镜（在产能内，不阻塞）。Actually voiceover[] field = 画外音，带位置. I'll list: VO-1 至 VO-4 对应 B1–B4（全程画外，或 B1/B4 可选转真人出镜）。

Now — do I need to verify the "小团队" production profile anywhere? It mainly constrains PD (crew size 3h shoot etc.), which the brief already covers. CS note: keep within one 3h shoot + 30min 补录. Resource note covers it.

Also "接力关系" — 苏禾向周宁交出问题. My script's ending (B4) hands the boundary over — the next piece (周宁) will reference "试穿暴露的问题中哪些可在选择阶段提前识别". Does my script need to explicitly name this handoff? No — it's an upstream sequencing fact, not content for this video. The content ends with the boundary statement, which is exactly the handoff substance. Good. Also I should NOT include a "关注周宁" type of cross-account pointer (no CTA allowed).

Let me reconsider the direction selection rationale once more to make it genuinely CS-1-grade (指名具体判据). The skill says: 选中的方向 + 为什么选它（指名具体判据，不写"更抓人"）. My criteria:
1. Brief 强制叙事结构是过程线性（事实→摩擦→调整→保留→未验证），A 的发动机与该结构同构，B/C 都需把该结构重新排序
2. 接力要求：周宁要引用的是"苏禾试穿观察"本身——A 让过程可见可引，B 压缩为感受、C 压缩为证据，都会削弱下一条的可引用性
3. 账号姿态"陪伴尝试，不急于给唯一答案"：A 在结构上把结论压到最后一句，B/C 都把结论前置——与账号姿态相反
4. B 的风险：内部演示人员被误读为真实顾客（brief 硬禁）；C 的风险：以"答不了"开场在短档里读起来像免责声明，且"边界先行"结构有滑向"惊人反转"修辞的风险（brief 硬禁）
5. 素材条件：主素材是 VID-C01 试穿记录，A 的使用效率最高（全程以记录为载体），C 需要苏禾正面出镜为主，在"出镜方式未确认"的条件下风险更高

Good.

Also failure_case: what would sink this. The skill wants: 会砸的那条方案＋为什么砸（要看得出机制）. Possible failure: 把 B3 的"正式感可调"剪成反转（音乐骤起、前后对比），或把 B1 的"内部演示"标注放在片尾而不是开头，导致观众前半段读成顾客故事——机制：SUBJECTIVE 判断被画面强化成客观事实＋身份边界后置导致整个内容的真实性承诺失效。Or maybe another failure: 把 B4 收成"所以解决了"——机制：删掉记录的另一半（未验证变量），把条件句写成结论句。The skill wants the failure case to show the mechanism. I'll write: 
failure_case: 「把调整剪成'惊人反转'版」——B3 的"正式感可调"是 SUBJECTIVE（基于一次内部试穿的观察），若配音乐骤起/前后对比分屏，画面会把专业判断强化成"这套衣服就是答案"的客观事实；同时 B1 的"内部演示"标注若被后置或省略，观众会把演示人员读成真实顾客——真实性与边界双双失效，恰好撞上 brief 两条硬禁。机制：CS-4 主观区被画面强化＋CS-6 素材剪辑模式下被剪出输入不支持的结论。

Hmm, the failure case should be "会砸的那条方案" — the方案 that would sink it. Maybe more precisely: 「版本 A 的'惊喜改造'化」— 把"调整"变成一个前后对比的改造惊喜，结尾说'这样就不正式了'。为什么砸：输入只登记了"正式程度可以调整"，没登记"调整后就是放松的最终答案"——删掉了仍未回答的肩部/袖长/裤长那一半；且"改造惊喜"结构把 SUBJECTIVE 判断用画面坐实，违背 brief 的"不剪成惊人反转"。机制：CS-7 ⑥（删掉记录的另一半）＋ CS-4（SUBJECTIVE 被画面强化）。

OK. Now let me also do the self-check mentally:

1. 第一句删掉，内容还成立吗？ — B1 第一句是身份标注，不是废话；删掉它整条内容的真实性承诺失效。✓（第一句是必要的）
2. 这条在反对什么/解决什么？ — 反对"看静态搭配图就以为知道答案"；解决"哪些问题能靠穿法调整、哪些必须本人试穿"的判断切分。✓
3. 有没有一句是只有这个品牌/这个人能说的？ — "这是这次试穿里的观察，不是标准答案" — 这个限定语只有有真实试穿记录的人能说；"内部演示试穿"这个自我暴露也只有愿意公开记录边界的账号会说。✓
4. 三方向五轴差三轴 — verified above. ✓
5. 每段状态变化 — ✓ (情境/信息/理解+判断/判断+预期). 停驻未用。✓
6. 每 beat 事实/素材填了 — ✓. 6b. fact_refs type 判对 — 我判了 EXTERNAL/INTERNAL/SUBJECTIVE/KNOWN_UNKNOWN，checked。✓
7. 有没有输入不存在的事实 — 我自查：没有时间"下午"、没有"解开一颗扣子"、没有给试穿人身体下判断、没有顾客数量。✓
8. 关联/沉默/身份/删半 — 没有编造关联；没有编造沉默；没有给任何人补身份（试穿人身份=内部演示人员，来自 brief）；没有删记录的另一半（B4 明示未验证）。✓
9. explicit_non_promise — written.✓

One more thing: the "会议" claim — B2 says "开会，成立。" This is the registered initial problem ("完整西装＋衬衫组合满足会议场景"). Good — it's INTERNAL (registered observation from C01), not EXTERNAL. In fact_refs f2 I included it. The phrasing "开会，成立" — terse but accurate. Maybe "进会议室，成立。" — "进会议室" adds a place not in input? The scenario is "会议"; "进会议室" is just a way of saying "for the meeting". The record says "满足会议场景". To be safe: 「开会这个场景，成立。」 Hmm. I'll use 「开会，成立。」as a自然短句 — it's a压缩 of "会议场景成立". Fine.

Also should the script acknowledge 价格? No — brief's必表达 list doesn't include price; adding price would be using registered facts unnecessarily (and the brief doesn't ask). Skip. But fact_refs for product facts — I'll list the product names + registration number references minimally, since script doesn't assert price/composition. Actually, the mapping requires "XQ-2501 廓形西装、XQ-2502 垂感阔腿裤、XQ-2503 雾蓝棉混衬衫" — the script asserts names &amp; the combo. fact_ref f1 covers it.

Wait — one nuance: the garment name. XQ-2503 is "雾蓝棉混衬衫" — in B2 I say "雾蓝棉混衬衫" (full name). In screen text "雾蓝棉混衬衫". Good. Actually for VO, "雾蓝衬衫" vs "雾蓝棉混衬衫" — the brief's must-express doesn't demand the full fabric descriptor, but since it's the registered name, use the full name at least once (screen text), and VO can use "雾蓝衬衫" as shorthand. Hmm — to be safe and precise (准确区), keep "雾蓝棉混衬衫" in VO too. It's 3 extra syllables. Fine.

Let me also handle zone labels per line precisely in the script_beats:

B1:
- L1「先说清楚——这是内部演示试穿，不是顾客故事。」: 准确区（身份标注，逐字）
- L2「情境设定：白天开会，下班接孩子。」: 准确区（演示情境，逐字）

B2:
- L1「原本搭的是：廓形西装、垂感阔腿裤、雾蓝棉混衬衫。」: 准确区（商品事实）
- L2「开会，成立。」: 准确区（C01 初始判断）
- L3「但试穿记录里记了一笔：连续穿下来，层次偏正式。」: 准确区（C01 初始问题）
- 连接处理（"原本搭的是""但"）: 发挥区

B3:
- L1「调整不是换单品。」: 发挥区（引导句）
- L2「西装和阔腿裤留着，只把衬衫领口、袖口放松一点。」: 准确区（C01 调整动作）
- L3「再脱掉西装，比了一下单穿。」: 准确区（C01 调整动作）— "比了一下" natural phrasing of "比较单穿效果"
- L4「这组衣服的正式感，可以靠穿法往下调——但这是这次试穿里的观察，不是所有人的标准答案。」: 主观区（苏禾专业判断；「这次试穿里」「不是所有人的标准答案」为限定语，不可删）

B4:
- L1「最后留下来的：西装，和阔腿裤。」: 准确区（C01 保留项）
- L2「没被回答的：肩部、袖长、裤长。」: 准确区（待验证变量点名）
- L3「这三处合不合适，一条视频回答不了——得本人试穿。」: KNOWN_UNKNOWN（显式不知声明）／主观区判断，但按 KNOWN_UNKNOWN 处理
- L4「内容能把判断做到这儿。再往下，是你自己试过才算数。」: 发挥区（收束句，不改变事实边界）— is this too close to a CTA? It's not an action prompt (no "来找我们"), it's a boundary statement. OK. Hmm, "是你自己试过才算数" — could a viewer read this as "go try it on"? That's... actually aligned with the经营任务: "到店试穿引导" is the campaign's broader goal, but this content is explicitly无 CTA and 不承担预约转化. "是你自己试过才算数" is a statement of principle, not an instruction to go to the store. It doesn't name any action, place, or channel. It stays within the judgment framework (识别哪些问题仍需本人试穿). I think it's fine. Alternatively "再往下，只能本人试过才知道" — safer, no second-person imperative feel. Let me use: 「内容能把判断做到这儿。再往下，只能本人试过才知道。」 Slightly less personal, avoids any action-read. Good.

Now, is "内容能把判断做到这儿" clear? Meaning: content can take the judgment this far. Then "再往下，只能本人试过才知道" = beyond this, only personal try-on can tell. Clear and matches the unique new judgment. Good.

Let me also add to B4 a brief screen text: 肩部 · 袖长 · 裤长 → 需本人试穿. And maybe on the商品图 screen text: the three product names.

One more beat-level item: the skill wants 素材 column to be precise. I'll write per beat:
- B1: 已确认 — VID-C01（试穿记录一原始片段，开场段）; 苏禾出镜镜头＝待产出·可控（可选，不阻塞）
- B2: 已确认 — VID-C01（完整组合/试穿过程）+ IMG-P01（三件商品图，识别用）
- B3: 待检索 — VID-C01 内"领口袖口放松""脱下西装单穿"两个子场景的可用性（记录存在但本环节未过片）；若不足，按 brief 降级路径
- B4: 已确认 — VID-C01（单穿效果或试穿人镜前检查片段）；结论强度随 B3 检索结果联动

And 检索判据清单 for B3 as designed above.

Also the 事实 column:
- B1: 有（内部演示身份与演示情境，brief/C01 登记）
- B2: 有（商品事实 B01/R01；C01 初始问题）
- B3: 有（C01 调整过程；苏禾已确认观察）
- B4: 有（C01 保留项；待验证变量）
No 事实=无 beats → question_list NOT_APPLICABLE, skeleton NOT_APPLICABLE.

Now, output format. Let me assemble the whole thing in the contract's field order:

```
content_origin_mode[]        ["现拍", "已有素材剪辑"]
creative_directions[]        [A, B, C each with five axes]
creative_concept             selected + rationale
audience_shift               (上游给定)
content_promise
explicit_non_promise[]
tension_mode
expression_subject
opening
script_beats[]
question_list[]              NOT_APPLICABLE (no 事实=无 beats)
检索判据清单                    for B3
skeleton                     NOT_APPLICABLE
voiceover[]
screen_text[]
fact_refs[]
evidence_requirements[]
resource_note
constraints[]
failure_case
assumptions[]
missing[]
```

Wait, the contract fields use English names (question_list[], skeleton etc.) but the 检索判据清单 appears in Chinese in the contract (it's a literal field). I'll mirror the contract's mixed format as the skill examples do. Actually the skill output block mixes: content_origin_mode[], creative_directions[], creative_concept, audience_shift, content_promise, explicit_non_promise[], tension_mode, expression_subject, opening, script_beats[], question_list[], 检索判据清单, skeleton, voiceover[], screen_text[], fact_refs[], evidence_requirements[], resource_note, constraints[], failure_case, assumptions[], missing[]. I'll follow exactly. For fields with no content: question_list: NOT_APPLICABLE（无"事实=无"的 beat）; skeleton: NOT_APPLICABLE; voiceover[]: I have VO so fill it.

Also I must not output title/cover/publish copy/subtitle rules/platform specs. My screen_text positions are placement within the edit — acceptable as in-script text. I'll avoid the word "字幕规则". Constraints mention "画面角落标注" — that's placement, fine.

Let me also double check: brief says "剪辑使用 VID-C01 试穿记录一素材" — good, my B1-B4 all draw from it.

One more check on explicit_non_promise: the brief's "不得表达" list is constraints, but explicit_non_promise is about what this content does NOT promise. I'll craft ~6 items combining brief's non-claims + content boundary.

Also — should I reflect the "衔接第 1 天/下一条是周宁"接力 in the script? No, not in content; but maybe in resource_note or a note that the ending boundary is exactly the handoff. I'll put a line in creative_concept or resource_note: 结尾的边界陈述即向周宁交出的问题（哪些需本人试穿）——保持原样，不添加对下一条的预告（无 CTA）. Good.

Also expression_subject: NATURAL_PERSON — 苏禾（口播主体）＋内部演示试穿人员（画面主体，非账号表达者）。为什么是他: 苏禾是 C01 事实确认人，判断的出处；试穿人员是记录中的行动者，不承担表达。账号声音与观察记录分离。I'll write that.

tension_mode: 让我再精确一点。格式: 六类强张力之一，和／或五类替代理由之一。I'll write:
`UNVERIFIED`（试穿中已经验证了"穿法可以调正式感"，但肩部/袖长/裤长的个人适配仍无定论——这是内容末尾刻意保留的未完成状态）＋ 替代理由：`Utility`（判断框架可复用：先分清"能靠穿法调"与"必须本人试"）＋ `Identity`（"白天开会、下班接孩子"正是目标顾客的连续一天）
And note: 两个并存（张力＋替代理由），不是二选一。

Hmm — is UNVERIFIED the right tension given the brief's wording "真实摩擦或决定性张力：试穿人在连续场景中觉得'完整西装＋衬衫'偏正式"? The decisive drive is the discomfort. But the discomfort is resolved by B3 (adjustment). What remains open is fit. The tension that carries viewers through the WHOLE piece: the discomfort opens at B2, resolved at B3; then B4 opens a new unresolved state (fit). For a 53s piece, the tension is more like "this combo isn't a slam dunk — what do we do?" which is UNVERIFIED-ish (试过了，还没定论) at the piece level: the overall verdict on "does this combo work for the continuous scenario" is only partially reached. Actually — the piece ends deliberately WITHOUT a complete verdict: formality adjustable (partial verified) + fit unanswerable here. So at the end, the question "这套组合适不适合我" remains UNVERIFIED/UNRESOLVED by design. I'll go with UNVERIFIED and explain. Actually, hmm, could it be UNRESOLVED_TRADEOFF (formal vs relaxed)? The record shows the tradeoff was partially resolved (adjustment worked for formality). So not an unresolved tradeoff at the end — the formality tradeoff was resolved within the demo; what's unresolved is personal fit, which is a verification gap, not a tradeoff. UNVERIFIED. ✓. And per CS-7 ⑥, since the record has two sides (partial success + unverified), tension must NOT be framed as fully resolved — UNVERIFIED respects that.

Also I should double check CS-2's note: "没有强张力时，填一条替代的继续消费理由" — I have a tension, so the alternative is additional. Both filled. Good.

Now the beat表 — I'll make each beat a structured block:

```
B1｜开场与身份边界
- 事实: 有 — 内部演示试穿，试穿人非现实顾客；"会议＋接送"为演示情境（brief 制作要求；C01 演示记录）
- 素材: 已确认 — VID-C01 试穿记录一开场可用段（选：能看清"有人在试衣服"的镜头）；苏禾出镜＝待产出·可控（可选，不阻塞本稿）
- state_change: 情境（观众先知道这段是什么，防止把演示人员读成顾客）
- 逐字稿（苏禾）:
  「先说清楚——这是内部演示试穿，不是顾客故事。」【准确区】
  「情境设定：白天开会，下班接孩子。」【准确区】
- zone: 准确区（身份与情境标注，逐字成立）；「情境设定」为仅有的术语，保持
```

Then B2, B3, B4 similarly.

For B3素材 I need the检索判据清单. Let me finalize:

```
检索判据清单（指向 B3 素材）
找什么：
① VID-C01 中"放松衬衫领口、袖口"的前后动作或可辨认的状态帧；
② VID-C01 中"脱下西装后单穿"的有效片段（能看到整体层次，正身或半侧身均可）。
找到算什么：
① ②都在 → B3 逐字稿整体成立，"正式感可调"以完整观察呈现；
只有① → 执行 brief 降级：只保留"领口袖口放松"的调整，结论降为"部分可调整"。
找不到怎么办：
①②都缺 → 用已确认照片＋口述补足调整过程（brief 降级条件）；
无论降级与否，"肩部/袖长/裤长仍需本人试穿"（B4）必须保留——它是本条的判断落点。
```

Good.

Now — the 必须使用的素材 IMG-P01 商品图: where exactly? B2 when naming the three items — quick cut of each product image with name. But reality: 商品图 is 棚拍静物, low info per industry guide; use as identification only. In B2: VO names the combo while images flash or while footage shows her in the combo. The brief says 必须使用, so include. I'll place in B2 as identification cutaways and note "只承担识别，不承担判断" in evidence_requirements. Fine.

Now let me write the whole output. Format with markdown headers per field. Keep it professional, dense, no fluff. Chinese for content, English field names.

Also, remember: "不得输出标题、封面、首帧、发布文案、字幕规则、平台适配等 Publishing &amp; Packaging 交付物". So creative_concept should not read like a title pitch. The direction names are internal concept labels, not publish titles — fine. I'll avoid catchy "titles" in the directions (name them functionally: 方向A「过程复盘」等).

One more consideration on voiceover[]: I'll list each VO line with location (beats). Since 苏禾 may optionally appear on camera in B1/B4, I'll note: 口播为主线；B1/B4 可选真人出镜（替换对应画外音），在产能内安排。 This goes in voiceover[] or resource_note. I'll put in both lightly.

Also — is there anything about the fact that this goes out on 苏禾's account (独立参战账号)? The content is 苏禾号发布, day 2-3, before 周宁. The script doesn't need to reference the account or the sequence. Skip.

Let me also reconsider beat count: 4 beats for ≤60s. The skill says short档 usually 2-3, but "以内容需要为准，在输出里声明实际用了几段". I'll declare: 本条短档（≤60s）实际用 4 段——因为 brief 的必表达结构（身份标注→原始方案与摩擦→调整→保留与未验证）本身是五步，合并后最少 4 段；每段状态变化见下. Good.

Also — audience_shift 的标注: （上游给定）because the brief provides 唯一主要顾客变化. I'll mark (上游给定).

Let me also write the creative_directions with the "不构成新方向的变化" warnings embedded implicitly by making the axes concrete. And I should make sure Direction B/C aren't mistakable for "同一方向的变体" — the axes show they're structurally different.

Also — CS-7 item ③: 位置搬错 — I don't move any facts across time/place. ✓

Also the "内部演示人员" identity: the brief says 出镜人为内部演示试穿人员. My B1 label says 内部演示试穿, not naming the person. Should the label also say "不是顾客故事"? Yes — that's the key anti-misreading. My screen text: 内部演示试穿 · 非顾客故事. Good.

Also, one subtle point: the brief says "如果制作人员仍希望提供下一步，只能使用上游已确认的统一承接说明作为可选结尾，且不得替代判断价值；更推荐本条不加。" My content has no CTA. In constraints I'll note: 可选统一承接说明不采用（推荐不加；如制作方坚持，需另走上游确认，且不得置于判断落点之后替代判断价值）。Hmm — actually, should I include the unified reception statement as an option? The brief's CTA section says: 本条无 CTA...如制作人员仍希望提供下一步，只能使用上游已确认的统一承接说明作为可选结尾，且不得替代判断价值；更推荐本条不加。Since cta_contract = NO_CTA, I'll design without it and note the option exists but is not recommended and requires upstream confirmation. Keep it in constraints/missing.

Let me now also think about whether to write the 苏禾 "真人出镜" variant. Since the brief lists 苏禾出镜方式 as a must-confirm before production, and my script is VO-based, the variant is: B1/B4 lines delivered face-to-camera. This doesn't change the script text. I'll note in assumptions: 本稿口播与出镜两版共用同一逐字稿；出镜版只需在 B1/B4 把 VO 转为对镜讲述。 Missing[]: 苏禾出镜方式待确认。

OK — also the skill says: "收到 return_from_downstream[] 时" — none received, skip. I could note: 无回改建议.

Let me also add the "核心共享证据链" context to creative_concept briefly (C01 记录一完整事实链支撑全过程，无需补写任何未登记事实). Good for rationale.

Now — a final review of the draft lines against CS-7 (no fabricated specifics):

「先说清楚——这是内部演示试穿，不是顾客故事。」✓ (from brief 制作要求)
「情境设定：白天开会，下班接孩子。」✓ ("白天会议、下班接送孩子" — 唯一顾客情境的用词；作为演示情境标签成立)
「原本搭的是：廓形西装、垂感阔腿裤、雾蓝棉混衬衫。」✓ (产品名 from B01)
「开会，成立。」✓ (C01: 完整组合满足会议场景)
「但试穿记录里记了一笔：连续穿下来，层次偏正式。」✓ (C01 初始问题: 连续穿着时层次偏正式)
「调整不是换单品。」✓ (发挥区引导)
「西装和阔腿裤留着，只把衬衫领口、袖口放松一点。」✓ (C01: 保留西装和阔腿裤，将衬衫袖口与领口处理得更放松)
「再脱掉西装，比了一下单穿。」✓ (C01: 比较脱下西装后的单穿效果)
「这组衣服的正式感，可以靠穿法往下调——但这是这次试穿里的观察，不是所有人的标准答案。」✓ (已确认观察 + 限定语)
「最后留下来的：西装，和阔腿裤。」✓ (C01 保留项)
「没被回答的：肩部、袖长、裤长。」✓ (待验证变量)
「这三处合不合适，一条视频回答不了——得本人试穿。」✓ (待验证变量表述)
「内容能把判断做到这儿。再往下，只能本人试过才知道。」✓ (发挥区收束)

Wait — "往下调" — 已经确认观察是"正式程度可以通过穿法调整"。 "往下调" 具体化为"降低正式程度"——方向符合记录（偏正式→放松），但这算不算具体化超出来源？The record says 调整 = 保留西装阔腿裤、放松领口袖口、比较单穿。这些动作的客观方向就是降低正式感。而观察结论"正式程度可以通过穿法调整"——"调整"的方向在这个记录里是从偏正式往放松调。说"往下调"是对已登记动作的忠实概括，不构成新事实。OK.

But hold on — "正式感，可以靠穿法往下调" — is this too close to a performance claim? It's the registered observation (f4). Fine.

Also double-check: 没有出现"显瘦/闭眼入/人人可穿" — ✓. 没有预约/名额 — ✓. 没有把试穿人描述为顾客 — ✓. 没有拼接 D01 — ✓. 没有性能补写 — ✓. 没有销售声称 — ✓.

Also — "比了一下单穿" — could "单穿" be misread as "单穿这件衬衫"? The record: "脱下西装后的单穿效果" — meaning wearing shirt+pants without blazer. "比了一下单穿" in context (after "再脱掉西装") is clear: 脱掉西装后的状态. Fine; maybe add "效果" — 「再脱掉西装，比了一下单穿的效果。」 Minor. I'll keep 「再脱掉西装，比了一下单穿效果。」(加"效果"更准确).

Alright — also verify the 素材 tags don't drift: IMG-P01 = 已确认 (brief says 已整理商品图, must use). I'll mark 已确认 with note "已整理，定位由剪辑执行".

One more: 苏禾's lines in B2-L3 "但试穿记录里记了一笔" — the "记了一笔" implies a written record exists. C01 is indeed a 登记试穿记录. ✓.

Now the fact_refs[].type assignments once more:

f1 商品事实（三件名称/品类）— source: 商品登记表/B01，确认人周宁 — type: EXTERNAL（品类与登记事实可对实物核验）
Hmm — actually let me reconsider. Is "廓形西装、垂感阔腿裤、雾蓝棉混衬衫" externally verifiable? Yes, against the product/barcode. EXTERNAL.
f2 C01 初始问题（完整组合满足会议、连续穿着层次偏正式）— source C01（内部登记），确认人苏禾 — INTERNAL
f3 调整过程 — C01 — INTERNAL
f4 已确认观察（正式感可调）— C01（苏禾专业判断）— SUBJECTIVE
f5 被保留（西装和阔腿裤）— C01 — INTERNAL
f6 待验证变量（肩部/袖长/裤长需本人试穿）— brief/C01（苏禾专业判断+显式能力边界）— KNOWN_UNKNOWN（压制 SUBJECTIVE：本条内容承诺的一部分是"这些答不了"）
f7 内部演示身份与演示情境 — Content Brief（制作要求）— INTERNAL（有记录可查、外部核验不了，且是制作指令）

Also maybe f8: 无 CTA 决定 — not a fact_ref, it's a constraint. Skip.

evidence_requirements — let me finalize as a list:
1. B1：试穿画面首次出现时必须同帧或同段出现身份标注（「内部演示试穿 · 非顾客故事」）——导演要求：标注不得晚于试穿人正面清晰入镜的画面。
2. B2：IMG-P01 三件商品图只承担"被识别"功能，不得用商品图承载任何穿着效果或性能判断；"开会，成立"是已登记观察，不得在画面上用"会议成功"类示意强化为普通结论。
3. B3：SUBJECTIVE 判断"正式感可调"——画面只呈现已登记动作（放松领口袖口、脱西装单穿）；禁止用音乐骤起、前后对比分屏、慢镜高亮等任何手段"证明"该判断；禁止把调整剪成惊人反转（brief 硬禁）。
4. B4：KNOWN_UNKNOWN 边界——画面只能呈现"这里没有答案"（如试穿人镜前查看肩部/袖长的动作），不得呈现"答案本该是什么"；不给试穿人的身体下任何评价（肩宽不合适、袖长刚好等一律不得出现）。
5. 全程：试穿人的可闻话语（如有）只允许来自 C01 已登记内容；C01 未登记的语句不得进入成片——剪辑时需先核对。

Wait — #5: does C01 contain any registered verbatim quotes? The brief doesn't quote the try-on person verbatim. So effectively the footage should avoid her audible unregistered speech, or the edit must verify. This is a constraint for PD. Good.

I think that's a comprehensive evidence section.

constraints[] (final):
- 身份红线：不得把内部试穿人员描述为现实顾客；"会议＋接送"是演示情境不是真实顾客经历（B1 标注 + 全片不得违背）
- 不得将 C01 试穿记录与 D01 匿名问题拼接成同一顾客故事（本条只用 C01）
- 不得声称适合所有"职场妈妈"或任何具体适穿人群
- 不得补写防水/防风/抗皱/保暖/显瘦等未登记性能
- 不得声称调整后提高了销售或顾客更喜欢
- 不得把调整剪成惊人反转
- 不使用"显瘦""闭眼入""人人可穿"等话术
- 不出现预约成功、名额稀缺、到店引导等表述；本条无 CTA（统一承接说明不采用；如制作方坚持需先走上游确认）
- 不给试穿人身体下判断（肩宽/袖长/裤长只说"需本人试穿"，不说"她合适/不合适"）
- 全程不得出现未登记原话的试穿人语音（如有，先核对 C01）

Hmm — "到店引导" — the brief's no-CTA but the campaign's经营任务 includes 到店试穿引导 at the campaign level. For THIS piece, no CTA. The constraint: 本条内不出现行动召唤. "到店引导" is broader — I'll say 不出现任何行动召唤（到店、预约、私信、评论区）即可，not banning the concept globally. Let me rephrase: 不出现预约成功/名额稀缺表述；本条无 CTA——不出现任何行动召唤（预约、到店、私信、评论引导）。✓.

assumptions[] final:
- platform：输入槽位为小红书，但 brief 明确"最终发布平台未确认，由 Founder 锁定"——本稿按平台中立母版处理，时长 ≤60s 对所有候选平台成立；不进入平台规格设计（留给下游，且 brief 明确在平台锁定前不做）
- 苏禾出镜方式未定：本稿按"口播为主线、B1/B4 可选真人出镜"设计，两版共用同一逐字稿；在 3 小时拍摄＋补录产能内可安排
- 无真实顾客原话可用：C01 为内部演示记录，不是顾客故事；试穿人语音默认视为未登记，除非与 C01 核对
- 单穿比较子场景的素材可用性按"待检索"处理，检索判据已给出
- duration_band 短档（≤60s），实际使用 4 个 beat
- 出镜人身体信息不进入内容（不给试穿人身体下判断）

missing[] final:
- 最终发布平台（Founder 锁定中；锁定前不下游做平台规格）
- 苏禾出镜方式（真人出镜或旁白）——brief 列在"进入脚本与拍摄设计前必须确认"事项
- 是否采用统一承接说明（建议不采用；如需，走上游确认）
- VID-C01 中"脱下西装单穿"子场景的可用性（检索判据清单已给，结果决定 B3/B4 结论强度）

Also resource_note:
- 出镜与声音：内部演示试穿人员（画面主体，来自 VID-C01 已有素材）；苏禾（口播全程；若出镜，B1 或 B4 对镜讲述，在 3h 拍摄＋30min 补录内安排）
- 现有素材：VID-C01 试穿记录一原始片段（必须使用）、IMG-P01 三件商品图（必须使用）、BROLL-S01 门店空镜（仅转场，不承担判断）
- 待产出：苏禾口播录音（3h 拍摄内或补录完成）；（可选）苏禾出镜镜头
- 接力说明：本条结尾的边界陈述即向周宁交出的问题（哪些需本人试穿）——成片中不得添加预告下一条或跨账号指引（无 CTA）

OK. I think I have everything. Let me now also double check the opening field: "视频＝前 3 秒画面＋逐字第一句". I'll write:

opening:
- 前 3 秒画面: VID-C01 中试穿人入镜的第一个有效镜头（选片判据：能看清"有人在试衣服"；不选任何可能被读成"顾客在抱怨"的表情/动作）；画面角落同帧出现「内部演示试穿 · 非顾客故事」标注
- 逐字第一句: 「先说清楚——这是内部演示试穿，不是顾客故事。」（苏禾，画外）

Good.

Also creative_directions[] — let me write them fully:

方向 A「过程复盘」（选中）：
- 核心矛盾：同一套组合在"会议成立"与"连续穿着偏正式"之间——输入里真实登记的不满足感
- 叙事发动机：调整过程本身的重演：保留→放松→脱西装比较，观众跟着走一遍
- 人物关系：苏禾带着观众复盘记录；试穿人员是过程里的共同尝试者
- 信息释放顺序：身份边界 → 原始方案 → 摩擦 → 调整 → 保留 → 未验证
- 视觉前提：VID-C01 试穿素材为主体，苏禾旁白贯穿

方向 B「摩擦先行」：
- 核心矛盾：正式与放松同时被需要，压在同一件衬衫上
- 叙事发动机：试穿中"觉得太正式"的那个瞬间作为引力点，再往回拆原因与解法
- 人物关系：试穿者（内部演示人员）第一人称在场，苏禾画外陪伴
- 信息释放顺序：感受先行 → 回拆 → 解法尝试 → 部分保留 → 边界
- 视觉前提：动作/反应特写优先，情绪在场感更强

方向 C「边界先行」：
- 核心矛盾：内容能替你判断什么，与必须本人试过才知道什么——把"答不了"摆到最前面
- 叙事发动机：边界划线：先亮能力边界，再举证能答的部分
- 人物关系：苏禾对镜头直接声明，姿态是坦白的边界告知者
- 信息释放顺序：边界结论 → 证据 → 点名未验证变量 → 交给本人
- 视觉前提：苏禾正面出镜为主，试穿片段作证据插页

These differ: A vs B on 矛盾/发动机/人物关系/信息顺序/视觉 all 5; A vs C on 矛盾/发动机/信息顺序/视觉 (4) — 人物关系 both 苏禾-led but posture differs (复盘引领者 vs 边界声明者), I'll acknowledge in the rationale that A vs C share "苏禾作为口播主体" but differ in posture; the三轴判据 is satisfied by the other four. B vs C all 5 differ. OK — in the creative_concept I'll state the axis-difference counts explicitly.

creative_concept (selected + why):
选中方向 A「过程复盘」，原因（指名判据）：
- 与 brief 强制叙事结构同构：事实→摩擦→调整→保留→未验证，A 的发动机就是这条线；B 需把感受前置、C 需把边界前置，都违反 brief 给定的结构顺序
- 接力需要：下一条周宁要引用的是"苏禾的试穿观察"本身——A 让过程完整可见可引；B 压成感受、C 压成证据，都会让周宁失去可引用的过程
- 账号姿态：陪伴尝试、不急于给唯一答案——A 把结论压到最后一拍；B/C 都让结论前置，与姿态相反
- 素材效率与风险：主素材是 VID-C01 记录，A 全程以它为载体；C 依赖苏禾正面出镜（出镜方式未确认，风险高）；B 的最优剪辑是试穿者特写（误读为真实顾客的风险最高，撞 brief 硬禁）
- 三轴判据：A 与 B 五轴全差；A 与 C 差四轴（仅"苏禾为口播主体"相近，但姿态不同：复盘引领者 vs 边界声明者）

Also add: 方向 A 的落点即 brief 的"唯一新判断"——同一组合的正式程度可调，但肩部/袖长/裤长只能本人试穿确认。

Now the beat count declaration — the skill wants "在输出里声明实际用了几段". I'll include in script_beats intro: 本条 ≤60s，实际 4 段（brief 必表达为五步，首步身份标注并入 B1；每段状态变化在段内标注）.

Let me also reconsider: should B1's label be on-screen AND spoken? Overlap risk. In a 53s piece, speaking it in B1-L1 plus screen text at the same time is heavy but necessary (the brief requires 字幕或口播, either/or — I'll do both lightly, or at least one. Since the brief says "以字幕或口播形式标注", one suffices. But some viewers watch muted; on Xiaohongshu, both is common. I'll specify: 口播主标（L1），同帧屏幕文字作冗余标注（S1），不重复占用时长。 Fine.

Also, screen_text positions — I'll give:
- S1｜B1 全程角落（叠加或紧随首帧）｜「内部演示试穿 · 非顾客故事」
- S2｜B2 三件商品图切换时，图内/图下｜「廓形西装」「垂感阔腿裤」「雾蓝棉混衬衫」
- S3｜B4 最后两句期间，屏幕下方｜「肩部 · 袖长 · 裤长 → 需本人试穿」

voiceover[]:
- VO-B1｜B1 全程｜苏禾（画外）：「先说清楚——这是内部演示试穿，不是顾客故事。」「情境设定：白天开会，下班接孩子。」
- VO-B2｜B2 全程｜苏禾（画外）：「原本搭的是：廓形西装、垂感阔腿裤、雾蓝棉混衬衫。」「开会，成立。」「但试穿记录里记了一笔：连续穿下来，层次偏正式。」
- VO-B3｜B3 全程｜苏禾（画外）：「调整不是换单品。」「西装和阔腿裤留着，只把衬衫领口、袖口放松一点。」「再脱掉西装，比了一下单穿效果。」「这组衣服的正式感，可以靠穿法往下调——但这是这次试穿里的观察，不是所有人的标准答案。」
- VO-B4｜B4 全程｜苏禾（画外）：「最后留下来的：西装，和阔腿裤。」「没被回答的：肩部、袖长、裤长。」「这三处合不合适，一条视频回答不了——得本人试穿。」「内容能把判断做到这儿。再往下，只能本人试过才知道。」
- 附注：B1/B4 可选真人出镜（对镜讲述同一逐字稿），口播与出镜共用文本。

Wait — the line "一条视频回答不了" — "一条视频" vs "这条视频"? "一条视频回答不了" is fine and general; "这条视频" is more precise (this specific content). Use 「这条视频回答不了」. OK.

Also — in VO-B3, "西装和阔腿裤留着" — earlier I wrote "西装和阔腿裤留着" in L2 and B4-L1 "最后留下来的：西装，和阔腿裤。" — repeated emphasis is intentional (the brief's structure: 指出去被保留的部分). Fine, but maybe vary: B3-L2 「西装和阔腿裤先不动」 vs B4-L1 「最后留下来的：西装，和阔腿裤。」 Hmm — "先不动" adds a temporal nuance not in the record. Keep "留着" both times — repetition is a deliberate structural emphasis (this is a state recurrence, not 停驻). Actually, slight variation avoids redundancy: B3-L2 「西装和阔腿裤留着，只动衬衫——领口、袖口放松一点。」 then B4-L1 「最后留下来的：西装，和阔腿裤。」 Hmm "只动衬衫" — the adjustment is to the shirt (loosen collar/cuffs), and blazer was kept then removed for comparison. "只动衬衫" could conflict with "再脱掉西装" (blazer was removed momentarily). Let me redo: 「西装和阔腿裤留着，衬衫领口、袖口放松一点。」 — accurate: kept blazer+pants, adjusted shirt. Then "再脱掉西装" — the blazer comparison. And B4: 最后留下来的——西装和阔腿裤。The retention is: over the whole process, blazer &amp; pants are the pieces you keep relying on. Consistent. OK, final VO-B3: 「调整不是换单品。」「西装和阔腿裤留着，只把衬衫领口、袖口放松一点。」「再脱掉西装，比了一下单穿效果。」「这组衣服的正式感，可以靠穿法往下调——但这是这次试穿里的观察，不是所有人的标准答案。」

Hmm, "可以靠穿法往下调" — wait, if the blazer is taken off in the comparison, that's also a穿法 choice. "靠穿法调" covers it. Fine.

One more nuance — "不是所有人的标准答案" vs brief "不构成对所有人和所有场景的通用答案" — mine mentions "所有人" but not "所有场景". Should I include场景? 「不是所有人的标准答案，也不是所有场景的通用答案」— that's wordy. The hedge's job: prevent generalization. "不是所有人的标准答案" covers the person dimension; the场景 dimension (this was one meeting+pickup demo scenario) is implied by "这次试穿里". Alternatively: 「但只限于这次试穿，不是通用答案。」 — covers both. Let me use: 「——但只限这次试穿里的观察，不是通用答案。」 That's tighter and covers person+scenario ("通用" implies both). Good: 「这组衣服的正式感，可以靠穿法往下调——但只限这次试穿里的观察，不是通用答案。」 Nice and clean.

Wait — is "只限这次试穿里的观察" accurate? The confirmed observation is based on C01 (one try-on record). Yes. And the professional judgment "正式程度可以通过穿法调整" is stated in the brief as a general judgment ("已确认观察...专业判断，基于 C01 已登记试穿观察"). Hmm — the brief states it as "已确认观察'同一组合在正式程度上可以通过穿法调整'：专业判断，基于 C01 已登记试穿观察；确认人苏禾。" So the claim IS a professional judgment — 苏禾 asserts it as a conclusion from the observation. But the brief also says "不构成对所有人和所有场景的通用答案". So the honest presentation: the judgment is 苏禾's, grounded in this one try-on. My hedge "只限这次试穿里的观察" might be too weak — it could undermine the professional judgment's validity. Balance: 「这是这次试穿里的观察，到这一步我先不下'人人都行'的结论。」 Hmm. Let me think about what the hedge must convey: the judgment is 苏禾's professional observation-based conclusion, but it doesn't generalize to all bodies/scenarios. The 限定语 that must survive: "这次试穿里" (basis) + "不构成对所有人和所有场景的通用答案" (boundary). So: 「这组衣服的正式感，可以靠穿法往下调——这是这次试穿里观察到的，不是一个对所有人和所有场景通用的结论。」 A bit long for VO. Shorter: 「——这是这次试穿里的观察，不是对所有人都通用的结论。」 The "场景" part is dropped... Actually "对所有人通用" plus "这次试穿里" implies scenario specificity. Hmm, the brief's exact: "不构成对所有人和所有场景的通用答案". To be safe, keep both: 「——但这是这次试穿里的观察，不是对所有人、所有场景的通用答案。」 That's 16 chars extra, OK for VO. I'll use that.

Final B3-L4: 「这组衣服的正式感，可以靠穿法往下调——但这是这次试穿里的观察，不是对所有人、所有场景的通用答案。」

Good.

Fact_refs f4 update: the claim as stated includes the generalization boundary. Fine.

Also recheck B2-L2 "开会，成立。" — should it include "会议场景" hedge? The record: "完整西装＋衬衫组合满足会议场景". My terse "开会，成立。" is a faithful compression. OK.

Now — assemble everything into the final response. Also check: the skill says the script_beats each need: beat_id | 事实 | 素材 | state_change | 逐字稿 | zone. I'll use a structured list per beat.

Also the intro notes: 确认使用的来源 (content_origin_mode[] = 现拍 + 已有素材剪辑). And maybe a line: 无 return_from_downstream。

Let me also add a brief line up top? The skill's output contract starts directly with content_origin_mode[]. I'll follow the contract directly without extra preamble. Maybe one line noting "无下游回改建议" — the contract doesn't have that field; return_from_downstream is an input. I'll skip it or fold into assumptions. Ah — I could add it to assumptions: 无 return_from_downstream。 Fine.

Length of final output: this is a dense deliverable; aiming for completeness without padding. Let me write it.

One more consideration on the 检索判据清单 — the contract places it between question_list[] and skeleton. In my output, since B3 is 待检索, I fill it there.

Wait — also double-check the B3 素材=待检索 vs the two-question table: "待检索: 存在但没人看过（未编目的存量素材）——这不是'有'，检索成本可能高于重拍". Is VID-C01 "没人看过"? The brief's team knows C01 record exists and its content (the record is registered with content summary). But the specific sub-scene (blazer-off) availability is unverified at script stage. "待检索" fits the spirit: existence asserted but specific shots unverified. To be precise, I'll mark B3's 素材 as 待检索（记录整体已确认，子场景可用性未过片） and give the search criteria. Good.

Also — one thing: B4's 素材 being "已确认" but its conclusion strength depends on B3's retrieval result — I noted the linkage. Good.

Let me also make sure I don't violate: "不得输出...字幕规则" — my screen_text is content not styling; I said placement only. OK.

Draft the final response now. I'll keep the format tight with markdown. Since the output contract uses a code-block-like field list, I'll use headings matching the field names. No code fences needed. Let me write.

Actually — one more check on "expression_subject" field: "五类之一 + 为什么是他". I'll write: NATURAL_PERSON — 苏禾（账号持续表达者，口播主体）＋内部演示试穿人员（画面主体，非表达主体）... why: 苏禾是 C01 事实确认人，判断有出处；试穿人员承担行动不承担表达，避免把她误读为顾客。 Good.

And tension_mode — format: I'll write `UNVERIFIED`（六类强张力）＋ `Utility`、`Identity`（替代理由，与张力并存）. With a short explanation.

Let me write out the response.
</think>content_origin_mode[]         `["现拍", "已有素材剪辑"]` —— 逐 beat 见 script_beats 的「事实／素材」两栏；必须传给下游，PD 不得按纯现拍处理

creative_directions[]

**方向 A「过程复盘」（选中）**
- 核心矛盾：同一套组合在「会议成立」与「连续穿着偏正式」之间——C01 登记的真实不满足感
- 叙事发动机：调整过程本身的重演（保留 → 放松 → 脱西装比较），观众跟着走一遍
- 人物关系：苏禾带观众复盘记录；试穿人员是过程里的共同尝试者
- 信息释放顺序：身份边界 → 原始方案 → 摩擦 → 调整 → 保留 → 未验证
- 视觉前提：VID-C01 试穿素材为主体，苏禾旁白贯穿

**方向 B「摩擦先行」**
- 核心矛盾：正式与放松同时被需要，压在同一件衬衫上
- 叙事发动机：试穿中「觉得太正式」的那个瞬间作为引力点，再往回拆原因与解法
- 人物关系：试穿者（内部演示人员）第一人称在场，苏禾画外陪伴
- 信息释放顺序：感受先行 → 回拆 → 解法尝试 → 部分保留 → 边界
- 视觉前提：动作／反应特写优先，情绪在场感更强

**方向 C「边界先行」**
- 核心矛盾：内容能替你判断什么，与必须本人试过才知道什么——把「答不了」摆到最前面
- 叙事发动机：边界划线：先亮能力边界，再举证能答的部分
- 人物关系：苏禾对镜头直接声明，姿态是坦白的边界告知者
- 信息释放顺序：边界结论 → 证据 → 点名未验证变量 → 交给本人
- 视觉前提：苏禾正面出镜为主，试穿片段作证据插页

三轴判据：A 与 B 五轴全差；A 与 C 差四轴（仅「苏禾为口播主体」相近，但姿态不同：复盘引领者 vs 边界声明者）；B 与 C 五轴全差。

creative_concept

选中方向 A「过程复盘」，理由（指名判据，非「更抓人」）：
- **与 brief 强制叙事结构同构**：事实→摩擦→调整→保留→未验证，A 的发动机就是这条线；B 需把感受前置、C 需把边界前置，都违反 brief 给定的结构顺序。
- **接力需要**：下一条周宁要引用的是「苏禾的试穿观察」本身——A 让过程完整可见可引；B 压成感受、C 压成证据，都会让周宁失去可引用的过程。
- **账号姿态**：陪伴尝试、不急于给唯一答案——A 把结论压到最后一拍；B、C 都让结论前置，与姿态相反。
- **素材效率与风险**：主素材是 VID-C01 记录，A 全程以它为载体；C 依赖苏禾正面出镜（出镜方式未确认，风险高）；B 的最优剪辑是试穿者特写（被误读为真实顾客的风险最高，撞 brief 硬禁）。
- **落点一致**：A 的落点即 brief 的「唯一新判断」——正式程度可调，但肩部/袖长/裤长只能本人试穿确认。

audience_shift

让目标顾客从按单件新品和表面风格被动浏览，进展为能够用自己的一个真实穿着问题，套用「哪些问题能靠穿法调整、哪些必须本人试穿」的判断，作出初步比较或排除，并识别下一步需本人试穿确认什么。（上游给定）

content_promise

这条内容承诺：让观众看到一个已登记试穿记录里的调整过程，并明确切分出「能通过穿法调整」与「只能由本人试穿确认」两类问题。不承诺回答个人适配，不承诺这套组合适合所有人。

explicit_non_promise[] —— 全链只读继承，任何一段不得加东西回来
- 不承诺给出「这套组合适不适合你」的答案
- 不承诺肩部、袖长、裤长的适配判断
- 不承诺该组合适合所有会议、所有连续场景或任何具体人群（不适用于所有「职场妈妈」）
- 不承诺任何性能表现（防水／防风／抗皱／保暖／显瘦）
- 不承诺这是顾客见证或真实顾客经历
- 不承诺调整带来任何销售、偏好或经营结果
- 无 CTA：不承诺预约、到店、名额或其他行动结果

tension_mode

`UNVERIFIED`（六类强张力）——「试过了，还没定论」：试穿验证了正式感可调，但肩部/袖长/裤长的个人适配仍无定论，这是内容末尾刻意保留的未完成状态。
＋ 替代理由（与张力并存）：`Utility`（判断框架可复用：先分清「能靠穿法调」与「必须本人试」）＋ `Identity`（「白天开会、下班接孩子」正是目标顾客的连续一天）。
两个并存，不是二选一：张力负责看完，Utility 负责值得存，Identity 负责愿意转。

expression_subject

`NATURAL_PERSON` —— 苏禾（账号持续表达者，口播主体）＋ 内部演示试穿人员（画面主体，非表达主体）。
为什么：苏禾是 C01 事实确认人，判断有出处；试穿人员承担行动、不承担表达，避免她被误读为顾客。账号声音与观察记录分离。

opening

- 前 3 秒画面：VID-C01 中试穿人入镜的第一个有效镜头（选片判据：能看清「有人在试衣服」；不选任何可能被读成「顾客在抱怨」的表情或动作）；画面角落同帧出现「内部演示试穿 · 非顾客故事」标注。
- 逐字第一句（苏禾，画外）：「先说清楚——这是内部演示试穿，不是顾客故事。」

script_beats[]

本条 ≤60s，实际 4 段。brief 必表达为五步，身份标注并入 B1；每段状态变化见段内标注。无「停驻」段——结尾是向前交接的边界陈述，不是停下来的未完成。

**B1｜开场与身份边界**
- 事实：`有`——内部演示试穿，试穿人非现实顾客；「会议＋接送」为演示情境（brief 制作要求；C01 登记）
- 素材：`已确认`——VID-C01 试穿记录一开场可用段；苏禾出镜＝`待产出·可控`（可选，不阻塞本稿）
- state_change：**情境**（观众先知道这段是什么，防止把演示人员读成顾客）
- 逐字稿（苏禾）：「先说清楚——这是内部演示试穿，不是顾客故事。」「情境设定：白天开会，下班接孩子。」
- zone：准确区（身份与情境标注，逐字成立）

**B2｜原始搭法与真实摩擦**
- 事实：`有`——原始组合＝廓形西装＋垂感阔腿裤＋雾蓝棉混衬衫（B01/商品登记表）；初始问题＝完整组合满足会议场景，但连续穿着时层次偏正式（C01）
- 素材：`已确认`——VID-C01 完整组合／试穿过程片段 ＋ IMG-P01 三件商品图（识别用）
- state_change：**信息**（观众知道原始方案与已登记的摩擦；预期被轻微打断——这组合不是静态成立的）
- 逐字稿（苏禾）：「原本搭的是：廓形西装、垂感阔腿裤、雾蓝棉混衬衫。」「开会，成立。」「但试穿记录里记了一笔：连续穿下来，层次偏正式。」
- zone：准确区（组合与记录陈述）；「原本搭的是」「但」为发挥区连接

**B3｜调整过程与本次观察**
- 事实：`有`——调整过程＝保留西装和阔腿裤，放松衬衫领口袖口，比较脱下西装后的单穿效果（C01）；已确认观察＝同一组合正式程度可通过穿法调整（苏禾专业判断，基于 C01）
- 素材：`待检索`——VID-C01 内「放松领口袖口」「脱下西装单穿」两个子场景的可用性（记录整体已确认，具体子场景本环节未过片）；检索判据清单见下
- state_change：**理解**（正式与否不只由单品决定，穿法能调）＋ **判断**（同一组合可覆盖正式到放松的区间）
- 逐字稿（苏禾）：「调整不是换单品。」「西装和阔腿裤留着，只把衬衫领口、袖口放松一点。」「再脱掉西装，比了一下单穿效果。」「这组衣服的正式感，可以靠穿法往下调——但这是这次试穿里的观察，不是对所有人、所有场景的通用答案。」
- zone：动作事实＝准确区；「正式感可以靠穿法往下调」＝主观区（专业判断）；「这次试穿里」「不是对所有人、所有场景的通用答案」＝主观区限定语，**一个字都不能删**

**B4｜保留、未验证与接手**
- 事实：`有`——被保留＝西装和阔腿裤（C01）；待验证变量＝肩部、袖长、裤长仍需本人试穿，不能由内容直接回答（brief/C01）
- 素材：`已确认`——VID-C01 单穿效果或试穿人镜前检查片段；结论强度随 B3 检索结果联动（降级路径见检索判据清单）
- state_change：**判断**（什么成立了、什么没成立被明确切分）＋ **预期**（观众对「内容能回答什么」的预期被重置——这正是本条内容承诺）
- 逐字稿（苏禾）：「最后留下来的：西装，和阔腿裤。」「没被回答的：肩部、袖长、裤长。」「这三处合不合适，这条视频回答不了——得本人试穿。」「内容能把判断做到这儿。再往下，只能本人试过才知道。」
- zone：前两句＝准确区（C01 保留项与待验证变量点名）；第三句＝主观区判断，但按 `KNOWN_UNKNOWN` 处理（显式声明「这条内容不知道」是本条承诺的一部分，压过 `SUBJECTIVE`）；第四句＝发挥区收束，不改变事实边界

question_list[]

`NOT_APPLICABLE` —— 无「事实=无」的 beat。C01 记录完整，无需向人追问即能写死逐字稿。

检索判据清单（指向 B3 素材）

- 找什么：
  ① VID-C01 中「放松衬衫领口、袖口」的前后动作或可辨认的状态帧；
  ② VID-C01 中「脱下西装后单穿」的有效片段（能看到整体层次，正身或半侧身均可）。
- 找到算什么：
  ①②都在 → B3 逐字稿整体成立，「正式感可调」以完整观察呈现；B4「西装和阔腿裤被保留」由同段素材支撑。
  只有① → 执行 brief 降级：只保留「领口袖口放松」的调整，B4 结论强度降为「部分可调整」。
- 找不到怎么办：
  ①②都缺 → 用已确认照片＋口述补足调整过程（brief 降级条件）。
  无论降级与否，「肩部、袖长、裤长仍需本人试穿」（B4）必须保留——它是本条的判断落点。

skeleton

`NOT_APPLICABLE` —— 无「事实=无」的 beat，不需要等答案回来再重写。段落关系已由逐字稿锁定：B1 立身份边界 → B2 立事实与摩擦 → B3 走调整并给出有边界的观察 → B4 切分保留与未验证并交给本人。

voiceover[]

- VO-B1｜B1 全程｜苏禾（画外）：「先说清楚——这是内部演示试穿，不是顾客故事。」「情境设定：白天开会，下班接孩子。」
- VO-B2｜B2 全程｜苏禾（画外）：「原本搭的是：廓形西装、垂感阔腿裤、雾蓝棉混衬衫。」「开会，成立。」「但试穿记录里记了一笔：连续穿下来，层次偏正式。」
- VO-B3｜B3 全程｜苏禾（画外）：「调整不是换单品。」「西装和阔腿裤留着，只把衬衫领口、袖口放松一点。」「再脱掉西装，比了一下单穿效果。」「这组衣服的正式感，可以靠穿法往下调——但这是这次试穿里的观察，不是对所有人、所有场景的通用答案。」
- VO-B4｜B4 全程｜苏禾（画外）：「最后留下来的：西装，和阔腿裤。」「没被回答的：肩部、袖长、裤长。」「这三处合不合适，这条视频回答不了——得本人试穿。」「内容能把判断做到这儿。再往下，只能本人试过才知道。」
- 附注：B1/B4 可选真人出镜（对镜讲述同一逐字稿），口播与出镜共用文本，在 3 小时拍摄＋补录产能内安排。

screen_text[]

- S1｜B1 全程角落（不得晚于试穿人正面清晰入镜的画面）｜「内部演示试穿 · 非顾客故事」
- S2｜B2 三件商品图切换时，图内／图下｜「廓形西装」「垂感阔腿裤」「雾蓝棉混衬衫」
- S3｜B4 最后两句期间，屏幕下方｜「肩部 · 袖长 · 裤长 → 需本人试穿」

fact_refs[]

| 内容 | 来源 | type |
|---|---|---|
| 三件单品名称与品类（廓形西装／垂感阔腿裤／雾蓝棉混衬衫） | 商品登记表／B01，确认人周宁 | `EXTERNAL`（品类与登记事实可对实物核验） |
| C01 初始问题：完整组合满足会议场景，但试穿人认为连续穿着时层次偏正式 | C01 内部登记，确认人苏禾 | `INTERNAL`（有记录可查、外部核验不了） |
| 调整过程：保留西装和阔腿裤，放松衬衫领口袖口，比较脱下西装后的单穿效果 | C01，确认人苏禾 | `INTERNAL` |
| 已确认观察：同一组合正式程度可通过穿法调整（含不构成通用答案的边界） | C01，苏禾专业判断 | `SUBJECTIVE`（有出处，但不是外部事实；不得用画面强化） |
| 被保留：西装和阔腿裤 | C01 | `INTERNAL` |
| 待验证变量：肩部、袖长、裤长仍需本人试穿，不能由内容直接回答 | brief/C01，苏禾专业判断 | `KNOWN_UNKNOWN`（显式声明「内容不知道」是本条承诺的一部分，压过 `SUBJECTIVE`；主语＝这条内容／苏禾，非角色） |
| 内部演示身份与「会议＋接送」演示情境 | Content Brief 制作要求 | `INTERNAL`（有记录可查、外部核验不了；属制作指令层） |

evidence_requirements[] —— 交给 Production Director

1. B1：试穿画面首次出现时必须同帧或同段出现「内部演示试穿 · 非顾客故事」标注，不得晚于试穿人正面清晰入镜。
2. B2：IMG-P01 三件商品图只承担「被识别」，不得用商品图承载任何穿着效果或性能判断；「开会，成立」是已登记观察，画面不得用「会议成功」类示意把它放大成普遍结论。
3. B3：`SUBJECTIVE` 判断「正式感可调」——画面只呈现已登记动作（放松领口袖口、脱西装单穿）；禁止用音乐骤起、前后对比分屏、慢镜高亮等手段「证明」该判断；禁止把调整剪成惊人反转（brief 硬禁）。
4. B4：`KNOWN_UNKNOWN` 边界——画面只能呈现「这里没有答案」（如试穿人镜前查看肩部／袖长的动作），不得呈现「答案本该是什么」；不给试穿人的身体下任何评价（「肩宽不合适」「袖长刚好」一类一律不得出现）。
5. 全程：试穿人的可闻话语（如有）只允许来自 C01 已登记内容；C01 未登记的语句不得进入成片，剪辑前先核对。

resource_note

- 出镜与声音：内部演示试穿人员（画面主体，来自 VID-C01 已有素材）；苏禾（口播全程；若出镜，B1 或 B4 对镜讲述，在 3 小时拍摄＋30 分钟补录内安排）。
- 现有素材：VID-C01 试穿记录一原始片段（必须使用）、IMG-P01 三件商品图（必须使用）、BROLL-S01 门店空镜（仅转场，不承担判断）。
- 待产出：苏禾口播录音（3 小时拍摄内或补录完成）；（可选）苏禾出镜镜头。
- 接力说明：本条结尾的边界陈述即向周宁交出的问题（哪些需本人试穿）——成片中不得添加预告下一条或跨账号指引（无 CTA）。

constraints[]

- 不得把内部试穿人员描述为现实顾客；「会议＋接送」是演示情境不是真实顾客经历（B1 标注 + 全片不得违背）
- 不得将 C01 试穿记录与 D01 匿名问题拼接成同一顾客故事（本条只用 C01）
- 不得声称适合所有「职场妈妈」或任何具体适穿人群
- 不得补写防水／防风／抗皱／保暖／显瘦等未登记性能
- 不得声称调整后提高了销售或顾客更喜欢
- 不得把调整剪成惊人反转
- 不使用「显瘦」「闭眼入」「人人可穿」等话术
- 不出现预约成功、名额稀缺表述；本条无 CTA——不出现任何行动召唤（预约、到店、私信、评论引导）；统一承接说明不采用（如制作方坚持，先走上游确认，且不得替代判断价值）
- 不给试穿人身体下判断（肩部／袖长／裤长只说「需本人试穿」，不说「她合适／不合适」）
- 试穿人语音如与 C01 未登记内容冲突，不得使用

failure_case

会砸的那条方案：「惊喜改造版」——把 B3 的调整剪成一个前后对比的改造反转，结尾收成「这样就不正式了」。
为什么砸：输入只登记了「正式程度可以调整」，没登记「调整后就解决了」；收尾一旦删掉「肩部、袖长、裤长仍需本人试穿」那一半，等于替 C01 宣布了一个它没宣布的结论（CS-7 ⑥ 删掉记录的另一半）。同时「惊喜反转」结构会用画面把 `SUBJECTIVE` 判断（一次试穿里的观察）坐实成客观事实，恰好撞上 brief 的硬禁「不得把调整剪成惊人反转」。机制：CS-4 主观区被画面强化 ＋ CS-7 ⑥ 删减输入记录的后半段。

assumptions[]

- platform：输入槽位为小红书，但 brief 明确「最终发布平台未确认，由 Founder 锁定」——本稿按平台中立母版处理，时长 ≤60s 对所有候选平台成立；不进入平台规格设计。
- 苏禾出镜方式未定：本稿按「口播为主线、B1/B4 可选真人出镜」设计，两版共用同一逐字稿。
- 无真实顾客原话可用：C01 为内部演示记录，不是顾客故事；试穿人语音默认视为未登记，除非与 C01 核对。
- 单穿比较子场景的素材可用性按「待检索」处理，检索判据已给出。
- duration_band 短档（≤60s），实际使用 4 段。
- 出镜人身体信息不进入内容（不给试穿人身体下判断）。
- 无 `return_from_downstream[]` 回改建议。

missing[]

- 最终发布平台（Founder 锁定中；锁定前下游不做平台规格）
- 苏禾出镜方式（真人出镜或旁白）——brief 列在「进入脚本与拍摄设计前必须确认」事项
- 是否采用统一承接说明（建议不采用；如需，走上游确认）
- VID-C01 中「脱下西装单穿」子场景的可用性（检索判据清单已给；结果决定 B3/B4 结论强度）
````
