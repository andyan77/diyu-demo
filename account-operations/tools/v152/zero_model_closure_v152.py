#!/usr/bin/env python3
"""候选 v1.5.2 · 零模型技术闭合（Execution Prompt v1.2 §4.3）

**本文件不发起任何模型调用。** 八项，逐项给数并落盘：

  Z1 Skill/template 静态一致性  ——  实际 diff 是不是**恰好**批准的那两处，一行不多
  Z2 DD-5 全量确定性回放        ——  两条语料轴、133 次真实运行 × 2 份正文
  Z3 审计块不得单独构成交付      ——  在**真实退化草稿**与机械构造变体上验硬门
  Z4 E07/E08 真拒不变性         ——  穷举补齐节点的一切可能输出
  Z5 B15-DIR-02 不再误拒
  Z6 新增误拒 / 新增确定性漏检   ——  两个方向都必须是 0
  Z7 四层分离                   ——  闸门不许给正文添一个字（机械证明，不是声明）
  Z8 凭据扫描                   ——  逐字节精确 + 通用形态

历史 69 份模型草稿只作历史/诊断输入。**零模型回放只能证明确定性组件的行为，
不能证明那两句 Skill 规则已经被模型执行**——后者只有 Founder 亲测能给。
"""
import hashlib
import io
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
WT = os.path.dirname(os.path.dirname(TOOLS))
GATE = os.path.join(TOOLS, "gate_v13")
for p in (GATE, TOOLS, os.path.join(TOOLS, "rebind006"), os.path.join(TOOLS, "rebind007")):
    sys.path.insert(0, p)
OUT = os.path.join(WT, "account-operations/evidence/ep34-candidate-v152-closure")
SKILL = os.path.join(WT, "account-operations/skills/operating-one-account/SKILL.md")
BASE = "5e1b6ee"          # v1.5.1 收口那次提交 = 本轮改动的直接前身

import shared_checks as S                                          # noqa: E402
from gate_main import main as gate_main                            # noqa: E402
from assemble_main import main as assemble_main                    # noqa: E402
from post_gate_main import main as post_gate_main                  # noqa: E402
from corpus_v15 import load_v15, load_regression                   # noqa: E402

# 合同 M3_ENGINEERING_TASK_CONTRACT_v1.3 · final_candidate.approved_skill_delta，逐字
APPROVED_DELTA = [
    "审计块只能出现在正文之后；正文不存在时不许单独输出审计块。",
    "审计块不加代码围栏，前后不加任何三个反引号标记。",
]


def _git_show(rev, path):
    return subprocess.run(["git", "-C", WT, "show", f"{rev}:{path}"],
                          capture_output=True, text=True, check=True).stdout


def _rel(p):
    return os.path.relpath(p, WT)



# ---------------------------------------------------------------- 代写判据（共用）
# `render_body` 的设计就是"外观层由代码还原"：它会把参考文件路径和 LOADED/NOT_LOADED
# 这些机器痕迹换成人话。所以"闸门一个字都不许加"这句话是**假的**，不能拿它当判据。
# 真正要证的是合同 hard_failures 里那一条：**闸门或补齐节点不得代写实质交付**。
# 机械化成两步，不循环：
#   ① 先把 `render_body` 那张**封闭替换表**同样施加到草稿上；
#   ② 然后要求闸门正文是它的**子序列**（子序列 = 只许删，不许插）。
# 如果哪天有人往 render_body 里加了表外的插入，这一步立刻挂——这正是它要守的东西。
def _apply_declared_substitutions(t):
    for path in sorted(S.REF_DISPLAY, key=len, reverse=True):
        t = t.replace(path, S.REF_DISPLAY[path])
    for a, b in (("NOT_LOADED", "未加载"), ("LOADED", "已加载")):
        t = re.sub(r"(?<![A-Za-z_])" + a + r"(?![A-Za-z_])", b, t)
    return t


def _is_subsequence(small, big):
    it = iter(big)
    return all(ch in it for ch in small)


def _not_authored(text, draft_raw):
    """text 里的每一个字符要么来自草稿，要么来自那张封闭替换表。"""
    body, _audit = S.split_audit(draft_raw)
    return _is_subsequence((text or "").strip(), _apply_declared_substitutions(body))


# ------------------------------------------------------------------ Z1
def z1():
    old = _git_show(BASE, _rel(SKILL))
    new = io.open(SKILL, encoding="utf-8").read()
    ol, nl = old.split("\n"), new.split("\n")
    import difflib
    added, removed = [], []
    for line in difflib.unified_diff(ol, nl, n=0, lineterm=""):
        if line.startswith("+++") or line.startswith("---") or line.startswith("@@"):
            continue
        if line.startswith("+"):
            added.append(line[1:])
        elif line.startswith("-"):
            removed.append(line[1:])

    want_added = ["- " + d for d in APPROVED_DELTA]
    want_removed = ["```text", "```"]

    # 审计块字段清单必须逐字未变（去掉围栏行之后比较）
    def audit_lines(t):
        i = t.index("<<AUDIT>>")
        j = t.index("<<END_AUDIT>>") + len("<<END_AUDIT>>")
        return [x for x in t[i:j].split("\n")]
    fields_same = audit_lines(old) == audit_lines(new)

    # 没有新增任何 AC-09 同义提醒：O-6 那一整节逐字未变
    def sec(t, head, nxt):
        return t[t.index(head):t.index(nxt)]
    o6_same = sec(old, "### O-6 ·", "### O-7 ·") == sec(new, "### O-6 ·", "### O-7 ·")

    # 除〈用户可见正文的硬要求〉与〈审计块〉两处外，全文其余部分逐字未变
    def strip_changed(t):
        t = t.replace("- " + APPROVED_DELTA[0] + "\n", "").replace("- " + APPROVED_DELTA[1] + "\n", "")
        t = t.replace("### 审计块（正文之后，格式固定）\n\n```text\n<<AUDIT>>",
                      "### 审计块（正文之后，格式固定）\n\n<<AUDIT>>")
        t = t.replace("<<END_AUDIT>>\n```\n", "<<END_AUDIT>>\n")
        return t
    rest_same = strip_changed(old) == strip_changed(new)

    fence_in_audit = "```" in new[new.index("### 审计块"):new.index("每行写一项")]

    return {
        "base_commit": BASE,
        "lines_added": added, "lines_removed": removed,
        "added_is_exactly_approved_delta": added == want_added,
        "removed_is_exactly_the_two_fence_markers": removed == want_removed,
        "audit_field_list_byte_identical": fields_same,
        "O6_section_byte_identical_no_new_ac09_synonym": o6_same,
        "everything_else_byte_identical": rest_same,
        "audit_template_still_fenced": fence_in_audit,
        "skill_sha256_before": hashlib.sha256(old.encode()).hexdigest(),
        "skill_sha256_after": hashlib.sha256(new.encode()).hexdigest(),
        "pass": (added == want_added and removed == want_removed and fields_same
                 and o6_same and rest_same and not fence_in_audit),
    }


# ------------------------------------------------------------------ 语料
def _rows():
    out = []
    for r in load_v15() + load_regression():
        if (r["draft_raw"] or "").strip():
            out.append(r)
    return out


ROWS = _rows()


# ------------------------------------------------------------------ Z2 / Z5 / Z6
def z2_z5_z6():
    import replay_v151 as R
    v15, sk15 = R._run(load_v15(), "main")
    reg, skrg = R._run(load_regression(), "regression")
    res = {}
    for name, rows, sk in (("main", v15, sk15), ("regression", reg, skrg)):
        res[name] = R.summarize(rows, sk, name)
    b15 = [x for x in v15 if x["case"] == "B15-DIR-02-topic-to-brief"]
    e0708 = sorted(x["case"] for x in reg if x["v15_carry"] == "REJECTED_KEEP_PREVIOUS")
    return {
        "replay": res,
        "Z5_b15_no_longer_rejected": bool(b15) and b15[0]["v15_carry"] != "REJECTED_KEEP_PREVIOUS",
        "Z6_newly_rejected_main": res["main"]["newly_rejected"],
        "Z6_newly_rejected_regression": res["regression"]["newly_rejected"],
        "Z4_still_rejected_regression": e0708,
        "pass": (not res["main"]["newly_rejected"] and not res["regression"]["newly_rejected"]
                 and bool(b15) and b15[0]["v15_carry"] != "REJECTED_KEEP_PREVIOUS"
                 and e0708 == ["E07", "E08"]),
    }


# ------------------------------------------------------------------ Z3
AUDIT_ONLY_REAL = {
    "B09-5@v1.5 (真实退化草稿)":
        "account-operations/evidence/ep06b-runtime-behavior-v15/B09-5-no-market-data.json",
    "B09-5@v1.3 (真实退化草稿，带代码围栏)":
        "account-operations/evidence/ep06b-runtime-behavior-v13/B09-5-no-market-data.json",
    "E09@v1.2 (真实退化草稿)":
        "account-operations/evidence/ep07-longitudinal-v12/E09.json",
}
AUDIT_ONLY_SYNTH = {
    "机械构造·裸审计块": "<<AUDIT>>\n探索提案=否;暂定锚点=否;冲突反馈=否;无内容任务=否\n<<END_AUDIT>>",
    "机械构造·围栏包住的审计块": "```\n<<AUDIT>>\n探索提案=否;暂定锚点=否;冲突反馈=否;无内容任务=否\n<<END_AUDIT>>\n```",
    "机械构造·前面只有空白": "   \n\n<<AUDIT>>\n探索提案=否;暂定锚点=否;冲突反馈=否;无内容任务=否\n<<END_AUDIT>>",
    "机械构造·前面只有一句寒暄": "好的。\n\n<<AUDIT>>\n探索提案=否;暂定锚点=否;冲突反馈=否;无内容任务=否\n<<END_AUDIT>>",
}


def _one_chain(draft, manifest, ctx):
    g = gate_main(draft, manifest, ctx)
    a = assemble_main(g["body"], "", g["needs_fix"], g["gate_status"], g["draft_audit"])
    pg = json.loads(post_gate_main(a["final_text"], manifest, g["gate_report"], ctx,
                                   a["final_audit"], a["path"])["post_gate_report"])
    return json.loads(g["gate_report"]), a, pg


def z3():
    cases = []
    for label, rel in AUDIT_ONLY_REAL.items():
        d = json.load(open(os.path.join(WT, rel), encoding="utf-8"))
        o = d["raw_response_body"]["data"]["outputs"]
        wi = d["workflow_inputs"]
        gr, a, pg = _one_chain(o["draft_raw"], wi["loaded_references"], wi["account_context"])
        cases.append({"case": label, "source": rel, "gate_status": gr["gate_status"],
                      "path": a["path"], "final_text_len": len(a["final_text"]),
                      "carry": pg["cycle_state_carry"],
                      "final_text": a["final_text"][:40],
                      "not_authored": _not_authored(a["final_text"], o["draft_raw"]),
                      "ok": (gr["gate_status"] == "HARD_FAIL_MIN_OUTPUT"
                             and a["path"] == "hard_fail_no_repair"
                             and pg["cycle_state_carry"] == "REJECTED_KEEP_PREVIOUS"
                             and _not_authored(a["final_text"], o["draft_raw"]))})
    for label, draft in AUDIT_ONLY_SYNTH.items():
        gr, a, pg = _one_chain(draft, "", "")
        cases.append({"case": label, "source": "synthesized", "gate_status": gr["gate_status"],
                      "path": a["path"], "final_text_len": len(a["final_text"]),
                      "final_text": a["final_text"][:40],
                      "not_authored": _not_authored(a["final_text"], draft),
                      "ok": (gr["gate_status"] == "HARD_FAIL_MIN_OUTPUT"
                             and a["path"] == "hard_fail_no_repair"
                             and pg["cycle_state_carry"] == "REJECTED_KEEP_PREVIOUS"
                             and _not_authored(a["final_text"], draft))})
    return {"cases": cases,
            "criterion": ("硬门开火 + 路径 hard_fail_no_repair + 周期状态拒收 + 交付里没有一个字"
                          "是闸门／补齐节点代写的。**不要求 final_text 长度为 0**——"
                          "模型自己留下的 ``` 或一句寒暄本来就该原样留着，"
                          "它们被硬门挡住即可，抹掉它们反而是执行侧在改模型输出。"),
            "pass": all(c["ok"] for c in cases)}


# ------------------------------------------------------------------ Z4
def z4():
    """穷举补齐节点在持续位这一层的**全部可能输出**，看 E07/E08 的拒收是否恒成立。
    复用 REBIND-006 那个验证器的 `blocking_for`，但**不调它的 main()**——
    那个 main() 会写进第 9 轮的历史证据目录 `ep28-…`，历史证据不覆盖。"""
    import itertools
    import verify_e07_e08_invariance as V
    rows = {r["case"]: r for r in load_regression()}
    out = []
    for case in ("E07", "E08"):
        r = rows[case]
        gr = json.loads(gate_main(r["draft_raw"], r["manifest"],
                                  r["account_context"])["gate_report"])
        input_ids = (gr.get("positions") or {}).get("input_position_ids") or []
        draft_ids = gr.get("draft_declared_position_ids") or []
        universe = list(dict.fromkeys(list(input_ids) + list(draft_ids) + [V.FOREIGN]))
        total = always = 0
        counter = []
        for k in range(len(universe) + 1):
            for combo in itertools.combinations(universe, k):
                total += 1
                blk, _why = V.blocking_for(input_ids, draft_ids, list(combo))
                if blk:
                    always += 1
                else:
                    counter.append(list(combo))
        out.append({"case": case, "input_position_ids": input_ids,
                    "draft_declared_position_ids": draft_ids, "universe": universe,
                    "possible_repair_outputs_enumerated": total, "rejected_in": always,
                    "counterexamples_where_it_would_pass": counter,
                    "invariant": not counter})
    return {"rows": out, "all_invariant": all(x["invariant"] for x in out),
            "pass": all(x["invariant"] for x in out)}


# ------------------------------------------------------------------ Z7 四层分离
def z7():
    """闸门不许给正文添一个字。机械证明：`gate.body` 必须是**草稿去掉推理段与审计块之后
    那段文本的子串**。同时验确定性：同一输入跑两次，报告逐字节相同。"""
    bad_author, bad_det, bad_assemble = [], [], []
    for r in ROWS:
        g1 = gate_main(r["draft_raw"], r["manifest"], r["account_context"])
        g2 = gate_main(r["draft_raw"], r["manifest"], r["account_context"])
        if g1["gate_report"] != g2["gate_report"] or g1["body"] != g2["body"]:
            bad_det.append(r["case"])
        if not _not_authored(g1["body"], r["draft_raw"]):
            bad_author.append({"case": r["case"], "body_head": g1["body"][:60]})
        a = assemble_main(g1["body"], "", g1["needs_fix"], g1["gate_status"], g1["draft_audit"])
        if g1["needs_fix"] == "no" and a["final_text"].strip() != g1["body"].strip():
            bad_assemble.append({"case": r["case"], "path": a["path"]})
    return {"samples": len(ROWS),
            "criterion": ("① 闸门正文里的每个字符要么来自草稿、要么来自 render_body 那张封闭"
                          "替换表（子序列判定，只许删不许插）；② 直发路上装配必须逐字返回闸门正文，"
                          "一个字都不加；③ 同一输入两次跑，报告逐字节相同。"),
            "gate_authored_text_outside_declared_table": bad_author,
            "assemble_changed_text_on_direct_path": bad_assemble,
            "non_deterministic": bad_det,
            "note": ("补齐路的终稿由补齐 LLM 产出，零模型拿不到，不在本项覆盖内；"
                     "那一层由 Z4 的穷举不变性与闸门的 D-3 代写检测分别覆盖。"),
            "pass": not bad_author and not bad_assemble and not bad_det}


# ------------------------------------------------------------------ Z8 凭据
def z8():
    env = {}
    for line in io.open(os.path.join(WT, ".env"), encoding="utf-8"):
        if "=" in line and not line.strip().startswith("#"):
            k, _, v = line.strip().partition("=")
            env[k] = v.strip().strip('"').strip("'")
    secrets = {"DEEPSEEK_API_KEY": env.get("DEEPSEEK_API_KEY"),
               "DIFY_CONSOLE_PASSWORD": env.get("DIFY_CONSOLE_PASSWORD")}
    kp = os.path.join(TOOLS, "m3_app_key.txt")
    if os.path.exists(kp):
        secrets["DIFY_APP_API_KEY"] = io.open(kp, encoding="utf-8").read().strip()
    files = [l[3:] for l in subprocess.run(["git", "-C", WT, "status", "--porcelain"],
                                           capture_output=True, text=True).stdout.splitlines()]
    exp = []
    for f in files:
        p = os.path.join(WT, f)
        if os.path.isdir(p):
            for root, _d, fs in os.walk(p):
                exp += [os.path.join(root, x) for x in fs]
        elif os.path.exists(p):
            exp.append(p)
    hits, pat_hits = [], []
    pat = re.compile(rb"sk-[A-Za-z0-9]{16,}|app-[A-Za-z0-9]{20,}|Bearer [A-Za-z0-9._-]{20,}")
    for f in exp:
        try:
            b = io.open(f, "rb").read()
        except Exception:  # noqa: BLE001
            continue
        for name, val in secrets.items():
            if val and val.encode() in b:
                hits.append({"secret": name, "file": _rel(f)})
        for m in pat.finditer(b):
            pat_hits.append({"file": _rel(f), "form": m.group(0)[:6].decode("ascii", "replace") + "…"})
    return {"files_scanned": len(exp), "secret_names_checked": sorted(secrets),
            "exact_hits": hits, "pattern_hits": pat_hits,
            "pass": not hits and not pat_hits}


def main():
    rep = {"what": "候选 v1.5.2 零模型技术闭合（Execution Prompt v1.2 §4.3）",
           "executor_model_calls": 0,
           "Z1_skill_static": z1(),
           "Z2_Z5_Z6_replay": z2_z5_z6(),
           "Z3_audit_only_hard_gate": z3(),
           "Z4_e07_e08_invariance": z4(),
           "Z7_layer_separation": z7(),
           "Z8_credential_scan": z8()}
    rep["ALL_PASS"] = all(v["pass"] for k, v in rep.items() if isinstance(v, dict) and "pass" in v)
    rep["claim_limit"] = ("零模型回放只能证明确定性组件的行为。那两句 Skill 规则是否真的被模型执行，"
                          "本轮**无法证明**，等级为推断；只有 Founder 亲测能给出观察。")
    os.makedirs(OUT, exist_ok=True)
    json.dump(rep, open(os.path.join(OUT, "ZERO_MODEL_CLOSURE_V152.json"), "w",
                        encoding="utf-8"), ensure_ascii=False, indent=2)
    for k, v in rep.items():
        if isinstance(v, dict) and "pass" in v:
            print(f"  {'PASS' if v['pass'] else 'FAIL'}  {k}")
    print("ALL_PASS", rep["ALL_PASS"])
    return rep


if __name__ == "__main__":
    sys.exit(0 if main()["ALL_PASS"] else 1)
