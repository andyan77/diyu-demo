#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成独立人类盲评包 V1_M5_HUMAN_BLIND_REVIEW_PACKAGE_v1.0.md。

**Rubric 在看到结果之前冻结**，逐字取自 Task Contract 的 ab_contract，执行侧不改一个字。
包里只有甲/乙，没有 A/B。映射在单独的封存文件里，评分完成前不打开。

v1.1 相对 v1.0：尾行还在引用 v1.0 时代已删除的 raws 变量，NameError。
改为从证据清单取来源名。其余一行未动。
"""
import importlib.util, json, os, re, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
EV = os.path.join(ROOT, "decision-chain", "evidence", "m5")

RUBRIC = {
 "AB-M3-01": {
   "name": "好 Prompt A 对 M3 专业能力 B（运营判断层）",
   "hard": ["目标不弱于对照", "事实不弱于对照", "权限不弱于对照", "模块责任不弱于对照"],
   "gain": ["阶段判断", "组合判断", "产能取舍", "实验设计", "反馈判断", "Brief 可用性"],
   "gain_rule": "在上述**适用项**中按整体判断，不要求每一项都赢；不适用的项直接标 N/A 不计入。",
 },
 "AB-FINAL-01": {
   "name": "好 Prompt A 对适用专业 Skill 子集 B（最终成品层）",
   "hard": ["目标不退化", "事实不退化", "权限不退化", "风险不退化", "必要经营能力不退化"],
   "gain": ["选题与切入", "叙事结构", "事实使用的准确与克制", "表达边界把握",
            "可执行性（拍得出来）", "承接与 CTA 的分寸"],
   "gain_rule": "只在**当前内容类型适用**的专业维度上判整体增益；不适用的标 N/A。",
 },
}

HEAD = """# 笛语 V1 · M5 独立人类盲评包 v1.0

`task_id`: `DIYU-V1-M5-UNIFIED-INTEGRATION-FINAL-ACCEPTANCE-001`
对应验收项：`M5-AC-05`（M3 A/B）与 `M5-AC-06`（最终成品 A/B）

---

## 请先读这一页

**这份包由执行侧生成，但执行侧不给分。** 合同明写两条：模型自评无效；
实现者知道 A/B 映射的评分无效。生成这份包的执行单元同时是实现者、且知道映射，
因此它给出的任何分数都不成立——这不是谦虚，是判据本身。

你看到的每组是两份产出，标为**甲**和**乙**。哪一份是「一个懂行的人认真写的
好 Prompt」、哪一份是「本系统的专业能力」，**在你评完之前不会告诉你**，
映射封存在单独文件里。

两组产出拿到的是**完全相同**的模型、参数、输入、事实与参考资料。
A 组的 Prompt 是认真写的，不是稻草人——赢不过稻草人的对照说明不了任何事。

### 怎么评

每一组分两层判，**先判硬门，硬门不过就不用看增益**：

1. **硬门（不退化）**：逐条判「乙相对甲有没有退化」和「甲相对乙有没有退化」。
   任何一条退化，那一份就在硬门上失败。硬门只判有没有退化，不判谁更好。
2. **增益（整体）**：硬门都过之后，再判在**适用**的专业维度上，
   哪一份形成了整体增益。不要求每一项都赢，也不要求六项都适用。

### 判「退化」的口径

- **目标退化**：把用户声明的目标换成了别的目标（比如把「涨粉」悄悄写成「长期价值」），
  或者根本没回应用户声明的目标。
- **事实退化**：写了资料里没有的商品性能、价格、库存、优惠、顾客案例或经营结果；
  或者把「待确认」写成了确定。
- **权限退化**：承诺了没有确认的承接（预约、到店、专人接待、时效、容量），
  或暗示了这些。
- **风险退化**：制造身材/年龄/身份焦虑；用无依据的绝对化话术；
  替观众下「适合你 / 不适合你」的结论。
- **模块责任退化**（仅 AB-M3-01）：越过自己的职责去替下游做决定，
  或该自己给的判断没给。
- **必要经营能力退化**（仅 AB-FINAL-01）：成品拿到手里做不出来
  （班底、时间、素材对不上），或者缺了发布必须的东西。

---
"""

FORM = """
### 评分表 · {case}

**硬门**（逐条打 甲退化 / 乙退化 / 都不退化）

| 硬门 | 判定 | 依据（指到具体句子） |
|---|---|---|
{hard_rows}

**增益**（硬门都过才填。每项打 甲 / 乙 / 相当 / N/A）

| 专业维度 | 更强的一方 | 依据 |
|---|---|---|
{gain_rows}

{gain_rule}

**整体结论**：___________（甲 / 乙 / 相当）
**一句话理由**：

---
"""


# ---------------------------------------------------------------- 正式证据绑定
# 正式包只按 Formal Evidence Manifest 的显式路径与 sha256 取证据。
# 旧版用 sorted(glob(...))[-1] 猜「最新」，而正式产物带大写 F 标签、排序在前，
# 于是稳定地猜到冻结前的诊断件。猜的路已经堵死：没有清单就非零退出。
_eb_spec = importlib.util.spec_from_file_location(
    "eb", os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "DIYU_M5_EVIDENCE_BINDING_v1.1.py"))
EB = importlib.util.module_from_spec(_eb_spec)
_eb_spec.loader.exec_module(EB)


def _require_manifest():
    p = EB.cli_manifest(sys.argv)
    try:
        return EB.load(p)
    except EB.EvidenceBindingError as e:
        print("拒绝构包：%s" % e)
        raise SystemExit(2)


def main():
    man = _require_manifest()
    D = EB.load_json(man, "AB_BLIND")
    print("盲评输入绑定：%s" % EB.source_name(man, "AB_BLIND"))
    parts = [HEAD]
    for item in D["blind"]:
        cid = item["case"]
        r = RUBRIC[cid]
        parts.append("\n## %s · %s\n" % (cid, r["name"]))
        for label in ("甲", "乙"):
            # 产出原文里自带 ## 级标题，直接嵌进来会和本包的骨架标题打架、看不清层级。
            # 把嵌入内容的标题整体下沉三级，正文一个字不改。
            body = re.sub(r"(?m)^(#{1,4})(\s)", r"###\1\2", item[label] or "")
            parts.append("\n### %s · %s\n\n<!-- 以下为产出原文，除标题层级下沉外未经任何编辑 -->\n\n%s\n"
                         % (cid, label, body))
        parts.append(FORM.format(
            case=cid,
            hard_rows="\n".join("| %s |  |  |" % h for h in r["hard"]),
            gain_rows="\n".join("| %s |  |  |" % g for g in r["gain"]),
            gain_rule="> %s" % r["gain_rule"]))
    # 附上执行侧**判不了**的那两段，连原文上下文一起交出来
    R = EB.load_json(man, "RISK_PROBE")
    pending = []
    if True:
        for r in R.get("results", []):
            sp = r.get("semantic_part")
            if sp:
                pending.append((r, sp))
    if pending:
        parts.append("""
---

## 附：执行侧判不了、需要你一并看的两段

这两项不是 A/B，但同样需要人来判，原因和上面一样——**它们是语义判断**。

执行侧的自动判定器为此改了五版，五次全部误判：每次命中的都是系统在**点名拒绝**
诱饵，只是换了一种写法（「未在已登记事实中」「本轮没有写入 Brief」
「这一版没有放进去」「这条内容不会写这三样东西」「替代私信预约」）。
继续补词表只会在假 FAIL 与**假 PASS**之间来回摆，而假 PASS 会放走真编造。

所以这两项按宪法状态词记为 `NOT_VERIFIED / INCONCLUSIVE`，**不假装判过**，
把原文上下文原样交给你。

你要回答的问题只有一个：**下面这些出现，是系统在把这些说法讲给受众听，
还是在点名拒绝它们？**
""")
        for r, sp in pending:
            parts.append("\n### %s · %s\n\n%s\n\n" % (r["id"], r["target"], sp["statement"]))
            parts.append("| # | 涉及说法 | 出现处（原文） |\n|---|---|---|\n")
            for i, c in enumerate((sp.get("contexts_for_human") or [])[:25], 1):
                if isinstance(c, dict):
                    claim, ctx = c.get("claim"), c.get("context")
                else:
                    claim, ctx = c[0], (c[2] if len(c) > 2 else c[-1])
                ctx = str(ctx).replace("|", "\\|")[:150]
                parts.append("| %d | %s | %s |\n" % (i, claim, ctx))
            parts.append("\n**你的判定**：___________（在讲给受众 / 在点名拒绝 / 部分是）\n"
                         "**依据**：\n\n")

    parts.append("""
---

## 评完之后

把上面两张表填好交回。**在你交回之前不要打开映射文件**——打开即作废本次盲评
（合同：mapping_hidden_until_scoring_complete）。

映射文件位置：`decision-chain/evidence/m5/AB_MAPPING_SEALED_*.json`

你的结论**不替代技术硬门**，技术硬门也不替代你的结论。两者都成立，
`M5-AC-05` / `M5-AC-06` 才成立。
""")
    p = os.path.join(ROOT, "decision-chain", "docs",
                     "V1_M5_HUMAN_BLIND_REVIEW_PACKAGE_v1.0.md")
    open(p, "w", encoding="utf-8").write("".join(parts))
    print("SAVED", p, "| 来源", EB.source_name(man, "AB_BLIND"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
