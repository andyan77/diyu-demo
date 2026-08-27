#!/usr/bin/env python3
"""REBIND-007 预检：DD-5 修法在真实语料上两个方向都量，零模型。

对照组 = **本轮改动之前那一次提交** `fc63add` = v1.5（正式取证批次真正跑的那份闸门）。

五项：
  Q1 误报方向  两条语料轴 ×（草稿／终稿）两份正文，v1.5 命中几处、v1.5.1 命中几处，逐条判读
  Q2 漏检方向  探针取自真实运行原句、一字未改，只把槽位权威值机械改成必然冲突的值；
               再加一族「正文机械改写成带周期速率」的独立解析器探针（INDEP_RATE）。
               判据：**v1.5 能抓到的 v1.5.1 一个都不许放过**
  Q3 具名族    「本周期／本日期」这一族的正负例：负例（选择性量词）必须不响，
               正例（真速率主张）必须仍然响
  Q4 消融      每个新守卫单独关掉，误报轴或漏检轴必须变；两轴都不变 ⇒ 按 A5 删除
  Q5 真拒不变  E07／E08 两个真拒收在 v1.5.1 下仍然被拒
"""
import io
import json
import os
import re
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
GATE = os.path.join(WT, "account-operations/tools/gate_v13")
R6 = os.path.join(WT, "account-operations/tools/rebind006")
OUT = os.path.join(WT, "account-operations/evidence/ep33-rebind007-v151")
for p in (GATE, R6, HERE):
    sys.path.insert(0, p)

OLD_COMMIT = "fc63add"        # 第 0/1 段部署那次提交 = v1.5，本轮改动的直接前身

import shared_checks as new                                      # noqa: E402
from corpus_v15 import load_v15, load_regression                 # noqa: E402

_src = subprocess.run(
    ["git", "-C", WT, "show", f"{OLD_COMMIT}:account-operations/tools/gate_v13/shared_checks.py"],
    capture_output=True, text=True, check=True).stdout
_d = tempfile.mkdtemp(prefix="v15_")
io.open(os.path.join(_d, "shared_checks_v15.py"), "w", encoding="utf-8").write(_src)
sys.path.insert(0, _d)
import shared_checks_v15 as old                                  # noqa: E402
assert old.PERIOD_WORD.pattern.endswith("(天|日|周)"), "取到的对照组不是 v1.5 —— 对照无效"
assert new.PERIOD_WORD.pattern.endswith("(天|日|周)(?!期)"), "当前不是 v1.5.1"

# 本轮 2 例真实拒收的逐例判读（判读写在改判据之前，见 M3_STAGE2_V15_RUN_REPORT）
RULING = {
    ("B15-DIR-02-topic-to-brief", "G4"): "误报（DD-5：「本周期」被当成「本周」，选择性量词读成速率）",
}


def bodies(loader, axis):
    """(axis, case, tag, slots, manifest, body)。正文由 draft_raw 确定性重算，不取二手结论。"""
    out = []
    for r in loader():
        if not (r["draft_raw"] or "").strip():
            continue
        slots = new._parse_slots(r["account_context"])
        d, _a = new.split_audit(r["draft_raw"])
        d, _x, _y = new.render_body(d)
        f, _x, _y = new.render_body(r["final_body"] or "")
        out.append((axis, r["case"], "draft", slots, r["manifest"], d))
        out.append((axis, r["case"], "final", slots, r["manifest"], f))
    return out


ROWS = bodies(load_v15, "main") + bodies(load_regression, "regression")


# ------------------------------------------------------------------ Q1 误报
def _fire(mod, rows):
    s = []
    for axis, case, tag, slots, man, body in rows:
        for h in mod.check_stale_value_override(slots, body)[0]:
            s.append((axis, case, tag, "G4", h[:80]))
        for h in mod.check_manifest(man, body, {})[2]:
            s.append((axis, case, tag, "MAN", h[:80]))
    return s


def q1():
    o, n = _fire(old, ROWS), _fire(new, ROWS)
    gone = [x for x in o if x not in n]
    added = [x for x in n if x not in o]
    return {
        "bodies_checked": len(ROWS),
        "v15_fire": len(o), "v151_fire": len(n),
        "removed": [{"case": x[1], "tag": x[2], "kind": x[3], "hit": x[4],
                     "ruling": RULING.get((x[1], x[3]), "未判读 —— 必须逐例判读后才能算清掉误报")}
                    for x in gone],
        "added": [{"case": x[1], "tag": x[2], "kind": x[3], "hit": x[4]} for x in added],
        "pass": all(RULING.get((x[1], x[3]), "").startswith("误报") for x in gone) and not added,
    }


# ------------------------------------------------------------------ Q2 漏检
INDEP_RATE = re.compile(r"(\d+)\s*条\s*[/／]\s*(天|日|周)")


def _forge(slots):
    """族一二：正文一字不改，把槽位权威值机械改成与正文必然冲突的值。"""
    outs = []
    for slot, raw in (slots or {}).items():
        for forged in ("99 条/周", "98 条/天"):
            f = dict(slots); f[slot] = forged
            outs.append((slot, forged, f))
    return outs


def _indep_forge_body(body):
    """族三：槽位真实，正文机械改写 —— 由**独立解析器**造，不用被测代码的词表。
    在正文每个「N 条」后面机械补一个半角周期后缀，制造必然的速率断言。"""
    return re.sub(r"(?<![第下上这那另某每前后同各])([0-9]|[一两二三四五六七八九十])\s*条(?!\s*[/／])",
                  r"\g<1> 条/周", body or "", count=3)


# 「旧能抓到的新也要抓到」有且只有一个例外：**旧的那一次抓取本身就是误报**。
# 这个例外不能由我读一遍句子来给，必须机械判定，否则它就退化成「想放过就放过」。
# 判定规则：把旧判据在这一段上真正开火的那个带周期数量找出来，看它的周期是不是
# 由一个**后面紧跟「期」**的周期词借来的。是 ⇒ 这次抓取正是 DD-5 要修掉的那类；
# 不是 ⇒ 真漏检，整项 FAIL。
_PERIOD_WORD_LOOSE = old.PERIOD_WORD


def _lost_is_dd5(slots, body):
    """返回 (是否全部由 DD-5 解释, 证据行)。逐段复算旧判据的开火点。"""
    ev, allx = [], True
    for slot, subj in old.QTY_SUBJECTS.items():
        raw = slots.get(slot)
        if raw is None or not old._slot_filled(raw):
            continue
        sq = old._slot_authority(raw)
        if not sq:
            continue
        spw = {old._per_week(q["n"], q["unit"]) for q in sq}
        for seg in old._segments(body or ""):
            if not re.search(subj, seg) or not re.search(old.NOW_MARKER, seg):
                continue
            if re.search(old.PAST_MARKER, seg):
                continue
            qs = [q for q in old._qty_scan(seg) if not q["partitive"]]
            per = [q for q in qs if q["unit"] and not old._negated_at(seg, q["start"])
                   and not old._negated_after(seg, q["end"])]
            if not per or any(old._per_week(q["n"], q["unit"]) in spw for q in per):
                continue
            # 这一段是旧判据的开火点。逐个数量看周期是从哪借的。
            for q in per:
                if q["period_source"] != "word":
                    allx = False
                    ev.append({"slot": slot, "seg": seg.strip()[:70], "n": q["n"],
                               "period_source": q["period_source"],
                               "dd5": False, "why": "周期不是由周期词借来的 —— 真漏检"})
                    continue
                pre = seg[max(0, q["start"] - old.PERIOD_LOOKBACK):q["start"]]
                mw = _PERIOD_WORD_LOOSE.search(pre)
                tail = pre[mw.end():mw.end() + 1] if mw else ""
                ok = (tail == "期")
                allx = allx and ok
                ev.append({"slot": slot, "seg": seg.strip()[:70], "n": q["n"],
                           "period_word": mw.group(0) if mw else None, "next_char": tail,
                           "dd5": ok,
                           "why": "「…期」被当成周期词 —— 正是 DD-5 要修掉的那次误抓"
                                  if ok else "周期词是真的 —— 真漏检"})
            break
    return allx, ev


def q2():
    caught_old = caught_new = 0
    lost, genuine = [], []
    for axis, case, tag, slots, man, body in ROWS:
        for slot, forged_v, forged in _forge(slots):
            co = bool(old.check_stale_value_override(forged, body)[0])
            cn = bool(new.check_stale_value_override(forged, body)[0])
            caught_old += co; caught_new += cn
            if co and not cn:
                ok, ev = _lost_is_dd5(forged, body)
                rec = {"family": "1-2 槽位伪造", "case": case, "body": tag,
                       "slot": slot, "forged": forged_v, "explained_by_dd5": ok,
                       "evidence": ev}
                lost.append(rec)
                if not ok:
                    genuine.append(rec)
        fb = _indep_forge_body(body)
        if fb != body:
            co = bool(old.check_stale_value_override(slots, fb)[0])
            cn = bool(new.check_stale_value_override(slots, fb)[0])
            caught_old += co; caught_new += cn
            if co and not cn:
                ok, ev = _lost_is_dd5(slots, fb)
                rec = {"family": "3 正文机械改写（独立解析器）", "case": case, "body": tag,
                       "explained_by_dd5": ok, "evidence": ev}
                lost.append(rec)
                if not ok:
                    genuine.append(rec)
    return {"v15_caught": caught_old, "v151_caught": caught_new,
            "lost_total": len(lost),
            "lost_explained_by_dd5": len(lost) - len(genuine),
            "genuine_losses": genuine,
            "lost_cases": sorted({x["case"] for x in lost}),
            "sample_evidence": lost[:2],
            "pass": not genuine}


# ------------------------------------------------------------------ Q3 具名族
NEG_CASES = ["这是长期价值目标下，本周期最重要的一条",
             "本周期内最值得做的一条",
             "本日期最靠前的一条"]
POS_CASES = [("本周实际产能只有一条", 1, "周"),
             ("每周 3 条", 3, "周"),
             ("一周 2 条", 2, "周"),
             ("该周 1 条", 1, "周"),
             ("目标是 4 条/周", 4, "周"),
             ("本周期内每周 3 条", 3, "周")]


def q3():
    neg = [{"text": t, "v15": old._qty_scan(t), "v151": new._qty_scan(t),
            "ok": all(q["unit"] is None for q in new._qty_scan(t))} for t in NEG_CASES]
    pos = [{"text": t, "want": (n, u), "got": new._qty_scan(t),
            "ok": any(q["n"] == n and q["unit"] == u for q in new._qty_scan(t))}
           for t, n, u in POS_CASES]
    return {"negative": neg, "positive": pos,
            "pass": all(x["ok"] for x in neg) and all(x["ok"] for x in pos)}


# ------------------------------------------------------------------ Q4 消融
def _miss_count(mod):
    n = 0
    for axis, case, tag, slots, man, body in ROWS:
        for slot, fv, forged in _forge(slots):
            n += bool(mod.check_stale_value_override(forged, body)[0])
        fb = _indep_forge_body(body)
        if fb != body:
            n += bool(mod.check_stale_value_override(slots, fb)[0])
    return n


def q4():
    base = (_fire(new, ROWS), _miss_count(new))
    units = []

    def one(name, apply_, undo):
        apply_()
        got = (_fire(new, ROWS), _miss_count(new))
        undo()
        units.append({"unit": name,
                      "fire_when_disabled": len(got[0]),
                      "miss_when_disabled": got[1],
                      "changed_on_fp_axis": got[0] != base[0],
                      "changed_on_miss_axis": got[1] != base[1],
                      "changed": got != base})

    o = new.PERIOD_WORD
    one("DD-5 `(?!期)`（「本周期」不是「本周」）",
        lambda: setattr(new, "PERIOD_WORD", old.PERIOD_WORD),
        lambda: setattr(new, "PERIOD_WORD", o))
    return {"baseline_fire": len(base[0]), "baseline_miss_caught": base[1],
            "units": units, "pass": all(u["changed"] for u in units)}


# ------------------------------------------------------------------ Q5 真拒不变
def q5():
    from replay_v151 import _run
    rows, _sk = _run(load_regression(), "regression")
    rej = [x["case"] for x in rows if x["v15_carry"] == "REJECTED_KEEP_PREVIOUS"]
    return {"still_rejected": rej, "pass": set(rej) == {"E07", "E08"}}


def main():
    rep = {"old_commit": OLD_COMMIT, "Q1_false_positive": q1(), "Q2_miss": q2(),
           "Q3_named_family": q3(), "Q4_ablation": q4(), "Q5_true_rejection": q5()}
    rep["ALL_PASS"] = all(rep[k]["pass"] for k in rep if k.startswith("Q"))
    print(json.dumps(rep, ensure_ascii=False, indent=2))
    os.makedirs(OUT, exist_ok=True)
    json.dump(rep, open(os.path.join(OUT, "VERIFY_REBIND007.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    return rep


if __name__ == "__main__":
    sys.exit(0 if main()["ALL_PASS"] else 1)
