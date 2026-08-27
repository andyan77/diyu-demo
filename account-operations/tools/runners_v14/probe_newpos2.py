#!/usr/bin/env python3
"""定向探针二：拿**第 7 轮确实声明过新增位的那几例**重跑，看机制回没回来。

探针一用的是纵向 E01。那一步走的是「无内容任务」诊断路径，本来就可以不产生任何持续位，
所以它零命中不能证明什么 —— 探针本身选错了样本。这一版换成 v13 里
`new_positions` 非空的三例，输入逐字节复用，一次并发跑完。

判据：三例里**至少一例**声明出 `新增·*`，就算机制已修回；三例全零，就是没修回。
探针不产生任何验收结论。
"""
import json, os, sys, time, urllib.request
from concurrent.futures import ThreadPoolExecutor

WT = "/home/faye/diyu-demo-worktrees/m3-account-content-operator-v1"
SCRATCH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KEY = open(os.path.join(SCRATCH, "m3_app_key.txt"), encoding="utf-8").read().strip()
SRC = os.path.join(WT, "account-operations/evidence/ep06b-runtime-behavior-v13")
CASES = ["B02-1-no-matrix", "B03-2-objective-02", "B03-5-objective-05"]


def one(cid):
    inp = json.load(open(os.path.join(SRC, cid + ".json"), encoding="utf-8"))["workflow_inputs"]
    req = urllib.request.Request(
        "http://localhost/v1/workflows/run",
        data=json.dumps({"inputs": inp, "response_mode": "blocking",
                         "user": f"m3-probe2-{cid}"}).encode(),
        headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"})
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=1200) as r:
            body = json.loads(r.read().decode())
    except Exception as e:                                          # noqa: BLE001
        return {"case": cid, "error": str(e)[:200]}
    d = body.get("data", {}); o = d.get("outputs") or {}
    gr = json.loads(o["gate_report"]) if o.get("gate_report") else {}
    p = gr.get("positions", {})
    raw = o.get("draft_raw") or ""
    pos = [l.strip()[:150] for l in raw.splitlines() if l.strip().startswith("POS")]
    return {"case": cid, "status": d.get("status"), "sec": round(time.time() - t0, 1),
            "new_positions": p.get("new_positions"), "declared": p.get("declared_position_ids"),
            "struct_explore": gr.get("structural_exploration_positions"),
            "pos_lines": pos}


with ThreadPoolExecutor(max_workers=3) as ex:
    res = list(ex.map(one, CASES))
prev = {"B02-1-no-matrix": True, "B03-2-objective-02": True, "B03-5-objective-05": True}
for r in res:
    print(json.dumps(r, ensure_ascii=False)[:700])
    print()
hit = sum(1 for r in res if r.get("new_positions"))
print(f"三例中 {hit} 例声明了新增持续位（第 7 轮同三例：3/3）")
print("探针结论：", "机制已修回" if hit else "仍然写不出新增位 —— 不要开整批")
sys.exit(0 if hit else 1)
