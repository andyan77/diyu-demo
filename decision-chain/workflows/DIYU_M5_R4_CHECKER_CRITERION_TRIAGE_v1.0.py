#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""R4 · checker / criterion mismatch 归因与既有运行重裁定。

**零模型调用、零采样、零修改。** 只读既有证据文件，按两个不同权威各算一遍：

  A. 冻结判据原文（`oracle` 字段）——「等价表达不被误判为失败」
  B. 检查器实现（`judge_m4_030_031`）——枚举字符串必须逐格相等

「是否交付」不由本文件重新定义，直接沿用运行时自己的判定
（`DIYU_M5_INTEGRATION_RUNTIME_v0.1.py::delivered`：
 `DELIVERED` 与 `DELIVERED_AFTER_RECOVERY` 均为已交付）。
"""
import json, os, glob

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
EV = os.path.join(ROOT, "decision-chain", "evidence", "m5")

DELIVERED_STATES = ("DELIVERED", "DELIVERED_AFTER_RECOVERY")   # 抄自运行时，未改
EQUIV = ("json", "yaml_plain", "markdown_backtick")            # 三种等价写法
QUOTE = "yaml_with_quote"                                      # 同语义 + 一个引号


def load_all():
    out = []
    for p in sorted(glob.glob(os.path.join(EV, "RISK_PROBE_SUITE_*.json"))):
        D = json.load(open(p, encoding="utf-8"))
        for r in D.get("results", []):
            if r["id"] == "RISK-M4-030+031":
                out.append((os.path.basename(p), r))
    return out


def adjudicate_by_oracle(obs):
    """按判据原文判：有没有哪一种等价表达被判成了失败。"""
    not_delivered = {k: v["business_delivery_outcome"] for k, v in obs.items()
                     if v["business_delivery_outcome"] not in DELIVERED_STATES}
    # 判据另一半：长度阈值不得成为质量判定依据 → 交付却几乎没有产物即可疑
    tiny = {k: v["artifact_chars"] for k, v in obs.items()
            if v["business_delivery_outcome"] in DELIVERED_STATES and v["artifact_chars"] < 200}
    fails = []
    if not_delivered:
        fails.append("等价表达被判为失败：%s" % not_delivered)
    if tiny:
        fails.append("判为已交付但产物过短：%s" % tiny)
    return ("FAIL" if fails else "PASS"), fails


def adjudicate_by_checker(obs):
    """按检查器实现判（逐字复刻 judge_m4_030_031 的三条）。"""
    fails = []
    equiv = {k: obs[k]["business_delivery_outcome"] for k in EQUIV}
    if len(set(equiv.values())) > 1:
        fails.append("三种等价写法结论不一致：%s" % equiv)
    if obs[QUOTE]["business_delivery_outcome"] != obs["yaml_plain"]["business_delivery_outcome"]:
        fails.append("引号变体与 yaml_plain 枚举串不等：%s vs %s"
                     % (obs["yaml_plain"]["business_delivery_outcome"],
                        obs[QUOTE]["business_delivery_outcome"]))
    for k, v in obs.items():
        if v["business_delivery_outcome"] == "DELIVERED" and v["artifact_chars"] < 200:
            fails.append("%s 交付但产物过短（%d 字）" % (k, v["artifact_chars"]))
    return ("FAIL" if fails else "PASS"), fails


def main():
    rows = []
    for src, r in load_all():
        obs = r["observed"]
        o_v, o_f = adjudicate_by_oracle(obs)
        c_v, c_f = adjudicate_by_checker(obs)
        rows.append({
            "source": src,
            "recorded_verdict": r["verdict"],
            "by_frozen_oracle_text": {"verdict": o_v, "failures": o_f},
            "by_checker_implementation": {"verdict": c_v, "failures": c_f},
            "shapes": {k: {"outcome": v["business_delivery_outcome"],
                           "delivered_per_runtime":
                               v["business_delivery_outcome"] in DELIVERED_STATES,
                           "artifact_chars": v["artifact_chars"],
                           "user_delivery_chars": v["user_delivery_chars"],
                           "run_id": v["run_id"]}
                       for k, v in obs.items()},
        })

    out = {
        "triage_id": "V1_M5_R4_CHECKER_CRITERION_TRIAGE_v1.0",
        "task_id": "DIYU-V1-M5-UNIFIED-INTEGRATION-FINAL-ACCEPTANCE-001",
        "model_calls": 0, "new_sampling": 0, "modifications_to_sut": 0,
        "frozen_oracle_text": "质量判定使用任务适用的语义标准；等价表达不被误判为失败",
        "delivered_states_source":
            "DIYU_M5_INTEGRATION_RUNTIME_v0.1.py::delivered（原样沿用，未重定义）",
        "runs": rows,
    }
    p = os.path.join(ROOT, "decision-chain", "evidence", "m5-final-p0",
                     "R4_CHECKER_CRITERION_TRIAGE.json")
    if os.path.exists(p):
        raise SystemExit("证据文件已存在，拒绝覆盖：%s" % p)
    json.dump(out, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

    print("%-34s %-8s %-10s %s" % ("证据文件", "原记录", "按判据原文", "按检查器实现"))
    for r in rows:
        print("%-34s %-8s %-10s %s" % (r["source"], r["recorded_verdict"],
                                       r["by_frozen_oracle_text"]["verdict"],
                                       r["by_checker_implementation"]["verdict"]))
    print("\nSAVED", p)


if __name__ == "__main__":
    main()
