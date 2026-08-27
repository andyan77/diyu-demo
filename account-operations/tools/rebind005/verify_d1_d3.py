#!/usr/bin/env python3
"""D-1 与 D-3：在**第 7 轮的真实运行记录**上，证明旧码全绿、新码开火。

两条缺陷都只关乎两个 id 集合的比对，而这两个集合在记录里是齐的：
  草稿侧 = `gate_report.positions.declared_position_ids`（首闸自己解析出来的）
  最终侧 = `post_gate_report.positions.declared_position_ids`（复检自己解析出来的）

复检节点的输入（final_audit）没有单独落盘，所以这里做一次**机械重建**：
按最终侧那份 id 清单，逐条配上草稿 POS 行里那句锚点，拼回审计块。
重建到底忠不忠实，不靠我说——**先用旧码跑一遍，逐字段比对记录里的 positions**。
对得上，重建才算数；对不上就报错退出，不往下走。
"""
import json
import os
import re
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
GATE = os.path.join(WT, "account-operations/tools/gate_v13")
OUT = os.path.join(WT, "account-operations/evidence/ep22-rebind005-g4")
LONG = os.path.join(WT, "account-operations/evidence/ep07-longitudinal-v13")
sys.path.insert(0, GATE)
import post_gate_main as new_pg                                        # noqa: E402
import shared_checks as sc                                             # noqa: E402

# 旧码从 git 取，不手抄
_OLD = tempfile.mkdtemp(prefix="pgv13_")
for f in ("shared_checks.py", "post_gate_main.py"):
    src = subprocess.run(["git", "-C", WT, "show",
                          f"HEAD:account-operations/tools/gate_v13/{f}"],
                         capture_output=True, text=True, check=True).stdout
    open(os.path.join(_OLD, f), "w", encoding="utf-8").write(src)
sys.path.insert(0, _OLD)
_saved = {k: v for k, v in sys.modules.items() if k in ("shared_checks", "post_gate_main")}
for k in list(_saved):
    del sys.modules[k]
old_pg = __import__("post_gate_main")
assert "positions_dropped_after_draft" not in open(
    os.path.join(_OLD, "post_gate_main.py"), encoding="utf-8").read(), "取到的不是旧码"
sys.modules.update(_saved)


def rebuild_audit(gr, pgr, final_body, draft_raw):
    """按最终侧的 id 清单重建审计块。锚点优先用草稿 POS 行里那句，
    找不到就退回在最终正文里搜同 id 的原句；两者都没有就留空（会被计为坏锚点，如实）。"""
    lines = [";".join(f"{cn}={'是' if gr['triggers_effective'].get(k) else '否'}"
                      for k, (cn, _) in sc.TRIGGER_ITEMS.items())]
    for item, anchor in (gr.get("audit_anchors") or {}).items():
        if sc._norm(anchor) and sc._norm(anchor) in sc._norm(final_body):
            lines.append(f"{item} :: {anchor}")
    # 锚点只能从 `draft_raw` 里逐字取——v1.3 的 gate_report 没有 draft_pos_lines 这个字段，
    # 拿不到就拼不出能解析的 POS 行，重建会自己失真。同 id 多次出现时取最后一次
    # （模型常先草拟再定稿，最后那一条才是它交出来的）。
    draft_anchor = {}
    for raw in re.findall(r"^\s*POS\s*::\s*(.+)$", draft_raw or "", flags=re.M):
        parts = [x.strip() for x in re.split(r"\s*::\s*", raw) if x.strip()]
        if len(parts) >= 3 and sc._norm(parts[2]) in sc._norm(final_body):
            draft_anchor[parts[0]] = (parts[1], " :: ".join(parts[2:]))
    pos = pgr["positions"]
    status_of = {}
    for i in pos.get("continued", []):
        status_of[i] = "继续"
    for i in pos.get("disposed", []):
        status_of[i] = "处置"
    for n in pos.get("new_positions", []):
        status_of[n["id"]] = "新增·探索" if n.get("kind") == "exploration" else "新增·常规"
    for pid in pos["declared_position_ids"]:
        st, anchor = draft_anchor.get(pid, (status_of.get(pid, "继续"), ""))
        lines.append(f"POS :: {pid} :: {status_of.get(pid, st)} :: {anchor}")
    return "<<AUDIT>>\n" + "\n".join(lines) + "\n<<END_AUDIT>>"


def derive_draft_fields(gr):
    """新码要读的三个字段，从**同一份记录**里机械推出来，不新造事实。"""
    p = gr["positions"]
    return {"draft_declared_position_ids": list(p["declared_position_ids"]),
            "draft_new_position_ids": [n["id"] for n in p.get("new_positions", [])]}


CASES = {
    "E04": ("D-1 · 模型声明的新探索位在补齐后消失，三个计数器全 []",
            "positions_dropped_after_draft"),
    "E12": ("D-3 · 模型没写审计块，补齐节点替它写出 POS 行，unaccounted 由 1 变 0",
            "positions_introduced_by_gate"),
}

results = []
for step, (what, key) in CASES.items():
    d = json.load(open(os.path.join(LONG, f"{step}.json"), encoding="utf-8"))
    o = ((d["raw_response_body"]).get("data") or {})["outputs"]
    gr, pgr = json.loads(o["gate_report"]), json.loads(o["post_gate_report"])
    ac = d["workflow_inputs"]["account_context"]
    final_body = re.sub(r"\n\n（系统说明）.*$", "", o["operating_judgment"], flags=re.S)
    audit = rebuild_audit(gr, pgr, final_body, o.get("draft_raw") or "")

    old_out = old_pg.main(final_body, "", json.dumps(gr, ensure_ascii=False),
                          ac, audit, o["gate_path"])
    old_pos = json.loads(old_out["positions_final"])
    fields = ("declared_position_ids", "positions_unaccounted", "positions_fabricated",
              "positions_duplicated", "blocking")
    fidelity = {f: (old_pos.get(f) == pgr["positions"].get(f)) for f in fields}

    gr_new = dict(gr); gr_new.update(derive_draft_fields(gr))
    new_out = new_pg.main(final_body, "", json.dumps(gr_new, ensure_ascii=False),
                          ac, audit, o["gate_path"])
    new_pos = json.loads(new_out["positions_final"])
    new_rep = json.loads(new_out["post_gate_report"])

    results.append({
        "step": step, "what": what,
        "reconstruction_matches_record": fidelity,
        "reconstruction_faithful": all(fidelity.values()),
        "recorded_v13": {"declared": pgr["positions"]["declared_position_ids"],
                         "unaccounted": pgr["positions"]["positions_unaccounted"],
                         "fabricated": pgr["positions"]["positions_fabricated"],
                         "blocking": pgr["positions"]["blocking"],
                         "carry": pgr["cycle_state_carry"]},
        "new_v14": {"dropped_after_draft": new_pos.get("positions_dropped_after_draft"),
                    "dropped_new": new_pos.get("positions_dropped_new"),
                    "introduced_by_gate": new_pos.get("positions_introduced_by_gate"),
                    "blocking": new_pos["blocking"],
                    "carry": new_out["cycle_state_carry"],
                    "reasons": json.loads(new_out["carry_reject_reason"])},
        "defect_now_caught": bool(new_rep["positions"].get(key)),
    })

report = {
    "what": "D-1 / D-3 在第 7 轮真实运行记录上的旧码—新码对照",
    "method": "复检输入按记录机械重建；重建的忠实性先由旧码复现记录里的 positions 逐字段证明，"
              "对不上就不算数。旧码从 git HEAD 取，不手抄。",
    "cases": results,
    "all_reconstructions_faithful": all(r["reconstruction_faithful"] for r in results),
    "all_defects_caught": all(r["defect_now_caught"] for r in results),
}
os.makedirs(OUT, exist_ok=True)
json.dump(report, open(os.path.join(OUT, "D1_D3_OLD_VS_NEW.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=2)
print(json.dumps(report, ensure_ascii=False, indent=2)[:3500])
sys.exit(0 if report["all_reconstructions_faithful"] and report["all_defects_caught"] else 1)
