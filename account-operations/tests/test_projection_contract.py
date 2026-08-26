"""M2→M3 投影 与 M3→M2 候选信封 的契约测试。

跑法（仓库根或任意目录，绝对路径）：

    python3 -m unittest discover -s account-operations/tests -v

为什么用 stdlib unittest 而不是 pytest：宿主 python 3.10.12 没装 pytest，也没装
pydantic。M2 自己的测试跑在 Docker 里、打的是 live HTTP（`conftest.py` 的
`APP_BASE_URL=http://diyu-m2-app:8000`），那套依赖在这里不可得。本轮要的是"离线可跑、
不需要数据库"的契约证据，所以走标准库。

为什么用 Draft7Validator 校验标着 draft/2020-12 的 schema：宿主的 jsonschema 是
3.2.0，只有 draft-7 校验器。schema 文件按仓库既有惯例（`V1_TASK_SNAPSHOT_SCHEMA_v0.1.json`）
标 2020-12，但**只使用两个 draft 语义完全一致的关键字**。
`test_schemas_avoid_2020_12_only_keywords` 是守卫：一旦有人加了 2020-12 专有关键字，
降级校验就不再可靠，那条测试会先炸。

证据等级：`static_verified`。样本是**依据 M2 的模型与 API 源码手工构造**的，
不是从运行中的 M2 实例抓的真实响应——真实响应比对属于 EP-05/EP-06。
"""

import json
import os
import sys
import unittest

_HERE = os.path.dirname(os.path.abspath(__file__))
_INTERFACES = os.path.join(os.path.dirname(_HERE), "interfaces")
if _INTERFACES not in sys.path:
    sys.path.insert(0, _INTERFACES)

import projection as P  # noqa: E402

try:
    from jsonschema import Draft7Validator
except ImportError:  # pragma: no cover
    Draft7Validator = None

PROJECTION_SCHEMA_PATH = os.path.join(_INTERFACES, "M2_TO_M3_PROJECTION_v1.0.schema.json")
WRITEBACK_SCHEMA_PATH = os.path.join(_INTERFACES, "M3_TO_M2_WRITEBACK_CANDIDATE_v1.0.schema.json")
CONTENT_TASK_SCHEMA_PATH = os.path.join(_INTERFACES, "M3_CONTENT_TASK_v1.0.schema.json")

DRAFT_2020_12_ONLY_KEYWORDS = (
    "$defs",
    "prefixItems",
    "unevaluatedItems",
    "unevaluatedProperties",
    "dependentSchemas",
    "dependentRequired",
    "$dynamicRef",
    "$dynamicAnchor",
)


def load(path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def errors(schema, instance):
    if Draft7Validator is None:
        raise unittest.SkipTest("jsonschema 不可用")
    return sorted(Draft7Validator(schema).iter_errors(instance), key=lambda e: list(e.path))


# --- 依据 M2 源码手工构造的响应样本 -----------------------------------------
# 字段名与类型取自 business-persistence@main:df2c595 的
# app/models/{operations,knowledge,publish}.py 与 app/api/*.py。

M2_CURRENT_CYCLE = {
    "id": "cyc-0001",
    "workspace_id": "ws-0001",
    "account_id": "acc-0001",
    "label": "2026-08 周期",
    "start_at": "2026-08-01T00:00:00+00:00",
    "end_at": None,
    "baseline_capacity": 10,
    "baseline_capacity_source": "团队自述",
    "actual_capacity": 2,
    "actual_capacity_source": "本周排班",
    "expected_publish_count": 21,
    "expected_publish_count_source": "用户本轮要求",
    "is_current": True,
    "supersedes_cycle_id": None,
    "created_at": "2026-08-01T00:00:00+00:00",
}

M2_ACTIVE_OVERRIDES = [
    {
        "id": "ovr-0001",
        "name": "秋上新冲刺",
        "status": "active",
        "targeted_positions": ["slot-2", "slot-5"],
        "scope_start": "2026-08-20T00:00:00+00:00",
        "scope_end": "2026-08-31T00:00:00+00:00",
        "rationale": "新品到货窗口",
    }
]

M2_MARKET_OBSERVATIONS = [
    {
        "id": "obs-current",
        "source": "平台榜单",
        "platform": "douyin",
        "collected_at": "2026-08-20T00:00:00+00:00",
        "applicable_track": "女装",
        "scope_ref": {"region": "华东"},
        "mechanism_summary": "通勤场景内容集中度上升",
        "layer": "analysis",
        "valid_until": "2026-09-30T00:00:00+00:00",
        "is_expired": False,
    },
    {
        "id": "obs-stale",
        "source": "旧报告",
        "platform": "douyin",
        "collected_at": "2026-03-01T00:00:00+00:00",
        "applicable_track": "女装",
        "scope_ref": {},
        "mechanism_summary": "春季通勤",
        "layer": "raw",
        "valid_until": "2026-05-01T00:00:00+00:00",
        "is_expired": True,
    },
    {
        "id": "obs-other-track",
        "source": "平台榜单",
        "platform": "douyin",
        "collected_at": "2026-08-20T00:00:00+00:00",
        "applicable_track": "母婴",
        "scope_ref": {},
        "mechanism_summary": "与本账号无关",
        "layer": "raw",
        "valid_until": None,
        "is_expired": False,
    },
]

M2_FEEDBACK = [
    {
        "id": "fb-real",
        "publish_instance_id": "pub-0001",
        "content_version_id": None,
        "kind": "observation",
        "is_test": False,
        "is_simulated": False,
        "is_manual_entry": False,
        "is_pre_publish_review": False,
        "source": "平台后台",
        "observed_at": "2026-08-22T00:00:00+00:00",
        "window_start": "2026-08-21T00:00:00+00:00",
        "window_end": "2026-08-24T00:00:00+00:00",
        "goal_at_the_time": "吸粉",
        "payload": {"views": 12000},
    },
    {
        "id": "fb-sim",
        "publish_instance_id": None,
        "content_version_id": "cv-0001",
        "kind": "observation",
        "is_test": True,
        "is_simulated": True,
        "is_manual_entry": False,
        "is_pre_publish_review": True,
        "source": "工程夹具",
        "observed_at": "2026-08-25T00:00:00+00:00",
        "window_start": None,
        "window_end": "2026-09-30T00:00:00+00:00",
        "goal_at_the_time": "吸粉",
        "payload": {"note": "模拟"},
    },
]

NOW = "2026-08-26T00:00:00+00:00"


def build_sample(requested_overrides=None, m2_overrides=None):
    m2 = {
        "current_cycle": M2_CURRENT_CYCLE,
        "active_overrides": M2_ACTIVE_OVERRIDES,
        "latest_cycle_decision": {"decision": "none_recorded"},
        "market_observations": M2_MARKET_OBSERVATIONS,
        "feedback": M2_FEEDBACK,
    }
    m2.update(m2_overrides or {})
    requested = {
        "account_anchor": {"positioning": "城市通勤女装选购顾问", "provisional": True},
        "primary_objective": "吸粉",
        "secondary_objectives": ["GMV"],
        "priority_note": "吸粉优先；GMV 不得牺牲事实纪律",
        "non_sacrifice_conditions": ["不编造库存与价格"],
        "stage_evidence": {"history": "连续更新 6 周", "repeatable_mechanism": "尚不确定"},
        "expression_permission": "允许情境模拟；不允许站外导流",
        "cta_authorizations": [],
        "applicable_tracks": ["女装"],
        "gaps": [],
        "task_id": "task-0001",
    }
    requested.update(requested_overrides or {})
    return P.build_projection("ws-0001", "acc-0001", m2, requested=requested, compiled_at=NOW)


class SchemaHygiene(unittest.TestCase):
    def test_schemas_are_wellformed_json(self):
        for path in (PROJECTION_SCHEMA_PATH, WRITEBACK_SCHEMA_PATH, CONTENT_TASK_SCHEMA_PATH):
            with self.subTest(path=os.path.basename(path)):
                self.assertIsInstance(load(path), dict)

    def test_schemas_avoid_2020_12_only_keywords(self):
        """守卫：只要 schema 里出现 2020-12 专有关键字，用 Draft7Validator 校验就
        不再可靠（该关键字会被静默忽略，测试会假通过）。宁可先炸在这里。
        """

        for path in (PROJECTION_SCHEMA_PATH, WRITEBACK_SCHEMA_PATH, CONTENT_TASK_SCHEMA_PATH):
            with open(path, encoding="utf-8") as handle:
                raw = handle.read()
            for keyword in DRAFT_2020_12_ONLY_KEYWORDS:
                with self.subTest(path=os.path.basename(path), keyword=keyword):
                    self.assertNotIn(
                        '"%s"' % keyword,
                        raw,
                        "%s 使用了 2020-12 专有关键字 %s，降级到 draft-7 校验不再可靠"
                        % (os.path.basename(path), keyword),
                    )


class ProjectionShape(unittest.TestCase):
    def test_projection_matches_schema(self):
        self.assertEqual([], errors(load(PROJECTION_SCHEMA_PATH), build_sample()))

    def test_projection_passes_cross_field_invariants(self):
        self.assertEqual([], P.validate_projection(build_sample()))

    def test_three_capacity_values_stay_separate(self):
        capacity = build_sample()["capacity"]
        self.assertEqual(21, capacity["expected_publish_count"]["value"])
        self.assertEqual(10, capacity["baseline_capacity"]["value"])
        self.assertEqual(2, capacity["actual_capacity"]["value"])
        # 每个数字带着自己的来源，不共用一个。
        self.assertEqual("用户本轮要求", capacity["expected_publish_count"]["source_ref"])
        self.assertEqual("本周排班", capacity["actual_capacity"]["source_ref"])

    def test_missing_capacity_key_is_caught_by_invariants(self):
        broken = build_sample()
        del broken["capacity"]["actual_capacity"]
        self.assertTrue(
            any("actual_capacity" in p for p in P.validate_projection(broken)),
            "删掉一类产能必须被抓到——三值合一会让产能取舍全部变成假的",
        )


class AntiCollapse(unittest.TestCase):
    """M3-AC-12 的核心：六种"没有值"两两不等，不得坍缩为同一个 null。"""

    def test_five_absence_kinds_are_distinguishable(self):
        seen = {}
        for availability in (P.UNKNOWN, P.NOT_PROVIDED, P.NOT_APPLICABLE, P.REFUSED, P.EXPIRED):
            proj = build_sample(
                requested_overrides={"declared_absences": {"capacity.actual_capacity": availability}}
            )
            envelope = proj["capacity"]["actual_capacity"]
            self.assertIsNone(envelope["value"], "不可用状态不得携带数据")
            seen[availability] = envelope["availability"]
        self.assertEqual(5, len(set(seen.values())), "五种缺失被坍缩成了同一个状态：%r" % seen)

    def test_m2_null_degrades_to_unknown_never_to_refused_or_not_provided(self):
        """M2 当前表结构承载不了"用户拒绝告诉我们产能"。

        既然承载不了，就必须是 UNKNOWN——猜成 REFUSED 或 NOT_PROVIDED 等于凭空
        伪造一个证据身份。这条是本轮登记的 M2 能力缺口的直接后果。
        """

        cycle = dict(M2_CURRENT_CYCLE, actual_capacity=None, actual_capacity_source=None)
        proj = build_sample(m2_overrides={"current_cycle": cycle})
        self.assertEqual(P.UNKNOWN, proj["capacity"]["actual_capacity"]["availability"])

    def test_declared_refusal_survives_even_when_m2_has_a_value(self):
        proj = build_sample(
            requested_overrides={"declared_absences": {"capacity.actual_capacity": P.REFUSED}}
        )
        envelope = proj["capacity"]["actual_capacity"]
        self.assertEqual(P.REFUSED, envelope["availability"])
        self.assertIsNone(envelope["value"], "REFUSED 却带值 = 给「拒绝提供」留了个偷带数据的后门")

    def test_none_recorded_is_unknown_not_kept_unchanged(self):
        """M2 无决策记录时返回 {"decision": "none_recorded"}。

        "从没评估过"和"评估过并决定保持不变"是两个完全不同的运营事实；让它们同形，
        复盘纪律就没有了立足点。
        """

        never = build_sample()
        self.assertEqual(P.UNKNOWN, never["latest_cycle_decision"]["availability"])

        held = build_sample(
            m2_overrides={
                "latest_cycle_decision": {
                    "id": "dec-0001",
                    "decision": "kept_unchanged",
                    "rationale": "证据不足，保持不变",
                    "created_at": "2026-08-25T00:00:00+00:00",
                }
            }
        )
        self.assertEqual(P.PRESENT, held["latest_cycle_decision"]["availability"])
        self.assertEqual("kept_unchanged", held["latest_cycle_decision"]["value"]["decision"])


class EvidenceIdentity(unittest.TestCase):
    def test_expired_observation_is_kept_and_marked_not_dropped(self):
        obs = {o["observation_id"]: o for o in build_sample()["market_observations"]}
        self.assertIn("obs-stale", obs, "丢弃过期观察会让'证据已过期'本身不可见")
        self.assertEqual(P.EXPIRED, obs["obs-stale"]["availability"])
        self.assertEqual(P.PRESENT, obs["obs-current"]["availability"])

    def test_off_track_observation_is_not_projected(self):
        ids = {o["observation_id"] for o in build_sample()["market_observations"]}
        self.assertNotIn("obs-other-track", ids, "最小必要投影不得把无关赛道的观察也带上")

    def test_observation_layer_is_preserved(self):
        obs = {o["observation_id"]: o for o in build_sample()["market_observations"]}
        self.assertEqual("analysis", obs["obs-current"]["layer"])
        self.assertEqual("raw", obs["obs-stale"]["layer"])

    def test_simulated_feedback_stays_distinguishable_from_real(self):
        feedback = {f["feedback_id"]: f for f in build_sample()["feedback"]}
        self.assertFalse(feedback["fb-real"]["is_simulated"])
        self.assertTrue(feedback["fb-sim"]["is_simulated"])
        self.assertTrue(feedback["fb-sim"]["is_test"])
        # 结构等价不代表业务身份等价——绑定对象也不同。
        self.assertEqual("publish_instance", feedback["fb-real"]["bound_to"]["binding_kind"])
        self.assertEqual("content_version", feedback["fb-sim"]["bound_to"]["binding_kind"])

    def test_unclosed_observation_window_is_visible(self):
        feedback = {f["feedback_id"]: f for f in build_sample()["feedback"]}
        self.assertTrue(feedback["fb-real"]["window_closed"])
        self.assertFalse(feedback["fb-sim"]["window_closed"], "窗口未结束时不得据此改判")

    def test_only_named_campaign_positions_are_covered(self):
        overlay = build_sample()["campaign_overlays"][0]
        self.assertEqual(["slot-2", "slot-5"], overlay["targeted_positions"])


class FieldAblation(unittest.TestCase):
    """FX-M3-ABL-02：逐项删除投影的必填顶层字段。

    删掉之后如果**没有**任何检查失败，该字段就没有挣到自己的存在（A5 消融律），
    必须删除或合并。这条测试就是那把尺子。
    """

    def test_removing_any_required_top_level_field_fails_validation(self):
        schema = load(PROJECTION_SCHEMA_PATH)
        base = build_sample()
        for name in schema["required"]:
            with self.subTest(field=name):
                ablated = dict(base)
                del ablated[name]
                self.assertTrue(
                    errors(schema, ablated),
                    "删掉 %s 之后校验仍然通过——这个字段不成立，应删除或合并" % name,
                )

    def test_unknown_field_is_rejected(self):
        polluted = dict(build_sample(), full_account_history=["…"])
        self.assertTrue(
            errors(load(PROJECTION_SCHEMA_PATH), polluted),
            "additionalProperties:false 必须挡住过量投影",
        )


VALID_CANDIDATE = {
    "schema_version": "1.0",
    "candidate_id": "cand-0001",
    "produced_at": NOW,
    "binding": {
        "workspace_id": "ws-0001",
        "account_id": "acc-0001",
        "projection_id": "proj-acc-0001",
        "cycle_id": "cyc-0001",
        "skill_version": "operating-one-account@v1.0",
        "model_ref": None,
    },
    "candidate_status": "proposed",
    "candidate_kind": "review_update",
    "rationale": "实际产能只支持两条，第三条延期",
    "based_on": [
        {"ref": "capacity.actual_capacity", "evidence_identity": "confirmed_fact", "note": None},
        {"ref": "feedback:fb-real", "evidence_identity": "real_publication_observation", "note": None},
    ],
    "payload": {"cycle_delta": {"defer": ["slot-3"]}},
    "affects": {
        "invalidates": ["task-0003"],
        "explicitly_unchanged": ["task-0001", "task-0002"],
        "stale_unknown_impact": [],
    },
    "suggested_m2_endpoint": "POST /workspaces/{workspace_id}/accounts/{account_id}/cycles/decisions",
}


class WritebackCandidate(unittest.TestCase):
    def test_valid_candidate_passes_schema_and_invariants(self):
        self.assertEqual([], errors(load(WRITEBACK_SCHEMA_PATH), VALID_CANDIDATE))
        self.assertEqual([], P.validate_writeback_candidate(VALID_CANDIDATE))

    def test_candidate_status_cannot_be_accepted(self):
        """接受与当前有效版本属于 M2 和用户。信封在语法层就不该表达得出来。"""

        for status in ("accepted", "current", "promoted"):
            with self.subTest(status=status):
                bad = dict(VALID_CANDIDATE, candidate_status=status)
                self.assertTrue(errors(load(WRITEBACK_SCHEMA_PATH), bad))
                self.assertTrue(P.validate_writeback_candidate(bad))

    def test_forbidden_promotion_keys_are_rejected_anywhere_in_the_tree(self):
        for key in ("is_current", "accepted", "overwrite", "feedback_override", "source_override"):
            with self.subTest(key=key):
                bad = dict(VALID_CANDIDATE, payload={"cycle_delta": {key: True}})
                problems = P.validate_writeback_candidate(bad)
                self.assertTrue(problems, "深埋在 payload 里的禁用键 %s 没被抓到" % key)

    def test_candidate_without_evidence_is_rejected(self):
        bad = dict(VALID_CANDIDATE, based_on=[])
        self.assertTrue(P.validate_writeback_candidate(bad), "没有依据的候选不是判断")

    def test_explicitly_unchanged_is_mandatory(self):
        bad = dict(VALID_CANDIDATE, affects={"invalidates": ["task-0003"]})
        self.assertTrue(
            P.validate_writeback_candidate(bad),
            "写不出'明确保持不变'时，它和'根本没想过'不可区分",
        )

    def test_suggested_endpoints_are_limited_to_existing_m2_write_endpoints(self):
        """反面保证：信封里没有任何一个指向反馈或市场观察的写端点。

        M3 不生成、不覆盖、不重写原始反馈，也不修改来源（M3-AC-13）。
        """

        allowed = load(WRITEBACK_SCHEMA_PATH)["properties"]["suggested_m2_endpoint"]["enum"]
        for endpoint in allowed:
            self.assertNotIn("feedback", endpoint.lower())
            self.assertNotIn("market-observation", endpoint.lower())

    def test_no_content_task_requires_all_four_elements(self):
        for missing in ("reason", "grounded_in", "scope", "reopen_trigger"):
            with self.subTest(missing=missing):
                block = {
                    "reason": "到店承接当前无人可接",
                    "grounded_in": ["门店当前无可用服务时段（来源=用户本轮陈述）"],
                    "scope": {"affected": ["到店类任务"], "unaffected": ["商品知识类任务"]},
                    "reopen_trigger": ["门店给出可承接时段"],
                }
                del block[missing]
                bad = dict(VALID_CANDIDATE, candidate_kind="no_content_task", no_content_task=block)
                self.assertTrue(
                    P.validate_writeback_candidate(bad),
                    "缺 %s 的无任务结论是逃避工作，不是判断" % missing,
                )


VALID_CONTENT_TASK = {
    "schema_version": "1.0",
    "result_kind": "content_task",
    "content_task": {
        "task_id": "ct-0001",
        "upstream_kind": "continuous_operation_decision",
        "cycle_role": {"value": "稳定兑现", "availability": "PRESENT", "note": None},
        "account": "acc-0001",
        "platform": {"value": "douyin", "availability": "PRESENT", "note": None},
        "content_form": {"value": "口播", "availability": "PRESENT", "note": None},
        "primary_job": "回答'通勤穿搭怎么在同一套里兼顾正式与松弛'",
        "secondary_contributions": ["为后续系列建立追更理由"],
        "priority": "吸粉优先于 GMV",
        "non_sacrifice_conditions": ["不编造库存与价格"],
        "audience_problem": "早上要出门但衣柜里挑不出能同时开会和下班的搭配",
        "audience_shift": "看完知道用哪一件做支点，明早能直接照做",
        "promise_or_hypothesis": "一件外套 + 两种下装可以覆盖两种场合",
        "facts": [
            {
                "statement": "该外套材质为羊毛混纺",
                "source": "商品资料库",
                "evidence_identity": "confirmed_fact",
                "valid_until": None,
            }
        ],
        "gaps": ["没有上身素材，版型与体感主张需降级或条件化"],
        "product_conditions": {"value": {"stock": "在售"}, "availability": "PRESENT", "note": None},
        "capacity": {
            "actual_capacity_note": "本周实际可完成两条，本条占其一",
            "timing": "本周内",
            "critical_material_needs": ["外套平铺细节素材"],
            "infeasible_if": ["平铺素材也拿不到"],
        },
        "permission": {
            "cta_class": "in_platform_low_risk",
            "cta_intent": {"value": "引导收藏", "availability": "PRESENT", "note": None},
            "fulfillment_path_verified": None,
            "authorization_ref": None,
            "risk_boundary": "不做价格与优惠承诺；不做站外导流",
        },
        "explicit_non_promise": ["不承诺显瘦", "不承诺现货尺码齐全"],
        "observation_target": {
            "what_to_observe": "收藏与追更意图相关的评论",
            "evidence_identity_expected": "real_publication_observation",
            "expires_at": None,
        },
        "m2_binding": {"value": {"cycle_id": "cyc-0001"}, "availability": "PRESENT", "note": None},
        "downstream_freedom": ["钩子与开场未定", "叙事结构未定", "镜头与包装未定"],
    },
}


class ContentTaskShape(unittest.TestCase):
    def test_valid_content_task_matches_schema(self):
        self.assertEqual([], errors(load(CONTENT_TASK_SCHEMA_PATH), VALID_CONTENT_TASK))

    def test_primary_job_is_single_valued(self):
        """一条任务只有一个主要业务工作。写成数组就等于允许"全都要"。"""

        bad = json.loads(json.dumps(VALID_CONTENT_TASK))
        bad["content_task"]["primary_job"] = ["吸粉", "GMV", "到店"]
        self.assertTrue(errors(load(CONTENT_TASK_SCHEMA_PATH), bad))

    def test_creative_fields_cannot_be_smuggled_in(self):
        """M3 越界最可能的形态不是显式违规，是"顺手多给一个字段"。

        additionalProperties:false 让钩子/台词/镜头/标题在语法层就进不来。
        """

        for smuggled in ("hook", "script", "shot_list", "title", "cover_copy"):
            with self.subTest(field=smuggled):
                bad = json.loads(json.dumps(VALID_CONTENT_TASK))
                bad["content_task"][smuggled] = "……"
                self.assertTrue(
                    errors(load(CONTENT_TASK_SCHEMA_PATH), bad),
                    "%s 被夹带进内容任务而没有被挡住" % smuggled,
                )

    def test_downstream_freedom_must_be_nonempty(self):
        bad = json.loads(json.dumps(VALID_CONTENT_TASK))
        bad["content_task"]["downstream_freedom"] = []
        self.assertTrue(
            errors(load(CONTENT_TASK_SCHEMA_PATH), bad),
            "一条创意空间都写不出来，通常意味着 M3 已经替下游做完了",
        )

    def test_no_content_task_shape_is_accepted(self):
        instance = {
            "schema_version": "1.0",
            "result_kind": "no_content_task",
            "no_content_task": {
                "reason": "本条依赖的到店承接当前没人能接",
                "grounded_in": ["门店当前无可用服务时段（来源=用户本轮陈述）"],
                "scope": {
                    "affected": ["到店类任务"],
                    "unaffected": ["商品知识类任务", "搭配原则类任务"],
                },
                "reopen_trigger": ["门店给出可承接时段"],
            },
        }
        self.assertEqual([], errors(load(CONTENT_TASK_SCHEMA_PATH), instance))


if __name__ == "__main__":
    unittest.main(verbosity=2)
