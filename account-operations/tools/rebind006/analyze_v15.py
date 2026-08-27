#!/usr/bin/env python3
"""第 9 轮第 2 段跑完之后的确定性复算：真运行 vs 零模型预测。

这份脚本回答第 6 条要的五件事里的前三件：
  真实调用账      次数、tokens、传输失败与重试，逐组给
  误拒/真拒结果    v1.5 真跑下还有几例拒收、分别是哪几例、判读
  DD-1 真运行结论  补齐路上「骨架里的 POS 行会不会被照发回来」——
                   这是第 9 轮预检里**唯一**降级成推断的一步，只能靠真跑兑现

**不把 `workflow_status == "succeeded"` 写成任何验收项的 PASS。** 它只说明这一次
Dify 运行没崩。
"""
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(WT, "account-operations/tools/gate_v13"))
EV = os.path.join(WT, "account-operations/evidence")
OUT = os.path.join(EV, "ep32-formal-v15")

DIFY_DIRS = {"EP-06 保真": "ep06-runtime-fidelity-dify-v15",
             "EP-06b 行为": "ep06b-runtime-behavior-v15",
             "EP-07 纵向": "ep07-longitudinal-v15"}
AB_DIR = "ep08-module-ab-v15"


def _dify_rows(d):
    p = os.path.join(EV, d)
    rows = []
    if not os.path.isdir(p):
        return rows
    for f in sorted(os.listdir(p)):
        if not f.endswith(".json") or f.startswith("_"):
            continue
        rec = json.load(open(os.path.join(p, f), encoding="utf-8"))
        rb = rec.get("raw_response_body")
        if isinstance(rb, str):
            rb = json.loads(rb)
        data = (rb or {}).get("data") or {}
        out = data.get("outputs") or {}
        rows.append({
            "case": rec.get("case_id") or rec.get("step_id") or f[:-5],
            "file": f, "transport_failure_record": "transport_failure" in f,
            "http_status": rec.get("http_status"),
            "workflow_status": data.get("status"),
            "total_tokens": data.get("total_tokens") or 0,
            "transport_attempts": rec.get("transport_attempts"),
            "gate_path": out.get("gate_path"),
            "carry": out.get("cycle_state_carry"),
            "carry_reject_reason": json.loads(out.get("carry_reject_reason") or "[]"),
            "gate_report": json.loads(out.get("gate_report") or "{}"),
            "post_gate_report": json.loads(out.get("post_gate_report") or "{}"),
        })
    return rows


def _ab_rows():
    p = os.path.join(EV, AB_DIR)
    rows = []
    if not os.path.isdir(p):
        return rows
    for f in sorted(os.listdir(p)):
        if not f.endswith("__B.json"):
            continue
        rec = json.load(open(os.path.join(p, f), encoding="utf-8"))
        gt = rec.get("gate_trace") or {}
        d = (rec.get("draft_response") or {}).get("body") or {}
        r = (rec.get("repair_response") or {}).get("body") or {}
        rows.append({
            "case": rec["case_id"] + "__B", "file": f, "transport_failure_record": False,
            "http_status": rec.get("http_status"), "workflow_status": "n/a (直连镜像)",
            "total_tokens": ((d.get("usage") or {}).get("total_tokens") or 0)
                            + ((r.get("usage") or {}).get("total_tokens") or 0),
            "transport_attempts": None,
            "gate_path": gt.get("gate_path"), "carry": gt.get("cycle_state_carry"),
            "carry_reject_reason": [],
            "gate_report": json.loads(gt.get("gate_report") or "{}"),
            "post_gate_report": json.loads(gt.get("post_gate_report") or "{}"),
        })
    return rows


def main():
    groups = {k: _dify_rows(v) for k, v in DIFY_DIRS.items()}
    groups["EP-08 A/B · B 臂"] = _ab_rows()

    # ---------------- 调用账 ----------------
    ledger = {}
    for g, rows in groups.items():
        real = [r for r in rows if not r["transport_failure_record"]]
        retries = sum(max(0, len(r["transport_attempts"] or []) - 1) for r in real
                      if r["transport_attempts"])
        ledger[g] = {"runs": len(real), "tokens": sum(r["total_tokens"] for r in real),
                     "http_non_200": [r["case"] for r in real if r["http_status"] != 200],
                     "workflow_not_succeeded": [r["case"] for r in real
                                                if r["workflow_status"] not in
                                                ("succeeded", "n/a (直连镜像)")],
                     "transport_retry_attempts": retries,
                     "transport_failure_files": [r["file"] for r in rows
                                                 if r["transport_failure_record"]]}
    ledger["合计"] = {"runs": sum(v["runs"] for v in ledger.values()),
                      "tokens": sum(v["tokens"] for v in ledger.values())}

    # ---------------- 拒收 ----------------
    allrows = [r for rows in groups.values() for r in rows if not r["transport_failure_record"]]
    rejected = [r for r in allrows if r["carry"] == "REJECTED_KEEP_PREVIOUS"]
    rej_detail = []
    for r in rejected:
        pg = r["post_gate_report"]
        rej_detail.append({
            "case": r["case"], "gate_path": r["gate_path"],
            "reasons": r["carry_reject_reason"] or pg.get("carry_reject_reason") or [],
            "positions_dropped_after_draft": pg.get("positions_dropped_after_draft"),
            "positions_dropped_new": pg.get("positions_dropped_new"),
            "positions_introduced_by_gate": pg.get("positions_introduced_by_gate"),
            "positions_unaccounted": (pg.get("positions") or {}).get("positions_unaccounted"),
            "positions_fabricated": (pg.get("positions") or {}).get("positions_fabricated"),
            "stale_value_override": pg.get("stale_value_override"),
            "manifest_contradiction": pg.get("still_manifest_contradiction"),
        })

    # ---------------- DD-1 真运行结论 ----------------
    dd1 = {"repaired_runs": 0, "runs_with_skeleton_pos_line": 0,
           "skeleton_pos_all_reproduced": 0, "skeleton_pos_dropped": [],
           "runs_with_new_position_declared": 0, "new_positions_dropped": []}
    for r in allrows:
        if r["gate_path"] != "gate_repaired":
            continue
        dd1["repaired_runs"] += 1
        gr, pg = r["gate_report"], r["post_gate_report"]
        skel = gr.get("skeleton_position_ids") or []
        newp = gr.get("draft_new_position_ids") or []
        if skel:
            dd1["runs_with_skeleton_pos_line"] += 1
            dropped = pg.get("positions_dropped_after_draft") or []
            if dropped:
                dd1["skeleton_pos_dropped"].append({"case": r["case"], "dropped": dropped,
                                                    "skeleton": skel})
            else:
                dd1["skeleton_pos_all_reproduced"] += 1
        if newp:
            dd1["runs_with_new_position_declared"] += 1
            dn = pg.get("positions_dropped_new") or []
            if dn:
                dd1["new_positions_dropped"].append({"case": r["case"], "dropped_new": dn})
    dd1["verdict"] = ("真运行证实：骨架里的 POS 行全部被补齐节点照发回来，新增持续位零删除"
                      if not dd1["skeleton_pos_dropped"] and not dd1["new_positions_dropped"]
                      else "真运行**证伪**了预检的那条推断，见 skeleton_pos_dropped / new_positions_dropped")

    # ---------------- DD-2/3/4 复发 ----------------
    recur = {"stale_value_override": [], "manifest_contradiction": []}
    for r in allrows:
        pg = r["post_gate_report"]
        if pg.get("stale_value_override"):
            recur["stale_value_override"].append({"case": r["case"],
                                                  "hits": pg["stale_value_override"]})
        if pg.get("still_manifest_contradiction"):
            recur["manifest_contradiction"].append({"case": r["case"],
                                                    "hits": pg["still_manifest_contradiction"]})

    # ---------------- 与零模型预测对照 ----------------
    pred_path = os.path.join(EV, "ep28-rebind006-precheck/REPLAY_V15.json")
    pred = json.load(open(pred_path, encoding="utf-8")) if os.path.exists(pred_path) else []
    pred_rej = {p["case"] for p in pred if p.get("v15_carry") == "REJECTED_KEEP_PREVIOUS"}
    real_rej = {r["case"] for r in rejected}
    compare = {
        "预测拒收": sorted(pred_rej), "真实拒收": sorted(real_rej),
        "预测到且真的被拒": sorted(pred_rej & real_rej),
        "预测清除但真跑仍被拒": sorted(real_rej & {p["case"] for p in pred
                                                   if p.get("recorded", {}).get("carry")
                                                   == "REJECTED_KEEP_PREVIOUS"} - pred_rej),
        "真跑新增的拒收（预测里没有）": sorted(real_rej - pred_rej),
        "注": "预测是在第 8 轮的**旧草稿**上做的反事实；本轮是**新草稿**，"
              "模型输出本来就会变，因此逐例对齐只对 E07/E08 这类由输入决定的例有意义，"
              "整体只看量级与病理是否复发。",
    }

    rep = {"what": "第 9 轮第 2 段：候选 v1.5 真运行的确定性复算",
           "hard_rule": "`workflow_status == \"succeeded\"` 只说明这一次运行没崩，"
                        "**不是**任何验收项的 PASS 依据。",
           "call_ledger": ledger,
           "rejections": {"total": len(rejected), "detail": rej_detail},
           "DD1_real_run": dd1, "DD234_recurrence": recur,
           "vs_zero_model_prediction": compare,
           "groups": {g: [{"case": r["case"], "carry": r["carry"], "path": r["gate_path"],
                           "tokens": r["total_tokens"]} for r in rows]
                      for g, rows in groups.items()}}
    os.makedirs(OUT, exist_ok=True)
    json.dump(rep, io.open(os.path.join(OUT, "ANALYZE_V15.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    print(json.dumps({k: rep[k] for k in ("call_ledger", "DD1_real_run",
                                          "DD234_recurrence", "vs_zero_model_prediction")},
                     ensure_ascii=False, indent=2))
    print("\n拒收合计", len(rejected), [r["case"] for r in rejected])
    return 0


if __name__ == "__main__":
    sys.exit(main())
