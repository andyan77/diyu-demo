#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""S4 外部验收复核｜证据真值纠偏。**零模型调用、零 Dify 写入、零工作流发起。**

只做三件确定性的事：
  1. 从 T1–T7 RAW 独立重算技术链事实（不引用任何既有摘要）；
  2. 从 Dify 只读运行库取 PP 真实运行的输入与输出，逐层定位违规文字首次出现的节点；
  3. 重算判据与证据的绑定关系，输出 BINDING_RECONCILIATION。

授权：CONTINUE EXECUTION PROMPT v1.0（DIYU V1 · UAPP S4 证据真值纠偏与 PP 交付边界归因）第三、五节。
本文件不修改任何 v1.0/v1.1 历史文件，不触碰候选画布与九个受保护应用。

    python3 S4_EXTERNAL_REVIEW_v1.0.py
"""
import hashlib
import io
import json
import os
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
UAPP = os.path.abspath(os.path.join(HERE, ".."))
STAGES = os.path.join(UAPP, "stages")
EVDIR = os.path.join(UAPP, "evidence", "stages", "s4_canonical_state")
RUN = os.path.join(EVDIR, "run")

CAND = "85c01f85-a081-43e9-ab09-9993289cc200"
APPS = {"M1_HOST": "a4c3b19b-243f-490b-9aca-3aa19767d6a5",
        "HOP": "6c46fdb1-5f49-4513-a0c0-29957b3dcee4",
        "SEAM": "5fca0162-e26b-4545-a00b-66b1a2a2a077",
        "MATRIX": "fd25ebfa-db67-40c3-82e5-202e1254facf",
        "CAMPAIGN": "1f9d65ea-8af5-45f0-a1d0-a80223d354e2",
        "CONTENT_BRIEF": "b1dcf784-540e-4b3f-8ba2-3812f477f3ce",
        "CREATIVE_SCRIPT": "44b55f9d-3792-40c3-b095-f2696464b4ec",
        "PRODUCTION_DIRECTOR": "13cfabd5-f592-4354-a304-47098b765697",
        "PUBLISHING_PACKAGING": "c9cdea24-9df3-400b-9ecd-1d740e8c96df"}
PP_RUN_ID = "15e2643a-7710-47d0-a162-40b13726219d"

# 冻结探针：来自 PP 冻结输入原文与 CONTINUE EXECUTION PROMPT 第三节 C 的逐条点名。
# 探针本身不判定「好坏」，只判定字符串在哪一层第一次出现。
PROBES = [
    ("PB-01", "一直在用这套三问", "把未登记的人物长期行为写成事实"),
    ("PB-02", "门店做搭配服务", "把未登记的人物长期行为写成事实（评论区口径）"),
    ("PB-03", "常用这套思路", "同上，推断词包装"),
    ("PB-04", "你自己买衣服前", "面向评论互动的提问"),
    ("PB-05", "哪个问题", "面向评论互动的提问（问句尾）"),
    ("PB-06", "评论区", "评论区设计整段"),
    ("PB-07", "只有内容讨论和问题回应", "把 NO_CTA 自我解释成可以引导评论"),
    ("PB-08", "低风险互动范畴", "自造的边界豁免类目"),
    ("PB-09", "不含购买引导", "把『只保留内容本身』改写成『不做购买引导』"),
]
# 冻结上游边界原文（PP 输入内逐字存在，作为 F2 的对照基线）
CTA_CONTRACT_TEXT = "不做购买、到店、私信或领取引导，只保留内容本身"


def psql(sql, db="dify"):
    p = subprocess.run(["docker", "exec", "-i", "docker-db_postgres-1", "psql", "-U", "postgres",
                        "-d", db, "-tA", "-c", sql], capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError("psql: " + (p.stderr or "")[:300])
    return p.stdout.strip()


def sha(s):
    return hashlib.sha256((s or "").encode("utf-8")).hexdigest()


def shaf(p):
    return hashlib.sha256(io.open(p, "rb").read()).hexdigest()


def J(x):
    if isinstance(x, str):
        try:
            return json.loads(x)
        except Exception:
            return {}
    return x or {}


def S(v):
    if v is None:
        return ""
    return v if isinstance(v, str) else json.dumps(v, ensure_ascii=False)


def nd(d, key):
    for n in d.get("node_detail") or []:
        if (n.get("node_id") or "") == key:
            return n
    return None


def chain_facts(T):
    """A. 技术链事实：全部从 RAW 现算。"""
    art, ud = {}, {}
    for i in sorted(T):
        o = J(nd(T[i], "uapp_seam").get("outputs"))
        art["T%d" % i] = {"cap": T[i].get("expect_capability"),
                          "len": len(S(o.get("artifact"))),
                          "sha256": sha(S(o.get("artifact")))}
        ud["T%d" % i] = {"len": len(S(o.get("user_delivery"))),
                         "sha256": sha(S(o.get("user_delivery")))}
    i7 = J(nd(T[7], "uapp_hop").get("inputs"))
    up = S(i7.get("upstream_delivery"))
    seam_tools = {}
    nested_total, nested_status, per_app = 0, {}, {}
    for i in sorted(T):
        info = (T[i].get("nested_app_runs") or {})
        seam_tools["T%d" % i] = sorted(n.get("node_id") for n in
                                       ((info.get("SEAM") or {}).get("latest_run_nodes") or [])
                                       if n.get("type") == "tool")
        for app, d in info.items():
            rs = d.get("runs_during_case") or []
            nested_total += len(rs)
            if rs:
                per_app.setdefault(app, []).append(i)
            for r in rs:
                nested_status[r.get("status")] = nested_status.get(r.get("status"), 0) + 1
    w0 = T[min(T)]["window_start"]
    node_stats = psql(
        "select coalesce(json_agg(json_build_object('type',t.node_type,'status',t.status,"
        "'c',t.c))::text,'[]') from (select ne.node_type, ne.status, count(*) c "
        "from workflow_node_executions ne join workflow_runs wr on wr.id=ne.workflow_run_id "
        "where wr.created_at >= timestamp '%s' and wr.app_id in (%s) group by 1,2) t;"
        % (w0, ",".join("'%s'" % a for a in [CAND] + sorted(APPS.values()))))
    return {
        "top_level_runs": sum(1 for i in T if T[i].get("workflow_run_id")),
        "http_status_set": sorted({T[i].get("http_status") for i in T}),
        "attempts_per_turn": [T[i].get("attempts") for i in sorted(T)],
        "conversation_ids": sorted({T[i].get("conversation_id") for i in T}),
        "graph_sha256_at_run_set": sorted({T[i].get("graph_sha256_at_run") for i in T}),
        "gate_sha256_bound_by_evidence": sorted({T[i].get("gate_sha256") for i in T}),
        "manifest_sha256_bound_by_evidence": sorted({T[i].get("manifest_sha256") for i in T}),
        "nested_app_runs_total": nested_total,
        "nested_app_runs_status": nested_status,
        "nested_app_runs_turns_by_app": {k: v for k, v in sorted(per_app.items())},
        "node_executions_in_window": json.loads(node_stats or "[]"),
        "artifact_per_turn": art,
        "user_delivery_per_turn": ud,
        "T7_upstream_capability": i7.get("upstream_capability"),
        "T7_upstream_len": len(up),
        "T7_upstream_sha256": sha(up),
        "T7_upstream_equals_T6_artifact": sha(up) == art["T6"]["sha256"],
        "seam_tool_nodes_per_turn": seam_tools,
    }


def scope_now():
    g = psql("select w.graph from workflows w join apps a on a.workflow_id=w.id "
             "where a.id='%s';" % CAND)
    return {
        "candidate_graph_sha256": hashlib.sha256(
            json.dumps(json.loads(g), ensure_ascii=False, sort_keys=True).encode("utf-8")
        ).hexdigest(),
        "candidate_nodes": len(json.loads(g).get("nodes") or []),
        "candidate_edges": len(json.loads(g).get("edges") or []),
        "protected_md5": {k: psql("select md5(w.graph) from workflows w join apps a "
                                  "on a.workflow_id=w.id where a.id='%s';" % v).strip()
                          for k, v in sorted(APPS.items())},
    }


def pp_layers(T):
    """B + C. PP 真实运行的输入约束与输出逐层归属。"""
    inp = json.loads(psql("select inputs from workflow_runs where id='%s';" % PP_RUN_ID))
    outp = json.loads(psql("select outputs from workflow_runs where id='%s';" % PP_RUN_ID))
    row = psql("select app_id||'|'||status||'|'||created_at::text||'|'||elapsed_time::text "
               "from workflow_runs where id='%s';" % PP_RUN_ID).split("|")
    t7 = T[7]
    so = J(nd(t7, "uapp_seam").get("outputs"))
    mo = J(nd(t7, "uapp_seam_merge").get("outputs"))
    do = J(nd(t7, "uapp_delivery").get("outputs"))
    layers = [
        ("IN.capability_call", S(inp.get("capability_call"))),
        ("IN.professional_input", S(inp.get("professional_input"))),
        ("PP.raw_preserved", S(outp.get("raw_preserved"))),
        ("PP.artifact", S(outp.get("artifact"))),
        ("PP.user_delivery", S(outp.get("user_delivery"))),
        ("SEAM.artifact", S(so.get("artifact"))),
        ("SEAM.user_delivery", S(so.get("user_delivery"))),
        ("SEAM_MERGE.artifact", S(mo.get("artifact"))),
        ("SEAM_MERGE.user_delivery", S(mo.get("user_delivery"))),
        ("CANVAS.final_text", S(do.get("final_text"))),
        ("CANVAS.answer", S(t7.get("answer"))),
    ]
    names = [n for n, _ in layers]
    body = dict(layers)

    # B. 输入约束是否真实到位
    t6art = S(J(nd(T[6], "uapp_seam").get("outputs")).get("artifact"))
    cc, pi = body["IN.capability_call"], body["IN.professional_input"]
    joined = cc + "\n" + pi
    input_constraints = {
        "cta_contract_verbatim_present": CTA_CONTRACT_TEXT in joined,
        "cta_contract_line": next((l.strip() for l in cc.splitlines()
                                   if "cta_contract" in l), None),
        "NO_CTA_marker_present": "NO_CTA" in joined,
        "facts_registered_present": "facts_registered" in joined,
        "explicit_non_promise_present": "explicit_non_promise" in joined,
        "expression_boundary_present": "expression_boundary" in joined,
        "asset_publish_permission_present": "asset_publish_permission" in joined,
        "T6_PD_artifact_contained_verbatim": t6art in pi,
        "T6_PD_artifact_sha256": sha(t6art),
        "input_lengths": {"capability_call": len(cc), "professional_input": len(pi)},
    }

    # C. 违规文字首次出现层
    trace = []
    for pid, probe, why in PROBES:
        counts = {n: body[n].count(probe) for n in names if body[n].count(probe)}
        first = next((n for n in names if body[n].count(probe)), None)
        trace.append({"id": pid, "probe": probe, "why": why,
                      "first_layer": first, "counts_by_layer": counts,
                      "present_in_pp_input": bool(counts.get("IN.capability_call") or
                                                  counts.get("IN.professional_input"))})

    passthrough = {
        "PP.artifact == SEAM.artifact": sha(body["PP.artifact"]) == sha(body["SEAM.artifact"]),
        "PP.user_delivery == SEAM.user_delivery":
            sha(body["PP.user_delivery"]) == sha(body["SEAM.user_delivery"]),
        "PP.user_delivery == CANVAS.final_text":
            sha(body["PP.user_delivery"]) == sha(body["CANVAS.final_text"]),
        "CANVAS.final_text == CANVAS.answer":
            sha(body["CANVAS.final_text"]) == sha(body["CANVAS.answer"]),
    }
    return {
        "pp_run": {"id": PP_RUN_ID, "app_id": row[0], "app": "PUBLISHING_PACKAGING",
                   "app_id_is_protected_pp": row[0] == APPS["PUBLISHING_PACKAGING"],
                   "status": row[1], "created_at": row[2], "elapsed_time": row[3]},
        "input_constraints": input_constraints,
        "layer_lengths": {n: len(body[n]) for n in names},
        "layer_sha256": {n: sha(body[n]) for n in names},
        "string_provenance": trace,
        "downstream_is_passthrough": passthrough,
    }


def binding(T):
    f = {
        "GATE_v1_0": os.path.join(STAGES, "S4_CANONICAL_TASK_STATE_GATE_v1.0.json"),
        "GATE_v1_1": os.path.join(STAGES, "S4_CANONICAL_TASK_STATE_GATE_v1.1.json"),
        "MANIFEST_v1_0": os.path.join(STAGES,
                                      "S4_CANONICAL_TASK_STATE_CANDIDATE_MANIFEST_v1.0.json"),
        "INPUTS_v1_0": os.path.join(STAGES, "S4_CANONICAL_TASK_STATE_INPUTS_v1.0.json"),
        "RESULT_v1_0": os.path.join(STAGES, "S4_CANONICAL_TASK_STATE_RESULT_v1.0.json"),
        "VERIFY_v1_0": os.path.join(EVDIR, "S4_CANONICAL_STATE_VERIFY.json"),
        "ADJUDICATE_v1_0": os.path.join(HERE, "S4_CANONICAL_STATE_ADJUDICATE_v1.0.py"),
        "NODES_v1_0": os.path.join(HERE, "S4_CANONICAL_STATE_NODES_v1.0.py"),
    }
    h = {k: shaf(v) for k, v in f.items()}
    g10 = json.load(io.open(f["GATE_v1_0"], encoding="utf-8"))
    g11 = json.load(io.open(f["GATE_v1_1"], encoding="utf-8"))
    man = json.load(io.open(f["MANIFEST_v1_0"], encoding="utf-8"))
    ver = json.load(io.open(f["VERIFY_v1_0"], encoding="utf-8"))
    res = json.load(io.open(f["RESULT_v1_0"], encoding="utf-8"))
    ev_gate = sorted({T[i].get("gate_sha256") for i in T})
    findings = []
    findings.append({
        "id": "BR-01",
        "claim": "Gate v1.1 自称 frozen_before_any_implementation_change=true",
        "counter_evidence": g11["document"]["supersedes"]["when"],
        "verdict": "CONTRADICTORY",
        "what_survives": "frozen_before_any_model_run=true（由 Manifest model_calls_so_far=0 与"
                         "证据内 gate_sha256 全等 v1.1 支持）",
        "what_does_not_survive": "frozen_before_any_implementation_change 对 v1.1 不成立："
                                 "v1.1 冻结于 Phase C 实现之后。该字段是 v1.0 的属性被复制到 v1.1。",
    })
    findings.append({
        "id": "BR-02",
        "claim": "Candidate Manifest v1.0 的 criteria_ref 指向 Gate v1.0",
        "manifest_criteria_ref": man["document"]["criteria_ref"],
        "evidence_gate_sha256": ev_gate,
        "gate_v1_1_sha256": h["GATE_v1_1"],
        "verdict": "MISMATCH",
        "note": "正式 T1–T7 全部绑定 Gate v1.1；Manifest 仍指 v1.0。"
                "Manifest 冻结于 git_head=%s（Phase B），早于 v1.1，属时序事实，"
                "但结果引用时不得把两者当作同一判据。" % man["document"]["git_branch"],
    })
    findings.append({
        "id": "BR-03",
        "claim": "S4_CANONICAL_STATE_VERIFY.json（14/14）绑定 Gate v1.0",
        "verify_criteria_ref": ver["document"]["criteria_ref"],
        "verify_criteria_sha256": ver["document"]["criteria_sha256"],
        "equals_gate_v1_0": ver["document"]["criteria_sha256"] == h["GATE_v1_0"],
        "verdict": "MISMATCH",
        "note": "该 14/14 在 Gate v1.0 下成立，不能被引用为『Gate v1.1 下的 14/14』。"
                "本轮以 S4_CANONICAL_STATE_VERIFY_v1.1.json 重绑定后重算。",
    })
    findings.append({
        "id": "BR-04",
        "claim": "RESULT v1.0 的 V-07 展示字段实现缺陷",
        "defect": "S4_CANONICAL_STATE_ADJUDICATE_v1.0.py 中 "
                  "`sorted(k for k, v in last.items() if v == \"E\")` 把字段字典 v 与字符串 \"E\" "
                  "比较，恒为空列表。",
        "impact": "只影响 observed 的展示，不进入 V-07 的 PASS 谓词 "
                  "`V(not bad_ref and not bad_kind and not ph)`。V-07 判定本身不受影响。",
        "verdict": "DISPLAY_ONLY",
        "result_v1_0_V07_display": next((c["observed"].get("E 级字段")
                                         for c in res["conditions"] if c["id"] == "V-07"), None),
    })
    findings.append({
        "id": "BR-05",
        "claim": "RESULT v1.0 的 V-08 用一个 PASS 同时代表五件事",
        "covered_by_one_verdict": ["单能力执行/无暗跑", "无泄漏", "无 M2 重复副作用",
                                   "无事实编造", "CTA 忠实"],
        "discriminating_evidence_available": {
            "单能力执行/无暗跑": "有——seam 工具节点与嵌套 run 计数确定性可判",
            "无泄漏": "有——leak_forbidden_tokens 逐条",
            "无 M2 重复副作用": "有——diyu_business 行数与幂等键",
            "无事实编造": "无——fabrication_probes 只覆盖面料百分比/库存/SKU/顾客口碑姓名/"
                          "预约时段/价格子集/人名白名单，苏禾在白名单内，"
                          "『长期行为主张是否可回指』不在探针覆盖面内",
            "CTA 忠实": "无——leak_forbidden_tokens 与 authorization_overclaim_tokens "
                        "均不含任何 CTA 语义项，CTA 忠实从未被真正检查",
        },
        "verdict": "OVERBROAD_SINGLE_VERDICT",
    })
    return {"file_sha256": h, "evidence_gate_sha256": ev_gate, "findings": findings}


def main():
    T = {}
    for i in range(1, 8):
        p = os.path.join(RUN, "S4-CT-T%d.json" % i)
        T[i] = json.load(io.open(p, encoding="utf-8"))
    meta = json.load(io.open(os.path.join(RUN, "RUN_META.json"), encoding="utf-8"))
    now = scope_now()
    before = meta["scope_snapshot_before"]
    drift = ([{"scope": "candidate_graph", "was": before["candidate_graph_sha256"],
               "now": now["candidate_graph_sha256"]}]
             if before["candidate_graph_sha256"] != now["candidate_graph_sha256"] else [])
    drift += [{"scope": "protected_app", "app": k, "was": before["protected_md5"].get(k), "now": v}
              for k, v in now["protected_md5"].items() if v != before["protected_md5"].get(k)]

    rep = {
        "document": {
            "id": "S4_EXTERNAL_REVIEW_v1.0",
            "task_id": "DIYU-V1-UNIFIED-DIFY-APPLICATION-001",
            "authority": "CONTINUE EXECUTION PROMPT v1.0"
                         "（UAPP S4 证据真值纠偏与 PP 交付边界归因）第三节",
            "model_calls": 0, "dify_writes": 0, "workflow_runs_started": 0,
            "reads_only": ["T1–T7 RAW", "Dify 只读运行库", "Git"],
        },
        "A_chain_facts": chain_facts(T),
        "A_scope_zero_drift_at_review_time": {"drift": drift, "now": now,
                                              "run_meta_before": before},
        "BC_pp_boundary": pp_layers(T),
        "binding_reconciliation": binding(T),
    }
    os.makedirs(EVDIR, exist_ok=True)
    io.open(os.path.join(EVDIR, "S4_EXTERNAL_REVIEW_EVIDENCE_v1.0.json"), "w",
            encoding="utf-8").write(json.dumps(rep, ensure_ascii=False, indent=1) + "\n")
    br = {"document": {"id": "S4_CANONICAL_TASK_STATE_BINDING_RECONCILIATION_v1.0",
                       "task_id": "DIYU-V1-UNIFIED-DIFY-APPLICATION-001",
                       "authority": "CONTINUE EXECUTION PROMPT v1.0 第四节 F4、第五节",
                       "not_an_inplace_edit": "新增文件。不覆盖 Gate v1.0/v1.1、Manifest v1.0、"
                                              "RESULT v1.0、VERIFY(v1.0) 中任何一个字节。",
                       "model_calls": 0},
          "evidence_binding_truth": {
              "formal_run_T1_T7_bound_to": "S4_CANONICAL_TASK_STATE_GATE_v1.1.json",
              "gate_v1_1_sha256": rep["binding_reconciliation"]["file_sha256"]["GATE_v1_1"],
              "gate_v1_0_sha256": rep["binding_reconciliation"]["file_sha256"]["GATE_v1_0"],
              "manifest_v1_0_sha256":
                  rep["binding_reconciliation"]["file_sha256"]["MANIFEST_v1_0"],
              "inputs_v1_0_sha256": rep["binding_reconciliation"]["file_sha256"]["INPUTS_v1_0"],
          },
          "findings": rep["binding_reconciliation"]["findings"],
          "file_sha256": rep["binding_reconciliation"]["file_sha256"]}
    io.open(os.path.join(STAGES, "S4_CANONICAL_TASK_STATE_BINDING_RECONCILIATION_v1.0.json"), "w",
            encoding="utf-8").write(json.dumps(br, ensure_ascii=False, indent=1) + "\n")

    a = rep["A_chain_facts"]
    print("A 顶层 run=%d 嵌套 run=%d %s LLM=%s" % (
        a["top_level_runs"], a["nested_app_runs_total"], a["nested_app_runs_status"],
        [x for x in a["node_executions_in_window"] if x["type"] == "llm"]))
    print("A T7 上游=%s  链哈希相等=%s" % (a["T7_upstream_capability"],
                                         a["T7_upstream_equals_T6_artifact"]))
    print("A 受保护面漂移：%s" % (drift or "无（9/9 + 候选图一致）"))
    b = rep["BC_pp_boundary"]
    print("B PP run app 是受保护 PP：%s  cta_contract 逐字在输入内：%s  PD artifact 逐字在输入内：%s"
          % (b["pp_run"]["app_id_is_protected_pp"],
             b["input_constraints"]["cta_contract_verbatim_present"],
             b["input_constraints"]["T6_PD_artifact_contained_verbatim"]))
    print("C 违规文字首次出现层：")
    for t in b["string_provenance"]:
        print("   %-6s %-12s first=%-18s 在PP输入内=%s" % (t["id"], t["probe"], t["first_layer"],
                                                          t["present_in_pp_input"]))
    print("C 下游是否纯透传：%s" % b["downstream_is_passthrough"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
