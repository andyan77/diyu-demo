#!/usr/bin/env python3
"""第 9 轮第 2 段 · A/B：**只重跑 B 臂 3 次**，A / A+ / B′ 九次逐字复用。

为什么只跑 B：A/A+/B′ 三臂不经过闸门，本轮改的全部在闸门里；而且
`SKILL.md` 本轮 sha256 逐字节未变（`245ee2ab…`），三臂的系统提示词哈希因此也没变。
按 A3「不多算」，让有证据、不受影响的项失效同样是错——所以这九次不重新调用模型。

**这不是声明，是断言**：复用前逐条比对三臂的 `system_prompt_sha256` 与第 8 轮记录，
对不上就拒绝复用、整个脚本退出，一次 API 都不花。

B 臂走 `gate_pipeline_v14.run_gated`，它 import 的就是仓库里 `gate_v13/` 那份
——现在是 v1.5。镜像等于产品由同一性保证，不靠声明。
"""
import hashlib
import io
import json
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
WT = os.path.dirname(os.path.dirname(TOOLS))
for p in (TOOLS, os.path.join(TOOLS, "gate_v13"), os.path.join(TOOLS, "runners_v14"),
          os.path.join(TOOLS, "ab_v5")):
    sys.path.insert(0, p)

from gate_pipeline_v14 import run_gated                                  # noqa: E402
from shared_checks import check_leaks                                    # noqa: E402
import run_ab_v5 as AB                                                   # noqa: E402

EV = os.path.join(WT, "account-operations/evidence")
SRC = os.path.join(EV, "ep08-module-ab-v14")          # 第 8 轮，只读
DST = os.path.join(EV, "ep08-module-ab-v15")
REUSED_ARMS = ("A", "Aplus", "Bprime")


def _sha(s):
    return hashlib.sha256(s.encode()).hexdigest()


def main():
    spec = json.load(open(os.path.join(SRC, "_arms_and_holdouts_v5.json"), encoding="utf-8"))
    arms, holdouts = spec["arms"], spec["holdouts"]

    # ---- 复用合法性：三臂提示词必须与第 8 轮逐字节相同，否则拒绝复用 ----
    reuse_proof = []
    for h in holdouts:
        for arm in REUSED_ARMS:
            p = os.path.join(SRC, f"{h['fixture_id']}__{arm}.json")
            rec = json.load(open(p, encoding="utf-8"))
            now = _sha(arms[arm].get("system_prompt") or "")
            same = rec["system_prompt_sha256"] == now
            reuse_proof.append({"case": h["fixture_id"], "arm": arm,
                                "recorded_sha256": rec["system_prompt_sha256"][:16],
                                "recomputed_now": now[:16], "identical": same})
            if not same:
                raise SystemExit(f"拒绝复用：{h['fixture_id']}__{arm} 提示词哈希对不上，未发起任何调用")

    os.makedirs(DST, exist_ok=True)
    left = [f for f in os.listdir(DST) if not f.startswith(".")]
    if left:
        raise SystemExit(f"REFUSE: {DST} 非空（{len(left)} 项），不混跑")
    probe = os.path.join(DST, ".write_probe")
    with open(probe, "w") as f:
        f.write("ok")
    os.remove(probe)

    for h in holdouts:                                   # 复用件逐字复制并校验哈希
        for arm in REUSED_ARMS:
            s = os.path.join(SRC, f"{h['fixture_id']}__{arm}.json")
            d = os.path.join(DST, f"{h['fixture_id']}__{arm}.json")
            shutil.copy2(s, d)
            assert (hashlib.sha256(open(s, "rb").read()).hexdigest()
                    == hashlib.sha256(open(d, "rb").read()).hexdigest())
    shutil.copy2(os.path.join(SRC, "_arms_and_holdouts_v5.json"),
                 os.path.join(DST, "_arms_and_holdouts_v5.json"))

    key = AB.load_key()
    sysp = arms["B"]["system_prompt"]
    rows = []
    for h in holdouts:
        cid = h["fixture_id"]
        um = h["account_context"] + "\n" + h["user_request"]
        print(f"start {cid}__B", file=sys.stderr, flush=True)
        t0 = time.time()
        text, trace, draft_res, repair_res = run_gated(
            AB.call, key, sysp, um, AB.MANIFEST, h["account_context"])
        rec = {"case_id": cid, "arm": "B", "runtime": "dify_mirror_v15",
               "answer_text": text, "gate_trace": trace,
               "draft_response": draft_res, "repair_response": repair_res,
               "http_status": (draft_res or {}).get("status"),
               "elapsed_seconds": round(time.time() - t0, 2),
               "model": AB.MODEL, "provider": "deepseek-direct",
               "temperature": AB.TEMPERATURE,
               "system_prompt_sha256": _sha(sysp),
               "user_message": um, "manifest": AB.MANIFEST,
               "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
        json.dump(rec, io.open(os.path.join(DST, f"{cid}__B.json"), "w", encoding="utf-8"),
                  ensure_ascii=False, indent=2)
        tok = (((draft_res or {}).get("body") or {}).get("usage") or {}).get("total_tokens")
        tok2 = (((repair_res or {}).get("body") or {}).get("usage") or {}).get("total_tokens")
        rows.append({"case": cid, "http": rec["http_status"], "chars": len(text or ""),
                     "carry": trace.get("cycle_state_carry"),
                     "gate_path": trace.get("gate_path"),
                     "draft_tokens": tok, "repair_tokens": tok2,
                     "elapsed_seconds": rec["elapsed_seconds"]})
        print(f"  done {cid}__B {rec['http_status']} {len(text or '')}字 "
              f"{trace.get('cycle_state_carry')}", file=sys.stderr, flush=True)

    leaks = {}
    for f in sorted(os.listdir(DST)):
        if not f.endswith(".json") or f.startswith("_"):
            continue
        r = json.load(open(os.path.join(DST, f), encoding="utf-8"))
        lk = check_leaks(r.get("answer_text") or "")
        if lk:
            leaks[f] = lk

    rep = {"what": "第 9 轮第 2 段 · A/B：只重跑 B 臂，A/A+/B′ 逐字复用",
           "reuse_rule": "A3 不多算：三臂不过闸门，且 SKILL.md 本轮 sha256 逐字节未变",
           "reuse_proof": reuse_proof,
           "reused_runs": len(holdouts) * len(REUSED_ARMS),
           "new_model_runs": len(holdouts),
           "b_arm": rows, "leak_scan": leaks or "无泄漏",
           "b_arm_system_prompt_sha256": _sha(sysp)}
    json.dump(rep, io.open(os.path.join(DST, "_RUN_INDEX_V15.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    print(json.dumps(rep, ensure_ascii=False, indent=2)[:1500])
    return 0 if not leaks else 1


if __name__ == "__main__":
    sys.exit(main())
