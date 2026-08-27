#!/usr/bin/env python3
"""EP-08 v1.1 preparation: re-bind the four arms to SKILL.md carrier-v1.2.

Writes a NEW file (`_arms_and_holdouts_v3.json`) in a NEW evidence dir.
Round-3's `_arms_and_holdouts.json` and its six completed runs are left
byte-untouched — 账本只追加，不改不删.

Criteria bodies (§5.1 fair conditions / §5.2 hard gates / §5.3 gain gate) are
NOT touched. Only the arm→artifact binding moves, plus ADDENDUM_001's tightened
blinding protocol.
"""
import hashlib
import json
import os
import sys

WORKTREE = "/home/faye/diyu-demo-worktrees/m3-account-content-operator-v1"
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
SKILL_DIR = os.path.join(WORKTREE, "account-operations/skills/operating-one-account")
OUT_DIR = os.path.join(WORKTREE, "account-operations/evidence/ep08-module-ab-v13")

BPRIME = "你是一个内容账号运营助手。请根据下面的账号情况和用户的问题，给出你的运营建议。"

MANIFEST = ("<<REFERENCE_MANIFEST>>\n"
            "references/fashion-and-market.md: LOADED\n"
            "references/six-skill-methods.md: LOADED\n"
            "<<END_REFERENCE_MANIFEST>>")


def read(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


def sha(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    skill = read(os.path.join(SKILL_DIR, "SKILL.md"))
    fashion = read(os.path.join(SKILL_DIR, "references/fashion-and-market.md"))
    sixskill = read(os.path.join(SKILL_DIR, "references/six-skill-methods.md"))
    a_prompt = read(os.path.join(HERE, "A_baseline_prompt.md"))
    holdouts = json.load(open(os.path.join(HERE, "holdouts.json"), encoding="utf-8"))
    V13 = os.path.join(WORKTREE, "account-operations/tools/gate_v13")
    gate_code = read(os.path.join(V13, "shared_checks.py")) + read(os.path.join(V13, "gate_main.py"))
    assemble_code = read(os.path.join(V13, "assemble_main.py"))

    # byte-identical attachment payload for Aplus and B (fairness)
    refs_block = ("\n\n---\n" + MANIFEST +
                  "\n\n---\n# references/fashion-and-market.md\n\n" + fashion +
                  "\n\n---\n# references/six-skill-methods.md\n\n" + sixskill)

    arms = {
        "A": {
            "role": "对照基线（AC-18 硬门与增益门的 A 臂）",
            "description": "独立撰写、未见过 M3 候选任何内容的胜任通用单账号运营基线提示词；已由第二名独立复核者按'是否被故意弱化'复核。第 3、5 轮与本轮逐字相同，未改一个字。",
            "system_prompt": a_prompt,
            "runtime": "single_call",
        },
        "Aplus": {
            "role": "辅助对照（不闸任何 AC）",
            "description": "A 臂 + 与 B 臂逐字相同的附件负载（含同一份 REFERENCE_MANIFEST）。用于把'M3 的专业语义'与'拿到了服装/方法附件'两个变量分开。其结果只作独立观察。",
            "system_prompt": a_prompt + refs_block,
            "runtime": "single_call",
        },
        "B": {
            "role": "候选（AC-18 的 B 臂；AC-01③ 的 B）",
            "description": "M3 Skill carrier-v1.3（含〈必填项闸门〉与〈持续位〉，审计块由代码剥离、外观机器痕迹由代码渲染）及其两份附件。B 臂的运行形态包含闸门本身——闸门是候选的一部分，不是评测装置。",
            "system_prompt": skill + refs_block,
            "runtime": "gated_pipeline",
        },
        "Bprime": {
            "role": "消融（AC-01③ 的 B′）",
            "description": "删除 M3、只保留通用运营提示。用于 AC-01 的'删除 M3 后是否还有可辨识运营增益'消融门。第 3、5 轮与本轮逐字相同。",
            "system_prompt": BPRIME,
            "runtime": "single_call",
        },
    }

    doc = {
        "ecc_id": "ECC-M3-MODULE-AB-002",
        "supersedes_binding_of": "ECC-M3-MODULE-AB-001（判据正文逐字继承，只换绑定；见 M3_ECC_REBIND_002_FROZEN_v1.0.md）",
        "inherits_criteria_verbatim_from": [
            "M3_ECC_MODULE_AB_001_FROZEN_v1.0.md §1/§2/§3/§5/§6/§7/§8",
            "M3_ECC_MODULE_AB_001_FROZEN_v1.0_ADDENDUM_001.md（盲评协议收紧版）",
            "M3_ECC_MODULE_AB_001_FROZEN_v1.0_ADDENDUM_002.md（逐场景·单臂·独立随机分配，已恢复冻结原文）",
            "M3_ECC_MODULE_AB_001_FROZEN_v1.0_ADDENDUM_003.md（**本轮的预冻结判据**：它写于上一轮结果之后，因此上一轮只算探索；本轮在它之后运行，是它的第一次正式执行）",
        ],
        "task_id": "DIYU-V1-M3-ACCOUNT-CONTENT-OPERATOR-001",
        "bound_ac": ["M3-AC-18", "M3-AC-01（③消融门半）"],
        "frozen_before_execution": True,
        "carrier": "direct DeepSeek chat/completions（四臂同一 harness）",
        "carrier_note": (
            "不走 Dify：任务专用候选 App 的 system prompt 已硬编码为 M3 Skill，"
            "把 A/A+/B′ 也塞进去需要再建 App，而合同只授权一个 task-id 专用 App。"
            "四臂改用同一段直连 harness，保证 §5.1 公平条件（同 provider/model/参数/输入/预算）。"
        ),
        "model": "deepseek-v4-flash",
        "provider": "deepseek (https://api.deepseek.com/v1/chat/completions)",
        "temperature": 0.4,
        "max_tokens": "未设置（四臂一致）",
        "user_message_rule": "account_context + '\\n' + user_request，四臂逐字相同",
        "arms": {k: {**v, "system_prompt_sha256": sha(v["system_prompt"]),
                     "system_prompt_chars": len(v["system_prompt"])}
                 for k, v in arms.items()},
        "b_arm_gate": {
            "why": ("SKILL.md v1.1 让模型输出一行 <<TRIGGERS>> 控制行，在 Dify 载体里由代码闸门剥掉。"
                    "直连 harness 若不镜像闸门，B 臂盲评稿会带一行别的臂都没有的控制行——"
                    "既不代表产品真实形态，又能被一眼认出，盲评当场作废。"),
            "how": ("镜像不是重写：ab/run_ab_v2.py 直接 import 部署进 Dify 图的同两份代码"
                    "（gate_code.py / assemble_code.py）与同一段补齐提示词（update_m3_app_v11.FINALIZE_SYS），"
                    "'镜像等于产品'因此由同一性成立，不靠声明。"),
            "gate_code_sha256": sha(gate_code),
            "assemble_code_sha256": sha(assemble_code),
        },
        "holdouts": holdouts,
        "holdout_integrity": {
            "authored_by": "独立夹具撰写者（未读 SKILL.md / references / evidence / 任何 M3_* 治理文档）",
            "skill_frozen_at_commit": "af61b82（v1.0）；v1.1 的两处改动见 M3_ECC_REBIND_002_FROZEN_v1.0.md",
            "claim": ("留出夹具在 Skill 冻结之后才被撰写，git 提交顺序可证；因此不存在'用留出集反向优化实现'的路径。"
                      "但执行侧（= 实现侧）在运行时看得到夹具内容，"
                      "所以留出强度低于'实现者全程不可见'的理想情形——如实记录，不用措辞掩盖。"
                      "v1.1 的两处改动是针对第 3 轮 ECC 实测缺陷做的，不是针对这三个留出场景做的："
                      "闸门标签表来自探索六项/暂定锚点四要素/冲突反馈/无任务四要素，全部是语义主稿早已存在的必填项。"),
        },
        "blinding_protocol": {
            "labels": ["甲", "乙", "丙", "丁"],
            "rule": "每个留出场景的四臂输出按 sha256(case_id + SALT) 派生的排列映射到甲乙丙丁；SALT 不在仓库内。",
            "bundle_location": "仓库之外（ADDENDUM_001 §2.1）：判定者只拿到 <out-of-repo>/ab-blind/<case_id>/ 与 rubric.md",
            "sealed_mapping_path": "scratch 目录下的 _SEALED_AB_MAPPING_v2.json（不进仓库，判定者被禁止读取）",
            "post_hoc_check": ("按 ADDENDUM_001 §2.2 扩到整个 ep08-module-ab* 目录、SKILL 目录、sealed mapping、"
                               "任何 M3_ECC_MODULE_AB_001_FROZEN_*.md；只扫会造成文件访问的参数，"
                               "结果按 §2.3 落成仓库内产物。"),
        },
        "gates": {
            "hard_gate": "M3_ACCEPTANCE_CRITERIA_FROZEN_v1.0.md §5.2 五项非补偿硬门，任一实质退化 = FAIL，不得用其他优势抵消",
            "gain_gate": "同文件 §5.3 七维盲评；整体增益成立 = 多数适用维度为'B 优'且无维度为'A 优且实质'",
            "no_gain_result": "M3_PROFESSIONAL_GAIN = NOT_VERIFIED；M3_MODULE_AB = NOT_PASSED（不是 FAIL）",
            "invalid_evidence": "模型自评、输出长度、Skill 调用次数、规则条数、节点数量、术语密度",
        },
        "known_confounds": [
            "提示词长度不对称：B 臂系统提示词远长于 A 臂。这是候选本身的形态，不是人为放大；Aplus 臂正是为分离这一变量而设。",
            "A 臂撰写者与判定者同为大模型代理，且共享同一份账户级协作宪法；这使 A 被写得更强，方向对 B 不利，不构成对 B 的偏袒。",
            "单次采样：每臂每场景只跑一次，结论是'该绑定下的一次观察'，不是稳定分布。",
            "【v1.1 新增】调用次数不对称：B 臂闸门命中时会多一次补齐调用（1→2 次），其余三臂恒为 1 次。"
            "这是候选的真实形态，不是给 B 的额外预算——但它确实是一处不对称，如实记录，不用'公平条件满足'一笔带过。",
            "【v1.1 写错、v1.2 更正】上一轮把这一条写成'风格不保证不可猜'，**实测是可机械还原**："
            "B 臂输出里带 [参考文件加载状态] 这类方括号字段名，其余三臂一个都没有；三名互不通气的盲评者"
            "各自独立据此定位出候选，揭盲后逐场景吻合。把确定性漏洞写成概率性风险，是低估，不是措辞问题。",
            "【v1.2 新增】上述指纹已在载体层拆除：必填项强制手段整体移出用户可见正文（改为由代码剥离的审计块），"
            "外观机器痕迹由代码确定性渲染成自然语言。本轮判定包生成前逐份机械扫描四臂输出，"
            "任一份命中内部字段即整轮作废重出，扫描结果落盘。",
            "【v1.2 新增】判定形式由并排对照改为**单臂绝对等第**（逐场景、单臂、独立随机分配、3 名取中位）。"
            "这消除了跨场景观察臂轮换的通道，代价是绝对打分噪声高于并排对照，对小幅但真实的增益更保守。"
            "推导规则在判定开始前冻结，见 ADDENDUM_002 §2.5。",
            "【v1.2 新增】风格仍然可能可猜：B 臂的段落组织与措辞习惯来自 SKILL.md 本身，这是候选的真实形态，"
            "无法也不该在盲评里抹掉。判定者被明确要求按 §5.2/§5.3 的实质判，"
            "§5.3 无效证据条款已禁止长度、术语密度、规则条数这类形式指标。",
        ],
    }

    with open(os.path.join(OUT_DIR, "_arms_and_holdouts_v4.json"), "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=2)

    for k, v in doc["arms"].items():
        print(f"{k:8s} {v['system_prompt_chars']:7d} chars  sha={v['system_prompt_sha256'][:16]}  {v['runtime']}")
    print("holdouts:", [h["fixture_id"] for h in holdouts])
    print("file sha256:", sha(read(os.path.join(OUT_DIR, "_arms_and_holdouts_v4.json"))))


if __name__ == "__main__":
    main()
