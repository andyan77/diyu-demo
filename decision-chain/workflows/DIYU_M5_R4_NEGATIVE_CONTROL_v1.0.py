#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RISK-M4-030+031 定向负控制 · 只跑一次。

输入与预期已在 `V1_M5_R4_NEGATIVE_CONTROL_FROZEN_SPEC_v1.0.md` 冻结（本文件之前）。
**本文件只发起调用并原样存产出，不做判定。** 判定在读过冻结书之后单独进行。

纪律：只运行一次；同名证据文件存在即拒绝写入；不重复采样。
"""
import importlib.util, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))

_s = importlib.util.spec_from_file_location(
    "rt", os.path.join(HERE, "DIYU_M5_INTEGRATION_RUNTIME_v0.1.py"))
RT = importlib.util.module_from_spec(_s); _s.loader.exec_module(RT)

SPEC = "V1_M5_R4_NEGATIVE_CONTROL_FROZEN_SPEC_v1.0.md"
SPEC_SHA = "d62ad5d05b82ac4f5cb7a71beaca6b165a258af5659af43b36add576c37091c9"

# 逐字取自冻结书 §四。改这里等于改冻结输入，不允许。
CALL = "\n".join([
    "objective: 让顾客理解针织马甲在通勤衣橱里承担什么任务",
    "expected_change: 看完后能自己判断要不要把这件马甲放进当季衣橱",
    "content_promise: 讲清楚这件马甲在什么条件下成立、什么条件下不成立",
    "facts_registered: XQ-2504 燕麦针织马甲已登记材质、版型与680元售价，确认人周宁；"
    "DOC-B01 周宁选品比较表；VID-C01 试穿记录二里'三层叠穿'那一组的观察，确认人苏禾；"
    "未登记保暖温度范围",
    "expression_subject_and_boundary: 周宁出镜，保持本人选品判断与语言习惯；"
    "不得包装成真实顾客案例；不写未登记的保暖温度范围",
])

OUT = os.path.join(ROOT, "decision-chain", "evidence", "m5-final-p0",
                   "R4_NEGATIVE_CONTROL_RUN.json")


def main():
    import hashlib
    p = os.path.join(ROOT, "decision-chain", "docs", SPEC)
    got = hashlib.sha256(open(p, "rb").read()).hexdigest()
    if got != SPEC_SHA:
        raise SystemExit("拒绝运行：冻结书哈希不符\n  期望 %s\n  现场 %s" % (SPEC_SHA, got))
    if os.path.exists(OUT):
        raise SystemExit("证据文件已存在，拒绝覆盖：%s" % OUT)

    print("冻结书哈希一致：%s" % SPEC_SHA)
    print("缺席字段：audience_problem（整项不出现）")
    print("引号形式：保留，位于 facts_registered 的值内")
    rt = RT.Runtime()
    r = rt.seam("CONTENT_BRIEF", capability_call=CALL, professional_input="")

    rec = {
        "control_id": "R4-NEG-01",
        "task_id": "DIYU-V1-M5-UNIFIED-INTEGRATION-FINAL-ACCEPTANCE-001",
        "frozen_spec": SPEC, "frozen_spec_sha256": SPEC_SHA,
        "authorization": "Founder 裁决 002 §四，只允许 1 次正式运行",
        "runs_executed": 1,
        "bind": os.environ.get("M5_BIND", "fp"),
        "capability_call_sent_verbatim": CALL,
        "execution_order": "先跑、后读冻结预期。本文件不做任何判定。",
        "observed": {
            "run_id": r.get("run_id"),
            "business_delivery_outcome": r.get("business_delivery_outcome"),
            "component_return": RT.is_component_return(r),
            "delivered_per_runtime": RT.delivered(r),
            "user_delivery": r.get("user_delivery"),
            "artifact": r.get("artifact"),
            "returns_json": r.get("returns_json"),
        },
    }
    json.dump(rec, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print("\noutcome=%s component_return=%s delivered=%s ud=%d art=%d" % (
        rec["observed"]["business_delivery_outcome"], rec["observed"]["component_return"],
        rec["observed"]["delivered_per_runtime"],
        len(rec["observed"]["user_delivery"] or ""), len(rec["observed"]["artifact"] or "")))
    print("产出已原样存下，**本文件不做任何判定**。SAVED", OUT)


if __name__ == "__main__":
    main()
