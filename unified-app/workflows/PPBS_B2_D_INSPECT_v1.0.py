#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PP 边界后继 b2｜Phase E 产出定位器。**零模型调用、零判定。**

只把冻结判据 D1-b / D1-c 关心的位置在真实产出里指出来，供有界判定使用。
本文件**不产生 PASS / FAIL**，标注 evidence_locator_only, NOT_A_CHECKER。

    python3 PPBS_B2_D_INSPECT_v1.0.py D1
"""
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
UAPP = os.path.abspath(os.path.join(HERE, ".."))
EVDIR = os.path.join(UAPP, "evidence", "stages", "pp_boundary_successor")

HISTORY_PROBES = ["一直在用", "常用", "长期以来", "十年", "历来", "向来", "一贯",
                  "多年来", "一直以来", "从来都"]
HEDGE_PROBES = ["合理推断", "基于职责", "据说", "印象中"]
ACTION_PROBES = ["关注", "评论", "回复", "收藏", "转发", "分享", "点赞", "话题",
                 "购买", "到店", "预约", "咨询", "私信", "领取", "下单"]
NEWRULE_TRACE = ["strict_cta_closed", "闭合", "权威顺序", "要求受众", "NOT_APPLICABLE",
                 "被动答复", "只保留内容本身"]


def main():
    which = (sys.argv[1] if len(sys.argv) > 1 else "D1").upper()
    raw = json.load(io.open(os.path.join(EVDIR, "PPBS_B2_%s_RAW.json" % which),
                            encoding="utf-8"))
    o = raw.get("outputs") or {}
    art = o.get("artifact") or ""
    ud = o.get("user_delivery") or ""
    rep = {"case": which, "evidence_locator_only": True, "NOT_A_CHECKER": True,
           "run_id": raw.get("workflow_run_id"), "run_status": raw.get("run_status"),
           "elapsed_seconds": raw.get("elapsed_seconds"), "attempts": raw.get("attempts"),
           "pp_graph_md5_at_run": raw.get("pp_graph_md5_at_run"),
           "pp_published_version_at_run": raw.get("pp_published_version_at_run"),
           "pp_provider_pin_at_run": raw.get("pp_provider_pin_at_run"),
           "output_keys": sorted(o), "artifact_len": len(art), "user_delivery_len": len(ud)}

    # 每一处问号结尾的句子（逐面）
    def qsent(text):
        out = []
        for line in text.split("\n"):
            for seg in re.split(r"(?<=[。！\n])", line):
                s = seg.strip()
                if s.endswith("？") or s.endswith("?"):
                    out.append(s[-120:])
        return out

    rep["question_sentences"] = {"artifact": qsent(art), "user_delivery": qsent(ud)}
    rep["history_probe_hits"] = {p: {"artifact": art.count(p), "user_delivery": ud.count(p)}
                                 for p in HISTORY_PROBES if art.count(p) or ud.count(p)}
    rep["hedge_probe_hits"] = {p: {"artifact": art.count(p), "user_delivery": ud.count(p)}
                               for p in HEDGE_PROBES if art.count(p) or ud.count(p)}
    rep["action_probe_hits"] = {p: {"artifact": art.count(p), "user_delivery": ud.count(p)}
                                for p in ACTION_PROBES if art.count(p) or ud.count(p)}
    rep["new_rule_trace"] = {p: {"artifact": art.count(p), "user_delivery": ud.count(p)}
                             for p in NEWRULE_TRACE}

    # 九行对外输出面各自的原文切片
    def slab(text, key, n=1400):
        i = text.find(key)
        return text[i:i + n] if i >= 0 else None

    rep["surface_slices"] = {k: slab(art, k) for k in
                             ("cta_surface", "comment_design", "author_share_line",
                              "used_fact_refs", "titles", "recommended_title",
                              "publish_copy", "platform_variants")}
    p = os.path.join(EVDIR, "PPBS_B2_%s_INSPECT.json" % which)
    io.open(p, "w", encoding="utf-8").write(json.dumps(rep, ensure_ascii=False, indent=1) + "\n")
    print("落盘：", p)
    print("run=%s %s %.1fs attempts=%s" % (rep["run_id"], rep["run_status"],
                                           rep["elapsed_seconds"] or 0, rep["attempts"]))
    print("artifact=%d user_delivery=%d" % (len(art), len(ud)))
    print("历史行为探针命中：", rep["history_probe_hits"] or "无")
    print("问号句 artifact=%d user_delivery=%d"
          % (len(rep["question_sentences"]["artifact"]),
             len(rep["question_sentences"]["user_delivery"])))
    print("新规则痕迹：", {k: v for k, v in rep["new_rule_trace"].items()
                          if v["artifact"] or v["user_delivery"]})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
