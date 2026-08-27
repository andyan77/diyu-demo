#!/usr/bin/env python3
"""对纵向判定者报出的三条缺陷做机械复核。**只读已冻结证据，不改判据、不重跑。**

判定者报的是他从交付正文与系统记录里读出的现象；这份脚本把每一条还原成
可复算的字段级证据，让第三方不必采信判定者、也不必采信执行侧。

三条各自的性质不同，结论里分开写：
  D-1 / D-3  实现没做到它自己冻结的判据（REBIND_004 §2.1 明写这两件不该发生）
  D-2        判据本身写得过宽（§2.3 逐字冻结了主语锚正则），改它属于事后改判据
"""
import json, os, re, sys

WT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(WT, "account-operations/tools/gate_v13"))
import shared_checks as S                                          # noqa: E402

EV = os.path.join(WT, "account-operations/evidence/ep07-longitudinal-v13")
OUT = os.path.join(WT, "account-operations/evidence/ep19-gate-v13-defects")


def step(sid):
    d = json.load(open(os.path.join(EV, f"{sid}.json"), encoding="utf-8"))
    o = d["raw_response_body"]["data"]["outputs"]

    def j(k):
        v = o.get(k)
        return json.loads(v) if isinstance(v, str) and v.strip().startswith(("{", "[")) else v
    return d, o, j


def d1():
    """E04：模型声明了第二个持续位，补齐后消失，无任何字段记录这次删除。"""
    rows = []
    for i in range(1, 13):
        sid = f"E{i:02d}"
        d, o, j = step(sid)
        a = (j("gate_report") or {})["positions"].get("declared_position_ids") or []
        b = ((j("post_gate_report") or {}).get("positions") or {}).get("declared_position_ids") or []
        lost = sorted(set(a) - set(b))
        if lost:
            rows.append({"step": sid, "gate_declared": a, "post_gate_declared": b,
                         "lost_between_gate_and_repair": lost,
                         "positions_unaccounted_at_gate":
                             (j("gate_report"))["positions"].get("positions_unaccounted"),
                         "projection_positions_unaccounted": d["projection"]["positions_unaccounted"],
                         "projection_declared_new": d["projection"]["declared_new"],
                         "prose_still_carries_it": "一件多穿" in (o.get("operating_judgment") or "")})
    return {
        "claim": "模型声明的新持续位可以在补齐环节被删掉，而三处计数器全为空",
        "confirmed": bool(rows),
        "occurrences": rows,
        "why_counters_stay_empty":
            "positions_unaccounted 的定义是「输入里有、声明里没有的 id」。"
            "本轮新声明的位不在输入里，被删掉之后它既不在输入也不在声明，"
            "因此不进任何差集 —— 计数器在定义上就看不见这类丢失。",
        "which_frozen_text_it_violates":
            "REBIND_004 §2.1：「positions_unaccounted[] ... 它非空即阻断，"
            "因此不会再出现『字段全程为空而内容全丢』这种事——空与不空这次真的有区别。」"
            "本例证明该断言对**本轮新增的位**不成立。",
    }


def d3():
    """E12：模型整个没写审计块，首闸正确阻断，补齐节点替它写了 POS 行。"""
    d, o, j = step("E12")
    gr, pg = j("gate_report"), j("post_gate_report")
    return {
        "claim": "补齐节点可以代模型写出 POS 行，从而替它满足连续性判据",
        "confirmed": (gr.get("audit_block_missing") is True
                      and not (gr["positions"].get("declared_position_ids") or [])
                      and bool((pg.get("positions") or {}).get("declared_position_ids"))),
        "gate_audit_block_missing": gr.get("audit_block_missing"),
        "gate_declared": gr["positions"].get("declared_position_ids"),
        "gate_positions_unaccounted": gr["positions"].get("positions_unaccounted"),
        "gate_blocking": gr["positions"].get("blocking"),
        "post_gate_declared": (pg.get("positions") or {}).get("declared_position_ids"),
        "blanket_introduced_by_gate": pg.get("blanket_introduced_by_gate"),
        "why_the_existing_guard_misses_it":
            "blanket_introduced_by_gate 只盯「其余保持不变」这一类概括句，"
            "不盯补齐节点代写的 POS 机器行。同一个病走了另一扇门。",
        "which_frozen_text_it_violates":
            "REBIND_004 §2.1：「判据能被闸门自己满足，就对模型没有约束力。」",
    }


def d2():
    """E06：expected_publish_count 的主语锚含裸词「目标」，在经营散文里到处命中。"""
    d, o, j = step("E06")
    body = o.get("draft_raw") or o.get("operating_judgment") or ""
    pat = S.QTY_SUBJECTS["expected_publish_count"]
    hits = []
    for s in S._segments(body):
        m = re.search(pat, s)
        if not m:
            continue
        hits.append({"anchor_word": m.group(0),
                     "segment": s.strip()[:120],
                     "has_now_marker": bool(re.search(S.NOW_MARKER, s)),
                     "mentions_publishing": bool(re.search(r"发|条内容|条视频|更新|publish", s))})
    fired = (j("gate_report") or {}).get("stale_value_override")
    return {
        "claim": "主语锚里的裸词「目标」使旧值覆盖检查在无发布量主张的句子上命中",
        "confirmed": bool(fired),
        "subject_anchor_regex": pat,
        "segments_matching_anchor": len(hits),
        "segments_matching_anchor_without_any_publishing_word":
            sum(1 for h in hits if not h["mentions_publishing"]),
        "examples": hits[:5],
        "what_actually_fired": fired,
        "consequence": "E06 整份交付被拒收（carry_blocking=true），"
                       "该步独有的三项安排在 E07–E12 永久消失。",
        "why_this_one_is_different":
            "D-1/D-3 是实现没做到自己冻结的判据，修它不改判据。"
            "D-2 相反：§2.3 把主语锚正则**逐字冻结**了，收窄它就是在看到结果之后改判据，"
            "按 A2 会使本轮 G-4 相关取证降为探索级。因此不在本轮自行改动。",
    }


def main():
    report = {
        "what": "对纵向判定者三条缺陷报告的机械复核",
        "scope": "只读已冻结证据；未改任何判据，未重跑任何取证",
        "source_of_claims": "M3_ECC_LONGITUDINAL_001_VERDICT_V13_v1.0.md（独立判定者）",
        "D-1_new_position_dropped_by_repair": d1(),
        "D-3_repair_authors_the_pos_line": d3(),
        "D-2_stale_override_false_positive": d2(),
    }
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "GATE_V13_DEFECTS_VERIFIED.json"), "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    for k in ("D-1_new_position_dropped_by_repair", "D-3_repair_authors_the_pos_line",
              "D-2_stale_override_false_positive"):
        print(f"  {k}: confirmed={report[k]['confirmed']}")


if __name__ == "__main__":
    main()
