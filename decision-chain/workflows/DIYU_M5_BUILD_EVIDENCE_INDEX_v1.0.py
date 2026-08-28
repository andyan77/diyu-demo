#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成 M5 正式验收证据索引（含十九维覆盖回填）。

**索引只索引，不判定。** 每一维的覆盖状态由它实际绑定到的用例结果推出，
索引本身不产生任何 PASS；用例没跑就是 `NOT_RUN`，跑了没过就是 `FAIL`，
不允许出现「有证据文件所以算覆盖」这种事。

十九维与用例的映射来自规划侧冻结的
`M5_ACCEPTANCE_FIXTURE_AND_19D_COVERAGE_INDEX_v1.0.yaml`，本文件照抄不改。
"""
import glob, json, os, subprocess, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
EV = os.path.join(ROOT, "decision-chain", "evidence", "m5")

# 照抄规划侧冻结的映射。改这里等于改判据，属于合同层动作，执行侧无权。
DIMENSIONS = [
    ("natural_interaction", "自然交互", ["FULL-01", "REG-M1-01"]),
    ("objective", "目标", ["FULL-01", "RISK-F10-01", "AB-M3-01", "AB-FINAL-01"]),
    ("platform", "平台", ["FULL-01", "DE-09", "RISK-PUBLISH-ID-01"]),
    ("account", "账号", ["FULL-01", "DE-01", "RISK-PUBLISH-ID-01"]),
    ("persistence", "持久化", ["FULL-02", "REG-M2-01"]),
    ("version", "版本", ["FULL-02", "RISK-PUBLISH-ID-01", "RISK-RECOVERY-01"]),
    ("publish_feedback", "发布反馈", ["FULL-02", "RISK-PUBLISH-ID-01"]),
    ("homogenization", "同质化", ["DE-06", "AB-FINAL-01"]),
    ("quality", "质量", ["FULL-01", "AB-FINAL-01", "RISK-M4-030"]),
    ("dramatization_derivative_creation", "演绎/二创", ["DE-06", "DE-07", "AB-FINAL-01"]),
    ("capacity", "产能", ["FULL-01", "AB-M3-01", "DE-08"]),
    ("external_market", "外部市场", ["FULL-01", "DE-06", "AB-M3-01"]),
    ("cta", "CTA", ["FULL-01", "DE-09", "RISK-PERM-CTA-01"]),
    ("user_discretion", "用户裁量", ["FULL-01", "DE-06", "DE-10", "AB-FINAL-01"]),
    ("production", "生产", ["FULL-01", "DE-08", "DE-09"]),
    ("permission", "权限", ["FULL-01", "RISK-PERM-CTA-01", "RISK-PUBLISH-ID-01"]),
    ("recovery", "恢复", ["DE-10", "RISK-RECOVERY-01"]),
    ("no_degradation", "不退化", ["AB-M3-01", "AB-FINAL-01", "REG-M1-01", "REG-M2-01",
                                  "REG-M3-01", "REG-M4-01", "REG-SKILLS-01"]),
    ("cross_cycle", "跨周期", ["FULL-02", "REG-M2-01", "REG-M3-01"]),
]


def collect():
    """扫描证据目录，把每个用例的最新结果收上来。只读文件，不重跑。"""
    cases = {}

    # 完整主故事
    for p in sorted(glob.glob(os.path.join(EV, "FULL_STORY_RUN_*.json"))):
        try:
            D = json.load(open(p, encoding="utf-8"))
        except Exception:
            continue
        d = D.get("full01") or {}
        delivered = [s["step"].split(":", 1)[1] for s in d.get("steps", [])
                     if s.get("step", "").startswith(("seam:", "reentry_seam:"))
                     and s.get("delivered")]
        cases["FULL-01"] = {
            "source": os.path.basename(p),
            "m3_gate_status": next((s.get("gate_status") for s in d.get("steps", [])
                                    if s.get("step") == "M3_operate"), None),
            "delivered_capabilities": delivered,
            "skipped": [x["capability"] for x in d.get("skipped", [])],
            "open_questions": len(d.get("open_questions") or []),
            "last_delivered_step": d.get("last_delivered_step"),
            "verdict": "PASS" if d.get("last_delivered_step") else "FAIL",
        }
        f2 = D.get("full02")
        if f2:
            steps = {s["step"]: s for s in f2.get("steps", [])}
            ok = (steps.get("M2_feedback_readback", {}).get("http") == 200
                  and steps.get("M2_cycle_next", {}).get("http") == 200
                  and steps.get("M2_cycle_decision", {}).get("http") == 200
                  and steps.get("M3_review", {}).get("judgment_chars", 0) > 0)
            cases["FULL-02"] = {
                "source": os.path.basename(p),
                "m3_review_gate": steps.get("M3_review", {}).get("gate_status"),
                "cycle_next": steps.get("M2_cycle_next", {}).get("cycle_id"),
                "decision_binds_next_cycle":
                    steps.get("M2_cycle_decision", {}).get("resulting_cycle_id")
                    == steps.get("M2_cycle_next", {}).get("cycle_id"),
                "verdict": "PASS" if ok else "FAIL"}
        pub = D.get("publish")
        if pub:
            cases["FULL-02"]["publish_is_test"] = pub.get("publish_is_test")
            cases["FULL-02"]["feedback_idempotent"] = pub.get("idempotent_same_row")

    # 短入口
    for p in sorted(glob.glob(os.path.join(EV, "DIRECT_ENTRY_SUITE_*.json"))):
        D = json.load(open(p, encoding="utf-8"))
        for r in D.get("results", []):
            cases[r["id"]] = {"source": os.path.basename(p), "verdict": r["verdict"],
                              "failures": r.get("failures"),
                              "apps_actually_run": r.get("apps_actually_run")}

    # 风险探针（生成侧 + 持久化侧）
    for pat in ("RISK_PROBE_SUITE_*.json", "M2_PROBE_SUITE_*.json"):
        for p in sorted(glob.glob(os.path.join(EV, pat))):
            D = json.load(open(p, encoding="utf-8"))
            for r in D.get("results", []):
                rec = {"source": os.path.basename(p), "verdict": r["verdict"],
                       "failures": r.get("failures"), "oracle": r.get("oracle")}
                # 语义部分未判定的，必须在索引里显式带出来，不许被「有一条 PASS」盖掉
                sp = r.get("semantic_part")
                if sp:
                    rec["semantic_part_status"] = "%s(%s)" % (sp.get("status"), sp.get("reason"))
                    rec["semantic_part_statement"] = sp.get("statement")
                    rec["contexts_handed_to_human"] = len(sp.get("contexts_for_human") or [])
                cases[r["id"]] = rec

    # 回归（由本文件的伴生脚本写入）
    reg = os.path.join(EV, "REGRESSION_RESULTS.json")
    if os.path.exists(reg):
        for k, v in json.load(open(reg, encoding="utf-8")).items():
            cases[k] = v
    return cases


def build(cases):
    dims = []
    for did, label, evidence in DIMENSIONS:
        rows = []
        for cid in evidence:
            c = cases.get(cid)
            rows.append({"case": cid,
                         "verdict": (c or {}).get("verdict", "NOT_RUN"),
                         "source": (c or {}).get("source")})
        vs = [r["verdict"] for r in rows]
        if any(v == "FAIL" for v in vs):
            status = "FAIL"
        elif any(v in ("PASS", "PASS_DECIDABLE_PART_ONLY") for v in vs):
            status = "CURRENT"          # 至少一条代表性 CURRENT 证据
        else:
            status = "NOT_COVERED"
        # 只要这一维的证据里有「语义部分未判定」，就把它挂在这一维上。
        # 否则「有一条 PASS 所以这一维 CURRENT」会把未判定悄悄盖掉——那正是
        # 合同禁止的「硬门失败被限制披露掩盖」的近亲。
        pend = [{"case": r["case"], "semantic": cases[r["case"]].get("semantic_part_status")}
                for r in rows
                if cases.get(r["case"], {}).get("semantic_part_status")]
        d = {"id": did, "label": label, "status": status, "evidence": rows}
        if pend:
            d["semantic_parts_not_verified"] = pend
        dims.append(d)
    return dims


def main():
    cases = collect()
    dims = build(cases)
    covered = sum(1 for d in dims if d["status"] == "CURRENT")
    failed = [d["id"] for d in dims if d["status"] == "FAIL"]
    missing = [d["id"] for d in dims if d["status"] == "NOT_COVERED"]

    out = {
        "index_id": "M5-FORMAL-ACCEPTANCE-EVIDENCE-INDEX-v1.0",
        "task_id": "DIYU-V1-M5-UNIFIED-INTEGRATION-FINAL-ACCEPTANCE-001",
        "note": ("索引只索引，不判定。每一维的状态由它实际绑定的用例结果推出；"
                 "用例没跑就是 NOT_RUN，不允许「有证据文件所以算覆盖」。"),
        "candidate_frozen": False,
        "all_runs_are_diagnostic_until_manifest_freeze": True,
        "summary": {"dimensions_total": len(dims), "current": covered,
                    "failed": failed, "not_covered": missing,
                    "dimensions_with_unverified_semantic_parts":
                        [d["id"] for d in dims if d.get("semantic_parts_not_verified")]},
        "dimensions": dims,
        "cases": cases,
    }
    p = os.path.join(ROOT, "decision-chain", "docs",
                     "V1_M5_FORMAL_ACCEPTANCE_EVIDENCE_INDEX_v1.0.yaml")
    import yaml
    with open(p, "w", encoding="utf-8") as f:
        yaml.safe_dump(out, f, allow_unicode=True, sort_keys=False, width=100)
    print("十九维：CURRENT %d / FAIL %d / NOT_COVERED %d"
          % (covered, len(failed), len(missing)))
    if failed:
        print("  FAIL:", ", ".join(failed))
    if missing:
        print("  未覆盖:", ", ".join(missing))
    print("SAVED", p)


if __name__ == "__main__":
    main()
