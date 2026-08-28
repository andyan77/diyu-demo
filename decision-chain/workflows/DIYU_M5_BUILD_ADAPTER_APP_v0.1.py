#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""建立 M5 测试候选应用：M3 运营判断 → M4 统一能力外壳（抽取适配）。

**为什么需要它**（诊断证据见 M5_NODE3_DIAGNOSTIC_FINDINGS_v1.0.md）：

Content Brief 能力的确定性外壳校验要求六个业务语义在场：
    objective / audience_problem / expected_change / content_promise /
    facts_registered / expression_subject_and_boundary
其中 audience_problem / expected_change / content_promise 恰好是 M1 声明**自己不抽取**的
三项（CONTENT_TASK_CALLER_SUPPLIED_KEYS），必须由上游供给；而 M3 的已发布应用只产出
自然语言 operating_judgment，不产出 schema 规定的结构化 content task。

本应用只做一件事：把 M3 已经写在判断里的业务实质，**抽取**成能力侧可识别的扁平外壳。

三条硬约束写进 Prompt 与代码，不是注释：
  1. 只抽取 M3 判断里**已明确写出**的内容；没写的一律留空，计入 extraction_gaps。
  2. 不推断、不补全、不润色、不合并同类项、不代 M3 作专业判断。
  3. 外壳用**扁平**写法（YAML 风格顶层键），因为能力侧的 envelope_check 只认
     `"key":"字符串"` / `key: value` / `key:` 块三种形状；嵌套 JSON 对象它看不见。

受保护资产零改动：不改 M4 八个已发布应用，不改 M3 已发布应用，不改六份 Skill 源文件。
"""
import importlib.util, json, os, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
DC = importlib.util.module_from_spec(
    importlib.util.spec_from_file_location("dc", os.path.join(ROOT, "account-operations", "tools", "dify_client.py")))
importlib.util.spec_from_file_location("dc", os.path.join(ROOT, "account-operations", "tools", "dify_client.py")).loader.exec_module(DC)

ENV = "/home/faye/diyu-demo-worktrees/m3-account-content-operator-v1/.env"
APP_NAME = "DIYU M5 TEST CANDIDATE · M3 判断 → 统一能力外壳（抽取适配）"
MARKED_NAME = "m5-adapter-v0.1"
MARKED_COMMENT = "M5 集成候选：把 M3 运营判断抽取成扁平统一能力外壳；只抽取不推断"

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

EXTRACT_SYSTEM = """你是一个**抽取器**，不是判断者。

输入是笛语 M3「单账号持续运营」能力写给 Founder 的运营判断正文。
你的唯一任务：把其中**已经明确写出来**的业务实质，抽成 JSON。

必须遵守：
1. 只抽取原文明确写出的内容。原文没写的，该字段返回空字符串 ""。
2. **绝对不要推断、补全、润色、扩写或代为判断。** 宁可留空也不要猜。
3. 不要把你自己的话写进去。尽量用原文的表述，可做最小限度的截断。
4. 不要合并不同意思的句子，也不要把「可能」「暂定」写成确定。

输出严格的 JSON，只输出 JSON 本体，不要代码块围栏，不要解释：

{
  "audience_problem": "目标受众当前卡在什么真实问题/场景上（原文写了才填）",
  "expected_change": "希望受众看完后发生什么变化（原文写了才填）",
  "content_promise": "这条内容可以承诺给受众什么（原文写了才填）",
  "facts_registered": "本轮已登记、可用的事实链（原文写了才填）",
  "expression_subject_and_boundary": "由谁出镜/表达，以及表达边界与禁止项（原文写了才填）",
  "primary_goal": "本轮主目标（原文写了才填）",
  "goal_family": "只能是 LONG_TERM_VALUE/ACCOUNT_STARTUP/FOLLOWER_GROWTH/TRAFFIC/GMV/LEADS/STORE_VISIT/MIXED 之一；原文不足以确定就填空字符串",
  "cta_level": "只能是 NO_CTA/LOW_RISK_INTERACTION/BUSINESS_HANDOFF/HIGH_RISK/KNOWN_BUT_NOT_AUTHORIZED 之一；不确定就填空字符串",
  "explicit_non_promise": "原文明确写了不承诺什么（写了才填）",
  "capacity_or_owner": "产能/班底/时间约束（写了才填）"
}"""

COMPOSE_CODE = r'''
import json
import re

# M3 判断 → M4 统一能力外壳（扁平写法）
#
# 为什么必须扁平：能力侧 envelope_check 的 _find_scalar 只认三种形状——
#   "key": "字符串" / key: value 行 / `key`: value ——外加 key: 独占一行的缩进块。
# 嵌套 JSON 对象（如 {"objective": {...}}）它一个都取不到，六项必填会全判缺失。
# 这一条是离线用同一套正则复算过的，不是推测。

REQUIRED = ["objective", "audience_problem", "expected_change",
            "content_promise", "facts_registered", "expression_subject_and_boundary"]

GOAL_FAMILIES = ["LONG_TERM_VALUE", "ACCOUNT_STARTUP", "FOLLOWER_GROWTH", "TRAFFIC",
                 "GMV", "LEADS", "STORE_VISIT", "MIXED"]
CTA_LEVELS = ["NO_CTA", "LOW_RISK_INTERACTION", "BUSINESS_HANDOFF",
              "HIGH_RISK", "KNOWN_BUT_NOT_AUTHORIZED"]


def _clean(v):
    if v is None:
        return ""
    s = str(v).strip()
    if s.lower() in ("null", "none", "n/a", "na", "待定", "无"):
        return ""
    return re.sub(r"\s+", " ", s)


def _parse(raw):
    t = (raw or "").strip()
    t = re.sub(r"^```(?:json)?\s*", "", t)
    t = re.sub(r"\s*```$", "", t)
    m = re.search(r"\{.*\}", t, re.S)
    if not m:
        return {}, "extractor_output_not_json"
    try:
        return json.loads(m.group(0)), ""
    except Exception as e:
        return {}, "extractor_json_parse_failed: %s" % (str(e)[:120],)


def main(extract_raw, m3_judgment, account_context, user_request):
    data, parse_note = _parse(extract_raw)

    f = {k: _clean(data.get(k)) for k in [
        "audience_problem", "expected_change", "content_promise", "facts_registered",
        "expression_subject_and_boundary", "primary_goal", "goal_family", "cta_level",
        "explicit_non_promise", "capacity_or_owner"]}

    # 枚举越界一律降回未声明，不硬塞
    if f["goal_family"].upper() not in GOAL_FAMILIES:
        f["goal_family"] = ""
    else:
        f["goal_family"] = f["goal_family"].upper()
    if f["cta_level"].upper() not in CTA_LEVELS:
        f["cta_level"] = ""
    else:
        f["cta_level"] = f["cta_level"].upper()

    lines = ["provenance:",
             "  source_kind: M3_OPERATION",
             "  source_ref: m5_m3_to_capability_adapter",
             "  confirmation_state: EXTRACTED_FROM_M3_JUDGMENT",
             "objective:"]
    lines.append("  primary_goal: " + (f["primary_goal"] or "（M3 判断中未明确写出）"))
    if f["goal_family"]:
        lines.append("  goal_family: " + f["goal_family"])

    for key in ["audience_problem", "expected_change", "content_promise",
                "facts_registered", "expression_subject_and_boundary"]:
        if f[key]:
            lines.append("%s: %s" % (key, f[key]))

    if f["capacity_or_owner"]:
        lines.append("capacity_or_owner: " + f["capacity_or_owner"])
    if f["explicit_non_promise"]:
        lines.append("explicit_non_promise: " + f["explicit_non_promise"])
    if f["cta_level"]:
        lines.append("cta_level: " + f["cta_level"])
    lines.append("platform: NOT_LOCKED")
    lines.append("equivalence_basis: 持续运营决策直接给出单条内容任务核心；由 M5 抽取适配落成统一外壳")

    envelope = "\n".join(lines)

    # 缺口如实上报：只看六项必填
    gaps = []
    if not f["primary_goal"]:
        gaps.append("objective.primary_goal")
    for key in ["audience_problem", "expected_change", "content_promise",
                "facts_registered", "expression_subject_and_boundary"]:
        if not f[key]:
            gaps.append(key)
    if not f["goal_family"]:
        gaps.append("objective.goal_family(未声明，不代为推断)")
    if not f["cta_level"]:
        gaps.append("cta_level(未声明，按能力侧默认处理)")

    prof = "## M3 运营判断原文（未经改写）\n" + (m3_judgment or "")
    if account_context:
        prof += "\n\n## 账号最小当前投影（M2 实时读取）\n" + account_context
    if user_request:
        prof += "\n\n## 用户本轮原话\n" + user_request

    note = parse_note or "抽取完成；空字段一律计入 extraction_gaps，未代为推断"

    return {
        "capability_call": envelope,
        "professional_input": prof,
        "extraction_gaps_text": "；".join(gaps) if gaps else "无",
        "extraction_gaps_count": len(gaps),
        "adapter_note": note,
        "extracted_json": json.dumps(f, ensure_ascii=False),
    }
'''


def build_graph():
    start = {
        "id": "m5_start", "type": "custom", "position": {"x": 80, "y": 200},
        "width": 244, "height": 120, "selected": False,
        "data": {"type": "start", "title": "输入", "desc": "M3 判断 + M2 投影 + 用户原话",
                 "variables": [
                     {"variable": "m3_judgment", "label": "M3 运营判断正文", "type": "paragraph",
                      "required": True, "max_length": 60000, "options": []},
                     {"variable": "account_context", "label": "账号最小当前投影", "type": "paragraph",
                      "required": False, "max_length": 60000, "options": []},
                     {"variable": "user_request", "label": "用户本轮原话", "type": "paragraph",
                      "required": False, "max_length": 20000, "options": []},
                 ]}}
    extract = {
        "id": "m5_extract", "type": "custom", "position": {"x": 400, "y": 200},
        "width": 244, "height": 120, "selected": False,
        "data": {"type": "llm", "title": "抽取器｜只抽不推断", "desc": "从 M3 判断抽取业务实质",
                 "model": MODEL, "vision": {"enabled": False},
                 "context": {"enabled": False, "variable_selector": []},
                 "prompt_template": [
                     {"role": "system", "text": EXTRACT_SYSTEM, "id": "sys-1"},
                     {"role": "user", "id": "usr-1",
                      "text": "M3 运营判断正文如下：\n\n{{#m5_start.m3_judgment#}}\n\n"
                              "（参考）账号最小当前投影：\n{{#m5_start.account_context#}}\n\n"
                              "（参考）用户本轮原话：\n{{#m5_start.user_request#}}\n\n"
                              "只输出 JSON。原文没写的字段一律空字符串。"}],
                 }}
    compose = {
        "id": "m5_compose", "type": "custom", "position": {"x": 720, "y": 200},
        "width": 244, "height": 120, "selected": False,
        "data": {"type": "code", "title": "组装扁平统一能力外壳",
                 "desc": "扁平写法；缺口如实上报，不代为推断",
                 "code_language": "python3", "code": COMPOSE_CODE,
                 "variables": [
                     {"variable": "extract_raw", "value_selector": ["m5_extract", "text"]},
                     {"variable": "m3_judgment", "value_selector": ["m5_start", "m3_judgment"]},
                     {"variable": "account_context", "value_selector": ["m5_start", "account_context"]},
                     {"variable": "user_request", "value_selector": ["m5_start", "user_request"]},
                 ],
                 "outputs": {
                     "capability_call": {"type": "string", "children": None},
                     "professional_input": {"type": "string", "children": None},
                     "extraction_gaps_text": {"type": "string", "children": None},
                     "extraction_gaps_count": {"type": "number", "children": None},
                     "adapter_note": {"type": "string", "children": None},
                     "extracted_json": {"type": "string", "children": None},
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
            "description": "M5 集成候选：把 M3 运营判断抽取成 M4 统一能力外壳。只抽取不推断，缺口如实上报。"})
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
                     body={"marked_name": MARKED_NAME, "marked_comment": MARKED_COMMENT}, timeout=300)
    assert st in (200, 201), ("publish failed", st, json.dumps(pub, ensure_ascii=False)[:500])
    print("PUBLISHED", json.dumps(pub, ensure_ascii=False)[:200])
    print("APP_ID", app_id)
    return app_id


if __name__ == "__main__":
    main()
