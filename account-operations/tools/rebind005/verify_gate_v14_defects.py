#!/usr/bin/env python3
"""第 8 轮：本轮**自己的修法**在真实运行上暴露出来的三条缺陷，逐条机械坐实。

第 7 轮的教训是：修法本身也会有缺陷，而且是同一类缺陷——挡掉判据**要求**的行为。
所以这一轮不等判定者来说，先把自己的修法放回 61 例真实语料上量一遍。

DD-1  补齐骨架里根本没有 `POS ::` 行 ⇒ 补齐节点按「一行不多、一行不少」把模型
      本轮声明的新增位删掉 ⇒ D-1 开火拒收。D-1 是**真检测**，但它检测出来的是
      闸门自己的构造缺陷；Founder 第 1 条要的是「不得静默丢失」，现在是
      「不再静默，但仍然丢失，而且赔上整份交付」。
DD-2  G-4 v2 读槽位时把解释性从句里的数字当成了权威值：
      `actual_capacity: 1 条（本周实际，低于基线 3 条）` 被读成 3 条/周。
DD-3  G-4 v2 把「本周必须让掉另外 2 条」读成了当前速率主张。

三条都会拒收合格交付 —— 与 D-2 同一病灶，只是换了位置。
"""
import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
GATE = os.path.join(WT, "account-operations/tools/gate_v13")
OUT = os.path.join(WT, "account-operations/evidence/ep26-gate-v14-defects")
sys.path.insert(0, GATE)
import shared_checks as sc                                             # noqa: E402
from gate_main import main as gate                                      # noqa: E402

DIRS = ("account-operations/evidence/ep06b-runtime-behavior-v14/B*.json",
        "account-operations/evidence/ep07-longitudinal-v14/E*.json")


def load():
    for pat in DIRS:
        for p in sorted(glob.glob(os.path.join(WT, pat))):
            if "/_" in p:
                continue
            d = json.load(open(p, encoding="utf-8"))
            o = ((d.get("raw_response_body") or {}).get("data") or {}).get("outputs") or {}
            if o:
                yield os.path.basename(p)[:-5], d, o


def dd1():
    """骨架里没有 POS 行 ⇒ 新增位必被删。逐例复算首闸的骨架，不引二手结论。"""
    rows = []
    for name, d, o in load():
        pg = json.loads(o["post_gate_report"])
        dropped = pg["positions"].get("positions_dropped_after_draft") or []
        if not dropped:
            continue
        wi = d["workflow_inputs"]
        g = gate(o["draft_raw"], wi.get("loaded_references", ""), wi["account_context"])
        skeleton = g["required_audit_lines"]
        pos_lines_in_skeleton = [l for l in skeleton.splitlines() if l.startswith("POS ::")]
        rows.append({
            "case": name,
            "dropped": dropped,
            "dropped_were_new": pg["positions"].get("positions_dropped_new") or [],
            "skeleton_pos_lines": pos_lines_in_skeleton,
            "skeleton_has_no_pos_line": not pos_lines_in_skeleton,
            "carry": o.get("cycle_state_carry"),
        })
    return rows


SLOT_PROBES = [
    ("actual_capacity", "1 条（本周实际，低于基线 3 条）", 1,
     "权威值是 1 条；括号里的 3 条是解释性对照，不是权威值"),
    ("actual_capacity", "3 条/周", 3, "对照：干净写法解析正确"),
    ("expected_publish_count", "每天 3 条（用户口径）", 3, "对照：等价换算基数解析正确"),
]


def dd2():
    """槽位解析：第一个数量才是权威值，解释性从句里的不是。"""
    rows = []
    for slot, raw, want, note in SLOT_PROBES:
        got = [q for q in sc._qty_scan(raw) if q["unit"]]
        first = got[0]["n"] if got else None
        rows.append({"slot": slot, "slot_text": raw, "expected_authority": want,
                     "parsed_as": [{"n": q["n"], "unit": q["unit"],
                                    "period_source": q["period_source"]} for q in got],
                     "authority_taken": first,
                     "correct": first == want, "note": note})
    return rows


def dd3():
    """正文侧：本轮真实命中里，逐条判是不是真的『用旧值压当轮输入』。"""
    rows = []
    for name, d, o in load():
        gr = json.loads(o["gate_report"])
        for h in gr.get("stale_value_override") or []:
            rows.append({"case": name, "hit": h})
    return rows


def rejection_ledger():
    """12 例拒收逐条归因：去掉本轮新加的两个计数器之后，还剩什么理由。

    这一步的意义是把「拒收」拆成「该拒的」与「被我自己的修法误拒的」。
    第 7 轮 G-4 的教训就是没做这一步：只看命中数，不看命中的是谁。
    """
    rows = []
    for name, d, o in load():
        if o.get("cycle_state_carry") == "ACCEPTABLE_AS_NEW_BASELINE":
            continue
        pg = json.loads(o["post_gate_report"])
        pos = pg["positions"]
        others = {
            "hard": bool(pg.get("hard_fail_reasons")),
            "input_contradiction": bool(pg.get("still_input_contradiction")),
            "manifest_contradiction": bool(pg.get("still_manifest_contradiction")),
            "leaks": bool(pg.get("still_leaks")),
            "unaccounted": bool(pos.get("positions_unaccounted")),
            "fabricated": bool(pos.get("positions_fabricated")),
            "stale_override_G4": bool(pg.get("stale_value_override")),
        }
        rows.append({"case": name, "reasons_other_than_DD1": [k for k, v in others.items() if v],
                     "rejected_only_by_DD1": not any(others.values())})
    return rows


def main():
    d1, d2, d3 = dd1(), dd2(), dd3()
    ledger = rejection_ledger()
    # 正面结果也一并量出来，好的坏的一起报
    newpos = explore = 0
    total = 0
    for name, d, o in load():
        total += 1
        gr = json.loads(o["gate_report"])
        if gr["positions"].get("new_positions"):
            newpos += 1
        if gr.get("structural_exploration_positions"):
            explore += 1

    rep = {
        "what": "第 8 轮：本轮修法自身在真实运行上的缺陷与效果，两侧都量",
        "corpus": {"samples": total, "source": list(DIRS)},
        "positive": {
            "新增持续位命中例数": f"{newpos}/{total}（第 7 轮 12/61）",
            "结构性探索位例数": f"{explore}/{total}（第 7 轮 11/61）",
            "G-4 阻断命中": f"{len(d3)}/{total}（第 7 轮 12/61，其中 11 例为误报）",
            "D-3 真检测": "E07（模型零 POS 行、补齐代写）、E08（模型写错 id、补齐改成正确 id）；"
                          "两例在 v1.3 下都会被放行并承载为新基线",
        },
        "DD-1": {
            "claim": "补齐骨架不含任何 `POS ::` 行 ⇒ 补齐节点按「一行不多、一行不少」删掉模型"
                     "本轮声明的新增位 ⇒ D-1 开火，整份交付被拒收",
            "root_cause": "gate_main 的 required_audit_lines 只按**输入侧**持续位生成，"
                          "模型本轮新声明的位从不进骨架",
            "count": len(d1),
            "skeleton_has_no_pos_line_at_all": sum(1 for r in d1 if r["skeleton_has_no_pos_line"]),
            "skeleton_has_pos_line_but_not_the_new_one":
                sum(1 for r in d1 if not r["skeleton_has_no_pos_line"]),
            "split_note": "输入侧没有持续位时骨架里一行 POS 都没有；有输入位时骨架只有输入那一行，"
                          "模型自己新声明的那一位同样不在骨架里。两种形态的后果一样。",
            "rows": d1,
            "founder_directive_1_status": "未满足。第 1 条要的是「新增持续位不得在补齐链路中"
                                          "静默丢失」；现在是不再静默，但仍然丢失，而且赔上整份交付。",
        },
        "DD-2": {
            "claim": "G-4 v2 读槽位时把解释性从句里的数字当成权威值",
            "count": sum(1 for r in d2 if not r["correct"]),
            "rows": d2,
        },
        "DD-3": {
            "claim": "G-4 v2 正文侧仍有把非速率句读成速率主张的情形",
            "hits": d3,
        },
        "DD-4": {
            "claim": "清单矛盾检查（v1.2 起就有，非本轮改动）把「参考资料用了、但缺某个账号事实」"
                     "读成「声称参考未加载」",
            "case": "B07-1-traffic-full-facts",
            "sentence": "面料/成分已登记（来源=商品负责人周宁），但没有试穿事实或试穿素材，必须限制上身类主张",
            "why_false": "缺的是试穿素材（账号事实缺口），不是参考文件；"
                         "SKILL.md O-6 恰好**要求**把这两类缺口分开写，这句话正是照做的",
        },
        "rejection_ledger": {
            "total_rejected": len(ledger),
            "rejected_only_by_DD1": sum(1 for r in ledger if r["rejected_only_by_DD1"]),
            "rows": ledger,
            "verdict": "12 例拒收里 10 例是误拒（8 例纯 DD-1、1 例 DD-2/DD-3 的 G-4 误报、"
                       "1 例 DD-4 的清单误报），真正该拒的只有 E07 与 E08 两例 D-3 真检测。"
                       "第 7 轮是 7 例拒收里 6 例误拒。**误拒数从 6 涨到 10。**",
        },
    }
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "GATE_V14_DEFECTS.json"), "w", encoding="utf-8") as f:
        json.dump(rep, f, ensure_ascii=False, indent=2)
    print(json.dumps({"positive": rep["positive"],
                      "DD-1": {k: v for k, v in rep["DD-1"].items() if k != "rows"},
                      "DD-1 例": [r["case"] for r in d1],
                      "DD-2": [r for r in d2 if not r["correct"]],
                      "DD-3": d3}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
