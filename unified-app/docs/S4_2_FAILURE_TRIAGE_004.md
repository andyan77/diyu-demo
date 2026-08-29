# S4.2 FAILURE TRIAGE 004

- 判据：`S4_2_STAGE_GATE_v1.1.json`，sha256 `81d91267…`，**四轮取证一字未动**
- 输入计划：`S4_2_POS_INPUT_PLAN_v1.1.json`，sha256 `d75e92ba…`
- 结果：**7/10 PASS**。五个负例全 PASS；CAMPAIGN 正例 PASS（11/11，交付 2643 字）、
  CONTENT_BRIEF 正例 PASS。仍 FAIL 的三项：`CREATIVE_SCRIPT`、`PRODUCTION_DIRECTOR`、
  `PUBLISHING_PACKAGING`——**恰好是链路中需要上游产物的三项**。
- `confirmed_origin = SYSTEM_UNDER_TEST`（本次是**执行侧自建画布**，不是判据、不是输入）

## 前一轮修复已生效（先记正面事实）

每轮附夹具后，被测轮次的 `uapp_hop.registered_facts` 均为 2452 字、五个夹具标记全部命中；
CONTENT_BRIEF 第 2 轮 `gaps=无`、交付 740 字、`artifact` 2034 字的完整 Content Brief Pack——
**三轮以来正例第一次真正走通**。

### 一并更正我自己的一次诊断错误

TRIAGE 003 之后我曾读出「夹具没进 hop」。那是诊断脚本的 bug：
`uapp_hop.inputs` 是 JSON 字符串，我未先 `json.loads` 就 `json.dumps` 比对，
中文被转义成 `\uXXXX`，任何中文标记都不可能命中——与此前修过的 S3 校验器同一类错误。
正确解码后夹具是**在场**的。此处更正，不影响本轮结论。

## confirmed_origin：接线只建了读端，没建写端

```
S4_BUILD_v1.0.py:71-72        读  upstream_delivery   ← conversation.uapp_last_artifact
                                  upstream_capability ← conversation.uapp_last_capability
UAPP_BUILD_CANVAS_v1.0.py:655-658  写  assigner「uapp_save」：
                                      uapp_seam_merge.artifact.output → uapp_last_artifact
                                      uapp_route.target_capability    → uapp_last_capability
```

- 继承的参考建图把 `uapp_save` 放在 `uapp_delivery` 与 `uapp_answer` 之间；
- 我的 S4 建图是 `uapp_seam_merge → uapp_delivery → uapp_answer_main`，**漏建 `uapp_save`**；
- 实测画布内 assigner 只有一个（`m1_save_snapshot`），
  四个被测轮次的 `upstream_capability` 恒为 `''`。

**能力产出了 artifact，转手被丢弃。** 因此 `CREATIVE_SCRIPT` 第 3 轮从零开始退回 7 个缺口，
`PRODUCTION_DIRECTOR` 缺 `script_or_equivalent_beats`、`PUBLISHING_PACKAGING` 缺
`content_body_or_beats` —— 结构上永远拿不到上游产物。

三个 FAIL 是**同一个根因的三个表现**，不是三个问题。链头两项（CAMPAIGN、CONTENT_BRIEF）
不依赖上游，因此已经 PASS —— 这本身就是该根因的定向验证。

## mutation_target

`unified-app/workflows/S4_BUILD_v1.0.py`：新增 `uapp_save` 节点，
接线改为 `uapp_delivery → uapp_save → uapp_answer_main`，赋值项与继承参考建图逐字一致。

## protected_targets

判据 v1.1 全部条目（**继续一字不动**）、`UAPP_BUILD_CANVAS_v1.0.py`、
`UAPP_CANVAS_NODES_v1.0.py`、M1 子图、M2 合同、M3/M4/Hop/Seam 及六能力应用、FP 八应用、旧 Canvas。

## A3 影响面（必须如实计入，不打折）

本修复**改图** ⇒ `graph_sha256` 变化 ⇒ 绑定该哈希的证据全部转 `STALE`：

- S4.1 的 `S4-CAP-MATRIX-01_a2` 与 `S4-REG-ASK-01_a2`（原为 PASS）；
- S4.2 本轮 10 份证据，**包括已经 PASS 的 7 份**——图变了，通过与否一并失效，不例外。

处置：S4.1 与 S4.2 各出新一版 Stage Gate，**只重绑定 identity，判据块逐块哈希证明一字未改**；
旧证据归档不删除、不改绿；然后重跑 S4.1 回归与 S4.2 正负两侧。

## next_reverification

1. 补 `uapp_save` → 重建 → 导入 → 发布，记录新 `graph_sha256` 与节点/边数。
2. `S4_CHECKS` 确定性检查 + 11 个受保护应用 `graph_md5` 零漂移复核。
3. S4.1 回归重跑；S4.2 正负两侧按冻结输入计划重跑。
4. 定向验证根因：重跑后 `upstream_capability` 在第 3 轮起必须非空，
   且三项下游能力的缺口中不再出现 `script_or_equivalent_beats` / `content_body_or_beats`。
   若仍为空，则本归因不成立，重新诊断，不得在下游打补丁。

## 累计成本

四轮共 41 次画布运行。逐轮定位到的失效节点依次为：
夹具编码（执行侧运行器）→ 判据机制假设（执行侧判据）→ 处理未施加于被测轮次（执行侧输入设计）
→ 画布漏建写端（执行侧画布）。**没有一次误改受保护资产。**
