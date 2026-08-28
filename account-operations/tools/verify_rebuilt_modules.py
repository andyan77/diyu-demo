#!/usr/bin/env python3
"""第 9 轮第 0 段：重建的四个模块，逐项对着**已落盘的真实运行记录**证保真。

重建不能靠"我觉得原来就是这样"。这份脚本把每个模块的输出与第 8 轮真实记录做
逐字节比对，比不上就 FAIL。零模型调用。

  M-1 `manifest.build_refs`      对 71 次运行的 `loaded_references` 逐字节比对
  M-2 `ep06_runtime_fidelity_v2.CASES`  对 9 例的 context/user/参考开关逐字节比对，
                                  并做 5 轮跨轮一致性核对
  M-3 `create_m3_app.MODEL/FEATURES`    对 Console 读回的实时草稿逐字段比对
  M-4 `dify_client`              真实登录 + 读回草稿，报告实际传输路径
"""
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)

from manifest import build_refs                              # noqa: E402
from ep06_runtime_fidelity_v2 import CASES, SKILL_DIR, read   # noqa: E402
from create_m3_app import MODEL, FEATURES, TASK_ID, APP_ID    # noqa: E402

EV = os.path.join(WT, "account-operations/evidence")
FID_ROUNDS = ["ep06-runtime-fidelity-dify", "ep06-runtime-fidelity-dify-v11",
              "ep06-runtime-fidelity-dify-v12", "ep06-runtime-fidelity-dify-v13",
              "ep06-runtime-fidelity-dify-v14"]


def _records(d):
    out = {}
    p = os.path.join(EV, d)
    if not os.path.isdir(p):
        return out
    for f in sorted(os.listdir(p)):
        if not f.endswith(".json") or f.startswith("_") or "transport" in f:
            continue
        out[f[:-5]] = json.load(open(os.path.join(p, f), encoding="utf-8"))
    return out


def m1():
    fashion = read(os.path.join(SKILL_DIR, "references/fashion-and-market.md"))
    ok = bad = 0
    for d in ("ep06-runtime-fidelity-dify-v14", "ep06b-runtime-behavior-v14",
              "ep07-longitudinal-v14"):
        for name, rec in _records(d).items():
            want = (rec.get("workflow_inputs") or {}).get("loaded_references")
            if want is None:
                continue
            inc = "fashion-and-market.md: LOADED" in want
            ok += (build_refs(inc, fashion) == want)
            bad += (build_refs(inc, fashion) != want)
    return {"compared": ok + bad, "byte_identical": ok, "different": bad, "pass": bad == 0}


def m2():
    byid = {c["id"]: c for c in CASES}
    v14 = _records("ep06-runtime-fidelity-dify-v14")
    same = diff = 0
    for name, rec in v14.items():
        wi = rec["workflow_inputs"]
        c = byid.get(name)
        if (c and c["context"] == wi["account_context"] and c["user"] == wi["user_request"]
                and c["include_fashion_ref"] == ("fashion-and-market.md: LOADED"
                                                 in wi["loaded_references"])):
            same += 1
        else:
            diff += 1
    cross = {}
    for d in FID_ROUNDS:
        recs = _records(d)
        s = c2 = 0
        for name, rec in recs.items():
            wi = rec.get("workflow_inputs") or {}
            cc = byid.get(name)
            if not cc or "account_context" not in wi:
                c2 += 1
            elif cc["context"] == wi["account_context"] and cc["user"] == wi["user_request"]:
                s += 1
            else:
                c2 += 1
        cross[d] = {"matched": s, "mismatched_or_absent": c2}
    return {"cases": len(CASES), "byte_identical_vs_v14": same, "different": diff,
            "cross_round": cross, "anchor_rounds": len(FID_ROUNDS),
            "pass": diff == 0 and len(CASES) == 9
                    and all(v["matched"] == 9 for v in cross.values())}


def m3_m4():
    from dify_client import Console
    c = Console()
    st, draft = c.call("GET", f"/console/api/apps/{APP_ID}/workflows/draft")
    assert st == 200, (st, draft)
    live_feat = draft.get("features")
    llms = [n for n in draft["graph"]["nodes"] if n["data"]["type"] == "llm"]
    live_models = [n["data"]["model"] for n in llms]
    model_ok = all(m.get("provider") == MODEL["provider"] and m.get("name") == MODEL["name"]
                   and m.get("mode") == MODEL["mode"]
                   and m.get("completion_params") == MODEL["completion_params"]
                   for m in live_models)
    hits = c.find_app(TASK_ID)
    return {"transport": c.transport,
            "features_byte_identical": live_feat == FEATURES,
            "model_matches_all_llm_nodes": model_ok, "llm_nodes": len(llms),
            "live_draft_hash": str(draft.get("hash"))[:16],
            "task_app_found": len(hits) == 1, "app_id": APP_ID,
            "no_qwen_in_graph": not any("qwen" in json.dumps(m).lower() for m in live_models),
            "pass": bool(live_feat == FEATURES and model_ok and len(hits) == 1)}


def main():
    rep = {"what": "第 9 轮第 0 段：重建模块对已落盘真实记录的保真校验",
           "zero_model_calls": True,
           "M1_manifest_build_refs": m1(),
           "M2_ep06_cases": m2(),
           "M3_M4_bindings_and_client": m3_m4()}
    rep["all_pass"] = all(v["pass"] for k, v in rep.items() if isinstance(v, dict))
    out = os.path.join(EV, "ep29-module-rebuild")
    os.makedirs(out, exist_ok=True)
    json.dump(rep, io.open(os.path.join(out, "REBUILD_FIDELITY.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    print(json.dumps(rep, ensure_ascii=False, indent=2))
    return 0 if rep["all_pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
