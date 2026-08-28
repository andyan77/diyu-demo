"""第 9 轮零模型重放的统一语料装载器。

三个来源，全部是**已落盘的真实运行记录**，本文件不发起任何模型调用：
  行为 49 例   account-operations/evidence/ep06b-runtime-behavior-v14/B*.json
  纵向 12 步   account-operations/evidence/ep07-longitudinal-v14/E*.json
  A/B B 臂 3 例 account-operations/evidence/ep08-module-ab-v14/FX-*__B.json

统一成同一个记录形状，字段来源逐个标注，缺什么就是 None，不猜、不补。
"""
import json
import os

WORKTREE = "/home/faye/diyu-demo-worktrees/m3-account-content-operator-v1"
EV = os.path.join(WORKTREE, "account-operations/evidence")
BEHAVIOR = os.path.join(EV, "ep06b-runtime-behavior-v14")
LONGI = os.path.join(EV, "ep07-longitudinal-v14")
AB = os.path.join(EV, "ep08-module-ab-v14")


def _dify(path):
    d = json.load(open(path, encoding="utf-8"))
    rb = d["raw_response_body"]
    if isinstance(rb, str):
        rb = json.loads(rb)
    out = (rb.get("data") or {}).get("outputs") or {}
    wi = d.get("workflow_inputs") or {}
    return {
        "case": d.get("case_id") or d.get("step_id"),
        "source": os.path.basename(os.path.dirname(path)),
        "path": path,
        "account_context": wi.get("account_context") or "",
        "manifest": wi.get("loaded_references") or "",
        "draft_raw": out.get("draft_raw") or "",
        "final_body": out.get("operating_judgment") or "",
        "final_audit": None,              # Dify 载体没有把补齐后的审计块单独回传
        "repair_raw": None,               # 同上
        "gate_report": json.loads(out.get("gate_report") or "{}"),
        "post_gate_report": json.loads(out.get("post_gate_report") or "{}"),
        "gate_path": out.get("gate_path") or "",
        "carry": out.get("cycle_state_carry") or "",
        "carry_reject_reason": json.loads(out.get("carry_reject_reason") or "[]"),
    }


def _ab(path, holdouts):
    d = json.load(open(path, encoding="utf-8"))
    gt = d["gate_trace"]
    h = holdouts[d["case_id"]]
    return {
        "case": d["case_id"] + "__B",
        "source": "ep08-module-ab-v14",
        "path": path,
        "account_context": h["account_context"],
        "manifest": d["manifest"],
        "draft_raw": gt.get("draft_raw") or "",
        "final_body": d.get("answer_text") or "",
        "final_audit": None,              # 由 repair_raw 现场切出来，见 replay
        "repair_raw": gt.get("repair_raw") or "",
        "gate_report": json.loads(gt.get("gate_report") or "{}"),
        "post_gate_report": json.loads(gt.get("post_gate_report") or "{}"),
        "gate_path": gt.get("gate_path") or "",
        "carry": gt.get("cycle_state_carry") or "",
        "carry_reject_reason": [],
    }


def load_all():
    rows = []
    for f in sorted(os.listdir(BEHAVIOR)):
        if f.startswith("B") and f.endswith(".json"):
            rows.append(_dify(os.path.join(BEHAVIOR, f)))
    for f in sorted(os.listdir(LONGI)):
        if f.startswith("E") and f.endswith(".json"):
            rows.append(_dify(os.path.join(LONGI, f)))
    ah = json.load(open(os.path.join(AB, "_arms_and_holdouts_v5.json"), encoding="utf-8"))
    holdouts = {h["fixture_id"]: h for h in ah["holdouts"]}
    for f in sorted(os.listdir(AB)):
        if f.endswith("__B.json"):
            rows.append(_ab(os.path.join(AB, f), holdouts))
    return rows


if __name__ == "__main__":
    rs = load_all()
    from collections import Counter
    print("总样本", len(rs), Counter(r["source"] for r in rs))
    print("有 repair_raw 的", sum(1 for r in rs if r["repair_raw"]))
    print("gate_path 分布", Counter(r["gate_path"] for r in rs))
    print("carry 分布", Counter(r["carry"] for r in rs))
