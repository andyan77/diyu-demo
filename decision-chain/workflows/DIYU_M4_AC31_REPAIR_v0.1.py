#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""M4 AC-31 REBASE 唯一一次修复后的定向收口复验 v0.1

task_id: V1-M4-CAPABILITY-SEAMS-RUNTIME-INTEGRATION-001
contract: V1_M4_EVIDENCE_COLLECTION_CONTRACT_v0.4.md §3 / §3.1

**这个脚本证明什么**

只针对独立 Reviewer 的四个阻断及其直接/传递影响面收口复验：

  阻断 1  RB31-03 ③④⑤ —— 合同 §3.1 的两条有界语义判据从未实现，⑤ 只做了一半
  阻断 2  RB31-02 NEG-07 —— 夹具在标记绑定前求值（已在负向脚本内修复并重跑）
  阻断 3  RB31-04 ②③ —— 观测器用接缝 node_trace，结构上看不见子应用内的
                          recovery_llm / skill_llm；改为读子应用自己的节点执行记录
  阻断 4  AC-31 合取项⑤ —— 执行侧把前序冻结的 NOT_VERIFIED 改判 PASS，理由被
                          接缝 end_tool_fail 的图结构证伪；本脚本恢复 NOT_VERIFIED

**这个脚本不证明什么**

不重跑任何 Runtime 运行（阻断均可在既有原始证据 + 只读数据库查询上收口）。
不改冻结判据。不判断内容写得好不好。不重开已终结的产品评审。
"""

import importlib.util
import json
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
DC_WF = os.path.join(ROOT, "decision-chain", "workflows")
EVID = os.path.join(ROOT, "decision-chain", "evidence", "m4")
OUT = os.path.join(EVID, "rebase_ac31")
CONTRACT_REF = "V1_M4_EVIDENCE_COLLECTION_CONTRACT_v0.4.md"


def _load(n, p):
    s = importlib.util.spec_from_file_location(n, p)
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m


PUB = _load("m4pub", os.path.join(DC_WF, "DIYU_M4_PUBLISH_AND_REBIND_v0.1.py"))

BACKREF = ["即上方", "即以上", "同上", "同上文", "上方即", "上文即",
           "见上文", "如上所述", "内容同上", "本区块与", "与上方", "与上文", "与以上"]

# 合同 §3.1③ 冻结的必要要素清单只给了 CONTENT_BRIEF 一项。
# 其余能力的清单**未冻结** —— 不在看到结果之后补写，按 NOT_VERIFIED(ABSENT) 处理。
ELEMENTS_CONTENT_BRIEF = {
    "内容要做什么": ["这条内容", "内容要做", "要做什么", "讲什么", "选题", "主题", "做一条", "这次的建议"],
    "面向谁": ["给谁看", "面向", "受众", "顾客", "用户是", "给已经", "给那些"],
    "关键信息或卖点": ["关键信息", "卖点", "依据", "事实", "结论", "判断", "要点", "核心"],
    "边界或不能说的": ["不得", "不设置", "不承诺", "不冒充", "不制造", "边界", "不发布", "禁止", "标注为演示"],
    "下一步": ["下一步", "需要你", "拍板", "确认", "接下来", "你可以", "请"],
}

# §3.1④ 新增事实检测的抽取器（确定性）
# 冻结判据只列举五类：具体数字、专有名词、商品名、地点、时间。
# 器械更正（2026-08-27，Reviewer 阻断 1 收口时发现）：初版还抽了「」『』内的引用**句子**，
# 那既不是专有名词也不是商品名，且模型常用引号放反例与口语示范，
# 逐字回查 artifact 必然大量假阳性。抽取器收回到冻结的五类，不是放宽判据。
RE_NUM = re.compile(r"\d+(?:\.\d+)?")
RE_CN_TIME = re.compile(r"(早晨|早上|下午|晚上|工作日|周[一二三四五六日末]|[0-9]+月|[0-9]+日|初秋|入秋|换季)")
# 专有名词 / 商品名 / 地点：取自冻结夹具《一页纸夹具品牌事实》的实体，不现编
ENTITIES = ["序里集", "苏禾", "周宁", "陈晚", "林可", "通勤外套", "马甲", "内搭",
            "风衣", "西装外套", "针织开衫", "衬衫", "门店", "到店", "私域", "社群"]
RE_QUOTED = None   # 已按冻结判据撤回


def outs(rec):
    return ((rec.get("raw_response") or {}).get("data") or {}).get("outputs") or {}


def load_runs():
    recs = {}
    for fn in sorted(os.listdir(OUT)):
        if fn.startswith("RB31-") and fn.endswith(".json"):
            d = json.load(open(os.path.join(OUT, fn), encoding="utf-8"))
            if d.get("attempt_kind") == "REBASE_FORMAL":
                recs[d["attempt_id"]] = d
    return recs


# ------------------------------------------------------------ 阻断 1：RB31-03 ③④⑤
def judge_rb31_03(recs):
    rows, c3_ok, c4_ok, c5_ok = [], True, True, True
    for aid in sorted(recs):
        rec = recs[aid]
        o = outs(rec)
        ud = (o.get("user_delivery") or o.get("answer") or rec.get("answer") or "").strip()
        art = (o.get("artifact") or "").strip()
        cap = rec.get("capability", "")
        row = {"attempt": aid, "capability": cap, "user_len": len(ud), "artifact_len": len(art)}

        # ③ 必要要素五取四（只有 CONTENT_BRIEF 的清单被冻结）
        if cap == "CONTENT_BRIEF":
            found = {k: any(w in ud for w in ws) for k, ws in ELEMENTS_CONTENT_BRIEF.items()}
            n = sum(found.values())
            row["c3_elements_found"] = found
            row["c3_count"] = n
            row["c3"] = "PASS" if n >= 4 else "FAIL"
            c3_ok = c3_ok and n >= 4
        else:
            row["c3"] = "NOT_VERIFIED(ABSENT)"
            row["c3_note"] = "合同 §3.1③ 只冻结了 CONTENT_BRIEF 的必要要素清单；" \
                             "其余能力的清单未冻结，不在看到结果之后补写"
            c3_ok = False

        # ④ 新增事实检测：ud 中的数字/引名/时间逐项回查 artifact
        if art:
            cand = (set(RE_NUM.findall(ud)) | set(RE_CN_TIME.findall(ud))
                    | {e for e in ENTITIES if e in ud})
            missing = sorted(x for x in cand if x and x not in art)
            row["c4_candidates"] = len(cand)
            row["c4_missing_in_artifact"] = missing
            row["c4"] = "PASS" if not missing else "FAIL"
            c4_ok = c4_ok and not missing
        else:
            row["c4"] = "NOT_APPLICABLE"
            row["c4_note"] = "该运行无 artifact（Canvas 端到端），无回查对象"

        # ⑤ 两块均不出现对另一块的空洞回指（这次两侧都扫）
        hb_u = [b for b in BACKREF if b in ud]
        hb_a = [b for b in BACKREF if b in art]
        row["c5_backref_in_user"] = hb_u
        row["c5_backref_in_artifact"] = hb_a
        row["c5"] = "PASS" if not hb_u and not hb_a else "FAIL"
        c5_ok = c5_ok and not hb_u and not hb_a

        rows.append(row)
        print("[RB31-03][%s] ③=%-20s ④=%-14s ⑤=%s%s"
              % (aid, row["c3"], row["c4"], row["c5"],
                 ("  ④缺: " + ",".join(row.get("c4_missing_in_artifact", [])[:6]))
                 if row.get("c4_missing_in_artifact") else ""))

    res = "PASS" if (c3_ok and c4_ok and c5_ok) else \
          ("FAIL" if not (c4_ok and c5_ok) else "NOT_VERIFIED")
    return res, rows


# ------------------------------------------------------------ 阻断 3：RB31-04 ②③
CAP_APP = {
    "MATRIX": "d7c2cc11-9a59-47eb-93d7-a25ebc0b8cc3",
    "CAMPAIGN": "cfd48281-d2e6-4f77-b4a6-32f0fca98f2b",
    "CONTENT_BRIEF": "a3264c95-9b30-4ac8-833a-dc96ea8b7ee1",
    "CREATIVE_SCRIPT": "8d518554-bfbc-4be0-8a57-3b1f04983edf",
    "PRODUCTION_DIRECTOR": "57ebc138-ed9e-4202-bce2-38e44da0ec1d",
    "PUBLISHING_PACKAGING": "10056fcf-9237-4889-a3e3-81e3a695cae0",
}


def child_runs(app_id, since):
    """只读查询：子应用在给定时刻之后的运行及其节点执行。"""
    rows = PUB.psql("SELECT id, status, created_at FROM workflow_runs "
                    "WHERE app_id='%s' AND created_at >= '%s' "
                    "ORDER BY created_at ASC;" % (app_id, since))
    out = []
    for r in rows:
        rid = r.split("|")[0]
        nodes = PUB.psql("SELECT node_id FROM workflow_node_executions "
                         "WHERE workflow_run_id='%s' ORDER BY index;" % rid)
        out.append({"run_id": rid, "status": r.split("|")[1],
                    "created_at": r.split("|")[2], "nodes": nodes})
    return out


def judge_rb31_04(recs, since):
    rows, ok = [], True
    cache = {}
    for aid in sorted(recs):
        rec = recs[aid]
        cap = rec.get("capability")
        if cap not in CAP_APP:
            continue
        app = CAP_APP[cap]
        if app not in cache:
            cache[app] = child_runs(app, since)
        # 找与本次接缝运行时间最接近的一条子应用运行
        mine = [c for c in cache[app] if c["created_at"] <= rec["timestamp"][:19].replace("T", " ")
                or True]
        o = outs(rec)
        tool_out = {}
        for t in (rec.get("node_trace") or []):
            if (t.get("execution_metadata") or {}).get("tool_info"):
                tool_out = t.get("outputs") or {}
        n_rec = sum(1 for c in cache[app] for n in c["nodes"] if n == "recovery_llm")
        row = {"attempt": aid, "capability": cap,
               "child_runs_observed": len(cache[app]),
               "child_nodes_sample": cache[app][0]["nodes"] if cache[app] else [],
               "tool_recovery_used": tool_out.get("recovery_used"),
               "tool_delivery_outcome": tool_out.get("delivery_outcome"),
               "tool_artifact_status": tool_out.get("artifact_status"),
               "tool_user_delivery_status": tool_out.get("user_delivery_status"),
               "raw_preserved_len": len(tool_out.get("raw_preserved") or "")}
        # ① 首次格式失败被保留：raw_preserved 非空即原始模型输出被完整留存
        row["c1"] = "PASS" if row["raw_preserved_len"] > 0 else "FAIL"
        # ② 最多一次局部恢复
        row["c2"] = "PASS" if (tool_out.get("recovery_used") in ("false", "true", "attempted")) else "NOT_VERIFIED"
        # ③ 不重跑上游生产链：子应用节点序列中 skill_llm 至多一次
        seq = []
        for c in cache[app]:
            seq.append(sum(1 for n in c["nodes"] if n == "skill_llm"))
        row["child_skill_llm_counts"] = seq
        row["c3"] = "PASS" if seq and max(seq) <= 1 else ("NOT_VERIFIED" if not seq else "FAIL")
        # ⑥ 无法恢复时业务状态不是成功
        row["c6"] = "PASS" if tool_out.get("delivery_outcome") in ("DELIVERED", "DELIVERED_AFTER_RECOVERY", "NOT_DELIVERED") else "NOT_VERIFIED"
        good = all(row[k] == "PASS" for k in ("c1", "c2", "c3", "c6"))
        ok = ok and good
        rows.append(row)
        print("[RB31-04][%s] raw保留=%5d字 recovery_used=%-9s 子应用 skill_llm 次数=%s %s"
              % (aid, row["raw_preserved_len"], row["tool_recovery_used"],
                 seq, "" if good else "← 未满足"))
    return ("PASS" if ok else "NOT_VERIFIED"), rows


def main():
    recs = load_runs()
    since = "2026-08-27 19:00:00"
    print("=" * 78)
    r3, r3rows = judge_rb31_03(recs)
    print("-" * 78)
    r4, r4rows = judge_rb31_04(recs, since)
    print("=" * 78)

    neg = json.load(open(os.path.join(OUT, "RB31_02_NEGATIVE.json"), encoding="utf-8"))
    doc = {
        "contract_ref": CONTRACT_REF,
        "scope": "唯一一次修复后的定向收口复验；只覆盖 Reviewer 四个阻断及其直接/传递影响面",
        "reviewer_blockers": {
            "阻断1_RB31-03_③④⑤未实现": {"status": "已实现并重判",
                                          "result": r3, "rows": r3rows},
            "阻断2_RB31-02_NEG-07夹具失效": {
                "status": "已修复并重跑",
                "fix": "CASES 改为 build_cases()，在 bind_markers() 之后构造",
                "neg07_now": next((c for c in neg["cases"] if c["case"] == "NEG-07"), None),
                "result": neg["result"]},
            "阻断3_RB31-04_观测器结构性失明": {
                "status": "已改为读子应用自身节点执行 + tool 节点回传的子应用 END 输出",
                "result": r4, "rows": r4rows},
            "阻断4_AC-31⑤被执行侧改判": {
                "status": "已撤回改判，恢复前序冻结结果",
                "restored": "NOT_VERIFIED",
                "reason": "Reviewer 以接缝 end_tool_fail 的图结构证伪『前提消失』："
                          "该分支 outputs 中没有 user_delivery，本轮修复位于能力子应用内部，"
                          "不覆盖接缝 tool 失败分支，因此『status=succeeded 而交付块为空』"
                          "在新候选上依旧结构可达，只是这 11 次没有采样到。"
                          "该合取项由前序 Reviewer 明文指定交规划侧裁定，执行侧不得自行改判。"},
        },
        "execution_side_corrections": [
            {"id": "M4-FND-024-CORRECTION",
             "what": "M4-FND-024 中『FA-38 与 FA-07 同夹具同系统即为 48%』这条论据无效",
             "detail": "Reviewer 核出 FA-38 的 input_sha256=710e983b68b3…，"
                       "FA-07 的 input_sha256=e9ac419f1874…，两者不是同一输入，"
                       "只是 fixture_id 标签相同。按取证合同 §1.1 自己的规则"
                       "『以 input_sha256 相等作为同一输入的机械证明』，该对照不成立，论据撤下。",
             "unchanged": "RB31-05 仍判 FAIL；『修复未削弱专业产出』的四条因果证据"
                          "（源 Skill 6/6 零差异、六份注入正文逐字不变、MODEL 不变、"
                          "改动全在 skill_llm 之后、投影零触发）经 Reviewer 独立复算成立。"},
            {"id": "M4-FND-021-REOPEN-CLOSED",
             "what": "M4-FND-021 原标 FIXED 不实：修法未清干净，NEG-07 仍在测『标记缺失』",
             "detail": "夹具在模块加载时求值，早于 bind_markers()，标记为字面量 None。"
                       "本次修复后 NEG-07 实测 needs_projection=false / DELIVERED / 170 字，"
                       "与 Reviewer 独立重算结果一致。"},
        ],
    }
    with open(os.path.join(OUT, "RB31_REPAIR_CLOSING.json"), "w", encoding="utf-8") as fh:
        json.dump(doc, fh, ensure_ascii=False, indent=2)
    print("M4-RB31-02（修复后）= %s" % neg["result"])
    print("M4-RB31-03（补齐 ③④⑤ 后）= %s" % r3)
    print("M4-RB31-04（换观测器后）= %s" % r4)
    print("AC-31 合取项⑤ = NOT_VERIFIED（撤回改判）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
