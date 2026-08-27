#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""M4 后继 Dify DSL 生成器与验证器 v0.1

task_id: V1-M4-CAPABILITY-SEAMS-RUNTIME-INTEGRATION-001

为什么用生成器而不是手写 DSL：
  AC-12 要求「源 Skill → Workflow System Prompt 正文 → 已发布实际 Prompt 字节」
  逐级可回指。生成器让 system prompt **按构造**由后继 SKILL 文件字节派生，
  保真链不依赖人工同步，也不依赖自报 hash。

用法：
  python3 decision-chain/workflows/DIYU_M4_DSL_BUILD_v0.1.py build     # 生成全部后继 DSL
  python3 decision-chain/workflows/DIYU_M4_DSL_BUILD_v0.1.py verify    # 静态验证
  python3 decision-chain/workflows/DIYU_M4_DSL_BUILD_v0.1.py bindings  # 打印 provider 绑定状态

provider 绑定：
  父接缝应用的 tool 节点需要子应用发布并注册为 workflow tool 之后才有 provider_id。
  绑定值来自 decision-chain/workflows/DIYU_M4_PROVIDER_BINDINGS.json，
  未发布时为 PENDING_PUBLISH，verify 会如实报告，**不得**据此宣称 Runtime 保真成立。
"""

import hashlib
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
DC_WF = os.path.join(ROOT, "decision-chain", "workflows")
CP_WF = os.path.join(ROOT, "content-production", "workflows")
BINDINGS = os.path.join(DC_WF, "DIYU_M4_PROVIDER_BINDINGS.json")

TASK_ID = "V1-M4-CAPABILITY-SEAMS-RUNTIME-INTEGRATION-001"
TASK_CONTRACT_HASH = "b3ceabcbe9bcd82dae2fae84161dce0f0aadd96e395a8d6fa06a3355138331c6"
APP_TAG = "M4 v1.3 TEST"

DEEPSEEK_DEP = {
    "current_identifier": None,
    "type": "marketplace",
    "value": {
        "marketplace_plugin_unique_identifier":
            "langgenius/deepseek:0.0.20@850efe73fb62bbe7ab2229116086596596297a77174fb86f73e1363b99a24116",
        "version": None,
    },
}

MODEL = {
    "completion_params": {"max_tokens": 384000, "reasoning_effort": "low", "thinking": True, "top_p": 0.8},
    "mode": "chat",
    "name": "deepseek-v4-flash",
    "provider": "langgenius/deepseek/deepseek",
}

START_ID = "1788000000001"

# --------------------------------------------------------------------------
# 能力定义
# --------------------------------------------------------------------------
# ref_load 按统一能力合同 §12 加载矩阵冻结：
#   platforms: NONE | STRUCTURAL（仅结构参数段） | PACKAGING（目标平台条目）
#   industry : NONE | BY_DOMAIN
#   examples : NEVER | ON_REQUEST
CAPABILITIES = [
    {
        "key": "matrix",
        "capability": "MATRIX",
        "entries": ["ENTRY-01"],
        "app_name": "DIYU %s · Matrix Architect" % APP_TAG,
        "tool_name": "diyu_m4_matrix",
        "skill_path": "decision-chain/skills/Matrix_Architect_v0.2_M4.md",
        "source_skill": "decision-chain/skills/Matrix_Architect_v0.1.2.md",
        "out_dir": DC_WF,
        "out_file": "DIYU_M4_TOOL_MATRIX_v1_3_TEST.yml",
        "ref_load": {"platforms": "NONE", "industry": "NONE", "examples": "NEVER"},
        "required_semantics": [
            "applicability_reason", "subject_and_account_scope", "objective",
            "facts_registered", "expression_boundary",
        ],
        "run_modes": ["DIAGNOSE_OR_ESTABLISH"],
        "produces": "长期账号架构或单账号诊断结论；账号责任卡；人格四项",
        "must_not_produce": "周期目标、内容组合、日常排期、脚本、拍摄或包装方案",
    },
    {
        "key": "campaign",
        "capability": "CAMPAIGN",
        "entries": ["ENTRY-02"],
        "app_name": "DIYU %s · Campaign Orchestrator" % APP_TAG,
        "tool_name": "diyu_m4_campaign",
        "skill_path": "decision-chain/skills/Campaign_Orchestrator_v0.2_M4.md",
        "source_skill": "decision-chain/skills/Campaign_Orchestrator_v0.1.md",
        "out_dir": DC_WF,
        "out_file": "DIYU_M4_TOOL_CAMPAIGN_v1_3_TEST.yml",
        "ref_load": {"platforms": "NONE", "industry": "NONE", "examples": "NEVER"},
        "required_semantics": [
            "objective", "deadline_or_stage_boundary", "audience_problem",
            "facts_registered", "capacity_or_owner",
        ],
        "run_modes": ["PLANNING", "COMPILE_CONFIRMED_DECISIONS"],
        "produces": "有期限的 Campaign 决策包；参战/主讲关系；不可互换表达角度；接力顺序；承接判断；统一 Content Task 出口",
        "must_not_produce": "完整脚本、逐镜分镜、成片文案",
    },
    {
        "key": "content_brief",
        "capability": "CONTENT_BRIEF",
        "entries": ["ENTRY-03"],
        "app_name": "DIYU %s · Content Brief Architect" % APP_TAG,
        "tool_name": "diyu_m4_content_brief",
        "skill_path": "decision-chain/skills/Content_Brief_Architect_v0.2_M4.md",
        "source_skill": "decision-chain/skills/Content_Brief_Architect_v0.1.md",
        "out_dir": DC_WF,
        "out_file": "DIYU_M4_TOOL_CONTENT_BRIEF_v1_3_TEST.yml",
        "ref_load": {"platforms": "NONE", "industry": "NONE", "examples": "NEVER"},
        "required_semantics": [
            "objective", "audience_problem", "expected_change", "content_promise",
            "facts_registered", "expression_subject_and_boundary",
        ],
        "run_modes": ["COMPILE_SINGLE_CONTENT_CONTRACT"],
        "produces": "单条内容生产合同：一个顾客问题 + 一个新判断 + 证据地图 + 叙事节拍 + 发布/降级/取消条件",
        "must_not_produce": "完整逐字稿、逐镜分镜、最终标题、封面、发布文案",
        # D-03（AC-28 / M4-FND-010）：判据指名了内部合同取值，产出必须落到取值本身，
        # 自然语言「权限条件未成立」不能替代。用户可见交付仍只用自然语言。
        "artifact_extra": (
            "\n4. `---M4_ARTIFACT---` 块内是否有**单独一行**写出本次的 CTA 内部合同取值：\n"
            "   `cta_contract: <取值>`\n"
            "   取值只能取自 NO_CTA / LOW_RISK_INTERACTION / BUSINESS_HANDOFF /\n"
            "   HIGH_RISK / KNOWN_BUT_NOT_AUTHORIZED。\n"
            "   权限已知但未获授权时取 `KNOWN_BUT_NOT_AUTHORIZED`（权限不全，不是信息不全）。\n"
            "   这一行只写在 ARTIFACT 块，**绝不出现在 USER_DELIVERY**。"
        ),
    },
    {
        "key": "creative_script",
        "capability": "CREATIVE_SCRIPT",
        "entries": ["ENTRY-04", "ENTRY-05"],
        "app_name": "DIYU %s · Creative Script (CS-1 + Script)" % APP_TAG,
        "tool_name": "diyu_m4_creative_script",
        "skill_path": "content-production/skills/writing-creative-scripts-m4/SKILL.md",
        "source_skill": "content-production/skills/writing-creative-scripts/SKILL.md",
        "out_dir": CP_WF,
        "out_file": "DIYU_M4_TOOL_CREATIVE_SCRIPT_v1_3_TEST.yml",
        "ref_load": {"platforms": "STRUCTURAL", "industry": "BY_DOMAIN", "examples": "ON_REQUEST"},
        "required_semantics": [
            "objective", "expected_change", "content_promise",
            "expression_subject", "content_origin_mode", "facts_registered",
        ],
        "run_modes": ["TOURNAMENT_ONLY", "SELECTED_DIRECTION_TO_SCRIPT", "FULL"],
        "produces": "创意方向（CS-1）与/或完整逐字稿 + 三区标注 + 两问表 + fact_refs 类型",
        "must_not_produce": "分镜、机位、剪辑、标题、封面、发布文案",
    },
    {
        "key": "production_director",
        "capability": "PRODUCTION_DIRECTOR",
        "entries": ["ENTRY-06"],
        "app_name": "DIYU %s · Production Director" % APP_TAG,
        "tool_name": "diyu_m4_production_director",
        "skill_path": "content-production/skills/directing-content-production-m4/SKILL.md",
        "source_skill": "content-production/skills/directing-content-production/SKILL.md",
        "out_dir": CP_WF,
        "out_file": "DIYU_M4_TOOL_PRODUCTION_DIRECTOR_v1_3_TEST.yml",
        "ref_load": {"platforms": "STRUCTURAL", "industry": "BY_DOMAIN", "examples": "ON_REQUEST"},
        "required_semantics": [
            "script_or_equivalent_beats", "content_origin_mode",
            "production_profile", "time_window", "content_promise",
        ],
        "run_modes": ["PLAN", "MANIFEST"],
        "produces": "realization_plan（七维表演指导、并置检查、降级路径）与 beat 级 realization_manifest",
        "must_not_produce": "改写脚本台词、标题、封面、发布文案、平台包装适配",
    },
    {
        "key": "publishing_packaging",
        "capability": "PUBLISHING_PACKAGING",
        "entries": ["ENTRY-07"],
        "app_name": "DIYU %s · Publishing & Packaging" % APP_TAG,
        "tool_name": "diyu_m4_publishing_packaging",
        "skill_path": "content-production/skills/packaging-content-for-release-m4/SKILL.md",
        "source_skill": "content-production/skills/packaging-content-for-release/SKILL.md",
        "out_dir": CP_WF,
        "out_file": "DIYU_M4_TOOL_PUBLISHING_PACKAGING_v1_3_TEST.yml",
        "ref_load": {"platforms": "PACKAGING", "industry": "BY_DOMAIN", "examples": "ON_REQUEST"},
        "required_semantics": [
            "content_body_or_beats", "content_promise", "explicit_non_promise",
            "facts_registered", "cta_contract", "asset_publish_permission",
        ],
        "run_modes": ["DERIVE_MODE_AND_PACKAGE"],
        "produces": "推导出的 mode（PRE/MIXED/FINAL）+ realized_payoff + 母版包 + 平台适配 + used_fact_refs",
        "must_not_produce": "重写脚本或分镜",
    },
]

CAP_BY_KEY = {c["key"]: c for c in CAPABILITIES}

# --------------------------------------------------------------------------
# 代码节点正文
# --------------------------------------------------------------------------

ENVELOPE_CHECK_CODE = r'''
import hashlib
import json
import re

# M4 统一能力接缝 · 确定性外壳校验
# 只做**结构性**充分性（在场 / 非空 / 可解析）与绑定计算。
# 语义单薄（N-34「极薄字段齐全」）的最终裁决属于业务判断，
# 由本能力的后继 Skill 正文负责；本节点只置 vacuity_flags 供其判断，
# 不代替 Skill 作专业裁决（统一能力合同 §1.2.4）。

REQUIRED = __REQUIRED_SEMANTICS__
CAPABILITY = "__CAPABILITY__"
ALLOWED_ENTRIES = __ALLOWED_ENTRIES__
ALLOWED_RUN_MODES = __ALLOWED_RUN_MODES__
DEFAULT_RUN_MODE = "__DEFAULT_RUN_MODE__"

VACUOUS = [
    "做一条好内容", "提升影响力", "让大家更了解我们", "顾客不了解我们",
    "提升曝光", "增加粉丝", "宣传新品", "促进转化", "打造心智", "多账号种草",
    "更好", "更专业", "待定", "无", "n/a", "none", "tbd",
]

GOAL_FAMILIES = ["LONG_TERM_VALUE", "ACCOUNT_STARTUP", "FOLLOWER_GROWTH", "TRAFFIC",
                 "GMV", "LEADS", "STORE_VISIT", "MIXED"]
CTA_LEVELS = ["NO_CTA", "LOW_RISK_INTERACTION", "BUSINESS_HANDOFF",
              "HIGH_RISK", "KNOWN_BUT_NOT_AUTHORIZED"]


def _sha(s):
    return hashlib.sha256((s or "").encode("utf-8")).hexdigest()


def _norm(s):
    return re.sub(r"\s+", " ", (s or "")).strip()


def _find_scalar(text, key):
    """从外壳文本里取一个标量语义值。容忍 YAML / JSON / Markdown 三种写法，
    因为统一外壳**不强制物理字段名**（统一能力合同 §1.1）。"""
    if not text:
        return ""
    pats = [
        r'"%s"\s*:\s*"([^"]*)"' % re.escape(key),
        r"^\s*%s\s*:\s*[\"']?([^\"'\n]+)[\"']?\s*$" % re.escape(key),
        r"`%s`\s*[:：]\s*([^\n]+)" % re.escape(key),
    ]
    for p in pats:
        m = re.search(p, text, re.MULTILINE)
        if m:
            return _norm(m.group(1))
    return ""


def _present(text, key):
    """语义在场判据：能取到标量值，或存在以该 key 起头的非空块。"""
    v = _find_scalar(text, key)
    if v and v.lower() not in ("", "null", "none"):
        return True, v
    m = re.search(r"^\s*%s\s*:\s*$" % re.escape(key), text or "", re.MULTILINE)
    if m:
        tail = (text or "")[m.end():]
        block = []
        for line in tail.split("\n"):
            if line.strip() == "":
                if block:
                    break
                continue
            if not line.startswith((" ", "\t", "-")):
                break
            block.append(line.strip())
        if block:
            return True, " ".join(block)[:400]
    return False, ""


def _vacuous(v):
    n = _norm(v).lower()
    if not n:
        return True
    if len(n) < 4:
        return True
    for w in VACUOUS:
        if n == w.lower():
            return True
    return False


def main(capability_call, professional_input, entry, run_mode, example_reference_requested):
    env = capability_call or ""
    prof = professional_input or ""
    blob = env + "\n" + prof

    missing = []
    vacuity_flags = []
    for key in REQUIRED:
        ok, val = _present(blob, key)
        if not ok:
            missing.append(key)
        elif _vacuous(val):
            vacuity_flags.append(key)

    # entry 解析：只接受结构化能力调用意图，不做自然语言意图识别
    entry_in = _norm(entry).upper()
    if entry_in in ALLOWED_ENTRIES:
        entry_resolved = entry_in
    elif entry_in in ("", "AUTO", "NONE"):
        entry_resolved = ALLOWED_ENTRIES[0]
    else:
        entry_resolved = "ENTRY_NOT_APPLICABLE_FOR_THIS_CAPABILITY"

    # run_mode 解析
    rm_in = _norm(run_mode).upper()
    if rm_in in ALLOWED_RUN_MODES:
        run_mode_resolved = rm_in
    else:
        run_mode_resolved = DEFAULT_RUN_MODE

    goal_family = (_find_scalar(blob, "goal_family") or "").upper()
    if goal_family not in GOAL_FAMILIES:
        goal_family = "UNDECLARED"

    cta_level = (_find_scalar(blob, "cta_level") or _find_scalar(blob, "cta_contract") or "").upper()
    if cta_level not in CTA_LEVELS:
        cta_level = "NO_CTA"

    subject_domain = _find_scalar(blob, "subject_domain")
    platform = _find_scalar(blob, "platform") or "NOT_LOCKED"
    duration_band = (_find_scalar(blob, "duration_band") or "SHORT").upper()
    equivalence_basis = _find_scalar(blob, "equivalence_basis") or "NOT_STATED"
    source_kind = (_find_scalar(blob, "source_kind") or "UNDECLARED").upper()

    if entry_resolved == "ENTRY_NOT_APPLICABLE_FOR_THIS_CAPABILITY":
        status = "INSUFFICIENT"
        note = "entry 与本能力不匹配：%s 不属于 %s" % (entry_in, ALLOWED_ENTRIES)
    elif missing:
        status = "INSUFFICIENT"
        note = "缺少完成本次判断所必需的业务语义：%s" % ", ".join(missing)
    elif vacuity_flags:
        # 结构在场但可能语义单薄：不在此处判定不足，交由 Skill 正文作专业裁决
        status = "SUFFICIENT_WITH_CONDITIONS"
        note = "结构在场；以下项疑似语义单薄，交由本能力 Skill 正文裁决：%s" % ", ".join(vacuity_flags)
    else:
        status = "SUFFICIENT"
        note = "结构性充分"

    can_run = "false" if status == "INSUFFICIENT" else "true"

    conditionalized = []
    if platform.upper() in ("NOT_LOCKED", "UNKNOWN", "未确认"):
        conditionalized.append("platform 未锁定：只产出平台中立母版，锁定平台列为条件")
    if goal_family == "UNDECLARED":
        conditionalized.append("objective.goal_family 未声明：不得代为推断，按未声明处理并在产出中标注")
    if vacuity_flags:
        conditionalized.append("疑似语义单薄项：%s" % ", ".join(vacuity_flags))

    return {
        "status": status,
        "can_run": can_run,
        "note": note,
        "missing": missing,
        "missing_text": ", ".join(missing) if missing else "无",
        "vacuity_flags": vacuity_flags,
        "conditionalized_text": "；".join(conditionalized) if conditionalized else "无",
        "entry_resolved": entry_resolved,
        "run_mode_resolved": run_mode_resolved,
        "goal_family": goal_family,
        "cta_level": cta_level,
        "source_kind": source_kind,
        "subject_domain": subject_domain,
        "platform": platform,
        "duration_band": duration_band,
        "equivalence_basis": equivalence_basis,
        "envelope_hash": _sha(env),
        "professional_input_hash": _sha(prof),
        "capability": CAPABILITY,
        "example_reference_requested": _norm(example_reference_requested).upper(),
    }
'''

COMPONENT_RETURN_CODE = r'''
import json

# 组件级 Return（统一能力合同 §10.1 七项）
# 关键语义：这是**本分支结果**，不是整任务终态；本身不触发下游失效。
# 硬禁：全局硬停、生成假产物、要求用户重填整套输入。

CAPABILITY = "__CAPABILITY__"
LAYER = "__RETURN_LAYER__"

# 用户交付里**不得出现内部字段名**（AC-13 / N-23）。
# 缺项到自然语言追问的映射是确定性的，不含业务判断。
QUESTION_MAP = {
    "applicability_reason": "这次是要新建或实质改动账号的长期定位、人设或职责分工吗？还是只想解决眼下这一条内容？",
    "subject_and_account_scope": "这次要处理的是哪个品牌／哪几个账号？",
    "objective": "这一轮你想拿到的结果是什么？（比如让人看懂某个判断、涨粉、带来到店咨询）",
    "audience_problem": "你想说给谁听？她现在具体卡在哪一步？",
    "expected_change": "看完之后，你希望她多知道什么、或者能做什么决定？",
    "content_promise": "这条内容对观众的承诺是什么？（一句话说清她能拿到什么）",
    "expression_boundary": "有哪些话是这个品牌明确不能说的？",
    "expression_subject_and_boundary": "这条由谁来讲？她能讲的和不能讲的边界是什么？",
    "expression_subject": "这条由谁来讲？（真人／角色／品牌口吻／只拍物件／无主体）",
    "facts_registered": "有哪些已经记下来的真实事实或亲历观察可以用？（没有登记的事实我不能替你补）",
    "deadline_or_stage_boundary": "这件事有明确的时间或阶段边界吗？到什么时候为止？",
    "capacity_or_owner": "这一轮谁能出镜、谁能确认事实、大概能投入多少时间？",
    "content_origin_mode": "这条的素材是现拍、用已有素材剪、访谈、还是生成的？（这项猜错整条会作废，我不替你默认）",
    "script_or_equivalent_beats": "把脚本或等价的内容方案给我：每一段讲什么、事实有没有、素材到位没有。",
    "production_profile": "这次是单人手机、一两个人、小团队，还是商业制作？",
    "time_window": "这次有多少时间可用？（半天／两天／几个天光窗口）",
    "content_body_or_beats": "把成片内容或逐段说明给我：每一段实际拍到了什么。",
    "explicit_non_promise": "这条明确**不**承诺什么？（这一项下游最容易悄悄加回来）",
    "cta_contract": "这条要不要引导观众做什么？如果要，做什么、谁在哪里接？",
    "asset_publish_permission": "这些素材可以公开发布吗？有没有第三方入镜或授权限制？",
}


def main(status, note, missing, entry_resolved, envelope_hash, capability_call):
    miss = missing or []
    # 只追问当前最具区分力的一项，并翻译成自然语言（不向用户暴露内部字段名）
    ask_key = miss[0] if miss else ""
    ask_one = QUESTION_MAP.get(ask_key, "") if ask_key else ""
    if not ask_one:
        ask_one = "还差一项才能做判断，你能补一句说明吗？"

    ret = {
        "return_id": "M4-RET-%s-%s" % (CAPABILITY, (envelope_hash or "0" * 8)[:8]),
        "source": CAPABILITY,
        "highest_damaged_layer": LAYER,
        "precise_gap": "；".join(miss) if miss else (note or "未指明"),
        "affected_objects": ["仅本次 %s 调用及其真实依赖分支" % CAPABILITY],
        "proposed_disposition": "ESCALATE",
        "needs_user_decision": True,
        "downstream_stale": ["仅真实依赖本次 %s 结论的下游项" % CAPABILITY],
        "parse_status": "OK",
    }

    user_text = (
        "这一步我还差一样东西才能往下判断：\n\n%s\n\n"
        "只补这一项就够了，其他已经给过的内容不用再说一遍。\n"
        "这一轮里不依赖这一步的其他事情不受影响，可以照常继续。" % ask_one
    )

    # 机械自检：用户交付里不得出现任何内部字段名（AC-13 / N-23）
    leaked = [k for k in QUESTION_MAP if k in user_text]

    return {
        "returns_json": json.dumps([ret], ensure_ascii=False),
        "user_delivery_leaks": leaked,
        "return_status": "COMPONENT_RETURN",
        "branch_result": "INPUT_INSUFFICIENT",
        "is_task_terminal_state": "false",
        "triggers_downstream_invalidation": "false",
        "single_most_discriminating_question": ask_one,
        "user_delivery": user_text,
        "fabricated_artifact_produced": "false",
        "downstream_invoked": "false",
    }
'''

RETURNS_ADAPTER_CODE = r'''
import json
import re

# 确定性 Returns / 交付分离适配器
# N-12 铁律：解析失败 != NONE。结构损坏时置 PARSE_FAILED、保留原文、局部阻断，
#           绝不伪装成空数组或 NONE。

CAPABILITY = "__CAPABILITY__"

A_OPEN, A_CLOSE = "---M4_ARTIFACT---", "---END_M4_ARTIFACT---"
U_OPEN, U_CLOSE = "---M4_USER_DELIVERY---", "---END_M4_USER_DELIVERY---"
R_OPEN, R_CLOSE = "---M4_RETURNS---", "---END_M4_RETURNS---"

RET_FIELDS = ["return_id", "source", "highest_damaged_layer", "precise_gap",
              "affected_objects", "proposed_disposition", "needs_user_decision",
              "downstream_stale"]
DISPOSITIONS = ["ACCEPT_AND_PATCH", "REJECT_WITH_AUTHORITY", "ESCALATE"]

# 用户交付块禁项（统一能力合同 §11.3 / 源 PP Skill「用户交付块的事实纪律」）
LEAK_PATTERNS = [
    "已删除", "已剔除", "已移除", "审查发现", "审查时发现", "修正后", "修正为",
    "原方案", "上一版", "之前的版本", "未核实，不得使用", "这句话不能使用",
    "LOW_RISK_INTERACTION", "BUSINESS_HANDOFF", "KNOWN_BUT_NOT_AUTHORIZED",
    "goal_family", "capability_call", "professional_payload", "system prompt",
    "INPUT_INSUFFICIENT", "STALE", "NOT_VERIFIED", "fact_refs[]", "used_fact_refs",
]


# AC-31 产出完整性冻结阈值（V1_M4_EVIDENCE_COLLECTION_CONTRACT_v0.2 §1.1）
# 阈值在任何新运行之前冻结，不因结果调整。
BACKREF_MARKERS = ["即上方", "即以上", "同上", "同上文", "上方即", "上文即",
                   "见上文", "如上所述", "内容同上", "本区块与",
                   "与上方", "与上文", "与以上"]
MIN_ARTIFACT_CHARS = 400
CHECK_WINDOW = 200


def _has_backref(text):
    head = (text or "")[:CHECK_WINDOW]
    for m in BACKREF_MARKERS:
        if m in head:
            return True
    return False


def _legit_block(rets):
    # 合法组件级 Return：同时含非空 highest_damaged_layer 与非空 precise_gap
    for r in rets:
        if not isinstance(r, dict):
            continue
        if (r.get("highest_damaged_layer") or "").strip() and (r.get("precise_gap") or "").strip():
            return True
    return False


def _artifact_status(artifact, rets):
    a = (artifact or "").strip()
    if _has_backref(a):
        return "BACKREF_COLLAPSED"
    if not a:
        return "OK" if _legit_block(rets) else "EMPTY"
    if len(a) < MIN_ARTIFACT_CHARS and not _legit_block(rets):
        return "BELOW_MIN"
    return "OK"


def _user_status_of(user_delivery):
    # 空交付无条件违规：legit_block 时用户仍必须被告知阻断
    u = (user_delivery or "").strip()
    if not u:
        return "EMPTY"
    if _has_backref(u):
        return "BACKREF_COLLAPSED"
    return "OK"


def _between(text, a, b):
    i = text.find(a)
    if i < 0:
        return None
    j = text.find(b, i + len(a))
    if j < 0:
        return None
    return text[i + len(a):j].strip()


def _parse_returns(block):
    """返回 (list, status, note)。status ∈ OK | NONE | PARSE_FAILED"""
    if block is None:
        return [], "PARSE_FAILED", "缺少 RETURNS 块，无法判定是无回改还是产出被截断"
    s = block.strip()
    if s == "":
        return [], "PARSE_FAILED", "RETURNS 块为空。空 != NONE：无回改必须显式写 NONE"
    if s.upper() == "NONE":
        return [], "NONE", "显式声明无回改"

    groups = [g for g in re.split(r"\n\s*\n", s) if g.strip()]
    out = []
    bad = []
    for g in groups:
        item = {}
        for line in g.split("\n"):
            m = re.match(r"^\s*([a-z_]+)\s*:\s*(.*)$", line)
            if m:
                item[m.group(1)] = m.group(2).strip()
        miss = [f for f in RET_FIELDS if f not in item or item[f] == ""]
        if miss:
            bad.append("一条 Return 缺字段：%s" % ",".join(miss))
            continue
        if item["proposed_disposition"] not in DISPOSITIONS:
            bad.append("proposed_disposition 非法：%s" % item["proposed_disposition"])
            continue
        item["affected_objects"] = [x.strip() for x in item["affected_objects"].split("|") if x.strip()]
        item["downstream_stale"] = [x.strip() for x in item["downstream_stale"].split("|") if x.strip()]
        item["needs_user_decision"] = item["needs_user_decision"].strip().lower() in ("true", "是", "yes")
        item["parse_status"] = "OK"
        out.append(item)

    if bad:
        return out, "PARSE_FAILED", "；".join(bad)
    if not out:
        return [], "PARSE_FAILED", "RETURNS 块存在内容但无法解析出任何合法条目"
    return out, "OK", "解析出 %d 条" % len(out)


def main(final_text):
    raw = final_text or ""

    artifact = _between(raw, A_OPEN, A_CLOSE)
    user_delivery = _between(raw, U_OPEN, U_CLOSE)
    returns_block = _between(raw, R_OPEN, R_CLOSE)

    structure_notes = []
    if artifact is None:
        structure_notes.append("缺少 ARTIFACT 块")
    if user_delivery is None:
        structure_notes.append("缺少 USER_DELIVERY 块")

    rets, ret_status, ret_note = _parse_returns(returns_block)

    leaks = [p for p in LEAK_PATTERNS if user_delivery and p in user_delivery]

    if artifact is None:
        artifact_out = raw if raw.strip() else "MODEL_OUTPUT_NO_FINAL"
        artifact_status = "STRUCTURE_MISSING_RAW_PRESERVED"
    else:
        artifact_out = artifact
        artifact_status = _artifact_status(artifact, rets)

    if user_delivery is None:
        user_out = ""
        user_status = "MISSING"
    elif leaks:
        user_out = user_delivery
        user_status = "LEAK_DETECTED"
    else:
        user_out = user_delivery
        user_status = _user_status_of(user_delivery)

    blocked = (
        ret_status == "PARSE_FAILED"
        or artifact_status != "OK"
        or user_status != "OK"
    )

    # AC-31 修复：专业内容已生成但用户交付块缺失/为空/回指 ⇒ 需要一次有界用户投影。
    # 判据来自取证判据合同 v0.2 §1.1 的冻结阈值，不新增业务事实。
    _sub = (artifact_out or "").strip()
    _needs = (user_status != "OK" or not (user_out or "").strip()) and len(_sub) >= MIN_ARTIFACT_CHARS

    return {
        "artifact": artifact_out,
        "artifact_status": artifact_status,
        "needs_projection": "true" if _needs else "false",
        "projection_source": _sub if _needs else "",
        "user_delivery": user_out,
        "user_delivery_status": user_status,
        "user_delivery_leaks": leaks,
        "returns_json": json.dumps(rets, ensure_ascii=False),
        "returns_status": ret_status,
        "returns_parse_note": ret_note,
        "returns_raw": returns_block if returns_block is not None else "ABSENT",
        "raw_preserved": raw,
        "local_block": "true" if blocked else "false",
        "structure_notes": structure_notes,
        "capability": CAPABILITY,
    }
'''

RECOVERY_PROJECTION_PROMPT = """你要做的**只有一件事**：把下面这份已经写好的专业产出，投影成一份**给用户看的自然语言正文**。

## 硬约束

1. **不得新增任何业务事实。** 只能用下面这份产出里已经存在的内容。产出里没有的商品、价格、面料、顾客、数字、平台数据，一个都不许补。
2. **不得重新做一次专业生产。** 不重新判断、不换方向、不补候选、不改结论。你不是在写一份新的产出，你是在把已有的产出讲给用户听。
3. **不得把整份原文抄过来。** 用户要的是能读、能判断、能据此行动的那部分，不是内部留档。
4. **不得出现任何内部技术词**：字段名、状态码、节点名、哈希、trace、系统提示、自检过程、被淘汰的候选及其淘汰原因、`PARSE_FAIL`、`NOT_APPLICABLE`、`STALE` 之类。
5. **不得省掉用户必须知道的东西**：结论、成立条件、限制、必要的选择、下一步。「不泄露内部」不等于「少给用户」。
6. 如果原文本身就是一次**阻断**（资料不足、权限不成立、无法安全产出），那就如实把阻断讲清楚：缺什么、为什么卡住、需要补什么，用自然语言说。

## 写法

- 直接开始写正文，不要写「好的」「以下是」这类开场；
- 不要标题党，不要总结这份任务；
- 该分段就分段，该列点就列点；
- 用用户能懂的话，不用工程化表达。

## 已写好的专业产出

{{#returns_adapter.projection_source#}}
"""


DELIVERY_FINALIZE_CODE = r'''
import json

# AC-31 交付收口：无论走哪条路径，用户都必须拿到非空正文。
# 技术运行 succeeded != 业务交付成功；两者在此显式分离。

LEAK = ["PARSE_FAIL", "SEAM_COMPLETENESS_GUARD", "NOT_APPLICABLE", "STALE",
        "NOT_VERIFIED", "returns_json", "artifact_status", "user_delivery_status",
        "system prompt", "goal_family", "capability_call", "professional_payload",
        # M4-FND-029：恢复正文里绝不允许出现模型的内部推理段
        "<think>", "</think>", "dify-deepseek-reasoning"]


def _strip_thinking(text):
    """剥离模型 thinking 段，取最终正文。

    缺陷 M4-FND-029：专业链的 final_extract 会做这一步，但 v1.4 新增的恢复路径没有做，
    于是 recovery_llm 的整段内部推理被原样当成用户正文交付出去。
    该缺陷此前无法被发现——recovery_llm 在 v1.4 的 13 次 Runtime 运行中触发 0 次。
    剥离规则与 final_extract 模板逐条等价，不另立第二套。
    """
    raw = (text or "").strip()
    if "</think>" in raw:
        return raw.split("</think>")[-1].strip()
    return raw


def main(adapter_user_delivery, adapter_status, needs_projection,
         recovered_text, returns_json, capability):
    ud = (adapter_user_delivery or "").strip()
    rec = _strip_thinking(recovered_text)
    need = str(needs_projection or "").strip().lower() == "true"

    try:
        rets = json.loads(returns_json or "[]")
    except Exception:
        rets = []

    if not need and ud:
        return {"user_delivery": ud, "delivery_outcome": "DELIVERED",
                "user_delivery_status": adapter_status or "OK",
                "returns_json": returns_json or "[]",
                "recovery_used": "false"}

    # ── 有界局部恢复：最多一次，已在上游完成 ──
    if rec and len(rec) >= 80:
        leaked = [w for w in LEAK if w in rec]
        if not leaked:
            return {"user_delivery": rec, "delivery_outcome": "DELIVERED_AFTER_RECOVERY",
                    "user_delivery_status": "RECOVERED",
                    "returns_json": json.dumps(rets + [{
                        "return_id": "M4-RET-PROJECTION-RECOVERED",
                        "source": "DELIVERY_FINALIZE",
                        "highest_damaged_layer": "OUTPUT_CONTRACT_BLOCK_MARKERS",
                        "precise_gap": "模型未输出用户交付块标记；已由一次有界用户投影补齐",
                        "affected_objects": ["本次 %s 调用的用户交付块" % capability],
                        "proposed_disposition": "ACCEPT_AND_PATCH",
                        "needs_user_decision": False,
                        "downstream_stale": [],
                        "parse_status": "RECOVERED_ONCE",
                    }], ensure_ascii=False),
                    "recovery_used": "true"}

    # ── 恢复失败：仍然必须给用户非空自然语言说明，且业务状态不是成功 ──
    msg = (
        "这一次没有成功给出可用的结果。\n\n"
        "系统在内部已经把专业判断做出来了，但在整理成给你看的那一份时出了问题，"
        "没能形成一份可以直接用的正文。\n\n"
        "**这次不算交付成功**——请不要把上面的空白当成「没有结论」，"
        "结论是有的，是整理环节断了。\n\n"
        "你可以把同样的需求再提一次；如果第二次仍然这样，说明这条路径上有需要修的问题，"
        "请把这次的情况反馈出来。"
    )
    return {"user_delivery": msg, "delivery_outcome": "NOT_DELIVERED",
            "user_delivery_status": "PROJECTION_FAILED",
            "returns_json": json.dumps(rets + [{
                "return_id": "M4-RET-PROJECTION-FAILED",
                "source": "DELIVERY_FINALIZE",
                "highest_damaged_layer": "OUTPUT_CONTRACT_BLOCK_MARKERS",
                "precise_gap": "用户交付块缺失，且一次有界投影未产出可用正文",
                "affected_objects": ["本次 %s 调用的用户交付块" % capability],
                "proposed_disposition": "ESCALATE",
                "needs_user_decision": True,
                "downstream_stale": ["仅真实依赖本次 %s 产出的下游项" % capability],
                "parse_status": "PROJECTION_FAILED",
            }], ensure_ascii=False),
            "recovery_used": "attempted"}
'''


BINDING_RECORD_CODE = r'''
import hashlib
import json

# AC-12 保真绑定记录（源 Skill → Workflow → Runtime → 模型 → provider → Attempt）
# 自报值只作声明；正式判定以从已发布 Runtime 实际读出的字节为准（N-19）。

# 注意：这里必须走 json.loads，不能把 json.dumps 的结果直接当 Python 字面量贴进来。
# 现场教训（2026-08-26）：直接贴会把 Python 的 True 写成 JSON 的 true，
# 代码节点一进沙箱就 NameError: name 'true' is not defined，整个能力应用调不起来。
RECORD = json.loads(__BINDING_RECORD_JSON__)


def main(envelope_hash, professional_input_hash, artifact, reference_projection,
         entry_resolved, run_mode_resolved, goal_family):
    art = artifact or ""
    rec = dict(RECORD)
    rec["input_envelope_sha256"] = envelope_hash
    rec["input_professional_sha256"] = professional_input_hash
    rec["artifact_sha256"] = hashlib.sha256(art.encode("utf-8")).hexdigest()
    rec["reference_projection_declared"] = reference_projection
    rec["entry"] = entry_resolved
    rec["run_mode"] = run_mode_resolved
    rec["goal_family_readonly_inherited"] = goal_family
    rec["self_reported_only"] = True
    rec["note"] = (
        "自报 hash 不构成保真证明。AC-12 以从已发布 Runtime 实际读出的 "
        "system prompt 字节 sha256 为准；两者不一致时以实际字节为准并判 FAIL（N-19）。"
    )
    return {"binding_json": json.dumps(rec, ensure_ascii=False, sort_keys=True)}
'''

ENTRY_RESOLVER_CODE = r'''
import hashlib
import json
import re

# M4 统一能力接缝 · 入口解析器
#
# 这里**不是路由**。M1 负责自然语言理解与跨诉求路由，并给出唯一能力调用意图。
# 本节点只做两件事：
#   1. 接收已结构化的能力调用意图（capability + 可选 entry）；
#   2. entry 缺省时，按统一能力合同 §2.3 的**确定性充分性规则**推导同一能力内部的运行模式。
# 它不读自然语言、不做意图判断、不选择能力。

CAPS = ["MATRIX", "CAMPAIGN", "CONTENT_BRIEF", "CREATIVE_SCRIPT",
        "PRODUCTION_DIRECTOR", "PUBLISHING_PACKAGING"]

CAP_TO_ENTRY = {
    "MATRIX": "ENTRY-01",
    "CAMPAIGN": "ENTRY-02",
    "CONTENT_BRIEF": "ENTRY-03",
    "PRODUCTION_DIRECTOR": "ENTRY-06",
    "PUBLISHING_PACKAGING": "ENTRY-07",
}

FIVE_AXES = ["核心矛盾", "叙事发动机", "人物关系", "信息释放顺序", "视觉前提"]


def _norm(s):
    return re.sub(r"\s+", " ", (s or "")).strip()


def _find(text, key):
    for p in [r'"%s"\s*:\s*"([^"]*)"' % re.escape(key),
              r"^\s*%s\s*:\s*[\"']?([^\"'\n]+)[\"']?\s*$" % re.escape(key),
              r"`%s`\s*[:：]\s*([^\n]+)" % re.escape(key)]:
        m = re.search(p, text or "", re.MULTILINE)
        if m:
            return _norm(m.group(1))
    return ""


def _axis_diff_count(text):
    """确定性统计：候选描述里出现了几个结构轴的显式差异标注。
    只用于判断『是否存在真实取舍』的**结构前提**；
    差异是否实质由 CS-1 在 Skill 正文里裁决（业务判断不入外壳）。"""
    return sum(1 for a in FIVE_AXES if a in (text or ""))


def main(capability, entry, capability_call, professional_input):
    cap = _norm(capability).upper()
    blob = (capability_call or "") + "\n" + (professional_input or "")

    if cap not in CAPS:
        return {
            "route": "UNSUPPORTED",
            "capability_resolved": cap or "MISSING",
            "entry_resolved": "NONE",
            "run_mode": "NONE",
            "derivation": "capability 不在 M4 接缝支持的六项能力内。M4 不代做能力选择（那是 M1 的职责）。",
            "call_hash": hashlib.sha256(blob.encode("utf-8")).hexdigest(),
        }

    e = _norm(entry).upper()
    if e.startswith("ENTRY"):
        entry_resolved = e
        derivation = "entry 由上游能力调用意图显式给出，未做任何推导"
    elif cap == "CREATIVE_SCRIPT":
        accepted = _find(blob, "accepted_direction")
        if accepted and accepted.upper() not in ("", "NONE", "NULL"):
            entry_resolved = "ENTRY-05"
            derivation = "已存在 accepted_direction ⇒ 直达脚本（不重开锦标赛）"
        elif _axis_diff_count(blob) >= 3:
            entry_resolved = "ENTRY-04"
            derivation = "输入结构上显示至少三个结构轴的候选差异标注 ⇒ 进入 CS-1；差异是否实质由 CS-1 正文裁决"
        else:
            entry_resolved = "ENTRY-05"
            derivation = "未发现真实取舍的结构前提 ⇒ 直接推荐一个方向并成稿，不机械凑候选"
    else:
        entry_resolved = CAP_TO_ENTRY[cap]
        derivation = "该能力只有一个直接入口，按能力确定性映射"

    if cap == "CREATIVE_SCRIPT":
        run_mode = "TOURNAMENT_ONLY" if entry_resolved == "ENTRY-04" else "SELECTED_DIRECTION_TO_SCRIPT"
    elif cap == "CAMPAIGN":
        confirmed = _find(blob, "campaign_run_mode").upper()
        run_mode = "COMPILE_CONFIRMED_DECISIONS" if confirmed == "COMPILE_CONFIRMED_DECISIONS" else "PLANNING"
    elif cap == "PRODUCTION_DIRECTOR":
        run_mode = "MANIFEST" if "realization_manifest" in blob else "PLAN"
    else:
        run_mode = "DEFAULT"

    return {
        "route": cap,
        "capability_resolved": cap,
        "entry_resolved": entry_resolved,
        "run_mode": run_mode,
        "derivation": derivation,
        "call_hash": hashlib.sha256(blob.encode("utf-8")).hexdigest(),
    }
'''

SEAM_FINALIZE_CODE = r'''
import json

# 接缝收口：记录实际调用了哪一个能力、跳过了哪些、失效集怎么算。
# A3：INVALIDATED = changed_bindings ∪ transitive_dependents ∪ unknown_dependency_items

ALL_CAPS = ["MATRIX", "CAMPAIGN", "CONTENT_BRIEF", "CREATIVE_SCRIPT",
            "PRODUCTION_DIRECTOR", "PUBLISHING_PACKAGING"]


def main(capability_resolved, entry_resolved, run_mode, derivation,
         tool_artifact, tool_user_delivery, tool_returns_json, tool_binding_json, call_hash,
         tool_local_block, tool_artifact_status, tool_user_delivery_status,
         tool_delivery_outcome, tool_recovery_used):
    invoked = [capability_resolved]
    skipped = [c for c in ALL_CAPS if c != capability_resolved]

    try:
        rets = json.loads(tool_returns_json or "[]")
    except Exception:
        rets = []

    # D-01b（AC-31 合取项③）：Tool 已算出的阻断信号必须端到端生效。
    # 缺陷 M4-FND-012：此前 local_block / *_status 被计算后在本节点整体丢弃，
    # 产出塌陷因此被 tool_artifact or "" 静默放行为成功。
    guard = {
        "checked": True,
        "tool_local_block": tool_local_block,
        "artifact_status": tool_artifact_status,
        "user_delivery_status": tool_user_delivery_status,
        # v1.4：Dify 技术运行状态与 M4 业务交付状态必须分开表达（取证合同 v0.4 §3 RB31-04⑦）
        "business_delivery_outcome": tool_delivery_outcome or "UNKNOWN",
        "user_projection_used": tool_recovery_used or "false",
    }

    # 业务交付失败时，即使平台技术状态为 succeeded，也必须登记为未成功交付
    if str(tool_delivery_outcome or "").strip().upper() == "NOT_DELIVERED":
        rets = list(rets) + [{
            "return_id": "M4-RET-NOT-DELIVERED-" + str(call_hash or "")[:8],
            "source": "SEAM_DELIVERY_OUTCOME",
            "highest_damaged_layer": "USER_DELIVERY_PROJECTION",
            "precise_gap": "本次未形成成功的用户交付；平台技术状态不代表业务交付成功",
            "affected_objects": ["本次 %s 调用的用户交付" % capability_resolved],
            "proposed_disposition": "ESCALATE",
            "needs_user_decision": True,
            "downstream_stale": ["仅真实依赖本次 %s 用户交付的下游项" % capability_resolved],
            "parse_status": "NOT_DELIVERED",
        }]

    if str(tool_local_block or "").strip().lower() == "true":
        gaps = [x for x in (tool_artifact_status, tool_user_delivery_status)
                if x and x != "OK"]
        rets = list(rets) + [{
            "return_id": "M4-RET-SEAM-COMPLETENESS-" + str(call_hash or "")[:8],
            "source": "SEAM_COMPLETENESS_GUARD",
            "highest_damaged_layer": "CAPABILITY_OUTPUT_COMPLETENESS",
            "precise_gap": " | ".join(gaps) if gaps else "local_block=true 但状态未指明",
            "affected_objects": ["本次 %s 调用的产出块" % capability_resolved],
            "proposed_disposition": "ESCALATE",
            "needs_user_decision": True,
            "downstream_stale": ["仅真实依赖本次 %s 产出的下游项" % capability_resolved],
            "parse_status": "PARSE_FAIL",
        }]
        returns_out = json.dumps(rets, ensure_ascii=False)
    else:
        returns_out = tool_returns_json or "[]"

    stale = []
    for r in rets:
        if isinstance(r, dict):
            stale.extend(r.get("downstream_stale") or [])

    trace = {
        "call_hash": call_hash,
        "capability_invoked": invoked,
        "capabilities_skipped_because_not_applicable_or_equivalent_input_satisfied": skipped,
        "entry": entry_resolved,
        "run_mode": run_mode,
        "entry_derivation": derivation,
        "upstream_auto_invoked": [],
        "upstream_auto_invoked_note": (
            "M4 六个能力应用之间零 tool 调用边；组合只由本接缝按显式 plan 编排。"
            "本次未暗跑任何上游能力。"
        ),
        "stale_set": stale,
        "stale_rule": "只使直接依赖、传递依赖与影响关系未知项 STALE；有证据不受影响的项继续复用",
        "completeness_guard": guard,
    }

    # ── CL31-01②：本终止分支的用户正文不得为空 ──────────────────────────
    # 子应用的 delivery_finalize 已保证非空；但接缝不得依赖上游承诺，
    # 一旦读回空值必须自己兜底，并且**不得**把技术执行完成冒充业务交付成功。
    ud = (tool_user_delivery or "").strip()
    outcome = str(tool_delivery_outcome or "").strip().upper() or "UNKNOWN"
    if not ud:
        ud = (
            "这一次没有拿到可以给你看的结果。\n\n"
            "内部这一步跑完了，但回到我这里时正文是空的，我没有可以转述的内容，"
            "也不会替它补一份看起来像结果的东西。\n\n"
            "**这不算一次成功交付**——请不要把这段空白理解成「没有结论」，"
            "而是这一轮的结果没有正常传回来。\n\n"
            "你可以把同样的需求原样再提一次；如果第二次仍然这样，请把这次的情况反馈出来。\n\n"
            "这一轮里不依赖这一步的其他事情不受影响，可以照常继续。"
        )
        outcome = "NOT_DELIVERED"
        rets = list(rets) + [{
            "return_id": "M4-RET-SEAM-EMPTY-DELIVERY-" + str(call_hash or "")[:8],
            "source": "SEAM_EMPTY_USER_DELIVERY",
            "highest_damaged_layer": "USER_DELIVERY_TRANSPORT",
            "precise_gap": "子能力返回的用户正文为空；接缝已兜底为非空失败说明，不冒充成功",
            "affected_objects": ["本次 %s 调用的用户交付" % capability_resolved],
            "proposed_disposition": "ESCALATE",
            "needs_user_decision": True,
            "downstream_stale": ["仅真实依赖本次 %s 用户交付的下游项" % capability_resolved],
            "parse_status": "NOT_DELIVERED",
        }]
        returns_out = json.dumps(rets, ensure_ascii=False)
        trace["completeness_guard"]["business_delivery_outcome"] = "NOT_DELIVERED"
        trace["completeness_guard"]["seam_empty_delivery_fallback_used"] = True

    return {
        "seam_trace_json": json.dumps(trace, ensure_ascii=False, sort_keys=True),
        "capability_invoked": capability_resolved,
        "capabilities_skipped": skipped,
        "artifact": tool_artifact or "",
        "user_delivery": ud,
        "business_delivery_outcome": outcome,
        "returns_json": returns_out,
        "binding_json": tool_binding_json or "{}",
    }
'''


# --------------------------------------------------------------------------
# 接缝失败终止分支（CL31-01 / CL31-02）
# 纪律：失败也必须给用户非空、可读、不含内部词的正文；
#       平台技术状态与业务交付状态显式分离，不以 succeeded 冒充业务成功。
# --------------------------------------------------------------------------

SEAM_TOOL_FAIL_CODE = r'''
import json

# 能力中文名映射是确定性的、不含业务判断；用于避免把内部能力标识写给用户。
CAP_LABEL = {
    "MATRIX": "账号架构与诊断",
    "CAMPAIGN": "单次经营任务策划",
    "CONTENT_BRIEF": "内容任务判断",
    "CREATIVE_SCRIPT": "创意与脚本",
    "PRODUCTION_DIRECTOR": "拍摄执行方案",
    "PUBLISHING_PACKAGING": "发布包装",
}


def main(route, derivation):
    key = (route or "").strip().upper()
    label = CAP_LABEL.get(key, "这一步")
    user_text = (
        "这一次没有把结果做出来。\n\n"
        "「%s」这一步在运行中没有跑通，所以这一轮没有产出可用的结论。"
        "**这不算一次成功交付**——我也没有替它编一份看起来像结果的东西给你。\n\n"
        "这不是你给的信息不够，你不需要重新整理一遍需求。\n\n"
        "你现在可以做的是：把同样的需求原样再提一次。"
        "如果第二次还是这样，说明这条路上有需要修的问题，请把这次的情况反馈出来。\n\n"
        "这一轮里不依赖这一步的其他事情不受影响，可以照常继续。" % label
    )
    ret = {
        "return_id": "M4-RET-TOOL-CALL-FAILED-" + (key or "UNKNOWN"),
        "source": "SEAM_TOOL_FAIL",
        "highest_damaged_layer": "CAPABILITY_APP_EXECUTION",
        "precise_gap": "能力应用调用失败；这是执行失败，不是业务输入不足，也不是空结果",
        "affected_objects": ["仅本次 %s 调用及其真实依赖分支" % (key or "UNKNOWN")],
        "proposed_disposition": "ESCALATE",
        "needs_user_decision": True,
        "downstream_stale": ["仅真实依赖本次 %s 结论的下游项" % (key or "UNKNOWN")],
        "parse_status": "NOT_DELIVERED",
    }
    return {
        "failure_kind": "TOOL_CALL_FAILED",
        "note": ("能力应用调用失败。这是执行失败，不是业务不足："
                 "不得伪装成 INPUT_INSUFFICIENT，也不得伪装成空结果。"),
        "capability": route,
        "derivation": derivation,
        "fabricated_artifact_produced": "false",
        "user_delivery": user_text,
        "business_delivery_outcome": "NOT_DELIVERED",
        "returns_json": json.dumps([ret], ensure_ascii=False),
    }
'''


SEAM_UNSUPPORTED_CODE = r'''
import json


def main(route, derivation):
    key = (route or "").strip().upper()
    user_text = (
        "这一次我没有往下做。\n\n"
        "你要的这件事不在我这一层能处理的范围里。我能做的是这六件："
        "账号架构与诊断、单次经营任务策划、内容任务判断、创意与脚本、拍摄执行方案、发布包装。\n\n"
        "**这不算一次成功交付**——我没有硬凑一个看起来相关的结果给你，"
        "也不替你决定该做上面哪一件，那不是我该替你拿的主意。\n\n"
        "你可以直接说明这次想解决的是上面哪一件；"
        "如果都不是，把你想拿到的结果说清楚，我再看接不接得住。"
    )
    ret = {
        "return_id": "M4-RET-UNSUPPORTED-" + (key or "UNKNOWN"),
        "source": "SEAM_UNSUPPORTED",
        "highest_damaged_layer": "CAPABILITY_SELECTION",
        "precise_gap": "能力调用意图不在本接缝支持的六项能力内；本接缝不代做能力选择",
        "affected_objects": ["仅本次调用意图"],
        "proposed_disposition": "ESCALATE",
        "needs_user_decision": True,
        "downstream_stale": [],
        "parse_status": "NOT_DELIVERED",
    }
    return {
        "note": ("capability 不在 M4 接缝支持的六项能力内。"
                 "M4 不代做能力选择——那是 M1 的职责；本接缝也不建第二套路由。"),
        "capability": route,
        "derivation": derivation,
        "user_delivery": user_text,
        "business_delivery_outcome": "NOT_DELIVERED",
        "returns_json": json.dumps([ret], ensure_ascii=False),
    }
'''


# --------------------------------------------------------------------------
# reference 投影模板（确定性，按统一能力合同 §12 加载矩阵）
# --------------------------------------------------------------------------

def ref_projection_template(cap):
    load = cap["ref_load"]
    if load["platforms"] == "NONE" and load["industry"] == "NONE":
        return (
            "## 参考投影 · 本次未加载任何参考文件\n\n"
            "按 M4 统一能力合同 §12 加载矩阵，本能力（%s）不加载 "
            "`platforms.md` / `industry-conditions.md` / `examples.md` 的任何片段。\n\n"
            "**未列出的参考内容本次没有加载，不得引用、不得凭记忆补写。**\n" % cap["capability"]
        )

    parts = ["{%- set INDS = [\"服装 / 门店零售\", \"餐饮 / 门店\", \"知识付费 / 课程\", "
             "\"动漫 / 原创 IP\", \"户外 / 露营（爱好垂类）\"] -%}"]
    parts.append("## 参考投影 · 按 M4 统一能力合同 §12 加载矩阵确定性选出\n")

    if load["platforms"] == "STRUCTURAL":
        parts.append(
            "### platforms.md :: 结构性参数（只取影响内容结构 / 构图的部分）\n\n"
            "**只在它改变结构时读。** 数值型参数若在主本中无当前有效条目，"
            "置 `PLATFORM_SPEC_UNVERIFIED` 并改写为定性制作要求，**不得自造数字**；"
            "分支型参数改写为条件式，两支都写完整。\n\n"
            "本次 `platform` = {{ platform }}。`NOT_LOCKED` 时只产出平台中立母版，不出任何平台改写。\n"
        )
    elif load["platforms"] == "PACKAGING":
        parts.append(
            "### platforms.md :: 目标平台条目（含 `as_of`）\n\n"
            "本次 `platform` = {{ platform }}。\n\n"
            "- `NOT_LOCKED` ⇒ **只出母版，不出任何平台改写**（这是正常状态，不是缺陷）。\n"
            "- 平台已锁定但主本条目不可得 / 已过期 ⇒ **分支型参数出条件式改写**（两支都写完整），"
            "**数值型参数置 `PLATFORM_SPEC_UNVERIFIED` 并改写为定性制作要求**，"
            "并在 `missing[]` 注明定稿前必须查表。**不得凭记忆补一个数字。**\n"
        )

    if load["industry"] == "BY_DOMAIN":
        parts.append(
            "{%- if subject_domain in INDS %}\n"
            "### industry-conditions.md :: {{ subject_domain }}\n\n"
            "按 `subject_domain` 条件加载该行业段落。\n"
            "{%- else %}\n"
            "### industry-conditions.md :: 未加载\n\n"
            "`subject_domain` = {{ subject_domain }} 不在五个已登记行业内 ⇒ "
            "**按通用处理并在 `assumptions[]` 声明**，不要挑一个「最像的」套上去。\n"
            "{%- endif %}\n"
        )

    if load["examples"] == "ON_REQUEST":
        parts.append(
            "{%- if example_reference_requested == 'YES' %}\n"
            "### examples.md :: 端到端黄金案例\n\n"
            "**只作形式与质量参考，不得变成事实、话术或模板。**\n"
            "{%- else %}\n"
            "### examples.md :: 未加载\n\n"
            "本次未显式请求案例参考 ⇒ 不加载。**不得凭记忆补一个案例上去。**\n"
            "{%- endif %}\n"
        )

    parts.append("\n**未列出的参考内容本次没有加载，不得引用、不得凭记忆补写。**\n")
    return "\n".join(parts)


def projection_record_template(cap):
    load = cap["ref_load"]
    lines = ['{', '  "capability": "%s",' % cap["capability"], '  "loaded_reference_sections": [',
             '    "SKILL.md :: 后继版全文（始终加载）"']
    if load["platforms"] == "STRUCTURAL":
        lines.append('    ,"platforms.md :: 结构性参数（仅当影响内容结构/构图）"')
    elif load["platforms"] == "PACKAGING":
        lines.append('    ,"platforms.md :: 目标平台条目（含 as_of）"')
    if load["industry"] == "BY_DOMAIN":
        lines.append('{%- if subject_domain in INDS %}\n    ,"industry-conditions.md :: {{ subject_domain }}"\n{%- endif %}')
    if load["examples"] == "ON_REQUEST":
        lines.append('{%- if example_reference_requested == \'YES\' %}\n    ,"examples.md :: 端到端黄金案例"\n{%- endif %}')
    lines.append('  ],')
    lines.append('  "load_matrix_ref": "V1_M4_UNIFIED_CAPABILITY_CONTRACT_v0.1.md §12",')
    lines.append('  "second_attachment_library_built": false,')
    lines.append('  "rag_first_layer_built": false')
    lines.append('}')
    body = "\n".join(lines)
    if load["industry"] == "BY_DOMAIN" or load["examples"] == "ON_REQUEST":
        body = ('{%- set INDS = ["服装 / 门店零售", "餐饮 / 门店", "知识付费 / 课程", '
                '"动漫 / 原创 IP", "户外 / 露营（爱好垂类）"] -%}\n') + body
    return body


# --------------------------------------------------------------------------
# Prompt 组装
# --------------------------------------------------------------------------

USER_PROMPT_TMPL = """# 本次运行输入

## 统一能力调用外壳（capability_call）

{{{{#{start}.capability_call#}}}}

## 本能力的专业输入（professional_input）

{{{{#{start}.professional_input#}}}}

## 接缝控制（由确定性节点给出，不由你判断）

- `capability`：{cap}
- `entry`：{{{{#envelope_check.entry_resolved#}}}}
- `run_mode`：{{{{#envelope_check.run_mode_resolved#}}}}
- 结构性充分性：{{{{#envelope_check.status#}}}}
- 结构性缺项：{{{{#envelope_check.missing_text#}}}}
- 等价输入依据：{{{{#envelope_check.equivalence_basis#}}}}
- 来源（provenance.source_kind）：{{{{#envelope_check.source_kind#}}}}
- 必须条件化的项：{{{{#envelope_check.conditionalized_text#}}}}
- `objective.goal_family`（**只读继承，你无权改写**）：{{{{#envelope_check.goal_family#}}}}
- CTA 授权级别：{{{{#envelope_check.cta_level#}}}}
- `subject_domain`：{{{{#envelope_check.subject_domain#}}}}
- `platform`：{{{{#envelope_check.platform#}}}}
- `duration_band`：{{{{#envelope_check.duration_band#}}}}

---

## 本次运行的接缝硬约束

1. **不得暗跑上游。** 你**没有**调用任何其他能力的手段，也不得假设任何上游组件已经被运行过。
   合法等价输入已由上面的外壳给出；缺什么就说缺什么，**不要替不存在的上游产物编内容**。
2. **`objective.goal_family` 只读继承。** 不得把起号、吸粉、流量、GMV、线索、到店或混合目标
   静默改写成长期价值任务。你无权改目标；确有冲突时只发一条**局部 Return**。
3. **`explicit_non_promise` 只读继承。** 任何一段都不得往回加内容。
4. **跳过组件不降低标准。** 短入口不等于降低事实纪律、权限约束、风险约束或当前任务
   真正适用的专业质量。
5. **不适用维度写 `NOT_APPLICABLE` 并说明**，不得留空，也不得把不适用维度变成硬门。
6. **候选数量不得硬编码。** 只有存在真实取舍时才给多个方向；不存在时直接给推荐。
7. **本次没有加载的参考内容一律不得引用**，不得凭记忆补平台数字、行业惯例或案例。
8. 本能力**产出**：{produces}
   本能力**不得产出**：{must_not_produce}

---

## 产出结构（三块，标记行原样照抄，各只出现一次、必须成对闭合）

**不要把本节说明抄进产出。**

---M4_ARTIFACT---
（内部 Artifact：完整专业产出。按你正文规定的输出格式写全。
 可以保留来源、版本、状态、未选候选、淘汰原因与调试信息。
 这一块**不直接给用户看**。）
---END_M4_ARTIFACT---

---M4_USER_DELIVERY---
status: READY | NEEDS_DECISION | BLOCKED_LOCAL
（自然、完整、可直接使用的结果；必要候选；推荐；真实阻断；最小决定。
 **禁止出现**：内部术语与状态码、Prompt 正文、凭据、数据库、内部推理、参考文件全文、
 「已删除／已剔除／审查发现／修正后／原方案／未核实不得使用」这类便条，
 以及任何被淘汰内容的全文。
 **同样禁止**把用户必要的选择和成立条件投影掉——「不泄露」不是「少给」。）
---END_M4_USER_DELIVERY---

---M4_RETURNS---
（没有回改就只写一个词：NONE。**空块不等于 NONE**，会被判为解析失败。
 有回改时，每条写满下面八行；多条之间空一行。
 `affected_objects` 与 `downstream_stale` 用 | 分隔多个值。
 `downstream_stale` **只列真实依赖本次结论的项**，不得列全链。）
return_id: <稳定 id>
source: {cap}
highest_damaged_layer: <被实际破坏的最上游判断层>
precise_gap: <具体缺什么。禁写「信息不足」>
affected_objects: <对象1 | 对象2>
proposed_disposition: ACCEPT_AND_PATCH | REJECT_WITH_AUTHORITY | ESCALATE
needs_user_decision: true | false
downstream_stale: <项1 | 项2>
---END_M4_RETURNS---

---

## 写完之后，交出去之前，自己核这三条

1. 上面三对标记行有没有**原样出现、各一次、成对闭合**。少一行、改一个字、写成别的样子，
   下游都读不出来，等于这一块没交。
2. `---M4_ARTIFACT---` 里是不是**专业产出本身**。不得写成「即上方」「即以上」「同上」
   「上方即」「见上文」「内容同上」「本区块与…一致」这类指向另一块的话——
   那样写，这一块实际就是空的，下游拿到的是一句指路，不是产出。
3. `---M4_USER_DELIVERY---` 是不是**非空**、且同样没有写成指向 ARTIFACT 的一句话。
   用户只看得到这一块。{artifact_extra}

两块内容有重复不是问题，**回指和留空才是问题**。
"""


def build_system_prompt(skill_body):
    return (
        skill_body.rstrip()
        + "\n\n---\n\n# 本次运行注入的参考文件片段\n\n"
        + "以下片段由确定性投影节点按 M4 统一能力合同 §12 的固定加载矩阵选出。"
        + "**未列出的参考内容本次没有加载，不得引用、不得凭记忆补写。**\n\n"
        + "{{#ref_projection.output#}}\n"
    )


# --------------------------------------------------------------------------
# 图构造工具
# --------------------------------------------------------------------------

def node(nid, data, x, y, w=244, h=100):
    return {
        "data": data,
        "height": h,
        "id": nid,
        "position": {"x": x, "y": y},
        "positionAbsolute": {"x": x, "y": y},
        "selected": False,
        "sourcePosition": "right",
        "targetPosition": "left",
        "type": "custom",
        "width": w,
        "zIndex": 0,
    }


def edge(src, tgt, src_type, tgt_type, handle="source"):
    return {
        "data": {"isInIteration": False, "sourceType": src_type, "targetType": tgt_type},
        "id": "%s-%s-%s-target" % (src, handle, tgt),
        "source": src,
        "sourceHandle": handle,
        "target": tgt,
        "targetHandle": "target",
        "type": "custom",
        "zIndex": 0,
    }


def var(name, label, vtype="paragraph", required=True, maxlen=200000):
    return {"label": label, "max_length": maxlen, "options": [], "required": required,
            "type": vtype, "variable": name}


def sel(nid, name):
    return {"value_selector": [nid, name], "variable": name}


def out_str():
    return {"children": None, "type": "string"}


def out_arr():
    return {"children": None, "type": "array[string]"}


def app_envelope(name, desc, mode="workflow", icon="🧩", bg="#E4FBCC"):
    return {
        "description": desc,
        "icon": icon,
        "icon_background": bg,
        "icon_type": "emoji",
        "mode": mode,
        "name": name,
        "use_icon_as_answer_icon": False,
    }


FEATURES = {
    "file_upload": {
        "allowed_file_extensions": [".JPG", ".JPEG", ".PNG", ".GIF", ".WEBP", ".SVG"],
        "allowed_file_types": ["image"],
        "allowed_file_upload_methods": ["local_file", "remote_url"],
        "enabled": False,
        "fileUploadConfig": {
            "attachment_image_file_size_limit": 2, "audio_file_size_limit": 50,
            "batch_count_limit": 5, "file_size_limit": 15, "file_upload_limit": 20,
            "image_file_batch_limit": 10, "image_file_size_limit": 10,
            "single_chunk_attachment_limit": 10, "video_file_size_limit": 100,
            "workflow_file_upload_limit": 10,
        },
        "image": {"enabled": False, "number_limits": 3,
                  "transfer_methods": ["local_file", "remote_url"]},
        "number_limits": 3,
    },
    "opening_statement": "",
    "retriever_resource": {"enabled": False},
    "sensitive_word_avoidance": {"enabled": False},
    "speech_to_text": {"enabled": False},
    "suggested_questions": [],
    "suggested_questions_after_answer": {"enabled": False},
    "text_to_speech": {"enabled": False, "language": "", "voice": ""},
}


def read(rel):
    with open(os.path.join(ROOT, rel), encoding="utf-8") as fh:
        return fh.read()


def sha(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


# --------------------------------------------------------------------------
# 能力子应用
# --------------------------------------------------------------------------

def build_capability_app(cap):
    skill_body = read(cap["skill_path"])
    system_prompt = build_system_prompt(skill_body)
    user_prompt = USER_PROMPT_TMPL.format(
        start=START_ID, cap=cap["capability"],
        produces=cap["produces"], must_not_produce=cap["must_not_produce"],
        artifact_extra=cap.get("artifact_extra", ""),
    )

    binding_record = {
        "task_id": TASK_ID,
        "task_contract_hash": TASK_CONTRACT_HASH,
        "capability": cap["capability"],
        "successor_skill_path": cap["skill_path"],
        "successor_skill_sha256": sha(skill_body),
        "source_skill_path": cap["source_skill"],
        "source_skill_sha256": sha(read(cap["source_skill"])),
        "system_prompt_sha256": sha(system_prompt),
        "user_prompt_sha256": sha(user_prompt),
        "model_provider": MODEL["provider"],
        "model_name": MODEL["name"],
        "completion_params": MODEL["completion_params"],
        "reference_load_matrix": cap["ref_load"],
        "target_environment": "本机 Docker Dify 1.16.1 · DEVELOPMENT_TEST",
    }

    env_code = (ENVELOPE_CHECK_CODE
                .replace("__REQUIRED_SEMANTICS__", json.dumps(cap["required_semantics"], ensure_ascii=False))
                .replace("__CAPABILITY__", cap["capability"])
                .replace("__ALLOWED_ENTRIES__", json.dumps(cap["entries"], ensure_ascii=False))
                .replace("__ALLOWED_RUN_MODES__", json.dumps(cap["run_modes"], ensure_ascii=False))
                .replace("__DEFAULT_RUN_MODE__", cap["run_modes"][0]))

    ret_code = (COMPONENT_RETURN_CODE
                .replace("__CAPABILITY__", cap["capability"])
                .replace("__RETURN_LAYER__", cap["capability"] + "_INPUT_SUFFICIENCY"))

    adapter_code = RETURNS_ADAPTER_CODE.replace("__CAPABILITY__", cap["capability"])
    # 先 json.dumps 成 JSON 文本，再用 repr() 包成合法的 Python 字符串字面量，
    # 由代码节点自己 json.loads —— 全程没有「JSON 字面量当 Python 字面量」这一步。
    bind_code = BINDING_RECORD_CODE.replace(
        "__BINDING_RECORD_JSON__",
        repr(json.dumps(binding_record, ensure_ascii=False, sort_keys=True)))

    nodes = []
    edges = []

    nodes.append(node(START_ID, {
        "desc": "统一能力调用外壳 + 本能力专业输入。外壳不强制物理字段名。",
        "selected": False, "title": "输入", "type": "start",
        "variables": [
            var("capability_call", "capability_call（统一业务能力外壳）"),
            var("professional_input", "professional_input（本能力专业输入）"),
            var("entry", "entry（能力调用意图给出，可留空由确定性规则推导）", "text-input", False, 64),
            var("run_mode", "run_mode（可留空）", "text-input", False, 64),
            var("example_reference_requested", "example_reference_requested（YES/NO）", "text-input", False, 8),
        ],
    }, 40, 300))

    nodes.append(node("envelope_check", {
        "code": env_code, "code_language": "python3",
        "desc": "确定性外壳校验：结构性充分性 + 绑定计算。语义单薄的裁决交给 Skill 正文。",
        "outputs": {
            "status": out_str(), "can_run": out_str(), "note": out_str(),
            "missing": out_arr(), "missing_text": out_str(), "vacuity_flags": out_arr(),
            "conditionalized_text": out_str(), "entry_resolved": out_str(),
            "run_mode_resolved": out_str(), "goal_family": out_str(), "cta_level": out_str(),
            "source_kind": out_str(), "subject_domain": out_str(), "platform": out_str(),
            "duration_band": out_str(), "equivalence_basis": out_str(),
            "envelope_hash": out_str(), "professional_input_hash": out_str(),
            "capability": out_str(), "example_reference_requested": out_str(),
        },
        "selected": False, "title": "外壳校验", "type": "code",
        "variables": [sel(START_ID, "capability_call"), sel(START_ID, "professional_input"),
                      sel(START_ID, "entry"), sel(START_ID, "run_mode"),
                      sel(START_ID, "example_reference_requested")],
    }, 340, 300))

    nodes.append(node("gate_sufficiency", {
        "cases": [{"case_id": "run", "conditions": [
            {"comparison_operator": "is", "value": "true",
             "variable_selector": ["envelope_check", "can_run"]}], "logical_operator": "and"}],
        "desc": "结构性不足只走组件级 Return，不全局硬停、不生成假产物、不启动任何下游。",
        "logical_operator": "and", "selected": False, "title": "充分性闸", "type": "if-else",
    }, 640, 300))

    nodes.append(node("ref_projection", {
        "desc": "按统一能力合同 §12 加载矩阵确定性投影；不由 LLM 决定加载范围；不建第二套附件库。",
        "selected": False, "template": ref_projection_template(cap),
        "title": "Reference Projection", "type": "template-transform",
        "variables": [sel("envelope_check", "subject_domain"), sel("envelope_check", "platform"),
                      sel("envelope_check", "example_reference_requested")],
    }, 940, 220))

    nodes.append(node("projection_record", {
        "desc": "登记本次实际加载了哪些参考片段，供 AC-11 机器核验。",
        "selected": False, "template": projection_record_template(cap),
        "title": "Projection Record", "type": "template-transform",
        "variables": [sel("envelope_check", "subject_domain"),
                      sel("envelope_check", "example_reference_requested")],
    }, 1240, 220))

    nodes.append(node("skill_llm", {
        "context": {"enabled": False, "variable_selector": []},
        "desc": "system prompt 由后继 SKILL 文件字节派生（生成器保证），不手工同步。",
        "memory": None, "model": MODEL,
        "prompt_template": [{"role": "system", "text": system_prompt},
                            {"role": "user", "text": user_prompt}],
        "selected": False, "title": cap["app_name"], "type": "llm",
        "vision": {"enabled": False},
    }, 1540, 220, 244, 120))

    nodes.append(node("final_extract", {
        "desc": "剥离 thinking 段，取最终正文。空输出显式标记，不静默当成空结果。",
        "selected": False,
        "template": ("{%- if '</think>' in llm_text -%}\n"
                     "{%- set tail = llm_text.split('</think>')|last -%}\n"
                     "{%- if tail.strip() == '' -%}MODEL_OUTPUT_NO_FINAL{%- else -%}{{ tail }}{%- endif -%}\n"
                     "{%- elif llm_text.strip() == '' -%}MODEL_OUTPUT_NO_FINAL{%- else -%}{{ llm_text }}{%- endif -%}"),
        "title": "Final Extract", "type": "template-transform",
        "variables": [{"value_selector": ["skill_llm", "text"], "variable": "llm_text"}],
    }, 1840, 220))

    nodes.append(node("returns_adapter", {
        "code": adapter_code, "code_language": "python3",
        "desc": "确定性 Returns / 交付分离。解析失败置 PARSE_FAILED 并保留原文，绝不伪装成 NONE。",
        "outputs": {
            "artifact": out_str(), "artifact_status": out_str(),
            "needs_projection": out_str(), "projection_source": out_str(),
            "user_delivery": out_str(), "user_delivery_status": out_str(),
            "user_delivery_leaks": out_arr(), "returns_json": out_str(),
            "returns_status": out_str(), "returns_parse_note": out_str(),
            "returns_raw": out_str(), "raw_preserved": out_str(),
            "local_block": out_str(), "structure_notes": out_arr(), "capability": out_str(),
        },
        "selected": False, "title": "Returns / 交付适配器", "type": "code",
        "variables": [{"value_selector": ["final_extract", "output"], "variable": "final_text"}],
    }, 2140, 220))

    nodes.append(node("projection_gate", {
        "cases": [{"case_id": "recover", "conditions": [
            {"comparison_operator": "is", "value": "true",
             "variable_selector": ["returns_adapter", "needs_projection"]}],
            "logical_operator": "and"}],
        "desc": "专业内容已生成但用户交付块缺失/为空/回指 ⇒ 走一次有界用户投影；否则直通收口。",
        "logical_operator": "and", "selected": False,
        "title": "交付缺失判定", "type": "if-else",
    }, 2440, 220))

    nodes.append(node("recovery_llm", {
        "context": {"enabled": False, "variable_selector": []},
        "desc": "有界用户投影：只把已生成的专业产出讲给用户听，不新增事实、不重做生产。",
        "memory": None, "model": MODEL,
        "prompt_template": [{"role": "system", "text": RECOVERY_PROJECTION_PROMPT}],
        "selected": False, "title": "用户交付投影（一次有界恢复）", "type": "llm",
        "vision": {"enabled": False},
    }, 2740, 120, 244, 120))

    nodes.append(node("delivery_finalize", {
        "code": DELIVERY_FINALIZE_CODE, "code_language": "python3",
        "desc": "交付收口：保证用户正文非空；技术运行完成 != 业务交付成功。",
        "outputs": {"user_delivery": out_str(), "delivery_outcome": out_str(),
                    "user_delivery_status": out_str(), "returns_json": out_str(),
                    "recovery_used": out_str()},
        "selected": False, "title": "交付收口", "type": "code",
        "variables": [
            {"value_selector": ["returns_adapter", "user_delivery"], "variable": "adapter_user_delivery"},
            {"value_selector": ["returns_adapter", "user_delivery_status"], "variable": "adapter_status"},
            {"value_selector": ["returns_adapter", "needs_projection"], "variable": "needs_projection"},
            {"value_selector": ["recovery_llm", "text"], "variable": "recovered_text"},
            {"value_selector": ["returns_adapter", "returns_json"], "variable": "returns_json"},
            {"value_selector": ["returns_adapter", "capability"], "variable": "capability"},
        ],
    }, 3040, 220))

    nodes.append(node("binding_record", {
        "code": bind_code, "code_language": "python3",
        "desc": "AC-12 保真绑定记录。自报值只作声明，正式判定以已发布 Runtime 实际字节为准。",
        "outputs": {"binding_json": out_str()},
        "selected": False, "title": "保真绑定记录", "type": "code",
        "variables": [sel("envelope_check", "envelope_hash"),
                      sel("envelope_check", "professional_input_hash"),
                      {"value_selector": ["returns_adapter", "artifact"], "variable": "artifact"},
                      {"value_selector": ["projection_record", "output"], "variable": "reference_projection"},
                      sel("envelope_check", "entry_resolved"),
                      sel("envelope_check", "run_mode_resolved"),
                      sel("envelope_check", "goal_family")],
    }, 2440, 220))

    nodes.append(node("component_return", {
        "code": ret_code, "code_language": "python3",
        "desc": "组件级 Return：本分支结果，不是整任务终态，本身不触发下游失效。",
        "outputs": {
            "returns_json": out_str(), "return_status": out_str(), "branch_result": out_str(),
            "is_task_terminal_state": out_str(), "triggers_downstream_invalidation": out_str(),
            "single_most_discriminating_question": out_str(), "user_delivery": out_str(),
            "user_delivery_leaks": out_arr(),
            "fabricated_artifact_produced": out_str(), "downstream_invoked": out_str(),
        },
        "selected": False, "title": "组件级 Return", "type": "code",
        "variables": [sel("envelope_check", "status"), sel("envelope_check", "note"),
                      sel("envelope_check", "missing"), sel("envelope_check", "entry_resolved"),
                      sel("envelope_check", "envelope_hash"), sel(START_ID, "capability_call")],
    }, 940, 460))

    nodes.append(node("end_ok", {
        "desc": "正常产出", "outputs": [
            {"value_selector": ["returns_adapter", "artifact"], "variable": "artifact"},
            {"value_selector": ["delivery_finalize", "user_delivery"], "variable": "user_delivery"},
            {"value_selector": ["delivery_finalize", "delivery_outcome"], "variable": "delivery_outcome"},
            {"value_selector": ["delivery_finalize", "recovery_used"], "variable": "recovery_used"},
            {"value_selector": ["returns_adapter", "artifact_status"], "variable": "artifact_status"},
            {"value_selector": ["delivery_finalize", "user_delivery_status"], "variable": "user_delivery_status"},
            {"value_selector": ["returns_adapter", "user_delivery_leaks"], "variable": "user_delivery_leaks"},
            {"value_selector": ["delivery_finalize", "returns_json"], "variable": "returns_json"},
            {"value_selector": ["returns_adapter", "returns_status"], "variable": "returns_status"},
            {"value_selector": ["returns_adapter", "returns_parse_note"], "variable": "returns_parse_note"},
            {"value_selector": ["returns_adapter", "returns_raw"], "variable": "returns_raw"},
            {"value_selector": ["returns_adapter", "local_block"], "variable": "local_block"},
            {"value_selector": ["returns_adapter", "raw_preserved"], "variable": "raw_preserved"},
            {"value_selector": ["binding_record", "binding_json"], "variable": "binding_json"},
            {"value_selector": ["projection_record", "output"], "variable": "reference_projection"},
            {"value_selector": ["ref_projection", "output"], "variable": "reference_projection_text"},
            {"value_selector": ["envelope_check", "entry_resolved"], "variable": "entry"},
            {"value_selector": ["envelope_check", "run_mode_resolved"], "variable": "run_mode"},
            {"value_selector": ["envelope_check", "status"], "variable": "sufficiency_status"},
            {"value_selector": ["envelope_check", "goal_family"], "variable": "goal_family"},
            {"value_selector": ["envelope_check", "conditionalized_text"], "variable": "conditionalized"},
        ], "selected": False, "title": "结束", "type": "end",
    }, 2740, 220))

    nodes.append(node("end_component_return", {
        "desc": "组件级 Return 结束：本分支不足，其他诉求不受影响", "outputs": [
            {"value_selector": ["component_return", "user_delivery"], "variable": "user_delivery"},
            {"value_selector": ["component_return", "returns_json"], "variable": "returns_json"},
            {"value_selector": ["component_return", "return_status"], "variable": "returns_status"},
            {"value_selector": ["component_return", "branch_result"], "variable": "branch_result"},
            {"value_selector": ["component_return", "is_task_terminal_state"], "variable": "is_task_terminal_state"},
            {"value_selector": ["component_return", "triggers_downstream_invalidation"],
             "variable": "triggers_downstream_invalidation"},
            {"value_selector": ["component_return", "single_most_discriminating_question"],
             "variable": "single_question"},
            {"value_selector": ["component_return", "user_delivery_leaks"], "variable": "user_delivery_leaks"},
            {"value_selector": ["component_return", "fabricated_artifact_produced"],
             "variable": "fabricated_artifact_produced"},
            {"value_selector": ["component_return", "downstream_invoked"], "variable": "downstream_invoked"},
            {"value_selector": ["envelope_check", "missing_text"], "variable": "missing"},
        ], "selected": False, "title": "组件级 Return 结束", "type": "end",
    }, 1240, 460))

    edges.append(edge(START_ID, "envelope_check", "start", "code"))
    edges.append(edge("envelope_check", "gate_sufficiency", "code", "if-else"))
    edges.append(edge("gate_sufficiency", "ref_projection", "if-else", "template-transform", "run"))
    edges.append(edge("gate_sufficiency", "component_return", "if-else", "code", "false"))
    edges.append(edge("ref_projection", "projection_record", "template-transform", "template-transform"))
    edges.append(edge("projection_record", "skill_llm", "template-transform", "llm"))
    edges.append(edge("skill_llm", "final_extract", "llm", "template-transform"))
    edges.append(edge("final_extract", "returns_adapter", "template-transform", "code"))
    edges.append(edge("returns_adapter", "projection_gate", "code", "if-else"))
    edges.append(edge("projection_gate", "recovery_llm", "if-else", "llm", "recover"))
    edges.append(edge("projection_gate", "delivery_finalize", "if-else", "code", "false"))
    edges.append(edge("recovery_llm", "delivery_finalize", "llm", "code"))
    edges.append(edge("delivery_finalize", "binding_record", "code", "code"))
    edges.append(edge("binding_record", "end_ok", "code", "end"))
    edges.append(edge("component_return", "end_component_return", "code", "end"))

    dsl = {
        "app": app_envelope(
            cap["app_name"],
            "M4 统一能力接缝后继测试应用（%s）。task_id=%s。"
            "system prompt 由后继 SKILL 字节派生；reference 按统一合同 §12 加载矩阵确定性投影；"
            "不足只出组件级 Return，不全局硬停；不调用任何其他能力应用。"
            % (cap["capability"], TASK_ID)),
        "dependencies": [DEEPSEEK_DEP],
        "kind": "app",
        "version": "0.7.0",
        "workflow": {
            "conversation_variables": [],
            "environment_variables": [],
            "features": FEATURES,
            "graph": {"edges": edges, "nodes": nodes, "viewport": {"x": 0, "y": 0, "zoom": 0.5}},
        },
    }
    return dsl, binding_record


# --------------------------------------------------------------------------
# 父接缝应用
# --------------------------------------------------------------------------

def load_bindings():
    if os.path.exists(BINDINGS):
        with open(BINDINGS, encoding="utf-8") as fh:
            return json.load(fh)
    return {c["key"]: {"provider_id": "PENDING_PUBLISH", "app_id": "PENDING_PUBLISH",
                       "published_workflow_id": "PENDING_PUBLISH",
                       "tool_name": c["tool_name"]} for c in CAPABILITIES}


def build_seam_app():
    b = load_bindings()
    nodes = []
    edges = []

    nodes.append(node(START_ID, {
        "desc": "接收 M1 给出的唯一能力调用意图 + 统一外壳。本应用不做自然语言意图识别。",
        "selected": False, "title": "能力调用意图", "type": "start",
        "variables": [
            var("capability", "capability（由 M1 给出的唯一能力调用意图）", "text-input", True, 64),
            var("entry", "entry（可留空，由确定性充分性规则推导）", "text-input", False, 64),
            var("capability_call", "capability_call（统一业务能力外壳）"),
            var("professional_input", "professional_input（本能力专业输入）"),
            var("example_reference_requested", "example_reference_requested（YES/NO）", "text-input", False, 8),
        ],
    }, 40, 400))

    nodes.append(node("entry_resolver", {
        "code": ENTRY_RESOLVER_CODE, "code_language": "python3",
        "desc": "确定性入口解析。不是路由：不读自然语言、不做意图判断、不选择能力。",
        "outputs": {"route": out_str(), "capability_resolved": out_str(),
                    "entry_resolved": out_str(), "run_mode": out_str(),
                    "derivation": out_str(), "call_hash": out_str()},
        "selected": False, "title": "入口解析（确定性）", "type": "code",
        "variables": [sel(START_ID, "capability"), sel(START_ID, "entry"),
                      sel(START_ID, "capability_call"), sel(START_ID, "professional_input")],
    }, 340, 400))

    cases = []
    for c in CAPABILITIES:
        cases.append({"case_id": c["key"], "logical_operator": "and", "conditions": [
            {"comparison_operator": "is", "value": c["capability"],
             "variable_selector": ["entry_resolver", "route"]}]})
    nodes.append(node("seam_dispatch", {
        "cases": cases,
        "desc": "按已解析的能力调用意图分派。六个能力应用之间零调用边，组合只由本节点显式编排。",
        "logical_operator": "and", "selected": False, "title": "能力分派", "type": "if-else",
    }, 640, 400, 244, 60 + 40 * len(cases)))

    y = 80
    for c in CAPABILITIES:
        bind = b.get(c["key"], {})
        tool_id = "tool_" + c["key"]
        fin_id = "fin_" + c["key"]
        end_id = "end_" + c["key"]
        nodes.append(node(tool_id, {
            "desc": "调用 %s 后继测试应用；失败进 fail-branch；一次基础设施重试。" % c["capability"],
            "error_strategy": "fail-branch",
            "provider_id": bind.get("provider_id", "PENDING_PUBLISH"),
            "provider_name": bind.get("provider_id", "PENDING_PUBLISH"),
            "provider_type": "workflow",
            "retry_config": {"max_retries": 1, "retry_enabled": True, "retry_interval": 2000},
            "selected": False, "title": "调用 " + c["app_name"],
            "tool_configurations": {},
            "tool_label": c["tool_name"], "tool_name": c["tool_name"], "tool_node_version": "2",
            "tool_parameters": {
                "capability_call": {"type": "mixed", "value": "{{#%s.capability_call#}}" % START_ID},
                "professional_input": {"type": "mixed", "value": "{{#%s.professional_input#}}" % START_ID},
                "entry": {"type": "mixed", "value": "{{#entry_resolver.entry_resolved#}}"},
                "run_mode": {"type": "mixed", "value": "{{#entry_resolver.run_mode#}}"},
                "example_reference_requested": {
                    "type": "mixed", "value": "{{#%s.example_reference_requested#}}" % START_ID},
            },
            "type": "tool",
        }, 960, y, 244, 120))

        nodes.append(node(fin_id, {
            "code": SEAM_FINALIZE_CODE, "code_language": "python3",
            "desc": "接缝收口：登记实际调用/跳过、失效集，证明未暗跑上游。",
            "outputs": {"seam_trace_json": out_str(), "capability_invoked": out_str(),
                        "capabilities_skipped": out_arr(), "artifact": out_str(),
                        "user_delivery": out_str(),
                        "business_delivery_outcome": out_str(),
                        "returns_json": out_str(),
                        "binding_json": out_str()},
            "selected": False, "title": "接缝收口｜" + c["capability"], "type": "code",
            "variables": [
                {"value_selector": ["entry_resolver", "capability_resolved"], "variable": "capability_resolved"},
                {"value_selector": ["entry_resolver", "entry_resolved"], "variable": "entry_resolved"},
                {"value_selector": ["entry_resolver", "run_mode"], "variable": "run_mode"},
                {"value_selector": ["entry_resolver", "derivation"], "variable": "derivation"},
                {"value_selector": [tool_id, "artifact"], "variable": "tool_artifact"},
                {"value_selector": [tool_id, "user_delivery"], "variable": "tool_user_delivery"},
                {"value_selector": [tool_id, "returns_json"], "variable": "tool_returns_json"},
                {"value_selector": [tool_id, "binding_json"], "variable": "tool_binding_json"},
                {"value_selector": ["entry_resolver", "call_hash"], "variable": "call_hash"},
                {"value_selector": [tool_id, "local_block"], "variable": "tool_local_block"},
                {"value_selector": [tool_id, "artifact_status"], "variable": "tool_artifact_status"},
                {"value_selector": [tool_id, "user_delivery_status"], "variable": "tool_user_delivery_status"},
                {"value_selector": [tool_id, "delivery_outcome"], "variable": "tool_delivery_outcome"},
                {"value_selector": [tool_id, "recovery_used"], "variable": "tool_recovery_used"},
            ],
        }, 1300, y))

        nodes.append(node(end_id, {
            "desc": "%s 结束" % c["capability"], "outputs": [
                {"value_selector": [fin_id, "user_delivery"], "variable": "user_delivery"},
                {"value_selector": [fin_id, "business_delivery_outcome"],
                 "variable": "business_delivery_outcome"},
                {"value_selector": [fin_id, "artifact"], "variable": "artifact"},
                {"value_selector": [fin_id, "returns_json"], "variable": "returns_json"},
                {"value_selector": [fin_id, "binding_json"], "variable": "binding_json"},
                {"value_selector": [fin_id, "seam_trace_json"], "variable": "seam_trace_json"},
                {"value_selector": [fin_id, "capabilities_skipped"], "variable": "capabilities_skipped"},
            ], "selected": False, "title": "结束｜" + c["capability"], "type": "end",
        }, 1620, y))

        edges.append(edge("seam_dispatch", tool_id, "if-else", "tool", c["key"]))
        edges.append(edge(tool_id, fin_id, "tool", "code"))
        edges.append(edge(fin_id, end_id, "code", "end"))
        edges.append(edge(tool_id, "seam_tool_fail", "tool", "code", "fail-branch"))
        y += 200

    nodes.append(node("seam_tool_fail", {
        "code": SEAM_TOOL_FAIL_CODE,
        "code_language": "python3",
        "desc": ("Tool 调用失败：如实标记为执行失败，不伪装成业务不足或空结果；"
                 "并向用户返回非空自然语言说明（CL31-01/02）。"),
        "outputs": {"failure_kind": out_str(), "note": out_str(), "capability": out_str(),
                    "derivation": out_str(), "fabricated_artifact_produced": out_str(),
                    "user_delivery": out_str(), "business_delivery_outcome": out_str(),
                    "returns_json": out_str()},
        "selected": False, "title": "执行失败", "type": "code",
        "variables": [{"value_selector": ["entry_resolver", "route"], "variable": "route"},
                      {"value_selector": ["entry_resolver", "derivation"], "variable": "derivation"}],
    }, 1300, y + 40))

    nodes.append(node("end_tool_fail", {
        "desc": "执行失败结束", "outputs": [
            {"value_selector": ["seam_tool_fail", "user_delivery"], "variable": "user_delivery"},
            {"value_selector": ["seam_tool_fail", "business_delivery_outcome"],
             "variable": "business_delivery_outcome"},
            {"value_selector": ["seam_tool_fail", "returns_json"], "variable": "returns_json"},
            {"value_selector": ["seam_tool_fail", "failure_kind"], "variable": "failure_kind"},
            {"value_selector": ["seam_tool_fail", "note"], "variable": "note"},
            {"value_selector": ["seam_tool_fail", "capability"], "variable": "capability"},
            {"value_selector": ["seam_tool_fail", "fabricated_artifact_produced"],
             "variable": "fabricated_artifact_produced"},
        ], "selected": False, "title": "结束｜执行失败", "type": "end",
    }, 1620, y + 40))

    nodes.append(node("unsupported", {
        "code": SEAM_UNSUPPORTED_CODE,
        "code_language": "python3",
        "desc": ("不支持的能力调用意图：如实拒绝，不代做 M1 的能力选择；"
                 "并向用户返回非空自然语言说明（CL31-01）。"),
        "outputs": {"note": out_str(), "capability": out_str(), "derivation": out_str(),
                    "user_delivery": out_str(), "business_delivery_outcome": out_str(),
                    "returns_json": out_str()},
        "selected": False, "title": "不支持的能力", "type": "code",
        "variables": [{"value_selector": ["entry_resolver", "route"], "variable": "route"},
                      {"value_selector": ["entry_resolver", "derivation"], "variable": "derivation"}],
    }, 960, y + 40))

    nodes.append(node("end_unsupported", {
        "desc": "不支持结束", "outputs": [
            {"value_selector": ["unsupported", "user_delivery"], "variable": "user_delivery"},
            {"value_selector": ["unsupported", "business_delivery_outcome"],
             "variable": "business_delivery_outcome"},
            {"value_selector": ["unsupported", "returns_json"], "variable": "returns_json"},
            {"value_selector": ["unsupported", "note"], "variable": "note"},
            {"value_selector": ["unsupported", "capability"], "variable": "capability"},
        ], "selected": False, "title": "结束｜不支持", "type": "end",
    }, 1300, y + 160))

    edges.append(edge(START_ID, "entry_resolver", "start", "code"))
    edges.append(edge("entry_resolver", "seam_dispatch", "code", "if-else"))
    edges.append(edge("seam_dispatch", "unsupported", "if-else", "code", "false"))
    edges.append(edge("unsupported", "end_unsupported", "code", "end"))
    edges.append(edge("seam_tool_fail", "end_tool_fail", "code", "end"))

    return {
        "app": app_envelope(
            "DIYU %s · Capability Seam" % APP_TAG,
            "M4 统一能力接缝父应用。接收 M1 给出的唯一能力调用意图，"
            "做接口、适配、组合、Return 与局部失效；**不建第二套路由**。"
            "七类直接入口在此可达；六个能力应用之间零调用边。task_id=%s" % TASK_ID,
            icon="🧵", bg="#D5F5F6"),
        "dependencies": [],
        "kind": "app",
        "version": "0.7.0",
        "workflow": {
            "conversation_variables": [],
            "environment_variables": [],
            "features": FEATURES,
            "graph": {"edges": edges, "nodes": nodes, "viewport": {"x": 0, "y": 0, "zoom": 0.4}},
        },
    }


# --------------------------------------------------------------------------
# Founder 画布（复用 M1 已落地的意图层，不重建自然语言理解）
# --------------------------------------------------------------------------

M1_SOURCE_DSL = os.path.join(DC_WF, "DIYU_DEMO_V1_FULL_CHAIN_CHATFLOW_v0.2.yml")

# 复用的 M1 节点：逐字节复制其 data，不改一个字符。
M1_REUSED_NODES = ["v1_start", "v1_shadow", "v1_state", "save_runtime",
                   "v1_chat_save", "v1_chat_llm", "v1_chat_answer"]


# --------------------------------------------------------------------------
# M4-BLK-002 外科式解锁（Founder 2026-08-26 授权）
#
# M1 已落地的 v1_state 里有一把线性硬锁：
#   · UPSTREAM_OF 把五个能力钉成
#     matrix → campaign → content_brief → production_stage1 → publishing_stage2；
#     gate_reason() 只要看到上游不是 USER_ACCEPTED，就 revoke_auth() 并把
#     route 打成 HUMAN_DECISION。
#   · NEXT_SKILL 把「接受并继续」自动推进到固定的下一棒。
# 两者合起来使 ENTRY-03 / 05 / 06 / 07 在 Founder 画布路径上不可能成立，
# 与上位合同 REQUIRED_ALWAYS=[] / DEFAULT_CALL=[] / FIXED_ORDER=false 直接冲突。
#
# 修法是外科式的：只替换这两处**定义**，其余每一个字节原样保留。
#   · gate_reason() 函数体不动 —— UPSTREAM_OF[slot] 变 None 后自动走
#     「up is None」那条 M1 本来就为 matrix 准备好的分支，仍然要求 confirmed_task。
#     「用户必须先确认任务」是真实的用户授权门，不是流水线锁，必须保留。
#   · NEXT_SKILL 全部置 "NONE" 后，「接受并继续」只接受产物、不自动授权下一棒，
#     落到既有的 ARTIFACT_ACCEPTED 分支（回执 + 说明下一步用户可以做什么），
#     不是死路，也不再替用户默认调用任何能力。
#   · DOWNSTREAM_OF_SLOT **不动**：快照里没有逐产物的依赖记录，
#     按 A3「无法判断者置 STALE」保守失效是正确的，清空反而是少算。
#   · v1_shadow（M1 的自然语言理解）零改动。
#
# 差异由 verify_v1_state_patch() 机械断言：恰好等于这两处，多一处即 FAIL。
# --------------------------------------------------------------------------

V1_STATE_PATCHES = [
    (
        'NEXT_SKILL = {"matrix": "CAMPAIGN", "campaign": "CONTENT_BRIEF",\n'
        '              "content_brief": "PRODUCTION_STAGE1",\n'
        '              "production_stage1": "PUBLISHING_STAGE2",\n'
        '              "publishing_stage2": "NONE"}',

        'NEXT_SKILL = {"matrix": "NONE", "campaign": "NONE",\n'
        '              "content_brief": "NONE",\n'
        '              "production_stage1": "NONE",\n'
        '              "publishing_stage2": "NONE"}',
    ),
    (
        'UPSTREAM_OF = {"matrix": None, "campaign": "matrix", "content_brief": "campaign",\n'
        '               "production_stage1": "content_brief",\n'
        '               "publishing_stage2": "production_stage1"}',

        'UPSTREAM_OF = {"matrix": None, "campaign": None, "content_brief": None,\n'
        '               "production_stage1": None,\n'
        '               "publishing_stage2": None}',
    ),
    # ---- 第三处：M4-FND-001（Founder 2026-08-26 定性为施工范畴内）----
    #
    # 现象：Founder 画布上说「确认这个任务」，约两成概率系统回「你的确认没有成功记录」。
    # 根因（实测，非推断）：v1_state.patch 接在 v1_shadow.structured_output 上，
    # 而 Dify 1.16.1 的 structured output 提取器会**间歇性挑错 JSON 对象** ——
    # 实测抓到两种：一次挑中 schema 里 continue_signal 自己的属性定义
    # {description, enum, type}，一次挑中被注入快照里的 pending_action
    # {kind, task_revision, confirmation_id}。
    # 同一次执行里，模型写进 `text` 的补丁**是完整正确的**。
    # 画布全部 10 次影子执行：text 合法 10/10，structured_output 合法 8/10，两者同时坏 0 次。
    #
    # 修法：不动校验器，改接线 —— structured_output 验不过时，用**同一个**
    # validate_patch 再验一次 text。验不过照样拒，安全性质一分不降；
    # 每次回收都记进 notes 备审。
    #
    # 明确**没有**采用的修法：让 validate_patch 丢掉未知字段继续。
    # 那个修法在失败样本 A 上根本无效（合法字段数为 0，丢完是空对象），
    # 而且会放行部分补丁，削弱「坏补丁不得到达 Skill」这条安全性质。
    (
        'def main(user_query, old_snapshot, patch, runtime_state_json):',
        'def main(user_query, old_snapshot, patch, runtime_state_json, patch_text=""):',
    ),
    (
        '    clean, patch_ok, reject = validate_patch(patch)\n'
        '\n'
        '    notes = []\n',

        '    clean, patch_ok, reject = validate_patch(patch)\n'
        '\n'
        '    notes = []\n'
        '    if not patch_ok:\n'
        '        # M4-FND-001：structured_output 提取器间歇性挑错对象；模型写进 text 的补丁是对的。\n'
        '        # 用**同一个** validate_patch 再验一次 text —— 验不过照样拒，安全性质不降。\n'
        '        _c2, _ok2, _rj2 = validate_patch(patch_text)\n'
        '        if _ok2:\n'
        '            notes.append("PATCH_RECOVERED_FROM_TEXT:" + reject)\n'
        '            clean, patch_ok, reject = _c2, True, ""\n',
    ),
    # ---- 第四处：M4-FND-003（固定顺序叙述残留）----
    #
    # 现象（实测抓到）：画布没走到 M4 的那些轮次里，对话节点对用户说
    # 「会依次产出账号矩阵、决策包和内容 Brief」「在系统里点开始生成」——
    # 前半句是上位合同已废止的固定顺序，后半句是编出来的、不存在的界面操作。
    #
    # 根因：v1_state 拼给对话节点的上下文里，五项产物按 ARTIFACT_SLOTS 的
    # 流水线顺序列出，且**没有任何一句**说明它们之间没有先后。
    # 对话节点只能照着这个排列去推，于是推出了流水线。
    #
    # 修法：在同一处再追加一句，把「无固定先后」写成显式事实。纯追加，
    # 不改既有任何一行，不动 art_bits 的取值逻辑。
    # 这一处明确属于 M4 施工范围：统一能力合同 §2 FIXED_ORDER: false /
    # REQUIRED_ALWAYS: []，以及 CLAUDE.md §3「Campaign 既不默认调用，也不默认绕过」。
    (
        '    parts.append("已有结果：" + "；".join(art_bits))\n',

        '    parts.append("已有结果：" + "；".join(art_bits))\n'
        '    parts.append("这五项之间没有固定先后，也没有哪一项是其它项的前置条件。"\n'
        '                 "只要某一项自己需要的业务输入已经齐了，就可以直接做那一项，"\n'
        '                 "不需要先补跑前面的。"\n'
        '                 "不要向用户描述任何固定顺序或依次生成的流程，"\n'
        '                 "也不要提任何按钮或界面操作——这里没有按钮。")\n',
    ),
]


def apply_v1_state_patch(code):
    """外科式替换两处定义；任一处不是恰好命中一次即中止。"""
    out = code
    for old, new in V1_STATE_PATCHES:
        hits = out.count(old)
        if hits != 1:
            raise SystemExit("v1_state 补丁未唯一命中（命中 %d 次）：%s"
                             % (hits, old.splitlines()[0]))
        out = out.replace(old, new)
    return out


def verify_v1_state_patch(src_code, patched_code):
    """机械断言：行级差异恰好等于两处补丁涉及的行；多一处即返回非空。"""
    import difflib
    allowed_minus, allowed_plus = set(), set()
    for old, new in V1_STATE_PATCHES:
        allowed_minus |= set(old.splitlines())
        allowed_plus |= set(new.splitlines())
    expected_added = sum(len(new.splitlines()) - len(old.splitlines())
                         for old, new in V1_STATE_PATCHES)
    bad = []
    a = src_code.splitlines()
    b = patched_code.splitlines()
    if len(b) - len(a) != expected_added:
        bad.append("行数变化 %d -> %d，期望净增 %d（多出的行不属于任何已登记补丁）"
                   % (len(a), len(b), expected_added))
    for line in difflib.unified_diff(a, b, lineterm="", n=0):
        if line.startswith(("---", "+++", "@@")):
            continue
        if line.startswith("-") and line[1:] not in allowed_minus:
            bad.append("越界删除：" + line[1:])
        elif line.startswith("+") and line[1:] not in allowed_plus:
            bad.append("越界新增：" + line[1:])
    return bad

M4_INTENT_ADAPTER_CODE = r'''
import json
import re

# M1 → M4 薄适配（纯传输 + 等价输入判定，不含自然语言理解）
#
# 边界说明（统一能力合同 §2.2、§5.5）：
#   · 自然语言理解、跨诉求路由、最小追问判断 = M1。本节点**不做**这三件事。
#   · 本节点只读 M1 已经给出的 `effective_route`（唯一能力调用意图），
#     再按**输入充分性**把它落到 M4 的七类入口之一。
#   · 「M1 的五值枚举怎么覆盖 M4 的七个入口」不是靠再做一次意图识别，
#     而是靠同一能力内部的等价输入判定：
#       EXECUTE_PRODUCTION_STAGE1 + 已有合法脚本      → ENTRY-06（直达 PD）
#       EXECUTE_PRODUCTION_STAGE1 + 已选创意方向      → ENTRY-05（直达 CS）
#       EXECUTE_PRODUCTION_STAGE1 + 确有取舍结构前提  → ENTRY-04（CS-1 锦标赛）
#     这属于 M4 的「合法等价输入 + 按需组合」职责，不是第二套路由。

ROUTE_TO_CAP = {
    "EXECUTE_MATRIX": "MATRIX",
    "EXECUTE_CAMPAIGN": "CAMPAIGN",
    "EXECUTE_CONTENT_BRIEF": "CONTENT_BRIEF",
    "EXECUTE_PRODUCTION_STAGE1": "CREATIVE_SCRIPT",
    "EXECUTE_PUBLISHING_STAGE2": "PUBLISHING_PACKAGING",
}

FIVE_AXES = ["核心矛盾", "叙事发动机", "人物关系", "信息释放顺序", "视觉前提"]


def _has(text, *keys):
    t = text or ""
    return any(k in t for k in keys)


def main(effective_route, task_goal, snapshot_json, runtime_state_json,
         matrix_artifact, campaign_artifact, content_brief_artifact,
         creative_script_artifact, production_plan_artifact, user_query):
    route = (effective_route or "").strip().upper()
    cap = ROUTE_TO_CAP.get(route, "")

    if not cap:
        return {
            "has_capability": "false",
            "capability": "",
            "entry": "",
            "capability_call": "",
            "professional_input": "",
            "adapter_note": "M1 本轮未给出能力调用意图；按自然对话处理。M4 不代做能力选择。",
            "equivalence_basis": "",
        }

    script = creative_script_artifact or ""
    plan = production_plan_artifact or ""
    brief = content_brief_artifact or ""

    entry = ""
    basis = ""
    if cap == "CREATIVE_SCRIPT":
        if _has(plan, "realization_plan", "capture_plan", "realization_manifest") or \
           _has(script, "script_beats", "逐字稿", "beat_id"):
            if _has(plan, "realization_plan", "capture_plan", "realization_manifest"):
                cap, entry = "PRODUCTION_DIRECTOR", "ENTRY-06"
                basis = "已存在合法制作方案/兑现清单：按等价输入直达 Production Director，不补跑上游"
            else:
                cap, entry = "PRODUCTION_DIRECTOR", "ENTRY-06"
                basis = "已存在合法脚本（含节拍与两问）：按等价输入直达 Production Director，不补跑 Brief/锦标赛/CS"
        elif _has(script, "accepted_direction", "已选方向") or _has(user_query, "就用这个", "按这个方向"):
            entry = "ENTRY-05"
            basis = "已有被接受的创意方向：直达完整脚本，不重开锦标赛、不强制物理 Brief"
        elif sum(1 for a in FIVE_AXES if a in (brief + script)) >= 3:
            entry = "ENTRY-04"
            basis = "输入存在真实取舍的结构前提：进入 CS-1；差异是否实质由 CS-1 正文裁决"
        else:
            entry = "ENTRY-05"
            basis = "未发现真实取舍的结构前提：直接推荐一个方向并成稿，不机械凑候选"
    elif cap == "PUBLISHING_PACKAGING":
        entry = "ENTRY-07"
        basis = "包装诉求：按已有兑现证据直达 PP；有合法成片时不补跑 CS/PD"
    elif cap == "MATRIX":
        entry, basis = "ENTRY-01", "账号架构/诊断诉求：独立可达，不继续生产链"
    elif cap == "CAMPAIGN":
        entry, basis = "ENTRY-02", "阶段经营任务诉求：独立可达，既不默认调用也不默认绕过"
    else:
        entry, basis = "ENTRY-03", "明确选题/等价输入：直达 Content Brief，不暗跑 Matrix/Campaign"

    envelope = {
        "capability": cap,
        "entry": entry,
        "provenance": {"source_kind": "USER_DIRECT", "source_ref": "founder_canvas",
                       "confirmation_state": "STATED_BY_USER"},
        "objective": {"primary_goal": task_goal or "", "goal_family": "UNDECLARED"},
        "accepted": {"user_verbatim": user_query or ""},
        "sufficiency": {"equivalence_basis": basis},
        "task_snapshot": snapshot_json or "",
        "runtime_state": runtime_state_json or "",
    }

    prof = "\n\n".join([x for x in [
        ("## 已有 Matrix 产物\n" + matrix_artifact) if matrix_artifact else "",
        ("## 已有 Campaign 产物\n" + campaign_artifact) if campaign_artifact else "",
        ("## 已有 Content Brief\n" + brief) if brief else "",
        ("## 已有脚本\n" + script) if script else "",
        ("## 已有制作方案 / 兑现清单\n" + plan) if plan else "",
    ] if x])

    return {
        "has_capability": "true",
        "capability": cap,
        "entry": entry,
        "capability_call": json.dumps(envelope, ensure_ascii=False, indent=2),
        "professional_input": prof or "（本轮没有已有上游产物；不得据此假设上游被运行过。）",
        "adapter_note": "纯传输 + 等价输入判定；未做自然语言理解，未选择能力。",
        "equivalence_basis": basis,
    }
'''

M4_CANVAS_FIN_CODE = r'''
import json


def main(capability, entry, equivalence_basis, seam_user_delivery, seam_returns_json,
         seam_trace_json, seam_capabilities_skipped):
    try:
        skipped = seam_capabilities_skipped if isinstance(seam_capabilities_skipped, list) else []
    except Exception:
        skipped = []

    text = seam_user_delivery or ""
    if not text.strip():
        text = ("这一步没有产出可交付内容。原始运行记录已保留在内部，"
                "没有被删掉，也没有被改写成通过。")

    return {
        "user_answer": text,
        "capability_used": capability,
        "entry_used": entry,
        "equivalence_basis": equivalence_basis,
        "capabilities_skipped": skipped,
        "returns_json": seam_returns_json or "[]",
        "seam_trace_json": seam_trace_json or "{}",
    }
'''


def build_founder_canvas():
    import yaml as _y
    with open(M1_SOURCE_DSL, encoding="utf-8") as fh:
        src = _y.safe_load(fh)
    src_nodes = {n["id"]: n for n in src["workflow"]["graph"]["nodes"]}

    b = load_bindings()
    seam_provider = b.get("_seam", {}).get("provider_id", "PENDING_PUBLISH")

    nodes = []
    patched = 0
    for nid in M1_REUSED_NODES:
        n = json.loads(json.dumps(src_nodes[nid]))     # 逐字节深拷贝，不改 data
        if nid == "v1_state":
            # M4-BLK-002：唯一被授权改动的 M1 节点，且只允许两处外科替换。
            _src = n["data"]["code"]
            _new = apply_v1_state_patch(_src)
            _bad = verify_v1_state_patch(_src, _new)
            if _bad:
                raise SystemExit("v1_state 外科补丁越界：\n  " + "\n  ".join(_bad))
            n["data"]["code"] = _new
            # M4-FND-001：把影子的 text 也接进来做兜底输入。
            _vars = n["data"].setdefault("variables", [])
            if not any(v.get("variable") == "patch_text" for v in _vars):
                _vars.append({"value_selector": ["v1_shadow", "text"],
                              "variable": "patch_text"})
            patched += 1
        nodes.append(n)
    if patched != 1:
        raise SystemExit("v1_state 节点未找到或不唯一（%d）" % patched)

    nodes.append(node("m4_intent_adapter", {
        "code": M4_INTENT_ADAPTER_CODE, "code_language": "python3",
        "desc": "M1 → M4 薄适配：纯传输 + 等价输入判定。不做自然语言理解、不选择能力、不建第二套路由。",
        "outputs": {"has_capability": out_str(), "capability": out_str(), "entry": out_str(),
                    "capability_call": out_str(), "professional_input": out_str(),
                    "adapter_note": out_str(), "equivalence_basis": out_str()},
        "selected": False, "title": "M1 意图 → M4 接缝（薄适配）", "type": "code",
        "variables": [
            {"value_selector": ["v1_state", "effective_route"], "variable": "effective_route"},
            {"value_selector": ["v1_state", "task_goal"], "variable": "task_goal"},
            {"value_selector": ["v1_state", "snapshot_json"], "variable": "snapshot_json"},
            {"value_selector": ["v1_state", "runtime_state_json"], "variable": "runtime_state_json"},
            {"value_selector": ["conversation", "matrix_artifact"], "variable": "matrix_artifact"},
            {"value_selector": ["conversation", "campaign_artifact"], "variable": "campaign_artifact"},
            {"value_selector": ["conversation", "content_brief_artifact"], "variable": "content_brief_artifact"},
            {"value_selector": ["conversation", "creative_script_artifact"], "variable": "creative_script_artifact"},
            {"value_selector": ["conversation", "production_plan_artifact"], "variable": "production_plan_artifact"},
            {"value_selector": ["sys", "query"], "variable": "user_query"},
        ],
    }, 1000, 300))

    nodes.append(node("m4_route", {
        "cases": [{"case_id": "capability", "logical_operator": "and", "conditions": [
            {"comparison_operator": "is", "value": "true",
             "variable_selector": ["m4_intent_adapter", "has_capability"]}]}],
        "desc": "M1 给出能力调用意图才进接缝；否则走自然对话。这里不做意图识别。",
        "logical_operator": "and", "selected": False, "title": "有能力调用意图吗", "type": "if-else",
    }, 1300, 300))

    nodes.append(node("tool_seam", {
        "desc": "调用 M4 统一能力接缝；失败进 fail-branch；一次基础设施重试。",
        "error_strategy": "fail-branch",
        "provider_id": seam_provider, "provider_name": seam_provider, "provider_type": "workflow",
        "retry_config": {"max_retries": 1, "retry_enabled": True, "retry_interval": 2000},
        "selected": False, "title": "调用 M4 统一能力接缝",
        "tool_configurations": {}, "tool_label": "diyu_m4_capability_seam",
        "tool_name": "diyu_m4_capability_seam", "tool_node_version": "2",
        "tool_parameters": {
            "capability": {"type": "mixed", "value": "{{#m4_intent_adapter.capability#}}"},
            "entry": {"type": "mixed", "value": "{{#m4_intent_adapter.entry#}}"},
            "capability_call": {"type": "mixed", "value": "{{#m4_intent_adapter.capability_call#}}"},
            "professional_input": {"type": "mixed", "value": "{{#m4_intent_adapter.professional_input#}}"},
            "example_reference_requested": {"type": "mixed", "value": "NO"},
        },
        "type": "tool",
    }, 1600, 240, 244, 120))

    nodes.append(node("m4_canvas_fin", {
        "code": M4_CANVAS_FIN_CODE, "code_language": "python3",
        "desc": "只把用户交付投影给用户；内部 Artifact、绑定与轨迹留在内部。",
        "outputs": {"user_answer": out_str(), "capability_used": out_str(), "entry_used": out_str(),
                    "equivalence_basis": out_str(), "capabilities_skipped": out_arr(),
                    "returns_json": out_str(), "seam_trace_json": out_str()},
        "selected": False, "title": "接缝结果收口", "type": "code",
        "variables": [
            {"value_selector": ["m4_intent_adapter", "capability"], "variable": "capability"},
            {"value_selector": ["m4_intent_adapter", "entry"], "variable": "entry"},
            {"value_selector": ["m4_intent_adapter", "equivalence_basis"], "variable": "equivalence_basis"},
            {"value_selector": ["tool_seam", "user_delivery"], "variable": "seam_user_delivery"},
            {"value_selector": ["tool_seam", "returns_json"], "variable": "seam_returns_json"},
            {"value_selector": ["tool_seam", "seam_trace_json"], "variable": "seam_trace_json"},
            {"value_selector": ["tool_seam", "capabilities_skipped"], "variable": "seam_capabilities_skipped"},
        ],
    }, 1900, 240))

    nodes.append(node("m4_answer", {
        "answer": "{{#m4_canvas_fin.user_answer#}}",
        "desc": "只输出自然语言交付；不泄露内部结构、状态码、Prompt 或调试对象。",
        "selected": False, "title": "回复｜M4 能力结果", "type": "answer", "variables": [],
    }, 2200, 240))

    nodes.append(node("m4_toolfail", {
        "code": ("def main(capability, entry):\n"
                 "    return {\n"
                 "        'user_answer': ('这一步没跑起来，是执行失败，不是你给的信息不够。'\n"
                 "                        '我没有替它生成任何内容。你可以让我再试一次。'),\n"
                 "        'failure_kind': 'TOOL_CALL_FAILED',\n"
                 "        'capability': capability,\n"
                 "        'entry': entry,\n"
                 "        'fabricated_artifact_produced': 'false',\n"
                 "    }\n"),
        "code_language": "python3",
        "desc": "执行失败如实标记，不伪装成业务不足或空结果。",
        "outputs": {"user_answer": out_str(), "failure_kind": out_str(), "capability": out_str(),
                    "entry": out_str(), "fabricated_artifact_produced": out_str()},
        "selected": False, "title": "执行失败", "type": "code",
        "variables": [{"value_selector": ["m4_intent_adapter", "capability"], "variable": "capability"},
                      {"value_selector": ["m4_intent_adapter", "entry"], "variable": "entry"}],
    }, 1900, 460))

    nodes.append(node("m4_toolfail_answer", {
        "answer": "{{#m4_toolfail.user_answer#}}",
        "desc": "执行失败回复", "selected": False, "title": "回复｜执行失败",
        "type": "answer", "variables": [],
    }, 2200, 460))

    edges = [
        edge("v1_start", "v1_shadow", "start", "llm"),
        edge("v1_shadow", "v1_state", "llm", "code"),
        edge("v1_state", "save_runtime", "code", "assigner"),
        edge("save_runtime", "m4_intent_adapter", "assigner", "code"),
        edge("m4_intent_adapter", "m4_route", "code", "if-else"),
        edge("m4_route", "tool_seam", "if-else", "tool", "capability"),
        edge("m4_route", "v1_chat_save", "if-else", "assigner", "false"),
        edge("v1_chat_save", "v1_chat_llm", "assigner", "llm"),
        edge("v1_chat_llm", "v1_chat_answer", "llm", "answer"),
        edge("tool_seam", "m4_canvas_fin", "tool", "code"),
        edge("m4_canvas_fin", "m4_answer", "code", "answer"),
        edge("tool_seam", "m4_toolfail", "tool", "code", "fail-branch"),
        edge("m4_toolfail", "m4_toolfail_answer", "code", "answer"),
    ]

    return {
        "app": app_envelope(
            "DIYU %s · Founder Canvas" % APP_TAG,
            "M4 Founder 实测画布。**M1 已落地的意图层（v1_shadow / v1_state）逐字节复用，"
            "M4 不重建自然语言理解、不建第二套路由**；其后由薄适配把唯一能力调用意图"
            "按等价输入落到七类入口之一，再进入统一能力接缝。task_id=%s" % TASK_ID,
            mode="advanced-chat", icon="🎛️", bg="#FFEAD5"),
        "dependencies": [DEEPSEEK_DEP],
        "kind": "app",
        "version": "0.7.0",
        "workflow": {
            "conversation_variables": src["workflow"]["conversation_variables"],
            "environment_variables": [],
            "features": src["workflow"]["features"],
            "graph": {"edges": edges, "nodes": nodes, "viewport": {"x": 0, "y": 0, "zoom": 0.45}},
        },
    }


# --------------------------------------------------------------------------
# build / verify
# --------------------------------------------------------------------------

def _dump(path, dsl):
    import yaml
    with open(path, "w", encoding="utf-8") as fh:
        yaml.safe_dump(dsl, fh, allow_unicode=True, sort_keys=True, default_flow_style=False, width=120)


def cmd_build():
    records = {}
    for cap in CAPABILITIES:
        dsl, rec = build_capability_app(cap)
        path = os.path.join(cap["out_dir"], cap["out_file"])
        _dump(path, dsl)
        records[cap["key"]] = rec
        print("built %-26s -> %s" % (cap["capability"], os.path.relpath(path, ROOT)))
    seam = build_seam_app()
    seam_path = os.path.join(DC_WF, "DIYU_M4_CAPABILITY_SEAM_v1_3_TEST.yml")
    _dump(seam_path, seam)
    print("built %-26s -> %s" % ("CAPABILITY_SEAM", os.path.relpath(seam_path, ROOT)))

    canvas = build_founder_canvas()
    canvas_path = os.path.join(DC_WF, "DIYU_M4_FOUNDER_CANVAS_v1_3_TEST.yml")
    _dump(canvas_path, canvas)
    print("built %-26s -> %s" % ("FOUNDER_CANVAS", os.path.relpath(canvas_path, ROOT)))

    rec_path = os.path.join(DC_WF, "DIYU_M4_FIDELITY_RECORDS.json")
    with open(rec_path, "w", encoding="utf-8") as fh:
        json.dump(records, fh, ensure_ascii=False, indent=2, sort_keys=True)
    print("built %-26s -> %s" % ("FIDELITY_RECORDS", os.path.relpath(rec_path, ROOT)))

    if not os.path.exists(BINDINGS):
        pending = load_bindings()          # 先算再写：open(..,"w") 会先截断文件
        with open(BINDINGS, "w", encoding="utf-8") as fh:
            json.dump(pending, fh, ensure_ascii=False, indent=2, sort_keys=True)
        print("built %-26s -> %s (PENDING_PUBLISH)" % ("PROVIDER_BINDINGS", os.path.relpath(BINDINGS, ROOT)))


def cmd_verify():
    import yaml
    fails, warns = [], []

    for cap in CAPABILITIES:
        path = os.path.join(cap["out_dir"], cap["out_file"])
        if not os.path.exists(path):
            fails.append("%s: DSL 未生成" % cap["capability"]); continue
        with open(path, encoding="utf-8") as fh:
            d = yaml.safe_load(fh)
        nodes = {n["id"]: n for n in d["workflow"]["graph"]["nodes"]}

        # V1 保真链：system prompt 必须逐字节包含后继 SKILL 全文
        body = read(cap["skill_path"])
        sysmsg = [m for m in nodes["skill_llm"]["data"]["prompt_template"]
                  if m["role"] == "system"][0]["text"]
        if body.rstrip() not in sysmsg:
            fails.append("%s: system prompt 未逐字节包含后继 SKILL 正文" % cap["capability"])

        # V2 零跨调用：能力子应用内不得有 tool 节点
        tools = [n for n in nodes.values() if n["data"].get("type") == "tool"]
        if tools:
            fails.append("%s: 能力应用内出现 tool 节点（会造成暗跑上游）" % cap["capability"])

        # V3 组件级 Return 路径存在
        if "component_return" not in nodes or "end_component_return" not in nodes:
            fails.append("%s: 缺少组件级 Return 路径" % cap["capability"])

        # V4 reference 加载矩阵一致
        tmpl = nodes["ref_projection"]["data"]["template"]
        load = cap["ref_load"]
        if load["platforms"] == "NONE" and "platforms.md ::" in tmpl:
            fails.append("%s: 加载矩阵声明不加载 platforms，模板却投影了它" % cap["capability"])
        if load["industry"] == "NONE" and "industry-conditions.md ::" in tmpl:
            fails.append("%s: 加载矩阵声明不加载 industry，模板却投影了它" % cap["capability"])
        if load["examples"] == "NEVER" and "examples.md ::" in tmpl:
            fails.append("%s: 加载矩阵声明从不加载 examples，模板却投影了它" % cap["capability"])

        # V5 模型参数一致
        if nodes["skill_llm"]["data"]["model"] != MODEL:
            fails.append("%s: 模型/参数与冻结绑定不一致" % cap["capability"])
        # V5b 恢复投影节点不得单独调参（取证合同 v0.4 §2 硬断言）
        if "recovery_llm" not in nodes:
            fails.append("%s: 缺少 recovery_llm 用户投影节点" % cap["capability"])
        elif nodes["recovery_llm"]["data"]["model"] != MODEL:
            fails.append("%s: recovery_llm 模型/参数与冻结绑定不一致" % cap["capability"])

        # V5e 恢复路径必须剥离 thinking（M4-FND-029）
        _df = nodes.get("delivery_finalize", {}).get("data", {}).get("code", "")
        if "_strip_thinking(recovered_text)" not in _df:
            fails.append("%s: delivery_finalize 未对 recovered_text 做 thinking 剥离（M4-FND-029）"
                         % cap["capability"])
        for _t in ("<think>", "</think>"):
            if _t not in _df:
                fails.append("%s: delivery_finalize 的泄漏词表缺少 %s（M4-FND-029）"
                             % (cap["capability"], _t))

        # V5c 终止分支非空交付（取证合同 v0.5 §3 CL31-01①）
        for nid, n in nodes.items():
            if n["data"].get("type") != "end":
                continue
            vs = [o["variable"] for o in n["data"].get("outputs", [])]
            if "user_delivery" not in vs:
                fails.append("%s: 终止节点 %s 的输出缺少 user_delivery（CL31-01①）"
                             % (cap["capability"], nid))

        # V5d 正式应用不得残留故障注入开关（取证合同 v0.5 §5 F-13）
        blob = json.dumps(d, ensure_ascii=False)
        for sentinel in ("M4_FAULT_DIRECTIVE", "FAULT INJECTION", "fault_injector"):
            if sentinel in blob:
                fails.append("%s: 正式 DSL 残留故障注入标记 %s（F-13）"
                             % (cap["capability"], sentinel))

        # V6 图连通性
        ids = set(nodes)
        for e in d["workflow"]["graph"]["edges"]:
            if e["source"] not in ids or e["target"] not in ids:
                fails.append("%s: 悬空边 %s" % (cap["capability"], e["id"]))

    # 父接缝
    seam_path = os.path.join(DC_WF, "DIYU_M4_CAPABILITY_SEAM_v1_3_TEST.yml")
    if not os.path.exists(seam_path):
        fails.append("SEAM: DSL 未生成")
    else:
        with open(seam_path, encoding="utf-8") as fh:
            s = yaml.safe_load(fh)
        snodes = {n["id"]: n for n in s["workflow"]["graph"]["nodes"]}
        # V7 七入口在分派中可达
        resolver = snodes["entry_resolver"]["data"]["code"]
        for e in ["ENTRY-01", "ENTRY-02", "ENTRY-03", "ENTRY-04", "ENTRY-05", "ENTRY-06", "ENTRY-07"]:
            if e not in resolver:
                fails.append("SEAM: 入口解析器未覆盖 %s" % e)

        # V6c 接缝所有终止分支必须有非空用户交付（取证合同 v0.5 §3 CL31-01①④）
        for nid, n in snodes.items():
            if n["data"].get("type") != "end":
                continue
            vs = [o["variable"] for o in n["data"].get("outputs", [])]
            if "user_delivery" not in vs:
                fails.append("SEAM: 终止节点 %s 的输出缺少 user_delivery（CL31-01①）" % nid)
            if "business_delivery_outcome" not in vs:
                fails.append("SEAM: 终止节点 %s 的输出缺少 business_delivery_outcome（CL31-01④）" % nid)
        # 失败类终止分支的用户正文不得含内部词（CL31-01③）
        LEAKS = ["PARSE_FAIL", "NOT_APPLICABLE", "STALE", "NOT_VERIFIED", "returns_json",
                 "artifact_status", "user_delivery_status", "capability_call",
                 "professional_payload", "goal_family", "skill_llm", "recovery_llm",
                 "returns_adapter", "delivery_finalize", "final_extract", "binding_record",
                 "seam_tool_fail", "end_tool_fail", "system prompt", "sha256", "Judge",
                 "M4_ARTIFACT", "M4_USER_DELIVERY", "M4_RETURNS"]
        for nid in ("seam_tool_fail", "unsupported"):
            if nid not in snodes:
                fails.append("SEAM: 缺少失败终止分支节点 %s" % nid); continue
            code = snodes[nid]["data"].get("code", "")
            i = code.find("user_text = (")
            j = code.find("    ret = {", i) if i >= 0 else -1
            if i < 0 or j < 0:
                fails.append("SEAM: %s 未按约定构造 user_text，无法做泄漏扫描" % nid); continue
            seg = code[i:j]
            for w in LEAKS:
                if w in seg:
                    fails.append("SEAM: %s 的用户正文含内部词 %s（CL31-01③）" % (nid, w))
        # V6d 正式接缝不得残留故障注入开关（F-13）
        sblob = json.dumps(s, ensure_ascii=False)
        for sentinel in ("M4_FAULT_DIRECTIVE", "FAULT INJECTION", "fault_injector"):
            if sentinel in sblob:
                fails.append("SEAM: 正式 DSL 残留故障注入标记 %s（F-13）" % sentinel)
        # V8 provider 绑定状态
        pend = [n["id"] for n in snodes.values()
                if n["data"].get("type") == "tool"
                and n["data"].get("provider_id") == "PENDING_PUBLISH"]
        if pend:
            warns.append("SEAM: %d 个 tool 节点的 provider_id 仍为 PENDING_PUBLISH（子应用尚未发布注册）。"
                         "在此状态下**不得**宣称 Runtime 保真或入口可达成立。" % len(pend))

    # Founder 画布：M1 意图层必须逐字节复用
    canvas_path = os.path.join(DC_WF, "DIYU_M4_FOUNDER_CANVAS_v1_3_TEST.yml")
    if not os.path.exists(canvas_path):
        fails.append("CANVAS: DSL 未生成")
    else:
        with open(canvas_path, encoding="utf-8") as fh:
            cv = yaml.safe_load(fh)
        with open(M1_SOURCE_DSL, encoding="utf-8") as fh:
            m1 = yaml.safe_load(fh)
        cn = {n["id"]: n for n in cv["workflow"]["graph"]["nodes"]}
        mn = {n["id"]: n for n in m1["workflow"]["graph"]["nodes"]}
        for nid in M1_REUSED_NODES:
            if nid not in cn:
                fails.append("CANVAS: 缺少复用的 M1 节点 %s" % nid); continue
            expect = json.loads(json.dumps(mn[nid]["data"]))
            if nid == "v1_state":
                # M4-BLK-002：只有这个节点被授权改动，且差异必须恰好等于两处外科补丁。
                _src = expect["code"]
                expect["code"] = apply_v1_state_patch(_src)
                # M4-FND-001 的第三处补丁同时改了节点输入变量，期望基线要一并算上
                _ev = expect.setdefault("variables", [])
                if not any(v.get("variable") == "patch_text" for v in _ev):
                    _ev.append({"value_selector": ["v1_shadow", "text"],
                                "variable": "patch_text"})
                _bad = verify_v1_state_patch(_src, expect["code"])
                if _bad:
                    fails.append("CANVAS: v1_state 外科补丁越界 -> " + "；".join(_bad))
                _live = cn[nid]["data"].get("code", "")
                if _live == _src:
                    fails.append("CANVAS: v1_state 仍是未解锁的原文（M4-BLK-002 未生效）")
                for _lock in ('"campaign": "matrix"', '"content_brief": "campaign"',
                              '"production_stage1": "content_brief"',
                              '"publishing_stage2": "production_stage1"',
                              '"matrix": "CAMPAIGN"', '"campaign": "CONTENT_BRIEF"',
                              '"content_brief": "PRODUCTION_STAGE1"',
                              '"production_stage1": "PUBLISHING_STAGE2"'):
                    if _lock in _live:
                        fails.append("CANVAS: v1_state 仍残留线性锁片段 %s" % _lock)
                if "DOWNSTREAM_OF_SLOT" not in _live:
                    fails.append("CANVAS: v1_state 的 DOWNSTREAM_OF_SLOT 被误删（A3 保守失效必须保留）")
                if "PATCH_RECOVERED_FROM_TEXT" not in _live:
                    fails.append("CANVAS: v1_state 缺少 M4-FND-001 的 text 兜底（补丁未生效）")
                if not any(v.get("variable") == "patch_text"
                           for v in (cn[nid]["data"].get("variables") or [])):
                    fails.append("CANVAS: v1_state 未接入 patch_text 输入变量（兜底拿不到 text）")
            a = json.dumps(cn[nid]["data"], ensure_ascii=False, sort_keys=True)
            b2 = json.dumps(expect, ensure_ascii=False, sort_keys=True)
            if a != b2:
                fails.append("CANVAS: M1 节点 %s 的 data 与授权基线不一致"
                             "（除已登记的三处外科补丁外必须逐字节复用）" % nid)
        # 画布内不得出现第二个自然语言意图识别节点
        llms = [n for n in cn.values() if n["data"].get("type") == "llm"]
        extra = [n["id"] for n in llms if n["id"] not in ("v1_shadow", "v1_chat_llm")]
        if extra:
            fails.append("CANVAS: 出现额外 LLM 节点 %s（有建第二套意图识别的风险）" % extra)
        seam_tools = [n for n in cn.values() if n["data"].get("type") == "tool"]
        if len(seam_tools) != 1:
            fails.append("CANVAS: 应当只调用统一接缝一个 tool，实际 %d 个" % len(seam_tools))
        elif seam_tools[0]["data"]["provider_id"] == "PENDING_PUBLISH":
            warns.append("CANVAS: 接缝 provider 仍为 PENDING_PUBLISH。")

    print("=" * 70)
    print("FAIL: %d" % len(fails))
    for f in fails:
        print("  [FAIL]", f)
    print("WARN: %d" % len(warns))
    for w in warns:
        print("  [WARN]", w)
    print("=" * 70)
    return 1 if fails else 0


def cmd_bindings():
    b = load_bindings()
    print(json.dumps(b, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "build"
    if cmd == "build":
        cmd_build()
    elif cmd == "verify":
        sys.exit(cmd_verify())
    elif cmd == "bindings":
        cmd_bindings()
    else:
        print(__doc__)
        sys.exit(2)
