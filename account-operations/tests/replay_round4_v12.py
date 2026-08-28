#!/usr/bin/env python3
"""把 v1.2 闸门重放到第 4 轮 70 次真实运行的原稿上（只读，不产生新调用）。

目的有两个，必须分清：
  1. **必须命中**：G6（零交付）、E07（自报=否但输入有三条冲突反馈）、B08-P（裸标签）；
  2. **误伤普查**：最低产出门、输入槽位矛盾这两条会不会在其余 67 例上乱开枪。
v1.1 的原稿本来就带方括号标签、用的是 <<TRIGGERS>> 而不是 <<AUDIT>>，
所以泄漏与审计块两项在旧数据上必然全红——那是预期，不算误伤。
"""
import json, glob, os, sys, re
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))), "tools/gate_v12"))
from gate_main import main as gate

WT = "/home/faye/diyu-demo-worktrees/m3-account-content-operator-v1"
DIRS = ["account-operations/evidence/ep06-runtime-fidelity-dify-v11",
        "account-operations/evidence/ep06b-runtime-behavior-v11-run2",
        "account-operations/evidence/ep07-longitudinal-v11-run2"]
MAN = ("<<REFERENCE_MANIFEST>>\nreferences/fashion-and-market.md: %s\n"
       "references/six-skill-methods.md: NOT_LOADED\n<<END_REFERENCE_MANIFEST>>")

rows = []
for d in DIRS:
    for p in sorted(glob.glob(os.path.join(WT, d, "*.json"))):
        if os.path.basename(p).startswith("_"):
            continue
        r = json.load(open(p, encoding="utf-8"))
        o = (r.get("raw_response_body", {}).get("data", {}) or {}).get("outputs", {}) or {}
        draft = o.get("draft_raw", "") or ""
        ctx = r["workflow_inputs"]["account_context"]
        man = MAN % ("LOADED" if r.get("include_fashion_ref", True) else "NOT_LOADED")
        g = gate(draft, man, ctx)
        rep = json.loads(g["gate_report"])
        rows.append((os.path.basename(p)[:-5], rep, g))

def n(rep, k): return len(rep.get(k, []) or [])

print(f"{'case':36s} {'status':22s} min contra leak cont     conflict")
for name, rep, g in rows:
    mo = "Y" if any("最低实质产出" in x or "实质句段" in x or "去掉谈参考" in x
                    for x in rep["hard_fail_reasons"]) else "."
    print(f"{name:36s} {rep['gate_status'][:22]:22s} {mo}   "
          f"{n(rep,'input_contradiction'):5d} {n(rep,'internal_leaks'):4d} "
          f"{rep['continuity']['status'][:9]:9s} "
          f"{str(rep['triggers_computed_from_input']['conflict'])}")

print()
minout = [x[0] for x in rows if any("最低实质产出" in y or "实质句段" in y or "去掉谈参考" in y
                                    for y in x[1]["hard_fail_reasons"])]
contra = [(x[0], x[1]["input_contradiction"]) for x in rows if x[1]["input_contradiction"]]
leaks0 = [x[0] for x in rows if not x[1]["internal_leaks"]]
print("总计", len(rows), "例")
print("最低产出门命中：", minout, " ← 期望只有 G6")
print("输入槽位矛盾命中：")
for c, v in contra:
    print("   ", c, "->", v[0][:110])
print("零泄漏（旧数据里理应极少）：", leaks0)
