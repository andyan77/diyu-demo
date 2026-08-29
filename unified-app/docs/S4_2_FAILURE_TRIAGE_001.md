# S4.2 FAILURE TRIAGE 001

- `task_id`: DIYU-V1-UNIFIED-DIFY-APPLICATION-001
- 阶段：S4.2（Rebase Prompt §8.2 逐项开放其余五项专业能力）
- 判据：`unified-app/stages/S4_2_STAGE_GATE_v1.0.json`，sha256 `28157073d7c6012ae5b8236c0053a5f503101050491ae9d44f59e76a0fd8fac2`（模型调用之前冻结）
- 结果：十例 **全 FAIL**。两种失败签名，对应两个独立失效节点，**都在执行侧本轮新写的产物里，没有一条落在受保护资产上**。

---

## observed_failure

| 签名 | 命中范围 | 判定器读到的实际值 |
|---|---|---|
| A｜路由来源不等于 `canvas_triage` | 10/10 全部 | `{"target": <正确能力>, "source": "m1_named", "route_mode": "CAPABILITY"}` |
| B｜正例交付里没有任何只可能来自夹具的标记 | 5/5 正例 | `{"fixture_marks": [], "price_band_present": false, "outcome": "UNKNOWN"}` |

同时可观察到的**未失败**事实（同一批证据，来自 `workflow_node_executions`，不是模型自述）：

- 十例 `http=200`，画布 33 个节点全 `succeeded`；
- 十例的 Seam 自身记录中，只有该能力对应的一个 `tool_*` 节点执行，其余五个未执行——**没有暗跑**；
- 十例 `route_mode=CAPABILITY`、`target_capability` 全部正确；
- 含「这条」的四例**无一落入 `ASK_ONE`**——S1 歧义规则的反向边界成立，未过度触发；
- 十例 `leak_hit_count=0`。

---

## frozen_target

- `pass_per_capability[0]`：「路由落到该能力：`uapp_route.target_capability` = 该能力，且来源为 `canvas_triage`（系统自己识别，用户没点名）」
- `pass_per_capability[6]`：「正例：交付含实质内容（不是纯缺口）」
- `pair_design.why_this_pair_discriminates`：「两例只差『事实是否在场』这一个变量……若正例也只能给缺口，就说明夹具没能进入能力。」

---

## R1｜签名 B 的根因：夹具在上传通道被双重编码，**从未以可读形式进入系统**

`confirmed_origin = CHECKER_OR_FIXTURE`（执行侧本轮新写的运行器，非被测对象）

### evidence（三条互相独立）

1. **抽取文本可被逐字节还原。** `S4-CAP-CAMPAIGN-POS.json` 的 `m1_extract.outputs.text[0]` 开头为
   `# ä¸\x80é¡µçº¸å¤¹å\x85·...`；对该字符串执行 `.encode("latin-1").decode("utf-8")` 得到
   `# 一页纸夹具品牌事实 v0.1`，与原夹具首行完全一致。**能被 latin-1→utf-8 还原，即证明发生了一次多余的编码。**
2. **Dify 落库事实。** `upload_files` 中 `id=7de85077-bea6-426a-b353-8ba39a94b000` 的记录：
   `name = ä¸é¡µçº¸å¤¹å·åçäºå® v0.1.md`，`size = 11780`。
   原文件 `wc -c` = **6119**。中文部分体积翻倍，是双重编码的确定性特征。
3. **代码路径闭合。** `account-operations/tools/dify_client.py::_direct` 对 `data` 执行 `data.encode("utf-8")`；
   而 `S4_2_RUN_v1.0.py::upload` 传入的是 `raw.decode("latin-1")`——
   原始 UTF-8 字节先被逐字节映射成 U+0080–U+00FF 字符，再被整体 UTF-8 编码一次。

三条证据指向同一处：**`upload()` 用一个 str 型的 `raw_body` 通道搬运二进制**。

### 后果（必须如实记入）

夹具标记词 `序里集 / 林序 / 周宁 / 苏禾 / 陈晚` 在抽取文本中**逐个为 False**。
因此五个正例交付里不可能出现夹具事实——**判据 B 是对的，失败也是真的**。

更重要的是：**本轮正负例并没有真正只差「事实是否在场」这一个变量**，
实际差的是「有没有一堆乱码字节」。§8.2 的正例侧因此**没有产生任何有效证据**，
不是"差一点通过"，是**该问题根本没被测到**。

正例交付与负例交付提出的缺口不同（正例问出镜与产能，负例问时间边界），
这**不是**夹具生效的证据——乱码同样会改变模型行为。此处不作任何有利解读。

### mutation_target

`unified-app/workflows/S4_2_RUN_v1.0.py::upload` —— 唯一允许修改的对象。

### protected_targets（本轮不得修改，且无证据表明其有错）

画布图与全部节点源码、`UAPP_CANVAS_NODES_v1.0.py`、`dify_client.py`（对 JSON 体的行为正确，
缺陷在调用方误用 `raw_body`）、M1 子图、M2 合同、M3/M4/Hop/Seam 及六个能力应用、FP 八应用、旧 Canvas。

---

## R2｜签名 A 的根因：判据冻结了一条**未经验证的关于 M1 行为的假设**

`confirmed_origin = ORACLE_OR_CRITERION`（执行侧本轮冻结的判据，非被测对象）

### evidence

`ROUTE_SRC`（继承自 `UAPP_CANVAS_NODES_v1.0.py`，本任务开工前既已存在的受保护资产）自身定义：

```python
intent_source = "m1_named" if picked else "none"
if picked:
    mode = "CAPABILITY"
...
elif intent in CAP6:
    picked = intent
    mode = "CAPABILITY"
    intent_source = "canvas_triage"
```

其中 `picked` 取自 **M1 的 `needed_capabilities`**。
即：`canvas_triage` **只在 M1 返回空表时才可能出现**。

本轮五句自然语言，M1 自己就解析出了能力（如 `intent_reason`：
「用户要求做春季新品的整体安排、排节奏和重点，属于一段时间的整体安排排期，对应 CAMPAIGN」），
`needed_capabilities` 非空，`ROUTE_SRC` 于是**按其自身定义正确地**标为 `m1_named`。

我在冻结判据时假定"这五句不点名 ⇒ M1 会返回空表 ⇒ 必然走 canvas_triage"。
**这个假设在冻结前从未被验证过**，且被证明为假。

### 这是判据错，不是系统错

§8.2 的产品要求是「五项专业能力各自能被自然语言真实调用并真实执行」。
十例的 `target_capability` 正确、`route_mode=CAPABILITY`、Seam 内对应 `tool_*` 真实执行、其余五个未跑——
**产品要求已被满足**。判据额外断言的是"由哪一段内部机制完成桥接"，属于 HOW，且断错了。

### mutation_target

`unified-app/stages/S4_2_STAGE_GATE_v1.0.json` → 新版本 `v1.1`。

### 按 A2 的处置：本轮不得据此宣告 PASS

「判据在看到结果后才定或改，本次运行只算探索，不产生正式 PASS。」

因此**不允许**把现有十份证据拿去重判成绿。正确路径是：
修 R1 → 冻结 v1.1（在重跑之前）→ **十例全部重跑** → 用 v1.1 独立判定。
R1 本来就要求重跑正例，本次索性十例一并重跑，负例同样在新判据下取证。

### 修改内容（只此两处，其余判据逐块哈希证明一字未改）

1. `pass_per_capability[0]`：来源条件由「必须为 `canvas_triage`」改为
   「`intent_source ∈ {m1_named, canvas_triage}`」。
2. **补一条确定性检查替代原来的机制假设，不是删掉守卫**：
   `discipline.user_never_names_modules` 原本只是一句声明、从未被机器检查过；
   v1.1 将其升为可执行判据——逐例断言输入串中不含任何 capability 名、模块名或内部字段名。
   原判据想防的是"用例被输入里的能力名喂成了送分题"，
   新判据**直接检验输入本身**，比断言内部机制标签更强、且可确定性复算。

### protected_targets

S1/S2/S3/S4.1 全部判据与结论、画布图、上述全部受保护资产。
`identity.graph_sha256 = 6f3d3e53...` 不变——**本层不改图，两处修复都不碰画布**。

---

## next_reverification

1. 修 `upload()`；**先做零模型调用的定向正控制**：只上传、不对话，回读 `upload_files` 的 `size` 与 `name`，
   必须等于 6119 与未乱码的原文件名。不通过则不进入重跑。
2. 冻结 `S4_2_STAGE_GATE_v1.1.json`（在任何重跑之前），并附各判据块哈希对照。
3. 归档本轮十份证据到 `evidence/stages/s4_2_attempt01/`——**不删除、不覆盖、不改绿**。
4. 十例全部重跑，按 v1.1 独立判定。
5. 运行后回归：`S4_CHECKS_v1.0.py` + 11 个受保护应用 `graph_md5` 零漂移复核。

## 本轮成本

十例画布运行 10 次、画布内 LLM 节点约 20 次，加 M3/Hop/Seam 及各能力应用的嵌套运行。
该成本因 R1 而**未换回正例侧的有效证据**，如实计入。
