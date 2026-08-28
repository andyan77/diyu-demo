#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""M5 跨能力接缝适配器 v0.2 · 能力感知版。

v0.1 只解决了 M3 → Content Brief 一跳，必填清单被写死成 Content Brief 的六项。
实测六个能力应用的确定性外壳校验各有各的必填清单（现场从已发布 graph 读出，不是推测）：

  MATRIX               applicability_reason / subject_and_account_scope / objective /
                       facts_registered / expression_boundary
  CAMPAIGN             objective / deadline_or_stage_boundary / audience_problem /
                       facts_registered / capacity_or_owner
  CONTENT_BRIEF        objective / audience_problem / expected_change / content_promise /
                       facts_registered / expression_subject_and_boundary
  CREATIVE_SCRIPT      objective / expected_change / content_promise / expression_subject /
                       content_origin_mode / facts_registered
  PRODUCTION_DIRECTOR  script_or_equivalent_beats / content_origin_mode / production_profile /
                       time_window / content_promise
  PUBLISHING_PACKAGING content_body_or_beats / content_promise / explicit_non_promise /
                       facts_registered / cta_contract / asset_publish_permission

这就是 M4 冻结的东西：**六个能力之间零调用边**，谁把上一跳的产出接成下一跳的外壳，
M4 没有规定，也不该由 M4 规定——那正是 M5「统一集成」要补的接缝。

三条硬约束（写进 Prompt 与代码，不是注释）：
  1. 只抽取三类**已登记来源**里明确写出的内容：M3 运营判断、上游能力已交付产出、
     已登记事实夹具。原文没写的一律留空并计入 extraction_gaps。
  2. 不推断、不补全、不润色、不跨源搬运。每个字段必须报出它来自哪一个来源。
  3. 外壳用扁平写法，且**只写目标能力实际需要的键**——避免 expression_subject 与
     expression_subject_and_boundary 这类前缀相同的键互相误命中。

受保护资产零改动：不改 M4 八个已发布应用、不改 M3 已发布应用、不改六份 Skill 源文件。
"""
import importlib.util, json, os

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
_p = os.path.join(ROOT, "account-operations", "tools", "dify_client.py")
_s = importlib.util.spec_from_file_location("dc", _p)
DC = importlib.util.module_from_spec(_s)
_s.loader.exec_module(DC)

ENV = "/home/faye/diyu-demo-worktrees/m3-account-content-operator-v1/.env"
APP_NAME = "DIYU M5 TEST CANDIDATE · 跨能力接缝适配器（能力感知抽取）"
MARKED_NAME = "m5-hop-adapt-v0.4"
MARKED_COMMENT = "M5 集成候选 v0.4：补第二条可审计合成规则——上游能力已交付的 artifact 定义上就是对应字段本体；上游身份不匹配或未交付一律不合成"

MODEL = {"mode": "chat", "name": "deepseek-v4-flash",
         "provider": "langgenius/deepseek/deepseek",
         "completion_params": {"top_p": 0.8, "thinking": False,
                               "max_tokens": 32000, "reasoning_effort": "low"}}

FEATURES = {"file_upload": {"enabled": False, "allowed_file_types": ["image"],
                            "allowed_file_extensions": [".JPG", ".JPEG", ".PNG"],
                            "allowed_file_upload_methods": ["local_file", "remote_url"],
                            "image": {"enabled": False, "number_limits": 3,
                                      "transfer_methods": ["local_file", "remote_url"]},
                            "number_limits": 3},
            "opening_statement": "", "retriever_resource": {"enabled": False},
            "sensitive_word_avoidance": {"enabled": False}, "speech_to_text": {"enabled": False},
            "suggested_questions": [], "suggested_questions_after_answer": {"enabled": False},
            "text_to_speech": {"enabled": False, "language": "", "voice": ""}}

EXTRACT_SYSTEM = """你是一个**抽取器**，不是判断者，也不是创作者。

你会拿到最多四个**已登记来源**：
  [M3]  笛语 M3「单账号持续运营」写给 Founder 的运营判断正文
  [UP]  上一个专业能力刚刚交付的产出（可能为空）
  [FACT] 已登记事实夹具：商品、素材、出镜授权、人员产能、时间窗口、明确的不承诺
  [ASK] 用户本轮原话与账号最小当前投影

你的唯一任务：把这四个来源里**已经明确写出来**的业务实质抽成 JSON。

必须遵守：
1. 只抽取来源里明确写出的内容。四个来源都没写的，该字段返回空字符串 ""。
2. **绝对不要推断、补全、润色、扩写或代为判断。宁可留空也不要猜。**
3. 每个非空字段都要在 "_sources" 里标出它来自哪一个来源，只能填 M3 / UP / FACT / ASK。
   一个字段的内容不得由多个来源拼接而成；拼不出来就留空。
4. 尽量用来源原文的表述，可做最小限度截断，不要改写成你自己的话。
5. 不要把「可能」「暂定」「建议」写成确定；不要把没发生的事写成已发生。
6. 「定向补齐」一段**不是来源**，它只告诉你上一轮哪几项没抽到，请你在四个来源里
   再找一遍这几项。**在四个来源里找不到，就仍然留空**——定向补齐不是让你去编。

输出严格 JSON，只输出 JSON 本体，不要代码块围栏，不要解释：

{
 "fields": {
  "primary_goal": "本轮主目标",
  "goal_family": "只能是 LONG_TERM_VALUE/ACCOUNT_STARTUP/FOLLOWER_GROWTH/TRAFFIC/GMV/LEADS/STORE_VISIT/MIXED 之一，不确定填空",
  "applicability_reason": "为什么本轮适用该能力",
  "subject_and_account_scope": "涉及哪些主体与账号范围",
  "audience_problem": "受众当前卡在什么真实问题或场景上",
  "expected_change": "希望受众看完后发生什么变化",
  "content_promise": "这条内容可以承诺给受众什么",
  "facts_registered": "本轮已登记、可用的事实链（商品、素材、试穿、记录编号等）",
  "expression_subject": "由谁出镜或表达",
  "expression_boundary": "表达边界与禁止项",
  "expression_subject_and_boundary": "出镜者＋表达边界合并表述",
  "explicit_non_promise": "明确写出的不承诺什么",
  "content_origin_mode": "内容从哪来：原创拍摄／已登记素材剪辑／二创／引用他人内容等，来源写了才填",
  "script_or_equivalent_beats": "已成稿的脚本或等价的分镜／段落节拍",
  "content_body_or_beats": "已成稿的内容正文或节拍",
  "production_profile": "制作班底与规格约束：几人、几次拍摄、能出几条、有无预算限制",
  "time_window": "时间窗口：几天、什么阶段、确认时效",
  "capacity_or_owner": "谁负责、可投入多少",
  "deadline_or_stage_boundary": "阶段边界或截止条件",
  "cta_contract": "本轮允许的行动号召到什么程度，以及不允许承诺什么（原话）",
  "cta_level": "只能是 NO_CTA/LOW_RISK_INTERACTION/BUSINESS_HANDOFF/HIGH_RISK/KNOWN_BUT_NOT_AUTHORIZED 之一；来源不足以确定就填空",
  "asset_publish_permission": "素材是否可公开发布、谁可出镜、引用需要标注什么"
 },
 "_sources": {"字段名": "M3|UP|FACT|ASK"}
}"""

COMPOSE_CODE = r'''
import json
import re

# 六个能力各自的确定性外壳必填清单。现场从已发布 graph 的 外壳校验 节点读出。
REQUIRED_BY_CAPABILITY = {
    "MATRIX": ["applicability_reason", "subject_and_account_scope", "objective",
               "facts_registered", "expression_boundary"],
    "CAMPAIGN": ["objective", "deadline_or_stage_boundary", "audience_problem",
                 "facts_registered", "capacity_or_owner"],
    "CONTENT_BRIEF": ["objective", "audience_problem", "expected_change", "content_promise",
                      "facts_registered", "expression_subject_and_boundary"],
    "CREATIVE_SCRIPT": ["objective", "expected_change", "content_promise", "expression_subject",
                        "content_origin_mode", "facts_registered"],
    "PRODUCTION_DIRECTOR": ["script_or_equivalent_beats", "content_origin_mode",
                            "production_profile", "time_window", "content_promise"],
    "PUBLISHING_PACKAGING": ["content_body_or_beats", "content_promise", "explicit_non_promise",
                             "facts_registered", "cta_contract", "asset_publish_permission"],
}

# 这些键即使不在必填清单里也值得带上——它们收紧边界，不放松边界。
# 只在不与必填键同名、且不是任何必填键的前缀时才写出，避免正则误命中。
USEFUL_EXTRAS = ["explicit_non_promise", "cta_contract", "asset_publish_permission",
                 "expression_boundary", "capacity_or_owner", "time_window"]

GOAL_FAMILIES = ["LONG_TERM_VALUE", "ACCOUNT_STARTUP", "FOLLOWER_GROWTH", "TRAFFIC",
                 "GMV", "LEADS", "STORE_VISIT", "MIXED"]
CTA_LEVELS = ["NO_CTA", "LOW_RISK_INTERACTION", "BUSINESS_HANDOFF",
              "HIGH_RISK", "KNOWN_BUT_NOT_AUTHORIZED"]
SOURCE_TAGS = ["M3", "UP", "FACT", "ASK"]


def _clean(v):
    if v is None:
        return ""
    s = str(v).strip()
    if s.lower() in ("null", "none", "n/a", "na", "待定", "无", "未写", "未登记"):
        return ""
    return re.sub(r"\s+", " ", s)


def _parse(raw):
    t = (raw or "").strip()
    t = re.sub(r"^```(?:json)?\s*", "", t)
    t = re.sub(r"\s*```$", "", t)
    m = re.search(r"\{.*\}", t, re.S)
    if not m:
        return {}, {}, "extractor_output_not_json"
    try:
        obj = json.loads(m.group(0))
    except Exception as e:
        return {}, {}, "extractor_json_parse_failed: %s" % (str(e)[:120],)
    if isinstance(obj.get("fields"), dict):
        return obj["fields"], (obj.get("_sources") or {}), ""
    # 抽取器直接给了扁平 JSON 也接受，来源标记按未声明处理
    return obj, {}, "extractor_returned_flat_json_without_sources"


def main(extract_raw, target_capability, m3_judgment, upstream_delivery,
         upstream_capability, registered_facts, account_context, user_request, focus_fields):
    cap = (target_capability or "").strip().upper()
    if cap not in REQUIRED_BY_CAPABILITY:
        return {"capability_call": "", "professional_input": "",
                "extraction_gaps_text": "target_capability 非法：%s" % cap,
                "extraction_gaps_count": 99, "adapter_note": "unknown_capability",
                "extracted_json": "{}", "source_map_json": "{}"}

    raw, srcs, parse_note = _parse(extract_raw)
    required = REQUIRED_BY_CAPABILITY[cap]

    keys = ["primary_goal", "goal_family", "applicability_reason", "subject_and_account_scope",
            "audience_problem", "expected_change", "content_promise", "facts_registered",
            "expression_subject", "expression_boundary", "expression_subject_and_boundary",
            "explicit_non_promise", "content_origin_mode", "script_or_equivalent_beats",
            "content_body_or_beats", "production_profile", "time_window", "capacity_or_owner",
            "deadline_or_stage_boundary", "cta_contract", "cta_level",
            "asset_publish_permission"]
    f = {k: _clean(raw.get(k)) for k in keys}

    if f["goal_family"].upper() in GOAL_FAMILIES:
        f["goal_family"] = f["goal_family"].upper()
    else:
        f["goal_family"] = ""
    # cta_level 是枚举，cta_contract 是原话。能力侧先读 cta_level 再回落到 cta_contract，
    # 所以两个都写出来：枚举给机器判级，原话给 Skill 作专业裁决，互不替代。
    if f["cta_level"].upper() in CTA_LEVELS:
        f["cta_level"] = f["cta_level"].upper()
    else:
        f["cta_level"] = ""

    # 来源标记越界一律降为 UNDECLARED，不代填
    smap = {}
    for k in keys:
        if not f[k]:
            continue
        tag = str(srcs.get(k, "")).strip().upper()
        smap[k] = tag if tag in SOURCE_TAGS else "UNDECLARED"

    # ---- 唯一一条允许的合成规则 ----
    # expression_subject_and_boundary 的定义就是「出镜者＋表达边界」。两个部件都已从
    # 已登记来源抽到时，把它们拼成复合字段是**格式化**，不是编造：没有引入任何新事实，
    # 且合成事实记进 source_map 可审计。任一部件缺失一律不合成，照旧计入缺口。
    if (not f["expression_subject_and_boundary"]
            and f["expression_subject"] and f["expression_boundary"]):
        f["expression_subject_and_boundary"] = "%s；%s" % (f["expression_subject"],
                                                          f["expression_boundary"])
        smap["expression_subject_and_boundary"] = "DERIVED(expression_subject+expression_boundary)"

    # ---- 第二条允许的合成规则：能力身份即字段身份 ----
    # CREATIVE_SCRIPT 这个能力**交付**出来的 artifact，定义上就是脚本本身；
    # PRODUCTION_DIRECTOR 交付的就是可执行的制作内容本体。因此当上一跳正是这些
    # 能力且确实已交付时，把它的产物本体作为下一跳对应字段的值，
    # **不是编造**——没有引入任何新事实，值就是上游能力自己交付的产物。
    # 上游身份不匹配、或上游根本没交付时一律不合成，照旧计入缺口。
    up_cap = (upstream_capability or "").strip().upper()
    up_text = _clean(upstream_delivery)
    ARTIFACT_IS_FIELD = {
        "CREATIVE_SCRIPT": ["script_or_equivalent_beats", "content_body_or_beats"],
        "PRODUCTION_DIRECTOR": ["content_body_or_beats"],
    }
    for key in ARTIFACT_IS_FIELD.get(up_cap, []):
        if key in required and not f.get(key) and up_text:
            f[key] = up_text[:6000]
            smap[key] = "DERIVED(upstream_%s_artifact)" % up_cap

    # ---- 组装扁平外壳：只写目标能力真正需要的键 + 不放松边界的附加键 ----
    lines = ["provenance:",
             "  source_kind: M3_OPERATION",
             "  source_ref: m5_hop_adapter_v0.2",
             "  confirmation_state: EXTRACTED_FROM_REGISTERED_SOURCES",
             "  target_capability: " + cap]

    def kv(key, val):
        # 写成 Markdown 反引号形状 `key`: value。
        # 为什么不是 YAML 平铺：能力侧 _find_scalar 的 YAML 分支，捕获组用的字符类
        # 把 ASCII 单双引号排除在外，而 M3 的判断里大量出现 '…' 这类引用。
        # 一旦值里带引号，正则在第一个引号处截断且无法回溯，整行被判为不在场
        # ——硬门假阴性。实测四项缺失里有三项栽在这上面。
        # 它的第三条分支 `key`: value 的捕获组接受除换行外的任意字符。
        # 改用第三种形状，值一个字都不改就能被读到，也不需要动 M4 任何已发布应用。
        return "`%s`: %s" % (key, val)

    written = set()
    if "objective" in required:
        lines.append("objective:")
        lines.append("  `primary_goal`: " + (f["primary_goal"] or "（已登记来源中未明确写出）"))
        if f["goal_family"]:
            lines.append("  goal_family: " + f["goal_family"])
        written.add("objective")

    for key in required:
        if key == "objective" or not f.get(key):
            continue
        lines.append(kv(key, f[key]))
        written.add(key)

    def collides(k):
        # 与已写出的键同名，或与任一必填键构成前缀关系，都不再重复写出
        if k in written:
            return True
        for r in required:
            if r.startswith(k) or k.startswith(r):
                return True
        return False

    for key in USEFUL_EXTRAS:
        if f.get(key) and not collides(key):
            lines.append(kv(key, f[key]))
            written.add(key)

    if f["cta_level"] and "cta_level" not in written:
        lines.append("cta_level: " + f["cta_level"])
        written.add("cta_level")
    lines.append("platform: NOT_LOCKED")
    lines.append("equivalence_basis: 持续运营决策直接给出单条内容任务核心；跨能力接缝由 M5 抽取适配落成统一外壳")
    envelope = "\n".join(lines)

    # ---- 缺口只按目标能力的必填清单算，如实上报 ----
    gaps = []
    for key in required:
        if key == "objective":
            if not f["primary_goal"]:
                gaps.append("objective.primary_goal")
        elif not f.get(key):
            gaps.append(key)
    if "objective" in required and not f["goal_family"]:
        gaps.append("objective.goal_family(未声明，不代为推断)")

    # ---- 专业输入：原文照带，标清楚哪段是哪个来源，不合并、不改写 ----
    parts = []
    if m3_judgment:
        parts.append("## [M3] 运营判断原文（未经改写）\n" + m3_judgment)
    if upstream_delivery:
        parts.append("## [UP] 上一个专业能力的已交付产出（未经改写）\n" + upstream_delivery)
    if registered_facts:
        parts.append("## [FACT] 已登记事实夹具（未经改写）\n" + registered_facts)
    if account_context:
        parts.append("## [ASK] 账号最小当前投影（M2 实时读取）\n" + account_context)
    if user_request:
        parts.append("## [ASK] 用户本轮原话\n" + user_request)
    prof = "\n\n".join(parts)

    note = parse_note or ("按 %s 的必填清单抽取；空字段一律计入 extraction_gaps，未代为推断" % cap)
    if focus_fields:
        note += "；本轮为定向补齐：%s" % str(focus_fields)[:200]

    return {
        "capability_call": envelope,
        "professional_input": prof,
        "extraction_gaps_text": "；".join(gaps) if gaps else "无",
        "extraction_gaps_count": len(gaps),
        "adapter_note": note,
        "extracted_json": json.dumps(f, ensure_ascii=False),
        "source_map_json": json.dumps(smap, ensure_ascii=False),
    }
'''


def build_graph():
    start = {
        "id": "m5_start", "type": "custom", "position": {"x": 80, "y": 200},
        "width": 244, "height": 160, "selected": False,
        "data": {"type": "start", "title": "输入", "desc": "目标能力 + 四类已登记来源",
                 "variables": [
                     {"variable": "target_capability", "label": "目标专业能力", "type": "text-input",
                      "required": True, "max_length": 64, "options": []},
                     {"variable": "m3_judgment", "label": "[M3] 运营判断正文", "type": "paragraph",
                      "required": False, "max_length": 60000, "options": []},
                     {"variable": "upstream_delivery", "label": "[UP] 上游能力已交付产出",
                      "type": "paragraph", "required": False, "max_length": 60000, "options": []},
                     {"variable": "upstream_capability", "label": "上游能力身份（哪个能力交付了 UP）",
                      "type": "text-input", "required": False, "max_length": 64, "options": []},
                     {"variable": "registered_facts", "label": "[FACT] 已登记事实夹具",
                      "type": "paragraph", "required": False, "max_length": 60000, "options": []},
                     {"variable": "account_context", "label": "[ASK] 账号最小当前投影",
                      "type": "paragraph", "required": False, "max_length": 60000, "options": []},
                     {"variable": "user_request", "label": "[ASK] 用户本轮原话", "type": "paragraph",
                      "required": False, "max_length": 20000, "options": []},
                     {"variable": "focus_fields", "label": "定向补齐字段（不是来源）",
                      "type": "paragraph", "required": False, "max_length": 2000, "options": []},
                 ]}}
    extract = {
        "id": "m5_extract", "type": "custom", "position": {"x": 400, "y": 200},
        "width": 244, "height": 120, "selected": False,
        "data": {"type": "llm", "title": "抽取器｜只抽不推断", "desc": "从四类已登记来源抽取业务实质并标注来源",
                 "model": MODEL, "vision": {"enabled": False},
                 "context": {"enabled": False, "variable_selector": []},
                 "prompt_template": [
                     {"role": "system", "text": EXTRACT_SYSTEM, "id": "sys-1"},
                     {"role": "user", "id": "usr-1",
                      "text": "本次要进入的专业能力：{{#m5_start.target_capability#}}\n\n"
                              "===== [M3] 运营判断正文 =====\n{{#m5_start.m3_judgment#}}\n\n"
                              "（上一个专业能力是：{{#m5_start.upstream_capability#}}）\n"
                              "===== [UP] 上一个专业能力的已交付产出 =====\n"
                              "{{#m5_start.upstream_delivery#}}\n\n"
                              "===== [FACT] 已登记事实夹具 =====\n{{#m5_start.registered_facts#}}\n\n"
                              "===== [ASK] 账号最小当前投影 =====\n{{#m5_start.account_context#}}\n\n"
                              "===== [ASK] 用户本轮原话 =====\n{{#m5_start.user_request#}}\n\n"
                              "===== 定向补齐（这不是来源，只是告诉你哪几项上一轮没抽到） =====\n"
                              "{{#m5_start.focus_fields#}}\n\n"
                              "只输出 JSON。四个来源都没写的字段一律空字符串，并且不要出现在 _sources 里。"}],
                 }}
    compose = {
        "id": "m5_compose", "type": "custom", "position": {"x": 720, "y": 200},
        "width": 244, "height": 120, "selected": False,
        "data": {"type": "code", "title": "按目标能力组装扁平外壳",
                 "desc": "只写该能力真正需要的键；缺口如实上报，不代为推断",
                 "code_language": "python3", "code": COMPOSE_CODE,
                 "variables": [
                     {"variable": "extract_raw", "value_selector": ["m5_extract", "text"]},
                     {"variable": "target_capability", "value_selector": ["m5_start", "target_capability"]},
                     {"variable": "m3_judgment", "value_selector": ["m5_start", "m3_judgment"]},
                     {"variable": "upstream_delivery", "value_selector": ["m5_start", "upstream_delivery"]},
                     {"variable": "upstream_capability", "value_selector": ["m5_start", "upstream_capability"]},
                     {"variable": "registered_facts", "value_selector": ["m5_start", "registered_facts"]},
                     {"variable": "account_context", "value_selector": ["m5_start", "account_context"]},
                     {"variable": "user_request", "value_selector": ["m5_start", "user_request"]},
                     {"variable": "focus_fields", "value_selector": ["m5_start", "focus_fields"]},
                 ],
                 "outputs": {
                     "capability_call": {"type": "string", "children": None},
                     "professional_input": {"type": "string", "children": None},
                     "extraction_gaps_text": {"type": "string", "children": None},
                     "extraction_gaps_count": {"type": "number", "children": None},
                     "adapter_note": {"type": "string", "children": None},
                     "extracted_json": {"type": "string", "children": None},
                     "source_map_json": {"type": "string", "children": None},
                 }}}
    end = {
        "id": "m5_end", "type": "custom", "position": {"x": 1040, "y": 200},
        "width": 244, "height": 120, "selected": False,
        "data": {"type": "end", "title": "输出统一能力外壳",
                 "outputs": [
                     {"variable": "capability_call", "value_selector": ["m5_compose", "capability_call"]},
                     {"variable": "professional_input", "value_selector": ["m5_compose", "professional_input"]},
                     {"variable": "extraction_gaps_text", "value_selector": ["m5_compose", "extraction_gaps_text"]},
                     {"variable": "extraction_gaps_count", "value_selector": ["m5_compose", "extraction_gaps_count"]},
                     {"variable": "adapter_note", "value_selector": ["m5_compose", "adapter_note"]},
                     {"variable": "extracted_json", "value_selector": ["m5_compose", "extracted_json"]},
                     {"variable": "source_map_json", "value_selector": ["m5_compose", "source_map_json"]},
                 ]}}

    def edge(s, t, st_, tt):
        return {"id": "%s-source-%s-target" % (s, t), "type": "custom", "source": s, "target": t,
                "sourceHandle": "source", "targetHandle": "target", "zIndex": 0,
                "data": {"sourceType": st_, "targetType": tt, "isInIteration": False}}

    return {"nodes": [start, extract, compose, end],
            "edges": [edge("m5_start", "m5_extract", "start", "llm"),
                      edge("m5_extract", "m5_compose", "llm", "code"),
                      edge("m5_compose", "m5_end", "code", "end")],
            "viewport": {"x": 0, "y": 0, "zoom": 0.8}}


def main():
    c = DC.Console(env=DC.load_env(ENV))
    st, apps = c.call("GET", "/console/api/apps?page=1&limit=100")
    assert st == 200, (st, apps)
    hit = [a for a in apps["data"] if a.get("name") == APP_NAME]
    if hit:
        app_id = hit[0]["id"]
        print("reuse existing app", app_id)
    else:
        st, app = c.call("POST", "/console/api/apps", body={
            "name": APP_NAME, "mode": "workflow", "icon_type": "emoji", "icon": "🧩",
            "icon_background": "#FFEAD5",
            "description": "M5 集成候选：按目标能力的必填清单，从已登记来源抽取扁平统一能力外壳。"
                           "只抽取不推断，缺口如实上报。"})
        assert st in (200, 201), (st, app)
        app_id = app["id"]
        print("created app", app_id)

    st, cur = c.call("GET", "/console/api/apps/%s/workflows/draft" % app_id)
    prev_hash = cur.get("hash") if st == 200 else None
    st, res = c.call("POST", "/console/api/apps/%s/workflows/draft" % app_id, body={
        "graph": build_graph(), "features": FEATURES, "hash": prev_hash,
        "environment_variables": [], "conversation_variables": []}, timeout=300)
    assert st == 200, ("draft sync failed", st, json.dumps(res, ensure_ascii=False)[:500])
    print("DRAFT SYNCED")

    st, pub = c.call("POST", "/console/api/apps/%s/workflows/publish" % app_id,
                     body={"marked_name": MARKED_NAME, "marked_comment": MARKED_COMMENT},
                     timeout=300)
    assert st in (200, 201), ("publish failed", st, json.dumps(pub, ensure_ascii=False)[:500])
    print("PUBLISHED")
    print("APP_ID", app_id)
    return app_id


if __name__ == "__main__":
    main()
