"""用**运行中的 M2 实例的真实响应**跑投影契约。

与 `test_projection_contract.py` 的分工：那份用手工构造的样本证明"实现内部自洽"，
可离线跑；这份用 `account-operations/fixtures/m2_live_capture_v1.json`（由
`account-operations/tools/capture_m2_live_fixtures.py` 从真实 M2 抓取，未经手工编辑）
证明"我们对 M2 的形状假设与 M2 的实际行为一致"。

两者都需要。手工样本证明不了序列化层、Pydantic response_model、SQLAlchemy 类型往返
和 `null` 实际出现在哪些键上——而 M3-AC-12 的整条命题正建立在这些之上。

**证据等级与基线（逐条，不整包升级）**

实测：运行中的 `diyu-m2-app:dev` 与绑定基线 `main@df2c595` 有且只有两个文件不同——
`app/api/knowledge.py` 与 `app/models/knowledge.py`（M2 任务分支上尚未提交的
"市场观察权限语义"）。其余 `app/**.py` 与 `alembic/**` 逐字节相同。

因此：

- `LiveCycleContract` / `LiveDecisionContract` / `LiveCampaignOverlayContract` /
  `LiveFeedbackContract` / `LivePermissionContract` 打到的代码路径逐字节等同于绑定
  基线 ⇒ 这些条目的证据等级为 `runtime_verified @ main:df2c595`；
- `LiveMarketObservationContract` 打到的是**在途构建** ⇒ 证据等级为
  `runtime_verified @ diyu-m2-app:dev(在途)`，对绑定基线为 `STALE`，
  待 M2 那两个文件合入 main 后定向复验。不多算，也不少算。
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
except ImportError:  # pragma: no cover
    Draft7Validator = None

CAPTURE_PATH = os.path.join(_ROOT, "fixtures", "m2_live_capture_v1.json")
PROJECTION_SCHEMA_PATH = os.path.join(_INTERFACES, "M2_TO_M3_PROJECTION_v1.0.schema.json")


def _load(path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


CAPTURE = _load(CAPTURE_PATH) if os.path.exists(CAPTURE_PATH) else None


def _requested(**overrides):
    base = {
        "account_anchor": {"positioning": "城市通勤女装选购顾问", "provisional": True},
        "primary_objective": "吸粉",
        "secondary_objectives": ["GMV"],
        "priority_note": "吸粉优先；GMV 不得牺牲事实纪律",
        "non_sacrifice_conditions": ["不编造库存与价格"],
        "stage_evidence": {"history": "连续更新 6 周"},
        "expression_permission": "允许情境模拟；不允许站外导流",
        "cta_authorizations": [],
        "applicable_tracks": ["女装"],
        "gaps": [],
        "task_id": CAPTURE["capture_meta"]["task_id"] if CAPTURE else "unbound",
    }
    base.update(overrides)
    return base


def _project(account_key="full", m2_overrides=None, requested_overrides=None):
    """把真实抓取的读端点响应原样喂进投影编译器。"""

    reads = CAPTURE["reads"]
    suffix = "__%s" % account_key
    m2 = {
        "current_cycle": reads["cycles_current" + suffix],
        "active_overrides": reads["campaign_overrides_active" + suffix],
        "latest_cycle_decision": reads["cycle_decisions_latest" + suffix],
        "market_observations": reads["market_observations"],
        "feedback": reads["publish_instance_feedback"],
    }
    m2.update(m2_overrides or {})
    account = CAPTURE["account_%s" % account_key]
    return P.build_projection(
        CAPTURE["workspace"]["id"],
        account["id"],
        m2,
        requested=_requested(**(requested_overrides or {})),
        compiled_at=CAPTURE["capture_meta"]["frozen_now"],
    )


@unittest.skipIf(CAPTURE is None, "缺少真实抓取夹具，先跑 tools/capture_m2_live_fixtures.py")
class LiveCaptureIntegrity(unittest.TestCase):
    """先证明夹具本身是真的、且知道自己绑定在哪个构建上。"""

    def test_capture_declares_its_baseline_divergence(self):
        div = CAPTURE["capture_meta"]["baseline_divergence"]
        self.assertEqual("business-persistence@main:df2c595", div["bound_baseline"])
        self.assertEqual(
            ["app/api/knowledge.py", "app/models/knowledge.py"],
            sorted(div["files_differing"]),
            "抓取夹具必须自带基线差异声明——不声明就等于默认它是基线，那是伪造绑定",
        )

    def test_capture_contains_no_smuggled_error_bodies(self):
        """静默失败伪装成证据是取证脚本最危险的失效模式。

        第一版抓取脚本没有状态码检查，一条被 M2 以 422 拒绝的 `register_feedback`
        把错误体 `{"detail": ...}` 原样写进了夹具，形状上和一条成功记录并无二致。
        这条测试是那次事故的回归。
        """

        for key in ("feedback_create_responses", "market_observation_create_responses"):
            for i, row in enumerate(CAPTURE[key]):
                payload = row.get("response", row)
                with self.subTest(key=key, i=i):
                    self.assertNotIn(
                        "detail",
                        payload,
                        "%s[%d] 是一个错误体，不是被创建的记录" % (key, i),
                    )
                    self.assertIn("id", payload)

    def test_ids_are_real_uuids_not_handwritten_placeholders(self):
        import uuid

        for key in ("workspace", "account_full", "account_sparse", "publish_instance"):
            with self.subTest(key=key):
                uuid.UUID(CAPTURE[key]["id"])


@unittest.skipIf(CAPTURE is None, "缺少真实抓取夹具")
class LiveProjectionShape(unittest.TestCase):
    """证据等级：`runtime_verified @ main:df2c595`（周期族代码与基线逐字节相同）。"""

    def test_real_response_projects_and_validates(self):
        proj = _project("full")
        self.assertEqual([], P.validate_projection(proj))
        if Draft7Validator is not None:
            self.assertEqual(
                [], sorted(Draft7Validator(_load(PROJECTION_SCHEMA_PATH)).iter_errors(proj),
                           key=lambda e: list(e.path))
            )

    def test_real_capacities_are_floats_not_ints(self):
        """真实响应把三类产能返回成 `2.0/10.0/21.0`，手工样本写的是 `2/10/21`。

        这正是手工样本证明不了的那一层：M2 的列类型经 SQLAlchemy/Pydantic 往返
        之后是 float。schema 若把它们写成 `integer` 就会在真实数据上炸——而离线
        测试永远不会发现。
        """

        cycle = CAPTURE["reads"]["cycles_current__full"]
        for key in ("baseline_capacity", "actual_capacity", "expected_publish_count"):
            with self.subTest(key=key):
                self.assertIsInstance(cycle[key], float)

        capacity = _project("full")["capacity"]
        self.assertEqual(21.0, capacity["expected_publish_count"]["value"])
        self.assertEqual(10.0, capacity["baseline_capacity"]["value"])
        self.assertEqual(2.0, capacity["actual_capacity"]["value"])

    def test_each_capacity_keeps_its_own_source(self):
        capacity = _project("full")["capacity"]
        self.assertEqual("用户本轮要求", capacity["expected_publish_count"]["source_ref"])
        self.assertEqual("团队自述", capacity["baseline_capacity"]["source_ref"])
        self.assertEqual("本周排班", capacity["actual_capacity"]["source_ref"])

    def test_m2_internal_keys_never_reach_the_projection(self):
        """本轮由真实响应抓出的**过量读取**缺陷的回归。

        修复前：`current_cycle` / `latest_cycle_decision` 把 M2 的整行原样塞进
        `value`，于是 `row_version`（并发控制）与 `idempotency_key`（去重）一起被
        投给了模型。手工样本永远抓不到这个——因为手工样本里根本没有这两个键。
        """

        cycle = CAPTURE["reads"]["cycles_current__full"]
        self.assertIn("row_version", cycle, "真实响应确实带着这些 M2 内部键")
        self.assertIn("idempotency_key", cycle)

        blob = json.dumps(_project("full"), ensure_ascii=False)
        for leaked in ("row_version", "idempotency_key"):
            with self.subTest(key=leaked):
                self.assertNotIn(leaked, blob)

    def test_capacity_is_not_duplicated_inside_the_cycle_summary(self):
        """同一事实在同一份投影里出现两次 = 两个真源。

        产能已经在 `capacity` 里逐个带着来源与可用状态。周期摘要若**同时**带着
        赤裸的数字，那么把 `capacity.actual_capacity` 标成"用户拒绝提供"之后，
        模型仍然能从周期摘要里读到那个数字——防坍缩机制当场失效。
        """

        proj = _project(
            "full",
            requested_overrides={"declared_absences": {"capacity.actual_capacity": P.REFUSED}},
        )
        self.assertEqual(P.REFUSED, proj["capacity"]["actual_capacity"]["availability"])
        summary = proj["current_cycle"]["value"]
        for key in ("actual_capacity", "baseline_capacity", "expected_publish_count"):
            with self.subTest(key=key):
                self.assertNotIn(key, summary)
        self.assertNotIn("2.0", json.dumps(summary, ensure_ascii=False))

    def test_cycle_summary_keeps_the_identity_fields_it_needs(self):
        summary = _project("full")["current_cycle"]["value"]
        self.assertEqual(CAPTURE["reads"]["cycles_current__full"]["id"], summary["cycle_id"])
        self.assertTrue(summary["is_current"])
        self.assertEqual("2026-08-01T00:00:00+00:00", summary["start_at"])


@unittest.skipIf(CAPTURE is None, "缺少真实抓取夹具")
class LiveAntiCollapse(unittest.TestCase):
    """M3-AC-12 反证探针，用**真实的** M2 `null` 而不是我们自己填的 `None`。"""

    def test_m2_really_returns_null_for_unrecorded_capacity(self):
        sparse = CAPTURE["reads"]["cycles_current__sparse"]
        self.assertIsNone(sparse["actual_capacity"])
        self.assertIsNone(sparse["actual_capacity_source"])
        self.assertIsNone(sparse["baseline_capacity"])
        self.assertEqual(21.0, sparse["expected_publish_count"])

    def test_real_null_degrades_to_unknown_never_refused(self):
        capacity = _project("sparse")["capacity"]
        self.assertEqual(P.UNKNOWN, capacity["actual_capacity"]["availability"])
        self.assertEqual(P.UNKNOWN, capacity["baseline_capacity"]["availability"])
        self.assertEqual(P.PRESENT, capacity["expected_publish_count"]["availability"])

    def test_refused_and_unknown_stay_distinguishable_on_real_data(self):
        """M2 的表结构装不下"用户拒绝提供产能"。

        所以这个区分只能由任务快照侧带进来，且必须与"M2 返回了 null"两两不等——
        否则"我们不知道"和"用户不肯说"在下游就是同一句话。
        """

        unknown = _project("sparse")["capacity"]["actual_capacity"]
        refused = _project(
            "sparse",
            requested_overrides={"declared_absences": {"capacity.actual_capacity": P.REFUSED}},
        )["capacity"]["actual_capacity"]
        self.assertEqual(P.UNKNOWN, unknown["availability"])
        self.assertEqual(P.REFUSED, refused["availability"])
        self.assertIsNone(refused["value"])

    def test_real_none_recorded_is_unknown_not_kept_unchanged(self):
        """`none_recorded` 是 M2 的真实返回，不是我们假设的形状。"""

        self.assertEqual(
            {"decision": "none_recorded"}, CAPTURE["reads"]["cycle_decisions_latest__sparse"]
        )
        self.assertEqual(P.UNKNOWN, _project("sparse")["latest_cycle_decision"]["availability"])

        held = _project("full")["latest_cycle_decision"]
        self.assertEqual(P.PRESENT, held["availability"])
        self.assertEqual("kept_unchanged", held["value"]["decision"])


@unittest.skipIf(CAPTURE is None, "缺少真实抓取夹具")
class LiveCampaignOverlay(unittest.TestCase):
    def test_only_named_positions_are_covered(self):
        overlay = _project("full")["campaign_overlays"][0]
        self.assertEqual(["slot-2", "slot-5"], overlay["targeted_positions"])
        self.assertEqual("active", overlay["status"])

    def test_account_without_campaign_gets_empty_not_missing(self):
        """空列表和"没查过"必须不同形。真实响应给的是 `[]`。"""

        self.assertEqual([], CAPTURE["reads"]["campaign_overrides_active__sparse"])
        self.assertEqual([], _project("sparse")["campaign_overlays"])


@unittest.skipIf(CAPTURE is None, "缺少真实抓取夹具")
class LiveFeedbackContract(unittest.TestCase):
    def test_evidence_identity_survives_projection(self):
        item = _project("full")["feedback"][0]
        self.assertFalse(item["is_simulated"])
        self.assertFalse(item["is_test"])
        self.assertFalse(item["is_pre_publish_review"])
        self.assertEqual("publish_instance", item["bound_to"]["binding_kind"])
        self.assertEqual("平台后台", item["source"])

    def test_closed_observation_window_is_computed_from_real_timestamps(self):
        item = _project("full")["feedback"][0]
        self.assertTrue(item["window_closed"])

    def test_m2_rejects_prepublish_review_bound_to_publish_instance(self):
        """真实的 422，不是我们编的错误码。

        证据层级边界由 M2 在写入时强制：`is_pre_publish_review` 必须与
        `content_version_id` 同真同假。这让"这条证据来自真实发布之后"无法被伪装。
        """

        rejected = CAPTURE["rejected__prepublish_bound_to_publish_instance"]
        self.assertEqual(422, rejected["status_code"])
        self.assertIn("is_pre_publish_review", rejected["body"]["detail"])

        both = CAPTURE["rejected__feedback_bound_to_both"]
        self.assertEqual(422, both["status_code"])
        self.assertIn("exactly one", both["body"]["detail"])

    def test_prepublish_review_is_created_but_unreachable_via_any_m2_read(self):
        """**已登记的 M2 读侧缺口**（本轮新发现，不在本任务内修 M2）。

        发布前评审记录挂在 `content_version_id` 上、`publish_instance_id` 为 null；
        而 M2 唯一的反馈读端点是 `GET /publish-instances/{id}/feedback`，它按
        `publish_instance_id` 过滤。因此发布前评审**写得进去、读不出来**。

        对 M3 的后果（必须如实承载，不得假装能读到）：投影的 `feedback[]` 经 M2 读
        端点永远不含发布前评审；该类证据只能由任务快照侧带入。`_project_feedback`
        里的 `content_version` 分支因此在当前 M2 读侧不可达。
        """

        created = {f["idempotency_key"]: f for f in CAPTURE["feedback_create_responses"]}
        review = created["m3-acco-001:fb-prepublish"]
        self.assertTrue(review["is_pre_publish_review"])
        self.assertIsNotNone(review["content_version_id"])
        self.assertIsNone(review["publish_instance_id"])

        readable = CAPTURE["reads"]["publish_instance_feedback"]
        self.assertEqual(1, len(readable), "M2 读端点若开始返回发布前评审，本条需重判")
        self.assertNotIn(review["id"], [r["id"] for r in readable])


@unittest.skipIf(CAPTURE is None, "缺少真实抓取夹具")
class LivePermissionContract(unittest.TestCase):
    """权限不足与未认证是两件事，真实响应也确实用两个状态码区分。"""

    def test_non_member_and_missing_actor_are_different_failures(self):
        denied = CAPTURE["permission_denied"]
        missing = CAPTURE["missing_actor_header"]
        self.assertEqual(403, denied["status_code"])
        self.assertEqual(401, missing["status_code"])
        self.assertNotEqual(denied["body"]["detail"], missing["body"]["detail"])

    def test_permission_failure_is_never_projected_as_data(self):
        """403 的响应体是 `{"detail": ...}`。

        把它当成周期喂进投影，必须炸——不能让"没权限看"被静默投影成"周期是空的"。
        """

        proj = P.build_projection(
            CAPTURE["workspace"]["id"],
            CAPTURE["account_full"]["id"],
            {"current_cycle": CAPTURE["permission_denied"]["body"]},
            requested=_requested(),
            compiled_at=CAPTURE["capture_meta"]["frozen_now"],
        )
        capacity = proj["capacity"]
        for key in ("expected_publish_count", "baseline_capacity", "actual_capacity"):
            with self.subTest(key=key):
                self.assertEqual(
                    P.UNKNOWN,
                    capacity[key]["availability"],
                    "权限失败被投影成了一个具体的产能数字",
                )


@unittest.skipIf(CAPTURE is None, "缺少真实抓取夹具")
class LiveMarketObservationContract(unittest.TestCase):
    """证据等级：`runtime_verified @ diyu-m2-app:dev(在途)`；对绑定基线为 `STALE`。

    这一族打到的 `app/api/knowledge.py` 与 `app/models/knowledge.py` 是 M2 任务分支上
    尚未提交的改动。合入 main 后需定向复验 AC-09 / AC-12 的市场观察半。
    """

    def test_running_build_really_exposes_permission_fields(self):
        """注意两个端点的形状**不同**，这本身是实测结论：

        创建响应只有 `permission_status`；`currently_usable` / `excluded_reason`
        是**列表端点**才计算的派生位。投影读的是列表端点，所以判据也钉在列表端点上。
        """

        created = CAPTURE["market_observation_create_responses"][0]["response"]
        self.assertEqual("unknown", created["permission_status"])
        self.assertNotIn("currently_usable", created)

        listed = {r["idempotency_key"]: r for r in CAPTURE["reads"]["market_observations"]}
        row = listed["m3-acco-001:obs-current"]
        self.assertEqual("unknown", row["permission_status"])
        self.assertFalse(row["currently_usable"])
        self.assertEqual("permission_unknown", row["excluded_reason"])

    def test_permission_unconfirmed_observation_is_not_usable_for_inference(self):
        """本轮由真实响应抓出的实现缺陷的回归。

        修复前：投影把一条 M2 明确判定 `currently_usable=false /
        permission_unknown` 的观察标成 `availability=PRESENT`，下游无从知道它不能用。
        授权未确认的来源被当成可引用证据，是 M3-AC-09/AC-12 的直接 FAIL。
        """

        for obs in _project("full")["market_observations"]:
            with self.subTest(obs=obs["observation_id"]):
                self.assertFalse(
                    obs["usable_for_inference"],
                    "M2 说当前不可用，投影却放行了",
                )
                self.assertEqual("unknown", obs["usage_permission"]["status"])
                self.assertEqual("permission_unknown", obs["usage_permission"]["excluded_reason"])

    def test_expired_observation_is_kept_and_marked_not_dropped(self):
        obs = {o["observation_id"]: o for o in _project("full")["market_observations"]}
        stale = [o for o in obs.values() if o["availability"] == P.EXPIRED]
        self.assertTrue(stale, "过期观察被丢弃了——'证据已过期'这件事因此不可见")
        self.assertFalse(stale[0]["usable_for_inference"])

    def test_off_track_observation_is_not_projected(self):
        projected = {o["applicable_track"] for o in _project("full")["market_observations"]}
        self.assertNotIn("母婴", projected, "最小必要投影不得带上无关赛道")

    def test_m2_current_endpoint_agrees_that_nothing_is_usable(self):
        """交叉核对：M2 自己的权限感知端点也判定当前无可用观察。

        两个独立来源给出同一结论，说明 M3 的保守判断不是自己发明的。
        """

        current = CAPTURE["reads"]["market_observations__current_track"]
        self.assertFalse(current["available"])
        self.assertEqual("all_observations_excluded", current["gap_reason"])
        self.assertEqual([], current["observations"])

    def test_baseline_shaped_row_degrades_to_pre_permission_behaviour(self):
        """绑定基线 `main@df2c595` 的市场观察**没有**权限字段。

        去掉那三个键后，投影必须退化成加入权限维度之前的行为——否则本次改动就不是
        向后兼容的，而是把一个 M2 尚未表达的判断强加给了基线。
        """

        rows = []
        for row in CAPTURE["reads"]["market_observations"]:
            trimmed = {k: v for k, v in row.items()
                       if k not in ("permission_status", "currently_usable",
                                    "excluded_reason", "usage_limits")}
            rows.append(trimmed)

        proj = _project("full", m2_overrides={"market_observations": rows})
        self.assertEqual([], P.validate_projection(proj))
        by_avail = {o["availability"]: o for o in proj["market_observations"]}
        self.assertIn(P.PRESENT, by_avail, "基线形状下未过期观察应恢复为可用")
        self.assertTrue(by_avail[P.PRESENT]["usable_for_inference"])
        self.assertIsNone(by_avail[P.PRESENT]["usage_permission"]["status"])
        self.assertIsNone(by_avail[P.PRESENT]["usage_permission"]["currently_usable"])
        # 过期仍然独立于权限成立
        self.assertFalse(by_avail[P.EXPIRED]["usable_for_inference"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
