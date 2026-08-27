#!/usr/bin/env python3
"""独立复算 Founder 七场景实测包（Execution Prompt v1.2 §5.2 第 5、8 项）。零模型调用。

不信任生成脚本的自述，全部从**冻结件与真源**重算：

  V1 七条输入文件的 sha256 == FREEZE_MANIFEST 记录值
  V2 逐字场景（S1/S3/S4/S5/S6）的 account_context 与 user_request
     与来源运行记录**逐字节相同**
  V3 机械改写场景（S2/S7）的差异**恰好**是声明的那几处，一处不多
  V4 loaded_references 由 manifest.build_refs 现场重建后逐字节相同
  V5 候选绑定（App、已发布版本、图哈希、系统提示词哈希、SKILL 哈希）与**线上实物**一致
  V6 A5 两两消融：任意一个场景的验收目的都不被另一个单独场景包住
  V7 七条 = 7，且每条只有一个主要验收目的
"""
import difflib
import hashlib
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
WT = os.path.dirname(os.path.dirname(TOOLS))
sys.path.insert(0, TOOLS)
PACK = os.path.join(WT, "account-operations/founder-pack-v152")
EV = os.path.join(WT, "account-operations/evidence")
SKILL = os.path.join(WT, "account-operations/skills/operating-one-account/SKILL.md")

VERBATIM = {"S1", "S3", "S4", "S5", "S6"}
COMPILED = {"S2", "S7"}
# S2 声明的机械改写：account_context 恰好两行替换，user_request 整条新写
S2_SUBS = [("primary_objective: 长期价值", "primary_objective: 到店（本周期主要目标）"),
           ("secondary_objectives: 未提供",
            "secondary_objectives: GMV（次要，有限次）；线索（次要，有限次）")]


def sha(t):
    return hashlib.sha256(t.encode("utf-8")).hexdigest()


def rd(p):
    return io.open(p, encoding="utf-8", newline="").read()


def src_wi(rel):
    return json.load(io.open(os.path.join(WT, rel), encoding="utf-8"))["workflow_inputs"]


def main():
    m = json.load(io.open(os.path.join(PACK, "FREEZE_MANIFEST.json"), encoding="utf-8"))
    scen = {s["id"]: s for s in m["scenarios"]}
    rep = {"what": "Founder 七场景实测包独立复算", "executor_model_calls": 0}

    # -------- V1 --------
    bad = []
    for sid, s in scen.items():
        for field, f in s["inputs"].items():
            t = rd(os.path.join(WT, f["path"]))
            if sha(t) != f["sha256"] or len(t) != f["chars"]:
                bad.append(f"{sid}/{field}")
    rep["V1_input_file_hashes"] = {"mismatched": bad, "pass": not bad}

    # -------- V2 --------
    bad = []
    for sid in sorted(VERBATIM):
        s = scen[sid]
        wi = src_wi(s["source"]["file"])
        for field in ("account_context", "user_request"):
            if rd(os.path.join(WT, s["inputs"][field]["path"])) != wi[field]:
                bad.append(f"{sid}/{field}")
    rep["V2_verbatim_byte_identical"] = {"checked": sorted(VERBATIM), "mismatched": bad,
                                         "pass": not bad}

    # -------- V3 --------
    d3 = {}
    s2 = scen["S2"]
    base = src_wi(s2["source"]["file"])["account_context"]
    want = base
    for a, b in S2_SUBS:
        assert want.count(a) == 1
        want = want.replace(a, b)
    got = rd(os.path.join(WT, s2["inputs"]["account_context"]["path"]))
    diff = [l for l in difflib.unified_diff(base.split("\n"), got.split("\n"), n=0, lineterm="")
            if l[:1] in "+-" and not l.startswith(("+++", "---"))]
    d3["S2"] = {"equals_declared_substitution": got == want,
                "changed_lines": diff,
                "changed_line_count": len(diff),
                "expected_line_count": 2 * len(S2_SUBS),
                "pass": got == want and len(diff) == 2 * len(S2_SUBS)}
    s7 = scen["S7"]
    base7 = src_wi(s7["source"]["file"])["account_context"]
    got7 = rd(os.path.join(WT, s7["inputs"]["account_context"]["path"]))
    d3["S7"] = {"account_context_byte_identical_to_source": got7 == base7, "pass": got7 == base7}
    # 两条新写的 user_request 不得含任何业务事实数字（价格/库存/尺码等具体事实）
    import re
    fact_pat = re.compile(r"\d{3,}\s*元|\d+\s*件现货|\d+\s*码|羊毛混纺|燕麦|藏青")
    leaks = {sid: fact_pat.findall(rd(os.path.join(WT, scen[sid]["inputs"]["user_request"]["path"])))
             for sid in sorted(COMPILED)}
    d3["no_new_business_facts_in_written_requests"] = {
        "hits": {k: v for k, v in leaks.items() if v},
        "pass": not any(leaks.values())}
    d3["pass"] = all(v["pass"] for v in d3.values() if isinstance(v, dict))
    rep["V3_compiled_delta_exact"] = d3

    # -------- V4 --------
    from manifest import build_refs
    ft = rd(os.path.join(WT, "account-operations/skills/operating-one-account/"
                             "references/fashion-and-market.md"))
    refs = build_refs(True, ft)
    bad = [sid for sid in scen
           if rd(os.path.join(WT, scen[sid]["inputs"]["loaded_references"]["path"])) != refs]
    rep["V4_manifest_rebuild"] = {"mismatched": bad, "sha256": sha(refs),
                                  "matches_freeze_manifest": sha(refs) == m["loaded_references_sha256"],
                                  "pass": not bad and sha(refs) == m["loaded_references_sha256"]}

    # -------- V5 --------
    from dify_client import Console
    b = m["binding"]
    c = Console()
    st, pub = c.call("GET", f"/console/api/apps/{b['dify_app_id']}/workflows/publish")
    assert st == 200, st
    live_prompt = None
    for n in pub["graph"]["nodes"]:
        if n["data"]["type"] == "llm" and n["id"] == "operating_one_account_llm":
            live_prompt = "".join(p["text"] for p in n["data"]["prompt_template"]
                                  if p.get("role") == "system")
    checks = {
        "published_version": pub.get("version") == b["published_version"],
        "published_marked_name": pub.get("marked_name") == b["published_marked_name"],
        "published_graph_hash": pub.get("hash") == b["published_graph_sha256"],
        "system_prompt_sha256": sha(live_prompt or "") == b["published_system_prompt_sha256"],
        "skill_md_sha256": hashlib.sha256(io.open(SKILL, "rb").read()).hexdigest() == b["skill_md_sha256"],
        "system_prompt_starts_with_skill": (live_prompt or "").startswith(rd(SKILL)),
        "graph_shape": (len(pub["graph"]["nodes"]) == 7 and len(pub["graph"]["edges"]) == 6),
        "no_http_request_or_tool_node": not [n for n in pub["graph"]["nodes"]
                                             if n["data"]["type"] in ("http-request", "tool")],
    }
    rep["V5_live_binding"] = {"checks": checks, "transport": c.transport,
                              "pass": all(checks.values())}

    # -------- V6 A5 两两消融 --------
    def sig(s):
        return set(s["hard_failures_probed"]) | {s["purpose"]}
    subsumed = []
    for i in scen:
        for j in scen:
            if i != j and sig(scen[i]) <= sig(scen[j]):
                subsumed.append(f"{i} ⊆ {j}")
    rep["V6_pairwise_ablation"] = {"subsumed_pairs": subsumed, "pass": not subsumed}

    # -------- V7 --------
    rep["V7_shape"] = {"set_size": len(scen), "runs_per_input": m["runs_per_input"],
                       "one_purpose_each": all(isinstance(s["purpose"], str) and s["purpose"]
                                               for s in scen.values()),
                       "pass": len(scen) == 7 and m["runs_per_input"] == 1}

    rep["ALL_PASS"] = all(v["pass"] for v in rep.values() if isinstance(v, dict) and "pass" in v)
    out = os.path.join(EV, "ep38-founder-pack-verify-v152")
    os.makedirs(out, exist_ok=True)
    json.dump(rep, io.open(os.path.join(out, "VERIFY_FOUNDER_PACK_V152.json"), "w",
                           encoding="utf-8"), ensure_ascii=False, indent=2)
    for k, v in rep.items():
        if isinstance(v, dict) and "pass" in v:
            print(f"  {'PASS' if v['pass'] else 'FAIL'}  {k}")
    print("ALL_PASS", rep["ALL_PASS"])
    return rep


if __name__ == "__main__":
    sys.exit(0 if main()["ALL_PASS"] else 1)
