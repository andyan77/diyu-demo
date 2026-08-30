#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""S4 事实充分性链 · 只读诊断器 v1.0

只读归档证据，**零模型调用、零 Dify 写入、零被测图修改**。
不判定验收，只重算「六个必要字段在每一跳的在场与来源」，并定位第一失效节点。

判定规则先于结果冻结（写在本文件里，运行时不改）：

R1  确定性来源在场：`uapp_ctx.registered_facts` 非空 ⇒ 事实来源 PRESENT。
    它由代码节点从「上传资料原文 + 已登记用户原话」确定性拼装，非模型产出。
R2  外壳在场：hop 的 `extracted_json[field]` 非空 ⇒ 该字段在 capability_call 外壳中 PRESENT。
    `objective` 取 `primary_goal`。
R3  抹除判定（只对有 1:1 确定性来源绑定的字段成立）：
    R1 为 PRESENT 且 R2 为 ABSENT ⇒ `SOURCE_PRESENT_BUT_ERASED`。
    六字段中只有 `facts_registered` 具备这种绑定（来源 = registered_facts）。
R4  其余五字段的来源是 M3 判断正文与用户原话等自然语言，其「是否已明确写出」需要专业判断，
    确定性侧无法独立断言。因此外壳缺失时只记 `INCONCLUSIVE`，不记 ABSENT，也不记抹除。
R5  复合缺口按全角与半角分号切分（TD-UAPP-17 在本诊断器内修正；历史裁定结果一字不动）。
R6  空 artifact 覆盖：**按 conversation_id 分组后**，同一会话内，若第 i 轮 artifact 非空、第 j>i 轮 artifact 为空
    且两轮都执行了 uapp_save，则 `uapp_last_artifact` 被空值覆盖；再看第 j+1 轮
    hop 的 upstream_delivery 是否随之变空，作为独立确证。

用法：
    python3 S4_FACT_CHAIN_DIAGNOSE_v1.0.py --selfcheck            # 正负控制自检
    python3 S4_FACT_CHAIN_DIAGNOSE_v1.0.py --graph-dump <hop.json> --out <trace.json>
"""
import argparse
import glob
import hashlib
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
EVID = os.path.abspath(os.path.join(HERE, "..", "evidence", "stages"))

SIX = ["objective", "audience_problem", "expected_change", "content_promise",
       "facts_registered", "expression_subject_and_boundary"]

# 只有这一个字段在链路里有 1:1 的确定性来源绑定（R3/R4）
DETERMINISTIC_SOURCE = {"facts_registered": ("uapp_ctx", "registered_facts")}


def sha(s):
    if isinstance(s, str):
        s = s.encode("utf-8")
    return hashlib.sha256(s).hexdigest()


def split_gaps(text):
    """R5：复合缺口按全角/半角分号切分，去空白与空项。"""
    t = (text or "").strip()
    if not t or t == "无":
        return []
    return [p.strip() for p in re.split(r"[；;]", t) if p.strip()]


def nodes_of(doc):
    return {n["node_id"]: n for n in doc.get("node_detail", [])}


def jload(v):
    if isinstance(v, dict):
        return v
    try:
        return json.loads(v)
    except Exception:
        return {}


def field_value(extracted, field):
    """R2：外壳在场判定。objective 取 primary_goal。"""
    if field == "objective":
        return str(extracted.get("primary_goal") or "").strip()
    return str(extracted.get(field) or "").strip()


def analyse_turn(doc):
    """对一次 T 轮重算六字段来源矩阵与 hop 缺口。只读，不修改任何输入。"""
    N = nodes_of(doc)
    out = {
        "case_id": doc.get("case_id"),
        "turn_index": doc.get("turn_index"),
        "conversation_id": doc.get("conversation_id"),
        "graph_sha256_at_run": doc.get("graph_sha256_at_run"),
        "fixture_sha256": (doc.get("uploaded_fixture") or {}).get("sha256"),
        "query_sha256": sha(doc.get("query") or ""),
        "nodes_executed": [n["node_id"] for n in doc.get("nodes_executed", [])],
        "uapp_save_executed": "uapp_save" in N,
    }
    if "uapp_hop" not in N:
        out["status"] = "NO_HOP_IN_TURN"
        return out

    hi = jload(N["uapp_hop"]["inputs"])
    ho = jload(N["uapp_hop"]["outputs"])
    ci = jload(N["uapp_ctx"]["outputs"]) if "uapp_ctx" in N else {}
    so = jload(N["uapp_seam"]["outputs"]) if "uapp_seam" in N else {}

    extracted = jload(ho.get("extracted_json"))
    smap = jload(ho.get("source_map_json"))

    reg_ctx = str(ci.get("registered_facts") or "")
    reg_hop = str(hi.get("registered_facts") or "")

    out["deterministic_inputs"] = {
        "uapp_ctx.registered_facts": {"len": len(reg_ctx), "sha256": sha(reg_ctx)},
        "uapp_hop.IN.registered_facts": {"len": len(reg_hop), "sha256": sha(reg_hop)},
        "carried_intact_ctx_to_hop": reg_ctx == reg_hop if reg_ctx else None,
        "uapp_hop.IN.m3_judgment_len": len(str(hi.get("m3_judgment") or "")),
        "uapp_hop.IN.upstream_capability": hi.get("upstream_capability"),
        "uapp_hop.IN.upstream_delivery_len": len(str(hi.get("upstream_delivery") or "")),
        "uapp_hop.IN.user_request_len": len(str(hi.get("user_request") or "")),
    }
    out["hop_gaps"] = split_gaps(ho.get("extraction_gaps_text"))
    out["hop_gaps_count_reported"] = ho.get("extraction_gaps_count")
    out["seam_artifact_len"] = len(str(so.get("artifact") or ""))
    rj = jload(so.get("returns_json"))
    if isinstance(so.get("returns_json"), str):
        try:
            rj = json.loads(so["returns_json"])
        except Exception:
            rj = []
    out["seam_precise_gaps"] = []
    if isinstance(rj, list):
        for r in rj:
            out["seam_precise_gaps"].extend(split_gaps((r or {}).get("precise_gap")))

    prof = str(jload(N["uapp_seam"]["inputs"]).get("professional_input") or "") \
        if "uapp_seam" in N else ""
    out["professional_input_carries_fact_block"] = "## [FACT] 已登记事实夹具" in prof
    out["professional_input_len"] = len(prof)

    matrix = {}
    for f in SIX:
        val = field_value(extracted, f)
        in_envelope = bool(val)
        cell = {
            "presence": "PRESENT" if in_envelope else "INCONCLUSIVE",
            "source_node": "",
            "source_ref_or_hash": "",
            "authorization": "",
            "executor_authored": False,
        }
        if in_envelope:
            tag = smap.get("primary_goal" if f == "objective" else f, "")
            cell["source_node"] = "uapp_hop.m5_extract"
            cell["source_ref_or_hash"] = "%s|%s" % (tag or "UNDECLARED", sha(val)[:16])
            cell["authorization"] = ("已登记来源内抽取（%s）" % tag) if tag else "UNDECLARED"
        if f in DETERMINISTIC_SOURCE:
            node, key = DETERMINISTIC_SOURCE[f]
            src = reg_ctx if node == "uapp_ctx" else ""
            cell["deterministic_source_node"] = "%s.%s" % (node, key)
            cell["deterministic_source_len"] = len(src)
            cell["deterministic_source_sha256"] = sha(src)
            cell["deterministic_source_present"] = bool(src)
            if src and not in_envelope:
                cell["presence"] = "ABSENT"
                cell["erasure"] = "SOURCE_PRESENT_BUT_ERASED"
                cell["authorization"] = "确定性来源在场（uapp_ctx 代码节点拼装，非模型产出）"
                cell["source_ref_or_hash"] = sha(src)[:16]
            elif src and in_envelope:
                cell["erasure"] = "NONE"
        matrix[f] = cell
    out["six_field_matrix"] = matrix
    out["erased_fields"] = [f for f, c in matrix.items()
                            if c.get("erasure") == "SOURCE_PRESENT_BUT_ERASED"]
    return out


def analyse_chain(turns):
    """R6：空 artifact 覆盖检测。**按 conversation_id 分组**，跨会话不配对。"""
    ev = []
    for conv in sorted({t.get("conversation_id") for t in turns}):
        ev.extend(_chain_one_conv(
            sorted([t for t in turns if t.get("conversation_id") == conv],
                   key=lambda x: x.get("turn_index") or 0)))
    return ev


def _chain_one_conv(turns):
    ev = []
    last_good = None
    for t in turns:
        idx, alen = t.get("turn_index"), t.get("seam_artifact_len")
        if alen and t.get("uapp_save_executed"):
            last_good = {"turn_index": idx, "artifact_len": alen}
        elif last_good and alen == 0 and t.get("uapp_save_executed"):
            ev.append({"overwrote_turn": last_good["turn_index"],
                       "overwrote_artifact_len": last_good["artifact_len"],
                       "by_turn": idx, "written_value_len": 0})
            last_good = None
    for e in ev:
        nxt = [t for t in turns if t.get("turn_index") == (e["by_turn"] or 0) + 1]
        if nxt:
            e["next_turn_upstream_delivery_len"] = \
                nxt[0]["deterministic_inputs"]["uapp_hop.IN.upstream_delivery_len"]
            e["confirmed_by_next_turn"] = e["next_turn_upstream_delivery_len"] == 0
    return ev


# --------------------------------------------------------------------------- #
# 正负控制自检：诊断器必须能区分「在场」「缺失」「复合缺口」「空覆盖」
# --------------------------------------------------------------------------- #
def _synth(registered_facts, extracted, gaps_text, artifact_len,
           with_save=True, turn=1, conv="SYNTH", upstream_len=0):
    def node(nid, i, o):
        return {"node_id": nid, "type": "x", "status": "succeeded",
                "inputs": json.dumps(i, ensure_ascii=False),
                "outputs": json.dumps(o, ensure_ascii=False)}
    nd = [
        node("uapp_ctx", {}, {"registered_facts": registered_facts}),
        node("uapp_hop",
             {"registered_facts": registered_facts, "m3_judgment": "m3",
              "upstream_capability": "", "upstream_delivery": "x" * upstream_len,
              "user_request": "u"},
             {"extracted_json": json.dumps(extracted, ensure_ascii=False),
              "source_map_json": json.dumps({k: "FACT" for k in extracted}, ensure_ascii=False),
              "extraction_gaps_text": gaps_text, "extraction_gaps_count": 0}),
        node("uapp_seam", {"professional_input": "## [FACT] 已登记事实夹具\n" + registered_facts},
             {"artifact": "a" * artifact_len, "returns_json": json.dumps(
                 [{"precise_gap": gaps_text}], ensure_ascii=False)}),
    ]
    if with_save:
        nd.append(node("uapp_save", {}, {}))
    return {"case_id": "SYNTH-T%d" % turn, "turn_index": turn, "conversation_id": conv,
            "query": "q", "uploaded_fixture": {"sha256": "0" * 64},
            "nodes_executed": [{"node_id": n["node_id"]} for n in nd], "node_detail": nd}


FULL = {"primary_goal": "g", "audience_problem": "a", "expected_change": "e",
        "content_promise": "c", "facts_registered": "F",
        "expression_subject_and_boundary": "s"}


def selfcheck():
    res, ok = [], True

    def chk(name, cond, detail=""):
        nonlocal ok
        ok = ok and bool(cond)
        res.append({"control": name, "result": "PASS" if cond else "FAIL", "detail": detail})

    # C-POS 字段在场能识别
    p = analyse_turn(_synth("FACTS" * 100, FULL, "无", 5000))
    chk("POS_all_six_present",
        all(p["six_field_matrix"][f]["presence"] == "PRESENT" for f in SIX),
        json.dumps({f: p["six_field_matrix"][f]["presence"] for f in SIX}, ensure_ascii=False))
    chk("POS_no_erasure", p["erased_fields"] == [], str(p["erased_fields"]))

    # C-NEG1 确定性来源在场但外壳缺失 ⇒ 必须识别为抹除
    e = dict(FULL); e["facts_registered"] = ""
    n1 = analyse_turn(_synth("FACTS" * 100, e, "facts_registered", 0))
    chk("NEG_erasure_detected", n1["erased_fields"] == ["facts_registered"],
        str(n1["erased_fields"]))
    chk("NEG_erasure_presence_ABSENT",
        n1["six_field_matrix"]["facts_registered"]["presence"] == "ABSENT",
        n1["six_field_matrix"]["facts_registered"]["presence"])

    # C-NEG2 来源本身为空 ⇒ 不得误报抹除（防止诊断器把真缺失说成被抹）
    n2 = analyse_turn(_synth("", e, "facts_registered", 0))
    chk("NEG_no_false_erasure_when_source_empty", n2["erased_fields"] == [],
        str(n2["erased_fields"]))

    # C-NEG3 非确定性绑定字段缺失 ⇒ 只记 INCONCLUSIVE，不记抹除
    e3 = dict(FULL); e3["content_promise"] = ""
    n3 = analyse_turn(_synth("FACTS" * 100, e3, "content_promise", 0))
    chk("NEG_nondeterministic_field_is_INCONCLUSIVE",
        n3["six_field_matrix"]["content_promise"]["presence"] == "INCONCLUSIVE"
        and n3["erased_fields"] == [],
        n3["six_field_matrix"]["content_promise"]["presence"])

    # C-SPLIT 复合缺口切分（TD-UAPP-17）
    comp = "expected_change；content_promise；expression_subject;content_origin_mode"
    chk("SPLIT_composite_gap", split_gaps(comp) == [
        "expected_change", "content_promise", "expression_subject", "content_origin_mode"],
        str(split_gaps(comp)))
    chk("SPLIT_none_is_empty", split_gaps("无") == [] and split_gaps("") == [])

    # C-OVW 空 artifact 覆盖能被发现
    chain = [analyse_turn(_synth("F" * 10, FULL, "无", 5593, turn=2)),
             analyse_turn(_synth("F" * 10, FULL, "无", 0, turn=3)),
             analyse_turn(_synth("F" * 10, FULL, "无", 0, turn=4, upstream_len=0))]
    ov = analyse_chain(chain)
    chk("OVW_detected", len(ov) == 1 and ov[0]["overwrote_turn"] == 2 and ov[0]["by_turn"] == 3,
        json.dumps(ov, ensure_ascii=False))
    chk("OVW_confirmed_by_next_turn", bool(ov) and ov[0].get("confirmed_by_next_turn") is True)

    # C-OVW-CONV 跨会话不得配对（分组正确性）
    cross = [analyse_turn(_synth("F" * 10, FULL, "无", 5593, turn=2, conv="CONV_A")),
             analyse_turn(_synth("F" * 10, FULL, "无", 0, turn=3, conv="CONV_B"))]
    chk("OVW_no_cross_conversation_pairing", analyse_chain(cross) == [],
        str(analyse_chain(cross)))

    # C-OVW-NEG 没有空轮时不得误报
    chain2 = [analyse_turn(_synth("F" * 10, FULL, "无", 5593, turn=2)),
              analyse_turn(_synth("F" * 10, FULL, "无", 3000, turn=3))]
    chk("OVW_no_false_positive", analyse_chain(chain2) == [], str(analyse_chain(chain2)))

    print(json.dumps({"selfcheck": "PASS" if ok else "FAIL", "controls": res},
                     ensure_ascii=False, indent=1))
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selfcheck", action="store_true")
    ap.add_argument("--graph-dump", default="")
    ap.add_argument("--out", default="")
    a = ap.parse_args()
    if a.selfcheck:
        return selfcheck()

    turns_cont, chain_a04 = [], []
    for p in sorted(glob.glob(os.path.join(EVID, "s4_continuation01", "S4-CO-T*.json"))):
        turns_cont.append(analyse_turn(json.load(io.open(p, encoding="utf-8"))))
    for p in sorted(glob.glob(os.path.join(EVID, "S4-CAP-*-POS.json"))):
        d = json.load(io.open(p, encoding="utf-8"))
        if d.get("attempt") == "attempt03_chain":
            r = analyse_turn(d)
            r["evidence_file"] = os.path.relpath(p, EVID)
            chain_a04.append(r)
    turns_cont.sort(key=lambda x: x.get("turn_index") or 0)
    chain_a04.sort(key=lambda x: x.get("turn_index") or 0)

    graph = {}
    if a.graph_dump and os.path.exists(a.graph_dump):
        g = json.load(io.open(a.graph_dump, encoding="utf-8"))
        n = {x["id"]: x for x in g["nodes"]}
        graph = {
            "hop_app_graph_sha256": sha(json.dumps(g, ensure_ascii=False, sort_keys=True)),
            "m5_compose_code_sha256": sha(n["m5_compose"]["data"]["code"]),
            "m5_extract_prompt_sha256": sha(json.dumps(
                n["m5_extract"]["data"]["prompt_template"], ensure_ascii=False, sort_keys=True)),
            "m5_extract_model": n["m5_extract"]["data"]["model"],
        }

    trace = {
        "document": {
            "id": "FACT_SUFFICIENCY_TRACE",
            "task_id": "DIYU-V1-UNIFIED-DIFY-APPLICATION-001",
            "produced_by": "unified-app/workflows/S4_FACT_CHAIN_DIAGNOSE_v1.0.py",
            "model_calls": 0, "dify_writes": 0, "sut_mutations": 0,
            "rules_frozen_in_source": ["R1", "R2", "R3", "R4", "R5", "R6"],
            "read_only": True,
        },
        "hop_adapter_binding": graph,
        "t2_a_attempt03_chain_5593": next(
            (t for t in chain_a04
             if t.get("evidence_file") == "S4-CAP-CONTENT_BRIEF-POS.json"), None),
        "t2_b_continuation_empty": next(
            (t for t in turns_cont if t.get("turn_index") == 2), None),
        "continuation_chain": turns_cont,
        "attempt03_chain": chain_a04,
        "overwrite_events": {
            "continuation": analyse_chain(turns_cont),
            "attempt03_chain": analyse_chain(chain_a04),
        },
    }
    js = json.dumps(trace, ensure_ascii=False, indent=1)
    if a.out:
        os.makedirs(os.path.dirname(a.out), exist_ok=True)
        io.open(a.out, "w", encoding="utf-8").write(js + "\n")
        print("written:", a.out, "sha256:", sha(js + "\n"))
    else:
        print(js)
    return 0


if __name__ == "__main__":
    sys.exit(main())
