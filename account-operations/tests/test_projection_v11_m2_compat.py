"""M3 投影 v1.1 对当前有效 M2 接口（`main@a7b8101`）的兼容契约。

分工：`test_projection_contract.py` 用手工样本证明 v1.0 内部自洽；
`test_live_m2_contract.py` 用 v1 实况证明我们对旧 M2 的形状假设成立；
**这一份用 v2 实况（`m2_live_capture_v2.json`，从运行中的 M2 原样抓取、未经手工编辑）
证明 v1.1 把新 M2 的五组语义一组不落地承载下来，而且没有一组被另一组顶替。**

为什么必须用实况而不是手工样本：v1 的三条演示观察全是 `permission_status=unknown`、
无 `usage_limits`、无 `evidence_digest`、无期间窗——**拿它去测 v1.1 等于什么都没测**。
v2 的抓取脚本因此把五组语义各自逼出一条真实响应。
"""
import json
import os
import sys
import unittest

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
_INTERFACES = os.path.join(_ROOT, "interfaces")
if _INTERFACES not in sys.path:
    sys.path.insert(0, _INTERFACES)

import projection as P  # noqa: E402

try:
    from jsonschema import Draft7Validator
except ImportError:                                   # pragma: no cover
    Draft7Validator = None

CAPTURE = os.path.join(_ROOT, "fixtures", "m2_live_capture_v2.json")
SCHEMA_V11 = os.path.join(_INTERFACES, "M2_TO_M3_PROJECTION_v1.1.schema.json")


def _load():
    with open(CAPTURE, encoding="utf-8") as h:
        return json.load(h)


def _build(cap, source="current", read_key="market_observations__current_track"):
    r = cap["reads"]
    cur = r["market_observations__current_track"]
    rows = cur["observations"] if source == "current" else r["market_observations"]
    m2 = {
        "current_cycle": r["cycles_current__full"],
        "active_overrides": r["campaign_overrides_active__full"],
        "latest_cycle_decision": r["cycle_decisions_latest__full"],
        "market_observations": rows,
        "market_observations_current": cur,
        "feedback": r["publish_instance_feedback"],
    }
    return P.build_projection(
        cap["workspace"]["id"], cap["account_full"]["id"], m2,
        requested={"applicable_tracks": None, "primary_objective": "长期价值",
                   "expression_permission": "低风险互动 CTA 可自主提出"},
        projection_id="test-v11", compiled_at=cap["capture_meta"]["frozen_now"],
        schema_version="1.1", market_observation_source=source)


class BindingAndBaseline(unittest.TestCase):
    def test_capture_is_bound_to_a7b8101(self):
        meta = _load()["capture_meta"]
        self.assertEqual(meta["bound_baseline"], "business-persistence@main:a7b8101")
        # v1 抓取时那两个文件还只在 M2 任务分支上，所以 v1 记了分歧栏。
        # v2 抓取时容器与 a7b8101 逐字节相同，分歧栏必须**消失**而不是被改小。
        self.assertNotIn("baseline_divergence", meta)
        self.assertIn("baseline_equivalence_claim", meta)

    def test_projection_declares_the_new_baseline(self):
        proj = _build(_load())
        self.assertEqual(proj["schema_version"], "1.1")
        self.assertEqual(proj["binding"]["m2_interface_baseline"],
                         "business-persistence@main:a7b8101")


class FiveSemanticGroupsSurvive(unittest.TestCase):
    """Founder 第 2 条点名的五组：来源、当前可用性、对外发布权限、适用范围、证据身份。"""

    def setUp(self):
        self.cap = _load()
        self.proj = _build(self.cap, source="list", read_key="market_observations")
        self.obs = self.proj["market_observations"]
        self.assertTrue(self.obs, "实况夹具里必须有观察，否则本组测试什么都没测")

    def test_source_is_carried_in_four_parts(self):
        keys = ("source", "source_type", "source_reference", "source_provider")
        for o in self.obs:
            for k in keys:
                self.assertIn(k, o, "四分来源合并成一个就分不清「谁说的」与「哪儿看到的」")
        # 夹具里必须真的有一条四项齐全的，否则这条测试是空转
        self.assertTrue(any(all(o.get(k) for k in keys) for o in self.obs))

    def test_currently_usable_is_fail_closed_allowlist(self):
        by_status = {}
        for o in self.obs:
            by_status.setdefault(o["usage_permission"]["status"], []).append(o)
        self.assertIn("unknown", by_status, "夹具必须含 permission_status=unknown 的观察")
        for o in by_status["unknown"]:
            self.assertFalse(o["usage_permission"]["currently_usable"])
            self.assertFalse(o["usable_for_inference"],
                             "权限未确认的观察不得可用于推理——这正是 M2 默认 unknown 的用意")
        for st in ("allowed", "restricted"):
            for o in by_status.get(st, []):
                self.assertTrue(o["usage_permission"]["currently_usable"])
        for o in by_status.get("denied", []):
            self.assertFalse(o["usable_for_inference"])

    def test_unknown_permission_status_is_fail_closed_not_fail_open(self):
        """v1.0 在这里是 fail-open 的，v1.1 修掉。这条测试就是那个缺陷的负向夹具。

        v1.0：`usable_for_inference = availability == PRESENT and currently_usable is not False`
        —— `/current` 端点不返回 `currently_usable`，于是它是 None，`None is not False` 为真，
        一条 `permission_status='unknown'` 的观察被判成可用于推理。
        """
        row = {"id": "x", "layer": "raw", "permission_status": "unknown",
               "valid_until": None, "applicable_track": None}
        v10 = P._project_market_observations([row], None, "2026-08-26T00:00:00+00:00")[0]
        v11 = P._project_market_observations_v11([row], None, "2026-08-26T00:00:00+00:00")[0]
        self.assertTrue(v10["usable_for_inference"], "这条断言记录的是 v1.0 的实际行为（fail-open）")
        self.assertFalse(v11["usable_for_inference"], "v1.1 必须 fail-closed")

    def test_future_unknown_status_value_is_also_excluded(self):
        """允许清单，不是拒绝清单：M2 将来新增一个没见过的状态值也必须被排除。"""
        row = {"id": "x", "layer": "raw", "permission_status": "some_future_status",
               "valid_until": None, "applicable_track": None}
        o = P._project_market_observations_v11([row], None, "2026-08-26T00:00:00+00:00")[0]
        self.assertFalse(o["usage_permission"]["currently_usable"])
        self.assertFalse(o["usable_for_inference"])

    def test_publishability_is_never_derived_from_usability(self):
        """M2 模型注释逐字：viewable never implies publishable。

        M2 **没有定义** usage_limits 的结构，所以 M3 不替它发明一个可发布判断——
        该位恒为 UNKNOWN/null。由第一道闸推出第二道，就是执行侧创造产品语义。
        """
        for o in self.obs:
            epp = o["external_publish_permission"]
            self.assertEqual(epp["availability"], "UNKNOWN")
            self.assertIsNone(epp["value"])
            self.assertTrue(epp["basis"])
        usable = [o for o in self.obs if o["usable_for_inference"]]
        self.assertTrue(usable, "夹具里必须有可用于推理的观察，否则本条是空转")
        for o in usable:
            self.assertIsNone(o["external_publish_permission"]["value"],
                              "可推理 ≠ 可发布，两道闸不得互相顶替")

    def test_usage_limits_travels_verbatim(self):
        limited = [o for o in self.obs if o["usage_permission"]["usage_limits"]]
        self.assertTrue(limited, "夹具必须含一条带 usage_limits 的 restricted 观察")
        for o in limited:
            self.assertEqual(o["usage_permission"]["status"], "restricted")
            self.assertIn("internal_only", o["usage_permission"]["usage_limits"])

    def test_applicable_scope_has_all_five_dimensions(self):
        for o in self.obs:
            sc = o["applicable_scope"]
            for k in ("account_id", "applicable_task_id", "applicable_track",
                      "applicable_period_start", "applicable_period_end",
                      "period_window_availability", "scope_ref"):
                self.assertIn(k, sc)

    def test_period_window_from_list_is_present_from_current_is_unknown(self):
        """M2 的 /current 最小投影不返回 applicable_period_*。
        取不到就记 UNKNOWN，**不猜也不填 null**——两者必须可区分。"""
        from_list = _build(self.cap, source="list")["market_observations"]
        from_current = _build(self.cap, source="current")["market_observations"]
        self.assertTrue(any(o["applicable_scope"]["period_window_availability"] == "PRESENT"
                            for o in from_list))
        self.assertTrue(from_current)
        for o in from_current:
            self.assertEqual(o["applicable_scope"]["period_window_availability"], "UNKNOWN")

    def test_evidence_digest_key_always_present(self):
        for o in self.obs:
            self.assertIn("evidence_digest", o,
                          "它由调用方给、M2 不算，因此缺键与 null 必须可区分")
        self.assertTrue(any(o["evidence_digest"] for o in self.obs))


class GapAccountingSurvives(unittest.TestCase):
    """M2 明写它 never fabricates a comparison。它的缺口账不得被投影丢掉。"""

    def test_three_gap_reasons_are_distinguishable(self):
        cap = _load()
        seen = {cap["reads"][k]["gap_reason"] for k in
                ("market_observations__current_track",
                 "market_observations__current_other_account",
                 "market_observations__current_track_mismatch")}
        self.assertIn("no_observation_in_scope", seen)
        self.assertGreaterEqual(len(seen), 2, "实况必须真的分得开，不能只是 schema 里写着")

    def test_query_block_carries_excluded_and_gap_reason(self):
        proj = _build(_load())
        q = proj["market_observation_query"]
        self.assertTrue(q["excluded"], "被排除的观察必须逐条带原因，不能塌成空数组")
        for e in q["excluded"]:
            self.assertTrue(e["reason"])
        self.assertIn("filters", q)
        self.assertIsNotNone(q["filters"]["account_id"],
                             "不记下按什么范围问的，"
                             "「这个账号没有相关观察」与「压根没按这个账号问」就不可区分")

    def test_missing_query_block_is_a_validation_failure(self):
        proj = _build(_load())
        del proj["market_observation_query"]
        self.assertTrue(any("market_observation_query" in p
                            for p in P.validate_projection(proj)))


class FieldAblationV11(unittest.TestCase):
    """AC-12 ③ 的字段消融门，作用到 v1.1 新增的五组上。

    一个字段如果删掉之后没有任何检查会失败，它在结构上就没有挣到自己的存在（A5）。
    """

    def _ablate(self, mutate):
        proj = _build(_load())
        mutate(proj["market_observations"][0])
        return P.validate_projection(proj)

    def test_removing_source_parts_is_caught(self):
        self.assertTrue(self._ablate(lambda o: o.pop("source_type")))

    def test_removing_applicable_scope_is_caught(self):
        self.assertTrue(self._ablate(lambda o: o.pop("applicable_scope")))

    def test_removing_period_window_availability_is_caught(self):
        self.assertTrue(self._ablate(
            lambda o: o["applicable_scope"].pop("period_window_availability")))

    def test_removing_external_publish_permission_is_caught(self):
        self.assertTrue(self._ablate(lambda o: o.pop("external_publish_permission")))

    def test_removing_currently_usable_basis_is_caught(self):
        self.assertTrue(self._ablate(lambda o: o["usage_permission"].pop("currently_usable_basis")))

    def test_removing_evidence_digest_is_caught(self):
        self.assertTrue(self._ablate(lambda o: o.pop("evidence_digest")))

    def test_claiming_publishable_without_m2_saying_so_is_caught(self):
        def mutate(o):
            o["external_publish_permission"] = {"availability": "PRESENT", "value": True,
                                                "basis": "我说的"}
            o["usage_permission"]["usage_limits"] = None
        self.assertTrue(self._ablate(mutate))

    def test_derived_usable_must_match_m2_allowlist(self):
        def mutate(o):
            o["usage_permission"]["status"] = "unknown"
            o["usage_permission"]["currently_usable"] = True
            o["usage_permission"]["currently_usable_basis"] = "derived_from_status_allowlist"
        self.assertTrue(self._ablate(mutate))


@unittest.skipIf(Draft7Validator is None, "jsonschema 不可用")
class SchemaConformance(unittest.TestCase):
    def test_projection_validates_against_v11_schema(self):
        with open(SCHEMA_V11, encoding="utf-8") as h:
            schema = json.load(h)
        schema.pop("$schema", None)
        proj = _build(_load())
        errors = sorted(Draft7Validator(schema).iter_errors(proj), key=lambda e: list(e.path))
        self.assertEqual([], ["%s: %s" % (list(e.path), e.message) for e in errors])

    def test_v10_projection_still_validates_against_v10_schema(self):
        """不多算：v1.1 上线不使 v1.0 路径失效。"""
        with open(os.path.join(_INTERFACES, "M2_TO_M3_PROJECTION_v1.0.schema.json"),
                  encoding="utf-8") as h:
            schema = json.load(h)
        schema.pop("$schema", None)
        cap = _load()
        r = cap["reads"]
        m2 = {"current_cycle": r["cycles_current__full"],
              "active_overrides": r["campaign_overrides_active__full"],
              "latest_cycle_decision": r["cycle_decisions_latest__full"],
              "market_observations": r["market_observations"],
              "feedback": r["publish_instance_feedback"]}
        proj = P.build_projection(cap["workspace"]["id"], cap["account_full"]["id"], m2,
                                  requested={"primary_objective": "长期价值"},
                                  projection_id="test-v10",
                                  compiled_at=cap["capture_meta"]["frozen_now"])
        self.assertEqual(proj["schema_version"], "1.0")
        errors = sorted(Draft7Validator(schema).iter_errors(proj), key=lambda e: list(e.path))
        self.assertEqual([], ["%s: %s" % (list(e.path), e.message) for e in errors])


if __name__ == "__main__":
    unittest.main(verbosity=2)
