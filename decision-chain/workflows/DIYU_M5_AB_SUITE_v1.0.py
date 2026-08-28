#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""M5 两级 A/B · AB-M3-01（运营判断）与 AB-FINAL-01（最终成品）。

**A 组必须是一个真正好的 Prompt，不能是稻草人。** 一个赢不过稻草人的对照说明不了
任何事；本文件里的 A 组 Prompt 按「一个懂行的人认真写一遍」的标准写，
并且拿到与 B 组**完全相同**的模型、输入、事实、权限与参数。

**执行侧只产出盲评包，不产出分数。** 合同明写：模型自评无效；实现者知道映射的
评分无效。我既是实现者又知道映射，所以我给的任何分数都无效——这不是谦虚，是判据。
本文件把 A/B 映射写进单独的封存文件，盲评包里只有甲/乙。
"""
import hashlib, importlib.util, json, os, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
def _load(n, p):
    s = importlib.util.spec_from_file_location(n, p); m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m); return m
FS = _load("fs", os.path.join(ROOT, "decision-chain", "workflows", "DIYU_M5_FULL_STORY_v0.1.py"))
DE = _load("de", os.path.join(ROOT, "decision-chain", "workflows",
                              "DIYU_M5_DIRECT_ENTRY_SUITE_v1.0.py"))
RT = FS.RT
DC = RT.DC
ENV = RT.DIFY_ENV
EV = os.path.join(ROOT, "decision-chain", "evidence", "m5")

# 与 B 组逐字相同的模型绑定。参数不同就不是同条件对照。
MODEL = {"mode": "chat", "name": "deepseek-v4-flash",
         "provider": "langgenius/deepseek/deepseek",
         "completion_params": {"top_p": 0.8, "thinking": True,
                               "max_tokens": 32000, "reasoning_effort": "low"}}

FEAT = {"file_upload": {"enabled": False, "allowed_file_types": ["image"],
                        "allowed_file_extensions": [".JPG"],
                        "allowed_file_upload_methods": ["local_file"],
                        "image": {"enabled": False, "number_limits": 3,
                                  "transfer_methods": ["local_file"]}, "number_limits": 3},
        "opening_statement": "", "retriever_resource": {"enabled": False},
        "sensitive_word_avoidance": {"enabled": False}, "speech_to_text": {"enabled": False},
        "suggested_questions": [], "suggested_questions_after_answer": {"enabled": False},
        "text_to_speech": {"enabled": False, "language": "", "voice": ""}}

# ---------------------------------------------------------------- A 组：好 Prompt
# 认真写的版本：给角色、给约束、给不许做什么、给输出结构、明确要求不编造。
# 这就是一个懂行的运营在没有本系统时会写出来的东西。

GOOD_PROMPT_M3 = """你是一位资深的品牌内容运营负责人，正在为一个真实品牌做本周期的运营判断。

你会拿到三样东西：账号的当前状态、用户这一轮的原话、以及可以引用的参考资料。

请给出这一轮的运营判断。要求：

1. **先给结论**：这一轮该怎么走，用一句话说清楚。
2. **说清依据**：你的判断建立在哪些已登记的事实上。参考资料里没有的事实，
   一律不要写进去——不要凭常识补一个行业惯例、一个季节结论或一条平台规则。
   缺什么就说缺什么，说明因此哪些结论不下。
3. **给出这一轮的内容任务**：受众卡在什么真实问题上、希望他们发生什么变化、
   这条内容可以承诺什么、由谁表达、表达的边界在哪、明确不承诺什么。
4. **说清取舍与代价**：这一轮为了做这件事放弃了什么，放弃的代价是什么。
5. **说清怎么算成功、看到什么就停**：给可观察的信号，不要给「提升影响力」
   这种无法证伪的话。
6. **产能要对得上**：不要排出班底做不完的量。
7. **不要越权**：没有确认承接路径就不要设计预约、到店、私信、购买类引导。
8. **不要写内部字段名、规则编号、文件路径**。用人话写给品牌方看。

写成 Founder 能直接读懂的中文，不要用术语堆砌。"""

GOOD_PROMPT_FINAL = """你是一位资深的短视频内容策划与发布包装负责人，正在为一个真实品牌
把这一轮的内容做成可以直接发布的成品包。

你会拿到：这一轮的运营判断与内容任务、以及可以引用的已登记事实资料。

请给出完整的发布成品包。要求：

1. **标题**：给一个推荐标题，可以给少量备选，但要说清什么场景用哪个。
2. **封面与首帧**：画面写什么、文字写什么，两者分工是什么。
3. **发布文案全文**：开头几行要能独立成立。
4. **口播或分镜要点**：给可执行的节拍，不要只给方向。
5. **评论区运营**：置顶发什么、可能被问什么、怎么答。
6. **发布前自检**：给可执行的检查项，不要给「确保质量」这种废话。

硬约束，违反任何一条这条内容就不能发：

- **不编造**。资料里没有的商品性能、价格、库存、优惠、顾客案例、经营结果，
  一个字都不许写。资料里说了不得推断的，就不要推断。
- **不越权承诺**。没有确认的承接路径（预约入口、接待人、服务时效、每日容量）
  不许出现在内容里，也不许暗示。
- **不制造焦虑**。不做身材、年龄、身份焦虑，不用无依据的绝对化话术。
- **判断权交回观众**。不要替观众下「这件适合你」或「这件你不适合」的结论。
- **平台未锁定时**，不要预先写死平台专属的规格数字。

写成品牌方可以直接拿去执行的中文。"""


def ensure_app(c, name, prompt, var_labels):
    st, apps = c.call("GET", "/console/api/apps?page=1&limit=100")
    hit = [a for a in apps["data"] if a.get("name") == name]
    if hit:
        return hit[0]["id"]
    st, app = c.call("POST", "/console/api/apps", body={
        "name": name, "mode": "workflow", "icon_type": "emoji", "icon": "🅰️",
        "icon_background": "#E6F4FF",
        "description": "M5 A/B 对照的 A 组基线：同模型、同输入、同事实、同参数下的冻结好 Prompt"})
    app_id = app["id"]
    def n(i, pos, data):
        return {"id": i, "type": "custom", "position": pos, "width": 244, "height": 120,
                "selected": False, "data": data}
    def e(a, b, at, bt):
        return {"id": "%s-%s" % (a, b), "type": "custom", "source": a, "target": b,
                "sourceHandle": "source", "targetHandle": "target", "zIndex": 0,
                "data": {"sourceType": at, "targetType": bt, "isInIteration": False}}
    graph = {"nodes": [
        n("a_start", {"x": 80, "y": 160}, {"type": "start", "title": "输入", "variables": [
            {"variable": v, "label": l, "type": "paragraph", "required": False,
             "max_length": 60000, "options": []} for v, l in var_labels]}),
        n("a_llm", {"x": 400, "y": 160}, {
            "type": "llm", "title": "A 组｜冻结好 Prompt", "model": MODEL,
            "vision": {"enabled": False}, "context": {"enabled": False, "variable_selector": []},
            "prompt_template": [
                {"role": "system", "text": prompt, "id": "s1"},
                {"role": "user", "id": "u1", "text": "\n\n".join(
                    "===== %s =====\n{{#a_start.%s#}}" % (l, v) for v, l in var_labels)}]}),
        n("a_end", {"x": 720, "y": 160}, {"type": "end", "title": "结束", "outputs": [
            {"variable": "text", "value_selector": ["a_llm", "text"]}]})],
        "edges": [e("a_start", "a_llm", "start", "llm"), e("a_llm", "a_end", "llm", "end")],
        "viewport": {"x": 0, "y": 0, "zoom": 0.8}}
    st, cur = c.call("GET", "/console/api/apps/%s/workflows/draft" % app_id)
    c.call("POST", "/console/api/apps/%s/workflows/draft" % app_id,
           body={"graph": graph, "features": FEAT,
                 "hash": cur.get("hash") if st == 200 else None,
                 "environment_variables": [], "conversation_variables": []}, timeout=300)
    c.call("POST", "/console/api/apps/%s/workflows/publish" % app_id,
           body={"marked_name": "ab-baseline-a"}, timeout=300)
    return app_id


def _sha(s):
    return hashlib.sha256((s or "").encode("utf-8")).hexdigest()


def main():
    rt = RT.Runtime()
    c = rt.console
    facts = FS.registered_facts()
    refs = FS.m3_loaded_references(facts)
    boot = FS.bootstrap("ab" + (sys.argv[1] if len(sys.argv) > 1 else "a"))
    acct_text, _ = FS.projection_text(boot)
    nl = ("我们序里集这一轮想弄清楚一件事：顾客到底能不能自己判断哪件衣服适合自己。"
          "这周先出一条内容试试水，看这个方向立不立得住。")

    app_m3 = ensure_app(c, "DIYU M5 AB · A 组基线（运营判断）", GOOD_PROMPT_M3,
                        [("account_context", "账号当前状态"), ("user_request", "用户本轮原话"),
                         ("loaded_references", "可引用的参考资料")])
    app_fin = ensure_app(c, "DIYU M5 AB · A 组基线（最终成品）", GOOD_PROMPT_FINAL,
                         [("operating_judgment", "这一轮的运营判断与内容任务"),
                          ("registered_facts", "已登记事实资料")])

    cases = []

    # ---------------- AB-M3-01 ----------------
    print(">>> AB-M3-01 A 组", flush=True)
    ra = RT._run_with_retry(rt.key(app_m3),
                            {"account_context": acct_text, "user_request": nl,
                             "loaded_references": refs}, "m5-ab", "ab-a-m3")
    a_text = (ra["outputs"] or {}).get("text") or ""
    print(">>> AB-M3-01 B 组", flush=True)
    rb = rt.m3_operate(account_context=acct_text, user_request=nl, loaded_references=refs)
    b_text = (rb["outputs"] or {}).get("operating_judgment") or ""
    cases.append({"case": "AB-M3-01", "name": "好 Prompt A 对 M3 专业能力 B",
                  "same_input": True,
                  "shared_inputs": {"account_context": acct_text, "user_request": nl,
                                    "loaded_references_sha256": _sha(refs),
                                    "loaded_references_chars": len(refs)},
                  "A": {"kind": "frozen_good_prompt_baseline", "app_id": app_m3,
                        "run_id": ra["run_id"], "text": a_text, "sha256": _sha(a_text)},
                  "B": {"kind": "m3_capability", "app_id": RT.M3_APP,
                        "run_id": rb["run_id"], "text": b_text, "sha256": _sha(b_text),
                        "gate_status": (rb["outputs"] or {}).get("gate_status")}})

    # ---------------- AB-FINAL-01 ----------------
    # B 组用 M5 链路的最终成品；A 组拿**同一份运营判断**去做成品，条件对齐。
    print(">>> AB-FINAL-01 B 组（走链路）", flush=True)
    upstream, up_cap, chain = "", "", []
    for cap in ("CONTENT_BRIEF", "CREATIVE_SCRIPT", "PUBLISHING_PACKAGING"):
        h = rt.hop(cap, m3_judgment=b_text, upstream_delivery=upstream,
                   upstream_capability=up_cap, registered_facts=facts,
                   account_context=acct_text, user_request=nl)
        ho = h["outputs"] or {}
        r = rt.seam(cap, capability_call=ho.get("capability_call") or "",
                    professional_input=ho.get("professional_input") or "")
        chain.append({"capability": cap, "gaps": ho.get("extraction_gaps_text"),
                      "outcome": r["business_delivery_outcome"], "run_id": r["run_id"],
                      "artifact_chars": len(r.get("artifact") or "")})
        if RT.delivered(r) and (r.get("artifact") or "").strip():
            upstream, up_cap = r["artifact"], cap
    b_final = upstream
    print(">>> AB-FINAL-01 A 组", flush=True)
    ra2 = RT._run_with_retry(rt.key(app_fin),
                             {"operating_judgment": b_text, "registered_facts": facts},
                             "m5-ab", "ab-a-final")
    a_final = (ra2["outputs"] or {}).get("text") or ""
    cases.append({"case": "AB-FINAL-01", "name": "好 Prompt A 对适用专业 Skill 子集 B 的最终成品",
                  "same_input": True,
                  "shared_inputs": {"operating_judgment_sha256": _sha(b_text),
                                    "registered_facts_sha256": _sha(facts)},
                  "A": {"kind": "frozen_good_prompt_baseline", "app_id": app_fin,
                        "run_id": ra2["run_id"], "text": a_final, "sha256": _sha(a_final)},
                  "B": {"kind": "applicable_skill_subset_chain", "chain": chain,
                        "text": b_final, "sha256": _sha(b_final)}})

    # ---------------- 盲评包与封存映射 ----------------
    # 甲/乙 的分配用输入哈希决定，确定性、可复算，但不看正文——
    # 既不是随机（不可复现），也不是固定（会被猜出规律）。
    blind, mapping = [], {}
    for cs in cases:
        h = int(_sha(cs["shared_inputs"].get("loaded_references_sha256",
                                             cs["shared_inputs"].get("operating_judgment_sha256", "")))[:8], 16)
        a_first = (h % 2 == 0)
        jia, yi = ("A", "B") if a_first else ("B", "A")
        mapping[cs["case"]] = {"甲": jia, "乙": yi}
        blind.append({"case": cs["case"], "name": cs["name"],
                      "甲": cs[jia]["text"], "乙": cs[yi]["text"]})

    with open(os.path.join(EV, "AB_SUITE_RAW_%s.json" % boot["tag"]), "w", encoding="utf-8") as f:
        json.dump({"boot": boot, "cases": cases}, f, ensure_ascii=False, indent=2)
    seal = os.path.join(EV, "AB_MAPPING_SEALED_%s.json" % boot["tag"])
    with open(seal, "w", encoding="utf-8") as f:
        json.dump({"warning": "评分完成之前不要打开。打开即作废本次盲评。",
                   "mapping": mapping}, f, ensure_ascii=False, indent=2)
    with open(os.path.join(EV, "AB_BLIND_%s.json" % boot["tag"]), "w", encoding="utf-8") as f:
        json.dump({"blind": blind}, f, ensure_ascii=False, indent=2)
    print("\n映射已封存：%s（评分完成前不要打开）" % os.path.basename(seal))
    for cs in cases:
        print("  %-14s A=%d字 B=%d字" % (cs["case"], len(cs["A"]["text"]), len(cs["B"]["text"])))
    print("SAVED", EV)


if __name__ == "__main__":
    main()
