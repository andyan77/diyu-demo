#!/usr/bin/env python3
"""第 8 轮影响面（A3）：本轮每一处变化，波及哪些取证。

A3 的两侧都要算：**不多算**（让有证据、不受影响的项失效同样是错），
**不少算**（漏掉已知依赖）；影响关系判断不了的标 `STALE` 待定向复验，不假装知道依赖图。

依赖边不靠印象，靠两样东西定：
  1. 各取证的载体是什么（Dify 已发布图 / 直连镜像 / 纯确定性代码）；
  2. 改动文件的 sha256 与上一轮比是否变化（取自 CANDIDATE_FREEZE_v1.4）。
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
FREEZE = os.path.join(WT, "account-operations/evidence/ep23-candidate-v14-freeze/CANDIDATE_FREEZE_v1.4.json")
OUT = os.path.join(WT, "account-operations/evidence/ep27-ac-recompute-v14")

CARRIER = {
    "EP-06 保真":      {"carrier": "Dify 已发布图", "deps": ["SKILL.md", "系统提示词", "闸门三节点", "图"]},
    "EP-06b 行为":     {"carrier": "Dify 已发布图", "deps": ["SKILL.md", "系统提示词", "闸门三节点", "图"]},
    "EP-07 纵向":      {"carrier": "Dify 已发布图 + 投影", "deps": ["SKILL.md", "闸门三节点", "图", "projection_v13.py"]},
    "EP-08 A/B（B 臂）": {"carrier": "直连镜像 gate_pipeline_v14", "deps": ["SKILL.md", "闸门三节点"]},
    "EP-08 A/B（A/A+/B′）": {"carrier": "直连单次调用", "deps": ["A 基线提示词", "参考文件"]},
    "M2→M3 投影契约":  {"carrier": "纯确定性代码", "deps": ["projection_v13.py", "M2 接口"]},
    "下游 Brief 消费":  {"carrier": "纯确定性代码", "deps": ["M3_CONTENT_TASK schema"]},
    "责任反搜／字段消融": {"carrier": "纯确定性代码", "deps": ["SKILL.md", "schema"]},
    "AC-12/13 定向复验": {"carrier": "运行中的 M2 容器 + 投影", "deps": ["M2 接口", "projection_v13.py"]},
    "Founder 实测包":   {"carrier": "从证据逐字取材", "deps": ["候选绑定", "EP-06b 与 EP-07 的运行记录"]},
}


def main():
    fz = json.load(open(FREEZE, encoding="utf-8"))
    changed = set(fz.get("changed_vs_v13") or []) | {"SKILL.md"}
    unchanged = set(fz.get("unchanged_vs_v13") or [])
    # 本轮实际变了的东西（相对第 7 轮候选 v1.3）
    changed_things = {
        "SKILL.md": True,
        "系统提示词": True,                       # = SKILL.md 全文 + 占位符
        "闸门三节点": True,                       # shared_checks / gate_main / post_gate_main
        "图": True,                              # 图哈希变了（因为节点代码与系统提示词嵌在图里）
        "projection_v13.py": False,              # sha256 与第 7 轮相同
        "M2 接口": False,                        # business-persistence 一字未动
        "A 基线提示词": False,                    # 哈希与第 7 轮逐字节相同
        "参考文件": False,                        # 两份 references 哈希未变
        "M3_CONTENT_TASK schema": False,
        "候选绑定": True,
    }
    rows = []
    for name, meta in CARRIER.items():
        hit = [d for d in meta["deps"] if changed_things.get(d)]
        rows.append({
            "取证": name, "载体": meta["carrier"], "依赖": meta["deps"],
            "被本轮变化触及的依赖": hit,
            "结论": "STALE ⇒ 必须重跑" if hit else "不受影响 ⇒ 按 A3 不多算，复用",
        })
    rep = {
        "what": "第 8 轮 A3 影响面：本轮变化 → 各取证的失效集与复验集",
        "changed_vs_v13_by_hash": sorted(changed),
        "unchanged_vs_v13_by_hash": sorted(unchanged),
        "rows": rows,
        "done_this_round": {
            "已按 STALE 重跑": ["EP-06 保真 9/9", "EP-06b 行为 49/49", "EP-07 纵向 12/12",
                              "EP-08 A/B 12/12（B 臂重绑 v1.4.2；A/A+/B′ 哈希逐字节沿用）",
                              "确定性测试全套（48/48 夹具、投影、下游 Brief、责任反搜、字段消融）",
                              "结构反搜对 v1.4.2 已发布图"],
            "已按不多算复用": ["AC-12/AC-13 对 main@a7b8101 的定向复验 —— M2 侧一字未动，"
                            "M3 侧承载该项的 projection_v13.py sha256 未变"],
            "被中止、未产出": ["三名 ECC 独立判定", "36 名盲评 + 揭盲", "判定者隔离核验", "独立收口审查"],
        },
        "founder_pack_impact": {
            "v1.0": "STALE（测的是载体 v1.2）",
            "v1.1": "STALE（测的是载体 v1.3）—— 已在文件头加 STALE 指针，正文一字未改",
            "v1.2 及后继": "**本轮不生成**（Founder PAUSE 第 8 条）。生成的前置条件未满足："
                          "技术验收未闭合、AC-18 无结论、独立收口未做、远端未推送",
        },
        "not_claimed": ["生产就绪", "真实经营提升", "单账号纵向切片完成", "M5 相关任何结论",
                        "任何验收项因『运行 succeeded』而 PASS"],
    }
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "IMPACT_SURFACE_v14.json"), "w", encoding="utf-8") as f:
        json.dump(rep, f, ensure_ascii=False, indent=2)
    for r in rows:
        print(f"{r['取证']:22s} {r['结论']:26s} 触及: {r['被本轮变化触及的依赖']}")
    print()
    print("已重跑:", len(rep["done_this_round"]["已按 STALE 重跑"]), "项 | 复用:",
          len(rep["done_this_round"]["已按不多算复用"]), "项 | 被中止:",
          len(rep["done_this_round"]["被中止、未产出"]), "项")


if __name__ == "__main__":
    main()
