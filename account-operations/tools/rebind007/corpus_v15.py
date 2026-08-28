"""第 10 轮零模型重放的语料装载器 —— 语料换成**本轮 v1.5 真实运行落盘的草稿**。

本文件不发起任何模型调用。三个来源全部是 v1.5 正式取证批次的原始记录：

  行为 49 例   account-operations/evidence/ep06b-runtime-behavior-v15/B*.json
  纵向 N 步    account-operations/evidence/ep07-longitudinal-v15/E*.json
  保真 N 例    account-operations/evidence/ep06-runtime-fidelity-dify-v15/G*.json

另外保留第 9 轮语料（v14 记录，64 次运行）作**回归轴**：v1.5.1 的修法不得
让第 9 轮已经证明的结果倒退。回归轴直接复用 `rebind006.corpus`，不另抄一份。

字段来源逐个标注，缺什么就是 None，不猜、不补。
"""
import json
import os

WORKTREE = "/home/faye/diyu-demo-worktrees/m3-account-content-operator-v1"
EV = os.path.join(WORKTREE, "account-operations/evidence")
V15 = {
    "behavior": (os.path.join(EV, "ep06b-runtime-behavior-v15"), "B"),
    "longitudinal": (os.path.join(EV, "ep07-longitudinal-v15"), "E"),
    "fidelity": (os.path.join(EV, "ep06-runtime-fidelity-dify-v15"), "G"),
}


def _dify(path, source):
    d = json.load(open(path, encoding="utf-8"))
    rb = d["raw_response_body"]
    if isinstance(rb, str):
        rb = json.loads(rb)
    out = (rb.get("data") or {}).get("outputs") or {}
    wi = d.get("workflow_inputs") or {}
    return {
        "case": d.get("case_id") or d.get("step_id"),
        "source": source,
        "path": path,
        "account_context": wi.get("account_context") or "",
        "manifest": wi.get("loaded_references") or "",
        "draft_raw": out.get("draft_raw") or "",
        "final_body": out.get("operating_judgment") or "",
        "final_audit": None,          # Dify 载体没有把补齐后的审计块单独回传
        "repair_raw": None,           # 同上
        "gate_report": json.loads(out.get("gate_report") or "{}"),
        "post_gate_report": json.loads(out.get("post_gate_report") or "{}"),
        "gate_path": out.get("gate_path") or "",
        "carry": out.get("cycle_state_carry") or "",
        "carry_reject_reason": json.loads(out.get("carry_reject_reason") or "[]"),
    }


def load_v15():
    """本轮 v1.5 落盘记录。目录里有几份就装几份，**不等、不补、不猜**。"""
    rows = []
    for source, (d, prefix) in V15.items():
        if not os.path.isdir(d):
            continue
        for f in sorted(os.listdir(d)):
            if not f.endswith(".json") or not f.startswith(prefix):
                continue
            rows.append(_dify(os.path.join(d, f), os.path.basename(d)))
    return rows


def load_regression():
    """第 9 轮语料（v14 的 64 次运行），只作回归轴。"""
    import sys
    here = os.path.dirname(os.path.abspath(__file__))
    r6 = os.path.join(os.path.dirname(here), "rebind006")
    if r6 not in sys.path:
        sys.path.insert(0, r6)
    import corpus as c6
    return c6.load_all()


if __name__ == "__main__":
    from collections import Counter
    v = load_v15()
    print("v15 语料:", len(v), dict(Counter(x["source"] for x in v)))
    print("回归语料:", len(load_regression()))
