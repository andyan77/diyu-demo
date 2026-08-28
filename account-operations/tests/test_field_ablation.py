"""M3-AC-12 ③：投影的**全字段**消融门（A5 消融律）。

冻结判据原文：「字段消融——删除任一投影字段后至少一条测试失败，否则该字段不成立」，
不足条款：「③中有字段删除后无测试失败 → 该字段须删除或合并，否则 `FAIL`」。

第 1 轮只机械遍历了**必填顶层字段**（11 个）。那是这条判据的一个真子集：嵌套字段、
数组元素字段、以及五个正交维度键当时全部没被覆盖。本轮按判据原文重跑全字段：

    首次全量运行：141 条字段路径，**53 条**删除后无任何检查失败。

53 条里绝大多数是同一个结构性原因：五个正交维度（`info_nature` / `provenance` /
`confirmation` / `scope` / `as_of` / `source_ref`）在 schema 里全是可选键，而
`field()` 又把值为 None 的维度直接省略——于是它们既不必填、又经常不存在，删掉当然
不会有任何检查失败。**它们在结构上没有挣到自己的存在。**

处置（不是放宽判据，是补齐结构）：

1. `field()` 区分「没传这个维度」与「传了 None」，后者保留成 `null`；
2. 新增 `MANDATORY_DIMENSIONS` / `MANDATORY_LIST_DIMENSIONS`：按站点声明哪些维度必须
   在场（一律必填是错的——`source_ref` 对 `objectives.primary` 没有意义）；
3. 不可用状态下不再挂 `as_of` / `source_ref`（一个「不知道」的产能没有来源可言）；
4. schema 收紧 `binding.task_id`、`feedback_item`、`market_observation_item`、
   campaign overlay 的 required。

    收敛后：**6 条**，全部落在**刻意不冻结**的自由载荷内部。

自由载荷是明确的设计决定而非疏漏：`feedback.payload`、`based_on`、`scope_ref` 由 M2
原样存储、不评判；`account_anchor.value` / `stage_evidence.value` 由任务快照侧供给。
把它们的内部结构冻死，等于替 M2 和用户决定他们能记录什么。

**判据没有被改，边界被写清楚了**：AC-12 ③ 的"投影字段"指投影自身的字段，
`payload` 是一个投影字段，`payload.views` 是被投影的内容。下面的
`FREEFORM_CONTAINERS` 把这条边界钉死——任何**新**的未挣到存在的字段都会让测试失败。
"""

import copy
import json
import os
import sys
import unittest

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
_INTERFACES = os.path.join(_ROOT, "interfaces")
for _path in (_INTERFACES, _HERE):
    if _path not in sys.path:
        sys.path.insert(0, _path)

import projection as P  # noqa: E402
import test_live_m2_contract as LIVE  # noqa: E402

try:
    from jsonschema import Draft7Validator
except ImportError:  # pragma: no cover
    Draft7Validator = None

PROJECTION_SCHEMA_PATH = os.path.join(_INTERFACES, "M2_TO_M3_PROJECTION_v1.0.schema.json")

# 刻意不冻结内部结构的自由载荷。键是"容器"的点路径前缀。
FREEFORM_CONTAINERS = (
    "account_anchor.value",
    "stage_evidence.value",
    "latest_cycle_decision.value.based_on",
    "feedback.payload",
    "market_observations.scope_ref",
)


def _load(path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def _iter_paths(node, prefix=()):
    if isinstance(node, dict):
        for key, value in node.items():
            yield prefix + (key,)
            for item in _iter_paths(value, prefix + (key,)):
                yield item
    elif isinstance(node, list):
        # 数组只取代表元素：同构元素重复遍历只是把同一条结论数一遍。
        for value in node[:1]:
            for item in _iter_paths(value, prefix + (0,)):
                yield item


def _delete(obj, path):
    cursor = obj
    for part in path[:-1]:
        cursor = cursor[part]
    if isinstance(cursor, list):
        cursor.pop(path[-1])
    else:
        del cursor[path[-1]]


def _normalise(path):
    """把数组下标抹掉，好和 FREEFORM_CONTAINERS 前缀比对。"""

    return ".".join(str(p) for p in path if not isinstance(p, int))


def _inside_freeform(path):
    dotted = _normalise(path)
    for container in FREEFORM_CONTAINERS:
        if dotted.startswith(container + "."):
            return True
    return False


def _survivors(projection, schema):
    """返回删除后**没有**任何检查失败的字段路径。"""

    validator = Draft7Validator(schema)
    out = []
    for path in list(_iter_paths(projection)):
        mutated = copy.deepcopy(projection)
        try:
            _delete(mutated, path)
        except (KeyError, IndexError, TypeError):
            continue
        if not list(validator.iter_errors(mutated)) and not P.validate_projection(mutated):
            out.append(path)
    return out


@unittest.skipIf(LIVE.CAPTURE is None, "缺少真实抓取夹具")
@unittest.skipIf(Draft7Validator is None, "jsonschema 不可用")
class FullFieldAblation(unittest.TestCase):
    """在**真实 M2 响应**投影出的两个形态上跑，而不是在手工样本上。"""

    def test_every_projection_field_earns_its_existence(self):
        schema = _load(PROJECTION_SCHEMA_PATH)
        for account_key in ("full", "sparse"):
            with self.subTest(account=account_key):
                projection = LIVE._project(account_key)
                unearned = [
                    _normalise(p) for p in _survivors(projection, schema) if not _inside_freeform(p)
                ]
                self.assertEqual(
                    [],
                    unearned,
                    "这些字段删掉之后没有任何检查失败——按 M3-AC-12 ③ 必须删除或合并，"
                    "或者补一条真正会失败的检查：%s" % unearned,
                )

    def test_the_gate_actually_covers_the_whole_tree_not_just_top_level(self):
        """守卫：防止这条门退化回第 1 轮那种"只查顶层必填"的假覆盖。"""

        projection = LIVE._project("full")
        paths = list(_iter_paths(projection))
        self.assertGreater(len(paths), 100, "字段路径数骤降，说明遍历没有真的走进嵌套结构")
        depths = [len(p) for p in paths]
        self.assertGreaterEqual(max(depths), 4, "没有遍历到足够深的嵌套字段")

    def test_freeform_containers_are_the_only_exemption_and_they_really_are_freeform(self):
        """豁免必须有据：这些容器在 schema 里确实是未约束内部结构的 object。"""

        schema = _load(PROJECTION_SCHEMA_PATH)
        definitions = schema["definitions"]
        self.assertEqual({"type": "object"}, definitions["feedback_item"]["properties"]["payload"])
        self.assertEqual(
            {"type": "object"},
            definitions["market_observation_item"]["properties"]["scope_ref"],
        )
        self.assertEqual(
            {"type": "object"}, definitions["decision_summary"]["properties"]["based_on"]
        )

    def test_removing_a_mandatory_dimension_is_caught(self):
        """正向反证：维度键不是装饰位，删掉必须被抓到。

        没有这条，`MANDATORY_DIMENSIONS` 本身就可能是一张写了但从不生效的表。
        """

        for dotted, dimensions in P.MANDATORY_DIMENSIONS.items():
            for dimension in dimensions:
                with self.subTest(path=dotted, dimension=dimension):
                    projection = LIVE._project("full")
                    envelope = P._dig(projection, dotted)
                    if not isinstance(envelope, dict) or dimension not in envelope:
                        continue
                    del envelope[dimension]
                    self.assertTrue(
                        P.validate_projection(projection),
                        "%s 删掉维度 %s 之后竟然仍然通过" % (dotted, dimension),
                    )

    def test_unavailable_envelope_does_not_carry_decorative_source_keys(self):
        """一个 UNKNOWN 的产能不该挂着永远为 null 的 `source_ref`。

        挂着它，删掉不会有任何检查失败——那就是一个没挣到存在的装饰位。
        """

        capacity = LIVE._project("sparse")["capacity"]
        self.assertEqual(P.UNKNOWN, capacity["actual_capacity"]["availability"])
        self.assertNotIn("source_ref", capacity["actual_capacity"])
        # 而 PRESENT 的那个必须带着来源
        self.assertIn("source_ref", capacity["expected_publish_count"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
