#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""M4-CL31-02/03 隔离故障注入对象构建（Prompt v1.5 §5.3）

只建两个 evaluation-only 对象，名称明确含 "M4 AC31 FAULT INJECTION EVAL ONLY"：
  EVAL-1  CONTENT_BRIEF 子应用副本，**唯一差异是 final_extract 节点本身**
          （节点 id 与输出键 output 不变，因此 returns_adapter / projection_gate /
            recovery_llm / delivery_finalize / binding_record / end_ok 逐字节不变）
  EVAL-2  Capability Seam 副本，**唯一差异是 tool_content_brief 的 provider 指向 EVAL-1**

冻结注入 artifact 正文直接从取证合同 v0.5 §2.3 抽取，保证与冻结判据逐字节同源。
"""
import hashlib, json, os, re, sys, yaml

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
CONTRACT = os.path.join(ROOT, "decision-chain/docs/V1_M4_EVIDENCE_COLLECTION_CONTRACT_v0.5.md")
CB = os.path.join(HERE, "DIYU_M4_TOOL_CONTENT_BRIEF_v1_3_TEST.yml")
SEAM = os.path.join(HERE, "DIYU_M4_CAPABILITY_SEAM_v1_3_TEST.yml")
EVAL1 = os.path.join(HERE, "DIYU_M4_AC31_INJECT_CHILD_EVAL_ONLY.yml")
EVAL2 = os.path.join(HERE, "DIYU_M4_AC31_INJECT_SEAM_EVAL_ONLY.yml")

NAME1 = "DIYU M4 AC31 FAULT INJECTION EVAL ONLY · Content Brief child"
NAME2 = "DIYU M4 AC31 FAULT INJECTION EVAL ONLY · Capability Seam"

RECOVERY_SUBGRAPH = ["returns_adapter", "projection_gate", "recovery_llm",
                     "delivery_finalize", "binding_record", "end_ok"]


def frozen_artifact():
    """从 v0.5 §2.3 的 ```text 围栏中逐字节抽取冻结专业产出。"""
    md = open(CONTRACT, encoding="utf-8").read()
    i = md.index("### §2.3 冻结专业产出")
    j = md.index("```text", i) + len("```text\n")
    k = md.index("```", j)
    return md[j:k].rstrip("\n")


INJECTOR_TMPL = '''
# ============================================================================
# 故障注入源（EVALUATION ONLY，绝不进入正式 M4 应用）
# 取代正式 final_extract；节点 id 与输出键 output 保持不变，
# 因此下游恢复子图（returns_adapter … end_ok）逐字节不变。
# 注入指令由 capability_call 中的哨兵串给出，运行前已在取证合同 v0.5 §2.2 冻结。
# ============================================================================

A_OPEN, A_CLOSE = "---M4_ARTIFACT---", "---END_M4_ARTIFACT---"
U_OPEN, U_CLOSE = "---M4_USER_DELIVERY---", "---END_M4_USER_DELIVERY---"
R_OPEN, R_CLOSE = "---M4_RETURNS---", "---END_M4_RETURNS---"

FROZEN_ARTIFACT = """%(FROZEN)s"""


def _strip_thinking(llm_text):
    """与正式 final_extract 模板逐条等价的 thinking 剥离。"""
    raw = llm_text or ""
    if "</think>" in raw:
        tail = raw.split("</think>")[-1]
        return "MODEL_OUTPUT_NO_FINAL" if tail.strip() == "" else tail
    if raw.strip() == "":
        return "MODEL_OUTPUT_NO_FINAL"
    return raw


def _drop_user_block(text):
    """只删用户交付块（标记连同其内容），artifact 与 returns 块原样保留。"""
    i = text.find(U_OPEN)
    if i < 0:
        return text
    j = text.find(U_CLOSE, i)
    if j < 0:
        return text[:i]
    return text[:i] + text[j + len(U_CLOSE):]


def main(llm_text, capability_call):
    cc = capability_call or ""
    out = _strip_thinking(llm_text)

    if "M4_FAULT_DIRECTIVE=TOOL_FAIL" in cc:
        raise RuntimeError("M4 AC31 FAULT INJECTION: forced capability app failure")

    if "M4_FAULT_DIRECTIVE=FROZEN_MARKERLESS" in cc:
        return {"output": (A_OPEN + "\\n" + FROZEN_ARTIFACT + "\\n" + A_CLOSE
                           + "\\n\\n" + R_OPEN + "\\nNONE\\n" + R_CLOSE)}

    if "M4_FAULT_DIRECTIVE=LIVE_MARKERLESS" in cc:
        return {"output": _drop_user_block(out)}

    return {"output": out}
'''


def sha(o):
    return hashlib.sha256(json.dumps(o, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


def dump(path, obj):
    with open(path, "w", encoding="utf-8") as fh:
        yaml.safe_dump(obj, fh, allow_unicode=True, sort_keys=True, width=100000,
                       default_flow_style=False)


def build_eval1():
    d = yaml.safe_load(open(CB, encoding="utf-8"))
    d["app"]["name"] = NAME1
    d["app"]["description"] = ("EVALUATION ONLY · 故障注入对象。不得接入 Founder Canvas、"
                               "主路由、生产入口或任何真实业务调用。取证完成后删除或隔离。")
    nodes = d["workflow"]["graph"]["nodes"]
    hit = 0
    for n in nodes:
        if n["id"] != "final_extract":
            continue
        hit += 1
        n["data"] = {
            "code": INJECTOR_TMPL % {"FROZEN": frozen_artifact()},
            "code_language": "python3",
            "desc": "EVALUATION ONLY 故障注入源；取代正式 Final Extract。",
            "outputs": {"output": {"children": None, "type": "string"}},
            "selected": False, "title": "Final Extract（故障注入）", "type": "code",
            "variables": [
                {"value_selector": ["skill_llm", "text"], "variable": "llm_text"},
                {"value_selector": ["1788000000001", "capability_call"],
                 "variable": "capability_call"},
            ],
        }
    if hit != 1:
        raise SystemExit("final_extract 命中 %d 次，中止" % hit)
    dump(EVAL1, d)
    return d


def build_eval2(child_provider_id):
    d = yaml.safe_load(open(SEAM, encoding="utf-8"))
    d["app"]["name"] = NAME2
    d["app"]["description"] = ("EVALUATION ONLY · 故障注入对象。CONTENT_BRIEF 分支指向注入子应用；"
                               "不得接入 Founder Canvas、主路由或生产入口。取证完成后删除或隔离。")
    hit = 0
    for n in d["workflow"]["graph"]["nodes"]:
        if n["id"] != "tool_content_brief":
            continue
        hit += 1
        n["data"]["provider_id"] = child_provider_id
        n["data"]["provider_name"] = child_provider_id
        n["data"]["tool_name"] = "diyu_m4_ac31_inject_child"
        n["data"]["tool_label"] = "diyu_m4_ac31_inject_child"
        n["data"]["title"] = "调用 " + NAME1
    if hit != 1:
        raise SystemExit("tool_content_brief 命中 %d 次，中止" % hit)
    dump(EVAL2, d)
    return d


def equivalence_report(e1, e2):
    """§5.3-4：恢复子图必须与最终候选逐字节等价；差异只允许出现在注入源。"""
    off = {n["id"]: n["data"] for n in yaml.safe_load(open(CB, encoding="utf-8"))["workflow"]["graph"]["nodes"]}
    inj = {n["id"]: n["data"] for n in e1["workflow"]["graph"]["nodes"]}
    diff = sorted([k for k in inj if k in off and sha(inj[k]) != sha(off[k])])
    added, removed = sorted(set(inj) - set(off)), sorted(set(off) - set(inj))
    sub_ok = all(sha(inj[k]) == sha(off[k]) for k in RECOVERY_SUBGRAPH)

    offs = {n["id"]: n["data"] for n in yaml.safe_load(open(SEAM, encoding="utf-8"))["workflow"]["graph"]["nodes"]}
    injs = {n["id"]: n["data"] for n in e2["workflow"]["graph"]["nodes"]}
    sdiff = sorted([k for k in injs if k in offs and sha(injs[k]) != sha(offs[k])])
    fail_ok = all(sha(injs[k]) == sha(offs[k]) for k in
                  ("seam_tool_fail", "end_tool_fail", "unsupported", "end_unsupported"))
    return {
        "child_changed_nodes": diff, "child_added": added, "child_removed": removed,
        "child_only_injection_source_differs": diff == ["final_extract"] and not added and not removed,
        "recovery_subgraph_bytewise_identical": sub_ok,
        "recovery_subgraph_nodes": RECOVERY_SUBGRAPH,
        "recovery_subgraph_sha256": {k: sha(inj[k]) for k in RECOVERY_SUBGRAPH},
        "final_candidate_recovery_subgraph_sha256": {k: sha(off[k]) for k in RECOVERY_SUBGRAPH},
        "seam_changed_nodes": sdiff,
        "seam_only_injection_wiring_differs": sdiff == ["tool_content_brief"],
        "seam_failure_path_bytewise_identical": fail_ok,
    }


if __name__ == "__main__":
    pid = sys.argv[1] if len(sys.argv) > 1 else "PENDING_PUBLISH"
    e1 = build_eval1()
    e2 = build_eval2(pid)
    rep = equivalence_report(e1, e2)
    print(json.dumps(rep, ensure_ascii=False, indent=2))
    out = os.path.join(ROOT, "decision-chain/evidence/m4/final_closure/INJECTION_EQUIVALENCE.json")
    json.dump(rep, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=2, sort_keys=True)
