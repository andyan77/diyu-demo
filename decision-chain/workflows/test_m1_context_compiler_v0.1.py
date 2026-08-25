"""
M1 任务上下文编译器 · 正式单元测试
task_id: DIYU-V1-M1-NATURAL-CONTEXT-001

用途：把 decision-chain/evidence/V1_M1_CANDIDATE_RUN_001.md 之前口头验证过的场景
（及后续新增场景）固化成可重复运行的测试文件，补齐 L3 记录标出的已知缺口
（"本地单测...非独立正式测试文件"）。

运行方式（核心用例纯 stdlib，无第三方依赖；一个可选的 DSL 防漂移用例需要 PyYAML，
缺少时自动 skip，不拖垮整个套件）：
    python3 decision-chain/workflows/test_m1_context_compiler_v0.1.py -v

被测源文件名含版本号（m1_context_compiler_v0.1.py），非法 Python 模块标识符，
故用 importlib.util 按路径加载，而非 import 语句。
"""

import importlib.util
import json
import os
import tempfile
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
        """断言变更说明（v0.3，非静默放松）：evidence_and_gaps 不再是
        "NOT_CAPTURED_IN_P0_SNAPSHOT" 哨兵——evidence_bundle[]/gaps[] 已落地，投影改为真实
        拼装。剩下的结构缺口收窄为 evidence_and_gaps.relevance_filter：设计文档 §三 要求取
        "与本条相关的子集"，而 P0 快照没有本条内容的标识符（无 item_id），任何过滤都会是
        编造的相关性判断，故全量透传并登记该缺口。"""
        snap = compiler._default_snapshot()
        ct = compiler.project_content_task(snap)
        self.assertIsInstance(ct["evidence_and_gaps"], dict)
        self.assertEqual(ct["evidence_and_gaps"]["evidence"], [])
        self.assertIn("evidence_and_gaps.relevance_filter", ct["projection_gaps"])
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


class TestV0_3EvidenceBundle(unittest.TestCase):
    """v0.3 扩展：evidence_bundle[]（设计文档 §二 #9 + §三 五个正交维度）。

    采用设计文档 §七 官方登记的降级路径：LLM 只出三个扁平粗粒度信号
    （evidence_text / evidence_nature / evidence_scope），五维度里其余三维由确定性代码
    按固定常量组装。不重试"LLM 直出嵌套对象"这条已有先例证据的路线。"""

    def test_evidence_entry_carries_all_five_dimensions(self):
        result = _run(None, {
            "current_task_text": "占位任务",
            "evidence_text": "我们店在杭州，主要卖通勤女装",
            "evidence_nature": "FACT",
            "evidence_scope": "THIS_ACCOUNT",
        })
        snap = json.loads(result["snapshot_json"])
        self.assertEqual(len(snap["evidence_bundle"]), 1)
        item = snap["evidence_bundle"][0]
        self.assertEqual(item["id"], "ev_001")
        self.assertEqual(item["text"], "我们店在杭州，主要卖通勤女装")
        self.assertEqual(item["nature"], "FACT")
        self.assertEqual(item["provenance"], "USER_DIRECT")
        self.assertEqual(item["confirmation"], "SYSTEM_TENTATIVE")
        self.assertEqual(item["scope"], "THIS_ACCOUNT")
        self.assertEqual(item["availability"], "AVAILABLE")
        self.assertEqual(item["captured_at_revision"], 0, "取增量前的 revision，与 open_threads 同一时序先例")

    def test_provenance_is_always_user_direct_never_fabricated_source(self):
        """本候选环境唯一的信息入口就是用户这一轮的自然语言（无 Tool 节点、无联网、
        file_upload.enabled=False），写成 SOURCED_MATERIAL 等值即伪造来源。"""
        result = _run(None, {"evidence_text": "我不喜欢强 CTA", "evidence_nature": "PREFERENCE"})
        snap = json.loads(result["snapshot_json"])
        self.assertEqual(snap["evidence_bundle"][0]["provenance"], "USER_DIRECT")

    def test_confirmation_stays_system_tentative_even_on_affirm_turn(self):
        """冻结硬约束一：系统推断不因为被写入持久化就升级为用户确认事实。
        轮级 confirmation_signal=AFFIRM 无法归因到具体哪一条证据，**不得**被解释成对某条
        证据的用户确认；轮级 DECLINE 同样不得写成 REJECTED。"""
        turn1 = _run(None, {"evidence_text": "去年双十一我们卖得最好的是大衣", "evidence_nature": "FACT"})
        turn2 = _run(turn1["snapshot_json"], {
            "confirmation_signal": "AFFIRM",
            "evidence_text": "客单价大概三百多",
            "evidence_nature": "FACT",
        })
        snap = json.loads(turn2["snapshot_json"])
        self.assertEqual(snap["last_confirmation_signal"], "AFFIRM")
        self.assertEqual(len(snap["evidence_bundle"]), 2)
        for item in snap["evidence_bundle"]:
            self.assertEqual(item["confirmation"], "SYSTEM_TENTATIVE",
                              "既有条目与新写入条目都不得因为一次轮级 AFFIRM 变成 USER_CONFIRMED")

    def test_decline_turn_does_not_write_rejected(self):
        turn1 = _run(None, {"evidence_text": "我们只有两个人做内容", "evidence_nature": "FACT"})
        turn2 = _run(turn1["snapshot_json"], {"confirmation_signal": "DECLINE"})
        snap = json.loads(turn2["snapshot_json"])
        self.assertEqual(snap["evidence_bundle"][0]["confirmation"], "SYSTEM_TENTATIVE")

    def test_scope_defaults_to_unstated_and_is_not_inferred_from_temporal_scope(self):
        """共享合同一 §三 反例：不得把"这条不要剧情"静默扩张成长期规则。用户没说作用域时
        只能是 UNSTATED——**绝不**从 current_task.temporal_scope 推导条目作用域，任务的时间
        作用域不等于某条证据的适用层级。"""
        result = _run(None, {
            "current_task_text": "做一条长期人设内容",
            "temporal_scope": "LONG_TERM",
            "evidence_text": "这条不要剧情",
            "evidence_nature": "PREFERENCE",
        })
        snap = json.loads(result["snapshot_json"])
        self.assertEqual(snap["current_task"]["temporal_scope"], "LONG_TERM")
        self.assertEqual(snap["evidence_bundle"][0]["scope"], "UNSTATED")

    def test_incomplete_dimension_drops_only_that_evidence_not_whole_patch(self):
        """维度不全（给了原话却没给性质）：只跳过这一条证据，本轮其余捕获照常合并。
        既有"整体拒绝"纪律的适用范围是"未知字段或非法枚举值"，而 UNSTATED 是 evidence_nature
        的合法取值——不得把它扩成整体拒绝（否则模型漏填一个枚举就作废用户这一轮说的任务和
        目标，与「资料不足时不得整任务拒绝」相冲）。"""
        result = _run(None, {
            "current_task_text": "本周期发三条穿搭",
            "primary_goal_text": "把到店转化做起来",
            "evidence_text": "我们店在杭州",
            "evidence_nature": "UNSTATED",
        })
        self.assertEqual(result["patch_ok"], "true", "不得因维度不全整体拒绝 patch")
        self.assertEqual(result["reject_reason"], "")
        snap = json.loads(result["snapshot_json"])
        self.assertEqual(snap["current_task"]["text"], "本周期发三条穿搭", "本轮其余捕获必须照常合并")
        self.assertEqual(snap["goal_structure"]["primary_goal"], "把到店转化做起来")
        self.assertEqual(snap["evidence_bundle"], [], "维度不全的条目不得写入快照，也不得补一个默认 nature")

    def test_dropped_evidence_recorded_in_turn_report_not_in_dialogue_directive(self):
        """丢弃事实如实登记在机器可读通道；dialogue_directive 不变——不给 CE-A2（内部枚举被
        对话 LLM 复述给用户）这个已知缺陷新增触发器。"""
        result = _run(None, {
            "current_task_text": "占位任务",
            "evidence_text": "我们店在杭州",
            "evidence_nature": "UNSTATED",
        })
        report = json.loads(result["turn_report_json"])
        self.assertTrue(report["evidence_dropped_incomplete"])
        self.assertNotIn("evidence", result["dialogue_directive"])
        self.assertNotIn("我们店在杭州", result["dialogue_directive"])

    def test_evidence_dropped_flag_false_on_normal_turn(self):
        ok = _run(None, {"evidence_text": "客单价三百多", "evidence_nature": "FACT"})
        self.assertFalse(json.loads(ok["turn_report_json"])["evidence_dropped_incomplete"])
        none_at_all = _run(None, {"current_task_text": "占位任务"})
        self.assertFalse(json.loads(none_at_all["turn_report_json"])["evidence_dropped_incomplete"],
                          "本轮根本没有证据信号时不算被丢弃")

    def test_empty_evidence_text_writes_nothing(self):
        result = _run(None, {"current_task_text": "占位任务", "evidence_text": "   ", "evidence_nature": "FACT"})
        snap = json.loads(result["snapshot_json"])
        self.assertEqual(snap["evidence_bundle"], [])

    def test_illegal_evidence_nature_rejects_whole_patch(self):
        result = _run(None, {"current_task_text": "不应写入", "evidence_nature": "VIBES"})
        self.assertEqual(result["patch_ok"], "false")
        self.assertTrue(result["reject_reason"].startswith("ILLEGAL_ENUM:evidence_nature"))
        snap = json.loads(result["snapshot_json"])
        self.assertIsNone(snap["current_task"]["text"])

    def test_system_inference_not_accepted_from_llm_patch(self):
        """SYSTEM_INFERENCE 刻意不在 patch 枚举内：系统推断只能由确定性代码写入，模型不得
        给自己对用户原话的复述贴上"系统判断"标签。P0 没有任何代码路径产出它。"""
        result = _run(None, {"evidence_text": "我猜你是想起号", "evidence_nature": "SYSTEM_INFERENCE"})
        self.assertEqual(result["patch_ok"], "false")
        self.assertTrue(result["reject_reason"].startswith("ILLEGAL_ENUM:evidence_nature"))
        self.assertNotIn("SYSTEM_INFERENCE", compiler.VALID_EVIDENCE_NATURE_PATCH)
        self.assertIn("SYSTEM_INFERENCE", compiler.EVIDENCE_DIMENSION_VOCAB["nature"],
                      "词表仍保留该取值供下游识别，只是 P0 无产出路径")

    def test_illegal_evidence_scope_rejects_whole_patch(self):
        result = _run(None, {"evidence_text": "x", "evidence_nature": "FACT", "evidence_scope": "FOREVER"})
        self.assertEqual(result["patch_ok"], "false")
        self.assertTrue(result["reject_reason"].startswith("ILLEGAL_ENUM:evidence_scope"))

    def test_duplicate_evidence_text_not_appended_and_revision_not_bumped(self):
        turn1 = _run(None, {"evidence_text": "我们只有两个人做内容", "evidence_nature": "FACT"})
        snap1 = json.loads(turn1["snapshot_json"])
        turn2 = _run(turn1["snapshot_json"], {"evidence_text": "我们只有两个人做内容", "evidence_nature": "FACT"})
        snap2 = json.loads(turn2["snapshot_json"])
        self.assertEqual(len(snap2["evidence_bundle"]), 1)
        self.assertEqual(snap2["revision"], snap1["revision"], "重复内容不构成真实状态变化")
        self.assertEqual(turn2["state_changed"], "false")

    def test_ids_increment_and_existing_entries_never_modified(self):
        """P0 纯追加：既有条目在任何情况下都不被修改——冻结硬约束二在 P0 天然不可违反。"""
        turn1 = _run(None, {"evidence_text": "第一条事实", "evidence_nature": "FACT", "evidence_scope": "THIS_ACCOUNT"})
        first_before = json.loads(turn1["snapshot_json"])["evidence_bundle"][0]
        turn2 = _run(turn1["snapshot_json"], {"evidence_text": "第二条偏好", "evidence_nature": "PREFERENCE"})
        bundle = json.loads(turn2["snapshot_json"])["evidence_bundle"]
        self.assertEqual([i["id"] for i in bundle], ["ev_001", "ev_002"])
        self.assertEqual(bundle[0], first_before, "既有条目必须逐字保持不变")
        self.assertEqual(bundle[1]["captured_at_revision"], 1)

    def test_no_user_confirmed_anywhere_in_p0_output(self):
        """全局规则：任何写入路径都不得把任何条目的 confirmation 置为 USER_CONFIRMED
        （不只是不得改既有条目，新建条目同样不可）。P0 没有按字段的用户确认交互。"""
        turn1 = _run(None, {
            "current_task_text": "占位任务",
            "account_stage_text": "刚起号",
            "evidence_text": "我们店在杭州",
            "evidence_nature": "FACT",
            "confirmation_signal": "AFFIRM",
        })
        turn2 = _run(turn1["snapshot_json"], {"confirmation_signal": "AFFIRM"})
        self.assertNotIn("USER_CONFIRMED", turn2["snapshot_json"])


# 曾经这里有一个 TestEvidenceOverwriteGuard 类，测的是 _may_modify_existing_evidence
# ——一个零调用方的运行时守卫。该守卫连同 PROVENANCE_MAY_MODIFY_USER_CONFIRMED 常量已被删除：
# P0 的 _merge_evidence_item 是纯追加、永不修改既有条目，两条冻结硬约束因此在**结构上**天然
# 满足，不需要独立守卫来保证一件不可能发生的事。原类里所有断言都只调用那个已删除的谓词，
# 没有一条覆盖 P0 真实可达的行为；两条硬约束在 P0 的真实覆盖仍在 TestV0_3EvidenceBundle 里，
# 且走的是 main() 这条真实路径（因此不再带 NOT_VERIFIED_IN_LIVE 标注）：
#   约束一（不得升级为用户确认事实）
#     → test_confirmation_stays_system_tentative_even_on_affirm_turn
#     → test_decline_turn_does_not_write_rejected
#     → test_no_user_confirmed_anywhere_in_p0_output
#   约束二（不得覆盖既有条目）
#     → test_ids_increment_and_existing_entries_never_modified（既有条目逐字不变）
#     → test_duplicate_evidence_text_not_appended_and_revision_not_bumped
# 未来引入"修改既有条目"动作的那一批（M4/M5）需要重新引入守卫及其配套测试。


class TestV0_3Gaps(unittest.TestCase):
    """v0.3 扩展：gaps[]（设计文档 §二 #11）。零新增 LLM patch key，完全由确定性代码
    从既有快照状态推导；每轮整体重算，不留历史（不是事件溯源）。

    两种视图（见 _compute_gaps 的 include_structural 参数）：
      - **持久化视图**（main() 写进 snapshot_json，include_structural=False）：只有随对话
        状态变化的动态子集。8 条 P0_STRUCTURAL_GAPS 内容恒定，逐轮序列化不携带任何新信息。
      - **完整合规视图**（include_structural=True，project_content_task 给下游的那一份）：
        动态子集 + 8 条结构性常量。
    `_gaps`/`_refs` 读持久化视图，`_full_gaps`/`_full_refs` 读完整视图。"""

    def _gaps(self, result):
        return json.loads(result["snapshot_json"])["gaps"]

    def _refs(self, result):
        return [g["field_ref"] for g in self._gaps(result)]

    def _full_gaps(self, result):
        snap = json.loads(result["snapshot_json"])
        return compiler._compute_gaps(snap, include_structural=True)

    def test_gap_entry_shape_is_exactly_three_keys(self):
        for gap in self._full_gaps(_run(None, {})):
            self.assertEqual(set(gap.keys()), {"field_ref", "status", "degraded_to"})
            self.assertIn(gap["status"], ("MISSING", "DEGRADED"))

    def test_fresh_snapshot_gap_inventory(self):
        """空快照：持久化视图 12 条动态；完整视图 = 12 + 8 条结构性常量 = 20 条。
        全部机器可读、不进用户可见文本。"""
        self.assertEqual(len(compiler.P0_STRUCTURAL_GAPS), 8)
        self.assertEqual(len(self._gaps(_run(None, {}))), 12)
        self.assertEqual(len(self._full_gaps(_run(None, {}))), 20)

    def test_persisted_gaps_exclude_constant_structural_entries(self):
        """8 条结构性常量内容恒定、不携带"这一轮独有"的信息——逐轮序列化进 Dify 会话变量
        只会让持久化快照白白膨胀。需要它们的消费方直接读 P0_STRUCTURAL_GAPS 常量，或用
        include_structural=True 现拼完整视图。"""
        persisted_refs = self._refs(_run(None, {"current_task_text": "占位任务"}))
        for gap in compiler.P0_STRUCTURAL_GAPS:
            self.assertNotIn(gap["field_ref"], persisted_refs,
                             gap["field_ref"] + " 是恒定常量，不应逐轮写进持久化快照")
        for ref in ("subject_scope", "market_observations", "runtime_evidence"):
            self.assertNotIn(ref, persisted_refs)

    def test_default_include_structural_is_true_for_backward_compatibility(self):
        """默认值保持 True：既有调用方与手工调用拿到的仍是完整视图，本次优化只作用于
        main() 显式传 False 的持久化路径。"""
        snap = compiler._default_snapshot()
        self.assertEqual(compiler._compute_gaps(snap), compiler._compute_gaps(snap, include_structural=True))
        self.assertEqual(len(compiler._compute_gaps(snap)), 20)

    def test_structural_gaps_declare_no_carrier_not_a_missing_answer(self):
        """结构性未承载必须是 DEGRADED/NOT_CAPTURED_IN_P0_SNAPSHOT（**不得向用户追问**，
        问了也没地方放），不能标成 MISSING（那会被读成"用户还没说"）。"""
        by_ref = {g["field_ref"]: g for g in self._full_gaps(_run(None, {}))}
        for ref in ("subject_scope", "business_goal_categories", "cycle_ref"):
            self.assertEqual(by_ref[ref]["status"], "DEGRADED")
            self.assertEqual(by_ref[ref]["degraded_to"], "NOT_CAPTURED_IN_P0_SNAPSHOT")

    def test_confirmation_and_availability_single_value_limits_registered(self):
        """确认维度五值里 P0 只可达 SYSTEM_TENTATIVE，可用性维度里 STALE/EXPIRED 需要生命
        周期时钟——如实登记为结构缺口，不假装这两维在正常运转。"""
        by_ref = {g["field_ref"]: g for g in self._full_gaps(_run(None, {}))}
        self.assertEqual(by_ref["account_stage.confirmation"]["degraded_to"],
                          "ALWAYS_SYSTEM_TENTATIVE_NO_PER_FIELD_CONFIRM_CHANNEL")
        self.assertEqual(by_ref["evidence_bundle[].confirmation"]["degraded_to"],
                          "ALWAYS_SYSTEM_TENTATIVE_NO_PER_FIELD_CONFIRM_CHANNEL")
        self.assertEqual(by_ref["evidence_bundle[].availability"]["degraded_to"],
                          "ALWAYS_AVAILABLE_NO_LIFECYCLE_CLOCK")

    def test_capacity_triad_three_gaps_never_merged_into_one(self):
        """共享合同一 §二.7 逐字要求三者分别承载、不得静默取其一覆盖三个。"""
        refs = self._refs(_run(None, {"cycle_available_text": "本周期只能做 2 条"}))
        self.assertIn("capacity_triad.desired_output", refs)
        self.assertIn("capacity_triad.baseline", refs)
        self.assertNotIn("capacity_triad.cycle_available", refs, "已说出口的一项应从缺口里消失")

    def test_unstated_discretion_registered_as_degraded_not_assumed_allowed(self):
        """未表态不得被推定为允许或不允许。"""
        by_ref = {g["field_ref"]: g for g in self._gaps(_run(None, {"plot_allowed": "NOT_ALLOWED"}))}
        self.assertNotIn("expression_discretion.plot_allowed", by_ref)
        for key in ("remix_allowed", "conflict_allowed", "controversy_allowed"):
            self.assertEqual(by_ref["expression_discretion." + key]["degraded_to"], "UNSTATED")

    def test_gaps_shrink_as_user_states_things(self):
        turn1 = _run(None, {})
        turn2 = _run(turn1["snapshot_json"], {
            "current_task_text": "本周期发三条穿搭",
            "temporal_scope": "CYCLE",
            "primary_goal_text": "把到店转化做起来",
            "account_stage_text": "刚起号",
            "evidence_text": "我们店在杭州",
            "evidence_nature": "FACT",
            "evidence_scope": "THIS_ACCOUNT",
        })
        refs1, refs2 = self._refs(turn1), self._refs(turn2)
        self.assertLess(len(refs2), len(refs1))
        for gone in ("current_task.text", "current_task.temporal_scope",
                     "goal_structure.primary_goal", "account_stage.text", "evidence_bundle"):
            self.assertIn(gone, refs1)
            self.assertNotIn(gone, refs2)
        self.assertNotIn("evidence_bundle[].scope", refs2, "用户说明了作用域时不应再登记该缺口")

    def test_unstated_evidence_scope_aggregated_into_one_gap(self):
        result = _run(None, {"evidence_text": "这条不要剧情", "evidence_nature": "PREFERENCE"})
        refs = self._refs(result)
        self.assertEqual(refs.count("evidence_bundle[].scope"), 1)
        self.assertNotIn("evidence_bundle", refs, "已有条目时不再是 MISSING")

    def test_gaps_recomputed_on_rejected_turn_without_bumping_revision(self):
        """缺口清单是既有状态的派生视图，不是用户造成的状态变化：patch 被拒绝的轮次同样
        重算，且不得推进 revision、不得置 state_changed。"""
        turn1 = _run(None, {"current_task_text": "做女装穿搭内容"})
        turn2 = _run(turn1["snapshot_json"], {"made_up_field": "x"})
        self.assertEqual(turn2["patch_ok"], "false")
        self.assertEqual(turn2["state_changed"], "false")
        snap1, snap2 = json.loads(turn1["snapshot_json"]), json.loads(turn2["snapshot_json"])
        self.assertEqual(snap2["revision"], snap1["revision"])
        self.assertEqual(snap2["gaps"], snap1["gaps"], "快照没变时重算结果应与上一轮一致")

    def test_gaps_never_leak_into_dialogue_directive(self):
        """field_ref 是纯内部路径字符串，一旦拼进指令文本必然泄漏（CE-A2 的真实教训）。
        用户可见的追问仍然只有既有的人话标签那一项。"""
        result = _run(None, {"requested_capability": "MATRIX"})
        directive = result["dialogue_directive"]
        for gap in json.loads(result["snapshot_json"])["gaps"]:
            self.assertNotIn(gap["field_ref"], directive)
        self.assertNotIn("NOT_CAPTURED_IN_P0_SNAPSHOT", directive)

    def test_compute_gaps_is_pure_and_does_not_write_into_input(self):
        snap = compiler._default_snapshot()
        del snap["gaps"]
        gaps = compiler._compute_gaps(snap)
        self.assertTrue(gaps)
        self.assertNotIn("gaps", snap, "_compute_gaps 必须是纯函数，不得写入入参")
        self.assertEqual(gaps, compiler._compute_gaps(snap), "幂等")


class TestNonBlockingGaps(unittest.TestCase):
    """共享合同一 §五「只追问真正阻塞当前任务的一项，其余作为缺口继续运行」的机制化落地：
    消解 compute_call_intent 里 non_blocking_gaps 一直硬编码为 [] 的空占位。"""

    def _cont(self, result):
        return json.loads(result["call_intent_json"])["continuation"]["non_blocking_gaps"]

    def test_blocking_field_excluded_when_requested_capability_is_blocked(self):
        result = _run(None, {"requested_capability": "MATRIX"})
        intent = json.loads(result["call_intent_json"])
        self.assertEqual(intent["per_capability"]["MATRIX"]["block_reason"], "NO_CURRENT_TASK_STATED")
        non_blocking = self._cont(result)
        self.assertNotIn("current_task.text", non_blocking, "真正阻塞的一项不算非阻塞缺口")
        self.assertIn("goal_structure.primary_goal", non_blocking, "其余缺口带着继续跑")

    def test_two_blocking_fields_excluded_for_task_or_goal_block_reason(self):
        result = _run(None, {"requested_capability": "CAMPAIGN"})
        intent = json.loads(result["call_intent_json"])
        self.assertEqual(intent["per_capability"]["CAMPAIGN"]["block_reason"], "NO_TASK_OR_GOAL_STATED")
        non_blocking = self._cont(result)
        self.assertNotIn("current_task.text", non_blocking)
        self.assertNotIn("goal_structure.primary_goal", non_blocking)

    def test_all_gaps_non_blocking_when_nothing_is_blocked(self):
        result = _run(None, {"current_task_text": "本周期发三条穿搭", "requested_capability": "CONTENT_BRIEF"})
        snap = json.loads(result["snapshot_json"])
        self.assertEqual(self._cont(result), [g["field_ref"] for g in snap["gaps"]])

    def test_all_gaps_non_blocking_when_no_capability_requested(self):
        result = _run(None, {})
        snap = json.loads(result["snapshot_json"])
        self.assertEqual(self._cont(result), [g["field_ref"] for g in snap["gaps"]])

    def test_non_blocking_gaps_carries_only_field_ref_strings(self):
        """完整对象留在 snapshot.gaps，call_intent 里只放字符串，避免膨胀。"""
        for item in self._cont(_run(None, {})):
            self.assertIsInstance(item, str)


class TestDeferredArrayFieldsHonestSentinels(unittest.TestCase):
    """market_observations[]（#10）与 runtime_evidence[]（#14）本批 DEFER。

    空数组 + gaps 条目**必须同时存在**：孤零零的 [] 会被下游读成"查过了，没有"，那是不实
    主张（共享合同一 §六「没有市场资料时不得声称已完成市场比较」）。这两个用例把这条诚实
    口径变成会失败的测试，防止后来者删掉 gaps 常量条目只留空数组。

    **配对成立于完整视图**：这两条是内容恒定的结构性常量，不进逐轮持久化快照，所以断言
    针对 project_content_task 给下游的 evidence_and_gaps.gaps（include_structural=True）
    ——那才是"空数组 + 缺口登记必须同时被下游看到"这条口径真正落地的地方。"""

    def _assert_empty_array_paired_with_gap(self, field):
        result = _run(None, {"current_task_text": "占位任务"})
        snap = json.loads(result["snapshot_json"])
        self.assertEqual(snap[field], [])
        full_gaps = compiler.project_content_task(snap)["evidence_and_gaps"]["gaps"]
        matching = [g for g in full_gaps if g["field_ref"] == field]
        self.assertEqual(len(matching), 1, field + " 的空数组必须配一条 gaps 登记，否则会被读成已查过")
        self.assertEqual(matching[0]["status"], "DEGRADED")
        self.assertEqual(matching[0]["degraded_to"], "NOT_CAPTURED_IN_P0_SNAPSHOT")

    def test_market_observations_empty_array_paired_with_gap_entry(self):
        self._assert_empty_array_paired_with_gap("market_observations")

    def test_runtime_evidence_empty_array_paired_with_gap_entry(self):
        self._assert_empty_array_paired_with_gap("runtime_evidence")

    def test_no_patch_key_can_write_into_deferred_arrays(self):
        """无生产者：这两个数组没有任何 LLM patch key，也没有代码写入路径。"""
        for key in compiler.PATCH_KEYS:
            self.assertNotIn("market", key)
            self.assertNotIn("runtime", key)


class TestV0_3BackwardCompatibility(unittest.TestCase):
    def test_pre_v0_3_persisted_snapshot_upgrades_without_crashing(self):
        """向前兼容：模拟 v0.2 持久化的快照（有 account_stage 等三项，但没有 v0.3 新增的
        evidence_bundle/market_observations/gaps/runtime_evidence 四个顶层键）。main() 既有的
        升级循环遍历 _default_snapshot() 全部顶层键，应自动补齐，且不丢失旧数据。"""
        old_snapshot = {
            "schema_version": 1,
            "task_id": None,
            "revision": 5,
            "current_task": {"text": "旧会话已经存在的任务", "temporal_scope": "CYCLE", "source_ref": "USER_DIRECT"},
            "goal_structure": {"primary_goal": "旧目标", "secondary_goals": [], "priority_order": [],
                               "non_sacrifice_constraints": ["不做剧情类内容"]},
            "account_stage": {"text": "已经有稳定粉丝但没转化", "confirmation": "SYSTEM_TENTATIVE"},
            "expression_discretion": {"plot_allowed": "NOT_ALLOWED", "remix_allowed": "UNSTATED",
                                      "conflict_allowed": "UNSTATED", "controversy_allowed": "UNSTATED"},
            "capacity_triad": {"desired_output": "每周 5 条", "cycle_available": None, "baseline": None},
            "allowed_capabilities": [],
            "open_threads": [],
            "last_confirmation_signal": "NONE",
            "last_route_intent": None,
        }
        result = _run(json.dumps(old_snapshot, ensure_ascii=False), {
            "evidence_text": "我们主要卖通勤女装",
            "evidence_nature": "FACT",
        })
        snap = json.loads(result["snapshot_json"])
        self.assertEqual(snap["current_task"]["text"], "旧会话已经存在的任务", "补齐新字段不得丢失旧数据")
        self.assertEqual(snap["goal_structure"]["non_sacrifice_constraints"], ["不做剧情类内容"])
        self.assertEqual(snap["market_observations"], [])
        self.assertEqual(snap["runtime_evidence"], [])
        self.assertEqual(len(snap["evidence_bundle"]), 1)
        self.assertEqual(snap["evidence_bundle"][0]["captured_at_revision"], 5)
        self.assertTrue(snap["gaps"])

    def test_pre_v0_2_persisted_snapshot_still_upgrades(self):
        """更早的 v0.1 快照（连 account_stage 都没有）也必须能一次补齐到 v0.3。"""
        very_old = json.dumps({
            "schema_version": 1,
            "task_id": None,
            "revision": 3,
            "current_task": {"text": "很旧的任务", "temporal_scope": "UNSTATED", "source_ref": "USER_DIRECT"},
            "goal_structure": {"primary_goal": None, "secondary_goals": [], "priority_order": [],
                               "non_sacrifice_constraints": []},
            "allowed_capabilities": [],
            "open_threads": [],
            "last_confirmation_signal": "NONE",
            "last_route_intent": None,
        }, ensure_ascii=False)
        snap = json.loads(_run(very_old, {})["snapshot_json"])
        for key in compiler._default_snapshot():
            self.assertIn(key, snap)
        self.assertEqual(snap["current_task"]["text"], "很旧的任务")


class TestV0_3ContentTaskProjectionEvidence(unittest.TestCase):
    """project_content_task 的 evidence_and_gaps 从哨兵改为真实拼装（设计文档 §三：
    保留来源与确认状态，不摊平）。"""

    def test_evidence_projected_with_five_dimensions_not_flattened(self):
        result = _run(None, {
            "current_task_text": "占位任务",
            "evidence_text": "我们店在杭州",
            "evidence_nature": "FACT",
            "evidence_scope": "THIS_ACCOUNT",
        })
        snap = json.loads(result["snapshot_json"])
        ct = compiler.project_content_task(snap)
        evidence = ct["evidence_and_gaps"]["evidence"]
        self.assertEqual(len(evidence), 1)
        for dim in ("nature", "provenance", "confirmation", "scope", "availability"):
            self.assertIn(dim, evidence[0], "五维度必须逐条保留，不得摊平成一段文本")
        self.assertEqual(evidence[0]["confirmation"], "SYSTEM_TENTATIVE")

    def test_projection_gaps_full_passthrough_with_relevance_filter_registered(self):
        """P0 快照没有"本条内容"的标识符（无 item_id），任何过滤都会是编造的相关性判断，
        故如实全量透传并把"相关性过滤未实现"登记进 projection_gaps。

        投影取的是**完整视图**（include_structural=True），不是持久化快照里的动态子集
        ——设计文档 §三 要求 evidence_and_gaps 完整、不摊平。"""
        result = _run(None, {"current_task_text": "占位任务"})
        snap = json.loads(result["snapshot_json"])
        ct = compiler.project_content_task(snap)
        self.assertEqual(ct["evidence_and_gaps"]["gaps"],
                         compiler._compute_gaps(snap, include_structural=True))
        self.assertIn("evidence_and_gaps.relevance_filter", ct["projection_gaps"])
        self.assertNotIn("evidence_and_gaps", ct["projection_gaps"])

    def test_projection_gaps_include_every_structural_entry_no_information_lost(self):
        """持久化路径只留动态子集，但投影这条完整合规视图**不得因此丢信息**：8 条结构性
        常量必须全部出现（含 market_observations / runtime_evidence 这两条 DEFER 登记），
        且动态子集的每一条也都在。"""
        result = _run(None, {"current_task_text": "占位任务"})
        snap = json.loads(result["snapshot_json"])
        projected_refs = [g["field_ref"] for g in
                          compiler.project_content_task(snap)["evidence_and_gaps"]["gaps"]]
        for gap in compiler.P0_STRUCTURAL_GAPS:
            self.assertIn(gap["field_ref"], projected_refs)
        for ref in ("subject_scope", "business_goal_categories", "cycle_ref",
                    "market_observations", "runtime_evidence",
                    "account_stage.confirmation", "evidence_bundle[].confirmation",
                    "evidence_bundle[].availability"):
            self.assertIn(ref, projected_refs)
        for gap in snap["gaps"]:
            self.assertIn(gap["field_ref"], projected_refs, "动态子集不得在完整视图里丢失")

    def test_projection_recomputes_gaps_for_snapshot_without_stored_gaps(self):
        """投影可能被喂一份手工构造的、或早于 v0.3 持久化的快照；此时存量 gaps 是 [] 或缺失，
        直接透传就会输出 "gaps": []，下游只能读成"查过了，没有缺口"——那是不实主张。"""
        legacy = compiler._default_snapshot()
        del legacy["gaps"]
        ct = compiler.project_content_task(legacy)
        self.assertTrue(ct["evidence_and_gaps"]["gaps"], "缺失存量值时必须重算，不得退化成空列表")

        stale = compiler._default_snapshot()
        stale["gaps"] = []
        self.assertTrue(compiler.project_content_task(stale)["evidence_and_gaps"]["gaps"])

    def test_projection_does_not_mutate_snapshot_evidence(self):
        result = _run(None, {"evidence_text": "我们店在杭州", "evidence_nature": "FACT"})
        snap = json.loads(result["snapshot_json"])
        ct = compiler.project_content_task(snap)
        ct["evidence_and_gaps"]["evidence"][0]["confirmation"] = "USER_CONFIRMED"
        self.assertEqual(snap["evidence_bundle"][0]["confirmation"], "SYSTEM_TENTATIVE",
                          "投影必须返回副本，下游改动不得回写快照")


try:  # PyYAML 是 DSL 构建脚本的依赖，不是本测试套件的依赖
    import yaml as _yaml  # noqa: F401
    _HAS_YAML = True
except ImportError:  # pragma: no cover
    _HAS_YAML = False


@unittest.skipUnless(_HAS_YAML, "缺少 PyYAML：跳过 DSL 防漂移用例，不影响其余纯 stdlib 用例")
class TestDslSyncDriftGuard(unittest.TestCase):
    """build_m1_candidate_dsl_v0.1.py 必须与编译器手动保持同步——这是历史上唯一容易漏改的
    地方（DEFAULT_SNAPSHOT_JSON 与 structured_output.schema）。这里把它变成会失败的测试。

    该脚本模块级 import yaml 且**导入即写文件**，所以导入前把输出重定向到临时目录，
    tearDown 还原环境变量。"""

    @classmethod
    def setUpClass(cls):
        cls._prev_out = os.environ.get("M1_DSL_OUT")
        cls._tmpdir = tempfile.TemporaryDirectory()
        os.environ["M1_DSL_OUT"] = os.path.join(cls._tmpdir.name, "m1_dsl_drift_check.yml")
        path = os.path.join(_HERE, "build_m1_candidate_dsl_v0.1.py")
        spec = importlib.util.spec_from_file_location("build_m1_candidate_dsl_v0_1", path)
        cls.builder = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.builder)

    @classmethod
    def tearDownClass(cls):
        if cls._prev_out is None:
            os.environ.pop("M1_DSL_OUT", None)
        else:
            os.environ["M1_DSL_OUT"] = cls._prev_out
        cls._tmpdir.cleanup()

    def test_default_snapshot_json_matches_compiler_default(self):
        dsl_default = json.loads(self.builder.DEFAULT_SNAPSHOT_JSON)
        compiler_default = compiler._default_snapshot()
        self.assertEqual(dsl_default, compiler_default,
                          "Dify 会话变量初值必须与编译器默认快照一致，否则第一轮起点就不同")
        self.assertEqual(list(dsl_default.keys()), list(compiler_default.keys()), "键序也必须一致")

    def test_structured_output_required_matches_patch_keys(self):
        schema = None
        for n in self.builder.nodes:
            if n["id"] == "m1_shadow":
                schema = n["data"]["structured_output"]["schema"]
        self.assertIsNotNone(schema)
        self.assertEqual(set(schema["required"]), set(compiler.PATCH_KEYS))
        self.assertEqual(set(schema["properties"].keys()), set(compiler.PATCH_KEYS))

    def test_shadow_prompt_field_count_matches_patch_keys(self):
        self.assertEqual(len(compiler.PATCH_KEYS), 20)
        self.assertIn("二十个字段", self.builder.SHADOW_SYSTEM_PROMPT)

    def test_evidence_enums_in_schema_match_compiler(self):
        schema = None
        for n in self.builder.nodes:
            if n["id"] == "m1_shadow":
                schema = n["data"]["structured_output"]["schema"]
        props = schema["properties"]
        self.assertEqual(props["evidence_nature"]["enum"], compiler.VALID_EVIDENCE_NATURE_PATCH)
        self.assertEqual(props["evidence_scope"]["enum"], compiler.VALID_EVIDENCE_SCOPE)

    def test_no_nested_object_in_structured_output(self):
        """v1_shadow 已观察到的限制：DeepSeek V4 Flash 只能稳定处理扁平字符串/枚举。
        新增字段必须全部是扁平 string，不引入嵌套对象、数组或布尔。"""
        schema = None
        for n in self.builder.nodes:
            if n["id"] == "m1_shadow":
                schema = n["data"]["structured_output"]["schema"]
        for name, prop in schema["properties"].items():
            self.assertEqual(prop["type"], "string", name + " 必须是扁平字符串")


if __name__ == "__main__":
    unittest.main(verbosity=2)
