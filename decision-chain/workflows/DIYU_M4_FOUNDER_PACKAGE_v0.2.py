#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Founder 交付包生成（冻结候选 398ec63 / 远端 a69cfa2）

产出两份：
  1. V1_M4_FOUNDER_TEST_CARDS_v0.2.md   —— 只含材料完整的卡；不完整的如实披露
  2. V1_M4_AC15_BLIND_EVAL_v0.1.md      —— 三组匿名 A/B；三组标 INCOMPARABLE

匿名化：甲/乙 的分配由 input_sha256 派生（确定性、可审计、卡面不可反推），
钥匙单独落盘 AC15_BLIND_KEY.json，不进交付文档。
"""
import glob, hashlib, io, json, os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
EV = os.path.join(ROOT, "decision-chain", "evidence", "m4")
DOC = os.path.join(ROOT, "decision-chain", "docs")
BACKREF = ["即上方","即以上","同上","同上文","上方即","上文即","见上文","如上所述",
           "内容同上","本区块与","与上方","与上文","与以上"]

def R(aid):
    p = os.path.join(EV, "runs", "%s.json" % aid)
    return json.load(io.open(p, encoding="utf-8")) if os.path.exists(p) else None

def outs(r):
    return ((r or {}).get("raw_response") or {}).get("data", {}).get("outputs") or {}

def legit(o):
    try: rs = json.loads(o.get("returns_json") or "[]")
    except Exception: rs = []
    return any(isinstance(x, dict) and (x.get("highest_damaged_layer") or "").strip()
               and (x.get("precise_gap") or "").strip() for x in rs)

def violations(o):
    a = (o.get("artifact") or "").strip(); u = (o.get("user_delivery") or "").strip()
    v = []
    if any(m in a[:200] for m in BACKREF): v.append("ARTIFACT_BACKREF")
    elif not a and not legit(o): v.append("ARTIFACT_EMPTY")
    elif a and len(a) < 400 and not legit(o): v.append("ARTIFACT_BELOW_MIN")
    if not u: v.append("USER_DELIVERY_EMPTY")
    elif any(m in u[:200] for m in BACKREF): v.append("USER_DELIVERY_BACKREF")
    return v

def clip(s, n):
    s = (s or "").strip()
    return s if len(s) <= n else s[:n] + "\n\n…（截断，完整内容见 %s）"

# ---- Founder 需有界判断的合取项（来自冻结判据正文的 H 类） ----
CARDS = [
    ("AC-05", "12 项业务核心逐项同义", ["FA-34", "FA-35"],
     "两份 Brief 的 12 项业务核心是否**逐项同义**？来源不同（M3 / Campaign）是否只体现在 provenance，而没有改变核心？"),
    ("AC-06", "Matrix 局部 Return", ["FA-05"],
     "Matrix 遇到资料不足时，是**只停不能判的那一支**，还是把整件事退回给你？"),
    ("AC-13", "内部与用户交付分离", ["FA-29"],
     "给你看的那一块，有没有出现内部术语/状态码/审查便条？必要的选择和成立条件有没有被删掉？"),
    ("AC-17", "F-10 目标忠实（硬门）", ["FA-39", "FA-40"],
     "只改了目标，内容承诺 / 结构 / CTA·承接是否**实质变化**？B 有没有被改写成长期价值表达？B 有没有因为目标是 LEADS 就自动拿到高风险 CTA？"),
    ("AC-18", "专业方法保留且非全链硬门", ["FA-31"],
     "短入口进来，适用的专业方法是否仍在？不适用的 Skill 是否被正确跳过、而不是变成必过的闸？"),
    ("AC-21", "混合目标显式取舍", ["FA-44"],
     "混合目标下，系统是否把取舍**显式讲出来**？还是压平成一个综合分？"),
    ("AC-22", "候选实质不同（用户可见）", ["FA-42", "FA-43"],
     "有真实取舍时给出的多个候选，在**你看得到的那一层**是不是真的不同？无取舍时只给 1 个，是否合理？"),
    ("AC-25", "ENTRY-07 Direct PP", ["FA-38"],
     "直接进入包装环节，产出是否可用？未核实的平台规格有没有被当成事实？"),
    ("AC-26", "共同质量底线（模板腔探针）", ["FA-P1"],
     "注入的三段模板腔材料（『氛围感拉满』『因人而异』『闭眼入不会错』），系统是**拒绝并说明理由**，还是搬运进产出？"),
    ("AC-27", "创意深度与成品质量不降", ["FA-30"],
     "无真实事件时的合法演绎，创意深度和成品质量有没有掉下来？"),
]

def build_cards():
    P = ["# V1-M4 Founder 测试卡 v0.2", "",
         "```yaml",
         "冻结候选: 398ec63（内容基线 7793306）",
         "远端: a69cfa2 · codex/v1-m4-capability-seams-runtime-integration-001",
         "判据: 31 项冻结判据 · PASS=16 FAIL=1 NOT_VERIFIED=14",
         "你的角色: 只做终结测试审查（有界判断）；技术裁决不归你",
         "```", "",
         "> **看之前先知道三件事**", ">",
         "> 1. 下面每张卡都附了**冻结运行的真实产出原文**，不是我复述的。",
         "> 2. 材料不完整的卡，我**标出来并说明为什么不能判**，不假装可判。",
         "> 3. `AC-31` 已判 **FAIL**（三份运行交付块为空），这是技术阻断项，**不需要你裁决**，"
         "已如实登记 `M4-FND-020` 并停止，未开启修复循环。", "", "---", ""]
    usable = blocked = 0
    for cid, name, aids, question in CARDS:
        recs = [(a, R(a)) for a in aids]
        missing = [a for a, r in recs if r is None]
        vio = {a: violations(outs(r)) for a, r in recs if r}
        bad = {a: v for a, v in vio.items() if v}
        P += ["## %s · %s" % (cid, name), ""]
        if missing:
            P += ["> ❌ **材料缺失**：%s 未落盘。本卡不可判。" % "、".join(missing), "", "---", ""]
            blocked += 1; continue
        if bad:
            P += ["> ❌ **材料不完整，本卡不可判。**", ">",
                  "> 用冻结阈值（取证判据合同 v0.2 §1.1）核验，下列运行存在完整性违规：", ">"]
            for a, v in bad.items():
                o = outs(dict(recs)[a])
                P += ["> - `%s`：%s（artifact %d 字 / 交付块 %d 字）"
                      % (a, "、".join(v), len((o.get("artifact") or "").strip()),
                         len((o.get("user_delivery") or "").strip()))]
            P += [">", "> **不请你在残缺产出上判定** —— 那样得到的差异来自形态而不是专业水平。",
                  "", "---", ""]
            blocked += 1; continue
        usable += 1
        P += ["**要你判断的**：%s" % question, ""]
        for a, r in recs:
            o = outs(r)
            P += ["### 运行 `%s`（`run_id` %s）" % (a, r.get("run_id") or "—"), "",
                  "**给用户看的那一份**：", "", "```", clip(o.get("user_delivery"), 2600) %
                  ("decision-chain/evidence/m4/runs/%s.json" % a) if len((o.get("user_delivery") or "").strip()) > 2600
                  else (o.get("user_delivery") or "").strip(), "```", "",
                  "**内部专业产出节选**：", "", "```",
                  ((o.get("artifact") or "").strip()[:2200] + "\n\n…（截断，完整见 runs/%s.json）" % a)
                  if len((o.get("artifact") or "").strip()) > 2200 else (o.get("artifact") or "").strip(),
                  "```", ""]
        P += ["**PASS 条件**：上面的问题答「是」。",
              "**退回条件**：答「否」——请指出具体是哪一句/哪一段让你这么判断。", "", "---", ""]
    P += ["## 汇总", "",
          "- 可判卡：**%d**" % usable,
          "- 材料不完整、如实披露不可判：**%d**" % blocked,
          "", "`AC-15` 另见盲评包 `V1_M4_AC15_BLIND_EVAL_v0.1.md`。"]
    p = os.path.join(DOC, "V1_M4_FOUNDER_TEST_CARDS_v0.2.md")
    io.open(p, "w", encoding="utf-8").write("\n".join(P))
    print("测试卡：可判 %d ｜不可判 %d -> %s" % (usable, blocked, os.path.relpath(p, ROOT)))
    return usable, blocked


def build_ac15():
    E = os.path.join(EV, "ac15_eval")
    recs = {}
    for f in glob.glob(os.path.join(E, "AC15_*_*.json")):
        if "MANIFEST" in f: continue
        d = json.load(io.open(f, encoding="utf-8"))
        recs.setdefault(d["capability"], {})[d["side"]] = d
    key = {}
    P = ["# V1-M4 · AC-15 匿名盲评包 v0.1", "",
         "```yaml",
         "判据: AC-15 六 Skill 专业非退化",
         "冻结候选: 398ec63 ｜ 远端: a69cfa2",
         "等参前提: 已由独立 Reviewer 从 12 份原始记录复算证实",
         "  completion_params 12/12 逐字节相同 · model 12/12 相同 · 六对 A/B input_sha256 两两相同",
         "AC-15 整条状态: NOT_VERIFIED（六能力未全部可比前不得记 PASS）",
         "```", "",
         "> **匿名说明**：每组的「甲」「乙」由输入哈希派生分配，**卡面不可反推**。",
         "> 钥匙单独落盘，不在本文档内。你不会知道哪边是源版本、哪边是 M4 后继版本。", "",
         "> **重要**：你对下面 3 组的判断，**不能补足另外 3 组的缺失证据**。",
         "> 六个能力未全部取得可比证据前，`AC-15` 整条保持 `NOT_VERIFIED`。", "", "---", ""]
    ok = bad = 0
    for cap in sorted(recs):
        A, B = recs[cap].get("A_source"), recs[cap].get("B_m4")
        if not (A and B): continue
        vA, vB = violations(A), violations(B)
        if vA or vB:
            bad += 1
            P += ["## %s · ❌ INCOMPARABLE / NOT_VERIFIED" % cap, "",
                  "用冻结阈值（取证判据合同 v0.2 §1.1）核验，两侧不满足可比前提：", "",
                  "| 侧 | artifact | 交付块 | 违规 |", "|---|---|---|---|",
                  "| 一 | %d | %d | %s |" % (len((A.get("artifact") or "").strip()),
                                             len((A.get("user_delivery") or "").strip()),
                                             "、".join(vA) or "—"),
                  "| 二 | %d | %d | %s |" % (len((B.get("artifact") or "").strip()),
                                             len((B.get("user_delivery") or "").strip()),
                                             "、".join(vB) or "—"), "",
                  "**不请你判这一组。** 一边完整一边残缺，看到的差异会来自形态而不是专业水平。", "", "---", ""]
            continue
        ok += 1
        flip = int(hashlib.sha256((A.get("input_sha256") or "").encode()).hexdigest()[0], 16) % 2
        first, second = (A, B) if flip == 0 else (B, A)
        key[cap] = {"甲": first["side"], "乙": second["side"],
                    "甲_app": first["app_id"], "乙_app": second["app_id"]}
        P += ["## %s · ✅ 可盲评" % cap, "",
              "两侧输入逐字节相同（`input_sha256` `%s…`），模型与全部采样参数相同。" % (A.get("input_sha256") or "")[:16], ""]
        for lab, r in (("甲", first), ("乙", second)):
            o = r
            P += ["### %s" % lab, "", "**给用户看的那一份**：", "", "```",
                  (o.get("user_delivery") or "").strip()[:2400], "```", "",
                  "**内部专业产出节选**：", "", "```",
                  (o.get("artifact") or "").strip()[:2400] +
                  ("\n\n…（截断）" if len((o.get("artifact") or "").strip()) > 2400 else ""), "```", ""]
        P += ["**要你判断的**：乙相对甲，这个能力的**关键专业行为**有没有退化？", "",
              "「退化」指：该问的没问、该给的判断没给、该标的边界没标、该拒的没拒。",
              "**不是**指哪份写得更好看、更长、更顺口。", "",
              "**可选答案**：`甲 明显更强` / `乙 明显更强` / `无实质差异` / `无法判断（说明缺什么）`", "", "---", ""]
    P += ["## 汇总", "", "- 可盲评：**%d / 6**" % ok, "- INCOMPARABLE：**%d / 6**" % bad, "",
          "无论你怎么判这 %d 组，`AC-15` 整条仍为 `NOT_VERIFIED`。" % ok]
    p = os.path.join(DOC, "V1_M4_AC15_BLIND_EVAL_v0.1.md")
    io.open(p, "w", encoding="utf-8").write("\n".join(P))
    json.dump({"note": "盲评钥匙，不进交付文档", "map": key},
              io.open(os.path.join(E, "AC15_BLIND_KEY.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print("盲评包：可判 %d/6 ｜INCOMPARABLE %d/6 -> %s" % (ok, bad, os.path.relpath(p, ROOT)))


if __name__ == "__main__":
    build_cards(); build_ac15()
