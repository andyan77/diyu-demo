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
        artifact_status = "OK"

    if user_delivery is None:
        user_out = ""
        user_status = "MISSING"
    elif leaks:
        user_out = user_delivery
        user_status = "LEAK_DETECTED"
    else:
        user_out = user_delivery
        user_status = "OK"

    blocked = (
        ret_status == "PARSE_FAILED"
        or artifact_status != "OK"
        or user_status != "OK"
    )

    return {
        "artifact": artifact_out,
        "artifact_status": artifact_status,
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

BINDING_RECORD_CODE = r'''
import hashlib
import json

# AC-12 保真绑定记录（源 Skill → Workflow → Runtime → 模型 → provider → Attempt）
# 自报值只作声明；正式判定以从已发布 Runtime 实际读出的字节为准（N-19）。

RECORD = __BINDING_RECORD__


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
         tool_artifact, tool_user_delivery, tool_returns_json, tool_binding_json, call_hash):
    invoked = [capability_resolved]
    skipped = [c for c in ALL_CAPS if c != capability_resolved]

    try:
        rets = json.loads(tool_returns_json or "[]")
    except Exception:
        rets = []

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
    }

    return {
        "seam_trace_json": json.dumps(trace, ensure_ascii=False, sort_keys=True),
        "capability_invoked": capability_resolved,
        "capabilities_skipped": skipped,
        "artifact": tool_artifact or "",
        "user_delivery": tool_user_delivery or "",
        "returns_json": tool_returns_json or "[]",
        "binding_json": tool_binding_json or "{}",
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
    bind_code = BINDING_RECORD_CODE.replace(
        "__BINDING_RECORD__", json.dumps(binding_record, ensure_ascii=False, sort_keys=True))

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
            "user_delivery": out_str(), "user_delivery_status": out_str(),
            "user_delivery_leaks": out_arr(), "returns_json": out_str(),
            "returns_status": out_str(), "returns_parse_note": out_str(),
            "returns_raw": out_str(), "raw_preserved": out_str(),
            "local_block": out_str(), "structure_notes": out_arr(), "capability": out_str(),
        },
        "selected": False, "title": "Returns / 交付适配器", "type": "code",
        "variables": [{"value_selector": ["final_extract", "output"], "variable": "final_text"}],
    }, 2140, 220))

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
            {"value_selector": ["returns_adapter", "user_delivery"], "variable": "user_delivery"},
            {"value_selector": ["returns_adapter", "user_delivery_status"], "variable": "user_delivery_status"},
            {"value_selector": ["returns_adapter", "user_delivery_leaks"], "variable": "user_delivery_leaks"},
            {"value_selector": ["returns_adapter", "returns_json"], "variable": "returns_json"},
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
    edges.append(edge("returns_adapter", "binding_record", "code", "code"))
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
                        "user_delivery": out_str(), "returns_json": out_str(),
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
            ],
        }, 1300, y))

        nodes.append(node(end_id, {
            "desc": "%s 结束" % c["capability"], "outputs": [
                {"value_selector": [fin_id, "user_delivery"], "variable": "user_delivery"},
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
        "code": (
            "def main(route, derivation):\n"
            "    return {\n"
            "        'failure_kind': 'TOOL_CALL_FAILED',\n"
            "        'note': ('能力应用调用失败。这是执行失败，不是业务不足：'\n"
            "                 '不得伪装成 INPUT_INSUFFICIENT，也不得伪装成空结果。'),\n"
            "        'capability': route,\n"
            "        'derivation': derivation,\n"
            "        'fabricated_artifact_produced': 'false',\n"
            "    }\n"),
        "code_language": "python3",
        "desc": "Tool 调用失败：如实标记为执行失败，不伪装成业务不足或空结果。",
        "outputs": {"failure_kind": out_str(), "note": out_str(), "capability": out_str(),
                    "derivation": out_str(), "fabricated_artifact_produced": out_str()},
        "selected": False, "title": "执行失败", "type": "code",
        "variables": [{"value_selector": ["entry_resolver", "route"], "variable": "route"},
                      {"value_selector": ["entry_resolver", "derivation"], "variable": "derivation"}],
    }, 1300, y + 40))

    nodes.append(node("end_tool_fail", {
        "desc": "执行失败结束", "outputs": [
            {"value_selector": ["seam_tool_fail", "failure_kind"], "variable": "failure_kind"},
            {"value_selector": ["seam_tool_fail", "note"], "variable": "note"},
            {"value_selector": ["seam_tool_fail", "capability"], "variable": "capability"},
            {"value_selector": ["seam_tool_fail", "fabricated_artifact_produced"],
             "variable": "fabricated_artifact_produced"},
        ], "selected": False, "title": "结束｜执行失败", "type": "end",
    }, 1620, y + 40))

    nodes.append(node("unsupported", {
        "code": (
            "def main(route, derivation):\n"
            "    return {\n"
            "        'note': ('capability 不在 M4 接缝支持的六项能力内。'\n"
            "                 'M4 不代做能力选择——那是 M1 的职责；本接缝也不建第二套路由。'),\n"
            "        'capability': route,\n"
            "        'derivation': derivation,\n"
            "    }\n"),
        "code_language": "python3",
        "desc": "不支持的能力调用意图：如实拒绝，不代做 M1 的能力选择。",
        "outputs": {"note": out_str(), "capability": out_str(), "derivation": out_str()},
        "selected": False, "title": "不支持的能力", "type": "code",
        "variables": [{"value_selector": ["entry_resolver", "route"], "variable": "route"},
                      {"value_selector": ["entry_resolver", "derivation"], "variable": "derivation"}],
    }, 960, y + 40))

    nodes.append(node("end_unsupported", {
        "desc": "不支持结束", "outputs": [
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
    bad = []
    a = src_code.splitlines()
    b = patched_code.splitlines()
    if len(a) != len(b):
        bad.append("行数变化 %d -> %d（补丁必须逐行等量替换）" % (len(a), len(b)))
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
            a = json.dumps(cn[nid]["data"], ensure_ascii=False, sort_keys=True)
            b2 = json.dumps(expect, ensure_ascii=False, sort_keys=True)
            if a != b2:
                fails.append("CANVAS: M1 节点 %s 的 data 与授权基线不一致"
                             "（除 M4-BLK-002 两处外科补丁外必须逐字节复用）" % nid)
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
