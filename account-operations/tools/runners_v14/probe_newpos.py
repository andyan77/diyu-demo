#!/usr/bin/env python3
"""上线前的定向探针：基线为空时，模型还写不写得出新增持续位。

只跑一次调用，用第 7 轮 E01 那份逐字输入（那一步在 v1.3 上声明过 NEW:选品判断支柱验证）。
探针不产生任何验收结论，只回答一个是非题：勘误有没有把机制修回来。
写不出来就别开整批——上一次没先问这个问题，花掉了 40 多次调用。
"""
import json, os, sys, time, urllib.request

WT = "/home/faye/diyu-demo-worktrees/m3-account-content-operator-v1"
SCRATCH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KEY = open(os.path.join(SCRATCH, "m3_app_key.txt"), encoding="utf-8").read().strip()
SRC = os.path.join(WT, "account-operations/evidence/ep07-longitudinal-v13/E01.json")

inp = json.load(open(SRC, encoding="utf-8"))["workflow_inputs"]
req = urllib.request.Request(
    "http://localhost/v1/workflows/run",
    data=json.dumps({"inputs": inp, "response_mode": "blocking", "user": "m3-probe-newpos"}).encode(),
    headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"})
t0 = time.time()
with urllib.request.urlopen(req, timeout=1200) as r:
    body = json.loads(r.read().decode())
d = body.get("data", {})
o = d.get("outputs") or {}
print("status", d.get("status"), f"{time.time()-t0:.1f}s")
raw = o.get("draft_raw") or ""
i = raw.find("<<AUDIT>>")
print("--- 草稿审计块 ---")
print(raw[i:i+1400] if i >= 0 else "（没有审计块）")
print("--- /审计块 ---")
gr = json.loads(o["gate_report"]) if o.get("gate_report") else {}
p = gr.get("positions", {})
print("declared:", p.get("declared_position_ids"))
print("new_positions:", p.get("new_positions"))
print("structural_exploration_positions:", gr.get("structural_exploration_positions"))
print("bad_lines:", p.get("positions_bad_lines"), "| fabricated:", p.get("positions_fabricated"))
ok = bool(p.get("new_positions"))
print("\n探针结论：", "机制已修回（基线为空仍能新增持续位）" if ok else "仍然写不出新增位 —— 不要开整批")
sys.exit(0 if ok else 1)
