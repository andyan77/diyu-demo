#!/usr/bin/env python3
"""AC 状态的**单一真源** + 两处渲染，结构上消掉第 6 轮阻断项 B-2 的成因。

B-2 是：`M3_ACCEPTANCE_CRITERIA_FROZEN_v1.0.md §7.2` 与 `M3_CHECKPOINT_*.md §8`
是同一份状态的两处呈现，第 4 轮它们不一致 —— 一处停在旧状态，另一处已推进。
当时的修法是"今后任一方更新，另一方必须同轮更新"，那是一条**靠自觉**的规则。

靠自觉的规则会再犯。本文件把它换成机制：状态只写在 AC_STATE_v13.json 里一份，
两处 Markdown 都由本脚本从它渲染。两处不可能不一致，因为它们不是两份数据。

用法：
    render_ac_state.py --check     核对仓库里两处表格是否与真源一致（不改文件）
    render_ac_state.py --emit      把两处表格的 Markdown 打到 stdout，供人工贴入

不自动改文件：这两份都是冻结文档，改动必须经过人手与提交，不由脚本静默写入。
"""
import argparse, json, os, re, sys

WT = "/home/faye/diyu-demo-worktrees/m3-account-content-operator-v1"
SRC = os.path.join(WT, "account-operations/evidence/ep18-ac-recompute-v13/AC_STATE_v13.json")

# 状态词只能取自通用内核 §4 的统一状态词，或本任务已在用的复合记法。
# 不允许再造同义词 —— 这是 A2 的"同一维度不得再造同义词"。
ALLOWED = {
    "PASS", "FAIL", "NOT_VERIFIED",
    "FAIL(INSUFFICIENT)", "FAIL(ABSENT)", "FAIL(NOT_CHECKED)", "FAIL(INCONCLUSIVE)",
    "NOT_APPLICABLE",
    "成立", "成立（带限定）", "部分成立", "不得 PASS", "未独立成立",
    "探索级（NOT_VERIFIED）",
}


def load():
    if not os.path.exists(SRC):
        sys.exit(f"真源不存在：{SRC}\n先由 AC 重算写出它，再渲染。")
    d = json.load(open(SRC, encoding="utf-8"))
    bad = []
    for ac in d["acs"]:
        for st in (ac["state"] if isinstance(ac["state"], list) else [ac["state"]]):
            s = st["value"] if isinstance(st, dict) else st
            if s not in ALLOWED:
                bad.append((ac["id"], s))
    if bad:
        sys.exit("出现未登记的状态词（不得再造同义词）：\n" +
                 "\n".join(f"  {a}: {s}" for a, s in bad))
    return d


def _states(ac):
    st = ac["state"]
    if isinstance(st, list):
        return "<br>".join(f"{x['binding']}：`{x['value']}`" for x in st)
    return f"`{st}`" if st in ALLOWED - {"成立", "部分成立"} else st


def table(d, style):
    """style='criteria' 渲染判据文件 §7.2；style='checkpoint' 渲染 Checkpoint §8。

    两者只在**列**上不同：判据文件要"依据"，Checkpoint 还要"下一步动作"。
    状态值本身来自同一个字段，不可能不同。
    """
    head = ("| AC | 当前状态 | 依据 |\n|---|---|---|"
            if style == "criteria" else
            "| AC | 当前状态 | 依据 | 还差什么 |\n|---|---|---|---|")
    rows = []
    for ac in d["acs"]:
        cells = [ac["id"], _states(ac), ac["basis"]]
        if style == "checkpoint":
            cells.append(ac.get("gap") or "—")
        rows.append("| " + " | ".join(c.replace("\n", " ") for c in cells) + " |")
    return head + "\n" + "\n".join(rows)


def summary(d):
    tally = {}
    for ac in d["acs"]:
        st = ac["state"]
        vals = [x["value"] for x in st] if isinstance(st, list) else [st]
        for v in vals:
            tally[v] = tally.get(v, 0) + 1
    return tally


def check(d):
    """核对仓库两处表格里的每个 AC 行，**整行**是否与真源渲染逐字一致。

    第一版只比状态词，结果 `AC-20` 的「依据」改了之后 --check 照样通过 ——
    状态词没变，依据文字却已经漂了。只比一部分字段，等于给漂移留了一条缝。
    现在整行比对：状态、依据、缺口任一处不一致都报。
    """
    targets = [
        ("M3_ACCEPTANCE_CRITERIA_FROZEN_v1.0.md", "criteria"),
        (d.get("checkpoint_file", "M3_CHECKPOINT_ROUND_7.md"), "checkpoint"),
    ]
    problems = []
    for fname, _style in targets:
        p = os.path.join(WT, fname)
        if not os.path.exists(p):
            problems.append(f"{fname}: 文件不存在")
            continue
        txt = open(p, encoding="utf-8").read()
        for ac in d["acs"]:
            st = ac["state"]
            vals = [x["value"] for x in st] if isinstance(st, list) else [st]
            # 找到该 AC 所在的表格行，只在该行里核对状态词
            m = re.search(r"^\|\s*" + re.escape(ac["id"]) + r"\b.*$", txt, re.M)
            if not m:
                problems.append(f"{fname}: 找不到 {ac['id']} 的表格行")
                continue
            line = m.group(0)
            expect = ("| " + " | ".join(
                c.replace("\n", " ") for c in
                ([ac["id"], _states(ac), ac["basis"]] +
                 ([ac.get("gap") or "—"] if _style == "checkpoint" else []))) + " |")
            if line.strip() != expect.strip():
                missing = [v for v in vals if v not in line]
                problems.append(
                    f"{fname}: {ac['id']} 行与真源渲染不一致"
                    + (f"（缺状态词 {missing}）" if missing else "（状态词一致，依据或缺口文字有漂移）"))
    return problems


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--emit", action="store_true")
    a = ap.parse_args()
    d = load()
    if a.emit:
        print("=== §7.2（判据文件） ===\n")
        print(table(d, "criteria"))
        print("\n\n=== §8（Checkpoint） ===\n")
        print(table(d, "checkpoint"))
        print("\n\n汇总：", json.dumps(summary(d), ensure_ascii=False))
        return
    if a.check:
        problems = check(d)
        if problems:
            print("两处呈现与真源不一致：", file=sys.stderr)
            for p in problems:
                print("  " + p, file=sys.stderr)
            sys.exit(1)
        print(f"两处呈现与真源一致，{len(d['acs'])} 条 AC 全部核对通过")
        print("汇总：", json.dumps(summary(d), ensure_ascii=False))
        return
    ap.print_help()


if __name__ == "__main__":
    main()
