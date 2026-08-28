#!/usr/bin/env python3
"""E07→E08 连续性回归：用第 4 轮的**真实**文本，证明 v1.1 会丢、v1.2 不会丢。"""
import json, os, sys, re
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))), "tools/gate_v12"))
from gate_main import main as gate
from assemble_main import main as assemble
from post_gate_main import main as post_gate
from projection_v12 import project

WT = "/home/faye/diyu-demo-worktrees/m3-account-content-operator-v1"
D = os.path.join(WT, "account-operations/evidence/ep07-longitudinal-v11-run2")
MAN = ("<<REFERENCE_MANIFEST>>\nreferences/fashion-and-market.md: LOADED\n"
       "references/six-skill-methods.md: NOT_LOADED\n<<END_REFERENCE_MANIFEST>>")

e07 = json.load(open(os.path.join(D, "E07.json"), encoding="utf-8"))
ctx07 = e07["workflow_inputs"]["account_context"]
from shared_checks import _parse_slots
prev_standing = _parse_slots(ctx07)["standing_cycle_baseline"]
out07 = e07["final_answer_only_after_reasoning_strip"]

fails = []
# 1) v1.1 的实际行为：无条件覆盖 ⇒ P1/P2/P3 与节奏消失
v11_next = out07
lost = [o for o in ("P1", "P2", "P3") if o in ctx07 and o not in v11_next]
print("v1.1 无条件覆盖后丢失的对象:", lost)
if not lost:
    fails.append("前提不成立：E07 在 v1.1 下并没有丢对象，回归无意义")

# 2) v1.2：闸门判定 → carry → 投影
g = gate(out07, MAN, ctx07)
rep = json.loads(g["gate_report"])
asm = assemble(g["body"], "", g["needs_fix"], g["gate_status"], g["draft_audit"])
pg = post_gate(asm["final_text"], MAN, g["gate_report"], ctx07, asm["final_audit"], asm["path"])
carry = pg["cycle_state_carry"]
print("v1.2 gate_status =", rep["gate_status"], "| carry =", carry)
print("           conflict computed =", rep["triggers_computed_from_input"]["conflict"],
      "| self =", rep["triggers_self_reported"]["conflict"])
print("           input_contradiction =", rep["input_contradiction"])
if carry != "REJECTED_KEEP_PREVIOUS":
    fails.append(f"E07 这份零实质输出仍被判为可承载新基线：{carry}")

new_standing, prec = project(prev_standing, asm["final_text"], carry, ctx07)
print("投影记录:", json.dumps({k: prec[k] for k in
      ("mode", "continuity_status", "objects_before", "objects_not_restated",
       "chars_before", "chars_after")}, ensure_ascii=False))
if prec["mode"] != "KEPT_PREVIOUS":
    fails.append(f"投影模式应为 KEPT_PREVIOUS，实为 {prec['mode']}")
for o in ("P1", "P2", "P3"):
    if o not in new_standing:
        fails.append(f"E07→E08 之后 {o} 仍然从投影里消失了")

# 3) 反向：一份合格但只点名部分对象的输出，必须走 MERGED_KEEP_PRIOR 而不是整体覆盖
partial = "本周 P3 改为上身效果展示，其余安排我不动。"
ns2, pr2 = project(prev_standing, partial, "ACCEPTABLE_AS_NEW_BASELINE", ctx07)
print("只点名 P3 ->", pr2["mode"], "| 保留句数:", len(pr2.get("preserved_sentences") or []))
if pr2["mode"] != "MERGED_KEEP_PRIOR":
    fails.append(f"P1/P2 未被点名，应 MERGED_KEEP_PRIOR，实为 {pr2['mode']}")
for o in ("P1", "P2"):
    if o not in ns2:
        fails.append(f"合并后 {o} 仍然丢失")
if len(ns2) <= len(partial):
    fails.append("合并后长度没有增加，说明什么都没保留")

# 4) 全部点名 ⇒ 整体替换，不做多余保留（多算也是错）
full = "本周 P3 改为上身效果展示，P1、P2 继续延期，节奏不变。"
ns3, pr3 = project(prev_standing, full, "ACCEPTABLE_AS_NEW_BASELINE", ctx07)
print("全部点名 ->", pr3["mode"])
if pr3["mode"] != "REPLACED" or ns3 != full:
    fails.append(f"全部对象都被点名处置，应整体替换，实为 {pr3['mode']}")

print()
if fails:
    print("FAIL:")
    for f in fails: print("  -", f)
    sys.exit(1)
print("E07→E08 连续性回归通过")
