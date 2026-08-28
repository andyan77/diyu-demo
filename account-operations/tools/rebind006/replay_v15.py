#!/usr/bin/env python3
"""第 9 轮零模型重放：v1.4.2（HEAD 基线）对 v1.5（本轮修法）在同一批真实记录上的差分。

**本文件不发起任何模型调用。** 语料是第 8 轮已落盘的真实运行：
行为 49 例 + 纵向 12 步 + A/B B 臂 3 例，共 64 次运行。

重放分两条路，路本身由 v1.5 的第一道闸门决定，不是执行侧挑的：

  A 直发路（`needs_fix == "no"`）
    装配确定性返回原稿、复检在原稿正文与原稿审计块上跑。整条链**没有模型参与**，
    因此重放结果是**完全确定性**的，等级=已观察。

  B 补齐路（`needs_fix == "yes"`）
    中间隔着一个 LLM 补齐节点，零模型重放拿不到它的新输出。
    这里**不伪造正文**，只对「持续位」这一层做集合代数反事实：
      新骨架 = 输入侧位 ∪ 模型草稿已声明位
      前提（唯一一条）：补齐节点把骨架里的 `POS ::` 行照发回来
      ⇒ 终稿声明集 = 新骨架 ⇒ 剥掉代写行后 decls = 草稿声明集
      ⇒ dropped = 草稿声明集 − 新骨架 = ∅（由构造恒成立）
         gate_authored = unaccounted = 输入位 − 草稿声明位
    前提不是凭空假设，它在第 8 轮同一批记录上量过（见 measure_repair_fidelity.py）：
    必填项骨架行 22/22 次全数复现、0 行丢失；骨架里出现过 `POS ::` 行的 3 次也 3/3 复现。
    即便如此，这一支的等级只能是**推断**，不是已观察——正式取证仍需真跑一次。

  另外三类判据（G-4 旧值压输入、参考清单矛盾、内部字段泄漏）是 `(输入, 正文)` 的
  纯函数，**两条路都直接在真实终稿正文上重跑**，不经过任何反事实，等级=已观察。
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(WT, "account-operations/tools/gate_v13"))
sys.path.insert(0, HERE)

import shared_checks as S                      # noqa: E402
from gate_main import main as gate_main        # noqa: E402
from assemble_main import main as assemble_main  # noqa: E402
from post_gate_main import main as post_gate_main  # noqa: E402
from corpus import load_all                    # noqa: E402


def replay_one(r):
    g = gate_main(r["draft_raw"], r["manifest"], r["account_context"])
    gr = json.loads(g["gate_report"])
    slots = S._parse_slots(r["account_context"])

    out = {
        "case": r["case"], "source": r["source"],
        "recorded": {
            "gate_status": r["gate_report"].get("gate_status"),
            "gate_path": r["gate_path"],
            "carry": r["carry"],
            "carry_reject_reason": r["carry_reject_reason"]
                                   or (r["post_gate_report"].get("carry_reject_reason") or []),
        },
        "v15_gate_status": gr["gate_status"],
        "skeleton_position_ids": gr.get("skeleton_position_ids") or [],
        "draft_declared_position_ids": gr.get("draft_declared_position_ids") or [],
        "draft_new_position_ids": gr.get("draft_new_position_ids") or [],
        "input_position_ids": (gr.get("positions") or {}).get("input_position_ids") or [],
    }

    # ---- 三类纯函数判据：直接在真实终稿正文上重跑（完全确定性）----
    fb = r["final_body"] or ""
    fb_r, _, _ = S.render_body(fb)
    out["final_body_recheck"] = {
        "stale_value_override": S.check_stale_value_override(slots, fb_r)[0],
        "manifest_contradiction": S.check_manifest(r["manifest"], fb_r, {})[2],
        "internal_leaks": S.check_leaks(fb_r),
        "input_contradiction": S.check_input_contradiction(slots, fb_r)[0],
    }

    if g["needs_fix"] == "no":
        # ---- A 直发路：整条链零模型，结果是**真的**跑出来的 ----
        a = assemble_main(g["body"], "", g["needs_fix"], g["gate_status"], g["draft_audit"])
        pg = json.loads(post_gate_main(a["final_text"], r["manifest"], g["gate_report"],
                                       r["account_context"], a["final_audit"],
                                       a["path"])["post_gate_report"])
        out["路"] = "A 直发路（确定性重放）"
        out["evidence_grade"] = "已观察"
        out["v15_gate_path"] = a["path"]
        out["v15_carry"] = pg["cycle_state_carry"]
        out["v15_reject_reason"] = pg["carry_reject_reason"]
        out["v15_positions"] = {
            "dropped": pg["positions_dropped_after_draft"],
            "dropped_new": pg["positions_dropped_new"],
            "introduced_by_gate": pg["positions_introduced_by_gate"],
            "unaccounted": pg["positions"]["positions_unaccounted"],
            "fabricated": pg["positions"]["positions_fabricated"],
        }
        return out

    # ---- B 补齐路：只对持续位做集合代数反事实 ----
    skel = out["skeleton_position_ids"]
    draft_ids = out["draft_declared_position_ids"]
    input_ids = out["input_position_ids"]
    dropped = [i for i in draft_ids if i not in skel]                 # 恒为 []
    gate_authored = [i for i in skel if i not in draft_ids]
    unaccounted = [i for i in input_ids if i not in draft_ids]
    decls, _bad = S.parse_positions_declaration(gr.get("draft_pos_lines") or [])
    fabricated = [d["id"] for d in decls if not d["is_new"] and d["id"] not in input_ids]

    reasons = []
    if unaccounted:
        reasons.append(("unaccounted", unaccounted))
    if fabricated:
        reasons.append(("fabricated", fabricated))
    if dropped:
        reasons.append(("dropped(D-1)", dropped))
    if gate_authored:
        reasons.append(("gate_authored(D-3)", gate_authored))
    if out["final_body_recheck"]["stale_value_override"]:
        reasons.append(("stale_override(G-4)", out["final_body_recheck"]["stale_value_override"]))
    if out["final_body_recheck"]["manifest_contradiction"]:
        reasons.append(("manifest_contradiction",
                        out["final_body_recheck"]["manifest_contradiction"]))
    if out["final_body_recheck"]["internal_leaks"]:
        reasons.append(("leaks", out["final_body_recheck"]["internal_leaks"]))
    if out["final_body_recheck"]["input_contradiction"]:
        reasons.append(("input_contradiction",
                        out["final_body_recheck"]["input_contradiction"]))

    out["路"] = "B 补齐路（持续位为集合代数反事实，其余在真实终稿上重跑）"
    out["evidence_grade"] = "推断（前提：补齐节点复现骨架 POS 行；第 8 轮实测 3/3、必填项行 22/22）"
    out["v15_gate_path"] = "gate_repaired"
    out["v15_carry"] = "REJECTED_KEEP_PREVIOUS" if reasons else "ACCEPTABLE_AS_NEW_BASELINE"
    out["v15_reject_reason"] = [f"{k}: {v}" for k, v in reasons]
    out["v15_positions"] = {"dropped": dropped, "dropped_new": [],
                            "introduced_by_gate": gate_authored,
                            "unaccounted": unaccounted, "fabricated": fabricated}
    return out


def main():
    rows = [replay_one(r) for r in load_all()]
    old_rej = [x["case"] for x in rows if x["recorded"]["carry"] == "REJECTED_KEEP_PREVIOUS"]
    new_rej = [x["case"] for x in rows if x["v15_carry"] == "REJECTED_KEEP_PREVIOUS"]
    print(json.dumps({
        "samples": len(rows),
        "v142_rejected": {"n": len(old_rej), "cases": old_rej},
        "v15_rejected": {"n": len(new_rej), "cases": new_rej},
        "cleared": [c for c in old_rej if c not in new_rej],
        "newly_rejected": [c for c in new_rej if c not in old_rej],
        "路分布": {"A": sum(1 for x in rows if x["路"].startswith("A")),
                   "B": sum(1 for x in rows if x["路"].startswith("B"))},
    }, ensure_ascii=False, indent=2))
    return rows


if __name__ == "__main__":
    rows = main()
    out = os.path.join(WT, "account-operations/evidence/ep28-rebind006-precheck")
    os.makedirs(out, exist_ok=True)
    json.dump(rows, open(os.path.join(out, "REPLAY_V15.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    print("已落盘", os.path.join(out, "REPLAY_V15.json"))
