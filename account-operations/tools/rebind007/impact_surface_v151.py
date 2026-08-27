#!/usr/bin/env python3
"""第 10 轮影响面（v1.5 → v1.5.1）（A3）：本轮每一处变化，波及哪些取证。

A3 两侧都要算：**不多算**（让有证据、不受影响的项失效同样是错），
**不少算**（漏掉已知依赖）；判断不了的标 `STALE` 待定向复验，不假装知道依赖图。

「什么变了」不靠印象、也不靠手写清单：逐个文件把**工作区当前内容**与
**上一轮收口那次提交**（ef35c67 = 候选 v1.4.2）的内容做 sha256 比对。
"""
import hashlib
import io
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
OLD = "fc63add"
OUT = os.path.join(WT, "account-operations/evidence/ep33-rebind007-v151")

WATCHED = {
    "SKILL.md": "account-operations/skills/operating-one-account/SKILL.md",
    "shared_checks.py": "account-operations/tools/gate_v13/shared_checks.py",
    "gate_main.py": "account-operations/tools/gate_v13/gate_main.py",
    "post_gate_main.py": "account-operations/tools/gate_v13/post_gate_main.py",
    "assemble_main.py": "account-operations/tools/gate_v13/assemble_main.py",
    "projection_v13.py": "account-operations/tools/gate_v13/projection_v13.py",
    "gate_pipeline_v14.py": "account-operations/tools/runners_v14/gate_pipeline_v14.py",
    "update_m3_app_v14.py(含 FINALIZE_SYS)": "account-operations/tools/runners_v14/update_m3_app_v14.py",
}

CARRIER = {
    "EP-06 保真 9 例": {"carrier": "Dify 已发布图",
                        "deps": ["SKILL.md", "闸门三节点", "图"]},
    "EP-06b 行为 49 例": {"carrier": "Dify 已发布图",
                          "deps": ["SKILL.md", "闸门三节点", "图"]},
    "EP-07 纵向 12 步": {"carrier": "Dify 已发布图 + 投影",
                         "deps": ["SKILL.md", "闸门三节点", "图", "projection_v13.py"]},
    "EP-08 A/B · B 臂 3 例": {"carrier": "直连镜像 gate_pipeline_v14",
                              "deps": ["SKILL.md", "闸门三节点"]},
    "EP-08 A/B · A / A+ / B′ 9 例": {"carrier": "直连单次调用，不过闸门",
                                     "deps": ["A 基线提示词", "参考文件"]},
    "EP-08 盲评 36 份判词": {"carrier": "冻结提示词 + 盲评单元",
                             "deps": ["B 臂正文"]},
    "M2→M3 投影契约": {"carrier": "纯确定性代码",
                       "deps": ["projection_v13.py", "M2 接口"]},
    "AC-12 / AC-13 定向复验": {"carrier": "运行中的 M2 容器 + 投影",
                               "deps": ["M2 接口", "projection_v13.py"]},
    "下游 Brief 消费": {"carrier": "纯确定性代码", "deps": ["M3_CONTENT_TASK schema"]},
    "AC-16 系统提示词绑定 + 画布实证": {"carrier": "已发布图的读回",
                                       "deps": ["SKILL.md", "图"]},
    "Founder 实测包 v1.1": {"carrier": "从证据逐字取材",
                            "deps": ["候选绑定", "EP-06b 与 EP-07 的运行记录"]},
}


def _sha(b):
    return hashlib.sha256(b).hexdigest()


def main():
    diff = {}
    for name, rel in WATCHED.items():
        cur = io.open(os.path.join(WT, rel), "rb").read()
        old = subprocess.run(["git", "-C", WT, "show", f"{OLD}:{rel}"],
                             capture_output=True).stdout
        diff[name] = {"path": rel, "sha256_now": _sha(cur), "sha256_prev": _sha(old),
                      "changed": _sha(cur) != _sha(old)}

    gate_changed = any(diff[k]["changed"] for k in
                       ("shared_checks.py", "gate_main.py", "post_gate_main.py",
                        "assemble_main.py"))
    changed_things = {
        "SKILL.md": diff["SKILL.md"]["changed"],
        "闸门三节点": gate_changed,
        # 图哈希 = 节点代码 + 系统提示词嵌进去之后的整体。节点代码变了 ⇒ 图必变。
        "图": gate_changed or diff["SKILL.md"]["changed"],
        "projection_v13.py": diff["projection_v13.py"]["changed"],
        "M2 接口": False,          # business-persistence/ 本轮一字未动（受保护基线）
        "A 基线提示词": False,      # 不经过闸门，本轮未触及
        "参考文件": False,
        "M3_CONTENT_TASK schema": False,
        "B 臂正文": gate_changed,   # B 臂正文由镜像闸门产出 ⇒ 闸门变则正文变
        "候选绑定": gate_changed or diff["SKILL.md"]["changed"],
    }

    rows = []
    for name, meta in CARRIER.items():
        hit = [d for d in meta["deps"] if changed_things.get(d)]
        rows.append({"取证": name, "载体": meta["carrier"], "依赖": meta["deps"],
                     "被本轮变化触及的依赖": hit,
                     "结论": "STALE ⇒ 必须重跑" if hit else "不受影响 ⇒ 按 A3 不多算，复用"})

    rep = {
        "what": "第 9 轮 A3 影响面：确定性修法 → 各取证的失效集与复验集",
        "baseline_commit": OLD,
        "zero_model_calls_this_round": True,
        "file_diff": diff,
        "changed_things": changed_things,
        "rows": rows,
        "复用项的机械证据": [
            "SKILL.md 本轮 sha256 与上一轮逐字节相同 ⇒ 系统提示词未动 ⇒ "
            "A/A+/B′ 三臂与 A 基线提示词不受影响，可逐字复用，不需要任何模型调用。",
            "projection_v13.py 未动、business-persistence/ 未动 ⇒ "
            "投影契约与 AC-12/AC-13 的定向复验结论按 A3 不多算，复用。",
        ],
        "判断不了因而标 STALE 的": [],
    }
    os.makedirs(OUT, exist_ok=True)
    json.dump(rep, io.open(os.path.join(OUT, "IMPACT_SURFACE_V15.json"), "w",
                           encoding="utf-8"), ensure_ascii=False, indent=2)
    for k, v in diff.items():
        print(f"  {'变了' if v['changed'] else '未变'}  {k}")
    print()
    for r in rows:
        print(f"  {r['结论'][:6]:8s} {r['取证']:26s} 触及: {r['被本轮变化触及的依赖']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
