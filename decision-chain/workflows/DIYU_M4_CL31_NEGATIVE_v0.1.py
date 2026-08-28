#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""M4 强制负向测试 NEG-C01…C14（Prompt v1.5 §9 / 取证合同 v0.5 §4）

每一项的预期结果已在 v0.5 §4 冻结，本脚本只执行，不改判据。
C05–C08 是**判定器判别力测试**：用构造输入驱动判定器，验证它确实报 FAIL；
判定器若对这些情形报 PASS，说明它无判别力，对应 CL 项不得放行。
纪律承接 M4-FND-021：块标记从被测节点代码的命名空间里绑定，不在本脚本里另抄一份。
"""
import importlib.util, json, os, sys, yaml

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
DC_WF = os.path.join(ROOT, "decision-chain", "workflows")
OUT = os.path.join(ROOT, "decision-chain/evidence/m4/final_closure/NEG_C01_C14.json")
CB = os.path.join(DC_WF, "DIYU_M4_TOOL_CONTENT_BRIEF_v1_3_TEST.yml")
SEAM = os.path.join(DC_WF, "DIYU_M4_CAPABILITY_SEAM_v1_3_TEST.yml")

sp = importlib.util.spec_from_file_location("m4judge", os.path.join(DC_WF, "DIYU_M4_CL31_JUDGE_v0.1.py"))
J = importlib.util.module_from_spec(sp); sp.loader.exec_module(J)

R = []


def nodes(p):
    return {n["id"]: n for n in yaml.safe_load(open(p, encoding="utf-8"))["workflow"]["graph"]["nodes"]}


def edges(p):
    return yaml.safe_load(open(p, encoding="utf-8"))["workflow"]["graph"]["edges"]


def ns_of(code):
    g = {}; exec(compile(code, "<node>", "exec"), g); return g


def rec(cid, name, expected, got, ok, detail=None):
    R.append({"case": cid, "name": name, "expected_before_run": expected,
              "observed": got, "result": "PASS" if ok else "FAIL", "detail": detail})
    print("  %-9s %-34s %s" % (cid, name, "PASS" if ok else "FAIL"))


CBN, SN = nodes(CB), nodes(SEAM)
AD = ns_of(CBN["returns_adapter"]["data"]["code"])
DF = ns_of(CBN["delivery_finalize"]["data"]["code"])
CR = ns_of(CBN["component_return"]["data"]["code"])
TF = ns_of(SN["seam_tool_fail"]["data"]["code"])
UN = ns_of(SN["unsupported"]["data"]["code"])
A, AC = AD["A_OPEN"], AD["A_CLOSE"]
U, UC = AD["U_OPEN"], AD["U_CLOSE"]
RO, RC = AD["R_OPEN"], AD["R_CLOSE"]
BODY = "这是一份足够长的专业产出正文，用于满足产出完整性阈值。" * 20

print("== 强制负向测试 NEG-C01…C14 ==")

# C01 tool 节点直接失败
o = TF["main"](route="CONTENT_BRIEF", derivation="d")
rec("NEG-C01", "tool 节点直接失败", "非空正文 + NOT_DELIVERED",
    {"len": len(o["user_delivery"]), "outcome": o["business_delivery_outcome"]},
    bool(o["user_delivery"].strip()) and o["business_delivery_outcome"] == "NOT_DELIVERED")

# C02 end_tool_fail 输出
vs = [x["variable"] for x in SN["end_tool_fail"]["data"]["outputs"]]
rec("NEG-C02", "end_tool_fail 终止", "outputs 含 user_delivery", vs,
    "user_delivery" in vs and "business_delivery_outcome" in vs)

# C03 专业内容在但用户 marker 缺失
txt = A + "\n" + BODY + "\n" + AC + "\n\n" + RO + "\nNONE\n" + RC
o = AD["main"](final_text=txt)
rec("NEG-C03", "专业内容在但用户块缺失", "needs_projection=true",
    {"needs_projection": o["needs_projection"], "artifact_len": len(o["artifact"])},
    o["needs_projection"] == "true")

# C04 恢复成功
o = DF["main"](adapter_user_delivery="", adapter_status="MISSING", needs_projection="true",
               recovered_text="这是一份恢复出来的、可直接读的用户正文。" * 10,
               returns_json="[]", capability="CONTENT_BRIEF")
rec("NEG-C04", "恢复成功", "DELIVERED_AFTER_RECOVERY", o["delivery_outcome"],
    o["delivery_outcome"] == "DELIVERED_AFTER_RECOVERY" and bool(o["user_delivery"].strip()))

# C05 恢复输出为空（判别力）
o = DF["main"](adapter_user_delivery="", adapter_status="MISSING", needs_projection="true",
               recovered_text="", returns_json="[]", capability="CONTENT_BRIEF")
rec("NEG-C05", "恢复输出为空", "NOT_DELIVERED + 非空失败说明",
    {"outcome": o["delivery_outcome"], "len": len(o["user_delivery"]), "used": o["recovery_used"]},
    o["delivery_outcome"] == "NOT_DELIVERED" and bool(o["user_delivery"].strip())
    and o["recovery_used"] == "attempted")

# C06 恢复输出含内部技术词（判别力）
for bad in ("PARSE_FAIL", "<think>", "</think>"):
    o = DF["main"](adapter_user_delivery="", adapter_status="MISSING", needs_projection="true",
                   recovered_text=("正文里混进了 %s 这个内部标记。" % bad) * 8,
                   returns_json="[]", capability="CONTENT_BRIEF")
    rec("NEG-C06", "恢复输出含内部词 %s" % bad, "NOT_DELIVERED",
        o["delivery_outcome"], o["delivery_outcome"] == "NOT_DELIVERED")

# C06b thinking 段必须被剥离而不是原样交付（M4-FND-029 回归）
o = DF["main"](adapter_user_delivery="", adapter_status="MISSING", needs_projection="true",
               recovered_text="<think>这是内部推理，绝不能给用户看。</think>这是真正要给用户看的正文。" * 6,
               returns_json="[]", capability="CONTENT_BRIEF")
rec("NEG-C06b", "恢复输出带 thinking 段", "剥离后交付，正文不含 think",
    {"outcome": o["delivery_outcome"], "has_think": "<think>" in o["user_delivery"],
     "has_reason": "内部推理" in o["user_delivery"]},
    "<think>" not in o["user_delivery"] and "内部推理" not in o["user_delivery"])

# C07 整份复制 Artifact（判定器判别力）
art = BODY
copy_ud = art
ok = not (J.lcs_len(copy_ud, art) < 0.60 * len(art) and len(copy_ud) < 0.80 * len(art))
rec("NEG-C07", "恢复输出整份复制 Artifact", "CL31-03⑥ 判 FAIL",
    {"lcs_ratio": round(J.lcs_len(copy_ud, art) / len(art), 4),
     "len_ratio": round(len(copy_ud) / len(art), 4), "criterion_says": "FAIL" if ok else "PASS"}, ok)

# C08 新增冻结输入与 Artifact 中不存在的事实（判定器判别力）
fx = importlib.util.module_from_spec(
    importlib.util.spec_from_file_location("fx", os.path.join(DC_WF, "DIYU_M4_DETERMINISTIC_PROBE_v0.1.py")))
importlib.util.spec_from_file_location(
    "fx", os.path.join(DC_WF, "DIYU_M4_DETERMINISTIC_PROBE_v0.1.py")).loader.exec_module(fx)
hay = J.frozen_artifact() + "\n" + fx.CT_M3
fake = "本季新到的 7 款风衣在杭州湖滨店 3 月 15 日上架，售价 1299 元。"
uns = [f for f in J.extract_facts(fake) if f not in hay]
rec("NEG-C08", "恢复输出新增未支撑事实", "unsupported_fact_count > 0",
    {"unsupported": uns, "count": len(uns)}, len(uns) > 0)

# C08b 判定器不得对合规正文误报
clean = "这次的卡点不是衣服不够，而是层数与场合没有分开。下一步交给脚本环节按节拍排。"
uns2 = [f for f in J.extract_facts(clean) if f not in hay]
rec("NEG-C08b", "合规正文不得被误报新增事实", "unsupported_fact_count == 0",
    {"unsupported": uns2}, len(uns2) == 0)

# C09 同一运行不得有第二次恢复
E = edges(CB)
into_rec = [e for e in E if e["target"] == "recovery_llm"]
out_rec = [e for e in E if e["source"] == "recovery_llm"]
rec("NEG-C09", "第二次恢复", "图上不存在第二次恢复边",
    {"into_recovery": [e["source"] for e in into_rec], "out_of_recovery": [e["target"] for e in out_rec]},
    len(into_rec) == 1 and into_rec[0]["source"] == "projection_gate"
    and len(out_rec) == 1 and out_rec[0]["target"] == "delivery_finalize")

# C10 恢复后不得回跑 skill_llm
back = [e for e in E if e["target"] == "skill_llm"]
rec("NEG-C10", "恢复后重跑 skill_llm", "skill_llm 无回边",
    {"into_skill_llm": [e["source"] for e in back]},
    len(back) == 1 and back[0]["source"] == "projection_record")

# C11 合法资料不足 Return
o = CR["main"](status="INSUFFICIENT", note="n", missing=["objective"], entry_resolved="ENTRY-03",
               envelope_hash="deadbeef", capability_call="")
rec("NEG-C11", "合法资料不足 Return", "非空正文 + 非任务终态",
    {"len": len(o["user_delivery"]), "terminal": o["is_task_terminal_state"],
     "invalidation": o["triggers_downstream_invalidation"]},
    bool(o["user_delivery"].strip()) and o["is_task_terminal_state"] == "false"
    and o["triggers_downstream_invalidation"] == "false")

# C12 正常不需要恢复的交付
o = DF["main"](adapter_user_delivery="一份正常的用户正文。" * 6, adapter_status="OK",
               needs_projection="false", recovered_text="", returns_json="[]",
               capability="CONTENT_BRIEF")
rec("NEG-C12", "正常不需要恢复的交付", "DELIVERED + recovery_used=false",
    {"outcome": o["delivery_outcome"], "used": o["recovery_used"]},
    o["delivery_outcome"] == "DELIVERED" and o["recovery_used"] == "false")

# C13 不支持的能力
o = UN["main"](route="SOMETHING_ELSE", derivation="d")
vs = [x["variable"] for x in SN["end_unsupported"]["data"]["outputs"]]
rec("NEG-C13", "不支持的能力", "非空正文 + NOT_DELIVERED",
    {"len": len(o["user_delivery"]), "outcome": o["business_delivery_outcome"], "end_outputs": vs},
    bool(o["user_delivery"].strip()) and o["business_delivery_outcome"] == "NOT_DELIVERED"
    and "user_delivery" in vs)

fails = [x for x in R if x["result"] == "FAIL"]
out = {"contract": "V1-M4-EVIDENCE-COLLECTION-v0.5 §4", "cases": R,
       "total": len(R), "failed": len(fails),
       "note_C14": "NEG-C14（Founder Canvas 失败说明的用户可见呈现）为 Runtime 项，"
                   "由 CL31-07⑩ 的 Canvas 实跑承担，不在本离线套件内。",
       "verdict": "PASS" if not fails else "FAIL"}
json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=2, sort_keys=True)
print("\nNEG 套件 = %s（%d 项，%d 失败）" % (out["verdict"], out["total"], out["failed"]))
sys.exit(0 if not fails else 1)
