#!/usr/bin/env python3
"""载体 v1.3 冒烟（探索性，不产生正式证据）：验证图能跑通、持续位链路通、无泄漏。

三例覆盖三种形态：带持续位清单、无持续位清单、以及上一轮 G-2 逃逸的那个场景。
"""
import json, os, sys, time, urllib.request, urllib.error
HERE = os.path.dirname(os.path.abspath(__file__)); SCRATCH = os.path.dirname(HERE)
WT = "/home/faye/diyu-demo-worktrees/m3-account-content-operator-v1"
SKILL_DIR = os.path.join(WT, "account-operations/skills/operating-one-account")
sys.path.insert(0, SCRATCH); sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(WT, "account-operations/tools/gate_v13"))
from manifest import build_refs  # noqa: E402

KEY = open(os.path.join(SCRATCH, "m3_app_key.txt"), encoding="utf-8").read().strip()
URL = "http://localhost/v1/workflows/run"


def run(inputs, user):
    req = urllib.request.Request(URL, data=json.dumps(
        {"inputs": inputs, "response_mode": "blocking", "user": user}).encode(),
        headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"}, method="POST")
    t = time.time()
    try:
        with urllib.request.urlopen(req, timeout=1200) as r:
            return json.loads(r.read().decode()), round(time.time() - t, 1)
    except urllib.error.HTTPError as e:
        return {"error": e.read().decode()}, round(time.time() - t, 1)


fashion = open(os.path.join(SKILL_DIR, "references/fashion-and-market.md"), encoding="utf-8").read()
e07 = json.load(open(os.path.join(WT, "account-operations/evidence/ep07-longitudinal-v12-g1fix/E07.json"), encoding="utf-8"))
g6 = json.load(open(os.path.join(WT, "account-operations/evidence/ep06-runtime-fidelity-dify-v12/G6-attachment-unloaded.json"), encoding="utf-8"))

POS = ('[{"id":"P-rhythm","kind":"regular","title":"每周三条节奏","since":"E01"},'
       '{"id":"P-fit","kind":"exploration","title":"上身效果验证","since":"E03"},'
       '{"id":"P-store","kind":"regular","title":"门店陈列栏目","since":"E02"}]')

ctx_with_pos = e07["workflow_inputs"]["account_context"].rstrip() + "\nstanding_positions: " + POS + "\n"

CASES = [
    ("S1-with-positions", {"account_context": ctx_with_pos,
                           "user_request": e07["workflow_inputs"]["user_request"],
                           "loaded_references": build_refs(True, fashion)}),
    ("S2-no-positions", {"account_context": g6["workflow_inputs"]["account_context"],
                         "user_request": g6["workflow_inputs"]["user_request"],
                         "loaded_references": build_refs(False, fashion)}),
]
for cid, inp in CASES:
    body, el = run(inp, f"m3-smoke-v13-{cid}")
    d = body.get("data", {}) if isinstance(body, dict) else {}
    o = d.get("outputs") or {}
    print(f"\n===== {cid}  {d.get('status')}  {el}s  tok={d.get('total_tokens')}")
    if not o:
        print("  ", json.dumps(body, ensure_ascii=False)[:600]); continue
    rep = json.loads(o.get("gate_report", "{}"))
    print("  gate:", o.get("gate_status"), "| carry:", o.get("cycle_state_carry"),
          "| gaps_closed:", o.get("gaps_closed"))
    print("  gate_version:", rep.get("gate_version"))
    p = rep.get("positions", {})
    print("  positions: in=", p.get("input_position_ids"), " declared=", p.get("declared_position_ids"))
    print("             unaccounted=", p.get("positions_unaccounted"),
          " fabricated=", p.get("positions_fabricated"),
          " bad_anchor=", p.get("positions_bad_anchor"))
    print("  stale_override:", rep.get("stale_value_override"))
    print("  triggers eff:", rep.get("triggers_effective"))
    print("  leaks:", rep.get("internal_leaks"))
    txt = o.get("operating_judgment", "")
    print("  final chars:", len(txt))
    print("  head:", txt[:180].replace("\n", " ⏎ "))
