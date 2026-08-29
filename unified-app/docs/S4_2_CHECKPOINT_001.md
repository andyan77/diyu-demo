# S4.2 CHECKPOINT 001 —— 定向链 FAIL，按授权停机

`S4_2_CURRENT_RUN = CHECKPOINT`｜`SECOND_REPAIR_ITERATION = NOT_TAKEN`｜`ADDITIONAL_MODEL_CALLS = NONE`

## 合同与判据引用

- `task_id`: DIYU-V1-UNIFIED-DIFY-APPLICATION-001
- 判据：`S4_2_STAGE_GATE_v1.2.json`，sha256 `c6d9d859f1a0d520adae2513ec46b18482e0d0c6d14c27e4e9b88b55147339ff`
  （相对 v1.1 只重绑定 identity，行为判据 11 块逐块哈希相等）
- 输入计划：`S4_2_POS_INPUT_PLAN_v1.1.json`，sha256 `d75e92ba…`
- 图身份：`graph_sha256 = f75555c0d6552a0894975242ef3fad7a5351ca63ce4404915c0ee1f71d8f3927`，46 节点 / 48 边

## Gate 结果

| Gate | 结果 | 证据 |
|---|---|---|
| Gate 1 确定性检查（零模型调用） | **PASS 16/16** | `S4_CONVVAR_CLOSURE_v1.0`：读取的会话变量均有可达写入，写入源均为本轮真实节点输出，无新增状态变量 |
| Gate 2 跨轮状态载体（零模型调用） | **PASS** | `workflow_conversation_variables` 直证；第 2 轮跳过全部 `boot_*` 证明读回生效 |
| Gate 3 冻结新 Candidate 身份 | **完成** | v1.2 只重绑定，行为判据未改 |
| Gate 4 定向链（4 能力，各 1 次） | **FAIL** | 1 PASS / 3 FAIL，见下 |

## 授权修复本身：定向验证成立

预先写下的验证条件是「重跑后 `upstream_capability` 在第 3 轮起必须非空，
且下游缺口中不再出现 `script_or_equivalent_beats` / `content_body_or_beats`」。前半条**成立**：

| 轮次 | 能力 | `upstream_capability` | `upstream_delivery` 长度 |
|---|---|---|---|
| T2 | CONTENT_BRIEF | `CONTENT_BRIEF` | 0（T1 为缺口停，本无产物） |
| T3 | CREATIVE_SCRIPT | `CONTENT_BRIEF` | **5593** |
| T4 | PRODUCTION_DIRECTOR | `CREATIVE_SCRIPT` | 0 |
| T5 | PUBLISHING_PACKAGING | `PRODUCTION_DIRECTOR` | 0 |

`uapp_save` 每轮执行且 `succeeded`；存储层 `uapp_last_artifact` 由 0 变为 5593。
**CREATIVE_SCRIPT 的缺口由 7 项塌缩到 1 项**（此前：`objective.primary_goal；expected_change；
content_promise；expression_subject；content_origin_mode；facts_registered；objective.goal_family`，
现仅剩 `content_origin_mode`）。上游产物确实被下游消费了。

## 链路结果与新暴露的停滞点

| 用例 | 判定 | 缺口 |
|---|---|---|
| CONTENT_BRIEF-POS | **PASS 11/11** | 无。交付 940 字，artifact 5593 字 |
| CREATIVE_SCRIPT-POS | FAIL 10/11 | `content_origin_mode` |
| PRODUCTION_DIRECTOR-POS | FAIL 10/11 | `script_or_equivalent_beats` 等（因上游无产物） |
| PUBLISHING_PACKAGING-POS | FAIL 10/11 | `content_body_or_beats` 等（同上） |

三例 FAIL 均只挂「正例交付含实质内容」一条，其余 10/11 全过。

**新的停滞点与本次修复无关**：CREATIVE_SCRIPT 问的是
「这条的素材是现拍、用已有素材剪、访谈、还是生成的？（这项猜错整条会作废，我不替你默认）」。
这是单条内容的经营决策，冻结的输入话术里没有给，夹具里也没有、也不该有。
系统明示拒绝代为默认——这是不编造该有的行为。
该项未产出 artifact，于是 T4、T5 拿到空上游，两者的缺口随之复现，属**级联结果，非独立缺陷**。

## 未判定项（不是 STALE，也不是 PASS）

五个负例证据绑定判据 v1.1，判定器按版本守卫标为 `OUT_OF_SCOPE_GATE_MISMATCH` 并拒绝判定。
守卫未被削弱。CAMPAIGN-POS 同。这些证据原地保留，未删除、未改绿、未 blanket STALE。

## 停机点与下一个可立即执行的动作（需 Founder 裁定，执行侧不自行选择）

1. **补一句素材来源后重跑该链**——只增一句用户话术；但这是执行侧代拟的单条内容经营决策，
   与 CAMPAIGN 那句时间预算同类，需显式授权。
2. **判定 §8.2 的「真实执行」是否等于「产出成品」**——若「正确调用 + 停在精确缺口」即达标，
   则需重定行为判据（属规划侧权威，执行侧不得自改）。
3. **只补齐版本对齐的回归**——把负例与 CAMPAIGN 在 v1.2 下重取证，用于消除
   `OUT_OF_SCOPE_GATE_MISMATCH`；不改判据、不加样本。

以上三项**均未执行**。当前不推进，等待裁定。
