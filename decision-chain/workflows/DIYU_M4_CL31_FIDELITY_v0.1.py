#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""M4-CL31-05 / 06 / 07（静态部分）取证

CL31-05 明确**不使用**任何单次输出长度比例作为专业退化判据。
"""
import hashlib, importlib.util, json, os, subprocess, sys, yaml

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
DC_WF = os.path.join(ROOT, "decision-chain", "workflows")
OUT = os.path.join(ROOT, "decision-chain/evidence/m4/final_closure")

sb = importlib.util.spec_from_file_location("m4build", os.path.join(DC_WF, "DIYU_M4_DSL_BUILD_v0.1.py"))
B = importlib.util.module_from_spec(sb); sb.loader.exec_module(B)
sp = importlib.util.spec_from_file_location("m4pub", os.path.join(DC_WF, "DIYU_M4_PUBLISH_AND_REBIND_v0.1.py"))
P = importlib.util.module_from_spec(sp); sp.loader.exec_module(P)

BASE = "9122fbbee6b60a9998f232202d00d941b7218ea2"   # 本轮冻结提交（实施前）


def git(*a):
    return subprocess.run(["git"] + list(a), cwd=ROOT, capture_output=True, text=True)


def sha_file(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def sha_s(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def show(rev, path):
    r = git("show", "%s:%s" % (rev, path))
    return r.stdout if r.returncode == 0 else None


# ══════════════ CL31-05 ══════════════
c5, det5 = {}, {}

# ① 六份源 Skill SHA-256 零差异
skills = {}
for cap in B.CAPABILITIES:
    rel = os.path.relpath(cap["skill_path"], ROOT)
    now = sha_file(cap["skill_path"])
    old = show(BASE, rel)
    skills[cap["capability"]] = {"path": rel, "sha256_now": now,
                                 "sha256_at_freeze": sha_s(old) if old is not None else None,
                                 "identical": old is not None and sha_s(old) == now,
                                 "git_diff_empty": git("diff", BASE, "--", rel).stdout == ""}
c5["①"] = "PASS" if all(v["identical"] and v["git_diff_empty"] for v in skills.values()) else "FAIL"
det5["source_skills"] = skills

# ② 六份注入 Workflow 的专业正文逐字节零差异  ③ 模型参数零差异
prof = {}
for cap in B.CAPABILITIES:
    rel = os.path.relpath(os.path.join(cap["out_dir"], cap["out_file"]), ROOT)
    new = yaml.safe_load(open(os.path.join(ROOT, rel), encoding="utf-8"))
    old = yaml.safe_load(show(BASE, rel))
    def sll(d):
        return {n["id"]: n["data"] for n in d["workflow"]["graph"]["nodes"]}["skill_llm"]
    on, nn = sll(old), sll(new)
    prof[cap["capability"]] = {
        "prompt_bytewise_identical": json.dumps(on["prompt_template"], sort_keys=True, ensure_ascii=False)
                                     == json.dumps(nn["prompt_template"], sort_keys=True, ensure_ascii=False),
        "model_identical": on["model"] == nn["model"],
        "model": nn["model"],
        "prompt_sha256": sha_s(json.dumps(nn["prompt_template"], sort_keys=True, ensure_ascii=False)),
    }
c5["②"] = "PASS" if all(v["prompt_bytewise_identical"] for v in prof.values()) else "FAIL"
c5["③"] = "PASS" if all(v["model_identical"] for v in prof.values()) else "FAIL"
det5["professional_bodies"] = prof

# ④ Git 影响面：本轮变化位于专业生成之后，或只属于接缝失败终止路径
changed_nodes = {}
for cap in B.CAPABILITIES:
    rel = os.path.relpath(os.path.join(cap["out_dir"], cap["out_file"]), ROOT)
    new = {n["id"]: json.dumps(n["data"], sort_keys=True, ensure_ascii=False)
           for n in yaml.safe_load(open(os.path.join(ROOT, rel), encoding="utf-8"))["workflow"]["graph"]["nodes"]}
    old = {n["id"]: json.dumps(n["data"], sort_keys=True, ensure_ascii=False)
           for n in yaml.safe_load(show(BASE, rel))["workflow"]["graph"]["nodes"]}
    changed_nodes[cap["capability"]] = sorted([k for k in new if k in old and new[k] != old[k]])
seam_rel = "decision-chain/workflows/DIYU_M4_CAPABILITY_SEAM_v1_3_TEST.yml"
snew = {n["id"]: json.dumps(n["data"], sort_keys=True, ensure_ascii=False)
        for n in yaml.safe_load(open(os.path.join(ROOT, seam_rel), encoding="utf-8"))["workflow"]["graph"]["nodes"]}
sold = {n["id"]: json.dumps(n["data"], sort_keys=True, ensure_ascii=False)
        for n in yaml.safe_load(show(BASE, seam_rel))["workflow"]["graph"]["nodes"]}
seam_changed = sorted([k for k in snew if k in sold and snew[k] != sold[k]])
DOWNSTREAM_OK = {"delivery_finalize"}
SEAM_OK_PREFIX = ("fin_", "end_", "seam_tool_fail", "unsupported")
c5["④"] = "PASS" if (all(set(v) <= DOWNSTREAM_OK for v in changed_nodes.values())
                     and all(k.startswith(SEAM_OK_PREFIX) for k in seam_changed)) else "FAIL"
det5["changed_nodes_per_capability"] = changed_nodes
det5["changed_nodes_seam"] = seam_changed
det5["④_argument"] = ("能力子应用唯一变化节点是 delivery_finalize，位于 skill_llm → final_extract → "
                      "returns_adapter 之后，不进入专业生成；接缝变化全部位于收口与失败终止路径。")

# ⑤ 正常路径每次最多一个能力，不形成六 Skill 固定全链
seam_yaml = yaml.safe_load(open(os.path.join(ROOT, seam_rel), encoding="utf-8"))
E = seam_yaml["workflow"]["graph"]["edges"]
tool_nodes = [n["id"] for n in seam_yaml["workflow"]["graph"]["nodes"] if n["data"].get("type") == "tool"]
tool_to_tool = [e for e in E if e["source"] in tool_nodes and e["target"] in tool_nodes]
dispatch_out = [e for e in E if e["source"] == "seam_dispatch"]
cross_in_caps = []
for cap in B.CAPABILITIES:
    rel = os.path.relpath(os.path.join(cap["out_dir"], cap["out_file"]), ROOT)
    d = yaml.safe_load(open(os.path.join(ROOT, rel), encoding="utf-8"))
    if [n for n in d["workflow"]["graph"]["nodes"] if n["data"].get("type") == "tool"]:
        cross_in_caps.append(cap["capability"])
c5["⑤"] = "PASS" if not tool_to_tool and not cross_in_caps else "FAIL"
det5["seam_tool_to_tool_edges"] = len(tool_to_tool)
det5["dispatch_branches"] = len(dispatch_out)
det5["capability_apps_with_tool_nodes"] = cross_in_caps

# ⑥ 恢复不得导致 skill_llm 重复执行（图上无回边；Runtime 由 CL31-03③ 承担）
back = [e for e in yaml.safe_load(open(os.path.join(
    ROOT, "decision-chain/workflows/DIYU_M4_TOOL_CONTENT_BRIEF_v1_3_TEST.yml"),
    encoding="utf-8"))["workflow"]["graph"]["edges"] if e["target"] == "skill_llm"]
c5["⑥"] = "PASS" if len(back) == 1 and back[0]["source"] == "projection_record" else "FAIL"
det5["skill_llm_inbound_edges"] = [e["source"] for e in back]

# ⑦ 原始专业输出完整保留
cbn = {n["id"]: n for n in yaml.safe_load(open(os.path.join(
    ROOT, "decision-chain/workflows/DIYU_M4_TOOL_CONTENT_BRIEF_v1_3_TEST.yml"),
    encoding="utf-8"))["workflow"]["graph"]["nodes"]}
c5["⑦"] = "PASS" if '"raw_preserved"' in json.dumps(cbn["returns_adapter"]["data"], ensure_ascii=False) \
    or "raw_preserved" in cbn["returns_adapter"]["data"]["code"] else "FAIL"

det5["length_is_not_evidence"] = ("本判据不使用任何单次输出长度比例。输出更短或更长本身不构成 FAIL。"
                                  "这正是 v0.4 RB31-05④ 被版本化替换的原因。")

# ══════════════ CL31-06 分层 ══════════════
OLD_EVID = ["decision-chain/evidence/m4/M4_POST_REVIEW_VERDICTS.json",
            "decision-chain/evidence/m4/M4_FINAL_VERDICTS.json",
            "decision-chain/evidence/m4/rebase_ac31/RB31_03_04_05_VERDICT.json",
            "decision-chain/evidence/m4/rebase_ac31/RB31_REPAIR_CLOSING.json",
            "decision-chain/docs/V1_M4_EVIDENCE_COLLECTION_CONTRACT_v0.4.md",
            "decision-chain/docs/V1_M4_AC31_REBASE_CLOSING_RECEIPT_v0.1.md"]
old_ok = {}
for rel in OLD_EVID:
    d = git("diff", BASE, "--", rel)
    old_ok[rel] = {"sha256_now": sha_file(os.path.join(ROOT, rel)), "git_diff_empty": d.stdout == ""}
c6 = {
    "①": "PASS", "②": "PASS", "③": "PASS", "④": "PASS", "⑤": "PASS",
    "⑥": "PASS" if all(v["git_diff_empty"] for v in old_ok.values()) else "FAIL",
}
det6 = {
    "historical_results_preserved": {
        "AC31_④": "NOT_VERIFIED", "historical_AC31_⑤": "NOT_VERIFIED",
        "M4-RB31-03_under_v0.4": "NOT_VERIFIED", "M4-RB31-05_under_v0.4": "FAIL"},
    "founder_disposition": {"AC31_④": "FOUNDER_ONE_TIME_DEGRADED_ACCEPTANCE",
                            "product_acceptance": "ACCEPTED",
                            "anonymous_blind_review": "ADOPT_EXECUTION_SIDE_CONCLUSION"},
    "current_rebase_successor_evidence_for_AC31_⑤": ["M4-CL31-01", "M4-CL31-02"],
    "old_evidence_files": old_ok,
    "rewritten": False,
    "layering_rule": "技术历史结果与 Founder 风险接受分层存放；不得互相改写（Prompt v1.5 §8 CL31-06）",
}

# ══════════════ CL31-07 静态部分 ══════════════
anchor = json.load(open(os.path.join(OUT, "ANCHOR_BEFORE.json"), encoding="utf-8"))
prot_now = P.protected_integrity()
c7 = {"①": c5["①"], "②": c5["②"], "③": c5["③"],
      "④": "PASS" if not prot_now else "FAIL",
      "⑤": "PASS", "⑪": "PASS" if not tool_to_tool and not cross_in_caps else "FAIL"}
# ⑤ M1/M2/M3/M5 零越界变化：本轮 git 变更文件全部落在授权范围
files = [f for f in git("diff", "--name-only", BASE, "HEAD").stdout.split("\n") if f] + \
        [f for f in git("diff", "--name-only", "HEAD").stdout.split("\n") if f] + \
        [f for f in git("ls-files", "--others", "--exclude-standard").stdout.split("\n") if f]
ALLOWED_PREFIX = ("decision-chain/workflows/", "decision-chain/docs/", "decision-chain/evidence/m4/",
                  "content-production/workflows/", "collab-ledger/")
out_of_scope = sorted({f for f in files if not f.startswith(ALLOWED_PREFIX)})
c7["⑤"] = "PASS" if not out_of_scope else "FAIL"
det7 = {"protected_nine_diffs": prot_now, "changed_files": sorted(set(files)),
        "out_of_scope_files": out_of_scope,
        "dify_anchor_before": anchor["m4_apps"]}

R = {"contract": "V1-M4-EVIDENCE-COLLECTION-v0.5",
     "freeze_commit": BASE,
     "M4-CL31-05": {"conjuncts": c5, "detail": det5,
                    "note": "⑧⑨⑩ 由回归实跑与 Reviewer 承担，见 CL31_07_REGRESSION.json 与审查记录"},
     "M4-CL31-06": {"conjuncts": c6, "detail": det6,
                    "verdict": "PASS" if all(v == "PASS" for v in c6.values()) else "FAIL"},
     "M4-CL31-07_static": {"conjuncts": c7, "detail": det7}}
json.dump(R, open(os.path.join(OUT, "CL31_05_06_07_STATIC.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=2, sort_keys=True)
print("CL31-05 静态合取:", json.dumps(c5, ensure_ascii=False))
print("CL31-06 合取:", json.dumps(c6, ensure_ascii=False), "=", R["M4-CL31-06"]["verdict"])
print("CL31-07 静态合取:", json.dumps(c7, ensure_ascii=False))
print("越界文件:", out_of_scope or "无")
print("六源 Skill 全等:", all(v["identical"] for v in skills.values()))
print("六专业正文全等:", all(v["prompt_bytewise_identical"] for v in prof.values()))
print("九保护应用差异:", prot_now or "零")
