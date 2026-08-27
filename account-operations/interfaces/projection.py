"""M2 → M3 投影编译 与 M3 → M2 候选校验。

只用标准库。这份文件有两个消费者，且必须保持是同一份代码：

1. 仓库内的 unittest（`account-operations/tests/`）——可离线跑，不需要数据库；
2. Dify 的 `code` 节点——`business-persistence/dify/m2_candidate.yaml` 里已有的形态是
   `code_language: python3` + `def main(...) -> dict` + 标准库 import。本文件的函数可以
   直接贴进那种节点（见文件末尾 `main` 示例）。

为什么投影层必须存在（而不是把 M2 的原始响应直接喂给模型）：

- 共享合同四 §一冻结了「Dify 每次只收到当前任务需要的最小投影」「Dify 不得自行读取整个
  租户数据库」「Skill 不依赖数据库物理结构」——直接喂原始响应会同时违反这三条；
- M2 用 `null` 表达一切"没有值"。而产品语义要求区分六种情形：已具备／未知／未提供／
  不适用／拒绝提供／已失效。把它们坍缩成同一个 `null` 是 M3-AC-12 明确的 FAIL 条件。
  本文件的 `_resolve()` 是防止这次坍缩的唯一地方。

绑定：`business-persistence` @ `main:df2c595` 的 API 形状。该形状变化时，本文件与
`M2_TO_M3_PROJECTION_v1.0.schema.json` 一并置 STALE，须定向复验 M3-AC-12/AC-13。
"""

SCHEMA_VERSION = "1.0"
SCHEMA_VERSION_V11 = "1.1"

# M2 自己的允许清单，逐字照抄自 business-persistence/app/api/knowledge.py @ main:a7b8101：
#   CURRENTLY_USABLE_PERMISSION_STATUSES = ("allowed", "restricted")
# 抄它而不是自己定义，是为了不出现两套口径——两套口径迟早不一致，
# 而不一致的那一刻没人会发现，因为两边都"看起来对"。
M2_CURRENTLY_USABLE_PERMISSION_STATUSES = ("allowed", "restricted")
M2_INTERFACE_BASELINE = "business-persistence@main:df2c595"
M2_INTERFACE_BASELINE_V11 = "business-persistence@main:a7b8101"

# 六个取值两两不等。对应共享合同一 §三「可用性状态」维度。
PRESENT = "PRESENT"
UNKNOWN = "UNKNOWN"
NOT_PROVIDED = "NOT_PROVIDED"
NOT_APPLICABLE = "NOT_APPLICABLE"
REFUSED = "REFUSED"
EXPIRED = "EXPIRED"

AVAILABILITY_VALUES = (PRESENT, UNKNOWN, NOT_PROVIDED, NOT_APPLICABLE, REFUSED, EXPIRED)

# M3 永远不得表达的东西。候选被"接受"、成为"当前有效版本"、覆盖原始反馈或改写来源，
# 全部属于 M2 与用户的权限（共享合同四 §二）。这里做的是整树键名反搜——语法层挡住，
# 不依赖模型自觉。
FORBIDDEN_WRITEBACK_KEYS = frozenset(
    {
        "is_current",
        "set_current",
        "current_version",
        "promote",
        "promoted",
        "accept",
        "accepted",
        "is_accepted",
        "approve",
        "approved",
        "overwrite",
        "override_feedback",
        "feedback_override",
        "source_override",
        "provenance_override",
        "delete",
        "purge",
    }
)


# 「调用方没提这个维度」与「调用方说了这个维度是 None」是两件事。
# 用 None 同时表达两者，会让"我们不知道这个数字的来源"和"我们根本没考虑来源"
# 不可区分——而 M3-AC-12 要求"保留来源"是可检查的。
_OMIT = object()


def field(
    value=None,
    availability=UNKNOWN,
    info_nature=_OMIT,
    provenance=_OMIT,
    confirmation=_OMIT,
    scope=_OMIT,
    as_of=_OMIT,
    valid_until=_OMIT,
    source_ref=_OMIT,
):
    """构造一个状态信封。

    不可用时 `value` 强制为 None：允许 `availability=REFUSED` 同时带一个值，等于给
    "拒绝提供"留了一个偷偷携带数据的后门。

    维度键的取舍：**显式传入的 `None` 会被保留成 `null`，只有完全没传才省略。**
    早先的实现把两者都省略掉，后果是 `source_ref` 这类键在"来源确实不知道"时
    直接消失，于是"没有来源"这件事在投影里不可见，字段消融门也抓不住它
    （删掉一个本来就常常不存在的键，当然不会有任何检查失败）。
    """

    if availability not in AVAILABILITY_VALUES:
        raise ValueError("unknown availability: %r" % (availability,))
    out = {"value": value if availability == PRESENT else None, "availability": availability}
    for key, val in (
        ("info_nature", info_nature),
        ("provenance", provenance),
        ("confirmation", confirmation),
        ("scope", scope),
        ("as_of", as_of),
        ("valid_until", valid_until),
        ("source_ref", source_ref),
    ):
        if val is _OMIT:
            continue
        # 一个「我们不知道」的产能没有来源可言，一条不存在的记录也没有 as_of。
        # 在不可用状态下仍然挂着这两个键，它们就成了永远为 null 的装饰位——
        # 删掉不会有任何检查失败，也就没挣到自己的存在（A5）。
        if availability != PRESENT and key in ("as_of", "source_ref"):
            continue
        out[key] = val
    return out


def _resolve(value, path, declared_absences, **kwargs):
    """把「M2 给了什么」和「调用方声明了什么」合成一个状态信封。

    顺序是刻意的：

    - 调用方显式声明了缺失原因（拒绝提供／不适用／未提供）→ 用它。M2 当前的表结构
      承载不了"用户拒绝告诉我们产能"这类信息，这个区分只能从任务快照侧带进来；
    - 否则 M2 给了 None → `UNKNOWN`。**绝不**默默升级为 `NOT_PROVIDED` 或 `REFUSED`：
      "不知道"和"被拒绝"是两回事，猜一个等于伪造证据身份；
    - 否则 → `PRESENT`。
    """

    declared = (declared_absences or {}).get(path)
    if declared is not None:
        if isinstance(declared, dict):
            note = dict(declared)
            availability = note.pop("availability", UNKNOWN)
            merged = dict(kwargs)
            merged.update(note)
            return field(None, availability, **merged)
        return field(None, declared, **kwargs)
    if value is None:
        return field(None, UNKNOWN, **kwargs)
    return field(value, PRESENT, **kwargs)


def _parse_iso(text):
    """容忍 `Z` 结尾的 ISO-8601 解析。3.10 的 fromisoformat 不认 `Z`。"""

    from datetime import datetime

    if not text:
        return None
    cleaned = text.strip()
    if cleaned.endswith("Z"):
        cleaned = cleaned[:-1] + "+00:00"
    try:
        return datetime.fromisoformat(cleaned)
    except ValueError:
        return None


def _observation_is_expired(obs, now_iso):
    """优先用 M2 自己算的 `is_expired`（列表端点已经算好）。

    只有 M2 没给这个键时才自己判——避免出现两套过期口径。两套口径迟早会不一致，
    而不一致的那一刻没人会发现，因为两边都"看起来对"。
    """

    if "is_expired" in obs:
        return bool(obs["is_expired"])
    valid_until = _parse_iso(obs.get("valid_until"))
    now = _parse_iso(now_iso)
    if valid_until is None or now is None:
        return False
    return valid_until < now


def _project_market_observations(rows, applicable_tracks, now_iso):
    """最小必要：只带与本轮赛道相关的观察。

    过期的**保留**并标 `EXPIRED`，不丢弃——丢弃会让"我们手上这条证据已经过期"
    这件事本身不可见，而 M3-AC-09 恰恰要求它可见。

    时效与**使用权限**是两个正交维度，分别承载，不合并：一条没过期的观察完全
    可能因为来源授权未确认而不可用；一条已获授权的观察也完全可能已经过期。把
    两者塞进同一个 `availability` 会让"为什么不能用"不可区分——而 M3-AC-12 要求
    同时保留来源、**权限**与时效。

    `usable_for_inference` 是唯一给下游看的结论位：它只会比 M2 更保守，永远不会
    把 M2 说"当前不可用"的观察抬成可用。M2 未表达权限概念时（如绑定基线
    `main@df2c595`，其 market_observations 尚无权限字段），`currently_usable`
    为 `None`，此位退化为纯时效判断，行为与加入本维度之前**逐字节一致**。
    """

    tracks = set(applicable_tracks or [])
    out = []
    for obs in rows or []:
        track = obs.get("applicable_track")
        if tracks and track is not None and track not in tracks:
            continue
        expired = _observation_is_expired(obs, now_iso)
        availability = EXPIRED if expired else PRESENT

        # 三个键在绑定基线里都不存在。用 sentinel 区分"这个 M2 构建没有权限概念"
        # 与"权限状态是 unknown"——把前者读成后者等于替 M2 发明一个它没说过的判断。
        has_permission_model = "permission_status" in obs or "currently_usable" in obs
        currently_usable = obs.get("currently_usable") if has_permission_model else None
        permission = {
            "status": obs.get("permission_status") if has_permission_model else None,
            "currently_usable": currently_usable,
            "excluded_reason": obs.get("excluded_reason") if has_permission_model else None,
            "usage_limits": obs.get("usage_limits") if has_permission_model else None,
        }

        out.append(
            {
                "observation_id": str(obs.get("id", "")),
                "layer": obs.get("layer", "raw"),
                "availability": availability,
                "usage_permission": permission,
                # 只在两个维度同时放行时才为真。永远 ≤ M2 自己的判断。
                "usable_for_inference": availability == PRESENT and currently_usable is not False,
                "source": obs.get("source"),
                "platform": obs.get("platform"),
                "collected_at": obs.get("collected_at"),
                "applicable_track": track,
                "scope_ref": obs.get("scope_ref") or {},
                "mechanism_summary": obs.get("mechanism_summary"),
                "valid_until": obs.get("valid_until"),
            }
        )
    return out




def _derive_currently_usable(obs):
    """第一道闸：这条观察能不能当**当前证据**用。

    三条来源，优先级固定，而且**必须记下来是哪一条**——不记，
    「M2 说可用」与「我们按清单推的」就不可区分：

      m2_explicit                    M2 给了显式布尔（/market-observations 列表端点会给）
      derived_from_status_allowlist  M2 只给了 permission_status ⇒ 按 M2 自己的允许清单推
      no_permission_model            这个 M2 构建根本没有权限概念（如 main@df2c595）

    派生是 **fail-closed 的允许清单，不是拒绝清单**：不在 {allowed, restricted} 里的
    一律 false，将来 M2 新增一个没见过的状态值也一律 false。
    v1.0 在这里是 fail-open 的（`currently_usable is not False`）——
    对新 M2 而言，一条 permission_status='unknown' 的观察会被判成可用。这是 v1.1 修掉的实质缺陷之一。
    """
    if "currently_usable" in obs and obs["currently_usable"] is not None:
        return bool(obs["currently_usable"]), "m2_explicit"
    if "permission_status" in obs:
        st = obs.get("permission_status")
        return (st in M2_CURRENTLY_USABLE_PERMISSION_STATUSES,
                "derived_from_status_allowlist")
    return None, "no_permission_model"


def _project_market_observations_v11(rows, applicable_tracks, now_iso, from_list_endpoint=False):
    """v1.1：五组语义分别承载，一组都不许坍缩。

    `from_list_endpoint` 决定期间窗的可用状态：M2 的 /current 最小投影**不返回**
    applicable_period_*（服务端按 queried_at 过滤后就不再外露），因此从该端点投影时
    期间窗记 UNKNOWN——**不猜、也不填 null**，两者必须可区分。
    """
    tracks = set(applicable_tracks or [])
    out = []
    for obs in rows or []:
        track = obs.get("applicable_track")
        if tracks and track is not None and track not in tracks:
            continue
        expired = _observation_is_expired(obs, now_iso)
        availability = EXPIRED if expired else PRESENT
        usable, basis = _derive_currently_usable(obs)

        has_period = from_list_endpoint or ("applicable_period_start" in obs
                                            or "applicable_period_end" in obs)
        out.append({
            "observation_id": str(obs.get("id", "")),
            "layer": obs.get("layer", "raw"),
            "availability": availability,
            "source": obs.get("source"),
            "source_type": obs.get("source_type"),
            "source_reference": obs.get("source_reference"),
            "source_provider": obs.get("source_provider"),
            "platform": obs.get("platform"),
            "collected_at": obs.get("collected_at"),
            "mechanism_summary": obs.get("mechanism_summary"),
            "valid_until": obs.get("valid_until"),
            "evidence_digest": obs.get("evidence_digest"),
            "applicable_scope": {
                "account_id": obs.get("account_id"),
                "applicable_task_id": obs.get("applicable_task_id"),
                "applicable_track": track,
                "applicable_period_start": obs.get("applicable_period_start") if has_period else None,
                "applicable_period_end": obs.get("applicable_period_end") if has_period else None,
                "period_window_availability": PRESENT if has_period else UNKNOWN,
                "scope_ref": obs.get("scope_ref") or {},
            },
            "usage_permission": {
                "status": obs.get("permission_status"),
                "currently_usable": usable,
                "currently_usable_basis": basis,
                "excluded_reason": obs.get("excluded_reason"),
                "usage_limits": obs.get("usage_limits"),
            },
            # 第一道闸放行 + 没过期，才可用于推理。永远 ≤ M2 自己的判断。
            "usable_for_inference": bool(availability == PRESENT and usable is not False),
            # 第二道闸：M2 没有定义 usage_limits 的结构，M3 **不替它发明**一个可发布判断。
            # 由第一道闸推出第二道，就是执行侧创造产品语义（A1 禁止）。
            "external_publish_permission": {
                "availability": UNKNOWN,
                "value": None,
                "basis": ("M2 @ main:a7b8101 只把 usage_limits 存成自由 JSONB，"
                          "未定义其结构、也未给出可发布布尔；M3 不替 M2 发明该判断。"
                          "原值已在 usage_permission.usage_limits 里逐字承载。"),
            },
        })
    return out


def project_market_observation_query(current_response):
    """把 M2 /current 的诚实缺口账原样带过来。

    丢掉它，「一条都没登记」「全被排除」「不在范围内」三种情形就塌成同一个空数组——
    而 M2 明写它 never fabricates a comparison，缺口是它**故意**说出来的话。
    """
    r = current_response or {}
    f = r.get("filters") or {}
    return {
        "queried_at": r.get("queried_at"),
        "filters": {
            "account_id": f.get("account_id"),
            "applicable_track": f.get("applicable_track"),
            "task_id": f.get("task_id"),
        },
        "available": bool(r.get("available")),
        "excluded": [{"observation_id": str(e.get("id", "")), "reason": e.get("reason", "")}
                     for e in (r.get("excluded") or [])],
        "gap_reason": r.get("gap_reason"),
    }


def _project_feedback(rows, now_iso):
    """保留证据身份四元组 + 观察窗是否结束。

    `window_closed` 是 None 表示"判断不了"，不是"没结束"也不是"结束了"——观察窗
    未结束时不得据此改判（M3-AC-10）。
    """

    out = []
    for row in rows or []:
        window_end = row.get("window_end")
        parsed_end = _parse_iso(window_end)
        now = _parse_iso(now_iso)
        if parsed_end is None or now is None:
            window_closed = None
        else:
            window_closed = parsed_end < now

        if row.get("publish_instance_id"):
            bound = {"binding_kind": "publish_instance", "binding_id": str(row["publish_instance_id"])}
        elif row.get("content_version_id"):
            bound = {"binding_kind": "content_version", "binding_id": str(row["content_version_id"])}
        else:
            # M2 的 register_feedback 强制二选一，走到这里说明输入不是 M2 的真实响应。
            raise ValueError("feedback row bound to neither publish_instance nor content_version")

        out.append(
            {
                "feedback_id": str(row.get("id", "")),
                "kind": row.get("kind", "observation"),
                "is_test": bool(row.get("is_test", False)),
                "is_simulated": bool(row.get("is_simulated", False)),
                "is_manual_entry": bool(row.get("is_manual_entry", False)),
                "is_pre_publish_review": bool(row.get("is_pre_publish_review", False)),
                "bound_to": bound,
                "source": row.get("source"),
                "observed_at": row.get("observed_at"),
                "window_start": row.get("window_start"),
                "window_end": window_end,
                "window_closed": window_closed,
                "goal_at_the_time": row.get("goal_at_the_time"),
                "payload": row.get("payload") or {},
            }
        )
    return out


def _project_cycle_summary(cycle):
    """把 M2 的周期行压成当轮最小必要字段。

    为什么不能直接把整行塞进 `value`（本轮由真实响应抓出的实现缺陷）：

    - M2 的真实行带着 `row_version` 与 `idempotency_key`——并发控制与去重细节，
      不是运营判断的输入。把它们投给模型就是"过量读取"（M3-AC-12 的失败条件）；
    - 整行还**重复携带**三类产能，而产能已经在 `capacity` 里逐个带上了自己的
      来源与可用状态。同一事实在同一份投影里出现两次，就是两个真源：一旦
      `declared_absences` 把 `capacity.actual_capacity` 标成"用户拒绝提供"，原始行
      里那个赤裸的数字仍然在，模型照样能读到——整个防坍缩机制当场失效。

    所以周期摘要**刻意不含**任何产能字段。
    """

    # 没有 id 就不是一行周期。403 的响应体（`{"detail": ...}`）也会走到这里，
    # 必须落成 None → UNKNOWN，而不是一条 cycle_id 为空串的"周期"。
    if not cycle or not cycle.get("id"):
        return None
    return {
        "cycle_id": str(cycle.get("id", "")),
        "label": cycle.get("label"),
        "start_at": cycle.get("start_at"),
        "end_at": cycle.get("end_at"),
        "is_current": bool(cycle.get("is_current", False)),
        "supersedes_cycle_id": (
            str(cycle["supersedes_cycle_id"]) if cycle.get("supersedes_cycle_id") else None
        ),
    }


def _project_decision_summary(decision):
    """同上：只带判断本身与它的依据，不带 M2 的内部键。"""

    return {
        "decision_id": str(decision.get("id", "")),
        "cycle_id": str(decision["cycle_id"]) if decision.get("cycle_id") else None,
        "decision": decision.get("decision"),
        "rationale": decision.get("rationale"),
        "source": decision.get("source"),
        "based_on": decision.get("based_on") or {},
        "resulting_cycle_id": (
            str(decision["resulting_cycle_id"]) if decision.get("resulting_cycle_id") else None
        ),
    }


def _project_overlays(rows):
    return [
        {
            "overlay_id": str(row.get("id", "")),
            "name": row.get("name", ""),
            "status": row.get("status", "active"),
            # 只有点名位置被覆盖；未列出的位置仍由 M3 管理。
            "targeted_positions": list(row.get("targeted_positions") or []),
            "scope_start": row.get("scope_start"),
            "scope_end": row.get("scope_end"),
            "rationale": row.get("rationale"),
        }
        for row in rows or []
    ]


def build_projection(
    workspace_id,
    account_id,
    m2,
    requested=None,
    projection_id=None,
    compiled_at=None,
    m2_interface_baseline=None,
    schema_version=SCHEMA_VERSION,
    market_observation_source="list",
):
    """把 M2 的原始响应编译成当轮最小投影。

    `m2` 里的键对应 M2 的读端点：

        current_cycle          GET /workspaces/{ws}/accounts/{acc}/cycles/current
        active_overrides       GET .../campaign-overrides/active
        latest_cycle_decision  GET .../cycles/decisions/latest
        market_observations    GET /workspaces/{ws}/market-observations
        feedback               GET /workspaces/{ws}/publish-instances/{id}/feedback

    `requested` 承载 M2 表结构装不下的任务侧语义：目标、锚点、阶段线索、表达权限、
    以及 `declared_absences`（哪个字段是"被拒绝"而不是"不知道"）。
    """

    requested = requested or {}
    declared = requested.get("declared_absences") or {}
    if m2_interface_baseline is None:
        m2_interface_baseline = (M2_INTERFACE_BASELINE_V11
                                 if schema_version == SCHEMA_VERSION_V11
                                 else M2_INTERFACE_BASELINE)
    now_iso = compiled_at or requested.get("now_iso") or ""

    cycle = m2.get("current_cycle") or {}
    decision = m2.get("latest_cycle_decision") or {}

    # M2 在没有任何决策记录时返回 {"decision": "none_recorded"}。
    # 它必须是 UNKNOWN，不能和 kept_unchanged（评估过、并决定保持）同形——
    # "从没看过"和"看过并决定不动"是两个完全不同的运营事实。
    if decision.get("decision") in (None, "none_recorded"):
        latest_decision_field = field(None, UNKNOWN, info_nature="fact", provenance="system_derived")
    else:
        latest_decision_field = field(
            _project_decision_summary(decision),
            PRESENT,
            info_nature="fact",
            provenance="system_derived",
            as_of=decision.get("created_at"),
        )

    projection = {
        "schema_version": schema_version,
        "projection_id": projection_id or "proj-%s-%s" % (str(account_id)[:8], now_iso or "unbound"),
        "compiled_at": now_iso,
        "binding": {
            "workspace_id": str(workspace_id),
            "account_id": str(account_id),
            "m2_interface_baseline": m2_interface_baseline,
            "task_id": requested.get("task_id"),
        },
        "account_anchor": _resolve(
            requested.get("account_anchor"),
            "account_anchor",
            declared,
            info_nature=requested.get("account_anchor_nature", "system_judgment"),
            provenance=requested.get("account_anchor_provenance", "system_derived"),
            # 暂定锚点必须显式暂定。系统推断不因为被写入持久化就升级为用户确认事实。
            confirmation=requested.get("account_anchor_confirmation", "system_provisional"),
            scope="this_account",
        ),
        "objectives": {
            "primary": _resolve(
                requested.get("primary_objective"),
                "objectives.primary",
                declared,
                info_nature="preference",
                provenance="user_direct",
                scope="this_cycle",
            ),
            "secondary": [
                field(obj, PRESENT, info_nature="preference", provenance="user_direct", scope="this_cycle")
                for obj in (requested.get("secondary_objectives") or [])
            ],
            "priority_note": _resolve(
                requested.get("priority_note"),
                "objectives.priority_note",
                declared,
                info_nature="preference",
                provenance="user_direct",
            ),
            "non_sacrifice_conditions": [
                field(cond, PRESENT, info_nature="preference", provenance="user_direct")
                for cond in (requested.get("non_sacrifice_conditions") or [])
            ],
        },
        "stage_evidence": _resolve(
            requested.get("stage_evidence"),
            "stage_evidence",
            declared,
            info_nature="fact",
            provenance=requested.get("stage_evidence_provenance", "system_derived"),
        ),
        # 三值分别承载。M2 把每个数字和它自己的 *_source 一起存，这里原样带过来——
        # 合并成一个数字会让后面的产能取舍全是假的。
        "capacity": {
            "expected_publish_count": _resolve(
                cycle.get("expected_publish_count"),
                "capacity.expected_publish_count",
                declared,
                info_nature="preference",
                provenance="user_direct",
                source_ref=cycle.get("expected_publish_count_source"),
            ),
            "baseline_capacity": _resolve(
                cycle.get("baseline_capacity"),
                "capacity.baseline_capacity",
                declared,
                info_nature="fact",
                source_ref=cycle.get("baseline_capacity_source"),
            ),
            "actual_capacity": _resolve(
                cycle.get("actual_capacity"),
                "capacity.actual_capacity",
                declared,
                info_nature="fact",
                source_ref=cycle.get("actual_capacity_source"),
            ),
        },
        "current_cycle": _resolve(
            _project_cycle_summary(m2.get("current_cycle")),
            "current_cycle",
            declared,
            info_nature="fact",
            provenance="system_derived",
            as_of=cycle.get("created_at"),
        ),
        "campaign_overlays": _project_overlays(m2.get("active_overrides")),
        "latest_cycle_decision": latest_decision_field,
        "feedback": _project_feedback(m2.get("feedback"), now_iso),
        "market_observations": (
            _project_market_observations_v11(
                m2.get("market_observations"), requested.get("applicable_tracks"), now_iso,
                from_list_endpoint=(market_observation_source == "list"))
            if schema_version == SCHEMA_VERSION_V11 else
            _project_market_observations(
                m2.get("market_observations"), requested.get("applicable_tracks"), now_iso)
        ),
        "permissions": {
            "expression_permission": _resolve(
                requested.get("expression_permission"),
                "permissions.expression_permission",
                declared,
                info_nature="preference",
                provenance="user_direct",
            ),
            # 高风险 CTA 只能来自这里。空数组 = 没有授权，不是"可以自己判断"。
            "cta_authorizations": [
                field(auth, PRESENT, info_nature="preference", provenance="user_direct")
                for auth in (requested.get("cta_authorizations") or [])
            ],
        },
        "gaps": list(requested.get("gaps") or []),
    }

    if schema_version == SCHEMA_VERSION_V11:
        # M2 /current 的诚实缺口账。没有它，「一条都没登记」「全被排除」「不在范围内」
        # 三种情形塌成同一个空数组——那正是 AC-12 明确的 FAIL 形态。
        projection["market_observation_query"] = project_market_observation_query(
            m2.get("market_observations_current"))

    if requested.get("behaviors"):
        projection["requested_behaviors"] = list(requested["behaviors"])
    if requested.get("side_requests"):
        projection["carried_side_requests"] = list(requested["side_requests"])
    return projection


# 每个具名信封**必须**承载哪些维度。JSON Schema 表达不了"按站点不同"的必填，
# 而"一律必填"是错的：`source_ref` 对 objectives.primary 没有意义。
#
# 这张表是 M3-AC-12 ③（字段消融门）的直接产物：没有它时，五个正交维度全部是可选键，
# 删掉任何一个都不会有任何检查失败——也就是说它们在结构上没有挣到自己的存在。
MANDATORY_DIMENSIONS = {
    "account_anchor": ("info_nature", "provenance", "confirmation", "scope"),
    "objectives.primary": ("info_nature", "provenance", "scope"),
    "objectives.priority_note": ("info_nature", "provenance"),
    "stage_evidence": ("info_nature", "provenance"),
    "capacity.expected_publish_count": ("info_nature", "provenance", "source_ref"),
    "capacity.baseline_capacity": ("info_nature", "source_ref"),
    "capacity.actual_capacity": ("info_nature", "source_ref"),
    "current_cycle": ("info_nature", "provenance", "as_of"),
    "latest_cycle_decision": ("info_nature", "provenance", "as_of"),
    "permissions.expression_permission": ("info_nature", "provenance"),
}

# 数组站点。同一条要求，只是承载在列表元素上——漏掉它们，等于让"次要目标"和
# "不可牺牲条件"这两组信封的维度全部退回可选。
MANDATORY_LIST_DIMENSIONS = {
    "objectives.secondary": ("info_nature", "provenance", "scope"),
    "objectives.non_sacrifice_conditions": ("info_nature", "provenance"),
    "permissions.cta_authorizations": ("info_nature", "provenance"),
}

# 这些维度只在"确实有值"时才必须在场：一个 UNKNOWN 的周期没有 `as_of` 可言。
_PRESENT_ONLY_DIMENSIONS = ("as_of", "source_ref", "valid_until")


def _dig(projection, dotted):
    node = projection
    for part in dotted.split("."):
        if not isinstance(node, dict) or part not in node:
            return None
        node = node[part]
    return node


def validate_projection(projection):
    """跨字段不变量。返回违规说明列表；空列表 = 通过。

    这些是 JSON Schema（在 draft-7 兼容子集内）表达不了、但一旦破掉就直接对应
    M3-AC-12 FAIL 的约束。
    """

    problems = []

    def check_field(obj, path):
        if not isinstance(obj, dict):
            problems.append("%s: 不是状态信封" % path)
            return
        availability = obj.get("availability")
        if availability not in AVAILABILITY_VALUES:
            problems.append("%s: availability 非法 (%r)" % (path, availability))
            return
        if availability != PRESENT and obj.get("value") is not None:
            problems.append("%s: availability=%s 却带着值——不可用状态不得携带数据" % (path, availability))
        if availability == PRESENT and obj.get("value") is None:
            problems.append("%s: availability=PRESENT 但值为 None" % path)

    for path in ("account_anchor", "stage_evidence", "current_cycle", "latest_cycle_decision"):
        check_field(projection.get(path), path)

    capacity = projection.get("capacity") or {}
    for key in ("expected_publish_count", "baseline_capacity", "actual_capacity"):
        if key not in capacity:
            problems.append("capacity.%s 缺失——三类产能必须分别承载" % key)
        else:
            check_field(capacity[key], "capacity.%s" % key)

    objectives = projection.get("objectives") or {}
    for key in ("primary", "priority_note"):
        if key not in objectives:
            problems.append("objectives.%s 缺失" % key)
        else:
            check_field(objectives[key], "objectives.%s" % key)

    permissions = projection.get("permissions") or {}
    if "expression_permission" not in permissions:
        problems.append("permissions.expression_permission 缺失")
    else:
        check_field(permissions["expression_permission"], "permissions.expression_permission")

    for dotted, dimensions in MANDATORY_DIMENSIONS.items():
        envelope = _dig(projection, dotted)
        if not isinstance(envelope, dict):
            continue  # 缺失本身已由上面的 check_field / required 检查负责
        for dimension in dimensions:
            if dimension in _PRESENT_ONLY_DIMENSIONS and envelope.get("availability") != PRESENT:
                continue
            if dimension not in envelope:
                problems.append(
                    "%s 缺维度 '%s'——五个正交维度不是可选装饰：省略它等于让"
                    "「不知道」和「没考虑过」不可区分" % (dotted, dimension)
                )

    for dotted, dimensions in MANDATORY_LIST_DIMENSIONS.items():
        rows = _dig(projection, dotted)
        if not isinstance(rows, list):
            continue
        for i, envelope in enumerate(rows):
            if not isinstance(envelope, dict):
                problems.append("%s[%d] 不是状态信封" % (dotted, i))
                continue
            for dimension in dimensions:
                if dimension in _PRESENT_ONLY_DIMENSIONS and envelope.get("availability") != PRESENT:
                    continue
                if dimension not in envelope:
                    problems.append("%s[%d] 缺维度 '%s'" % (dotted, i, dimension))

    if projection.get("schema_version") == SCHEMA_VERSION_V11:
        q = projection.get("market_observation_query")
        if not isinstance(q, dict):
            problems.append("v1.1 缺 market_observation_query——M2 的 excluded[] 与 gap_reason "
                            "丢掉后，「一条都没登记」「全被排除」「不在范围内」塌成同一个空数组")
        else:
            for key in ("queried_at", "filters", "available", "excluded", "gap_reason"):
                if key not in q:
                    problems.append("market_observation_query 缺 '%s'" % key)
            gr = q.get("gap_reason")
            if gr not in (None, "no_observation_recorded", "no_observation_in_scope",
                          "all_observations_excluded"):
                problems.append("market_observation_query.gap_reason 非法：%r" % (gr,))
            if q.get("available") and gr is not None:
                problems.append("market_observation_query 同时声称有可用观察与存在缺口")

    for i, obs in enumerate(projection.get("market_observations") or []):
        if obs.get("availability") not in AVAILABILITY_VALUES:
            problems.append("market_observations[%d].availability 非法" % i)
        if obs.get("layer") not in ("raw", "analysis", "homogeneous_judgment"):
            problems.append("market_observations[%d].layer 非法——原始观察/分析/同质判断必须分清" % i)

        permission = obs.get("usage_permission")
        if not isinstance(permission, dict):
            problems.append(
                "market_observations[%d].usage_permission 缺失——权限与时效是两个维度，不得只留时效" % i
            )
            continue
        usable = obs.get("usable_for_inference")
        if not isinstance(usable, bool):
            problems.append("market_observations[%d].usable_for_inference 必须是布尔" % i)
            continue

        if projection.get("schema_version") == SCHEMA_VERSION_V11:
            # v1.1 的五组语义，一组都不许坍缩。逐条检查，不靠 Schema——
            # Schema 只能查键在不在，查不了「第二道闸有没有被第一道闸顶替」。
            for key in ("source", "source_type", "source_reference", "source_provider"):
                if key not in obs:
                    problems.append("market_observations[%d] 缺来源分项 '%s'"
                                    "——四分来源合并成一个 source 就分不清"
                                    "「谁说的」与「哪儿看到的」" % (i, key))
            scope = obs.get("applicable_scope")
            if not isinstance(scope, dict):
                problems.append("market_observations[%d].applicable_scope 缺失"
                                "——一条属于别的账号/任务/期间的观察就无法被机械排除" % i)
            else:
                for key in ("account_id", "applicable_task_id", "applicable_track",
                            "applicable_period_start", "applicable_period_end",
                            "period_window_availability", "scope_ref"):
                    if key not in scope:
                        problems.append("market_observations[%d].applicable_scope 缺 '%s'" % (i, key))
                if scope.get("period_window_availability") not in AVAILABILITY_VALUES:
                    problems.append("market_observations[%d].applicable_scope."
                                    "period_window_availability 非法——期间窗取不到时必须是 "
                                    "UNKNOWN，不能填 null" % i)
            basis = permission.get("currently_usable_basis")
            if basis not in ("m2_explicit", "derived_from_status_allowlist", "no_permission_model"):
                problems.append("market_observations[%d].usage_permission.currently_usable_basis "
                                "非法——不记来源，「M2 说可用」与「我们按清单推的」不可区分" % i)
            if (basis == "derived_from_status_allowlist"
                    and permission.get("currently_usable") is not
                    (permission.get("status") in M2_CURRENTLY_USABLE_PERMISSION_STATUSES)):
                problems.append("market_observations[%d] 的 currently_usable 与 M2 自己的"
                                "允许清单不一致——派生必须 fail-closed" % i)
            epp = obs.get("external_publish_permission")
            if not isinstance(epp, dict):
                problems.append("market_observations[%d].external_publish_permission 缺失"
                                "——「能不能当证据」与「能不能对外发布」是两道闸，"
                                "M2 逐字写着 viewable never implies publishable" % i)
            else:
                if epp.get("availability") not in AVAILABILITY_VALUES:
                    problems.append("market_observations[%d].external_publish_permission."
                                    "availability 非法" % i)
                if epp.get("value") is True and epp.get("availability") != PRESENT:
                    problems.append("market_observations[%d] 声称可对外发布，"
                                    "但该位的 availability 不是 PRESENT" % i)
                if epp.get("value") is True and permission.get("usage_limits") is None:
                    problems.append("market_observations[%d] 在 M2 没有表达 usage_limits 的情况下"
                                    "声称可对外发布——这是执行侧替 M2 发明产品语义" % i)
            if "evidence_digest" not in obs:
                problems.append("market_observations[%d] 缺 evidence_digest 键"
                                "——它由调用方给、M2 不算，缺键与 null 必须可区分" % i)
        # 单向不等式：M3 侧的结论位不得比 M2 更宽松。
        if permission.get("currently_usable") is False and usable:
            problems.append(
                "market_observations[%d]: M2 已判定当前不可用（%s），投影却标为可用——"
                "权限未确认的观察被抬成可引用证据是 M3-AC-09/AC-12 的直接 FAIL"
                % (i, permission.get("excluded_reason"))
            )
        if obs.get("availability") != PRESENT and usable:
            problems.append(
                "market_observations[%d]: availability=%s 却标为可用——过期证据不得参与推理"
                % (i, obs.get("availability"))
            )

    for i, item in enumerate(projection.get("feedback") or []):
        for key in ("is_test", "is_simulated", "is_manual_entry", "is_pre_publish_review"):
            if not isinstance(item.get(key), bool):
                problems.append("feedback[%d].%s 必须是布尔——证据身份不得缺省" % (i, key))
        bound = item.get("bound_to") or {}
        if bound.get("binding_kind") not in ("publish_instance", "content_version"):
            problems.append("feedback[%d].bound_to.binding_kind 非法" % i)

    return problems


def _walk_keys(node, path="$"):
    if isinstance(node, dict):
        for key, value in node.items():
            yield key, "%s.%s" % (path, key)
            for pair in _walk_keys(value, "%s.%s" % (path, key)):
                yield pair
    elif isinstance(node, list):
        for i, item in enumerate(node):
            for pair in _walk_keys(item, "%s[%d]" % (path, i)):
                yield pair


def validate_writeback_candidate(candidate):
    """M3 → M2 候选信封的跨字段与禁区校验。返回违规说明列表；空列表 = 通过。"""

    problems = []

    if candidate.get("schema_version") != SCHEMA_VERSION:
        problems.append("schema_version 必须是 %s" % SCHEMA_VERSION)

    # 唯一合法状态。信封在语法层就无法表达"已接受"。
    if candidate.get("candidate_status") != "proposed":
        problems.append("candidate_status 只能是 'proposed'——接受与当前有效版本不属于 M3")

    kind = candidate.get("candidate_kind")
    if kind not in ("diagnosis", "cycle_plan", "content_task_set", "review_update", "no_content_task"):
        problems.append("candidate_kind 非法 (%r)" % (kind,))

    based_on = candidate.get("based_on")
    if not isinstance(based_on, list) or not based_on:
        problems.append("based_on 至少要有一条——没有依据的候选不是判断")
    else:
        for i, item in enumerate(based_on):
            if not isinstance(item, dict) or not item.get("evidence_identity"):
                problems.append("based_on[%d] 缺 evidence_identity——证据身份不得混写" % i)

    affects = candidate.get("affects")
    if not isinstance(affects, dict):
        problems.append("affects 缺失")
    else:
        for key in ("invalidates", "explicitly_unchanged"):
            if not isinstance(affects.get(key), list):
                problems.append(
                    "affects.%s 必须存在——'明确保持不变'写不出来时，它与'没想过'不可区分" % key
                )

    if kind == "no_content_task":
        block = candidate.get("no_content_task")
        if not isinstance(block, dict):
            problems.append("candidate_kind=no_content_task 必须带 no_content_task 四要素")
        else:
            for key in ("reason", "grounded_in", "scope", "reopen_trigger"):
                if not block.get(key):
                    problems.append("no_content_task.%s 缺失——四要素缺一即是逃避工作" % key)

    for key, path in _walk_keys(candidate):
        if key in FORBIDDEN_WRITEBACK_KEYS:
            problems.append(
                "%s: 出现禁用键 '%s'——晋升、接受、覆盖反馈与改写来源都不属于 M3" % (path, key)
            )

    return problems


# --- Dify code 节点用法示例 -------------------------------------------------
# 与 business-persistence/dify/m2_candidate.yaml 中已有的 code 节点同形：
#
#     def main(m2_payload: str, requested_payload: str, workspace_id: str,
#              account_id: str, now_iso: str) -> dict:
#         import json
#         m2 = json.loads(m2_payload) if m2_payload else {}
#         requested = json.loads(requested_payload) if requested_payload else {}
#         projection = build_projection(workspace_id, account_id, m2,
#                                       requested=requested, compiled_at=now_iso)
#         problems = validate_projection(projection)
#         return {"projection": json.dumps(projection, ensure_ascii=False),
#                 "problems": json.dumps(problems, ensure_ascii=False),
#                 "ok": 1 if not problems else 0}
#
# `ok=0` 时不得继续调用 LLM 节点：带着坍缩状态的投影跑出来的判断，看起来和正常的
# 一模一样，而这正是最难被发现的失败。
