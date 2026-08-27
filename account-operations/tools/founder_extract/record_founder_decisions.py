#!/usr/bin/env python3
"""登记 Founder 的三项证据绑定裁定，并对每一项做机械复算（零模型调用）。

授权事件：`FOUNDER_EVIDENCE_BINDING_AND_RECOVERY_DECISION = ACCEPTED`，
`entry_mode = RECOVERY_TASK`，合同不变（49021e60…）。

三项裁定各自带**执行侧必须自己算出来的依据**，Founder 只接受证据身份，
不代替执行侧自证技术等价（授权 §1.6）。
"""
import hashlib
import io
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
WT = os.path.dirname(os.path.dirname(TOOLS))
sys.path.insert(0, HERE)
sys.path.insert(0, TOOLS)

import extract_founder_runs as E  # noqa: E402

EV = os.path.join(WT, "account-operations/evidence/ep41-founder-binding-decisions")
V = json.load(io.open(os.path.join(
    WT, "account-operations/evidence/ep39-founder-seven-run-extraction/"
        "FOUNDER_RUN_VERIFICATION.json"), encoding="utf-8"))
INTER = json.load(io.open(os.path.join(
    WT, "account-operations/evidence/ep39-founder-seven-run-extraction/"
        "_binding_intermediate.json"), encoding="utf-8"))
GD = {r["run_id"]: r["graph_delta"] for r in INTER["runs"]}
ROWS = {r["run_id"]: r for r in V["rows"]}

FROZEN_VERSION = "2026-08-27 19:46:47.281053"
UNNAMED_VERSION = "2026-08-27 20:46:36.695260"
OFFICIAL_S6 = "55eb0a6b-44ac-4370-bc8a-478cf5fc7d07"
EXTRA_S6 = "0a0f406d-d4d3-4c4e-9596-2f0c936f5117"


def sha(t):
    return hashlib.sha256(t.encode("utf-8")).hexdigest()


def write(p, t):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with io.open(p, "w", encoding="utf-8", newline="") as f:
        f.write(t)


def decision_1():
    """未命名重新发布版本 = 执行内容等价载体。六项依据逐项复算。"""
    on_unnamed = [r for r in V["rows"] if r["workflow_version"] == UNNAMED_VERSION]
    ev = {
        "node_data_byte_identical": {r["run_id"]: GD[r["run_id"]]["all_node_data_byte_identical"]
                                     for r in on_unnamed},
        "edge_execution_topology_identical": {
            r["run_id"]: GD[r["run_id"]]["edge_topology_identical"] for r in on_unnamed},
        "system_prompt_sha256": {r["run_id"]: r["system_prompt_sha256"] for r in on_unnamed},
        "system_prompt_matches_frozen": {r["run_id"]: r["system_prompt_matches_frozen"]
                                         for r in on_unnamed},
        "model_provider_temperature": {r["run_id"]: r["llm_model"] for r in on_unnamed},
        "offline_recompute_identical": {
            r["run_id"]: {"gate": r["repo_recompute_gate_identical"],
                          "assemble": r["repo_recompute_assemble_identical"],
                          "post_gate": r["repo_recompute_post_gate_identical"]}
            for r in on_unnamed},
    }
    non_semantic = {r["run_id"]: {
        "node_geometry_deltas": sorted(GD[r["run_id"]]["node_geometry_deltas"].keys()),
        "edge_frontend_flag_added": GD[r["run_id"]]["edges_identical_modulo_isInLoop_flag"],
        "viewport_frozen": GD[r["run_id"]]["viewport_frozen"],
        "viewport_actual": GD[r["run_id"]]["viewport_actual"]} for r in on_unnamed}
    all_ok = (all(ev["node_data_byte_identical"].values())
              and all(ev["edge_execution_topology_identical"].values())
              and all(ev["system_prompt_matches_frozen"].values())
              and len({json.dumps(m, sort_keys=True) for m in
                       ev["model_provider_temperature"].values()}) == 1
              and all(all(x.values()) for x in ev["offline_recompute_identical"].values()))
    return {
        "founder_ruling": "EXECUTION_CONTENT_EQUIVALENT_TO_M3_V1.5.2",
        "ruling_scope": "S2-S7 的执行内容等价载体身份；**不宣称版本标签相同**",
        "unnamed_version": UNNAMED_VERSION,
        "unnamed_workflow_id": "ff801653-ba58-48c9-bbfe-e77c144c9b1d",
        "unnamed_marked_name": "",
        "marked_name_historical_record_preserved": True,
        "s1_bound_to": {"version": FROZEN_VERSION, "marked_name": "m3-cand-v1.5.2",
                        "workflow_id": "706fdce0-9a0d-42ec-8a8c-e4f6a3071173"},
        "s2_s7_bound_to": {"version": UNNAMED_VERSION, "marked_name": "",
                           "status": "EXECUTION_CONTENT_EQUIVALENT_TO_M3_V1.5.2"},
        "equivalence_evidence_recomputed_by_execution_side": ev,
        "non_execution_semantic_differences": non_semantic,
        "equivalence_evidence_all_hold": all_ok,
        "authority_note": ("技术等价依据来自执行侧的确定性比对（上表逐项），"
                           "Founder 只接受其证据身份。**不得写成执行侧自行宣布技术等价，"
                           "也不得写成未命名版本就是具名版本。**"),
    }


def decision_2():
    o, x = ROWS[OFFICIAL_S6], ROWS[EXTRA_S6]
    return {
        "founder_ruling": "official_S6 固定为第一次提交",
        "official_S6_run_id": OFFICIAL_S6,
        "extra_S6_run_id": EXTRA_S6,
        "extra_marked_as": "UNAUTHORIZED_EXTRA_SUBMISSION",
        "extra_is_legitimate_retry": False,
        "selection_between_the_two": "NOT_PERFORMED（不择优、不替换、不覆盖、不删除）",
        "official": {"run_id": o["run_id"], "started": o["created_at_local"],
                     "final_body_len": o["final_body_len"],
                     "final_body_sha256": o["final_body_sha256"]},
        "extra": {"run_id": x["run_id"], "started": x["created_at_local"],
                  "final_body_len": x["final_body_len"],
                  "final_body_sha256": x["final_body_sha256"]},
        "S6_FIRST_OUTPUT_PRODUCT_ACCEPTANCE": "PASS",
        "S6_SECOND_OUTPUT_PRODUCT_ACCEPTANCE": "PASS",
        "acceptance_note": ("该确认只表示两份输出在产品上均被接受；"
                            "**不把第二次运行改写成符合「一次运行」协议。**"),
        "FOUNDER_OFFICIAL_TEST_RUNS": 7,
        "DISCLOSED_EXTRA_SUBMISSIONS": 1,
        "formal_acceptance_evidence_bound_to": OFFICIAL_S6,
    }


def decision_3():
    """LF 归一化：只准去掉一个结尾 LF，去掉后必须与冻结输入逐字节相同。"""
    froz = E.frozen_inputs()
    RAW = os.path.join(WT, "account-operations/evidence/"
                           "ep39-founder-seven-run-extraction/raw")
    per, ok = {}, True
    for scen, rid, _role in __import__("verify_founder_runs").BINDING:
        run = json.load(io.open(os.path.join(RAW, rid, "workflow_run.json"), encoding="utf-8"))
        inp = run["inputs"]
        rec = {}
        for k in E.FIELDS:
            actual, frozen = inp.get(k, ""), froz[scen][k]
            if k == "user_request":
                norm = actual[:-1] if actual.endswith("\n") else actual
                removed = len(actual) - len(norm)
                rec[k] = {
                    "raw_sha256": sha(actual), "normalized_sha256": sha(norm),
                    "frozen_sha256": sha(frozen),
                    "trailing_lf_removed": removed,
                    "only_one_lf_removed": removed <= 1,
                    "normalized_equals_frozen_bytewise": norm == frozen,
                    "any_other_char_difference": norm != frozen,
                }
                if not (removed <= 1 and norm == frozen):
                    ok = False
            else:
                rec[k] = {"raw_sha256": sha(actual), "frozen_sha256": sha(frozen),
                          "byte_identical": actual == frozen,
                          "normalization_applied": False}
                if actual != frozen:
                    ok = False
        per[rid] = {"scenario": scen, "fields": rec}
    return {
        "founder_ruling": "DIFY_UI_CARRIER_NORMALIZATION_ACCEPTED",
        "scope": "仅 user_request 结尾的一个 LF；仅本次七场景实测",
        "inputs_byte_identical_claim_allowed": False,
        "per_run": per,
        "account_context_all_byte_identical": all(
            v["fields"]["account_context"]["byte_identical"] for v in per.values()),
        "loaded_references_all_byte_identical": all(
            v["fields"]["loaded_references"]["byte_identical"] for v in per.values()),
        "user_request_all_normalize_to_frozen": all(
            v["fields"]["user_request"]["normalized_equals_frozen_bytewise"]
            for v in per.values()),
        "user_request_at_most_one_lf_removed": all(
            v["fields"]["user_request"]["only_one_lf_removed"] for v in per.values()),
        "all_hold": ok,
        "no_precedent_note": ("此豁免**不得**套用到其他空白、标点、字段或内容差异；"
                             "仅限本次、仅限 user_request 结尾的一个 LF。"),
    }


def main():
    d1, d2, d3 = decision_1(), decision_2(), decision_3()
    rep = {
        "authority_event": "FOUNDER_EVIDENCE_BINDING_AND_RECOVERY_DECISION = ACCEPTED",
        "task_id": "DIYU-V1-M3-ACCOUNT-CONTENT-OPERATOR-001",
        "entry_mode": "RECOVERY_TASK",
        "contract_sha256": "49021e601658194bc734285830d531352c19c1fa4416855c1f524efb073bff49",
        "recorded_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "executor_model_calls": 0,
        "decision_1_unnamed_republish": d1,
        "decision_2_s6_duplicate": d2,
        "decision_3_trailing_lf": d3,
        "all_recomputations_hold": (d1["equivalence_evidence_all_hold"] and d3["all_hold"]),
    }
    write(os.path.join(EV, "FOUNDER_BINDING_DECISIONS.json"),
          json.dumps(rep, ensure_ascii=False, indent=2))
    print("裁定 1 · 等价依据六项全部复算成立 :", d1["equivalence_evidence_all_hold"])
    print("裁定 2 · 正式 S6 =", d2["official_S6_run_id"][:8],
          "| 额外提交 =", d2["extra_S6_run_id"][:8], "(UNAUTHORIZED_EXTRA_SUBMISSION)")
    print("裁定 3 · account_context 八条逐字节相同 :", d3["account_context_all_byte_identical"])
    print("裁定 3 · loaded_references 八条逐字节相同 :", d3["loaded_references_all_byte_identical"])
    print("裁定 3 · user_request 去掉一个 LF 后 == 冻结 :", d3["user_request_all_normalize_to_frozen"])
    print("裁定 3 · 每条最多只去掉 1 个 LF :", d3["user_request_at_most_one_lf_removed"])
    print("全部复算成立 :", rep["all_recomputations_hold"])


if __name__ == "__main__":
    main()
