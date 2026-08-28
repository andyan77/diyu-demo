#!/usr/bin/env python3
"""第 9 轮第 2 段：候选 v1.5 的正式取证（保真 9 + 行为 49 + 纵向 12 = 70 次运行）。

**仪器不换。** 三个 runner 一个字没改——它们是产出历轮证据的同一把尺子，改了就等于
换了尺子。这里只做一件事：把落盘目录从第 8 轮的 `-v14` 改道到 `-v15`，
免得覆盖历史证据。判据、用例、payload、并发度、重试策略全部原样。

A/B 的 B 臂 3 次单独跑（`stage2_ab_v15.py`），因为 A/A+/B′ 九次按 A3 复用、
不重新调用模型。
"""
import io
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
WT = os.path.dirname(os.path.dirname(TOOLS))
sys.path.insert(0, TOOLS)
sys.path.insert(0, os.path.join(TOOLS, "gate_v13"))
sys.path.insert(0, os.path.join(TOOLS, "runners_v14"))

EV = os.path.join(WT, "account-operations/evidence")
STEPS = [
    ("EP-06 保真 9 例", "ep06_dify_fidelity_v14", "EVIDENCE_DIR",
     os.path.join(EV, "ep06-runtime-fidelity-dify-v15")),
    ("EP-06b 行为 49 例", "run_behavior_002_v14", "EVID",
     os.path.join(EV, "ep06b-runtime-behavior-v15")),
    ("EP-07 纵向 12 步", "run_longitudinal_v14", "EVID",
     os.path.join(EV, "ep07-longitudinal-v15")),
]


def main():
    only = sys.argv[1] if len(sys.argv) > 1 else None
    rows = []
    for label, mod, attr, out in STEPS:
        if only and only not in mod:
            continue
        os.makedirs(out, exist_ok=True)
        left = [f for f in os.listdir(out) if not f.startswith(".")]
        if left:
            rows.append({"step": label, "skipped": f"{out} 非空（{len(left)} 项），不混跑"})
            print(f"跳过 {label}：目录非空", flush=True)
            continue
        print(f"\n{'='*70}\n=== {label} -> {os.path.basename(out)} ===", flush=True)
        m = __import__(mod)
        setattr(m, attr, out)
        t0 = time.time()
        try:
            m.main()
            ok, err = True, None
        except SystemExit as e:
            ok, err = (e.code in (0, None)), f"SystemExit {e.code}"
        except Exception as e:  # noqa: BLE001 - 失败如实记，不隐藏
            ok, err = False, f"{type(e).__name__}: {e}"
        rows.append({"step": label, "module": mod, "out": out, "ok": ok, "error": err,
                     "minutes": round((time.time() - t0) / 60, 1)})
        print(f"=== {label} 结束 ok={ok} err={err} 用时 {rows[-1]['minutes']} 分钟",
              flush=True)
    rep = {"what": "第 9 轮第 2 段：候选 v1.5 正式取证（Dify 三组）",
           "carrier": "dify_workflow", "app_id": "b7fb5b1a-9278-426c-bb8a-f9f288639548",
           "candidate": "m3-cand-v1.5", "steps": rows}
    o = os.path.join(EV, "ep32-formal-v15")
    os.makedirs(o, exist_ok=True)
    json.dump(rep, io.open(os.path.join(o, "STAGE2_DIFY_RUN.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    print("\n" + json.dumps(rep, ensure_ascii=False, indent=2), flush=True)
    return 0 if all(r.get("ok") for r in rows if "ok" in r) else 1


if __name__ == "__main__":
    sys.exit(main())
