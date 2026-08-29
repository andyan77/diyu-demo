#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""M5 新鲜留出运行器 · HOLDOUT-M5-01..06。

**只在 Candidate Run Manifest 冻结之后运行。**

刻意的执行顺序：**先跑，后读期望判据**。
先读判据再跑，运行方式会被判据塑形，跑出来的东西就不是「系统面对这段话会怎么做」，
而是「我按判据摆出来的样子」。所以本文件只负责把留出原文送进系统并把产出原样存下来，
**不做任何判定**；判定在读过封存 oracle 之后单独进行。

路由是我显式声明的，写在这里可审计：每份留出要进哪个专业能力，由留出本身在说什么
决定（比如 06 明说「都拍完了，只要包装」，那就直达 Publishing，不补跑 Brief 和脚本）。
把它写出来，比藏在代码里好。
"""
import importlib.util, json, os, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
CUSTODY = "/home/faye/diyu-demo-holdout-custody/m5"
def _load(n, p):
    s = importlib.util.spec_from_file_location(n, p); m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m); return m
FS = _load("fs", os.path.join(ROOT, "decision-chain", "workflows", "DIYU_M5_FULL_STORY_v0.1.py"))
RT = FS.RT
EV = os.path.join(ROOT, "decision-chain", "evidence", "m5")

# 显式路由。理由写在这里，不藏在代码里。
ROUTE = {
    "HOLDOUT-M5-01": {"caps": ["CONTENT_BRIEF"],
                      "why": "要求就一条内容，且核心是两条已登记事实互相冲突要先理清楚"},
    "HOLDOUT-M5-02": {"caps": ["PUBLISHING_PACKAGING"],
                      "why": "片子已在拍，只要定结尾与评论区，属发布包装"},
    "HOLDOUT-M5-03": {"caps": ["CREATIVE_SCRIPT"],
                      "why": "明确拒绝 brief 与完整脚本，只要标题与钩子，属创意表达层"},
    "HOLDOUT-M5-04": {"caps": [],
                      "why": "全是发布与反馈的记账问题，不进内容生产，只走 M3 判断"},
    "HOLDOUT-M5-05": {"caps": ["CONTENT_BRIEF"],
                      "why": "中断在 Brief 阶段，恢复应从最高失效节点起，不是全链重跑"},
    "HOLDOUT-M5-06": {"caps": ["PUBLISHING_PACKAGING"],
                      "why": "明说都拍完了只要包装，不得补跑 Brief 与脚本"},
}


def run_one(rt, hid, text, facts, refs, boot):
    rec = {"id": hid, "route": ROUTE[hid], "steps": []}
    acct_text, _ = FS.projection_text(boot)

    m3 = rt.m3_operate(account_context=acct_text, user_request=text, loaded_references=refs)
    j = (m3["outputs"] or {}).get("operating_judgment") or ""
    rec["m3"] = {"run_id": m3["run_id"], "gate_status": (m3["outputs"] or {}).get("gate_status"),
                 "attempts": m3.get("attempts"), "judgment": j}

    upstream, up_cap = "", ""
    for cap in ROUTE[hid]["caps"]:
        h = rt.hop(cap, m3_judgment=j, upstream_delivery=upstream, upstream_capability=up_cap,
                   registered_facts=facts, account_context=acct_text, user_request=text)
        ho = h["outputs"] or {}
        step = {"hop": cap, "gaps": ho.get("extraction_gaps_text"),
                "source_map": ho.get("source_map_json"), "run_id": h["run_id"]}
        if (ho.get("capability_call") or "").strip():
            r = rt.seam(cap, capability_call=ho["capability_call"],
                        professional_input=ho.get("professional_input") or "")
            step.update({"seam_run_id": r["run_id"],
                         "business_delivery_outcome": r["business_delivery_outcome"],
                         "delivered": RT.delivered(r),
                         "component_return": RT.is_component_return(r),
                         "user_delivery": r.get("user_delivery"),
                         "artifact": r.get("artifact"),
                         "returns_json": (r.get("outputs") or {}).get("returns_json"),
                         "capabilities_skipped": r.get("capabilities_skipped")})
            if RT.delivered(r) and (r.get("artifact") or "").strip():
                upstream, up_cap = r["artifact"], cap
        rec["steps"].append(step)
    return rec


def main():
    import yaml
    man = yaml.safe_load(open(os.path.join(ROOT, "decision-chain", "docs",
                                           "V1_M5_CANDIDATE_RUN_MANIFEST_v1.1.4_FINAL_P0.yaml"),
                              encoding="utf-8"))
    if man.get("status") != "FROZEN":
        print("拒绝运行：候选清单尚未冻结，留出不得在冻结前使用。")
        return 2

    rt = RT.Runtime()
    facts = FS.registered_facts()
    refs = FS.m3_loaded_references(facts)
    only = set((os.environ.get("HOLDOUT_ONLY") or "").split(",")) - {""}
    out = {"frozen_candidate": man["git"]["candidate_commit"],
           "frozen_at": man["frozen_at"], "results": []}
    for hid in sorted(ROUTE):
        if only and hid not in only:
            continue
        path = os.path.join(CUSTODY, hid + ".md")
        text = open(path, encoding="utf-8").read().strip()
        boot = FS.bootstrap("h" + hid[-2:])
        print(">>> %s（%s）" % (hid, ROUTE[hid]["why"]), flush=True)
        rec = run_one(rt, hid, text, facts, refs, boot)
        rec["holdout_text"] = text
        rec["boot"] = boot
        out["results"].append(rec)
        for s in rec["steps"]:
            print("    %-22s %s deliver=%s" % (s.get("hop"),
                  s.get("business_delivery_outcome"), s.get("delivered")), flush=True)
    # 输出带标签：不带标签时任何一次复验都会**覆盖正式证据**。
    # 这是实际发生过的事故（HOLDOUT-03 定向复验覆盖了六份正式留出的结果，
    # 靠 git 里的提交才恢复回来）。证据文件必须只增不覆盖。
    tag = os.environ.get("HOLDOUT_TAG") or ("only_" + "_".join(sorted(only)) if only else "formal")
    p = os.path.join(EV, "HOLDOUT_RUNS_%s.json" % tag)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print("\n产出已原样存下，**本文件不做任何判定**。SAVED", p)
    return 0


if __name__ == "__main__":
    sys.exit(main())
