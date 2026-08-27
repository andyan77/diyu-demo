#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""M4 AC-31 三次原缺陷精确重放 v0.1

task_id: V1-M4-CAPABILITY-SEAMS-RUNTIME-INTEGRATION-001
contract: V1_M4_EVIDENCE_COLLECTION_CONTRACT_v0.4.md §1.1 / §3 M4-RB31-01

**这个脚本证明什么**

把 FA-10 / FA-27 / FA-32 的**原始输入**（不改写、不补充、不挑选）以新的
Attempt ID 重放到修复后的已发布应用上，并以 `input_sha256 == 冻结值` 作为
「确实是同一输入」的机械证明。原始输入不相等即拒绝运行，不做近似重放。

**这个脚本不证明什么**

不判定用户正文写得好不好。只判定合同 §3 M4-RB31-01 的八个合取项里
可机械核验的部分，并把原始输出、node_trace 全量落盘供后续判定与审查。

用法：
  python3 decision-chain/workflows/DIYU_M4_AC31_REPLAY_v0.1.py run
  python3 decision-chain/workflows/DIYU_M4_AC31_REPLAY_v0.1.py judge
"""

import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
DC_WF = os.path.join(ROOT, "decision-chain", "workflows")
EVID = os.path.join(ROOT, "decision-chain", "evidence", "m4")
OUT = os.path.join(EVID, "rebase_ac31")
OLD_RUNS = os.path.join(EVID, "runs")

CONTRACT_REF = "V1_M4_EVIDENCE_COLLECTION_CONTRACT_v0.4.md"
TASK_CONTRACT_HASH = "a5735c319402056f3c8552da229c816324a8a4ce56f36e0d781924114d68b40a"
ENVIRONMENT = "本机 Docker Dify 1.16.1"


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


PUB = _load("m4pub", os.path.join(DC_WF, "DIYU_M4_PUBLISH_AND_REBIND_v0.1.py"))
FA = _load("m4fa", os.path.join(DC_WF, "DIYU_M4_FORMAL_ATTEMPT_v0.1.py"))
CV = _load("m4cv", os.path.join(DC_WF, "DIYU_M4_CLOSING_VERIFICATION_v0.1.py"))
FX = _load("m4fx", os.path.join(DC_WF, "DIYU_M4_DETERMINISTIC_PROBE_v0.1.py"))


def sha(s):
    return hashlib.sha256((s or "").encode("utf-8")).hexdigest()


def file_sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def git(*args):
    return subprocess.run(["git"] + list(args), cwd=ROOT, capture_output=True,
                          text=True).stdout.strip()


# 合同 §1.1 冻结重放表：新 Attempt → 被重放对象 → 输入正文来源
REPLAYS = [
    ("RB31-R10", "FA-10", "FX-M4-GOAL-COUNTERFACTUAL-A", "CONTENT_BRIEF", FX.GOAL_A),
    ("RB31-R27", "FA-27", "FX-M4-CTA-THREE/case_business_handoff", "CONTENT_BRIEF",
     CV.CTA_BUSINESS_HANDOFF),
    ("RB31-R32", "FA-32", "FX-M4-RETURN-PARSE-FAIL", "CONTENT_BRIEF", CV.RETURN_PARSE_FAIL),
]


def cmd_run():
    os.makedirs(OUT, exist_ok=True)

    # ---- 前置：输入同一性断言（合同 §3 M4-RB31-01 ①）
    frozen = {}
    for aid, old_id, fx_id, cap, payload in REPLAYS:
        old = json.load(open(os.path.join(OLD_RUNS, "%s.json" % old_id), encoding="utf-8"))
        want, got = old["input_sha256"], sha(payload)
        frozen[old_id] = {"want": want, "got": got, "same": want == got,
                          "old_file_sha256": file_sha(os.path.join(OLD_RUNS, "%s.json" % old_id))}
        print("[input] %s ← %s  %s" % (aid, old_id, "同一输入" if want == got else "**不是同一输入**"))
        if want != got:
            print("        冻结值 %s" % want)
            print("        现场值 %s" % got)
    if not all(v["same"] for v in frozen.values()):
        print("中止：输入不同一，重放无效。不做近似重放。")
        return 1

    c = PUB.Console()
    c.login()
    reb = json.load(open(os.path.join(EVID, "M4_DIFY_REBIND.json"), encoding="utf-8"))
    seam_app = reb["seam_app_id"]
    bindings = reb["bindings"]
    token = FA.ensure_api_key(c, seam_app)
    base = c.base

    rows = PUB.psql("SELECT workflow_id FROM apps WHERE id='%s';" % seam_app)
    seam_wf = rows[0] if rows else "UNKNOWN"
    candidate_commit = git("rev-parse", "HEAD")

    build = _load("m4build", os.path.join(DC_WF, "DIYU_M4_DSL_BUILD_v0.1.py"))
    model = build.MODEL

    index = []
    for aid, old_id, fx_id, cap, payload in REPLAYS:
        t0 = time.time()
        body = {
            "inputs": {
                "capability": cap,
                "entry": "",
                "capability_call": payload,
                "professional_input": payload,
                "example_reference_requested": "NO",
            },
            "response_mode": "blocking",
            "user": "m4-ac31-replay",
        }
        try:
            res = FA.service_call(base, token, "/v1/workflows/run", body)
            err = None
        except Exception as e:
            res, err = {}, str(e)[:600]
        run_id = ((res.get("data") or {}).get("id")) or res.get("workflow_run_id") or ""
        outputs = ((res.get("data") or {}).get("outputs") or {})
        rec = {
            "attempt_id": aid,
            "attempt_kind": "REBASE_FORMAL",
            "replays": old_id,
            "fixture_id": fx_id,
            "capability": cap,
            "entry_requested": "(由确定性充分性规则推导)",
            "contract_ref": CONTRACT_REF,
            "current_task_contract_hash": TASK_CONTRACT_HASH,
            "candidate_commit": candidate_commit,
            "environment": ENVIRONMENT,
            "dify_app_id": seam_app,
            "dify_workflow_id": seam_wf,
            "provider_bindings": bindings,
            "model_provider": model["provider"],
            "model_name": model["name"],
            "completion_params": model["completion_params"],
            "input_sha256": sha(payload),
            "frozen_input_sha256": frozen[old_id]["want"],
            "input_identical_to_frozen": True,
            "run_id": run_id,
            "elapsed_s": round(time.time() - t0, 2),
            "error": err,
            "raw_response": res,
            "node_trace": FA.node_trace(c, seam_app, run_id) if run_id else [],
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        }
        p = os.path.join(OUT, "%s.json" % aid)
        with open(p, "w", encoding="utf-8") as fh:
            json.dump(rec, fh, ensure_ascii=False, indent=2)
        ud = (outputs.get("user_delivery") or "").strip()
        print("[%s] ← %s  status=%-18s user_delivery=%d字  outcome=%s  recovery=%s" % (
            aid, old_id, (res.get("data") or {}).get("status", "ERR" if err else "?"),
            len(ud), outputs.get("delivery_outcome", "-"), outputs.get("recovery_used", "-")))
        if err:
            print("      ERR: %s" % err[:200])
        index.append({"attempt_id": aid, "replays": old_id, "run_id": run_id,
                      "path": os.path.relpath(p, ROOT)})

    # ---- 事后：原失败记录未被修改（合同 §3 M4-RB31-01 ⑦）
    untouched = {}
    for old_id, v in frozen.items():
        now = file_sha(os.path.join(OLD_RUNS, "%s.json" % old_id))
        untouched[old_id] = {"before": v["old_file_sha256"], "after": now,
                             "unchanged": now == v["old_file_sha256"]}
        print("[原记录] %s %s" % (old_id, "未被修改" if now == v["old_file_sha256"] else "**被修改**"))

    with open(os.path.join(OUT, "REPLAY_INDEX.json"), "w", encoding="utf-8") as fh:
        json.dump({"contract_ref": CONTRACT_REF,
                   "current_task_contract_hash": TASK_CONTRACT_HASH,
                   "candidate_commit": candidate_commit,
                   "dify_app_id": seam_app, "dify_workflow_id": seam_wf,
                   "input_identity": frozen,
                   "old_records_unchanged": untouched,
                   "attempts": index}, fh, ensure_ascii=False, indent=2)
    print("evidence -> %s" % os.path.relpath(OUT, ROOT))
    return 0


# ------------------------------------------------------------------ 判定
BACKREF = ["即上方", "即以上", "同上", "同上文", "上方即", "上文即",
           "见上文", "如上所述", "内容同上", "本区块与", "与上方", "与上文", "与以上"]

LEAK = ["PARSE_FAIL", "PARSE_FAILED", "SEAM_COMPLETENESS_GUARD", "STRUCTURE_MISSING",
        "BACKREF_COLLAPSED", "BELOW_MIN", "NOT_APPLICABLE", "NOT_VERIFIED", "STALE",
        "artifact_status", "user_delivery_status", "returns_status", "local_block",
        "needs_projection", "projection_source", "delivery_outcome", "recovery_used",
        "seam_trace", "call_hash", "binding_record", "node_trace", "workflow_run_id",
        "system prompt", "系统提示词", "Judge", "判定器", "sha256", "commit",
        "---M4_ARTIFACT---", "---M4_USER---", "---M4_RETURNS---"]

PLACEHOLDER = ["见内部产出", "详见内部", "无内容", "N/A", "TODO", "待补", "略"]


def outputs_of(rec):
    return ((rec.get("raw_response") or {}).get("data") or {}).get("outputs") or {}


def cmd_judge():
    idx = json.load(open(os.path.join(OUT, "REPLAY_INDEX.json"), encoding="utf-8"))
    conj = []
    per = {}
    for aid, old_id, fx_id, cap, _ in REPLAYS:
        rec = json.load(open(os.path.join(OUT, "%s.json" % aid), encoding="utf-8"))
        o = outputs_of(rec)
        ud = (o.get("user_delivery") or "")
        art = (o.get("artifact") or "")
        raw = json.dumps(o, ensure_ascii=False)
        trace = rec.get("node_trace") or []
        titles = [str(t.get("title") or t.get("node_id") or "") for t in trace]

        c1 = rec["input_sha256"] == rec["frozen_input_sha256"]
        c2 = len(ud.strip()) > 0
        # ③ 不是占位符、不是纯回指、不含内部状态码
        c3 = (not any(p in ud for p in PLACEHOLDER)
              and not any(l in ud for l in LEAK)
              and not (len(ud.strip()) < 80 and any(b in ud for b in BACKREF)))
        c4 = (len(ud.strip()) > 0
              and not ud.strip().startswith("{") and not ud.strip().startswith("["))
        c5 = len(art.strip()) > 0 or len((o.get("artifact_raw") or "").strip()) > 0
        c6 = all(rec.get(k) for k in ("model_provider", "model_name", "dify_app_id",
                                      "dify_workflow_id", "candidate_commit"))
        c7 = idx["old_records_unchanged"][old_id]["unchanged"]
        c8 = sum(1 for t in titles if "skill" in t.lower() or "专业" in t) <= 1

        row = {"attempt": aid, "replays": old_id,
               "①同一输入": c1, "②非空": c2, "③非占位非回指非状态码": c3,
               "④可直接阅读": c4, "⑤内部Artifact保留": c5, "⑥绑定完整": c6,
               "⑦原记录未改": c7, "⑧未重跑生产链": c8,
               "user_delivery_len": len(ud.strip()), "artifact_len": len(art.strip()),
               "delivery_outcome": o.get("delivery_outcome", ""),
               "recovery_used": o.get("recovery_used", "")}
        per[aid] = row
        conj.append(all([c1, c2, c3, c4, c5, c6, c7, c8]))
        print("[%s] %s" % (aid, " ".join("%s=%s" % (k, "T" if v else "F")
                                         for k, v in row.items() if isinstance(v, bool))))
        print("        user_delivery=%d字 artifact=%d字 outcome=%s recovery=%s"
              % (row["user_delivery_len"], row["artifact_len"],
                 row["delivery_outcome"], row["recovery_used"]))

    result = "PASS" if all(conj) else "FAIL"
    print("\nM4-RB31-01 = %s" % result)
    with open(os.path.join(OUT, "RB31_01_VERDICT.json"), "w", encoding="utf-8") as fh:
        json.dump({"criterion": "M4-RB31-01", "contract_ref": CONTRACT_REF,
                   "result": result, "flag": "CURRENT", "per_attempt": per}, fh,
                  ensure_ascii=False, indent=2)
    return 0


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "run"
    sys.exit({"run": cmd_run, "judge": cmd_judge}.get(cmd, lambda: (print(__doc__), 2)[1])())
