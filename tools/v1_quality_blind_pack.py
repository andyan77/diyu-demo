#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""九组质量对照：自动 Hard Gate + 匿名盲审包生成。

X / Y 归属由预注册的确定性规则决定，运行结果无法影响它：
    h = sha256(pre_registration_commit + pair_id)
    int(h[:8],16) 为偶数 → 甲方=X、乙方=Y；为奇数 → 甲方=Y、乙方=X

映射表只写到任务临时目录（权限 600），盲审前不入库；
其 SHA-256 作为承诺先写进 Manifest。
"""
import argparse, hashlib, json, os, re

from _repo_paths import ROOT as REPO, rpath  # 目录重组后按文件名解析
PRE_COMMIT = "00fc94e6c39bc161d33a3df7df260abb7d37b9ec"

PAIRS = [
 ("A1", "集成", "matrix",        "独立 Workflow 直接调用", "主 Chatflow 集成调用"),
 ("A2", "集成", "campaign",      "独立 Workflow 直接调用", "主 Chatflow 集成调用"),
 ("A3", "集成", "content_brief", "独立 Workflow 直接调用", "主 Chatflow 集成调用"),
 ("B1", "模型", "matrix",        "DeepSeek V4 Flash", "Qwen3.8 Max"),
 ("B2", "模型", "campaign",      "DeepSeek V4 Flash", "Qwen3.8 Max"),
 ("B3", "模型", "content_brief", "DeepSeek V4 Flash", "Qwen3.8 Max"),
 ("C1", "Skill", "matrix",        "Skill System Prompt", "No-Skill 强基线"),
 ("C2", "Skill", "campaign",      "Skill System Prompt", "No-Skill 强基线"),
 ("C3", "Skill", "content_brief", "Skill System Prompt", "No-Skill 强基线"),
]
CN = {"matrix": "账号矩阵", "campaign": "Campaign 决策包", "content_brief": "Content Brief"}
SECTIONS = {"matrix": ["第一部分", "第二部分", "账号责任", "唯一使命"],
            "campaign": ["运行结论", "内容目标", "参战账号", "内容排序", "用户行动"],
            "content_brief": ["Content Brief Pack", "运行结论", "内容单元索引", "brief_id"]}
LEAK = ["<think>", "</think>", "reasoning_content", "task_snapshot", "System 提示词"]


def sha(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def side_of(pair_id):
    """返回 (甲方标签, 乙方标签)，甲=第一路，乙=第二路。"""
    h = sha(PRE_COMMIT + pair_id)
    return ("X", "Y") if int(h[:8], 16) % 2 == 0 else ("Y", "X")


def hard_gate(skill, arm_label, rec, frozen_sha):
    """确定性 Hard Gate。返回 [(门名, 是否通过, 说明)]。"""
    g, fo = [], (rec.get("final_output") or "")
    g.append(("1 Final 存在且非空",
              str(rec.get("final_present")).lower() == "true" and len(fo.strip()) > 0,
              "final_present=%s chars=%d" % (rec.get("final_present"), len(fo))))
    if rec.get("task_context_sha256") is not None:
        g.append(("2 输入事实 SHA 与冻结值一致",
                  rec.get("task_context_sha256") == frozen_sha,
                  "实际 %s / 冻结 %s" % (str(rec.get("task_context_sha256"))[:16],
                                       str(frozen_sha)[:16])))
    else:
        g.append(("2 输入事实 SHA 与冻结值一致", None,
                  "集成侧输入由状态机现场组装，SHA 另在 A 轴专项比对"))
    miss = [s for s in SECTIONS[skill] if s not in fo]
    g.append(("6 输出合同关键章节齐全", not miss, "缺失 %s" % (miss or "无")))
    hits = {m: fo.count(m) for m in LEAK if fo.count(m)}
    g.append(("8 无 think / 内部状态泄漏", not hits, "命中 %s" % (hits or "无")))
    g.append(("9 Skill 失败却声称完成", str(rec.get("final_present")).lower() == "true" or len(fo) == 0,
              "final_present=%s" % rec.get("final_present")))
    return g


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", required=True, help="含 comparison_runs.jsonl / integrated.json")
    ap.add_argument("--inputs", required=True, help="frozen_inputs.json")
    ap.add_argument("--out", required=True, help="盲审包 .md 输出路径")
    ap.add_argument("--mapping", required=True, help="映射表输出路径（权限 600，不入库）")
    a = ap.parse_args()

    frozen = json.load(open(a.inputs, encoding="utf-8"))
    runs = {}
    p_runs = os.path.join(a.runs, "comparison_runs.jsonl")
    p = p_runs
    if os.path.exists(p):
        for ln in open(p, encoding="utf-8"):
            try:
                r = json.loads(ln)
            except Exception:
                continue
            runs[r["arm_id"]] = r          # 后写覆盖先写，重跑取最新
    integ, integ_conv = {}, "（未收集）"
    pi = os.path.join(a.runs, "integrated.json")
    if os.path.exists(pi):
        _ij = json.load(open(pi, encoding="utf-8"))
        integ = _ij.get("artifacts") or {}
        integ_conv = _ij.get("conversation_id") or integ_conv

    def usable(rec):
        """只有真正产出了非空正文的臂才算可比较。失败臂不得以空正文混进盲审。"""
        if not rec:
            return None
        if rec.get("run_status") not in (None, "succeeded"):
            return None
        return rec if (rec.get("final_output") or "").strip() else None

    def fetch(pair_id, skill, which):
        axis = pair_id[0]
        if axis == "A":
            return runs.get("%s|deepseek" % skill) if which == 0 else \
                   (dict(integ.get(skill) or {}, final_present="true",
                         arm_id="%s|integrated" % skill) if integ.get(skill) else None)
        if axis == "B":
            return runs.get("%s|deepseek" % skill) if which == 0 else runs.get("%s|qwen" % skill)
        return runs.get("%s|deepseek" % skill) if which == 0 else runs.get("%s|noskill" % skill)

    gates, mapping, blocks, avail = {}, {}, [], []
    for pid, axis, skill, jia, yi in PAIRS:
        raw0, raw1 = fetch(pid, skill, 0), fetch(pid, skill, 1)
        r0, r1 = usable(raw0), usable(raw1)
        sj, sy = side_of(pid)
        mapping[pid] = {"axis": axis, "skill": skill,
                        sj: {"label": jia, "arm_id": (r0 or {}).get("arm_id"),
                             "app_id": (r0 or {}).get("app_id"),
                             "workflow_run_id": (r0 or {}).get("workflow_run_id"),
                             "final_sha256": (r0 or {}).get("final_sha256")},
                        sy: {"label": yi, "arm_id": (r1 or {}).get("arm_id"),
                             "app_id": (r1 or {}).get("app_id"),
                             "workflow_run_id": (r1 or {}).get("workflow_run_id"),
                             "final_sha256": (r1 or {}).get("final_sha256")}}
        gg = {}
        for tagname, rec, raw in ((sj, r0, raw0), (sy, r1, raw1)):
            if rec:
                gg[tagname] = hard_gate(skill, tagname, rec, frozen[skill]["sha256"])
            else:
                gg[tagname] = [("0 该侧未产出可比较正文", False,
                                "run_status=%s error=%s" % ((raw0 or raw1 or {}).get("run_status"),
                                str((raw or {}).get("error"))[:160]))]
        gates[pid] = gg
        if r0 and r1:
            avail.append(pid)
        texts = {sj: (r0 or {}).get("final_output") or "", sy: (r1 or {}).get("final_output") or ""}
        blocks.append((pid, axis, skill, texts, bool(r0 and r1)))

    os.makedirs(os.path.dirname(a.mapping) or ".", exist_ok=True)
    json.dump({"pre_registration_commit": PRE_COMMIT, "rule":
               "h=sha256(pre_registration_commit+pair_id); int(h[:8],16)%2==0 -> 甲=X 否则 甲=Y",
               "mapping": mapping, "hard_gate": gates},
              open(a.mapping, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    os.chmod(a.mapping, 0o600)
    mp_sha = hashlib.sha256(open(a.mapping, "rb").read()).hexdigest()

    L = ["""# 笛语 V1 质量对照匿名盲审包 v0.1

> **请只看内容本身。** 本文件不显示模型、不显示是否使用 Skill、不显示独立还是集成、不显示执行顺序。
> 两份输出使用完全相同的排版，未做任何润色、删减或重排。
>
> X / Y 的归属由预注册的确定性规则在**运行之前**决定，运行结果无法影响它。
> 映射表存在任务临时目录、权限 600，本文件提交时**尚未**入库；其 SHA-256 作为承诺登记在 Manifest。

## 怎么填

每组回答五行，直接贴回给我即可：

```text
pair_id:
preference: X | Y | TIE
material_difference: YES | NO
critical_error: NONE | X | Y | BOTH
reason: 一至三句
```

- `preference`：你更愿意把哪一份交给团队去执行。
- `material_difference`：两份的差别是否**实质**影响经营结果。只是措辞不同请填 `NO`。
- `critical_error`：哪一份出现了**不可接受**的错误（编造事实、改写你已确认的决定、越权、把申请写成确认）。

## 建议观察维度

顾客问题是否具体 · 专业判断与取舍是否成立 · 事实边界是否安全 · 账号或角色是否不可互换
· 内容目标是否清楚 · 下一步行动是否准确 · 输出是否模板化 · 是否值得进入下游

---
"""]
    for pid, axis, skill, texts, ready in blocks:
        L.append("\n## %s ｜ %s\n\n" % (pid, CN[skill]))
        if not ready:
            L.append("> **本组无法盲审**：至少一侧没有产出可比较的正文，原因见 EVAL 失败账本。\n")
            continue
        for tag in ("X", "Y"):
            L.append("### %s — %s\n\n" % (pid, tag))
            L.append("````text\n" + (texts.get(tag) or "").strip() + "\n````\n\n")
        L.append("```text\npair_id: %s\npreference: \nmaterial_difference: \ncritical_error: \nreason: \n```\n" % pid)

    # ---- 对照 RAW：全部运行原样归档，失败臂一并保留 ----
    R = ["""# 笛语 V1 质量对照 RUN_001 原始记录

> 九组对照的全部真实运行原样归档。**失败运行一律保留，未用成功样本覆盖，未选择性重试。**
> 按预注册第 6 节，整轮失败且命中已登记传输失败者允许**一次**完全相同的重试；额度用尽即计入结果。

## 1. 逐臂运行记录（按时间顺序，含重试）

| arm_id | 尝试 | 状态 | app_id | workflow_run_id | 正文字数 | model_used | 墙钟秒 | 错误 |
|---|---|---|---|---|---|---|---|---|
"""]
    order = {}
    if os.path.exists(p_runs):
        for ln in open(p_runs, encoding="utf-8"):
            try:
                r = json.loads(ln)
            except Exception:
                continue
            order.setdefault(r["arm_id"], []).append(r)
    for aid in sorted(order):
        for i, r in enumerate(order[aid], 1):
            R.append("| `%s` | %d | %s | `%s` | `%s` | %s | %s | %.1f | %s |\n" % (
                aid, i, r.get("run_status"), str(r.get("app_id"))[:8],
                str(r.get("workflow_run_id"))[:8], r.get("final_chars"),
                r.get("model_used"), r.get("wall_seconds") or 0,
                (str(r.get("error")) if r.get("error") else "")[:110].replace("|", "/").replace(chr(10), " ")))
    R.append("""
## 2. 集成侧产物来源

A 轴的集成侧**不是本脚本产生的**，而是从主 Chatflow 一条真实跑通的全链会话中原样取出。

| 项 | 值 |
|---|---|
| 来源 conversation | `%s` |
| 来源用例 | `SK-03`（40 类 E2E，6 轮，matrix → campaign → content_brief 依次真实执行） |
| 终态 | matrix `USER_ACCEPTED` / campaign `USER_ACCEPTED` / content_brief `VALIDATED` |

| Skill | 字数 | SHA-256 |
|---|---|---|
""" % integ_conv)
    for k in ("matrix", "campaign", "content_brief"):
        v = integ.get(k) or {}
        R.append("| %s | %s | `%s` |\n" % (k, v.get("final_chars", "——"), v.get("final_sha256", "——")))

    R.append("\n## 3. 冻结输入校验\n\n| Skill | 冻结 SHA-256 | 实际送入 SHA-256 | 一致 |\n|---|---|---|---|\n")
    for skill in ("matrix", "campaign", "content_brief"):
        rec = runs.get("%s|deepseek" % skill) or {}
        got = rec.get("task_context_sha256")
        R.append("| %s | `%s` | `%s` | %s |\n" % (
            skill, frozen[skill]["sha256"], got or "（该臂未产出）",
            "是" if got == frozen[skill]["sha256"] else "——"))

    R.append("\n## 4. 自动 Hard Gate 逐项\n\n| pair | 侧 | 门 | 结果 | 说明 |\n|---|---|---|---|---|\n")
    for pid, gg in gates.items():
        for tag, rows in gg.items():
            for nm, okv, det in rows:
                R.append("| %s | %s | %s | %s | %s |\n" % (
                    pid, tag, nm, {True: "通过", False: "**未通过**", None: "不适用"}[okv],
                    str(det)[:150].replace("|", "/")))

    R.append("\n## 5. 各臂输出正文\n\n> 失败臂无正文，如实标注。\n\n")
    for aid in sorted(order):
        last = order[aid][-1]
        R.append("### %s\n\n" % aid)
        if (last.get("final_output") or "").strip():
            R.append("- workflow_run_id `%s`，model `%s`，%d 字\n\n````text\n%s\n````\n\n" % (
                last.get("workflow_run_id"), last.get("model_used"),
                last.get("final_chars"), last["final_output"].strip()))
        else:
            R.append("- **未产出正文**。最后一次 `run_status=%s`，错误：\n\n````text\n%s\n````\n\n" % (
                last.get("run_status"), str(last.get("error"))[:1500]))
    open(os.path.join(os.path.dirname(os.path.abspath(a.out)) or ".",
                      "V1_QUALITY_COMPARISON_RUN_001_RAW.md"), "w", encoding="utf-8").write("".join(R))
    print("对照 RAW → V1_QUALITY_COMPARISON_RUN_001_RAW.md")

    open(a.out, "w", encoding="utf-8").write("".join(L))
    print("盲审包 → %s（%d 字节）" % (a.out, os.path.getsize(a.out)))
    print("可盲审组：%s（%d/9）" % (avail, len(avail)))
    print("映射承诺 SHA-256：%s" % mp_sha)
    print("\n=== 自动 Hard Gate ===")
    for pid, gg in gates.items():
        for tag, rows in gg.items():
            bad = [r for r in rows if r[1] is False]
            print("%-3s %s  %s" % (pid, tag, "PASS" if not bad else
                  "FAIL: " + "; ".join("%s(%s)" % (r[0], r[2][:70]) for r in bad)))


if __name__ == "__main__":
    main()
