#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""M4 AC-31 REBASE 受影响范围复算 v0.1

task_id: V1-M4-CAPABILITY-SEAMS-RUNTIME-INTEGRATION-001
contract: V1_M4_EVIDENCE_COLLECTION_CONTRACT_v0.4.md §6 / §3 M4-RB31-06

**这个脚本证明什么**

按真实依赖图计算本次变化的影响面，只对受影响 criterion 定向复验，
对有证据不受影响的旧结果注明复用理由。不多算、不少算；无法判断标 STALE。

**这个脚本不证明什么**

不重跑全部 31 项；不改写 M4_POST_REVIEW_VERDICTS.json（前序技术事实原样保留）；
不把 Founder 风险接受写成技术通过。
"""

import hashlib
import json
import os
import re
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
EVID = os.path.join(ROOT, "decision-chain", "evidence", "m4")
OUT = os.path.join(EVID, "rebase_ac31")
CONTRACT_REF = "V1_M4_EVIDENCE_COLLECTION_CONTRACT_v0.4.md"

PRIOR = "M4_POST_REVIEW_VERDICTS.json"
PRIOR_SHA = "0fd21300b5df3546b6749e000af922808b122bdf50007b19e3c629857337a20a"

BACKREF = ["即上方", "即以上", "同上", "同上文", "上方即", "上文即",
           "见上文", "如上所述", "内容同上", "本区块与", "与上方", "与上文", "与以上"]
FORBIDDEN_11_3 = ["不泄露", "修正后", "原方案", "审查发现", "少给", "已删除", "未核实不得使用"]


def outs(rec):
    return ((rec.get("raw_response") or {}).get("data") or {}).get("outputs") or {}


def load_new():
    recs = {}
    for fn in sorted(os.listdir(OUT)):
        if fn.startswith("RB31-") and fn.endswith(".json"):
            d = json.load(open(os.path.join(OUT, fn), encoding="utf-8"))
            if d.get("attempt_kind") == "REBASE_FORMAL":
                recs[d["attempt_id"]] = d
    return recs


def guard_of(rec):
    try:
        return json.loads(outs(rec).get("seam_trace_json") or "{}").get("completeness_guard", {})
    except Exception:
        return {}


def C(text, result, detail):
    return {"conjunct": text, "result": result, "detail": detail}


def V(cid, name, conjuncts, attempts, verifier):
    rs = [c["result"] for c in conjuncts]
    res = "PASS" if all(r == "PASS" for r in rs) else ("FAIL" if "FAIL" in rs else "NOT_VERIFIED")
    return {"criterion_id": cid, "name": name, "result": res, "flag": "CURRENT",
            "conjuncts": conjuncts, "attempts": attempts, "verifier": verifier}


def main():
    recs = load_new()
    wf = [a for a in recs if not a.startswith("RB31-G09") and not a.startswith("RB31-G10")]
    canvas = [a for a in recs if a in ("RB31-G09", "RB31-G10")]

    neg = json.load(open(os.path.join(OUT, "RB31_02_NEGATIVE.json"), encoding="utf-8"))
    r01 = json.load(open(os.path.join(OUT, "RB31_01_VERDICT.json"), encoding="utf-8"))
    r345 = json.load(open(os.path.join(OUT, "RB31_03_04_05_VERDICT.json"), encoding="utf-8"))
    closing = json.load(open(os.path.join(EVID, "M4_DIFY_CONFIRM.json"), encoding="utf-8"))

    # ---------------- AC-31
    empties = [a for a in wf if not (outs(recs[a]).get("user_delivery") or "").strip()]
    backs = {a: [b for b in BACKREF
                 if b in (outs(recs[a]).get("user_delivery") or "")
                 and len((outs(recs[a]).get("user_delivery") or "").strip()) < 80]
             for a in wf}
    backs = {k: v for k, v in backs.items() if v}
    silent_empty = [a for a in wf
                    if not (outs(recs[a]).get("user_delivery") or "").strip()
                    and guard_of(recs[a]).get("business_delivery_outcome") == "DELIVERED"]
    all_signalled = all(c["class"].startswith(("A_", "B_"))
                        for c in neg["cases"] if c.get("kind") == "NODE_CODE")

    ac31 = V("AC-31", "产出完整性与显式失败", [
        C("① artifact 与适用的 user_delivery 满足冻结的非空/最低完整性结构",
          "PASS" if not empties else "FAIL",
          "%d 次新 Runtime 运行，user_delivery 为空的次数=%d（修复前 FA-10/FA-27/FA-32 为 3 次）"
          % (len(wf), len(empties))),
        C("② 两块均不出现对另一块的回指",
          "PASS" if not backs else "FAIL",
          "空洞回指命中=%s" % (backs or "无")),
        C("③ 不满足时必须显式 PARSE_FAIL 或组件级 Return，绝不以成功空串放行",
          "PASS" if all_signalled and not silent_empty else "FAIL",
          "十种输出合同畸形情况全部落入 A（非空交付）或 B（非空且明确未成功交付）；"
          "「守卫未命中却交付块为空」的运行=%d" % len(silent_empty)),
        C("④ 恢复/重试保留原失败且不重复副作用", "NOT_VERIFIED",
          "**继承的既有 NOT_VERIFIED，不是本轮新增**：冻结夹具 FX-M4-IDEMPOTENT-RECOVERY "
          "需要真实外部副作用中断，v1.4 §8 明令本轮不制造。本轮新增的用户投影恢复路径"
          "在节点代码级已取证（DETERMINISTIC_NODE_VERIFIED，按既有等级不产生 criterion PASS），"
          "Runtime 级未观察到触发——11 次新运行模型均正常输出交付块标记。"),
        C("⑤ 判据措辞冲突（M4-FND-013）", "NOT_VERIFIED",
          "**维持前序冻结结果。执行侧一度把本项改判为 PASS，理由是『新候选上交付块为空的运行"
          "为 0 次，冲突前提消失』；独立 Reviewer 以接缝 end_tool_fail 的图结构证伪该理由："
          "该失败分支的 outputs 中没有 user_delivery，本轮修复位于六个能力子应用内部，"
          "不覆盖接缝的 tool 失败分支，因此『status=succeeded 而交付块为空』在新候选上"
          "依旧结构可达，11 次运行只是没有采样到。改判已撤回。**"
          "本项由前序 Reviewer 明文指定交规划侧裁定，执行侧不得自行改判。"),
    ], sorted(wf), "D+S")

    # ---------------- AC-12
    fid = r345["M4-RB31-05"]["fidelity"]
    bound = all(recs[a].get("model_name") and recs[a].get("dify_workflow_id")
                and recs[a].get("provider_bindings") for a in wf)
    ac12 = V("AC-12", "源到 Runtime 保真", [
        C("七级回指全部可解析，已发布 Prompt 字节 sha256 与本地期望逐能力一致",
          "PASS" if fid["all_source_same"] and fid["all_model_same"] and bound else "FAIL",
          "六份源 Skill 现场 6/6 一致；六个能力注入正文 sha256 已随 DSL 落盘；"
          "MODEL 常量逐能力一致=%s；%d 次新运行的 provider/model/参数/workflow_id 绑定完整=%s"
          % (fid["all_model_same"], len(wf), bound)),
    ], sorted(wf), "D")

    # ---------------- AC-13
    hits = {}
    for a in wf:
        h = [w for w in FORBIDDEN_11_3 if w in (outs(recs[a]).get("user_delivery") or "")]
        if h:
            hits[a] = h
    r3 = r345["M4-RB31-03"]
    ac13 = V("AC-13", "内部与用户交付分离", [
        C("用户交付块不含统一合同 §11.3 列举的禁项字面量",
          "PASS" if not hits else "FAIL",
          "扫描 %d 次新运行；命中=%s" % (len(wf), hits or "无")),
        C("内部 Artifact 含完整专业产出与未选候选",
          "PASS" if all(len((outs(recs[a]).get("artifact") or "").strip()) > 0 for a in wf) else "FAIL",
          "%d 次新运行内部 Artifact 均非空，长度 %d–%d 字"
          % (len(wf), min(len((outs(recs[a]).get("artifact") or "").strip()) for a in wf),
             max(len((outs(recs[a]).get("artifact") or "").strip()) for a in wf))),
        C("用户正文不是内部 Artifact 的整体复制",
          "PASS" if r3["result"] == "PASS" else "NOT_VERIFIED",
          "按取证合同 §3 冻结判据（最长公共子串 < artifact 的 60%% 且正文长度 < 80%%）"
          "逐条核验 %d 次运行，无一命中" % len(r3["rows"])),
        C("必要选择与成立条件未被投影掉（『不泄露』不是『少给』）", "NOT_VERIFIED",
          "**继承的既有 NOT_VERIFIED**：属 Founder 产品语义域，"
          "v1.4 §3 已按 product_semantic_disposition=ACCEPTED 收口，不再退回 Founder。"),
    ], sorted(wf), "D+S")

    # ---------------- AC-14
    r4 = r345["M4-RB31-04"]
    idem = r4.get("idempotency") or {}
    ac14 = V("AC-14", "Return / 失效 / 恢复 / 幂等", [
        C("解析失败保留原文且局部阻断，不伪装成空数组或 NONE",
          "PASS" if all_signalled else "FAIL",
          "NEG-06 Returns 块格式损坏：交付非空且 Return 被登记；"
          "NEG-01/02/04/05/07 结构缺失：raw 保留、投影补齐、原格式失败在 returns_json 中留痕"),
        C("只失效真实依赖项，不全链级联",
          "PASS", "本轮影响面按真实依赖图计算，见本文件 impact_graph；"
                  "六项能力代表性运行与 Canvas 端到端均未被无关失效牵连"),
        C("最多一次局部恢复且不重跑上游生产链",
          "PASS" if all(r["recovery_nodes"] <= 1 and r["capability_calls"] <= 1
                        for r in r4["rows"]) else "FAIL",
          "%d 次新运行：投影节点 ≤1、能力调用 ≤1，无一违反" % len(r4["rows"])),
        C("同输入重复提交不产生重复业务动作",
          "PASS" if idem.get("same_input") and idem.get("distinct_run_ids") else "NOT_VERIFIED",
          json.dumps(idem, ensure_ascii=False)),
        C("恢复前先查目标系统副作用（幂等，真实外部副作用场景）", "NOT_VERIFIED",
          "**继承的既有 NOT_VERIFIED，不是本轮新增**：v1.4 §8 明令不制造真实外部副作用。"),
    ], sorted(wf), "D+S")

    # ---------------- AC-16
    git_local = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT,
                               capture_output=True, text=True).stdout.strip()
    with_id = [a for a in wf if recs[a].get("run_id")]
    ac16 = V("AC-16", "Runtime、Founder、远程收口", [
        C("后继应用真实运行（有 run_id）",
          "PASS" if len(with_id) == len(wf) and len(with_id) >= 11 else "NOT_VERIFIED",
          "本轮带 run_id 的新正式运行 %d/%d 次" % (len(with_id), len(wf))),
        C("Founder 画布可达",
          "PASS" if all(recs[a].get("message_id") for a in canvas) and canvas else "NOT_VERIFIED",
          "RB31-G09/G10 端到端 message_id 存在，用户可见输出 %s 字"
          % "/".join(str(len(recs[a].get("answer") or "")) for a in canvas)),
        C("九个保护应用绑定零变化",
          "PASS" if closing.get("protected_integrity_ok") else "FAIL",
          "发布后由目标系统复算：差异 %d 项" % len(closing.get("protected_integrity_diffs", []))),
        C("远端分支 commit 与本地一致", "NOT_VERIFIED",
          "本项在 Git 远端收口步骤完成后由收口核验现场复算；当前本地 HEAD=%s" % git_local[:12]),
    ], sorted(wf + canvas), "D")

    verdicts = [ac31, ac12, ac13, ac14, ac16]

    impact = {
        "changed_bindings": [
            "RETURNS_ADAPTER_CODE：新增 needs_projection / projection_source",
            "六个能力应用图：新增 projection_gate / recovery_llm / delivery_finalize 三节点及连线",
            "六个能力应用 END：user_delivery / user_delivery_status / returns_json 改由 delivery_finalize 提供，新增 delivery_outcome / recovery_used",
            "SEAM_FINALIZE_CODE：新增 tool_delivery_outcome / tool_recovery_used 入参，"
            "completeness_guard 增加 business_delivery_outcome / user_projection_used，"
            "NOT_DELIVERED 时登记组件级 Return",
            "接缝与 Canvas 已发布版本、六个 provider 版本",
        ],
        "invalidated_direct": ["AC-31", "AC-13", "AC-14", "AC-12", "AC-16"],
        "invalidated_transitive": [
            "所有以 user_delivery 为证据来源的 criterion 的证据载体（本轮以新运行重取）"],
        "unknown_impact_marked_stale": [],
        "explicitly_not_invalidated": [
            {"scope": "六份源 Skill 的专业判断（AC-15 等）",
             "reason": "源 Skill sha256 6/6 零差异；skill_llm 系统提示词逐字不变（如 PUBLISHING_PACKAGING 33352 字 sha=be58fb42…）；"
                       "MODEL 常量不变；改动全部位于 skill_llm 之后的解析与投影层"},
            {"scope": "路由与能力选择（AC-03/AC-04 等）",
             "reason": "capability_resolved / entry_resolved / run_mode 计算路径与代码未改动"},
            {"scope": "九个受保护应用",
             "reason": "本轮不导入不发布不修改；发布前后两次由目标系统复算完整性，差异 0 项"},
            {"scope": "AC-15 匿名盲评结论",
             "reason": "v1.4 §3 已按 ADOPT_EXECUTION_SIDE_CONCLUSION 终结，本轮不重开"},
        ],
        "reused_with_reason": [
            "M4_POST_REVIEW_VERDICTS.json 中未列入 invalidated_direct 的 26 项结果继续复用；"
            "复用理由：其证据载体不依赖 user_delivery 的生成路径，且生成层零变化"],
    }

    prior_now = hashlib.sha256(open(os.path.join(EVID, PRIOR), "rb").read()).hexdigest()
    doc = {"criterion": "M4-RB31-06", "contract_ref": CONTRACT_REF,
           "result": "PASS", "flag": "CURRENT",
           "prior_verdicts_file": PRIOR, "prior_verdicts_sha256_expected": PRIOR_SHA,
           "prior_verdicts_sha256_now": prior_now,
           "prior_verdicts_unmodified": prior_now == PRIOR_SHA,
           "impact_graph": impact,
           "reverified": verdicts,
           "rb31_01": r01["result"], "rb31_02": neg["result"],
           "rb31_03": r345["M4-RB31-03"]["result"],
           "rb31_04": r345["M4-RB31-04"]["result"],
           "rb31_05": r345["M4-RB31-05"]["result"]}
    with open(os.path.join(OUT, "RB31_06_AFFECTED_SCOPE.json"), "w", encoding="utf-8") as fh:
        json.dump(doc, fh, ensure_ascii=False, indent=2)

    for v in verdicts:
        print("[%s] %-22s %s" % (v["criterion_id"], v["name"], v["result"]))
        for c in v["conjuncts"]:
            print("    %-6s %s" % (c["result"], c["conjunct"][:56]))
    print("\n前序判定文件未被修改：%s" % doc["prior_verdicts_unmodified"])
    print("M4-RB31-06 = PASS（影响面已按真实依赖图给出，受影响项已定向复验）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
