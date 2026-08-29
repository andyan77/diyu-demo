#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""R7 · 机械重算十九维索引与 AC 状态（FINAL-P0 轮）。

**不新增十九维案例，不改十九维映射。** 映射从冻结的
`DIYU_M5_BUILD_EVIDENCE_INDEX_v1.0.py` 原样 import，不在本文件复写——
复写就等于给自己开了一个改判据的口子。

本文件相对索引构建器多做一件事，且只多做这一件：**按 A3 计算失效面。**
本轮改了 M3 successor、六个能力应用与接缝。凡是穿过这些应用、但证据来自
本轮之前（`rb` / `FRB3` 绑定）的用例，一律置 `STALE`，不按 PASS 继承。
不多算：只碰 M1 / M2 / Skill 哈希的用例不受影响，保持原判。
无法判断依赖关系的，置 `STALE` 待定向复验，不假装已知。
"""
import importlib.util, json, os, hashlib, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
EV = os.path.join(ROOT, "decision-chain", "evidence", "m5")

_spec = importlib.util.spec_from_file_location(
    "idx", os.path.join(HERE, "DIYU_M5_BUILD_EVIDENCE_INDEX_v1.0.py"))
IDX = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(IDX)          # 只为拿 DIMENSIONS / AC_BINDING，不调用它的 main

# 本轮被替换的应用。M1 / M2 / 六份 Skill 不在其中。
CHANGED_APPS = {"M3", "SEAM", "M5_HOP_ADAPTER", "MATRIX", "CAMPAIGN", "CONTENT_BRIEF",
                "CREATIVE_SCRIPT", "PRODUCTION_DIRECTOR", "PUBLISHING_PACKAGING"}

# 显式证据绑定：路径写死，不 glob、不排序、不取「最新」。
BIND = {
    "FULL_STORY_FP":  "FULL_STORY_RUN_full01fp1.json",      # 本轮 R5，fp
    "RISK_FP":        "RISK_PROBE_SUITE_riskfp1.json",      # 本轮 R4，fp
    "DIRECT_ENTRY":   "DIRECT_ENTRY_SUITE_deFRB3.json",     # 未重跑，rb
    "RISK_RB":        "RISK_PROBE_SUITE_riskFRB3.json",     # 未重跑，rb
    "M2_PROBE":       "M2_PROBE_SUITE_m2pFRB3.json",        # 纯 M2，不穿过被改应用
    "REGRESSION":     "REGRESSION_RESULTS_FRB3.json",
    "REGRESSION_RV":  "REGRESSION_RESULTS_FRB3rv1.json",    # REG-M4-01 的定向复验
}

# 用例 → 它实际穿过哪些应用。只写有独立证据支持的；证据里没有的不猜。
TOUCHES = {
    "REG-M1-01":    set(),          # 纯 M1
    "REG-M2-01":    set(),          # 纯 M2
    "REG-SKILLS-01": set(),         # 六份 Skill 运行时哈希比对
    "REG-M3-01":    {"M3"},
    "REG-M4-01":    set(),          # M4 已发布的八个应用，本轮未改
    "RISK-PUBLISH-ID-01": set(),    # M2 持久化探针
    "RISK-RECOVERY-01":   set(),    # M2 持久化探针
}


def sha256(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def load(key):
    p = os.path.join(EV, BIND[key])
    if not os.path.exists(p):
        raise SystemExit("拒绝重算：缺证据 %s" % p)
    return json.load(open(p, encoding="utf-8")), p


def touched_apps(case_id, rec):
    """返回该用例穿过的应用集合；无法判断返回 None（按 A3 置 STALE，不算少算）。"""
    if case_id in TOUCHES:
        return TOUCHES[case_id]
    apps = rec.get("apps_actually_run")
    if isinstance(apps, dict):
        return set(apps.keys())
    return None


def main():
    cases, srcs = {}, {}

    # ---- 本轮 fp 证据：CURRENT ----
    D, p = load("FULL_STORY_FP"); srcs["FULL_STORY_FP"] = (p, sha256(p))
    f1 = D.get("full01") or {}
    cases["FULL-01"] = {"verdict": "PASS" if f1.get("last_delivered_step") else "FAIL",
                        "source": os.path.basename(p), "bind": "fp",
                        "last_delivered_step": f1.get("last_delivered_step")}
    f2 = D.get("full02") or {}
    steps = {s.get("step"): s for s in f2.get("steps", [])}
    ok = (steps.get("M2_feedback_readback", {}).get("http") == 200
          and steps.get("M2_cycle_next", {}).get("http") == 200
          and steps.get("M2_cycle_decision", {}).get("http") == 200
          and steps.get("M3_review", {}).get("judgment_chars", 0) > 0)
    cases["FULL-02"] = {"verdict": "PASS" if ok else "FAIL",
                        "source": os.path.basename(p), "bind": "fp"}

    D, p = load("RISK_FP"); srcs["RISK_FP"] = (p, sha256(p))
    for r in D.get("results", []):
        cases[r["id"]] = {"verdict": r["verdict"], "source": os.path.basename(p),
                          "bind": "fp", "failures": r.get("failures")}

    # ---- 轮前证据：先原样收，再按 A3 判失效 ----
    for key in ("DIRECT_ENTRY", "RISK_RB", "M2_PROBE"):
        D, p = load(key); srcs[key] = (p, sha256(p))
        for r in D.get("results", []):
            if r["id"] in cases:          # 已被本轮 fp 证据覆盖的，不回退
                continue
            rec = {"verdict": r["verdict"], "source": os.path.basename(p),
                   "bind": "pre-round", "failures": r.get("failures"),
                   "apps_actually_run": r.get("apps_actually_run")}
            sp = r.get("semantic_part")
            if sp:
                rec["semantic_part_status"] = "%s(%s)" % (sp.get("status"), sp.get("reason"))
            cases[r["id"]] = rec

    D, p = load("REGRESSION"); srcs["REGRESSION"] = (p, sha256(p))
    for k, v in D.items():
        cases[k] = {"verdict": v.get("verdict"), "source": os.path.basename(p),
                    "bind": "pre-round"}
    D, p = load("REGRESSION_RV"); srcs["REGRESSION_RV"] = (p, sha256(p))
    for k, v in D.items():
        cases[k] = {"verdict": v.get("verdict"), "source": os.path.basename(p),
                    "bind": "pre-round", "note": "定向复验结果，取代同名旧判"}

    # ---- A3 失效传播 ----
    for cid, rec in cases.items():
        if rec.get("bind") == "fp":
            rec["freshness"] = "CURRENT"
            continue
        apps = touched_apps(cid, rec)
        if apps is None:
            rec["freshness"] = "STALE"
            rec["stale_reason"] = "依赖关系无法从证据判断，按 A3 置 STALE 待定向复验"
        elif apps & CHANGED_APPS:
            rec["freshness"] = "STALE"
            rec["stale_reason"] = "穿过本轮被替换的应用：%s" % sorted(apps & CHANGED_APPS)
        else:
            rec["freshness"] = "CURRENT"
            rec["current_reason"] = "不穿过本轮被替换的任何应用"
        if rec["freshness"] == "STALE":
            rec["verdict_before_stale"] = rec["verdict"]
            rec["verdict"] = "NOT_VERIFIED"

    # ---- 十九维（映射照抄冻结件）----
    dims = []
    for did, label, evidence in IDX.DIMENSIONS:
        rows = []
        for cid in evidence:
            c = cases.get(cid)
            rows.append({"case": cid,
                         "verdict": (c or {}).get("verdict", "NOT_RUN"),
                         "freshness": (c or {}).get("freshness", "NOT_RUN"),
                         "source": (c or {}).get("source")})
        vs = [(r["verdict"], r["freshness"]) for r in rows]
        if any(v == "FAIL" and f == "CURRENT" for v, f in vs):
            status = "FAIL"
        elif any(v in ("PASS", "PASS_DECIDABLE_PART_ONLY") and f == "CURRENT" for v, f in vs):
            status = "CURRENT"
        elif any(f == "STALE" for _, f in vs):
            status = "STALE"
        else:
            status = "NOT_COVERED"
        d = {"id": did, "label": label, "status": status, "evidence": rows}
        pend = [{"case": r["case"],
                 "semantic": cases[r["case"]].get("semantic_part_status")}
                for r in rows if cases.get(r["case"], {}).get("semantic_part_status")]
        if pend:
            d["semantic_parts_not_verified"] = pend
        dims.append(d)

    # ---- AC 状态 ----
    acs = []
    for acid, label, spec in IDX.AC_BINDING:
        if spec["kind"] == "human_only":
            acs.append({"id": acid, "label": label, "status": "NOT_VERIFIED",
                        "note": spec["note"]})
        elif spec["kind"] == "static":
            acs.append({"id": acid, "label": label, "status": "NOT_RECOMPUTED_HERE",
                        "note": spec["note"] + "（R7 只重算用例推出的状态，不重算静态项）"})
        elif spec["kind"] == "dimensions":
            bad = [d["id"] for d in dims if d["status"] == "FAIL"]
            stale = [d["id"] for d in dims if d["status"] == "STALE"]
            nc = [d["id"] for d in dims if d["status"] == "NOT_COVERED"]
            acs.append({"id": acid, "label": label,
                        "status": "FAIL" if bad else ("STALE" if stale or nc else "CURRENT"),
                        "failing_dimensions": bad, "stale_dimensions": stale,
                        "not_covered_dimensions": nc})
        else:
            rows = [{"case": c, "verdict": cases.get(c, {}).get("verdict", "NOT_RUN"),
                     "freshness": cases.get(c, {}).get("freshness", "NOT_RUN")}
                    for c in spec["cases"]]
            if any(r["verdict"] == "FAIL" and r["freshness"] == "CURRENT" for r in rows):
                st = "FAIL"
            elif any(r["freshness"] in ("STALE", "NOT_RUN") for r in rows):
                st = "STALE"
            else:
                st = "CURRENT"
            rec = {"id": acid, "label": label, "status": st, "cases": rows}
            if spec.get("holdouts"):
                rec["holdouts_this_round"] = {
                    "HOLDOUT-M5-RB-01": "R2 重跑：原 P0 不复现（见 R2 判定）",
                    "HOLDOUT-M5-RB-02": "R2 重跑：原 P0 不复现",
                    "HOLDOUT-M5-05": "R2 重跑：两项残留不复现",
                    "FINAL-P0-HOLDOUT-01": "R3：执行侧可判 P0 零命中；含一项未决 P0 人判子项 → NOT_VERIFIED",
                    "FINAL-P0-HOLDOUT-02-A": "R3：NOT_VERIFIED（人判子项未决）",
                    "FINAL-P0-HOLDOUT-02-B": "R3：NOT_VERIFIED（人判子项未决）",
                }
                rec["status"] = "FAIL" if st == "FAIL" else "NOT_VERIFIED"
                rec["status_reason"] = ("RISK-M4-030+031 本轮 CURRENT 且 FAIL；"
                                        "同时三份留出均含未决人判子项。两者都不允许记 PASS。")
            acs.append(rec)

    out = {
        "recompute_id": "V1_M5_FINAL_P0_R7_INDEX_RECOMPUTE_v1.0",
        "task_id": "DIYU-V1-M5-UNIFIED-INTEGRATION-FINAL-ACCEPTANCE-001",
        "candidate_commit": "5f84d94d542693f143faab0444525618ab21a4e9",
        "bind": "fp",
        "dimension_mapping_source": "DIYU_M5_BUILD_EVIDENCE_INDEX_v1.0.py（原样 import，未改）",
        "changed_apps_this_round": sorted(CHANGED_APPS),
        "evidence_bindings": {k: {"path": os.path.relpath(v[0], ROOT), "sha256": v[1]}
                              for k, v in srcs.items()},
        "ab_package": "本轮重建中；A/B 结论只能由独立人类盲评给出，机器侧不产生 verdict",
        "cases": cases, "dimensions": dims, "acceptance_criteria": acs,
    }
    p = os.path.join(ROOT, "decision-chain", "evidence", "m5-final-p0",
                     "FINAL_P0_R7_INDEX_RECOMPUTE.json")
    if os.path.exists(p):
        raise SystemExit("证据文件已存在，拒绝覆盖：%s" % p)
    json.dump(out, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

    print("十九维：")
    for d in dims:
        print("  %-32s %s" % (d["id"], d["status"]))
    print("AC：")
    for a in acs:
        print("  %-10s %-28s %s" % (a["id"], a["label"], a["status"]))
    print("SAVED", p)


if __name__ == "__main__":
    main()
