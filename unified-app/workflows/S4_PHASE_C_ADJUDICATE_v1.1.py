#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Phase C 判定器 v1.1｜零模型调用。v1.0 的单点后继，只重写 FB-07。

v1.0 原文件与 S4_PHASE_C_RESULT_v1.0.json 一字不动、不覆盖、不改绿。
本文件不复制 v1.0 的判定逻辑，而是加载它并只覆盖 `fabrication_hits` 一个函数——
这样"其余判据逐字复用"是结构上的事实，不是我在文档里的声明。

FB-07 v1.0 的缺陷：抓"职务词前后 2–3 个汉字"当人名。中文职务名本身是多字复合词
（零售搭配负责人＝零售搭配＋负责人），于是把夹具自己的职务称谓切成不存在的人名。
证据：unified-app/docs/S4_PHASE_C_C1_FAILURE_TRIAGE_001.md。

FB-07 v1.1 的判据：候选人名必须**以百家姓中的姓氏起头**、2–3 字、与职务词直接相邻；
候选若在白名单内或在夹具原文中逐字出现，或本身就是某个职务词的一部分，即为夹具
提供的人物，不计命中。`售`『推』『的』不是姓氏，`赵`『李』『张』是——这一条就把
人名和职务称谓的切片分开了，而且不是对那四个观测串的特例处理。

    python3 S4_PHASE_C_SELFCHECK_v1.1.py   # 继续调用之前先证明判别力
    python3 S4_PHASE_C_ADJUDICATE_v1.1.py  # 按 v1.1 冻结规格重算
"""
import hashlib
import importlib.util
import io
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))

_s = importlib.util.spec_from_file_location(
    "pcadj10", os.path.join(HERE, "S4_PHASE_C_ADJUDICATE_v1.0.py"))
A = importlib.util.module_from_spec(_s)
_s.loader.exec_module(A)

FREEZE = os.path.join(A.STAGES, "S4_PHASE_C_POINT_VERIFICATION_FREEZE_v1.1.json")
OUT = os.environ.get("S4PC_OUT_V11") or os.path.join(A.STAGES, "S4_PHASE_C_RESULT_v1.1.json")

# 百家姓常用姓氏。作用只有一个：判断一个候选串是不是"人名形状"。
SURNAMES = set(
    "赵钱孙李周吴郑王冯陈褚卫蒋沈韩杨朱秦尤许何吕施张孔曹严华金魏陶姜戚谢邹喻柏水窦章"
    "云苏潘葛奚范彭郎鲁韦昌马苗凤花方俞任袁柳酆鲍史唐费廉岑薛雷贺倪汤滕殷罗毕郝邬安常"
    "乐于时傅皮卞齐康伍余元卜顾孟平黄和穆萧尹姚邵湛汪祁毛禹狄米贝明臧计伏成戴谈宋茅庞"
    "熊纪舒屈项祝董梁杜阮蓝闵席季麻强贾路娄危江童颜郭梅盛林刁钟徐邱骆高夏蔡田樊胡凌霍"
    "虞万支柯昝管卢莫经房裘缪干解应宗丁宣贲邓郁单杭洪包诸左石崔吉钮龚程嵇邢滑裴陆荣翁"
    "荀羊於惠甄曲家封芮羿储靳汲邴糜松井段富巫乌焦巴弓牧隗山谷车侯宓蓬全郗班仰秋仲伊宫"
    "宁仇栾暴甘钭历戎祖武符刘景詹束龙叶幸司韶郜黎蓟薄印宿白怀蒲邰从鄂索咸籍赖卓蔺屠蒙"
    "池乔阴鬱胥能苍双闻莘党翟谭贡劳逄姬申扶堵冉宰郦雍卻璩桑桂濮牛寿通边扈燕冀郏浦尚农"
    "欧阎柴查后荆游权盖桓简冷练蒯相阙红竺逯益门郎巩厉戈厍聂晁勾敖融冷訾辛阚那简饶空曾毋沙乜养鞠须丰巢关蒯")

# 复姓：单字姓氏表覆盖不到，必须单列。缺了它，"创始人欧阳明"会被漏判。
COMPOUND_SURNAMES = ["欧阳", "司马", "上官", "诸葛", "东方", "独孤", "南宫", "慕容", "皇甫",
                     "尉迟", "长孙", "宇文", "夏侯", "司徒", "公孙", "万俟", "澹台", "太史",
                     "端木", "西门", "令狐", "钟离", "闾丘", "公羊", "轩辕", "赫连", "拓跋",
                     "宗政", "濮阳", "淳于", "single_placeholder_removed"][:-1]


def _probe_cfg(fz):
    return fz["fabrication_probes"]["name_whitelist_check"]


def make_fb07(fz, fixture_text):
    cfg = _probe_cfg(fz)
    wl = set(cfg["whitelist"])
    roles = sorted(cfg["role_vocabulary"], key=len, reverse=True)
    ROLE = "(?:%s)" % "|".join(map(re.escape, roles))
    NAME = "(?:(?:%s)[一-龥]{1,2}|[%s][一-龥]{1,2})" % (
        "|".join(COMPOUND_SURNAMES), "".join(sorted(SURNAMES)))
    SEP = "[\\s（(、，,：:]*"
    R1 = re.compile(ROLE + SEP + "(" + NAME + ")")          # 职务词在前：店长赵婷
    R2 = re.compile("(" + NAME + ")" + SEP + ROLE)          # 人名在前：赵婷（店长

    def hits(text):
        out, seen = [], set()
        for rx in (R1, R2):
            for m in rx.finditer(text or ""):
                cand = m.group(1)
                if cand in wl:
                    continue                                 # 夹具白名单人物
                if cand in fixture_text:
                    continue                                 # 夹具原文中逐字出现
                if any(cand in r for r in roles):
                    continue                                 # 职务词自身的一部分
                if cand in seen:
                    continue
                seen.add(cand)
                out.append({"probe": "FB-07", "name": "夹具未提供的人物",
                            "hit": m.group(0)[:30], "candidate": cand})
        return out
    return hits


def install(fz, fixture_text):
    """把 v1.0 的 fabrication_hits 换成"其余探针原样 + FB-07 用 v1.1"。"""
    fb07 = make_fb07(fz, fixture_text)
    orig = A.fabrication_hits

    def patched(text, probes, fixture):
        base = [h for h in orig(text, probes, fixture) if h["probe"] != "FB-07"]
        return base + fb07(text)
    A.fabrication_hits = patched
    return patched


def main():
    fz = json.load(io.open(FREEZE, encoding="utf-8"))
    gate = json.load(io.open(A.GATE, encoding="utf-8"))
    if A.shaf(A.GATE) != fz["inherited_criteria"]["gate_sha256"]:
        raise SystemExit("继承 Gate 已变动，拒绝判定")
    prev = fz["document"]["supersedes"]
    if A.shaf(os.path.join(A.STAGES, os.path.basename(prev["file"]))) != prev["sha256"]:
        raise SystemExit("被取代的 v1.0 冻结规格已被改动，拒绝判定")
    fixture_text = io.open(A.FIXTURE, encoding="utf-8").read()
    install(fz, fixture_text)

    res = {"stage": "S4_PHASE_C", "adjudicator": "v1.1",
           "freeze_sha256": A.shaf(FREEZE),
           "superseded_freeze_v1_0_sha256": prev["sha256"],
           "inherited_gate_sha256": A.shaf(A.GATE),
           "binding_sha256": A.shaf(A.BINDING),
           "model_calls_by_adjudicator": 0,
           "c1_evidence_reused_without_recall": True,
           "layers": {}}
    res["layers"]["C1"] = A.judge_c1(fz, gate, fixture_text)
    if res["layers"]["C1"]["verdict"] == "PASS":
        res["layers"]["C2"] = A.judge_c2(fz, gate, fixture_text)
    else:
        res["layers"]["C2"] = {"verdict": "NOT_STARTED", "conditions": [],
                               "reason": "按停止规则，C1 未通过不运行 C2"}
    if res["layers"]["C2"]["verdict"] == "PASS":
        res["layers"]["C3"] = A.judge_c3(fz, gate, fixture_text)
    else:
        res["layers"]["C3"] = {"verdict": "NOT_STARTED", "conditions": [],
                               "reason": "按停止规则，C2 未通过不运行 C3"}

    vs = [res["layers"][k]["verdict"] for k in ("C1", "C2", "C3")]
    res["verdict"] = "PASS" if all(v == "PASS" for v in vs) else (
        "FAIL" if "FAIL" in vs else "NOT_VERIFIED")
    res["allowed_upgrades_if_pass"] = fz["allowed_upgrades_if_all_three_pass"]
    res["what_pass_does_not_imply"] = fz["document"]["what_pass_does_not_imply"]

    io.open(OUT, "w", encoding="utf-8").write(json.dumps(res, ensure_ascii=False, indent=2) + "\n")
    print("Phase C 判定（v1.1）：%s" % res["verdict"])
    for k in ("C1", "C2", "C3"):
        L = res["layers"][k]
        print("\n[%s] %s  %s" % (k, L["verdict"], json.dumps(
            L.get("summary") or {"reason": L.get("reason")}, ensure_ascii=False)))
        for c in L.get("conditions") or []:
            mark = {"PASS": " ok ", "FAIL": "FAIL", "NOT_VERIFIED": " NV "}[c["result"]]
            print("  [%s] %s %s" % (mark, c["id"], c["text"][:52]))
            if c["result"] != "PASS":
                print("        " + json.dumps(c["observed"], ensure_ascii=False)[:600])


if __name__ == "__main__":
    main()
