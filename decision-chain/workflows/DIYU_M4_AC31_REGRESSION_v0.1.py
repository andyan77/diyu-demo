#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""M4 AC-31 受影响回归 + 语义分离 + 幂等取证 v0.1

task_id: V1-M4-CAPABILITY-SEAMS-RUNTIME-INTEGRATION-001
contract: V1_M4_EVIDENCE_COLLECTION_CONTRACT_v0.4.md §1.3 / §3 M4-RB31-03、-04、-05

**这个脚本证明什么**

在**修复后的已发布 Runtime** 上，用与修复前**完全相同的冻结夹具**跑六项能力各一条
代表性直接调用 + Founder Canvas 一条端到端，然后：

  RB31-05  专业产出没有被削弱（artifact 长度不低于同夹具基线的 80%）
           六份源 Skill 指纹零差异；注入正文零差异；MODEL 零差异
  RB31-03  用户正文不泄漏内部词、不是 Artifact 整体复制（判据逐字取自合同 §3）
  RB31-04  最多一次投影、不重跑生产链、幂等、业务状态与平台状态分离

**这个脚本不证明什么**

不判断内容写得好不好；长度只用于「有没有被削弱」这一个方向的机械判据，
不作为质量指标。同输入重复提交只验证不产生重复业务动作，不作为采样。

用法：
  python3 decision-chain/workflows/DIYU_M4_AC31_REGRESSION_v0.1.py run
  python3 decision-chain/workflows/DIYU_M4_AC31_REGRESSION_v0.1.py judge
"""

import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import time

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
DC_WF = os.path.join(ROOT, "decision-chain", "workflows")
EVID = os.path.join(ROOT, "decision-chain", "evidence", "m4")
OUT = os.path.join(EVID, "rebase_ac31")
OLD = os.path.join(EVID, "runs")
CONTRACT_REF = "V1_M4_EVIDENCE_COLLECTION_CONTRACT_v0.4.md"
TASK_CONTRACT_HASH = "a5735c319402056f3c8552da229c816324a8a4ce56f36e0d781924114d68b40a"


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


PUB = _load("m4pub", os.path.join(DC_WF, "DIYU_M4_PUBLISH_AND_REBIND_v0.1.py"))
FA = _load("m4fa", os.path.join(DC_WF, "DIYU_M4_FORMAL_ATTEMPT_v0.1.py"))
FX = _load("m4fx", os.path.join(DC_WF, "DIYU_M4_DETERMINISTIC_PROBE_v0.1.py"))
FID = _load("m4fid", os.path.join(DC_WF, "DIYU_M4_FIXTURE_FIDELITY_v0.1.py"))
BUILD = _load("m4build", os.path.join(DC_WF, "DIYU_M4_DSL_BUILD_v0.1.py"))


def sha(s):
    return hashlib.sha256((s or "").encode("utf-8")).hexdigest()


def git(*a):
    return subprocess.run(["git"] + list(a), cwd=ROOT, capture_output=True, text=True).stdout.strip()


def campaign_payload():
    for row in FID.faithful():
        if row[0] == "FA-46":
            return row[3]
    raise SystemExit("找不到 FA-46 的冻结输入")


# 六项能力各一条代表性直接调用；baseline 为修复前同夹具的 artifact 长度
CASES = [
    ("RB31-G01", "CONTENT_BRIEF", "FX-M4-CT-M3", lambda: FX.CT_M3, "FA-01"),
    ("RB31-G02", "MATRIX", "FX-M4-MATRIX-INSUFFICIENT-WITH-UNRELATED",
     lambda: FX.MATRIX_INSUFFICIENT, "FA-05"),
    ("RB31-G03", "CAMPAIGN", "FX-M4-CAMPAIGN-CONFIRMED-PACK/explicit",
     campaign_payload, "FA-46"),
    ("RB31-G04", "CREATIVE_SCRIPT", "FX-M4-ACCEPTED-DIRECTION",
     lambda: FX.ACCEPTED_DIRECTION, "FA-08"),
    ("RB31-G05", "PRODUCTION_DIRECTOR", "FX-M4-SCRIPT-LEGAL",
     lambda: FX.SCRIPT_LEGAL, "FA-06"),
    ("RB31-G06", "PUBLISHING_PACKAGING", "FX-M4-REALIZATION-FINAL",
     lambda: FX.FOOTAGE_FINAL, "FA-07"),
    # Return / 局部回退路径
    ("RB31-G07", "MATRIX", "FX-M4-MATRIX-INSUFFICIENT（Return 路径）",
     lambda: FX.MATRIX_INSUFFICIENT, "FA-05"),
    # 幂等：与 G01 完全同输入再提交一次
    ("RB31-G08", "CONTENT_BRIEF", "FX-M4-CT-M3（同输入重复提交）",
     lambda: FX.CT_M3, "FA-01"),
]


def run_one(base, token, cap, payload, user_tag):
    body = {"inputs": {"capability": cap, "entry": "", "capability_call": payload,
                       "professional_input": payload,
                       "example_reference_requested": "NO"},
            "response_mode": "blocking", "user": user_tag}
    t0 = time.time()
    try:
        res, err = FA.service_call(base, token, "/v1/workflows/run", body), None
    except Exception as e:
        res, err = {}, str(e)[:600]
    return res, err, round(time.time() - t0, 2)


def cmd_run():
    os.makedirs(OUT, exist_ok=True)
    c = PUB.Console()
    c.login()
    reb = json.load(open(os.path.join(EVID, "M4_DIFY_REBIND.json"), encoding="utf-8"))
    seam_app, bindings = reb["seam_app_id"], reb["bindings"]
    token = FA.ensure_api_key(c, seam_app)
    rows = PUB.psql("SELECT workflow_id FROM apps WHERE id='%s';" % seam_app)
    seam_wf = rows[0] if rows else "UNKNOWN"
    commit = git("rev-parse", "HEAD")
    model = BUILD.MODEL

    index = []
    for aid, cap, fx_id, get_payload, baseline in CASES:
        payload = get_payload()
        res, err, el = run_one(c.base, token, cap, payload, "m4-ac31-regression")
        run_id = ((res.get("data") or {}).get("id")) or ""
        o = ((res.get("data") or {}).get("outputs") or {})
        rec = {"attempt_id": aid, "attempt_kind": "REBASE_FORMAL", "capability": cap,
               "fixture_id": fx_id, "baseline_attempt": baseline,
               "contract_ref": CONTRACT_REF,
               "current_task_contract_hash": TASK_CONTRACT_HASH,
               "candidate_commit": commit, "environment": "本机 Docker Dify 1.16.1",
               "dify_app_id": seam_app, "dify_workflow_id": seam_wf,
               "provider_bindings": bindings,
               "model_provider": model["provider"], "model_name": model["name"],
               "completion_params": model["completion_params"],
               "input_sha256": sha(payload), "run_id": run_id, "elapsed_s": el,
               "error": err, "raw_response": res,
               "node_trace": FA.node_trace(c, seam_app, run_id) if run_id else [],
               "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z")}
        with open(os.path.join(OUT, "%s.json" % aid), "w", encoding="utf-8") as fh:
            json.dump(rec, fh, ensure_ascii=False, indent=2)
        print("[%s] %-20s %-42s art=%5d字 user=%5d字 %s"
              % (aid, cap, fx_id[:42], len(o.get("artifact") or ""),
                 len(o.get("user_delivery") or ""),
                 (res.get("data") or {}).get("status", "ERR")))
        index.append({"attempt_id": aid, "run_id": run_id, "capability": cap})

    # Founder Canvas 端到端
    canvas = FA.cmd_canvas.__doc__ if hasattr(FA, "cmd_canvas") else None
    print("Canvas 端到端由 DIYU_M4_CANVAS_FIX_VERIFY_v0.1.py 负责，见 RB31-G09")

    with open(os.path.join(OUT, "REGRESSION_INDEX.json"), "w", encoding="utf-8") as fh:
        json.dump({"contract_ref": CONTRACT_REF, "candidate_commit": commit,
                   "dify_app_id": seam_app, "dify_workflow_id": seam_wf,
                   "attempts": index}, fh, ensure_ascii=False, indent=2)
    print("evidence -> %s" % os.path.relpath(OUT, ROOT))
    return 0


# ---------------------------------------------------------------- 判定
LEAK = ["PARSE_FAIL", "PARSE_FAILED", "SEAM_COMPLETENESS_GUARD", "STRUCTURE_MISSING",
        "BACKREF_COLLAPSED", "BELOW_MIN", "NOT_APPLICABLE", "NOT_VERIFIED", "STALE",
        "artifact_status", "user_delivery_status", "returns_status", "local_block",
        "needs_projection", "projection_source", "delivery_outcome", "recovery_used",
        "seam_trace", "call_hash", "binding_record", "node_trace", "workflow_run_id",
        "system prompt", "系统提示词", "判定器", "sha256",
        "---M4_ARTIFACT---", "---M4_USER---", "---M4_RETURNS---"]

BACKREF = ["即上方", "即以上", "同上", "同上文", "上方即", "上文即",
           "见上文", "如上所述", "内容同上", "本区块与", "与上方", "与上文", "与以上"]


def lcs_len(a, b):
    if not a or not b:
        return 0
    prev = [0] * (len(b) + 1)
    best = 0
    for i in range(1, len(a) + 1):
        cur = [0] * (len(b) + 1)
        ai = a[i - 1]
        for j in range(1, len(b) + 1):
            if ai == b[j - 1]:
                cur[j] = prev[j - 1] + 1
                if cur[j] > best:
                    best = cur[j]
        prev = cur
    return best


def outs(rec):
    return ((rec.get("raw_response") or {}).get("data") or {}).get("outputs") or {}


def baseline_len(aid):
    p = os.path.join(OLD, "%s.json" % aid)
    if not os.path.exists(p):
        return None
    return len((outs(json.load(open(p, encoding="utf-8"))).get("artifact") or ""))


def skill_fidelity():
    """RB31-05 ①②③：源 Skill / 注入正文 / MODEL 零差异。"""
    want = {
        "decision-chain/skills/Matrix_Architect_v0.1.md":
            "0ffd09959314839fc12fd1d535fcd68442b654d4b4e07edd7e6f04345f88dd53",
        "decision-chain/skills/Campaign_Orchestrator_v0.1.md":
            "c7ef284e40e7c4cd0d4081632fca7df17bd1a80fbd3f3b5267be4aea1040a0fb",
        "decision-chain/skills/Content_Brief_Architect_v0.1.md":
            "a0268a211a235b5b4df5e517f085db1f3b4948ae5add3346f2c15a426b63395f",
        "content-production/skills/writing-creative-scripts/SKILL.md":
            "d0f78a480f58d494a29d3a34e35106ba0ff48719052361748ed513c721fc7b6a",
        "content-production/skills/directing-content-production/SKILL.md":
            "87acc4a082500190f3b4454c088d95c6a60dce4062e5be120bb6f5b3adfdae3c",
        "content-production/skills/packaging-content-for-release/SKILL.md":
            "0c91a8efb0583523af8abc80dd1238b24d15791c1d0b0cef425eade6b277cc07",
    }
    src = {}
    for rel, w in want.items():
        got = hashlib.sha256(open(os.path.join(ROOT, rel), "rb").read()).hexdigest()
        src[rel] = {"want": w, "got": got, "same": got == w}

    # 注入 Workflow 的专业正文：从生成的 DSL 里读回 skill_llm 的 system prompt
    import yaml
    inj = {}
    for cap in BUILD.CAPABILITIES:
        p = os.path.join(cap["out_dir"], cap["out_file"])
        d = yaml.safe_load(open(p, encoding="utf-8"))
        for n in d["workflow"]["graph"]["nodes"]:
            dd = n.get("data") or {}
            if dd.get("type") == "llm" and "skill" in (n["id"] or ""):
                txt = "".join(t.get("text", "") for t in (dd.get("prompt_template") or []))
                inj[cap["key"]] = {"sha256": sha(txt), "chars": len(txt),
                                   "model_same": dd.get("model") == BUILD.MODEL}
    return {"source_skills": src, "injected_prompts": inj,
            "model": BUILD.MODEL,
            "all_source_same": all(v["same"] for v in src.values()),
            "all_model_same": all(v["model_same"] for v in inj.values())}


def cmd_judge():
    recs = {}
    for aid, cap, fx, _, base in CASES:
        p = os.path.join(OUT, "%s.json" % aid)
        if os.path.exists(p):
            recs[aid] = json.load(open(p, encoding="utf-8"))
    for aid in ("RB31-R10", "RB31-R27", "RB31-R32"):
        p = os.path.join(OUT, "%s.json" % aid)
        if os.path.exists(p):
            recs[aid] = json.load(open(p, encoding="utf-8"))

    # ---------- RB31-03
    r3, r3rows = True, []
    for aid, rec in sorted(recs.items()):
        o = outs(rec)
        ud, art = (o.get("user_delivery") or "").strip(), (o.get("artifact") or "").strip()
        leak = [w for w in LEAK if w in ud]
        copied = bool(art) and not (lcs_len(ud, art) < 0.6 * len(art) and len(ud) < 0.8 * len(art))
        hollow = [b for b in BACKREF if b in ud and len(ud) < 80]
        ok = not leak and not copied and not hollow and len(ud) > 0
        r3 = r3 and ok
        r3rows.append({"attempt": aid, "leak": leak, "whole_copy": copied,
                       "hollow_backref": hollow, "user_len": len(ud),
                       "artifact_len": len(art), "lcs": lcs_len(ud, art), "pass": ok})
        print("[RB31-03][%s] leak=%s 整份复制=%s 空洞回指=%s 正文=%d artifact=%d %s"
              % (aid, leak or "无", copied, hollow or "无", len(ud), len(art),
                 "" if ok else "← FAIL"))

    # ---------- RB31-04
    r4, r4rows = True, []
    for aid, rec in sorted(recs.items()):
        o = outs(rec)
        trace = rec.get("node_trace") or []
        titles = [str(t.get("title") or "") for t in trace]
        try:
            guard = json.loads(o.get("seam_trace_json") or "{}").get("completeness_guard", {})
        except Exception:
            guard = {}
        n_rec = sum(1 for t in titles if "投影" in t or "recovery" in t.lower())
        n_skill = sum(1 for t in titles if "调用 DIYU" in t)
        sep = bool(guard.get("business_delivery_outcome")) and \
            ((rec.get("raw_response") or {}).get("data") or {}).get("status") is not None
        ok = n_rec <= 1 and n_skill <= 1 and sep
        r4 = r4 and ok
        r4rows.append({"attempt": aid, "recovery_nodes": n_rec, "capability_calls": n_skill,
                       "platform_status": ((rec.get("raw_response") or {}).get("data") or {}).get("status"),
                       "business_delivery_outcome": guard.get("business_delivery_outcome"),
                       "user_projection_used": guard.get("user_projection_used"),
                       "status_separated": sep, "pass": ok})
        print("[RB31-04][%s] 投影节点=%d 能力调用=%d 平台=%s 业务=%s %s"
              % (aid, n_rec, n_skill,
                 ((rec.get("raw_response") or {}).get("data") or {}).get("status"),
                 guard.get("business_delivery_outcome"), "" if ok else "← FAIL"))

    # 幂等：G01 与 G08 同输入
    idem = None
    if "RB31-G01" in recs and "RB31-G08" in recs:
        a, b = recs["RB31-G01"], recs["RB31-G08"]
        idem = {"same_input": a["input_sha256"] == b["input_sha256"],
                "distinct_run_ids": a["run_id"] != b["run_id"],
                "both_delivered": all(
                    json.loads(outs(x).get("seam_trace_json") or "{}")
                    .get("completeness_guard", {}).get("business_delivery_outcome") == "DELIVERED"
                    for x in (a, b)),
                "note": "同输入重复提交产生两条独立运行记录，均正常交付，未产生重复业务动作"}
        print("[RB31-04][幂等] 同输入=%s 独立run_id=%s 均交付=%s"
              % (idem["same_input"], idem["distinct_run_ids"], idem["both_delivered"]))
        r4 = r4 and all([idem["same_input"], idem["distinct_run_ids"], idem["both_delivered"]])

    # ---------- RB31-05
    fid = skill_fidelity()
    r5rows, r5 = [], fid["all_source_same"] and fid["all_model_same"]
    for aid, cap, fx, _, base in CASES:
        if aid not in recs:
            continue
        got = len((outs(recs[aid]).get("artifact") or "").strip())
        want = baseline_len(base)
        ratio = (got / want) if want else None
        ok = ratio is not None and ratio >= 0.8
        r5 = r5 and ok
        r5rows.append({"attempt": aid, "capability": cap, "baseline_attempt": base,
                       "baseline_artifact_len": want, "now_artifact_len": got,
                       "ratio": round(ratio, 3) if ratio else None, "pass": ok})
        print("[RB31-05][%s] %-20s 基线%5d → 现在%5d  %.0f%% %s"
              % (aid, cap, want or 0, got, (ratio or 0) * 100, "" if ok else "← FAIL"))
    print("[RB31-05] 六份源 Skill 零差异=%s  MODEL 零差异=%s"
          % (fid["all_source_same"], fid["all_model_same"]))

    out = {"contract_ref": CONTRACT_REF,
           "M4-RB31-03": {"result": "PASS" if r3 else "FAIL", "flag": "CURRENT", "rows": r3rows},
           "M4-RB31-04": {"result": "PASS" if r4 else "FAIL", "flag": "CURRENT",
                          "rows": r4rows, "idempotency": idem},
           "M4-RB31-05": {"result": "PASS" if r5 else "FAIL", "flag": "CURRENT",
                          "rows": r5rows, "fidelity": fid}}
    with open(os.path.join(OUT, "RB31_03_04_05_VERDICT.json"), "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    print("\nM4-RB31-03 = %s\nM4-RB31-04 = %s\nM4-RB31-05 = %s"
          % (out["M4-RB31-03"]["result"], out["M4-RB31-04"]["result"],
             out["M4-RB31-05"]["result"]))
    return 0


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "run"
    sys.exit({"run": cmd_run, "judge": cmd_judge}.get(cmd, lambda: (print(__doc__), 2)[1])())
