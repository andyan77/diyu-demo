#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""M4-CL31-02/03/04 Attempt 2（M4-FND-029 修复后）

为什么重跑而不是「重抽到满意为止」（N-30 / v0.5 F-15）：
  Attempt 1 暴露了一个**真实产品缺陷**——恢复路径未剥离模型 thinking 段，
  整段内部推理被当成用户正文交付。系统已被修改，因此这是对同一冻结判据的
  **新一次 Attempt**，不是对同一系统的重复采样。
  Attempt 1 的原始记录（CL31_RUNTIME_RAW_A1.json / CL31_02_03_04_VERDICT_A1.json）
  原样保留，不删不改。
  冻结注入输入逐字节不变（input_sha256 必须与 A1 相等，不等即中止）。
"""
import hashlib, importlib.util, json, os, subprocess, sys, time

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
DC_WF = os.path.join(ROOT, "decision-chain", "workflows")
OUT = os.path.join(ROOT, "decision-chain/evidence/m4/final_closure")


def _load(n, p):
    s = importlib.util.spec_from_file_location(n, p); m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m); return m


PUB = _load("m4pub", os.path.join(DC_WF, "DIYU_M4_PUBLISH_AND_REBIND_v0.1.py"))
FA = _load("m4fa", os.path.join(DC_WF, "DIYU_M4_FORMAL_ATTEMPT_v0.1.py"))
FX = _load("m4fx", os.path.join(DC_WF, "DIYU_M4_DETERMINISTIC_PROBE_v0.1.py"))
INJ = _load("m4inj", os.path.join(DC_WF, "DIYU_M4_CL31_INJECT_BUILD_v0.1.py"))
COL = _load("m4col", os.path.join(DC_WF, "DIYU_M4_CL31_RUNTIME_COLLECT_v0.1.py"))

DIRECTIVES = {"INJ-01": "TOOL_FAIL", "INJ-02": "FROZEN_MARKERLESS", "INJ-03": "LIVE_MARKERLESS"}
PROF = "professional_input: 见 capability_call"


def sha(s): return hashlib.sha256((s or "").encode("utf-8")).hexdigest()


def main():
    a1 = json.load(open(os.path.join(OUT, "CL31_RUNTIME_RAW_A1.json"), encoding="utf-8"))
    objs = json.load(open(os.path.join(OUT, "INJECTION_OBJECTS.json"), encoding="utf-8"))
    ids = {p["tag"]: p["app_id"] for p in objs["published"]}
    child_id, seam_id = ids["EVAL-1"], ids["EVAL-2"]
    pid1 = objs["eval1_provider_id"]

    # 冻结输入逐字节不变
    frozen = {t: FX.CT_M3 + "\nM4_FAULT_DIRECTIVE=%s\n" % d for t, d in DIRECTIVES.items()}
    for t, cc in frozen.items():
        if sha(cc) != a1["frozen_input_sha256"][t]:
            raise SystemExit("中止：%s 的冻结输入与 A1 不一致，禁止近似重放" % t)
    print("冻结注入输入 input_sha256 与 A1 逐条相等", flush=True)

    # ── 重建并重发布注入对象，使其恢复子图与新候选逐字节等价 ────────────
    c = PUB.Console(); c.login()
    e1 = INJ.build_eval1(); e2 = INJ.build_eval2(pid1)
    rep = INJ.equivalence_report(e1, e2)
    if not (rep["child_only_injection_source_differs"]
            and rep["recovery_subgraph_bytewise_identical"]
            and rep["seam_only_injection_wiring_differs"]):
        raise SystemExit("中止：注入对象与最终候选不再等价 -> %s" % json.dumps(rep, ensure_ascii=False)[:400])
    print("注入对象等价性复核通过（恢复子图逐字节相同）", flush=True)
    c.import_dsl(open(INJ.EVAL1, encoding="utf-8").read(), app_id=child_id); c.publish(child_id)
    c.import_dsl(open(INJ.EVAL2, encoding="utf-8").read(), app_id=seam_id); c.publish(seam_id)
    params = PUB.params_from_start(INJ.EVAL1)
    PUB.Console and c.update_workflow_tool(pid1, "diyu_m4_ac31_inject_child", INJ.NAME1, params)
    print("注入对象已重发布并重绑", flush=True)

    t0 = COL.psql("SELECT to_char(now(),'YYYY-MM-DD HH24:MI:SS');")[0]
    time.sleep(1)

    tok_seam = FA.ensure_api_key(c, seam_id)
    tok_child = FA.ensure_api_key(c, child_id)
    base = "http://127.0.0.1"

    # INJ-01 走接缝
    body = {"inputs": {"capability": "CONTENT_BRIEF", "entry": "", "capability_call": frozen["INJ-01"],
                       "professional_input": PROF, "example_reference_requested": "NO"},
            "response_mode": "blocking", "user": "m4-cl31-a2-inj01"}
    try:
        FA.service_call(base, tok_seam, "/v1/workflows/run", body, timeout=900)
    except Exception as e:
        print("[INJ-01] 服务调用异常:", str(e)[:200], flush=True)
    COL.wait_idle()

    for tag in ("INJ-02", "INJ-03"):
        body = {"inputs": {"capability_call": frozen[tag], "professional_input": PROF, "entry": "",
                           "run_mode": "", "example_reference_requested": "NO"},
                "response_mode": "blocking", "user": "m4-cl31-a2-%s" % tag.lower()}
        try:
            FA.service_call(base, tok_child, "/v1/workflows/run", body, timeout=900)
        except Exception as e:
            print("[%s] 服务调用异常: %s" % (tag, str(e)[:200]), flush=True)
        COL.wait_idle()

    # ── 只收集 Attempt 2 窗口内的运行 ────────────────────────────────────
    rec = {"attempt": 2, "contract": "V1_M4_EVIDENCE_COLLECTION_CONTRACT_v0.5.md",
           "current_task_contract_hash":
               "8d73b4f157883eb422e6ae17ececcf87a64d98c6a51f35537b8446155fa85070",
           "reason_for_second_attempt":
               "Attempt 1 暴露真实产品缺陷 M4-FND-029（恢复路径未剥离 thinking）；系统已修改，"
               "非同系统重复采样。A1 记录原样保留。",
           "attempt1_ref": "CL31_RUNTIME_RAW_A1.json",
           "window_start": t0,
           "frozen_artifact_sha256": sha(INJ.frozen_artifact()),
           "frozen_input_sha256": {t: sha(v) for t, v in frozen.items()},
           "injection_equivalence": rep,
           "eval_app_ids": {"child": child_id, "seam": seam_id}, "runs": {}}

    def after(rows_):
        return [r for r in rows_ if r["created_at"] >= t0]

    for tag, d in DIRECTIVES.items():
        e = {"directive": "M4_FAULT_DIRECTIVE=" + d, "seam_runs": [], "child_runs": []}
        for r in after(COL.runs_for(seam_id, d)):
            r["node_executions"] = COL.execs_for(r["run_id"]); e["seam_runs"].append(r)
        for r in after(COL.runs_for(child_id, d)):
            r["node_executions"] = COL.execs_for(r["run_id"]); e["child_runs"].append(r)
        e["skill_llm_exec_total"] = sum(1 for r in e["child_runs"] for x in r["node_executions"]
                                        if x["node_id"] == "skill_llm")
        e["recovery_llm_exec_total"] = sum(1 for r in e["child_runs"] for x in r["node_executions"]
                                           if x["node_id"] == "recovery_llm")
        rec["runs"][tag] = e
        print("[%s] seam_runs=%d child_runs=%d skill_llm=%d recovery_llm=%d"
              % (tag, len(e["seam_runs"]), len(e["child_runs"]),
                 e["skill_llm_exec_total"], e["recovery_llm_exec_total"]), flush=True)

    p = os.path.join(OUT, "CL31_RUNTIME_RAW.json")
    json.dump(rec, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=2, sort_keys=True)
    print("evidence -> CL31_RUNTIME_RAW.json（Attempt 2）", flush=True)


if __name__ == "__main__":
    main()
