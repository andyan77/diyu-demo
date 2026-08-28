"""M3-AC-14 ①：内容任务的下游消费测试。

**这份测试的目的是量化一个已披露的合同冲突，不是绕过它。**

背景（第 1 轮已登记的缺口 B，本轮不修、不改 Brief）：

- 已被接受的〈共享合同二〉冻结了「持续运营决策」是 Content Brief 的**第一条合法上游**；
- 但仓库现行 `decision-chain/skills/Content_Brief_Architect_v0.1.md` §3.2 仍把
  「已被接受的上游 Campaign 决策」列为**阻塞项**，缺失即输出 `INPUT_INSUFFICIENT`；
- 改 Brief 属六份既有 Skill，本合同 `never_authorized_by_this_contract` 明确禁止。

所以本测试做的是**机械核对业务实质**：把 Brief §3.2 的五条阻塞项逐条对到 M3 内容任务
的承载字段上，得出"齐备／部分／缺失"，并把结论钉死。M3 侧能补的实质就补（本轮补了
`facts[].confirmed_by`）；补不了的（Campaign 决策包这个**类别**）如实留成缺口。

**判据不因结果而改**：下面的 `EXPECTED_COVERAGE` 是对现状的断言。任何一格发生变化——
Brief 正文被改、M3 补齐了字段、或缺口扩大——这份测试都会失败，强制重新判断，而不是
悄悄跟着变。Brief 的 SHA-256 一并钉住（A3：绑定变化即失效）。
"""

import hashlib
import json
import os
import sys
import unittest

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
_REPO = os.path.dirname(_ROOT)
_INTERFACES = os.path.join(_ROOT, "interfaces")
if _INTERFACES not in sys.path:
    sys.path.insert(0, _INTERFACES)

try:
    from jsonschema import Draft7Validator
except ImportError:  # pragma: no cover
    Draft7Validator = None

BRIEF_PATH = os.path.join(_REPO, "decision-chain", "skills", "Content_Brief_Architect_v0.1.md")
CONTENT_TASK_SCHEMA_PATH = os.path.join(_INTERFACES, "M3_CONTENT_TASK_v1.0.schema.json")

# 本测试的结论只对这一版 Brief 成立。Brief 一旦改动，本轮取证即 STALE。
BRIEF_SHA256 = "a0268a211a235b5b4df5e517f085db1f3b4948ae5add3346f2c15a426b63395f"

# Brief §3.2 的五条阻塞项（原文摘录，不转述）。
BRIEF_BLOCKING_ITEMS = (
    "已被接受的上游 Campaign 决策",
    "账号发布身份与责任边界",
    "内容数量与顺序结论",
    "至少一条本轮实际可用、可确认、可公开、可制作的事实链",
    "该事实链有明确的事实确认人，并具备完成最低内容单元的基本制作条件",
)

# 逐条核对结果。SUFFICIENT / PARTIAL / ABSENT 三态，"有但不够"独立成态
# （宪法动作 4：反查，不得把"有但不够"填成"有"）。
EXPECTED_COVERAGE = {
    "已被接受的上游 Campaign 决策": "ABSENT",
    "账号发布身份与责任边界": "SUFFICIENT",
    "内容数量与顺序结论": "PARTIAL",
    "至少一条本轮实际可用、可确认、可公开、可制作的事实链": "SUFFICIENT",
    "该事实链有明确的事实确认人，并具备完成最低内容单元的基本制作条件": "SUFFICIENT",
}


def _load(path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def _sha256(path):
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


# 一条生产条件充分的内容任务（AC-14 冻结输入①）。
READY_CONTENT_TASK = {
    "schema_version": "1.0",
    "result_kind": "content_task",
    "content_task": {
        "task_id": "ct-brief-001",
        "upstream_kind": "continuous_operation_decision",
        "cycle_role": {"value": "稳定兑现", "availability": "PRESENT", "note": None},
        "account": "acc-0001",
        "expression_subject": {"value": "门店主理人", "availability": "PRESENT", "note": None},
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
                "confirmed_by": "门店主理人（2026-08-20 当面确认）",
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


def _task():
    return READY_CONTENT_TASK["content_task"]


# --- 五条阻塞项各自的机械核对 ------------------------------------------------


def _check_upstream_campaign(task):
    """Brief §3.2 要的是「已被接受的上游 **Campaign** 决策」。

    M3 产出的上游是持续运营决策。业务实质（一个已被接受的、说明了为什么做的上游判断）
    存在，但**载体类别**不是 Campaign 决策包，而 Brief v0.1 §3.2 是按类别阻塞的。
    """

    if task.get("upstream_kind") == "campaign":
        return "SUFFICIENT"
    return "ABSENT"


def _check_account_identity(task):
    needed = ("account", "expression_subject", "permission", "explicit_non_promise",
              "non_sacrifice_conditions")
    if not all(task.get(k) for k in needed):
        return "ABSENT"
    if not task["permission"].get("risk_boundary"):
        return "PARTIAL"
    return "SUFFICIENT"


def _check_count_and_order(task):
    """单条内容任务带得动"本轮共几条、本条占其一"（capacity 说明），

    但**跨条顺序**属于 `candidate_kind = content_task_set` 那一层，单条载体表达不了。
    因此是 PARTIAL，不是 SUFFICIENT——"有但不够"必须独立成态。
    """

    note = (task.get("capacity") or {}).get("actual_capacity_note")
    if not note:
        return "ABSENT"
    has_role = bool((task.get("cycle_role") or {}).get("value"))
    return "PARTIAL" if has_role else "ABSENT"


def _check_fact_chain(task):
    facts = task.get("facts") or []
    if not facts:
        return "ABSENT"
    usable = [
        f for f in facts
        if f.get("statement") and f.get("source")
        and f.get("evidence_identity") not in (None, "unknown", "provisional_hypothesis")
    ]
    if not usable:
        return "ABSENT"
    # 可制作性由 capacity 承载；缺口显式写在 gaps 里而不是被吞掉。
    capacity = task.get("capacity") or {}
    if not capacity.get("critical_material_needs") and not capacity.get("timing"):
        return "PARTIAL"
    return "SUFFICIENT"


def _check_confirmer_and_min_conditions(task):
    facts = task.get("facts") or []
    confirmed = [f for f in facts if f.get("confirmed_by")]
    if not confirmed:
        return "ABSENT"
    capacity = task.get("capacity") or {}
    if not capacity.get("infeasible_if"):
        return "PARTIAL"
    return "SUFFICIENT"


CHECKERS = {
    "已被接受的上游 Campaign 决策": _check_upstream_campaign,
    "账号发布身份与责任边界": _check_account_identity,
    "内容数量与顺序结论": _check_count_and_order,
    "至少一条本轮实际可用、可确认、可公开、可制作的事实链": _check_fact_chain,
    "该事实链有明确的事实确认人，并具备完成最低内容单元的基本制作条件": _check_confirmer_and_min_conditions,
}


class BriefBinding(unittest.TestCase):
    def test_brief_is_unmodified_and_bound_by_hash(self):
        self.assertTrue(os.path.exists(BRIEF_PATH))
        self.assertEqual(
            BRIEF_SHA256,
            _sha256(BRIEF_PATH),
            "Content Brief Architect 已变化——本轮 AC-14 下游消费取证全部置 STALE，需定向复验",
        )

    def test_the_five_blocking_items_are_quoted_from_the_brief(self):
        """判据必须来自 Brief 原文，不能是我们对它的转述。"""

        with open(BRIEF_PATH, encoding="utf-8") as handle:
            text = handle.read()
        for item in BRIEF_BLOCKING_ITEMS:
            with self.subTest(item=item):
                self.assertIn(item, text, "§3.2 阻塞项原文对不上：%s" % item)


class DownstreamConsumption(unittest.TestCase):
    def test_ready_task_is_schema_valid(self):
        if Draft7Validator is None:
            self.skipTest("jsonschema 不可用")
        schema = _load(CONTENT_TASK_SCHEMA_PATH)
        self.assertEqual([], sorted(Draft7Validator(schema).iter_errors(READY_CONTENT_TASK),
                                    key=lambda e: list(e.path)))

    def test_coverage_matrix_matches_the_frozen_expectation(self):
        """五条逐项核对。任何一格变化都必须让这条测试失败。"""

        actual = {name: CHECKERS[name](_task()) for name in BRIEF_BLOCKING_ITEMS}
        self.assertEqual(
            EXPECTED_COVERAGE,
            actual,
            "Brief 消费覆盖矩阵变了——不得默认接受，须重新判断 AC-14",
        )

    def test_the_only_absent_item_is_the_disclosed_contract_conflict(self):
        """量化结论：五条里恰好一条 ABSENT，且就是已披露的那条。

        若将来出现第二条 ABSENT，说明 M3 侧真的漏了业务实质（那是 M3 的实现缺陷），
        必须与"合同冲突"分开处理——两者混为一谈就等于用一个已知冲突掩护新缺陷。
        """

        actual = {name: CHECKERS[name](_task()) for name in BRIEF_BLOCKING_ITEMS}
        absent = [k for k, v in actual.items() if v == "ABSENT"]
        self.assertEqual(["已被接受的上游 Campaign 决策"], absent)

    def test_upstream_kind_cannot_assert_an_acceptance_event(self):
        """最重要的一条负向判据。

        让内容任务通过 Brief §3.2 有一条捷径：把 `upstream_kind` 写成一个**自带
        "已被接受"含义**的值。那是伪造一个从未发生过的上游接受事件，比留着缺口
        严重得多——接受与否属于用户与 M2，不属于 M3（共享合同四 §二）。

        注意 `campaign` **是**合法枚举值：账号确实处在 Campaign overlay 下时，上游
        本来就是 Campaign。它不是伪造向量。真正不该存在的是
        `accepted_*` / `*_decision_package` 这类把"接受"编进标签的值。
        """

        schema = _load(CONTENT_TASK_SCHEMA_PATH)
        allowed = schema["definitions"]["content_task"]["properties"]["upstream_kind"].get("enum")
        self.assertIsNotNone(allowed, "upstream_kind 必须是 enum，否则可以随便写")
        self.assertIn("campaign", allowed, "Campaign 是八项能力之一，不能因为怕误用就删掉")
        for forged in ("accepted_campaign_decision", "campaign_decision_package",
                       "accepted_campaign", "approved_campaign"):
            with self.subTest(forged=forged):
                self.assertNotIn(forged, allowed)
        for value in allowed:
            with self.subTest(value=value):
                self.assertNotIn("accept", value)
                self.assertNotIn("approv", value)

    def test_relabelling_as_campaign_would_close_the_gap_which_is_why_it_needs_runtime_evidence(self):
        """把 `upstream_kind` 从持续运营决策改写成 `campaign`，五条阻塞项就全绿了。

        这正说明：schema 层挡不住"误标上游"。**在没有真实 Campaign 的情况下标成
        `campaign` 是伪造上游**，而能不能挡住它是运行时行为判据（EP-06），本轮
        `NOT_VERIFIED`。把这件事写成测试，是为了不让它被"结构检查已通过"掩盖。
        """

        relabelled = json.loads(json.dumps(_task()))
        relabelled["upstream_kind"] = "campaign"
        actual = {name: CHECKERS[name](relabelled) for name in BRIEF_BLOCKING_ITEMS}
        self.assertNotIn("ABSENT", actual.values())
        self.assertEqual("SUFFICIENT", actual["已被接受的上游 Campaign 决策"])

    def test_confirmed_by_is_required_so_a_missing_confirmer_stays_visible(self):
        """`confirmed_by` 是本轮为满足 Brief §3.2 第五条补的字段。

        它 required 且允许 null：拿不到确认人时必须显式写 null。省略这个键会让
        "没有确认人"和"忘了填"不可区分——而 Brief 正是按前者阻塞的。
        """

        if Draft7Validator is None:
            self.skipTest("jsonschema 不可用")
        schema = _load(CONTENT_TASK_SCHEMA_PATH)
        omitted = json.loads(json.dumps(READY_CONTENT_TASK))
        del omitted["content_task"]["facts"][0]["confirmed_by"]
        self.assertTrue(
            list(Draft7Validator(schema).iter_errors(omitted)),
            "省略 confirmed_by 竟然通过了校验",
        )

        explicit_null = json.loads(json.dumps(READY_CONTENT_TASK))
        explicit_null["content_task"]["facts"][0]["confirmed_by"] = None
        self.assertEqual(
            [], sorted(Draft7Validator(schema).iter_errors(explicit_null), key=lambda e: list(e.path)),
            "显式写 null 必须合法——那是'这条事实链没有确认人'的唯一诚实写法",
        )
        self.assertEqual("ABSENT", _check_confirmer_and_min_conditions(explicit_null["content_task"]))


class AblationOfNewField(unittest.TestCase):
    """A5：`confirmed_by` 删掉之后结果必须改变，否则它不成立。"""

    def test_removing_confirmed_by_changes_the_coverage_result(self):
        with_confirmer = _check_confirmer_and_min_conditions(_task())
        stripped = json.loads(json.dumps(_task()))
        for fact in stripped["facts"]:
            fact.pop("confirmed_by", None)
        without = _check_confirmer_and_min_conditions(stripped)
        self.assertNotEqual(with_confirmer, without)
        self.assertEqual("SUFFICIENT", with_confirmer)
        self.assertEqual("ABSENT", without)


if __name__ == "__main__":
    unittest.main(verbosity=2)
