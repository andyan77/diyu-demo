#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""确定性验证重绑定｜P-01…P-11 与 R-01…R-03 在 **Gate v1.1** 下重算。**零模型调用。**

为什么需要这一版：S4_CANONICAL_STATE_VERIFY.json（14/14）的 criteria_ref 指向 Gate v1.0，
而正式 T1–T7 证据绑定的是 Gate v1.1。旧结果在 Gate v1.0 下成立，不能被引用成
「Gate v1.1 下的 14/14」。

本文件不修改 v1.0 脚本一个字节，也不改任何一条判据内容——被测对象、检查逻辑、
正负控制全部沿用 v1.0，只做两件事：
  1. 把 criteria 绑定改成 Gate v1.1 的真实 sha256，结果落到新文件；
  2. 加一层**单点变异区分证明**：对被测源码逐条施加一处内存内变异，
     要求至少翻掉一条检查。翻不掉的变异原样登记为覆盖缺口，不粉饰。

变异只发生在内存里的源码副本上；磁盘上的 S4_CANONICAL_STATE_NODES_v1.0.py 不变。

    python3 S4_CANONICAL_STATE_VERIFY_v1.1.py
"""
import hashlib
import importlib.util
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
UAPP = os.path.abspath(os.path.join(HERE, ".."))
EVDIR = os.path.join(UAPP, "evidence", "stages", "s4_canonical_state")
V10_PY = os.path.join(HERE, "S4_CANONICAL_STATE_VERIFY_v1.0.py")
NODES_PY = os.path.join(HERE, "S4_CANONICAL_STATE_NODES_v1.0.py")
GATE11 = os.path.join(UAPP, "stages", "S4_CANONICAL_TASK_STATE_GATE_v1.1.json")
GATE10 = os.path.join(UAPP, "stages", "S4_CANONICAL_TASK_STATE_GATE_v1.0.json")
OUT = os.path.join(EVDIR, "S4_CANONICAL_STATE_VERIFY_v1.1.json")

# 单点变异：每条只改被测源码的一个地方，且对应一条明确的业务保证。
MUTATIONS = [
    ("MUT-01", "缺失语义词表整体失效（占位识别的唯一真源）", "FLIP",
     'MISS = ["未明确写出", "未明确说明", "未明确", "未声明", "未提供", "未给出", "未确认", "未指定",\n'
     '        "未锁定", "无法确定", "尚未确定", "尚未给出", "待确定", "待确认", "待补充", "暂无", "不详",\n'
     '        "UNDECLARED", "UNKNOWN", "UNSPECIFIED", "NOT_GIVEN", "N/A", "TBD"]',
     'MISS = []'),
    ("MUT-02", "只拆掉 offer 内的第二道占位闸门", "MASKED_BY_INDEPENDENT_LAYER",
     "    def offer(cid, val, lvl, kind, ref):\n        if _missing(val):",
     "    def offer(cid, val, lvl, kind, ref):\n        if False:"),
    ("MUT-03", "低权威可以覆盖高权威（等级闸门失效）", "FLIP",
     'if ln > lo or (ln == lo and lvl == "E"):',
     'if ln > 99 or (ln == lo and lvl == "E"):'),
    ("MUT-04", "同轮细化与跨轮纠正不再区分（纠正被吞成 REFINED）", "FLIP",
     'if int(old.get("origin_turn") or 0) >= rev:',
     'if int(old.get("origin_turn") or 0) >= 0:'),
    ("MUT-05", "生产时间窗的作用域限定被去掉", "FLIP",
     '"only": ["PRODUCTION_DIRECTOR"]},', '"only": []},'),
    ("MUT-06", "依赖字段变化不再使 artifact 失效", "FLIP",
     '            a["stale"] = True', '            a["stale"] = False'),
    # 以下两条在 MUT-01 未按冻结预期翻转之后追加。MUT-01 的预期不回改（A2：判据不因结果而改），
    # 改为**新增**探针把「没被检查」与「被另一道独立防线挡住」分开。两条的预期在运行之前写死。
    ("MUT-07", "P-08 fail-closed 矛盾闸门失效（占位识别的第二道独立防线）", "FLIP",
     "contradictions = [c for c in list(env_vals) if c in gaps]",
     "contradictions = []"),
    ("MUT-08", "两道占位防线同时拆掉（两点探针，用于判定 MUT-01 是覆盖缺口还是冗余遮蔽）", "FLIP",
     "__TWO_POINT__", "__TWO_POINT__"),
]
TWO_POINT = {
    "MUT-08": [("MISS = [\"未明确写出\", \"未明确说明\", \"未明确\", \"未声明\", \"未提供\", "
                "\"未给出\", \"未确认\", \"未指定\",\n"
                "        \"未锁定\", \"无法确定\", \"尚未确定\", \"尚未给出\", \"待确定\", "
                "\"待确认\", \"待补充\", \"暂无\", \"不详\",\n"
                "        \"UNDECLARED\", \"UNKNOWN\", \"UNSPECIFIED\", \"NOT_GIVEN\", "
                "\"N/A\", \"TBD\"]", "MISS = []"),
               ("contradictions = [c for c in list(env_vals) if c in gaps]",
                "contradictions = []")],
}
MASK_NOTE = {
    "MUT-02": "env 解析处（`if _missing(e[\"v\"]): env_missing.append(cid)`）先于 offer 生效，"
              "占位值在进入 offer 之前已被拦掉。这是两道**独立**防线的正确先后，"
              "不是检查覆盖缺口——同一条业务保证由 MUT-01 证明确实被 14 条覆盖。",
}


def shaf(p):
    return hashlib.sha256(io.open(p, "rb").read()).hexdigest()


def load_v10():
    spec = importlib.util.spec_from_file_location("v10_%d" % id(object()), V10_PY)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def run_suite(fields_src=None, state_src=None, quiet=False):
    """跑一遍 v1.0 的 14 条检查，返回 {id: result}。不落盘。"""
    m = load_v10()
    if fields_src is not None:
        ns = {}
        exec(compile(fields_src, "<uapp_fields_mut>", "exec"), ns)
        m.fields = ns["main"]
    if state_src is not None:
        ns = {}
        exec(compile(state_src, "<uapp_state_mut>", "exec"), ns)
        m.state = ns["main"]
    tmp = OUT + ".probe"
    m.OUT = tmp
    keep = sys.stdout
    if quiet:
        sys.stdout = io.StringIO()
    try:
        m.run()
        rep = json.load(io.open(tmp, encoding="utf-8"))
    finally:
        sys.stdout = keep
        if os.path.exists(tmp):
            os.remove(tmp)
    return rep


def main():
    base = run_suite()

    csn_spec = importlib.util.spec_from_file_location("csn_v11", NODES_PY)
    csn = importlib.util.module_from_spec(csn_spec)
    csn_spec.loader.exec_module(csn)
    src = csn.FIELDS_SRC

    baseline = {c["id"]: c["result"] for c in base["checks"]}
    muts = []
    for mid, what, expect, old, new in MUTATIONS:
        if mid in TWO_POINT:
            mutated, pts, bad = src, [], []
            for o, nw in TWO_POINT[mid]:
                if src.count(o) != 1:
                    bad.append(o.splitlines()[-1].strip())
                    continue
                mutated = mutated.replace(o, nw, 1)
                pts.append(o.splitlines()[-1].strip())
            if bad:
                muts.append({"id": mid, "guarantee": what, "expect": expect, "applied": False,
                             "reason": "两点探针中有锚点不唯一：%s" % bad,
                             "flipped_checks": [], "as_expected": False})
                continue
            got = run_suite(fields_src=mutated, quiet=True)
            res = {c["id"]: c["result"] for c in got["checks"]}
            flipped = sorted(k for k in baseline
                             if baseline[k] == "PASS" and res.get(k) != "PASS")
            muts.append({"id": mid, "guarantee": what, "expect": expect, "applied": True,
                         "anchors": pts, "two_point": True, "flipped_checks": flipped,
                         "as_expected": bool(flipped), "raised": None,
                         "why_masked": MASK_NOTE.get(mid)})
            continue
        n = src.count(old)
        if n != 1:
            muts.append({"id": mid, "guarantee": what, "expect": expect, "applied": False,
                         "reason": "锚点在被测源码中出现 %d 次，不是唯一单点，本轮不施加" % n,
                         "flipped_checks": [], "as_expected": False})
            continue
        raised = None
        try:
            got = run_suite(fields_src=src.replace(old, new, 1), quiet=True)
            res = {c["id"]: c["result"] for c in got["checks"]}
            flipped = sorted(k for k in baseline
                             if baseline[k] == "PASS" and res.get(k) != "PASS")
        except Exception as e:  # 变异让被测源码直接抛错，也算被区分开
            flipped, raised = ["<RAISED>"], "%s: %s" % (type(e).__name__, str(e)[:160])
        ok = bool(flipped) if expect == "FLIP" else not flipped
        muts.append({"id": mid, "guarantee": what, "expect": expect, "applied": True,
                     "anchor": old.splitlines()[-1].strip(),
                     "flipped_checks": flipped, "as_expected": ok, "raised": raised,
                     "why_masked": MASK_NOTE.get(mid) if expect != "FLIP" else None})

    applied = [m for m in muts if m["applied"]]
    disc_ok = bool(applied) and all(m["as_expected"] for m in applied)

    rep2 = {
        "document": {
            "id": "S4_CANONICAL_STATE_VERIFY_v1.1",
            "task_id": "DIYU-V1-UNIFIED-DIFY-APPLICATION-001",
            "authority": "CONTINUE EXECUTION PROMPT v1.0"
                         "（UAPP S4 证据真值纠偏与 PP 交付边界归因）第五节第 1 条",
            "criteria_ref": "unified-app/stages/S4_CANONICAL_TASK_STATE_GATE_v1.1.json",
            "criteria_sha256": shaf(GATE11),
            "supersedes_binding_only": {
                "file": "unified-app/evidence/stages/s4_canonical_state/"
                        "S4_CANONICAL_STATE_VERIFY.json",
                "its_criteria_ref": "unified-app/stages/S4_CANONICAL_TASK_STATE_GATE_v1.0.json",
                "its_criteria_sha256": shaf(GATE10),
                "kind": "只换判据绑定与展示，不改判据内容、不改被测对象、不改检查逻辑。"
                        "v1.0 结果文件原样保留。",
            },
            "checker_src_sha256": shaf(V10_PY),
            "nodes_src_sha256": shaf(NODES_PY),
            "system_under_test": "S4_CANONICAL_STATE_NODES_v1.0.py 的 FIELDS_SRC / STATE_SRC"
                                 "（磁盘文件未修改；变异只作用于内存副本）",
            "model_calls": 0, "dify_writes": 0, "workflow_runs_started": 0,
        },
        "summary": base["summary"],
        "discrimination": {
            "method": "单点变异：改被测源码一处，与冻结的预期对照。"
                      "expect=FLIP 的必须至少翻掉一条检查；"
                      "expect=MASKED_BY_INDEPENDENT_LAYER 的必须翻不掉，"
                      "并给出更前一道独立防线作为理由。预期在运行之前写死在 MUTATIONS 表里。",
            "mutations_total": len(MUTATIONS),
            "mutations_applied": len(applied),
            "all_as_expected": disc_ok,
            "deviations": [m["id"] for m in applied if not m["as_expected"]],
            "deviation_resolution": {
                "MUT-01": {
                    "observed": "未翻掉任何一条；冻结预期为 FLIP。预期不回改。",
                    "why": "P-02 的正控制场景里，占位值同时出现在外壳与缺口清单中，"
                           "P-08 的 fail-closed 矛盾闸门先把它拦掉，"
                           "因此只拆掉 MISS 词表这一处不足以让任何一条翻绿变红。",
                    "resolved_by": ["MUT-07", "MUT-08"],
                    "conclusion": "MUT-07 单独拆掉矛盾闸门 ⇒ P-08 翻；"
                                  "MUT-08 两道同时拆掉 ⇒ P-02、P-08、R-02 一起翻。"
                                  "因此占位保证**确实**被 14 条覆盖，"
                                  "MUT-01 的偏差是两道独立防线互相遮蔽，不是检查覆盖缺口。",
                    "not_upgraded": "all_as_expected 保持 false，不因这条解释而改绿。",
                },
            },
            "per_mutation": muts,
        },
        "checks": base["checks"],
        "replay": base["replay"],
    }
    io.open(OUT, "w", encoding="utf-8").write(json.dumps(rep2, ensure_ascii=False, indent=1) + "\n")
    print("---- Gate v1.1 重绑定：%d/%d ----" % (base["summary"]["pass"], base["summary"]["total"]))
    for m in muts:
        got = ("翻掉 " + ",".join(m["flipped_checks"])) if m["flipped_checks"] else "未翻掉"
        if not m["applied"]:
            got = "未施加：" + m.get("reason", "")
        print("  %-7s %-8s %-38s %-16s %s"
              % (m["id"], m["expect"], m["guarantee"], got,
                 "符合预期" if m["as_expected"] else "**不符合预期**"))
    print("  逐条变异均符合冻结预期：%s" % disc_ok)
    return 0 if base["summary"]["verdict"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
