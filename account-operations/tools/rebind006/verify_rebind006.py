#!/usr/bin/env python3
"""REBIND-006 预检：DD-1～DD-4 的修法在真实语料上两个方向都量，零模型。

对照组 = **本轮改动之前那一次提交**（不是 HEAD；判据一提交，HEAD 里就已经是新版，
那时再拿 HEAD 当对照组，比的是新版对新版）。

六项，逐项给数：
  P1 误报方向   64 次真实运行 × 2 份正文（草稿／终稿）= 128 份，旧判据命中几处、
                新判据命中几处、每一处逐条判读
  P2 漏检方向   探针句子全部取自真实运行、一字未改，只把权威值机械改成必然冲突的值；
                规则写死在代码里，不挑句子。**判据是「旧能抓到的新也要抓到」**
  P3 清单方向   真实语料里全部「参考类名词 + 否定类词同分句」的句子，
                配 LOADED / NOT_LOADED 两种清单各跑一遍
  P4 具名族     Founder 第 3 条点名的四族：真实旧值覆盖、三值分离、等价单位换算、拒绝合并
  P5 消融       本轮每个新守卫单独关掉，命中集必须变；不变就是不该存在（A5）
  P6 DD-1 覆盖  64 次运行里，新骨架有没有漏掉任何一个模型草稿已声明的持续位
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
OUT = os.path.join(WT, "account-operations/evidence/ep28-rebind006-precheck")
sys.path.insert(0, GATE)
sys.path.insert(0, HERE)

OLD_COMMIT = "ef35c67"          # 第 8 轮收口那一次提交 = v1.4.2，本轮改动的直接前身

import shared_checks as new                                      # noqa: E402
from corpus import load_all                                      # noqa: E402

_src = subprocess.run(
    ["git", "-C", WT, "show", f"{OLD_COMMIT}:account-operations/tools/gate_v13/shared_checks.py"],
    capture_output=True, text=True, check=True).stdout
_d = tempfile.mkdtemp(prefix="v142_")
io.open(os.path.join(_d, "shared_checks_v142.py"), "w", encoding="utf-8").write(_src)
sys.path.insert(0, _d)
import shared_checks_v142 as old                                 # noqa: E402
assert not hasattr(old, "PARTITIVE_PREFIX"), "取到的对照组不是 v1.4.2 —— 对照无效"

# 第 8 轮 12 例拒收的逐例判读（ep26 REJECTION_LEDGER_v14.json，判读在改判据之前做的）
# 加上本轮新查出的第 13 例：A/B 的 B 臂 FX-M3-HOLD-02，第 8 轮拒收台账没覆盖到它。
RULING = {
    ("B04-1P-capacity-1", "G4"): "误报（DD-2/DD-3）",
    ("B07-1-traffic-full-facts", "MAN"): "误报（DD-4）",
    ("FX-M3-HOLD-02__B", "G4"): "误报（DD-3b，本轮新查出，第 8 轮拒收台账未覆盖 A/B 臂）",
}


def bodies():
    """(case, tag, slots, manifest, body)。正文由 draft_raw 确定性重算，不取二手结论。"""
    out = []
    for r in load_all():
        slots = new._parse_slots(r["account_context"])
        d, _a = new.split_audit(r["draft_raw"])
        d, _x, _y = new.render_body(d)
        f, _x, _y = new.render_body(r["final_body"] or "")
        out.append((r["case"], "draft", slots, r["manifest"], d))
        out.append((r["case"], "final", slots, r["manifest"], f))
    return out


# ------------------------------------------------------------------ P1 误报
def p1(rows):
    hits = {"old": [], "new": []}
    for case, tag, slots, man, body in rows:
        for mod, key in ((old, "old"), (new, "new")):
            for h in mod.check_stale_value_override(slots, body)[0]:
                hits[key].append({"case": case, "body": tag, "check": "G4", "hit": h})
            for h in mod.check_manifest(man, body, {})[2]:
                hits[key].append({"case": case, "body": tag, "check": "MAN", "hit": h})
    for h in hits["old"]:
        h["ruling"] = RULING.get((h["case"], h["check"]), "未判读")
    newly = [h for h in hits["new"]
             if not any(o["case"] == h["case"] and o["body"] == h["body"]
                        and o["check"] == h["check"] for o in hits["old"])]
    return {"bodies_scanned": len(rows),
            "v142_blocking_hits": len(hits["old"]), "v142_detail": hits["old"],
            "v15_blocking_hits": len(hits["new"]), "v15_detail": hits["new"],
            "newly_blocked_by_v15": newly,
            "all_v142_hits_ruled_false_positive":
                all(h["ruling"].startswith("误报") for h in hits["old"])}


# ------------------------------------------------------------------ P2 漏检
def _miss_probes(mod, slots, body):
    """探针规则写死，不挑句子：句子原样不动，只把权威值机械改成必然冲突的值。
      同单位   权威值 = 正文里该主语相关的最大每周值 + 1 条/周
      跨单位   权威值 = (最大每周值 + 1) 条/天 —— 7 倍后必然仍冲突，专测换算的**捕捉**方向
    """
    probes = []
    for slot, subj in mod.QTY_SUBJECTS.items():
        if slot not in slots or not mod._slot_filled(slots.get(slot)):
            continue
        for seg in mod._segments(body):
            if not re.search(subj, seg) or not re.search(mod.NOW_MARKER, seg):
                continue
            if re.search(mod.PAST_MARKER, seg):
                continue
            per = [q for q in mod._qty_scan(seg) if q["unit"]]
            if not per:
                continue
            top = max(mod._per_week(q["n"], q["unit"]) for q in per)
            for fam, val in (("同单位", f"{top + 1} 条/周"), ("跨单位换算", f"{top + 1} 条/天")):
                forged = dict(slots)
                forged[slot] = val
                probes.append((slot, fam, forged, seg.strip()[:80]))
            break
    return probes


# ---- 独立解析器：既不属于 v1.4.2 也不属于 v1.5，用来生成第三族探针 ----
# 前两族探针会把槽位值整个换掉，于是「槽位解析对不对」这件事永远测不到——
# 换句话说，用前两族给槽位解析做消融，是在用一把量不到它的尺子量它。
# 第三族反过来：**槽位保持真实原值**，只把正文里的数字机械改写成必然冲突的值。
# 探针集合由这个独立解析器决定，不由被测的任何一版判据决定。
INDEP_RATE = re.compile(r"(\d+)\s*条\s*[/／]\s*(天|日|周)")


def _indep_per_week(raw):
    m = INDEP_RATE.search(raw or "")
    if not m:
        return None
    n, u = int(m.group(1)), m.group(2)
    return n * 7 if u in ("天", "日") else n


def _body_forged_probes(slots, body):
    """第三族：槽位真实、正文机械改写。返回 (slot, 原句, 改写后的正文)。"""
    probes = []
    for slot, subj in new.QTY_SUBJECTS.items():
        pw = _indep_per_week(slots.get(slot) or "")
        if pw is None:
            continue
        for seg in new._segments(body):
            if not re.search(subj, seg) or not re.search(new.NOW_MARKER, seg):
                continue
            if re.search(new.PAST_MARKER, seg):
                continue
            if not re.search(r"[\d零一两二三四五六七八九十]\s*条", seg):
                continue
            forged_seg = re.sub(r"[\d零一两二三四五六七八九十]\s*条",
                                f"{pw + 1} 条/周", seg)
            probes.append((slot, seg.strip()[:80], forged_seg + "。"))
            break
    return probes


def _family3(rows, mod):
    tot = caught = 0
    lost = []
    for case, tag, slots, man, body in rows:
        for slot, seg, forged_body in _body_forged_probes(slots, body):
            tot += 1
            if mod.check_stale_value_override(slots, forged_body)[0]:
                caught += 1
            else:
                lost.append({"case": case, "body": tag, "slot": slot,
                             "authority": slots.get(slot, "")[:40], "sentence": seg})
    return tot, caught, lost


def _excluded_reason(seg, forged_slot_value):
    """探针的伪造权威值是从哪个数推出来的，那个数在新判据里被哪条守卫排掉了。"""
    out = []
    for q in new._qty_scan(seg):
        if not q["unit"]:
            continue
        if q["partitive"]:
            out.append(f"{q['n']}条/{q['unit']} 被『部分量／移除类前缀』排除")
        elif new._negated_after(seg, q["end"]):
            out.append(f"{q['n']}条/{q['unit']} 被『后置可行性否定』排除")
    return out


def p2(rows):
    tot = caught_old = caught_new = 0
    regress, oos, new_catch = [], [], 0
    for case, tag, slots, man, body in rows:
        # 探针集合由**旧判据**的口径生成，避免"用新判据出题给新判据做"
        for slot, fam, forged, seg in _miss_probes(old, slots, body):
            tot += 1
            o = bool(old.check_stale_value_override(forged, body)[0])
            n = bool(new.check_stale_value_override(forged, body)[0])
            caught_old += o
            caught_new += n
            if o and not n:
                rec = {"case": case, "body": tag, "slot": slot, "family": fam,
                       "forged_authority": forged[slot], "sentence": seg}
                why = _excluded_reason(seg, forged[slot])
                if why:
                    # 伪造值本身就是从「新判据明确不当作速率主张」的那个数推出来的：
                    # 这不是漏检，是作用域边界。**留在分母里、单独归类**，不从分母里拿掉——
                    # 拿掉了边界就看不见了（沿用 REBIND-005 §3 对否定句探针的同一处理）。
                    rec["why_out_of_scope"] = why
                    rec["segment_has_other_assertive_rate_claim"] = bool(
                        [q for q in new._qty_scan(seg)
                         if q["unit"] and not q["partitive"]
                         and not new._negated_after(seg, q["end"])
                         and not new._negated_at(seg, q["start"])])
                    oos.append(rec)
                else:
                    regress.append(rec)
            if n and not o:
                new_catch += 1
    t3, c3_new, lost3_new = _family3(rows, new)
    _t3o, c3_old, lost3_old = _family3(rows, old)
    return {"probes": tot, "caught_v142": caught_old, "caught_v15": caught_new,
            "family3_body_forged": {
                "probes": t3, "caught_v142": c3_old, "caught_v15": c3_new,
                "v15_missed": lost3_new, "v142_missed": lost3_old,
                "rule": "槽位保持真实原值，只把正文里的「N 条」机械改写成"
                        "（槽位每周值+1）条/周；探针集合由独立解析器决定，"
                        "不由被测的任何一版判据决定"},
            "new_misses_introduced_by_v15": len(regress), "detail": regress,
            "out_of_scope_by_design": len(oos), "out_of_scope_detail": oos,
            "caught_by_v15_only": new_catch,
            "rule": "句子取自真实运行、一字未改；只把权威值机械改成必然冲突的值。"
                    "判据是「旧能抓到的新也要抓到」；旧抓到而新没抓到的，"
                    "只有当伪造值来自新判据明确排除的那个数时才算作用域边界，"
                    "其余一律计为新漏检。"}


# ------------------------------------------------------------------ P3 清单
def p3(rows):
    """真实语料里全部『参考类名词 + 否定类词同分句』的句子，两种清单各跑一遍。"""
    sents = {}
    for case, tag, slots, man, body in rows:
        for seg in [x for x in re.split(r"[。；;！!？?，,、\n]", body or "") if x.strip()]:
            if re.search(old.REF_NOUN, seg) and re.search(old.REF_NEGATION, seg):
                sents.setdefault(seg.strip(), case)
    fam = "references/fashion-and-market.md", "references/six-skill-methods.md"
    out = []
    for seg, case in sorted(sents.items()):
        row = {"sentence": seg[:90], "first_seen_in": case}
        for f in fam:
            for state in ("LOADED", "NOT_LOADED"):
                man = f"<<REFERENCE_MANIFEST>>\n{f}: {state}\n<<END_REFERENCE_MANIFEST>>"
                row[f"{f.split('/')[-1][:-3]}|{state}"] = {
                    "v142": bool(old.check_manifest(man, seg, {})[2]),
                    "v15": bool(new.check_manifest(man, seg, {})[2])}
        out.append(row)
    return {"sentences": len(out), "rows": out,
            "note": "清单说 LOADED 而正文说这份参考没加载 ⇒ 应命中；"
                    "清单说 NOT_LOADED ⇒ 正文照实说，不该命中；"
                    "正文说的是账号事实缺口（不是参考文件）⇒ 两种清单都不该命中"}


# ------------------------------------------------------------------ P4 具名族
NAMED = {
    # 权威值一律写半角 `5 条/周`：全角斜杠是本轮如实披露的已知漏检（REBIND-006 §4），
    # 拿它当探针的权威值等于用一个已知不生效的输入去考判据，考不出东西来。
    "真实旧值覆盖": [("actual_capacity", "5 条/周", "本周实际产能砍到 2 条/周。", True),
                     ("actual_capacity", "5 条/周", "当前实际产能是每周 2 条。", True)],
    "三值分离": [("actual_capacity", "3 条/周",
                  "期望发布量、基线产能、本周实际可用产能都是每周 3 条，三者对齐。", False)],
    "等价单位换算": [("expected_publish_count", "每天 3 条（用户口径）",
                      "你说的每天 3 条，按本周算就是 21 条，这个数我按周口径来排。", False)],
    "拒绝合并": [("expected_publish_count", "3 条/周",
                  "本周目标 3 条不能压成一条内容同时覆盖四个目标。", False)],
    "取舍陈述（O-3 要求写的）": [("expected_publish_count", "3 条/周",
                                  "按先保主目标的一条来排，本周必须让掉另外 2 条。", False)],
    "后置否定（被否掉的方案）": [("actual_capacity", "本周实际 2 条。",
                                  "一周五条这周做不到，不是安排问题，是真实产能只剩两条。", False)],
}


def p4():
    out = {}
    for fam, cases in NAMED.items():
        rows = []
        for slot, val, body, should_fire in cases:
            slots = {slot: val}
            rows.append({"slot": slot, "authority": val, "body": body,
                         "should_fire": should_fire,
                         "v142": bool(old.check_stale_value_override(slots, body)[0]),
                         "v15": bool(new.check_stale_value_override(slots, body)[0])})
        out[fam] = {"rows": rows,
                    "pass": all(r["v15"] == r["should_fire"] for r in rows)}
    return out


# ------------------------------------------------------------------ P5 消融
NEVER = re.compile(r"(?!x)x")
NEVER_SPLIT = re.compile(r"(?!x)x")   # split 切不开 = 回到「跨小句回看」


def _fire_set(rows):
    s = []
    for case, tag, slots, man, body in rows:
        for h in new.check_stale_value_override(slots, body)[0]:
            s.append((case, tag, "G4", h[:60]))
        for h in new.check_manifest(man, body, {})[2]:
            s.append((case, tag, "MAN", h[:60]))
    return s


class _LooseRefNeg:
    """把 DD-4 的紧贴判据换回 v1.4.2 的『同分句里各出现一次』。"""

    def search(self, seg):
        return re.search(new.REF_NOUN, seg) and re.search(new.REF_NEGATION, seg)


def _miss_catch_count(rows):
    """漏检轴的签名 = 两族相加：
       族一二（槽位伪造，正文真实）+ 族三（槽位真实，正文机械改写）。
       只用族一二会把「槽位解析」这一层测不到——那一族把槽位整个换掉了。"""
    n = 0
    for case, tag, slots, man, body in rows:
        for slot, fam, forged, seg in _miss_probes(old, slots, body):
            n += bool(new.check_stale_value_override(forged, body)[0])
    n += _family3(rows, new)[1]
    return n


def p5(rows):
    """消融要在**两个轴**上看：误报轴（命中集）和漏检轴（探针捕获数）。
    只看误报轴会把「专治漏检」的守卫误判成无差别单元。"""
    base = (_fire_set(rows), _miss_catch_count(rows))
    out = {"baseline_fire_count": len(base[0]), "baseline_miss_caught": base[1], "units": []}

    def one(name, apply_, undo):
        apply_()
        got = (_fire_set(rows), _miss_catch_count(rows))
        undo()
        out["units"].append({"unit": name,
                             "fire_count_when_disabled": len(got[0]),
                             "miss_caught_when_disabled": got[1],
                             "changed_on_fp_axis": got[0] != base[0],
                             "changed_on_miss_axis": got[1] != base[1],
                             "changed": got != base,
                             "delta_cases": sorted({f"{c}/{k}" for c, _t, k, _h in got[0]})})

    o = new.PARTITIVE_PREFIX
    one("PARTITIVE_PREFIX（部分量／移除类前缀）",
        lambda: setattr(new, "PARTITIVE_PREFIX", NEVER),
        lambda: setattr(new, "PARTITIVE_PREFIX", o))
    o2 = new.NEG_AFTER
    one("NEG_AFTER（后置可行性否定）",
        lambda: setattr(new, "NEG_AFTER", NEVER),
        lambda: setattr(new, "NEG_AFTER", o2))
    o3 = new.REF_NEG_ATTACHED
    one("REF_NEG_ATTACHED（否定必须紧贴参考名词）",
        lambda: setattr(new, "REF_NEG_ATTACHED", _LooseRefNeg()),
        lambda: setattr(new, "REF_NEG_ATTACHED", o3))
    o4 = new.NEG_CLAUSE_CUT
    one("NEG_CLAUSE_CUT（前置否定不跨小句）",
        lambda: setattr(new, "NEG_CLAUSE_CUT", NEVER_SPLIT),
        lambda: setattr(new, "NEG_CLAUSE_CUT", o4))
    real = new._slot_authority
    one("_slot_authority（槽位权威值只认第一个数量）",
        lambda: setattr(new, "_slot_authority",
                        lambda raw: [q for q in new._qty_scan(raw) if q["unit"]]),
        lambda: setattr(new, "_slot_authority", real))
    out["all_units_ablatable"] = all(u["changed"] for u in out["units"])
    return out


# ------------------------------------------------------------------ P6 DD-1
def p6():
    from gate_main import main as gate_main
    bad, added, cases_added = [], 0, 0
    for r in load_all():
        gr = json.loads(gate_main(r["draft_raw"], r["manifest"],
                                  r["account_context"])["gate_report"])
        skel = gr.get("skeleton_position_ids") or []
        draft = gr.get("draft_declared_position_ids") or []
        inp = (gr.get("positions") or {}).get("input_position_ids") or []
        miss = [i for i in draft if i not in skel]
        if miss:
            bad.append({"case": r["case"], "missing_from_skeleton": miss})
        ex = [i for i in skel if i not in inp]
        if ex:
            cases_added += 1
            added += len(ex)
    return {"runs": 64, "runs_with_draft_position_missing_from_skeleton": len(bad),
            "detail": bad, "runs_with_extra_skeleton_lines": cases_added,
            "extra_skeleton_lines_total": added,
            "claim": "骨架的义务集 = 输入侧持续位 ∪ 模型草稿已声明持续位；"
                     "64 次运行里没有一个已声明位落在骨架外"}


def main():
    rows = bodies()
    rep = {"what": "REBIND-006 预检 · DD-1～DD-4 的修法在真实语料上两个方向都量",
           "zero_model_calls": True,
           "baseline_commit": OLD_COMMIT,
           "corpus": {"runs": 64, "bodies": len(rows),
                      "source": ["ep06b-runtime-behavior-v14 (49)",
                                 "ep07-longitudinal-v14 (12)",
                                 "ep08-module-ab-v14 B 臂 (3)"]},
           "P1_误报方向": p1(rows), "P2_漏检方向": p2(rows), "P3_清单方向": p3(rows),
           "P4_具名族": p4(), "P5_消融": p5(rows), "P6_DD1骨架覆盖": p6()}
    v = {
        "P1 旧判据的阻断命中全部是误报，且新判据全部清零":
            rep["P1_误报方向"]["all_v142_hits_ruled_false_positive"]
            and rep["P1_误报方向"]["v15_blocking_hits"] == 0,
        "P1 新判据没有引入任何新的阻断": not rep["P1_误报方向"]["newly_blocked_by_v15"],
        "P2 没有引入新漏检": rep["P2_漏检方向"]["new_misses_introduced_by_v15"] == 0,
        "P2 作用域边界探针逐条给出了排除理由":
            all(x.get("why_out_of_scope") for x in rep["P2_漏检方向"]["out_of_scope_detail"]),
        "P4 六族逐族符合预期": all(x["pass"] for x in rep["P4_具名族"].values()),
        "P5 每个新守卫都可消融（关掉就变）": rep["P5_消融"]["all_units_ablatable"],
        "P6 骨架零遗漏": rep["P6_DD1骨架覆盖"]["runs_with_draft_position_missing_from_skeleton"] == 0,
    }
    rep["verdict"] = {k: ("PASS" if ok else "FAIL") for k, ok in v.items()}
    rep["all_pass"] = all(v.values())
    os.makedirs(OUT, exist_ok=True)
    json.dump(rep, io.open(os.path.join(OUT, "REBIND006_FP_AND_MISS.json"), "w",
                           encoding="utf-8"), ensure_ascii=False, indent=2)
    print(json.dumps({k: rep[k] for k in ("verdict", "all_pass")}, ensure_ascii=False, indent=2))
    for k in ("P1_误报方向", "P2_漏检方向", "P5_消融", "P6_DD1骨架覆盖"):
        d = dict(rep[k])
        d.pop("v142_detail", None), d.pop("v15_detail", None), d.pop("detail", None)
        print(k, json.dumps(d, ensure_ascii=False)[:700])
    return 0 if rep["all_pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
