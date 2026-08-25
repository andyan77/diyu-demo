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


class TestV0_2SnapshotExpansion(unittest.TestCase):
    """v0.2 扩展：account_stage / expression_discretion / capacity_triad 三项新增字段
    （设计文档 §二 #5/#6/#7），刻意只用扁平字符串/枚举承载，回避 §七 登记的嵌套结构
    稳定性风险。"""

    def test_account_stage_text_captured(self):
        result = _run(None, {"current_task_text": "占位", "account_stage_text": "已经有稳定粉丝但没转化"})
        snap = json.loads(result["snapshot_json"])
        self.assertEqual(snap["account_stage"]["text"], "已经有稳定粉丝但没转化")
        self.assertEqual(snap["account_stage"]["confirmation"], "SYSTEM_TENTATIVE",
                          "P0 每轮只有一个通用 confirmation_signal，无法可靠归因到某个具体字段，"
                          "如实固定为 SYSTEM_TENTATIVE，不得伪造 USER_CONFIRMED")

    def test_discretion_fields_only_overwrite_when_stated(self):
        turn1 = _run(None, {"current_task_text": "占位", "plot_allowed": "NOT_ALLOWED"})
        turn2 = _run(turn1["snapshot_json"], {"remix_allowed": "ALLOWED"})
        snap2 = json.loads(turn2["snapshot_json"])
        self.assertEqual(snap2["expression_discretion"]["plot_allowed"], "NOT_ALLOWED",
                          "第二轮没有重新提到剧情裁量时，第一轮的表态不应被 UNSTATED 覆盖掉")
        self.assertEqual(snap2["expression_discretion"]["remix_allowed"], "ALLOWED")

    def test_illegal_discretion_enum_rejects_whole_patch(self):
        patch = {"plot_allowed": "MAYBE_SOMETIMES"}
        result = _run(None, patch)
        self.assertEqual(result["patch_ok"], "false")
        self.assertTrue(result["reject_reason"].startswith("ILLEGAL_ENUM:plot_allowed"))

    def test_capacity_triad_three_fields_independently_carried(self):
        result = _run(None, {
            "current_task_text": "占位",
            "desired_output_text": "每周 5 条",
            "cycle_available_text": "本周期只能做 2 条",
            "baseline_text": "团队长期稳定产出 3 条/周",
        })
        snap = json.loads(result["snapshot_json"])
        triad = snap["capacity_triad"]
        self.assertEqual(triad["desired_output"], "每周 5 条")
        self.assertEqual(triad["cycle_available"], "本周期只能做 2 条")
        self.assertEqual(triad["baseline"], "团队长期稳定产出 3 条/周")

    def test_pre_v0_2_persisted_snapshot_upgrades_without_crashing(self):
        """向前兼容：模拟 v0.3 及更早持久化的快照（没有 account_stage 等三个新字段），
        必须能被本版本正常读取、补齐缺失字段、继续合并新 patch，而不是抛异常或丢失旧数据。"""
        old_snapshot_json = json.dumps({
            "schema_version": 1,
            "task_id": None,
            "revision": 3,
            "current_task": {"text": "旧会话已经存在的任务", "temporal_scope": "CYCLE", "source_ref": "USER_DIRECT"},
            "goal_structure": {"primary_goal": "旧目标", "secondary_goals": [], "priority_order": [], "non_sacrifice_constraints": []},
            "allowed_capabilities": [],
            "open_threads": [],
            "last_confirmation_signal": "NONE",
            "last_route_intent": None,
        }, ensure_ascii=False)

        result = _run(old_snapshot_json, {"account_stage_text": "新会话里才第一次提到阶段"})
        snap = json.loads(result["snapshot_json"])
        self.assertEqual(snap["current_task"]["text"], "旧会话已经存在的任务", "补齐新字段不得丢失旧字段的真实数据")
        self.assertEqual(snap["account_stage"]["text"], "新会话里才第一次提到阶段")


class TestContentTaskProjection(unittest.TestCase):
    """project_content_task：快照 → Content Brief 下游投影，设计参照
    V1_M1_TASK_CONTEXT_COMPILER_DESIGN_v0.1.md §三。P0 快照结构性地缺少多个设计文档
    要求的字段，投影必须如实标记缺口，不得编造等价值。"""

    def test_fresh_snapshot_marks_remaining_structural_gap_not_fabricated_value(self):
        """v0.2 起 account_stage / expression_discretion / available_capacity 已由快照
        承载，不再是缺口；evidence_and_gaps（evidence_bundle[]/gaps[]，数组+多维度）仍未
        落地，如实标记为 NOT_CAPTURED_IN_P0_SNAPSHOT。"""
        snap = compiler._default_snapshot()
        ct = compiler.project_content_task(snap)
        self.assertEqual(ct["evidence_and_gaps"], "NOT_CAPTURED_IN_P0_SNAPSHOT")
        self.assertIsNone(ct["account_stage"])
        self.assertEqual(
            ct["expression_discretion"],
            {"plot_allowed": "UNSTATED", "remix_allowed": "UNSTATED", "conflict_allowed": "UNSTATED", "controversy_allowed": "UNSTATED"},
        )
        self.assertIsNone(ct["available_capacity"])
        self.assertEqual(ct["platform_and_form"], "PLATFORM_UNCONFIRMED")

    def test_captured_account_stage_discretion_and_capacity_pass_through_projection(self):
        result = _run(None, {
            "current_task_text": "占位任务",
            "account_stage_text": "刚起号，还没有稳定粉丝",
            "plot_allowed": "NOT_ALLOWED",
            "controversy_allowed": "ALLOWED",
            "cycle_available_text": "本周期能做 3 条",
        })
        snap = json.loads(result["snapshot_json"])
        ct = compiler.project_content_task(snap)
        self.assertEqual(ct["account_stage"], "刚起号，还没有稳定粉丝")
        self.assertEqual(ct["expression_discretion"]["plot_allowed"], "NOT_ALLOWED")
        self.assertEqual(ct["expression_discretion"]["controversy_allowed"], "ALLOWED")
        self.assertEqual(ct["expression_discretion"]["remix_allowed"], "UNSTATED")
        self.assertEqual(ct["available_capacity"], "本周期能做 3 条")

    def test_caller_supplied_professional_judgment_fields_not_fabricated_by_m1(self):
        """audience_problem_scene / audience_shift / content_promise / post_publish_observation
        设计文档明确规定 M1 不做专业判断；未提供时必须是 None，不得由 M1 自己生成内容。"""
        snap = compiler._default_snapshot()
        ct = compiler.project_content_task(snap)
        for field in compiler.CONTENT_TASK_CALLER_SUPPLIED_KEYS:
            self.assertIsNone(ct[field])
            self.assertIn(field, ct["projection_gaps"])

    def test_caller_supplied_values_pass_through_and_leave_gaps(self):
        snap = compiler._default_snapshot()
        ct = compiler.project_content_task(
            snap,
            caller_supplied={
                "audience_problem_scene": "受众看腻了同质化穿搭内容",
                "content_promise": "三件基础款穿出五种通勤感",
            },
        )
        self.assertEqual(ct["audience_problem_scene"], "受众看腻了同质化穿搭内容")
        self.assertEqual(ct["content_promise"], "三件基础款穿出五种通勤感")
        self.assertIsNone(ct["audience_shift"])
        self.assertNotIn("audience_problem_scene", ct["projection_gaps"])
        self.assertNotIn("content_promise", ct["projection_gaps"])
        self.assertIn("audience_shift", ct["projection_gaps"])
        self.assertIn("post_publish_observation", ct["projection_gaps"])

    def test_unknown_caller_supplied_key_rejected(self):
        snap = compiler._default_snapshot()
        with self.assertRaises(ValueError):
            compiler.project_content_task(snap, caller_supplied={"made_up_field": "x"})

    def test_cycle_role_not_applicable_when_temporal_scope_is_not_cycle(self):
        result = _run(None, {"current_task_text": "做一条长期人设内容", "temporal_scope": "LONG_TERM"})
        snap = json.loads(result["snapshot_json"])
        ct = compiler.project_content_task(snap)
        self.assertEqual(ct["cycle_role"], "NOT_APPLICABLE")

    def test_cycle_role_marked_as_structural_gap_when_temporal_scope_is_cycle(self):
        """temporal_scope=CYCLE 时设计文档要求取真实 cycle_role，但 P0 快照没有承载该
        字段的位置——不得从 temporal_scope 本身编造一个 cycle_role，如实标记缺口。"""
        result = _run(None, {"current_task_text": "本周期发三条穿搭", "temporal_scope": "CYCLE"})
        snap = json.loads(result["snapshot_json"])
        ct = compiler.project_content_task(snap)
        self.assertEqual(ct["cycle_role"], "NOT_CAPTURED_IN_P0_SNAPSHOT")

    def test_goal_structure_passthrough_not_flattened(self):
        result = _run(None, {
            "current_task_text": "占位任务",
            "primary_goal_text": "三个月内起量到万粉",
            "non_sacrifice_constraint_text": "不做剧情类内容",
        })
        snap = json.loads(result["snapshot_json"])
        ct = compiler.project_content_task(snap)
        self.assertEqual(ct["primary_goal"], "三个月内起量到万粉")
        self.assertEqual(ct["non_sacrifice_constraints"], ["不做剧情类内容"])

    def test_source_defaults_to_current_task_source_ref_then_override(self):
        snap = compiler._default_snapshot()
        ct_default = compiler.project_content_task(snap)
        self.assertEqual(ct_default["source"], "USER_DIRECT")

        ct_override = compiler.project_content_task(snap, source_override="CAMPAIGN_DECISION_PACKAGE")
        self.assertEqual(ct_override["source"], "CAMPAIGN_DECISION_PACKAGE")


if __name__ == "__main__":
    unittest.main(verbosity=2)
