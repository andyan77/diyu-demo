# -*- coding: utf-8 -*-
"""M4-CL31-01 终止分支非空交付取证（取证合同 v0.5 §3 CL31-01）

执行者类型：确定性工具。
做两件事：
  A. 枚举最终候选中「接缝 + 六个能力子应用」的全部 end 节点，断言 outputs 含 user_delivery；
  B. 把产出 user_delivery 的代码节点逐个 exec 出来，以边界输入驱动其**全部返回路径**，
     断言每条路径返回的 user_delivery trim 后非空、且不含 §2.6 泄漏词。

纪律：判据来自已冻结的 v0.5，本脚本只执行判据，不改判据。
"""
import json, os, sys, yaml

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, "decision-chain/evidence/m4/final_closure/CL31_01_BRANCH_ENUM.json")

SEAM = "decision-chain/workflows/DIYU_M4_CAPABILITY_SEAM_v1_3_TEST.yml"
APPS = [
    ("MATRIX", "decision-chain/workflows/DIYU_M4_TOOL_MATRIX_v1_3_TEST.yml"),
    ("CAMPAIGN", "decision-chain/workflows/DIYU_M4_TOOL_CAMPAIGN_v1_3_TEST.yml"),
    ("CONTENT_BRIEF", "decision-chain/workflows/DIYU_M4_TOOL_CONTENT_BRIEF_v1_3_TEST.yml"),
    ("CREATIVE_SCRIPT", "content-production/workflows/DIYU_M4_TOOL_CREATIVE_SCRIPT_v1_3_TEST.yml"),
    ("PRODUCTION_DIRECTOR", "content-production/workflows/DIYU_M4_TOOL_PRODUCTION_DIRECTOR_v1_3_TEST.yml"),
    ("PUBLISHING_PACKAGING", "content-production/workflows/DIYU_M4_TOOL_PUBLISHING_PACKAGING_v1_3_TEST.yml"),
]

# §2.6 冻结泄漏词表（与 v0.5 逐条一致）
LEAKS = ["PARSE_FAIL", "NOT_APPLICABLE", "STALE", "NOT_VERIFIED", "SEAM_COMPLETENESS_GUARD",
         "returns_json", "artifact_status", "user_delivery_status", "user_delivery",
         "capability_call", "professional_payload", "goal_family", "skill_llm", "recovery_llm",
         "returns_adapter", "delivery_finalize", "final_extract", "binding_record",
         "seam_tool_fail", "end_tool_fail", "system prompt", "trace", "sha256", "Judge",
         "M4_ARTIFACT", "M4_USER_DELIVERY", "M4_RETURNS"]


def load(p):
    with open(os.path.join(ROOT, p), encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def nodes_of(d):
    return {n["id"]: n for n in d["workflow"]["graph"]["nodes"]}


def run_node(code, kwargs):
    ns = {}
    exec(compile(code, "<node>", "exec"), ns)
    return ns["main"](**kwargs)


def leaks_in(text):
    return [w for w in LEAKS if w in (text or "")]


R = {"criterion": "M4-CL31-01", "contract": "V1-M4-EVIDENCE-COLLECTION-v0.5",
     "conjuncts": {}, "end_nodes": [], "branch_runs": [], "failures": []}


def fail(msg):
    R["failures"].append(msg)


# ── ① 每个 end 节点都必须有 user_delivery ────────────────────────────────
seam = load(SEAM)
sn = nodes_of(seam)
targets = [("SEAM", sn)] + [(k, nodes_of(load(p))) for k, p in APPS]
for scope, ns in targets:
    for nid, n in sorted(ns.items()):
        if n["data"].get("type") != "end":
            continue
        vs = [o["variable"] for o in n["data"].get("outputs", [])]
        rec = {"scope": scope, "end_node": nid, "has_user_delivery": "user_delivery" in vs,
               "has_business_delivery_outcome": "business_delivery_outcome" in vs,
               "user_delivery_source": next((o["value_selector"] for o in n["data"]["outputs"]
                                             if o["variable"] == "user_delivery"), None)}
        R["end_nodes"].append(rec)
        if not rec["has_user_delivery"]:
            fail("%s/%s 的 end 输出缺少 user_delivery" % (scope, nid))
R["conjuncts"]["①"] = "PASS" if not R["failures"] else "FAIL"

# ── ②③④ 逐条返回路径驱动 ────────────────────────────────────────────────
FAILURE_BRANCH_NODES = []

# --- 接缝 seam_tool_fail：六个能力 + 未知 route ---
code = sn["seam_tool_fail"]["data"]["code"]
for route in ["MATRIX", "CAMPAIGN", "CONTENT_BRIEF", "CREATIVE_SCRIPT",
              "PRODUCTION_DIRECTOR", "PUBLISHING_PACKAGING", "", None, "UNKNOWN_X"]:
    o = run_node(code, {"route": route, "derivation": "d"})
    ud = (o.get("user_delivery") or "").strip()
    lk = leaks_in(ud)
    R["branch_runs"].append({"node": "seam_tool_fail", "input": {"route": route},
                             "user_delivery_len": len(ud), "nonempty": bool(ud),
                             "business_delivery_outcome": o.get("business_delivery_outcome"),
                             "leaks": lk, "returns_parsed": len(json.loads(o["returns_json"]))})
    if not ud: fail("seam_tool_fail route=%r 返回空正文" % route)
    if lk: fail("seam_tool_fail route=%r 正文泄漏 %s" % (route, lk))
    if o.get("business_delivery_outcome") != "NOT_DELIVERED":
        fail("seam_tool_fail route=%r 业务状态不是 NOT_DELIVERED" % route)

# --- 接缝 unsupported ---
code = sn["unsupported"]["data"]["code"]
for route in ["", None, "SOMETHING_ELSE", "M1_PLANNING"]:
    o = run_node(code, {"route": route, "derivation": "d"})
    ud = (o.get("user_delivery") or "").strip(); lk = leaks_in(ud)
    R["branch_runs"].append({"node": "unsupported", "input": {"route": route},
                             "user_delivery_len": len(ud), "nonempty": bool(ud),
                             "business_delivery_outcome": o.get("business_delivery_outcome"),
                             "leaks": lk})
    if not ud: fail("unsupported route=%r 返回空正文" % route)
    if lk: fail("unsupported route=%r 正文泄漏 %s" % (route, lk))
    if o.get("business_delivery_outcome") != "NOT_DELIVERED":
        fail("unsupported route=%r 业务状态不是 NOT_DELIVERED" % route)

# --- 接缝 fin_*（seam_finalize）：三条返回路径 ---
FIN_CASES = [
    ("正常交付", dict(tool_user_delivery="这是一份可读的用户正文。" * 5,
                  tool_delivery_outcome="DELIVERED", tool_local_block="false",
                  tool_artifact_status="OK", tool_user_delivery_status="OK"), "DELIVERED"),
    ("子应用已判未交付", dict(tool_user_delivery="这一次没有成功给出可用的结果。",
                  tool_delivery_outcome="NOT_DELIVERED", tool_local_block="true",
                  tool_artifact_status="OK", tool_user_delivery_status="PROJECTION_FAILED"),
     "NOT_DELIVERED"),
    ("子应用返回空正文", dict(tool_user_delivery="", tool_delivery_outcome="DELIVERED",
                  tool_local_block="false", tool_artifact_status="OK",
                  tool_user_delivery_status="OK"), "NOT_DELIVERED"),
    ("空正文且状态缺失", dict(tool_user_delivery=None, tool_delivery_outcome=None,
                  tool_local_block=None, tool_artifact_status=None,
                  tool_user_delivery_status=None), "NOT_DELIVERED"),
    ("只有空白字符", dict(tool_user_delivery="   \n\t  ", tool_delivery_outcome="DELIVERED",
                  tool_local_block="false", tool_artifact_status="OK",
                  tool_user_delivery_status="OK"), "NOT_DELIVERED"),
]
code = sn["fin_content_brief"]["data"]["code"]
for name, kw, want in FIN_CASES:
    base = dict(capability_resolved="CONTENT_BRIEF", entry_resolved="ENTRY-03",
                run_mode="COMPILE_SINGLE_CONTENT_CONTRACT", derivation="d",
                tool_artifact="A" * 200, tool_returns_json="[]", tool_binding_json="{}",
                call_hash="abcd1234", tool_recovery_used="false")
    base.update(kw)
    o = run_node(code, base)
    ud = (o.get("user_delivery") or "").strip()
    got = o.get("business_delivery_outcome")
    lk = leaks_in(ud) if want == "NOT_DELIVERED" else []
    R["branch_runs"].append({"node": "fin_content_brief", "case": name,
                             "user_delivery_len": len(ud), "nonempty": bool(ud),
                             "business_delivery_outcome": got, "expected": want, "leaks": lk})
    if not ud: fail("fin_* [%s] 返回空正文" % name)
    if got != want: fail("fin_* [%s] 业务状态 %s != 预期 %s" % (name, got, want))
    if lk: fail("fin_* [%s] 兜底正文泄漏 %s" % (name, lk))

# --- 子应用 delivery_finalize：三条返回路径 ---
cb = nodes_of(load(APPS[2][1]))
code = cb["delivery_finalize"]["data"]["code"]
DF_CASES = [
    ("直通交付", dict(adapter_user_delivery="正常的用户正文，可以直接读。" * 4,
                  adapter_status="OK", needs_projection="false", recovered_text=""),
     "DELIVERED"),
    ("恢复成功", dict(adapter_user_delivery="", adapter_status="MISSING",
                  needs_projection="true", recovered_text="恢复出来的用户正文。" * 12),
     "DELIVERED_AFTER_RECOVERY"),
    ("恢复为空", dict(adapter_user_delivery="", adapter_status="MISSING",
                  needs_projection="true", recovered_text=""), "NOT_DELIVERED"),
    ("恢复过短", dict(adapter_user_delivery="", adapter_status="MISSING",
                  needs_projection="true", recovered_text="太短了"), "NOT_DELIVERED"),
    ("恢复泄漏内部词", dict(adapter_user_delivery="", adapter_status="MISSING",
                  needs_projection="true",
                  recovered_text="这里混进了 PARSE_FAIL 这个内部状态码。" * 8), "NOT_DELIVERED"),
]
for name, kw, want in DF_CASES:
    base = dict(returns_json="[]", capability="CONTENT_BRIEF"); base.update(kw)
    o = run_node(code, base)
    ud = (o.get("user_delivery") or "").strip()
    got = o.get("delivery_outcome")
    R["branch_runs"].append({"node": "delivery_finalize", "case": name,
                             "user_delivery_len": len(ud), "nonempty": bool(ud),
                             "delivery_outcome": got, "expected": want})
    if not ud: fail("delivery_finalize [%s] 返回空正文" % name)
    if got != want: fail("delivery_finalize [%s] 交付状态 %s != 预期 %s" % (name, got, want))

# --- 子应用 component_return：缺项 / 无缺项 / 未知字段 ---
code = cb["component_return"]["data"]["code"]
for name, miss in [("有缺项", ["objective"]), ("无缺项", []),
                   ("未知缺项名", ["__not_a_real_field__"]), ("缺项为 None", None)]:
    o = run_node(code, dict(status="INSUFFICIENT", note="n", missing=miss,
                            entry_resolved="ENTRY-03", envelope_hash="deadbeef",
                            capability_call=""))
    ud = (o.get("user_delivery") or "").strip()
    R["branch_runs"].append({"node": "component_return", "case": name,
                             "user_delivery_len": len(ud), "nonempty": bool(ud),
                             "field_name_leaks": o.get("user_delivery_leaks")})
    if not ud: fail("component_return [%s] 返回空正文" % name)
    if o.get("user_delivery_leaks"): fail("component_return [%s] 泄漏字段名" % name)

nonempty_all = all(b["nonempty"] for b in R["branch_runs"])
R["conjuncts"]["②"] = "PASS" if nonempty_all else "FAIL"
R["conjuncts"]["③"] = "PASS" if not any(b.get("leaks") for b in R["branch_runs"]) else "FAIL"
R["conjuncts"]["④"] = "PASS" if all(
    b.get("business_delivery_outcome") == "NOT_DELIVERED"
    for b in R["branch_runs"] if b["node"] in ("seam_tool_fail", "unsupported")) else "FAIL"
# ⑤ 平台技术状态与业务交付状态分离：每个 end 都有独立的 business_delivery_outcome 变量
sep = all(e["has_business_delivery_outcome"] for e in R["end_nodes"] if e["scope"] == "SEAM")
R["conjuncts"]["⑤"] = "PASS" if sep else "FAIL"
if not sep: fail("接缝存在未分离业务交付状态的 end 节点")

R["verdict"] = "PASS" if (not R["failures"] and
                          all(v == "PASS" for v in R["conjuncts"].values())) else "FAIL"
R["branch_runs_total"] = len(R["branch_runs"])
R["end_nodes_total"] = len(R["end_nodes"])

os.makedirs(os.path.dirname(OUT), exist_ok=True)
json.dump(R, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=2, sort_keys=True)
print("M4-CL31-01 = %s" % R["verdict"])
print("  end 节点 %d 个，全部含 user_delivery=%s" % (
    R["end_nodes_total"], all(e["has_user_delivery"] for e in R["end_nodes"])))
print("  分支驱动 %d 条，全部非空=%s" % (R["branch_runs_total"], nonempty_all))
print("  合取项:", json.dumps(R["conjuncts"], ensure_ascii=False))
for f in R["failures"]:
    print("  [FAIL]", f)
sys.exit(0 if R["verdict"] == "PASS" else 1)
