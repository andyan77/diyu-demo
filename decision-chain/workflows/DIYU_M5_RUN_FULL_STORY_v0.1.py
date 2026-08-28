#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""跑一次完整主故事并把原始结果落盘。**诊断用**——正式运行由 Candidate Run Manifest 冻结后驱动。"""
import importlib.util, json, os, sys, traceback

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
def _load(n, p):
    s = importlib.util.spec_from_file_location(n, p); m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m); return m
FS = _load("fs", os.path.join(ROOT, "decision-chain", "workflows", "DIYU_M5_FULL_STORY_v0.1.py"))
RT = FS.RT

OUT = os.path.join(ROOT, "decision-chain", "evidence", "m5")
NL = ("我们序里集这一轮想弄清楚一件事：顾客到底能不能自己判断哪件衣服适合自己。"
      "这周先出一条内容试试水，看这个方向立不立得住。")

def main(tag_suffix="a"):
    rt = RT.Runtime()
    boot = FS.bootstrap("full01" + tag_suffix)
    print("boot ws=%s account=%s" % (boot["ws"], boot["account"]), flush=True)
    rec, m3 = FS.full_story_01(rt, boot, NL)
    print(json.dumps({k: v for k, v in rec.items() if k not in ("deliveries", "final_text")},
                     ensure_ascii=False, indent=2), flush=True)
    result = {"full01": rec, "m3_judgment": (m3["outputs"] or {}).get("operating_judgment")}
    if rec.get("final_text"):
        pub = FS.record_publish_and_feedback(boot, rec["final_text"], boot["tag"])
        print("PUBLISH+FEEDBACK", json.dumps(pub, ensure_ascii=False), flush=True)
        rec2, m3b = FS.full_story_02(rt, boot, pub)
        print(json.dumps(rec2, ensure_ascii=False, indent=2), flush=True)
        result["publish"] = pub
        result["full02"] = rec2
        result["m3_review"] = (m3b["outputs"] or {}).get("operating_judgment")
    with open(os.path.join(OUT, "FULL_STORY_RUN_%s.json" % boot["tag"]), "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print("SAVED", os.path.join(OUT, "FULL_STORY_RUN_%s.json" % boot["tag"]), flush=True)

if __name__ == "__main__":
    try:
        main(sys.argv[1] if len(sys.argv) > 1 else "a")
    except Exception:
        traceback.print_exc(); sys.exit(1)
