#!/usr/bin/env python3
"""误伤普查：把 v1.2 闸门重放到第 4 轮 70 次真实运行上，逐项量测阻断/触发率。

对抗审查提出的三条阻断级发现（explore 措辞 crosscheck 无极性、连续性误杀、
槽位非空判据太字面）改完之后，必须在同一批实测语料上量出数字才算改好。
"""
import json, glob, os, sys, re
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))), "tools/gate_v12"))
from gate_main import main as gate
from shared_checks import positive_hit, BODY_KEYWORDS, _parse_slots, _slot_filled

WT = "/home/faye/diyu-demo-worktrees/m3-account-content-operator-v1"
DIRS = ["ep06-runtime-fidelity-dify-v11", "ep06b-runtime-behavior-v11-run2",
        "ep07-longitudinal-v11-run2"]
MAN = ("<<REFERENCE_MANIFEST>>\nreferences/fashion-and-market.md: %s\n"
       "references/six-skill-methods.md: NOT_LOADED\n<<END_REFERENCE_MANIFEST>>")
THINK = re.compile(r"<think>.*?</think>", re.S)

rows = []
for d in DIRS:
    for p in sorted(glob.glob(os.path.join(WT, "account-operations/evidence", d, "*.json"))):
        if os.path.basename(p).startswith("_"):
            continue
        r = json.load(open(p, encoding="utf-8"))
        o = (r.get("raw_response_body", {}).get("data", {}) or {}).get("outputs", {}) or {}
        draft = o.get("draft_raw", "") or ""
        # 旧数据没有 <<AUDIT>> 块，四个自报值全是 None，会一律走"自报缺失 ⇒ fail-closed"，
        # 那是对 B-1 的**有意**设计，不是误伤。要量措辞 crosscheck 的误伤率，
        # 必须补一个"四项全报否"的审计块进去，再看还有多少被措辞判成触发。
        draft = draft + ("\n\n<<AUDIT>>\n探索提案=否;暂定锚点=否;冲突反馈=否;无内容任务=否\n"
                         "参考文件加载状态 :: __PROBE__\n<<END_AUDIT>>")
        ctx = r["workflow_inputs"]["account_context"]
        man = MAN % ("LOADED" if r.get("include_fashion_ref", True) else "NOT_LOADED")
        g = gate(draft, man, ctx)
        rep = json.loads(g["gate_report"])
        body = THINK.sub("", draft)
        rows.append((os.path.basename(p)[:-5], rep, body))

n = len(rows)
def cnt(f): return sum(1 for _, rep, _ in rows if f(rep))
explore_fc = [c for c, rep, _ in rows
              if any(x.startswith("探索提案:") for x in rep["trigger_fail_closed_blocks"])]
notask_fc = [c for c, rep, _ in rows
             if any(x.startswith("无内容任务:") for x in rep["trigger_fail_closed_blocks"])]
minout = [c for c, rep, _ in rows if any("最低实质产出" in x or "实质句段" in x or "去掉谈参考" in x
                                         for x in rep["hard_fail_reasons"])]
contra = [(c, rep["input_contradiction"]) for c, rep, _ in rows if rep["input_contradiction"]]
cont_merged = [c for c, rep, _ in rows if rep["continuity"]["status"] == "MERGED"]
print(f"总计 {n} 例\n")
print(f"探索 fail-closed 误触发：{len(explore_fc)}/{n}  {explore_fc}")
print(f"无内容任务 fail-closed：{len(notask_fc)}/{n}  {notask_fc}")
print(f"最低产出硬门：       {len(minout)}/{n}  {minout}   ← 期望只有 G6")
print(f"输入槽位矛盾：       {len(contra)}/{n}")
for c, v in contra:
    print(f"    {c}: {v[0][:100]}")
print(f"连续性判 MERGED（不阻断，投影逐字保留）：{len(cont_merged)}/{n}")
print(f"连续性判 OK：{cnt(lambda r: r['continuity']['status']=='OK')}/{n}  "
      f"BLANKET：{cnt(lambda r: r['continuity']['status']=='BLANKET_CARRY')}/{n}  "
      f"NO_BASELINE：{cnt(lambda r: r['continuity']['status']=='NO_BASELINE')}/{n}")
