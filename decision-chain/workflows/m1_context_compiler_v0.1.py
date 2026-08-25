"""
M1 任务上下文编译器 · 确定性状态节点
task_id: DIYU-V1-M1-NATURAL-CONTEXT-001

设计参照: decision-chain/docs/V1_M1_TASK_CONTEXT_COMPILER_DESIGN_v0.1.md

本文件是独立开发/测试用源码，最终以字符串形式嵌入 Dify Code 节点（code_language: python3）。
Dify 按 `variables:` 声明把节点输入作为关键字参数传给 main()，返回值字典的键必须与节点
`outputs:` 声明一致。

工程纪律（继承已验证的 v1_state 模式，代码本体不复用、不修改受保护资产）：
  1. 只有本节点能产出最终 call_intent / task_context_snapshot；LLM 影子节点只出扁平结构化 patch。
  2. patch 整体拒绝：任一未知字段或非法枚举值，拒绝整个 patch，不局部采纳。
  3. 失败诚实：不编造原因，不假装已完成。
  4. open_threads 补终态 HANDLED（v1_state 的 OPEN/SURFACED 二值在此基础上扩展，互不覆盖）。
"""

import json

SCHEMA_VERSION = 1

# ---- CAP-01/02/04/06/07/08：当前有物理路由入口的六项能力 ----
# CAP-03（M3）/ CAP-05（创意锦标赛）当前无物理入口，故不在此枚举中；
# call_intent 对它们如实标记 BLOCKED / NO_PHYSICAL_ENTRY_YET，不伪造入口。
CAPABILITIES = [
    "MATRIX",
    "CAMPAIGN",
    "CONTENT_BRIEF",
    "CREATIVE_SCRIPT",
    "PRODUCTION_DIRECTOR",
    "PUBLISHING_PACKAGING",
]
NO_ENTRY_CAPABILITIES = ["SINGLE_ACCOUNT_OPERATION", "CREATIVE_TOURNAMENT"]  # CAP-03 / CAP-05

# 给对话 LLM 的人话标签：dialogue_directive 面向对话 LLM 组织自然语言，不得把内部枚举代码
# （如 "MATRIX"）原样拼进指令文本——这类代码本质是 Prompt 内部字段值，chat LLM 系统提示词
# 明确禁止"出现 Prompt 内部字段名"，直接拼代码会被它当作用户说过的原话复述出来（真实发现，
# 见 evidence/V1_M1_CANDIDATE_RUN_001.md CE-A2）。
CAPABILITY_LABEL_ZH = {
    "MATRIX": "账号矩阵",
    "CAMPAIGN": "经营任务策划",
    "CONTENT_BRIEF": "内容 Brief",
    "CREATIVE_SCRIPT": "创意脚本",
    "PRODUCTION_DIRECTOR": "成片导演",
    "PUBLISHING_PACKAGING": "发布与打包",
    "SINGLE_ACCOUNT_OPERATION": "单账号持续运营",
    "CREATIVE_TOURNAMENT": "创意锦标赛",
}

# _capability_input_status 里唯一会产出的四个 block_reason 代码，同理不得原样拼进
# dialogue_directive；call_intent_json（机器可读、不面向用户）仍保留原始代码。
BLOCK_REASON_LABEL_ZH = {
    "NO_CURRENT_TASK_STATED": "还没有听你说过具体任务内容",
    "NO_TASK_OR_GOAL_STATED": "还没有听你说过具体任务或目标",
    "NO_PHYSICAL_ENTRY_YET": "这项能力目前还没有可以实际调用的入口",
    "UNKNOWN_CAPABILITY": "无法识别这项能力",
}

VALID_TEMPORAL_SCOPE = ["UNSTATED", "ONE_ITEM", "CYCLE", "LONG_TERM"]
VALID_CONFIRMATION_SIGNAL = ["NONE", "AFFIRM", "DECLINE"]
VALID_ROUTE_INTENT = ["DISCUSS", "FOCUS", "EXECUTE_REQUEST", "CANCEL", "OUT_OF_SCOPE"]
VALID_REQUESTED_CAPABILITY = ["NONE"] + CAPABILITIES

# 影子节点必须原样返回的扁平字段集合（v0.1 最小切片，覆盖 P0 核心行为，
# 不是快照设计文档 14 条语义的完整落地——完整落地留给后续迭代真实 Dify 运行后再扩展，
# 避免一次性给 LLM 塞过多嵌套结构导致结构化输出不稳定，参照侦察对 v1_shadow 的发现）
PATCH_KEYS = {
    "route_intent",
    "current_task_text",
    "temporal_scope",
    "primary_goal_text",
    "non_sacrifice_constraint_text",
    "requested_capability",
    "confirmation_signal",
    "side_question",
    "user_message_summary",
}


def _default_snapshot():
    return {
        "schema_version": SCHEMA_VERSION,
        "task_id": None,
        "revision": 0,
        "current_task": {"text": None, "temporal_scope": "UNSTATED", "source_ref": "USER_DIRECT"},
        "goal_structure": {
            "primary_goal": None,
            "secondary_goals": [],
            "priority_order": [],
            "non_sacrifice_constraints": [],
        },
        "allowed_capabilities": [],  # 由 call_intent 现算，不在快照里静态存
        "open_threads": [],
        "last_confirmation_signal": "NONE",
        "last_route_intent": None,
    }


def _validate_patch(patch):
    """整体校验：任一未知键或非法枚举值，整体拒绝，返回 (ok: bool, reason: str)。"""
    if not isinstance(patch, dict):
        return False, "PATCH_NOT_OBJECT"
    unknown = set(patch.keys()) - PATCH_KEYS
    if unknown:
        return False, "PATCH_UNKNOWN_FIELDS:" + ",".join(sorted(unknown))
    ts = patch.get("temporal_scope", "UNSTATED")
    if ts not in VALID_TEMPORAL_SCOPE:
        return False, "ILLEGAL_ENUM:temporal_scope:" + str(ts)
    cs = patch.get("confirmation_signal", "NONE")
    if cs not in VALID_CONFIRMATION_SIGNAL:
        return False, "ILLEGAL_ENUM:confirmation_signal:" + str(cs)
    ri = patch.get("route_intent")
    if ri is not None and ri not in VALID_ROUTE_INTENT:
        return False, "ILLEGAL_ENUM:route_intent:" + str(ri)
    rc = patch.get("requested_capability", "NONE")
    if rc not in VALID_REQUESTED_CAPABILITY:
        return False, "ILLEGAL_ENUM:requested_capability:" + str(rc)
    return True, ""


def _merge_patch(snap, patch):
    """把校验通过的 patch 合并进快照。只有用户本轮真的说出口的内容才写入
    （不得把 §四 冻结的"不得把用户没说的目标写成已确认"违反）。"""
    changed = False

    text = (patch.get("current_task_text") or "").strip()
    if text:
        snap["current_task"]["text"] = text
        snap["current_task"]["temporal_scope"] = patch.get("temporal_scope", "UNSTATED")
        changed = True

    goal = (patch.get("primary_goal_text") or "").strip()
    if goal:
        snap["goal_structure"]["primary_goal"] = goal
        changed = True

    nsc = (patch.get("non_sacrifice_constraint_text") or "").strip()
    if nsc and nsc not in snap["goal_structure"]["non_sacrifice_constraints"]:
        snap["goal_structure"]["non_sacrifice_constraints"].append(nsc)
        changed = True

    side_q = (patch.get("side_question") or "").strip()
    if side_q:
        tid = "thread_%03d" % (len(snap["open_threads"]) + 1)
        snap["open_threads"].append(
            {"id": tid, "text": side_q, "raised_at_revision": snap["revision"], "status": "OPEN"}
        )
        changed = True

    cs = patch.get("confirmation_signal", "NONE")
    if cs != "NONE":
        snap["last_confirmation_signal"] = cs
        changed = True

    ri = patch.get("route_intent")
    if ri:
        snap["last_route_intent"] = ri

    if changed:
        snap["revision"] = snap["revision"] + 1

    return snap, changed


def _capability_input_status(snap, cap_id):
    """对照该能力的"必需业务输入"判定 DIRECT_ENTRY_ELIGIBLE / DEGRADED_INPUT / BLOCKED。

    v0.1 只实现判据里最核心、可从当前扁平快照直接判断的部分（有无当前任务描述、
    有无主目标）；更细的必需输入项（如 Matrix 的六类企业/组织事实）快照里还没有专门
    字段承载，如实标记为 DEGRADED_INPUT 并在 block_reason 里说明缺什么，不假装已满足。
    """
    has_task = bool(snap["current_task"]["text"])
    has_goal = bool(snap["goal_structure"]["primary_goal"])

    if cap_id == "MATRIX":
        # Matrix 六类必需输入里，快照目前只能判断"是否涉及长期定位/账号结构"这一条件本身
        # 是否成立；其余五类（企业事实/组织事实/账号责任卡数量等）本设计尚未采集专门字段。
        if not has_task:
            return "BLOCKED", "NO_CURRENT_TASK_STATED"
        return "DEGRADED_INPUT", "MATRIX_REQUIRES_SIX_INPUT_CATEGORIES_SNAPSHOT_ONLY_HAS_TASK_TEXT"

    if cap_id in ("CAMPAIGN", "CONTENT_BRIEF", "CREATIVE_SCRIPT", "PRODUCTION_DIRECTOR", "PUBLISHING_PACKAGING"):
        if not has_task and not has_goal:
            return "BLOCKED", "NO_TASK_OR_GOAL_STATED"
        return "DEGRADED_INPUT", cap_id + "_REQUIRES_FULL_CONTRACT_INPUT_SNAPSHOT_ONLY_HAS_TASK_AND_GOAL"

    return "BLOCKED", "UNKNOWN_CAPABILITY"


def compute_call_intent(snap, requested_capability):
    per_capability = {}
    needed = []

    if requested_capability and requested_capability != "NONE":
        needed = [requested_capability]

    for cap_id in CAPABILITIES:
        status, reason = _capability_input_status(snap, cap_id)
        per_capability[cap_id] = {
            "status": status,
            "reachable_if_requested": status != "BLOCKED",
            "block_reason": reason if status == "BLOCKED" else None,
            "known_limitation": "此判定不代表主 Chatflow 的既有线性锁(v1_state.UPSTREAM_OF)会放行；"
            "M1 候选环境不经过该锁，锁的解除暂定为 M4 施工范围。"
            if cap_id in ("CAMPAIGN", "CONTENT_BRIEF")
            else None,
        }

    for cap_id in NO_ENTRY_CAPABILITIES:
        per_capability[cap_id] = {
            "status": "BLOCKED",
            "reachable_if_requested": False,
            "block_reason": "NO_PHYSICAL_ENTRY_YET",
            "known_limitation": None,
        }

    open_now = [t for t in snap["open_threads"] if t.get("status") == "OPEN"]

    return {
        "needed_capabilities": needed,
        "per_capability": per_capability,
        "continuation": {
            "open_threads_to_surface": [t["id"] for t in open_now[:1]],
            "non_blocking_gaps": [],
        },
    }


def _dialogue_directive(snap, patch_ok, reject_reason, call_intent, requested_capability):
    """给对话 LLM 的确定性指令，不让模型自己判断状态或编造原因（继承 A-4 纪律）。"""
    if not patch_ok:
        return (
            "补丁校验未通过（" + reject_reason + "）。保持旧任务状态不变，正常回答用户，"
            "不要声称任何确认、授权或执行已经生效。"
        )

    parts = []
    if snap["current_task"]["text"]:
        parts.append("当前任务：" + snap["current_task"]["text"])
    else:
        parts.append("当前系统这边确实还没有记录任何任务内容（不是用户表达得不够清楚，"
                      "也不是落库失败，就是还没有形成任务）。")

    if requested_capability and requested_capability != "NONE":
        info = call_intent["per_capability"].get(requested_capability)
        if info:
            label = CAPABILITY_LABEL_ZH.get(requested_capability, requested_capability)
            if info["status"] == "BLOCKED":
                reason_label = BLOCK_REASON_LABEL_ZH.get(info["block_reason"], str(info["block_reason"]))
                parts.append(
                    "当前识别到你想调用的能力是" + label + "，判定为阻塞，原因是：" + reason_label
                    + "。如实告知，不编造网络或系统故障之类的原因。"
                )
            else:
                parts.append(
                    "当前识别到你想调用的能力是" + label + "，业务语义上可以直接进入，"
                    "但本候选环境是独立评估，不代表主 Chatflow 会立即放行——如实说明这是"
                    "M1 候选环境下的意图判定，不代表已经执行。"
                )

    open_now = [t for t in snap["open_threads"] if t.get("status") == "OPEN"]
    if open_now:
        parts.append("有一件之前提到、还没细聊的事：" + open_now[0]["text"])
        open_now[0]["status"] = "SURFACED"

    return "\n".join(parts)


def main(user_query: str, snapshot_json: str, shadow_patch: dict) -> dict:
    try:
        snap = json.loads(snapshot_json) if snapshot_json else _default_snapshot()
    except Exception:
        snap = _default_snapshot()
    if not isinstance(snap, dict) or "schema_version" not in snap:
        snap = _default_snapshot()

    # Dify 把 LLM 节点的 structured_output 作为原生 object 传给下游 Code 节点
    # （非 JSON 字符串），故这里直接按 dict 校验，不做 json.loads。
    patch = shadow_patch if isinstance(shadow_patch, dict) else None

    if patch is None:
        patch_ok = False
        reject_reason = "PATCH_NOT_OBJECT"
    else:
        patch_ok, reject_reason = _validate_patch(patch)

    requested_capability = "NONE"
    if patch_ok:
        snap, changed = _merge_patch(snap, patch)
        requested_capability = patch.get("requested_capability", "NONE")
    else:
        changed = False

    call_intent = compute_call_intent(snap, requested_capability)
    directive = _dialogue_directive(snap, patch_ok, reject_reason, call_intent, requested_capability)

    return {
        "snapshot_json": json.dumps(snap, ensure_ascii=False),
        "call_intent_json": json.dumps(call_intent, ensure_ascii=False),
        "dialogue_directive": directive,
        "patch_ok": "true" if patch_ok else "false",
        "reject_reason": reject_reason,
        "state_changed": "true" if changed else "false",
        "turn_report_json": json.dumps(
            {
                "patch_ok": patch_ok,
                "reject_reason": reject_reason,
                "revision": snap["revision"],
                "requested_capability": requested_capability,
                "needed_capabilities": call_intent["needed_capabilities"],
                "open_threads_open_count": len(
                    [t for t in snap["open_threads"] if t.get("status") in ("OPEN", "SURFACED")]
                ),
            },
            ensure_ascii=False,
        ),
    }
