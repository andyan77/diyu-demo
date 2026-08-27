#!/usr/bin/env python3
"""Founder 七场景实测的九项只读核验 + 逐场景证据落盘（零模型调用）。

执行侧**不得重新做产品裁决，也不得推翻 Founder 的 PASS**（授权 §4）。
本文件只核验绑定、完整性与确定性行为，不评价内容质量。

九项对应授权 §4：
  V1 七个场景是否全部存在
  V2 每个场景是否只绑定一次正式运行
  V3 输入是否与冻结包逐字一致
  V4 运行是否来自 v1.5.2 已发布候选
  V5 是否存在未披露的纯传输失败或重试
  V6 最终输出是否完整落盘
  V7 Founder 裁决是否准确绑定这七次输出
  V8 闸门或补齐节点是否代写实质交付
  V9 是否出现会使 Founder 裁决对象失真的版本 / 输入 / 证据错绑
"""
import hashlib
import io
import json
import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
WT = os.path.dirname(os.path.dirname(TOOLS))
for p in (os.path.join(TOOLS, "gate_v13"), TOOLS, HERE):
    sys.path.insert(0, p)

import shared_checks as S            # noqa: E402
from gate_main import main as gate_main            # noqa: E402
from assemble_main import main as assemble_main    # noqa: E402
from post_gate_main import main as post_gate_main  # noqa: E402
import extract_founder_runs as E     # noqa: E402

EV = os.path.join(WT, "account-operations/evidence/ep39-founder-seven-run-extraction")
RAW = os.path.join(EV, "raw")
PACK = os.path.join(WT, "account-operations/founder-pack-v152")
RESULTS = os.path.join(PACK, "results")

# 绑定表由 extract 阶段的逐字输入哈希得出，不是按时间挑的。
BINDING = [
    ("S1", "591d3e80-6dc3-436b-8e0b-fdc90e896f9c", "official"),
    ("S2", "41e1fa39-beca-4deb-b158-5ab36ae78aad", "official"),
    ("S3", "136f7212-36ec-4366-99d1-e8dc4c9836a0", "official"),
    ("S4", "8eab421c-1133-453b-9383-acf4e9d269ed", "official"),
    ("S5", "fef43015-e54a-47ce-853e-4a2f522b9187", "official"),
    ("S6", "55eb0a6b-44ac-4370-bc8a-478cf5fc7d07", "official"),
    ("S6", "0a0f406d-d4d3-4c4e-9596-2f0c936f5117", "extra_second_submission"),
    ("S7", "aa92b3ca-a3a8-4125-9314-3d84ce6cf85a", "official"),
]
FROZEN_VERSION = "2026-08-27 19:46:47.281053"
FROZEN_MARKED_NAME = "m3-cand-v1.5.2"
FROZEN_PROMPT_SHA = "3a3c657d82d45e96dfbf9abdcb88adf66c58bb74f69f1e1e0412591242898028"


def sha(t):
    return hashlib.sha256(t.encode("utf-8")).hexdigest()


def jread(p):
    with io.open(p, encoding="utf-8") as f:
        return json.load(f)


def write(p, t):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with io.open(p, "w", encoding="utf-8", newline="") as f:
        f.write(t)


def _subst(t):
    for path in sorted(S.REF_DISPLAY, key=len, reverse=True):
        t = t.replace(path, S.REF_DISPLAY[path])
    for a, b in (("NOT_LOADED", "未加载"), ("LOADED", "已加载")):
        t = re.sub(r"(?<![A-Za-z_])" + a + r"(?![A-Za-z_])", b, t)
    return t


def _is_subseq(small, big):
    it = iter(big)
    return all(ch in it for ch in small)


def _repair_body(raw_fixed):
    """与 assemble_main 同一套剥离，用来拿补齐节点自己写的正文（模型产物）。"""
    f = re.sub(r"<think>.*?</think>", "", raw_fixed or "", flags=re.S)
    f = re.sub(r"<<AUDIT>>.*?<<END_AUDIT>>", "", f, flags=re.S)
    f = re.sub(r"<<AUDIT>>.*$", "", f, flags=re.S).strip()
    return f


def not_authored(final_text, path, draft_raw, raw_fixed):
    """终稿里的每个字符必须来自模型产物（草稿或补齐输出）或那张封闭替换表。

    直发 / 硬失败路 → 源是主生成节点的草稿；
    补齐路         → 源是补齐 LLM 自己的输出（它是模型节点，本来就有权改正文）。
    两条路都要求确定性节点**只许删、不许插**。
    """
    if path == "gate_repaired":
        src = _repair_body(raw_fixed)
    else:
        src, _audit = S.split_audit(draft_raw or "")
    return _is_subseq((final_text or "").strip(), _subst(src)), (
        "repair_output" if path == "gate_repaired" else "draft_body")


def nodes_of(rid):
    return {n["node_id"]: n for n in jread(os.path.join(RAW, rid, "node_executions.json"))}


def main():
    froz = E.frozen_inputs()
    census = jread(os.path.join(EV, "app_logs_census.json"))
    lineage = jread(os.path.join(EV, "published_version_lineage.json"))
    inter = jread(os.path.join(EV, "_binding_intermediate.json"))
    gd = {r["run_id"]: r["graph_delta"] for r in inter["runs"]}
    rows = []

    for scen, rid, role in BINDING:
        run = jread(os.path.join(RAW, rid, "workflow_run.json"))
        nx = nodes_of(rid)
        end_out = nx["end"]["outputs"]
        gate_out = nx["required_item_gate"]["outputs"]
        asm_out = nx["assemble"]["outputs"]
        asm_in = nx["assemble"]["inputs"]
        pg_out = nx["post_gate"]["outputs"]
        llm_out = nx["operating_one_account_llm"]["outputs"]
        inp = run["inputs"]

        deltas = {k: E.field_delta(froz[scen][k], inp.get(k, "")) for k in E.FIELDS}

        g = gate_main(end_out["draft_raw"], inp["loaded_references"], inp["account_context"])
        gate_match = (g["gate_report"] == gate_out["gate_report"] and g["body"] == gate_out["body"]
                      and g["needs_fix"] == gate_out["needs_fix"]
                      and g["gate_status"] == gate_out["gate_status"])
        a = assemble_main(g["body"], asm_in.get("fixed", ""), g["needs_fix"], g["gate_status"],
                          g["draft_audit"])
        asm_match = (a["final_text"] == asm_out["final_text"] and a["path"] == asm_out["path"]
                     and a["final_audit"] == asm_out["final_audit"])
        pg = post_gate_main(a["final_text"], inp["loaded_references"], g["gate_report"],
                            inp["account_context"], a["final_audit"], a["path"])
        pg_match = (pg["post_gate_report"] == pg_out["post_gate_report"]
                    and pg["cycle_state_carry"] == pg_out["cycle_state_carry"]
                    and pg["operating_judgment_final"] == pg_out["operating_judgment_final"])

        na, na_src = not_authored(asm_out["final_text"], asm_out["path"],
                                  end_out["draft_raw"], asm_in.get("fixed", ""))
        gate_na, _ = not_authored(gate_out["body"], "direct", end_out["draft_raw"], "")

        # 模型配置与系统提示词直接从**这一次运行自带的执行图**里取，不从别处推断
        gnode = {n["id"]: n for n in run["graph"]["nodes"]}["operating_one_account_llm"]["data"]
        llm_cfg = {"provider": gnode.get("model", {}).get("provider"),
                   "name": gnode.get("model", {}).get("name"),
                   "completion_params": gnode.get("model", {}).get("completion_params")}
        sys_sha = sha("".join(x.get("text", "") for x in (gnode.get("prompt_template") or [])
                              if x.get("role") == "system"))

        gr = json.loads(gate_out["gate_report"])
        pgr = json.loads(pg_out["post_gate_report"])
        usage = (json.loads(llm_out["usage"]) if isinstance(llm_out.get("usage"), str)
                 else llm_out.get("usage"))

        row = {
            "scenario": scen, "run_id": rid, "role": role,
            "workflow_version": run["version"],
            "is_frozen_marked_version": run["version"] == FROZEN_VERSION,
            "status": run["status"], "error": run["error"],
            "created_at": run["created_at"], "finished_at": run["finished_at"],
            "created_at_local": time.strftime("%Y-%m-%d %H:%M:%S",
                                              time.localtime(run["created_at"])),
            "elapsed_seconds": run["elapsed_time"], "total_tokens": run["total_tokens"],
            "total_steps": run["total_steps"], "exceptions_count": run["exceptions_count"],
            "created_by_role": run["created_by_role"],
            "end_user_session": (run.get("created_by_end_user") or {}).get("session_id"),
            "node_statuses": {k: v["status"] for k, v in nx.items()},
            "node_errors": {k: v.get("error") for k, v in nx.items() if v.get("error")},
            "truncated_any": any(v.get("inputs_truncated") or v.get("outputs_truncated")
                                 or v.get("process_data_truncated") for v in nx.values()),
            "input_deltas": deltas,
            "input_all_identical": all(d["verdict"] == "IDENTICAL" for d in deltas.values()),
            "input_identical_or_whitespace": all(
                d["verdict"] in ("IDENTICAL", "WHITESPACE_ONLY") for d in deltas.values()),
            "gate_version": gr.get("gate_version"),
            "post_gate_version": pgr.get("post_gate_version"),
            "gate_status": gate_out["gate_status"], "gate_path": asm_out["path"],
            "cycle_state_carry": pg_out["cycle_state_carry"],
            "carry_reject_reason": pg_out["carry_reject_reason"],
            "draft_raw_len": len(end_out["draft_raw"]),
            "final_body_len": len(end_out["operating_judgment"]),
            "final_body_sha256": sha(end_out["operating_judgment"]),
            "draft_raw_sha256": sha(end_out["draft_raw"]),
            "llm_model": llm_cfg, "system_prompt_sha256": sys_sha,
            "system_prompt_matches_frozen": sys_sha == FROZEN_PROMPT_SHA,
            "llm_finish_reason": llm_out.get("finish_reason"),
            "llm_usage": usage,
            "repo_recompute_gate_identical": gate_match,
            "repo_recompute_assemble_identical": asm_match,
            "repo_recompute_post_gate_identical": pg_match,
            "deterministic_no_authoring": na, "no_authoring_source": na_src,
            "gate_body_no_authoring": gate_na,
            "end_equals_post_gate": (end_out["operating_judgment"]
                                     == pg_out["operating_judgment_final"]),
            "post_gate_equals_assemble": (pg_out["operating_judgment_final"]
                                          == asm_out["final_text"]),
        }
        rows.append(row)

        d = (os.path.join(RESULTS, scen) if role == "official"
             else os.path.join(RESULTS, scen, "extra_second_submission_" + rid[:8]))
        for k in E.FIELDS:
            write(os.path.join(d, "input_%s.txt" % k), inp.get(k, ""))
        write(os.path.join(d, "final_output.txt"), end_out["operating_judgment"])
        write(os.path.join(d, "draft_raw.txt"), end_out["draft_raw"])
        write(os.path.join(d, "gate_report.json"), gate_out["gate_report"])
        write(os.path.join(d, "post_gate_report.json"), pg_out["post_gate_report"])
        write(os.path.join(d, "positions_final.json"), pg_out["positions_final"])
        if asm_out["path"] == "gate_repaired":
            write(os.path.join(d, "gate_repair_raw.txt"), asm_in.get("fixed", ""))
        write(os.path.join(d, "final_audit.txt"), asm_out["final_audit"])
        write(os.path.join(d, "node_executions.json"),
              json.dumps(jread(os.path.join(RAW, rid, "node_executions.json")),
                         ensure_ascii=False, indent=2))
        write(os.path.join(d, "run_meta.json"), json.dumps({
            "scenario": scen, "run_id": rid, "role": role,
            "app_id": E.APP, "workflow_version": run["version"],
            "frozen_candidate_marked_name": FROZEN_MARKED_NAME,
            "frozen_candidate_version": FROZEN_VERSION,
            "ran_on_frozen_marked_version": run["version"] == FROZEN_VERSION,
            "executed_graph_vs_frozen": gd[rid],
            "status": run["status"], "error": run["error"],
            "started_at_epoch": run["created_at"], "finished_at_epoch": run["finished_at"],
            "started_at_local": row["created_at_local"],
            "elapsed_seconds": run["elapsed_time"], "total_tokens": run["total_tokens"],
            "total_steps": run["total_steps"], "created_by_role": run["created_by_role"],
            "end_user_session": row["end_user_session"], "created_from": "web-app",
            "model": llm_cfg, "system_prompt_sha256": sys_sha,
            "system_prompt_matches_frozen": sys_sha == FROZEN_PROMPT_SHA,
            "input_sha256": {k: sha(inp.get(k, "")) for k in E.FIELDS},
            "frozen_input_sha256": {k: sha(froz[scen][k]) for k in E.FIELDS},
            "input_deltas": deltas,
            "gate_version": gr.get("gate_version"),
            "post_gate_version": pgr.get("post_gate_version"),
            "gate_status": gate_out["gate_status"], "gate_path": asm_out["path"],
            "cycle_state_carry": pg_out["cycle_state_carry"],
            "final_output_sha256": row["final_body_sha256"],
            "draft_raw_sha256": row["draft_raw_sha256"],
            "founder_acceptance": "M3_FOUNDER_ACCEPTANCE = PASS（Founder 整体裁决，非逐场景）",
            "extraction_method": "Dify Console API 只读："
                                 "workflow-app-logs / workflow-runs / node-executions",
            "extraction_transport": census.get("transport"),
            "extracted_at": census.get("extracted_at"),
        }, ensure_ascii=False, indent=2))

    official = [r for r in rows if r["role"] == "official"]
    extra = [r for r in rows if r["role"] != "official"]

    V = {}
    V["V1_all_seven_present"] = {
        "scenarios": sorted({r["scenario"] for r in official}),
        "pass": sorted({r["scenario"] for r in official}) == ["S%d" % i for i in range(1, 8)]}
    V["V2_one_official_run_each"] = {
        "counts": {s: sum(1 for r in official if r["scenario"] == s)
                   for s in sorted({r["scenario"] for r in official})},
        "extra_submissions": [{"scenario": r["scenario"], "run_id": r["run_id"],
                               "created_at_local": r["created_at_local"],
                               "status": r["status"]} for r in extra],
        "pass": (all(sum(1 for r in official if r["scenario"] == s) == 1
                     for s in {r["scenario"] for r in official}) and not extra)}
    V["V3_inputs_verbatim"] = {
        "all_fields_identical": all(r["input_all_identical"] for r in rows),
        "identical_or_whitespace_only": all(r["input_identical_or_whitespace"] for r in rows),
        "per_field_verdicts": {r["run_id"][:8]: {k: v["verdict"]
                                                 for k, v in r["input_deltas"].items()}
                               for r in rows},
        "pass": all(r["input_all_identical"] for r in rows)}
    V["V4_ran_on_frozen_candidate"] = {
        "runs_on_frozen_marked_version": [r["run_id"] for r in rows
                                          if r["is_frozen_marked_version"]],
        "runs_on_other_version": [{"run_id": r["run_id"], "scenario": r["scenario"],
                                   "version": r["workflow_version"]}
                                  for r in rows if not r["is_frozen_marked_version"]],
        "executed_graph_all_node_data_identical_to_frozen": {
            r["run_id"][:8]: gd[r["run_id"]]["all_node_data_byte_identical"] for r in rows},
        "executed_graph_edge_topology_identical": {
            r["run_id"][:8]: gd[r["run_id"]]["edge_topology_identical"] for r in rows},
        "executed_graph_byte_identical": {
            r["run_id"][:8]: gd[r["run_id"]]["byte_identical_to_frozen_graph"] for r in rows},
        "system_prompt_sha256_all_runs": sorted({r["system_prompt_sha256"] for r in rows}),
        "system_prompt_matches_frozen_all_runs": all(r["system_prompt_matches_frozen"]
                                                     for r in rows),
        "model_config_all_runs": sorted({json.dumps(r["llm_model"], sort_keys=True,
                                                    ensure_ascii=False) for r in rows}),
        "executable_content_binding_pass": all(
            r["system_prompt_matches_frozen"]
            and gd[r["run_id"]]["all_node_data_byte_identical"]
            and gd[r["run_id"]]["edge_topology_identical"] for r in rows),
        "label_binding_pass": all(r["is_frozen_marked_version"] for r in rows),
        "note": "两半分开算：可执行内容绑定（系统提示词 + 全部节点 data + 边拓扑）与"
                "已发布版本标签绑定。前者成立不得自动上推成后者成立。",
        "pass": all(r["is_frozen_marked_version"] for r in rows)}
    V["V5_no_undisclosed_transport_failure_or_retry"] = {
        "all_succeeded": all(r["status"] == "succeeded" for r in rows),
        "runs_with_error": [r["run_id"] for r in rows if r["error"]],
        "node_errors": {r["run_id"][:8]: r["node_errors"] for r in rows if r["node_errors"]},
        "duplicate_submissions": V["V2_one_official_run_each"]["extra_submissions"],
        "pure_transport_failures_found": 0,
        "pass": (all(r["status"] == "succeeded" for r in rows)
                 and not any(r["error"] for r in rows) and not extra)}
    V["V6_outputs_fully_landed"] = {
        "any_truncated": any(r["truncated_any"] for r in rows),
        "empty_final_body": [r["run_id"] for r in rows if r["final_body_len"] == 0],
        "final_body_lens": {r["run_id"][:8]: r["final_body_len"] for r in rows},
        "end_equals_post_gate": all(r["end_equals_post_gate"] for r in rows),
        "post_gate_equals_assemble": all(r["post_gate_equals_assemble"] for r in rows),
        "pass": (not any(r["truncated_any"] for r in rows)
                 and not [r for r in rows if r["final_body_len"] == 0]
                 and all(r["end_equals_post_gate"] and r["post_gate_equals_assemble"]
                         for r in rows))}
    V["V7_founder_verdict_bound"] = {
        "founder_statement": "M3_FOUNDER_ACCEPTANCE = PASS; founder_observed_all_outputs = true; "
                             "founder_test_runs_completed = 7/7",
        "official_runs_bound": len(official),
        "note": "Founder 给的是整体裁决，不是逐场景裁决；本项只核验 7 条正式运行全部落盘可回指。",
        "pass": len(official) == 7 and all(r["final_body_len"] > 0 for r in official)}
    V["V8_no_deterministic_authoring"] = {
        "criterion": "终稿与闸门正文的每个字符必须来自模型产物（草稿或补齐输出），"
                     "或来自 render_body 那张封闭替换表；子序列判定，只许删不许插。",
        "final_text_not_authored": {r["run_id"][:8]: r["deterministic_no_authoring"] for r in rows},
        "gate_body_not_authored": {r["run_id"][:8]: r["gate_body_no_authoring"] for r in rows},
        "sources_used": {r["run_id"][:8]: r["no_authoring_source"] for r in rows},
        "repo_recompute_identical": {
            r["run_id"][:8]: {"gate": r["repo_recompute_gate_identical"],
                              "assemble": r["repo_recompute_assemble_identical"],
                              "post_gate": r["repo_recompute_post_gate_identical"]} for r in rows},
        "pass": (all(r["deterministic_no_authoring"] and r["gate_body_no_authoring"]
                     for r in rows)
                 and all(r["repo_recompute_gate_identical"]
                         and r["repo_recompute_assemble_identical"]
                         and r["repo_recompute_post_gate_identical"] for r in rows))}
    V["V9_no_distorting_misbinding"] = {
        "version_lineage_in_founder_window": [
            v for v in lineage["versions"]
            if v["created_at"] and rows[0]["created_at"] <= v["created_at"] <= rows[-1]["created_at"]],
        "gate_version_reported_by_every_run": sorted({r["gate_version"] for r in rows}),
        "post_gate_version_reported_by_every_run": sorted({r["post_gate_version"] for r in rows}),
        "all_runs_same_end_user_session": len({r["end_user_session"] for r in rows}) == 1,
        "service_api_runs_excluded": census["by_created_from"].get("service-api"),
        "pass": (sorted({r["gate_version"] for r in rows}) == ["v1.5.2"]
                 and sorted({r["post_gate_version"] for r in rows}) == ["v1.5.2"]
                 and len({r["end_user_session"] for r in rows}) == 1)}

    report = {"generated_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
              "model_calls_made_by_this_tool": 0,
              "binding": [{"scenario": s, "run_id": r, "role": ro} for s, r, ro in BINDING],
              "rows": rows, "checks": V,
              "all_pass": all(v["pass"] for v in V.values()),
              "failing": [k for k, v in V.items() if not v["pass"]]}
    write(os.path.join(EV, "FOUNDER_RUN_VERIFICATION.json"),
          json.dumps(report, ensure_ascii=False, indent=2))

    for k, v in V.items():
        print(("PASS " if v["pass"] else "FAIL ") + k)
    print("\nall_pass =", report["all_pass"], "| failing =", report["failing"])
    return report


if __name__ == "__main__":
    main()
