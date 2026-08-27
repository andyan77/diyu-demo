#!/usr/bin/env python3
"""REBIND_005 §3 的方法义务：G-4 的**两个方向都要量**，都在真实语料上量。

REBIND_004 §2.2 只给 G-2 冻结了「误报族与漏检族两族都跑、两个数字都写进记录」。
G-4 没有这一条，于是它的夹具是执行侧自己造的句子，误报率报 0，而真实运行里
12 次命中 11 次是误报、6 次拒收了合格交付。在自己造的样本上量误报，等于自己出题。

这份脚本量四件事，全部在**真实模型输出**上跑：
  A 误报：61 例真实运行，v1 与 v2 各自命中多少、哪几例
  B 真阳性：v1 抓到的唯一一次真覆盖（E04），v2 必须仍然抓到
  C 漏检：把真实正文与一个**机械改动过的**权威值重新配对（句子是真的，只有配对是构造的，
    构造规则写死在 `_miss_pairs` 里），v2 必须命中；命中不了的逐条列出来
  D 三个具名族：三值分离 / 等价单位换算 / 拒绝合并 —— 各自单独报，不并进总数

判读依据是冻结判据自己的作用域声明（REBIND_004 §2.3）：
「这一条只挡『用旧值压当轮输入』，不挡『解释为什么产能会变』。」
"""
import glob
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
GATE = os.path.join(WT, "account-operations/tools/gate_v13")
OUT = os.path.join(WT, "account-operations/evidence/ep22-rebind005-g4")
sys.path.insert(0, GATE)

import shared_checks as v2                                             # noqa: E402

# ---- v1 从 git 里取，不手抄。手抄的对照组等于没有对照组 ----
_V1_SRC = subprocess.run(
    ["git", "-C", WT, "show", "HEAD:account-operations/tools/gate_v13/shared_checks.py"],
    capture_output=True, text=True, check=True).stdout
_V1_DIR = tempfile.mkdtemp(prefix="g4v1_")
with open(os.path.join(_V1_DIR, "shared_checks_v1.py"), "w", encoding="utf-8") as f:
    f.write(_V1_SRC)
sys.path.insert(0, _V1_DIR)
import shared_checks_v1 as v1                                          # noqa: E402
assert not hasattr(v1, "_qty_scan"), "取到的 v1 不是旧版——对照组无效"

# 第 7 轮普查的逐例判读，逐字搬过来（判读在改判据之前做的，见 ep19 证据）
RULING = {
    "B02-2-blank-account": "误报", "B02-4-blocking-dependency": "误报",
    "B03-1-objective-01": "误报", "B03-4-objective-04": "误报",
    "B03-8-objective-08": "误报", "B04-N1-all-in-one": "误报",
    "B07-P-daily-three": "误报", "B09-2-medium-signal-good-fit": "误报",
    "B10-3-conflicting": "误报", "E03": "误报", "E06": "误报",
    "E04": "真阳性",
}
# Founder 第 3 条点名要验的三族，各自钉一例真实运行（例子取自第 7 轮普查，判读在先）
NAMED_FAMILIES = {
    "三值分离": ["B03-1-objective-01", "B09-2-medium-signal-good-fit"],
    "等价单位换算": ["B07-P-daily-three"],
    "拒绝合并": ["B04-N1-all-in-one"],
}


def load_samples():
    """(name, slots, body)。body 由 draft_raw 确定性重算，不从记录里取二手结论。"""
    out = []
    for pat in ("account-operations/evidence/ep06b-runtime-behavior-v13/*.json",
                "account-operations/evidence/ep07-longitudinal-v13/E*.json"):
        for p in sorted(glob.glob(os.path.join(WT, pat))):
            if "/_" in p:
                continue
            d = json.load(open(p, encoding="utf-8"))
            o = ((d.get("raw_response_body") or {}).get("data") or {}).get("outputs") or {}
            draft = o.get("draft_raw") or ""
            body, _audit = v2.split_audit(draft)
            body, _r, _s = v2.render_body(body)
            slots = v2._parse_slots((d.get("workflow_inputs") or {}).get("account_context", ""))
            out.append((os.path.basename(p)[:-5], slots, body))
    return out


def run_v1(slots, body):
    return v1.check_stale_value_override(slots, body)


def run_v2(slots, body):
    return v2.check_stale_value_override(slots, body)[0]          # 只取阻断那一半


def _miss_pairs(slots, body):
    """构造漏检探针：句子是真的，只把权威值机械改成一个必然冲突的值。

    两族，规则都写死在这里，看得见、可复算，不挑句子：
      同单位  权威值改成「正文所说的每周值 + 1 条/周」
      跨单位  权威值改成「N 条/天」，其中 7N ≠ 正文的每周值 —— 专测换算这条路的**捕捉**方向，
              光证明「换算不误伤」不够，还得证明换算之后该拦的仍然拦得住

    每个探针带一个 `assertive` 标记：句中那个数落在否定语境里的（「不为凑三条把本周压缩成
    一条内容」），v2 明确不把它当主张。这类探针**保留在计数里**、单独归类，
    不从分母里悄悄拿掉——拿掉了，作用域边界就看不见了。
    """
    import re
    probes = []
    for slot, subj in v2.QTY_SUBJECTS.items():
        if slot not in slots or not v2._slot_filled(slots.get(slot)):
            continue
        for seg in v2._segments(body):
            if not re.search(subj, seg) or not re.search(v2.NOW_MARKER, seg):
                continue
            if re.search(v2.PAST_MARKER, seg):
                continue
            per = [q for q in v2._qty_scan(seg) if q["unit"]]
            if not per:
                continue
            assertive = any(not v2._negated_at(seg, q["start"]) for q in per)
            pw = [v2._per_week(q["n"], q["unit"]) for q in per]
            top = max(pw)
            same = dict(slots)
            same[slot] = f"{top + 1} 条/周"
            probes.append((slot, same, seg.strip()[:70], assertive, "同单位"))
            cross = dict(slots)
            cross[slot] = f"{top + 1} 条/天"          # 7*(top+1) 必然 ≠ top
            probes.append((slot, cross, seg.strip()[:70], assertive, "跨单位换算"))
            break
    return probes


def main():
    samples = load_samples()
    rows, v1_fire, v2_fire = [], [], []
    for name, slots, body in samples:
        h1 = run_v1(slots, body)
        h2 = run_v2(slots, body)
        if h1:
            v1_fire.append(name)
        if h2:
            v2_fire.append(name)
        if h1 or h2:
            rows.append({"case": name, "ruling_round7": RULING.get(name, "未命中过"),
                         "v1_hits": h1, "v2_hits": h2})

    fp_cases = [c for c, r in RULING.items() if r == "误报"]
    tp_cases = [c for c, r in RULING.items() if r == "真阳性"]
    fp_still = [c for c in fp_cases if c in v2_fire]
    tp_lost = [c for c in tp_cases if c not in v2_fire]
    # v2 新增的命中（v1 没命中过的），必须逐例看，不许默认它是好事
    v2_new = [c for c in v2_fire if c not in v1_fire]

    # ---- 漏检族 ----
    miss_total, miss_caught, miss_lost, miss_negated = 0, 0, [], []
    for name, slots, body in samples:
        for slot, forged, seg, assertive, family in _miss_pairs(slots, body):
            miss_total += 1
            rec = {"case": name, "slot": slot, "family": family,
                   "forged_authority": forged[slot], "sentence": seg}
            if run_v2(forged, body):
                miss_caught += 1
            elif assertive:
                miss_lost.append(rec)
            else:
                rec["why"] = "句中那个数落在否定语境里；v2 明确不把否定句当当前值主张（作用域边界，不是漏检）"
                miss_negated.append(rec)

    # ---- 三个具名族 ----
    named = {}
    for fam, cases in NAMED_FAMILIES.items():
        named[fam] = [{"case": c,
                       "v1": bool(next(r["v1_hits"] for r in rows if r["case"] == c)),
                       "v2": bool(next(r["v2_hits"] for r in rows if r["case"] == c))}
                      for c in cases]

    report = {
        "what": "REBIND_005 §3 · G-4 v2 的误报与漏检，两个方向都在真实语料上量",
        "corpus": {"samples": len(samples),
                   "source": ["ep06b-runtime-behavior-v13", "ep07-longitudinal-v13"],
                   "note": "全部是真实模型输出，无一句由执行侧撰写"},
        "v1_baseline": {"fired": len(v1_fire), "cases": v1_fire,
                        "false_positives": len(fp_cases), "true_positives": len(tp_cases)},
        "v2": {"fired": len(v2_fire), "cases": v2_fire,
               "false_positives_remaining": fp_still,
               "true_positives_lost": tp_lost,
               "new_hits_vs_v1": v2_new},
        "miss_probe": {
            "rule": "两族：同单位（权威值 = 正文每周值 + 1 条/周）与跨单位换算"
                    "（权威值 = N 条/天，7N ≠ 正文每周值）；句子取自真实运行，未改一字",
            "probes": miss_total, "caught": miss_caught,
            "missed_assertive": len(miss_lost), "missed_assertive_detail": miss_lost,
            "out_of_scope_negated": len(miss_negated),
            "out_of_scope_negated_detail": miss_negated,
            "note": "否定句探针保留在分母里、单独归类，不从分母里拿掉——拿掉了作用域边界就看不见了"},
        "named_families_founder_directive_3": named,
        "rows": rows,
    }
    verdict = []
    verdict.append(("误报清零", not fp_still))
    verdict.append(("真阳性保住", not tp_lost))
    verdict.append(("漏检探针（主张句）全数命中", not miss_lost))
    verdict.append(("三值分离不再被拦", all(not x["v2"] for x in named["三值分离"])))
    verdict.append(("等价换算不再被拦", all(not x["v2"] for x in named["等价单位换算"])))
    verdict.append(("拒绝合并不再被拦", all(not x["v2"] for x in named["拒绝合并"])))
    report["verdict"] = {k: ("PASS" if ok else "FAIL") for k, ok in verdict}
    report["all_pass"] = all(ok for _, ok in verdict)

    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "G4_V2_FP_AND_MISS.json"), "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(json.dumps({k: report[k] for k in
                      ("v1_baseline", "v2", "miss_probe", "named_families_founder_directive_3",
                       "verdict", "all_pass")}, ensure_ascii=False, indent=2)[:4000])
    return 0 if report["all_pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
