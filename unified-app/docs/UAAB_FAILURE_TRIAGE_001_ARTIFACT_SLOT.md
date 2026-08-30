# FAILURE TRIAGE 001 · 已接受上游产物正文丢失在单槽位覆盖上

`task_id: DIYU-V1-UAPP-ACCEPTED-ARTIFACT-BINDING-001`｜`task_mode: NEW_TASK`
授权：《统一应用已接受上游产物绑定修复与 D3 收口 Execution Prompt》第五节
证据：`unified-app/evidence/stages/uapp_artifact_binding/UAAB_PHASE_A_ROOTCAUSE.json`
（可复算：`python3 unified-app/workflows/UAAB_PHASE_A_ROOTCAUSE_v1.0.py`，零模型、零写入）

## observed_failure

D3（canvas run `217f8e2d`）中，用户说「基于刚才那份制作方案，重新给我一版标题和封面。」
统一应用没能把已接受的 Production Director 正文交给 PUBLISHING_PACKAGING，
PP 收到的 `capability_call` **不含 `content_body_or_beats`**，返回 `INPUT_INSUFFICIENT`。

## frozen_target

统一应用必须取回准确的、同任务、已接受、CURRENT、非 STALE 的 PD artifact 正文，
作为 PP 的 `content_body_or_beats` 传入；不得用「最近一次任意能力产物」代替。

## 现场事实（逐条可复算）

**账本知道 PD 是合法候选：**

| 能力 | turn | accepted | accepted_turn | stale | fp | len |
|---|---|---|---|---|---|---|
| CONTENT_BRIEF | 2 | true | 3 | **true** | `2e41c4b7629a081d` | 6600 |
| CREATIVE_SCRIPT | 4 | true | 5 | **true** | `95ecee48bdb1357a` | 6016 |
| **PRODUCTION_DIRECTOR** | **6** | **true** | **7** | **false** | `099061257c9677bd` | **10121** |
| PUBLISHING_PACKAGING | 7 | **false** | null | true | `757af4204cc42fb3` | 14984 |

**但唯一的正文槽位里装的是 PP 的产物：**

```
conversation.uapp_last_capability = PUBLISHING_PACKAGING
conversation.uapp_last_artifact   = 14984 字
  规范化前 256 字的 FNV-1a 指纹 = 757af4204cc42fb3
  → 精确命中账本第 4 条：PP@turn7，accepted=false，stale=true
```

**D3 当次的数据流：**

```
uapp_hop.upstream_capability ← conversation.uapp_last_capability = PUBLISHING_PACKAGING
uapp_hop.upstream_delivery   ← conversation.uapp_last_artifact   = PP 自己的旧产物（14984 字）
        ↓ Hop 从 PP 旧产物里抽出了「标题候选T1…」当作 content_body_or_beats
uapp_fields 血缘门：
  [{"slot":"content_body_or_beats","fp":"c954384c9822fc20",
    "lineage":"REJECTED","reason":"NO_LEDGER_MATCH"}]
        ↓ 该槽位被剔除
PP 实际收到的 capability_call 不含 content_body_or_beats → INPUT_INSUFFICIENT
```

## candidate_sources 四选一

| 候选 | 判定 | 依据 |
|---|---|---|
| ① 已接受 artifact 正文**从未持久化** | **CONFIRMED** | M2 本任务 `artifacts=0`、`task_snapshots=0`；且 M2 的 `artifacts` 列只有 `task_id,kind,content_hash,parent_artifact_id,id,created_at`，`content_versions` 只有 `content_ref,content_hash` —— **两张表都没有正文列**。会话里唯一的正文槽位装的是 PP 产物。PD 正文没有任何一处留存。 |
| ② 已持久化但没有可取回引用 | REFUTED | 前提不成立：正文根本没被持久化。 |
| ③ 选择器只读 `uapp_last_artifact` | **CONFIRMED_BUT_DOWNSTREAM** | `uapp_hop.upstream_delivery` 直接接 `{{#conversation.uapp_last_artifact#}}`，对 accepted / stale / capability 一无所知。但这是**写入侧只有一个槽位**的必然结果——选择器写得再对，也没有第二份正文可选。按 A3，最高失效节点在写入侧。 |
| ④ 取到了但在 fields/Seam 前被丢弃 | REFUTED | PD 正文从未被取到；被取到的是 PP 自己的旧产物，而血缘门**正确地**拒绝了它。丢弃是对的，不是缺陷。 |

## confirmed_origin

`SYSTEM_UNDER_TEST` · 统一画布的**产物持久化接缝**。

**最高失效节点：`uapp_persist` + `uapp_save` 的单槽位无条件覆盖。**

```python
# uapp_persist 现状（全文 460 字）
def main(new_artifact, new_capability, prev_artifact, prev_capability):
    new_a = (new_artifact or "").strip()
    if new_a:
        return {"artifact_to_persist": new_artifact or "",
                "capability_to_persist": new_capability or "",
                "persist_action": "WRITE_NEW"}          # ← 任何能力的产物都整体覆盖
    return {"artifact_to_persist": prev_artifact or "",
            "capability_to_persist": prev_capability or "",
            "persist_action": "KEEP_PREVIOUS"}
```

它不看 `accepted`、不看 `stale`、不按能力分格。T7 那份**未被接受**的 PP 产物
因此覆盖掉了 T6 **已被接受**的 PD 正文。账本仍然记着 PD 存在、已接受、未过期，
但正文已经没了——系统「知道有，拿不到」。

## 影响面：只有三处引用该槽位

全图 49 个节点里，只有 `uapp_persist`（写入决策）、`uapp_save`（单点赋值）、
`uapp_hop`（取回接线）引用 `uapp_last_artifact` / `uapp_last_capability`，**没有第四处**。

## 没坏、不许动的

- `uapp_fields` 的血缘门：正确拒绝了 PP 自己的旧产物，防住了「PP 拿自己的输出当上游」；
- `uapp_state` 的账本：PD 的 `accepted=true` / `stale=false` 记录准确；
- PP b2：缺输入时精确升级、不编造，行为正确；
- Seam 路由、Hop 抽取 Prompt、M1 / M2 / M3、其余五个专业能力。

## M2 不能充当正文真源（未经授权不扩大）

M2 已有 `POST /workspaces/{ws}/tasks/{task_id}/artifacts`、
`POST,GET /workspaces/{ws}/artifacts/{id}/versions`、`.../versions/current` 等完整 API，
但底层两张表**都不存正文**，只存 `content_ref` 与 `content_hash`。
要让 M2 成为正文真源必须改 schema —— 按 Prompt 第 6.3 节末段，
这属于「必须修改 M2 schema」的情形，**不自行扩大授权**，因此不走这条路。

## mutation_target（Phase B 只改这些）

1. `uapp_persist`：改为按能力分格、带指纹与哈希的**有界产物存储**写入者；
2. `uapp_save`：赋值目标不变，值改为存储 JSON；
3. **新增** `uapp_pick_upstream`：确定性选择器，按冻结的合法性条件挑上游产物并现场复算哈希；
4. `uapp_hop` 的 `upstream_delivery` / `upstream_capability` 接线改指选择器输出。

`uapp_last_artifact` 由「上一跳正文」**改为该存储本身**——不新增会话变量，
因为本会话已存在的 12 个变量与图里声明的 12 个一一对应，
新声明的变量不会为既有会话补建行，取回会 fail-open，风险不可接受。
这样正文仍然**只有一处**，不产生平行副本。

## protected_targets（本轮不得修改）

PP b2 Skill 与 `skill_llm.system`、PP b2 graph `8366328b`、`PPBS_GATE_v2.0` 的 D1/D2/D3 判据、
D1/D2/D3 历史证据、Hop provider 的抽取 Prompt / 模型 / 参数、Seam 路由与六能力分派、
M1 / M2 / M3 / 其余五能力、M2 schema 与 API 合同、M5 历史 DONE 回执、`main`。

## next_reverification

Phase C 确定性正负控制 C-01…C-12（模型调用前），Phase E 一条真实自然语言链的
E-01…E-10。判据在 Phase D 冻结，早于任何新模型结果。
