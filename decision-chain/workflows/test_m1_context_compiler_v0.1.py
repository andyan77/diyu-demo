"""
M1 任务上下文编译器 · 正式单元测试
task_id: DIYU-V1-M1-NATURAL-CONTEXT-001

用途：把 decision-chain/evidence/V1_M1_CANDIDATE_RUN_001.md 之前口头验证过的场景
（及后续新增场景）固化成可重复运行的测试文件，补齐 L3 记录标出的已知缺口
（"本地单测...非独立正式测试文件"）。

运行方式（无第三方依赖，纯 stdlib）：
    python3 decision-chain/workflows/test_m1_context_compiler_v0.1.py -v

被测源文件名含版本号（m1_context_compiler_v0.1.py），非法 Python 模块标识符，
故用 importlib.util 按路径加载，而非 import 语句。
"""

import importlib.util
import json
import os
import unittest

_HERE = os.path.dirname(os.path.abspath(__file__))
_MODULE_PATH = os.path.join(_HERE, "m1_context_compiler_v0.1.py")

_spec = importlib.util.spec_from_file_location("m1_context_compiler_v0_1", _MODULE_PATH)
compiler = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(compiler)


def _run(snapshot_json, shadow_patch, user_query="（测试输入，内容不影响编译器判定）"):
    return compiler.main(user_query, snapshot_json, shadow_patch)


class TestFreshTurnBasics(unittest.TestCase):
    """对应 RUN-001：空快照 + 任务陈述 + 点名能力。"""

    def setUp(self):
        self.patch = {
            "route_intent": "FOCUS",
            "current_task_text": "我想为账号规划一下长期人设和分工",
            "temporal_scope": "LONG_TERM",
            "requested_capability": "MATRIX",
        }
        self.result = _run(None, self.patch)

    def test_patch_accepted(self):
        self.assertEqual(self.result["patch_ok"], "true")
        self.assertEqual(self.result["reject_reason"], "")

    def test_snapshot_captures_task_text_verbatim(self):
        snap = json.loads(self.result["snapshot_json"])
        self.assertEqual(snap["current_task"]["text"], self.patch["current_task_text"])
        self.assertEqual(snap["current_task"]["temporal_scope"], "LONG_TERM")

    def test_revision_increments_on_real_change(self):
        snap = json.loads(self.result["snapshot_json"])
        self.assertEqual(snap["revision"], 1)
        self.assertEqual(self.result["state_changed"], "true")

    def test_call_intent_needs_requested_capability(self):
        intent = json.loads(self.result["call_intent_json"])
        self.assertEqual(intent["needed_capabilities"], ["MATRIX"])

    def test_matrix_degraded_input_not_fabricated_satisfied(self):
        """六类必需输入只满足了任务文本，必须如实标 DEGRADED_INPUT，不得标为可直接进入。"""
        intent = json.loads(self.result["call_intent_json"])
        matrix = intent["per_capability"]["MATRIX"]
        self.assertEqual(matrix["status"], "DEGRADED_INPUT")
        self.assertTrue(matrix["reachable_if_requested"])
        self.assertIsNone(matrix["block_reason"])


class TestWholePatchRejection(unittest.TestCase):
    """未知字段必须整体拒绝，不得局部采纳（防止把用户没说的内容悄悄写成已确认）。"""

    def test_unknown_field_rejects_whole_patch(self):
        empty_snapshot = json.dumps(compiler._default_snapshot(), ensure_ascii=False)
        patch = {
            "current_task_text": "这段文本不应该被写入",
            "made_up_field": "不存在的字段",
        }
        result = _run(empty_snapshot, patch)
        self.assertEqual(result["patch_ok"], "false")
        self.assertIn("PATCH_UNKNOWN_FIELDS", result["reject_reason"])
        self.assertIn("made_up_field", result["reject_reason"])

        snap = json.loads(result["snapshot_json"])
        self.assertIsNone(snap["current_task"]["text"], "被拒绝的 patch 内容不得泄漏进快照")
        self.assertEqual(result["state_changed"], "false")

    def test_illegal_enum_rejects_whole_patch(self):
        patch = {"temporal_scope": "SOMEDAY_MAYBE_NOT_A_REAL_VALUE"}
        result = _run(None, patch)
        self.assertEqual(result["patch_ok"], "false")
        self.assertTrue(result["reject_reason"].startswith("ILLEGAL_ENUM:temporal_scope"))

    def test_patch_not_object_rejected(self):
        result = _run(None, "这不是一个 dict，是字符串")
        self.assertEqual(result["patch_ok"], "false")
        self.assertEqual(result["reject_reason"], "PATCH_NOT_OBJECT")


class TestSideQuestionCapture(unittest.TestCase):
    """侧问必须被捕获为 open_threads，且不得被当场回答掉（对应 RUN-002/RUN-003 场景背景）。"""

    def test_side_question_becomes_open_thread(self):
        """_merge_patch 落库时线程状态是 OPEN；但 main() 单次调用内 _dialogue_directive
        紧接着在同一轮把它标 SURFACED 再序列化输出（因为同一轮 directive 已经把线程文本带给了
        对话 LLM）——这是当前代码的真实行为，不是本测试断言错误。真正的"仍为 OPEN"状态只在
        同一轮内、且它不是本轮唯一/最早的 open 线程时才会被观察到，见
        test_second_open_thread_in_same_turn_stays_open。"""
        patch = {
            "current_task_text": "主要是做女装穿搭内容",
            "side_question": "如果不做剧情类的内容会不会不好起量？",
        }
        result = _run(None, patch)
        snap = json.loads(result["snapshot_json"])
        self.assertEqual(len(snap["open_threads"]), 1)
        thread = snap["open_threads"][0]
        self.assertEqual(thread["id"], "thread_001")
        self.assertEqual(thread["status"], "SURFACED")
        self.assertEqual(thread["text"], patch["side_question"])

    def test_new_thread_each_turn_gets_surfaced_same_turn_real_finding(self):
        """真实发现（非测试书写错误）：PATCH_KEYS 每轮只支持一个 side_question，
        新线程诞生时永远是本轮唯一的 OPEN 线程，会在同一次 main() 调用内被
        _dialogue_directive 立刻标 SURFACED 再序列化输出。结果是"先记录、留到下一轮
        才主动提"这个设计意图目前从未在持久化快照里被观察到——两轮各自的线程最终都是
        SURFACED，不存在跨轮仍为 OPEN 的情形。是否要改成"确认对话 LLM 真的说出口了才转
        SURFACED"或"至少跨一轮再表面化"，是设计判断，不在本次测试形式化范围内擅自改动，
        如实记录为已知限制（另见 evidence/V1_M1_CANDIDATE_RUN_001.md 已知限制章节）。"""
        turn1 = _run(None, {"side_question": "第一个追问"})
        turn2 = _run(turn1["snapshot_json"], {"side_question": "第二个追问"})
        snap2 = json.loads(turn2["snapshot_json"])
        self.assertEqual(snap2["open_threads"][0]["status"], "SURFACED")
        self.assertEqual(snap2["open_threads"][1]["status"], "SURFACED")

    def test_dialogue_directive_surfaces_open_thread_without_answering_it(self):
        patch = {"side_question": "会不会不好起量？"}
        result = _run(None, patch)
        self.assertIn("会不会不好起量", result["dialogue_directive"])
        snap = json.loads(result["snapshot_json"])
        self.assertEqual(snap["open_threads"][0]["status"], "SURFACED",
                          "directive 生成后线程应转为 SURFACED，而不是仍标 OPEN 或被直接判定为 HANDLED")


class TestNoEntryCapabilitiesHonestBlocking(unittest.TestCase):
    """CAP-03 / CAP-05 当前无物理入口，必须如实标 BLOCKED，不得伪造入口。"""

    def test_single_account_operation_blocked(self):
        result = _run(None, {"current_task_text": "帮我做单账号持续运营"})
        intent = json.loads(result["call_intent_json"])
        cap = intent["per_capability"]["SINGLE_ACCOUNT_OPERATION"]
        self.assertEqual(cap["status"], "BLOCKED")
        self.assertEqual(cap["block_reason"], "NO_PHYSICAL_ENTRY_YET")
        self.assertFalse(cap["reachable_if_requested"])

    def test_creative_tournament_blocked(self):
        result = _run(None, {"current_task_text": "来一场创意锦标赛"})
        intent = json.loads(result["call_intent_json"])
        cap = intent["per_capability"]["CREATIVE_TOURNAMENT"]
        self.assertEqual(cap["status"], "BLOCKED")
        self.assertEqual(cap["block_reason"], "NO_PHYSICAL_ENTRY_YET")


class TestKnownLimitationAnnotation(unittest.TestCase):
    """CAMPAIGN / CONTENT_BRIEF 必须携带既有线性锁未被绕过的说明；其余能力不得携带同一条说明
    （不得把不适用的免责话术泛化到所有能力上）。"""

    def test_campaign_and_content_brief_carry_lock_limitation(self):
        result = _run(None, {"current_task_text": "占位任务，仅用于触发 call_intent 计算"})
        intent = json.loads(result["call_intent_json"])
        for cap_id in ("CAMPAIGN", "CONTENT_BRIEF"):
            self.assertIsNotNone(intent["per_capability"][cap_id]["known_limitation"])

    def test_matrix_and_others_do_not_carry_lock_limitation(self):
        result = _run(None, {"current_task_text": "占位任务，仅用于触发 call_intent 计算"})
        intent = json.loads(result["call_intent_json"])
        for cap_id in ("MATRIX", "CREATIVE_SCRIPT", "PRODUCTION_DIRECTOR", "PUBLISHING_PACKAGING"):
            self.assertIsNone(intent["per_capability"][cap_id]["known_limitation"])


class TestDialogueDirectiveNoRawCodeLeak(unittest.TestCase):
    """真实发现（CE-A2 真实运行）：dialogue_directive 曾把内部枚举代码（如 "MATRIX"）原样
    拼进给对话 LLM 的指令文本，对话 LLM 系统提示词禁止"出现 Prompt 内部字段名"，结果被复述给
    用户、且在 CE-A2 场景里被错误地表述成"用户提到的"内容（用户实际未曾提及该代码）。
    修复：改用人话标签 + 不再宣称"用户点名"。此处锁定修复后的行为，防止再次回归。"""

    def test_requested_capability_raw_code_does_not_leak_into_directive(self):
        result = _run(None, {"current_task_text": "占位任务", "requested_capability": "MATRIX"})
        self.assertNotIn("MATRIX", result["dialogue_directive"])
        self.assertIn("账号矩阵", result["dialogue_directive"])

    def test_directive_does_not_overclaim_user_named_the_capability(self):
        """requested_capability 也可能是模型从语义推断出来的，不一定是用户逐字点名——
        指令文本不应断言"用户点名"，避免对话 LLM 复述成不实归因。"""
        result = _run(None, {"current_task_text": "占位任务", "requested_capability": "MATRIX"})
        self.assertNotIn("用户点名", result["dialogue_directive"])

    def test_block_reason_raw_code_does_not_leak_into_directive(self):
        """NO_ENTRY_CAPABILITIES（CAP-03/05）不在 VALID_REQUESTED_CAPABILITY 枚举里，
        无法通过 requested_capability 字段点名，因此 BLOCKED 分支的 directive 只能用
        MATRIX/CAMPAIGN 等六项有物理入口能力在"没有任务描述"时触发（block_reason=
        NO_CURRENT_TASK_STATED），这里用这一真实可达路径验证不泄漏原始代码。"""
        result = _run(None, {"requested_capability": "MATRIX"})
        self.assertNotIn("NO_CURRENT_TASK_STATED", result["dialogue_directive"])
        self.assertIn("还没有听你说过具体任务内容", result["dialogue_directive"])

    def test_call_intent_json_still_carries_raw_machine_readable_codes(self):
        """结构化的 call_intent_json 不面向用户展示，机器可读代码原样保留是正确的，
        不应该被这次修复误伤。"""
        result = _run(None, {"requested_capability": "MATRIX"})
        intent = json.loads(result["call_intent_json"])
        self.assertEqual(intent["per_capability"]["MATRIX"]["block_reason"], "NO_CURRENT_TASK_STATED")


class TestMultiTurnPersistence(unittest.TestCase):
    """第二轮必须在第一轮快照基础上合并，而不是从零重建（真实对话是多轮的）。"""

    def test_second_turn_preserves_first_turn_task_when_not_restated(self):
        turn1 = _run(None, {"current_task_text": "做女装穿搭内容", "temporal_scope": "CYCLE"})
        turn2 = _run(turn1["snapshot_json"], {"confirmation_signal": "AFFIRM"})

        snap2 = json.loads(turn2["snapshot_json"])
        self.assertEqual(snap2["current_task"]["text"], "做女装穿搭内容",
                          "第二轮没有重新陈述任务时，第一轮任务文本不应丢失")
        self.assertEqual(snap2["last_confirmation_signal"], "AFFIRM")
        self.assertEqual(snap2["revision"], 2, "两轮都产生了真实变化，revision 应累加而非重置")

    def test_rejected_second_turn_leaves_first_turn_state_untouched(self):
        turn1 = _run(None, {"current_task_text": "做女装穿搭内容"})
        turn2 = _run(turn1["snapshot_json"], {"unknown_field": "x"})

        self.assertEqual(turn2["patch_ok"], "false")
        snap2 = json.loads(turn2["snapshot_json"])
        self.assertEqual(snap2["current_task"]["text"], "做女装穿搭内容")
        self.assertEqual(snap2["revision"], 1, "被拒绝的第二轮不得推进 revision")


if __name__ == "__main__":
    unittest.main(verbosity=2)
