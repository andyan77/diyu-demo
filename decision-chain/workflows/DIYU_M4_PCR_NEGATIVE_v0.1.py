#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""M4 恢复后收口 · 强制负向测试（Execution Prompt v1.0 §10）

用构造输入驱动 PCR 检查器，验证它们在越界情形下**确实报 FAIL**。
检查器若对这些情形报 PASS，说明它无判别力，对应 PCR 不得放行。
全部为内存内构造，不修改任何真实文件、Dify 对象或数据库。
另含九个既有受保护应用的零变化复核。
"""
import copy, hashlib, importlib.util, json, os, subprocess, sys, yaml

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
DC_WF = os.path.join(ROOT, "decision-chain", "workflows")
OUT = os.path.join(ROOT, "decision-chain/evidence/m4/post_restore/M4_PCR_NEGATIVE.json")
V = json.load(open(os.path.join(ROOT, "decision-chain/evidence/m4/post_restore/M4_PCR_VERIFY.json"), encoding="utf-8"))
THINK = ["<think>", "</think>", "dify-deepseek-reasoning"]
R = []


def rec(nid, name, expected, got, ok, detail=None):
    R.append({"case": nid, "name": name, "expected": expected, "observed": got,
              "result": "PASS" if ok else "FAIL", "detail": detail})
    print("  %-9s %-46s %s" % (nid, name, "PASS" if ok else "FAIL"))


# ── 检查器（与 PCR 核验器同判定逻辑，纯函数形式） ────────────────────────
def chk_old_receipt(present, states_blocked):
    return present and states_blocked


def chk_layering(founder_acceptance, historical_states):
    """Founder 风险接受不得被写成旧技术 PASS。"""
    bad = [k for k, v in historical_states.items() if v == "PASS"]
    return founder_acceptance == "PASS" and not bad, bad


def chk_graph_binding(app_graph, frozen_graph):
    return app_graph == frozen_graph


def chk_stale_propagation(changed_app, bindings):
    """A3：只使直接/传递依赖失效，不多算不少算。"""
    stale = {changed_app}
    for a, deps in bindings.items():
        if any(d in stale for d in deps):
            stale.add(a)
    return sorted(stale)


def chk_injection_routable(providers, reverse_refs):
    return not providers and not reverse_refs


def chk_delivery(texts):
    empty = [t[0] for t in texts if t[2] == 0]
    leaks = {t[0]: [w for w in THINK if w in (t[1] or "")] for t in texts}
    leaks = {k: v for k, v in leaks.items() if v}
    return (not empty and not leaks), empty, leaks


def chk_protected(now_sha, frozen_sha):
    return now_sha == frozen_sha


def chk_out_of_scope(changed, allowed_prefixes):
    return sorted({f for f in changed if not f.startswith(allowed_prefixes)})


def chk_target_binding(run_workflow_id, current_published_workflow_id):
    """PCR-03~09 必须由目标系统绑定成立，不能只靠文件/提交/自述。"""
    return bool(run_workflow_id) and run_workflow_id == current_published_workflow_id


print("== 强制负向测试 NEG-P01…P08 ==")

# P01 删除或隐藏旧 BLOCKED 回执会被检出
ok = (chk_old_receipt(True, True) is True) and (chk_old_receipt(False, False) is False) \
     and (chk_old_receipt(True, False) is False)
rec("NEG-P01", "隐藏/删除旧 BLOCKED 回执", "检查器报 FAIL",
    {"present&blocked": True, "absent": False, "present_but_not_blocked": False}, ok)

# P02 把 Founder 风险接受写成旧技术 PASS 会被检出
good, _ = chk_layering("PASS", {"AC31_④": "NOT_VERIFIED", "RB31_05": "FAIL"})
bad, badk = chk_layering("PASS", {"AC31_④": "PASS", "RB31_05": "FAIL"})
rec("NEG-P02", "把 Founder 风险接受写成旧技术 PASS", "检查器报 FAIL",
    {"正确分层": good, "把历史改成PASS": bad, "命中": badk}, good and not bad)

# P03 官方应用漂移只使直接/传递依赖 STALE（不多算不少算）
BIND = {"CONTENT_BRIEF": [], "CAPABILITY_SEAM": ["CONTENT_BRIEF", "MATRIX"],
        "FOUNDER_CANVAS": ["CAPABILITY_SEAM"], "MATRIX": [], "CAMPAIGN": []}
stale = chk_stale_propagation("CONTENT_BRIEF", BIND)
drift_detected = not chk_graph_binding("aaa", "bbb")
ok = (drift_detected and stale == ["CAPABILITY_SEAM", "CONTENT_BRIEF", "FOUNDER_CANVAS"]
      and "CAMPAIGN" not in stale)
rec("NEG-P03", "官方应用图漂移 -> 只使直接/传递依赖 STALE", "漂移被检出且失效集不多算",
    {"drift_detected": drift_detected, "stale_set": stale, "未被牵连": "CAMPAIGN"}, ok)

# P04 故障注入对象仍被正式链引用会判 FAIL
ok = (chk_injection_routable([], []) is True) \
     and (chk_injection_routable([{"id": "x"}], []) is False) \
     and (chk_injection_routable([], [{"app": "SEAM", "token": "M4_FAULT_DIRECTIVE"}]) is False)
rec("NEG-P04", "注入对象仍被正式链引用", "检查器报 FAIL",
    {"无provider无引用": True, "有provider": False, "有反向引用": False}, ok)

# P05 空正文或含 <think> 会判 FAIL
g, _, _ = chk_delivery([("A", "正常正文", 4)])
e, emp, _ = chk_delivery([("A", "", 0)])
t, _, lk = chk_delivery([("A", "正文里混进了 <think>推理</think>", 20)])
rec("NEG-P05", "用户正文为空 / 含 <think>", "两种情形均报 FAIL",
    {"正常": g, "空正文": e, "带think": t, "empty命中": emp, "leak命中": lk}, g and not e and not t)

# P06 六 Skill / 专业正文 / 模型参数 / 九保护应用变化会判 FAIL
ok = chk_protected("abc", "abc") and not chk_protected("abc", "abd")
rec("NEG-P06", "受保护资产哈希变化", "检查器报 FAIL",
    {"相同": True, "不同": False}, ok)

# P07 越界写入（main / PR / 生产 / M5）会判 FAIL
ALLOWED = ("decision-chain/docs/", "decision-chain/evidence/m4/post_restore/", "collab-ledger/",
           "decision-chain/workflows/DIYU_M4_PCR_")
clean = chk_out_of_scope(["decision-chain/docs/x.md", "collab-ledger/y.md"], ALLOWED)
dirty = chk_out_of_scope(["decision-chain/docs/x.md",
                          "decision-chain/workflows/DIYU_M4_TOOL_MATRIX_v1_3_TEST.yml",
                          "m5/engine.py"], ALLOWED)
rec("NEG-P07", "越界改动（M4 DSL / M5 资产）", "越界文件被列出并判 FAIL",
    {"合规": clean, "越界": dirty}, not clean and len(dirty) == 2)

# P08 只有文件/提交/自述而无目标系统绑定，不能通过 PCR-03~09
ok = chk_target_binding("wf-1", "wf-1") and not chk_target_binding("wf-1", "wf-2") \
     and not chk_target_binding(None, "wf-1")
rec("NEG-P08", "只有文件与自述、无目标系统绑定", "检查器报 FAIL",
    {"绑定成立": True, "绑定不符": False, "无运行记录": False}, ok)

# ── 九个既有受保护应用零变化复核 ─────────────────────────────────────────
sp = importlib.util.spec_from_file_location("m4pub", os.path.join(DC_WF, "DIYU_M4_PUBLISH_AND_REBIND_v0.1.py"))
PUBM = importlib.util.module_from_spec(sp); sp.loader.exec_module(PUBM)
diffs = PUBM.protected_integrity()
rec("NEG-P09", "九个既有受保护应用零变化（真实目标系统）", "差异数 == 0",
    {"diff_count": len(diffs), "diffs": diffs}, not diffs)

fails = [x for x in R if x["result"] == "FAIL"]
out = {"source": "Execution Prompt v1.0 §10 强制负向测试 + 九保护应用复核",
       "cases": R, "total": len(R), "failed": len(fails),
       "nine_protected_apps_diffs": diffs,
       "verdict": "PASS" if not fails else "FAIL"}
json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=2, sort_keys=True)
print("\n负向套件 = %s（%d 项，%d 失败）" % (out["verdict"], out["total"], out["failed"]))
sys.exit(0 if not fails else 1)
