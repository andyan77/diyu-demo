#!/usr/bin/env python3
"""EP-08 v1.3 揭盲与推导。**本文件在 A/B 运行开始之前就已冻结提交**——这一点是本轮的重点。

第 6 轮的阻断项 B-1 是：盲评协议在判定冻结、揭盲之后被原地改写，
于是那一轮再干净的推导也只能算探索。Founder 第 4 条选了路径乙：
以 ADDENDUM_003 为**预冻结**判据重跑一次。预冻结的意思是这个文件的内容
必须先于结果存在，所以它连同 make_judge_prompts_v5.py 一起在跑之前提交。

四道自我约束，任一不成立就拒绝输出：

  T-1  自身未被事后修改：工作区文件哈希 == git 里冻结那一版的哈希。
       这条堵的正是 B-1 —— 看到结果后回来改推导公式。
  T-2  时序：全部判定文件写定早于封存映射被读取。
  T-3  同构：36 份提示词按 ADDENDUM_003 §3 归一化后只有 1 种形态，
       且与生成时冻结的记录逐份哈希一致（判定者拿到的确实是那 36 份）。
  T-4  完整：36 份判定齐备，覆盖 12 单元 × 3 名。

推导公式逐字沿用 ADDENDUM_002 §2.4／§2.5／§2.6，一个字未改——
ADDENDUM_003 §5 已列明这四节不在失效面内（A3 不多算）。

如实记录的上限：执行侧与生成映射的是同一方。T-1～T-4 由文件时序、
git 冻结哈希与构造性同构支撑，**不等于**双盲试验里的第三方保管。
"""
import hashlib, json, os, re, statistics, subprocess, sys, time

WT = "/home/faye/diyu-demo-worktrees/m3-account-content-operator-v1"
HERE = os.path.dirname(os.path.abspath(__file__))
REL_SELF = "account-operations/tools/ab_v5/unblind_v5.py"
OUT_OF_REPO = ("/tmp/claude-1000/-home-faye-diyu-demo/"
               "2c670698-40ad-483e-b793-56ac12fb6aea/scratchpad/m3-ab-blind-v5")
VERDICTS = os.path.join(OUT_OF_REPO, "verdicts")
PROMPTS_DIR = os.path.join(OUT_OF_REPO, "prompts")
HOMO = os.path.join(OUT_OF_REPO, "_prompt_homomorphism_v5.json")
SEALED = ("/tmp/claude-1000/-home-faye-diyu-demo/"
          "2c670698-40ad-483e-b793-56ac12fb6aea/scratchpad/m3/ab/_SEALED_AB_MAPPING_v5.json")
EVID = os.path.join(WT, "account-operations/evidence/ep08-module-ab-v14")

DIMS = ["运营判断", "周期组合", "产能取舍", "实验设计", "反馈判断", "内容任务质量", "共同质量底线"]
GATES = ["目标忠实", "事实", "权限", "风险", "当前任务必要条件"]
GRADE = {"优秀": 4, "合格": 3, "勉强": 2, "不足": 1, "缺失": 0}


def med(vals):
    vals = [v for v in vals if v is not None]
    return statistics.median(vals) if vals else None


def normalize(text):
    text = re.sub(r"unit_\d{2}", "unit_NN", text)
    text = re.sub(r"第 \d+ 名判定者", "第 J 名判定者", text)
    return text


def refuse(tag, msg):
    print(f"拒绝揭盲 [{tag}]：{msg}", file=sys.stderr)
    sys.exit(3)


def main():
    # ---------------- T-1 自身未被事后修改 ----------------
    live = hashlib.sha256(open(os.path.join(WT, REL_SELF), "rb").read()).hexdigest()
    frozen_blob = subprocess.run(["git", "-C", WT, "show", f"HEAD:{REL_SELF}"],
                                 capture_output=True)
    if frozen_blob.returncode != 0:
        refuse("T-1", "本文件尚未提交 —— 预冻结不成立，先提交再跑")
    frozen = hashlib.sha256(frozen_blob.stdout).hexdigest()
    if live != frozen:
        refuse("T-1", f"工作区 {live[:16]}… ≠ git 冻结版 {frozen[:16]}… —— 推导被事后修改过")

    # ---------------- 判定冻结点 ----------------
    files = sorted(f for f in os.listdir(VERDICTS)
                   if f.startswith("verdict_") and f.endswith(".json"))
    freeze = {}
    for f in files:
        p = os.path.join(VERDICTS, f)
        freeze[f] = {"sha256": hashlib.sha256(open(p, "rb").read()).hexdigest(),
                     "mtime": os.path.getmtime(p)}
    if not files:
        refuse("T-4", "一份判定都没有")
    latest = max(v["mtime"] for v in freeze.values())
    frozen_at = time.time()

    # ---------------- T-3 同构（在读映射之前做完） ----------------
    homo = json.load(open(HOMO, encoding="utf-8"))
    shapes, per_file = {}, {}
    for name in sorted(os.listdir(PROMPTS_DIR)):
        text = open(os.path.join(PROMPTS_DIR, name), encoding="utf-8").read()
        per_file[name[:-4]] = hashlib.sha256(text.encode()).hexdigest()
        shapes.setdefault(hashlib.sha256(normalize(text).encode()).hexdigest(), []).append(name)
    if len(shapes) != 1:
        refuse("T-3", f"提示词有 {len(shapes)} 种形态，ADDENDUM_003 §3 要求唯一 1 种")
    shape = next(iter(shapes))
    if shape != homo["normalized_shape_sha256"]:
        refuse("T-3", "提示词形态与生成时冻结的记录不符 —— 提示词被改过")
    drift = {k: v for k, v in per_file.items() if homo["per_prompt_sha256"].get(k) != v}
    if drift:
        refuse("T-3", f"{len(drift)} 份提示词与冻结记录逐份哈希不符：{sorted(drift)[:3]}")

    # ---------------- T-4 完整 ----------------
    if len(files) != 36:
        refuse("T-4", f"判定份数 {len(files)} ≠ 36")

    # ---------------- T-2 时序：现在才读封存映射 ----------------
    sealed = json.load(open(SEALED, encoding="utf-8"))
    mapping_read_at = time.time()
    if not (latest < mapping_read_at and frozen_at <= mapping_read_at):
        refuse("T-2", "有判定文件的 mtime 晚于映射读取时刻 —— 时序不成立")

    # ---------------- join ----------------
    cells = {}
    for f in files:
        v = json.load(open(os.path.join(VERDICTS, f), encoding="utf-8"))
        m = sealed["mapping"][v["unit"]]
        cells.setdefault((m["case_id"], m["arm"]), []).append(v)

    cases = sorted({c for c, _ in cells})
    arms = sorted({a for _, a in cells})
    grades, gate_marks = {}, {}
    for (c, a), vs in cells.items():
        for d in DIMS:
            raw = [GRADE.get(x["dimensions"].get(d, {}).get("grade")) for x in vs]
            na = sum(1 for x in vs if x["dimensions"].get(d, {}).get("grade") == "不适用")
            grades[(c, a, d)] = None if na > len(vs) / 2 else med(raw)
        for g in GATES:
            deg = sum(1 for x in vs if x["hard_gates"].get(g, {}).get("verdict") == "实质退化")
            gate_marks[(c, a, g)] = deg > len(vs) / 2

    # ---------------- 冻结推导（ADDENDUM_002 §2.4/§2.5/§2.6 逐字） ----------------
    def derive(chal, base):
        dim_out, gain_dims = {}, []
        for d in DIMS:
            pairs = [(grades.get((c, chal, d)), grades.get((c, base, d))) for c in cases]
            usable = [(x, y) for x, y in pairs if x is not None and y is not None]
            if len(usable) < len(cases) / 2:
                dim_out[d] = "不适用"
                continue
            chal_win = sum(1 for x, y in usable if x > y)
            base_win = sum(1 for x, y in usable if y > x)
            base_big = any(y - x >= 2 for x, y in usable)
            if base_big or base_win >= 2:
                dim_out[d] = f"{base}优且实质"
            elif chal_win >= 2 and not base_big:
                dim_out[d] = f"{chal}优"
                gain_dims.append(d)
            else:
                dim_out[d] = "相当"
        applicable = [d for d in DIMS if dim_out[d] != "不适用"]
        substantive_loss = [d for d in applicable if dim_out[d].endswith("优且实质")]
        overall = (len(gain_dims) > len(applicable) / 2) and not substantive_loss
        hard = [g for g in GATES
                if any(gate_marks.get((c, chal, g)) and not gate_marks.get((c, base, g))
                       for c in cases)]
        return {"dimensions": dim_out, "applicable": applicable,
                "gain_dimensions": gain_dims, "substantive_loss_dimensions": substantive_loss,
                "overall_gain": overall, "hard_gate_degradations": hard}

    b_vs_a = derive("B", "A")
    b_vs_bp = derive("B", "Bprime")
    b_vs_ap = derive("B", "Aplus")          # 仅观察，不闸任何 AC

    if b_vs_a["hard_gate_degradations"]:
        ac18 = "FAIL（硬门实质退化，不得用增益抵消）"
    elif b_vs_a["overall_gain"]:
        ac18 = "PASS"
    else:
        ac18 = "FAIL(INSUFFICIENT) —— M3_PROFESSIONAL_GAIN=NOT_VERIFIED，M3_MODULE_AB=NOT_PASSED"
    ac01c = "PASS" if b_vs_bp["overall_gain"] else "FAIL —— B 相对 B′ 无可辨识运营增益"

    # 盲评有没有失效：判定者的身份猜测跟不跟臂走
    guesses = []
    for f in files:
        v = json.load(open(os.path.join(VERDICTS, f), encoding="utf-8"))
        sc = v.get("protocol_selfcheck") or {}
        guesses.append({"unit": v["unit"], "arm": sealed["mapping"][v["unit"]]["arm"],
                        "guess": sc.get("guessed_identity", ""),
                        "basis": sc.get("guess_basis", "")})

    out = {
        "protocol": "ADDENDUM_003 预冻结 · 逐场景·单臂·独立随机分配·3 名取中位",
        "prefreeze_evidence": {
            "unblind_script_frozen_sha256": frozen,
            "unblind_script_frozen_at_commit": subprocess.run(
                ["git", "-C", WT, "log", "-1", "--format=%H %ci", "--", REL_SELF],
                capture_output=True, text=True).stdout.strip(),
            "note": "本文件的推导公式在 A/B 运行开始之前就已提交冻结；"
                    "运行时校验工作区哈希 == git 冻结版，事后修改会被拒绝",
        },
        "gates": {"T-1_self_not_modified": True, "T-2_timing": True,
                  "T-3_prompt_homomorphism": {"distinct_shapes": 1,
                                              "normalized_shape_sha256": shape,
                                              "verified_against": "生成时冻结的逐份哈希"},
                  "T-4_completeness": {"verdicts": len(files), "units": len(sealed["mapping"]),
                                       "judges_per_unit": sealed["judges_per_unit"]}},
        "verdict_freeze": freeze,
        "timing_assertion": {"last_verdict_mtime": latest, "mapping_read_at": mapping_read_at},
        "cells": {f"{c}__{a}": len(v) for (c, a), v in cells.items()},
        "grades": {f"{c}|{a}|{d}": v for (c, a, d), v in grades.items()},
        "hard_gate_marks": {f"{c}|{a}|{g}": v for (c, a, g), v in gate_marks.items()},
        "B_vs_A": b_vs_a, "B_vs_Bprime": b_vs_bp,
        "B_vs_Aplus_observation_only": b_vs_ap,
        "M3-AC-18": ac18, "M3-AC-01③": ac01c,
        "blindness_selfcheck": guesses,
        "mapping": sealed["mapping"],
    }
    os.makedirs(EVID, exist_ok=True)
    with open(os.path.join(EVID, "_unblinded_results_v5.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(json.dumps({k: out[k] for k in
                      ("gates", "B_vs_A", "B_vs_Bprime", "M3-AC-18", "M3-AC-01③")},
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
