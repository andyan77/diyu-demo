#!/usr/bin/env python3
"""第 10 轮零模型重放：v1.5（本轮已跑的载体）对 v1.5.1（B15-DIR-02 修法）的差分。

**本文件不发起任何模型调用。** 两条语料轴：

  主轴  本轮 v1.5 正式取证批次落盘的真实草稿（行为 49 + 纵向 N + 保真 N）
  回归轴 第 9 轮语料（v14 的 64 次运行）—— 修法不得让已证明的结果倒退

重放的两条路（A 直发路=确定性/已观察，B 补齐路=集合代数反事实/推断）与第 9 轮
`rebind006/replay_v15.py` 完全同一套，直接复用它的 `replay_one`，不另抄一份判读逻辑。

主轴的 `recorded` 是**本轮真跑出来的 v1.5 结果**，因此主轴上的差分就是
「同一批草稿、只换闸门代码」的纯净对照：草稿是模型输出，闸门是后处理。
"""
import json
import os
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(WT, "account-operations/tools/gate_v13"))
sys.path.insert(0, os.path.join(WT, "account-operations/tools/rebind006"))
sys.path.insert(0, HERE)

from replay_v15 import replay_one                      # noqa: E402
from corpus_v15 import load_v15, load_regression       # noqa: E402


def _run(rows, axis):
    usable, skipped = [], []
    for r in rows:
        if not (r["draft_raw"] or "").strip():
            # 传输失败的记录不是草稿，不能当语料。如实登记，不静默丢弃。
            skipped.append(r["case"])
            continue
        usable.append(r)
    out = [dict(replay_one(r), axis=axis) for r in usable]
    return out, skipped


def summarize(rows, skipped, axis):
    old_rej = [x["case"] for x in rows if x["recorded"]["carry"] == "REJECTED_KEEP_PREVIOUS"]
    new_rej = [x["case"] for x in rows if x["v15_carry"] == "REJECTED_KEEP_PREVIOUS"]
    return {
        "axis": axis,
        "samples": len(rows),
        "skipped_no_draft": skipped,
        "as_run_rejected": {"n": len(old_rej), "cases": old_rej},
        "v151_rejected": {"n": len(new_rej), "cases": new_rej},
        "cleared": [c for c in old_rej if c not in new_rej],
        "newly_rejected": [c for c in new_rej if c not in old_rej],
        "path_shift": [
            {"case": x["case"], "as_run": x["recorded"]["gate_path"], "v151": x["v15_gate_path"]}
            for x in rows if x["recorded"]["gate_path"] and x["recorded"]["gate_path"] != x["v15_gate_path"]
        ],
        "grades": dict(Counter(x["evidence_grade"].split("（")[0] for x in rows)),
    }


def main():
    v15, sk15 = _run(load_v15(), "本轮 v1.5 草稿（主轴）")
    reg, skrg = _run(load_regression(), "第 9 轮 v14 语料（回归轴）")
    rep = {"main": summarize(v15, sk15, "本轮 v1.5 草稿（主轴）"),
           "regression": summarize(reg, skrg, "第 9 轮 v14 语料（回归轴）")}
    print(json.dumps(rep, ensure_ascii=False, indent=2))
    return rep, v15 + reg


if __name__ == "__main__":
    rep, rows = main()
    out = os.path.join(WT, "account-operations/evidence/ep33-rebind007-v151")
    os.makedirs(out, exist_ok=True)
    json.dump(rep, open(os.path.join(out, "REPLAY_V151_SUMMARY.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    json.dump(rows, open(os.path.join(out, "REPLAY_V151_ROWS.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    print("已落盘", out)
