"""补齐节点对骨架的复现保真度：第 8 轮真实记录，零模型。

为什么要量这个：DD-1 的修法是把「模型本轮自己声明过的持续位」补进补齐骨架
（`required_audit_lines`）。修法能不能奏效，取决于补齐节点会不会把骨架里的
`POS ::` 行照原样发回来。这一点**不能靠声明**，只能看它在第 8 轮真实记录里
对**已有**骨架行的复现率——那是同一个节点、同一个系统提示词、同一个模型。

口径：
  骨架 POS id      = gate_report.positions.input_position_ids（v1.4.2 骨架只装输入侧位）
  终稿审计 POS id  = post_gate_report.positions.declared_position_ids
                     ∪ post_gate_report.positions_introduced_by_gate
                     （复检把「不在草稿里」的行剥进 introduced_by_gate，两者合起来
                       才是补齐节点实际发回来的那一组）
只统计 gate_path == "gate_repaired" 且补齐节点重发了审计块的运行；没重发审计块的
单列一类，不混进保真度分母。
"""
import json
import sys

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from corpus import load_all  # noqa: E402


def main():
    rows = load_all()
    stats = {"repaired": 0, "no_audit_after_repair": 0,
             "skeleton_pos_reproduced": 0, "skeleton_pos_missing": 0,
             "detail": [], "no_skeleton_pos_line": 0}
    for r in rows:
        if r["gate_path"] != "gate_repaired":
            continue
        stats["repaired"] += 1
        pg = r["post_gate_report"]
        if pg.get("audit_missing_after_repair"):
            stats["no_audit_after_repair"] += 1
            continue
        skel = list((r["gate_report"].get("positions") or {}).get("input_position_ids") or [])
        final_ids = set((pg.get("positions") or {}).get("declared_position_ids") or [])
        final_ids |= set(pg.get("positions_introduced_by_gate") or [])
        if not skel:
            stats["no_skeleton_pos_line"] += 1
            continue
        miss = [i for i in skel if i not in final_ids]
        if miss:
            stats["skeleton_pos_missing"] += 1
        else:
            stats["skeleton_pos_reproduced"] += 1
        stats["detail"].append({"case": r["case"], "skeleton_pos": skel,
                                "final_audit_pos": sorted(final_ids),
                                "missing_from_final": miss})
    n = stats["skeleton_pos_reproduced"] + stats["skeleton_pos_missing"]
    stats["denominator_with_skeleton_pos_line"] = n
    stats["reproduction_rate"] = (f"{stats['skeleton_pos_reproduced']}/{n}" if n else "0/0")
    print(json.dumps(stats, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
