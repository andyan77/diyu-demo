#!/usr/bin/env python3
"""E07 / E08 的拒收是不是**与补齐节点怎么写无关**——枚举证明，不靠假设。

DD-1 的修法在补齐路上依赖一条前提（补齐节点会照发骨架里的 `POS ::` 行），
所以「10 个误拒消失」只能是推断。但「两个真拒仍被拒收」不一定要跟着一起降级：
如果在**补齐节点所有可能的输出**下结论都一样，那这两例就是确定性的。

做法：把补齐节点终稿审计块里的持续位声明当成一个自由变量，取遍
  U = 输入侧位 ∪ 草稿声明位 ∪ {一个外来 id}
的**全部子集**（外来 id 用来覆盖「补齐节点凭空写了个别的位」这一支），
逐个跑一遍 v1.5 的 D-3 剥离 + `check_positions` + D-1 丢位计算，看拒收是否恒成立。
"""
import itertools
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(WT, "account-operations/tools/gate_v13"))
sys.path.insert(0, HERE)

import shared_checks as S                       # noqa: E402
from gate_main import main as gate_main         # noqa: E402
from corpus import load_all                     # noqa: E402

FOREIGN = "NEW:补齐节点凭空写的一个位"


def blocking_for(input_ids, draft_ids, final_ids):
    """复刻 post_gate v1.5 在 gate_repaired 路径上的持续位那一层。"""
    decls = [{"id": i, "status": "continued", "kind": None, "anchor": "", "is_new": False}
             for i in final_ids]
    gate_authored = [d["id"] for d in decls if d["id"] not in draft_ids]
    kept = [d for d in decls if d["id"] in draft_ids]
    kept_ids = {d["id"] for d in kept}
    unaccounted = [i for i in input_ids if i not in kept_ids]
    fabricated = [d["id"] for d in kept if not d["is_new"] and d["id"] not in input_ids]
    dropped = [i for i in draft_ids if i not in kept_ids and i not in gate_authored]
    reasons = []
    for k, v in (("unaccounted", unaccounted), ("fabricated", fabricated),
                 ("dropped", dropped), ("gate_authored", gate_authored)):
        if v:
            reasons.append(k)
    return bool(reasons), reasons


def main():
    rows = {r["case"]: r for r in load_all()}
    out = []
    for case in ("E07", "E08"):
        r = rows[case]
        gr = json.loads(gate_main(r["draft_raw"], r["manifest"],
                                  r["account_context"])["gate_report"])
        input_ids = (gr.get("positions") or {}).get("input_position_ids") or []
        draft_ids = gr.get("draft_declared_position_ids") or []
        universe = list(dict.fromkeys(list(input_ids) + list(draft_ids) + [FOREIGN]))
        total = always = 0
        counterexample = []
        for k in range(len(universe) + 1):
            for combo in itertools.combinations(universe, k):
                total += 1
                blk, why = blocking_for(input_ids, draft_ids, list(combo))
                if blk:
                    always += 1
                else:
                    counterexample.append(list(combo))
        out.append({"case": case, "input_position_ids": input_ids,
                    "draft_declared_position_ids": draft_ids,
                    "universe": universe,
                    "possible_repair_outputs_enumerated": total,
                    "rejected_in": always,
                    "counterexamples_where_it_would_pass": counterexample,
                    "invariant": not counterexample})
    rep = {"what": "E07 / E08：补齐节点任意输出下拒收是否恒成立（枚举，零模型）",
           "note": "枚举的是终稿审计块里持续位声明的**全部子集**，含『凭空写一个外来位』这一支。"
                   "其余拒收理由（泄漏、清单、G-4）在真实终稿上已单独重跑，均为 0，"
                   "所以持续位这一层就是这两例拒收的全部依据。",
           "rows": out,
           "all_invariant": all(x["invariant"] for x in out)}
    o = os.path.join(WT, "account-operations/evidence/ep28-rebind006-precheck")
    os.makedirs(o, exist_ok=True)
    json.dump(rep, open(os.path.join(o, "E07_E08_INVARIANCE.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    print(json.dumps(rep, ensure_ascii=False, indent=2))
    return 0 if rep["all_invariant"] else 1


if __name__ == "__main__":
    sys.exit(main())
