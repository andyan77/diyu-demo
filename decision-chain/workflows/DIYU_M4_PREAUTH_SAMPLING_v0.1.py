#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""M4 预授权采样 v0.1

依据：取证判据合同 §1.3
  「预授权采样：预先冻结 N 个候选、全部保留、一并盲评 ⇒ 算**一次**」
登记发现：M4-FND-011（内部 Artifact 与用户交付的分工不稳定，
          45 次正式运行里 7 次出现一边整体缺席）

**为什么要采样**
AC-17 的 A/B 对照里，B（FA-40）的 artifact 塌成 90 字的一句回指，
A（FA-39）是 3923 字完整 Pack。拿 5404 字比 805 字，B 必然显得薄——
但那个薄来自输出形态波动，不来自「换了目标」，会判出假 FAIL。

**为什么是 A/B 都重采，不是只重跑 B**
只重跑 B 等于按形态挑结果，是 N-30 明令禁止的「失败后重抽、只留满意输出」。
N=3 在跑之前定死，A 与 B 各 3 次，6 次全部保留，一并交 Founder。

不改任何交付物字节，不对 Dify 做任何写操作。
"""
import hashlib, importlib.util, json, os, sys, time

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
DC_WF = os.path.join(ROOT, "decision-chain", "workflows")
EVID = os.path.join(ROOT, "decision-chain", "evidence", "m4")
RUNS = os.path.join(EVID, "runs")
SAMP = os.path.join(EVID, "samples")

N = 3          # ← 跑之前冻结，跑完不改


def _load(n, p):
    s = importlib.util.spec_from_file_location(n, p)
    m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m


FA = _load("m4fa", os.path.join(DC_WF, "DIYU_M4_FORMAL_ATTEMPT_v0.1.py"))
PUB = FA.PUB

# 采样对：全部沿用已落盘的冻结输入，一个字节都不改
PAIRS = [
    ("AC-17", [("A", "FA-39"), ("B", "FA-40")]),
    ("AC-05", [("M3", "FA-34"), ("CAMPAIGN", "FA-35")]),
]


def main():
    c = PUB.Console(); c.login()
    reb = json.load(open(os.path.join(EVID, "M4_DIFY_REBIND.json"), encoding="utf-8"))
    seam = reb["seam_app_id"]; token = FA.ensure_api_key(c, seam); base = c.base
    os.makedirs(SAMP, exist_ok=True)
    index = []
    for crit, arms in PAIRS:
        for arm, src in arms:
            rec0 = json.load(open(os.path.join(RUNS, "%s.json" % src), encoding="utf-8"))
            payload = rec0["input_text"]; cap = rec0["capability"]
            assert hashlib.sha256(payload.encode()).hexdigest() == rec0["input_sha256"]
            for k in range(1, N + 1):
                sid = "%s-%s-S%d" % (crit, arm, k)
                p = os.path.join(SAMP, "%s.json" % sid)
                if os.path.exists(p):
                    print("[%s] 已有，保留" % sid); continue
                body = {"inputs": {"capability": cap, "entry": "",
                                   "capability_call": payload, "professional_input": payload,
                                   "example_reference_requested": "NO"},
                        "response_mode": "blocking", "user": "m4-preauth-sampling"}
                try:
                    res = FA.service_call(base, token, "/v1/workflows/run", body); err = None
                except Exception as e:
                    res, err = {}, str(e)[:500]
                d = res.get("data") or {}; o = d.get("outputs") or {}
                a = o.get("artifact") or ""; u = o.get("user_delivery") or ""
                rec = {"sample_id": sid, "criterion": crit, "arm": arm,
                       "source_attempt": src, "fixture_id": rec0["fixture_id"],
                       "sampling_rule": "取证判据合同 §1.3 预授权采样：N=3 跑前冻结，全部保留，一并盲评，算一次",
                       "N": N, "capability": cap,
                       "input_sha256": rec0["input_sha256"], "input_text": payload,
                       "run_id": d.get("id", ""), "status": d.get("status", "ERR" if err else "?"),
                       "error": err, "artifact_len": len(a), "user_delivery_len": len(u),
                       "artifact_collapsed": len(a) < 200 and len(u) > 400,
                       "raw_response": res,
                       "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z")}
                json.dump(rec, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
                print("[%s] %-22s status=%-10s artifact=%-5d delivery=%-5d 塌陷=%s"
                      % (sid, rec0["fixture_id"][:22], rec["status"], len(a), len(u),
                         rec["artifact_collapsed"]))
                index.append({k2: rec[k2] for k2 in
                              ("sample_id", "criterion", "arm", "run_id", "status",
                               "artifact_len", "user_delivery_len", "artifact_collapsed")})
    json.dump({"samples": index, "N": N,
               "rule": "预授权采样，全部保留，算一次；不按形态挑结果（N-30）",
               "finding": "M4-FND-011"},
              open(os.path.join(EVID, "M4_PREAUTH_SAMPLES.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    print("-> decision-chain/evidence/m4/M4_PREAUTH_SAMPLES.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
